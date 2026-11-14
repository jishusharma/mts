"""Render the table sections of RESULT.md from results.json (python make_result.py > tables.md). No judgement text here."""
import json
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "results.json")))
PH = ["UP", "DOWN", "RANGE"]


def lab(vid):
    p = vid.split("_")
    if p[0] == "A":
        return "A %s VWAP, %s, %s" % ({"U": "00:00", "N": "13:30"}[p[1]], {"I": "30m/5m", "P": "1d/30m"}[p[2]], "RSI>50 filter" if p[3] == "h1" else "no 50 filter")
    return "B %s th%s %s" % (p[1], p[2][1:], {"st": "Supertrap", "gp": "gap rule", "gd": "gap rule+PDHL"}[p[3]])


def f(x, nd=3):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else ("%+.*f" % (nd, x))


def rowtxt(r):
    v = r["val"]
    pl = r.get("placebo")
    g = r.get("gates", {})
    fails = [k for k, ok in g.items() if k != "PASS" and not ok]
    return "| %s | %d | %s | %s | %s | %s | %s | %s | %s | %s/%s | %s/%s | %s | %s | %s |" % (
        lab(r["vid"]), v["n"], f(v.get("mean")), f(2 * r["val6"]["mean"] - v["mean"]) if r["val6"].get("mean") is not None else "-", f(v.get("ci_day_lo")), f(v.get("ex5")), "%.2f" % r["fee_R_med"], f(r["val6"].get("mean")),
        "%d / %s" % (r["dev"]["n"], f(r["dev"]["mean"])), r["long"]["n"], f(r["long"]["mean"], 2), r["short"]["n"], f(r["short"]["mean"], 2),
        "%.3f" % pl["p"] if pl else "n/a", "yes" if r.get("bh_pass") else "no", "PASS" if g.get("PASS") else ("fails: " + ",".join(fails) if fails else "-"))


def main():
    rows = [r for r in R["rows"] if r["cut"] == "daily_phase"]
    out = []
    for ph in PH:
        rs = [r for r in rows if r["phase"] == ph]
        big = [r for r in rs if r["val"]["n"] >= 100]
        small = [r for r in rs if r["val"]["n"] < 100]
        out.append("### %s days (VALIDATION >= 2024-01-01, 12 bp net R per trade; columns: n, mean net R at 12 bp, gross R (= 2 x 6bp mean - 12bp mean), day-cluster CI low, ex-best-5-days mean, median fee/R, mean at 6 bp, DEV n / mean, long n/mean, short n/mean, placebo p, BH, gates)\n" % ph)
        out.append("| Variant | n | mean R | gross R | CI day lo | ex5 | fee/R | 6bp mean | DEV n / mean | long | short | placebo p | BH | gates |")
        out.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in sorted(big, key=lambda r: -r["val"]["mean"]):
            out.append(rowtxt(r))
        out.append("")
        out.append("UNDERPOWERED (n < 100, no verdict): " + "; ".join("%s n=%d mean %s" % (lab(r["vid"]), r["val"]["n"], f(r["val"].get("mean"), 2)) for r in small) + "\n")
    out.append("### Best VAL row per phase (highest mean net R at 12 bp, n >= 100)\n")
    out.append("| Phase | Variant | n | mean R | CI day lo | CI trade lo | ex5 | placebo p | BH | gates |")
    out.append("|---|---|---|---|---|---|---|---|---|---|")
    for ph in PH:
        rs = [r for r in rows if r["phase"] == ph and r["val"]["n"] >= 100]
        b = max(rs, key=lambda r: r["val"]["mean"]) if rs else None
        if b:
            v, g = b["val"], b["gates"]
            fails = [k for k, ok in g.items() if k != "PASS" and not ok]
            out.append("| %s | %s | %d | %s | %s | %s | %s | %s | %s | %s |" % (ph, lab(b["vid"]), v["n"], f(v["mean"]), f(v.get("ci_day_lo")), f(v.get("ci_trade_lo")), f(v.get("ex5")),
                       "%.3f" % b["placebo"]["p"] if b.get("placebo") else "n/a", "yes" if b["bh_pass"] else "no", "PASS" if g["PASS"] else "fails: " + ",".join(fails)))
    out.append("")
    out.append("### Cycle cut (BTC vs 200-week SMA), VALIDATION, descriptive, n >= 100 only\n")
    out.append("| Cycle | Variant | n | mean R 12bp | CI day lo | 6bp mean |")
    out.append("|---|---|---|---|---|---|")
    for r in sorted([r for r in R["rows"] if r["cut"] == "cycle" and r["val"]["n"] >= 100], key=lambda r: (r["phase"], -r["val"]["mean"])):
        out.append("| %s | %s | %d | %s | %s | %s |" % (r["phase"], lab(r["vid"]), r["val"]["n"], f(r["val"]["mean"]), f(r["val"].get("ci_day_lo")), f(r["val6"].get("mean"))))
    out.append("")
    print("\n".join(out))


if __name__ == "__main__":
    main()
