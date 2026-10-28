"""Fail-first tests for the EU-low/US-sweep follow-up legs (synthetic 1m / 5m bars, every expected number worked by hand).
Run: python test_followups.py"""
import math
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import followups as F  # noqa: E402

T0 = 1440


def flat(n, px=100.0):
    a = np.full(n, px)
    return a.copy(), a.copy(), a.copy(), a.copy()          # O, H, L, C


def planted_sweep():
    """Lookback flat at 100 with ONE low of 98 at minute 200 (SINGLE day). In the window: break at T0+30 (low 97.5, close 97.7 < L),
    deeper low 97.0 at T0+31, reclaim at T0+32 (close 98.3 > 98). Entry open 99.0 at T0+34, time-exit open 100.0 at T0+34+120."""
    n = T0 + 700
    O, H, L, C = flat(n)
    L[200] = 98.0
    b = T0 + 30
    O[b], H[b], L[b], C[b] = 100.0, 100.0, 97.5, 97.7
    O[b + 1], H[b + 1], L[b + 1], C[b + 1] = 97.7, 97.8, 97.0, 97.5
    O[b + 2], H[b + 2], L[b + 2], C[b + 2] = 97.5, 98.5, 97.4, 98.3
    for k in range(b + 3, n):
        O[k] = H[k] = L[k] = C[k] = 99.0
    O[b + 4 + 120] = 100.0
    return O, H, L, C


class TestLegA(unittest.TestCase):
    def test_planted_reclaim_time_entry_stop_and_R(self):
        O, H, L, C = planted_sweep()
        ev = F.leg_a(O, H, L, C, 0, T0)
        self.assertEqual(ev["kind"], "SINGLE")
        self.assertEqual(ev["break_idx"], T0 + 30)
        self.assertEqual(ev["reclaim_idx"], T0 + 32)                 # first CLOSE above L=98 after the break
        self.assertEqual(ev["entry_idx"], T0 + 34)                   # decision at the reclaim close, +1 bar, +1 delay bar
        self.assertAlmostEqual(ev["stop"], 97.0 * 0.999, places=9)   # lowest low break..reclaim, minus 0.1 %
        self.assertAlmostEqual(ev["risk"], (99.0 - 97.0 * 0.999) / 99.0, places=9)
        res = F.sim(O, H, L, +1, ev["entry_idx"], ev["stop"], F.H_A)
        self.assertEqual(res["why"], "time")
        self.assertAlmostEqual(res["gross"], 100.0 / 99.0 - 1.0, places=9)
        self.assertAlmostEqual(res["gross"] / ev["risk"], (100.0 / 99.0 - 1.0) / ((99.0 - 96.903) / 99.0), places=9)  # 0.4769 R

    def test_stop_exit_is_minus_one_R(self):
        O, H, L, C = planted_sweep()
        L[T0 + 40] = 96.0                                           # trades through the stop 96.903
        ev = F.leg_a(O, H, L, C, 0, T0)
        res = F.sim(O, H, L, +1, ev["entry_idx"], ev["stop"], F.H_A)
        self.assertEqual(res["why"], "stop")
        self.assertAlmostEqual(res["gross"] / ev["risk"], -1.0, places=9)

    def test_no_reclaim_inside_120_minutes_is_skipped(self):
        O, H, L, C = planted_sweep()
        for k in range(T0 + 32, T0 + 30 + 125):                     # keep every close below L for >120 minutes
            C[k] = 97.5
        ev = F.leg_a(O, H, L, C, 0, T0)
        self.assertEqual(ev["skip"], "noreclaim")

    def test_entry_beyond_stop_is_skipped(self):
        O, H, L, C = planted_sweep()
        O[T0 + 34] = 96.0                                           # fills under the stop
        ev = F.leg_a(O, H, L, C, 0, T0)
        self.assertEqual(ev["skip"], "entry_through_stop")


class TestSim(unittest.TestCase):
    def test_short_stop_gap_fills_at_open(self):
        n = 50
        O, H, L, C = flat(n)
        O[10], H[10], L[10], C[10] = 106.0, 107.0, 105.5, 106.5     # gaps through the stop 102
        res = F.sim(O, H, L, -1, 5, 102.0, 30)
        self.assertEqual(res["why"], "stop")
        self.assertAlmostEqual(res["gross"], -(106.0 / 100.0 - 1.0), places=9)


class TestLegB(unittest.TestCase):
    def arrays(self):
        H5 = np.full(288, 100.0)
        R5 = np.full(288, 50.0)
        H5[80], H5[100] = 110.0, 111.0
        R5[80], R5[100] = 75.0, 68.0
        return H5, R5

    def test_bearish_divergence_first_signal(self):
        H5, R5 = self.arrays()
        self.assertEqual(F.rsi_div_first_signal(H5, R5, 0, 288), 100)

    def test_rsi_not_lower_enough_is_no_signal(self):
        H5, R5 = self.arrays()
        R5[100] = 74.0                                               # only 1 point lower than 75 (< 2)
        self.assertIsNone(F.rsi_div_first_signal(H5, R5, 0, 288))

    def test_previous_high_too_close_is_no_signal(self):
        H5, R5 = self.arrays()
        H5[100], R5[100] = 100.0, 50.0
        H5[85], R5[85] = 111.0, 68.0                                 # 5 bars after the 110 high (< 12)
        self.assertIsNone(F.rsi_div_first_signal(H5, R5, 0, 288))

    def test_previous_high_not_strong_is_no_signal(self):
        H5, R5 = self.arrays()
        R5[80] = 55.0                                                # earlier high came with RSI 55 < 60
        self.assertIsNone(F.rsi_div_first_signal(H5, R5, 0, 288))


class TestLegC(unittest.TestCase):
    def arrays(self, base=100.0):
        n = 1000 + 400
        O, H, L, C = flat(n, base)
        H[700] = 105.0                                               # P1
        H[900] = 104.9                                               # P2, 0.095 % under P1 (tolerance 0.15 %)
        O[1001] = 104.0                                              # entry open (decision T0=1000, +1 delay)
        return O, H, L, C

    def test_double_top_found_with_stop_above_P1(self):
        O, H, L, C = self.arrays()
        ev = F.leg_c(O, H, L, C, 1000)
        self.assertEqual((ev["p1"], ev["p2"]), (700, 900))
        self.assertAlmostEqual(ev["stop"], 105.0 * 1.001, places=9)
        self.assertEqual(ev["entry_idx"], 1001)
        self.assertAlmostEqual(ev["risk"], (105.105 - 104.0) / 104.0, places=9)

    def test_second_top_outside_tolerance_is_none(self):
        O, H, L, C = self.arrays()
        H[900] = 104.0
        self.assertIsNone(F.leg_c(O, H, L, C, 1000))

    def test_no_valley_is_none(self):
        O, H, L, C = self.arrays(base=104.7)                         # lows never fall 0.5 % under P1 (104.475)
        self.assertIsNone(F.leg_c(O, H, L, C, 1000))


class TestGate(unittest.TestCase):
    def test_mde_hand_value(self):
        mde, ok = F.gate(160, 1.0, 0.28, 3)                          # (2.3939 + 0.84) / sqrt(160) = 0.2557
        self.assertAlmostEqual(mde, 0.2557, places=3)
        self.assertFalse(ok)
        mde2, ok2 = F.gate(10000, 1.0, 0.05, 3)
        self.assertAlmostEqual(mde2, 0.0323, places=3)
        self.assertTrue(ok2)


if __name__ == "__main__":
    unittest.main()
