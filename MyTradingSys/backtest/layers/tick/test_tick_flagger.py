import unittest

from MyTradingSys.backtest.layers.tick.tick_flagger import (
    tier_boundaries,
    classify_reading,
    should_emit,
    make_flag,
    replay,
)


# Tier table fragment used throughout (hand-built, matches 093-tick-live-flagger.md's
# own worked example so both the spec and this test agree on the same ground truth,
# independently derived by inspection of the tier ordering rule: tier_boundaries takes
# the LAST occurrence carrying a given tier number as that tier's boundary).
HIGH_OCC = [
    {"value": 200, "tier": 1},
    {"value": 190, "tier": 1},
    {"value": 50, "tier": 2},
    {"value": 40, "tier": 2},
]
LOW_OCC = [
    {"value": -200, "tier": 1},
    {"value": -190, "tier": 1},
    {"value": -50, "tier": 2},
    {"value": -40, "tier": 2},
]


class TestTierBoundaries(unittest.TestCase):
    def test_high_boundaries(self):
        # tier1's last entry is 190, tier2's last entry is 40
        self.assertEqual(tier_boundaries(HIGH_OCC), [(1, 190), (2, 40)])

    def test_low_boundaries(self):
        self.assertEqual(tier_boundaries(LOW_OCC), [(1, -190), (2, -40)])

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            tier_boundaries([])


class TestClassifyReading(unittest.TestCase):
    def setUp(self):
        self.high_bounds = tier_boundaries(HIGH_OCC)
        self.low_bounds = tier_boundaries(LOW_OCC)

    def test_high_tier1(self):
        self.assertEqual(
            classify_reading(195, self.high_bounds, self.low_bounds),
            {"side": "high", "tier": 1},
        )

    def test_high_tier2(self):
        self.assertEqual(
            classify_reading(45, self.high_bounds, self.low_bounds),
            {"side": "high", "tier": 2},
        )

    def test_neutral(self):
        self.assertEqual(
            classify_reading(0, self.high_bounds, self.low_bounds),
            {"side": None, "tier": None},
        )

    def test_low_tier1(self):
        self.assertEqual(
            classify_reading(-195, self.high_bounds, self.low_bounds),
            {"side": "low", "tier": 1},
        )

    def test_low_tier2(self):
        self.assertEqual(
            classify_reading(-45, self.high_bounds, self.low_bounds),
            {"side": "low", "tier": 2},
        )

    def test_empty_bounds_means_no_match(self):
        self.assertEqual(
            classify_reading(1000, [], []),
            {"side": None, "tier": None},
        )


class TestShouldEmit(unittest.TestCase):
    def test_first_emit_always_true(self):
        self.assertTrue(should_emit({}, ("net_delta", "2", "high"), 2, 1000, 5000))

    def test_same_tier_within_cooldown_suppressed(self):
        state = {("net_delta", "2", "high"): {"last_tier": 1, "last_emit_ms": 1000}}
        self.assertFalse(should_emit(state, ("net_delta", "2", "high"), 1, 2000, 5000))

    def test_escalation_always_emits_ignoring_cooldown(self):
        state = {("net_delta", "2", "high"): {"last_tier": 2, "last_emit_ms": 1000}}
        # tier 1 is stricter (more extreme) than the last tier 2 -> emits even
        # though only 500ms have passed (cooldown 5000)
        self.assertTrue(should_emit(state, ("net_delta", "2", "high"), 1, 1500, 5000))

    def test_same_tier_after_cooldown_rearms(self):
        state = {("net_delta", "2", "high"): {"last_tier": 1, "last_emit_ms": 2500}}
        self.assertTrue(should_emit(state, ("net_delta", "2", "high"), 1, 8000, 5000))

    def test_weaker_tier_within_cooldown_suppressed(self):
        state = {("net_delta", "2", "high"): {"last_tier": 1, "last_emit_ms": 8000}}
        self.assertFalse(should_emit(state, ("net_delta", "2", "high"), 2, 8100, 5000))

    def test_does_not_mutate_state(self):
        state = {("k",): {"last_tier": 3, "last_emit_ms": 100}}
        before = dict(state)
        should_emit(state, ("k",), 1, 9999, 10)
        self.assertEqual(state, before)


class TestMakeFlag(unittest.TestCase):
    def test_shape(self):
        flag = make_flag("net_delta", "2", "high", 1, 195, 1000)
        self.assertEqual(flag["t"], 1000)
        self.assertEqual(flag["event"], "tick_extreme")
        self.assertEqual(flag["source"], "tick")
        self.assertEqual(flag["indicator"], "net_delta")
        self.assertEqual(flag["tf"], "2")
        self.assertEqual(flag["side"], "high")
        self.assertEqual(flag["tier"], 1)
        self.assertEqual(flag["value"], 195)

    def test_extra_does_not_override_base_keys(self):
        flag = make_flag("net_delta", "2", "high", 1, 195, 1000,
                          extra={"session": "asian", "tier": 999})
        self.assertEqual(flag["session"], "asian")
        self.assertEqual(flag["tier"], 1)  # base key wins over extra


class TestReplay(unittest.TestCase):
    def test_hand_computed_sequence(self):
        # Independently worked through in 093-tick-live-flagger.md; reproduced
        # here for an isolated, from-scratch check.
        tiers_table = {
            "2": {
                "net_delta": {"high": HIGH_OCC, "low": LOW_OCC},
            }
        }
        historical = [
            {"t": 1000, "tf": "2", "indicator": "net_delta", "value": 195},
            {"t": 2000, "tf": "2", "indicator": "net_delta", "value": 193},
            {"t": 3000, "tf": "2", "indicator": "net_delta", "value": 5},
            {"t": 9000, "tf": "2", "indicator": "net_delta", "value": 45},
            {"t": 9500, "tf": "2", "indicator": "net_delta", "value": -195},
        ]
        flags = replay(historical, tiers_table, cooldown_ms=5000)
        self.assertEqual(len(flags), 3)
        self.assertEqual((flags[0]["t"], flags[0]["side"], flags[0]["tier"]), (1000, "high", 1))
        self.assertEqual((flags[1]["t"], flags[1]["side"], flags[1]["tier"]), (9000, "high", 2))
        self.assertEqual((flags[2]["t"], flags[2]["side"], flags[2]["tier"]), (9500, "low", 1))
        for f in flags:
            self.assertEqual(f["source"], "tick")

    def test_unknown_tf_indicator_pair_skipped(self):
        tiers_table = {"2": {"net_delta": {"high": HIGH_OCC, "low": LOW_OCC}}}
        historical = [{"t": 1, "tf": "5", "indicator": "volume", "value": 999}]
        self.assertEqual(replay(historical, tiers_table), [])


if __name__ == "__main__":
    unittest.main()
