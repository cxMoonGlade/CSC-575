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


def extract_projected_features(path, config):
    """Read audio and compute projected chroma without feature caching."""
    import librosa
    import soundfile as sf
    sr = int(config.get("sample_rate", 22050))
    hop = int(config.get("hop_length", 512))
    n_fft = int(config.get("n_fft_long", 8192))
    midi_min = int(config.get("midi_min", 36))
    n_bins = 12 * int(config.get("n_octaves", 5))
    if min(sr, hop, n_fft, n_bins) <= 0:
        raise ValueError("Sample rate, hop, window length and pitch range must be positive")
    if librosa.midi_to_hz(midi_min + n_bins - 1) >= sr / 2:
        raise ValueError("Pitch range reaches or exceeds Nyquist")
    samples, original_sr = sf.read(path, dtype="float32", always_2d=True)
    if not len(samples) or not np.all(np.isfinite(samples)):
        raise ValueError("Audio must contain finite, nonempty samples")
    duration = len(samples) / original_sr
    y = samples.mean(axis=1)
    if original_sr != sr:
        y = librosa.resample(y, orig_sr=original_sr, target_sr=sr, res_type="soxr_hq")
    if "tuning" in config:
        tuning = float(config["tuning"])
    elif np.max(np.abs(y)) <= 1e-12:
        tuning = 0.0
    else:
        tuning = float(librosa.estimate_tuning(
            y=y, sr=sr, n_fft=n_fft, hop_length=hop,
            fmin=librosa.midi_to_hz(midi_min), fmax=librosa.midi_to_hz(midi_min + n_bins - 1),
        ))
    frames = 1 + len(y) // hop
    times = np.arange(frames, dtype=np.float64) * hop / sr
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop,
                             center=True, pad_mode="constant")[0].astype(np.float64)
    magnitude = np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop, win_length=n_fft,
                                   window="hann", center=True, pad_mode="constant"))
    chroma = project_chroma(magnitude, config, tuning)
    if chroma.shape != (12, frames) or rms.shape != (frames,):
        raise ValueError("Projected chroma and RMS must share the baseline frame grid")
    if times[-1] > duration:
        beyond = times > duration
        if original_sr == sr or np.count_nonzero(beyond) != 1 or times[-1]-duration > 1/sr + 1e-12:
            raise ValueError("Frame centres extend beyond the audio duration")
        times, rms, chroma = times[~beyond], rms[~beyond], chroma[:, ~beyond]
    return {"times": times, "rms": rms, "duration": float(duration), "tuning": tuning,
            "harmonic": chroma, "diagnostics": {"projection_frames": frames, "dictionary_decay": 0.0}}
