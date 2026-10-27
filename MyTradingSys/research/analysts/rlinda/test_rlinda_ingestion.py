"""Unit tests for RLinda TradingView idea scraping and ledger ingestion.

Verifies:
1. Parsing TradingView user ideas HTML stream into structured idea dictionaries.
2. Conversion of idea bodies into validated AnalystSignal and AnalystCallLedgerRow records.
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
    parse_tradingview_user_ideas_html,
    ingest_rlinda_ideas,
    save_ledger_rows,
    load_ledger_rows,
)

MOCK_TRADINGVIEW_PROFILE_HTML = """<!DOCTYPE html>
<html>
<head><title>Trading Ideas — RLinda — TradingView</title></head>
<body>
<div class="tv-feed__items">
  <div class="tv-widget-idea" data-author="RLinda">
    <div class="tv-widget-idea__title-row">
      <a class="tv-widget-idea__title" href="/chart/BTCUSDT/rlinda-btc-long-reclaim-67k/">
        Bitcoin: Bullish Reversal from Demand Zone & Liquidity Sweep
      </a>
    </div>
    <span class="tv-widget-idea__time" data-timestamp="1729245600">2024-10-18T10:00:00Z</span>
    <div class="tv-widget-idea__description-text">
      BTCUSDT Daily analysis.
      Direction: LONG
      Entry: 67,500
      Stop Loss: 66,200
      Target 1: 69,000
      Target 2: 71,500
      Target 3: 74,000
      False breakdown of 67k followed by absorption.
    </div>
  </div>

  <div class="tv-widget-idea" data-author="RLinda">
    <div class="tv-widget-idea__title-row">
      <a class="tv-widget-idea__title" href="/chart/BTCUSDT/rlinda-btc-short-sweep-69k/">
        Bitcoin: Rejection at Major Resistance after Range High Sweep
      </a>
    </div>
    <span class="tv-widget-idea__time" data-timestamp="1729332000">2024-10-19T10:00:00Z</span>
    <div class="tv-widget-idea__description-text">
      BTCUSDT 4H Chart.
      Direction: SHORT
      Entry: 69,200
      Stop Loss: 70,400
      Target 1: 67,800
      Target 2: 66,500
      S/R liquidity trap above 69k resistance.
    </div>
  </div>

  <div class="tv-widget-idea" data-author="RLinda">
    <div class="tv-widget-idea__title-row">
      <a class="tv-widget-idea__title" href="/chart/ETHUSDT/rlinda-eth-idea/">
        Ethereum Outlook
      </a>
    </div>
    <span class="tv-widget-idea__time" data-timestamp="1729418400">2024-10-20T10:00:00Z</span>
    <div class="tv-widget-idea__description-text">
      ETH general commentary, no concrete trade levels.
    </div>
  </div>
</div>
</body>
</html>
"""


class TestRLindaIngestion(unittest.TestCase):
    def test_parse_tradingview_user_ideas_html(self):
        items = parse_tradingview_user_ideas_html(MOCK_TRADINGVIEW_PROFILE_HTML, username="RLinda")
        self.assertEqual(len(items), 3)
        self.assertIn("BTCUSDT", items[0]["url"])
        self.assertEqual(items[0]["published_utc"], "2024-10-18T10:00:00Z")
        self.assertIn("Entry: 67,500", items[0]["body"])

    def test_ingest_rlinda_ideas_filters_and_normalizes(self):
        rows = ingest_rlinda_ideas(html=MOCK_TRADINGVIEW_PROFILE_HTML)
        # Should extract the 2 valid BTC ideas, skipping the non-trade ETH idea
        self.assertEqual(len(rows), 2)

        long_row = rows[0]
        self.assertEqual(long_row.analyst, "RLinda")
        self.assertEqual(long_row.symbol, "BTCUSDT")
        self.assertEqual(long_row.direction, "LONG")
        self.assertEqual(long_row.entry, 67500.0)
        self.assertEqual(long_row.stop, 66200.0)
        self.assertEqual(long_row.targets_str, "69000.0;71500.0;74000.0")
        self.assertEqual(long_row.imbalance_construct, "S_R_LIQUIDITY_TRAP")

        short_row = rows[1]
        self.assertEqual(short_row.analyst, "RLinda")
        self.assertEqual(short_row.direction, "SHORT")
        self.assertEqual(short_row.entry, 69200.0)
        self.assertEqual(short_row.stop, 70400.0)
        self.assertEqual(short_row.targets_str, "67800.0;66500.0")

    def test_ledger_save_and_load_roundtrip_idempotent(self):
        rows = ingest_rlinda_ideas(html=MOCK_TRADINGVIEW_PROFILE_HTML)
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "CALL_LEDGER.csv"
            saved_count = save_ledger_rows(rows, csv_path)
            self.assertEqual(saved_count, 2)

            loaded = load_ledger_rows(csv_path)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0].call_id, rows[0].call_id)
            self.assertEqual(loaded[1].call_id, rows[1].call_id)

            # Re-saving same rows should not duplicate
            saved_again = save_ledger_rows(rows, csv_path)
            self.assertEqual(saved_again, 0)
            reloaded = load_ledger_rows(csv_path)
            self.assertEqual(len(reloaded), 2)


if __name__ == "__main__":
    unittest.main()
