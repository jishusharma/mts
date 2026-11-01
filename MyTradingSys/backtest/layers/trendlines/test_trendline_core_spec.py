"""
Spec-derived kill tests for trendline_core.py survivors of the mutation audit
(research/layer_lab/reports/2026-11-01_gpt-mutation-trendline-core-1031.md).
Expected values come from layers/FORMULAS.md section 12 (ATR worked example), 19.5 (strict penetration test
L6) and the close-location definition (c-l)/(h-l); never from the module.
"""
import unittest

from MyTradingSys.backtest.layers.trendlines import trendline_core as tc


def _detector_with(bars, side, ia, pa, ib, pb, atr_b):
    d = tc.TrendlineDetector(transform="linear")
    d.bars = bars
    ln = {"side": side, "ia": ia, "pa": pa, "ib": ib, "pb": pb, "atr_b": atr_b}
    return d, ln


class TestSpecSurvivors(unittest.TestCase):
    def test_atr_section12_worked_example_uses_gap_term(self):
        # FORMULAS s12: TR[3] = max(2, 0.5, 2.5) = 2.5 (the |low - prev close| arm); ATR(3) = 6.5/3 = 2.1667
        h = [10, 11, 12, 11]
        lo = [9, 9, 10, 9]
        c = [9.5, 10.5, 11.5, 10]
        bars = [{"h": h[i], "l": lo[i], "c": c[i], "o": c[i]} for i in range(4)]
        self.assertAlmostEqual(tc.true_range(bars, 3), 2.5, places=9)
        self.assertAlmostEqual(tc.atr_sma(bars, 3, 3), 6.5 / 3, places=9)

    def test_close_location_is_close_minus_low_over_range(self):
        # (c - l)/(h - l): h=110 l=100 c=104 -> 0.4; close at the high -> 1, at the low -> 0
        self.assertAlmostEqual(tc._close_loc({"h": 110, "l": 100, "c": 104, "o": 105}), 0.4, places=12)
        self.assertEqual(tc._close_loc({"h": 110, "l": 100, "c": 110, "o": 105}), 1.0)
        self.assertEqual(tc._close_loc({"h": 110, "l": 100, "c": 100, "o": 105}), 0.0)

    def test_penetration_support_boundary_low_equals_line_minus_tol_passes(self):
        # FORMULAS 19.5 L6: passes iff low >= L - 0.10*ATR_b. ATR_b = 8 -> tol 0.8; L(1) = 102.
        tol = 0.10 * 8
        bars = [{"l": 100, "c": 100, "h": 110, "o": 100},
                {"l": 102 - tol, "c": 102, "h": 110, "o": 102},
                {"l": 104, "c": 104, "h": 110, "o": 104}]
        d, ln = _detector_with(bars, "support", 0, 100, 2, 104, 8)
        self.assertTrue(d._penetration_ok(ln))
        bars[1]["l"] = 102 - tol - 0.01
        self.assertFalse(d._penetration_ok(ln))

    def test_penetration_resistance_boundary_high_equals_line_plus_tol_passes(self):
        # mirror: passes iff high <= L + 0.10*ATR_b. Line falls 100 -> 96, L(1) = 98.
        tol = 0.10 * 8
        bars = [{"h": 100, "c": 100, "l": 90, "o": 100},
                {"h": 98 + tol, "c": 98, "l": 90, "o": 98},
                {"h": 96, "c": 96, "l": 90, "o": 96}]
        d, ln = _detector_with(bars, "resistance", 0, 100, 2, 96, 8)
        self.assertTrue(d._penetration_ok(ln))
        bars[1]["h"] = 98 + tol + 0.01
        self.assertFalse(d._penetration_ok(ln))


if __name__ == "__main__":
    unittest.main()
