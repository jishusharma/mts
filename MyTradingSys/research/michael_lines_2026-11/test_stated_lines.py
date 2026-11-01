"""Tests for extract_stated_lines (card tl-michael-lines-detect-alert)."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import extract_stated_lines as x  # noqa: E402

TR = HERE.parent / "yt_feed_2026-10-31" / "transcripts_michael-pizzino-new10"


class T(unittest.TestCase):
    def test_known_quote(self):
        rows = x.extract_file(TR / "7wl0C1lVfRE_timed.txt")
        self.assertTrue(any(r["timestamp"] == "00:03:51" and "our trend line, our 50% level" in r["quote_window"]
                            for r in rows))

    def test_rejects_no_timestamp(self):
        self.assertEqual(x.extract_lines(["a trend line with no stamp", "[00:00:01] nothing"], "v"), [])

    def test_every_video_with_mention_has_row(self):
        vids = {r["video"] for r in x.extract_all(TR)}
        self.assertGreaterEqual(len(vids), 8)

    def test_kind_and_asset(self):
        r = x.extract_lines(["[00:01:00] gold bounced and a trend line break", "[00:01:02] then a retest"], "v")[0]
        self.assertEqual(r["asset"], "gold")
        self.assertIn("break", r["kind"])


if __name__ == "__main__":
    unittest.main()
