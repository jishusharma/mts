"""
Offline test for S1 (2026-09-28): executor.py's account-wide notional cap
preflight check, wired to risk_guard.check_new_plan_against_cap().

Verifies:
  (a) a plan that would push account notional (existing position + this
      plan's max_position_size) over risk_guard.MAX_ACCOUNT_NOTIONAL_USD is
      refused before any order is placed - no do.buy/sell call happens.
  (b) a plan that stays within the cap is NOT refused by the S1 check (it
      runs through to completion against a simple fake exchange).
  (c) the refusal does not leave a journal file behind, so the same plan_id
      can be retried later (all OTHER preflight refusals - B079, R8,
      validity, trailing-stop - follow this same rule; see the "S1:" comment
      in executor.py's execute_plan for why).

No network. Run:
    python3 -m unittest test_s1_cap_offline -v
"""
import shutil
import unittest

import deribit_orders as do
import journal
import executor
import risk_guard


def _order(oid, direction, amount, order_type, label, reduce_only, state, filled=0, avg=80000.0):
    return dict(order_id=oid, direction=direction.lower(), amount=amount, order_type=order_type,
                label=label, reduce_only=reduce_only, order_state=state, filled_amount=filled,
                average_price=avg)


class FakeExchange:
    """Minimal fake: market entries fill immediately, stop_market always
    succeeds. `pos` is pre-set by the test to simulate an existing account
    position before this plan is ever compiled/entered."""

    def __init__(self, existing_pos=0):
        self.pos = existing_pos
        self.n = 0
        self.orders = {}
        self.mark = 80000.0
        self.buy_calls = []
        self.sell_calls = []

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

    def buy(self, token, instrument, amount, order_type, price=None, label=None, reduce_only=False, **kw):
        self.buy_calls.append(label)
        oid = self._new_id()
        filled = amount if order_type == "market" else 0
        state = "filled" if order_type == "market" else "open"
        self.orders[oid] = _order(oid, "BUY", amount, order_type, label, reduce_only, state, filled=filled)
        if filled:
            self.pos += amount
        return {"order": self.orders[oid]}

    def sell(self, token, instrument, amount, order_type, price=None, label=None, reduce_only=False, **kw):
        self.sell_calls.append(label)
        oid = self._new_id()
        filled = amount if order_type == "market" else 0
        state = "filled" if order_type == "market" else "open"
        self.orders[oid] = _order(oid, "SELL", amount, order_type, label, reduce_only, state, filled=filled)
        if filled:
            self.pos -= amount
        return {"order": self.orders[oid]}

    def stop_market(self, token, instrument, side, amount, trigger_price, label, trigger="mark_price"):
        oid = self._new_id()
        self.orders[oid] = _order(oid, side, amount, "stop_market", label, True, "untriggered")
        return {"order": self.orders[oid]}

    def edit(self, token, oid, amount=None, price=None, trigger_price=None):
        o = self.orders[oid]
        if amount is not None:
            o["amount"] = amount
        return {"order": o}

    def cancel(self, token, oid):
        o = self.orders[oid]
        o["order_state"] = "cancelled"
        return {"order": o}

    def cancel_by_label(self, token, label, currency="BTC"):
        return 0

    def close_position(self, token, instrument="BTC-PERPETUAL"):
        amt = abs(self.pos)
        self.pos = 0
        oid = self._new_id()
        self.orders[oid] = _order(oid, "SELL", amt, "market", "emergency_close", True, "filled", filled=amt)
        return {"order": self.orders[oid]}


PATCHED_NAMES = ("authenticate", "get_ticker", "get_position", "get_open_orders", "get_order_state",
                 "buy", "sell", "stop_market", "edit", "cancel", "cancel_by_label", "close_position")


def _compiled(plan_id, entry_amount):
    return {
        "plan_id": plan_id,
        "stop_order": {"side": "SELL", "label": "stop_order", "price": 79000.0},
        "caps_check": {"within_max_loss": True, "max_notional_usd": 10_000_000, "max_loss_usd": -1_000_000},
        "max_position_size": entry_amount,
        "entry_orders": [{"side": "BUY", "amount": entry_amount, "order_type": "market",
                          "price": None, "label": "entry_1"}],
        "target_orders": [],
    }


class S1AccountCapTests(unittest.TestCase):
    def _patch(self, fake):
        self._orig = {name: getattr(do, name) for name in PATCHED_NAMES}
        for name in PATCHED_NAMES:
            setattr(do, name, getattr(fake, name))

    def tearDown(self):
        for name, fn in getattr(self, "_orig", {}).items():
            setattr(do, name, fn)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)

    def test_breach_refused_before_any_order(self):
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        # existing position already at 9500 of the 10000 cap; a 1000 plan
        # would project to 10500 > cap.
        fake = FakeExchange(existing_pos=9500)
        self._patch(fake)
        compiled = _compiled("s1_breach", entry_amount=1000)

        with self.assertRaises(executor.ExecutionHalted) as ctx:
            executor.execute_plan(compiled)

        self.assertIn("S1", str(ctx.exception))
        self.assertIn("PREFLIGHT REFUSED", str(ctx.exception))
        self.assertEqual(fake.buy_calls, [], "no entry order may be placed once the account cap refuses")
        self.assertEqual(fake.sell_calls, [])
        self.assertEqual(fake.pos, 9500, "existing position must be untouched")
        self.assertEqual(journal.read_events("s1_breach"), [],
                         "a preflight refusal must leave no journal - the plan_id must stay retriable")

    def test_within_cap_not_refused_by_s1(self):
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        # existing position 0; a 500 plan projects to 500, well within the
        # default MAX_ACCOUNT_NOTIONAL_USD=10000 cap.
        fake = FakeExchange(existing_pos=0)
        self._patch(fake)
        compiled = _compiled("s1_ok", entry_amount=500)

        result = executor.execute_plan(compiled)

        self.assertEqual(result["status"], "entry_filled_stop_placed")
        self.assertEqual(fake.buy_calls, ["s1_ok:entry_1"])
        events = journal.read_events("s1_ok")
        intent = next(e for e in events if e["event_type"] == "intent")
        self.assertIn("account_cap_check", intent["data"])
        self.assertTrue(intent["data"]["account_cap_check"]["ok"])

    def test_cap_math_matches_risk_guard_directly(self):
        # sanity: the exact numbers executor's S1 check will see, checked
        # directly against risk_guard so a future edit to either side is
        # caught by both test files.
        current = risk_guard.account_position_notional(9500, None)
        result = risk_guard.check_new_plan_against_cap(current, 1000)
        self.assertFalse(result["ok"])
        self.assertIn("10500", result["reason"])


if __name__ == "__main__":
    unittest.main()
