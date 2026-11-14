# RESULT: shorts at stacked seller layers, DOWN phase only (edge9-downtrend-seller-layers-1114)

**Verdict: FAIL on all 27 row x exit hypotheses. No row has a positive VALIDATION mean R fee-net; 0 pass BH. Gross R is about zero (ALL: -0.02 / +0.01 / +0.02 for 1R / 2R / prior-day-low), so the 12 bp round trip alone sets the result (~ -0.4R at these stop sizes). Stacking layers (k=1, 2, 3+) does not help: K3+ gross +0.08R at 2R is not distinguishable from zero and net is -0.33R.** Pre-registration: PRE_REG.md (commits ca574ca3a, amendment f4c302c1e), unchanged after outcomes.

Regime mix: BTC UTC days (close vs 200-day SMA, 5% band): DEV bull 597 / bear 466 / range 114 (n/a 199 warm-up); VALIDATION bull 586 / bear 309 / range 152. BTC DOWN days (phase gate): DEV 466 of 1350, VALIDATION 395 of 1048. Share of all-days signals (E2) that fall on DOWN days: DEV 40%, VALIDATION 42%.

Data: Bybit v5 public linear 15m klines, 10 USDT perps, history from 2020-03 (BTC) / 2020-10 (LINK, LTC) / 2021 (others) to 2026-11-13 20:15 UTC; closed bars only. L6 (taker selling) dropped: Bybit klines have no taker split (see PRE_REG). One open trade per coin; DEV to 2023-12-31, VALIDATION from 2024-01-01. Trades column is DEV/VAL. Placebo = matched random shorts (coin, hour, holding time) on VALIDATION DOWN days; placebo mean R is about -0.38 to -0.44 in every row, i.e. the same cost-dominated level. Overlap: single-layer rows overlap each other and K rows (one signal can sit in several rows); BH family = 27 hypotheses on the day-cluster one-sided p; no row reached the BH gate because none has a positive mean.

## DOWN-phase rows (verdict table)
| row exit | trades DEV/VAL | win rate VAL | mean R VAL | CI per-trade | CI day-cluster | placebo p | w/o best 5 days | mean R DEV | verdict |
|---|---|---|---|---|---|---|---|---|---|
| ALL E1 | 12644/14648 | 48.4% | -0.404 | [-0.421, -0.387] | [-0.425, -0.383] | 0.866 | -0.409 | -0.416 | FAIL |
| K1 E1 | 9371/11070 | 48.0% | -0.408 | [-0.427, -0.389] | [-0.430, -0.386] | 0.921 | -0.414 | -0.417 | FAIL |
| K2 E1 | 2877/3103 | 49.6% | -0.387 | [-0.424, -0.350] | [-0.423, -0.350] | 0.436 | -0.399 | -0.409 | FAIL |
| K3+ E1 | 396/475 | 48.6% | -0.426 | [-0.515, -0.331] | [-0.516, -0.333] | 0.500 | -0.468 | -0.467 | FAIL |
| L1 VAH E1 | 3944/4646 | 49.0% | -0.410 | [-0.438, -0.380] | [-0.443, -0.377] | 0.540 | -0.420 | -0.454 | FAIL |
| L2 POC E1 | 4401/5064 | 47.5% | -0.427 | [-0.456, -0.399] | [-0.459, -0.397] | 0.894 | -0.436 | -0.422 | FAIL |
| L3 PDH E1 | 2788/3211 | 49.1% | -0.378 | [-0.412, -0.342] | [-0.418, -0.336] | 0.511 | -0.390 | -0.398 | FAIL |
| L4 LVN E1 | 3081/3511 | 48.8% | -0.396 | [-0.429, -0.362] | [-0.431, -0.360] | 0.621 | -0.406 | -0.424 | FAIL |
| L5 RSI>=60 E1 | 2117/2287 | 48.7% | -0.381 | [-0.423, -0.338] | [-0.422, -0.338] | 0.621 | -0.393 | -0.357 | FAIL |
| ALL E2 | 11083/12610 | 33.7% | -0.367 | [-0.392, -0.343] | [-0.400, -0.334] | 0.263 | -0.377 | -0.373 | FAIL |
| K1 E2 | 8214/9534 | 33.3% | -0.376 | [-0.404, -0.347] | [-0.411, -0.339] | 0.445 | -0.387 | -0.374 | FAIL |
| K2 E2 | 2511/2669 | 34.9% | -0.340 | [-0.394, -0.286] | [-0.399, -0.277] | 0.210 | -0.365 | -0.384 | FAIL |
| K3+ E2 | 358/407 | 36.4% | -0.334 | [-0.467, -0.194] | [-0.459, -0.199] | 0.281 | -0.392 | -0.284 | FAIL |
| L1 VAH E2 | 3356/3896 | 33.8% | -0.385 | [-0.429, -0.341] | [-0.436, -0.333] | 0.331 | -0.402 | -0.416 | FAIL |
| L2 POC E2 | 3844/4334 | 33.4% | -0.379 | [-0.421, -0.337] | [-0.430, -0.329] | 0.435 | -0.399 | -0.400 | FAIL |
| L3 PDH E2 | 2526/2842 | 34.5% | -0.338 | [-0.390, -0.285] | [-0.400, -0.275] | 0.263 | -0.360 | -0.322 | FAIL |
| L4 LVN E2 | 2688/2991 | 34.4% | -0.351 | [-0.402, -0.299] | [-0.405, -0.295] | 0.259 | -0.373 | -0.360 | FAIL |
| L5 RSI>=60 E2 | 1911/2045 | 34.7% | -0.326 | [-0.388, -0.263] | [-0.394, -0.258] | 0.256 | -0.351 | -0.307 | FAIL |
| ALL E3 | 8949/9978 | 19.0% | -0.349 | [-0.403, -0.294] | [-0.430, -0.268] | 0.143 | -0.378 | -0.280 | FAIL |
| K1 E3 | 6370/7237 | 19.0% | -0.365 | [-0.426, -0.301] | [-0.453, -0.275] | 0.294 | -0.401 | -0.295 | FAIL |
| K2 E3 | 2260/2363 | 19.0% | -0.297 | [-0.407, -0.186] | [-0.438, -0.149] | 0.133 | -0.373 | -0.246 | FAIL |
| K3+ E3 | 319/378 | 19.8% | -0.379 | [-0.621, -0.116] | [-0.636, -0.086] | 0.427 | -0.573 | -0.234 | FAIL |
| L1 VAH E3 | 2761/3139 | 17.1% | -0.371 | [-0.467, -0.270] | [-0.488, -0.241] | 0.287 | -0.427 | -0.366 | FAIL |
| L2 POC E3 | 3001/3360 | 21.6% | -0.362 | [-0.443, -0.279] | [-0.462, -0.258] | 0.320 | -0.410 | -0.268 | FAIL |
| L3 PDH E3 | 2325/2553 | 17.5% | -0.347 | [-0.454, -0.238] | [-0.485, -0.202] | 0.309 | -0.416 | -0.218 | FAIL |
| L4 LVN E3 | 1975/2136 | 20.6% | -0.303 | [-0.417, -0.188] | [-0.437, -0.162] | 0.168 | -0.370 | -0.315 | FAIL |
| L5 RSI>=60 E3 | 1797/1924 | 18.1% | -0.295 | [-0.412, -0.171] | [-0.453, -0.122] | 0.222 | -0.387 | -0.153 | FAIL |

## Control: same signals on ALL days (descriptive)
| row exit | trades DEV/VAL | win rate VAL | mean R VAL | CI per-trade | CI day-cluster | placebo p | w/o best 5 days | mean R DEV | verdict |
|---|---|---|---|---|---|---|---|---|---|
| ALL E1 | 31563/34754 | 48.7% | -0.401 | [-0.411, -0.390] | [-0.415, -0.386] | - | -0.403 | -0.392 | control |
| K1 E1 | 22819/25109 | 48.5% | -0.404 | [-0.416, -0.391] | [-0.419, -0.388] | - | -0.407 | -0.398 | control |
| K2 E1 | 7810/8349 | 49.6% | -0.380 | [-0.403, -0.358] | [-0.405, -0.355] | - | -0.385 | -0.363 | control |
| K3+ E1 | 934/1296 | 47.8% | -0.480 | [-0.534, -0.425] | [-0.538, -0.417] | - | -0.500 | -0.476 | control |
| ALL E2 | 27732/30079 | 34.3% | -0.352 | [-0.367, -0.336] | [-0.375, -0.328] | - | -0.357 | -0.338 | control |
| K1 E2 | 20042/21718 | 34.1% | -0.357 | [-0.376, -0.338] | [-0.382, -0.331] | - | -0.362 | -0.346 | control |
| K2 E2 | 6869/7238 | 35.0% | -0.327 | [-0.360, -0.294] | [-0.367, -0.286] | - | -0.337 | -0.315 | control |
| K3+ E2 | 821/1123 | 34.2% | -0.421 | [-0.503, -0.338] | [-0.504, -0.336] | - | -0.449 | -0.351 | control |
| ALL E3 | 22217/23485 | 19.2% | -0.328 | [-0.362, -0.293] | [-0.384, -0.270] | - | -0.347 | -0.284 | control |
| K1 E3 | 15305/16068 | 19.5% | -0.329 | [-0.371, -0.286] | [-0.391, -0.266] | - | -0.350 | -0.303 | control |
| K2 E3 | 6166/6378 | 18.7% | -0.318 | [-0.386, -0.251] | [-0.407, -0.224] | - | -0.359 | -0.234 | control |
| K3+ E3 | 746/1039 | 18.5% | -0.374 | [-0.536, -0.208] | [-0.553, -0.179] | - | -0.483 | -0.303 | control |

## BTC seller layers (descriptive research, not a trade instruction)
Last 15m bar in the data: 2026-11-13 20:00 UTC, close 69,000.3 (BTC DOWN phase flag = True; daily close 71,435 on 11-12 vs SMA20 77,301, SMA20 falling from 79,410 five days earlier). 1h RSI(14) of the last closed hour: 38.0 (L5 not active).

| layer | 11-13 levels (prior day 11-12 complete) | vs last 69,000 | provisional 11-14 levels (11-13 so far, 81 of 96 bars; will move when the day closes) | vs last 69,000 |
|---|---|---|---|---|
| L1 prior-day VAH | 74,116 | +7.4% | 71,364 | +3.4% |
| L2 prior-day POC | 72,535 | +5.1% | 69,340 | +0.5% |
| L3 prior-day high | 74,194 | +7.5% | 71,499 | +3.6% |
| L4 3-day low-volume node | 74,133 | +7.4% | 69,789 | +1.1% |
| prior-day low (E3 target) | 71,073 | n/a | 67,468 | -2.2% |
| prior-day VAL (reference) | n/a | n/a | 68,734 | -0.4% |

Reading: price is already below the 11-13 layers (it fell ~3.4% from 71.4k). For 11-14 the nearest overhead sellers are POC 69,340 (+0.5%) and the 3-day LVN 69,789 (+1.1%), within 0.7% of each other, VAH and prior-day high 71.4k to 71.5k (0.2% apart). Given the study result these are context, not an edge.

## Files
study.py (levels, signals, exits, bootstrap, placebo, BH), fetch_bybit.py, report.py, test_study.py (4 tests; with `E9_LAG=0`, the deliberately wrong version using today's bars for today's levels, 2 tests fail: test_levels_do_not_use_today and test_prior_day_high_is_yesterdays), results.json. Raw klines are not in git.
