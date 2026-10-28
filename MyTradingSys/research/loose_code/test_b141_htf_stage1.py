"""Tests for b141_htf_stage1.py. Expected values are hand arithmetic from the pre-registration section 4 rule
(R <= k*sqrt(N)*ATR_N, |c-poc| <= b*R, ER = |c_i - c_(i-N)| / sum|dc| <= e), not taken from the code under test.
Flat window (every bar o=c=1025, h=1029, l=1021): TR=8, ATR=8, R=8, 0.8*sqrt(240)*8=99.2 >= 8; hlc3=1025 -> bin 1000, poc 1025,
|c-poc|=0 -> balanced for every k and b. ER: path 0 -> None (not balanced for family B).
Trend window (c = 1000 + j, h = c+1, l = c-1): TR=2, ATR=2, R=N+1; 2.0*sqrt(240)*2=62 < 241 -> not balanced for any k; ER = 1."""
import math
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
import b141_htf_stage1 as s1

MIN = 60000
N = 240


def bars(c, half=1.0, vol=1.0):
    n = len(c)
    c = np.array(c, dtype=float)
    return {"t": np.arange(n, dtype=np.int64) * MIN, "h": c + half, "l": c - half, "c": c, "v": np.full(n, vol)}


class Stage1Test(unittest.TestCase):
    def test_flat_window_balanced_all_family_a(self):
        K = bars([1025.0] * (N + 1), half=4.0)
        st = s1.window_stats(K, N, N)
        self.assertAlmostEqual(st["atr"], 8.0)
        self.assertAlmostEqual(st["R"], 8.0)
        self.assertEqual(st["poc"], 1025.0)
        for k in s1.K_GRID:
            for b in s1.B_GRID:
                self.assertTrue(s1.is_balanced("A", {"k": k, "b": b}, st, N))

    def test_flat_window_family_b_undefined(self):
        st = s1.window_stats(bars([1025.0] * (N + 1), half=4.0), N, N)
        self.assertIsNone(st["er"])
        self.assertFalse(s1.is_balanced("B", {"e": 0.25}, st, N))

    def test_trend_not_balanced(self):
        K = bars([1000.0 + j for j in range(N + 1)])
        st = s1.window_stats(K, N, N)
        self.assertAlmostEqual(st["atr"], 2.0)
        self.assertAlmostEqual(st["R"], N + 1.0)
        self.assertAlmostEqual(st["er"], 1.0)
        for k in s1.K_GRID:
            self.assertFalse(s1.is_balanced("A", {"k": k, "b": 0.5}, st, N))
        for e in s1.E_GRID:
            self.assertFalse(s1.is_balanced("B", {"e": e}, st, N))

    def test_gap_invalid(self):
        K = bars([1025.0] * (N + 1))
        K["t"][100:] += MIN                                   # one missing minute inside the window
        self.assertIsNone(s1.window_stats(K, N, N))

    def test_incumbent_matches_signals_balance(self):
        from MyTradingSys.backtest.layers.fabio.v3.signals import balance
        rng = np.random.default_rng(7)
        c = 84000 + np.cumsum(rng.normal(0, 3, N + 1))
        K = bars(c, half=5.0, vol=2.0)
        sb = [{"t": int(K["t"][j]), "o": c[j], "h": K["h"][j], "l": K["l"][j], "c": c[j], "buy_vol": 1.0, "sell_vol": 1.0,
               "delta": 0.0, "fp": "%g:1.0:1.0" % (math.floor(((K["h"][j] + K["l"][j] + c[j]) / 3.0) / 10.0 + 1e-9) * 10.0)}
              for j in range(N + 1)]
        for k in (0.8, 2.0, 4.0):
            ref = balance(sb, N, N, k_bal=k) is not None
            st = s1.window_stats(K, N, N)
            self.assertEqual(s1.is_balanced("A", {"k": k, "b": 0.25}, st, N), ref)

    def test_28_cells(self):
        self.assertEqual(len(s1.cells()), 28)

    def test_holdout_not_loaded(self):
        self.assertEqual(s1.DEV_END, "2026-06-25")


if __name__ == "__main__":
    unittest.main()
