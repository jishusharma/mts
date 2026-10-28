"""Formatter tests for status_board.py with fake inputs (no machine access)."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import status_board as sb  # noqa: E402


class T(unittest.TestCase):
    def test_budget_newest_per_login(self):
        txt = ("1700Z h/C [note] BUDGET login=C 5h=10% week=80% reset=2026-10-27T20:00Z sup=X\n"
               "1750Z h/C [note] BUDGET login=C 5h=12% week=81% reset=2026-10-27T20:00Z sup=X\n"
               "1751Z h/A [note] BUDGET login=A 5h=3% week=40% reset=R\nnoise\n")
        b = sb.parse_budget(txt)
        self.assertEqual(b["C"], ("1750", 12, 81, "2026-10-27T20:00Z"))
        self.assertEqual(b["A"][2], 40)

    def test_table_shape_and_pipe_escape(self):
        t = sb.table(["a", "b"], [["x|y", 2]])
        self.assertEqual(t[1], "|---|---|")
        self.assertEqual(t[2], "| x/y | 2 |")

    def test_missing_data_is_marked(self):
        self.assertTrue(any(sb.ND in ln for ln in sb.fmt_budget({}, 0, 0, 0, 0)))
        self.assertIn("NOT_IN_DATA", sb.fmt_speed([("d", 1)], [], 0, None, "ships")[-3])
        self.assertTrue(all(sb.ND in ln for ln in sb.fmt_sessions()))

    def test_red_minutes_streak(self):
        now = datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc)
        runs = [{"conclusion": "failure", "created_at": "2026-10-28T11:50:00Z"}, {"conclusion": "failure", "created_at": "2026-10-28T11:30:00Z"},
                {"conclusion": "success", "created_at": "2026-10-28T11:00:00Z"}]
        self.assertEqual(sb.red_minutes(runs, now), 30)
        self.assertEqual(sb.red_minutes(runs[2:], now), 0)

    def test_gate_median(self):
        z = "2026-10-28T10:%02d:00Z"
        rows = [{"secs": 10, "utc": z % 0}, {"secs": 5, "utc": z % 1}, {"secs": 40, "utc": z % 30}, {"secs": 90, "utc": z % 59}]
        self.assertEqual(sb.gate_summary(rows), (40.0, [15, 40, 90]))
        self.assertIsNone(sb.gate_summary([]))

    def test_stale_claims_parsed(self):
        txt = "claim a: JIS-NUC / sharma - a [area: -] 45h old STALE (ask)" + chr(10) + "claim b: JIS-NB / jis - b [area: -] 1h old"
        self.assertEqual(sb.stale_claims(txt), ["JIS-NUC: a (45h)"])

    def test_count_open_ignores_done(self):
        cs = [{"weight": "CRITICAL", "state": "ready"}, {"weight": "CRITICAL", "state": "done"}, {"weight": "CRUCIAL", "state": "raw"}]
        self.assertEqual(sb.count_open(cs), {"CRITICAL": 1, "CRUCIAL": 1})

    def test_section_failure_does_not_stop_others(self):
        def boom():
            raise RuntimeError("x")
        fails, body = sb.build([("A", boom), ("B", lambda: ["ok"])])
        self.assertEqual(fails, 1)
        self.assertIn("NOT_IN_DATA: RuntimeError: x", body)
        self.assertIn("ok", body)

    def test_result_line_first_and_short(self):
        r = sb.result_line({"C": ("1", 1, 81, "r")}, 0, {"CRITICAL": 2, "CRUCIAL": 3}, 0)
        self.assertTrue(r.startswith("**Status:") and "81%" in r and "5 CRITICAL/CRUCIAL" in r)

    def test_budget_newest_by_time_not_file_order(self):
        nl = chr(10)
        txt = ("1600Z h/C [note] BUDGET login=C 5h=5% week=16% reset=2026-11-03T20:00Z" + nl
               + "1100Z h/C [note] BUDGET login=C 5h=90% week=95% reset=2026-10-27T20:00Z" + nl)
        self.assertEqual(sb.parse_budget(txt)["C"][2], 16)

    def test_budget_midnight_wrap(self):
        nl = chr(10)
        txt = ("2359Z h/C [note] BUDGET login=C 5h=8% week=4% reset=R" + nl
               + "0820Z h/C [note] BUDGET login=C 5h=7% week=5% reset=R" + nl
               + "0700Z h/C [note] BUDGET login=C 5h=1% week=3% reset=R" + nl)
        self.assertEqual(sb.parse_budget(txt)["C"][2], 5)

    def test_cleanup_widened(self):
        subj = ["dedup helpers", "Cleanup temp", "temp leak fix", "feat: x", "Declutter", "prune old", "retire card"]
        c = sb.cleanup_commits(subj)
        self.assertEqual(len(c), 6)
        self.assertIn("commits today: 6", chr(10).join(sb.fmt_value([], c, [], [])))

    def test_gpt_row_stale_and_fresh(self):
        d = {"allowance": {"plan": "plus", "window_used": 68.0, "week_used": 29.0}, "at": "2026-10-27T21:29:47Z"}
        r = sb.gpt_row(d, datetime(2026, 10, 28, 12, 0, tzinfo=timezone.utc), "src")
        self.assertEqual(r[:4], ["GPT (Codex)", "plus", "68%", "29%"])
        self.assertIn("STALE", r[4])
        self.assertNotIn("STALE", sb.gpt_row(d, datetime(2026, 10, 28, 0, 0, tzinfo=timezone.utc), "src")[4])

    def test_gemini_not_in_data_and_no_email(self):
        txt = chr(10).join(sb.fmt_gpt_gemini(sb.gpt_row({}, datetime.now(timezone.utc), "s")))
        self.assertIn("NOT_IN_DATA (no Gemini usage file", txt)
        self.assertNotIn("@", txt)


if __name__ == "__main__":
    unittest.main()
