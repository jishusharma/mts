"""malkan_window_wide_2026-11: Malkan regular-divergence window bands with WIDE pivots (strength 3), 10 symbols, DEV only. See PRE_REG.md.

Pivot strength L: close[i] is a low/high if strictly below/above the L closes on each side; known at bar i+L, so the event bar is b+L (causal).
Bands (swing-to-swing bars inclusive of both swings): S3_10 SOURCED, B11_12 / C13_18 / D19_50 OURS.
Passes: --pass count (events and days, no returns + gate lines), --pass dev (fee-net stats only for (tf, band) that PASS the power gate).
Bars from 2024-07-01 are never opened.
"""
import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts" / "dev"))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


base = _load("malkan_window_study_ro", REPO / "MyTradingSys/research/malkan_window_dev_2026-11/study.py")   # read only reuse
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_core import rsi_core  # noqa: E402
import prereg_gate  # noqa: E402
import verdicts  # noqa: E402

DEV_END_MS = base.DEV_END_MS
DAY, H, COST, ARMS, KINDS, TF_MS = base.DAY, base.H, base.COST, base.ARMS, base.KINDS, base.TF_MS
arm_of, resample, load_1m, cell_stats = base.arm_of, base.resample, base.load_1m, base.cell_stats
STRENGTH = 3                       # OURS: lookaround bars each side
MIN_BARS_1H = 7200                 # OURS (card): fewer 1h bars = no-signal symbol
MAX_PLAUSIBLE = prereg_gate.MAX_PLAUSIBLE_GROSS
ROOT = "F:/MTS/data/tom_raw"
SYMS = {"BTCUSDT": "klines", "ETHUSDT": "klines_eth", "SOLUSDT": "klines_sol", "BNBUSDT": "klines_bnb", "XRPUSDT": "klines_xrp",
        "DOGEUSDT": "klines_doge", "ADAUSDT": "klines_ada", "AVAXUSDT": "klines_avax", "LINKUSDT": "klines_link", "LTCUSDT": "klines_ltc"}


def coverage_ok(n_1h_bars):
    return n_1h_bars >= MIN_BARS_1H


def _pivots(vals, rsi, kind, L):
    sgn = 1 if kind == "low" else -1
    out = []
    for i in range(L, len(vals) - L):
        if rsi[i] is None:
            continue
        v = sgn * vals[i]
        if all(v < sgn * vals[i - j] and v < sgn * vals[i + j] for j in range(1, L + 1)):
            out.append(i)
    return out


def divergences(close, rsi, ts, kind, L=STRENGTH):
    """Regular divergence between consecutive strength-L swings, 3..50 bars apart, tagged with its band; event at b+L."""
    sign = 1 if kind == "bullish" else -1
    piv = _pivots(close, rsi, "low" if kind == "bullish" else "high", L)
    out = []
    for k in range(1, len(piv)):
        a, b = piv[k - 1], piv[k]
        bars = b - a + 1
        if sign * close[b] < sign * close[a] and sign * rsi[b] - sign * rsi[a] > 0 and 3 <= bars <= 50:
            out.append({"i": b + L, "t": ts[b + L], "a_i": a, "b_i": b, "bars": bars, "arm": arm_of(bars)})
    return out


def collect():
    """(tf, kind, arm) -> (gross, cluster keys); also per-tf pooled 10-bar return sd and per-symbol status."""
    cells, rets, status = {}, {tf: [] for tf in TF_MS}, {}
    for si, (sym, folder) in enumerate(SYMS.items()):
        m1 = load_1m("%s/%s" % (ROOT, folder), sym)
        assert not m1 or m1[-1]["t"] < DEV_END_MS
        bars1h = resample(m1, "1h")
        status[sym] = {"bars_1h": len(bars1h), "ok": coverage_ok(len(bars1h))}
        if not status[sym]["ok"]:
            continue
        for tf in TF_MS:
            bars = resample(m1, tf)
            closes = [b["c"] for b in bars]
            ts = [b["t"] for b in bars]
            rsi = rsi_core(closes, base.RSI_PERIOD)
            rets[tf].extend((closes[i + H] / closes[i] - 1) * 100 for i in range(len(closes) - H))
            for kind in KINDS:
                evs = [e for e in divergences(closes, rsi, ts, kind) if e["arm"]]
                for arm in ARMS:
                    trs = base.trades_for([e for e in evs if e["arm"] == arm], bars, kind)
                    g, k = cells.setdefault((tf, kind, arm), ([], []))
                    g.extend(x["gross"] for x in trs)
                    k.extend(si * 1000000 + x["day"] for x in trs)
        print(sym, "done", status[sym], file=sys.stderr, flush=True)
    sd = {tf: float(np.std(v)) for tf, v in rets.items()}
    return cells, sd, status


def gate(days, sd, m):
    mde = prereg_gate.mde(days, sd, m)
    ok = mde + COST <= MAX_PLAUSIBLE
    return {"mde_plus_cost": mde + COST, "pass": ok}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", default="count", choices=("count", "dev"))
    a = ap.parse_args()
    cells, sd, status = collect()
    total, _, _ = verdicts.count_with_ledger(str(verdicts.CSV_PATH), str(verdicts.RESEARCH / "TRIAL_LEDGER.csv"), "DEV")
    m = total + len(ARMS) * len(TF_MS) * len(KINDS)
    gates = {}
    for tf in TF_MS:
        for arm in ARMS:
            days = len({k for kind in KINDS for k in cells.get((tf, kind, arm), ([], []))[1]})
            n = sum(len(cells.get((tf, kind, arm), ([], []))[0]) for kind in KINDS)
            gates[(tf, arm)] = {"n": n, "days": days, "sd": sd[tf], "m": m, **(gate(days, sd[tf], m) if days else {"mde_plus_cost": float("nan"), "pass": False})}
    rows = []
    for (tf, arm), g in sorted(gates.items()):
        rows.append({"tf": tf, "arm": arm, "n": g["n"], "days": g["days"], "sd": round(g["sd"], 3), "m": m,
                     "mde_plus_cost": round(g["mde_plus_cost"], 3) if g["days"] else "", "gate": "PASS" if g["pass"] else "BLOCK"})
    _w(HERE / "gate_lines.csv", rows)
    _w(HERE / "counts.csv", [{"tf": tf, "kind": kind, "arm": arm, "n": len(g), "days": len(set(k))} for (tf, kind, arm), (g, k) in sorted(cells.items())])
    (HERE / "symbols.json").write_text(json.dumps(status, indent=1), encoding="utf-8", newline="\n")
    if a.pass_ == "dev":
        out = []
        for (tf, kind, arm), (g, k) in sorted(cells.items()):
            if gates[(tf, arm)]["pass"] and g:
                r = {"tf": tf, "kind": kind, "arm": arm}
                r.update(cell_stats(g, k))
                out.append(r)
        _w(HERE / "dev_cells.csv", out)
        print("outcome cells run:", len(out))
    for r in rows:
        print(r)
    print("m =", m)
    return 0


def _w(path, rows):
    keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("tf", "kind", "arm"), k))
    with open(path, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    sys.exit(main())
