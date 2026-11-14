VERDICT: FAIL. No primary row of the NK pivot S/R reclaim (15m, 1h; 20 coins; VALIDATION 2024+) has positive fee-net R; 0 of 8 pass (mean net R > 0 fails everywhere, 6 of 8 also lose at the 6 bp maker fee; only the two 1h shorts are slightly positive there). Best row: 1h SHORT-P, net -0.009 R at 12 bp (+0.046 at 6 bp) but CI low -0.054 and ex-best-5 -0.041.

PRE_REG sha c07a835 (committed before any outcome). All parameters fixed in PRE_REG.md (SOURCED vs OURS labelled there); nothing tuned on DEV.

## Context
Phase of each day from the prior daily close: MA20 slope + ADX(14)>=20 with DI direction = UP/DOWN, else RANGE. Primary rows trade only the matching direction (LONG in UP/RANGE, SHORT in DOWN/RANGE); mismatched direction is a control row.

Regime mix: all coin-days in VALIDATION: UP 25%, DOWN 35%, RANGE 40%.

## Matched rows (VALIDATION 2024-01-01+, taker 12 bp; trigger = reclaim of level, target = next pivot, stop = swing with min 0.6 ATR / 0.5%)

| tf | row | n DEV/VAL | win % | gross R | net R 12bp | net R 6bp | CI low trade | CI low day | placebo p | BH | ex-best-5 | fee/R | mix UP/DOWN/RANGE % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 15m | LONG-P | 17598/10962 | 35.4 | -0.060 | -0.198 | -0.129 | -0.232 | -0.262 | 0.004 | yes | -0.219 | 0.138 | 40/0/60 |
| 15m | LONG-S1 | 6679/4887 | 34.8 | -0.139 | -0.279 | -0.209 | -0.329 | -0.371 | 0.813 | no | -0.318 | 0.140 | 39/0/61 |
| 15m | SHORT-P | 17474/12819 | 37.3 | 0.038 | -0.105 | -0.034 | -0.139 | -0.178 | 0.080 | no | -0.132 | 0.144 | 0/48/52 |
| 15m | SHORT-R1 | 7012/5418 | 38.3 | 0.031 | -0.122 | -0.045 | -0.172 | -0.211 | 0.350 | no | -0.162 | 0.153 | 0/46/54 |
| 1h | LONG-P | 8773/5227 | 42.7 | -0.046 | -0.152 | -0.099 | -0.197 | -0.226 | 0.141 | no | -0.181 | 0.106 | 40/0/60 |
| 1h | LONG-S1 | 2917/2181 | 42.5 | -0.106 | -0.215 | -0.160 | -0.286 | -0.331 | 0.728 | no | -0.263 | 0.109 | 40/0/60 |
| 1h | SHORT-P | 8634/6102 | 46.2 | 0.101 | -0.009 | 0.046 | -0.054 | -0.098 | 0.001 | yes | -0.041 | 0.110 | 0/47/53 |
| 1h | SHORT-R1 | 3119/2503 | 46.4 | 0.094 | -0.031 | 0.032 | -0.102 | -0.147 | 0.015 | yes | -0.082 | 0.124 | 0/46/54 |

DEV net R 12bp (same rows): 15m LONG-P -0.136, 15m LONG-S1 -0.138, 15m SHORT-P -0.141, 15m SHORT-R1 -0.184, 1h LONG-P -0.071, 1h LONG-S1 -0.089, 1h SHORT-P -0.139, 1h SHORT-R1 -0.172

Control rows (mismatched direction, not gated):

| tf | row | n VAL | net R 12bp | placebo p |
|---|---|---|---|---|
| 15m | LONG-P | 5912 | -0.191 | 0.012 |
| 15m | LONG-S1 | 2572 | -0.131 | 0.002 |
| 15m | SHORT-P | 4280 | -0.042 | 0.002 |
| 15m | SHORT-R1 | 1868 | -0.090 | 0.141 |
| 1h | LONG-P | 2804 | -0.165 | 0.264 |
| 1h | LONG-S1 | 1069 | -0.123 | 0.145 |
| 1h | SHORT-P | 2021 | -0.062 | 0.068 |
| 1h | SHORT-R1 | 769 | -0.138 | 0.536 |

## Reading
- Gross edge is ~0 (-0.14 to +0.10 R); the 12 bp fee costs 0.10-0.15 R per trade even with the 0.5% / 0.6 ATR minimum stop (mean stop 1.0-1.6%), so net is negative. Only the 1h shorts are gross-positive (+0.09 to +0.10 R) and still end at or below zero at taker fee.
- Placebo p < 0.05 on 15m LONG-P, 1h SHORT-P, 1h SHORT-R1 means the trigger beats random entries under the same exit machinery, not that it makes money: the random pool is itself negative. BH keeps those three, but gates 2, 3 and 6 fail.
- Control (mismatched) rows are no worse than matched ones (15m shorts in UP and 1h LONG-P in DOWN are similar), so the phase label adds nothing here.
- Maker row (6 bp, optimistic fill at next open): only 1h SHORT-P (+0.046), 1h SHORT-R1 (+0.032) turn positive; neither has CI low above 0 at taker, and maker fills at the next open are not tested.
- Not tested (PRE_REG): RSI<30 filter, CPR, S2/S3/R2/R3 triggers, tighter/looser variants.

## BTC today (descriptive only, no advice)
Data ends 2026-11-13 20:30 UTC (BTC 68,888). Provisional 11-13 day (H 71,514, L 67,568, C 68,888, not yet closed) gives 11-14 standard pivots: P 69,323, R1 71,079, R2 73,269, R3 75,025, S1 67,133, S2 65,377, S3 63,187. Price sits below P (about 0.6% under). Phase label = DOWN (MA20 slope down, ADX>=20 with DI- above DI+). Under the rule a short-side setup would be a rejection of P 69,323 or R1 71,079; the long reclaim trigger would be a close back above P with the control-phase caveat (long in DOWN is a control row, net -0.165 R on 1h). 12 Nov levels for reference: P 72,264, S1 70,310, S3 67,205.

Files: PRE_REG.md, fetch_15m.py, study.py, run_nk2.py, test_study.py (passes real; STUDY_BUG=1 fails), summary.json. Data in F:\MTS\data_cacheinance\<SYM>USDT_15m.npz.
