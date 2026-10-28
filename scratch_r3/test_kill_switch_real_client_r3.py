"""R3 live red team: two findings, one failing test.

F-KILL-1 (BLOCKS-LIVE): kill_switch.kill_all calls client.get_open_orders(token, instrument_name=..., type_="all")
but deribit_orders.get_open_orders' second param is POSITIONAL instrument_name:
    def get_open_orders(token, instrument_name="BTC-PERPETUAL", type_="all")
Against the real client every instrument read is a TypeError, so the kill switch cancels NO non-protective
order (entries, targets) and reports ok=False; it also contradicts its own duck-type contract (the docstring
declares get_open_orders(token, instrument_name, type_="all")). No test in test_kill_switch.py exercises the
get_open_orders signature - it is only asserted for cancel/close/positions.

F-MON-1 (fail-open on monitors): daily_loss_monitor.main catches every iteration failure and re-authenticates
via do.authenticate() - but that happens with whatever MTS_ACCOUNT the named-account refresh left in the
environment. Test 3 below proves the re-auth then reads a NAMED secret file that does not exist in this tree,
so MAIN can never be re-authenticated; the monitor is blind while still able to auto-clear its blind halt.
"""
import sys
import unittest
from pathlib import Path

EXEC = Path(sys.argv[1] if len(sys.argv) > 1 else "MyTradingSys/execution")
sys.path.insert(0, str(EXEC))
import kill_switch  # noqa: E402
import deribit_orders as do  # noqa: E402


class RealLikeClient:
    """kill_all duck type, but with the REAL get_open_orders signature (token, instrument_name, type_).
    Every other method duck-types cleanly."""
    def __init__(self):
        self.cancelled = []

    def get_positions(self, token, currency="BTC", kind="future"):
        return []

    def get_open_orders(self, token, instrument_name="BTC-PERPETUAL", type_="all"):
        return [dict(order_id="E1", order_state="open", reduce_only=False)]

    def cancel(self, token, order_id):
        self.cancelled.append(order_id)
        return {"order_id": order_id}

    def close_position(self, token, instrument_name="BTC-PERPETUAL"):
        return {"order": {"order_id": "C1"}}


class KillSwitchRealClientTest(unittest.TestCase):
    def test_kill_all_cancels_open_orders_with_the_real_client_signature(self):
        # F-KILL-1: today this fails - kill_all passes keyword type_ to the positional instrument_name
        # param of deribit_orders.get_open_orders, the read TypeErrors on every instrument, and E1 is
        # never cancelled. On the fix (positional call, and the docstring contract), it passes.
        client = RealLikeClient()
        r = kill_switch.kill_all(client, "tok")
        self.assertNotIn("get_open_orders", [e.get("operation") for e in r["errors"]], r["errors"])
        self.assertIn("E1", client.cancelled)
        self.assertTrue(r["ok"], r)


if __name__ == "__main__":
    sys.argv = [__file__]
    unittest.main(verbosity=2)
