"""T04 clean-room twin: shared loader and statistics. Written from the two PRE_REGs only (no study.py)."""
import sys
sys.dont_write_bytecode = True
import glob
import os
import numpy as np

KL_DIR = "F:/MTS/data/tom_raw/klines"
DEV_END_MS = 1719792000000   # 2024-07-01 00:00:00 UTC
T0_MS = 1640995200000        # 2022-01-01 00:00:00 UTC
COST = 0.14                  # percent round trip
FUND = 0.01                  # percent per settlement crossed (flat 1 bp, PRE_REG s.1)


def load_dev(kl_dir=KL_DIR):
    """Own loader: BTCUSDT 1m monthly files 2022-01..2024-06, dedup on open_time, DEV only, contiguity asserted."""
    rows = []
    for y in (2022, 2023, 2024):
        for m in range(1, 13):
            p = "%s/BTCUSDT-1m-%d-%02d.csv" % (kl_dir, y, m)
            if not os.path.exists(p):
                continue
            a = np.loadtxt(p, delimiter=",", skiprows=1, usecols=(0, 1, 2, 3, 4, 5, 9))
            rows.append(a)
    a = np.vstack(rows)
    a = a[a[:, 0] < DEV_END_MS]
    _, ix = np.unique(a[:, 0], return_index=True)
    a = a[ix]
    t = a[:, 0].astype(np.int64)
    assert t[0] == T0_MS and np.all(np.diff(t) == 60000), "gap or misalignment in 1m tape"
    return dict(t=t, o=a[:, 1], h=a[:, 2], l=a[:, 3], c=a[:, 4], v=a[:, 5], tbv=a[:, 6])


def agg(k, d):
    """Aggregate 1m bars into k-minute bars aligned to UTC (tape starts at 00:00, so index blocks align)."""
    n = len(d["t"]) // k * k
    r = lambda x: x[:n].reshape(-1, k)
    return dict(o=r(d["o"])[:, 0], h=r(d["h"]).max(1), l=r(d["l"]).min(1), c=r(d["c"])[:, -1],
                v=r(d["v"]).sum(1), tbv=r(d["tbv"]).sum(1))


SMA_EXACT = True   # False reproduces twin v0 (running cumulative-sum SMA, drifts ~1e-9 over 2.6M bars: twin bug T1)


def sma(x, n):
    out = np.full(len(x), np.nan)
    if SMA_EXACT:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(x, n).mean(axis=1)
        return out
    cs = np.cumsum(np.insert(x, 0, 0.0))
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def bb(c, n=20, k=2.0):
    mid = sma(c, n)
    sd = np.full(len(c), np.nan)
    for i in range(n - 1, len(c)):
        sd[i] = np.std(c[i - n + 1:i + 1])   # population SD
    return mid, mid + k * sd, mid - k * sd


def rsi_wilder(c, n=14):
    """FORMULAS.md s.1: SMA seed over first n deltas at index n, then Wilder smoothing."""
    out = np.full(len(c), np.nan)
    d = np.diff(c)
    g = np.maximum(d, 0.0)
    ls = np.maximum(-d, 0.0)
    ag = g[:n].mean()
    al = ls[:n].mean()
    def put(i, ag, al):
        if al == 0:
            out[i] = 100.0 if ag > 0 else 50.0
        else:
            out[i] = 100 - 100 / (1 + ag / al)
    put(n, ag, al)
    for i in range(n + 1, len(c)):
        ag = (ag * (n - 1) + g[i - 1]) / n
        al = (al * (n - 1) + ls[i - 1]) / n
        put(i, ag, al)
    return out


def cooldown(idx, gap, strict=False):
    """Keep an event if it is at least gap (strict: more than gap) index units after the previously kept one."""
    keep, last = [], None
    for i in idx:
        if last is None or (i - last > gap if strict else i - last >= gap):
            keep.append(i)
            last = i
    return np.array(keep, dtype=np.int64)


def funding_count(e_min, x_min):
    """Settlements at 00/08/16 UTC (minute index multiple of 480) with e < s <= x."""
    return x_min // 480 - e_min // 480


def trade(d, e, x, side):
    """Fill at open of 1m bar e, exit at open of 1m bar x. Returns entry px, exit px, G (after funding), net (percent)."""
    pe, px = d["o"][e], d["o"][x]
    gross = side * (px - pe) / pe * 100.0
    g = gross - FUND * funding_count(e, x)
    return pe, px, g, g - COST


def day_cluster_se(vals, days):
    m = vals.mean()
    n = len(vals)
    s = {}
    for v, dd in zip(vals, days):
        s[dd] = s.get(dd, 0.0) + (v - m)
    return np.sqrt(sum(x * x for x in s.values())) / n


def mdd_sum(net):
    cs = np.cumsum(net)
    peak = np.maximum.accumulate(np.insert(cs, 0, 0.0))[1:]
    return float((peak - cs).max())


def mdd_bh(c):
    peak = np.maximum.accumulate(c)
    return float(((peak - c) / peak * 100).max())


def verdict(G, days, ent_t, Gc, days_c, bh):
    """PRE_REG s.4 pass rule. G/Gc after funding; events ordered by time."""
    n = len(G)
    mean = G.mean()
    se = day_cluster_se(G, days)
    t_cost = (mean - COST) / se
    out = dict(n=n, mean_G=mean, se=se, t_cost=t_cost, mde=2.8 * se)
    if len(Gc):
        dd = mean - Gc.mean()
        sec = day_cluster_se(Gc, days_c)
        sed = float(np.hypot(se, sec))
        out.update(n_ctrl=len(Gc), mean_ctrl=Gc.mean(), diff=dd, t_diff=dd / sed)
    else:
        out.update(n_ctrl=0, mean_ctrl=np.nan, diff=np.nan, t_diff=np.nan)
    out["mdd_arm"] = mdd_sum(G - COST)
    out["mdd_bh"] = bh
    if n < 200:
        out["verdict"] = "INCONCLUSIVE"
    else:
        ok = (mean >= COST and t_cost >= 2 and out["diff"] >= 0.05 and out["t_diff"] >= 2
              and out["mdd_arm"] <= bh)
        out["verdict"] = "PASS" if ok else "FAIL"
    return out
