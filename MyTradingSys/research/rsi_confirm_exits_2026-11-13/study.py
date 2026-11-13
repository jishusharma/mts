"""RSI-confirm exits study (PRE_REG.md). Run: python study.py  (reads runtime_data/edge4-rsi-confirm-exits-1113 klines from fetch.py)
Writes results.json, trades_S1.csv. Entry logic = edge3 lib (rsi_grid_lib), exit engine = exits_lib."""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "backtest")))
import fees  # noqa: E402
import rsi_grid_lib as L  # noqa: E402
import exits_lib as X  # noqa: E402

CACHE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge4-rsi-confirm-exits-1113"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX", "DOT", "TRX", "ATOM", "UNI", "FIL", "NEAR", "BCH", "ETC", "XLM", "AAVE"]
SETS = {"S1": (1, 20), "S2": (1, 15), "S3": (4, 20)}
TAKER = fees.BINANCE_TAKER
SLIP = fees.SLIPPAGE_RT_S13
COST = X.costs(TAKER, SLIP)
HOUR, DAY = L.HOUR, L.DAY
VAL_START = 1704067200000  # 2024-01-01 UTC
NOW = int(time.time() * 1000)
B, K_PLAC = 2000, 30
rng = np.random.default_rng(20261113)


def week_of(t):
    return (np.asarray(t, np.int64) // DAY + 3) // 7


def boot(vals, wk, nb=B):
    if len(vals) == 0:
        return (np.nan,) * 4
    uw, inv = np.unique(wk, return_inverse=True)
    S = np.bincount(inv, weights=vals)
    N = np.bincount(inv).astype(float)
    ix = rng.integers(0, len(uw), (nb, len(uw)))
    m = S[ix].sum(1) / N[ix].sum(1)
    return float(vals.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((np.sum(m <= 0) + 1) / (nb + 1))


def bh(p, q=0.10):
    p = np.asarray(p)
    m = len(p)
    o = np.argsort(p)
    passed = p[o] <= (np.arange(1, m + 1) / m) * q
    k = (np.max(np.where(passed)[0]) + 1) if passed.any() else 0
    sig = np.zeros(m, bool)
    sig[o[:k]] = True
    return sig


def load():
    cs, off = [], 0
    for name in COINS:
        a = np.array(json.load(open(os.path.join(CACHE, name + "_60.json"))))
        a = a[a[:, 0] + HOUR <= NOW]
        t = a[:, 0].astype(np.int64)
        o, h, l, c, v = (a[:, i].copy() for i in range(1, 6))
        cs.append(dict(name=name, t=t, o=o, h=h, l=l, c=c, v=v, rsi=L.wilder_rsi(c), sma=L.sma(c, 20), off=off, n=len(t),
                       pos={int(x): i for i, x in enumerate(t)}))
        off += len(t)
    G = {k: np.concatenate([c[k] for c in cs]) for k in ("o", "h", "l", "c", "rsi", "sma")}
    return cs, G


def build_set(cs, tf, T):
    rows = []
    for ci, co in enumerate(cs):
        f = L.fold(co["t"], co["o"], co["h"], co["l"], co["c"], co["v"], tf)
        rsi = L.wilder_rsi(f["c"])
        for s in L.episodes(rsi, T):
            s = int(s)
            info = L.confirm_info(f["t"], f["o"], f["h"], f["l"], f["c"], s, tf)
            if info is None or not info["confirm"]:
                continue
            e0 = co["pos"].get(info["entry_close_t"] - HOUR)
            if e0 is None or e0 + L.WIN >= co["n"] or co["t"][e0 + L.WIN] - co["t"][e0] != L.WIN * HOUR:
                continue
            rows.append((ci, co["off"] + e0, info["entry"], info["stop"], float(f["l"][s + 1]), info["entry_close_t"]))
    a = np.array(rows, dtype=float)
    return dict(ci=a[:, 0].astype(int), g0=a[:, 1].astype(int), entry=a[:, 2], stop=a[:, 3], cstop=a[:, 4], t=a[:, 5].astype(np.int64))


def part1(G, S):
    g0, entry, stop = S["g0"], S["entry"], S["stop"]
    risk = entry - stop
    idx = g0[:, None] + 1 + np.arange(72)[None, :]
    H, Lo = G["h"][idx], G["l"][idx]
    out = {"n": int(len(g0)), "mfe": {}, "mae": {}}
    for k in (1, 2, 4, 8, 12, 24, 48):
        out["mfe"][k] = float(np.median((H[:, :k].max(1) - entry) / risk))
        out["mae"][k] = float(np.median((entry - Lo[:, :k].min(1)) / risk))
    si = L.fwd_first(Lo <= stop[:, None])
    big = 10 ** 6
    si_ = np.where(si < 0, big, si)
    reach = {}
    for r in (0.5, 1.0, 2.0):
        ti = L.fwd_first(H >= (entry + r * risk)[:, None])
        ti = np.where(ti < 0, big, ti)
        reach[r] = ti
        out["reach%g" % r] = float(np.mean(ti < si_))
    out["half_then_stop"] = float(np.mean((reach[0.5] < si_) & (si_ < 72) & ~(reach[1.0] < si_)))
    out["stop_bar1"] = float(np.mean(si == 0))
    pk = []
    for q in range(len(g0)):
        e = si_[q] if si_[q] < big else 72
        if e > 0:
            pk.append(int(np.argmax(H[q, :e])) + 1)
    out["peak_bars_median"] = float(np.median(pk)) if pk else float("nan")
    out["stopped_72h"] = float(np.mean(si_ < 72))
    return out


def placebo_ids(cs, tf, kind):
    ids = []
    for co in cs:
        i = np.arange(20, co["n"] - L.WIN - 1)
        i = i[((co["t"][i] + HOUR) % (tf * HOUR)) == 0]
        if kind == "oversold":
            i = i[(co["c"][i] < co["sma"][i]) & (co["rsi"][i] <= 40)]
        ids.append(i)
    return ids


def placebo_draw(cs, G, ids_by_coin, S, mask, sd):
    """One placebo draw for trades in `mask`: random eligible bar of the same coin in the same ISO week. Returns g0, entry, stop, ok."""
    sel = np.flatnonzero(mask)
    n = len(sel)
    g0 = np.zeros(n, int)
    ok = np.zeros(n, bool)
    for ci, co in enumerate(cs):
        m = S["ci"][sel] == ci
        if not m.any():
            continue
        ids = ids_by_coin[ci]
        wk = week_of(co["t"][ids])
        o = np.argsort(wk, kind="stable")
        ids, wk = ids[o], wk[o]
        wt = week_of(S["t"][sel[m]])
        lo, hi = np.searchsorted(wk, wt, "left"), np.searchsorted(wk, wt, "right")
        ln = hi - lo
        pick = lo + np.floor(rng.random(m.sum()) * np.maximum(ln, 1)).astype(int)
        e = ids[np.minimum(pick, max(len(ids) - 1, 0))] if len(ids) else np.zeros(m.sum(), int)
        g0[m] = co["off"] + e
        ok[m] = ln > 0
    entry = G["c"][g0]
    return g0, entry, entry * (1 - sd[sel]), ok


def main():
    cs, G = load()
    res = {"coins": {c["name"]: c["n"] for c in cs}, "cost": COST, "taker": TAKER, "slip_rt": SLIP, "n_all": {}}
    p1, p2 = {}, {}
    t0 = time.time()
    for sname, (tf, T) in SETS.items():
        S = build_set(cs, tf, T)
        val = S["t"] >= VAL_START
        res["n_all"][sname] = [int(len(val)), int((~val).sum()), int(val.sum())]
        p1[sname] = part1(G, S)
        rows = []
        for name, rule in X.RULES:
            stop = S["cstop"] if rule.get("conf") else S["stop"]
            sd = (S["entry"] - stop) / S["entry"]
            gp = X.fwd_sim(rule, G, S["g0"], S["entry"], stop)
            gR, nR = gp / sd, (gp - COST) / sd
            row = dict(rule=name, n_dev=int((~val).sum()), n_val=int(val.sum()))
            for tag, m in (("val", val), ("dev", ~val)):
                row["gross_" + tag] = float(gR[m].mean()) if m.any() else float("nan")
                row["net_" + tag] = float(nR[m].mean()) if m.any() else float("nan")
            row["win_val"] = float((nR[val] > 0).mean())
            row["med_val"] = float(np.median(nR[val]))
            row["pct_net_val"] = float((gp[val] - COST).mean())
            _, lo, hi, p = boot(nR[val], week_of(S["t"][val] // DAY * DAY))
            row.update(ci_lo=lo, ci_hi=hi, p=p)
            ud, inv = np.unique(S["t"][val] // DAY, return_inverse=True)
            dm = np.bincount(inv, weights=nR[val]) / np.bincount(inv)
            _, dlo, dhi, _ = boot(dm, week_of(ud * DAY))
            row.update(n_days=int(len(ud)), day_mean=float(dm.mean()), day_lo=dlo, day_hi=dhi)
            kind = "oversold" if rule["kind"] in ("rsi", "ma_touch", "ma_close") else "any"
            ids = placebo_ids(cs, tf, kind)
            means = []
            for _ in range(K_PLAC):
                g0p, enp, stp, ok = placebo_draw(cs, G, ids, S, val, sd)
                gpp = X.fwd_sim(rule, G, g0p, enp, stp)
                v = ((gpp - COST) / ((enp - stp) / enp))[ok]
                means.append(float(v.mean()) if len(v) else np.nan)
            means = np.array(means)
            row["placebo_mean"] = float(np.nanmean(means))
            row["placebo_p"] = float((np.sum(means >= row["net_val"]) + 1) / (K_PLAC + 1))
            rows.append(row)
            print(sname, name, "n_val", row["n_val"], "net_val %.3f" % row["net_val"], "plac %.3f" % row["placebo_mean"], "%.0fs" % (time.time() - t0), flush=True)
        sig = bh([r["p"] for r in rows])
        for r, s_ in zip(rows, sig):
            r["bh"] = bool(s_)
            if r["n_val"] < 30:
                r["verdict"] = "UNDERPOWERED"
            elif r["net_val"] > 0 and r["ci_lo"] > 0 and r["day_lo"] > 0 and r["placebo_p"] <= 0.05 and r["bh"]:
                r["verdict"] = "PASS" + (" (ROBUST)" if r["net_dev"] > 0 else "")
            else:
                r["verdict"] = "FAIL"
        p2[sname] = rows
        if sname == "S1":
            np.savetxt(os.path.join(HERE, "trades_S1.csv"), np.c_[S["ci"], S["t"], S["entry"], S["stop"], S["cstop"]], delimiter=",",
                       fmt="%.10g", header="coin_idx,entry_close_ms,entry,stop,confirm_low")
    res["part1"], res["part2"] = p1, p2
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
