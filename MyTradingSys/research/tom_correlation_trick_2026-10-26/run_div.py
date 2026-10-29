"""TOM-CTX-DIV pre-registered backtest (EXTRACT.md s4, frozen by PRE_REG.md). Daily as-of grid, fee-net.

python run_div.py --count-only            events per variant, NO returns computed (for the freeze)
python run_div.py --split DEV             all variants on DEV (older 70%)
python run_div.py --split VALIDATION      primary only, once (refuses a second read)
python run_div.py --split HOLDOUT         primary only, once, only if VALIDATION passed
All parameters are OURS (Tom states no numeric threshold).
"""
import argparse
import bisect
import csv
import datetime as dt
import json
import math
import pathlib
import random
import sys

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"
READ_LOG = HERE / "split_reads.json"

WINDOW = 250
HOLD = 3                      # trading days, exit at close (OURS)
WAIT = 5                      # max days after divergence day to wait for convergence start (OURS)
COST = {"H1": 0.0004, "H2": 0.0010}   # round-trip fee+slippage as fraction (OURS): FDAX/FDXM ~4bp, BTC perp ~10bp


def quantile_thr(vals, cut):
    s = sorted(vals)
    return s[math.ceil(cut * len(s)) - 1]


def _ret(c, t, k):
    a, b = c[t - k], c[t]
    if a is None or b is None or a == 0:
        return None
    return b / a - 1


def find_events(mover, members, flips, L, window, cut, hold, mode="basket", wait=WAIT):
    """Return [(D_idx, entry_idx, dir)] with dir = sign of the mover's move (trade is the fade: -dir).

    mode 'basket': divergence = mover top-quantile |L-day move| AND sign opposite to the median member L-day return
                   (members multiplied by their flip); trigger = first t in D+1..D+wait where the median member 1-day
                   return has sign == dir AND the mover close(t) has not made a new extreme since D.
    mode 'control': same top-quantile move WITHOUT the cross-market condition; trigger = mover 1-day return against dir
                   AND not a new extreme.
    mode 'divday': basket divergence, entry at D itself (the timing Tom warns against); reported, not selected.
    Non-overlapping: a D <= previous exit index is skipped. Entry needs entry+hold within data.
    """
    n = len(mover)
    rabs = [None] * n
    for t in range(L, n):
        r = _ret(mover, t, L)
        rabs[t] = None if r is None else abs(r)
    events, last_exit = [], -1
    names = list(members)
    for D in range(L + window, n):
        trail = rabs[D - window:D]
        if rabs[D] is None or any(x is None for x in trail):
            continue
        if D <= last_exit:
            continue
        r = _ret(mover, D, L)
        if rabs[D] <= quantile_thr(trail, cut) or r == 0:
            continue
        dr = 1 if r > 0 else -1
        if mode in ("basket", "divday"):
            mr = []
            for m in names:
                x = _ret(members[m], D, L)
                if x is None:
                    mr = None
                    break
                mr.append(x * flips[m])
            if mr is None:
                continue
            mr.sort()
            med = mr[len(mr) // 2] if len(mr) % 2 else (mr[len(mr) // 2 - 1] + mr[len(mr) // 2]) / 2
            if med == 0 or (1 if med > 0 else -1) == dr:
                continue
        if mode == "divday":
            entry = D
        else:
            entry = None
            ext = mover[D]
            for t in range(D + 1, min(D + wait, n - 1) + 1):
                new_ext = (mover[t] > ext) if dr > 0 else (mover[t] < ext)
                ext = max(ext, mover[t]) if dr > 0 else min(ext, mover[t])
                if new_ext:
                    continue
                if mode == "control":
                    x = _ret(mover, t, 1)
                    ok = x is not None and x * dr < 0
                else:
                    ms = []
                    for m in names:
                        y = _ret(members[m], t, 1)
                        if y is None:
                            ms = None
                            break
                        ms.append(y * flips[m])
                    if ms is None:
                        continue
                    ms.sort()
                    med1 = ms[len(ms) // 2] if len(ms) % 2 else (ms[len(ms) // 2 - 1] + ms[len(ms) // 2]) / 2
                    ok = med1 * dr > 0
                if ok:
                    entry = t
                    break
            if entry is None:
                continue
        if entry + hold > n - 1:
            continue
        events.append((D, entry, dr))
        last_exit = entry + hold
    return events


def trade_returns(mover, events, hold, cost):
    return [(-dr) * (mover[e + hold] / mover[e] - 1) - cost for _, e, dr in events]


def cluster_mean_se(r, clusters):
    n = len(r)
    mean = sum(r) / n
    agg = {}
    for x, c in zip(r, clusters):
        agg[c] = agg.get(c, 0.0) + (x - mean)
    return mean, math.sqrt(sum(v * v for v in agg.values())) / n


def boot_lower(r, clusters, B=2000, seed=7):
    """Cluster (month) bootstrap 2.5th percentile of the mean."""
    groups = {}
    for x, c in zip(r, clusters):
        groups.setdefault(c, []).append(x)
    keys = list(groups)
    rng = random.Random(seed)
    means = []
    for _ in range(B):
        tot, k = 0.0, 0
        for _ in keys:
            g = groups[rng.choice(keys)]
            tot += sum(g)
            k += len(g)
        means.append(tot / k)
    means.sort()
    return means[int(0.025 * B)]


def asof(dates, closes, cutoffs, lag_days):
    """Last close with bar date <= cutoff - lag days (calendar). None before the first bar."""
    out = []
    for c, lag in zip(cutoffs, lag_days):
        cd = (dt.date.fromisoformat(c) - dt.timedelta(days=lag)).isoformat()
        i = bisect.bisect_right(dates, cd) - 1
        out.append(closes[i] if i >= 0 else None)
    return out


def load(name):
    d, c = [], []
    with open(DATA / f"{name}.csv") as f:
        for row in csv.DictReader(f):
            d.append(row["date"])
            c.append(float(row["close"]))
    return d, c


# lag_days: calendar days subtracted from the traded-market date so that nothing after the traded close is used.
# H1 grid = DAX trading dates (close 16:30 UTC): Nikkei same date (06:00 UTC, stale by design); ES/NQ/DXY previous
# calendar day's last close (US close is after Xetra close); BTC daily bar of date-1 closes 00:00 UTC of date.
# H2 grid = BTC dates (bar closes 00:00 UTC next day): ES/NQ/DXY same-date close (<=21:00 UTC) is earlier. Holidays/weekends
# carry the last close forward (zero return).
H1_LAG = {"NIKKEI": 0, "ES": 1, "NQ": 1, "DXY": 1, "BTC": 1}
H2_LAG = {"ES": 0, "NQ": 0, "DXY": 0}
H1_BASKETS = {"B1": ["ES", "NIKKEI", "BTC"], "B2": ["ES", "NIKKEI"], "B3": ["ES", "BTC"]}
H2_BASKETS = {"B1": ["ES", "DXY"], "B2": ["NQ", "DXY"]}
FLIP = {"DXY": -1}
LS = [1, 2, 3, 5]
CUTS = [0.8, 0.7]
PRIMARY = {"H1": ("B1", 2, 0.8), "H2": ("B1", 2, 0.8)}


def build(h):
    if h == "H1":
        dates, mover = load("DAX")
        lag, baskets = H1_LAG, H1_BASKETS
    else:
        dates, mover = load("BTC")
        lag, baskets = H2_LAG, H2_BASKETS
    cache = {}
    for b in baskets.values():
        for m in b:
            if m not in cache:
                md, mc = load(m)
                cache[m] = asof(md, mc, dates, [lag[m]] * len(dates))
    return dates, mover, cache, baskets


def split_bounds(dates):
    n = len(dates)
    return {"DEV": (0, int(0.70 * n)), "VALIDATION": (int(0.70 * n), int(0.85 * n)), "HOLDOUT": (int(0.85 * n), n)}


def run_variant(h, dates, mover, cache, baskets, bname, L, cut, mode, split):
    members = {m: cache[m] for m in baskets[bname]}
    ev = find_events(mover, members, FLIP_OF(members), L, WINDOW, cut, HOLD, mode)
    lo, hi = split_bounds(dates)[split]
    ev = [e for e in ev if lo <= e[1] < hi]
    r = trade_returns(mover, ev, HOLD, COST[h])
    return ev, r


def FLIP_OF(members):
    return {m: FLIP.get(m, 1) for m in members}


def summarize(r, ev, dates):
    if not r:
        return {"n": 0}
    cl = [dates[e[1]][:7] for e in ev]
    mean, se = cluster_mean_se(r, cl)
    return {"n": len(r), "mean": mean, "se": se, "lb95": boot_lower(r, cl),
            "hit": sum(1 for x in r if x > 0) / len(r)}


def placebo(h, dates, mover, cache, baskets, bname, L, cut, split, draws=100, seed=11):
    rng = random.Random(seed)
    n = len(dates)
    res = []
    for _ in range(draws):
        k = rng.randint(60, n - 60)
        sh = {m: cache[m][k:] + cache[m][:k] for m in baskets[bname]}
        ev = find_events(mover, sh, FLIP_OF(sh), L, WINDOW, cut, HOLD, "basket")
        lo, hi = split_bounds(dates)[split]
        ev = [e for e in ev if lo <= e[1] < hi]
        r = trade_returns(mover, ev, HOLD, COST[h])
        if r:
            res.append(sum(r) / len(r))
    return res


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["DEV", "VALIDATION", "HOLDOUT"])
    ap.add_argument("--count-only", action="store_true")
    ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    if a.count_only:
        for h in ("H1", "H2"):
            dates, mover, cache, baskets = build(h)
            b = split_bounds(dates)
            print(h, "grid", dates[0], dates[-1], "n", len(dates),
                  {k: (dates[lo], dates[hi - 1]) for k, (lo, hi) in b.items()})
            for bn in baskets:
                for L in LS:
                    for cut in CUTS:
                        members = {m: cache[m] for m in baskets[bn]}
                        ev = find_events(mover, members, FLIP_OF(members), L, WINDOW, cut, HOLD, "basket")
                        c = {k: sum(1 for e in ev if lo <= e[1] < hi) for k, (lo, hi) in b.items()}
                        print(f"  {h} {bn} L={L} cut={cut} events", c)
        return 0
    if not a.split:
        ap.error("--split or --count-only required")
    if a.split != "DEV":
        if "FROZEN" not in (HERE / "PRE_REG.md").read_text():
            sys.exit("PRE_REG.md not frozen")
        log = json.loads(READ_LOG.read_text()) if READ_LOG.exists() else {}
        if a.split in log:
            sys.exit(f"{a.split} already read once ({log[a.split]}); refusing")
        if a.split == "HOLDOUT" and "VALIDATION" not in log:
            sys.exit("HOLDOUT only after VALIDATION")
        log[a.split] = dt.datetime.now(dt.timezone.utc).isoformat()
        READ_LOG.write_text(json.dumps(log), newline="\n")
    out = {}
    for h in ("H1", "H2"):
        dates, mover, cache, baskets = build(h)
        combos = [(bn, L, cut) for bn in baskets for L in LS for cut in CUTS] if a.split == "DEV" else [PRIMARY[h]]
        for bn, L, cut in combos:
            key = f"{h}|{bn}|L{L}|cut{cut}"
            row = {}
            for mode in ("basket", "control", "divday"):
                ev, r = run_variant(h, dates, mover, cache, baskets, bn, L, cut, mode, a.split)
                row[mode] = summarize(r, ev, dates)
            if (bn, L, cut) == PRIMARY[h]:
                pl = placebo(h, dates, mover, cache, baskets, bn, L, cut, a.split)
                real = row["basket"].get("mean")
                row["placebo"] = {"draws": len(pl), "mean": sum(pl) / len(pl) if pl else None,
                                  "p95": sorted(pl)[int(0.95 * len(pl))] if pl else None,
                                  "frac_ge_real": (sum(1 for x in pl if real is not None and x >= real) / len(pl)) if pl else None}
            out[key] = row
            p = row["basket"]
            print(key, "basket", {k: (round(v, 5) if isinstance(v, float) else v) for k, v in p.items()},
                  "| control n", row["control"].get("n"), "mean", row["control"].get("mean"),
                  "| divday n", row["divday"].get("n"), "mean", row["divday"].get("mean"))
            if "placebo" in row:
                print("   placebo", row["placebo"])
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps({"split": a.split, "rows": out}, indent=1), newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
