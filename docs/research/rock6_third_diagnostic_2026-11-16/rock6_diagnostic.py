"""Inspect frozen rock_6 scores and their relation to decoded quality errors."""
from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def write_csv(path, rows):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def margin_sign(value, tolerance):
    if value > tolerance:
        return "correct_quality_higher"
    if value < -tolerance:
        return "opposite_quality_higher"
    return "numerical_tie"


def check_intervals(actual, expected, np):
    if len(actual) != len(expected):
        raise AssertionError("The interval count differs from the frozen predictions")
    if [x[2] for x in actual] != [x[2] for x in expected]:
        raise AssertionError("Labels differ from the frozen predictions")
    error = float(np.max(np.abs(np.asarray([x[:2] for x in actual])
                              - np.asarray([x[:2] for x in expected]))))
    if error > 1e-12:
        raise AssertionError(f"Prediction boundaries differ by {error} s")
    return {"intervals": len(actual), "labels_equal": True,
            "maximum_boundary_difference_seconds": error}


def make_figure(output, cells, features, arrays, reference, predictions, np):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    plt.rcParams.update({"font.size": 9, "axes.labelsize": 9,
                         "axes.titlesize": 10, "pdf.fonttype": 42})
    fig, axes = plt.subplots(4, 1, figsize=(9.0, 8.5), sharex=True,
                             gridspec_kw={"height_ratios": [1, 1, 1.15, 1.75]},
                             layout="constrained")
    colours = {"major": "#377eb8", "minor": "#d95f02"}
    for ax, method, label in zip(axes[:2], ("long", "projection"),
                                ("(a) Long STFT", "(b) Projection")):
        part = [row for row in cells if row["method"] == method]
        t = np.asarray([(row["start"] + row["end"]) / 2 for row in part])
        ax.plot(t, [row["major_third_activation"] for row in part],
                color=colours["major"], linewidth=.8, label="Major third")
        ax.plot(t, [row["minor_third_activation"] for row in part],
                color=colours["minor"], linewidth=.8, label="Minor third")
        ax.set_ylabel("Normalized\nactivation")
        ax.set_title(label, loc="left")
        ax.set_ylim(0, 1)
        ax.legend(loc="upper right", ncols=2, frameon=False)
        ax.grid(axis="y", alpha=.2)
    for method, colour, label in (("long", "#377eb8", "Long STFT"),
                                  ("projection", "#d95f02", "Projection")):
        part = [row for row in cells if row["method"] == method]
        t = np.asarray([(row["start"] + row["end"]) / 2 for row in part])
        axes[2].plot(t, [row["quality_margin"] for row in part], color=colour,
                     linewidth=.8, label=label)
    axes[2].axhline(0, color="black", linewidth=.7)
    axes[2].set_ylabel("Major − minor\nscore")
    axes[2].set_title("(c) Template margin at the reference root", loc="left")
    axes[2].legend(loc="upper right", ncols=2, frameon=False)
    axes[2].grid(axis="y", alpha=.2)
    ax = axes[3]
    palette = {"A": "#8dd3c7", "D": "#80b1d3", "E": "#fdb462"}
    tracks = [("Reference", reference)]
    for method, label in (("long", "Long"), ("projection", "Proj.")):
        for decoder, suffix in (("raw", "raw"), ("viterbi", "decoded")):
            tracks.append((f"{label} {suffix}", predictions[method][decoder]))
    for i, (label, intervals) in enumerate(tracks):
        for start, end, chord in intervals:
            root = chord.split(":")[0]
            ax.broken_barh([(start, end - start)], (i - .35, .7),
                           facecolors=palette.get(root, "#cccccc"),
                           edgecolors="#666666", linewidth=.15,
                           hatch="////" if chord.endswith(":min") else None)
    ax.set_yticks(range(len(tracks)), [track[0] for track in tracks])
    ax.set_ylim(len(tracks) - .5, -.5)
    ax.set_title("(d) Reference and predictions", loc="left")
    ax.set_xlabel("Time (s)")
    ax.set_xlim(reference[0][0], reference[-1][1])
    legend = [Patch(facecolor=colour, label=root) for root, colour in palette.items()]
    legend += [Patch(facecolor="#cccccc", label="Other root / N"),
               Patch(facecolor="white", edgecolor="#666666", hatch="////", label="Minor")]
    ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(.5, -.23),
              ncols=5, frameon=False)
    previous = None
    changes = []
    for start, _, label in reference:
        if label != previous:
            changes.append(start)
            previous = label
    for ax in axes[:3]:
        for start in changes[1:]:
            ax.axvline(start, color="grey", linewidth=.45, alpha=.45)
    fig.savefig(output / "rock6_diagnostic.pdf")
    fig.savefig(output / "rock6_diagnostic.png", dpi=170)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_root.resolve()
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError("Choose a new diagnostic output directory")
    output.mkdir(parents=True)
    sys.dont_write_bytecode = True
    for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMBA_NUM_THREADS"):
        os.environ[name] = "1"
    os.environ["NUMBA_CACHE_DIR"] = str(output / "numba_cache")
    os.environ["MPLCONFIGDIR"] = str(output / "matplotlib_cache")
    os.environ.pop("LIBROSA_CACHE_DIR", None)

    frozen = project / "results/root_optimization/fast"
    snapshot = frozen / "source_snapshot"
    source_hashes = read_json(frozen / "sources.json")
    checked_sources = {}
    for relative, expected in source_hashes.items():
        source = snapshot / relative
        if sha256(source) != expected:
            raise AssertionError(f"The frozen source changed: {relative}")
        checked_sources[relative] = expected
    sys.path.insert(0, str(snapshot))
    import numpy as np
    from threadpoolctl import threadpool_limits
    from chordrec.audio import normalize_chroma
    from chordrec.data import reduce_label
    from chordrec.error_analysis import error_category
    from chordrec.evaluate import prediction_intervals
    from chordrec.idmt import load_chords
    from chordrec.isolated_compare import predict
    from chordrec.model import LABELS, PITCH_CLASSES, chord_templates, combine_features, decode
    from chordrec.run import read_intervals

    audit_path = frozen / "annotation_audit.json"
    audit = next(x for x in read_json(audit_path) if x["recording"] == "rock_6")
    data = project / "docs/datasets/IDMT-SMT-Guitar-fast"
    audio, annotation = data / audit["audio"], data / audit["annotation"]
    for path, key in ((audio, "audio_sha256"), (annotation, "annotation_sha256")):
        if sha256(path) != audit[key]:
            raise AssertionError(f"The selected data changed: {path}")
    folder = frozen / "predictions/rock_6"
    reference_path = folder / "reference.csv"
    reference = read_intervals(reference_path)
    original_reference, _ = load_chords(annotation)
    if reference != original_reference:
        raise AssertionError("The saved and parsed references differ")
    configs_path = frozen / "configurations.json"
    configs = read_json(configs_path)
    methods = ("long", "projection")
    config_paths = {"long": project / "configs/frozen.json",
                    "projection": project / "configs/note_projection.json"}
    for method in methods:
        if read_json(config_paths[method]) != configs[method] or configs[method]["status"] != "frozen":
            raise AssertionError("The current and saved frozen settings differ")
        if configs[method]["switch_penalty"] != 4.0:
            raise AssertionError("This diagnosis retains the reported shared penalty")

    inputs = [audio, annotation, audit_path, reference_path, configs_path,
              frozen / "per_recording.csv", frozen / "environment.json", frozen / "sources.json"]
    inputs += list(config_paths.values())
    before_hashes = {str(path.relative_to(project)): sha256(path) for path in inputs}
    versions = {name: importlib.metadata.version(name) for name in
                ("numpy", "scipy", "librosa", "soundfile", "mir_eval", "threadpoolctl")}
    if versions != read_json(frozen / "environment.json")["packages"]:
        raise AssertionError("Package versions differ from the frozen comparison")
    with (frozen / "per_recording.csv").open() as stream:
        stored_rows = {(x["method"], x["decoder"]): x for x in csv.DictReader(stream)
                       if x["recording"] == "rock_6"}
    tolerance = 1e-12
    features_by_method, arrays, predictions = {}, {}, {}
    all_cells, frame_rows, checks = [], [], []
    summaries = {}
    label_array = np.asarray(LABELS)
    with threadpool_limits(limits=1):
        for method in methods:
            config = configs[method]
            features, decoded, raw, _ = predict(audio, method, config)
            features_by_method[method] = features
            predictions[method] = {"raw": raw, "viterbi": decoded}
            metadata_path = folder / f"{method}_features.json"
            metadata = read_json(metadata_path)
            before_hashes[str(metadata_path.relative_to(project))] = sha256(metadata_path)
            for key in ("times", "rms"):
                actual = hashlib.sha256(np.asarray(features[key]).tobytes()).hexdigest()
                if actual != metadata[f"{key}_sha256"]:
                    raise AssertionError(f"The frozen {key} hash differs for {method}")
            if features["tuning"] != metadata["tuning"] or len(features["times"]) != metadata["frames"]:
                raise AssertionError("Tuning or frame count differs")
            for decoder, intervals in predictions[method].items():
                path = folder / f"{method}_{decoder}.csv"
                before_hashes[str(path.relative_to(project))] = sha256(path)
                check = check_intervals(intervals, read_intervals(path), np)
                checks.append({"method": method, "decoder": decoder, **check})
            chroma = combine_features(features, "long", config)[0] if method == "long" else features["harmonic"]
            normalized = normalize_chroma(chroma)
            scores = chord_templates() @ normalized
            times, duration = features["times"], features["duration"]
            raw_index = decode(chroma, features["rms"], config, smooth=False)
            decoded_index = decode(chroma, features["rms"], config, smooth=True)
            for decoder, indices in (("raw", raw_index), ("viterbi", decoded_index)):
                check_intervals(prediction_intervals(times, indices, duration, LABELS),
                                predictions[method][decoder], np)
            edges = np.r_[0., (times[:-1] + times[1:]) / 2, duration]
            top = np.argmax(scores, axis=0)
            arrays[method] = {"normalized_chroma": normalized, "template_scores": scores,
                              "raw_index": raw_index, "decoded_index": decoded_index,
                              "times": times, "edges": edges, "rms": features["rms"]}
            for i, time in enumerate(times):
                row = {"method": method, "frame": i, "time": float(time),
                       "start": float(edges[i]), "end": float(edges[i + 1]),
                       "raw_label": LABELS[raw_index[i]], "decoded_label": LABELS[decoded_index[i]],
                       "best_template": LABELS[top[i]],
                       "maximizing_templates": "|".join(label_array[:24][scores[:, i] >= scores[top[i], i] - tolerance])}
                row.update({f"chroma_{note}": float(normalized[j, i]) for j, note in enumerate(PITCH_CLASSES)})
                row.update({f"score_{label}": float(scores[j, i]) for j, label in enumerate(LABELS[:24])})
                frame_rows.append(row)
            cells = []
            for start, end, original in reference:
                reduced = reduce_label(original)
                if reduced in (None, "N"):
                    continue
                root, quality = reduced.split(":")
                r = PITCH_CLASSES.index(root)
                correct = r if quality == "maj" else r + 12
                opposite = r + 12 if quality == "maj" else r
                first = max(0, int(np.searchsorted(edges, start, side="right")) - 1)
                last = min(len(times), int(np.searchsorted(edges, end, side="left")))
                other_roots = np.array([j for j in range(24) if j % 12 != r])
                for i in range(first, last):
                    a, b = max(start, float(edges[i])), min(end, float(edges[i + 1]))
                    if b <= a:
                        continue
                    margin = float(scores[correct, i] - scores[opposite, i])
                    major_third = float(normalized[(r + 4) % 12, i])
                    minor_third = float(normalized[(r + 3) % 12, i])
                    analytic = (major_third - minor_third) / np.sqrt(3)
                    if quality == "min":
                        analytic = -analytic
                    if abs(margin - analytic) > tolerance:
                        raise AssertionError("Template margin differs from the third-activation formula")
                    best_other = int(other_roots[np.argmax(scores[other_roots, i])])
                    row = {"method": method, "frame": i, "start": a, "end": b, "seconds": b - a,
                           "reference_original": original, "reference": reduced,
                           "major_third_activation": major_third, "minor_third_activation": minor_third,
                           "correct_quality_score": float(scores[correct, i]),
                           "opposite_quality_score": float(scores[opposite, i]),
                           "quality_margin": margin, "margin_sign": margin_sign(margin, tolerance),
                           "best_other_root_template": LABELS[best_other],
                           "best_other_root_score": float(scores[best_other, i]),
                           "reference_minus_best_other_root": float(scores[correct, i] - scores[best_other, i]),
                           "best_template": LABELS[top[i]],
                           "raw_label": LABELS[raw_index[i]], "decoded_label": LABELS[decoded_index[i]],
                           "raw_category": error_category(reduced, LABELS[raw_index[i]]),
                           "decoded_category": error_category(reduced, LABELS[decoded_index[i]])}
                    cells.append(row)
            all_cells.extend(cells)
            total = sum(row["seconds"] for row in cells)
            if abs(total - audit["supported_chord_seconds"]) > 1e-7:
                raise AssertionError("Frame/reference intersections do not cover the reference duration")
            categories = {}
            for decoder, column in (("raw", "raw_category"), ("viterbi", "decoded_category")):
                by_category = defaultdict(float)
                for row in cells:
                    by_category[row[column]] += row["seconds"]
                expected = stored_rows[method, decoder]
                mapping = {"correct": "chord_correct_seconds",
                           "same_root_wrong_quality": "same_root_wrong_quality_seconds",
                           "other_root": "other_root_seconds", "chord_to_n": "chord_to_n_seconds"}
                differences = {name: by_category[name] - float(expected[field]) for name, field in mapping.items()}
                maximum = max(abs(x) for x in differences.values())
                if maximum > 1e-7:
                    raise AssertionError(f"Integrated errors differ from the frozen table: {differences}")
                categories[decoder] = dict(by_category)
                checks.append({"method": method, "decoder": decoder,
                               "maximum_category_duration_difference_seconds": maximum})
            partitions = {}
            masks = {"all_reference_chords": lambda row: True,
                     "decoded_quality_errors": lambda row: row["decoded_category"] == "same_root_wrong_quality",
                     "raw_quality_errors": lambda row: row["raw_category"] == "same_root_wrong_quality",
                     "decoded_quality_error_raw_correct": lambda row: row["decoded_category"] == "same_root_wrong_quality" and row["raw_category"] == "correct"}
            for name, condition in masks.items():
                selected = [row for row in cells if condition(row)]
                seconds = sum(row["seconds"] for row in selected)
                by_sign = {sign: sum(row["seconds"] for row in selected if row["margin_sign"] == sign)
                           for sign in ("correct_quality_higher", "opposite_quality_higher", "numerical_tie")}
                by_raw = {category: sum(row["seconds"] for row in selected if row["raw_category"] == category)
                          for category in ("correct", "same_root_wrong_quality", "other_root", "chord_to_n")}
                mean_margin = sum(row["seconds"] * row["quality_margin"] for row in selected) / seconds if seconds else None
                partitions[name] = {"seconds": seconds, "margin_sign_seconds": by_sign,
                                    "raw_category_seconds": by_raw, "mean_quality_margin": mean_margin}
            summaries[method] = {"categories_seconds": categories, "partitions": partitions}

    write_csv(output / "frame_scores.csv", frame_rows)
    write_csv(output / "reference_cells.csv", all_cells)
    np.savez_compressed(output / "features.npz", **{f"{method}_{key}": value
                       for method, values in arrays.items() for key, value in values.items()})
    for method in methods:
        write_csv(output / f"{method}_quality_error_cells.csv",
                  [row for row in all_cells if row["method"] == method and row["decoded_category"] == "same_root_wrong_quality"]
                  or [{"method": method, "decoded_quality_error_seconds": 0.}])
    make_figure(output, all_cells, features_by_method, arrays, reference, predictions, np)
    for relative, expected in before_hashes.items():
        if sha256(project / relative) != expected:
            raise AssertionError(f"Input changed during diagnosis: {relative}")
    for relative, expected in checked_sources.items():
        if sha256(snapshot / relative) != expected:
            raise AssertionError(f"Frozen source changed during diagnosis: {relative}")
    summary = {"recording": "rock_6", "tempo_branch": "fast", "audio_seconds": audit["audio_seconds"],
               "reference_chord_seconds": audit["supported_chord_seconds"], "margin_tolerance": tolerance,
               "switch_penalty": 4.0, "methods": summaries,
               "scope": "Exploratory diagnosis of the previously selected recording; no parameter selection.",
               "units": "Chroma values are L2-normalized feature activations, not acoustic energy or measured played-note amplitudes."}
    write_json(output / "summary.json", summary)
    write_json(output / "validation.json", {"checks": checks, "input_hashes_unchanged": True,
               "frozen_source_hashes_verified": True, "saved_grid_rms_tuning_verified": True,
               "prediction_intervals_reproduced": True, "score_formula_verified": True,
               "saved_score_values_available": False,
               "score_validation": "Archived artifacts contain labels and grid/RMS metadata, but not score arrays. Scores were recomputed from the verified frozen source and settings; resulting labels and intervals match the archive."})
    write_json(output / "provenance.json", {"created_utc": datetime.now(timezone.utc).isoformat(),
               "python": sys.version, "packages": versions, "inputs": before_hashes,
               "frozen_sources": checked_sources, "diagnostic_script_sha256": sha256(__file__),
               "configuration_source": str(configs_path.relative_to(project)),
               "source_snapshot": str(snapshot.relative_to(project)),
               "duration_rule": "Exact intersections of original reference intervals with the recognizer's midpoint frame cells.",
               "selection": "rock_6 was selected in the existing report for the largest decoded quality-error increase."})
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
