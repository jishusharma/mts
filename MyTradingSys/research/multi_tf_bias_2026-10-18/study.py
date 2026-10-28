"""Multi-TF bias stack study (see RULE.md). Run: python MyTradingSys/research/multi_tf_bias_2026-10-18/study.py
DEV only: 1m bars opening before 2024-07-01. All TF bars are built from 1m."""
import csv
import glob
import math
import os
import sys

import numpy as np

CUT_MS = 1719792000000  # 2024-07-01 00:00 UTC (DEV cut, SOURCED layer_lab/LAB_BLOCKED_2026-10-17.md:17)
KL_DIR = "F:/MTS/data/tom_raw/klines"
MIN = 60000
TFS = {"1h": 60, "4h": 240, "8h": 480, "12h": 720, "1d": 1440}
N = 20            # OURS lookback bars per TF
ER_IMB = 0.30     # OURS
EDGE = 0.15       # OURS (HIGH >= 1-EDGE, LOW <= EDGE)
HOLD_MIN = 480    # OURS exit 8h after decision
COST_BPS = 12.0   # round trip, same as session_flow_context report
STEP_MIN = 240    # OURS decision every 4h


def load_1m(symbol="BTCUSDT", dirpath=KL_DIR):
    """Dict of numpy arrays t,o,h,l,c,v,tbv sorted by t. Rows with open >= CUT_MS are never kept."""
    rows = []
    for f in sorted(glob.glob(os.path.join(dirpath, symbol + "-1m-*.csv"))):
        with open(f, newline="") as fh:
            rd = csv.reader(fh)
            next(rd)
            for r in rd:
                t = int(r[0])
                if t >= CUT_MS:
                    continue
                rows.append((t, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9])))
    rows.sort()
    a = np.array(rows, dtype=float)
    return {k: a[:, i] for i, k in enumerate(["t", "o", "h", "l", "c", "v", "tbv"])}


def check_dev(m):
    if len(m["t"]) and m["t"].max() >= CUT_MS:
        raise ValueError("bar open >= 2024-07-01 (VALIDATION/HOLDOUT) refused")


def build_tf(m, minutes):
    """Aggregate 1m arrays into TF bars aligned to the UTC epoch."""
    check_dev(m)
    L = minutes * MIN
    key = (m["t"] // L).astype(np.int64)
    ks, start, counts = np.unique(key, return_index=True, return_counts=True)
    tp = (m["h"] + m["l"] + m["c"]) / 3.0
    pv = tp * m["v"]
    out = {"t": (ks * L).astype(float), "n": counts}
    out["o"] = m["o"][start]
    out["c"] = m["c"][start + counts - 1]
    out["h"] = np.maximum.reduceat(m["h"], start)
    out["l"] = np.minimum.reduceat(m["l"], start)
    out["v"] = np.add.reduceat(m["v"], start)
    out["tbv"] = np.add.reduceat(m["tbv"], start)
    out["pv"] = np.add.reduceat(pv, start)
    with np.errstate(invalid="ignore", divide="ignore"):
        out["vwap"] = out["pv"] / out["v"]
    out["delta"] = 2 * out["tbv"] - out["v"]
    out["len"] = L
    out["full"] = counts == minutes
    return out


def sgn(x):
    return int(x > 0) - int(x < 0)


def tf_state(bars, t, n=N, er_imb=ER_IMB, edge=EDGE):
    """State of one TF as-of t from bars fully closed at or before t (bar open + len <= t), all complete.
    Returns dict(state, dir, loc, flow) or None."""
    last = int(np.searchsorted(bars["t"] + bars["len"], t, side="right"))
    if last < n:
        return None
    sl = slice(last - n, last)
    if not bars["full"][sl].all():
        return None
    c = bars["c"][sl]
    hi, lo = bars["h"][sl].max(), bars["l"][sl].min()
    path = np.abs(np.diff(c)).sum()
    er = abs(c[-1] - c[0]) / path if path > 0 else 0.0
    pos = (c[-1] - lo) / (hi - lo) if hi > lo else 0.5
    loc = "HIGH" if pos >= 1 - edge else ("LOW" if pos <= edge else "MID")
    return {"state": "IMB" if er >= er_imb else "BAL", "dir": sgn(c[-1] - c[0]), "loc": loc,
            "flow": sgn(bars["delta"][last - 1])}


def bias(st):
    """st: dict tf -> tf_state dict or None. +1 LONG, -1 SHORT, 0 NO BIAS (RULE.md output table)."""
    d, h4, h1 = st.get("1d"), st.get("4h"), st.get("1h")
    if d is None or h4 is None or h1 is None or h1["flow"] == 0:
        return 0
    if d["state"] == "IMB":
        for k in ("4h", "8h", "12h"):
            o = st.get(k)
            if o is None or (o["state"] == "IMB" and o["dir"] == -d["dir"]):
                return 0
        return d["dir"] if (d["dir"] != 0 and h1["flow"] == d["dir"]) else 0
    if d["loc"] == "HIGH":
        return -1 if h1["flow"] < 0 else 0
    if d["loc"] == "LOW":
        return 1 if h1["flow"] > 0 else 0
    if h4["loc"] == "HIGH" and h1["flow"] < 0:
        return -1
    if h4["loc"] == "LOW" and h1["flow"] > 0:
        return 1
    return 0


def last_flow(bars, t):
    last = int(np.searchsorted(bars["t"] + bars["len"], t, side="right"))
    if last < 1 or not bars["full"][last - 1]:
        return 0
    return sgn(bars["delta"][last - 1])


def cluster_stats(x, days):
    """mean, day-clustered SE = sqrt(sum_g (sum_{i in g} (x_i-m))^2)/n, t, n, n_days."""
    x = np.asarray(x, float)
    n = len(x)
    if n == 0:
        return {"n": 0, "days": 0, "mean": float("nan"), "se": float("nan"), "t": float("nan")}
    m = x.mean()
    dd = np.asarray(days)
    ud = sorted(set(days))
    s2 = sum((x[dd == d] - m).sum() ** 2 for d in ud)
    se = math.sqrt(s2) / n
    return {"n": n, "days": len(ud), "mean": float(m), "se": se, "t": float(m / se) if se > 0 else float("nan")}


def run(m, step_min=STEP_MIN, hold_min=HOLD_MIN, cost=COST_BPS):
    tf = {k: build_tf(m, v) for k, v in TFS.items()}
    tt = m["t"]
    first = (int(tt[0]) // (step_min * MIN) + 1) * step_min * MIN
    tmax = int(tt[-1]) - hold_min * MIN
    open_at = {int(t): float(o) for t, o in zip(tt, m["o"])}
    rec = []
    t = first
    while t <= tmax:
        entry, exit_px = open_at.get(t), open_at.get(t + hold_min * MIN)
        if entry is not None and exit_px is not None:
            st = {k: tf_state(tf[k], t) for k in ("1d", "12h", "8h", "4h", "1h")}
            rec.append({"t": t, "day": t // 86400000, "ret": (exit_px / entry - 1) * 1e4, "stack": bias(st),
                        "h1": last_flow(tf["1h"], t), "d1": last_flow(tf["1d"], t)})
        t += step_min * MIN
    return rec, cost


def summarise(rec, cost):
    out = {}
    for name, key in (("STACK", "stack"), ("1h-only", "h1"), ("1D-only", "d1")):
        sel = [r for r in rec if r[key] != 0]
        out[name] = cluster_stats([r[key] * r["ret"] - cost for r in sel], [r["day"] for r in sel])
        out[name]["gross"] = float(np.mean([r[key] * r["ret"] for r in sel])) if sel else float("nan")
    out["ALL-LONG"] = cluster_stats([r["ret"] - cost for r in rec], [r["day"] for r in rec])
    out["ALL-LONG"]["gross"] = float(np.mean([r["ret"] for r in rec])) if rec else float("nan")
    # the stack side always equals the 1h flow side, so a paired diff is 0 by construction; the filter's value is the
    # 1h-only trades the stack removed (stack NO BIAS) against the ones it kept
    for key, name in (("h1", "1h-only"), ("d1", "1D-only")):
        sel = [r for r in rec if r[key] != 0 and r["stack"] == 0]
        out[name + "-filtered-out"] = cluster_stats([r[key] * r["ret"] - cost for r in sel], [r["day"] for r in sel])
        out[name + "-filtered-out"]["gross"] = float(np.mean([r[key] * r["ret"] for r in sel])) if sel else float("nan")
    return out


def main():
    m = load_1m()
    rec, cost = run(m)
    res = summarise(rec, cost)
    print("decisions", len(rec), "first", rec[0]["t"], "last", rec[-1]["t"])
    for k, v in res.items():
        g = ("%.2f" % v["gross"]) if "gross" in v else "-"
        print("%-20s n=%5d days=%4d mean=%8.2f se=%7.2f t=%6.2f gross=%s" % (k, v["n"], v["days"], v["mean"], v["se"], v["t"], g))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "RESULTS.csv"), "w", newline="\n") as fh:
        w = csv.writer(fh)
        w.writerow(["arm", "n", "days", "mean_net_bps", "se", "t", "mean_gross_bps"])
        for k, v in res.items():
            w.writerow([k, v["n"], v["days"], round(v["mean"], 3), round(v["se"], 3), round(v["t"], 3), round(v.get("gross", float("nan")), 3)])
    return 0


if __name__ == "__main__":
    sys.exit(main())
