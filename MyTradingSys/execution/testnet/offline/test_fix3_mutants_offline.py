"""
FT-2 (2026-09-28) mutation-survivor kill file.

Targets the 13 SURVIVED mutants listed in
MyTradingSys/research/fast_track_2026-09-27/review/MUTATION_REPORT_FT2.md,
section "Survivors - missing test, precisely": R3, M1, K1, K2, K4, E1, E2,
E3, E7, E8, E11, P2, P5. Each test method is named after its mutant id.

Written against BEHAVIOUR/CONTRACT, not incidental implementation details,
because the staged code (kill_switch.py.new / executor.py.new /
position_manager.py.new) is being fixed concurrently for these same
findings:
  - K1/K2/K4: only assert cancels-before-close-per-instrument, that
    BTC-PERPETUAL is queried on the no-positions fallback, and that an
    explicit instruments=[...] list still gets BTC-PERPETUAL included -
    nothing about how the "no positions found" fallback is implemented
    (get_positions()-empty vs. get_positions()-raises).
  - E11: only asserts cancel_by_label was called for every target_i label
    at some point during fail_closed - no ordering vs. close_position.
  - P5: stop-out with zero target fills must close cleanly.
  - P2: unprotected window, confirmed live again (reset), a second
    unprotected window just under MAX_UNPROTECTED_SECONDS must NOT halt.
    The stop is made "not live" via a genuinely non-live confirmed state
    ("cancelled"), never via a read failure/exception.

No network, no exchange calls, no git writes. Run from a temp copy via:
    python scripts/dev/run_staged_tests.py MyTradingSys/execution \
        MyTradingSys/execution/testnet/offline -- test_fix3_mutants_offline
"""
import shutil
import tempfile
import types
import unittest
from pathlib import Path

import deribit_orders as do
import journal
import executor
import kill_switch
import position_manager as pm
import risk_guard
from daily_loss_guard import DEFAULT_DAILY_LOSS_CAP_USD  # noqa: F401 (sanity import, same module family)
import daily_loss_monitor as dlm


def _order(oid, direction, amount, order_type, label, reduce_only, state, filled=0, avg=80000.0,
          price=None, trigger_price=None):
    return dict(order_id=oid, direction=direction.lower(), amount=amount, order_type=order_type,
                label=label, reduce_only=reduce_only, order_state=state, filled_amount=filled,
                average_price=avg, price=price, trigger_price=trigger_price)


# ---------------------------------------------------------------------------
# R3 - risk_guard.account_position_notional, mark_price-given branch abs()
# ---------------------------------------------------------------------------
class TestR3(unittest.TestCase):
    def test_R3_abs_with_mark_price(self):
        # A short position (negative contracts) with a mark price must still
        # come back positive - abs() must be applied in the mark_price-given
        # branch too, not just the mark_price=None branch.
        self.assertEqual(risk_guard.account_position_notional(-2, 50000.0), 100000.0)


# ---------------------------------------------------------------------------
# M1 - daily_loss_monitor.run_once, breached_today idempotency guard
# ---------------------------------------------------------------------------
class FakeDailyLossClient:
    """Only what run_once/ensure_day_state/compute_total_pnl_usd need -
    kill_switch.kill_all itself is monkeypatched out below, so this client
    never needs get_positions/get_open_orders/cancel/close_position."""

    def __init__(self, equity, mark_price):
        self.equity = equity
        self.mark_price = mark_price

    def get_account_summary(self, token, currency="BTC"):
        return {"equity": self.equity}

    def get_ticker(self, instrument_name="BTC-PERPETUAL"):
        return {"mark_price": self.mark_price}


def _clock_at(iso_str):
    from datetime import datetime, timezone
    dt = datetime.fromisoformat(iso_str).replace(tzinfo=timezone.utc)
    return lambda: dt


class TestM1(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.state_path = Path(self.tmpdir.name) / "state.json"
        self.halt_path = Path(self.tmpdir.name) / "HALT_DAILY_LOSS"
        self._orig_kill_all = dlm.kill_switch.kill_all
        self.kill_all_calls = 0

        def counting_kill_all(client, token, currency="BTC"):
            self.kill_all_calls += 1
            return {"cancelled_orders": [], "closed_positions": [], "errors": [], "ok": True}

        dlm.kill_switch.kill_all = counting_kill_all

    def tearDown(self):
        dlm.kill_switch.kill_all = self._orig_kill_all
        self.tmpdir.cleanup()

    def test_M1_breach_guard_prevents_second_kill_all_call(self):
        # kill_switch.kill_all is directly mocked/counted here (per the
        # mutation report), independent of any fake client position-size
        # side effect - the mutant drops the `not state.get("breached_today")`
        # guard, so a SECOND same-day breached poll would call kill_all again.
        client = FakeDailyLossClient(equity=1.0, mark_price=85000.0)
        clock = _clock_at("2026-09-28T00:05:00")
        # baseline (no breach): sets day_start_equity
        dlm.run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)
        self.assertEqual(self.kill_all_calls, 0)

        # equity drops enough to breach the default cap
        client.equity = 1.0 - (600.0 / 85000.0)
        result1 = dlm.run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)
        self.assertFalse(result1["ok"])
        self.assertEqual(self.kill_all_calls, 1, "first breached poll must call kill_all exactly once")

        # a second, still-breached poll the same UTC day must NOT call kill_all again
        result2 = dlm.run_once(client, "tok", clock=clock, state_path=self.state_path, halt_path=self.halt_path)
        self.assertFalse(result2["ok"])
        self.assertEqual(self.kill_all_calls, 1,
                         "breached_today guard must prevent a second kill_all call the same day")


# ---------------------------------------------------------------------------
# K1 / K2 / K4 - kill_switch.kill_all instrument-selection/ordering
# ---------------------------------------------------------------------------
class OrderedClient:
    """Records every call in one ordered log, so call ORDER (not just call
    counts) can be asserted - kill_all's own client, no exchange/network."""

    def __init__(self, data):
        self._data = data
        self.log = []
        self.order_queries = []

    def get_positions(self, token, currency="BTC", kind="future"):
        self.log.append(("get_positions",))
        return [{"instrument_name": i, "size": d["size"]} for i, d in self._data.items()]

    def get_open_orders(self, token, instrument_name, type_="all"):
        self.order_queries.append(instrument_name)
        self.log.append(("get_open_orders", instrument_name))
        if instrument_name not in self._data:
            return []
        return [{"order_id": oid} for oid in self._data[instrument_name]["orders"]]

    def cancel(self, token, order_id):
        for instrument, info in self._data.items():
            if order_id in info["orders"]:
                info["orders"].remove(order_id)
                self.log.append(("cancel", instrument, order_id))
                return {}
        raise KeyError(order_id)

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        self.log.append(("close_position", instrument_name))
        if instrument_name not in self._data:
            raise ValueError(instrument_name)
        self._data[instrument_name]["size"] = 0
        return {"order": {"order_id": f"flat-{instrument_name}", "filled_amount": 0}}


class TestK1K2K4(unittest.TestCase):
    def test_K1_close_position_precedes_cancels_per_instrument(self):
        client = OrderedClient({
            "BTC-PERPETUAL": {"size": 10, "orders": ["o1", "o2"]},
            "ETH-PERPETUAL": {"size": 5, "orders": ["o3"]},
        })
        result = kill_switch.kill_all(client, "fake_token")
        self.assertTrue(result["ok"])

        cancel_idx = {}
        close_idx = {}
        for i, entry in enumerate(client.log):
            if entry[0] == "cancel":
                cancel_idx.setdefault(entry[1], []).append(i)
            elif entry[0] == "close_position":
                close_idx[entry[1]] = i

        for instrument in ("BTC-PERPETUAL", "ETH-PERPETUAL"):
            self.assertIn(instrument, close_idx, "each instrument must be flattened")
            self.assertTrue(cancel_idx.get(instrument), f"expected cancel(s) recorded for {instrument}")
            self.assertTrue(all(ci > close_idx[instrument] for ci in cancel_idx[instrument]),
                            f"every cancel for {instrument} must happen AFTER its close_position (PREMAINNET1 B1: close first) "
                            f"(cancels at {cancel_idx[instrument]}, close at {close_idx[instrument]})")

    def test_K2_no_positions_still_queries_btc_perpetual_fallback(self):
        client = OrderedClient({
            "BTC-PERPETUAL": {"size": 0, "orders": []},
            "ETH-PERPETUAL": {"size": 0, "orders": []},
        })
        result = kill_switch.kill_all(client, "fake_token", instruments=None)
        self.assertTrue(result["ok"])
        self.assertIn("BTC-PERPETUAL", client.order_queries,
                      "the no-positions fallback must actually query BTC-PERPETUAL's open orders, "
                      "not just claim it as a default")

    def test_K4_explicit_instruments_list_still_includes_btc_perpetual(self):
        client = OrderedClient({
            "ETH-PERPETUAL": {"size": 5, "orders": ["o1"]},
            "BTC-PERPETUAL": {"size": 3, "orders": ["o2"]},
        })
        result = kill_switch.kill_all(client, "fake_token", instruments=["ETH-PERPETUAL"])
        self.assertTrue(result["ok"])
        self.assertIn("BTC-PERPETUAL", client.order_queries,
                      "BTC-PERPETUAL must always be included/queried even when an explicit "
                      "instruments= list omits it")
        self.assertIn("BTC-PERPETUAL", [p["instrument_name"] for p in result["closed_positions"]],
                      "BTC-PERPETUAL's nonzero position must still be flattened")


# ---------------------------------------------------------------------------
# E1 / E2 / E3 / E7 / E8 / E11 - executor.py preflight/execute_plan/fail_closed
# ---------------------------------------------------------------------------
class ExecutorFakeExchange:
    """Minimal stand-in for the network boundary, same convention as
    test_gh_executor_offline.py's FakeExchange."""

    def __init__(self, existing_pos=0):
        self.pos = existing_pos
        self.orders = {}
        self.n = 0
        self.mark = 80000.0
        self.buy_calls = []
        self.sell_calls = []
        self.cancel_by_label_calls = []
        self.entry_script = None  # None | "ambiguous_fill"

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

    def _place(self, direction, amount, order_type, label, reduce_only, calls):
        calls.append(label)
        if self.entry_script == "ambiguous_fill":
            oid = self._new_id()
            self.orders[oid] = _order(oid, direction, amount, order_type, label, reduce_only,
                                      "filled", filled=amount)
            self.pos += amount if direction == "BUY" else -amount
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
        return self._place("BUY", amount, order_type, label, reduce_only, self.buy_calls)

    def sell(self, token, instrument, amount, order_type, price=None, label=None, reduce_only=False, **kw):
        return self._place("SELL", amount, order_type, label, reduce_only, self.sell_calls)

    def stop_market(self, token, instrument, side, amount, trigger_price, label, trigger="mark_price"):
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


def _compiled(plan_id, entry_amount=100, target_orders=None):
    return {
        "plan_id": plan_id,
        "stop_order": {"side": "SELL", "label": "stop_order", "price": 79000.0},
        "caps_check": {"within_max_loss": True, "max_notional_usd": 10_000_000, "max_loss_usd": -1_000_000},
        "max_position_size": entry_amount,
        "entry_orders": [{"side": "BUY", "amount": entry_amount, "order_type": "market",
                          "price": None, "label": "entry_1"}],
        "target_orders": target_orders if target_orders is not None else [],
    }


class TestExecutorPreflightPure(unittest.TestCase):
    """E1/E2/E3/E8 - executor.preflight() is pure (besides HALT-file reads,
    which don't come into play with the default HALT_PATH args pointing at
    real, nonexistent paths next to executor.py in the sandbox - but to be
    safe we point them at a tmp dir with no files)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="e_preflight_"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _reasons(self, compiled, plan=None, mark=None):
        return executor.preflight(compiled, plan=plan, mark=mark,
                                  halt_path=self.tmp / "HALT",
                                  halt_daily_loss_path=self.tmp / "HALT_DAILY_LOSS")

    def test_E1_plan_level_max_notional_refusal(self):
        compiled = _compiled("e1")
        compiled["max_position_size"] = 6000
        compiled["caps_check"] = {"within_max_loss": True, "max_notional_usd": 5000, "max_loss_usd": -1_000_000}
        reasons = self._reasons(compiled)
        self.assertTrue(any("max_notional_usd" in r and "6000" in r for r in reasons), reasons)

    def test_E2_b079_within_max_loss_false_refusal(self):
        compiled = _compiled("e2")
        compiled["caps_check"] = {"within_max_loss": False, "max_notional_usd": 1_000_000, "max_loss_usd": -500}
        reasons = self._reasons(compiled)
        self.assertTrue(any("B079" in r and "worst_case_loss" in r for r in reasons), reasons)

    def test_E3_market_entry_estimated_loss_refusal(self):
        compiled = _compiled("e3")
        compiled["max_position_size"] = 10000
        compiled["caps_check"] = {"within_max_loss": "unknown_until_fill", "max_notional_usd": 1_000_000,
                                  "max_loss_usd": -500}
        plan = {"stop": {"type": "fixed_percent", "percent_below_entry": 10}}
        reasons = self._reasons(compiled, plan=plan, mark=80000.0)
        self.assertTrue(any("B079" in r and "market est. loss" in r for r in reasons), reasons)

    def test_E8_unsupported_stop_type_refusal(self):
        compiled = _compiled("e8")
        compiled["stop_order"] = {"side": "SELL", "label": "stop_order", "order_type": "trailing_percent"}
        reasons = self._reasons(compiled)
        self.assertTrue(any("not implemented" in r and "trailing_percent" in r for r in reasons), reasons)


class TestExecutorExecutePlan(unittest.TestCase):
    """E7/E11 - end-to-end execute_plan()."""

    def setUp(self):
        self.fake = ExecutorFakeExchange()
        self._orig = {name: getattr(do, name) for name in PATCHED_NAMES}
        for name in PATCHED_NAMES:
            setattr(do, name, getattr(self.fake, name))
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        for p in (executor.HALT_PATH, executor.HALT_DAILY_LOSS_PATH):
            if p.exists():
                p.unlink()

    def tearDown(self):
        for name, fn in self._orig.items():
            setattr(do, name, fn)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        # fail_closed (FIX3 M5) writes a REAL manual HALT file next to
        # executor.py (not a tmp path) - clean it up so it can never leak
        # into another test in this process (e.g. E11's fail_closed call
        # must not cause E7's dirty-account test to be refused by a stale
        # HALT file instead of R8).
        for p in (executor.HALT_PATH, executor.HALT_DAILY_LOSS_PATH):
            if p.exists():
                p.unlink()

    def test_E7_r8_refuses_before_any_order_on_dirty_account(self):
        self.fake.pos = 50  # a pre-existing position on the instrument
        compiled = _compiled("e7_dirty")

        with self.assertRaises(executor.ExecutionHalted) as ctx:
            executor.execute_plan(compiled)

        self.assertIn("R8", str(ctx.exception))
        self.assertEqual(self.fake.buy_calls, [], "R8 must refuse before placing any entry order")
        self.assertEqual(self.fake.sell_calls, [])
        self.assertEqual(journal.read_events("e7_dirty"), [],
                         "an R8 refusal must leave no journal - the plan_id must stay retriable")

    def test_E11_fail_closed_sweeps_every_target_label(self):
        # n_targets, when execute_plan is called with compiled only (no raw
        # plan - the offline-test path documented in fail_closed's own
        # comment), comes from len(compiled["target_orders"]); force an
        # early fail_closed (ambiguous-but-filled entry, same as the G-h
        # scenario) with two target_orders present so the target-label sweep
        # actually has i=1..2 to iterate, independent of whether targets were
        # ever really placed in this particular run.
        self.fake.entry_script = "ambiguous_fill"
        compiled = _compiled("e11", target_orders=[{"label": "target_1"}, {"label": "target_2"}])

        with self.assertRaises(executor.ExecutionHalted):
            executor.execute_plan(compiled)

        self.assertIn("e11:target_1", self.fake.cancel_by_label_calls)
        self.assertIn("e11:target_2", self.fake.cancel_by_label_calls)


# ---------------------------------------------------------------------------
# P2 / P5 - position_manager.py
# ---------------------------------------------------------------------------
class FakeClock:
    def __init__(self):
        self.now = 0.0

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class ScriptedStopExchange:
    """Position fixed at 100 the whole test; get_order_state returns states
    from a scripted list, one per call (there is exactly one get_order_state
    call per manage() poll here, since no targets are journaled)."""

    def __init__(self, states):
        self.pos = 100
        self.n = 0
        self._states = list(states)
        self.stop_market_calls = 0

    def _new_id(self):
        self.n += 1
        return f"O{self.n}"

    def authenticate(self):
        return "tok"

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        return {"size": self.pos}

    def get_order_state(self, token, oid):
        state = self._states.pop(0)
        return {"order_state": state, "filled_amount": 0, "average_price": 0}

    def stop_market(self, token, instrument, side, amount, trigger_price, label, trigger="mark_price"):
        self.stop_market_calls += 1
        oid = self._new_id()
        return {"order": _order(oid, side, amount, "stop_market", label, True, "untriggered",
                                trigger_price=trigger_price)}

    def edit(self, token, oid, amount=None, price=None, trigger_price=None):
        return {"order": {"order_id": oid, "amount": amount}}

    def cancel(self, token, oid):
        return {"order_id": oid, "order_state": "cancelled"}

    def cancel_by_label(self, token, label, currency="BTC"):
        return 0

    def close_position(self, token, instrument="BTC-PERPETUAL"):
        self.pos = 0
        oid = self._new_id()
        return {"order": _order(oid, "SELL", 100, "market", "emergency_close", True, "filled", filled=100)}


PM_PATCHED_NAMES = ("authenticate", "get_position", "get_order_state", "stop_market", "edit", "cancel",
                    "cancel_by_label", "close_position")


class TestP2(unittest.TestCase):
    def setUp(self):
        # States, one per poll: not-live, LIVE (confirmed live -> reset),
        # not-live again, not-live again (still under the bound when the
        # test's max_seconds cuts the loop off).
        self.fake = ScriptedStopExchange(["cancelled", "untriggered", "cancelled", "cancelled"])
        self._orig = {name: getattr(do, name) for name in PM_PATCHED_NAMES}
        for name in PM_PATCHED_NAMES:
            setattr(do, name, getattr(self.fake, name))
        self._orig_time = pm.time
        self.clock = FakeClock()
        pm.time = types.SimpleNamespace(time=self.clock.time, sleep=self.clock.sleep, monotonic=self.clock.time)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)

        self.plan_id = "p2_reset"
        journal.append_event(self.plan_id, "order_placed", {"order_id": "E1", "label": "entry_1",
                                                             "side": "BUY", "amount": 100})
        journal.append_event(self.plan_id, "order_filled", {"order_id": "E1", "filled_amount": 100,
                                                             "order_state": "filled"})
        journal.append_event(self.plan_id, "order_placed", {"order_id": "S1", "label": "stop_order",
                                                             "side": "SELL", "amount": 100,
                                                             "trigger_price": 79000.0})

    def tearDown(self):
        for name, fn in self._orig.items():
            setattr(do, name, fn)
        pm.time = self._orig_time
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)

    def test_P2_unprotected_since_resets_when_stop_confirmed_live_again(self):
        # max_seconds=6 stops the loop right after the second unprotected
        # window has been open for 2s (well under MAX_UNPROTECTED_SECONDS=4s,
        # counted from when that SECOND window started, not the first).
        # Without the reset, the mutant reuses the first window's start time
        # and the cumulative elapsed (6s) exceeds the bound -> flattens.
        try:
            result = pm.manage(self.plan_id, once=False, max_seconds=6, token="t")
        except pm.ManagerHalted as e:
            self.fail(f"must not halt: the second unprotected window is still under "
                     f"MAX_UNPROTECTED_SECONDS after the reset ({e})")
        self.assertEqual(result["status"], "managing")
        self.assertGreaterEqual(self.fake.stop_market_calls, 2,
                                "must have retried the re-place across both unprotected windows")


class ZeroTargetFillExchange:
    """Position already flat (stop fired), and no targets were ever placed
    for this plan - target_filled must come out to 0."""

    def __init__(self):
        self.pos = 0

    def authenticate(self):
        return "tok"

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        return {"size": self.pos}

    def get_order_state(self, token, oid):
        # the stop fired (a genuinely non-live, non-error state)
        return {"order_state": "filled", "filled_amount": 100, "average_price": 79000.0}

    def stop_market(self, token, instrument, side, amount, trigger_price, label, trigger="mark_price"):
        raise AssertionError("stop_market must not be called: position is already flat")

    def edit(self, token, oid, amount=None, price=None, trigger_price=None):
        raise AssertionError("edit must not be called: position is already flat")

    def cancel(self, token, oid):
        return {"order_id": oid, "order_state": "cancelled"}

    def cancel_by_label(self, token, label, currency="BTC"):
        return 0

    def close_position(self, token, instrument="BTC-PERPETUAL"):
        return {"order": _order("emerg", "SELL", 0, "market", "emergency_close", True, "filled", filled=0)}


class TestP5(unittest.TestCase):
    def setUp(self):
        self.fake = ZeroTargetFillExchange()
        self._orig = {name: getattr(do, name) for name in PM_PATCHED_NAMES}
        for name in PM_PATCHED_NAMES:
            setattr(do, name, getattr(self.fake, name))
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)

        self.plan_id = "p5_zero_target_fill"
        journal.append_event(self.plan_id, "order_placed", {"order_id": "E1", "label": "entry_1",
                                                             "side": "BUY", "amount": 100})
        journal.append_event(self.plan_id, "order_filled", {"order_id": "E1", "filled_amount": 100,
                                                             "order_state": "filled"})
        journal.append_event(self.plan_id, "order_placed", {"order_id": "S1", "label": "stop_order",
                                                             "side": "SELL", "amount": 100,
                                                             "trigger_price": 79000.0})
        # deliberately no target order_placed events -> targets == {} -> target_filled == 0

    def tearDown(self):
        for name, fn in self._orig.items():
            setattr(do, name, fn)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)

    def test_P5_stop_out_with_zero_target_fills_closes_cleanly(self):
        try:
            result = pm.manage(self.plan_id, once=True, token="t")
        except pm.ManagerHalted as e:
            self.fail(f"a legitimate stop-out with zero target fills must not mismatch_halt ({e})")
        self.assertEqual(result["status"], "closed")
        self.assertEqual(result["target_filled"], 0)
        events = journal.read_events(self.plan_id)
        self.assertFalse(any(e["event_type"] == "mismatch_halt" for e in events))


if __name__ == "__main__":
    unittest.main()
