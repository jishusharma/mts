import json
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence

PARAMS = Path(__file__).parent / "params" / "malkan_divergence_default.json"


def _ts(x):
    return list(range(len(x)))


class TestDivergence(unittest.TestCase):
    """Series are hand-built: swing closes and RSI at them are chosen first, expectations follow from the rule text."""

    def test_bullish_single(self):
        close = [12, 10, 11, 12, 9, 10, 11, 13]       # low pivots idx 1 (10) and idx 4 (9)
        rsi = [40, 30, 35, 38, 33, 36, 38, 45]        # RSI at pivots 30 -> 33 (higher)
        ev = rsi_divergence(close, rsi, _ts(close), 3, 10)
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["t"], e["a_i"], e["b_i"], e["bars"], e["chain"]), (5, 1, 4, 4, 1))
        self.assertEqual((e["close_a"], e["close_b"], e["rsi_a"], e["rsi_b"]), (10, 9, 30, 33))

    def test_rsi_not_higher_no_divergence(self):
        close = [12, 10, 11, 12, 9, 10, 11, 13]
        rsi = [40, 30, 35, 38, 28, 36, 38, 45]
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10), [])

    def test_decimal_difference_counts(self):
        close = [12, 10, 11, 12, 9, 10, 11, 13]
        rsi = [40, 37.2, 35, 38, 37.7, 36, 38, 45]
        self.assertEqual(len(rsi_divergence(close, rsi, _ts(close), 3, 10)), 1)
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10, min_rsi_diff=0.5), [])

    def test_bar_window(self):
        close = [12, 10, 11, 12, 9, 10, 11, 13]       # pair spans 4 bars inclusive
        rsi = [40, 30, 35, 38, 33, 36, 38, 45]
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 3), [])
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 5, 10), [])
        self.assertEqual(len(rsi_divergence(close, rsi, _ts(close), 4, 4)), 1)

    def test_too_far_apart(self):
        close = [12, 10] + [11, 12] * 6 + [9, 10, 13]
        # pivot lows idx 1 (10) and the 9 at idx 14; 14 - 1 + 1 = 14 bars > 10
        rsi = [None] * len(close)               # zigzag pivots in between have no RSI, so they are skipped
        rsi[1], rsi[14] = 30, 33
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10), [])
        self.assertEqual(len(rsi_divergence(close, rsi, _ts(close), 3, 14)), 1)

    def test_chain_counts_multiple_divergences(self):
        close = [12, 10, 11, 9, 10, 8, 9, 11]         # lows idx 1 (10), 3 (9), 5 (8)
        rsi = [50, 30, 35, 32, 40, 34, 45, 50]        # 30 < 32 < 34
        ev = rsi_divergence(close, rsi, _ts(close), 3, 10)
        self.assertEqual([(e["b_i"], e["chain"], e["t"]) for e in ev], [(3, 1, 4), (5, 2, 6)])

    def test_chain_resets_when_a_pair_fails(self):
        close = [12, 10, 11, 9, 10, 8, 9, 11]
        rsi = [50, 30, 35, 32, 40, 31, 45, 50]       # second pair: 31 < 32, no divergence
        ev = rsi_divergence(close, rsi, _ts(close), 3, 10)
        self.assertEqual([(e["b_i"], e["chain"]) for e in ev], [(3, 1)])

    def test_bearish(self):
        close = [8, 10, 9, 8, 11, 10, 9, 7]           # high pivots idx 1 (10) and idx 4 (11)
        rsi = [60, 70, 65, 60, 66, 64, 60, 50]        # RSI at highs 70 -> 66 (lower)
        ev = rsi_divergence(close, rsi, _ts(close), 3, 10, kind="bearish")
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["event"], e["t"], e["bars"], e["rsi_a"], e["rsi_b"]), ("bearish_divergence", 5, 4, 70, 66))
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10, kind="bullish"), [])

    def test_equal_closes_are_not_pivots(self):
        close = [12, 10, 10, 12, 9, 10, 11, 13]
        rsi = [40, 30, 30, 38, 33, 36, 38, 45]
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10), [])

    def test_none_rsi_at_pivot_is_skipped(self):
        close = [12, 10, 11, 12, 9, 10, 11, 13]
        rsi = [40, 30, 35, 38, None, 36, 38, 45]
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10), [])

    def test_causal_event_needs_only_bars_up_to_its_time(self):
        close = [12, 10, 11, 12, 9, 10, 11, 13]
        rsi = [40, 30, 35, 38, 33, 36, 38, 45]
        full = rsi_divergence(close, rsi, _ts(close), 3, 10)[0]
        cut = rsi_divergence(close[:6], rsi[:6], list(range(6)), 3, 10)
        self.assertEqual(cut, [full])                  # bar idx 5 is its stamp; later bars change nothing
        self.assertEqual(rsi_divergence(close[:5], rsi[:5], list(range(5)), 3, 10), [])

    def test_validation(self):
        with self.assertRaises(ValueError):
            rsi_divergence([1, 2], [1], [1, 2], 3, 10)
        with self.assertRaises(ValueError):
            rsi_divergence([1], [1], [1], 2, 10)
        with self.assertRaises(ValueError):
            rsi_divergence([1], [1], [1], 3, 10, kind="x")

    def test_params_file_matches_sourced_values(self):
        p = json.loads(PARAMS.read_text(encoding="utf-8"))
        self.assertEqual((p["min_bars"], p["max_bars"], p["min_rsi_diff"]), (3, 10, 0.0))
        self.assertIn("three", p["min_bars_quote"].lower())


if __name__ == "__main__":
    unittest.main()
