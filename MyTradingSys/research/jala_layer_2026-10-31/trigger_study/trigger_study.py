"""Jala 400D close trigger study (pure functions). DEV bars only: forward windows must end before DEV_END.
Windows 200/400 SOURCED (method_jala.md:4-23); everything else OURS (see PRE_REG.md)."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "backtest"))
import splits  # noqa: E402

RT_DRAG = 0.002  # round trip, spot taker 0.1% x2 (OURS)
HORIZONS = (10, 30, 60)  # OURS
DIRECTION = {"under": -1, "death": -1, "over": +1, "golden": +1}  # OURS: trade the side Jala's text implies


def events(close, kind, fast=200, slow=400):
    """Dates where the trigger first becomes true (state flips). SMA bars may come from pre-DEV warmup."""
    close = close.sort_index()
    if kind in ("under", "over"):
        s = close.rolling(slow, min_periods=slow).mean()
        below = close < s
        valid = s.notna() & s.shift(1).notna()
        if kind == "under":
            hit = below & ~below.shift(1, fill_value=False) & valid & (close.shift(1) >= s.shift(1))
        else:
            hit = (close > s) & (close.shift(1) <= s.shift(1)) & valid
    else:
        f = close.rolling(fast, min_periods=fast).mean()
        s = close.rolling(slow, min_periods=slow).mean()
        d = f - s
        valid = d.notna() & d.shift(1).notna()
        if kind == "golden":
            hit = (d > 0) & (d.shift(1) <= 0) & valid
        else:
            hit = (d < 0) & (d.shift(1) >= 0) & valid
    return list(close.index[hit.fillna(False).values])


def dev_event_filter(close, dates, h):
    """Keep dates inside DEV whose exit bar (t+h days) is also before DEV_END and exists."""
    out = []
    for t in dates:
        if t < splits.DEV_START or t + pd.Timedelta(days=h) >= splits.DEV_END:
            continue
        if (t + pd.Timedelta(days=h)) in close.index and t in close.index:
            out.append(t)
    return out


def fwd_net(close, dates, h, sign, rt=RT_DRAG):
    c = close
    return np.array([sign * (c[t + pd.Timedelta(days=h)] / c[t] - 1) - rt for t in dates])


def eligible_days(close, h):
    s400 = close.rolling(400, min_periods=400).mean()
    days = [t for t in close.index[s400.notna().values]]
    return dev_event_filter(close, days, h)


def null_means(elig_by_sym, closes, sym_counts, h, sign, draws=2000, seed=7, rt=RT_DRAG):
    """Per draw: for each symbol pick as many random eligible days as it has events; mean net over all picks."""
    rng = np.random.default_rng(seed)
    pre = {s: fwd_net(closes[s], elig_by_sym[s], h, sign, rt) for s in sym_counts if sym_counts[s] and len(elig_by_sym[s])}
    out = np.empty(draws)
    for i in range(draws):
        tot, n = 0.0, 0
        for s, k in sym_counts.items():
            if s not in pre:
                continue
            v = pre[s][rng.integers(0, len(pre[s]), size=k)]
            tot += v.sum(); n += k
        out[i] = tot / n if n else np.nan
    return out


def week_block_ci(dates, vals, draws=2000, seed=11):
    """Bootstrap mean resampling ISO-week blocks of events (pooled across symbols)."""
    wk = pd.Series([f"{d.isocalendar()[0]}-{d.isocalendar()[1]:02d}" for d in dates])
    v = np.asarray(vals, float)
    groups = [v[(wk == w).values] for w in wk.unique()]
    rng = np.random.default_rng(seed)
    means = np.empty(draws)
    for i in range(draws):
        pick = rng.integers(0, len(groups), size=len(groups))
        a = np.concatenate([groups[j] for j in pick])
        means[i] = a.mean()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))
