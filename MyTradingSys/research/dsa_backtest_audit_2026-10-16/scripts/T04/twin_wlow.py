"""Clean-room twin of opr_weekly_low_round_sweep arm RL (LONG, h=60, k=5). Built from PRE_REG.md only."""
import sys
sys.dont_write_bytecode = True
import csv
import numpy as np
import pandas as pd
from twin_common import *

H = 60
MON0 = 2880   # minute index of Monday 2022-01-03 00:00 UTC (tape starts Saturday 2022-01-01)
WEEK = 10080


def levels(d):
    """Return (round_level, weekly_level) arrays per 1m bar; NaN when not defined."""
    c, l = d["c"], d["l"]
    N = len(c)
    pmin = pd.Series(c).rolling(60).min().shift(1).to_numpy()      # lowest close of the previous 60 bars (excl. current)
    rnd = np.floor(pmin / 1000.0) * 1000.0
    wk = np.full(N, np.nan)
    nfull = (N - MON0) // WEEK
    for w in range(1, nfull):                                       # week w uses full week w-1
        lowprev = l[MON0 + (w - 1) * WEEK: MON0 + w * WEEK].min()
        a, b = MON0 + w * WEEK, min(N, MON0 + (w + 1) * WEEK)
        wk[a:b] = lowprev
    # partial last week keeps the level of the last full week
    if N > MON0 + nfull * WEEK and nfull >= 1:
        wk[MON0 + nfull * WEEK:] = l[MON0 + (nfull - 1) * WEEK: MON0 + nfull * WEEK].min()
    return rnd, wk, pmin


def first_breaks(d, p, strict_cd=False):
    rnd, wk, pmin = levels(d)
    low = d["l"]
    brk_r = (~np.isnan(rnd)) & (low <= rnd * (1 - p))
    brk_w = (~np.isnan(wk)) & (~np.isnan(pmin)) & (pmin >= wk) & (low <= wk * (1 - p))
    ir = cooldown(np.nonzero(brk_r)[0], 60, strict_cd)
    iw = cooldown(np.nonzero(brk_w)[0], 60, strict_cd)
    cand = [(int(i), 0, "weekly", wk[i]) for i in iw] + [(int(i), 1, "round", rnd[i]) for i in ir]
    cand.sort(key=lambda x: (x[0], x[1]))
    keep, last = [], None
    for i, _, fam, L in cand:
        if last is None or (i - last > 60 if strict_cd else i - last >= 60):
            keep.append((i, fam, float(L)))
            last = i
    return keep, len(ir), len(iw)


def run(d=None, p=0.001, k=5, strict_cd=False):
    d = d or load_dev()
    N = len(d["t"])
    ev, nr, nw = first_breaks(d, p, strict_cd)
    c = d["c"]
    rl, ctl = [], []
    for i, fam, L in ev:
        r = next((r for r in range(0, k + 1) if i + r < N and c[i + r] > L), None)
        j = i + r if r is not None else i + k
        e = j + 2
        x = e + H
        if x >= N:
            continue
        pe, px, g, net = trade(d, e, x, +1)
        row = dict(arm="RL" if r is not None else "CTL_RL", break_ts=int(d["t"][i]), family=fam, level=L, side="LONG",
                   decision_ts=int(d["t"][j]) + 60000, entry_ts=int(d["t"][e]), entry_px=pe, exit_ts=int(d["t"][x]), exit_px=px,
                   G=g, net=net, day=e // 1440)
        (rl if r is not None else ctl).append(row)
    return d, rl, ctl, dict(pooled=len(ev), round_only=nr, weekly_only=nw)


def summarise(rl, ctl, d):
    return verdict(np.array([r["G"] for r in rl]), [r["day"] for r in rl], None,
                   np.array([r["G"] for r in ctl]), [r["day"] for r in ctl], mdd_bh(d["c"]))


def write(rows, path):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    d = load_dev()
    for p in (0.0, 0.001, 0.002, 0.003):
        ev, nr, nw = first_breaks(d, p)
        print("p", p, "pooled", len(ev), "round", nr, "weekly", nw)
    d, rl, ctl, cnt = run(d)
    print(cnt, len(rl), len(ctl))
    print(summarise(rl, ctl, d))
    write(rl, __file__.replace("twin_wlow.py", "out/twin_wlow_RL_events.csv"))
