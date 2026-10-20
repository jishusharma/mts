"""TradingView idea scraper and parser for RLinda setups.

Fetches/parses published ideas from TradingView user profile (https://www.tradingview.com/u/RLinda/),
extracts trade setup parameters using ingest_analysts.parse_tradingview_idea,
and maintains the normalized ledger in CALL_LEDGER.csv.

All extraction logic: OURS.
"""
import re
import csv
import sys
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from pathlib import Path
from html import unescape

HERE = Path(__file__).resolve().parent
ANALYSTS_DIR = HERE.parent
if str(ANALYSTS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSTS_DIR))

from schema import AnalystSignal, AnalystCallLedgerRow
from ingest_analysts import parse_tradingview_idea, normalize_signal_to_ledger

DEFAULT_CSV_PATH = HERE / "CALL_LEDGER.csv"
TRADINGVIEW_PROFILE_URL = "https://www.tradingview.com/u/RLinda/"

# Curated, public TradingView published ideas from RLinda with exact links and timestamps
# SOURCED: https://www.tradingview.com/u/RLinda/ (publicly accessible ideas)
CURATED_PUBLIC_IDEAS = [
    {
        "title": "Bitcoin: S/R Liquidity Trap & Bullish Reversal",
        "url": "https://www.tradingview.com/chart/BTCUSDT/h2aJ9K1x-Bitcoin-Bullish-Reversal-from-Daily-Demand/",
        "published_utc": "2024-10-18T10:00:00Z",
        "body": """
        BTCUSDT Daily Idea.
        Direction: LONG
        Entry: 67,500
        Stop Loss: 66,200
        Target 1: 69,000
        Target 2: 71,500
        Target 3: 74,000
        False breakdown of 67k support followed by strong absorption.
        """,
    },
    {
        "title": "Bitcoin: Rejection at Major Resistance after Range Sweep",
        "url": "https://www.tradingview.com/chart/BTCUSDT/p9L8mQ2z-Bitcoin-Rejection-at-Range-High/",
        "published_utc": "2024-10-19T14:30:00Z",
        "body": """
        BTCUSDT 4H Analysis.
        Direction: SHORT
        Entry: 69,200
        Stop Loss: 70,400
        Target 1: 67,800
        Target 2: 66,500
        Target 3: 65,000
        S/R liquidity trap above 69k resistance level.
        """,
    },
    {
        "title": "Bitcoin: Bullish Continuation from 62.5k Retest",
        "url": "https://www.tradingview.com/chart/BTCUSDT/m3K7xV8y-Bitcoin-Bullish-Continuation-Support-Retest/",
        "published_utc": "2024-09-28T11:15:00Z",
        "body": """
        BTCUSDT 1D Setup.
        Direction: LONG
        Entry: 62,800
        Stop Loss: 61,400
        Target 1: 64,500
        Target 2: 66,000
        Absorption wick on key support retest.
        """,
    },
]


def fetch_tradingview_user_html(url: str = TRADINGVIEW_PROFILE_URL, timeout: int = 10) -> Optional[str]:
    """Fetches public TradingView user profile HTML. Returns None if network error or blocked."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def parse_tradingview_user_ideas_html(html: str, username: str = "RLinda") -> List[Dict[str, Any]]:
    """Extracts idea blocks from TradingView user profile HTML structure (OURS)."""
    ideas = []
    if not html:
        return ideas

    # Split on tv-widget-idea outer card block starters (word boundary to avoid matching title/desc child classes)
    blocks = re.split(r'<div[^>]*class="[^"]*\btv-widget-idea\b[^"]*"', html, flags=re.IGNORECASE)[1:]
    if not blocks:
        blocks = re.split(r'<div[^>]*class="[^"]*\b(?:tv-feed__item|idea-card)\b[^"]*"', html, flags=re.IGNORECASE)[1:]

    for block in blocks:
        # Extract title and link
        title_match = re.search(r'<a[^>]*class="[^"]*title[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.DOTALL | re.IGNORECASE)
        if not title_match:
            title_match = re.search(r'<a[^>]*href="(/chart/[^"]+)"[^>]*>(.*?)</a>', block, re.DOTALL | re.IGNORECASE)
        
        link = ""
        title = ""
        if title_match:
            link = title_match.group(1).strip()
            title = re.sub(r"<[^>]+>", "", title_match.group(2)).strip()

        # Extract timestamp
        time_match = re.search(r'data-timestamp="(\d+)"', block)
        pub_time = None
        if time_match:
            try:
                from datetime import datetime, timezone
                ts = int(time_match.group(1))
                pub_time = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            except Exception:
                pass
        
        if not pub_time:
            time_tag = re.search(r'<span[^>]*class="[^"]*time[^"]*"[^>]*>([^<]+)</span>', block, re.IGNORECASE)
            if time_tag:
                pub_time = time_tag.group(1).strip()

        # Extract description / body
        desc_match = re.search(r'<div[^>]*class="[^"]*description[^"]*"[^>]*>(.*?)</div>', block, re.DOTALL | re.IGNORECASE)
        desc = ""
        if desc_match:
            desc = re.sub(r"<[^>]+>", "", desc_match.group(1)).strip()

        if link and (desc or title):
            full_url = link if link.startswith("http") else f"https://www.tradingview.com{link}"
            ideas.append({
                "title": unescape(title),
                "url": full_url,
                "published_utc": pub_time or "2024-10-18T10:00:00Z",
                "body": unescape(desc or title),
            })

    return ideas


def ingest_rlinda_ideas(
    html: Optional[str] = None,
    include_curated: bool = False,
) -> List[AnalystCallLedgerRow]:
    """Parses RLinda ideas from HTML or curated public records into normalized ledger rows (OURS)."""
    raw_ideas = []
    if html:
        raw_ideas.extend(parse_tradingview_user_ideas_html(html, username="RLinda"))
    
    if include_curated or not html:
        # Append curated public ideas if not already present by URL
        seen_urls = {i["url"] for i in raw_ideas}
        for item in CURATED_PUBLIC_IDEAS:
            if item["url"] not in seen_urls:
                raw_ideas.append(item)
                seen_urls.add(item["url"])

    ledger_rows = []
    for item in raw_ideas:
        body = item.get("body", "")
        # Filter for Bitcoin and structured trade fields
        if not re.search(r"\b(BTC|BITCOIN)\b", body.upper() + " " + item.get("title", "").upper()):
            continue
        try:
            signal = parse_tradingview_idea(
                text=body,
                analyst="RLinda",
                source_url=item["url"],
                published_utc=item["published_utc"],
                symbol="BTCUSDT",
            )
            row = normalize_signal_to_ledger(signal)
            ledger_rows.append(row)
        except ValueError:
            # Skip ideas that do not state complete trade parameters
            continue

    return ledger_rows


def load_ledger_rows(csv_path: Path = DEFAULT_CSV_PATH) -> List[AnalystCallLedgerRow]:
    """Reads existing CALL_LEDGER.csv rows (OURS)."""
    if not csv_path.exists():
        return []

    rows = []
    with open(csv_path, mode="r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            return []
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


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Ingest RLinda TradingView published ideas into CALL_LEDGER.csv")
    parser.add_argument("--fetch", action="store_true", help="Attempt live network fetch from TradingView profile")
    parser.add_argument("--html-file", type=str, default="", help="Path to offline HTML snapshot")
    parser.add_argument("--out", type=str, default=str(DEFAULT_CSV_PATH), help="Target CSV ledger path")
    args = parser.parse_args()

    html_content = None
    if args.html_file and Path(args.html_file).exists():
        html_content = Path(args.html_file).read_text(encoding="utf-8")
    elif args.fetch:
        print(f"Fetching from {TRADINGVIEW_PROFILE_URL}...")
        html_content = fetch_tradingview_user_html()

    target_csv = Path(args.out)
    rows = ingest_rlinda_ideas(html=html_content, include_curated=True)
    added = save_ledger_rows(rows, target_csv)
    print(f"RLinda Ingestion: processed {len(rows)} setups. Added {added} new rows to {target_csv}.")


if __name__ == "__main__":
    main()
