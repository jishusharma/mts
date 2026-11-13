"""Tests for run_1113.py: ADX against the hand toy of FORMULAS.md 30.2, Rule A events, a hand-built Rule B trade, bootstrap."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_1113 as R  # noqa: E402

H = [10, 11, 12, 11, 13, 14, 13, 12, 11, 12, 13, 15, 14, 13, 12, 11, 12, 14, 15, 14]
L = [8, 9, 10, 9, 10, 12, 11, 10, 9, 10, 11, 12, 12, 11, 10, 9, 10, 11, 13, 12]
C = [9, 10, 11, 10, 12, 13, 12, 11, 10, 11, 12, 14, 13, 12, 11, 10, 11, 13, 14, 13]


class TestAdx(unittest.TestCase):
    def test_toy_n3(self):
        dip, dim, adx = R.adx_di(H, L, C, 3)
        self.assertAlmostEqual(dip[3], 33.3333, 3)
        self.assertAlmostEqual(dim[3], 16.6667, 3)
        self.assertAlmostEqual(dip[4], 47.619, 3)
        self.assertAlmostEqual(dim[4], 9.524, 3)
        self.assertIsNone(adx[4])
        self.assertAlmostEqual(adx[5], 5800 / 99, 4)       # 58.586
        self.assertAlmostEqual(adx[6], 435500 / 9207, 4)   # 47.301
        self.assertAlmostEqual(adx[19], 34.938, 3)

    def test_ema_seed(self):
        e = R.ema([1, 2, 3, 4, 5], 3)
        self.assertEqual(e[:2], [None, None])
        self.assertAlmostEqual(e[2], 2.0)
        self.assertAlmostEqual(e[3], 3.0)                  # (4-2)*0.5+2
        self.assertAlmostEqual(e[4], 4.0)


class TestRuleA(unittest.TestCase):
    def test_events(self):
        adx = [None, 24, 25, 26, 24, 26, 27]
        dip = [None, 30, 30, 30, 10, 10, 10]
        dim = [None, 10, 10, 10, 30, 30, 30]
        # bar 3: 25 -> 26 crosses (<=25 < 26) long; bar 5: 24 -> 26 short; bar 2: 24 -> 25 is not > 25
        self.assertEqual(R.rule_a_events(dip, dim, adx, start=1), [(3, 1), (5, -1)])

    def test_net_uses_next_open_and_close_h(self):
        bars = [{"o": 50, "c": 50}, {"o": 100, "c": 90}, {"o": 90, "c": 95}, {"o": 95, "c": 120}]
        # signal bar 0, enter open of bar 1 (100), exit close of bar 3 (120), long
        self.assertAlmostEqual(R.a_net(bars, 0, 1, 3), 0.20 - R.FEE)
        self.assertAlmostEqual(R.a_net(bars, 0, -1, 3), -0.20 - R.FEE)


def build(n=40):
    bars = [{"d": "x", "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0} for _ in range(n)]
    adx = [30 + 0.1 * i for i in range(n)]
    return bars, [30.0] * n, [10.0] * n, adx, [98.0] * n


class TestRuleB(unittest.TestCase):
    def test_target_on_entry_bar(self):
        bars, dip, dim, adx, e20 = build()
        bars[25].update(l=97.0, h=100.5, c=99.0)             # touch bar t=25, High 100.5
        bars[26].update(o=100.0, h=101.0, l=99.5, c=100.8)   # breaks 100.5; fill max(100,100.5)=100.5; target 101
        tr, st = R.rule_b(bars, dip, dim, adx, e20, start=21)
        self.assertEqual(len(tr), 1)
        t = tr[0]
        self.assertEqual((t["side"], t["k"], t["e"], t["d"]), (1, 26, 26, 0))
        self.assertAlmostEqual(t["net"], 101 / 100.5 - 1 - R.FEE)

    def test_gap_through_stop(self):
        bars, dip, dim, adx, e20 = build()
        bars[25].update(l=97.0, h=100.5, c=99.0)
        bars[26].update(o=100.0, h=100.6, l=99.5, c=100.0)   # fill 100.5, target 101 not reached
        bars[27].update(o=96.0, h=97.0, l=95.0, c=96.0)      # gaps under stop 97 -> exit at open 96
        tr, _ = R.rule_b(bars, dip, dim, adx, e20, start=21)
        self.assertEqual((tr[0]["k"], tr[0]["e"]), (26, 27))
        self.assertAlmostEqual(tr[0]["net"], 96 / 100.5 - 1 - R.FEE)

    def test_no_trigger_expires_and_short_mirror(self):
        bars, dip, dim, adx, e20 = build()
        bars[25].update(l=97.0, h=100.5, c=99.0)             # nothing in 26..28 exceeds 100.5
        for j in (26, 27, 28):
            bars[j]["h"] = 100.4
        tr, _ = R.rule_b(bars, dip, dim, adx, e20, start=21)
        self.assertEqual(tr, [])
        bars, dip, dim, adx, e20 = build()
        dip, dim = [10.0] * 40, [30.0] * 40
        e20 = [102.0] * 40                                    # short: High[t] >= EMA, Close[t-1] < EMA
        bars[25].update(h=103.0, l=99.5, c=101.0)
        bars[26].update(o=100.0, h=100.2, l=99.0, c=99.2)     # breaks 99.5; fill min(100, 99.5)=99.5
        tr, _ = R.rule_b(bars, dip, dim, adx, e20, start=21)
        self.assertEqual(tr[0]["side"], -1)
        self.assertEqual(tr[0]["k"], 26)


class TestBoot(unittest.TestCase):
    def test_small_n_has_no_ci(self):
        m, lo, hi = R.boot([("2024-01", 0.01)] * 3)
        self.assertAlmostEqual(m, 0.01)
        self.assertIsNone(lo)

    def test_ci_brackets_mean_and_is_seeded(self):
        items = [("2024-%02d" % (i % 12 + 1), (i % 7 - 3) / 100.0 + 0.01) for i in range(60)]
        a = R.boot(items, reps=2000)
        b = R.boot(items, reps=2000)
        self.assertEqual(a, b)
        self.assertLess(a[1], a[0])
        self.assertGreater(a[2], a[0])


if __name__ == "__main__":
    unittest.main()
