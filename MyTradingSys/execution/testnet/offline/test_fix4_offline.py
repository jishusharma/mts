"""
Offline TESTS-FIRST for three open findings of
review/ADVERSARIAL_REVIEW_FT2.md that FIX3/FT-2 did not close: M4, L1, L2.

THESE TESTS ARE EXPECTED TO FAIL until the corresponding M4/L1/L2 fixes land
in executor.py / position_manager.py. They are written against the CURRENT
(unfixed) staged behaviour on purpose, to pin down exactly what "fixed" must
look like:

  M4 - execute_plan() only checks the HALT files once, in preflight(), before
       any order is placed. It never re-checks them again for the rest of the
       run. A HALT (or a same-day HALT_DAILY_LOSS) written mid-run - by an
       operator, a concurrent kill_all, or daily_loss_monitor - is invisible
       to every order-creating call after the first (entry rungs 2..N, the
       stop create/resize, every target). Fix: re-check before EVERY
       order-creating call; on a hit, fail_closed("HALT observed mid-run").
  L1 - position_manager's pos==0 "explained" check
       (`target_filled >= stop["amount"]`) compares against stop["amount"],
       which SHRINKS every time a target fills (G1). So a partial target
       fill followed by a manual close of the remainder is wrongly counted
       as "explained" once target_filled clears the already-shrunk amount,
       even though it never covered the ORIGINAL entry fill. Fix: compare
       against the original entry fill total, or require stop_fired.
  L2 - the executor targets loop's `except do.DeribitError: continue` also
       swallows OrderStateUnknown (a subclass), so a target create that may
       have actually rested on the exchange (response merely lost) is never
       swept by label - only a plain rejection (order never rested) needs no
       sweep. Fix: on OrderStateUnknown specifically, cancel_by_label the
       target's plan-scoped label; a plain DeribitError keeps today's
       continue-with-no-sweep behaviour either way.

Run (from repo root):
  python scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline -- test_fix4_offline

No network, no secrets. HALT/journal state only ever touches the sandbox
copy run_staged_tests.py builds next to the staged modules.
"""
import sys
sys.dont_write_bytecode = True

import json
import unittest
from unittest import mock

import deribit_orders as do
import journal
import executor
import position_manager as pm
from test_gh_executor_offline import FakeExchange, PATCHED_NAMES, _compiled
from test_fix3_offline import _ExchangeCase, TODAY


class _Clock:
    """Fake executor.time - rungs 2/3 of the M4 ladder test are resting limit
    orders that never fill, so an UNFIXED run polls all the way to the entry
    deadline (default 600s) with real time.sleep in between. Patching
    executor.time to this in-memory clock lets that deadline pass instantly
    instead of hanging the suite for ten minutes."""

    def __init__(self):
        self.t = 1_000_000.0

    def time(self):
        return self.t

    def sleep(self, s):
        self.t += s


def _compiled_ladder(plan_id, amounts=(30, 30, 40)):
    """A 3-rung entry ladder: rung 1 is a market order (fills immediately),
    rungs 2/3 are resting limit orders (never fill in this fake unless the
    price is scripted to move - not needed for the M4 mid-run-HALT tests,
    which only care whether the CREATE call happens at all)."""
    entry_orders = []
    for i, amt in enumerate(amounts, start=1):
        if i == 1:
            entry_orders.append({"side": "BUY", "amount": amt, "order_type": "market",
                                 "price": None, "label": f"entry_rung_{i}"})
        else:
            entry_orders.append({"side": "BUY", "amount": amt, "order_type": "limit",
                                 "price": 50000.0 - i, "label": f"entry_rung_{i}"})
    return {
        "plan_id": plan_id,
        "stop_order": {"side": "SELL", "label": "stop_order", "price": 79000.0},
        "caps_check": {"within_max_loss": True, "max_notional_usd": 10_000_000, "max_loss_usd": -1_000_000},
        "max_position_size": sum(amounts),
        "entry_orders": entry_orders,
    }


# ==================================================================== M4
class M4HaltMidRun(_ExchangeCase):
    """execute_plan must re-check the HALT files before EVERY order-creating
    call, not just once in preflight()."""

    def setUp(self):
        super().setUp()
        executor.HALT_DAILY_LOSS_PATH.unlink(missing_ok=True)
        self._clock = _Clock()
        self._clock_patch = mock.patch.object(executor, "time", self._clock)
        self._clock_patch.start()

    def tearDown(self):
        self._clock_patch.stop()
        executor.HALT_DAILY_LOSS_PATH.unlink(missing_ok=True)
        super().tearDown()

    def test_M4_halt_after_rung1_stops_ladder_and_flattens(self):
        # HALT appears the instant rung 1's entry-create call returns (R14:
        # a kill_all / operator HALT racing a ladder still mid-fill).
        compiled = _compiled_ladder("m4_ladder")
        n = {"i": 0}

        def after_first_buy(*a):
            n["i"] += 1
            if n["i"] == 1:
                executor.HALT_PATH.write_text("operator HALT mid-run\n", encoding="utf-8")
            return None  # let the real call proceed normally
        self.inject["buy"] = after_first_buy

        # rungs 2/3 are resting limit orders that never fill in this fake, so
        # an UNFIXED run polls all the way to the entry deadline - the
        # patched _Clock (see setUp) makes that instantaneous instead of a
        # real 600s wait.
        with self.assertRaises(executor.ExecutionHalted) as ctx:
            executor.execute_plan(compiled)

        self.assertIn("HALT observed mid-run", str(ctx.exception))
        self.assertEqual(self.names().count("buy"), 1,
                         "no order-creating call may happen after the HALT file appears "
                         f"(rungs 2/3 must never be placed): {self.calls}")
        self.assertEqual(self.fake.pos, 0, "the rung-1 fill must be flattened")
        self.assertIn("close_position", self.names())

    def test_M4_halt_daily_loss_today_before_targets_blocks_all_targets(self):
        # Single market entry fills 100, stop gets placed - then, right at
        # the post-poll verify read (the last do.get_position call before the
        # targets loop begins), a same-day HALT_DAILY_LOSS appears.
        compiled = _compiled(pid := "m4_targets")
        plan = {"stop": {"type": "fixed_percent", "percent_below_entry": 5},
               "targets": [{"amount_percent": 50, "pnl_target_percent": 5},
                           {"amount_percent": 50, "pnl_target_percent": 10}]}
        n = {"i": 0}

        def before_targets(token, instrument="BTC-PERPETUAL"):
            n["i"] += 1
            if n["i"] == 2:  # 1 = R8 preflight read, 2 = post-poll verify (right before targets)
                executor.HALT_DAILY_LOSS_PATH.write_text(
                    json.dumps({"date": TODAY, "reason": "cap breached mid-run"}), encoding="utf-8")
            return None
        self.inject["get_position"] = before_targets

        with self.assertRaises(executor.ExecutionHalted) as ctx:
            executor.execute_plan(compiled, plan)

        self.assertIn("HALT observed mid-run", str(ctx.exception))
        target_labels = [o["label"] for o in self.fake.orders.values() if "target" in o["label"]]
        self.assertEqual(target_labels, [], f"no target may be created once HALT_DAILY_LOSS is active: {target_labels}")
        self.assertEqual(self.fake.pos, 0, "the filled entry must be flattened")


# ==================================================================== L1
class L1PositionManagerExplainedCheck(_ExchangeCase):
    """pos==0 'explained' must compare target fills against the ORIGINAL
    entry fill total (or require stop_fired) - not the shrunken stop amount."""

    def _place_with_two_targets(self, pid):
        compiled = _compiled(pid)
        plan = {"stop": {"type": "fixed_percent", "percent_below_entry": 5},
               "targets": [{"amount_percent": 60, "pnl_target_percent": 5},
                           {"amount_percent": 40, "pnl_target_percent": 10}]}
        r = executor.execute_plan(compiled, plan)
        self.assertEqual(r["status"], "entry_filled_stop_placed")
        self.assertEqual(len(r["target_order_ids"]), 2, r)
        self.calls.clear()
        return r["target_order_ids"], r["stop_order_id"]

    def test_L1_partial_target_then_manual_close_is_unexplained(self):
        (t1, t2), stop_id = self._place_with_two_targets("fx_l1a")

        # target_1 (60 of 100) fills fully; the exchange position drops by 60.
        self.fake.orders[t1]["order_state"] = "filled"
        self.fake.orders[t1]["filled_amount"] = 60
        self.fake.pos -= 60
        r = pm.manage("fx_l1a", once=True, token="tok")
        self.assertEqual(r["status"], "managing")
        self.assertEqual(self.fake.orders[stop_id]["amount"], 40, "G1: stop shrinks to the live 40")

        # the remaining 40 is closed BY HAND - not target_2 (still resting,
        # never filled) and not the stop (still untriggered/live).
        self.fake.pos = 0
        with self.assertRaises(pm.ManagerHalted) as ctx:
            pm.manage("fx_l1a", once=True, token="tok")
        self.assertIn("unexplained", str(ctx.exception),
                      "60 of 100 filled by targets must NOT be 'explained' just because it "
                      "clears the already-shrunk stop amount (40)")

    def test_L1_target_fills_totalling_full_entry_close_cleanly(self):
        (t1, t2), stop_id = self._place_with_two_targets("fx_l1b")

        self.fake.orders[t1]["order_state"] = "filled"
        self.fake.orders[t1]["filled_amount"] = 60
        self.fake.pos -= 60
        pm.manage("fx_l1b", once=True, token="tok")

        self.fake.orders[t2]["order_state"] = "filled"
        self.fake.orders[t2]["filled_amount"] = 40
        self.fake.pos -= 40  # now flat, 60 + 40 == 100 == the original entry fill
        r = pm.manage("fx_l1b", once=True, token="tok")
        self.assertEqual(r["status"], "closed")
        self.assertEqual(r["target_filled"], 100)


# ==================================================================== L2
class L2TargetsOrderStateUnknown(_ExchangeCase):
    """OrderStateUnknown on a target create must sweep that target's
    plan-scoped label and must not reduce `remaining`; a plain DeribitError
    rejection keeps today's behaviour (continue, no sweep)."""

    def _plan_two_targets(self):
        return {"stop": {"type": "fixed_percent", "percent_below_entry": 5},
               "targets": [{"amount_percent": 50, "pnl_target_percent": 5},
                           {"amount_percent": 50, "pnl_target_percent": 10}]}

    def test_L2_order_state_unknown_on_target_sweeps_label(self):
        compiled = _compiled("fx_l2a")
        n = {"i": 0}

        def target_1_ambiguous(*a):
            n["i"] += 1
            if n["i"] == 1:  # first `sell` after the entry `buy` is target_1
                return do.OrderStateUnknown("private/sell", "fx_l2a:target_1", 10050)
            return None
        self.inject["sell"] = target_1_ambiguous

        r = executor.execute_plan(compiled, self._plan_two_targets())

        self.assertIn("fx_l2a:target_1", self.fake.cancel_by_label_calls,
                      f"an ambiguous target create must sweep its own label: {self.fake.cancel_by_label_calls}")
        # target_2 must still be placed for its full remaining share (100),
        # not reduced as if target_1 had actually consumed 50 of it.
        self.assertEqual(len(r["target_order_ids"]), 1)
        t2_orders = [o for o in self.fake.orders.values() if o["label"] == "fx_l2a:target_2"]
        self.assertEqual(len(t2_orders), 1)
        self.assertEqual(t2_orders[0]["amount"], 100,
                         "remaining must not be reduced by the ambiguous (possibly-never-placed) target_1")

    def test_L2_plain_deribit_error_on_target_keeps_current_behaviour(self):
        compiled = _compiled("fx_l2b")
        n = {"i": 0}

        def target_1_rejected(*a):
            n["i"] += 1
            if n["i"] == 1:
                return do.DeribitError("private/sell", {"code": 10009, "message": "not_enough_funds"})
            return None
        self.inject["sell"] = target_1_rejected

        r = executor.execute_plan(compiled, self._plan_two_targets())

        self.assertNotIn("fx_l2b:target_1", self.fake.cancel_by_label_calls,
                         "a plain rejection (order never rested) must not sweep by label")
        self.assertEqual(len(r["target_order_ids"]), 1)


if __name__ == "__main__":
    unittest.main()
