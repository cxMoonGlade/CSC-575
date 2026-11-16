"""Inspect RMS levels in saved IDMT reference intervals without changing predictions."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .audio import extract_features
from .evaluate import _normalize
from .regions import read_intervals
from .run import save_csv, save_json


def weighted_quantiles(values, weights, probabilities):
    """Return inverse empirical-CDF quantiles with duration weights."""
    values, weights = np.asarray(values), np.asarray(weights)
    probabilities = np.asarray(probabilities)
    if values.ndim != 1 or values.shape != weights.shape:
        raise ValueError("Expected equal-length vectors")
    if (not np.isfinite(values).all() or not np.isfinite(weights).all()
            or np.any(weights < 0) or np.any(~np.isfinite(probabilities))
            or np.any((probabilities < 0) | (probabilities > 1))):
        raise ValueError("Invalid values, weights or probabilities")
    keep = weights > 0
    if not np.any(keep):
        return [None] * len(probabilities)
    order = np.argsort(values[keep], kind="stable")
    v, w = values[keep][order], weights[keep][order]
    cdf = np.cumsum(w) / np.sum(w)
    indices = np.minimum(np.searchsorted(cdf, probabilities), len(v) - 1)
    return v[indices].tolist()


def frame_weights(edges, start, end):
    """Intersect one reference interval with the centred prediction cells."""
    return np.maximum(0, np.minimum(edges[1:], end) - np.maximum(edges[:-1], start))


def analyze(run: Path, data_root: Path, output: Path):
    if output.exists():
        raise FileExistsError("Choose a new output directory")
    config = json.loads((run / "configurations.json").read_text())["long"]
    selection = json.loads((run / "selection.json").read_text())
    buckets = {key: [[], []] for key in ("N", "chord", "unsupported")}
    rows, plots, inputs = [], {}, {}
    threshold_db = float(config["silence_db"])
    for record in selection["recordings"]:
        name = record["piece_id"]
        audio = data_root / record["archive_path"]
        reference_path = run / "predictions" / name / "reference.csv"
        prediction_path = run / "predictions" / name / "long_viterbi.csv"
        # Tuning does not enter RMS; skip its estimation and all chroma transforms.
        features = extract_features(audio, config | {"tuning": 0.0}, required=())
        rms, times, duration = features["rms"], features["times"], features["duration"]
        edges = np.r_[0, (times[:-1] + times[1:]) / 2, duration]
        peak = float(rms.max())
        db = 20 * np.log10(np.maximum(rms, 1e-12) / max(peak, 1e-12))
        silent = (rms <= peak * 10 ** (threshold_db / 20)) | (rms <= 1e-12)
        reference = _normalize(read_intervals(reference_path), duration)
        prediction = read_intervals(prediction_path)
        predicted_n = [(a, b) for a, b, label in prediction if label == "N"]
        for a, b, label in reference:
            category = "unsupported" if label is None else "N" if label == "N" else "chord"
            weights = frame_weights(edges, a, b)
            keep = weights > 0
            buckets[category][0].extend(db[keep].tolist())
            buckets[category][1].extend(weights[keep].tolist())
            silent_seconds = float(weights[silent].sum())
            saved_n_seconds = sum(max(0, min(b, d) - max(a, c)) for c, d in predicted_n)
            if abs(silent_seconds - saved_n_seconds) > 1e-7:
                raise AssertionError(f"RMS decision differs from saved predictions: {name}")
            q = weighted_quantiles(db[keep], weights[keep], [.1, .5, .9])
            rows.append(dict(recording=name, start=a, end=b, category=category,
                             label=label or "X", seconds=b-a,
                             below_threshold_seconds=silent_seconds,
                             rms_db_p10=q[0], rms_db_median=q[1], rms_db_p90=q[2]))
        plots[name] = (times, db, reference)
        inputs[name] = {"audio_sha256": hashlib.sha256(audio.read_bytes()).hexdigest(),
                        "reference_sha256": hashlib.sha256(reference_path.read_bytes()).hexdigest(),
                        "prediction_sha256": hashlib.sha256(prediction_path.read_bytes()).hexdigest()}
    summary = {}
    for category, (values, weights) in buckets.items():
        selected = [row for row in rows if row["category"] == category]
        seconds = sum(row["seconds"] for row in selected)
        below = sum(row["below_threshold_seconds"] for row in selected)
        summary[category] = dict(seconds=seconds, intervals=len(selected),
                                 recordings=len({r["recording"] for r in selected}),
                                 below_threshold_seconds=below,
                                 below_threshold_fraction=below / seconds if seconds else None,
                                 rms_db_quantiles=weighted_quantiles(values, weights, [.1, .5, .9]))
    totals = {}
    for row in rows:
        if row["category"] == "N":
            totals[row["recording"]] = totals.get(row["recording"], 0) + row["seconds"]
    example = min(totals, key=lambda name: (-totals[name], name)) if totals else None
    output.mkdir(parents=True)
    save_csv(output / "intervals.csv", rows)
    save_json(output / "summary.json", dict(
        source_run=str(run), threshold_db=threshold_db, summary=summary,
        quantile_probabilities=[.1, .5, .9], example=example,
        example_selection="Largest total reference N duration, ties by recording ID.",
        measurement="RMS from the frozen audio path: 22,050 Hz, centred 2,048-sample frames, hop 512. Exact overlap of reference intervals with prediction cells. dB relative to each recording's peak RMS; quantiles weighted by duration.",
        interpretation="NC is mapped to N by the evaluation adapter. RMS describes energy, not perceived content or the annotator's intended harmonic label. No listening judgement or new model selection is made.",
        saved_prediction_check="RMS threshold decisions agree with saved long-window N predictions on every reference interval.",
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), inputs=inputs))
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.15), layout="constrained")
    for key, label, colour in [("chord", "Supported chord", "#0072B2"), ("N", "NC mapped to N", "#D55E00")]:
        values, weights = (np.asarray(v) for v in buckets[key])
        order = np.argsort(values)
        axes[0].plot(values[order], np.cumsum(weights[order]) / weights.sum(), label=label, color=colour)
    axes[0].axvline(threshold_db, color="black", ls="--", lw=1, label="Frozen threshold")
    axes[0].set(xlabel="RMS relative to recording peak (dB)", ylabel="Cumulative share of reference duration", xlim=(-65, 0), ylim=(0, 1))
    axes[0].legend(fontsize=8)
    if example:
        times, db, reference = plots[example]
        axes[1].plot(times, db, lw=.7, color="#0072B2")
        for a, b, label in reference:
            if label == "N":
                axes[1].axvspan(a, b, color="#D55E00", alpha=.25)
        axes[1].axhline(threshold_db, color="black", ls="--", lw=1)
        axes[1].set(xlabel="Time (s)", ylabel="Relative RMS (dB)", ylim=(-65, 2), title=f"{example}: shaded reference NC intervals")
    for extension in ("pdf", "png"):
        fig.savefig(output / f"rms_diagnostic.{extension}", dpi=180)
    plt.close(fig)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(analyze(args.run, args.data_root, args.output), indent=2))


if __name__ == "__main__":
    main()
