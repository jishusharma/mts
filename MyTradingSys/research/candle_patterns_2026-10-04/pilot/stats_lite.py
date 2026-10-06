"""Inference helpers for the candle pilot. Stdlib only.

block_boot_family: studentised, single-step max-T (White Reality-Check / Westfall-Young style) over a family of
"pattern events vs all bars" statistics, using a circular block bootstrap of (event, value) pairs so serial
dependence and overlapping forward windows are respected.  Stat_k = sign_k * (mean(val | event_k) - mean(val)).
bh_qvalues: Benjamini-Hochberg step-up q-values.
"""
import sys
sys.dont_write_bytecode = True
import math
import random


def bh_qvalues(p):
    m = len(p)
    order = sorted(range(m), key=lambda i: p[i])
    q = [0.0] * m
    prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        prev = min(prev, p[i] * m / rank)
        q[i] = prev
    return q


def _prefix(a):
    out = [0.0]
    s = 0.0
    for x in a:
        s += x
        out.append(s)
    return out


def block_boot_family(items, m, block, reps=1000, seed=12345):
    """items: list of dict(name, ev=[0/1]*m, val=[float]*m, sign=+1/-1, min_n=int).
    Returns per item: n, stat, sd, t, p_raw (one-sided, sign-adjusted), p_two (two-sided), p_adj_max (single-step max-T over the family)."""
    res = []
    live = []
    for it in items:
        n = sum(it["ev"])
        r = {"name": it["name"], "n": n, "stat": None, "sd": None, "t": None, "p_raw": None, "p_two": None, "p_adj": None,
             "insufficient": n < it["min_n"]}
        res.append(r)
        if n >= it["min_n"]:
            live.append((it, r))
    if not live:
        return res
    # prefix sums on the doubled (circular) arrays
    pre = []
    mean_all_cache = {}
    for it, r in live:
        ev, val = it["ev"], it["val"]
        evd, vald = ev + ev, val + val
        pc = _prefix(evd)
        psf = _prefix([e * v for e, v in zip(evd, vald)])
        key = id(val)
        if key not in mean_all_cache:
            mean_all_cache[key] = (_prefix(vald), sum(val) / m)
        pa, mu = mean_all_cache[key]
        pre.append((pc, psf, pa, mu, it["sign"]))
        n = r["n"]
        r["stat"] = it["sign"] * (sum(e * v for e, v in zip(ev, val)) / n - mu)
    nb = int(math.ceil(m / float(block)))
    rng = random.Random(seed)
    K = len(live)
    boot = [[0.0] * reps for _ in range(K)]
    for b in range(reps):
        starts = [rng.randrange(m) for _ in range(nb)]
        tot = nb * block
        for k in range(K):
            pc, psf, pa, mu, sg = pre[k]
            cnt = sf = sa = 0.0
            for s in starts:
                e = s + block
                cnt += pc[e] - pc[s]
                sf += psf[e] - psf[s]
                sa += pa[e] - pa[s]
            boot[k][b] = sg * ((sf / cnt) - (sa / tot)) if cnt > 0 else 0.0
    sds, tobs = [], []
    for k, (it, r) in enumerate(live):
        mb = sum(boot[k]) / reps
        sd = math.sqrt(sum((x - mb) ** 2 for x in boot[k]) / (reps - 1)) or 1e-12
        r["sd"], r["t"] = sd, r["stat"] / sd
        sds.append(sd)
        tobs.append(r["t"])
    # centered studentised replicates
    maxT = [-1e18] * reps
    for k, (it, r) in enumerate(live):
        mb = sum(boot[k]) / reps
        cen = [(x - mb) / sds[k] for x in boot[k]]
        r["p_raw"] = (sum(1 for x in cen if x >= r["t"]) + 1.0) / (reps + 1)
        r["p_two"] = (sum(1 for x in cen if abs(x) >= abs(r["t"])) + 1.0) / (reps + 1)
        for b in range(reps):
            if cen[b] > maxT[b]:
                maxT[b] = cen[b]
    for k, (it, r) in enumerate(live):
        r["p_adj"] = (sum(1 for x in maxT if x >= r["t"]) + 1.0) / (reps + 1)
    return res
