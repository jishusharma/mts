"""H4 (PRE_REG addendum): OI build then unwind on 30m / 1h bars. Writes results_h4.csv, summary_h4.json."""
import csv, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fade as F
import run as R

HERE = Path(__file__).resolve().parent
TFS = {"30m": 1_800_000, "1h": 3_600_000}

def agg(t, o, h, l, c, oit, oiv, tf):
    """15m -> TF bars (complete groups only) + OI at bar close."""
    n = tf // F.BAR
    g = (t // tf).astype(np.int64)
    ug, first, cnt = np.unique(g, return_index=True, return_counts=True)
    ok = cnt == n
    first = first[ok]
    ok2 = np.array([t[f + n - 1] - t[f] == (n - 1) * F.BAR for f in first]) if len(first) else np.array([], bool)
    first = first[ok2]
    T = t[first]
    O = o[first]; C = c[first + n - 1]
    H = np.maximum.reduceat(h, first)[:0] if False else np.array([h[f:f + n].max() for f in first])
    L = np.array([l[f:f + n].min() for f in first])
    idx = np.searchsorted(oit, T + tf)
    okk = idx < len(oit)
    oic = np.full(len(T), np.nan)
    m = okk.copy(); m[okk] = oit[idx[okk]] == (T + tf)[okk]
    oic[m] = oiv[idx[m]]
    return T, O, H, L, C, oic

def h4_events(T, C, oic, atr, N, y, tf):
    """Return dict of index arrays: follow (onset of BUILD), unwind (first drop bar), plus side arrays and build mask."""
    n = len(T)
    ch = np.full(n, np.nan); pc = np.full(n, np.nan)
    ch[N:] = oic[N:] / oic[:-N] - 1
    pc[N:] = C[N:] - C[:-N]
    build = (ch >= y / 100) & (abs(pc) >= atr)
    s = np.where(build, np.sign(pc), 0)
    # onset
    onset = np.zeros(n, bool)
    onset[1:] = build[1:] & (~build[:-1] | (s[1:] != s[:-1]))
    # unwind
    idx = np.arange(n)
    lastb = np.maximum.accumulate(np.where(build, idx, -1))
    lastb_prev = np.full(n, -1); lastb_prev[1:] = lastb[:-1]          # last build at <= j-1
    inwin = (lastb_prev >= idx - N) & (lastb_prev >= 0)
    side_b = np.where(inwin, s[np.maximum(lastb_prev, 0)], 0)
    win = np.lib.stride_tricks.sliding_window_view(oic, N)            # win[k] = oic[k..k+N-1]
    peak = np.full(n, np.nan)
    peak[N:] = np.nanmax(win[:n - N], axis=1) if n > N else peak[N:]   # oic[j-N..j-1]
    prev = np.full(n, np.nan); prev[1:] = oic[:-1]
    unw = inwin & (oic <= peak * 0.995) & (prev > peak * 0.995)
    return dict(onset=np.where(onset)[0], unwind=np.where(unw)[0], s=s, side_b=side_b, build=build, ch=ch)

def dedup(ix, N):
    out, last = [], -10**9
    for i in ix:
        if i - last > N: out.append(int(i)); last = int(i)
    return out

def run_cell(coins, kind, tfn, N, y, hours, placebo=True, reverse=False):
    tf = TFS[tfn]; hold = hours * 3_600_000 // tf
    rows = []
    for c, d in coins.items():
        ev = d["ev"][(tfn, N, y)]
        t = d["bars"][tfn]["T"]; o, h, l, cl = (d["bars"][tfn][k] for k in "OHLC")
        if kind == "H4b":
            ix = [i for i in dedup(ev["onset"], N) if t[i] >= d["oi_start"]]
            sides = {i: int(ev["s"][i]) for i in ix}
        else:
            ix = [i for i in dedup(ev["unwind"], N) if t[i] >= d["oi_start"]]
            sides = {i: int(-ev["side_b"][i]) * (-1 if reverse else 1) for i in ix}
        for e in ix:
            side = sides[e]
            if side == 0: continue
            v = F.fwd_sim(t, o, h, l, cl, d["ft"], d["fr"], e, side, None, None, hold, bar=tf)
            if v is None: continue
            pv = []
            cand = d["pool"][(tfn, N, y)].get(R.month(t[e]), []) if placebo else []
            if len(cand):
                for b in R.nrng.choice(cand, size=min(R.DRAWS, len(cand)), replace=False):
                    r = F.fwd_sim(t, o, h, l, cl, d["ft"], d["fr"], int(b), side, None, None, hold, bar=tf)
                    if r is not None: pv.append(r)
            rows.append((R.split_of(t[e] + tf), int(t[e] // 86400000), v, float(np.mean(pv)) if pv else np.nan, c))
    return rows

def main():
    coins = {}
    for c in R.COINS:
        f = R.DATA / f"{c}USDT.json"
        if not f.exists(): continue
        dd = json.loads(f.read_text())
        k = np.array(dd["kl"], float); t, o, h, l, cl, v = (k[:, i] for i in range(6))
        oi = np.array(dd["oi"], float); oit, oiv = oi[:, 0], oi[:, 1]
        d = dict(ft=[x[0] for x in dd["fund"]], fr=[x[1] for x in dd["fund"]], oi_start=int(oit[0]), bars={}, ev={}, pool={})
        for tfn, tf in TFS.items():
            T, O, H, L, C, oic = agg(t, o, h, l, cl, oit, oiv, tf)
            atr = F.atr_prior(H, L, C)
            d["bars"][tfn] = dict(T=T, O=O, H=H, L=L, C=C)
            for N in (6, 12):
                for y in (1, 2):
                    ev = h4_events(T, C, oic, atr, N, y, tf)
                    d["ev"][(tfn, N, y)] = ev
                    mv = np.full(len(T), np.nan); mv[N:] = abs(oic[N:] / oic[:-N] - 1)
                    okb = ~ev["build"] & (mv < 0.005) & ~np.isnan(atr)
                    pool = {}
                    for b in np.where(okb)[0]: pool.setdefault(R.month(T[b]), []).append(b)
                    d["pool"][(tfn, N, y)] = {m: np.array(x) for m, x in pool.items()}
        coins[c] = d
        print("loaded", c, {k: (len(v["onset"]), len(v["unwind"])) for k, v in d["ev"].items() if k[0] == "1h"}, flush=True)
    cells = [(kind, tfn, N, y, hh, True, False) for kind in ("H4a", "H4b") for tfn in TFS for N in (6, 12) for y in (1, 2) for hh in (4, 12, 24)]
    cells += [("H4a", tfn, N, y, hh, False, True) for tfn in TFS for N in (6, 12) for y in (1, 2) for hh in (4, 12, 24)]
    out = []
    for kind, tfn, N, y, hh, prim, rev in cells:
        rows = run_cell(coins, kind, tfn, N, y, hh, placebo=prim, reverse=rev)
        name = kind + ("_rev" if rev else "")
        for sp, _, _ in R.SPLITS:
            s = R.summarize(rows, sp)
            if s: out.append(dict(hyp=kind if prim else "CTRL", rule=name, tf=tfn, N=N, y=y, hold=hh, split=sp, primary=prim, **s))
        print(name, tfn, N, y, hh, [(o["split"], o["n"], round(o["mean"] * 100, 3)) for o in out[-3:] if o["rule"] == name], flush=True)
    prim = sorted([o for o in out if o["primary"] and o["split"] == "VALIDATION"], key=lambda o: o["p"])
    cut = max([i + 1 for i, o in enumerate(prim) if o["p"] <= 0.10 * (i + 1) / 96] + [0])
    bh = {(o["rule"], o["tf"], o["N"], o["y"], o["hold"]) for o in prim[:cut]}
    for o in out:
        o["bh"] = o["primary"] and (o["rule"], o["tf"], o["N"], o["y"], o["hold"]) in bh
        o["pass"] = bool(o["primary"] and o["split"] == "VALIDATION" and o["mean"] > 0 and o["lo"] > 0 and o["n"] >= 30 and o["dlo"] > 0 and o["bh"])
    with open(HERE / "results_h4.csv", "w", newline="") as f:
        w = csv.DictWriter(f, list(out[0].keys())); w.writeheader(); [w.writerow(o) for o in out]
    json.dump(dict(passes=[(o["rule"], o["tf"], o["N"], o["y"], o["hold"]) for o in out if o["pass"]]), open(HERE / "summary_h4.json", "w"), indent=1)

if __name__ == "__main__":
    main()
