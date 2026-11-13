"""Deep-RSI-extreme + confirm-candle grid (PRE_REG.md in this folder). Run: python study.py
Reads the kline/OI cache written by fetch.py; writes events_btc.csv, cells.csv, cells_bands.csv, tables.json (+ runtime_data/.../events_all.csv)."""
import datetime as dt
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

CACHE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge3-rsi-deep-extreme-grid-1113"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX"]
TFS = [1, 4, 8, 12]
TS_ALL = [10, 12, 15, 20]
COMBOS = [(1, 10), (1, 15), (1, 20), (4, 10), (4, 15), (4, 20), (8, 15), (8, 20), (12, 15), (12, 20)]
EXITS = [("tgt1", "tgt", 1.0), ("tgt2", "tgt", 2.0), ("tgt3", "tgt", 3.0), ("rsi50", "rsi50", 0), ("time24", "time", 24), ("time72", "time", 72)]
TAKER = fees.BINANCE_TAKER
HOUR, DAY = L.HOUR, L.DAY
SPLITS = [("DEV", None, 1719792000000), ("VAL", 1719792000000, 1751328000000), ("REC", 1751328000000, None)]  # 2024-07-01, 2025-07-01
NOW = int(time.time() * 1000)
B = 2000
K_PLAC = 100
rng = np.random.default_rng(20261113)


def split_of(t):
    t = np.asarray(t)
    return np.where(t < SPLITS[1][1], 0, np.where(t < SPLITS[2][1], 1, 2))


def week_of(t):
    return (np.asarray(t, np.int64) // DAY + 3) // 7


def utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


class Coin:
    def __init__(self, name):
        self.name = name
        a = np.array(json.load(open(os.path.join(CACHE, name + "_60.json"))))
        a = a[a[:, 0] + HOUR <= NOW]
        self.t, self.o, self.h, self.l, self.c, self.v = (a[:, i].copy() for i in range(6))
        self.t = self.t.astype(np.int64)
        self.n = len(self.t)
        self.pos = {int(x): i for i, x in enumerate(self.t)}
        d = np.array(json.load(open(os.path.join(CACHE, name + "_D.json"))))
        d = d[d[:, 0] + DAY <= NOW]
        self.dclose_t = d[:, 0].astype(np.int64) + DAY
        self.dc = d[:, 4]
        self.drsi = L.wilder_rsi(d[:, 4])
        self.dsma = L.sma(d[:, 4], 200)
        self.dadx, self.dpdi, self.dmdi = L.adx_di(d[:, 2], d[:, 3], d[:, 4])
        p = os.path.join(CACHE, name + "_oi.json")
        oi = np.array(json.load(open(p))) if os.path.exists(p) else np.zeros((0, 2))
        self.oi_t, self.oi_v = oi[:, 0].astype(np.int64), oi[:, 1]
        self.tf = {}
        for tf in TFS:
            f = L.fold(self.t, self.o, self.h, self.l, self.c, self.v, tf)
            rsi = L.wilder_rsi(f["c"])
            self.tf[tf] = dict(f=f, rsi=rsi, rsi_h=L.rsi_at_hours(f["t"], rsi, tf, self.t))

    def daily_at(self, tc):
        k = int(np.searchsorted(self.dclose_t, tc, side="right")) - 1
        return k

    def oi_at(self, x):
        if len(self.oi_t) == 0:
            return np.nan
        k = int(np.searchsorted(self.oi_t, x, side="right")) - 1
        return self.oi_v[k] if k >= 0 and x - self.oi_t[k] <= 2 * HOUR else np.nan

    def win(self, e0):
        return [L.fwd_window(a, e0) for a in (self.o, self.h, self.l, self.c)]


def build_events(co):
    rows = []
    for tf in TFS:
        f, rsi = co.tf[tf]["f"], co.tf[tf]["rsi"]
        rsi_by_t = dict(zip(f["t"].tolist(), rsi.tolist()))
        for T in TS_ALL:
            for s in L.episodes(rsi, T):
                s = int(s)
                ci = L.confirm_info(f["t"], f["o"], f["h"], f["l"], f["c"], s, tf)
                if ci is None:
                    continue
                tc = int(f["t"][s]) + tf * HOUR
                k = co.daily_at(tc)
                r = dict(coin=co.name, tf=tf, T=T, sig_open=utc(f["t"][s]), sig_close_t=tc, sig_rsi=float(rsi[s]), sig_low=float(f["l"][s]),
                         sig_color="red" if f["c"][s] < f["o"][s] else "green",
                         drsi=float(co.drsi[k]) if k >= 0 else np.nan, **ci)
                r["entry_time"] = utc(ci["entry_close_t"])
                if k >= 0 and not np.isnan(co.dsma[k]):
                    r["above200"] = bool(co.dc[k] > co.dsma[k])
                else:
                    r["above200"] = None
                r["adx_dn"] = (bool(co.dadx[k] >= 25 and co.dmdi[k] > co.dpdi[k]) if k >= 0 and not np.isnan(co.dadx[k]) else None)
                vm = f["v"][max(0, s - 20):s]
                r["volspike"] = bool(f["v"][s] >= 2 * vm.mean()) if len(vm) == 20 else None
                o_now, o_prev = co.oi_at(tc), co.oi_at(tc - 4 * tf * HOUR)
                r["oi_fell"] = None if np.isnan(o_now) or np.isnan(o_prev) else bool(o_now < o_prev)
                oh = (int(f["t"][s]) // HOUR) % 24
                r["session"] = "Asia" if oh < 8 else ("Europe" if oh < 16 else "US")
                r["weekend"] = bool(((int(f["t"][s]) // DAY + 3) % 7) >= 5)
                e0 = co.pos.get(ci["entry_close_t"] - HOUR)
                ok = e0 is not None and e0 + L.WIN < co.n and co.t[e0 + L.WIN] - co.t[e0] == L.WIN * HOUR
                r["e0"] = e0 if ok else -1
                r["_rsi_by_t"] = rsi_by_t
                rows.append(r)
    return rows


def fwd_metrics(co, rows):
    """Part A forward columns for confirm-yes events with a full window (in place)."""
    idx = [i for i, r in enumerate(rows) if r["confirm"] and r["e0"] >= 0]
    if not idx:
        return
    e0 = np.array([rows[i]["e0"] for i in idx])
    entry = np.array([rows[i]["entry"] for i in idx])
    stop = np.array([rows[i]["stop"] for i in idx])
    O, H, Lo, C = co.win(e0)
    risk = entry - stop
    si = L.fwd_first(Lo <= stop[:, None])
    for q, i in enumerate(idx):
        r = rows[i]
        for hh in (6, 24, 72):
            r["mfe%d" % hh] = H[q, :hh].max() / entry[q] - 1
            r["mae%d" % hh] = Lo[q, :hh].min() / entry[q] - 1
        r["ret24"], r["ret72"], r["ret7d"] = C[q, 23] / entry[q] - 1, C[q, 71] / entry[q] - 1, C[q, 167] / entry[q] - 1
        r["hrs_to_break"] = (si[q] + 1) if si[q] >= 0 else np.nan
        r["broke_7d"] = bool(si[q] >= 0)
        for k in (1, 2, 3):
            ti = L.fwd_first(H[q:q + 1, :72] >= (entry[q] + k * risk[q]))[0]
            if ti >= 0 and (si[q] < 0 or ti < si[q]):
                r["r%d_first" % k] = "target"
            elif si[q] >= 0 and si[q] < 72:
                r["r%d_first" % k] = "stop"
            else:
                r["r%d_first" % k] = "neither"
        j = int(H[q, :72].argmax())
        tf = r["tf"]
        gt = (int(co.t[r["e0"] + 1 + j]) // (tf * HOUR)) * tf * HOUR
        r["rsi_at_peak"] = r["_rsi_by_t"].get(gt, np.nan)
        sd = r["stopdist"]
        r["mfe24_R"], r["mfe72_R"] = r["mfe24"] / sd, r["mfe72"] / sd
    for tgt in (idx,):
        for kind, nm in (("tgt", "tgt2"),):
            pass


def exits_for(co_arrays, tf, e0, entry, stop):
    """Run all 6 exits for trades given as parallel arrays per coin (list of (coin, e0, entry, stop)); returns dict name->net_r concatenated."""
    Os, Hs, Ls, Cs, Rs = [], [], [], [], []
    for co, e, _, _ in co_arrays:
        o, h, l, c = co.win(e)
        Os.append(o); Hs.append(h); Ls.append(l); Cs.append(c)
        Rs.append(L.fwd_window(co.tf[tf]["rsi_h"], e))
    O, H, Lo, C, R = (np.concatenate(x) for x in (Os, Hs, Ls, Cs, Rs))
    en = np.concatenate([x[2] for x in co_arrays])
    st = np.concatenate([x[3] for x in co_arrays])
    return {nm: L.fwd_exit(en, st, O, H, Lo, C, R, kind, p, TAKER)["net_r"] for nm, kind, p in EXITS}


def boot(vals, wk, nb=B):
    """Week-block bootstrap of the mean: returns (mean, lo, hi, p_le0)."""
    n = len(vals)
    if n == 0:
        return (np.nan,) * 4
    uw, inv = np.unique(wk, return_inverse=True)
    S = np.bincount(inv, weights=vals)
    N = np.bincount(inv).astype(float)
    ix = rng.integers(0, len(uw), (nb, len(uw)))
    m = S[ix].sum(1) / N[ix].sum(1)
    return float(vals.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((np.sum(m <= 0) + 1) / (nb + 1))


def placebo_trades(co, tf, w_trade, sd_trade, low_only):
    """Random TF-bar-close entries of coin `co` in the same ISO weeks as the real trades, same stop distances."""
    ids = np.arange(co.n - L.WIN - 1)
    ids = ids[((co.t[ids] + HOUR) % (tf * HOUR)) == 0]
    if low_only:
        rv = co.tf[tf]["rsi_h"][ids]
        ids = ids[rv <= 35]
    wk = week_of(co.t[ids])
    order = np.argsort(wk, kind="stable")
    ids, wk = ids[order], wk[order]
    lo = np.searchsorted(wk, w_trade, side="left")
    hi = np.searchsorted(wk, w_trade, side="right")
    ln = hi - lo
    ok = ln > 0
    pick = lo + np.floor(rng.random(len(w_trade)) * np.maximum(ln, 1)).astype(int)
    e = ids[np.minimum(pick, len(ids) - 1)] if len(ids) else np.zeros(len(w_trade), int)
    entry = co.c[e]
    return e, entry, entry * (1 - sd_trade), ok


def bh(p, q=0.10):
    p = np.asarray(p)
    m = len(p)
    o = np.argsort(p)
    thr = (np.arange(1, m + 1) / m) * q
    passed = p[o] <= thr
    k = (np.max(np.where(passed)[0]) + 1) if passed.any() else 0
    sig = np.zeros(m, bool)
    sig[o[:k]] = True
    return sig


def main():
    t_start = time.time()
    coins = {c: Coin(c) for c in COINS}
    print("loaded", {c: coins[c].n for c in COINS}, flush=True)
    allrows = []
    for c in COINS:
        rows = build_events(coins[c])
        fwd_metrics(coins[c], rows)
        allrows += rows
    ev = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in allrows])
    ev["entry_split"] = np.array(["DEV", "VAL", "REC"])[split_of(ev["entry_close_t"])]
    ev["stopdist_pct"] = 100 * ev["stopdist"]
    ev.to_csv(os.path.join(CACHE, "events_all.csv"), index=False)
    cols = ["coin", "tf", "T", "sig_open", "sig_rsi", "sig_color", "drsi", "confirm", "undercut", "entry", "stop", "stopdist_pct",
            "mfe6", "mae6", "mfe24", "mae24", "mfe72", "mae72", "r1_first", "r2_first", "r3_first", "hrs_to_break",
            "ret24", "ret72", "ret7d", "rsi_at_peak", "entry_time", "entry_split"]
    btc = ev[ev.coin == "BTC"].sort_values(["tf", "T", "sig_open"])
    btc[cols].round(5).to_csv(os.path.join(HERE, "events_btc.csv"), index=False)

    # ---- Part B cells (pooled decision universe + BTC alone), exits for every combo
    cell_rows, band_rows = [], []
    store = {}
    for (tf, T) in COMBOS:
        sub = ev[(ev.tf == tf) & (ev["T"] == T) & ev.confirm & (ev.e0 >= 0)].copy()
        sub = sub.sort_values(["coin", "sig_close_t"])
        if sub.empty:
            continue
        arrs = []
        for c in COINS:
            s2 = sub[sub.coin == c]
            if len(s2):
                arrs.append((coins[c], s2.e0.to_numpy(int), s2.entry.to_numpy(), s2.stop.to_numpy()))
        sub = pd.concat([sub[sub.coin == c] for c in COINS if (sub.coin == c).any()])
        res = exits_for(arrs, tf, None, None, None)
        wk = week_of(sub.entry_close_t.to_numpy())
        sp = split_of(sub.entry_close_t.to_numpy())
        isb = (sub.coin == "BTC").to_numpy()
        dr = sub.drsi.to_numpy()
        band = np.where(dr <= 20, 0, np.where(dr <= 25, 1, np.where(dr <= 30, 2, np.where(dr <= 40, 3, 4))))
        band = np.where(np.isnan(dr), -1, band)
        # placebo draws
        plac = {nm: np.full((K_PLAC, 3), np.nan) for nm, _, _ in EXITS}
        sd_all = sub.stopdist.to_numpy()
        coin_list = [c for c in COINS if (sub.coin == c).any()]
        for kdraw in range(K_PLAC):
            for low_only in (False, True):
                arr2, ents, meta = [], [], []
                off = 0
                for c in coin_list:
                    m = (sub.coin == c).to_numpy()
                    e, en, stp, ok = placebo_trades(coins[c], tf, wk[m], sd_all[m], low_only)
                    arr2.append((coins[c], e, en, stp))
                    meta.append((m, ok, e))
                r2 = exits_for(arr2, tf, None, None, None)
                ent_t = np.concatenate([coins[c].t[e] + HOUR for c, (m, ok, e) in zip(coin_list, meta)])
                okc = np.concatenate([ok for (m, ok, e) in meta])
                spp = split_of(ent_t)
                for nm, kind, p in EXITS:
                    if (nm == "rsi50") != low_only:
                        continue
                    for si_ in range(3):
                        mm = okc & (spp == si_)
                        plac[nm][kdraw, si_] = r2[nm][mm].mean() if mm.any() else np.nan
        for nm, kind, p in EXITS:
            x = res[nm]
            for uni, um in (("pooled", np.ones(len(x), bool)), ("BTC", isb)):
                rec = dict(tf=tf, T=T, exit=nm, universe=uni)
                for si_, (sn, _, _) in enumerate(SPLITS):
                    mm = um & (sp == si_)
                    v = x[mm]
                    mean, lo, hi, pv = boot(v, wk[mm]) if len(v) else (np.nan,) * 4
                    rec.update({sn + "_n": int(len(v)), sn + "_mean": mean, sn + "_lo": lo, sn + "_hi": hi, sn + "_p": pv,
                                sn + "_win": float((v > 0).mean()) if len(v) else np.nan})
                    if uni == "pooled":
                        pm = plac[nm][:, si_]
                        pm = pm[~np.isnan(pm)]
                        rec[sn + "_plac_mean"] = float(pm.mean()) if len(pm) else np.nan
                        rec[sn + "_plac_p"] = float((np.sum(pm >= mean) + 1) / (len(pm) + 1)) if len(pm) and len(v) else np.nan
                cell_rows.append(rec)
            for b in range(-1, 5):
                for si_, (sn, _, _) in enumerate(SPLITS):
                    mm = (band == b) & (sp == si_)
                    band_rows.append(dict(tf=tf, T=T, exit=nm, band=["nan", "<=20", "20-25", "25-30", "30-40", ">40"][b + 1], split=sn,
                                          n=int(mm.sum()), mean=float(x[mm].mean()) if mm.any() else np.nan))
        store[(tf, T)] = (sub, res)
        print("combo", tf, T, len(sub), "t=%.0fs" % (time.time() - t_start), flush=True)
    cells = pd.DataFrame(cell_rows)
    pool = cells.universe == "pooled"
    sig = bh(cells.loc[pool, "VAL_p"].fillna(1.0).to_numpy())
    cells["bh_sig"] = False
    cells.loc[pool, "bh_sig"] = sig
    v = cells
    ok = pool & (v.VAL_n >= 30) & (v.VAL_mean > 0) & (v.VAL_lo > 0) & (v.VAL_plac_p <= 0.05) & v.bh_sig
    cells["verdict"] = np.where(~pool, "BTC-descriptive", np.where(ok & (v.DEV_mean > 0) & (v.REC_mean > 0), "ROBUST",
                                np.where(ok, "PASS", np.where(v.VAL_n < 30, "UNDERPOWERED", "FAIL"))))
    cells.round(5).to_csv(os.path.join(HERE, "cells.csv"), index=False)
    pd.DataFrame(band_rows).round(5).to_csv(os.path.join(HERE, "cells_bands.csv"), index=False)
    print(cells[pool].verdict.value_counts().to_dict(), flush=True)

    # ---- Parts C and D on pooled confirm-yes, T=20, per TF (tgt2 net R from the stored exits)
    layers, where = [], []
    for tf in TFS:
        key = (tf, 20)
        if key not in store:
            continue
        sub, res = store[key]
        sub = sub.copy()
        sub["netr_tgt2"] = res["tgt2"]
        sub["win1"] = sub.r1_first == "target"
        feats = [("daily trend", "above200", {True: "above 200d SMA", False: "below 200d SMA"}),
                 ("daily ADX>=25 & -DI>+DI", "adx_dn", {True: "yes", False: "no"}),
                 ("OI over last 4 bars", "oi_fell", {True: "fell", False: "rose/flat"}),
                 ("signal volume >=2x 20-bar mean", "volspike", {True: "yes", False: "no"}),
                 ("session of signal bar", "session", {"Asia": "Asia 0-8", "Europe": "Europe 8-16", "US": "US 16-24"}),
                 ("weekend", "weekend", {True: "Sat/Sun", False: "Mon-Fri"})]
        for lname, col, lv in feats:
            for val, lab in lv.items():
                m = sub[col] == val
                d = sub[m]
                layers.append(dict(tf=tf, layer=lname, level=lab, n=int(len(d)), thin=len(d) < 30,
                                   win1R=float(d.win1.mean()) if len(d) else np.nan, mean_R_tgt2=float(d.netr_tgt2.mean()) if len(d) else np.nan))
            layers.append(dict(tf=tf, layer=lname, level="(missing)", n=int(sub[col].isna().sum()), thin=True, win1R=np.nan, mean_R_tgt2=np.nan))
        for tname, tm in (("above 200d SMA", sub.above200 == True), ("below 200d SMA", sub.above200 == False), ("all", sub.above200.notna() | sub.above200.isna())):  # noqa: E712
            d = sub[tm]
            if not len(d):
                continue
            where.append(dict(tf=tf, trend=tname, n=int(len(d)), thin=len(d) < 30,
                              med_mfe24_pct=100 * d.mfe24.median(), med_mfe24_R=d.mfe24_R.median(), med_mfe72_pct=100 * d.mfe72.median(), med_mfe72_R=d.mfe72_R.median(),
                              reach_1R=float((d.r1_first == "target").mean()), reach_2R=float((d.r2_first == "target").mean()), reach_3R=float((d.r3_first == "target").mean()),
                              new_low_7d=float(d.broke_7d.mean()), med_stop_pct=100 * d.stopdist.median()))
    json.dump(dict(layers=layers, where=where), open(os.path.join(CACHE, "layers_where.json"), "w"), default=str)

    # ---- today's trade (BTC 1h signal bar opened 2026-11-13 05:00Z)
    co = coins["BTC"]
    f = co.tf[1]["f"]
    s = int(np.where(f["t"] == 1794546000000)[0][0]) if 1794546000000 in set(f["t"].tolist()) else None
    out = {}
    if s is not None:
        ci = L.confirm_info(f["t"], f["o"], f["h"], f["l"], f["c"], s, 1)
        e0 = co.pos[ci["entry_close_t"] - HOUR]
        h, l, c = co.h[e0 + 1:], co.l[e0 + 1:], co.c[e0 + 1:]
        risk = ci["entry"] - ci["stop"]
        brk = np.where(l <= ci["stop"])[0]
        out = dict(rsi_sig=float(co.tf[1]["rsi"][s]), low=ci["stop"], close=float(f["c"][s]), entry=ci["entry"], entry_time=utc(ci["entry_close_t"]),
                   stopdist_pct=100 * ci["stopdist"], confirm=ci["confirm"], stopped=bool(len(brk)), bars_since=int(len(c)),
                   max_high=float(h.max()) if len(h) else None, best_R=float((h.max() - ci["entry"]) / risk) if len(h) else None,
                   worst_low=float(l.min()) if len(l) else None, last_close=float(c[-1]) if len(c) else None,
                   last_R=float((c[-1] - ci["entry"]) / risk) if len(c) else None, last_bar_open=utc(co.t[-1]), daily_rsi=float(co.drsi[co.daily_at(int(f["t"][s]) + HOUR)]))
    json.dump(out, open(os.path.join(CACHE, "today.json"), "w"), default=str)
    print("today", out, flush=True)
    print("done %.0fs" % (time.time() - t_start))


if __name__ == "__main__":
    main()
