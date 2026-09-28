import unittest

from MyTradingSys.backtest.layers.rsi.tolerance_sweep import (
    event_side, sweep_tolerances, pick_best_tolerance,
)


class TestEventSide(unittest.TestCase):
    def test_support_is_long(self):
        self.assertEqual(event_side({"event": "support"}), "long")

    def test_rejection_is_short(self):
        self.assertEqual(event_side({"event": "rejection"}), "short")

    def test_cross_up_is_long_down_is_short(self):
        self.assertEqual(event_side({"event": "cross", "direction": "up"}), "long")
        self.assertEqual(event_side({"event": "cross", "direction": "down"}), "short")

    def test_failure_is_none(self):
        self.assertIsNone(event_side({"event": "failure"}))


class TestSweepAndPick(unittest.TestCase):
    """Spec 081-d3-tolerance-sweep.md hand-computed check."""

    RSI = [None, None, 59, 61, 57, 63, 58, 62]
    TS = list(range(8))
    CLOSES = [100, 101, 99, 102, 98, 103, 97, 104]

    def test_sweep_at_tolerance_0_5_and_2_0(self):
        sweep = sweep_tolerances(self.RSI, self.TS, self.CLOSES, level=60,
                                  tolerances=(0.5, 2.0), horizons=(1,))

        s05 = sweep[0.5]
        self.assertEqual(s05["n_events_total"], 5)
        self.assertEqual(s05["n_events_scored"], 5)
        self.assertEqual(s05["stats"][1]["n"], 4)
        self.assertAlmostEqual(s05["stats"][1]["mean_return"], -0.055163, delta=1e-4)
        self.assertAlmostEqual(s05["stats"][1]["hit_rate"], 0.0, delta=1e-9)

        s20 = sweep[2.0]
        self.assertEqual(s20["n_events_total"], 1)
        self.assertEqual(s20["n_events_scored"], 1)
        self.assertEqual(s20["stats"][1]["n"], 1)
        self.assertAlmostEqual(s20["stats"][1]["mean_return"], -0.058252, delta=1e-4)
        self.assertAlmostEqual(s20["stats"][1]["hit_rate"], 0.0, delta=1e-9)

    def test_pick_best_tolerance_prefers_qualifying_larger_n(self):
        sweep = sweep_tolerances(self.RSI, self.TS, self.CLOSES, level=60,
                                  tolerances=(0.5, 2.0), horizons=(1,))
        got = pick_best_tolerance(sweep, horizon=1, min_events=2)
        self.assertEqual(got, 0.5)

    def test_pick_best_tolerance_none_when_nothing_qualifies(self):
        sweep = sweep_tolerances(self.RSI, self.TS, self.CLOSES, level=60,
                                  tolerances=(0.5, 2.0), horizons=(1,))
        self.assertIsNone(pick_best_tolerance(sweep, horizon=1, min_events=100))

    def test_pick_best_tolerance_missing_horizon_raises(self):
        sweep = sweep_tolerances(self.RSI, self.TS, self.CLOSES, level=60,
                                  tolerances=(0.5, 2.0), horizons=(1,))
        with self.assertRaises(KeyError):
            pick_best_tolerance(sweep, horizon=999, min_events=1)

    def test_sweep_raises_on_empty_closes(self):
        with self.assertRaises(ValueError):
            sweep_tolerances(self.RSI, self.TS, [], level=60, tolerances=(1.0,), horizons=(1,))

    def test_sweep_skips_non_positive_tolerances(self):
        sweep = sweep_tolerances(self.RSI, self.TS, self.CLOSES, level=60,
                                  tolerances=(0.0, -1.0, 0.5), horizons=(1,))
        self.assertEqual(list(sweep.keys()), [0.5])


if __name__ == "__main__":
    unittest.main()
