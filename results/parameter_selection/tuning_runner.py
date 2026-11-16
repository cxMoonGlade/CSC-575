"""Bounded development-only parameter selection for the chord-recognition report.

Cached features and exact duration overlaps are used only for selection. Final
runtime experiments must use the project's uncached audio-to-label runner.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import sys
import time

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(variable, "1")
os.environ.pop("LIBROSA_CACHE_DIR", None)

import numpy as np

PENALTIES = (0.0, 0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0)
FIXED_WEIGHTS = (0.0, 0.25, 0.5, 0.75, 1.0)
THRESHOLDS = (0.25, 0.4, 0.6, 0.8, 1.0)
RADII = (0.2, 0.3, 0.4)
ANCHOR_METHODS = ("short", "long", "cqt", "equal")


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def save_csv(path, rows):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def exact_overlap_weights(times, duration, reference, labels, reduce_label):
    """Reference seconds assigned to each candidate label and frame cell."""
    times = np.asarray(times, dtype=float)
    edges = np.r_[0.0, (times[:-1] + times[1:]) / 2.0, float(duration)]
    weights = np.zeros((len(labels), len(times)), dtype=float)
    label_indices = {label: index for index, label in enumerate(labels)}
    for start, end, raw_label in reference:
        label = reduce_label(raw_label)
        if label is None:
            continue
        start, end = max(0.0, start), min(float(duration), end)
        if end <= start:
            continue
        left = max(0, int(np.searchsorted(edges, start, side="right")) - 1)
        right = min(len(times), int(np.searchsorted(edges, end, side="left")))
        if right > left:
            overlap = np.maximum(0.0, np.minimum(edges[left + 1:right + 1], end)
                                 - np.maximum(edges[left:right], start))
            weights[label_indices[label], left:right] += overlap
    return weights


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = args.project_root.resolve()
    sys.path.insert(0, str(root))
    from chordrec.audio import extract_features
    from chordrec.data import load_reference, reduce_label
    from chordrec.model import LABELS, combine_features, decode
    from chordrec.evaluate import evaluate, prediction_intervals

    config = json.loads((root / "configs/default.json").read_text())
    manifest = json.loads((root / "configs/guitarset_split.json").read_text())
    records = sorted((r for r in manifest["records"] if r["split"] == "development"), key=lambda r: r["id"])
    if len(records) != 119 or any(r["progression"] not in (1, 2) for r in records):
        raise ValueError("Expected the pre-specified 119-recording development split only.")
    plan = dict(
        objective="Maximize duration-weighted accuracy on supported reference time; no test access.",
        shared_penalty=dict(values=PENALTIES, methods=ANCHOR_METHODS,
                            criterion="Mean of four aggregate duration accuracies; ties prefer smaller penalty."),
        fixed_weight=dict(values=FIXED_WEIGHTS,
                          criterion="Aggregate duration accuracy; ties prefer weight closest to 0.5, then smaller weight."),
        adaptive=dict(thresholds=THRESHOLDS, radii_seconds=RADII,
                      stable_short_weight=0.2, change_short_weight=0.8,
                      criterion="Aggregate duration accuracy; ties prefer larger threshold, then smaller radius."),
        diagnostic_only="Boundary F1 and near-boundary accuracy are not selection objectives.",
        scope="One predeclared staged search on all development recordings. Parameters are selected once before final test evaluation.",
        records=[r["id"] for r in records],
    )
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return
    if args.output.exists() and any(args.output.iterdir()):
        raise FileExistsError("Choose a new output directory to preserve prior results.")
    args.output.mkdir(parents=True)
    save_json(args.output / "selection_plan.json", plan)
    save_json(args.output / "source_hashes.json", {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((root / "chordrec").glob("*.py"))
    })
    save_json(args.output / "input_hashes.json", {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (root / "configs/default.json", root / "configs/guitarset_split.json")
    })
    (args.output / "tuning_runner.py").write_bytes(Path(__file__).read_bytes())
    feature_started = time.perf_counter()
    prepared = []
    for index, record in enumerate(records, 1):
        features = extract_features(root / record["audio"], config)
        reference = load_reference(root / record["annotation"], config["annotation"])
        weights = exact_overlap_weights(features["times"], features["duration"], reference, LABELS, reduce_label)
        scoreable = float(weights.sum())
        prepared.append((record, features, reference, weights, scoreable))
        if index % 20 == 0 or index == len(records):
            print(f"Cached development features {index}/{len(records)}", flush=True)
    feature_seconds = time.perf_counter() - feature_started
    # Verify exact duration overlap scoring against the full project evaluator,
    # including every anchor frontend for the first development recording.
    checks = []
    check_records = [prepared[0],
                     next(item for item in prepared if item[0]["style"] == "Funk" and item[0]["progression"] == 2),
                     next(item for item in prepared if item[0]["style"] == "Jazz" and item[0]["progression"] == 1)]
    for record, features, reference, weights, scoreable in check_records:
        for method in ANCHOR_METHODS:
            chroma, _ = combine_features(features, method, config)
            decoded = decode(chroma, features["rms"], config)
            fast_correct = float(weights[decoded, np.arange(len(decoded))].sum())
            intervals = prediction_intervals(features["times"], decoded, features["duration"], LABELS)
            metrics = evaluate(reference, intervals, features["duration"], config["boundary_tolerance"])
            if not np.isclose(fast_correct, metrics["correct_seconds"], atol=1e-9, rtol=0):
                raise AssertionError("Cached duration scorer differs from the project evaluator.")
            if not np.isclose(scoreable, metrics["scoreable_seconds"], atol=1e-9, rtol=0):
                raise AssertionError("Cached scorer coverage differs from the project evaluator.")
            checks.append(dict(recording=record["id"], method=method,
                               absolute_error_seconds=abs(fast_correct - metrics["correct_seconds"])))
    save_json(args.output / "scorer_validation.json", checks)
    rows = []
    candidates = []
    selection_started = time.perf_counter()

    def score_candidate(stage, candidate_id, method, candidate_config):
        correct_total = scoreable_total = 0.0
        for record, features, reference, weights, scoreable in prepared:
            chroma, fusion_weights = combine_features(features, method, candidate_config)
            decoded = decode(chroma, features["rms"], candidate_config)
            correct = float(weights[decoded, np.arange(len(decoded))].sum())
            correct_total += correct
            scoreable_total += scoreable
            rows.append(dict(stage=stage, candidate=candidate_id, recording=record["id"],
                             method=method, correct_seconds=correct, scoreable_seconds=scoreable,
                             duration_accuracy=correct / scoreable if scoreable else None,
                             switch_penalty=candidate_config["switch_penalty"],
                             fixed_weight=candidate_config["fixed_weight"],
                             change_threshold=candidate_config["change_threshold"],
                             change_radius_seconds=candidate_config["change_radius_seconds"]))
        accuracy = correct_total / scoreable_total
        candidates.append(dict(stage=stage, candidate=candidate_id, method=method,
                               duration_accuracy=accuracy, correct_seconds=correct_total,
                               scoreable_seconds=scoreable_total,
                               switch_penalty=candidate_config["switch_penalty"],
                               fixed_weight=candidate_config["fixed_weight"],
                               change_threshold=candidate_config["change_threshold"],
                               change_radius_seconds=candidate_config["change_radius_seconds"]))
        return accuracy

    penalty_scores = []
    for penalty in PENALTIES:
        candidate_config = dict(config, switch_penalty=penalty)
        accuracies = [score_candidate("shared_penalty", f"penalty_{penalty:g}", method, candidate_config)
                      for method in ANCHOR_METHODS]
        score = float(np.mean(accuracies))
        penalty_scores.append((score, penalty))
        print(f"Shared penalty {penalty:g}: mean accuracy {score:.6f}", flush=True)
    best_score = max(row[0] for row in penalty_scores)
    penalty = min(p for score, p in penalty_scores if best_score - score <= 1e-12)
    selected_config = dict(config, switch_penalty=penalty)
    fixed_scores = []
    for weight in FIXED_WEIGHTS:
        score = score_candidate("fixed_weight", f"weight_{weight:g}", "fixed", dict(selected_config, fixed_weight=weight))
        fixed_scores.append((score, weight))
        print(f"Fixed weight {weight:g}: accuracy {score:.6f}", flush=True)
    best_score = max(row[0] for row in fixed_scores)
    weight = min((weight for score, weight in fixed_scores if best_score - score <= 1e-12), key=lambda w: (abs(w - 0.5), w))
    selected_config["fixed_weight"] = weight
    adaptive_scores = []
    for threshold in THRESHOLDS:
        for radius in RADII:
            candidate_config = dict(selected_config, change_threshold=threshold, change_radius_seconds=radius,
                                    stable_short_weight=0.2, change_short_weight=0.8)
            score = score_candidate("adaptive", f"threshold_{threshold:g}_radius_{radius:g}", "adaptive", candidate_config)
            adaptive_scores.append((score, threshold, radius))
            print(f"Adaptive threshold {threshold:g}, radius {radius:g}: accuracy {score:.6f}", flush=True)
    best_score = max(row[0] for row in adaptive_scores)
    threshold, radius = min(((threshold, radius) for score, threshold, radius in adaptive_scores if best_score - score <= 1e-12), key=lambda pair: (-pair[0], pair[1]))
    selected_config.update(change_threshold=threshold, change_radius_seconds=radius,
                           stable_short_weight=0.2, change_short_weight=0.8,
                           status="selected_on_development")
    # Choose the best single-window control using the same shared decoder.
    anchor_rows = [r for r in candidates if r["stage"] == "shared_penalty" and r["switch_penalty"] == penalty and r["method"] in ("short", "long")]
    selected_window = max(anchor_rows, key=lambda r: (r["duration_accuracy"], r["method"] == "long"))["method"]
    selected_config["selected_single_window"] = selected_window
    save_json(args.output / "selected_config.json", selected_config)
    save_json(args.output / "candidate_summary.json", candidates)
    save_csv(args.output / "candidate_summary.csv", candidates)
    save_csv(args.output / "per_recording_candidates.csv", rows)
    save_json(args.output / "selection_summary.json", dict(
        development_recordings=len(records), feature_extraction_seconds=feature_seconds,
        selection_seconds=time.perf_counter() - selection_started,
        method_settings=len(candidates), scored_config_recording_pairs=len(rows),
        selected_config=selected_config,
        selected_single_window=selected_window,
        initial_baseline_long=next(r for r in candidates if r["stage"] == "shared_penalty" and r["switch_penalty"] == 0.1 and r["method"] == "long"),
        shared_penalty_scores=[dict(penalty=p, mean_duration_accuracy=s) for s, p in penalty_scores],
        test_evaluation_performed=False,
        runtime_note="Selection used cached features and therefore is not an inference runtime comparison.",
    ))
    print("Selected config:", json.dumps(selected_config), flush=True)


if __name__ == "__main__":
    main()
