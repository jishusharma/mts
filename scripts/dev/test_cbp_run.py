"""cbp_run.py: the extractor prompt carries the video metadata it is formatted with (audit 2026-10-30 finding 3:
PROMPT % {...} on a string without placeholders silently dropped analyst, date and title)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cbp_run


class Prompt(unittest.TestCase):
    def test_metadata_reaches_the_extractor(self):
        sent = {}

        def fake_run(cmd, input, **kw):
            sent["prompt"] = input
            sent["cmd"] = cmd

            class R:
                stdout, stderr = '{"bias": "NEUTRAL", "symbols": ["BTC"], "quotes": [], "trades": [], "pointers": []}', ""

                def check_returncode(self):
                    pass
            return R()

        got = cbp_run.llm_extract(("vid1", "Michael", "2026-10-29", 'BTC "break" ahead', Path("x")), "TRANSCRIPT", run=fake_run)
        self.assertEqual(got["bias"], "NEUTRAL")
        for s in ("Analyst: Michael.", "Published: 2026-10-29.", "Title: \"BTC 'break' ahead\".", "TRANSCRIPT"):
            self.assertIn(s, sent["prompt"])
        cmd = sent["cmd"]
        self.assertEqual(cmd[cmd.index("--setting-sources") + 1], "")  # no project hooks in a scheduled run


if __name__ == "__main__":
    unittest.main()
