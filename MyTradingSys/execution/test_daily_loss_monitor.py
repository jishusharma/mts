import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from daily_loss_monitor import run_once, ensure_day_state, compute_total_pnl_usd, transaction_log_pnl_btc


class FakeClient:
    """Duck-typed like kill_switch.kill_all's client, plus get_account_summary
    / get_ticker used by daily_loss_monitor."""

    def __init__(self, equity: float, mark_price: float, position_size: int = 0):
        self.equity = equity
        self.mark_price = mark_price
        self._position_size = position_size
        self.kill_all_calls = 0
        self.cancelled = []

    # --- daily_loss_monitor reads ---
    def get_account_summary(self, token, currency="BTC"):
        return {"equity": self.equity, "futures_session_upl": 0.0}

    def get_ticker(self, instrument_name="BTC-PERPETUAL"):
        return {"mark_price": self.mark_price}

    # --- kill_switch.kill_all duck-typed methods ---
    def get_positions(self, token, currency="BTC", kind="future"):
        if self._position_size:
            return [{"instrument_name": "BTC-PERPETUAL", "size": self._position_size}]
        return []

    def get_open_orders(self, token, instrument_name, type_="all"):
        return []

    def cancel(self, token, order_id):
        self.cancelled.append(order_id)
        return {}

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        self.kill_all_calls += 1
        self._position_size = 0
        return {"order": {"order_id": "flat", "filled_amount": 0}}


def _clock_at(iso_str):
    dt = datetime.fromisoformat(iso_str).replace(tzinfo=timezone.utc)
    return lambda: dt


class TestDailyLossMonitor(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_path = Path(self.tmpdir.name) / "state.json"
        self.halt_path = Path(self.tmpdir.name) / "HALT_DAILY_LOSS"

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_no_breach_first_iteration_sets_baseline_and_no_kill(self):
        client = FakeClient(equity=1.0, mark_price=85000.0, position_size=50)
        result = run_once(client, "tok", clock=_clock_at("2026-09-28T00:05:00"),
                           state_path=self.state_path, halt_path=self.halt_path)
        self.assertTrue(result["ok"])
        self.assertEqual(client.kill_all_calls, 0)
        self.assertFalse(self.halt_path.exists())
        self.assertEqual(result["state"]["day_start_equity"], 1.0)

    def test_breach_triggers_kill_once_and_writes_halt_file(self):
        client = FakeClient(equity=1.0, mark_price=85000.0, position_size=50)
        clock = _clock_at("2026-09-28T00:05:00")
        run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)

        # Equity drops enough that equity_delta * mark <= cap (-500 default).
        client.equity = 1.0 - (600.0 / 85000.0)
        result = run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)

        self.assertFalse(result["ok"])
        self.assertEqual(result["action"], "halt_and_flatten_all")
        self.assertEqual(client.kill_all_calls, 1)
        self.assertTrue(self.halt_path.exists())
        halt_data = json.loads(self.halt_path.read_text())
        self.assertEqual(halt_data["date"], "2026-09-28")
        self.assertIn("cap", halt_data["reason"])

        # Second loop iteration same day, still breached: no second kill.
        result2 = run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)
        self.assertFalse(result2["ok"])
        self.assertEqual(client.kill_all_calls, 1, "must not double-kill on repeated breach")

    def test_day_rollover_resets_baseline_and_breach_flag(self):
        client = FakeClient(equity=1.0, mark_price=85000.0, position_size=50)
        day1 = _clock_at("2026-09-28T23:59:00")
        run_once(client, "tok", clock=day1, state_path=self.state_path, halt_path=self.halt_path)
        client.equity = 1.0 - (600.0 / 85000.0)
        breach = run_once(client, "tok", clock=day1, state_path=self.state_path, halt_path=self.halt_path)
        self.assertFalse(breach["ok"])
        self.assertEqual(client.kill_all_calls, 1)

        # New UTC day: baseline resets to today's (already-dropped) equity,
        # so pnl-for-today is back to 0 and breached_today resets too.
        day2 = _clock_at("2026-09-29T00:05:00")
        result = run_once(client, "tok", clock=day2, state_path=self.state_path, halt_path=self.halt_path)
        self.assertTrue(result["ok"])
        self.assertEqual(result["state"]["date"], "2026-09-29")
        self.assertFalse(result["state"]["breached_today"])
        self.assertEqual(client.kill_all_calls, 1, "rollover itself must not trigger a kill")

    def test_ensure_day_state_reuses_same_day_state(self):
        client = FakeClient(equity=2.0, mark_price=90000.0)
        now = _clock_at("2026-09-28T01:00:00")()
        state1 = ensure_day_state(client, "tok", now, state_path=self.state_path)
        from daily_loss_monitor import save_state
        save_state(state1, self.state_path)
        client.equity = 2.5  # would change baseline if re-fetched
        state2 = ensure_day_state(client, "tok", now, state_path=self.state_path)
        self.assertEqual(state2["day_start_equity"], 2.0)

    def test_compute_total_pnl_usd_matches_equity_delta_times_mark(self):
        client = FakeClient(equity=1.01, mark_price=80000.0)
        state = {"day_start_equity": 1.0}
        pnl = compute_total_pnl_usd(client, "tok", state)
        self.assertEqual(pnl, round(0.01 * 80000.0, 2))

    def test_rearm_when_halt_file_cleared_by_operator(self):
        """L6: a genuine re-arm needs BOTH the operator clearing HALT_DAILY_LOSS
        AND equity back within the cap (e.g. position closed out / market
        recovered) - clearing the file alone while still breached must not
        leave the monitor un-halted (see test_rehalt_if_still_breached_after_clear)."""
        client = FakeClient(equity=1.0, mark_price=85000.0, position_size=50)
        clock = _clock_at("2026-09-28T00:05:00")

        # First iteration: set baseline
        run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)

        # Trigger breach
        client.equity = 1.0 - (600.0 / 85000.0)
        result = run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)
        self.assertFalse(result["ok"])
        self.assertTrue(self.halt_path.exists())
        self.assertTrue(result["state"]["breached_today"])
        self.assertEqual(client.kill_all_calls, 1)

        # Operator clears the HALT file AND equity has recovered back within
        # cap (position flattened / market moved back) - a genuine re-arm.
        self.halt_path.unlink()
        self.assertFalse(self.halt_path.exists())
        client.equity = 1.0

        # Now run_once should detect breached_today=True and halt_path absent,
        # re-arm (set breached_today=False), and since equity is back within
        # cap it must NOT immediately re-halt.
        result = run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)
        self.assertTrue(result["ok"], "equity is back within cap, monitor must not re-halt")
        self.assertFalse(result["state"]["breached_today"], "breached_today should be re-armed to False")
        self.assertFalse(self.halt_path.exists(), "must not rewrite HALT file when not breached")
        self.assertEqual(client.kill_all_calls, 1, "recovered equity must not trigger another kill")

    def test_rehalt_if_still_breached_after_clear(self):
        """L6: operator clears HALT_DAILY_LOSS but equity is still below the
        cap (e.g. position not actually closed) - the monitor must re-arm and
        then immediately re-detect the breach and halt again. Guards must
        never leave the account unprotected just because the file was
        cleared (Lesson B: never stand down the protective halt on a
        technicality)."""
        client = FakeClient(equity=1.0, mark_price=85000.0, position_size=50)
        clock = _clock_at("2026-09-28T00:05:00")

        run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)

        client.equity = 1.0 - (600.0 / 85000.0)
        result = run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)
        self.assertFalse(result["ok"])
        self.assertEqual(client.kill_all_calls, 1)

        # Operator clears the file, but equity is still breached (e.g. the
        # position was reopened, or exposure otherwise persists).
        self.halt_path.unlink()
        client._position_size = 50

        result = run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)
        self.assertFalse(result["ok"], "still below cap - must re-halt")
        self.assertTrue(result["state"]["breached_today"])
        self.assertTrue(self.halt_path.exists(), "HALT file must be rewritten")
        self.assertEqual(client.kill_all_calls, 2, "must kill again on genuine re-breach")

    def test_no_rearm_while_halt_file_exists(self):
        """No re-arm when HALT file still exists, even if breached_today=True"""
        client = FakeClient(equity=1.0, mark_price=85000.0, position_size=50)
        clock = _clock_at("2026-09-28T00:05:00")

        # First iteration: set baseline
        run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)

        # Trigger breach
        client.equity = 1.0 - (600.0 / 85000.0)
        result = run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)
        self.assertTrue(self.halt_path.exists())
        self.assertTrue(result["state"]["breached_today"])

        # Run_once again while halt file still exists
        result = run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)
        # breached_today should remain True (no re-arm while file exists)
        self.assertTrue(result["state"]["breached_today"], "breached_today should not be re-armed while HALT file exists")


class TxLogClient(FakeClient):
    """L6 part 2: mainnet-style client - active_env()=='mainnet' selects the transaction-log source."""

    def __init__(self, logs, **kw):
        super().__init__(**kw)
        self.logs = logs
        self.tx_calls = []

    def active_env(self):
        return "mainnet"

    def get_transaction_log(self, token, currency="BTC", start_ms=0, end_ms=0):
        self.tx_calls.append((start_ms, end_ms))
        return self.logs


class TestTransactionLogSource(unittest.TestCase):
    STATE = {"date": "2026-09-28", "day_start_equity": 1.0}

    def test_excludes_only_money_movement_types(self):
        logs = [{"type": "trade", "change": -0.001}, {"type": "settlement", "change": -0.0005},
                {"type": "transfer", "change": 5.0}, {"type": "transfer_out", "change": -2.0},
                {"type": "deposit", "change": 1.0}, {"type": "withdrawal", "change": -1.0}]
        self.assertAlmostEqual(transaction_log_pnl_btc(logs), -0.0015)

    def test_mainnet_client_uses_log_not_equity(self):
        # equity moved +100 BTC (a deposit); the log says only -0.01 BTC of trading P/L
        c = TxLogClient([{"type": "trade", "change": -0.01}, {"type": "deposit", "change": 100.0}],
                        equity=101.0, mark_price=80000.0)
        pnl = compute_total_pnl_usd(c, "tok", self.STATE, now_ms=1_800_000_000_000)
        self.assertEqual(pnl, -800.0)
        start_ms = int(datetime(2026, 9, 28, tzinfo=timezone.utc).timestamp() * 1000)
        self.assertEqual(c.tx_calls, [(start_ms, 1_800_000_000_000)])

    def test_testnet_default_stays_equity(self):
        c = FakeClient(equity=1.01, mark_price=80000.0)  # no active_env / get_transaction_log
        self.assertEqual(compute_total_pnl_usd(c, "tok", self.STATE), 800.0)

    def test_missing_change_fails_closed(self):
        with self.assertRaises(ValueError):
            transaction_log_pnl_btc([{"type": "trade"}])

    def test_bad_source_rejected(self):
        with self.assertRaises(ValueError):
            compute_total_pnl_usd(FakeClient(1.0, 1.0), "tok", self.STATE, pnl_source="bogus")

    def test_deposit_does_not_mask_or_fake_breach_in_run_once(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        sp, hp = Path(tmp.name) / "s.json", Path(tmp.name) / "HALT_DAILY_LOSS"
        c = TxLogClient([{"type": "trade", "change": -0.001}, {"type": "transfer", "change": -50.0}],
                        equity=1.0, mark_price=80000.0, position_size=10)
        r = run_once(c, "tok", clock=_clock_at("2026-09-28T01:00:00"), state_path=sp, halt_path=hp)
        self.assertTrue(r["ok"])  # -80 USD trading loss; the -50 BTC transfer is ignored
        c.logs = [{"type": "trade", "change": -0.01}]
        r = run_once(c, "tok", clock=_clock_at("2026-09-28T01:01:00"), state_path=sp, halt_path=hp)
        self.assertFalse(r["ok"])
        self.assertEqual(c.kill_all_calls, 1)
        self.assertTrue(hp.exists())


class TestHelpText(unittest.TestCase):
    def test_pnl_source_help_matches_default_pnl_source(self):
        # B149: default_pnl_source picks transaction_log on testnet too when the client can read the log
        import contextlib
        import io
        import daily_loss_monitor as dlm
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit):
            dlm.main(["--help"])
        text = " ".join(buf.getvalue().split())
        self.assertNotIn("equity on testnet", text)
        self.assertIn("transaction_log", text)


if __name__ == "__main__":
    unittest.main()
