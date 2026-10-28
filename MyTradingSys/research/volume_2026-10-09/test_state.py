"""Tests for the V2 state variables. Expected values are hand-derived from PRE_REG_ADDENDUM_A_2026-10-09.md A2.
Run: python MyTradingSys/research/volume_2026-10-09/test_state.py"""
import sys
sys.dont_write_bytecode = True
import math
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vstate as T  # noqa: E402

DAY, HOUR = 86400000, 3600000


def daily(n, v=10.0, tbv=7.0, c=None):
    c = np.linspace(100, 200, n) if c is None else c
    return {"t": np.arange(n, dtype=np.int64) * DAY, "o": c.copy(), "h": c + 1, "l": c - 1, "c": c, "v": np.full(n, v), "tbv": np.full(n, tbv)}


def hourly(n_days, us_frac=0.8, as_frac=0.2):
    t = np.arange(n_days * 24, dtype=np.int64) * HOUR
    hr = (t % DAY) // HOUR
    frac = np.where(hr >= 16, us_frac, np.where(hr < 8, as_frac, 0.5))
    v = np.full(len(t), 100.0)
    return {"t": t, "v": v, "tbv": v * frac, "o": v, "h": v, "l": v, "c": v}


class TestStates(unittest.TestCase):
    def test_d20_hand(self):
        d = daily(60)
        s = T.states(d, hourly(60))
        self.assertAlmostEqual(s["D20"][30], 0.4)                  # (2*7-10)/10
        self.assertTrue(np.isnan(s["D20"][18]))
        self.assertAlmostEqual(s["D20"][19], 0.4)

    def test_vt_hand(self):
        d = daily(150)
        d["v"][130:] = 20.0                                         # last 20 days double, previous 80 of the 100-day window stay 10
        s = T.states(d, hourly(150))
        self.assertAlmostEqual(s["VT"][149], math.log(20.0 / 12.0))
        self.assertTrue(np.isnan(s["VT"][98]))

    def test_mom_hand(self):
        c = np.linspace(100, 200, 60)
        s = T.states(daily(60, c=c), hourly(60))
        self.assertAlmostEqual(s["MOM"][30], math.log(c[30] / c[10]))

    def test_rank_hand_and_extremes(self):
        x = np.array([3, 1, 2, 5, 4, 2.5])
        r = T.exante_rank(x, win=5)
        self.assertAlmostEqual(r[5], 0.4)                          # previous [3,1,2,5,4]; <= 2.5 are {1,2}
        self.assertTrue(np.isnan(r[4]))
        self.assertAlmostEqual(T.exante_rank(np.full(8, 2.0), win=5)[7], 1.0)   # ties count as <=
        up = T.exante_rank(np.arange(1.0, 301.0))
        self.assertAlmostEqual(up[250], 1.0)
        down = T.exante_rank(np.arange(300.0, 0.0, -1.0))
        self.assertAlmostEqual(down[250], 0.0)

    def test_time_split_us_vs_asia(self):
        d = daily(60)
        s = T.states(d, hourly(60))
        self.assertAlmostEqual(s["DUS"][30], 0.6)                  # 8 h * (2*80-100) / (8*100)
        self.assertAlmostEqual(s["DAS"][30], -0.6)

    def test_incomplete_day_is_nan(self):
        h = hourly(60)
        keep = np.ones(len(h["t"]), dtype=bool)
        keep[30 * 24 + 5] = False                                   # drop one hour of day 30
        h = {k: v[keep] for k, v in h.items()}
        sp = T.day_split(h, daily(60)["t"])
        self.assertTrue(np.isnan(sp["v_us"][30]))
        self.assertFalse(np.isnan(sp["v_us"][29]))

    def test_no_lookahead(self):
        rng = np.random.default_rng(4)
        n = 500
        c = 100 + np.cumsum(rng.normal(0, 1, n))
        d = daily(n, c=c)
        d["v"] = rng.lognormal(0, 0.4, n) * 100
        d["tbv"] = d["v"] * rng.uniform(0.4, 0.6, n)
        h = hourly(n)
        h["v"] = rng.lognormal(0, 0.4, len(h["t"])) * 100
        h["tbv"] = h["v"] * rng.uniform(0.4, 0.6, len(h["t"]))
        s1 = T.states(d, h)
        d2 = {k: x.copy() for k, x in d.items()}
        h2 = {k: x.copy() for k, x in h.items()}
        d2["v"][400:] *= 5; d2["tbv"][400:] *= 3; d2["c"][400:] *= 1.5
        h2["v"][400 * 24:] *= 5; h2["tbv"][400 * 24:] *= 3
        s2 = T.states(d2, h2)
        for k in ("D20", "VT", "MOM", "DUS", "DAS", "PR_D20", "PR_VT", "PR_MOM", "PR_DUS", "PR_DAS", "rsi"):
            a, b = s1[k][:400], s2[k][:400]
            self.assertTrue(np.allclose(a, b, equal_nan=True), k)

    def test_events_regime_interaction(self):
        n = 500
        s = {"PR_D20": np.full(n, 0.5), "PR_VT": np.full(n, 0.5), "PR_MOM": np.full(n, 0.5), "PR_DUS": np.full(n, 0.5), "PR_DAS": np.full(n, 0.5), "rsi": np.full(n, 50.0)}
        s["PR_D20"][400] = 0.9; s["rsi"][400] = 65.0          # bull regime + high delta
        s["PR_D20"][401] = 0.9; s["rsi"][401] = 50.0          # range regime + high delta
        s["PR_D20"][402] = 0.1; s["rsi"][402] = 35.0          # bear regime + low delta
        s["PR_D20"][100] = 0.9                                 # before warm-up
        e = T.events2(s, n)
        self.assertTrue(e["BULLR_D20HI"][400] and not e["RANGE_D20HI"][400])
        self.assertTrue(e["RANGE_D20HI"][401] and not e["BULLR_D20HI"][401])
        self.assertTrue(e["BEARR_D20LO"][402] and e["D20_LO"][402])
        self.assertFalse(e["D20_HI"][100])
        self.assertEqual(int(e["D20_HI"].sum()), 2)
        self.assertTrue(e["BULLR_D20HI"].sum() == 1)

    def test_rsi_boundaries_are_inclusive_for_extremes(self):
        n = 500
        s = {"PR_D20": np.full(n, 0.9), "PR_VT": np.full(n, 0.5), "PR_MOM": np.full(n, 0.5), "PR_DUS": np.full(n, 0.5), "PR_DAS": np.full(n, 0.5), "rsi": np.full(n, 60.0)}
        s["rsi"][401] = 40.0
        s["rsi"][402] = 59.9
        e = T.events2(s, n)
        self.assertTrue(e["BULLR_D20HI"][400])                     # RSI == 60 -> bull regime (>= 60)
        self.assertTrue(e["BEARR_D20HI"][401])                     # RSI == 40 -> bear regime (<= 40)
        self.assertTrue(e["RANGE_D20HI"][402])


if __name__ == "__main__":
    unittest.main(verbosity=1)
