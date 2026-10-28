"""T063 event study per research/_archive/loose_2026-10/T063_STOP_RUN_OI_FLUSH.md section 1 (PRE_REG). Parameters are fixed there.

Usage (repo root): python MyTradingSys/research/loose_code/t063_event_study.py [--oi oi_5m.csv]
--oi CSV columns: t (ms, 5m bar open), oi (sumOpenInterest). Without it only arm A0 runs.
"""
import csv, glob, random, statistics, sys, math
from pathlib import Path

N, W, M, COOL = 12, 6, 2.0, 6
H = {"15m": 3, "1h": 12, "4h": 48}
ROOT = Path(__file__).resolve().parents[2]


def load_5m():
    rows = []
    for f in sorted(glob.glob(str(ROOT / "runtime/orderflow_live/*.csv"))):
        for r in csv.DictReader(open(f)):
            rows.append((int(r["t"]), float(r["o"]), float(r["h"]), float(r["l"]), float(r["c"]), float(r["delta"])))
    rows.sort()
    by = {}
    for t, o, h, l, c, d in rows:
        by.setdefault(t - t % 300000, []).append((t, o, h, l, c, d))
    bars = []
    for k in sorted(by):
        g = by[k]
        if len(g) != 5:
            continue
        g.sort()
        bars.append(dict(t=k, o=g[0][1], h=max(x[2] for x in g), l=min(x[3] for x in g), c=g[-1][4], d=sum(x[5] for x in g)))
    return bars


def contiguous(bars, i, j):
    return bars[j]["t"] - bars[i]["t"] == (j - i) * 300000


def atr14(bars, i):
    trs = []
    for k in range(i - 14, i):
        if k < 1:
            return None
        b, p = bars[k], bars[k - 1]
        trs.append(max(b["h"] - b["l"], abs(b["h"] - p["c"]), abs(b["l"] - p["c"])))
    return sum(trs) / 14


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    a = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - a) / d, (c + a) / d)


def build(bars, oi=None):
    n = len(bars)
    flush_ok = {}
    for t in range(N, n):
        if not contiguous(bars, t - N, t):
            continue
        b = bars[t]
        body = b["c"] - b["o"]
        med = statistics.median(abs(bars[k]["c"] - bars[k]["o"]) for k in range(t - N, t))
        big = abs(body) >= M * med and med > 0
        if not big or body == 0 or body * b["d"] <= 0:
            continue
        if oi is not None:
            cur, prev = oi.get(b["t"]), oi.get(b["t"] - 300000)
            if cur is None or prev is None:
                continue
            dd = cur - prev
            meds = []
            for k in range(t - N, t):
                a1, a0 = oi.get(bars[k]["t"]), oi.get(bars[k]["t"] - 300000)
                if a1 is not None and a0 is not None:
                    meds.append(abs(a1 - a0))
            if not meds or not (dd < 0 and abs(dd) >= M * statistics.median(meds)):
                continue
        flush_ok[t] = -1 if body < 0 else 1  # f: flush direction
    sweeps = {}  # s -> side (+1 up-sweep, -1 down-sweep)
    for s in range(N, n):
        if not contiguous(bars, s - N, s):
            continue
        if bars[s]["h"] > max(bars[k]["h"] for k in range(s - N, s)):
            sweeps.setdefault(s, []).append(1)
        if bars[s]["l"] < min(bars[k]["l"] for k in range(s - N, s)):
            sweeps.setdefault(s, []).append(-1)
    events, last = [], {1: -10**9, -1: -10**9}
    n_sweeps = 0
    used = set()
    for s in sorted(sweeps):
        for side in sweeps[s]:
            if s + W >= n:
                continue
            n_sweeps += 1
            for t in range(s + 1, s + W + 1):
                f = flush_ok.get(t)
                if f == -side and t - last[side] > COOL and (t, side) not in used:
                    events.append((t, f, side, s)); last[side] = t; used.add((t, side))
                    break
    ctrl, lastc = [], {1: -10**9, -1: -10**9}
    for t in sorted(flush_ok):
        f = flush_ok[t]
        side = -f
        if any(side in sweeps.get(s, []) for s in range(t - W, t)):
            continue
        if t - lastc[side] > COOL:
            ctrl.append((t, f, side, None)); lastc[side] = t
    return events, ctrl, n_sweeps


def outcomes(bars, evs):
    out = []
    n = len(bars)
    for t, f, side, s in evs:
        if t + 48 >= n or not contiguous(bars, t, t + 48):
            continue
        a = atr14(bars, t)
        if not a:
            continue
        c0 = bars[t]["c"]
        r = {k: f * (bars[t + h]["c"] / c0 - 1) * 1e4 for k, h in H.items()}
        if f < 0:
            depth = (c0 - min(bars[k]["l"] for k in range(t + 1, t + 13))) / a
        else:
            depth = (max(bars[k]["h"] for k in range(t + 1, t + 13)) - c0) / a
        snap = None
        for k in range(t + 1, t + 13):
            if (f < 0 and bars[k]["c"] > bars[t]["o"]) or (f > 0 and bars[k]["c"] < bars[t]["o"]):
                snap = k - t; break
        opp = None
        if s is not None:
            if side == 1:  # up-sweep: opposite pivot = lowest low of the 12 bars before the sweep
                piv = min(bars[k]["l"] for k in range(s - N, s))
                opp = any(bars[k]["l"] < piv for k in range(t + 1, t + 49))
            else:
                piv = max(bars[k]["h"] for k in range(s - N, s))
                opp = any(bars[k]["h"] > piv for k in range(t + 1, t + 49))
        out.append(dict(t=t, f=f, r=r, depth=depth, snap=snap, opp=opp, day=bars[t]["t"] // 86400000))
    return out


def boot(a, b, reps=10000, seed=7):
    rnd = random.Random(seed)
    if not a or not b:
        return (float("nan"),) * 2
    ds = []
    for _ in range(reps):
        ma = sum(rnd.choice(a) for _ in a) / len(a)
        mb = sum(rnd.choice(b) for _ in b) / len(b)
        ds.append(ma - mb)
    ds.sort()
    return ds[int(.025 * reps)], ds[int(.975 * reps)]


def report(tag, ev, ct, n_sweeps, bars):
    days = len({b["t"] // 86400000 for b in bars})
    print(f"## {tag}")
    print(f"bars={len(bars)} days_touched={days} sweeps_with_window={n_sweeps} events_raw={len(ev)} control_raw={len(ct)}")
    eo, co = outcomes(bars, ev), outcomes(bars, ct)
    print(f"events_with_full_4h={len(eo)} control_with_full_4h={len(co)}")
    if n_sweeps:
        print(f"P(flush|sweep)={len(ev)/n_sweeps:.3f} ({len(ev)}/{n_sweeps}); events/day={len(ev)/days:.2f}")
    for name, o in (("EVENT", eo), ("CONTROL", co)):
        print(f"-- {name} n={len(o)}")
        for k in H:
            xs = [x["r"][k] for x in o]
            if not xs:
                continue
            rev = sum(1 for v in xs if v < 0)
            lo, hi = wilson(rev, len(xs))
            print(f"  {k}: mean={statistics.mean(xs):.1f}bp median={statistics.median(xs):.1f}bp reversal={rev}/{len(xs)}={rev/len(xs):.2f} CI[{lo:.2f},{hi:.2f}]")
        if o:
            print(f"  depth_ATR median={statistics.median(x['depth'] for x in o):.2f} p75={sorted(x['depth'] for x in o)[int(.75*(len(o)-1))]:.2f}")
            sn = [x["snap"] for x in o if x["snap"]]
            print(f"  snap_back_12bars={len(sn)}/{len(o)} median_bars={statistics.median(sn) if sn else 'n/a'}")
            oc = [x["opp"] for x in o if x["opp"] is not None]
            if oc:
                print(f"  opposite_pivot_taken_within_4h={sum(oc)}/{len(oc)}")
            dd = {}
            for x in o:
                dd[x["day"]] = dd.get(x["day"], 0) + 1
            print(f"  per_day={dict(sorted(dd.items()))}")
    for k in H:
        a = [x["r"][k] for x in eo]; b = [x["r"][k] for x in co]
        if a and b:
            lo, hi = boot(a, b)
            print(f"diff(event-control) {k}: mean {statistics.mean(a)-statistics.mean(b):.1f}bp boot95[{lo:.1f},{hi:.1f}]")


def main(argv):
    bars = load_5m()
    report("A0 sweep + price/CVD (no OI)", *build(bars), bars)
    if "--oi" in argv:
        oi = {int(r.get("t") or r["ts_ms"]): float(r.get("oi") or r["sumOpenInterest"]) for r in csv.DictReader(open(argv[argv.index("--oi") + 1]))}
        report("A1 sweep + OI drop + price/CVD", *build(bars, oi), bars)


if __name__ == "__main__":
    main(sys.argv[1:])
