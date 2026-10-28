"""Offline tests for the mainnet daily-P/L wiring in daily_loss_monitor.compute_total_pnl_usd (brief 132-SONNET).
Numbers worked by hand from Deribit's documented semantics (see spec 129); needs mainnet_pnl promoted first."""
import unittest

import daily_loss_monitor as dlm

STATE = {"date": "2026-09-29", "day_start_equity": 1.0, "breached_today": False}
MARK = 100000.0


class Client:
    def __init__(self, logs, summary, env="mainnet"):
        self.logs, self.summary, self.env, self.calls = logs, summary, env, []

    def active_env(self):
        return self.env

    def get_transaction_log(self, token, currency="BTC", start_ms=0, end_ms=0):
        self.calls.append(("log", start_ms, end_ms))
        return self.logs

    def get_account_summary(self, token, currency="BTC"):
        self.calls.append("summary")
        return self.summary

    def get_ticker(self, instrument_name="BTC-PERPETUAL"):
        return {"mark_price": MARK}


LOGS = [
    {"type": "trade", "change": -1e-05, "cashflow": -0.0005, "profit_as_cashflow": True},
    {"type": "trade", "change": -2e-06, "cashflow": 0.0},
    {"type": "deposit", "change": 1.0},
    {"type": "swap", "change": 0.5},
    {"type": "correction", "change": 0.3},
    {"type": "transfer", "change": -0.4},
]


class DailyPnlWiringTests(unittest.TestCase):
    def test_mainnet_counts_cashflow_and_unrealized_and_skips_money_movement(self):
        # realized -0.000512 BTC, session UPL -0.0002 BTC -> -0.000712 BTC * 100000 = -71.2 USD
        c = Client(LOGS, {"equity": 1.0, "futures_session_upl": -0.0002})
        self.assertEqual(dlm.compute_total_pnl_usd(c, "tok", STATE, now_ms=1_790_000_000_000), -71.2)

    def test_mainnet_queries_log_from_utc_day_start(self):
        c = Client(LOGS, {"futures_session_upl": 0.0})
        dlm.compute_total_pnl_usd(c, "tok", STATE, now_ms=1_790_000_000_000)
        kind, start_ms, end_ms = next(x for x in c.calls if isinstance(x, tuple))
        self.assertEqual(start_ms, 1790640000000)  # 2026-09-29T00:00:00Z
        self.assertEqual(end_ms, 1_790_000_000_000)

    def test_summary_without_upl_fails_closed(self):
        c = Client(LOGS, {"equity": 1.0})
        with self.assertRaises(ValueError):
            dlm.compute_total_pnl_usd(c, "tok", STATE, now_ms=1_790_000_000_000)

    def test_explicit_equity_source_still_available(self):
        c = Client(LOGS, {"equity": 0.999}, env="test")
        # (0.999 - 1.0) * 100000 = -100.0 (float noise rounded to 2 dp)
        self.assertEqual(dlm.compute_total_pnl_usd(c, "tok", STATE, pnl_source="equity"), -100.0)  # XFERFIX: testnet default is now the log
        self.assertFalse(any(isinstance(x, tuple) for x in c.calls), "equity source must not read the tx log")


if __name__ == "__main__":
    unittest.main()
