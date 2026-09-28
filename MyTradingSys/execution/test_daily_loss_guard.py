import unittest
from daily_loss_guard import (
    daily_pnl,
    check_daily_loss_cap,
    format_breach_report,
    DEFAULT_DAILY_LOSS_CAP_USD
)


class TestDailyLossGuard(unittest.TestCase):

    def test_daily_pnl_empty(self):
        self.assertEqual(daily_pnl([], 0.0), 0.0)

    def test_daily_pnl_with_events(self):
        events = [{"pnl_usd": -100.0}, {"pnl_usd": 50.0}]
        self.assertEqual(daily_pnl(events, -20.0), -70.0)

    def test_daily_pnl_malformed_raises(self):
        # This test was changed to reflect new contract: missing keys now raise ValueError
        # Instead of silently skipping, we now expect a ValueError for malformed events
        with self.assertRaises(ValueError):
            daily_pnl([{"pnl_usd": -100.0}, {"other": 1}], 0.0)

    def test_check_daily_loss_cap_ok_default(self):
        result = check_daily_loss_cap([], 0.0)
        self.assertTrue(result["ok"])
        self.assertEqual(result["action"], "none")

    def test_check_daily_loss_cap_breach(self):
        result = check_daily_loss_cap([{"pnl_usd": -600.0}], 0.0)
        self.assertFalse(result["ok"])
        self.assertEqual(result["action"], "halt_and_flatten_all")
        self.assertIn("-600", result["reason"])
        self.assertIn("-500", result["reason"])

    def test_check_daily_loss_cap_boundary_exact(self):
        result = check_daily_loss_cap([{"pnl_usd": -500.0}], 0.0)
        self.assertFalse(result["ok"])  # Exactly at cap breaches

    def test_check_daily_loss_cap_boundary_inside(self):
        result = check_daily_loss_cap([{"pnl_usd": -499.99}], 0.0)
        self.assertTrue(result["ok"])  # Just inside cap is OK

    def test_check_daily_loss_cap_invalid_positive_cap(self):
        with self.assertRaises(ValueError):
            check_daily_loss_cap([], 0.0, cap_usd=0)

    def test_check_daily_loss_cap_invalid_positive_cap2(self):
        with self.assertRaises(ValueError):
            check_daily_loss_cap([], 0.0, cap_usd=100)

    def test_missing_pnl_usd_raises(self):
        # Test that a missing pnl_usd key raises ValueError
        with self.assertRaises(ValueError):
            check_daily_loss_cap([{"pnl": -5}], 0.0)

    def test_format_breach_report_ok(self):
        result = {"ok": True, "total_pnl_usd": -100.0, "cap_usd": DEFAULT_DAILY_LOSS_CAP_USD, "action": "none", "reason": None}
        self.assertIn("DAILY LOSS OK", format_breach_report(result))

    def test_format_breach_report_breach(self):
        result = {"ok": False, "total_pnl_usd": -600.0, "cap_usd": DEFAULT_DAILY_LOSS_CAP_USD, "action": "halt_and_flatten_all", "reason": "daily pnl -600.0 breached cap -500.0"}
        self.assertIn("DAILY LOSS BREACH - HALT ALL TRADING", format_breach_report(result))


if __name__ == "__main__":
    unittest.main()
