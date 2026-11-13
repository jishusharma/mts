"""Run the PRE_REG study: python run.py -> results.json. Two worker processes below-normal priority (+ this one idle = 3 processes)."""
import ctypes
import json
import multiprocessing as mp
import os
import sys
import time
import numpy as np
import study as S

HERE = os.path.dirname(os.path.abspath(__file__))
COSTS = {"12bp": 0.0012, "6bp": 0.0006}
BOOT = 2000
PLB = 200
PLB_N = 3000
NWORK = 2


def lower_priority():
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)   # BELOW_NORMAL
    except Exception:
        pass


# ----------------------------------------------------------------------------------------------- stats
def stats(x, day, rng, boot=BOOT, trade_ci=True):
    n = len(x)
    out = dict(n=int(n))
    if n == 0:
        return out
    out["win"] = float((x > 0).mean())
    out["mean"] = float(x.mean())
    if n < 2:
        return out
    if trade_ci:
        m = np.empty(boot)
        for b in range(boot):
            m[b] = x[rng.integers(0, n, n)].mean()
        out["ci_trade_lo"] = float(np.quantile(m, 0.025))
    ud, inv = np.unique(day, return_inverse=True)
    sums = np.bincount(inv, weights=x)
    cnt = np.bincount(inv).astype(float)
    D = len(ud)
    idx = rng.integers(0, D, (boot, D))
    md = sums[idx].sum(1) / cnt[idx].sum(1)
    out["ci_day_lo"] = float(np.quantile(md, 0.025))
    out["p_day"] = float((np.sum(md <= 0) + 1) / (boot + 1))
    top = np.argsort(-sums)[:5]
    rest_n = n - cnt[top].sum()
    out["ex5"] = float((x.sum() - sums[top].sum()) / rest_n) if rest_n > 0 else float("nan")
    out["days"] = int(D)
    return out


def bh(ps, q=0.05):
    ps = np.array(ps, dtype=float)
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


# ----------------------------------------------------------------------------------------------- pass 1: per coin
CYC = None


def init(cyc):
    global CYC
    lower_priority()
    CYC = cyc


def snapshot(B):
    n5 = B["n5"]
    nd = n5 // S.DAY5
    names = {0: "NA", 1: "UP", 2: "DOWN", 3: "RANGE"}
    last = n5 - 1
    r9 = {}
    for k, nm in ((1, "5m"), (6, "30m"), (288, "1d")):
        r, e, w = S.hm_lines(B["P"][k]["C"])
        r9[nm] = dict(rsi9=float(r[-1]), ema3=float(e[-1]), wma21=float(w[-1]), state=int(B["raw"][(0, k)][-1]))
    return dict(asof_bar_start_utc=str(np.datetime64(int(B["grid"][last]), "ms")), close=float(B["c"][last]),
                phase_today=names[int(B["ph_day"][nd])], cycle_today={0: "NA", 1: "BULL", 2: "BEAR"}[int(B["cyc"][last])],
                hm=r9, vwap_utc00=float(B["vw"]["U"][last]), vwap_ny1330=float(B["vw"]["N"][last]),
                prev_day_high=float(B["dH"][-1]), prev_day_low=float(B["dL"][-1]), atr14_5m=float(B["atr5"][last]),
                sma20_daily=float(np.mean(B["P"][288]["C"][-20:])))


def coin_job(sym):
    t0 = time.time()
    grid, o, h, l, c, v = S.load_grid(sym)
    B = S.prep(grid, o, h, l, c, v, CYC)
    tr = S.coin_trades(B)
    nd = B["n5"] // S.DAY5
    dts = grid[0] + np.arange(nd) * 86400000
    dv = dts >= S.VAL_START_MS
    ph = B["ph_day"][:nd]
    cy = B["cyc"][::S.DAY5][:nd]
    mix = {}
    for nm, sel in (("dev", ~dv), ("val", dv)):
        mix[nm] = np.zeros((4, 3), dtype=np.int64)
        for p in range(4):
            for k in range(3):
                mix[nm][p, k] = int(((ph == p) & (cy == k) & sel).sum())
        mix[nm] = mix[nm].tolist()
    os.makedirs(S.WORK, exist_ok=True)
    np.save(os.path.join(S.WORK, sym + "_ohl.npy"), np.stack([o, h, l]))
    np.save(os.path.join(S.WORK, sym + "_ph.npy"), B["ph"])
    np.save(os.path.join(S.WORK, sym + "_grid0.npy"), np.array([grid[0]]))
    snap = snapshot(B) if sym == "BTC" else None
    return sym, tr, mix, snap, B["n5"], time.time() - t0


# ----------------------------------------------------------------------------------------------- pass 2: placebo
_ARR = {}


def _coin_arrays(sym):
    if sym not in _ARR:
        ohl = np.load(os.path.join(S.WORK, sym + "_ohl.npy"), mmap_mode="r")
        ph = np.load(os.path.join(S.WORK, sym + "_ph.npy"), mmap_mode="r")
        g0 = int(np.load(os.path.join(S.WORK, sym + "_grid0.npy"))[0])
        _ARR[sym] = (np.asarray(ohl[0]), np.asarray(ohl[1]), np.asarray(ohl[2]), np.asarray(ph), g0)
    return _ARR[sym]


def placebo_job(args):
    key, phase, coins, d, held, sfrac, greal, seed = args
    lower_priority()
    rng = np.random.default_rng(seed)
    sumg = np.zeros(PLB)
    N = len(d)
    for ci in np.unique(coins):
        sel = coins == ci
        o, h, l, phb, g0 = _coin_arrays(S.COINS[ci])
        n5 = len(o)
        vidx = int((S.VAL_START_MS - g0) // S.MS5)
        hmax = int(held[sel].max())
        pool = np.flatnonzero(phb == phase)
        pool = pool[(pool >= max(vidx, 2)) & (pool < n5 - 2 - hmax)]
        if len(pool) == 0:
            return key, None
        dd, hh, sf = np.tile(d[sel], PLB), np.tile(held[sel], PLB), np.tile(sfrac[sel], PLB)
        draw = np.repeat(np.arange(PLB), sel.sum())
        e2 = pool[rng.integers(0, len(pool), len(dd))]
        Sd = sf * o[e2]
        g, _, _ = S.sim(o, h, l, e2, dd, Sd, hh)
        sumg += np.bincount(draw, weights=g, minlength=PLB)
    pm = sumg / N
    real = float(greal.mean())
    return key, dict(real_gross=real, placebo_gross_mean=float(pm.mean()), p=float((np.sum(pm >= real) + 1) / (PLB + 1)), n_sub=int(N))


# ----------------------------------------------------------------------------------------------- main
def concat(parts):
    keys = [k for k in parts[0] if k != "coin"]
    out = {k: np.concatenate([p[k] for p in parts]) for k in keys}
    out["coin"] = np.concatenate([np.full(len(p["e"]), i, dtype=np.int64) for i, p in enumerate(parts)])
    return out


def main():
    t0 = time.time()
    lower_priority()
    a = np.load(os.path.join(S.CACHE, "BTCUSDT_1d.npz"))["a"]
    day0, flag, full, sma = S.cycle_by_day(a[:, 0].astype(np.int64), a[:, 4])
    cyc = (day0, flag)
    btc_cycle = dict(last_close_1d=float(full[-1]), sma_200w=float(sma[-1]), ratio=float(full[-1] / sma[-1]) if not np.isnan(sma[-1]) else None,
                     first_flag_day_utc=str(np.datetime64(int(day0 + np.flatnonzero(flag[1:] > 0)[0]), "D")), last_day_utc=str(np.datetime64(int(day0 + len(full) - 1), "D")))
    with mp.Pool(NWORK, initializer=init, initargs=(cyc,)) as pool:
        res = []
        for r in pool.imap(coin_job, S.COINS):
            res.append(r)
            print(r[0], r[4], "%.0fs" % r[5], flush=True)
    mix = {r[0]: dict(dev=r[2]["dev"], val=r[2]["val"]) for r in res}
    snap = [r[3] for r in res if r[3]][0]
    V = S.variants()
    T = {v["id"]: concat([r[1][v["id"]] for r in res]) for v in V}
    print("pass1 %.0fs" % (time.time() - t0), flush=True)
    rng = np.random.default_rng(7)
    rows = []
    jobs = []
    for vi, v in enumerate(V):
        t = T[v["id"]]
        val = t["ts"] >= S.VAL_START_MS
        x12 = t["g"] - COSTS["12bp"] * t["costu"]
        x6 = t["g"] - COSTS["6bp"] * t["costu"]
        for cut, vals, names in (("daily_phase", (1, 2, 3), S.PHASES), ("cycle", (1, 2), {1: "BULL", 2: "BEAR"})):
            arr = t["ph"] if cut == "daily_phase" else t["cyc"]
            for pv in vals:
                sel = val & (arr == pv)
                dsel = ~val & (arr == pv)
                st = stats(x12[sel], t["day"][sel], rng, BOOT, trade_ci=True) if cut == "daily_phase" else stats(x12[sel], t["day"][sel], rng, 500, trade_ci=False)
                st6 = stats(x6[sel], t["day"][sel], rng, 500, trade_ci=False) if sel.sum() > 1 else dict(n=int(sel.sum()))
                row = dict(vid=v["id"], part=v["part"], cut=cut, phase=names[pv], val=st, val6=dict(mean=st6.get("mean"), ci_day_lo=st6.get("ci_day_lo")),
                           dev=dict(n=int(dsel.sum()), mean=float(x12[dsel].mean()) if dsel.any() else None, win=float((x12[dsel] > 0).mean()) if dsel.any() else None),
                           fee_R_med=float(np.median(COSTS["12bp"] * t["costu"][sel])) if sel.any() else None,
                           hold_h_med=float(np.median(t["held"][sel]) * 5 / 60) if sel.any() else None)
                for dn, dv_ in (("long", 1), ("short", -1)):
                    s2 = sel & (t["d"] == dv_)
                    row[dn] = dict(n=int(s2.sum()), mean=float(x12[s2].mean()) if s2.any() else None)
                rows.append(row)
                if cut == "daily_phase" and st["n"] >= 100 and st["mean"] > 0:
                    ii = np.flatnonzero(sel)
                    if len(ii) > PLB_N:
                        ii = np.sort(rng.choice(ii, PLB_N, replace=False))
                    jobs.append(((v["id"], pv), pv, t["coin"][ii], t["d"][ii], t["held"][ii], t["sfrac"][ii], t["g"][ii], 1000 + 31 * vi + pv))
    print("stats done %.0fs, placebo jobs %d" % (time.time() - t0, len(jobs)), flush=True)
    pl = {}
    with mp.Pool(NWORK, initializer=init, initargs=(cyc,)) as pool:
        for k, r in pool.imap_unordered(placebo_job, jobs):
            pl[k] = r
    inv = {1: "UP", 2: "DOWN", 3: "RANGE"}
    gated = [r for r in rows if r["cut"] == "daily_phase"]
    ps = [r["val"].get("p_day", 1.0) if r["val"]["n"] >= 100 else 1.0 for r in gated]
    ok = bh(ps)
    for r, o in zip(gated, ok):
        r["bh_pass"] = bool(o)
        k = (r["vid"], {"UP": 1, "DOWN": 2, "RANGE": 3}[r["phase"]])
        r["placebo"] = pl.get(k)
        v = r["val"]
        if v["n"] >= 100 and "ci_day_lo" in v:
            g = dict(n100=True, mean_pos=v["mean"] > 0, ci_trade=v.get("ci_trade_lo", -1) > 0, ci_day=v["ci_day_lo"] > 0,
                     placebo=bool(r["placebo"] and r["placebo"]["p"] < 0.05), bh=bool(o), ex5=v["ex5"] > 0)
            g["PASS"] = all(g.values())
            r["gates"] = g
        else:
            r["gates"] = dict(n100=False, PASS=False)
    out = dict(rows=rows, mix=mix, btc_today=snap, btc_cycle=btc_cycle, m_family=len(gated), n_pass=int(sum(1 for r in gated if r["gates"].get("PASS"))),
               variants=V, secs=time.time() - t0)
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("done %.0fs; PASS rows %d of %d" % (time.time() - t0, out["n_pass"], len(gated)))


if __name__ == "__main__":
    mp.freeze_support()
    main()
