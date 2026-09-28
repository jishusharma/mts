import unittest

from MyTradingSys.backtest.layers.cryptocred.cc_retest import find_retest, classify_retest_timing


def bar(t, l, c, h=None, o=None):
    if h is None:
        h = max(l, c) + 1
    if o is None:
        o = c
    return {"t": t, "o": o, "c": c, "h": h, "l": l}


# Neutral filler bar used for indices 0..2 (before confirm_i's touch/invalidate window is
# meaningfully exercised) so it never touches or invalidates a broken_level=100 bull level.
FILLER_BULL = bar(0, l=110, c=107)
# Neutral filler for bear scenarios (broken_level=50), never touches or invalidates.
FILLER_BEAR = bar(0, l=40, h=42, c=41)


class TestFindRetestBull(unittest.TestCase):
    def setUp(self):
        self.msb = {"direction": "bull", "broken_level": 100, "confirm_i": 2}

    def test_r1_immediate_touch(self):
        bars = [
            dict(FILLER_BULL, t=0), dict(FILLER_BULL, t=1), dict(FILLER_BULL, t=2),
            bar(3, l=105, c=106),
            bar(4, l=100.05, c=101),
            bar(5, l=110, c=108),
        ]
        got = find_retest(bars, self.msb, tolerance_pct=0.001, invalidate_pct=0.005, expiry_bars=5)
        self.assertEqual(got, {"t": 4, "i": 4, "level": 100, "bars_since_break": 2})

        self.assertEqual(classify_retest_timing(got, immediate_bars=5), "immediate")
        self.assertEqual(classify_retest_timing(got, immediate_bars=1), "rounded")

    def test_r2_invalidated_before_touch(self):
        bars = [
            dict(FILLER_BULL, t=0), dict(FILLER_BULL, t=1), dict(FILLER_BULL, t=2),
            bar(3, l=105, c=99),
            bar(4, l=100.05, c=101),
        ]
        got = find_retest(bars, self.msb, tolerance_pct=0.001, invalidate_pct=0.005, expiry_bars=5)
        self.assertIsNone(got)

    def test_r3_expires_no_touch_no_invalidate(self):
        bars = [
            dict(FILLER_BULL, t=0), dict(FILLER_BULL, t=1), dict(FILLER_BULL, t=2),
            bar(3, l=110, c=105),
            bar(4, l=110, c=105),
            bar(5, l=110, c=105),
            bar(6, l=110, c=105),
            bar(7, l=110, c=105),
        ]
        got = find_retest(bars, self.msb, tolerance_pct=0.001, invalidate_pct=0.005, expiry_bars=5)
        self.assertIsNone(got)


class TestFindRetestBear(unittest.TestCase):
    def test_r4_bear_retest_found(self):
        msb = {"direction": "bear", "broken_level": 50, "confirm_i": 2}
        bars = [
            dict(FILLER_BEAR, t=0), dict(FILLER_BEAR, t=1), dict(FILLER_BEAR, t=2),
            bar(3, l=47, h=48, c=49),
            bar(4, l=49, h=49.97, c=49.5),
        ]
        got = find_retest(bars, msb, tolerance_pct=0.001, invalidate_pct=0.005, expiry_bars=5)
        self.assertEqual(got, {"t": 4, "i": 4, "level": 50, "bars_since_break": 2})


class TestInvalidParams(unittest.TestCase):
    def test_r5_find_retest_bad_tolerance(self):
        with self.assertRaises(ValueError):
            find_retest([], {"direction": "bull", "broken_level": 100, "confirm_i": 0}, tolerance_pct=0)

    def test_r5_classify_retest_timing_bad_immediate_bars(self):
        with self.assertRaises(ValueError):
            classify_retest_timing({"bars_since_break": 1}, immediate_bars=0)


if __name__ == "__main__":
    unittest.main()
