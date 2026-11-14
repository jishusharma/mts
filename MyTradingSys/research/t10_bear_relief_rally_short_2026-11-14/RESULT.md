**T10 bear-phase relief-rally short: SIGN-FLIP (positive only in the phase opposite to the gate). VAL n 115 trades, 28 entry weeks, net +0.160 R (price-only, fee-net), CI -0.273..+0.497.**

Regime mix: gate = BTC < SMA200d on 1094 DEV and 402 VAL days (all bear by gate). Entries by smoothed BTC cycle state: DEV BULL 3 / BASE(range) 17 / BEAR 224; VAL BULL 48 / BASE(range) 0 / BEAR 67.

| row | n | weeks | gross R | fee R | net R | total R (with real funding) |
|---|---|---|---|---|---|---|
| VAL | 115 | 28 | +0.168 | 0.008 | +0.160 | +0.159 |
| DEV | 244 | 42 | +0.054 | 0.006 | +0.048 | +0.045 |

Bars: 1_power=PASS, 2_val_ci=FAIL, 3_dev_sign=PASS, 4_placebo=PASS, 5_ex_best=FAIL, 6_baseline=PASS, 7_top3_coin=PASS, 8_loyo=PASS

Failed bars: 2_val_ci, 5_ex_best. Kill flags: none. Flags: carry_only=False sign_flip=True.

Placebo (same-window, VAL): real +0.160 R, draw mean -0.083, 97.5th +0.059, rank 99.9%, n 115. Global variant: real +0.160, draw mean -0.060, 97.5th +0.087, rank 100.0%.

Baseline (short-and-hold of downtrending coins on gated days, mean daily return): VAL -0.00011, DEV -0.00069; strategy per day in position VAL +0.00489, DEV +0.00133.

Ex-best-2 weeks (VAL) mean -0.077; ex-best-5 -0.259. Top-3 coin removal (VAL): EGLD -> +0.146; EGLD+BCH -> +0.131; EGLD+BCH+SNX -> +0.119. Leave-one-year-out (VAL): 2024 -> +0.107; 2025 -> +0.256; 2026 -> +0.148.

Second unit (rally episode): VAL 11 episodes, mean of pooled R +0.160, CI -0.289..+0.459; DEV 11 episodes, mean +0.048.

Funding: VAL trades with real funding 110 of 115 (rest NOT_IN_DATA, no funding imputed); covered-only net +0.163, total +0.161. Survivorship direction: shorts biased DOWN by survivor-only lists, UP by delisting collapses; ex-ENDED VAL mean +0.160 (n 115), ex-LUNA/FTT VAL mean +0.163 (n 110).

Three bear periods (sign report, not a test; net R): 2018 n 0 mean n/a; 2022 n 157 mean +0.075; 2025-26 n 73 mean +0.360

Holm: single-cell p (week-block bootstrap, one-sided) 0.2214; worst case over the 9-cell family 1.0000.

Rescue row (descriptive only, rally threshold 8%, never the verdict): VAL n 230, weeks 33, net R +0.051 (CI -0.289..+0.355), total R +0.049; DEV n 416, net R +0.048.

## Tables

### by smoothed BTC cycle state (VAL)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| BEAR | 67 | 20 | +0.002 | 0.009 | -0.006 | -0.008 |
| BULL | 48 | 8 | +0.400 | 0.007 | +0.393 | +0.392 |

### by year of entry (VAL)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| 2024 | 21 | 4 | +0.408 | 0.008 | +0.400 | +0.406 |
| 2025 | 53 | 11 | +0.056 | 0.008 | +0.049 | +0.044 |
| 2026 | 41 | 14 | +0.190 | 0.008 | +0.182 | +0.182 |

### by BTC brain label (VAL)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| ACCUM-RANGE | 15 | 4 | +0.003 | 0.008 | -0.005 | +0.001 |
| DISTRIBUTION | 22 | 4 | +0.453 | 0.008 | +0.445 | +0.444 |
| MARKDOWN | 77 | 21 | +0.115 | 0.008 | +0.107 | +0.104 |
| RELIEF | 1 | 1 | +0.522 | 0.006 | +0.516 | +0.515 |

### by exit reason (VAL)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| STOP | 25 | 9 | -1.000 | 0.010 | -1.010 | -1.011 |
| TARGET | 51 | 14 | +0.796 | 0.007 | +0.789 | +0.788 |
| TIME | 39 | 19 | +0.096 | 0.007 | +0.089 | +0.087 |

### by smoothed BTC cycle state (DEV)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| BASE | 17 | 1 | +0.046 | 0.005 | +0.041 | +0.048 |
| BEAR | 224 | 40 | +0.057 | 0.007 | +0.051 | +0.047 |
| BULL | 3 | 1 | -0.150 | 0.002 | -0.153 | -0.150 |

### by year of entry (DEV)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| 2020 | 22 | 4 | -0.496 | 0.006 | -0.502 | -0.504 |
| 2021 | 61 | 10 | +0.187 | 0.005 | +0.182 | +0.184 |
| 2022 | 157 | 25 | +0.081 | 0.007 | +0.075 | +0.070 |
| 2023 | 4 | 3 | -0.032 | 0.010 | -0.042 | -0.049 |

### by BTC brain label (DEV)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| ACCUM-RANGE | 12 | 4 | -0.711 | 0.009 | -0.721 | -0.714 |
| CAPITULATION | 2 | 1 | -1.000 | 0.006 | -1.006 | -1.003 |
| DISTRIBUTION | 2 | 1 | -0.655 | 0.003 | -0.659 | -0.665 |
| MARKDOWN | 188 | 34 | +0.092 | 0.006 | +0.086 | +0.083 |
| RELIEF | 40 | 8 | +0.194 | 0.008 | +0.186 | +0.182 |

### by exit reason (DEV)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| STOP | 66 | 19 | -1.000 | 0.007 | -1.007 | -1.008 |
| TARGET | 90 | 24 | +0.724 | 0.006 | +0.717 | +0.714 |
| TIME | 88 | 24 | +0.160 | 0.006 | +0.154 | +0.150 |

### by smoothed BTC cycle state (ALL)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| BASE | 17 | 1 | +0.046 | 0.005 | +0.041 | +0.048 |
| BEAR | 291 | 60 | +0.045 | 0.007 | +0.038 | +0.035 |
| BULL | 51 | 9 | +0.368 | 0.007 | +0.361 | +0.360 |

### by year of entry (ALL)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| 2020 | 22 | 4 | -0.496 | 0.006 | -0.502 | -0.504 |
| 2021 | 61 | 10 | +0.187 | 0.005 | +0.182 | +0.184 |
| 2022 | 157 | 25 | +0.081 | 0.007 | +0.075 | +0.070 |
| 2023 | 4 | 3 | -0.032 | 0.010 | -0.042 | -0.049 |
| 2024 | 21 | 4 | +0.408 | 0.008 | +0.400 | +0.406 |
| 2025 | 53 | 11 | +0.056 | 0.008 | +0.049 | +0.044 |
| 2026 | 41 | 14 | +0.190 | 0.008 | +0.182 | +0.182 |

### by BTC brain label (ALL)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| ACCUM-RANGE | 27 | 8 | -0.314 | 0.009 | -0.323 | -0.317 |
| CAPITULATION | 2 | 1 | -1.000 | 0.006 | -1.006 | -1.003 |
| DISTRIBUTION | 24 | 5 | +0.361 | 0.008 | +0.353 | +0.352 |
| MARKDOWN | 265 | 55 | +0.099 | 0.006 | +0.092 | +0.089 |
| RELIEF | 41 | 9 | +0.202 | 0.008 | +0.194 | +0.190 |

### by exit reason (ALL)

| key | n | weeks | gross R | fee R | net R | total R (fund) |
|---|---|---|---|---|---|---|
| STOP | 91 | 28 | -1.000 | 0.008 | -1.008 | -1.009 |
| TARGET | 141 | 38 | +0.750 | 0.007 | +0.743 | +0.741 |
| TIME | 127 | 43 | +0.140 | 0.006 | +0.134 | +0.131 |
