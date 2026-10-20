"""Unit tests for Crypto Chase social call ingestion and ledger maintenance.
"""
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANALYSTS_DIR = HERE.parent
if str(ANALYSTS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSTS_DIR))

from schema import ImbalanceConstruct, SignalDirection
from cryptochase.scraper import (
    CURATED_CRYPTO_CHASE_POSTS,
    ingest_cryptochase_posts,
    load_ledger_rows,
    parse_crypto_chase_post,
    parse_inbox_paste,
    save_ledger_rows,
)


class TestCryptoChaseIngestion(unittest.TestCase):
    def test_parse_crypto_chase_post_long(self):
        text = "$BTC 4H Fair Value Gap retest. Limit long at 65,200. Invalidation below 64,100. Target 68,000 opposing liquidity pool."
        url = "https://x.com/Crypto_Chase/status/1847240182941016320"
        sig = parse_crypto_chase_post(text, source_url=url, published_utc="2024-10-18T14:15:00Z")

        self.assertEqual(sig.analyst, "Crypto Chase")
        self.assertEqual(sig.direction, SignalDirection.LONG)
        self.assertEqual(sig.entry_price, 65200.0)
        self.assertEqual(sig.stop_loss, 64100.0)
        self.assertEqual(sig.targets, [68000.0])
        self.assertEqual(sig.imbalance_construct, ImbalanceConstruct.FVG_DISPLACEMENT)

    def test_parse_crypto_chase_post_short(self):
        text = "$BTC clean 1D FVG rejection and deviation above range highs. Limit short at 67,800 with stop loss above 68,900. Target 64,200 range lows."
        url = "https://x.com/Crypto_Chase/status/1844001298418299136"
        sig = parse_crypto_chase_post(text, source_url=url, published_utc="2024-10-09T18:30:00Z")

        self.assertEqual(sig.direction, SignalDirection.SHORT)
        self.assertEqual(sig.entry_price, 67800.0)
        self.assertEqual(sig.stop_loss, 68900.0)
        self.assertEqual(sig.targets, [64200.0])

    def test_inbox_paste_and_ledger_dedup(self):
        inbox_raw = """
        $BTC 4H Fair Value Gap retest. Limit long at 65,200. Invalidation below 64,100. Target 68,000 opposing liquidity pool.
        Commentary without levels: BTC looks bullish today.
        $BTC clean 1D FVG rejection. Limit short at 67,800 with stop loss above 68,900. Target 64,200.
        """
        sigs = parse_inbox_paste(inbox_raw, published_utc="2024-10-18T12:00:00Z")
        self.assertEqual(len(sigs), 2)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_csv = Path(tmp_dir) / "test_ledger.csv"
            added = ingest_cryptochase_posts(CURATED_CRYPTO_CHASE_POSTS, csv_path=tmp_csv)
            self.assertEqual(added, 3)

            # Re-running same posts should add 0 new rows (dedup test)
            added_again = ingest_cryptochase_posts(CURATED_CRYPTO_CHASE_POSTS, csv_path=tmp_csv)
            self.assertEqual(added_again, 0)

            rows = load_ledger_rows(tmp_csv)
            self.assertEqual(len(rows), 3)


if __name__ == "__main__":
    unittest.main()
