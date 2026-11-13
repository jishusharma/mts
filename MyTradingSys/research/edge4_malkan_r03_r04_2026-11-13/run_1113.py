"""Malkan MAL-R03 (bearish) / MAL-R04 (bullish) regular RSI divergence engine. Rules: PRE_REG.md. Part b = engine only.

Bars are [open_ms, o, h, l, c, v] ascending. Swing = close strictly above (R03) / below (R04) both neighbouring closes
(1 bar each side, OURS); A, B and C use closes only, never wicks. The confirming candle is the bar right after B
(red for R03, green for R04); entry at its close, stop beyond its extreme, target point C.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "backtest")))
import fees  # noqa: E402

def cost_rt():
    """Round trip as a fraction of entry price, taker on every fill (fees.py constants, none of my own)."""
    return 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13


def rsi_wilder(closes, n=14):
    """Wilder RSI; None for the first n bars (index n is the first value)."""
    out = [None] * len(closes)
    if len(closes) <= n:
        return out
    ch = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    ag = sum(max(c, 0.0) for c in ch[:n]) / n
    al = sum(max(-c, 0.0) for c in ch[:n]) / n

    def val():
        return 100.0 if al == 0 else 100.0 - 100.0 / (1.0 + ag / al)
    out[n] = val()
    for i in range(n + 1, len(closes)):
        c = ch[i - 1]
        ag = (ag * (n - 1) + max(c, 0.0)) / n
        al = (al * (n - 1) + max(-c, 0.0)) / n
        out[i] = val()
    return out


def find_signals(bars, lookback, rule, rsi=None):
    """Signals for rule 'R03' (short) or 'R04' (long): dicts t (confirm bar index), a, b, entry, stop, target, side.
    A = most recent swing before B, 2..lookback bars earlier; divergence needs price and RSI to disagree."""
    short = rule == "R03"
    c = [b[4] for b in bars]
    if rsi is None:
        rsi = rsi_wilder(c)
    sgn = 1 if short else -1  # compare sgn*close so one code path serves both sides

    def pivot(i):
        return 0 < i < len(c) - 1 and sgn * c[i] > sgn * c[i - 1] and sgn * c[i] > sgn * c[i + 1]
    piv = [i for i in range(len(c)) if pivot(i)]
    out = []
    for k, b in enumerate(piv):
        t = b + 1
        if t >= len(bars):
            continue
        o, h, l, cl = bars[t][1], bars[t][2], bars[t][3], bars[t][4]
        if not (cl < o if short else cl > o):
            continue
        if k == 0:
            continue
        a = piv[k - 1]
        if not (2 <= b - a <= lookback) or rsi[a] is None or rsi[b] is None:
            continue
        if not (sgn * c[b] > sgn * c[a] and sgn * rsi[b] < sgn * rsi[a]):
            continue
        seg = c[a:b + 1]
        target = min(seg) if short else max(seg)
        stop = h if short else l
        if (short and not (stop > cl > target)) or (not short and not (stop < cl < target)):
            continue
        out.append({"t": t, "a": a, "b": b, "entry": cl, "stop": stop, "target": target, "side": "short" if short else "long"})
    return out


def simulate(bars, signals, lookback, iv_ms, exclusive=True):
    """One open position per coin: a signal while a trade is open is skipped. Exit at target, stop, or the close of bar
    t + 2*lookback; a bar touching both counts as the stop. Trades whose bars A..exit are not contiguous are dropped.
    net_r = (gross move - cost_rt() * entry) / risk."""
    trades = []
    busy_until = -1
    for s in signals:
        t = s["t"]
        if exclusive and t <= busy_until:
            continue
        short = s["side"] == "short"
        risk = abs(s["stop"] - s["entry"])
        end = min(t + 2 * lookback, len(bars) - 1)
        reason, ex, px = None, None, None
        for j in range(t + 1, end + 1):
            h, l = bars[j][2], bars[j][3]
            hit_stop = h >= s["stop"] if short else l <= s["stop"]
            hit_tgt = l <= s["target"] if short else h >= s["target"]
            if hit_stop:
                reason, ex, px = "stop", j, s["stop"]
            elif hit_tgt:
                reason, ex, px = "target", j, s["target"]
            if reason:
                break
        if reason is None:
            if end < t + 2 * lookback:
                continue  # data ended before the cap: unresolved, not counted
            reason, ex, px = "cap", end, bars[end][4]
        busy_until = ex
        if any(bars[i + 1][0] - bars[i][0] != iv_ms for i in range(s["a"], ex)):
            continue
        move = (s["entry"] - px) if short else (px - s["entry"])
        trades.append({"t": t, "side": s["side"], "entry": s["entry"], "stop": s["stop"], "target": s["target"],
                       "exit": ex, "reason": reason, "net_r": (move - cost_rt() * s["entry"]) / risk})
    return trades


# ---------------------------------------------------------------------------- part c: run, placebo, report
import datetime  # noqa: E402
import json  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge4-malkan-r03-r04-1113"))
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX",
         "DOT", "ATOM", "TRX", "BCH", "ETC", "UNI", "NEAR", "FIL", "XLM", "AAVE"]
IV_MS = {"1h": 3600000, "4h": 14400000}
IV_FILE = {"1h": "60", "4h": "240"}
LOOKBACKS = (12, 18)
RULES = ("R03", "R04")
SPLITS = ("DEV", "VALIDATION", "RECENT")
VAL0 = int(datetime.datetime(2024, 7, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)
REC0 = int(datetime.datetime(2025, 7, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)
DAY = 86400000
MIN_N = 30
B_BOOT, B_PLAC, SEED = 2000, 1000, 20261114
PLAC_MAX = 3000  # placebo candidate bars sampled per coin and cell (speed; the pool is a random subset)


def split_of(ms):
    return 0 if ms < VAL0 else (1 if ms < REC0 else 2)


def bh(pvals, q=0.10):
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    ok = p[order] <= q * np.arange(1, m + 1) / m
    kmax = int(np.where(ok)[0].max()) + 1 if ok.any() else 0
    sig = np.zeros(m, bool)
    sig[order[:kmax]] = True
    return sig


def cluster_stats(rs, days, rng):
    """n, mean net R, one-sided p (share of day-cluster bootstrap means <= 0, add-one), 95% CI only at n >= MIN_N."""
    n = len(rs)
    if n == 0:
        return dict(n=0, mean_r=None, p=1.0, lo=None, hi=None, win=None)
    rs, days = np.asarray(rs, float), np.asarray(days)
    u, inv = np.unique(days, return_inverse=True)
    sm = np.bincount(inv, weights=rs)
    cn = np.bincount(inv).astype(float)
    ix = rng.integers(0, len(u), (B_BOOT, len(u)))
    means = sm[ix].sum(1) / cn[ix].sum(1)
    lo = hi = None
    if n >= MIN_N:
        lo, hi = (float(x) for x in np.percentile(means, [2.5, 97.5]))
    return dict(n=n, mean_r=float(rs.mean()), p=float((1 + (means <= 0).sum()) / (B_BOOT + 1)), lo=lo, hi=hi,
                win=float((rs > 0).mean()))


def placebo_draw(pool_by_coin, n_by_coin, rng):
    """One resample: for each coin draw exactly its observed trade count from that coin's placebo pool."""
    out = []
    for c, n in n_by_coin.items():
        pool = pool_by_coin[c]
        out.extend(pool[rng.integers(0, len(pool), n)])
    return out


def placebo_p(pool_by_coin, n_by_coin, observed_mean, rng, b=B_PLAC):
    tot = sum(n_by_coin.values())
    if tot == 0 or any(len(pool_by_coin.get(c, [])) == 0 for c in n_by_coin):
        return None
    ge = sum(1 for _ in range(b) if float(np.mean(placebo_draw(pool_by_coin, n_by_coin, rng))) >= observed_mean)
    return (1 + ge) / (b + 1)


def verdict_cell(c, bh_sig, one_regime):
    """PASS rule of PRE_REG on a VALIDATION cell dict."""
    if c["n"] < MIN_N:
        return "UNDERPOWERED"
    ok = (c["mean_r"] > 0 and c["lo"] is not None and c["lo"] > 0 and c["placebo_p"] is not None
          and c["placebo_p"] <= 0.05 and bh_sig and not one_regime)
    return "PASS" if ok else "FAIL"


def overall(verdicts):
    if "PASS" in verdicts:
        return "PASS"
    return "FAIL" if "FAIL" in verdicts else "UNDERPOWERED"


def build_summary(cells):
    """cells: list of cell dicts; VALIDATION rows carry the verdict."""
    val = [c["verdict"] for c in cells if c["split"] == "VALIDATION"]
    return {"study": "edge4-malkan-r03-r04", "trials": None, "overall": overall(val), "cells": cells,
            "n_pass": sum(v == "PASS" for v in val), "cost_rt": cost_rt()}


def layer_map_row(summary, report):
    return {"id": "MALKAN-R03-R04-RSI-DIV-20261114", "trials": None,
            "title": "Malkan regular RSI divergence (MAL-R03 short, MAL-R04 long), closes-only swings, 1h/4h, 12/18-bar lookback, 20 perps",
            "date": "2026-11-14", "market": "Bybit linear USDT perps, 20 coins, 1h and 4h, 2020+", "layers": ["rsi_divergence"],
            "params": "SOURCED: divergence, confirm candle, stop beyond signal candle, target point C, RSI 14; OURS: closes-only swings, 12/18 lookback, 1h/4h, 2x lookback time cap",
            "split": "DEV 2020-01..2024-06 / VAL 2024-07..2025-06 / RECENT 2025-07+",
            "fees": "fee-net: 2 x BINANCE_TAKER + SLIPPAGE_RT_S13 from fees.py, no funding",
            "interaction": "day-cluster bootstrap CI; placebo (any bar closing in trade direction, same stop and C-style target); BH 10% over 8 VALIDATION cells",
            "effects": summary["effects"], "n": summary["n_text"], "verdict": summary["overall"] + ": " + summary["verdict_text"],
            "report": report, "read": "summary"}


# ---------------------------------------------------------------------------- data and run
def load(coin, tf):
    p = os.path.join(DATA, "%s_%s.json" % (coin, IV_FILE[tf]))
    return json.load(open(p)) if os.path.exists(p) else None


def placebo_signals(bars, lookback, rule, rng, max_n):
    """Every bar that merely closes in the trade direction (no divergence); stop = its extreme, target = lowest (R03) or
    highest (R04) close of the prior `lookback` bars including itself; dropped when stop or target is on the wrong side."""
    short = rule == "R03"
    idx = [t for t in range(lookback, len(bars)) if (bars[t][4] < bars[t][1] if short else bars[t][4] > bars[t][1])]
    if len(idx) > max_n:
        idx = sorted(rng.choice(idx, max_n, replace=False).tolist())
    out = []
    for t in idx:
        h, l, cl = bars[t][2], bars[t][3], bars[t][4]
        seg = [b[4] for b in bars[t - lookback:t + 1]]
        target, stop = (min(seg), h) if short else (max(seg), l)
        if (short and not (stop > cl > target)) or (not short and not (stop < cl < target)):
            continue
        out.append({"t": t, "a": t - lookback, "b": t, "entry": cl, "stop": stop, "target": target,
                    "side": "short" if short else "long"})
    return out


def btc_regime():
    """BTC daily close vs its 200-day SMA (from 1h): 1 above by >5%, -1 below by >5%, 0 within; keyed by UTC day index."""
    dayc = {}
    for r in load("BTC", "1h"):
        dayc[int(r[0] // DAY)] = r[4]
    days = sorted(dayc)
    c = np.array([dayc[d] for d in days])
    cs = np.cumsum(np.insert(c, 0, 0.0))
    reg = {}
    for i, d in enumerate(days):
        if i >= 199:
            dev = c[i] / ((cs[i + 1] - cs[i - 199]) / 200.0) - 1.0
            reg[d] = 1 if dev > 0.05 else (-1 if dev < -0.05 else 0)
    return reg


def run_cell(rule, tf, lb, data, reg, rng):
    trs, plac = [], {}
    iv = IV_MS[tf]
    for coin in COINS:
        bars, rsi = data.get(coin, (None, None))
        if not bars:
            continue
        for t in simulate(bars, find_signals(bars, lb, rule, rsi=rsi), lb, iv):
            te = bars[t["t"]][0] + iv  # entry = close of the confirm bar
            trs.append(dict(t, coin=coin, te=te, split=split_of(te), day=int(te // DAY), regime=reg.get(int(te // DAY) - 1)))
        for t in simulate(bars, placebo_signals(bars, lb, rule, rng, PLAC_MAX), lb, iv, exclusive=False):
            plac.setdefault((coin, split_of(bars[t["t"]][0] + iv)), []).append(t["net_r"])
    return trs, plac


def main():
    rng = np.random.default_rng(SEED)
    reg = btc_regime()
    cells = []
    for tf in ("1h", "4h"):
        data = {}
        for coin in COINS:
            bars = load(coin, tf)
            data[coin] = (bars, rsi_wilder([b[4] for b in bars]) if bars else None)
        for rule in RULES:
            for lb in LOOKBACKS:
                trs, plac = run_cell(rule, tf, lb, data, reg, rng)
                for si, sp in enumerate(SPLITS):
                    sel = [t for t in trs if t["split"] == si]
                    st = cluster_stats([t["net_r"] for t in sel], [t["day"] for t in sel], rng)
                    nbc = {}
                    for t in sel:
                        nbc[t["coin"]] = nbc.get(t["coin"], 0) + 1
                    pools = {c: np.array(plac.get((c, si), [])) for c in nbc}
                    st["placebo_p"] = placebo_p(pools, nbc, st["mean_r"], rng) if sel else None
                    allp = [x for c in nbc for x in plac.get((c, si), [])]
                    st["placebo_mean"] = float(np.mean(allp)) if allp else None
                    rm = [t["regime"] for t in sel if t["regime"] is not None]
                    st["regime_share"] = {k: (rm.count(v) / len(rm) if rm else None) for k, v in (("above", 1), ("below", -1), ("within", 0))}
                    st["one_regime"] = bool(rm) and max(rm.count(v) for v in (1, -1, 0)) / len(rm) > 0.85
                    st.update(rule=rule, tf=tf, lookback=lb, split=sp)
                    cells.append(st)
                print(rule, tf, lb, [c["n"] for c in cells[-3:]], flush=True)
    vals = [c for c in cells if c["split"] == "VALIDATION"]
    sig = bh([c["p"] for c in vals], 0.10)
    for c, s in zip(vals, sig):
        c["bh"] = bool(s)
        c["verdict"] = verdict_cell(c, bool(s), c["one_regime"])
    for c in cells:
        if c["split"] != "VALIDATION":
            c["verdict"] = None
    rec = {(c["rule"], c["tf"], c["lookback"]): c for c in cells if c["split"] == "RECENT"}
    for c in vals:
        r = rec[(c["rule"], c["tf"], c["lookback"])]
        c["robust"] = bool(c["verdict"] == "PASS" and r["n"] >= MIN_N and r["mean_r"] is not None and r["mean_r"] > 0)
    summ = build_summary(cells)
    shares = {}
    for si, sp in enumerate(SPLITS):
        ds = [r for d, r in reg.items() if split_of(d * DAY) == si]
        shares[sp] = {k: (ds.count(v) / len(ds) if ds else None) for k, v in (("above", 1), ("below", -1), ("within", 0))}
    summ["day_regime_share"] = shares
    summ["n_text"] = "VALIDATION n by cell %d..%d" % (min(c["n"] for c in vals), max(c["n"] for c in vals))
    summ["effects"] = "; ".join("%s %s %d: VAL n=%d mean %s R" % (c["rule"], c["tf"], c["lookback"], c["n"], f(c["mean_r"])) for c in vals)
    summ["verdict_text"] = "%d of 8 VALIDATION cells PASS; rule in PRE_REG.md frozen before any outcome" % summ["n_pass"]
    json.dump(summ, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
    write_report(summ, vals)
    return summ


def f(x, d=3):
    return "n/a" if x is None else ("%." + str(d) + "f") % x


def write_report(summ, vals):
    L = ["# Malkan MAL-R03 / MAL-R04 regular RSI divergence, 1h/4h, 20 perps (edge4-malkan-c-1114)", ""]
    L.append("**Result: %s.** %s. %s. Rule: `PRE_REG.md` (frozen before any outcome). Fee-net (round trip %.4f of entry), no funding." % (
        summ["overall"], summ["verdict_text"], summ["n_text"], cost_rt()))
    L += ["", "Regime mix (BTC daily close vs 200-day SMA: above / below / within 5%), share of days: " + "; ".join(
        "%s %s/%s/%s" % (sp, f(s["above"], 2), f(s["below"], 2), f(s["within"], 2)) for sp, s in summ["day_regime_share"].items()), ""]
    L += ["## VALIDATION cells (the verdict)",
          "| rule | tf | lookback | n | mean net R | 95% CI | win | boot p | placebo p | placebo mean R | BH10 | ONE-REGIME | verdict |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for c in vals:
        ci = "[%s, %s]" % (f(c["lo"]), f(c["hi"])) if c["lo"] is not None else "n<30"
        L.append("| %s | %s | %d | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s%s |" % (
            c["rule"], c["tf"], c["lookback"], c["n"], f(c["mean_r"]), ci, f(c["win"], 2), f(c["p"]), f(c["placebo_p"]),
            f(c["placebo_mean"]), c["bh"], c["one_regime"], c["verdict"], " (ROBUST)" if c["robust"] else ""))
    L += ["", "## DEV and RECENT (context; CI only at n >= 30)", "| rule | tf | lookback | split | n | mean net R | 95% CI | placebo p |", "|---|---|---|---|---|---|---|---|"]
    for c in summ["cells"]:
        if c["split"] != "VALIDATION":
            ci = "[%s, %s]" % (f(c["lo"]), f(c["hi"])) if c["lo"] is not None else "n<30"
            L.append("| %s | %s | %d | %s | %d | %s | %s | %s |" % (c["rule"], c["tf"], c["lookback"], c["split"], c["n"], f(c["mean_r"]), ci, f(c["placebo_p"])))
    L += ["", "Limitations: no funding charge; stops and targets assumed taker with 2 bp slippage in total; placebo pools are random subsets (up to %d candidate bars per coin and cell, split by entry time); swing = 1-bar-each-side close pivot and the 2x lookback time cap are OURS; a stop touched in the same bar as the target counts as the stop." % PLAC_MAX,
          "The 12 and 18 lookback cells are near copies (A is the most recent swing, usually well inside 12 bars), so they are not independent tests. The stop is one signal candle wide, so the 0.0012 round-trip cost alone is a large fraction of R (the loss is mostly cost, not direction).",
          "One-sided p is the share of day-cluster bootstrap means at or below zero; BH 10% over the 8 VALIDATION p-values. n < 30 is UNDERPOWERED, never no edge."]
    open(os.path.join(HERE, "REPORT.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
