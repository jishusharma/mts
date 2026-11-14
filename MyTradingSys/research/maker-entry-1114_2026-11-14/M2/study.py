"""M2: NK3 fakeout fade (type B), 1h, X1 (2R target, +24 bar time exit), no blast filter, phase-fit direction.
Maker entry: limit at the BROKEN (fakeout) level. Signals/phases/stop-distance rule exactly the original (orig_lib.py = copy of
nk3 lib.py); only the entry-level mapping is new. Usage: python study.py [--quick]"""
import ctypes, json, os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import orig_lib as lib
import maker_fill as mf

CACHE = r"F:\MTS\data_cache\binance_spot"
COINS = "BTC ETH BNB XRP ADA SOL DOGE LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL ALGO".split()
SPLIT = int(np.datetime64("2024-01-01").astype("datetime64[ms]").astype(np.int64))
TF = 3600000
TS_BARS = lib.H_X1 + 1  # time exit at close of bar e+24 = open of bar e+25
SLOTS = r"F:\MTS\maker_slots"


def load15(coin):
    z = np.load(os.path.join(CACHE, f"{coin}USDT_15m.npz"))
    return [z["ts" if "ts" in z.files else "t"]] + [z[k] for k in "o h l c v".split()]


def maker_params(s, h_i, l_i):
    """-> (side, L, stop, target, dist). L = broken level. Original rule: dist = max(nat, .6 ATR, .5% px),
    nat = breakout-candle extreme to entry; here entry = L."""
    d = s["dir"]
    L = s["lvl"]
    nat = (h_i - L) if d == -1 else (L - l_i)
    dist = max(nat, lib.MINATR * s["atr"], lib.MINPCT * L)
    return d, L, L - d * dist, L + d * lib.TGT_R * dist, dist


def build_symbol(coin):
    t, o, h, l, c, v = load15(coin)
    days, lab = lib.daily_phase_table(t, o, h, l, c, v)
    t, o, h, l, c, v = lib.resample(t, o, h, l, c, v, 4)
    ph = lib.phase_for_bars(t, days, lab)
    F = lib.features(t, o, h, l, c)
    S = [s for s in lib.signals(t, o, h, l, c, F, ph) if s["type"] == "B"]
    for s in S:
        s["lvl"] = float(F["H"][s["i"]] if s["dir"] == -1 else F["L"][s["i"]])
    return dict(t=t, o=o, h=h, l=l, c=c, ph=ph, F=F, S=S)


def taker_sim(B, S):
    """original taker X1 sim: {e: (gross R, exit idx, px, dist)}"""
    if not S:
        return {}
    idx = np.array([s["e"] for s in S]); px = np.array([s["px"] for s in S]); d = np.array([s["dir"] for s in S])
    dist = lib.stop_dist(np.array([s["nat"] for s in S]), np.array([s["atr"] for s in S]), px)
    g, ex = lib.sim(B["o"], B["h"], B["l"], B["c"], idx, px, d, dist, "X1", np.zeros(len(S), bool))
    return {int(i): (float(g_), int(e_), float(p_), float(di_)) for i, g_, e_, p_, di_ in zip(idx, g, ex, px, dist)}


def pick_orig(S, tk):
    """original one-position-per-coin cooldown (taker exits), phase-fit rows only."""
    keep, last = [], -1
    for s in sorted(S, key=lambda s: s["e"]):
        if s["fit"] == 1 and s["e"] > last:
            keep.append(s)
            last = tk[s["e"]][1]
    return keep


def run_maker(B, m1, tick, s):
    """one maker trade for signal s (signal bar = bar e = B+1; order placed at its close)."""
    side, L, stop, target, dist = maker_params(s, B["h"][s["i"]], B["l"][s["i"]])
    sig_close = float(B["t"][s["e"]] + TF)
    ts = float(B["t"][s["e"]] + TS_BARS * TF)
    r = mf.simulate_maker(side, L, stop, target, sig_close, TF, ts, False, m1, tick=tick)
    r["signal_close_ms"] = sig_close
    return r


def lower_priority():
    try:
        ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


def acquire_slot():
    os.makedirs(SLOTS, exist_ok=True)
    while True:
        for k in range(4):
            p = os.path.join(SLOTS, f"slot{k}")
            try:
                os.mkdir(p)
                return p
            except FileExistsError:
                pass
        time.sleep(20)


def main(quick=False):
    t0 = time.time()
    coins = COINS[:3] if quick else COINS
    real = {"DEV": [], "VAL": []}
    base = {"DEV": [], "VAL": []}
    gross_all = {"DEV": [], "VAL": []}
    gross_fill = {"DEV": [], "VAL": []}
    netbase_fill = {"DEV": [], "VAL": []}
    cells, offsets, pools, M1V, TICK, BARS, mix = [], [], {}, {}, {}, {}, {}
    for coin in coins:
        B = build_symbol(coin)
        m1 = mf.load_m1(coin + "USDT")
        tick = mf.estimate_tick(m1, use_cache=False)
        tk = taker_sim(B, B["S"])
        keep = pick_orig(B["S"], tk)
        for s in keep:
            g, ex, px, dist = tk[s["e"]]
            split = "VAL" if B["t"][s["e"]] >= SPLIT else "DEV"
            nR = g - 12 / 1e4 * px / dist
            r = run_maker(B, m1, tick, s)
            day = int(B["t"][s["e"]] // lib.DAY)
            r["day"] = int(r["fill_ms"] // lib.DAY) if r["filled"] else day
            r["coin"], r["split"], r["ph"] = coin, split, s["ph"]
            real[split].append(r)
            base[split].append(nR)
            gross_all[split].append(g)
            if r["filled"]:
                gross_fill[split].append(g)
                netbase_fill[split].append(nR)
            if split == "VAL":
                side, L, stop, target, dd = maker_params(s, B["h"][s["i"]], B["l"][s["i"]])
                offsets.append(float((B["c"][s["e"]] - L) * side / B["F"]["atr_prev"][s["e"]]))
                cells.append(dict(coin=coin, side=side, ph=s["ph"], dpct=dd / L))
        n = len(B["t"])
        valid = (B["t"] >= SPLIT) & (np.arange(n) >= 150) & (np.arange(n) < n - TS_BARS - 2)
        for p in (-1, 0, 1):
            pools[(coin, p)] = np.flatnonzero(valid & (B["ph"] == p))
        m = m1["t_ms"] >= SPLIT - 86400000
        M1V[coin] = {k: v[m] for k, v in m1.items()}
        TICK[coin] = tick
        BARS[coin] = dict(t=B["t"], c=B["c"], atr=B["F"]["atr_prev"])
        mix[coin] = {p: float((B["ph"][B["t"] >= SPLIT] == v).mean()) for p, v in (("UP", 1), ("DOWN", -1), ("RANGE", 0))}
        print(coin, len(B["S"]), "signals", f"{time.time()-t0:.0f}s tick={tick}", flush=True)
        del m1
    out = dict(coins=coins)
    for sp in ("DEV", "VAL"):
        a = np.array(base[sp])
        out[f"taker_{sp}"] = dict(n=len(a), mean_net12=float(a.mean()), gross=float(np.mean(gross_all[sp])))
    summ = {sp: mf.summarize(real[sp]) for sp in ("DEV", "VAL")}
    out["summary"] = {sp: {k: (list(v) if isinstance(v, tuple) else v) for k, v in summ[sp].items()} for sp in summ}
    for sp in ("DEV", "VAL"):
        s = out["summary"][sp]
        s["adverse_gross_orig_filled_minus_all"] = float(np.mean(gross_fill[sp]) - np.mean(gross_all[sp])) if gross_fill[sp] else None
        s["taker_net_R_filled_subset"] = float(np.mean(netbase_fill[sp])) if netbase_fill[sp] else None
        s["taker_net_R_all"] = out[f"taker_{sp}"]["mean_net12"]
        s["exit_types"] = {k: sum(1 for r in real[sp] if r["filled"] and r["exit_type"] == k) for k in ("stop", "target", "time", "data_end")}
        s["miss_reasons"] = {k: sum(1 for r in real[sp] if not r["filled"] and r["reason_missed"] == k) for k in ("no_through", "stop_before_fill", "no_data")}
        ph = {}
        for r in real[sp]:
            nm = {1: "UP", -1: "DOWN", 0: "RANGE"}[r["ph"]]
            ph[nm] = ph.get(nm, 0) + 1
        s["signals_by_phase"] = ph
    vs = summ["VAL"]
    ov = 0
    for coin in coins:
        last = -1
        for r in sorted([r for r in real["VAL"] if r["filled"] and r["coin"] == coin], key=lambda r: r["fill_ms"]):
            if r["fill_ms"] < last:
                ov += 1
            last = max(last, r["exit_ms"])
    out["summary"]["VAL"]["overlapping_maker_positions"] = ov
    rng = np.random.default_rng(11)
    nf = vs["n_filled"]
    if nf >= 20:
        def run_one(cell, off):
            pool = pools[(cell["coin"], cell["ph"])]
            j = int(pool[rng.integers(0, len(pool))])
            Bc = BARS[cell["coin"]]
            L = mf.placebo_limit(cell["side"], Bc["c"][j], Bc["atr"][j], off)
            dist = cell["dpct"] * L
            sd = cell["side"]
            return mf.simulate_maker(sd, L, L - sd * dist, L + sd * lib.TGT_R * dist, float(Bc["t"][j] + TF), TF,
                                     float(Bc["t"][j] + TS_BARS * TF), False, M1V[cell["coin"]], tick=TICK[cell["coin"]])
        cells = [c for c in cells if len(pools[(c["coin"], c["ph"])])]
        nd = 100 if quick else 1000
        p, draws = mf.placebo_pvalue(vs["mean_net_R_filled"], run_one, cells, offsets, nf, n_draws=nd, seed=7)
        out["placebo"] = dict(p=p, mean=float(draws.mean()), sd=float(draws.std()), n_draws=nd)
        rej, adj = mf.benjamini_hochberg([p] + [1.0] * 5)
        out["gates"] = mf.gates(vs, p, rej[0])
        out["gates"]["gate5_note"] = "BH computed with the other 5 rows' p set to 1 (worst case); lead must recompute over all 6"
    out["mix_val_by_coin"] = mix
    out["offsets_atr_summary"] = dict(mean=float(np.mean(offsets)), p10=float(np.percentile(offsets, 10)), p90=float(np.percentile(offsets, 90)))
    out["secs"] = time.time() - t0
    json.dump(out, open(os.path.join(HERE, "results_quick.json" if quick else "results.json"), "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("taker_DEV", "taker_VAL", "summary", "placebo", "gates") if k in out}, indent=1, default=float))


if __name__ == "__main__":
    lower_priority()
    slot = acquire_slot()
    try:
        main("--quick" in sys.argv)
    finally:
        os.rmdir(slot)
