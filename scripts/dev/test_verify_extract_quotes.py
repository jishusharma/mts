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

    def test_nested_metadata_header_is_not_searched(self):
        # Outer header, '# ---', nested '# Video ID .. # Description' block, second '# ---', then the spoken body.
        self._transcript("# Video: x\n# ---\n# Video ID: AAAAAAAAAAA\n# Description: zebra crossing quote only here\n# ---\n"
                         "[0:00] alpha beta\n[0:02] gamma delta\n")
        bad, out = self._check("zebra crossing quote only here", "BEGIN")
        self.assertEqual(bad, 1, out)
        self.assertEqual(self._check("beta gamma", "BEGIN")[0], 0)

    def test_single_header_transcript_unchanged(self):
        self._transcript("# Video: x\n# ---\n[0:00] alpha beta\n[0:02] gamma delta\n")
        self.assertEqual(self._check("alpha beta gamma", "BEGIN")[0], 0)

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

    def _stamped(self, quote, stamp, where="gps", pos="END"):
        ex = self.root / "extract.md"
        gps = f"**Source GPS: {VID} | {pos}**" + (f" ({stamp})" if where == "gps" else "")
        q = f'> "{quote}"' + (f" {stamp}" if where == "quote" else "")
        ex.write_text(f"{q}\n{gps}\n", encoding="utf-8")
        with redirect_stdout(io.StringIO()) as out:
            bad = v.check(ex)
        return bad, out.getvalue()

    TIMED = "[0:00] alpha beta gamma\n[76:01] delta epsilon zeta\n[1:30:45] eta theta iota\n"

    def test_stamp_far_from_marker_fails(self):
        # IR-09 case: stamp [76:01] but the quote sits at the 1:30:45 marker
        self._transcript(self.TIMED)
        bad, out = self._stamped("eta theta iota", "[76:01]")
        self.assertEqual(bad, 1, out)
        self.assertIn("STAMP-OFF", out)
        bad, out = self._stamped("eta theta iota", "[76:01]", "quote")
        self.assertIn("STAMP-OFF", out)

    def test_correct_stamp_passes_within_tolerance(self):
        self._transcript(self.TIMED)
        for st in ("[1:30:45]", "[90:45]", "[90:50]"):
            bad, out = self._stamped("eta theta iota", st)
            self.assertEqual(bad, 0, out)
            self.assertNotIn("STAMP", out)

    def test_stamp_in_untimed_transcript_is_unchecked_not_failed(self):
        self._transcript("alpha beta gamma delta epsilon\n")
        bad, out = self._stamped("beta gamma", "[76:01]", pos="BEGIN")
        self.assertEqual(bad, 0, out)
        self.assertIn("STAMP-UNCHECKED", out)

    def test_no_stamp_means_no_stamp_check(self):
        self._transcript(self.TIMED)
        bad, out = self._check("eta theta iota", "END")
        self.assertEqual(bad, 0, out)
        self.assertNotIn("STAMP", out)

    def test_empty_gps_quote_fails(self):
        """Reject an empty GPS quote instead of treating it as a valid dummy quote."""
        self._transcript("[0:00] alpha beta gamma\n")
        bad, out = self._check("", "BEGIN")
        self.assertNotEqual(bad, 0, out)
        self.assertEqual(bad, 1, out)
        self.assertIn("MISSING", out)

    def _cbp(self, evidence, cues=("[0:00] alpha beta gamma", "[0:02] delta epsilon zeta")):
        (self.root / "inbox").mkdir(exist_ok=True)
        (self.root / "inbox" / f"Jala_{VID}.txt").write_text(chr(10).join([*cues, ""]), encoding="utf-8")
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

    def test_cbp_quote_survives_caption_fillers_and_stutters(self):
        # real CBP rows: transcript "see uh bitcoin below", "this is is really"; the clean quote omits them
        cues = ("[0:00] i don t think that we see uh bitcoin below", "[0:03] if this is is really um a breakout")
        bad, out = self._cbp("we see Bitcoin below... if this is really a breakout", cues)
        self.assertEqual(bad, 0, out)

    def test_cbp_spliced_quote_still_fails(self):
        # restart in speech ("it s gonna it s going to be") is not a plain stutter: a stitched quote is not verbatim
        cues = ("[0:00] it s gonna it s going to be going up",)
        bad, out = self._cbp("it's gonna be going up", cues)
        self.assertEqual(bad, 1)
        self.assertIn("MISSING", out)

    def test_cbp_empty_ellipsis_fails(self):
        # quote normalizes to no spoken words: must fail
        cues = ("[0:00] alpha beta gamma",)
        bad, out = self._cbp("...", cues)
        self.assertEqual(bad, 1, out)
        self.assertIn("MISSING", out)

    def test_cbp_punctuation_only_fails(self):
        # punctuation only normalizes to empty: must fail
        cues = ("[0:00] alpha beta gamma",)
        bad, out = self._cbp("!?!", cues)
        self.assertEqual(bad, 1, out)
        self.assertIn("MISSING", out)

    def test_cbp_empty_quoted_evidence_fails(self):
        """Reject explicit empty CBP evidence instead of treating it as valid dummy evidence."""
        bad, out = self._cbp("")
        self.assertNotEqual(bad, 0, out)
        self.assertEqual(bad, 1, out)
        self.assertIn("MISSING", out)

    def test_cbp_partial_word_fails(self):
        # transcript has 'belong', evidence 'long' must not match partial word
        cues = ("[0:00] these assets belong together",)
        bad, out = self._cbp("long", cues)
        self.assertEqual(bad, 1, out)
        self.assertIn("MISSING", out)

    def test_pure_hindi_quote_ok_and_changed_number_missing(self):
        # Devanagari words must be compared, not dropped: an exact Hindi quote passes, a changed number fails.
        q1 = "आज बाजार में निफ्टी दस प्रतिशत गिरा"
        q2 = "स्टॉप लॉस 22500 पर रखें"
        self._transcript("[0:00] " + q1 + "।\n[0:03] " + q2 + "\n")
        bad, out = self._check(q1, "BEGIN")
        self.assertEqual(bad, 0, out)
        bad, out = self._check(q2, "MIDDLE")
        self.assertEqual(bad, 0, out)
        bad, out = self._check(q2.replace("22500", "22600"), "MIDDLE")
        self.assertEqual(bad, 1)
        self.assertIn("MISSING", out)
        bad, out = self._check(q1.replace("दस", "बीस"), "BEGIN")
        self.assertEqual(bad, 1, "a different Hindi number word must not match")

    def test_unicode_forms_and_joiners_compare_equal(self):
        # NFD vs NFC, zero-width joiners and the danda must not break an exact Hindi quote.
        import unicodedata
        word = "क्षति ड़ा"
        self.assertEqual(v.norm(unicodedata.normalize("NFD", word)), v.norm(unicodedata.normalize("NFC", word)))
        self.assertEqual(v.norm("क्‍ष"), v.norm("क्ष"))
        self.assertEqual(v.norm("निफ्टी। buy 5%"), "निफ्टी buy 5%")


class VerifyRepoDocCitesTest(unittest.TestCase):
    """layer_facts / layer review sheets: file:line cites and quoted repo-doc spans are resolved."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        body = [str(n) for n in range(1, 10)] + ["Volume gives intensity, not direction.", "end"]
        (self.root / "docs" / "a.md").write_text(chr(10).join(body) + chr(10), encoding="utf-8")
        self._old_root = v.ROOT
        v.ROOT = self.root
        v._doc_cache.clear()

    def tearDown(self):
        v.ROOT = self._old_root
        v._doc_cache.clear()
        self.tmp.cleanup()

    def _sheet(self, text):
        f = self.root / "sheet.md"
        f.write_text(text + chr(10), encoding="utf-8")
        with redirect_stdout(io.StringIO()) as out:
            bad = v.check(f)
        return bad, out.getvalue()

    def test_good_cite_and_quote_pass(self):
        bad, out = self._sheet('- Finding: "Volume gives intensity, not direction" (`docs/a.md:10`)')
        self.assertEqual(bad, 0, out)

    def test_missing_file_fails(self):
        bad, out = self._sheet("- x (`docs/nope.md:3`)")
        self.assertEqual(bad, 1, out)
        self.assertIn("NO-FILE", out)

    def test_line_past_end_fails(self):
        bad, out = self._sheet("- x (`docs/a.md:99`)")
        self.assertEqual(bad, 1, out)
        self.assertIn("NO-LINE", out)

    def test_invented_quote_fails(self):
        bad, out = self._sheet('- "ratio thresholds 1.5, 2.0, 2.5" (`docs/a.md:2`)')
        self.assertEqual(bad, 1, out)
        self.assertIn("NO-QUOTE", out)

    def test_quote_on_wrong_line_fails(self):
        bad, out = self._sheet('- "Volume gives intensity, not direction" (`docs/a.md:1`)')
        self.assertEqual(bad, 1, out)
        self.assertIn("WRONG-LINE", out)

    def test_comma_list_of_lines(self):
        bad, out = self._sheet('- "Volume gives intensity, not direction" (`docs/a.md:1,10`)')
        self.assertEqual(bad, 0, out)

    def test_pre_fix_volume_candles_ma_fails_current_passes(self):
        """b7ad6ad1c copy (invented quotes, wrong DEV window, absent files) must fail; 46ee60ea8 version passes."""
        import subprocess
        v.ROOT = self._old_root
        rel = "MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/volume_candles_ma.md"
        r = subprocess.run(["git", "-C", str(self._old_root), "show", f"b7ad6ad1c:{rel}"], capture_output=True)
        if r.returncode != 0:
            self.skipTest("commit b7ad6ad1c not in this clone")
        old = self.root / "old_volume_candles_ma.md"
        old.write_bytes(r.stdout)
        with redirect_stdout(io.StringIO()):
            self.assertGreater(v.check(old), 0)
        cur = self._old_root / rel
        if cur.is_file():
            with redirect_stdout(io.StringIO()) as out:
                self.assertEqual(v.check(cur), 0, out.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=1)
