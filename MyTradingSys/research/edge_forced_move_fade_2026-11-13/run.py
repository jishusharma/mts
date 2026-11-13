"""Run PRE_REG.md. Reads runtime_data/edge-forced-1113/*.json (fetch.py). Writes results.csv, summary.json."""
import csv, datetime as dt, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fade as F

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "runtime_data" / "edge-forced-1113"
COINS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
UTC = dt.timezone.utc
def ms(y, m, d): return int(dt.datetime(y, m, d, tzinfo=UTC).timestamp() * 1000)
SPLITS = [("DEV", ms(2020, 1, 1), ms(2024, 7, 1)), ("VALIDATION", ms(2024, 7, 1), ms(2025, 7, 1)), ("RECENT", ms(2025, 7, 1), ms(2100, 1, 1))]
HOLD = {"T2": 8, "T4": 16, "T8": 32, "BR": 32}
REPS, DRAWS = 5000, 10
nrng = np.random.default_rng(20261113)

def split_of(t):
    for n, a, b in SPLITS:
        if a <= t < b: return n

def month(t): return dt.datetime.fromtimestamp(t / 1000, UTC).strftime("%Y-%m")

def cluster_ci(vals, days, reps=REPS):
    """Day-cluster bootstrap of the mean: mean, lo, hi, one-sided p(mean<=0)."""
    vals = np.asarray(vals, float)
    if len(vals) == 0: return (np.nan,) * 3 + (1.0,)
    ud, inv = np.unique(days, return_inverse=True)
    s = np.bincount(inv, vals); n = np.bincount(inv).astype(float)
    idx = nrng.integers(0, len(ud), (reps, len(ud)))
    m = s[idx].sum(1) / n[idx].sum(1)
    return vals.mean(), np.percentile(m, 2.5), np.percentile(m, 97.5), float((m <= 0).mean())

def load():
    coins = {}
    for c in COINS:
        f = DATA / f"{c}USDT.json"
        if not f.exists(): continue
        d = json.loads(f.read_text())
        k = np.array(d["kl"], float)
        t, o, h, l, cl, v = (k[:, i] for i in range(6))
        im = F.impulses(t, o, h, l, cl, v, [tuple(x) for x in d["oi"]])
        ok = ~np.isnan(im["atr"]) & ~np.isnan(im["med"])
        notimp = ~((im["rng"] >= 1.5) & (im["volx"] >= 2))
        pool = {}
        for b in np.where(ok & notimp)[0]:
            if b + 33 < len(t): pool.setdefault(month(t[b]), []).append(b)
        coins[c] = dict(t=t, o=o, h=h, l=l, c=cl, v=v, im=im, ft=[x[0] for x in d["fund"]], fr=[x[1] for x in d["fund"]],
                        oi_start=int(d["oi"][0][0]), pool={m: np.array(x) for m, x in pool.items()})
    return coins

def select(cx, k, cls, x):
    """Impulse bars passing k and volume 3x; class A/B/C/ALL on dOI; dedup 8 bars."""
    im = cx["im"]
    base = (im["dir"] != 0) & (im["rng"] >= k) & (im["volx"] >= 3) & ~np.isnan(im["atr"]) & (cx["t"] >= cx["oi_start"])
    if cls != "ALL":
        d = im["doi"]
        base = base & ~np.isnan(d)
        base = base & ((d <= -x / 100) if cls == "A" else (d >= x / 100) if cls == "B" else (abs(d) < x / 100))
    out, last = [], -99
    for i in np.where(base)[0]:
        if i - last > 8 and i + 2 < len(cx["t"]):
            out.append(int(i)); last = int(i)
    return out

def event_trade(cx, i, mode, exitm):
    """(side, stop, target, e) at close of bar i+1, or None if nothing left to trade."""
    h, l, c, im = cx["h"], cx["l"], cx["c"], cx["im"]
    e = i + 1; dr = int(im["dir"][i]); A = im["atr"][i]; p = c[e]
    E = h[i] if dr > 0 else l[i]; M = (h[i] + l[i]) / 2
    if mode == "fade":
        side = -dr; stop = E + dr * 0.25 * A
        if (side > 0 and (p <= stop or p >= M)) or (side < 0 and (p >= stop or p <= M)): return None
        tgt = M if exitm == "BR" else None
    else:
        side = dr; stop = M - dr * 0.25 * A
        if (side > 0 and p <= stop) or (side < 0 and p >= stop): return None
        tgt = p + side * 2 * abs(p - stop) if exitm == "BR" else None
    return side, stop, tgt, e

def run_cell(coins, name, k, cls, x, exitm, placebo=True):
    mode = "fade" if name.startswith("fade") else "follow"
    rows = []; skipped = 0
    for c, cx in coins.items():
        t = cx["t"]
        for i in select(cx, k, cls, x):
            tr = event_trade(cx, i, mode, exitm)
            if tr is None: skipped += 1; continue
            side, stop, tgt, e = tr
            v = F.fwd_sim(t, cx["o"], cx["h"], cx["l"], cx["c"], cx["ft"], cx["fr"], e, side, stop, tgt, HOLD[exitm])
            if v is None: skipped += 1; continue
            A = cx["im"]["atr"][i]; p = cx["c"][e]
            sd = abs(p - stop) / A; td = None if tgt is None else abs(tgt - p) / A
            pv = []
            cand = cx["pool"].get(month(t[i]), []) if placebo else []
            if len(cand):
                for b in nrng.choice(cand, size=min(DRAWS, len(cand)), replace=False):
                    Ab = cx["im"]["atr"][b]; pb = cx["c"][b]
                    r = F.fwd_sim(t, cx["o"], cx["h"], cx["l"], cx["c"], cx["ft"], cx["fr"], int(b), side,
                                  pb - side * sd * Ab, None if td is None else pb + side * td * Ab, HOLD[exitm])
                    if r is not None: pv.append(r)
            rows.append((split_of(t[e]), int(t[e] // 86400000), v, float(np.mean(pv)) if pv else np.nan, c))
    return rows, skipped

def summarize(rows, split):
    r = [x for x in rows if x[0] == split]
    if not r: return None
    days = np.array([x[1] for x in r]); v = np.array([x[2] for x in r]); p = np.array([x[3] for x in r])
    m, lo, hi, pv = cluster_ci(v, days)
    okp = ~np.isnan(p)
    dm, dlo, dhi, _ = cluster_ci((v - p)[okp], days[okp]) if okp.sum() else (np.nan,) * 4
    return dict(n=len(r), days=len(set(days)), mean=m, lo=lo, hi=hi, p=pv if len(r) >= 30 else 1.0,
                plac=float(np.nanmean(p)) if okp.sum() else np.nan, dmean=dm, dlo=dlo, dhi=dhi, hit=float((v > 0).mean()))

def main():
    coins = load()
    cells = []
    for hid, hyp, cls in (("H1", "fade", "A"), ("H2", "follow", "B")):
        for k in (2.0, 3.0):
            for x in (0.3, 0.6):
                for ex in ("T2", "T4", "T8", "BR"):
                    cells.append((hid, hyp + "_" + cls, k, cls, x, ex, True))
    for k in (2.0, 3.0):
        for x in (0.3, 0.6):
            for hyp, cls in (("fade", "B"), ("follow", "A")):
                for ex in ("T4", "BR"): cells.append(("CTRL", hyp + "_" + cls, k, cls, x, ex, False))
        for hyp in ("fade", "follow"):
            for ex in ("T4", "BR"): cells.append(("CTRL", hyp + "_ALL", k, "ALL", 0, ex, False))
    out = []
    for hid, name, k, cls, x, ex, prim in cells:
        rows, sk = run_cell(coins, name, k, cls, x, ex, placebo=prim)
        for sp, _, _ in SPLITS:
            s = summarize(rows, sp)
            if s: out.append(dict(hyp=hid, rule=name, k=k, x=x, exit=ex, split=sp, primary=prim, skipped=sk, **s))
        print(hid, name, k, x, ex, [(o["split"], o["n"], round(o["mean"] * 100, 3)) for o in out[-3:]], flush=True)
    prim = sorted([o for o in out if o["primary"] and o["split"] == "VALIDATION"], key=lambda o: o["p"])
    cut = max([i + 1 for i, o in enumerate(prim) if o["p"] <= 0.10 * (i + 1) / 32] + [0])
    bh = {(o["rule"], o["k"], o["x"], o["exit"]) for o in prim[:cut]}
    for o in out:
        o["bh"] = o["primary"] and (o["rule"], o["k"], o["x"], o["exit"]) in bh
        o["pass"] = bool(o["primary"] and o["split"] == "VALIDATION" and o["mean"] > 0 and o["lo"] > 0 and o["n"] >= 30
                         and o["dlo"] > 0 and o["bh"])
    with open(HERE / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(out[0].keys())); w.writeheader(); [w.writerow(o) for o in out]
    json.dump(dict(coins=list(coins), oi_start={c: dt.datetime.fromtimestamp(cx["oi_start"] / 1000, UTC).strftime("%Y-%m-%d") for c, cx in coins.items()},
                   passes=[(o["rule"], o["k"], o["x"], o["exit"]) for o in out if o["pass"]]), open(HERE / "summary.json", "w"), indent=1)

if __name__ == "__main__":
    main()
