"""Three pre-registered cells on 40 new coins (PRE_REG.md in this folder). Run: python study.py
Reads runtime_data/edge5-rsi-oi-unwind-newcoins-1113 (fetch.py); writes trades cache, results.json."""
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
from fetch import COINS  # noqa: E402

CACHE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge5-rsi-oi-unwind-newcoins-1113"))
TFS = [1, 4]
T_MAX = 20
COST = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13   # round-trip fraction of entry price
HOUR, DAY = L.HOUR, L.DAY
NOW = int(time.time() * 1000)
Y2024 = int(np.datetime64("2024-01-01", "ms").astype(np.int64))
B_BOOT, B_PLAC = 5000, 2000
rng = np.random.default_rng(20261113)
BONF = 3


def last_idx(arr_t, x):
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
        self.dadx = L.adx_di(d[:, 2], d[:, 3], d[:, 4])[0]
        oi = np.array(json.load(open(os.path.join(CACHE, name + "_oi.json"))))
        self.oi_t, self.oi_v = (oi[:, 0].astype(np.int64), oi[:, 1]) if len(oi) else (np.zeros(0, np.int64), np.zeros(0))
        self.tf = {}
        for tf in TFS:
            fo = L.fold(self.t, self.o, self.h, self.l, self.c, self.v, tf)
            self.tf[tf] = dict(f=fo, rsi=L.wilder_rsi(fo["c"]))

    def oi_at(self, x):
        if len(self.oi_t) == 0:
            return np.nan
        k = last_idx(self.oi_t, x)
        return self.oi_v[k] if k >= 0 and x - self.oi_t[k] <= 2 * HOUR else np.nan

    def win(self, e0):
        return [L.fwd_window(a, e0) for a in (self.o, self.h, self.l, self.c)]


def build(co):
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
            tc = int(f["t"][s]) + tf * HOUR
            r = dict(coin=co.name, tf=tf, sig_t=int(f["t"][s]), entry_t=ci["entry_close_t"], rsi=float(rsi[s]),
                     entry=ci["entry"], stop=ci["stop"], stopdist=ci["stopdist"], e0=e0)
            k = last_idx(co.dclose_t, tc)
            r["dadx"] = co.dadx[k] if k >= 0 else np.nan
            o_now, o_prev = co.oi_at(tc), co.oi_at(tc - 24 * HOUR)
            r["oi24"] = o_now / o_prev - 1 if np.isfinite(o_now) and np.isfinite(o_prev) and o_prev > 0 else np.nan
            r["hour"] = (int(f["t"][s]) // HOUR) % 24
            rows.append(r)
    return rows


def run_exit(coins, df):
    df["net_r"] = np.nan
    for cn, g in df.groupby("coin"):
        O, H, Lo, C = coins[cn].win(g["e0"].values.astype(int))
        res = L.fwd_exit(g["entry"].values, g["stop"].values, O, H, Lo, C, np.zeros_like(O), "tgt", 2.0, COST / 2)
        df.loc[g.index, "net_r"] = res["net_r"]
    return df


def boot_trade(v):
    ix = rng.integers(0, len(v), (B_BOOT, len(v)))
    m = v[ix].mean(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def boot_day(v, day):
    ud, inv = np.unique(day, return_inverse=True)
    S = np.bincount(inv, weights=v)
    N = np.bincount(inv).astype(float)
    ix = rng.integers(0, len(ud), (B_BOOT, len(ud)))
    m = S[ix].sum(1) / N[ix].sum(1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((np.sum(m <= 0) + 1) / (B_BOOT + 1))


def placebo_p(base, n, real):
    if n >= len(base) or n == 0:
        return np.nan
    m = np.array([rng.choice(base, n, replace=False).mean() for _ in range(B_PLAC)])
    return float((np.sum(m >= real) + 1) / (B_PLAC + 1))


def best5(sub):
    d = sub.groupby("day").net_r.sum().sort_values(ascending=False)
    tot = d.sum()
    top = d.index[:5]
    rest = sub[~sub.day.isin(top)].net_r
    return (float(d.iloc[:5].sum() / tot) if tot > 0 else np.nan), (float(rest.mean()) if len(rest) else np.nan), len(rest)


def cell(df, label, tf, mask, min_n):
    base = df[df.tf == tf]
    sub = base[mask(base)]
    v, day = sub.net_r.values, sub.day.values
    out = dict(cell=label, tf=tf, n=len(sub), days=int(sub.day.nunique()), n_base=len(base), base_mean=float(base.net_r.mean()),
               base_win=float((base.net_r > 0).mean()), n_noOI=int(base.oi24.isna().sum()))
    if len(sub) < 5:
        out.update(verdict="UNDERPOWERED")
        return out
    out.update(win=float((v > 0).mean()), mean=float(v.mean()))
    out["t_lo"], out["t_hi"] = boot_trade(v)
    out["d_lo"], out["d_hi"], out["d_p"] = boot_day(v, day)
    out["placebo_p"] = placebo_p(base.net_r.values, len(sub), v.mean())
    s24 = sub[sub.entry_t >= Y2024]
    out["n_2024"], out["mean_2024"] = len(s24), (float(s24.net_r.mean()) if len(s24) else np.nan)
    out["per_year"] = {str(y): [int(len(g)), round(float(g.net_r.mean()), 3)] for y, g in sub.groupby(pd.to_datetime(sub.entry_t, unit="ms").dt.year)}
    out["best5_share"], out["mean_wo_best5"], out["n_wo_best5"] = best5(sub)
    out["n_coins"] = int(sub.coin.nunique())
    thr = 0.05 / BONF
    ok = (out["mean"] > 0 and out["t_lo"] > 0 and out["d_lo"] > 0 and out["mean"] > out["base_mean"]
          and out["placebo_p"] <= thr and out["d_p"] <= thr)
    if len(sub) < min_n or out["days"] < 40:
        out["verdict"] = "UNDERPOWERED"
    else:
        out["verdict"] = "PASS" if ok else "FAIL"
    if out["verdict"] != "FAIL" and not (out["mean_wo_best5"] > 0):
        out["verdict"] += " FRAGILE"
    return out


def main():
    coins, cov = {}, {}
    for c in COINS:
        coins[c] = Coin(c)
        co = coins[c]
        cov[c] = dict(bars_1h=co.n, first=str(pd.to_datetime(co.t[0], unit="ms"))[:10],
                      oi_first=str(pd.to_datetime(co.oi_t[0], unit="ms"))[:10] if len(co.oi_t) else None, oi_n=len(co.oi_t))
    rows = []
    for c in COINS:
        rows += build(coins[c])
    df = pd.DataFrame(rows).sort_values(["entry_t", "coin"]).reset_index(drop=True)
    df = run_exit(coins, df)
    df["day"] = (df.sig_t // DAY).astype(int)
    df.to_csv(os.path.join(CACHE, "trades.csv"), index=False)

    def A(s):
        return s.oi24 <= -0.03

    cells = [cell(df, "A 1h OI-unwind +2R", 1, A, 100),
             cell(df, "B 4h dADX20-25 +2R", 4, lambda s: (s.dadx >= 20) & (s.dadx < 25), 60),
             cell(df, "C 1h OI-unwind & US 13-21", 1, lambda s: A(s) & (s.hour >= 13) & (s.hour <= 20), 100)]
    base = {str(tf): dict(n=int((df.tf == tf).sum()), mean=float(df[df.tf == tf].net_r.mean()), win=float((df[df.tf == tf].net_r > 0).mean()),
                          mean_2024=float(df[(df.tf == tf) & (df.entry_t >= Y2024)].net_r.mean())) for tf in TFS}
    json.dump(dict(cells=cells, coverage=cov, cost_rt=COST, base=base, data_end=str(pd.to_datetime(df.entry_t.max(), unit="ms"))),
              open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print(json.dumps(cells, indent=1))
    print(base)


if __name__ == "__main__":
    main()
