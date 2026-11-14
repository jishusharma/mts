**T6 DD20 weekly dip long, 44 fresh coins: FAIL at bar 2, KILL (criteria a, b, c). VAL n 561 (92 entry weeks), gross -0.023 R, fee-net -0.028 R (-0.63%), week-cluster CI [-4.8%, +3.4%] (R: [-0.233, +0.190]).**

| test | n VAL | gross R | fee-net R | CI (net %) | placebo pct | verdict |
|---|---|---|---|---|---|---|
| DD20 E1 X2, primary, fresh 44 coins | 561 | -0.023 | -0.028 | [-4.81%, +3.40%] | about 57 (p 0.435) | FAIL + KILL, FRAGILE |
| STOP row (2.5 ATR14), VAL | 561 | n/a | -0.063 | [-0.269, +0.157] R | p 0.742 | kill criterion b fired |
| DEV primary | 803 | +0.040 | +0.025 | [-3.31%, +8.70%] | - | sign positive, a 2021 result |

Failed bars: 2 (VAL mean -0.63%, CI low -4.81%), 4 (placebo, real below p97.5 +1.12%), 5 (ex-best-5 weeks -4.31%), 7 (top-coin removal still negative; FRAGILE). Met: 1 (power), 3 (DEV +2.58%), 6 (only because the basket baseline is also negative, -0.91%).

What was learned:
- The source cell's +2.6% VAL mean did not appear on 44 fresh coins: VAL is -0.63% net, gross is already negative, so fees and funding are not the cause.
- DEV +2.58% is a 2021 result (+15% in 2021, about -1.4% per trade outside it).
- The rule did no better than buying a random Monday of the same coins (placebo p 0.435).
- VAL is carried by three trades (ONE +461%, ZIL, AXS funding credits); without them VAL is -1.59%.
- DEV excludes pre-gap LUNA/FTT (longest-run rule contradicts the PRE_REG survivorship note, about 16 trades); VAL unaffected.

Kill-criteria outcome (design note, T6): fresh VAL mean <= 0 FIRED; stop row mean R <= 0 FIRED; ex-best-5 weeks <= 0 FIRED. Conclusion: DD20 was drift plus survivorship. Power: measured week sd 2.41 R, MDE 0.81 R at n 92; a negative point estimate, not an untested one, but not proof against a small edge.

Active today: no new fresh-coin event after the last closed week; 12 events (entries 2026-11-02 and 2026-11-09) unresolved at data end. BTC weekly close 0.865 x prior 8-week max, not an event. Descriptive, not advice.

Worktree: <local-path> (folder MyTradingSys/research/t6_dd20_dip_long_fresh_2026-11-14), branch JIS-NB/t6-dd20-dip-long-fresh, commit: a7fc47ef0.
shipped: no (coordinator ships)
