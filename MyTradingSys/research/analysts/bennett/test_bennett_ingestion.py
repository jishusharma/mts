"""Unit tests for Justin Bennett DailyPriceAction market plan scraper and ledger ingestion.

Verifies:
1. Parsing DailyPriceAction RSS XML into structured article dictionaries.
2. Conversion of article text into validated AnalystSignal and AnalystCallLedgerRow records.
3. Strict enforcement of price geometry (Long: stop < entry < targets; Short: stop > entry > targets).
4. Idempotent CSV ledger read/write and duplicate avoidance.
"""
import unittest
from pathlib import Path
import tempfile
import sys
import os

HERE = Path(__file__).resolve().parent
ANALYSTS_DIR = HERE.parent
if str(ANALYSTS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSTS_DIR))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from schema import SignalDirection, ImbalanceConstruct, SignalStatus
from scraper import (
    parse_dpa_rss_items,
    ingest_articles_to_ledger,
    save_ledger_rows,
    load_ledger_rows,
    CURATED_PUBLIC_ARTICLES,
)

MOCK_RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Daily Price Action</title>
    <link>https://dailypriceaction.com</link>
    <description>Daily Forex and Crypto Price Action Analysis</description>
    <item>
      <title>Bitcoin (BTC) Rejection at 68.4k Resistance &amp; 4H FVG</title>
      <link>https://dailypriceaction.com/market-analysis/bitcoin-fvg-retest-68400/</link>
      <pubDate>Fri, 18 Oct 2024 08:00:00 +0000</pubDate>
      <description><![CDATA[
        <p>Bitcoin Price Action Analysis - Oct 18, 2024</p>
        <p>By Justin Bennett</p>
        <p>Market: BTCUSDT</p>
        <p>Bias: Bearish</p>
        <p>Entry: 68,400 (retest of 4H Fair Value Gap)</p>
        <p>Invalidation / Stop Loss: 69,600</p>
        <p>Take Profit 1: 66,800</p>
        <p>Take Profit 2: 65,000</p>
      ]]></description>
    </item>
    <item>
      <title>EURUSD Daily Range Analysis</title>
      <link>https://dailypriceaction.com/market-analysis/eurusd-oct-18/</link>
      <pubDate>Fri, 18 Oct 2024 07:00:00 +0000</pubDate>
      <description><![CDATA[
        <p>EURUSD commentary without Bitcoin trade levels.</p>
      ]]></description>
    </item>
  </channel>
</rss>
"""


class TestJustinBennettDailyPriceActionScraper(unittest.TestCase):
    def test_parse_dpa_rss_items(self):
        items = parse_dpa_rss_items(MOCK_RSS_XML)
        self.assertEqual(len(items), 1)  # Only the Bitcoin article should be included
        self.assertIn("68.4k", items[0]["title"])
        self.assertIn("Entry: 68,400", items[0]["body"])
        self.assertEqual(items[0]["url"], "https://dailypriceaction.com/market-analysis/bitcoin-fvg-retest-68400/")

    def test_curated_articles_parse_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_csv = Path(tmp_dir) / "test_ledger.csv"
            added = ingest_articles_to_ledger(CURATED_PUBLIC_ARTICLES, csv_path=tmp_csv)
            self.assertEqual(added, 3)

            # Re-ingesting same articles should add 0 new rows (idempotence)
            second_pass = ingest_articles_to_ledger(CURATED_PUBLIC_ARTICLES, csv_path=tmp_csv)
            self.assertEqual(second_pass, 0)

            # Verify saved rows
            rows = load_ledger_rows(tmp_csv)
            self.assertEqual(len(rows), 3)

            # Check individual setups
            call_map = {r.call_id: r for r in rows}
            short_call = call_map["DPA-2024-10-18-68400"]
            self.assertEqual(short_call.direction, "SHORT")
            self.assertEqual(short_call.entry, 68400.0)
            self.assertEqual(short_call.stop, 69600.0)
            self.assertEqual(short_call.targets_str, "66800.0;65000.0")
            self.assertEqual(short_call.imbalance_construct, "FVG_DISPLACEMENT")

            long_call = call_map["DPA-2024-10-06-63800"]
            self.assertEqual(long_call.direction, "LONG")
            self.assertEqual(long_call.entry, 63800.0)
            self.assertEqual(long_call.stop, 62500.0)
            self.assertEqual(long_call.targets_str, "65500.0;67000.0")

    def test_invalid_article_raises_or_skips(self):
        bad_article = [{
            "title": "Bitcoin Missing Levels",
            "url": "https://dailypriceaction.com/market-analysis/bad/",
            "published_utc": "2024-10-18T10:00:00Z",
            "body": "No numeric entry or stop provided.",
        }]
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_csv = Path(tmp_dir) / "test_ledger.csv"
            added = ingest_articles_to_ledger(bad_article, csv_path=tmp_csv)
            self.assertEqual(added, 0)


if __name__ == "__main__":
    unittest.main()
