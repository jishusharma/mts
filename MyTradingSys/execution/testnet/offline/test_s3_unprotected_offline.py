"""
Offline test for S3 (G-d, 2026-09-28): position_manager's explicit
MAX_UNPROTECTED_SECONDS / unprotected_since invariant.

Uses a fake clock (monkeypatched onto position_manager's `time` reference
only - not the global time module, so journal.py's real timestamps and any
other test running in the same process are unaffected) so the test does not
actually sleep in wall-clock time. The fake exchange always reports the
stop's state as "cancelled" (simulating a stubborn condition where every
re-place attempt is accepted by the exchange but never actually holds), so
the only thing that should stop the loop is the explicit time bound - not
the (now-removed) one-attempt retry counter.

No network. Run:
    python3 -m unittest test_s3_unprotected_offline -v
"""
import shutil
import types
import unittest

import deribit_orders as do
import journal
import position_manager as pm


def _order(oid, direction, amount, order_type, label, reduce_only, state, filled=0, avg=80000.0,
          trigger_price=None):
    return dict(order_id=oid, direction=direction.lower(), amount=amount, order_type=order_type,
                label=label, reduce_only=reduce_only, order_state=state, filled_amount=filled,
                average_price=avg, trigger_price=trigger_price)


class StubbornStopExchange:
    """Position fixed at 100 the whole test. Every stop_market call succeeds
    (creates a new resting order) but get_order_state ALWAYS reports it as
    "cancelled" regardless of which order_id is asked about or what was just
    created - simulating a persistent problem where the position never
    actually becomes protected, however many times we retry."""

    def __init__(self):
        self.pos = 100
        self.n = 0
        self.stop_market_calls = 0
        self.cancelled = False

    def _new_id(self):
        self.n += 1
        return f"O{self.n}"

    def authenticate(self):
        return "tok"

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        return {"size": self.pos}

    def get_order_state(self, token, oid):
        return {"order_state": "cancelled", "filled_amount": 0, "average_price": 0}

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
        self.cancelled = True
        oid = self._new_id()
        return {"order": _order(oid, "SELL", 100, "market", "emergency_close", True, "filled", filled=100)}


PATCHED_NAMES = ("authenticate", "get_position", "get_order_state", "stop_market", "edit", "cancel",
                 "cancel_by_label", "close_position")


class FakeClock:
    """Replaces position_manager's `time` reference (module-local rebind,
    not the global `time` module) so time.time()/time.sleep() are
    deterministic and instantaneous."""

    def __init__(self):
        self.now = 0.0

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class S3UnprotectedTimeBoundTests(unittest.TestCase):
    def setUp(self):
        self.fake = StubbornStopExchange()
        self._orig = {name: getattr(do, name) for name in PATCHED_NAMES}
        for name in PATCHED_NAMES:
            setattr(do, name, getattr(self.fake, name))
        self._orig_time = pm.time
        self.clock = FakeClock()
        pm.time = types.SimpleNamespace(time=self.clock.time, sleep=self.clock.sleep, monotonic=self.clock.time)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        pm.HALT_PATH.unlink(missing_ok=True)  # FIX3 M5: flatten_halt now writes HALT (sandbox copy)

        self.plan_id = "s3_unprotected"
        entry_oid, stop_oid = "E1", "S1"
        journal.append_event(self.plan_id, "order_placed", {"order_id": entry_oid, "label": "entry_1",
                                                             "side": "BUY", "amount": 100})
        journal.append_event(self.plan_id, "order_filled", {"order_id": entry_oid, "filled_amount": 100,
                                                             "order_state": "filled"})
        journal.append_event(self.plan_id, "order_placed", {"order_id": stop_oid, "label": "stop_order",
                                                             "side": "SELL", "amount": 100,
                                                             "trigger_price": 79000.0})

    def tearDown(self):
        for name, fn in self._orig.items():
            setattr(do, name, fn)
        pm.time = self._orig_time
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        pm.HALT_PATH.unlink(missing_ok=True)  # FIX3 M5: flatten_halt now writes HALT (sandbox copy)

    def test_flattens_only_after_max_unprotected_seconds_elapsed(self):
        with self.assertRaises(pm.ManagerHalted) as ctx:
            pm.manage(self.plan_id, once=False, token="t")

        self.assertIn(f"MAX_UNPROTECTED_SECONDS={pm.MAX_UNPROTECTED_SECONDS}", str(ctx.exception))
        self.assertTrue(self.fake.cancelled, "position must have been flattened")
        # the loop must have kept retrying the re-place across more than one
        # poll before giving up - it must not halt on the very first attempt
        # (that would mean the old one-attempt counter, not the time bound,
        # is what fired).
        self.assertGreater(self.fake.stop_market_calls, 1,
                           "must retry the re-place at least once before the time bound trips")
        # the fake clock must show the elapsed time actually exceeded the bound
        self.assertGreater(self.clock.now, pm.MAX_UNPROTECTED_SECONDS)


if __name__ == "__main__":
    unittest.main()
