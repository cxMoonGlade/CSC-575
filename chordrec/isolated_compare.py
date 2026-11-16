"""Compare frozen front ends on the prospectively selected isolated chords."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import time

import soundfile as sf

from chordrec.error_analysis import decompose
from chordrec.isolated import load_isolated
from chordrec.model import LABELS, decode
from chordrec.evaluate import prediction_intervals
from chordrec.run import recognize, save_csv, save_intervals, save_json


def predict(audio, method, config):
    if method == "long":
        features, _, decoded, raw, seconds = recognize(audio, "long", config)
        return features, decoded, raw, seconds
    started = time.perf_counter()
    if method == "projection":
        from chordrec.projection import extract_projected_features
        features = extract_projected_features(audio, config)
    else:
        from chordrec.harmonic import extract_harmonic_features
        features = extract_harmonic_features(audio, config, config["harmonic_decay"])
    decoded = prediction_intervals(features["times"],
        decode(features["harmonic"], features["rms"], config), features["duration"], LABELS)
    seconds = time.perf_counter() - started
    raw = prediction_intervals(features["times"],
        decode(features["harmonic"], features["rms"], config, smooth=False), features["duration"], LABELS)
    return features, decoded, raw, seconds


def aggregate(rows):
    scored = sum(r["scoreable_seconds"] for r in rows)
    correct = sum(r["correct_seconds"] for r in rows)
    root = sum(r["root_correct_seconds"] for r in rows)
    runtime = [r["runtime_seconds"] for r in rows if r["runtime_seconds"] is not None]
    return dict(recordings=len(rows), scoreable_seconds=scored,
                audio_seconds=sum(r["audio_seconds"] for r in rows),
                correct_seconds=correct, root_correct_seconds=root,
                duration_accuracy=correct/scored if scored else None,
                root_accuracy=root/scored if scored else None,
                other_root_seconds=sum(r["other_root_seconds"] for r in rows),
                same_root_wrong_quality_seconds=sum(r["same_root_wrong_quality_seconds"] for r in rows),
                chord_to_n_seconds=sum(r["chord_to_n_seconds"] for r in rows),
                total_runtime_seconds=sum(runtime) if runtime else None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--projection", type=Path, help="Frozen direct-projection cost control")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new output directory")
    configs = {"long":json.loads(args.baseline.read_text()),
               "harmonic":json.loads(args.candidate.read_text())}
    if args.projection:
        configs["projection"] = json.loads(args.projection.read_text())
    if any(config["status"] != "frozen" for config in configs.values()):
        raise ValueError("Both configurations must be frozen")
    for config in configs.values():
        for key in ("sample_rate", "hop_length", "n_fft_long", "midi_min", "n_octaves",
                    "silence_db", "switch_penalty"):
            if configs["long"][key] != config[key]:
                raise ValueError(f"Shared setting differs: {key}")
        if configs["long"].get("tuning") != config.get("tuning"):
            raise ValueError("Tuning policy must match")
    selection_path = args.data_root / "prospective_selection.json"
    selection = json.loads(selection_path.read_text())
    validation_path = args.data_root / "validation_manifest.json"
    validation = json.loads(validation_path.read_text())
    if hashlib.sha256(selection_path.read_bytes()).hexdigest() != validation["source_selection_sha256"]:
        raise ValueError("Prospective selection changed after data validation")
    validated = {r["audio"]:r for r in validation["recordings"]}
    members = sorted(m["name"] for m in selection["members"] if m["name"].endswith(".wav"))
    if len(members) != 88 or len(set(members)) != 88:
        raise ValueError("Expected the complete 88-recording selection")
    if set(members) != set(validated):
        raise ValueError("Selection differs from the validated recordings")
    prepared = []
    for index, member in enumerate(members):
        if not member.startswith("IDMT-SMT-GUITAR_V2/dataset1/") or ".." in Path(member).parts:
            raise ValueError("Member outside the selected archive subset")
        audio = args.data_root / member
        annotation = audio.parent.parent / "annotation" / (audio.stem + ".xml")
        reference, metadata = load_isolated(annotation)
        duration = sf.info(audio).duration
        expected = validated[member]
        if any(hashlib.sha256(path.read_bytes()).hexdigest() != expected[key]
               for path, key in ((audio, "audio_sha256"), (annotation, "annotation_sha256"))):
            raise ValueError(f"Audio or annotation changed after validation: {member}")
        if ([list(interval) for interval in reference] != expected["reference"]
                or duration != expected["duration_seconds"]):
            raise ValueError("Reference or duration differs from the frozen data check")
        if reference[-1][1] > duration:
            raise ValueError("Reference extends beyond the recording")
        prepared.append(dict(recording=f"{index:03d}", audio=audio, annotation=annotation,
                             reference=reference, metadata=metadata, duration=duration,
                             instrument=audio.parent.parent.name))
    if set(Counter(r["metadata"]["group_id"] for r in prepared).values()) != {2}:
        raise ValueError("Each of the 44 chord groups must contain two instruments")
    expected_instruments = {"Fender Strat Clean Neck SC Chords", "Ibanez Power Strat Clean Bridge HU Chords"}
    for group in {r["metadata"]["group_id"] for r in prepared}:
        if {r["instrument"] for r in prepared if r["metadata"]["group_id"] == group} != expected_instruments:
            raise ValueError("Each chord group must contain both selected instruments")
    args.output.mkdir(parents=True)
    save_json(args.output / "configurations.json", configs)
    save_json(args.output / "selection.json", selection)
    save_json(args.output / "annotation_audit.json", [{
        "recording":r["recording"], "audio":str(r["audio"]), "annotation":str(r["annotation"]),
        "reference":r["reference"], "duration":r["duration"], **r["metadata"], "instrument":r["instrument"]
        } for r in prepared])
    save_json(args.output / "inputs.json", {str(path):hashlib.sha256(path.read_bytes()).hexdigest()
        for path in [selection_path, validation_path, args.baseline, args.candidate]
        + ([args.projection] if args.projection else [])
        + [r[key] for r in prepared for key in ("audio", "annotation")]})
    source_files = sorted(Path(__file__).parent.glob("*.py"))
    save_json(args.output / "sources.json", {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files})
    for path in source_files:
        target = args.output / "source_snapshot" / path.name
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(path.read_bytes())
    save_json(args.output / "environment.json", dict(python=platform.python_version(),
        platform=platform.platform(), packages={p:importlib.metadata.version(p) for p in
        ("numpy", "scipy", "librosa", "soundfile", "mir_eval")},
        thread_environment={key:os.environ.get(key) for key in
        ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}))
    started = time.perf_counter()
    for method, config in configs.items():
        predict(prepared[0]["audio"], method, config)
    save_json(args.output / "warmup.json", {"seconds":time.perf_counter()-started})
    jobs = [(record, method) for record in prepared for method in configs]
    random.Random(20261109).shuffle(jobs)
    rows = []
    for i, (record, method) in enumerate(jobs, 1):
        features, decoded, raw, seconds = predict(record["audio"], method, configs[method])
        directory = args.output / "predictions" / record["recording"]
        directory.mkdir(parents=True, exist_ok=True)
        save_intervals(directory / "reference.csv", record["reference"])
        for decoder, predictions in (("viterbi", decoded), ("raw", raw)):
            score = decompose(record["reference"], predictions, record["duration"])["regions"]["all"]
            categories = score["categories_seconds"]
            rows.append(dict(recording=record["recording"], group=record["metadata"]["group_id"],
                instrument=record["instrument"], fingering=record["metadata"]["fingering"],
                quality=record["metadata"]["quality"], method=method, decoder=decoder,
                audio_seconds=record["duration"], scoreable_seconds=score["scoreable_seconds"],
                correct_seconds=score["correct_seconds"], duration_accuracy=score["duration_accuracy"],
                root_correct_seconds=score["correct_seconds"]+categories["same_root_wrong_quality"],
                other_root_seconds=categories["other_root"],
                same_root_wrong_quality_seconds=categories["same_root_wrong_quality"],
                chord_to_n_seconds=categories["chord_to_n"],
                runtime_seconds=seconds if decoder=="viterbi" else None))
            save_intervals(directory / f"{method}_{decoder}.csv", predictions)
        if "diagnostics" in features:
            save_json(directory / f"{method}_diagnostics.json", features["diagnostics"])
        if i % 32 == 0:
            print(f"Completed {i}/{len(jobs)} audio-to-label runs", flush=True)
    save_csv(args.output / "per_recording.csv", rows)
    summary = []
    for method in configs:
        for decoder in ("raw", "viterbi"):
            part = [r for r in rows if r["method"] == method and r["decoder"] == decoder]
            summary.append(dict(method=method, decoder=decoder, **aggregate(part),
                instruments={key:aggregate([r for r in part if r["instrument"]==key])
                             for key in sorted({r["instrument"] for r in part})}))
    save_json(args.output / "summary.json", summary)
    save_json(args.output / "protocol.json", dict(
        order_seed=20261109, recording_groups=44,
        metric="Exact duration accuracy on the first-onset to last-offset chord span. Root accuracy counts the correct root regardless of major/minor quality; a predicted N is an error.",
        runtime="Uncached file loading, resampling, tuning, RMS, required spectral features, dictionary construction and NNLS when used, decoding, and interval construction. Imports, warm-up, raw diagnostics, scoring and writing are excluded.",
        scope="Isolated guitar chords from a separate recording session; paired fingerings across instruments. No new-song generalization claim."))
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
