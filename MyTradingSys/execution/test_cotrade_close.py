"""test_cotrade_close.py - cotrade.close_trade (us_open_trader DESIGN V2-7) and ensure_stop V2-6 (default stop,
never loosen). Fake client only, no network, no secrets. Expectations come from the V2 rule text."""
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

WRITES = {"place", "stop_market", "cancel", "cancel_by_label", "close_position"}


class CloseClient(FakeClient):
    """FakeClient whose cancel_by_label really removes labelled orders and can fail / be a no-op, whose close can
    leave size behind, and whose close_position can raise while the position nevertheless ends flat."""
    def __init__(self, *a, cancel_exc=None, cancel_noop=False, close_leaves=0, pos_exc_after_close=False,
                 close_raises_but_flat=False, orders_exc=False, **kw):
        super().__init__(*a, **kw)
        self.cancel_exc = cancel_exc
        self.cancel_noop = cancel_noop
        self.close_leaves = close_leaves
        self.pos_exc_after_close = pos_exc_after_close
        self.close_raises_but_flat = close_raises_but_flat
        self.orders_exc = orders_exc
        self.closed_once = False
        self.cancelled = False

    def get_position(self, token, instrument_name="BTC-PERPETUAL"):
        if self.pos_exc_after_close and self.closed_once:
            raise RuntimeError("position api down")
        return super().get_position(token, instrument_name)

    def get_open_orders(self, token, instrument_name="BTC-PERPETUAL", type_="all"):
        if self.orders_exc and self.cancelled:
            raise RuntimeError("orders api down")
        return super().get_open_orders(token, instrument_name, type_)

    def cancel_by_label(self, token, label, currency="BTC"):
        self.calls.append(("cancel_by_label", label))
        self._see("cancel_by_label")
        self.cancelled = True
        if self.cancel_exc:
            raise self.cancel_exc
        if not self.cancel_noop:
            self.orders = [o for o in self.orders if o.get("label") != label]
        return 1

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        self.closed_once = True
        if self.close_raises_but_flat:
            self.calls.append(("close_position",))
            self.position = 0
            raise self.close_exc or RuntimeError("reduce_only rejected: position is 0")
        r = super().close_position(token, instrument_name)
        if self.close_leaves:
            self.position = self.close_leaves
        return r


class MultiClient(CloseClient):
    """One token per account; `other` maps an account name to its position size."""
    def __init__(self, *a, other=None, **kw):
        super().__init__(*a, **kw)
        self.other = other or {}

    def authenticate(self, account=None):
        self.calls.append(("authenticate", account))
        return f"tok:{account}"

    def get_position(self, token, instrument_name="BTC-PERPETUAL"):
        name = token[4:]
        if name in self.other:
            return {"size": self.other[name]}
        return super().get_position(token, instrument_name)


class CloseBase(Base):
    def open_trade(self, cls=CloseClient, **kw):
        c = cls(**kw)
        c.halt_path = self.halt
        r = self.run_place(c)
        self.assertTrue(r["ok"], r)
        c.calls.clear()
        return c

    def close(self, c, **kw):
        args = dict(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt, env="test", reason="flat time",
                    secret_exists=lambda a: False)
        args.update(kw)
        return cotrade.close_trade(**args)

    def states(self):
        return [x["result"].get("state") for x in self.lines()]

    def add(self, kind, state, account="main", **action):
        cotrade._append(self.jdir, {"said": SAID, "heard": "t", "env": "test", "account": account, "market": {},
                                    "action": {"kind": kind, **action}, "result": {"state": state}})

    def assert_refused_reads_only(self, c, r, word):
        self.assertFalse(r["ok"])
        self.assertIn(word, r["reasons"][0])
        self.assertEqual([n for n in c.names() if n in WRITES], [])
        self.assertEqual(self.states()[-1], "refused")
        self.assertFalse(self.halt.exists())


class TestClose(CloseBase):
    def test_happy_path_close_then_cancel_no_halt(self):
        c = self.open_trade()
        r = self.close(c)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["closed_size"], -100)
        self.assertFalse(r["was_flat"])
        self.assertEqual([n for n in c.names() if n in WRITES], ["close_position", "cancel_by_label"])
        self.assertEqual(c.orders, [])
        self.assertFalse(self.halt.exists())   # a normal close writes NO HALT
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

    def test_close_raises_position_open_flatten_halt_unknown(self):
        c = self.open_trade()
        c.close_exc = RuntimeError("boom")
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertTrue(self.halt.exists())
        self.assertEqual(self.states()[-1], "unknown")
        self.assertIn("cancel_by_label", c.names())   # _flatten_and_halt ran
        self.assertEqual(c.names().count("close_position"), 2)   # close + the flatten's own close

    def test_close_raises_but_position_flat_continues_no_halt(self):
        c = self.open_trade(close_raises_but_flat=True)   # stop filled in the race before close_position
        r = self.close(c)
        self.assertTrue(r["ok"], r)
        self.assertFalse(self.halt.exists())
        self.assertEqual(c.names().count("close_position"), 1)
        self.assertEqual(self.states()[-1], "closed")
        self.assertIn("cancel_by_label", c.names())

    def test_order_state_unknown_position_still_open_halt_never_resent(self):
        c = self.open_trade()
        c.close_exc = do.OrderStateUnknown("private/close", "cotrade", "timeout")
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertEqual(c.names().count("close_position"), 1)
        self.assertNotIn("cancel_by_label", c.names())   # the server stop stays
        self.assertTrue(self.halt.exists())
        self.assertEqual(self.states()[-1], "unknown")

    def test_order_state_unknown_but_position_flat_continues_no_halt(self):
        c = self.open_trade(close_raises_but_flat=True)
        c.close_exc = do.OrderStateUnknown("private/close", "cotrade", "timeout")
        r = self.close(c)
        self.assertTrue(r["ok"], r)
        self.assertFalse(self.halt.exists())
        self.assertEqual(self.states()[-1], "closed")

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

    def test_cancel_raises_after_flat_is_closed_cancel_failed_no_halt(self):
        c = self.open_trade()
        c.cancel_exc = RuntimeError("cancel api down")
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertTrue(r["position_flat"])
        self.assertEqual(c.position, 0)
        self.assertEqual(self.states()[-1], "closed_cancel_failed")
        self.assertFalse(self.halt.exists())

    def test_labelled_order_still_open_after_cancel_is_closed_cancel_failed(self):
        c = self.open_trade(cancel_noop=True)
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertEqual(self.states()[-1], "closed_cancel_failed")
        self.assertFalse(self.halt.exists())

    def test_open_orders_unreadable_after_cancel_is_closed_cancel_failed(self):
        c = self.open_trade(orders_exc=True)
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertEqual(self.states()[-1], "closed_cancel_failed")
        self.assertFalse(self.halt.exists())

    def test_closed_cancel_failed_blocks_place_and_rerun_reconciles(self):
        c = self.open_trade()
        c.cancel_exc = RuntimeError("cancel api down")
        self.close(c)
        self.assertIsNotNone(cotrade._unknown_state(cotrade._records(self.jdir)))
        c2 = CloseClient()
        r2 = self.run_place(c2)
        self.assertFalse(r2["ok"])
        self.assertNotIn("place", c2.names())
        c.cancel_exc = None   # API is back: the re-run reconciles
        r3 = self.close(c)
        self.assertTrue(r3["ok"], r3)
        self.assertEqual(self.states()[-1], "closed")
        self.assertIsNone(cotrade._unknown_state(cotrade._records(self.jdir)))

    def test_non_testnet_refused_zero_calls_nothing_journaled_no_halt(self):
        c = self.open_trade()
        before = self.lines()
        r = self.close(c, env="live")
        self.assertFalse(r["ok"])
        self.assertEqual(c.calls, [])
        self.assertEqual(self.lines(), before)
        self.assertFalse(self.halt.exists())

    def test_non_testnet_fresh_journal_dir_not_even_created(self):
        c = CloseClient()
        r = self.close(c, env="mainnet")
        self.assertFalse(r["ok"])
        self.assertEqual(c.calls, [])
        self.assertFalse(self.jdir.exists())
        self.assertFalse(self.halt.exists())

    def test_restart_journal_open_exchange_flat(self):
        c = self.open_trade()
        c.position = 0
        c.orders = []
        self.assertEqual(self.states()[-2:], ["placed", "stop_placed"])
        r = self.close(c)   # fresh call = fresh process, the journal is the only memory
        self.assertTrue(r["ok"])
        self.assertTrue(r["was_flat"])
        self.assertEqual(self.states()[-1], "closed")

    def test_place_allowed_after_closed(self):
        c = self.open_trade()
        self.assertTrue(self.close(c)["ok"])
        self.assertIsNone(cotrade._unknown_state(cotrade._records(self.jdir)))
        c2 = CloseClient()
        c2.halt_path = self.halt
        r = self.run_place(c2)
        self.assertTrue(r["ok"], r)

    def test_no_journal_refused(self):
        c = CloseClient()
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertEqual(c.calls, [])


class TestCloseRefusals(CloseBase):
    def test_live_ladder_refused(self):
        c = CloseClient()
        r = cotrade.place_ladder(SAID, "sell", 110500.0, 3, 100, 112000.0, to=111500.0, client=c, account=None,
                                 journal_dir=self.jdir, halt_path=self.halt, halt_daily_loss_path=self.halt_dl,
                                 env="test")
        self.assertTrue(r["ok"], r)
        c.calls.clear()
        self.assert_refused_reads_only(c, self.close(c), "ladder")

    def test_ladder_stopped_but_last_place_is_a_ladder_refused(self):
        c = CloseClient()
        r = cotrade.place_ladder(SAID, "sell", 110500.0, 3, 100, 112000.0, to=111500.0, client=c, account=None,
                                 journal_dir=self.jdir, halt_path=self.halt, halt_daily_loss_path=self.halt_dl,
                                 env="test")
        self.assertTrue(r["ok"], r)
        self.add("ladder_sync", "ladder_stopped")
        self.assertIsNone(cotrade._unknown_state(cotrade._records(self.jdir)))   # reconciled, yet still a ladder
        c.calls.clear()
        self.assert_refused_reads_only(c, self.close(c), "ladder")

    def test_hedge_lineage_refused_even_when_hedge_stop_placed(self):
        c = self.open_trade()
        self.add("hedge", "hedge_pending", account="jishu_1", side="buy")
        self.add("hedge", "hedge_placed", account="jishu_1", side="buy")
        self.add("stop", "stop_placed", account="jishu_1", stop=104000.0)   # hides the hedge from _unknown_state
        self.assertIsNone(cotrade._unknown_state(cotrade._records(self.jdir)))
        self.assert_refused_reads_only(c, self.close(c), "hedge")

    def test_half_placed_hedge_refused(self):
        c = self.open_trade()
        self.add("hedge", "hedge_pending", account="jishu_1", side="buy")
        self.assert_refused_reads_only(c, self.close(c), "kill")

    def test_unknown_in_flight_refused(self):
        c = self.open_trade()
        self.add("place", "unknown", side="sell")
        self.assert_refused_reads_only(c, self.close(c), "unknown")

    def test_unknown_before_closed_cancel_failed_still_refused(self):
        c = self.open_trade()
        self.add("place", "unknown", side="sell")
        self.add("close", "closed_cancel_failed")
        r = self.close(c)
        self.assertFalse(r["ok"])
        self.assertEqual([n for n in c.names() if n in WRITES], [])

    def test_other_slot_with_position_refused(self):
        c = self.open_trade(MultiClient, other={"jishu_1": 50})
        r = self.close(c, secret_exists=lambda a: a == "jishu_1")
        self.assert_refused_reads_only(c, r, "another co-trade slot")
        self.assertEqual(c.position, -100)

    def test_other_slot_flat_does_not_block(self):
        c = self.open_trade(MultiClient, other={"jishu_1": 0})
        r = self.close(c, secret_exists=lambda a: a == "jishu_1")
        self.assertTrue(r["ok"], r)

    def test_other_slot_unreadable_refused(self):
        class Bad(MultiClient):
            def get_position(self, token, instrument_name="BTC-PERPETUAL"):
                if token == "tok:jishu_1":
                    raise RuntimeError("down")
                return super().get_position(token, instrument_name)
        c = self.open_trade(Bad)
        r = self.close(c, secret_exists=lambda a: a == "jishu_1")
        self.assertFalse(r["ok"])
        self.assertEqual([n for n in c.names() if n in WRITES], [])
        self.assertFalse(self.halt.exists())


class TestEnsureStopV2(CloseBase):
    def stop(self, c, **kw):
        args = dict(client=c, account=None, journal_dir=self.jdir, halt_path=self.halt, env="test")
        args.update(kw)
        return cotrade.ensure_stop(**args)

    def set_live_stop(self, c, trigger):
        for o in c.orders:
            o["trigger_price"] = trigger

    def test_break_even_stop_untouched_by_default_call(self):
        c = self.open_trade()   # short -100, journaled stop 111000
        self.set_live_stop(c, 110500.0)   # moved to break-even: lower = tighter for a short
        before = [dict(o) for o in c.orders]
        r = self.stop(c)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["note"], "kept tighter stop")
        self.assertEqual([n for n in c.names() if n in WRITES], [])
        self.assertEqual(c.orders, before)
        self.assertFalse(self.halt.exists())
        self.assertEqual(self.states()[-1], "stop_placed")   # nothing new journaled

    def test_explicit_looser_stop_ignored_short(self):
        c = self.open_trade()
        self.set_live_stop(c, 110500.0)
        r = self.stop(c, stop_px=111500.0)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["note"], "kept tighter stop")
        self.assertEqual([n for n in c.names() if n in WRITES], [])
        self.assertEqual(c.orders[0]["trigger_price"], 110500.0)

    def test_explicit_looser_stop_ignored_long(self):
        c = CloseClient()
        c.halt_path = self.halt
        self.assertTrue(self.run_place(c, side="buy", stop=110000.0)["ok"])   # long 100, stop 110000
        c.calls.clear()
        self.set_live_stop(c, 110200.0)   # higher = tighter for a long
        r = self.stop(c, stop_px=109500.0)
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["note"], "kept tighter stop")
        self.assertEqual([n for n in c.names() if n in WRITES], [])
        self.assertEqual(c.orders[0]["trigger_price"], 110200.0)

    def test_explicit_tighter_stop_replaces_loose_one(self):
        c = self.open_trade()   # live 111000
        r = self.stop(c, stop_px=110800.0)   # lower = tighter for the short: allowed
        self.assertTrue(r["ok"], r)
        self.assertEqual([o["trigger_price"] for o in c.orders], [110800.0])
        self.assertIn("stop_market", c.names())

    def test_tighter_stop_with_wrong_size_is_resized_never_loosened(self):
        c = self.open_trade()
        self.set_live_stop(c, 110500.0)
        c.orders[0]["amount"] = 40   # tighter but covers only 40 of 100
        r = self.stop(c)
        self.assertTrue(r["ok"], r)
        self.assertEqual([(o["amount"], o["trigger_price"]) for o in c.orders], [(100, 110500.0)])
        self.assertEqual([x for x in c.calls if x[0] == "stop_market"][0][3], 110500.0)

    def test_default_stop_is_newest_journaled_stop(self):
        c = self.open_trade()
        self.assertTrue(self.stop(c, stop_px=110800.0)["ok"])   # journals stop_placed 110800
        c.orders = []   # stop lost on the exchange
        c.calls.clear()
        r = self.stop(c)
        self.assertTrue(r["ok"], r)
        self.assertEqual([x for x in c.calls if x[0] == "stop_market"][0][3], 110800.0)   # not the place action's 111000

    def test_default_stop_ignores_other_account_and_older_lineage(self):
        c = self.open_trade()
        self.add("stop", "stop_placed", account="jishu_1", stop=105000.0)   # a hedge leg's stop: not ours
        c.orders = []
        c.calls.clear()
        r = self.stop(c)
        self.assertTrue(r["ok"], r)
        self.assertEqual([x for x in c.calls if x[0] == "stop_market"][0][3], 111000.0)

    def test_default_stop_falls_back_to_place_stop(self):
        c = CloseClient(position=-100)
        cotrade._append(self.jdir, {"said": SAID, "heard": "t", "env": "test", "account": "main", "market": {},
                                    "action": {"kind": "place", "side": "sell", "stop": 111000.0},
                                    "result": {"state": "placed"}})
        r = self.stop(c)
        self.assertTrue(r["ok"], r)
        self.assertEqual([x for x in c.calls if x[0] == "stop_market"][0][3], 111000.0)

    def test_old_lineage_stop_not_reused_after_new_place(self):
        c = self.open_trade()
        self.stop(c, stop_px=110800.0)
        self.assertTrue(self.close(c)["ok"])
        c2 = CloseClient()
        c2.halt_path = self.halt
        self.assertTrue(self.run_place(c2, stop=111200.0)["ok"])   # new lineage, stop 111200
        c2.orders = []
        c2.calls.clear()
        self.assertTrue(self.stop(c2)["ok"])
        self.assertEqual([x for x in c2.calls if x[0] == "stop_market"][0][3], 111200.0)


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
