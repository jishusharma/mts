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


class TestInverseMathFormulasR3(unittest.TestCase):
    """R2 addition (Opus audit MUTATION_REPORT_FT2.md, mutant R3): dropping
    the abs() in account_position_notional's mark_price-GIVEN branch
    SURVIVED the original mutation suite - every existing test above
    (test_contract_denominated included) uses a non-negative size, so
    `abs(size)*mark` and `size*mark` agree and never distinguish the
    mutant. A SHORT position reports a NEGATIVE size from the exchange -
    this class is the first coverage of that sign on the mark-given
    branch. Also keeps two extra non-integer hand-computed cases (mark=None
    and mark-given) for precision beyond the existing suite's round numbers.
    """

    def test_mark_none_non_integer_size(self):
        # hand calc: abs(-1234.567) rounded to 2dp = 1234.57
        self.assertEqual(account_position_notional(-1234.567, None), 1234.57)

    def test_mark_given_non_integer(self):
        # hand calc: abs(-2.5) * 51234.333 = 128085.8325 -> round 2dp = 128085.83
        self.assertEqual(account_position_notional(-2.5, 51234.333), round(2.5 * 51234.333, 2))

    def test_r3_short_position_mark_given_stays_positive(self):
        # R3 killer: a short of size=-4 contracts, mark_price=25000 ->
        # abs(-4)*25000 = 100000.0. If abs() is dropped, this returns
        # -100000.0 instead - wrong sign, and a real caller (risk_guard's
        # own cap check, which never expects a negative notional) would
        # silently under-count the account's true exposure.
        self.assertEqual(account_position_notional(-4, 25000), 100000.0)

    def test_r3_short_position_mark_given_non_round(self):
        # hand calc: abs(-6.25) * 33333.33 = 208333.3125 -> round 2dp = 208333.31
        self.assertEqual(account_position_notional(-6.25, 33333.33), round(6.25 * 33333.33, 2))



class TestNanFailClosed(unittest.TestCase):
    def test_nonfinite_size_is_refused_by_cap(self):
        import math
        for bad in (float("nan"), float("inf"), None, "x"):
            for px in (None, 50000.0):
                n = account_position_notional(bad, px)
                self.assertEqual(n, math.inf, repr((bad, px)))
                self.assertFalse(check_new_plan_against_cap(n, 100.0)["ok"])

    def test_nan_notional_direct_to_cap_is_refused(self):
        self.assertFalse(check_new_plan_against_cap(float("nan"), 100.0)["ok"])
        self.assertFalse(check_new_plan_against_cap(0.0, float("nan"))["ok"])
        self.assertTrue(check_new_plan_against_cap(100.0, 1.0, cap=10000)["ok"])  # sanity: normal still ok


if __name__ == "__main__":
    unittest.main()
