# RESULT_M4: NK5 session open, NY-asia hold to 08:00 UTC, maker entry

**VERDICT: FAIL (gates 3 and 6). Maker entry lifts the VALIDATION net R per filled trade from +0.074 (taker, replicated) to +0.109, with a 92.7% fill rate and placebo p 0.001, but the day-cluster CI lower is -0.110 (trade CI lower -0.006) and the mean after removing the best 5 days is -0.078. Gate 5 is provisional (needs the other 5 rows).**

Spec: ../PRE_REG.md (frozen, unedited). Original: nk5-session-open-15-10-5-1114 (study.py copied verbatim as nk5_orig.py, nothing re-tuned).
Code note: the original RESULT text says RSI 30/70; the CODE (and its PRE_REG) uses a 35/65 band (min of last 4 closed 15m RSI14 <= 35 / max >= 65). This study replicates the CODE.

## Mapping (only thing added)
- Signal, phase gate (ADX14 + SMA20 slope at D-1; LONG in UP/RANGE, SHORT in DOWN/RANGE), NY-cash-close anchor, 20 original coins (incl. EOS to 2025-05, DASH, ZEC, NEO, IOTA, VET): exactly the original.
- Limit L = close of the signal bar (bar closing at the anchor T). Order life 15 x 1m (entry timeframe taken as 15m, the RSI timeframe; OURS, fixed before any result). Stop = L -/+ max(0.5% of L, 0.6 x ATR14 1h) (original formula with entry := L), no target, time stop = open of 1m bar at 08:00 UTC next day (taker). Fill, cancel, fees: PRE_REG fill model via lib/maker_fill.py (entry maker 3bp, stop/time exit taker 6bp).
- Tick = smallest nonzero increment in each symbol's 1m data. All 20 symbols have 1m files (6 fetched: EOS DASH ZEC NEO IOTA VET).

## Taker baseline replication
VALIDATION taker 12bp mean net R, n 1663: **+0.0745** vs original RESULT +0.074 (n 1663 identical): replicated. DEV: -0.243 (n 2599, same n as original). Independent 1m recomputation of the original taker gross R (400 signals per coin, entry at 1m open at T, stop by 1m touch): per-coin mean abs diff vs the 5m original is 0 for most coins and small (<=0.05 R, worst ZEC 0.048, IOTA 0.033) for others (5m vs 1m stop resolution); see results.json.

## Results
| | DEV (to 2023-12) | VALIDATION (2024-) |
|---|---|---|
| signals | 2599 | 1663 |
| fills / fill rate | 2490 / 95.8% | 1541 / 92.7% |
| maker net R per filled trade | -0.236 | **+0.109** |
| maker gross R per filled | -0.117 | +0.241 |
| mean fee in R (filled) | 0.119 | 0.131 |
| net R per signal (miss = 0) | -0.226 | +0.101 |
| taker baseline net R (original, all signals, 12bp) | -0.243 | +0.0745 |
| taker gross R, all signals / filled subset | -0.083 / -0.098 | +0.251 / +0.255 |
| exits (filled) | stop 1824, time 666 | stop 1030, time 511 |
| misses | 109 no-through | 122 no-through |

Adverse selection (VAL): mean gross R of the ORIGINAL model over filled subset minus over all signals = +0.255 - +0.251 = **+0.004 R** (none visible; unfilled signals are barely different). Mean net R, taker baseline, filled subset +0.080 vs all +0.0745. The maker gain (+0.035 R per trade vs taker) is the fee saving (entry 3bp instead of 6bp, about +0.05 R less) partly offset by entering at L instead of next open (maker gross 0.241 vs taker gross filled 0.255).

## PASS gates (VALIDATION, maker net R per filled trade)
| gate | value | result |
|---|---|---|
| 1 filled n >= 100 | 1541 | pass |
| 2 mean net R > 0 | +0.109 | pass |
| 3 CI lower > 0, per trade AND per UTC-day cluster | trade [-0.006, +0.227]; day [-0.110, +0.357] (508 days) | **FAIL** |
| 4 like-for-like placebo p < 0.05 | p = 0.001 (1000 draws at n 1541; placebo mean -0.167; offsets all 0 since L = signal close; placebo pool fill rate 90.9%; stratified by symbol x side of the real signals) | pass |
| 5 BH q=0.05 over 6 rows | provisional: with the other five p set to 1, p x 6 = 0.006 <= 0.05 passes; final value needs M1-M6 p's | provisional pass |
| 6 mean net R > 0 after dropping best 5 UTC days | -0.078 | **FAIL** |

gates_failed: 3, 6. THIN flag: no (fill rate 92.7%).

Regime mix: coin-anchor days DEV RANGE 36.0% / DOWN 32.3% / UP 31.7%; VAL RANGE 39.9% / DOWN 35.6% / UP 24.6% (matches original). VAL matched fills by phase: RANGE 949, DOWN 435, UP 279 signals (shorts 869, longs 794).

## Read
The long hold (about 11-12 h, 30% win rate, a few large winners) stays a trend-carry row: the maker entry changes fees and entry price by a few hundredths of R but not the day-cluster dispersion. The placebo beats random entries again, but the CI and best-5-days gates fail as in the original.

## Limitations / flags
- The 15m order life is a reading of "one entry-timeframe bar" (original entry timeframe is 5m); a 5m life would only lower the fill rate.
- Stop is evaluated on 1m touches here vs 5m in the original (more stop hits are possible on 1m; this is the PRE_REG fill model).
- EOS 1m ends 2025-05-26 (delisted), as its 5m data.
- Gate 5 needs the other rows. The independent checker pass was not run by this agent.

Files: study.py, nk5_orig.py (original, verbatim), test_study.py (5 tests pass; 4 fail with STUDY_BUG=1: limit at next open and the signal bar readable), results.json, run.log, fetch_m4.log.
