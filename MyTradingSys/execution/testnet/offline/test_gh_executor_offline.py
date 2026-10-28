"""
Offline test for the G-h executor-side fix (2026-09-28 follow-up):

  (1) deribit_orders.OrderStateUnknown now subclasses DeribitError, so every
      existing `except do.DeribitError` handler in executor.py routes it into
      fail_closed instead of crashing past it.
  (2) executor.py's fail_closed() now sweeps do.cancel_by_label(...) for every
      compiled entry label, because an entry whose create call raised
      OrderStateUnknown has no order_id in `entries` but may be resting.

Runs executor.py's REAL execute_plan() against a minimal fake exchange built
in this file (fake_deribit_orders.py.new has no buy/sell/cancel_by_label/
OrderStateUnknown, so it can't stand in for deribit_orders here). The fake is
installed by monkeypatching attributes directly on the real, G-h-fixed
deribit_orders module - executor's `import deribit_orders as do` binds to
that same module object, so patching its attributes is visible through `do.*`
inside executor without touching executor's source.

No network. Run from a temp copy (deribit_orders.py.new / executor.py.new /
plan_compiler.py.new stripped to .py, journal.py copied as-is) with:
    python3 -m unittest test_gh_executor_offline -v
"""
import shutil
import unittest
from pathlib import Path

import deribit_orders as do
import journal
import executor


def _order(oid, direction, amount, order_type, label, reduce_only, state, filled=0, avg=80000.0,
          price=None, trigger_price=None):
    return dict(order_id=oid, direction=direction.lower(), amount=amount, order_type=order_type,
                label=label, reduce_only=reduce_only, order_state=state, filled_amount=filled,
                average_price=avg, price=price, trigger_price=trigger_price)


class FakeExchange:
    """Minimal stand-in for the network boundary. Position is the truth,
    same convention as fake_deribit_orders.py.new."""

    def __init__(self):
        self.pos = 0
        self.orders = {}
        self.n = 0
        self.mark = 80000.0
        self.cancel_by_label_calls = []
        # scripted per-scenario behaviour for the entry-creating call:
        #   None            -> create normally (filled immediately, market)
        #   "ambiguous_fill" -> fill the position behind the scenes, then raise
        #                       OrderStateUnknown (response lost, order WAS accepted+filled)
        #   "ambiguous_rest" -> leave a resting open order under the label, then raise
        #                       OrderStateUnknown (response lost, order WAS accepted, unfilled)
        self.entry_script = None
        self.stop_script = None

    def _new_id(self):
        self.n += 1
        return f"O{self.n}"

    # ---- patched onto the deribit_orders module ----
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
        # normal path: market entries fill immediately (matches real Deribit market-order behaviour)
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
        if self.stop_script == "ambiguous":
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


def _compiled(plan_id, entry_amount=100, entry_order_type="market", entry_price=None,
             stop_price=79000.0):
    return {
        "plan_id": plan_id,
        "stop_order": {"side": "SELL", "label": "stop_order", "price": stop_price},
        "caps_check": {"within_max_loss": True, "max_notional_usd": 10_000_000, "max_loss_usd": -1_000_000},
        "max_position_size": entry_amount,
        "entry_orders": [{"side": "BUY", "amount": entry_amount, "order_type": entry_order_type,
                          "price": entry_price, "label": "entry_1"}],
    }


class GhExecutorOfflineTests(unittest.TestCase):
    def setUp(self):
        self.fake = FakeExchange()
        self._orig = {name: getattr(do, name) for name in PATCHED_NAMES}
        for name in PATCHED_NAMES:
            setattr(do, name, getattr(self.fake, name))
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        executor.HALT_PATH.unlink(missing_ok=True)  # FIX3 M5: fail_closed now writes HALT (sandbox copy)

    def tearDown(self):
        for name, fn in self._orig.items():
            setattr(do, name, fn)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        executor.HALT_PATH.unlink(missing_ok=True)  # FIX3 M5: fail_closed now writes HALT (sandbox copy)

    # A: market entry create raises OrderStateUnknown but the fake DID fill the position.
    def test_a_market_entry_ambiguous_but_filled_flattens_and_halts(self):
        self.fake.entry_script = "ambiguous_fill"
        compiled = _compiled("gh_a")

        with self.assertRaises(executor.ExecutionHalted):
            executor.execute_plan(compiled)

        self.assertEqual(self.fake.pos, 0, "position must be flattened to zero")
        events = journal.read_events("gh_a")
        self.assertTrue(any(e["event_type"] == "mismatch_halt" for e in events),
                        "journal must record a mismatch_halt")
        self.assertTrue(any(e["event_type"] == "order_placed" and e["data"].get("label") == "emergency_close"
                            for e in events), "close_position must have been journaled")

    # B: limit entry create raises OrderStateUnknown, fake left a resting order under that label.
    def test_b_limit_entry_ambiguous_resting_order_gets_cancelled_by_label(self):
        self.fake.entry_script = "ambiguous_rest"
        compiled = _compiled("gh_b", entry_order_type="limit", entry_price=50000.0)

        with self.assertRaises(executor.ExecutionHalted):
            executor.execute_plan(compiled)

        expected_label = f"gh_b:entry_1"
        self.assertIn(expected_label, self.fake.cancel_by_label_calls,
                     "fail_closed must sweep cancel_by_label with the exact plan-scoped label")
        self.assertEqual(self.fake.get_open_orders("t"), [], "no resting orders may be left behind")
        self.assertEqual(self.fake.pos, 0, "position must remain flat")

    # C: stop_market raises OrderStateUnknown after a filled entry.
    def test_c_stop_market_ambiguous_after_fill_flattens_and_halts(self):
        self.fake.entry_script = None      # normal entry: market order fills immediately
        self.fake.stop_script = "ambiguous"
        compiled = _compiled("gh_c")

        with self.assertRaises(executor.ExecutionHalted):
            executor.execute_plan(compiled)

        self.assertEqual(self.fake.pos, 0, "position must be flattened after the stop-placement failure")
        events = journal.read_events("gh_c")
        self.assertTrue(any(e["event_type"] == "mismatch_halt" for e in events))
        self.assertTrue(any(e["event_type"] == "order_placed" and e["data"].get("label") == "emergency_close"
                            for e in events))


if __name__ == "__main__":
    unittest.main()
