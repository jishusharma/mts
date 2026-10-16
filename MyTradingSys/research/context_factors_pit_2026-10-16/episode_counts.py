"""PRE_REG power table: episodes per pre-registered contrast, per side and per period, from grid_context.csv.
Counts only (no outcome column exists in the grid). An episode = grid row with at_level, first_touch, a ladder rung and a
stop at/above the cost floor. The contrasts are the ones frozen in PRE_REG.md section 2 (one per factor per side).

  python episode_counts.py   -> EPISODE_COUNTS.md
"""
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = os.path.join(HERE, "grid_context.csv")

# sd bound of a -1 / +1.5 R outcome = 1.25 R; K = 20 controls -> sd of (event - control mean) <= 1.25 * sqrt(1 + 1/20)
SD_R = 1.25
K = 20
Z = 2.8
PLAUSIBLE_R = 0.15
N_MIN = int(((Z * SD_R * (1 + 1.0 / K) ** 0.5) / PLAUSIBLE_R) ** 2) + 1


def contrasts(df, side):
    bull = df["pat_4h"].astype(str).str.contains("bull_engulf|bull_pin")
    bear = df["pat_4h"].astype(str).str.contains("bear_engulf|bear_pin")
    c = {
        "F1 at a side-aware level (every episode)": pd.Series(True, index=df.index),
        "F2 confluence n_layers >= 2": df["n_layers"] >= 2,
        "F3 operator condition (ladder_cond)": df["ladder_cond"].astype(str) == "True",
        "F4 4h pattern in the trade direction": bull if side == "long" else bear,
        "F5 long: re-entry from the lower band" if side == "long" else "F5 short: band-walk-down veto":
            (df["bb_long_conf"].astype(str) == "True") if side == "long" else (df["bb_short_veto_walk"].astype(str) == "True"),
        "F6 phase A with the trade (markup long / markdown short)": df["phase_a"] == ("markup" if side == "long" else "markdown"),
        "F7 HTF alignment (htf_align)": df["htf_align"].astype(str) == "True",
    }
    return c


def main():
    g = pd.read_csv(GRID, low_memory=False)
    g["year"] = g["utc_close"].str[:4]
    ep = g[(g["at_level"].astype(str) == "True") & (g["first_touch"].astype(str) == "True")
           & (g["ladder_rung"].astype(str) != "none") & (g["ladder_below_floor"].astype(str) == "False")]
    L = ["# Episodes per pre-registered contrast (counts only; PRE_REG.md section 3)", "",
         f"Episode = grid row with at_level, first_touch, a ladder rung and a stop >= the 0.56 % cost floor. n_min = {N_MIN} "
         f"(MDE = {Z} x {SD_R} R x sqrt(1 + 1/{K}) / sqrt(n) <= {PLAUSIBLE_R} R, the cost-free filter contrast). "
         "`<n` marks a cell below n_min on the pooled count; the per-period columns are for the consistent-sign rule.", "",
         "| contrast | side | 2022 | 2023 | 2024H1 | all | complement all |", "|---|---|---|---|---|---|---|"]
    for side in ("long", "short"):
        e = ep[ep["side"] == side]
        for name, mask in contrasts(e, side).items():
            m = mask.reindex(e.index).fillna(False).astype(bool)
            by = e[m].groupby("year").size()
            tot = int(m.sum())
            flag = "" if tot >= N_MIN else " <n"
            L.append(f"| {name} | {side} | {by.get('2022', 0)} | {by.get('2023', 0)} | {by.get('2024', 0)} | {tot}{flag} | {int((~m).sum())} |")
    L += ["", f"Episodes with a valid stop: long {int((ep['side'] == 'long').sum())}, short {int((ep['side'] == 'short').sum())} "
          f"(of {int((g['side'] == 'long').sum())} grid points per side).", ""]
    with open(os.path.join(HERE, "EPISODE_COUNTS.md"), "w", newline="\n", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print("\n".join(L[4:]))


if __name__ == "__main__":
    main()
