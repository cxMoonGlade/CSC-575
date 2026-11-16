"""Duration-weighted chord scores and one-to-one chord-boundary matching."""

from __future__ import annotations

import numpy as np

from .data import reduce_label

_EPS = 1e-9


def prediction_intervals(times, indices, duration: float, labels) -> list[tuple[float, float, str]]:
    """Assign centred frame labels to midpoint cells and merge identical labels.

    The first cell starts at zero, the last ends at the actual audio duration.
    This avoids treating frame centres as the starts of prediction intervals.
    """
    times = np.asarray(times, dtype=float)
    indices = np.asarray(indices)
    if duration <= 0 or not np.isfinite(duration):
        raise ValueError("duration must be positive and finite")
    if times.ndim != 1 or indices.ndim != 1 or len(times) != len(indices) or not len(times):
        raise ValueError("times and indices must be non-empty, equal-length vectors")
    if not np.isfinite(times).all() or np.any(np.diff(times) <= 0) or times[0] < 0 or times[-1] > duration + _EPS:
        raise ValueError("Frame times must be strictly increasing within the recording")
    if not np.issubdtype(indices.dtype, np.integer) or np.any(indices < 0) or np.any(indices >= len(labels)):
        raise ValueError("Prediction indices must be valid integer label indices")
    edges = np.r_[0.0, (times[:-1] + times[1:]) / 2.0, float(duration)]
    intervals = []
    for start, end, index in zip(edges[:-1], edges[1:], indices):
        label = str(labels[int(index)])
        if end <= start:
            continue
        if intervals and intervals[-1][2] == label:
            intervals[-1] = (intervals[-1][0], float(end), label)
        else:
            intervals.append((float(start), float(end), label))
    return intervals


def _normalize(intervals, duration: float):
    result = []
    previous_end = 0.0
    for raw_start, raw_end, label in sorted(intervals, key=lambda item: item[0]):
        start, end = float(raw_start), float(raw_end)
        if not np.isfinite([start, end]).all() or end <= start:
            raise ValueError("Intervals must have positive, finite durations")
        start, end = max(0.0, start), min(duration, end)
        if end <= start:
            continue
        if start < previous_end - _EPS:
            raise ValueError("Intervals must not overlap")
        if abs(start - previous_end) <= _EPS:
            start = previous_end
        reduced = reduce_label(label)
        if result and result[-1][2] == reduced and abs(start - result[-1][1]) <= _EPS:
            result[-1] = (result[-1][0], end, reduced)
        else:
            result.append((start, end, reduced))
        previous_end = end
    return result


def _boundaries(intervals):
    return [
        left[1]
        for left, right in zip(intervals[:-1], intervals[1:])
        if left[2] is not None and right[2] is not None
        and left[2] != right[2] and abs(left[1] - right[0]) <= _EPS
    ]


def _scoreable_spans(reference):
    spans = []
    for start, end, label in reference:
        if label is None:
            continue
        if spans and abs(spans[-1][1] - start) <= _EPS:
            spans[-1] = (spans[-1][0], end)
        else:
            spans.append((start, end))
    return spans


def _match_boundaries(reference, prediction, tolerance):
    """Maximum-cardinality, then minimum-total-error ordered matching.

    Sorted one-dimensional event times admit an order-preserving optimum for
    this absolute-error objective, so dynamic programming avoids double hits.
    """
    n, m = len(reference), len(prediction)
    counts = np.zeros((n + 1, m + 1), dtype=np.int32)
    costs = np.zeros((n + 1, m + 1), dtype=float)
    decisions = np.zeros((n + 1, m + 1), dtype=np.uint8)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            options = [(counts[i - 1, j], costs[i - 1, j], 1), (counts[i, j - 1], costs[i, j - 1], 2)]
            error = abs(reference[i - 1] - prediction[j - 1])
            if error <= tolerance + 1e-12:
                options.append((counts[i - 1, j - 1] + 1, costs[i - 1, j - 1] + error, 3))
            count, cost, decision = min(options, key=lambda value: (-value[0], value[1]))
            counts[i, j], costs[i, j], decisions[i, j] = count, cost, decision
    pairs = []
    i, j = n, m
    while i and j:
        decision = decisions[i, j]
        if decision == 3:
            pairs.append((float(reference[i - 1]), float(prediction[j - 1])))
            i, j = i - 1, j - 1
        elif decision == 1:
            i -= 1
        else:
            j -= 1
    return list(reversed(pairs))


def evaluate(reference, prediction, duration: float, tolerance: float = 0.1) -> dict:
    """Score predictions only where the reference has a supported label.

    No-chord is scoreable. Unsupported labels and annotation gaps reduce
    coverage. Boundaries at gap edges are excluded, and matching occurs inside
    each contiguous scoreable span so a match cannot cross an excluded gap.
    Missing/unsupported predictions count as incorrect on scoreable reference
    time. Empty boundary denominators yield zero precision/recall, not a
    fabricated perfect score; no scoreable duration gives accuracy=None.
    """
    if not np.isfinite(duration) or duration <= 0:
        raise ValueError("duration must be positive and finite")
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be nonnegative and finite")
    reference = _normalize(reference, duration)
    prediction = _normalize(prediction, duration)
    scoreable = sum(end - start for start, end, label in reference if label is not None)
    correct = 0.0
    i = j = 0
    while i < len(reference) and j < len(prediction):
        a, b = reference[i], prediction[j]
        overlap = min(a[1], b[1]) - max(a[0], b[0])
        if overlap > 0 and a[2] is not None and a[2] == b[2]:
            correct += overlap
        if a[1] <= b[1]:
            i += 1
        else:
            j += 1

    reference_boundaries = _boundaries(reference)
    prediction_boundaries = _boundaries(prediction)
    kept_reference = []
    kept_prediction = []
    pairs = []
    for start, end in _scoreable_spans(reference):
        ref = [t for t in reference_boundaries if start + _EPS < t < end - _EPS]
        pred = [t for t in prediction_boundaries if start + _EPS < t < end - _EPS]
        kept_reference.extend(ref)
        kept_prediction.extend(pred)
        pairs.extend(_match_boundaries(ref, pred, tolerance))
    hits, nr, npred = len(pairs), len(kept_reference), len(kept_prediction)
    precision = hits / npred if npred else 0.0
    recall = hits / nr if nr else 0.0
    errors = [pred - ref for ref, pred in pairs]
    return {
        "duration_accuracy": float(correct / scoreable) if scoreable > 0 else None,
        "correct_seconds": float(correct),
        "scoreable_seconds": float(scoreable),
        "excluded_seconds": float(max(0.0, duration - scoreable)),
        "coverage": float(scoreable / duration),
        "boundary_precision": float(precision),
        "boundary_recall": float(recall),
        "boundary_f1": float(2 * precision * recall / (precision + recall)) if precision + recall else 0.0,
        "boundary_matches": hits,
        "reference_boundaries": nr,
        "predicted_boundaries": npred,
        "boundary_mae_seconds": float(np.mean(np.abs(errors))) if errors else None,
        "boundary_mean_signed_error_seconds": float(np.mean(errors)) if errors else None,
        "boundary_timing_errors_seconds": errors,
        "matched_boundary_pairs": pairs,
    }
