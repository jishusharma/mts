"""
R3 F-GAP-1 regression tests: restart with a FILLED entry journaled but NO stop journaled (executor crash window
between executor.py entry order_filled and stop order_placed). position_manager must fail closed: write HALT, flatten
the plan's own position, sweep the plan's labels, journal everything, and never claim 'flattened' if a step failed.

journal.JOURNAL_DIR and position_manager.HALT_PATH are redirected to a temp dir: the real ones are never touched.
Run: python MyTradingSys/execution/test_stop_gap_offline.py
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import deribit_orders as do
import journal
import position_manager as pm


def _order(oid, side, amount, state="filled", filled=0):
    return dict(order_id=oid, direction=side.lower(), amount=amount, order_state=state, filled_amount=filled)


class Fake:
    def __init__(self, pos=100):
        self.pos = pos
        self.closed = 0
        self.swept = []
        self.close_mode = "ok"      # ok | raise | noop | error_reply
        self.sweep_raises = False

    def authenticate(self):
        return "tok"

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        return {"size": self.pos}

    def close_position(self, token, instrument="BTC-PERPETUAL"):
        self.closed += 1
        if self.close_mode == "raise":
            raise RuntimeError("close boom")
        if self.close_mode == "error_reply":
            self.pos = 0
            return {"order": None}          # malformed reply -> TypeError in the caller
        if self.close_mode == "ok":
            self.pos = 0
        return {"order": _order("C1", "SELL", 100, filled=100)}

    def cancel_by_label(self, token, label, currency="BTC"):
        self.swept.append(label)
        if self.sweep_raises:
            raise RuntimeError("sweep boom")
        return 0


NAMES = ("authenticate", "get_position", "close_position", "cancel_by_label")


class StopGapTests(unittest.TestCase):
    PLAN = "stop_gap_r3"

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_jd, self.old_halt = journal.JOURNAL_DIR, pm.HALT_PATH
        journal.JOURNAL_DIR = Path(self.tmp.name) / "journal"
        pm.HALT_PATH = Path(self.tmp.name) / "HALT"
        self.fake = Fake()
        self._orig = {n: getattr(do, n) for n in NAMES}
        for n in NAMES:
            setattr(do, n, getattr(self.fake, n))
        self.old_append = journal.append_event
        journal.append_event(self.PLAN, "order_placed", {"order_id": "E1", "label": "entry_1", "side": "BUY",
                                                         "amount": 100})
        journal.append_event(self.PLAN, "order_filled", {"order_id": "E1", "filled_amount": 100,
                                                         "order_state": "filled"})

    def tearDown(self):
        journal.append_event = self.old_append
        for n, fn in self._orig.items():
            setattr(do, n, fn)
        journal.JOURNAL_DIR, pm.HALT_PATH = self.old_jd, self.old_halt
        self.tmp.cleanup()

    def run_manage(self):
        with self.assertRaises(pm.ManagerHalted) as cm:
            pm.manage(self.PLAN, once=True, token="tok")
        return str(cm.exception)

    def events(self, t):
        return [e for e in journal.read_events(self.PLAN) if e["event_type"] == t]

    def test_happy_path_flattens_halts_and_sweeps_right_labels(self):
        msg = self.run_manage()
        self.assertEqual(self.fake.pos, 0)
        self.assertTrue(pm.HALT_PATH.exists(), "HALT not written")
        self.assertEqual(len(self.events("mismatch_halt")), 1)
        self.assertIn("flattened + halted", msg)
        for lab in ("entry_1", "stop_order", "stop_order_trailing"):
            self.assertIn(f"{self.PLAN}:{lab}", self.fake.swept)
        self.assertNotIn(f"{self.PLAN}:", self.fake.swept)       # the old no-op prefix sweep is gone
        self.assertEqual(len(self.events("order_placed")), 2)     # entry + emergency_close journaled

    def test_idempotent_second_run(self):
        self.run_manage()
        n_closed = self.fake.closed
        msg = self.run_manage()                                    # plan is already halted in the journal
        self.assertEqual(self.fake.closed, n_closed)
        self.assertIn("halted", msg)

    def test_close_raises_is_not_claimed_flattened(self):
        self.fake.close_mode = "raise"
        msg = self.run_manage()
        self.assertEqual(self.fake.pos, 100)
        self.assertNotIn("flattened + halted", msg)
        self.assertIn("close boom", msg)
        self.assertTrue(pm.HALT_PATH.exists())
        self.assertTrue(self.events("error"))

    def test_close_error_reply(self):
        self.fake.close_mode = "error_reply"
        msg = self.run_manage()
        self.assertEqual(self.fake.pos, 0)    # close did fill; a bad reply is journaled, flat is verified
        self.assertIn("close_position", msg)
        self.assertNotIn("flattened + halted", msg)

    def test_still_not_flat_after_close(self):
        self.fake.close_mode = "noop"
        msg = self.run_manage()
        self.assertIn("FLATTEN FAILED", msg)
        self.assertIn("position 100 after close_position", msg)
        self.assertEqual(self.fake.swept, [])   # no sweep while still exposed

    def test_sweep_raises_reported(self):
        self.fake.sweep_raises = True
        msg = self.run_manage()
        self.assertEqual(self.fake.pos, 0)
        self.assertNotIn("flattened + halted", msg)
        self.assertIn("sweep boom", msg)
        self.assertTrue(self.events("error"))

    def test_journal_write_raises_still_halts_and_closes(self):
        real = journal.append_event

        def boom(plan_id, event_type, data):
            if event_type == "mismatch_halt":
                raise OSError("disk full")
            return real(plan_id, event_type, data)
        journal.append_event = boom
        msg = self.run_manage()
        self.assertTrue(pm.HALT_PATH.exists())
        self.assertEqual(self.fake.pos, 0)
        self.assertIn("disk full", msg)
        self.assertNotIn("flattened + halted", msg)

    def test_position_not_this_plans_is_not_closed(self):
        for pos in (-100, 250):       # opposite side; larger than the plan's fill
            self.fake.pos = pos
            self.fake.closed = 0
            pm.HALT_PATH.unlink(missing_ok=True)
            jp = journal._journal_path(self.PLAN)
            keep = [ln for ln in jp.read_text(encoding="utf-8").splitlines() if "mismatch_halt" not in ln]
            jp.write_text("\n".join(keep) + "\n", encoding="utf-8")
            msg = self.run_manage()
            self.assertEqual(self.fake.closed, 0, f"closed a foreign position {pos}")
            self.assertEqual(self.fake.pos, pos)
            self.assertIn("does not match", msg)
            self.assertTrue(pm.HALT_PATH.exists())

    def test_already_flat_no_global_halt(self):
        self.fake.pos = 0
        msg = self.run_manage()
        self.assertFalse(pm.HALT_PATH.exists(), "global HALT written for a flat account")
        self.assertEqual(self.fake.closed, 0)
        self.assertEqual(len(self.events("mismatch_halt")), 1)
        self.assertIn("flattened + halted", msg)
        self.assertIn(f"{self.PLAN}:entry_1", self.fake.swept)

    def test_real_dirs_untouched(self):
        self.assertNotEqual(journal.JOURNAL_DIR, self.old_jd)
        self.assertNotEqual(pm.HALT_PATH, self.old_halt)


if __name__ == "__main__":
    sys.argv = [__file__]
    unittest.main(verbosity=2)
