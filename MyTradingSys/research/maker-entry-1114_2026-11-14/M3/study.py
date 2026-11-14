"""M3 maker-entry study: NK6 combo L2&L3&L5 (phase-matched), limit at close of the signal bar.
Signals/stop/target/time-stop frozen from the original (orig_study.py, copied unchanged). Fill model: lib/maker_fill.py.
Usage: python study.py   (writes results.json). Stop distance S = max(1 ATR[i], 0.5% of L) (original used entry=next open; the
limit level L is the entry here). Target L+-2S; time stop = end of bar i+24 (original exit at close of bar i+24)."""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import orig_study as O
import maker_fill as MF

BAR = 900000; HOLD = O.HOLD; TGT_R = O.TGT_R; COMBO = [1, 2, 4]   # L2,L3,L5 (0-based rows)
VAL_DAY = int(np.datetime64("2024-01-01").astype("datetime64[D]").astype(int))
SYMS = O.SYMS


def level_and_levels(close, atr, sd):
    """Signal-to-limit mapping: L = close of the signal bar; stop/target from L (original multiples)."""
    L = float(close)
    S = max(1.0 * float(atr), 0.005 * L)
    return L, L - sd * S, L + sd * TGT_R * S


def run_signal(ts_i, close, atr, sd, m1, tick, bad_variant=None):
    """One order. ts_i = open time of signal bar. Order placed at the signal bar close = ts_i + BAR."""
    L, stop, tgt = level_and_levels(close, atr, sd)
    sig_close = ts_i + BAR
    return MF.simulate_maker(sd, L, stop, tgt, sig_close, BAR, ts_i + (HOLD + 1) * BAR, False, m1, tick=tick)


def taker_net(gross, feeR, bp=12.0):
    return gross - bp * feeR


def acquire_slot():
    root = r"F:\MTS\maker_slots"; os.makedirs(root, exist_ok=True)
    while True:
        for k in range(4):
            p = os.path.join(root, f"slot{k}")
            try:
                os.mkdir(p); return p
            except FileExistsError:
                pass
        time.sleep(20)


def main(n_draws=1000):
    t0 = time.time()
    rows = []; place = {}
    for sym in SYMS:
        D, F, out = O.build_coin(sym)
        m1 = MF.load_m1(sym + "USDT"); tick = MF.estimate_tick(m1)
        ts = D["ts"]; dayn = (ts // 86400000).astype(int); ph = F["phase"]
        for dirn in (1, -1):
            o = out[dirn]
            for i in o["trades"][("L2&L3&L5", "prim")]:
                r = run_signal(ts[i], D["c"][i], F["atr"][i], dirn, m1, tick)
                r.update(sym=sym, dirn=dirn, i=int(i), day=int(dayn[i]), signal_close_ms=float(ts[i] + BAR), phase=float(ph[i]),
                         orig_gross=float(o["gross"][i]), orig_feeR=float(o["feeR"][i]))
                rows.append(r)
            valid = o["prim"] & (dayn >= VAL_DAY) & (np.arange(len(ts)) < len(ts) - HOLD - 3)
            place[(sym, dirn)] = dict(idx=np.flatnonzero(valid), ts=ts, c=D["c"], atr=F["atr"], m1=m1, tick=tick)
        print(sym, round(time.time() - t0), flush=True)
    val = [r for r in rows if r["day"] >= VAL_DAY]; dev = [r for r in rows if r["day"] < VAL_DAY]
    res = {}
    for nm, sub in (("VAL", val), ("DEV", dev)):
        g = np.array([r["orig_gross"] for r in sub]); f = np.array([r["orig_feeR"] for r in sub])
        tk = g - 12 * f
        fl = [r for r in sub if r["filled"]]
        s = MF.summarize(sub)
        s["taker_n"] = len(sub); s["taker_gross"] = float(g.mean()); s["taker_net12"] = float(tk.mean())
        s["taker_net6"] = float((g - 6 * f).mean())
        gi = np.array([r["orig_gross"] for r in fl]); fi = np.array([r["orig_feeR"] for r in fl]); ti = gi - 12 * fi
        s["orig_gross_filled"] = float(gi.mean()) if len(fl) else None
        s["adverse_selection_R"] = float(gi.mean() - g.mean()) if len(fl) else None
        s["taker_net12_filled_subset"] = float(ti.mean()) if len(fl) else None
        s["miss_reasons"] = {k: sum(1 for r in sub if r["reason_missed"] == k) for k in {r["reason_missed"] for r in sub if not r["filled"]}}
        s["exit_types"] = {k: sum(1 for r in fl if r["exit_type"] == k) for k in {r["exit_type"] for r in fl}}
        s["phase_mix"] = [float(np.mean([r["phase"] == p for r in sub])) for p in (1.0, 0.0, -1.0)] if sub else None
        res[nm] = s
    # placebo (VAL), same fill model, limit = signal bar close (offset = 0: the real L - close is 0 by construction)
    offsets = MF.signal_offsets_atr([r["dirn"] for r in val], [D_L(r, place) for r in val],
                                    [place[(r["sym"], r["dirn"])]["c"][r["i"]] for r in val],
                                    [place[(r["sym"], r["dirn"])]["atr"][r["i"]] for r in val])
    res["offset_atr_max_abs"] = float(np.abs(offsets).max())
    groups = {}
    for r in val:
        if r["filled"]: groups[(r["sym"], r["dirn"])] = groups.get((r["sym"], r["dirn"]), 0) + 1
    memo = {}
    def sim(key, i):
        k = (key, i)
        if k not in memo:
            P = place[key]; sd = key[1]
            m = run_signal(P["ts"][i], P["c"][i], P["atr"][i], sd, P["m1"], P["tick"])
            memo[k] = m["net_R"] if m["filled"] else None
        return memo[k]
    rng = np.random.default_rng(7); obs = res["VAL"]["mean_net_R_filled"]; nfill = sum(groups.values())
    draws = np.empty(n_draws)
    for d in range(n_draws):
        tot = 0.0
        for key, ng in groups.items():
            idx = place[key]["idx"]; got = 0; tries = 0
            while got < ng:
                tries += 1
                if tries > 200 * ng: raise RuntimeError("placebo fill too low")
                v = sim(key, int(idx[rng.integers(0, len(idx))]))
                if v is not None: tot += v; got += 1
        draws[d] = tot / nfill
        if d % 50 == 0: print("placebo", d, round(time.time() - t0), flush=True)
    res["placebo_p"] = float((1 + np.sum(draws >= obs)) / (n_draws + 1)); res["placebo_mean"] = float(draws.mean())
    res["placebo_filled_n"] = nfill
    res["seconds"] = time.time() - t0
    return res, rows


def D_L(r, place):
    return float(place[(r["sym"], r["dirn"])]["c"][r["i"]])   # L = close of the signal bar


if __name__ == "__main__":
    slot = acquire_slot()
    try:
        res, rows = main(int(sys.argv[1]) if len(sys.argv) > 1 else 1000)
        json.dump(dict(res=res), open(os.path.join(HERE, "results_raw.json"), "w"), indent=1, default=float)
        json.dump(rows, open(os.path.join(HERE, "rows.json"), "w"), default=float)
    finally:
        os.rmdir(slot)
