"""SUPER_SESSION.md stays wired: rules that say the coordinator prompt carries their line really are in the prompt, the
session log keeps its last 5, and no step tells the coordinator to call something retired or missing on every wake.

Fail-first: SUPER_DOC=<copy of the 2026-10-18 file> python -m pytest this_file
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

    def test_rules_that_claim_a_prompt_line_have_it(self):
        rules = section(self.text, "Rules")
        prompt = section(self.text, "Prompt: start a super session")
        claim = re.compile(r"(Both|Every)\s+coordinator\s+prompts?\s+(\(below\)\s+)?carr(y|ies)\s+this\s+line", re.I)
        rule_blocks = re.split(r"\n(?=\d+\. \*\*)", "\n" + rules)
        claimed = [re.match(r"\s*(\d+)\.", b).group(1) for b in rule_blocks if re.match(r"\s*\d+\.", b) and claim.search(b)]
        self.assertGreaterEqual(len(claimed), 3)
        missing = [n for n in claimed if not re.search(rf"\bRule {n}\b", prompt, re.I)]
        self.assertEqual(missing, [], "rule claims its line is in the coordinator prompt, but the prompt lacks 'Rule N'")

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
        start_title = next(t for t in sections(self.text) if t.startswith("Start"))
        self.assertNotRegex(start_title, r"model Opus,")


if __name__ == "__main__":
    unittest.main()
