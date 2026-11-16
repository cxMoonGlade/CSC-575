"""Check saved CLI predictions and guards before recognition starts."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest
import soundfile as sf

from chordrec.isolated_compare import predict
from chordrec.note_predict import predict_file
from chordrec.run import ROOT, read_intervals


@pytest.mark.parametrize("method", ["note_projection", "note_nnls"])
def test_cli_matches_shared_predictor(tmp_path, method):
    path = tmp_path / "tone.wav"
    y = .2*np.sin(2*np.pi*261.63*np.arange(22050)/22050)
    sf.write(path, y, 22050)
    config_path = ROOT / "configs" / f"{method}.json"
    config = json.loads(config_path.read_text())
    output = tmp_path / method
    completed = subprocess.run([sys.executable, "-m", "chordrec.note_predict", "--audio", str(path),
                                "--config", str(config_path), "--output", str(output)],
                               cwd=ROOT, capture_output=True, text=True, check=True)
    printed = json.loads(completed.stdout)
    summary = json.loads((output / "summary.json").read_text())
    _, expected, _, _ = predict(path, "projection" if method == "note_projection" else "harmonic", config)
    assert read_intervals(output / "prediction.csv") == expected
    assert summary["method"] == printed["method"] == method
    assert summary["input"]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert summary["config"] == config
    assert summary["runtime_seconds"] > 0 and summary["warmup_seconds"] > 0
    assert summary["audio_seconds"] == 1.0
    assert not (output / "playback.html").exists()


def test_existing_output_is_preserved(tmp_path):
    output = tmp_path / "previous"
    output.mkdir()
    marker = output / "keep.txt"
    marker.write_text("existing result")
    with pytest.raises(FileExistsError):
        predict_file(tmp_path / "missing.wav", tmp_path / "missing.json", output)
    assert marker.read_text() == "existing result"


def test_unrecognized_audio_cannot_request_reference_player(tmp_path):
    path = tmp_path / "tone.wav"
    sf.write(path, np.zeros(22050), 22050)
    output = tmp_path / "result"
    with pytest.raises(ValueError, match="development recording"):
        predict_file(path, ROOT / "configs/note_projection.json", output, player=True)
    assert not output.exists()


def test_projection_rejects_an_inconsistent_decay(tmp_path):
    path = tmp_path / "tone.wav"
    sf.write(path, np.zeros(22050), 22050)
    config = json.loads((ROOT / "configs/note_projection.json").read_text())
    config["harmonic_decay"] = .6
    config_path = tmp_path / "wrong.json"
    config_path.write_text(json.dumps(config))
    output = tmp_path / "result"
    with pytest.raises(ValueError, match="harmonic_decay=0"):
        predict_file(path, config_path, output)
    assert not output.exists()


def test_reference_player_clips_rounded_audio_endpoint(tmp_path, monkeypatch):
    import chordrec.note_predict as module
    path = tmp_path / "tone.wav"
    sf.write(path, .2*np.sin(2*np.pi*261.63*np.arange(22050)/22050), 22050)
    monkeypatch.setattr(module, "_development_record", lambda audio: {"id": "test_development", "annotation": "unused.jams"})
    monkeypatch.setattr(module, "load_reference", lambda path, annotation: [(0., 1.00001, "C:maj")])
    output = tmp_path / "player"
    summary = predict_file(path, ROOT / "configs/note_projection.json", output, player=True)
    assert read_intervals(output / "reference.csv") == [(0., 1., "C:maj")]
    assert summary["demonstration"]["split"] == "development"
    assert "development example" in (output / "playback.html").read_text()
