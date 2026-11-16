"""Harmonic note fitting on the baseline STFT frequency range."""
from functools import lru_cache
import numpy as np
from scipy.optimize import nnls
from .audio import normalize_chroma


def _window_response(offset, n_fft):
    """Evaluate the DFT of a periodic Hann window at fractional bin offsets."""
    def rectangular(value):
        return n_fft * np.sinc(value) / np.sinc(value / n_fft) * np.exp(-1j * np.pi * (n_fft - 1) * value / n_fft)
    return .5 * rectangular(offset) - .25 * rectangular(offset - 1) - .25 * rectangular(offset + 1)


@lru_cache(maxsize=128)
def note_dictionary(sr, n_fft, tuning, midi_min, n_bins, decay):
    """Return unit-sine harmonic profiles and the retained FFT-bin indices.

    Each profile sums the magnitudes of separately windowed sine partials.
    Partials at or above Nyquist are omitted. Observation bins match the
    baseline pitch span, so high-frequency evidence is not added.
    """
    if not 0 <= decay < 1:
        raise ValueError('Harmonic decay must satisfy 0 <= decay < 1')
    if min(sr, n_fft, n_bins) <= 0 or not np.isfinite(tuning):
        raise ValueError('Dictionary dimensions and tuning must be valid')
    frequencies = np.arange(n_fft // 2 + 1) * sr / n_fft
    lower = 440 * 2 ** ((midi_min - .5 + tuning - 69) / 12)
    upper = 440 * 2 ** ((midi_min + n_bins - .5 + tuning - 69) / 12)
    indices = np.flatnonzero((frequencies >= lower) & (frequencies < upper))
    dictionary = np.zeros((len(indices), n_bins))
    for column, midi in enumerate(range(midi_min, midi_min + n_bins)):
        fundamental = 440 * 2 ** ((midi + tuning - 69) / 12)
        for harmonic in range(1, int(np.ceil(sr / 2 / fundamental))):
            weight = decay ** (harmonic - 1)
            if weight < 1e-8:
                break
            centre = harmonic * fundamental * n_fft / sr
            profile = np.abs((_window_response(indices - centre, n_fft)
                              - _window_response(indices + centre, n_fft)) / (2j))
            dictionary[:, column] += weight * profile
    # One scalar keeps activation units consistent across pitches.
    dictionary /= n_fft / 4
    dictionary.setflags(write=False)
    indices.setflags(write=False)
    return dictionary, indices


def fit_chroma(magnitude, config, tuning, decay):
    """Fit nonnegative note amplitudes frame by frame, then fold to chroma."""
    sr = int(config.get('sample_rate', 22050))
    n_fft = int(config.get('n_fft_long', 8192))
    midi_min = int(config.get('midi_min', 36))
    n_bins = 12 * int(config.get('n_octaves', 5))
    magnitude = np.asarray(magnitude, dtype=float)
    if magnitude.ndim != 2 or magnitude.shape[0] != n_fft // 2 + 1:
        raise ValueError('Expected a long-window magnitude STFT')
    if not np.all(np.isfinite(magnitude)) or np.any(magnitude < 0):
        raise ValueError('Magnitude spectra must be finite and nonnegative')
    dictionary, indices = note_dictionary(sr, n_fft, float(tuning), midi_min, n_bins, float(decay))
    observed = magnitude[indices]
    activations = np.empty((n_bins, observed.shape[1]))
    residuals = np.empty(observed.shape[1])
    for frame in range(observed.shape[1]):
        activations[:, frame], residuals[frame] = nnls(dictionary, observed[:, frame], maxiter=10*n_bins)
    chroma = np.zeros((12, observed.shape[1]))
    np.add.at(chroma, (midi_min + np.arange(n_bins)) % 12, activations)
    norms = np.linalg.norm(observed, axis=0)
    relative = np.divide(residuals, norms, out=np.zeros_like(norms), where=norms > 1e-12)
    return normalize_chroma(chroma), {
        'relative_residual_mean': float(relative.mean()),
        'relative_residual_max': float(relative.max(initial=0)),
        'nnls_frames': observed.shape[1],
    }
