"""Tests for study.py. Expected numbers are hand-computed (RULE.md, FORMULAS.md s.14 delta = 2*taker_buy - vol), never from the code.
Run: python MyTradingSys/research/multi_tf_bias_2026-10-18/test_study.py
"""
import math
import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study as S  # noqa: E402

MIN = 60000
D0 = 1640995200000  # 2022-01-01 00:00 UTC


def m1(rows, t0=D0):
    """rows: (o,h,l,c,v,tbv) per minute."""
    a = np.array(rows, float)
    t = t0 + MIN * np.arange(len(rows), dtype=float)
    return {"t": t, "o": a[:, 0], "h": a[:, 1], "l": a[:, 2], "c": a[:, 3], "v": a[:, 4], "tbv": a[:, 5]}


# 4 one-minute bars. typical=(h+l+c)/3:
#  b1 o10 h12 l9  c11 v2 tbv1 -> tp 32/3 ; pv 64/3 ; delta 2*1-2 =  0
#  b2 o11 h13 l10 c12 v3 tbv3 -> tp 35/3 ; pv 35   ; delta 2*3-3 =  3
#  b3 o12 h12 l8  c9  v1 tbv0 -> tp 29/3 ; pv 29/3 ; delta 0-1   = -1
#  b4 o9  h10 l9  c10 v4 tbv1 -> tp 29/3 ; pv 116/3; delta 2-4   = -2
FIX = m1([(10, 12, 9, 11, 2, 1), (11, 13, 10, 12, 3, 3), (12, 12, 8, 9, 1, 0), (9, 10, 9, 10, 4, 1)])


class TestBuild(unittest.TestCase):
    def test_two_minute_bars(self):
        b = S.build_tf(FIX, 2)
        self.assertEqual(list(b["o"]), [10, 12])
        self.assertEqual(list(b["c"]), [12, 10])
        self.assertEqual(list(b["h"]), [13, 12])
        self.assertEqual(list(b["l"]), [9, 8])
        self.assertEqual(list(b["v"]), [5, 5])
        self.assertEqual(list(b["delta"]), [3, -3])
        # vwap bar1 = (64/3 + 35)/5 = (169/3)/5 = 169/15 ; bar2 = (29/3+116/3)/5 = 145/15
        self.assertAlmostEqual(b["vwap"][0], 169 / 15, places=12)
        self.assertAlmostEqual(b["vwap"][1], 145 / 15, places=12)

    def test_vwap_same_for_every_tf_path(self):
        # the whole fixture: direct 4-minute bar equals the volume-weighted combination of the two 2-minute bars
        # and of the four 1-minute bars: (64/3+35+29/3+116/3)/10 = (64+105+29+116)/30 = 314/30
        want = 314 / 30
        b4 = S.build_tf(FIX, 4)
        self.assertAlmostEqual(b4["vwap"][0], want, places=12)
        b2 = S.build_tf(FIX, 2)
        self.assertAlmostEqual(float((b2["vwap"] * b2["v"]).sum() / b2["v"].sum()), want, places=12)
        b1 = S.build_tf(FIX, 1)
        self.assertAlmostEqual(float((b1["vwap"] * b1["v"]).sum() / b1["v"].sum()), want, places=12)

    def test_cut_refused(self):
        bad = m1([(1, 1, 1, 1, 1, 1)], t0=S.CUT_MS)
        with self.assertRaises(ValueError):
            S.build_tf(bad, 1)


def tfb(closes, hi=None, lo=None, delta=None):
    """Hand TF bars of length 1 minute-units: build directly from closes."""
    n = len(closes)
    return {"t": MIN * np.arange(n, dtype=float), "len": MIN, "c": np.array(closes, float),
            "h": np.array(hi if hi is not None else closes, float), "l": np.array(lo if lo is not None else closes, float),
            "delta": np.array(delta if delta is not None else [1.0] * n), "full": np.ones(n, bool)}


class TestState(unittest.TestCase):
    def test_trend_vs_balance_and_location(self):
        # closes 1,2,3,4 (n=4): ER = |4-1| / (1+1+1) = 1.0 -> IMB, dir +1, pos=(4-1)/(4-1)=1 -> HIGH
        s = S.tf_state(tfb([1, 2, 3, 4]), 4 * MIN, n=4)
        self.assertEqual((s["state"], s["dir"], s["loc"]), ("IMB", 1, "HIGH"))
        # closes 5,6,5,6.1... use 5,7,5,6: ER = 1/(2+2+1) = 0.2 -> BAL ; hi7 lo5 pos=(6-5)/2=.5 MID
        s = S.tf_state(tfb([5, 7, 5, 6]), 4 * MIN, n=4)
        self.assertEqual((s["state"], s["loc"]), ("BAL", "MID"))
        # low edge: 7,5,6,5.1 hi7 lo5 pos=.05 -> LOW ; ER=1.9/(2+1+.9)=.487 IMB dir -1
        s = S.tf_state(tfb([7, 5, 6, 5.1]), 4 * MIN, n=4)
        self.assertEqual((s["state"], s["dir"], s["loc"]), ("IMB", -1, "LOW"))

    def test_flow_from_last_closed_bar(self):
        s = S.tf_state(tfb([1, 2, 3, 4], delta=[5, 5, 5, -2]), 4 * MIN, n=4)
        self.assertEqual(s["flow"], -1)

    def test_no_lookahead(self):
        # the bar that closes after t must not change the state at t
        a = tfb([1, 2, 3, 4, 100], delta=[1, 1, 1, 1, -9])
        s_a = S.tf_state(a, 4 * MIN, n=4)
        b = tfb([1, 2, 3, 4, -50], delta=[1, 1, 1, 1, 9])
        s_b = S.tf_state(b, 4 * MIN, n=4)
        self.assertEqual(s_a, s_b)
        # a bar still open at t (close > t) is not used
        s_c = S.tf_state(a, 4 * MIN + 30000, n=4)
        self.assertEqual(s_c, s_a)

    def test_not_enough_or_incomplete(self):
        self.assertIsNone(S.tf_state(tfb([1, 2, 3]), 3 * MIN, n=4))
        b = tfb([1, 2, 3, 4])
        b["full"][1] = False
        self.assertIsNone(S.tf_state(b, 4 * MIN, n=4))


def st(state, d, loc, flow):
    return {"state": state, "dir": d, "loc": loc, "flow": flow}


class TestRule(unittest.TestCase):
    def all_tf(self, **kw):
        base = {"1d": st("IMB", 1, "MID", 1), "12h": st("IMB", 1, "MID", 1), "8h": st("BAL", 0, "MID", 1),
                "4h": st("IMB", 1, "MID", 1), "1h": st("BAL", 0, "MID", 1)}
        base.update(kw)
        return base

    def test_trend_aligned_long(self):  # row 1
        self.assertEqual(S.bias(self.all_tf()), 1)

    def test_tfs_disagree_no_bias(self):  # row 2
        self.assertEqual(S.bias(self.all_tf(**{"4h": st("IMB", -1, "MID", -1)})), 0)
        self.assertEqual(S.bias(self.all_tf(**{"12h": st("IMB", -1, "MID", 1)})), 0)

    def test_trend_flow_against_no_bias(self):
        self.assertEqual(S.bias(self.all_tf(**{"1h": st("BAL", 0, "MID", -1)})), 0)

    def test_missing_tf_no_bias(self):
        self.assertEqual(S.bias(self.all_tf(**{"8h": None})), 0)

    def test_balance_edge_failed_auction(self):  # rows 3-5
        d_hi = self.all_tf(**{"1d": st("BAL", 0, "HIGH", 0)})
        self.assertEqual(S.bias(dict(d_hi, **{"1h": st("BAL", 0, "MID", -1)})), -1)
        self.assertEqual(S.bias(dict(d_hi, **{"1h": st("BAL", 0, "MID", 1)})), 0)
        d_lo = self.all_tf(**{"1d": st("BAL", 0, "LOW", 0)})
        self.assertEqual(S.bias(dict(d_lo, **{"1h": st("BAL", 0, "MID", 1)})), 1)
        self.assertEqual(S.bias(dict(d_lo, **{"1h": st("BAL", 0, "MID", -1)})), 0)

    def test_balance_mid_uses_4h_edge(self):  # rows 6-8
        b = self.all_tf(**{"1d": st("BAL", 0, "MID", 0)})
        self.assertEqual(S.bias(dict(b, **{"4h": st("BAL", 0, "HIGH", 0), "1h": st("BAL", 0, "MID", -1)})), -1)
        self.assertEqual(S.bias(dict(b, **{"4h": st("BAL", 0, "LOW", 0), "1h": st("BAL", 0, "MID", 1)})), 1)
        self.assertEqual(S.bias(dict(b, **{"4h": st("BAL", 0, "MID", 0), "1h": st("BAL", 0, "MID", 1)})), 0)

    def test_zero_flow_no_bias(self):
        self.assertEqual(S.bias(self.all_tf(**{"1h": st("BAL", 0, "MID", 0)})), 0)


class TestStats(unittest.TestCase):
    def test_cluster_se_by_hand(self):
        # x = [1,3,5,7], days [a,a,b,b]; mean 4; devs -3,-1,1,3 ; day sums -4, +4 ; sqrt(16+16)/4 = sqrt(32)/4
        r = S.cluster_stats([1, 3, 5, 7], ["a", "a", "b", "b"])
        self.assertAlmostEqual(r["mean"], 4.0)
        self.assertAlmostEqual(r["se"], math.sqrt(32) / 4, places=12)
        self.assertEqual((r["n"], r["days"]), (4, 2))


class TestRunNet(unittest.TestCase):
    def test_summarise_net_of_cost(self):
        rec = [{"t": 0, "day": 0, "ret": 100.0, "stack": 1, "h1": 1, "d1": -1},
               {"t": 1, "day": 1, "ret": -40.0, "stack": -1, "h1": 1, "d1": 1}]
        r = S.summarise(rec, 12.0)
        # stack nets: +100-12=88 ; (-1)(-40)-12=28 -> mean 58
        self.assertAlmostEqual(r["STACK"]["mean"], 58.0)
        # 1h-only nets: 100-12=88, -40-12=-52 -> mean 18
        self.assertAlmostEqual(r["1h-only"]["mean"], 18.0)
        # 1h-only trades the stack removed (stack 0): none here
        self.assertEqual(r["1h-only-filtered-out"]["n"], 0)
        rec.append({"t": 2, "day": 2, "ret": 50.0, "stack": 0, "h1": -1, "d1": 0})
        r = S.summarise(rec, 12.0)
        # removed trade: -1*50-12 = -62
        self.assertAlmostEqual(r["1h-only-filtered-out"]["mean"], -62.0)
        self.assertEqual(r["1D-only-filtered-out"]["n"], 0)

    def test_run_has_no_lookahead_in_bias(self):
        # synthetic 30 days of 1m bars; the bias at a decision time must not change when later bars are rewritten
        n = 30 * 1440
        rng = np.random.default_rng(0)
        c = 100 + np.cumsum(rng.normal(0, 0.1, n))
        rows = [(c[i - 1] if i else c[0], c[i] + 0.2, c[i] - 0.2, c[i], 10.0, float(rng.integers(0, 11))) for i in range(n)]
        m_a = m1(rows)
        tf_a = {k: S.build_tf(m_a, v) for k, v in S.TFS.items()}
        t = D0 + 20 * 86400000
        cut = int((t - D0) // MIN)
        rows_b = rows[:cut] + [(9999, 10000, 1, 5000, 99.0, 0.0)] * (n - cut)
        tf_b = {k: S.build_tf(m1(rows_b), v) for k, v in S.TFS.items()}
        f = lambda tf: S.bias({k: S.tf_state(tf[k], t) for k in ("1d", "12h", "8h", "4h", "1h")})
        self.assertEqual(f(tf_a), f(tf_b))


if __name__ == "__main__":
    unittest.main()
