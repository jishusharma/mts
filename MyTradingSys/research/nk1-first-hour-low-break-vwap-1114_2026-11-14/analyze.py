"""Run the pre-registered study on the cached data and write RESULT.md + results.json. python analyze.py"""
import os, sys, json, time, datetime as dt
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get("MTS_DATA_CACHE", r"F:\MTS\data_cache") + os.sep + "binance"
SYMS = "BTC ETH BNB XRP ADA LTC TRX LINK XLM DOGE ETC BCH SOL DOT AVAX ATOM UNI VET NEO ZEC".split()
B = 5000
SEED = 1114
KN = {0: "S_UTC", 1: "S_NY"}
EN = {0: "E1 band", 1: "E2 prior-day", 2: "E3 sess-end"}


def load():
    out = {}
    now = time.time() * 1000
    for s in SYMS:
        p = os.path.join(CACHE, s + "USDT_5m.npz")
        if not os.path.exists(p):
            print("MISSING", s)
            continue
        a = np.load(p)["a"]
        a = a[np.unique(a[:, 0], return_index=True)[1]]
        a = a[a[:, 0] + study.MS5 <= now]
        out[s] = a
    return out


def boot_cluster(days, x, rng):
    ud, inv = np.unique(days, return_inverse=True)
    S = np.bincount(inv, weights=x)
    N = np.bincount(inv).astype(float)
    D = len(ud)
    idx = rng.integers(0, D, (B, D))
    m = S[idx].sum(1) / N[idx].sum(1)
    return m, S, N, ud


def boot_trade(x, rng):
    T = len(x)
    out = np.empty(B)
    ch = max(1, 20_000_000 // T)
    for i in range(0, B, ch):
        k = min(ch, B - i)
        out[i:i + k] = x[rng.integers(0, T, (k, T))].mean(1)
    return out


def row_stats(tr, kind, et, maker, split=1, matched=True, placebo=True, rng=None):
    fee = study.FEE_M if maker else study.FEE_T
    sel = [t for t in tr if t["kind"] == kind and t["matched"] == matched and t["split"] == split and (t["Rm"] is not None if maker else True)]
    if matched is False:
        sel = [t for t in sel if t["phase"] != 0]
    n = len(sel)
    if n == 0:
        return dict(n=0)
    R = np.array([t["Rm" if maker else "R"] for t in sel])
    g = np.array([(t["retm"] if maker else t["ret"])[et] for t in sel])
    x = g / R - fee / R
    days = np.array([t["day"] for t in sel])
    res = dict(n=n, win=float((x > 0).mean()), mean=float(x.mean()), fee_R=float((fee / R).mean()), R_pct=float(R.mean() * 100))
    if n >= 20 and rng is not None:
        m, S, N, ud = boot_cluster(days, x, rng)
        res["cl_lo"] = float(np.percentile(m, 2.5))
        res["cl_p"] = float((1 + (m <= 0).sum()) / (B + 1))
        tb = boot_trade(x, rng)
        res["tr_lo"] = float(np.percentile(tb, 2.5))
        o = np.argsort(S)[::-1][:5]
        keep = np.ones(len(S), bool)
        keep[o] = False
        res["ex5"] = float(S[keep].sum() / N[keep].sum())
        res["days"] = int(len(ud))
        if placebo:
            pl = np.array([t["pl"][:, et] for t in sel])  # (T,10) gross ret
            net = pl / R[:, None] - (fee / R)[:, None]
            idx = rng.integers(0, 10, (200, n))
            pm = net[np.arange(n)[None, :], idx].mean(1)
            res["plc_mean"] = float(pm.mean())
            res["plc_p"] = float((1 + (pm >= x.mean()).sum()) / 201)
    return res


def bh(ps, q=0.10):
    m = len(ps)
    o = np.argsort(ps)
    ok = np.zeros(m, bool)
    k = -1
    for r, i in enumerate(o, 1):
        if ps[i] <= q * r / m:
            k = r
    for r, i in enumerate(o, 1):
        if r <= k:
            ok[i] = True
    return ok


def regime_mix(coins):
    cnt = {0: np.zeros(3), 1: np.zeros(3)}
    bull = {0: [0, 0], 1: [0, 0]}
    for s, a in coins.items():
        ud, O, H, L, C = study.daily(a)
        ph = study.phases(ud, H, L, C)
        for d, p in ph.items():
            cnt[0 if d < study.SPLIT_DAY else 1][{1: 0, -1: 1, 0: 2}[p]] += 1
        cs = np.cumsum(np.r_[0, C])
        for i in range(200, len(C)):
            sp = 0 if ud[i] < study.SPLIT_DAY else 1
            bull[sp][0] += C[i] > (cs[i + 1] - cs[i - 199]) / 200
            bull[sp][1] += 1
    return cnt, bull


def btc_today(a):
    t = a[:, 0]
    last = int(t[-1])
    day = last // study.DAY
    ud, O, H, L, C = study.daily(a)
    ph = study.phases(ud, H, L, C)
    lines = []
    lines.append("Data ends %s UTC (last closed 5m bar). Prior UTC day (%s): H %.0f, L %.0f, C %.0f." % (
        dt.datetime.fromtimestamp(last / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
        dt.datetime.fromtimestamp((day - 1) * 86400, dt.timezone.utc).date(),
        H[ud == day - 1][0] if (ud == day - 1).any() else float("nan"), L[ud == day - 1][0] if (ud == day - 1).any() else float("nan"),
        C[ud == day - 1][0] if (ud == day - 1).any() else float("nan")))
    lines.append("Phase for UTC day %s (rule from the prior close): %s." % (
        dt.datetime.fromtimestamp(day * 86400, dt.timezone.utc).date(), {1: "UP", -1: "DOWN", 0: "RANGE"}.get(ph.get(day), "n/a")))
    for kind in (0, 1):
        om = study.open_ms(day, kind)
        i0 = int(np.searchsorted(t, om))
        if i0 >= len(t) or t[i0] != om:
            lines.append("%s: session not open yet in the data." % KN[kind])
            continue
        w = a[i0:i0 + 12]
        k = len(w)
        typ = (w[:, 2] + w[:, 3] + w[:, 4]) / 3
        vw = (typ * w[:, 5]).cumsum() / w[:, 5].cumsum()
        txt = "%s (open %s UTC), %d of 12 first-hour bars in: " % (KN[kind], dt.datetime.fromtimestamp(om / 1000, dt.timezone.utc).strftime("%H:%M"), k)
        if k >= 3:
            Lo, Hi = w[:3, 3].min(), w[:3, 2].max()
            txt += "opening-range low %.0f / high %.0f; " % (Lo, Hi)
            bl = [i for i in range(3, k) if w[i, 3] < Lo]
            bh_ = [i for i in range(3, k) if w[i, 2] > Hi]
            txt += "low broken in hour: %s; high broken in hour: %s; " % ("yes (bar %d)" % bl[0] if bl else "no", "yes (bar %d)" % bh_[0] if bh_ else "no")
        txt += "session VWAP %.0f, last close %.0f." % (vw[-1], w[-1, 4])
        lines.append(txt)
    return lines


def main():
    coins = load()
    t0 = time.time()
    tr = study.run(coins)
    print("trades", len(tr), "secs", int(time.time() - t0), flush=True)
    rng = np.random.default_rng(SEED)
    rows = []
    for kind in (0, 1):
        for et in (0, 1, 2):
            for maker in (False, True):
                v = row_stats(tr, kind, et, maker, 1, True, True, rng)
                d = row_stats(tr, kind, et, maker, 0, True, False, None)
                ctl = row_stats(tr, kind, et, maker, 1, False, False, rng)
                rows.append(dict(kind=kind, et=et, maker=maker, val=v, dev=d, ctl=ctl))
    ps = np.array([r["val"].get("cl_p", 1.0) for r in rows])
    ok = bh(ps)
    for r, b in zip(rows, ok):
        v = r["val"]
        r["bh"] = bool(b)
        g = dict(n=v["n"] >= 100, mean=v.get("mean", -1) > 0, cl=v.get("cl_lo", -1) > 0, tr=v.get("tr_lo", -1) > 0,
                 plc=v.get("plc_p", 1) < 0.05, bh=bool(b), ex5=v.get("ex5", -1) > 0)
        r["gates"] = g
        r["pass"] = all(g.values())
        r["under"] = v["n"] < 100
    json.dump(rows, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    cnt, bull = regime_mix(coins)
    # per-phase descriptive (taker, E3 and E1) validation
    ph_tab = []
    for kind in (0, 1):
        for et in (0, 1, 2):
            for p in (1, -1, 0):
                sel = [t for t in tr if t["kind"] == kind and t["split"] == 1 and t["matched"] and t["phase"] == p]
                if sel:
                    x = np.array([t["ret"][et] / t["R"] - study.FEE_T / t["R"] for t in sel])
                    ph_tab.append((KN[kind], EN[et], {1: "UP", -1: "DOWN", 0: "RANGE"}[p], len(sel), float(x.mean())))
    anyp = any(r["pass"] for r in rows)
    allunder = all(r["under"] for r in rows)
    verdict = "PASS" if anyp else ("UNDERPOWERED" if allunder else "FAIL")
    best = max(rows, key=lambda r: r["val"].get("mean", -9))
    L = []
    L.append("VERDICT: %s. NK first-hour low-break + close-back + near-VWAP, 20 Binance spot coins, 5m, context-matched, fee-net: %d of 12 primary VALIDATION rows pass all gates; best row %s %s %s mean net R %+.3f (n=%d)." % (
        verdict, sum(r["pass"] for r in rows), KN[best["kind"]], EN[best["et"]], "maker6" if best["maker"] else "taker12", best["val"].get("mean", float("nan")), best["val"]["n"]))
    L.append("")
    L.append("Pre-registered in PRE_REG.md (committed before any outcome). DEV <= 2023-12-31, VALIDATION >= 2024-01-01. Coins loaded: %d (%s). Signals: %d coin-session-side triggers." % (len(coins), " ".join(coins), len(tr)))
    L.append("")
    L.append("## Matched rows, VALIDATION (matched direction by phase; fee-net; R = max(structural, 0.5% of price, 0.6 ATR14-5m))")
    L.append("")
    L.append("| Session | Exit | Fee | n DEV / VAL | win % | mean net R | fee/R | R % | CI low trade | CI low day | placebo p | placebo mean R | ex-best-5 | BH | gates failed | PASS |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        v, d = r["val"], r["dev"]
        f = lambda k, fmt: (fmt % v[k]) if k in v else "n/a"
        failed = ",".join(k for k, g in r["gates"].items() if not g) or "none"
        L.append("| %s | %s | %s | %d / %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            KN[r["kind"]], EN[r["et"]], "6bp maker" if r["maker"] else "12bp", d.get("n", 0), v["n"],
            "%.1f" % (v["win"] * 100) if v["n"] else "n/a", f("mean", "%+.3f"), f("fee_R", "%.2f"), f("R_pct", "%.2f"),
            f("tr_lo", "%+.3f"), f("cl_lo", "%+.3f"), f("plc_p", "%.3f"), f("plc_mean", "%+.3f"), f("ex5", "%+.3f"),
            "yes" if r["bh"] else "no", failed, "PASS" if r["pass"] else "no"))
    L.append("")
    L.append("DEV mean net R (same rows, descriptive): " + "; ".join("%s %s %s %+.3f" % (KN[r["kind"]], EN[r["et"]], "m" if r["maker"] else "t", r["dev"].get("mean", float("nan"))) for r in rows))
    L.append("")
    L.append("## Control rows (mismatched direction in UP/DOWN days; VALIDATION; descriptive, never in the verdict)")
    L.append("")
    L.append("| Session | Exit | Fee | n | mean net R | CI low day |")
    L.append("|---|---|---|---|---|---|")
    for r in rows:
        c = r["ctl"]
        if c.get("n"):
            L.append("| %s | %s | %s | %d | %+.3f | %s |" % (KN[r["kind"]], EN[r["et"]], "6bp" if r["maker"] else "12bp", c["n"], c["mean"], ("%+.3f" % c["cl_lo"]) if "cl_lo" in c else "n/a"))
    L.append("")
    L.append("## Context")
    L.append("Phase for each day from data known at the prior close: 20-day MA slope (5-day lag) plus ADX(14) >= 20 with DI direction, else RANGE. Longs in UP, shorts in DOWN, fades both ways in RANGE are the primary rows; the opposite direction in UP/DOWN is the control table.")
    L.append("")
    L.append("Regime mix: share of coin-days by phase, and share of coin-days with close above the own 200-day SMA.")
    L.append("")
    L.append("| Split | UP | DOWN | RANGE | bull (>200d SMA) | flag |")
    L.append("|---|---|---|---|---|---|")
    for sp, nm in ((0, "DEV"), (1, "VALIDATION")):
        c = cnt[sp] / cnt[sp].sum()
        bl = bull[sp][0] / max(bull[sp][1], 1)
        fl = "ONE-REGIME" if max(c.max(), bl, 1 - bl) > 0.85 else "mixed"
        L.append("| %s | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %s |" % (nm, *(c * 100), bl * 100, fl))
    L.append("")
    L.append("## Matched VALIDATION by phase (taker 12bp, mean net R, n)")
    L.append("")
    L.append("| Session | Exit | Phase | n | mean net R |")
    L.append("|---|---|---|---|---|")
    for x in ph_tab:
        L.append("| %s | %s | %s | %d | %+.3f |" % x)
    L.append("")
    L.append("## BTC today (descriptive, no advice)")
    L.append("")
    if "BTC" in coins:
        for ln in btc_today(coins["BTC"]):
            L.append("- " + ln)
    L.append("")
    L.append("## Labels")
    L.append("SOURCED (NK): low break early in the session (first 10 min, sometimes 30), close back up, entry near VWAP without waiting for an exact touch, all inside the first hour, no big candle, stop = low breaks or 1h under VWAP. OURS: crypto sessions (00:00 UTC, NY cash open), opening-range low = first 3 bars, near-VWAP tolerance 0.1%, big-candle cutoff 2.5x, min stop 0.5% / 0.6 ATR, three exits, session lengths (12h UTC, NY close), 5-day-slope phase rule, placebo design, fees 12bp / 6bp.")
    L.append("")
    L.append("Placebo: random entry bar b3..b12 on the same coin-session and side, same R in price terms, same exit machinery, 200 draws (maker rows use 6bp fee with open-entry placebo). Bootstrap: %d resamples, seed %d, cluster = UTC date." % (B, SEED))
    open(os.path.join(HERE, "RESULT.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:30]))


if __name__ == "__main__":
    main()
