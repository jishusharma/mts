"""Weekly-low break -> bounce -> hold under RSI 60 near the upper Bollinger band (1h, closed candles only).

Pure functions, no I/O. OBSERVATION ONLY: this setup is UNVALIDATED (PRE_REG: research/wlow_bounce_bbrsi60_2026-10-16/PRE_REG.md).
It never produces an order or a side. Candle = dict with keys t (open time ms, UTC), o, h, l, c, v, tbv (taker buy volume).
Parameter labels: SOURCED = operator words 2026-10-16; OURS = judgement (see PRE_REG section 2).
"""
import statistics
from datetime import datetime, timezone

from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core

HOUR_MS = 3_600_000
PARAMS = {
    "bb_n": 20, "bb_k": 2.0,   # SOURCED (operator: Bollinger band; chart settings 20, 2)
    "rsi_n": 14,               # SOURCED (operator chart RSI 14)
    "rsi_hi": 60.0,            # SOURCED ("just under the RSI 60 line")
    "rsi_lo": 52.0,            # OURS (chart showed 56-58; floor 4 points below)
    "slope_max": 3.0,          # OURS ("flat RSI": |RSI change| over the hold window <= 3 points)
    "band_x": 0.005,           # OURS ("near the upper edge": close >= upper*(1-0.5%))
    "K": 4,                    # OURS (chart showed 5-6 candles; 4 keeps more events)
    "B": 6,                    # OURS (chart showed a 2-3 candle bounce; 6 = double)
    "HMAX": 24,                # OURS (trigger must fire within 24 bars of the break)
    "COOLDOWN": 24,            # OURS (no new episode within 24 bars of the previous episode start)
    "week_mode": "iso",        # OURS: "iso" = prior completed ISO week (Mon 00:00 UTC); "roll168" = prior 168 bars
}


def bollinger_upper(closes, n=20, k=2.0):
    """SMA(n) + k * population stdev (TradingView convention). None before index n-1."""
    out = [None] * len(closes)
    for i in range(n - 1, len(closes)):
        w = closes[i - n + 1:i + 1]
        out[i] = sum(w) / n + k * statistics.pstdev(w)
    return out


def indicators(candles, p=PARAMS):
    closes = [x["c"] for x in candles]
    rsi = rsi_core(closes, p["rsi_n"]) if len(closes) > p["rsi_n"] else [None] * len(closes)
    return bollinger_upper(closes, p["bb_n"], p["bb_k"]), rsi


def _monday_ms(t_ms):
    d = datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc)
    day0 = int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)
    return day0 - d.weekday() * 24 * HOUR_MS


def weekly_low_series(candles, mode="iso"):
    """W[i] = the reference weekly low known at the OPEN of bar i (uses bars strictly before i), else None.
    iso: min low of the previous completed ISO week, only if that week has all 168 hourly bars.
    roll168: min low of bars i-168..i-1 (requires 168 contiguous bars)."""
    n = len(candles)
    W = [None] * n
    if mode == "roll168":
        for i in range(168, n):
            if candles[i]["t"] - candles[i - 168]["t"] == 168 * HOUR_MS:
                W[i] = min(x["l"] for x in candles[i - 168:i])
        return W
    by_week = {}
    for x in candles:
        by_week.setdefault(_monday_ms(x["t"]), []).append(x["l"])
    wk_low = {m: min(v) for m, v in by_week.items() if len(v) == 168}
    for i, x in enumerate(candles):
        W[i] = wk_low.get(_monday_ms(x["t"]) - 168 * HOUR_MS)
    return W


def hold_ok(candles, bb, rsi, t, p=PARAMS):
    """The hold condition over bars t-K+1..t (all closed): close >= upper*(1-X), RSI in [lo, hi), |RSI[t]-RSI[t-K+1]| <= slope_max."""
    K = p["K"]
    if t - K + 1 < 0:
        return False
    for i in range(t - K + 1, t + 1):
        if bb[i] is None or rsi[i] is None:
            return False
        if candles[i]["c"] < bb[i] * (1 - p["band_x"]) or not (p["rsi_lo"] <= rsi[i] < p["rsi_hi"]):
            return False
    return abs(rsi[t] - rsi[t - K + 1]) <= p["slope_max"]


def find_events(candles, p=PARAMS, ind=None):
    """All episodes. Each: {start, W, bounce, trigger, status}. status: TRIGGERED | NO_BOUNCE | EXPIRED | BROKEN | BOUNCED
    (BROKEN / BOUNCED only for an episode whose window is still open at the end of the data = ARMED)."""
    bb, rsi = ind if ind is not None else indicators(candles, p)
    W = weekly_low_series(candles, p["week_mode"])
    n = len(candles)
    events, last_start, i = [], -10**9, 0
    while i < n:
        if W[i] is None or candles[i]["l"] >= W[i] or i - last_start < p["COOLDOWN"]:
            i += 1
            continue
        ev = {"start": i, "W": W[i], "bounce": None, "trigger": None, "status": None}
        last_start = i
        j = next((q for q in range(i, min(i + p["B"], n - 1) + 1) if candles[q]["c"] > ev["W"]), None)
        if j is None:
            ev["status"] = "BROKEN" if i + p["B"] > n - 1 else "NO_BOUNCE"
        else:
            ev["bounce"] = j
            end = min(i + p["HMAX"], n - 1)
            t = next((q for q in range(j + p["K"], end + 1) if hold_ok(candles, bb, rsi, q, p)), None)
            if t is not None:
                ev["trigger"], ev["status"] = t, "TRIGGERED"
            else:
                ev["status"] = "BOUNCED" if i + p["HMAX"] > n - 1 else "EXPIRED"
        events.append(ev)
        i += 1
    return events


def status_now(candles, p=PARAMS, active_bars=6):
    """Latest state on closed candles. ACTIVE = an event triggered within the last `active_bars` bars; ARMED = broke the weekly low
    and the window is still open (BROKEN waiting for a bounce, BOUNCED waiting for the hold); else IDLE."""
    evs = find_events(candles, p)
    n = len(candles)
    for e in reversed(evs):
        if e["status"] == "TRIGGERED" and n - 1 - e["trigger"] <= active_bars:
            return {"state": "ACTIVE", "event": e}
        if e["status"] in ("BROKEN", "BOUNCED"):
            return {"state": "ARMED", "event": e}
    return {"state": "IDLE", "event": evs[-1] if evs else None}


def delta_sum(candles, a, b):
    """Sum of taker delta (2*tbv - v) over bars a..b inclusive (kline-based; equals the CVD change over the same bars)."""
    return sum(2 * x["tbv"] - x["v"] for x in candles[a:b + 1])
