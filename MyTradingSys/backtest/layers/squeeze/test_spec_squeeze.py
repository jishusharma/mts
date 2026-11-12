"""Independent spec tests for squeeze.py derived from FORMULAS.md section 31.

All expected values are hand-computed from the definitions in FORMULAS.md s31,
never read from squeeze.py.
"""
import unittest

from MyTradingSys.backtest.layers.squeeze.squeeze import squeeze_momentum


class TestSqueezeWarmupAndValidationSpec(unittest.TestCase):
    def test_empty_input(self):
        self.assertEqual(squeeze_momentum([], [], []), ([], [], []))

    def test_length_mismatch_raises(self):
        with self.assertRaises(ValueError):
            squeeze_momentum([1.0, 2.0], [1.0], [1.0, 2.0])
        with self.assertRaises(ValueError):
            squeeze_momentum([1.0], [1.0], [1.0, 2.0])

    def test_first_defined_indices_default_and_asymmetric(self):
        # FORMULAS s31.1: flags first defined at max(bb_len, kc_len) - 1;
        # momentum first defined at kc_len + mom_len - 2 (2n - 2 when equal).
        n_bars = 40
        c = [100.0 + i for i in range(n_bars)]
        h = [x + 1.0 for x in c]
        lo = [x - 1.0 for x in c]
        on, off, mom = squeeze_momentum(h, lo, c)
        self.assertEqual(len(on), n_bars)
        self.assertEqual(len(off), n_bars)
        self.assertEqual(len(mom), n_bars)
        for i in range(19):
            self.assertIsNone(on[i])
            self.assertIsNone(off[i])
        self.assertIsNotNone(on[19])
        self.assertIsNotNone(off[19])
        for i in range(38):
            self.assertIsNone(mom[i])
        self.assertIsNotNone(mom[38])

        # Asymmetric lengths: bb_len=4, kc_len=3, mom_len=5 -> flags at 3, mom at 3+5-2=6.
        on_a, off_a, mom_a = squeeze_momentum(
            h[:10], lo[:10], c[:10], bb_len=4, kc_len=3, mom_len=5
        )
        for i in range(3):
            self.assertIsNone(on_a[i])
            self.assertIsNone(off_a[i])
        self.assertIsNotNone(on_a[3])
        self.assertIsNotNone(off_a[3])
        for i in range(6):
            self.assertIsNone(mom_a[i])
        self.assertIsNotNone(mom_a[6])

    def test_input_lists_not_mutated(self):
        c = [10.0, 11.0, 12.0, 13.0, 14.0]
        h = [x + 0.5 for x in c]
        lo = [x - 0.5 for x in c]
        h0, l0, c0 = list(h), list(lo), list(c)
        squeeze_momentum(h, lo, c, bb_len=2, kc_len=2, mom_len=2)
        self.assertEqual(h, h0)
        self.assertEqual(lo, l0)
        self.assertEqual(c, c0)


class TestSqueezeBandsAndQuirkSpec(unittest.TestCase):
    def test_population_stdev_not_sample_stdev(self):
        # FORMULAS s31.1: dev uses POPULATION stdev (divisor n, not n-1).
        # C = [10, 10, 12, 12] -> mean=11, pop_sd=1.0, sample_sd=2/sqrt(3)=1.1547.
        # H = C+0.5, L = C-0.5 -> TR = [1.0, 1.0, 2.5, 1.0], SMA(TR,4) = 1.375.
        # KChw = 1.5 * 1.375 = 2.0625.
        # With textbook_bb=True, bb_mult=2.0: BBhw_pop = 2.0 < 2.0625 -> ON;
        # sample stdev would give BBhw_samp = 2.3094 > 2.0625 -> OFF.
        c = [10.0, 10.0, 12.0, 12.0]
        h = [x + 0.5 for x in c]
        lo = [x - 0.5 for x in c]
        on, off, _ = squeeze_momentum(
            h, lo, c, bb_len=4, bb_mult=2.0, kc_len=4, kc_mult=1.5, mom_len=2, textbook_bb=True
        )
        self.assertEqual((on[3], off[3]), (True, False))

    def test_script_quirk_vs_textbook_bb(self):
        # FORMULAS s31 Script quirk: default BBhw = kc_mult * sd (bb_mult ignored);
        # textbook_bb=True restores BBhw = bb_mult * sd.
        # C = [10, 10, 12, 12] -> sd = 1.0.
        # H = C+0.4, L = C-0.4 -> TR = [0.8, 0.8, 2.4, 0.8], SMA(TR,4) = 1.2, KChw = 1.8.
        # Default (kc_mult=1.5): BBhw = 1.5 < 1.8 -> ON (even if bb_mult=3.0).
        # textbook_bb=True, bb_mult=2.0: BBhw = 2.0 > 1.8 -> OFF.
        c = [10.0, 10.0, 12.0, 12.0]
        h = [x + 0.4 for x in c]
        lo = [x - 0.4 for x in c]
        on_def, off_def, _ = squeeze_momentum(h, lo, c, bb_len=4, kc_len=4, mom_len=2)
        self.assertEqual((on_def[3], off_def[3]), (True, False))

        on_ign, off_ign, _ = squeeze_momentum(
            h, lo, c, bb_len=4, bb_mult=3.0, kc_len=4, mom_len=2, textbook_bb=False
        )
        self.assertEqual((on_ign[3], off_ign[3]), (True, False))

        on_tb, off_tb, _ = squeeze_momentum(
            h, lo, c, bb_len=4, bb_mult=2.0, kc_len=4, mom_len=2, textbook_bb=True
        )
        self.assertEqual((on_tb[3], off_tb[3]), (False, True))

    def test_true_range_gap_down_dominates(self):
        # FORMULAS s31.1: TR_0 = H_0 - L_0; TR_i = max(H_i-L_i, |H_i-C_{i-1}|, |L_i-C_{i-1}|).
        # Bar 0: C=20, H=20.5, L=19.5 -> TR_0 = 1.0.
        # Bar 1: C=14, H=14.5, L=13.5 -> H-L=1.0, |H-C0|=5.5, |L-C0|=6.5 -> TR_1 = 6.5.
        # SMA(TR,2) = 3.75 -> KChw = 1.5 * 3.75 = 5.625.
        # C=[20,14] -> sd=3.0. With textbook_bb=True, bb_mult=1.7: BBhw = 5.1 < 5.625 -> ON.
        # (If |L-C0| were omitted, TR_1=5.5 -> KChw=4.875 < 5.1 -> OFF.)
        c = [20.0, 14.0]
        h = [20.5, 14.5]
        lo = [19.5, 13.5]
        on, off, _ = squeeze_momentum(
            h, lo, c, bb_len=2, bb_mult=1.7, kc_len=2, kc_mult=1.5, mom_len=2, textbook_bb=True
        )
        self.assertEqual((on[1], off[1]), (True, False))

    def test_tie_tolerance_1e_9(self):
        # FORMULAS s31.1: equal -> neither; ties within 1e-9 relative count as equal.
        # C = [10, 13] -> sd = 1.5. With textbook_bb=True, bb_mult=2.0: BBhw = 3.0.
        # H = [11.5, 13.0], L = [8.5, 10.0] -> TR_0 = 3.0, TR_1 = max(3.0, 3.0, 0.0) = 3.0.
        # With kc_mult=1.0: KChw = 1.0 * 3.0 = 3.0 (exact tie -> neither).
        c = [10.0, 13.0]
        on, off, _ = squeeze_momentum(
            [11.5, 13.0], [8.5, 10.0], c,
            bb_len=2, bb_mult=2.0, kc_len=2, kc_mult=1.0, mom_len=2, textbook_bb=True,
        )
        self.assertEqual((on[1], off[1]), (False, False))

        # Within 1e-9 relative: KChw = 3.0 * (1 + 1e-11) -> still neither.
        on_w, off_w, _ = squeeze_momentum(
            [11.5 + 6e-11, 13.0], [8.5, 10.0], c,
            bb_len=2, bb_mult=2.0, kc_len=2, kc_mult=1.0, mom_len=2, textbook_bb=True,
        )
        self.assertEqual((on_w[1], off_w[1]), (False, False))

        # Outside 1e-9 relative: KChw = 3.0 * (1 + 1e-6) -> ON; (1 - 1e-6) -> OFF.
        on_hi, off_hi, _ = squeeze_momentum(
            [11.5 + 6e-6, 13.0], [8.5, 10.0], c,
            bb_len=2, bb_mult=2.0, kc_len=2, kc_mult=1.0, mom_len=2, textbook_bb=True,
        )
        self.assertEqual((on_hi[1], off_hi[1]), (True, False))

        on_lo, off_lo, _ = squeeze_momentum(
            [11.5 - 6e-6, 13.0], [8.5, 10.0], c,
            bb_len=2, bb_mult=2.0, kc_len=2, kc_mult=1.0, mom_len=2, textbook_bb=True,
        )
        self.assertEqual((on_lo[1], off_lo[1]), (False, True))


class TestSqueezeMomentumSpec(unittest.TestCase):
    def test_constant_src_linear_trend(self):
        # FORMULAS s31.1: C_i = 10+i, H_i = C_i+1, L_i = C_i-1, kc_len=3, mom_len=3.
        # At i>=2: HH=C_i+1, LL=C_i-3, mid=C_i-1, SMA=C_i-1 -> src_i = +1.0 -> mom_i = +1.0.
        c = [10.0 + i for i in range(7)]
        h = [x + 1.0 for x in c]
        lo = [x - 1.0 for x in c]
        _, _, mom = squeeze_momentum(h, lo, c, bb_len=3, kc_len=3, mom_len=3)
        for i in range(4):
            self.assertIsNone(mom[i])
        for i in range(4, 7):
            self.assertAlmostEqual(mom[i], 1.0, places=12)

    def test_ols_endpoint_on_non_linear_src(self):
        # Hand-computed OLS endpoint for kc_len=2, mom_len=3:
        # bar 0: C=10, H=10, L=10
        # bar 1: C=10, H=10, L=10 -> HH=10, LL=10, mid=10, SMA=10 -> src_1 = 0
        # bar 2: C=12, H=12, L=10 -> HH=12, LL=10, mid=11, SMA=11 -> src_2 = 1
        # bar 3: C=16, H=16, L=12 -> HH=16, LL=10, mid=13, SMA=14 -> avg=13.5 -> src_3 = 2.5
        # y=[0, 1, 2.5]: ym = 7/6, slope = 2.5/2 = 5/4, endpoint(x=2) = 7/6 + 5/4 = 29/12.
        h = [10.0, 10.0, 12.0, 16.0]
        lo = [10.0, 10.0, 10.0, 12.0]
        c = [10.0, 10.0, 12.0, 16.0]
        _, _, mom = squeeze_momentum(h, lo, c, bb_len=2, kc_len=2, mom_len=3)
        self.assertIsNone(mom[0])
        self.assertIsNone(mom[1])
        self.assertIsNone(mom[2])
        self.assertAlmostEqual(mom[3], 29.0 / 12.0, places=12)

    def test_mom_len_one_returns_src(self):
        # Degenerate mom_len=1: OLS through 1 point returns src_i without ZeroDivisionError.
        h = [10.0, 12.0, 14.0]
        lo = [10.0, 10.0, 12.0]
        c = [10.0, 12.0, 14.0]
        # bar 1: HH=12, LL=10, mid=11, SMA=11 -> src_1 = 12 - 11 = 1.0
        # bar 2: HH=14, LL=10, mid=12, SMA=13 -> avg=12.5 -> src_2 = 14 - 12.5 = 1.5
        _, _, mom = squeeze_momentum(h, lo, c, bb_len=2, kc_len=2, mom_len=1)
        self.assertIsNone(mom[0])
        self.assertAlmostEqual(mom[1], 1.0, places=12)
        self.assertAlmostEqual(mom[2], 1.5, places=12)


if __name__ == "__main__":
    unittest.main()
