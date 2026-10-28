"""B141 Stage 2 (H1: forward range) of PRE_REG_HTF_REPLACE_2026-10-07.md section 5.2, on the cells Stage 1 kept.

For every close of the cell's TF (4H N=240, 1D N=1440) over hist+dev (2022-01-01 .. 2026-06-25 UTC; holdout NOT loaded):
FR = (max high - min low over the next Hb 1m bars) / (sqrt(Hb) * ATR_N at the close); Hb = 1440 (24 h) for 4H, 10080 (7 d) for 1D.
Statistic D = median(FR | balanced) - median(FR | not balanced); H1 predicts D < 0. CI95: day-block bootstrap (block = UTC day of the
close, seed 12345, 2000 draws, weighted medians). Effective n = closes greedily spaced >= Hb bars apart. Year stability: sign of D per
calendar year of the close. Placebo: balanced labels shuffled within ATR_N/close terciles (1000 shuffles, seed 12345); the real D must lie
at or below the 5th percentile of the placebo D (the declared direction of "exceeds the 95th percentile"). PASS = CI upper < 0 and every
year D < 0 and placebo beaten. Selection (section 5.4): among PASS cells the smallest CI upper bound; ties -> coverage nearest 0.70.
No holdout, no Stage 3, no PBO here.
Usage: python research/loose_code/b141_htf_stage2.py [--klines DIR] [--stage1 FILE.json] [--out FILE.json]
"""
import argparse
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import b141_htf_stage1 as s1

MIN_MS = s1.MIN_MS
HB = {"4H": 1440, "1D": 10080}
DRAWS, SHUFFLES, SEED = 2000, 1000, 12345
DAY_MS = 86400000


def forward_ratio(K, i, hb, atr):
    """FR over bars i+1..i+hb; None when not contiguous / past the data / atr<=0."""
    if i + hb >= len(K["t"]) or K["t"][i + hb] - K["t"][i] != hb * MIN_MS or atr <= 0:
        return None
    s = slice(i + 1, i + hb + 1)
    return float((K["h"][s].max() - K["l"][s].min()) / (math.sqrt(hb) * atr))


def collect(K):
    """Per TF: list of dicts {st, fr, day, year, vol} for closes with a valid window and a valid forward range."""
    out = {}
    for tf, (N, step) in s1.TFS.items():
        lst = []
        for j in range(len(K["t"])):
            if (K["t"][j] + MIN_MS) % step:
                continue
            st = s1.window_stats(K, j, N)
            if st is None:
                continue
            fr = forward_ratio(K, j, HB[tf], st["atr"])
            if fr is None:
                continue
            t_close = int(K["t"][j]) + MIN_MS
            year = int(np.datetime64(t_close, "ms").astype("datetime64[Y]").astype(int)) + 1970
            lst.append({"st": st, "fr": fr, "i": j, "day": t_close // DAY_MS, "year": year, "vol": st["atr"] / st["c"]})
        out[tf] = lst
    return out


def wmedian(vals_sorted, w_sorted):
    tot = w_sorted.sum()
    if tot <= 0:
        return float("nan")
    return float(vals_sorted[np.searchsorted(np.cumsum(w_sorted), tot / 2.0)])


def day_block_ci(fr, lab, day, rng):
    """CI95 of median(FR|lab) - median(FR|~lab) by resampling UTC days with replacement."""
    ud, dix = np.unique(day, return_inverse=True)
    parts = []
    for m in (lab, ~lab):
        o = np.argsort(fr[m], kind="stable")
        parts.append((fr[m][o], dix[m][o]))
    ds = []
    for _ in range(DRAWS):
        cnt = np.bincount(rng.integers(0, len(ud), len(ud)), minlength=len(ud))
        a = wmedian(parts[0][0], cnt[parts[0][1]].astype(float))
        b = wmedian(parts[1][0], cnt[parts[1][1]].astype(float))
        if not (math.isnan(a) or math.isnan(b)):
            ds.append(a - b)
    ds = np.array(ds)
    return float(np.percentile(ds, 2.5)), float(np.percentile(ds, 97.5))


def effective_n(idx, hb):
    n, last = 0, None
    for i in sorted(idx):
        if last is None or i - last >= hb:
            n, last = n + 1, i
    return n


def terciles(vol):
    q = np.quantile(vol, [1 / 3, 2 / 3])
    return np.digitize(vol, q)


def placebo(fr, lab, tc, rng):
    groups = [np.where(tc == g)[0] for g in range(3)]
    ds = []
    for _ in range(SHUFFLES):
        sh = lab.copy()
        for g in groups:
            sh[g] = rng.permutation(lab[g])
        ds.append(np.median(fr[sh]) - np.median(fr[~sh]))
    return np.array(ds)


def evaluate(rows, fam, par, tf):
    N = s1.TFS[tf][0]
    fr = np.array([r["fr"] for r in rows])
    lab = np.array([s1.is_balanced(fam, par, r["st"], N) for r in rows], dtype=bool)
    res = {"family": fam, "tf": tf, "params": par, "n": len(rows), "n_balanced": int(lab.sum()),
           "coverage": float(lab.mean()) if len(rows) else None}
    if lab.sum() < 30 or (~lab).sum() < 30:
        res.update(D=None, pass_=False, reason="a class has < 30 closes")
        return res
    day = np.array([r["day"] for r in rows])
    year = np.array([r["year"] for r in rows])
    rng = np.random.default_rng(SEED)
    D = float(np.median(fr[lab]) - np.median(fr[~lab]))
    lo, hi = day_block_ci(fr, lab, day, rng)
    yrs = {}
    for y in sorted(set(year.tolist())):
        m = year == y
        if lab[m].any() and (~lab[m]).any():
            yrs[str(y)] = float(np.median(fr[m & lab]) - np.median(fr[m & ~lab]))
    pl = placebo(fr, lab, terciles(np.array([r["vol"] for r in rows])), rng)
    p5 = float(np.percentile(pl, 5))
    res.update(median_bal=float(np.median(fr[lab])), median_unbal=float(np.median(fr[~lab])), D=D, ci95=[lo, hi],
               eff_n=effective_n([r["i"] for r in rows], HB[tf]), eff_n_balanced=effective_n(
                   [r["i"] for r, l in zip(rows, lab) if l], HB[tf]),
               years=yrs, year_sign_ok=bool(yrs) and all(v < 0 for v in yrs.values()),
               placebo_p5=p5, placebo_beaten=D <= p5)
    res["pass_"] = bool(hi < 0 and res["year_sign_ok"] and res["placebo_beaten"])
    return res


def select(results):
    ok = [r for r in results if r.get("pass_")]
    if not ok:
        return None
    return min(ok, key=lambda r: (r["ci95"][1], abs(r["coverage"] - 0.70)))


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--klines", default="F:/MTS/data/tom_raw/klines")
    ap.add_argument("--stage1", default=os.path.join(here, "b141_stage1_result.json"))
    ap.add_argument("--out", default=os.path.join(here, "b141_stage2_result.json"))
    a = ap.parse_args()
    with open(a.stage1) as fh:
        kept = [c for c in json.load(fh)["cells"] if c["kept"]]
    K = s1.load_klines(a.klines)
    data = collect(K)
    results = [evaluate(data[c["tf"]], c["family"], c["params"], c["tf"]) for c in kept]
    sel = select(results)
    doc = {"period": [s1.HIST_START, s1.DEV_END], "n_cells": len(results), "cells": results, "selected": sel}
    with open(a.out, "w", newline="\n") as fh:
        json.dump(doc, fh, indent=1)
    for r in results:
        print(r["family"], r["tf"], r["params"], "n=%d D=%s ci=%s years_ok=%s placebo=%s PASS=%s" % (
            r["n"], None if r["D"] is None else "%.4f" % r["D"], r.get("ci95"), r.get("year_sign_ok"),
            r.get("placebo_beaten"), r["pass_"]))
    print("SELECTED:", None if sel is None else (sel["family"], sel["tf"], sel["params"]))


if __name__ == "__main__":
    main()
