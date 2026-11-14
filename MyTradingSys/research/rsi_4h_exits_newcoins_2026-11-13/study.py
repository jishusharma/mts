"""Confirmation of time8 and confstop_2R (S3 = 4h RSI<=20 + confirm) on 40 new coins (PRE_REG.md). Run: python fetch.py; python study.py"""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "backtest")))
import fees  # noqa: E402
import rsi_grid_lib as L  # noqa: E402
import exits_lib as X  # noqa: E402
import fetch  # noqa: E402

CACHE, COINS = fetch.OUT, fetch.COINS
TF, THR = 4, 20
CELLS = ["time8", "confstop_2R"]
COST = X.costs(fees.BINANCE_TAKER, fees.SLIPPAGE_RT_S13)
HOUR, DAY = L.HOUR, L.DAY
Y2024 = 1704067200000
NOW = int(time.time() * 1000)
B, K_PLAC = 2000, 200
rng = np.random.default_rng(20261113)


def week_of(t):
    return (np.asarray(t, np.int64) // DAY + 3) // 7


def boot(vals, wk, nb=B):
    """block bootstrap of the mean (wk = block id per value); wk=None -> plain resample."""
    if wk is None:
        wk = np.arange(len(vals))
    uw, inv = np.unique(wk, return_inverse=True)
    S = np.bincount(inv, weights=vals)
    N = np.bincount(inv).astype(float)
    ix = rng.integers(0, len(uw), (nb, len(uw)))
    m = S[ix].sum(1) / N[ix].sum(1)
    return float(vals.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((np.sum(m <= 0) + 1) / (nb + 1))


def load():
    cs, off = [], 0
    for name in COINS:
        a = np.array(json.load(open(os.path.join(CACHE, name + "_60.json"))))
        if len(a) < 500:
            continue
        a = a[a[:, 0] + HOUR <= NOW]
        t = a[:, 0].astype(np.int64)
        o, h, l, c, v = (a[:, i].copy() for i in range(1, 6))
        cs.append(dict(name=name, t=t, o=o, h=h, l=l, c=c, v=v, off=off, n=len(t), pos={int(x): i for i, x in enumerate(t)}))
        off += len(t)
    G = {k: np.concatenate([c[k] for c in cs]) for k in ("o", "h", "l", "c")}
    G["rsi"] = np.full(len(G["c"]), np.nan)  # RSI/SMA exits are not used by the two cells
    G["sma"] = np.full(len(G["c"]), np.nan)
    return cs, G


def build_set(cs):
    rows = []
    for ci, co in enumerate(cs):
        f = L.fold(co["t"], co["o"], co["h"], co["l"], co["c"], co["v"], TF)
        rsi = L.wilder_rsi(f["c"])
        for s in L.episodes(rsi, THR):
            s = int(s)
            info = L.confirm_info(f["t"], f["o"], f["h"], f["l"], f["c"], s, TF)
            if info is None or not info["confirm"]:
                continue
            e0 = co["pos"].get(info["entry_close_t"] - HOUR)
            if e0 is None or e0 + L.WIN >= co["n"] or co["t"][e0 + L.WIN] - co["t"][e0] != L.WIN * HOUR:
                continue
            rows.append((ci, co["off"] + e0, info["entry"], info["stop"], float(f["l"][s + 1]), info["entry_close_t"]))
    a = np.array(rows, dtype=float)
    return dict(ci=a[:, 0].astype(int), g0=a[:, 1].astype(int), entry=a[:, 2], stop=a[:, 3], cstop=a[:, 4], t=a[:, 5].astype(np.int64))


def placebo_ids(cs):
    ids = []
    for co in cs:
        i = np.arange(20, co["n"] - L.WIN - 1)
        ids.append(i[((co["t"][i] + HOUR) % (TF * HOUR)) == 0])
    return ids


def placebo_draw(cs, G, ids_by_coin, S, sd):
    n = len(S["g0"])
    g0 = np.zeros(n, int)
    ok = np.zeros(n, bool)
    for ci, co in enumerate(cs):
        m = S["ci"] == ci
        if not m.any():
            continue
        ids = ids_by_coin[ci]
        wk = week_of(co["t"][ids])
        o = np.argsort(wk, kind="stable")
        ids, wk = ids[o], wk[o]
        wt = week_of(S["t"][m])
        lo, hi = np.searchsorted(wk, wt, "left"), np.searchsorted(wk, wt, "right")
        ln = hi - lo
        pick = lo + np.floor(rng.random(m.sum()) * np.maximum(ln, 1)).astype(int)
        e = ids[np.minimum(pick, max(len(ids) - 1, 0))]
        g0[m] = co["off"] + e
        ok[m] = ln > 0
    entry = G["c"][g0]
    return g0, entry, entry * (1 - sd), ok


def year_of(t):
    return (np.asarray(t, np.int64) // 1000 // 31556952 + 1970).astype(int)


def main():
    cs, G = load()
    S = build_set(cs)
    res = dict(coins={c["name"]: c["n"] for c in cs}, cost=COST, n=int(len(S["g0"])), cells={})
    ids = placebo_ids(cs)
    day = S["t"] // DAY
    for name in CELLS:
        rule = dict(X.RULES)[name]
        stop = S["cstop"] if rule.get("conf") else S["stop"]
        sd = (S["entry"] - stop) / S["entry"]
        gp = X.fwd_sim(rule, G, S["g0"], S["entry"], stop)
        R = (gp - COST) / sd
        r = dict(n=int(len(R)), win=float((R > 0).mean()), mean=float(R.mean()), median=float(np.median(R)), gross=float((gp / sd).mean()),
                 coins_with_trades=int(len(np.unique(S["ci"]))))
        _, r["lo"], r["hi"], r["p"] = boot(R, week_of(S["t"]))
        ud, inv = np.unique(day, return_inverse=True)
        dsum = np.bincount(inv, weights=R)
        dm = dsum / np.bincount(inv)
        r["n_days"] = int(len(ud))
        _, r["day_lo_plain"], r["day_hi_plain"], _ = boot(dm, None)
        _, r["day_lo_wk"], r["day_hi_wk"], _ = boot(dm, week_of(ud * DAY))
        r["day_mean"] = float(dm.mean())
        top = np.argsort(-dsum)[:5]
        keep = ~np.isin(inv, top)
        r["top5_days"] = [int(ud[i]) * DAY for i in top]
        r["top5_share"] = float(dsum[top].sum() / R.sum()) if R.sum() != 0 else float("nan")
        r["mean_wo_top5"] = float(R[keep].mean())
        r["n_wo_top5"] = int(keep.sum())
        _, r["lo_wo_top5"], r["hi_wo_top5"], _ = boot(R[keep], week_of(S["t"][keep]))
        m24 = S["t"] >= Y2024
        r["n_2024"] = int(m24.sum())
        r["mean_2024"] = float(R[m24].mean()) if m24.any() else None
        if m24.any():
            _, r["lo_2024"], r["hi_2024"], _ = boot(R[m24], week_of(S["t"][m24]))
        yr = year_of(S["t"])
        r["per_year"] = {int(y): [int((yr == y).sum()), float(R[yr == y].mean())] for y in np.unique(yr)}
        means = []
        for _ in range(K_PLAC):
            g0p, enp, stp, ok = placebo_draw(cs, G, ids, S, sd)
            gpp = X.fwd_sim(rule, G, g0p, enp, stp)
            v = ((gpp - COST) / ((enp - stp) / enp))[ok]
            means.append(float(v.mean()))
        means = np.array(means)
        r["placebo_mean"] = float(means.mean())
        r["placebo_p"] = float((np.sum(means >= r["mean"]) + 1) / (K_PLAC + 1))
        ok_ = (r["mean"] > 0 and r["lo"] > 0 and r["day_lo_plain"] > 0 and r["day_lo_wk"] > 0 and r["placebo_p"] <= 0.025 and r["p"] <= 0.025)
        if r["n"] < 100:
            r["verdict"] = "UNDERPOWERED"
        elif ok_:
            r["verdict"] = "PASS" + (" (FRAGILE)" if r["mean_wo_top5"] <= 0 else "")
        else:
            r["verdict"] = "FAIL"
        res["cells"][name] = r
        print(name, {k: v for k, v in r.items() if k not in ("per_year", "top5_days")}, flush=True)
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
