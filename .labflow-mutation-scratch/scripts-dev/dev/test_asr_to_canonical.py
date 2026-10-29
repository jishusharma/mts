"""asr_to_canonical: timestamp format, line cutting, hallucination drop, and that the quote verifier can match
a quote that spans two timestamped lines (the whole point of the canonical format)."""
import json
import pathlib
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import asr_to_canonical as c  # noqa: E402
import verify_extract_quotes as v  # noqa: E402


def words(text, t0, step=0.4):
    out, t = [], t0
    for w in text.split():
        out.append((" " + w, t, t + step - 0.05))
        t += step
    return out


class T(unittest.TestCase):
    def test_stamp(self):
        self.assertEqual(c.stamp(5), "[0:05]")
        self.assertEqual(c.stamp(125.9), "[2:05]")
        self.assertEqual(c.stamp(3723), "[1:02:03]")

    def test_cut_at_pause_and_at_ten_seconds(self):
        w = words("one two three", 0) + words("four five six", 10.0)  # 8.8 s pause between the groups
        self.assertEqual([x for _, x in c.build_lines(w)], ["one two three", "four five six"])
        long = words(" ".join("w%d" % i for i in range(40)), 0)  # 16 s of speech, no pause
        lines = c.build_lines(long)
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(len(x.split()) <= 26 for _, x in lines))

    def test_sentence_end_cut_only_after_four_seconds(self):
        short = words("Yes. And then", 0)  # sentence ends at 0.4 s: no cut
        self.assertEqual(len(c.build_lines(short)), 1)
        longer = words("this is a fairly long first sentence that runs on for a while.", 0) + words("second one", 4.8)
        self.assertEqual(len(c.build_lines(longer)), 2)

    def test_hallucinated_credit_line_dropped(self):
        lines, dropped = c.collapse_loops([(0, "real speech"), (4, "Subs by www.zeoranger.co.uk"), (9, "more speech")])
        self.assertEqual([x for _, x in lines], ["real speech", "more speech"])
        self.assertEqual(dropped, 1)

    def test_loop_collapsed_after_three_repeats(self):
        lines, dropped = c.collapse_loops([(i, "thank you") for i in range(6)])
        self.assertEqual(len(lines), 3)
        self.assertEqual(dropped, 3)

    def test_quote_spanning_two_lines_matches_verifier_normalisation(self):
        with tempfile.TemporaryDirectory() as d:
            j = pathlib.Path(d) / "x.jsonl"
            rec = {"start": 0, "end": 6, "text": "", "avg_logprob": -0.2, "no_speech_prob": 0.1,
                   "compression_ratio": 1.5,
                   "words": [list(x) + [0.9] for x in words("the sellers got absorbed at the level", 0)
                             + words("and the buyers took control", 12.0)]}
            j.write_text(json.dumps(rec) + "\n", encoding="utf-8")
            out = pathlib.Path(d) / "x_raw.txt"
            c.main(["--jsonl", str(j), "--id", "abcdefghijk", "--model", "small.en", "--out", str(out)])
            text = out.read_text(encoding="utf-8")
        self.assertIn("MACHINE TRANSCRIPTION", text)
        self.assertIn("ASR faster-whisper small.en, local, 2026-10-16", text)
        body = v.norm(v.TIMESTAMP.sub(" ", text.split("# ---", 1)[1]))
        self.assertIn(v.norm("absorbed at the level and the buyers took control"), body)  # crosses the two lines


if __name__ == "__main__":
    unittest.main()
