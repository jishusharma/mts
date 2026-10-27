"""
R3 scratch test (NOT shipped - proves the stop-gap finding against current code).

Scenario: the executor is killed AFTER the entry fill is journaled but BEFORE the
protective stop order is journaled (the crash window between executor.py:461
entry order_filled append and :338 stop order_placed append). On restart the
position_manager replays the journal, sees a filled entry but NO stop, and must
not leave the open position naked.

Desired fail-closed behavior: the position is auto-protected/flattened (S3 bound)
or the manager keeps the protective stop live. Current code instead raises
ManagerHalted("journal has no entry/stop - nothing to manage") at
position_manager._manage_impl BEFORE the S3 loop ever runs, so the position stays
fully unprotected - the 4s MAX_UNPROTECTED_SECONDS bound is unreachable in this
state, and only the operator respawn loop (MAX_RESPAWNS=3 -> alert) sees it.

Run (from a dir where execution/ modules import):
    cd MyTradingSys/execution && python -m unittest scratch_r3.test_stop_gap_r3 -v
"""
import shutil
import sys
import types
import unittest
from pathlib import Path

EXEC_DIR = Path(__file__).resolve().parents[1] / "MyTradingSys" / "execution"
sys.path.insert(0, str(EXEC_DIR))

import deribit_orders as do
import journal
import position_manager as pm


def _order(oid, direction, amount, order_type, label, reduce_only, state, filled=0,
           avg=80000.0, trigger_price=None):
    return dict(order_id=oid, direction=direction.lower(), amount=amount, order_type=order_type,
                label=label, reduce_only=reduce_only, order_state=state, filled_amount=filled,
                average_price=avg, trigger_price=trigger_price)


class NakedPositionExchange:
    """Position fixed at 100 the whole test. close_position flattens it."""

    def __init__(self):
        self.pos = 100
        self.cancelled = False
        self.n = 0

    def _new_id(self):
        self.n += 1
        return f"O{self.n}"

    def authenticate(self):
        return "tok"

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        return {"size": self.pos}

    def get_order_state(self, token, oid):
        return {"order_state": "order_not_found", "filled_amount": 0, "average_price": 0}

    def stop_market(self, token, instrument, side, amount, trigger_price, label, trigger="mark_price"):
        return {"order": _order(self._new_id(), side, amount, "stop_market", label, True,
                                "untriggered", trigger_price=trigger_price)}

    def edit(self, token, oid, amount=None, price=None, trigger_price=None):
        return {"order": {"order_id": oid, "amount": amount}}

    def cancel(self, token, oid):
        return {"order_id": oid, "order_state": "cancelled"}

    def cancel_by_label(self, token, label, currency="BTC"):
        return 0

    def close_position(self, token, instrument="BTC-PERPETUAL"):
        self.pos = 0
        self.cancelled = True
        return {"order": _order(self._new_id(), "SELL", 100, "market", "emergency_close", True,
                                "filled", filled=100)}


PATCHED_NAMES = ("authenticate", "get_position", "get_order_state", "stop_market", "edit",
                 "cancel", "cancel_by_label", "close_position")


class StopGapOnRestartTests(unittest.TestCase):
    def setUp(self):
        self.fake = NakedPositionExchange()
        self._orig = {n: getattr(do, n) for n in PATCHED_NAMES}
        for n in PATCHED_NAMES:
            setattr(do, n, getattr(self.fake, n))
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        pm.HALT_PATH.unlink(missing_ok=True)
        self.plan_id = "stop_gap_r3"
        # Crash window: entry filled and journaled, but the stop was NEVER journaled.
        journal.append_event(self.plan_id, "order_placed", {"order_id": "E1", "label": "entry_1",
                                                             "side": "BUY", "amount": 100})
        journal.append_event(self.plan_id, "order_filled", {"order_id": "E1", "filled_amount": 100,
                                                             "order_state": "filled"})
        # no "stop" order_placed event - that is the gap.

    def tearDown(self):
        for n, fn in self._orig.items():
            setattr(do, n, fn)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        pm.HALT_PATH.unlink(missing_ok=True)

    def test_restart_with_filled_entry_and_no_journaled_stop_does_not_leave_position_naked(self):
        try:
            pm.manage(self.plan_id, once=True, token="tok")
        except pm.ManagerHalted as e:
            # The manager HALT is acceptable - but a fail-closed halt on an OPEN position
            # must have protected it (flattened it or left a live stop), not just given up.
            self.assertTrue(
                self.fake.cancelled or self.fake.pos == 0,
                "position_manager halted without protecting the open position: "
                f"|pos|={self.fake.pos}, close_position called={self.fake.cancelled} "
                "(ManagerHalted: %s)" % (e,))
            return
        # If manage returned normally the position should also be flat.
        self.assertTrue(self.fake.cancelled or self.fake.pos == 0,
                        "manage returned but the open position was left unprotected "
                        f"(|pos|={self.fake.pos})")


if __name__ == "__main__":
    sys.argv = [__file__]
    unittest.main(verbosity=2)
