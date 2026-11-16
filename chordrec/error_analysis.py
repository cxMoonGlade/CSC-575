"""Partition saved chord errors by label relation and reference-boundary region."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from .data import PITCH_CLASSES
from .evaluate import _boundaries, _normalize, _scoreable_spans, evaluate
from .regions import intersection, measure, merge, read_intervals, region_scores

LABELS = tuple(f"{root}:{quality}" for root in PITCH_CLASSES for quality in ("maj", "min")) + ("N",)
MISSING = "<missing>"
UNSUPPORTED = "<unsupported>"
CATEGORIES = ("correct", "reference_n_error", "chord_to_n", "same_root_wrong_quality", "other_root", "invalid_prediction")
ERROR_CATEGORIES = CATEGORIES[1:]
REGIONS = ("all", "near", "stable")


def error_category(reference, prediction):
    """Assign one category to each supported-reference prediction pair."""
    if reference not in LABELS:
        raise ValueError("Reference label must be a supported triad or N")
    if reference == prediction:
        return "correct"
    if reference == "N":
        return "reference_n_error"
    if prediction in (MISSING, UNSUPPORTED):
        return "invalid_prediction"
    if prediction not in LABELS:
        raise ValueError("Prediction must be reduced or an explicit missing/unsupported value")
    if prediction == "N":
        return "chord_to_n"
    if reference.split(":")[0] == prediction.split(":")[0]:
        return "same_root_wrong_quality"
    return "other_root"


def _cells(reference, prediction):
    """Yield supported reference overlaps, including uncovered prediction time."""
    j = 0
    for start, end, label in reference:
        if label is None:
            continue
        cursor = start
        while j < len(prediction) and prediction[j][1] <= start:
            j += 1
        k = j
        while cursor < end:
            if k >= len(prediction) or prediction[k][0] >= end:
                yield cursor, end, label, MISSING
                break
            pstart, pend, predicted = prediction[k]
            if pend <= cursor:
                k += 1
                continue
            if pstart > cursor:
                right = min(pstart, end)
                yield cursor, right, label, MISSING
                cursor = right
                continue
            right = min(end, pend)
            yield cursor, right, label, UNSUPPORTED if predicted is None else predicted
            cursor = right
            if pend <= cursor:
                k += 1


def decompose(reference, prediction, duration, halfwidth=.2):
    """Integrate durations exactly; near windows use the existing region rule."""
    if not np.isfinite(duration) or duration <= 0:
        raise ValueError("Duration must be positive and finite")
    if not np.isfinite(halfwidth) or halfwidth <= 0:
        raise ValueError("Boundary half-width must be positive and finite")
    ref = _normalize(reference, duration)
    pred = _normalize(prediction, duration)
    spans = _scoreable_spans(ref)
    boundaries = _boundaries(ref)
    near = merge((max(a, t-halfwidth), min(b, t+halfwidth))
                 for a, b in spans for t in boundaries if a < t < b)
    confusion = {name: defaultdict(float) for name in REGIONS}
    categories = {name: {category: 0.0 for category in CATEGORIES} for name in REGIONS}
    atoms = []
    for start, end, label, predicted in _cells(ref, pred):
        category = error_category(label, predicted)
        total = end - start
        near_seconds = measure(intersection([(start, end)], near))
        stable_seconds = max(0.0, total - near_seconds)
        for name, seconds in (("all", total), ("near", near_seconds), ("stable", stable_seconds)):
            confusion[name][(label, predicted)] += seconds
            categories[name][category] += seconds
        atoms.append({"start": start, "end": end, "reference": label, "prediction": predicted,
                      "category": category, "near_seconds": near_seconds, "stable_seconds": stable_seconds})
    scoreable = sum(b-a for a, b, label in ref if label is not None)
    regions = {}
    for name in REGIONS:
        seconds = sum(categories[name].values())
        correct = categories[name]["correct"]
        regions[name] = {"scoreable_seconds": seconds, "correct_seconds": correct,
                         "error_seconds": seconds-correct,
                         "duration_accuracy": correct/seconds if seconds else None,
                         "categories_seconds": categories[name]}
    result = {"audio_seconds": float(duration), "scoreable_seconds": scoreable,
              "excluded_seconds": max(0.0, duration-scoreable), "coverage": scoreable/duration,
              "regions": regions, "confusion": confusion, "atoms": atoms}
    original = evaluate(reference, prediction, duration)
    original_regions = region_scores(reference, prediction, duration, halfwidth)
    for key in ("scoreable_seconds", "correct_seconds"):
        if abs(regions["all"][key]-original[key]) > 1e-7:
            raise AssertionError(f"Overall {key} differs from evaluator")
        for name in ("near", "stable"):
            if abs(regions[name][key]-original_regions[f"{name}_{key}"]) > 1e-7:
                raise AssertionError(f"{name} {key} differs from region evaluator")
    return result


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write_csv(path, rows):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _examples(records, method="long"):
    """Choose a median error-bearing recording and a median-time error interval."""
    examples = []
    for category in ERROR_CATEGORIES:
        candidates = [r for r in records if r["method"] == method
                      and r["analysis"]["regions"]["all"]["categories_seconds"][category] > 0]
        if not candidates:
            continue
        candidates.sort(key=lambda r: (
            r["analysis"]["regions"]["all"]["categories_seconds"][category]/r["analysis"]["scoreable_seconds"],
            r["recording"]))
        record = candidates[(len(candidates)-1)//2]
        atoms = [a for a in record["analysis"]["atoms"] if a["category"] == category]
        target = sum(a["end"]-a["start"] for a in atoms)/2
        elapsed = 0.0
        for atom in atoms:
            elapsed += atom["end"]-atom["start"]
            if elapsed >= target:
                break
        examples.append({"category": category, "method": method, "recording": record["recording"],
                         "eligible_recordings": len(candidates), "selected_order_index": (len(candidates)-1)//2,
                         "category_seconds": record["analysis"]["regions"]["all"]["categories_seconds"][category],
                         "scoreable_seconds": record["analysis"]["scoreable_seconds"],
                         "interval": atom,
                         "context_start": max(0.0, atom["start"]-2),
                         "context_end": min(record["analysis"]["audio_seconds"], atom["end"]+2)})
    return examples


def analyze_run(run, output, methods, dataset, halfwidth=.2):
    """Analyze existing Viterbi CSVs and check their saved metric totals."""
    run, output = Path(run), Path(output)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Output directory is not empty: {output}")
    with (run/"per_recording.csv").open() as stream:
        rows = [row for row in csv.DictReader(stream) if row["decoder"] == "viterbi" and row["method"] in methods]
    if not rows or {r["method"] for r in rows} != set(methods):
        raise ValueError("Requested methods are missing from saved results")
    keys = [(r["recording"], r["method"]) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate recording/method results")
    record_ids = [{r["recording"] for r in rows if r["method"] == method} for method in methods]
    if any(ids != record_ids[0] for ids in record_ids):
        raise ValueError("Methods must contain the same recordings")
    region_path = run/"regions"/"per_recording_regions.csv"
    saved_regions = {}
    if region_path.is_file():
        with region_path.open() as stream:
            saved_regions = {(r["recording"], r["method"]): r for r in csv.DictReader(stream) if r["decoder"] == "viterbi"}
    source_paths = {run/"per_recording.csv", run/"summary.json"}
    if region_path.is_file():
        source_paths.add(region_path)
    records, flat_rows = [], []
    maximum_difference = 0.0
    for row in sorted(rows, key=lambda r: (r["recording"], methods.index(r["method"]))):
        name = row["recording"]
        if Path(name).name != name:
            raise ValueError("Recording name must be a single path component")
        ref_path = run/"predictions"/name/"reference.csv"
        pred_path = run/"predictions"/name/f"{row['method']}_viterbi.csv"
        source_paths.update((ref_path, pred_path))
        result = decompose(read_intervals(ref_path), read_intervals(pred_path), float(row["audio_seconds"]), halfwidth)
        for key in ("scoreable_seconds", "correct_seconds"):
            difference = abs(result["regions"]["all"][key]-float(row[key]))
            maximum_difference = max(maximum_difference, difference)
            if difference > 1e-6:
                raise AssertionError(f"Saved {key} mismatch: {name}/{row['method']}")
        region_row = saved_regions.get((name, row["method"]), row)
        for region in ("near", "stable"):
            for key in ("scoreable_seconds", "correct_seconds"):
                saved_key = f"{region}_{key}"
                if saved_key in region_row:
                    difference = abs(result["regions"][region][key]-float(region_row[saved_key]))
                    maximum_difference = max(maximum_difference, difference)
                    if difference > 1e-6:
                        raise AssertionError(f"Saved {saved_key} mismatch: {name}/{row['method']}")
        records.append({"recording": name, "method": row["method"], "analysis": result})
        for region in REGIONS:
            value = result["regions"][region]
            flat_rows.append({"recording": name, "method": row["method"], "region": region,
                              "audio_seconds": result["audio_seconds"], "excluded_seconds": result["excluded_seconds"],
                              "coverage": result["coverage"],
                              **{key: value[key] for key in ("scoreable_seconds", "correct_seconds", "error_seconds", "duration_accuracy")},
                              **{f"{key}_seconds": value["categories_seconds"][key] for key in ERROR_CATEGORIES}})
    summary, confusion_rows = [], []
    saved_summary = json.loads((run/"summary.json").read_text())
    for method in methods:
        selected = [r["analysis"] for r in records if r["method"] == method]
        audio_seconds = sum(r["audio_seconds"] for r in selected)
        total = {"method": method, "decoder": "viterbi", "recordings": len(selected),
                 "scoreable_recordings": sum(r["scoreable_seconds"] > 0 for r in selected),
                 "audio_seconds": audio_seconds, "excluded_seconds": sum(r["excluded_seconds"] for r in selected),
                 "coverage": sum(r["scoreable_seconds"] for r in selected)/audio_seconds, "regions": {}}
        for region in REGIONS:
            categories = {c: sum(r["regions"][region]["categories_seconds"][c] for r in selected) for c in CATEGORIES}
            seconds = sum(categories.values())
            total["regions"][region] = {"scoreable_seconds": seconds, "correct_seconds": categories["correct"],
                                         "error_seconds": seconds-categories["correct"],
                                         "duration_accuracy": categories["correct"]/seconds if seconds else None,
                                         "categories_seconds": categories,
                                         "categories_fraction": {c: value/seconds if seconds else None for c, value in categories.items()}}
            for reference in LABELS:
                for prediction in LABELS+(MISSING, UNSUPPORTED):
                    seconds = sum(r["confusion"][region].get((reference, prediction), 0.0) for r in selected)
                    confusion_rows.append({"method": method, "region": region, "reference": reference,
                                           "prediction": prediction, "seconds": seconds,
                                           "category": error_category(reference, prediction)})
        old = next(row for row in saved_summary if row["method"] == method and row["decoder"] == "viterbi")
        difference = abs(total["regions"]["all"]["duration_accuracy"]-old["duration_accuracy"])
        maximum_difference = max(maximum_difference, difference)
        if difference > 1e-10:
            raise AssertionError("Aggregate accuracy differs from saved summary")
        summary.append(total)
    metadata = {"dataset": dataset, "source_run": str(run), "boundary_halfwidth_seconds": halfwidth,
                "definition": "Exact interval duration with the existing majmin reduction. Unsupported reference labels and gaps are excluded. Near is the union of reference-change neighborhoods, confined to each scoreable span; stable is the remainder.",
                "category_definitions": {
                    "correct": "Identical reduced labels, including N.",
                    "reference_n_error": "Reference N, predicted chord or missing/unsupported prediction.",
                    "chord_to_n": "Supported reference chord, predicted N.",
                    "same_root_wrong_quality": "Supported chords with the same root but different major/minor quality.",
                    "other_root": "Supported chords with different roots, regardless of quality.",
                    "invalid_prediction": "Supported reference chord, missing or unsupported prediction."},
                "interpretation": "Post-hoc description of frozen predictions. Near-boundary errors are a location category, not a causal attribution to boundary timing. IDMT NC was mapped to N under the existing evaluation policy.",
                "summary": summary,
                "validation": {"saved_metric_maximum_absolute_difference": maximum_difference,
                               "per_recording_rows": len(flat_rows), "confusion_rows": len(confusion_rows)},
                "sources": [{"path": str(path), "sha256": _sha256(path)} for path in sorted(source_paths)]}
    output.mkdir(parents=True, exist_ok=True)
    _write_csv(output/"per_recording.csv", flat_rows)
    _write_csv(output/"confusion.csv", confusion_rows)
    (output/"summary.json").write_text(json.dumps(metadata, indent=2, allow_nan=False)+"\n")
    (output/"examples.json").write_text(json.dumps({
        "selection": "For each nonempty error category in the long baseline, choose the lower median recording by category duration divided by scoreable duration among recordings with that error; break ties by ID. Select the interval containing the median elapsed error time in that recording. These post-hoc examples illustrate categories, not population representativeness.",
        "examples": _examples(records)}, indent=2, allow_nan=False)+"\n")
    return metadata


def plot_comparison(datasets, output):
    """Plot error fractions with the scoreable duration of each row shown."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    colors = ("#CC79A7", "#009E73", "#0072B2", "#D55E00", "#777777")
    names = ("Reference N error", "Chord → N", "Same root, wrong quality", "Other root", "Missing/unsupported")
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axes = plt.subplots(1, len(datasets), figsize=(7.1, 3.7), sharex=True, squeeze=False)
    max_error = 0.0
    for axis, dataset in zip(axes.flat, datasets):
        rows = [(method, region) for method in dataset["summary"] for region in REGIONS]
        for i, (method, region) in enumerate(rows):
            value = method["regions"][region]
            left = 0.0
            for category, color in zip(ERROR_CATEGORIES, colors):
                percent = 100*(value["categories_fraction"][category] or 0.0)
                axis.barh(i, percent, left=left, color=color, height=.7, linewidth=0)
                left += percent
            max_error = max(max_error, left)
            axis.text(left+.7, i, f"{left:.1f}%", va="center", fontsize=7)
        labels = []
        for method, region in rows:
            name = {"long": "Long", "adaptive": "Adaptive", "fixed": "Fusion"}[method["method"]]
            seconds = method["regions"][region]["scoreable_seconds"]
            labels.append(f"{name}: {region} ({seconds:.0f} s)")
        axis.set_yticks(range(len(rows)), labels)
        axis.invert_yaxis()
        axis.set_title(dataset["dataset"], loc="left", fontsize=9, fontweight="bold")
        axis.set_xlabel("Error duration / row's scoreable duration (%)")
        axis.grid(axis="x", alpha=.22)
        axis.set_axisbelow(True)
        axis.axhline(2.5, color="#bbbbbb", linewidth=.6)
    for axis in axes.flat:
        axis.set_xlim(0, max_error+9)
    fig.legend([Patch(facecolor=c) for c in colors], names, loc="lower center", ncol=3,
               frameon=False, fontsize=7, bbox_to_anchor=(.5, .015))
    fig.subplots_adjust(left=.20, right=.96, top=.88, bottom=.29, wspace=.95)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(output.with_suffix(".png"), dpi=240, bbox_inches="tight")
    plt.close(fig)


def plot_baseline(datasets, output):
    """Draw a single-column view of the long baseline's error composition."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    colors = ("#CC79A7", "#009E73", "#0072B2", "#D55E00", "#777777")
    names = ("Reference N error", "Chord → N", "Same root, wrong quality", "Other root", "Missing/unsupported")
    plt.rcParams.update({"font.size": 7, "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42})
    fig, axis = plt.subplots(figsize=(3.3, 2.2))
    active = set()
    labels = []
    for i, dataset in enumerate(datasets):
        result = next(row for row in dataset["summary"] if row["method"] == "long")["regions"]["all"]
        left = 0.0
        for j, (category, color) in enumerate(zip(ERROR_CATEGORIES, colors)):
            width = 100*(result["categories_fraction"][category] or 0.0)
            if width > 0:
                active.add(j)
            axis.barh(i, width, left=left, height=.48, color=color, linewidth=0)
            left += width
        axis.text(left+.65, i, f"{left:.1f}%", va="center", fontsize=7)
        name = "GuitarSet" if dataset["dataset"] == "GuitarSet" else "IDMT"
        labels.append(f"{name}\n{result['scoreable_seconds']:.1f} s")
    axis.set_yticks(range(len(datasets)), labels)
    axis.set_ylim(len(datasets)-.4, -.6)
    axis.set_xlim(0, 40)
    axis.set_xticks([0, 10, 20, 30, 40])
    axis.set_xlabel("Error / scoreable duration (%)", labelpad=3)
    axis.grid(axis="x", alpha=.2)
    axis.set_axisbelow(True)
    fig.legend([Patch(facecolor=colors[j]) for j in sorted(active)],
               [names[j] for j in sorted(active)], loc="lower center", ncol=2,
               fontsize=6, frameon=False, columnspacing=.9, handlelength=1.2,
               bbox_to_anchor=(.5, .01))
    fig.subplots_adjust(left=.21, right=.98, bottom=.37, top=.98)
    output = Path(output)
    fig.savefig(output.with_suffix(".pdf"))
    fig.savefig(output.with_suffix(".png"), dpi=300)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("results/error_analysis"))
    args = parser.parse_args()
    root = args.project_root.resolve()
    output = args.output if args.output.is_absolute() else root/args.output
    summaries = [analyze_run(root/"results/test_frozen", output/"guitarset", ["long", "adaptive"], "GuitarSet"),
                 analyze_run(root/"results/optimization_v2/external", output/"idmt", ["long", "fixed"], "IDMT-SMT-Guitar")]
    plot_comparison(summaries, output/"error_decomposition")
    plot_baseline(summaries, output/"error_baseline")
    print(f"Saved duration error analysis to {output}")


if __name__ == "__main__":
    main()
