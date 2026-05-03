"""Coverage interval/gap analysis and CSV reporting."""

from __future__ import annotations

import csv
import logging
import os

import numpy as np

log = logging.getLogger(__name__)


def smooth_depth(y_vals: np.ndarray, window_size: int = 10) -> np.ndarray:
    """Smooth a depth array using a moving average kernel."""
    kernel = np.ones(window_size) / window_size
    return np.convolve(y_vals, kernel, mode="same")


def call_blocks(y: np.ndarray, threshold: int) -> tuple[list[dict], list[dict], float]:
    """Identify contiguous intervals >= threshold and gaps < threshold.

    Returns (intervals, gaps, pct_covered).
    """
    covered = y >= threshold

    edges = np.diff(np.r_[False, covered, False].astype(int))
    starts = np.where(edges == 1)[0]
    ends = np.where(edges == -1)[0]

    intervals = []
    for s, e in zip(starts, ends):
        seg = y[s:e]
        intervals.append({
            "start_bp": int(s + 1),
            "end_bp": int(e),
            "length_bp": int(e - s),
            "min_depth": int(seg.min()) if seg.size else 0,
            "mean_depth": float(seg.mean()) if seg.size else 0.0,
        })

    not_covered = ~covered
    edges2 = np.diff(np.r_[False, not_covered, False].astype(int))
    g_starts = np.where(edges2 == 1)[0]
    g_ends = np.where(edges2 == -1)[0]

    gaps = [
        {"start_bp": int(s + 1), "end_bp": int(e), "length_bp": int(e - s)}
        for s, e in zip(g_starts, g_ends)
    ]

    covered_bp = sum(iv["length_bp"] for iv in intervals)
    pct_covered = 100.0 * covered_bp / len(y) if len(y) else 0.0

    return intervals, gaps, pct_covered


def write_csvs(intervals: list[dict], gaps: list[dict],
               outdir: str, base: str, threshold: int) -> None:
    """Write interval and gap CSV reports for a given threshold."""
    iv_path = os.path.join(outdir, f"{base}.intervals_ge{threshold}.csv")
    gp_path = os.path.join(outdir, f"{base}.gaps_lt{threshold}.csv")

    with open(iv_path, "w", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=["start_bp", "end_bp", "length_bp", "min_depth", "mean_depth"])
        w.writeheader()
        w.writerows(intervals)

    with open(gp_path, "w", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=["start_bp", "end_bp", "length_bp"])
        w.writeheader()
        w.writerows(gaps)

    log.info("Reports written: %s, %s", os.path.basename(iv_path), os.path.basename(gp_path))
