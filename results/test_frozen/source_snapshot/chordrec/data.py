"""GuitarSet annotation loading and a progression-disjoint recording split."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re

import mir_eval.chord
import numpy as np


PITCH_CLASSES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
KNOWN_TIMING_ERRORS = {"04_BN3-154-E_comp", "04_Jazz1-200-B_comp"}
_RECORDING = re.compile(
    r"(?P<performer>\d{2})_(?P<style>[A-Za-z]+)(?P<progression>[123])-"
    r"(?P<tempo>\d+)-(?P<key>.+)_comp"
)


@lru_cache(maxsize=4096)
def reduce_label(label: str) -> str | None:
    """Reduce a Harte label using mir_eval 0.8.2's ``majmin`` vocabulary.

    The first eight relative semitone bins must match a major or minor triad
    exactly. This preserves the treatment of explicit alterations and bass
    notes in ``mir_eval.chord.majmin``; it is not a substring/quality lookup.
    N is retained, while X, malformed labels, and unsupported chords are None.
    """
    if label == "N":
        return "N"
    if not isinstance(label, str) or label == "X":
        return None
    try:
        root, bitmap, _ = mir_eval.chord.encode(label, reduce_extended_chords=False)
    except (mir_eval.chord.InvalidChordException, ValueError, TypeError):
        return None
    if root < 0:
        return None
    for quality in ("maj", "min"):
        if np.array_equal(bitmap[:8], mir_eval.chord.QUALITIES[quality][:8]):
            return f"{PITCH_CLASSES[root]}:{quality}"
    return None


def load_reference(jams_path: str | Path, annotation: str = "performed") -> list[tuple[float, float, str]]:
    """Read GuitarSet chord observations without requiring the JAMS package.

    Select performed labels from their provenance metadata rather than relying
    on annotation order. The empty-metadata chord track is the instructed chart.
    """
    if annotation not in {"performed", "instructed"}:
        raise ValueError("annotation must be 'performed' or 'instructed'")
    document = json.loads(Path(jams_path).read_text())
    candidates = []
    for item in document.get("annotations", []):
        if item.get("namespace") != "chord":
            continue
        metadata = item.get("annotation_metadata", {})
        source = str(metadata.get("data_source", "")).lower()
        rules = str(metadata.get("annotation_rules", "")).lower()
        performed = "semi-automatic chord transcription" in source or "note transcriptions" in rules
        instructed = not source.strip() and not rules.strip()
        if (annotation == "performed" and performed) or (annotation == "instructed" and instructed):
            candidates.append(item)
    if len(candidates) != 1:
        raise ValueError(f"Expected exactly one {annotation} chord annotation in {jams_path}; found {len(candidates)}")
    intervals = []
    previous_end = -np.inf
    for observation in sorted(candidates[0]["data"], key=lambda value: value["time"]):
        start = float(observation["time"])
        end = start + float(observation["duration"])
        label = observation["value"]
        if not np.isfinite([start, end]).all() or end <= start or start < -1e-9:
            raise ValueError(f"Invalid chord interval in {jams_path}: {observation}")
        if start < previous_end - 1e-9 or not isinstance(label, str):
            raise ValueError(f"Overlapping intervals or non-string chord label in {jams_path}")
        intervals.append((start, end, label))
        previous_end = end
    if not intervals:
        raise ValueError(f"Empty chord annotation in {jams_path}")
    return intervals


def make_manifest(
    data_root: str | Path,
    output_path: str | Path,
    seed: int = 20261107,
    project_root: str | Path | None = None,
) -> dict:
    """Save the prescribed split before scoring: progressions 1/2 dev, 3 test.

    Progression numbers recur across styles, tempi, keys, and performers.
    Therefore the global number, not style plus number, defines a split group.
    ``seed`` is reserved for experiment run order; the split is deterministic.
    """
    data_root = Path(data_root).resolve()
    output_path = Path(output_path)
    project_root = Path(project_root or Path(__file__).resolve().parents[1]).resolve()

    def stored_path(path: Path) -> str:
        try:
            return path.resolve().relative_to(project_root).as_posix()
        except ValueError:
            return str(path.resolve())

    records = []
    exclusions = []
    for annotation_path in sorted((data_root / "annotations").rglob("*_comp.jams")):
        recording_id = annotation_path.stem
        if recording_id in KNOWN_TIMING_ERRORS:
            exclusions.append({"id": recording_id, "reason": "Known annotation timing error", "source": "https://github.com/marl/GuitarSet/issues/5"})
            continue
        match = _RECORDING.fullmatch(recording_id)
        if not match:
            raise ValueError(f"Unrecognized GuitarSet recording ID: {recording_id}")
        audio_path = data_root / "audio_mono-mic" / f"{recording_id}_mic.wav"
        if not audio_path.is_file():
            raise FileNotFoundError(audio_path)
        metadata = match.groupdict()
        progression = int(metadata["progression"])
        records.append({
            "id": recording_id,
            "audio": stored_path(audio_path),
            "annotation": stored_path(annotation_path),
            "group": f"progression_{progression}",
            "progression": progression,
            "style": metadata["style"],
            "performer": metadata["performer"],
            "tempo": int(metadata["tempo"]),
            "key": metadata["key"],
            "split": "test" if progression == 3 else "development",
        })
    if not records:
        raise ValueError(f"No accompaniment recordings found under {data_root}")
    result = {
        "dataset": "GuitarSet 1.1.0 microphone audio, accompaniment recordings",
        "data_root": stored_path(data_root),
        "path_base": "project_root",
        "annotation": "performed",
        "run_order_seed": int(seed),
        "policy": {
            "development_progressions": [1, 2],
            "test_progressions": [3],
            "grouping": "Global progression number across every style, tempo, key, and performer",
            "selection_basis": "Pre-specified using chord sheets containing major/minor material, before predictions or evaluation",
            "scope": "One held-out progression family; recordings are not independent songs",
            "boundary_caveat": "Performed chord segmentation follows the instructed score and is not independently measured acoustic timing",
        },
        "counts": {split: sum(record["split"] == split for record in records) for split in ("development", "test")},
        "exclusions": exclusions,
        "records": records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result
