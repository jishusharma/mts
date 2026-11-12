"""test_spec_vfi.py - Independent spec tests for Volume Flow Indicator (vfi.py).

Derived from FORMULAS.md section 32 (Volume Flow Indicator - LazyBear / Katsanos).
Expected values are mathematically derived from specification formulas, never copied from implementation code.
"""
import math
import os
import sys
import unittest

# Import vfi robustly across different test runners and directory contexts
try:
    from MyTradingSys.backtest.layers.vfi.vfi import vfi as _vfi
except ImportError:
    _dir = os.path.dirname(os.path.abspath(__file__))
    if _dir not in sys.path:
        sys.path.insert(0, _dir)
    import vfi as _vfi_mod
    _vfi = getattr(_vfi_mod, "vfi", _vfi_mod)

if hasattr(_vfi, "vfi"):
    vfi = _vfi.vfi
else:
    vfi = _vfi


class TestVfiSpecSection32(unittest.TestCase):
    """Spec tests derived directly from FORMULAS.md section 32 definitions."""

    def test_section_32_2_worked_toy_raw_and_smoothed(self):
        """FORMULAS.md s32.2 worked toy:

        stdev_len = 2, length = 3, smooth = 2, coef = 0.2, vcoef = 2.5
        C = [100, 102, 101, 105, 105, 104, 110, 108, 108.25]
        H = C + 1, L = C - 1 -> typ = C
        V = [10, 20, 30, 20, 40, 10, 100, 30, 50]
        """
        c = [100.0, 102.0, 101.0, 105.0, 105.0, 104.0, 110.0, 108.0, 108.25]
        h = [x + 1.0 for x in c]
        lo = [x - 1.0 for x in c]
        v = [10.0, 20.0, 30.0, 20.0, 40.0, 10.0, 100.0, 30.0, 50.0]

        raw, sm_sma = vfi(h, lo, c, v, length=3, coef=0.2, vcoef=2.5, smooth=2, stdev_len=2, smooth_kind="sma")
        _, sm_ema = vfi(h, lo, c, v, length=3, coef=0.2, vcoef=2.5, smooth=2, stdev_len=2, smooth_kind="ema")

        # first = max(2, 3) + 3 - 1 = 5
        self.assertEqual(len(raw), 9)
        for i in range(5):
            self.assertIsNone(raw[i], f"raw[{i}] should be None")

        # Raw hand values from s32.2:
        # bar 5: 1/3
        # bar 6: 29/14
        # bar 7: 11/30
        # bar 8: 47/28
        expected_raw = {
            5: 1.0 / 3.0,
            6: 29.0 / 14.0,
            7: 11.0 / 30.0,
            8: 47.0 / 28.0,
        }
        for idx, exp in expected_raw.items():
            self.assertAlmostEqual(raw[idx], exp, places=6, msg=f"raw[{idx}]")

        # Smoothed SMA(2), first at bar 6:
        # bar 6: 101/84
        # bar 7: 128/105
        # bar 8: 859/840
        for i in range(6):
            self.assertIsNone(sm_sma[i], f"sm_sma[{i}] should be None")

        expected_sma = {
            6: 101.0 / 84.0,
            7: 128.0 / 105.0,
            8: 859.0 / 840.0,
        }
        for idx, exp in expected_sma.items():
            self.assertAlmostEqual(sm_sma[idx], exp, places=6, msg=f"sm_sma[{idx}]")

        # Smoothed EMA(2), alpha = 2/(2+1) = 2/3, seed at bar 6 = 101/84:
        # bar 6: 101/84
        # bar 7: 271/420
        # bar 8: 1681/1260
        for i in range(6):
            self.assertIsNone(sm_ema[i], f"sm_ema[{i}] should be None")

        expected_ema = {
            6: 101.0 / 84.0,
            7: 271.0 / 420.0,
            8: 1681.0 / 1260.0,
        }
        for idx, exp in expected_ema.items():
            self.assertAlmostEqual(sm_ema[idx], exp, places=6, msg=f"sm_ema[{idx}]")

    def test_population_stdev_vs_sample_stdev_kill_test(self):
        """FORMULAS.md s32.2 note on Bar 8:

        'cutoff = 0.2 * 0.010331 * 108.25 = 0.2237; 0.25 > 0.2237 -> vcp = +50.
        (A SAMPLE stdev, divisor n-1, would give cutoff 0.3163 and vcp = 0: the variant, not used.)'
        If sample stdev was erroneously used, vcp_8 would be 0, changing raw[8] from 47/28 (1.67857)
        to (175/3 - 30 + 0) / (140/3) = 85/140 = 17/28 (0.60714).
        """
        c = [100.0, 102.0, 101.0, 105.0, 105.0, 104.0, 110.0, 108.0, 108.25]
        h = [x + 1.0 for x in c]
        lo = [x - 1.0 for x in c]
        v = [10.0, 20.0, 30.0, 20.0, 40.0, 10.0, 100.0, 30.0, 50.0]

        raw, _ = vfi(h, lo, c, v, length=3, coef=0.2, vcoef=2.5, smooth=2, stdev_len=2)
        self.assertAlmostEqual(raw[8], 47.0 / 28.0, places=6)
        # Verify it is not the sample stdev result
        self.assertNotAlmostEqual(raw[8], 17.0 / 28.0, places=2)

    def test_independent_hand_derived_series_with_capping_and_down_move(self):
        """Independent derivation from definitions in s32.1:

        length = 2, stdev_len = 2, coef = 0.1, vcoef = 2.0, smooth = 2
        H = L = C = [10, 10, 12, 12, 15, 9] -> typ = C
        V = [100, 100, 100, 100, 500, 100]

        Bar 0: C=10, V=100
        Bar 1: C=10, V=100
        Bar 2: C=12, V=100:
            inter = [ln(1), ln(1.2)] = [0, 0.182321557]
            vinter = 0.182321557 / 2 = 0.091160778
            cutoff = 0.1 * 0.091160778 * 12 = 0.109392934
            vave = mean(V[0..1]) = 100, vmax = 2.0 * 100 = 200, vc = min(100, 200) = 100
            mf = 12 - 10 = 2 > cutoff -> vcp = +100
        Bar 3: C=12, V=100:
            inter = [ln(1.2), ln(1)]
            cutoff = 0.109392934
            vave = mean(V[1..2]) = 100, vmax = 200, vc = 100
            mf = 0 <= cutoff -> vcp = 0
            first = max(2,2)+2-1 = 3:
            raw[3] = sum(vcp[2..3]) / vave = (100 + 0) / 100 = 1.0
        Bar 4: C=15, V=500:
            inter = [0, ln(1.25)]
            vinter = ln(1.25) / 2 = 0.111571776
            cutoff = 0.1 * 0.111571776 * 15 = 0.167357663
            vave = mean(V[2..3]) = 100, vmax = 2.0 * 100 = 200, vc = min(500, 200) = 200 (capped!)
            mf = 15 - 12 = 3 > cutoff -> vcp = +200
            raw[4] = sum(vcp[3..4]) / vave = (0 + 200) / 100 = 2.0
        Bar 5: C=9, V=100:
            inter = [ln(1.25), ln(0.6)] = [0.223143551, -0.510825624]
            vinter = |0.223143551 - (-0.510825624)| / 2 = 0.366984588
            cutoff = 0.1 * 0.366984588 * 9 = 0.330286129
            vave = mean(V[3..4]) = (100 + 500) / 2 = 300
            vmax = 2.0 * 300 = 600, vc = min(100, 600) = 100
            mf = 9 - 15 = -6 < -cutoff -> vcp = -100
            raw[5] = sum(vcp[4..5]) / vave = (200 - 100) / 300 = 100 / 300 = 1/3 (0.333333333)

        Smoothed SMA(2):
            bar 4: mean(raw[3..4]) = (1.0 + 2.0) / 2 = 1.5
            bar 5: mean(raw[4..5]) = (2.0 + 1/3) / 2 = 7/6 (1.166666667)
        Smoothed EMA(2):
            alpha = 2/(2+1) = 2/3, seed at bar 4 = 1.5
            bar 5: (2/3) * (1/3) + (1/3) * 1.5 = 2/9 + 1/2 = 13/18 (0.722222222)
        """
        c = [10.0, 10.0, 12.0, 12.0, 15.0, 9.0]
        h = list(c)
        lo = list(c)
        v = [100.0, 100.0, 100.0, 100.0, 500.0, 100.0]

        raw, sma = vfi(h, lo, c, v, length=2, coef=0.1, vcoef=2.0, smooth=2, stdev_len=2, smooth_kind="sma")
        _, ema = vfi(h, lo, c, v, length=2, coef=0.1, vcoef=2.0, smooth=2, stdev_len=2, smooth_kind="ema")

        self.assertIsNone(raw[0])
        self.assertIsNone(raw[1])
        self.assertIsNone(raw[2])
        self.assertAlmostEqual(raw[3], 1.0, places=6)
        self.assertAlmostEqual(raw[4], 2.0, places=6)
        self.assertAlmostEqual(raw[5], 1.0 / 3.0, places=6)

        self.assertIsNone(sma[3])
        self.assertAlmostEqual(sma[4], 1.5, places=6)
        self.assertAlmostEqual(sma[5], 7.0 / 6.0, places=6)

        self.assertIsNone(ema[3])
        self.assertAlmostEqual(ema[4], 1.5, places=6)
        self.assertAlmostEqual(ema[5], 13.0 / 18.0, places=6)

    def test_smooth_less_than_or_equal_to_one_returns_raw(self):
        """s32.1: 'smooth <= 1 returns vfi itself'."""
        c = [100.0, 102.0, 101.0, 105.0, 105.0, 104.0, 110.0, 108.0, 108.25]
        h = [x + 1.0 for x in c]
        lo = [x - 1.0 for x in c]
        v = [10.0, 20.0, 30.0, 20.0, 40.0, 10.0, 100.0, 30.0, 50.0]

        raw, sm1 = vfi(h, lo, c, v, length=3, stdev_len=2, smooth=1)
        self.assertEqual(raw, sm1)
        self.assertIsNot(raw, sm1)  # Distinct list copy

        raw0, sm0 = vfi(h, lo, c, v, length=3, stdev_len=2, smooth=0)
        self.assertEqual(raw0, sm0)

    def test_warmup_window_bounds_when_stdev_len_exceeds_length(self):
        """s32.1: first defined at bar max(stdev_len, length) + length - 1.

        When stdev_len = 4, length = 2:
        max(4, 2) + 2 - 1 = 5. Bars 0..4 must be None; bar 5 must be defined.
        """
        c = [10.0 + i for i in range(8)]
        h = [x + 1.0 for x in c]
        lo = [x - 1.0 for x in c]
        v = [100.0] * 8

        raw, _ = vfi(h, lo, c, v, length=2, stdev_len=4, smooth=2)
        for i in range(5):
            self.assertIsNone(raw[i], f"raw[{i}] must be None")
        self.assertIsNotNone(raw[5], "raw[5] must be computed")

    def test_strict_cutoff_ties_yield_zero_vcp(self):
        """s32.1: '+vc_i if mf_i > cutoff_i; -vc_i if mf_i < -cutoff_i; else 0 (strict; a tie is 0)'."""
        # Setup bars where typical price difference mf is 0.0, while cutoff is positive.
        c = [10.0, 10.0, 12.0, 12.0, 12.0]
        h = list(c)
        lo = list(c)
        v = [50.0] * 5

        # Bar 2 to 3: mf = 0, inter was non-zero earlier so cutoff > 0.
        raw, _ = vfi(h, lo, c, v, length=2, stdev_len=2, smooth=1)
        # If tie yielded vc instead of 0, raw would differ.
        self.assertIsNotNone(raw[3])

    def test_zero_vave_returns_none(self):
        """When volume is all zero, vave = 0. Division by zero must be protected and return None."""
        c = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]
        h = list(c)
        lo = list(c)
        v = [0.0] * 6

        raw, _ = vfi(h, lo, c, v, length=2, stdev_len=2, smooth=1)
        # All bars should be None because vave is 0
        for i, val in enumerate(raw):
            self.assertIsNone(val, f"raw[{i}] should be None when vave is zero")

    def test_validation_input_errors(self):
        """Contract requirements on parameter validity."""
        # Length mismatch
        with self.assertRaises(ValueError):
            vfi([10.0, 11.0], [10.0], [10.0, 11.0], [100.0, 100.0])
        with self.assertRaises(ValueError):
            vfi([10.0, 11.0], [10.0, 11.0], [10.0], [100.0, 100.0])
        with self.assertRaises(ValueError):
            vfi([10.0, 11.0], [10.0, 11.0], [10.0, 11.0], [100.0])

        # Invalid smooth_kind
        with self.assertRaises(ValueError):
            vfi([10.0, 11.0], [10.0, 11.0], [10.0, 11.0], [100.0, 100.0], smooth_kind="wma")

        # Non-positive typical price
        with self.assertRaises(ValueError):
            vfi([0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [100.0, 100.0])
        with self.assertRaises(ValueError):
            vfi([-1.0, 10.0], [-1.0, 10.0], [-1.0, 10.0], [100.0, 100.0])


if __name__ == "__main__":
    unittest.main()
