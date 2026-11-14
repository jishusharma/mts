"""edge8: rules 9 and 10 of the parent, long only, gross cap 1.0x, on the 60 NEW coins (confirmation) and on the parent 60 (NOT-CONFIRMATION).
Usage: python study.py -> results.json. Functions below the pnl/boot/segments line are copied from the parent study.py (edge7) except where marked NEW."""
import json, os, sys, time, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import trend_lib as T
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "backtest")))
import fees
CU = fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 / 2
FLAT_FUND = 0.0001 * 3
DAY = 86400000
T0 = int(dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
LAST_DAY = dt.datetime(2026, 11, 12, tzinfo=dt.timezone.utc)      # last closed day; the forming bar (2026-11-13) is dropped
N_DAYS = (int(LAST_DAY.timestamp() * 1000) - T0) // DAY + 1
rng = np.random.default_rng(20261114)
NDRAW = 1000
GROSS_CAP = 1.0
NEW_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "..", "runtime_data", "edge8-long-gated-trend-newcoins-1114"))
PARENT_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "mts-jis-nb-edge7-daily-trend-follow-1113-2", "runtime_data", "edge7-daily-trend-follow-1113"))


def load_series(path, n=N_DAYS):
    O, H, L, C = (np.full(n, np.nan) for _ in range(4))
    for r in json.load(open(path)):
        d = (r[0] - T0) // DAY
        if 0 <= d < n: O[d], H[d], L[d], C[d] = r[1], r[2], r[3], r[4]
    return O, H, L, C


def load_funding(path, n=N_DAYS):
    F = np.full(n, np.nan)
    for ts, rate in json.load(open(path))["rows"]:
        d = (ts - T0) // DAY
        if 0 <= d < n: F[d] = (0.0 if np.isnan(F[d]) else F[d]) + rate
    return F


def load(coins, folder, btc_file=None):
    O, H, L, C, F = (np.full((len(coins), N_DAYS), np.nan) for _ in range(5))
    for i, c in enumerate(coins):
        O[i], H[i], L[i], C[i] = load_series(os.path.join(folder, c + "_1d.json"))
        F[i] = load_funding(os.path.join(folder, c + "_fund.json"))
    btc_c = load_series(btc_file)[3] if btc_file else C[0].copy()
    dates = np.array([dt.datetime.fromtimestamp((T0 + d * DAY) / 1000, dt.timezone.utc) for d in range(N_DAYS)])
    return O, H, L, C, F, btc_c, dates


def coin_returns(O, C):
    n = O.shape[1]; R = np.full(O.shape, np.nan)
    R[:, :n - 1] = O[:, 1:] / O[:, :n - 1] - 1
    R[:, n - 1] = C[:, n - 1] / O[:, n - 1] - 1
    return R


# ---------------- NEW: long-only gated rules + gross cap ----------------
def cap(E, limit=GROSS_CAP):
    """Scale each day's column pro rata so that sum of |weights| <= limit. Uses only that day's weights (no look-ahead)."""
    g = np.abs(E).sum(0)
    scale = np.where(g > limit, limit / np.where(g > 0, g, 1.0), 1.0)
    return E * scale


def eff(W):
    """weight in force on day d = weight set at close d-1."""
    E = np.zeros_like(W); E[:, 1:] = W[:, :-1]; return E


def build_W(H, L, C, dates, btc_c):
    """Parent rules 9 and 10 (gate applied first, as in the parent), long (positive) part only. Weights set at the close of each day, uncapped."""
    dow = np.array([d.weekday() for d in dates]); m200 = T.sma(btc_c, 200)
    r9 = np.array([T.gate(T.tsm(C[i], dow, 30), btc_c, m200) for i in range(C.shape[0])])
    r10 = np.array([T.gate(T.adx_rule(H[i], L[i], C[i]), btc_c, m200) for i in range(C.shape[0])])
    return {"9 GATED-TSM30": np.where(r9 > 0, r9, 0.0), "10 GATED-ADX14": np.where(r10 > 0, r10, 0.0)}, m200


def build_E(W, cap_fn=cap, shift_fn=eff):
    return cap_fn(shift_fn(W))


# ---------------- copied from parent ----------------
def pnl_matrix(E, R, F):
    Rz = np.where(np.isnan(R), 0.0, R)
    dE = np.abs(np.diff(E, axis=1, prepend=0.0))
    fund = np.where(np.isnan(F), np.where(E > 0, FLAT_FUND * E, 0.0), E * F)
    return E * Rz - dE * CU - fund


def sharpe(x): return float(np.mean(x) / np.std(x, ddof=1) * np.sqrt(365)) if len(x) > 2 and np.std(x) > 0 else 0.0


def boot(x, nb=10000, blk=10):
    n = len(x); k = int(np.ceil(n / blk)); cs = np.concatenate([[0.0], np.cumsum(x)])
    st = rng.integers(0, n - blk + 1, size=(nb, k))
    m = (cs[st + blk] - cs[st]).sum(1) / (k * blk)
    return float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)), float((m <= 0).mean())


def segments(E):
    out = []
    for i in range(E.shape[0]):
        s = np.sign(E[i]); a = None
        for d in range(E.shape[1] + 1):
            cur = s[d] if d < E.shape[1] else 0
            if a is not None and (cur != s[a]): out.append((i, a, d)); a = None
            if a is None and cur != 0: a = d
    return out


def placebo(E, R, F, segs, v0):
    """NDRAW VAL means; each run moved to a random start on the same coin (same weight path/duration), gross cap and costs recomputed (NEW: cap)."""
    n = E.shape[1]
    firsts = [int(np.argmax(~np.isnan(R[i]))) if (~np.isnan(R[i])).any() else 0 for i in range(E.shape[0])]
    lasts = [n - 1 - int(np.argmax(~np.isnan(R[i][::-1]))) if (~np.isnan(R[i])).any() else 0 for i in range(E.shape[0])]
    out = np.empty(NDRAW)
    for k in range(NDRAW):
        Ep = np.zeros_like(E)
        for (i, a, b) in segs:
            ln = b - a; f, l = firsts[i], lasts[i]
            ns = a if l - f + 1 <= ln else int(rng.integers(f, l - ln + 2))
            Ep[i, ns:ns + ln] += E[i, a:b][:max(0, min(ln, n - ns))]
        P = pnl_matrix(cap(Ep), R, F)
        out[k] = P[:, v0:].sum(0).mean()
    return out


def regime_mix(btc_c, m200, v0):
    rel = btc_c[v0:] / m200[v0:] - 1
    ok = ~np.isnan(rel); rel = rel[ok]
    return dict(bull=float((rel > 0.05).mean()), bear=float((rel < -0.05).mean()), range=float(((rel >= -0.05) & (rel <= 0.05)).mean()), n=int(len(rel)))


def stats(E, R, F, v0, d0, dates, coins, bsh, bmean, rebuilt_for_placebo=True):
    P = pnl_matrix(E, R, F); port = P.sum(0)
    val, dev = port[v0:], port[d0:v0]
    ci = boot(val); bsum = P[:, v0:].sum(1); tot = bsum.sum()
    top5 = np.argsort(-bsum)[:5]
    wo5 = (tot - bsum[top5].sum()) / len(val) * 365
    wo10 = float(np.sort(val)[:-10].mean()) if len(val) > 10 else float("nan")
    cum = np.cumsum(val); mdd_val = float((np.maximum.accumulate(cum) - cum).max())
    cumf = np.cumsum(port[d0:]); mdd_all = float((np.maximum.accumulate(cumf) - cumf).max())
    segs = segments(E); segv = [s for s in segs if s[1] >= v0]
    yrs = {}
    for y in range(2020, dates[-1].year + 1):
        idx = [d for d in range(d0, len(dates)) if dates[d].year == y]
        if idx: yrs[y] = float(port[idx].sum())
    held = E != 0
    cov = float(np.mean(~np.isnan(F)[held])) if held.any() else float("nan")
    gross = np.abs(E[:, v0:]).sum(0)
    r = dict(trades_val=len(segv), trades_total=len(segs), val_mean=float(val.mean()), val_ann=float(val.mean() * 365), val_sharpe=sharpe(val),
             dev_sharpe=sharpe(dev) if np.std(dev) > 0 else None, dev_ann=float(dev.mean() * 365) if len(dev) else None, ci_lo=ci[0], ci_hi=ci[1], p_one=ci[2],
             mdd_val=mdd_val, mdd_all=mdd_all, basket_sharpe=bsh, basket_mean=bmean, beats_basket=bool(sharpe(val) > bsh and val.mean() > bmean),
             ex5_ann=float(wo5), top5=[coins[i] for i in top5], ex10d_mean=wo10, ex10d_ann=wo10 * 365,
             top10d_share=float(np.sort(val)[::-1][:10].sum() / val.sum()) if val.sum() > 0 else None,
             avg_gross=float(gross.mean()), max_gross=float(gross.max()), days_invested=float((gross > 0).mean()), coins_in_book=float((E[:, v0:] > 0).sum(0).mean()),
             coins_ever=int((E[:, v0:] > 0).any(1).sum()), avg_hold=float(np.mean([b - a for _, a, b in segs])) if segs else None, fund_cov=cov,
             last90_sum=float(port[-90:].sum()), per_year=yrs, val_cum=float(val.sum()))
    if segs:
        pv = placebo(E, R, F, segs, v0)
        r["placebo_p"] = float((1 + (pv >= val.mean()).sum()) / (NDRAW + 1)); r["placebo_mean"] = float(pv.mean())
    else: r["placebo_p"] = None
    return r


def verdict(c):
    g = dict(g1_ci=c["ci_lo"] > 0, g2_sharpe=c["val_sharpe"] >= 1.0, g3_basket=c["beats_basket"], g4_placebo=bool(c["placebo_p"] is not None and c["placebo_p"] < 0.05),
             g5_bonf=bool(c["p_one"] <= 0.025 and c["placebo_p"] is not None and c["placebo_p"] <= 0.025),
             g6_robust=bool(c["ex10d_mean"] > 0 and c["ex5_ann"] > 0))
    return g, ("PASS" if all(g.values()) else "FAIL")


def run(label, coins, folder, btc_file):
    t = time.time()
    O, H, L, C, F, btc_c, dates = load(coins, folder, btc_file)
    R = coin_returns(O, C)
    W9, m200 = build_W(H, L, C, dates, btc_c)
    d0 = int(np.argmax(~np.isnan(m200)))
    v0 = [d for d in range(N_DAYS) if dates[d] >= dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)][0]
    bk = np.nanmean(R, axis=0); bk = np.where(np.isnan(bk), 0.0, bk)
    bval = bk[v0:]; bsh, bmean = sharpe(bval), float(bval.mean())
    out = {"label": label, "n_coins": len(coins), "d0": str(dates[d0].date()), "v0": str(dates[v0].date()), "last": str(dates[-1].date()),
           "basket_val_sharpe": bsh, "basket_val_ann": bmean * 365, "basket_val_cum": float(bval.sum()), "regime_val": regime_mix(btc_c, m200, v0),
           "coins_with_funding": int(sum(1 for i in range(len(coins)) if (~np.isnan(F[i])).any())), "rules": {}}
    print(label, "d0", out["d0"], "v0", out["v0"], "basket Sh %.2f" % bsh, "regime", out["regime_val"], flush=True)
    for name, W in W9.items():
        E = build_E(W)
        r = stats(E, R, F, v0, d0, dates, coins, bsh, bmean)
        r["gates"], r["verdict"] = verdict(r)
        # for reference only: the same book without the cap (parent sizing, long only)
        Eu = eff(W); ru = pnl_matrix(Eu, R, F).sum(0)[v0:]
        r["uncapped_ref"] = dict(val_ann=float(ru.mean() * 365), val_sharpe=sharpe(ru), avg_gross=float(np.abs(Eu[:, v0:]).sum(0).mean()))
        out["rules"][name] = r
        print("%-16s tr %4d valAnn %+.3f Sh %+.2f CI[%+.5f,%+.5f] plc %s mdd %.2f gross %.2f %s %.0fs" % (name, r["trades_val"], r["val_ann"], r["val_sharpe"], r["ci_lo"], r["ci_hi"], r["placebo_p"], r["mdd_val"], r["avg_gross"], r["verdict"], time.time() - t), flush=True)
    return out


def main():
    from universe import COINS as NEW
    from universe_parent import COINS as PAR
    res = {"new60_CONFIRMATION": run("new60", NEW, NEW_DIR, os.path.join(NEW_DIR, "BTC_spot_1d.json")),
           "parent60_NOT_CONFIRMATION": run("parent60", PAR, PARENT_DIR, None)}
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    print("done")


if __name__ == "__main__":
    main()
