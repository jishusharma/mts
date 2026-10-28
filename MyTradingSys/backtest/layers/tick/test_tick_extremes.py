import unittest

from MyTradingSys.backtest.layers.tick.tick_extremes import (
    bucket_start_ms,
    resample,
    session_tag,
    in_funding_window,
    gap_tiers,
    rank_extremes,
    build_tier_table,
)


def bar(t, o, c, v, tbv, h=None, l=None):
    return {
        "t": t, "o": o, "c": c,
        "h": h if h is not None else max(o, c),
        "l": l if l is not None else min(o, c),
        "v": v, "tbv": tbv,
    }


# 12 one-minute bars used in the spec's own hand-computed fixture
# (091-tick-extremes.md). delta = 2*tbv - v for each bar.
SPEC_BARS = [
    bar(0,      100, 100, 10, 5),    # delta 0
    bar(60000,  100, 101, 20, 15),   # delta 10
    bar(120000, 101, 99,  10, 2),    # delta -6
    bar(180000, 99,  102, 30, 20),   # delta 10
    bar(240000, 102, 98,  10, 1),    # delta -8
    bar(300000, 98,  103, 40, 35),   # delta 30
    bar(360000, 103, 104, 10, 9),    # delta 8
    bar(420000, 104, 101, 10, 0),    # delta -10
    bar(480000, 101, 105, 20, 18),   # delta 16
    bar(540000, 105, 103, 10, 4),    # delta -2
    bar(600000, 103, 106, 10, 10),   # delta 10
    bar(660000, 106, 104, 10, 3),    # delta -4
]


class TestBucketStartMs(unittest.TestCase):
    def test_floor_alignment(self):
        # 2-minute buckets: minute 3 (180000ms) floors to bucket start 120000ms.
        self.assertEqual(bucket_start_ms(180000, 2), 120000)
        self.assertEqual(bucket_start_ms(239999, 2), 120000)
        self.assertEqual(bucket_start_ms(240000, 2), 240000)

    def test_rejects_non_positive_tf(self):
        with self.assertRaises(ValueError):
            bucket_start_ms(0, 0)


class TestResample(unittest.TestCase):
    def test_two_minute_buckets_hand_computed(self):
        # Hand-computed independently (see spec's own worked example):
        # B0(bars0,1): v=30,tbv=20 -> net_delta=2*20-30=10; o=100,c=101 -> pct=1.0
        # B1(bars2,3): v=40,tbv=22 -> net_delta=2*22-40=4;  o=101,c=102 -> pct=(1/101)*100
        # B2(bars4,5): v=50,tbv=36 -> net_delta=2*36-50=22; o=102,c=103 -> pct=(1/102)*100
        # B3(bars6,7): v=20,tbv=9  -> net_delta=2*9-20=-2;  o=103,c=101 -> pct=(-2/103)*100
        # B4(bars8,9): v=30,tbv=22 -> net_delta=2*22-30=14; o=101,c=103 -> pct=(2/101)*100
        # B5(bars10,11): v=20,tbv=13 -> net_delta=2*13-20=6; o=103,c=104 -> pct=(1/103)*100
        buckets = resample(SPEC_BARS, 2)
        self.assertEqual(len(buckets), 6)
        expected_net_delta = [10, 4, 22, -2, 14, 6]
        expected_o = [100, 101, 102, 103, 101, 103]
        expected_c = [101, 102, 103, 101, 103, 104]
        expected_t = [0, 120000, 240000, 360000, 480000, 600000]
        for i, b in enumerate(buckets):
            self.assertEqual(b["t"], expected_t[i])
            self.assertEqual(b["o"], expected_o[i])
            self.assertEqual(b["c"], expected_c[i])
            self.assertEqual(b["net_delta"], expected_net_delta[i])
            self.assertEqual(b["cvd_change"], expected_net_delta[i])
            self.assertAlmostEqual(
                b["price_change_pct"],
                (expected_c[i] - expected_o[i]) / expected_o[i] * 100.0,
                places=9,
            )
        # volume = sum of v within the bucket
        self.assertEqual(buckets[0]["volume"], 30)
        self.assertEqual(buckets[2]["volume"], 50)

    def test_one_minute_is_identity_on_delta(self):
        buckets = resample(SPEC_BARS, 1)
        self.assertEqual(len(buckets), 12)
        # bar 5 alone: v=40, tbv=35 -> net_delta = 2*35-40 = 30
        self.assertEqual(buckets[5]["net_delta"], 30)
        self.assertEqual(buckets[5]["t"], 300000)

    def test_empty_bars_raises(self):
        with self.assertRaises(ValueError):
            resample([], 2)

    def test_zero_open_raises_on_price_pct(self):
        bars = [bar(0, 0, 5, 10, 5)]
        with self.assertRaises(ValueError):
            resample(bars, 1)


class TestSessionTag(unittest.TestCase):
    def test_boundaries(self):
        # md = minute of day; boundaries per the spec: asian[0,480) european[480,780)
        # overlap[780,990) american[990,1260) off_hours[1260,1440)
        self.assertEqual(session_tag(0), "asian")
        self.assertEqual(session_tag(479 * 60000), "asian")
        self.assertEqual(session_tag(480 * 60000), "european")
        self.assertEqual(session_tag(779 * 60000), "european")
        self.assertEqual(session_tag(780 * 60000), "overlap")
        self.assertEqual(session_tag(989 * 60000), "overlap")
        self.assertEqual(session_tag(990 * 60000), "american")
        self.assertEqual(session_tag(1259 * 60000), "american")
        self.assertEqual(session_tag(1260 * 60000), "off_hours")
        self.assertEqual(session_tag(1439 * 60000), "off_hours")

    def test_wraps_across_days(self):
        # minute-of-day for t = 1440+5 minutes is 5 -> still "asian"
        self.assertEqual(session_tag((1440 + 5) * 60000), "asian")


class TestInFundingWindow(unittest.TestCase):
    def test_hand_computed_points(self):
        # Hand-computed independently, resets at md=0,480,960, window=30:
        self.assertTrue(in_funding_window(0))                    # md=0, dist 0
        self.assertTrue(in_funding_window(479 * 60000))          # dist to 480 = 1
        self.assertTrue(in_funding_window(500 * 60000))          # dist to 480 = 20
        self.assertFalse(in_funding_window(600 * 60000))         # nearest dist 120
        self.assertFalse(in_funding_window(800 * 60000))         # nearest dist 160 (to 960)
        self.assertTrue(in_funding_window(965 * 60000))          # dist to 960 = 5
        self.assertFalse(in_funding_window(1000 * 60000))        # dist to 960 = 40
        self.assertFalse(in_funding_window(1300 * 60000))        # nearest wrap dist 140
        # circular wrap: md=1439 is 1 minute from the NEXT day's 0-reset
        self.assertTrue(in_funding_window(1439 * 60000))


class TestGapTiers(unittest.TestCase):
    def test_hand_computed_break(self):
        # values already sorted descending: [22,14,10,6,4,-2]
        # gaps = [8,4,4,2,6]; median = 4; threshold (factor=1.5) = 6
        # only gap[0]=8 exceeds 6 -> one break after rank 0
        tiers = gap_tiers([22, 14, 10, 6, 4, -2], factor=1.5)
        self.assertEqual(tiers, [1, 2, 2, 2, 2, 2])

    def test_single_value(self):
        self.assertEqual(gap_tiers([5.0]), [1])

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            gap_tiers([])

    def test_unsorted_raises(self):
        with self.assertRaises(ValueError):
            gap_tiers([1, 5, 2])


class TestRankExtremes(unittest.TestCase):
    def test_high_and_low_hand_computed(self):
        buckets = resample(SPEC_BARS, 2)
        result = rank_extremes(buckets, "net_delta", top_n=20)
        # HIGH side descending: 22(t=240000),14(t=480000),10(t=0),6(t=600000),4(t=120000),-2(t=360000)
        high_values = [e["value"] for e in result["high"]]
        self.assertEqual(high_values, [22, 14, 10, 6, 4, -2])
        self.assertEqual(result["high"][0]["t"], 240000)
        self.assertEqual(result["high"][0]["tier"], 1)
        self.assertEqual(result["high"][1]["tier"], 2)
        # LOW side ascending: -2(t=360000),4(t=120000),6(t=600000),10(t=0),14(t=480000),22(t=240000)
        low_values = [e["value"] for e in result["low"]]
        self.assertEqual(low_values, [-2, 4, 6, 10, 14, 22])
        self.assertEqual(result["low"][0]["t"], 360000)
        # session/funding tags present and correctly computed for one entry
        self.assertEqual(result["high"][0]["session"], session_tag(240000))
        self.assertEqual(result["high"][0]["funding_window"], in_funding_window(240000))

    def test_invalid_indicator_raises(self):
        buckets = resample(SPEC_BARS, 2)
        with self.assertRaises(ValueError):
            rank_extremes(buckets, "not_a_real_indicator")

    def test_empty_buckets_raises(self):
        with self.assertRaises(ValueError):
            rank_extremes([], "net_delta")


class TestBuildTierTable(unittest.TestCase):
    def test_shape_and_skips_undersized_timeframes(self):
        # 12 minutes of data: tf=15 cannot form a single closed 15-minute bucket
        # (would need bucket_end=900000 <= last bar close 720000, which is false),
        # so "15" must be omitted; "1".."10" all fit at least one closed bucket.
        table = build_tier_table(SPEC_BARS, timeframes=(1, 2, 3, 5, 10, 15),
                                  indicators=("net_delta", "volume"), top_n=5)
        self.assertNotIn("15", table)
        self.assertIn("2", table)
        self.assertIn("net_delta", table["2"])
        self.assertIn("volume", table["2"])
        self.assertIn("high", table["2"]["net_delta"])
        self.assertIn("low", table["2"]["net_delta"])


if __name__ == "__main__":
    unittest.main()
