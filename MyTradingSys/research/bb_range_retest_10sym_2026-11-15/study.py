"""bb_range_retest_10sym_2026-11-15: the bb_range_retest_2026-11-04 rule (BB(20,2) excursion -> re-entry close -> retest of the band at
level +- k ATR, range-gated, session-range tagged), re-derived UNCHANGED on 10 Binance spot symbols, out of sample 2024-01-01..2026-11-14.
See PRE_REG.md. Event finder, level-arm entry, bracket and cell statistics are reused by path from the 11-04 studies (no rule edited).
Regime (research_kit.regime_tag) is the BTC market regime for every symbol. Passes: --pass count (no returns), --pass run."""
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
from MyTradingSys.backtest import research_kit as rk  # noqa: E402

_sp = importlib.util.spec_from_file_location("bb_lvl_arm", REPO / "MyTradingSys/research/bb_range_retest_2026-11-04/study.py")
lvl = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(lvl)
prev = lvl.prev
sib = prev._sib

CACHE = REPO / "runtime_data" / "bb-retest-10sym-1115"
SYMS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
DAY, TF_MS = 86400000, 900000
OOS_START = 1704067200000   # 2024-01-01 UTC
SPLIT_MS = 1751328000000    # 2025-07-01 UTC (sub-window boundary, descriptive and the same-sign rule)
OOS_END = 1794700800000     # 2026-11-15 UTC (exclusive; last 15m bar 2026-11-14 23:45)
K_GRID, CONFIRM = lvl.K_GRID, lvl.CONFIRM_SESSIONS
MIN_N, MIN_DAYS = lvl.MIN_N, lvl.MIN_DAYS


def load(sym, iv):
    rows = json.loads((CACHE / ("%s_%s.json" % (sym, iv))).read_text())
    return [{"t": r[0], "o": r[1], "h": r[2], "l": r[3], "c": r[4]} for r in rows]


def regime_fn():
    d, w, m = load("BTC", "1d"), load("BTC", "1w"), load("BTC", "1M")
    daily = ([x["t"] + DAY for x in d], [x["c"] for x in d])
    return sib.make_regime_at(daily, sib.rsi_series(w), sib.rsi_series(m))


def symbol_trades(sym, regime_at, lo, hi):
    bars = load(sym, "15m")
    gaps = sum(1 for a, b in zip(bars, bars[1:]) if b["t"] - a["t"] != TF_MS)
    tags = lvl.session_range_tags(bars, TF_MS)
    evs = prev.find_events(bars, TF_MS)
    for e in evs:
        e["session"] = rk.session_tag(e["t_close"] / 1000)
        e["tag"] = tags[e["i"]]
        e["regime"] = regime_at(e["t_close"]) or "none"
    ohlc = [(b["o"], b["h"], b["l"], b["c"]) for b in bars]
    inwin = [e for e in evs if lo <= e["t_close"] < hi]
    out = {}
    for k in K_GRID:
        trs = lvl.build_trades(evs, bars, k, lo, hi)
        for x in trs:
            x["sym"] = sym
        out[k] = trs
    for e in inwin:
        e["reentered"] = lvl.reentered(ohlc, e)
        e["sym"] = sym
    return out, inwin, gaps, len(bars)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pass_", required=True, choices=("count", "run"))
    a = ap.parse_args()
    regime_at = regime_fn()
    trades = {k: [] for k in K_GRID}
    events, meta = [], {}
    for s in SYMS:
        t, ev, gaps, nb = symbol_trades(s, regime_at, OOS_START, OOS_END)
        for k in K_GRID:
            trades[k] += t[k]
        events += ev
        meta[s] = {"bars": nb, "gaps": gaps, "signals": len(ev)}
        print(s, meta[s], file=sys.stderr, flush=True)
    mix = rk.regime_mix_line([regime_at(t) for t in lvl.week_starts(OOS_START, OOS_END)])
    rows = []
    for k in K_GRID:
        trs = trades[k]
        for sess in ("ALL",) + lvl.SESSIONS:
            for gate in ("range", "all"):
                for tag in ("tagged", "untagged", "any"):
                    sub = [x for x in trs if (sess == "ALL" or x["session"] == sess) and (gate == "all" or x["regime"] == gate)
                           and (tag == "any" or (x["tag"] if tag == "tagged" else not x["tag"]))]
                    ev_s = [e for e in events if (sess == "ALL" or e["session"] == sess) and (gate == "all" or e["regime"] == gate)
                            and (tag == "any" or (e["tag"] if tag == "tagged" else not e["tag"]))]
                    row = {"session": sess, "k": k, "gate": gate, "tag": tag, "signals": len(ev_s),
                           "reentered": sum(1 for e in ev_s if e["reentered"]),
                           "fills": sum(1 for e in ev_s if e.get("fill_" + str(k)) is not None)}
                    row["fill_rate"] = row["fills"] / row["signals"] if row["signals"] else float("nan")
                    if a.pass_ == "count":
                        row.update({"n": len(sub), "days": len({x["day"] for x in sub}),
                                    "median_stop_pct": float(np.median([x["stop_pct"] for x in sub])) if sub else float("nan")})
                    else:
                        row.update(prev.cell_stats(sub))
                        if gate == "range" and tag == "tagged":
                            oth = [x for x in trs if (sess == "ALL" or x["session"] == sess) and x["tag"]]
                            if sub and oth:
                                d, dse = rk.cluster_diff([x["gross"] for x in sub], [x["day"] for x in sub],
                                                         [x["gross"] for x in oth], [x["day"] for x in oth])
                                row.update({"vs_ungated": d, "vs_ungated_se": dse, "vs_ungated_t": rk.t_stat(d, dse)})
                            for nm, f in (("w1", lambda x: x["t"] < SPLIT_MS), ("w2", lambda x: x["t"] >= SPLIT_MS)):
                                st = prev.cell_stats([x for x in sub if f(x)])
                                row[nm + "_n"], row[nm + "_net"] = st["n"], st.get("net", float("nan"))
                    rows.append(row)
    if a.pass_ == "run":
        fam = [r for r in rows if r["gate"] == "range" and r["tag"] == "tagged" and r["session"] in CONFIRM and r.get("n", 0) > 0]
        adj = rk.holm([r["p"] if r["p"] == r["p"] else 1.0 for r in fam], m=len(CONFIRM) * len(K_GRID))
        for r, q in zip(fam, adj):
            r["holm_p"] = float(q)
            vt = r.get("vs_ungated_t", float("nan"))
            r["survivor"] = bool(r["n"] >= MIN_N and r["days"] >= MIN_DAYS and r["net"] > 0 and q < 0.05 and vt == vt and vt >= 2
                                 and r["w1_net"] > 0 and r["w2_net"] > 0)
        per = []
        for s in SYMS:
            for k in K_GRID:
                sub = [x for x in trades[k] if x["sym"] == s and x["regime"] == "range" and x["tag"]]
                per.append({"sym": s, "k": k, **prev.cell_stats(sub)})
        keys = sorted({kk for r in per for kk in r}, key=lambda kk: (kk not in ("sym", "k"), kk))
        with open(HERE / "per_symbol.csv", "w", newline="\n") as f:
            w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
            w.writeheader()
            w.writerows(per)
        (HERE / "survivors.json").write_text(json.dumps([[r["session"], r["k"]] for r in fam if r["survivor"]]))
    name = "counts.csv" if a.pass_ == "count" else "cells.csv"
    keys = sorted({kk for r in rows for kk in r}, key=lambda kk: (kk not in ("session", "k", "gate", "tag"), kk))
    with open(HERE / name, "w", newline="\n", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    (HERE / "meta.json").write_text(json.dumps(meta, indent=1))
    (HERE / "regime_mix.txt").write_text(mix + "\n")
    print(mix)
    return 0


if __name__ == "__main__":
    sys.exit(main())
