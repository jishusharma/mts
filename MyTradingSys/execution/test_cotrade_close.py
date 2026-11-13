"""test_cotrade_close.py - cotrade.close_trade (us_open_trader DESIGN section 5). Fake client only, no network."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cotrade  # noqa: E402
import deribit_orders as do  # noqa: E402
from test_cotrade import Base, FakeClient, SAID  # noqa: E402


class CloseClient(FakeClient):
    """FakeClient whose cancel_by_label can fail and whose close can leave size behind."""
    def __init__(self, *a, cancel_exc=None, close_leaves=0, pos_exc_after_close=False, **kw):
        super().__init__(*a, **kw)
        self.cancel_exc = cancel_exc
        self.close_leaves = close_leaves
        self.pos_exc_after_close = pos_exc_after_close
        self.closed_once = False

    def get_position(self, token, instrument_name="BTC-PERPETUAL"):
        if self.pos_exc_after_close and self.closed_once:
            raise RuntimeError("position api down")
        return super().get_position(token, instrument_name)

    def cancel_by_label(self, token, label, currency="BTC"):
        self.calls.append(("cancel_by_label", label))
        self._see("cancel_by_label")
        if self.cancel_exc:
            raise self.cancel_exc
        self.orders = [o for o in self.orders if o.get("label") != label]
        return 1

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        r = super().close_position(token, instrument_name)
        self.closed_once = True
        if self.close_leaves:
            self.position = self.close_leaves
        return r


class CloseBase(Base):
    def open_trade(self, **kw):
        c = CloseClient(**kw)
        c.halt_path = self.halt
        r = self.run_place(c)
        self.assertTrue(r["ok"], r)
        c.calls.clear()
        return c

    def close(self, c, **kw):
        args = dict(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt, env="test", reason="flat time")
        args.update(kw)
        return cotrade.close_trade(**args)

    def states(self):
        return [x["result"].get("state") for x in self.lines()]


class TestClose(CloseBase):
    def test_happy_path_close_then_cancel_no_halt(self):
        c = self.open_trade()
        r = self.close(c)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["closed_size"], -100)
        self.assertEqual(c.names(), ["authenticate", "close_position", "cancel_by_label"])
        self.assertEqual(c.orders, [])
        self.assertFalse(self.halt.exists())
        self.assertEqual(self.states()[-1], "closed")

    def test_stop_cancelled_only_after_flat(self):
        c = self.open_trade()
        self.close(c)
        self.assertLess(c.names().index("close_position"), c.names().index("cancel_by_label"))

    def test_already_flat_with_leftover_stop(self):
        c = self.open_trade()
        c.position = 0   # server stop filled, the stop order object lingers
        r = self.close(c)
        self.assertTrue(r["ok"])
        self.assertTrue(r["was_flat"])
        self.assertNotIn("close_position", c.names())
        self.assertIn("cancel_by_label", c.names())
        self.assertEqual(c.orders, [])
        self.assertEqual(self.states()[-1], "closed")
        self.assertFalse(self.halt.exists())

    def test_close_raises_flatten_halt_unknown(self):
        c = self.open_trade()
        c.close_exc = RuntimeError("boom")
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertEqual(self.states()[-1], "unknown")
        self.assertIn("cancel_by_label", c.names())   # _flatten_and_halt pattern ran

    def test_position_still_nonzero_after_close(self):
        c = self.open_trade(close_leaves=-40)
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertEqual(self.states()[-1], "unknown")

    def test_position_unreadable_after_close(self):
        c = self.open_trade(pos_exc_after_close=True)
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertEqual(self.states()[-1], "unknown")

    def test_cancel_fails_after_close_is_not_clean(self):
        c = self.open_trade()
        c.cancel_exc = RuntimeError("cancel api down")
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertTrue(r["position_flat"])
        self.assertEqual(c.position, 0)
        self.assertEqual(self.states()[-1], "unknown")
        self.assertFalse(self.halt.exists())
        # not silently clean: a new place is refused by the journal
        c2 = CloseClient()
        r2 = self.run_place(c2)
        self.assertFalse(r2["ok"])
        self.assertNotIn("place", c2.names())
        # re-running close once the API is back reconciles
        c.cancel_exc = None
        self.assertTrue(self.close(c)["ok"])
        self.assertEqual(self.states()[-1], "closed")

    def test_order_state_unknown_never_retried(self):
        c = self.open_trade()
        c.close_exc = do.OrderStateUnknown("private/close", "cotrade", "timeout")
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertEqual(c.names().count("close_position"), 1)
        self.assertNotIn("cancel_by_label", c.names())   # the stop stays
        self.assertTrue(self.halt.exists())
        self.assertEqual(self.states()[-1], "unknown")

    def test_non_testnet_refused_no_calls_nothing_journaled(self):
        c = self.open_trade()
        before = self.lines()
        r = self.close(c, env="live")
        self.assertFalse(r["ok"])
        self.assertEqual(c.calls, [])
        self.assertEqual(self.lines(), before)
        self.assertFalse(self.halt.exists())

    def test_restart_journal_open_exchange_flat(self):
        c = self.open_trade()
        c.position = 0
        c.orders = []
        self.assertEqual(self.states()[-2:], ["placed", "stop_placed"])
        r = self.close(c)   # fresh call = fresh process, journal is the only memory
        self.assertTrue(r["ok"])
        self.assertEqual(self.states()[-1], "closed")

    def test_place_allowed_after_closed(self):
        c = self.open_trade()
        self.assertTrue(self.close(c)["ok"])
        self.assertIsNone(cotrade._unknown_state(cotrade._records(self.jdir)))
        c2 = CloseClient()
        c2.halt_path = self.halt
        r = self.run_place(c2)
        self.assertTrue(r["ok"], r)

    def test_unknown_blocks_place_until_closed(self):
        c = self.open_trade()
        c.close_exc = RuntimeError("boom")
        self.close(c)
        self.halt.unlink()
        self.assertIsNotNone(cotrade._unknown_state(cotrade._records(self.jdir)))

    def test_live_ladder_refused(self):
        c = CloseClient()
        r = cotrade.place_ladder(SAID, "sell", 110500.0, 3, 100, 112000.0, to=111500.0, client=c, account=None,
                                 journal_dir=self.jdir, halt_path=self.halt, halt_daily_loss_path=self.halt_dl,
                                 env="test")
        self.assertTrue(r["ok"], r)
        c.calls.clear()
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertIn("ladder", r["reasons"][0])
        self.assertEqual(c.calls, [])
        self.assertFalse(self.halt.exists())

    def test_no_journal_refused(self):
        c = CloseClient()
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertEqual(c.calls, [])


class TestCloseCli(unittest.TestCase):
    def test_cli_close_registered_empty_journal_exit_1(self):
        with tempfile.TemporaryDirectory() as d:
            os.environ["COTRADE_JOURNAL_DIR"] = d
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    rc = cotrade.main(["close", "--reason", "t"])
            finally:
                os.environ.pop("COTRADE_JOURNAL_DIR", None)
        self.assertEqual(rc, 1)
        self.assertIn("no co-trade order in the journal", json.loads(buf.getvalue())["reasons"][0])


if __name__ == "__main__":
    unittest.main()
