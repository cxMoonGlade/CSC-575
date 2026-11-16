"""Move existing chord boundaries using local template scores."""

import numpy as np

from chordrec.audio import normalize_chroma
from chordrec.model import LABELS, chord_templates


def refine_boundaries(labels, short_chroma, long_chroma, radius_frames, short_weight):
    """Refine timing while preserving the decoded chord sequence and silence.

    Boundaries are visited from left to right. Each proposed split maximizes
    the left/right chord scores within its search interval. Bounds retain at
    least one frame per chord and prevent crossing neighbouring boundaries.
    A tied score keeps the split closest to its original position.
    """
    labels = np.asarray(labels)
    short = np.asarray(short_chroma, dtype=np.float64)
    long = np.asarray(long_chroma, dtype=np.float64)
    if labels.ndim != 1 or labels.dtype.kind not in "iu":
        raise ValueError("Expected a one-dimensional integer label array")
    if np.any((labels < 0) | (labels >= len(LABELS))):
        raise ValueError("Label index is outside the chord vocabulary")
    if short.shape != (12, labels.size) or long.shape != short.shape:
        raise ValueError("Both chromas must have shape (12, number of labels)")
    if not np.isfinite(short).all() or not np.isfinite(long).all():
        raise ValueError("Chroma values must be finite")
    if int(radius_frames) != radius_frames or radius_frames < 0:
        raise ValueError("The search radius must be a nonnegative frame count")
    if not 0 <= short_weight <= 1:
        raise ValueError("Short-window weight must lie between zero and one")
    radius_frames = int(radius_frames)
    if labels.size == 0 or radius_frames == 0:
        return labels.copy()

    original = np.r_[0, np.flatnonzero(np.diff(labels)) + 1, labels.size]
    identities = labels[original[:-1]]
    refined = original.copy()
    # Mix cosine scores, without renormalizing the feature mixture.
    evidence = short_weight * normalize_chroma(short)
    evidence += (1 - short_weight) * normalize_chroma(long)
    emissions = chord_templates() @ evidence
    silence_label = LABELS.index("N")

    for index in range(1, len(original) - 1):
        left_label, right_label = identities[index - 1:index + 1]
        if silence_label in (left_label, right_label):
            continue
        boundary = original[index]
        lower = max(boundary - radius_frames, refined[index - 1] + 1)
        upper = min(boundary + radius_frames, original[index + 1] - 1)
        candidates = np.arange(lower, upper + 1)
        # The right-chord sum is common to every split. Moving a frame to the
        # left chord adds the left-minus-right emission difference.
        differences = emissions[left_label, lower:upper] - emissions[right_label, lower:upper]
        values = np.r_[0.0, np.cumsum(differences)]
        tied = candidates[np.isclose(values, values.max(), rtol=0, atol=1e-12)]
        refined[index] = tied[np.argmin(np.abs(tied - boundary))]

    return np.repeat(identities, np.diff(refined)).astype(np.int64)
