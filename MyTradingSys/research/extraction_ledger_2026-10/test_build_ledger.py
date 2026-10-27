"""Fixture tree: 1 captions id, 1 hindi id, 1 orphan transcript; bad quote must give FAIL."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_ledger as bl  # noqa: E402

CAP, HIN, ORP = "AAAAAAAAAAA", "BBBBBBBBBBB", "CCCCCCCCCCC"


def transcript(path, analyst, text):
    path.write_text(f"# Video ID: x\n# Analyst: {analyst}\n# ---\n{text}\n", encoding="utf-8")


class LedgerTest(unittest.TestCase):
    def make(self, tmp, bad_quote):
        t = tmp / "raw_transcripts_canonical"
        t.mkdir()
        transcript(t / f"{CAP}_raw.txt", "Krown", "price tends to revisit the level before it breaks out of the range")
        transcript(t / f"{HIN}_hi_raw.txt", "Malkan", "namaste yeh rsi hai")
        transcript(t / f"{ORP}_raw.txt", "Tom", "nothing extracted from this one")
        e = tmp / "extracts" / "fresh"
        e.mkdir(parents=True)
        q = "price will melt into the sun" if bad_quote else "price tends to revisit the level"
        (e / f"extract_{CAP}_fresh.md").write_text(f'> "{q}"\n**Source GPS: {CAP} | BEGIN**\n', encoding="utf-8")
        (e / f"extract_{HIN}_fresh.md").write_text(
            f'- Video ID: {HIN}\n- Language: hi\n> "this is rsi"\n- Hindi original: "yeh rsi hai"\n', encoding="utf-8")
        lp = tmp / "MyTradingSys" / "backtest" / "layers" / "krown" / "params"
        lp.mkdir(parents=True)
        (lp / "p.json").write_text('{"src": "%s"}' % CAP, encoding="utf-8")

    def run_build(self, bad):
        tmp = Path(tempfile.mkdtemp())
        self.make(tmp, bad)
        out = tmp / "out"
        rows, gaps = bl.build(tmp, out)
        return rows, gaps, out

    def test_three_rows_and_orphan(self):
        rows, gaps, out = self.run_build(False)
        self.assertEqual(sorted(r["video_id"] for r in rows), sorted([CAP, HIN, ORP]))
        by = {r["video_id"]: r for r in rows}
        self.assertEqual(by[CAP]["method"], "captions")
        self.assertEqual(by[CAP]["quotes_verified"], "PASS")
        self.assertEqual(by[CAP]["used_by"], "krown:p.json")
        self.assertEqual((by[HIN]["method"], by[HIN]["language"], by[HIN]["quotes_verified"]), ("hindi_asr", "hi", "PASS"))
        self.assertIn(ORP, gaps["no_extract"])
        self.assertIn(ORP, (out / "GAPS.md").read_text(encoding="utf-8"))
        with (out / "EXTRACTION_LEDGER.csv").open(encoding="utf-8", newline="") as f:
            self.assertEqual(len(list(csv.DictReader(f))), 3)

    def test_bad_quote_fails(self):
        rows, gaps, _ = self.run_build(True)
        self.assertEqual({r["video_id"]: r for r in rows}[CAP]["quotes_verified"], "FAIL")
        self.assertTrue(any(CAP in x for x in gaps["bad_quotes"]))


if __name__ == "__main__":
    unittest.main()
