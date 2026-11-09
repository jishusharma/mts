"""test_vfi.py - expected numbers are the hand values of FORMULAS.md section 32.2 (stdev_len 2, length 3, smooth 2, 9-bar toy), not read from the code."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vfi import vfi  # noqa: E402

C = [100, 102, 101, 105, 105, 104, 110, 108, 108.25]
H = [c + 1 for c in C]
L = [c - 1 for c in C]
V = [10, 20, 30, 20, 40, 10, 100, 30, 50]
K = dict(length=3, stdev_len=2, smooth=2)
# hand: bar 3 +20, 4 zero (tie), 5 -10, 6 +175/3 (capped from 100), 7 -30, 8 +50 (population-stdev cutoff 0.2237 < mf 0.25)
HAND_RAW = {5: 1.0 / 3.0, 6: 29.0 / 14.0, 7: 11.0 / 30.0, 8: 47.0 / 28.0}
HAND_SMA = {6: 101.0 / 84.0, 7: 128.0 / 105.0, 8: 859.0 / 840.0}
HAND_EMA = {6: 101.0 / 84.0, 7: 271.0 / 420.0, 8: 1681.0 / 1260.0}


class TestVfi(unittest.TestCase):
    def test_raw(self):
        raw, _ = vfi(H, L, C, V, **K)
        self.assertEqual(len(raw), 9)
        for i in range(5):
            self.assertIsNone(raw[i], i)
        for i, v in HAND_RAW.items():
            self.assertAlmostEqual(raw[i], v, places=9, msg=str(i))

    def test_smoothed_sma(self):
        _, sm = vfi(H, L, C, V, **K)
        for i in range(6):
            self.assertIsNone(sm[i], i)
        for i, v in HAND_SMA.items():
            self.assertAlmostEqual(sm[i], v, places=9, msg=str(i))

    def test_smoothed_ema(self):
        _, sm = vfi(H, L, C, V, smooth_kind="ema", **K)
        for i in range(6):
            self.assertIsNone(sm[i], i)
        for i, v in HAND_EMA.items():
            self.assertAlmostEqual(sm[i], v, places=9, msg=str(i))

    def test_no_smoothing_returns_raw(self):
        raw, sm = vfi(H, L, C, V, length=3, stdev_len=2, smooth=1)
        self.assertEqual(raw, sm)

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            vfi([1], [1, 2], [1], [1])
        with self.assertRaises(ValueError):
            vfi([1, 2], [1, 2], [1, 2], [1, 2], smooth_kind="wma")


if __name__ == "__main__":
    unittest.main()
