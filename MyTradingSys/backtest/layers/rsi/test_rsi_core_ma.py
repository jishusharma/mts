import json
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core
from MyTradingSys.backtest.layers.rsi.rsi_ma import rsi_ma

PARAMS = json.loads((Path(__file__).parent / "params" / "default.json").read_text())


class TestRsiCore(unittest.TestCase):
    """layers/rsi/TEST_PLAN.md rsi_core.py section."""

    def test_c1_wilder_rsi_period_5(self):
        closes = [100, 102, 101, 103, 106, 105, 107, 110, 108, 112, 111, 113, 116, 114, 118]
        expected = {
            5: 77.777778, 6: 82.608696, 7: 87.644788, 8: 70.606532, 9: 80.21978,
            10: 72.781223, 11: 77.903574, 12: 83.666874, 13: 68.728457, 14: 78.379232,
        }
        got = rsi_core(closes, period=5)
        for i in range(5):
            self.assertIsNone(got[i])
        for i, exp in expected.items():
            self.assertAlmostEqual(got[i], exp, delta=1e-4)

    def test_c2_invalid_params_raise(self):
        closes = list(range(15))
        with self.assertRaises(ValueError):
            rsi_core(closes, period=0)
        with self.assertRaises(ValueError):
            rsi_core(closes, period=20)

    def test_c3_default_period_is_14(self):
        self.assertEqual(PARAMS["rsi_core"]["period"], 14)

    def test_c4_isolation_no_40_or_60_in_default_params(self):
        def walk(node):
            if isinstance(node, dict):
                for v in node.values():
                    yield from walk(v)
            elif isinstance(node, (int, float)) and not isinstance(node, bool):
                yield node

        for leaf in walk(PARAMS["rsi_core"]):
            self.assertNotIn(leaf, (40, 60))
        for leaf in walk(PARAMS["rsi_ma"]):
            self.assertNotIn(leaf, (40, 60))
        self.assertEqual(PARAMS["rsi_events"]["levels"], [70, 50, 30])


class TestRsiMa(unittest.TestCase):
    """layers/rsi/TEST_PLAN.md rsi_ma.py section."""

    RSI = [None, None, None, 50.0, 55.0, 45.0, 60.0, 40.0]

    def test_m1_sma3(self):
        got = rsi_ma(self.RSI, type="SMA", length=3)
        self.assertEqual(got[:5], [None] * 5)
        self.assertAlmostEqual(got[5], 50.0, delta=1e-4)
        self.assertAlmostEqual(got[6], 53.333333, delta=1e-4)
        self.assertAlmostEqual(got[7], 48.333333, delta=1e-4)

    def test_m2_wma3(self):
        got = rsi_ma(self.RSI, type="WMA", length=3)
        self.assertAlmostEqual(got[5], 49.166667, delta=1e-4)
        self.assertAlmostEqual(got[6], 54.166667, delta=1e-4)
        self.assertAlmostEqual(got[7], 47.5, delta=1e-4)

    def test_m3_ema3(self):
        got = rsi_ma(self.RSI, type="EMA", length=3)
        self.assertAlmostEqual(got[5], 50.0, delta=1e-4)
        self.assertAlmostEqual(got[6], 55.0, delta=1e-4)
        self.assertAlmostEqual(got[7], 47.5, delta=1e-4)

    def test_m4_rma3(self):
        got = rsi_ma(self.RSI, type="RMA", length=3)
        self.assertAlmostEqual(got[5], 50.0, delta=1e-4)
        self.assertAlmostEqual(got[6], 53.333333, delta=1e-4)
        self.assertAlmostEqual(got[7], 48.888889, delta=1e-4)

    def test_m5_default_type_length_from_params(self):
        self.assertEqual(PARAMS["rsi_ma"], {"type": "SMA", "length": 14})

    def test_m6_invalid_type_raises(self):
        with self.assertRaises(ValueError):
            rsi_ma(self.RSI, type="XMA", length=3)


if __name__ == "__main__":
    unittest.main()
