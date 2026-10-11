"""B156: the Tom alert card's SSOT_THESIS line must say WHEN the thesis was written, so a reader of the card
can see that "Price ~77600 never printed 76300" is 25 days old next to a live price of 83106.5.
No age threshold is invented (it would be NO-SOURCE): the age is always printed, nothing is hidden or tuned.

Expected strings come from the B156 item (items/B156_tom_alert_stale_ssot_thesis.md): thesis text, written time, age.
"""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
import session_state as ss  # noqa: E402

STATE = {"updated_utc": "2026-09-14T09:28:31.006753Z",
         "thesis": {"direction": "neutral", "confidence": "low", "text": "Price ~77600 never printed 76300."}}
NOW = datetime(2026, 10, 9, 14, 26, tzinfo=timezone.utc)


class TestThesisLine(unittest.TestCase):
    def test_line_carries_written_time_and_age(self):
        line = ss.thesis_line(STATE, NOW)
        self.assertTrue(line.startswith("THESIS: neutral (low)"), line)
        self.assertIn("Price ~77600 never printed 76300.", line)
        self.assertIn("written 2026-09-14T09:28Z", line)
        self.assertIn("25d 4h old", line)   # 2026-09-14 09:28 -> 2026-10-09 14:26 = 25 d 4 h 58 min

    def test_empty_thesis_text_gives_no_line(self):
        st = {"updated_utc": STATE["updated_utc"], "thesis": {"direction": "neutral", "confidence": "low", "text": ""}}
        self.assertEqual(ss.thesis_line(st, NOW), "")

    def test_missing_timestamp_says_unknown_age_not_fresh(self):
        st = {"thesis": STATE["thesis"]}
        self.assertIn("written time unknown", ss.thesis_line(st, NOW))

    def test_fresh_thesis_reads_minutes(self):
        st = dict(STATE, updated_utc="2026-10-09T14:00:00Z")
        self.assertIn("0h 26m old", ss.thesis_line(st, NOW))

    def test_card_no_longer_prints_the_thesis(self):
        # D13 (operator 2026-10-09, "Remove it from the card"): B156's age line is superseded; the card carries no thesis.
        ps1 = (Path(__file__).resolve().parents[2] / "scripts" / "core" / "start-trading-day.ps1").read_text(encoding="utf-8")
        self.assertNotIn('"SSOT_THESIS:', ps1)
        self.assertNotIn("thesis-line", ps1)
        self.assertIn("session_state.py", ps1)   # SSOT_TRIGGER still read from the same store


if __name__ == "__main__":
    unittest.main()
