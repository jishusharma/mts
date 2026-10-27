import math
import random
import tempfile
import unittest
from pathlib import Path

from MyTradingSys.backtest.layers.rsi import div_flags_chart as D
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence, KINDS
from MyTradingSys.backtest.layers.rsi.krown_hidden_divergence import krown_hidden_divergence

try:
    import matplotlib  # noqa: F401
    HAVE_MPL = True
except ImportError:
    HAVE_MPL = False

# Hand-built: swing closes and RSI values are chosen first, expectations follow from the rule text.
DAY = 86400000


def _ts(x):
    return list(range(len(x)))


class TestReverse(unittest.TestCase):
    """PRD / NRD as Malkan says them (shape + trend regime RSI 60/40). Numbers chosen first, expectations by hand."""

    def test_prd(self):
        # low pivots idx1 (10) and idx4 (11): price HIGHER low; RSI 65 -> 62 LOWER low, both >= 60 (uptrend regime)
        close = [12, 10, 11, 12, 11, 12, 13, 14]
        rsi = [70, 65, 66, 68, 62, 66, 68, 72]
        ev = rsi_divergence(close, rsi, _ts(close), 3, 10, "prd")
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["t"], e["a_i"], e["b_i"], e["bars"], e["event"]), (5, 1, 4, 4, "prd_divergence"))
        self.assertEqual((e["close_a"], e["close_b"], e["rsi_a"], e["rsi_b"]), (10, 11, 65, 62))
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10, "bullish"), [])

    def test_prd_shape_correct_but_not_uptrend(self):
        # same price shape, RSI lower low (35 -> 30) but RSI far below 60: no uptrend regime -> NOT a PRD
        close = [12, 10, 11, 12, 11, 12, 13, 14]
        rsi = [40, 35, 36, 38, 30, 36, 38, 45]
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10, "prd"), [])
        # only point B drops under 60 (65 -> 55): still not a PRD
        rsi2 = [70, 65, 66, 68, 55, 66, 68, 72]
        self.assertEqual(rsi_divergence(close, rsi2, _ts(close), 3, 10, "prd"), [])

    def test_nrd(self):
        # high pivots idx1 (20) and idx4 (19): price LOWER high; RSI 30 -> 36 HIGHER high, both <= 40 (downtrend regime)
        close = [18, 20, 19, 17, 19, 17, 16, 15]
        rsi = [25, 30, 28, 26, 36, 28, 20, 15]
        ev = rsi_divergence(close, rsi, _ts(close), 3, 10, "nrd")
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["t"], e["a_i"], e["b_i"], e["close_a"], e["close_b"], e["rsi_a"], e["rsi_b"]),
                         (5, 1, 4, 20, 19, 30, 36))
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10, "bearish"), [])

    def test_nrd_shape_correct_but_not_downtrend(self):
        close = [18, 20, 19, 17, 19, 17, 16, 15]
        rsi = [55, 60, 58, 56, 66, 58, 50, 45]   # RSI higher high 60 -> 66 but above 40: not a downtrend regime
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10, "nrd"), [])

    def test_bars_window_applies(self):
        close = [12, 10, 11, 12, 11, 12, 13, 14]
        rsi = [70, 65, 66, 68, 62, 66, 68, 72]   # bars A..B = 4
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 5, 14, "prd"), [])

    def test_no_hidden_kind_in_malkan_layer(self):
        for k in ("hidden_bullish", "hidden_bearish"):
            self.assertNotIn(k, KINDS)
            with self.assertRaises(ValueError):
                rsi_divergence([1, 2, 3], [1, 2, 3], [0, 1, 2], 3, 10, k)


class TestKrownHidden(unittest.TestCase):
    """KROWN-CONFLUENCE generic hidden divergence: same shapes, NO trend condition."""

    def test_hidden_bullish_any_level(self):
        close = [12, 10, 11, 12, 11, 12, 13, 14]
        rsi = [40, 35, 36, 38, 30, 36, 38, 45]   # low RSI: the Malkan PRD rejects this, Krown accepts
        ev = krown_hidden_divergence(close, rsi, _ts(close), 3, 10, "hidden_bullish")
        self.assertEqual(len(ev), 1)
        e = ev[0]
        self.assertEqual((e["t"], e["a_i"], e["b_i"], e["bars"], e["event"], e["source"]),
                         (5, 1, 4, 4, "hidden_bullish_divergence", "KROWN-CONFLUENCE"))
        self.assertEqual((e["close_a"], e["close_b"], e["rsi_a"], e["rsi_b"]), (10, 11, 35, 30))

    def test_hidden_bearish_any_level(self):
        close = [18, 20, 19, 17, 19, 17, 16, 15]
        rsi = [55, 60, 58, 56, 66, 58, 50, 45]
        ev = krown_hidden_divergence(close, rsi, _ts(close), 3, 10, "hidden_bearish")
        self.assertEqual([(e["t"], e["rsi_a"], e["rsi_b"]) for e in ev], [(5, 60, 66)])

    def test_regular_not_hidden(self):
        close = [12, 10, 11, 12, 9, 10, 11, 13]
        rsi = [40, 30, 35, 38, 33, 36, 38, 45]
        self.assertEqual(len(rsi_divergence(close, rsi, _ts(close), 3, 10, "bullish")), 1)
        self.assertEqual(krown_hidden_divergence(close, rsi, _ts(close), 3, 10, "hidden_bullish"), [])

    def test_bad_kind(self):
        with self.assertRaises(ValueError):
            krown_hidden_divergence([1, 2, 3], [1, 2, 3], [0, 1, 2], 3, 10, "prd")


class TestRegular(unittest.TestCase):
    def test_regular_still_detected(self):
        close = [12, 10, 11, 12, 9, 10, 11, 13]
        rsi = [40, 30, 35, 38, 33, 36, 38, 45]
        self.assertEqual(len(rsi_divergence(close, rsi, _ts(close), 3, 10, "bullish")), 1)
        self.assertEqual(rsi_divergence(close, rsi, _ts(close), 3, 10, "prd"), [])

    def test_bad_kind(self):
        with self.assertRaises(ValueError):
            rsi_divergence([1, 2, 3], [1, 2, 3], [0, 1, 2], 3, 10, "sideways")


def _series(n=400):
    out = []
    rnd = random.Random(7)
    c = 100.0
    for i in range(n):
        c += rnd.uniform(-3, 3) + 2.0 * math.sin(i / 40.0)   # slow trend swings so PRD/NRD regimes occur
        out.append({"t": i * DAY, "o": c - 0.5, "h": c + 1.5, "l": c - 1.5, "c": c, "v": 1.0})
    return out


class TestCausalAndRender(unittest.TestCase):
    def test_causality_truncation(self):
        bars = _series()
        full, _ = D.detect_all(bars)
        self.assertGreater(len(full), 3)
        self.assertEqual({e["kind"] for e in full}, set(D.ALL_KINDS))

        def key(e):
            return (e["kind"], e["a_i"], e["b_i"], e["t"], e["rsi_a"], e["rsi_b"])

        for cut in (60, 150, 250, 399):
            part, _ = D.detect_all(bars[:cut])
            expect = [key(e) for e in full if e["i"] < cut]
            self.assertEqual([key(e) for e in part], expect, "cut=%d" % cut)

    def test_event_stamped_after_swing(self):
        for e in D.detect_all(_series())[0]:
            self.assertEqual(e["i"], e["b_i"] + 1)

    def test_weekly_complete_weeks_only(self):
        # epoch day 0 is Thursday, day 4 is Monday. Days 2..20: complete weeks start 4 and 11 (4..10, 11..17)
        days = [{"t": d * DAY, "o": d, "h": d + 2, "l": d - 1, "c": d + 1, "v": 1} for d in range(2, 21)]
        wk = D.weekly_from_daily(days)
        self.assertEqual([w["t"] // DAY for w in wk], [4, 11])
        self.assertEqual((wk[0]["o"], wk[0]["c"], wk[0]["h"], wk[0]["l"]), (4, 11, 12, 3))

    @unittest.skipUnless(HAVE_MPL, "matplotlib not installed")
    def test_render_smoke(self):
        bars = _series()
        evs, rsi = D.detect_all(bars)
        with tempfile.TemporaryDirectory() as d:
            png = Path(d) / "c" / "x.png"
            res = D.render(bars, evs, rsi, "1d", "TEST", 100, png)
            self.assertTrue(png.exists() and png.stat().st_size > 5000)
            start, sel = D.select_window(evs, 100, len(bars))
            self.assertEqual(res["n_events"], len(sel))
            self.assertEqual(res["n_annotations"], res["n_events"])
            self.assertGreater(res["n_events"], 0)
            rows = D.table_rows(res["events"], "1d")
            D.write_table({"1d": rows}, d, "TEST")
            md = (Path(d) / "TEST_divergences.md").read_text(encoding="utf-8")
            self.assertEqual(md.count("| 1d |"), len(rows))


if __name__ == "__main__":
    unittest.main()
