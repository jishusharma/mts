"""R2 breakeven move in position_manager, offline (session MTS-2026-10-03-CLI-BLD-r2-runner-exit).

Rule under test: a plan with breakeven_after_first_target gets its live stop's trigger edited to the average entry
fill once the FIRST target order is completely filled and the position really shrank - once per plan, never before,
never again, never by halting, never by loosening protection.

Fixture: LONG, 200 USD filled at 80000.0, stop S1 at 79200.0, target_1 T1 (100) and runner target_2 T2 (100).
Hand expectations:
  breakeven trigger = average entry snapped UP to the 0.5 tick (LONG) / DOWN (SHORT): 80000.0 -> 80000.0
  ladder 100 @ 80000 + 100 @ 79000: inverse-contract mean = 2ab/(a+b) = 2*80000*79000/159000 = 79496.855
      -> LONG trigger 79497.0, SHORT trigger 79496.5          (FORMULAS.md 11.4, 11.1)
  after T1 fills the position is 100: G1 shrinks the stop to 100 at the OLD trigger, then breakeven edits the trigger.

Hermetic: journal / plans / HALT redirected to a temp dir, exchange and clock are fakes. Run through
scripts/dev/run_staged_tests.py (run_all_tests.py step 1) so the staged position_manager.py.new is imported.
"""
import json
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import deribit_orders as do
import journal
import position_manager as pm

PLAN_ID = "r2_be_t1"
PATCHED = ("authenticate", "get_position", "get_order_state", "get_ticker", "stop_market", "edit", "cancel",
           "cancel_by_label", "close_position")


class FakeClock:
    def __init__(self, on_sleep=None):
        self.now, self.on_sleep = 1_000_000.0, on_sleep

    def time(self):
        return self.now

    def sleep(self, s):
        self.now += s
        if self.on_sleep:
            self.on_sleep(self.now)


class FakeExchange:
    def __init__(self, pos=200, mark=81000.0, stop_trigger=79200.0):
        self.pos, self.mark = pos, mark
        self.orders = {
            "S1": dict(order_state="untriggered", filled_amount=0, average_price=0, amount=pos, trigger=stop_trigger),
            "T1": dict(order_state="open", filled_amount=0, average_price=0, amount=100),
            "T2": dict(order_state="open", filled_amount=0, average_price=0, amount=100)}
        self.edits = []              # (order_id, amount, trigger_price) of every accepted edit
        self.failed_edits = 0        # trigger-moving edits that were rejected
        self.fail_trigger_edits = False
        self.stop_places = []        # (side, amount, trigger, label) of every re-placed stop
        self.closes = 0

    def fill_t1(self, filled=100):
        o = self.orders["T1"]
        o.update(filled_amount=filled, order_state="filled" if filled >= 100 else "open", average_price=81200.0)
        self.pos = self.pos - filled if self.pos > 0 else self.pos + filled      # reduce |pos|, either side

    def authenticate(self):
        return "tok"

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        return {"size": self.pos}

    def get_order_state(self, token, oid):
        return dict(self.orders[oid])

    def get_ticker(self, instrument="BTC-PERPETUAL"):
        return {"mark_price": self.mark}

    def edit(self, token, oid, amount=None, price=None, trigger_price=None):
        o = self.orders[oid]
        if trigger_price is not None and self.fail_trigger_edits and trigger_price != o["trigger"]:
            self.failed_edits += 1
            raise do.DeribitError("private/edit", {"code": 10009, "message": "rejected"})
        self.edits.append((oid, amount, trigger_price))
        if amount is not None:
            o["amount"] = amount
        if trigger_price is not None:
            o["trigger"] = trigger_price
        return {"order": {"order_id": oid}}

    def stop_market(self, token, instrument, side, amount, trigger_price, label, trigger="mark_price"):
        self.stop_places.append((side, amount, trigger_price, label))
        self.orders["S2"] = dict(order_state="untriggered", filled_amount=0, average_price=0, amount=amount,
                                 trigger=trigger_price)
        return {"order": {"order_id": "S2"}}

    def cancel(self, token, oid):
        return {"order_id": oid}

    def cancel_by_label(self, token, label, currency="BTC"):
        return 0

    def close_position(self, token, instrument="BTC-PERPETUAL"):
        self.closes += 1
        raise AssertionError("breakeven must never flatten")


class BreakevenBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="r2_be_"))
        (self.tmp / "plans").mkdir()
        self.fake = FakeExchange()
        for n in PATCHED:
            self._patch(do, n, getattr(self.fake, n))
        self._patch(journal, "JOURNAL_DIR", self.tmp / "journal")
        self._patch(pm, "PLANS_DIR", self.tmp / "plans")
        self._patch(pm, "HALT_PATH", self.tmp / "HALT")
        self._patch(pm.pm_heartbeat, "write_heartbeat", lambda *a, **k: None)
        self._patch(pm.pm_heartbeat, "remove_heartbeat", lambda *a, **k: None)
        self.clock = FakeClock()
        self._patch(pm, "time", types.SimpleNamespace(time=self.clock.time, sleep=self.clock.sleep,
                                                      monotonic=self.clock.time))
        self.write_plan(True)
        self.seed_journal()

    def _patch(self, obj, name, val):
        p = mock.patch.object(obj, name, val)
        p.start()
        self.addCleanup(p.stop)

    def write_plan(self, flag):
        body = {"plan_id": PLAN_ID}
        if flag is not None:
            body["breakeven_after_first_target"] = flag
        (self.tmp / "plans" / f"{PLAN_ID}.json").write_text(json.dumps(body), encoding="utf-8")

    def seed_journal(self, entries=(("E1", 200, 80000.0),), side="BUY", stop_side="SELL", stop_trigger=79200.0):
        j = lambda t, d: journal.append_event(PLAN_ID, t, d)    # noqa: E731
        for i, (oid, amt, px) in enumerate(entries, 1):
            j("order_placed", {"order_id": oid, "label": f"entry_rung_{i}", "side": side, "amount": amt})
            j("order_filled", {"order_id": oid, "filled_amount": amt, "order_state": "filled", "average_price": px})
        j("order_placed", {"order_id": "S1", "label": "stop_order", "side": stop_side,
                           "amount": sum(e[1] for e in entries), "trigger_price": stop_trigger})
        j("order_placed", {"order_id": "T1", "label": "target_1", "side": stop_side, "amount": 100})
        j("order_placed", {"order_id": "T2", "label": "target_2", "side": stop_side, "amount": 100})

    def events(self, kind):
        return [e["data"] for e in journal.read_events(PLAN_ID) if e["event_type"] == kind]

    def be_events(self):
        return [d for d in self.events("stop_resized") if d.get("reason") == pm.BREAKEVEN_REASON]

    def be_edits(self):
        """Accepted edits that moved the trigger away from the original stop price."""
        return [e for e in self.fake.edits if e[2] is not None and e[2] != 79200.0]

    def manage(self, **kw):
        kw.setdefault("once", "max_seconds" not in kw)       # one poll, or poll on the fake clock until max_seconds
        return pm.manage(PLAN_ID, token="t", **kw)


class FirstLegFillMovesStopToEntry(BreakevenBase):
    def test_stop_trigger_becomes_the_entry_on_the_first_fill(self):
        self.fake.fill_t1()
        res = self.manage()
        self.assertEqual(res["status"], "managing")
        # G1 shrinks the amount at the OLD trigger first, then the breakeven edit moves the trigger to the entry
        self.assertEqual(self.fake.edits, [("S1", 100, 79200.0), ("S1", 100, 80000.0)])
        self.assertEqual(self.fake.orders["S1"]["trigger"], 80000.0)
        be = self.be_events()
        self.assertEqual(len(be), 1)
        self.assertEqual((be[0]["new_stop_price"], be[0]["amount"], be[0]["entry_avg"]), (80000.0, 100, 80000.0))
        self.assertEqual(self.fake.closes, 0)
        self.assertFalse(pm.HALT_PATH.exists())

    def test_not_before_the_first_target_fills(self):
        res = self.manage(max_seconds=20)
        self.assertEqual(res["status"], "managing")
        self.assertEqual(self.fake.edits, [])
        self.assertEqual(self.be_events(), [])

    def test_not_again_once_done_across_many_polls(self):
        self.fake.fill_t1()
        self.manage(max_seconds=20)            # ~11 polls
        self.assertEqual(len(self.be_edits()), 1)
        self.assertEqual(len(self.be_events()), 1)

    def test_not_again_when_the_manager_is_restarted(self):
        self.fake.fill_t1()
        self.manage()
        self.manage()                          # fresh process: state comes from the journal only
        self.manage(max_seconds=10)
        self.assertEqual(len(self.be_edits()), 1)
        self.assertEqual(len(self.be_events()), 1)

    def test_partial_fill_of_the_first_target_does_not_move_the_stop(self):
        self.fake.fill_t1(filled=40)           # 40 of 100: the leg is not filled yet
        self.manage(max_seconds=10)
        self.assertEqual(self.be_edits(), [])
        self.assertEqual(self.fake.edits[0], ("S1", 160, 79200.0))     # G1 shrink still happens, trigger untouched
        self.fake.orders["T1"].update(filled_amount=100, order_state="filled")
        self.fake.pos = 100
        self.manage()
        self.assertEqual(self.be_edits(), [("S1", 100, 80000.0)])      # now it is filled

    def test_no_move_while_the_position_did_not_shrink(self):
        self.fake.orders["T1"].update(filled_amount=100, order_state="filled")     # order says filled, position says 200
        self.manage(max_seconds=6)
        self.assertEqual(self.fake.edits, [])

    def test_plan_without_the_flag_never_moves_the_stop(self):
        for flag in (None, False, "true", 1):
            with self.subTest(flag=flag):
                self.setUp()
                self.write_plan(flag)
                self.fake.fill_t1()
                self.manage(max_seconds=6)
                self.assertEqual(self.be_edits(), [])
                self.assertEqual(self.fake.orders["S1"]["trigger"], 79200.0)

    def test_missing_plan_file_is_no_breakeven_not_a_crash(self):
        (self.tmp / "plans" / f"{PLAN_ID}.json").unlink()
        self.fake.fill_t1()
        self.manage(max_seconds=6)
        self.assertEqual(self.be_edits(), [])

    def test_short_side_trigger_snaps_down_to_the_tick(self):
        for f in (self.tmp / "journal").glob("*.jsonl"):
            f.unlink()
        self.seed_journal(entries=(("E1", 200, 80000.3),), side="SELL", stop_side="BUY", stop_trigger=80800.0)
        self.fake.orders["S1"]["trigger"] = 80800.0
        self.fake.pos, self.fake.mark = -200, 79000.0
        self.fake.fill_t1()
        self.manage()
        self.assertEqual(self.fake.orders["S1"]["trigger"], 80000.0)       # floor(80000.3 / 0.5) * 0.5

    def test_unit_trigger_snap_both_sides(self):
        self.assertEqual(pm._breakeven_trigger(80000.3, True), 80000.5)
        self.assertEqual(pm._breakeven_trigger(80000.3, False), 80000.0)
        self.assertEqual(pm._breakeven_trigger(80000.5, True), 80000.5)    # exact tick stays
        self.assertEqual(pm._breakeven_trigger(80000.5, False), 80000.5)

    def test_ladder_entry_uses_the_inverse_contract_mean(self):
        for f in (self.tmp / "journal").glob("*.jsonl"):
            f.unlink()
        self.seed_journal(entries=(("E1", 100, 80000.0), ("E2", 100, 79000.0)))
        self.assertAlmostEqual(pm._entry_avg_price(PLAN_ID), 79496.855, places=3)
        self.fake.fill_t1()
        self.manage()
        self.assertEqual(self.fake.orders["S1"]["trigger"], 79497.0)       # LONG: up to the tick


class RestartDoesNotRearm(BreakevenBase):
    """Mid-position restart with one leg filled."""

    def seed_after_breakeven(self):
        j = lambda t, d: journal.append_event(PLAN_ID, t, d)    # noqa: E731
        j("order_filled", {"order_id": "T1", "filled_amount": 100, "order_state": "filled", "average_price": 81200.0})
        j("stop_resized", {"order_id": "S1", "amount": 100, "new_stop_price": 79200.0, "reason": "target_fill"})
        j("stop_resized", {"order_id": "S1", "amount": 100, "new_stop_price": 80000.0, "reason": pm.BREAKEVEN_REASON})
        self.fake.fill_t1()
        self.fake.orders["S1"].update(amount=100, trigger=80000.0)

    def test_replay_restores_breakeven_trigger_and_marks_it_done(self):
        self.seed_after_breakeven()
        stop, _targets, _side, _total = pm._plan_orders(PLAN_ID)
        self.assertEqual((stop["trigger"], stop["amount"]), (80000.0, 100))
        self.assertTrue(pm._breakeven_done(PLAN_ID))

    def test_restart_after_breakeven_edits_nothing(self):
        self.seed_after_breakeven()
        self.manage(max_seconds=10)
        self.assertEqual(self.fake.edits, [])
        self.assertEqual(self.fake.stop_places, [])
        self.assertEqual(self.fake.orders["S1"]["trigger"], 80000.0)

    def test_restart_with_a_dead_stop_replaces_it_at_breakeven_not_at_the_original_price(self):
        self.seed_after_breakeven()
        self.fake.orders["S1"]["order_state"] = "cancelled"
        self.manage()
        self.assertEqual(self.fake.stop_places, [("SELL", 100, 80000.0, f"{PLAN_ID}:stop_order")])
        self.assertEqual(self.fake.edits, [])

    def test_restart_after_replace_then_restart_again_keeps_breakeven_and_never_repeats_it(self):
        self.seed_after_breakeven()
        self.fake.orders["S1"]["order_state"] = "cancelled"
        self.manage()                                   # re-places at 80000 (journals stop_replaced + order_placed)
        self.manage()                                   # second restart: the replayed stop is S2 at 80000
        stop, _t, _s, _tot = pm._plan_orders(PLAN_ID)
        self.assertEqual(stop["trigger"], 80000.0)
        self.assertEqual(len(self.fake.stop_places), 1)
        self.assertEqual(len(self.be_events()), 1)

    def test_crash_between_the_leg_fill_and_the_breakeven_edit_arms_exactly_once(self):
        j = lambda t, d: journal.append_event(PLAN_ID, t, d)    # noqa: E731
        j("order_filled", {"order_id": "T1", "filled_amount": 100, "order_state": "filled", "average_price": 81200.0})
        j("stop_resized", {"order_id": "S1", "amount": 100, "new_stop_price": 79200.0, "reason": "target_fill"})
        self.fake.fill_t1()
        self.fake.orders["S1"].update(amount=100)
        self.assertFalse(pm._breakeven_done(PLAN_ID))
        self.manage()
        self.manage()
        self.assertEqual(self.fake.edits, [("S1", 100, 80000.0)])
        self.assertEqual(len(self.be_events()), 1)


class FailsClosed(BreakevenBase):
    def test_rejected_edit_keeps_the_old_stop_retries_five_times_then_stops_trying(self):
        self.fake.fill_t1()
        self.fake.fail_trigger_edits = True
        res = self.manage(max_seconds=40)
        self.assertEqual(res["status"], "managing")
        self.assertEqual(self.fake.failed_edits, pm.BREAKEVEN_MAX_ATTEMPTS)
        self.assertEqual(self.fake.orders["S1"]["trigger"], 79200.0)       # old stop untouched
        self.assertEqual(self.fake.orders["S1"]["amount"], 100)            # still covers the whole position
        self.assertEqual(self.be_events(), [])
        errs = [e for e in self.events("error") if e["context"] == "breakeven_move"]
        self.assertEqual(len(errs), pm.BREAKEVEN_MAX_ATTEMPTS)
        self.assertEqual(self.fake.closes, 0)
        self.assertFalse(pm.HALT_PATH.exists())
        self.assertEqual(self.events("mismatch_halt"), [])

    def test_a_later_good_poll_succeeds_after_transient_rejections(self):
        self.fake.fill_t1()
        self.fake.fail_trigger_edits = True
        self.clock.on_sleep = lambda now: setattr(self.fake, "fail_trigger_edits", now < 1_000_000.0 + 4)
        self.manage(max_seconds=20)
        self.assertEqual(self.fake.orders["S1"]["trigger"], 80000.0)
        self.assertEqual(len(self.be_events()), 1)
        self.assertEqual(self.fake.failed_edits, 2)                        # polls at t=0 and t=2 rejected, t=4 accepted

    def test_mark_at_or_through_the_entry_defers_the_move_without_error(self):
        self.fake.fill_t1()
        self.fake.mark = 79990.0                                           # LONG: mark <= 80000 -> would fire at once
        self.clock.on_sleep = lambda now: setattr(self.fake, "mark", 80500.0 if now >= 1_000_000.0 + 6 else 79990.0)
        self.manage(max_seconds=20)
        self.assertEqual(self.events("error"), [])
        self.assertEqual(self.fake.orders["S1"]["trigger"], 80000.0)
        self.assertEqual(len(self.be_events()), 1)

    def test_deferral_alone_leaves_the_original_stop(self):
        self.fake.fill_t1()
        self.fake.mark = 80000.0                                           # exactly at the entry: still deferred
        self.manage(max_seconds=10)
        self.assertEqual(self.be_edits(), [])
        self.assertEqual(self.fake.orders["S1"]["trigger"], 79200.0)

    def test_unreadable_mark_defers_and_does_not_crash(self):
        self.fake.fill_t1()
        with mock.patch.object(do, "get_ticker", side_effect=OSError("down")):
            self.manage(max_seconds=6)
        self.assertEqual(self.be_edits(), [])
        self.assertEqual(self.events("mismatch_halt"), [])

    def test_unverifiable_entry_price_skips_breakeven_and_says_so(self):
        for f in (self.tmp / "journal").glob("*.jsonl"):
            f.unlink()
        j = lambda t, d: journal.append_event(PLAN_ID, t, d)    # noqa: E731
        j("order_placed", {"order_id": "E1", "label": "entry_limit", "side": "BUY", "amount": 200})
        j("order_filled", {"order_id": "E1", "filled_amount": 200, "order_state": "filled"})      # no average_price
        j("order_placed", {"order_id": "S1", "label": "stop_order", "side": "SELL", "amount": 200,
                           "trigger_price": 79200.0})
        j("order_placed", {"order_id": "T1", "label": "target_1", "side": "SELL", "amount": 100})
        j("order_placed", {"order_id": "T2", "label": "target_2", "side": "SELL", "amount": 100})
        self.assertIsNone(pm._entry_avg_price(PLAN_ID))
        self.fake.fill_t1()
        self.manage(max_seconds=10)
        self.assertEqual(self.be_edits(), [])
        self.assertEqual([e["context"] for e in self.events("error")], ["breakeven_skipped"])     # said once, not per poll
        self.assertEqual(self.fake.orders["S1"]["trigger"], 79200.0)

    def test_manager_still_closes_normally_after_the_breakeven_stop_fires(self):
        self.fake.fill_t1()
        self.manage()
        self.fake.pos = 0                                                  # stop fired on the runner leg
        self.fake.orders["S1"].update(order_state="filled", filled_amount=100)
        res = self.manage()
        self.assertEqual((res["status"], res["target_filled"]), ("closed", 100))


if __name__ == "__main__":
    unittest.main()
