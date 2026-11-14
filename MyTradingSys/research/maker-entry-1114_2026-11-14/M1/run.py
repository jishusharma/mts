"""M1 run: baseline replication + maker model + placebo + gates. Writes results.json. Parameters frozen (PRE_REG)."""
import os, sys, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study as S
import maker_fill as MF
import nk2_orig as O

SYMS = O.SYMS
DRAWS, SEED, BANK = 1000, 7, 12000
FEE_T = 0.0012


def main():
    t00 = time.time()
    rows_all, ph_mix, ticks, sig_offs = [], np.zeros(3), {}, []
    for sym in SYMS:                                   # pass 1: real signals, maker + taker baseline
        D = O.prep(sym, S.TFK)
        m1 = MF.load_m1(sym + "USDT")
        tick = MF.estimate_tick(m1)
        ticks[sym] = tick
        a = D["a"]
        mv = D["valid"] & (a[:, 0] >= S.SPLIT)
        ph = D["ph"][mv]
        ph_mix += [(ph == 1).sum(), (ph == -1).sum(), (ph == 0).sum()]
        sigs = S.orig_signals(D)
        for (i, R, df, phase, entry_ms) in sigs:
            r = S.maker_trade(D, i, m1, tick)
            isval = bool(a[i, 0] + S.TF_MS >= S.SPLIT)
            if isval:
                sig_offs.append((float(D["lv"][S.LEVEL][i]) - a[i, 4]) / D["atr"][i])
            rows_all.append(dict(sym=sym, i=i, signal_close_ms=r["signal_close_ms"], tkr_gross=R, tkr_df=df,
                                 tkr_net=R - FEE_T / df, phase=phase, entry_ms=entry_ms, filled=r["filled"],
                                 gross_R=r["gross_R"], fee_R=r["fee_R"], net_R=r["net_R"], exit_type=r["exit_type"],
                                 fill_ms=r["fill_ms"], miss=r["reason_missed"], val=isval))
        print(sym, "tick", tick, "signals", len(sigs), "t", round(time.time() - t00), flush=True)
        del D, m1
    offs = np.array(sig_offs)
    offs = offs[np.isfinite(offs) & (offs >= 0)]
    print("offsets n", len(offs), "q10/50/90", np.percentile(offs, [10, 50, 90]), flush=True)
    rng = np.random.default_rng(SEED)
    pbank, pbank_n = {}, {}
    for sym in SYMS:                                   # pass 2: placebo bank per symbol (same fill code)
        D = O.prep(sym, S.TFK)
        m1 = MF.load_m1(sym + "USDT")
        tick = ticks[sym]
        a = D["a"]
        mv = D["valid"] & (a[:, 0] >= S.SPLIT)
        cand = np.flatnonzero(mv & np.isin(D["ph"], S.PHASES) & ~np.isnan(D["atr"]) & (np.arange(len(a)) < len(a) - 30))
        out, nb = [], BANK
        for _ in range(nb):
            i = int(cand[int(rng.integers(0, len(cand)))])
            off = float(offs[int(rng.integers(0, len(offs)))])
            L = MF.placebo_limit(S.SIDE, float(a[i, 4]), float(D["atr"][i]), off)
            r = S.maker_trade(D, i, m1, tick, L=L)
            if r["filled"]:
                out.append(r["net_R"])
        pbank[sym], pbank_n[sym] = out, nb
        print("placebo bank", sym, len(out), "of", nb, "cand", len(cand), flush=True)
        del D, m1
    json.dump(dict(rows=rows_all, ticks=ticks, ph_mix=ph_mix.tolist(), offs_n=int(len(offs)),
                   offs_q=[float(x) for x in np.percentile(offs, [10, 50, 90])], pbank=pbank, pbank_n=pbank_n),
              open(os.path.join(HERE, "raw_run.json"), "w"), default=float)
    print("raw saved", round(time.time() - t00), flush=True)


if __name__ == "__main__":
    main()
