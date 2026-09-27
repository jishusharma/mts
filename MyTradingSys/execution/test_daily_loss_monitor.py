import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from daily_loss_monitor import run_once, ensure_day_state, compute_total_pnl_usd


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
        return {"equity": self.equity}

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


if __name__ == "__main__":
    unittest.main()
