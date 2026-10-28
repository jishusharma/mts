"""B141 Stage 1 (coverage only, no outcome data) of PRE_REG_HTF_REPLACE_2026-10-07.md section 5.1.

For each of the 28 declared cells (section 4) and each close of the cell's TF (4H: N=240, 1D: N=1440) over the
hist+dev period (2022-01-01 .. 2026-06-25 UTC), count the closes whose window is balanced. Coverage = balanced / valid.
A cell outside [15%, 85%] is dropped (section 5.1). No return, forward range or flag-vs-future value is computed.

Family A reproduces signals.balance(): R <= k*sqrt(N)*ATR_N and |c - poc| <= b*R, poc = centre of the max-volume 50 USD
bin of the 10 USD hlc3 kline approximation (same as htf_context_live.klines_to_bars + B_PROF). Family B: ER <= e.
Usage: python research/loose_code/b141_htf_stage1.py [--klines DIR] [--out FILE.json]
"""
import argparse
import csv
import glob
import json
import math
import os
from datetime import datetime, timezone

import numpy as np

MIN_MS = 60000
HIST_START = "2022-01-01"
DEV_END = "2026-06-25"          # holdout 2026-06-26.. is NOT read here
TFS = {"4H": (240, 4 * 3600 * 1000), "1D": (1440, 24 * 3600 * 1000)}
K_GRID = (0.8, 1.0, 1.25, 1.5, 2.0)
B_GRID = (0.25, 0.5)
E_GRID = (0.05, 0.10, 0.15, 0.25)
BIN = 50.0
COV_LO, COV_HI = 0.15, 0.85


def _ms(day):
    return int(datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)


def load_klines(folder, start=HIST_START, end=DEV_END):
    """-> dict of numpy arrays t,h,l,c,v for t in [start, end+1d), ascending, deduplicated."""
    lo, hi = _ms(start), _ms(end) + 86400000
    rows = {}
    for f in sorted(glob.glob(os.path.join(folder, "BTCUSDT-1m-*.csv"))):
        with open(f, newline="") as fh:
            for r in csv.DictReader(fh):
                t = int(r["open_time"])
                if lo <= t < hi:
                    rows[t] = (float(r["high"]), float(r["low"]), float(r["close"]), float(r["volume"]))
    ts = sorted(rows)
    a = np.array([rows[t] for t in ts], dtype=float).reshape(-1, 4)
    return {"t": np.array(ts, dtype=np.int64), "h": a[:, 0], "l": a[:, 1], "c": a[:, 2], "v": a[:, 3]}


def window_stats(K, i, N):
    """Stats of window [i-N+1, i] using bar i-N for the previous close; None when not contiguous (N+1 bars)."""
    if i < N or K["t"][i] - K["t"][i - N] != N * MIN_MS:
        return None
    s = slice(i - N + 1, i + 1)
    h, l, c = K["h"][s], K["l"][s], K["c"][s]
    pc = K["c"][i - N:i]
    tr = np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))
    atr = float(tr.mean())
    H, L = float(h.max()), float(l.min())
    hlc3 = (h + l + c) / 3.0
    kfp = np.floor(hlc3 / 10.0 + 1e-9) * 10.0              # 10 USD fp bin of the bar (klines_to_bars)
    kb = np.floor(kfp / BIN + 1e-9).astype(np.int64)
    kb -= kb.min()
    vol = np.bincount(kb, weights=K["v"][s])
    lo_bin = (np.floor(kfp / BIN + 1e-9).min()) * BIN
    poc = float(lo_bin + int(np.argmax(vol)) * BIN + BIN / 2.0)   # argmax -> first max = lower bin on ties
    path = float(np.abs(np.diff(K["c"][i - N:i + 1])).sum())
    er = abs(float(K["c"][i] - K["c"][i - N])) / path if path > 0 else None
    return {"H": H, "L": L, "R": H - L, "atr": atr, "poc": poc, "c": float(K["c"][i]), "er": er}


def cells():
    out = []
    for tf in TFS:
        for k in K_GRID:
            for b in B_GRID:
                out.append(("A", tf, {"k": k, "b": b}))
        for e in E_GRID:
            out.append(("B", tf, {"e": e}))
    return out


def is_balanced(fam, par, st, N):
    if fam == "A":
        return st["R"] <= par["k"] * math.sqrt(N) * st["atr"] and abs(st["c"] - st["poc"]) <= par["b"] * st["R"]
    return st["er"] is not None and st["er"] <= par["e"]


def run(K):
    res = []
    stats = {}
    for tf, (N, step) in TFS.items():
        lst = []
        for j in range(len(K["t"])):                       # bar i whose close lands on a TF boundary
            if (K["t"][j] + MIN_MS) % step == 0:
                st = window_stats(K, j, N)
                if st is not None:
                    lst.append(st)
        stats[tf] = lst
    for fam, tf, par in cells():
        N = TFS[tf][0]
        lst = stats[tf]
        nb = sum(1 for st in lst if is_balanced(fam, par, st, N))
        cov = nb / len(lst) if lst else None
        res.append({"family": fam, "tf": tf, "params": par, "valid": len(lst), "balanced": nb, "coverage": cov,
                    "kept": cov is not None and COV_LO <= cov <= COV_HI})
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--klines", default="F:/MTS/data/tom_raw/klines")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "b141_stage1_result.json"))
    a = ap.parse_args()
    K = load_klines(a.klines)
    res = run(K)
    doc = {"period": [HIST_START, DEV_END], "bars": int(len(K["t"])), "n_cells": len(res), "cells": res}
    with open(a.out, "w", newline="\n") as fh:
        json.dump(doc, fh, indent=1)
    for r in res:
        print(r["family"], r["tf"], r["params"], "valid=%d bal=%d cov=%s %s" % (
            r["valid"], r["balanced"], "n/a" if r["coverage"] is None else "%.3f" % r["coverage"],
            "KEEP" if r["kept"] else "drop"))


if __name__ == "__main__":
    main()
