# V3 VALIDATION RESULTS (2024-07-01 .. 2025-06-30, run once; HOLDOUT never loaded)

Frozen in PRE_REG_ADDENDUM_A_2026-10-09.md (commit 6e6227b). Features computed on DEV+VALIDATION concatenated for warm-up; events and baselines restricted to bars opening on/after 2024-07-01; forward windows end by 2025-06-30.

## Candidate 1: R40D_N, 4h, h=6, reversal (long after RSI(14) crosses down through 40 on RVadj < 1.5)

| n events | gross bp | net bp [95% CI] | win | excess bp vs all bars | one-sided p | min n (registered) |
|---|---|---|---|---|---|---|
| 50 | +14 | -2 [-68, +64] | 52% | -1 | 0.523 | 100 |

Verdict: **INSUFFICIENT-N (n < 100: registered rule cannot be met; numbers shown for information, candidate stays an unvalidated hypothesis)**

DEV had 189 such events in 4.5 years (about 42 per year); VALIDATION has 50 in 1 year.

## Candidate 2: TH1 replication - SP3 spike continuation return (h=18), session C (16-24 UTC) minus session A (00-08 UTC)

| nC | nA | mean C bp | mean A bp | diff bp | 95% CI bp | p |
|---|---|---|---|---|---|---|
| 31 | 36 | -26 | -152 | +126 | [-90, +377] | 0.310 |

DEV: diff -178 bp, CI [-344, -20] (C mean -40, A mean +138). Replicated only if the CI excludes 0 with diff < 0: **NOT REPLICATED**

