"""gemini-task-dispatch-assignment: ROUTING.md names one explicit tag for cards meant for the Gemini lane, so a Gemini builder
picks them without guessing (lane CODEX is shared with GPT)."""
import unittest
from pathlib import Path

ROUTING = Path(__file__).resolve().parents[2] / "MyTradingSys" / "system" / "ROUTING.md"


class GeminiTagTest(unittest.TestCase):
    def test_routing_defines_gemini_title_tag(self):
        t = ROUTING.read_text(encoding="utf-8")
        self.assertIn("[GEMINI]", t)
        self.assertIn("tasks.py list --lane CODEX", t)


class CodexRunSkipsGeminiTest(unittest.TestCase):
    def test_pick_skips_gemini_tagged_cards(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
        import codex_run
        cards = [{"id": "g1", "title": "[GEMINI] blind read", "lane": "CODEX"}, {"id": "p1", "title": "audit", "lane": "CODEX"}]
        got = codex_run.pick(cards, set(), {})
        self.assertEqual(got["id"], "p1")


if __name__ == "__main__":
    unittest.main()
