"""run_context_read tests. Expected numbers are hand values computed independently of the code (arithmetic written out in each test)."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import run_context_read as rc  # noqa: E402

T0 = 1640995200000          # 2022-01-01 00:00 UTC, a Saturday


class TestStats(unittest.TestCase):
    def test_cluster_mean_hand(self):
        # x = [1,3,2,6], weeks A,A,B,B: mean 3; S_A = (1-3)+(3-3) = -2, S_B = (2-3)+(6-3) = 2; se = sqrt(4+4)/4 = 0.707107; t = 3/0.707107 = 4.242641
        m, se, t, g = rc.cluster_mean([1, 3, 2, 6], ["A", "A", "B", "B"])
        self.assertAlmostEqual(m, 3.0, 9)
        self.assertAlmostEqual(se, 0.7071068, 6)
        self.assertAlmostEqual(t, 4.2426407, 5)
        self.assertEqual(g, 2)

    def test_slope_cluster_hand(self):
        # x = [-1,1,-1,1], y = [0,2,1,1]: xbar 0, ybar 1, slope = (1+1+0+0)/4 = 0.5; e = [-.5,.5,.5,-.5];
        # scores x*e = [.5,.5,-.5,-.5]; S_A = 1, S_B = -1; se = sqrt(2)/4 = 0.353553; t = 1.414214
        b, se, t = rc.slope_cluster([-1, 1, -1, 1], [0, 2, 1, 1], ["A", "A", "B", "B"])
        self.assertAlmostEqual(b, 0.5, 9)
        self.assertAlmostEqual(se, 0.3535534, 6)
        self.assertAlmostEqual(t, 1.4142136, 5)

    def test_spearman_is_rank_correlation(self):
        # perfectly monotone but non-linear: rho = 1
        x = [1, 2, 3, 4, 5, 6]
        y = [1, 4, 9, 16, 25, 36]
        rho, _, _ = rc.spearman_cluster(x, y, [1, 1, 2, 2, 3, 3])
        self.assertAlmostEqual(rho, 1.0, 9)

    def test_mde_matches_prereg(self):
        # (2.991 + 0.8416) * 2.5 * sqrt((1 + (21888/128 - 1) * 0.3) / 21888) = 9.5805 * sqrt(52.2/21888) = 0.468 (PRE_REG: about 0.47)
        self.assertAlmostEqual(rc.mde(21888, 128), 0.468, 2)

    def test_week_anchor(self):
        # 2022-01-03 is a Monday; 2022-01-02 (Sunday) is the previous week
        mon = T0 + 2 * rc.DAY
        self.assertEqual(rc.week_of(mon) - rc.week_of(mon - rc.H1), 1)
        self.assertEqual(rc.week_of(mon + 6 * rc.DAY) - rc.week_of(mon), 0)


class TestNoFutureBar(unittest.TestCase):
    def test_guard_raises_on_planted_future_bar(self):
        t = np.array([rc.CUT - 2 * rc.H1, rc.CUT - rc.H1, rc.CUT])        # the last bar opens AT the cut
        with self.assertRaises(rc.AccessViolation):
            rc.guard(t)

    def test_build_points_refuses_future_bar(self):
        n = 40
        t = rc.CUT - (n - 1) * rc.H1 + np.arange(n) * rc.H1 + rc.H1       # last bar opens at the cut
        c = np.full(n, 100.0)
        with self.assertRaises(rc.AccessViolation):
            rc.build_points(t, c, c, np.array([0], dtype=np.int64), {"D1": np.array([1])})

    def test_guard_accepts_last_dev_bar(self):
        rc.guard(np.array([rc.CUT - rc.H1]))


class TestPoints(unittest.TestCase):
    def _toy(self):
        n = 60
        t = T0 + np.arange(n) * rc.H1
        o = np.full(n, 100.0)
        c = np.full(n, 100.0)
        o[1] = 100.0                      # entry of decision bar 0
        c[24] = 102.0                     # exit of decision bar 0 = close of bar 0 + 24
        return t, o, c

    def test_r24_and_sides_hand(self):
        t, o, c = self._toy()
        dec0 = T0 + rc.H1
        # one row visible before the first decision (available_at = dec0 - 1), one row available exactly AT the decision (must NOT be used)
        av = np.array([dec0 - 1, dec0], dtype=np.int64)
        sides = {"D1": np.array([1, -1]), "sma": np.array([1, 1]), "ret": np.array([-1, -1])}
        P = rc.build_points(t, o, c, av, sides)
        self.assertEqual(P["dec"][0], dec0)
        self.assertAlmostEqual(P["gross"][0], 2.0, 9)                     # (102 / 100 - 1) * 100
        self.assertEqual(P["side_D1"][0], 1)                              # strict availability: the row at dec0 is not used
        self.assertAlmostEqual(P["net"]["D1"][0], 1.9, 9)                 # long: +2.0 - 0.10
        self.assertAlmostEqual(P["net"]["ret"][0], -2.1, 9)               # short: -2.0 - 0.10 (cost after the sign)
        self.assertEqual(P["side_D1"][1], -1)                             # next decision sees the second row
        self.assertEqual(len(P["dec"]), 60 - 24)

    def test_flat_side_pays_nothing(self):
        t, o, c = self._toy()
        P = rc.build_points(t, o, c, np.array([T0], dtype=np.int64), {"D1": np.array([0])})
        self.assertAlmostEqual(P["net"]["D1"][0], 0.0, 9)

    def test_d1_side_rule(self):
        self.assertEqual(rc._side_d1(1, 1), 1)
        self.assertEqual(rc._side_d1(-1, -1), -1)
        self.assertEqual(rc._side_d1(1, -1), 0)
        self.assertEqual(rc._side_d1(0, 1), 0)


if __name__ == "__main__":
    unittest.main()
