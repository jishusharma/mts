"""
MyTradingSys/backtest/layers/run_bracket_grid.py

Q1 per-layer bracket grid driver (DSA_BACKLOG B item; MISSING_PIECES_2026-09-30 section 4 H1).
For each layer's historical events, grid stop {0.3,0.5,0.75,1,1.5,2}% x target {1,2,3}R x time exit
{4,8,16} bars (54 trials per layer, reported), 70/30 chronological IS/OOS, PBO (CSCV, existing
bt.ref_pbo via run_t055.compute_pbo on daily-bucketed IS net R). Output per layer: the best frozen
bracket (chosen on IS only, applied unchanged to OOS) or "fixed 1%/2% default stands".

Trade model (bar by bar, same conventions as sim.py): entry = close of the event bar (taker);
bars i+1..i+T scanned with OHLC; stop checked BEFORE target inside one bar (worst case); stop fills
at the stop price (no gap slippage); time exit at close of bar i+T. Fees are sim.py's (operator
decision 2026-09-30, bug B080): taker 5 bps, maker 0; fee_pct = taker + (maker if target else taker),
fee_R = fee_pct / stop_frac (sim.py: fee_pct * entry / risk). Net R = gross R - fee_R.
Events with fewer than T bars after them are skipped. IS trades must exit before the IS/OOS
boundary (purge); OOS events are those at or after it. Alert-only research code; never touches
execution or Tom core.

Desktop: python MyTradingSys/backtest/layers/run_bracket_grid.py --layer all
"""

import argparse
import json
import math
import os
import sys
from pathlib import Path

REPO = Path(os.environ.get("MTS_REPO") or Path(__file__).resolve().parents[3])
sys.path.insert(0, str(REPO))

from MyTradingSys.backtest.layers import run_t055 as T055  # noqa: E402

TAKER = 0.0005   # sim.py canonical (argparse default)
MAKER = 0.0
STOPS = (0.003, 0.005, 0.0075, 0.01, 0.015, 0.02)
TARGETS_R = (1, 2, 3)
TIMES = (4, 8, 16)
DEFAULT_STOP, DEFAULT_TARGET_R = 0.01, 2
MIN_IS, MIN_OOS, MAX_PBO = 20, 30, 0.5
MD_DIR = T055.MD_DIR
DEFAULT_TEXT = "fixed 1%/2% default stands"


def bracket_grid():
    return [(s, k, t) for s in STOPS for k in TARGETS_R for t in TIMES]


# ---------------------------------------------------------------- simulation

def simulate_trade(bars, i, side, stop_frac, target_r, time_bars, taker=TAKER, maker=MAKER):
    """Returns {"kind","exit_i","gross_R","fee_R","net_R"} or None if bar i+time_bars does not exist."""
    j_max = i + time_bars
    if j_max >= len(bars):
        return None
    e = bars[i]["c"]
    sgn = 1.0 if side == "long" else -1.0
    stop = e * (1 - sgn * stop_frac)
    target = e * (1 + sgn * stop_frac * target_r)
    risk = stop_frac * e
    kind, exit_i, gross = None, j_max, None
    for j in range(i + 1, j_max + 1):
        b = bars[j]
        if (side == "long" and b["l"] <= stop) or (side == "short" and b["h"] >= stop):
            kind, exit_i, gross = "stop", j, -1.0
            break
        if (side == "long" and b["h"] >= target) or (side == "short" and b["l"] <= target):
            kind, exit_i, gross = "target", j, float(target_r)
            break
    if kind is None:
        kind, gross = "time", sgn * (bars[j_max]["c"] - e) / risk
    fee_pct = taker + (maker if kind == "target" else taker)
    fee_R = fee_pct / stop_frac
    return {"kind": kind, "exit_i": exit_i, "gross_R": gross, "fee_R": fee_R, "net_R": gross - fee_R}


def cell_stats(trades, stop_frac, taker=TAKER):
    n = len(trades)
    base = {"n": n, "fee_per_stop_R": 2 * taker / stop_frac}
    if n == 0:
        base.update({"stop_rate": None, "target_rate": None, "time_rate": None, "mean_net_R": None,
                     "ci95": None, "mean_net_usd_per_100": None})
        return base
    nets = [t["net_R"] for t in trades]
    mean = sum(nets) / n
    ci = None
    if n >= 2:
        var = sum((x - mean) ** 2 for x in nets) / (n - 1)
        h = 1.96 * math.sqrt(var / n)
        ci = (mean - h, mean + h)
    base.update({"stop_rate": sum(1 for t in trades if t["kind"] == "stop") / n,
                 "target_rate": sum(1 for t in trades if t["kind"] == "target") / n,
                 "time_rate": sum(1 for t in trades if t["kind"] == "time") / n,
                 "mean_net_R": mean, "ci95": ci,
                 "mean_net_usd_per_100": mean * stop_frac * 100})
    return base


def decide(is_mean, oos_mean, oos_n, pbo, min_oos=MIN_OOS, max_pbo=MAX_PBO):
    crit = {"is_mean_net_R>0": is_mean is not None and is_mean > 0,
            "oos_mean_net_R>0": oos_mean is not None and oos_mean > 0,
            f"oos_n>={min_oos}": oos_n >= min_oos,
            "pbo<0.5": pbo is not None and pbo < max_pbo}
    return all(crit.values()), crit


# ---------------------------------------------------------------- per-layer run

def run_layer(name, bars, events, is_frac=0.70, min_is=MIN_IS, min_oos=MIN_OOS, pbo_s=16):
    n_is = int(len(bars) * is_frac)
    bars_is = bars[:n_is]
    grid = bracket_grid()
    cells, columns, per_cell = [], [], {}
    for (s, k, t) in grid:
        is_tr, oos_tr = [], []
        for e in events:
            r = simulate_trade(bars, e["i"], e["side"], s, k, t)
            if r is None:
                continue
            r["t"], r["net"] = bars[e["i"]]["t"], r["net_R"]
            if e["i"] < n_is:
                if r["exit_i"] < n_is:
                    is_tr.append(r)
            else:
                oos_tr.append(r)
        per_cell[(s, k, t)] = (is_tr, oos_tr)
        c = {"stop_pct": round(s * 100, 4), "target_r": k, "time_bars": t}
        c.update(cell_stats(is_tr + oos_tr, s))
        c["n_is"], c["n_oos"] = len(is_tr), len(oos_tr)
        cells.append(c)
        columns.append(T055.daily_matrix_column(is_tr, bars_is))

    pbo = T055.compute_pbo(columns, pbo_s) if events else None
    res = {"layer": name, "n_bars": len(bars), "n_is_bars": n_is, "n_events": len(events),
           "n_trials": len(grid), "fee_taker": TAKER, "fee_maker": MAKER, "pbo": pbo, "cells": cells,
           "default_cells": [c for c in cells if c["stop_pct"] == DEFAULT_STOP * 100
                             and c["target_r"] == DEFAULT_TARGET_R],
           "chosen": None, "is": None, "oos": None, "criteria": {}, "verdict": "DEFAULT"}

    best, best_mean = None, None
    for key in grid:   # first in grid order wins ties
        is_tr = per_cell[key][0]
        if len(is_tr) < min_is:
            continue
        m = sum(x["net_R"] for x in is_tr) / len(is_tr)
        if best_mean is None or m > best_mean:
            best, best_mean = key, m
    if best is None:
        res["reason"] = f"no IS cell with >= {min_is} trades"
        return res
    s, k, t = best
    is_st = cell_stats(per_cell[best][0], s)
    oos_st = cell_stats(per_cell[best][1], s)
    ok, crit = decide(is_st["mean_net_R"], oos_st["mean_net_R"], oos_st["n"], pbo, min_oos)
    res.update({"chosen": {"stop_pct": round(s * 100, 4), "target_r": k, "time_bars": t},
                "is": is_st, "oos": oos_st, "criteria": crit, "verdict": "FROZEN" if ok else "DEFAULT"})
    return res


# ---------------------------------------------------------------- report

def _r(x, nd=3):
    return "n/a" if x is None else f"{x:.{nd}f}"


def _p(x):
    return "n/a" if x is None else f"{100 * x:.1f}%"


def _cell_row(c):
    ci = c["ci95"]
    return (f"| {c['stop_pct']}% | {c['target_r']}R | {c['time_bars']} | {c['n']} ({c['n_is']}/{c['n_oos']}) | "
            f"{_p(c['stop_rate'])} | {_p(c['target_rate'])} | {_p(c['time_rate'])} | {_r(c['mean_net_R'])} | "
            f"{'n/a' if ci is None else '[%s, %s]' % (_r(ci[0]), _r(ci[1]))} | {_r(c['mean_net_usd_per_100'], 4)} | "
            f"{_r(c['fee_per_stop_R'])} |")


HEAD = ["| stop | target | time bars | fills (IS/OOS) | stop-out | target-hit | time-exit | mean net R | 95% CI | "
        "net USD/100 notional | fee per stop-out (R) |", "|---|---|---|---|---|---|---|---|---|---|---|"]


def render_markdown(results):
    L = ["# Q1 per-layer bracket grid", "",
         f"Fees (sim.py canonical, B080): taker {TAKER * 1e4:.0f} bps, maker {MAKER * 1e4:.0f} bps. "
         "Entry close of event bar; stop before target in one bar; 70/30 chronological IS/OOS with purge; "
         "bracket chosen on IS only. PBO = CSCV on daily IS net R across the whole grid.", ""]
    for r in results:
        L += [f"## {r['layer']}", "",
              f"trials: {r['n_trials']} | events {r['n_events']} | bars {r['n_bars']} (IS {r['n_is_bars']}) | "
              f"PBO {_r(r['pbo'])}", ""]
        if r["chosen"]:
            c = r["chosen"]
            L += [f"Best IS cell: stop {c['stop_pct']}%, target {c['target_r']}R, time exit {c['time_bars']} bars. "
                  f"IS n={r['is']['n']} mean net R {_r(r['is']['mean_net_R'])}; "
                  f"OOS n={r['oos']['n']} mean net R {_r(r['oos']['mean_net_R'])}.", "",
                  "| criterion | result |", "|---|---|"]
            L += [f"| {k} | {'PASS' if v else 'FAIL'} |" for k, v in r["criteria"].items()]
            L.append("")
        elif r.get("reason"):
            L += [f"No IS cell qualified: {r['reason']}.", ""]
        if r["verdict"] == "FROZEN":
            c = r["chosen"]
            L += [f"**Verdict: frozen bracket stop {c['stop_pct']}% / target {c['target_r']}R / "
                  f"time {c['time_bars']} bars.**", ""]
        else:
            L += [f"**Verdict: {DEFAULT_TEXT}.**", ""]
        L += ["Default cells (stop 1%, 2R):", ""] + HEAD + [_cell_row(c) for c in r["default_cells"]] + [""]
        L += ["All cells:", ""] + HEAD + [_cell_row(c) for c in r["cells"]] + [""]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- layers + CLI

def _c(key):
    return lambda bars, funding: T055.CANDIDATES[key]["events_fn"](bars, funding)


def _absorption(bars, funding):
    from MyTradingSys.backtest.layers.fabio.fabio_cvd_absorption import cvd_absorption_events
    return cvd_absorption_events(bars)


def _escalation(bars, funding):
    from MyTradingSys.backtest.layers.fabio.fabio_escalation import escalation_events
    return escalation_events(bars)


# data: run_t055 candidate whose loader/roots to use; tf: bar timeframe; default layer parameters
LAYERS = {
    "c1": {"data": "c1", "tf": "15m", "events": _c("c1")},
    "c2": {"data": "c2", "tf": "5m", "events": _c("c2")},
    "c3": {"data": "c3", "tf": "1m", "events": _c("c3")},
    "fabio_absorption": {"data": "c2", "tf": "5m", "events": _absorption},
    "fabio_escalation": {"data": "c2", "tf": "5m", "events": _escalation},
}


def resolve_layers(names):
    return sorted(LAYERS) if "all" in names else list(names)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--layer", action="append", required=True, choices=sorted(LAYERS) + ["all"])
    ap.add_argument("--out", default=None)
    ap.add_argument("--md-dir", default=str(MD_DIR))
    ap.add_argument("--data-root", default=str(REPO / "Dumps" / "backtest" / "raw_1m_2022"))
    ap.add_argument("--data-root2", default=str(REPO / "Dumps" / "backtest" / "raw"))
    ap.add_argument("--min-is", type=int, default=MIN_IS)
    ap.add_argument("--min-oos", type=int, default=MIN_OOS)
    ap.add_argument("--pbo-s", type=int, default=16)
    return ap.parse_args(argv)


def main(argv=None):
    a = parse_args(argv)
    out_dir = Path(a.out or REPO / "Dumps" / "backtest" / "runs" / "q1_bracket_grid")
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for name in resolve_layers(a.layer):
        spec = LAYERS[name]
        bars, funding = T055.load_data(spec["data"], a.data_root, a.data_root2, spec["tf"])
        print(f"{name}: {len(bars)} {spec['tf']} bars", file=sys.stderr)
        events = spec["events"](bars, funding)
        r = run_layer(name, bars, events, min_is=a.min_is, min_oos=a.min_oos, pbo_s=a.pbo_s)
        r["tf"] = spec["tf"]
        results.append(r)
        print(f"{name}: {r['n_events']} events, PBO {_r(r['pbo'])}, {r['verdict']}", file=sys.stderr)
    with open(out_dir / "result.json", "w", newline="\n", encoding="utf-8") as f:
        json.dump(results, f, indent=1, default=str)
    md = Path(a.md_dir) / "Q1_BRACKET_GRID.md"
    md.parent.mkdir(parents=True, exist_ok=True)
    with open(md, "w", newline="\n", encoding="utf-8") as f:
        f.write(render_markdown(results))
    return results


if __name__ == "__main__":
    main()
