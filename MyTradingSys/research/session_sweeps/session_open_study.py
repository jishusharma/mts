"""BTC session-open / pre-US sweep DESCRIPTIVE study (T054 + T058). Session MTS-2026-10-03-2051Z-APP-ANA-btc-session-sweeps.

PRE-REGISTRATION (written before the first run, 2026-10-04; nothing below is tuned after seeing results):
Status: descriptive (H3-S1 class). No trade rule, no costs applied, no parameter selection. Result is NOT a verdict.
Data : Binance USDT-M BTCUSDT 1m klines, Dumps/backtest/raw_1m_2022/klines + Dumps/backtest/raw/klines,
       2022-01-03 .. 2026-09-25 (duplicates: keep first, as bt_data.load_klines).
Days : UTC date D with fabio v3 day_gates.ny_open_utc(D) not None (Mon-Fri, DST-aware 13:30/14:30 UTC, US_CLOSED)
       and D not in NYSE_EXTRA (2022-01..2024-12-23 closures + 13:00 ET early closes; from memory, VERIFY).
       A day is dropped if [00:00 UTC, O+390) misses > 5 minutes.
Anchors: A = 00:00 UTC, L = day_gates.london_open_utc(D), O = NY cash open, E = O + 390 min (cash close).
Tests (the ENTIRE set; all reported, none selected):
 T1 volume and |15m return| by fixed UTC 15-min bucket, split US-DST vs US-standard days. If the peak bucket moves
    13:30 -> 14:30 with DST, the US cash open (not a UTC clock time) drives it.            [operator: US open special]
 T2 first-k persistence, k in {10,15,30}: P(sign(c[E]-c[O+k]) == sign(c[O+k]-o[O])). Placebo: same at the 24 fixed
    UTC hh:00 anchors and at L and O-60, k=15, horizon 390.                               [operator: first 10-15 min]
 T3 London sweep of the Asia range [A,L): class at O (swept high and back below Asia high / swept low and back above /
    break-hold / both / none) -> P(US session up = c[E] > o[O]). T3b same with previous-UTC-day high/low over [A,O).
                                                                                         [operator: pre-US sweep]
 T4 open sweep: [O,O+30) trades beyond the pre-US range [A,O) and c[O+30] is back inside -> P(rest up), rest =
    c[E] vs c[O+30]. Placebo anchors: L (ref [A,L)) and O+180 (ref [A,O+180)).          [operator: sweep then real move]
 T5 Tom opening range: IB = [O,O+30) high-low (30 min: Fabio StaphlRH8NQ:192-193); size relative to the median of the
    previous 20 valid days (Tom Ld1dhjGdTCA:19 "same as in the previous days"; 20 = reporting choice, NO-SOURCE).
    Terciles (whole sample, ex-post, reporting only). Outcome: trend day |c[E]-o[O]|/(H-L)[O,E) >= 0.6
    (day_gates.TREND_RATIO, reporting only); IB broken on 0/1/2 sides after O+30.
    Tom Fj4FDZQxw0I:19: "If it's very large, it likely won't hold. If it's very small, it likely will."
 Stability: per calendar year for T2(k=15), T3, T4, T5. A sign flip across years = unstable.
 Statistics: Wilson 95% CI on proportions; n = days. Overlap: one observation per day, so no overlap within a test.
"""
import bisect
import csv
import datetime as dt
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from MyTradingSys.backtest.layers.fabio.v3 import day_gates as G  # noqa: E402

MIN = 60000
DAY = 86400000
DIRS = [ROOT / "Dumps/backtest/raw_1m_2022/klines", ROOT / "Dumps/backtest/raw/klines"]
OUT = Path(__file__).resolve().parent / "results_2026-10-04.json"
NYSE_EXTRA = frozenset(dt.date(*x) for x in (
    (2022, 1, 17), (2022, 2, 21), (2022, 4, 15), (2022, 5, 30), (2022, 6, 20), (2022, 7, 4), (2022, 9, 5),
    (2022, 11, 24), (2022, 11, 25), (2022, 12, 26),
    (2023, 1, 2), (2023, 1, 16), (2023, 2, 20), (2023, 4, 7), (2023, 5, 29), (2023, 6, 19), (2023, 7, 3), (2023, 7, 4),
    (2023, 9, 4), (2023, 11, 23), (2023, 11, 24), (2023, 12, 25),
    (2024, 1, 1), (2024, 1, 15), (2024, 2, 19), (2024, 3, 29), (2024, 5, 27), (2024, 6, 19), (2024, 7, 3), (2024, 7, 4),
    (2024, 9, 2), (2024, 11, 28), (2024, 11, 29)))


def load():
    rows = {}
    for d in DIRS:
        for f in sorted(d.glob("*.csv")):
            with open(f, newline="", encoding="utf-8") as fh:
                for r in csv.reader(fh):
                    if not r or not r[0].isdigit():
                        continue
                    t = int(r[0])
                    if t not in rows:
                        rows[t] = (float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5]))
    T = sorted(rows)
    return T, [rows[t] for t in T]


class Bars:
    def __init__(self, T, R):
        self.T, self.O = T, [r[0] for r in R]
        self.H, self.L = [r[1] for r in R], [r[2] for r in R]
        self.C, self.V = [r[3] for r in R], [r[4] for r in R]

    def span(self, t0, t1):
        return bisect.bisect_left(self.T, t0), bisect.bisect_left(self.T, t1)

    def missing(self, t0, t1):
        i0, i1 = self.span(t0, t1)
        return (t1 - t0) // MIN - (i1 - i0)

    def hi(self, t0, t1):
        i0, i1 = self.span(t0, t1)
        return max(self.H[i0:i1]) if i1 > i0 else None

    def lo(self, t0, t1):
        i0, i1 = self.span(t0, t1)
        return min(self.L[i0:i1]) if i1 > i0 else None

    def open_at(self, t):
        i = bisect.bisect_left(self.T, t)
        return self.O[i] if i < len(self.T) and self.T[i] - t <= 2 * MIN else None

    def close_at(self, t):
        """Close of the last bar that ENDS at or before t (bar open < t)."""
        i = bisect.bisect_left(self.T, t) - 1
        return self.C[i] if i >= 0 and t - self.T[i] <= 3 * MIN else None

    def vol(self, t0, t1):
        i0, i1 = self.span(t0, t1)
        return math.fsum(self.V[i0:i1])


def ms(x):
    return int(x.timestamp() * 1000)


def wilson(k, n):
    if n == 0:
        return None, None, None
    p, z = k / n, 1.96
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(p, 4), round(c - h, 4), round(c + h, 4)


def prop(flags):
    flags = [f for f in flags if f is not None]
    p, lo, hi = wilson(sum(flags), len(flags))
    return {"n": len(flags), "p": p, "ci": [lo, hi]}


def sgn(x):
    return (x > 0) - (x < 0)


def persistence(b, a, k, horizon=390):
    o, ck, ce = b.open_at(a), b.close_at(a + k * MIN), b.close_at(a + horizon * MIN)
    if None in (o, ck, ce):
        return None
    s1, s2 = sgn(ck - o), sgn(ce - ck)
    return None if s1 == 0 or s2 == 0 else s1 == s2


def sweep_class(hi_w, lo_w, ref_hi, ref_lo, c_end):
    sh, sl = hi_w > ref_hi, lo_w < ref_lo
    if sh and sl:
        return "both"
    if not sh and not sl:
        return "none"
    if sh:
        return "H_sweep_back" if c_end < ref_hi else "H_break_hold"
    return "L_sweep_back" if c_end > ref_lo else "L_break_hold"


def main():
    T, R = load()
    b = Bars(T, R)
    print(f"bars {len(T)}  {dt.datetime.utcfromtimestamp(T[0]/1000)} .. {dt.datetime.utcfromtimestamp(T[-1]/1000)}")
    d, d_end = dt.date(2022, 1, 3), dt.date(2026, 9, 25)
    days, dropped = [], 0
    while d <= d_end:
        op = G.ny_open_utc(d)
        if op is not None and d not in NYSE_EXTRA:
            A = ms(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc))
            O = ms(op)
            if b.missing(A, O + 390 * MIN) > 5 or b.missing(A - DAY, A) > 10:
                dropped += 1
            else:
                days.append((d, A, ms(G.london_open_utc(d)), O, G.us_dst(d)))
        d += dt.timedelta(days=1)
    print(f"days {len(days)} dropped {dropped}")
    res = {"days": len(days), "dropped": dropped}

    # T1 by fixed UTC 15-min bucket
    t1 = {}
    for reg in (True, False):
        acc_v, acc_r = [[] for _ in range(96)], [[] for _ in range(96)]
        for (d, A, L, O, dst) in days:
            if dst != reg:
                continue
            dayv = b.vol(A, A + DAY) / 96 or None
            for j in range(96):
                t0 = A + j * 15 * MIN
                o, c = b.open_at(t0), b.close_at(t0 + 15 * MIN)
                if o and c and dayv:
                    acc_v[j].append(b.vol(t0, t0 + 15 * MIN) / dayv)
                    acc_r[j].append(abs(math.log(c / o)))
        base_r = statistics.fmean(x for a in acc_r for x in a)
        rows = [(j, statistics.fmean(acc_v[j]), statistics.fmean(acc_r[j]) / base_r) for j in range(96) if acc_v[j]]
        top = sorted(rows, key=lambda r: -r[2])[:6]
        lab = "us_dst" if reg else "us_std"
        t1[lab] = [{"bucket_utc": f"{j*15//60:02d}:{j*15%60:02d}", "vol_x": round(v, 2), "absret_x": round(r, 2)}
                   for j, v, r in top]
        print(lab, t1[lab])
    res["T1"] = t1

    # T2 persistence + placebo
    t2 = {}
    for k in (10, 15, 30):
        t2[f"O_k{k}"] = prop([persistence(b, O, k) for (_, _, _, O, _) in days])
    t2["L_k15"] = prop([persistence(b, L, 15) for (_, _, L, _, _) in days])
    t2["Om60_k15"] = prop([persistence(b, O - 60 * MIN, 15) for (_, _, _, O, _) in days])
    plc = {}
    for hh in range(24):
        plc[f"{hh:02d}:00"] = prop([persistence(b, A + hh * 3600000, 15) for (_, A, _, _, _) in days])
    t2["placebo_utc_k15"] = plc
    ps = sorted(v["p"] for v in plc.values())
    t2["placebo_p_range"] = [ps[0], ps[len(ps) // 2], ps[-1]]
    moves = [abs(math.log(b.close_at(O + 390 * MIN) / b.close_at(O + 15 * MIN))) * 1e4 for (_, _, _, O, _) in days
             if b.close_at(O + 390 * MIN) and b.close_at(O + 15 * MIN)]
    t2["median_abs_rest_move_bp"] = round(statistics.median(moves), 1)
    print("T2", {k: v for k, v in t2.items() if k != "placebo_utc_k15"})
    res["T2"] = t2

    # T3 / T3b / T4 / T5 per day, then aggregate (overall + per year)
    recs = []
    for (d, A, L, O, dst) in days:
        E = O + 390 * MIN
        oO, cO, cE, c30 = b.open_at(O), b.close_at(O), b.close_at(E), b.close_at(O + 30 * MIN)
        if None in (oO, cO, cE, c30):
            continue
        AH, AL, LH, LL = b.hi(A, L), b.lo(A, L), b.hi(L, O), b.lo(L, O)
        PH, PL, PDH, PDL = b.hi(A, O), b.lo(A, O), b.hi(A - DAY, A), b.lo(A - DAY, A)
        IBH, IBL = b.hi(O, O + 30 * MIN), b.lo(O, O + 30 * MIN)
        UH, UL = b.hi(O, E), b.lo(O, E)
        RH, RL = b.hi(O + 30 * MIN, E), b.lo(O + 30 * MIN, E)
        r = {"d": d, "y": d.year, "us_up": cE > oO, "rest_up": cE > c30,
             "t3": sweep_class(LH, LL, AH, AL, cO),
             "t3b": sweep_class(PH, PL, PDH, PDL, cO),
             "t4": sweep_class(IBH, IBL, PH, PL, c30),
             "ibw": (IBH - IBL) / oO,
             "trend": (abs(cE - oO) / (UH - UL) >= G.TREND_RATIO) if UH > UL else None,
             "ib_sides": (RH > IBH) + (RL < IBL)}
        # placebo T4 at L (ref Asia range) and at O+180 (ref [A, O+180))
        cL30, cLE = b.close_at(L + 30 * MIN), b.close_at(L + 390 * MIN)
        r["t4_L"] = sweep_class(b.hi(L, L + 30 * MIN), b.lo(L, L + 30 * MIN), AH, AL, cL30) if cL30 else None
        r["t4_L_rest_up"] = (cLE > cL30) if (cL30 and cLE) else None
        P0 = O + 180 * MIN
        cP30, cPE = b.close_at(P0 + 30 * MIN), b.close_at(P0 + 390 * MIN)
        r["t4_P"] = (sweep_class(b.hi(P0, P0 + 30 * MIN), b.lo(P0, P0 + 30 * MIN), b.hi(A, P0), b.lo(A, P0), cP30)
                     if cP30 else None)
        r["t4_P_rest_up"] = (cPE > cP30) if (cP30 and cPE) else None
        recs.append(r)
    # T5 relative IB size vs previous 20 valid days
    for i, r in enumerate(recs):
        prev = [x["ibw"] for x in recs[max(0, i - 20):i]]
        r["ib_rel"] = r["ibw"] / statistics.median(prev) if len(prev) == 20 else None
    rel = sorted(r["ib_rel"] for r in recs if r["ib_rel"] is not None)
    q1, q2 = rel[len(rel) // 3], rel[2 * len(rel) // 3]
    for r in recs:
        x = r["ib_rel"]
        r["ib_terc"] = None if x is None else ("small" if x < q1 else "large" if x >= q2 else "mid")

    def classes(key, out_key, sub):
        o = {"base": prop([r[out_key] for r in sub if r.get(key) is not None])}
        for c in ("H_sweep_back", "L_sweep_back", "H_break_hold", "L_break_hold", "both", "none"):
            o[c] = prop([r[out_key] for r in sub if r.get(key) == c])
        return o

    years = sorted({r["y"] for r in recs})
    res["T3_london_sweep_asia"] = {"all": classes("t3", "us_up", recs)}
    res["T3b_pre_sweep_prevday"] = {"all": classes("t3b", "us_up", recs)}
    res["T4_open_sweep_pre"] = {"all": classes("t4", "rest_up", recs)}
    res["T4_placebo_L"] = {"all": classes("t4_L", "t4_L_rest_up", recs)}
    res["T4_placebo_Op180"] = {"all": classes("t4_P", "t4_P_rest_up", recs)}
    t5 = {"tercile_cuts": [round(q1, 3), round(q2, 3)]}
    for tc in ("small", "mid", "large"):
        sub = [r for r in recs if r["ib_terc"] == tc]
        t5[tc] = {"trend": prop([r["trend"] for r in sub]),
                  "ib_broken_both": prop([r["ib_sides"] == 2 for r in sub]),
                  "ib_broken_none": prop([r["ib_sides"] == 0 for r in sub])}
    res["T5_tom_opening_range"] = {"all": t5}
    for y in years:
        sub = [r for r in recs if r["y"] == y]
        ys = str(y)
        res["T3_london_sweep_asia"][ys] = classes("t3", "us_up", sub)
        res["T3b_pre_sweep_prevday"][ys] = classes("t3b", "us_up", sub)
        res["T4_open_sweep_pre"][ys] = classes("t4", "rest_up", sub)
        res["T5_tom_opening_range"][ys] = {tc: prop([r["trend"] for r in sub if r["ib_terc"] == tc])
                                           for tc in ("small", "mid", "large")}
        res["T2"].setdefault("by_year_O_k15", {})[ys] = prop(
            [persistence(b, O, 15) for (dd, _, _, O, _) in days if dd.year == y])
    OUT.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8", newline="\n")
    for k in ("T3_london_sweep_asia", "T3b_pre_sweep_prevday", "T4_open_sweep_pre", "T4_placebo_L", "T4_placebo_Op180"):
        print(k, json.dumps(res[k]["all"]))
    print("T5", json.dumps(res["T5_tom_opening_range"]["all"]))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
