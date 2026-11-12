"""Operator 2026-11-12 13:45Z: no Chrome tool until he names a deviceId. No rule text may tell a session to use "Browser 2"."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
FILES = ["CLAUDE.md", "scripts/dev/cbp_run.py", "scripts/dev/fetch_captions_timed.py",
         "scripts/dev/yt_transcript_sites.py", "MyTradingSys/system/YT_PROXY.md",
         "MyTradingSys/system/DSA_HAIKU_GUIDE.md"]


class NoBrowser2(unittest.TestCase):
    def test_no_browser2_instruction(self):
        for f in FILES:
            self.assertNotIn("Browser 2", (ROOT / f).read_text(encoding="utf-8"), f)

    def test_claude_md_names_device_rule(self):
        s = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("names a deviceId", s)


if __name__ == "__main__":
    unittest.main()
