# T4 RESULT (2026-11-14): trapped-shorts squeeze long, 48 fresh coins, 4h

**FAIL, all three kill criteria fire. Fresh VAL RIDE: n 111, 37 entry weeks, gross +0.050 R, fee-net -0.002 R, week-cluster 95% CI [-0.664, +1.148], placebo percentile 64.7. The old-coin +2.42 R did not carry over.**

| Test | n VAL | Gross R | Fee-net R | CI (weeks) | Placebo pct | Verdict |
|---|---|---|---|---|---|---|
| RIDE fresh VAL (primary) | 111 | +0.050 | -0.002 | [-0.664, +1.148] | 64.7 | FAIL |
| RIDE fresh DEV (sign) | 106 (DEV) | +0.801 | +0.791 | [-0.176, +1.982] | n/a | sign ok |
| T3R fresh VAL (ex-best-5 row) | 112 | -0.241 | -0.272 | [-0.562, +0.092] | n/a | ex-best-5 -0.488, FAIL |
| Control DOWN RIDE VAL | 21 | -0.338 | -0.204 | [-0.988, +0.933] | n/a | descriptive |
| Old-20 RIDE VAL (same code) | 72 | +2.554 | +2.420 | [-0.012, +6.214] | n/a | replicates the miner |

Failed bars: 2 (mean ~0, CI low -0.664), 4 (placebo 64.7 vs needed 97.5), 5 (ex-best-5 T3R -0.488), 6 (strategy -0.00152/day vs basket -0.00002), 7 (FRAGILE: worst removal OCEAN -0.304; 9 of 38 removals negative). Met: 1 (n 111, 37 weeks), 3 (DEV +0.791). Holm p 0.539, cannot pass.

## What was learned
- Same code, same weeks: old 20 coins +2.55 R gross on VAL, 48 fresh coins +0.05 R. The old-coin result belongs to those coins, not to the rule.
- The rule is tail-shaped: 76% of VAL trades hit the stop, five trades add +68.7 R, the full set nets -0.2 R. DEV +0.79 R rests on 2020-21 outliers.
- Fees are not the problem (0.02 R); the gross edge is absent on new coins.
- Power: at the measured sd (3.9 R) only a mean of about +1.2 R could register, so this kills the claimed +2.4 R, not every smaller edge (n needed for +0.3 R is about 2000).
- Splits sit in different cycles: DEV signals mostly BASE/BEAR, VAL signals 77% BULL. Funding cache ends 2026-10-31, so the last 2 weeks cannot be checked; no known open signal.

## Kill criteria from the design note
T4 KILL if (a) VAL RIDE mean <= 0: fires (-0.0019). (b) T3R ex-best-5 <= 0: fires (-0.488). (c) real mean at or below 97.5th placebo pct with n >= 60: fires (n 111). Outcome: KILLED, "squeeze long was a tail of 20 old coins". No testnet-forward card.

## Allowlist rows needed (not self-approved)
`t4_stats.py` lines 50 and 119 (fullsample-quantile WARN: bootstrap and placebo percentiles on resampled means). `t4_report.py` has no WARN after rewrite. 0 FAIL. Context lint clean, 37 tests pass (9 s, `-W error`).

## Where
- Worktree: <local-path>
- Branch: JIS-NB/t4-squeeze-long-fresh
- Commit: e38520598 (stage 4); fix round was 8f9a2c4b8
- Folder: MyTradingSys/research/t4_squeeze_long_fresh_2026-11-14 (RESULT.md, summary.json, tables.md, report_numbers.json)
- Untracked stray `stats_run.log` in the worktree root (not committed; a delete was denied, coordinator may remove it)

shipped: no (coordinator ships)
