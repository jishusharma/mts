"""Proposed gate regressions. The fixture inherits the existing throwaway Git setup."""
import copy
import unittest

from MyTradingSys.backtest.layers.promotion import promote as pm
from MyTradingSys.backtest.layers.promotion.test_promote import Base


class ValidationDateFormat(Base):
    def test_validation_read_at_must_be_iso_date(self):
        # EXPECT: REJECT; RESULT on current promote.py: PASS (the string is only checked for non-emptiness).
        m = copy.deepcopy(self.m)
        m["validation_reads"][0]["at"] = "not-a-date"
        self.assertEqual(pm.check(m, repo=self.repo, config_path=self.cfg)["result"], "REJECT")


class GateBoundaryProbes(unittest.TestCase):
    def test_holm_one_variant_is_two_sided_five_percent(self):
        # PASS-ONLY: current implementation should retain its one-variant z boundary.
        self.assertAlmostEqual(pm.holm_z(1), 1.9599639845, places=8)

    def test_mde_integer_cutoff_uses_ceiling(self):
        # PASS-ONLY: formula yields 170.154..., so 170 fails and 171 meets the floor.
        o = {"ci_low": 0.09, "ci_high": 0.15, "n_trades": 250, "net_r": 0.12}
        floor = pm.mde_floor(o, pm.holm_z(3))
        self.assertLess(170, floor)
        self.assertGreaterEqual(171, floor)

    def test_30_is_the_documented_basic_floor_boundary(self):
        # PASS-ONLY arithmetic boundary; full check also requires consistent CSV and statistical gates.
        self.assertEqual(pm.MIN_TRADES, 30)


if __name__ == "__main__":
    unittest.main()
