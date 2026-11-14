"""Run Test 3 exactly as PRE_REG.md. Writes REPORT.md and summary.json next to this file. Data from the host cache, never committed."""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bear4h as B
from fetch_data import D1, FUND, H4, UNIVERSE

HERE = os.path.dirname(os.path.abspath(__file__))
NDRAW = 2000
SPLITS = ["DEV", "VAL", "RECENT", "ALL"]


def load_arr(path):
    a = np.array(json.load(open(path)), float)[:-1]    # drop the last, possibly partial bar
    return a[:, 0].astype(np.int64), a[:, 1], a[:, 2], a[:, 3], a[:, 4]


def load():
    coins = {}
    for c in UNIVERSE:
        ts, o, h, l, cl = load_arr(os.path.join(H4, c + "USDT.json"))
        dts, do, dh, dl, dc = load_arr(os.path.join(D1, c + "USDT.json"))
        bear_d, lab_d = B.daily_flags(dh, dl, dc)
        bearA = B.map_prev_day(ts, dts, bear_d, False)
        labA = B.map_prev_day(ts, dts, lab_d, "")
        fund = json.load(open(os.path.join(FUND, c + "USDT.json")))
        G, first = B.funding_cum(ts, fund)
        coins[c] = dict(ts=ts, o=o, h=h, l=l, c=cl, bearA=bearA, labA=labA, G=G, first=first, dts=dts, bear_d=bear_d, lab_d=lab_d)
    return coins


def sel(evs, group, split):
    out = []
    for e in evs:
        if group == "BEAR":
            ok = e["bear"]
        elif group.startswith("BEAR/"):
            ok = e["bear"] and e["label"] == group[5:]
        else:
            ok = (not e["bear"]) and e["label"] == group
        if ok and B.in_split(e["ts"], split):
            out.append(e)
    return out


def Rv(evs, fee, w):
    return np.array([B.R_of(e, fee, w) for e in evs])


def cell(evs, table, group, split, do_placebo):
    s = sel(evs, group, split)
    d = dict(n=len(s))
    if not s:
        return d
    F = B.FEES
    d.update(win=float(np.mean([e["gross"] - F["12"] > 0 for e in s])),
             R12nf=float(Rv(s, F["12"], False).mean()), R12f=float(Rv(s, F["12"], True).mean()),
             R6nf=float(Rv(s, F["6"], False).mean()), R6f=float(Rv(s, F["6"], True).mean()),
             fund_mean=float(np.mean([e["fund"] for e in s])), uncovered=int(sum(1 for e in s if not e["covered"])))
    for w, tag in ((False, "nf"), (True, "f")):
        lo, hi = B.L1.block_ci([e["ts"] for e in s], Rv(s, F["12"], w), block_days=7)
        d["ci_lo_" + tag], d["ci_hi_" + tag] = float(lo), float(hi)
    if do_placebo:
        dr = B.placebo(table, s, split, NDRAW)
        for (f, w), arr in dr.items():
            if len(arr) == 0:
                continue
            tag = f + ("f" if w else "nf")
            actual = d["R" + tag]
            d["pl_pct_" + tag] = float((arr <= actual).mean() * 100)
            d["pl_lo_" + tag], d["pl_hi_" + tag] = float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))
            d["pl_n_" + tag] = int(len(arr))
    return d


def row(d):
    if d["n"] == 0:
        return "0 | | | | | | | | "
    pl = ""
    if "pl_pct_12nf" in d:
        pl = "nf %.1f%% [%.3f..%.3f] / f %.1f%% [%.3f..%.3f]" % (d["pl_pct_12nf"], d["pl_lo_12nf"], d["pl_hi_12nf"],
                                                                 d.get("pl_pct_12f", float("nan")), d.get("pl_lo_12f", float("nan")), d.get("pl_hi_12f", float("nan")))
    return "%d%s | %.0f%% | %.3f | %.3f | %.3f | %.3f | nf [%.2f, %.2f] f [%.2f, %.2f] | %s" % (
        d["n"], " (under)" if d["n"] < 30 else "", d["win"] * 100, d["R12nf"], d["R12f"], d["R6nf"], d["R6f"],
        d["ci_lo_nf"], d["ci_hi_nf"], d["ci_lo_f"], d["ci_hi_f"], pl)


def verdict(res):
    v, dev = res["VAL"], res["DEV"]
    if v["n"] < 30:
        return "UNDERPOWERED (VAL n=%d < 30), no claim" % v["n"]
    ok = dev["n"] > 0
    parts = []
    for tag, name in (("nf", "no-funding"), ("f", "with-funding")):
        good = (v["R12" + tag] > 0 and v["ci_lo_" + tag] > 0 and v.get("pl_pct_12" + tag, 0) > 97.5 and dev["n"] > 0 and dev["R12" + tag] > 0)
        ok = ok and good
        parts.append("%s: VAL meanR12=%.3f CI[%.3f, %.3f] placebo pct=%.1f (97.5th=%.3f) DEV meanR12=%s" % (
            name, v["R12" + tag], v["ci_lo_" + tag], v["ci_hi_" + tag], v.get("pl_pct_12" + tag, float("nan")),
            v.get("pl_hi_12" + tag, float("nan")), ("%.3f" % dev["R12" + tag]) if dev["n"] else "n/a"))
    return ("PASS" if ok else "KILL") + " (VAL n=%d, DEV n=%d) | " % (v["n"], dev["n"]) + " | ".join(parts)


def main():
    data = load()
    table = B.PlaceboTable(data)
    summary, lines = {}, []
    P = lines.append
    P("# REPORT: Test 3, bear-phase 4H bearish-divergence short, 22 coins, with funding\n")
    P("Rules frozen in `PRE_REG.md` (committed before any outcome). Price: Binance spot 1d and 4h (host cache, not committed). Funding: Bybit linear perpetual funding history used as the proxy (NOT Binance futures). Code: `bear4h.py`, `run_test3.py`, `fetch_data.py`, tests `test_bear4h.py`. Nothing here is a trade instruction.\n")
    P("## Coverage\n")
    P("| coin | 4H bars | first 4H bar | funding from |\n|---|---|---|---|")
    for c, d in data.items():
        P("| %s | %d | %s | %s |" % (c, len(d["c"]), str(np.datetime64(int(d["ts"][0]), "ms"))[:10],
                                     str(np.datetime64(int(d["first"]), "ms"))[:10] if d["first"] else "none (funding 0)"))
    mix = {sp: {k: 0 for k in ["BEAR"] + B.T1_PHASES} for sp in ("DEV", "VAL")}
    for c, d in data.items():
        for i in range(len(d["dts"])):
            if d["lab_d"][i] == "":
                continue
            sp = "DEV" if d["dts"][i] + B.DAY < B.VAL_START else "VAL"
            mix[sp][d["lab_d"][i]] += 1
            mix[sp]["BEAR"] += int(d["bear_d"][i])
    P("\n### Regime mix (share of coin-days with a defined phase, per split; BEAR overlaps the Test 1 labels DOWN and POSTPEAK_BEAR)\n")
    P("| split | BEAR | " + " | ".join(B.T1_PHASES) + " |\n|---|---|" + "---|" * len(B.T1_PHASES))
    for sp in mix:
        tot = sum(mix[sp][p] for p in B.T1_PHASES) or 1
        P("| %s | " % sp + " | ".join("%.1f%%" % (100 * mix[sp][k] / tot) for k in ["BEAR"] + B.T1_PHASES) + " |")
    summary["regime_mix"] = mix

    evs, drop, per_coin = [], 0, {}
    for c, d in data.items():
        e, dr = B.build_events(c, d["ts"], d["o"], d["h"], d["l"], d["c"], d["bearA"], d["labA"], d["G"], d["first"])
        evs += e
        drop += dr
        per_coin[c] = e
    P("\nEvents kept after lockout: %d (BEAR %d); dropped for entry >= stop: %d; claim events without funding coverage: %d.\n" % (
        len(evs), sum(e["bear"] for e in evs), drop, sum(1 for e in evs if e["bear"] and not e["covered"])))
    S = summary["cells"] = {}
    groups = ["BEAR"] + ["BEAR/" + p for p in B.T1_PHASES] + B.T1_PHASES
    P("## Pooled by group and split\n")
    P("BEAR = claim. `BEAR/<phase>` = claim events by Test 1 label (descriptive, no placebo). Bare phase names = BEAR false = control. Columns: mean R fee-net 12 bp / 6 bp, no funding (nf) / with funding (f); placebo = %d same-coin same-group same-stop draws, percentile of the actual 12 bp mean and the 2.5..97.5 band.\n" % NDRAW)
    P("| group | split | n | win % | R12 nf | R12 f | R6 nf | R6 f | 95% CI (12 bp) | placebo |\n|---|---|---|---|---|---|---|---|---|---|")
    for g in groups:
        S[g] = {}
        for sp in SPLITS:
            d = cell(evs, table, g, sp, do_placebo=not g.startswith("BEAR/"))
            S[g][sp] = d
            if d["n"]:
                P("| %s | %s | %s |" % (g, sp, row(d)))
    P("\n### Per coin, BEAR (n<30 per cell is UNDERPOWERED; no verdict from a coin)\n")
    P("| coin | split | n | win % | R12 nf | R12 f | R6 nf | R6 f |\n|---|---|---|---|---|---|---|---|")
    summary["per_coin"] = {}
    for c, e in per_coin.items():
        summary["per_coin"][c] = {}
        for sp in SPLITS:
            d = cell(e, table, "BEAR", sp, do_placebo=False)
            summary["per_coin"][c][sp] = d
            if d["n"]:
                P("| %s | %s | %d%s | %.0f%% | %.3f | %.3f | %.3f | %.3f |" % (c, sp, d["n"], " (under)" if d["n"] < 30 else "", d["win"] * 100, d["R12nf"], d["R12f"], d["R6nf"], d["R6f"]))
    vb = sel(evs, "BEAR", "VAL")
    if vb:
        by_year, by_coin = {}, {}
        for e in vb:
            y = str(np.datetime64(e["ts"], "ms"))[:4]
            by_year[y] = by_year.get(y, 0) + 1
            by_coin[e["coin"]] = by_coin.get(e["coin"], 0) + 1
        mxy = max(by_year.values()) / len(vb)
        summary["val_by_year"], summary["one_year"] = by_year, bool(mxy > 0.85)
        P("\nVAL claim events by year: %s; largest-year share %.0f%% -> %s" % (by_year, mxy * 100, "ONE-YEAR flag" if mxy > 0.85 else "not one-year"))
        P("VAL claim events by coin: %s" % dict(sorted(by_coin.items(), key=lambda kv: -kv[1])))
        top = max(by_coin, key=by_coin.get)
        rest = [e for e in evs if e["coin"] != top]
        d = cell(rest, table, "BEAR", "VAL", False)
        summary["without_top_coin"] = dict(coin=top, **d)
        if d["n"]:
            P("\nVAL BEAR with top coin %s removed (descriptive): n=%d R12 nf %.3f f %.3f R6 nf %.3f f %.3f" % (top, d["n"], d["R12nf"], d["R12f"], d["R6nf"], d["R6f"]))
    P("\n### BTC only (replication check of the earlier +1.03 R, n=28 figure; descriptive)\n")
    P("| split | n | win % | R12 nf | R12 f | R6 nf | R6 f |\n|---|---|---|---|---|---|---|")
    summary["btc"] = {}
    for sp in SPLITS:
        d = cell(per_coin["BTC"], table, "BEAR", sp, False)
        summary["btc"][sp] = d
        if d["n"]:
            P("| %s | %d | %.0f%% | %.3f | %.3f | %.3f | %.3f |" % (sp, d["n"], d["win"] * 100, d["R12nf"], d["R12f"], d["R6nf"], d["R6f"]))
    summary["verdict"] = verdict(S["BEAR"])
    P("\n**VERDICT: %s**" % summary["verdict"])
    json.dump(summary, open(os.path.join(HERE, "summary.json"), "w"), indent=1, default=float)
    open(os.path.join(HERE, "REPORT.md"), "w").write("\n".join(lines) + "\n")
    print("VERDICT:", summary["verdict"])


if __name__ == "__main__":
    main()
