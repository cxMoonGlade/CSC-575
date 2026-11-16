"""Compare five fixed low-register score settings on development recordings."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import os
import sys
import time

for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(key, "1")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
import chordrec

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--project-root", type=Path, required=True)
parser.add_argument("--cache-dir", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.project_root / "experiments/optimization_v2"))
from common import load_records, score, EXPECTED_BASELINE_ACCURACY
import numpy as np
from chordrec.bass import decode_register, extract_register_features
from chordrec.model import decode

SETTINGS = [("baseline", 0.0, "root"), ("root_w0.1", .1, "root"),
            ("root_w0.2", .2, "root"), ("triad_w0.1", .1, "triad"), ("triad_w0.2", .2, "triad")]
plan = {
    "hypothesis": "Low-register evidence may distinguish chords sharing strong upper-register pitch classes.",
    "created_before_inference": True,
    "settings": [{"name": n, "weight": w, "evidence": e} for n, w, e in SETTINGS],
    "low_midi_range": [36, 59], "n_fft": 8192,
    "fixed": "Tuning, RMS silence threshold, frame grid and Viterbi penalty 4.",
    "empty_low_policy": "Retain baseline scores when low-register chroma has zero norm.",
    "primary_metric": "Duration-weighted major/minor accuracy on all 119 development recordings.",
    "secondary_metrics": ["root_accuracy", "other_root_seconds", "same_root_quality_seconds", "chord_to_n_seconds", "near_accuracy"],
    "selection": "Maximize primary accuracy; report both development progression families and retain adverse changes.",
    "scope": "Five settings only; no test or IDMT evaluation, no adaptive band or weight search.",
    "timing": "Selection uses cached baseline features and reports no full-pipeline speedup."
}
if args.output.exists():
    raise FileExistsError("Choose a fresh output directory")
args.output.mkdir(parents=True)
(args.output / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
source_files = [Path(__file__), Path(chordrec.__file__).parent / "bass.py",
                Path(chordrec.__file__).parent / "audio.py", Path(chordrec.__file__).parent / "model.py",
                args.project_root / "experiments/optimization_v2/common.py",
                args.project_root / "configs/frozen.json", args.project_root / "configs/guitarset_split.json"]
(args.output / "source_hashes.json").write_text(json.dumps({str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}, indent=2) + "\n")
items = load_records()
started = time.perf_counter()
max_difference = 0.0
for index, item in enumerate(items, 1):
    cached = item["features"]
    config = dict(item["config"], tuning=cached["tuning"])
    features = extract_register_features(args.project_root / item["record"]["audio"], config)
    for key in ("times", "rms"):
        np.testing.assert_array_equal(features[key], cached[key])
    difference = float(np.max(np.abs(features["long"] - cached["long"])))
    max_difference = max(max_difference, difference)
    np.testing.assert_array_equal(features["long"], cached["long"])
    cached["low"] = features["low"]
    np.testing.assert_array_equal(decode_register(cached, config, 0, "root"),
                                  decode(cached["long"], cached["rms"], config))
    if index % 30 == 0 or index == len(items):
        print(f"Low-register extraction and baseline equality: {index}/{len(items)}", flush=True)
extract_seconds = time.perf_counter() - started

summaries, rows = [], []
for name, weight, evidence in SETTINGS:
    predictions = {item["record"]["id"]: decode_register(item["features"], item["config"], weight, evidence) for item in items}
    summary, local_rows = score(name, items, lambda item: predictions[item["record"]["id"]])
    for item, row in zip(items, local_rows):
        labels = predictions[item["record"]["id"]]
        w = item["weights"]
        chord_weights = w[:24].sum(axis=0)
        same_root = w[:12] + w[12:24]
        index = np.arange(labels.size)
        root_match = np.where(labels < 24, same_root[labels % 12, index], 0.0)
        chord_correct = np.where(labels < 24, w[labels, index], 0.0)
        chord_to_n = float(chord_weights[labels == 24].sum())
        root_correct = float(root_match.sum())
        chord_seconds = float(chord_weights.sum())
        row.update(root_correct_seconds=root_correct, chord_reference_seconds=chord_seconds,
                   root_accuracy=root_correct/chord_seconds if chord_seconds else None,
                   other_root_seconds=chord_seconds-root_correct-chord_to_n,
                   same_root_quality_seconds=root_correct-float(chord_correct.sum()),
                   chord_to_n_seconds=chord_to_n)
    def extra_metrics(selected):
        fields = ("root_correct_seconds", "chord_reference_seconds", "other_root_seconds", "same_root_quality_seconds", "chord_to_n_seconds")
        result = {field: sum(row[field] for row in selected) for field in fields}
        result["root_accuracy"] = result["root_correct_seconds"]/result["chord_reference_seconds"] if result["chord_reference_seconds"] else None
        return result
    summary.update(extra_metrics(local_rows))
    for family in ("1", "2"):
        summary["families"][family].update(extra_metrics([r for r in local_rows if str(r["progression"]) == family]))
    summaries.append(summary)
    rows.extend(dict(candidate=name, **r) for r in local_rows)
    print(f"{name}: majmin={summary['accuracy']:.8f}, root={summary['root_accuracy']:.8f}, other-root={summary['other_root_seconds']:.3f}s", flush=True)
baseline = summaries[0]
assert abs(baseline["accuracy"] - EXPECTED_BASELINE_ACCURACY) < 1e-12
for summary in summaries:
    summary["delta_accuracy_pp"] = 100*(summary["accuracy"]-baseline["accuracy"])
    summary["delta_root_accuracy_pp"] = 100*(summary["root_accuracy"]-baseline["root_accuracy"])
    summary["family_delta_pp"] = {f: 100*(summary["families"][f]["accuracy"]-baseline["families"][f]["accuracy"]) for f in ("1", "2")}
result = {"plan": plan, "recordings": len(items), "candidate_summaries": summaries,
          "baseline_chroma_max_absolute_difference": max_difference,
          "baseline_decoder_exact_equal_recordings": len(items),
          "extraction_and_parity_check_seconds": extract_seconds,
          "best_by_duration_accuracy": max(summaries, key=lambda r: r["accuracy"])["name"],
          "test_or_idmt_accessed": False}
(args.output / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
with (args.output / "per_recording.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(json.dumps({"best": result["best_by_duration_accuracy"], "recordings": len(items)}), flush=True)
