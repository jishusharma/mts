"""Fail-first tests for the pre-open tops screen (synthetic bars, hand-computed). Run: python test_study.py"""
import datetime as dt
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "chart_read_g5_2026-10-16"))
import study as P  # noqa: E402
import common as K  # noqa: E402


class TestOpen(unittest.TestCase):
    def test_dst_open_utc(self):
        ms = lambda d, h, m: int(dt.datetime(d.year, d.month, d.day, h, m, tzinfo=dt.timezone.utc).timestamp() * 1000)
        for d, hh in ((dt.date(2023, 3, 10), 14), (dt.date(2023, 3, 13), 13), (dt.date(2022, 11, 4), 13), (dt.date(2022, 11, 7), 14)):
            self.assertEqual(P.open_idx(d), (ms(d, hh, 30) - K.TS0) // K.MS, str(d))


class TestSwing(unittest.TestCase):
    def test_swing_tie_first_wins(self):
        H = np.array([1, 2, 3, 10, 4, 3, 2, 1, 1, 1], float)
        self.assertEqual(P.swing_highs(H, 0, 9, 3), [3])
        H2 = np.array([1, 2, 3, 10, 10, 3, 2, 1, 1, 1], float)      # equal peak to the right allowed, to the left not
        self.assertEqual(P.swing_highs(H2, 0, 9, 3), [3])

    def test_unbroken(self):
        H = np.array([1, 2, 3, 10, 4, 3, 2, 11, 1, 1], float)
        self.assertTrue(P.unbroken(H, 3, 7))        # bars 4..6 stay <= 10
        self.assertFalse(P.unbroken(H, 3, 9))       # bar 7 is 11 > 10


class TestBreakAndSpeed(unittest.TestCase):
    def setUp(self):
        n = 40
        self.H = np.full(n, 90.0)
        self.L = np.full(n, 89.0)
        self.C = np.full(n, 90.0)
        self.atr = np.full(n, 2.0)

    def test_break_threshold_is_strict(self):
        self.C[20] = 100.2                         # top 100 + 0.1 x ATR 2 = 100.2: equal is NOT a break
        self.C[22] = 100.21
        self.assertEqual(P.first_break(self.C, self.atr, 100.0, 12, 30, 0.1), 22)
        self.assertEqual(P.first_break(self.C, self.atr, 100.0, 12, 21, 0.1), -1)

    def test_quick_speeds_hand_computed(self):
        # open at 3m bar 12, break at bar 18 (close 101), top 100, ATR 2
        self.H[13], self.H[14], self.H[15], self.H[16] = 99.7, 98.0, 99.6, 95.0
        self.C[18], self.H[18] = 101.0, 101.5
        self.L[12] = 84.0                                  # lowest low of bars 8..17
        s1, s2, s3 = P.speeds(self.H, self.L, self.C, self.atr, 12, 18, 100.0)
        self.assertEqual(s1, (18 + 1 - 12) * 3)            # 21 minutes from the open to the break-bar close
        self.assertAlmostEqual(s2, (101.0 - 84.0) / 2.0)   # 8.5 ATR
        self.assertEqual(s3, 2)                            # bars 13 (99.7) and 15 (99.6) are >= 100 - 0.25 x 2 = 99.5

    def test_slow_speeds_hand_computed(self):
        self.H[13], self.H[15] = 99.7, 99.6
        self.H[18:27] = 99.9
        self.C[27], self.H[27] = 100.5, 100.6
        self.L[12] = 98.0
        s1, s2, s3 = P.speeds(self.H, self.L, self.C, self.atr, 12, 27, 100.0)
        self.assertEqual(s1, (27 + 1 - 12) * 3)            # 48 minutes
        self.assertEqual(s3, 2 + 9)                        # 13, 15 and the nine bars 18..26
        self.assertGreater(s1, 21)
        self.assertGreater(s3, 2)


class TestTertiles(unittest.TestCase):
    def test_groups(self):
        s = np.array([3, 3, 6, 9, 12, 30, 60, 90, 120], float)
        g = P.groups(s, 1 / 3, 2 / 3)
        q1, q2 = np.quantile(s, [1 / 3, 2 / 3])
        self.assertTrue(((g == "quick") == (s <= q1)).all())
        self.assertTrue(((g == "slow") == (s >= q2)).all())


if __name__ == "__main__":
    unittest.main()
