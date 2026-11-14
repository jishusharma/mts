"""Run Test 4 exactly as PRE_REG.md. Writes REPORT.md and summary.json next to this file. Data from the host cache, never committed."""
import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib as T
from fetch import UNIVERSE

HERE = os.path.dirname(os.path.abspath(__file__))
NDRAW = 2000
SPLITS = ["DEV", "VAL", "RECENT", "ALL"]
PHASES = ["UP", "BASE", "RANGE", "DOWN", "POSTPEAK_BEAR", "NOPHASE"]


def pct(x):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else "%.1f%%" % (x * 100)


def f3(x):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else "%.3f" % x


def fisher(a, b, c, d):
    try:
        from scipy.stats import fisher_exact
        return float(fisher_exact([[a, b], [c, d]])[1])
    except Exception:
        return None


def lows_table(rows):
    """rows: list of dict(coin, i, fwd{1,3,7}, ll(True/False/None), flags)."""
    out = {}
    groups = {
        "ALL": lambda r: True, "SIG (F+O+B)": lambda r: r["F"] and r["O"] and r["B"],
        "NOT-SIG": lambda r: not (r["F"] and r["O"] and r["B"]),
        "F only-flag (funding<0)": lambda r: r["F"], "O (OI unwind)": lambda r: r["O"], "B (failed breakdown)": lambda r: r["B"],
        "F+O": lambda r: r["F"] and r["O"], "F+B": lambda r: r["F"] and r["B"], "O+B": lambda r: r["O"] and r["B"],
    }
    for g, fn in groups.items():
        sel = [r for r in rows if fn(r)]
        d = dict(n=len(sel))
        for h in T.HORIZONS:
            v = [r["fwd"][h] for r in sel if r["fwd"][h] is not None]
            d["med%d" % h] = float(np.median(v)) if v else None
            d["mean%d" % h] = float(np.mean(v)) if v else None
            d["n%d" % h] = len(v)
        ll = [r["ll"] for r in sel if r["ll"] is not None]
        d["ll_n"], d["ll_yes"] = len(ll), int(sum(ll))
        d["ll_share"] = (sum(ll) / len(ll)) if ll else None
        d["censored"] = len(sel) - len(ll)
        out[g] = d
    return out


def lows_md(tab):
    s = "| Group | n | med 1d | med 3d | med 7d | mean 7d | lower-low share <=26w (n eligible) | censored |\n|---|---|---|---|---|---|---|---|\n"
    for g, d in tab.items():
        s += "| %s | %d | %s | %s | %s | %s | %s (%d) | %d |\n" % (
            g, d["n"], pct(d["med1"]), pct(d["med3"]), pct(d["med7"]), pct(d["mean7"]), pct(d["ll_share"]), d["ll_n"], d["censored"])
    return s


def year_flag(evs):
    if not evs:
        return False
    ys = pd.Series([pd.Timestamp(e["ts"], unit="ms").year for e in evs]).value_counts()
    return bool(ys.iloc[0] / len(evs) > 0.85)


def cell(evs, h, split, pools, do_placebo=True):
    sel = [e for e in evs if T.L.in_split(e["ts"], split)] if split != "ALL" else list(evs)
    d = dict(n=len(sel), underpowered=len(sel) < 30)
    if not sel:
        return d
    r12 = np.array([T.R_of(e["gross"], e["r"], T.FEES["12"]) for e in sel])
    r6 = np.array([T.R_of(e["gross"], e["r"], T.FEES["6"]) for e in sel])
    lo, hi = T.block_ci([e["ts"] for e in sel], r12, h)
    d.update(win=float(np.mean([e["gross"] - T.FEES["12"] > 0 for e in sel])), R12=float(r12.mean()), R6=float(r6.mean()),
             ci_lo=float(lo), ci_hi=float(hi), one_year=year_flag(sel), gross_mean=float(np.mean([e["gross"] for e in sel])))
    if do_placebo:
        for name, ll in (("any", False), ("lowslike", True)):
            dr, skip = T.placebo(pools, sel, split, h, T.FEES["12"], ll, NDRAW)
            if len(dr):
                d[name] = dict(lo=float(np.percentile(dr, 2.5)), hi=float(np.percentile(dr, 97.5)), mean=float(dr.mean()),
                               pct=float((dr <= r12.mean()).mean() * 100), skipped=skip)
            dr6, _ = T.placebo(pools, sel, split, h, T.FEES["6"], ll, NDRAW)
            if len(dr6):
                d.setdefault(name, {})["pct6"] = float((dr6 <= r6.mean()).mean() * 100)
    return d


def cell_md(name, d):
    if d["n"] == 0:
        return "| %s | 0 | | | | | | |\n" % name
    pl = lambda k: ("%.1f%% (band %s..%s)" % (d[k]["pct"], f3(d[k]["lo"]), f3(d[k]["hi"]))) if k in d and "pct" in d[k] else "n/a"
    return "| %s | %d%s | %s | %s | %s | [%s, %s] | %s | %s |\n" % (
        name, d["n"], " (underpowered)" if d["underpowered"] else "", pct(d["win"]), f3(d["R12"]), f3(d["R6"]),
        f3(d["ci_lo"]), f3(d["ci_hi"]), pl("any"), pl("lowslike"))


def main():
    data = {}
    for c in UNIVERSE:
        d = T.load(c)
        if d is not None:
            data[c] = d
    cov = []
    for c in UNIVERSE:
        if c not in data:
            cov.append("| %s | no Bybit data | | |" % c)
            continue
        d = data[c]
        cov.append("| %s | %s | %d | %s |" % (c, pd.Timestamp(d["oi_start"], unit="ms").date(), len(d["c"]), pd.Timestamp(int(d["ts"][-1]), unit="ms").date()))

    # ---- Step 1a: lows
    rows = []
    for c, d in data.items():
        n = len(d["c"])
        sg = {x["u"]: x for x in T.signatures(d["l"], d["c"], d["fund"], d["oi"])}
        for i in T.lows(d["h"], d["l"], d["fund"], d["oi"]):
            F = bool(d["fund"][i] < 0)
            O = bool(d["oi"][i] / d["oi"][i - T.OI_LAG] - 1 <= T.OI_DROP)
            B = i in sg
            fwd = {h: (float(d["c"][i + h] / d["c"][i] - 1) if i + h < n else None) for h in T.HORIZONS}
            if i + T.LL_DAYS <= n - 1:
                ll = bool((d["l"][i + 1:i + T.LL_DAYS + 1] < T.LL_PCT * d["l"][i]).any())
            else:
                ll = None
            rows.append(dict(coin=c, i=i, ts=int(d["ts"][i]), F=F, O=O, B=B, fwd=fwd, ll=ll))
    tab_all = lows_table(rows)
    tab_btc = lows_table([r for r in rows if r["coin"] == "BTC"])
    sig_rows = [r for r in rows if r["F"] and r["O"] and r["B"]]
    non = [r for r in rows if not (r["F"] and r["O"] and r["B"])]
    a = [r["ll"] for r in sig_rows if r["ll"] is not None]
    b = [r["ll"] for r in non if r["ll"] is not None]
    fp = fisher(sum(a), len(a) - sum(a), sum(b), len(b) - sum(b)) if a and b else None
    n_sig_lows = len(sig_rows)

    # ---- Step 1b: causal signature events
    pools = {c: T.PlaceboPool(d) for c, d in data.items()}
    ev = {h: [] for h in T.HORIZONS}
    dropped = {h: 0 for h in T.HORIZONS}
    for c, d in data.items():
        for h in T.HORIZONS:
            e, dr = T.build_events(d, h)
            ev[h] += e
            dropped[h] += dr
    # unstopped forward return Close[s+h] / Open[s+1] for the h=7 kept set (descriptive)
    ev7 = ev[7]
    fwd_rows = []
    for e in ev7:
        d = data[e["coin"]]
        fr = {h: (float(d["c"][e["s"] + h] / d["o"][e["e"]] - 1) if e["s"] + h < len(d["c"]) else None) for h in T.HORIZONS}
        fwd_rows.append(fr)
    fwd_stats = {}
    for h in T.HORIZONS:
        v = np.array([f[h] for f in fwd_rows if f[h] is not None])
        fwd_stats[h] = dict(n=int(len(v)), median=float(np.median(v)) if len(v) else None, mean=float(v.mean()) if len(v) else None,
                            win=float((v - 0.0012 > 0).mean()) if len(v) else None, med_net12=float(np.median(v) - 0.0012) if len(v) else None)
    mix = {}
    for sp in ("DEV", "VAL", "ALL"):
        sel = [e for e in ev7 if sp == "ALL" or T.L.in_split(e["ts"], sp)]
        mix[sp] = {p: sum(1 for e in sel if e["phase"] == p) for p in PHASES}
        mix[sp]["n"] = len(sel)
        mix[sp]["one_year"] = year_flag(sel)
    years = pd.Series([pd.Timestamp(e["ts"], unit="ms").year for e in ev7]).value_counts().sort_index().to_dict()

    # ---- today's reading (never a sample)
    reading = "BTC data missing"
    if "BTC" in data:
        d = data["BTC"]
        k = len(d["c"]) - 1
        oi_hist = d["oi"][max(0, k - 365):k]
        oi_hist = oi_hist[~np.isnan(oi_hist)]
        pr = float((oi_hist < d["oi"][k]).mean() * 100) if len(oi_hist) and not np.isnan(d["oi"][k]) else float("nan")
        ch = d["oi"][k] / d["oi"][k - T.OI_LAG] - 1 if not np.isnan(d["oi"][k]) else float("nan")
        reading = "BTC last closed day %s: funding mean %.5f (%s), OI %.1f%% over 7d, OI at the %.1fth percentile of the prior 365 days" % (
            pd.Timestamp(int(d["ts"][k]), unit="ms").date(), d["fund"][k], "negative" if d["fund"][k] < 0 else "positive",
            ch * 100, pr)

    S = dict(coverage=cov, lows_all=tab_all, lows_btc=tab_btc, n_lows=len(rows), n_sig_lows=n_sig_lows, fisher_p=fp,
             fwd_stats=fwd_stats, mix=mix, years={int(k): int(v) for k, v in years.items()}, dropped=dropped,
             n_events={h: len(ev[h]) for h in T.HORIZONS}, reading=reading)

    md = ["# REPORT: Test 4, capitulation signature at lows (%s)\n" % pd.Timestamp.utcnow().date(),
          "Rules frozen in `PRE_REG.md` (committed before this run). Data: Binance spot daily + Bybit funding and 1d OI (public), host cache outside the repo. Rules are OURS unless marked SOURCED in the PRE_REG. Not a trade instruction.\n"]
    md.append("## Coverage\n| Coin | OI first stamp | daily bars | last closed bar |\n|---|---|---|---|\n" + "\n".join(cov) + "\n")
    md.append("## Step 1a: lows (ex-post labelled, descriptive)\nLows population = k=10 swing lows after a >=25%% fall from the 120-day high with funding and OI available: **%d lows, %d meet the full signature** (gate for Step 2 is >= 6).\n" % (len(rows), n_sig_lows))
    md.append("All coins pooled:\n\n" + lows_md(tab_all))
    md.append("BTC alone:\n\n" + lows_md(tab_btc))
    md.append("Lower-low share SIG %s (n %d) vs NOT-SIG %s (n %d); Fisher exact p = %s. Forward returns are from Close[L], where L is the ex-post low (not tradable; anatomy only). Partial-flag groups overlap.\n" % (
        pct(tab_all["SIG (F+O+B)"]["ll_share"]), tab_all["SIG (F+O+B)"]["ll_n"], pct(tab_all["NOT-SIG"]["ll_share"]), tab_all["NOT-SIG"]["ll_n"], f3(fp) if fp is not None else "n/a"))
    md.append("## Step 1b: causal signature events (all days, lockout 10 bars)\nEvents kept at hold 1 / 3 / 7: %d / %d / %d (dropped entry<=stop: %s). Year spread of the 7-day set: %s.\n" % (
        len(ev[1]), len(ev[3]), len(ev[7]), dropped, S["years"]))
    md.append("Unstopped forward return from Open[s+1] to Close[s+h] (7-day kept set; descriptive):\n\n| h | n | median | mean | win % net 12 bp | median net 12 bp |\n|---|---|---|---|---|---|\n" +
              "".join("| %dd | %d | %s | %s | %s | %s |\n" % (h, v["n"], pct(v["median"]), pct(v["mean"]), pct(v["win"]), pct(v["med_net12"])) for h, v in fwd_stats.items()))
    md.append("Regime mix (events per phase, 7-day set):\n\n| Split | n | " + " | ".join(PHASES) + " | ONE-YEAR |\n|---|---|" + "---|" * (len(PHASES) + 1) + "\n" +
              "".join("| %s | %d | %s | %s |\n" % (sp, m["n"], " | ".join(str(m[p]) for p in PHASES), "yes" if m["one_year"] else "no") for sp, m in mix.items()))
    md.append("Today's state (reading only, never a sample): %s.\n" % reading)

    verdict = "DESCRIPTIVE ONLY (Step 2 not run: %d signature lows < 6)" % n_sig_lows
    S["step2"] = None
    if n_sig_lows >= 6:
        step2 = {}
        md.append("## Step 2: fee-net trades of the causal signature (long, stop = failed-breakdown low - max(0.6 ATR, 0.5%%))\nColumns: n, win %% at 12 bp, mean R 12 bp, mean R 6 bp, block-bootstrap 95%% CI (12 bp), placebo percentile and band (12 bp; any day in the same phase / lows-like days in the same phase). Placebo %d draws, seed 1114. The placebo pool is restricted to days from the coin's first OI stamp + 7 days, where the signature can exist.\n" % NDRAW)
        for h in T.HORIZONS:
            step2[h] = {sp: cell(ev[h], h, sp, pools) for sp in SPLITS}
            md.append("### hold %d day%s%s\n| Split | n | win | R 12bp | R 6bp | CI 12bp | placebo any-day | placebo lows-like |\n|---|---|---|---|---|---|---|---|\n" % (h, "s" if h > 1 else "", " (PRIMARY)" if h == 7 else " (descriptive)") +
                      "".join(cell_md(sp, step2[h][sp]) for sp in SPLITS))
        # per phase and per coin, h=7, no placebo (descriptive)
        pp = "### hold 7, per phase (descriptive, no placebo)\n| Phase | split | n | win | R 12bp | R 6bp | CI |\n|---|---|---|---|---|---|---|\n"
        for p in PHASES:
            for sp in ("DEV", "VAL"):
                sel = [e for e in ev[7] if e["phase"] == p and T.L.in_split(e["ts"], sp)]
                c = cell(sel, 7, "ALL", pools, do_placebo=False)
                pp += "| %s | %s | %d%s | %s | %s | %s | [%s, %s] |\n" % (p, sp, c["n"], " (underpowered)" if c["n"] < 30 else "", pct(c.get("win")), f3(c.get("R12")), f3(c.get("R6")), f3(c.get("ci_lo")), f3(c.get("ci_hi"))) if c["n"] else "| %s | %s | 0 | | | | |\n" % (p, sp)
        md.append(pp)
        pc = "### hold 7, per coin, all splits (descriptive)\n| Coin | n | win | R 12bp |\n|---|---|---|---|\n"
        for cn in data:
            c = cell([e for e in ev[7] if e["coin"] == cn], 7, "ALL", pools, do_placebo=False)
            if c["n"]:
                pc += "| %s | %d | %s | %s |\n" % (cn, c["n"], pct(c["win"]), f3(c["R12"]))
        md.append(pc)
        v, dv = step2[7]["VAL"], step2[7]["DEV"]
        S["step2"] = {str(h): step2[h] for h in T.HORIZONS}
        if v["n"] < 30:
            verdict = "UNDERPOWERED: VAL pooled n = %d < 30, no claim (VAL mean R 12 bp %s, CI [%s, %s]; DEV n = %d, mean R %s)" % (
                v["n"], f3(v.get("R12")), f3(v.get("ci_lo")), f3(v.get("ci_hi")), dv["n"], f3(dv.get("R12")))
        else:
            beats = all(k in v and "pct" in v[k] and v["R12"] > v[k]["hi"] for k in ("any", "lowslike"))
            ok = v["R12"] > 0 and v["ci_lo"] > 0 and beats and dv["n"] > 0 and dv["R12"] > 0 and not v["one_year"]
            verdict = ("PASS" if ok else "KILL") + ": VAL h=7 12 bp mean R %s, CI [%s, %s], placebo any-day percentile %s, lows-like percentile %s, n = %d; DEV mean R %s (n %d)" % (
                f3(v["R12"]), f3(v["ci_lo"]), f3(v["ci_hi"]), "%.1f" % v["any"]["pct"] if "any" in v else "n/a",
                "%.1f" % v["lowslike"]["pct"] if "lowslike" in v else "n/a", v["n"], f3(dv.get("R12")), dv["n"])
    S["verdict"] = verdict
    md.insert(1, "**Verdict: %s.**\n" % verdict)
    open(os.path.join(HERE, "REPORT.md"), "w", encoding="utf-8").write("\n".join(md))
    json.dump(S, open(os.path.join(HERE, "summary.json"), "w"), indent=1, default=str)
    print(verdict)


if __name__ == "__main__":
    main()
