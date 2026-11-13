"""Crowding-reversal study core (see PRE_REG.md). Pure numpy/pandas; no network."""
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from MyTradingSys.backtest import fees  # noqa: E402

H4 = 4 * 3600 * 1000
DAY = 24 * 3600 * 1000
ROUND_TRIP_FEE = fees.BINANCE_TAKER * 2
WIN_FUND = 90 * 3          # 8h prints in 90 days
WIN_ROW = 90 * 6           # 4h rows in 90 days
Q = 0.05
SPLITS = {"DEV": ("2020-01-01", "2024-07-01"), "VALIDATION": ("2024-07-01", "2025-07-01"),
          "RECENT": ("2025-07-01", "2100-01-01")}


def ms(d):
    return int(pd.Timestamp(d, tz="UTC").timestamp() * 1000)


def trailing_flag(x, win, q=Q):
    """+1 if x[k] >= trailing (1-q) quantile of the previous `win` values, -1 if <= q quantile, else 0.
    NaN while history is short. The window excludes x[k] itself (shift 1)."""
    s = pd.Series(np.asarray(x, float))
    hi = s.shift(1).rolling(win, min_periods=win).quantile(1 - q)
    lo = s.shift(1).rolling(win, min_periods=win).quantile(q)
    f = np.where(s >= hi, 1.0, np.where(s <= lo, -1.0, 0.0))
    f[hi.isna().values | lo.isna().values] = np.nan
    return f


def oi_surge_flag(oi, lag=18, win=WIN_ROW, k=2.0):
    """1 where the 3-day (lag rows) OI change exceeds k x trailing sd of 3-day changes (window excludes current)."""
    o = pd.Series(np.asarray(oi, float))
    chg = o / o.shift(lag) - 1
    sd = chg.shift(1).rolling(win, min_periods=win).std()
    f = np.where(chg > k * sd, 1.0, 0.0)
    f[sd.isna().values | chg.isna().values] = np.nan
    return f


def daily_atr_frac(t, h, l, c):
    """Per 4h bar i: ATR14 (SMA of daily TR) over days fully completed by the close of bar i, divided by c[i]."""
    df = pd.DataFrame({"t": t, "h": h, "l": l, "c": c})
    df["d"] = df.t // DAY
    g = df.groupby("d").agg(h=("h", "max"), l=("l", "min"), c=("c", "last"))
    pc = g.c.shift(1)
    tr = np.maximum(g.h - g.l, np.maximum((g.h - pc).abs(), (g.l - pc).abs()))
    atr = tr.rolling(14, min_periods=14).mean()
    hour = (t % DAY) // H4
    done_day = np.where(hour == 5, t // DAY, t // DAY - 1)
    return atr.reindex(done_day).values / c


def build_coin(d):
    """d: raw dict kline/funding/oi/ratio. Returns aligned per-4h-bar arrays (decision at the close of bar i)."""
    k = d["kline"]
    if len(k) < 500 or not d["funding"] or not d["ratio"] or not d["oi"]:
        return None
    t = np.array([int(r[0]) for r in k], dtype=np.int64)
    o, h, l, c = (np.array([float(r[j]) for r in k]) for j in (1, 2, 3, 4))
    keep = np.concatenate([[True], np.diff(t) > 0])
    t, o, h, l, c = t[keep], o[keep], h[keep], l[keep], c[keep]
    n = len(t)
    T = t + H4
    f = sorted((int(r["fundingRateTimestamp"]), float(r["fundingRate"])) for r in d["funding"])
    fts = np.array([x[0] for x in f], dtype=np.int64)
    fr = np.array([x[1] for x in f])
    fflag = trailing_flag(fr, WIN_FUND)
    idx = np.searchsorted(fts, T, side="right") - 1
    ci = np.clip(idx, 0, None)
    fund_flag = np.where(idx >= 0, fflag[ci], np.nan)
    fund_rate = np.where(idx >= 0, fr[ci], np.nan)
    fund_cum = np.concatenate([[0.0], np.cumsum(fr)])

    def rows(key, val_key):
        r = sorted((int(x["timestamp"]), float(x[val_key])) for x in d[key])
        return np.array([x[0] for x in r], dtype=np.int64), np.array([x[1] for x in r])

    rts, rv = rows("ratio", "buyRatio")
    ots, ov = rows("oi", "openInterest")
    rflag = trailing_flag(rv, WIN_ROW)
    oflag = oi_surge_flag(ov)

    def align(ts, arr):
        # the row stamped t[i] (period start) is complete at t[i]+4h = decision time of bar i
        j = np.clip(np.searchsorted(ts, t, side="left"), 0, len(ts) - 1)
        ok = ts[j] == t
        return np.where(ok, arr[j], np.nan)

    ret3 = np.full(n, np.nan)
    ret3[18:] = c[18:] / c[:-18] - 1
    contiguous = np.full(n, False)
    contiguous[18:] = (t[18:] - t[:-18]) == 18 * H4
    ret3[~contiguous] = np.nan
    X = daily_atr_frac(t, h, l, c) * math.sqrt(3)
    return dict(t=t, o=o, c=c, fts=fts, fund_cum=fund_cum, fund_flag=fund_flag, fund_rate=fund_rate,
                ratio_flag=align(rts, rflag), oi_flag=align(ots, oflag), ret3=ret3, X=X)


def signal_side(cd, sig):
    """Side per bar (+1 long, -1 short, 0 none) for signal a, b, c or d (see PRE_REG)."""
    ff, X, r3 = cd["fund_flag"], cd["X"], cd["ret3"]
    if sig == "a":
        s = np.where(ff == 1, -1.0, np.where(ff == -1, 1.0, 0.0))
    elif sig == "b":
        rf = cd["ratio_flag"]
        s = np.where(rf == 1, -1.0, np.where(rf == -1, 1.0, 0.0))
    elif sig == "c":
        s = np.where((ff == 1) & (r3 > X), -1.0, np.where((ff == -1) & (r3 < -X), 1.0, 0.0))
    elif sig == "d":
        fr = cd["fund_rate"]
        ok = (cd["oi_flag"] == 1) & (np.abs(r3) < 0.5 * X)
        s = np.where(ok & (fr > 0), -1.0, np.where(ok & (fr < 0), 1.0, 0.0))
    else:
        raise ValueError(sig)
    return s


def fwd_trade_arrays(cd, hold_days):
    """Per entry bar e (entry at open of e): gross long return, funding paid by a long, valid mask."""
    t, o = cd["t"], cd["o"]
    n = len(t)
    step = hold_days * 6
    gross = np.full(n, np.nan)
    fund = np.full(n, np.nan)
    valid = np.zeros(n, bool)
    e = np.arange(0, max(n - step, 0))
    x = e + step
    ok = (t[x] - t[e]) == hold_days * DAY
    e, x = e[ok], x[ok]
    gross[e] = o[x] / o[e] - 1
    j1 = np.searchsorted(cd["fts"], t[e], side="right")   # prints at or before entry are excluded
    j2 = np.searchsorted(cd["fts"], t[x], side="right")   # prints up to and including exit are paid
    fund[e] = cd["fund_cum"][j2] - cd["fund_cum"][j1]
    valid[e] = True
    return gross, fund, valid


def net(side, gross, fund):
    return side * (gross - fund) - ROUND_TRIP_FEE


def select_trades(cd, sig, tf, hold_days):
    """Signal at the close of bar i, entry at open of bar i+1, one position per coin."""
    s = signal_side(cd, sig)
    gross, fund, valid = fwd_trade_arrays(cd, hold_days)
    t = cd["t"]
    step = hold_days * 6
    ents, sides = [], []
    busy_until = -1
    for i in np.nonzero(s != 0)[0]:
        e = i + 1
        if e >= len(t) or not valid[e]:
            continue
        if tf == "1d" and (t[i] % DAY) // H4 != 5:
            continue
        if e <= busy_until:
            continue
        ents.append(e)
        sides.append(s[i])
        busy_until = e + step - 1
    return np.array(ents, int), np.array(sides), gross, fund, valid


def cluster_boot(vals, weeks, B=4000, seed=1):
    """Weekly-cluster bootstrap of the mean: (mean, lo95, hi95, one-sided p of mean <= 0)."""
    vals = np.asarray(vals, float)
    if len(vals) == 0:
        return (float("nan"),) * 4
    uw, inv = np.unique(weeks, return_inverse=True)
    S = np.bincount(inv, weights=vals)
    N = np.bincount(inv).astype(float)
    rng = np.random.default_rng(seed)
    draw = rng.integers(0, len(uw), size=(B, len(uw)))
    m = S[draw].sum(1) / N[draw].sum(1)
    return (float(vals.mean()), float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975)),
            float((np.sum(m <= 0) + 1) / (B + 1)))


def placebo_sums(cd, ents, sides, gross, fund, valid, tf, R=200, seed=2):
    """Same coin, random entry bar in the same calendar month, same side/TF/hold.
    Returns (R array of summed placebo net returns, number of trades matched) or None."""
    t = cd["t"]
    mon = pd.to_datetime(t, unit="ms", utc=True).strftime("%Y%m").astype(int).values
    elig = valid.copy()
    if tf == "1d":
        elig &= ((t % DAY) // H4 == 0)
    pos = np.nonzero(elig)[0]
    pm = mon[pos]
    start = np.searchsorted(pm, mon[ents], side="left")
    ln = np.searchsorted(pm, mon[ents], side="right") - start
    ok = ln > 0
    if not ok.any():
        return None
    sides, start, ln = sides[ok], start[ok], ln[ok]
    u = np.random.default_rng(seed).random((R, len(sides)))
    pick = pos[start + (u * ln).astype(int)]
    return net(sides[None, :], gross[pick], fund[pick]).sum(1), int(ok.sum())
