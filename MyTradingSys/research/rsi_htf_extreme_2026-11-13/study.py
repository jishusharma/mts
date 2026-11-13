"""HTF RSI extreme study (PRE_REG.md). Run: python study.py
Reads runtime_data/edge4-rsi-htf-extreme-1113 klines; writes cells.csv, bands.csv, meta.json."""
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

CACHE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge4-rsi-htf-extreme-1113"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX", "DOT", "ATOM", "UNI", "TRX", "BCH", "ETC", "FIL", "XLM", "NEAR", "SAND"]
COMBOS = [(4, 20), (4, 15), (4, 12), (8, 25), (8, 20), (8, 15), (12, 25), (12, 20), (12, 15)]
EXITS = [("tgt1R", "tgt", 1.0), ("tgt2R", "tgt", 2.0), ("tgt3R", "tgt", 3.0), ("time10", "time", 10)]
CAP_BARS = 20
COST = 2 * (fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 / 2)  # round trip, fraction of price
HOUR, DAY = H.HOUR, H.DAY
CUT = 1704067200000  # 2024-01-01 UTC
NOW = int(time.time() * 1000)
K_PLAC = 100
rng = np.random.default_rng(20261113)


def week_of(t):
    return (np.asarray(t, np.int64) // DAY + 3) // 7


def split_of(t):
    return (np.asarray(t) >= CUT).astype(int)  # 0 DEV, 1 VAL


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
        self.drsi = G.wilder_rsi(d[:, 4])
        self.tf = {}
        for tf in (4, 8, 12):
            f = G.fold(self.t, self.o, self.h, self.l, self.c, self.v, tf)
            self.tf[tf] = dict(f=f, rsi=G.wilder_rsi(f["c"]))

    def daily_rsi_at(self, tc):
        k = int(np.searchsorted(self.dclose_t, tc, side="right")) - 1
        return float(self.drsi[k]) if k >= 0 else np.nan

    def full_window(self, e0, w):
        return e0 >= 0 and e0 + w < self.n and self.t[e0 + w] - self.t[e0] == w * HOUR

    def wins(self, e0, w):
        return [H.fwd_window(x, e0, w) for x in (self.o, self.h, self.l, self.c)]


def trade_rs(co, e0, entry, stop, tf):
    """dict exit name -> net R array for trades of one coin."""
    w = CAP_BARS * tf
    O, Hh, Lo, C = co.wins(e0, w)
    return {nm: H.fwd_exit_r(entry, stop, O, Hh, Lo, C, kind, p, w if kind == "tgt" else int(p * tf), COST) for nm, kind, p in EXITS}


def build(coins):
    rows = []
    for co in coins.values():
        for tf in (4, 8, 12):
            f, rsi = co.tf[tf]["f"], co.tf[tf]["rsi"]
            w = CAP_BARS * tf
            for T in sorted({t for (x, t) in COMBOS if x == tf}):
                for s, entry, stop, ect in H.signal_events(f["t"], f["o"], f["h"], f["l"], f["c"], rsi, T, tf):
                    e0 = co.pos.get(ect - HOUR, -1)
                    if not co.full_window(e0, w):
                        continue
                    rows.append(dict(coin=co.name, tf=tf, T=T, s=s, e0=e0, entry=entry, stop=stop, entry_t=ect,
                                     drsi=co.daily_rsi_at(int(f["t"][s]) + tf * HOUR), stopdist=(entry - stop) / entry))
    return pd.DataFrame(rows)


def placebo(coins, sub, tf):
    """One placebo draw (same coin, same ISO week, same stop distance): dict exit -> net R aligned to sub rows (nan = no candidate)."""
    out = {nm: np.full(len(sub), np.nan) for nm, _, _ in EXITS}
    w = CAP_BARS * tf
    coin_arr = sub.coin.to_numpy()
    for c in np.unique(coin_arr):
        ix = np.where(coin_arr == c)[0]
        g = sub.iloc[ix]
        co = coins[c]
        ids = np.arange(co.n - w - 1)
        ids = ids[((co.t[ids] + HOUR) % (tf * HOUR)) == 0]
        ids = ids[(co.t[ids + w] - co.t[ids]) == w * HOUR]
        if len(ids) == 0:
            continue
        wk = week_of(co.t[ids])
        order = np.argsort(wk, kind="stable")
        ids, wk = ids[order], wk[order]
        tw = week_of(g.entry_t.to_numpy())
        lo, hi = np.searchsorted(wk, tw, "left"), np.searchsorted(wk, tw, "right")
        ok = (hi - lo) > 0
        pick = lo + np.floor(rng.random(len(tw)) * np.maximum(hi - lo, 1)).astype(int)
        e = ids[np.minimum(pick, len(ids) - 1)]
        entry = co.c[e]
        stop = entry * (1 - g.stopdist.to_numpy())
        r = trade_rs(co, e, entry, stop, tf)
        for nm in r:
            out[nm][ix[ok]] = r[nm][ok]
    return out


def run_cell(tf, T, sub, res, plac, gate):
    rows = []
    sp = split_of(sub.entry_t.to_numpy())
    wk = week_of(sub.entry_t.to_numpy())
    day = sub.entry_t.to_numpy() // DAY
    for nm, _, _ in EXITS:
        x = res[nm]
        rec = dict(cell="%dh<=%d%s %s" % (tf, T, " d<30" if gate else "", nm), tf=tf, T=T, gate="daily<30" if gate else "none", exit=nm)
        for si, sn in ((0, "DEV"), (1, "VAL")):
            m = sp == si
            v = x[m]
            mean, lo, hi, p = H.week_boot(v, wk[m], rng) if len(v) else (np.nan,) * 4
            rec.update({sn + "_n": int(len(v)), sn + "_mean": mean, sn + "_lo": lo, sn + "_hi": hi, sn + "_p": p,
                        sn + "_median": float(np.median(v)) if len(v) else np.nan, sn + "_win": float((v > 0).mean()) if len(v) else np.nan})
            pm = np.array([np.nanmean(pl[nm][m]) if (m.any() and np.isfinite(pl[nm][m]).any()) else np.nan for pl in plac])
            pm = pm[~np.isnan(pm)]
            rec[sn + "_plac_mean"] = float(pm.mean()) if len(pm) else np.nan
            rec[sn + "_plac_p"] = float((np.sum(pm >= mean) + 1) / (len(pm) + 1)) if len(pm) and len(v) else np.nan
            if len(v):
                dd = pd.Series(v).groupby(day[m]).mean()
                dm, dlo, dhi, _ = H.week_boot(dd.to_numpy(), np.arange(len(dd)), rng)
                rec.update({sn + "_days": int(len(dd)), sn + "_daymean": dm, sn + "_daylo": dlo, sn + "_dayhi": dhi})
            else:
                rec.update({sn + "_days": 0, sn + "_daymean": np.nan, sn + "_daylo": np.nan, sn + "_dayhi": np.nan})
        rows.append(rec)
    return rows


def main():
    t0 = time.time()
    coins, missing = {}, []
    for c in COINS:
        try:
            coins[c] = Coin(c)
        except Exception:
            missing.append(c)
    print("loaded", {c: coins[c].n for c in coins}, "missing", missing, flush=True)
    ev = build(coins)
    ev.to_csv(os.path.join(CACHE, "events.csv"), index=False)
    print("events", len(ev), flush=True)
    cell_rows, band_rows = [], []
    for (tf, T) in COMBOS:
        sub = ev[(ev.tf == tf) & (ev["T"] == T)].sort_values(["coin", "entry_t"]).reset_index(drop=True)
        if sub.empty:
            continue
        res = {nm: np.full(len(sub), np.nan) for nm, _, _ in EXITS}
        for c, g in sub.groupby("coin"):
            r = trade_rs(coins[c], g.e0.to_numpy(int), g.entry.to_numpy(), g.stop.to_numpy(), tf)
            for nm in r:
                res[nm][g.index.to_numpy()] = r[nm]
        plac = [placebo(coins, sub, tf) for _ in range(K_PLAC)]
        cell_rows += run_cell(tf, T, sub, res, plac, False)
        dr = sub.drsi.to_numpy()
        band = np.where(np.isnan(dr), "nan", np.where(dr < 30, "<30", np.where(dr <= 40, "30-40", ">40")))
        sp = split_of(sub.entry_t.to_numpy())
        for nm, _, _ in EXITS:
            for b in ("<30", "30-40", ">40"):
                for si, sn in ((0, "DEV"), (1, "VAL")):
                    m = (band == b) & (sp == si)
                    band_rows.append(dict(tf=tf, T=T, exit=nm, band=b, split=sn, n=int(m.sum()), mean=float(res[nm][m].mean()) if m.any() else np.nan))
        if (tf, T) == (4, 12):
            m = sub.drsi.to_numpy() < 30
            g = sub[m].reset_index(drop=True)
            resg = {nm: res[nm][m] for nm in res}
            plg = [placebo(coins, g, tf) for _ in range(K_PLAC)]
            cell_rows += run_cell(tf, T, g, resg, plg, True)
            g.assign(**{k: v for k, v in resg.items()}).to_csv(os.path.join(HERE, "trades_4h12_daily_lt30.csv"), index=False)
        print("combo", tf, T, len(sub), "t=%.0fs" % (time.time() - t0), flush=True)
    cells = pd.DataFrame(cell_rows)
    cells["bh_sig"] = H.bh(cells.VAL_p.fillna(1.0).to_numpy())
    ok = (cells.VAL_n >= 30) & (cells.VAL_mean > 0) & (cells.VAL_lo > 0) & (cells.VAL_plac_p <= 0.05) & cells.bh_sig
    cells["verdict"] = np.where(ok, "PASS", np.where(cells.VAL_n < 30, "UNDERPOWERED", "FAIL"))
    cells.round(5).to_csv(os.path.join(HERE, "cells.csv"), index=False)
    pd.DataFrame(band_rows).round(5).to_csv(os.path.join(HERE, "bands.csv"), index=False)
    json.dump(dict(missing=missing, coins=list(coins), n_events=int(len(ev)), n_cells=int(len(cells))), open(os.path.join(HERE, "meta.json"), "w"))
    print(cells.verdict.value_counts().to_dict(), "done %.0fs" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
