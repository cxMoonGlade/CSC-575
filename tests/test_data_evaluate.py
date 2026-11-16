import json
from pathlib import Path

import mir_eval.chord
import numpy as np
import pytest

from chordrec.data import load_reference, make_manifest, reduce_label
from chordrec.evaluate import evaluate, prediction_intervals, _match_boundaries


@pytest.mark.parametrize("label", [
    "C:maj", "B#:maj7", "Db:min7/5", "G:7", "A:maj6", "C:dim", "C:aug",
    "C:sus4", "C:maj(*5)", "C:maj(2)", "F:min9", "C:maj/b3", "N", "X",
])
def test_reduction_agrees_with_mir_eval_majmin(label):
    reduced = reduce_label(label)
    candidate = reduced or "C:maj"
    official = mir_eval.chord.majmin([label], [candidate])[0]
    assert official == (1.0 if reduced is not None else -1.0)


def test_reduction_enharmonic_and_unknown():
    assert reduce_label("Db:min7/5") == "C#:min"
    assert reduce_label("B#:maj7") == "C:maj"
    assert reduce_label("not a chord") is None


def test_reference_selection_uses_metadata_not_position(tmp_path):
    performed = {"namespace": "chord", "annotation_metadata": {
        "data_source": "Semi-automatic chord transcription with manual verification"},
        "data": [{"time": 0, "duration": 1, "value": "C:min"}]}
    instructed = {"namespace": "chord", "annotation_metadata": {},
        "data": [{"time": 0, "duration": 1, "value": "C:maj"}]}
    path = tmp_path / "example.jams"
    path.write_text(json.dumps({"annotations": [performed, instructed]}))
    assert load_reference(path) == [(0.0, 1.0, "C:min")]
    assert load_reference(path, "instructed") == [(0.0, 1.0, "C:maj")]


def test_midpoint_prediction_intervals_and_merging():
    result = prediction_intervals([0, 1, 2, 3], np.array([0, 0, 1, 1]), 3.5, ["C:maj", "G:maj"])
    assert result == [(0.0, 1.5, "C:maj"), (1.5, 3.5, "G:maj")]


def test_duration_weighting_coverage_and_no_fake_gap_boundaries():
    ref = [(0, 1, "C:maj"), (1, 2, "C:7"), (2, 3, "X"), (4, 5, "G:maj"), (5, 6, "N")]
    pred = [(0, 0.5, "D:maj"), (0.5, 2, "C:maj"), (2, 4, "D:maj"), (4, 5.08, "G:maj"), (5.08, 6, "N")]
    scores = evaluate(ref, pred, 6)
    assert scores["scoreable_seconds"] == 4
    assert scores["excluded_seconds"] == 2
    assert scores["correct_seconds"] == pytest.approx(3.42)
    assert scores["duration_accuracy"] == pytest.approx(3.42 / 4)
    assert scores["coverage"] == pytest.approx(2 / 3)
    assert scores["reference_boundaries"] == 1
    assert scores["predicted_boundaries"] == 2
    assert scores["boundary_matches"] == 1
    assert scores["boundary_precision"] == 0.5
    assert scores["boundary_mae_seconds"] == pytest.approx(0.08)


def test_boundary_matching_is_one_to_one_and_chooses_smallest_error():
    assert _match_boundaries([1.0], [0.95, 1.01], 0.1) == [(1.0, 1.01)]
    # Nearest-first matching at 0.09 would strand the second reference event.
    assert _match_boundaries([0.10, 0.20], [0.01, 0.11], 0.1) == [(0.10, 0.01), (0.20, 0.11)]


def test_boundaries_do_not_match_across_excluded_gap():
    ref = [(0, 0.95, "C:maj"), (0.95, 1, "G:maj"), (1, 1.01, "X"), (1.01, 2, "C:maj")]
    pred = [(0, 1.02, "C:maj"), (1.02, 2, "G:maj")]
    scores = evaluate(ref, pred, 2)
    assert scores["reference_boundaries"] == 1
    assert scores["predicted_boundaries"] == 1
    assert scores["boundary_matches"] == 0


def test_missing_predictions_count_incorrect_and_empty_reference_is_unknown():
    assert evaluate([(0, 2, "C:maj")], [(0, 1, "C:maj")], 2)["duration_accuracy"] == 0.5
    scores = evaluate([], [], 2)
    assert scores["duration_accuracy"] is None
    assert scores["coverage"] == 0
    assert scores["boundary_mae_seconds"] is None
    json.dumps(scores, allow_nan=False)


def test_manifest_keeps_progressions_together_across_style_and_performer(tmp_path):
    root = tmp_path / "guitar"
    (root / "annotations").mkdir(parents=True)
    (root / "audio_mono-mic").mkdir()
    ids = ["00_BN1-129-Eb_comp", "01_Rock1-90-C_comp", "00_Jazz2-120-A_comp",
           "00_BN3-154-E_comp", "05_SS3-98-C_comp", "04_BN3-154-E_comp"]
    for recording_id in ids:
        (root / "annotations" / f"{recording_id}.jams").write_text("{}")
        (root / "audio_mono-mic" / f"{recording_id}_mic.wav").touch()
    result = make_manifest(root, tmp_path / "manifest.json", project_root=tmp_path)
    assert len(result["records"]) == 5
    assert len(result["exclusions"]) == 1
    for record in result["records"]:
        assert record["split"] == ("test" if record["progression"] == 3 else "development")
        assert not Path(record["audio"]).is_absolute()
    assert result["counts"] == {"development": 3, "test": 2}
