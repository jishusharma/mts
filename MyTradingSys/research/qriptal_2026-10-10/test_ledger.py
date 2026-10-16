"""Tests for the Qriptal call ledger (card qriptal-call-ledger). Expected values come from RULES.md
(eligible = BTC + forward-looking + entry + stop + at least one target; call time = video publish time),
never from ledger.py's own output.
Run: python MyTradingSys/research/qriptal_2026-10-10/test_ledger.py
"""
import sys
sys.dont_write_bytecode = True
import contextlib
import io
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ledger as L  # noqa: E402

NS = "NOT STATED"
TIME = "2026-06-02T11:41:14Z"

# three hand-written transcript snippets (raw format: "[m:ss] text" per line)
FULL_CALL = """[0:01] So the plan for this week is simple
[0:03] I will short a sweep of 82,200 dollars
[0:06] with my stop loss at 82,800 and the target
[0:09] is 73,000 then 72,000 dollars."""
NO_STOP = """[0:01] I would look for a long at 61,000
[0:04] targeting 65,000 but I do not have a stop yet."""
RECAP = """[0:01] Last week I took a short at 80,000
[0:04] with a stop at 80,500 and it got stopped out."""


def row(**kw):
    base = dict(kind="PLAN", asset="BTC", direction="short", entry="82,200", stop="82,800",
                targets="73,000; 72,000", published_utc=TIME)
    base.update(kw)
    return base


class TestClassify(unittest.TestCase):
    def test_full_call_is_eligible(self):
        ok, reason = L.classify(row())
        self.assertTrue(ok)
        self.assertIn("entry+stop+target", reason)

    def test_call_without_stop(self):
        ok, reason = L.classify(row(stop=NS))
        self.assertFalse(ok)
        self.assertEqual(reason, "no stop")

    def test_chart_relative_stop_counts_as_not_stated(self):
        ok, reason = L.classify(row(stop="NOT STATED (chart-relative: below this low)"))
        self.assertFalse(ok)
        self.assertEqual(reason, "no stop")

    def test_several_fields_missing(self):
        ok, reason = L.classify(row(entry=NS, stop=NS, targets=NS))
        self.assertFalse(ok)
        self.assertEqual(reason, "no entry, no stop, no target")

    def test_recap_is_retrospective_even_with_all_fields(self):
        ok, reason = L.classify(row(kind="RECAP", entry="80,000", stop="80,500"))
        self.assertFalse(ok)
        self.assertEqual(reason, "retrospective")

    def test_hypothetical_and_view_and_other_asset(self):
        self.assertEqual(L.classify(row(kind="HYPO"))[1], "hypothetical")
        self.assertEqual(L.classify(row(kind="VIEW"))[1], "view only, no trade offered")
        self.assertEqual(L.classify(row(asset="NFLX"))[1], "not BTC")

    def test_no_publish_time_is_no_time(self):
        ok, reason = L.classify(row(published_utc=""))
        self.assertFalse(ok)
        self.assertEqual(reason, "NO_TIME")

    def test_unknown_kind_is_rejected(self):
        with self.assertRaises(ValueError):
            L.classify(row(kind="MAYBE"))


class TestLocate(unittest.TestCase):
    def test_quote_spanning_two_lines(self):
        lines = L.parse_transcript(FULL_CALL)
        l1, l2, ts = L.locate(lines, "with my stop loss at 82,800 and the target is 73,000")
        self.assertEqual((l1, l2, ts), (3, 4, "0:06"))

    def test_case_and_punctuation_are_ignored(self):
        lines = L.parse_transcript(NO_STOP)
        l1, l2, _ = L.locate(lines, "Targeting 65,000, but I do not have a STOP yet")
        self.assertEqual((l1, l2), (2, 2))

    def test_missing_quote_raises(self):
        with self.assertRaises(L.QuoteError):
            L.locate(L.parse_transcript(RECAP), "I will short at 90,000")

    def test_ambiguous_quote_raises(self):
        with self.assertRaises(L.QuoteError):
            L.locate(L.parse_transcript("[0:01] go long now\n[0:02] and go long now"), "go long now")

    def test_quote_longer_than_25_words_rejected(self):
        q = " ".join(["word"] * 26)
        with self.assertRaises(L.QuoteError):
            L.check_quote_length(q)
        L.check_quote_length(" ".join(["word"] * 25))


class TestSplit(unittest.TestCase):
    # BACKTEST_PROTOCOL s2: holdout starts 2026-06-26; a call can run 24 h to fill + 7 d open = 8 d
    def test_window_inside_dev(self):
        self.assertEqual(L.window_split("2026-06-18T00:00:00Z"), "DEV")

    def test_window_touching_holdout(self):
        self.assertEqual(L.window_split("2026-06-18T00:00:01Z"), "HOLDOUT")
        self.assertEqual(L.window_split("2026-09-21T07:11:25Z"), "HOLDOUT")


class TestReviewedRows(unittest.TestCase):
    """The reviewed rows must verify against the staged raw transcripts and match the committed CSV."""

    def test_every_reviewed_row_verifies(self):
        rows = L.build_rows()
        self.assertGreater(len(rows), 40)
        for r in rows:
            self.assertRegex(r["file_line"], r"^extracts/_staged_2026-09-27/raw/qriptal_.+_raw\.txt:\d+(-\d+)?$")
            self.assertLessEqual(len(r["quote"].split()), 25)

    def test_csv_matches_rebuild(self):
        self.assertEqual(L.read_csv_text(), L.render_csv(L.build_rows()))

    def test_crlf_checkout_of_the_csv_matches_but_a_content_change_does_not(self):
        # windows-latest checks the file out with core.autocrlf=true: same content, CRLF line ends
        want = L.render_csv(L.build_rows())
        tampered = want.replace("QRP-", "QRX-", 1)
        self.assertNotEqual(tampered, want)

        def check(content):
            """-> (read_csv_text() of a file holding `content`, exit code of `ledger.py check` on it)"""
            real = L.CSV_PATH
            try:
                with tempfile.TemporaryDirectory() as d:
                    L.CSV_PATH = Path(d, "CALL_LEDGER.csv")
                    L.CSV_PATH.write_bytes(content.encode("utf-8"))
                    with contextlib.redirect_stdout(io.StringIO()):
                        return L.read_csv_text(), L.main(["ledger.py", "check"])
            finally:
                L.CSV_PATH = real

        self.assertEqual(check(want), (want, 0))
        self.assertEqual(check(want.replace("\n", "\r\n")), (want, 0))
        self.assertEqual(check(tampered.replace("\n", "\r\n")), (tampered, 1))

    def test_eligible_rows_have_all_three_fields_and_a_time(self):
        for r in L.build_rows():
            if r["eligible"] == "Y":
                self.assertEqual(r["asset"], "BTC")
                self.assertEqual(r["kind"], "PLAN")
                for f in ("entry", "stop", "targets"):
                    self.assertFalse(r[f].startswith(NS), (r["video_id"], f))
                self.assertTrue(r["published_utc"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
