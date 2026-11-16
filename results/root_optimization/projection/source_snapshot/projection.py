"""Independent note-profile projections as a control for joint NNLS fitting."""
import numpy as np

from .audio import normalize_chroma
from .harmonic import note_dictionary


def project_notes(dictionary: np.ndarray, observed: np.ndarray) -> np.ndarray:
    """Fit each nonnegative profile separately, ignoring profile overlap."""
    dictionary = np.asarray(dictionary, dtype=np.float64)
    observed = np.asarray(observed, dtype=np.float64)
    if dictionary.ndim != 2 or observed.ndim != 2 or dictionary.shape[0] != observed.shape[0]:
        raise ValueError("Dictionary and observations must share their frequency dimension")
    if not np.all(np.isfinite(dictionary)) or not np.all(np.isfinite(observed)) or np.any(dictionary < 0) or np.any(observed < 0):
        raise ValueError("Dictionary and observations must be finite and nonnegative")
    denominator = np.sum(dictionary * dictionary, axis=0)
    if np.any(denominator <= 0):
        raise ValueError("Every note profile must have positive energy")
    return np.maximum(0.0, (dictionary.T @ observed) / denominator[:, None])


def project_chroma(magnitude: np.ndarray, config: dict, tuning: float) -> np.ndarray:
    """Project onto the decay-zero dictionary and fold note strengths to chroma."""
    sr = int(config.get("sample_rate", 22050))
    n_fft = int(config.get("n_fft_long", 8192))
    midi_min = int(config.get("midi_min", 36))
    n_bins = 12 * int(config.get("n_octaves", 5))
    magnitude = np.asarray(magnitude, dtype=float)
    if magnitude.ndim != 2 or magnitude.shape[0] != n_fft // 2 + 1:
        raise ValueError("Expected a long-window magnitude STFT")
    if not np.all(np.isfinite(magnitude)) or np.any(magnitude < 0):
        raise ValueError("Magnitude spectra must be finite and nonnegative")
    dictionary, indices = note_dictionary(sr, n_fft, float(tuning), midi_min, n_bins, 0.0)
    activations = project_notes(dictionary, magnitude[indices])
    chroma = np.zeros((12, magnitude.shape[1]))
    np.add.at(chroma, (midi_min + np.arange(n_bins)) % 12, activations)
    return normalize_chroma(chroma)
