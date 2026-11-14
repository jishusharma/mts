**VERDICT: FAIL. 0 of 6 primary cells pass VAL (2024+) at 12 bp fee-net. Cell 1 (DOWN x MARKDOWN short, V0): n 749, net +0.041 R, trade CI low -0.051, day-cluster CI low -0.116, BH q 0.635. Cells 2 and 3 (V1, V2 short) are THIN (n 162 and 153) with net +0.207 and +0.209 R, day-cluster CI low -0.073 and -0.065, BH q 0.220, so cannot PASS. Cells 4-6 (UP x MARKUP long) are net negative.**

## Context
Phase x BTC label cells per PRE_REG.md (DOWN x MARKDOWN short, UP x MARKUP long), 15m trigger at the daily SMA20, HM gate, 20 Binance spot coins, taker 12 bp round trip (6 bp per leg, spot-equivalent, no funding), fee constants own dict `RT_BP` in study.py. DEV <= 2023-12-31, VAL >= 2024-01-01, one run on VAL. Counts were taken on DEV only before the run (`counts_dev.txt`): primary cells 1-6 had 2630 / 448 / 423 / 2336 / 457 / 447 DEV candidates, so none was underpowered up front. Regime mix: see the line below the verdict (coin-day UP/DOWN/RANGE share and BTC label share, DEV and VAL).

## Reading (no forecast)
- Cell 1 beats the placebo (p 0.003) but is not profitable enough: net +0.041 R with both CI lows below zero. Beating random is not profit.
- V1/V2 short cells have a positive mean and trade CI low just above 0 (0.003, 0.005) but day-cluster CI low is negative and n is below 200 (THIN); the layer count shrinks cells to roughly 21% of V0 n.
- At-level beats away-level for the short side (0.041 vs -0.172; 0.207 vs -0.243; 0.209 vs -0.247) and not for the long side (-0.065 vs -0.057; -0.073 vs +0.056; -0.068 vs +0.100). The away V1/V2 long controls are positive but are controls and carry no verdict.
- Controls: C4 (long in DOWN x MARKDOWN) -0.197 R and cell 4 -0.065 R; FP control cell 19 short +0.351 R at n 68 (UNDERPOWERED, control only, not a rescue).

## Deviations
None. No cell, parameter or horizon changed after the first run; PRE_REG.md written before the run.

## Tests
`python -m pytest test_study.py`: 16 passed. Mutation check: charging fee on the entry leg only makes `test_fee_on_both_legs_hand_number` fail (0.05 vs 0.1005). Look-ahead poke tests (`test_lookahead_has_teeth`, truncation test) pass. Lint: `scripts/dev/lookahead_lint.py` hits are allowlisted FAIL-pattern entries (entry at next open) plus two NEW WARN fullsample-quantile hits (bootstrap CI percentiles, not look-ahead).

## Files
PRE_REG.md, study.py, test_study.py, results.json, RESULT_AUTO.md (generator output, same tables), counts_dev.txt, run1.log, run1.err.

Regime mix: coin-days DEV UP 31.4% / DOWN 32.0% / RANGE 36.6% (31386 coin-days); VAL UP 24.8% / DOWN 35.1% / RANGE 40.1% (20960). BTC cycle label share DEV: MARKUP 33.1%, MARKDOWN 23.8%, other 43.1%, blank 0.0%; VAL: MARKUP 30.6%, MARKDOWN 18.9%, other 50.5%, blank 0.0%.

## PRIMARY cells (VALIDATION, signal bar >= 2024-01-01, 15m trigger, level = daily SMA20 at-level, HM gate on)

| cell | phase tested | context conditions | crypto translation | layer agreement | level type | TF | side | n DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day-cluster CI low | ex-best-5 | placebo p | BH q | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | DOWN x MARKDOWN | PRE_REG conds 1-8 (SMA20 SOURCED; windows, bands OURS) | BTC cycle label replaces index filter; no session/gap | V0 | daily SMA20 at-level | 15m | short | 1483 | 749 | 0.130 | 0.041 | 0.085 | 38.5 | -0.051 | -0.116 | 0.018 | 0.003 | 0.635 | FAIL |
| 2 | DOWN x MARKDOWN | PRE_REG conds 1-8 (SMA20 SOURCED; windows, bands OURS) | BTC cycle label replaces index filter; no session/gap | V1 | daily SMA20 at-level | 15m | short | 325 | 162 | 0.296 | 0.207 | 0.251 | 45.7 | 0.003 | -0.073 | 0.135 | 0.001 | 0.220 | FAIL |
| 3 | DOWN x MARKDOWN | PRE_REG conds 1-8 (SMA20 SOURCED; windows, bands OURS) | BTC cycle label replaces index filter; no session/gap | V2 | daily SMA20 at-level | 15m | short | 313 | 153 | 0.298 | 0.209 | 0.254 | 45.8 | 0.005 | -0.065 | 0.134 | 0.002 | 0.220 | FAIL |
| 4 | UP x MARKUP | PRE_REG conds 1-8 (SMA20 SOURCED; windows, bands OURS) | BTC cycle label replaces index filter; no session/gap | V0 | daily SMA20 at-level | 15m | long | 1423 | 713 | 0.017 | -0.065 | -0.024 | 33.0 | -0.175 | -0.220 | -0.124 | 0.516 | 0.762 | FAIL |
| 5 | UP x MARKUP | PRE_REG conds 1-8 (SMA20 SOURCED; windows, bands OURS) | BTC cycle label replaces index filter; no session/gap | V1 | daily SMA20 at-level | 15m | long | 346 | 211 | 0.003 | -0.073 | -0.035 | 29.4 | -0.329 | -0.347 | -0.251 | 0.628 | 0.762 | FAIL |
| 6 | UP x MARKUP | PRE_REG conds 1-8 (SMA20 SOURCED; windows, bands OURS) | BTC cycle label replaces index filter; no session/gap | V2 | daily SMA20 at-level | 15m | long | 341 | 209 | 0.008 | -0.068 | -0.030 | 29.7 | -0.324 | -0.354 | -0.247 | 0.581 | 0.762 | FAIL |

Placebo p = random same-coin, same phase x label, same side, hour-matched entries with identical stop/exit/fee (1000 draws). A low placebo p means 'beats random', not 'profitable'. Gates need net R > 0 AND both CI lows > 0 AND ex-best-5 > 0 AND placebo p < 0.05 AND BH q <= 0.10 AND n VAL >= 200 (n 100-199 = THIN, cannot PASS; n < 100 = UNDERPOWERED).

## CONTROL cells (never pooled with the primaries, descriptive; no gate or placebo)

| cell | role | description | n DEV | net R 12bp DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day-cluster CI low | ex-best-5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7 | CONTROL | short DOWNxMARKDOWN V0 away | 3555 | -0.098 | 2120 | -0.084 | -0.172 | -0.128 | 31.9 | -0.228 | -0.298 | -0.183 |
| 8 | CONTROL | short DOWNxMARKDOWN V1 away | 294 | 0.058 | 194 | -0.150 | -0.243 | -0.197 | 30.9 | -0.419 | -0.503 | -0.307 |
| 9 | CONTROL | short DOWNxMARKDOWN V2 away | 245 | 0.104 | 170 | -0.152 | -0.247 | -0.200 | 30.6 | -0.435 | -0.512 | -0.319 |
| 10 | CONTROL | long UPxMARKUP V0 away | 5358 | -0.038 | 2974 | 0.019 | -0.057 | -0.019 | 35.4 | -0.110 | -0.144 | -0.077 |
| 11 | CONTROL | long UPxMARKUP V1 away | 407 | -0.041 | 273 | 0.131 | 0.056 | 0.093 | 37.4 | -0.171 | -0.248 | -0.093 |
| 12 | CONTROL | long UPxMARKUP V2 away | 331 | 0.039 | 218 | 0.174 | 0.100 | 0.137 | 38.1 | -0.167 | -0.230 | -0.085 |
| 13 | CONTROL C1 | short DOWNx!MARKDOWN V0 at | 1145 | -0.044 | 1204 | 0.122 | 0.033 | 0.078 | 38.3 | -0.043 | -0.082 | 0.018 |
| 14 | CONTROL C2 | long UPx!MARKUP V0 at | 969 | -0.059 | 476 | 0.021 | -0.065 | -0.022 | 35.7 | -0.178 | -0.202 | -0.100 |
| 15 | CONTROL C3 | short UPxMARKUP V0 at | 581 | -0.081 | 399 | 0.087 | 0.002 | 0.044 | 36.1 | -0.127 | -0.171 | -0.039 |
| 16 | CONTROL C4 | long DOWNxMARKDOWN V0 at | 535 | -0.100 | 281 | -0.106 | -0.197 | -0.152 | 28.5 | -0.332 | -0.364 | -0.251 |
| 17 | CONTROL C5 | short RANGEx* V0 at | 3655 | -0.092 | 2472 | 0.081 | -0.010 | 0.035 | 36.2 | -0.060 | -0.088 | -0.020 |
| 18 | CONTROL C6 | long RANGEx* V0 at | 3356 | -0.040 | 2033 | -0.046 | -0.136 | -0.091 | 31.0 | -0.188 | -0.206 | -0.146 |
| 19 | CONTROL FP | cell1 + FP split | 109 | 0.043 | 68 | 0.439 | 0.351 | 0.395 | 39.7 | 0.063 | 0.019 | 0.195 |
| 20 | CONTROL FP | cell4 + FP split | 141 | -0.051 | 97 | -0.039 | -0.119 | -0.079 | 25.8 | -0.315 | -0.309 | -0.238 |
| 21 | CONTROL WC | cell1 + weekly confluence | 103 | -0.093 | 6 | 0.659 | 0.570 | 0.615 | 66.7 | -0.416 | -0.422 | -1.101 |
| 22 | CONTROL WC | cell4 + weekly confluence | 123 | 0.090 | 69 | 0.122 | 0.035 | 0.078 | 39.1 | -0.270 | -0.306 | -0.146 |

## At-level vs away-from-level, same cell (VALIDATION net R 12bp, n)

| variant | cell at | at-level | cell away | away-level |
|---|---|---|---|---|
| short V0 | 1 | 0.041 (n 749) | 7 | -0.172 (n 2120) |
| short V1 | 2 | 0.207 (n 162) | 8 | -0.243 (n 194) |
| short V2 | 3 | 0.209 (n 153) | 9 | -0.247 (n 170) |
| long V0 | 4 | -0.065 (n 713) | 10 | -0.057 (n 2974) |
| long V1 | 5 | -0.073 (n 211) | 11 | 0.056 (n 273) |
| long V2 | 6 | -0.068 (n 209) | 12 | 0.100 (n 218) |

Total cells tried: 22. Primary cells: 6 (BH family m = 6). Placebo rows (6) are gate components.
Candidates simulated (all cells, before de-overlap): 112376. Exit reasons: {'runner': 32183, 'stop': 63397, 'time': 12817, 'close_through': 3979}.

## Provenance

phase_daily.csv sha256 b2cc2314324609fce7c1666912e0b7064e699dde275057456aa4ad311f867365. Source: F:/MTS/data_cache/binance/<SYM>USDT_15m.npz (key `a`, [t,o,h,l,c,v]); every higher timeframe is resampled from that one 15m series per coin.

| coin | first bar (UTC) | last bar (UTC) | rows | gaps | filled bars |
|---|---|---|---|---|---|
| BTC | 2019-01-01 00:00 | 2026-11-13 20:30 | 275621 | 21 | 270 |
| ETH | 2019-01-01 00:00 | 2026-11-13 20:30 | 275621 | 21 | 270 |
| BNB | 2019-01-01 00:00 | 2026-11-13 20:30 | 275621 | 21 | 270 |
| XRP | 2019-01-01 00:00 | 2026-11-13 20:30 | 275621 | 21 | 270 |
| ADA | 2019-01-01 00:00 | 2026-11-13 20:30 | 275621 | 21 | 270 |
| DOGE | 2019-07-05 12:00 | 2026-11-13 20:45 | 257882 | 18 | 202 |
| SOL | 2020-08-11 06:00 | 2026-11-13 20:45 | 219326 | 10 | 94 |
| LTC | 2019-01-01 00:00 | 2026-11-13 20:45 | 275622 | 21 | 270 |
| LINK | 2019-01-16 10:00 | 2026-11-13 20:45 | 274142 | 21 | 270 |
| TRX | 2019-01-01 00:00 | 2026-11-13 20:45 | 275622 | 21 | 270 |
| DOT | 2020-08-18 23:00 | 2026-11-13 20:45 | 218586 | 10 | 94 |
| AVAX | 2020-09-22 06:30 | 2026-11-13 20:45 | 215292 | 10 | 94 |
| ATOM | 2019-04-29 04:00 | 2026-11-13 20:45 | 264302 | 20 | 246 |
| ETC | 2019-01-01 00:00 | 2026-11-13 20:45 | 275622 | 21 | 270 |
| BCH | 2019-11-28 10:00 | 2026-11-13 20:45 | 243923 | 15 | 153 |
| XLM | 2019-01-01 00:00 | 2026-11-13 21:00 | 275623 | 21 | 270 |
| UNI | 2020-09-17 03:00 | 2026-11-13 21:00 | 215787 | 10 | 94 |
| NEAR | 2020-10-14 05:00 | 2026-11-13 21:00 | 213187 | 10 | 94 |
| FIL | 2020-10-15 17:00 | 2026-11-13 21:00 | 213043 | 10 | 94 |
| ALGO | 2019-06-22 00:00 | 2026-11-13 21:00 | 259179 | 18 | 202 |
