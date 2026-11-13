"""4h/8h/12h RSI(14) <= 12 + daily RSI < 30 + next candle closes higher; stop = signal low; exits 1R/2R/3R/time (PRE_REG.md).
python run_1113.py -> REPORT.md, summary.json, cells.csv next to this file. Data cache: runtime_data/edge4-rsi-4h-le12-1113/ (fetch_klines.py)."""
import csv
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DATA = os.path.abspath(os.path.join(ROOT, "..", "runtime_data", "edge4-rsi-4h-le12-1113"))
sys.path.insert(0, os.path.join(ROOT, "backtest"))
import fees  # noqa: E402
import research_kit as RK  # noqa: E402

COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "BNB", "ADA", "LINK", "LTC", "AVAX",
         "DOT", "ATOM", "TRX", "BCH", "ETC", "UNI", "NEAR", "FIL", "XLM", "AAVE"]
TFS = {"4h": 4 * 3600000, "8h": 8 * 3600000, "12h": 12 * 3600000}
EXITS = ("1R", "2R", "3R", "time")
RSI_MAX = 12.0
DAILY_MAX = 30.0
HOLD = 12          # bars after the entry bar (OURS)
DAY = 86400000
def cost_rt():
    return 2 * fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13

SPLITS = ("DEV", "VAL", "RECENT")
VAL0 = int(np.datetime64("2024-07-01", "ms").astype(np.int64))
REC0 = int(np.datetime64("2025-07-01", "ms").astype(np.int64))
B_BOOT, B_PLAC, MIN_N = 2000, 1000, 30
rng = np.random.default_rng(20261113)


def rsi(closes, period=14):
    """Wilder RSI, nan before index `period` (FORMULAS s1)."""
    c = np.asarray(closes, float)
    out = np.full(len(c), np.nan)
    if len(c) <= period:
        return out
    d = np.diff(c)
    ag = np.maximum(d[:period], 0).sum() / period
    al = np.maximum(-d[:period], 0).sum() / period

    def val(g, lo):
        if lo == 0:
            return 100.0 if g > 0 else 50.0
        return 100.0 - 100.0 / (1.0 + g / lo)
    out[period] = val(ag, al)
    for i in range(period + 1, len(c)):
        ag = (ag * (period - 1) + max(d[i - 1], 0.0)) / period
        al = (al * (period - 1) + max(-d[i - 1], 0.0)) / period
        out[i] = val(ag, al)
    return out


def daily_asof(close_ms, d_open, d_rsi):
    """Daily RSI of the last daily bar whose close (open + 1 day) is <= close_ms; nan if none."""
    d_close = np.asarray(d_open) + DAY
    idx = np.searchsorted(d_close, np.asarray(close_ms), side="right") - 1
    out = np.full(len(idx), np.nan)
    ok = idx >= 0
    out[ok] = np.asarray(d_rsi, float)[idx[ok]]
    return out


def signals(rsi_tf, d_asof, close, thr=RSI_MAX, dthr=DAILY_MAX):
    """Signal bar indices S: RSI<=thr, daily RSI<dthr (nan = no), and close[S+1] > close[S]."""
    rsi_tf, d_asof, close = np.asarray(rsi_tf, float), np.asarray(d_asof, float), np.asarray(close, float)
    m = np.zeros(len(close), bool)
    with np.errstate(invalid="ignore"):
        m[:-1] = (rsi_tf[:-1] <= thr) & (d_asof[:-1] < dthr) & (close[1:] > close[:-1])
    return np.where(m)[0]


def outcomes(o, h, l, c, t, S, tf_ms, exit_kind):
    """Long trades for setup bars S: entry = close[S+1], stop = low[S], walk bars S+2 .. S+1+HOLD. Returns dict of arrays aligned with S."""
    S = np.asarray(S, dtype=int)
    n = len(c)
    e = S + 1
    ok = (S >= 0) & (e + HOLD < n)
    e = np.where(ok, e, 0)
    s = np.where(ok, S, 0)
    idx = np.minimum(e[:, None] + 1 + np.arange(HOLD)[None, :], n - 1)
    ok &= (t[np.minimum(e + HOLD, n - 1)] - t[s] == (HOLD + 1) * tf_ms)
    entry = c[e]
    P = l[s]
    R = entry - P
    ok &= np.isfinite(R) & (R > 0)
    R = np.where(ok, R, 1.0)
    O, H, L, C = o[idx], h[idx], l[idx], c[idx]
    stop_hit = L <= P[:, None]
    ev = stop_hit.copy()
    tgt_hit = np.zeros_like(stop_hit)
    tgt = entry.copy()
    if exit_kind != "time":
        tgt = entry + float(exit_kind[0]) * R
        tgt_hit = (H >= tgt[:, None]) & ~stop_hit
        ev |= tgt_hit
    ev[:, HOLD - 1] = True
    j = ev.argmax(axis=1)
    r = np.arange(len(S))
    px = np.where(stop_hit[r, j], np.minimum(O[r, j], P), np.where(tgt_hit[r, j], tgt, C[r, j]))
    net_pct = px / entry - 1.0 - cost_rt()
    return {"valid": ok, "e": e, "x": e + 1 + j, "net_pct": net_pct, "net_r": net_pct / (R / entry)}


def make_8h(rows):
    """Build 8h rows [t,o,h,l,c,v] from 4h rows: aligned pairs (open at 0/8/16 UTC and the next 4h bar present)."""
    rows = np.asarray(rows, float)
    h4, h8 = 4 * 3600000, 8 * 3600000
    by = {int(r[0]): r for r in rows}
    out = []
    for tt in sorted(by):
        pair = tt + h4
        if tt % h8 == 0 and pair in by:
            a, b = by[tt], by[pair]
            out.append([tt, a[1], max(a[2], b[2]), min(a[3], b[3]), b[4], a[5] + b[5]])
    return np.array(out, float).reshape(-1, 6)


def pick_one_position(e, x):
    """Greedy chronological: take a signal only if its entry bar is after the previous taken trade's exit bar."""
    keep, free = [], -1
    for k in range(len(e)):
        if e[k] > free:
            keep.append(k)
            free = x[k]
    return np.array(keep, dtype=int)


def bh(pvals, q=0.10):
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    ok = p[order] <= q * np.arange(1, m + 1) / m
    kmax = np.where(ok)[0].max() + 1 if ok.any() else 0
    sig = np.zeros(m, bool)
    sig[order[:kmax]] = True
    return sig


# ---------------------------------------------------------------------------- data and tables
def load(coin, iv):
    p = os.path.join(DATA, "%s_%s.json" % (coin, iv))
    return np.array(json.load(open(p)), float) if os.path.exists(p) else None


def split_of(te):
    return np.where(te < VAL0, 0, np.where(te < REC0, 1, 2))


def build():
    """tabs[(tf, coin, exit)] = arrays over all confirm bars with a valid walk: e, x, net_r, net_pct, sig, dlow, split, day."""
    tabs, nsig = {}, {}
    for coin in COINS:
        dk, k4, k12 = load(coin, "D"), load(coin, "240"), load(coin, "720")
        if dk is None or k4 is None or k12 is None:
            print("missing data", coin)
            continue
        dk = dk[:-1]  # last daily bar may be open
        d_rsi = rsi(dk[:, 4])
        for tf, ms in TFS.items():
            k = k4 if tf == "4h" else k12 if tf == "12h" else make_8h(k4)
            k = k[:-1]  # last bar may be open
            t, o, h, l, c = k[:, 0].astype(np.int64), k[:, 1], k[:, 2], k[:, 3], k[:, 4]
            rs = rsi(c)
            da = daily_asof(t + ms, dk[:, 0], d_rsi)
            conf = np.zeros(len(c), bool)
            conf[:-1] = c[1:] > c[:-1]
            conf &= np.isfinite(rs) & np.isfinite(da)
            s_all = np.where(conf)[0]
            sig_all = (rs[s_all] <= RSI_MAX) & (da[s_all] < DAILY_MAX)
            for ex in EXITS:
                out = outcomes(o, h, l, c, t, s_all, ms, ex)
                v = out["valid"]
                te = t[out["e"][v]] + ms
                tabs[(tf, coin, ex)] = dict(e=out["e"][v], x=out["x"][v], net_r=out["net_r"][v], net_pct=out["net_pct"][v],
                                            sig=sig_all[v], dlow=(da[s_all] < DAILY_MAX)[v], split=split_of(te), day=te // DAY)
            nsig[(tf, coin)] = int(len(signals(rs, da, c)))
    return tabs, nsig


def cell_trades(tabs, tf, ex):
    out = {k: [] for k in ("net_r", "net_pct", "day", "split", "coin")}
    for ci, coin in enumerate(COINS):
        tb = tabs.get((tf, coin, ex))
        if tb is None:
            continue
        ix = np.where(tb["sig"])[0]
        if len(ix) == 0:
            continue
        ix = ix[np.argsort(tb["e"][ix], kind="stable")]
        keep = ix[pick_one_position(tb["e"][ix], tb["x"][ix])]
        for k in ("net_r", "net_pct", "day", "split"):
            out[k].append(tb[k][keep])
        out["coin"].append(np.full(len(keep), ci))
    return {k: (np.concatenate(v) if v else np.array([])) for k, v in out.items()}


def stats(Rr, P, day):
    n = len(Rr)
    if n == 0:
        return dict(n=0, mean_r=np.nan, win=np.nan, mean_pct=np.nan, p=1.0, lo=np.nan, hi=np.nan)
    mean, se = RK.cluster_mean_se(Rr, day)
    p = 1.0 if not np.isfinite(se) or se <= 0 else 0.5 * math.erfc(mean / se / math.sqrt(2))
    lo = hi = np.nan
    if n >= MIN_N:
        u, inv = np.unique(day, return_inverse=True)
        Sm = np.bincount(inv, weights=Rr)
        Cn = np.bincount(inv).astype(float)
        ix = rng.integers(0, len(u), (B_BOOT, len(u)))
        m = Sm[ix].sum(1) / Cn[ix].sum(1)
        lo, hi = np.percentile(m, [2.5, 97.5])
    return dict(n=n, mean_r=float(np.mean(Rr)), win=float(np.mean(P > 0)), mean_pct=float(np.mean(P)), p=p, lo=float(lo), hi=float(hi))


def placebo(tabs, tf, ex, tr, sp, obs_mean, need_dlow):
    sel = tr["split"] == sp
    tot = int(sel.sum())
    if tot == 0:
        return np.nan, np.nan
    sums = np.zeros(B_PLAC)
    for ci in np.unique(tr["coin"][sel]):
        nc = int((tr["coin"][sel] == ci).sum())
        tb = tabs[(tf, COINS[int(ci)], ex)]
        m = tb["split"] == sp
        if need_dlow:
            m &= tb["dlow"]
        pool = tb["net_r"][m]
        if len(pool) == 0:
            return np.nan, np.nan
        sums += pool[rng.integers(0, len(pool), (B_PLAC, nc))].sum(1)
    means = sums / tot
    return float(means.mean()), float((1 + (means >= obs_mean).sum()) / (B_PLAC + 1))


def regime_share():
    """BTC daily close vs its 200d SMA: bull > +5%, bear < -5%, else range. Share of days per split."""
    dk = load("BTC", "D")[:-1]
    c = dk[:, 4]
    cs = np.cumsum(np.insert(c, 0, 0.0))
    sma = np.full(len(c), np.nan)
    sma[199:] = (cs[200:] - cs[:-200]) / 200.0
    dev = c / sma - 1.0
    reg = np.where(dev > 0.05, 0, np.where(dev < -0.05, 1, 2)).astype(float)
    reg[~np.isfinite(dev)] = np.nan
    sp = split_of(dk[:, 0] + DAY)
    shares = {}
    for i, nm in enumerate(SPLITS):
        r = reg[(sp == i) & np.isfinite(reg)]
        shares[nm] = [float((r == k).mean()) if len(r) else float("nan") for k in range(3)]
    return shares


def main():
    tabs, nsig = build()
    rows, tradesets = [], {}
    for tf in TFS:
        for ex in EXITS:
            tr = cell_trades(tabs, tf, ex)
            tradesets[(tf, ex)] = tr
            for si, sp in enumerate(SPLITS + ("ALL",)):
                m = np.ones(len(tr["split"]), bool) if sp == "ALL" else tr["split"] == si
                st = stats(tr["net_r"][m], tr["net_pct"][m], tr["day"][m])
                st.update(tf=tf, exit=ex, split=sp, p1_mean=np.nan, p1_p=np.nan, p2_mean=np.nan, p2_p=np.nan)
                if sp != "ALL" and st["n"] > 0:
                    st["p1_mean"], st["p1_p"] = placebo(tabs, tf, ex, tr, si, st["mean_r"], False)
                    st["p2_mean"], st["p2_p"] = placebo(tabs, tf, ex, tr, si, st["mean_r"], True)
                rows.append(st)
    val = [r for r in rows if r["split"] == "VAL"]
    sig = bh([r["p"] for r in val])
    for r, s in zip(val, sig):
        r["bh"] = bool(s)
    shares = regime_share()
    one_regime_val = max(shares["VAL"]) > 0.85
    for r in rows:
        r.setdefault("bh", None)
        r["pass"] = None
        if r["split"] == "VAL":
            p1 = r["p1_p"] if np.isfinite(r["p1_p"]) else 1.0
            r["pass"] = bool(r["n"] >= MIN_N and r["mean_r"] > 0 and r["lo"] > 0 and p1 <= 0.05 and r["bh"] and not one_regime_val)
    if any(r["pass"] for r in val):
        verdict = "PASS"
    elif any(r["n"] >= MIN_N for r in val):
        verdict = "FAIL"
    else:
        verdict = "UNDERPOWERED"
    btc = {}
    for key, tr in tradesets.items():
        m = tr["coin"] == 0
        btc[key] = (int(m.sum()), float(tr["net_r"][m].mean()) if m.any() else float("nan"))
    _write(rows, verdict, nsig, shares, one_regime_val, btc)


def f(x, d=3):
    return "n/a" if x is None or (isinstance(x, float) and not np.isfinite(x)) else ("%.*f" % (d, x))


def _clean(v):
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, (np.integer, int)):
        return int(v)
    if isinstance(v, (float, np.floating)):
        return None if not np.isfinite(v) else float(v)
    return v


def _write(rows, verdict, nsig, shares, one_regime_val, btc):
    keys = ["tf", "exit", "split", "n", "mean_r", "lo", "hi", "win", "mean_pct", "p", "p1_mean", "p1_p", "p2_mean", "p2_p", "bh", "pass"]
    with open(os.path.join(HERE, "cells.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    val = [r for r in rows if r["split"] == "VAL"]
    allr = [r for r in rows if r["split"] == "ALL"]
    n_pass = sum(1 for r in val if r["pass"])
    summ = dict(verdict=verdict, cost_rt=cost_rt(), hold_bars=HOLD, coins=len(COINS), n_pass=n_pass,
                cells=[{k: _clean(r.get(k)) for k in keys} for r in rows],
                signals_per_tf_coin={"%s/%s" % k: v for k, v in nsig.items()}, regime_share=shares)
    json.dump(summ, open(os.path.join(HERE, "summary.json"), "w"), indent=1)
    best = max(val, key=lambda r: (r["n"], r["mean_r"] if np.isfinite(r["mean_r"]) else -9))
    L = []
    L.append("# REPORT: 4h / 8h / 12h RSI(14) <= 12 + daily RSI < 30 + next candle closes higher (edge4-rsi-4h-le12-daily-lt30-1113)")
    L.append("")
    L.append("**Result: %s.** VALIDATION n by cell %d..%d; largest-n VALIDATION cell %s %s: n=%d, fee-net mean %s R, CI [%s, %s], P1 placebo p=%s, BH=%s. %d of 12 cells PASS. Rule: `PRE_REG.md` (frozen before any outcome)." % (
        verdict, min(r["n"] for r in val), max(r["n"] for r in val), best["tf"], best["exit"], best["n"], f(best["mean_r"]), f(best["lo"]), f(best["hi"]), f(best["p1_p"]), best["bh"], n_pass))
    L.append("")
    mix = ["%s bull %d%% / bear %d%% / range %d%%" % (s, *[round(100 * x) for x in shares[s]]) for s in SPLITS]
    L.append("Regime mix: BTC daily close vs 200d SMA (bull > +5%%, bear < -5%%, else range), share of days: %s%s." % (
        "; ".join(mix), "; VALIDATION is ONE-REGIME (cannot carry a PASS)" if one_regime_val else ""))
    L.append("")
    L.append("Round-trip cost %.4f (2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13), no funding; stop = signal-candle low; entry at the close of the confirming candle; %d-bar cap after entry; 20 Bybit perps from listing (2020-03 on)." % (cost_rt(), HOLD))
    L.append("")
    L.append("## Pooled all-period (descriptive, the card's headline)")
    L.append("| TF | exit | n | mean net R | 95% CI | win % | mean net % |")
    L.append("|---|---|---|---|---|---|---|")
    for r in allr:
        L.append("| %s | %s | %d | %s | [%s, %s] | %s | %s |" % (r["tf"], r["exit"], r["n"], f(r["mean_r"]), f(r["lo"]), f(r["hi"]),
                                                                 f(100 * r["win"], 1) if r["n"] else "n/a", f(100 * r["mean_pct"], 2) if r["n"] else "n/a"))
    L.append("")
    L.append("## By split (CI only at n >= 30; P1 = coin/split-matched random bars with only 'next closes higher'; P2 = same restricted to daily RSI < 30; p = share of placebo means >= observed)")
    L.append("| TF | exit | split | n | mean net R | 95% CI | win % | P1 mean R | P1 p | P2 mean R | P2 p | BH10 (VAL) | PASS (VAL) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        if r["split"] == "ALL":
            continue
        L.append("| %s | %s | %s | %d%s | %s | [%s, %s] | %s | %s | %s | %s | %s | %s | %s |" % (
            r["tf"], r["exit"], r["split"], r["n"], " UNDERPOWERED" if r["n"] < MIN_N else "", f(r["mean_r"]), f(r["lo"]), f(r["hi"]),
            f(100 * r["win"], 1) if r["n"] else "n/a", f(r["p1_mean"]), f(r["p1_p"]), f(r["p2_mean"]), f(r["p2_p"]),
            "" if r["bh"] is None else ("yes" if r["bh"] else "no"), "" if r["pass"] is None else ("PASS" if r["pass"] else "no")))
    L.append("")
    L.append("## BTC alone (descriptive, all periods)")
    L.append("| TF | exit | n | mean net R |")
    L.append("|---|---|---|---|")
    for (tf, ex), (n, m) in btc.items():
        L.append("| %s | %s | %d | %s |" % (tf, ex, n, f(m)))
    L.append("")
    L.append("## Signals per coin (RSI<=12, daily<30, next closes higher; before the one-position rule and the 12-bar-walk validity filter)")
    L.append("| coin | 4h | 8h | 12h |")
    L.append("|---|---|---|---|")
    for coin in COINS:
        L.append("| %s | %s | %s | %s |" % (coin, *[nsig.get((tf, coin), "n/a") for tf in TFS]))
    L.append("")
    L.append("Limitations: no funding charge; 8h built from 4h pairs; stops and targets assumed taker with 2 bp slippage in total (real stop slippage in a selloff is larger); long only; Bybit data begins 2020-03 (BTC) to 2022 (newer coins).")
    open(os.path.join(HERE, "REPORT.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:6]))


if __name__ == "__main__":
    main()
