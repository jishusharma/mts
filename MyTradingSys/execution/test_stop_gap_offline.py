"""
F-GAP-1 (fable R3 red team, R3_LIVE_REDTEAM.md): restart with a filled entry but NO journaled stop.

The executor can die after journaling the entry fill (executor.py order_filled) and before journaling the
protective stop (executor.py ensure_stop order_placed). On restart position_manager used to raise
ManagerHalted("journal has no entry/stop - nothing to manage") before its S3 loop ran, leaving the open
position naked. Now it fails closed: HALT file + mismatch_halt first, cancel entries/targets, close the
position, verify flat, and only then sweep any unjournaled stop.

Covers (MOVED_RULES live-path): restart/reset state (crash window, re-run after the halt), position that does
not match the journal (non-trade move / outside change), API errors (get_position, close_position, auth).
Journal and HALT are redirected to a temp dir. No network. Run from MyTradingSys/execution:
    python -m unittest test_stop_gap_offline -v
"""
import shutil
import tempfile
import unittest
from pathlib import Path

import deribit_orders as do
import journal
import position_manager as pm


class FakeExchange:
    def __init__(self, pos=100):
        self.pos = pos
        self.calls = []                 # (name, arg) in call order
        self.close_fails = False        # close_position raises and the position stays
        self.position_read_errors = 0   # first N get_position calls raise
        self.auth_fails = False

    def authenticate(self):
        self.calls.append(("authenticate", None))
        if self.auth_fails:
            raise do.DeribitError("private/auth", {"code": 13009, "message": "unauthorized"})
        return "tok"

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        self.calls.append(("get_position", None))
        if self.position_read_errors:
            self.position_read_errors -= 1
            raise do.DeribitError("private/get_position", {"code": 10028, "message": "too_many_requests"})
        return {"size": self.pos}

    def get_order_state(self, token, oid):
        return {"order_state": "order_not_found", "filled_amount": 0, "average_price": 0}

    def stop_market(self, token, instrument, side, amount, trigger_price, label, trigger="mark_price"):
        self.calls.append(("stop_market", label))
        return {"order": {"order_id": "S9", "amount": amount, "order_state": "untriggered"}}

    def edit(self, token, oid, amount=None, price=None, trigger_price=None):
        return {"order": {"order_id": oid, "amount": amount}}

    def cancel(self, token, oid):
        self.calls.append(("cancel", oid))
        return {"order_id": oid, "order_state": "cancelled"}

    def cancel_by_label(self, token, label, currency="BTC"):
        self.calls.append(("cancel_by_label", label))
        return 0

    def close_position(self, token, instrument="BTC-PERPETUAL"):
        self.calls.append(("close_position", None))
        if self.close_fails:
            raise do.DeribitError("private/close_position", {"code": 11044, "message": "not_open_order"})
        self.pos = 0
        return {"order": {"order_id": "X1", "filled_amount": 100, "order_state": "filled"}}

    def names(self):
        return [n for n, _ in self.calls]


PATCHED = ("authenticate", "get_position", "get_order_state", "stop_market", "edit", "cancel",
           "cancel_by_label", "close_position")


class StopGapTests(unittest.TestCase):
    PLAN = "gap_plan"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="stopgap_"))
        self._orig_dir, self._orig_halt = journal.JOURNAL_DIR, pm.HALT_PATH
        self._orig_sleep = pm.time.sleep
        journal.JOURNAL_DIR = self.tmp / "journal"
        pm.HALT_PATH = self.tmp / "HALT"
        self.fake = FakeExchange()
        self._orig = {n: getattr(do, n) for n in PATCHED}
        for n in PATCHED:
            setattr(do, n, getattr(self.fake, n))
        pm.time.sleep = lambda s: None   # NETRETRY backoff: no wall-clock wait

    def tearDown(self):
        for n, fn in self._orig.items():
            setattr(do, n, fn)
        pm.time.sleep = self._orig_sleep
        journal.JOURNAL_DIR, pm.HALT_PATH = self._orig_dir, self._orig_halt
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _crash_window_journal(self, side="BUY", intent=False):
        if intent:
            journal.append_event(self.PLAN, "intent", {"env": do.active_env(), "compiled": {
                "entry_orders": [{"label": "entry_1"}, {"label": "entry_2"}],
                "target_orders": [{"label": "target_1"}],
                "stop_order": {"label": "stop", "side": "SELL" if side == "BUY" else "BUY"}}})
        journal.append_event(self.PLAN, "order_placed", {"order_id": "E1", "label": "entry_1", "side": side,
                                                         "amount": 100})
        journal.append_event(self.PLAN, "order_filled", {"order_id": "E1", "filled_amount": 100,
                                                         "order_state": "filled", "average_price": 80000.0})

    def _manage(self, token="tok"):
        with self.assertRaises(pm.ManagerHalted) as cm:
            pm.manage(self.PLAN, once=True, token=token)
        return str(cm.exception)

    def test_filled_entry_no_stop_is_flattened_and_halted(self):
        self._crash_window_journal()
        msg = self._manage()
        self.assertEqual(self.fake.pos, 0, f"open position left naked: {msg}")
        self.assertIn("flattened + halted", msg)
        self.assertTrue(pm.HALT_PATH.exists(), "HALT file must survive the process")
        self.assertTrue(journal.reconstruct_belief(self.PLAN)["halted"])
        n = self.fake.names()
        self.assertIn(("cancel", "E1"), self.fake.calls)
        self.assertIn(("cancel_by_label", f"{self.PLAN}:entry_1"), self.fake.calls)
        # C3 order: entries swept before the close; the stop label only after the position is flat
        self.assertLess(n.index("cancel"), n.index("close_position"))
        stop_sweep = self.fake.calls.index(("cancel_by_label", f"{self.PLAN}:stop"))
        self.assertGreater(stop_sweep, n.index("close_position"))
        self.assertNotIn("stop_market", n)

    def test_intent_labels_are_swept_including_unjournaled_entries_and_targets(self):
        self._crash_window_journal(intent=True)
        self._manage()
        for lab in ("entry_1", "entry_2", "target_1", "stop"):
            self.assertIn(("cancel_by_label", f"{self.PLAN}:{lab}"), self.fake.calls, lab)

    def test_short_plan_is_flattened(self):
        self.fake.pos = -100
        self._crash_window_journal(side="SELL")
        self.assertIn("flattened + halted", self._manage())
        self.assertEqual(self.fake.pos, 0)

    def test_restart_after_halt_does_not_trade_again(self):
        self._crash_window_journal()
        self._manage()
        before = len(self.fake.calls)
        self.fake.pos = 100   # position reappears (outside change): a respawn must not act on a halted plan
        msg = self._manage()
        self.assertIn("already halted", msg)
        self.assertNotIn("close_position", self.fake.names()[before:])

    def test_position_differs_from_journal_is_still_closed(self):
        # non-trade / outside change: exchange size 37 != journaled 100 - close whatever is there
        self.fake.pos = 37
        self._crash_window_journal()
        self._manage()
        self.assertEqual(self.fake.pos, 0)
        self.assertIn("close_position", self.fake.names())

    def test_already_flat_halts_without_close(self):
        self.fake.pos = 0   # e.g. an unjournaled stop already fired
        self._crash_window_journal()
        msg = self._manage()
        self.assertIn("flattened + halted", msg)
        self.assertNotIn("close_position", self.fake.names())
        self.assertTrue(pm.HALT_PATH.exists())

    def test_close_api_error_reports_flatten_failed_and_keeps_stop_sweep_off(self):
        self.fake.close_fails = True
        self._crash_window_journal()
        msg = self._manage()
        self.assertIn("FLATTEN FAILED", msg)
        self.assertTrue(pm.HALT_PATH.exists())
        self.assertNotIn(("cancel_by_label", f"{self.PLAN}:stop"), self.fake.calls)

    def test_position_read_error_still_attempts_close(self):
        self.fake.position_read_errors = 1
        self._crash_window_journal()
        msg = self._manage()
        self.assertIn("flattened + halted", msg)
        self.assertEqual(self.fake.pos, 0)

    def test_auth_failure_still_writes_halt(self):
        self.fake.auth_fails = True
        self._crash_window_journal()
        msg = self._manage(token=None)
        self.assertIn("FLATTEN FAILED", msg)
        self.assertTrue(pm.HALT_PATH.exists())
        self.assertTrue(journal.reconstruct_belief(self.PLAN)["halted"])

    def test_no_fill_keeps_old_nothing_to_manage_without_halt(self):
        journal.append_event(self.PLAN, "order_placed", {"order_id": "E1", "label": "entry_1", "side": "BUY",
                                                         "amount": 100})
        msg = self._manage()
        self.assertIn("nothing to manage", msg)
        self.assertFalse(pm.HALT_PATH.exists())
        self.assertEqual(self.fake.calls, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
