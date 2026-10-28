"""Tests for the candle pilot. Expected values are hand-derived from PRE_REG_CANDLE_PILOT.md, not from the code.
Run: python -m unittest discover -s MyTradingSys/research/candle_patterns_2026-10-04/pilot -p "test_*.py"
"""
import sys
sys.dont_write_bytecode = True
import math
import random
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import candles  # noqa: E402
import cdata  # noqa: E402
import op_rule  # noqa: E402
import stats_lite  # noqa: E402


def B(o, c, h=None, l=None):
    return {"o": o, "c": c, "h": h if h is not None else max(o, c) + 1, "l": l if l is not None else min(o, c) - 1}


def sig(bars):
    return candles.signals(bars)


DOWN4 = [B(20, 19), B(19, 18), B(18, 17), B(17, 16)]   # closes 19,18,17,16 -> close[3] < close[0]: down context at i=4
UP4 = [B(10, 11), B(11, 12), B(12, 13), B(13, 14)]     # closes rising: up context at i=4


class TestPatterns(unittest.TestCase):
    def test_engulfing(self):
        s = sig([B(10, 8, 10.5, 7.5), B(7.5, 10.5, 11, 7)])
        self.assertEqual(s["bull_engulf"], [1])
        self.assertEqual(s["bear_engulf"], [])
        s = sig([B(8, 10, 10.5, 7.5), B(10.5, 7.5, 11, 7)])
        self.assertEqual(s["bear_engulf"], [1])
        # body not larger than the prior body: c=9.9 < o[i-1]=10 -> no engulf
        self.assertEqual(sig([B(10, 8, 10.5, 7.5), B(7.5, 9.9, 11, 7)])["bull_engulf"], [])

    def test_harami(self):
        s = sig([B(12, 8, 12.5, 7.5), B(9, 11, 11.5, 8.5)])
        self.assertEqual(s["bull_harami"], [1])
        self.assertEqual(s["bull_engulf"], [])
        s = sig([B(8, 12, 12.5, 7.5), B(11, 9, 11.5, 8.5)])
        self.assertEqual(s["bear_harami"], [1])

    def test_harami_requires_body_containment_and_doji_boundary(self):
        # close 13 is above the prior open 12: the body is not inside the prior body
        self.assertEqual(sig([B(12, 8, 12.5, 7.5), B(9, 13, 13.5, 8.5)])["bull_harami"], [])
        # range 10: body 1.5 is 15 percent -> not a doji; body 1.0 is exactly 10 percent -> doji
        self.assertEqual(sig([B(10, 11.5, 16, 6)])["doji"], [])
        self.assertEqual(sig([B(10, 11, 16, 6)])["doji"], [0])

    def test_hammer_family(self):
        self.assertEqual(sig(DOWN4 + [B(14, 14.5, 14.5, 12)])["hammer"], [4])
        self.assertEqual(sig(DOWN4 + [B(14, 14.5, 14.5, 12)])["hanging_man"], [])
        self.assertEqual(sig(UP4 + [B(16, 16.5, 16.5, 14)])["hanging_man"], [4])
        self.assertEqual(sig(UP4 + [B(16, 16.5, 16.5, 14)])["hammer"], [])
        self.assertEqual(sig(DOWN4 + [B(14, 14.5, 16.5, 14)])["inv_hammer"], [4])
        self.assertEqual(sig(UP4 + [B(16, 16.5, 18.5, 16)])["shooting_star"], [4])
        # lower wick only 1.5x body -> not a hammer
        self.assertEqual(sig(DOWN4 + [B(14, 14.5, 14.5, 13.25)])["hammer"], [])

    def test_stars(self):
        self.assertEqual(sig([B(20, 10), B(9.5, 9.8), B(9.8, 16)])["morning_star"], [2])
        self.assertEqual(sig([B(10, 20), B(20.5, 20.2), B(20.2, 14)])["evening_star"], [2])
        # recovery only to 14 < midpoint 15 -> no morning star
        self.assertEqual(sig([B(20, 10), B(9.5, 9.8), B(9.8, 14)])["morning_star"], [])

    def test_three_soldiers_crows(self):
        self.assertEqual(sig([B(10, 12), B(11, 14), B(13, 16)])["three_white_soldiers"], [2])
        self.assertEqual(sig([B(16, 14), B(15, 12), B(13, 10)])["three_black_crows"], [2])
        # third open 14.5 is above the previous close 14 (outside the body) -> no soldiers
        self.assertEqual(sig([B(10, 12), B(11, 14), B(14.5, 16)])["three_white_soldiers"], [])

    def test_piercing_dark_cloud(self):
        self.assertEqual(sig([B(20, 10), B(9, 16)])["piercing"], [1])
        self.assertEqual(sig([B(10, 20), B(21, 14)])["dark_cloud"], [1])
        self.assertEqual(sig([B(20, 10), B(9, 14)])["piercing"], [])   # 14 < midpoint 15

    def test_hikkake(self):
        m = [B(15, 15, 20, 10), B(15, 15, 18, 12), B(14, 14, 17, 11)]
        # indices: mother 0, inside 1, false break 2, bar3 close 17 (<=18), bar4 close 19 > 18 -> signal at i=4
        s = sig(m + [B(16, 17, 17.5, 15.5), B(17, 19, 19.5, 16.5)])
        self.assertEqual(s["hikkake_bull"], [4])
        # first confirming close at bar 3 -> signal at 3 only, not again at 4
        s = sig(m + [B(17, 19, 19.5, 16.5), B(19, 20, 20.5, 18.5)])
        self.assertEqual(s["hikkake_bull"], [3])
        bear = [B(15, 15, 20, 10), B(15, 15, 18, 12), B(15, 15, 19, 13)]
        self.assertEqual(sig(bear + [B(13, 11, 13.5, 10.5)])["hikkake_bear"], [3])

    def test_marubozu(self):
        base = [B(10, 11, 11, 9)] * 14   # rng 2 each
        self.assertEqual(sig(base + [B(10, 14, 14, 10)])["marubozu_up"], [14])
        self.assertEqual(sig(base + [B(14, 10, 14, 10)])["marubozu_dn"], [14])
        self.assertEqual(sig(base + [B(10, 12, 12, 10)])["marubozu_up"], [])   # rng 2 < 1.5*2

    def test_vol_states(self):
        self.assertEqual(sig([B(10, 10.1, 12, 8)])["doji"], [0])
        self.assertEqual(sig([B(10, 11, 12, 8), B(10, 10.5, 11, 9)])["inside_bar"], [1])
        rngs = [5, 4, 6, 5, 4, 6, 3]
        bars = [B(10, 10.1, 10 + r / 2.0, 10 - r / 2.0) for r in rngs]
        self.assertEqual(sig(bars)["nr7"], [6])

    def test_causal(self):
        rng = random.Random(7)
        bars, px = [], 100.0
        for _ in range(250):
            o = px
            c = o * (1 + rng.gauss(0, 0.02))
            h = max(o, c) * (1 + abs(rng.gauss(0, 0.01)))
            l = min(o, c) * (1 - abs(rng.gauss(0, 0.01)))
            bars.append({"o": o, "h": h, "l": l, "c": c})
            px = c
        full = sig(bars)
        for k in (60, 130, 200):
            part = sig(bars[:k])
            for name in full:
                self.assertEqual([i for i in full[name] if i < k], part[name], name)
        self.assertTrue(any(full[n] for n in candles.DIRECTIONAL))


class StubFunding:
    def __init__(self, rows):
        self.rows = rows

    def sum(self, t0, t1):
        return sum(r for t, r in self.rows if t0 < t <= t1)


def day_bars(rows, step=100):
    return [{"t": i * step, "o": o, "h": h, "l": l, "c": c} for i, (o, h, l, c) in enumerate(rows)]


ROWS = [(10, 12, 9, 11), (11, 13, 10, 12), (12, 14, 11, 13), (13, 13.5, 11, 11.5), (11.5, 12.5, 11, 12),
        (12, 13, 11.8, 12.8), (12.8, 13, 10, 10.5), (10.5, 13.0, 10.4, 12.9), (12.9, 13, 12, 12.5), (12.5, 12.6, 12.4, 12.5)]


class TestOpRule(unittest.TestCase):
    def test_p0a_hand_trades(self):
        r = op_rule.simulate(day_bars(ROWS), "P0a", StubFunding([]), day_ms=100, fee=0.0, slip=0.0)
        tr = r["trades"]
        self.assertEqual([(t["entry_i"], t["exit_i"]) for t in tr], [(1, 3), (5, 6), (7, 8)])
        self.assertEqual([(t["entry_px"], t["exit_px"]) for t in tr], [(11, 11.5), (12, 10.5), (12.8, 12.5)])
        self.assertAlmostEqual(tr[0]["gross"], math.log(11.5 / 11), places=12)
        self.assertAlmostEqual(tr[1]["net"], math.log(10.5 / 12), places=12)
        self.assertAlmostEqual(sum(r["net_d"]), sum(t["net"] for t in tr), places=12)
        self.assertFalse(r["open_at_end"])

    def test_exit_needs_strictly_lower_close(self):
        rows = [(10, 11, 9, 10.5), (10.6, 11, 10.4, 10.8), (10.8, 11, 10.6, 10.8), (10.8, 11, 10.0, 10.2)]
        r = op_rule.simulate(day_bars(rows), "P0a", StubFunding([]), day_ms=100, fee=0.0, slip=0.0)
        self.assertEqual([(t["entry_i"], t["exit_i"], t["exit_px"]) for t in r["trades"]], [(1, 3, 10.2)])

    def test_costs_and_funding_and_series_consistency(self):
        f = StubFunding([(250, 0.001), (450, 0.002)])
        r = op_rule.simulate(day_bars(ROWS), "P0a", f, day_ms=100, fee=0.0005, slip=0.0002)
        t0 = r["trades"][0]    # entry t=100 (open), exit t=399 -> window (100,399] holds the 250 settlement only
        self.assertAlmostEqual(t0["fund"], 0.001, places=12)
        self.assertAlmostEqual(t0["net"], math.log(11.5 / 11) - 0.0014 - 0.001, places=12)
        self.assertAlmostEqual(sum(r["net_d"]), sum(t["net"] for t in r["trades"]), places=12)

    def test_stop_buy_same_day_exit(self):
        rows = [(10, 11, 9, 10.5), (9.8, 10.2, 9.5, 10.0)]
        r = op_rule.simulate(day_bars(rows), "P0a", StubFunding([]), day_ms=100, fee=0.0, slip=0.0)
        self.assertEqual([(t["entry_i"], t["exit_i"], t["entry_px"], t["exit_px"]) for t in r["trades"]], [(1, 1, 10, 10.0)])
        # stop-buy entry time is open + half day for funding
        self.assertEqual(r["trades"][0]["t_entry"], 100 + 50)

    def test_short_mirror(self):
        rows = [(10, 11, 9, 9.5), (9.5, 10, 9, 9.2), (9.2, 10, 9.1, 9.8)]
        r = op_rule.simulate(day_bars(rows), "P0s", StubFunding([]), day_ms=100, fee=0.0, slip=0.0)
        t = r["trades"][0]
        self.assertEqual((t["entry_i"], t["exit_i"], t["entry_px"], t["exit_px"]), (1, 2, 9.5, 9.8))
        self.assertAlmostEqual(t["gross"], -math.log(9.8 / 9.5), places=12)
        # a short pays when funding is negative and receives when positive
        f = StubFunding([(150, 0.001)])
        r2 = op_rule.simulate(day_bars(rows), "P0s", f, day_ms=100, fee=0.0, slip=0.0)
        self.assertAlmostEqual(r2["trades"][0]["net"], t["gross"] + 0.001, places=12)

    def test_close_confirmed_entry(self):
        rows = [(10, 10.6, 9.9, 10.5), (10.2, 11.2, 10.1, 11), (11, 11.1, 10.7, 10.8)]
        r = op_rule.simulate(day_bars(rows), "P0c", StubFunding([]), day_ms=100, fee=0.0, slip=0.0)
        t = r["trades"][0]
        self.assertEqual((t["entry_i"], t["exit_i"], t["entry_px"], t["exit_px"]), (1, 2, 11, 10.8))

    def test_entry_ablation_enters_at_open_when_flat(self):
        rows = [(10, 10.6, 9.9, 10.5), (10.2, 11.2, 10.1, 11), (11, 11.1, 10.7, 10.8)]
        r = op_rule.simulate(day_bars(rows), "P0e", StubFunding([]), day_ms=100, fee=0.0, slip=0.0)
        t = r["trades"][0]
        self.assertEqual((t["entry_i"], t["entry_px"], t["exit_i"], t["exit_px"]), (1, 10.2, 2, 10.8))

    def test_open_position_at_end_is_not_counted(self):
        rows = [(10, 11, 9, 10.5), (10.6, 11.5, 10.5, 11), (11, 12, 10.9, 11.8)]
        r = op_rule.simulate(day_bars(rows), "P0a", StubFunding([]), day_ms=100, fee=0.0, slip=0.0)
        self.assertEqual(r["trades"], [])
        self.assertTrue(r["open_at_end"])

    def test_random_null_single_full_block_is_deterministic(self):
        bars = day_bars(ROWS)
        nulls = op_rule.random_null(bars, [len(bars)], 1, n_perm=5)
        want = math.log(12.5 / 10)
        for x in nulls:
            self.assertAlmostEqual(x, want, places=12)
        nulls_s = op_rule.random_null(bars, [len(bars)], -1, n_perm=3)
        self.assertAlmostEqual(nulls_s[0], -want, places=12)

    def test_random_null_blocks_fit_and_vary(self):
        bars = day_bars(ROWS)
        nulls = op_rule.random_null(bars, [2, 3], 1, n_perm=200)
        self.assertGreater(len(set(round(x, 9) for x in nulls)), 5)
        with self.assertRaises(ValueError):
            op_rule.random_null(bars, [6, 6], 1, n_perm=1)

    def test_curve_stats(self):
        s = op_rule.curve_stats([0.1, -0.2, 0.05, 0.05])
        self.assertAlmostEqual(s["total_log"], 0.0, places=12)
        self.assertAlmostEqual(s["max_dd_log"], -0.2, places=12)


class TestStats(unittest.TestCase):
    def test_bh(self):
        q = stats_lite.bh_qvalues([0.01, 0.04, 0.03, 0.005])
        for got, want in zip(q, [0.02, 0.04, 0.04, 0.02]):
            self.assertAlmostEqual(got, want, places=12)

    def _family(self, rng, m, planted=None):
        val = [rng.gauss(0, 1) for _ in range(m)]
        items = []
        for k in range(6):
            ev = [1 if rng.random() < 0.15 else 0 for _ in range(m)]
            if planted is not None and k == 0:
                for i in range(m):
                    if ev[i]:
                        val[i] += planted
            items.append({"name": "p%d" % k, "ev": ev, "val": val, "sign": 1, "min_n": 10})
        return items

    def test_calibration_under_null(self):
        hits = 0
        for seed in range(20):
            rng = random.Random(1000 + seed)
            res = stats_lite.block_boot_family(self._family(rng, 400), 400, 5, reps=300, seed=seed)
            if min(r["p_adj"] for r in res) < 0.05:
                hits += 1
        self.assertLessEqual(hits, 4)   # nominal 5 percent of 20 = 1; allow sampling noise

    def test_detects_planted_effect(self):
        rng = random.Random(5)
        res = stats_lite.block_boot_family(self._family(rng, 600, planted=1.0), 600, 5, reps=400, seed=1)
        r0 = [r for r in res if r["name"] == "p0"][0]
        self.assertLess(r0["p_adj"], 0.05)
        self.assertGreater(r0["stat"], 0.6)

    def test_insufficient_n_is_flagged_not_tested(self):
        items = [{"name": "rare", "ev": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0], "val": [float(i) for i in range(10)], "sign": 1, "min_n": 5}]
        res = stats_lite.block_boot_family(items, 10, 2, reps=10, seed=1)
        self.assertTrue(res[0]["insufficient"])
        self.assertIsNone(res[0]["p_adj"])


class TestData(unittest.TestCase):
    def test_resample_offset(self):
        one = [{"t": i * 60000, "o": i, "h": i + 5, "l": i - 5, "c": i + 0.5, "v": 1.0, "tbv": 0.5} for i in range(8)]
        out, dropped = cdata.resample_offset(one, 3, 0)
        self.assertEqual(len(out), 2)
        self.assertEqual(dropped, 1)                       # minutes 6,7 form a partial bucket
        b0 = out[0]
        self.assertEqual((b0["t"], b0["o"], b0["h"], b0["l"], b0["c"], b0["v"]), (0, 0, 7, -5, 2.5, 3.0))
        out1, _ = cdata.resample_offset(one, 3, 1)         # buckets start at minute 1: [1,2,3], [4,5,6]; minute 0 and 7 partial
        self.assertEqual([b["t"] for b in out1], [60000, 240000])

    def test_dev_only_guard(self):
        with self.assertRaises(PermissionError):
            cdata.load_daily(end_ms=cdata.DEV_END_MS + 86400000)
        with self.assertRaises(PermissionError):
            cdata.load_1m(cdata.HOURLY_START_MS, None)

    def test_funding_window(self):
        f = cdata.Funding([(100, 0.1), (200, 0.2), (300, 0.3)])
        self.assertAlmostEqual(f.sum(100, 300), 0.5)     # (100,300] excludes 100, includes 300
        self.assertAlmostEqual(f.sum(0, 99), 0.0)


if __name__ == "__main__":
    unittest.main()
