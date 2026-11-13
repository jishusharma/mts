"""Run the pre-registered study; writes results.json and RESULT.md. Usage: python run.py"""
import json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import study

HERE = os.path.dirname(os.path.abspath(__file__))
VAL_DAY = int(np.datetime64("2024-01-01").astype("datetime64[D]").astype(int))
B = 2000; BP = 1000
rng = np.random.default_rng(20261114)
FEES = {"12bp": 12.0, "6bp": 6.0}


def boot_trade(r):
    n = len(r); out = np.empty(B)
    for s in range(0, B, 250):
        e = min(B, s + 250); ix = rng.integers(0, n, (e - s, n)); out[s:e] = r[ix].mean(1)
    return out


def boot_day(r, days):
    ud, inv = np.unique(days, return_inverse=True)
    sums = np.bincount(inv, weights=r); cnt = np.bincount(inv).astype(float)
    ix = rng.integers(0, len(ud), (B, len(ud)))
    return sums[ix].sum(1) / cnt[ix].sum(1), (ud, sums)


def stats(r, days, pools, groups, dev_r):
    n = len(r)
    o = dict(n=int(n), dev_n=int(len(dev_r)), dev_mean=float(dev_r.mean()) if len(dev_r) else None)
    if n == 0: return o
    o["win"] = float((r > 0).mean()); o["mean"] = float(r.mean())
    bt = boot_trade(r); bd, (ud, sums) = boot_day(r, days)
    o["ci_trade_lo"] = float(np.percentile(bt, 2.5)); o["ci_day_lo"] = float(np.percentile(bd, 2.5))
    o["p_day"] = float((np.sum(bd <= 0) + 1) / (B + 1))
    tot = np.zeros(BP)
    for key, ng in groups.items():
        pool = pools[key]
        if len(pool) == 0: continue
        tot += pool[rng.integers(0, len(pool), (BP, ng))].sum(1)
    pm = tot / n
    o["placebo_mean"] = float(pm.mean()); o["placebo_p"] = float((np.sum(pm >= r.mean()) + 1) / (BP + 1))
    best = np.argsort(sums)[-5:]
    keep = ~np.isin(days, ud[best])
    o["ex_best5"] = float(r[keep].mean()) if keep.sum() else None
    return o


def main():
    t0 = time.time()
    names = None; T = {}      # (combo, kind, fee) accumulators
    rows = {}                 # (combo, kind) -> dict of lists
    pools = {}                # (fee, coin, dir) -> val net pool
    mix = {"DEV": np.zeros(3), "VAL": np.zeros(3)}
    last = {}
    for sym in study.SYMS:
        D, F, out = study.build_coin(sym)
        dayn = (D["ts"] // 86400000).astype(int)
        ph = F["phase"]; val = dayn >= VAL_DAY
        for nm_, msk in (("DEV", ~val), ("VAL", val)):
            for k, p in enumerate((1.0, 0.0, -1.0)): mix[nm_][k] += np.sum(msk & (ph == p))
        for dirn in (1, -1):
            o = out[dirn]
            for fee, bp in FEES.items():
                net = o["gross"] - bp * o["feeR"]
                pools[(fee, sym, dirn)] = net[o["prim"] & val]
            for (nm, kind), ix in o["trades"].items():
                rows.setdefault((nm, kind), []).append(dict(
                    coin=sym, dirn=dirn, day=dayn[ix], gross=o["gross"][ix], feeR=o["feeR"][ix], ph=ph[ix]))
        if sym == "BTC": last = dict(D=D, F=F)
        print(sym, round(time.time() - t0), flush=True)
    res = {}
    for (nm, kind), lst in rows.items():
        day = np.concatenate([x["day"] for x in lst]); g = np.concatenate([x["gross"] for x in lst])
        fR = np.concatenate([x["feeR"] for x in lst]); ph = np.concatenate([x["ph"] for x in lst])
        v = day >= VAL_DAY
        for fee, bp in FEES.items():
            net = g - bp * fR
            groups = {(fee, x["coin"], x["dirn"]): int((x["day"] >= VAL_DAY).sum()) for x in lst if (x["day"] >= VAL_DAY).sum() > 0}
            if kind == "prim":
                s = stats(net[v], day[v], pools, groups, net[~v])
            else:
                s = dict(n=int(v.sum()), dev_n=int((~v).sum()), mean=float(net[v].mean()) if v.any() else None,
                         dev_mean=float(net[~v].mean()) if (~v).any() else None)
            s["fee_R"] = float(np.mean(bp * fR[v])) if v.any() else None
            s["gross_mean"] = float(g[v].mean()) if v.any() else None
            s["val_phase_share"] = [float((ph[v] == p).mean()) if v.any() else None for p in (1.0, 0.0, -1.0)]
            res[f"{nm}|{kind}|{fee}"] = s
    # BH over primary rows (both fees)
    keys = [k for k in res if "|prim|" in k]
    p = np.array([res[k].get("p_day", 1.0) for k in keys]); m = len(p)
    order = np.argsort(p); q = np.empty(m); prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]; prev = min(prev, p[i] * m / rank); q[i] = prev
    for k, qq in zip(keys, q): res[k]["bh_q"] = float(qq)
    for k in keys:
        s = res[k]
        s["pass"] = bool(s["n"] >= 100 and s["mean"] > 0 and s["ci_trade_lo"] > 0 and s["ci_day_lo"] > 0 and s["placebo_p"] < 0.05
                         and s["bh_q"] < 0.05 and s["ex_best5"] is not None and s["ex_best5"] > 0)
    # BTC today
    D, F = last["D"], last["F"]; i = len(D["c"]) - 1
    dd = F["dd"]
    today = dict(last_bar_utc=str(np.datetime64(int(D["ts"][i]), "ms")), close=float(D["c"][i]),
                 phase_next_day=float(("UP" if (dd["adx"][-1] >= 20 and dd["pdi"][-1] > dd["mdi"][-1] and dd["sma"][-1] > dd["sma"][-6]) else "DOWN" if (dd["adx"][-1] >= 20 and dd["mdi"][-1] > dd["pdi"][-1] and dd["sma"][-1] < dd["sma"][-6]) else "RANGE") == "x") if False else 0,
                 phase_label=("UP" if (dd["adx"][-1] >= 20 and dd["pdi"][-1] > dd["mdi"][-1] and dd["sma"][-1] > dd["sma"][-6]) else "DOWN" if (dd["adx"][-1] >= 20 and dd["mdi"][-1] > dd["pdi"][-1] and dd["sma"][-1] < dd["sma"][-6]) else "RANGE"),
                 adx=float(dd["adx"][-1]), pdi=float(dd["pdi"][-1]), mdi=float(dd["mdi"][-1]), sma20=float(dd["sma"][-1]),
                 yday_hlc=[float(dd["dh"][-1]), float(dd["dl"][-1]), float(dd["dc"][-1])],
                 vwap=float(F["vwap"][i]), active_long=F["long"][:, i].tolist(), active_short=F["short"][:, i].tolist())
    ph_, h_, l_ = today["yday_hlc"][2], today["yday_hlc"][0], today["yday_hlc"][1]
    Pv = (h_ + l_ + ph_) / 3; today["pivots_from_last_day"] = dict(P=Pv, R1=2 * Pv - l_, S1=2 * Pv - h_)
    out = dict(res=res, mix={k: v.tolist() for k, v in mix.items()}, today=today, seconds=time.time() - t0)
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    print("done", round(time.time() - t0))


if __name__ == "__main__":
    main()
