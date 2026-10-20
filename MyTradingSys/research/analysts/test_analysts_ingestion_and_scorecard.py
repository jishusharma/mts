"""Test suite for analyst setup ingestion and scorecard evaluation.

Tests must fail before the implementation modules are created.
All numbers labeled SOURCED or OURS:
- FEE_PER_SIDE = 0.0005 (SOURCED: MyTradingSys/backtest/layers/FORMULAS.md:s17)
- FILL_WINDOW_HOURS = 24 (OURS: MyTradingSys/research/qriptal_2026-10-10/score_calls.py:30)
- OPEN_WINDOW_DAYS = 7 (OURS: MyTradingSys/research/qriptal_2026-10-10/score_calls.py:31)
"""
import unittest
import os
import sys
from pathlib import Path

# Ensure package directory is importable
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

# These imports will fail initially on old code
from schema import (
    AnalystSignal,
    AnalystCallLedgerRow,
    SignalDirection,
    SignalStatus,
    ImbalanceConstruct,
)
from ingest_analysts import (
    parse_tradingview_idea,
    parse_dailypriceaction_article,
    parse_social_call,
    normalize_signal_to_ledger,
)
from score_analysts import (
    score_signal_against_klines,
    compute_scorecard_metrics,
    calculate_binomial_power,
    FEE_PER_SIDE,
)


class TestAnalystSchema(unittest.TestCase):
    def test_valid_signal_creation(self):
        sig = AnalystSignal(
            call_id="RLINDA-20261018-BTC-01",
            analyst="RLinda",
            source_platform="TradingView",
            source_url="https://www.tradingview.com/chart/BTCUSDT/idea123/",
            published_utc="2026-10-18T12:00:00Z",
            symbol="BTCUSDT",
            direction=SignalDirection.LONG,
            imbalance_construct=ImbalanceConstruct.S_R_LIQUIDITY_TRAP,
            entry_price=82000.0,
            stop_loss=81000.0,
            targets=[83000.0, 84000.0, 85000.0],
            invalidation_condition="1H close below 81000",
            notes="TradingView published idea with Play button verification",
        )
        self.assertEqual(sig.call_id, "RLINDA-20261018-BTC-01")
        self.assertEqual(sig.risk_amount, 1000.0)  # OURS: |entry - stop|
        self.assertAlmostEqual(sig.risk_reward_t1, 1.0)  # OURS: |83000 - 82000| / 1000.0

    def test_invalid_prices_raise(self):
        with self.assertRaises(ValueError):
            # Stop loss higher than entry for LONG
            AnalystSignal(
                call_id="ERR-01",
                analyst="Test",
                source_platform="Twitter",
                source_url="https://x.com/test/1",
                published_utc="2026-10-18T12:00:00Z",
                symbol="BTCUSDT",
                direction=SignalDirection.LONG,
                imbalance_construct=ImbalanceConstruct.FVG_DISPLACEMENT,
                entry_price=80000.0,
                stop_loss=81000.0,  # Invalid for LONG
                targets=[82000.0],
            )


class TestAnalystIngestionParsers(unittest.TestCase):
    def test_parse_tradingview_idea_rlinda(self):
        sample_text = """
        Bitcoin (BTC/USDT) - Bullish Reversal from Daily Demand Zone
        Trading Idea by RLinda
        Direction: LONG
        Entry zone: 67,500
        Stop Loss: 66,200
        Target 1: 69,000
        Target 2: 71,500
        Target 3: 74,000
        Key level: False breakdown of 67k followed by absorption.
        """
        signal = parse_tradingview_idea(
            sample_text,
            analyst="RLinda",
            source_url="https://www.tradingview.com/chart/BTCUSDT/rlinda-idea/",
            published_utc="2026-10-18T09:30:00Z",
            symbol="BTCUSDT",
        )
        self.assertIsNotNone(signal)
        self.assertEqual(signal.direction, SignalDirection.LONG)
        self.assertEqual(signal.entry_price, 67500.0)
        self.assertEqual(signal.stop_loss, 66200.0)
        self.assertEqual(signal.targets, [69000.0, 71500.0, 74000.0])

    def test_parse_dailypriceaction_article(self):
        sample_article = """
        Bitcoin Price Action Analysis - Oct 18, 2026
        By Justin Bennett
        Market: BTCUSDT
        Bias: Bearish
        Entry: 68,400 (retest of 4H Fair Value Gap)
        Invalidation / Stop Loss: 69,600
        Take Profit 1: 66,800
        Take Profit 2: 65,000
        """
        signal = parse_dailypriceaction_article(
            sample_article,
            source_url="https://dailypriceaction.com/market-analysis/bitcoin-fvg-retest-2026-10-18",
            published_utc="2026-10-18T08:00:00Z",
        )
        self.assertIsNotNone(signal)
        self.assertEqual(signal.analyst, "Justin Bennett")
        self.assertEqual(signal.direction, SignalDirection.SHORT)
        self.assertEqual(signal.entry_price, 68400.0)
        self.assertEqual(signal.stop_loss, 69600.0)
        self.assertEqual(signal.targets, [66800.0, 65000.0])

    def test_parse_social_call_crypto_chase(self):
        tweet_text = "$BTC 4H FVG tapped. Looking to long 65,200 with invalidation below 64,100. Target 68,000 liquidity."
        signal = parse_social_call(
            tweet_text,
            analyst="Crypto Chase",
            source_url="https://x.com/Crypto_Chase/status/123456",
            published_utc="2026-10-18T14:15:00Z",
            symbol="BTCUSDT",
        )
        self.assertIsNotNone(signal)
        self.assertEqual(signal.direction, SignalDirection.LONG)
        self.assertEqual(signal.entry_price, 65200.0)
        self.assertEqual(signal.stop_loss, 64100.0)
        self.assertEqual(signal.targets, [68000.0])


class TestAnalystScorecardEngine(unittest.TestCase):
    def test_fee_constant(self):
        # SOURCED: MyTradingSys/backtest/layers/FORMULAS.md:s17
        self.assertEqual(FEE_PER_SIDE, 0.0005)

    def test_score_signal_win(self):
        sig = AnalystSignal(
            call_id="TEST-WIN-01",
            analyst="Crypto Chase",
            source_platform="Twitter",
            source_url="https://x.com/test",
            published_utc="2026-10-18T00:00:00Z",
            symbol="BTCUSDT",
            direction=SignalDirection.LONG,
            imbalance_construct=ImbalanceConstruct.FVG_DISPLACEMENT,
            entry_price=100.0,
            stop_loss=90.0,
            targets=[120.0],
        )
        # Synthetic 1m klines: [timestamp_ms, open, high, low, close]
        # Bar 0: opens 100, fills entry
        # Bar 1: low 95, high 125 -> reaches target 120
        start_ms = 1776470400000
        klines = [
            [start_ms, 100.0, 105.0, 98.0, 102.0],
            [start_ms + 60000, 102.0, 122.0, 95.0, 121.0],
        ]
        result = score_signal_against_klines(sig, klines)
        self.assertEqual(result["status"], SignalStatus.TARGET_HIT)
        self.assertEqual(result["exit_price"], 120.0)
        # Gross = +20.0, Net = 20 - 0.0005 * (100 + 120) = 20 - 0.11 = 19.89
        # Risk = 10.0, Net R = 19.89 / 10 = 1.989 (OURS)
        self.assertAlmostEqual(result["net_r"], 1.989, places=3)
        self.assertTrue(result["is_win"])

    def test_score_signal_stop_first_in_same_bar(self):
        sig = AnalystSignal(
            call_id="TEST-STOP-01",
            analyst="Roman Trading",
            source_platform="Twitter",
            source_url="https://x.com/test",
            published_utc="2026-10-18T00:00:00Z",
            symbol="BTCUSDT",
            direction=SignalDirection.LONG,
            imbalance_construct=ImbalanceConstruct.VOLUME_ABSORPTION,
            entry_price=100.0,
            stop_loss=90.0,
            targets=[120.0],
        )
        start_ms = 1776470400000
        # Bar 0: fills entry at 100
        # Bar 1: reaches both stop (85 <= 90) and target (125 >= 120)
        # Rule (SOURCED: MyTradingSys/research/qriptal_2026-10-10/score_calls.py:83-84):
        # Stop is checked first inside every candle!
        klines = [
            [start_ms, 100.0, 102.0, 99.0, 101.0],
            [start_ms + 60000, 101.0, 125.0, 85.0, 110.0],
        ]
        result = score_signal_against_klines(sig, klines)
        self.assertEqual(result["status"], SignalStatus.STOPPED)
        self.assertEqual(result["exit_price"], 90.0)
        self.assertFalse(result["is_win"])

    def test_metrics_and_binomial_power(self):
        trades = [
            {"is_win": True, "net_r": 2.0, "status": SignalStatus.TARGET_HIT},
            {"is_win": True, "net_r": 1.5, "status": SignalStatus.TARGET_HIT},
            {"is_win": False, "net_r": -1.02, "status": SignalStatus.STOPPED},
        ]
        metrics = compute_scorecard_metrics(trades)
        self.assertEqual(metrics["total_trades"], 3)
        self.assertEqual(metrics["wins"], 2)
        self.assertEqual(metrics["losses"], 1)
        self.assertAlmostEqual(metrics["win_rate"], 2.0 / 3.0, places=4)
        # Power test function check
        # With n = 0, power is 0.0 (SOURCED: MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:38)
        p_0 = calculate_binomial_power(0, claimed_win_rate=0.671, null_win_rate=0.5, alpha=0.05)
        self.assertEqual(p_0, 0.0)


class TestRLindaTradingViewScraper(unittest.TestCase):
    def test_rlinda_ingestion_and_ledger(self):
        from rlinda.scraper import (
            parse_tradingview_user_ideas_html,
            ingest_rlinda_ideas,
            save_ledger_rows,
            load_ledger_rows,
        )

        mock_html = """
        <div class="tv-widget-idea" data-author="RLinda">
          <a class="tv-widget-idea__title" href="/chart/BTCUSDT/rlinda-idea-1/">BTC Long Setup</a>
          <span class="tv-widget-idea__time" data-timestamp="1729245600">2024-10-18T10:00:00Z</span>
          <div class="tv-widget-idea__description-text">
            BTCUSDT Idea
            Direction: LONG
            Entry: 67,500
            Stop Loss: 66,200
            Target 1: 69,000
            Target 2: 71,500
          </div>
        </div>
        """
        ideas = parse_tradingview_user_ideas_html(mock_html, username="RLinda")
        self.assertEqual(len(ideas), 1)
        rows = ingest_rlinda_ideas(html=mock_html, include_curated=False)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].analyst, "RLinda")
        self.assertEqual(rows[0].entry, 67500.0)
        self.assertEqual(rows[0].stop, 66200.0)
        self.assertEqual(rows[0].targets_str, "69000.0;71500.0")


class TestJustinBennettDailyPriceActionScraper(unittest.TestCase):
    def test_bennett_ingestion_and_ledger(self):
        from bennett.scraper import (
            parse_dpa_rss_items,
            ingest_articles_to_ledger,
            load_ledger_rows,
            MOCK_RSS_XML,
        )
        import tempfile

        items = parse_dpa_rss_items(MOCK_RSS_XML)
        self.assertEqual(len(items), 1)
        self.assertIn("68.4k", items[0]["title"])

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_csv = Path(tmp_dir) / "test_ledger.csv"
            added = ingest_articles_to_ledger(items, csv_path=tmp_csv)
            self.assertEqual(added, 1)

            rows = load_ledger_rows(tmp_csv)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].analyst, "Justin Bennett")
            self.assertEqual(rows[0].direction, "SHORT")
            self.assertEqual(rows[0].entry, 68400.0)
            self.assertEqual(rows[0].stop, 69600.0)
            self.assertEqual(rows[0].targets_str, "66800.0;65000.0")


class TestCryptoChaseSocialScraper(unittest.TestCase):
    def test_cryptochase_ingestion_and_ledger(self):
        from cryptochase.scraper import (
            CURATED_CRYPTO_CHASE_POSTS,
            ingest_cryptochase_posts,
            load_ledger_rows,
            parse_crypto_chase_post,
        )
        import tempfile

        post = CURATED_CRYPTO_CHASE_POSTS[0]
        sig = parse_crypto_chase_post(post["text"], post["url"], post["published_utc"])
        self.assertEqual(sig.analyst, "Crypto Chase")
        self.assertEqual(sig.direction, SignalDirection.LONG)
        self.assertEqual(sig.entry_price, 65200.0)
        self.assertEqual(sig.stop_loss, 64100.0)
        self.assertEqual(sig.targets, [68000.0])

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_csv = Path(tmp_dir) / "test_ledger.csv"
            added = ingest_cryptochase_posts(CURATED_CRYPTO_CHASE_POSTS, csv_path=tmp_csv)
            self.assertEqual(added, 3)

            rows = load_ledger_rows(tmp_csv)
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[0].analyst, "Crypto Chase")
            self.assertEqual(rows[0].symbol, "BTCUSDT")
            self.assertEqual(rows[0].entry, 65200.0)
            self.assertEqual(rows[0].stop, 64100.0)
            self.assertEqual(rows[0].targets_str, "68000.0")


if __name__ == "__main__":
    unittest.main()
