**T7 cycle-bottom weekly-reclaim long: FAIL (first failing bar 2_val_ci). VAL n 436 trades in 67 entry weeks, net +0.652 R (CI -0.285 to +1.768), gross +0.687 R, fee 0.0071 R per trade.**

Regime mix: BTC smoothed cycle state of the entry day, VAL: BASE 15% BEAR 44% BULL 41%; DEV: BASE 32% BEAR 64% BULL 4% (trades, not weeks; the market is mostly bear or base at these entries by construction of the 55% drawdown gate).

| Row | n trades | entry weeks | mean net R | CI low | CI high | gross R | net % | note |
|---|---|---|---|---|---|---|---|---|
| VAL | 436 | 67 | +0.652 | -0.285 | +1.768 | +0.687 | +10.61 | funding NOT_IN_DATA on 15, ENDED 1, stop exits 137 |
| DEV | 554 | 85 | +0.267 | -0.225 | +0.793 | +0.302 | +4.79 | funding NOT_IN_DATA on 14, ENDED 1, stop exits 181 |

Bars passed: 1_power, 3_dev_sign, 4_placebo, 6_baseline, 7_top_coin.
Bars failed: 2_val_ci, 5_ex_best, 8_loyo.

| Bar | Pass | Statement |
|---|---|---|
| 1_power | yes | VAL n>=30 trades and >=20 entry weeks |
| 2_val_ci | NO | VAL mean net R > 0 and block-bootstrap CI low > 0 |
| 3_dev_sign | yes | DEV mean net R > 0 |
| 4_placebo | yes | real mean above placebo 97.5th (same-window) |
| 5_ex_best | NO | ex-best entry weeks mean > 0 (and ex-best-2 episodes if >= 8 episodes) |
| 6_baseline | yes | net daily return in position >= DD-basket baseline |
| 7_top_coin | yes | top-coin removal mean > 0 |
| 8_loyo | NO | leave-one-year-out stays > 0 |

Placebo same-window: real +0.652, draw mean +0.325, 97.5th +0.512, excess +0.327, p 0.001, n 436 (skipped 0). Global: real +0.652, draw mean +0.072, 97.5th +0.237, excess +0.580, p 0.001.

Baseline (DD basket, same Mondays, 28d, no stop): +0.043% per day vs real +0.461% per day (VAL); DEV baseline +0.134% vs real +0.213%.

Kill criteria: {'a_val_net_le0': False, 'b_placebo_not_above': False}. Top-3 coin removal (sequential): [('HBAR', '+0.588'), ('CRV', '+0.549'), ('ZRX', '+0.510')]. Ex-best weeks (k=5): mean -0.277.

Episodes VAL: 11 (reading valid); mean +0.011 R, CI -0.580 to +0.698, ex-best-2 -0.475. DEV episodes 13.

Leave-one-year-out VAL: {'2024': '-0.087', '2025': '+1.104', '2026': '+0.912'}.
Holm: per-study p 0.1034 (one cell), family (9 cells) p 0.9310. DEV week-level sd (measured now) +1.264 R.

### BTC cycle state VAL

| key | n | weeks | mean net R | median | win | worst | best |
|---|---|---|---|---|---|---|---|
| BASE | 64 | 12 | +2.183 | +1.652 | 0.86 | -0.84 | +17.08 |
| BEAR | 192 | 29 | +0.184 | -0.041 | 0.48 | -1.04 | +5.66 |
| BULL | 180 | 26 | +0.606 | -0.986 | 0.29 | -1.05 | +29.36 |

### BTC cycle state DEV

| key | n | weeks | mean net R | median | win | worst | best |
|---|---|---|---|---|---|---|---|
| BASE | 176 | 35 | +0.045 | -0.374 | 0.40 | -1.24 | +6.71 |
| BEAR | 354 | 41 | +0.390 | -0.164 | 0.44 | -1.07 | +11.91 |
| BULL | 24 | 9 | +0.077 | -0.020 | 0.46 | -1.15 | +3.23 |

### by year VAL

| key | n | weeks | mean net R | median | win | worst | best |
|---|---|---|---|---|---|---|---|
| 2024 | 151 | 18 | +2.046 | +0.853 | 0.64 | -1.04 | +29.36 |
| 2025 | 135 | 22 | -0.358 | -0.538 | 0.27 | -1.05 | +3.07 |
| 2026 | 150 | 27 | +0.156 | -0.175 | 0.44 | -1.04 | +5.66 |

### by year DEV

| key | n | weeks | mean net R | median | win | worst | best |
|---|---|---|---|---|---|---|---|
| 2020 | 48 | 13 | +0.651 | +0.255 | 0.62 | -1.24 | +6.32 |
| 2021 | 53 | 14 | +1.440 | +1.605 | 0.81 | -1.15 | +11.91 |
| 2022 | 187 | 26 | -0.430 | -0.820 | 0.20 | -1.06 | +5.31 |
| 2023 | 266 | 32 | +0.454 | -0.103 | 0.48 | -1.05 | +9.82 |

BEAR-only VAL: n 192, mean +0.184, CI -0.494 to +0.448. BASE-only VAL: n 64, mean +2.183, CI +0.422 to n/a.
Survivorship: ex-ENDED VAL n 435 mean +0.656; ex-LUNA/FTT VAL n 418 mean +0.680 (DEV: ex-ENDED +0.269, ex-LUNA/FTT +0.264). Direction: longs are biased UP (hindsight list, collapsed coins exit at a last close that may not be tradable).
Thin dates (< 30 alive coins) excluded: 45 trades.

BTC descriptive row (a), not a pass cell: [{"signal_date": "2019-04-07", "entry_date": "2019-04-08", "exit_date": "2019-10-07", "n_coins": 0, "basket_net": NaN, "btc_net": 0.5181210412609013, "split": "DEV"}, {"signal_date": "2020-02-02", "entry_date": "2020-02-03", "exit_date": "2020-03-02", "n_coins": 0, "basket_net": NaN, "btc_net": -0.13027412901639496, "split": "DEV"}, {"signal_date": "2020-05-03", "entry_date": "2020-05-04", "exit_date": "2020-11-02", "n_coins": 24, "basket_net": 0.5615597904526061, "btc_net": 0.47461898531405455, "split": "DEV"}, {"signal_date": "2023-01-15", "entry_date": "2023-01-16", "exit_date": "2023-07-17", "n_coins": 65, "basket_net": -0.07573487371717087, "btc_net": 0.4114556116408691, "split": "DEV"}, {"signal_date": "2023-10-22", "entry_date": "2023-10-23", "exit_date": "2024-04-22", "n_coins": 64, "basket_net": 0.8432649294192925, "btc_net": 1.07144516929876, "split": "DEV"}, {"signal_date": "2026-08-23", "entry_date": "2026-08-24", "exit_date": null, "n_coins": 0, "basket_net": NaN, "btc_net": NaN, "split": "VAL"}]
