import os, sys, json, time
import numpy as np
import study as S

HERE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)
FAMS = [("LONG-P", 1, "P"), ("LONG-S1", 1, "S1"), ("SHORT-P", -1, "P"), ("SHORT-R1", -1, "R1")]
OKPH = {1: (1, 0), -1: (-1, 0)}      # matched phases per side
CTRL = {1: (-1,), -1: (1,)}          # control phases
TFS = {"15m": (1, 96), "1h": (4, 24)}


def boot_ci(x, B=10000):
    n = len(x)
    idx = rng.integers(0, n, (B, n)) if n * B <= 4e7 else None
    if idx is None:
        m = np.array([x[rng.integers(0, n, n)].mean() for _ in range(B)])
    else:
        m = x[idx].mean(1)
    return np.percentile(m, 2.5)


def cluster_ci(days, x, B=5000):
    u, inv = np.unique(days, return_inverse=True)
    s = np.bincount(inv, weights=x)
    c = np.bincount(inv).astype(float)
    k = len(u)
    ii = rng.integers(0, k, (B, k))
    m = s[ii].sum(1) / c[ii].sum(1)
    return np.percentile(m, 2.5)


def ex_best5(days, x):
    u, inv = np.unique(days, return_inverse=True)
    s = np.bincount(inv, weights=x)
    keep = np.ones(len(u), bool)
    keep[np.argsort(-s)[:5]] = False
    c = np.bincount(inv).astype(float)
    return s[keep].sum() / c[keep].sum() if c[keep].sum() else float("nan")


def main():
    data = {}
    for tfn, (k, bm) in TFS.items():
        for sym in S.SYMS:
            if os.path.exists(os.path.join(S.CACHE, sym + "USDT_15m.npz")):
                data[(tfn, sym)] = S.prep(sym, k)
    syms = sorted({s for _, s in data})
    print("symbols", len(syms), syms, flush=True)
    res, rows = {}, []
    # regime mix over all days (VAL), per symbol-day
    mixd = {}
    for sym in syms:
        D = data[("1h", sym)]
        m = D["valid"] & (D["a"][:, 0] >= S.SPLIT)
        ph = D["ph"][m]
        mixd[sym] = [int((ph == v).sum()) for v in (1, -1, 0)]
    tot = np.array(list(mixd.values())).sum(0)
    allmix = dict(UP=tot[0] / tot.sum(), DOWN=tot[1] / tot.sum(), RANGE=tot[2] / tot.sum())
    for tfn, (k, bm) in TFS.items():
        for fam, side, lvl in FAMS:
            for kind in ("primary", "control"):
                phs = OKPH[side] if kind == "primary" else CTRL[side]
                tr = []
                for sym in syms:
                    D = data[(tfn, sym)]
                    for (t, R, df, ph) in S.run_trades(D, side, lvl, k, phs, bm):
                        tr.append((sym, t, R, df, ph))
                res[(tfn, fam, kind)] = tr
    # placebo pools
    pool = {}
    for tfn, (k, bm) in TFS.items():
        for side in (1, -1):
            for sym in syms:
                D = data[(tfn, sym)]
                a = D["a"]
                cand = np.flatnonzero(D["valid"] & (a[:, 0] >= S.SPLIT) & np.isin(D["ph"], OKPH[side]))
                if len(cand) > 2000:
                    cand = rng.choice(cand, 2000, replace=False)
                out = []
                for i in cand:
                    s = S.simulate(D, int(i), side, bm)
                    if s:
                        out.append((s[0], s[1]))
                pool[(tfn, side, sym)] = np.array(out) if out else np.zeros((0, 2))
        print("pool", tfn, flush=True)
    summary, pvals = [], []
    for tfn in TFS:
        for fam, side, lvl in FAMS:
            for kind in ("primary", "control"):
                tr = res[(tfn, fam, kind)]
                row = dict(tf=tfn, fam=fam, kind=kind)
                for per, sel in (("DEV", lambda t: t < S.SPLIT), ("VAL", lambda t: t >= S.SPLIT)):
                    z = [x for x in tr if sel(x[1])]
                    R = np.array([x[2] for x in z]); df = np.array([x[3] for x in z])
                    n12 = R - S.FEE_TAKER / df if len(z) else R
                    row[per] = dict(n=len(z), win=float((n12 > 0).mean()) if len(z) else None,
                                    net12=float(n12.mean()) if len(z) else None,
                                    net6=float((R - S.FEE_MAKER / df).mean()) if len(z) else None,
                                    gross=float(R.mean()) if len(z) else None,
                                    fee_frac=float((S.FEE_TAKER / df).mean()) if len(z) else None,
                                    stop_pct=float(df.mean() * 100) if len(z) else None)
                    if per == "VAL" and len(z) >= 2:
                        days = np.array([int(x[1] // S.DAY) for x in z])
                        row["ci_trade"] = float(boot_ci(n12))
                        row["ci_day"] = float(cluster_ci(days, n12))
                        row["ex5"] = float(ex_best5(days, n12))
                        ph = np.array([x[4] for x in z])
                        row["mix"] = dict(UP=float((ph == 1).mean()), DOWN=float((ph == -1).mean()), RANGE=float((ph == 0).mean()))
                        # placebo
                        symv = [x[0] for x in z]
                        cnt = {s: symv.count(s) for s in set(symv)}
                        ok = all(len(pool[(tfn, side, s)]) >= 20 for s in cnt)
                        if ok:
                            B = 1000
                            sums = np.zeros(B)
                            for s, c in cnt.items():
                                p = pool[(tfn, side, s)]
                                ii = rng.integers(0, len(p), (B, c))
                                sums += (p[ii, 0] - S.FEE_TAKER / p[ii, 1]).sum(1)
                            means = sums / len(z)
                            row["placebo_mean"] = float(means.mean())
                            row["placebo_p"] = float((1 + (means >= n12.mean()).sum()) / (B + 1))
                if kind == "primary":
                    pvals.append(row.get("placebo_p", 1.0))
                summary.append(row)
    prim = [r for r in summary if r["kind"] == "primary"]
    okbh = S.bh(np.array([r.get("placebo_p", 1.0) for r in prim]))
    for r, o in zip(prim, okbh):
        v = r["VAL"]
        gates = dict(
            n=v["n"] >= 100, mean=(v["net12"] or -1) > 0,
            ci=(r.get("ci_trade", -1) > 0 and r.get("ci_day", -1) > 0),
            placebo=r.get("placebo_p", 1) < 0.05, bh=bool(o), ex5=(r.get("ex5", -1) or -1) > 0)
        r["bh"] = bool(o); r["gates"] = gates; r["pass"] = all(gates.values())
    json.dump(dict(rows=summary, allmix=allmix, syms=syms), open(os.path.join(HERE, "summary.json"), "w"), indent=1, default=float)
    print("done", flush=True)


if __name__ == "__main__":
    main()
