"""wlow_bounce_bbrsi60 study, DEV ONLY (bars opened before 2024-07-01). Rules: PRE_REG.md in this folder (read it first).

  python -m MyTradingSys.research.wlow_bounce_bbrsi60_2026-10-16.study --counts   # counts + unconditional SD only (no event outcomes)
  python -m MyTradingSys.research.wlow_bounce_bbrsi60_2026-10-16.study --run      # full outcome run, writes RESULT.md + events.csv

(The folder name has a dash-free date prefix issue for -m; run it as `python MyTradingSys/research/wlow_bounce_bbrsi60_2026-10-16/study.py --run`
from the repo root.) Loader guard: a bar with open >= 2024-07-01 is never read.
"""
import argparse
import csv
import glob
import math
import os
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, REPO)
from MyTradingSys.backtest.layers.wlow_bounce import detector as D  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
KLINES = "F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv"
DEV_END_MS = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)   # exclusive: VALIDATION starts here
C = 0.14          # % round trip (gross-effect PRE_REG section 1)
HORIZONS = (1, 4, 12, 24)
N_BASE_B = 20     # random same-hour draws per event
SEED = 20261016
VARIANTS = [
    ("V1_primary", dict()),
    ("V2_roll168", dict(week_mode="roll168")),
    ("V3_K3", dict(K=3)),
    ("V4_K6", dict(K=6)),
]


def load_dev():
    """1m rows (t, o, h, l, c, v, tbv) for files whose month is <= 2024-06 and bars < DEV_END_MS."""
    rows = []
    for f in sorted(glob.glob(KLINES)):
        ym = os.path.basename(f)[len("BTCUSDT-1m-"):-4]
        if ym > "2024-06":
            continue
        with open(f, newline="") as fh:
            rd = csv.reader(fh)
            next(rd)
            for r in rd:
                t = int(r[0])
                if t >= DEV_END_MS:
                    continue
                rows.append((t, float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]), float(r[9])))
    rows.sort()
    return rows


def to_hourly(rows):
    by = defaultdict(list)
    for r in rows:
        by[r[0] // D.HOUR_MS * D.HOUR_MS].append(r)
    out, dropped = [], 0
    for h in sorted(by):
        g = by[h]
        if len(g) != 60:
            dropped += 1
            continue
        out.append({"t": h, "o": g[0][1], "h": max(x[2] for x in g), "l": min(x[3] for x in g), "c": g[-1][4],
                    "v": sum(x[5] for x in g), "tbv": sum(x[6] for x in g)})
    return out, dropped


def day(t_ms):
    return t_ms // 86_400_000


def mean(x):
    return sum(x) / len(x)


def cluster_se(vals, days):
    """Day-clustered SE of the mean: sqrt(sum_d S_d^2) / n, S_d = sum over the day's items of (x - mean)."""
    n = len(vals)
    if n < 2:
        return float("nan")
    m = mean(vals)
    s = defaultdict(float)
    for v, d in zip(vals, days):
        s[d] += v - m
    return math.sqrt(sum(z * z for z in s.values())) / n


def iso(t_ms):
    return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def outcome(candles, m1_idx, m1, t):
    """Forward outcome of a trigger at 1h bar index t (entry = open of bar t+1). None if the 24 h forward window is missing."""
    n = len(candles)
    if t + 24 >= n or candles[t + 24]["t"] - candles[t + 1]["t"] != 23 * D.HOUR_MS:
        return None
    e = candles[t + 1]["o"]
    r = {f"R{h}": (candles[t + h]["c"] / e - 1) * 100 for h in HORIZONS}
    seg = candles[t + 1:t + 25]
    r["MFE"] = (max(x["h"] for x in seg) / e - 1) * 100
    r["MAE"] = (min(x["l"] for x in seg) / e - 1) * 100
    # first touch of +-1 % on 1m bars, ambiguous 1m bar (both touched) counted as adverse-first for BOTH directions' readouts
    i0 = m1_idx.get(candles[t + 1]["t"])
    first = "none"
    if i0 is not None:
        up, dn = e * 1.01, e * 0.99
        for q in range(i0, min(i0 + 1440, len(m1))):
            hi, lo = m1[q][2], m1[q][3]
            if hi >= up and lo <= dn:
                first = "both"
                break
            if hi >= up:
                first = "up"
                break
            if lo <= dn:
                first = "dn"
                break
    r["first"] = first
    return r


def group_stats(vals, days):
    n = len(vals)
    return {"n": n, "mean": mean(vals) if n else float("nan"), "se": cluster_se(vals, days) if n > 1 else float("nan")}


def diff_stats(a, b):
    """a, b: (vals, days). DIFF = mean_a - mean_b, independent groups, day-clustered SE each."""
    sa, sb = group_stats(*a), group_stats(*b)
    if sa["n"] < 2 or sb["n"] < 2:
        return {"diff": float("nan"), "se": float("nan"), "t": float("nan"), "lo": float("nan"), "hi": float("nan"), "mde": float("nan")}
    d = sa["mean"] - sb["mean"]
    se = math.sqrt(sa["se"] ** 2 + sb["se"] ** 2)
    return {"diff": d, "se": se, "t": d / se if se > 0 else float("nan"), "lo": d - 1.96 * se, "hi": d + 1.96 * se, "mde": 2.8 * se}


def baseline_a(candles, bb, rsi, p, exclude_break_bars=24):
    """Hold condition without a weekly-low break in the previous 24 bars; cooldown COOLDOWN bars between baseline events."""
    W = D.weekly_low_series(candles, p["week_mode"])
    brk = [W[i] is not None and candles[i]["l"] < W[i] for i in range(len(candles))]
    out, last = [], -10**9
    for t in range(len(candles)):
        if t - last < p["COOLDOWN"]:
            continue
        if any(brk[max(0, t - exclude_break_bars):t + 1]):
            continue
        if D.hold_ok(candles, bb, rsi, t, p):
            out.append(t)
            last = t
    return out


def baseline_b(candles, ev_triggers, rng, p):
    """For each event, N_BASE_B random bars with the same UTC hour-of-day, at least HMAX bars away from every event trigger."""
    hours = defaultdict(list)
    for i, x in enumerate(candles):
        hours[(x["t"] // D.HOUR_MS) % 24].append(i)
    out = []
    for t in ev_triggers:
        pool = [i for i in hours[(candles[t]["t"] // D.HOUR_MS) % 24] if all(abs(i - e) > p["HMAX"] for e in ev_triggers)]
        out += rng.sample(pool, min(N_BASE_B, len(pool)))
    return out


def build(candles, m1_idx, m1, over):
    p = dict(D.PARAMS)
    p.update(over)
    bb, rsi = D.indicators(candles, p)
    evs = D.find_events(candles, p, ind=(bb, rsi))
    return p, bb, rsi, evs


def table_row(label, vals, days):
    s = group_stats(vals, days)
    return s


def fmt(x, nd=3):
    return "nan" if x != x else f"{x:.{nd}f}"


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--counts", action="store_true")
    g.add_argument("--run", action="store_true")
    a = ap.parse_args()
    rows = load_dev()
    assert rows[-1][0] < DEV_END_MS, "VALIDATION/HOLDOUT bar read"
    candles, dropped = to_hourly(rows)
    m1 = rows
    m1_idx = {r[0]: i for i, r in enumerate(m1)}
    print(f"DEV 1m rows {len(rows)}, 1h bars {len(candles)}, hours dropped (missing 1m) {dropped}, first {iso(candles[0]['t'])}, last {iso(candles[-1]['t'])}")

    if a.counts:
        closes = [x["c"] for x in candles]
        r4 = [(closes[i + 4] / closes[i] - 1) * 100 for i in range(len(closes) - 4)]
        sd = (sum((x - mean(r4)) ** 2 for x in r4) / (len(r4) - 1)) ** 0.5
        print(f"UNCONDITIONAL 4h return SD over all DEV bars (not event-conditioned): {sd:.4f} %")
        for name, over in VARIANTS:
            p, bb, rsi, evs = build(candles, m1_idx, m1, over)
            st = defaultdict(int)
            for e in evs:
                st[e["status"]] += 1
            trig = [e for e in evs if e["status"] == "TRIGGERED"]
            ba = baseline_a(candles, bb, rsi, p)
            print(f"{name}: episodes {len(evs)} {dict(st)}; triggered {len(trig)}; baseline_a events {len(ba)}")
            if name == "V1_primary" and len(trig):
                se = sd * math.sqrt(1 / len(trig))
                print(f"  V1 MDE80 on one group mean = 2.8*SD/sqrt(n) = {2.8 * se:.3f} % (n={len(trig)})")
        return

    # ---------------- full run ----------------
    rng = random.Random(SEED)
    res = {}
    lines = []
    ev_rows = []
    for name, over in VARIANTS:
        p, bb, rsi, evs = build(candles, m1_idx, m1, over)
        trig = [e for e in evs if e["status"] == "TRIGGERED"]
        recs = []
        for e in trig:
            o = outcome(candles, m1_idx, m1, e["trigger"])
            if o is None:
                continue
            t = e["trigger"]
            o.update(t=candles[t]["t"], idx=t, start=candles[e["start"]]["t"], W=e["W"],
                     d_hold=D.delta_sum(candles, t - p["K"] + 1, t), d_epi=D.delta_sum(candles, e["start"], t))
            recs.append(o)
            ev_rows.append((name, iso(candles[e["start"]]["t"]), iso(candles[e["bounce"]]["t"]), iso(candles[t]["t"]), round(e["W"], 2)))
        ba_idx = baseline_a(candles, bb, rsi, p)
        ba = [o for o in (dict(outcome(candles, m1_idx, m1, t) or {}, t=candles[t]["t"]) for t in ba_idx) if "R4" in o]
        trigs = [e["trigger"] for e in trig]
        bb_idx = baseline_b(candles, trigs, rng, p) if trigs else []
        bbl = [o for o in (dict(outcome(candles, m1_idx, m1, t) or {}, t=candles[t]["t"]) for t in bb_idx) if "R4" in o]
        res[name] = dict(p=p, recs=recs, base_a=ba, base_b=bbl, n_trig_raw=len(trig))

    def vd(rs, key, sign=1):
        return [sign * r[key] for r in rs], [day(r["t"]) for r in rs]

    # ---- primary
    P = res["V1_primary"]
    ev, ba, bbl = P["recs"], P["base_a"], P["base_b"]
    n = len(ev)
    dl = diff_stats(vd(ev, "R4"), vd(ba, "R4"))
    dl_b = diff_stats(vd(ev, "R4"), vd(bbl, "R4"))
    se_ev = group_stats(*vd(ev, "R4"))
    net_long = se_ev["mean"] - C if n else float("nan")
    net_short = -se_ev["mean"] - C if n else float("nan")
    if n < 10:
        verdict = "INCONCLUSIVE"
        why = f"n={n} < 10 events on DEV"
    elif n >= 30 and dl["lo"] > 0 and dl["t"] >= 2 and net_long > 0:
        verdict = "PASS"
        why = "n>=30, DIFF CI excludes 0 (above), t_DIFF>=2, fee-net long mean > 0"
    elif dl["mde"] <= 2 * C:
        verdict = "FAIL"
        why = f"bar not met with power (MDE {dl['mde']:.3f} % <= 2C = {2 * C:.2f} %)"
    else:
        verdict = "INCONCLUSIVE"
        why = f"bar not met and MDE {fmt(dl['mde'])} % > 2C = {2 * C:.2f} % (n too small to detect a cost-sized effect)"

    L = []
    L.append(f"VERDICT: {verdict}")
    L.append("")
    L.append(f"Study wlow_bounce_bbrsi60_2026-10-16, DEV only (1h bars from 1m klines, open < 2024-07-01). Rules: PRE_REG.md (committed before this file). Why: {why}.")
    L.append(f"Primary cell: V1 (ISO prior-week low, K=4), LONG, h=4 h, cost C={C} %. Events with full 24 h forward window: n={n} (triggers before forward-window filter: {P['n_trig_raw']}).")
    L.append("")
    L.append("## Primary table (R4 = % return, entry open[t+1], exit close[t+4]; day-clustered SE)")
    L.append("| group | n | mean R4 % | SE | net long (R4-C) | net short (-R4-C) |")
    L.append("|---|---|---|---|---|---|")
    for lab, rs in (("EVENT (break+bounce+hold)", ev), ("BASELINE a (hold, no weekly break)", ba), ("BASELINE b (same hour-of-day)", bbl)):
        s = group_stats(*vd(rs, "R4")) if rs else {"n": 0, "mean": float("nan"), "se": float("nan")}
        L.append(f"| {lab} | {s['n']} | {fmt(s['mean'])} | {fmt(s['se'])} | {fmt(s['mean'] - C)} | {fmt(-s['mean'] - C)} |")
    L.append("")
    L.append(f"DIFF vs baseline a: {fmt(dl['diff'])} % SE {fmt(dl['se'])} t {fmt(dl['t'],2)} 95% CI [{fmt(dl['lo'])}, {fmt(dl['hi'])}] MDE80 {fmt(dl['mde'])} %")
    L.append(f"DIFF vs baseline b: {fmt(dl_b['diff'])} % SE {fmt(dl_b['se'])} t {fmt(dl_b['t'],2)} 95% CI [{fmt(dl_b['lo'])}, {fmt(dl_b['hi'])}] MDE80 {fmt(dl_b['mde'])} %")
    L.append("")
    L.append("## Horizons, MFE/MAE, first touch (events | baseline a)")
    L.append("| h | event mean % | event SE | event net long | event net short | base-a mean % | base-b mean % |")
    L.append("|---|---|---|---|---|---|---|")
    for h in HORIZONS:
        s = group_stats(*vd(ev, f"R{h}")) if ev else {"mean": float("nan"), "se": float("nan")}
        sa = group_stats(*vd(ba, f"R{h}")) if ba else {"mean": float("nan")}
        sb = group_stats(*vd(bbl, f"R{h}")) if bbl else {"mean": float("nan")}
        L.append(f"| {h} | {fmt(s['mean'])} | {fmt(s['se'])} | {fmt(s['mean'] - C)} | {fmt(-s['mean'] - C)} | {fmt(sa['mean'])} | {fmt(sb['mean'])} |")
    for lab, rs in (("event", ev), ("base-a", ba), ("base-b", bbl)):
        if rs:
            ft = defaultdict(int)
            for r in rs:
                ft[r["first"]] += 1
            L.append(f"- {lab}: mean MFE {fmt(mean([r['MFE'] for r in rs]))} %, mean MAE {fmt(mean([r['MAE'] for r in rs]))} %; first +-1 % within 24 h: up {ft['up']}, dn {ft['dn']}, both-in-one-minute {ft['both']}, none {ft['none']} (n={len(rs)})")
    L.append("")
    L.append("## Event list (UTC; break bar open, bounce bar open, trigger bar open, prior weekly low)")
    for r in ev_rows:
        if r[0] == "V1_primary":
            L.append(f"- {r[1]} | {r[2]} | {r[3]} | W={r[4]}")
    L.append("")
    L.append("## Variants (secondary, no verdict; each is a ledger row)")
    L.append("| variant | events | baseline a n | event mean R4 % | base-a mean R4 % | DIFF | t_DIFF | MDE80 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for name, _ in VARIANTS:
        R = res[name]
        e_, a_ = R["recs"], R["base_a"]
        d_ = diff_stats(vd(e_, "R4"), vd(a_, "R4")) if e_ and a_ else {"diff": float("nan"), "t": float("nan"), "mde": float("nan")}
        me = mean([r["R4"] for r in e_]) if e_ else float("nan")
        ma = mean([r["R4"] for r in a_]) if a_ else float("nan")
        L.append(f"| {name} | {len(e_)} | {len(a_)} | {fmt(me)} | {fmt(ma)} | {fmt(d_['diff'])} | {fmt(d_['t'],2)} | {fmt(d_['mde'])} |")
    L.append("")
    L.append("## Conditioning layers on the V1 events (one at a time; each split side next to the base; NOT_EVALUATED if a side has n < 10)")
    L.append("- L1 open interest: NOT_IN_DATA for DEV (Binance metrics archive starts 2025-09-01). Live-tracking field only.")
    L.append("| layer / split | side | n | mean R4 % | net long | net short | DIFF vs other side | t |")
    L.append("|---|---|---|---|---|---|---|---|")
    L.append(f"| BASE | all | {n} | {fmt(se_ev['mean'])} | {fmt(net_long)} | {fmt(net_short)} | - | - |")
    layers = []
    if ev:
        for lab, key in (("L2 CVD change (break->trigger)", "d_epi"), ("L3 net delta (hold window)", "d_hold")):
            vals = sorted(r[key] for r in ev)
            med = vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2
            layers.append((lab + ", sign", key, 0.0, "up (>0)", "down (<=0)"))
            layers.append((lab + ", median", key, med, "high (>median)", "low (<=median)"))
    for lab, key, thr, hn, ln in layers:
        hi_ = [r for r in ev if r[key] > thr]
        lo_ = [r for r in ev if r[key] <= thr]
        ok = len(hi_) >= 10 and len(lo_) >= 10
        d_ = diff_stats(vd(hi_, "R4"), vd(lo_, "R4")) if len(hi_) > 1 and len(lo_) > 1 else {"diff": float("nan"), "t": float("nan")}
        for sidename, rs in ((hn, hi_), (ln, lo_)):
            s = group_stats(*vd(rs, "R4")) if rs else {"mean": float("nan"), "n": 0}
            tag = "" if ok else " NOT_EVALUATED"
            L.append(f"| {lab}{tag} | {sidename} | {len(rs)} | {fmt(s['mean'])} | {fmt(s['mean'] - C)} | {fmt(-s['mean'] - C)} | {fmt(d_['diff'])} | {fmt(d_['t'],2)} |")
    L.append("")
    L.append("Layer rule (PRE_REG): no combined stack; a layer matters only if its own side passes the primary bar (n>=30, DIFF vs baseline a CI above 0, fee-net > 0). The base verdict above does not depend on the layers.")
    with open(os.path.join(HERE, "RESULT.md"), "w", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(HERE, "events.csv"), "w", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["variant", "break_open", "bounce_open", "trigger_open", "prior_weekly_low"])
        w.writerows(ev_rows)
    print("\n".join(L))


if __name__ == "__main__":
    main()
