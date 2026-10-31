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
    # Expected values come from Deribit's equity identity (equity = balance + session_rpl + session_upl) and
    # hand arithmetic on the recorded logs, not from repo code. session_rpl restarts only at a settlement entry
    # (the 2026-10-10 08:00Z capture has none), so the identity window is the entries strictly AFTER the last
    # settlement (2026-10-09T08:00:00Z, 36h before the capture); the settlement entry itself belongs to the old session.
    LAST_SETTLEMENT = "2026-10-09T08:00:00Z"

    @staticmethod
    def _load(name):
        import json
        import os
        # run_staged_tests copies this file to a temp dir and sets MTS_REPO_ROOT; fall back to the checkout layout.
        root = os.environ.get("MTS_REPO_ROOT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
        path = os.path.join(root, "MyTradingSys", "research", "loose_code", name)
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def test_recorded_settlement_identity(self):
        cap = self._load("txlog_capture_2026-10-10_jishu_11.json")
        s = cap["account_summary"]
        last = max(e["ts_utc"] for e in cap["entries"] if e["type"] == "settlement")
        self.assertEqual(last, self.LAST_SETTLEMENT)
        win = [e for e in cap["entries"] if e["ts_utc"] > last]
        self.assertEqual(len(win), 11)
        # By hand: 8 trades x -6.1e-07 + 3 trades x -6e-07 = -6.68e-06 (change); session_rpl +1.17e-06; upl 0.
        expected = -6.68e-06 + 1.17e-06
        self.assertAlmostEqual(sum(e["change"] for e in win) + s["session_rpl"] + s["session_upl"], expected, delta=1e-12)
        # Cashflow on the profit_as_cashflow trades: -4e-08+4.7e-06-8.2e-07+9.9e-07-3.05e-06-6e-07 = +1.18e-06
        # vs session_rpl +1.17e-06 (summary rounded to 1e-8).
        self.assertAlmostEqual(sum(e["cashflow"] for e in win if e["profit_as_cashflow"] is True), 1.18e-06, delta=1e-12)
        # Tolerance moved from 1e-9 to 2e-8 because session_rpl in the summary is rounded to 1e-8.
        self.assertAlmostEqual(mp.daily_pnl_btc(win, s), expected, delta=2e-8)

    def test_wrong_short_window_is_not_the_identity(self):
        # The old 4h slice (>= 2026-10-10T08:00Z, 3 trades) misses the session_rpl built up since the 10-09 settlement.
        cap = self._load("txlog_capture_2026-10-10_jishu_11.json")
        s = cap["account_summary"]
        win = [e for e in cap["entries"] if e["ts_utc"] >= "2026-10-10T08:00:00Z"]
        self.assertEqual(len(win), 3)
        expected = sum(e["change"] for e in win) + s["session_rpl"] + s["session_upl"]
        self.assertGreater(abs(mp.daily_pnl_btc(win, s) - expected), 4e-06)

    def test_same_day_trade_then_settlement_is_not_double_counted(self):
        # Item 2 part 2 (recorded): 07:31Z opener (cashflow 0), 08:00Z settlement -1.59e-06, then the 36h trades.
        # Equity change over the window by hand: change -6.1e-07 (07:31) -1.59e-06 (settlement) -6.68e-06 (later trades)
        # + session_rpl 1.17e-06 + upl 0 = -7.71e-06. realized_btc counts the settlement by change only.
        cap = self._load("txlog_capture_2026-10-10_jishu_11.json")
        s = cap["account_summary"]
        win = [e for e in cap["entries"] if e["ts_utc"] >= "2026-10-09T00:00:00Z"]
        self.assertEqual(len(win), 13)
        self.assertAlmostEqual(mp.daily_pnl_btc(win, s), -7.71e-06, delta=2e-8)

    def test_settlement_entry_does_not_add_its_cashflow_again(self):
        # SYNTHETIC (not a recorded entry): fail closed on the shape that would double count, a settlement carrying profit_as_cashflow True.
        e = {"type": "settlement", "change": -1.59e-06, "cashflow": -1.59e-06, "profit_as_cashflow": True}
        self.assertAlmostEqual(mp.realized_btc([e]), -1.59e-06, places=12)

    def test_recorded_log_missing_change_in_window_raises(self):
        cap = self._load("txlog_capture_2026-10-10_jishu_11.json")
        win = [dict(e) for e in cap["entries"] if e["ts_utc"] > self.LAST_SETTLEMENT]
        del win[3]["change"]
        with self.assertRaises(ValueError):
            mp.realized_btc(win)

    def test_non_trade_balance_moves_inside_window_are_ignored(self):
        cap = self._load("txlog_capture_2026-10-10_jishu_11.json")
        s = cap["account_summary"]
        win = [e for e in cap["entries"] if e["ts_utc"] > self.LAST_SETTLEMENT]
        noise = [{"type": "deposit", "change": 0.5, "ts_utc": "2026-10-09T12:00:00Z"},
                 {"type": "withdrawal", "change": -0.2, "ts_utc": "2026-10-09T13:00:00Z"}]
        self.assertAlmostEqual(mp.daily_pnl_btc(win + noise, s), mp.daily_pnl_btc(win, s), places=12)


if __name__ == "__main__":
    unittest.main()
