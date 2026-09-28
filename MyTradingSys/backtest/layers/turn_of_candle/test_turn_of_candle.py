import unittest

from MyTradingSys.backtest.layers.turn_of_candle.turn_of_candle import (
    minute_of_quarter,
    toc_minute_stats,
    turn_of_candle_events,
)

# Expected numbers hand-computed from FORMULAS.md section 16 (T055 C3).
M = 60000


def make_bars():
    bars = [{"t": k * M, "o": 100.0, "c": 100.0} for k in range(30)]
    bars[0]["c"] = 101.0    # +0.01
    bars[15]["c"] = 103.0   # +0.03
    bars[1]["c"] = 99.0     # -0.01
    return bars


class TestMinuteOfQuarter(unittest.TestCase):
    def test_values(self):
        self.assertEqual(minute_of_quarter(0), 0)
        self.assertEqual(minute_of_quarter(14 * M), 14)
        self.assertEqual(minute_of_quarter(15 * M), 0)
        self.assertEqual(minute_of_quarter(3600 * 1000 + 47 * M), 2)  # minute 47 of hour -> 47 % 15 = 2


class TestStats(unittest.TestCase):
    def test_stats(self):
        s = toc_minute_stats(make_bars())
        self.assertEqual(s["turn_n"], 2)
        self.assertEqual(s["other_n"], 28)
        self.assertAlmostEqual(s["turn_mean"], 0.02, places=12)
        self.assertAlmostEqual(s["other_mean"], -0.01 / 28, places=12)
        self.assertAlmostEqual(s["by_minute"][1], -0.005, places=12)
        self.assertAlmostEqual(s["by_minute"][0], 0.02, places=12)
        self.assertEqual(sorted(s["by_minute"]), list(range(15)))

    def test_no_turn_bars(self):
        s = toc_minute_stats([{"t": 1 * M, "o": 100.0, "c": 101.0}])
        self.assertIsNone(s["turn_mean"])
        self.assertEqual(s["turn_n"], 0)
        self.assertAlmostEqual(s["other_mean"], 0.01, places=12)

    def test_errors(self):
        with self.assertRaises(ValueError):
            toc_minute_stats([])
        with self.assertRaises(ValueError):
            toc_minute_stats([{"t": 0, "o": 0.0, "c": 1.0}])


class TestEvents(unittest.TestCase):
    def test_lead1(self):
        ev = turn_of_candle_events(make_bars(), lead_minutes=1, side="long")
        self.assertEqual(ev, [{"i": 14, "side": "long"}, {"i": 29, "side": "long"}])

    def test_lead2_short(self):
        ev = turn_of_candle_events(make_bars(), lead_minutes=2, side="short")
        self.assertEqual(ev, [{"i": 13, "side": "short"}, {"i": 28, "side": "short"}])

    def test_empty_and_errors(self):
        self.assertEqual(turn_of_candle_events([]), [])
        with self.assertRaises(ValueError):
            turn_of_candle_events(make_bars(), lead_minutes=0)
        with self.assertRaises(ValueError):
            turn_of_candle_events(make_bars(), lead_minutes=15)
        with self.assertRaises(ValueError):
            turn_of_candle_events(make_bars(), side="flat")


if __name__ == "__main__":
    unittest.main()
