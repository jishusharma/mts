"""Run the PRE_REG.md grid. python run.py  -> cells.csv + RESULT.md next to this file. Data cache: runtime_data/edge-rsi-extreme-confirm-1113/."""
import csv
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.abspath(os.path.join(ROOT, "..", "runtime_data", "edge-rsi-extreme-confirm-1113"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "backtest", "layers", "rsi"))
sys.path.insert(0, os.path.join(ROOT, "backtest"))
import engine as E  # noqa: E402
import fees  # noqa: E402
import research_kit as RK  # noqa: E402
from rsi_core import rsi_core  # noqa: E402

COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX"]
TS = {1: (10, 15, 20, 25), -1: (75, 80, 85, 90)}
SPLITS = ("DEV", "VAL", "RECENT")
DAY = 86400000
VAL0 = int(np.datetime64("2024-07-01", "ms").astype(np.int64))
REC0 = int(np.datetime64("2025-07-01", "ms").astype(np.int64))
TAKER = fees.BINANCE_TAKER
B_BOOT, B_PLAC = 2000, 1000
MIN_N = 30
rng = np.random.default_rng(20261113)


def bucket_of(side, rd):
    """Daily RSI bucket code 0..3 (-1 = no daily RSI yet). Long: <30, 30-40, 40-50, >=50. Short: >70, 60-70, 50-60, <=50."""
    out = np.full(len(rd), -1)
    ok = np.isfinite(rd)
    if side > 0:
        out[ok] = np.where(rd[ok] < 30, 0, np.where(rd[ok] < 40, 1, np.where(rd[ok] < 50, 2, 3)))
    else:
        out[ok] = np.where(rd[ok] > 70, 0, np.where(rd[ok] > 60, 1, np.where(rd[ok] > 50, 2, 3)))
    return out


def load(coin):
    k = np.array(json.load(open(os.path.join(DATA, coin + "_60.json"))), float)
    dk = np.array(json.load(open(os.path.join(DATA, coin + "_D.json"))), float)
    f = json.load(open(os.path.join(DATA, coin + "_fund.json")))
    t = k[:, 0].astype(np.int64)
    o, h, l, c = k[:, 1], k[:, 2], k[:, 3], k[:, 4]
    rsi = np.array([np.nan if v is None else v for v in rsi_core(list(c), 14)])
    atr = E.wilder_atr(h, l, c, 14)
    fts = np.array([r[0] for r in f], dtype=np.int64)
    G = E.fund_cum(t, fts, np.array([r[1] for r in f]))
    dt = dk[:, 0].astype(np.int64)
    rd = np.array([np.nan if v is None else v for v in rsi_core(list(dk[:, 4]), 14)])
    # last daily bar closed at or before bar open t: dt + DAY <= t
    di = np.searchsorted(dt + DAY, t, side="right") - 1
    rd_at = np.where(di >= 0, rd[np.maximum(di, 0)], np.nan)
    return dict(t=t, o=o, h=h, l=l, c=c, rsi=rsi, atr=atr, G=G, rd_at=rd_at, dt=dt, dc=dk[:, 4])


def split_of(te):
    return np.where(te < VAL0, 0, np.where(te < REC0, 1, 2))


def build(coin_data):
    """tables[(coin, side, stop, exit)] = dict of arrays over confirm-condition setup bars (valid trades only)."""
    tabs = {}
    for coin, D in coin_data.items():
        for side in (1, -1):
            cm = E.confirm_mask(side, D["c"], D["rsi"], D["atr"])
            s_all = np.where(cm)[0]
            for stop in E.STOPS:
                for ex in E.EXITS:
                    r = E.fwd_outcomes(side, stop, ex, s_all, D["t"], D["o"], D["h"], D["l"], D["c"], D["rsi"], D["atr"], D["G"], TAKER)
                    v = r["valid"]
                    e = r["e"][v]
                    te = D["t"][e]
                    bk = bucket_of(side, D["rd_at"][e])
                    tabs[(coin, side, stop, ex)] = dict(
                        s=s_all[v], e=e, x=r["x"][v], net_r=r["net_r"][v], net_pct=r["net_pct"][v], mae=r["mae_r"][v],
                        rsi_s=D["rsi"][s_all[v]], bucket=bk, day=te // DAY, split=split_of(te))
    return tabs


def stats(R, P, M, day, ci=True):
    n = len(R)
    if n == 0:
        return dict(n=0, mean_r=np.nan, win=np.nan, mae=np.nan, mean_pct=np.nan, p=1.0, lo=np.nan, hi=np.nan)
    mean, se = RK.cluster_mean_se(R, day)
    p = 1.0 if not np.isfinite(se) or se <= 0 else 0.5 * math.erfc(mean / se / math.sqrt(2))
    lo = hi = np.nan
    if ci and n >= MIN_N:
        u, inv = np.unique(day, return_inverse=True)
        S = np.bincount(inv, weights=R)
        Cn = np.bincount(inv).astype(float)
        idx = rng.integers(0, len(u), (B_BOOT, len(u)))
        m = S[idx].sum(1) / Cn[idx].sum(1)
        lo, hi = np.percentile(m, [2.5, 97.5])
    return dict(n=n, mean_r=float(np.mean(R)), win=float(np.mean(P > 0)), mae=float(np.mean(M)), mean_pct=float(np.mean(P)), p=p, lo=lo, hi=hi)


def cell_trades(tabs, coins, side, T, bucket, stop, ex):
    """Pooled trades of one cell after the one-position-per-coin rule: list of per-coin arrays concatenated."""
    out = {k: [] for k in ("net_r", "net_pct", "mae", "day", "split", "coin")}
    for coin in coins:
        tb = tabs[(coin, side, stop, ex)]
        m = (tb["rsi_s"] <= T) if side > 0 else (tb["rsi_s"] >= T)
        if bucket >= 0:
            m &= tb["bucket"] == bucket
        ix = np.where(m)[0]
        if len(ix) == 0:
            continue
        ix = ix[np.argsort(tb["e"][ix], kind="stable")]
        keep = ix[E.pick_one_position(tb["e"][ix], tb["x"][ix])]
        for k in ("net_r", "net_pct", "mae", "day", "split"):
            out[k].append(tb[k][keep])
        out["coin"].append(np.full(len(keep), COINS.index(coin)))
    return {k: (np.concatenate(v) if v else np.array([])) for k, v in out.items()}


def placebo_p(tabs, side, bucket, stop, ex, trades, sp, obs_mean):
    """Share of placebo resamples (matched coin / bucket / split, confirm condition only) with mean >= observed."""
    sel = trades["split"] == sp
    tot = int(sel.sum())
    sums = np.zeros(B_PLAC)
    for ci in np.unique(trades["coin"][sel]):
        nc = int((trades["coin"][sel] == ci).sum())
        tb = tabs[(COINS[int(ci)], side, stop, ex)]
        m = tb["split"] == sp
        if bucket >= 0:
            m &= tb["bucket"] == bucket
        pool = tb["net_r"][m]
        if len(pool) == 0:
            return np.nan, np.nan
        sums += pool[rng.integers(0, len(pool), (B_PLAC, nc))].sum(1)
    means = sums / tot
    return float(means.mean()), float((1 + (means >= obs_mean).sum()) / (B_PLAC + 1))


def bh(pvals, q=0.10):
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    thr = q * (np.arange(1, m + 1)) / m
    ok = p[order] <= thr
    kmax = np.where(ok)[0].max() + 1 if ok.any() else 0
    sig = np.zeros(m, bool)
    sig[order[:kmax]] = True
    return sig


def regime_mix(D):
    """BTC daily close vs 200d SMA: bull > +5 %, bear < -5 %, else range. Share of days per window."""
    c = D["dc"]
    dt = D["dt"]
    sma = np.full(len(c), np.nan)
    cs = np.cumsum(np.insert(c, 0, 0.0))
    sma[199:] = (cs[200:] - cs[:-200]) / 200.0
    lab = np.where(c > sma * 1.05, "bull", np.where(c < sma * 0.95, "bear", "range"))
    lab[np.isnan(sma)] = "na"
    sp = split_of(dt)
    res = {}
    for i, nm in enumerate(SPLITS):
        m = (sp == i) & (lab != "na")
        tot = max(int(m.sum()), 1)
        res[nm] = " / ".join("%s %d%%" % (k, round(100 * (lab[m] == k).sum() / tot)) for k in ("bull", "bear", "range"))
    return res


def main():
    t0 = time.time()
    cd = {c: load(c) for c in COINS if os.path.exists(os.path.join(DATA, c + "_fund.json"))}
    tabs = build(cd)
    coins = list(cd)
    print("built", len(tabs), "tables", round(time.time() - t0), "s", flush=True)
    rows = []
    for side in (1, -1):
        for T in TS[side]:
            for bucket in (0, 1, 2, 3, -1):
                for stop in E.STOPS:
                    for ex in E.EXITS:
                        tr = cell_trades(tabs, coins, side, T, bucket, stop, ex)
                        row = dict(side="long" if side > 0 else "short", T=T, bucket=bucket, stop=stop, exit=ex, family=int(bucket >= 0))
                        btc = cell_trades(tabs, ["BTC"], side, T, bucket, stop, ex)
                        for i, nm in enumerate(SPLITS):
                            sel = tr["split"] == i if len(tr["split"]) else np.array([], bool)
                            st = stats(tr["net_r"][sel], tr["net_pct"][sel], tr["mae"][sel], tr["day"][sel])
                            pm, pp = (np.nan, np.nan)
                            if st["n"] >= MIN_N:
                                pm, pp = placebo_p(tabs, side, bucket, stop, ex, tr, i, st["mean_r"])
                            for k, v in st.items():
                                row["%s_%s" % (nm, k)] = v
                            row["%s_plac_mean" % nm] = pm
                            row["%s_plac_p" % nm] = pp
                            bs = btc["split"] == i if len(btc["split"]) else np.array([], bool)
                            bst = stats(btc["net_r"][bs], btc["net_pct"][bs], btc["mae"][bs], btc["day"][bs], ci=False)
                            row["%s_btc_n" % nm] = bst["n"]
                            row["%s_btc_mean_r" % nm] = bst["mean_r"]
                        rows.append(row)
        print("side done", side, round(time.time() - t0), "s", flush=True)
    fam = [r for r in rows if r["family"]]
    for nm in ("VAL", "DEV"):
        pv = [r["%s_p" % nm] if r["%s_n" % nm] >= MIN_N else 1.0 for r in fam]
        sg = bh(pv)
        for r, s in zip(fam, sg):
            r["%s_bh" % nm] = int(s)
    for r in rows:
        r.setdefault("VAL_bh", 0)
        r.setdefault("DEV_bh", 0)
        r["PASS"] = int(bool(r["family"] and r["VAL_n"] >= MIN_N and r["VAL_mean_r"] > 0 and r["VAL_lo"] > 0 and r["VAL_plac_p"] <= 0.05
                             and r["VAL_bh"] and r["DEV_mean_r"] > 0))
        r["ROBUST"] = int(bool(r["PASS"] and r["RECENT_n"] >= MIN_N and r["RECENT_mean_r"] > 0 and r["RECENT_lo"] > 0))
    keys = list(rows[0].keys())
    with open(os.path.join(HERE, "cells.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: ("%.6g" % v if isinstance(v, float) else v) for k, v in r.items()})
    rm = regime_mix(cd["BTC"])
    json.dump(dict(regime=rm, coins=coins, bars={c: len(cd[c]["t"]) for c in coins},
                   first={c: int(cd[c]["t"][0]) for c in coins}), open(os.path.join(HERE, "meta.json"), "w"))
    print("rows", len(rows), "PASS", sum(r["PASS"] for r in rows), "ROBUST", sum(r["ROBUST"] for r in rows), round(time.time() - t0), "s")


if __name__ == "__main__":
    main()
