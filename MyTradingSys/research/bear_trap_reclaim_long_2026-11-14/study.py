"""Bear-trap reclaim LONG, 1h Bybit linear, 20 coins. Rules frozen in PRE_REG.md.
python study.py  (writes results.json, results_table.csv, prints table)."""
import json
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from backtest.fees import DERIBIT_TAKER, SLIPPAGE_RT_S13  # noqa: E402  (5 bp per side taker, 2 bp round-trip slippage)

DATA = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge9-bear-trap-1114"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX",
         "DOT", "ATOM", "TRX", "BCH", "ETC", "UNI", "NEAR", "FIL", "XLM", "AAVE"]
H = 3600000
DAY = 24 * H
SWEEP = 0.001
STOP_PAD = 0.001
RECLAIM_BARS = 6
HOLD_MAX = 24
MIN_RISK, MAX_RISK = 0.002, 0.10
COST = 2 * DERIBIT_TAKER + SLIPPAGE_RT_S13  # 0.0012 of entry price
FLUSH = -0.01
VAL_START_MS = 1704067200000  # 2024-01-01
ENTRY_OFFSET = 1  # entry = open of bar r+1 (0 would be one-bar look-ahead; the test must fail then)
NBOOT, NPLAC, SEED = 2000, 2000, 9114


def day_tables(t, o, h, l, c):
    """Per complete UTC day (24 bars): open, high, low, close, indexed by day number (ms // DAY)."""
    df = pd.DataFrame({"d": t // DAY, "o": o, "h": h, "l": l, "c": c})
    g = df.groupby("d")
    out = pd.DataFrame({"o": g["o"].first(), "h": g["h"].max(), "l": g["l"].min(), "c": g["c"].last(), "n": g["o"].size()})
    out = out[out["n"] == 24].drop(columns="n")
    full = pd.RangeIndex(int(out.index.min()), int(out.index.max()) + 1)
    return out.reindex(full)


def week_tables(dt):
    """Complete Mon-start weeks from a day table: week number = (day+3)//7."""
    df = dt.copy()
    df["w"] = (dt.index.values + 3) // 7
    g = df.groupby("w")
    out = pd.DataFrame({"o": g["o"].first(), "h": g["h"].max(), "l": g["l"].min(), "c": g["c"].last(), "n": g["o"].count()})
    out = out[out["n"] == 7].drop(columns="n")
    full = pd.RangeIndex(int(out.index.min()), int(out.index.max()) + 1)
    return out.reindex(full)


def coin_trend_by_day(dt):
    """flag[D] (known at start of day D, uses days <= D-1 only): close[D-1] < SMA20 and SMA20 < SMA20 one day earlier."""
    c = dt["c"]
    sma = c.rolling(20, min_periods=20).mean()  # SMA ending at day d (inclusive)
    ok = (c < sma) & (sma < sma.shift(1))
    return ok.shift(1, fill_value=False).astype(bool)  # value for day D = state at the end of D-1


def btc_red3_by_week(wt):
    """flag[W] (week W): the weeks W-1, W-2, W-3 are all complete and red."""
    red = (wt["c"] < wt["o"]) & wt["c"].notna()
    r3 = red & red.shift(1, fill_value=False) & red.shift(2, fill_value=False)
    return r3.shift(1, fill_value=False).astype(bool)


def trend_flag_array(t, coin_dt, btc_wt):
    """Per-bar downtrend flag for a coin's bars: coin trend of its day OR BTC red streak of its week."""
    d = t // DAY
    cf = coin_trend_by_day(coin_dt).reindex(d).fillna(False).values.astype(bool)
    bf = btc_red3_by_week(btc_wt).reindex((d + 3) // 7).fillna(False).values.astype(bool)
    return cf | bf


def find_events(t, o, h, l, c, dt, wt):
    """List of dict(lt, s, r, e, level, slow) per level period. Arrays are one coin's 1h bars."""
    n = len(t)
    day = t // DAY
    wk = (day + 3) // 7
    events = []
    for ltype, per, tab in (("PDL", day, dt), ("PWL", wk, wt)):
        lows = tab["l"]
        starts = np.flatnonzero(np.r_[True, per[1:] != per[:-1]])
        ends = np.r_[starts[1:], n]
        for a, b in zip(starts, ends):
            P = int(per[a])
            L = lows.get(P - 1, np.nan)
            if not np.isfinite(L):
                continue
            seg = np.flatnonzero(l[a:b] <= L * (1 - SWEEP))
            if len(seg) == 0:
                continue
            s = a + int(seg[0])
            hi = min(s + RECLAIM_BARS, b - 1)
            rr = np.flatnonzero(c[s + 1:hi + 1] > L)
            if len(rr) == 0:
                continue
            r = s + 1 + int(rr[0])
            e = r + ENTRY_OFFSET
            if e + HOLD_MAX >= n or t[e + HOLD_MAX] - t[s] != (e + HOLD_MAX - s) * H:
                continue
            events.append(dict(lt=ltype, s=s, r=r, e=e, level=float(L), slow=float(l[s:r + 1].min())))
    return events


def simulate(o, h, l, c, e, stop, target):
    """(exit_price, hold_bars). Scan bars e..e+23; stop first on a tie; gaps fill at open; time exit at open of e+24."""
    for k in range(e, e + HOLD_MAX):
        if o[k] <= stop:
            return o[k], k - e + 1
        if l[k] <= stop:
            return stop, k - e + 1
        if o[k] >= target:
            return o[k], k - e + 1
        if h[k] >= target:
            return target, k - e + 1
    return o[e + HOLD_MAX], HOLD_MAX


def trade_r(entry, stop, exit_px):
    R = entry - stop
    return ((exit_px - entry) / R) - COST * entry / R


def build_trades(coin, t, o, h, l, c, events, flag, pdh_by_day, oi):
    """One record per event x target."""
    rows = []
    for ev in events:
        e = ev["e"]
        entry = o[e]
        stop = ev["slow"] * (1 - STOP_PAD)
        R = entry - stop
        if R <= 0 or R / entry < MIN_RISK or R / entry > MAX_RISK:
            continue
        d = int(t[e] // DAY)
        pdh = pdh_by_day.get(d - 1, np.nan)
        flush = None
        if oi is not None:
            a, b = oi.get(int(t[ev["s"]])), oi.get(int(t[ev["r"]]))
            if a and b:
                flush = bool((b / a - 1) <= FLUSH)
        for tg in ("1R", "2R", "PDH"):
            if tg == "1R":
                target = entry + R
            elif tg == "2R":
                target = entry + 2 * R
            else:
                if not np.isfinite(pdh) or pdh <= entry * 1.001:
                    continue
                target = pdh
            px, hold = simulate(o, h, l, c, e, stop, target)
            rows.append(dict(coin=coin, lt=ev["lt"], tg=tg, e=e, t=int(t[e]), date=d, r=trade_r(entry, stop, px),
                             hold=hold, rfrac=R / entry, trend=bool(flag[ev["r"]]), flush=flush, val=bool(t[e] >= VAL_START_MS)))
    return rows


def boot_ci(x, rng):
    n = len(x)
    if n < 2:
        return (np.nan, np.nan)
    idx = rng.integers(0, n, size=(NBOOT, n))
    return tuple(np.percentile(x[idx].mean(axis=1), [2.5, 97.5]))


def cluster_ci(x, days, rng):
    u, inv = np.unique(days, return_inverse=True)
    if len(u) < 2:
        return (np.nan, np.nan)
    sums = np.bincount(inv, weights=x)
    cnt = np.bincount(inv).astype(float)
    idx = rng.integers(0, len(u), size=(NBOOT, len(u)))
    return tuple(np.percentile(sums[idx].sum(axis=1) / cnt[idx].sum(axis=1), [2.5, 97.5]))


def drop_best5(x, days):
    u, inv = np.unique(days, return_inverse=True)
    sums = np.bincount(inv, weights=x)
    cnt = np.bincount(inv)
    keep = np.ones(len(u), bool)
    keep[np.argsort(sums)[-5:]] = False
    return float(sums[keep].sum() / cnt[keep].sum()) if cnt[keep].sum() else np.nan


def placebo_p(trs, coin_data, rng):
    """Random entries matched on coin, UTC hour, hold, R width and cost; downtrend rows draw only from flagged bars."""
    tot = np.zeros(NPLAC)
    for tr in trs:
        cd = coin_data[tr["coin"]]
        hour = (tr["t"] // H) % 24
        cands = cd["cand_flag"][hour] if tr["need_flag"] else cd["cand_all"][hour]
        cands = cands[cands + tr["hold"] - 1 < cd["n"]]
        if len(cands) == 0:
            cands = cd["cand_all"][hour]
        ep = cands[rng.integers(0, len(cands), size=NPLAC)]
        ent = cd["o"][ep]
        ex = cd["c"][np.minimum(ep + tr["hold"] - 1, cd["n"] - 1)]
        tot += ((ex / ent - 1) - COST) / tr["rfrac"]
    pm = tot / len(trs)
    actual = np.mean([x["r"] for x in trs])
    return float((pm >= actual).mean()), float(pm.mean())


def bh(pvals, q=0.10):
    p = np.array([1.0 if not np.isfinite(x) else x for x in pvals])
    m = len(p)
    order = np.argsort(p)
    kmax = -1
    for i, j in enumerate(order):
        if p[j] <= (i + 1) / m * q:
            kmax = i
    ok = np.zeros(m, bool)
    for i, j in enumerate(order):
        ok[j] = i <= kmax
    return ok


def load_all():
    out = {}
    for c in COINS:
        p = os.path.join(DATA, c + "_1h.json")
        if not os.path.exists(p):
            continue
        a = np.array(json.load(open(p)), dtype=float)
        oi = None
        po = os.path.join(DATA, c + "_oi.json")
        if os.path.exists(po):
            oi = {int(k): float(v) for k, v in json.load(open(po))}
        out[c] = dict(t=a[:, 0].astype(np.int64), o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4], oi=oi)
    return out


def main(coins=None):
    raw = load_all()
    if coins:
        raw = {k: v for k, v in raw.items() if k in coins}
    btc = raw["BTC"]
    btc_wt = week_tables(day_tables(btc["t"], btc["o"], btc["h"], btc["l"], btc["c"]))
    trades, cdata, flagmix = [], {}, {}
    for c, d in raw.items():
        t, o, h, l, cl = d["t"], d["o"], d["h"], d["l"], d["c"]
        dt = day_tables(t, o, h, l, cl)
        wt = week_tables(dt)
        flag = trend_flag_array(t, dt, btc_wt)
        evs = find_events(t, o, h, l, cl, dt, wt)
        trades += build_trades(c, t, o, h, l, cl, evs, flag, dt["h"].to_dict(), d["oi"])
        hours = (t // H) % 24
        valm = t >= VAL_START_MS
        prev_flag = np.r_[False, flag[:-1]]  # flag at the signal bar (bar before the entry bar)
        cdata[c] = dict(o=o, c=cl, n=len(t),
                        cand_all={hh: np.flatnonzero((hours == hh) & valm) for hh in range(24)},
                        cand_flag={hh: np.flatnonzero((hours == hh) & valm & prev_flag) for hh in range(24)})
        flagmix[c] = dict(bars=len(t), flag=float(flag.mean()))
    df = pd.DataFrame(trades)
    df["flush"] = df["flush"].map({True: 1.0, False: 0.0})  # NaN when OI unknown
    rng = np.random.default_rng(SEED)
    rows = []
    for lt in ("PDL", "PWL"):
        for tg in ("1R", "2R", "PDH"):
            for filt in ("downtrend", "control"):
                for oiv in ("none", "flush"):
                    sub = df[(df["lt"] == lt) & (df.tg == tg)]
                    if filt == "downtrend":
                        sub = sub[sub.trend]
                    if oiv == "flush":
                        sub = sub[sub.flush == 1.0]
                    dev, val = sub[~sub.val], sub[sub.val]
                    x = val.r.values
                    row = dict(level=lt, target=tg, filter=filt, oi=oiv, n_dev=len(dev), n_val=len(val),
                               win_dev=float((dev.r > 0).mean()) if len(dev) else np.nan,
                               mean_dev=float(dev.r.mean()) if len(dev) else np.nan,
                               win_val=float((x > 0).mean()) if len(x) else np.nan,
                               mean_val=float(x.mean()) if len(x) else np.nan)
                    if len(x) >= 2:
                        row["ci_trade"] = boot_ci(x, rng)
                        row["ci_day"] = cluster_ci(x, val.date.values, rng)
                        row["no_best5"] = drop_best5(x, val.date.values)
                        trs = [dict(coin=q.coin, t=q.t, hold=q.hold, rfrac=q.rfrac, r=q.r, need_flag=(filt == "downtrend")) for q in val.itertuples()]
                        row["placebo_p"], row["placebo_mean"] = placebo_p(trs, cdata, rng)
                    else:
                        row.update(ci_trade=(np.nan, np.nan), ci_day=(np.nan, np.nan), no_best5=np.nan, placebo_p=np.nan, placebo_mean=np.nan)
                    rows.append(row)
    ok = bh([r["placebo_p"] for r in rows])
    for r, k in zip(rows, ok):
        r["bh10"] = bool(k)
        g = (r["n_val"] >= 100 and r["mean_val"] > 0 and r["ci_trade"][0] > 0 and r["ci_day"][0] > 0
             and r["placebo_p"] < 0.05 and r["bh10"] and r["no_best5"] > 0)
        r["verdict"] = "PASS" if g else ("UNDERPOWERED" if r["n_val"] < 100 else "FAIL")
    ev = df[df.tg == "1R"]
    byyear = ev.assign(y=pd.to_datetime(ev.t, unit="ms").dt.year).groupby("y").trend.mean()
    mix = dict(coins=len(raw), events_1R=int(len(ev)), share_events_downtrend=float(ev.trend.mean()),
               share_bars_downtrend=float(np.average([v["flag"] for v in flagmix.values()], weights=[v["bars"] for v in flagmix.values()])),
               by_year={int(y): round(float(v), 3) for y, v in byyear.items()},
               flush_known=int(ev.flush.notna().sum()), flush_true=int((ev.flush == 1.0).sum()))
    json.dump(dict(rows=rows, mix=mix), open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "results_table.csv"), index=False)
    return rows, mix


if __name__ == "__main__":
    rows, mix = main()
    print(json.dumps(mix))
    for r in rows:
        print("%s %s %-9s %-5s n %4d/%4d win %.3f mean %+.3f ci_t [%+.3f,%+.3f] ci_d [%+.3f,%+.3f] p %.3f nb5 %+.3f bh %s %s" % (
            r["level"], r["target"], r["filter"], r["oi"], r["n_dev"], r["n_val"], r["win_val"], r["mean_val"], r["ci_trade"][0], r["ci_trade"][1],
            r["ci_day"][0], r["ci_day"][1], r["placebo_p"], r["no_best5"], r["bh10"], r["verdict"]))
