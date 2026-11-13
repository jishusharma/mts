"""extreme_confirm_template_2026-11 runner. PRE_REG.md frozen first. Outputs cells.csv."""
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import core  # noqa: E402
from MyTradingSys.backtest.layers.krown.krown_core import ema, rsi  # noqa: E402
from MyTradingSys.backtest.bigtrade.bigmoves import atr as atr_fn  # noqa: E402
from MyTradingSys.backtest.layers.alerts.live_bb_top_reversal import bollinger  # noqa: E402
from MyTradingSys.backtest.layers.kurisko.stoch_core import stoch_line  # noqa: E402

DATA = core.REPO / "runtime_data" / "edge-extreme-confirm-template-1113"
COINS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
H, DAY = core.HOUR, 86400000
DEV_END, VAL_END = 1719792000000, 1751328000000   # 2024-07-01, 2025-07-01
BUCKETS = ("above", "between", "below")
KS = (0.25, 1.0)
B, SEED, NPLC = 2000, 1113, 500
NAN = float("nan")


def split_of(t):
    return "DEV" if t < DEV_END else "VALIDATION" if t < VAL_END else "RECENT"


def nanify(x):
    return [NAN if v is None else v for v in x]


def prep(coin):
    k = json.load(open(DATA / (coin + "_1h.json")))
    t = [r[0] for r in k]
    o, h, l, c = ([r[j] for r in k] for j in (1, 2, 3, 4))
    n = len(c)
    a = [float(x) for x in atr_fn(h, l, c)]
    days = {}
    for i, ti in enumerate(t):
        days.setdefault(ti // DAY, []).append(i)
    ds = [d for d in sorted(days) if len(days[d]) == 24]
    dc = [c[days[d][-1]] for d in ds]
    de_arr = np.array([(d + 1) * DAY for d in ds])
    e20, e50 = ema(dc, 20), ema(dc, 50)
    kk = np.searchsorted(de_arr, np.array(t) + H, side="right") - 1
    bucket = [None] * n
    d20 = [NAN] * n
    for i in range(n):
        j = kk[i]
        if j < 0 or e50[j] is None:
            continue
        x = dc[j]
        bucket[i] = "above" if x > e20[j] and x > e50[j] else "below" if x < e20[j] and x < e50[j] else "between"
        d20[i] = e20[j]
    f4 = {}
    for i, ti in enumerate(t):
        f4.setdefault(ti // (4 * H), []).append(i)
    fs = [q for q in sorted(f4) if len(f4[q]) == 4]
    c4 = [c[f4[q][-1]] for q in fs]
    r4 = nanify(rsi(c4, 14))
    k4 = stoch_line(r4, r4, r4, 14, 1, 3)
    e4 = np.array([(q + 1) * 4 * H for q in fs])
    j4 = np.searchsorted(e4, np.array(t) + H, side="right") - 1
    K4 = [k4[j] if j >= 0 else NAN for j in j4]
    r1 = nanify(rsi(c, 14))
    K1 = stoch_line(r1, r1, r1, 14, 1, 3)
    up, lo = bollinger(c)
    e200 = ema(c, 200)
    fj = json.load(open(DATA / (coin + "_fund.json")))
    ft = np.array([r[0] for r in fj])
    cs = np.concatenate([[0.0], np.cumsum(np.array([r[1] for r in fj]))])
    tt = np.array(t)

    def fund(e, xj):
        lo_i = np.searchsorted(ft, tt[e], side="right")
        hi_i = np.searchsorted(ft, tt[xj] + H, side="right")
        return float(cs[hi_i] - cs[lo_i])
    return dict(t=t, o=o, h=h, l=l, c=c, a=a, bucket=bucket, d20=d20, K1=K1, K4=K4, up=up, lo=lo, e200=e200, fund=fund, n=n)


def readings(D):
    n, c, a = D["n"], D["c"], D["a"]
    out = {}
    m_a = {1: [NAN] * n, -1: [NAN] * n}
    m_b1 = {1: [NAN] * n, -1: [NAN] * n}
    m_b2 = {1: [NAN] * n, -1: [NAN] * n}
    for i in range(n):
        ai = a[i]
        if not (ai == ai and ai > 0):
            continue
        if D["lo"][i] is not None:
            m_a[1][i] = (D["lo"][i] - c[i]) / ai
            m_a[-1][i] = (c[i] - D["up"][i]) / ai
        if D["e200"][i] is not None:
            m_b1[1][i] = (D["e200"][i] - c[i]) / ai
            m_b1[-1][i] = -m_b1[1][i]
        if D["d20"][i] == D["d20"][i]:
            m_b2[1][i] = (D["d20"][i] - c[i]) / ai
            m_b2[-1][i] = -m_b2[1][i]
    out["a"], out["b1"], out["b2"] = m_a, m_b1, m_b2
    K1, K4 = D["K1"], D["K4"]
    out["c"] = {1: [K1[i] < 5 and K4[i] < 20 for i in range(n)], -1: [K1[i] > 95 and K4[i] > 80 for i in range(n)]}
    h, l = D["h"], D["l"]
    out["e"] = {1: [False] * n, -1: [False] * n}
    for i in range(1, n):
        ap = a[i - 1]
        if not (ap == ap and ap > 0) or h[i] == l[i]:
            continue
        if h[i] - l[i] >= 3 * ap:
            pos = (c[i] - l[i]) / (h[i] - l[i])
            out["e"][1][i] = pos <= 0.25
            out["e"][-1][i] = pos >= 0.75
    out["runs"] = {1: core.runs(c, False), -1: core.runs(c, True)}
    return out


def build():
    coins = {}
    for cn in COINS:
        D = prep(cn)
        R = readings(D)
        n = D["n"]
        ok = [D["bucket"][i] is not None and D["a"][i] == D["a"][i] and D["e200"][i] is not None and D["lo"][i] is not None
              and D["K1"][i] == D["K1"][i] and D["K4"][i] == D["K4"][i] for i in range(n)]
        dev = [i for i in range(n) if ok[i] and D["t"][i] + H <= DEV_END]
        conds = {}
        for s in (1, -1):
            for nm in ("a", "b1", "b2"):
                v = np.array([R[nm][s][i] for i in dev])
                v = v[~np.isnan(v)]
                for p in (99, 95):
                    thr = float(np.percentile(v, p)) if len(v) else NAN
                    conds[(nm + "_" + str(p), s)] = [ok[i] and R[nm][s][i] == R[nm][s][i] and R[nm][s][i] >= thr for i in range(n)]
            conds[("c", s)] = [ok[i] and R["c"][s][i] for i in range(n)]
            conds[("e", s)] = [ok[i] and R["e"][s][i] for i in range(n)]
            rl = np.array([R["runs"][s][i] for i in dev])
            N = int(math.ceil(np.percentile(rl, 99))) if len(rl) else 99
            conds[("d", s)] = [ok[i] and R["runs"][s][i] == N for i in range(n)]
            conds[("dN", s)] = N
        trades = {}
        c = D["c"]
        for s in (1, -1):
            for k in KS:
                arr = [None] * n
                for i in range(n - 3 - core.HOLD):
                    if not ok[i]:
                        continue
                    if (c[i + 1] > c[i]) if s > 0 else (c[i + 1] < c[i]):
                        r = core.fwd_trade(D["o"], D["h"], D["l"], c, i, s, k, D["a"][i], D["fund"])
                        if r:
                            arr[i] = r
                trades[(s, k)] = arr
        coins[cn] = dict(D=D, conds=conds, trades=trades)
        print(cn, n, "run N long/short", conds[("dN", 1)], conds[("dN", -1)], flush=True)
    return coins


def pick(cd, cn, key, s, bucket, k):
    D = cd[cn]["D"]
    cond = cd[cn]["conds"][(key, s)]
    arr = cd[cn]["trades"][(s, k)]
    out, free = [], -1
    for i in range(D["n"]):
        if not cond[i] or D["bucket"][i] != bucket or arr[i] is None:
            continue
        e = i + 2
        if e <= free:
            continue
        ret, xj = arr[i]
        free = xj
        out.append((i, D["t"][e] // DAY, ret, split_of(D["t"][i] + H)))
    return out


def boot(days, rets, rng):
    if len(rets) == 0:
        return NAN, NAN, NAN, NAN
    ud, inv = np.unique(days, return_inverse=True)
    sm = np.bincount(inv, weights=rets)
    ct = np.bincount(inv).astype(float)
    idx = rng.integers(0, len(ud), size=(B, len(ud)))
    bm = sm[idx].sum(1) / ct[idx].sum(1)
    mean = float(np.sum(rets) / len(rets))
    return mean, float(np.percentile(bm, 2.5)), float(np.percentile(bm, 97.5)), (1 + float((bm <= 0).sum())) / (B + 1)


def main():
    cd = build()
    rng = np.random.default_rng(SEED)
    cells = [(k, s) for k in ("a_99", "a_95", "b1_99", "b1_95", "b2_99", "b2_95") for s in (1, -1)] + \
            [(k, s) for k in ("c", "d", "e") for s in (1, -1)]
    assert len(cells) * 3 == 54
    rows = []
    for key, s in cells:
        for bk in BUCKETS:
            res = {k: {cn: pick(cd, cn, key, s, bk, k) for cn in COINS} for k in KS}

            def sel(k, sp, coins=COINS):
                return [x for cn in coins for x in res[k][cn] if x[3] == sp]
            dm = {k: (np.mean([x[2] for x in sel(k, "DEV")]) if sel(k, "DEV") else -9) for k in KS}
            kb = 1.0 if dm[1.0] >= dm[0.25] else 0.25
            row = dict(cond=key, side="L" if s > 0 else "S", bucket=bk, k=kb)
            for sp in ("DEV", "VALIDATION", "RECENT"):
                xs = sel(kb, sp)
                mean, lo, hi, p = boot(np.array([x[1] for x in xs]), np.array([x[2] for x in xs]), rng)
                row.update({sp + "_n": len(xs), sp + "_mean": mean, sp + "_lo": lo, sp + "_hi": hi, sp + "_p": p})
                cnt = {cn: len([x for x in res[kb][cn] if x[3] == sp]) for cn in COINS}
                pools = {}
                for cn in COINS:
                    D = cd[cn]["D"]
                    cond = cd[cn]["conds"][(key, s)]
                    arr = cd[cn]["trades"][(s, kb)]
                    pools[cn] = np.array([arr[i][0] for i in range(D["n"]) if arr[i] is not None and not cond[i]
                                          and D["bucket"][i] == bk and split_of(D["t"][i] + H) == sp])
                tot = sum(cnt.values())
                if tot > 0 and all(len(pools[cn]) > 0 or cnt[cn] == 0 for cn in COINS):
                    pms = np.zeros(NPLC)
                    for cn in COINS:
                        if cnt[cn]:
                            pms += rng.choice(pools[cn], size=(NPLC, cnt[cn]), replace=True).sum(1)
                    pms /= tot
                    row[sp + "_plc_mean"] = float(pms.mean())
                    row[sp + "_plc_p95"] = float(np.percentile(pms, 95))
                else:
                    row[sp + "_plc_mean"] = row[sp + "_plc_p95"] = NAN
            for sp in ("DEV", "VALIDATION", "RECENT"):
                bt = sel(kb, sp, ["BTC"])
                row["BTC_" + sp + "_n"] = len(bt)
                row["BTC_" + sp + "_mean"] = float(np.mean([x[2] for x in bt])) if bt else NAN
            rows.append(row)
    m = len(rows)
    ps = sorted((r["VALIDATION_p"] if r["VALIDATION_n"] >= 30 else 9.0, i) for i, r in enumerate(rows))
    cut = 0
    for rank, (p, i) in enumerate(ps, 1):
        if p <= 0.10 * rank / m:
            cut = rank
    bh = {i for rank, (p, i) in enumerate(ps, 1) if rank <= cut}
    for i, r in enumerate(rows):
        r["BH"] = i in bh
        r["under"] = r["VALIDATION_n"] < 30
        r["passV"] = bool(r["VALIDATION_n"] >= 30 and r["VALIDATION_mean"] > 0 and r["VALIDATION_lo"] > 0
                          and r["VALIDATION_mean"] > r["VALIDATION_plc_p95"] and r["BH"])
        r["passVR"] = bool(r["passV"] and r["RECENT_n"] >= 30 and r["RECENT_mean"] > 0 and r["RECENT_lo"] > 0)
    with open(HERE / "cells.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print("cells", m, "BH", len(bh), "passV", sum(r["passV"] for r in rows), "passVR", sum(r["passVR"] for r in rows),
          "underpowered", sum(r["under"] for r in rows))
    best = sorted(rows, key=lambda r: -(r["VALIDATION_mean"] if r["VALIDATION_n"] >= 30 else -9))[:8]
    for r in best:
        print(r["cond"], r["side"], r["bucket"], r["k"], "n", r["VALIDATION_n"], "mean %.3f%%" % (100 * r["VALIDATION_mean"]),
              "lo %.3f" % (100 * r["VALIDATION_lo"]), "p %.3f" % r["VALIDATION_p"], "plc95 %.3f" % (100 * r["VALIDATION_plc_p95"]),
              "REC n", r["RECENT_n"], "%.3f" % (100 * r["RECENT_mean"]))


if __name__ == "__main__":
    main()
