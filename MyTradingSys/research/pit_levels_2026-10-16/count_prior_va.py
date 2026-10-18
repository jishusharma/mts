"""Count-only pass (NO outcome column) for the chosen experiment: failed auction at the PRIOR UTC DAY's value-area edge
(FAB-4 / TOM-12 family) on BTCUSDT 1m -> 5m closes, DEV only (bar open 2022-01-01 .. 2024-06-30).

Levels: prior-day POC / VAH / VAL per FORMULAS 18.1 (w = 10 USD) from the previous UTC day's 1m bars, static for the
whole day (PIT_CONTRACT.md L1).  The repo builder vp_pivot_probe.build_profile is used when importable (it passed the
leakage test F3); otherwise an independent FORMULAS 18.1 implementation (same arithmetic) is used and said so.

Event T (per side; SHORT at VAH written, LONG at VAL is the mirror): a 5m close ABOVE VAH (price discovery outside
yesterday's value) followed, inside the same UTC day, by the first 5m close BACK BELOW VAH (failed auction).
  entry = that close; stop = the highest high of the excursion bars (Fabio: "Stop was likely somewhere above here",
  the probe extreme, CATALOGUE_AUDIT.md F-1); target = VAL (Fabio: "all the way to the other side of the range").
Control C (location only): the first 5m bar of the day whose high >= VAH (touch), same stop floor, no acceptance check.
Printed: n per arm / side / year, open-inside-VA split, stop % distribution, share with stop >= 0.40 %, geometric R:R
distribution, and the count-only MDE under Tom's SOURCED two-point payoff. Nothing forward of the entry bar is read.
"""
import csv
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
ARCH = Path("F:/MTS/data/tom_raw/klines")
TS0 = 1640995200000                      # 2022-01-01
CUTOFF = 1719792000000                   # 2024-07-01 00:00 UTC: refuse any bar at or after it
NDAYS = 912
MIN = 60000
W = 10.0
STOP_FLOOR = 0.40                        # % of price, TOM_ON_BTC.md:24 (taker legs)
COST_TAKER, COST_MAKER = 0.14, 0.09      # % round trip, PRE_REG 2026-10-15 section 1

try:
    from MyTradingSys.backtest.vp_pivot_probe import build_profile as repo_build_profile
    BUILDER = "repo vp_pivot_probe.build_profile (FORMULAS 18.1)"
except Exception as e:                   # pragma: no cover
    repo_build_profile = None
    BUILDER = f"own FORMULAS 18.1 implementation (repo import failed: {e!r})"

try:
    from MyTradingSys.backtest.power_mde import power_mde
except Exception:                        # pragma: no cover
    power_mde = None


def own_profile(l, h, v, w=W):
    """Independent FORMULAS 18.1: uniform spread of v over [l,h] into bins of width w; POC lowest max bin; 70 % VA."""
    l = np.asarray(l, float); h = np.asarray(h, float); v = np.asarray(v, float)
    ok = ~(np.isnan(l) | np.isnan(h) | np.isnan(v)) & (v > 0)
    l, h, v = l[ok], h[ok], v[ok]
    if len(l) == 0:
        return None
    kl = np.floor(l / w).astype(int); kh = np.floor(h / w).astype(int)
    k0, k1 = int(kl.min()), int(kh.max())
    vol = np.zeros(k1 - k0 + 1)
    for li, hi, vi, a, b in zip(l, h, v, kl, kh):
        if hi > li:
            for k in range(a, b + 1):
                ov = min(hi, (k + 1) * w) - max(li, k * w)
                if ov > 0:
                    vol[k - k0] += vi * ov / (hi - li)
        else:
            vol[a - k0] += vi
    total = vol.sum()
    if total <= 0:
        return None
    ip = int(np.argmax(vol))                   # first (lowest) max
    lo = hi_ = ip; acc = vol[ip]
    while acc < 0.70 * total and (lo > 0 or hi_ < len(vol) - 1):
        vl = vol[lo - 1] if lo > 0 else -1
        vh = vol[hi_ + 1] if hi_ < len(vol) - 1 else -1
        if vl >= vh and lo > 0:
            lo -= 1; acc += vol[lo]
        elif hi_ < len(vol) - 1:
            hi_ += 1; acc += vol[hi_]
        else:
            lo -= 1; acc += vol[lo]
    return {"poc_price": (ip + k0) * w + w / 2, "vah": (hi_ + 1 + k0) * w, "val": (lo + k0) * w}


def profile(l, h, v):
    if repo_build_profile is not None:
        return repo_build_profile(l, h, v, W)
    return own_profile(l, h, v)


def load_dev():
    n = NDAYS * 1440
    A = {k: np.full(n, np.nan) for k in ("O", "H", "L", "C", "V")}
    files = [ARCH / f"BTCUSDT-1m-{y}-{m:02d}.csv" for y, m in
             [(2022, i) for i in range(1, 13)] + [(2023, i) for i in range(1, 13)] + [(2024, i) for i in range(1, 7)]]
    missing = [f.name for f in files if not f.exists()]
    for f in files:
        if not f.exists():
            continue
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                if t >= CUTOFF:
                    raise ValueError(f"bar {t} >= 2024-07-01 refused (VALIDATION/HOLDOUT sealed): {f}")
                i = (t - TS0) // MIN
                if 0 <= i < n:
                    A["O"][i], A["H"][i], A["L"][i], A["C"][i], A["V"][i] = (float(r[1]), float(r[2]), float(r[3]),
                                                                              float(r[4]), float(r[5]))
    return A, missing


def five_min(A, d):
    s = slice(d * 1440, (d + 1) * 1440)
    O, H, L, C = (A[k][s].reshape(288, 5) for k in ("O", "H", "L", "C"))
    bad = np.isnan(O).any(1) | np.isnan(H).any(1) | np.isnan(L).any(1) | np.isnan(C).any(1)
    o, h, l, c = O[:, 0], np.nanmax(H, 1) if not bad.all() else H[:, 0], np.nanmin(L, 1) if not bad.all() else L[:, 0], C[:, -1]
    return o, h, l, c, bad


def main():
    A, missing = load_dev()
    print(f"loader: DEV 912 days, missing files {missing or 'none'}; bars present {int((~np.isnan(A['C'])).sum())} of {NDAYS * 1440}")
    print(f"profile builder: {BUILDER}")
    levels = {}
    for d in range(NDAYS):
        s = slice(d * 1440, (d + 1) * 1440)
        if np.isnan(A["C"][s]).sum() > 5:          # a prior day with > 5 missing minutes gives no level (OURS)
            continue
        p = profile(A["L"][s], A["H"][s], A["V"][s])
        if p:
            levels[d] = p
    print(f"prior-day profiles built: {len(levels)} days")

    T, Cc = [], []
    for d in range(1, NDAYS):
        p = levels.get(d - 1)
        if p is None:
            continue
        o, h, l, c, bad = five_min(A, d)
        if bad.sum() > 1:
            continue
        vah, val, poc = p["vah"], p["val"], p["poc_price"]
        open_inside = val <= o[0] <= vah
        year = 2022 + (d * 86400000 + TS0 - TS0) // 31557600000
        for side, edge, other in ((-1, vah, val), (1, val, vah)):
            outside = False; ext = None; touched = False
            for k in range(288):
                if bad[k]:
                    continue
                hh, ll, cc_ = h[k], l[k], c[k]
                beyond_hi = hh if side == -1 else -ll
                close_s = cc_ * side * -1                     # signed close: > edge_s means outside
                edge_s = edge * side * -1
                if not touched and beyond_hi >= edge_s:
                    touched = True
                    Cc.append(dict(d=d, side=side, k=k, open_inside=open_inside, year=year))
                if close_s > edge_s:
                    if not outside:
                        outside = True; ext = beyond_hi
                    else:
                        ext = max(ext, beyond_hi)
                elif outside and close_s < edge_s:            # first close back inside
                    entry = cc_; stop = ext * (-1 if side == 1 else 1)
                    stop_pct = abs(stop - entry) / entry * 100.0
                    reward = abs(entry - other)
                    rr = reward / abs(stop - entry) if stop != entry else float("inf")
                    T.append(dict(d=d, side=side, k=k, entry=entry, stop=stop, stop_pct=stop_pct, rr=rr,
                                  open_inside=open_inside, year=year, excursion_bars=0))
                    outside = False; ext = None
    T = np.array([(e["d"], e["side"], e["k"], e["stop_pct"], e["rr"], e["open_inside"], e["year"]) for e in T], float)
    print(f"\nT (failed auction at prior-day VA edge, 5m closes): n = {len(T)} over {len(np.unique(T[:, 0]))} days")
    for sd in (-1, 1):
        m = T[:, 1] == sd
        print(f"  side {'SHORT@VAH' if sd == -1 else 'LONG@VAL':10s} n = {int(m.sum())}")
    for y in (2022, 2023, 2024):
        print(f"  year {y}: n = {int((T[:, 6] == y).sum())}")
    print(f"  open inside prior VA: n = {int(T[:, 5].sum())}; open outside: n = {int((T[:, 5] == 0).sum())}")
    first = {}
    for row in T:
        first.setdefault((row[0], row[1]), row)
    print(f"  first event per day and side: n = {len(first)}")
    sp = T[:, 3]
    q = np.percentile(sp, [10, 25, 50, 75, 90])
    print(f"  stop % of price: p10 {q[0]:.3f} p25 {q[1]:.3f} median {q[2]:.3f} p75 {q[3]:.3f} p90 {q[4]:.3f}")
    feas = sp >= STOP_FLOOR
    print(f"  stop >= {STOP_FLOOR} %: n = {int(feas.sum())} ({feas.mean() * 100:.1f} %); cost in R at the median stop: taker {COST_TAKER / q[2]:.2f} R, maker-in {COST_MAKER / q[2]:.2f} R")
    rr = T[:, 4]
    qr = np.percentile(rr[np.isfinite(rr)], [25, 50, 75])
    print(f"  geometric R:R to the other VA edge: p25 {qr[0]:.2f} median {qr[1]:.2f} p75 {qr[2]:.2f}")
    fe = T[feas]
    if len(fe):
        qf = np.percentile(fe[:, 3], [25, 50, 75]); qfr = np.percentile(fe[np.isfinite(fe[:, 4]), 4], [25, 50, 75])
        print(f"  FEASIBLE subset (stop >= 0.40 %): n = {len(fe)}, days {len(np.unique(fe[:, 0]))}, stop median {qf[1]:.3f} % (p25 {qf[0]:.3f}, p75 {qf[2]:.3f}), R:R median {qfr[1]:.2f} (p25 {qfr[0]:.2f}, p75 {qfr[2]:.2f}), open-inside n = {int(fe[:, 5].sum())}")
        for y in (2022, 2023, 2024):
            print(f"    year {y}: n = {int((fe[:, 6] == y).sum())}")
        n = len(fe); stop_med = qf[1]; rr_med = qfr[1]
        cost_r = COST_TAKER / stop_med
        # plausible gross effect: Tom's SOURCED intraday swing numbers (hQ8sOq67x5o: 35 % win, 4 R) => +0.75 R per trade;
        # at the setup's own median R:R the implied win rate for the same +0.75 R is p = 1.75 / (rr + 1).
        p_impl = min(0.95, 1.75 / (rr_med + 1.0))
        if power_mde is not None:
            res = power_mde(p_impl, rr_med, cost_r, n)
            print(f"  count-only power (power_mde.py, two-point payoff p={p_impl:.3f}, rr={rr_med:.2f}, cost_R={cost_r:.3f}, n={n}): {res}")
        sd = math.sqrt(p_impl * (1 - p_impl)) * (rr_med + 1.0)
        mde = 2.8 * sd / math.sqrt(n)
        print(f"  MDE (80 % power, 2.8 x sd/sqrt n, sd = {sd:.2f} R): {mde:.3f} R; cost {cost_r:.3f} R; MDE + cost = {mde + cost_r:.3f} R vs plausible gross +0.75 R -> {'FREEZE OK' if mde + cost_r <= 0.75 else 'DO NOT FREEZE'}")
    Cc = np.array([(e["d"], e["side"], e["k"], e["open_inside"], e["year"]) for e in Cc], float)
    print(f"\nC (first touch of the prior-day VA edge per side and day, location only): n = {len(Cc)} over {len(np.unique(Cc[:, 0]))} days; open-inside n = {int(Cc[:, 3].sum())}")
    for y in (2022, 2023, 2024):
        print(f"  year {y}: n = {int((Cc[:, 4] == y).sum())}")
    print("\nNo outcome column was computed; nothing after the entry bar was read.")


if __name__ == "__main__":
    main()
