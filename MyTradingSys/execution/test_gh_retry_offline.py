"""
Offline unit test for the G-h fix in deribit_orders.py: order-creating calls
must NOT auto-retry on an ambiguous error code (10050); non-order (read)
calls must keep the existing retry-then-succeed behaviour.

No network. Monkeypatches deribit_orders._post (the transport boundary used
by _call) to return canned JSON-RPC bodies.

Run with: python3 -m unittest test_gh_retry_offline -v
"""
import unittest
from unittest import mock

import deribit_orders as do


def _error_body(code, message="ambiguous"):
    return {"jsonrpc": "2.0", "id": 1, "error": {"code": code, "message": message}}


def _result_body(result):
    return {"jsonrpc": "2.0", "id": 1, "result": result}


class OrderCreatingCallsDoNotRetryOnAmbiguousCode(unittest.TestCase):
    def test_buy_raises_order_state_unknown_and_calls_transport_once(self):
        calls = []

        def fake_post(method, params, token=None):
            calls.append(method)
            return _error_body(10050, "queue timeout")

        with mock.patch.object(do, "_post", side_effect=fake_post):
            with self.assertRaises(do.OrderStateUnknown) as ctx:
                do.buy("tok", "BTC-PERPETUAL", 10, "limit", price=50000, label="entry_1")

        self.assertEqual(calls, ["private/buy"])  # exactly one transport call - no retry
        self.assertEqual(ctx.exception.code, 10050)
        self.assertEqual(ctx.exception.method, "private/buy")
        self.assertIn("BTC-PERPETUAL", ctx.exception.params_label)

    def test_sell_raises_order_state_unknown_and_calls_transport_once(self):
        calls = []

        def fake_post(method, params, token=None):
            calls.append(method)
            return _error_body(10050)

        with mock.patch.object(do, "_post", side_effect=fake_post):
            with self.assertRaises(do.OrderStateUnknown):
                do.sell("tok", "BTC-PERPETUAL", 10, "limit", price=50000, label="entry_1")

        self.assertEqual(calls, ["private/sell"])

    def test_close_position_raises_order_state_unknown_and_calls_transport_once(self):
        calls = []

        def fake_post(method, params, token=None):
            calls.append(method)
            return _error_body(10050)

        with mock.patch.object(do, "_post", side_effect=fake_post):
            with self.assertRaises(do.OrderStateUnknown):
                do.close_position("tok", "BTC-PERPETUAL")

        self.assertEqual(calls, ["private/close_position"])

    def test_buy_still_retries_on_confirmed_pre_processing_reject_code(self):
        # 10028 (rate limited) is CONFIRMED pre-processing-reject - order
        # creating calls must still retry it, unlike 10050.
        calls = []

        def fake_post(method, params, token=None):
            calls.append(method)
            if len(calls) == 1:
                return _error_body(10028, "rate limited")
            return _result_body({"order": {"order_id": "ORD1"}})

        with mock.patch.object(do, "_post", side_effect=fake_post), \
             mock.patch.object(do.time, "sleep", return_value=None):
            result = do.buy("tok", "BTC-PERPETUAL", 10, "limit", price=50000, label="entry_1")

        self.assertEqual(len(calls), 2)
        self.assertEqual(result, {"order": {"order_id": "ORD1"}})


class NonOrderCallsKeepCurrentRetryBehaviour(unittest.TestCase):
    def test_read_method_retries_on_10050_then_succeeds(self):
        calls = []

        def fake_post(method, params, token=None):
            calls.append(method)
            if len(calls) == 1:
                return _error_body(10050, "queue timeout")
            return _result_body({"size": 10})

        with mock.patch.object(do, "_post", side_effect=fake_post), \
             mock.patch.object(do.time, "sleep", return_value=None):
            result = do.get_position("tok", "BTC-PERPETUAL")

        self.assertEqual(len(calls), 2)  # first call hit 10050, retried, second succeeded
        self.assertEqual(result, {"size": 10})

    def test_cancel_retries_on_10050_then_succeeds(self):
        calls = []

        def fake_post(method, params, token=None):
            calls.append(method)
            if len(calls) == 1:
                return _error_body(10050)
            return _result_body({"order": {"order_id": "ORD1", "order_state": "cancelled"}})

        with mock.patch.object(do, "_post", side_effect=fake_post), \
             mock.patch.object(do.time, "sleep", return_value=None):
            result = do.cancel("tok", "ORD1")

        self.assertEqual(len(calls), 2)
        self.assertEqual(result["order"]["order_id"], "ORD1")

    def test_edit_retries_on_10050_then_succeeds(self):
        calls = []

        def fake_post(method, params, token=None):
            calls.append(method)
            if len(calls) == 1:
                return _error_body(10050)
            return _result_body({"order": {"order_id": "ORD1", "amount": 20}})

        with mock.patch.object(do, "_post", side_effect=fake_post), \
             mock.patch.object(do.time, "sleep", return_value=None):
            result = do.edit("tok", "ORD1", amount=20)

        self.assertEqual(len(calls), 2)
        self.assertEqual(result["order"]["amount"], 20)


if __name__ == "__main__":
    unittest.main()
