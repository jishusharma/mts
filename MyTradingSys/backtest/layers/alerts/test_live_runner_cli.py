import json
import shutil
import tempfile
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.alerts import live_runner_cli as cli
from MyTradingSys.backtest.layers.alerts.live_runner_core import empty_state, build_registry


def _row(t, o, h, l, c, v, tbv):
    # Binance kline row shape: [openTime, o, h, l, c, v, closeTime, qav, n, tbv, tqv, ignore]
    return [t, str(o), str(h), str(l), str(c), str(v), t + 59999, "0", 1, str(tbv), "0", "0"]


class TestKlinesToBars(unittest.TestCase):
    def test_maps_fields_and_casts_types(self):
        raw = [_row(0, 100, 101, 99, 100.5, 10, 6)]
        bars = cli.klines_to_bars(raw)
        self.assertEqual(bars, [{"t": 0, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.5, "v": 10.0, "tbv": 6.0}])

    def test_empty_raw_returns_empty(self):
        self.assertEqual(cli.klines_to_bars([]), [])

    def test_short_row_raises(self):
        with self.assertRaises(ValueError):
            cli.klines_to_bars([[0, "1", "1", "1", "1"]])

    def test_preserves_order(self):
        raw = [_row(0, 1, 1, 1, 1, 1, 1), _row(60000, 2, 2, 2, 2, 2, 2)]
        bars = cli.klines_to_bars(raw)
        self.assertEqual([b["t"] for b in bars], [0, 60000])


class TestFetchClosedBars(unittest.TestCase):
    def test_drops_last_possibly_open_row(self):
        raw = [_row(0, 1, 1, 1, 1, 1, 1), _row(60000, 2, 2, 2, 2, 2, 2), _row(120000, 3, 3, 3, 3, 3, 3)]
        fetch = lambda symbol, interval, limit: raw
        closed = cli.fetch_closed_bars(fetch, "BTCUSDT", "1h", 100)
        self.assertEqual([b["t"] for b in closed], [0, 60000])

    def test_fewer_than_two_rows_raises(self):
        fetch = lambda symbol, interval, limit: [_row(0, 1, 1, 1, 1, 1, 1)]
        with self.assertRaises(ValueError):
            cli.fetch_closed_bars(fetch, "BTCUSDT", "1h", 100)

    def test_no_rows_raises(self):
        fetch = lambda symbol, interval, limit: []
        with self.assertRaises(ValueError):
            cli.fetch_closed_bars(fetch, "BTCUSDT", "1h", 100)

    def test_non_ascending_raises(self):
        raw = [_row(60000, 1, 1, 1, 1, 1, 1), _row(0, 2, 2, 2, 2, 2, 2), _row(120000, 3, 3, 3, 3, 3, 3)]
        fetch = lambda symbol, interval, limit: raw
        with self.assertRaises(ValueError):
            cli.fetch_closed_bars(fetch, "BTCUSDT", "1h", 100)

    def test_passes_through_args_to_fetch_fn(self):
        seen = {}

        def fetch(symbol, interval, limit):
            seen["args"] = (symbol, interval, limit)
            return [_row(0, 1, 1, 1, 1, 1, 1), _row(60000, 2, 2, 2, 2, 2, 2)]

        cli.fetch_closed_bars(fetch, "ETHUSDT", "15m", 50)
        self.assertEqual(seen["args"], ("ETHUSDT", "15m", 50))


class TestBuildDefaultRegistry(unittest.TestCase):
    def test_three_entries_expected_keys(self):
        registry = cli.build_default_registry()
        self.assertTrue(
            {"rsi|rsi_events|1h", "rsi|rsi_events|15m", "fabio|cvd_absorption|1h"} <= set(registry.keys()))
        for entry in registry.values():
            self.assertTrue(callable(entry["fn"]))
            self.assertIsInstance(entry["params_id"], str)
            self.assertTrue(entry["params_id"])

    def test_is_a_build_registry_result(self):
        # build_default_registry must delegate to live_runner_core.build_registry (same shape/behavior)
        registry = cli.build_default_registry()
        reconstructed = build_registry([
            {"layer": e["layer"], "sub": e["sub"], "tf": e["tf"], "fn": e["fn"], "params_id": e["params_id"]}
            for e in registry.values()
        ])
        self.assertEqual(set(registry.keys()), set(reconstructed.keys()))

    def test_fabio_layer_fn_returns_empty_list_on_too_short_history(self):
        # find_swings' default left=2/right=2 window yields zero swings (and so zero events)
        # on a single bar -- an empty list, not an error (cc_structure.find_swings: range(2, 1-2) is empty).
        entry = cli.build_default_registry()["fabio|cvd_absorption|1h"]
        events = entry["fn"]([{"t": 0, "o": 1, "h": 1, "l": 1, "c": 1, "v": 1, "tbv": 0}])
        self.assertEqual(events, [])


class TestPollOnce(unittest.TestCase):
    def _stub_registry(self):
        return build_registry([
            {"layer": "L", "sub": "S", "tf": "1h",
             "fn": lambda bars: [{"t": b["t"], "event": "e"} for b in bars], "params_id": "P"}
        ])

    def test_happy_path_returns_alerts_and_state(self):
        raw = [_row(0, 1, 1, 1, 1, 1, 1), _row(60000, 2, 2, 2, 2, 2, 2), _row(120000, 3, 3, 3, 3, 3, 3)]
        fetch = lambda symbol, interval, limit: raw
        result = cli.poll_once(self._stub_registry(), "BTCUSDT", ["1h"], fetch, empty_state())
        # bars 0 and 60000 survive fetch_closed_bars' drop; only the last (60000) is fresh
        self.assertEqual(len(result["alerts"]), 2)
        self.assertEqual(result["errors"], [])
        self.assertIn("1h", result["state"]["last_t"])

    def test_fetch_failure_for_one_tf_isolated_as_error(self):
        def flaky(symbol, interval, limit):
            if interval == "bad":
                raise RuntimeError("network down")
            return [_row(0, 1, 1, 1, 1, 1, 1), _row(60000, 2, 2, 2, 2, 2, 2)]

        result = cli.poll_once(self._stub_registry(), "BTCUSDT", ["1h", "bad"], flaky, empty_state())
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["key"], "fetch:bad")
        self.assertGreater(len(result["alerts"]), 0)

    def test_dedupes_tfs(self):
        calls = []

        def fetch(symbol, interval, limit):
            calls.append(interval)
            return [_row(0, 1, 1, 1, 1, 1, 1), _row(60000, 2, 2, 2, 2, 2, 2)]

        cli.poll_once(self._stub_registry(), "BTCUSDT", ["1h", "1h"], fetch, empty_state())
        self.assertEqual(calls, ["1h"])


class TestMainOnce(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)

    def test_once_writes_alerts_and_state_with_injected_fetch(self):
        raw = [_row(0, 1, 1, 1, 1, 1, 1), _row(60000, 2, 2, 2, 2, 2, 2), _row(120000, 3, 3, 3, 3, 3, 3)]
        original_fetch = cli.default_fetch_klines
        cli.default_fetch_klines = lambda symbol, interval, limit: raw
        try:
            state_path = Path(self.tmpdir) / "state.json"
            alerts_dir = Path(self.tmpdir) / "alerts"
            rc = cli.main([
                "--symbol", "BTCUSDT",
                "--tfs", "1h",
                "--state-path", str(state_path),
                "--alerts-dir", str(alerts_dir),
                "--once",
            ])
            self.assertEqual(rc, 0)
            self.assertTrue(state_path.exists())
            saved = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertIn("last_t", saved)
            self.assertIn("1h", saved["last_t"])
        finally:
            cli.default_fetch_klines = original_fetch


class TestLoadSaveState(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir, ignore_errors=True)

    def test_load_missing_file_returns_empty_state(self):
        path = Path(self.tmpdir) / "nope.json"
        self.assertEqual(cli.load_state(path), empty_state())

    def test_save_then_load_roundtrip(self):
        path = Path(self.tmpdir) / "nested" / "state.json"
        state = {"last_t": {"1h": 5}, "prev_events": {"L|S|1h": [{"t": 5, "event": "e"}]}}
        cli.save_state(state, path)
        self.assertEqual(cli.load_state(path), state)


if __name__ == "__main__":
    unittest.main()
