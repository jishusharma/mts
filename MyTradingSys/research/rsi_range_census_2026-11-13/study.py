"""RSI range census (descriptive). Writes results.json next to this file."""
import csv, json, sys, datetime as dt
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "MyTradingSys" / "backtest" / "layers" / "rsi"))
sys.path.insert(0, str(HERE))
from rsi_core import rsi_core  # the one Wilder RSI
from census_lib import percentiles, episode_starts, bucket_of

DATA = ROOT / "runtime_data" / "rsi_range_census_1113"
WARM = 150
MS = {"5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000, "1w": 604_800_000}
WEEK_OFF = 4 * 86_400_000  # epoch is Thursday; Monday-UTC weeks
DBK = [25, 30, 35, 40, 45, 50, 60, 70]
DNAMES = ["<25", "25-30", "30-35", "35-40", "40-45", "45-50", "50-60", "60-70", ">70"]
THR_COND = [30, 25, 20, 15, 10]
THR_EP = [30, 25, 20, 15, 10]
FWD_H = [1, 4, 12, 24, 72]


def load5(sym):
    return np.loadtxt(DATA / f"{sym}_5m.csv", delimiter=",", skiprows=1)  # t,o,h,l,c,v


def resample(a, tf, src_ms=300_000):
    """Complete groups only, UTC-aligned (weeks Monday-aligned)."""
    t = a[:, 0].astype(np.int64)
    step = MS[tf]
    off = WEEK_OFF if tf == "1w" else 0
    key = (t - off) // step
    uk, first = np.unique(key, return_index=True)
    need = step // src_ms
    cnt = np.diff(np.append(first, len(t)))
    out = []
    for k, f, c in zip(uk, first, cnt):
        if c < need:
            continue
        g = a[f:f + c]
        out.append((k * step + off, g[0, 1], g[:, 2].max(), g[:, 3].min(), g[-1, 4], g[:, 5].sum()))
    return np.array(out)


def rsi_arr(bars, warm=WARM):
    r = rsi_core(list(bars[:, 4]))
    r = np.array([np.nan if v is None else v for v in r], dtype=float)
    r[:warm] = np.nan
    return r


def date(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def per_year_eps(r, t, thr):
    yrs = {}
    for i in episode_starts(list(r), thr):
        y = dt.datetime.fromtimestamp(t[i] / 1000, dt.timezone.utc).year
        yrs[y] = yrs.get(y, 0) + 1
    return yrs


def sec1(bars, r):
    t = bars[:, 0].astype(np.int64)
    ok = np.isfinite(r)
    v = r[ok]
    tt = t[ok]
    imin, imax = int(np.argmin(v)), int(np.argmax(v))
    return {
        "n": int(ok.sum()), "first": date(tt[0]), "last": date(tt[-1]),
        "min": float(v[imin]), "min_at": date(tt[imin]), "max": float(v[imax]), "max_at": date(tt[imax]),
        "pct": {str(k): x for k, x in percentiles(v).items()},
        "eps": {str(th): per_year_eps(r, t, th) for th in THR_EP},
        "eps_total": {str(th): len(episode_starts(list(r), th)) for th in THR_EP},
        "bars_below": {str(th): int((v < th).sum()) for th in THR_EP},
    }


LOWMS = {"1h|1d": ("1h", "1d"), "4h|1d": ("4h", "1d"), "15m|1h": ("15m", "1h")}


def cond_table(low_bars, r_low, hi_bars, r_hi, key):
    """Condition = RSI of last CLOSED hi bar (j-1); outcome = lowest low-tf RSI inside hi bar j."""
    lowtf, hitf = LOWMS[key]
    step = MS[hitf]
    per = step // MS[lowtf]
    th = hi_bars[:, 0].astype(np.int64)
    tl = low_bars[:, 0].astype(np.int64)
    rows = {n: [] for n in DNAMES}
    for j in range(1, len(th)):
        c = r_hi[j - 1]
        if not np.isfinite(c) or th[j] - th[j - 1] != step:
            continue
        lo = np.searchsorted(tl, th[j], side="left")
        hi = np.searchsorted(tl, th[j] + step, side="left")
        seg = r_low[lo:hi]
        if hi - lo < per:
            continue
        seg = seg[np.isfinite(seg)]
        if len(seg) < per:
            continue
        rows[DNAMES[bucket_of(c, DBK)]].append(seg.min())
    out = {}
    for n, vals in rows.items():
        if not vals:
            out[n] = None
            continue
        a = np.array(vals)
        out[n] = {"n": len(a), "min": float(a.min()), "p1": float(np.percentile(a, 1)), "p5": float(np.percentile(a, 5)),
                  "p25": float(np.percentile(a, 25)), "med": float(np.percentile(a, 50)),
                  **{f"lt{x}": float((a < x).mean() * 100) for x in THR_COND}}
    return out


def fwd_ret(c, i, h):
    j = i + h
    return c[j] / c[i] - 1 if j < len(c) else np.nan


def fwd_low(lo, i, h):
    seg = lo[i + 1:i + 1 + h]
    return seg.min() if len(seg) == h else np.nan


def atr14(b):
    h, l, c = b[:, 2], b[:, 3], b[:, 4]
    pc = np.roll(c, 1)
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    tr[0] = h[0] - l[0]
    a = np.full(len(b), np.nan)
    a[14] = tr[1:15].mean()
    for i in range(15, len(b)):
        a[i] = (a[i - 1] * 13 + tr[i]) / 14
    return a


def sec3(h1, r1, d1, rd):
    t1 = h1[:, 0].astype(np.int64)
    close_td = d1[:, 0].astype(np.int64) + MS["1d"]
    c = h1[:, 4]
    lo = h1[:, 3]
    atr = atr14(h1)
    didx = np.searchsorted(close_td, t1 + MS["1h"], side="right") - 1
    res = {}
    for thr in THR_COND:
        starts = episode_starts(list(r1), thr, include_equal=True)
        cells = {n: [] for n in DNAMES + ["ALL"]}
        for i in starts:
            k = didx[i]
            if k < 0 or not np.isfinite(rd[k]):
                continue
            d = fwd_low(lo, i, 24)
            rec = {"ret": [fwd_ret(c, i, h) for h in FWD_H],
                   "dd": d / c[i] - 1 if np.isfinite(d) else np.nan,
                   "ddatr": (d - c[i]) / atr[i] if np.isfinite(d) and np.isfinite(atr[i]) and atr[i] > 0 else np.nan}
            cells[DNAMES[bucket_of(rd[k], DBK)]].append(rec)
            cells["ALL"].append(rec)
        out = {}
        for n, recs in cells.items():
            if not recs:
                out[n] = None
                continue
            cell = {"n": len(recs)}
            for hi_, h in enumerate(FWD_H):
                a = np.array([x["ret"][hi_] for x in recs])
                a = a[np.isfinite(a)]
                cell[str(h)] = None if len(a) == 0 else {
                    "n": len(a), "med": float(np.median(a) * 100), "mean": float(a.mean() * 100),
                    "pos": float((a > 0).mean() * 100), "worst": float(a.min() * 100)}
            dd = np.array([x["dd"] for x in recs]); dd = dd[np.isfinite(dd)]
            da = np.array([x["ddatr"] for x in recs]); da = da[np.isfinite(da)]
            cell["dd_med"] = float(np.median(dd) * 100) if len(dd) else None
            cell["dd_worst"] = float(dd.min() * 100) if len(dd) else None
            cell["ddatr_med"] = float(np.median(da)) if len(da) else None
            cell["ddatr_worst"] = float(da.min()) if len(da) else None
            out[n] = cell
        res[str(thr)] = out
    return res


def main():
    out = {}
    for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        a5 = load5(sym)
        tfs = {"5m": a5}
        for tf in ["15m", "1h", "4h", "1d"]:
            tfs[tf] = resample(a5, tf)
        tfs["1w"] = resample(tfs["1d"], "1w", MS["1d"])
        rs = {tf: rsi_arr(b, 50 if tf == '1w' else WARM) for tf, b in tfs.items()}
        o = {"sec1": {tf: sec1(tfs[tf], rs[tf]) for tf in tfs}}
        o["sec2"] = {k: cond_table(tfs[v[0]], rs[v[0]], tfs[v[1]], rs[v[1]], k) for k, v in LOWMS.items()}
        o["sec3"] = sec3(tfs["1h"], rs["1h"], tfs["1d"], rs["1d"])
        out[sym] = o
        print(sym, {tf: len(b) for tf, b in tfs.items()}, flush=True)
    rows = [r for r in csv.DictReader(open(ROOT / "MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv")) if r["date"] >= "2013-01-01"]
    ts = [int(dt.datetime.strptime(r["date"], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() * 1000) for r in rows]
    L = np.array([[t, 0, float(r["high"]), float(r["low"]), float(r["close"]), 0] for t, r in zip(ts, rows)])
    Lw = resample(L, "1w", MS["1d"])
    out["BTC_LONG"] = {"1d": sec1(L, rsi_arr(L)), "1w": sec1(Lw, rsi_arr(Lw, 50))}
    json.dump(out, open(HERE / "results.json", "w"), indent=1)
    print("done")


if __name__ == "__main__":
    main()
