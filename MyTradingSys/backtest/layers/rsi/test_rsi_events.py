import unittest

from MyTradingSys.backtest.layers.rsi.rsi_events import rsi_events


class TestRsiEvents(unittest.TestCase):
    """layers/rsi/TEST_PLAN.md rsi_events.py section."""

    def test_e1_full_walk_every_edge_case(self):
        rsi = [None, None, 50, 55, 59, 61, 57, 56, 65, 64, 61, 59, 63, 63, 60, 56, 55, 58, 60, 60,
               57, None, 59, 65, 60, 61]
        ts = list(range(26))
        got = rsi_events(rsi, ts, level=60, tolerance=2)
        expected = [
            {"t": 6, "event": "rejection", "level_value": 60, "tolerance_used": 2, "penetration": 1},
            {"t": 8, "event": "cross", "level_value": 60, "tolerance_used": 2, "penetration": 5, "direction": "up"},
            {"t": 12, "event": "support", "level_value": 60, "tolerance_used": 2, "penetration": 1},
            {"t": 15, "event": "failure", "level_value": 60, "tolerance_used": 2, "penetration": 4},
            {"t": 20, "event": "rejection", "level_value": 60, "tolerance_used": 2, "penetration": 2},
            {"t": 23, "event": "failure", "level_value": 60, "tolerance_used": 2, "penetration": 5},
        ]
        self.assertEqual(len(got), len(expected))
        for g, e in zip(got, expected):
            self.assertEqual(g["t"], e["t"])
            self.assertEqual(g["event"], e["event"])
            self.assertEqual(g["level_value"], e["level_value"])
            self.assertEqual(g["tolerance_used"], e["tolerance_used"])
            self.assertAlmostEqual(g["penetration"], e["penetration"], delta=1e-9)
            if "direction" in e:
                self.assertEqual(g["direction"], e["direction"])

    def test_e3_invalid_tolerance_raises(self):
        with self.assertRaises(ValueError):
            rsi_events([50, 60], [0, 1], level=60, tolerance=0)


if __name__ == "__main__":
    unittest.main()
