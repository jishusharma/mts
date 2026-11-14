"""Tests for M2 mapping. Run: python -I test_study.py (from this folder)."""
import os, sys, unittest
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import study  # noqa
import maker_fill as mf  # noqa

MIN = 60000
T0 = 1_700_000_000_000 - (1_700_000_000_000 % 3600000)
TICK = 0.01


def m1(bars, t0=T0):
    a = np.array(bars, float)
    return dict(t_ms=t0 + MIN * np.arange(len(a), dtype=float), o=a[:, 0], h=a[:, 1], l=a[:, 2], c=a[:, 3])


def flat(n, px):
    return [(px, px + 0.02, px - 0.02, px)] * n


# short fakeout fade: up-break at H=100, fakeout candle high 100.8, fade SHORT limit sell at 100 (above close ~99.5)
SIG = dict(dir=-1, lvl=100.0, atr=0.5)


class MapAndFill(unittest.TestCase):
    def test_params_use_broken_level(self):
        side, L, stop, tgt, dist = study.maker_params(SIG, 100.8, 99.0)
        self.assertEqual(L, 100.0)
        self.assertAlmostEqual(dist, max(0.8, 0.3, 0.5))     # nat = breakout high - L = 0.8
        self.assertAlmostEqual(stop, 100.8)
        self.assertAlmostEqual(tgt, 100.0 - 1.6)

    def test_touch_is_not_fill_and_no_fill_on_signal_bar(self):
        # first 1m bars after the signal close only touch 100.00 (high == L): no fill; later through 100.03 fills
        bars = flat(5, 99.5) + [(99.5, 100.00, 99.4, 99.5)] + flat(54, 99.5) + [(99.5, 100.2, 99.4, 99.5)] * 3
        side, L, stop, tgt, dist = study.maker_params(SIG, 100.8, 99.0)
        r = mf.simulate_maker(side, L, stop, tgt, T0, 60 * MIN, T0 + 25 * 3600000, False, m1(bars), tick=TICK)
        self.assertFalse(r["filled"])
        # naive fill-on-touch variant (tick=0) WOULD fill on the same bars: the test discriminates
        naive = mf.simulate_maker(side, L, stop, tgt, T0, 60 * MIN, T0 + 25 * 3600000, False, m1(bars), tick=0.0)
        self.assertTrue(naive["filled"])
        # through by one tick fills at L, never at a better price
        bars2 = flat(5, 99.5) + [(99.5, 100.01, 99.4, 99.5)] + flat(54, 99.5)
        r = mf.simulate_maker(side, L, stop, tgt, T0, 60 * MIN, T0 + 25 * 3600000, False, m1(bars2), tick=TICK)
        self.assertTrue(r["filled"])
        self.assertEqual(r["entry_px"], 100.0)

    def test_naive_fill_on_close_would_differ(self):
        # naive variant (fill at the signal close 99.5, original taker style) gives a different, better entry;
        # the maker model must keep entry == broken level 100.0 and must ignore bars before the signal close
        bars = [(99.5, 101.0, 99.4, 99.5)] * 3 + flat(57, 99.5)     # bars BEFORE signal close would 'fill'
        side, L, stop, tgt, dist = study.maker_params(SIG, 100.8, 99.0)
        pre = m1(bars, t0=T0 - 3 * MIN)
        r = mf.simulate_maker(side, L, stop, tgt, T0, 60 * MIN, T0 + 25 * 3600000, False, pre, tick=TICK)
        self.assertFalse(r["filled"])   # pre-signal bars never read

    def test_order_expires_after_one_bar(self):
        bars = flat(60, 99.5) + [(99.5, 100.5, 99.4, 99.5)] + flat(10, 99.5)   # through only at minute 60 = after expiry
        side, L, stop, tgt, dist = study.maker_params(SIG, 100.8, 99.0)
        r = mf.simulate_maker(side, L, stop, tgt, T0, 60 * MIN, T0 + 25 * 3600000, False, m1(bars), tick=TICK)
        self.assertFalse(r["filled"])

    def test_long_mirror_uses_low_extreme(self):
        s = dict(dir=1, lvl=100.0, atr=0.5)
        side, L, stop, tgt, dist = study.maker_params(s, 101.0, 99.3)
        self.assertAlmostEqual(dist, 0.7)
        self.assertAlmostEqual(stop, 99.3)
        self.assertAlmostEqual(tgt, 101.4)

    def test_time_exit_bar(self):
        self.assertEqual(study.TS_BARS, 25)   # close of bar e+24 = open of bar e+25


if __name__ == "__main__":
    unittest.main()
