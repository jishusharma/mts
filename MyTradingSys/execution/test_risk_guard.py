"""
MyTradingSys/execution/test_risk_guard.py

Unit tests for risk_guard.py
"""
import unittest
from risk_guard import (
    account_position_notional,
    check_new_plan_against_cap,
    format_guard_report,
    MAX_ACCOUNT_NOTIONAL_USD
)


class TestAccountPositionNotional(unittest.TestCase):
    def test_already_usd(self):
        self.assertEqual(account_position_notional(5, None), 5.0)
        self.assertEqual(account_position_notional(-5, None), 5.0)

    def test_contract_denominated(self):
        self.assertEqual(account_position_notional(2, 50000.0), 100000.0)
        self.assertEqual(account_position_notional(0, 50000.0), 0.0)


class TestCheckNewPlanAgainstCap(unittest.TestCase):
    def test_ok_case(self):
        result = check_new_plan_against_cap(0, 5000, cap=10000)
        self.assertTrue(result["ok"])
        self.assertIsNone(result["reason"])

    def test_breach_case(self):
        result = check_new_plan_against_cap(9000, 2000, cap=10000)
        self.assertFalse(result["ok"])
        self.assertIn("11000", result["reason"])
        self.assertIn("10000", result["reason"])

    def test_boundary_case(self):
        result = check_new_plan_against_cap(9000, 1000, cap=10000)
        self.assertTrue(result["ok"])
        self.assertIsNone(result["reason"])

    def test_negative_inputs_raise(self):
        with self.assertRaises(ValueError):
            check_new_plan_against_cap(-1, 100)
        with self.assertRaises(ValueError):
            check_new_plan_against_cap(100, -1)
        with self.assertRaises(ValueError):
            check_new_plan_against_cap(100, 100, cap=0)

    def test_projected_rounding(self):
        # Test that rounding works correctly in the projection
        result = check_new_plan_against_cap(9999.99, 0.01, cap=10000)
        self.assertTrue(result["ok"])
        self.assertEqual(result["projected_notional_usd"], 10000.0)


class TestFormatGuardReport(unittest.TestCase):
    def test_ok_report(self):
        result = check_new_plan_against_cap(1200, 800, cap=10000)
        report = format_guard_report(result)
        self.assertIn("ACCOUNT CAP OK", report)
        self.assertIn("current=1200.0 + new=800.0 = 2000.0 <= cap=10000", report)

    def test_breach_report(self):
        result = check_new_plan_against_cap(9000, 2000, cap=10000)
        report = format_guard_report(result)
        self.assertIn("ACCOUNT CAP BREACH", report)
        self.assertIn("account notional would reach 11000.0 > cap 10000", report)


if __name__ == "__main__":
    unittest.main()
