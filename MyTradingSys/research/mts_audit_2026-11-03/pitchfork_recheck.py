"""Independent recheck of the Pitchfork 4H "PASS" (PHASE2_4H_POC_STUDY.md), audit 2026-11-03.

Reads only 2020-01..2024-06 (DEV_EXT and DEV). VALIDATION and HOLDOUT are cut at load.
Three arms per variant x filter, same fork geometry, same profile, same stop and target as the study:
  STUDY   final pivot list, fill allowed on the confirm bar, no stop check on the fill bar, ML before stop.
  CAUSAL  pivots as known at each bar (a swing later extended stays in the record), fills as STUDY.
  EXACT   causal pivots, order rests from the bar after confirmation, 1m walk, stop first inside one minute.
PLACEBO EXACT with the same side, stop and target distance, entered at a random 4H bar open in the same year.
Costs come from backtest/fees.py. Maker entry + taker exit + 2 bp is the study's own figure; the taker pair + slip is the stress line.
"""
import argparse
import csv
import glob
import json
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from MyTradingSys.backtest.fees import BINANCE_MAKER, BINANCE_TAKER
from MyTradingSys.backtest.layers.pitchfork.pitchfork_detector import (
    PitchforkChannel,
    PitchforkPivot,
    PitchforkVariant,
    find_pivots_zigzag,
)
from MyTradingSys.backtest.vp_pivot_probe import build_profile

HERE = Path(__file__).resolve().parent
CSV_4H = REPO_ROOT / "MyTradingSys" / "research" / "pitchfork_2026-10-19" / "btc_4h_2020_2026.csv"
KLINE_GLOBS = ["F:/MTS/data/dev_ext_2019_2021/klines/BTCUSDT-1m-*.csv", "F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv"]
START_MS = int(datetime(2020, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
CUT_MS = int(datetime(2024, 7, 1, tzinfo=timezone.utc).timestamp() * 1000)
DEV_START_MS = int(datetime(2022, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
LOOKBACK = 4  # study value, OURS
MIN_CHANGE = 0.03  # study value, OURS
HORIZON_BARS = 60  # study value, OURS
STOP_PCT = 0.015  # study value, OURS
BAR_MS = 14_400_000
SLIP = 0.0002  # study's 2 bp, OURS
COST_STUDY = BINANCE_MAKER + BINANCE_TAKER + SLIP
COST_STRESS = 2 * BINANCE_TAKER + 2 * SLIP


@dataclass
class Setup:
    p0: PitchforkPivot
    p1: PitchforkPivot
    p2: PitchforkPivot
    known_at: int  # bar index whose close first shows this triplet


def load_4h():
    bars = []
    with open(CSV_4H, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ts = int(row["timestamp"])
            if START_MS <= ts and ts + BAR_MS <= CUT_MS:
                bars.append((ts, float(row["open"]), float(row["high"]), float(row["low"]), float(row["close"]), float(row["volume"])))
    return bars


def load_1m():
    rows = []
    for pattern in KLINE_GLOBS:
        for path in sorted(glob.glob(pattern)):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    p = line.split(",")
                    if len(p) < 5 or not p[0].isdigit():
                        continue
                    ts = int(p[0])
                    if START_MS <= ts < CUT_MS:
                        rows.append((ts, float(p[2]), float(p[3]), float(p[4])))
    rows = sorted(set(rows))
    a = np.array(rows, dtype=float)
    return a[:, 0].astype(np.int64), a[:, 1], a[:, 2], a[:, 3]


def causal_setups(highs, lows, lookback=LOOKBACK, min_change=MIN_CHANGE):
    """The zigzag of find_pivots_zigzag replayed bar by bar: every triplet as it was known, including ones later extended."""
    pivots = []
    last = None
    out = []
    for c in range(lookback * 2, len(highs)):
        i = c - lookback
        hi = all(highs[i] >= highs[j] for j in range(i - lookback, c + 1) if j != i)
        lo = all(lows[i] <= lows[j] for j in range(i - lookback, c + 1) if j != i)
        changed = False
        if last is None:
            if hi:
                pivots.append(PitchforkPivot(index=i, price=highs[i], is_high=True))
                last, changed = True, True
            elif lo:
                pivots.append(PitchforkPivot(index=i, price=lows[i], is_high=False))
                last, changed = False, True
        elif last is True:
            if hi and highs[i] > pivots[-1].price:
                pivots[-1] = PitchforkPivot(index=i, price=highs[i], is_high=True)
                changed = True
            elif lo and (pivots[-1].price - lows[i]) / max(1e-9, pivots[-1].price) >= min_change:
                pivots.append(PitchforkPivot(index=i, price=lows[i], is_high=False))
                last, changed = False, True
        else:
            if lo and lows[i] < pivots[-1].price:
                pivots[-1] = PitchforkPivot(index=i, price=lows[i], is_high=False)
                changed = True
            elif hi and (highs[i] - pivots[-1].price) / max(1e-9, pivots[-1].price) >= min_change:
                pivots.append(PitchforkPivot(index=i, price=highs[i], is_high=True))
                last, changed = True, True
        if changed and len(pivots) >= 3:
            out.append(Setup(pivots[-3], pivots[-2], pivots[-1], c))
    return out


def final_setups(highs, lows):
    pv = find_pivots_zigzag(highs, lows, lookback=LOOKBACK, min_change_pct=MIN_CHANGE)
    return [Setup(a, b, c, c.index + LOOKBACK) for a, b, c in zip(pv, pv[1:], pv[2:])]


def passes_filter(setup, bars, flt):
    if flt == "UNFILTERED":
        return True
    a, b = min(setup.p0.index, setup.p2.index), max(setup.p0.index, setup.p2.index) + 1
    sub = bars[a:b]
    if len(sub) < 2:
        return False
    vp = build_profile([x[3] for x in sub], [x[2] for x in sub], [x[5] for x in sub], w=10.0)
    if not vp:
        return False
    return vp["val"] <= setup.p2.price <= vp["vah"]


def study_trade(setup, pf, bars):
    """The study's own TINE_LIMIT_RETEST bar loop. Returns (entry bar ts, gross return) or None."""
    long_side = not setup.p2.is_high
    entry = None
    window = bars[setup.known_at : setup.known_at + HORIZON_BARS]
    for k, b in enumerate(window):
        t = setup.known_at + k
        if entry is None:
            tine = pf.get_lml(t) if long_side else pf.get_uml(t)
            if b[3] <= tine <= b[2]:
                entry, entry_ts = tine, b[0]
            continue
        res = pf.eval_bar(t, high=b[2], low=b[3], close=b[4])
        if res.reached_ml:
            r = (res.ml_value - entry) / entry
            return entry_ts, (r if long_side else -r)
        if long_side and b[3] <= entry * (1 - STOP_PCT):
            return entry_ts, -STOP_PCT
        if not long_side and b[2] >= entry * (1 + STOP_PCT):
            return entry_ts, -STOP_PCT
    if entry is None or not window:
        return None
    r = (window[-1][4] - entry) / entry
    return entry_ts, (r if long_side else -r)


def walk_1m(m_ts, m_hi, m_lo, m_cl, i0, long_side, entry, stop_dist, target_fn, end_ts):
    """Stop first inside one minute. target_fn(ts) gives the target price at that minute."""
    stop = entry * (1 - stop_dist) if long_side else entry * (1 + stop_dist)
    i = i0
    n = len(m_ts)
    while i < n and m_ts[i] < end_ts:
        if (long_side and m_lo[i] <= stop) or (not long_side and m_hi[i] >= stop):
            return -stop_dist
        tgt = target_fn(m_ts[i])
        if long_side and m_hi[i] >= tgt:
            return (tgt - entry) / entry
        if not long_side and m_lo[i] <= tgt:
            return (entry - tgt) / entry
        i += 1
    last = m_cl[min(i, n) - 1]
    r = (last - entry) / entry
    return r if long_side else -r


def exact_trade(setup, pf, bars, m):
    """Order rests from the bar after confirmation. Fill on the first 1m bar that touches the tine of its 4H bar."""
    m_ts, m_hi, m_lo, m_cl = m
    long_side = not setup.p2.is_high
    first = setup.known_at + 1
    if first >= len(bars):
        return None
    end_ts = bars[min(setup.known_at + HORIZON_BARS, len(bars) - 1)][0] + BAR_MS
    base_ts = bars[0][0]

    def bar_of(ts):
        return int((ts - base_ts) // BAR_MS)

    index_of = {b[0]: i for i, b in enumerate(bars)}

    def line(fn, ts):
        k = index_of.get(ts - ts % BAR_MS)
        return fn(k if k is not None else bar_of(ts))

    i = int(np.searchsorted(m_ts, bars[first][0]))
    n = len(m_ts)
    while i < n and m_ts[i] < end_ts:
        tine = line(pf.get_lml, int(m_ts[i])) if long_side else line(pf.get_uml, int(m_ts[i]))
        if m_lo[i] <= tine <= m_hi[i]:
            target_fn = lambda ts: line(pf.get_ml, int(ts))
            gross = walk_1m(m_ts, m_hi, m_lo, m_cl, i, long_side, tine, STOP_PCT, target_fn, end_ts)
            target_gap = abs(line(pf.get_ml, int(m_ts[i])) - tine) / tine
            return int(m_ts[i]), gross, long_side, target_gap
        i += 1
    return None


def stats(trades, cost, seed=7, draws=2000):
    """trades = [(entry ts, gross)]. Mean net % with a calendar-month block bootstrap interval."""
    if not trades:
        return {"n": 0}
    net = np.array([g - cost for _, g in trades]) * 100
    months = {}
    for (ts, g) in trades:
        key = datetime.fromtimestamp(ts / 1000, timezone.utc).strftime("%Y-%m")
        months.setdefault(key, []).append((g - cost) * 100)
    keys = list(months)
    rnd = random.Random(seed)
    boot = []
    for _ in range(draws):
        s = []
        for _k in keys:
            s.extend(months[rnd.choice(keys)])
        boot.append(sum(s) / len(s))
    boot.sort()
    pos = net[net > 0].sum()
    neg = -net[net <= 0].sum()
    return {
        "n": len(trades),
        "mean_net_pct": round(float(net.mean()), 3),
        "ci95": [round(boot[int(draws * 0.025)], 3), round(boot[int(draws * 0.975)], 3)],
        "win_pct": round(float((net > 0).mean() * 100), 1),
        "pf": round(float(pos / neg), 2) if neg else None,
    }


def split(trades):
    return {
        "DEV_EXT 2020-2021": [t for t in trades if t[0] < DEV_START_MS],
        "DEV 2022..2024-06": [t for t in trades if t[0] >= DEV_START_MS],
        "both": trades,
    }


def placebo_mean(exact, bars, m, cost, runs, seed=11):
    """Same year, side, stop and target distance as each real trade, entered at a random 4H bar open."""
    m_ts, m_hi, m_lo, m_cl = m
    rnd = random.Random(seed)
    by_year = {}
    for b in bars[:-HORIZON_BARS]:
        by_year.setdefault(datetime.fromtimestamp(b[0] / 1000, timezone.utc).year, []).append(b[0])
    out = []
    for _ in range(runs):
        vals = []
        for ts, _g, long_side, gap in exact:
            year = datetime.fromtimestamp(ts / 1000, timezone.utc).year
            start = rnd.choice(by_year[year])
            i = int(np.searchsorted(m_ts, start))
            if i >= len(m_ts):
                continue
            entry = float(m_cl[i])
            tgt = entry * (1 + gap) if long_side else entry * (1 - gap)
            vals.append(walk_1m(m_ts, m_hi, m_lo, m_cl, i, long_side, entry, STOP_PCT, lambda _t: tgt, start + HORIZON_BARS * BAR_MS) - cost)
        out.append(float(np.mean(vals)) * 100)
    out.sort()
    return {"mean": round(float(np.mean(out)), 3), "p95": round(out[int(len(out) * 0.95)], 3), "runs": runs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--placebo-runs", type=int, default=200)
    args = ap.parse_args()
    bars = load_4h()
    assert bars[-1][0] + BAR_MS <= CUT_MS
    highs = [b[2] for b in bars]
    lows = [b[3] for b in bars]
    m = load_1m()
    print("4H bars", len(bars), "1m bars", len(m[0]), flush=True)
    final = final_setups(highs, lows)
    causal = causal_setups(highs, lows)
    print("setups final", len(final), "causal", len(causal), flush=True)
    variants = [("Standard_Andrews", PitchforkVariant.STANDARD), ("Modified_Schiff", PitchforkVariant.MODIFIED_SCHIFF)]
    out = {"cost_study": COST_STUDY, "cost_stress": COST_STRESS, "setups_final": len(final), "setups_causal": len(causal), "cells": []}
    for vname, var in variants:
        for flt in ("UNFILTERED", "VA_CONFLUENT"):
            cell = {"variant": vname, "filter": flt, "arms": {}}
            arms = {"STUDY": [], "CAUSAL": []}
            exact = []
            for tag, setups in (("STUDY", final), ("CAUSAL", causal)):
                for s in setups:
                    if s.known_at >= len(bars) or not passes_filter(s, bars, flt):
                        continue
                    r = study_trade(s, PitchforkChannel(s.p0, s.p1, s.p2, variant=var), bars)
                    if r:
                        arms[tag].append(r)
            for s in causal:
                if s.known_at >= len(bars) or not passes_filter(s, bars, flt):
                    continue
                r = exact_trade(s, PitchforkChannel(s.p0, s.p1, s.p2, variant=var), bars, m)
                if r:
                    exact.append(r)
            arms["EXACT"] = [(t, g) for t, g, _s, _g in exact]
            for tag, tr in arms.items():
                cell["arms"][tag] = {k: stats(v, COST_STUDY) for k, v in split(tr).items()}
            cell["arms"]["EXACT_stress_both"] = stats(arms["EXACT"], COST_STRESS)
            cell["placebo_both"] = placebo_mean(exact, bars, m, COST_STUDY, args.placebo_runs)
            out["cells"].append(cell)
            print(json.dumps(cell), flush=True)
    (HERE / "pitchfork_recheck.json").write_text(json.dumps(out, indent=1), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
