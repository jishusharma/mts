"""
10041 settlement_in_progress on an entry create (2026-10-15): the plan is skipped, NO HALT, no order, no position; any other code (10009
not_enough_funds, an unknown code) and a 10041 after an earlier entry went in still fail closed and write HALT. Reuses the fake exchange of
test_gh_executor_offline. No network.
"""
import shutil
import unittest
from pathlib import Path

import deribit_orders as do
import journal
import executor
from test_gh_executor_offline import FakeExchange, PATCHED_NAMES, _compiled


class RejectingExchange(FakeExchange):
    def __init__(self, code, after=0):
        super().__init__()
        self.code, self.after, self.creates = code, after, 0

    def _place(self, direction, amount, order_type, label, reduce_only, script):
        self.creates += 1
        if self.creates > self.after:
            raise do.DeribitError("private/" + direction.lower(), {"code": self.code, "message": "rejected"})
        return super()._place(direction, amount, order_type, label, reduce_only, script)


class SettlementSkipTests(unittest.TestCase):
    def setUp(self):
        self._orig = {n: getattr(do, n) for n in PATCHED_NAMES}
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        executor.HALT_PATH.unlink(missing_ok=True)

    def tearDown(self):
        for n, fn in self._orig.items():
            setattr(do, n, fn)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        executor.HALT_PATH.unlink(missing_ok=True)

    def install(self, fake):
        self.fake = fake
        for n in PATCHED_NAMES:
            setattr(do, n, getattr(fake, n))

    def test_10041_on_first_entry_skips_without_halt_or_order(self):
        self.install(RejectingExchange(10041))
        r = executor.execute_plan(_compiled("st_a"))
        self.assertEqual(r["status"], "no_fill")          # auto_trader: '"no_fill" in out' -> no manager spawned
        self.assertEqual(r["reason"], "entry_skipped_settlement")
        self.assertFalse(executor.HALT_PATH.exists(), "10041 must not write HALT")
        self.assertEqual(self.fake.creates, 1, "no retry storm: exactly one create attempt")
        self.assertEqual(self.fake.pos, 0)
        self.assertEqual(self.fake.get_open_orders("t"), [])
        types = [e["event_type"] for e in journal.read_events("st_a")]
        self.assertIn("entry_skipped_settlement", types)
        self.assertNotIn("mismatch_halt", types)

    def test_no_stale_halt_state_for_next_plan_after_skip(self):
        self.install(RejectingExchange(10041))
        executor.execute_plan(_compiled("st_b"))
        self.install(FakeExchange())                       # settlement over: a fresh plan runs normally
        r = executor.execute_plan(_compiled("st_b2"))
        self.assertEqual(r["status"], "entry_filled_stop_placed")

    def test_other_codes_still_halt(self):
        for code in (10009, 99999):
            with self.subTest(code=code):
                executor.HALT_PATH.unlink(missing_ok=True)
                shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
                self.install(RejectingExchange(code))
                with self.assertRaises(executor.ExecutionHalted):
                    executor.execute_plan(_compiled("st_c%d" % code))
                self.assertTrue(executor.HALT_PATH.exists(), "code %d must still write HALT" % code)

    def test_10041_after_an_earlier_entry_still_fails_closed(self):
        self.install(RejectingExchange(10041, after=1))
        c = _compiled("st_d")
        c["entry_orders"].append(dict(c["entry_orders"][0], label="entry_2"))
        with self.assertRaises(executor.ExecutionHalted):
            executor.execute_plan(c)
        self.assertTrue(executor.HALT_PATH.exists())
        self.assertEqual(self.fake.pos, 0, "the filled first entry is flattened")


if __name__ == "__main__":
    unittest.main()
