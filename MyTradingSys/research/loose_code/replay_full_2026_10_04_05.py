"""Full G1 replay 10-04/05 over runtime_data/snapshots (research/_archive/loose_2026-10/REPLAY_2026-10-04_05.md).
net_rr per backtest/layers/FORMULAS.md section 17 (written independently of runtime/mts_math.py).
Episode = same (setup_type, zone type, round zone price) seen in consecutive snapshots with gaps <= 30 min; first snapshot of the episode is used.
Nodes = volume-profile levels beyond the zone price in trade direction (weekly/daily/prior_day/post_funding/4h poc,vah,val + prior_week_poc + two_week_ago_poc).
Outcome: 1m bars from orderflow_live after the snapshot; fill if price touches zone price within 60 min; then first of stop / node within 12 h (same bar -> stop)."""
import csv, glob, json, datetime as dt, statistics, collections
from pathlib import Path
TAKER = 0.0005
ROOT = Path(__file__).resolve().parents[2]
FLOORS = (1.0, 1.25, 1.5, 2.33)


def net_rr(e, t, s):
    cost = 2 * TAKER * e
    d = abs(e - s) + cost
    return (abs(t - e) - cost) / d if d else 0.0


def ts(j):
    s = j["timestamp_utc"].rstrip("Z")
    if "." in s:
        a, b = s.split(".")
        s = a + "." + b[:6]
    return dt.datetime.fromisoformat(s).replace(tzinfo=dt.timezone.utc).timestamp()


def nodes_of(j):
    out = {}
    for k in ("weekly_vp", "daily_vp", "prior_day", "post_funding_vp", "intraday_4h_vp"):
        v = j.get(k) or {}
        for f in ("poc", "vah", "val"):
            if v.get(f):
                out[f"{k}.{f}"] = v[f]
    w = j.get("weekly_vp") or {}
    for f in ("prior_week_poc", "two_week_ago_poc"):
        if w.get(f):
            out[f"weekly_vp.{f}"] = w[f]
    return out


def bars():
    r = []
    for f in sorted(glob.glob(str(ROOT / "runtime/orderflow_live/2026-10-0[345].csv"))):
        for x in csv.DictReader(open(f)):
            r.append((int(x["t"]) / 1000, float(x["h"]), float(x["l"])))
    r.sort()
    return r


def outcome(B, t0, side, entry, stop, node):
    fill = None
    for t, h, l in B:
        if t < t0:
            continue
        if t > t0 + 3600 and fill is None:
            return "nofill"
        if fill is None:
            if l <= entry <= h:
                fill = t
            continue
        if t > fill + 43200:
            return "open"
        hit_s = (l <= stop) if side > 0 else (h >= stop)
        hit_n = (h >= node) if side > 0 else (l <= node)
        if hit_s:
            return "stop"
        if hit_n:
            return "node"
    return "nofill" if fill is None else "open"


def main():
    B = bars()
    last_bar = B[-1][0]
    eps = {}
    for f in sorted(glob.glob(str(ROOT.parent / "runtime_data/snapshots/BTCUSDT_2026-10-0[45]*.json"))):
        j = json.load(open(f))
        t = ts(j)
        for c in j.get("setup_candidates") or []:
            z, m = c["zone"], c["math"]
            if not m.get("stop") or not m.get("target"):
                continue
            key = (c["setup_type"], z["type"], round(z["price"]))
            e = eps.get(key)
            if e and t - e["last"] <= 1800:
                e["last"] = t; e["n"] += 1
                e["max_rr"] = max(e["max_rr"], m["net_rr"]); e["min_rr"] = min(e["min_rr"], m["net_rr"])
                continue
            side = 1 if c["direction"] == "long" else -1
            eps.setdefault(key, None)
            rec = dict(key=key, t=t, last=t, n=1, side=side, entry=z["price"], stop=m["stop"], target=m["target"], rr=m["net_rr"],
                       max_rr=m["net_rr"], min_rr=m["net_rr"], sanity=m["net_rr_sanity"], tier=m["tier"], nodes=nodes_of(j))
            eps[key] = rec
            eps.setdefault("_all", []).append(rec) if False else None
            ALL.append(rec)
    return B, last_bar


ALL = []
if __name__ == "__main__":
    B, last_bar = main()
    # episodes were replaced when key re-appeared after a gap; ALL holds every episode first-record
    # (running max/min of later cycles are attached to the dict that was current at the time)
    rows = []
    for r in ALL:
        if r["stop"] == r["entry"] or (r["stop"] - r["entry"]) * r["side"] > 0:
            continue
        ns = sorted([(abs(p - r["entry"]), k, p) for k, p in r["nodes"].items() if (p - r["entry"]) * r["side"] > r["entry"] * 0.0005])
        r["ns"] = ns
        rows.append(r)
    print(f"episodes={len(rows)}  window_end_bar={dt.datetime.fromtimestamp(last_bar, dt.timezone.utc):%m-%d %H:%M}Z")
    byset = collections.Counter(r["key"][0] for r in rows)
    print("by setup_type:", dict(byset))
    print()
    print("A. engine target (the target the engine used): net_rr at first sighting")
    for fl in FLOORS:
        print(f"  clears {fl}: {sum(1 for r in rows if r['rr'] >= fl)}/{len(rows)}")
    print(f"  engine net_rr_sanity true: {sum(1 for r in rows if r['sanity'])}/{len(rows)}")
    print(f"  best net_rr seen in episode >= 1.25: {sum(1 for r in rows if r['max_rr'] >= 1.25)}")
    q = sorted(r["rr"] for r in rows)
    print("  engine net_rr quantiles p10/p25/p50/p75/p90:", [round(q[int(p * (len(q) - 1))], 2) for p in (.1, .25, .5, .75, .9)])
    print()
    print("B. node-by-node net_rr (nodes beyond entry, ascending distance)")
    for k in range(3):
        v = [net_rr(r["entry"], r["ns"][k][2], r["stop"]) for r in rows if len(r["ns"]) > k]
        if v:
            print(f"  node{k+1}: n={len(v)} median={statistics.median(v):.2f}  >=1.0:{sum(x>=1 for x in v)} >=1.25:{sum(x>=1.25 for x in v)} >=1.5:{sum(x>=1.5 for x in v)} >=2.33:{sum(x>=2.33 for x in v)}")
    print("  first node that clears 1.25 per episode (index -> count):", dict(sorted(collections.Counter(
        next((i + 1 for i, (_, _, p) in enumerate(r["ns"]) if net_rr(r["entry"], p, r["stop"]) >= 1.25), 0) for r in rows).items())))
    print()
    print("C. outcomes (fill within 60 min of first sighting, then stop vs node within 12 h; same bar = stop)")
    for k in range(3):
        c = collections.Counter(); rr = []
        for r in rows:
            if len(r["ns"]) <= k:
                continue
            node = r["ns"][k][2]
            o = outcome(B, r["t"], r["side"], r["entry"], r["stop"], node)
            c[o] += 1
            if o in ("node", "stop"):
                rr.append(net_rr(r["entry"], node, r["stop"]) if o == "node" else -1.0)
        dec = c["node"] + c["stop"]
        p = c["node"] / dec if dec else float("nan")
        ev = statistics.mean(rr) if rr else float("nan")
        print(f"  nearest-node #{k+1}: {dict(c)} hit={p:.2f} (n_decided={dec}) mean_R_net={ev:+.2f}")
    c = collections.Counter(); rr = []
    for r in rows:
        o = outcome(B, r["t"], r["side"], r["entry"], r["stop"], r["target"]); c[o] += 1
        if o in ("node", "stop"):
            rr.append(r["rr"] if o == "node" else -1.0)
    dec = c["node"] + c["stop"]
    print(f"  engine target: {dict(c)} hit={c['node']/dec if dec else float('nan'):.2f} (n_decided={dec}) mean_R_net={statistics.mean(rr) if rr else float('nan'):+.2f}")
    print()
    print("E. engine-target outcome by engine net_rr bucket (decided = fill then stop/target within 12 h)")
    for lo, hi in ((-99, 0), (0, 1.0), (1.0, 1.25), (1.25, 1.5), (1.5, 2.33), (2.33, 99)):
        c = collections.Counter(); rr = []
        for r in rows:
            if lo <= r["rr"] < hi:
                o = outcome(B, r["t"], r["side"], r["entry"], r["stop"], r["target"]); c[o] += 1
                if o in ("node", "stop"):
                    rr.append(r["rr"] if o == "node" else -1.0)
        dec = c["node"] + c["stop"]
        print(f"  eng_nrr [{lo},{hi}): episodes={sum(c.values())} decided={dec} hit={c['node']/dec if dec else float('nan'):.2f} mean_R_net={statistics.mean(rr) if rr else float('nan'):+.2f} break-even hit={(1/(1+statistics.mean([r['rr'] for r in rows if lo <= r['rr'] < hi]))) if any(lo <= r['rr'] < hi for r in rows) else float('nan'):.2f}")
    print()
    print("D. episodes listing (first sighting UTC, setup, zone, engine nrr, node1/2/3 nrr)")
    for r in rows:
        n3 = " ".join(f"{net_rr(r['entry'], p, r['stop']):.2f}" for _, _, p in r["ns"][:3])
        print(f"  {dt.datetime.fromtimestamp(r['t'], dt.timezone.utc):%m-%d %H:%M} {r['key'][0]:9s} {r['key'][1]:22s} {r['entry']:.1f} stop {r['stop']:.1f} eng={r['rr']:.2f} nodes[{n3}] cycles={r['n']}")
