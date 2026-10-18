"""Fail-first tests for the OPR-BB-MTF-CENTER screen + Krown M tests (synthetic bars, hand-computed). Run: python test_study.py"""
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "chart_read_g5_2026-10-16"))
import study as B  # noqa: E402


def lower_trend_bars():
    """16 bars, mid falls by 1 per bar from 30; closes 0.5 below the mid; highs 0.2 below the mid (no touch) except where a test sets them."""
    mid = np.arange(30.0, 14.0, -1.0)
    return mid - 0.5, mid - 0.2, mid - 1.0, mid, np.full(16, 2.0)       # C, H, L, mid, half-width


def idx(ev):
    return list(np.nonzero(ev["event"])[0])


class TestTouch(unittest.TestCase):
    def test_wick_event_after_n_closes_below_not_under_close_rule(self):
        C, H, L, mid, hw = lower_trend_bars()
        H[9] = mid[9] + 0.1                       # bar 9 wick reaches its own mid but still closes below it
        self.assertEqual(idx(B.touch_events(C, H, L, mid, hw, N=6, rule="wick")), [9])    # run of 9 closes below >= 6, first touch
        self.assertEqual(idx(B.touch_events(C, H, L, mid, hw, N=6, rule="close")), [])    # no close above the mid -> no event

    def test_first_touch_after_the_precondition_is_met(self):
        C, H, L, mid, hw = lower_trend_bars()
        H[8] = mid[8] + 0.1
        H[12] = mid[12] + 0.1
        self.assertEqual(idx(B.touch_events(C, H, L, mid, hw, N=6, rule="wick")), [8])     # 12 is a later touch in the same run
        self.assertEqual(idx(B.touch_events(C, H, L, mid, hw, N=3, rule="wick")), [8])
        # N=12: the bar-8 touch is at position 9 <= 12 (before the precondition is met), bar 12 is the first touch after it
        self.assertEqual(idx(B.touch_events(C, H, L, mid, hw, N=12, rule="wick")), [12])

    def test_slope_condition_and_near_rule(self):
        C, H, L, mid, hw = lower_trend_bars()
        mid_up = mid[::-1].copy()                 # rising mid: the lower-band-trend slope test fails
        H2 = mid_up - 0.2
        H2[9] = mid_up[9] + 0.1
        self.assertEqual(idx(B.touch_events(mid_up - 0.5, H2, mid_up - 1, mid_up, hw, N=6, rule="wick")), [])
        H = mid - 1.0                             # far from the mid (0.5 half-widths)
        H[9] = mid[9] - 0.3                       # 0.15 half-widths below the mid
        self.assertEqual(idx(B.touch_events(C, H, L, mid, hw, N=6, rule="near", x=0.25)), [9])
        self.assertEqual(idx(B.touch_events(C, H, L, mid, hw, N=6, rule="near", x=0.10)), [])
        self.assertEqual(idx(B.touch_events(C, H, L, mid, hw, N=6, rule="wick")), [])

    def test_mirror_up_trend_touches_from_above(self):
        mid = np.arange(14.0, 30.0)
        C, H, L = mid + 0.5, mid + 1.0, mid + 0.2
        L[9] = mid[9] - 0.1
        self.assertEqual(idx(B.touch_events(C, H, L, mid, np.full(16, 2.0), N=6, rule="wick", side=1)), [9])


class TestUDR(unittest.TestCase):
    def test_classification(self):
        Hw = np.array([[1.0, 2, 3, 12], [1, 2, 3, 12], [11, 1, 1, 1], [1, 2, 3, 4], [1, np.nan, 3, 4]])
        Lw = np.array([[0.5, 0.4, 0.3, 0.2], [0.5, 0.4, 0.3, 0.2], [-1, 1, 1, 1], [0.5, 0.4, 0.3, 0.2], [0.5, 0.4, 0.3, 0.2]])
        up = np.array([10.0, 10, 10, 10, 10])
        lo = np.array([0.0, 0.35, 0.0, 0.0, 0.0])
        # row 1: low 0.3 <= 0.35 at index 2, before the up hit at index 3 -> D; row 2: both in minute 0 -> B; row 4: NaN -> X
        self.assertEqual(list(B.classify_udr(Hw, Lw, up, lo)), ["U", "D", "B", "R", "X"])


class TestRanges(unittest.TestCase):
    def test_range_detector_needs_two_reactions_each_side(self):
        H = np.array([10.0, 9, 10, 9, 10, 9, 9, 9])
        L = np.array([5.0, 6, 6, 5, 6, 6, 5, 6])
        r = B.detect_ranges(H, L, 8, 0.01)
        self.assertEqual(len(r), 1)
        self.assertEqual((r[0][0], r[0][1], r[0][2], r[0][3]), (0, 7, 10.0, 5.0))
        H2 = H.copy()
        H2[2] = H2[4] = 9.0                      # the high zone is now a single reaction (bar 0)
        self.assertEqual(len(B.detect_ranges(H2, L, 8, 0.01)), 0)

    def test_clusters(self):
        self.assertEqual(B.clusters(np.array([True, True, False, True, False, False, True])), 3)


if __name__ == "__main__":
    unittest.main()
