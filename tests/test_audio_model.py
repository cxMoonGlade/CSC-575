import numpy as np
import pytest
import soundfile as sf

from chordrec.audio import extract_features
from chordrec.evaluate import prediction_intervals
from chordrec.model import LABELS, chord_templates, combine_features, decode


def test_synthetic_chord_audio_has_aligned_features_and_c_first_order(tmp_path):
    sr = 44100
    t = np.arange(sr * 2) / sr
    # An A-major triad, written as stereo at the dataset's original sample rate.
    y = sum(np.sin(2 * np.pi * (440 * 2 ** ((midi - 69) / 12)) * t)
            for midi in (69, 73, 76)) / 6
    path = tmp_path / "triad.wav"
    sf.write(path, np.column_stack([y, y]), sr)
    result = extract_features(path, {"tuning": 0})
    expected_frames = 1 + 44100 // 512
    assert result["times"].shape == result["rms"].shape == (expected_frames,)
    np.testing.assert_allclose(np.diff(result["times"]), 512 / 22050)
    assert result["duration"] == 2
    inner = (result["times"] > 0.4) & (result["times"] < 1.6)
    for method in ("short", "long", "cqt"):
        chroma = result[method]
        assert chroma.shape == (12, expected_frames)
        np.testing.assert_allclose(np.linalg.norm(chroma, axis=0), 1, atol=1e-6)
        predictions = decode(chroma, result["rms"], {}, smooth=False)
        assert np.mean(predictions[inner] == LABELS.index("A:maj")) > 0.95


def test_all_silent_audio_remains_finite_and_no_chord(tmp_path):
    path = tmp_path / "silence.wav"
    sf.write(path, np.zeros(22050), 22050)
    result = extract_features(path, {})
    for method in ("short", "long", "cqt", "equal", "fixed", "adaptive"):
        chroma, _ = combine_features(result, method, {})
        assert np.all(chroma == 0)
        assert np.all(decode(chroma, result["rms"], {}) == LABELS.index("N"))


def test_positive_tuning_is_shared_without_rotating_pitch_classes(tmp_path):
    sr = 22050
    t = np.arange(sr * 2) / sr
    tuning = 0.27  # C#4 sharpened by 27 cents, not shifted to another pitch class.
    frequency = 440 * 2 ** ((61 + tuning - 69) / 12)
    path = tmp_path / "sharp_c_sharp.wav"
    sf.write(path, 0.5 * np.sin(2 * np.pi * frequency * t), sr)
    result = extract_features(path, {})
    assert abs(result["tuning"] - tuning) < 0.04
    inner = (result["times"] > 0.4) & (result["times"] < 1.6)
    for method in ("short", "long", "cqt"):
        assert np.all(np.argmax(result[method][:, inner], axis=0) == 1)


@pytest.mark.filterwarnings("ignore:n_fft=.* is too large for input signal of length=.*:UserWarning")
def test_resampling_rounding_does_not_create_frame_past_audio_end(tmp_path):
    sr = 44100
    samples = np.arange(1023) / sr
    path = tmp_path / "odd_length.wav"
    sf.write(path, 0.5 * np.sin(2 * np.pi * 440 * samples), sr)
    features = extract_features(path, {"tuning": 0.0})
    assert features["duration"] == 1023 / sr
    np.testing.assert_array_equal(features["times"], [0.0])
    assert features["rms"].shape == (1,)
    for method in ("short", "long", "cqt"):
        assert features[method].shape == (12, 1)
        indices = decode(features[method], features["rms"], {})
        intervals = prediction_intervals(features["times"], indices, features["duration"], LABELS)
        assert intervals[0][0] == 0
        assert intervals[-1][1] == features["duration"]


def test_adaptive_window_expands_both_sides_of_change():
    short = np.zeros((12, 80))
    short[0, :40] = 1
    short[7, 40:] = 1
    long = np.ones_like(short)
    _, weights = combine_features({"short": short, "long": long}, "adaptive", {})
    assert weights[35] == weights[45] == 0.8
    assert weights[10] == weights[70] == 0.2
    # A tiny requested radius must still account for the long window's half width.
    _, weights = combine_features({"short": short, "long": long}, "adaptive", {"change_radius_seconds": 0})
    assert weights[33] == weights[47] == 0.8


def test_decoder_suppresses_brief_flip_but_preserves_silence():
    templates = chord_templates()
    c = LABELS.index("C:maj")
    g = LABELS.index("G:maj")
    chroma = np.repeat(templates[c, :, None], 15, axis=1)
    chroma[:, 7] = templates[g]
    raw = decode(chroma, np.ones(15), {}, smooth=False)
    assert raw[7] == g
    smoothed = decode(chroma, np.ones(15), {"switch_penalty": 0.5})
    assert np.all(smoothed == c)
    rms = np.ones(15)
    rms[7] = 0
    assert decode(chroma, rms, {"switch_penalty": 100})[7] == LABELS.index("N")


@pytest.mark.parametrize("root", range(12))
@pytest.mark.parametrize("quality", ("maj", "min"))
def test_every_template_decodes_to_its_label(root, quality):
    label = LABELS.index(f"{LABELS[root].split(':')[0]}:{quality}")
    chroma = chord_templates()[label, :, None]
    assert decode(chroma, np.ones(1), {}, smooth=False).item() == label


def test_fixed_fusion_endpoints_recover_single_front_ends():
    features = {"short": np.eye(12), "long": np.roll(np.eye(12), 1, axis=0)}
    for weight, method in ((0, "long"), (1, "short")):
        result, _ = combine_features(features, "fixed", {"fixed_weight": weight})
        np.testing.assert_allclose(result, features[method])
