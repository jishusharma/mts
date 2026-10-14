"""EU-session retested low -> broken in the US window? (operator ask 2026-10-14, shot e2379c5fdf2e)

Pre-registered before the first run. Every number below is OURS (our judgement, not a trader's words);
nothing is tuned: one definition, one run, DEV 2022-2024 / VALIDATION 2025 / HOLDOUT 2026 reported side by side.

Anchor (per weekday D): A = US cash open, 13:30Z under US DST, 14:30Z otherwise. T0 = A - 90 min (decision time,
before the 08:30 ET data slot). Lookback = [T0-24h, T0). L = lowest low in the lookback, t1 = its minute.
RETESTED day: some minute t2 in [max(t1+120m, T0-6h), T0) has low <= L*(1+RT) after a bounce: max high in (t1, t2)
>= L*(1+BOUNCE). The T0-6h window = 06:00Z-12:00Z in summer, i.e. the EU session.
SINGLE day (control): same L, no qualifying retest anywhere in [t1+120m, T0).
Both need close(T0-1m) >= L*(1+RT) (price is off the level when we decide).
Outcome window W = [T0, T0+4h) (12:00-16:00Z summer: data slot + cash open + first 2.5 h).
  break   = any low < L in W;   break_deep = any low < L*(1-DEEP).
  after a break: reclaim = a close > L within 120 min of the break minute (sweep), else hold.
Placebo anchors: the same construction with T0 shifted by -12h, -6h, +6h (no US open inside W).
Distance control: d = close(T0-1m)/L - 1 in buckets; RETESTED vs SINGLE compared inside each bucket.

Trade (short at T0 close, RETESTED days and SINGLE days separately):
  flat:   1 unit; stop = max high in [T0-6h, T0) * (1+0.001); target = L*(1-DEEP); time exit T0+4h.
  ladder: units 1,1,2,3 (operator's fixed-fixed-double-triple) at entry, +LAD, +2LAD, +3LAD above entry;
          one stop for all at entry*(1+4LAD); same target / time exit.
  Same-minute stop+target counts as stop. Costs: taker 0.05% per side on every fill (FEE_RT per unit round trip).
  Leverage: return on margin = lev * pnl% of notional; a trade is LIQUIDATED at lev x when its maximum adverse
  excursion (of the average entry) reaches 1/lev - MMR before the exit.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
from pathlib import Path

import numpy as np

MIN = 60000
RT = 0.0020        # OURS: "touched again" = within 0.20% of L
BOUNCE = 0.0060    # OURS: real bounce between the two touches
DEEP = 0.0030      # OURS: meaningful break / short target below L
LAD = 0.0040       # OURS: ladder step
FEE = 0.0005       # Binance taker per side (FORMULAS cost convention)
MMR = 0.005        # OURS: maintenance margin approximation for liquidation
LEVS = (5, 10, 20)
BUCKETS = [(0.002, 0.005), (0.005, 0.01), (0.01, 0.02), (0.02, 0.04), (0.04, 9.0)]


def us_dst(d: dt.date) -> bool:
    mar = dt.date(d.year, 3, 1)
    start = mar + dt.timedelta(days=(6 - mar.weekday()) % 7 + 7)       # 2nd Sunday March
    nov = dt.date(d.year, 11, 1)
    end = nov + dt.timedelta(days=(6 - nov.weekday()) % 7)             # 1st Sunday November
    return start <= d < end


def load(dirs):
    rows = {}
    for d in dirs:
        for f in sorted(Path(d).glob("BTCUSDT-1m-*.csv")):
            with open(f, newline="", encoding="utf-8") as fh:
                for r in csv.reader(fh):
                    if not r or not r[0][:1].isdigit():
                        continue
                    t = int(r[0])
                    if t > 1e14:          # microsecond files
                        t //= 1000
                    rows[t] = (float(r[2]), float(r[3]), float(r[4]))
    ts = np.array(sorted(rows), dtype=np.int64)
    t0 = ts[0]
    n = int((ts[-1] - t0) // MIN) + 1
    H = np.full(n, np.nan); L = np.full(n, np.nan); C = np.full(n, np.nan)
    idx = ((ts - t0) // MIN).astype(np.int64)
    v = np.array([rows[t] for t in ts])
    H[idx], L[idx], C[idx] = v[:, 0], v[:, 1], v[:, 2]
    return int(t0), H, L, C


def day_event(t0, H, L, C, T0):
    """Return dict for decision minute index T0 (index into arrays) or None if data missing."""
    lb = 24 * 60
    if T0 - lb < 0 or T0 + 240 > len(C):
        return None
    lh, ll = H[T0 - lb:T0], L[T0 - lb:T0]
    if np.isnan(ll).sum() > 30 or np.isnan(L[T0:T0 + 240]).sum() > 10:
        return None
    i1 = int(np.nanargmin(ll)); lev = float(ll[i1])
    px = C[T0 - 1]
    if math.isnan(px) or px < lev * (1 + RT):
        return None
    # retest search
    retest_any = None; retest_eu = None
    run_hi = -np.inf
    for j in range(i1 + 1, lb):
        if not math.isnan(lh[j - 1]):
            run_hi = max(run_hi, lh[j - 1])
        if j >= i1 + 120 and run_hi >= lev * (1 + BOUNCE) and ll[j] <= lev * (1 + RT):
            if retest_any is None:
                retest_any = j
            if j >= lb - 360:
                retest_eu = j
                break
    kind = "RETESTED" if retest_eu is not None else ("SINGLE" if retest_any is None else "OTHER")
    w_l = L[T0:T0 + 240]; w_c = C[T0:T0 + 240]
    brk = np.where(w_l < lev)[0]
    out = {"kind": kind, "L": lev, "px": float(px), "d": float(px / lev - 1), "t1_min_before": lb - i1,
           "break": bool(len(brk)), "break_deep": bool((w_l < lev * (1 - DEEP)).any())}
    if len(brk):
        b = int(brk[0])
        after = C[T0 + b: T0 + b + 120]
        out["break_min"] = b
        out["reclaim"] = bool((after > lev).any())
    out["stop_px"] = float(np.nanmax(H[T0 - 360:T0]) * 1.001)
    return out


def sim_short(H, L, C, T0, entry, target, legs, stop):
    """legs = [(trigger_price, units)]; first leg fills at entry. Returns pnl fraction of filled notional,
    filled units, max adverse excursion of the average entry, exit reason."""
    filled = [(entry, legs[0][1])]
    pending = list(legs[1:])
    mae = 0.0
    for k in range(T0, T0 + 240):
        h, l, c = H[k], L[k], C[k]
        if math.isnan(h):
            continue
        while pending and h >= pending[0][0]:
            filled.append(pending.pop(0))
        u = sum(x[1] for x in filled); avg = sum(p * q for p, q in filled) / u
        if h >= stop:
            mae = max(mae, stop / avg - 1)
            return _pnl(filled, stop), u, mae, "stop"
        mae = max(mae, h / avg - 1)
        if l <= target:
            return _pnl(filled, target), u, mae, "target"
    k = T0 + 239
    while math.isnan(C[k]):
        k -= 1
    u = sum(x[1] for x in filled)
    avg = sum(p * q for p, q in filled) / u
    return _pnl(filled, C[k]), u, mae, "time"


def _pnl(filled, exit_px):
    """P&L in base units of notional (1 unit = the first leg), fees on every filled unit. A full 1-1-2-3 ladder
    that stops out loses 7 units' worth, so it weighs 7x a one-unit loser (per-filled-notional averaging hides it)."""
    return sum(q * ((p - exit_px) / p - 2 * FEE) for p, q in filled)


def stats(xs):
    xs = np.asarray(xs, dtype=float)
    if len(xs) < 2:
        return {"n": int(len(xs))}
    m, s = xs.mean(), xs.std(ddof=1)
    return {"n": int(len(xs)), "mean_pct": round(100 * m, 3), "t": round(m / (s / math.sqrt(len(xs))), 2),
            "win": round(float((xs > 0).mean()), 3)}


def wilson(k, n):
    if n == 0:
        return (0, 0, 0)
    p = k / n; z = 1.96
    den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(p, 3), round(c - h, 3), round(c + h, 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dirs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    t0, H, L, C = load(a.dirs)
    first = dt.datetime.fromtimestamp(t0 / 1000, dt.timezone.utc).date()
    last = dt.datetime.fromtimestamp((t0 + (len(C) - 1) * MIN) / 1000, dt.timezone.utc).date()
    res = {"data": [str(first), str(last)], "params": {"RT": RT, "BOUNCE": BOUNCE, "DEEP": DEEP, "LAD": LAD,
                                                      "FEE": FEE, "MMR": MMR}, "anchors": {}}
    events = []
    for shift_h in (0, -12, -6, 6):
        rows = []
        d = first + dt.timedelta(days=2)
        while d <= last:
            if d.weekday() < 5:
                a_min = (13 * 60 + 30) if us_dst(d) else (14 * 60 + 30)
                T0ms = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() * 1000) \
                    + (a_min - 90 + shift_h * 60) * MIN
                T0 = (T0ms - t0) // MIN
                ev = day_event(t0, H, L, C, int(T0))
                if ev:
                    ev["date"] = str(d); ev["year"] = d.year; ev["T0"] = int(T0)
                    rows.append(ev)
            d += dt.timedelta(days=1)
        res["anchors"][str(shift_h)] = summarise(rows)
        if shift_h == 0:
            events = rows
    # trades on the US anchor
    tr = {}
    for kind in ("RETESTED", "SINGLE"):
        flat, lad = [], []
        for ev in (e for e in events if e["kind"] == kind):
            e_px = ev["px"]; tgt = ev["L"] * (1 - DEEP)
            p, u, mae, why = sim_short(H, L, C, ev["T0"], e_px, tgt, [(e_px, 1)], ev["stop_px"])
            flat.append((ev["year"], p, mae, why))
            legs = [(e_px, 1), (e_px * (1 + LAD), 1), (e_px * (1 + 2 * LAD), 2), (e_px * (1 + 3 * LAD), 3)]
            p2, u2, mae2, why2 = sim_short(H, L, C, ev["T0"], e_px, tgt, legs, e_px * (1 + 4 * LAD))
            lad.append((ev["year"], p2, mae2, why2, u2))
        tr[kind] = {"flat": trade_block(flat, 1), "ladder_1_1_2_3": trade_block(lad, 7)}
    res["trades_us_anchor"] = tr
    res["events_us_anchor"] = [{k: v for k, v in e.items() if k != "T0"} for e in events if e["kind"] == "RETESTED"]
    Path(a.out).write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in res.items() if k != "events_us_anchor"}, indent=1))


def split(y):
    return "DEV" if y <= 2024 else ("VAL" if y == 2025 else "HOLDOUT")


def summarise(rows):
    out = {}
    for kind in ("RETESTED", "SINGLE"):
        rk = [r for r in rows if r["kind"] == kind]
        blk = {}
        for part in ("ALL", "DEV", "VAL", "HOLDOUT"):
            rp = rk if part == "ALL" else [r for r in rk if split(r["year"]) == part]
            nb = sum(r["break"] for r in rp)
            brk = [r for r in rp if r["break"]]
            blk[part] = {"n": len(rp), "break": wilson(nb, len(rp)),
                         "break_deep": wilson(sum(r["break_deep"] for r in rp), len(rp)),
                         "reclaim_after_break": wilson(sum(r["reclaim"] for r in brk), len(brk))}
        byb = {}
        for lo, hi in BUCKETS:
            rb = [r for r in rk if lo <= r["d"] < hi]
            byb[f"{lo*100:.1f}-{hi*100:.1f}%"] = {"n": len(rb), "break": wilson(sum(r["break"] for r in rb), len(rb))}
        blk["by_distance"] = byb
        out[kind] = blk
    return out


def trade_block(rows, maxu):
    """rows: (year, pnl_units, mae, exit[, units]) in time order; mean_pct is per unit of FULL-size notional."""
    blk = {}
    for part in ("ALL", "DEV", "VAL", "HOLDOUT"):
        rp = rows if part == "ALL" else [r for r in rows if split(r[0]) == part]
        s = stats([r[1] / maxu for r in rp])
        if rp:
            s["exits"] = {w: int(sum(r[3] == w for r in rp)) for w in ("target", "stop", "time")}
            for lev in LEVS:
                liq = 1 / lev - MMR
                s[f"liq_{lev}x"] = int(sum(bool(r[2] >= liq) for r in rp))
                # leverage = full-size notional / equity; per-trade equity return = lev * pnl_units / max_units
                eq, peak, mdd = 1.0, 1.0, 0.0
                for r in rp:
                    eq *= max(0.0, 1 + lev * r[1] / maxu)
                    peak = max(peak, eq); mdd = max(mdd, 1 - eq / peak)
                s[f"equity_{lev}x"] = round(eq, 3); s[f"maxdd_{lev}x"] = round(mdd, 3)
        blk[part] = s
    return blk


if __name__ == "__main__":
    main()
