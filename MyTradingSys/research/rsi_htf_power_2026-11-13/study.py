"""Power test of two RSI-HTF-extreme leads on new data (PRE_REG.md). Run: python study.py  (after fetch.py)
Writes cells.csv, trades.csv, meta.json next to this file."""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "backtest")))
import fees  # noqa: E402
import rsi_grid_lib as G  # noqa: E402
import htf_lib as H  # noqa: E402
from fetch import PARENT20, NEW40  # noqa: E402

CACHE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge5-rsi-htf-power-1113"))
CAP_BARS = 20
TIME_BARS = 10
COST = 2 * (fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 / 2)
HOUR, DAY = H.HOUR, H.DAY
CUT20 = 1577836800000  # 2020-01-01 UTC
NOW = int(time.time() * 1000)
NB = int(os.environ.get("NB", 5000))
K_PLAC = int(os.environ.get("K_PLAC", 400))
BONF = 0.05 / 6
rng = np.random.default_rng(20261113)
SIGNALS = [("S1", "4h<=12 & d<30", 4, 12, True), ("S2", "4h<=15 & d<30", 4, 15, True), ("S3", "12h<=20", 12, 20, False)]
EXITS = ["tgt2R", "time10"]


def month_of(t):
    d = np.asarray(t, np.int64).astype("datetime64[ms]")
    return d.astype("datetime64[M]").astype(np.int64)


class Coin:
    def __init__(self, name):
        self.name = name
        a = np.array(json.load(open(os.path.join(CACHE, name + "_1h.json"))))
        a = a[a[:, 0] + HOUR <= NOW]
        self.t = a[:, 0].astype(np.int64)
        self.o, self.h, self.l, self.c, self.v = (a[:, i].copy() for i in range(1, 6))
        self.n = len(self.t)
        self.pos = {int(x): i for i, x in enumerate(self.t)}
        d = np.array(json.load(open(os.path.join(CACHE, name + "_1d.json"))))
        d = d[d[:, 0] + DAY <= NOW]
        self.dclose_t = d[:, 0].astype(np.int64) + DAY
        self.dc = d[:, 4]
        self.drsi = G.wilder_rsi(d[:, 4])
        self.tf = {}
        for tf in (4, 12):
            f = G.fold(self.t, self.o, self.h, self.l, self.c, self.v, tf)
            self.tf[tf] = dict(f=f, rsi=G.wilder_rsi(f["c"]))

    def didx(self, tc):
        return np.searchsorted(self.dclose_t, np.asarray(tc, np.int64), side="right") - 1

    def full_window(self, e0, w):
        return e0 >= 0 and e0 + w < self.n and self.t[e0 + w] - self.t[e0] == w * HOUR

    def wins(self, e0, w):
        return [H.fwd_window(x, e0, w) for x in (self.o, self.h, self.l, self.c)]


def trade_rs(co, e0, entry, stop, tf):
    w = CAP_BARS * tf
    O, Hh, Lo, C = co.wins(e0, w)
    return {"tgt2R": H.fwd_exit_r(entry, stop, O, Hh, Lo, C, "tgt", 2.0, w, COST),
            "time10": H.fwd_exit_r(entry, stop, O, Hh, Lo, C, "time", TIME_BARS * tf, TIME_BARS * tf, COST)}


def build(coins, btc):
    sma = pd.Series(btc.dc).rolling(200).mean().to_numpy()
    rows = []
    for co in coins.values():
        for sid, _, tf, T, gate in SIGNALS:
            f, rsi = co.tf[tf]["f"], co.tf[tf]["rsi"]
            w = CAP_BARS * tf
            for s, entry, stop, ect in H.signal_events(f["t"], f["o"], f["h"], f["l"], f["c"], rsi, T, tf):
                e0 = co.pos.get(ect - HOUR, -1)
                if not co.full_window(e0, w):
                    continue
                sig_t = int(f["t"][s])
                tc = sig_t + tf * HOUR
                k0 = int(co.didx(tc))
                dr = float(co.drsi[k0]) if k0 >= 0 else np.nan
                if gate and not (dr < 30):
                    continue
                if co.name in PARENT20:
                    if ect >= CUT20:
                        continue
                    blk = "B1"
                else:
                    blk = "B2"
                k = int(btc.didx(tc))
                reg = "na"
                if k >= 0 and not np.isnan(sma[k]):
                    reg = "bull" if btc.dc[k] > sma[k] else "bear"
                rows.append(dict(sig=sid, coin=co.name, blk=blk, tf=tf, e0=e0, entry=entry, stop=stop, entry_t=ect, sig_t=sig_t,
                                 drsi=dr, stopdist=(entry - stop) / entry, regime=reg))
    return pd.DataFrame(rows)


def candidates(co, tf, btc, kind, blk):
    """Candidate placebo entry hours (index e0) for one coin: TF-bar closes with a full forward window, sorted by match key."""
    w = CAP_BARS * tf
    ids = np.arange(co.n - w - 1)
    ids = ids[((co.t[ids] + HOUR) % (tf * HOUR)) == 0]
    ids = ids[(co.t[ids + w] - co.t[ids]) == w * HOUR]
    ect = co.t[ids] + HOUR
    if blk == "B1":
        keep = ect < CUT20
        ids, ect = ids[keep], ect[keep]
    if kind == "A":
        key = month_of(ect)
    else:
        k = btc.didx(ect)
        r = np.where(k >= 0, btc.drsi[np.maximum(k, 0)], np.nan)
        keep = r < 35
        ids, ect = ids[keep], ect[keep]
        key = np.zeros(len(ids), np.int64)
    o = np.argsort(key, kind="stable")
    return ids[o], key[o]


def placebo(coins, btc, sub, kind, cache):
    """One draw: dict exit -> R aligned to sub (nan where no candidate)."""
    out = {nm: np.full(len(sub), np.nan) for nm in EXITS}
    coin_arr, blk_arr = sub.coin.to_numpy(), sub.blk.to_numpy()
    for (c, b) in set(zip(coin_arr, blk_arr)):
        ix = np.where((coin_arr == c) & (blk_arr == b))[0]
        g = sub.iloc[ix]
        tf = int(g.tf.iloc[0])
        ck = (c, b, tf, kind)
        if ck not in cache:
            cache[ck] = candidates(coins[c], tf, btc, kind, b)
        ids, key = cache[ck]
        if len(ids) == 0:
            continue
        tk = month_of(g.entry_t.to_numpy()) if kind == "A" else np.zeros(len(g), np.int64)
        lo, hi = np.searchsorted(key, tk, "left"), np.searchsorted(key, tk, "right")
        ok = (hi - lo) > 0
        pick = lo + np.floor(rng.random(len(tk)) * np.maximum(hi - lo, 1)).astype(int)
        e = ids[np.minimum(pick, len(ids) - 1)]
        co = coins[c]
        entry = co.c[e]
        stop = entry * (1 - g.stopdist.to_numpy())
        r = trade_rs(co, e, entry, stop, tf)
        for nm in r:
            out[nm][ix[ok]] = r[nm][ok]
    return out


def pstat(draws, mask, real):
    m = np.array([np.nanmean(d[mask]) if np.isfinite(d[mask]).any() else np.nan for d in draws])
    m = m[~np.isnan(m)]
    if len(m) == 0:
        return np.nan, np.nan
    return float(m.mean()), float((np.sum(m >= real) + 1) / (len(m) + 1))


def cell_rows(sid, label, sub, x, plac, nm):
    """Stats rows (B1, B2, POOL) for one signal x exit. x = net R per trade; plac = {'A': [arrays], 'B': [arrays]} for this exit."""
    rows = []
    day = sub.sig_t.to_numpy() // DAY
    yr = pd.to_datetime(sub.entry_t.to_numpy(), unit="ms").year.to_numpy()
    for bl in ("B1", "B2", "POOL"):
        m = np.ones(len(sub), bool) if bl == "POOL" else (sub.blk.to_numpy() == bl)
        v = x[m]
        rec = dict(sig=sid, signal=label, exit=nm, block=bl, n=int(len(v)))
        if len(v) == 0:
            rows.append(rec)
            continue
        dd = day[m]
        ds = pd.Series(v).groupby(dd).sum()
        mean, tlo, thi, _ = H.week_boot(v, np.arange(len(v)), rng, NB)
        _, dlo, dhi, dp = H.week_boot(v, dd, rng, NB)
        rec.update(days=int(len(ds)), win=float((v > 0).mean()), mean=mean, median=float(np.median(v)), tlo=tlo, thi=thi,
                   dlo=dlo, dhi=dhi, dp=dp)
        for kk in ("A", "B"):
            rec[kk + "_mean"], rec[kk + "_p"] = pstat(plac[kk], m, mean)
        ym = yr[m]
        rec["per_year"] = "; ".join("%d:%.2f(n%d)" % (y, v[ym == y].mean(), (ym == y).sum()) for y in sorted(set(ym)))
        top = ds.sort_values(ascending=False).index[:5]
        tot = float(v.sum())
        rec["top5_share"] = float(ds.loc[top].sum() / tot) if tot > 0 else np.nan
        keep = ~np.isin(dd, top)
        rec["ex5_n"] = int(keep.sum())
        rec["ex5_mean"] = float(v[keep].mean()) if keep.any() else np.nan
        for rg in ("bull", "bear", "na"):
            mm = sub.regime.to_numpy()[m] == rg
            rec[rg + "_n"] = int(mm.sum())
            rec[rg + "_mean"] = float(v[mm].mean()) if mm.any() else np.nan
            rec[rg + "_win"] = float((v[mm] > 0).mean()) if mm.any() else np.nan
        if bl == "POOL":
            ok = (rec["days"] >= 30) and mean > 0 and tlo > 0 and dlo > 0 and rec["A_p"] <= BONF and rec["B_p"] <= BONF and dp <= BONF
            rec["verdict"] = "PASS" if ok else ("UNDERPOWERED" if rec["days"] < 30 else "FAIL")
        rows.append(rec)
    return rows


def main():
    t0 = time.time()
    coins, missing = {}, []
    for c in PARENT20 + NEW40:
        try:
            coins[c] = Coin(c)
        except Exception:
            missing.append(c)
    btc = coins["BTC"]
    first = {c: pd.Timestamp(coins[c].t[0], unit="ms").strftime("%Y-%m-%d") for c in coins}
    print("loaded", len(coins), "missing", missing, flush=True)
    ev = build(coins, btc)
    print("events", ev.groupby(["sig", "blk"]).size().to_dict(), flush=True)
    out, trades = [], []
    for sid, label, tf, T, gate in SIGNALS:
        sub = ev[ev.sig == sid].sort_values(["coin", "entry_t"]).reset_index(drop=True)
        if sub.empty:
            continue
        res = {nm: np.full(len(sub), np.nan) for nm in EXITS}
        for c, g in sub.groupby("coin"):
            r = trade_rs(coins[c], g.e0.to_numpy(int), g.entry.to_numpy(), g.stop.to_numpy(), tf)
            for nm in r:
                res[nm][g.index.to_numpy()] = r[nm]
        plac, cache = {"A": [], "B": []}, {}
        for kk in ("A", "B"):
            for _ in range(K_PLAC):
                plac[kk].append(placebo(coins, btc, sub, kk, cache))
        for nm in EXITS:
            out += cell_rows(sid, label, sub, res[nm], {kk: [d[nm] for d in plac[kk]] for kk in plac}, nm)
        trades.append(sub.assign(**res))
        print("signal", sid, len(sub), "t=%.0fs" % (time.time() - t0), flush=True)
    cells = pd.DataFrame(out)
    cells.round(5).to_csv(os.path.join(HERE, "cells.csv"), index=False)
    pd.concat(trades).drop(columns=["e0"]).round(6).to_csv(os.path.join(HERE, "trades.csv"), index=False)
    json.dump(dict(missing=missing, first_bar=first, n_coins=len(coins)), open(os.path.join(HERE, "meta.json"), "w"), indent=1)
    print(cells[cells.block == "POOL"][["sig", "exit", "n", "days", "mean", "tlo", "dlo", "A_p", "B_p", "verdict"]].to_string(), flush=True)


if __name__ == "__main__":
    main()
