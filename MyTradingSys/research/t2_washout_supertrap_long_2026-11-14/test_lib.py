"""Synthetic-bar tests for lib.py. Expected numbers are hand computed (see comments). No cache reads."""
import math
import os
import sys
import unittest

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib  # noqa: E402

H = lib.HOUR_MS


def flat_grid(n, price=100.0, vol=1.0):
    a = np.full(n, price)
    return {"t0": 0, "period": H, "n": n, "o": a.copy(), "h": a.copy(), "l": a.copy(), "c": a.copy(),
            "v": np.full(n, vol)}


def planted(after):
    """25 flat bars at 100, trap bar 25, signal bar 26, entry bar 27 (open 99), then `after(k)` opens."""
    g = flat_grid(60)
    # trap bar 25: o99 h99 l90 c95 v10 ; typical (99+90+95)/3 = 94.6667
    g["o"][25], g["h"][25], g["l"][25], g["c"][25], g["v"][25] = 99, 99, 90, 95, 10
    # signal bar 26: o95 h100 l95 c99 v1 ; typical 98 ; vwap = (94.6667*10+98)/11 = 94.9697 < 99 -> signal
    g["o"][26], g["h"][26], g["l"][26], g["c"][26], g["v"][26] = 95, 100, 95, 99, 1
    for k in range(27, 60):
        op = after(k)
        g["o"][k], g["h"][k], g["l"][k], g["c"][k], g["v"][k] = op, op + 0.5, op - 0.2, op, 1
    return g


class TestIndicators(unittest.TestCase):
    def test_rsi_worked_example(self):
        # FORMULAS.md: period 3, closes 10,12,11,14 -> 83.3333 ; then 13: ag=1.6667*2/3=1.1111, al=(0.3333*2+1)/3=0.5556 -> 66.6667
        r = lib.wilder_rsi([10, 12, 11, 14, 13], 3)
        self.assertTrue(np.isnan(r[:3]).all())
        self.assertAlmostEqual(r[3], 83.33333333, places=6)
        self.assertAlmostEqual(r[4], 66.66666667, places=6)

    def test_rsi_restarts_after_gap(self):
        c = [10, 12, 11, 14, np.nan, 13, 14, 13, 15]
        r = lib.wilder_rsi(c, 3)
        self.assertAlmostEqual(r[3], 83.33333333, places=6)
        self.assertTrue(np.isnan(r[4:8]).all())  # new run 13,14,13,15 seeds only at its 4th close
        # deltas +1,-1,+2 -> ag=1, al=1/3 -> rs 3 -> 75
        self.assertAlmostEqual(r[8], 75.0, places=6)

    def test_atr_hand(self):
        # n=3; closes: 10,11,13,12,10 ; bars (h,l): b1 12/9 b2 15/11 b3 14/12 b4 13/9
        h = [10, 12, 15, 14, 13]
        l = [10, 9, 11, 12, 9]
        c = [10, 11, 13, 12, 10]
        # TR1=max(3,2,1)=3 TR2=max(4,4,0)=4 TR3=max(2,1,1)=2 TR4=max(4,1,3)=4
        a = lib.wilder_atr(h, l, c, 3)
        self.assertAlmostEqual(a[3], 3.0, places=9)
        self.assertAlmostEqual(a[4], (3.0 * 2 + 4) / 3, places=9)

    def test_bollinger_population_sd(self):
        c = np.arange(1, 21, dtype=float)
        mid, lo, up = lib.bollinger(c)
        sd = math.sqrt(399 / 12)  # population variance (n^2-1)/12
        self.assertAlmostEqual(mid[19], 10.5)
        self.assertAlmostEqual(lo[19], 10.5 - 2 * sd, places=9)
        self.assertAlmostEqual(up[19], 10.5 + 2 * sd, places=9)
        self.assertTrue(np.isnan(lo[18]))

    def test_trap_exactly_half(self):
        # range 0..10, lower 5 -> exactly 50% -> trap ; just under -> no
        self.assertTrue(lib.trap_mask([10.0], [0.0], [5.0])[0])
        self.assertFalse(lib.trap_mask([10.0], [0.0], [4.9999])[0])
        self.assertTrue(lib.trap_mask([10.0], [0.0], [50.0])[0])  # whole candle below band
        self.assertFalse(lib.trap_mask([5.0], [5.0], [9.0])[0])  # no range
        self.assertFalse(lib.trap_mask([10.0], [0.0], [np.nan])[0])

    def test_aggregate_complete_only(self):
        q = 900_000
        t = np.array([0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12]) * q  # hour 1 (4..7) misses bar 7
        o = np.arange(12) + 100.0
        h = o + 5
        l = o - 5
        c = o + 1
        v = np.ones(12)
        ot, oo, oh, ol, oc, ov = lib.aggregate(t, o, h, l, c, v, q, H)
        # hour 0: bars 0-3 ; hour 2 (8..11) complete ; hour 1 incomplete ; hour 3 has only bar 12
        self.assertEqual(list(ot), [0, 2 * H])
        self.assertEqual(oo[0], 100.0)
        self.assertEqual(oh[0], 103.0 + 5)
        self.assertEqual(ol[0], 100.0 - 5)
        self.assertEqual(oc[0], 103.0 + 1)
        self.assertEqual(ov[0], 4.0)
        self.assertEqual(oo[1], 107.0)  # hour 2 = bars at 8q..11q = array positions 7..10, open 107

    def test_aggregate_utc_alignment(self):
        q = 900_000
        # bars start half an hour late: bars at 2,3,4,5 (q units) straddle two hours -> none complete
        t = np.arange(2, 6) * q
        out = lib.aggregate(t, np.ones(4), np.ones(4), np.ones(4), np.ones(4), np.ones(4), q, H)
        self.assertEqual(len(out[0]), 0)


class TestLookups(unittest.TestCase):
    def test_gate_series_causal(self):
        h4 = np.arange(0, 6) * lib.H4_MS
        rsi = np.array([10.0, 20, 30, 40, 50, 60])
        hours = np.array([3, 6, 7, 8, 4 * 4 - 1]) * H  # hour starts
        # hour 3 closes at 4h -> 4h bar starting 0 closed -> 10 ; hour 6 closes 7h -> bar 0 (closes 4h) -> 10
        # hour 7 closes 8h -> bar starting 4h closed -> 20 ; hour 8 closes 9h -> 20 ; hour 15 closes 16h -> bar 12h -> 40
        g = lib.gate_series(hours, h4, rsi)
        self.assertEqual(list(g), [10.0, 10.0, 20.0, 20.0, 40.0])
        # hour 0 closes at 1h: no 4h bar closed yet -> NaN
        self.assertTrue(np.isnan(lib.gate_series([0], h4, rsi)[0]))
        # causality: changing 4h bars that close after the trap close changes nothing
        rsi2 = rsi.copy()
        rsi2[2:] = 99.0  # bars starting >= 8h close at >= 12h
        g2 = lib.gate_series(hours[:3], h4, rsi2)
        self.assertEqual(list(g2), [10.0, 10.0, 20.0])

    def test_lookup_day_same_day(self):
        days = np.array([0, 1, 2]) * lib.DAY_MS
        vals = np.array(["BEAR", "BULL", "BASE"])
        self.assertEqual(lib.lookup_day(days, vals, 1 * lib.DAY_MS + 23 * H), "BULL")
        self.assertEqual(lib.lookup_day(days, vals, 2 * lib.DAY_MS), "BASE")
        self.assertIsNone(lib.lookup_day(days, vals, 5 * lib.DAY_MS))


class TestSignal(unittest.TestCase):
    def _bars(self):
        # trap bar 0: o100 h101 l90 c95 v10 -> typical 95.3333
        o = np.full(14, 100.0)
        h = np.full(14, 100.0)
        l = np.full(14, 100.0)
        c = np.full(14, 100.0)
        v = np.full(14, 1.0)
        o[0], h[0], l[0], c[0], v[0] = 100, 101, 90, 95, 10
        # bar 1: h97 l94 c95.3 v10: typical 95.4333 ; vwap=(95.3333+95.4333)/2=95.3833 -> close 95.3 NOT above
        o[1], h[1], l[1], c[1], v[1] = 95, 97, 94, 95.3, 10
        # bar 2: h98 l95 c96 v10: typical 96.3333 ; vwap=(953.333+954.333+963.333)/30=95.7 -> 96 > -> signal at 2
        o[2], h[2], l[2], c[2], v[2] = 95, 98, 95, 96, 10
        return o, h, l, c, v

    def test_first_close_above_vwap(self):
        o, h, l, c, v = self._bars()
        self.assertAlmostEqual(lib.anchored_vwap(o, h, l, c, v, 0, 1), 95.3833333333, places=8)
        self.assertEqual(lib.find_signal(o, h, l, c, v, 0), 2)

    def test_signal_causal(self):
        o, h, l, c, v = self._bars()
        base = lib.find_signal(o, h, l, c, v, 0)
        for arr in (o, h, l, c):
            arr[3:] = 500.0
        v[3:] = 1000.0
        self.assertEqual(lib.find_signal(o, h, l, c, v, 0), base)

    def test_signal_causal_when_first_bar_qualifies(self):
        o, h, l, c, v = self._bars()
        c[1] = 96.0
        h[1] = 97.0  # typical (97+94+96)/3=95.6667 ; vwap 95.5 -> signal at 1
        self.assertEqual(lib.find_signal(o, h, l, c, v, 0), 1)
        h[2:] = 200.0
        l[2:] = 200.0
        c[2:] = 200.0
        v[2:] = 1000.0  # a whole-window VWAP would sit near 200 and kill the signal
        self.assertEqual(lib.find_signal(o, h, l, c, v, 0), 1)

    def test_window_12_bars(self):
        o, h, l, c, v = self._bars()
        c[1:] = 90.0  # never above VWAP
        self.assertIsNone(lib.find_signal(o, h, l, c, v, 0))
        # signal exactly on bar 12 is inside the window, bar 13 is not
        c[12] = 200.0
        h[12] = 200.0
        self.assertEqual(lib.find_signal(o, h, l, c, v, 0), 12)
        c[12] = 90.0
        h[12] = 100.0
        c[13] = 200.0
        h[13] = 200.0
        self.assertIsNone(lib.find_signal(o, h, l, c, v, 0))


class TestSimulation(unittest.TestCase):
    def _arrs(self, n=30):
        o = np.full(n, 100.0)
        l = np.full(n, 99.0)
        return o, l

    def test_stop_hit_inside_bar(self):
        o, l = self._arrs()
        l[3] = 97.5  # D=2 stop 98, entry bar e=1
        x, px, why = lib.simulate_trade(o, l, 1, 2.0)
        self.assertEqual((x, px, why), (3, 98.0, "stop"))

    def test_stop_first_inside_bar_with_huge_high(self):
        o, l = self._arrs()
        l[2] = 97.0
        # there is no target in the rules: a huge high cannot rescue the bar, stop first
        x, px, why = lib.simulate_trade(o, l, 1, 2.0)
        self.assertEqual((px, why), (98.0, "stop"))

    def test_entry_bar_can_stop(self):
        o, l = self._arrs()
        l[1] = 98.0  # low equals stop -> hit
        self.assertEqual(lib.simulate_trade(o, l, 1, 2.0)[:2], (1, 98.0))

    def test_gap_fills_at_open(self):
        o, l = self._arrs()
        o[4] = 96.0
        l[4] = 95.0
        x, px, why = lib.simulate_trade(o, l, 1, 2.0)
        self.assertEqual((x, px, why), (4, 96.0, "gap_stop"))
        self.assertEqual(lib.fee_net_r(100.0, px, 2.0, 0.0)[0], -2.0)

    def test_time_exit_open_of_24th_bar(self):
        o, l = self._arrs()
        o[25] = 105.0  # entry bar 1 -> 1+24 = 25
        l[25] = 50.0  # the low of the exit bar is irrelevant (exit at its open)
        x, px, why = lib.simulate_trade(o, l, 1, 2.0)
        self.assertEqual((x, px, why), (25, 105.0, "time"))
        self.assertAlmostEqual(lib.fee_net_r(100.0, px, 2.0, 0.0)[0], 2.5)

    def test_last_checked_bar_is_23rd_after_entry(self):
        o, l = self._arrs()
        l[24] = 98.0  # bar e+23 touches the stop
        self.assertEqual(lib.simulate_trade(o, l, 1, 2.0)[:2], (24, 98.0))

    def test_missing_bars_unresolved(self):
        o, l = self._arrs(20)
        self.assertIsNone(lib.simulate_trade(o, l, 1, 2.0))  # needs bar 25
        o, l = self._arrs()
        o[10] = np.nan
        self.assertIsNone(lib.simulate_trade(o, l, 1, 2.0))

    def test_stop_before_gap_is_resolved(self):
        # stop hit on bar 3, bar 10 missing afterwards: the trade is resolved (old code dropped it)
        o, l = self._arrs()
        l[3] = 97.5
        o[10] = np.nan
        l[10] = np.nan
        self.assertEqual(lib.simulate_trade(o, l, 1, 2.0), (3, 98.0, "stop"))
        # data ends before the 24-bar window but the stop was hit earlier
        o2, l2 = self._arrs(12)
        l2[3] = 97.5
        self.assertEqual(lib.simulate_trade(o2, l2, 1, 2.0)[:2], (3, 98.0))
        # gap before the stop hit stays unresolved
        o3, l3 = self._arrs()
        o3[2] = np.nan
        l3[2] = np.nan
        l3[5] = 97.5
        self.assertIsNone(lib.simulate_trade(o3, l3, 1, 2.0))

    def test_vectorised_matches_scalar(self):
        rs = np.random.RandomState(7)
        n = 400
        o = 100 + np.cumsum(rs.randn(n))
        l = o - np.abs(rs.randn(n)) * 1.5
        es = np.arange(5, 300, 7)
        sf = np.full(len(es), 0.02)
        R, xi, ok = lib.sim_many(o, l, es, sf)
        self.assertTrue(ok.all())
        for i, e in enumerate(es):
            D = o[e] * 0.02
            x, px, why = lib.simulate_trade(o, l, e, D)
            self.assertEqual(x, xi[i])
            self.assertAlmostEqual((px - o[e]) / D, R[i], places=9)
        # out of range -> not ok
        self.assertFalse(lib.sim_many(o, l, [n - 3], [0.02])[2][0])


class TestFees(unittest.TestCase):
    def test_fee_constants(self):
        self.assertAlmostEqual(lib.FEE_RT_12, 0.0012)
        self.assertAlmostEqual(lib.FEE_RT_6, 0.0006)

    def test_fee_net_r(self):
        # entry 100, D 2, exit 102 -> R 1 ; fee 0.0012*100/2 = 0.06 -> 0.94
        r, rn = lib.fee_net_r(100.0, 102.0, 2.0, lib.FEE_RT_12)
        self.assertAlmostEqual(r, 1.0)
        self.assertAlmostEqual(rn, 0.94)
        # stop-out: -1 - 0.06
        self.assertAlmostEqual(lib.fee_net_r(100.0, 98.0, 2.0, lib.FEE_RT_12)[1], -1.06)

    def test_D_rule(self):
        self.assertEqual(lib.compute_D(100.0, 97.0, 0.5), 3.0)  # entry-low dominates
        self.assertEqual(lib.compute_D(100.0, 99.9, 1.5), 1.5)  # ATR dominates
        self.assertAlmostEqual(lib.compute_D(100.0, 99.9, 0.5), 1.2)  # 1.2% floor


class TestEpisodes(unittest.TestCase):
    def test_chain_gap_72h(self):
        s = np.array([0, 50, 130, 190, 262.5, 400]) * H
        # gaps: 50, 80 (>72 new), 60, 72.5 (>72 new), 137.5 (new)
        ids = lib.assign_episodes(s)
        self.assertEqual(list(ids), [1, 1, 2, 2, 3, 4])
        self.assertEqual(list(lib.assign_episodes([72 * H, 0])), [1, 1])  # exactly 72h stays together; order kept


class TestScanPlanted(unittest.TestCase):
    GATE_LOW = np.full(60, 30.0)

    def test_gate_blocks(self):
        g = planted(lambda k: 99.0)
        trades, _ = lib.scan_coin(g, np.full(60, 41.0))
        self.assertEqual(trades, [])

    def test_trap_found_hand_numbers(self):
        # lower BB at bar 25: 19 closes of 100 plus 95 -> mean 99.75, var (19*.25^2+4.75^2)/20=1.1875
        g = planted(lambda k: 99.0)
        mid, lo, up = lib.bollinger(g["c"])
        self.assertAlmostEqual(lo[25], 99.75 - 2 * math.sqrt(1.1875), places=9)
        self.assertTrue(lib.trap_mask(g["h"], g["l"], lo)[25])

    def test_null_series_loses_fee_over_D(self):
        g = planted(lambda k: 99.0)
        trades, _ = lib.scan_coin(g, self.GATE_LOW)
        self.assertEqual(len(trades), 1)
        t = trades[0]
        self.assertEqual((t["trap_idx"], t["signal_idx"], t["entry_idx"]), (25, 26, 27))
        self.assertEqual(t["entry"], 99.0)
        self.assertAlmostEqual(t["D"], 9.0, places=9)  # entry - trap low 99-90 beats ATR (~1.02) and 1.188
        self.assertEqual((t["exit_idx"], t["exit_reason"], t["exit_price"]), (51, "time", 99.0))
        r, rn = lib.fee_net_r(t["entry"], t["exit_price"], t["D"], lib.FEE_RT_12)
        self.assertAlmostEqual(r, 0.0)
        self.assertAlmostEqual(rn, -0.0012 * 99.0 / 9.0, places=9)  # = -0.0132

    def test_rising_series_known_positive_R(self):
        g = planted(lambda k: 99.0 + (k - 27))  # open of bar 51 = 123
        trades, _ = lib.scan_coin(g, self.GATE_LOW)
        t = trades[0]
        r, rn = lib.fee_net_r(t["entry"], t["exit_price"], t["D"], lib.FEE_RT_12)
        self.assertEqual(t["exit_price"], 123.0)
        self.assertAlmostEqual(r, 24.0 / 9.0, places=9)  # 2.6667
        self.assertAlmostEqual(rn, 24.0 / 9.0 - 0.0132, places=9)
        self.assertGreater(rn, 0)

    def test_falling_series_stops_at_minus_one_R(self):
        g = planted(lambda k: 99.0)
        g["l"][30] = 89.0  # stop = 99-9 = 90
        t = lib.scan_coin(g, self.GATE_LOW)[0][0]
        self.assertEqual((t["exit_idx"], t["exit_price"], t["exit_reason"]), (30, 90.0, "stop"))
        self.assertAlmostEqual(lib.fee_net_r(t["entry"], t["exit_price"], t["D"], 0.0)[0], -1.0)

    def test_scan_causal_in_future_bars(self):
        a = planted(lambda k: 99.0)
        ta = lib.scan_coin(a, self.GATE_LOW)[0][0]
        b = planted(lambda k: 99.0)
        for k in ("o", "h", "l", "c"):
            b[k][28:] = b[k][28:] * 1.0  # copy
        b["o"][40:] = 300.0
        b["c"][40:] = 300.0
        b["h"][40:] = 300.0
        tb = lib.scan_coin(b, self.GATE_LOW)[0][0]
        for key in ("trap_idx", "signal_idx", "entry_idx", "entry", "D", "stop"):
            self.assertEqual(ta[key], tb[key])

    def test_D_cap_skips(self):
        g = planted(lambda k: 99.0)
        g["l"][25] = 50.0  # entry - low = 49 > 10% of 99
        trades, skips = lib.scan_coin(g, self.GATE_LOW)
        self.assertEqual(trades, [])
        self.assertEqual(skips["D_over_cap"], 1)

    def test_one_position_first_trap_wins(self):
        g = planted(lambda k: 99.0)
        # a second trap-like candle while the first is open (bar 30) must be ignored
        g["l"][30] = 92.0
        g["c"][30] = 95.0
        trades, _ = lib.scan_coin(g, self.GATE_LOW)
        self.assertEqual([t["trap_idx"] for t in trades], [25])

    def test_gap_in_data_resets_indicators(self):
        g = planted(lambda k: 99.0)
        g["c"][10] = g["o"][10] = g["h"][10] = g["l"][10] = g["v"][10] = np.nan
        # bar 10 missing: only 14 contiguous bars before bar 25 -> no BB -> no trap
        trades, _ = lib.scan_coin(g, self.GATE_LOW)
        self.assertEqual(trades, [])


if __name__ == "__main__":
    unittest.main()
