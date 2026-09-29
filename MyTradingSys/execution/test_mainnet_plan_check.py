"""Offline tests for mainnet_plan_check.plan_refusals (spec 128). Derived from the spec, not from the implementation."""
import unittest

import mainnet_plan_check as mpc

PLAN = {"stop": {"type": "fixed_percent"}}


def compiled(*amounts, mps=None):
    return {"max_position_size": sum(amounts) if mps is None else mps,
            "entry_orders": [{"side": "BUY", "amount": a, "order_type": "limit", "price": 1.0, "label": f"entry_{i}"}
                             for i, a in enumerate(amounts)]}


class PlanRefusalsTests(unittest.TestCase):
    def test_testnet_never_refuses(self):
        self.assertEqual(mpc.plan_refusals(compiled(500, 500), None, "test", 50.0), [])
        self.assertEqual(mpc.plan_refusals(compiled(500, mps=1), PLAN, "test", 50.0), [])

    def test_mainnet_raw_plan_within_cap_ok(self):
        self.assertEqual(mpc.plan_refusals(compiled(50), PLAN, "mainnet", 50.0), [])
        self.assertEqual(mpc.plan_refusals(compiled(20, 30), PLAN, "mainnet", 50.0), [])

    def test_mainnet_precompiled_input_refused(self):
        r = mpc.plan_refusals(compiled(50), None, "mainnet", 50.0)
        self.assertEqual(len(r), 1)
        self.assertIn("pre-compiled", r[0])

    def test_two_rungs_of_50_with_max_50_refused(self):  # audit R5
        r = mpc.plan_refusals(compiled(50, 50, mps=50), PLAN, "mainnet", 50.0)
        self.assertTrue(any("sum of entry amounts 100" in x for x in r), r)

    def test_sum_above_cap_refused_even_if_max_matches(self):
        r = mpc.plan_refusals(compiled(60), PLAN, "mainnet", 50.0)
        self.assertTrue(any("cap 50" in x for x in r), r)

    def test_max_position_size_above_cap_refused(self):
        r = mpc.plan_refusals(compiled(50, mps=80), PLAN, "mainnet", 50.0)
        self.assertTrue(r)

    def test_sum_below_max_position_size_refused(self):
        r = mpc.plan_refusals(compiled(10, mps=50), PLAN, "mainnet", 50.0)
        self.assertTrue(any("sum of entry amounts 10" in x for x in r), r)

    def test_bad_entry_amounts_refused(self):
        for bad in (0, -10, None, "50", True):
            c = compiled(50)
            c["entry_orders"][0]["amount"] = bad
            self.assertTrue(mpc.plan_refusals(c, PLAN, "mainnet", 50.0), bad)

    def test_no_entries_or_missing_keys_refused_not_raised(self):
        self.assertTrue(mpc.plan_refusals({"max_position_size": 50, "entry_orders": []}, PLAN, "mainnet", 50.0))
        self.assertTrue(mpc.plan_refusals({"entry_orders": [{"amount": 50}]}, PLAN, "mainnet", 50.0))
        self.assertTrue(mpc.plan_refusals({"max_position_size": 50}, PLAN, "mainnet", 50.0))

    def test_unknown_env_is_treated_as_mainnet(self):
        self.assertTrue(mpc.plan_refusals(compiled(50), None, "weird", 50.0))


if __name__ == "__main__":
    unittest.main()
