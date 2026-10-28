import unittest

from MyTradingSys.backtest.layers.cryptocred.cc_bt_adapter import signals_to_trades, signals_to_events


def bar(t, o, h, l, c):
    return {"t": t, "o": o, "h": h, "l": l, "c": c}


class TestSignalsToTrades(unittest.TestCase):
    """Spec 075-cc-bt-adapter.md: signals_to_trades wires cc_setups signals into bt_engine.simulate_trade."""

    def test_empty_signals_returns_empty_list(self):
        self.assertEqual(signals_to_trades([], bars=[bar(0, 1, 1, 1, 1)]), [])

    def test_drops_meta_before_calling_simulate_trade_and_preserves_order(self):
        bars = [
            bar(0, 100, 100, 100, 100),
            bar(1, 100, 105, 95, 96),   # hits the long's stop first (stop_first=True)
            bar(2, 100, 106, 99, 105),  # hits the short's target
        ]
        long_signal = {
            "side": "long", "entry_price": 100, "entry_t": 0, "stop": 97,
            "targets": [(110, 1.0)], "meta": {"setup": "sr_flip", "rule_id": "C10-E01"},
        }
        short_signal = {
            "side": "short", "entry_price": 100, "entry_t": 0, "stop": 103,
            "targets": [(95, 1.0)], "meta": {"setup": "fib_pullback", "rule_id": "C10-E02"},
        }
        got = signals_to_trades([long_signal, short_signal], bars=bars)
        self.assertEqual(len(got), 2)
        # Same order as input.
        self.assertEqual(got[0]["signal_meta"], {"setup": "sr_flip", "rule_id": "C10-E01"})
        self.assertEqual(got[1]["signal_meta"], {"setup": "fib_pullback", "rule_id": "C10-E02"})
        # trade_result came back from bt_engine.simulate_trade (a dict), not the raw signal.
        self.assertIsInstance(got[0]["trade_result"], dict)
        self.assertIsInstance(got[1]["trade_result"], dict)

    def test_propagates_simulate_trade_errors(self):
        bars = [bar(0, 100, 100, 100, 100)]
        bad_signal = {
            "side": "long", "entry_price": 100, "entry_t": 0, "stop": 100,  # stop == entry: invalid
            "targets": [(110, 1.0)], "meta": {},
        }
        with self.assertRaises(ValueError):
            signals_to_trades([bad_signal], bars=bars)


class TestSignalsToEvents(unittest.TestCase):
    """signals_to_events resolves entry_t -> bar index for layers/runner.py's event shape."""

    def test_empty_signals_returns_empty_list(self):
        self.assertEqual(signals_to_events([], bars=[bar(0, 1, 1, 1, 1)]), [])

    def test_resolves_index_by_matching_t_and_skips_unmatched(self):
        bars = [bar(0, 1, 1, 1, 1), bar(5, 1, 1, 1, 1), bar(10, 1, 1, 1, 1)]
        signals = [
            {"side": "long", "entry_price": 1, "entry_t": 5, "stop": 0.9, "targets": [], "meta": {}},
            {"side": "short", "entry_price": 1, "entry_t": 999, "stop": 1.1, "targets": [], "meta": {}},
            {"side": "long", "entry_price": 1, "entry_t": 0, "stop": 0.9, "targets": [], "meta": {}},
        ]
        got = signals_to_events(signals, bars=bars)
        self.assertEqual(got, [{"i": 1, "side": "long"}, {"i": 0, "side": "long"}])


if __name__ == "__main__":
    unittest.main()
