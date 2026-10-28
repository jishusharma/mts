"""Classify the Java-vs-Python prior-day zone mismatches of java_zone_check.py by cause (DEV days, counts only).

Same 48 days, same closed 1m bars, same UTC day for both sides, so the boundary/timezone, intrabar, data-source and
lookback causes are 0 by construction. The remaining causes are measured with counterfactuals:
  edge   : Java reports bin LOWER edges for poc/vah/val; FORMULAS 18.1 reports poc = bin centre, vah = TOP edge of the top bin.
           Convert Java (poc + bin/2, vah + bin) and re-test.
  grid   : Java algorithm (triangular weights) on a fixed 10 USDT grid (origin floor(min/10)*10) instead of the dynamic ~5 grid.
  weight : Python uniform overlap spread on the Java dynamic grid vs the Java triangular weights.
  other  : remainder.
Attribution is sequential in the order edge, grid, weight, other. The Java port is checked against the compiled Java (port_ok).
  python zone_mismatch_classify.py [--every 19]
"""
import argparse
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import level_ledger as LL  # noqa: E402
import java_zone_check as JZ  # noqa: E402

W = 10.0
VA = 0.70


def _va(vals, ip):
    total = float(vals.sum()); target = VA * total
    lo = hi = ip; acc = vals[ip]; last = len(vals) - 1
    while acc < target and (lo > 0 or hi < last):
        vl = vals[lo - 1] if lo > 0 else -1.0
        up = hi + 1
        vh = vals[up] if up <= last else -1.0
        if vl >= vh and lo > 0:
            lo -= 1; acc += vals[lo]
        elif hi < last:
            hi += 1; acc += vals[hi]
        elif lo > 0:
            lo -= 1; acc += vals[lo]
        else:
            break
    return lo, hi


def java_port(h, l, c, v, fixed=0.0):
    """Python port of MarketDataSnapshot.buildVp (triangular weights). Returns (poc, vah, val, bin) as lower-edge keys."""
    minP, maxP = float(l.min()), float(h.max()); rng = maxP - minP
    if fixed > 0:
        bs = fixed; org = np.floor(minP / bs) * bs; nb = max(50, int(np.ceil(rng / bs)) + 1)
    else:
        nb = max(50, int(rng / 5)); bs = rng / nb; org = minP
    if bs <= 0:
        bs = 1.0
    keys = org + np.arange(nb + 1) * bs
    prof = np.zeros(nb + 1)
    for hi, lo, cl, vo in zip(h, l, c, v):
        tp = (hi + lo + cl) / 3.0; hr = (hi - lo) / 2.0
        n = int(max(1, (hi - lo) / bs))
        ps = lo + np.arange(n) * (hi - lo) / n
        w = np.clip(1.0 - np.abs(ps - tp) / hr, 0, None) if hr > 0 else np.zeros(n)
        s = w.sum()
        if s > 0:
            idx = np.clip(np.searchsorted(keys, ps, side="right") - 1, 0, nb)
            np.add.at(prof, idx, vo * w / s)
        else:
            prof[max(0, int(np.searchsorted(keys, tp, side="right")) - 1)] += vo
    ip = int(prof.argmax()); lo, hi = _va(prof, ip)
    return keys[ip], keys[hi], keys[lo], bs, prof


def uniform_on_grid(h, l, v, bs, org, nb):
    prof = np.zeros(nb + 1)
    for hi, lo, vo in zip(h, l, v):
        k0 = int(np.floor((lo - org) / bs)); k1 = max(k0, int(np.ceil((hi - org) / bs)) - 1)
        for k in range(k0, k1 + 1):
            ov = min(hi, org + (k + 1) * bs) - max(lo, org + k * bs)
            prof[min(max(k, 0), nb)] += vo * (ov / (hi - lo) if hi > lo else 1.0)
    ip = int(prof.argmax()); lo_, hi_ = _va(prof, ip)
    return org + ip * bs, org + hi_ * bs, org + lo_ * bs


def standard_profile(h, l, v, w=W):
    """FORMULAS 18.1 reference profile (decision OURS, ZONE_MISMATCH.md): fixed w-USDT grid anchored at multiples of w,
    uniform overlap weighting, poc_price = bin centre, vah = top edge, val = bottom edge. Returns a dict."""
    h = np.asarray(h, float); l = np.asarray(l, float); v = np.asarray(v, float)
    org = np.floor(float(l.min()) / w) * w
    nb = max(0, int(np.ceil((float(h.max()) - org) / w)) - 1)
    poc, vah, val = uniform_on_grid(h, l, v, w, org, nb)
    return {"poc_price": poc + w / 2, "vah": vah + w, "val": val}


def conv(poc, vah, val, bs):
    return {"poc": poc + bs / 2, "vah": vah + bs, "val": val}


def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--every", type=int, default=19)
    a = ap.parse_args(argv)
    import count_prior_va as C
    from MyTradingSys.backtest.vp_pivot_probe import build_profile
    from MyTradingSys.backtest.tom_profile_parity import EngineProfile
    A, _ = C.load_dev()
    cnt = {k: 0 for k in ("total", "match", "mismatch", "edge", "grid", "weight", "tie", "other", "port_ok", "port_n")}
    per = {"poc": dict(cnt), "vah": dict(cnt), "val": dict(cnt)}
    with EngineProfile() as eng:
        for d in range(0, C.NDAYS, a.every):
            s = slice(d * 1440, (d + 1) * 1440)
            if np.isnan(A["L"][s]).sum() > LL.MAX_MISSING:
                continue
            ok = ~np.isnan(A["L"][s])
            t0 = LL.TS0 + d * LL.DAY_MS
            bars = [[int(t0 + int(i) * LL.MIN_MS)] + [float(A[k][d * 1440 + i]) for k in ("O", "H", "L", "C", "V")]
                    for i in np.nonzero(ok)[0]]
            jv = eng.profile(bars)
            L_, H_, C_, V_ = (A[k][s][ok] for k in ("L", "H", "C", "V"))
            py = build_profile(L_, H_, V_, W)
            if jv is None or py is None:
                continue
            lo, hi = float(L_.min()), float(H_.max())
            jb = JZ.java_bin(lo, hi); tol = max(jb, W)
            port = java_port(H_, L_, C_, V_)
            fx = java_port(H_, L_, C_, V_, fixed=W)
            org = lo; nb = max(50, int((hi - lo) / 5))
            uni = uniform_on_grid(H_, L_, V_, jb, org, nb)
            pyv = {"poc": py["poc_price"], "vah": py["vah"], "val": py["val"]}
            jc = conv(*port[:3], port[3]); fc = conv(*fx[:3], fx[3])
            uc = conv(*uni, jb)
            for i, k in enumerate(("poc", "vah", "val")):
                p = per[k]; p["total"] += 1
                p["port_n"] += 1; p["port_ok"] += abs(port[i] - float(jv[k])) <= 0.011 + 1e-9
                if abs(float(jv[k]) - pyv[k]) <= tol:
                    p["match"] += 1; continue
                p["mismatch"] += 1
                if abs(jc[k] - pyv[k]) <= tol:
                    p["edge"] += 1
                elif abs(fc[k] - pyv[k]) <= tol:
                    p["grid"] += 1
                elif abs(uc[k] - jc[k]) > tol:
                    p["weight"] += 1
                else:
                    p["other"] += 1
    keys = ("total", "match", "mismatch", "edge", "grid", "weight", "other", "port_ok", "port_n")
    print("level " + " ".join(f"{k:>9}" for k in keys))
    tot = {k: 0 for k in keys}
    for lv in ("poc", "vah", "val"):
        print(f"{lv:5} " + " ".join(f"{per[lv][k]:9d}" for k in keys))
        for k in keys:
            tot[k] += per[lv][k]
    print("all   " + " ".join(f"{tot[k]:9d}" for k in keys))


if __name__ == "__main__":
    main()
