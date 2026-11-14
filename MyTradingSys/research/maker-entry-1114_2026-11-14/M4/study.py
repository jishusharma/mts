"""M4 maker-entry study: NK5 session open, NY-asia row (hold to 08:00 UTC). See ../PRE_REG.md.
Signal rule, phase gate, stop/hold machinery = original nk5_orig.py (verbatim copy; RSI 35/65 band as the CODE, not the
30/70 in the RESULT text). Only mapping added here: limit L = close of the signal bar (the bar that closes at the
anchor T = last bar closed at or before T); order life 15 x 1m (entry timeframe = 15m, OURS); stop = L -/+ max(0.5% L,
0.6 x ATR14 1h) (original formula with entry := L); no target; time stop = open of the 1m bar at 08:00 UTC next day.
STUDY_BUG=1 -> naive variant used only by test_study.py (L = next open at T, and the signal bar itself may fill)."""
import os, sys, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import nk5_orig as O          # noqa: E402
import maker_fill as mf       # noqa: E402

SPLIT = O.SPLIT
ROW = "NY-asia"
TF_MS = 15 * 60000
FIVE = pd.Timedelta(minutes=5)


def bug():
    return os.environ.get("STUDY_BUG") == "1"


def build_order(sd, T_ms, close_prev, open_T, a1, E_ms):
    """Signal -> limit mapping. close_prev = close of the signal bar (bar closing at T)."""
    L = float(open_T if bug() else close_prev)
    S = max(0.005 * L, 0.6 * float(a1))
    stop = L - sd * S
    sc = T_ms - (TF_MS if bug() else 0)
    return dict(side=sd, L=L, stop=stop, signal_close_ms=float(sc), tf_ms=TF_MS, time_stop_ms=float(E_ms))


def run_order(o, m1, tick=None):
    return mf.simulate_maker(o["side"], o["L"], o["stop"], None, o["signal_close_ms"], o["tf_ms"], o["time_stop_ms"],
                             False, m1, tick=tick)


def coin_frame(sym):
    """All NY anchors of the coin (any signal state), row NY-asia: original taker gross + maker-order inputs."""
    df5 = O.prep(O.load5(sym))
    orig = O.coin_candidates(sym, df5=df5)
    orig = orig[orig.row == ROW].copy()
    if orig.empty:
        return orig
    sg = O.signals(df5)
    c5, o5 = df5.c, df5.o
    cprev, oT, a1, E = [], [], [], []
    for T in orig["T"]:
        cprev.append(c5.get(T - FIVE, np.nan))
        oT.append(o5.get(T, np.nan))
        a1.append(sg["atr1"].get(T.floor("1h") - pd.Timedelta(hours=1), np.nan))
        E.append(T.normalize() + pd.Timedelta(days=1, hours=8))
    orig["close_prev"], orig["open_T"], orig["a1"] = cprev, oT, a1
    orig["T_ms"] = orig["T"].map(lambda x: x.value // 10**6).astype(float)
    orig["E_ms"] = [float(e.value // 10**6) for e in E]
    orig["daynum"] = orig["day"].map(lambda x: x.value // (86400 * 10**9)).astype(int)
    return orig.dropna(subset=["close_prev", "a1"])


def matched_side(sigL, sigS, phase):
    """+1 long / -1 short / 0 none: matched-direction signal (LONG in UP/RANGE, SHORT in DOWN/RANGE)."""
    if sigL and phase in (1, 0):
        return 1
    if sigS and phase in (-1, 0):
        return -1
    return 0


def simulate_frame(F, m1, tick, sides):
    res = []
    for r, sd in zip(F.itertuples(index=False), sides):
        o = build_order(int(sd), r.T_ms, r.close_prev, r.open_T, r.a1, r.E_ms)
        x = run_order(o, m1, tick)
        x["day"] = int(r.daynum)
        x["signal_close_ms"] = r.T_ms
        res.append(x)
    return res


def taker_net(F, sides, fee_bp=12.0):
    """ORIGINAL taker baseline per signal (next-open entry, original gl/gs, 12 bp)."""
    fee = fee_bp / 1e4
    g = np.where(np.asarray(sides) > 0, F.gl.to_numpy(), F.gs.to_numpy())
    return (g - fee) / F.S.to_numpy(), g / F.S.to_numpy()


def indep_gross_check(F, m1, sides, n=400, seed=3):
    """Independent recomputation of taker gross R from the 1m file (entry = 1m open at T, stop = 1m touch of
    entry -/+ S, exit = open of 1m at 08:00 UTC) vs original 5m result."""
    t, o, h, l = m1["t_ms"], m1["o"], m1["h"], m1["l"]
    idx = np.random.default_rng(seed).permutation(len(F))[:n]
    a, b = [], []
    for k in idx:
        r = F.iloc[k]
        sd = sides[k]
        i0 = int(np.searchsorted(t, r.T_ms))
        i1 = int(np.searchsorted(t, r.E_ms))
        if i1 >= len(t) or i0 >= len(t) or t[i0] != r.T_ms or t[i1] != r.E_ms:
            continue
        e = o[i0]
        S = r.S * e
        if sd > 0:
            g = -S if l[i0:i1].min() <= e - S else o[i1] - e
        else:
            g = -S if h[i0:i1].max() >= e + S else e - o[i1]
        a.append((r.gl if sd > 0 else r.gs) / r.S)
        b.append(g / S)
    a, b = np.array(a), np.array(b)
    return [float(a.mean()), float(b.mean()), float(np.abs(a - b).mean()), int(len(a))] if len(a) else [None] * 3 + [0]


def regime_mix(F):
    out = {}
    for name, m in (("DEV", F["T"] < SPLIT), ("VAL", F["T"] >= SPLIT)):
        out[name] = F[m].phase.map({1: "UP", -1: "DOWN", 0: "RANGE"}).value_counts(normalize=True).round(3).to_dict()
    return out


def main():
    import ctypes
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass
    sigs, pools, m1s, indep, anch = [], [], {}, {}, []
    for s in O.SYMS:
        if not os.path.exists(rf"F:\MTS\data_cache\binance_1m\{s}USDT_1m.npz"):
            print("missing 1m", s, flush=True)
            continue
        F = coin_frame(s).reset_index(drop=True)
        if F.empty:
            continue
        m1 = mf.load_m1(s + "USDT")
        tick = mf.estimate_tick(m1)
        m1s[s] = (m1, tick)
        F["sym"] = s
        F["side"] = [matched_side(a, b, c) for a, b, c in zip(F.sigL, F.sigS, F.phase)]
        Fs = F[F.side != 0].reset_index(drop=True)
        Fs["res"] = simulate_frame(Fs, m1, tick, Fs.side.to_numpy())
        Fs["taker_net"], Fs["taker_gross"] = taker_net(Fs, Fs.side.to_numpy())
        indep[s] = indep_gross_check(Fs, m1, Fs.side.to_numpy())
        pl = []
        for sd in (1, -1):
            ok = F.phase.isin([1, 0]) if sd > 0 else F.phase.isin([-1, 0])
            pl.append(F[ok & (F["T"] >= SPLIT)].assign(pside=sd))
        pools.append(pd.concat(pl))
        anch.append(F[["T", "phase"]])
        sigs.append(Fs)
        print(s, "anchors", len(F), "signals", len(Fs), "filled", sum(r["filled"] for r in Fs["res"]), "tick", tick, flush=True)
    allF = pd.concat(sigs, ignore_index=True)
    allP = pd.concat(pools, ignore_index=True)
    out = dict(spec="M4 NK5 NY-asia maker", rsi_band_used="35/65 (code); the original RESULT text said 30/70",
               order_life="15 x 1m", L="close of signal bar (bar closing at anchor T)")
    for period in ("DEV", "VAL"):
        m = allF["T"] < SPLIT if period == "DEV" else allF["T"] >= SPLIT
        d = allF[m]
        res = list(d["res"])
        sm = mf.summarize(res)
        fl = np.array([r["filled"] for r in res])
        out[period] = dict(summary=sm, n_taker=int(len(d)), taker_mean_net_R_all=float(d.taker_net.mean()),
                           taker_mean_net_R_filled_subset=float(d.taker_net[fl].mean()) if fl.any() else None,
                           taker_gross_all=float(d.taker_gross.mean()),
                           taker_gross_filled_subset=float(d.taker_gross[fl].mean()) if fl.any() else None,
                           maker_gross_filled=sm["mean_gross_R_filled"],
                           maker_fee_R_filled=sm["mean_fee_R_filled"],
                           exit_types={k: int(v) for k, v in pd.Series([r["exit_type"] for r in res if r["filled"]]).value_counts().items()},
                           miss_reasons={str(k): int(v) for k, v in pd.Series([r["reason_missed"] for r in res if not r["filled"]]).value_counts().items()})
    V = allF[allF["T"] >= SPLIT]
    obs = out["VAL"]["summary"]["mean_net_R_filled"]
    nf = out["VAL"]["summary"]["n_filled"]
    rng = np.random.default_rng(7)
    idx_by = {k: g.index.to_numpy() for k, g in allP.groupby(["sym", "pside"])}
    cnt = V.groupby(["sym", "side"]).size()
    cand = np.concatenate([rng.choice(idx_by[(s, sd)], max(1, int(round(20000 * k / cnt.sum()))))
                           for (s, sd), k in cnt.items() if (s, sd) in idx_by])
    memo = {}
    offs = mf.signal_offsets_atr(V.side.to_numpy(), V.close_prev.to_numpy(), V.close_prev.to_numpy(), V.a1.to_numpy())
    out["placebo_offsets_unique"] = sorted(set(np.round(offs, 12).tolist()))

    def run_one(ci, off):
        key = (int(ci), off)
        if key not in memo:
            r = allP.loc[int(ci)]
            m1, tick = m1s[r.sym]
            sd = int(r.pside)
            L = mf.placebo_limit(sd, float(r.close_prev), float(r.a1), off)
            S = max(0.005 * L, 0.6 * float(r.a1))
            x = mf.simulate_maker(sd, L, L - sd * S, None, float(r.T_ms), TF_MS, float(r.E_ms), False, m1, tick=tick)
            x["day"] = int(r.daynum)
            memo[key] = x
        return memo[key]
    p, draws = mf.placebo_pvalue(obs, run_one, list(cand), offs, nf, n_draws=1000, seed=7)
    out["placebo_p"] = p
    out["placebo_draw_mean"] = float(draws.mean())
    out["placebo_pool_fill_rate"] = float(np.mean([v["filled"] for v in memo.values()]))
    rej, adj = mf.benjamini_hochberg([p, 1, 1, 1, 1, 1])
    out["gates"] = mf.gates(out["VAL"]["summary"], p, rej[0])
    out["gate5_note"] = "BH needs the other 5 rows' p; provisional best case (others p=1): passes only if p*6<=0.05"
    out["regime_mix_coin_anchor_days"] = regime_mix(pd.concat(anch))
    out["regime_trades_VAL"] = {str(k): int(v) for k, v in V.phase.map({1: "UP", -1: "DOWN", 0: "RANGE"}).value_counts().items()}
    out["sides_VAL"] = {str(k): int(v) for k, v in V.side.value_counts().items()}
    out["indep_gross_check_[orig_mean,1m_mean,mean_abs_diff,n]"] = indep
    json.dump(out, open(os.path.join(HERE, "results.json"), "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
