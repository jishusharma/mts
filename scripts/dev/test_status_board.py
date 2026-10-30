"""Formatter tests for status_board.py with fake inputs (no machine access)."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import status_board as sb  # noqa: E402


class T(unittest.TestCase):
    def test_asks_overdue_first_with_age(self):
        asks = [{"id": "q-1", "from": "jis-nb/C", "to": "A", "state": "none", "age_min": 20, "due_min": 60, "overdue": False, "esc": "", "text": "x"},
                {"id": "q-2", "from": "jis-nuc/A", "to": "C", "state": "told", "age_min": 90, "due_min": 60, "overdue": True, "esc": "jis-nb", "text": "y"}]
        high = [{"id": "b-1", "host": "vm", "state": "none", "hours": 3.0, "note": ""}]
        out = sb.fmt_asks(asks, high)
        self.assertEqual(out[0], "2 OVERDUE of 3 waiting")
        self.assertIn("| OVERDUE | q-2 |", out[3])
        self.assertIn("1.5 h", out[3])
        self.assertIn("| OVERDUE | b-1 |", out[4])
        self.assertIn("| open | q-1 |", out[5])
        self.assertEqual(sb.fmt_asks([], []), ["No ask or HIGH broadcast waits for a reply."])

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
        self.assertEqual(r[:2], ["GPT (Codex)", "plus"])
        self.assertTrue(r[2].startswith("STALE 68% (14.5 h old)"), r[2])
        self.assertTrue(r[3].startswith("STALE 29%"), r[3])
        self.assertIn("STALE", r[4])
        fresh = sb.gpt_row(d, datetime(2026, 10, 27, 21, 40, tzinfo=timezone.utc), "src")
        self.assertEqual(fresh[2:4], ["68% (10 min old)", "29% (10 min old)"])
        self.assertNotIn("STALE", fresh[4])

    def test_gpt_reading_2h_old_is_never_a_plain_percent(self):
        # 2026-10-30: status printed GPT "36%" from a 2.3 h old codex_usage.json while the allowance was spent
        d = {"allowance": {"plan": "plus", "window_used": 36.0, "week_used": 29.0}, "at": "2026-10-29T21:15:19Z"}
        r = sb.gpt_row(d, datetime(2026, 10, 29, 23, 33, tzinfo=timezone.utc), "src")
        self.assertNotIn(r[2], ("36%", "36.0%"))
        self.assertIn("STALE", r[2])
        self.assertIn("STALE", r[3])

    def test_gpt_exhausted_from_usage_flag_and_from_lane_state(self):
        now = datetime(2026, 10, 29, 23, 33, tzinfo=timezone.utc)
        d = {"allowance": {"plan": "plus", "window_used": 36.0, "week_used": 29.0}, "at": "2026-10-29T23:30:00Z",
             "exhausted": {"flag": True, "until": "2026-10-30T02:29:05Z", "why": "x"}}
        self.assertEqual(sb.gpt_row(d, now, "s")[2:4], ["EXHAUSTED until 2026-10-30T02:29Z"] * 2)
        lane = {"status": "down", "reason": "window", "until": "2026-10-30T02:29:05Z"}
        d2 = {"allowance": {"plan": "plus", "window_used": 36.0, "week_used": 29.0}, "at": "2026-10-29T21:15:19Z"}
        r = sb.gpt_row(d2, now, "s", lane)
        self.assertEqual(r[2], "EXHAUSTED until 2026-10-30T02:29Z")
        self.assertIn("lane_state.json", r[5])
        auth = sb.gpt_row(d2, now, "s", {"status": "down", "reason": "auth", "until": ""})
        self.assertEqual(auth[2], "EXHAUSTED, reset unknown")
        after = sb.gpt_row(d2, datetime(2026, 10, 30, 3, 0, tzinfo=timezone.utc), "s", lane)   # reset passed: back to aged numbers
        self.assertNotIn("EXHAUSTED", after[2])
        self.assertIn("STALE", after[2])

    def test_budget_rows_carry_age_and_stale(self):
        b = {"A": ("2110", 26, 91, "2026-11-01T17:00Z"), "B": ("2325", 50, 57, "?")}
        txt = chr(10).join(sb.fmt_budget(b, 0, 0, 0, 0, datetime(2026, 10, 29, 23, 35, tzinfo=timezone.utc)))
        self.assertIn("STALE 26% (2.4 h old)", txt)
        self.assertIn("| B | 50% (10 min old) | 57% (10 min old) | 23:25 (10 min ago)", txt)
        self.assertEqual(round(sb.hhmm_age_h("2350", datetime(2026, 10, 30, 0, 10, tzinfo=timezone.utc)), 2), 0.33)   # crosses midnight

    def test_gemini_not_in_data_and_no_email(self):
        txt = chr(10).join(sb.fmt_gpt_gemini(sb.gpt_row({}, datetime.now(timezone.utc), "s")))
        self.assertIn("NOT_IN_DATA (no Gemini usage file", txt)
        self.assertNotIn("@", txt)

    def test_parse_commit_utc_day_handles_offsets_around_midnight(self):
        # 04:30 in +05:30 is 23:00 on previous day in UTC
        ts_local_morning = "2026-10-30T04:30:00+05:30"
        self.assertEqual(sb.parse_commit_utc_day(ts_local_morning), "2026-10-29")

        # 06:00 in +05:30 is 00:30 on same day in UTC
        ts_local_after_utc_midnight = "2026-10-30T06:00:00+05:30"
        self.assertEqual(sb.parse_commit_utc_day(ts_local_after_utc_midnight), "2026-10-30")

        # Negative offset: 21:00 on 2026-10-29 in -04:00 is 01:00 on 2026-10-30 in UTC
        ts_west = "2026-10-29T21:00:00-04:00"
        self.assertEqual(sb.parse_commit_utc_day(ts_west), "2026-10-30")

    def test_git_days_uses_explicit_utc(self):
        fake_log = "2026-10-30T04:30:00+05:30\n2026-10-30T06:00:00+05:30\n2026-10-29T20:00:00Z"
        original_run = sb.run
        try:
            sb.run = lambda cmd, timeout=20: fake_log
            sb.git_days.cache_clear()
            days = sb.git_days()
            self.assertEqual(days, ["2026-10-29", "2026-10-30", "2026-10-29"])
        finally:
            sb.run = original_run
            sb.git_days.cache_clear()


if __name__ == "__main__":
    unittest.main()
