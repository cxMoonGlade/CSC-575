import numpy as np
import pytest

from chordrec.error_analysis import MISSING, UNSUPPORTED, decompose, error_category


def test_categories_cover_scoreable_time_and_prediction_gaps():
    ref = [(0, 2, "N"), (2, 8, "C:maj"), (8, 9, "X")]
    pred = [(0, 1, "C:maj"), (2, 3, "N"), (3, 4, "C:min"),
            (4, 5, "G:maj"), (5, 6, "X"), (7, 8, "C:7"), (8, 9, "G:maj")]
    result = decompose(ref, pred, 10)
    categories = result["regions"]["all"]["categories_seconds"]
    assert categories == {"correct": 1, "reference_n_error": 2, "chord_to_n": 1,
                          "same_root_wrong_quality": 1, "other_root": 1, "invalid_prediction": 2}
    assert result["confusion"]["all"][("N", MISSING)] == 1
    assert result["confusion"]["all"][("C:maj", UNSUPPORTED)] == 1
    assert result["confusion"]["all"][("C:maj", MISSING)] == 1
    assert result["excluded_seconds"] == 2
    assert result["coverage"] == .8
    assert result["regions"]["all"]["duration_accuracy"] == 1/8


def test_near_regions_merge_and_do_not_cross_excluded_gaps():
    ref = [(0, .4, "C:maj"), (.4, .5, "G:maj"), (.5, .55, "X"), (.55, 1, "F:maj")]
    result = decompose(ref, [(0, 1, "C:maj")], 1)
    near, stable = result["regions"]["near"], result["regions"]["stable"]
    assert near["scoreable_seconds"] == pytest.approx(.3)
    assert near["categories_seconds"]["other_root"] == pytest.approx(.1)
    assert stable["scoreable_seconds"] == pytest.approx(.65)
    assert stable["categories_seconds"]["other_root"] == pytest.approx(.45)
    ref = [(0, 1, "C:maj"), (1, 1.2, "G:maj"), (1.2, 3, "C:maj")]
    result = decompose(ref, [(0, 3, "C:maj")], 3)
    assert result["regions"]["near"]["scoreable_seconds"] == pytest.approx(.6)
    assert result["regions"]["near"]["error_seconds"] == pytest.approx(.2)


def test_enharmonic_reduction_empty_coverage_and_n_correctness():
    result = decompose([(0, 1, "Db:maj"), (1, 2, "N")], [(0, 1, "C#:7"), (1, 2, "N")], 2)
    assert result["regions"]["all"]["correct_seconds"] == 2
    empty = decompose([(0, 1, "X")], [], 2)
    assert empty["regions"]["all"]["duration_accuracy"] is None
    assert empty["excluded_seconds"] == 2
    assert error_category("N", UNSUPPORTED) == "reference_n_error"


@pytest.mark.parametrize("halfwidth", [0, -1, np.nan, np.inf])
def test_reject_invalid_boundary_width(halfwidth):
    with pytest.raises(ValueError):
        decompose([(0, 1, "C:maj")], [(0, 1, "C:maj")], 1, halfwidth)
