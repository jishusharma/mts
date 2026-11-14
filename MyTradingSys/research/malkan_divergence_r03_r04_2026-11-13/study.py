"""Malkan MAL-R03/R04 divergence, 20 coins pooled, 1h+4h. Runs the 24 cells frozen in PRE_REG.md; writes cells.csv, summary.json, RESULT.md.
Usage: python study.py [--draws 200]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from MyTradingSys.backtest import fees  # noqa: E402
from MyTradingSys.backtest import research_kit as rk  # noqa: E402
from MyTradingSys.backtest.layers.rsi.rsi_divergence import rsi_divergence  # noqa: E402
import mal_div_lib as L  # noqa: E402

DATA = REPO / "runtime_data" / "edge4-malkan-divergence-1113"
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX", "DOT", "TRX", "ATOM", "NEAR", "UNI", "ETC", "BCH", "FIL", "AAVE", "XLM"]
DAY = 86400000
COST = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13
VAL_START = 1704067200000  # 2024-01-01 UTC
RECENT_START = 1751328000000  # 2025-07-01 UTC
EXITS = [("1R", "tgt", 1.0), ("2R", "tgt", 2.0), ("T12", "time", 0.0)]
TFS = (1, 4)
WS = (12, 18)
KINDS = (("R03", "bearish"), ("R04", "bullish"))


def load(sym, now_ms):
    rows = {int(r[0]): r for r in json.load(open(DATA / ("%s_60.json" % sym)))}
    ks = sorted(k for k in rows if k + L.HOUR <= now_ms)  # closed bars only
    a = np.array([rows[k][:5] for k in ks], float)
    return a[:, 0].astype(np.int64), a[:, 1], a[:, 2], a[:, 3], a[:, 4]


def week_key(t):
    return (t // DAY + 3) // 7


def btc_regime_weeks(btc):
    d = L.fold(*btc, 24)
    c = d["c"]
    sma = np.full(len(c), np.nan)
    cs = np.cumsum(np.insert(c, 0, 0.0))
    sma[199:] = (cs[200:] - cs[:-200]) / 200
    wk = week_key(d["t"])
    tags = {}
    for i in range(len(c)):
        w = wk[i]
        if np.isnan(sma[i]):
            tags[w] = None
        else:
            tags[w] = "bull" if c[i] > 1.05 * sma[i] else ("bear" if c[i] < 0.95 * sma[i] else "range")
    return tags


def mix_line(tags, t0, t1):
    ws = sorted(w for w in tags if t0 <= w * 7 * DAY - 3 * DAY < t1)
    return rk.regime_mix_line([tags[w] for w in ws])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=200)
    a = ap.parse_args()
    now_ms = int(time.time() * 1000)
    raw = {c: load(c, now_ms) for c in COINS}
    data_end = max(int(r[0][-1]) for r in raw.values()) + L.HOUR
    out_cells, summary = [], {"cost_rt": COST, "coins": {}, "data_end_utc": time.strftime("%Y-%m-%d %H:%M", time.gmtime(data_end / 1000))}
    for c in COINS:
        summary["coins"][c] = [time.strftime("%Y-%m-%d", time.gmtime(raw[c][0][0] / 1000)), int(len(raw[c][0]))]
    tags = btc_regime_weeks(raw["BTC"])
    rng = np.random.default_rng(11)
    trades = {}  # (tf) -> global arrays + per-(side,W) trades
    cellrows = []
    for tf in TFS:
        # global concatenated arrays for placebo pool
        G = dict(o=[], h=[], l=[], c=[], t=[], coin=[], ok=[])
        per_coin = {}
        for ci, coin in enumerate(COINS):
            b = L.fold(*raw[coin], tf)
            rsi = L.wilder_rsi(b["c"])
            per_coin[coin] = (b, rsi, len(b["t"]) and sum(len(x) for x in G["t"]))
            for k in ("o", "h", "l", "c", "t"):
                G[k].append(b[k])
            G["coin"].append(np.full(len(b["t"]), ci))
            G["ok"].append(L.fwd_ok(b["t"], tf))
        G = {k: np.concatenate(v) for k, v in G.items()}
        wkey = week_key(G["t"]) + 100000 * G["coin"]
        valid = np.where(G["ok"])[0]
        order = valid[np.argsort(wkey[valid], kind="stable")]
        okeys = wkey[order]
        for rule, kind in KINDS:
            for w in WS:
                tr = dict(idx=[], entry=[], stop=[], coin=[])
                for ci, coin in enumerate(COINS):
                    b, rsi, off = per_coin[coin]
                    r = L.build_trades(b, rsi, kind, w, tf, rsi_divergence)
                    keep = L.fwd_ok(b["t"], tf)[r["idx"]] if len(r["idx"]) else np.array([], bool)
                    tr["idx"].append(r["idx"][keep] + off)
                    tr["entry"].append(r["entry"][keep])
                    tr["stop"].append(r["stop"][keep])
                    tr["coin"].append(np.full(int(keep.sum()), ci))
                tr = {k: np.concatenate(v) for k, v in tr.items()}
                side = -1 if kind == "bearish" else 1
                te = G["t"][tr["idx"]] + tf * L.HOUR  # entry bar close time
                sd = np.abs(tr["entry"] - tr["stop"]) / tr["entry"]
                O, Hh, Ll, C = (L.fwd_window(G[k], tr["idx"]) for k in ("o", "h", "l", "c"))
                for en, ek, kk in EXITS:
                    R = L.fwd_exit(side, tr["entry"], tr["stop"], O, Hh, Ll, C, ek, kk, COST)
                    dev, val, rec = te < VAL_START, te >= VAL_START, te >= RECENT_START
                    # placebo for VAL trades
                    vi = np.where(val)[0]
                    pm = np.full(a.draws, np.nan)
                    if len(vi):
                        wk_t = wkey[tr["idx"][vi]]
                        lo = np.searchsorted(okeys, wk_t, "left")
                        hi = np.searchsorted(okeys, wk_t, "right")
                        okp = hi > lo
                        vi2, lo, ln = vi[okp], lo[okp], (hi - lo)[okp]
                        for d in range(a.draws):
                            j = order[lo + (rng.random(len(vi2)) * ln).astype(int)]
                            ent = G["c"][j]
                            stp = L.placebo_stop(side, ent, sd[vi2])
                            pO, pH, pL, pC = (L.fwd_window(G[k], j) for k in ("o", "h", "l", "c"))
                            pm[d] = L.fwd_exit(side, ent, stp, pO, pH, pL, pC, ek, kk, COST).mean()
                    row = dict(cell="%s_%dh_W%d_%s" % (rule, tf, w, en), rule=rule, tf=tf, w=w, exit=en,
                               n_dev=int(dev.sum()), mean_dev=float(R[dev].mean()) if dev.any() else None,
                               n_val=int(val.sum()), n_rec=int(rec.sum()), mean_rec=float(R[rec].mean()) if rec.any() else None,
                               days_val=int(len(np.unique(te[val] // DAY))), median_stopdist_pct=float(np.median(sd) * 100) if len(sd) else None)
                    if val.sum() >= 2:
                        m, lo_c, hi_c, p_c = L.boot_cluster(R[val], te[val] // DAY)
                        _, lo_i, hi_i, p_i = L.boot_cluster(R[val], np.arange(val.sum()))
                        pv = pm[~np.isnan(pm)]
                        row.update(mean_val=m, ci_cl=[lo_c, hi_c], p_cl=p_c, ci_iid=[lo_i, hi_i], p_iid=p_i,
                                   win_val=float((R[val] > 0).mean()),
                                   placebo_mean=float(pv.mean()) if len(pv) else None,
                                   placebo_p=float((pv >= m).mean()) if len(pv) else None)
                        hrs = (te[val] // L.HOUR) % 24
                        row["hour_blocks_meanR"] = {nm: (float(R[val][(hrs >= s) & (hrs < s + 8)].mean()) if ((hrs >= s) & (hrs < s + 8)).any() else None)
                                                    for nm, s in (("00-08", 0), ("08-16", 8), ("16-24", 16))}
                    cellrows.append(row)
                print(rule, tf, w, "n", len(tr["idx"]), "val", int((te >= VAL_START).sum()), flush=True)
    ps = np.array([r.get("p_cl", 1.0) for r in cellrows])
    sig = L.bh(ps)
    for r, s in zip(cellrows, sig):
        r["bh"] = bool(s)
        if r["n_val"] < 30:
            r["verdict"] = "UNDERPOWERED"
        else:
            ok = (r["mean_val"] > 0 and r["ci_cl"][0] > 0 and r["placebo_p"] is not None and r["placebo_p"] <= 0.05 and r["bh"])
            r["verdict"] = "PASS" if ok else "FAIL"
    summary["cells"] = cellrows
    summary["regime_mix"] = {"DEV": mix_line(tags, 0, VAL_START), "VALIDATION": mix_line(tags, VAL_START, data_end),
                             "RECENT": mix_line(tags, RECENT_START, data_end)}
    json.dump(summary, open(HERE / "summary.json", "w"), indent=1)
    write_result(summary)


def write_result(s):
    cells = s["cells"]
    npass = sum(1 for r in cells if r["verdict"] == "PASS")
    best = sorted([r for r in cells if "mean_val" in r], key=lambda r: -r["mean_val"])[:3]
    L_ = []
    L_.append("Regime mix: VALIDATION %s (BTC weekly close vs 200d SMA +-5 %%)" % s["regime_mix"]["VALIDATION"])
    L_.append("")
    L_.append("Verdict: %s. %d of 24 cells PASS (VALIDATION fee-net mean R > 0, day-clustered CI lower > 0, n >= 30, placebo p <= 0.05, BH 10 %%)."
              % ("PASS (lead)" if npass else "FAIL / no edge", npass))
    L_.append("")
    L_.append("Regime mix DEV: %s | RECENT: %s" % (s["regime_mix"]["DEV"], s["regime_mix"]["RECENT"]))
    L_.append("Costs: 2 x BINANCE_TAKER + SLIPPAGE_RT_S13 = %.2f bp round trip, charged on entry, converted to R. Data end %s UTC. 20 Bybit USDT perps, 1h; 4h folded." % (s["cost_rt"] * 1e4, s["data_end_utc"]))
    L_.append("")
    L_.append("| cell | n DEV | n VAL | mean R VAL | CI (day-cluster) | CI (per-trade) | placebo (mean, p) | BH | verdict |")
    L_.append("|---|---|---|---|---|---|---|---|---|")
    for r in cells:
        if "mean_val" in r:
            L_.append("| %s | %d | %d | %+.3f | [%+.3f, %+.3f] | [%+.3f, %+.3f] | %s, %s | %s | %s |" % (
                r["cell"], r["n_dev"], r["n_val"], r["mean_val"], r["ci_cl"][0], r["ci_cl"][1], r["ci_iid"][0], r["ci_iid"][1],
                "%+.3f" % r["placebo_mean"] if r["placebo_mean"] is not None else "n/a",
                "%.3f" % r["placebo_p"] if r["placebo_p"] is not None else "n/a", "yes" if r["bh"] else "no", r["verdict"]))
        else:
            L_.append("| %s | %d | %d | n/a | n/a | n/a | n/a | n/a | %s |" % (r["cell"], r["n_dev"], r["n_val"], r["verdict"]))
    L_.append("")
    L_.append("DEV mean R and RECENT (>= 2025-07-01) are descriptive only (cells.csv). Best 3 by VALIDATION mean R: " + "; ".join(
        "%s %+.3f (n %d, cluster CI lower %+.3f, placebo p %s)" % (r["cell"], r["mean_val"], r["n_val"], r["ci_cl"][0], r["placebo_p"]) for r in best))
    L_.append("")
    L_.append("Not a deployable PASS even if a row says PASS: needs a causal replay test and an independent trade-loop re-run first (CLAUDE.md). "
              "Coverage: " + ", ".join("%s from %s" % (c, v[0]) for c, v in s["coins"].items()))
    (HERE / "RESULT.md").write_text("\n".join(L_) + "\n", encoding="utf-8")
    import csv
    with open(HERE / "cells.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "n_dev", "mean_dev", "n_val", "mean_val", "ci_cl_lo", "ci_cl_hi", "ci_iid_lo", "ci_iid_hi", "p_cl", "placebo_mean", "placebo_p", "win_val", "days_val", "n_rec", "mean_rec", "median_stopdist_pct", "bh", "verdict", "hour_blocks_meanR"])
        for r in cells:
            g = lambda k: r.get(k)  # noqa: E731
            w.writerow([r["cell"], r["n_dev"], g("mean_dev"), r["n_val"], g("mean_val"), (g("ci_cl") or [None, None])[0], (g("ci_cl") or [None, None])[1],
                        (g("ci_iid") or [None, None])[0], (g("ci_iid") or [None, None])[1], g("p_cl"), g("placebo_mean"), g("placebo_p"), g("win_val"),
                        r["days_val"], r["n_rec"], g("mean_rec"), g("median_stopdist_pct"), r["bh"], r["verdict"], json.dumps(g("hour_blocks_meanR"))])


if __name__ == "__main__":
    main()
