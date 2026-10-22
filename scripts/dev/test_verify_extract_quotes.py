"""Tests for verify_extract_quotes.py. Run: python scripts/dev/test_verify_extract_quotes.py"""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_extract_quotes as v  # noqa: E402

VID = "AAAAAAAAAAA"


class VerifyQuotesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "raw_transcripts_canonical").mkdir()
        self._old_root = v.ROOT
        v.ROOT = self.root

    def tearDown(self):
        v.ROOT = self._old_root
        self.tmp.cleanup()

    def _transcript(self, text):
        (self.root / "raw_transcripts_canonical" / f"{VID}_raw.txt").write_text(text, encoding="utf-8")

    def _check(self, quote, pos):
        ex = self.root / "extract.md"
        ex.write_text(f'> "{quote}"\n**Source GPS: {VID} | {pos}**\n', encoding="utf-8")
        with redirect_stdout(io.StringIO()) as out:
            bad = v.check(ex)
        return bad, out.getvalue()

    def test_quote_spanning_timestamp_markers_is_found(self):
        # Auto-caption transcripts carry a [m:ss] marker every few words; a verbatim quote spans them.
        self._transcript("[0:00] I'm a professional day trader and in\n[0:02] this video I will show you the best\n"
                         "[0:04] trading session of the last month\n")
        bad, out = self._check("and in this video I will show you", "BEGIN")
        self.assertEqual(bad, 0, out)

    def test_hour_marker_is_stripped(self):
        self._transcript("[1:02:03] alpha beta\n[1:02:05] gamma delta\n")
        bad, out = self._check("beta gamma", "BEGIN")
        self.assertEqual(bad, 0, out)

    def test_invented_quote_still_missing(self):
        self._transcript("[0:00] alpha beta\n[0:02] gamma delta\n")
        bad, out = self._check("beta epsilon", "MIDDLE")
        self.assertEqual(bad, 1)
        self.assertIn("MISSING", out)

    def test_numbers_in_speech_are_kept(self):
        # Only bracketed markers are removed; spoken numbers like 25,584 must still have to match.
        self._transcript("[0:00] reload 25,584 that is the level\n")
        self.assertEqual(self._check("reload 25,584 that is", "BEGIN")[0], 0)
        self.assertEqual(self._check("reload 25,585 that is", "BEGIN")[0], 1)

    def test_position_tag_checked(self):
        self._transcript("one two three four five six seven eight nine\n")
        self.assertEqual(self._check("one two", "BEGIN")[0], 0)
        bad, out = self._check("one two", "END")
        self.assertEqual(bad, 1)
        self.assertIn("POSITION", out)

    def _cbp(self, evidence):
        (self.root / "inbox").mkdir(exist_ok=True)
        (self.root / "inbox" / f"Jala_{VID}.txt").write_text(
            "\n".join(["[0:00] alpha beta gamma", "[0:02] delta epsilon zeta", ""]), encoding="utf-8")
        ex = self.root / "extractions.md"
        ex.write_text("\n".join([f"### Jala | 2026-09-27 | {VID} | Some title", "bottom_call: IN",
                                 f'evidence: "{evidence}"', "btc_levels: support=[1]", ""]), encoding="utf-8")
        with redirect_stdout(io.StringIO()) as out:
            bad = v.check(ex)
        return bad, out.getvalue()

    def test_cbp_evidence_line_verified(self):
        # CBP: one evidence line per video, id in the ### header, transcript in sibling inbox/, "..." joins fragments.
        bad, out = self._cbp("beta gamma delta... zeta")
        self.assertEqual(bad, 0, out)
        self.assertIn("OK", out)  # a checker that skips the line would also report 0 problems

    def test_cbp_invented_quote_fails(self):
        bad, out = self._cbp("beta gamma invented words")
        self.assertEqual(bad, 1)
        self.assertIn("MISSING", out)


if __name__ == "__main__":
    unittest.main(verbosity=1)
