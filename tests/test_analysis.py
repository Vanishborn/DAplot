"""Tests for virplot.analysis."""

import numpy as np

from virplot.analysis import call_blocks, smooth_depth


# call_blocks

def test_call_blocks_all_covered():
    y = np.array([10, 20, 30, 40, 50])
    intervals, gaps, pct = call_blocks(y, threshold=5)
    assert len(intervals) == 1
    assert intervals[0]["start_bp"] == 1
    assert intervals[0]["end_bp"] == 5
    assert intervals[0]["length_bp"] == 5
    assert len(gaps) == 0
    assert pct == 100.0


def test_call_blocks_none_covered():
    y = np.array([0, 0, 0, 0])
    intervals, gaps, pct = call_blocks(y, threshold=1)
    assert len(intervals) == 0
    assert len(gaps) == 1
    assert gaps[0]["length_bp"] == 4
    assert pct == 0.0


def test_call_blocks_mixed():
    y = np.array([0, 10, 10, 0, 5, 0])
    intervals, gaps, pct = call_blocks(y, threshold=5)
    assert len(intervals) == 2
    assert intervals[0] == {"start_bp": 2, "end_bp": 3, "length_bp": 2, "min_depth": 10, "mean_depth": 10.0}
    assert intervals[1] == {"start_bp": 5, "end_bp": 5, "length_bp": 1, "min_depth": 5, "mean_depth": 5.0}
    assert len(gaps) == 3


def test_call_blocks_empty():
    y = np.array([], dtype=int)
    intervals, gaps, pct = call_blocks(y, threshold=1)
    assert intervals == []
    assert gaps == []
    assert pct == 0.0


# smooth_depth

def test_smooth_depth_preserves_shape():
    y = np.random.randint(0, 100, size=500)
    smoothed = smooth_depth(y, window_size=10)
    assert smoothed.shape == y.shape


def test_smooth_depth_window_1_is_identity():
    y = np.array([1, 2, 3, 4, 5], dtype=float)
    smoothed = smooth_depth(y, window_size=1)
    np.testing.assert_allclose(smoothed, y)


def test_call_blocks_at_exact_threshold():
    """Values exactly equal to threshold count as covered."""
    y = np.array([5, 5, 5, 5])
    intervals, gaps, pct = call_blocks(y, threshold=5)
    assert len(intervals) == 1
    assert len(gaps) == 0
    assert pct == 100.0


def test_call_blocks_threshold_above_max():
    """Threshold higher than all values → no intervals, one gap."""
    y = np.array([3, 7, 2, 5])
    intervals, gaps, pct = call_blocks(y, threshold=100)
    assert len(intervals) == 0
    assert len(gaps) == 1
    assert gaps[0]["length_bp"] == 4
    assert pct == 0.0
