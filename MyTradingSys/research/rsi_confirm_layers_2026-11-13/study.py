"""Layers on the RSI-extreme + confirm long (PRE_REG.md in this folder). Run: python study.py
Reads runtime_data/edge4-rsi-confirm-layers-1113 (fetch.py), writes trades (cache), cells.csv, base.csv, pairs.csv, results.json."""
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
import rsi_grid_lib as L  # noqa: E402

CACHE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge4-rsi-confirm-layers-1113"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX", "DOT", "ATOM", "NEAR", "UNI", "TRX", "BCH", "ETC", "FIL", "APT", "ARB"]
TFS = [1, 4]
T_MAX = 20
TAKER = fees.BINANCE_TAKER
HOUR, DAY = L.HOUR, L.DAY
VAL0 = int(np.datetime64("2024-01-01", "ms").astype(np.int64))
NOW = int(time.time() * 1000)
B_BOOT, B_PLAC = 2000, 1000
rng = np.random.default_rng(20261113)
LAYERS = ["dADX<20", "dADX20-25", "dADX>25", "dDI-down", "4hADX>=40", "OI-unwind", "VolCap", "BTC>200MA", "BTC/ETH", "Asia", "US", "FundNeg", "Deep", "SmallR"]
EXITS = {"1R": 1.0, "2R": 2.0}


def week_of(t):
    return (np.asarray(t, np.int64) // DAY + 3) // 7


def last_idx(arr_t, x):
    """Index of last element of sorted arr_t that is <= x, else -1."""
    return int(np.searchsorted(arr_t, x, side="right")) - 1


class Coin:
    def __init__(self, name):
        self.name = name
        a = np.array(json.load(open(os.path.join(CACHE, name + "_60.json"))))
        a = a[a[:, 0] + HOUR <= NOW]
        self.t = a[:, 0].astype(np.int64)
        self.o, self.h, self.l, self.c, self.v = (a[:, i].copy() for i in range(1, 6))
        self.n = len(self.t)
        self.pos = {int(x): i for i, x in enumerate(self.t)}
        d = np.array(json.load(open(os.path.join(CACHE, name + "_D.json"))))
        d = d[d[:, 0] + DAY <= NOW]
        self.dclose_t = d[:, 0].astype(np.int64) + DAY
        self.dc = d[:, 4]
        self.dsma = L.sma(d[:, 4], 200)
        self.dadx, self.dpdi, self.dmdi = L.adx_di(d[:, 2], d[:, 3], d[:, 4])
        f = json.load(open(os.path.join(CACHE, name + "_fund.json")))
        self.f_t = np.array([r[0] for r in f], np.int64)
        self.f_v = np.array([r[1] for r in f])
        oi = np.array(json.load(open(os.path.join(CACHE, name + "_oi.json"))))
        self.oi_t, self.oi_v = (oi[:, 0].astype(np.int64), oi[:, 1]) if len(oi) else (np.zeros(0, np.int64), np.zeros(0))
        self.tf = {}
        for tf in TFS:
            fo = L.fold(self.t, self.o, self.h, self.l, self.c, self.v, tf)
            self.tf[tf] = dict(f=fo, rsi=L.wilder_rsi(fo["c"]))
        f4 = self.tf[4]["f"]
        self.adx4 = L.adx_di(f4["h"], f4["l"], f4["c"])[0]
        self.close4_t = f4["t"] + 4 * HOUR

    def oi_at(self, x):
        if len(self.oi_t) == 0:
            return np.nan
        k = last_idx(self.oi_t, x)
        return self.oi_v[k] if k >= 0 and x - self.oi_t[k] <= 2 * HOUR else np.nan

    def fund_at(self, x):
        k = last_idx(self.f_t, x)
        return self.f_v[k] if k >= 0 and x - self.f_t[k] <= 9 * HOUR else np.nan

    def win(self, e0):
        return [L.fwd_window(a, e0) for a in (self.o, self.h, self.l, self.c)]


def build(co, btc):
    rows = []
    for tf in TFS:
        f, rsi = co.tf[tf]["f"], co.tf[tf]["rsi"]
        for s in L.episodes(rsi, T_MAX):
            s = int(s)
            ci = L.confirm_info(f["t"], f["o"], f["h"], f["l"], f["c"], s, tf)
            if ci is None or not ci["confirm"]:
                continue
            e0 = co.pos.get(ci["entry_close_t"] - HOUR)
            if e0 is None or e0 + L.WIN >= co.n or co.t[e0 + L.WIN] - co.t[e0] != L.WIN * HOUR:
                continue
            tc = int(f["t"][s]) + tf * HOUR  # signal bar close: every layer reads data closed at or before tc
            r = dict(coin=co.name, tf=tf, sig_t=int(f["t"][s]), entry_t=ci["entry_close_t"], rsi=float(rsi[s]),
                     entry=ci["entry"], stop=ci["stop"], stopdist=ci["stopdist"], e0=e0)
            k = last_idx(co.dclose_t, tc)
            ad = co.dadx[k] if k >= 0 else np.nan
            r["dadx"] = ad
            r["ddi_down"] = float(co.dmdi[k] > co.dpdi[k]) if np.isfinite(ad) else np.nan
            j = last_idx(co.close4_t, tc)
            r["adx4"] = co.adx4[j] if j >= 0 else np.nan
            o_now, o_prev = co.oi_at(tc), co.oi_at(tc - 24 * HOUR)
            r["oi24"] = o_now / o_prev - 1 if np.isfinite(o_now) and np.isfinite(o_prev) and o_prev > 0 else np.nan
            vm = f["v"][s - 50:s] if s >= 50 else None
            r["volx"] = float(f["v"][s] / vm.mean()) if vm is not None and vm.mean() > 0 else np.nan
            kb = last_idx(btc.dclose_t, tc)
            r["btc_above"] = float(btc.dc[kb] > btc.dsma[kb]) if kb >= 0 and np.isfinite(btc.dsma[kb]) else np.nan
            r["fund"] = co.fund_at(tc)
            r["hour"] = (int(f["t"][s]) // HOUR) % 24
            rows.append(r)
    return rows


def run_exits(coins, df):
    """Add net_1R / net_2R columns by walking forward windows coin by coin (windows are outcomes, never signals)."""
    for nm in EXITS:
        df["net_" + nm] = np.nan
    for cn, g in df.groupby("coin"):
        co = coins[cn]
        O, H, Lo, C = co.win(g["e0"].values.astype(int))
        R50 = np.zeros_like(O)
        for nm, k in EXITS.items():
            res = L.fwd_exit(g["entry"].values, g["stop"].values, O, H, Lo, C, R50, "tgt", k, TAKER)
            df.loc[g.index, "net_" + nm] = res["net_r"]
    return df


def add_layer_flags(df):
    tert = {tf: np.percentile(df[(df.tf == tf) & (df.entry_t < VAL0)].stopdist, 100 / 3) for tf in TFS}
    df["L_dADX<20"] = df.dadx < 20
    df["L_dADX20-25"] = (df.dadx >= 20) & (df.dadx < 25)
    df["L_dADX>25"] = df.dadx > 25
    df["L_dDI-down"] = df.ddi_down == 1.0
    df["L_4hADX>=40"] = df.adx4 >= 40
    df["L_OI-unwind"] = df.oi24 <= -0.03
    df["L_VolCap"] = df.volx >= 3
    df["L_BTC>200MA"] = df.btc_above == 1.0
    df["L_BTC/ETH"] = df.coin.isin(["BTC", "ETH"])
    df["L_Asia"] = df.hour < 8
    df["L_US"] = df.hour >= 16
    df["L_FundNeg"] = df.fund < 0
    df["L_Deep"] = df.rsi <= 10
    df["L_SmallR"] = df.stopdist <= df.tf.map(tert)
    df["has_OI"] = df.oi24.notna()
    return df, tert


def boot(vals, wk, nb=B_BOOT):
    """Week-block bootstrap of the mean: (mean, lo, hi, p_le0)."""
    if len(vals) == 0:
        return (np.nan,) * 4
    uw, inv = np.unique(wk, return_inverse=True)
    S = np.bincount(inv, weights=vals)
    N = np.bincount(inv).astype(float)
    ix = rng.integers(0, len(uw), (nb, len(uw)))
    m = S[ix].sum(1) / N[ix].sum(1)
    return float(vals.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((np.sum(m <= 0) + 1) / (nb + 1))


def placebo_p(base_vals, n, real_mean):
    """Share of random same-size subsets (no replacement) of the unfiltered base whose mean >= real_mean."""
    if n >= len(base_vals) or n == 0:
        return np.nan
    m = np.array([rng.choice(base_vals, n, replace=False).mean() for _ in range(B_PLAC)])
    return float((np.sum(m >= real_mean) + 1) / (B_PLAC + 1))


def bh(pvals, q=0.10):
    """Benjamini-Hochberg: boolean mask of rejected nulls (nan -> never)."""
    p = np.array([1.0 if not np.isfinite(x) else x for x in pvals])
    m = len(p)
    order = np.argsort(p)
    ok = p[order] <= q * (np.arange(1, m + 1) / m)
    k = int(np.max(np.where(ok)[0])) + 1 if ok.any() else 0
    out = np.zeros(m, bool)
    out[order[:k]] = True
    return out


def stats(sub, col):
    v = sub[col].values
    mean, lo, hi, p = boot(v, week_of(sub.entry_t.values))
    return dict(n=len(v), win=float((v > 0).mean()) if len(v) else np.nan, mean=mean, lo=lo, hi=hi, p=p)


def evaluate(df, mask_fn, label, tf, ex, base_val_vals, base_val_mean, base_dev_mean):
    col = "net_" + ex
    sub = df[df.tf == tf]
    sub = sub[mask_fn(sub)]
    sd, sv = stats(sub[sub.entry_t < VAL0], col), stats(sub[sub.entry_t >= VAL0], col)
    pp = placebo_p(base_val_vals, sv["n"], sv["mean"]) if sv["n"] >= 5 else np.nan
    return dict(split=label, tf=tf, exit=ex, n_dev=sd["n"], mean_dev=sd["mean"], n_val=sv["n"], win_val=sv["win"], mean_val=sv["mean"],
                lo_val=sv["lo"], hi_val=sv["hi"], p_val=sv["p"], vs_base=sv["mean"] - base_val_mean if sv["n"] else np.nan,
                placebo_p=pp, dev_screen=bool(sd["n"] >= 30 and sd["mean"] > 0 and sd["mean"] > base_dev_mean))


def verdicts(r):
    r["bh"] = bh(r.p_val.values)
    r["verdict"] = ["UNDERPOWERED" if x.n_val < 30 else
                    ("PASS" if (x.mean_val > 0 and x.lo_val > 0 and x.vs_base > 0 and x.placebo_p <= 0.05 and x.bh) else "FAIL")
                    for x in r.itertuples()]
    return r


def main():
    coins = {c: Coin(c) for c in COINS}
    btc = coins["BTC"]
    rows = []
    for c in COINS:
        rows += build(coins[c], btc)
    df = pd.DataFrame(rows).sort_values(["entry_t", "coin"]).reset_index(drop=True)
    df = run_exits(coins, df)
    df, tert = add_layer_flags(df)
    df.to_csv(os.path.join(CACHE, "trades.csv"), index=False)
    res, base_rows, bases = [], [], {}
    for tf in TFS:
        for ex in EXITS:
            col = "net_" + ex
            b = df[df.tf == tf]
            bd, bv = b[b.entry_t < VAL0], b[b.entry_t >= VAL0]
            sd, sv = stats(bd, col), stats(bv, col)
            bases[(tf, ex)] = (bv[col].values, sv["mean"], sd["mean"])
            base_rows.append(dict(split="BASE (all)", tf=tf, exit=ex, n_dev=sd["n"], mean_dev=sd["mean"], n_val=sv["n"], win_val=sv["win"],
                                  mean_val=sv["mean"], lo_val=sv["lo"], hi_val=sv["hi"], p_val=sv["p"]))
            for lay in LAYERS:
                res.append(evaluate(df, lambda s, lay=lay: s["L_" + lay], lay, tf, ex, *bases[(tf, ex)]))
    r = verdicts(pd.DataFrame(res))
    r.to_csv(os.path.join(HERE, "cells.csv"), index=False)
    pd.DataFrame(base_rows).to_csv(os.path.join(HERE, "base.csv"), index=False)
    cov = {}
    for tf in TFS:
        s = df[df.tf == tf]
        cov[str(tf)] = dict(n=len(s), n_oi=int(s.has_OI.sum()), n_fund=int(s.fund.notna().sum()), n_dadx=int(s.dadx.notna().sum()),
                            oi_first=str(pd.to_datetime(s[s.has_OI].entry_t.min(), unit="ms")), small_r_cut=float(tert[tf]))
    # stage 2: pairs among layers that pass the DEV screen
    helped, cand = {}, []
    for tf in TFS:
        for ex in EXITS:
            lays = r[(r.tf == tf) & (r.exit == ex) & r.dev_screen].split.tolist()
            helped["%dh/%s" % (tf, ex)] = lays
            for i in range(len(lays)):
                for j in range(i + 1, len(lays)):
                    s = df[(df.tf == tf) & df["L_" + lays[i]] & df["L_" + lays[j]] & (df.entry_t < VAL0)]
                    if len(s) >= 30 and s["net_" + ex].mean() > 0:
                        cand.append((float(s["net_" + ex].mean()), tf, ex, lays[i], lays[j]))
    cand.sort(reverse=True)
    chosen, used = [], set()
    for c in cand:  # one pair per base set first, then fill
        if len(chosen) < 3 and (c[1], c[2]) not in used:
            chosen.append(c)
            used.add((c[1], c[2]))
    for c in cand:
        if len(chosen) < 3 and c not in chosen:
            chosen.append(c)
    pairs = [evaluate(df, lambda s, a=a, b2=b2: s["L_" + a] & s["L_" + b2], a + " + " + b2, tf, ex, *bases[(tf, ex)]) for _, tf, ex, a, b2 in chosen]
    pr = verdicts(pd.DataFrame(pairs)) if pairs else pd.DataFrame()
    pr.to_csv(os.path.join(HERE, "pairs.csv"), index=False)
    json.dump(dict(coverage=cov, dev_screen_layers=helped, n_pairs=len(pairs), data_end=str(pd.to_datetime(df.entry_t.max(), unit="ms")),
                   n_by_tf_split={"%dh" % tf: [int(((df.tf == tf) & (df.entry_t < VAL0)).sum()), int(((df.tf == tf) & (df.entry_t >= VAL0)).sum())] for tf in TFS}),
              open(os.path.join(HERE, "results.json"), "w"), indent=1)
    pd.set_option("display.width", 250)
    print(r.round(3).to_string())
    print(pd.DataFrame(base_rows).round(3).to_string())
    print(pr.round(3).to_string() if len(pr) else "no pairs")
    print(json.dumps(cov, indent=1), helped)


if __name__ == "__main__":
    main()
