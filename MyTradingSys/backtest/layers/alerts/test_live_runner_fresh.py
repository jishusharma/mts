"""Live runner must emit only latest-closed-bar events, with rsi values, never twice."""
import unittest

from MyTradingSys.backtest.layers.alerts.live_runner_core import run_registry, empty_state, build_registry

M15 = 900000
T0 = 1790000000000


def _bars(n):
    return [{"t": T0 + i * M15, "o": 1, "h": 2, "l": 0.5, "c": 1 + (i % 7) * 0.1 + i * 0.01, "v": 1, "tbv": 0.5}
            for i in range(n)]


def _fn(bars):  # emits an event on every 5th bar, i.e. a history backlog plus (sometimes) the last bar
    return [{"t": b["t"], "event": "cross"} for i, b in enumerate(bars) if i % 5 == 4]


REG = build_registry([{"layer": "x", "sub": "s", "tf": "15m", "fn": _fn, "params_id": "p"}])


class TestFresh(unittest.TestCase):
    def test_first_run_emits_no_backlog(self):
        res = run_registry(REG, {"15m": _bars(60)}, empty_state())  # bar 59 is the last -> fresh; 4,9,..54 stale
        self.assertEqual([a["t_close"] for a in res["alerts"]], [T0 + 59 * M15])

    def test_old_events_only_emits_nothing(self):
        res = run_registry(REG, {"15m": _bars(58)}, empty_state())  # events at idx 54 and earlier: >1 bar old
        self.assertEqual(res["alerts"], [])

    def test_rsi_not_null(self):
        a = run_registry(REG, {"15m": _bars(60)}, empty_state())["alerts"][0]
        self.assertIsNotNone(a["rsi"])
        self.assertIsNotNone(a["rsi_ma"])

    def test_never_reemits_same_key(self):
        r1 = run_registry(REG, {"15m": _bars(60)}, empty_state())
        st = r1["state"]
        st["last_t"] = {}  # simulate lost last_t / prev_events (restart)
        st["prev_events"] = {}
        r2 = run_registry(REG, {"15m": _bars(60)}, st)
        self.assertEqual(r2["alerts"], [])


if __name__ == "__main__":
    unittest.main()
