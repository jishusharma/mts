"""Run Test 5 exactly as frozen in PRE_REG.md. Reads host caches (not in the repo); writes REPORT.md and summary.json here."""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "buyzone_test1_ladder_2026-11-14"))
import flow as W
import ladder as L

FLOW = os.environ.get("MTS_FLOW_CACHE", "C:/Users/e-ngineers/mts_cache/buyzone_test5")
PRICE = os.environ.get("MTS_DATA_CACHE", "C:/Users/e-ngineers/MTS_data_cache") + "/binance_spot_1d/BTCUSDT.json"
START = "2023-01-01"
PH = ["UP", "BASE", "RANGE", "DOWN", "POSTPEAK_BEAR"]
FEATS = [("ALL1M", "ALL", "1"), ("ALL5M", "ALL", "5"), ("SPOT1M", "SPOT", "1"), ("FUT1M", "FUT", "1"),
         ("SPOT5M", "SPOT", "5"), ("FUT5M", "FUT", "5")]


def build():
    k = json.load(open(PRICE))[:-1]                  # last (possibly partial) bar dropped
    ts = np.array([r[0] for r in k], dtype=np.int64)
    o, h, l, c = (np.array([r[i] for r in k], float) for i in (1, 2, 3, 4))
    ph = L.phases(h, l, c)
    spot = W.load_flow_dir(os.path.join(FLOW, "spot"))
    fut = W.load_flow_dir(os.path.join(FLOW, "fut"))
    cb = json.load(open(os.path.join(FLOW, "coinbase_1d.json")))
    date = pd.to_datetime(ts, unit="ms").strftime("%Y-%m-%d")
    n = len(ts)
    rows = {"ts": [], "phase": [], "ret24": [], "ret72": [], "retcon": [], "prem": [], "daynum": []}
    for f, _, _ in FEATS:
        rows[f] = []
    dropped = {"no_flow": 0, "no_phase": 0, "no_ret24": 0}
    for i in range(1, n):
        d = date[i]
        if d < START:
            continue
        sp, fu = spot.get(d), fut.get(d)
        if sp is None or fu is None:
            dropped["no_flow"] += 1
            continue
        if ph[i] == "":
            dropped["no_phase"] += 1
            continue
        if i + 1 >= n or ts[i + 1] != ts[i] + W.DAY:
            dropped["no_ret24"] += 1
            continue
        rows["ts"].append(int(ts[i]))
        rows["daynum"].append(int(ts[i] // W.DAY))
        rows["phase"].append(ph[i])
        rows["ret24"].append(c[i + 1] / c[i] - 1)
        rows["ret72"].append(c[i + 3] / c[i] - 1 if i + 3 < n and ts[i + 3] == ts[i] + 3 * W.DAY else np.nan)
        rows["retcon"].append(c[i] / c[i - 1] - 1)
        rows["prem"].append(1e4 * (cb[d] / c[i] - 1) if d in cb else np.nan)
        for f, v, kk in FEATS:
            rows[f].append(W.net_flow_bp(sp, fu, kk, v))
    out = {k2: np.array(v) for k2, v in rows.items()}
    out["ts"] = out["ts"].astype(np.int64)
    out["_dropped"] = dropped
    out["_first"] = date[np.searchsorted(ts, out["ts"][0])]
    out["_last"] = pd.to_datetime(out["ts"][-1], unit="ms").strftime("%Y-%m-%d")
    return out


def cell(D, feat, ret_key, mask, edges, heavy):
    F = D[feat][mask]
    r = D[ret_key][mask]
    st = W.spread_stats(F, r, edges)
    res = {"n": st["n"], "cnt": st["cnt"].tolist(), "mean_bp": (st["mean"] * 1e4).round(2).tolist(),
           "spread_bp": round(float(st["spread"]) * 1e4, 2) if st["n"] else None, "underpowered": st["underpowered"],
           "spearman": W.spearman(F, r)}
    for nm, fee in W.FEES.items():
        res["fee" + nm] = {a: round(float(b), 2) for a, b in W.fee_rows(st, fee).items()} if not st["underpowered"] else None
    if heavy and not st["underpowered"]:
        lo, hi = W.block_ci(D["ts"][mask], F, r, edges)
        dr = W.shuffle_placebo(F, r, D["phase"][mask], edges)
        res["ci_bp"] = [round(float(lo) * 1e4, 2), round(float(hi) * 1e4, 2)]
        res["placebo_bp"] = [round(float(np.nanpercentile(dr, 2.5)) * 1e4, 2), round(float(np.nanpercentile(dr, 97.5)) * 1e4, 2)]
        res["placebo_pct"] = round(W.pct_of(st["spread"], dr), 1)
    return res


def run():
    D = build()
    dev = W.split_mask(D["ts"], "DEV")
    spl = {s: W.split_mask(D["ts"], s) for s in ("DEV", "VAL", "RECENT")}
    out = {"first_day": D["_first"], "last_day": D["_last"], "n_days": int(len(D["ts"])), "dropped": D["_dropped"], "cells": {}, "mix": {}, "edges": {}}
    for s, m in spl.items():
        yrs = pd.to_datetime(D["ts"][m], unit="ms").year
        out["mix"][s] = {"n": int(m.sum()), **{p: int((D["phase"][m] == p).sum()) for p in PH},
                         "max_year_share": round(float(pd.Series(yrs).value_counts(normalize=True).max()), 3)}
    feats = [f for f, _, _ in FEATS] + ["PREM"]
    D["PREM"] = D["prem"]
    for f in feats:
        edges = W.quintile_edges(D[f][dev & ~np.isnan(D["ret24"])])
        out["edges"][f] = [round(float(e), 2) for e in edges]
        primary = f in ("ALL1M", "ALL5M")
        for hz, key in (("24", "ret24"), ("72o0", "ret72"), ("72o1", "ret72"), ("72o2", "ret72"), ("con", "retcon")):
            hm = np.ones(len(D["ts"]), bool)
            if hz.startswith("72"):
                hm = (D["daynum"] % 3 == int(hz[-1]))
            for s, sm in spl.items():
                for ph in ["ALL"] + PH:
                    pm = np.ones(len(D["ts"]), bool) if ph == "ALL" else (D["phase"] == ph)
                    mask = sm & pm & hm & ~np.isnan(D[key])
                    heavy = (hz in ("24", "72o0")) and (primary or ph == "ALL") and mask.sum() >= 40
                    out["cells"]["|".join([f, hz, s, ph])] = cell(D, f, key, mask, edges, heavy)
    return out


def verdict(out):
    v = {}
    for f in ("ALL1M", "ALL5M"):
        va = out["cells"][f + "|24|VAL|ALL"]
        de = out["cells"][f + "|24|DEV|ALL"]
        v[f] = {"val_spread_bp": va["spread_bp"], "val_ci_bp": [float(x) for x in va["ci_bp"]] if va.get("ci_bp") else None, "val_placebo_pct": va.get("placebo_pct"),
                "val_placebo_band_bp": va.get("placebo_bp"), "val_n": va["n"], "dev_spread_bp": de["spread_bp"], "dev_n": de["n"]}
        ok = (va.get("ci_bp") is not None and va["spread_bp"] > 0 and va["ci_bp"][0] > 0 and va["placebo_pct"] > 97.5
              and de["spread_bp"] is not None and de["spread_bp"] > 0)
        v[f]["pass"] = bool(ok)
    under = out["cells"]["ALL1M|24|VAL|ALL"]["n"] < 200 or out["cells"]["ALL1M|24|DEV|ALL"]["n"] < 300
    signs = {np.sign(v[f]["val_spread_bp"]) for f in v}
    out["verdict"] = ("UNDERPOWERED" if under else "PASS (LEAD ONLY)" if all(v[f]["pass"] for f in v)
                      else "KILL (MIXED)" if len(signs) > 1 else "KILL")
    out["verdict_detail"] = v


def fmt(x):
    return "" if x is None else str(x)


def report(out):
    c = out["cells"]
    L_ = ["# REPORT: Test 5, large-trade flow lead test, BTC", "",
          "Rules frozen in `PRE_REG.md` (committed before any outcome). Code `flow.py`, `run_test5.py`, `fetch_flow.py`, `fetch_cb.py`; tests `test_flow.py`. Data: Binance public aggTrades (spot + USD-M futures, BTCUSDT) reduced to large-trade sums, Binance spot 1d price, Coinbase BTC-USD 1d; host caches, never committed. A LEAD-signal test: no trade result is claimed, nothing here is a trade instruction.", ""]
    v = out["verdict_detail"]
    L_.append("**Verdict: %s.** Primary = all phases, VAL, next-24 h, top vs bottom flow quintile, both cutoffs." % out["verdict"])
    L_ += ["", "| cutoff | VAL n | VAL spread bp | 95% CI bp | shuffle band bp | shuffle pct | DEV n | DEV spread bp | pass |", "|---|---|---|---|---|---|---|---|---|"]
    for f in v:
        a = v[f]
        L_.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (f, a["val_n"], a["val_spread_bp"], a["val_ci_bp"], a["val_placebo_band_bp"], a["val_placebo_pct"], a["dev_n"], a["dev_spread_bp"], a["pass"]))
    L_ += ["", "## Coverage and regime mix", "",
           "Flow days used: %d, %s to %s. Dropped: %s. Regime mix: share of flow days per phase per split." % (out["n_days"], out["first_day"], out["last_day"], out["dropped"]), "",
           "| split | n | " + " | ".join(PH) + " | max one-year share |", "|---|---|" + "---|" * (len(PH) + 1)]
    for s, m in out["mix"].items():
        L_.append("| %s | %d | %s | %s |" % (s, m["n"], " | ".join("%.1f%%" % (100 * m[p] / max(m["n"], 1)) for p in PH), m["max_year_share"]))
    L_.append("")
    L_.append("Regime mix: DEV, VAL and RECENT shares above; a split with max one-year share above 0.85 is ONE-YEAR and cannot carry a PASS alone.")
    L_ += ["", "## Quintile table, next-24 h return (bp), all phases", "",
           "| feature | split | n | Q1 | Q2 | Q3 | Q4 | Q5 | spread bp | CI bp | shuffle pct | Spearman |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for f in ("ALL1M", "ALL5M", "SPOT1M", "FUT1M", "SPOT5M", "FUT5M", "PREM"):
        for s in ("DEV", "VAL", "RECENT"):
            x = c["|".join([f, "24", s, "ALL"])]
            L_.append("| %s | %s | %d | %s | %s | %s | %s |" % (f, s, x["n"], " | ".join(map(str, x["mean_bp"])), x["spread_bp"], fmt(x.get("ci_bp")), "%s | %.3f" % (fmt(x.get("placebo_pct")), x["spearman"])))
    L_ += ["", "## 72 h (stride 3, offsets 0/1/2 as replicates), all phases", "",
           "| feature | split | offset | n | spread bp | Spearman |", "|---|---|---|---|---|---|"]
    for f in ("ALL1M", "ALL5M"):
        for s in ("DEV", "VAL"):
            for o in (0, 1, 2):
                x = c["|".join([f, "72o%d" % o, s, "ALL"])]
                L_.append("| %s | %s | %d | %d | %s | %.3f |" % (f, s, o, x["n"], x["spread_bp"], x["spearman"]))
    L_ += ["", "## Concurrent check (Spearman of flow with the SAME day's return)", "", "| feature | DEV | VAL |", "|---|---|---|"]
    for f in ("ALL1M", "ALL5M"):
        L_.append("| %s | %.3f | %.3f |" % (f, c[f + "|con|DEV|ALL"]["spearman"], c[f + "|con|VAL|ALL"]["spearman"]))
    L_ += ["", "## Per phase, ALL1M, next-24 h, spread bp (n)", "", "| split | " + " | ".join(PH) + " |", "|---|" + "---|" * len(PH)]
    for s in ("DEV", "VAL", "RECENT"):
        L_.append("| %s | %s |" % (s, " | ".join("%s (%d)%s" % (c["|".join(["ALL1M", "24", s, p])]["spread_bp"], c["|".join(["ALL1M", "24", s, p])]["n"], " UNDERPOWERED" if c["|".join(["ALL1M", "24", s, p])]["underpowered"] else "") for p in PH)))
    L_ += ["", "## Fee-net rows (descriptive, bp per trade, next-24 h, all phases; no trade claimed)", "",
           "| feature | split | fee | long Q5 | short Q1 | two-leg spread (2 x fee) |", "|---|---|---|---|---|---|"]
    for f in ("ALL1M", "ALL5M"):
        for s in ("DEV", "VAL", "RECENT"):
            x = c["|".join([f, "24", s, "ALL"])]
            for nm in ("12", "6"):
                r = x["fee" + nm]
                L_.append("| %s | %s | %s bp | %s | %s | %s |" % (f, s, nm, r["long_q5"] if r else "", r["short_q1"] if r else "", r["two_leg"] if r else ""))
    L_ += ["", "Quintile edges (bp, from DEV): " + "; ".join("%s %s" % (k, e) for k, e in out["edges"].items()), "",
           "PREM = Coinbase BTC-USD close vs Binance BTCUSDT close, bp; mixes the USD-USDT basis with the premium. Binance futures aggTrades come from the public data dump; the brief's Bybit caveat concerns funding and OI, not used here."]
    return "\n".join(L_) + "\n"


if __name__ == "__main__":
    out = run()
    verdict(out)
    json.dump(out, open(os.path.join(HERE, "summary.json"), "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    open(os.path.join(HERE, "REPORT.md"), "w", encoding="utf8").write(report(out))
    print(out["verdict"], json.dumps(out["verdict_detail"], default=str))
