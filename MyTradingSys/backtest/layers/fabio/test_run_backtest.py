"""Plumbing tests for run_backtest.py (synthetic bars; expected numbers hand-derived)."""
import unittest

from MyTradingSys.backtest.layers.fabio import run_backtest as rb

HOUR = 3600000
DAY = 24 * HOUR


def hourly_bars(n, start=0):
    """Rising 0.1%/bar series, 1h spacing."""
    bars = []
    for i in range(n):
        c = 100.0 * 1.001 ** i
        bars.append({"t": start + i * HOUR, "o": c, "h": c * 1.001, "l": c * 0.999, "c": c, "v": 10.0, "tbv": 6.0})
    return bars


def minute_bars(n, start=0):
    bars = []
    for i in range(n):
        c = 100.0 + (i % 7) * 0.1
        bars.append({"t": start + i * 60000, "o": c, "h": c + 0.2, "l": c - 0.2, "c": c, "v": 2.0, "tbv": 1.5})
    return bars


class TestPlumbing(unittest.TestCase):
    def test_split_70_30(self):
        a, b, n_is = rb.chronological_split(list(range(10)))
        self.assertEqual((len(a), len(b), n_is), (7, 3, 7))
        self.assertEqual(rb.chronological_split([]), ([], [], 0))

    def test_resample_sums_tbv(self):
        reg = rb.load_registry()
        out = rb.resample_with_tbv(minute_bars(30), "5m", reg)
        self.assertEqual(len(out), 6)
        for bar in out:
            self.assertAlmostEqual(bar["tbv"], 7.5)  # 5 x 1.5
            self.assertAlmostEqual(bar["v"], 10.0)
        self.assertEqual(rb.resample_with_tbv([], "5m", reg), [])

    def test_daily_bucketed_returns(self):
        bars = [{"t": 0}, {"t": HOUR}, {"t": DAY}, {"t": DAY + HOUR}]
        closes = [100.0, 110.0, 121.0, 133.1]
        events = [{"i": 0, "side": "long"}, {"i": 1, "side": "short"}, {"i": 2, "side": "long"}]
        days = sorted({rb._day(b["t"]) for b in bars})
        days.append(rb._day(2 * DAY))  # a third, no-signal day
        got = rb.daily_bucketed_returns(events, closes, bars, 1, days)
        # day0: mean(+0.1, -0.1)=0 ; day1: +0.1 ; day2: no signal -> 0
        self.assertAlmostEqual(got[0], 0.0)
        self.assertAlmostEqual(got[1], 0.1)
        self.assertEqual(got[2], 0.0)

    def test_chunked_events_indices(self):
        bars = [{"t": i} for i in range(25)]
        fn = lambda b, **p: [{"i": len(b) - 1, "side": "long"}]
        got = rb.chunked_events(fn, bars, own=10, warm=5)
        self.assertEqual([e["i"] for e in got], [9, 19, 24])

    def test_pbo_too_little_data(self):
        self.assertIsNone(rb.pbo_from_columns([[0.0] * 3]))          # one variant
        self.assertIsNone(rb.pbo_from_columns([[0.0] * 3, [0.1] * 3]))  # 3 rows < 4
        p = rb.pbo_from_columns([[0.01 * (i % 3) for i in range(40)], [0.01 * (i % 5) for i in range(40)]], S=8)
        self.assertTrue(p is None or 0.0 <= p <= 1.0)

    def test_grid_too_few_bars(self):
        r = rb.grid_search_and_oos(lambda b, **p: [], [{"k": 0}], hourly_bars(10), hourly_bars(3))
        self.assertIsNone(r["chosen"])
        self.assertEqual(r["reason"], "too_few_bars")

    def test_grid_zero_events(self):
        r = rb.grid_search_and_oos(lambda b, **p: [], [{"k": 0}, {"k": 1}], hourly_bars(200), hourly_bars(80))
        self.assertIsNone(r["chosen"])
        self.assertEqual(r["reason"], "no_variant_with_min_events")

    def test_grid_picks_best_variant(self):
        def fn(bars, k):
            side = "long" if k == 0 else "short"
            return [{"i": i, "side": side} for i in range(0, len(bars), 3)]
        is_bars, oos_bars = hourly_bars(300), hourly_bars(120, start=300 * HOUR)
        r = rb.grid_search_and_oos(fn, [{"k": 1}, {"k": 0}], is_bars, oos_bars)
        self.assertEqual(r["chosen"], {"k": 0})           # rising series: long wins
        self.assertAlmostEqual(r["is_stats"][1]["mean_return"], 0.001, places=6)
        self.assertGreater(r["oos_stats"][5]["mean_return"], 0.0)
        self.assertGreaterEqual(r["oos_stats"][5]["n"], 1)

    def test_grid_survives_detector_error(self):
        def fn(bars, k):
            if k == 0:
                raise ValueError("boom")
            return [{"i": i, "side": "long"} for i in range(0, len(bars), 3)]
        r = rb.grid_search_and_oos(fn, [{"k": 0}, {"k": 1}], hourly_bars(300), hourly_bars(120, start=300 * HOUR))
        self.assertEqual(r["chosen"], {"k": 1})

    def test_run_tf_smoke_and_short_input(self):
        reg = rb.load_registry()
        res = rb.run_tf("1h", minute_bars(600), reg)          # only 10 hourly bars
        self.assertIsNone(res["cvd_absorption"]["chosen"])
        self.assertEqual(res["volume_fvg"]["n_legs"], 0)
        res2 = rb.run_tf("5m", minute_bars(6000), reg,
                         cvd_grid=[{"price_tolerance": 0.001}], esc_grid=[{"level_tolerance": 0.001}])
        self.assertEqual(res2["n_bars"], 1200)
        self.assertIn("volume_fvg", res2)


if __name__ == "__main__":
    unittest.main()
