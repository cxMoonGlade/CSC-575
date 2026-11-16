"""Aligned, tuning-aware chroma front ends for the course experiments."""

from pathlib import Path

import librosa
import numpy as np
import soundfile as sf


def normalize_chroma(chroma: np.ndarray) -> np.ndarray:
    """Normalize nonzero columns without turning silence into numerical noise."""
    chroma = np.asarray(chroma, dtype=np.float64)
    norm = np.linalg.norm(chroma, axis=0, keepdims=True)
    return np.divide(chroma, norm, out=np.zeros_like(chroma), where=norm > 1e-12)


def _stft_chroma(y, sr, hop, n_fft, tuning, midi_min, n_bins):
    magnitude = np.abs(librosa.stft(
        y, n_fft=n_fft, hop_length=hop, win_length=n_fft,
        window="hann", center=True, pad_mode="constant",
    ))
    basis = librosa.filters.chroma(
        sr=sr, n_fft=n_fft, tuning=tuning, octwidth=None,
        norm=2, base_c=True,
    )
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    # Use the same semitone-centre range as the CQT. The half-semitone
    # margins cover its end bins, rather than retaining arbitrary FFT octaves.
    lower = librosa.midi_to_hz(midi_min - 0.5 + tuning)
    upper = librosa.midi_to_hz(midi_min + n_bins - 0.5 + tuning)
    basis[:, (frequencies < lower) | (frequencies >= upper)] = 0
    return normalize_chroma(basis @ magnitude)


def extract_features(
    path: str | Path,
    config: dict,
    required: tuple[str, ...] = ("short", "long", "cqt"),
) -> dict:
    """Read audio and return requested chromas on a common centred time grid.

    All processing, including file decoding, resampling and one tuning estimate,
    happens on each call. No extracted features are cached by this module.
    """
    unknown = set(required) - {"short", "long", "cqt"}
    if unknown:
        raise ValueError(f"Unknown front ends: {sorted(unknown)}")
    sr = int(config.get("sample_rate", 22050))
    hop = int(config.get("hop_length", 512))
    short_fft = int(config.get("n_fft_short", 2048))
    long_fft = int(config.get("n_fft_long", 8192))
    midi_min = int(config.get("midi_min", 36))
    n_octaves = int(config.get("n_octaves", 5))
    if min(sr, hop, short_fft, long_fft, n_octaves) <= 0:
        raise ValueError("Sample rate, hop, window lengths and octaves must be positive")
    n_bins = 12 * n_octaves
    if librosa.midi_to_hz(midi_min + n_bins - 1) >= sr / 2:
        raise ValueError("Pitch range reaches or exceeds Nyquist")
    samples, original_sr = sf.read(path, dtype="float32", always_2d=True)
    if not len(samples) or not np.all(np.isfinite(samples)):
        raise ValueError("Audio must contain finite, nonempty samples")
    original_duration = len(samples) / original_sr
    y = samples.mean(axis=1)
    if original_sr != sr:
        y = librosa.resample(y, orig_sr=original_sr, target_sr=sr, res_type="soxr_hq")

    if "tuning" in config:
        tuning = float(config["tuning"])
    elif np.max(np.abs(y)) <= 1e-12:
        tuning = 0.0
    else:
        tuning = float(librosa.estimate_tuning(
            y=y, sr=sr, n_fft=long_fft, hop_length=hop,
            fmin=librosa.midi_to_hz(midi_min),
            fmax=librosa.midi_to_hz(midi_min + n_bins - 1),
        ))

    frames = 1 + len(y) // hop
    result = {
        "times": np.arange(frames, dtype=np.float64) * hop / sr,
        "rms": librosa.feature.rms(
            y=y, frame_length=2048, hop_length=hop,
            center=True, pad_mode="constant",
        )[0].astype(np.float64),
        "duration": float(original_duration),
        "tuning": tuning,
    }
    for name, n_fft in (("short", short_fft), ("long", long_fft)):
        if name in required:
            result[name] = _stft_chroma(y, sr, hop, n_fft, tuning, midi_min, n_bins)
    if "cqt" in required:
        magnitude = np.abs(librosa.cqt(
            y, sr=sr, hop_length=hop, fmin=librosa.midi_to_hz(midi_min),
            n_bins=n_bins, bins_per_octave=12, tuning=tuning,
            window="hann", pad_mode="constant",
        ))
        chroma = np.zeros((12, magnitude.shape[1]), dtype=np.float64)
        np.add.at(chroma, (midi_min + np.arange(n_bins)) % 12, magnitude)
        result["cqt"] = normalize_chroma(chroma)
    # Fail explicitly if an implementation change breaks alignment. Padding or
    # interpolation here would quietly change the time-resolution experiment.
    for name in required:
        if result[name].shape != (12, frames):
            raise ValueError(f"{name} has {result[name].shape[1]} frames; expected {frames}")
    if result["rms"].shape != (frames,):
        raise ValueError("RMS and chroma frame grids differ")
    # Resampling rounds its output length up. For an odd-length 44.1 kHz
    # recording, that extra sample can place one centred frame just beyond
    # the actual recording duration. Remove only that bounded terminal frame,
    # after validating every transform's unmodified frame count above.
    if result["times"][-1] > original_duration:
        beyond = result["times"] > original_duration
        overrun = result["times"][-1] - original_duration
        if original_sr == sr or np.count_nonzero(beyond) != 1 or overrun > 1 / sr + 1e-12:
            raise ValueError("Frame centres extend beyond the audio duration")
        result["times"] = result["times"][~beyond]
        result["rms"] = result["rms"][~beyond]
        for name in set(required):
            result[name] = result[name][:, ~beyond]
    return result
