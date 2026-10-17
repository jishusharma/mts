"""Docs-lane test for RECALL.md (card krown-recall-check): every example row cites an extract line and a kline row,
the summary counts match the rows, and the fire-rate verdict matches the ceiling."""
import re
import unittest
from pathlib import Path

RECALL = Path(__file__).resolve().parents[3] / "research" / "krown_ta101_2026-10-13" / "RECALL.md"


def rows():
    out = []
    for line in RECALL.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (R\d+\w?) \|", line)
        if m:
            out.append([c.strip() for c in line.strip().strip("|").split("|")])
    return out


class RecallTable(unittest.TestCase):
    def test_every_row_cites_extract_line_and_kline_row(self):
        rs = rows()
        self.assertGreaterEqual(len(rs), 10)
        for r in rs:
            self.assertRegex(r[2], r"extract_[\w-]+\.md:\d+-\d+", r[0])
            self.assertRegex(r[4], r"(BTCUSDT|COINBASE)[\w.\-()]*\.csv", r[0])
            self.assertRegex(r[4], r"\d{4}-\d{2}-\d{2}", r[0])

    def test_summary_matches_rows(self):
        text = RECALL.read_text(encoding="utf-8")
        rs = rows()
        verified = sum(1 for r in rs if r[3].startswith("VERIFIED"))
        hits = sum(1 for r in rs if r[3].startswith("VERIFIED") and r[5].startswith("HIT"))
        m = re.search(r"Verified: (\d+)\. Recall hits within 2 bars: \*\*(\d+)\*\*", text)
        self.assertEqual((verified, hits), (int(m.group(1)), int(m.group(2))))
        self.assertIn("RECALL PASS" if hits >= 6 else "RECALL FAIL", text)

    def test_hit_means_within_two_bars(self):
        for r in rows():
            m = re.match(r"HIT offset ([+-]\d+)", r[5])
            if m:
                self.assertLessEqual(abs(int(m.group(1))), 2, r[0])
            self.assertNotIn("range_state coverage", r[5], r[0])
        hits = sum(1 for r in rows() if r[3].startswith("VERIFIED") and r[5].startswith("HIT"))
        self.assertRegex(RECALL.read_text(encoding="utf-8"), rf"hits within 2 bars: \*\*{hits}\*\* strict")

    def test_fire_rate_verdict_matches_ceiling(self):
        text = RECALL.read_text(encoding="utf-8")
        line = next(l for l in text.splitlines() if l.startswith("| BTCUSDT 1d |"))
        cells = re.findall(r"\(([\d.]+)\)", line)
        self.assertEqual(len(cells), 9)
        over = any(float(x) > 1.0 for x in cells)
        self.assertIn("FIRE RATE FAIL" if over else "FIRE RATE PASS", text)

    def test_sealed_examples_not_read(self):
        text = RECALL.read_text(encoding="utf-8")
        for mark in ("2025-", "2026-"):
            self.assertNotRegex("\n".join(l for l in text.splitlines() if l.startswith("| R")), mark)


if __name__ == "__main__":
    unittest.main()
