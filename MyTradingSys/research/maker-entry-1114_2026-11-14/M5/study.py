"""M5 (maker-entry-1114): NY prior-session value area, POC target, best cell = balanced / stop A (session extreme) / SHORT,
pooled over the 10 new coins. Signals are exactly edge5-ny-value-poc-target-1113 (orig_study5.py / parent_study.py are copies);
only the entry changes: resting limit at the value-area edge the rule re-entered through (VAH for short, VAL for long).
Usage: python -I study.py   (hold a maker slot while it runs)"""
import sys, json, datetime as dt
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import parent_study as ps          # noqa: E402  (copy of the original parent code)
import orig_study5 as s5           # noqa: E402  (copy of the original study5 code)
import maker_fill as mf            # noqa: E402

ORIG = r"F:\MTS\data_cache\moved_from_worktrees\mts-jis-nb-edge5-ny-value-poc-target-1113-2\runtime_data\edge5-ny-value-poc"
SYMS = s5.NEW
SIDE = -1                        # best cell: SHORT
TF_MS = 30 * 60_000              # entry timeframe = 30m block
SPLIT = ps.SPLIT_MS
N_DRAWS = 1000


# ------------------------------------------------------------------ signal -> limit mapping (the only new logic)
def limit_level(ev):
    """Value-area edge the rule re-entered through: VAH for a short, VAL for a long (OURS mapping, SOURCED rule)."""
    return float(ev["vah"]) if ev["side"] == -1 else float(ev["val"])


def maker_signal(ev, ei, t_sig_ms, m1, tick, s1_ms, **kw):
    """Maker outcome for one original signal. ev['H'/'C'] session arrays, ei = 1m index (in session) of the signal bar,
    t_sig_ms = open time of the signal bar. Order is placed at the signal bar close (= t_sig_ms + 60000)."""
    side = ev["side"]
    stop = s5.stop_for("A", side, ev, ei)
    return mf.simulate_maker(side, limit_level(ev), stop, float(ev["poc"]), t_sig_ms + 60_000, TF_MS, s1_ms, False, m1,
                             tick=tick, **kw)


def base_trade(ev, ei):
    """ORIGINAL taker model (entry at the signal close, 12 bp) for stop A; None if the original guard fails."""
    H, L, C, side, poc = ev["H"], ev["L"], ev["C"], ev["side"], ev["poc"]
    entry = float(C[ei])
    stop = s5.stop_for("A", side, ev, ei)
    if abs(stop - entry) / entry < ps.MIN_STOP:
        return None
    ex, kind, reach, _ = ps.sim_trade(side, ei, poc, stop, H, L, C)
    g, n = s5.gross_net(side, entry, ex, stop)
    return dict(G=g, R=n, kind=kind)


def atr30(bars, g):
    """30m ATR14 = mean 30m high-low of the 14 back-to-back 30m windows ending at 1m global index g."""
    h, l = bars[2], bars[3]
    if g < 420:
        return float("nan")
    hh = h[g - 419:g + 1].reshape(14, 30).max(1)
    ll = l[g - 419:g + 1].reshape(14, 30).min(1)
    return float((hh - ll).mean())


# ------------------------------------------------------------------ data pass
def collect_sym(sym):
    import pickle
    cache = Path(r"F:\MTS\maker_cache\M5") / f"{sym}.pkl"
    if cache.exists():
        return pickle.loads(cache.read_bytes())
    sigs, cand_sessions = [], []
    for sym in [sym]:
        ev_list, n_sess, bars, sess = ps.day_events(sym, ORIG)
        t = bars[0]
        m1 = mf.load_m1(sym)
        tick = mf.estimate_tick(m1)
        for ev in ev_list:
            if ev["side"] != SIDE or not ev["balanced"]:
                continue
            ei, skipped = s5.setups(ev)
            if ei is None or skipped:
                continue
            b = base_trade(ev, ei)
            if b is None:
                continue
            s0, s1 = ps.ac.ny_session_window(dt.date.fromisoformat(ev["date"]))
            g = ev["i0"] + ei
            t_sig = int(t[g])
            L = limit_level(ev)
            rec = dict(sym=sym, date=ev["date"], ms=ev["ms"], t_sig=t_sig, ei=ei, G=b["G"], R=b["R"], kind=b["kind"],
                       L=L, close=float(ev["C"][ei]), atr=atr30(bars, g), balanced=True, stype="A", side=SIDE)
            rec["maker"] = maker_signal(ev, ei, t_sig, m1, tick, int(s1))
            rec["risk_bp_from_L"] = 1e4 * (float(s5.stop_for("A", SIDE, ev, ei)) - L) / L
            sigs.append(rec)
            if ev["ms"] >= SPLIT:
                ks, cl, stp, at = [], [], [], []
                runext = np.maximum.accumulate(ev["H"]) * (1 + ps.BUF_FRAC)
                C = ev["C"]
                for k in range(s5.FIRST_ENTRY_BAR, len(C) - 1):
                    if not (ev["val"] <= C[k] <= ev["vah"]) or not s5.tgt_ok(SIDE, float(C[k]), ev["poc"]):
                        continue
                    if abs(runext[k] - C[k]) / C[k] < ps.MIN_STOP:
                        continue
                    a = atr30(bars, ev["i0"] + k)
                    if not a > 0:
                        continue
                    ks.append(k); cl.append(float(C[k])); stp.append(float(runext[k])); at.append(a)
                if ks:
                    cand_sessions.append(dict(sym=sym, poc=float(ev["poc"]), s1=int(s1), ks=np.array(ks),
                                              close=np.array(cl), stop=np.array(stp), atr=np.array(at), tick=tick,
                                              tg=t[ev["i0"]:ev["i1"]]))
        print(sym, "signals", len(sigs), flush=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(pickle.dumps((sigs, cand_sessions)))
    return sigs, cand_sessions


def collect():
    from multiprocessing import Pool
    with Pool(3) as pool:
        parts = pool.map(collect_sym, SYMS, chunksize=1)
    sigs, cands = [], []
    for sg, cs in parts:
        sigs += sg
        cands += cs
    m1s = {}
    for c in cands:
        if c["sym"] not in m1s:
            m1s[c["sym"]] = mf.load_m1(c["sym"])
        c["m1"] = m1s[c["sym"]]
    return sigs, cands


def placebo(sigs_val, cands, observed, n_filled):
    offs = mf.signal_offsets_atr(np.full(len(sigs_val), SIDE), [s["L"] for s in sigs_val], [s["close"] for s in sigs_val],
                                 [s["atr"] for s in sigs_val])
    offs = offs[np.isfinite(offs)]
    rng = np.random.default_rng(11)

    def run_one(c, off):
        j = int(rng.integers(0, len(c["ks"])))
        close, stop, atr = c["close"][j], c["stop"][j], c["atr"][j]
        L = mf.placebo_limit(SIDE, close, atr, off)
        if not (stop > L and c["poc"] < L):
            return dict(filled=False, net_R=0.0)
        t_sig = int(c["tg"][int(c["ks"][j])])
        return mf.simulate_maker(SIDE, L, stop, c["poc"], t_sig + 60_000, TF_MS, c["s1"], False, c["m1"], tick=c["tick"])
    return mf.placebo_pvalue(observed, run_one, cands, offs, n_filled, n_draws=N_DRAWS, seed=7)


def split_stats(sig):
    mk = [dict(s["maker"], day=(int(s["maker"]["fill_ms"] // 86400000) if s["maker"]["filled"] else int(s["t_sig"] // 86400000)))
          for s in sig]
    summ = mf.summarize(mk)
    fl = [s for s in sig if s["maker"]["filled"]]
    out = dict(summary=summ)
    out["taker_baseline_net_all"] = float(np.mean([s["R"] for s in sig])) if sig else None
    out["taker_baseline_gross_all"] = float(np.mean([s["G"] for s in sig])) if sig else None
    out["orig_gross_filled_subset"] = float(np.mean([s["G"] for s in fl])) if fl else None
    out["orig_net_taker_filled_subset"] = float(np.mean([s["R"] for s in fl])) if fl else None
    out["adverse_selection_R"] = (out["orig_gross_filled_subset"] - out["taker_baseline_gross_all"]) if fl else None
    out["exit_types"] = {k: sum(1 for s in fl if s["maker"]["exit_type"] == k) for k in ("target", "stop", "time", "data_end")}
    out["miss_reasons"] = {k: sum(1 for s in sig if s["maker"]["reason_missed"] == k) for k in ("no_through", "stop_before_fill", "no_data")}
    out["median_risk_bp_from_L"] = float(np.median([s["risk_bp_from_L"] for s in sig])) if sig else None
    return out


def main():
    sigs, cands = collect()
    dev = [s for s in sigs if s["ms"] < SPLIT]
    val = [s for s in sigs if s["ms"] >= SPLIT]
    out = dict(cell="balanced/stopA/short, 10 new coins", baseline_all_period=dict(
        n=len(sigs), gross=float(np.mean([s["G"] for s in sigs])), net=float(np.mean([s["R"] for s in sigs])),
        orig_result=dict(n=370, gross=0.077, net=-0.006)))
    out["DEV"], out["VAL"] = split_stats(dev), split_stats(val)
    sv = out["VAL"]["summary"]
    if sv["n_filled"] > 0:
        p, draws = placebo(val, cands, sv["mean_net_R_filled"], sv["n_filled"])
        out["placebo_p"], out["placebo_mean"], out["placebo_p95"] = p, float(draws.mean()), float(np.percentile(draws, 95))
    else:
        out["placebo_p"] = None
    rej, adj = mf.benjamini_hochberg([out["placebo_p"] if out["placebo_p"] is not None else 1.0] + [1.0] * 5)
    out["bh_provisional_only_M5_p_known"] = dict(reject=rej[0], adj_p=adj[0])
    out["gates"] = mf.gates(sv, out["placebo_p"], rej[0])
    out["regime"] = s5.regime(ORIG, sigs)
    out["trade_log_VAL"] = [dict(sym=s["sym"], date=s["date"], filled=s["maker"]["filled"], net_R=s["maker"]["net_R"],
                                 exit=s["maker"]["exit_type"], taker_R=s["R"]) for s in val]
    (HERE / "results.json").write_text(json.dumps(out, indent=1, default=float), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "trade_log_VAL"}, indent=1, default=float))


if __name__ == "__main__":
    main()
