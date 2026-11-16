"""Check the independent-projection formula and its overlap limitation."""
import numpy as np
import pytest
from scipy.optimize import nnls
from chordrec.projection import project_notes


def test_disjoint_profiles_recover_the_coefficients():
    dictionary = np.asarray([[2., 0.], [0., 3.], [0., 0.]])
    amplitudes = np.asarray([[1., .3], [.4, 2.]])
    np.testing.assert_allclose(project_notes(dictionary, dictionary @ amplitudes), amplitudes)


def test_overlapping_profiles_differ_from_joint_fit():
    dictionary = np.asarray([[1., 1.], [0., 1.]])
    observed = dictionary @ np.asarray([[1.], [0.]])
    np.testing.assert_allclose(project_notes(dictionary, observed)[:, 0], [1., .5])
    np.testing.assert_allclose(nnls(dictionary, observed[:, 0])[0], [1., 0.])


def test_zero_observation_stays_zero():
    np.testing.assert_array_equal(project_notes(np.eye(2), np.zeros((2, 3))), np.zeros((2, 3)))


def test_zero_profile_rejected():
    with pytest.raises(ValueError):
        project_notes(np.zeros((2, 1)), np.zeros((2, 3)))


def test_uncached_audio_alignment_and_tuning(tmp_path):
    import soundfile as sf
    from chordrec.audio import extract_features
    from chordrec.harmonic import extract_harmonic_features
    from chordrec.projection import extract_projected_features
    sr = 44100
    y = .2*np.sin(2*np.pi*262.7*np.arange(44101)/sr)
    path = tmp_path / "tone.wav"
    sf.write(path, y, sr)
    config = {"sample_rate": 22050, "hop_length": 512, "n_fft_long": 8192,
              "midi_min": 36, "n_octaves": 5}
    projected = extract_projected_features(path, config)
    for other in (extract_features(path, config, required=("long",)),
                  extract_harmonic_features(path, config, 0.0)):
        assert projected["tuning"] == other["tuning"]
        assert projected["duration"] == other["duration"]
        np.testing.assert_array_equal(projected["times"], other["times"])
        np.testing.assert_array_equal(projected["rms"], other["rms"])
    assert projected["harmonic"].shape == (12, projected["times"].size)


def test_silent_audio_stays_zero(tmp_path):
    import soundfile as sf
    from chordrec.projection import extract_projected_features
    path = tmp_path / "silence.wav"
    sf.write(path, np.zeros(22050), 22050)
    actual = extract_projected_features(path, {})
    assert actual["tuning"] == 0.0
    assert not np.any(actual["rms"])
    assert not np.any(actual["harmonic"])
