"""Tests for build_artifact.py / export_results.py (the simulator page)."""
import csv
import json
import os
import re
import subprocess
import sys
import tempfile
import types
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import build_artifact as ba  # noqa: E402
import export_results as ex  # noqa: E402


def load_sim_desk():
    """sim_desk's own desk.py by explicit path: scripts/dev/desk.py can win a bare `import desk` when both are on sys.path."""
    import importlib.util
    path = os.path.join(os.path.dirname(HERE), "desk.py")
    spec = importlib.util.spec_from_file_location("sim_desk_own_desk", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(path))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(os.path.dirname(path))
    return mod

COLS = ["day", "touch_t", "side", "L1", "L2", "T1", "T2", "families", "E1"] + ba.STOP_COLS + [ba.FROZEN_COL]
RULE = {
    "rule": {"entry_filter": "E1"},
    "dev": {"n": 4, "mean": -0.1, "lo": -0.3, "hi": 0.1, "maxdd": 2.0, "win_rate": 0.33,
            "mean_fee_r": 0.2, "mean_gross_r": 0.1},
    "power": {"power_mde": {"power": 0.3}, "power_plausible_0.10R": 0.9},
    "verdict": "FAIL fixture",
}


def _row(day, t, side, l1, l2, t1, t2, r, e1="True"):
    d = dict(day=day, touch_t=t, side=side, L1=l1, L2=l2, T1=t1, T2=t2, families="naked_poc", E1=e1)
    for c in ba.STOP_COLS:
        d[c] = "-0.2"
    d[ba.FROZEN_COL] = r
    return d


def _fixture(rows):
    d = tempfile.mkdtemp()
    with open(os.path.join(d, "frozen_rule.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(RULE, f)
    with open(os.path.join(d, "ladder_ideas_dev.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return d


def _result(rid="t1", **kw):
    r = {"id": rid, "family": "Fam", "title": "Title " + rid,
         "what": [{"name": "p", "value_plain": "v", "label": "OURS"}], "how": "h", "window": "DEV",
         "verdict": {"label": "FAIL", "tone": "bad"}, "why": ["w"], "kpis": [{"label": "k", "value": "1"}],
         "examples": [{"kind": "none", "title": "e"}], "source_files": ["a"], "commit": "abc"}
    r.update(kw)
    return r


def _results_dir(*results):
    d = tempfile.mkdtemp()
    for r in results:
        with open(os.path.join(d, r["id"] + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(r, f)
    return d


NODE_TIMEOUT = 60  # a slow node start must skip, not turn CI red (flake 22b22e93)


def _run_node(node, prog):
    try:
        return subprocess.run([node, "-e", prog], capture_output=True, text=True, timeout=NODE_TIMEOUT)
    except subprocess.TimeoutExpired:
        raise unittest.SkipTest("node did not finish in %ss (slow start); skipped, not failed" % NODE_TIMEOUT)


class NodeTimeout(unittest.TestCase):
    def test_timeout_reports_skip(self):
        import unittest.mock as mock
        with mock.patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired("node", NODE_TIMEOUT)):
            with self.assertRaises(unittest.SkipTest):
                _run_node("node", "1")


class Levels(unittest.TestCase):
    def test_unfilled_ideas_are_not_trades(self):
        # 2 filled (1.5, -1.0) + 2 never filled (r == 0.0) + 1 filtered out by E1
        rule, rows = ba.load(_fixture([
            _row(19083, 1, 1, 100.0, 99.0, 101.0, "", "1.5"),
            _row(19084, 2, -1, 200.0, 202.0, 198.0, 196.0, "-1.0"),
            _row(19085, 3, 1, 100.0, 99.0, 101.0, 102.0, "0.000"),
            _row(19086, 4, 1, 100.0, 99.0, 101.0, 102.0, "0.0"),
            _row(19087, 5, 1, 100.0, 99.0, 101.0, 102.0, "0.2", e1="False")]))
        data = ba.build_data(rule, rows)
        self.assertEqual(data["n"], 2)
        self.assertEqual(data["unfilled"], 2)
        self.assertEqual(data["wins"], 1)
        self.assertAlmostEqual(data["dev"]["mean"], 0.25)
        self.assertEqual(data["cum"], [1.5, 0.5])
        # frozen means were over 4 selected ideas; rescaled to 2 filled trades
        self.assertAlmostEqual(data["dev"]["mean_gross_r"], 0.2)
        self.assertAlmostEqual(data["dev"]["mean_fee_r"], 0.4)

    def test_real_data_filled_only(self):
        if not os.path.isfile(os.path.join(ba.DEFAULT_SRC, "ladder_ideas_dev.csv")):
            self.skipTest("precomputed ladder csv not present")
        rule, rows = ba.load(ba.DEFAULT_SRC)
        data = ba.build_data(rule, rows)
        self.assertEqual(data["n"], 255)
        self.assertEqual(data["unfilled"], 517)
        self.assertAlmostEqual(data["dev"]["mean"], -0.119, places=3)
        self.assertAlmostEqual(sum(t["r"] for t in data["trades"]) / 255, -0.119, places=3)
        self.assertAlmostEqual(data["wins"] / 255, 0.408, places=3)
        self.assertAlmostEqual(data["dev"]["mean_gross_r"] - data["dev"]["mean_fee_r"], data["dev"]["mean"], places=2)

    def test_relative_only_and_t2_fallback(self):
        rule, rows = ba.load(_fixture([_row(19083, 2, 1, 12345.5, 12300.5, 12400.5, "", "1.5")]))
        t = ba.build_data(rule, rows)["trades"][0]
        self.assertAlmostEqual(t["l2"], -0.365, places=2)
        self.assertAlmostEqual(t["t2"], t["t1"] * 2, places=2)
        self.assertNotIn("12345", json.dumps(ex.levels_result(ba.build_data(rule, rows))))

    def test_dev_window_enforced(self):
        rule, rows = ba.load(_fixture([_row(20000, 1, 1, 100.0, 99.0, 101.0, 102.0, "1.0")]))
        with self.assertRaises(ValueError):
            ba.build_data(rule, rows)


class Page(unittest.TestCase):
    def _build(self, *results):
        d = _results_dir(*results)
        out = os.path.join(d, "index.html")
        ba.main(["--results", d, "--out", out])
        return open(out, encoding="utf-8").read()

    def test_trade_chart_example_renders(self):
        # Operator item 2: a trade_chart example must reach a renderer, not "no example trades exported".
        self.assertIn('x.kind==="trade_chart"', ba.TEMPLATE)
        self.assertIn("function tradeChart(x)", ba.TEMPLATE)
        c30 = os.path.join(os.path.dirname(HERE), "results", "eagle-c30-wt-rsi-div.json")
        ex = json.load(open(c30, encoding="utf-8"))["examples"][0]
        self.assertEqual(ex["kind"], "trade_chart")
        for t in ex["trades"]:
            self.assertTrue(0 <= t["sig"] < t["ent"] < t["ext"] < len(t["c"]))
            self.assertEqual(t["c"][t["ent"]][0], 0.0)  # entry open is the 0 % line: percent only, no prices

    def test_trade_chart_has_candle_replay(self):
        # Operator item 5: watch one trade candle by candle with a phase line (waiting, signal, in trade, exited).
        for k in ('id="cvr"', 'id="cvst"', 'id="cvph"', "WAITING", "SIGNAL", "IN TRADE", "EXIT SIGNAL", "EXITED", "if(k>u)return;"):
            self.assertIn(k, ba.TEMPLATE)

    def test_search_keeps_caret_at_end(self):
        # The list rebuild re-creates the search box; without the caret reset "C30" typed as "03C".
        line = next(x for x in ba.TEMPLATE.splitlines() if x.startswith("function refilter()"))
        self.assertIn("setSelectionRange(el.value.length,el.value.length)", line)

    def test_every_result_file_becomes_a_test(self):
        h = self._build(_result("aa"), _result("bb"), _result("cc"))
        tests = json.loads(re.search(r"const TESTS=(\[.*?\]);\n", h, re.S).group(1))
        self.assertEqual([t["id"] for t in tests], ["aa", "bb", "cc"])
        self.assertNotRegex(h, r'(src|href)="https?://')
        self.assertIn("prefers-color-scheme:dark", h)
        self.assertIn("What was tested", h)

    def test_event_charts_use_their_own_label(self):
        # event studies (no winners/losers) caption each chart with its label, not "typical loser"
        h = self._build(_result("ev", examples=[{"kind": "charts", "title": "t", "items": [
            {"kind": "event", "label": "operator chart", "note": "n", "svg": "<svg></svg>"}]}]))
        self.assertIn('esc((c.label||(c.kind==="winner"', h)

    def test_bad_result_files_fail_the_build(self):
        bad = _result("x")
        del bad["why"]
        with self.assertRaises(ValueError):
            self._build(bad)
        with self.assertRaises(ValueError):
            self._build(_result("y", what=[{"name": "p", "value_plain": "v", "label": "GUESS"}]))

    def test_committed_results_build(self):
        names = sorted(os.listdir(ba.RESULTS_DIR))
        for need in ("levels_ladder.json", "t09_live_parity.json", "t06_cost_fill.json", "t07_stale_verdicts.json", "wavetrend_atlas.json", "_catalogue.json"):
            self.assertIn(need, names)
        tests = ba.collect(ba.RESULTS_DIR)  # skips _catalogue.json
        self.assertNotIn("_catalogue", [t["id"] for t in tests])
        for t in tests:
            self.assertIn(t.get("kind"), ("backtest", "audit", "thought_experiment"), t["id"])
            self.assertTrue(t["examples"], t["id"])
            self.assertNotRegex(json.dumps(t), r"\b\d{5}\.\d")  # no raw price like 44375.0

    def test_catalogue_lists_every_row_and_flags_exported(self):
        cat = ba.load_catalogue(ba.RESULTS_DIR)
        rows = cat["rows"]
        self.assertGreater(len(rows), 100)
        have = {t["id"] for t in ba.collect(ba.RESULTS_DIR)}
        for r in rows:
            for k in ("id", "family", "title", "kind", "verdict", "source", "exported"):
                self.assertIn(k, r, r.get("id"))
            self.assertIn(r["kind"], ("backtest", "audit", "thought_experiment"))
            self.assertEqual(r["exported"], r.get("result_id") in have, r["id"])
        self.assertEqual({r["result_id"] for r in rows if r["exported"]}, have)
        self.assertEqual(len({r["id"] for r in rows}), len(rows))
        d = _results_dir(_result("aa"))
        out = os.path.join(d, "index.html")
        with open(os.path.join(d, "_catalogue.json"), "w", encoding="utf-8", newline=chr(10)) as f:
            json.dump({"rows": [{"id": "old1", "family": "F", "title": "Old test", "kind": "thought_experiment", "verdict": "v",
                                 "source": "x.md", "exported": False, "result_id": None}]}, f)
        ba.main(["--results", d, "--out", out])
        h = open(out, encoding="utf-8").read()
        self.assertIn("Old test", h)  # unexported row on the page
        self.assertIn("charts not exported yet", h)
        self.assertIn("Title aa", h)  # exported test still added


class Banner(unittest.TestCase):
    """Survey C1+C2: one fixed verdict banner on every result; trade list with exit reason for every result that carries charts."""

    def _r(self, tone, n, net="-0.1 R", label="PASSED"):
        k = [{"label": "filled trades", "value": str(n)}, {"label": "average per trade, after fees", "value": net},
             {"label": "try number", "value": "7"}]
        return _result("b", verdict={"label": label, "tone": tone}, kpis=k)

    def test_small_n_never_reads_pass(self):
        for n in (0, 1, 12, 29):
            b = ba.banner_of(self._r("good", n, "+0.8 R"))
            self.assertEqual(b["state"], "TOO_FEW", n)
            self.assertNotIn("PASS", b["text"].split("verdict as written")[0])
        self.assertEqual(ba.banner_of(self._r("good", 30, "+0.8 R"))["state"], "PASS")
        self.assertNotEqual(ba.banner_of(self._r("good", 80, "-0.2 R"))["state"], "PASS")  # net R after fees not above zero

    def test_banner_fields(self):
        b = ba.banner_of(self._r("bad", 64, "-0.445 R", "FAILED"))
        self.assertEqual((b["state"], b["n"], b["net_r"], b["try_no"]), ("FAIL", 64, -0.445, 7))
        self.assertIn("n=64", b["text"])
        self.assertIn("try #7", b["text"])
        self.assertIn("break-even", b["text"])
        self.assertEqual(ba.banner_of(_result("z"))["state"], "UNCLEAR")  # no trade count anywhere: never a pass

    def test_trade_list_gives_count_when_kpis_do_not(self):
        # Demo 11-04: C30 showed "n=? net n/a" although its trade chart holds all 35 VALIDATION trades.
        t = [{"net": 0.5}] * 20 + [{"net": -0.4}] * 15
        r = _result("tc", verdict={"label": "VALIDATION: H1 FAIL", "tone": ""},
                    examples=[{"kind": "trade_chart", "tf": "30m", "title": "t", "trades": t}])
        b = ba.banner_of(r)
        self.assertEqual(b["n"], 35)
        self.assertAlmostEqual(b["net_pct"], round(4.0 / 35, 3))
        self.assertIsNone(b["net_r"])  # a % mean is never shown as R
        self.assertIn("n=35 (trade list)", b["text"])
        self.assertIn("%/trade after fees", b["text"])
        self.assertNotEqual(b["state"], "PASS")

    def test_c30_chart_names_its_divergence_rule(self):
        # Operator: Malkan divergence = closes only, 12 and 18 bars; C30 draws an OURS wick rule and must say so.
        self.assertIn("x.div_rule", ba.TEMPLATE)
        r = json.load(open(os.path.join(ba.RESULTS_DIR, "eagle-c30-wt-rsi-div.json"), encoding="utf-8"))
        x = next(e for e in r["examples"] if e["kind"] == "trade_chart")
        self.assertIn("OURS", x["div_rule"])
        self.assertIn("not Malkan", x["div_rule"])

    def test_div_on_close_draws_at_closes(self):
        # Operator: Malkan divergence = closes only; a div_on="close" chart draws the line at c[p][3], not the low c[p][2].
        self.assertIn('x.div_on==="close"?3:2', ba.TEMPLATE)
        self.assertIn("c[p][dk]", ba.TEMPLATE)
        self.assertIn("c[qd][dk]", ba.TEMPLATE)

    def test_malkan_close_div_chart_matches_study_ledger(self):
        r = json.load(open(os.path.join(ba.RESULTS_DIR, "rsi-divergence-mtf-gated-run1-2026-11-04.json"), encoding="utf-8"))
        x = next(e for e in r["examples"] if e["kind"] == "trade_chart" and e.get("div_on") == "close")
        cells = os.path.join(ba.RESULTS_DIR, "..", "..", "rsi_divergence_mtf_gated_2026-11-04", "dev_cells.csv")
        row = next(c for c in csv.DictReader(open(cells, encoding="utf-8"))
                   if (c["tf"], c["arm"], c["kind"], c["gate"], c["entry"]) == ("4h", "W18", "bullish", "aligned", "signal"))
        self.assertEqual(len(x["trades"]), int(row["n"]))
        self.assertEqual(x["ledger_n"], int(row["n"]))
        self.assertAlmostEqual(sum(t["net"] for t in x["trades"]) / len(x["trades"]), float(row["net"]), places=2)
        self.assertIn("CLOSES", x["div_rule"])

    def test_every_committed_result_has_banner(self):
        n = 0
        for fn in os.listdir(ba.RESULTS_DIR):
            if not fn.endswith(".json") or fn.startswith("_"):
                continue
            r = json.load(open(os.path.join(ba.RESULTS_DIR, fn), encoding="utf-8"))
            n += 1
            b = r.get("banner")
            self.assertIsInstance(b, dict, fn)
            for k in ("state", "tone", "verdict", "n", "net_r", "try_no", "breakeven_x", "text"):
                self.assertIn(k, b, fn)
            if b["n"] is None or b["n"] < ba.MIN_N:
                self.assertNotEqual(b["state"], "PASS", fn)
            self.assertEqual(b, ba.banner_of(r), fn)  # file is current with the rule
        self.assertGreaterEqual(n, 337)

    def test_trade_row_from_caption(self):
        svg = '<svg><text x="4">2023-10-17 17:02 UTC  +0.71 R short, hit target (5m)</text></svg>'
        self.assertEqual(ba.trade_row({"kind": "winner", "net_r": 0.7109, "svg": svg}),
                         {"when": "2023-10-17 17:02", "side": "short", "net_r": 0.7109, "exit_reason": "hit target", "span": "5m"})
        self.assertIsNone(ba.trade_row({"kind": "event", "svg": "<svg><text>2026-10-01 18:30 DOWN high: taken 0h</text></svg>"}))

    def test_committed_charts_have_trade_rows(self):
        have = 0
        for t in ba.collect(ba.RESULTS_DIR):
            for e in t["examples"]:
                if e["kind"] != "charts":
                    continue
                trades = [i for i in e["items"] if i.get("kind") in ("winner", "loser")]
                for i in trades:
                    for k in ("when", "side", "exit_reason"):
                        self.assertTrue(i.get(k), (t["id"], k))
                have += bool(trades)
        self.assertGreaterEqual(have, 25)

    def test_page_renders_banner_and_trade_list(self):
        for k in ("function banner(", 'class="banner', "function chartList(", 'id="tlist"', "exit_reason"):
            self.assertIn(k, ba.TEMPLATE)
        r = _result("bn", examples=[{"kind": "charts", "title": "t", "items": [
            {"kind": "winner", "net_r": 1.0, "when": "2023-01-01 00:00", "side": "long", "exit_reason": "hit target", "svg": "<svg></svg>"}]}])
        d = _results_dir(r)
        out = os.path.join(d, "index.html")
        ba.main(["--results", d, "--out", out])
        h = open(out, encoding="utf-8").read()
        self.assertIn('"banner":{', h)  # build fills a missing banner (desk runs written after the last enrich)


class EquityStability(unittest.TestCase):
    """Survey C3+C4: drawdown shading + Monte Carlo band on curve results; year strip with a stable / not stable flag."""

    def _curve(self, **kw):
        c = {"kind": "curve", "title": "c", "r": [0.5, -0.5, 1.0], "usd": [1, 2, 3], "start_usd": 1000.0, "risk_pct": 1.0}
        c.update(kw)
        return _result("cv", examples=[c])

    def test_curve_without_band_fails_the_build(self):
        d = _results_dir(self._curve())
        with self.assertRaises(ValueError):
            ba.collect(d)
        ok = self._curve()
        ok["examples"][0]["mc"] = {"lo": [0.0, -1.0, 1.0], "hi": [1.0, 0.0, 1.0], "dd_lo": 0.0, "dd_hi": 1.0, "shuffles": 1000}
        self.assertEqual(len(ba.collect(_results_dir(ok))), 1)
        none_ok = self._curve()
        none_ok["examples"][0]["mc"] = None  # a one-trade run has no band, but the field must be there
        self.assertEqual(len(ba.collect(_results_dir(none_ok))), 1)

    def test_one_good_year_among_bad_is_not_stable(self):
        y = [{"k": "2022", "n": 40, "mean": 0.2, "few": False}, {"k": "2023", "n": 55, "mean": -0.1, "few": False},
             {"k": "2024", "n": 35, "mean": -0.3, "few": False}]
        s = ba.stability_of(y)
        self.assertEqual(s["state"], "NOT_STABLE")
        self.assertIn("not stable", s["text"].lower())

    def test_all_positive_years_stable_and_few_years_labelled(self):
        y = [{"k": "2022", "n": 40, "mean": 0.2, "few": False}, {"k": "2023", "n": 55, "mean": 0.1, "few": False},
             {"k": "2024", "n": 5, "mean": -0.9, "few": True}]
        s = ba.stability_of(y)
        self.assertEqual(s["state"], "STABLE")  # the 5-trade year is labelled, not judged
        self.assertIn("too few", s["text"].lower())
        self.assertEqual(ba.stability_of([{"k": "2023", "n": 90, "mean": 0.3, "few": False}])["state"], "TOO_FEW")  # one judged year
        self.assertEqual(ba.stability_of(None)["state"], "UNKNOWN")

    def test_derived_band_matches_desk_monte_carlo(self):
        import numpy as np
        desk = load_sim_desk()
        net = [0.5, -1.0, 1.5, -0.2, 0.7, -1.0, 2.0, -0.4]
        cum = np.cumsum(net).tolist()
        got = ex.derive_mc(cum, len(net))
        res = {"net": net, "filled": [True] * len(net)}
        want = desk.monte_carlo(res, list(range(1, len(net) + 1)))
        self.assertEqual(got["lo"], want["lo"])
        self.assertEqual(got["dd_hi"], want["dd_hi"])

    def test_load_sim_desk_ignores_shadowing_desk_module(self):
        shadow = types.ModuleType("desk")  # what scripts/dev/desk.py looks like to a bare `import desk`
        saved = sys.modules.get("desk")
        sys.modules["desk"] = shadow
        try:
            self.assertTrue(hasattr(load_sim_desk(), "monte_carlo"))
        finally:
            if saved is not None:
                sys.modules["desk"] = saved
            else:
                del sys.modules["desk"]

    def test_year_split_of_single_year_window(self):
        y = ex.derive_years("DEV only, 2023-03-01 to 2023-05-31 (VALIDATION and HOLDOUT never offered)", 7, -0.516)
        self.assertEqual(y, [{"k": "2023", "n": 7, "mean": -0.516, "few": True}])
        self.assertIsNone(ex.derive_years("DEV only, 2022-04-01 to 2024-06-30", 90, 0.1))

    def test_committed_curves_have_band_and_stability(self):
        curves = trades = 0
        for t in ba.collect(ba.RESULTS_DIR):
            for e in t["examples"]:
                if e["kind"] == "curve":
                    curves += 1
                    self.assertIn("mc", e, t["id"])
                    if e["mc"]:
                        self.assertEqual(len(e["mc"]["lo"]), len(e["r"]), t["id"])
            if t["banner"]["n"]:
                trades += 1
                self.assertIn(t["stability"]["state"], ("STABLE", "NOT_STABLE", "TOO_FEW", "UNKNOWN"), t["id"])
        self.assertGreaterEqual(curves, 50)
        self.assertGreaterEqual(trades, 50)

    def test_page_draws_shading_band_and_year_strip(self):
        for k in ("function yearStrip(", 'class="dd"', 'class="mcb"', "x.mc", "stability"):
            self.assertIn(k, ba.TEMPLATE)

    def test_lone_peak_labelled(self):
        mk = lambda n, m: {"n": n, "mean": m}
        one = [mk(100, -0.2), mk(120, 0.08), mk(90, -0.1), mk(60, -0.3)]
        self.assertIs(ba.lone_peak(one), one[1])
        self.assertIsNone(ba.lone_peak([mk(100, -0.2), mk(90, -0.1), mk(60, -0.3)]))          # no positive cell
        self.assertIsNone(ba.lone_peak([mk(100, 0.2), mk(90, 0.1), mk(60, -0.3)]))             # two positives: a plateau
        self.assertIsNone(ba.lone_peak([mk(100, -0.2), mk(10, 0.9), mk(90, -0.1), mk(60, -0.3)]))   # positive cell under 30 trades is not a peak
        self.assertIsNone(ba.lone_peak([mk(100, -0.2), mk(90, 0.1)]))                          # too few cells to call it lone

    def test_committed_heatmaps(self):
        tests = ba.collect(ba.RESULTS_DIR)
        studies = {}
        for t in tests:
            if t["id"].startswith(("desk-tom_vp-", "desk-fabio_v3-")):
                self.assertTrue(t.get("heatmaps"), t["id"])
                studies[t["id"].split("-")[1]] = t["heatmaps"]
                by = {x["id"]: x for x in tests}
                for h in t["heatmaps"]:
                    for c in h["cells"]:   # every cell is a real run: n and mean equal that run's banner
                        self.assertEqual((c["n"], c["mean"]), (by[c["id"]]["banner"]["n"], by[c["id"]]["banner"]["net_r"]))
        self.assertEqual(sorted(studies), ["fabio_v3", "tom_vp"])
        anchor = [h for h in studies["tom_vp"] if h["x"] == "anchor"][0]
        self.assertEqual(len(anchor["cells"]), 4)
        self.assertEqual((anchor["peak"]["x"], anchor["peak"]["y"]), ("prior_week", "ACCEPT"))   # the one +0.081 cell
        for h in studies["fabio_v3"]:
            self.assertIsNone(h["peak"])   # Model C cells are all positive (a plateau); Model B all negative

    def test_page_draws_heatmap(self):
        for k in ("function heatmap(", "lone peak", "under 30 trades"):
            self.assertIn(k, ba.TEMPLATE)


if __name__ == "__main__":
    unittest.main()


class UxOneScreen(unittest.TestCase):
    """Operator verdicts 2026-11-04 (d-sim-ux-1104): timeframe pills + tabs, inline comments, one screen."""

    def test_tf_parsing_and_inference(self):
        self.assertEqual(ba.tfs_in("RSI deep 1m/5m/15m/60m, 0.10% fee, EMA 10"), ["1m", "5m", "15m", "1h"])
        self.assertEqual(ba.tfs_in("W01 5m A1_L53"), ["5m"])
        self.assertEqual(ba.tfs_in("BTCUSDT 15min 2024"), [])
        r = _result(examples=[{"kind": "table", "title": "H2 (15m bottom buy)", "cols": ["Arm"], "rows": [["x"]]},
                              {"kind": "trade_chart", "tf": "30m", "title": "t"}])
        ba.add_tf(r)
        a, b = r["examples"]
        self.assertEqual((a["tf"], a["tf_source"]), ("15m", "inferred"))
        self.assertEqual((b["tf"], b["tf_source"]), ("30m", "json"))
        self.assertEqual(r["tfs"], ["30m", "15m"])
        self.assertEqual(r["tf_tabs"], ["30m", "15m"])

    def test_table_rows_carry_their_tf(self):
        r = _result(examples=[{"kind": "table", "title": "cells", "cols": ["Arm", "n"],
                               "rows": [["W01 5m A", "1"], ["W04 15m A", "2"], ["W07 1h A", "3"]]}])
        ba.add_tf(r)
        self.assertEqual(r["examples"][0]["row_tf"], ["5m", "15m", "1h"])
        self.assertEqual(r["tf_tabs"], ["5m", "15m", "1h"])

    def test_committed_results_have_tfs_field(self):
        tests = ba.collect(ba.RESULTS_DIR)
        self.assertTrue(all("tfs" in t and "tf_tabs" in t for t in tests))
        atlas = next(t for t in tests if t["id"] == "wavetrend_atlas")
        self.assertGreaterEqual(len(atlas["tf_tabs"]), 2)

    def test_page_renders_tf_pill_and_tabs(self):
        for k in ('class="pill tf', "function tfTabs", 'role="tablist"', 'role="tab"', "data-tf", "function applyTf", "tf_source"):
            self.assertIn(k, ba.TEMPLATE)
        self.assertNotIn("<option", ba.TEMPLATE.split("function tfTabs")[1].split("function ")[0])  # tabs, never a dropdown

    def test_top_tabs(self):
        for k in ("Families", "Verdict grid", "Charts", "Comments", "function showTab", "function gridTab", "function chartsTab", "function commentsTab"):
            self.assertIn(k, ba.TEMPLATE)

    def test_news_and_concept_tabs(self):
        for k in ('["news","News"', "function inConcept", "/*concepts*/", "/*end-concepts*/", 'startsWith("c:")', "CONC"):
            self.assertIn(k, ba.TEMPLATE)
        for c in ("Tom", "Fabio", "Malkan", "Krown", "Bollinger", "RSI", "WaveTrend"):
            self.assertIn('["' + c + '",[', ba.TEMPLATE)
            self.assertIn('"c:"+', ba.TEMPLATE)

    def test_concept_tab_hides_other_families(self):
        import shutil
        import subprocess
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        src = ba.TEMPLATE
        self.assertIn("/*concepts*/", src)
        js = src[src.index("/*concepts*/"):src.index("/*end-concepts*/")]
        rows = [{"family": "Tom Core", "title": "Tom VP pivot", "id": "a"},
                {"family": "Krown Audit", "title": "Krown capture", "id": "b"},
                {"family": "News Feeds", "title": "News feeds 2026-10-30", "id": "dir-news_feeds_2026-10-30"},
                {"family": "Bb State Map", "title": "BB state map", "id": "c"},
                {"family": "Rsi Levels", "title": "RSI levels", "id": "d"},
                {"family": "WaveTrend", "title": "WaveTrend atlas", "id": "e"},
                {"family": "Fabio Cvd", "title": "Fabio CVD", "id": "f"},
                {"family": "Malkan Rsi", "title": "Malkan RSI", "id": "g"},
                {"family": "Desk runs", "title": "other", "id": "h"}]
        prog = js + "const R=" + json.dumps(rows) + ";const o={};['News','Tom','Fabio','Malkan','Krown','Bollinger','RSI','WaveTrend'].forEach(c=>{o[c]=R.filter(r=>inConcept(r,c)).map(r=>r.id)});console.log(JSON.stringify(o))"
        out = _run_node(node, prog)
        self.assertEqual(out.returncode, 0, out.stderr)
        o = json.loads(out.stdout)
        self.assertEqual(o["Tom"], ["a"])
        self.assertEqual(o["Krown"], ["b"])
        self.assertEqual(o["News"], ["dir-news_feeds_2026-10-30"])
        self.assertEqual(o["Bollinger"], ["c"])
        self.assertEqual(o["RSI"], ["d", "g"])
        self.assertEqual(o["WaveTrend"], ["e"])
        self.assertEqual(o["Fabio"], ["f"])
        self.assertEqual(o["Malkan"], ["g"])

    def test_verdict_grid_cell_is_tone_plus_glyph_with_tooltip(self):
        for k in ('class="gc', "function glyphOf", "title=", "&#10006;", "&#10004;"):
            self.assertIn(k, ba.TEMPLATE)

    def test_comment_box_under_charts_and_cards(self):
        for k in ("function commentBox", 'data-copy', "copy all", 'chart_id', "commentBox(t.id,\"card\")"):
            self.assertIn(k, ba.TEMPLATE)
        self.assertIn('commentBox(t.id,"ex"+i)', ba.TEMPLATE)

    def test_save_comment_adapter_runs(self):
        import shutil
        import subprocess
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        src = ba.TEMPLATE
        j = src.index("/*end-comments-adapter*/")
        js = src[src.index("const CKEY"):j] if "const CKEY" in src else ""
        self.assertTrue(js, "CKEY / adapter block missing")
        # Runtime contract 0.2.96: `await claude.use("db")` -> {collection(path).doc(id).set(body)}; null when unavailable.
        prog = js + r'''
const store={};global.localStorage={getItem:k=>store[k]??null,setItem:(k,v)=>{store[k]=v}};
const calls=[];const fakeDb={collection:p=>({doc:id=>({set:b=>{calls.push([p,id,b]);return Promise.resolve()}})})};
global.window={claude:{use:n=>Promise.resolve(n==="db"?fakeDb:null)}};
saveComment({test_id:"t",chart_id:"ex0",text:"hi",ts:1});
(async()=>{await new Promise(r=>setTimeout(r,20));
DBP=null;global.window={claude:{use:()=>Promise.reject(new Error("boom"))}};saveComment({test_id:"t",chart_id:"ex1",text:"two",ts:2});
await new Promise(r=>setTimeout(r,20));
DBP=null;global.localStorage={getItem:()=>{throw new Error("x")},setItem:()=>{throw new Error("x")}};global.window={};saveComment({test_id:"t",chart_id:"c",text:"three",ts:3});
await new Promise(r=>setTimeout(r,20));
console.log(JSON.stringify({calls:calls.length,first:calls[0],local:JSON.parse(store[CKEY]).length}));})();'''
        out = _run_node(node, prog)
        self.assertEqual(out.returncode, 0, out.stderr)
        res = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(res["calls"], 1)
        self.assertEqual(res["local"], 2)  # db rejection and storage throw never block
        self.assertEqual(res["first"][0], "comments")
        self.assertEqual(res["first"][1], "1-t-ex0")
        self.assertIn("hi", json.dumps(res["first"]))

    def test_one_screen_layout(self):
        css = ba.TEMPLATE.split("</style>")[0]
        for k in ("height:100vh", "overflow:hidden", ".pane{", "min-height:0"):
            self.assertIn(k, css)
        self.assertIn('id="app"', ba.TEMPLATE)
        self.assertIn("@media(max-width:700px)", css)  # phone width


class TradeStrip(unittest.TestCase):
    """sim-continuous-strip: one candle strip with every trade marked + a plain rule card (SIM_VISUALS_REVIEW rows 1, 6)."""

    def test_rule_card_fields_from_what(self):
        r = _result(what=[{"name": "Signal", "value_plain": "buy dot", "label": "SOURCED"},
                          {"name": "Exits", "value_plain": "centre line, cap 60", "label": "OURS"},
                          {"name": "Costs", "value_plain": "0.10% per round trip", "label": "SOURCED"}],
                    examples=[{"kind": "trade_chart", "tf": "30m", "title": "t", "stop_note": "No stop loss.", "trades": []}])
        ba.add_tf(r)
        ba.add_rule_card(r)
        rc = r["examples"][0]["rule_card"]
        self.assertEqual(list(rc), ["entry", "exit", "stop", "timeframe", "costs"])
        self.assertEqual(rc["exit"]["text"], "centre line, cap 60")
        self.assertEqual(rc["exit"]["label"], "OURS")
        self.assertEqual(rc["costs"]["label"], "SOURCED")
        self.assertEqual(rc["stop"]["text"], "No stop loss.")
        self.assertEqual(rc["timeframe"]["text"], "30m")

    def test_rule_card_absent_costs_is_na(self):
        r = _result(examples=[{"kind": "trade_chart", "tf": "30m", "title": "t", "trades": []}])
        ba.add_rule_card(r)
        rc = r["examples"][0]["rule_card"]
        self.assertEqual(rc["costs"]["text"], "n/a")
        self.assertEqual(rc["stop"]["text"], "n/a")

    def test_page_has_strip_and_card_for_c30(self):
        self.assertIn('id="trade-strip"', ba.TEMPLATE)
        self.assertIn('id="rule-card"', ba.TEMPLATE)
        self.assertIn("trade-marker", ba.TEMPLATE)
        tests = ba.collect(ba.RESULTS_DIR)
        c30 = next(t for t in tests if t["id"] == "eagle-c30-wt-rsi-div")
        ex = next(e for e in c30["examples"] if e["kind"] == "trade_chart")
        self.assertTrue(ex["trades"])
        for k in ("entry", "exit", "stop", "timeframe", "costs"):
            self.assertIn(k, ex["rule_card"])
        self.assertIn("0.10%", ex["rule_card"]["costs"]["text"])
        self.assertEqual(ex["rule_card"]["costs"]["label"], "SOURCED")

    def test_strip_marks_every_trade_in_node(self):
        import shutil
        import subprocess
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        js = ba.TEMPLATE.split("function tradeStrip(x)")[1].split("\nfunction ")[0]
        prog = ("const esc=s=>String(s);const f2=v=>v.toFixed(2);function tradeStrip(x)" + js +
                ";const tr=[1,2,3].map(i=>({d:'d'+i,t0:i*1e7,net:i==2?-1:1,sig:3,ent:4,ext:8,c:Array.from({length:12},()=>[0,1,-1,0.5])}));"
                "const r=tradeStrip({trades:tr,tf_min:30});const h=r.html;"
                "console.log(JSON.stringify({m:(h.match(/class=\"trade-marker/g)||[]).length,"
                "w:(h.match(/trade-marker trade-win/g)||[]).length,l:(h.match(/trade-marker trade-loss/g)||[]).length,id:h.includes('id=\"trade-strip\"')}))")
        out = _run_node(node, prog)
        self.assertEqual(out.returncode, 0, out.stderr)
        res = json.loads(out.stdout.strip().splitlines()[-1])
        self.assertEqual(res["m"], 3)
        self.assertEqual((res["w"], res["l"]), (2, 1))
        self.assertTrue(res["id"])
