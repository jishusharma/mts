"""Angle d (red team), the top 3 risks tested on the real DEV tape (counts only, no outcome):

  R1 boundary look-ahead: vectorised rows at 40 seeded decision hours on D/12h/8h/4h boundaries and mid-bucket, built
     from bars[0..t] only, must equal the full-DEV frame rows (truncation invariance on real data, not only synthetic).
  R2 wrong side: every row must have supports below / resistances above the close, stops on the loss side, distance >= 0.
  R3 silent level moves: for decision events, how often the nearest level at T is gone (no level within 1 USD of it on the
     same side) one hour later although no 1h close went through it. A PIT-correct level can still move or vanish
     between bars (Krown zone re-chaining, ATR-scaled tolerance, rolling windows); a trader would call that a repaint.
  python redteam.py
"""
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
import context_asof as C  # noqa: E402


def main():
    bars = C.load_dev()
    fr = {s: pd.read_pickle(C.CACHE / f"frame_{s}.pkl") for s in ("long", "short")}
    rng = np.random.default_rng(20261016)
    Ts = fr["long"].index.to_numpy(np.int64)
    bnd = Ts[(Ts % C.DAY) == 0]
    mid = Ts[(Ts % (4 * C.HOUR)) != 0]
    pick = np.r_[rng.choice(bnd, 20, replace=False), rng.choice(mid, 20, replace=False)]
    bad = 0
    for T in pick:
        t = C.decision_index(bars, int(T))
        cut = {k: (v[:t + 1] if k in ("ot", "o", "h", "l", "c", "v") else v) for k, v in bars.items()}
        for s in ("long", "short"):
            a = C.context_frame(cut, s, decisions=[int(T)]).iloc[0].to_dict()
            d = C.row_diff(a, fr[s].loc[int(T)].to_dict())
            if d:
                bad += 1
                print("R1 MISMATCH", int(T), s, d)
    print(f"R1 boundary truncation on real DEV: {len(pick)} hours x 2 sides, mismatches {bad}")

    for s, sg in (("long", 1), ("short", -1)):
        f = fr[s]
        has = f["f1_near_layer"] != "none"
        wrong_lvl = int((sg * (f.loc[has, "close"] - f.loc[has, "f1_near_px"]) <= 0).sum())
        neg_dist = int((f.loc[has, "f1_dist_atr"] < 0).sum())
        st = f["f3_stop_tf"] != "none"
        wrong_stop = int((f.loc[st, "f3_stop_pct"] <= 0).sum())
        print(f"R2 {s}: rows {len(f)}, level on the wrong side {wrong_lvl}, negative distance {neg_dist}, "
              f"stop on the wrong side {wrong_stop}")

    lv = C.context_frame(bars, "long", keep_levels=True)[["close", "levels"]]
    for s, sg in (("long", 1), ("short", -1)):
        f = fr[s]
        ev = f[f["f1_at_level"]]
        ev = ev[(ev.index + C.HOUR).isin(lv.index)]
        gone = []
        for T, r in ev.iterrows():
            L, lay = r["f1_near_px"], r["f1_near_layer"]
            nxt = lv.loc[T + C.HOUR]
            if sg * (nxt["close"] - L) <= 0:
                continue                                   # broken by the next close: a legitimate change
            still = any(abs(p - L) <= 1.0 and q == lay for p, q in nxt["levels"])
            gone.append((lay, not still, bool((T + C.HOUR) % C.DAY == 0)))
        g = pd.DataFrame(gone, columns=["layer", "vanished", "day_roll"])
        print(f"   of the vanished: at the 00:00 day roll {int((g.vanished & g.day_roll).sum())}, inside a day "
              f"{int((g.vanished & ~g.day_roll).sum())}")
        tab = g[~g.day_roll].groupby("layer")["vanished"].agg(["sum", "size"])
        tab["share"] = (tab["sum"] / tab["size"]).round(3)
        print(f"R3 {s}: at-level hours not broken by the next close {len(g)}; nearest level absent 1 h later "
              f"(same layer, within 1 USD): {int(g.vanished.sum())} ({g.vanished.mean():.1%})")
        print(tab.to_string())

if __name__ == "__main__":
    main()
