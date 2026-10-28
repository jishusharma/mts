"""B149 capture tool: keeps only the fields needed to decide the settlement double-count, never keys or ids; fake client, no network."""
import unittest

import capture_txlog_settlement as cap

RAW = [
    {"type": "trade", "timestamp": 1760000000000, "change": -1e-6, "cashflow": 0.0002, "profit_as_cashflow": True,
     "instrument_name": "BTC-PERPETUAL", "currency": "BTC", "id": 99, "trade_id": "T1", "user_seq": 7},
    {"type": "settlement", "timestamp": 1760025600000, "change": 0.0002, "cashflow": 0.0002, "session_profit_loss": 0.0002,
     "instrument_name": "BTC-PERPETUAL", "currency": "BTC", "id": 100},
    {"type": "deposit", "timestamp": 1760030000000, "change": 1.0, "cashflow": 1.0, "currency": "BTC"},
]


class FakeClient:
    def __init__(self):
        self.calls = []

    def get_transaction_log(self, token, currency, start_ms, end_ms):
        self.calls.append((token, currency, start_ms, end_ms))
        return RAW


class CaptureTests(unittest.TestCase):
    def test_slim_drops_ids_and_adds_utc_time(self):
        s = cap.slim(RAW[0])
        self.assertNotIn("id", s)
        self.assertNotIn("trade_id", s)
        self.assertNotIn("user_seq", s)
        self.assertEqual(s["ts_utc"], "2025-10-09T08:53:20Z")
        self.assertTrue(s["profit_as_cashflow"])

    def test_capture_window_and_summary(self):
        c = FakeClient()
        res = cap.capture(c, "tok", lambda: {"futures_session_upl": 0.0}, 36, now_ms=1760100000000)
        self.assertEqual(c.calls, [("tok", "BTC", 1760100000000 - 36 * 3600 * 1000, 1760100000000)])
        self.assertEqual(res["summary"]["by_type"], {"trade": 1, "settlement": 1, "deposit": 1})
        self.assertEqual(len(res["summary"]["settlements"]), 1)
        self.assertEqual(res["summary"]["settlements"][0]["session_profit_loss"], 0.0002)
        self.assertEqual(res["account_summary"], {"futures_session_upl": 0.0})


if __name__ == "__main__":
    unittest.main()
