"""Run the PRE_REG study. python run.py -> results.json (+ prints). Two passes (trades, then placebo)."""
import json, os, sys, time
import numpy as np
import study as S

HERE = os.path.dirname(os.path.abspath(__file__))
TFS = {1: "5m", 2: "10m", 3: "15m"}
COSTS = {"12bp": 0.0012, "6bp": 0.0006}
BOOT = 2000
PLB = 300
PLB_MAX_N = 20000


def matched_mask(ph, d):
    return ((ph == 1) & (d == 1)) | ((ph == 2) & (d == -1)) | (ph == 3)


def mismatched_mask(ph, d):
    return ((ph == 1) & (d == -1)) | ((ph == 2) & (d == 1))


def net(t, cost):
    return t["g"] - cost * t["costu"]


def stats(x, day, rng):
    n = len(x)
    out = dict(n=int(n))
    if n == 0:
        return out
    out["win"] = float((x > 0).mean())
    out["mean"] = float(x.mean())
    if n < 2:
        return out
    # per-trade bootstrap
    m = np.empty(BOOT)
    for b in range(BOOT):
        m[b] = x[rng.integers(0, n, n)].mean()
    out["ci_trade_lo"] = float(np.quantile(m, 0.025))
    ud, inv = np.unique(day, return_inverse=True)
    sums = np.bincount(inv, weights=x)
    cnt = np.bincount(inv).astype(float)
    D = len(ud)
    idx = rng.integers(0, D, (BOOT, D))
    md = sums[idx].sum(1) / cnt[idx].sum(1)
    out["ci_day_lo"] = float(np.quantile(md, 0.025))
    out["p_day"] = float((np.sum(md <= 0) + 1) / (BOOT + 1))
    top = np.argsort(-sums)[:5]
    rest_n = n - cnt[top].sum()
    out["ex5"] = float((x.sum() - sums[top].sum()) / rest_n) if rest_n > 0 else float("nan")
    out["days"] = int(D)
    return out


def bh(ps, q=0.05):
    ps = np.array(ps)
    o = np.argsort(ps)
    m = len(ps)
    ok = np.zeros(m, bool)
    thr = -1
    for r, i in enumerate(o, 1):
        if ps[i] <= q * r / m:
            thr = r
    for r, i in enumerate(o, 1):
        ok[i] = r <= thr
    return ok


def pass1():
    T = {k: [] for k in TFS}
    mix = {}
    btc = None
    for ci, sym in enumerate(S.COINS):
        t0 = time.time()
        B = S.build_coin(sym)
        ph = B["ph"]
        dts = B["grid"][0] + np.arange(len(ph)) * 86400000
        dv = dts >= S.VAL_START_MS
        mix[sym] = dict(dev=[int(((ph == p) & ~dv).sum()) for p in (0, 1, 2, 3)], val=[int(((ph == p) & dv).sum()) for p in (0, 1, 2, 3)])
        for k in TFS:
            t = S.trades_for(B, k)
            t["coin"] = np.full(len(t["e"]), ci)
            T[k].append(t)
        if sym == "BTC":
            btc = btc_today(B)
        print(sym, len(B["c"]), "%.0fs" % (time.time() - t0), flush=True)
        del B
    out = {}
    for k in TFS:
        out[k] = {key: np.concatenate([t[key] for t in T[k]]) for key in T[k][0] if key != "k"}
    return out, mix, btc


def btc_today(B):
    o, h, l, c, grid = B["o"], B["h"], B["l"], B["c"], B["grid"]
    ext = lambda a: np.concatenate([a, np.full(288, a[-1])])
    ph_today = int(S.daily_phase(ext(h), ext(l), ext(c))[-1])
    nd = len(c) // 288
    H = h.reshape(nd, -1).max(1); L = l.reshape(nd, -1).min(1); C = c.reshape(nd, -1)[:, -1]
    names = {0: "NA", 1: "UP", 2: "DOWN", 3: "RANGE"}
    return dict(asof_utc=str(np.datetime64(int(grid[-1]) + S.MS5, "ms")), close=float(c[-1]), phase_next_day=names[ph_today],
                hm_state={TFS[k]: int(B["P"][k]["s"][-1]) for k in TFS},
                rsi14_15m=float(B["r14"][-1]), rsi14_15m_min_last3=float(np.nanmin(B["r14"][-3:])), rsi14_15m_max_last3=float(np.nanmax(B["r14"][-3:])),
                atr14_15m=float(B["P"][3]["atr"][-1]), prev_day_high=float(H[-1]), prev_day_low=float(L[-1]),
                ma20_daily=float(C[-20:].mean()), high_7d=float(H[-7:].max()), low_7d=float(L[-7:].min()), high_30d=float(H[-30:].max()), low_30d=float(L[-30:].min()))


def placebo_pass(T, sel, rows_sel):
    """rows_sel: {(k, filt): bool mask on T[k] (matched, VAL, filt)}. returns {(k,filt): dict(real_sub_mean per cost, placebo means arrays per cost, n)}"""
    rng = np.random.default_rng(11)
    acc = {}
    for key, mk in rows_sel.items():
        n = int(mk.sum())
        f = min(1.0, PLB_MAX_N / max(n, 1))
        acc[key] = dict(f=f, n=0, real_g=0.0, real_c=0.0, pg=np.zeros(PLB), pc=np.zeros(PLB))
    for ci, sym in enumerate(S.COINS):
        B = S.build_coin(sym)
        n5 = len(B["c"]); dayi = np.arange(n5) // 288
        phb = B["ph"][np.minimum(dayi, len(B["ph"]) - 1)]
        for k in TFS:
            atr5 = S.on5(B["P"][k]["atr"], k, n5, fill=np.nan)
            cap_t = S.CAP * k
            valid = (B["grid"] >= S.VAL_START_MS) & (np.arange(n5) + cap_t + 2 < n5) & ~np.isnan(atr5)
            valid[:2] = False
            pools = {p: np.nonzero(valid & (phb == p))[0] for p in (1, 2, 3)}
            for filt in ("raw", "conf"):
                key = (k, filt)
                T_ = T[k]
                m = rows_sel[key] & (T_["coin"] == ci)
                ii = np.nonzero(m)[0]
                if len(ii) == 0:
                    continue
                a = acc[key]
                if a["f"] < 1.0:
                    ii = ii[rng.random(len(ii)) < a["f"]]
                if len(ii) == 0:
                    continue
                a["n"] += len(ii)
                a["real_g"] += T_["g"][ii].sum(); a["real_c"] += T_["costu"][ii].sum()
                d = T_["d"][ii]; ph = T_["ph"][ii]; held = T_["held"][ii]
                for b0 in range(PLB):
                    pass
                # tile PLB draws
                dd = np.tile(d, PLB); hh = np.tile(held, PLB); pp = np.tile(ph, PLB)
                e = np.empty(len(dd), dtype=np.int64)
                for p in (1, 2, 3):
                    q = pp == p
                    if q.any() and len(pools[p]):
                        e[q] = pools[p][rng.integers(0, len(pools[p]), q.sum())]
                    elif q.any():
                        e[q] = -1
                good = e >= 0
                dd, hh, e2 = dd[good], hh[good], e[good]
                draw = np.tile(np.arange(PLB)[:, None], (1, len(ii))).ravel()[good]
                at = atr5[e2 - 1]
                Sd = np.maximum(S.STOP_ATR * at, S.STOP_PCT * B["o"][e2])
                g, _, entry = S.sim(B["o"], B["h"], B["l"], e2, dd, Sd, hh)
                a["pg"] += np.bincount(draw, weights=g, minlength=PLB)
                a["pc"] += np.bincount(draw, weights=entry / Sd, minlength=PLB)
        print("placebo", sym, flush=True)
        del B
    res = {}
    for key, a in acc.items():
        r = {}
        for cn, c in COSTS.items():
            if a["n"] == 0:
                continue
            real = (a["real_g"] - c * a["real_c"]) / a["n"]
            pm = (a["pg"] - c * a["pc"]) / a["n"]
            r[cn] = dict(real_sub_mean=float(real), placebo_mean=float(pm.mean()), p=float((np.sum(pm >= real) + 1) / (PLB + 1)), n_sub=int(a["n"]))
        res[key] = r
    return res


def main():
    t0 = time.time()
    T, mix, btc = pass1()
    print("pass1 %.0fs" % (time.time() - t0), flush=True)
    rng = np.random.default_rng(7)
    rows = []
    rows_sel = {}
    for k in TFS:
        t = T[k]
        val = t["ts"] >= S.VAL_START_MS
        mat = matched_mask(t["ph"], t["d"]) & (t["ph"] > 0)
        mis = mismatched_mask(t["ph"], t["d"])
        for filt in ("raw", "conf"):
            fm = np.ones(len(val), bool) if filt == "raw" else t["conf"]
            rows_sel[(k, filt)] = mat & val & fm
            for sname, sm in (("matched", mat), ("mismatched", mis)):
                for cn, c in COSTS.items():
                    x = net(t, c)
                    rv = stats(x[sm & fm & val], t["day"][sm & fm & val], rng)
                    rd = dict(n=int((sm & fm & ~val).sum()), mean=float(x[sm & fm & ~val].mean()) if (sm & fm & ~val).any() else None,
                              win=float((x[sm & fm & ~val] > 0).mean()) if (sm & fm & ~val).any() else None)
                    selv = sm & fm & val
                    fee_r = float(np.median(c * t["costu"][selv])) if selv.any() else None
                    hold = float(np.median(t["held"][selv]) * k * 5) if selv.any() else None
                    rows.append(dict(tf=TFS[k], k=k, filt=filt, set=sname, cost=cn, val=rv, dev=rd, fee_R_median=fee_r, hold_min_median=hold))
                    print(TFS[k], filt, sname, cn, rv.get("n"), rv.get("mean"), flush=True)
    pl = placebo_pass(T, None, rows_sel)
    ps = [r["val"].get("p_day", 1.0) if r["val"]["n"] > 1 else 1.0 for r in rows]
    ok = bh(ps)
    for r, o in zip(rows, ok):
        r["bh_pass"] = bool(o)
        if r["set"] == "matched":
            r["placebo"] = pl.get((r["k"], r["filt"]), {}).get(r["cost"])
        v = r["val"]
        r["gates"] = None
        if r["set"] == "matched" and v["n"] > 1 and r.get("placebo"):
            g = dict(n100=v["n"] >= 100, mean_pos=v["mean"] > 0, ci_trade=v["ci_trade_lo"] > 0, ci_day=v["ci_day_lo"] > 0,
                     placebo=r["placebo"]["p"] < 0.05, bh=r["bh_pass"], ex5=v["ex5"] > 0)
            g["PASS"] = all(g.values())
            r["gates"] = g
    json.dump(dict(rows=rows, mix=mix, btc_today=btc, secs=time.time() - t0), open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print("done %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
