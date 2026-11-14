"""Run the 10 pre-registered rules x {long, short, combined}. Usage: python study.py -> results.json (+ printed summary)."""
import json, os, sys, time, datetime as dt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from universe import COINS
from fetch import OUT
import trend_lib as T
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "backtest")))
import fees
CU = fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 / 2      # per unit of |weight change| at each fill
FLAT_FUND = 0.0001 * 3                                  # 0.01 % per 8 h = 0.03 % per day, against longs only, where no record
DAY = 86400000
T0 = int(dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
rng = np.random.default_rng(20261113)
NDRAW = 1000


def load():
    rows = {c: json.load(open(os.path.join(OUT, c + "_1d.json"))) for c in COINS}
    last = max(r[-1][0] for r in rows.values())
    nd = (last - T0) // DAY            # drop the newest (forming or just-closed unverified) bar
    # keep only bars with open time < last (newest bar may be forming); index = day number
    n = int(nd)
    O, H, L, C = (np.full((len(COINS), n), np.nan) for _ in range(4))
    F = np.full((len(COINS), n), np.nan)
    for i, c in enumerate(COINS):
        for r in rows[c]:
            d = (r[0] - T0) // DAY
            if 0 <= d < n: O[i, d], H[i, d], L[i, d], C[i, d] = r[1], r[2], r[3], r[4]
        fj = json.load(open(os.path.join(OUT, c + "_fund.json")))
        for ts, rate in fj["rows"]:
            d = (ts - T0) // DAY
            if 0 <= d < n: F[i, d] = (0.0 if np.isnan(F[i, d]) else F[i, d]) + rate
    dates = np.array([dt.datetime.fromtimestamp((T0 + d * DAY) / 1000, dt.timezone.utc) for d in range(n)])
    return O, H, L, C, F, dates


def coin_returns(O, C):
    """r[d] = open[d+1]/open[d]-1 (position set at close d-1 is held open d -> open d+1); last day ends at its close."""
    n = O.shape[1]; R = np.full(O.shape, np.nan)
    R[:, :n - 1] = O[:, 1:] / O[:, :n - 1] - 1
    R[:, n - 1] = C[:, n - 1] / O[:, n - 1] - 1
    return R


def build_W(O, H, L, C, dates):
    n = O.shape[1]; dow = np.array([d.weekday() for d in dates])
    btc_m200 = T.sma(C[0], 200)
    rules = {}
    def per(fn): return np.array([fn(i) for i in range(len(COINS))])
    rules["1 DON20/10"] = per(lambda i: T.donchian(H[i], L[i], C[i], 20, 10))
    rules["2 DON55/20"] = per(lambda i: T.donchian(H[i], L[i], C[i], 55, 20))
    rules["3 TSM30"] = per(lambda i: T.tsm(C[i], dow, 30))
    rules["4 TSM90"] = per(lambda i: T.tsm(C[i], dow, 90))
    rules["5 ADX14"] = per(lambda i: T.adx_rule(H[i], L[i], C[i]))
    rules["6 ADX14-3d"] = per(lambda i: T.adx_3d(O[i], H[i], L[i], C[i]))
    rules["7 MA20/50"] = per(lambda i: T.ma_rule(C[i]))
    rules["8 GATED-DON20/10"] = np.array([T.gate(w, C[0], btc_m200) for w in rules["1 DON20/10"]])
    rules["9 GATED-TSM30"] = np.array([T.gate(w, C[0], btc_m200) for w in rules["3 TSM30"]])
    rules["10 GATED-ADX14"] = np.array([T.gate(w, C[0], btc_m200) for w in rules["5 ADX14"]])
    return rules, btc_m200


def eff(W):
    """weight in force on day d = weight set at close d-1."""
    E = np.zeros_like(W); E[:, 1:] = W[:, :-1]; return E


def pnl_matrix(E, R, F):
    """per coin-day net pnl (fraction of equity): E*R - |dE|*CU - funding."""
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
    """maximal runs of one sign per coin: list of (coin, a, b) b exclusive."""
    out = []
    for i in range(E.shape[0]):
        s = np.sign(E[i]); a = None
        for d in range(E.shape[1] + 1):
            cur = s[d] if d < E.shape[1] else 0
            if a is not None and (cur != s[a]): out.append((i, a, d)); a = None
            if a is None and cur != 0: a = d
    return out


def placebo(E, R, F, segs, v0, side):
    """returns array of VAL means for NDRAW draws. side 'both' -> random direction per run; else random start date on the same coin."""
    n = E.shape[1]; seg_id = np.full(E.shape, -1)
    for k, (i, a, b) in enumerate(segs): seg_id[i, a:b] = k
    firsts = [int(np.argmax(~np.isnan(R[i]))) if (~np.isnan(R[i])).any() else 0 for i in range(E.shape[0])]
    lasts = [n - 1 - int(np.argmax(~np.isnan(R[i][::-1]))) if (~np.isnan(R[i])).any() else 0 for i in range(E.shape[0])]
    out = np.empty(NDRAW)
    lo = max(v0 - 1, 0)
    for k in range(NDRAW):
        if side == "both":
            sg = np.where(rng.random(len(segs)) < 0.5, -1.0, 1.0)
            Ep = E * np.where(seg_id >= 0, sg[np.maximum(seg_id, 0)], 1.0)
        else:
            Ep = np.zeros_like(E)
            for (i, a, b) in segs:
                ln = b - a; f, l = firsts[i], lasts[i]
                if l - f + 1 <= ln: ns = a
                else: ns = int(rng.integers(f, l - ln + 2))
                Ep[i, ns:ns + ln] += E[i, a:b][:max(0, min(ln, n - ns))]
        P = pnl_matrix(Ep, R, F)
        out[k] = P[:, v0:].sum(0).mean()
    return out


def stats(E, R, F, v0, d0, dates, bsk_val, basket_sharpe, basket_mean, do_placebo, side):
    P = pnl_matrix(E, R, F); port = P.sum(0)
    val, dev = port[v0:], port[d0:v0]
    ci = boot(val); bsum = P[:, v0:].sum(1); tot = bsum.sum()
    top5 = np.argsort(-bsum)[:5]
    wo5 = (tot - bsum[top5].sum()) / len(val) * 365
    best10 = np.sort(val)[::-1][:10].sum()
    cum = np.cumsum(val); mdd_val = float((np.maximum.accumulate(cum) - cum).max())
    cumf = np.cumsum(port[d0:]); mdd_all = float((np.maximum.accumulate(cumf) - cumf).max())
    segs = segments(E); segv = [s for s in segs if s[1] >= v0]
    yrs = {}
    for y in range(2020, dates[-1].year + 1):
        idx = [d for d in range(d0, len(dates)) if dates[d].year == y]
        if idx: yrs[y] = float(port[idx].sum())
    held = E != 0
    cov = float(np.mean(~np.isnan(F)[held])) if held.any() else float("nan")
    r = dict(trades_val=len(segv), trades_total=len(segs), trades_per_year=len(segv) / (len(val) / 365),
             val_mean=float(val.mean()), val_ann=float(val.mean() * 365), val_sharpe=sharpe(val), dev_sharpe=sharpe(dev),
             dev_ann=float(dev.mean() * 365), ci_lo=ci[0], ci_hi=ci[1], p_one=ci[2], mdd_val=mdd_val, mdd_all=mdd_all,
             basket_sharpe=basket_sharpe, basket_mean=basket_mean, beats_basket=bool(sharpe(val) > basket_sharpe and val.mean() > basket_mean),
             ex5_ann=float(wo5), top5=[COINS[i] for i in top5], top5_share=float(bsum[top5].sum() / tot) if tot > 0 else None,
             top10d_share=float(best10 / val.sum()) if val.sum() > 0 else None, avg_hold=float(np.mean([b - a for _, a, b in segs])) if segs else None,
             avg_gross=float(np.abs(E[:, v0:]).sum(0).mean()), fund_cov=cov, last90_sum=float(port[-90:].sum()), per_year=yrs)
    if do_placebo and segs:
        pv = placebo(E, R, F, segs, v0, side)
        r["placebo_p"] = float((1 + (pv >= val.mean()).sum()) / (NDRAW + 1)); r["placebo_mean"] = float(pv.mean())
    else: r["placebo_p"] = None
    return r


def bh(ps, q=0.10):
    order = np.argsort(ps); m = len(ps); k = 0
    for rank, i in enumerate(order, 1):
        if ps[i] <= q * rank / m: k = rank
    rej = np.zeros(m, bool)
    for rank, i in enumerate(order, 1):
        if rank <= k: rej[i] = True
    return rej


def main():
    t = time.time()
    O, H, L, C, F, dates = load()
    R = coin_returns(O, C)
    rules, m200 = build_W(O, H, L, C, dates)
    n = O.shape[1]
    d0 = int(np.argmax(~np.isnan(m200)))
    v0 = [d for d in range(n) if dates[d] >= dt.datetime(2024, 1, 1, tzinfo=dt.timezone.utc)][0]
    bk = np.nanmean(np.where(np.isnan(R), np.nan, R), axis=0)
    bval = bk[v0:]; bsh, bmean = sharpe(bval), float(bval.mean())
    print("days", n, "d0", dates[d0].date(), "v0", dates[v0].date(), "last", dates[-1].date(), "basket VAL sharpe %.2f mean %.5f" % (bsh, bmean), "load %.0fs" % (time.time() - t), flush=True)
    res = {"meta": dict(last_day=str(dates[-1].date()), d0=str(dates[d0].date()), v0=str(dates[v0].date()), n_days=n, basket_val_sharpe=bsh,
                        basket_val_ann=bmean * 365, basket_val_cum=float(bval.sum()), coins_with_funding=int(sum(1 for i in range(len(COINS)) if (~np.isnan(F[i])).any())),
                        coins_with_funding_list=[c for i, c in enumerate(COINS) if (~np.isnan(F[i])).any()]), "rules": {}}
    for name, W in rules.items():
        E = eff(W); out = {}
        for side, Es in (("long", np.where(E > 0, E, 0.0)), ("short", np.where(E < 0, E, 0.0)), ("combined", E)):
            out[side] = stats(Es, R, F, v0, d0, dates, bval, bsh, bmean, True, "both" if side == "combined" else side)
            r = out[side]
            print("%-18s %-8s tr %4d valAnn %+.3f Sh %+.2f devSh %+.2f CI[%+.5f,%+.5f] plc %s %.0fs" % (name, side, r["trades_val"], r["val_ann"], r["val_sharpe"], r["dev_sharpe"], r["ci_lo"], r["ci_hi"], r["placebo_p"], time.time() - t), flush=True)
        res["rules"][name] = out
    names = list(rules)
    rej = bh(np.array([res["rules"][k]["combined"]["p_one"] for k in names]))
    for k, rj in zip(names, rej):
        c = res["rules"][k]["combined"]; c["bh_reject"] = bool(rj)
        c["gates"] = dict(g1_ci=c["ci_lo"] > 0 and c["val_mean"] > 0, g2_sharpe=c["val_sharpe"] >= 1.0 and c["dev_sharpe"] > 0, g3a_basket=c["beats_basket"],
                          g3b_placebo=bool(c["placebo_p"] is not None and c["placebo_p"] <= 0.05), g4_bh=bool(rj))
        c["verdict"] = "PASS" if all(c["gates"].values()) else "FAIL"
    json.dump(res, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=float)
    print("done %.0fs" % (time.time() - t))


if __name__ == "__main__":
    main()
