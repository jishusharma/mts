"""Fail-first tests for the MAL-BB-MID-ENGULF screen (synthetic 5m bars, hand-computed). Run: python test_study.py"""
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "chart_read_g5_2026-10-16"))
import study as M  # noqa: E402


class TestEngulf(unittest.TestCase):
    def setUp(self):
        #            0 green      1 red full engulf   2 green        3 red, opens inside the body   4 green     5 red, close above prev open
        self.O = np.array([100.0, 101.0, 99.6, 100.2, 99.0, 99.9])
        self.C = np.array([101.0, 99.5, 100.5, 99.0, 99.8, 99.2])

    def test_variant_a_vs_b(self):
        a, b = M.engulf_a(self.O, self.C), M.engulf_b(self.O, self.C)
        self.assertEqual(list(a), [False, True, False, True, False, False])
        # bar 3 closes below the previous green bar's open (99.6) -> engulf under (a); its open 100.2 < previous close 100.5 -> NOT under (b)
        self.assertEqual(list(b), [False, True, False, False, False, False])

    def test_body_ratio_variant(self):
        # bar 1: body 1.5 / previous body 1.0 = 1.5 ; bar 3: body 1.2 / previous 0.9 = 1.3333
        self.assertEqual(list(M.engulf_c(self.O, self.C, 1.5)), [False, True, False, False, False, False])
        self.assertEqual(list(M.engulf_c(self.O, self.C, 1.0)), [False, True, False, True, False, False])
        self.assertEqual(list(M.engulf_c(self.O, self.C, 2.0)), [False] * 6)


class TestState(unittest.TestCase):
    def test_bounce_window_and_grid(self):
        H = np.array([10.0, 10, 10, 12, 10, 10, 10, 10])
        mid, width = np.full(8, 11.0), np.full(8, 4.0)
        b0 = M.bounce(H, mid, width, 0.0)
        self.assertEqual(list(b0), [False, False, False, True, True, True, False, False])   # bar 3 touches; stays in the last-3 window to bar 5
        b25 = M.bounce(H, mid, width, 0.25)                                                   # 11 - 0.25 x 4 = 10 -> every bar touches
        self.assertTrue(b25.all())

    def test_falling(self):
        mid = np.linspace(20, 9, 12)                       # strictly falling
        dl = np.full(12, -1.0)
        f = M.falling(mid, dl)
        self.assertTrue(f[11] and f[10] and not f[9])      # needs 10 bars of mid history and 6 bars of delta
        dl[11] = 100.0                                     # net delta of the last 6 bars turns positive
        self.assertFalse(M.falling(mid, dl)[11])

    def test_htf_index_uses_closed_bars_only(self):
        t = np.array([10, 11, 12, 59])
        self.assertEqual(list(M.htf_idx(t, 60)), [-1, 0, 0, 4])      # 5m bar 11 closes at minute 60 -> first closed 1h bar 0
        self.assertEqual(list(M.htf_idx(t, 240)), [-1, -1, -1, 0])   # 5m bar 59 closes at minute 300 -> 4h bar 0 closed at 240


class TestSecondBreak(unittest.TestCase):
    def test_next_bar_trades_below_engulf_low(self):
        L = np.array([5.0, 4.0, 3.9, 4.1, 3.0])
        self.assertEqual(list(M.second_break(L)), [True, True, False, True, False])   # L[i+1] < L[i]; last bar has no next


if __name__ == "__main__":
    unittest.main()
