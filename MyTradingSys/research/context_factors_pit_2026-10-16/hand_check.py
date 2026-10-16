"""Angle (c): hand arithmetic for every factor from the raw bars (pandas, indep_pandas.py) against the engine at chosen
DEV decision points. Nothing here is computed by the code under test; context_asof is only called for the row it claims.

  python hand_check.py            # three points: a mid-day 1h close, a 4h close, a day close (23:59) -> hand_check.md
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import context_asof as CA      # noqa: E402
import indep_pandas as IP      # noqa: E402
import run_compare as RC       # noqa: E402

SCRATCH = os.environ.get("CF_SCRATCH", os.path.join(HERE, "_scratch"))
CACHE = os.path.join(SCRATCH, "dev1m.npz")
# three grid points in 2023 (OURS, chosen before any row was read): 2023-03-14 10:59, 2023-08-21 15:59 (4h close), 2023-11-30 23:59 (day close)
POINTS = [(365 + 72) * 1440 + 10 * 60 + 59, (365 + 232) * 1440 + 15 * 60 + 59, (365 + 333) * 1440 + 1439]
FIELDS = ["price", "c_4h", "c_8h", "c_12h", "c_1d", "p_4h", "p_1d", "c_1w_hl", "pat_4h", "pat_8h", "pat_12h", "pat_1d", "atr4",
          "bb_4h_state", "bb_4h_pctb", "bb_4h_bw", "bb_1d_state", "bb_1d_pctb", "bb_1d_bw", "phase_a", "phase_b", "intraday", "intraday_alt",
          "vol_regime", "squeeze", "session", "weekend", "funding", "htf_align", "n_levels", "n_krown", "near_price", "near_src",
          "near_dist_atr", "level_age_h", "at_level", "n_layers", "touch_count", "first_touch", "approach", "sweep", "near_src_4hrule",
          "stop_d_pct", "stop_12_pct", "stop_8_pct", "ladder_rung", "ladder_stop_pct", "ladder_cost_r", "ladder_below_floor", "ladder_cond",
          "ladder_cond_alt", "bb_long_conf", "bb_short_veto_walk", "bb_short_veto_band"]


def same(a, b):
    if isinstance(a, tuple) and isinstance(b, tuple):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, (float, np.floating)) or isinstance(b, (float, np.floating)):
        if a is None or b is None:
            return False
        if a != a and b != b:
            return True
        return RC.same(float(a), float(b))
    return a == b


def fmt(v):
    if isinstance(v, tuple):
        return "(" + ", ".join(fmt(x) for x in v) + ")"
    if isinstance(v, (float, np.floating)):
        return "nan" if v != v else f"{v:.6g}"
    return str(v)


def main():
    bars = CA.load_dev(cache=CACHE)
    fund = CA.load_funding()
    V = CA.VecTables(bars, fund)
    out = ["# Angle (c): hand arithmetic (pandas, raw CSVs) vs the engine", "",
           "Points chosen before any row was read (OURS): a mid-day 1h close, a 4h close and a day close in 2023. `hand` is",
           "indep_pandas.py (resample + rolling + the spec's rules, no engine code); `engine` is the VEC build. A mismatch is a finding.", ""]
    n_bad = 0
    n_cmp = 0
    for t in POINTS:
        df = IP.bars_upto(t)
        for side in ("long", "short"):
            h = IP.hand_context(t, side, df)
            e = V.context(t, side)
            out += [f"## t = {t} ({IP.utc(t).strftime('%Y-%m-%d %H:%M')} UTC close), {side}", "", "| field | hand | engine | ok |", "|---|---|---|---|"]
            for k in FIELDS:
                if k not in h or k not in e:
                    continue
                ok = same(h[k], e[k])
                n_cmp += 1
                n_bad += (not ok)
                out.append(f"| {k} | {fmt(h[k])} | {fmt(e[k])} | {'yes' if ok else '**NO**'} |")
            out.append("")
            srcs = sorted({s for _, s, _ in h["_levels"]})
            out.append(f"hand ledger: {len(h['_levels'])} levels from {len(srcs)} sources ({', '.join(srcs)}); the nearest {side} level by hand = "
                       f"{fmt(h['near_price'])} ({h['near_src']}), by the engine = {fmt(e['near_price'])} ({e['near_src']}).")
            out.append("")
    out += [f"**{n_cmp} field comparisons, {n_bad} mismatches.**", ""]
    with open(os.path.join(HERE, "hand_check.md"), "w", newline="\n", encoding="utf-8") as fh:
        fh.write("\n".join(out))
    print(f"{n_cmp} comparisons, {n_bad} mismatches -> hand_check.md")


if __name__ == "__main__":
    main()
