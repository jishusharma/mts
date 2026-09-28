import unittest

from MyTradingSys.backtest.layers.rsi.rsi_ma_events import rsi_ma_events


class TestRsiMaEvents(unittest.TestCase):
    """Spec 078-rsi-ma-events.md hand-computed check, reproducing layers/rsi/TEST_PLAN.md
    rsi_events.py Case E1 exactly via a constant rsi_ma=60.0 (diff = rsi - 60.0)."""

    RSI = [None, None, 50, 55, 59, 61, 57, 56, 65, 64, 61, 59, 63, 63, 60, 56, 55, 58, 60, 60,
           57, None, 59, 65, 60, 61]

    def _rsi_ma(self):
        return [None if v is None else 60.0 for v in self.RSI]

    def test_reproduces_case_e1_with_renamed_events_and_rsi_ma_value(self):
        ts = list(range(26))
        got = rsi_ma_events(self.RSI, self._rsi_ma(), ts, tolerance=2)
        expected = [
            {"t": 6, "event": "ma_rejection", "tolerance_used": 2, "penetration": 1},
            {"t": 8, "event": "cross", "tolerance_used": 2, "penetration": 5, "direction": "up"},
            {"t": 12, "event": "ma_support", "tolerance_used": 2, "penetration": 1},
            {"t": 15, "event": "failure", "tolerance_used": 2, "penetration": 4},
            {"t": 20, "event": "ma_rejection", "tolerance_used": 2, "penetration": 2},
            {"t": 23, "event": "failure", "tolerance_used": 2, "penetration": 5},
        ]
        self.assertEqual(len(got), len(expected))
        for g, e in zip(got, expected):
            self.assertEqual(g["t"], e["t"])
            self.assertEqual(g["event"], e["event"])
            self.assertEqual(g["tolerance_used"], e["tolerance_used"])
            self.assertAlmostEqual(g["penetration"], e["penetration"], delta=1e-9)
            if "direction" in e:
                self.assertEqual(g["direction"], e["direction"])
            self.assertNotIn("level_value", g)
            self.assertAlmostEqual(g["rsi_ma_value"], 60.0, delta=1e-9)

    def test_invalid_tolerance_raises(self):
        ts = list(range(26))
        with self.assertRaises(ValueError):
            rsi_ma_events(self.RSI, self._rsi_ma(), ts, tolerance=0)

    def test_mismatched_lengths_raise(self):
        with self.assertRaises(ValueError):
            rsi_ma_events([50, 55], [50], [0, 1], tolerance=2)


if __name__ == "__main__":
    unittest.main()
