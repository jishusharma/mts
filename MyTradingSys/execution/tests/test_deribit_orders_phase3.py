"""T050 phase 3 offline tests: place / amend / cancel / reconcile on deribit_orders primitives.
Derived from the Deribit JSON-RPC contract (private/buy|sell, private/edit, private/cancel,
get_open_orders_by_instrument, get_order_history_by_instrument), not from the implementation.
DO_UNDER_TEST=<path> loads a staged .new copy instead of the committed module."""
import importlib.util
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
_path = os.environ.get("DO_UNDER_TEST") or str(HERE / "deribit_orders.py")
_spec = importlib.util.spec_from_file_location("do_under_test", _path,
                                               loader=importlib.machinery.SourceFileLoader("do_under_test", _path))
do = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(do)


class FakeExchange:
    def __init__(self):
        self.calls = []
        self.open = []
        self.history = []

    def post(self, method, params, token=None):
        self.calls.append((method, dict(params)))
        if method in ("private/buy", "private/sell"):
            o = {"order_id": "ETH-1", "order_state": "open", "instrument_name": params["instrument_name"],
                 "amount": params["amount"], "price": params.get("price"), "label": params.get("label", "")}
            self.open.append(o)
            return {"result": {"order": o, "trades": []}}
        if method == "private/edit":
            o = next(x for x in self.open if x["order_id"] == params["order_id"])
            o.update({k: v for k, v in params.items() if k in ("amount", "price")})
            return {"result": {"order": o, "trades": []}}
        if method == "private/cancel":
            o = next(x for x in self.open if x["order_id"] == params["order_id"])
            self.open.remove(o)
            return {"result": dict(o, order_state="cancelled")}
        if method == "private/get_open_orders_by_instrument":
            return {"result": list(self.open)}
        if method == "private/get_order_history_by_instrument":
            return {"result": list(self.history)}
        return {"error": {"code": 11050, "message": "bad_request"}}


class Phase3(unittest.TestCase):
    def setUp(self):
        self.ex = FakeExchange()
        self.orig_post, self.orig_env = do._post, do._ACTIVE_ENV
        do._post = self.ex.post
        do._ACTIVE_ENV = "test"
        self.addCleanup(self._restore)

    def _restore(self):
        do._post, do._ACTIVE_ENV = self.orig_post, self.orig_env

    def test_place_limit_sends_expected_params(self):
        o = do.place("t", "buy", "BTC-PERPETUAL", 10, "limit", price=1000.0, label="p3", post_only=True)
        self.assertEqual(o["order_id"], "ETH-1")
        m, p = self.ex.calls[0]
        self.assertEqual(m, "private/buy")
        self.assertEqual((p["amount"], p["price"], p["type"], p["label"], p["post_only"]), (10, 1000.0, "limit", "p3", True))

    def test_place_refuses_bad_input_before_http(self):
        for kw in ({"side": "hold"}, {"amount": 0}, {"amount": True}, {"price": None}, {"price": -1}):
            args = dict(side="buy", instrument_name="BTC-PERPETUAL", amount=10, order_type="limit", price=1000.0)
            args.update(kw)
            with self.assertRaises(ValueError):
                do.place("t", **args)
        self.assertEqual(self.ex.calls, [])

    def test_place_refuses_on_mainnet(self):
        do._ACTIVE_ENV = "mainnet"
        with self.assertRaises(RuntimeError):
            do.place("t", "buy", "BTC-PERPETUAL", 10, "limit", price=1000.0)
        self.assertEqual(self.ex.calls, [])

    def test_place_without_order_in_response_is_state_unknown(self):
        do._post = lambda m, p, t=None: {"result": {}}
        with self.assertRaises(do.OrderStateUnknown):
            do.place("t", "sell", "BTC-PERPETUAL", 10, "limit", price=1000.0)

    def test_amend_changes_price_and_requires_a_field(self):
        do.place("t", "buy", "BTC-PERPETUAL", 10, "limit", price=1000.0)
        o = do.amend("t", "ETH-1", price=1001.0)
        self.assertEqual(o["price"], 1001.0)
        n = len(self.ex.calls)
        with self.assertRaises(ValueError):
            do.amend("t", "ETH-1")
        with self.assertRaises(ValueError):
            do.amend("t", "ETH-1", price=0)
        self.assertEqual(len(self.ex.calls), n)

    def test_cancel_removes_from_open_orders(self):
        do.place("t", "buy", "BTC-PERPETUAL", 10, "limit", price=1000.0)
        self.assertTrue(do.reconcile_open("t", "ETH-1")["ok"])
        self.assertEqual(do.cancel("t", "ETH-1")["order_state"], "cancelled")
        self.assertFalse(do.reconcile_open("t", "ETH-1")["ok"])

    def test_reconcile_open_missing_order_is_not_ok(self):
        self.assertFalse(do.reconcile_open("t", "nope")["ok"])

    def test_reconcile_filled_needs_history_filled_and_not_open(self):
        self.ex.history = [{"order_id": "F-1", "order_state": "filled"}, {"order_id": "C-1", "order_state": "cancelled"}]
        self.assertTrue(do.reconcile_filled("t", "F-1")["ok"])
        self.assertFalse(do.reconcile_filled("t", "C-1")["ok"])
        self.assertFalse(do.reconcile_filled("t", "absent")["ok"])
        self.ex.open = [{"order_id": "F-1"}]  # filled yet still listed open -> mismatch
        self.assertFalse(do.reconcile_filled("t", "F-1")["ok"])
        m = [c for c in self.ex.calls if c[0] == "private/get_order_history_by_instrument"][0][1]
        self.assertEqual(m["instrument_name"], "BTC-PERPETUAL")


if __name__ == "__main__":
    unittest.main()
