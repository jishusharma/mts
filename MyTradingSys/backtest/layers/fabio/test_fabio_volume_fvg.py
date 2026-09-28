import unittest

from MyTradingSys.backtest.layers.fabio.fabio_volume_fvg import (
    build_profile,
    value_area,
    lowest_volume_level,
    random_va_level,
    swing_legs,
)


def B(t, v):
    return {"t": t, "o": v, "c": v, "h": v, "l": v}


# Same fixture as MyTradingSys/backtest/layers/cryptocred/test_cc_structure.py's
# test_s1_use_body_true, re-verified independently here: find_swings(left=1,
# right=1, use_body=True) yields swings at i=1 (high,100), i=3 (low,60),
# i=5 (high,95), i=6 (low,75), confirmed at i+1 in each case.
class TestSwingLegs(unittest.TestCase):
    def test_consecutive_swing_pairs(self):
        vals = [80, 100, 70, 60, 90, 95, 75, 98, 99]
        bars = [B(i, v) for i, v in enumerate(vals)]
        legs = swing_legs(bars, left=1, right=1, use_body=True)
        expected = [
            {"a_i": 1, "b_i": 3, "a_price": 100, "b_price": 60, "confirmed_i": 4},
            {"a_i": 3, "b_i": 5, "a_price": 60, "b_price": 95, "confirmed_i": 6},
            {"a_i": 5, "b_i": 6, "a_price": 95, "b_price": 75, "confirmed_i": 7},
        ]
        self.assertEqual(legs, expected)


# Hand-verified fixture (see 089-fabio-volume-fvg.md packed spec): 3 bars,
# range [100,108], n_bins=4 -> bin_width=2, per-bin volumes [20,30,30,20]
# (arithmetic shown in full in the spec).
def _profile_bars():
    return [
        {"l": 100, "h": 104, "v": 40},
        {"l": 102, "h": 106, "v": 20},
        {"l": 104, "h": 108, "v": 40},
    ]


class TestBuildProfile(unittest.TestCase):
    def test_uniform_overlap_distribution(self):
        p = build_profile(_profile_bars(), 0, 2, n_bins=4)
        self.assertEqual(p["lo"], 100)
        self.assertEqual(p["hi"], 108)
        self.assertEqual(p["bin_width"], 2.0)
        for got, want in zip(p["volumes"], [20.0, 30.0, 30.0, 20.0]):
            self.assertAlmostEqual(got, want)

    def test_bad_range_raises(self):
        with self.assertRaises(ValueError):
            build_profile(_profile_bars(), 2, 0, n_bins=4)


class TestValueArea(unittest.TestCase):
    def test_expands_from_poc_to_70pct(self):
        profile = {"lo": 100, "hi": 108, "n_bins": 4, "bin_width": 2.0,
                   "volumes": [20.0, 30.0, 30.0, 20.0]}
        va = value_area(profile, pct=0.70)
        # poc = idx1 (first of the 30/30 tie); expand to idx2 (30>20) -> covered 60;
        # then idx0 vs idx3 tie (20 vs 20) -> prefer lower price -> add idx0 -> 80 >= 70.
        self.assertEqual(va, (0, 2))

    def test_bad_total_raises(self):
        with self.assertRaises(ValueError):
            value_area({"volumes": [0, 0, 0]}, pct=0.7)


class TestLowestVolumeLevel(unittest.TestCase):
    def test_lowest_bin_in_value_area(self):
        profile = {"lo": 100, "hi": 108, "n_bins": 4, "bin_width": 2.0,
                   "volumes": [20.0, 30.0, 30.0, 20.0]}
        level = lowest_volume_level(profile, (0, 2))
        self.assertEqual(level["bin_index"], 0)
        self.assertEqual(level["price_lo"], 100.0)
        self.assertEqual(level["price_hi"], 102.0)
        self.assertEqual(level["volume"], 20.0)


class TestRandomVaLevel(unittest.TestCase):
    def test_deterministic_with_seed(self):
        # random.Random(42).randrange(0, 3) == 2 (verified directly with the
        # stdlib random module).
        profile = {"lo": 100, "hi": 108, "n_bins": 4, "bin_width": 2.0,
                   "volumes": [20.0, 30.0, 30.0, 20.0]}
        level = random_va_level(profile, (0, 2), seed=42)
        self.assertEqual(level["bin_index"], 2)
        self.assertEqual(level["price_lo"], 104.0)
        self.assertEqual(level["price_hi"], 106.0)
        self.assertEqual(level["volume"], 30.0)


if __name__ == "__main__":
    unittest.main()
