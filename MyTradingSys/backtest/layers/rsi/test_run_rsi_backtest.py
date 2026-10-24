"""Tests for run_rsi_backtest.py. Synthetic bars only; expected numbers are hand-derived from the
spec (fees: sim.py maker 0 / taker 5 bps; bracket stop 1% / target 2%), never computed with the driver."""
import math
import random
import unittest

from MyTradingSys.backtest.layers.rsi import run_rsi_backtest as rr

HOUR = 3600000
DAY = 24 * HOUR


def bar(t, o, h, l, c):
    return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": 1.0}


def flat(t, px=100.0):
    return bar(t, px, px + 0.5, px - 0.5, px)


def hourly_bars(n, start=0):
    """Rising 0.1%/bar series (open == close), 1h spacing."""
    out = []
    for i in range(n):
        c = 100.0 * 1.001 ** i
        out.append(bar(start + i * HOUR, c, c * 1.001, c * 0.999, c))
    return out


def minute_bars(n, start=0):
    out = []
    for i in range(n):
        c = 100.0 + (i % 7) * 0.1
        out.append({"t": start + i * 60000, "o": c, "h": c + 0.2, "l": c - 0.2, "c": c, "v": 2.0, "tbv": 1.5})
    return out


def wavy(seed, n=400, mirror=False):
    r = random.Random(seed)
    p, bars = 100.0, []
    for i in range(n):
        o = p
        p = p * (1 + 0.004 * math.sin(i / 9) + r.gauss(0, 0.006))
        bars.append(bar(i * HOUR, o, max(o, p) * 1.001, min(o, p) * 0.999, p))
    if not mirror:
        return bars
    K = max(b["h"] for b in bars) + min(b["l"] for b in bars)
    return [bar(b["t"], K - b["o"], K - b["l"], K - b["h"], K - b["c"]) for b in bars]


class TestFees(unittest.TestCase):
    def test_fees_are_sim_canonical(self):
        self.assertEqual(rr.TAKER_FEE, 0.0005)
        self.assertEqual(rr.MAKER_FEE, 0.0)

    def test_default_brackets(self):
        self.assertEqual((rr.STOP_PCT, rr.TARGET_PCT), (0.01, 0.02))


class TestSplitAndVerdict(unittest.TestCase):
    def test_split_70_30(self):
        a, b, n_is = rr.chronological_split(list(range(10)))
        self.assertEqual((len(a), len(b), n_is), (7, 3, 7))
        self.assertEqual(rr.chronological_split([]), ([], [], 0))

    def test_verdict_rule(self):
        v = rr.verdict
        self.assertEqual(v(29, 0.01, 0.1), "insufficient n")
        self.assertEqual(v(30, 0.01, 0.49), "edge")
        self.assertEqual(v(30, 0.01, 0.5), "no edge")
        self.assertEqual(v(30, -0.001, 0.1), "no edge")
        self.assertEqual(v(30, 0.0, 0.1), "no edge")
        self.assertEqual(v(30, 0.01, None), "no edge")
        self.assertEqual(v(0, None, None), "insufficient n")


class TestTrades(unittest.TestCase):
    def test_long_target(self):
        bars = [flat(0), bar(HOUR, 100, 102.5, 99.5, 102)]
        tr = rr.trades_from_events([{"i": 0, "side": "long"}], bars, max_bars=10)
        self.assertEqual(len(tr), 1)
        self.assertEqual(tr[0]["exit_reason"], "targets")
        self.assertAlmostEqual(tr[0]["net"], 0.02 - 0.0005, places=9)  # maker target, taker entry

    def test_short_target(self):
        bars = [flat(0), bar(HOUR, 100, 100.5, 97.5, 98)]
        tr = rr.trades_from_events([{"i": 0, "side": "short"}], bars, max_bars=10)
        self.assertAlmostEqual(tr[0]["net"], 0.0195, places=9)

    def test_long_stop(self):
        bars = [flat(0), bar(HOUR, 100, 100.2, 98.5, 99)]
        tr = rr.trades_from_events([{"i": 0, "side": "long"}], bars, max_bars=10)
        self.assertEqual(tr[0]["exit_reason"], "stop")
        # -1% - entry taker 0.05% - stop taker 0.0005*0.99
        self.assertAlmostEqual(tr[0]["net"], -0.01 - 0.0005 - 0.000495, places=9)

    def test_gap_through_stop_fills_at_open(self):
        bars = [flat(0), bar(HOUR, 98, 98.5, 97, 98)]
        tr = rr.trades_from_events([{"i": 0, "side": "long"}], bars, max_bars=10)
        self.assertAlmostEqual(tr[0]["net"], -0.02 - 0.0005 - 0.0005 * 0.98, places=9)

    def test_same_bar_stop_and_target_is_stop(self):
        bars = [flat(0), bar(HOUR, 100, 102.5, 98.5, 100)]
        tr = rr.trades_from_events([{"i": 0, "side": "long"}], bars, max_bars=10)
        self.assertEqual(tr[0]["exit_reason"], "stop")

    def test_timeout_exit_at_close_pays_taker(self):
        bars = [flat(0)] + [bar((k + 1) * HOUR, 100.5, 100.6, 100.4, 100.5) for k in range(2)]
        tr = rr.trades_from_events([{"i": 0, "side": "long"}], bars, max_bars=2)
        self.assertEqual(tr[0]["exit_reason"], "timeout")
        self.assertAlmostEqual(tr[0]["net"], 0.005 - 0.0005 - 0.0005 * 1.005, places=9)

    def test_open_at_end_dropped_and_custom_fees(self):
        bars = [flat(0), flat(HOUR)]
        self.assertEqual(rr.trades_from_events([{"i": 0, "side": "long"}], bars, max_bars=10), [])
        bars = [flat(0), bar(HOUR, 100, 102.5, 99.5, 102)]
        tr = rr.trades_from_events([{"i": 0, "side": "long"}], bars, max_bars=10, taker=0.0, maker=0.0)
        self.assertAlmostEqual(tr[0]["net"], 0.02, places=9)

    def test_one_position_at_a_time(self):
        bars = [flat(0), flat(HOUR), bar(2 * HOUR, 100, 102.5, 99.5, 100),   # A: target on bar 2
                bar(3 * HOUR, 100, 100.2, 98.5, 99), flat(4 * HOUR)]        # C: stop on bar 3
        ev = [{"i": 0, "side": "long"}, {"i": 1, "side": "long"}, {"i": 2, "side": "long"}]
        tr = rr.trades_from_events(ev, bars, max_bars=10)
        self.assertEqual([t["i"] for t in tr], [0, 2])   # i=1 overlaps trade A (exit bar 2)
        self.assertAlmostEqual(tr[0]["net"], 0.0195, places=9)
        self.assertAlmostEqual(tr[1]["net"], -0.010995, places=9)
        self.assertEqual(tr[1]["t"], 2 * HOUR)

    def test_trade_stats(self):
        s = rr.trade_stats([{"net": 0.02, "exit_reason": "targets"}, {"net": -0.01, "exit_reason": "stop"}])
        self.assertEqual(s["n"], 2)
        self.assertAlmostEqual(s["mean_net"], 0.005)
        self.assertAlmostEqual(s["sum_net"], 0.01)
        self.assertEqual(s["hit_rate"], 0.5)
        e = rr.trade_stats([])
        self.assertEqual((e["n"], e["mean_net"], e["hit_rate"]), (0, None, None))

    def test_daily_net_returns(self):
        trades = [{"t": 0, "net": 0.01}, {"t": HOUR, "net": 0.03}, {"t": DAY, "net": -0.02}]
        days = [rr._day(0), rr._day(DAY), rr._day(2 * DAY)]
        got = rr.daily_net_returns(trades, days)
        self.assertAlmostEqual(got[0], 0.04)
        self.assertAlmostEqual(got[1], -0.02)
        self.assertEqual(got[2], 0.0)


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.bars = hourly_bars(420)
        self.n_is = 294

    def test_too_few_bars(self):
        r = rr.grid_search_and_oos(lambda p: [], [{"k": 0}], hourly_bars(40), 28)
        self.assertIsNone(r["chosen"])
        self.assertEqual(r["reason"], "too_few_bars")

    def test_zero_events(self):
        r = rr.grid_search_and_oos(lambda p: [], [{"k": 0}, {"k": 1}], self.bars, self.n_is)
        self.assertIsNone(r["chosen"])
        self.assertEqual(r["reason"], "no_variant_with_min_events")
        self.assertEqual(r["verdict"], "insufficient n")

    def _fn(self, p):
        side = "long" if p["k"] == 0 else "short"
        return [{"i": i, "side": side} for i in range(0, 420, 40)]

    def test_picks_best_variant_on_net_bracket_returns(self):
        # rising 0.1%/bar: long target is hit on the 19th bar after entry (+2% - 5bp = +1.95%); short is stopped after
        # 10 bars at +1% (-1% - 0.05% - 0.0505% = -1.1005%).
        r = rr.grid_search_and_oos(self._fn, [{"k": 1}, {"k": 0}], self.bars, self.n_is, max_bars=100)
        self.assertEqual(r["chosen"], {"k": 0})
        # IS = 294 bars: long events 0..240 resolve in-sample (i=280 would exit at 300 -> dropped)
        self.assertEqual(r["is_stats"]["n"], 7)
        self.assertAlmostEqual(r["is_stats"]["mean_net"], 0.0195, places=9)
        # bar i+m has high c*1.001**(m+1) >= 1.02c first at m=19, so i=400 exits on bar 419 (the last): all
        # three OOS events (320, 360, 400) resolve
        self.assertEqual(r["oos_stats"]["n"], 3)
        self.assertAlmostEqual(r["oos_stats"]["mean_net"], 0.0195, places=9)
        self.assertEqual(r["verdict"], "insufficient n")
        self.assertTrue(r["pbo"] is None or 0.0 <= r["pbo"] <= 1.0)
        self.assertEqual(r["n_variants"], 2)
        short = [g for g in r["all_grid"] if g["params"] == {"k": 1}][0]
        self.assertAlmostEqual(short["mean_is"], -0.011005, places=9)
        self.assertEqual(short["n_is"], 8)

    def test_is_trades_do_not_use_oos_bars(self):
        # only event at i=290 (IS); target would be hit at bar 310 (OOS) -> must be dropped, n_is = 0
        r = rr.grid_search_and_oos(lambda p: [{"i": 290, "side": "long"}], [{"k": 0}], self.bars, self.n_is,
                                   max_bars=100, min_events=1)
        self.assertIsNone(r["chosen"])

    def test_survives_detector_error(self):
        def fn(p):
            if p["k"] == 0:
                raise ValueError("boom")
            return self._fn({"k": 0})
        r = rr.grid_search_and_oos(fn, [{"k": 0}, {"k": 1}], self.bars, self.n_is, max_bars=100)
        self.assertEqual(r["chosen"], {"k": 1})

    def test_min_events_gate(self):
        r = rr.grid_search_and_oos(self._fn, [{"k": 0}], self.bars, self.n_is, max_bars=100, min_events=8)
        self.assertIsNone(r["chosen"])


class TestSignalMapping(unittest.TestCase):
    def test_signals_to_events(self):
        bars = [flat(0), flat(HOUR), flat(2 * HOUR)]
        sigs = [{"t": 2 * HOUR, "side": "short"}, {"t": HOUR, "side": "long"}]
        self.assertEqual(rr.signals_to_events(sigs, bars),
                         [{"i": 1, "side": "long"}, {"i": 2, "side": "short"}])

    def test_rsi_ma_event_mapping(self):
        bars = [flat(k * HOUR) for k in range(5)]
        evs = [{"t": HOUR, "event": "ma_support"}, {"t": 2 * HOUR, "event": "ma_rejection"},
               {"t": 3 * HOUR, "event": "cross", "direction": "up"},
               {"t": 4 * HOUR, "event": "cross", "direction": "down"},
               {"t": 4 * HOUR, "event": "failure"}]
        touch = rr.rsi_ma_to_events(evs, bars, "touch")
        self.assertEqual(touch, [{"i": 1, "side": "long"}, {"i": 2, "side": "short"}])
        cross = rr.rsi_ma_to_events(evs, bars, "cross")
        self.assertEqual(cross, [{"i": 3, "side": "long"}, {"i": 4, "side": "short"}])
        with self.assertRaises(ValueError):
            rr.rsi_ma_to_events(evs, bars, "nope")

    def test_safe_rsi_short_series(self):
        self.assertEqual(rr.safe_rsi([1.0, 2.0, 3.0], 14), [None, None, None])
        self.assertEqual(len(rr.safe_rsi([float(i % 5) for i in range(40)], 14)), 40)


class TestHtfClose(unittest.TestCase):
    def test_close_times_shift_open_to_close(self):
        reg = rr.load_registry()
        # 1970-01-05 is a Monday: week bar opens at 4d, closes at 11d. 1970-01 month closes at 31d.
        self.assertEqual(rr.htf_close_times([{"t": 4 * DAY}], "1w", reg), [11 * DAY])
        self.assertEqual(rr.htf_close_times([{"t": 0}], "1M", reg), [31 * DAY])

    def test_gate_sees_only_closed_htf_bar(self):
        # weekly regime: week opened at 4d is BULL but closes at 11d. A daily signal at 8d must NOT see it
        # (module's state_asof on open-times would leak it); a signal at 11d may.
        from MyTradingSys.backtest.layers.rsi.malkan_mtf import state_asof
        reg = rr.load_registry()
        closes = rr.htf_close_times([{"t": 4 * DAY}], "1w", reg)
        self.assertIsNone(state_asof(closes, ["BULL"], 8 * DAY))
        self.assertEqual(state_asof(closes, ["BULL"], 11 * DAY), "BULL")


class TestFamilyEvents(unittest.TestCase):
    """Metamorphic: a linear price mirror (p' = K - p) maps RSI to 100 - RSI, so every long event on the
    series must be a short event at the same bar on the mirror (bull<->bear, support<->rejection,
    cross up<->down)."""

    def _idx(self, ev, side):
        return [e["i"] for e in ev if e["side"] == side]

    def test_malkan_40_60_mirror(self):
        p = {"period": 6, "tolerance": 5.0, "lookback": 5}
        a = rr.malkan_events(wavy(1), p)
        b = rr.malkan_events(wavy(1, mirror=True), p)
        self.assertEqual(self._idx(a, "long"), [i for i in self._idx(b, "short")])
        self.assertEqual(self._idx(a, "short"), self._idx(b, "long"))
        self.assertEqual(len(self._idx(a, "long")), 4)       # hand-checked fixture, bull-only
        self.assertEqual(self._idx(a, "short"), [])
        self.assertEqual(sorted(e["i"] for e in a), [e["i"] for e in a])

    def test_rsi_ma_mirror_both_modes(self):
        for mode in ("touch", "cross"):
            p = {"period": 6, "ma_length": 5, "tolerance": 1.0, "mode": mode}
            a = rr.rsi_ma_family_events(wavy(2), p)
            b = rr.rsi_ma_family_events(wavy(2, mirror=True), p)
            self.assertGreater(len(a), 5, mode)
            self.assertEqual(self._idx(a, "long"), self._idx(b, "short"), mode)
            self.assertEqual(self._idx(a, "short"), self._idx(b, "long"), mode)

    def test_short_series_gives_no_events(self):
        self.assertEqual(rr.malkan_events(wavy(1, n=5), {"period": 14, "tolerance": 2.0, "lookback": 20}), [])
        self.assertEqual(rr.rsi_ma_family_events(wavy(1, n=5), {"period": 14, "ma_length": 14, "tolerance": 1.0,
                                                               "mode": "touch"}), [])

    def test_mtf_subset_of_single_tf(self):
        # MTF = single-TF malkan signals gated by weekly+monthly regime: never more events than ungated.
        bars = wavy(1)
        p = {"period": 6, "tolerance": 5.0, "lookback": 5, "htf_lookback": 3}
        htf = {"1w": wavy(1, n=5), "1M": wavy(1, n=5)}   # <= period bars: no RSI -> gates all None
        m = rr.malkan_mtf_events(bars, htf, rr.load_registry(), p)
        self.assertEqual(m, [])


class TestRunFamily(unittest.TestCase):
    def test_unknown_family(self):
        with self.assertRaises(ValueError):
            rr.run_family("nope", minute_bars(10), rr.load_registry())

    def test_default_grids_sizes(self):
        self.assertEqual(len(rr.GRIDS["malkan_40_60"]), 27)
        self.assertEqual(len(rr.GRIDS["malkan_mtf"]), 18)
        self.assertEqual(len(rr.GRIDS["rsi_ma_events"]), 24)

    def test_smoke_single_tf_families(self):
        reg = rr.load_registry()
        g40 = [{"period": 6, "tolerance": 3.0, "lookback": 5}]
        gma = [{"period": 6, "ma_length": 5, "tolerance": 1.0, "mode": "touch"}]
        for fam, grid in (("malkan_40_60", g40), ("rsi_ma_events", gma)):
            res = rr.run_family(fam, minute_bars(6000), reg, tfs=["5m"], grid=grid)
            r = res["5m"]
            self.assertEqual((r["n_bars"], r["n_bars_is"], r["n_bars_oos"]), (1200, 840, 360))
            self.assertIn(r["result"]["verdict"], ("edge", "no edge", "insufficient n"))
            self.assertEqual(r["result"]["n_variants"], 1)
            self.assertIn("baseline_oos", r)

    def test_short_input(self):
        res = rr.run_family("malkan_40_60", minute_bars(600), rr.load_registry(), tfs=["1h"])
        self.assertIsNone(res["1h"]["result"]["chosen"])
        self.assertEqual(res["1h"]["result"]["reason"], "too_few_bars")

    def test_smoke_mtf(self):
        res = rr.run_family("malkan_mtf", minute_bars(60 * 24 * 40), rr.load_registry(), tfs=["1d"],
                            grid=[{"period": 6, "tolerance": 3.0, "lookback": 5, "htf_lookback": 3}])
        self.assertIn("1d", res)
        self.assertIn("result", res["1d"])


class TestReport(unittest.TestCase):
    def test_render_report(self):
        summary = {"family": "malkan_40_60", "tfs": {"1h": {
            "n_bars": 100, "n_bars_is": 70, "n_bars_oos": 30,
            "result": {"chosen": {"period": 14}, "n_variants": 27, "pbo": 0.25, "verdict": "edge",
                       "is_stats": {"n": 40, "mean_net": 0.001}, "oos_stats": {"n": 31, "mean_net": 0.002,
                                                                                   "hit_rate": 0.5}}}}}
        md = rr.render_report(summary)
        self.assertIn("malkan_40_60", md)
        self.assertIn("| 1h |", md)
        self.assertIn("edge", md)
        self.assertIn("0.250", md)


if __name__ == "__main__":
    unittest.main()
