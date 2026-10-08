"""
Tests for run_t055.py (staged as .new). Synthetic bars and stub layer functions injected
through run_candidate parameters; no network, no disk data, no layer-module imports.
Expected numbers are derived from the T055 runbook / FORMULAS.md sections 13-16 by hand.
"""

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
_name = "run_t055.py" if (HERE / "run_t055.py").exists() else "run_t055.py.new"
_spec = importlib.util.spec_from_file_location("run_t055", HERE / _name)
R = importlib.util.module_from_spec(_spec)
sys.modules["run_t055"] = R
_spec.loader.exec_module(R)

T0 = 1640995200000  # 2022-01-01 UTC
DAY = 86400000


def net_ref(side, p_in, p_out, t_in, t_out, funding, fee_rt=0.0010, slip_rt=0.0002):
    """FORMULAS.md section 13, written independently of trade_costs.py."""
    sgn = 1.0 if side == "long" else -1.0
    f = sum(r for (t, r) in funding if t_in < t <= t_out)
    return sgn * (p_out - p_in) / p_in - fee_rt - slip_rt - sgn * f


def make_bars(n, step_ms, slope=0.5, sign=1.0):
    bars = []
    for k in range(n):
        c = 100.0 + sign * slope * k + ((k * 7) % 5) * 0.1
        bars.append({"t": T0 + k * step_ms, "o": c, "h": c + 1, "l": c - 1, "c": c, "v": 1.0, "tbv": 0.5})
    return bars


def stub_events(bars, funding, side="long", step=3):
    return [{"i": i, "side": side} for i in range(0, len(bars), step)]


class TestSplitAndScore(unittest.TestCase):
    def test_split_70_30(self):
        b = make_bars(10, 60000)
        a, o, n = R.chronological_split(b)
        self.assertEqual((len(a), len(o), n), (7, 3, 7))
        self.assertEqual(a[-1]["t"] + 60000, o[0]["t"])

    def test_score_fixed_horizon_hand_numbers(self):
        bars = [{"t": T0 + k * 60000, "c": c} for k, c in enumerate([100.0, 101.0, 99.0, 100.0])]
        ev = [{"i": 0, "side": "long"}, {"i": 1, "side": "short"}, {"i": 3, "side": "long"}]
        tr = R.score_trades(ev, bars, 1, 60000, [], net_ref)
        self.assertEqual(len(tr), 2)  # i=3 has no bar at i+1
        self.assertAlmostEqual(tr[0]["gross"], 0.01)
        self.assertAlmostEqual(tr[0]["net"], 0.01 - 0.0012)
        self.assertAlmostEqual(tr[1]["gross"], -1 * (99 - 101) / 101)
        self.assertAlmostEqual(tr[1]["net"], 2 / 101 - 0.0012)

    def test_funding_window_uses_bar_close_instants(self):
        # entry instant = t_i + bar_ms (excluded), exit instant = t_j + bar_ms (included)
        bars = [{"t": T0 + k * 60000, "c": 100.0} for k in range(3)]
        entry_inst = T0 + 60000
        exit_inst = T0 + 2 * 60000
        funding = [(entry_inst, 0.5), (exit_inst, 0.001)]
        tr = R.score_trades([{"i": 0, "side": "long"}], bars, 1, 60000, funding, net_ref)
        self.assertAlmostEqual(tr[0]["net"], -0.0012 - 0.001)
        tr = R.score_trades([{"i": 0, "side": "short"}], bars, 1, 60000, funding, net_ref)
        self.assertAlmostEqual(tr[0]["net"], -0.0012 + 0.001)

    def test_session_horizon_exits_at_session_end(self):
        bars = []
        for k in range(2 * 288):
            c = 100.0 if k < 288 else 110.0
            bars.append({"t": T0 + k * 300000, "c": c})
        # T0 is a UTC midnight; session 0 ends at T0 + DAY, i.e. bar index 287 closes then
        ev = [{"i": 6, "side": "long", "session_start": T0}]
        tr = R.score_trades(ev, bars, "session", 300000, [], net_ref, 0.0, 0.0)
        self.assertEqual(len(tr), 1)
        self.assertAlmostEqual(tr[0]["gross"], 0.0)  # bar 287 close is still 100
        # event with no session-end bar in the data is dropped
        ev2 = [{"i": 300, "side": "long", "session_start": T0 + DAY + 3600000}]
        self.assertEqual(R.score_trades(ev2, bars, "session", 300000, [], net_ref), [])

    def test_summarize(self):
        tr = [{"gross": 0.02, "net": 0.01}, {"gross": -0.01, "net": -0.02}, {"gross": 0.03, "net": 0.02}]
        s = R.summarize(tr)
        self.assertEqual(s["n"], 3)
        self.assertAlmostEqual(s["mean_gross"], 0.04 / 3)
        self.assertAlmostEqual(s["mean_net"], 0.01 / 3)
        self.assertAlmostEqual(s["hit_net"], 2 / 3)
        self.assertEqual(R.summarize([])["mean_net"], None)

    def test_daily_column_zero_fills_and_averages(self):
        bars = [{"t": T0 + d * DAY, "c": 1.0} for d in range(4)]
        tr = [{"t": T0, "net": 0.02}, {"t": T0 + 1000, "net": 0.04}, {"t": T0 + 2 * DAY, "net": -0.01}]
        self.assertEqual(R.daily_matrix_column(tr, bars), [0.03, 0.0, -0.01, 0.0])

    def test_pbo_none_when_too_short_or_single_variant(self):
        self.assertIsNone(R.compute_pbo([[0.1] * 40], 16))
        self.assertIsNone(R.compute_pbo([[0.1] * 3, [0.2] * 3], 16))


class TestRunCandidate(unittest.TestCase):
    def run_c(self, cand, bars, **kw):
        kw.setdefault("events_fn", stub_events)
        kw.setdefault("grid", [{"side": "long"}, {"side": "short"}])
        kw.setdefault("horizons", (1,))
        kw.setdefault("bar_ms", 2 * DAY)
        kw.setdefault("net_return", net_ref)
        kw.setdefault("fee_rt", 0.0)
        kw.setdefault("slip_rt", 0.0)
        kw.setdefault("pbo_s", 8)
        return R.run_candidate(cand, bars, [], **kw)

    def test_is_choice_and_oos_pass_on_rising_market(self):
        bars = make_bars(400, 2 * DAY)  # rising; long wins, short loses; OOS spans 2023 and 2024
        r = self.run_c("c3", bars)
        self.assertEqual(r["chosen"]["params"], {"side": "long"})
        self.assertGreater(r["is"]["mean_net"], 0)
        self.assertGreater(r["oos"]["mean_net"], 0)
        self.assertGreaterEqual(r["oos"]["n"], 30)
        self.assertEqual(r["n_variants"], 2)
        self.assertIsNotNone(r["pbo"])
        self.assertLess(r["pbo"], 0.5)
        self.assertGreaterEqual(len(r["oos_years"]), 2)
        self.assertTrue(all(r["criteria"].values()), r["criteria"])
        self.assertEqual(r["verdict"], "PASS")

    def test_c1_has_no_year_criterion_and_is_provisional(self):
        r = self.run_c("c1", make_bars(400, 2 * DAY))
        self.assertNotIn(">=2_positive_oos_years", r["criteria"])
        self.assertTrue(r["provisional"])

    def test_year_criterion_fails_inside_one_year_for_c2_c3(self):
        bars = make_bars(400, 6 * 3600000)  # 100 days: a single OOS year
        r = self.run_c("c3", bars, bar_ms=6 * 3600000)
        self.assertFalse(r["criteria"][">=2_positive_oos_years"])
        self.assertEqual(r["verdict"], "FAIL")
        self.assertTrue(r["criteria"]["oos_mean_net>0"])

    def test_falling_market_with_long_only_grid_fails(self):
        bars = make_bars(400, 2 * DAY, slope=0.2, sign=-1.0)
        r = self.run_c("c1", bars, grid=[{"side": "long"}, {"side": "long", "step": 4}])
        self.assertEqual(r["verdict"], "FAIL")
        self.assertFalse(r["criteria"]["oos_mean_net>0"])
        self.assertFalse(r["criteria"]["same_sign_is_oos"] and r["criteria"]["oos_mean_net>0"])

    def test_costs_are_charged(self):
        bars = make_bars(400, 2 * DAY)
        r0 = self.run_c("c1", bars, grid=[{"side": "long"}])
        r1 = self.run_c("c1", bars, grid=[{"side": "long"}], fee_rt=0.0010, slip_rt=0.0002)
        self.assertAlmostEqual(r0["oos"]["mean_net"] - r1["oos"]["mean_net"], 0.0012)
        self.assertAlmostEqual(r1["oos"]["mean_gross"], r0["oos"]["mean_gross"])

    def test_runner_gross_matches_own_gross(self):
        r = self.run_c("c1", make_bars(400, 2 * DAY), grid=[{"side": "long"}])
        self.assertAlmostEqual(r["runner_gross_oos"], r["oos"]["mean_gross"])

    def test_grid_search_never_sees_oos_bars(self):
        seen = []

        def spy(bars, funding, side="long"):
            seen.append(len(bars))
            return stub_events(bars, funding, side)

        self.run_c("c1", make_bars(400, 2 * DAY), events_fn=spy, grid=[{"side": "long"}])
        self.assertEqual(seen, [280, 120])  # IS pass, then one OOS pass on OOS bars only

    def test_erroring_param_is_recorded_not_chosen(self):
        def bad(bars, funding, side="long"):
            if side == "short":
                raise ValueError("boom")
            return stub_events(bars, funding, side)

        r = self.run_c("c1", make_bars(400, 2 * DAY), events_fn=bad)
        self.assertEqual(r["chosen"]["params"], {"side": "long"})
        self.assertTrue(any(g["error"] == "boom" for g in r["grid"]))

    def test_no_qualifying_variant_fails_cleanly(self):
        r = self.run_c("c1", make_bars(400, 2 * DAY), events_fn=lambda b, f, **p: [])
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIsNone(r["chosen"])

    def test_funding_is_passed_to_cost_function(self):
        got = []

        def spy(side, p_in, p_out, t_in, t_out, funding, fee_rt, slip_rt):
            got.append(funding)
            return 0.0

        f = [(T0 + 5 * DAY, 0.0001)]
        R.run_candidate("c1", make_bars(50, 2 * DAY), f, events_fn=stub_events, grid=[{"side": "long"}],
                        horizons=(1,), bar_ms=2 * DAY, net_return=spy)
        withf = [x for x in got if x]  # the fee-only shadow call passes []
        self.assertTrue(withf and all(x is f or x == f for x in withf))


class TestFundingForC2(unittest.TestCase):
    """Gap closure: C2/C3 holds cross 00/08/16 UTC funding times; funding must reach the cost model."""

    def test_all_candidates_load_funding(self):
        for c in ("c1", "c2", "c3"):
            self.assertTrue(R.CANDIDATES[c]["use_funding"], c)

    def test_load_data_passes_funding_for_c2(self):
        import MyTradingSys.backtest.bt.bt_data as bd
        old = (bd.load_klines, bd.load_funding)
        bd.load_klines = lambda root: [{"t": T0, "o": 1, "h": 1, "l": 1, "c": 1, "v": 1, "tbv": 0}]
        bd.load_funding = lambda root: [(T0 + 8 * 3600000, 0.0001)]
        try:
            _bars, f = R.load_data("c2", "r1", "r2", "1m")
        finally:
            bd.load_klines, bd.load_funding = old
        self.assertEqual(f, [(T0 + 8 * 3600000, 0.0001)])

    def test_load_data_clips_bars_to_funding_coverage(self):
        # Funding archive ends before the klines do (funding to 2026-08-31, klines to 2026-09-26): a hold past the
        # last funding record raises in trade_costs.funding_paid, so bars whose close is after the last record are dropped.
        import MyTradingSys.backtest.bt.bt_data as bd
        old = (bd.load_klines, bd.load_funding)
        last_f = T0 + 8 * 3600000
        bd.load_klines = lambda root: [{"t": T0 + i * 60000, "o": 1, "h": 1, "l": 1, "c": 1, "v": 1, "tbv": 0}
                                       for i in range(0, 8 * 60 + 30)]
        bd.load_funding = lambda root: [(T0, 0.0001), (last_f, 0.0001)]
        try:
            bars, f = R.load_data("c2", "r1", "r2", "1m")
        finally:
            bd.load_klines, bd.load_funding = old
        self.assertEqual(f[-1][0], last_f)
        self.assertTrue(bars)
        self.assertTrue(all(b["t"] + 60000 <= last_f for b in bars))
        self.assertEqual(bars[-1]["t"] + 60000, last_f)

    def test_session_hold_crossing_funding_times_section13_worked_example(self):
        # FORMULAS.md s13: long 100 -> 101, funding 8h 0.0001 and 16h 0.0003, t_in=0, t_out=16h:
        # net = 0.01 - 0.0010 - 0.0002 - 0.0004 = 0.0084 ; short 100 -> 99: 0.01 - 0.0012 + 0.0004 = 0.0092
        bm = 300000
        bars = [{"t": T0 - bm, "c": 100.0}, {"t": T0 + 16 * 3600000 - bm, "c": 101.0}]
        funding = [(T0 - 8 * 3600000, 0.0), (T0 + 8 * 3600000, 0.0001), (T0 + 16 * 3600000, 0.0003)]
        tr = R.score_trades([{"i": 0, "side": "long"}], bars, 1, bm, funding, R._cost_fn())
        self.assertAlmostEqual(tr[0]["net"], 0.0084, places=9)
        self.assertAlmostEqual(tr[0]["net_nofund"], 0.0088, places=9)
        self.assertTrue(tr[0]["funded"])
        bars[1]["c"] = 99.0
        tr = R.score_trades([{"i": 0, "side": "short"}], bars, 1, bm, funding, R._cost_fn())
        self.assertAlmostEqual(tr[0]["net"], 0.0092, places=9)
        # B103: hold outside the funding history fails closed (was: scored fee-only, funded=False)
        with self.assertRaises(ValueError):
            R.score_trades([{"i": 0, "side": "short"}], bars, 1, bm, [(T0 + 99 * DAY, 0.1)], R._cost_fn())


class TestSpecsAndReport(unittest.TestCase):
    def test_c1_grid_matches_runbook(self):
        g = R.c1_grid()
        self.assertEqual(len(g), 3 * 2 * 3 * 2)
        self.assertEqual({x["lookback"] for x in g}, {60, 90, 180})
        self.assertEqual({x["n"] for x in g}, {20, 50})
        self.assertEqual({(x["hi"], x["lo"]) for x in g}, {(0.90, 0.10), (0.95, 0.05), (0.99, 0.01)})
        self.assertEqual({x["use_divergence"] for x in g}, {True, False})
        self.assertEqual(R.CANDIDATES["c1"]["horizons"], (4, 16, 48))

    def test_c2_grid_matches_runbook(self):
        g = R.c2_grid(5)
        self.assertEqual(len(g), 16)
        self.assertEqual({x["first_min"] for x in g}, {30, 60})
        self.assertEqual({x["session_start_min"] for x in g}, {0, "ny"})
        self.assertEqual({x["min_abs"] for x in g}, {0.0, 0.001})
        for x in g:
            self.assertIn(x["entry_min"], (x["first_min"], 1410))
            self.assertEqual(x["bar_min"], 5)
        self.assertEqual(R.CANDIDATES["c2"]["horizons"], ("session",))

    def test_c3_grid_matches_runbook(self):
        g = R.c3_grid()
        self.assertEqual({(x["lead_minutes"], x["side"]) for x in g},
                         {(1, "long"), (1, "short"), (2, "long"), (2, "short")})
        self.assertEqual(R.CANDIDATES["c3"]["horizons"], (1, 2, 5))
        self.assertEqual(R.CANDIDATES["c3"]["tf"], "1m")

    def test_markdown_contains_required_fields(self):
        r = TestRunCandidate().run_c("c3", make_bars(400, 2 * DAY))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "sub" / "T055_BT_c3.md"
            R.write_markdown(r, p)
            txt = p.read_text(encoding="utf-8")
            self.assertNotIn("\r", txt)
        for s in ("Verdict: **PASS**", "| IS |", "| OOS |", "gross mean", "net mean", "hit (net)",
                  "PBO", "oos_n>=30", "pbo<0.5", "same_sign_is_oos", "OOS by calendar year"):
            self.assertIn(s, txt)

    def test_markdown_for_no_result(self):
        r = TestRunCandidate().run_c("c1", make_bars(400, 2 * DAY), events_fn=lambda b, f, **p: [])
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.md"
            R.write_markdown(r, p)
            self.assertIn("No result", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
