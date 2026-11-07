"""test_squeeze.py - expected numbers are the hand values of FORMULAS.md section 31 (all lengths 5, 25-bar toy), not read from the code."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from squeeze import squeeze_momentum  # noqa: E402

H = [10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.5, 19.75, 19.75, 19.75, 19.75, 19.75, 19.75, 19.75,
     19.75, 21.5, 23.5, 25.5, 26.5, 28.5, 30.5, 31.5]
L = [9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5, 18.5, 19.25, 19.25, 19.25, 19.25, 19.25, 19.25, 19.25,
     19.25, 19.5, 21.5, 23.5, 25.5, 26.5, 28.5, 29.5]
C = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 19.5, 19.5, 19.5, 19.5, 19.5, 19.5, 19.5, 19.5, 21, 23, 25, 26, 28, 30, 31]
# the section 31.2 hand toy is the textbook BB half-width 2.0*sd (OURS flag); the script default is covered below
K = dict(bb_len=5, kc_len=5, mom_len=5, textbook_bb=True)
# hand flags: 4-11 OFF, 12-17 ON, 18 tie (neither), 19-24 OFF
HAND_MOM = {8: 2.0, 9: 2.0, 10: 1.8425, 11: 1.3775, 12: 0.785, 13: 0.225, 14: -0.125, 15: -0.18, 16: -0.1275,
            17: -0.0475, 18: 0.5475, 19: 1.6025, 20: 2.815, 21: 3.485, 22: 3.885, 23: 3.97, 24: 3.6075}


class TestSqueeze(unittest.TestCase):
    def test_flags(self):
        on, off, _ = squeeze_momentum(H, L, C, **K)
        for i in range(4):
            self.assertIsNone(on[i])
            self.assertIsNone(off[i])
        for i in range(4, 12):
            self.assertEqual((on[i], off[i]), (False, True), i)
        for i in range(12, 18):
            self.assertEqual((on[i], off[i]), (True, False), i)
        self.assertEqual((on[18], off[18]), (False, False))      # BB half-width 1.2 == KC half-width 1.2: neither
        for i in range(19, 25):
            self.assertEqual((on[i], off[i]), (False, True), i)

    def test_momentum(self):
        _, _, m = squeeze_momentum(H, L, C, **K)
        for i in range(8):
            self.assertIsNone(m[i])
        for i, v in HAND_MOM.items():
            self.assertAlmostEqual(m[i], v, places=9, msg=str(i))

    def test_script_quirk_vs_textbook(self):
        # closes 0..19 step 1: sd = sqrt(399/12) = 5.7663; H = C+3.15, L = C-3.15 so every TR = 6.3 (ATR 6.3).
        # script (BBhw = kc_mult*sd): 1.5*5.7663 = 8.649 < KChw 1.5*6.3 = 9.45 -> ON
        # textbook (BBhw = 2.0*sd):   11.533 > 9.45 -> OFF
        c = [float(i) for i in range(20)]
        h = [x + 3.15 for x in c]
        lo = [x - 3.15 for x in c]
        on, off, _ = squeeze_momentum(h, lo, c)                      # script default (SOURCED quirk)
        self.assertEqual((on[19], off[19]), (True, False))
        on, off, _ = squeeze_momentum(h, lo, c, bb_mult=2.0)         # bb_mult alone does not change the script default
        self.assertEqual((on[19], off[19]), (True, False))
        on, off, _ = squeeze_momentum(h, lo, c, textbook_bb=True)    # textbook 2.0 (OURS)
        self.assertEqual((on[19], off[19]), (False, True))

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            squeeze_momentum([1], [1, 2], [1])


if __name__ == "__main__":
    unittest.main()
