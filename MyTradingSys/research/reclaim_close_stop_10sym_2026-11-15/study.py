"""reclaim_close_stop_10sym_2026-11-15: the reclaim_close_stop_2026-11 rule (fractal swing break by 0.1 ATR, reclaim close within N bars, enter at
the reclaim close, stop = first close back beyond the level, cap 6 bars 4h / 5 bars 1D) re-derived UNCHANGED on 10 Binance spot symbols, out of
sample 2024-01-01..2026-11-14. Event finder reused by path (reclaim.events, no line changed). Cost = research_kit.TAKER_RT_PCT. See PRE_REG.md.
Passes: --pass count (events and days only, no returns), --pass run."""
import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import research_kit as rk  # noqa: E402


def _load(name, rel):
    sp = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


reclaim = _load("reclaim_btc", "MyTradingSys/research/reclaim_close_stop_2026-11/reclaim.py")
sib = _load("rsi_gated_sib", "MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/study.py")

CACHE = REPO / "runtime_data" / "reclaim-10sym-1115"
SYMS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
DAY = 86400000
TF_MS = {"4h": 4 * 3600000, "1D": DAY}
IV = {"4h": "4h", "1D": "1d"}
OOS_START = 1704067200000   # 2024-01-01 UTC
SPLIT_MS = 1751328000000    # 2025-07-01 UTC
OOS_END = 1794700800000     # 2026-11-15 UTC exclusive
MIN_N = 100
COST = rk.TAKER_RT_PCT / 100.0


def load(sym, iv):
    rows = json.loads((CACHE / ("%s_%s.json" % (sym, iv))).read_text())
    return rows


def regime_fn():
    def bars(iv):
        return [{"t": r[0], "c": r[4]} for r in load("BTC", iv)]
    d, w, m = bars("1d"), bars("1w"), bars("1M")
    daily = ([x["t"] + DAY for x in d], [x["c"] for x in d])
    return sib.make_regime_at(daily, sib.rsi_series(w), sib.rsi_series(m))


def sym_events(sym, tf, regime_at):
    rows = load(sym, IV[tf])
    b = pd.DataFrame({"t": [r[0] for r in rows], "h": [r[2] for r in rows], "l": [r[3] for r in rows], "c": [r[4] for r in rows]})
    out = []
    for e in reclaim.events(b, tf):
        tc = int(e["t"]) + TF_MS[tf]  # fill = close of the reclaim bar
        if not (OOS_START <= tc < OOS_END):
            continue
        out.append(dict(sym=sym, tf=tf, side=e["side"], t_close=tc, day=tc // DAY, gross=e["gross"], net=e["gross"] - COST,
                        hold=e["hold"], exit=e["exit"], regime=regime_at(tc) or "none",
                        win="w1" if tc < SPLIT_MS else "w2"))
    return out


def stats(sub):
    n = len(sub)
    if n == 0:
        return dict(n=0, days=0)
    g = np.array([x["gross"] for x in sub]) * 100
    nt = np.array([x["net"] for x in sub]) * 100
    day = [x["day"] for x in sub]
    m, se = rk.cluster_mean_se(nt, day)
    t = rk.t_stat(m, se) if se == se else float("nan")
    p = rk.norm_p_two(t) if t == t else float("nan")
    return dict(n=n, days=len(set(day)), gross=g.mean(), net=m, se=se, t=t, p=p, win_pct=100 * (nt > 0).mean(),
                stop_share=np.mean([x["exit"] == "stop" for x in sub]), mean_hold=np.mean([x["hold"] for x in sub]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="ps", choices=("count", "run"), required=True)
    ps = ap.parse_args().ps
    regime_at = regime_fn()
    ev = {tf: [x for s in SYMS for x in sym_events(s, tf, regime_at)] for tf in ("4h", "1D")}
    if ps == "count":
        with open(HERE / "counts.csv", "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["arm", "events", "days"])
            for tf in ev:
                w.writerow([tf, len(ev[tf]), len({x["day"] for x in ev[tf]})])
                print(tf, len(ev[tf]), len({x["day"] for x in ev[tf]}))
        return
    mix = rk.regime_mix_line([regime_at(t) for t in sib.week_starts(OOS_START, OOS_END)])
    (HERE / "regime_mix.txt").write_text(mix + "\n")
    fam = {}
    rows = []
    for tf in ev:
        fam[tf] = stats(ev[tf])
    adj = rk.holm([fam[t]["p"] if fam[t].get("p") == fam[t].get("p") and "p" in fam[t] else 1.0 for t in fam], m=2)
    for (tf, r), q in zip(fam.items(), adj):
        r["holm_p"] = float(q)
        r["w1_net"] = stats([x for x in ev[tf] if x["win"] == "w1"]).get("net", float("nan"))
        r["w2_net"] = stats([x for x in ev[tf] if x["win"] == "w2"]).get("net", float("nan"))
        r["edge"] = bool(r["n"] >= MIN_N and r["net"] > 0 and r["holm_p"] < 0.05 and r["w1_net"] > 0 and r["w2_net"] > 0)
        rows.append(dict(arm=tf, cut="family", **r))
        for name, sub in [("side=" + s, [x for x in ev[tf] if x["side"] == s]) for s in ("low", "high")] + \
                         [("regime=" + g, [x for x in ev[tf] if x["regime"] == g]) for g in ("bull", "bear", "range")] + \
                         [("win=" + w, [x for x in ev[tf] if x["win"] == w]) for w in ("w1", "w2")] + \
                         [("sym=" + s, [x for x in ev[tf] if x["sym"] == s]) for s in SYMS]:
            rows.append(dict(arm=tf, cut=name, **stats(sub)))
    cols = ["arm", "cut", "n", "days", "gross", "net", "se", "t", "p", "holm_p", "win_pct", "stop_share", "mean_hold", "w1_net", "w2_net", "edge"]
    with open(HERE / "cells.csv", "w", newline="") as f:
        w = csv.DictWriter(f, cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    print(mix)
    for r in rows:
        if r["cut"] == "family" or r["cut"].startswith(("side", "regime", "win")):
            print(r["arm"], r["cut"], {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k not in ("arm", "cut")})


if __name__ == "__main__":
    main()
