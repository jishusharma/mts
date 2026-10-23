"""Checks on the committed S1 outputs in research/krown_audit_2026-10-22/run/ (skipped when run/ is absent)."""
import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import krown_context as kx  # noqa: E402

HERE = Path(__file__).parent
RUN = HERE.parents[2] / "research" / "krown_audit_2026-10-22" / "run"
CUT = 1719792000000                                   # 2024-07-01 UTC
JOINED_COLUMNS = ["layer", "decision_ts", "decision_utc", "side", "iso_week", "set", "usable", "d1", "d2", "d3", "S",
                  "daily_row_open_ms", "h4_row_open_ms"]


class TestShippedArtifacts(unittest.TestCase):
    def test_joined_events_have_only_the_whitelisted_columns_and_are_point_in_time(self):
        f = RUN / "joined_events.csv"
        if not f.exists():
            if (RUN / "COUNTS.md").exists():
                self.fail("COUNTS.md is committed without run/joined_events.csv")
            self.skipTest("run/ absent")
        with open(f, newline="", encoding="utf-8") as fh:
            rd = csv.DictReader(fh)
            self.assertEqual(rd.fieldnames, JOINED_COLUMNS)
            n = 0
            for r in rd:
                if r["usable"] != "1":
                    continue
                dts = int(r["decision_ts"])
                self.assertLessEqual(dts, CUT)
                self.assertLess(int(r["daily_row_open_ms"]) + kx.DAY_MS + kx.LATENCY_MS, dts)
                self.assertLess(int(r["h4_row_open_ms"]) + kx.H4_MS + kx.LATENCY_MS, dts)
                self.assertEqual(int(r["S"]), int(r["d1"]) + int(r["d2"]) + int(r["d3"]))
                n += 1
            self.assertGreater(n, 1000)

    def test_context_csv_has_baselines_labels_and_no_bar_after_cut(self):
        f = RUN / "context_dev.csv"
        if not f.exists():
            if (RUN / "COUNTS.md").exists():
                self.fail("COUNTS.md is committed without run/context_dev.csv")
            self.skipTest("run/ absent")
        with open(f, newline="", encoding="utf-8") as fh:
            fh.readline()                             # label comment line
            rd = csv.DictReader(fh)
            self.assertIn("naive_trend_sma200", rd.fieldnames)
            self.assertIn("naive_trend_ret20", rd.fieldnames)
            plain = ("tf", "set", "open_ms", "open_utc", "available_at", "naive_trend_sma200", "naive_trend_ret20", "atr14_1d")
            for c in rd.fieldnames:
                if c not in plain:
                    self.assertTrue(c.endswith("_ours"), c)
            last = max(int(r["open_ms"]) for r in rd)
        self.assertLess(last, CUT)

    def test_counts_md_carries_required_sentences(self):
        f = RUN / "COUNTS.md"
        if not f.exists():
            self.skipTest("run/COUNTS.md absent")
        txt = f.read_text(encoding="utf-8")
        for needle in ("never cost/R alone", "cost/R falling is not evidence of improvement", "iso_weeks", "mde_week", "FROZEN D3",
                       "FROZEN D2", "DESCRIPTIVE", "prereg_gate.py", "No outcome column was opened"):
            self.assertIn(needle, txt)


if __name__ == "__main__":
    unittest.main()
