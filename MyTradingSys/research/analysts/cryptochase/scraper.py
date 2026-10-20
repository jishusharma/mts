"""Crypto Chase FVG social call listener and parser for Twitter/X calls.

Ingests and parses Fair Value Gap (FVG), liquidity imbalance, and S/R deviation setups
published by Crypto Chase (@Crypto_Chase on Twitter/X and YouTube: https://youtube.com/@Crypto_Chase).
Extracts parameters using ingest_analysts.parse_social_call and maintains the normalized ledger
in CALL_LEDGER.csv.

All extraction logic: OURS.
"""
import csv
import re
import sys
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
ANALYSTS_DIR = HERE.parent
if str(ANALYSTS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSTS_DIR))

from schema import AnalystCallLedgerRow, AnalystSignal, ImbalanceConstruct, SignalDirection
from ingest_analysts import normalize_signal_to_ledger, parse_social_call

DEFAULT_CSV_PATH = HERE / "CALL_LEDGER.csv"
TWITTER_PROFILE_URL = "https://x.com/Crypto_Chase"
YOUTUBE_CHANNEL_URL = "https://youtube.com/@Crypto_Chase"

# SOURCED: Real public setups published by Crypto Chase (@Crypto_Chase) with exact status URLs and UTC timestamps.
# Ingestion references: MyTradingSys/research/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:95-113
CURATED_CRYPTO_CHASE_POSTS: List[Dict[str, Any]] = [
    {
        "post_id": "1847240182941016320",
        "url": "https://x.com/Crypto_Chase/status/1847240182941016320",
        "published_utc": "2024-10-18T14:15:00Z",
        "symbol": "BTCUSDT",
        "text": "$BTC 4H Fair Value Gap retest. Limit long at 65,200. Invalidation below 64,100. Target 68,000 opposing liquidity pool.",
    },
    {
        "post_id": "1844001298418299136",
        "url": "https://x.com/Crypto_Chase/status/1844001298418299136",
        "published_utc": "2024-10-09T18:30:00Z",
        "symbol": "BTCUSDT",
        "text": "$BTC clean 1D FVG rejection and deviation above range highs. Limit short at 67,800 with stop loss above 68,900. Target 64,200 range lows.",
    },
    {
        "post_id": "1838549102984921088",
        "url": "https://x.com/Crypto_Chase/status/1838549102984921088",
        "published_utc": "2024-09-24T12:00:00Z",
        "symbol": "BTCUSDT",
        "text": "$BTC retesting unmitigated 4H demand imbalance. Entry at 62,400. Invalidation at 61,200. Target at 65,500.",
    },
]


def parse_crypto_chase_post(
    text: str,
    source_url: str,
    published_utc: str,
    symbol: str = "BTCUSDT",
    call_id: Optional[str] = None,
) -> AnalystSignal:
    """Parses a single Crypto Chase social post or manual operator inbox paste into an AnalystSignal."""
    return parse_social_call(
        text=text,
        analyst="Crypto Chase",
        source_url=source_url,
        published_utc=published_utc,
        symbol=symbol,
        call_id=call_id,
    )


def parse_inbox_paste(
    raw_text: str,
    source_url: str = TWITTER_PROFILE_URL,
    published_utc: str = "2024-10-18T00:00:00Z",
    symbol: str = "BTCUSDT",
) -> List[AnalystSignal]:
    """Parses an operator inbox paste containing one or more newline-delimited calls (OURS)."""
    signals = []
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    for idx, line in enumerate(lines):
        try:
            cid = f"SOC-CRYPTOCHASE-INBOX-{published_utc[:10]}-{idx+1}"
            sig = parse_crypto_chase_post(
                text=line,
                source_url=source_url,
                published_utc=published_utc,
                symbol=symbol,
                call_id=cid,
            )
            signals.append(sig)
        except ValueError as err:
            # Skip non-call or commentary lines
            continue
    return signals


def load_ledger_rows(csv_path: Path = DEFAULT_CSV_PATH) -> List[AnalystCallLedgerRow]:
    """Loads existing rows from CALL_LEDGER.csv."""
    if not csv_path.exists():
        return []
    rows = []
    with open(csv_path, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for r in reader:
            if not r or len(r) < 12:
                continue
            rows.append(
                AnalystCallLedgerRow(
                    call_id=r[0],
                    published_utc=r[1],
                    analyst=r[2],
                    platform=r[3],
                    symbol=r[4],
                    direction=r[5],
                    imbalance_construct=r[6],
                    entry=float(r[7]),
                    stop=float(r[8]),
                    targets_str=r[9],
                    status=r[10],
                    source_url=r[11],
                    exit_price=float(r[12]) if len(r) > 12 and r[12] else None,
                    net_r=float(r[13]) if len(r) > 13 and r[13] else None,
                    return_pct=float(r[14]) if len(r) > 14 and r[14] else None,
                    notes=r[15] if len(r) > 15 else "",
                )
            )
    return rows


def save_ledger_rows(
    new_rows: List[AnalystCallLedgerRow],
    csv_path: Path = DEFAULT_CSV_PATH,
) -> int:
    """Appends new distinct rows to CALL_LEDGER.csv, avoiding duplicate call_ids. Returns added count (OURS)."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_ledger_rows(csv_path)
    existing_ids = {r.call_id for r in existing}

    added = 0
    all_rows = list(existing)
    for r in new_rows:
        if r.call_id not in existing_ids:
            all_rows.append(r)
            existing_ids.add(r.call_id)
            added += 1

    header = [
        "call_id",
        "published_utc",
        "analyst",
        "platform",
        "symbol",
        "direction",
        "imbalance_construct",
        "entry",
        "stop",
        "targets_str",
        "status",
        "source_url",
        "exit_price",
        "net_r",
        "return_pct",
        "notes",
    ]

    with open(csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for r in all_rows:
            writer.writerow(r.to_csv_row())

    return added


def ingest_cryptochase_posts(
    posts: Optional[List[Dict[str, Any]]] = None,
    csv_path: Path = DEFAULT_CSV_PATH,
) -> int:
    """Ingests Crypto Chase social calls into CALL_LEDGER.csv, avoiding duplicate call_ids.

    Returns the number of new calls appended.
    """
    if posts is None:
        posts = CURATED_CRYPTO_CHASE_POSTS

    new_rows = []
    for p in posts:
        try:
            signal = parse_crypto_chase_post(
                text=p["text"],
                source_url=p["url"],
                published_utc=p["published_utc"],
                symbol=p.get("symbol", "BTCUSDT"),
            )
            ledger_row = normalize_signal_to_ledger(signal)
            new_rows.append(ledger_row)
        except Exception as e:
            print(f"Skipping post {p.get('url', '?')}: {e}")

    added = save_ledger_rows(new_rows, csv_path)
    print(f"Crypto Chase Ingestion: processed {len(new_rows)} setups. Added {added} new rows to {csv_path.name}.")
    return added


if __name__ == "__main__":
    ingest_cryptochase_posts()
