"""Compare two short-window resolutions under the same fusion rules."""
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
sys.path.insert(0, str(HERE.parent))

import numpy as np
from common import ROOT, BASE, add_common_arguments, load_records, score
from chordrec.audio import extract_features, normalize_chroma
from chordrec.model import chord_templates, decode


def confidence_weight(short, long):
    """Bound the short-window weight using the two template-score margins."""
    templates = chord_templates()
    margins = []
    for chroma in (short, long):
        scores = templates @ normalize_chroma(chroma)
        largest = np.partition(scores, -2, axis=0)[-2:]
        margins.append(largest.max(axis=0) - largest.min(axis=0))
    total = margins[0] + margins[1]
    weight = np.divide(margins[0], total, out=np.full_like(total, 0.5), where=total > 0)
    return np.clip(weight, 0.2, 0.8)


def prediction(item, short_name=None, fixed_weight=None, confidence=False):
    features = item["features"]
    if short_name is None:
        chroma = features["long"]
    elif fixed_weight is None and not confidence:
        chroma = features[short_name]
    else:
        short, long = features[short_name], features["long"]
        weight = confidence_weight(short, long) if confidence else fixed_weight
        chroma = normalize_chroma(short * weight + long * (1 - weight))
    return decode(chroma, features["rms"], item["config"], smooth=True)


def main():
    parser = add_common_arguments(argparse.ArgumentParser(description=__doc__))
    parser.add_argument("--output", type=Path, default=BASE / "runs/resolution")
    args = parser.parse_args()
    plan_path = HERE / "plan.json"
    plan = json.loads(plan_path.read_text())
    output = args.output
    if output.exists():
        raise FileExistsError("Preserve prior scores; choose a fresh output directory.")
    output.mkdir(parents=True)
    (output / "plan.json").write_bytes(plan_path.read_bytes())
    source_files = [Path(__file__), HERE.parent / "common.py",
                    ROOT / "chordrec/audio.py", ROOT / "chordrec/model.py"]
    (output / "source_hashes.json").write_text(json.dumps({str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}, indent=2) + "\n")
    items = load_records()
    assert len(items) == 119
    assert all(item["record"]["split"] == "development" and item["record"]["progression"] in (1, 2) for item in items)
    started = time.perf_counter()
    for index, item in enumerate(items, 1):
        features = item["features"]
        config = dict(item["config"], n_fft_short=4096, tuning=features["tuning"])
        assert config["switch_penalty"] == 4.0 and config["n_fft_long"] == 8192
        medium = extract_features(ROOT / item["record"]["audio"], config, required=("short",))
        np.testing.assert_array_equal(medium["times"], features["times"])
        np.testing.assert_array_equal(medium["rms"], features["rms"])
        assert medium["tuning"] == features["tuning"]
        features["medium"] = medium["short"]
        if index % 30 == 0 or index == len(items):
            print(f"Extracted 4096-sample chroma: {index}/{len(items)}", flush=True)
    extraction_seconds = time.perf_counter() - started

    settings = [
        ("single_2048", dict(short_name="short")),
        ("single_4096", dict(short_name="medium")),
        ("single_8192", {}),
        ("fixed_2048_8192_w0.2", dict(short_name="short", fixed_weight=0.2)),
        ("fixed_2048_8192_w0.5", dict(short_name="short", fixed_weight=0.5)),
        ("fixed_4096_8192_w0.2", dict(short_name="medium", fixed_weight=0.2)),
        ("fixed_4096_8192_w0.5", dict(short_name="medium", fixed_weight=0.5)),
        ("margin_2048_8192", dict(short_name="short", confidence=True)),
        ("margin_4096_8192", dict(short_name="medium", confidence=True)),
    ]
    assert [name for name, _ in settings] == plan["candidates"]
    summaries, all_rows = [], []
    for name, kwargs in settings:
        summary, rows = score(name, items, lambda item: prediction(item, **kwargs))
        summaries.append(summary)
        all_rows.extend(dict(candidate=name, **row) for row in rows)
        print(f"{name}: accuracy={summary['accuracy']:.8f}, near={summary['near_accuracy']:.8f}", flush=True)
    baseline = next(summary for summary in summaries if summary["name"] == "single_8192")
    for summary in summaries:
        delta = summary["accuracy"] - baseline["accuracy"]
        family_deltas = {family: summary["families"][family]["accuracy"] - baseline["families"][family]["accuracy"] for family in ("1", "2")}
        summary.update(delta_vs_long=delta, family_deltas_vs_long=family_deltas,
                       gate_passed=bool(delta >= 0.005 and all(value >= 0 for value in family_deltas.values())))
    result = dict(hypothesis=plan["hypothesis"], development_recordings=len(items),
                  additional_4096_extraction_seconds=extraction_seconds,
                  test_accessed=False, candidate_summaries=summaries,
                  best_by_accuracy=max(summaries, key=lambda row: row["accuracy"])["name"],
                  eligible_candidates=[row["name"] for row in summaries if row["gate_passed"]],
                  cost_note="Selection reused 2048/8192 chroma. Cached prediction timings and the extra extraction time are not complete audio-to-label inference comparisons.")
    (output / "summary.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    with (output / "per_recording.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(all_rows[0]))
        writer.writeheader(); writer.writerows(all_rows)
    print(json.dumps(dict(best=result["best_by_accuracy"], eligible=result["eligible_candidates"])), flush=True)


if __name__ == "__main__":
    main()
