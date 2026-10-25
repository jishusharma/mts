"""Unit tests for Roman Trading volume-absorption call ingestion."""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANALYSTS_DIR = HERE.parent
if str(ANALYSTS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSTS_DIR))

from schema import ImbalanceConstruct, SignalDirection
from roman.scraper import (
    VERIFIED_ROMAN_POSTS, ingest_roman_posts, load_ledger_rows,
    parse_inbox_paste, parse_roman_post,
)

URL = "https://x.com/Roman_Trading/status/1000000000000000001"  # synthetic test fixture only
TS = "2026-01-02T03:04:05Z"
TEXT = "$BTC volume absorption at swing low, gap down rejected. Long at 90,000. Stop below 88,500. Target 94,000."


class TestRoman(unittest.TestCase):
    def test_parse_forces_volume_absorption(self):
        # text contains "gap": generic parser would say FVG; Roman must stay VOLUME_ABSORPTION
        sig = parse_roman_post(TEXT, URL, TS)
        self.assertEqual(sig.imbalance_construct, ImbalanceConstruct.VOLUME_ABSORPTION)
        self.assertEqual(sig.direction, SignalDirection.LONG)
        self.assertEqual((sig.entry_price, sig.stop_loss, sig.targets), (90000.0, 88500.0, [94000.0]))
        self.assertEqual(sig.analyst, "Roman Trading")

    def test_provenance_required(self):
        with self.assertRaises(ValueError):
            parse_roman_post(TEXT, "https://x.com/Roman_Trading", TS)
        with self.assertRaises(ValueError):
            parse_roman_post(TEXT, URL, "2026-01-02")
        with self.assertRaises(ValueError):
            parse_inbox_paste(TEXT, "https://x.com/other/status/1", TS)

    def test_inbox_skips_commentary_and_ledger_dedup(self):
        raw = "Great session everyone\n" + TEXT + "\n"
        sigs = parse_inbox_paste(raw, URL, TS)
        self.assertEqual(len(sigs), 1)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "CALL_LEDGER.csv"
            posts = [{"url": URL, "published_utc": TS, "text": TEXT}]
            self.assertEqual(ingest_roman_posts(posts, p), 1)
            self.assertEqual(ingest_roman_posts(posts, p), 0)
            rows = load_ledger_rows(p)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].source_url, URL)
            self.assertEqual(rows[0].imbalance_construct, "VOLUME_ABSORPTION")

    def test_shipped_posts_have_provenance(self):
        for p in VERIFIED_ROMAN_POSTS:
            parse_roman_post(p["text"], p["url"], p["published_utc"])


if __name__ == "__main__":
    unittest.main()
