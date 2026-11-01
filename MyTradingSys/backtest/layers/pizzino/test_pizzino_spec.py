"""Spec-derived boundary tests for the Pizzino indicators (mutation-kill audit,
card gpt-mutation-pizzino-indicators-1031).

Every expected value is hand-computed from the rule text of
MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md (FORMULAS.md has no Pizzino
section), never from pizzino_indicators.py. Each test names the hand mutant it kills
(MNN ids in the audit report MyTradingSys/research/layer_lab/reports/
2026-11-01_gpt-mutation-pizzino-indicators-1031.md). The bars are made up (OURS);
tol = 0.25 and level 100 are picked so the band edges 125 and 75 are exact floats.
"""
import unittest

from MyTradingSys.backtest.layers.pizzino import pizzino_indicators as pz


class TestPivotSpec(unittest.TestCase):
    def test_equal_lows_are_not_strict_pivot_lows(self):
        # SPEC s1 (SPEC.md:15): pivot low needs low[i] < low[j], strict both sides.
        # lows 1, 1 at bars 1, 2: 1 < 1 is false for both -> no pivot low. Kills M02.
        h = [10, 9, 9, 10, 11]
        lo = [5, 1, 1, 5, 6]
        self.assertEqual([p.index for p in pz.find_pivots(h, lo, 1) if p.kind == "L"], [])

    def test_two_lows_keep_lower(self):
        # SPEC s1 (SPEC.md:15): "two lows in a row keep the lower one".
        # n = 1: bar 1 low 2 (< 5, < 3) and bar 3 low 1 (< 3, < 4) are pivot lows; highs
        # 10, 7, 8, 9, 10 have no pivot high between them -> keep bar 3 (1). Kills M04.
        h = [10, 7, 8, 9, 10]
        lo = [5, 2, 3, 1, 4]
        ls = [(p.index, p.price) for p in pz.find_pivots(h, lo, 1) if p.kind == "L"]
        self.assertEqual(ls, [(3, 1)])


class TestStateSpec(unittest.TestCase):
    def test_down_close_equal_to_last_ph_is_neutral(self):
        # SPEC s2 (SPEC.md:40): down needs c < PH[-1]. PH 14, 12; PL 9, 7; close 12:
        # 12 < 12 false -> not down; up needs 12 > 14 false -> neutral. Kills M05.
        self.assertEqual(pz.swing_state([14, 12], [9, 7], 12), (0, None))

    def test_up_close_equal_to_last_pl_is_neutral(self):
        # SPEC s2 (SPEC.md:39): up needs c > PL[-1]. PH 12, 14; PL 8, 10; close 10:
        # 10 > 10 false -> not up; down needs 14 < 12 false -> neutral. Kills M06.
        self.assertEqual(pz.swing_state([12, 14], [8, 10], 10), (0, None))


class TestLeadFlagSpec(unittest.TestCase):
    Z = [0, 0, 0, 0, 0, 0]

    def test_lead_down_mirror(self):
        # SPEC s2 (SPEC.md:43-45): lead_up / lead_down mirror. state1 turns down at
        # bar 2, states 2 and 3 not down at i = 5, L = 5: 5 - 2 = 3 bars ago -> -1. Kills M07.
        self.assertEqual(pz.lead_flag([0, 0, -1, -1, -1, -1], self.Z, self.Z, 5, 5), -1)

    def test_lead_window_last_L_bars(self):
        # SPEC s2 (SPEC.md:43): "became up within the last L bars". The last L bars at
        # i = 5 are bars i-L+1..i (reading: OURS). Turn at bar 2: L = 4 covers bars 2..5
        # -> +1; L = 3 covers bars 3..5 -> bar 2 is outside -> 0. Kills M08.
        s1 = [0, 0, 1, 1, 1, 1]
        self.assertEqual(pz.lead_flag(s1, self.Z, self.Z, 4, 5), 1)
        self.assertEqual(pz.lead_flag(s1, self.Z, self.Z, 3, 5), 0)

    def test_no_observed_turn_no_lead(self):
        # SPEC s2 (SPEC.md:43): "became up" needs a turn. state1 is up from bar 0, so no
        # turn is observed inside the data -> 0. Kills M09.
        self.assertEqual(pz.lead_flag([1, 1, 1], [0, 0, 0], [0, 0, 0], 5, 2), 0)


class TestCountSpec(unittest.TestCase):
    def test_significance_window_is_W_bars(self):
        # SPEC s3 (SPEC.md:65): lowest low "of the previous W bars before the pivot bar".
        # Pivot bar 20, W = 5: previous 5 bars are 15..19. Low 7.5 at bar 15 < 8 -> not
        # significant. Kills M10. Low 7.5 at bar 14 is outside -> significant.
        lows = [9.0] * 30
        lows[20] = 8
        lows[15] = 7.5
        self.assertFalse(pz.is_significant(lows, 20, "L", 5))
        lows[15], lows[14] = 9.0, 7.5
        self.assertTrue(pz.is_significant(lows, 20, "L", 5))

    def test_down_count_needs_strict_lower_low(self):
        # SPEC s3 (SPEC.md:63): down-count mirrors HH+HL: lower high AND lower low.
        # After pivot high at bar 0: bar 1 (19 < 20, 17 < 18) -> -1; bar 2 low 17 < 17
        # false -> stop, value kept -> [0, -1, -1, -1]. Kills M11.
        h = [20, 19, 18, 17]
        lo = [18, 17, 17, 15]
        self.assertEqual(pz.bar_count_from(h, lo, 0, "H"), [0, -1, -1, -1])


class TestHalfSpec(unittest.TestCase):
    MID = 92000  # SPEC example 4b: (100,000 + 84,000) / 2

    def test_hold_above_touch_at_mid(self):
        # SPEC s4 (SPEC.md:81): hold_above = low <= mid and close > mid.
        # L 92,000 <= 92,000 and C 92,800 > 92,000 -> True. Kills M12.
        self.assertTrue(pz.half_events(93000, 92000, 92800, 92700, self.MID)["hold_above"])

    def test_hold_below_touch_at_mid(self):
        # SPEC s4 (SPEC.md:81): hold_below = high >= mid and close < mid.
        # H 92,000 >= 92,000 and C 91,000 < 92,000 -> True. Kills M13.
        self.assertTrue(pz.half_events(92000, 90000, 91000, 90500, self.MID)["hold_below"])

    def test_reject_needs_previous_close_below(self):
        # SPEC s4 (SPEC.md:82): reject_from_below = hold_below while previous close < mid.
        # H 92,500, L 90,000, C 91,000 -> hold_below; previous close 92,300 > 92,000 ->
        # reject_from_below False. Kills M14.
        e = pz.half_events(92500, 90000, 91000, 92300, self.MID)
        self.assertTrue(e["hold_below"])
        self.assertFalse(e["reject_from_below"])


class TestBreakRetestSpec(unittest.TestCase):
    def test_break_needs_a_close_below_first(self):
        # SPEC s5 (SPEC.md:92): break confirmed when N closes are above X, "the first of
        # them closed above after being below". X = 63,000, N = 2. Bars 0-2 are above
        # with no close below before them -> no break there; bar 3 closes 62,900 (below);
        # bars 4, 5 close above -> break confirmed at bar 5. Kills M15.
        closes = [63400, 63800, 63900, 62900, 63200, 63500]
        r = pz.break_retest(63000, closes, [64000] * 6, [62800] * 6, 2, 0.005, 20)
        self.assertEqual(r["break_confirmed_at"], 5)

    def test_retest_on_the_Rth_bar_counts(self):
        # SPEC s5 (SPEC.md:92): retest = first later bar "within R bars". Break at bar 2,
        # R = 2 -> bars 3 and 4 (bar 2 + 2 is within; reading: OURS). Bar 3 low 63,600 >
        # 63,315 (band edge, SPEC.md:98); bar 4 low 63,200 <= 63,315 -> retest at 4,
        # close 63,900 > 63,000 -> hold. Kills M16.
        closes = [62800, 63400, 63800, 64000, 63900]
        lows = [62500, 63100, 63500, 63600, 63200]
        r = pz.break_retest(63000, closes, [65000] * 5, lows, 2, 0.005, 2)
        self.assertEqual((r["break_confirmed_at"], r["retest_bar"], r["outcome"]), (2, 4, "hold"))

    def test_up_retest_touch_at_band_edge(self):
        # SPEC s5 (SPEC.md:92): retest if low <= X * (1 + tol). X = 100, tol = 0.25 ->
        # edge 125. Closes 99, 101, 102 -> break at bar 2; bar 3 low 125 <= 125 -> retest,
        # close 130 > 100 -> hold. Kills M17.
        r = pz.break_retest(100, [99, 101, 102, 130], [140] * 4, [98, 100, 101, 125], 2, 0.25, 20)
        self.assertEqual((r["break_confirmed_at"], r["retest_bar"], r["outcome"]), (2, 3, "hold"))

    def test_down_retest_touch_at_band_edge(self):
        # SPEC s5 (SPEC.md:92): down retest if high >= X * (1 - tol). X = 100, tol = 0.25 ->
        # edge 75. Closes 101, 99, 98 -> down-break at bar 2; bar 3 high 75 >= 75 ->
        # retest, close 70 < 100 -> hold. Kills M18.
        r = pz.break_retest(100, [101, 99, 98, 70], [102, 100, 99, 75], [60] * 4, 2, 0.25, 20,
                            direction="down")
        self.assertEqual((r["break_confirmed_at"], r["retest_bar"], r["outcome"]), (2, 3, "hold"))


if __name__ == "__main__":
    unittest.main()
