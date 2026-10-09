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


DAY = 1791504000000  # 2026-10-09 00:00 UTC (epoch day 20735)
H = 3600000
MIN = 60000


def day_bars(start_ms, n, skip=()):
    """n consecutive 1m bars from start_ms, minus the minute offsets in skip."""
    return [{"t": start_ms + i * MIN, "o": i, "h": i, "l": i, "c": i, "v": 1} for i in range(n) if i not in skip]


class TestT088NewFrames(unittest.TestCase):
    """T088 (items/T088_all_timeframe_module.md): 4m, 3h, 7h day-reset, 7h_epoch."""

    def test_t088_registry_holds_the_four_keys_and_7h_flags(self):
        for tf in ("4m", "3h", "7h", "7h_epoch"):
            self.assertIn(tf, REGISTRY["timeframes"])
        self.assertIn("NO-SOURCE", REGISTRY["timeframes"]["7h"].get("flag", ""))
        self.assertIn("NO-SOURCE", REGISTRY["timeframes"]["7h_epoch"].get("flag", ""))

    def test_t088_4m_bucket_start_end(self):
        t = DAY + 9 * MIN
        self.assertEqual(bucket_start(t, "4m", REGISTRY), DAY + 8 * MIN)
        self.assertEqual(bucket_end(t, "4m", REGISTRY), DAY + 12 * MIN)

    def test_t088_3h_bucket_start_end(self):
        t = DAY + 14 * H + 30 * MIN
        self.assertEqual(bucket_start(t, "3h", REGISTRY), DAY + 12 * H)
        self.assertEqual(bucket_end(t, "3h", REGISTRY), DAY + 15 * H)

    def test_t088_7h_day_reset_buckets(self):
        cases = [(0, 0, 7), (6 * H + 59 * MIN, 0, 7), (7 * H, 7, 14), (20 * H + 59 * MIN, 14, 21),
                 (21 * H, 21, 24), (23 * H + 59 * MIN, 21, 24)]
        for off, s, e in cases:
            self.assertEqual(bucket_start(DAY + off, "7h", REGISTRY), DAY + s * H, off)
            self.assertEqual(bucket_end(DAY + off, "7h", REGISTRY), DAY + e * H, off)
        # Next day restarts at 00:00, not at 04:00.
        self.assertEqual(bucket_start(DAY + 24 * H + 30 * MIN, "7h", REGISTRY), DAY + 24 * H)

    def test_t088_7h_epoch_drifts_against_utc_day(self):
        # 1791504000 % 25200 = 10800: the epoch bucket holding 00:00 opened at 21:00 the day before.
        self.assertEqual(bucket_start(DAY, "7h_epoch", REGISTRY), DAY - 3 * H)
        self.assertEqual(bucket_end(DAY, "7h_epoch", REGISTRY), DAY + 4 * H)

    def test_t088_7h_full_day_is_four_bars_last_is_3h_stub(self):
        out = resample(day_bars(DAY, 1440), "7h", REGISTRY)
        self.assertEqual([b["t"] for b in out], [DAY, DAY + 7 * H, DAY + 14 * H, DAY + 21 * H])
        self.assertEqual([b["n_bars"] for b in out], [420, 420, 420, 180])
        self.assertEqual([b["gap_count"] for b in out], [0, 0, 0, 0])
        last = out[-1]
        self.assertEqual((last["o"], last["c"], last["v"]), (1260, 1439, 180))

    def test_t088_7h_open_stub_is_not_closed(self):
        out = resample(day_bars(DAY, 22 * 60), "7h", REGISTRY)
        self.assertEqual(len(out), 3)

    def test_t088_7h_gap_count(self):
        out = resample(day_bars(DAY, 7 * 60 + 1, skip=(5, 100)), "7h", REGISTRY)
        self.assertEqual(len(out), 1)
        self.assertEqual((out[0]["n_bars"], out[0]["gap_count"]), (418, 2))

    def test_t088_4m_and_3h_gap_and_closed_only(self):
        out = resample(day_bars(DAY, 10, skip=(1,)), "4m", REGISTRY)
        self.assertEqual([(b["t"], b["n_bars"], b["gap_count"]) for b in out],
                         [(DAY, 3, 1), (DAY + 4 * MIN, 4, 0)])
        out = resample(day_bars(DAY, 7 * 60), "3h", REGISTRY)
        self.assertEqual([(b["t"], b["n_bars"]) for b in out], [(DAY, 180), (DAY + 3 * H, 180)])


if __name__ == "__main__":
    unittest.main()
