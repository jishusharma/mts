"""
candidate C2, intraday session momentum.
Source: Shen, Urquhart, Wang, Financial Review 57(2), 319-344, 2022 (T1):
the return over the first half-hour predicts the return of the last half-hour.
The 24/7 BTC adaptation (session = UTC day from `session_start_min`; "ny"/"london" = DST-aware day_gates open, B102) is UNDEFINED in the source
and is a parameter, not a claim. Independent layer, never a Tom filter.
"""

import datetime as dt
from typing import List, Dict

from MyTradingSys.backtest.layers.fabio.v3.day_gates import ny_open_utc, london_open_utc

_ANCHORS = {"ny": ny_open_utc, "london": london_open_utc}  # B102: DST-aware, None on weekends/holidays

def session_momentum_events(bars: List[Dict], bar_min: int = 1, session_start_min=0,
                            first_min: int = 30, entry_min: int = 30, min_abs: float = 0.0) -> List[Dict]:
    if not bars:
        raise ValueError("bars cannot be empty")
    if bar_min <= 0:
        raise ValueError("bar_min must be positive")
    if first_min <= 0:
        raise ValueError("first_min must be positive")
    if entry_min < first_min:
        raise ValueError("entry_min must be >= first_min")

    bar_ms = bar_min * 60000
    DAY = 86400000

    # Group bars by session
    sessions = {}
    for i, bar in enumerate(bars):
        t = bar["t"]
        if isinstance(session_start_min, str):
            # DST-aware named anchor: session starts at that day's open; days with no open are skipped
            day = dt.datetime.fromtimestamp(t // DAY * DAY / 1000, tz=dt.timezone.utc).date()
            o = _ANCHORS[session_start_min](day)
            if o is None:
                continue
            S = int(o.timestamp() * 1000)
            if S > t:
                prev = _ANCHORS[session_start_min](day - dt.timedelta(days=1))
                if prev is None:
                    continue
                S = int(prev.timestamp() * 1000)
        else:
            S = (t // DAY) * DAY + session_start_min * 60000
            if S > t:
                S -= DAY
        if S not in sessions:
            sessions[S] = []
        sessions[S].append((i, bar))

    events = []

    for S in sorted(sessions.keys()):
        session_bars = sessions[S]
        E = S + first_min * 60000

        # Find first_bar
        first_bar = None
        for i, bar in session_bars:
            if bar["t"] >= S and bar["t"] < E:
                first_bar = bar
                break

        if first_bar is None:
            continue

        # Find last_bar
        last_bar = None
        for i, bar in reversed(session_bars):
            if bar["t"] >= S and bar["t"] + bar_ms <= E:
                last_bar = bar
                break

        if last_bar is None:
            continue

        # Compute return
        open_price = first_bar["o"]
        if open_price <= 0:
            continue
        close_price = last_bar["c"]
        r_first = close_price / open_price - 1.0

        # Determine side
        side = None
        if r_first > min_abs:
            side = "long"
        elif r_first < -min_abs:
            side = "short"

        if side is None:
            continue

        # Find entry bar
        entry_time = S + entry_min * 60000
        entry_bar = None
        for i, bar in session_bars:
            if bar["t"] >= S and bar["t"] + bar_ms == entry_time:
                entry_bar = (i, bar)
                break

        if entry_bar is None:
            continue

        entry_idx, _ = entry_bar
        events.append({
            "i": entry_idx,
            "side": side,
            "r_first": r_first,
            "session_start": S
        })

    # Sort by entry index
    events.sort(key=lambda x: x["i"])
    return events
