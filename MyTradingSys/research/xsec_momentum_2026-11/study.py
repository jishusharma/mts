"""study.py - cross-sectional momentum / reversal on Bybit USDT perps, weekly. Rule frozen in PRE_REG.md (committed first).
  python study.py [--cache runtime_data/edge-xsec-momentum-1113] [--out REPORT_DATA.json]
No tuning: every parameter is fixed in PRE_REG. Forward lookups are in fwd_* helpers only."""
import argparse
import bisect
import csv
import datetime
import json
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "backtest"))
import fees as _fees  # noqa: E402

DAY = 86400000
WEEK = 7 * DAY
FEE = _fees.BINANCE_TAKER            # per side, applied to |weight change|
UNIV_N, MIN_UNIV, TURN_DAYS, MIN_BARS = 20, 10, 30, 29
LOOKBACKS = (7, 14, 28)
CELLS = ("MOM-7", "MOM-14", "MOM-28", "REV-7", "LO-7", "LO-14", "LO-28")
SPLITS = {"DEV": ("2020-01-01", "2024-06-30"), "VALIDATION": ("2024-07-01", "2025-06-30"), "RECENT": ("2025-07-01", "2099-01-01")}
BLOCK, NBOOT, SEED, NPLACEBO = 4, 10000, 1113, 200


def ms(d):
    return int(datetime.datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc).timestamp() * 1000)


def split_of(t):
    for k, (a, b) in SPLITS.items():
        if ms(a) <= t < ms(b) + DAY:
            return k
    return None


def quintile_weights(sig, q, mode):
    """sig: {sym: signal}. 'LS' = long top q / short bottom q (each side sums to 1); 'REV' = reverse; 'LO' = top q minus equal-weight universe."""
    order = sorted(sig, key=lambda s: (sig[s], s))
    top, bot = order[-q:], order[:q]
    w = {}
    if mode == "LS":
        for s in top:
            w[s] = w.get(s, 0.0) + 1.0 / q
        for s in bot:
            w[s] = w.get(s, 0.0) - 1.0 / q
    elif mode == "REV":
        for s in bot:
            w[s] = w.get(s, 0.0) + 1.0 / q
        for s in top:
            w[s] = w.get(s, 0.0) - 1.0 / q
    else:
        n = len(order)
        for s in order:
            w[s] = -1.0 / n
        for s in top:
            w[s] += 1.0 / q
    return w


def drift(w, ret):
    """Weights after one week of price moves, as a fraction of the new equity."""
    p = sum(w[s] * ret.get(s, 0.0) for s in w)
    return {s: w[s] * (1 + ret.get(s, 0.0)) / (1 + p) for s in w}


def turnover(w_old, w_new):
    return sum(abs(w_new.get(s, 0.0) - w_old.get(s, 0.0)) for s in set(w_old) | set(w_new))


def week_net(w, w_prev_drifted, ret, fund):
    gross = sum(w[s] * ret[s] for s in w)
    fee = FEE * turnover(w_prev_drifted, w)
    fu = -sum(w[s] * fund.get(s, 0.0) for s in w)
    return gross - fee + fu, gross, fee, fu


def block_boot(x, rng, block=BLOCK, n=NBOOT):
    x = np.asarray(x, float)
    m = len(x)
    if m == 0:
        return {"mean": None, "lo": None, "hi": None, "p": 1.0, "n": 0}
    nb = -(-m // block)
    starts = rng.integers(0, m, size=(n, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % m
    means = x[idx.reshape(n, -1)[:, :m]].mean(axis=1)
    return {"mean": float(x.mean()), "lo": float(np.percentile(means, 2.5)), "hi": float(np.percentile(means, 97.5)),
            "p": float((means <= 0).mean()), "n": m}


def bh(pvals, alpha=0.10):
    """Benjamini-Hochberg: set of keys rejected at FDR alpha."""
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, k = len(items), 0
    for i, (_, p) in enumerate(items, 1):
        if p <= alpha * i / m:
            k = i
    return {key for key, _ in items[:k]}


def fwd_open(opens, t):
    return opens.get(t + WEEK)


def fwd_funding_sum(fl, ts, t):
    a = bisect.bisect_left(ts, t)
    b = bisect.bisect_left(ts, t + WEEK)
    return sum(r for _, r in fl[a:b])


def load(cache):
    data = {}
    for f in os.listdir(cache):
        if f.endswith("USDT.json"):
            d = json.load(open(os.path.join(cache, f)))
            rows = d["daily"]
            data[f[:-5]] = {"o": {r[0]: r[1] for r in rows}, "c": {r[0]: r[4] for r in rows}, "to": {r[0]: r[6] for r in rows},
                            "fund": d["funding"], "fts": [x[0] for x in d["funding"]]}
    return data


def build_weeks(data):
    """Per Monday: universe, signals, weekly returns and funding. Skips weeks lacking MIN_UNIV members or a full forward week."""
    allt = sorted({t for d in data.values() for t in d["o"]})
    last = allt[-1]
    mon = [t for t in allt if datetime.datetime.fromtimestamp(t / 1000, datetime.timezone.utc).weekday() == 0 and t + WEEK <= last]
    weeks = []
    for t in mon:
        cand = []
        for s, d in data.items():
            if t not in d["o"] or fwd_open(d["o"], t) is None:
                continue
            if sum(1 for k in range(1, MIN_BARS + 1) if (t - k * DAY) in d["c"]) < MIN_BARS:
                continue
            tv = [d["to"][t - k * DAY] for k in range(1, TURN_DAYS + 1) if (t - k * DAY) in d["to"]]
            cand.append((sum(tv) / len(tv), s))
        cand.sort(reverse=True)
        uni = [s for _, s in cand[:UNIV_N]]
        if len(uni) < MIN_UNIV:
            continue
        sig = {k: {} for k in LOOKBACKS}
        for s in uni:
            c = data[s]["c"]
            for k in LOOKBACKS:
                c0, c1 = c.get(t - DAY - k * DAY), c.get(t - DAY)
                if c0 and c1:
                    sig[k][s] = c1 / c0 - 1
        ret = {s: fwd_open(data[s]["o"], t) / data[s]["o"][t] - 1 for s in uni}
        fund = {s: fwd_funding_sum(data[s]["fund"], data[s]["fts"], t) for s in uni}
        nofund = sum(1 for s in uni if not data[s]["fund"] or data[s]["fts"][0] > t)
        weeks.append({"t": t, "uni": uni, "sig": sig, "ret": ret, "fund": fund, "nofund": nofund})
    return weeks


CELL_SPEC = {"MOM-7": (7, "LS"), "MOM-14": (14, "LS"), "MOM-28": (28, "LS"), "REV-7": (7, "REV"),
             "LO-7": (7, "LO"), "LO-14": (14, "LO"), "LO-28": (28, "LO")}


def run_cell(weeks, wfun):
    """wfun(week) -> weights. Returns list of (t, net, gross, fee, fund)."""
    out, prev = [], {}
    for wk in weeks:
        w = wfun(wk)
        net, g, fe, fu = week_net(w, prev, wk["ret"], wk["fund"])
        out.append((wk["t"], net, g, fe, fu))
        prev = drift(w, wk["ret"])
    return out


def real_wfun(cell):
    k, mode = CELL_SPEC[cell]

    def f(wk):
        sig = wk["sig"][k]
        return quintile_weights(sig, max(1, len(sig) // 5), mode)
    return f


def placebo_wfun(mode, rng):
    def f(wk):
        uni = list(wk["uni"])
        fake = {s: rng.random() for s in uni}
        return quintile_weights(fake, max(1, len(uni) // 5), "LS" if mode == "LS" else "LO")
    return f


def by_split(rows):
    r = {k: [] for k in SPLITS}
    for t, net, *_ in rows:
        r[split_of(t)].append(net)
    return r


def regime_mix(data, weeks):
    b = data["BTCUSDT"]["o"]
    mix = {k: [0, 0, 0] for k in SPLITS}
    for wk in weeks:
        t = wk["t"]
        if (t + WEEK) not in b or t not in b:
            continue
        r = b[t + WEEK] / b[t] - 1
        mix[split_of(t)][0 if r > 0.05 else (1 if r < -0.05 else 2)] += 1
    return mix


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="runtime_data/edge-xsec-momentum-1113")
    ap.add_argument("--out", default=os.path.join(HERE, "REPORT_DATA.json"))
    ap.add_argument("--regime-only", action="store_true")
    a = ap.parse_args()
    data = load(a.cache)
    weeks = build_weeks(data)
    mix = regime_mix(data, weeks)
    if a.regime_only:
        for k, v in mix.items():
            print(k, "weeks", sum(v), "up %d down %d range %d" % tuple(v))
        return 0
    rng = np.random.default_rng(SEED)
    res = {"weeks": len(weeks), "regime_mix": mix, "cells": {}, "placebo": {}}
    for cell in CELLS:
        rows = run_cell(weeks, real_wfun(cell))
        res["cells"][cell] = {}
        for k in SPLITS:
            sub = [r for r in rows if split_of(r[0]) == k]
            st = block_boot([r[1] for r in sub], rng)
            for name, j in (("gross", 2), ("fee", 3), ("fund", 4)):
                st[name] = float(np.mean([r[j] for r in sub])) if sub else None
            res["cells"][cell][k] = st
    for mode in ("LS", "LO"):
        pr = random.Random(SEED)
        means = {k: [] for k in SPLITS}
        for _ in range(NPLACEBO):
            for k, v in by_split(run_cell(weeks, placebo_wfun(mode, pr))).items():
                means[k].append(float(np.mean(v)) if v else 0.0)
        res["placebo"][mode] = {k: {"p5": float(np.percentile(v, 5)), "mean": float(np.mean(v)), "p95": float(np.percentile(v, 95))}
                                for k, v in means.items()}
    sig = bh({c: res["cells"][c]["VALIDATION"]["p"] for c in CELLS})
    for c in CELLS:
        v = res["cells"][c]["VALIDATION"]
        pl = res["placebo"]["LO" if c.startswith("LO") else "LS"]["VALIDATION"]["p95"]
        res["cells"][c]["bh"] = c in sig
        res["cells"][c]["pass"] = bool(v["mean"] is not None and v["mean"] > 0 and v["lo"] > 0 and v["n"] >= 30 and v["mean"] > pl and c in sig)
    json.dump(res, open(a.out, "w"), indent=1)
    with open(os.path.join(HERE, "universe_by_week.csv"), "w", newline="") as f:
        w = csv.writer(f)
        for wk in weeks:
            w.writerow([datetime.datetime.fromtimestamp(wk["t"] / 1000, datetime.timezone.utc).strftime("%Y-%m-%d")] + wk["uni"])
    print(json.dumps({c: {k: res["cells"][c][k] for k in ("pass", "bh")} for c in CELLS}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
