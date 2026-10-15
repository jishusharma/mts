"""Fail-first tests for the OPR-WEEKLY-LOW-ROUND-SWEEP screen (synthetic 1m bars, hand-computed). Run: python test_study.py"""
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "chart_read_g5_2026-10-16"))
import study as W  # noqa: E402


class TestWeekLow(unittest.TestCase):
    def test_prior_monday_sunday_week_low(self):
        # day 0 = Saturday 2022-01-01; days 2..8 = Mon 01-03 .. Sun 01-09 (week 1); days 9..15 = week 2; days 16..22 = week 3
        nd = 23
        L = np.full(nd * 1440, 100.0)
        L[5 * 1440 + 10] = 90.0              # Thursday of week 1
        L[12 * 1440 + 10] = 95.0             # Thursday of week 2
        out = W.week_low_prior(L)
        self.assertTrue(np.isnan(out[:9 * 1440]).all())          # weeks 0 (partial) and 1 (no full prior week)
        self.assertTrue((out[9 * 1440:16 * 1440] == 90.0).all())  # week 2 sees week 1's low
        self.assertTrue((out[16 * 1440:23 * 1440] == 95.0).all())  # week 3 sees week 2's low


class TestBreak(unittest.TestCase):
    def test_first_break_needs_previous_closes_above_and_penetration(self):
        Cl = np.array([101.0, 101, 101, 101, 101, 99, 99])
        Lo = np.array([100.5, 100.5, 100.5, 100.5, 99.5, 98, 98])
        lvl = np.full(7, 100.0)
        self.assertEqual(list(W.break_candidates(Lo, Cl, lvl, 0.001, prev=3)), [4, 5])    # threshold 99.9: low 99.5 and 98 qualify
        self.assertEqual(list(W.break_candidates(Lo, Cl, lvl, 0.01, prev=3)), [5])        # threshold 99.0: only the 98 low; bar 6 has closes below
        self.assertEqual(list(W.break_candidates(Lo, Cl, lvl, 0.0, prev=3)), [4, 5])


class TestClassify(unittest.TestCase):
    def test_abc(self):
        n, w = 5, 61
        Cw = np.full((n, w), 101.0)
        Cw[0, :] = 101                                   # immediate reclaim, holds -> A
        Cw[1, :3] = 99                                   # three closes below first (s=2), reclaim at 3 -> acceptance came first -> B
        Cw[2, 0] = 99; Cw[2, 2] = 99                     # reclaim at 1 but a close below at 2 inside the 15-minute hold, no 3 in a row -> C
        Cw[3, :10] = 99                                  # ten closes below -> B
        Cw[4, 0] = 99                                    # one close below then reclaim at 1 and hold -> A
        self.assertEqual(list(W.classify_abc(Cw, np.full(n, 100.0), k=5, m=3)), ["A", "B", "C", "B", "A"])
        Cw[0, 0] = np.nan
        self.assertEqual(W.classify_abc(Cw, np.full(n, 100.0))[0], "X")

    def test_k_and_m_grid(self):
        Cw = np.full((1, 61), 101.0)
        Cw[0, :4] = 99                                   # reclaim at 4
        lvl = np.full(1, 100.0)
        self.assertEqual(W.classify_abc(Cw, lvl, k=3, m=5)[0], "C")   # reclaim after k=3, 4 closes below < m=5 -> neither
        self.assertEqual(W.classify_abc(Cw, lvl, k=3, m=3)[0], "B")
        self.assertEqual(W.classify_abc(Cw, lvl, k=5, m=5)[0], "A")   # reclaim at 4 <= 5, acceptance (5 below) never happened


class TestTradeIndex(unittest.TestCase):
    def test_reclaim_and_acceptance_entries(self):
        Cw = np.full((3, 61), 101.0)
        Cw[0, :2] = 99        # reclaim at 2
        Cw[1, :] = 99         # never reclaims
        Cw[2, 0] = 99         # reclaim at 1
        r = W.first_above(Cw, np.full(3, 100.0))
        self.assertEqual(list(r), [2, 10 ** 6, 1])
        self.assertEqual(list(W.accepted_first3(Cw, np.full(3, 100.0))), [False, True, False])


if __name__ == "__main__":
    unittest.main()
