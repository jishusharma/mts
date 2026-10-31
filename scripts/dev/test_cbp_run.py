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


class Verdicts(unittest.TestCase):
    def test_old_thesis_video_gets_a_verdict_not_a_row_and_bad_quote_is_dropped(self):
        import json
        import tempfile
        from datetime import datetime, timezone
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "v1_raw.txt").write_text(
                chr(10).join(["# Video ID: v1", "# Title: Alts", "# Published: 2026-10-16", "# Analyst: Jala",
                           "# Channel: @jalacrypto", "# ---", "we go to level 70 guys and aave looks fine", ""]), encoding="utf-8")
            got = {"bias": "BEARISH", "symbols": ["BTC"], "quotes": [], "trades": [], "pointers": [],
                   "bottom_call": "NOT_IN", "bottom_quote": "we go to level 70 guys",
                   "alts": [{"coin": "AAVE", "stance": "WATCH", "note": "n", "quote": "aave looks fine"},
                            {"coin": "SOL", "stance": "BUY", "note": "n", "quote": "never said this"}]}
            old, cbp_run.TRANSCRIPTS = cbp_run.TRANSCRIPTS, d
            try:
                added, total, rej = cbp_run.run_once(datetime(2026, 10, 31, tzinfo=timezone.utc), fetch=lambda c, k: None,
                                                     extract=lambda v, b: got, store=d / "rows.json")
            finally:
                cbp_run.TRANSCRIPTS = old
            v = json.loads((d / "verdicts.json").read_text(encoding="utf-8"))["v1"]
            self.assertEqual((added, total), (0, 0))
            self.assertEqual(v["bottom_call"], "NOT_IN")
            self.assertEqual([a["coin"] for a in v["alts"]], ["AAVE"])


class ExtractorFailure(unittest.TestCase):
    def test_llm_extract_error_carries_stderr(self):
        import subprocess

        def fake_run(cmd, input, **kw):
            class R:
                returncode, stdout, stderr = 1, "", "OAuth token expired"

                def check_returncode(self):
                    raise subprocess.CalledProcessError(1, cmd)
            return R()
        with self.assertRaises(subprocess.CalledProcessError) as cm:
            cbp_run.llm_extract(("v", "A", "2026-10-29", "t", Path("x")), "B", run=fake_run)
        self.assertIn("OAuth token expired", str(cm.exception.stderr))

    def test_good_video_kept_and_error_names_cause(self):
        import json
        import subprocess
        import tempfile
        from datetime import datetime, timezone
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for vid in ("v1", "v2"):
                (d / (vid + "_raw.txt")).write_text(chr(10).join(
                    ["# Video ID: " + vid, "# Title: T", "# Published: 2026-10-29", "# Analyst: Jala",
                     "# Channel: @j", "# ---", "btc looks fine here", ""]), encoding="utf-8")
            good = {"bias": "NEUTRAL", "symbols": ["BTC"], "quotes": ["btc looks fine"], "trades": [], "pointers": [],
                    "bottom_call": "NOT_IN", "bottom_quote": "", "alts": []}

            def ext(v, b):
                if v[0] == "v2":
                    raise subprocess.CalledProcessError(1, "claude", stderr="OAuth token expired")
                return good
            old, cbp_run.TRANSCRIPTS = cbp_run.TRANSCRIPTS, d
            try:
                with self.assertRaises(RuntimeError) as cm:
                    cbp_run.run_once(datetime(2026, 10, 31, tzinfo=timezone.utc), fetch=lambda c, k: None,
                                     extract=ext, store=d / "rows.json")
            finally:
                cbp_run.TRANSCRIPTS = old
            self.assertIn("OAuth token expired", str(cm.exception))
            self.assertIn("v1", json.loads((d / "verdicts.json").read_text(encoding="utf-8")))
            self.assertEqual(len(json.loads((d / "rows.json").read_text(encoding="utf-8"))["rows"]), 1)


if __name__ == "__main__":
    unittest.main()
