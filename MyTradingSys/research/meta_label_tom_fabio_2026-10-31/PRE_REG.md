# PRE_REG: meta-label test on sim-desk trades, Tom VP and Fabio Model C (card meta-label-tom-vp-fabio-trades, operator "run it" 2026-10-31)

Written and committed BEFORE any outcome-by-feature number was read. What was read before this file: the committed `desk-tom_vp-*.json` KPI "filled trades" (to pick the run), the filled-trade counts and the UNCONDITIONAL sd of net R of the regenerated trade lists (`gen_trades.py`). No feature exists yet in code; no win rate, mean R or split by any feature has been looked at. Sister protocol: `system/tasks/meta-label-break-events-layer-features.json`. Every parameter below is OURS (none comes from a trader); fees and slippage are the sim-desk's (Binance 0.02/0.05 %, 0.02 % slippage on market and stop fills, `studies/_bars.py`).

Question: can other MTS layers' state at entry separate winners (net R > 0) from losers in (a) Tom VP and (b) Fabio Model C sim-desk trades?

## 1. Trade lists (DEV 2022-04-01..2024-06-30, filled only, produced by the studies' own `run()`)

| study | setting | filled n | unconditional sd of net R |
|---|---|---|---|
| (a) Tom VP | `desk-tom_vp-c8d2f341`: prior_day FADE, accept_n 6, shift WITH, stop 1 ATR, target POC, BTCUSDT. Picked because it has the MOST filled trades (1812) of the 12 `results/desk-tom_vp-*.json`; the 12 daily-value-area/weekly counts: 1054, 1765, 148, 1038, 1180, 1420, 365, 1640, 1812, 1054, 1247, 918 (of these 2 are prior_week) | 1812 | 0.8271 |
| (b) Fabio Model C | `studies/fabio_v3.py` DEFAULT, model C (m 15, push OFF, f 0.5 %, rule exit = hold to window end, no target) | 518 | 2.3817 |

Entry time t0 = the desk's `touch_t` (open of the bar after the signal bar closed). Every feature may use only bars whose CLOSE time is <= t0 (bar open + bar length <= t0). Funding: a settlement with calc_time <= t0.

## 2. Frozen features (8 layer features; 10 model columns; all computed from data on disk, DEV only)

Existing MTS layer code is used unchanged: `krown_core.bbwp` (FORMULAS 21.5, basis 7, lookback 100), `rsi_core` (Wilder 14), `wavetrend.compute` (10/21/4, zone), `cowen_bmsb.features` (completed-week band, daily SMA50). Bar timeframes (OURS): 1h for BBWP, RSI, WaveTrend, relative volume; 1d for D1 trend and Cowen band. "Aligned" = multiplied by the trade side (+1 long, -1 short), so + means "in the trade's favour".

| # | feature | definition at t0 | model column(s) |
|---|---|---|---|
| 1 | BBWP percentile | BBWP of the last closed 1h bar, 0..100 | bbwp/100 |
| 2 | D1 trend sign | sign(close - SMA50) of the last closed daily bar | d1 x side |
| 3 | Cowen band side | last closed daily close above band top = +1, below band bottom = -1, inside = 0 (band from COMPLETED weeks) | cowen x side |
| 4 | Funding sign | sign of the last funding rate with calc_time <= t0 (data on disk covers DEV: `F:/MTS/Dumps/backtest/raw/fundingRate`, BTCUSDT 2020-01..2026-09, read only up to 2024-06) | fund x side |
| 5 | Session | UTC hour of t0: Asia 21-07 (wrapping), EU 07-13, US 13-21 | sess_eu, sess_us (Asia = base) |
| 6 | RSI zone | RSI14 of last closed 1h bar: >= 60 = +1, <= 40 = -1, else 0 (40/60 = the Malkan layer bands) | rsi x side |
| 7 | WaveTrend zone | `wavetrend` zone of last closed 1h bar: ob2 +2, ob1 +1, mid 0, os1 -1, os2 -2 | wt x side |
| 8 | Relative volume | ln(volume of last closed 1h bar / mean volume of the 24 closed 1h bars before it) | relvol |
| - | trade side (covariate, not a layer) | +1 / -1 | side |

A trade with any feature unavailable (warm-up: Cowen band needs 21 completed weeks, so the first trades of April-June 2022 are dropped; WaveTrend 200 bars; BBWP 106 bars) is dropped from the MODEL (complete-case) but stays in the descriptive table as "not available". The count dropped is reported. For Fabio Model C every entry is in the US window, so the session columns are constant and carry no information (ridge keeps them at 0); stated, not hidden.

## 3. Model, CV, scoring

- Logistic regression, y = (net R > 0), L2 ridge lambda = 1.0 on standardized columns (train-fold mean and sd), intercept unpenalised, IRLS (Newton), 50 iterations max. No tuning of lambda or anything else.
- Blocked cross-validation, week-purged: DEV trades are cut into K = 6 contiguous blocks of equal numbers of ISO weeks; each block is scored by a model trained on the other five blocks after dropping every training trade whose entry week is within 1 week (before or after) of the test block's weeks (purge + embargo; Tom trades last at most a day, Fabio at most 390 minutes). Every complete-case trade gets exactly one out-of-fold score.
- Buckets: out-of-fold score terciles (equal-size thirds by score rank).
- Primary metric: top-tercile mean net R (fee-net). 95 % CI: day-block bootstrap (resample UTC entry days with replacement, 2000 draws, seed 20261031, percentile). Also reported: bottom tercile, top-minus-bottom spread (same bootstrap), and the middle tercile.
- Placebo: shuffled labels, 300 shuffles (seed 20261031): permute the trades' outcomes (net R and its win flag together) across trades with features and times fixed, re-run the whole purged CV, record the top-minus-bottom spread. The real spread must exceed the placebo 95th percentile; placebo p = (1 + #(placebo >= real)) / (1 + 300).

## 4. Pass rule (per study)

PASS = top-tercile fee-net mean > 0 with the 95 % day-block CI lower bound > 0 on DEV AND the real spread above the placebo 95th percentile. Sim-desk verdict words: PASSED = the rule is met; NOT ENOUGH DATA = fewer than 100 trades in the top tercile; otherwise FAILED. ONLY if a study passes on DEV: exactly one VALIDATION read (2024-07-01..2025-06-30) of that frozen model, reported as same sign or not; HOLDOUT is never touched. If a study fails on DEV, VALIDATION is not read. No trading verdict beyond this rule.

## 5. Power (n = 7.849 (sd/delta)^2, FORMULAS-style two-sided 5 % / 80 % power, computed independently: (1.96 + 0.8416)^2 = 7.849)

delta_min = sd x sqrt(7.849 / n). Tercile size is about (complete-case n)/3.

| study | sd | approx top-tercile n | delta_min (R) |
|---|---|---|---|
| Tom VP | 0.8271 | ~555 (1812 less warm-up drops, /3) | 0.8271 x sqrt(7.849/555) = 0.098 |
| Fabio C | 2.3817 | ~160 (518 less drops, /3) | 2.3817 x sqrt(7.849/160) = 0.527 |

So Tom can resolve a +0.10 R shift in a tercile mean; Fabio Model C (huge sd: no target, tiny stops) can only resolve about +0.5 R, i.e. a Fabio null is weak evidence. The exact n and delta_min are recomputed from the realised tercile sizes in REPORT.md (formula unchanged).

## 6. Deflation and descriptive single-feature splits

Features tried per study: 8 (10 columns, one model fit, no feature selection). Across both studies 16 feature-study pairs. Single-feature splits are DESCRIPTIVE only (they do not enter the pass rule): for each of the 8 features, trades are grouped by the raw reading (BBWP: compression <= 30 / normal / expansion >= 85 (FORMULAS 21.5); D1 trend up / down; Cowen above / inside / below band; funding positive / zero / negative; session Asia / EU / US; RSI < 40 / 40-60 / > 60; WaveTrend oversold / mid / overbought; relative volume low / mid / high third by the sample's own tertile cut points), each group's mean net R gets a day-block bootstrap CI at the Bonferroni level 1 - 0.05/8 (99.375 %), and groups are labelled "distinguishable from zero" only if that deflated CI excludes 0. The "luck" level for the best of N = 16 no-edge tries, sd x sqrt(2 ln 16) / sqrt(n), is printed beside the top-tercile mean (desk.luck formula).

## 7. Tests and exports

- `test_features.py`: perturbation test (all 1m bars at or after t0 are replaced with garbage; every feature at t0 must be bit-identical) plus a meta-test that a deliberately leaky implementation (bar counted as closed at its OPEN) is caught. It is also run once against the leaky variant to show it fails.
- Export: one sim-desk result JSON per study (`desk-meta_label_tom_vp`, `desk-meta_label_fabio_c` kinds backtest) with exactly three parts: (1) a table "Layer reading | trades | win % | average R after fees", one row per reading value, each feature's rows summing to the study's filled-trade count; (2) one verdict line "Best third by filter: +x R (range a..b) vs random third: +y R -> PASSED / FAILED / NOT ENOUGH DATA"; (3) the 3 winner / 3 loser example charts of the best third and of the worst third. A test checks these parts and the count sums.
