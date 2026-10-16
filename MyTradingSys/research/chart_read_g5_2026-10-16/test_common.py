"""Tests for common.py. Expected numbers are hand-computed from FORMULAS.md (RSI s.1, ATR s.12, s.13 costs) or by hand below."""
import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as K  # noqa: E402


class TestIndicators(unittest.TestCase):
    def test_rsi_worked_example(self):
        # FORMULAS.md s.1 worked example, period=3, closes [10,12,11,14] -> rsi[3] = 100 - 100/6
        r = K.rsi_wilder([10, 12, 11, 14], 3)
        self.assertTrue(np.isnan(r[:3]).all())
        self.assertAlmostEqual(r[3], 83.3333333, places=5)

    def test_rsi_restarts_after_nan(self):
        r = K.rsi_wilder([10, 12, 11, 14, np.nan, 10, 12, 11, 14], 3)
        self.assertTrue(np.isnan(r[4:8]).all())
        self.assertAlmostEqual(r[8], 83.3333333, places=5)

    def test_atr_sma_worked_example(self):
        # FORMULAS.md s.12: TR[1..3] = 2, 2, 2.5 -> ATR(3) at index 3 = 2.1666667 (plain SMA, not Wilder)
        a = K.atr_sma([10, 11, 12, 11], [9, 9, 10, 9], [9.5, 10.5, 11.5, 10], 3)
        self.assertTrue(np.isnan(a[:3]).all())
        self.assertAlmostEqual(a[3], 2.1666667, places=5)

    def test_bb_population_sd(self):
        # closes 1,2,3,4, n=4: mid 2.5, population SD sqrt(1.25) = 1.118034; upper 2.5 + 2*1.118034
        lo, mid, up = K.bb([1, 2, 3, 4], 4, 2.0)
        self.assertAlmostEqual(mid[3], 2.5)
        self.assertAlmostEqual(up[3], 2.5 + 2 * math.sqrt(1.25), places=6)
        self.assertAlmostEqual(lo[3], 2.5 - 2 * math.sqrt(1.25), places=6)
        self.assertTrue(np.isnan(mid[:3]).all())


class TestAgg(unittest.TestCase):
    def test_agg_and_incomplete_bar(self):
        A = {k: np.array([1.0, 2, 3, 4, 5, 6]) for k in ("O", "H", "L", "C", "V", "TBV", "QV")}
        A["H"] = np.array([5.0, 9, 3, 4, 5, 6])
        A["L"] = np.array([1.0, 2, 0.5, 4, 5, 6])
        A["C"] = np.array([1.5, 2, 3, 4, 5, 6.5])
        a = K.agg(A, 3)
        self.assertEqual(list(a["O"]), [1.0, 4.0])
        self.assertEqual(list(a["H"]), [9.0, 6.0])
        self.assertEqual(list(a["L"]), [0.5, 4.0])
        self.assertEqual(list(a["C"]), [3.0, 6.5])
        self.assertEqual(list(a["V"]), [6.0, 15.0])
        A["H"][4] = np.nan                                        # second 3m bar incomplete -> all NaN
        b = K.agg(A, 3)
        self.assertTrue(np.isnan(b["O"][1]) and np.isnan(b["C"][1]) and not np.isnan(b["O"][0]))


class TestStats(unittest.TestCase):
    def test_wilson(self):
        lo, hi = K.wilson(5, 10)
        self.assertAlmostEqual(lo, 0.2366, places=3)
        self.assertAlmostEqual(hi, 0.7634, places=3)
        self.assertTrue(np.isnan(K.wilson(0, 0)[0]))

    def test_cluster_se(self):
        m, se = K.cm_se(np.array([1.0, 2.0, 6.0]), np.array([0, 0, 1]))
        self.assertAlmostEqual(m, 3.0)
        self.assertAlmostEqual(se, math.sqrt(18) / 3, places=9)         # day sums of deviations: -3 and +3

    def test_diff_cluster_matches_two_means(self):
        g = np.array([1.0, 3.0, 5.0, 9.0])
        f = np.array([0.0, 0.0, 1.0, 1.0])
        d, se = K.diff_se(g, f, np.array([0, 1, 2, 3]))
        self.assertAlmostEqual(d, 7.0 - 2.0)

    def test_max_dd(self):
        self.assertAlmostEqual(K.max_dd(np.array([1.0, -3.0, 1.0, -1.0, 4.0])), 3.0)


class TestTrade(unittest.TestCase):
    def test_gross_delay_and_side(self):
        O = np.array([100.0, 100, 100, 110, 110, 110, 90, 90])
        # decision at the close of bar 1, d=1 -> p_in = O[1+1+1] = 110, h=3 -> p_out = O[6] = 90
        g = K.trade_gross(O, np.array([1]), np.array([-1]), 3, d=1)
        self.assertAlmostEqual(g[0], -1 * (90 / 110 - 1) * 100)
        self.assertTrue(np.isnan(K.trade_gross(O, np.array([5]), np.array([1]), 3, d=1)[0]))   # exit beyond the data

    def test_funding_crossings(self):
        ms = 60_000
        base = K.TS0                                              # 2022-01-01 00:00 UTC
        f = K.funding_pct(np.array([479, 479, 0]), np.array([481, 960, 479]))   # 07:59 -> 08:01 | 07:59 -> 16:00 | 00:00 -> 07:59
        self.assertEqual(list(np.round(f, 6)), [0.01, 0.02, 0.0])

    def test_cooldown(self):
        t = np.array([0, 10, 61, 62, 200])
        s = np.array([1, 1, 1, -1, 1])
        keep = K.cooldown_mask(t, s, 60)
        self.assertEqual(list(keep), [True, False, True, True, True])    # 61 is 61 > 60 after 0 (kept); 10 dropped; 62 other side


class TestVerdict(unittest.TestCase):
    def test_inconclusive_small_n(self):
        rng = np.random.default_rng(1)
        g = rng.normal(1.0, 0.1, 50)
        r = K.verdict_arm(g, np.arange(50), g * 0, np.arange(50), np.arange(50), 5.0)
        self.assertEqual(r["verdict"], "INCONCLUSIVE")

    def test_pass_and_fail(self):
        rng = np.random.default_rng(2)
        n = 400
        day = np.arange(n)
        t = np.arange(n) * 100
        good = rng.normal(0.5, 0.05, n)                          # mean 0.5 % gross, cost 0.14 -> net 0.36
        ctrl = rng.normal(0.0, 0.05, n)
        self.assertEqual(K.verdict_arm(good, day, ctrl, day, t, 1000.0)["verdict"], "PASS")
        bad = rng.normal(0.1, 0.05, n)                           # gross below cost
        self.assertEqual(K.verdict_arm(bad, day, ctrl, day, t, 1000.0)["verdict"], "FAIL")
        # cost passes but no incremental over control -> FAIL
        self.assertEqual(K.verdict_arm(good, day, good + rng.normal(0, 0.01, n), day, t, 1000.0)["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
