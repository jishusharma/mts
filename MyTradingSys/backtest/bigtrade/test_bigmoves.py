"""
Tests for bigmoves.py. Every expected number below is hand-computed on a tiny bar series and written in the comment next to it;
none was produced by running the code under test. ATR definition and the period-3 worked example come from
MyTradingSys/backtest/layers/FORMULAS.md section 12 (Wilder TR; plain SMA vs Wilder smoothing).
Run: python -m pytest MyTradingSys/backtest/bigtrade -q   (or python -m unittest from the repo root)
"""
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from MyTradingSys.backtest.bigtrade import bigmoves as bm  # noqa: E402

T0 = 1_700_000_100_000  # divisible by 300000, so 5m buckets align
MS5 = 300_000


def path_bars(prices, tf="5m", half_range=0.0):
    """Bars whose close/open is the price; high/low = price +- half_range. t_open = T0 + i * tf_ms."""
    p = np.array(prices, dtype=float)
    n = len(p)
    ms = bm.TF_MS[tf]
    t_open = T0 + np.arange(n, dtype=np.int64) * ms
    return {"tf": tf, "t_open": t_open, "t_close": t_open + ms, "o": p.copy(), "h": p + half_range, "l": p - half_range,
            "c": p.copy(), "v": np.ones(n), "n_bars": np.full(n, ms // 60000), "gap_count": np.zeros(n, dtype=np.int64)}


# Zero-range path used by the zigzag tests (high = low = open = close = P[i]), ATR forced to 1.
P = [10, 12, 15, 13, 11, 8, 9, 9.8, 7.0, 14, 17, 16, 12]


class TestAtr(unittest.TestCase):
    # FORMULAS.md section 12 worked example: highs [10,11,12,11], lows [9,9,10,9], closes [9.5,10.5,11.5,10].
    H = [10, 11, 12, 11]
    L = [9, 9, 10, 9]
    C = [9.5, 10.5, 11.5, 10]

    def test_true_range_is_undefined_at_zero_and_matches_example(self):
        # TR[1] = max(2, 1.5, 0.5) = 2; TR[2] = max(2, 1.5, 0.5) = 2; TR[3] = max(2, 0.5, 2.5) = 2.5
        tr = bm.true_range(self.H, self.L, self.C)
        self.assertTrue(math.isnan(tr[0]))
        self.assertEqual(list(tr[1:]), [2.0, 2.0, 2.5])

    def test_sma_and_wilder_seed_equal_2_1667_then_diverge(self):
        h, l, c = self.H + [13], self.L + [11], self.C + [12.5]
        # TR[4] = max(13-11, |13-10|, |11-10|) = 3
        w = bm.atr(h, l, c, 3, "wilder")
        s = bm.atr(h, l, c, 3, "sma")
        self.assertTrue(all(math.isnan(x) for x in w[:3]) and all(math.isnan(x) for x in s[:3]))
        self.assertAlmostEqual(w[3], 6.5 / 3, places=9)  # seed = mean(2, 2, 2.5) = 2.16667
        self.assertAlmostEqual(s[3], 6.5 / 3, places=9)
        self.assertAlmostEqual(w[4], (6.5 / 3 * 2 + 3) / 3, places=9)  # Wilder: (2.16667*2 + 3)/3 = 2.44444
        self.assertAlmostEqual(s[4], (2 + 2.5 + 3) / 3, places=9)  # SMA: mean(TR[2..4]) = 2.5

    def test_atr_is_strictly_causal(self):
        # Extend the FORMULAS.md example with bar5 (h 13.5, l 12, c 13) and a violent bar6 (h 20, l 10, c 15), period 3.
        # TR[5] = max(1.5, |13.5-12.5|, |12-12.5|) = 1.5 ; Wilder ATR[5] = (2.44444*2 + 1.5)/3 = 2.12963 (TR[4]=3, ATR[4]=2.44444 as above)
        h = self.H + [13, 13.5, 20]
        l = self.L + [11, 12, 10]
        c = self.C + [12.5, 13, 15]
        full = bm.atr(h, l, c, 3, "wilder")
        prefix = bm.atr(h[:6], l[:6], c[:6], 3, "wilder")
        self.assertAlmostEqual(prefix[5], (6.5 / 3 * 2 + 3) / 3 * 2 / 3 + 0.5, places=9)  # = (2.44444*2 + 1.5)/3 = 2.12963
        for i in range(3, 6):
            self.assertEqual(full[i], prefix[i])  # bar6 (and later) never changes an earlier ATR
        h2 = list(h)
        h2[4] = 99.0
        changed = bm.atr(h2, l, c, 3, "wilder")
        self.assertEqual(changed[3], full[3])  # changing bar 4 leaves bars before it alone
        self.assertNotEqual(changed[4], full[4])
        s_full, s_prefix = bm.atr(h, l, c, 3, "sma"), bm.atr(h[:6], l[:6], c[:6], 3, "sma")
        for i in range(3, 6):
            self.assertEqual(s_full[i], s_prefix[i])


class TestForwardLabels(unittest.TestCase):
    O = [10, 10, 11, 12, 11, 13]
    Hh = [10.5, 11.5, 12.5, 12.5, 13.5, 14]
    L = [9.5, 9.5, 10.5, 10.0, 10.9, 12.5]
    A = [2, 1, float("nan"), 1, 1, 1]

    def test_hand_computed_labels_h2(self):
        lab = bm.forward_labels(self.O, self.Hh, self.L, self.A, 2)
        # j=0, atr 2, entry open[1]=10, bars 1..2. long: max high 12.5 (bar 2) -> mfe 2.5/2 = 1.25; min low over bars 1..2 = 9.5 -> mae 0.5/2 = 0.25
        #   short: min low 9.5 (bar 1) -> mfe 0.5/2 = 0.25; max high over bar 1 only = 11.5 -> mae 1.5/2 = 0.75
        self.assertAlmostEqual(lab["mfe_long"][0], 1.25)
        self.assertAlmostEqual(lab["mae_long"][0], 0.25)
        self.assertAlmostEqual(lab["mfe_short"][0], 0.25)
        self.assertAlmostEqual(lab["mae_short"][0], 0.75)
        # j=1, atr 1, entry open[2]=11, bars 2..3. highs 12.5, 12.5 TIE -> first bar (2): mfe 1.5; mae = 11 - low[2] = 0.5 (a last-tie rule would give 1.0)
        #   short: lows 10.5, 10.0 -> min 10.0 at bar 3: mfe 1.0; max high over bars 2..3 = 12.5 -> mae 1.5
        self.assertAlmostEqual(lab["mfe_long"][1], 1.5)
        self.assertAlmostEqual(lab["mae_long"][1], 0.5)
        self.assertAlmostEqual(lab["mfe_short"][1], 1.0)
        self.assertAlmostEqual(lab["mae_short"][1], 1.5)
        # j=2: ATR undefined -> NaN for all four
        for name in bm.LABEL_NAMES:
            self.assertTrue(math.isnan(lab[name][2]))
        # j=3, atr 1, entry open[4]=11, bars 4..5. long: max 14 (bar 5) mfe 3.0; min low 10.9 -> mae 0.1. short: min 10.9 (bar 4) mfe 0.1; high bar 4 = 13.5 -> mae 2.5
        self.assertAlmostEqual(lab["mfe_long"][3], 3.0)
        self.assertAlmostEqual(lab["mae_long"][3], 0.1)
        self.assertAlmostEqual(lab["mfe_short"][3], 0.1)
        self.assertAlmostEqual(lab["mae_short"][3], 2.5)
        # j=4, j=5: fewer than H=2 bars follow -> NaN
        for j in (4, 5):
            for name in bm.LABEL_NAMES:
                self.assertTrue(math.isnan(lab[name][j]))

    def test_chunking_does_not_change_labels(self):
        a = bm.forward_labels(self.O, self.Hh, self.L, self.A, 2, chunk=1)
        b = bm.forward_labels(self.O, self.Hh, self.L, self.A, 2, chunk=100)
        for name in bm.LABEL_NAMES:
            np.testing.assert_array_equal(a[name], b[name])


class TestZigzag(unittest.TestCase):
    def piv(self, prices, r):
        p = np.array(prices, dtype=float)
        return bm.zigzag_pivots(p, p, p, p, np.ones(len(p)), r)

    def test_two_r_values_give_different_pivots(self):
        # r=1.5 (threshold 1.5): L0=10; up 2 >= 1.5 at i=1. H2=15 confirmed at i=3 (13 <= 13.5). L5=8 confirmed at i=7 (9.8 >= 9.5).
        #   H7=9.8 confirmed at i=8 (7 <= 8.3). L8=7 confirmed at i=9 (14 >= 8.5). H10=17 confirmed at i=12 (12 <= 15.5).
        self.assertEqual(self.piv(P, 1.5), [(0, -1, 10), (2, 1, 15), (5, -1, 8), (7, 1, 9.8), (8, -1, 7.0), (10, 1, 17)])
        # r=2.0: 9.8 - 8 = 1.8 < 2 so the 8 -> 9.8 bounce is not a reversal; 7 < 8 extends the low to bar 8.
        #   H2 confirmed at i=3 (13 <= 13, inclusive); L8=7 confirmed at i=9; H10 confirmed at i=12 (12 <= 15).
        self.assertEqual(self.piv(P, 2.0), [(0, -1, 10), (2, 1, 15), (8, -1, 7.0), (10, 1, 17)])

    def test_unconfirmed_trailing_swing_is_not_a_pivot(self):
        # Series cut after bar 10 (the 17): H10 was never followed by a 1.5 reversal, so it must not be emitted; L8 was confirmed at i=9.
        self.assertEqual(self.piv(P[:11], 1.5)[-1], (8, -1, 7.0))

    def test_bar_cannot_confirm_its_own_reversal(self):
        # bar2 makes a new high 13 AND trades down to 10 (3 point range). It extends the swing; it must not reverse it on its own bar.
        # L0=10 is confirmed by bar1 (12 - 10 = 2 >= 1.5). bars 3 and 4 have lows 11.8 and 12.0 (> 13 - 1.5 = 11.5): no reversal yet.
        # bar5 low 11.0 <= 11.5 confirms H2=13. Expected [(0,-1,10),(2,1,13)]; a same-bar rule would also emit a low at bar 2 (price 10).
        o = [10, 12, 12, 11.9, 12.2, 11.0]
        h = [10, 12, 13, 12.0, 12.4, 11.0]
        l = [10, 12, 10, 11.8, 12.0, 11.0]
        c = [10, 12, 10.5, 11.9, 12.3, 11.0]
        out = bm.zigzag_pivots(o, h, l, c, np.ones(6), 1.5)
        self.assertEqual(out, [(0, -1, 10), (2, 1, 13)])

    def test_reversal_of_exactly_r_atr_confirms_the_pivot(self):
        # prices 10, 12, 15, 13.5, 16 with ATR 1, r=1.5. L0 confirmed at i=1 (+2). High 15 at bar 2. Bar 3 = 13.5 = 15 - 1.5 is a reversal of EXACTLY r x ATR:
        # inclusive rule -> H2 confirmed at i=3, then bar 4 (16 >= 13.5 + 1.5) confirms L3.  Expected [(0,-1,10),(2,1,15),(3,-1,13.5)].
        # (A strict rule would not confirm at i=3, bar 4 would simply extend the high and the list would end at L0.)
        self.assertEqual(self.piv([10, 12, 15, 13.5, 16], 1.5), [(0, -1, 10), (2, 1, 15), (3, -1, 13.5)])

    def test_equal_highs_keep_the_earlier_bar(self):
        # bar1 and bar2 both have high 12; bar2 low 11.9 does not reverse (needs <= 10.5). bar3 low 10 does: pivot is bar 1, not bar 2.
        o = [10, 12, 12, 10]
        h = [10, 12, 12, 10]
        l = [10, 12, 11.9, 10]
        c = [10, 12, 12, 10]
        out = bm.zigzag_pivots(o, h, l, c, np.ones(4), 1.5)
        self.assertEqual(out, [(0, -1, 10), (1, 1, 12)])

    def test_no_pivots_before_atr_is_defined(self):
        atr_arr = np.array([np.nan, np.nan, 1.0, 1.0, 1.0, 1.0])
        p = np.array([10, 20, 10, 20, 10, 20], dtype=float)
        out = bm.zigzag_pivots(p, p, p, p, atr_arr, 1.5)
        self.assertTrue(all(i >= 2 for i, _, _ in out))


class TestBuildLegs(unittest.TestCase):
    # Step-0.5 series with high = P + 0.5 and low = P - 0.5: TR is exactly 1 on every bar, so ATR (period 3) is 1 from index 3.
    S = [10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 13.5, 13.0, 12.5, 12.0, 11.5, 11.0, 10.5, 10.0, 9.5, 9.0,
         9.5, 10.0, 10.5, 11.0]

    def bars(self):
        b = path_bars(self.S, half_range=0.5)
        b["atr_wilder"] = bm.atr(b["h"], b["l"], b["c"], 3, "wilder")
        b["atr_sma"] = bm.atr(b["h"], b["l"], b["c"], 3, "sma")
        return b

    def test_atr_is_exactly_one(self):
        b = self.bars()
        self.assertTrue(all(math.isnan(x) for x in b["atr_wilder"][:3]))
        np.testing.assert_array_equal(b["atr_wilder"][3:], np.ones(len(self.S) - 3))
        np.testing.assert_array_equal(b["atr_sma"][3:], np.ones(len(self.S) - 3))

    def test_two_legs_with_flags_and_close_time_convention(self):
        b = self.bars()
        legs = bm.build_legs(b)
        # r=1.5: L3 (low 11.0) confirmed at i=4 (high 12.5 - 11.0 = 1.5 >= 1.5); H8 (high 14.5) confirmed at i=9 (low 13.0 <= 14.5 - 1.5);
        #   L18 (low 8.5) confirmed at i=19 (high 10.0 >= 8.5 + 1.5). r=2.0 reaches the same pivots one or two bars later.
        # leg1 long bar3 -> bar8: p 11.0 -> 14.5, size 3.5, dur 5.   leg2 short bar8 -> bar18: p 14.5 -> 8.5, size 6.0, dur 10.
        self.assertEqual(len(legs["i0"]), 2)
        self.assertEqual(list(legs["i0"]), [3, 8])
        self.assertEqual(list(legs["i1"]), [8, 18])
        self.assertEqual(list(legs["side"]), [1, -1])
        self.assertEqual(list(legs["p0"]), [11.0, 14.5])
        self.assertEqual(list(legs["p1"]), [14.5, 8.5])
        self.assertEqual(list(legs["size"]), [3.5, 6.0])
        self.assertEqual(list(legs["dur"]), [5, 10])
        self.assertEqual(list(legs["t_start"]), [T0 + 4 * MS5, T0 + 9 * MS5])  # close time of the pivot bar = open + 300000
        self.assertEqual(list(legs["t_end"]), [T0 + 9 * MS5, T0 + 19 * MS5])
        for r in (1.5, 2.0):  # sizes 3.5 and 6.0: k=3 -> both, k=5 -> only leg2, k=8 -> none
            self.assertEqual(list(legs["flags"][(r, 3)]), [1, 1])
            self.assertEqual(list(legs["flags"][(r, 5)]), [0, 1])
            self.assertEqual(list(legs["flags"][(r, 8)]), [0, 0])

    def test_flag_requires_the_leg_to_exist_in_that_r(self):
        # Zero-range path P with ATR 1. Union of r=1.5 and r=2.0 legs:
        # (0,2,long) both; (2,5,short) r1.5 only; (5,7,long) r1.5 only; (7,8,short) r1.5 only; (2,8,short) r2.0 only; (8,10,long) both.
        b = path_bars(P)
        b["atr_wilder"] = np.ones(len(P))
        legs = bm.build_legs(b)
        keys = [(int(a), int(z), int(s)) for a, z, s in zip(legs["i0"], legs["i1"], legs["side"])]
        self.assertEqual(keys, [(0, 2, 1), (2, 5, -1), (2, 8, -1), (5, 7, 1), (7, 8, -1), (8, 10, 1)])
        # sizes: 5, 7, 8, 1.8, 2.8, 10.   k=3: r1.5 -> legs 5,7,10 ; r2.0 -> legs 5,8,10
        self.assertAlmostEqual(list(legs["size"])[3], 1.8)
        self.assertEqual(list(legs["flags"][(1.5, 3)]), [1, 1, 0, 0, 0, 1])
        self.assertEqual(list(legs["flags"][(2.0, 3)]), [1, 0, 1, 0, 0, 1])
        # k=8: r1.5 -> only the 10 (the 7 is below 8); r2.0 -> the 8 (>= is inclusive) and the 10
        self.assertEqual(list(legs["flags"][(1.5, 8)]), [0, 0, 0, 0, 0, 1])
        self.assertEqual(list(legs["flags"][(2.0, 8)]), [0, 0, 1, 0, 0, 1])

    def test_csv_schema_and_roundtrip(self):
        b = self.bars()
        legs = bm.build_legs(b)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "legs_5m.csv"
            bm.write_legs_csv(p, legs)
            raw = p.read_bytes()
            self.assertNotIn(b"\r", raw)
            lines = raw.decode().split("\n")
            self.assertEqual(lines[0], "leg_id,tf,side,t_start_ms,t_end_ms,p_start,p_end,size_atr,atr_at_start,dur_bars,"
                                       "flags_r1.5_k3,flags_r1.5_k5,flags_r1.5_k8,flags_r2.0_k3,flags_r2.0_k5,flags_r2.0_k8")
            self.assertEqual(lines[1], "5m-000001,5m,long,%d,%d,11,14.5,3.500000,1,5,1,0,0,1,0,0" % (T0 + 4 * MS5, T0 + 9 * MS5))
            back = bm.read_legs_csv(p)
            self.assertEqual(list(back["side"]), [1, -1])
            self.assertEqual(list(back["flags"][(1.5, 5)]), [0, 1])
            self.assertEqual(list(back["t_end"]), [T0 + 9 * MS5, T0 + 19 * MS5])

    def test_labels_csv_roundtrip_has_nan_for_incomplete_horizon(self):
        b = self.bars()
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "labels_5m.csv"
            bm.write_labels_csv(p, b, h_list=(2,))
            lab = bm.read_labels_csv(p)
            self.assertEqual(list(lab["t_close_ms"][:2]), [T0 + MS5, T0 + 2 * MS5])
            self.assertTrue(math.isnan(lab["mfe_long_2"][-1]))  # last bar: no bars follow
            self.assertTrue(math.isnan(lab["mfe_long_2"][0]))  # ATR undefined at bar 0
            # bar 3 (atr 1): entry open[4] = 12.0; bars 4..5 have highs 12.5 and 13.0; max 13.0 -> mfe 1.0
            self.assertAlmostEqual(lab["mfe_long_2"][3], 1.0)

    def test_invariants_zero_violations_and_fractal_share(self):
        b = self.bars()
        legs = bm.build_legs(b)
        inv = bm.check_leg_invariants(b, legs)
        self.assertEqual(inv, {"legs": 2, "pivot_not_bar_extreme": 0, "interior_more_extreme_bar": 0, "pivot_bar_engulfs_leg": 0, "size_below_r": 0})
        # +-2 fractal on pivots L3, H8, L18: L3 low 11.0 vs lows of bars 1..2 = 10.0, 10.5 -> not lower -> fail.
        # H8 high 14.5 > bars 6..7 highs 13.5, 14.0 and >= bars 9..10 highs 14.0, 13.5 -> pass.  L18 low 8.5 < bars 16..17 lows 9.5, 9.0 and <= bars 19..20 lows 9.0, 9.5 -> pass.
        fr = bm.fractal_share(b, legs, 1.5)
        self.assertEqual((fr["pivots"], fr["pass"]), (3, 2))

    def test_invariant_check_detects_whipsaw_and_engulfing_bars(self):
        def mk(h, l, p0, p1, side):
            return {"i0": np.array([0]), "i1": np.array([len(h) - 1]), "side": np.array([side]), "p0": np.array([p0]), "p1": np.array([p1]),
                    "size": np.array([5.0]), "r_list": (1.5,), "in_r": {1.5: np.array([True])}}, {"h": np.array(h, dtype=float), "l": np.array(l, dtype=float)}
        # long leg 10 -> 14 over 3 bars; the middle bar trades down to 9 (< 10): a whipsaw bar inside the leg
        legs, b = mk([11, 12, 14], [10, 9, 11], 10.0, 14.0, 1)
        self.assertEqual(bm.check_leg_invariants(b, legs), {"legs": 1, "pivot_not_bar_extreme": 0, "interior_more_extreme_bar": 1,
                                                            "pivot_bar_engulfs_leg": 0, "size_below_r": 0})
        # long leg whose START bar also trades up to 16 (> end pivot 14): the pivot bar spans the whole leg
        legs, b = mk([16, 12, 14], [10, 11, 11], 10.0, 14.0, 1)
        self.assertEqual(bm.check_leg_invariants(b, legs), {"legs": 1, "pivot_not_bar_extreme": 0, "interior_more_extreme_bar": 0,
                                                            "pivot_bar_engulfs_leg": 1, "size_below_r": 0})
        # leg price that is not the bar's low: counted as a pivot error
        legs, b = mk([11, 12, 14], [10.5, 11, 11], 10.0, 14.0, 1)
        self.assertEqual(bm.check_leg_invariants(b, legs)["pivot_not_bar_extreme"], 1)

    def test_stats_tradable_and_travel(self):
        b = self.bars()
        b["atr_sma"] = b["atr_wilder"]
        legs = bm.build_legs(b)
        st = bm.compute_tf_stats(b, legs)
        # k=5, r=1.5: one big leg (6.0, dur 10). Both legs have dur > 3, k=3 has 2 big legs with 2 of them > 3 bars.
        self.assertEqual(st["tradable"]["1.5|3"]["n_big"], 2)
        self.assertEqual(st["tradable"]["1.5|3"]["n_dur_gt3"], 2)
        self.assertEqual(st["tradable"]["1.5|5"]["n_big"], 1)
        self.assertEqual(st["tradable"]["1.5|8"]["n_big"], 0)
        # per-year: both legs start in 2023 (T0 = 2023-11-14)
        self.assertEqual(st["per_year"]["1.5|3"], {"2023": 2})
        # path share for k=5 = |ln(14.5/8.5)| / (|ln(14.5/11)| + |ln(14.5/8.5)|) = 0.53408 / (0.27625 + 0.53408) = 0.6591 (logs by hand)
        self.assertAlmostEqual(st["travel"]["1.5|5"]["legs_path_share"], 0.6591, delta=1e-3)
        # time share k=5 = dur 10 bars of 23
        self.assertAlmostEqual(st["travel"]["1.5|5"]["time_share"], 10 / 23, places=9)

    def test_tradable_counts_on_short_legs(self):
        b = path_bars(P)
        b["atr_wilder"] = np.ones(len(P))
        b["atr_sma"] = np.ones(len(P))
        st = bm.compute_tf_stats(b, bm.build_legs(b))
        # r=1.5, k=3: legs 5 (dur 2), 7 (dur 3), 10 (dur 2): none longer than 3 bars.  r=2.0, k=3: 5 (2), 8 (dur 6), 10 (2): one.
        self.assertEqual((st["tradable"]["1.5|3"]["n_big"], st["tradable"]["1.5|3"]["n_dur_gt3"]), (3, 0))
        self.assertEqual((st["tradable"]["2.0|3"]["n_big"], st["tradable"]["2.0|3"]["n_dur_gt3"]), (3, 1))


def write_kline_csv(path, rows):
    header = "open_time,open,high,low,close,volume,close_time,quote_volume,count,taker_buy_volume,taker_buy_quote_volume,ignore\n"
    with open(path, "w", newline="\n") as fh:
        fh.write(header)
        for t, o, h, l, c, v in rows:
            fh.write("%d,%s,%s,%s,%s,%s,%d,0,0,0,0,0\n" % (t, o, h, l, c, v, t + 59999))


class TestLoadingAndResample(unittest.TestCase):
    def test_merge_first_source_wins_and_reports_conflicts(self):
        with tempfile.TemporaryDirectory() as d:
            a = Path(d) / "A" / "klines"
            b = Path(d) / "B" / "klines"
            a.mkdir(parents=True)
            b.mkdir(parents=True)
            t = T0
            write_kline_csv(a / "BTCUSDT-1m-2023-11.csv", [(t, 1, 2, 0.5, 1.5, 3), (t + 60000, 1.5, 2.5, 1, 2, 4), (t + 120000, 2, 3, 1.5, 2.5, 5)])
            # B repeats minute 1 with a different close (conflict), repeats minute 2 identically, adds minute 3
            write_kline_csv(b / "BTCUSDT-1m-2023-11.csv", [(t + 60000, 1.5, 2.5, 1, 9.9, 4), (t + 120000, 2, 3, 1.5, 2.5, 5), (t + 180000, 3, 4, 2.5, 3.5, 6)])
            bars, rep = bm.load_1m(((Path(d) / "A", "klines"), (Path(d) / "B", "klines")))
            self.assertEqual([x["t"] for x in bars], [t, t + 60000, t + 120000, t + 180000])
            self.assertEqual(bars[1]["c"], 2.0)  # first source kept, not the 9.9 from B
            self.assertEqual((rep[0]["n_new"], rep[1]["n_new"]), (3, 1))
            self.assertEqual((rep[1]["n_duplicate_of_earlier_source"], rep[1]["n_conflicting_duplicates"]), (2, 1))

    def test_resample_5m_ohlc_and_close_time(self):
        # minute m (0..9): o=m, h=m+1, l=m-1, c=m+0.5, v=1.  Bucket 0 = minutes 0..4: o=0 (first), c=4.5 (last), h=5, l=-1, v=5.
        # Bucket 1 = minutes 5..9: o=5, c=9.5, h=10, l=4, v=5.
        bars = [{"t": T0 + m * 60000, "o": float(m), "h": m + 1.0, "l": m - 1.0, "c": m + 0.5, "v": 1.0, "tbv": 0.0} for m in range(10)]
        rb = bm.resample_bars(bars, "5m")
        self.assertEqual(list(rb["t_open"]), [T0, T0 + MS5])
        self.assertEqual(list(rb["t_close"]), [T0 + MS5, T0 + 2 * MS5])
        self.assertEqual((rb["o"][0], rb["h"][0], rb["l"][0], rb["c"][0], rb["v"][0]), (0.0, 5.0, -1.0, 4.5, 5.0))
        self.assertEqual((rb["o"][1], rb["h"][1], rb["l"][1], rb["c"][1], rb["v"][1]), (5.0, 10.0, 4.0, 9.5, 5.0))

    def test_resample_drops_open_trailing_bucket(self):
        bars = [{"t": T0 + m * 60000, "o": 1.0, "h": 1.0, "l": 1.0, "c": 1.0, "v": 1.0, "tbv": 0.0} for m in range(8)]
        self.assertEqual(len(bm.resample_bars(bars, "5m")["t_open"]), 1)  # minutes 5..7 do not fill the second bucket

    def test_coverage_counts_gap_zero_volume_and_bad_ohlc(self):
        def bar(m, v=1.0, h=2.0, l=1.0):
            return {"t": T0 + m * 60000, "o": 1.5, "h": h, "l": l, "c": 1.5, "v": v, "tbv": 0.0}
        bars = [bar(0), bar(1, v=0.0, h=1.5, l=1.5), bar(4), bar(5, h=1.0)]  # minutes 2,3 missing; bar 1 flat zero volume; bar 5 has high < close
        cov = bm.coverage_1m(bars)
        self.assertEqual((cov["n_bars"], cov["n_gaps"], cov["missing_minutes"]), (4, 1, 2))
        self.assertEqual((cov["zero_volume_bars"], cov["zero_volume_flat_ohlc"]), (1, 1))
        self.assertEqual(cov["ohlc_inconsistent"], 1)


if __name__ == "__main__":
    unittest.main()
