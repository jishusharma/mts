"""Tests for the Pizzino indicator module. Expected numbers are the hand-computed
worked examples 1-6 in MyTradingSys/research/pizzino_layer_2026-10-27/SPEC.md,
never taken from the code."""
import unittest

from MyTradingSys.backtest.layers.pizzino import pizzino_indicators as pz

# SPEC example 1
H1 = [10, 12, 14, 13, 12, 11, 12, 14, 16, 15, 14]
L1 = [8, 9, 11, 10, 9, 7, 8, 10, 12, 11, 10]
C1 = [9, 11, 13, 11, 10, 8, 11, 13, 15, 12, 13]


def tup(ps):
    return [(p.index, p.price, p.confirmed_at) for p in ps]


class TestPivots(unittest.TestCase):
    def test_example1_n2(self):
        self.assertEqual(tup(pz.find_pivots(H1, L1, 2)), [(2, 14, 4), (5, 7, 7), (8, 16, 10)])

    def test_example1_n1_same_three(self):
        self.assertEqual(tup(pz.find_pivots(H1, L1, 1)), [(2, 14, 3), (5, 7, 6), (8, 16, 9)])

    def test_kinds_alternate(self):
        self.assertEqual([p.kind for p in pz.find_pivots(H1, L1, 2)], ["H", "L", "H"])

    def test_strict_both_sides(self):
        # equal highs at bars 1 and 2: neither is a strict pivot high
        ps = pz.find_pivots([1, 5, 5, 1, 0], [0, 4, 4, 0, -1], 1)
        self.assertEqual([p.index for p in ps if p.kind == "H"], [])

    def test_two_highs_keep_higher(self):
        # highs at bars 1 (5) and 3 (7), lows never form a pivot between them: keep 7
        h = [1, 5, 4, 7, 2]
        lo = [0, 3, 3.5, 4, 1]
        hs = [p for p in pz.find_pivots(h, lo, 1) if p.kind == "H"]
        self.assertEqual([(p.index, p.price) for p in hs], [(3, 7)])

    def test_causal_view(self):
        known = pz.pivots_known(H1, L1, 1, 3)
        self.assertEqual(tup(known), [(2, 14, 3)])
        # truncating the series gives the same answer: no look-ahead
        self.assertEqual(tup(pz.pivots_known(H1[:4], L1[:4], 1, 3)), tup(known))


class TestStates(unittest.TestCase):
    # SPEC example 2
    def test_up(self):
        self.assertEqual(pz.swing_state([12, 14], [8, 10], 13), (1, 10))
        self.assertEqual(pz.swing_state([14, 16], [7, 10], 13), (1, 10))

    def test_degree3_neutral(self):
        self.assertEqual(pz.swing_state([20, 16], [5, 10], 13)[0], 0)

    def test_conf_plus2_mixed(self):
        args = (([12, 14], [8, 10], 13), ([14, 16], [7, 10], 13), ([20, 16], [5, 10], 13))
        self.assertEqual(pz.nested_conf([pz.swing_state(*a)[0] for a in args]), 2)

    def test_close_below_swing_low_neutral(self):
        self.assertEqual(pz.swing_state([12, 14], [8, 10], 9.5)[0], 0)
        self.assertEqual(pz.nested_conf([0, 0, 0]), 0)

    def test_down_and_break_above(self):
        self.assertEqual(pz.swing_state([14, 12], [9, 7], 11.5), (-1, 12))
        self.assertEqual(pz.swing_state([14, 12], [9, 7], 12.5)[0], 0)

    def test_too_few_pivots_neutral(self):
        self.assertEqual(pz.swing_state([14], [9, 7], 11.5)[0], 0)

    def test_confluence_sum(self):
        self.assertEqual(pz.nested_conf([-1, -1, -1]), -3)

    def test_lead_flag(self):
        s1 = [0, 0, 1, 1, 1, 1]
        s2 = [0, 0, 0, 0, 0, 0]
        s3 = [0, 0, 0, 0, 0, 0]
        self.assertTrue(pz.lead_flag(s1, s2, s3, 5, 5))
        s2b = [0, 0, 0, 0, 0, 1]
        self.assertFalse(pz.lead_flag(s1, s2b, s3, 5, 5))
        # state1 turned up 5 bars before i=5 with L=3: too old
        self.assertFalse(pz.lead_flag([0, 1, 1, 1, 1, 1], s2, s3, 3, 5))


class TestBarCount(unittest.TestCase):
    # SPEC example 3: T (pivot low) at bar 0
    H = [10, 11, 12, 13, 12.5]
    L = [8, 9, 10, 10.5, 11]

    def test_three_bar(self):
        self.assertEqual(pz.bar_count_from(self.H, self.L, 0, "L"), [0, 1, 2, 3, 3])

    def test_failure_case(self):
        h = [10, 11, 12, 13, 14]
        lo = [8, 9, 9, 10.5, 11]
        self.assertEqual(pz.bar_count_from(h, lo, 0, "L"), [0, 1, 1, 1, 1])

    def test_down_mirror(self):
        h = [20, 19, 18, 17]
        lo = [18, 17, 16, 15]
        self.assertEqual(pz.bar_count_from(h, lo, 0, "H"), [0, -1, -2, -3])

    def test_significance(self):
        lows = [9.0] * 30
        lows[10] = 7.5
        lows[20] = 8
        self.assertFalse(pz.is_significant(lows, 20, "L", 50))
        self.assertTrue(pz.is_significant(lows, 20, "L", 5))
        self.assertTrue(pz.is_significant([9, 9, 8, 9, 10], 2, "L", 50))
        self.assertTrue(pz.is_significant([1, 1, 12, 1], 2, "H", 50))
        self.assertFalse(pz.is_significant([1, 13, 12, 1], 2, "H", 50))


class TestMid(unittest.TestCase):
    def test_example4a(self):
        mid = pz.mid_line(16, 7)
        self.assertEqual(mid, 11.5)
        self.assertEqual(pz.half_state(13, mid, None), "strong")
        self.assertEqual(pz.half_state(10, mid, "strong"), "weak")
        self.assertEqual(pz.half_state(11.5, mid, "weak"), "weak")

    def test_example4b(self):
        mid = pz.mid_line(100000, 84000)
        self.assertEqual(mid, 92000)
        e = pz.half_events(92500, 90000, 91000, 90500, mid)
        self.assertTrue(e["hold_below"] and e["reject_from_below"])
        self.assertFalse(e["hold_above"])
        e = pz.half_events(93000, 91500, 92800, 92700, mid)
        self.assertTrue(e["hold_above"])
        self.assertFalse(e["hold_below"] or e["reject_from_below"])


class TestBreakRetest(unittest.TestCase):
    # SPEC example 5
    def test_break_hold(self):
        closes = [62800, 63400, 63800, 63900]
        highs = [63000, 63900, 64000, 64000]
        lows = [62500, 63100, 63500, 63200]
        r = pz.break_retest(63000, closes, highs, lows, N=2, tol=0.005, R=20)
        self.assertEqual((r["break_confirmed_at"], r["retest_bar"], r["outcome"]), (2, 3, "hold"))

    def test_fail(self):
        closes = [62800, 63400, 63800, 62900]
        lows = [62500, 63100, 63500, 63200]
        r = pz.break_retest(63000, closes, [64000] * 4, lows, 2, 0.005, 20)
        self.assertEqual((r["retest_bar"], r["outcome"]), (3, "fail"))

    def test_no_touch(self):
        closes = [62800, 63400, 63800, 63900]
        lows = [62500, 63100, 63500, 63500]
        r = pz.break_retest(63000, closes, [64000] * 4, lows, 2, 0.005, 20)
        self.assertEqual(r["break_confirmed_at"], 2)
        self.assertIsNone(r["retest_bar"])
        self.assertIsNone(r["outcome"])

    def test_no_break_when_one_close(self):
        r = pz.break_retest(63000, [62800, 63400, 62900], [64000] * 3, [62000] * 3, 2, 0.005, 20)
        self.assertIsNone(r["break_confirmed_at"])

    def test_retest_window(self):
        closes = [62800, 63400, 63800, 64000, 64100, 63900]
        lows = [62500, 63100, 63500, 63600, 63700, 63200]
        r = pz.break_retest(63000, closes, [65000] * 6, lows, 2, 0.005, 2)
        self.assertIsNone(r["retest_bar"])

    def test_down_mirror(self):
        closes = [63200, 62600, 62400, 62300]
        highs = [63500, 62800, 62500, 62800]
        r = pz.break_retest(63000, closes, highs, [62000] * 4, 2, 0.005, 20, direction="down")
        # band edge 63000 * 0.995 = 62685; bar 3 high 62800 >= 62685, close 62300 < 63000
        self.assertEqual((r["break_confirmed_at"], r["retest_bar"], r["outcome"]), (2, 3, "hold"))


class TestPlan(unittest.TestCase):
    # SPEC example 6
    def test_take_with_pivot_target(self):
        p = pz.plan_trade("long", 63950, 62500, [66000], rr_min=1.0)
        self.assertEqual((p["risk"], p["reward"], p["target"], p["take"]), (1450, 2050, 66000, True))
        self.assertAlmostEqual(p["rr"], 1.4138, places=4)

    def test_fallback_2r(self):
        p = pz.plan_trade("long", 63950, 62500, [], rr_min=1.0)
        self.assertEqual((p["target"], p["take"]), (66850, True))

    def test_skip_low_rr(self):
        p = pz.plan_trade("long", 63950, 62500, [64500, 66000], rr_min=1.0)
        self.assertEqual((p["target"], p["reward"], p["take"]), (64500, 550, False))
        self.assertAlmostEqual(p["rr"], 0.3793, places=4)

    def test_short_mirror(self):
        p = pz.plan_trade("short", 100, 110, [90, 80], rr_min=1.0)
        self.assertEqual((p["risk"], p["target"], p["reward"], p["take"]), (10, 90, 10, True))
        p = pz.plan_trade("short", 100, 110, [], rr_min=1.0)
        self.assertEqual(p["target"], 80)

    def test_target_ignores_wrong_side(self):
        p = pz.plan_trade("long", 100, 95, [90, 120, 110])
        self.assertEqual(p["target"], 110)

    def test_bad_stop_not_taken(self):
        p = pz.plan_trade("long", 100, 100, [120])
        self.assertFalse(p["take"])


if __name__ == "__main__":
    unittest.main()
