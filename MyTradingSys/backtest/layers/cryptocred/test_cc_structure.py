import unittest

from MyTradingSys.backtest.layers.cryptocred.cc_structure import find_swings, is_range_extreme, classify_msb


def B(t, v):
    return {"t": t, "o": v, "c": v, "h": v, "l": v}


def BHL(t, h, l):
    o = c = (h + l) / 2.0
    return {"t": t, "o": o, "c": c, "h": h, "l": l}


class TestFindSwings(unittest.TestCase):
    def test_s1_use_body_true(self):
        vals = [80, 100, 70, 60, 90, 95, 75, 98, 99]
        bars = [B(i, v) for i, v in enumerate(vals)]
        got = find_swings(bars, left=1, right=1, use_body=True)
        expected = [
            {"i": 1, "t": 1, "price": 100, "kind": "high", "confirmed_i": 2},
            {"i": 3, "t": 3, "price": 60, "kind": "low", "confirmed_i": 4},
            {"i": 5, "t": 5, "price": 95, "kind": "high", "confirmed_i": 6},
            {"i": 6, "t": 6, "price": 75, "kind": "low", "confirmed_i": 7},
        ]
        self.assertEqual(got, expected)

    def test_s2_use_body_false(self):
        bars = [
            BHL(0, 11, 9),
            BHL(1, 14, 7),
            BHL(2, 10, 6),
            BHL(3, 16, 5),
            BHL(4, 9, 3),
        ]
        got = find_swings(bars, left=1, right=1, use_body=False)
        expected = [
            {"i": 1, "t": 1, "price": 14, "kind": "high", "confirmed_i": 2},
            {"i": 3, "t": 3, "price": 16, "kind": "high", "confirmed_i": 4},
        ]
        self.assertEqual(got, expected)

    def test_s3_bad_params_raise(self):
        bars = [B(0, 1), B(1, 2), B(2, 3)]
        with self.assertRaises(ValueError):
            find_swings(bars, left=0, right=1)


class TestIsRangeExtreme(unittest.TestCase):
    def test_s4_too_few_lookback_bars(self):
        bars = [BHL(0, 10, 8), BHL(1, 12, 9)]
        self.assertFalse(is_range_extreme(bars, i=1, lookback=3, extreme_pct=0.25))

    def test_s5_true_at_top_and_bottom(self):
        bars = [
            BHL(0, 10, 8),
            BHL(1, 12, 9),
            {"t": 2, "o": 8.0, "c": 8.0, "h": 11, "l": 7},
            {"t": 3, "o": 11.8, "c": 11.8, "h": 12, "l": 11},
            {"t": 4, "o": 8.2, "c": 8.2, "h": 8.5, "l": 8},
        ]
        self.assertTrue(is_range_extreme(bars, i=3, lookback=3, extreme_pct=0.25))
        self.assertTrue(is_range_extreme(bars, i=4, lookback=3, extreme_pct=0.25))


class TestClassifyMsb(unittest.TestCase):
    def test_s6_bull_msb_default_prior_sequence(self):
        vals = [80, 100, 70, 60, 90, 95, 75, 98, 99]
        bars = [B(i, v) for i, v in enumerate(vals)]
        swings = find_swings(bars, left=1, right=1, use_body=True)
        got = classify_msb(bars, swings)
        expected = [{
            "t": 7, "i": 7, "direction": "bull", "broken_level": 95,
            "broken_swing_i": 5, "confirm_i": 7, "at_range_extreme": True,
        }]
        self.assertEqual(got, expected)

    def test_s7_require_prior_sequence_false(self):
        vals = [70, 80, 65, 90, 60, 95]
        bars = [B(i, v) for i, v in enumerate(vals)]
        swings = [
            {"i": 1, "price": 80, "kind": "high", "confirmed_i": 2, "t": 1},
            {"i": 2, "price": 65, "kind": "low", "confirmed_i": 3, "t": 2},
            {"i": 3, "price": 90, "kind": "high", "confirmed_i": 4, "t": 3},
            {"i": 4, "price": 60, "kind": "low", "confirmed_i": 5, "t": 4},
        ]
        got_true = classify_msb(bars, swings, require_prior_sequence=True)
        self.assertEqual(got_true, [])

        got_false = classify_msb(bars, swings, require_prior_sequence=False)
        expected_false = [{
            "t": 5, "i": 5, "direction": "bull", "broken_level": 90,
            "broken_swing_i": 3, "confirm_i": 5, "at_range_extreme": True,
        }]
        self.assertEqual(got_false, expected_false)


if __name__ == "__main__":
    unittest.main()
