"""Spec-derived tests: turn_of_candle wiring (FORMULAS.md sec 16), RSI failure side (rsi/TEST_PLAN.md: a failure
resolves on the side opposite to the run's entry side), per-poll observability line, default tfs."""
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

from MyTradingSys.backtest.layers.alerts import live_layers as ll
from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
from MyTradingSys.backtest.layers.alerts.live_runner_core import run_registry, empty_state

MIN = 60000


def bars_1m(n, t0=0):
    return [{"t": t0 + k * MIN, "o": 100.0, "h": 100.0, "l": 100.0, "c": 100.0, "v": 1.0, "tbv": 0.5}
            for k in range(n)]


class TestTurnOfCandle(unittest.TestCase):
    def test_layer_events_at_minute_14_no_side(self):
        # spec hand check: 30 bars t=k*60000 -> lead_minutes=1 events at i=14 and i=29
        ev = ll.turn_of_candle_layer(bars_1m(30))
        self.assertEqual([e["t"] for e in ev], [14 * MIN, 29 * MIN])
        for e in ev:
            self.assertNotIn("side", e)
            self.assertIn("event", e)

    def test_registered_on_1m_and_alerts_without_side(self):
        reg = cli.build_default_registry()
        self.assertIn("turn_of_candle|turn_of_candle|1m", reg)
        bars = bars_1m(30)  # last bar (k=29) is minute 14 of the quarter -> fresh
        res = run_registry({k: v for k, v in reg.items() if v["layer"] == "turn_of_candle"},
                           {"1m": bars}, empty_state())
        self.assertEqual(res["errors"], [])
        self.assertEqual(len(res["alerts"]), 1)
        self.assertEqual(res["alerts"][0]["tf"], "1m")
        self.assertNotIn("side", res["alerts"][0])


class TestRsiFailureSide(unittest.TestCase):
    def _run(self, rsi_series):
        bars = [{"t": i * 1000, "c": 1.0} for i in range(len(rsi_series))]
        with mock.patch.object(ll, "rsi_core", return_value=rsi_series):
            return ll.rsi_level_layer(bars)

    def test_support_from_above_fails_below_is_alert_only(self):
        # T09-F3: failure no longer carries a side (untested as a live trade)
        ev = self._run([45, 45, 40.2, 38, 38])
        self.assertEqual([(e["event"], e.get("side")) for e in ev], [("failure", None)])

    def test_resistance_from_below_fails_above_is_alert_only(self):
        ev = self._run([35, 35, 40.2, 42, 42])
        self.assertEqual([(e["event"], e.get("side")) for e in ev], [("failure", None)])

    def test_support_rejection_cross_have_no_side(self):
        for series in ([45, 40.2, 45], [35, 40.2, 35], [45, 45, 35]):
            for e in self._run(series):
                self.assertNotIn("side", e)

    def test_registry_uses_it_for_both_tfs(self):
        reg = cli.build_default_registry()
        for k in ("rsi|rsi_events|1h", "rsi|rsi_events|15m"):
            self.assertIs(reg[k]["fn"], ll.rsi_level_layer)


class TestObservability(unittest.TestCase):
    def test_poll_line_lists_every_layer_with_counts(self):
        reg = cli.build_default_registry()
        res = {"alerts": [{"layer": "rsi", "sub": "rsi_events", "tf": "1h"}] * 2, "errors": [{"key": "x"}]}
        line = cli.format_poll_line(reg, res, now_ms=0)
        self.assertTrue(line.startswith("poll 1970-01-01T00:00:00Z alerts=2 errors=1"))
        self.assertIn("rsi|rsi_events|1h=2", line)
        for k in reg:
            self.assertIn(k + "=", line)
        self.assertIn("turn_of_candle|turn_of_candle|1m=0", line)

    def test_once_prints_flushed_poll_line_and_polls_1m(self):
        seen = {}

        def fake_poll(registry, symbol, tfs, fetch, state, limit=100):
            seen["tfs"] = tfs
            return {"alerts": [], "state": state, "errors": []}

        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as d, mock.patch.object(cli, "poll_once", fake_poll), \
                redirect_stdout(buf):
            self.assertEqual(cli.main(["--once", "--state-path", d + "/s.json", "--alerts-dir", d]), 0)
        self.assertIn("1m", seen["tfs"])
        self.assertTrue(buf.getvalue().startswith("poll "))


class TestConsensusWiring(unittest.TestCase):
    """LY5 / B125: the runner calls the consensus hook after each poll; the hook can never stop the runner."""

    FABIO = {"layer": "fabio", "sub": "v3_grid", "tf": "1m", "event": "v3_x_A_long", "model": "A", "side": "long",
             "entry_ref": 100.5, "stop": 99.5, "target": 103.0, "t_close": 60000, "params_id": "p"}

    def _run(self, d, alerts):
        def fake_poll(registry, symbol, tfs, fetch, state, limit=100):
            return {"alerts": alerts, "state": state, "errors": []}

        with mock.patch.object(cli, "poll_once", fake_poll), redirect_stdout(io.StringIO()):
            return cli.main(["--once", "--state-path", d + "/s.json", "--alerts-dir", d + "/alerts",
                             "--consensus-dir", d + "/consensus"])

    def test_fabio_alert_in_poll_writes_one_consensus_row(self):
        import json
        import pathlib
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self._run(d, [dict(self.FABIO)]), 0)
            files = list(pathlib.Path(d, "consensus").glob("consensus_*.jsonl"))
            self.assertEqual(len(files), 1)
            rows = [json.loads(x) for x in files[0].read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["fabio"]["model"], "A")
            self.assertEqual(rows[0]["fabio"]["entry"], 100.5)

    def test_no_alert_in_poll_writes_no_consensus_row(self):
        import pathlib
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(self._run(d, []), 0)
            self.assertFalse(pathlib.Path(d, "consensus").exists())

    def test_hook_failure_does_not_stop_the_runner(self):
        from MyTradingSys.backtest.layers.consensus import hook
        err = io.StringIO()
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(hook, "consensus_after_poll", side_effect=RuntimeError("boom")), \
                mock.patch("sys.stderr", err):
            self.assertEqual(self._run(d, [dict(self.FABIO)]), 0)
            self.assertTrue(__import__("os").path.exists(d + "/s.json"))     # state still saved after the hook error
        self.assertIn("consensus_hook", err.getvalue())


if __name__ == "__main__":
    unittest.main()
