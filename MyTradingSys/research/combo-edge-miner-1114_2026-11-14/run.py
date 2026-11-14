"""Pipeline for combo-edge-miner-1114 (see PRE_REG.md): exhaustive 2/3-way DEV search, deflation, top-10 VAL confirmation, named
thinker combos, active-now readout. Writes results.json; make_result.py renders RESULT.md. Run: python run.py [--syms BTC,ETH]"""
import os
import sys
import json
import time
import math
import itertools
import argparse
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import miner as M  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
MIN_N = 100          # min trades per cell on DEV
NULL_B = 40          # max-of-N placebo rounds
BOOT_B = 2000
PLACEBO_B = 1000
SEED = 20261114
NONBEAR = ["UP_E", "UP_L", "MIX_E", "MIX_L"]
DOWN = ["DOWN_E", "DOWN_L"]
ALLP = M.PHASES

# thinker combos approximated with bank features (PRE_REG section 5); dir, feature names, allowed phases, label
NAMED = [
    ("T1 flush-reset long", 1, ["OI_FLUSH", "NB_ABS", "SWEEP"], NONBEAR),
    ("T2 trapped-longs short", -1, ["PDOU", "OI_HI", "FUND_HI"], DOWN),
    ("T2b trapped-longs short + no spot absorb", -1, ["PDOU", "OI_HI", "FUND_HI", "NB_PER"], DOWN),
    ("T3 trapped-shorts squeeze long", 1, ["FUND_LO", "NB_ABS", "BRK5"], NONBEAR),
    ("T4 squeeze-exhaustion short", -1, ["PUOD", "ABOVE_200", "BIGBAR"], DOWN),
    ("T5 spot-led ignition long", 1, ["NB_PER", "BRK20", "NEAR_200W"], NONBEAR),
    ("T7 bear rip-sell short", -1, ["BB_EXT", "ADX_DI", "ABOVE_200"], DOWN),
    ("T8 broken-low continuation short", -1, ["BRK20", "ADX_DI", "FUND_HI"], DOWN),
    ("T9 200w failed breakdown long", 1, ["NEAR_200W", "SWEEP", "RSI_X"], ["MIX_E", "MIX_L", "DOWN_E", "DOWN_L"]),
    ("T10 washout band-reclaim trend long", 1, ["TREND_MA", "RSI_MOM", "ADX_DI"], ["UP_E", "UP_L", "MIX_E"]),
    ("T11 sweep-reclaim discount long", 1, ["SWEEP", "DD_DEEP"], ALLP),
    ("T11b sweep-reclaim discount + OI flush long", 1, ["SWEEP", "DD_DEEP", "OI_FLUSH"], ALLP),
    ("T12 flag long (squeeze, ADX, break)", 1, ["BB_SQZ", "ADX_DI", "BRK5"], ["UP_E", "UP_L"]),
    ("T12 flag short (squeeze, ADX, break)", -1, ["BB_SQZ", "ADX_DI", "BRK5"], DOWN),
]
NOT_IN_DATA = ["T6 cohort divergence (top-trader position ratio not in the cache; data.binance.vision metrics columns were not fetched)"]


def combos():
    ids = list(range(M.NF))
    return [c for k in (2, 3) for c in itertools.combinations(ids, k)]


def mask_of(names):
    return np.array([p in names for p in M.PHASES], bool)


def pool(fr, d, kind, p_mask, window):
    sm = fr.sim[(d, kind)]
    wm = fr.dev if window == "dev" else fr.val
    ok = wm & (sm["xg"] >= 0) & (fr.phase_i >= 0) & p_mask[np.clip(fr.phase_i, 0, 5)]
    idx = np.flatnonzero(ok)
    return idx, M.net_r(sm, idx, M.COST12), fr.entry_day[idx]


def dev_search(fr, log, cl=None):
    """Evaluate every 2/3-way combo x phase x exit on DEV for one frame. Returns list of cell dicts and the number of cells tried."""
    cells = []
    tried = 0
    t0 = time.time()
    cl = cl or combos()
    for d in (1, -1):
        for ci, c in enumerate(cl):
            tried += 6 * len(M.KINDS)
            on = M.onsets(fr, d, list(c)) & fr.dev
            idx = np.flatnonzero(on)
            if idx.size < MIN_N:
                continue
            ph = fr.phase_i[idx]
            for p in range(6):
                ip = idx[ph == p]
                if ip.size < MIN_N:
                    continue
                for kind in M.KINDS:
                    sm = fr.sim[(d, kind)]
                    ik = ip[sm["xg"][ip] >= 0]
                    if ik.size < MIN_N:
                        continue
                    pk = M.greedy(ik, sm["xg"][ik])
                    if pk.size < MIN_N:
                        continue
                    r = M.net_r(sm, pk, M.COST12)
                    m, se, g = M.cluster_stats(r, fr.entry_day[pk])
                    cells.append(dict(tf=fr.tf, d=d, combo=c, phase=p, kind=kind, n=int(pk.size), days=int(g), mean12=m, se12=se,
                                      mean6=float(M.net_r(sm, pk, M.COST6).mean()),
                                      gross=float((sm["ret"][pk] / sm["risk"][pk]).mean()),
                                      feeR=float((M.COST12 / sm["risk"][pk]).mean()), win=float((r > 0).mean())))
            if ci % 500 == 0:
                log(f"  {fr.tf} dir {d} combo {ci}/{len(cl)} cells {len(cells)} {time.time()-t0:.0f}s")
    return cells, tried


def null_maxt(fr, cells_tf, rng, rounds):
    """Max-of-N placebo: per round, every qualifying cell gets n RANDOM same-phase DEV entries (same tf, dir, exit); the max cluster t
    over all cells is the null statistic. Returns array of per-round max t."""
    pools = {}
    mx = np.full(rounds, -np.inf)
    for c in cells_tf:
        key = (c["d"], c["kind"], c["phase"])
        if key not in pools:
            pm = np.zeros(6, bool)
            pm[c["phase"]] = True
            pools[key] = pool(fr, c["d"], c["kind"], pm, "dev")
        _, r, dd = pools[key]
        if len(r) < c["n"]:
            continue
        for b in range(rounds):
            ix = rng.integers(0, len(r), c["n"])
            m, se, _ = M.cluster_stats(r[ix], dd[ix])
            if se > 0:
                t = m / se
                if t > mx[b]:
                    mx[b] = t
    return mx


def evaluate(fr, d, feats, kind, p_mask, window, rng, full=True):
    """Stats of one cell in a window at 12 and 6 bp; bootstrap CI over day clusters, ex-best-5 days, same-phase random placebo."""
    pk = M.cell_picks(fr, d, feats, kind, p_mask, window)
    out = dict(n=int(pk.size))
    if pk.size < 5:
        return out
    sm = fr.sim[(d, kind)]
    r12 = M.net_r(sm, pk, M.COST12)
    r6 = M.net_r(sm, pk, M.COST6)
    day = fr.entry_day[pk]
    m, se, g = M.cluster_stats(r12, day)
    out.update(mean12=m, se12=se, days=int(g), mean6=float(r6.mean()), gross=float((sm["ret"][pk] / sm["risk"][pk]).mean()),
               feeR=float((M.COST12 / sm["risk"][pk]).mean()), win=float((r12 > 0).mean()), avg_win=float(r12[r12 > 0].mean()) if (r12 > 0).any() else 0.0,
               avg_loss=float(r12[r12 <= 0].mean()) if (r12 <= 0).any() else 0.0, phase_counts=[int(((fr.phase_i[pk]) == i).sum()) for i in range(6)])
    _, inv = np.unique(day, return_inverse=True)
    sums, cnt = np.bincount(inv, weights=r12), np.bincount(inv)
    gc = len(sums)
    bi = rng.integers(0, gc, (BOOT_B, gc))
    bm = sums[bi].sum(1) / cnt[bi].sum(1)
    out["ci_lo12"] = float(np.percentile(bm, 2.5))
    out["ci_hi12"] = float(np.percentile(bm, 97.5))
    out["p_boot"] = float((1 + (bm <= 0).sum()) / (BOOT_B + 1))
    s6 = np.bincount(inv, weights=r6)
    b6 = s6[bi].sum(1) / cnt[bi].sum(1)
    out["ci_lo6"] = float(np.percentile(b6, 2.5))
    top5 = np.argsort(sums)[::-1][:5]
    keep = np.ones(gc, bool)
    keep[top5] = False
    out["ex_best5"] = float(sums[keep].sum() / cnt[keep].sum()) if keep.any() else float("nan")
    _, rp, _ = pool(fr, d, kind, p_mask, window)
    if len(rp):
        pm = rp[rng.integers(0, len(rp), (PLACEBO_B, len(pk)))].mean(1)
        out["placebo_mean"] = float(pm.mean())
        out["placebo_p"] = float((1 + (pm >= m).sum()) / (PLACEBO_B + 1))
    return out


def regime_mix(fr):
    res = {}
    for w, mk in (("dev", fr.dev), ("val", fr.val)):
        ph = fr.phase_i[mk & (fr.phase_i >= 0)]
        tot = max(len(ph), 1)
        sh = [float((ph == i).sum() / tot) for i in range(6)]
        res[w] = dict(labels=dict(zip(M.PHASES, sh)), bull=sh[0] + sh[1], range=sh[2] + sh[3], bear=sh[4] + sh[5], bars=int(len(ph)))
    return res


def active_now(fr, cell):
    d, feats = cell["d"], list(cell["combo"])
    out = {}
    for sym in ("BTC", "ETH"):
        ci = fr.syms.index(sym)
        i = fr.end[ci] - 1
        state = bool(all(fr.feat[d][f][i] for f in feats))
        out[sym] = dict(signal_state=state, phase=(M.PHASES[int(fr.phase_i[i])] if fr.phase_i[i] >= 0 else None),
                        in_phase=bool(fr.phase_i[i] >= 0 and mask_of_cell(cell)[fr.phase_i[i]]))
    return out


def mask_of_cell(cell):
    m = np.zeros(6, bool)
    m[cell["phase"]] = True
    return m


def cell_name(cell):
    return "+".join(M.FEATS[f] for f in cell["combo"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--syms", default=",".join(M.SYMS))
    ap.add_argument("--null-rounds", type=int, default=NULL_B)
    a = ap.parse_args()
    syms = a.syms.split(",")
    t0 = time.time()

    def log(s):
        print(f"[{time.time()-t0:6.0f}s] {s}", flush=True)
    rng = np.random.default_rng(SEED)
    frames = {}
    for tf in ("1d", "4h"):
        frames[tf] = M.build_frame(tf, syms)
        log(f"built {tf}: {len(frames[tf].ts)} bars, dev entries {int(frames[tf].dev.sum())}, val entries {int(frames[tf].val.sum())}")
    res = dict(syms=syms, regime={tf: regime_mix(f) for tf, f in frames.items()})
    all_cells, tried = [], 0
    for tf, fr in frames.items():
        c, t = dev_search(fr, log)
        all_cells += c
        tried += t
        log(f"{tf} DEV search: {len(c)} cells with n>={MIN_N} of {t} enumerated")
    res["trials_enumerated"] = tried
    res["cells_n100"] = len(all_cells)
    # deflation
    t = np.array([c["mean12"] / c["se12"] if c["se12"] > 0 else -9 for c in all_cells])
    p = np.array([M.norm_sf(x) for x in t])
    named_trials = len(NAMED) * len(M.KINDS) * 2
    m_total = tried + named_trials
    q = M.bh_qvalues(p, m_total)
    for c, ti, pi, qi in zip(all_cells, t, p, q):
        c["t"], c["p"], c["q"] = float(ti), float(pi), float(qi)
    res["trials_total"] = m_total
    res["named_trials"] = named_trials
    res["bh_reject_q05"] = int((q < 0.05).sum())
    res["dev_best_t"] = float(t.max()) if len(t) else None
    res["dev_positive_cells"] = int(sum(1 for c in all_cells if c["mean12"] > 0))
    res["dev_ci_pos_cells"] = int(sum(1 for c in all_cells if c["mean12"] - 1.96 * c["se12"] > 0))
    log(f"BH rejects at q<0.05: {res['bh_reject_q05']}; positive-mean cells {res['dev_positive_cells']}; CI-low>0 cells {res['dev_ci_pos_cells']}")
    nm = []
    for tf, fr in frames.items():
        nm.append(null_maxt(fr, [c for c in all_cells if c["tf"] == tf], np.random.default_rng(SEED + (1 if tf == "1d" else 2)), a.null_rounds))
        log(f"null max-t {tf} done")
    null_max = np.maximum(nm[0], nm[1])
    res["null_max_t"] = dict(rounds=a.null_rounds, mean=float(null_max.mean()), p95=float(np.percentile(null_max, 95)), max=float(null_max.max()))
    # top 10: rank by day-cluster CI low at 12 bp, one cell per (tf, dir, feature set)
    for c in all_cells:
        c["ci_lo"] = c["mean12"] - 1.96 * c["se12"]
    ranked = sorted(all_cells, key=lambda c: -c["ci_lo"])
    top, seen = [], set()
    for c in ranked:
        key = (c["tf"], c["d"], c["combo"])
        if key in seen:
            continue
        seen.add(key)
        top.append(c)
        if len(top) == 10:
            break
    for c in top:
        c["name"] = cell_name(c)
        c["dev_maxn_p"] = float((1 + (null_max >= c["t"]).sum()) / (len(null_max) + 1))
        fr = frames[c["tf"]]
        pm = mask_of_cell(c)
        c["dev_excess_vs_random"] = c["mean12"] - float(pool(fr, c["d"], c["kind"], pm, "dev")[1].mean())
        c["val12"] = evaluate(fr, c["d"], list(c["combo"]), c["kind"], pm, "val", rng)
        c["active_now"] = active_now(fr, c)
        c["phase_name"] = M.PHASES[c["phase"]]
        c["combo"] = list(c["combo"])
    pv = [c["val12"].get("p_boot", 1.0) for c in top]
    qv = M.bh_qvalues(pv, len(top))
    for c, qq in zip(top, qv):
        v = c["val12"]
        v["bh_q"] = float(qq)
        v["pass"] = bool(v.get("n", 0) >= 30 and v.get("mean12", -1) > 0 and v.get("ci_lo12", -1) > 0 and v.get("ex_best5", -1) > 0
                         and v.get("placebo_p", 1) < 0.05 and qq < 0.05)
        v["underpowered"] = bool(v.get("n", 0) < 30)
    res["top10"] = top
    # named thinker combos on DEV and VAL
    named = []
    for label, d, names, phases in NAMED:
        feats = [M.FIDX[x] for x in names]
        for tf, fr in frames.items():
            for kind in M.KINDS:
                pm = mask_of(phases)
                named.append(dict(name=label, tf=tf, kind=kind, d=d, feats=names, phases=phases,
                                  dev=evaluate(fr, d, feats, kind, pm, "dev", rng), val=evaluate(fr, d, feats, kind, pm, "val", rng)))
    pn = [x["val"].get("p_boot", 1.0) for x in named]
    qn = M.bh_qvalues(pn, len(named))
    for x, qq in zip(named, qn):
        v = x["val"]
        v["bh_q"] = float(qq)
        v["pass"] = bool(v.get("n", 0) >= 30 and v.get("mean12", -1) > 0 and v.get("ci_lo12", -1) > 0 and v.get("ex_best5", -1) > 0
                         and v.get("placebo_p", 1) < 0.05 and qq < 0.05)
    res["named"] = named
    res["named_not_in_data"] = NOT_IN_DATA
    # reference: same-phase random-entry means (the beta every long/short cell is up against)
    base = {}
    for tf, fr in frames.items():
        for d in (1, -1):
            for w in ("dev", "val"):
                for kind in M.KINDS:
                    _, r, _ = pool(fr, d, kind, np.ones(6, bool), w)
                    base[f"{tf}|{d}|{w}|{kind}"] = dict(n=int(len(r)), mean12=float(r.mean()) if len(r) else None)
    res["baseline_all_days"] = base
    res["cost12"], res["cost6"] = M.COST12, M.COST6
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    pd.DataFrame([{**{k: v for k, v in c.items() if k != "combo"}, "combo": "+".join(M.FEATS[f] for f in c["combo"])} for c in all_cells]
                 ).to_csv(os.path.join(M.DATA, "dev_cells.csv"), index=False)
    log("done")


if __name__ == "__main__":
    main()
