"""Tests for run_divergence_mtf.py (T089/T091). Expected values are hand-derived from the module docstring
spec and FORMULAS.md s7, never computed with the module."""
import unittest

from MyTradingSys.backtest.layers.rsi import run_divergence_mtf as rd


def series(closes, rsi):
    return closes, rsi, list(range(1000, 1000 + len(closes)))


class LongRangeDivergence(unittest.TestCase):
    def _bear(self):
        # swing highs at 2 (close 110, rsi 70), 7 (105, 60) and 14 (112, 65); lows elsewhere.
        c = [100.0] * 17
        r = [50.0] * 17
        c[2], r[2] = 110.0, 70.0
        c[7], r[7] = 105.0, 60.0
        c[14], r[14] = 112.0, 65.0
        c[1] = c[3] = c[6] = c[8] = c[13] = c[15] = 101.0
        return series(c, r)

    def test_bearish_hit_with_smaller_swing_between(self):
        c, r, ts = self._bear()
        ev = rd.long_range_divergence(c, r, ts, 11, 60, "bearish")
        # B=14, A=2: 13 bars inclusive, one swing (7, close 105 < 110) between, close 112 > 110, rsi 65 < 70.
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["a_i"], e["b_i"], e["bars"], e["n_between"], e["i"], e["t"]), (2, 14, 13, 1, 15, 1015))

    def test_between_swing_larger_than_a_blocks(self):
        c, r, ts = self._bear()
        c[7] = 111.0   # in-between high above A (110): not "smaller swings between"
        ev = rd.long_range_divergence(c, r, ts, 11, 60, "bearish")
        self.assertEqual(ev, [])

    def test_window_bounds(self):
        c, r, ts = self._bear()
        self.assertEqual(rd.long_range_divergence(c, r, ts, 14, 60, "bearish"), [])   # 13 < 14
        self.assertEqual(rd.long_range_divergence(c, r, ts, 3, 12, "bearish"), [])    # 13 > 12

    def test_rsi_must_disagree(self):
        c, r, ts = self._bear()
        r[14] = 75.0   # RSI higher high too: no divergence
        self.assertEqual(rd.long_range_divergence(c, r, ts, 11, 60, "bearish"), [])

    def test_adjacent_pair_not_counted(self):
        c = [100.0] * 16
        r = [50.0] * 16
        c[2], r[2] = 110.0, 70.0
        c[14], r[14] = 112.0, 65.0
        c[1] = c[3] = c[13] = c[15] = 101.0
        self.assertEqual(rd.long_range_divergence(c, r, list(range(16)), 11, 60, "bearish"), [])

    def test_bullish_mirror(self):
        c, r, ts = self._bear()
        c = [200.0 - x for x in c]          # highs become lows: A 90, between 95, B 88
        r = [100.0 - x for x in r]          # rsi A 30, B 35 (higher low)
        ev = rd.long_range_divergence(c, r, ts, 11, 60, "bullish")
        self.assertEqual([(e["a_i"], e["b_i"]) for e in ev], [(2, 14)])


class Scoring(unittest.TestCase):
    def test_forward_returns_formula7(self):
        closes = [100.0, 101.0, 99.0]
        f = rd.forward_returns(0, -1.0, closes, horizons=(1, 2, 5))
        self.assertAlmostEqual(f[1], -0.01)
        self.assertAlmostEqual(f[2], 0.01)
        self.assertNotIn(5, f)          # no data: no entry, not zero

    def test_net_deducts_round_trip_taker(self):
        closes = [100.0 + i for i in range(30)]   # long event at 0: +10% at h=10
        s = rd.score([{"i": 0, "t": 0}], closes, 1.0, rd.baseline(closes), taker=0.0005)
        p = s["horizons"][10]
        self.assertAlmostEqual(p["gross_mean"], 0.10)
        self.assertAlmostEqual(p["net_mean"], 0.10 - 0.001)
        self.assertEqual(s["verdict"], "insufficient n")

    def test_verdict_rules(self):
        good = {"n": 300, "net_mean": 0.001, "net_t": 2.5, "gross_mean": 0.002, "baseline_side": 0.0}
        years_ok = {2022: {"n": 100, "net_mean": 0.001}, 2023: {"n": 100, "net_mean": -0.001}}
        self.assertEqual(rd.verdict(good, years_ok), "edge candidate")
        self.assertEqual(rd.verdict(dict(good, n=299), years_ok), "insufficient n")
        self.assertEqual(rd.verdict(dict(good, net_t=1.9), years_ok), "no edge")
        self.assertEqual(rd.verdict(dict(good, baseline_side=0.003), years_ok), "no edge")
        bad_years = {2022: {"n": 100, "net_mean": 0.001}, 2023: {"n": 100, "net_mean": -0.001},
                     2024: {"n": 100, "net_mean": -0.002}}
        self.assertEqual(rd.verdict(good, bad_years), "no edge")


if __name__ == "__main__":
    unittest.main()
