"""Run PRE_REG.md study. Reads runtime_data/edge-oi-flush-1113/*.json (fetch.py). Writes results.csv, events.csv (small), summary.json."""
import csv, datetime as dt, json, random, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import flush as F

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "runtime_data" / "edge-oi-flush-1113"
COINS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
UTC = dt.timezone.utc
def ms(y, m, d): return int(dt.datetime(y, m, d, tzinfo=UTC).timestamp() * 1000)
SPLITS = [("DEV", ms(2020, 1, 1), ms(2024, 7, 1)), ("VALIDATION", ms(2024, 7, 1), ms(2025, 7, 1)), ("RECENT", ms(2025, 7, 1), ms(2100, 1, 1))]
HOLDS = [4, 12, 24, 72]
CELLS = [(tf, h) for tf in (1, 4) for h in HOLDS + ["br"]]
DRAWS, REPS, K = 20, 5000, 2.0
rng = random.Random(20261113)

def split_of(t):
    for n, a, b in SPLITS:
        if a <= t < b: return n

def outcome(cx, bars, i, side, tf, cell, delay=0):
    t_e = bars[i][0] + tf * F.HOUR * (1 + delay)
    if cell == "br":
        stop = bars[i][3] if side > 0 else bars[i][2]
        return F.fwd_bracket(cx["t"], cx["kl"], cx["ft"], cx["fr"], t_e, side, stop)
    return F.fwd_fixed(cx["t"], cx["kl"], cx["ft"], cx["fr"], t_e, side, cell)

def month(t): return dt.datetime.fromtimestamp(t / 1000, UTC).strftime("%Y-%m")

def main():
    recs = []   # dict(coin, tf, cell, side, t, day, v, p, delay_v)
    starts, nev = {}, {}
    for c in COINS:
        d = json.loads((DATA / f"{c}USDT.json").read_text())
        kl = [tuple(x) for x in d["kl"]]
        oi = {t: v for t, v in d["oi"]}
        ft = [t for t, _ in d["fund"]]; fr = [r for _, r in d["fund"]]
        cx = dict(t=[k[0] for k in kl], kl=kl, ft=ft, fr=fr)
        starts[c] = dict(oi=dt.datetime.fromtimestamp(d["oi"][0][0] / 1000, UTC).strftime("%Y-%m-%d"),
                         kl=dt.datetime.fromtimestamp(kl[0][0] / 1000, UTC).strftime("%Y-%m-%d"))
        for tf in (1, 4):
            bars = F.agg(kl, tf)
            atr = F.atr_series(bars)
            doi = F.doi_series(bars, oi, tf)
            rows = F.events(bars, doi, atr, tf)
            ev = F.dedup([dict(r, side=1 if r["mv"] <= -K else -1) for r in rows if r["drop"] and abs(r["mv"]) >= K], bars, 24)
            pool = {}
            for r in rows:
                if not r["drop"] and abs(r["mv"]) >= K:
                    pool.setdefault((month(bars[r["i"]][0]), 1 if r["mv"] < 0 else -1), []).append(r)
            nev[(c, tf)] = len(ev)
            for e in ev:
                i, side = e["i"], e["side"]
                t_e = bars[i][0] + tf * F.HOUR
                cands = pool.get((month(bars[i][0]), side), [])
                near = [r for r in cands if 0.75 * abs(e["mv"]) <= abs(r["mv"]) <= 1.25 * abs(e["mv"])] or cands
                for cell in HOLDS + ["br"]:
                    v = outcome(cx, bars, i, side, tf, cell)
                    if v is None: continue
                    ps = []
                    if near:
                        for _ in range(DRAWS):
                            pv = outcome(cx, bars, rng.choice(near)["i"], side, tf, cell)
                            if pv is not None: ps.append(pv)
                    dv = outcome(cx, bars, i, side, tf, cell, delay=1) if cell != "br" else None
                    recs.append(dict(coin=c, tf=tf, cell=cell, side=side, t=t_e, day=t_e // 86400000, v=v,
                                     p=(sum(ps) / len(ps)) if ps else None, dv=dv, mv=e["mv"], dOI=e["d"]))
    return recs, starts, nev

def boot(day, val, reps=REPS, seed=7):
    """Day-cluster bootstrap of the mean; returns mean, lo, hi, p(mean<=0)."""
    val = np.asarray(val, float); day = np.asarray(day)
    if len(val) == 0: return (float("nan"),) * 3 + (1.0,)
    u, inv = np.unique(day, return_inverse=True)
    S = np.bincount(inv, val); N = np.bincount(inv).astype(float)
    r = np.random.default_rng(seed); idx = r.integers(0, len(u), (reps, len(u)))
    m = S[idx].sum(1) / N[idx].sum(1)
    return float(val.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((m <= 0).mean())

def bh(ps, q=0.10):
    o = sorted(range(len(ps)), key=lambda i: ps[i]); n = len(ps); keep = set(); kmax = -1
    for r, i in enumerate(o, 1):
        if ps[i] <= q * r / n: kmax = r
    for r, i in enumerate(o, 1):
        if r <= kmax: keep.add(i)
    return keep

def table(recs):
    out = []
    for tf, cell in CELLS:
        for sp, _, _ in SPLITS:
            for side_name, sides in (("both", (1, -1)), ("long", (1,)), ("short", (-1,))):
                r = [x for x in recs if x["tf"] == tf and x["cell"] == cell and split_of(x["t"]) == sp and x["side"] in sides]
                if not r: out.append(dict(tf=tf, cell=cell, split=sp, side=side_name, n=0)); continue
                m, lo, hi, p = boot([x["day"] for x in r], [x["v"] for x in r])
                pr = [x for x in r if x["p"] is not None]
                pm = pdiff = dlo = dhi = None
                if pr:
                    pm = float(np.mean([x["p"] for x in pr]))
                    pdiff, dlo, dhi, _ = boot([x["day"] for x in pr], [x["v"] - x["p"] for x in pr])
                dl = [x for x in r if x["dv"] is not None]
                out.append(dict(tf=tf, cell=cell, split=sp, side=side_name, n=len(r), days=len({x["day"] for x in r}), mean=m, lo=lo, hi=hi, p=p,
                                n_placebo=len(pr), placebo_mean=pm, diff=pdiff, diff_lo=dlo, diff_hi=dhi,
                                delay1_mean=float(np.mean([x["dv"] for x in dl])) if dl else None,
                                hit=float(np.mean([x["v"] > 0 for x in r]))))
    return out

if __name__ == "__main__":
    recs, starts, nev = main()
    tab = table(recs)
    # BH over the 10 primary cells (VALIDATION, both sides); n<30 -> p=1
    prim = [t for t in tab if t["split"] == "VALIDATION" and t["side"] == "both"]
    ps = [t["p"] if t["n"] >= 30 else 1.0 for t in prim]
    keep = bh(ps)
    for j, t in enumerate(prim):
        t["bh_pass"] = j in keep
        t["pass"] = bool(t["n"] >= 30 and t["mean"] > 0 and t["lo"] > 0 and t.get("diff") is not None and t["diff"] > 0 and t["diff_lo"] > 0 and j in keep)
        t["verdict"] = "PASS" if t["pass"] else ("UNDERPOWERED" if t["n"] < 30 else "FAIL")
    keys = sorted({k for t in tab for k in t})
    with open(HERE / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, keys); w.writeheader(); w.writerows(tab)
    with open(HERE / "events.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["coin", "tf", "side", "t_entry_utc", "move_atr", "dOI"])
        seen = set()
        for x in recs:
            k = (x["coin"], x["tf"], x["t"])
            if k in seen: continue
            seen.add(k); w.writerow([x["coin"], x["tf"], x["side"], dt.datetime.fromtimestamp(x["t"] / 1000, UTC).strftime("%Y-%m-%d %H:%M"), round(x["mv"], 2), round(x["dOI"], 4)])
    json.dump(dict(starts=starts, nev={f"{c}_{tf}h": n for (c, tf), n in nev.items()}), open(HERE / "summary.json", "w"), indent=1)
    print(json.dumps(starts)); print(nev)
    for t in prim: print({k: (round(v, 5) if isinstance(v, float) else v) for k, v in t.items()})
