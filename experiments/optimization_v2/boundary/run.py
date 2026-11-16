"""Evaluate the predeclared boundary-refinement grid on development audio."""

from pathlib import Path
import argparse
import hashlib
import json
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from common import ROOT, BASE, CACHE, add_common_arguments, load_records, score
import numpy as np

from refinement import refine_boundaries
from chordrec.evaluate import evaluate, prediction_intervals
from chordrec.model import LABELS, decode


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main():
    parser = add_common_arguments(argparse.ArgumentParser(description=__doc__))
    parser.add_argument("--output", type=Path, default=BASE / "runs/boundary")
    args = parser.parse_args()
    directory = args.output
    if directory.exists():
        raise FileExistsError("Choose a fresh output directory")
    directory.mkdir(parents=True)
    (directory / "plan.json").write_bytes((HERE / "plan.json").read_bytes())
    result_path = directory / "results.json"
    if result_path.exists():
        raise FileExistsError("Preserve the existing run before starting another")
    plan = json.loads((directory / "plan.json").read_text())
    items = load_records()
    assert len(items) == 119
    assert all(item["record"]["progression"] in (1, 2) for item in items)
    assert all(item["config"]["switch_penalty"] == 4 for item in items)
    summaries, rows, outputs = [], {}, {}
    settings = [("long_baseline", None, None)]
    settings += [(f"boundary_r{radius:.1f}_w{weight:.1f}", radius, weight)
                 for radius in plan["radii_seconds"] for weight in plan["short_weights"]]
    assert len(settings) == 7

    for name, radius, weight in settings:
        predictions = {}
        inference_seconds = []

        def predict(item):
            started = time.perf_counter()
            features, config = item["features"], item["config"]
            labels = decode(features["long"], features["rms"], config)
            if radius is not None:
                radius_frames = int(np.floor(radius * config["sample_rate"] / config["hop_length"]))
                labels = refine_boundaries(labels, features["short"], features["long"], radius_frames, weight)
            inference_seconds.append(time.perf_counter() - started)
            predictions[item["record"]["id"]] = labels
            return labels

        summary, details = score(name, items, predict)
        summary.update(radius_seconds=radius, short_weight=weight,
                       cached_inference_seconds=sum(inference_seconds))
        summaries.append(summary)
        rows[name] = details
        outputs[name] = predictions
        print(json.dumps({key: summary[key] for key in
                          ("name", "accuracy", "near_accuracy", "cached_inference_seconds")}), flush=True)

    baseline = summaries[0]
    for summary in summaries[1:]:
        summary["delta_percentage_points"] = 100 * (summary["accuracy"] - baseline["accuracy"])
        summary["near_delta_percentage_points"] = 100 * (summary["near_accuracy"] - baseline["near_accuracy"])
        summary["family_delta_percentage_points"] = {
            family: 100 * (summary["families"][family]["accuracy"] - baseline["families"][family]["accuracy"])
            for family in ("1", "2")
        }
        summary["passes_gate"] = (summary["delta_percentage_points"] >= 0.5 and
                                  min(summary["family_delta_percentage_points"].values()) >= 0)
    best = min(summaries[1:], key=lambda value: (-value["accuracy"], value["radius_seconds"], value["short_weight"]))

    diagnostics = {}
    for name in (baseline["name"], best["name"]):
        details = []
        shifted = shifts = changed_frames = 0
        absolute_shift_seconds = 0.0
        for item in items:
            identifier = item["record"]["id"]
            features = item["features"]
            labels = outputs[name][identifier]
            intervals = prediction_intervals(features["times"], labels, features["duration"], LABELS)
            value = evaluate(item["reference"], intervals, features["duration"], tolerance=0.1)
            details.append(dict(recording=identifier, **value))
            old = outputs[baseline["name"]][identifier]
            old_bounds = np.flatnonzero(np.diff(old)) + 1
            new_bounds = np.flatnonzero(np.diff(labels)) + 1
            np.testing.assert_array_equal(old[np.r_[0, old_bounds]], labels[np.r_[0, new_bounds]])
            np.testing.assert_array_equal(old == LABELS.index("N"), labels == LABELS.index("N"))
            delta = new_bounds - old_bounds
            shifted += int(np.count_nonzero(delta))
            shifts += delta.size
            absolute_shift_seconds += float(np.abs(delta).sum()) * item["config"]["hop_length"] / item["config"]["sample_rate"]
            changed_frames += int(np.count_nonzero(old != labels))
        hits = sum(value["boundary_matches"] for value in details)
        expected = sum(value["reference_boundaries"] for value in details)
        predicted = sum(value["predicted_boundaries"] for value in details)
        errors = [error for value in details for error in value["boundary_timing_errors_seconds"]]
        diagnostics[name] = dict(
            boundary_precision=hits / predicted if predicted else 0,
            boundary_recall=hits / expected if expected else 0,
            boundary_f1=2 * hits / (predicted + expected) if predicted + expected else 0,
            matched_boundary_mae_seconds=float(np.mean(np.abs(errors))) if errors else None,
            reference_boundaries=expected, predicted_boundaries=predicted, matched_boundaries=hits,
            shifted_boundaries=shifted, total_decoded_boundaries=shifts,
            mean_absolute_shift_seconds=absolute_shift_seconds / shifts if shifts else 0,
            changed_frames=changed_frames, rows=details,
        )
        exact_correct = sum(value["correct_seconds"] for value in details)
        cached_correct = next(value["correct_seconds"] for value in summaries if value["name"] == name)
        assert abs(exact_correct - cached_correct) < 1e-8

    save(result_path, dict(
        summaries=summaries, best_candidate=best["name"], passes_gate=best["passes_gate"],
        timing_scope="Cached long-window decoding and refinement only. Excludes audio reading, feature extraction, and file caching. Common-helper cached_prediction_seconds also includes scoring overhead.",
        test_access=False, rows=rows,
        provenance={str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in
                    (directory / "plan.json", Path(__file__), HERE / "refinement.py", HERE.parent / "common.py", CACHE / "manifest.json")},
    ))
    save(directory / "boundary_diagnostics.json", diagnostics)


if __name__ == "__main__":
    main()
