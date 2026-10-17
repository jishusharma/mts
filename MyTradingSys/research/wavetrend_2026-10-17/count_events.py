"""Count-only pass for the WaveTrend PRE_REG (card wavetrend-prereg-counts). DEV only (< 2024-07-01).

Reads open/high/low/close/volume of Binance BTCUSDT 1m klines, resamples to 5m/15m/1h/4h/1d, computes WT with the
parity reference (wt_parity_ref.py, contract PARITY_CONTRACT.md s3) and counts causal events (ATLAS_STUDY_SPEC.md s2).
NO return, MFE/MAE or hit-rate is computed anywhere; the only price-derived outputs are event timestamps and context bins.
Event at index t uses bars <= t only (pivot events are confirmed at p+k, never at p).

Usage: python count_events.py --out <dir>      writes counts_*.csv + SELECTION.md inputs
"""
import argparse
import csv
import datetime as dt
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ARCH = Path("F:/MTS/data/tom_raw/klines")
MS = 60_000
TS0 = int(dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
CUTOFF_MS = int(dt.datetime(2024, 7, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
NDAYS = 912
TFS = {"5m": 5, "15m": 15, "1h": 60, "4h": 240, "1d": 1440}
HTF = {"5m": "15m", "15m": "1h", "1h": "4h", "4h": "1d", "1d": None}
WARMUP = 200

_spec = importlib.util.spec_from_file_location("wt_parity_ref", HERE / "wt_parity_ref.py")
ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ref)


# ------------------------------------------------------------------ data
def load_dev(files):
    n = NDAYS * 1440
    A = {k: np.full(n, np.nan) for k in "OHLCV"}
    for f in files:
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.reader(fh):
                if not r or not r[0][:1].isdigit():
                    continue
                t = int(float(r[0]))
                if t > 1e14:
                    t //= 1000
                if t >= CUTOFF_MS:
                    raise ValueError(f"bar {t} >= 2024-07-01 refused (VALIDATION/HOLDOUT sealed): {f}")
                i = (t - TS0) // MS
                if 0 <= i < n:
                    A["O"][i], A["H"][i], A["L"][i], A["C"][i], A["V"][i] = (float(r[1]), float(r[2]), float(r[3]),
                                                                              float(r[4]), float(r[5]))
    return A


def resample(A, m):
    n = len(A["O"]) // m
    sh = lambda k: A[k][: n * m].reshape(n, m)
    return {"O": sh("O")[:, 0], "H": sh("H").max(axis=1), "L": sh("L").min(axis=1),
            "C": sh("C")[:, -1], "V": sh("V").sum(axis=1)}      # any NaN 1m bar -> NaN bar (no bridging)


# ------------------------------------------------------------------ indicator
def wt_series(B):
    """wt1, wt2 with output masked until WARMUP valid bars since series start / last gap (PARITY_CONTRACT s3)."""
    h, l, c = B["H"], B["L"], B["C"]
    wt1, wt2 = ref.wavetrend(list(h), list(l), list(c))
    wt1, wt2 = np.array(wt1), np.array(wt2)
    ok = ~np.isnan(c) & ~np.isnan(h) & ~np.isnan(l)
    run = 0
    mask = np.zeros(len(c), bool)
    for i, o in enumerate(ok):
        run = run + 1 if o else 0
        mask[i] = run > WARMUP
    wt1[~mask] = np.nan
    wt2[~mask] = np.nan
    return wt1, wt2


def ema_np(x, n):
    a = 2.0 / (n + 1)
    out = np.full(len(x), np.nan)
    p = None
    for i, v in enumerate(x):
        if np.isnan(v):
            p = None
            continue
        p = v if p is None else a * v + (1 - a) * p
        out[i] = p
    return out


# ------------------------------------------------------------------ events (each returns list of (t, side))
def ev_cross(wt1, wt2):
    return np.array(ref.cross_events(wt1.tolist(), wt2.tolist(), "le"))


def ev_A(wt1, L, R):
    """A1 arrivals, A2 first turn inside the open episode, A4 re-entries. side +1 upper zone, -1 lower."""
    n = len(wt1)
    A1, A2, A4 = [], [], []
    for sgn in (1, -1):
        x = sgn * wt1
        out_run = 0           # consecutive valid bars below L
        in_ep, turned = False, False
        for t in range(n):
            v = x[t]
            if np.isnan(v):
                in_ep, turned, out_run = False, False, 0
                continue
            if v >= L:
                if not in_ep:
                    if out_run >= R:
                        A1.append((t, sgn)); in_ep, turned = True, False
                    else:
                        in_ep, turned = True, True     # flicker re-entry: part of no new episode, no A2 either
                elif not turned and not np.isnan(x[t - 1]) and v < x[t - 1]:
                    A2.append((t, sgn)); turned = True
                out_run = 0
            else:
                if in_ep:
                    A4.append((t, sgn))
                in_ep = False
                out_run += 1
    return A1, A2, A4


def ev_A3(wt1, cross, L):
    out = []
    for t in range(1, len(wt1)):
        if cross[t] != 0 and not np.isnan(wt1[t - 1]):
            if wt1[t - 1] >= L and cross[t] == -1:
                out.append((t, 1))
            elif wt1[t - 1] <= -L and cross[t] == 1:
                out.append((t, -1))
    return out


def ev_B1(wt1):
    return [(t, 1 if wt1[t] > 0 else -1) for t in range(1, len(wt1))
            if not np.isnan(wt1[t]) and not np.isnan(wt1[t - 1]) and wt1[t] * wt1[t - 1] < 0]


def ev_B2(wt1, c):
    """came from side s (|wt1|>c), touched |wt1|<=c, leaves on side s: event at the leaving bar, side s."""
    out = []
    s0, touching = 0, False
    for t in range(len(wt1)):
        v = wt1[t]
        if np.isnan(v):
            s0, touching = 0, False
            continue
        if abs(v) > c:
            sg = 1 if v > 0 else -1
            if touching and sg == s0:
                out.append((t, sg))
            s0, touching = sg, False
        elif s0 != 0:
            touching = True
    return out


def pivots(x, k, hi=True):
    """confirmed pivots as (p, t_confirm=p+k): x[p] strictly beyond the k bars to the left, not beyond the k bars to the right."""
    out = []
    n = len(x)
    for p in range(k, n - k):
        w = x[p - k:p + k + 1]
        if np.isnan(w).any():
            continue
        left, right = w[:k], w[k + 1:]
        if hi:
            if x[p] > left.max() and x[p] >= right.max():
                out.append((p, p + k))
        else:
            if x[p] < left.min() and x[p] <= right.min():
                out.append((p, p + k))
    return out


def ev_C(B, wt1, k, G, L):
    """C1 regular divergence at price-pivot confirmation; C2 lower second WT peak in the band. side +1 = upper (bearish)."""
    C1, C2 = [], []
    for hi, sgn in ((True, 1), (False, -1)):
        pp = pivots(B["H"] if hi else B["L"], k, hi)
        prev = None
        for p, t in pp:
            if prev is not None and p - prev <= G and not np.isnan(wt1[p]) and not np.isnan(wt1[prev]):
                price_more = (B["H"][p] > B["H"][prev]) if hi else (B["L"][p] < B["L"][prev])
                wt_less = (sgn * wt1[p] < sgn * wt1[prev]) and sgn * wt1[prev] > 0 and sgn * wt1[p] > 0
                if price_more and wt_less:
                    C1.append((t, sgn))
            prev = p
        wp = pivots(wt1 * sgn, k, True)       # peaks of sgn*wt1
        prev = None
        for p, t in wp:
            if prev is not None and p - prev <= G and wt1[prev] * sgn >= L and wt1[p] * sgn >= L and wt1[p] * sgn < wt1[prev] * sgn:
                C2.append((t, sgn))
            prev = p
    C1.sort(); C2.sort()
    return C1, C2


# ------------------------------------------------------------------ context (bars <= t only)
def context(B, wt1, m, htf_wt1, m_h):
    n = len(B["C"])
    c = B["C"]
    lr = np.full(n, np.nan)
    lr[1:] = np.log(c[1:] / c[:-1])
    vol = np.full(n, np.nan)
    for t in range(100, n):
        w = lr[t - 99:t + 1]
        if not np.isnan(w).any():
            vol[t] = w.std()
    e = ema_np(c, 200)
    valid200 = np.zeros(n, bool)
    run = 0
    for i in range(n):
        run = run + 1 if not np.isnan(c[i]) else 0
        valid200[i] = run > 200
    e[~valid200] = np.nan
    slope = np.full(n, np.nan)
    slope[10:] = e[10:] - e[:-10]
    trend = np.full(n, 0, int)         # +1 up, -1 down, 0 mixed, 9 NA
    na = np.isnan(e) | np.isnan(slope)
    trend[(c > e) & (slope > 0)] = 1
    trend[(c < e) & (slope < 0)] = -1
    trend[na] = 9
    slot = max(1, 1440 // m)
    v = B["V"]
    part = np.full(n, np.nan)
    if m < 1440:
        for t in range(20 * slot, n):
            past = v[t - 20 * slot:t:slot]
            if not np.isnan(past).any() and not np.isnan(v[t]) and past.mean() > 0:
                part[t] = v[t] / past.mean()
    else:
        for t in range(20, n):
            past = v[t - 20:t]
            if not np.isnan(past).any() and not np.isnan(v[t]) and past.mean() > 0:
                part[t] = v[t] / past.mean()
    hour = (((np.arange(n) + 1) * m) % 1440) // 60            # UTC hour of the bar close (0 for day close)
    hour3 = np.where(m >= 1440, 9, (hour // 8))                # 1d: not defined
    htf = np.full(n, np.nan)
    if htf_wt1 is not None:
        idx = ((np.arange(n) + 1) * m) // m_h - 1
        ok = idx >= 0
        htf[ok] = htf_wt1[idx[ok]]
    return {"vol": vol, "trend": trend, "part": part, "hour3": hour3, "htf": htf}


def tercile_edges(x):
    v = x[~np.isnan(x)]
    return (float(np.quantile(v, 1 / 3)), float(np.quantile(v, 2 / 3))) if len(v) else (np.nan, np.nan)


def bin_of(ctx, edges, t, side):
    """context bins for one event at t with event side (+1/-1). Returns dict var -> bin label or None."""
    r = {}
    vv = ctx["vol"][t]
    r["vol"] = None if np.isnan(vv) else ("vol_lo", "vol_mid", "vol_hi")[int(vv > edges["vol"][0]) + int(vv > edges["vol"][1])]
    tr = ctx["trend"][t]
    r["trend"] = None if tr == 9 else ("trend_against", "trend_mixed", "trend_with")[int(np.sign(tr * side)) + 1]
    pv = ctx["part"][t]
    r["part"] = None if np.isnan(pv) else ("part_lo", "part_mid", "part_hi")[int(pv > edges["part"][0]) + int(pv > edges["part"][1])]
    h = ctx["hour3"][t]
    r["hour"] = None if h == 9 else ("utc00_08", "utc08_16", "utc16_24")[int(h)]
    hv = ctx["htf"][t]
    if np.isnan(hv):
        r["htf"] = None
    else:
        sv = side * hv
        r["htf"] = "htf_with" if sv >= 53 else ("htf_against" if sv <= -53 else "htf_mid")
    return r


# ------------------------------------------------------------------ main
def mde_d(n_days, m_holm=12, power_z=0.8416):
    from statistics import NormalDist
    z = NormalDist().inv_cdf(1 - 0.05 / (2 * m_holm))
    return (z + power_z) / np.sqrt(n_days) if n_days > 0 else float("inf")


def run(out_dir, params):
    files = sorted(ARCH.glob("BTCUSDT-1m-202[234]-*.csv"))
    files = [f for f in files if f.stem[-7:] < "2024-07"]
    A = load_dev(files)
    rows, qlines, series = [], [], {}
    wts = {}
    Bs = {}
    for tf, m in TFS.items():
        B = resample(A, m)
        Bs[tf] = B
        wts[tf] = wt_series(B)
        qlines.append(f"{tf}: bars {len(B['C'])}, NaN bars {int(np.isnan(B['C']).sum())}, valid wt1 {int((~np.isnan(wts[tf][0])).sum())}")
    R, c_, k, G = params["R_out"], params["c"], params["k"], params["G"]
    res = {}
    for tf, m in TFS.items():
        B = Bs[tf]
        wt1, wt2 = wts[tf]
        h = HTF[tf]
        ctx = context(B, wt1, m, wts[h][0] if h else None, TFS[h] if h else None)
        edges = {"vol": tercile_edges(ctx["vol"]), "part": tercile_edges(ctx["part"])}
        cross = ev_cross(wt1, wt2)
        ties = int(np.sum((wt1 == wt2) & ~np.isnan(wt1)))
        evs = {}
        for L in (53, 60):
            a1, a2, a4 = ev_A(wt1, L, R)
            evs[f"A1_L{L}"], evs[f"A2_L{L}"], evs[f"A4_L{L}"] = a1, a2, a4
            evs[f"A3_L{L}"] = ev_A3(wt1, cross, L)
        evs["B1"] = ev_B1(wt1)
        evs["B2"] = ev_B2(wt1, c_)
        c1, c2 = ev_C(B, wt1, k, G, 53)
        evs["C1"], evs["C2"] = c1, c2
        res[tf] = {"ctx": ctx, "edges": edges, "evs": evs, "ties": ties, "n": len(wt1)}
        qlines.append(f"{tf}: tie bars wt1==wt2 {ties}; terciles vol {edges['vol']} part {edges['part']}")
    return res, qlines, Bs


def strata(res):
    """size of the random-clock pool per TF x vol bin x hour-of-day slot (arm 4 matches on these; bars with valid features)."""
    out = []
    for tf, m in TFS.items():
        ctx, edges = res[tf]["ctx"], res[tf]["edges"]
        n = res[tf]["n"]
        slots = max(1, 1440 // m) if m < 1440 else 1
        cnt = {}
        for t in range(n):
            vv = ctx["vol"][t]
            if np.isnan(vv):
                continue
            vb = int(vv > edges["vol"][0]) + int(vv > edges["vol"][1])
            sl = t % slots
            cnt[(vb, sl)] = cnt.get((vb, sl), 0) + 1
        out.append({"tf": tf, "strata": len(cnt), "min_stratum": min(cnt.values()), "median_stratum": int(np.median(list(cnt.values())))})
    return out


def tabulate(res, out_dir):
    out = []
    for tf, m in TFS.items():
        ctx, edges = res[tf]["ctx"], res[tf]["edges"]
        for name, evl in res[tf]["evs"].items():
            days = {}
            def add(key, t, side):
                d = (t * m) // 1440
                e = days.setdefault(key, [0, set(), 0, 0])
                e[0] += 1; e[1].add(d)
                e[2 + (0 if side > 0 else 1)] += 1
            for t, side in evl:
                add(("ALL", "all"), t, side)
                for var, b in bin_of(ctx, edges, t, side).items():
                    if b is not None:
                        add((var, b), t, side)
            for (var, b), (n, ds, up, lo) in days.items():
                out.append({"tf": tf, "event": name, "var": var, "bin": b, "events": n, "event_days": len(ds),
                            "side_up": up, "side_lo": lo, "mde_d": round(float(mde_d(len(ds))), 3)})
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--R", type=int, default=3)
    ap.add_argument("--c", type=float, default=5)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--G", type=int, default=40)
    a = ap.parse_args()
    Path(a.out).mkdir(parents=True, exist_ok=True)
    res, q, _ = run(a.out, {"R_out": a.R, "c": a.c, "k": a.k, "G": a.G})
    tab = tabulate(res, a.out)
    with open(Path(a.out) / f"counts_R{a.R}_c{a.c:g}_k{a.k}_G{a.G}.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tab[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(tab)
    st = strata(res)
    with open(Path(a.out) / "strata.csv", "w", newline="\n", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(st[0].keys()), lineterminator="\n")
        w.writeheader(); w.writerows(st)
    (Path(a.out) / "quality.txt").write_text("\n".join(q) + "\n", newline="\n", encoding="utf-8")
    print("\n".join(q))
