"""Major/minor template scores, feature fusion, and a shared Viterbi decoder."""

import numpy as np
from scipy.ndimage import maximum_filter1d
from scipy.signal import find_peaks

from .audio import normalize_chroma


PITCH_CLASSES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
LABELS = tuple(f"{root}:{quality}" for quality in ("maj", "min") for root in PITCH_CLASSES) + ("N",)


def chord_templates() -> np.ndarray:
    """Return unit-length templates ordered as LABELS, excluding N."""
    templates = np.zeros((24, 12), dtype=np.float64)
    for quality_index, third in enumerate((4, 3)):
        for root in range(12):
            templates[quality_index * 12 + root, [(root + interval) % 12 for interval in (0, third, 7)]] = 1 / np.sqrt(3)
    return templates


def combine_features(features: dict, method: str, config: dict) -> tuple[np.ndarray, np.ndarray]:
    """Return normalized chroma and each frame's short-window weight.

    For CQT, the second return value is NaN because no STFT mixture is used.
    """
    if method in ("short", "long", "cqt"):
        chroma = normalize_chroma(features[method])
        value = {"short": 1.0, "long": 0.0, "cqt": np.nan}[method]
        return chroma, np.full(chroma.shape[1], value)
    if method not in ("equal", "fixed", "adaptive"):
        raise ValueError(f"Unknown method: {method}")
    short = normalize_chroma(features["short"])
    long = normalize_chroma(features["long"])
    if short.shape != long.shape:
        raise ValueError("Short and long chroma must share the same frame grid")
    frames = short.shape[1]
    if method in ("equal", "fixed"):
        value = 0.5 if method == "equal" else float(config.get("fixed_weight", 0.5))
        weights = np.full(frames, value)
    else:
        threshold = float(config.get("change_threshold", 0.25))
        stable = float(config.get("stable_short_weight", 0.2))
        change = float(config.get("change_short_weight", 0.8))
        if not 0 <= stable <= change <= 1 or threshold < 0:
            raise ValueError("Adaptive weights must satisfy 0 <= stable <= change <= 1; threshold >= 0")
        novelty = np.zeros(frames)
        novelty[1:] = np.linalg.norm(np.diff(short, axis=1), axis=0)
        peaks, _ = find_peaks(novelty, height=threshold)
        peak_mask = np.zeros(frames, dtype=bool)
        peak_mask[peaks] = True
        sr = int(config.get("sample_rate", 22050))
        hop = int(config.get("hop_length", 512))
        seconds = max(float(config.get("change_radius_seconds", 0.20)),
                      float(config.get("n_fft_long", 8192)) / (2 * sr))
        radius = int(np.ceil(seconds * sr / hop))
        near_change = maximum_filter1d(peak_mask, size=2 * radius + 1, mode="constant", cval=False)
        weights = np.where(near_change, change, stable)
    if np.any((weights < 0) | (weights > 1)):
        raise ValueError("Fusion weights must be between 0 and 1")
    return normalize_chroma(weights[None, :] * short + (1 - weights[None, :]) * long), weights


def decode(chroma: np.ndarray, rms: np.ndarray, config: dict, smooth: bool = True) -> np.ndarray:
    """Decode cosine scores with one common switching cost and forced silence.

    N is an energy label, not a learned acoustic template. Frames below the
    configured RMS level relative to the recording peak are forced to N.
    """
    chroma = normalize_chroma(chroma)
    rms = np.asarray(rms, dtype=np.float64)
    if chroma.ndim != 2 or chroma.shape[0] != 12 or rms.shape != (chroma.shape[1],):
        raise ValueError("Expected chroma shape (12, frames) and one RMS value per frame")
    if not np.all(np.isfinite(chroma)) or not np.all(np.isfinite(rms)) or np.any(rms < 0):
        raise ValueError("Chroma and RMS must be finite; RMS must be nonnegative")
    frames = chroma.shape[1]
    if not frames:
        return np.empty(0, dtype=np.int64)
    silence_db = float(config.get("silence_db", -45.0))
    silence_level = float(np.max(rms)) * 10 ** (silence_db / 20)
    silence = (rms <= silence_level) | (rms <= 1e-12)
    emissions = np.full((25, frames), -np.inf)
    emissions[:24, :] = chord_templates() @ chroma
    emissions[:24, silence] = -np.inf
    emissions[24, silence] = 0.0
    if not smooth:
        return np.argmax(emissions, axis=0).astype(np.int64)
    penalty = float(config.get("switch_penalty", 0.1))
    if penalty < 0 or not np.isfinite(penalty):
        raise ValueError("Switch penalty must be finite and nonnegative")
    previous = emissions[:, 0].copy()
    predecessors = np.zeros((frames, 25), dtype=np.int64)
    states = np.arange(25)
    for frame in range(1, frames):
        best = int(np.argmax(previous))
        switching = previous[best] - penalty
        stay = previous >= switching
        predecessors[frame] = np.where(stay, states, best)
        previous = emissions[:, frame] + np.maximum(previous, switching)
    result = np.empty(frames, dtype=np.int64)
    result[-1] = np.argmax(previous)
    for frame in range(frames - 1, 0, -1):
        result[frame - 1] = predecessors[frame, result[frame]]
    return result
