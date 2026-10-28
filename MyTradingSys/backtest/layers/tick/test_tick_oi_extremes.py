import unittest

from MyTradingSys.backtest.layers.tick.tick_oi_extremes import (
    resample_oi,
    oi_delta_series,
    session_tag,
    in_funding_window,
    gap_tiers,
    rank_oi_extremes,
    build_oi_tier_table,
)


def oi_bar(t, oi, oi_usd=None):
    return {"t": t, "oi": oi, "oi_usd": oi_usd if oi_usd is not None else oi * 50000.0}


# Six 5-minute bars used in the spec's own hand-computed fixture
# (092-tick-oi-extremes.md). oi = [1000, 1050, 1010, 1120, 1080, 1200].
SPEC_BARS = [
    oi_bar(0, 1000),
    oi_bar(300000, 1050),
    oi_bar(600000, 1010),
    oi_bar(900000, 1120),
    oi_bar(1200000, 1080),
    oi_bar(1500000, 1200),
]


class TestResampleOi(unittest.TestCase):
    def test_native_5m_identity(self):
        buckets = resample_oi(SPEC_BARS, 5)
        self.assertEqual(len(buckets), 6)
        self.assertEqual([b["oi_last"] for b in buckets], [1000, 1050, 1010, 1120, 1080, 1200])
        self.assertEqual(buckets[0]["t"], 0)
        self.assertEqual(buckets[-1]["t"], 1500000)

    def test_10m_buckets_take_last_sample(self):
        # bucket(0,10m) covers bars t=0,300000 -> oi_last = 1050
        # bucket(600000,10m) covers bars t=600000,900000 -> oi_last = 1120
        # bucket(1200000,10m) covers bars t=1200000,1500000 -> oi_last = 1200
        buckets = resample_oi(SPEC_BARS, 10)
        self.assertEqual([b["oi_last"] for b in buckets], [1050, 1120, 1200])
        self.assertEqual([b["t"] for b in buckets], [0, 600000, 1200000])

    def test_rejects_non_multiple_of_5(self):
        with self.assertRaises(ValueError):
            resample_oi(SPEC_BARS, 3)

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            resample_oi([], 5)


class TestOiDeltaSeries(unittest.TestCase):
    def test_hand_computed_deltas(self):
        # 50-40+110-40+120 series independently derived in the spec:
        # k=1: 1050-1000=50 @300000; k=2: 1010-1050=-40 @600000;
        # k=3: 1120-1010=110 @900000; k=4: 1080-1120=-40 @1200000;
        # k=5: 1200-1080=120 @1500000
        buckets = resample_oi(SPEC_BARS, 5)
        deltas = oi_delta_series(buckets)
        self.assertEqual([d["oi_delta"] for d in deltas], [50, -40, 110, -40, 120])
        self.assertEqual([d["t"] for d in deltas], [300000, 600000, 900000, 1200000, 1500000])

    def test_single_bucket_raises(self):
        with self.assertRaises(ValueError):
            oi_delta_series([{"t": 0, "oi_last": 1000, "oi_usd_last": 1.0, "n": 1}])


class TestSharedHelpersMatchTickExtremes(unittest.TestCase):
    """Same boundary contract as tick_extremes.py -- duplicated per the spec's own note."""

    def test_session_tag_boundaries(self):
        self.assertEqual(session_tag(0), "asian")
        self.assertEqual(session_tag(480 * 60000), "european")
        self.assertEqual(session_tag(780 * 60000), "overlap")
        self.assertEqual(session_tag(990 * 60000), "american")
        self.assertEqual(session_tag(1260 * 60000), "off_hours")

    def test_funding_window_wrap(self):
        self.assertTrue(in_funding_window(1439 * 60000))
        self.assertFalse(in_funding_window(700 * 60000))

    def test_gap_tiers_basic(self):
        self.assertEqual(gap_tiers([10.0]), [1])
        with self.assertRaises(ValueError):
            gap_tiers([])


class TestRankOiExtremes(unittest.TestCase):
    def test_high_and_low_hand_computed(self):
        # Independently re-derived (see spec 092's worked example):
        # HIGH descending [120,110,50,-40(t=600000),-40(t=1200000)]
        # gaps=[10,60,90,0]; median=35; threshold(1.5x)=52.5
        # tiers: 120->1, 110->1 (gap 10<=52.5), 50->2 (gap 60>52.5),
        #        -40(600000)->3 (gap 90>52.5), -40(1200000)->3 (gap 0<=52.5)
        deltas = oi_delta_series(resample_oi(SPEC_BARS, 5))
        result = rank_oi_extremes(deltas, top_n=20)
        high_values = [e["value"] for e in result["high"]]
        high_tiers = [e["tier"] for e in result["high"]]
        self.assertEqual(high_values, [120, 110, 50, -40, -40])
        self.assertEqual(high_tiers, [1, 1, 2, 3, 3])
        self.assertEqual(result["high"][3]["t"], 600000)
        self.assertEqual(result["high"][4]["t"], 1200000)

        # LOW ascending [-40(t=600000),-40(t=1200000),50,110,120] -> tiers [1,1,2,3,3]
        low_values = [e["value"] for e in result["low"]]
        low_tiers = [e["tier"] for e in result["low"]]
        self.assertEqual(low_values, [-40, -40, 50, 110, 120])
        self.assertEqual(low_tiers, [1, 1, 2, 3, 3])
        self.assertEqual(result["low"][0]["t"], 600000)
        self.assertEqual(result["low"][1]["t"], 1200000)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            rank_oi_extremes([])


class TestBuildOiTierTable(unittest.TestCase):
    def test_shape_and_skips_undersized_timeframe(self):
        # 6 native 5m bars = 30 minutes of data; tf=15 needs >=2 closed
        # 15-minute buckets (30 min) to form even one delta -- here it can
        # (buckets at t=0 and t=900000, both closed since bucket_end<=1500000+300000),
        # so "15" IS present; tf=10 likewise present; tf=5 present.
        table = build_oi_tier_table(SPEC_BARS, timeframes=(5, 10, 15), top_n=5)
        self.assertIn("5", table)
        self.assertIn("10", table)
        self.assertIn("15", table)
        self.assertIn("high", table["5"])
        self.assertIn("low", table["5"])

    def test_skips_when_fewer_than_two_buckets(self):
        # Only 20 minutes of data (4 bars): tf=15 forms exactly one closed
        # bucket (t=0..15m), not two, so no delta can be computed -> skipped.
        short_bars = SPEC_BARS[:4]  # t = 0,300000,600000,900000 (0..15 min)
        table = build_oi_tier_table(short_bars, timeframes=(5, 10, 15), top_n=5)
        self.assertNotIn("15", table)
        self.assertIn("5", table)


if __name__ == "__main__":
    unittest.main()
