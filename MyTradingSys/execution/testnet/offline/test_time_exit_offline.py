"""
Offline tests for the max_hold_minutes time exit in position_manager (tag: timeexit).

Fake exchange + fake clock (position_manager's `time` reference only). The clock is anchored
to the journal's real entry-fill timestamp so "elapsed since entry fill" is exact and no test sleeps.
No network. Run:  python -m unittest test_time_exit_offline -v
"""
import json
import shutil
import types
import unittest
from pathlib import Path

import deribit_orders as do
import journal
import position_manager as pm

PLANS_DIR = getattr(pm, "PLANS_DIR", Path(pm.__file__).resolve().parent / "plans")
PATCHED = ("authenticate", "get_position", "get_order_state", "stop_market", "edit", "cancel",
           "cancel_by_label", "close_position")
MAX_HOLD_MIN = 2  # -> 120 s


class FakeExchange:
    def __init__(self, close_fails=False):
        self.pos = 100
        self.close_fails = close_fails
        self.calls = []          # ordered ("close"|"cancel"|"cancel_by_label", arg, clock_now)
        self.clock = None

    def _t(self):
        return self.clock.now if self.clock else None

    def authenticate(self):
        return "tok"

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        return {"size": self.pos}

    def get_order_state(self, token, oid):
        return {"order_state": "untriggered", "filled_amount": 0, "average_price": 0}

    def stop_market(self, *a, **k):
        raise AssertionError("stop must never be re-placed in these scenarios")

    def edit(self, token, oid, amount=None, price=None, trigger_price=None):
        return {"order": {"order_id": oid}}

    def cancel(self, token, oid):
        self.calls.append(("cancel", oid, self._t()))
        return {"order_id": oid}

    def cancel_by_label(self, token, label, currency="BTC"):
        self.calls.append(("cancel_by_label", label, self._t()))
        return 0

    def close_position(self, token, instrument="BTC-PERPETUAL"):
        self.calls.append(("close", None, self._t()))
        if self.close_fails:
            raise RuntimeError("close rejected")
        self.pos = 0
        return {"order": {"order_id": "C1", "filled_amount": 100}}


class FakeClock:
    def __init__(self, now):
        self.now = now

    def time(self):
        return self.now

    def sleep(self, s):
        self.now += s


class TimeExitTests(unittest.TestCase):
    plan_id = "timeexit_t1"

    def setUp(self):
        self.fake = FakeExchange()
        self._orig = {n: getattr(do, n) for n in PATCHED}
        for n in PATCHED:
            setattr(do, n, getattr(self.fake, n))
        self._orig_time = pm.time
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        pm.HALT_PATH.unlink(missing_ok=True)
        journal.append_event(self.plan_id, "order_placed", {"order_id": "E1", "label": "entry_1",
                                                            "side": "BUY", "amount": 100})
        journal.append_event(self.plan_id, "order_filled", {"order_id": "E1", "filled_amount": 100,
                                                            "order_state": "filled"})
        journal.append_event(self.plan_id, "order_placed", {"order_id": "S1", "label": "stop_order",
                                                            "side": "SELL", "amount": 100, "trigger_price": 79000.0})
        journal.append_event(self.plan_id, "order_placed", {"order_id": "T1", "label": "target_1",
                                                            "side": "SELL", "amount": 100})
        self.entry_ts = journal.read_events(self.plan_id)[1]["ts"]
        PLANS_DIR.mkdir(exist_ok=True)
        self.plan_file = PLANS_DIR / f"{self.plan_id}.json"
        self.plan_file.write_text(json.dumps({"plan_id": self.plan_id, "max_hold_minutes": MAX_HOLD_MIN}),
                                  encoding="utf-8")

    def tearDown(self):
        for n, fn in self._orig.items():
            setattr(do, n, fn)
        pm.time = self._orig_time
        self.plan_file.unlink(missing_ok=True)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        pm.HALT_PATH.unlink(missing_ok=True)

    def _clock(self, elapsed):
        c = FakeClock(self.entry_ts + elapsed)
        self.fake.clock = c
        pm.time = types.SimpleNamespace(time=c.time, sleep=c.sleep, monotonic=c.time)
        return c

    def _events(self, kind):
        return [e for e in journal.read_events(self.plan_id) if e["event_type"] == kind]

    def test_time_exit_fires_and_journals_normal_close(self):
        self._clock(MAX_HOLD_MIN * 60 + 5)
        res = pm.manage(self.plan_id, max_seconds=60, token="t")
        self.assertEqual(res["status"], "closed")
        self.assertEqual(res["stop_state"], "time_exit")
        self.assertEqual(self.fake.pos, 0)
        self.assertEqual(len(self._events("time_exit")), 1)
        rec = self._events("reconciliation")
        self.assertEqual(rec[-1]["data"]["result"], "position_closed")

    def test_close_first_then_cancel_stop_and_targets(self):
        self._clock(MAX_HOLD_MIN * 60 + 5)
        pm.manage(self.plan_id, max_seconds=60, token="t")
        kinds = [c[0] for c in self.fake.calls]
        self.assertEqual(kinds[0], "close", f"close must precede every cancel: {kinds}")
        cancelled = [c[1] for c in self.fake.calls if c[0] == "cancel"]
        self.assertIn("S1", cancelled)
        self.assertIn("T1", cancelled)

    def test_close_failure_keeps_stop_and_targets(self):
        self.fake.close_fails = True
        self._clock(MAX_HOLD_MIN * 60 + 5)
        res = pm.manage(self.plan_id, max_seconds=30, token="t")
        self.assertEqual(res["status"], "managing")
        self.assertEqual(res["position"], 100)
        closes = [c for c in self.fake.calls if c[0] == "close"]
        self.assertGreaterEqual(len(closes), 1, "time exit must be attempted")
        self.assertLessEqual(len(closes), 4, "retries must be throttled")
        self.assertEqual([c for c in self.fake.calls if c[0] != "close"], [],
                         "stop/targets must not be cancelled while the position is open")
        self.assertTrue(any(e["data"].get("context") == "time_exit_failed" for e in self._events("error")))

    def test_no_false_halt(self):
        self._clock(MAX_HOLD_MIN * 60 + 5)
        res = pm.manage(self.plan_id, max_seconds=60, token="t")  # would raise ManagerHalted on a false halt
        self.assertEqual(res["status"], "closed")
        self.assertEqual(self._events("mismatch_halt"), [])
        self.assertFalse(pm.HALT_PATH.exists())

    def test_no_exit_before_limit(self):
        c = self._clock(MAX_HOLD_MIN * 60 - 10)
        pm.manage(self.plan_id, max_seconds=30, token="t")
        closes = [x for x in self.fake.calls if x[0] == "close"]
        self.assertEqual(len(closes), 1, "must exit once the limit is crossed")
        self.assertGreater(closes[0][2] - self.entry_ts, MAX_HOLD_MIN * 60, "must not exit before the limit")

    def test_no_max_hold_means_no_time_exit(self):
        self.plan_file.write_text(json.dumps({"plan_id": self.plan_id}), encoding="utf-8")
        self._clock(10 * 3600)
        res = pm.manage(self.plan_id, max_seconds=10, token="t")
        self.assertEqual(res["status"], "managing")
        self.assertEqual(self.fake.calls, [])
        # sanity that the harness would have exited had a limit been set: covered by the tests above


if __name__ == "__main__":
    unittest.main()
