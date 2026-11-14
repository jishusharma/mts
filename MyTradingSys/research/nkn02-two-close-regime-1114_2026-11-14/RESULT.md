**Verdict: UNDERPOWERED** (NKN-02 two-close regime switch, 6 primary cells of 28 tried; daily, 20 spot coins, fee-net, VALIDATION = signal bar on/after 2024-01-01)

Regime mix: DEV: UP 31.5%, DOWN 32.0%, RANGE 36.6% (coin-days, trend phase), above own SMA200 40.1% | VAL: UP 24.7%, DOWN 35.2%, RANGE 40.1% (coin-days, trend phase), above own SMA200 43.0% | BTC cycle days DEV: BEAR 800, BASE 787, BULL 239; VAL: BEAR 336, BASE 148, BULL 563

Code commit (study.py run): bcf7668ca537ba903a6cd81de2b4185addf91447. Total cells tried: 28. Primary cells: 6. Controls (22) are descriptive, never pooled, not in BH. Episodes (VAL): cell 1: 10, cell 2: 5, cell 3: 1, cell 4: 18, cell 5: 16, cell 6: 11.

## PRIMARY table (VALIDATION unless stated; net R at 12 bp taker is the verdict basis)

| cell | phase tested | context conditions (S=SOURCED, O=OURS) | crypto translation | layer agreement | level type | timeframe | side | n DEV | n VAL | gross R | net R 12bp | net R 6bp | win % | trade CI low | day-cluster CI low | ex-best-5 | placebo p | BH q | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 L-TURN V0 | regime TURN (counter-trend entry into new trend) | S: 2 closes vs SMA20/SMA50/SMA200 (a8RP5ftOfGo, PLJda-dtBIc); O: 10-of-30 drop-arming, cycle not BULL + coin DOWN/RANGE at prior close; S: stop = 2 closes back (lmhqooBqJWU) | UTC daily bar, signal 00:00 UTC close, entry next open (O) | V0 rule alone | SMA200 (all distances; AT/AWAY in controls) | 1d | long | 56 | 17 | 0.304 | 0.295 | 0.299 | 29.4 | -0.283 | -0.301 | -0.451 | 0.233 | 0.847 | UNDERPOWERED (n VAL 17 < 100) |
| 2 L-TURN V1 | regime TURN (counter-trend entry into new trend) | S: 2 closes vs SMA20/SMA50/SMA200 (a8RP5ftOfGo, PLJda-dtBIc); O: 10-of-30 drop-arming, cycle not BULL + coin DOWN/RANGE at prior close; S: stop = 2 closes back (lmhqooBqJWU) | UTC daily bar, signal 00:00 UTC close, entry next open (O) | V1 = V0 + ADX14>=20 & DI sign (O) | SMA200 (all distances; AT/AWAY in controls) | 1d | long | 26 | 9 | 0.145 | 0.138 | 0.141 | 33.3 | -0.284 | -0.380 | -0.425 | 0.349 | 0.847 | UNDERPOWERED (n VAL 9 < 100) |
| 3 L-TURN V2 | regime TURN (counter-trend entry into new trend) | S: 2 closes vs SMA20/SMA50/SMA200 (a8RP5ftOfGo, PLJda-dtBIc); O: 10-of-30 drop-arming, cycle not BULL + coin DOWN/RANGE at prior close; S: stop = 2 closes back (lmhqooBqJWU) | UTC daily bar, signal 00:00 UTC close, entry next open (O) | V2 = V1 + RSI14 Malkan BULL/BEAR (S 40/60, O 20-bar) | SMA200 (all distances; AT/AWAY in controls) | 1d | long | 9 | 4 | 0.749 | 0.741 | 0.745 | 75.0 | n/a | n/a | n/a | 0.087 | 1.000 | UNDERPOWERED (n VAL 4 < 100) |
| 4 S-TURN V0 | regime TURN (counter-trend entry into new trend) | S: 2 closes under SMA20 + all 10 closes < SMA200 (a8RP5ftOfGo, IjU9PpqvrI8); O: cycle BULL + coin UP/RANGE at prior close; S: stop = 2 closes back | UTC daily bar, signal 00:00 UTC close, entry next open (O) | V0 rule alone | SMA200 (all distances; AT/AWAY in controls) | 1d | short | 9 | 133 | -0.231 | -0.241 | -0.236 | 25.6 | -0.378 | -0.476 | -0.422 | 0.970 | 1.000 | UNDERPOWERED (DEV episodes 2 < 15) |
| 5 S-TURN V1 | regime TURN (counter-trend entry into new trend) | S: 2 closes under SMA20 + all 10 closes < SMA200 (a8RP5ftOfGo, IjU9PpqvrI8); O: cycle BULL + coin UP/RANGE at prior close; S: stop = 2 closes back | UTC daily bar, signal 00:00 UTC close, entry next open (O) | V1 = V0 + ADX14>=20 & DI sign (O) | SMA200 (all distances; AT/AWAY in controls) | 1d | short | 0 | 42 | -0.131 | -0.138 | -0.134 | 21.4 | -0.330 | -0.364 | -0.366 | 0.785 | 1.000 | UNDERPOWERED (n VAL 42 < 100) |
| 6 S-TURN V2 | regime TURN (counter-trend entry into new trend) | S: 2 closes under SMA20 + all 10 closes < SMA200 (a8RP5ftOfGo, IjU9PpqvrI8); O: cycle BULL + coin UP/RANGE at prior close; S: stop = 2 closes back | UTC daily bar, signal 00:00 UTC close, entry next open (O) | V2 = V1 + RSI14 Malkan BULL/BEAR (S 40/60, O 20-bar) | SMA200 (all distances; AT/AWAY in controls) | 1d | short | 0 | 22 | 0.053 | 0.045 | 0.049 | 31.8 | -0.294 | -0.343 | -0.406 | 0.511 | 0.847 | UNDERPOWERED (n VAL 22 < 100) |

Placebo (same coin, same phase/cycle pool, same side, matched count, same exit and fee): mean placebo net R at 12 bp per primary cell on VAL: cell 1: 0.081, cell 2: 0.151, cell 3: -0.010, cell 4: 0.033, cell 5: 0.066, cell 6: 0.063. "Beats placebo" and "profitable" are separate columns above (placebo p and net R).

## Claim test (NK: a 1-close flip is a trap; 2 closes are safer): day-cluster CI low, 2-close V0 vs 1-close V0

| cell | split | n 2-close | CI low 2-close | n 1-close | CI low 1-close | 2-close higher? |
|---|---|---|---|---|---|---|
| L-TURN | DEV | 56 | -0.080 | 61 | -0.084 | yes |
| L-TURN | VAL | 17 | -0.301 | 14 | -0.604 | yes |
| S-TURN | DEV | 9 | -1.009 | 14 | -0.942 | no |
| S-TURN | VAL | 133 | -0.476 | 168 | -0.420 | no |

## CONTROL table (descriptive; never pooled with primary, not in BH)

| cell | variant | level | tf | side | trigger | n DEV | n VAL | gross R VAL | net R 12bp DEV | net R 12bp VAL | net R 6bp VAL | win % VAL | day CI low VAL | stop1R net12 VAL | floor beat structural VAL | med SMA20-SMA200 (ATR) | med days since SMA200 cross | VAL episodes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7 L-TURN | V0 | all | 1d | long | 1-close | 61 | 14 | 0.171 | 0.412 | 0.160 | 0.166 | 35.7 | -0.604 | 0.228 | 0.00 | -0.43 | 0 | 11 |
| 8 S-TURN | V0 | all | 1d | short | 1-close | 14 | 168 | -0.196 | -0.284 | -0.208 | -0.202 | 25.6 | -0.420 | -0.157 | 0.01 | -3.64 | 92 | 17 |
| 9 continuation UP x BULL (draft original, no drop-arming) | V0 | all | 1d | long | 2-close | 98 | 134 | 0.418 | 1.529 | 0.409 | 0.413 | 39.6 | -0.018 | 0.417 | 0.00 | 0.83 | 10 | 21 |
| 10 continuation DOWN x BEAR (draft original short) | V0 | all | 1d | short | 2-close | 272 | 180 | -0.084 | 0.123 | -0.094 | -0.089 | 30.6 | -0.317 | -0.047 | 0.01 | -5.11 | 63 | 14 |
| 11 L-TURN cell, mismatched direction | V0 | all | 1d | short | 2-close | 290 | 143 | -0.286 | 0.060 | -0.301 | -0.294 | 20.3 | -0.484 | -0.253 | 0.00 | -7.40 | 136 | 13 |
| 12 S-TURN cell, mismatched direction | V0 | all | 1d | long | 2-close | 15 | 33 | 0.789 | 0.298 | 0.779 | 0.784 | 30.3 | -0.484 | 0.822 | 0.00 | -0.39 | 1 | 13 |
| 13 random same-cell placebo (matched cycle + phase) | n/a | all | 1d | long | none | 56 | 17 | n/a | 0.150 | 0.113 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| 14 random same-cell placebo | n/a | all | 1d | short | none | 9 | 133 | n/a | -0.057 | 0.030 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |
| 15 MARKDOWN (BRAINS spec), descriptive | V0 | all | 1d | short | 2-close | 152 | 89 | -0.273 | 0.075 | -0.286 | -0.280 | 25.8 | -0.494 | -0.265 | 0.01 | -6.64 | 103 | 8 |
| 16 L-TURN | V0 | AT | 1d | long | 2-close | 45 | 14 | 0.324 | 0.319 | 0.314 | 0.319 | 28.6 | -0.384 | 0.291 | 0.00 | -0.64 | 1 | 10 |
| 17 L-TURN | V0 | AWAY | 1d | long | 2-close | 15 | 3 | 0.211 | 0.476 | 0.204 | 0.207 | 33.3 | n/a | 0.204 | 0.00 | -0.84 | 1 | 2 |
| 18 S-TURN | V0 | AT | 1d | short | 2-close | 4 | 4 | 0.262 | -0.019 | 0.252 | 0.257 | 50.0 | n/a | 0.275 | 0.00 | -0.82 | 66 | 1 |
| 19 S-TURN | V0 | AWAY | 1d | short | 2-close | 5 | 131 | -0.234 | -0.391 | -0.244 | -0.239 | 25.2 | -0.475 | -0.187 | 0.01 | -3.57 | 92 | 18 |
| 20 L-TURN + funding veto | V0 | all | 1d | long | 2-close | 40 | 12 | 0.566 | 0.363 | 0.556 | 0.561 | 33.3 | -0.203 | 0.528 | 0.00 | -0.64 | 1 | 10 |
| 21 L-TURN + funding veto | V0 | all | 1d | long | 1-close | 50 | 12 | 0.134 | 0.371 | 0.123 | 0.129 | 33.3 | -0.643 | 0.202 | 0.00 | -0.43 | 0 | 10 |
| 22 S-TURN + funding veto | V0 | all | 1d | short | 2-close | 6 | 92 | -0.258 | -0.526 | -0.269 | -0.263 | 26.1 | -0.505 | -0.209 | 0.01 | -3.45 | 92 | 17 |
| 23 S-TURN + funding veto | V0 | all | 1d | short | 1-close | 9 | 116 | -0.235 | -0.707 | -0.248 | -0.241 | 24.1 | -0.499 | -0.178 | 0.01 | -3.50 | 91 | 15 |
| 24 L-TURN alts + BTC>SMA200 | V0 | all | 1d | long | 2-close | 37 | 11 | 0.668 | 0.125 | 0.658 | 0.663 | 45.5 | -0.188 | 0.627 | 0.00 | -0.84 | 1 | 5 |
| 25 unconditioned draft (no phase/cycle) | V0 | all | 1d | long | 2-close | 511 | 365 | 0.481 | 0.703 | 0.469 | 0.475 | 29.9 | 0.006 | 0.486 | 0.00 | 1.60 | 28 | 34 |
| 26 unconditioned draft (no phase/cycle) | V0 | all | 1d | short | 2-close | 504 | 449 | -0.084 | 0.092 | -0.096 | -0.090 | 33.0 | -0.237 | -0.056 | 0.01 | -4.23 | 73 | 16 |
| 27 1h SMA200 switch | V0 | all | 1h | long | 1h close > SMA200 | 13090 | 8654 | 0.150 | 0.213 | 0.076 | 0.113 | 12.2 | -0.056 | 0.076 | 0.04 | n/a | n/a | 1 |
| 28 weekly-close re-entry (>SMA200 and >SMA50) | V0 | all | 1w | long | 1 weekly close | 253 | 184 | 0.612 | 0.629 | 0.603 | 0.607 | 33.7 | -0.117 | 0.603 | 0.00 | 0.22 | 4 | 35 |

Cells 13/14: n = matched count of cells 1/4 on the split, net R = mean of 1000 placebo means (random entries in the same coin and same phase/cycle pool).

## DEV detail of the primary cells (selection-free: DEV is descriptive)

| cell | n DEV | episodes DEV | net R 12bp DEV | day CI low DEV | median SMA20-SMA200 gap (ATR) VAL | median days since SMA200 cross VAL | floor beat structural VAL | OI 5d change median VAL |
|---|---|---|---|---|---|---|---|---|
| 1 | 56 | 29 | 0.368 | -0.080 | -0.69 | 1 | 0.00 | 0.064 |
| 2 | 26 | 19 | 0.826 | 0.139 | -0.69 | 1 | 0.00 | 0.044 |
| 3 | 9 | 6 | 1.206 | -0.329 | -0.36 | 1 | 0.00 | 0.116 |
| 4 | 9 | 2 | -0.225 | -1.009 | -3.52 | 92 | 0.01 | 0.004 |
| 5 | 0 | 0 | n/a | n/a | -4.14 | 72 | 0.00 | -0.013 |
| 6 | 0 | 0 | n/a | n/a | -3.71 | 48 | 0.00 | -0.043 |

## Provenance (loader asserts the time key, strictly increasing timestamps, 15m alignment, min step 15m, gaps <= 12 h; gaps are exchange downtime and are kept as short days)

| coin | key | first 15m bar (UTC ms) | last 15m bar | 15m bars | gaps | daily bars | first day | last complete day | funding file | OI file |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | t | 1546300800000 | 1794600900000 | 275620 | 21 | 2873 | 2019-01-01 | 2026-11-12 | True | True |
| ETH | t | 1546300800000 | 1794600900000 | 275620 | 21 | 2873 | 2019-01-01 | 2026-11-12 | True | True |
| BNB | t | 1546300800000 | 1794600900000 | 275620 | 21 | 2873 | 2019-01-01 | 2026-11-12 | True | True |
| XRP | t | 1546300800000 | 1794600900000 | 275620 | 21 | 2873 | 2019-01-01 | 2026-11-12 | True | True |
| ADA | t | 1546300800000 | 1794600900000 | 275620 | 21 | 2873 | 2019-01-01 | 2026-11-12 | True | True |
| DOGE | ts | 1562328000000 | 1794601800000 | 257882 | 18 | 2688 | 2019-07-05 | 2026-11-12 | True | True |
| SOL | t | 1597125600000 | 1794600900000 | 219324 | 10 | 2285 | 2020-08-11 | 2026-11-12 | True | True |
| LTC | ts | 1546300800000 | 1794601800000 | 275622 | 21 | 2873 | 2019-01-01 | 2026-11-12 | True | True |
| LINK | ts | 1547632800000 | 1794601800000 | 274142 | 21 | 2858 | 2019-01-16 | 2026-11-12 | True | True |
| TRX | ts | 1546300800000 | 1794601800000 | 275622 | 21 | 2873 | 2019-01-01 | 2026-11-12 | True | True |
| DOT | ts | 1597791600000 | 1794601800000 | 218586 | 10 | 2278 | 2020-08-18 | 2026-11-12 | True | True |
| AVAX | ts | 1600756200000 | 1794601800000 | 215292 | 10 | 2243 | 2020-09-22 | 2026-11-12 | True | True |
| ATOM | ts | 1556510400000 | 1794601800000 | 264302 | 20 | 2755 | 2019-04-29 | 2026-11-12 | True | True |
| ETC | ts | 1546300800000 | 1794601800000 | 275622 | 21 | 2873 | 2019-01-01 | 2026-11-12 | True | True |
| BCH | ts | 1574935200000 | 1794601800000 | 243923 | 15 | 2542 | 2019-11-28 | 2026-11-12 | True | True |
| XLM | ts | 1546300800000 | 1794601800000 | 275622 | 21 | 2873 | 2019-01-01 | 2026-11-12 | True | True |
| UNI | ts | 1600311600000 | 1794601800000 | 215786 | 10 | 2248 | 2020-09-17 | 2026-11-12 | True | True |
| NEAR | ts | 1602651600000 | 1794601800000 | 213186 | 10 | 2221 | 2020-10-14 | 2026-11-12 | False | False |
| FIL | ts | 1602781200000 | 1794601800000 | 213042 | 10 | 2220 | 2020-10-15 | 2026-11-12 | False | False |
| ALGO | ts | 1561161600000 | 1794601800000 | 259178 | 18 | 2701 | 2019-06-22 | 2026-11-12 | False | False |

Daily close cross-check against `binance_spot_htf/<COIN>_1d.json` (other source, majors only): BTC: 2873 days, max |rel diff| 0.0000, share > 0.5%: 0.000; ETH: 2873 days, max |rel diff| 0.0000, share > 0.5%: 0.000; BNB: 2873 days, max |rel diff| 0.0000, share > 0.5%: 0.000; SOL: 2285 days, max |rel diff| 0.0000, share > 0.5%: 0.000.

## Deviations

- BUG fix before the first complete run (commit after 268ba967f): the first `study.py run` attempt crashed in the 1h control row (cell 27) with "resampled series not contiguous", because Binance spot downtime removed whole 1h buckets for some coins; no result of any cell had been written or read. Fix: the 1h resampler inserts flat bars at the previous close for wholly missing hours (daily resampling is unchanged and still asserts contiguity). Test `test_hourly_resample_fills_missing_hours_flat` added. No parameter, cell or rule changed.
- Design item changes are listed in PRE_REG.md under "Design items not implemented / readings changed before any run" (coin trend phase labeller written fresh; no fresh 10-coin holdout; funding veto lacks NEAR/FIL/ALGO; no 15m/4h rows).

## Parameter labels

See PRE_REG.md section Parameters (SOURCED = video id + time; OURS = one value, no grid). No parameter here is NK's unless marked SOURCED.

## Reading (hand-written after the single run; numbers are those in the tables above, nothing re-run or tuned)
- All 6 primary cells are UNDERPOWERED, so no cell passes and none fails on the gates. Long (L-TURN) VAL n = 17 / 9 / 4 and 10 / 5 / 1 episodes; short (S-TURN) V0 has n VAL 133 and 18 VAL episodes but only 9 DEV trades (2 DEV episodes), so the DEV episode gate (15) closes it; V1 and V2 short have 0 DEV trades. The frozen triggers are stricter than the controls, as the design predicted (open doubt 1: DEV L-TURN total 56 trades, below the 60 note threshold; reported, not loosened).
- Short S-TURN V0 on VAL is the only primary cell with a large n and it is negative: net R 12 bp -0.241 (n 133), day-cluster CI low -0.476, placebo p 0.970. The long cells show positive means on tiny n (cell 1: +0.295, trade CI low -0.283, day CI low -0.301, placebo p 0.233); positive and not distinguishable from random entries in the same phase/cycle cell (placebo mean +0.081).
- Claim test (2 closes vs 1 close): L-TURN the 2-close CI low is higher on DEV (-0.080 vs -0.084, a tie in practice) and on VAL (-0.301 vs -0.604, tiny n); S-TURN the 1-close version is higher on both splits (DEV -1.009 vs -0.942, VAL -0.476 vs -0.420). No support for "2 closes are safer" in the short cell, which is the only side with n.
- Controls (descriptive, not pooled): the unconditioned draft long (cell 25) and the weekly re-entry (cell 28) are net positive on VAL (+0.469, +0.603) with day-cluster CI lows around 0 (0.006, -0.117); continuation UP x BULL (cell 9) +0.409 with CI low -0.018. The phase/cycle turn conditioning did not help the long side versus those. Short controls (10, 11, 15, 19, 26) are all net negative on VAL. 1h SMA200 switch (cell 27): net +0.076 at 12 bp, win 12.2%, n 8654 (one VAL episode label: its entries are not episode-gated). AT vs AWAY: L-TURN AT n VAL 14 (+0.314), AWAY n 3; S-TURN AT n VAL 4, AWAY 131 (-0.244): no usable at-level evidence either way.
- Funding veto: cells 20 and 21 (n 12 each) versus 1 and 7 do not change the 2-close vs 1-close ordering in any decidable way (n too small); per the design the veto is dropped from further work. NEAR, FIL, ALGO have no funding file and are absent from cells 20-23.
- Fresh 10-coin holdout and forward days were not run (no cached OHLCV, not fetched). The daily cross-check against `binance_spot_htf` shows zero difference because that file is derived from the same 15m cache, so it is a consistency check, not an independent source.
- What would be needed for a decidable L-TURN: far more independent turn episodes (VAL has one bull-to-bear transition worth of cycle turns); more symbols or a longer history would add episodes only if they add distinct cycle turn dates, since the cycle gate is shared.
