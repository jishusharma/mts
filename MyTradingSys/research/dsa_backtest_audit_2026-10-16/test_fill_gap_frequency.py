"""Test for fill_gap_frequency.py: FILL_CANARY plant (entry 100, stop 99, R = 1, gap bar open 98.01).
Run: python -m pytest MyTradingSys/research/dsa_backtest_audit_2026-10-16/test_fill_gap_frequency.py
Expected numbers are by hand: understatement = (stop - open) / D = (99.00 - 98.01) / 1.00 = 0.99 R.
"""
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fill_gap_frequency as G  # noqa: E402


def b(k, o, h, l, c):
    return {"t": k * 60000, "o": o, "h": h, "l": l, "c": c}


class FillGapFrequency(unittest.TestCase):
    def test_planted_post_fill_gap_long(self):
        bars = [b(0, 100, 100.2, 99.8, 100), b(1, 100, 100.1, 99.5, 99.9), b(2, 98.01, 98.2, 97.9, 98.0)]
        recs = G.stop_exit_records(bars, [(0, 1, 100.0, 1.0, 99.0)])
        s = G.summarize(recs)
        self.assertEqual((s["n_stop"], s["n_gap"]), (1, 1))
        self.assertAlmostEqual(s["share"], 1.0)
        self.assertAlmostEqual(s["mean_r"], 0.99, places=9)
        self.assertAlmostEqual(s["p95_r"], 0.99, places=9)
        self.assertEqual(recs[0]["where"], "post_fill")

    def test_planted_fill_bar_gap_short_mirror(self):
        # short: entry 100, stop 101, fill bar opens 101.99 (beyond stop) -> F scenario, 0.99 R
        bars = [b(0, 101.99, 102.1, 99.9, 100.5), b(1, 100, 100.2, 99.8, 100)]
        recs = G.stop_exit_records(bars, [(0, -1, 100.0, 1.0, 101.0)])
        s = G.summarize(recs)
        self.assertEqual((s["n_stop"], s["n_gap"]), (1, 1))
        self.assertAlmostEqual(s["mean_r"], 0.99, places=9)
        self.assertEqual(recs[0]["where"], "fill_bar")

    def test_clean_stop_is_not_a_gap(self):
        bars = [b(0, 100, 100.2, 99.8, 100), b(1, 99.9, 100.0, 98.9, 99.0)]
        s = G.summarize(G.stop_exit_records(bars, [(0, 1, 100.0, 1.0, 99.0)]))
        self.assertEqual((s["n_stop"], s["n_gap"]), (1, 0))
        self.assertAlmostEqual(s["share"], 0.0)

    def test_p95_nearest_rank(self):
        self.assertAlmostEqual(G.pctl([float(x) for x in range(1, 21)], 95), 19.0)


if __name__ == "__main__":
    unittest.main()
