"""Tests for build_artifact.py (fixture build; red before build_artifact.py existed)."""
import csv
import json
import os
import re
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build_artifact as ba  # noqa: E402  (ImportError = red before the build script existed)

COLS = ["day", "touch_t", "side", "L1", "L2", "T1", "T2", "families", "E1"] + ba.STOP_COLS + [ba.FROZEN_COL]
RULE = {
    "rule": {"entry_filter": "E1"},
    "dev": {"n": 3, "mean": -0.1, "lo": -0.3, "hi": 0.1, "maxdd": 2.0, "win_rate": 0.33,
            "mean_fee_r": 0.1, "mean_gross_r": 0.0},
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


class T(unittest.TestCase):
    def _build(self, rows):
        src = _fixture(rows)
        out = os.path.join(src, "index.html")
        ba.main(["--src", src, "--out", out])
        return open(out, encoding="utf-8").read()

    def test_sections_and_selfcontained(self):
        h = self._build([_row(19083, 2, 1, 100.0, 99.0, 101.0, "", "1.5"),
                         _row(19084, 1, -1, 200.0, 202.0, 198.0, 196.0, "-1.0"),
                         _row(19085, 3, 1, 100.0, 99.0, 101.0, 102.0, "0.2", e1="False")])
        for s in ("Parameters in plain words", "Trade replay", "Why it failed"):
            self.assertIn(s, h)
        self.assertNotRegex(h, r'(src|href)="https?://')
        self.assertIn("prefers-color-scheme:dark", h)

    def test_only_e1_filled_and_relative_only(self):
        h = self._build([_row(19083, 2, 1, 12345.5, 12300.5, 12400.5, "", "1.5"),
                         _row(19085, 3, 1, 100.0, 99.0, 101.0, 102.0, "0.2", e1="False")])
        data = json.loads(re.search(r"const D=(\{.*?\});\n", h, re.S).group(1))
        self.assertEqual(data["n"], 1)
        self.assertNotIn("12345", h)  # no absolute price in the page
        t = data["trades"][0]
        self.assertAlmostEqual(t["l2"], -0.365, places=2)  # (12300.5-12345.5)/12345.5
        self.assertAlmostEqual(t["t2"], t["t1"] * 2, places=2)  # T2 fallback = T1 + (T1-L1)

    def test_dev_window_enforced(self):
        with self.assertRaises(ValueError):
            self._build([_row(20000, 1, 1, 100.0, 99.0, 101.0, 102.0, "1.0")])  # 2024-10: outside DEV

    def test_real_build_matches_frozen_numbers(self):
        if not os.path.isfile(os.path.join(ba.DEFAULT_SRC, "ladder_ideas_dev.csv")):
            self.skipTest("precomputed ladder csv not present")
        rule, rows = ba.load(ba.DEFAULT_SRC)
        data = ba.build_data(rule, rows)
        self.assertEqual(data["n"], rule["dev"]["n"])
        self.assertAlmostEqual(sum(t["r"] for t in data["trades"]) / data["n"], rule["dev"]["mean"], places=2)


if __name__ == "__main__":
    unittest.main()
