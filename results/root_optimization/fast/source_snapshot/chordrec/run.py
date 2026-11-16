"""Reproducible development runs and per-recording outputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import random
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from .audio import extract_features
from .data import load_reference, make_manifest
from .evaluate import evaluate, prediction_intervals
from .model import LABELS, combine_features, decode

ROOT = Path(__file__).resolve().parents[1]
METHODS = ("short", "long", "cqt", "equal", "fixed", "adaptive")


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def save_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def read_intervals(path):
    with Path(path).open() as stream:
        return [(float(r["start"]), float(r["end"]), r["label"])
                for r in csv.DictReader(stream)]


def save_intervals(path, intervals):
    save_csv(path, [dict(start=a, end=b, label=c) for a, b, c in intervals])


def required_features(method):
    return (method,) if method in ("short", "long", "cqt") else ("short", "long")


def recognize(audio, method, config):
    """Time audio read/resampling through decoded interval construction."""
    started = time.perf_counter()
    features = extract_features(audio, config, required=required_features(method))
    chroma, weights = combine_features(features, method, config)
    decoded = prediction_intervals(
        features["times"], decode(chroma, features["rms"], config, smooth=True),
        features["duration"], LABELS,
    )
    seconds = time.perf_counter() - started
    # The raw diagnostic and scoring/plotting are outside audio-to-label timing.
    raw = prediction_intervals(
        features["times"], decode(chroma, features["rms"], config, smooth=False),
        features["duration"], LABELS,
    )
    return features, weights, decoded, raw, seconds


def summarize(rows):
    output = []
    for method in METHODS:
        for decoder in ("raw", "viterbi"):
            selected = [r for r in rows if r["method"] == method and r["decoder"] == decoder]
            if not selected:
                continue
            valid = sum(r["scoreable_seconds"] for r in selected)
            correct = sum(r["correct_seconds"] for r in selected)
            total = sum(r["audio_seconds"] for r in selected)
            matches = sum(r["boundary_matches"] for r in selected)
            refs = sum(r["reference_boundaries"] for r in selected)
            preds = sum(r["predicted_boundaries"] for r in selected)
            times = [r["runtime_seconds"] for r in selected if r["runtime_seconds"] is not None]
            errors = [r["boundary_mae_seconds"] * r["boundary_matches"] for r in selected
                      if r["boundary_mae_seconds"] is not None]
            accuracies = [r["duration_accuracy"] for r in selected if r["duration_accuracy"] is not None]
            output.append(dict(
                method=method, decoder=decoder, recordings=len(selected),
                duration_accuracy=correct / valid if valid else None,
                mean_recording_accuracy=float(np.mean(accuracies)) if accuracies else None,
                coverage=valid / total if total else None,
                boundary_precision=matches / preds if preds else 0.0,
                boundary_recall=matches / refs if refs else 0.0,
                boundary_f1=2 * matches / (refs + preds) if refs + preds else 0.0,
                boundary_mae_seconds=sum(errors) / matches if matches else None,
                total_runtime_seconds=sum(times) if times else None,
                realtime_factor=sum(times) / total if times and total else None,
            ))
    return output


def run(args):
    config = json.loads(args.config.read_text())
    if args.split == "test" and config.get("status") != "frozen":
        raise ValueError("Select and save development settings before setting status='frozen' for a test run.")
    manifest = json.loads(args.manifest.read_text())
    records = [r for r in manifest["records"] if r["split"] == args.split]
    if args.performer is not None:
        records = [r for r in records if r["id"].startswith(args.performer + "_")]
    records = sorted(records, key=lambda r: r["id"])
    if args.limit:
        records = records[:args.limit]
    if not records:
        raise ValueError("No recordings match the selection.")
    if args.output.exists() and any(args.output.iterdir()):
        raise FileExistsError(f"Choose a new output directory; {args.output} already contains a run.")
    args.output.mkdir(parents=True, exist_ok=True)
    save_json(args.output / "config.json", config)
    save_json(args.output / "selection.json", records)
    save_json(args.output / "environment.json", dict(
        python=platform.python_version(), platform=platform.platform(),
        packages={p: importlib.metadata.version(p) for p in
                  ("numpy", "scipy", "librosa", "soundfile", "mir_eval", "matplotlib")},
    ))
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted((ROOT / "chordrec").glob("*.py"))}
    save_json(args.output / "sources.json", source_hashes)
    for name in source_hashes:
        destination = args.output / "source_snapshot" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((ROOT / name).read_bytes())

    # Separate first-call/JIT overhead. Each timed method still rereads the audio
    # and computes its required features from scratch; no feature cache is used.
    started = time.perf_counter()
    warm = extract_features(ROOT / records[0]["audio"], config)
    for method in args.methods:
        chroma, _ = combine_features(warm, method, config)
        decode(chroma, warm["rms"], config, smooth=True)
    warmup_seconds = time.perf_counter() - started
    print(f"Warm-up: {warmup_seconds:.2f}s; running {len(records)} {args.split} recordings", flush=True)

    rng = random.Random(config["seed"])
    rng.shuffle(records)
    rows, order = [], []
    for index, record in enumerate(records, 1):
        reference = load_reference(ROOT / record["annotation"], config["annotation"])
        record_dir = args.output / "predictions" / record["id"]
        save_intervals(record_dir / "reference.csv", reference)
        methods = list(args.methods)
        rng.shuffle(methods)
        for method in methods:
            features, weights, decoded, raw, seconds = recognize(ROOT / record["audio"], method, config)
            order.append(dict(recording=record["id"], method=method))
            for decoder, intervals in (("raw", raw), ("viterbi", decoded)):
                metrics = evaluate(reference, intervals, features["duration"],
                                   tolerance=config["boundary_tolerance"])
                rows.append(dict(recording=record["id"], group=record["group"],
                                 split=record["split"], method=method, decoder=decoder,
                                 audio_seconds=features["duration"],
                                 runtime_seconds=seconds if decoder == "viterbi" else None,
                                 **metrics))
                save_intervals(record_dir / f"{method}_{decoder}.csv", intervals)
        save_csv(args.output / "per_recording.csv", rows)
        print(f"[{index}/{len(records)}] {record['id']}", flush=True)
    summary = summarize(rows)
    save_json(args.output / "summary.json", summary)
    save_csv(args.output / "summary.csv", summary)
    save_json(args.output / "run.json", dict(
        completed_at_utc=datetime.now(timezone.utc).isoformat(), split=args.split,
        recordings=len(records), annotation=config["annotation"],
        warmup_seconds=warmup_seconds, run_order=order,
        runtime_definition="Serial CPU wall time: audio load, resampling, shared tuning/RMS, required features, fusion, Viterbi and intervals. Feature caches disabled; imports, warm-up, raw diagnostics, scoring and output excluded. OS disk cache is not cleared.",
        interpretation="Development results with initial settings; no held-out conclusions." if args.split == "development" else "Frozen-setting held-out recording results; recordings share progression and performers.",
    ))
    from .visualize import make_example
    make_example(args.output, sorted(records, key=lambda r: r["id"])[0], config, ROOT)
    print(f"Saved results to {args.output}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare", help="Save a progression-grouped development/test split")
    prepare.add_argument("--data-root", type=Path, default=ROOT / "docs/datasets/GuitarSet")
    prepare.add_argument("--output", type=Path, default=ROOT / "configs/guitarset_split.json")
    batch = sub.add_parser("run", help="Compare front ends on selected recordings")
    batch.add_argument("--config", type=Path, default=ROOT / "configs/default.json")
    batch.add_argument("--manifest", type=Path, default=ROOT / "configs/guitarset_split.json")
    batch.add_argument("--split", choices=("development", "test"), default="development")
    batch.add_argument("--performer", default=None)
    batch.add_argument("--limit", type=int)
    batch.add_argument("--methods", nargs="+", choices=METHODS, default=list(METHODS))
    batch.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        manifest = make_manifest(args.data_root, args.output, project_root=ROOT)
        print(f"Saved {len(manifest['records'])} records to {args.output}")
    else:
        run(args)
