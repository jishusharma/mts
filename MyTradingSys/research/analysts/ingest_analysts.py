"""Ingestion module for external analyst setups.

Parses semi-structured publications into standardized AnalystSignal instances:
1. TradingView published ideas (RLinda style: immutable, standardized Entry/SL/TP).
2. Daily Price Action market analyses (Justin Bennett style: daily text plans).
3. Social / X / Telegram posts (Crypto Chase / Roman Trading style: limit calls and invalidations).

All extraction and interpretation rules: OURS.
"""
import re
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pathlib import Path

from schema import (
    AnalystSignal,
    AnalystCallLedgerRow,
    SignalDirection,
    SignalStatus,
    ImbalanceConstruct,
)

_NUM_PATTERN = re.compile(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?|\b\d+(?:\.\d+)?\b")


def extract_first_number(text: str) -> Optional[float]:
    """Extracts the first valid floating-point number from text (OURS)."""
    m = _NUM_PATTERN.search(text or "")
    if not m:
        return None
    cleaned = m.group(0).replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def extract_all_numbers(text: str) -> List[float]:
    """Extracts all floating-point numbers from text (OURS)."""
    matches = _NUM_PATTERN.findall(text or "")
    nums = []
    for m in matches:
        try:
            nums.append(float(m.replace(",", "")))
        except ValueError:
            continue
    return nums


def extract_value_after_colon_or_keyword(line: str, keywords: List[str]) -> Optional[float]:
    """Extracts numeric value from a line, ignoring indices in labels like 'Target 1: 69,000' (OURS)."""
    if ":" in line:
        val_part = line.split(":", 1)[1]
        num = extract_first_number(val_part)
        if num is not None:
            return num
    pattern = r"(?:" + "|".join(re.escape(k) for k in keywords) + r")\s*\d*\s*[:=-]?\s*(.*)"
    m = re.search(pattern, line, re.IGNORECASE)
    if m:
        return extract_first_number(m.group(1))
    return extract_first_number(line)


def parse_tradingview_idea(
    text: str,
    analyst: str,
    source_url: str,
    published_utc: str,
    symbol: str = "BTCUSDT",
    call_id: Optional[str] = None,
) -> AnalystSignal:
    """Parses TradingView published idea text (e.g. RLinda standardized format).

    Format expectations:
    - Direction: BUY / LONG or SELL / SHORT
    - Entry: <price>
    - Stop Loss / SL: <price>
    - Target 1 / TP1: <price> (and optional Target 2, Target 3)
    """
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    direction = None
    entry_price = None
    stop_loss = None
    targets = []

    # Detect direction
    upper_text = text.upper()
    if re.search(r"\b(BUY|LONG|BULLISH)\b", upper_text):
        direction = SignalDirection.LONG
    elif re.search(r"\b(SELL|SHORT|BEARISH)\b", upper_text):
        direction = SignalDirection.SHORT

    for line in lines:
        l_upper = line.upper()
        if any(k in l_upper for k in ["ENTRY", "BUY AT", "SELL AT", "TRIGGER"]):
            num = extract_value_after_colon_or_keyword(line, ["ENTRY", "BUY AT", "SELL AT", "TRIGGER"])
            if num is not None and entry_price is None:
                entry_price = num
        elif any(k in l_upper for k in ["STOP LOSS", "STOP:", "SL:", "INVALIDATION"]):
            num = extract_value_after_colon_or_keyword(line, ["STOP LOSS", "STOP", "SL", "INVALIDATION"])
            if num is not None and stop_loss is None:
                stop_loss = num
        elif any(k in l_upper for k in ["TARGET", "TP", "TAKE PROFIT"]):
            num = extract_value_after_colon_or_keyword(line, ["TARGET", "TP", "TAKE PROFIT"])
            if num is not None:
                targets.append(num)

    if not entry_price:
        raise ValueError("Could not extract entry_price from TradingView idea text")
    if not stop_loss:
        raise ValueError("Could not extract stop_loss from TradingView idea text")
    if not targets:
        raise ValueError("Could not extract targets from TradingView idea text")
    if not direction:
        # Infer direction from entry vs stop (OURS)
        direction = SignalDirection.LONG if stop_loss < entry_price else SignalDirection.SHORT

    cid = call_id or f"TV-{analyst.upper().replace(' ', '')}-{published_utc[:10]}-{int(entry_price)}"

    return AnalystSignal(
        call_id=cid,
        analyst=analyst,
        source_platform="TradingView",
        source_url=source_url,
        published_utc=published_utc,
        symbol=symbol,
        direction=direction,
        imbalance_construct=ImbalanceConstruct.S_R_LIQUIDITY_TRAP,
        entry_price=entry_price,
        stop_loss=stop_loss,
        targets=targets,
        notes="Parsed from TradingView idea publication",
    )


def parse_dailypriceaction_article(
    text: str,
    source_url: str,
    published_utc: str,
    analyst: str = "Justin Bennett",
    symbol: str = "BTCUSDT",
    call_id: Optional[str] = None,
) -> AnalystSignal:
    """Parses DailyPriceAction analysis articles (Justin Bennett format)."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]

    direction = None
    entry_price = None
    stop_loss = None
    targets = []

    upper_text = text.upper()
    if "BIAS: BULLISH" in upper_text or "LONG" in upper_text:
        direction = SignalDirection.LONG
    elif "BIAS: BEARISH" in upper_text or "SHORT" in upper_text:
        direction = SignalDirection.SHORT

    for line in lines:
        l_upper = line.upper()
        if "ENTRY" in l_upper:
            num = extract_value_after_colon_or_keyword(line, ["ENTRY"])
            if num is not None and entry_price is None:
                entry_price = num
        elif any(k in l_upper for k in ["STOP LOSS", "INVALIDATION"]):
            num = extract_value_after_colon_or_keyword(line, ["STOP LOSS", "INVALIDATION"])
            if num is not None and stop_loss is None:
                stop_loss = num
        elif any(k in l_upper for k in ["TAKE PROFIT", "TARGET", "TP"]):
            num = extract_value_after_colon_or_keyword(line, ["TAKE PROFIT", "TARGET", "TP"])
            if num is not None:
                targets.append(num)

    if not entry_price or not stop_loss or not targets:
        raise ValueError(
            f"Failed parsing DailyPriceAction article: entry={entry_price}, stop={stop_loss}, targets={targets}"
        )
    if not direction:
        direction = SignalDirection.LONG if stop_loss < entry_price else SignalDirection.SHORT

    cid = call_id or f"DPA-{published_utc[:10]}-{int(entry_price)}"

    return AnalystSignal(
        call_id=cid,
        analyst=analyst,
        source_platform="DailyPriceAction",
        source_url=source_url,
        published_utc=published_utc,
        symbol=symbol,
        direction=direction,
        imbalance_construct=ImbalanceConstruct.FVG_DISPLACEMENT,
        entry_price=entry_price,
        stop_loss=stop_loss,
        targets=targets,
        notes="Parsed from Daily Price Action market plan",
    )


def parse_social_call(
    text: str,
    analyst: str,
    source_url: str,
    published_utc: str,
    symbol: str = "BTCUSDT",
    call_id: Optional[str] = None,
) -> AnalystSignal:
    """Parses unstructured social / X calls (Crypto Chase or Roman Trading)."""
    upper_text = text.upper()
    # Search for numbers associated with keywords
    entry_m = re.search(r"(?:long|short|entry|retest|limit)\s+(?:at\s+)?([0-9,]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    stop_m = re.search(r"(?:stop|invalidation|sl|below|above)\s+(?:below\s+|above\s+|at\s+)?([0-9,]+(?:\.[0-9]+)?)", text, re.IGNORECASE)
    target_m = re.search(r"(?:target|tp|take\s+profit)\s+(?:at\s+)?([0-9,]+(?:\.[0-9]+)?)", text, re.IGNORECASE)

    if not (entry_m and stop_m and target_m):
        raise ValueError(f"Could not extract entry/stop/target from social call: {text!r}")

    entry_price = float(entry_m.group(1).replace(",", ""))
    stop_loss = float(stop_m.group(1).replace(",", ""))
    targets = [float(target_m.group(1).replace(",", ""))]

    if re.search(r"\b(LONG|BUY|BULLISH)\b", upper_text):
        direction = SignalDirection.LONG
    elif re.search(r"\b(SHORT|SELL|BEARISH)\b", upper_text):
        direction = SignalDirection.SHORT
    else:
        direction = SignalDirection.LONG if stop_loss < entry_price else SignalDirection.SHORT

    # Imbalance construct detection
    if "FVG" in upper_text or "GAP" in upper_text:
        construct = ImbalanceConstruct.FVG_DISPLACEMENT
    elif "ABSORPTION" in upper_text or "VOLUME" in upper_text or "CVD" in upper_text:
        construct = ImbalanceConstruct.VOLUME_ABSORPTION
    else:
        construct = ImbalanceConstruct.FVG_DISPLACEMENT

    cid = call_id or f"SOC-{analyst.upper().replace(' ', '')}-{published_utc[:10]}-{int(entry_price)}"

    return AnalystSignal(
        call_id=cid,
        analyst=analyst,
        source_platform="Twitter/X",
        source_url=source_url,
        published_utc=published_utc,
        symbol=symbol,
        direction=direction,
        imbalance_construct=construct,
        entry_price=entry_price,
        stop_loss=stop_loss,
        targets=targets,
        notes=text[:120],
    )


def normalize_signal_to_ledger(signal: AnalystSignal) -> AnalystCallLedgerRow:
    """Converts an AnalystSignal into an AnalystCallLedgerRow for ledger storage (OURS)."""
    targets_str = ";".join(str(t) for t in signal.targets)
    return AnalystCallLedgerRow(
        call_id=signal.call_id,
        published_utc=signal.published_utc,
        analyst=signal.analyst,
        platform=signal.source_platform,
        symbol=signal.symbol,
        direction=signal.direction.value,
        imbalance_construct=signal.imbalance_construct.value,
        entry=signal.entry_price,
        stop=signal.stop_loss,
        targets_str=targets_str,
        status=signal.status.value,
        source_url=signal.source_url,
        notes=signal.notes or "",
    )
