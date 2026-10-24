"""Tests for build_artifact.py / export_results.py (the simulator page)."""
import csv
import json
import os
import re
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

import build_artifact as ba  # noqa: E402
import export_results as ex  # noqa: E402

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

    def test_every_result_file_becomes_a_test(self):
        h = self._build(_result("aa"), _result("bb"), _result("cc"))
        tests = json.loads(re.search(r"const TESTS=(\[.*?\]);\n", h, re.S).group(1))
        self.assertEqual([t["id"] for t in tests], ["aa", "bb", "cc"])
        self.assertNotRegex(h, r'(src|href)="https?://')
        self.assertIn("prefers-color-scheme:dark", h)
        self.assertIn("What was tested", h)

    def test_bad_result_files_fail_the_build(self):
        bad = _result("x")
        del bad["why"]
        with self.assertRaises(ValueError):
            self._build(bad)
        with self.assertRaises(ValueError):
            self._build(_result("y", what=[{"name": "p", "value_plain": "v", "label": "GUESS"}]))

    def test_committed_results_build(self):
        names = sorted(os.listdir(ba.RESULTS_DIR))
        for need in ("levels_ladder.json", "t09_live_parity.json", "t06_cost_fill.json", "t07_stale_verdicts.json"):
            self.assertIn(need, names)
        tests = ba.collect(ba.RESULTS_DIR)
        for t in tests:
            self.assertTrue(t["examples"], t["id"])
            self.assertNotRegex(json.dumps(t), r"\b\d{5}\.\d")  # no raw price like 44375.0


if __name__ == "__main__":
    unittest.main()
