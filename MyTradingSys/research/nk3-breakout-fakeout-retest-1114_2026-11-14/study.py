"""Run the pre-registered study (PRE_REG.md). Writes results.json. Usage: python study.py"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib

CACHE = r"F:\MTS\data_cache\binance_spot"
COINS = "BTC ETH BNB XRP ADA SOL DOGE LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
SPLIT = int(np.datetime64("2024-01-01").astype("datetime64[ms]").astype(np.int64))
HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(20261114)
NDRAW, NBOOT = 300, 10000


def load(coin):
    z = np.load(os.path.join(CACHE, f"{coin}USDT_15m.npz"))
    return [z["ts" if "ts" in z.files else "t"]] + [z[k] for k in "o h l c v".split()]


def build(tfk):
    """global arrays per tf; also per-symbol signals."""
    parts, sigs, sym_ranges = [], [], []
    off = 0
    info = {}
    for ci, coin in enumerate(COINS):
        t, o, h, l, c, v = load(coin)
        days, lab = lib.daily_phase_table(t, o, h, l, c, v)
        if tfk != 1:
            t, o, h, l, c, v = lib.resample(t, o, h, l, c, v, tfk)
        ph = lib.phase_for_bars(t, days, lab)
        F = lib.features(t, o, h, l, c)
        S = lib.signals(t, o, h, l, c, F, ph)
        for s in S:
            s["i"] += off; s["e"] += off; s["sym"] = ci
        sigs += S
        parts.append((t, o, h, l, c, ph, np.full(len(t), ci)))
        sym_ranges.append((off, off + len(t)))
        off += len(t)
        info[coin] = dict(F=F, n=len(t))
    G = {k: np.concatenate([p[j] for p in parts]) for j, k in enumerate("t o h l c ph sym".split())}
    return G, sigs, sym_ranges, info


def simall(G, sigs, mode):
    idx = np.array([s["e"] for s in sigs]); px = np.array([s["px"] for s in sigs]); d = np.array([s["dir"] for s in sigs])
    dist = lib.stop_dist(np.array([s["nat"] for s in sigs]), np.array([s["atr"] for s in sigs]), px)
    chk = np.array([s["chk"] for s in sigs])
    g, ex = lib.sim(G["o"], G["h"], G["l"], G["c"], idx, px, d, dist, mode, chk)
    return dict(g=g, ex=ex, dist=dist, px=px, idx=idx, d=d)


def pick(sigs, sim, typ, fit, blast):
    """indices of signals for a row, with one-position-per-coin cooldown."""
    sel = [k for k, s in enumerate(sigs) if s["type"] == typ and s["fit"] == fit and (s["blast"] or not blast)]
    sel.sort(key=lambda k: (sigs[k]["sym"], sigs[k]["e"]))
    keep, last, cs = [], -1, -1
    for k in sel:
        s = sigs[k]
        if s["sym"] != cs:
            cs, last = s["sym"], -1
        if s["e"] > last:
            keep.append(k)
            last = sim["ex"][k]
    return np.array(keep, dtype=int)


def boot_trade(R):
    n = len(R)
    if n == 0:
        return np.nan
    ms = []
    chunk = max(1, int(2e7 // n))
    done = 0
    while done < NBOOT:
        b = min(chunk, NBOOT - done)
        ms.append(R[rng.integers(0, n, (b, n))].mean(axis=1))
        done += b
    return float(np.percentile(np.concatenate(ms), 2.5))


def boot_day(R, day):
    u, inv = np.unique(day, return_inverse=True)
    sR = np.bincount(inv, weights=R)
    nn = np.bincount(inv).astype(float)
    D = len(u)
    ms = []
    for _ in range(10):
        ix = rng.integers(0, D, (NBOOT // 10, D))
        ms.append(sR[ix].sum(axis=1) / nn[ix].sum(axis=1))
    ms = np.concatenate(ms)
    return float(np.percentile(ms, 2.5)), float((ms <= 0).mean())


def ex_best5(R, day):
    u, inv = np.unique(day, return_inverse=True)
    sR = np.bincount(inv, weights=R)
    worst = np.argsort(-sR)[:5]
    m = ~np.isin(inv, worst)
    return float(R[m].mean()) if m.any() else np.nan


def stats(Rn, dist_frac_fee, tt, wins):
    return dict(n=len(Rn), win=float((Rn > 0).mean() * 100) if len(Rn) else np.nan, mean=float(Rn.mean()) if len(Rn) else np.nan)


def bh(ps, q=0.05):
    m = len(ps)
    order = np.argsort(ps)
    thr = -1
    for rank, k in enumerate(order, 1):
        if ps[k] <= q * rank / m:
            thr = rank
    ok = np.zeros(m, bool)
    for rank, k in enumerate(order, 1):
        if rank <= thr:
            ok[k] = True
    return ok


def main():
    t0 = time.time()
    res = dict(rows=[], mix={}, btc={})
    for tfk, tfn in ((1, "15m"), (4, "1h")):
        G, sigs, rngs, info = build(tfk)
        print(tfn, "signals", len(sigs), f"{time.time()-t0:.0f}s", flush=True)
        # regime mix on this tf bars (valid warm bars only)
        for nm, m in (("DEV", G["t"] < SPLIT), ("VAL", G["t"] >= SPLIT)):
            tot = m.sum()
            res["mix"][f"{tfn}_{nm}"] = {p: float(((G["ph"] == v) & m).sum() / tot) for p, v in (("UP", 1), ("DOWN", -1), ("RANGE", 0))}
        # placebo pools: (sym, phase) -> VAL bars
        valid = np.ones(len(G["t"]), bool)
        for (a, b) in rngs:
            valid[a:a + 150] = False
            valid[b - 70:b] = False
        pools = {}
        for ci in range(len(COINS)):
            for p in (-1, 0, 1):
                pools[(ci, p)] = np.flatnonzero(valid & (G["sym"] == ci) & (G["ph"] == p) & (G["t"] >= SPLIT))
        for mode in ("X1", "X2"):
            sm = simall(G, sigs, mode)
            for typ in ("A", "B"):
                for blast in (False, True):
                    for fit in (1, 0):
                        keep = pick(sigs, sm, typ, fit, blast)
                        for cost in (12, 6):
                            kk = keep
                            px = sm["px"][kk]; dist = sm["dist"][kk]
                            Rn = sm["g"][kk] - cost / 1e4 * px / dist
                            tt = G["t"][sm["idx"][kk]]
                            val = tt >= SPLIT
                            row = dict(tf=tfn, type=typ, mode=mode, blast=blast, fit=fit, cost=cost,
                                       dev_n=int((~val).sum()), dev_mean=float(Rn[~val].mean()) if (~val).any() else None,
                                       n=int(val.sum()), win=float((Rn[val] > 0).mean() * 100) if val.any() else None,
                                       mean=float(Rn[val].mean()) if val.any() else None,
                                       fee_R=float((cost / 1e4 * px[val] / dist[val]).mean()) if val.any() else None,
                                       phase_n={p: int(((np.array([sigs[k]["ph"] for k in kk]) == v) & val).sum()) for p, v in (("UP", 1), ("DOWN", -1), ("RANGE", 0))})
                            if val.sum() >= 20 and cost == 12 and fit == 1 or (val.sum() >= 20 and fit == 1 and cost == 12):
                                R = Rn[val]; day = tt[val] // lib.DAY
                                row["ci_trade"] = boot_trade(R)
                                row["ci_day"], row["p_day"] = boot_day(R, day)
                                row["ex5"] = ex_best5(R, day)
                                # placebo
                                ks = kk[val]
                                key = [(sigs[k]["sym"], sigs[k]["ph"]) for k in ks]
                                pl = [pools[x] for x in key]
                                d = sm["d"][ks]
                                distpct = dist[val] / px[val]
                                means = []
                                if all(len(p) for p in pl):
                                    for _ in range(NDRAW):
                                        ix = np.array([p[rng.integers(0, len(p))] for p in pl]) if len(ks) < 400 else np.concatenate(
                                            [p[rng.integers(0, len(p), 1)] for p in pl])
                                        ppx = G["c"][ix]
                                        pdist = distpct * ppx
                                        g, _ = lib.sim(G["o"], G["h"], G["l"], G["c"], ix, ppx, d, pdist, mode, np.zeros(len(ix), bool))
                                        means.append((g - cost / 1e4 * ppx / pdist).mean())
                                    means = np.array(means)
                                    row["placebo_mean"] = float(means.mean())
                                    row["placebo_p"] = float((means >= R.mean()).mean())
                            res["rows"].append(row)
                            if cost == 12:
                                print(tfn, mode, typ, "blast" if blast else "all", "fit" if fit else "ctl", row["n"], row["mean"], flush=True)
        if tfk == 4:
            res["btc"] = btc_today(G, info, rngs)
    # BH over the 16-row family
    fam = [r for r in res["rows"] if r["fit"] == 1 and r["cost"] == 12]
    ps = np.array([r.get("p_day", 1.0) if r.get("p_day") is not None else 1.0 for r in fam])
    ok = bh(ps)
    for r, o in zip(fam, ok):
        r["bh"] = bool(o)
        r["pass"] = bool(r["n"] >= 100 and r["mean"] and r["mean"] > 0 and r.get("ci_trade", -1) > 0 and r.get("ci_day", -1) > 0
                         and r.get("placebo_p", 1) < 0.05 and o and r.get("ex5", -1) > 0)
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    print("done", f"{time.time()-t0:.0f}s")


def btc_today(G, info, rngs):
    a, b = rngs[0]
    t, o, h, l, c, ph = (G[k][a:b] for k in ("t o h l c ph".split()))
    F = info["BTC"]["F"]
    i = len(c) - 1
    H, L = np.max(h[i - 19:i + 1]), np.min(l[i - 19:i + 1])
    return dict(last_bar_utc=str(np.datetime64(int(t[i]), "ms")), close=float(c[i]), phase_today=int(ph[i]), box_H20=float(H),
                box_L20=float(L), width_atr=float((H - L) / (F["atr_prev"][i] if not np.isnan(F["atr_prev"][i]) else np.nan)),
                prev_box_H=float(F["H"][i]), prev_box_L=float(F["L"][i]), last3_close=[float(x) for x in c[-3:]])


if __name__ == "__main__":
    main()
