**Verdict: FAIL. NKN-06 pivot R2/R3 (S2/S3), 3 primary cells, validation 2024-01-01 onward, fee-net at 12 bp taker. P1 FAIL (n VAL 276, net12 -0.183 R); P2 FAIL (n VAL 201, net12 -0.430 R); P3 UNDERPOWERED (n VAL 0, net12 n/a R).**

Regime mix: coin-day trend phase DEV UP 31% / DOWN 32% / RANGE 36%; VAL UP 25% / DOWN 35% / RANGE 40%. Primary phase cells as share of coin-days: P1 UP x MARKUP DEV 18.7%, VAL 15.8%; P2 DOWN x MARKDOWN DEV 15.2%, VAL 12.2% (30385 DEV and 20960 VAL labelled coin-days, 20 coins). Flag: mixed (no single phase over 50%).

Total cells tried: 15 (3 primary, 11 controls, 1 placebo C12). Primary cells: 3. Underpowered primary cells: 1. Code commit at run: `13967cd392ecc9824f3547b93155fae84823a823`; PRE_REG last commit: `c9f514b9b08bd0b1a61edbb4bfc4ee5aa76c175a`.

## PRIMARY cells (validation, 12 bp taker is the verdict; 6 bp maker secondary)

| cell | phase tested | context conditions (SOURCED/OURS) | crypto translation | layer agreement | level type | timeframe | side | n DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day-cluster CI low | ex-best-5 | placebo p | BH q | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | UP x MARKUP | R2 break leads to R3 (FzNDQm7wC_s 00:09:44) SOURCED idea; pivots, 1h, fresh cross, at-level <=1 ATR, 1.5R room, day-end exit OURS | UTC 00:00 day pivots; no gap; closed bars only | V0 rule alone | daily floor pivot R2 trigger, R3 target | 1h | long | 525 | 276 | -0.030 | -0.183 | -0.106 | 27.2 | -0.376 | -0.384 | -0.324 | 0.868 | 1.000 | FAIL |
| P2 | DOWN x MARKDOWN | mirror of P1 (S2 to S3), mirror OURS | UTC 00:00 day pivots; no gap; closed bars only | V0 rule alone | daily floor pivot S2 trigger, S3 target | 1h | short | 364 | 201 | -0.264 | -0.430 | -0.347 | 20.9 | -0.622 | -0.735 | -0.778 | 0.636 | 1.000 | FAIL |
| P3 | UP x MARKUP (labels of the entry day) | three days sitting at R3 (a8RP5ftOfGo 00:13:56) SOURCED idea (count 3); 0.5% band, 5-day hold OURS | UTC 00:00 day pivots; no gap; closed bars only | V0 rule alone | daily floor pivot R3, three daily closes under it | 1d | long | 0 | 0 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 1.000 | 1.000 | UNDERPOWERED |

Gates per primary cell (all needed for PASS): net12 > 0, trade CI low > 0, day-cluster CI low > 0, ex-best-5 days > 0, placebo p < 0.05, BH q <= 0.10 over the 3 primaries, n VAL >= 200 (100-199: numbers shown, cannot PASS; under 100: UNDERPOWERED).

### Placebo and hit rate (primary cells)

| cell | matched real trades | real mean net R (matched) | placebo mean net R | placebo p | R3/S3 hit rate | share time-exit | skipped by 1.5R room VAL | no entry in day VAL |
|---|---|---|---|---|---|---|---|---|
| P1 | 276 | -0.183 | -0.103 | 0.868 | +0.22 | +0.07 | 74 | 20 |
| P2 | 201 | -0.430 | -0.402 | 0.636 | +0.15 | +0.09 | 31 | 12 |
| P3 | 0 | n/a | n/a | 1.000 | n/a | n/a | n/a | n/a |

'Beats placebo' and 'profitable' are separate: a cell can beat random entries (which lose about 0.2 R after fees) and still have net R below zero.

## CONTROL cells (never pooled with primary; 15 cells in total beside any positive row)

| cell | phase | layer / variant | at/away | tf | side | n DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day CI low | ex-best-5 | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | RANGE x MARKUP | V0 | at level | 1h | long | 351 | 226 | +0.141 | -0.033 | +0.054 | 34.1 | -0.241 | -0.296 | -0.235 | does the trend label add |
| C2 | UP x cycle not MARKUP | V0 | at level | 1h | long | 313 | 117 | +0.072 | -0.099 | -0.013 | 34.2 | -0.364 | -0.378 | -0.284 | does the cycle label add |
| C3 | DOWN x MARKDOWN, long (mismatched side) | V0 | at level | 1h | long | 311 | 205 | +0.019 | -0.162 | -0.072 | 28.3 | -0.383 | -0.484 | -0.472 | mismatch, descriptive |
| C4 | UP x MARKUP | V1 | at level | 1h | long | 435 | 216 | +0.060 | -0.097 | -0.018 | 29.6 | -0.319 | -0.319 | -0.249 | Malkan BULL (daily) |
| C5 | UP x MARKUP | V1opp | at level | 1h | long | 4 | 2 | +1.097 | +0.920 | +1.008 | 50.0 | -1.151 | -1.151 | n/a | Malkan BEAR (layer adds?) |
| C6 | UP x MARKUP | V2 | at level | 1h | long | 414 | 209 | +0.076 | -0.081 | -0.003 | 30.1 | -0.299 | -0.309 | -0.238 | Malkan BULL + 4h %B>=0.5 |
| C7 | UP x MARKUP | V0 | away from level | 1h | long | 18 | 14 | +0.419 | +0.305 | +0.362 | 57.1 | -0.332 | -0.329 | -0.624 | level effect |
| C8 | UP x MARKUP | V0 | at level | 15m | long | 719 | 408 | +0.072 | -0.132 | -0.030 | 24.3 | -0.340 | -0.345 | -0.295 | 15m trigger |
| C9 | UP x MARKUP | V0 | at level | 4h | long | 132 | 82 | +0.065 | -0.022 | +0.022 | 41.5 | -0.294 | -0.312 | -0.256 | 4h trigger |
| C10 | UP x MARKUP | V0+BTC | at level | 1h | long | 472 | 251 | -0.025 | -0.175 | -0.100 | 27.5 | -0.378 | -0.388 | -0.320 | BTC daily close > SMA20 and SMA50 |
| C11 | UP x MARKUP | V0 | at level | 1h | long | 525 | 276 | -0.021 | -0.174 | -0.098 | 25.7 | -0.365 | -0.375 | -0.314 | close-based exit: 1h close back under R2 |
| C12 | UP x MARKUP | placebo for P1 | - | 1h | long | - | 276 matched | - | real -0.183 vs placebo -0.103 | - | - | - | - | - | p 0.868 |

Controls with positive net R 12bp on VAL: C5, C7 (read against 15 cells tried; no control carries a verdict).

## Event study (same signals before the 1.5R room skip; descriptive, cannot PASS)

| set | n DEV | n VAL | gross R VAL | net R 12bp VAL |
|---|---|---|---|---|
| P1_event | 598 | 350 | -0.028 | -0.181 |
| P2_event | 426 | 232 | -0.248 | -0.414 |

Descriptive P1 VAL columns (no filter): stacked overhead (weekly R1 or prior-week high between entry and R3) n 57 net12 +0.050; clear n 219 net12 -0.243. Entry-hour counts: {'1': 3, '2': 9, '3': 7, '4': 20, '5': 12, '6': 11, '7': 12, '8': 16, '9': 13, '10': 15, '11': 8, '12': 20, '13': 15, '14': 21, '15': 24, '16': 20, '17': 6, '18': 12, '19': 13, '20': 6, '21': 7, '22': 6}.

## Skipped signals per cell (room rule, no entry in the day, busy)

| cell | DEV room | DEV no entry | VAL room | VAL no entry | VAL busy |
|---|---|---|---|---|---|
| P1 | 73 | 36 | 74 | 20 | 0 |
| P2 | 62 | 25 | 31 | 12 | 0 |
| C1 | 66 | 25 | 54 | 12 | 0 |
| C2 | 50 | 24 | 57 | 6 | 0 |
| C3 | 62 | 24 | 57 | 8 | 0 |
| C4 | 58 | 30 | 64 | 15 | 0 |
| C5 | 0 | 1 | 0 | 1 | 0 |
| C6 | 51 | 30 | 58 | 15 | 0 |
| C7 | 193 | 18 | 120 | 7 | 0 |
| C8 | 20 | 25 | 30 | 4 | 0 |
| C9 | 163 | 105 | 104 | 47 | 0 |
| C10 | 69 | 30 | 68 | 18 | 0 |
| C11 | 73 | 36 | 74 | 20 | 0 |

## Provenance (cache = F:/MTS/data_cache/binance_spot, 15m, read-only; all timeframes resampled from it)

| coin | key | first bar (UTC) | last bar (UTC) | bars | gaps (steps > 15m) |
|---|---|---|---|---|---|
| BTC | t | 2019-01-01 00:00 | 2026-11-13 20:15 | 275620 | 21 |
| ETH | t | 2019-01-01 00:00 | 2026-11-13 20:15 | 275620 | 21 |
| BNB | t | 2019-01-01 00:00 | 2026-11-13 20:15 | 275620 | 21 |
| XRP | t | 2019-01-01 00:00 | 2026-11-13 20:15 | 275620 | 21 |
| ADA | t | 2019-01-01 00:00 | 2026-11-13 20:15 | 275620 | 21 |
| DOGE | ts | 2019-07-05 12:00 | 2026-11-13 20:30 | 257882 | 18 |
| SOL | t | 2020-08-11 06:00 | 2026-11-13 20:15 | 219324 | 10 |
| LTC | ts | 2019-01-01 00:00 | 2026-11-13 20:30 | 275622 | 21 |
| LINK | ts | 2019-01-16 10:00 | 2026-11-13 20:30 | 274142 | 21 |
| TRX | ts | 2019-01-01 00:00 | 2026-11-13 20:30 | 275622 | 21 |
| DOT | ts | 2020-08-18 23:00 | 2026-11-13 20:30 | 218586 | 10 |
| AVAX | ts | 2020-09-22 06:30 | 2026-11-13 20:30 | 215292 | 10 |
| ATOM | ts | 2019-04-29 04:00 | 2026-11-13 20:30 | 264302 | 20 |
| ETC | ts | 2019-01-01 00:00 | 2026-11-13 20:30 | 275622 | 21 |
| BCH | ts | 2019-11-28 10:00 | 2026-11-13 20:30 | 243923 | 15 |
| XLM | ts | 2019-01-01 00:00 | 2026-11-13 20:30 | 275622 | 21 |
| UNI | ts | 2020-09-17 03:00 | 2026-11-13 20:30 | 215786 | 10 |
| NEAR | ts | 2020-10-14 05:00 | 2026-11-13 20:30 | 213186 | 10 |
| FIL | ts | 2020-10-15 17:00 | 2026-11-13 20:30 | 213042 | 10 |
| ALGO | ts | 2019-06-22 00:00 | 2026-11-13 20:30 | 259178 | 18 |

Loader asserts: key is `ts` or `t`, timestamps strictly increasing, every step a multiple of 15 minutes (gaps are counted, resampled bars are built from complete groups only, a bar group with a hole is dropped). BTC cycle labels recomputed from `btc_daily.csv` plus the cached 15m; informational comparison with the shared phase_daily.csv: {'days_compared': 4532, 'differing': 0}.

## Deviations

None. The code ran once as committed.

## Parameter labels

SOURCED: R2 break leads to R3 (FzNDQm7wC_s 00:09:44), three days at R3 (a8RP5ftOfGo 00:13:56), zones not lines (FzNDQm7wC_s 00:04:44), close-based stop spirit (control C11 only), Malkan 40/60/20 (Malkan layer). OURS (one value each, no grid): classic floor pivots from the prior UTC day, 1h trigger, fresh cross first per day, 00:00 bar skipped, ATR14 simple mean, at-level cap 1.0 ATR, R floor max(0.5% of entry, 0.6 ATR14, entry minus level), room rule 1.5 R, day-end time exit, coin trend phase (SMA20 slope 5-day lag, ADX14 >= 20 with DI direction), cycle state thresholds (MTS_BRAINS_SPEC_1114), V1 daily Malkan timeframe, V2 %B 20/2 with threshold 0.50, P3 band 0.5% and 5-day hold, placebo +-0.3 ATR distance match. No parameter is NK's own.


## Context (added by hand after the run; the sections above are generator output)
Order of 2026-11-14: NK rules are not tested blindly. Phase cells are fixed before the day starts: P1 = coin trend UP x BTC cycle MARKUP (long), P2 = DOWN x MARKDOWN (short mirror); every other phase combination is a control (C1 RANGE x MARKUP, C2 UP x not-MARKUP, C3 DOWN x MARKDOWN long, mismatched side) and is never pooled. Labels use data through the prior UTC close only (trend: SMA20 slope with 5-day lag plus ADX14 >= 20; cycle: MTS_BRAINS_SPEC_1114 thresholds recomputed from `btc_daily.csv` plus cached 15m). Pivots: classic floor pivots from the prior UTC day; trigger first 1h cross of R2 inside 1 ATR; target R3; 1.5 R room rule; day-end time exit; 12 bp taker fee-net (6 bp per leg, shared convention of nkp2). Not a forecast and not advice: a FAIL here means this exact frozen rule did not show a fee-net edge on 2024+.

## Per-phase read (VAL 2024+, 12 bp, net R per trade; n = trades)
| phase cell | role | n VAL | net R | day-cluster CI low | placebo (random entries, same coin/cell/hour/distance) |
|---|---|---|---|---|---|
| UP x MARKUP long (P1) | PRIMARY | 276 | -0.183 | -0.384 | placebo mean -0.103, p 0.868 (real is worse than random entries) |
| DOWN x MARKDOWN short (P2) | PRIMARY | 201 | -0.430 | -0.735 | placebo mean -0.402, p 0.636 |
| UP x MARKUP daily, 3 days at R3 (P3) | PRIMARY | 0 | n/a | n/a | n/a |
| RANGE x MARKUP long (C1) | control | 226 | -0.033 | -0.296 | none |
| UP x not-MARKUP long (C2) | control | 117 | -0.099 | -0.378 | none |
| DOWN x MARKDOWN long (C3) | control | 205 | -0.162 | -0.484 | none |
Net R is negative in every phase cell with n >= 100; gross R is about zero (P1 -0.030, P2 -0.264), so cost is not the only cause for P2. Controls with positive net R (C5 n 2, C7 n 14) are too thin to read. The room rule skips 74 of P1 VAL signals and 31 of P2. P1 reaches R3 on 22% of trades (P2 reaches S3 on 15%).

## Findings added after the run
- P3 never fires: the frozen condition (three consecutive daily closes each within 0.5% under the R3 in force on day 3) has 0 events on DEV and VAL, before any phase filter. Independent check from the raw 15m cache (daily bars rebuilt separately, 20 coins, 2019-2026): 0 events at the 0.5% band (5890 events if the band were 5%, which was not registered and is NOT used). So P3 is UNDERPOWERED by construction, not a measured null, and the "three days at R3" claim is untested by this study.
- P1 and P2 are powered on n but FAIL: net R below zero, every CI low below zero, placebo not beaten, BH q 1.000.
- Report fix: `study.py run` computed and wrote `results.json`, then crashed in `make_result` (KeyError 'VAL' on the P3 row of the placebo table, because P3 has no skipped-signal counts). Fixed by `.get` in that one table row; RESULT.md was re-rendered from the unchanged `results.json` (no recomputation, numbers identical to the run). Under PRE_REG this is a report-format bug fix, to ship as a separate commit; the "Deviations: None" line above (generator text) should read: one report-rendering bug fixed after the run, no parameter, cell or number changed. `run1.log` / `run1.err` hold the original run output including the traceback.
- Tests: `test_study.py` 18 passed before the run and after the fix. Code commit at run `13967cd39` (`results.json` code_commit), PRE_REG commit `c9f514b9b`.
