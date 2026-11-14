"""Run Test 1 exactly as PRE_REG.md. Writes REPORT.md and summary.json next to this file. Data from the host cache, never committed."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ladder as L
from fetch_spot import CACHE, UNIVERSE

HERE = os.path.dirname(os.path.abspath(__file__))
NDRAW = 2000
SPLITS = ["DEV", "VAL", "RECENT", "ALL"]
LONG = ("UP", "BASE")


def load():
    out = {}
    for c in UNIVERSE:
        a = np.array(json.load(open(os.path.join(CACHE, c + "USDT.json"))), float)
        a = a[:-1]  # drop the partial current day
        out[c] = (a[:, 0].astype(np.int64), a[:, 1], a[:, 2], a[:, 3], a[:, 4])
    return out


def pick(evs, phases, split):
    return [e for e in evs if e["phase"] in phases and L.in_split(e["ts"], split)]


def Rs(evs, fee):
    return np.array([L.R_of(e["gross"], e["r"], fee) for e in evs])


def cell(evs, table, phases, split, do_placebo=True):
    sel = pick(evs, phases, split)
    d = dict(n=len(sel))
    if not sel:
        return d
    r12, r6 = Rs(sel, L.FEES["12"]), Rs(sel, L.FEES["6"])
    d.update(win=float(np.mean([e["gross"] - L.FEES["12"] > 0 for e in sel])), R12=float(r12.mean()), R6=float(r6.mean()))
    lo, hi = L.block_ci([e["ts"] for e in sel], r12)
    d.update(ci_lo=float(lo), ci_hi=float(hi))
    if do_placebo:
        draws = L.placebo(table, sel, split, L.FEES["12"], NDRAW)
        if len(draws):
            d.update(pl_lo=float(np.percentile(draws, 2.5)), pl_hi=float(np.percentile(draws, 97.5)),
                     pl_mean=float(draws.mean()), pl_pct=float((draws <= r12.mean()).mean() * 100))
        draws6 = L.placebo(table, sel, split, L.FEES["6"], NDRAW)
        if len(draws6):
            d.update(pl_pct6=float((draws6 <= r6.mean()).mean() * 100))
    return d


def row(d):
    if d["n"] == 0:
        return "0 | | | | | "
    pl = ("%.1f%% (band %.3f..%.3f; 6bp pct %.1f%%)" % (d["pl_pct"], d["pl_lo"], d["pl_hi"], d.get("pl_pct6", float("nan")))) if "pl_pct" in d else ""
    return "%d | %.0f%% | %.3f | %.3f | [%.2f, %.2f] | %s" % (d["n"], d["win"] * 100, d["R12"], d["R6"], d["ci_lo"], d["ci_hi"], pl)


def verdict(res):
    v, dev = res["VAL"], res["DEV"]
    if v["n"] < 30:
        return "UNDERPOWERED (VAL n=%d < 30), no claim" % v["n"]
    ok = (v["R12"] > 0 and v["ci_lo"] > 0 and v.get("pl_pct", 0) > 97.5 and dev["n"] > 0 and dev["R12"] > 0)
    s = "VAL n=%d meanR12=%.3f CI[%.3f, %.3f] placebo pct=%.1f (97.5th=%.3f) DEV n=%d meanR12=%s" % (
        v["n"], v["R12"], v["ci_lo"], v["ci_hi"], v.get("pl_pct", float("nan")), v.get("pl_hi", float("nan")),
        dev["n"], ("%.3f" % dev["R12"]) if dev["n"] else "n/a")
    return ("PASS: " if ok else "KILL: ") + s


def main():
    data = load()
    table = L.PlaceboTable(data)
    summary, lines = {}, []
    P = lines.append
    P("# REPORT: Test 1, causal confirmation ladder, long side\n")
    P("Rules frozen in `PRE_REG.md` (committed before any outcome). Data: Binance spot daily, host cache, not committed. Code: `ladder.py`, `run_test1.py`, tests `test_ladder.py`. Nothing here is a trade instruction.\n")
    P("## Coverage and regime mix (share of coin-days per phase per split, post warm-up)\n")
    P("| coin | bars | first day |\n|---|---|---|")
    for c, (ts, o, h, l, cl) in data.items():
        P("| %s | %d | %s |" % (c, len(cl), str(np.datetime64(int(ts[0]), "ms"))[:10]))
    mix = {sp: {p: 0 for p in L.PHASES} for sp in ["DEV", "VAL"]}
    for c, (ts, o, h, l, cl) in data.items():
        ph = L.phases(h, l, cl)
        for i in range(L.WARM + 1, len(cl)):
            if ph[i - 1] in mix["DEV"]:
                mix[L.split_of(ts[i])][ph[i - 1]] += 1
    P("\n| split | " + " | ".join(L.PHASES) + " |\n|---|" + "---|" * len(L.PHASES))
    for sp in mix:
        tot = sum(mix[sp].values()) or 1
        P("| %s | " % sp + " | ".join("%.1f%%" % (100 * mix[sp][p] / tot) for p in L.PHASES) + " |")
    summary["regime_mix"] = mix

    for mode, name in (("A", "A HL_BREAK (PRIMARY)"), ("B", "B BULL_DIV (SECONDARY)")):
        evs, drop, per_coin = [], 0, {}
        for c, (ts, o, h, l, cl) in data.items():
            e, dr = L.build_events(c, ts, o, h, l, cl, mode)
            evs += e
            drop += dr
            per_coin[c] = e
        P("\n## Candidate %s\n" % name)
        P("Events kept after lockout: %d; dropped for entry <= stop: %d; with a phase label: %d.\n" % (
            len(evs), drop, sum(1 for e in evs if e["phase"] in L.PHASES)))
        S = summary[mode] = {"events": len(evs), "cells": {}}
        groups = [("UP+BASE (claim)", LONG)] + [(p, (p,)) for p in L.PHASES]
        P("### Pooled by phase group and split (mean R fee-net; placebo = %d same-coin same-phase same-stop draws)\n" % NDRAW)
        P("| group | split | n | win % | mean R 12bp | mean R 6bp | 95% CI (12bp) | placebo pct (12bp) |\n|---|---|---|---|---|---|---|---|")
        for gname, ph in groups:
            S["cells"][gname] = {}
            for sp in SPLITS:
                d = cell(evs, table, ph, sp)
                S["cells"][gname][sp] = d
                P("| %s | %s | %s |" % (gname, sp, row(d)))
        P("\n### Per coin, UP+BASE (n<30 per cell is UNDERPOWERED; no verdict from a coin)\n")
        P("| coin | split | n | win % | mean R 12bp | mean R 6bp |\n|---|---|---|---|---|---|")
        S["per_coin"] = {}
        for c, e in per_coin.items():
            S["per_coin"][c] = {}
            for sp in ("DEV", "VAL", "RECENT", "ALL"):
                d = cell(e, table, LONG, sp, do_placebo=False)
                S["per_coin"][c][sp] = d
                if d["n"]:
                    P("| %s | %s | %d%s | %.0f%% | %.3f | %.3f |" % (c, sp, d["n"], " (under)" if d["n"] < 30 else "", d["win"] * 100, d["R12"], d["R6"]))
        vl = pick(evs, LONG, "VAL")
        if vl:
            by_year, top = {}, {}
            for e in vl:
                y = str(np.datetime64(e["ts"], "ms"))[:4]
                by_year[y] = by_year.get(y, 0) + 1
                top[e["coin"]] = top.get(e["coin"], 0) + 1
            mxy = max(by_year.values()) / len(vl)
            S["val_by_year"], S["one_year"] = by_year, bool(mxy > 0.85)
            P("\nVAL long-phase events by year: %s; largest-year share %.0f%% -> %s" % (by_year, mxy * 100, "ONE-YEAR flag" if mxy > 0.85 else "not one-year"))
            P("VAL long-phase events by coin: %s" % dict(sorted(top.items(), key=lambda kv: -kv[1])))
        S["verdict"] = verdict(S["cells"]["UP+BASE (claim)"])
        P("\n**VERDICT %s: %s**" % (mode, S["verdict"]))
        if mode == "B":
            P("(Secondary: two tests run, multiplicity noted; a B-only PASS needs independent replication before any use.)")
    json.dump(summary, open(os.path.join(HERE, "summary.json"), "w"), indent=1, default=float)
    open(os.path.join(HERE, "REPORT.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(l for l in lines if l.startswith("**VERDICT")))


if __name__ == "__main__":
    main()
