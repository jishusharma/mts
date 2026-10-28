"""COUNT-ONLY power check on DEV + DEV_EXT (no outcome column is read or built; D3).

  python count_ext.py frames   -> CACHE/frame_ext_long.pkl, frame_ext_short.pkl (vectorised factor frames, decisions 2020-04-01 ..)
  python count_ext.py counts   -> COUNTS_DEV_EXT.md, counts_dev_ext.csv

Same factor builder (context_asof.context_frame, unedited), same ledger rule and cooldown as counts.py, same power formula as
PRE_REG s.4: n_needed = ((z + 0.8416) x sd / (plausible - cost))^2 in distinct UTC days, sd 1.5 R, plausible 0.20 R, cost = median
cost in R of the tradeable ledger. Gates: m = 1 (z 1.960) and Holm m = 37 (z 3.205, the PRE_REG number). A bucket is POWERED
when its distinct days on a side reach n_needed. DECISION (OURS): the m = 37 gate is the one that counts as "powered";
m = 1 is printed beside it. Decisions start 2020-04-01 (same 90-day warm-up rule as run_dev.py).
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import context_asof as C  # noqa: E402
import counts as K  # noqa: E402
import dev_ext as X  # noqa: E402

START_MS = 1_585_699_200_000      # 2020-04-01 00:00 UTC (OURS warm-up, as run_dev.START_MS)
Z_M1, Z_HOLM, Z_BETA = 1.959964, 3.205, 0.8416   # PRE_REG s.4: z_holm = 3.205 at m = 37; 0.8416 = power 0.80


def decisions(bars):
    ends = bars["ot"] + C.MIN5
    return ends[(ends % C.HOUR == 0) & (ends >= START_MS) & (ends <= C.DEV_END_MS)]


def n_needed(cost_r, z):
    gap = K.PLAUSIBLE_R - cost_r
    return int(np.ceil(((z + Z_BETA) * K.SD_R / gap) ** 2)) if gap > 0 else None


def build_frames():
    bars = X.load_dev_bars(include_dev_ext=True)
    Ts = decisions(bars)
    for s in ("long", "short"):
        t0 = time.time()
        f = C.context_frame(bars, s, decisions=Ts)
        f.to_pickle(C.CACHE / f"frame_ext_{s}.pkl")
        print(s, len(f), f"{time.time() - t0:.0f}s")


def main():
    fr = {s: pd.read_pickle(C.CACHE / f"frame_ext_{s}.pkl") for s in ("long", "short")}
    ev = {s: K.ledger(fr[s]) for s in fr}
    tr = {s: ev[s][ev[s]["f3_stop_tf"] != "none"] for s in ev}
    allev = pd.concat([tr["long"], tr["short"]])
    allev["day"] = allev["T"] // C.DAY
    allev["seg"] = np.where(allev["T"] <= X.DEV_EXT_END_MS, "DEV_EXT", "DEV")
    cost = float(allev["f3_cost_R"].median())
    n1, n37 = n_needed(cost, Z_M1), n_needed(cost, Z_HOLM)
    rows = []
    for fct in K.FACTORS:
        vals = allev[fct].map(K.bucket)
        for val in sorted(vals.unique()):
            sub = allev[vals == val]
            r = {"factor": fct, "value": val}
            for s in ("long", "short"):
                x = sub[sub["side"] == s]
                r[f"{s}_n"], r[f"{s}_days"] = len(x), x["day"].nunique()
                r[f"{s}_days_dev"] = x[x.seg == "DEV"]["day"].nunique()
                r[f"{s}_days_ext"] = x[x.seg == "DEV_EXT"]["day"].nunique()
            r["powered_m1"] = max(r["long_days"], r["short_days"]) >= n1
            r["powered_m37"] = max(r["long_days"], r["short_days"]) >= n37
            rows.append(r)
    t = pd.DataFrame(rows)
    t.to_csv(HERE / "counts_dev_ext.csv", index=False)
    per = t.groupby("factor", sort=False).agg(values=("value", "size"), p1=("powered_m1", "sum"), p37=("powered_m37", "sum"))
    fac1 = [f for f in K.FACTORS if per.loc[f, "p1"] > 0]
    fac37 = [f for f in K.FACTORS if per.loc[f, "p37"] > 0]
    days_all = len({int(d) for d in (fr["long"]["T"] // C.DAY)})
    days_ext = len({int(d) for d in (fr["long"]["T"][fr["long"]["T"] <= X.DEV_EXT_END_MS] // C.DAY)})
    L = ["# COUNTS_DEV_EXT: DEV + DEV_EXT per-factor event counts (counts only, no outcome read)", "",
         "Built by `count_ext.py` (frames: `context_asof.context_frame`, unedited; ledger rule of `counts.py`). Segments: DEV_EXT = "
         "bar open 2020-01-01 .. 2021-12-31 (decisions from 2020-04-01), DEV = 2022-01-01 .. 2024-06-30 (decisions from 2022-01-01 "
         "now, because DEV_EXT supplies the warm-up). VALIDATION and HOLDOUT are never loaded (`dev_ext.assert_dev_stage`).", "",
         f"- Decision days: {days_all} total, of which {days_ext} in DEV_EXT. Tradeable ledger: long {len(tr['long'])}, short {len(tr['short'])}.",
         f"- Median cost in R of the tradeable ledger: {cost:.3f} R.",
         f"- n_needed (distinct UTC days per bucket and side, plausible {K.PLAUSIBLE_R} R, sd {K.SD_R} R): **{n1}** at m = 1; **{n37}** at Holm m = 37 (PRE_REG s.4: 1,242 and 2,064 on DEV only).",
         f"- Factors with at least one POWERED value at m = 37: **{', '.join(fac37) if fac37 else 'none'}**.",
         f"- Factors with at least one POWERED value at m = 1 only: {', '.join(f for f in fac1 if f not in fac37) or 'none'}.", "",
         "| factor | value | long n | long d | (DEV / EXT) | short n | short d | (DEV / EXT) | m=1 | m=37 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['factor']} | {r['value']} | {r['long_n']} | {r['long_days']} | {r['long_days_dev']} / {r['long_days_ext']} | "
                 f"{r['short_n']} | {r['short_days']} | {r['short_days_dev']} / {r['short_days_ext']} | "
                 f"{'POWERED' if r['powered_m1'] else 'low'} | {'POWERED' if r['powered_m37'] else 'low'} |")
    (HERE / "COUNTS_DEV_EXT.md").write_text("\n".join(L) + "\n", encoding="utf-8", newline="\n")
    print(f"days {days_all} ext {days_ext} cost {cost:.3f} n1 {n1} n37 {n37}")
    print("powered m37:", fac37)
    print("powered m1:", fac1)


if __name__ == "__main__":
    {"frames": build_frames, "counts": main}[sys.argv[1]]()
