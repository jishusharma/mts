"""Per-layer confirmation lag in the live alert filter (signal-flow fix, tag sigflow)."""
import unittest

from MyTradingSys.backtest.layers.alerts.live_runner_core import run_registry, empty_state, build_registry

M15 = 900000
T0 = 1790000000000
N = 60
LAST = T0 + (N - 1) * M15


def _bars(n=N):
    return [{"t": T0 + i * M15, "o": 1, "h": 2, "l": 0.5, "c": 1 + (i % 7) * 0.1 + i * 0.01, "v": 1, "tbv": 0.5}
            for i in range(n)]


def _reg(lag_bars_behind, lag_declared=None, name="ev"):
    """A layer whose only event sits `lag_bars_behind` bars before the latest closed bar."""
    def fn(bars):
        return [{"t": bars[-1 - lag_bars_behind]["t"], "event": name, "side": "long"}]
    entry = {"layer": "x", "sub": "s", "tf": "15m", "fn": fn, "params_id": "p"}
    if lag_declared is not None:
        entry["confirm_lag_bars"] = lag_declared
    return build_registry([entry])


class TestLag(unittest.TestCase):
    def test_lag2_layer_emits_when_confirmed_on_latest_bar_fresh_state(self):
        res = run_registry(_reg(2, lag_declared=2), {"15m": _bars()}, empty_state())
        self.assertEqual([a["t_close"] for a in res["alerts"]], [LAST - 2 * M15])
        self.assertEqual(res["alerts"][0]["t_confirm"], LAST)

    def test_undeclared_layer_keeps_one_bar_rule(self):
        self.assertEqual(run_registry(_reg(2), {"15m": _bars()}, empty_state())["alerts"], [])

    def test_fresh_state_backlog_beyond_lag_suppressed(self):
        # declared lag 2: an event 3 bars behind is history on a fresh state
        self.assertEqual(run_registry(_reg(3, lag_declared=2), {"15m": _bars()}, empty_state())["alerts"], [])

    def test_steady_state_allows_one_bar_slack(self):
        reg = _reg(3, lag_declared=2)
        st = empty_state()
        st["prev_events"] = {"x|s|15m": []}          # layer already seen once: slack of 1 bar applies
        res = run_registry(reg, {"15m": _bars()}, st)
        self.assertEqual(len(res["alerts"]), 1)

    def test_steady_state_backlog_beyond_slack_suppressed(self):
        reg = _reg(4, lag_declared=2)
        st = empty_state()
        st["prev_events"] = {"x|s|15m": []}
        self.assertEqual(run_registry(reg, {"15m": _bars()}, st)["alerts"], [])

    def test_emitted_key_dedupe_after_state_reset(self):
        reg = _reg(2, lag_declared=2)
        r1 = run_registry(reg, {"15m": _bars()}, empty_state())
        st = r1["state"]
        st["last_t"], st["prev_events"] = {}, {}
        self.assertEqual(run_registry(reg, {"15m": _bars()}, st)["alerts"], [])


if __name__ == "__main__":
    unittest.main()
