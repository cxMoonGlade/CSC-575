"""Harmonic note fitting on the baseline STFT frequency range."""
import numpy as np
from scipy.optimize import nnls
from .audio import normalize_chroma


def _window_response(offset, n_fft):
    """Evaluate the DFT of a periodic Hann window at fractional bin offsets."""
    def rectangular(value):
        return n_fft * np.sinc(value) / np.sinc(value / n_fft) * np.exp(-1j * np.pi * (n_fft - 1) * value / n_fft)
    return .5 * rectangular(offset) - .25 * rectangular(offset - 1) - .25 * rectangular(offset + 1)


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


def extract_harmonic_features(path, config, decay):
    """Read audio and compute aligned harmonic chroma without feature caching."""
    import librosa
    import soundfile as sf
    sr = int(config.get('sample_rate', 22050))
    hop = int(config.get('hop_length', 512))
    n_fft = int(config.get('n_fft_long', 8192))
    midi_min = int(config.get('midi_min', 36))
    n_bins = 12 * int(config.get('n_octaves', 5))
    if min(sr, hop, n_fft, n_bins) <= 0:
        raise ValueError('Sample rate, hop, window length and pitch range must be positive')
    if librosa.midi_to_hz(midi_min + n_bins - 1) >= sr / 2:
        raise ValueError('Pitch range reaches or exceeds Nyquist')
    samples, original_sr = sf.read(path, dtype='float32', always_2d=True)
    if not len(samples) or not np.all(np.isfinite(samples)):
        raise ValueError('Audio must contain finite, nonempty samples')
    duration = len(samples) / original_sr
    y = samples.mean(axis=1)
    if original_sr != sr:
        y = librosa.resample(y, orig_sr=original_sr, target_sr=sr, res_type='soxr_hq')
    if 'tuning' in config:
        tuning = float(config['tuning'])
    elif np.max(np.abs(y)) <= 1e-12:
        tuning = 0.0
    else:
        tuning = float(librosa.estimate_tuning(y=y, sr=sr, n_fft=n_fft, hop_length=hop,
            fmin=librosa.midi_to_hz(midi_min), fmax=librosa.midi_to_hz(midi_min + n_bins - 1)))
    frames = 1 + len(y) // hop
    times = np.arange(frames, dtype=np.float64) * hop / sr
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop,
                              center=True, pad_mode='constant')[0].astype(np.float64)
    magnitude = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop, win_length=n_fft,
                                    window='hann', center=True, pad_mode='constant'))
    chroma, diagnostics = fit_chroma(magnitude, config, tuning, decay)
    if chroma.shape != (12, frames) or rms.shape != (frames,):
        raise ValueError('Harmonic chroma and RMS must share the baseline frame grid')
    if times[-1] > duration:
        beyond = times > duration
        if original_sr == sr or np.count_nonzero(beyond) != 1 or times[-1]-duration > 1/sr + 1e-12:
            raise ValueError('Frame centres extend beyond the audio duration')
        times, rms, chroma = times[~beyond], rms[~beyond], chroma[:, ~beyond]
    return {'times': times, 'rms': rms, 'duration': float(duration), 'tuning': tuning,
            'harmonic': chroma, 'diagnostics': diagnostics}
