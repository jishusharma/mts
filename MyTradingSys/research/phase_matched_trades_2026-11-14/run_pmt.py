"""Run the pre-registered study (PRE_REG.md). Output: runtime_data/edge9-phase-matched-1114/{trades.npz,summary.json}, prints tables."""
import sys, os, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "backtest"))
import numpy as np
from math import erfc, sqrt
import engine as E
import research_kit as RK

DATA = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge9-phase-matched-1114"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX", "DOT", "TRX", "BCH", "ATOM", "NEAR", "UNI", "APT", "ARB", "OP", "SUI"]
VAL_START = 1704067200000   # 2024-01-01 UTC
SPEC = {"T1": [("2R", "R", 2.0), ("1R", "R", 1.0), ("PD", "P", None)], "T2": [("2R", "R", 2.0), ("1R", "R", 1.0), ("PD", "P", None)],
        "T3": [("mid", "P", None)], "T4": [("2R", "R", 2.0)]}
MAXB = {"T1": 24, "T2": 24, "T3": 72, "T4": 24}
PRIMARY = {"T1": "2R", "T2": "2R", "T3": "mid", "T4": "2R"}
MATCH = {"T1": E.DOWN, "T2": E.UP, "T3": E.RANGE, "T4": E.DOWN}
RNG = np.random.RandomState(20261114)


def load(coin, now_ms):
    def rd(name):
        return np.array(json.load(open(os.path.join(DATA, "%s_%s.json" % (coin, name)))), float)
    h1, d = rd("60"), rd("D")
    h1 = h1[h1[:, 0] + E.H1 <= now_ms]
    d = d[d[:, 0] + E.DAY <= now_ms]
    f = rd("fund")
    return h1, d, f


def run_coin(coin, now_ms):
    h1, d, f = load(coin, now_ms)
    t = h1[:, 0].astype(np.int64)
    o, h, l, c = h1[:, 1], h1[:, 2], h1[:, 3], h1[:, 4]
    dt = d[:, 0].astype(np.int64)
    lab = E.daily_phase(d[:, 2], d[:, 3], d[:, 4])
    bph = E.bar_phase(t, dt, lab, 1)
    sig = E.signals(t, o, h, l, c, dt, d[:, 2], d[:, 3], 1)
    ft = f[:, 0].astype(np.int64) if len(f) else np.zeros(0, np.int64)
    cf = np.concatenate(([0.0], np.cumsum(f[:, 1]))) if len(f) else np.zeros(1)
    rows = []
    for ty, sl in sig.items():
        for ph in (E.UP, E.DOWN, E.RANGE):
            cand = [x for x in sl if bph[x[0]] == ph]
            for vname, kind, val in SPEC[ty]:
                busy = -1
                for (s, side, stop, aux) in cand:
                    if s + 1 <= busy:
                        continue
                    tv = val if kind == "R" else aux
                    r = E.simulate(o, h, l, c, s, side, stop, kind, tv, MAXB[ty])
                    if r is None:
                        continue
                    j, xp, entry = r
                    busy = j
                    fund = E.funding_between(ft, cf, t[s + 1], t[j] + E.H1)
                    pct, R = E.net_r(side, entry, xp, stop, fund)
                    rows.append((ty, vname, ph, coin, side, int(t[s + 1]), j - (s + 1) + 1, pct, R))
    return rows, dict(t=t, o=o, c=c, bph=bph, ft=ft, cf=cf), (dt, lab, d)


def boot_ci(x, groups=None, nb=2000):
    x = np.asarray(x, float)
    n = len(x)
    if n < 2:
        return float("nan"), float("nan")
    if groups is None:
        idx = RNG.randint(0, n, size=(nb, n))
        m = x[idx].mean(axis=1)
    else:
        u, inv = np.unique(groups, return_inverse=True)
        s = np.bincount(inv, weights=x)
        k = np.bincount(inv).astype(float)
        idx = RNG.randint(0, len(u), size=(nb, len(u)))
        m = s[idx].sum(axis=1) / k[idx].sum(axis=1)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def one_sided_p(x, day):
    m, se = RK.cluster_mean_se(x, day)
    if not np.isfinite(se) or se == 0:
        return float("nan")
    return 0.5 * erfc((m / se) / sqrt(2))


def cell(rows):
    n = len(rows)
    if n == 0:
        return dict(n=0, mean=float("nan"), win=float("nan"))
    R = np.array([r[8] for r in rows])
    return dict(n=n, mean=float(R.mean()), win=float((R > 0).mean()))


def random_control(obs, data, ph, nrs=1000):
    """obs: list of trade rows of one coin-pooled cell (VALIDATION). Returns p = share random means >= observed mean (net pct)."""
    obs_pct = np.array([r[7] for r in obs])
    cache = {}
    sums = np.zeros(nrs)
    cnt = 0
    for r in obs:
        coin, side, hold = r[3], r[4], r[6]
        D = data[coin]
        if coin not in cache:
            ok = (D["bph"] == ph) & (D["t"] >= VAL_START)
            cache[coin] = np.where(ok)[0]
        cands = cache[coin]
        cands = cands[cands + hold < len(D["c"])]
        if len(cands) == 0:
            continue
        ci = cands[RNG.randint(0, len(cands), size=nrs)]
        entry = D["o"][ci]
        xp = D["c"][ci + hold - 1]
        a = np.searchsorted(D["ft"], D["t"][ci], side="right")
        b = np.searchsorted(D["ft"], D["t"][ci + hold - 1] + E.H1, side="right")
        fund = D["cf"][b] - D["cf"][a]
        sums += side * (xp / entry - 1) - E.COST - side * fund
        cnt += 1
    if cnt == 0:
        return float("nan"), float("nan")
    rm = sums / cnt
    return float((rm >= obs_pct.mean()).mean()), float(rm.mean())


def fmt(v, p=3):
    return "nan" if v is None or (isinstance(v, float) and np.isnan(v)) else ("%." + str(p) + "f") % v


def main():
    now_ms = int(time.time() * 1000)
    allrows, data, phases = [], {}, {}
    for c in COINS:
        rows, dd, ph = run_coin(c, now_ms)
        allrows += rows
        data[c] = dd
        phases[c] = ph
        print(c, len(rows), flush=True)
    # regime mix
    mix = {}
    tot = {k: 0 for k in (E.UP, E.DOWN, E.RANGE)}
    totv = dict(tot)
    for c, (dt, lab, d) in phases.items():
        # label applies to the following day; count days (label days) by split of the day it applies to
        cnt = {k: int((lab == k).sum()) for k in tot}
        v = {k: int(((lab == k) & (dt + E.DAY >= VAL_START)).sum()) for k in tot}
        mix[c] = cnt
        for k in tot:
            tot[k] += cnt[k]
            totv[k] += v[k]
    sm = sum(tot.values()); sv = sum(totv.values())
    btc = mix["BTC"]; sb = sum(btc.values())
    dt, lab, d = phases["BTC"]
    adx, pdi, mdi = E.adx_di(d[:, 2], d[:, 3], d[:, 4])
    ma20 = d[-20:, 4].mean()
    today = dict(last_closed_day=time.strftime("%Y-%m-%d", time.gmtime(dt[-1] / 1000)), close=float(d[-1, 4]), ma20=float(ma20),
                 ma20_5ago=float(d[-25:-5, 4].mean()), adx=float(adx[-1]), pdi=float(pdi[-1]), mdi=float(mdi[-1]), phase=E.PH.get(int(lab[-1]), "NONE"))
    # last 10 BTC labels
    recent = [E.PH.get(int(x), "-") for x in lab[-10:]]
    out = []
    P = out.append
    P("Regime mix: pooled %d coin-days: UP %.1f%% DOWN %.1f%% RANGE %.1f%%; VALIDATION days: UP %.1f%% DOWN %.1f%% RANGE %.1f%%; BTC all: UP %.1f%% DOWN %.1f%% RANGE %.1f%%" % (
        sm, 100 * tot[E.UP] / sm, 100 * tot[E.DOWN] / sm, 100 * tot[E.RANGE] / sm, 100 * totv[E.UP] / sv, 100 * totv[E.DOWN] / sv, 100 * totv[E.RANGE] / sv,
        100 * btc[E.UP] / sb, 100 * btc[E.DOWN] / sb, 100 * btc[E.RANGE] / sb))
    P("BTC today: %s" % json.dumps(today))
    P("BTC last 10 daily labels: %s" % recent)
    # split
    def sel(ty, var, ph, split, coin=None):
        return [r for r in allrows if r[0] == ty and r[1] == var and r[2] == ph and (coin is None or r[3] == coin) and ((r[5] >= VAL_START) == (split == "VAL"))]
    summary = {"regime_mix": out[0], "btc_today": today, "cells": {}, "gates": {}}
    for var_kind in ("primary", "1R", "PD"):
        P("")
        P("MATRIX VALIDATION mean net R (n, win%%) -- exit: %s" % var_kind)
        P("type | exit | UP | DOWN | RANGE")
        for ty in ("T1", "T2", "T3", "T4"):
            var = PRIMARY[ty] if var_kind == "primary" else var_kind
            if var not in [v[0] for v in SPEC[ty]]:
                continue
            cells = []
            for ph in (E.UP, E.DOWN, E.RANGE):
                cv, cd = cell(sel(ty, var, ph, "VAL")), cell(sel(ty, var, ph, "DEV"))
                mark = "*" if MATCH[ty] == ph and var_kind == "primary" else ""
                cells.append("%s%s (n=%d, %s%%) [DEV %s n=%d]" % (fmt(cv["mean"]), mark, cv["n"], fmt(100 * cv["win"], 1), fmt(cd["mean"]), cd["n"]))
                summary["cells"]["%s|%s|%s" % (ty, var, E.PH[ph])] = dict(val=cv, dev=cd)
            P("%s | %s | %s" % (ty, var, " | ".join(cells)))
    P("(* = matched cell)")
    # BTC alone primary
    P("")
    P("BTC ALONE VALIDATION mean net R primary exit (n)")
    for ty in ("T1", "T2", "T3", "T4"):
        cs = []
        for ph in (E.UP, E.DOWN, E.RANGE):
            cv = cell(sel(ty, PRIMARY[ty], ph, "VAL", "BTC"))
            cs.append("%s (n=%d)" % (fmt(cv["mean"]), cv["n"]))
        P("%s | %s" % (ty, " | ".join(cs)))
    # gates
    P("")
    P("GATES matched rows (VALIDATION, primary exit)")
    P("row | n | win% | meanR | CI trade | CI day | random p | cluster p | BH | ex-best-5 | matched-minus-best-mismatch (diff, se)")
    pv = {}
    rowsinfo = {}
    for ty in ("T1", "T2", "T3", "T4"):
        ph = MATCH[ty]
        v = sel(ty, PRIMARY[ty], ph, "VAL")
        R = np.array([r[8] for r in v]); day = np.array([r[5] // E.DAY for r in v])
        n = len(v)
        info = dict(n=n)
        if n >= 2:
            info["mean"] = float(R.mean()); info["win"] = float((R > 0).mean())
            info["ci_trade"] = boot_ci(R); info["ci_day"] = boot_ci(R, day)
            info["p"] = one_sided_p(R, day)
            info["rand_p"], info["rand_mean_pct"] = random_control(v, data, ph)
            info["obs_mean_pct"] = float(np.mean([r[7] for r in v]))
            u, inv = np.unique(day, return_inverse=True)
            ds = np.bincount(inv, weights=R)
            drop = set(u[np.argsort(-ds)[:5]])
            rest = R[~np.isin(day, list(drop))]
            info["ex5"] = float(rest.mean()) if len(rest) else float("nan")
            # best mismatched
            best = None
            for ph2 in (E.UP, E.DOWN, E.RANGE):
                if ph2 == ph:
                    continue
                w = sel(ty, PRIMARY[ty], ph2, "VAL")
                if len(w) >= 2:
                    mm = np.mean([r[8] for r in w])
                    if best is None or mm > best[0]:
                        best = (mm, ph2, w)
            if best:
                dif, se = RK.cluster_diff(R, day, [r[8] for r in best[2]], [r[5] // E.DAY for r in best[2]])
                info["diff_best_mismatch"] = (float(dif), float(se), E.PH[best[1]], float(best[0]))
            pv[ty] = info["p"]
        rowsinfo[ty] = info
    # BH 10% over the 4 matched rows (p nan -> 1)
    keys = list(rowsinfo)
    ps = np.array([rowsinfo[k].get("p", 1.0) if np.isfinite(rowsinfo[k].get("p", 1.0)) else 1.0 for k in keys])
    order = np.argsort(ps)
    bh = {k: False for k in keys}
    kmax = -1
    for rank, ix in enumerate(order, 1):
        if ps[ix] <= 0.10 * rank / len(keys):
            kmax = rank
    for rank, ix in enumerate(order, 1):
        if rank <= kmax:
            bh[keys[ix]] = True
    for ty in keys:
        i = rowsinfo[ty]
        if i["n"] < 2:
            P("%s/%s | n=%d | no trades" % (ty, E.PH[MATCH[ty]], i["n"]))
            continue
        g = dict(n=i["n"] >= 100, ci_trade=i["ci_trade"][0] > 0 and i["mean"] > 0, ci_day=i["ci_day"][0] > 0, rand=i["rand_p"] < 0.05, bh=bh[ty], ex5=i["ex5"] > 0)
        i["gates"] = g
        i["pass"] = all(g.values())
        db = i.get("diff_best_mismatch")
        P("%s/%s | %d | %s | %s | [%s, %s] | [%s, %s] | %s (obs %s%% vs rand %s%%) | %s | %s | %s | %s" % (
            ty, E.PH[MATCH[ty]], i["n"], fmt(100 * i["win"], 1), fmt(i["mean"]), fmt(i["ci_trade"][0]), fmt(i["ci_trade"][1]), fmt(i["ci_day"][0]), fmt(i["ci_day"][1]),
            fmt(i["rand_p"]), fmt(100 * i["obs_mean_pct"], 3), fmt(100 * i["rand_mean_pct"], 3), fmt(i["p"], 4), "Y" if bh[ty] else "N", fmt(i["ex5"]),
            ("%s vs %s %s: %s (se %s)" % (E.PH[MATCH[ty]], db[2], fmt(db[3]), fmt(db[0]), fmt(db[1]))) if db else "-"))
        P("   gates: %s -> %s%s" % (g, "PASS" if i["pass"] else "FAIL", "" if g["n"] else " (UNDERPOWERED)"))
    summary["gates"] = {k: {kk: (list(vv) if isinstance(vv, tuple) else vv) for kk, vv in v.items()} for k, v in rowsinfo.items()}
    npass = sum(1 for v in rowsinfo.values() if v.get("pass"))
    allpow = all(v["n"] >= 100 for v in rowsinfo.values())
    verdict = "PASS" if npass else ("FAIL" if allpow else "UNDERPOWERED/FAIL")
    P("")
    P("VERDICT: %s (%d of 4 matched rows pass)" % (verdict, npass))
    P("Trades total: %d; coins: %d; data end: %s" % (len(allrows), len(COINS), time.strftime("%Y-%m-%d %H:%M", time.gmtime(max(int(data[c]["t"][-1]) for c in COINS) / 1000))))
    txt = "\n".join(out)
    print(txt)
    open(os.path.join(DATA, "result_tables.txt"), "w").write(txt)
    json.dump(summary, open(os.path.join(DATA, "summary.json"), "w"), default=lambda x: None if x != x else str(x))
    np.save(os.path.join(DATA, "trades.npy"), np.array(allrows, dtype=object), allow_pickle=True)


if __name__ == "__main__":
    main()
