"""
Offline test for the S6 orphan-stop sweep (2026-09-28):

  (a) executor.py: ensure_stop's do.stop_market call raises an
      OrderStateUnknown-style DeribitError AFTER the fake exchange already
      rested the stop order server-side. fail_closed() must sweep that
      order away by cancel_by_label (its order_id was never recorded), not
      just by the id-based cancel it already had.

  (b) position_manager.py: a stop re-place (the stop_state not-live branch
      in manage()) raises the same kind of ambiguous DeribitError after the
      fake already rested the NEW stop order. flatten_halt() must sweep that
      new, unknown-id order away by cancel_by_label too.

Both run the real executor.execute_plan() / position_manager.manage()
against a small fake exchange built in this file, monkeypatched directly
onto the deribit_orders module object (same technique as
test_gh_executor_offline.py) so that `import deribit_orders as do` inside
executor.py / position_manager.py sees the fake without touching their
source.

No network. Run (from a temp dir with the .new files staged to their live
names - see scripts/dev/run_staged_tests.py):
    python3 -m unittest test_s6_orphan_offline -v
"""
import shutil
import unittest

import deribit_orders as do
import journal
import executor
import position_manager as pm


def _order(oid, direction, amount, order_type, label, reduce_only, state, filled=0, avg=80000.0,
          price=None, trigger_price=None):
    return dict(order_id=oid, direction=direction.lower(), amount=amount, order_type=order_type,
                label=label, reduce_only=reduce_only, order_state=state, filled_amount=filled,
                average_price=avg, price=price, trigger_price=trigger_price)


class FakeExchange:
    """Minimal stand-in for the network boundary. Position is the truth,
    same convention as fake_deribit_orders.py / test_gh_executor_offline.py."""

    def __init__(self):
        self.pos = 0
        self.orders = {}
        self.n = 0
        self.mark = 80000.0
        self.cancel_by_label_calls = []
        self.entry_script = None
        # stop_script: None -> stop_market succeeds normally.
        # "ambiguous_rest" -> the fake RESTS the stop order under the given
        # label (so it exists server-side) and THEN raises OrderStateUnknown -
        # exactly the "response lost, order was accepted" case S6 is about.
        self.stop_script = None

    def _new_id(self):
        self.n += 1
        return f"O{self.n}"

    def authenticate(self):
        return "tok"

    def get_ticker(self, instrument="BTC-PERPETUAL"):
        return {"mark_price": self.mark}

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        return {"size": self.pos}

    def get_open_orders(self, token, instrument="BTC-PERPETUAL", type_="all"):
        return [dict(o) for o in self.orders.values() if o["order_state"] in ("open", "untriggered")]

    def get_order_state(self, token, oid):
        return dict(self.orders[oid])

    def _place(self, direction, amount, order_type, label, reduce_only, script):
        if script == "ambiguous_fill":
            oid = self._new_id()
            self.orders[oid] = _order(oid, direction, amount, order_type, label, reduce_only,
                                      "filled", filled=amount)
            self.pos += amount if direction == "BUY" else -amount
            raise do.OrderStateUnknown(f"private/{direction.lower()}", label, 10050)
        if script == "ambiguous_rest":
            oid = self._new_id()
            self.orders[oid] = _order(oid, direction, amount, order_type, label, reduce_only, "open")
            raise do.OrderStateUnknown(f"private/{direction.lower()}", label, 10050)
        oid = self._new_id()
        filled_now = amount if order_type == "market" else 0
        state = "filled" if order_type == "market" else "open"
        self.orders[oid] = _order(oid, direction, amount, order_type, label, reduce_only, state,
                                  filled=filled_now)
        if filled_now:
            self.pos += amount if direction == "BUY" else -amount
        return {"order": self.orders[oid]}

    def buy(self, token, instrument, amount, order_type, price=None, label=None, reduce_only=False, **kw):
        return self._place("BUY", amount, order_type, label, reduce_only, self.entry_script)

    def sell(self, token, instrument, amount, order_type, price=None, label=None, reduce_only=False, **kw):
        return self._place("SELL", amount, order_type, label, reduce_only, self.entry_script)

    def stop_market(self, token, instrument, side, amount, trigger_price, label, trigger="mark_price"):
        if self.stop_script == "ambiguous_rest":
            oid = self._new_id()
            self.orders[oid] = _order(oid, side, amount, "stop_market", label, True, "untriggered",
                                      trigger_price=trigger_price)
            raise do.OrderStateUnknown("private/" + ("sell" if side == "SELL" else "buy"), label, 10050)
        oid = self._new_id()
        self.orders[oid] = _order(oid, side, amount, "stop_market", label, True, "untriggered",
                                  trigger_price=trigger_price)
        return {"order": self.orders[oid]}

    def edit(self, token, oid, amount=None, price=None, trigger_price=None):
        o = self.orders[oid]
        if amount is not None:
            o["amount"] = amount
        return {"order": o}

    def cancel(self, token, oid):
        o = self.orders.get(oid)
        if o is None or o["order_state"] not in ("open", "untriggered"):
            raise do.DeribitError("private/cancel", {"code": 11044, "message": "not_open_order"})
        o["order_state"] = "cancelled"
        return {"order": o}

    def cancel_by_label(self, token, label, currency="BTC"):
        self.cancel_by_label_calls.append(label)
        n = 0
        for o in self.orders.values():
            if o["label"] == label and o["order_state"] in ("open", "untriggered"):
                o["order_state"] = "cancelled"
                n += 1
        return n

    def close_position(self, token, instrument="BTC-PERPETUAL"):
        amt = abs(self.pos)
        self.pos = 0
        oid = self._new_id()
        self.orders[oid] = _order(oid, "SELL", amt, "market", "emergency_close", True, "filled", filled=amt)
        return {"order": self.orders[oid]}


PATCHED_NAMES = ("authenticate", "get_ticker", "get_position", "get_open_orders", "get_order_state",
                 "buy", "sell", "stop_market", "edit", "cancel", "cancel_by_label", "close_position")


def _compiled(plan_id, entry_amount=100, entry_order_type="market", entry_price=None, stop_price=79000.0):
    return {
        "plan_id": plan_id,
        "stop_order": {"side": "SELL", "label": "stop_order", "price": stop_price},
        "caps_check": {"within_max_loss": True, "max_notional_usd": 10_000_000, "max_loss_usd": -1_000_000},
        "max_position_size": entry_amount,
        "entry_orders": [{"side": "BUY", "amount": entry_amount, "order_type": entry_order_type,
                          "price": entry_price, "label": "entry_1"}],
        "target_orders": [],
    }


class PatchedExchangeTestCase(unittest.TestCase):
    def setUp(self):
        self.fake = FakeExchange()
        self._orig = {name: getattr(do, name) for name in PATCHED_NAMES}
        for name in PATCHED_NAMES:
            setattr(do, name, getattr(self.fake, name))
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        executor.HALT_PATH.unlink(missing_ok=True)  # FIX3 M5: fail_closed/flatten_halt now write HALT (sandbox copy)

    def tearDown(self):
        for name, fn in self._orig.items():
            setattr(do, name, fn)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        executor.HALT_PATH.unlink(missing_ok=True)  # FIX3 M5: fail_closed/flatten_halt now write HALT (sandbox copy)


class S6aExecutorOrphanStopTests(PatchedExchangeTestCase):
    """(a) stop_market raises OrderStateUnknown but the fake DID create the
    stop order -> after fail_closed, zero open orders under the plan's labels."""

    def test_orphan_stop_swept_after_ambiguous_replace(self):
        self.fake.entry_script = None            # normal market entry, fills immediately
        self.fake.stop_script = "ambiguous_rest"  # stop IS rested, then raises
        compiled = _compiled("s6a")

        with self.assertRaises(executor.ExecutionHalted):
            executor.execute_plan(compiled)

        expected_label = "s6a:stop_order"
        self.assertIn(expected_label, self.fake.cancel_by_label_calls,
                     "fail_closed must sweep cancel_by_label with the stop's exact plan-scoped label")
        self.assertEqual(self.fake.get_open_orders("t"), [],
                         "the orphaned stop order must be cancelled - zero open orders left behind")
        self.assertEqual(self.fake.pos, 0, "position must be flattened")
        events = journal.read_events("s6a")
        self.assertTrue(any(e["event_type"] == "mismatch_halt" for e in events))
        self.assertTrue(any(e["event_type"] == "order_placed" and e["data"].get("label") == "emergency_close"
                            for e in events))


class S6bPositionManagerOrphanStopTests(PatchedExchangeTestCase):
    """(b) position_manager re-places a stop, the create call raises
    OrderStateUnknown but the fake DID rest the new stop order -> after
    flatten_halt, zero open orders under the plan's labels."""

    def test_orphan_replaced_stop_swept_after_ambiguous_replace(self):
        plan_id = "s6b"
        self.fake.pos = 100  # position already open and filled, as executor would have left it

        entry_oid = self.fake._new_id()
        self.fake.orders[entry_oid] = _order(entry_oid, "BUY", 100, "market", "entry_1", False,
                                             "filled", filled=100)
        old_stop_oid = self.fake._new_id()
        self.fake.orders[old_stop_oid] = _order(old_stop_oid, "SELL", 100, "stop_market", "s6b:stop_order",
                                                True, "cancelled", trigger_price=79000.0)

        journal.append_event(plan_id, "order_placed", {"order_id": entry_oid, "label": "entry_1",
                                                        "side": "BUY", "amount": 100})
        journal.append_event(plan_id, "order_filled", {"order_id": entry_oid, "filled_amount": 100,
                                                        "order_state": "filled"})
        journal.append_event(plan_id, "order_placed", {"order_id": old_stop_oid, "label": "stop_order",
                                                        "side": "SELL", "amount": 100,
                                                        "trigger_price": 79000.0})

        self.fake.stop_script = "ambiguous_rest"  # the re-place call rests a NEW stop, then raises

        with self.assertRaises(pm.ManagerHalted):
            pm.manage(plan_id, once=True, token="t")

        expected_label = "s6b:stop_order"
        self.assertIn(expected_label, self.fake.cancel_by_label_calls,
                     "flatten_halt must sweep cancel_by_label with the stop's exact plan-scoped label")
        self.assertEqual(self.fake.get_open_orders("t"), [],
                         "the orphaned re-placed stop order must be cancelled - zero open orders left behind")
        self.assertEqual(self.fake.pos, 0, "position must be flattened")


if __name__ == "__main__":
    unittest.main()
