"""Research-only RSI divergence event table and forward excursion measurement."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


DETECTOR = Path(__file__).resolve().parents[3] / "backtest/layers/rsi/rsi_divergence.py"
_SPEC = importlib.util.spec_from_file_location("mts_rsi_divergence_readonly", DETECTOR)
_DETECTOR = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_DETECTOR)

DEV_END_MS = 1719792000000  # 2024-07-01 00:00 UTC
MIN_BARS = 3  # sourced: RESULT.md, Malkan 3-10 bar rule
MAX_BARS = 10
MIN_RSI_DIFF = 0.0  # detector's sourced rule: any strictly higher RSI
HORIZON = 24


def _rsi14(close):
    """Wilder RSI-14, seeded with the first 14 close-to-close changes."""
    close = np.asarray(close, dtype=float)
    out = np.full(len(close), np.nan, dtype=float)
    if len(close) <= 14:
        return out
    delta = np.diff(close)
    gains = np.maximum(delta, 0.0)
    losses = np.maximum(-delta, 0.0)
    avg_gain = float(gains[:14].mean())
    avg_loss = float(losses[:14].mean())
    out[14] = 100.0 if avg_loss == 0 and avg_gain > 0 else (0.0 if avg_gain == 0 else 100 - 100 / (1 + avg_gain / avg_loss))
    for i in range(15, len(close)):
        avg_gain = (avg_gain * 13 + gains[i - 1]) / 14
        avg_loss = (avg_loss * 13 + losses[i - 1]) / 14
        out[i] = 100.0 if avg_loss == 0 and avg_gain > 0 else (0.0 if avg_gain == 0 else 100 - 100 / (1 + avg_gain / avg_loss))
    return out


def _atr14(high, low, close):
    high, low, close = (np.asarray(x, dtype=float) for x in (high, low, close))
    out = np.full(len(close), np.nan, dtype=float)
    if len(close) < 15:
        return out
    prev = np.r_[close[0], close[:-1]]
    tr = np.maximum(high - low, np.maximum(np.abs(high - prev), np.abs(low - prev)))
    value = float(np.mean(tr[1:15]))
    out[14] = value
    for i in range(15, len(close)):
        value = (value * 13 + tr[i]) / 14
        out[i] = value
    return out


def _valid_rsi(values):
    return [None if not np.isfinite(x) else float(x) for x in values]


def _event_rows(bars, timeframe, horizon):
    t = np.asarray(bars["t"], dtype=np.int64)
    close = np.asarray(bars["c"], dtype=float)
    rsi = bars.get("rsi")
    if rsi is None:
        rsi = _rsi14(close)
    rsi = _valid_rsi(rsi)
    events = []
    for kind in ("bullish", "bearish"):
        events.extend(_DETECTOR.rsi_divergence(close.tolist(), rsi, t.tolist(), MIN_BARS,
                                               MAX_BARS, kind, MIN_RSI_DIFF))
    events.sort(key=lambda e: (e["i"], e["event"]))
    out = []
    o, h, l = (np.asarray(bars[k], dtype=float) for k in ("o", "h", "l"))
    atr = np.asarray(bars["atr"], dtype=float)
    for event in events:
        entry_i = int(event["i"]) + 1
        row = dict(event, timeframe=timeframe, entry_i=entry_i, entry_t=int(t[entry_i]) if entry_i < len(t) else "",
                   side="long" if event["event"].startswith("bullish") else "short", status="OK",
                   entry="", r="", mfe_R="", mae_R="", bars_forward=0)
        if entry_i >= len(t) or int(t[entry_i]) >= DEV_END_MS:
            row["status"] = "NOT_IN_DATA"
            out.append(row)
            continue
        entry = float(o[entry_i])
        risk = float(atr[entry_i])
        end = min(len(t), entry_i + int(horizon))
        # The forward window cannot cross out of DEV, even if cached arrays contain later bars.
        end = min(end, int(np.searchsorted(t, DEV_END_MS, side="left")))
        if not np.isfinite(risk) or risk <= 0 or end - entry_i < int(horizon):
            row["status"] = "NOT_IN_DATA"
            out.append(row)
            continue
        highs, lows = h[entry_i:end], l[entry_i:end]
        if row["side"] == "long":
            mfe, mae = (float(np.max(highs) - entry) / risk, float(entry - np.min(lows)) / risk)
        else:
            mfe, mae = (float(entry - np.min(lows)) / risk, float(np.max(highs) - entry) / risk)
        row.update(entry=entry, r=risk, mfe_R=mfe, mae_R=mae, bars_forward=end - entry_i)
        out.append(row)
    return out


def build_event_table(bars_by_timeframe, timeframe=None, horizon=HORIZON):
    """Build rows from bars dict or {timeframe: bars}; arrays have t,o,h,l,c,atr."""
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    if "t" in bars_by_timeframe:
        return _event_rows(bars_by_timeframe, timeframe or "", horizon)
    rows = []
    for tf, bars in bars_by_timeframe.items():
        rows.extend(_event_rows(bars, tf, horizon))
    return rows


def _dev_1h(path):
    """Load only bars opening before the fixed DEV cutoff."""
    with np.load(path, allow_pickle=False) as z:
        t_all = z["t"]
        mask = t_all < DEV_END_MS
        return {k: z[k][mask] for k in ("t", "o", "h", "l", "c", "atr")}


def _to_4h(hourly):
    """Aggregate complete UTC 00/04/... buckets from DEV hourly bars."""
    t = np.asarray(hourly["t"])
    groups = {}
    for i, stamp in enumerate(t):
        bucket = int(stamp // 14_400_000 * 14_400_000)
        groups.setdefault(bucket, []).append(i)
    out = {k: [] for k in ("t", "o", "h", "l", "c", "atr")}
    for bucket, idx in groups.items():
        if len(idx) != 4 or any(int(t[idx[j]]) != bucket + j * 3_600_000 for j in range(4)):
            continue
        out["t"].append(bucket)
        out["o"].append(float(hourly["o"][idx[0]]))
        out["h"].append(float(np.max(hourly["h"][idx])))
        out["l"].append(float(np.min(hourly["l"][idx])))
        out["c"].append(float(hourly["c"][idx[-1]]))
    result = {k: np.asarray(v) for k, v in out.items() if k != "atr"}
    result["atr"] = _atr14(result["h"], result["l"], result["c"])
    return result


def run(data_path="F:/MTS/data/bigtrade/cache/perp/klines_1h.npz"):
    """Run the reproducible BTCUSDT 1h/4h DEV event table."""
    path = Path(data_path)
    if not path.exists():
        return []
    one = _dev_1h(path)
    four = _to_4h(one)
    return build_event_table({"1h": one, "4h": four})
