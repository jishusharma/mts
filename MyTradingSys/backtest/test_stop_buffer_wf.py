import sys
sys.dont_write_bytecode = True
"""Tests for stop_buffer_wf.py (T081). Expected numbers are derived by hand from FORMULAS.md section 12 (ATR worked example)
and plain arithmetic (R = |entry - stop|, fee_R = fee*price/R, gross = (exit - entry)/R), not from the code."""
import unittest
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import stop_buffer_wf as W  # noqa: E402
import tom_bt as T  # noqa: E402

# FORMULAS.md s12 worked example: highs=[10,11,12,11], lows=[9,9,10,9], closes=[9.5,10.5,11.5,10] -> ATR(3) = 2.1667
H, L, C = [10, 11, 12, 11], [9, 9, 10, 9], [9.5, 10.5, 11.5, 10]


def mk(bars, t0=0):
    """bars: list of (o,h,l,c). Volumes 1, taker-buy 0.5."""
    o, h, l, c, v, tbv = (array("d") for _ in range(6))
    for a, b, d, e in bars:
        o.append(a); h.append(b); l.append(d); c.append(e); v.append(1.0); tbv.append(0.5)
    return T.Bars1m(t0, o, h, l, c, v, tbv)


def example_1m(group=1):
    """1m bars so that every `group` consecutive bars aggregate to one H/L/C bar of the worked example."""
    bars = []
    for h, l, c in zip(H, L, C):
        bars += [(c, h, l, c)] * group
    return mk(bars)


class TestAtr(unittest.TestCase):
    def test_worked_example(self):
        self.assertAlmostEqual(W.atr_at(H, L, C, 3, 3), (2 + 2 + 2.5) / 3)
        self.assertAlmostEqual(W.atr_at(H, L, C, 2, 2), 2.0)       # TR[1]=TR[2]=2
        self.assertIsNone(W.atr_at(H, L, C, 2, 3))                # needs i >= n

    def test_atr_1m_no_lookahead(self):
        a = W.Atr1m(example_1m(1))
        self.assertAlmostEqual(a.atr(4 * 60000, 3), (2 + 2 + 2.5) / 3)   # last closed bar = index 3
        self.assertIsNone(a.atr(3 * 60000, 3))                           # last closed bar = index 2, needs 3 TRs

    def test_atr_tf_uses_closed_bars_only(self):
        s = W.TfSeries(example_1m(5), 5)
        self.assertEqual(s.h, [10, 11, 12, 11])
        self.assertEqual(s.c, [9.5, 10.5, 11.5, 10])
        self.assertAlmostEqual(s.atr(20 * 60000, 3), (2 + 2 + 2.5) / 3)   # 4th 5m bar closes at minute 20
        self.assertAlmostEqual(s.atr(19 * 60000, 2), 2.0)                # only 3 bars closed at minute 19 -> j=2
        self.assertIsNone(s.atr(19 * 60000, 3))


class TestWiden(unittest.TestCase):
    def test_direction(self):
        self.assertAlmostEqual(W.widen_stop("long", 99.0, 0.5, 1.5), 98.25)
        self.assertAlmostEqual(W.widen_stop("short", 101.0, 0.5, 1.5), 101.75)
        self.assertEqual(W.widen_stop("long", 99.0, 0.5, 0.0), 99.0)
        self.assertEqual(W.widen_stop("short", 101.0, 0.5, 0.0), 101.0)


class _Stub:
    def __init__(self, v):
        self.v = v

    def atr(self, t_ms, n=14):
        return self.v


class TestWithAtr(unittest.TestCase):
    def test_basis_choice_and_drop(self):
        series = {5: _Stub(0.5), 15: _Stub(1.5), 60: _Stub(6.0), "1m": _Stub(0.1)}
        mkr = lambda zt: dict(t=1.0, ztype=zt, dir="long", zprice=100.0, stop=99.0, target=103.0)
        out, dropped = W.with_atr([mkr("vwap_band"), mkr("daily_x"), mkr("weekly_x")], "zone_tf", None, series)
        self.assertEqual([r["atr"] for r in out], [0.5, 1.5, 6.0])   # zone_tf: 5m / 15m / 1h
        self.assertEqual(dropped, 0)
        out, _ = W.with_atr([mkr("weekly_x")], "1m", None, series)
        self.assertEqual(out[0]["atr"], 0.1)
        series["1m"] = _Stub(None)
        out, dropped = W.with_atr([mkr("weekly_x")], "1m", None, series)
        self.assertEqual((len(out), dropped), (0, 1))


class TestSimWidened(unittest.TestCase):
    def run_k(self, sig, bars, k, fees):
        rows = W.rows_for_k([sig], k)
        return T.run_variant(rows, mk(bars), fees=fees)[0]

    def test_long_k0_stop_vs_k1_target(self):
        # entry 100 (5m zone: vwap_band), structure stop 99, target 103, ATR 0.5.
        bars = [(100.2, 100.5, 99.9, 100.3),     # fills at 100
                (99.5, 99.8, 98.8, 99.0),        # low 98.8: hits stop 99 (k=0), not 98.5 (k=1)
                (99.0, 103.5, 98.9, 103.2)]      # target 103
        sig = dict(t=0.0, ztype="vwap_band", dir="long", zprice=100.0, stop=99.0, target=103.0, atr=0.5)
        r0 = self.run_k(sig, bars, 0.0, T.FEES_DERIBIT)
        self.assertEqual(r0["reason"], "stop")
        self.assertAlmostEqual(r0["gross_r"], -1.0)                       # exit min(open 99.5, stop 99) = 99; R = 1
        self.assertAlmostEqual(r0["fee_r"], 0.0005 * 99.0 / 1.0)          # 0.0495
        self.assertAlmostEqual(r0["net_r"], -1.0 - 0.0495)
        r1 = self.run_k(sig, bars, 1.0, T.FEES_DERIBIT)
        self.assertEqual(r1["reason"], "target")
        self.assertAlmostEqual(r1["gross_r"], 3.0 / 1.5)                  # stop 98.5 -> R = 1.5
        self.assertAlmostEqual(r1["net_r"], 2.0)                          # maker entry + maker target
        r1t = self.run_k(sig, bars, 1.0, T.FEES_ALL_TAKER)
        self.assertAlmostEqual(r1t["net_r"], 2.0 - (0.0005 * 100 + 0.0005 * 103) / 1.5)

    def test_short_mirror(self):
        bars = [(99.8, 100.1, 99.5, 99.6),       # fills at 100
                (100.8, 101.2, 100.5, 100.9),    # high 101.2: hits stop 101 (k=0), not 101.5 (k=1)
                (100.9, 101.0, 96.5, 97.0)]      # target 97
        sig = dict(t=0.0, ztype="vwap_band", dir="short", zprice=100.0, stop=101.0, target=97.0, atr=0.5)
        r0 = self.run_k(sig, bars, 0.0, T.FEES_DERIBIT)
        self.assertEqual(r0["reason"], "stop")
        self.assertAlmostEqual(r0["net_r"], -1.0 - 0.0005 * 101.0)       # exit max(open 100.8, 101) = 101
        r1 = self.run_k(sig, bars, 1.0, T.FEES_DERIBIT)
        self.assertEqual(r1["reason"], "target")
        self.assertAlmostEqual(r1["net_r"], 2.0)                          # (100-97)/1.5


class TestBlocksPeriod(unittest.TestCase):
    def test_month_blocks(self):
        b = W.month_blocks(W._ts(2025, 9, 1), W._ts(2025, 11, 15))
        self.assertEqual(b, [(W._ts(2025, 9, 1), W._ts(2025, 10, 1)), (W._ts(2025, 10, 1), W._ts(2025, 11, 1)),
                             (W._ts(2025, 11, 1), W._ts(2025, 11, 15))])

    def test_dev_blocks(self):
        b = W.month_blocks(W.DEV_START, W.HOLDOUT_START)
        self.assertEqual(len(b), 10)                                      # Sep 2025 .. Jun 2026
        self.assertEqual(b[-1], (W._ts(2026, 6, 1), W.HOLDOUT_START))
        self.assertEqual(len(b) - W.MIN_TRAIN_BLOCKS, 6)                  # 6 folds >= 4

    def test_period(self):
        self.assertEqual(W.period(W.DEV_START - 1), "hist")
        self.assertEqual(W.period(W.DEV_START), "dev")
        self.assertEqual(W.period(W.HOLDOUT_START - 1), "dev")
        self.assertEqual(W.period(W.HOLDOUT_START), "holdout")


def tr(t, net):
    return dict(t=t, net_r=net)


class TestWalkForward(unittest.TestCase):
    def test_choose_k_rules(self):
        by_k = {0.0: [tr(1, 1.0), tr(2, 1.0), tr(3, 1.0)], 1.0: [tr(4, 5.0)]}
        k, st = W.choose_k(by_k, 100, 0, min_n=3)
        self.assertEqual(k, 0.0)                                          # k=1 has the best mean but n=1 < 3
        self.assertEqual(st[1.0], (1, 5.0))
        self.assertIsNone(W.choose_k(by_k, 100, 0, min_n=4)[0])           # nobody eligible -> abstain
        tie = {0.5: [tr(1, 2.0)], 0.0: [tr(1, 2.0)]}
        self.assertEqual(W.choose_k(tie, 100, 0, min_n=1)[0], 0.0)        # tie -> smaller k

    def test_embargo_excludes_late_train_trades(self):
        by_k = {0.0: [tr(1, 1.0), tr(38, 1.0)], 1.0: [tr(2, 0.5), tr(38, 9.0)]}
        self.assertEqual(W.choose_k(by_k, 40, 0, min_n=1)[0], 1.0)        # means 1.0 vs 4.75
        self.assertEqual(W.choose_k(by_k, 35, 0, min_n=1)[0], 0.0)        # t=38 embargoed: 1.0 vs 0.5

    def test_expanding_folds(self):
        blocks = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 50), (50, 60)]
        by_k = {0.0: [tr(t, -1.0) for t in (1, 11, 21, 31, 41, 51)],
                1.0: [tr(2, 0.5), tr(12, 0.5), tr(22, 0.5), tr(32, 0.5), tr(42, -2.0), tr(52, 3.0)]}
        folds = W.walk_forward(by_k, blocks, min_train=4, min_n=2, embargo=0)
        self.assertEqual(len(folds), 2)
        # fold 1 train t<40: k0 mean -1, k1 mean +0.5 -> k1; test block [40,50): k1 trade t=42 = -2
        self.assertEqual(folds[0]["k"], 1.0)
        self.assertEqual([t["net_r"] for t in folds[0]["oos"]], [-2.0])
        # fold 2 train t<50: k0 -1 (n=5); k1 (4*0.5-2)/5 = 0 -> k1; test [50,60): +3
        self.assertEqual(folds[1]["k"], 1.0)
        self.assertEqual(W.pooled(folds, "oos"), [-2.0, 3.0])
        self.assertEqual(W.pooled(folds, "base"), [-1.0, -1.0])


class TestCell(unittest.TestCase):
    def test_cell_stats(self):
        trades = [dict(filled=True, reason="target", gross_r=2.0, fee_r=0.1, net_r=1.9),
                  dict(filled=True, reason="stop", gross_r=-1.0, fee_r=0.05, net_r=-1.05),
                  dict(filled=True, reason="timeout", gross_r=0.2, fee_r=0.05, net_r=0.15),
                  dict(filled=False, reason="no_fill"), dict(filled=False, reason="ran")]
        c = W.cell(trades)
        self.assertEqual((c["n_sig"], c["n"], c["no_fill"], c["ran"]), (5, 3, 1, 1))
        self.assertAlmostEqual(c["win"], 1 / 3)
        self.assertAlmostEqual(c["timeout"], 1 / 3)
        self.assertAlmostEqual(c["gross"], 1.2 / 3)
        self.assertAlmostEqual(c["net"], 1.0 / 3)
        self.assertAlmostEqual(c["fee"], 0.2 / 3)
        self.assertAlmostEqual(c["net_med"], 0.15)
        self.assertEqual(W.cell([])["n"], 0)


if __name__ == "__main__":
    unittest.main()
