"""Core-rule tests for study.py (quintile weights, drift, turnover/fee, funding sign, BH, block bootstrap)."""
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study  # noqa: E402


class T(unittest.TestCase):
    def test_ls_weights_neutral(self):
        sig = {"s%d" % i: i for i in range(20)}
        w = study.quintile_weights(sig, 4, "LS")
        self.assertAlmostEqual(sum(w.values()), 0.0)
        self.assertEqual({s for s, v in w.items() if v > 0}, {"s16", "s17", "s18", "s19"})
        self.assertEqual({s for s, v in w.items() if v < 0}, {"s0", "s1", "s2", "s3"})
        r = study.quintile_weights(sig, 4, "REV")
        self.assertTrue(all(abs(r[s] + w[s]) < 1e-12 for s in w))

    def test_lo_net_weights(self):
        sig = {"s%d" % i: i for i in range(20)}
        w = study.quintile_weights(sig, 4, "LO")
        self.assertAlmostEqual(sum(w.values()), 0.0)
        self.assertAlmostEqual(w["s19"], 0.25 - 0.05)
        self.assertAlmostEqual(w["s0"], -0.05)

    def test_fee_and_funding_signs(self):
        w = {"A": 0.5, "B": -0.5}
        net, gross, fee, fu = study.week_net(w, {}, {"A": 0.10, "B": 0.0}, {"A": 0.001, "B": 0.001})
        self.assertAlmostEqual(gross, 0.05)
        self.assertAlmostEqual(fee, study.FEE * 1.0)       # first week pays full entry, |0.5|+|0.5|
        self.assertAlmostEqual(fu, 0.0)                    # long pays, short receives the same rate
        net2, _, _, fu2 = study.week_net({"A": 1.0}, {"A": 1.0}, {"A": 0.0}, {"A": 0.002})
        self.assertAlmostEqual(fu2, -0.002)                # long pays positive funding
        self.assertAlmostEqual(study.week_net({"A": -1.0}, {"A": -1.0}, {"A": 0.0}, {"A": 0.002})[3], 0.002)

    def test_drift_and_turnover(self):
        w = {"A": 0.5, "B": -0.5}
        d = study.drift(w, {"A": 0.2, "B": 0.0})
        self.assertAlmostEqual(d["A"], 0.5 * 1.2 / 1.1)
        self.assertAlmostEqual(study.turnover(d, w), abs(d["A"] - 0.5) + abs(d["B"] + 0.5))

    def test_bh(self):
        self.assertEqual(study.bh({"a": 0.001, "b": 0.5, "c": 0.04}, 0.10), {"a", "c"})

    def test_boot_positive_series(self):
        r = study.block_boot(np.full(40, 0.01), np.random.default_rng(1), n=500)
        self.assertGreater(r["lo"], 0)
        z = study.block_boot(np.random.default_rng(2).normal(0, 0.05, 60), np.random.default_rng(3), n=500)
        self.assertLess(z["lo"], 0)


if __name__ == "__main__":
    unittest.main()
