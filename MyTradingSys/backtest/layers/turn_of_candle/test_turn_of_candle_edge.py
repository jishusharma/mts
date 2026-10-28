import unittest
import math

from MyTradingSys.backtest.layers.turn_of_candle.turn_of_candle import (
    minute_of_quarter,
    toc_minute_stats,
    turn_of_candle_events,
)

# Expected numbers hand-computed from FORMULAS.md section 16 (T055 C3).
M = 60000


class TestMinuteOfQuarterEdges(unittest.TestCase):
    """Edge cases for minute_of_quarter."""

    def test_minute_of_quarter_zero(self):
        """Minute 0 at epoch."""
        self.assertEqual(minute_of_quarter(0), 0)

    def test_minute_of_quarter_boundaries(self):
        """Minute boundaries (0, 14, 15)."""
        self.assertEqual(minute_of_quarter(0 * M), 0)
        self.assertEqual(minute_of_quarter(14 * M), 14)
        self.assertEqual(minute_of_quarter(15 * M), 0)  # Wraps to 0
        self.assertEqual(minute_of_quarter(29 * M), 14)
        self.assertEqual(minute_of_quarter(30 * M), 0)  # Wraps to 0

    def test_minute_of_quarter_hour_boundaries(self):
        """Minute calculations across hour boundaries."""
        hour_ms = 3600 * 1000
        self.assertEqual(minute_of_quarter(hour_ms), 0)
        self.assertEqual(minute_of_quarter(hour_ms + 14 * M), 14)
        self.assertEqual(minute_of_quarter(hour_ms + 15 * M), 0)
        self.assertEqual(minute_of_quarter(hour_ms + 47 * M), (47 % 15))

    def test_minute_of_quarter_large_values(self):
        """Large timestamp values."""
        large_ts = 9999999999000
        self.assertEqual(minute_of_quarter(large_ts), (large_ts // 60000) % 15)


class TestTocMinuteStatsEdges(unittest.TestCase):
    """Edge cases for toc_minute_stats."""

    def test_single_bar_turn_minute(self):
        """Single bar at turn minute (0)."""
        bars = [{"t": 0 * M, "o": 100.0, "c": 102.0}]
        s = toc_minute_stats(bars)
        self.assertEqual(s["turn_n"], 1)
        self.assertEqual(s["other_n"], 0)
        self.assertAlmostEqual(s["turn_mean"], 0.02, places=12)
        self.assertIsNone(s["other_mean"])
        self.assertAlmostEqual(s["by_minute"][0], 0.02, places=12)
        self.assertEqual(len(s["by_minute"]), 1)

    def test_single_bar_non_turn_minute(self):
        """Single bar at non-turn minute."""
        bars = [{"t": 1 * M, "o": 100.0, "c": 101.0}]
        s = toc_minute_stats(bars)
        self.assertEqual(s["turn_n"], 0)
        self.assertEqual(s["other_n"], 1)
        self.assertIsNone(s["turn_mean"])
        self.assertAlmostEqual(s["other_mean"], 0.01, places=12)
        self.assertAlmostEqual(s["by_minute"][1], 0.01, places=12)

    def test_zero_return_bars(self):
        """Bars with zero return (open == close)."""
        bars = [
            {"t": 0 * M, "o": 100.0, "c": 100.0},
            {"t": 1 * M, "o": 100.0, "c": 100.0},
        ]
        s = toc_minute_stats(bars)
        self.assertAlmostEqual(s["turn_mean"], 0.0, places=12)
        self.assertAlmostEqual(s["other_mean"], 0.0, places=12)

    def test_negative_returns(self):
        """Bars with negative returns (close < open)."""
        bars = [
            {"t": 0 * M, "o": 100.0, "c": 95.0},
            {"t": 15 * M, "o": 100.0, "c": 90.0},
        ]
        s = toc_minute_stats(bars)
        self.assertAlmostEqual(s["turn_mean"], -0.075, places=12)

    def test_extreme_values(self):
        """Extreme but valid values."""
        bars = [
            {"t": 0 * M, "o": 0.0001, "c": 0.0002},
            {"t": 1 * M, "o": 1000000.0, "c": 1000001.0},
        ]
        s = toc_minute_stats(bars)
        # First bar: (0.0002 - 0.0001) / 0.0001 = 1.0
        # Second bar: (1000001 - 1000000) / 1000000 = 0.000001
        self.assertAlmostEqual(s["turn_mean"], 1.0, places=12)
        self.assertAlmostEqual(s["other_mean"], 0.000001, places=6)

    def test_all_minutes_represented(self):
        """Full 15-minute cycle with one bar per minute."""
        bars = []
        for k in range(15):
            bars.append({"t": k * M, "o": 100.0, "c": 100.0 + k * 0.01})
        s = toc_minute_stats(bars)
        self.assertEqual(len(s["by_minute"]), 15)
        self.assertEqual(set(s["by_minute"].keys()), set(range(15)))

    def test_only_turn_bars(self):
        """Only bars at turn minutes (0)."""
        bars = [
            {"t": 0 * M, "o": 100.0, "c": 101.0},
            {"t": 15 * M, "o": 100.0, "c": 102.0},
            {"t": 30 * M, "o": 100.0, "c": 103.0},
        ]
        s = toc_minute_stats(bars)
        self.assertEqual(s["turn_n"], 3)
        self.assertEqual(s["other_n"], 0)
        self.assertAlmostEqual(s["turn_mean"], 0.02, places=12)
        self.assertIsNone(s["other_mean"])

    def test_only_non_turn_bars(self):
        """Only bars at non-turn minutes."""
        bars = [
            {"t": 1 * M, "o": 100.0, "c": 101.0},
            {"t": 2 * M, "o": 100.0, "c": 102.0},
        ]
        s = toc_minute_stats(bars)
        self.assertEqual(s["turn_n"], 0)
        self.assertEqual(s["other_n"], 2)
        self.assertIsNone(s["turn_mean"])

    def test_error_empty_bars(self):
        """Error on empty bars."""
        with self.assertRaises(ValueError):
            toc_minute_stats([])

    def test_error_zero_open(self):
        """Error on zero open price."""
        bars = [{"t": 0, "o": 0.0, "c": 1.0}]
        with self.assertRaises(ValueError):
            toc_minute_stats(bars)

    def test_error_zero_open_mixed(self):
        """Error on zero open price in a list of otherwise valid bars."""
        bars = [
            {"t": 0 * M, "o": 100.0, "c": 101.0},
            {"t": 1 * M, "o": 0.0, "c": 1.0},
        ]
        with self.assertRaises(ValueError):
            toc_minute_stats(bars)


class TestTurnOfCandleEventsEdges(unittest.TestCase):
    """Edge cases for turn_of_candle_events."""

    def test_empty_bars(self):
        """Empty bars list."""
        ev = turn_of_candle_events([])
        self.assertEqual(ev, [])

    def test_single_bar_at_target(self):
        """Single bar at target minute."""
        bars = [{"t": 14 * M, "o": 100.0, "c": 101.0}]
        ev = turn_of_candle_events(bars, lead_minutes=1, side="long")
        self.assertEqual(ev, [{"i": 0, "side": "long"}])

    def test_single_bar_not_at_target(self):
        """Single bar not at target minute."""
        bars = [{"t": 13 * M, "o": 100.0, "c": 101.0}]
        ev = turn_of_candle_events(bars, lead_minutes=1, side="long")
        self.assertEqual(ev, [])

    def test_lead_minutes_boundary_1(self):
        """lead_minutes=1 (minimum)."""
        bars = [{"t": 14 * M, "o": 100.0, "c": 101.0}]
        ev = turn_of_candle_events(bars, lead_minutes=1, side="long")
        self.assertEqual(ev, [{"i": 0, "side": "long"}])

    def test_lead_minutes_boundary_14(self):
        """lead_minutes=14 (maximum)."""
        bars = [{"t": 1 * M, "o": 100.0, "c": 101.0}]
        ev = turn_of_candle_events(bars, lead_minutes=14, side="long")
        self.assertEqual(ev, [{"i": 0, "side": "long"}])

    def test_error_lead_minutes_too_low(self):
        """Error on lead_minutes=0."""
        with self.assertRaises(ValueError):
            turn_of_candle_events([], lead_minutes=0)

    def test_error_lead_minutes_too_high(self):
        """Error on lead_minutes=15."""
        with self.assertRaises(ValueError):
            turn_of_candle_events([], lead_minutes=15)

    def test_error_invalid_side(self):
        """Error on invalid side."""
        with self.assertRaises(ValueError):
            turn_of_candle_events([], side="flat")

    def test_side_short(self):
        """side='short' works correctly."""
        bars = [{"t": 14 * M, "o": 100.0, "c": 101.0}]
        ev = turn_of_candle_events(bars, lead_minutes=1, side="short")
        self.assertEqual(ev, [{"i": 0, "side": "short"}])

    def test_multiple_matches_ascending_order(self):
        """Multiple matches returned in ascending order."""
        bars = []
        for k in range(45):
            bars.append({"t": k * M, "o": 100.0, "c": 101.0})
        ev = turn_of_candle_events(bars, lead_minutes=1, side="long")
        # Events should be at i = 14, 29, 44 (minutes 14, 14, 14)
        self.assertEqual(len(ev), 3)
        self.assertEqual([e["i"] for e in ev], [14, 29, 44])

    def test_all_lead_minutes_values(self):
        """Test all valid lead_minutes values."""
        bars = []
        for k in range(15):
            bars.append({"t": k * M, "o": 100.0, "c": 101.0})

        for lead_minutes in range(1, 15):
            target_minute = 15 - lead_minutes
            ev = turn_of_candle_events(bars, lead_minutes=lead_minutes, side="long")
            if target_minute == 0:
                self.assertEqual(ev, [{"i": 0, "side": "long"}])
            else:
                self.assertEqual(ev, [{"i": target_minute, "side": "long"}])

    def test_default_parameters(self):
        """Default parameters: lead_minutes=1, side='long'."""
        bars = [{"t": 14 * M, "o": 100.0, "c": 101.0}]
        ev1 = turn_of_candle_events(bars)
        ev2 = turn_of_candle_events(bars, lead_minutes=1, side="long")
        self.assertEqual(ev1, ev2)

    def test_gaps_in_timestamps(self):
        """Bars with gaps in timestamps."""
        bars = [
            {"t": 0 * M, "o": 100.0, "c": 101.0},
            {"t": 10 * M, "o": 100.0, "c": 101.0},  # Gap
            {"t": 20 * M, "o": 100.0, "c": 101.0},  # Gap
        ]
        ev = turn_of_candle_events(bars, lead_minutes=1, side="long")
        # Minute at i=0 is 0, i=1 is 10, i=2 is 5
        # With lead_minutes=1, we need minute=14
        self.assertEqual(ev, [])

    def test_large_indices(self):
        """Large number of bars."""
        bars = []
        for k in range(1000):
            bars.append({"t": k * M, "o": 100.0, "c": 101.0})
        ev = turn_of_candle_events(bars, lead_minutes=1, side="long")
        # Should have events at i = 14, 29, 44, ... (every 15th index + 14)
        expected_indices = [i for i in range(1000) if i % 15 == 14]
        actual_indices = [e["i"] for e in ev]
        self.assertEqual(actual_indices, expected_indices)


if __name__ == "__main__":
    unittest.main()
