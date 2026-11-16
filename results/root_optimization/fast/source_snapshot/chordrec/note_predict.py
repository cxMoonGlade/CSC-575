"""Recognize chords in one audio file with a frozen note-profile front end."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(variable, "1")
os.environ.pop("LIBROSA_CACHE_DIR", None)

from .data import load_reference
from .diagnostic_player import write_diagnostic_player
from .evaluate import evaluate
from .isolated_compare import predict
from .run import ROOT, read_intervals, save_intervals, save_json

METHODS = {"note_projection": ("projection", "Note projection"),
           "note_nnls": ("harmonic", "Note NNLS")}


def _fingerprint(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def _development_record(audio):
    """Require a known development recording before adding reference playback."""
    manifest = json.loads((ROOT / "configs/guitarset_split.json").read_text())
    records = [record for record in manifest["records"]
               if record["split"] == "development" and (ROOT / record["audio"]).resolve() == audio]
    if len(records) != 1:
        raise ValueError("--player requires a GuitarSet development recording from the saved split")
    return records[0]


def predict_file(audio, config_path, output, *, player=False):
    """Save predictions and timing; optional references are used only afterward."""
    audio, config_path, output = Path(audio).resolve(), Path(config_path).resolve(), Path(output).resolve()
    if output.exists():
        raise FileExistsError(f"Choose a new output directory: {output}")
    if not audio.is_file():
        raise FileNotFoundError(f"Audio file does not exist: {audio}")
    config = json.loads(config_path.read_text())
    if config.get("status") != "frozen" or config.get("method") not in METHODS:
        raise ValueError("Use a frozen note_projection or note_nnls configuration")
    if config.get("harmonic_decay") != 0.0:
        raise ValueError("These frozen note front ends use harmonic_decay=0")
    method, label = METHODS[config["method"]]
    record = _development_record(audio) if player else None
    input_fingerprint, config_fingerprint = _fingerprint(audio), _fingerprint(config_path)

    started = time.perf_counter()
    predict(audio, method, config)
    warmup_seconds = time.perf_counter() - started
    features, intervals, _, runtime = predict(audio, method, config)
    summary = {
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "method": config["method"], "method_label": label, "decoder": "viterbi",
        "input": input_fingerprint, "config_file": config_fingerprint, "config": config,
        "audio_seconds": features["duration"], "frames": len(features["times"]),
        "tuning": features["tuning"], "prediction_intervals": len(intervals),
        "runtime_seconds": runtime, "warmup_seconds": warmup_seconds,
        "realtime_factor": runtime / features["duration"],
        "runtime_definition": "CPU wall time from audio loading through decoded interval construction, including resampling, tuning, RMS, STFT, dictionary and note features. Imports, the separate warm-up pass, raw diagnostics, hashing, file output and playback generation are excluded. No feature cache is used; the OS disk cache is not cleared.",
        "thread_settings": {key: os.environ.get(key) for key in
                            ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
    }
    output.mkdir(parents=True)
    save_intervals(output / "prediction.csv", intervals)
    save_json(output / "config.json", config)
    if record is not None:
        reference = load_reference(ROOT / record["annotation"], config["annotation"])
        # JAMS endpoints may be rounded beyond the final audio sample.
        reference = [(max(0.0, a), min(features["duration"], b), chord)
                     for a, b, chord in reference if min(features["duration"], b) > max(0.0, a)]
        save_intervals(output / "reference.csv", reference)
        tracks = {}
        baseline_path = ROOT / "results/dev_frozen/predictions" / record["id"] / "long_viterbi.csv"
        if baseline_path.is_file():
            tracks["Long STFT"] = read_intervals(baseline_path)
        tracks[label] = intervals
        player_summary = write_diagnostic_player(
            output / "playback.html", audio, f"{record['id']}: development example", reference, tracks,
            dataset="guitarset", context="Development example with performed reference labels. Predictions use the frozen configuration.",
            focus_intervals=[(0.0, min(features["duration"], 10.0))],
        )
        summary["demonstration"] = {"recording": record["id"], "split": "development", **player_summary}
        summary["development_metrics"] = evaluate(reference, intervals, features["duration"],
                                                   tolerance=config["boundary_tolerance"])
    save_json(output / "summary.json", summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/note_projection.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--player", action="store_true", help="Add reference playback for a GuitarSet development recording")
    args = parser.parse_args(argv)
    try:
        result = predict_file(args.audio, args.config, args.output, player=args.player)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(json.dumps({"method": result["method"], "audio_seconds": result["audio_seconds"],
                      "runtime_seconds": result["runtime_seconds"], "output": str(args.output.resolve())}, indent=2))


if __name__ == "__main__":
    main()
