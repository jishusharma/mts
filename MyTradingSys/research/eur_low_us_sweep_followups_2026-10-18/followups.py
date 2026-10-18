"""EU-low / US-sweep follow-up legs (card eu-low-us-sweep-follow-ups-long-after-sw). Rules: PRE_REG.md (frozen before any outcome).
DEV only: bars before 2024-07-01 (the loader refuses later bars). Every number below is OURS unless marked SOURCED.

Leg A  long after sweep + reclaim: EU-session 24 h low L, day-level decision time T0 = US open - 90 min (study.py day_event, imported
       unchanged). First 1m low < L inside [T0, T0+4h) is the sweep; first 1m CLOSE > L within 120 min of it is the reclaim (the sweep
       info is only used up to the reclaim close). LONG at the open of the 2nd bar after the reclaim close (1 delay bar), protective
       stop = lowest low sweep..reclaim minus 0.1 %, time exit after H_A = 120 min.
Leg B  LTF RSI-divergence short from the day high: 5m bars, weekdays, scan 06:00-20:00 UTC. New day-to-date high bar i whose previous
       day high (bar j) is >= 60 min earlier, RSI14(j) >= 60 and RSI14(i) < RSI14(j) - 2 (RSI = FORMULAS.md s.1 Wilder). First signal
       per day. SHORT at the open of the 2nd 1m bar after the 5m close, stop = H(i) + 0.1 %, time exit H_B = 120 min.
Leg C  pre-US double-top short: at T0 the highest high P1 of [T0-6h, T0) is >= 61 min old, the highest high P2 of [P1+60m, T0) is within
       0.15 % under P1 and the lows between fell >= 0.5 % under P1. SHORT at the open of the 2nd bar after the T0-1 close, stop = P1 + 0.1 %,
       time exit H_C = 240 min (the study's outcome window).
Costs: taker 0.05 % per side (card), funding NOT modelled, no slippage. Trades with risk (entry-to-stop) < 0.15 % are skipped.
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "eur_low_us_sweep_2026-10-14"))
sys.path.insert(0, str(HERE.parent / "chart_read_g5_2026-10-16"))
sys.path.insert(0, str(HERE.parents[2] / "scripts" / "dev"))
import study as E  # noqa: E402  (day_event, us_dst, stats: imported, not edited)
import prereg_gate as PG  # noqa: E402

MIN = 60000
FEE_SIDE = 0.0005          # card: 0.05 %/side
COST = 2 * FEE_SIDE        # 0.10 % round trip
STOP_PAD = 0.001           # OURS
MIN_RISK = 0.0015          # OURS
DELAY = 1                  # extra 1m bar between decision close and fill (G5 template)
RECLAIM_MIN = 120          # study.py finding 4
H_A, H_B, H_C = 120, 120, 240
SCAN_FROM, SCAN_TO = 72, 240       # 5m bars: 06:00-20:00 UTC
GAP5 = 12                  # 60 min in 5m bars
RSI_N, RSI_PREV_MIN, RSI_DIFF = 14, 60.0, 2.0
LOOK_C, TOP_GAP, TOP_TOL, TOP_VALLEY = 360, 60, 0.0015, 0.005
SD_R, M_FAMILY = 1.0, 3    # OURS: sd of R used by the gate (precedent runs used 1.5); Holm family = the three legs


def gate(n, sd, cost_r, m):
    """(MDE in R, passes) with the repo rule of scripts/dev/prereg_gate.py: MDE + cost <= 0.30 R."""
    d = PG.mde(n, sd, m)
    return d, d + cost_r <= PG.MAX_PLAUSIBLE_GROSS


def sim(O, H, L, side, ei, stop, h):
    """Enter at O[ei] (side +1 long / -1 short), protective stop, time exit at O[ei+h]. Gross return as a fraction of notional.
    A bar that gaps through the stop fills at its open. None when the entry or exit open is missing or the entry is through the stop."""
    if ei + h >= len(O) or math.isnan(O[ei]) or math.isnan(O[ei + h]):
        return None
    entry = float(O[ei])
    if (side > 0 and entry <= stop) or (side < 0 and entry >= stop):
        return None
    risk = abs(entry - stop) / entry
    for k in range(ei, ei + h):
        if math.isnan(L[k]) or math.isnan(H[k]):
            continue
        if side > 0 and L[k] <= stop:
            px = min(stop, O[k]) if not math.isnan(O[k]) else stop
            return {"gross": px / entry - 1.0, "why": "stop", "risk": risk}
        if side < 0 and H[k] >= stop:
            px = max(stop, O[k]) if not math.isnan(O[k]) else stop
            return {"gross": -(px / entry - 1.0), "why": "stop", "risk": risk}
    return {"gross": side * (float(O[ei + h]) / entry - 1.0), "why": "time", "risk": risk}


def _finish(ev, O, entry_idx, stop, side):
    """Entry/stop geometry shared by the legs; returns ev with a skip reason when the trade cannot be taken."""
    if entry_idx + 1 >= len(O) or math.isnan(O[entry_idx]):
        ev["skip"] = "tape_end"
        return ev
    entry = float(O[entry_idx])
    if (side > 0 and entry <= stop) or (side < 0 and entry >= stop):
        ev["skip"] = "entry_through_stop"
        return ev
    risk = abs(entry - stop) / entry
    if risk < MIN_RISK:
        ev["skip"] = "risk_small"
        return ev
    ev.update(entry_idx=entry_idx, stop=stop, risk=risk, side=side)
    return ev


# ------------------------------------------------------------------ leg A
def leg_a(O, H, L, C, t0, T0):
    ev = E.day_event(t0, H, L, C, T0)
    if not ev or ev["kind"] not in ("RETESTED", "SINGLE") or not ev["break"]:
        return None
    lev = ev["L"]
    b = T0 + ev["break_min"]
    out = {"kind": ev["kind"], "level": lev, "break_idx": b}
    above = np.where(C[b:b + RECLAIM_MIN] > lev)[0]
    if not len(above):
        out["skip"] = "noreclaim"
        return out
    r = b + int(above[0])
    out["reclaim_idx"] = r
    entry_idx = r + 1 + DELAY
    if entry_idx + H_A >= len(O):
        out["skip"] = "tape_end"
        return out
    stop = float(np.nanmin(L[b:r + 1])) * (1 - STOP_PAD)
    return _finish(out, O, entry_idx, stop, +1)


# ------------------------------------------------------------------ leg B
def rsi_div_first_signal(H5, R5, ds, de):
    """First 5m bar i in the day [ds, de) scan window that makes a new day-to-date high with a bearish RSI divergence, else None."""
    for i in range(ds + SCAN_FROM, min(de, ds + SCAN_TO)):
        if math.isnan(H5[i]) or math.isnan(R5[i]):
            continue
        prev = H5[ds:i]
        if np.isnan(prev).all():
            continue
        j = ds + int(np.nanargmax(prev))
        if H5[i] <= H5[j] or i - j < GAP5:
            continue
        if R5[j] >= RSI_PREV_MIN and R5[i] < R5[j] - RSI_DIFF:
            return i
    return None


def leg_b(O, H5, R5, ds, de):
    i = rsi_div_first_signal(H5, R5, ds, de)
    if i is None:
        return None
    t = (i + 1) * 5 - 1                     # last 1m bar of 5m bar i (TS0 is a UTC midnight, 1440 % 5 == 0)
    return _finish({"bar5": i}, O, t + 1 + DELAY, float(H5[i]) * (1 + STOP_PAD), -1)


# ------------------------------------------------------------------ leg C
def leg_c(O, H, L, C, T0):
    if T0 - LOOK_C < 0 or T0 + DELAY + 1 >= len(O):
        return None
    w = H[T0 - LOOK_C:T0]
    if np.isnan(w).sum() > 30 or np.isnan(w).all():
        return None
    p1 = T0 - LOOK_C + int(np.nanargmax(w))
    if T0 - p1 < TOP_GAP + 1:
        return None
    seg = H[p1 + TOP_GAP:T0]
    if np.isnan(seg).all():
        return None
    p2 = p1 + TOP_GAP + int(np.nanargmax(seg))
    if H[p2] < H[p1] * (1 - TOP_TOL):
        return None
    if np.isnan(L[p1 + 1:p2]).all() or np.nanmin(L[p1 + 1:p2]) > H[p1] * (1 - TOP_VALLEY):
        return None
    ev = _finish({"p1": p1, "p2": p2}, O, T0 + DELAY, float(H[p1]) * (1 + STOP_PAD), -1)
    return ev


# ------------------------------------------------------------------ event tables (no outcomes are computed here)
def weekday_T0s(ts0_ms, nbars):
    """(date, day_index, T0 index) of every weekday decision minute A-90 min (study.py anchor), DEV tape only."""
    first = dt.datetime.fromtimestamp(ts0_ms / 1000, dt.timezone.utc).date()
    d = first + dt.timedelta(days=2)
    out = []
    while True:
        a_min = (13 * 60 + 30) if E.us_dst(d) else (14 * 60 + 30)
        T0ms = int(dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() * 1000) + (a_min - 90) * MIN
        T0 = (T0ms - ts0_ms) // MIN
        if T0 + 600 >= nbars:
            break
        if d.weekday() < 5:
            out.append((d, int((dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() * 1000 - ts0_ms) // (MIN * 1440)), int(T0)))
        d += dt.timedelta(days=1)
    return out


def build_events(A, ts0_ms, rsi5):
    """All three legs on the DEV tape: lists of event dicts (some carry a skip reason)."""
    O, H, L, C = A["O"], A["H"], A["L"], A["C"]
    legs = {"A": [], "B": [], "C": []}
    A5 = rsi5["A5"]
    for d, day, T0 in weekday_T0s(ts0_ms, len(C)):
        for key, ev in (("A", leg_a(O, H, L, C, ts0_ms, T0)), ("C", leg_c(O, H, L, C, T0)),
                        ("B", leg_b(O, A5["H"], rsi5["R5"], day * 288, day * 288 + 288))):
            if ev is not None:
                ev.update(date=str(d), year=d.year, day=day)
                legs[key].append(ev)
    return legs


def tradeable(evs):
    return [e for e in evs if "skip" not in e]


def count_text(legs):
    lines = ["# COUNT: events per leg on the DEV tape (bars before 2024-07-01), no outcome computed", "",
             f"Gate rule: scripts/dev/prereg_gate.py, sd {SD_R} R (OURS; precedent runs used 1.5), m {M_FAMILY} (the three legs), cost = "
             f"{100 * COST:.2f}% round trip / median stop distance. MDE + cost must be <= 0.30 R.", "",
             "| leg | candidates | skipped (reason: n) | n tradeable (= days) | median risk % | cost R | MDE R | MDE+cost R | n needed | gate |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    verdict = {}
    for key, name in (("A", "A long after sweep+reclaim"), ("B", "B RSI-divergence short"), ("C", "C pre-US double-top short")):
        evs = legs[key]
        ok_ = tradeable(evs)
        skips = {}
        for e in evs:
            if "skip" in e:
                skips[e["skip"]] = skips.get(e["skip"], 0) + 1
        n = len(ok_)
        risk = np.array([e["risk"] for e in ok_]) if n else np.array([np.nan])
        med = float(np.nanmedian(risk))
        cost_r = COST / med if n else float("inf")
        if n:
            mde, ok = gate(n, SD_R, cost_r, M_FAMILY)
            need = ((PG.z_holm(M_FAMILY) + PG.POWER_Z) * SD_R / (PG.MAX_PLAUSIBLE_GROSS - cost_r)) ** 2 if cost_r < PG.MAX_PLAUSIBLE_GROSS else float("inf")
        else:
            mde, ok, need = float("nan"), False, float("inf")
        verdict[key] = {"n": n, "median_risk_pct": round(100 * med, 3), "cost_R": round(cost_r, 3), "MDE_R": round(mde, 3),
                        "need": None if math.isinf(need) else int(need), "gate": "PASS" if ok else "BLOCK", "skips": skips}
        lines.append(f"| {name} | {len(evs)} | {skips or '-'} | {n} | {100 * med:.3f} | {cost_r:.3f} | {mde:.3f} | {mde + cost_r:.3f} | "
                     f"{'inf' if math.isinf(need) else int(need)} | {'PASS' if ok else 'BLOCK'} |")
    return "\n".join(lines) + "\n", verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", action="store_true", help="print the count + gate table; computes no outcome")
    a = ap.parse_args()
    import common as K  # noqa: E402  (loads the DEV tape; refuses bars >= 2024-07-01)
    A = K.load()
    A5 = K.agg(A, 5)
    rsi5 = {"A5": A5, "R5": K.rsi_wilder(A5["C"], RSI_N)}
    legs = build_events(A, K.TS0, rsi5)
    text, verdict = count_text(legs)
    if a.count:
        print(text)
        (HERE / "COUNT.md").write_text(text, encoding="utf-8", newline="\n")
        return
    raise SystemExit("outcome run not enabled: gate must PASS for a leg first (see COUNT.md)")


if __name__ == "__main__":
    main()
