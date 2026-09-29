import unittest

from MyTradingSys.backtest.layers.alerts.live_runner_core import (
    latest_closed_t, build_registry, empty_state, run_registry,
)


class TestLatestClosedT(unittest.TestCase):
    def test_returns_last_bar_t(self):
        self.assertEqual(latest_closed_t([{"t": 1}, {"t": 2}, {"t": 5}]), 5)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            latest_closed_t([])

    def test_non_ascending_raises(self):
        with self.assertRaises(ValueError):
            latest_closed_t([{"t": 2}, {"t": 1}])

    def test_duplicate_t_raises(self):
        with self.assertRaises(ValueError):
            latest_closed_t([{"t": 1}, {"t": 1}])


class TestBuildRegistry(unittest.TestCase):
    def _entry(self, layer="rsi", sub="rsi_events", tf="1h", params_id="p1"):
        return {"layer": layer, "sub": sub, "tf": tf, "fn": lambda bars: [], "params_id": params_id}

    def test_single_entry_keyed_correctly(self):
        entry = self._entry()
        reg = build_registry([entry])
        self.assertEqual(list(reg.keys()), ["rsi|rsi_events|1h"])
        self.assertIs(reg["rsi|rsi_events|1h"], entry)

    def test_missing_key_raises(self):
        bad = {"layer": "rsi", "sub": "rsi_events", "tf": "1h", "fn": lambda b: []}  # no params_id
        with self.assertRaises(ValueError):
            build_registry([bad])

    def test_duplicate_key_raises(self):
        e1 = self._entry()
        e2 = self._entry()
        with self.assertRaises(ValueError):
            build_registry([e1, e2])

    def test_preserves_insertion_order(self):
        e1 = self._entry(sub="a")
        e2 = self._entry(sub="b")
        reg = build_registry([e1, e2])
        self.assertEqual(list(reg.keys()), ["rsi|a|1h", "rsi|b|1h"])

    def test_does_not_mutate_entries_list(self):
        entries = [self._entry()]
        entries_copy = list(entries)
        build_registry(entries)
        self.assertEqual(entries, entries_copy)


class TestEmptyState(unittest.TestCase):
    def test_shape(self):
        self.assertEqual(empty_state(), {"last_t": {}, "prev_events": {}})

    def test_returns_fresh_dicts_each_call(self):
        s1 = empty_state()
        s2 = empty_state()
        s1["last_t"]["1h"] = 5
        self.assertEqual(s2["last_t"], {})


class TestRunRegistry(unittest.TestCase):
    """Spec 085-live-alert-runner.md hand-computed check."""

    def _fn(self, bars):
        return [{"t": b["t"], "event": "e"} for b in bars]

    def _registry(self):
        return build_registry([
            {"layer": "L", "sub": "S", "tf": "1h", "fn": self._fn, "params_id": "P"}
        ])

    def test_call1_first_run_all_new(self):
        registry = self._registry()
        bars_by_tf = {"1h": [{"t": 1}, {"t": 2}, {"t": 3}]}
        result = run_registry(registry, bars_by_tf, empty_state())
        # only events <=1 bar old are emitted; history (t=1) is never emitted on a first run
        self.assertEqual({a["t_close"] for a in result["alerts"]}, {2, 3})
        self.assertEqual(result["state"]["last_t"], {"1h": 3})
        self.assertEqual(
            result["state"]["prev_events"]["L|S|1h"],
            [{"t": 1, "event": "e"}, {"t": 2, "event": "e"}, {"t": 3, "event": "e"}],
        )
        self.assertEqual(result["errors"], [])

    def test_call2_same_bars_is_noop(self):
        registry = self._registry()
        bars_by_tf = {"1h": [{"t": 1}, {"t": 2}]}
        state1 = run_registry(registry, bars_by_tf, empty_state())["state"]
        result2 = run_registry(registry, bars_by_tf, state1)
        self.assertEqual(result2["alerts"], [])
        self.assertEqual(result2["errors"], [])
        self.assertEqual(result2["state"]["last_t"], state1["last_t"])
        self.assertEqual(result2["state"]["prev_events"], state1["prev_events"])

    def test_call3_new_bar_only_new_event_alerted(self):
        registry = self._registry()
        state1 = run_registry(registry, {"1h": [{"t": 1}, {"t": 2}]}, empty_state())["state"]
        result3 = run_registry(registry, {"1h": [{"t": 1}, {"t": 2}, {"t": 3}]}, state1)
        self.assertEqual(len(result3["alerts"]), 1)
        self.assertEqual(result3["alerts"][0]["t_close"], 3)
        self.assertEqual(result3["state"]["last_t"], {"1h": 3})
        self.assertEqual(
            result3["state"]["prev_events"]["L|S|1h"],
            [{"t": 1, "event": "e"}, {"t": 2, "event": "e"}, {"t": 3, "event": "e"}],
        )

    def test_missing_tf_in_bars_by_tf_is_skipped_silently(self):
        registry = self._registry()
        result = run_registry(registry, {}, empty_state())
        self.assertEqual(result["alerts"], [])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["state"]["last_t"], {})
        self.assertEqual(result["state"]["prev_events"], {})

    def test_empty_bars_list_for_tf_is_skipped(self):
        registry = self._registry()
        result = run_registry(registry, {"1h": []}, empty_state())
        self.assertEqual(result["alerts"], [])
        self.assertEqual(result["errors"], [])

    def test_broken_layer_fn_is_isolated_as_an_error(self):
        def boom(bars):
            raise RuntimeError("layer exploded")

        registry = build_registry([
            {"layer": "L", "sub": "S", "tf": "1h", "fn": boom, "params_id": "P"}
        ])
        result = run_registry(registry, {"1h": [{"t": 1}]}, empty_state())
        self.assertEqual(result["alerts"], [])
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(result["errors"][0]["key"], "L|S|1h")
        self.assertIn("layer exploded", result["errors"][0]["error"])
        # last_t/prev_events for the broken key must NOT be advanced (retry next call)
        self.assertEqual(result["state"]["last_t"], {})
        self.assertEqual(result["state"]["prev_events"], {})

    def test_one_broken_entry_does_not_block_others(self):
        def boom(bars):
            raise RuntimeError("nope")

        registry = build_registry([
            {"layer": "A", "sub": "S", "tf": "1h", "fn": boom, "params_id": "P"},
            {"layer": "B", "sub": "S", "tf": "1h", "fn": self._fn, "params_id": "P"},
        ])
        result = run_registry(registry, {"1h": [{"t": 1}]}, empty_state())
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(len(result["alerts"]), 1)
        self.assertEqual(result["alerts"][0]["layer"], "B")

    def test_non_list_event_return_is_reported_as_error(self):
        registry = build_registry([
            {"layer": "L", "sub": "S", "tf": "1h", "fn": lambda bars: "not-a-list", "params_id": "P"}
        ])
        result = run_registry(registry, {"1h": [{"t": 1}]}, empty_state())
        self.assertEqual(result["alerts"], [])
        self.assertEqual(len(result["errors"]), 1)

    def test_does_not_mutate_inputs(self):
        registry = self._registry()
        bars_by_tf = {"1h": [{"t": 1}, {"t": 2}]}
        state = empty_state()
        registry_copy_keys = list(registry.keys())
        bars_copy = {"1h": [dict(b) for b in bars_by_tf["1h"]]}
        run_registry(registry, bars_by_tf, state)
        self.assertEqual(list(registry.keys()), registry_copy_keys)
        self.assertEqual(bars_by_tf, bars_copy)
        self.assertEqual(state, {"last_t": {}, "prev_events": {}})


if __name__ == "__main__":
    unittest.main()
