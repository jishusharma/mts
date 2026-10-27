"""Tests for build_rows.py / event_table.py. Expected numbers are hand-computed from FORMULAS.md s.14
(delta = 2*taker_buy_vol - vol, summed over the session) and from the PRE_REG definitions; never from the code.
Run: python MyTradingSys/research/session_flow_context_2026-10-18/test_build_rows.py
"""
import math
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_rows as B  # noqa: E402
import event_table as E  # noqa: E402

MIN = 60000
D0 = 1759276800000  # 2025-10-01 00:00 UTC (Wednesday)


def bar(t, o, h, l, c, v, tbv):
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": v, "tbv": tbv}


# Hand fixture, one session of three bars
#  b1 o100 h102 l99  c101 v10 tbv7  -> delta 2*7-10  =  4
#  b2 o101 h104 l100 c103 v20 tbv8  -> delta 2*8-20  = -4
#  b3 o103 h103 l98  c99  v5  tbv4  -> delta 2*4-5   =  3
# session: o=100 c=99 h=104 l=98 vol=35 delta=3 delta_norm=3/35 chg=-0.01 (-100 bps)
SESS = [bar(D0, 100, 102, 99, 101, 10, 7), bar(D0 + MIN, 101, 104, 100, 103, 20, 8), bar(D0 + 2 * MIN, 103, 103, 98, 99, 5, 4)]


class TestSessionStats(unittest.TestCase):
    def test_stats(self):
        s = B.session_stats(SESS)
        self.assertEqual((s["o"], s["c"], s["h"], s["l"]), (100, 99, 104, 98))
        self.assertAlmostEqual(s["chg_bps"], -100.0, places=9)
        self.assertEqual(s["vol"], 35)
        self.assertEqual(s["delta"], 3)
        self.assertAlmostEqual(s["delta_norm"], 3 / 35, places=12)
        self.assertAlmostEqual(s["range_pct"], 6 / 100, places=12)

    def test_bounds_utc_00_08_1330_20(self):
        b = B.session_bounds(D0)
        self.assertEqual([x[0] for x in b], ["ASIA", "LDN", "US", "LATE"])
        self.assertEqual([x[1] for x in b], [D0, D0 + 8 * 3600000, D0 + 13 * 3600000 + 30 * MIN, D0 + 20 * 3600000])
        self.assertEqual(b[3][2], D0 + 24 * 3600000)


class TestOI(unittest.TestCase):
    def test_oi_chg_and_missing(self):
        oi_t = [D0, D0 + 5 * MIN, D0 + 8 * 3600000]
        oi_v = [1000.0, 1010.0, 1100.0]
        self.assertAlmostEqual(B.oi_chg(oi_t, oi_v, D0, D0 + 8 * 3600000), 0.10, places=12)
        # no sample within 10 minutes of the end -> NaN, never 0 (NOT_IN_DATA)
        self.assertTrue(math.isnan(B.oi_chg(oi_t, oi_v, D0, D0 + 9 * 3600000)))
        # a sample AFTER t must never be used
        self.assertTrue(math.isnan(B.oi_at(oi_t, oi_v, D0 - MIN)))


class TestLabels(unittest.TestCase):
    def test_quadrant(self):
        self.assertEqual(B.quadrant(-100.0, 0.10), "NEW_SHORT")
        self.assertEqual(B.quadrant(50.0, 0.10), "NEW_LONG")
        self.assertEqual(B.quadrant(50.0, -0.02), "SHORT_COVER")
        self.assertEqual(B.quadrant(-5.0, -0.02), "LONG_LIQ")
        self.assertEqual(B.quadrant(0.0, 0.10), "NA")
        self.assertEqual(B.quadrant(5.0, float("nan")), "NA")

    def test_sweep_reclaim(self):
        # session h=104 l=98 c=99; prior 24h high 103 low 97 -> high swept (104>103) and closed back below 103 -> BEAR
        self.assertEqual(B.sweep_reclaim(104, 98, 99, 103, 97), "SR_BEAR")
        # low swept and reclaimed
        self.assertEqual(B.sweep_reclaim(102, 96, 100, 103, 97), "SR_BULL")
        # high broke and CLOSED above: that is acceptance, not a reclaim
        self.assertEqual(B.sweep_reclaim(104, 98, 104, 103, 97), "NONE")
        self.assertEqual(B.sweep_reclaim(104, 96, 100, 103, 97), "BOTH")

    def test_context_buckets(self):
        self.assertEqual(B.htf_bucket(0.0751), "UP")
        self.assertEqual(B.htf_bucket(-0.0751), "DOWN")
        self.assertEqual(B.htf_bucket(0.075), "BALANCE")
        self.assertEqual(B.rangepos_bucket(0.2), "LOW")
        self.assertEqual(B.rangepos_bucket(0.5), "MID")
        self.assertEqual(B.rangepos_bucket(0.9), "HIGH")
        self.assertEqual(B.oitrend_bucket(0.03), "UP")
        self.assertEqual(B.oitrend_bucket(-0.03), "DOWN")
        self.assertEqual(B.oitrend_bucket(0.01), "FLAT")
        self.assertEqual(B.oitrend_bucket(float("nan")), "NA")
        # 2025-10-04 is a Saturday
        self.assertEqual(B.weekday_bucket(D0 + 3 * 86400000), "WEEKEND")
        self.assertEqual(B.weekday_bucket(D0), "WEEKDAY")

    def test_vol_pct_hand(self):
        hist = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
        # 0.065 -> 6 of 10 prior values are <= 0.065 -> 0.6
        self.assertAlmostEqual(B.vol_pct(0.065, hist), 0.6, places=12)
        self.assertEqual(B.vol_bucket(0.6), "MID")
        self.assertEqual(B.vol_bucket(0.9), "HIGH")
        self.assertEqual(B.vol_bucket(0.2), "LOW")
        self.assertTrue(math.isnan(B.vol_pct(0.05, hist[:3])))  # fewer than 10 prior sessions


def synth(days, start=D0 - 40 * 86400000):
    """Deterministic minute bars + 5m OI for a leak test."""
    bars, oi_t, oi_v = [], [], []
    n = days * 1440
    for i in range(n):
        t = start + i * MIN
        c = 100000 + 3000 * math.sin(i / 3000.0) + 40 * math.sin(i / 37.0)
        o = c - 5
        bars.append(bar(t, o, c + 20, o - 20, c, 10.0, 5.0 + 3 * math.sin(i / 91.0)))
        if i % 5 == 0:
            oi_t.append(t)
            oi_v.append(80000 + 2000 * math.sin(i / 5000.0))
    return bars, oi_t, oi_v


class TestBuild(unittest.TestCase):
    def test_rows_use_only_data_before_session_end_and_outcome_is_next_session(self):
        bars, oi_t, oi_v = synth(50)
        rows = B.build_rows(bars, oi_t, oi_v)
        r = [x for x in rows if x["date"] == "2025-10-05" and x["session"] == "LDN"][0]
        nxt = [x for x in rows if x["date"] == "2025-10-05" and x["session"] == "US"][0]
        self.assertAlmostEqual(r["next_ret_bps"], nxt["chg_bps"], places=9)
        self.assertAlmostEqual(r["next_range_pct"], nxt["range_pct"], places=12)
        # leak test: destroy everything at/after the session end; every feature (not the outcome) must be unchanged
        end = [s for s in B.session_bounds(D0 + 4 * 86400000) if s[0] == "LDN"][0][2]
        bars2 = [dict(b) if b["t"] < end else bar(b["t"], 1.0, 2.0, 0.5, 1.5, 1.0, 0.5) for b in bars]
        oi2 = [v if t < end else 1.0 for t, v in zip(oi_t, oi_v)]
        rows2 = B.build_rows(bars2, oi_t, oi2)
        r2 = [x for x in rows2 if x["date"] == "2025-10-05" and x["session"] == "LDN"][0]
        for k in ("chg_bps", "delta_norm", "oi_chg", "quadrant", "sr", "htf", "rangepos", "vol", "oitrend", "wkend", "ret30", "rangepos_x"):
            a, b = r[k], r2[k]
            if isinstance(a, float):
                self.assertAlmostEqual(a, b, places=9, msg=k)
            else:
                self.assertEqual(a, b, k)

    def test_split_guard(self):
        self.assertEqual(B.split_of("2025-10-01"), "DEV")
        self.assertEqual(B.split_of("2026-02-28"), "DEV")
        self.assertEqual(B.split_of("2026-03-01"), "VALIDATION")
        self.assertEqual(B.split_of("2026-07-01"), "HOLDOUT")
        self.assertEqual(B.split_of("2025-09-15"), "WARMUP")
        with self.assertRaises(PermissionError):
            B.select_split([{"date": "2026-03-05"}], "VALIDATION")


class TestEventTable(unittest.TestCase):
    def test_direction_and_cluster_se(self):
        # two days, two events each; x = [10, 30] day1, [20, 40] day2 -> mean 25
        # day sums of deviations: day1 (10-25)+(30-25) = -10 ; day2 (20-25)+(40-25) = 10
        # SE = sqrt(100 + 100) / 4 = 3.5355339
        xs = [10.0, 30.0, 20.0, 40.0]
        days = ["a", "a", "b", "b"]
        m, se, nd = E.cluster_mean_se(xs, days)
        self.assertAlmostEqual(m, 25.0)
        self.assertAlmostEqual(se, math.sqrt(200) / 4, places=9)
        self.assertEqual(nd, 2)
        self.assertEqual(E.direction("NEW_LONG", {"chg_bps": 40.0}), 1)
        self.assertEqual(E.direction("LONG_LIQ", {"chg_bps": -40.0}), -1)
        self.assertEqual(E.direction("SR_BEAR", {"chg_bps": 3.0}), -1)
        self.assertEqual(E.direction("SR_BULL", {"chg_bps": -3.0}), 1)

    def test_chi2_sf_known_values(self):
        self.assertAlmostEqual(E.chi2_sf(3.841458820694124, 1), 0.05, places=6)
        self.assertAlmostEqual(E.chi2_sf(5.991464547107979, 2), 0.05, places=6)
        self.assertAlmostEqual(E.chi2_sf(7.814727903251179, 3), 0.05, places=6)

    def test_wald_detects_planted_difference_and_not_null(self):
        import random
        rnd = random.Random(7)
        xs, days, cells = [], [], []
        for d in range(120):
            for k in range(2):
                c = "A" if (d + k) % 2 == 0 else "B"
                xs.append(rnd.gauss(0, 10) + (30 if c == "B" else 0))
                days.append(str(d))
                cells.append(c)
        w, df, p = E.wald_equal_means(xs, days, cells, min_n=10)
        self.assertEqual(df, 1)
        self.assertLess(p, 1e-6)
        xs0 = [rnd.gauss(0, 10) for _ in xs]
        w0, df0, p0 = E.wald_equal_means(xs0, days, cells, min_n=10)
        self.assertGreater(p0, 0.01)


if __name__ == "__main__":
    unittest.main(verbosity=1)
