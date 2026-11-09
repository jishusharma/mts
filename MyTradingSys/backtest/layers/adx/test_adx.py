"""test_adx.py - expected numbers are the hand values of FORMULAS.md section 30 (n = 3, 20-bar toy), not read from the code."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from adx import adx_di, crosses  # noqa: E402

H = [10, 11, 12, 11, 13, 14, 13, 12, 11, 12, 13, 15, 14, 13, 12, 11, 12, 14, 15, 14]
L = [8, 9, 10, 9, 10, 12, 11, 10, 9, 10, 11, 12, 12, 11, 10, 9, 10, 11, 13, 12]
C = [9, 10, 11, 10, 12, 13, 12, 11, 10, 11, 12, 14, 13, 12, 11, 10, 11, 13, 14, 13]


class TestAdx(unittest.TestCase):
    def test_toy_hand_values(self):
        p, m, a = adx_di(H, L, C, 3)
        self.assertTrue(all(v is None for v in p[:3]) and all(v is None for v in a[:5]))
        self.assertAlmostEqual(p[3], 100 / 3, places=6)       # sTR 6, sDM+ 2
        self.assertAlmostEqual(m[3], 50 / 3, places=6)        # sDM- 1
        self.assertAlmostEqual(p[4], 1000 / 21, places=6)     # sTR 7, sDM+ 10/3
        self.assertAlmostEqual(m[4], 200 / 21, places=6)
        self.assertAlmostEqual(p[5], 145 / 3, places=6)
        self.assertAlmostEqual(m[5], 20 / 3, places=6)
        self.assertAlmostEqual(a[5], 5800 / 99, places=6)     # mean(DX 100/3, 200/3, 2500/33)
        self.assertAlmostEqual(a[6], 435500 / 9207, places=6)
        self.assertAlmostEqual(a[19], 67730859096663278979970580785859463248355425686862073919501532 /
                               1938573918298943572482878986601900641205561397631935169214145, places=6)

    def test_short_input(self):
        p, m, a = adx_di([1, 2], [0, 1], [1, 2], 3)
        self.assertEqual(p, [None, None])

    def test_crosses_synthetic(self):
        dip = [None, 10, 12, 8, 7, 9]
        dim = [None, 12, 10, 9, 8, 7]
        self.assertEqual(crosses(dip, dim), [(2, "green"), (3, "red"), (5, "green")])


if __name__ == "__main__":
    unittest.main()