"""WaveTrend DEV atlas (card wavetrend-dev-atlas): the ONE pre-registered DEV run of PRE_REG.md. DEV only (< 2024-07-01).

Cells, outcomes, arms and the Holm family are exactly PRE_REG.md s5-s6; a cell id or definition that is not in the frozen
CELLS.csv / PRE_REG.md raises. Events, context bins and the WT series come from count_events.py (same code that froze the
counts); the WT series is cross-checked against backtest/layers/wavetrend (the observation module) before any outcome is read.
Gross only: no fees, no funding, no strategy. VALIDATION and HOLDOUT are never opened (the loader refuses bars >= 2024-07-01).

Usage: python atlas.py --out <dir>      writes atlas_results.json + RESULT.md
"""
import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import count_events as ce  # noqa: E402

PARAMS = {"R_out": 3, "c": 5, "k": 2, "G": 20}
HS = (4, 12, 48)
PRIMARY_H = 12
NDRAW = 200
SEED = 20261017
M_HOLM = 9
REVERSAL = {"A1", "A2", "A3", "C1", "C2"}       # implied direction toward the centre: -side
CONTINUE = {"B1", "B2"}                          # implied direction = side
CONTROLS = ("A3_L53", "A1_L60", "A3_L60")        # PRE_REG s6: reported beside the A cells, never cells
CTX_VARS = ("trend", "htf")                      # the only context variables that appear in the 9 frozen cells


# ------------------------------------------------------------------ frozen definition
def load_cells(cells_csv=None, pre_reg=None):
    """Frozen cells from counts/CELLS.csv, each checked against its PRE_REG.md table row. Anything else raises."""
    cells_csv = Path(cells_csv or HERE / "counts" / "CELLS.csv")
    text = Path(pre_reg or HERE / "PRE_REG.md").read_text(encoding="utf-8")
    cells = list(csv.DictReader(open(cells_csv, newline="", encoding="utf-8")))
    if not 0 < len(cells) <= 12:
        raise ValueError(f"{len(cells)} cells; PRE_REG freezes <= 12")
    for c in cells:
        row = next((ln for ln in text.splitlines() if ln.startswith(f"| {c['cell']} |")), None)
        if row is None:
            raise ValueError(f"cell {c['cell']} is not in PRE_REG.md")
        if c["tf"] not in row or c["bin"].split("_", 1)[1] not in row or int(c["events"]) != int(row.split("|")[5]):
            raise ValueError(f"cell {c['cell']} in CELLS.csv does not match its PRE_REG.md row")
    return {c["cell"]: c for c in cells}


def require_cell(cells, cell_id, tf, event, var, bn):
    """A requested cell must equal the frozen one; a cell not in PRE_REG raises."""
    c = cells.get(cell_id)
    if c is None:
        raise KeyError(f"cell {cell_id} is not in PRE_REG (frozen: {sorted(cells)})")
    if (c["tf"], c["event"], c["context_var"], c["bin"]) != (tf, event, var, bn):
        raise ValueError(f"cell {cell_id} definition differs from PRE_REG")
    return c


def direction(event, side):
    base = event.split("_")[0]
    if base in REVERSAL:
        return -side
    if base in CONTINUE:
        return side
    raise ValueError(event)


# ------------------------------------------------------------------ outcome arrays (per bar, raw; sign applied per event)
def forward(B):
    """fwd[H][t] = C[t+H]/O[t+1]-1; up/dn[t] = max high / min low over t+1..t+12 vs O[t+1] (bar extremes: upper bounds)."""
    O, H_, L, C = B["O"], B["H"], B["L"], B["C"]
    n = len(C)
    out = {}
    o1 = np.full(n, np.nan)
    o1[:-1] = O[1:]
    for h in HS:
        f = np.full(n, np.nan)
        f[:n - h] = C[h:] / o1[:n - h] - 1
        out[h] = f
    w = PRIMARY_H
    up = np.full(n, np.nan)
    dn = np.full(n, np.nan)
    if n > w + 1:
        sw = np.lib.stride_tricks.sliding_window_view
        up[:n - w] = sw(H_[1:], w).max(axis=1)[:n - w] / o1[:n - w] - 1
        dn[:n - w] = sw(L[1:], w).min(axis=1)[:n - w] / o1[:n - w] - 1
    out["up"], out["dn"] = up, dn
    return out


def vol_bin(ctx, edges):
    v = ctx["vol"]
    vb = np.where(np.isnan(v), -1, (v > edges["vol"][0]).astype(int) + (v > edges["vol"][1]).astype(int))
    return vb


def bin_mask(ctx, var, bn, side):
    """Vectorised twin of count_events.bin_of for the two context variables used by the frozen cells."""
    if var == "trend":
        lab = ("trend_against", "trend_mixed", "trend_with")
        tr = ctx["trend"]
        return (tr != 9) & (np.sign(tr * side).astype(int) + 1 == lab.index(bn))
    if var == "htf":
        hv = ctx["htf"]
        ok = ~np.isnan(hv)
        sv = np.where(ok, side * hv, 0.0)
        lab = np.where(sv >= 53, "htf_with", np.where(sv <= -53, "htf_against", "htf_mid"))
        return ok & (lab == bn)
    raise ValueError(f"context variable {var} is not in any frozen cell")


# ------------------------------------------------------------------ statistics
def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (float(c - h), float(c + h))


def cluster_mean_se(x, day):
    """Mean and day-clustered SE (sum of within-day deviations, squared, over N)."""
    x = np.asarray(x, float)
    n = len(x)
    if n == 0:
        return float("nan"), float("nan"), 0
    m = x.mean()
    s = {}
    for xi, d in zip(x - m, day):
        s[d] = s.get(d, 0.0) + xi
    se = float(np.sqrt(sum(v * v for v in s.values())) / n)
    return float(m), se, len(s)


def pval(z):
    return float(2 * (1 - NormalDist().cdf(abs(z)))) if np.isfinite(z) else float("nan")


def holm(ps, alpha=0.05):
    """Holm step-down: returns reject flags and adjusted p."""
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    rej, adj, run = [False] * m, [0.0] * m, 0.0
    still = True
    for r, i in enumerate(order):
        a = min(1.0, (m - r) * ps[i])
        run = max(run, a)
        adj[i] = run
        still = still and (ps[i] <= alpha / (m - r))
        rej[i] = still
    return rej, adj


# ------------------------------------------------------------------ arms
def realised(B, F, wt1, wt2, cross, events, m, name, with_response=True):
    """Per-event arrays for a list of (t, side): signed returns (bps) per horizon, MFE/MAE bps, response time, depth."""
    rows = []
    for t, s in events:
        r12 = F[PRIMARY_H][t]
        if np.isnan(r12) or np.isnan(F["up"][t]) or np.isnan(F["dn"][t]):
            continue
        rows.append((t, s))
    if not rows:
        return None
    T = np.array([r[0] for r in rows])
    S = np.array([r[1] for r in rows])
    d = np.array([direction(name, s) for s in S])
    out = {"t": T, "side": S, "d": d, "day": (T * m) // 1440}
    for h in HS:
        out[f"r{h}"] = d * F[h][T] * 1e4
    up, dn = F["up"][T], F["dn"][T]
    out["mfe"] = np.where(d > 0, up, -dn) * 1e4
    out["mae"] = np.where(d > 0, dn, -up) * 1e4
    if with_response:
        n = len(wt1)
        resp = np.empty(len(T))
        for i, (t, s) in enumerate(zip(T, S)):
            r = PRIMARY_H                                  # censored at H
            for u in range(1, PRIMARY_H + 1):
                if t + u >= n:
                    break
                w1 = wt1[t + u]
                if cross[t + u] != 0 or (not np.isnan(w1) and s * w1 <= 0):
                    r = u
                    break
            resp[i] = r
        out["resp"] = resp
    return out


def depth_of(wt1, events, L):
    """Episode depth (outcome only): max side*wt1 from t until side*wt1 < L (A1/A2 events)."""
    out = []
    for t, s in events:
        mx, u = -np.inf, t
        while u < len(wt1) and not np.isnan(wt1[u]) and s * wt1[u] >= L:
            mx = max(mx, s * wt1[u])
            u += 1
        out.append(mx)
    return float(np.median(out)) if out else float("nan")


def summarize(a):
    if a is None:
        return {"n": 0}
    x = a["r12"]
    mean, se, nd = cluster_mean_se(x, a["day"])
    k = int((x > 0).sum())
    lo, hi = wilson(k, len(x))
    s = {"n": int(len(x)), "days": nd, "events_per_day": round(len(x) / nd, 2), "mean_bps": mean, "se_bps": se,
         "hit": k / len(x), "hit_lo": lo, "hit_hi": hi, "sd_bps": float(x.std(ddof=1)) if len(x) > 1 else float("nan"),
         "mfe_med": float(np.median(a["mfe"])), "mae_med": float(np.median(a["mae"]))}
    for h in (4, 48):
        s[f"mean{h}_bps"] = float(np.nanmean(a[f"r{h}"])) if np.isfinite(a[f"r{h}"]).any() else float("nan")
    if "resp" in a:
        s["resp_med"] = float(np.median(a["resp"]))
    return s


def draws_summary(R12, R4, R48, MFE, MAE, event_day_n=None):
    """Summary of a (NDRAW, N) draw matrix: mean = mean of draw means; SE = SD of draw means (control sampling noise)."""
    dm = R12.mean(axis=1)
    return {"mean_bps": float(dm.mean()), "se_bps": float(dm.std(ddof=1)), "hit": float((R12 > 0).mean()),
            "mean4_bps": float(np.nanmean(R4)), "mean48_bps": float(np.nanmean(R48)),
            "mfe_med": float(np.median(MFE)), "mae_med": float(np.median(MAE)), "sd_bps": float(R12.std()), "n": int(R12.shape[1])}


def diff_test(a, b):
    """a minus b on the primary outcome, independent-arm z (cluster SE for event arms, draw SD for control arms)."""
    d = a["mean_bps"] - b["mean_bps"]
    se = float(np.sqrt(a["se_bps"] ** 2 + b["se_bps"] ** 2))
    z = d / se if se > 0 else float("nan")
    return {"diff_bps": d, "se_bps": se, "z": z, "p": pval(z)}


class Tf:
    """Everything per timeframe that arms need (built once)."""

    def __init__(self, tf, res, Bs, wts):
        self.tf, self.m = tf, ce.TFS[tf]
        self.B, self.r = Bs[tf], res[tf]
        self.wt1, self.wt2 = wts[tf]
        self.cross = ce.ev_cross(self.wt1, self.wt2)
        self.F = forward(self.B)
        self.ctx, self.edges = self.r["ctx"], self.r["edges"]
        self.vb = vol_bin(self.ctx, self.edges)
        self.slots = max(1, 1440 // self.m) if self.m < 1440 else 1
        n = len(self.wt1)
        self.slot = np.arange(n) % self.slots
        valid = (self.vb >= 0) & ~np.isnan(self.F[PRIMARY_H]) & ~np.isnan(self.F["up"]) & ~np.isnan(self.F["dn"])
        self.pool = {}
        for key in set(zip(self.vb[valid], self.slot[valid])):
            self.pool[key] = np.where(valid & (self.vb == key[0]) & (self.slot == key[1]))[0]


def run_arm_draws(rng, N, members_by_key, pool_by_key, dir_by_pick):
    """Generic draw: members_by_key {key: [event positions]}; pool_by_key {key: (t array, side array or None)}.
    Returns t_matrix (NDRAW, N) and side_matrix or None, plus the count of events without any pool."""
    tm = np.zeros((NDRAW, N), int)
    sm = np.zeros((NDRAW, N), int)
    missing = 0
    for key, mem in members_by_key.items():
        pool = pool_by_key.get(key)
        if pool is None or len(pool[0]) == 0:
            missing += len(mem)
            tm[:, mem] = -1
            continue
        pick = rng.integers(0, len(pool[0]), (NDRAW, len(mem)))
        tm[:, mem] = pool[0][pick]
        if pool[1] is not None:
            sm[:, mem] = pool[1][pick]
    return tm, sm, missing


def control_stats(tfo, T, D, F, tm):
    """Signed outcomes of a draw matrix tm (NDRAW, N) with directions D (N,) -> summary dict."""
    good = (tm >= 0).all(axis=0)
    tm = tm[:, good]
    D = D[good]
    r = lambda h: D[None, :] * F[h][tm] * 1e4
    mfe = np.where(D[None, :] > 0, F["up"][tm], -F["dn"][tm]) * 1e4
    mae = np.where(D[None, :] > 0, F["dn"][tm], -F["up"][tm]) * 1e4
    return draws_summary(r(PRIMARY_H), r(4), r(48), mfe, mae), int((~good).sum())


def event_arms(tfo, name, events, rng, ctx_spec=None):
    """All four arms for one set of conjunction events. ctx_spec=(var, bin) enables the context-alone arm."""
    base = name.split("_")[0]
    conj = realised(tfo.B, tfo.F, tfo.wt1, tfo.wt2, tfo.cross, events, tfo.m, name)
    if conj is None:
        return {"n": 0}
    out = {"conj": summarize(conj)}
    T, D = conj["t"], conj["d"]
    vb_ev = tfo.vb[T]
    keep = vb_ev >= 0
    out["dropped_no_vol"] = int((~keep).sum())
    T2, D2, S2 = T[keep], D[keep], conj["side"][keep]
    mem = {}
    for i, (t, v) in enumerate(zip(T2, vb_ev[keep])):
        mem.setdefault((int(v), int(t % tfo.slots)), []).append(i)
    # random clock: stratum (vol tercile, hour slot), side-agnostic bars, event's own direction applied
    tm, _, miss = run_arm_draws(rng, len(T2), mem, {k: (v, None) for k, v in tfo.pool.items()}, None)
    rc, drop = control_stats(tfo, T2, D2, tfo.F, tm)
    rc["unmatched_events"] = miss
    rc["strata_min_pool"] = int(min(len(v) for v in tfo.pool.values()))
    out["random_clock"] = rc
    # context alone: same bin, bar has no event of this type, hour slot matched, drawn with the bar's own side
    if ctx_spec:
        var, bn = ctx_spec
        evt = np.zeros(len(tfo.wt1), bool)
        evt[[t for t, _ in tfo.r["evs"][name]]] = True
        ok = ~evt & ~np.isnan(tfo.F[PRIMARY_H]) & ~np.isnan(tfo.F["up"]) & ~np.isnan(tfo.F["dn"])
        pools = {}
        for sl in range(tfo.slots):
            ts, ss = [], []
            for s in (1, -1):
                mk = bin_mask(tfo.ctx, var, bn, s) & ok & (tfo.slot == sl)
                idx = np.where(mk)[0]
                ts.append(idx)
                ss.append(np.full(len(idx), s))
            pools[sl] = (np.concatenate(ts), np.concatenate(ss))
        mem2 = {}
        for i, t in enumerate(T2):
            mem2.setdefault(int(t % tfo.slots), []).append(i)
        tm2, sm2, miss2 = run_arm_draws(rng, len(T2), mem2, pools, None)
        Dm = np.vectorize(lambda s: direction(name, s))(np.where(sm2 == 0, 1, sm2))
        good = (tm2 >= 0).all(axis=0)
        tm2g, Dg = tm2[:, good], Dm[:, good]
        r = lambda h: Dg * tfo.F[h][tm2g] * 1e4
        mfe = np.where(Dg > 0, tfo.F["up"][tm2g], -tfo.F["dn"][tm2g]) * 1e4
        mae = np.where(Dg > 0, tfo.F["dn"][tm2g], -tfo.F["up"][tm2g]) * 1e4
        ca = draws_summary(r(PRIMARY_H), r(4), r(48), mfe, mae)
        ca["unmatched_events"] = miss2
        out["context_alone"] = ca
    return out


def cell_result(tfo, cell, rng, frozen_counts_ok):
    name, var, bn = cell["event"], cell["context_var"], cell["bin"]
    allev = tfo.r["evs"][name]
    conj_ev = [(t, s) for t, s in allev if ce.bin_of(tfo.ctx, tfo.edges, t, s)[var] == bn]
    n_ev = len(conj_ev)
    n_days = len({(t * tfo.m) // 1440 for t, _ in conj_ev})
    counts_match = (n_ev == int(cell["events"]) and n_days == int(cell["event_days"]))
    res = event_arms(tfo, name, conj_ev, rng, (var, bn))
    alone = realised(tfo.B, tfo.F, tfo.wt1, tfo.wt2, tfo.cross, allev, tfo.m, name)
    res["wt_alone"] = summarize(alone)
    if name.startswith(("A1", "A2")):
        L = int(name.split("_L")[1])
        res["depth_med_conj"] = depth_of(tfo.wt1, conj_ev, L)
    c = res["conj"]
    tests = {"vs_random_clock": diff_test(c, res["random_clock"]),
             "vs_wt_alone": diff_test(c, res["wt_alone"]),
             "vs_context_alone": diff_test(c, res["context_alone"])}
    res.update({"cell": cell["cell"], "tf": tfo.tf, "event": name, "context": f"{var}:{bn}", "counts_match_prereg": counts_match,
                "events_prereg": int(cell["events"]), "event_days_prereg": int(cell["event_days"]),
                "events_found": n_ev, "event_days_found": n_days, "tests": tests, "mde_sd_prereg": float(cell["mde_d_holm12"])})
    return res


def descriptive_row(tfo, name, rng, ctx_spec=None):
    ev = tfo.r["evs"][name]
    r = event_arms(tfo, name, ev, rng, ctx_spec)
    if r.get("n") == 0:
        return r
    r["tests"] = {"vs_random_clock": diff_test(r["conj"], r["random_clock"])}
    r["event"], r["tf"] = name, tfo.tf
    return r


# ------------------------------------------------------------------ module cross-check (observation module vs reference WT)
def module_crosscheck(Bs, wts, tfs=("5m", "15m", "1h", "4h")):
    p = HERE.parent.parent / "backtest" / "layers" / "wavetrend" / "wavetrend.py"
    spec = importlib.util.spec_from_file_location("wt_module", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rep = {}
    for tf in tfs:
        B, m = Bs[tf], ce.TFS[tf]
        bars = [(ce.TS0 + i * m * ce.MS, float(h), float(l), float(c)) for i, (h, l, c) in enumerate(zip(B["H"], B["L"], B["C"]))]
        rows = mod.compute(bars, m * ce.MS)
        w1 = np.array([r.wt1 for r in rows])
        w2 = np.array([r.wt2 for r in rows])
        a1, a2 = wts[tf]
        both = ~np.isnan(w1) & ~np.isnan(a1)
        rep[tf] = {"valid_module": int((~np.isnan(w1)).sum()), "valid_ref": int((~np.isnan(a1)).sum()), "valid_both": int(both.sum()),
                   "max_abs_diff_wt1": float(np.abs(w1[both] - a1[both]).max()) if both.any() else None,
                   "max_abs_diff_wt2": float(np.abs(w2[both] - a2[both]).max()) if both.any() else None}
    return rep


# ------------------------------------------------------------------ main
def main(out_dir):
    cells = load_cells()
    res, qlines, Bs = ce.run(out_dir, PARAMS)
    wts = {}
    for tf in ce.TFS:
        wts[tf] = ce.wt_series(Bs[tf])
    xcheck = module_crosscheck(Bs, wts)
    rng = np.random.default_rng(SEED)
    tfo = {tf: Tf(tf, res, Bs, wts) for tf in ("5m", "15m", "1h", "4h")}
    cell_res = []
    for cid, cell in cells.items():
        require_cell(cells, cid, cell["tf"], cell["event"], cell["context_var"], cell["bin"])
        cell_res.append(cell_result(tfo[cell["tf"]], cell, rng, True))
    ps = [c["tests"]["vs_random_clock"]["p"] for c in cell_res]
    rej, adj = holm(ps)
    for c, r, a in zip(cell_res, rej, adj):
        c["holm_reject"], c["holm_adj_p"] = bool(r), float(a)
        t = c["tests"]
        pos = t["vs_random_clock"]["diff_bps"] > 0
        beats = lambda k: t[k]["diff_bps"] > 0 and abs(t[k]["z"]) > 1.96
        c["pass_gross_dev"] = bool(r and pos and beats("vs_wt_alone") and beats("vs_context_alone"))
        c["underpowered"] = bool(c["event_days_found"] < 153)
        mde_bps = (NormalDist().inv_cdf(1 - 0.05 / (2 * M_HOLM)) + 0.8416) * t["vs_random_clock"]["se_bps"]
        c["realised_mde_bps_holm9"] = float(mde_bps)
        c["mde_bps_prereg_sd"] = c["mde_sd_prereg"] * c["random_clock"]["sd_bps"]
    controls, descriptive = [], []
    for tf in ("5m", "15m", "1h"):
        for nm in CONTROLS:
            controls.append(descriptive_row(tfo[tf], nm, rng))
    for nm in ("A1_L53", "A2_L53", "B1", "B2", "C1", "C2"):
        descriptive.append(descriptive_row(tfo["4h"], nm, rng))
    for tf in ("5m", "15m"):
        descriptive.append(descriptive_row(tfo[tf], "C2", rng))
    out = {"params": PARAMS, "seed": SEED, "ndraw": NDRAW, "horizons": HS, "primary_h": PRIMARY_H, "cells": cell_res,
           "controls": controls, "descriptive": descriptive, "module_crosscheck": xcheck, "quality": qlines,
           "reads": {"validation": 0, "holdout": 0}}
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    (Path(out_dir) / "atlas_results.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    o = main(a.out)
    for c in o["cells"]:
        t = c["tests"]["vs_random_clock"]
        print(c["cell"], c["tf"], c["event"], c["context"], "n", c["conj"]["n"], "mean", round(c["conj"]["mean_bps"], 2),
              "rc", round(c["random_clock"]["mean_bps"], 2), "z", round(t["z"], 2), "holm", c["holm_reject"], "pass", c["pass_gross_dev"],
              "counts_match", c["counts_match_prereg"])
    print(json.dumps(o["module_crosscheck"]))
