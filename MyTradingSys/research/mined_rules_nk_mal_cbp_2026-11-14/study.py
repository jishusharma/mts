"""Mined rules MAL-R05, NK-R04, NK-R05, NK-R11 on 20 Bybit perps. Runs the 9 cells frozen in PRE_REG.md; writes cells.csv, summary.json, RESULT.md.
Usage: python study.py [--draws 200] [--coins N]
"""
import argparse
import csv
import json
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
import rules_lib as R  # noqa: E402

DATA = REPO / "MyTradingSys" / "runtime_data" / "edge8-mined-rules-1114"
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX", "DOT", "TRX", "ATOM", "NEAR", "UNI", "ETC", "BCH", "FIL", "AAVE", "XLM"]
DAY = R.DAY
M15 = 15 * R.MIN
COST = 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13
VAL_START = 1704067200000  # 2024-01-01 UTC
HH = {"15m": 96, "D": 30}
BAR = {"15m": M15, "D": DAY}


def load(sym, iv, now_ms):
    rows = {int(r[0]): r for r in json.load(open(DATA / ("%s_%s.json" % (sym, iv))))}
    step = BAR["15m" if iv == "15" else "D"]
    ks = sorted(k for k in rows if k + step <= now_ms)  # closed bars only
    a = np.array([rows[k][:5] for k in ks], float)
    return a[:, 0].astype(np.int64), a[:, 1], a[:, 2], a[:, 3], a[:, 4]


def week_key(t):
    return (t // DAY + 3) // 7


def btc_regime_weeks(btc):
    t, o, h, l, c = btc
    sma = np.full(len(c), np.nan)
    cs = np.cumsum(np.insert(c, 0, 0.0))
    sma[199:] = (cs[200:] - cs[:-200]) / 200
    wk = week_key(t)
    tags = {}
    for i in range(len(c)):
        tags[wk[i]] = None if np.isnan(sma[i]) else ("bull" if c[i] > 1.05 * sma[i] else ("bear" if c[i] < 0.95 * sma[i] else "range"))
    return tags


def mix_line(tags, t0, t1):
    ws = sorted(w for w in tags if t0 <= w * 7 * DAY - 3 * DAY < t1)
    return rk.regime_mix_line([tags[w] for w in ws])


def build_group(raw, tfname):
    """Concatenate per-coin bars into global arrays; returns G with offsets and per-coin slices."""
    hh = HH[tfname]
    G = dict(t=[], o=[], h=[], l=[], c=[], coin=[], ok=[])
    off = {}
    n0 = 0
    for ci, coin in enumerate(COINS):
        if coin not in raw:
            continue
        t, o, h, l, c = raw[coin]
        off[coin] = n0
        n0 += len(t)
        for k, v in zip(("t", "o", "h", "l", "c"), (t, o, h, l, c)):
            G[k].append(v)
        G["coin"].append(np.full(len(t), ci))
        G["ok"].append(R.fwd_ok(t, BAR[tfname], hh))
    return {k: np.concatenate(v) for k, v in G.items()}, off


def trades_for(cell, raw, off, now_ms):
    """Per-cell trades as global arrays: e (entry bar), entry, stop, tp (or None), coin."""
    parts = dict(e=[], entry=[], stop=[], tp=[], coin=[])
    for coin in COINS:
        if coin not in raw:
            continue
        t, o, h, l, c = raw[coin]
        ci = COINS.index(coin)
        tp = None
        if cell["rule"] == "NK-R11":
            e, en, st = R.bb_entries(t, o, h, l, c, M15)
        elif cell["rule"] in ("NK-R04", "NK-R05"):
            rsi = R.wilder_rsi(c)
            sig = R.nk_signals(t, rsi, cell["side"], cell["window"])
            e, en, st = R.nk_entries(t, o, h, l, cell["side"], sig, M15)
        else:  # MAL-R05
            wk = R.fold_weeks(t, o, h, l, c)
            rsi_w = R.wilder_rsi(wk["c"])
            e, en, st, tp = R.mal_r05_entries(t, o, h, l, c, wk, rsi_w, "bearish" if cell["side"] == -1 else "bullish", cell["w"], rsi_divergence)
        ok = R.fwd_ok(t, BAR[cell["tf"]], HH[cell["tf"]])[e] if len(e) else np.array([], bool)
        parts["e"].append(e[ok] + off[coin])
        parts["entry"].append(en[ok])
        parts["stop"].append(st[ok])
        if tp is not None:
            parts["tp"].append(tp[ok])
        parts["coin"].append(np.full(int(ok.sum()), ci))
    out = {k: (np.concatenate(v) if v else np.array([])) for k, v in parts.items()}
    out["e"] = out["e"].astype(int)
    out["coin"] = out["coin"].astype(int)
    if not len(out["tp"]):
        out["tp"] = None
    return out


def walk_global(G, e, entry, stop, tp, side, trail, hh):
    O, Hh, Ll, C = (R.fwd_window(G[k], e, hh) for k in ("o", "h", "l", "c"))
    return R.fwd_walk(side, entry, stop, tp, O, Hh, Ll, C, trail, COST)


def evaluate(cell, G, tr, draws, rng):
    side, hh, trail = cell["side"], HH[cell["tf"]], cell["trail"]
    e, entry, stop, tp = tr["e"], tr["entry"], tr["stop"], tr["tp"]
    row = dict(cell=cell["cell"], rule=cell["rule"], tf=cell["tf"], side=side, n_all=int(len(e)))
    if not len(e):
        row.update(n_dev=0, n_val=0, verdict="UNDERPOWERED")
        return row
    r, hold, net = walk_global(G, e, entry, stop, tp, side, trail, hh)
    te = G["t"][e]
    dev, val = te < VAL_START, te >= VAL_START
    sd = np.abs(entry - stop) / entry
    row.update(n_dev=int(dev.sum()), n_val=int(val.sum()), mean_dev=float(r[dev].mean()) if dev.any() else None,
               win_val=float((r[val] > 0).mean()) if val.any() else None, hold_val=float(hold[val].mean()) if val.any() else None,
               median_stop_pct=float(np.median(sd[val]) * 100) if val.any() else None,
               mean_net_pct_val=float(net[val].mean() * 100) if val.any() else None,
               median_r_val=float(np.median(r[val])) if val.any() else None,
               days_val=int(len(np.unique(te[val] // DAY))))
    if val.sum() < 2:
        row["verdict"] = "UNDERPOWERED"
        return row
    rv, dv = r[val], te[val] // DAY
    m, lo_c, hi_c, p_c = R.boot_cluster(rv, dv)
    _, lo_i, hi_i, p_i = R.boot_cluster(rv, np.arange(len(rv)))
    # best 5 days removed
    ud, inv = np.unique(dv, return_inverse=True)
    ds = np.bincount(inv, weights=rv)
    drop = ud[np.argsort(-ds)[:5]]
    keep = ~np.isin(dv, drop)
    row.update(mean_val=m, ci_cl=[lo_c, hi_c], p_cl=p_c, ci_iid=[lo_i, hi_i], p_iid=p_i,
               mean_ex5=float(rv[keep].mean()) if keep.any() else None)
    hrs = (te[val] // R.HOUR) % 24
    row["hour_blocks_meanR"] = {nm: (float(rv[(hrs >= s) & (hrs < s + 8)].mean()) if ((hrs >= s) & (hrs < s + 8)).any() else None)
                                for nm, s in (("00-08", 0), ("08-16", 8), ("16-24", 16))}
    # placebo: same coin, same ISO week, same side, same stop (and target) fraction, same exit machinery
    wkey = week_key(G["t"]) + 1000000 * G["coin"]
    valid = np.where(G["ok"])[0]
    order = valid[np.argsort(wkey[valid], kind="stable")]
    okeys = wkey[order]
    vi = np.where(val)[0]
    wk_t = wkey[e[vi]]
    lo = np.searchsorted(okeys, wk_t, "left")
    hi = np.searchsorted(okeys, wk_t, "right")
    okp = hi > lo
    vi2, lo, ln = vi[okp], lo[okp], (hi - lo)[okp]
    tpfrac = None if tp is None else np.abs(tp[vi2] - entry[vi2]) / entry[vi2]
    pm = np.full(draws, np.nan)
    ph = np.full(draws, np.nan)
    for d in range(draws):
        j = order[lo + (rng.random(len(vi2)) * ln).astype(int)]
        ent = G["o"][j]
        stp = R.placebo_stop(side, ent, sd[vi2])
        tpp = None if tpfrac is None else ent * (1.0 + side * tpfrac)
        rr, hh_, _ = walk_global(G, j, ent, stp, tpp, side, trail, hh)
        pm[d], ph[d] = rr.mean(), hh_.mean()
    row.update(placebo_mean=float(pm.mean()), placebo_p=float((pm >= m).mean()), placebo_hold=float(ph.mean()),
               placebo_n=int(len(vi2)))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--coins", type=int, default=20)
    a = ap.parse_args()
    global COINS
    COINS = COINS[:a.coins]
    now_ms = int(time.time() * 1000)
    raw15 = {c: load(c, "15", now_ms) for c in COINS if (DATA / ("%s_15.json" % c)).exists()}
    rawD = {c: load(c, "D", now_ms) for c in COINS}
    G15, off15 = build_group(raw15, "15m")
    GD, offD = build_group(rawD, "D")
    cells = []
    for w in (12, 18):
        for side in (-1, 1):
            cells.append(dict(cell="MAL-R05_%s_W%d" % ("short" if side == -1 else "long", w), rule="MAL-R05", tf="D", side=side, w=w, trail=False))
    for rule, side in (("NK-R04", 1), ("NK-R05", -1)):
        for var, win in (("WIN", True), ("ALL", False)):
            cells.append(dict(cell="%s_%s" % (rule, var), rule=rule, tf="15m", side=side, window=win, trail=True))
    cells.append(dict(cell="NK-R11_BB", rule="NK-R11", tf="15m", side=1, trail=True))
    rng = np.random.default_rng(11)
    rows = []
    for cell in cells:
        t0 = time.time()
        G, off, raw = (GD, offD, rawD) if cell["tf"] == "D" else (G15, off15, raw15)
        tr = trades_for(cell, raw, off, now_ms)
        row = evaluate(cell, G, tr, a.draws, rng)
        rows.append(row)
        print(cell["cell"], "n_dev", row.get("n_dev"), "n_val", row.get("n_val"), "mean_val", row.get("mean_val"), "%.0fs" % (time.time() - t0), flush=True)
    sig = R.bh(np.array([r.get("p_cl", 1.0) for r in rows]))
    for r, s in zip(rows, sig):
        r["bh"] = bool(s)
        if r["n_val"] < 100:
            r["verdict"] = "UNDERPOWERED"
        else:
            ok = (r["mean_val"] > 0 and r["ci_cl"][0] > 0 and r["ci_iid"][0] > 0 and r["placebo_p"] < 0.05 and r["bh"] and r["mean_ex5"] is not None and r["mean_ex5"] > 0)
            r["verdict"] = "PASS" if ok else "FAIL"
    tags = btc_regime_weeks(rawD["BTC"])
    data_end = max(int(v[0][-1]) for v in raw15.values()) + M15
    summary = dict(cost_rt=COST, data_end_utc=time.strftime("%Y-%m-%d %H:%M", time.gmtime(data_end / 1000)), cells=rows,
                   coins15={c: [time.strftime("%Y-%m-%d", time.gmtime(v[0][0] / 1000)), int(len(v[0]))] for c, v in raw15.items()},
                   regime_mix={"DEV": mix_line(tags, 0, VAL_START), "VALIDATION": mix_line(tags, VAL_START, data_end)})
    json.dump(summary, open(HERE / "summary.json", "w"), indent=1)
    write_result(summary)


def fm(x, f="%+.3f"):
    return "n/a" if x is None else f % x


def write_result(s):
    cells = s["cells"]
    npass = sum(1 for r in cells if r["verdict"] == "PASS")
    L = []
    L.append("Regime mix: VALIDATION %s | DEV %s (BTC weekly close vs 200d SMA +-5 %%)" % (s["regime_mix"]["VALIDATION"], s["regime_mix"]["DEV"]))
    L.append("")
    L.append("Verdict: %s. %d of 9 cells PASS; CBP-R05 NOT_TESTABLE." % ("PASS (lead)" if npass else "FAIL / no edge", npass))
    L.append("")
    L.append("| rule | cell | TF | trades DEV/VAL | win rate VAL | mean R VAL | CI day-cluster | CI per-trade | placebo (mean R, p) | mean R w/o best 5 days | BH | verdict |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in cells:
        if "mean_val" in r:
            L.append("| %s | %s | %s | %d / %d | %s | %s | [%+.3f, %+.3f] | [%+.3f, %+.3f] | %s, %s | %s | %s | %s |" % (
                r["rule"], r["cell"], r["tf"], r["n_dev"], r["n_val"], fm(r["win_val"], "%.1f%%" if False else "%.3f"), fm(r["mean_val"]),
                r["ci_cl"][0], r["ci_cl"][1], r["ci_iid"][0], r["ci_iid"][1], fm(r.get("placebo_mean")), fm(r.get("placebo_p"), "%.3f"),
                fm(r["mean_ex5"]), "yes" if r["bh"] else "no", r["verdict"]))
        else:
            L.append("| %s | %s | %s | %d / %d | n/a | n/a | n/a | n/a | n/a | n/a | n/a | %s |" % (r["rule"], r["cell"], r["tf"], r.get("n_dev", 0), r.get("n_val", 0), r["verdict"]))
    L.append("| CBP-R05 | - | 1h/D | - | - | - | - | - | - | - | - | NOT_TESTABLE |")
    L.append("")
    L.append("Descriptive (VALIDATION): " + "; ".join("%s hold %s bars (placebo %s), median stop %s%%, median R %s, mean net %s%% per trade" % (
        r["cell"], fm(r.get("hold_val"), "%.1f"), fm(r.get("placebo_hold"), "%.1f"), fm(r.get("median_stop_pct"), "%.2f"), fm(r.get("median_r_val")), fm(r.get("mean_net_pct_val"), "%.3f"))
        for r in cells if r.get("n_val")))
    L.append("")
    L.append("Costs: 2 x BINANCE_TAKER + SLIPPAGE_RT_S13 = %.0f bp round trip. Data end %s UTC. Coverage (15m start dates): %s." % (
        s["cost_rt"] * 1e4, s["data_end_utc"], ", ".join("%s %s" % (c, v[0]) for c, v in s["coins15"].items())))
    (HERE / "RESULT_numbers.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    with open(HERE / "cells.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cell", "n_dev", "mean_dev", "n_val", "mean_val", "ci_cl_lo", "ci_cl_hi", "ci_iid_lo", "ci_iid_hi", "p_cl", "placebo_mean", "placebo_p",
                    "win_val", "days_val", "mean_ex5", "hold_val", "placebo_hold", "median_stop_pct", "bh", "verdict", "hour_blocks_meanR"])
        for r in cells:
            g = lambda k: r.get(k)  # noqa: E731
            w.writerow([r["cell"], r.get("n_dev"), g("mean_dev"), r.get("n_val"), g("mean_val"), (g("ci_cl") or [None, None])[0], (g("ci_cl") or [None, None])[1],
                        (g("ci_iid") or [None, None])[0], (g("ci_iid") or [None, None])[1], g("p_cl"), g("placebo_mean"), g("placebo_p"), g("win_val"),
                        g("days_val"), g("mean_ex5"), g("hold_val"), g("placebo_hold"), g("median_stop_pct"), r.get("bh"), r["verdict"], json.dumps(g("hour_blocks_meanR"))])


if __name__ == "__main__":
    main()
