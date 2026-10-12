"""check_spec_quotes.py: a quote is accepted only when it is verbatim inside the cited caption lines."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_spec_quotes as C

VID = "abcdefghijk"
CAPTIONS = "\n".join([
    "00:01 I can clearly see that there's no",
    "00:03 liquidity left. For the first position,",
    "00:05 I'm setting a stop-loss of 20 points",
    "00:07 in the DAX. The trend is short.",
]) + "\n"


class QuoteCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        (Path(self.tmp.name) / f"{VID}.txt").write_text(CAPTIONS, encoding="utf-8", newline="\n")

    def tearDown(self):
        self.tmp.cleanup()

    def bad(self, text):
        return C.check(text, self.tmp.name)

    def test_verbatim_across_lines_passes(self):
        self.assertEqual(self.bad(f'"there\'s no liquidity left. For the first position" ({VID}:1-2)'), [])

    def test_changed_word_fails(self):
        out = self.bad(f'"I\'m setting a stop-loss of 25 points" ({VID}:3)')
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0][3], "not verbatim in cited lines")

    def test_right_words_wrong_lines_fails(self):
        self.assertEqual(len(self.bad(f'"The trend is short." ({VID}:1-2)')), 1)

    def test_two_quotes_share_one_citation(self):
        text = f'"no liquidity left" and "a stop-loss of 20 points" ({VID}:1-2, 3-4)'
        self.assertEqual(len(C.pairs(text)), 2)
        self.assertEqual(self.bad(text), [])

    def test_missing_transcript_fails(self):
        self.assertEqual(self.bad('"something he never said here" (zzzzzzzzzzz:1-2)')[0][3], "transcript missing")

    def test_uncited_quote_is_ignored(self):
        self.assertEqual(C.pairs('He calls it "really risky and dangerous" in passing.'), [])

    def test_missing_folder_is_not_a_failure(self):
        spec = Path(self.tmp.name) / "s.md"
        spec.write_text("x", encoding="utf-8", newline="\n")
        self.assertEqual(C.main([str(spec), "--dir", str(Path(self.tmp.name) / "nope")]), 0)


if __name__ == "__main__":
    unittest.main()
