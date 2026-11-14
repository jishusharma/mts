# RESULT nk5-nyasia-fresh-coins-1114

**VERDICT: FAIL. NY-asia (hold to 08:00 UTC, 12 bp) on 14 fresh coins, full history: mean net R -0.101 (n 2524), day-cluster CI low -0.254, ex-best-5-days -0.215, placebo p 0.118. Fails gates 2, 3, 4, 5; only n>=100 passes. The source near-miss (+0.074) did not replicate.**

Pre-registered and committed (PRE_REG.md, study.py, test_study.py in commit d195de43c) before any data was fetched or run. Rule, parameters and exit identical to nk5-session-open-15-10-5-1114 NY-asia; no new parameter. Universe (none in the source 20): AVAX DOT UNI AAVE FIL NEAR ALGO XTZ SAND MANA THETA GRT HBAR ENJ, all 14 fetched, none dropped, 5m Binance spot, listing to 2026-11-12 day. Data in F:\MTS\data_cache\binance_fresh\nk5_nyasia\ (16 files, ~11 MB each, none in the worktree).

## Gated rows (matched rule, 12 bp, full history)
| gate | value | pass |
|---|---|---|
| n >= 100 | 2524 trades, 959 trade days | yes |
| mean net R > 0 | -0.101 | NO |
| day-cluster CI low > 0 | -0.254 (trade-level CI low -0.186) | NO |
| ex-best-5 days > 0 | -0.215 | NO |
| placebo p < 0.05 | p 0.118 (placebo mean -0.154: signal beats random entries but both lose) | NO |

Win rate 25.0%, fee 0.145 R, median stop 0.88% of price.

## Other rows (not gated)
| sample | fee | n | mean net R | CI low (day) | ex-best-5 | placebo p |
|---|---|---|---|---|---|---|
| ALL | 6 bp | 2524 | -0.028 | -0.169 | -0.142 | 0.131 |
| pre-2024 | 12 bp | 1392 | -0.253 | -0.404 | -0.371 | 0.93 |
| 2024+ | 12 bp | 1132 | +0.086 | -0.173 | -0.157 | 0.001 |
| 2024+ | 6 bp | 1132 | +0.162 | -0.096 | -0.080 | 0.001 |

Per-coin mean net R at 12 bp: DOT +0.29, GRT +0.22, FIL +0.08, HBAR +0.01, ENJ -0.04, NEAR -0.12, MANA -0.14, ALGO -0.15, UNI -0.18, AAVE -0.19, XTZ -0.21, SAND -0.27, AVAX -0.28, THETA -0.40. Four of 14 positive, none tested individually.

## Context
Phase labelled per coin-day from data to the prior close (UP = ADX14>=20, +DI>-DI, SMA20 5-day slope>0; DOWN mirror; else RANGE). UP trades longs only, DOWN shorts only, RANGE fades both ways.
Regime mix (coin-days, whole fresh history): RANGE 38.1% / DOWN 35.1% / UP 26.7% (source VAL: 39.9 / 35.6 / 24.6, so the mix is comparable). Trades by phase: RANGE 1425, DOWN 647, UP 452; longs 1240, shorts 1284.

## Read
The positive sign exists only in 2024+ (+0.086, same direction as the source's +0.074 on 2024+ data) and reverses badly before 2024 (-0.253). Even in 2024+ the day-cluster CI low is -0.173 and ex-best-5 is -0.157, the same failure pattern as the source. The 2024+ placebo p of 0.001 means the signal beats random same-phase entries in that period, but random entries lose more (placebo mean -0.142), consistent with a weak timing edge on top of a costly long hold, not a tradable rule at 12 bp. The long-hold is regime-dependent (2024-26 trend), not a stable session effect. Recommendation: close this row; no further parameter work on NY-asia.

## Forward rows (BTC/ETH, from 2026-11-13)
n = 0 completed. The 2026-11-13 NY-close anchor is 21:00 UTC and its 08:00 UTC exit on 2026-11-14 had not passed when the study ran (data ended about 21:50 UTC 11-13), so by the pre-registered inclusion rule there is no row yet. Not gated, nothing lost.

Limitations: stop fills at stop price (no gap slippage); HM reconstruction unverified against NK's chart; the 14-coin list was chosen for liquidity and 2021 history before running, several coins start 2019-2020 and their full history is used.

Files: study.py, test_study.py (passes; the causality test fails under STUDY_BUG=1), fetch.py, results.csv, run.log.
