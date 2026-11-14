"""Descriptive study: BTC bear-phase episodes and where buyers stepped in. No trading rule.
All thresholds are OURS unless noted; see RESULT.md."""
import math
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_CSV = os.path.join(HERE, "..", "btc_cycles_2026-11", "btc_daily.csv")

# Cycle dates: SOURCED from research/mts_bible/BIBLE.md section 1 (2011 pair read from the held csv, OURS).
HALVINGS = ["2012-11-28", "2016-07-09", "2020-05-11", "2024-04-20"]
PEAKS = ["2011-06-08", "2013-12-05", "2017-12-17", "2021-11-10", "2025-10-06"]
BOTTOMS = ["2011-11-18", "2015-01-15", "2018-12-15", "2022-11-21", "2026-07-01"]  # last provisional (Bible s.1)


# ---------------------------------------------------------------- data
def load_daily(data_dir=None):
    """Daily OHLCV, UTC date index. Before 2017-08-17: blockchain.info index from the repo csv (open = prior
    close, no volume); after: Binance SPOT."""
    data_dir = data_dir or os.path.join(HERE, "data")
    old = pd.read_csv(REPO_CSV, parse_dates=["date"]).set_index("date")
    old = old[old["source"] == "blockchain.info"][["high", "low", "close"]]
    old["open"] = old["close"].shift(1).fillna(old["close"])
    old["volume"] = np.nan
    b = pd.read_csv(os.path.join(data_dir, "binance_spot_1d.csv"))
    b["date"] = pd.to_datetime(b["ts_ms"], unit="ms").dt.normalize()
    b = b.set_index("date")[["open", "high", "low", "close", "volume"]]
    old = old[old.index < b.index[0]]
    d = pd.concat([old[["open", "high", "low", "close", "volume"]], b])
    return d[d.index >= "2011-01-01"]


def to_weekly(d):
    """Monday-start UTC weeks; 'complete' is False for a week with fewer than 7 daily bars."""
    start = d.index.to_series().dt.to_period("W-SUN").dt.start_time
    g = d.groupby(start.values)
    w = pd.DataFrame({"open": g["open"].first(), "high": g["high"].max(), "low": g["low"].min(),
                      "close": g["close"].last(), "volume": g["volume"].sum(), "ndays": g["close"].count()})
    w["complete"] = w["ndays"] == 7
    return w


# ---------------------------------------------------------------- episodes
def red_flags(w):
    return (w["close"] < w["open"]).to_numpy()


def find_streaks(red, min_len=5):
    """Maximal runs of True with length >= min_len -> list of (first_idx, last_idx)."""
    out, i, n = [], 0, len(red)
    while i < n:
        if red[i]:
            j = i
            while j + 1 < n and red[j + 1]:
                j += 1
            if j - i + 1 >= min_len:
                out.append((i, j))
            i = j + 1
        else:
            i += 1
    return out


def fall_triggers(close, lookback=8, thr=0.18):
    """Week indices whose close is >= thr below the highest weekly close of the prior `lookback` weeks."""
    out = []
    for t in range(lookback, len(close)):
        if close[t] <= (1 - thr) * np.max(close[t - lookback:t]):
            out.append(t)
    return out


def fractal_lows(low, k=2):
    """Indices i with low[i] strictly below the k bars before and after (5-bar fractal); confirmed at i+k."""
    return [i for i in range(k, len(low) - k)
            if all(low[i] < low[i - j] and low[i] < low[i + j] for j in range(1, k + 1))]


def sma(series, n):
    return series.rolling(n, min_periods=n).mean()


def cycle_phase(date):
    date = pd.Timestamp(date)
    ev = [(pd.Timestamp(x), "post-bottom base") for x in BOTTOMS] + \
         [(pd.Timestamp(x), "post-halving bull") for x in HALVINGS] + \
         [(pd.Timestamp(x), "post-peak bear") for x in PEAKS]
    ev = sorted(e for e in ev if e[0] <= date)
    if not ev:
        return "pre-cycle", None, None
    hv = [pd.Timestamp(x) for x in HALVINGS if pd.Timestamp(x) <= date]
    pk = [pd.Timestamp(x) for x in PEAKS if pd.Timestamp(x) <= date]
    return ev[-1][1], (date - hv[-1]).days if hv else None, (date - pk[-1]).days if pk else None


def _real_bounce(d, wc, c, x, bounce_split):
    """True if, between cluster c's start and the next event x, price rallied >= bounce_split from the running
    low (a recovery, so x is a new episode, not a continuation)."""
    seg = d.loc[wc.index[c["s"]] - pd.Timedelta(weeks=1): wc.index[x["s"]]]
    if seg.empty:
        return False
    i = int(np.argmin(seg["low"].to_numpy()))
    return float(seg["high"].iloc[i:].max() / seg["low"].iloc[i] - 1) >= bounce_split


def build_episodes(d, w, min_streak=5, fall_thr=0.18, lookback=8, merge_gap=8, bounce_split=0.40):
    """Clusters of (a) >=min_streak red-week runs and (b) >=fall_thr falls, merged when within merge_gap weeks.
    Only completed weeks are used. The low is the lowest daily low in the cluster, extended while a lower low
    prints within 28 days of the current one."""
    wc = w[w["complete"]]
    red = red_flags(wc)
    close = wc["close"].to_numpy()
    ev = []
    for s, e in find_streaks(red, min_streak):
        ev.append({"kind": "streak", "s": s, "e": e, "trig": s + min_streak - 1, "len": e - s + 1})
    for t in fall_triggers(close, lookback, fall_thr):
        ev.append({"kind": "fall", "s": t, "e": t, "trig": t, "len": 0})
    ev.sort(key=lambda x: (x["s"], x["e"]))
    clusters = []
    for x in ev:
        if clusters and x["s"] <= clusters[-1]["e"] + merge_gap and not _real_bounce(d, wc, clusters[-1], x, bounce_split):
            c = clusters[-1]
            c["e"] = max(c["e"], x["e"])
            c["kinds"].add(x["kind"])
            c["trig"] = min(c["trig"], x["trig"])
            c["streak_len"] = max(c["streak_len"], x["len"])
        else:
            clusters.append({"s": x["s"], "e": x["e"], "trig": x["trig"], "kinds": {x["kind"]},
                             "streak_len": x["len"]})
    out, i = [], 0
    while i < len(clusters):
        c = clusters[i]
        i += 1
        while True:
            ws, we = wc.index[c["s"]] - pd.Timedelta(weeks=1), wc.index[c["e"]] + pd.Timedelta(days=6)
            low_date = d.loc[ws:we, "low"].idxmin()
            while True:
                nxt = d.loc[low_date + pd.Timedelta(days=1): low_date + pd.Timedelta(days=28), "low"]
                if len(nxt) and nxt.min() < d.at[low_date, "low"]:
                    low_date = nxt.idxmin()
                else:
                    break
            if i < len(clusters) and wc.index[clusters[i]["s"]] <= low_date:
                n = clusters[i]
                c["e"] = max(c["e"], n["e"])
                c["kinds"] |= n["kinds"]
                c["streak_len"] = max(c["streak_len"], n["streak_len"])
                i += 1
                continue
            break
        c["low_date"], c["low"] = low_date, float(d.at[low_date, "low"])
        c["trig_week"] = wc.index[c["trig"]]
        c["start_week"] = wc.index[c["s"]]
        c["detect_date"] = c["trig_week"] + pd.Timedelta(days=6)
        if out and out[-1]["low_date"] == c["low_date"]:  # same low reached from two clusters: one episode
            o = out[-1]
            o["kinds"] |= c["kinds"]
            o["streak_len"] = max(o["streak_len"], c["streak_len"])
            if c["trig_week"] < o["trig_week"]:
                o["trig_week"], o["detect_date"], o["start_week"] = c["trig_week"], c["detect_date"], c["start_week"]
            continue
        out.append(c)
    return out


# ---------------------------------------------------------------- per-episode features
def week_of(date):
    return pd.Timestamp(date).to_period("W-SUN").start_time


def bounce(d, low_date, low, weeks):
    win = d.loc[low_date + pd.Timedelta(days=1): low_date + pd.Timedelta(weeks=weeks)]
    return float(win["high"].max() / low - 1) if len(win) else float("nan")


def ma_state(w, week_ts, n):
    """(close above n-week SMA?, pct vs SMA) at that week, or (None, None) if there is not enough history."""
    v = sma(w["close"], n).get(week_ts)
    if v is None or pd.isna(v):
        return None, None
    c = float(w.at[week_ts, "close"])
    return bool(c > v), c / v - 1


def swing_low_info(w, ref_idx, lookback=26):
    """Lowest 5-bar weekly fractal low confirmed before week index ref_idx, within lookback (else 52) weeks."""
    low = w["low"].to_numpy()
    fr = [i for i in fractal_lows(low) if i + 2 < ref_idx]
    for lb in (lookback, 52):
        cand = [i for i in fr if i >= ref_idx - lb]
        if cand:
            i = min(cand, key=lambda j: low[j])
            return i, float(low[i])
    return None, None


def episode_features(d, w, ep):
    wi = {t: k for k, t in enumerate(w.index)}
    low, ld = ep["low"], ep["low_date"]
    lw = week_of(ld)
    trig_i = wi[ep["trig_week"]]
    ref = float(w["close"].iloc[max(0, trig_i - 8):trig_i].max()) if trig_i > 0 else float(w["close"].iloc[0])
    ep["ref"] = ref
    ep["depth"] = low / ref - 1
    ep["depth_detect"] = float(w.at[ep["trig_week"], "close"]) / ref - 1  # state when the trigger fired
    ep["low_vs_detect"] = low / float(w.at[ep["trig_week"], "close"]) - 1
    ep["bounce"] = {k: bounce(d, ld, low, k) for k in (1, 2, 4, 8)}
    ep["days_trig_to_low"] = (ld - ep["detect_date"]).days
    ep["ma50_t"], ep["ma50_t_pct"] = ma_state(w, ep["trig_week"], 50)
    ep["ma200_t"], ep["ma200_t_pct"] = ma_state(w, ep["trig_week"], 200)
    ep["cycle"], ep["days_halving"], ep["days_peak"] = cycle_phase(ld)
    si, S = swing_low_info(w, wi[ep["start_week"]])
    ep["swing_low"], ep["trap"], ep["swept"] = S, None, None
    if S is not None:
        ep["swept"] = low < S
        cl = w["close"].iloc[wi[lw]: wi[lw] + 3]
        ep["trap"] = bool(ep["swept"] and len(cl) and cl.max() >= S)
    ep["retest"] = "n/a (swing low not undercut)"
    if S is not None and low < S:
        after = w.loc[lw + pd.Timedelta(weeks=1): lw + pd.Timedelta(weeks=8)]
        rec = after[after["close"] > S]
        if rec.empty:
            ep["retest"] = "no reclaim in 8w"
        else:
            t0 = rec.index[0]
            later = d.loc[t0 + pd.Timedelta(days=7): t0 + pd.Timedelta(weeks=8)]
            touch = later[later["low"] <= S * 1.02]
            if touch.empty:
                ep["retest"] = "reclaimed, no retest"
            else:
                wk = w.loc[week_of(touch.index[0]): week_of(touch.index[0]) + pd.Timedelta(weeks=1)]
                ep["retest"] = "held" if (wk["close"] >= S * 0.98).all() else "failed"
    post = w.loc[lw + pd.Timedelta(weeks=1): lw + pd.Timedelta(weeks=26)]
    post = post[post["complete"]]
    reclaimed = bool((post["close"] > ref).any())
    newlow = bool(d.loc[ld + pd.Timedelta(days=1): ld + pd.Timedelta(weeks=26), "low"].min() < low)
    ep["outcome_short"] = "UP" if reclaimed else ("LH+newlow" if newlow else "LH")
    ep["new_low_26w"] = newlow
    ep["post_weeks"] = len(post)
    return ep


# ---------------------------------------------------------------- levels
def round_steps(price):
    e = math.floor(math.log10(price))
    return 5 * 10 ** (e - 1), 10 ** e


def nearest_mult(price, step):
    return round(price / step) * step


def hvn_levels(d, end_date, days=182, bin_pct=0.01):
    """High-volume nodes of the `days` daily bars ending the day before end_date: volume spread uniformly over
    each bar's [low, high] in 1% log bins, [1,2,1] smoothed; node = local max (+-2 bins) and >= 1.3x the mean of
    non-empty bins. Returns [] if volume is missing (pre-2017-08 index data)."""
    win = d.loc[end_date - pd.Timedelta(days=days): end_date - pd.Timedelta(days=1)]
    if len(win) < days // 2 or win["volume"].isna().any():
        return []
    lo, hi = np.log(win["low"].min()), np.log(win["high"].max())
    nb = max(5, int(math.ceil((hi - lo) / bin_pct)) + 1)
    prof = np.zeros(nb)
    for lw_, hw_, v in zip(win["low"], win["high"], win["volume"]):
        a, b = int((np.log(lw_) - lo) / bin_pct), int((np.log(hw_) - lo) / bin_pct)
        prof[a:b + 1] += v / (b - a + 1)
    sm = np.convolve(prof, [1, 2, 1], mode="same") / 4
    thr = 1.3 * sm[sm > 0].mean()
    return [float(np.exp(lo + (i + 0.5) * bin_pct)) for i in range(nb)
            if sm[i] > 0 and sm[i] >= thr and sm[i] == sm[max(0, i - 2): i + 3].max()]


def level_set(d, w, price, date):
    """Level prices of each type as known at `date`. Returns dict type -> list of prices."""
    date = pd.Timestamp(date)
    ww = w.loc[:week_of(date)]
    L = {}
    p52 = d.loc[date - pd.Timedelta(days=365): date - pd.Timedelta(days=28), "low"]
    p26 = d.loc[date - pd.Timedelta(days=182): date - pd.Timedelta(days=28), "low"]
    L["range low 26w"] = [float(p26.min())] if len(p26) else []
    L["range low 52w"] = [float(p52.min())] if len(p52) else []
    s5, s10 = round_steps(price)
    L["round, 5k-style step"] = [nearest_mult(price, s5)]
    L["round, 10k-style step"] = [nearest_mult(price, s10)]
    for n in (50, 100, 200):
        v = sma(ww["close"], n).iloc[-1] if len(ww) >= n else np.nan
        L[f"{n}w SMA"] = [] if pd.isna(v) else [float(v)]
    low = ww["low"].to_numpy()
    L["weekly fractal low, 104w"] = [float(low[i]) for i in fractal_lows(low)
                                     if i + 2 < len(ww) - 1 and i >= len(ww) - 105]
    L["volume node, 6m daily"] = hvn_levels(d, date)
    return L


def within(price, levels, tol=0.02):
    """(smallest |level/price-1|, within tol?) or (None, None) when there are no levels."""
    if not levels:
        return None, None
    dist = min(abs(l / price - 1) for l in levels)
    return dist, dist <= tol


def hit_table(d, w, episodes, tol=0.02, base_from="2014-06-01"):
    """Per level type: hits at episode lows vs the base rate over every complete week's low (same rule)."""
    rows = {}
    for ep in episodes:
        for t, lv in level_set(d, w, ep["low"], ep["low_date"]).items():
            dist, hit = within(ep["low"], lv, tol)
            r = rows.setdefault(t, {"n": 0, "hit": 0, "dists": [], "bn": 0, "bhit": 0})
            if hit is not None:
                r["n"] += 1
                r["hit"] += int(hit)
                r["dists"].append(dist)
    wc = w[w["complete"] & (w.index >= pd.Timestamp(base_from))]
    for ts, r_ in wc.iterrows():
        ld = d.loc[ts: ts + pd.Timedelta(days=6), "low"].idxmin()
        px = float(r_["low"])
        for t, lv in level_set(d, w, px, ld).items():
            dist, hit = within(px, lv, tol)
            if hit is not None and t in rows:
                rows[t]["bn"] += 1
                rows[t]["bhit"] += int(hit)
    return rows
