"""
Offline test for FT-2 (2026-09-28): the two HALT-file preflight checks added
to executor.py's preflight() (see the "HALT files (FT-2, 2026-09-28)" note
in executor.py's docstring for the exact contract each file follows).

Verifies:
  (a) _check_halt_files()/preflight() in isolation, with explicit tmp paths -
      no files -> no HALT reasons; generic HALT present -> refused; today's
      HALT_DAILY_LOSS -> refused; a well-formed PAST-dated HALT_DAILY_LOSS ->
      ALSO refused (FIX4 M2: existence blocks, whatever the date - see
      test_daily_loss_halt_past_dated_still_refuses); malformed
      HALT_DAILY_LOSS JSON -> refused (fail closed on ambiguity).
  (b) execute_plan() end-to-end, using the module's real default HALT_PATH/
      HALT_DAILY_LOSS_PATH (a real file written next to executor.py in the
      staged-test tmp dir) - a HALT (either kind, any date) refuses BEFORE
      any order is placed and leaves no journal (plan_id stays retriable,
      same rule as the existing B079/R8/S1 refusals).

No network. Run:
    python3 -m unittest test_halt_preflight_offline -v
"""
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import deribit_orders as do
import journal
import executor


def _order(oid, direction, amount, order_type, label, reduce_only, state, filled=0, avg=80000.0):
    return dict(order_id=oid, direction=direction.lower(), amount=amount, order_type=order_type,
                label=label, reduce_only=reduce_only, order_state=state, filled_amount=filled,
                average_price=avg)


class FakeExchange:
    """Minimal fake: market entries fill immediately, stop_market always
    succeeds. Same shape as test_s1_cap_offline.FakeExchange - a HALT
    refusal must happen before ANY of these methods place an order."""

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


def _compiled(plan_id, entry_amount=100):
    return {
        "plan_id": plan_id,
        "stop_order": {"side": "SELL", "label": "stop_order", "price": 79000.0},
        "caps_check": {"within_max_loss": True, "max_notional_usd": 10_000_000, "max_loss_usd": -1_000_000},
        "max_position_size": entry_amount,
        "entry_orders": [{"side": "BUY", "amount": entry_amount, "order_type": "market",
                          "price": None, "label": "entry_1"}],
        "target_orders": [],
    }


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _yesterday():
    return (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")


class HaltFilesUnitTests(unittest.TestCase):
    """preflight()/_check_halt_files() in isolation - explicit tmp paths, no
    exchange, no executor.HALT_PATH/HALT_DAILY_LOSS_PATH touched at all."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="halt_test_"))
        self.halt = self.tmp / "HALT"
        self.halt_dl = self.tmp / "HALT_DAILY_LOSS"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _reasons(self):
        compiled = _compiled("halt_unit")
        return executor.preflight(compiled, plan=None, mark=None,
                                  halt_path=self.halt, halt_daily_loss_path=self.halt_dl)

    def test_no_files_no_halt_reason(self):
        reasons = self._reasons()
        self.assertEqual(reasons, [])

    def test_generic_halt_file_refuses(self):
        self.halt.write_text("manual brake\n", encoding="utf-8")
        reasons = self._reasons()
        self.assertTrue(any("HALT:" in r for r in reasons), reasons)

    def test_daily_loss_halt_today_refuses(self):
        self.halt_dl.write_text(json.dumps({"date": _today(), "reason": "cap breached",
                                           "ts_iso": "2026-09-28T00:00:00Z"}), encoding="utf-8")
        reasons = self._reasons()
        self.assertTrue(any("HALT_DAILY_LOSS" in r and "cap breached" in r for r in reasons), reasons)

    def test_daily_loss_halt_past_dated_still_refuses(self):
        # FIX4 M2 supersedes the old "stale date -> warn only" contract:
        # existence blocks, whatever the date - only an operator deleting the
        # file resumes trading (was
        # test_daily_loss_halt_stale_does_not_refuse_but_warns).
        y = _yesterday()
        self.halt_dl.write_text(json.dumps({"date": y, "reason": "cap breached",
                                           "ts_iso": "2026-09-27T00:00:00Z"}), encoding="utf-8")
        reasons = self._reasons()
        self.assertTrue(any(f"HALT_DAILY_LOSS from {y} still present" in r for r in reasons), reasons)

    def test_daily_loss_halt_malformed_json_fails_closed(self):
        self.halt_dl.write_text("not valid json {{{", encoding="utf-8")
        reasons = self._reasons()
        self.assertTrue(any("HALT_DAILY_LOSS" in r for r in reasons), reasons)

    def test_both_halt_files_report_both_reasons(self):
        self.halt.write_text("x", encoding="utf-8")
        self.halt_dl.write_text(json.dumps({"date": _today(), "reason": "r", "ts_iso": "x"}), encoding="utf-8")
        reasons = self._reasons()
        self.assertTrue(any("HALT:" in r for r in reasons), reasons)
        self.assertTrue(any("HALT_DAILY_LOSS" in r for r in reasons), reasons)


class HaltFilesExecutePlanTests(unittest.TestCase):
    """execute_plan() end-to-end against the module's real default HALT
    paths (executor.HALT_PATH / executor.HALT_DAILY_LOSS_PATH), same style
    as test_s1_cap_offline.py's S1AccountCapTests."""

    def _patch(self, fake):
        self._orig = {name: getattr(do, name) for name in PATCHED_NAMES}
        for name in PATCHED_NAMES:
            setattr(do, name, getattr(fake, name))

    def tearDown(self):
        for name, fn in getattr(self, "_orig", {}).items():
            setattr(do, name, fn)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        for p in (executor.HALT_PATH, executor.HALT_DAILY_LOSS_PATH):
            if p.exists():
                p.unlink()

    def test_generic_halt_refuses_before_any_order(self):
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        executor.HALT_PATH.write_text("operator brake\n", encoding="utf-8")
        fake = FakeExchange()
        self._patch(fake)
        compiled = _compiled("halt_generic")

        with self.assertRaises(executor.ExecutionHalted) as ctx:
            executor.execute_plan(compiled)

        self.assertIn("HALT", str(ctx.exception))
        self.assertIn("PREFLIGHT REFUSED", str(ctx.exception))
        self.assertEqual(fake.buy_calls, [])
        self.assertEqual(fake.sell_calls, [])
        self.assertEqual(journal.read_events("halt_generic"), [],
                         "a HALT refusal must leave no journal - the plan_id must stay retriable")

    def test_daily_loss_halt_today_refuses_before_any_order(self):
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        executor.HALT_DAILY_LOSS_PATH.write_text(
            json.dumps({"date": _today(), "reason": "daily cap breached", "ts_iso": "x"}), encoding="utf-8")
        fake = FakeExchange()
        self._patch(fake)
        compiled = _compiled("halt_daily_today")

        with self.assertRaises(executor.ExecutionHalted) as ctx:
            executor.execute_plan(compiled)

        self.assertIn("HALT_DAILY_LOSS", str(ctx.exception))
        self.assertEqual(fake.buy_calls, [])
        self.assertEqual(journal.read_events("halt_daily_today"), [])

    def test_daily_loss_halt_past_dated_blocks_execution(self):
        # FIX4 M2 supersedes the old "stale date does not block" contract
        # (was test_daily_loss_halt_stale_does_not_block_execution).
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        y = _yesterday()
        executor.HALT_DAILY_LOSS_PATH.write_text(
            json.dumps({"date": y, "reason": "old breach", "ts_iso": "x"}), encoding="utf-8")
        fake = FakeExchange()
        self._patch(fake)
        compiled = _compiled("halt_daily_pastdated")

        with self.assertRaises(executor.ExecutionHalted) as ctx:
            executor.execute_plan(compiled)

        self.assertIn(f"HALT_DAILY_LOSS from {y} still present", str(ctx.exception))
        self.assertEqual(fake.buy_calls, [])
        self.assertEqual(journal.read_events("halt_daily_pastdated"), [])


if __name__ == "__main__":
    unittest.main()
