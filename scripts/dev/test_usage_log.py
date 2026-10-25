"""Tests for usage_log.py (written before the module): header, row refusal, transcript parser, idle edges, summary."""
import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PILOT = os.path.join(HERE, "..", "..", "MyTradingSys", "research", "USAGE_PILOT.csv")


def _mod():
    import usage_log
    return usage_log


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class UsageLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.csv = os.path.join(self.tmp, "u.csv")

    def _row(self, *extra, before="10,20,5", after="12,21,5"):
        return subprocess.run([sys.executable, os.path.join(HERE, "usage_log.py"), "row", "--csv", self.csv, "--card", "c1",
                               "--step", "s1", "--lane", "builder", "--model", "sonnet-5.5", "--before", before,
                               "--after", after] + list(extra), capture_output=True, text=True)

    def test_header_matches_pilot_file(self):
        with open(PILOT, newline="") as f:
            want = f.readline().rstrip("\r\n")
        self.assertEqual(",".join(_mod().HEADER), want)
        self.assertEqual(len(_mod().HEADER), 19)

    def test_row_refuses_missing_after_read(self):
        r = self._row(after="")
        self.assertEqual(r.returncode, 1)
        self.assertFalse(os.path.exists(self.csv))

    def test_row_refuses_missing_before_read(self):
        self.assertEqual(self._row(before="10,,5").returncode, 1)
        self.assertFalse(os.path.exists(self.csv))

    def test_row_writes_header_once_and_blank_optionals(self):
        self.assertEqual(self._row().returncode, 0)
        self.assertEqual(self._row("--codex5h", "7").returncode, 0)
        rows = list(csv.reader(open(self.csv, newline="")))
        self.assertEqual(rows[0], _mod().HEADER)
        self.assertEqual(len(rows), 3)
        d = dict(zip(rows[0], rows[1]))
        self.assertEqual((d["pct5h_before"], d["pct5h_after"], d["pctweek_after"], d["fable_week_after"]), ("10", "12", "21", "5"))
        self.assertEqual((d["codex_5h_pct"], d["gemini"], d["tokens_in"]), ("", "", ""))
        self.assertEqual(dict(zip(rows[0], rows[2]))["codex_5h_pct"], "7")

    def _transcript(self, lines):
        p = os.path.join(self.tmp, "t.jsonl")
        with open(p, "w", newline="\n") as f:
            for ln in lines:
                f.write((ln if isinstance(ln, str) else json.dumps(ln)) + "\n")
        return p

    def test_parser_sums_dedupes_and_skips(self):
        a = {"type": "assistant", "message": {"id": "m1", "usage": {"input_tokens": 10, "output_tokens": 5,
                                                                     "cache_read_input_tokens": 100, "cache_creation_input_tokens": 20}}}
        a_dup = json.loads(json.dumps(a))
        b = {"type": "assistant", "message": {"id": "m2", "usage": {"input_tokens": 1, "output_tokens": 2}}}
        none = {"type": "assistant", "message": {"id": "m3"}}
        user = {"type": "user", "message": {"content": "hi"}}
        p = self._transcript([a, a_dup, b, none, user])
        self.assertEqual(_mod().parse_transcript(p), (11, 7, 120))

    def test_parser_malformed_or_missing_gives_none(self):
        self.assertIsNone(_mod().parse_transcript(self._transcript(["{not json", "[1,2"])))
        self.assertIsNone(_mod().parse_transcript(os.path.join(self.tmp, "nope.jsonl")))

    def test_row_with_transcript_fills_token_cells_and_bad_one_stays_exit0(self):
        a = {"type": "assistant", "message": {"id": "m1", "usage": {"input_tokens": 3, "output_tokens": 4, "cache_read_input_tokens": 5}}}
        self.assertEqual(self._row("--transcript", self._transcript([a])).returncode, 0)
        self.assertEqual(self._row("--transcript", self._transcript(["{bad"])).returncode, 0)
        rows = list(csv.reader(open(self.csv, newline="")))
        d1, d2 = dict(zip(rows[0], rows[1])), dict(zip(rows[0], rows[2]))
        self.assertEqual((d1["tokens_in"], d1["tokens_out"], d1["tokens_cache"]), ("3", "4", "5"))
        self.assertEqual((d2["tokens_in"], d2["tokens_out"], d2["tokens_cache"]), ("", "", ""))

    # idle: pure function idle_lanes(last_rows, ready_lanes, claimed_lanes, now, reset)
    def test_idle_five_hour_edge(self):
        U = _mod()
        now = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
        reset = now + timedelta(minutes=30)
        last = {"builder": {"pct5h_after": "39", "pctweek_after": "100"}}
        self.assertEqual(U.idle_lanes(last, {"builder"}, set(), now, reset), ["builder"])
        last["builder"]["pct5h_after"] = "40"
        self.assertEqual(U.idle_lanes(last, {"builder"}, set(), now, reset), [])
        last["builder"]["pct5h_after"] = "10"
        self.assertEqual(U.idle_lanes(last, set(), set(), now, reset), [])  # no ready card for the lane

    def test_idle_sixty_minute_edge(self):
        U = _mod()
        now = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
        last = {"builder": {"pct5h_after": "10", "pctweek_after": "99"}}
        self.assertEqual(U.idle_lanes(last, {"builder"}, set(), now, now + timedelta(minutes=60)), ["builder"])
        self.assertEqual(U.idle_lanes(last, {"builder"}, set(), now, now + timedelta(minutes=61)), [])
        self.assertEqual(U.idle_lanes(last, {"builder"}, set(), now, now - timedelta(minutes=1)), [])  # reset already passed

    def test_idle_week_under_pace_needs_no_claim(self):
        U = _mod()
        now = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
        reset = now + timedelta(minutes=30)          # ~99.7 % of the 7 days elapsed
        last = {"builder": {"pct5h_after": "90", "pctweek_after": "50"}}
        self.assertEqual(U.idle_lanes(last, set(), set(), now, reset), ["builder"])
        self.assertEqual(U.idle_lanes(last, set(), {"builder"}, now, reset), [])
        last["builder"]["pctweek_after"] = "100"
        self.assertEqual(U.idle_lanes(last, set(), set(), now, reset), [])

    def test_summary_mean_per_kind_over_rows_with_tokens(self):
        U = _mod()
        rows = [{"card": "a", "tokens_in": "10", "tokens_out": "5", "tokens_cache": "5"},
                {"card": "a", "tokens_in": "30", "tokens_out": "0", "tokens_cache": ""},
                {"card": "a", "tokens_in": "", "tokens_out": "", "tokens_cache": ""},
                {"card": "b", "tokens_in": "7", "tokens_out": "", "tokens_cache": ""}]
        s = U.summarize(rows, {"a": "SONNET", "b": "HAIKU"})
        self.assertEqual(s["SONNET"], (2, 25.0))
        self.assertEqual(s["HAIKU"], (1, 7.0))


if __name__ == "__main__":
    unittest.main()
