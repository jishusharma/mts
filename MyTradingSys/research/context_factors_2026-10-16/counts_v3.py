"""counts_v3.py: PRE_REG_V3.md s.2 counts only (keys, pool membership, stop width known at T). No outcome, no price after T.

  python counts_v3.py  -> per side: V2 pool vs V3 pool (V2 pool + stop-width caliper), matched events/days,
                          median stop_pct of matched C and of the chosen controls, relative gap.
V3 = V2 control rule (PRE_REG_V2.md s.1) plus one change: a candidate control is eligible for a C event only if its
ladder stop width f3_stop_pct (known at its own T) lies within [C / CAL, C x CAL] of the C event's width (CAL = 1.25, OURS).
"""
import sys, numpy as np
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import study as S

CAL = 1.25  # OURS: the AUDIT_BEFORE_RUN item 1 comparability bound (25 % relative), applied per event instead of per pool


def main():
    fr = S.frames()
    led = {s: S.tradeable_ledger(fr[s]) for s in fr}
    cset = {s: S.form_c(led[s], s) for s in led}
    b = S.load_1m()
    cn = S.load_context_null()
    cfg = cn.Config(bar_min=60, cooldown=4, seed=0)
    Cc, _ = S.hourly_closes(b)
    rv = cn.rolling_rv(Cc, cfg.vol_win_min // cfg.bar_min)

    def keyof(T):
        return cn.context_key(Cc, int((T - S.HOUR - S.DEV_START_MS) // S.HOUR), cfg, rv=rv)

    for variant in ("V2_pool", "V3_caliper"):
        tot, days = 0, set()
        for s in ("long", "short"):
            f = fr[s]
            Tn = f["T"].to_numpy(np.int64)
            sp = f["f3_stop_pct"].to_numpy(float)
            ok = (f["f3_stop_tf"] != "none").to_numpy() & f["f1_at_level"].to_numpy(bool)
            c = cset[s]
            Tc = c["T"].to_numpy(np.int64)
            spc = c["f3_stop_pct"].to_numpy(float)
            near = (np.abs(Tn[:, None] - Tc[None, :]) <= S.DAY).any(axis=1)
            pool = ok & ~near
            keys = {}
            for i in np.flatnonzero(pool):
                k = keyof(Tn[i])
                if k is not None:
                    keys.setdefault(k, []).append(i)
            rng = np.random.default_rng(0)
            m, mdays, c_sp, ctl_sp = 0, set(), [], []
            for T, w in zip(Tc, spc):
                k = keyof(T)
                if k is None:
                    continue
                cand = np.array(keys.get(k, []), np.int64)
                if variant == "V3_caliper" and len(cand):
                    cand = cand[(sp[cand] >= w / CAL) & (sp[cand] <= w * CAL)]
                rng.shuffle(cand)
                ch = []
                for j in cand:
                    if len(ch) >= cfg.K:
                        break
                    if any(abs(int(Tn[j]) - int(Tn[c2])) <= cfg.cooldown * S.HOUR for c2 in ch):
                        continue
                    ch.append(int(j))
                if len(ch) >= cfg.kmin:
                    m += 1
                    mdays.add(int(T // S.DAY))
                    c_sp.append(w)
                    ctl_sp.extend(sp[ch])
            mc, mk = float(np.median(c_sp)), float(np.median(ctl_sp))
            print(f"{variant} {s}: pool {int(pool.sum())} C {len(Tc)} matched {m} days {len(mdays)} "
                  f"median stop_pct C {mc:.3f} controls {mk:.3f} gap {abs(mk - mc) / mc:.1%}")
            tot += m
            days |= mdays
        print(f"{variant} POOLED matched {tot} days {len(days)}")


if __name__ == "__main__":
    main()
