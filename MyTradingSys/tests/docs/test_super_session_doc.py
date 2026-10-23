"""SUPER_SESSION.md stays wired: rules that say the coordinator prompt carries their line really are in the prompt, the
session log keeps its last 5, and no step tells the coordinator to call something retired or missing on every wake.

Fail-first: SUPER_DOC=<copy of the 2026-10-18 file> python -m pytest this_file (D1-D6 tests: the pre-2026-10-24 file)
"""
import os
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DOC = Path(os.environ.get("SUPER_DOC") or REPO / "MyTradingSys" / "system" / "SUPER_SESSION.md")


def sections(text):
    out = {}
    for part in re.split(r"^## ", text, flags=re.M)[1:]:
        title, _, body = part.partition("\n")
        out[title] = body
    return out


def section(text, prefix):
    hits = [b for t, b in sections(text).items() if t.startswith(prefix)]
    assert len(hits) == 1, prefix
    return hits[0]


class SuperSessionDoc(unittest.TestCase):
    def setUp(self):
        self.text = DOC.read_text(encoding="utf-8")

    def test_decisions_d1_to_d6_and_opus_needs_approval(self):
        """2026-10-24 design: one table D1-D6; Opus only when the operator names it or the card has approved_by."""
        table = section(self.text, "Decisions")
        for n in range(1, 7):
            self.assertTrue(re.search(rf"^\| D{n} \|", table, re.M), f"D{n}")
        d1 = re.search(r"^\| D1 \|.*$", table, re.M).group(0)
        self.assertIn("approved_by", d1)

    def test_prompt_is_one_supervisor_line(self):
        prompt = section(self.text, "Prompt: start a super session")
        block = re.search(r"```\n(.*?)\n```", prompt, re.S).group(1)
        self.assertTrue(block.startswith("You are Supervisor."))
        self.assertEqual(len(block.splitlines()), 1)

    def test_every_numbered_rule_is_in_the_rules_section(self):
        for title, body in sections(self.text).items():
            if title.startswith("Rules"):
                continue
            self.assertIsNone(re.search(r"^\d+\. \*\*", body, re.M), f"numbered rule outside Rules, in '{title}'")

    def test_session_log_keeps_last_five(self):
        log = section(self.text, "Session log")
        self.assertLessEqual(len([l for l in log.splitlines() if l.startswith("- ")]), 5)

    def test_no_dead_or_missing_calls(self):
        # gh is not installed on JIS-NUC / DESKTOP-F7IU69N (ci_watch hook covers CI); relay + watchdog are RETIRED
        for pat in (r"gh run list", r"relay\.py (heartbeat|stop|resume)"):
            self.assertIsNone(re.search(pat, self.text), pat)

    def test_start_model_follows_workers_rule_6(self):
        self.assertNotIn("new Opus session", self.text)
        start_title = next(t for t in sections(self.text) if t.startswith("Prompt"))
        self.assertNotRegex(start_title, r"model Opus,")

    def test_compaction_rebuilds_from_notes_file(self):
        """D5: state lives in the notes file, so a compaction cannot erase progress (10-15 audit: 39 of 68 lost work)."""
        d5 = re.search(r"^\| D5 \|.*$", self.text, re.M).group(0)
        self.assertIn("handover/SUPERVISOR_<L>.md", d5)
        self.assertIn("never from memory", d5)

if __name__ == "__main__":
    unittest.main()
