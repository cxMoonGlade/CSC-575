import numpy as np
import pytest

from chordrec.nc_diagnostic import frame_weights, weighted_quantiles


def test_partial_frame_duration_and_weighted_quantiles():
    weights = frame_weights(np.array([0, .2, .7, 1]), .1, .8)
    np.testing.assert_allclose(weights, [.1, .5, .1])
    assert weighted_quantiles([-40, -10, -30], weights, [.1, .5, .9]) == [-40, -10, -10]
    assert weighted_quantiles([2, 9], [1, 0], [0, 1]) == [2, 2]


def test_empty_and_invalid_weights():
    assert weighted_quantiles([1], [0], [.5]) == [None]
    with pytest.raises(ValueError):
        weighted_quantiles([1], [-1], [.5])
    with pytest.raises(ValueError):
        weighted_quantiles([1], [1], [float("nan")])
