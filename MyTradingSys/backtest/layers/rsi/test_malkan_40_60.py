import json
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.rsi.malkan_40_60 import (
    malkan_regime, malkan_setup_bull, malkan_setup_bear,
)

DEFAULT_PARAMS = json.loads((Path(__file__).parent / "params" / "default.json").read_text())
MALKAN_PARAMS = json.loads((Path(__file__).parent / "params" / "malkan_40_60_default.json").read_text())


def _filler_bars(n):
    return [{"t": i, "o": 50, "c": 50} for i in range(n)]


class TestMalkanRegime(unittest.TestCase):
    """layers/rsi/TEST_PLAN.md malkan_40_60.py Case D1/D2."""

    def test_d1_regime_lo40_hi60_lookback3(self):
        rsi = [None, None, 65, 62, 58, 42, 38, 45, 55, 63]
        got = malkan_regime(rsi, lo=40, hi=60, lookback=3)
        expected = [None, None, None, None, "BULL", "BULL", "BEAR", "BEAR", "BEAR", "BULL"]
        self.assertEqual(got, expected)

    def test_d2_invalid_thresholds_and_lookback_raise(self):
        rsi = [50, 60, 70]
        with self.assertRaises(ValueError):
            malkan_regime(rsi, lo=60, hi=40)
        with self.assertRaises(ValueError):
            malkan_regime(rsi, lookback=0)


class TestMalkanSetupBull(unittest.TestCase):
    """Case D3/D4/D5 (MLK-S1)."""

    def _rsi(self):
        # idx0..10 held far above the 40/2 band (no spurious events); idx11 above, idx12 dips
        # into the band from above, idx13 exits back above -> a "support" event at t=13.
        rsi = [70.0] * 11 + [44, 39, 43]
        return rsi

    def test_d3_bull_setup_fires(self):
        rsi = self._rsi()
        bars = _filler_bars(14)
        bars[13] = {"t": 13, "o": 100, "c": 103}
        regime = [None] * 14
        regime[13] = "BULL"
        got = malkan_setup_bull(bars, rsi, regime, level=40, tolerance=2)
        self.assertEqual(got, [{
            "t": 13, "side": "long", "rule_id": "MLK-S1", "event": "support",
            "level_value": 40, "regime": "BULL",
        }])

    def test_d4_skipped_regime_not_bull(self):
        rsi = self._rsi()
        bars = _filler_bars(14)
        bars[13] = {"t": 13, "o": 100, "c": 103}
        regime = [None] * 14
        regime[13] = "RANGE"
        got = malkan_setup_bull(bars, rsi, regime, level=40, tolerance=2)
        self.assertEqual(got, [])

    def test_d5_skipped_bearish_entry_candle(self):
        rsi = self._rsi()
        bars = _filler_bars(14)
        bars[13] = {"t": 13, "o": 103, "c": 100}  # bearish candle
        regime = [None] * 14
        regime[13] = "BULL"
        got = malkan_setup_bull(bars, rsi, regime, level=40, tolerance=2)
        self.assertEqual(got, [])


class TestMalkanSetupBear(unittest.TestCase):
    """Case D6 (MLK-S2)."""

    def test_d6_bear_setup_fires(self):
        rsi = [30.0] * 19 + [57, 61, 56]  # idx19 below, idx20 band, idx21 exits below -> rejection@21
        bars = _filler_bars(22)
        bars[21] = {"t": 21, "o": 50, "c": 47}  # bearish candle
        regime = [None] * 22
        regime[21] = "BEAR"
        got = malkan_setup_bear(bars, rsi, regime, level=60, tolerance=2)
        self.assertEqual(got, [{
            "t": 21, "side": "short", "rule_id": "MLK-S2", "event": "rejection",
            "level_value": 60, "regime": "BEAR",
        }])


class TestMalkanIsolation(unittest.TestCase):
    """Case D7: 40/60 live ONLY in malkan_40_60_default.json."""

    def test_d7_malkan_default_has_40_and_60(self):
        self.assertEqual(MALKAN_PARAMS["malkan_40_60"]["lo"], 40)
        self.assertEqual(MALKAN_PARAMS["malkan_40_60"]["hi"], 60)

    def test_c4_cross_reference_other_params_file_has_no_40_60(self):
        def walk(node):
            if isinstance(node, dict):
                for v in node.values():
                    yield from walk(v)
            elif isinstance(node, (int, float)) and not isinstance(node, bool):
                yield node

        for leaf in walk(DEFAULT_PARAMS["rsi_core"]):
            self.assertNotIn(leaf, (40, 60))
        for leaf in walk(DEFAULT_PARAMS["rsi_ma"]):
            self.assertNotIn(leaf, (40, 60))


if __name__ == "__main__":
    unittest.main()
