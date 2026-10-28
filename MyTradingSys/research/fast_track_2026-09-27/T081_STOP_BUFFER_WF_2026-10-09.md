# T081 - stop_buffer_atr walk-forward (Tom core), 2026-10-09

Rows: F:\MTS\data\tom_bt_2026-10-07 (signals at or after 2026-06-26 excluded: HOLDOUT burned for Tom, B147). Bars: F:\MTS\data\tom_raw\klines.
Stop under test: `stop_k = structure_stop -/+ k x ATR(14)` (long lower, short higher). Entry, target, fill window, hold, fees and `sim_limit_trade()` are those of tom_bt.py; only the stop moves (so R grows and fee R shrinks). ATR = plain SMA of True Range over the last 14 closed bars before the signal (FORMULAS.md s12). Bases: **zone_tf** (primary; the row's zone timeframe 5m/15m/1h) and **1m** (sensitivity).
Signal variants are SENSITIVITY as in B146 (watch_episode = WATCH or SETUP_FORMING, p4_episode = proof>=4); the live rule has 0 signals.
Fees: DERIBIT = maker entry/target 0, taker stop/timeout 5 bp; ALL_TAKER = 5 bp every leg (fees.py).

## Pre-registration (frozen before the run)

- k grid (0.0, 0.25, 0.5, 1.0, 1.5, 2.0): **NO-SOURCE** (tuning grid fixed by task T081; no trader quote). Every k that is picked below is **BT-TUNED**, not a parameter.
- ATR window 14 and plain-SMA form: FORMULAS.md s12 (operator decision 2026-09-28) / Java averageTrueRange callers. Taking ATR on the zone timeframe is an assumption of this study (the row carries the zone type, not the Java ATR timeframe).
- Trials: 2 variants x 2 ATR bases x 6 k x 2 fee profiles = 48 cells, each printed for dev and for hist; 8 walk-forward runs (variant x basis x fee). None dropped.
- Walk-forward: **expanding** window over UTC calendar-month blocks of DEV (2025-09-01..2026-06-25): 10 blocks, first test block = block 5 (train = first 4 months), so 6 folds; embargo 86400 s before each test block (**NO-SOURCE**, > 16 h max trade life); MIN_TRAIN_BLOCKS=4 is **NO-SOURCE** (engineering choice). Choice rule: highest mean net R with n >= 30 in the training set, ties -> smaller k; if no k has n >= 30 the fold abstains (no trade, counted as such).
- Pass rule for the verdict: out-of-fold mean net R > 0 AND bootstrap 95% CI lower bound > 0 (T.boot_ci, 2000 resamples, seed fixed).
- hist (2022-01..2025-08) rows are printed for context only; they play no part in selection.
- A trade opened by the last dev signal can exit up to 16 h after 2026-06-26 00:00; those exit bars are read (unavoidable, same as tom_stop_width.py), but no holdout signal is generated or selected on.

## watch_episode / ATR basis zone_tf / DERIBIT

Signals with ATR: 3030 of 3030 (dropped for missing ATR: 0).

### period dev (pooled; IN-SAMPLE for the k grid, not an out-of-sample number)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (dev) | 555 | 520 | 5.6% | 0.7% | 1.3% | 19.8% | -0.294 | -4.947 [-11.231, -1.643] | -1.521 | +4.654 |
| k=0.25 (dev) | 538 | 504 | 5.6% | 0.7% | 3.4% | 30.6% | -0.125 | -0.630 [-0.786, -0.472] | -1.263 | +0.505 |
| k=0.5 (dev) | 527 | 493 | 5.7% | 0.8% | 4.1% | 38.5% | -0.117 | -0.458 [-0.581, -0.335] | -1.150 | +0.341 |
| k=1 (dev) | 515 | 481 | 5.8% | 0.8% | 5.0% | 51.8% | -0.092 | -0.305 [-0.397, -0.211] | -0.429 | +0.213 |
| k=1.5 (dev) | 508 | 474 | 5.9% | 0.8% | 5.7% | 61.0% | -0.092 | -0.249 [-0.330, -0.176] | -0.202 | +0.157 |
| k=2 (dev) | 505 | 471 | 5.9% | 0.8% | 5.5% | 69.2% | -0.086 | -0.210 [-0.275, -0.145] | -0.130 | +0.125 |

### period hist (context only)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (hist) | 2298 | 2179 | 4.0% | 1.2% | 2.9% | 17.3% | -0.135 | -2.430 [-3.423, -1.744] | -1.512 | +2.295 |
| k=0.25 (hist) | 2242 | 2127 | 4.0% | 1.2% | 4.6% | 26.6% | -0.154 | -0.592 [-0.668, -0.511] | -1.261 | +0.438 |
| k=0.5 (hist) | 2207 | 2092 | 4.0% | 1.2% | 5.5% | 33.9% | -0.135 | -0.428 [-0.494, -0.367] | -1.143 | +0.294 |
| k=1 (hist) | 2159 | 2045 | 4.1% | 1.2% | 6.4% | 49.9% | -0.097 | -0.282 [-0.330, -0.237] | -0.505 | +0.185 |
| k=1.5 (hist) | 2144 | 2031 | 4.1% | 1.2% | 6.6% | 61.4% | -0.082 | -0.219 [-0.255, -0.181] | -0.239 | +0.137 |
| k=2 (hist) | 2133 | 2023 | 4.1% | 1.1% | 6.9% | 70.4% | -0.061 | -0.170 [-0.201, -0.138] | -0.139 | +0.109 |

### Walk-forward (expanding, dev only)

| fold | test block | k chosen (BT-TUNED) | train n / mean net at chosen k | train table n/mean net per k | OOS n | OOS mean net | k=0 n | k=0 mean net |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-01-01..2026-01-31 | 2 | 176 / -0.227 | 0:190/-2.09; 0.25:185/-0.67; 0.5:184/-0.47; 1:178/-0.36; 1.5:176/-0.27; 2:176/-0.23 | 60 | -0.217 | 70 | -24.835 |
| 2 | 2026-02-01..2026-02-28 | 2 | 233 / -0.221 | 0:257/-8.23; 0.25:248/-0.67; 0.5:246/-0.48; 1:238/-0.33; 1.5:234/-0.27; 2:233/-0.22 | 39 | -0.140 | 43 | -2.258 |
| 3 | 2026-03-01..2026-03-31 | 2 | 273 / -0.214 | 0:301/-7.41; 0.25:290/-0.66; 0.5:288/-0.47; 1:280/-0.31; 1.5:275/-0.26; 2:273/-0.21 | 51 | -0.229 | 57 | -1.676 |
| 4 | 2026-04-01..2026-04-30 | 2 | 326 / -0.215 | 0:360/-6.46; 0.25:348/-0.61; 0.5:342/-0.42; 1:333/-0.30; 1.5:328/-0.25; 2:326/-0.22 | 55 | -0.135 | 58 | -1.716 |
| 5 | 2026-05-01..2026-05-31 | 2 | 381 / -0.204 | 0:418/-5.81; 0.25:405/-0.63; 0.5:397/-0.44; 1:388/-0.30; 1.5:383/-0.24; 2:381/-0.20 | 56 | -0.193 | 67 | -1.754 |
| 6 | 2026-06-01..2026-06-25 | 2 | 434 / -0.200 | 0:482/-5.23; 0.25:467/-0.63; 0.5:456/-0.45; 1:444/-0.30; 1.5:437/-0.24; 2:434/-0.20 | 34 | -0.314 | 35 | -0.806 |

- **OUT-OF-FOLD (chosen k)**: n=295 mean net R -0.200, 95% CI [-0.277, -0.120], median -0.129
- **same test blocks at k=0**: n=330 mean net R -6.595, 95% CI [-16.440, -1.471], median -1.511

## watch_episode / ATR basis zone_tf / ALL_TAKER

Signals with ATR: 3030 of 3030 (dropped for missing ATR: 0).

### period dev (pooled; IN-SAMPLE for the k grid, not an out-of-sample number)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (dev) | 555 | 520 | 5.6% | 0.7% | 1.3% | 19.8% | -0.294 | -9.618 [-22.179, -3.068] | -2.049 | +9.325 |
| k=0.25 (dev) | 538 | 504 | 5.6% | 0.7% | 3.4% | 30.6% | -0.125 | -1.165 [-1.340, -0.999] | -1.525 | +1.040 |
| k=0.5 (dev) | 527 | 493 | 5.7% | 0.8% | 4.1% | 38.5% | -0.117 | -0.821 [-0.952, -0.691] | -1.302 | +0.704 |
| k=1 (dev) | 515 | 481 | 5.8% | 0.8% | 5.0% | 51.8% | -0.092 | -0.534 [-0.630, -0.440] | -0.614 | +0.442 |
| k=1.5 (dev) | 508 | 474 | 5.9% | 0.8% | 5.7% | 61.0% | -0.092 | -0.419 [-0.501, -0.344] | -0.348 | +0.326 |
| k=2 (dev) | 505 | 471 | 5.9% | 0.8% | 5.5% | 69.2% | -0.086 | -0.344 [-0.411, -0.276] | -0.259 | +0.259 |

### period hist (context only)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (hist) | 2298 | 2179 | 4.0% | 1.2% | 2.9% | 17.3% | -0.135 | -4.759 [-6.676, -3.452] | -2.024 | +4.625 |
| k=0.25 (hist) | 2242 | 2127 | 4.0% | 1.2% | 4.6% | 26.6% | -0.154 | -1.063 [-1.142, -0.980] | -1.528 | +0.909 |
| k=0.5 (hist) | 2207 | 2092 | 4.0% | 1.2% | 5.5% | 33.9% | -0.135 | -0.751 [-0.817, -0.688] | -1.291 | +0.617 |
| k=1 (hist) | 2159 | 2045 | 4.1% | 1.2% | 6.4% | 49.9% | -0.097 | -0.488 [-0.538, -0.444] | -0.693 | +0.390 |
| k=1.5 (hist) | 2144 | 2031 | 4.1% | 1.2% | 6.6% | 61.4% | -0.082 | -0.371 [-0.408, -0.333] | -0.373 | +0.289 |
| k=2 (hist) | 2133 | 2023 | 4.1% | 1.1% | 6.9% | 70.4% | -0.061 | -0.291 [-0.325, -0.259] | -0.235 | +0.230 |

### Walk-forward (expanding, dev only)

| fold | test block | k chosen (BT-TUNED) | train n / mean net at chosen k | train table n/mean net per k | OOS n | OOS mean net | k=0 n | k=0 mean net |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-01-01..2026-01-31 | 2 | 176 / -0.369 | 0:190/-3.77; 0.25:185/-1.24; 0.5:184/-0.85; 1:178/-0.60; 1.5:176/-0.45; 2:176/-0.37 | 60 | -0.389 | 70 | -49.435 |
| 2 | 2026-02-01..2026-02-28 | 2 | 233 / -0.370 | 0:257/-16.11; 0.25:248/-1.26; 0.5:246/-0.88; 1:238/-0.59; 1.5:234/-0.46; 2:233/-0.37 | 39 | -0.226 | 43 | -4.217 |
| 3 | 2026-03-01..2026-03-31 | 2 | 273 / -0.355 | 0:301/-14.46; 0.25:290/-1.23; 0.5:288/-0.85; 1:280/-0.55; 1.5:275/-0.44; 2:273/-0.36 | 51 | -0.333 | 57 | -3.027 |
| 4 | 2026-04-01..2026-04-30 | 2 | 326 / -0.350 | 0:360/-12.59; 0.25:348/-1.15; 0.5:342/-0.79; 1:333/-0.53; 1.5:328/-0.42; 2:326/-0.35 | 55 | -0.251 | 58 | -3.016 |
| 5 | 2026-05-01..2026-05-31 | 2 | 381 / -0.336 | 0:418/-11.26; 0.25:405/-1.16; 0.5:397/-0.80; 1:388/-0.52; 1.5:383/-0.41; 2:381/-0.34 | 56 | -0.352 | 67 | -3.463 |
| 6 | 2026-06-01..2026-06-25 | 2 | 434 / -0.335 | 0:482/-10.16; 0.25:467/-1.17; 0.5:456/-0.82; 1:444/-0.53; 1.5:437/-0.41; 2:434/-0.34 | 34 | -0.429 | 35 | -1.830 |

- **OUT-OF-FOLD (chosen k)**: n=295 mean net R -0.330, 95% CI [-0.406, -0.248], median -0.244
- **same test blocks at k=0**: n=330 mean net R -12.986, 95% CI [-32.607, -2.853], median -2.021

## watch_episode / ATR basis 1m / DERIBIT

Signals with ATR: 3030 of 3030 (dropped for missing ATR: 0).

### period dev (pooled; IN-SAMPLE for the k grid, not an out-of-sample number)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (dev) | 555 | 520 | 5.6% | 0.7% | 1.3% | 19.8% | -0.294 | -4.947 [-11.231, -1.643] | -1.521 | +4.654 |
| k=0.25 (dev) | 553 | 518 | 5.6% | 0.7% | 1.7% | 21.8% | -0.278 | -1.253 [-1.479, -1.037] | -1.454 | +0.976 |
| k=0.5 (dev) | 549 | 515 | 5.5% | 0.7% | 2.3% | 25.2% | -0.192 | -0.930 [-1.116, -0.742] | -1.372 | +0.738 |
| k=1 (dev) | 540 | 506 | 5.6% | 0.7% | 2.8% | 31.6% | -0.097 | -0.633 [-0.800, -0.452] | -1.268 | +0.536 |
| k=1.5 (dev) | 538 | 504 | 5.6% | 0.7% | 3.4% | 34.7% | -0.123 | -0.552 [-0.695, -0.401] | -1.203 | +0.428 |
| k=2 (dev) | 536 | 502 | 5.6% | 0.7% | 3.6% | 38.0% | -0.146 | -0.507 [-0.635, -0.385] | -1.154 | +0.361 |

### period hist (context only)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (hist) | 2298 | 2179 | 4.0% | 1.2% | 2.9% | 17.3% | -0.135 | -2.430 [-3.423, -1.744] | -1.512 | +2.295 |
| k=0.25 (hist) | 2287 | 2168 | 4.0% | 1.2% | 3.2% | 19.5% | -0.161 | -0.965 [-1.095, -0.831] | -1.420 | +0.805 |
| k=0.5 (hist) | 2273 | 2155 | 4.0% | 1.2% | 3.7% | 22.4% | -0.110 | -0.727 [-0.828, -0.614] | -1.345 | +0.617 |
| k=1 (hist) | 2251 | 2136 | 4.0% | 1.2% | 4.4% | 26.9% | -0.134 | -0.580 [-0.664, -0.494] | -1.250 | +0.446 |
| k=1.5 (hist) | 2235 | 2120 | 4.0% | 1.2% | 5.0% | 31.5% | -0.115 | -0.472 [-0.542, -0.395] | -1.184 | +0.357 |
| k=2 (hist) | 2224 | 2109 | 4.0% | 1.2% | 5.4% | 35.0% | -0.104 | -0.405 [-0.471, -0.335] | -1.139 | +0.301 |

### Walk-forward (expanding, dev only)

| fold | test block | k chosen (BT-TUNED) | train n / mean net at chosen k | train table n/mean net per k | OOS n | OOS mean net | k=0 n | k=0 mean net |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-01-01..2026-01-31 | 1.5 | 184 / -0.483 | 0:190/-2.09; 0.25:190/-1.42; 0.5:188/-1.02; 1:185/-0.63; 1.5:184/-0.48; 2:184/-0.49 | 67 | -0.737 | 70 | -24.835 |
| 2 | 2026-02-01..2026-02-28 | 2 | 248 / -0.510 | 0:257/-8.23; 0.25:257/-1.49; 0.5:254/-1.02; 1:250/-0.67; 1.5:248/-0.55; 2:248/-0.51 | 41 | -0.375 | 43 | -2.258 |
| 3 | 2026-03-01..2026-03-31 | 2 | 290 / -0.493 | 0:301/-7.41; 0.25:301/-1.43; 0.5:298/-1.00; 1:293/-0.66; 1.5:291/-0.54; 2:290/-0.49 | 55 | -0.439 | 57 | -1.676 |
| 4 | 2026-04-01..2026-04-30 | 2 | 347 / -0.485 | 0:360/-6.46; 0.25:360/-1.37; 0.5:357/-0.98; 1:351/-0.63; 1.5:349/-0.54; 2:347/-0.49 | 56 | -0.478 | 58 | -1.716 |
| 5 | 2026-05-01..2026-05-31 | 2 | 403 / -0.484 | 0:418/-5.81; 0.25:417/-1.32; 0.5:414/-0.95; 1:407/-0.62; 1.5:405/-0.54; 2:403/-0.48 | 65 | -0.626 | 67 | -1.754 |
| 6 | 2026-06-01..2026-06-25 | 2 | 465 / -0.499 | 0:482/-5.23; 0.25:481/-1.27; 0.5:478/-0.93; 1:469/-0.62; 1.5:467/-0.55; 2:465/-0.50 | 34 | -0.552 | 35 | -0.806 |

- **OUT-OF-FOLD (chosen k)**: n=318 mean net R -0.551, 95% CI [-0.704, -0.385], median -1.192
- **same test blocks at k=0**: n=330 mean net R -6.595, 95% CI [-16.440, -1.471], median -1.511

## watch_episode / ATR basis 1m / ALL_TAKER

Signals with ATR: 3030 of 3030 (dropped for missing ATR: 0).

### period dev (pooled; IN-SAMPLE for the k grid, not an out-of-sample number)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (dev) | 555 | 520 | 5.6% | 0.7% | 1.3% | 19.8% | -0.294 | -9.618 [-22.179, -3.068] | -2.049 | +9.325 |
| k=0.25 (dev) | 553 | 518 | 5.6% | 0.7% | 1.7% | 21.8% | -0.278 | -2.246 [-2.615, -1.919] | -1.908 | +1.969 |
| k=0.5 (dev) | 549 | 515 | 5.5% | 0.7% | 2.3% | 25.2% | -0.192 | -1.695 [-1.950, -1.460] | -1.753 | +1.503 |
| k=1 (dev) | 540 | 506 | 5.6% | 0.7% | 2.8% | 31.6% | -0.097 | -1.191 [-1.384, -0.997] | -1.543 | +1.094 |
| k=1.5 (dev) | 538 | 504 | 5.6% | 0.7% | 3.4% | 34.7% | -0.123 | -1.004 [-1.163, -0.843] | -1.411 | +0.880 |
| k=2 (dev) | 536 | 502 | 5.6% | 0.7% | 3.6% | 38.0% | -0.146 | -0.890 [-1.029, -0.760] | -1.311 | +0.744 |

### period hist (context only)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (hist) | 2298 | 2179 | 4.0% | 1.2% | 2.9% | 17.3% | -0.135 | -4.759 [-6.676, -3.452] | -2.024 | +4.625 |
| k=0.25 (hist) | 2287 | 2168 | 4.0% | 1.2% | 3.2% | 19.5% | -0.161 | -1.811 [-1.960, -1.661] | -1.849 | +1.650 |
| k=0.5 (hist) | 2273 | 2155 | 4.0% | 1.2% | 3.7% | 22.4% | -0.110 | -1.383 [-1.495, -1.262] | -1.698 | +1.273 |
| k=1 (hist) | 2251 | 2136 | 4.0% | 1.2% | 4.4% | 26.9% | -0.134 | -1.061 [-1.148, -0.974] | -1.505 | +0.927 |
| k=1.5 (hist) | 2235 | 2120 | 4.0% | 1.2% | 5.0% | 31.5% | -0.115 | -0.862 [-0.934, -0.784] | -1.379 | +0.747 |
| k=2 (hist) | 2224 | 2109 | 4.0% | 1.2% | 5.4% | 35.0% | -0.104 | -0.736 [-0.806, -0.666] | -1.287 | +0.632 |

### Walk-forward (expanding, dev only)

| fold | test block | k chosen (BT-TUNED) | train n / mean net at chosen k | train table n/mean net per k | OOS n | OOS mean net | k=0 n | k=0 mean net |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-01-01..2026-01-31 | 2 | 184 / -0.902 | 0:190/-3.77; 0.25:190/-2.41; 0.5:188/-1.82; 1:185/-1.22; 1.5:184/-0.97; 2:184/-0.90 | 67 | -1.066 | 70 | -49.435 |
| 2 | 2026-02-01..2026-02-28 | 2 | 248 / -0.943 | 0:257/-16.11; 0.25:257/-2.61; 0.5:254/-1.88; 1:250/-1.30; 1.5:248/-1.06; 2:248/-0.94 | 41 | -0.640 | 43 | -4.217 |
| 3 | 2026-03-01..2026-03-31 | 2 | 290 / -0.902 | 0:301/-14.46; 0.25:301/-2.50; 0.5:298/-1.82; 1:293/-1.26; 1.5:291/-1.02; 2:290/-0.90 | 55 | -0.741 | 57 | -3.027 |
| 4 | 2026-04-01..2026-04-30 | 2 | 347 / -0.877 | 0:360/-12.59; 0.25:360/-2.40; 0.5:357/-1.76; 1:351/-1.20; 1.5:349/-1.00; 2:347/-0.88 | 56 | -0.784 | 58 | -3.016 |
| 5 | 2026-05-01..2026-05-31 | 2 | 403 / -0.864 | 0:418/-11.26; 0.25:417/-2.31; 0.5:414/-1.71; 1:407/-1.17; 1.5:405/-0.99; 2:403/-0.86 | 65 | -1.071 | 67 | -3.463 |
| 6 | 2026-06-01..2026-06-25 | 2 | 465 / -0.883 | 0:482/-10.16; 0.25:481/-2.26; 0.5:478/-1.69; 1:469/-1.18; 1.5:467/-1.00; 2:465/-0.88 | 34 | -0.847 | 35 | -1.830 |

- **OUT-OF-FOLD (chosen k)**: n=318 mean net R -0.883, 95% CI [-1.052, -0.713], median -1.349
- **same test blocks at k=0**: n=330 mean net R -12.986, 95% CI [-32.607, -2.853], median -2.021

## p4_episode / ATR basis zone_tf / DERIBIT

Signals with ATR: 59 of 59 (dropped for missing ATR: 0).

### period dev (pooled; IN-SAMPLE for the k grid, not an out-of-sample number)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (dev) | 18 | 18 | 0.0% | 0.0% | 0.0% | 22.2% | +0.213 | -0.599 [-1.786, +0.761] | -1.333 | +0.811 |
| k=0.25 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 27.8% | +0.061 | -0.304 [-1.028, +0.531] | -1.213 | +0.365 |
| k=0.5 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 27.8% | -0.108 | -0.368 [-0.956, +0.297] | -1.162 | +0.260 |
| k=1 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 44.4% | +0.153 | -0.018 [-0.621, +0.631] | -0.613 | +0.171 |
| k=1.5 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 50.0% | +0.024 | -0.104 [-0.602, +0.428] | -0.266 | +0.128 |
| k=2 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 61.1% | +0.049 | -0.054 [-0.471, +0.356] | -0.026 | +0.103 |

### period hist (context only)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (hist) | 41 | 41 | 0.0% | 0.0% | 0.0% | 4.9% | -0.926 | -3.467 [-6.592, -1.735] | -1.581 | +2.541 |
| k=0.25 (hist) | 41 | 41 | 0.0% | 0.0% | 4.9% | 17.1% | -0.207 | -0.622 [-1.158, -0.008] | -1.305 | +0.415 |
| k=0.5 (hist) | 41 | 41 | 0.0% | 0.0% | 4.9% | 24.4% | -0.146 | -0.427 [-0.891, +0.112] | -1.185 | +0.281 |
| k=1 (hist) | 41 | 41 | 0.0% | 0.0% | 7.3% | 43.9% | -0.035 | -0.209 [-0.565, +0.179] | -0.948 | +0.174 |
| k=1.5 (hist) | 41 | 41 | 0.0% | 0.0% | 12.2% | 58.5% | +0.147 | +0.023 [-0.272, +0.327] | +0.117 | +0.123 |
| k=2 (hist) | 41 | 41 | 0.0% | 0.0% | 14.6% | 65.9% | +0.145 | +0.047 [-0.199, +0.296] | +0.103 | +0.097 |

### Walk-forward (expanding, dev only)

| fold | test block | k chosen (BT-TUNED) | train n / mean net at chosen k | train table n/mean net per k | OOS n | OOS mean net | k=0 n | k=0 mean net |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-01-01..2026-01-31 | abstain | - | 0:11/-0.86; 0.25:11/-0.40; 0.5:11/-0.42; 1:11/-0.04; 1.5:11/-0.11; 2:11/+0.02 | 0 | - | 0 | - |
| 2 | 2026-02-01..2026-02-28 | abstain | - | 0:11/-0.86; 0.25:11/-0.40; 0.5:11/-0.42; 1:11/-0.04; 1.5:11/-0.11; 2:11/+0.02 | 0 | - | 0 | - |
| 3 | 2026-03-01..2026-03-31 | abstain | - | 0:11/-0.86; 0.25:11/-0.40; 0.5:11/-0.42; 1:11/-0.04; 1.5:11/-0.11; 2:11/+0.02 | 0 | - | 3 | -1.249 |
| 4 | 2026-04-01..2026-04-30 | abstain | - | 0:14/-0.95; 0.25:14/-0.36; 0.5:14/-0.38; 1:14/+0.03; 1.5:14/-0.05; 2:14/+0.03 | 0 | - | 3 | +1.231 |
| 5 | 2026-05-01..2026-05-31 | abstain | - | 0:17/-0.56; 0.25:17/-0.25; 0.5:17/-0.32; 1:17/+0.04; 1.5:17/-0.05; 2:17/+0.00 | 0 | - | 0 | - |
| 6 | 2026-06-01..2026-06-25 | abstain | - | 0:17/-0.56; 0.25:17/-0.25; 0.5:17/-0.32; 1:17/+0.04; 1.5:17/-0.05; 2:17/+0.00 | 0 | - | 1 | -1.229 |

- **OUT-OF-FOLD (chosen k)**: n=0
- **same test blocks at k=0**: n=7 mean net R -0.183, 95% CI [-2.825, +2.796], median -1.229

## p4_episode / ATR basis zone_tf / ALL_TAKER

Signals with ATR: 59 of 59 (dropped for missing ATR: 0).

### period dev (pooled; IN-SAMPLE for the k grid, not an out-of-sample number)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (dev) | 18 | 18 | 0.0% | 0.0% | 0.0% | 22.2% | +0.213 | -1.410 [-2.996, +0.094] | -1.665 | +1.622 |
| k=0.25 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 27.8% | +0.061 | -0.683 [-1.428, +0.140] | -1.425 | +0.744 |
| k=0.5 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 27.8% | -0.108 | -0.639 [-1.219, +0.020] | -1.324 | +0.531 |
| k=1 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 44.4% | +0.153 | -0.196 [-0.793, +0.453] | -0.698 | +0.349 |
| k=1.5 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 50.0% | +0.024 | -0.238 [-0.730, +0.295] | -0.354 | +0.262 |
| k=2 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 61.1% | +0.049 | -0.162 [-0.579, +0.248] | -0.098 | +0.211 |

### period hist (context only)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (hist) | 41 | 41 | 0.0% | 0.0% | 0.0% | 4.9% | -0.926 | -6.008 [-12.221, -2.559] | -2.163 | +5.082 |
| k=0.25 (hist) | 41 | 41 | 0.0% | 0.0% | 4.9% | 17.1% | -0.207 | -1.076 [-1.637, -0.456] | -1.610 | +0.869 |
| k=0.5 (hist) | 41 | 41 | 0.0% | 0.0% | 4.9% | 24.4% | -0.146 | -0.734 [-1.196, -0.204] | -1.370 | +0.587 |
| k=1 (hist) | 41 | 41 | 0.0% | 0.0% | 7.3% | 43.9% | -0.035 | -0.406 [-0.761, -0.020] | -1.070 | +0.370 |
| k=1.5 (hist) | 41 | 41 | 0.0% | 0.0% | 12.2% | 58.5% | +0.147 | -0.127 [-0.418, +0.168] | -0.107 | +0.274 |
| k=2 (hist) | 41 | 41 | 0.0% | 0.0% | 14.6% | 65.9% | +0.145 | -0.073 [-0.316, +0.169] | -0.038 | +0.218 |

### Walk-forward (expanding, dev only)

| fold | test block | k chosen (BT-TUNED) | train n / mean net at chosen k | train table n/mean net per k | OOS n | OOS mean net | k=0 n | k=0 mean net |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-01-01..2026-01-31 | abstain | - | 0:11/-1.41; 0.25:11/-0.75; 0.5:11/-0.68; 1:11/-0.22; 1.5:11/-0.25; 2:11/-0.10 | 0 | - | 0 | - |
| 2 | 2026-02-01..2026-02-28 | abstain | - | 0:11/-1.41; 0.25:11/-0.75; 0.5:11/-0.68; 1:11/-0.22; 1.5:11/-0.25; 2:11/-0.10 | 0 | - | 0 | - |
| 3 | 2026-03-01..2026-03-31 | abstain | - | 0:11/-1.41; 0.25:11/-0.75; 0.5:11/-0.68; 1:11/-0.22; 1.5:11/-0.25; 2:11/-0.10 | 0 | - | 3 | -3.247 |
| 4 | 2026-04-01..2026-04-30 | abstain | - | 0:14/-1.81; 0.25:14/-0.75; 0.5:14/-0.66; 1:14/-0.15; 1.5:14/-0.19; 2:14/-0.08 | 0 | - | 3 | +0.452 |
| 5 | 2026-05-01..2026-05-31 | abstain | - | 0:17/-1.41; 0.25:17/-0.65; 0.5:17/-0.60; 1:17/-0.14; 1.5:17/-0.19; 2:17/-0.11 | 0 | - | 0 | - |
| 6 | 2026-06-01..2026-06-25 | abstain | - | 0:17/-1.41; 0.25:17/-0.65; 0.5:17/-0.60; 1:17/-0.14; 1.5:17/-0.19; 2:17/-0.11 | 0 | - | 1 | -1.458 |

- **OUT-OF-FOLD (chosen k)**: n=0
- **same test blocks at k=0**: n=7 mean net R -1.406, 95% CI [-5.194, +1.909], median -1.458

## p4_episode / ATR basis 1m / DERIBIT

Signals with ATR: 59 of 59 (dropped for missing ATR: 0).

### period dev (pooled; IN-SAMPLE for the k grid, not an out-of-sample number)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (dev) | 18 | 18 | 0.0% | 0.0% | 0.0% | 22.2% | +0.213 | -0.599 [-1.786, +0.761] | -1.333 | +0.811 |
| k=0.25 (dev) | 18 | 18 | 0.0% | 0.0% | 0.0% | 22.2% | +0.053 | -0.569 [-1.539, +0.523] | -1.292 | +0.622 |
| k=0.5 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 22.2% | +0.106 | -0.401 [-1.291, +0.566] | -1.241 | +0.507 |
| k=1 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 27.8% | +0.014 | -0.370 [-1.105, +0.428] | -1.169 | +0.385 |
| k=1.5 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 27.8% | -0.074 | -0.388 [-1.045, +0.316] | -1.135 | +0.314 |
| k=2 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 27.8% | -0.137 | -0.404 [-0.996, +0.239] | -1.117 | +0.268 |

### period hist (context only)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (hist) | 41 | 41 | 0.0% | 0.0% | 0.0% | 4.9% | -0.926 | -3.467 [-6.592, -1.735] | -1.581 | +2.541 |
| k=0.25 (hist) | 41 | 41 | 0.0% | 0.0% | 2.4% | 12.2% | -0.567 | -1.304 [-1.781, -0.730] | -1.430 | +0.737 |
| k=0.5 (hist) | 41 | 41 | 0.0% | 0.0% | 2.4% | 17.1% | -0.271 | -0.813 [-1.374, -0.168] | -1.293 | +0.543 |
| k=1 (hist) | 41 | 41 | 0.0% | 0.0% | 2.4% | 24.4% | -0.131 | -0.505 [-1.046, +0.113] | -1.192 | +0.375 |
| k=1.5 (hist) | 41 | 41 | 0.0% | 0.0% | 4.9% | 31.7% | +0.101 | -0.177 [-0.715, +0.451] | -1.141 | +0.279 |
| k=2 (hist) | 41 | 41 | 0.0% | 0.0% | 7.3% | 39.0% | +0.126 | -0.101 [-0.582, +0.438] | -1.092 | +0.227 |

### Walk-forward (expanding, dev only)

| fold | test block | k chosen (BT-TUNED) | train n / mean net at chosen k | train table n/mean net per k | OOS n | OOS mean net | k=0 n | k=0 mean net |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-01-01..2026-01-31 | abstain | - | 0:11/-0.86; 0.25:11/-0.78; 0.5:11/-0.48; 1:11/-0.40; 1.5:11/-0.41; 2:11/-0.42 | 0 | - | 0 | - |
| 2 | 2026-02-01..2026-02-28 | abstain | - | 0:11/-0.86; 0.25:11/-0.78; 0.5:11/-0.48; 1:11/-0.40; 1.5:11/-0.41; 2:11/-0.42 | 0 | - | 0 | - |
| 3 | 2026-03-01..2026-03-31 | abstain | - | 0:11/-0.86; 0.25:11/-0.78; 0.5:11/-0.48; 1:11/-0.40; 1.5:11/-0.41; 2:11/-0.42 | 0 | - | 3 | -1.249 |
| 4 | 2026-04-01..2026-04-30 | abstain | - | 0:14/-0.95; 0.25:14/-0.78; 0.5:14/-0.50; 1:14/-0.40; 1.5:14/-0.38; 2:14/-0.38 | 0 | - | 3 | +1.231 |
| 5 | 2026-05-01..2026-05-31 | abstain | - | 0:17/-0.56; 0.25:17/-0.53; 0.5:17/-0.36; 1:17/-0.33; 1.5:17/-0.35; 2:17/-0.36 | 0 | - | 0 | - |
| 6 | 2026-06-01..2026-06-25 | abstain | - | 0:17/-0.56; 0.25:17/-0.53; 0.5:17/-0.36; 1:17/-0.33; 1.5:17/-0.35; 2:17/-0.36 | 0 | - | 1 | -1.229 |

- **OUT-OF-FOLD (chosen k)**: n=0
- **same test blocks at k=0**: n=7 mean net R -0.183, 95% CI [-2.825, +2.796], median -1.229

## p4_episode / ATR basis 1m / ALL_TAKER

Signals with ATR: 59 of 59 (dropped for missing ATR: 0).

### period dev (pooled; IN-SAMPLE for the k grid, not an out-of-sample number)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (dev) | 18 | 18 | 0.0% | 0.0% | 0.0% | 22.2% | +0.213 | -1.410 [-2.996, +0.094] | -1.665 | +1.622 |
| k=0.25 (dev) | 18 | 18 | 0.0% | 0.0% | 0.0% | 22.2% | +0.053 | -1.191 [-2.417, -0.016] | -1.583 | +1.244 |
| k=0.5 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 22.2% | +0.106 | -0.922 [-2.009, +0.130] | -1.482 | +1.028 |
| k=1 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 27.8% | +0.014 | -0.766 [-1.618, +0.089] | -1.338 | +0.780 |
| k=1.5 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 27.8% | -0.074 | -0.711 [-1.446, +0.023] | -1.270 | +0.638 |
| k=2 (dev) | 18 | 18 | 0.0% | 0.0% | 5.6% | 27.8% | -0.137 | -0.680 [-1.333, -0.011] | -1.233 | +0.543 |

### period hist (context only)

| k / period | orders | filled | no_fill | ran | win (target) | timeout | gross R | net R mean [95% CI] | net R med | fee R |
|---|---|---|---|---|---|---|---|---|---|---|
| k=0 (hist) | 41 | 41 | 0.0% | 0.0% | 0.0% | 4.9% | -0.926 | -6.008 [-12.221, -2.559] | -2.163 | +5.082 |
| k=0.25 (hist) | 41 | 41 | 0.0% | 0.0% | 2.4% | 12.2% | -0.567 | -2.054 [-2.740, -1.385] | -1.860 | +1.487 |
| k=0.5 (hist) | 41 | 41 | 0.0% | 0.0% | 2.4% | 17.1% | -0.271 | -1.368 [-1.976, -0.682] | -1.585 | +1.097 |
| k=1 (hist) | 41 | 41 | 0.0% | 0.0% | 2.4% | 24.4% | -0.131 | -0.891 [-1.453, -0.282] | -1.384 | +0.760 |
| k=1.5 (hist) | 41 | 41 | 0.0% | 0.0% | 4.9% | 31.7% | +0.101 | -0.493 [-1.015, +0.112] | -1.283 | +0.594 |
| k=2 (hist) | 41 | 41 | 0.0% | 0.0% | 7.3% | 39.0% | +0.126 | -0.365 [-0.836, +0.163] | -1.193 | +0.491 |

### Walk-forward (expanding, dev only)

| fold | test block | k chosen (BT-TUNED) | train n / mean net at chosen k | train table n/mean net per k | OOS n | OOS mean net | k=0 n | k=0 mean net |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-01-01..2026-01-31 | abstain | - | 0:11/-1.41; 0.25:11/-1.21; 0.5:11/-0.86; 1:11/-0.71; 1.5:11/-0.67; 2:11/-0.64 | 0 | - | 0 | - |
| 2 | 2026-02-01..2026-02-28 | abstain | - | 0:11/-1.41; 0.25:11/-1.21; 0.5:11/-0.86; 1:11/-0.71; 1.5:11/-0.67; 2:11/-0.64 | 0 | - | 0 | - |
| 3 | 2026-03-01..2026-03-31 | abstain | - | 0:11/-1.41; 0.25:11/-1.21; 0.5:11/-0.86; 1:11/-0.71; 1.5:11/-0.67; 2:11/-0.64 | 0 | - | 3 | -3.247 |
| 4 | 2026-04-01..2026-04-30 | abstain | - | 0:14/-1.81; 0.25:14/-1.45; 0.5:14/-1.06; 1:14/-0.82; 1.5:14/-0.74; 2:14/-0.69 | 0 | - | 3 | +0.452 |
| 5 | 2026-05-01..2026-05-31 | abstain | - | 0:17/-1.41; 0.25:17/-1.18; 0.5:17/-0.90; 1:17/-0.74; 1.5:17/-0.68; 2:17/-0.65 | 0 | - | 0 | - |
| 6 | 2026-06-01..2026-06-25 | abstain | - | 0:17/-1.41; 0.25:17/-1.18; 0.5:17/-0.90; 1:17/-0.74; 1.5:17/-0.68; 2:17/-0.65 | 0 | - | 1 | -1.458 |

- **OUT-OF-FOLD (chosen k)**: n=0
- **same test blocks at k=0**: n=7 mean net R -1.406, 95% CI [-5.194, +1.909], median -1.458

## Walk-forward summary (all 8 runs)

| variant | ATR basis | fees | folds with a k | OOS n | OOS mean net R | OOS 95% CI | k=0 same blocks mean net R | k picked per fold | passes (mean>0 and CI lo>0) |
|---|---|---|---|---|---|---|---|---|---|
| watch_episode | zone_tf | DERIBIT | 6/6 | 295 | -0.200 | [-0.277, -0.120] | -6.595 | 2,2,2,2,2,2 | no |
| watch_episode | zone_tf | ALL_TAKER | 6/6 | 295 | -0.330 | [-0.406, -0.248] | -12.986 | 2,2,2,2,2,2 | no |
| watch_episode | 1m | DERIBIT | 6/6 | 318 | -0.551 | [-0.704, -0.385] | -6.595 | 1.5,2,2,2,2,2 | no |
| watch_episode | 1m | ALL_TAKER | 6/6 | 318 | -0.883 | [-1.052, -0.713] | -12.986 | 2,2,2,2,2,2 | no |
| p4_episode | zone_tf | DERIBIT | 0/6 | 0 | - | - | -0.183 | -,-,-,-,-,- | no |
| p4_episode | zone_tf | ALL_TAKER | 0/6 | 0 | - | - | -1.406 | -,-,-,-,-,- | no |
| p4_episode | 1m | DERIBIT | 0/6 | 0 | - | - | -0.183 | -,-,-,-,-,- | no |
| p4_episode | 1m | ALL_TAKER | 0/6 | 0 | - | - | -1.406 | -,-,-,-,-,- | no |

VERDICT: NO. In none of the 8 walk-forward runs (2 variants x 2 ATR bases x 2 fee profiles) does the chosen stop buffer give out-of-fold net R > 0 with the 95% CI above zero. A wider ATR stop shrinks the fee drag but does not create an edge.

Grid-edge note: the largest registered k (2) was chosen in 23 of 24 folds that picked a k. Net R improves monotonically with k (fee drag shrinks) while gross R stays negative, so the optimum sits at the edge of the grid: the grid was not widened (that would be a new trial family after seeing results), and the verdict does not depend on it because even the edge cell has a negative mean.

Consistency check: k=0, watch_episode, zone_tf ATR, DERIBIT gives 2699 resolved filled trades over hist+dev (tom_stop_width.py B146 reported 2699 with no ATR requirement; 0 signals had no ATR and were dropped).

## Caveats

- Scope: Tom core only. The other tight-stop layers named in T081 (CryptoCred cc_setups stop_buffer_pct 0.001, B143; fabio, etc.) are NOT run here: they have their own row sources and B143 forbids gridding NO-SOURCE values without a separate ruling. Follow-up needed.
- k pooled over dev is in-sample; only the walk-forward 'OUT-OF-FOLD' lines are out-of-sample. Mean net R is dominated by fee drag on very small stops at k=0 (see median columns).
- Same signal set is reused across k, but one_at_a_time busy-state depends on exit time, so orders processed can differ slightly between k (the 'orders' column shows it).
- Funding is not modelled (as in tom_bt.py). Holdout 2026-06-26.. not selected on, not reported.

