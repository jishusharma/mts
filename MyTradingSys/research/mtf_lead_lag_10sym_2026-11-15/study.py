"""mtf_lead_lag_10sym_2026-11-15: the mtf_lead_lag_2026-11-09 early-flip rules R1-R3 (RSI 60/40 state flips on 4h/1h/1d, code reused by path:
lead_lag.py, no line changed) re-derived UNCHANGED on 10 Binance spot symbols, out of sample 2024-01-01..2026-11-14. Cost = research_kit.TAKER_RT_PCT.
Passes: --pass count (events per rule, no returns), --pass run. See PRE_REG.md."""
import argparse
import csv
import importlib.util
import json
import sys
from bisect import bisect_left, bisect_right
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
from MyTradingSys.backtest import research_kit as rk  # noqa: E402


def _load(name, rel):
    sp = importlib.util.spec_from_file_location(name, REPO / rel)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


ll = _load("lead_lag_btc", "MyTradingSys/research/mtf_lead_lag_2026-11-09/lead_lag.py")
sib = _load("rsi_gated_sib", "MyTradingSys/research/rsi_divergence_mtf_gated_2026-11-04/study.py")

CACHE = REPO / "runtime_data" / "mtf-10sym-1115"
SYMS = "BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX".split()
DAY = 86400000
WEEK = 7 * DAY
OOS_START = 1704067200000   # 2024-01-01 UTC
SPLIT_MS = 1751328000000    # 2025-07-01 UTC
OOS_END = 1794700800000     # 2026-11-15 UTC exclusive
EV_END = OOS_END - WEEK     # events need a full 7-day look-forward for the hit test
MIN_N = 100
RULES = ("R1", "R2", "R3")
HORIZONS = (1, 3, 7)


def bars_of(sym, iv):
    return [{"t": r[0], "h": r[2], "l": r[3], "c": r[4]} for r in json.loads((CACHE / ("%s_%s.json" % (sym, iv))).read_text())]


def sym_data(sym):
    b = {tf: bars_of(sym, tf) for tf in ("1h", "4h", "1d")}
    f = {"rsi": {tf: ll.rsi_flips(b[tf], ll.STEP[tf]) for tf in b}, "wt": {tf: ll.wt_flips(b[tf], ll.STEP[tf]) for tf in b}}
    r1d = ll.rsi_core([x["c"] for x in b["1d"]], 14)
    dc = [x["t"] + ll.STEP["1d"] for x in b["1d"]]

    def rsi1d_val(t):
        i = bisect_right(dc, t) - 1
        return r1d[i] if i >= 0 else None
    f["rsi1d_val"] = rsi1d_val
    return b, f


def fwd_ret(b1h, ts, t, s, days):
    i = bisect_left(ts, t)
    k = i + 24 * days
    if i >= len(ts) or k >= len(ts) or ts[i] != t:
        return None
    r = b1h[k]["c"] / b1h[i]["c"] - 1
    return r if s == "BULL" else -r


def hit(t, s, d_ts, d_f):
    i = bisect_left(d_ts, t)
    while i < len(d_ts) and d_ts[i] <= t + WEEK:
        if d_f[i][1] == s:
            return 1
        i += 1
    return 0


def mkrow(sym, rule, s, t, b1h, ts, d_ts, d_f, regime_at):
    row = dict(sym=sym, rule=rule, side=s, t=t, day=t // DAY, week=t // WEEK, hit=hit(t, s, d_ts, d_f),
               regime=(regime_at(t) or "none") if rule != "BASE" else "", win="w1" if t < SPLIT_MS else "w2")
    for d in HORIZONS:
        row["fwd_%dd" % d] = fwd_ret(b1h, ts, t, s, d)
    return row


def build(regime_at):
    ev, base = [], []
    leads = {k: [] for k in ("rsi", "wt")}
    for sym in SYMS:
        b, f = sym_data(sym)
        ts = [x["t"] + ll.STEP["1h"] for x in b["1h"]]
        d_f = f["rsi"]["1d"]
        d_ts = [x[0] for x in d_f]
        for rule in RULES:
            for t, s in ll.rule_events(rule, f, OOS_START, EV_END):
                ev.append(mkrow(sym, rule, s, t, b["1h"], ts, d_ts, d_f, regime_at))
        for t in range(OOS_START, EV_END, ll.STEP["4h"]):          # unconditional grid, every 4h close, both directions
            for s in ("BULL", "BEAR"):
                base.append(mkrow(sym, "BASE", s, t, b["1h"], ts, d_ts, d_f, regime_at))
        for ind in ("rsi", "wt"):
            lo_f = f[ind]["4h"]
            tab = ll.lead_table(f[ind]["1d"], lo_f, [x[0] for x in lo_f], OOS_START, EV_END)
            leads[ind].append((sym, tab))
    return ev, base, leads


def net_stats(rows, h, week_cluster=False):
    v = [(r["fwd_%dd" % h], r["week"] if week_cluster else r["day"]) for r in rows if r["fwd_%dd" % h] is not None]
    if not v:
        return dict(n=0)
    g = np.array([x[0] for x in v]) * 100
    nt = g - rk.TAKER_RT_PCT
    cl = [x[1] for x in v]
    m, se = rk.cluster_mean_se(nt, cl)
    t = rk.t_stat(m, se)
    return dict(n=len(v), days=len({r["day"] for r in rows}), gross=g.mean(), net=m, se=se, t=t, p=rk.norm_p_two(t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="ps", choices=("count", "run"), required=True)
    ps = ap.parse_args().ps

    def series(iv):
        return [{"t": r[0], "c": r[4]} for r in json.loads((CACHE / ("BTC_%s.json" % iv)).read_text())]
    d = series("1d")
    daily = ([x["t"] + DAY for x in d], [x["c"] for x in d])
    regime_at = sib.make_regime_at(daily, sib.rsi_series(series("1w")), sib.rsi_series(series("1M")))
    ev, base, leads = build(regime_at)
    if ps == "count":
        with open(HERE / "counts.csv", "w", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["rule", "events", "days"])
            for r in RULES:
                sub = [x for x in ev if x["rule"] == r]
                w.writerow([r, len(sub), len({x["day"] for x in sub})])
                print(r, len(sub), len({x["day"] for x in sub}))
        return
    mix = rk.regime_mix_line([regime_at(t) for t in sib.week_starts(OOS_START, OOS_END)])
    (HERE / "regime_mix.txt").write_text(mix + "\n")
    bst = {h: net_stats(base, h) for h in HORIZONS}
    base_hit = float(np.mean([x["hit"] for x in base]))
    bv = [x for x in base if x["fwd_3d"] is not None]
    bnet = np.array([x["fwd_3d"] for x in bv]) * 100 - rk.TAKER_RT_PCT
    fam = {}
    for r in RULES:
        sub = [x for x in ev if x["rule"] == r]
        s = net_stats(sub, 3)
        s["se_week"] = net_stats(sub, 3, True)["se"]
        s["se_used"] = float(max(s["se"], s["se_week"]))
        s["t_used"] = rk.t_stat(s["net"], s["se_used"])
        s["p_used"] = rk.norm_p_two(s["t_used"])
        s["hit"] = float(np.mean([x["hit"] for x in sub]))
        sv = [x for x in sub if x["fwd_3d"] is not None]
        dd, dse = rk.cluster_diff(np.array([x["fwd_3d"] for x in sv]) * 100 - rk.TAKER_RT_PCT, [x["day"] for x in sv],
                                  bnet, [x["day"] for x in bv])
        s["vs_base"], s["vs_base_se"] = dd, dse
        fam[r] = s
    adj = rk.holm([fam[r]["p_used"] if fam[r]["p_used"] == fam[r]["p_used"] else 1.0 for r in RULES], m=3)
    rows = []
    for r, q in zip(RULES, adj):
        s = fam[r]
        sub = [x for x in ev if x["rule"] == r]
        s["holm_p"] = float(q)
        s["w1_net"] = net_stats([x for x in sub if x["win"] == "w1"], 3).get("net", float("nan"))
        s["w2_net"] = net_stats([x for x in sub if x["win"] == "w2"], 3).get("net", float("nan"))
        s["hit_lift_pts"] = 100 * (s["hit"] - base_hit)
        s["edge"] = bool(s["n"] >= MIN_N and s["net"] > 0 and s["holm_p"] < 0.05 and s["w1_net"] > 0 and s["w2_net"] > 0
                         and s["hit_lift_pts"] >= 10 and s["vs_base"] > 2 * s["vs_base_se"])
        rows.append(dict(rule=r, cut="family_3d", **s))
        for h in (1, 7):
            rows.append(dict(rule=r, cut="fwd_%dd" % h, **net_stats(sub, h)))
        cuts = [("side=" + s_, [x for x in sub if x["side"] == s_]) for s_ in ("BULL", "BEAR")]
        cuts += [("regime=" + g, [x for x in sub if x["regime"] == g]) for g in ("bull", "bear", "range")]
        cuts += [("win=" + w, [x for x in sub if x["win"] == w]) for w in ("w1", "w2")]
        cuts += [("sym=" + y, [x for x in sub if x["sym"] == y]) for y in SYMS]
        for name, sb in cuts:
            st = net_stats(sb, 3)
            st["hit"] = float(np.mean([x["hit"] for x in sb])) if sb else float("nan")
            rows.append(dict(rule=r, cut=name, **st))
    for h in HORIZONS:
        rows.append(dict(rule="BASE", cut="fwd_%dd" % h, **bst[h]))
    cols = ["rule", "cut", "n", "days", "gross", "net", "se", "se_week", "se_used", "t", "p", "p_used", "holm_p", "hit", "hit_lift_pts",
            "vs_base", "vs_base_se", "w1_net", "w2_net", "edge"]
    with open(HERE / "cells.csv", "w", newline="") as f:
        w = csv.DictWriter(f, cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
    with open(HERE / "leads.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["ind", "sym", "n", "with_lead", "median_h", "iqr_h"])
        for ind in ("rsi", "wt"):
            for sym, tab in leads[ind]:
                w.writerow([ind, sym, tab.get("n"), tab.get("with_lead"), tab.get("median_h", ""), json.dumps(tab.get("iqr_h", ""))])
    (HERE / "meta.json").write_text(json.dumps(dict(base_hit_1d_flip_7d=base_hit, base=bst), indent=1, default=float))
    print(mix, "base hit", round(base_hit, 3))
    for r in rows:
        if r["cut"] == "family_3d" or r["cut"].startswith(("side", "regime", "win", "fwd_")):
            print(r["rule"], r["cut"], {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k not in ("rule", "cut")})


if __name__ == "__main__":
    main()
