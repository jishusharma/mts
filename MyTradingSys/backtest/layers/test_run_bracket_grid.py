"""
Tests for run_bracket_grid.py (Q1 per-layer bracket grid). Synthetic bars only; no data, no network.
Expected numbers are derived by hand (see comments), never computed with the driver.
Fees: sim.py is canonical (taker 5 bps, maker 0; operator decision 2026-09-30, B080).
Conventions: entry = close of event bar, taker. Bars i+1..i+T scanned. Stop checked before
target inside one bar (worst case). Stop/time exits pay taker on exit, target pays maker.
fee_R = fee_pct / stop_frac (risk = stop_frac * entry).
"""
import importlib.util
import re
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("run_bracket_grid", HERE / "run_bracket_grid.py")
G = importlib.util.module_from_spec(_spec)
sys.modules["run_bracket_grid"] = G
_spec.loader.exec_module(G)

T0 = 1640995200000
H4 = 4 * 3600 * 1000


def bar(k, c, h=None, l=None, step=H4):
    return {"t": T0 + k * step, "o": c, "h": c if h is None else h, "l": c if l is None else l, "c": c}


def flat(n, step=H4):
    return [bar(k, 100.0, 100.1, 99.9, step) for k in range(n)]


class TestFees(unittest.TestCase):
    def test_fee_constants_match_fees_py(self):
        # B081: fees.py is the single source of truth.
        from MyTradingSys.backtest.fees import DERIBIT_TAKER, DERIBIT_MAKER
        self.assertEqual(G.TAKER, DERIBIT_TAKER)
        self.assertEqual(G.MAKER, DERIBIT_MAKER)


class TestSimulate(unittest.TestCase):
    # entry 100, stop 1% -> risk 1.0 price; long stop 99, 2R target 102. fee_R: taker+taker = 0.001/0.01 = 0.1;
    # target: 0.0005/0.01 = 0.05.
    def sim(self, bars, side="long", s=0.01, k=2, T=4):
        return G.simulate_trade(bars, 0, side, s, k, T)

    def test_long_stop(self):
        b = [bar(0, 100.0)] + [bar(1, 99.5, 100.5, 98.9)] + [bar(k, 100.0) for k in range(2, 6)]
        r = self.sim(b)
        self.assertEqual((r["kind"], r["exit_i"]), ("stop", 1))
        self.assertAlmostEqual(r["gross_R"], -1.0)
        self.assertAlmostEqual(r["fee_R"], 0.1)
        self.assertAlmostEqual(r["net_R"], -1.1)

    def test_long_target(self):
        b = [bar(0, 100.0), bar(1, 101.0, 102.5, 99.5)] + [bar(k, 100.0) for k in range(2, 6)]
        r = self.sim(b)
        self.assertEqual(r["kind"], "target")
        self.assertAlmostEqual(r["gross_R"], 2.0)
        self.assertAlmostEqual(r["fee_R"], 0.05)
        self.assertAlmostEqual(r["net_R"], 1.95)

    def test_same_bar_stop_wins(self):
        b = [bar(0, 100.0), bar(1, 100.0, 103.0, 98.0)] + [bar(k, 100.0) for k in range(2, 6)]
        r = self.sim(b)
        self.assertEqual(r["kind"], "stop")
        self.assertAlmostEqual(r["net_R"], -1.1)

    def test_time_exit_long(self):
        b = [bar(0, 100.0)] + [bar(k, 100.2, 101.0, 99.5) for k in (1, 2, 3)] + [bar(4, 100.5, 101.0, 99.5), bar(5, 50.0)]
        r = self.sim(b)
        self.assertEqual((r["kind"], r["exit_i"]), ("time", 4))
        self.assertAlmostEqual(r["gross_R"], 0.5)   # (100.5-100)/1.0
        self.assertAlmostEqual(r["net_R"], 0.4)

    def test_stop_on_last_bar_is_stop_not_time(self):
        b = [bar(0, 100.0)] + [bar(k, 100.0, 100.5, 99.5) for k in (1, 2, 3)] + [bar(4, 99.0, 100.0, 98.9)]
        r = self.sim(b)
        self.assertEqual((r["kind"], r["exit_i"]), ("stop", 4))

    def test_short_target_and_time(self):
        # short: stop 101, target 98
        b = [bar(0, 100.0), bar(1, 99.0, 100.5, 97.9)] + [bar(k, 100.0) for k in range(2, 6)]
        r = self.sim(b, "short")
        self.assertEqual(r["kind"], "target")
        self.assertAlmostEqual(r["net_R"], 1.95)
        b = [bar(0, 100.0)] + [bar(k, 99.8, 100.5, 99.0) for k in (1, 2, 3)] + [bar(4, 99.5, 100.5, 99.0)]
        r = self.sim(b, "short")
        self.assertEqual(r["kind"], "time")
        self.assertAlmostEqual(r["gross_R"], 0.5)   # (100-99.5)/1.0
        self.assertAlmostEqual(r["net_R"], 0.4)

    def test_short_stop(self):
        b = [bar(0, 100.0), bar(1, 100.0, 101.2, 99.5)] + [bar(k, 100.0) for k in range(2, 6)]
        r = self.sim(b, "short")
        self.assertEqual(r["kind"], "stop")
        self.assertAlmostEqual(r["net_R"], -1.1)

    def test_not_enough_bars_returns_none(self):
        self.assertIsNone(self.sim([bar(k, 100.0) for k in range(4)]))   # needs index 4
        self.assertIsNotNone(self.sim([bar(k, 100.0) for k in range(5)]))

    def test_wider_stop_fee_in_R(self):
        # 0.5% stop: stop 99.5; stop-out fee = 0.001/0.005 = 0.2R; net -1.2
        b = [bar(0, 100.0), bar(1, 100.0, 100.1, 99.4)] + [bar(k, 100.0) for k in range(2, 6)]
        r = G.simulate_trade(b, 0, "long", 0.005, 1, 4)
        self.assertEqual(r["kind"], "stop")
        self.assertAlmostEqual(r["net_R"], -1.2)


class TestCellStats(unittest.TestCase):
    def test_hand_example(self):
        tr = [{"kind": "stop", "net_R": -1.1}, {"kind": "target", "net_R": 1.95},
              {"kind": "time", "net_R": 0.4}, {"kind": "target", "net_R": 1.95}]
        s = G.cell_stats(tr, 0.01)
        self.assertEqual(s["n"], 4)
        self.assertAlmostEqual(s["stop_rate"], 0.25)
        self.assertAlmostEqual(s["target_rate"], 0.5)
        self.assertAlmostEqual(s["time_rate"], 0.25)
        self.assertAlmostEqual(s["mean_net_R"], 0.8)
        # deviations -1.9,1.15,-0.4,1.15 -> SS 6.415, var 2.138333, se 0.731178, CI half 1.93*... 1.96*0.731178
        self.assertAlmostEqual(s["ci95"][0], -0.63311, places=3)
        self.assertAlmostEqual(s["ci95"][1], 2.23311, places=3)
        self.assertAlmostEqual(s["mean_net_usd_per_100"], 0.8)   # 0.8R * 1% * 100
        self.assertAlmostEqual(s["fee_per_stop_R"], 0.1)

    def test_usd_and_fee_scale_with_stop(self):
        tr = [{"kind": "target", "net_R": 2.0}, {"kind": "target", "net_R": 2.0}]
        s = G.cell_stats(tr, 0.003)
        self.assertAlmostEqual(s["mean_net_usd_per_100"], 2.0 * 0.3)
        self.assertAlmostEqual(s["fee_per_stop_R"], 0.001 / 0.003)
        self.assertEqual(s["ci95"], (2.0, 2.0))   # zero variance

    def test_empty_and_single(self):
        s = G.cell_stats([], 0.01)
        self.assertEqual(s["n"], 0)
        self.assertIsNone(s["mean_net_R"])
        self.assertIsNone(s["ci95"])
        s = G.cell_stats([{"kind": "stop", "net_R": -1.1}], 0.01)
        self.assertEqual(s["n"], 1)
        self.assertIsNone(s["ci95"])
        self.assertAlmostEqual(s["stop_rate"], 1.0)


class TestGrid(unittest.TestCase):
    def test_grid_size_and_members(self):
        g = G.bracket_grid()
        self.assertEqual(len(g), 6 * 3 * 3)
        self.assertEqual(sorted({c[0] for c in g}), [0.003, 0.005, 0.0075, 0.01, 0.015, 0.02])
        self.assertEqual(sorted({c[1] for c in g}), [1, 2, 3])
        self.assertEqual(sorted({c[2] for c in g}), [4, 8, 16])
        self.assertEqual(g[0], (0.003, 1, 4))
        self.assertEqual(g[1], (0.003, 1, 8))


class TestDecide(unittest.TestCase):
    def ok(self, **kw):
        a = dict(is_mean=0.2, oos_mean=0.1, oos_n=40, pbo=0.3)
        a.update(kw)
        return G.decide(**a)

    def test_pass(self):
        self.assertTrue(self.ok()[0])

    def test_each_failure(self):
        self.assertFalse(self.ok(oos_mean=-0.1)[0])
        self.assertFalse(self.ok(oos_mean=0.0)[0])
        self.assertFalse(self.ok(is_mean=-0.1)[0])
        self.assertFalse(self.ok(oos_n=29)[0])
        self.assertTrue(self.ok(oos_n=30)[0])
        self.assertFalse(self.ok(pbo=0.5)[0])
        self.assertFalse(self.ok(pbo=None)[0])
        self.assertFalse(self.ok(oos_mean=None)[0])

    def test_criteria_named(self):
        ok, crit = self.ok(pbo=0.9)
        self.assertFalse(ok)
        self.assertFalse(crit["pbo<0.5"])
        self.assertTrue(crit["oos_mean_net_R>0"])


class TestRunLayer(unittest.TestCase):
    """100 four-hour bars (16.7 days), n_is = 70. Every event's next bar is h=110 l=100, so in EVERY
    cell the target is hit on bar i+1 (stop never touched: lowest low 99.9 > 99.7). Net R of a cell =
    k - 0.0005/s (fee shrinks as the stop widens), best IS = stop 2%, 3R: 3 - 0.0005/0.02 = 2.975;
    tie over time -> first = 4."""

    def setUp(self):
        self.bars = flat(100)
        for i in (10, 20, 30, 69, 75, 80, 85):
            self.bars[i + 1] = bar(i + 1, 100.0, 110.0, 100.0)
        self.events = [{"i": i, "side": "long"} for i in (10, 20, 30, 69, 75, 80, 85)]
        self.res = G.run_layer("stub", self.bars, self.events, min_is=3, min_oos=3)

    def test_trials_reported(self):
        self.assertEqual(self.res["n_trials"], 54)

    def test_frozen_cell_chosen_on_is(self):
        self.assertEqual(self.res["chosen"], {"stop_pct": 2.0, "target_r": 3, "time_bars": 4})

    def test_is_purged_and_oos_counts(self):
        # event 69 exits at bar 70 >= n_is: dropped from IS (and it is not an OOS event, i < 70)
        self.assertEqual(self.res["n_is_bars"], 70)
        self.assertEqual(self.res["is"]["n"], 3)
        self.assertEqual(self.res["oos"]["n"], 3)
        self.assertAlmostEqual(self.res["is"]["mean_net_R"], 3 - 0.0005 / 0.02, places=6)
        self.assertAlmostEqual(self.res["oos"]["mean_net_R"], 3 - 0.0005 / 0.02, places=6)
        self.assertAlmostEqual(self.res["is"]["target_rate"], 1.0)

    def test_pbo_and_verdict_consistent(self):
        p = self.res["pbo"]
        self.assertTrue(p is None or 0.0 <= p <= 1.0)
        ok, _ = G.decide(self.res["is"]["mean_net_R"], self.res["oos"]["mean_net_R"], 3, p, min_oos=3)
        self.assertEqual(self.res["verdict"], "FROZEN" if ok else "DEFAULT")

    def test_all_cells_reported_with_fields(self):
        self.assertEqual(len(self.res["cells"]), 54)
        c = next(x for x in self.res["cells"] if (x["stop_pct"], x["target_r"], x["time_bars"]) == (1.0, 2, 4))
        for k in ("n", "stop_rate", "target_rate", "time_rate", "mean_net_R", "ci95",
                  "mean_net_usd_per_100", "fee_per_stop_R", "n_is", "n_oos"):
            self.assertIn(k, c)
        # stop 1%, 2R, every trade target: net 2 - 0.05 = 1.95; usd/100 = 1.95 * 1% * 100 = 1.95
        self.assertAlmostEqual(c["mean_net_R"], 1.95)
        self.assertAlmostEqual(c["mean_net_usd_per_100"], 1.95)
        self.assertEqual(c["n"], 6)   # 3 IS + 3 OOS; purged IS event excluded

    def test_default_cells_present(self):
        d = self.res["default_cells"]
        self.assertEqual(sorted(x["time_bars"] for x in d), [4, 8, 16])
        self.assertTrue(all(x["stop_pct"] == 1.0 and x["target_r"] == 2 for x in d))

    def test_no_events_default_stands(self):
        r = G.run_layer("none", self.bars, [], min_is=3, min_oos=3)
        self.assertEqual(r["verdict"], "DEFAULT")
        self.assertIsNone(r["chosen"])
        self.assertEqual(r["n_trials"], 54)

    def test_losing_layer_default_stands(self):
        # every event's next bar dives to 90: stop hit in every cell -> negative -> DEFAULT
        bars = flat(100)
        ev = []
        for i in (10, 20, 30, 40, 75, 80, 85):
            bars[i + 1] = bar(i + 1, 95.0, 100.0, 90.0)
            ev.append({"i": i, "side": "long"})
        r = G.run_layer("lose", bars, ev, min_is=3, min_oos=3)
        self.assertEqual(r["verdict"], "DEFAULT")


class TestReport(unittest.TestCase):
    def test_markdown_default_and_frozen_wording(self):
        bars = flat(100)
        r = G.run_layer("none", bars, [], min_is=3, min_oos=3)
        md = G.render_markdown([r])
        self.assertIn("trials: 54", md)
        self.assertIn("fixed 1%/2% default stands", md)
        self.assertNotIn("\r", md)


class TestCli(unittest.TestCase):
    def test_layer_registry_and_args(self):
        self.assertTrue({"c1", "c2", "c3"} <= set(G.LAYERS))
        a = G.parse_args(["--layer", "c3", "--layer", "c1"])
        self.assertEqual(a.layer, ["c3", "c1"])
        self.assertEqual(G.parse_args(["--layer", "all"]).layer, ["all"])
        self.assertEqual(G.resolve_layers(["all"]), sorted(G.LAYERS))


if __name__ == "__main__":
    unittest.main()
