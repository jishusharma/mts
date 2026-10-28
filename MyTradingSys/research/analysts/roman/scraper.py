"""Roman Trading volume-absorption / CVD-divergence social call listener (Twitter/X).

Parses calls via ingest_analysts.parse_social_call and forces the construct to
VOLUME_ABSORPTION (Construct 1, peer to Habib/Qriptal). Ledger: roman/CALL_LEDGER.csv.

No X API is used (paid). Calls enter only as operator inbox pastes or as verified
entries in VERIFIED_ROMAN_POSTS, each needing a verbatim status URL and published_utc.
Fabricated or unverified calls are never added (card scope_out).
All extraction logic: OURS.
"""
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
ANALYSTS_DIR = HERE.parent
if str(ANALYSTS_DIR) not in sys.path:
    sys.path.insert(0, str(ANALYSTS_DIR))

from schema import AnalystSignal, ImbalanceConstruct
from ingest_analysts import normalize_signal_to_ledger, parse_social_call
from cryptochase.scraper import load_ledger_rows, save_ledger_rows  # generic CSV helpers

DEFAULT_CSV_PATH = HERE / "CALL_LEDGER.csv"
TWITTER_PROFILE_URL = "https://x.com/Roman_Trading"
STATUS_URL_RE = re.compile(r"^https://(?:x|twitter)\.com/Roman_Trading/status/\d+$")
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

# Verified posts only: {"url", "published_utc", "symbol", "text"}. Empty until the operator
# pastes real calls or a free fetch is verified; X is login-walled and no post was verifiable
# at build time (DECISION OURS: ship empty rather than invent calls).
VERIFIED_ROMAN_POSTS: List[Dict[str, Any]] = []


def validate_provenance(source_url: str, published_utc: str) -> None:
    """Requires a verbatim Roman_Trading status URL and a UTC timestamp, else ValueError."""
    if not STATUS_URL_RE.match(source_url or ""):
        raise ValueError(f"source_url must be an exact Roman_Trading status URL: {source_url!r}")
    if not UTC_RE.match(published_utc or ""):
        raise ValueError(f"published_utc must be YYYY-MM-DDTHH:MM:SSZ: {published_utc!r}")


def parse_roman_post(
    text: str,
    source_url: str,
    published_utc: str,
    symbol: str = "BTCUSDT",
    call_id: Optional[str] = None,
) -> AnalystSignal:
    """Parses one Roman Trading post into a VOLUME_ABSORPTION AnalystSignal."""
    validate_provenance(source_url, published_utc)
    sig = parse_social_call(
        text=text,
        analyst="Roman Trading",
        source_url=source_url,
        published_utc=published_utc,
        symbol=symbol,
        call_id=call_id,
    )
    sig.imbalance_construct = ImbalanceConstruct.VOLUME_ABSORPTION
    return sig


def parse_inbox_paste(
    raw_text: str, source_url: str, published_utc: str, symbol: str = "BTCUSDT"
) -> List[AnalystSignal]:
    """Parses newline-delimited calls from one operator paste; non-call lines are skipped.

    Provenance (status URL + UTC) is mandatory: a bad value raises, never defaults.
    """
    validate_provenance(source_url, published_utc)
    signals = []
    lines = [ln.strip() for ln in raw_text.splitlines() if ln.strip()]
    for idx, line in enumerate(lines):
        try:
            signals.append(
                parse_roman_post(
                    line, source_url, published_utc, symbol,
                    call_id=f"SOC-ROMANTRADING-INBOX-{published_utc[:10]}-{idx + 1}",
                )
            )
        except ValueError as err:
            if "Could not extract" in str(err):
                continue
            raise
    return signals


def ingest_roman_posts(
    posts: Optional[List[Dict[str, Any]]] = None,
    csv_path: Path = DEFAULT_CSV_PATH,
) -> int:
    """Appends parsed posts to the ledger (dedup by call_id). Returns rows added."""
    if posts is None:
        posts = VERIFIED_ROMAN_POSTS
    rows = []
    for p in posts:
        try:
            sig = parse_roman_post(p["text"], p["url"], p["published_utc"], p.get("symbol", "BTCUSDT"))
            rows.append(normalize_signal_to_ledger(sig))
        except ValueError as err:
            print(f"Skipping post {p.get('url', '?')}: {err}")
    added = save_ledger_rows(rows, csv_path)
    print(f"Roman Ingestion: processed {len(rows)} setups. Added {added} new rows to {csv_path.name}.")
    return added


if __name__ == "__main__":
    ingest_roman_posts()
