"""Re-score the Habib/Qriptal imbalance fade (10-16) with plan stops and Deribit fees (card fee-stop-rescore-fabio-habib-1106).

Same entries as imb.py (imb_small at k = 2, next-bar-open, 24-bar hold, 1R/2R targets, design + check windows).
Stops (all OURS; his 'plan' is level + imbalance + wick, no stop rule is public):
  OLD   candle's own extreme (the 10-16 stop)
  PLAN1 extreme + 0.5 x candle range beyond (room for the wick to be retaken)
  PLAN2 extreme + 1.0 x candle range beyond (the whole imbalance candle is the invalidation zone)
Costs: MyTradingSys/backtest/fees.py via fabio/rescore.py. Regime A = taker in, taker stop/time, taker target;
regime B = maker entry at the next open (OPTIMISTIC: fill assumed, no queue), maker target, taker stop/time.
Run: python rescore_habib.py   (writes RESCORE_tables.json next to this file)
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2]))
import imb  # noqa: E402
from MyTradingSys.backtest.layers.fabio import rescore as R  # noqa: E402

K = 2.0
STOPS = {"OLD": 0.0, "PLAN1": 0.5, "PLAN2": 1.0}


def events(df1m, tf, start, end):
    b = imb.resample(df1m, tf)
    cls, side = imb.classify(b, K)
    t1, o1, h1, l1, c1 = (df1m[x].to_numpy() for x in ("t", "o", "h", "l", "c"))
    s_ms, e_ms = (pd.Timestamp(x).value // 1_000_000 for x in (start, end))
    ms = imb.TF_MS[tf]
    n_hold = imb.HOLD_BARS * ms // imb.MIN_MS
    out = []
    for i in np.flatnonzero((cls == "imb_small") & (side != 0)):
        if not (s_ms <= int(b.t[i]) < e_ms):
            continue
        t_entry = int(b.t[i]) + ms
        a = int(np.searchsorted(t1, t_entry))
        z = a + n_hold
        if a >= len(t1) or t1[a] != t_entry or z > len(t1) or t1[z - 1] - t_entry != (n_hold - 1) * imb.MIN_MS:
            continue
        sd = int(side[i])
        entry = float(o1[a])
        rng = float(b.h[i] - b.l[i])
        for name, mult in STOPS.items():
            stop = (float(b.l[i]) - mult * rng) if sd > 0 else (float(b.h[i]) + mult * rng)
            if sd * (entry - stop) <= 0:
                continue
            for Rt in imb.TARGETS_R:
                tgt = entry + sd * Rt * abs(entry - stop)
                xp, oc = imb.resolve(sd, entry, stop, tgt, h1[a:z], l1[a:z], c1[a:z])
                row = {"tf": tf, "stop": name, "R": Rt, "risk_bp": abs(entry - stop) / entry * 1e4}
                xk = R.exit_kind_for(oc)
                row["gross"], row["fee_A"], row["net_A"] = R.net_r(sd, entry, stop, xp, "taker", "taker")
                _, row["fee_B"], row["net_B"] = R.net_r(sd, entry, stop, xp, "maker", xk)
                out.append(row)
    return out


def main():
    df = imb.load_1m()
    res = {}
    for wname, (s, e) in (("design", imb.DESIGN), ("check", imb.CHECK)):
        rows = []
        for tf in imb.TF_MS:
            rows += events(df, tf, s, e)
        d = pd.DataFrame(rows)
        g = d.groupby(["tf", "stop", "R"]).agg(n=("gross", "size"), gross=("gross", "mean"), net_A=("net_A", "mean"),
                                               net_B=("net_B", "mean"), risk_bp=("risk_bp", "median")).reset_index()
        res[wname] = g.to_dict("records")
    (HERE / "RESCORE_tables.json").write_text(json.dumps(res, indent=1), encoding="utf-8", newline="\n")
    for w, rs in res.items():
        print(w)
        for r in rs:
            print(r["tf"], r["stop"], r["R"], r["n"], round(r["gross"], 3), round(r["net_A"], 3), round(r["net_B"], 3), round(r["risk_bp"], 0))


if __name__ == "__main__":
    main()
