"""
Offline test: a stopped-out trade must NOT false-halt when the triggered stop's
get_order_state answers order_not_found (Deribit archives/re-ids it). The flat
position is then explained via this plan's reduce-side fills
(private/get_user_trades_by_instrument_and_time, label "<plan_id>:..." + exit direction).
  (a) order_not_found + full reduce fills -> closed, stop_state triggered_by_fills
  (b) order_not_found + no fills          -> halt
  (c) order_not_found + partial fills     -> halt
No network.  python -m unittest test_triggered_stop_offline -v
"""
import shutil
import unittest

import deribit_orders as do
import journal
import position_manager as pm

NOT_FOUND = do.DeribitError("private/get_order_state", {"code": 10004, "message": "order_not_found"})


class FlatExchange:
    def __init__(self, trades):
        self.trades = trades

    def authenticate(self):
        return "tok"

    def get_position(self, token, instrument="BTC-PERPETUAL"):
        return {"size": 0}

    def get_order_state(self, token, oid):
        raise NOT_FOUND

    def cancel(self, token, oid):
        return {}

    def get_user_trades_by_instrument_and_time(self, token, instrument, start_ms, end_ms, count=100):
        return self.trades


NAMES = ("authenticate", "get_position", "get_order_state", "cancel",
         "get_user_trades_by_instrument_and_time")


def _trade(label, direction, amount):
    return {"label": label, "direction": direction, "amount": amount, "timestamp": 1}


class TriggeredStopTests(unittest.TestCase):
    def setUp(self):
        self._orig = {n: getattr(do, n, None) for n in NAMES}
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        pm.HALT_PATH.unlink(missing_ok=True)
        self.pid = "trig_stop"
        journal.append_event(self.pid, "order_placed", {"order_id": "E1", "label": "entry_1", "side": "BUY", "amount": 100})
        journal.append_event(self.pid, "order_filled", {"order_id": "E1", "filled_amount": 100, "order_state": "filled"})
        journal.append_event(self.pid, "order_placed", {"order_id": "S1", "label": "stop_order", "side": "SELL",
                                                        "amount": 100, "trigger_price": 79000.0})

    def tearDown(self):
        for n, f in self._orig.items():
            setattr(do, n, f)
        shutil.rmtree(journal.JOURNAL_DIR, ignore_errors=True)
        pm.HALT_PATH.unlink(missing_ok=True)

    def _run(self, trades):
        fake = FlatExchange(trades)
        for n in NAMES:
            setattr(do, n, getattr(fake, n))
        return pm.manage(self.pid, once=True, token="t")

    def test_a_fills_explain_flat(self):
        r = self._run([_trade("trig_stop:stop_order", "sell", 100),
                       _trade("trig_stop:entry_1", "buy", 100),       # entry side ignored
                       _trade("other_plan:stop_order", "sell", 500)])  # other plan ignored
        self.assertEqual(r["status"], "closed")
        self.assertEqual(r["stop_state"], "triggered_by_fills")
        ev = [e for e in journal.read_events(self.pid) if e["event_type"] == "reconciliation"]
        self.assertEqual(ev[-1]["data"]["stop_state"], "triggered_by_fills")

    def test_b_no_fills_halts(self):
        with self.assertRaises(pm.ManagerHalted):
            self._run([_trade("trig_stop:entry_1", "buy", 100)])

    def test_c_partial_fills_halt(self):
        with self.assertRaises(pm.ManagerHalted):
            self._run([_trade("trig_stop:stop_order", "sell", 60)])


if __name__ == "__main__":
    unittest.main()
