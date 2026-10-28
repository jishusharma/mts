import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from daily_loss_monitor import run_once, default_pnl_source
from test_daily_loss_monitor import FakeClient


class TestnetLogClient(FakeClient):
    """Testnet-style client (no active_env) that can read the transaction log."""
    def __init__(self, logs, **kw):
        super().__init__(**kw)
        self.logs = logs

    def get_account_summary(self, token, currency="BTC"):
        return {"equity": self.equity, "futures_session_upl": 0.0}

    def get_transaction_log(self, token, currency="BTC", start_ms=0, end_ms=0):
        return self.logs

    def kill_all_marker(self):
        return self.kill_all_calls


def _clock():
    return lambda: datetime(2026, 9, 29, 8, 54, tzinfo=timezone.utc)


class TestTestnetTransfersNotPnl(unittest.TestCase):
    def test_transfer_out_no_trades_no_halt(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        sp, hp = Path(tmp.name) / "s.json", Path(tmp.name) / "HALT_DAILY_LOSS"
        c = TestnetLogClient([], equity=100.0, mark_price=83810.0)
        self.assertTrue(run_once(c, "t", clock=_clock(), state_path=sp, halt_path=hp)["ok"])
        c.equity = 60.0
        c.logs = [{"type": "transfer", "change": -40.0}, {"type": "transfer_subaccount", "change": -10.0}]
        r = run_once(c, "t", clock=_clock(), state_path=sp, halt_path=hp)
        self.assertTrue(r["ok"])
        self.assertEqual(r["total_pnl_usd"], 0.0)
        self.assertFalse(hp.exists())
        self.assertEqual(c.kill_all_calls, 0)

    def test_default_source_uses_log_when_available(self):
        self.assertEqual(default_pnl_source(TestnetLogClient([], equity=1.0, mark_price=1.0)), "transaction_log")
        self.assertEqual(default_pnl_source(FakeClient(1.0, 1.0)), "equity")


if __name__ == "__main__":
    unittest.main()
