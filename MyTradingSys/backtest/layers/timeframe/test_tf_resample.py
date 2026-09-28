import json
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.timeframe.tf_resample import bucket_start, bucket_end, resample

REGISTRY = json.loads((Path(__file__).parent / "registry.json").read_text())


def m(minute, v=1):
    """1m bar dict keyed by epoch-minute (t stored as epoch ms) for TF-B* readability cases."""
    t = minute * 60000
    return {"t": t, "o": minute, "h": minute, "l": minute, "c": minute, "v": v}


class TestBucketBoundaryMath(unittest.TestCase):
    """layers/timeframe/TEST_PLAN.md Part A."""

    def test_tf_a1_2d_bucket_start_odd_epoch_day(self):
        t = 20725 * 86400000
        self.assertEqual(bucket_start(t, "2d", REGISTRY), 1790553600000)
        self.assertEqual(bucket_end(t, "2d", REGISTRY), 1790726400000)

    def test_tf_a2_3d_bucket_start_same_bucket(self):
        for day in (20724, 20725, 20726):
            t = day * 86400000
            self.assertEqual(bucket_start(t, "3d", REGISTRY), 1790553600000)
        t_new = 20727 * 86400000
        self.assertEqual(bucket_start(t_new, "3d", REGISTRY), 20727 * 86400000)

    def test_tf_a3_5d_bucket_start_crosses_midweek(self):
        t28 = 20724 * 86400000
        self.assertEqual(bucket_start(t28, "5d", REGISTRY), 1790208000000)
        t29 = 20725 * 86400000
        self.assertEqual(bucket_start(t29, "5d", REGISTRY), 1790640000000)

    def test_tf_a4_1w_monday_anchoring(self):
        t_wed = 20726 * 86400000 + 15 * 3600000
        self.assertEqual(bucket_start(t_wed, "1w", REGISTRY), 1790553600000)
        self.assertEqual(bucket_end(t_wed, "1w", REGISTRY), 1791158400000)
        # A timestamp already on the Monday does not shift.
        t_mon = 20724 * 86400000 + 10 * 3600000 + 15 * 60000
        self.assertEqual(bucket_start(t_mon, "1w", REGISTRY), 1790553600000)

    def test_tf_a5_1m_calendar_month_incl_leap(self):
        t = 1790812799000  # 2026-09-30 23:59:00 UTC (60000ms before bucket end)
        self.assertEqual(bucket_start(t, "1M", REGISTRY), 1788220800000)
        self.assertEqual(bucket_end(t, "1M", REGISTRY), 1790812800000)
        self.assertEqual((1790812800000 - 1788220800000) // 60000, 43200)

        t_leap = 1709208000000  # 2024-02-29 12:00:00 UTC
        self.assertEqual(bucket_start(t_leap, "1M", REGISTRY), 1706745600000)
        self.assertEqual(bucket_end(t_leap, "1M", REGISTRY), 1709251200000)
        self.assertEqual((1709251200000 - 1706745600000) // 60000, 41760)


class TestResampleAggregation(unittest.TestCase):
    """layers/timeframe/TEST_PLAN.md Part B."""

    def test_tf_b1_3m_alignment_gap_closed_only(self):
        bars = [m(minute) for minute in (7, 8, 9, 10, 11, 12)]
        out = resample(bars, "3m", REGISTRY)
        self.assertEqual(len(out), 2)
        b0, b1 = out
        self.assertEqual(b0["t"], 6 * 60000)
        self.assertEqual((b0["o"], b0["h"], b0["l"], b0["c"], b0["v"]), (7, 8, 7, 8, 2))
        self.assertEqual(b0["gap_count"], 1)
        self.assertEqual(b0["n_bars"], 2)
        self.assertEqual(b1["t"], 9 * 60000)
        self.assertEqual((b1["o"], b1["h"], b1["l"], b1["c"], b1["v"]), (9, 11, 9, 11, 3))
        self.assertEqual(b1["gap_count"], 0)
        self.assertEqual(b1["n_bars"], 3)

    def test_tf_b2_10m_closed_bars_only_cuts_partial_bucket(self):
        bars = [m(minute) for minute in range(0, 25)]
        out = resample(bars, "10m", REGISTRY)
        self.assertEqual(len(out), 2)
        b0, b1 = out
        self.assertEqual((b0["t"], b0["o"], b0["h"], b0["l"], b0["c"], b0["v"], b0["gap_count"], b0["n_bars"]),
                          (0, 0, 9, 0, 9, 10, 0, 10))
        self.assertEqual((b1["t"], b1["o"], b1["h"], b1["l"], b1["c"], b1["v"], b1["gap_count"], b1["n_bars"]),
                          (10 * 60000, 10, 19, 10, 19, 10, 0, 10))
        # bucket 20 (minutes 20-24, only 5 bars) must be excluded: not closed.
        self.assertFalse(any(b["t"] == 20 * 60000 for b in out))

    def test_tf_b3_empty_input(self):
        for tf in ("1m", "1d", "1w", "1M"):
            self.assertEqual(resample([], tf, REGISTRY), [])

    def test_tf_b4_unknown_timeframe_raises(self):
        bars = [m(0)]
        with self.assertRaises(Exception):
            resample(bars, "7m", REGISTRY)


if __name__ == "__main__":
    unittest.main()
