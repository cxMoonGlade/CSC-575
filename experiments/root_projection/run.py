"""Compare one independent projection with the saved development controls."""
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
sys.path.insert(0, str(HERE.parents[1]))
import chordrec
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--project-root", type=Path, required=True)
parser.add_argument("--cache-dir", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
sys.path.insert(0, str(args.project_root / "experiments/optimization_v2"))
from common import load_records
import librosa
import numpy as np
import soundfile as sf
from chordrec.model import decode
from chordrec.projection import project_chroma
if args.output.exists():
    raise FileExistsError("Choose a fresh output directory")
args.output.mkdir(parents=True)
(args.output / "plan.md").write_bytes((HERE / "plan.md").read_bytes())
sources = [Path(__file__), Path(chordrec.__file__).parent / "projection.py", Path(chordrec.__file__).parent / "harmonic.py",
           args.project_root / "experiments/optimization_v2/common.py", args.project_root / "configs/frozen.json",
           HERE.parent / "root_harmonic/results/summary.json"]
(args.output / "source_hashes.json").write_text(json.dumps({str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}, indent=2) + "\n")
items = load_records()
rows = []
for index, item in enumerate(items, 1):
    config = item["config"]
    features = item["features"]
    started = time.perf_counter()
    y, original_sr = sf.read(args.project_root / item["record"]["audio"], dtype="float32", always_2d=True)
    y = y.mean(axis=1)
    sr = config["sample_rate"]
    if original_sr != sr:
        y = librosa.resample(y, orig_sr=original_sr, target_sr=sr, res_type="soxr_hq")
    magnitude = np.abs(librosa.stft(y, n_fft=config["n_fft_long"], hop_length=config["hop_length"],
                                   window="hann", center=True, pad_mode="constant"))[:, :len(features["times"])]
    audio_stft_seconds = time.perf_counter() - started
    started = time.perf_counter()
    chroma = project_chroma(magnitude, config, features["tuning"])
    labels = decode(chroma, features["rms"], config)
    projection_decode_seconds = time.perf_counter() - started
    w, near = item["weights"], item["near_weights"]
    positions = np.arange(labels.size)
    chord_weights = w[:24].sum(axis=0)
    roots = w[:12] + w[12:24]
    root_correct = float(np.where(labels < 24, roots[labels % 12, positions], 0.).sum())
    chord_n = float(chord_weights[labels == 24].sum())
    rows.append(dict(recording=item["record"]["id"], progression=item["record"]["progression"],
                     correct_seconds=float(w[labels, positions].sum()), scoreable_seconds=float(w.sum()),
                     near_correct_seconds=float(near[labels, positions].sum()), near_scoreable_seconds=float(near.sum()),
                     chord_seconds=float(chord_weights.sum()), root_correct_seconds=root_correct,
                     other_root_seconds=float(chord_weights.sum())-root_correct-chord_n,
                     chord_to_n_seconds=chord_n, audio_stft_seconds=audio_stft_seconds,
                     projection_decode_seconds=projection_decode_seconds))
    if index % 30 == 0 or index == len(items):
        print(f"Independent projection: {index}/{len(items)}", flush=True)
def aggregate(selected):
    fields = tuple(k for k in rows[0] if k not in ("recording", "progression"))
    out = {key: sum(row[key] for row in selected) for key in fields}
    out.update(accuracy=out["correct_seconds"]/out["scoreable_seconds"],
               root_accuracy=out["root_correct_seconds"]/out["chord_seconds"],
               near_accuracy=out["near_correct_seconds"]/out["near_scoreable_seconds"])
    return out
summary = dict(setting="independent_projection", **aggregate(rows),
               families={str(f): aggregate([row for row in rows if row["progression"] == f]) for f in (1, 2)})
controls = json.loads((HERE.parent / "root_harmonic/results/summary.json").read_text())
controls = [r for r in controls if r["setting"] in ("baseline", "decay_0")]
for control in controls:
    if abs(control["scoreable_seconds"] - summary["scoreable_seconds"]) > 1e-7:
        raise AssertionError("Control and projection reference durations differ")
summary["delta_accuracy_pp"] = {r["setting"]: 100*(summary["accuracy"]-r["accuracy"]) for r in controls}
summary["family_delta_accuracy_pp"] = {r["setting"]: {f: 100*(summary["families"][f]["accuracy"]-r["families"][f]["accuracy"]) for f in ("1", "2")} for r in controls}
result = {"summary": summary, "saved_controls": controls, "recordings": len(items), "test_or_idmt_accessed": False,
          "timing_note": "Projection timing includes dictionary construction, projection, folding and decoding. It excludes tuning and RMS, so it is not full-pipeline runtime."}
(args.output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
with (args.output / "per_recording.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows)
print(json.dumps(summary, indent=2), flush=True)
