"""Offline tests for mainnet_pnl (spec 129). Expected numbers come from Deribit's documented field semantics
(private/get_transaction_log, private/get_account_summary), worked by hand in each test - not from any repo code."""
import unittest

import mainnet_pnl as mp


def tr(change, cashflow=None, pac=None, typ="trade"):
    e = {"type": typ, "change": change}
    if cashflow is not None:
        e["cashflow"] = cashflow
    if pac is not None:
        e["profit_as_cashflow"] = pac
    return e


class RealizedTests(unittest.TestCase):
    def test_stopped_out_loss_in_cashflow_is_counted(self):  # audit R4
        # fee -0.000003 (change) + realized session PnL -0.0005 (cashflow, profit_as_cashflow true) = -0.000503
        self.assertAlmostEqual(mp.realized_btc([tr(-3e-06, -0.0005, True)]), -0.000503, places=12)

    def test_cashflow_ignored_when_not_profit_as_cashflow(self):
        # change already holds the balance movement; cashflow must not be added again
        self.assertAlmostEqual(mp.realized_btc([tr(-2e-06, 0.0004, False)]), -2e-06, places=12)
        self.assertAlmostEqual(mp.realized_btc([tr(-2e-06, 0.0004)]), -2e-06, places=12)

    def test_sum_of_several_trades(self):
        es = [tr(-1e-05, -0.0005, True), tr(-1e-05, 0.0002, True), tr(-2e-06)]
        # (-0.00001-0.0005) + (-0.00001+0.0002) + (-0.000002) = -0.000322
        self.assertAlmostEqual(mp.realized_btc(es), -0.000322, places=12)

    def test_non_allow_listed_types_excluded(self):
        junk = [tr(1.0, typ="deposit"), tr(-1.0, typ="withdrawal"), tr(0.5, typ="transfer"), tr(0.5, typ="swap"),
                tr(0.3, typ="correction"), tr(0.2, typ="reward"),
                tr(0.2, typ="insurance fund"), tr(0.2, typ="something new"), tr(0.2, typ="TRANSFER")]
        self.assertEqual(mp.realized_btc(junk), 0.0)
        self.assertAlmostEqual(mp.realized_btc(junk + [tr(-1e-05)]), -1e-05, places=12)

    def test_settlement_counted_and_no_double_count_with_closing_trade(self):  # B149, captured jishu_11 2026-10-09
        # short 100 USD 82500 -> 82611.5 held across 08:00: whole PnL 100*(1/82611.5-1/82500) = -1.636e-06 BTC.
        # settlement at 08:00 -1.59e-06 (change == cashflow); closing trade cashflow -4e-08 (fee -6.1e-07 in change).
        es = [tr(-6.1e-07, -4e-08, True), {"type": "settlement", "change": -1.59e-06, "cashflow": -1.59e-06}]
        self.assertAlmostEqual(mp.realized_btc(es), -6.1e-07 - 4e-08 - 1.59e-06, places=12)
        # settlement alone (position still open after 08:00) is counted once, even if flagged profit_as_cashflow
        self.assertAlmostEqual(mp.realized_btc([{"type": "settlement", "change": -1.59e-06, "cashflow": -1.59e-06,
                                                 "profit_as_cashflow": True}]), -1.59e-06, places=12)
        self.assertAlmostEqual(mp.realized_btc([tr(2e-06, typ="Settlement")]), 2e-06, places=12)

    def test_settlement_without_numeric_change_raises(self):
        with self.assertRaises(ValueError):
            mp.realized_btc([{"type": "settlement", "cashflow": -1e-6}])

    def test_settlement_counted_and_no_double_count_with_closing_trade(self):  # B149, captured jishu_11 2026-10-09
        # short 100 USD 82500 -> 82611.5 held across 08:00: whole PnL 100*(1/82611.5-1/82500) = -1.636e-06 BTC.
        # settlement at 08:00 -1.59e-06 (change == cashflow); closing trade cashflow -4e-08 (fee -6.1e-07 in change).
        es = [tr(-6.1e-07, -4e-08, True), {"type": "settlement", "change": -1.59e-06, "cashflow": -1.59e-06}]
        self.assertAlmostEqual(mp.realized_btc(es), -6.1e-07 - 4e-08 - 1.59e-06, places=12)
        # settlement alone (position still open after 08:00) is counted once, even if flagged profit_as_cashflow
        self.assertAlmostEqual(mp.realized_btc([{"type": "settlement", "change": -1.59e-06, "cashflow": -1.59e-06,
                                                 "profit_as_cashflow": True}]), -1.59e-06, places=12)
        self.assertAlmostEqual(mp.realized_btc([tr(2e-06, typ="Settlement")]), 2e-06, places=12)

    def test_settlement_without_numeric_change_raises(self):
        with self.assertRaises(ValueError):
            mp.realized_btc([{"type": "settlement", "cashflow": -1e-6}])

    def test_trade_type_match_is_case_insensitive(self):
        self.assertAlmostEqual(mp.realized_btc([tr(-1e-05, typ="Trade")]), -1e-05, places=12)

    def test_empty_is_zero(self):
        self.assertEqual(mp.realized_btc([]), 0.0)

    def test_missing_or_bad_change_on_a_trade_raises(self):
        for bad in ({"type": "trade"}, {"type": "trade", "change": None}, {"type": "trade", "change": "1"},
                    {"type": "trade", "change": True}):
            with self.assertRaises(ValueError):
                mp.realized_btc([bad])

    def test_profit_as_cashflow_true_without_numeric_cashflow_raises(self):
        for bad in ({"type": "trade", "change": -1e-6, "profit_as_cashflow": True},
                    {"type": "trade", "change": -1e-6, "profit_as_cashflow": True, "cashflow": "x"}):
            with self.assertRaises(ValueError):
                mp.realized_btc([bad])

    def test_excluded_entries_are_not_validated(self):
        self.assertEqual(mp.realized_btc([{"type": "deposit"}, {"type": "swap", "change": None}]), 0.0)


class UnrealizedTests(unittest.TestCase):
    def test_prefers_futures_session_upl(self):
        self.assertEqual(mp.unrealized_btc({"futures_session_upl": -0.0002, "session_upl": -0.5}), -0.0002)

    def test_falls_back_to_session_upl(self):
        self.assertEqual(mp.unrealized_btc({"session_upl": 0.0001}), 0.0001)

    def test_missing_or_non_numeric_raises(self):
        for bad in ({}, {"equity": 1.0}, {"futures_session_upl": None}, {"session_upl": "1"},
                    {"futures_session_upl": True}):
            with self.assertRaises(ValueError):
                mp.unrealized_btc(bad)


class DailyTests(unittest.TestCase):
    def test_realized_plus_unrealized(self):
        es = [tr(-1e-05, -0.0005, True), tr(-2e-06), tr(1.0, typ="deposit")]
        # realized (-0.00001-0.0005) + (-0.000002) = -0.000512; upl -0.0002 -> -0.000712
        self.assertAlmostEqual(mp.daily_pnl_btc(es, {"futures_session_upl": -0.0002}), -0.000712, places=12)

    def test_open_position_only(self):
        self.assertAlmostEqual(mp.daily_pnl_btc([], {"futures_session_upl": -0.001}), -0.001, places=12)

    def test_unreadable_summary_raises_even_with_good_log(self):
        with self.assertRaises(ValueError):
            mp.daily_pnl_btc([tr(-1e-05)], {})


class RecordedSettlementTests(unittest.TestCase):
    # Expected value from Deribit's equity identity (equity = balance + session_rpl + session_upl), not from repo code.
    # By hand on the recorded 2026-10-10 log: sum(change) of the 3 trades after 08:00Z + session_rpl + session_upl = -6.30e-07 BTC.
    # OURS assumption: session_rpl/upl were 0 right after the 10-10 08:00 settlement.
    @unittest.expectedFailure  # OURS assumption: session_rpl/upl were 0 after the 10-10 08:00 settlement; see settlement-capture-testnet-second-log
    def test_recorded_settlement_identity(self):
        import json
        import os
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "research", "loose_code",
                            "txlog_capture_2026-10-10_jishu_11.json")
        with open(path, encoding="utf-8") as f:
            cap = json.load(f)
        s = cap["account_summary"]
        win = [e for e in cap["entries"] if e["ts_utc"] >= "2026-10-10T08:00:00Z"]
        self.assertEqual(len(win), 3)
        expected = sum(e["change"] for e in win) + s["session_rpl"] + s["session_upl"]
        self.assertAlmostEqual(expected, -6.30e-07, delta=5e-9)
        self.assertAlmostEqual(mp.daily_pnl_btc(win, s), expected, delta=1e-9)


if __name__ == "__main__":
    unittest.main()
