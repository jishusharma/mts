import unittest

from MyTradingSys.backtest.layers.rsi.malkan_mtf import state_asof, malkan_mtf_bull, malkan_mtf_bear


def _filler_bars(n):
    return [{"t": i, "o": 50, "c": 50} for i in range(n)]


class TestStateAsof(unittest.TestCase):
    def test_empty_times_returns_none(self):
        self.assertIsNone(state_asof([], [], 5))

    def test_all_entries_after_t_returns_none(self):
        self.assertIsNone(state_asof([10, 20], ["BULL", "BEAR"], 5))

    def test_returns_latest_entry_at_or_before_t(self):
        self.assertEqual(state_asof([0, 10, 20], ["RANGE", "BULL", "BULL"], 13), "BULL")
        self.assertEqual(state_asof([0, 10, 20], ["RANGE", "BULL", "BULL"], 10), "BULL")
        self.assertEqual(state_asof([0, 10, 20], ["RANGE", "BULL", "BULL"], 9), "RANGE")

    def test_mismatched_lengths_raise(self):
        with self.assertRaises(ValueError):
            state_asof([0, 10], ["BULL"], 5)


class TestMalkanMtfBull(unittest.TestCase):
    """Spec 079-malkan-mtf.md hand-computed check, reusing TEST_PLAN.md Case D3."""

    def _base_args(self):
        rsi = [70.0] * 11 + [44, 39, 43]
        bars = _filler_bars(14)
        bars[13] = {"t": 13, "o": 100, "c": 103}
        regime = [None] * 14
        regime[13] = "BULL"
        return bars, rsi, regime

    def test_kept_when_weekly_and_monthly_both_bull(self):
        bars, rsi, regime = self._base_args()
        got = malkan_mtf_bull(
            bars, rsi, regime,
            weekly_times=[0, 10, 20], weekly_regime=["RANGE", "BULL", "BULL"],
            monthly_times=[0], monthly_regime=["BULL"],
            level=40, tolerance=2,
        )
        self.assertEqual(len(got), 1)
        sig = got[0]
        self.assertEqual(sig["t"], 13)
        self.assertEqual(sig["side"], "long")
        self.assertEqual(sig["rule_id"], "MLK-S1-MTF")
        self.assertEqual(sig["event"], "support")
        self.assertEqual(sig["regime"], "BULL")
        self.assertEqual(sig["weekly_regime"], "BULL")
        self.assertEqual(sig["monthly_regime"], "BULL")

    def test_dropped_when_monthly_gate_fails(self):
        bars, rsi, regime = self._base_args()
        got = malkan_mtf_bull(
            bars, rsi, regime,
            weekly_times=[0, 10, 20], weekly_regime=["RANGE", "BULL", "BULL"],
            monthly_times=[0], monthly_regime=["RANGE"],
            level=40, tolerance=2,
        )
        self.assertEqual(got, [])


class TestMalkanMtfBear(unittest.TestCase):
    """Mirror check using TEST_PLAN.md Case D6."""

    def _base_args(self):
        rsi = [30.0] * 19 + [57, 61, 56]
        bars = _filler_bars(22)
        bars[21] = {"t": 21, "o": 50, "c": 47}
        regime = [None] * 22
        regime[21] = "BEAR"
        return bars, rsi, regime

    def test_kept_when_weekly_and_monthly_both_bear(self):
        bars, rsi, regime = self._base_args()
        got = malkan_mtf_bear(
            bars, rsi, regime,
            weekly_times=[0, 10, 20], weekly_regime=["RANGE", "BEAR", "BEAR"],
            monthly_times=[0], monthly_regime=["BEAR"],
            level=60, tolerance=2,
        )
        self.assertEqual(len(got), 1)
        sig = got[0]
        self.assertEqual(sig["t"], 21)
        self.assertEqual(sig["side"], "short")
        self.assertEqual(sig["rule_id"], "MLK-S2-MTF")
        self.assertEqual(sig["weekly_regime"], "BEAR")
        self.assertEqual(sig["monthly_regime"], "BEAR")

    def test_dropped_when_weekly_gate_fails(self):
        bars, rsi, regime = self._base_args()
        got = malkan_mtf_bear(
            bars, rsi, regime,
            weekly_times=[0, 10, 20], weekly_regime=["RANGE", "RANGE", "RANGE"],
            monthly_times=[0], monthly_regime=["BEAR"],
            level=60, tolerance=2,
        )
        self.assertEqual(got, [])


if __name__ == "__main__":
    unittest.main()
