"""Tests for malkan_level_short (card malkan-level-short-4h-count-1109). Expected numbers are hand-derived from the
PRE_REG stack table and FORMULAS.md (RSI/SMA/WaveTrend), never read from the module under test."""
import csv
import math
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.rsi import malkan_level_short as m

H4 = 4 * 3600 * 1000
NAN = float("nan")
FIX = Path(__file__).resolve().parents[3] / "research" / "malkan_level_shorts_2026-11-09" / "fixture"


def mk(i, o, h, l, c, off=12):
    return {"t": (i + off) * H4, "o": o, "h": h, "l": l, "c": c}


def scenario():
    """13 bars, k=2 pivot at bar 3 (high 100). Zone 99.75..100.25. Sweep bar 8, RSI cross bar 9, entry bar 10."""
    rows = [
        (96, 97, 95, 96), (96, 96, 94, 95), (95, 97, 94, 96),      # 0-2 left of the pivot
        (97, 100, 96, 99),                                          # 3 pivot high 100
        (98, 96, 94, 95), (95, 95, 94, 94.5),                       # 4,5 right: low 94 is 6 pct under 100 -> rejected
        (95, 97, 94.5, 96), (96, 98, 95, 97.5),                     # 6,7 climb
        (99, 100.1, 98, 99.5),                                      # 8 sweep: high 100.1 > 100, close 99.5 < 100
        (99.5, 99.6, 99.0, 99.4),                                   # 9 trigger bar (open 99.5)
        (99.3, 99.5, 98.0, 98.5),                                   # 10 low 98.0 <= prior open 99.5 -> entry min(99.3, 99.5)
        (98.5, 99.6, 98.3, 99.0),                                   # 11 reaches 1R (98.3 <= 99.3 - 0.9001)
        (99.0, 99.2, 98.8, 99.0),
    ]
    bars = [mk(i, *r) for i, r in enumerate(rows)]
    n = len(bars)
    rsi = [70.0] * n
    ma = [65.0] * n
    rsi[8], ma[8] = 68.0, 66.0
    rsi[9], ma[9] = 60.0, 64.0
    wt1, wt2 = [30.0] * n, [30.0] * n
    wt1[8], wt2[8] = 55.0, 54.0
    wt1[9], wt2[9] = 50.0, 52.0
    ev = [0] * n
    ev[9] = -1
    ind = {"rsi": rsi, "ma": ma, "wt1": wt1, "wt2": wt2, "wt_ev": ev}
    htf = {"d": ([0, 24 * 3600000, 48 * 3600000], [62.0, 60.0, 55.0]), "w": ([-604800000], [70.0])}
    return bars, ind, htf


class TestZones(unittest.TestCase):
    def test_pivot_zone_values(self):
        bars, _, _ = scenario()
        zs = m.build_zones(bars, k=2)
        self.assertEqual([z["p"] for z in zs], [100, 100.1])   # bar 3 and the sweep bar 8 (confirmed at bar 10) are both 2/2 pivots
        z = zs[0]
        self.assertEqual((z["j"], z["confirm"], z["p"]), (3, 5, 100))
        self.assertAlmostEqual(z["lo"], 100 * 0.9975)   # 0.5 pct wide, centred
        self.assertAlmostEqual(z["hi"], 100 * 1.0025)

    def test_zone_needs_rejection(self):
        bars, _, _ = scenario()
        for q in (4, 5, 9, 10):
            bars[q]["l"] = 99.5                    # price never fell 1 pct under either pivot: no rejected level
        self.assertEqual(m.build_zones(bars, k=2), [])

    def test_unconfirmed_pivot_not_a_zone(self):
        bars, _, _ = scenario()
        self.assertEqual(m.build_zones(bars[:5], k=2), [])   # only 1 bar after the pivot, k=2 needs 2


class TestStructure(unittest.TestCase):
    def test_sweep_fires_on_bar_8_only(self):
        bars, ind, _ = scenario()
        z = m.build_zones(bars, k=2)[0]
        arm = {"div": "W", "basis": "close"}
        s = m.structure_at(8, bars, ind, z, arm)
        self.assertEqual(s["kind"], "sweep")
        self.assertEqual(s["ref"], 3)
        self.assertIsNone(m.structure_at(7, bars, ind, z, arm))   # bar 7 high 98 is below zone lo 99.75

    def test_close_vs_wick_arm(self):
        # bars: ref r=10 has high 100 close 98 rsi 70; bar i=14 has high 101 (wick HH) but close 97 (close LH), rsi 60
        n = 16
        bars = [mk(i, 90, 90, 90, 90) for i in range(n)]
        bars[10] = mk(10, 95, 100, 94, 98)
        bars[14] = mk(14, 96, 101, 95, 97)
        rsi = [50.0] * n
        rsi[10], rsi[14] = 70.0, 60.0
        ind = {"rsi": rsi, "ma": [50.0] * n}
        z = {"j": 0, "confirm": 2, "p": 100.0, "lo": 99.75, "hi": 100.25}
        z2 = dict(z, p=101.0, lo=100.7475, hi=101.2525)
        wick = m.structure_at(14, bars, ind, z2, {"div": "W", "basis": "wick"})
        close = m.structure_at(14, bars, ind, z2, {"div": "W", "basis": "close"})
        self.assertEqual(wick["kind"], "div")
        self.assertEqual(wick["ref"], 10)
        self.assertIsNone(close)

    def test_window_3_to_10_inclusive_vs_swing(self):
        # same shape but the reference is 14 bars back: window arm (<=10) misses it, swing arm (<=50) finds it
        n = 24
        bars = [mk(i, 90, 90, 90, 90) for i in range(n)]
        bars[4] = mk(4, 95, 100, 94, 100)      # swing high, close 100
        bars[18] = mk(18, 96, 101, 95, 101)    # close higher (101 > 100)
        rsi = [50.0] * n
        rsi[4], rsi[18] = 75.0, 65.0
        ind = {"rsi": rsi, "ma": [50.0] * n}
        z = {"j": 0, "confirm": 2, "p": 101.0, "lo": 100.7475, "hi": 101.2525}
        self.assertIsNone(m.structure_at(18, bars, ind, z, {"div": "W", "basis": "close"}))
        s = m.structure_at(18, bars, ind, z, {"div": "S", "basis": "close"})
        self.assertEqual((s["kind"], s["ref"]), ("div", 4))

    def test_window_edge_inclusive_counts(self):
        # bars = i - r + 1: ref 9 back -> 10 bars (in), ref 10 back -> 11 bars (out)
        for back, expect in ((9, True), (10, False)):
            n = 20
            bars = [mk(i, 90, 90, 90, 90) for i in range(n)]
            i = 15
            r = i - back
            bars[r] = mk(r, 95, 100, 94, 100)
            bars[i] = mk(i, 96, 101, 95, 101)
            rsi = [50.0] * n
            rsi[r], rsi[i] = 75.0, 65.0
            z = {"j": 0, "confirm": 2, "p": 101.0, "lo": 100.7475, "hi": 101.2525}
            got = m.structure_at(i, bars, {"rsi": rsi, "ma": [50.0] * n}, z, {"div": "W", "basis": "close"})
            self.assertEqual(got is not None, expect, back)


class TestTriggerEntryOutcome(unittest.TestCase):
    def test_trigger_cross_below_ma_with_rsi_ge_60(self):
        bars, ind, _ = scenario()
        self.assertEqual(m.trigger_after(8, ind, tw=12, strict60=False), 9)
        # strict arm: bar 9 RSI is exactly 60.0, not < 60 -> no trigger
        self.assertIsNone(m.trigger_after(8, ind, tw=12, strict60=True))
        ind["rsi"][9] = 59.0
        self.assertEqual(m.trigger_after(8, ind, tw=12, strict60=True), 9)

    def test_trigger_needs_rsi_to_have_been_60(self):
        bars, ind, _ = scenario()
        for i in range(len(ind["rsi"])):
            ind["rsi"][i] = 55.0 if i < 9 else 50.0
        ind["ma"] = [54.0] * 8 + [56.0, 52.0, 52.0, 52.0, 52.0]
        ind["rsi"][8] = 55.0
        self.assertIsNone(m.trigger_after(8, ind, tw=12, strict60=False))

    def test_entry_trade_through_prior_open_fill(self):
        bars, _, _ = scenario()
        j, px = m.entry_after(9, bars, win=3)
        self.assertEqual(j, 10)
        self.assertEqual(px, 99.3)                 # min(open 99.3, prior open 99.5)
        bars[10]["o"] = 99.9                        # opens above prior open, low 98.0 trades through it
        self.assertEqual(m.entry_after(9, bars, win=3), (10, 99.5))

    def test_entry_none_when_never_traded_through(self):
        bars, _, _ = scenario()
        bars[10]["l"] = bars[11]["l"] = bars[12]["l"] = 99.55
        self.assertIsNone(m.entry_after(9, bars, win=3))

    def test_outcome_one_r_target_fee_net(self):
        bars, _, _ = scenario()
        entry, stop = 99.3, 100.1 * 1.001
        risk = stop - entry                          # 0.9001
        o = m.simulate(bars, 10, entry, stop, target_r=1.0, horizon=60)
        self.assertEqual(o["outcome"], "target")
        self.assertAlmostEqual(o["r_gross"], 1.0)
        exit_px = entry - risk
        self.assertAlmostEqual(o["r_net"], 1.0 - 0.0004 * (entry + exit_px) / risk, places=9)
        self.assertTrue(o["hit1"])

    def test_outcome_stop_first_on_same_bar(self):
        bars, _, _ = scenario()
        bars[10]["l"] = 98.5                         # no 1R yet on the entry bar (target 98.3999)
        bars[11]["h"] = 101.0                        # same bar touches both the 1R target and the stop: stop wins
        entry, stop = 99.3, 100.1 * 1.001
        o = m.simulate(bars, 10, entry, stop, target_r=1.0, horizon=60)
        self.assertEqual(o["outcome"], "stop")
        self.assertAlmostEqual(o["r_gross"], -1.0)
        risk = stop - entry
        self.assertAlmostEqual(o["r_net"], -1.0 - 0.0004 * (entry + stop) / risk, places=9)
        self.assertFalse(o["hit1"])

    def test_outcome_time_exit_marks_to_close(self):
        bars, _, _ = scenario()
        o = m.simulate(bars, 10, 99.3, 120.0, target_r=2.0, horizon=2)   # wide stop, unreachable 2R
        self.assertEqual(o["outcome"], "time")
        self.assertEqual(o["exit_idx"], 12)
        risk = 120.0 - 99.3
        self.assertAlmostEqual(o["r_gross"], (99.3 - 99.0) / risk)


class TestHtf(unittest.TestCase):
    def test_daily_fail(self):
        self.assertTrue(m.htf_ok(56.8, 60.0, None, None))        # below 60 and turning down
        self.assertFalse(m.htf_ok(61.0, 62.0, None, None))       # still above 60
        self.assertFalse(m.htf_ok(55.0, 54.0, None, None))       # below 60 but rising

    def test_weekly_back_under_60(self):
        self.assertTrue(m.htf_ok(70.0, 69.0, 57.0, [58.0, 61.0, 63.3, 62.0]))
        self.assertFalse(m.htf_ok(70.0, 69.0, 57.0, [50.0, 52.0, 55.0, 56.0]))   # never was above 60

    def test_missing_htf_fails_closed(self):
        self.assertFalse(m.htf_ok(None, None, None, None))

    def test_htf_uses_last_closed_bar_only(self):
        d = ([0, 24 * 3600000, 48 * 3600000], [62.0, 60.0, 55.0])
        # t = 95h: the 72h-open daily bar (not in list) is open; last closed in list is open 48h? closes 72h <= 95h
        self.assertEqual(m.htf_asof(d, 71 * 3600000, 24 * 3600000, back=0), 60.0)   # open 48h closes 72h > 71h: not yet
        self.assertEqual(m.htf_asof(d, 72 * 3600000, 24 * 3600000, back=0), 55.0)
        self.assertEqual(m.htf_asof(d, 72 * 3600000, 24 * 3600000, back=1), 60.0)


class TestScan(unittest.TestCase):
    def test_full_chain_fires_with_hand_numbers(self):
        bars, ind, htf = scenario()
        ch = m.scan(bars, ind, htf, {"div": "W", "basis": "close", "strict60": False}, k=2)
        self.assertEqual(len(ch), 1)
        c = ch[0]
        self.assertEqual((c["setup"], c["trigger"], c["entry_idx"]), (8, 9, 10))
        self.assertAlmostEqual(c["entry"], 99.3)
        self.assertAlmostEqual(c["stop"], 100.1 * 1.001)
        self.assertTrue(c["l1"] and c["l2"] and c["l3"] and c["l4"] and c["l5"])
        self.assertTrue(c["fires"])

    def test_wavetrend_gate_blocks(self):
        bars, ind, htf = scenario()
        ind["wt_ev"] = [0] * len(bars)
        c = m.scan(bars, ind, htf, {"div": "W", "basis": "close", "strict60": False}, k=2)[0]
        self.assertFalse(c["l4"])
        self.assertFalse(c["fires"])
        self.assertTrue(c["l3"])

    def test_wavetrend_nan_fails_closed(self):
        bars, ind, htf = scenario()
        ind["wt1"] = [NAN] * len(bars)
        c = m.scan(bars, ind, htf, {"div": "W", "basis": "close", "strict60": False}, k=2)[0]
        self.assertFalse(c["l4"])

    def test_htf_gate_blocks(self):
        bars, ind, htf = scenario()
        htf["d"] = ([0, 24 * 3600000, 48 * 3600000], [62.0, 60.0, 65.0])
        c = m.scan(bars, ind, htf, {"div": "W", "basis": "close", "strict60": False}, k=2)[0]
        self.assertFalse(c["l5"])
        self.assertFalse(c["fires"])

    def test_close_above_zone_before_trigger_drops_chain(self):
        bars, ind, htf = scenario()
        bars[9].update(h=100.6, c=100.5)            # price accepted above the zone top (100.25) between setup and trigger
        arm = {"div": "W", "basis": "close", "strict60": False}
        self.assertEqual([c for c in m.scan(bars, ind, htf, arm, k=2) if c["zone_p"] == 100], [])

    def test_tight_stop_flagged_and_not_fired(self):
        bars, ind, htf = scenario()
        bars[9].update(o=100.0, h=100.0)            # entry min(open 100.0, prior open 100.0) = 100.0; stop 100.2001 = 0.2 pct < 0.40 pct
        bars[10].update(o=100.0)
        c = m.scan(bars, ind, htf, {"div": "W", "basis": "close", "strict60": False}, k=2)[0]
        self.assertTrue(c["too_tight"])
        self.assertFalse(c["fires"])


class TestOperatorPoints(unittest.TestCase):
    """The 5 operator-marked shorts (READING.md). Window = operator entry bar .. +24h (UTC)."""

    @classmethod
    def setUpClass(cls):
        def load(name):
            with open(FIX / name, newline="") as f:
                r = csv.DictReader(f)
                return [{"t": int(x["t"]), "o": float(x["o"]), "h": float(x["h"]), "l": float(x["l"]), "c": float(x["c"])} for x in r]
        cls.b4, cls.bd, cls.bw = load("btc_4h_2026-05_10.csv"), load("btc_1d_2025-08_2026-10.csv"), load("btc_1w_2025-06_2026-10.csv")
        cls.ind, cls.htf = m.indicators_and_htf(cls.b4, cls.bd, cls.bw)

    def ms(self, s):
        from datetime import datetime, timezone
        return int(datetime.strptime(s, "%Y-%m-%d %H").replace(tzinfo=timezone.utc).timestamp() * 1000)

    POINTS = {
        "C1": ("2026-08-28 00", "2026-08-29 00"),
        "C2": ("2026-09-03 20", "2026-09-04 20"),
        "V1": ("2026-09-23 00", "2026-09-24 00"),
        "V2": ("2026-10-06 08", "2026-10-07 08"),
        "C3": ("2026-10-21 16", "2026-10-22 04"),
    }

    def fired(self, name, **arm):
        a, b = self.POINTS[name]
        lo, hi = self.ms(a), self.ms(b)
        out = []
        for c in m.scan(self.b4, self.ind, self.htf, arm):
            if lo <= self.b4[c["entry_idx"]]["t"] <= hi:
                out.append(c)
        return out

    ARMS = [{"div": d, "basis": bs, "strict60": st} for d in "WS" for bs in ("close", "wick") for st in (False, True)]
    # Operator entry prices from READING.md (his reads, not from this code): C1 79,660 and C3 82,925.
    # Named misses (checked on all 8 arms; the test pins them so a drift is noticed):
    #   C2: layer 2. A level trade with no divergence and no sweep (READING.md "No divergence at all (C2, C3)"); C3 only fires
    #       because it sweeps the 10-12 high. The stack by design needs structure.
    #   V1: layer 1. Operator red line 86,807 vs the nearest confirmed pivot zone 87,396 (lo 87,177); the setup bar 09-23 00 high
    #       86,975 never reaches it (proxy miss: his hand-drawn line is not a 5/5 pivot).
    #   V2: layer 1. Setup bar 10-04 20 high 86,800; the pivot zone 87,220 (lo 87,002, confirmed 10-03 08) is not reached; the
    #       86,999 pivot confirms only on 10-05 20, after the setup (same proxy miss; its 15-bar divergence is outside the 3-10 window).
    MISSES = ("C2", "V1", "V2")

    def test_operator_points_fire(self):
        for arm in self.ARMS:
            c1 = self.fired("C1", **arm)
            c3 = self.fired("C3", **arm)
            self.assertEqual(len(c1), 1, arm)
            self.assertEqual(len(c3), 1, arm)
            self.assertLess(abs(c1[0]["entry"] - 79660), 1.0, arm)
            self.assertLess(abs(c3[0]["entry"] - 82925), 1.0, arm)
            self.assertTrue(c1[0]["l1"] and c1[0]["l2"] and c1[0]["l3"] and c1[0]["l4"], arm)
            self.assertFalse(c1[0]["l5"], arm)           # READING.md layer 5 is seen in V2/C3 only, not C1
            self.assertTrue(c3[0]["fires"], arm)         # all five layers, 4h daily-RSI gate included
            for name in self.MISSES:
                self.assertEqual(self.fired(name, **arm), [], (name, arm))

    def test_fixture_is_public_klines_shape(self):
        self.assertEqual(self.b4[1]["t"] - self.b4[0]["t"], H4)
        self.assertGreater(len(self.b4), 1000)


if __name__ == "__main__":
    unittest.main()
