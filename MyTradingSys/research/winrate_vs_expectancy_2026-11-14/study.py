"""edge9: win rate vs expectancy. See PRE_REG.md. python study.py [coins...]  -> cells.csv, summary.json"""
import json
import os
import sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge9-winrate-1114"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX",
         "DOT", "ATOM", "TRX", "BCH", "ETC", "UNI", "NEAR", "FIL", "XLM", "AAVE"]
STEP = 300000
W = 288  # 24 h in 5m bars
T0 = 1609459200000
SPLIT = 1704067200000  # 2024-01-01
TARGETS = [0.003, 0.005, 0.01]
STOPS = [0.005, 0.01, 0.02, 0.03]
COST = {"taker": 0.0022, "maker": 0.0013}


def walk(O, H, L, C, e, entry, T, S, W=W):
    """Exit of long entries. e: index of fill bar (array); entry: price (array). Stop-first on same-bar touch.
    Returns (exit_idx, fill_price, ok). ok False when the window has NaN or runs past the end."""
    n = len(O)
    e = np.asarray(e)
    ok = (e + W <= n)
    ex = np.zeros(len(e), dtype=np.int64)
    fp = np.zeros(len(e))
    ok_idx = np.where(ok)[0]
    for a in range(0, len(ok_idx), 20000):
        ii = ok_idx[a:a + 20000]
        ee = e[ii]
        cols = ee[:, None] + np.arange(W)[None, :]
        o, h, l, c = O[cols], H[cols], L[cols], C[cols]
        fin = np.isfinite(o).all(1) & np.isfinite(h).all(1) & np.isfinite(l).all(1) & np.isfinite(c).all(1)
        en = entry[ii][:, None]
        stop = en * (1 - S)
        tgt = en * (1 + T)
        sh = l <= stop
        th = h >= tgt
        big = W + 1
        fs = np.where(sh.any(1), sh.argmax(1), big)
        ft = np.where(th.any(1), th.argmax(1), big)
        stop_first = (fs <= ft) & (fs < big)
        tgt_first = (ft < fs)
        j = np.where(stop_first, fs, np.where(tgt_first, ft, W - 1))
        rows = np.arange(len(ii))
        opn = o[rows, np.minimum(j, W - 1)]
        sp = stop[:, 0]
        price = np.where(stop_first, np.minimum(sp, opn),
                         np.where(tgt_first, tgt[:, 0], c[rows, W - 1]))
        ex[ii] = ee + j
        fp[ii] = price
        ok[ii[~fin]] = False
    return ex, fp, ok


def greedy(sig_e, ex, ok):
    """Keep non-overlapping trades in time order (one open position per coin). Returns keep mask over the input order."""
    keep = np.zeros(len(sig_e), dtype=bool)
    busy = -1
    for i in np.argsort(sig_e, kind="stable"):
        if sig_e[i] <= busy or not ok[i]:
            continue
        keep[i] = True
        busy = ex[i]
    return keep


def wilder_rsi(c, n=14):
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    up, dn = np.maximum(d, 0), np.maximum(-d, 0)
    au, ad = up[:n].mean(), dn[:n].mean()
    out[n] = 100 if ad == 0 else 100 - 100 / (1 + au / ad)
    for i in range(n, len(d)):
        au = (au * (n - 1) + up[i]) / n
        ad = (ad * (n - 1) + dn[i]) / n
        out[i + 1] = 100 if ad == 0 else 100 - 100 / (1 + au / ad)
    return out


def load(sym):
    a = np.array(json.load(open(os.path.join(DATA, sym + "_5m.json"))))
    n = int((a[-1, 0] - T0) // STEP) + 1
    g = np.full((n, 5), np.nan)
    g[((a[:, 0] - T0) // STEP).astype(int)] = a[:, 1:6]
    oi = None
    p = os.path.join(DATA, sym + "_oi1h.json")
    if os.path.exists(p):
        oi = np.array(json.load(open(p)))
    return g[:, 0], g[:, 1], g[:, 2], g[:, 3], oi


def signals(O, H, L, C, oi, rng):
    """Family -> array of signal bar indices (bar closed at its index; fill bar = index + 1)."""
    n = len(C)
    out = {}
    out["S0"] = np.where((rng.random(n) < 1 / 288) & np.isfinite(C))[0]
    k = n // 3
    cc = C[:k * 3].reshape(k, 3)
    idx15 = np.where(np.isfinite(cc).all(1))[0]
    r = wilder_rsi(cc[idx15, 2])
    out["S1"] = idx15[np.where(r <= 25)[0]] * 3 + 2
    tp = pd.Series((H + L + C) / 3)
    m = tp.rolling(48, min_periods=48).mean().values
    with np.errstate(invalid="ignore"):
        out["S2"] = np.where(C <= 0.985 * m)[0]
        prev = np.full(n, np.nan)
        prev[12:] = C[:-12]
        flush = np.where(C <= 0.985 * prev)[0]
    if oi is None or len(oi) < 100:
        out["S3"] = None
    else:
        ts, v = oi[:, 0], oi[:, 1]
        tc = T0 + (flush + 1) * STEP
        k2 = np.searchsorted(ts, tc, side="right") - 1
        good = k2 >= 1
        k2g = np.where(good, k2, 1)
        good &= (ts[k2g] - ts[k2g - 1] == 3600000) & (tc - ts[k2g] <= 3600000)
        chg = v[k2g] / v[k2g - 1] - 1
        out["S3"] = flush[good & (chg <= -0.02)]
    return out


def simulate(O, H, L, C, sigs, fills):
    res = []
    n = len(C)
    for fam, s in sigs.items():
        if s is None:
            continue
        s = s[(s + 1 < n)]
        for fill in fills:
            e = s + 1
            if fill == "taker":
                entry = O[e]
                m = np.isfinite(entry)
            else:
                lim = C[s]
                m = np.isfinite(lim) & np.isfinite(L[e]) & np.isfinite(O[e]) & (L[e] < lim)
                entry = np.where(m, np.minimum(lim, O[e]), np.nan)
            ee, en = e[m], entry[m]
            for T in TARGETS:
                for S in STOPS:
                    ex, fp, ok = walk(O, H, L, C, ee, en, T, S)
                    keep = greedy(ee, ex, ok)
                    res.append((fam, fill, T, S, ee[keep], ex[keep], fp[keep] / en[keep] - 1))
    return res


def day_stats(entry_day, net):
    if len(net) == 0:
        return np.array([]), np.array([])
    _, inv = np.unique(entry_day, return_inverse=True)
    return np.bincount(inv, weights=net), np.bincount(inv).astype(float)


def boot_means(sums, cnts, rng, B=4000):
    nd = len(sums)
    if nd == 0:
        return np.full(B, np.nan)
    idx = rng.integers(0, nd, size=(B, nd))
    return sums[idx].sum(1) / np.maximum(cnts[idx].sum(1), 1)


def worst5(exit_day, net):
    s = pd.Series(net).groupby(exit_day).sum()
    full = s.reindex(np.arange(s.index.min(), s.index.max() + 1), fill_value=0.0)
    return float(full.rolling(5, min_periods=1).sum().min())


def bh(p, q=0.10):
    p = np.asarray(p)
    m = len(p)
    o = np.argsort(p)
    below = np.where(p[o] <= q * np.arange(1, m + 1) / m)[0]
    out = np.zeros(m, dtype=bool)
    if len(below):
        out[o[:below.max() + 1]] = True
    return out


def main(coins):
    rng = np.random.default_rng(20261114)
    trades, skipped = {}, {}
    for sym in coins:
        O, H, L, C, oi = load(sym)
        sigs = signals(O, H, L, C, oi, rng)
        if sigs["S3"] is None:
            skipped[sym] = "no OI"
        for fam, fill, T, S, ei, xi, g in simulate(O, H, L, C, sigs, ("taker", "maker")):
            trades.setdefault((fam, fill, T, S), []).append((T0 + ei * STEP, T0 + xi * STEP, g))
        print("sim", sym, flush=True)
    brng = np.random.default_rng(7)
    cells, boots = [], {}
    for (fam, fill, T, S), parts in sorted(trades.items()):
        et = np.concatenate([p[0] for p in parts])
        xt = np.concatenate([p[1] for p in parts])
        g = np.concatenate([p[2] for p in parts])
        net = g - COST[fill]
        for split, msk in (("VAL", et >= SPLIT), ("DEV", et < SPLIT)):
            gg, nn, e_, x_ = g[msk], net[msk], et[msk], xt[msk]
            n = len(nn)
            wins, losses = gg[gg > 0], gg[gg <= 0]
            gl = -nn[nn < 0].sum()
            sums, cnts = day_stats((e_ // 86400000).astype(int), nn)
            bm = boot_means(sums, cnts, brng)
            row = dict(fam=fam, fill=fill, T=T, S=S, split=split, trades=n,
                       win=float((gg > 0).mean()) if n else np.nan,
                       avg_win=float(wins.mean() * 100) if len(wins) else np.nan,
                       avg_loss=float(losses.mean() * 100) if len(losses) else np.nan,
                       mean_net=float(nn.mean() * 100) if n else np.nan,
                       pf=float(nn[nn > 0].sum() / gl) if gl > 0 else np.nan,
                       worst5=worst5((x_ // 86400000).astype(int), nn * 100) if n else np.nan,
                       breakeven=(S + COST[fill]) / (T + S),
                       ci_lo=float(np.nanpercentile(bm, 2.5) * 100) if n else np.nan,
                       p_pos=float((bm <= 0).mean()) if n else np.nan, mean_ex5=np.nan)
            if split == "VAL":
                if n:
                    keep = np.ones(len(sums), bool)
                    keep[np.argsort(sums)[::-1][:5]] = False
                    row["mean_ex5"] = float(sums[keep].sum() / max(cnts[keep].sum(), 1) * 100)
                boots[(fam, fill, T, S)] = bm
            cells.append(row)
    df = pd.DataFrame(cells)
    val = df[df.split == "VAL"].copy()
    pv = []
    for _, r in val.iterrows():
        b0 = boots.get(("S0", r.fill, r["T"], r.S))
        if r.fam == "S0" or r.trades == 0 or b0 is None or np.isnan(b0).any():
            pv.append(np.nan)
        else:
            pv.append(float((boots[(r.fam, r.fill, r["T"], r.S)] - b0 <= 0).mean()))
    val["p_vs_s0"] = pv
    fam = val[(val.fam != "S0") & (val.trades > 0)]
    flag = bh(fam.p_pos.values)
    val["bh"] = False
    val.loc[fam.index[flag], "bh"] = True
    val["pass"] = ((val.mean_net > 0) & (val.ci_lo > 0) & (val.trades >= 200) & (val.p_vs_s0 < 0.05)
                   & val.bh & (val.mean_ex5 > 0) & (val.fam != "S0"))
    val["win75"] = val.win >= 0.75
    df = df.drop(columns=["mean_ex5"]).merge(
        val[["fam", "fill", "T", "S", "split", "mean_ex5", "p_vs_s0", "bh", "pass", "win75"]],
        on=["fam", "fill", "T", "S", "split"], how="left")
    df.to_csv(os.path.join(HERE, "cells.csv"), index=False)
    json.dump(dict(coins=coins, skipped=skipped, n_family=int(len(fam)), n_pass=int(val["pass"].sum()),
                   n_bh=int(flag.sum())), open(os.path.join(HERE, "summary.json"), "w"), indent=1)
    print("done; pass", int(val["pass"].sum()))


if __name__ == "__main__":
    main(sys.argv[1:] or [c for c in COINS if os.path.exists(os.path.join(DATA, c + "_5m.json"))])
