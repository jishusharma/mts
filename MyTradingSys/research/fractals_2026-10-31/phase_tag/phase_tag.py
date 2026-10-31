"""Phase tag v1 (P0): BTC market-phase tags for daily bar t, computed only from bars closed <= t-1.

Spec: research/fractals_2026-10-31/SYNTHESIS.md s3-s4 (P0), checks in VALIDATION.md (3a, 5b).
Formulas: MyTradingSys/backtest/layers/FORMULAS.md (halving clock, Cowen band).
Single daily source: F:/MTS/data/krown_daily/BTCUSDT_1d.csv (Binance spot, 2017-08-17..2026-09-30).

Rule: the tag in row t is the feature at the CLOSE of bar t-1 (features_at_close(), then shifted one row).
Row 0 has no tag. A bar's own close is never in its own tag.

Parameters (each SOURCED = a quote or link, OURS = our judgement; never call OURS the trader's):

| Parameter | Value | Label | Source / reason |
|---|---|---|---|
| Halving instants (UTC) | 2012-11-28, 2016-07-09, 2020-05-11, 2024-04-20 00:09 (block 840,000) | SOURCED | block timestamps; 2024 value pinned in VALIDATION.md 2a; day count uses the UTC calendar date |
| Days since halving | calendar days from the halving date to the date of the last closed bar | OURS | epoch switches when the last closed bar is dated on/after the halving date |
| Cycle-year bin | 1 + floor(days/365), capped at 4 | OURS | descriptive bins only; n = 2-3 cycles, never a trigger (R2 s6) |
| Running ATH | max close from the first bar of the file | OURS | close-based; pre-2017-08 BTC highs (<= ~1,200 USD) are far below the first close (4,285) |
| Drawdown bins | >-20%: shallow; -20..-50%: mid; <=-50%: deep | OURS | three bins as in SYNTHESIS P1 text; edges not tuned |
| Cowen band | 20-week SMA and 21-week EMA of completed weekly closes | SOURCED | R2_BTC_PHASES.md s2 (Cowen band, video bWdXPK3Hlok 00:06:02, 72-76k band); sim-desk cowen_bmsb.py:35 |
| Completed week | ISO week Mon..Sun UTC, closes at the Sunday bar; a week whose Monday is not in the data is dropped | OURS | no partial weeks, no peeking at a running week |
| EMA seed | SMA of the first 21 weekly closes, then alpha = 2/22 | OURS | TradingView ta.ema convention |
| Cowen side | close of last closed bar vs max/min of (SMA20w, EMA21w): above / inside / below | OURS | three states |
| 200D, 400D SMA side | close of last closed bar vs plain SMA of the last 200 / 400 daily closes (incl. that bar) | OURS | R2 s2 lists 200D as a standard level; 400D OURS; strict > is above |
| Weekly SMA10 phase | side of close vs SMA10 of completed weekly closes, and slope (SMA10 vs one week earlier) | OURS | R2 s2 "weekly SMA10 phase (OURS)"; strict > is above / up |
"""
import datetime as dt

import numpy as np
import pandas as pd

HALVINGS_UTC = [
    dt.datetime(2012, 11, 28, 15, 24),
    dt.datetime(2016, 7, 9, 16, 46),
    dt.datetime(2020, 5, 11, 19, 23),
    dt.datetime(2024, 4, 20, 0, 9),
]
_HAL_DATES = np.array([h.date() for h in HALVINGS_UTC], dtype="datetime64[D]")

CYCLE_YEAR_DAYS = 365
DD_SHALLOW, DD_DEEP = -0.20, -0.50
SMA_FAST_D, SMA_SLOW_D = 200, 400
WEEKS_SMA_BAND, WEEKS_EMA_BAND, WEEKS_SMA_PHASE = 20, 21, 10

FEATURE_COLS = [
    "days_since_halving", "cycle_year", "dd_ath", "dd_bin",
    "sma20w", "ema21w", "cowen_side",
    "sma200", "sma200_side", "sma400", "sma400_side",
    "sma10w", "wsma10_phase",
]


def _check(df):
    if not {"date", "close"} <= set(df.columns):
        raise ValueError("need columns date, close")
    d = pd.to_datetime(df["date"]).dt.normalize()
    if len(d) > 1 and not (d.diff().dropna() == pd.Timedelta(days=1)).all():
        raise ValueError("dates must be contiguous daily bars (no gaps, no duplicates, ascending)")
    return d


def _side(close, level):
    out = np.where(np.isnan(level), None, np.where(close > level, "above", "below"))
    return pd.Series(out, dtype=object)


def features_at_close(df):
    """Feature known at the CLOSE of each bar (includes that bar). NOT safe to use as the tag of the same bar."""
    d = _check(df)
    close = df["close"].to_numpy(dtype=float)
    n = len(close)
    out = pd.DataFrame({"date": d.values})

    # halving clock: calendar date of this bar vs the latest halving date <= it
    dd64 = d.values.astype("datetime64[D]")
    idx = np.searchsorted(_HAL_DATES, dd64, side="right") - 1
    days = np.where(idx >= 0, (dd64 - _HAL_DATES[np.clip(idx, 0, None)]).astype(int), np.nan)
    out["days_since_halving"] = days
    out["cycle_year"] = np.where(np.isnan(days), np.nan, np.minimum(4, 1 + np.floor(days / CYCLE_YEAR_DAYS)))

    # drawdown from running ATH close
    dd = close / np.maximum.accumulate(close) - 1.0
    out["dd_ath"] = dd
    out["dd_bin"] = np.where(dd > DD_SHALLOW, "shallow", np.where(dd > DD_DEEP, "mid", "deep"))

    # daily SMAs
    s = pd.Series(close)
    out["sma200"] = s.rolling(SMA_FAST_D).mean().to_numpy()
    out["sma400"] = s.rolling(SMA_SLOW_D).mean().to_numpy()
    out["sma200_side"] = _side(close, out["sma200"].to_numpy())
    out["sma400_side"] = _side(close, out["sma400"].to_numpy())

    # completed weeks: Sunday bars with the Monday (6 bars earlier) present
    is_sun = (d.dt.dayofweek.to_numpy() == 6) & (np.arange(n) >= 6)
    sun_idx = np.flatnonzero(is_sun)
    wk = pd.Series(close[sun_idx])
    sma20 = wk.rolling(WEEKS_SMA_BAND).mean().to_numpy()
    sma10 = wk.rolling(WEEKS_SMA_PHASE).mean().to_numpy()
    ema21 = np.full(len(wk), np.nan)
    if len(wk) >= WEEKS_EMA_BAND:
        a = 2.0 / (WEEKS_EMA_BAND + 1)
        e = wk.iloc[:WEEKS_EMA_BAND].mean()
        ema21[WEEKS_EMA_BAND - 1] = e
        for k in range(WEEKS_EMA_BAND, len(wk)):
            e = e + a * (wk.iloc[k] - e)
            ema21[k] = e
    sma10_prev = np.concatenate([[np.nan], sma10[:-1]])

    def spread(arr):
        full = np.full(n, np.nan)
        full[sun_idx] = arr
        return pd.Series(full).ffill().to_numpy()

    f20, f21, f10, f10p = spread(sma20), spread(ema21), spread(sma10), spread(sma10_prev)
    out["sma20w"], out["ema21w"], out["sma10w"] = f20, f21, f10
    hi, lo = np.fmax(f20, f21), np.fmin(f20, f21)
    cow = np.where(close > hi, "above", np.where(close < lo, "below", "inside"))
    out["cowen_side"] = np.where(np.isnan(f20) | np.isnan(f21), None, cow)
    ph = np.where(close > f10, "above", "below") + np.char.add("_", np.where(f10 > f10p, "up", "down"))
    out["wsma10_phase"] = np.where(np.isnan(f10) | np.isnan(f10p), None, ph)
    return out[["date"] + FEATURE_COLS]


def compute_tags(df):
    """Tags for each row t from bars closed <= t-1 (features_at_close shifted one row). Row 0 is all-NaN."""
    f = features_at_close(df)
    out = f.copy()
    for c in FEATURE_COLS:
        out[c] = f[c].shift(1)
    return out


def main(src="F:/MTS/data/krown_daily/BTCUSDT_1d.csv", dst=None):
    import os
    d = pd.read_csv(src)
    df = pd.DataFrame({"date": pd.to_datetime(d["open_time_ms"], unit="ms").dt.normalize(), "close": d["close"].astype(float)})
    tags = compute_tags(df)
    dst = dst or os.path.join(os.path.dirname(os.path.abspath(__file__)), "tags.csv")
    tags["date"] = tags["date"].dt.strftime("%Y-%m-%d")
    tags.to_csv(dst, index=False, float_format="%.10g", lineterminator="\n")
    return tags


if __name__ == "__main__":
    t = main()
    print(t.iloc[[-1]].T.to_string())
