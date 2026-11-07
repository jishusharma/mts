# ADX/DI 2d cross census

Card adx-di-2d-cross-census-1107; SPEC.md; formulas FORMULAS.md section 30. Context layer, no orders, no edge claim; every threshold is OURS (CCU, Steve 2026-11-05, names none). Data: btc_daily.csv (2017-01-01..2026-11-06, 3597 daily bars -> 1799 closed 2d bars), n = 14, indicator warm-up from 2017-01-01, crosses reported from 2020-01-01. Swing extreme = lowest low (red) / highest high (green) in the 30 2d bars after the cross; depth = extreme / close at the cross - 1; rows with fewer than 30 bars after are '-' and not counted in the depth/bars columns (n_dp). Whipsaw = opposite cross within k bars; cells need k bars after (n_ws).

**1h / 4h not run:** no 1h/4h BTC kline file covering 2020-2026 is on this machine (F:/MTS/data holds aggTrades and short orderflow files only), so table (c) is 1d-vs-2d only (DECISION OURS).

## (b) bucket x slope (per split)

### DEV 2020-01-01..2024-06-30: 56 crosses (red 28, green 28)

| dir | ADX | slope | n | n_ws | whipsaw<=3 | n_dp | median depth (dir all = absolute) | median bars to extreme |
|---|---|---|---|---|---|---|---|---|
| all | <20 | falling | 22 | 22 | 31.8% | 22 | 20.6% | 18.5 |
| all | <20 | rising | 1 | 1 | 0.0% | 1 | 2.8% | 6.0 |
| all | 20-40 | falling | 28 | 28 | 35.7% | 28 | 12.1% | 8.5 |
| all | 20-40 | rising | 4 | 4 | 25.0% | 4 | 17.6% | 16.0 |
| all | >40 | falling | 1 | 1 | 0.0% | 1 | 32.2% | 20.0 |
| all | >40 | rising | 0 | 0 | - | 0 | - | - |
| red | <20 | falling | 9 | 9 | 33.3% | 9 | -7.5% | 7.0 |
| red | <20 | rising | 1 | 1 | 0.0% | 1 | -2.8% | 6.0 |
| red | 20-40 | falling | 17 | 17 | 17.6% | 17 | -13.9% | 5.0 |
| red | 20-40 | rising | 1 | 1 | 0.0% | 1 | -4.4% | 12.0 |
| red | >40 | falling | 0 | 0 | - | 0 | - | - |
| red | >40 | rising | 0 | 0 | - | 0 | - | - |
| green | <20 | falling | 13 | 13 | 30.8% | 13 | 31.0% | 20.0 |
| green | <20 | rising | 0 | 0 | - | 0 | - | - |
| green | 20-40 | falling | 11 | 11 | 63.6% | 11 | 10.4% | 20.0 |
| green | 20-40 | rising | 3 | 3 | 33.3% | 3 | 29.2% | 20.0 |
| green | >40 | falling | 1 | 1 | 0.0% | 1 | 32.2% | 20.0 |
| green | >40 | rising | 0 | 0 | - | 0 | - | - |
| all | all | all | 56 | 56 | 32.1% | 56 | 14.8% | 16.0 |

### VALIDATION 2024-07-01..2025-06-30: 15 crosses (red 7, green 8)

| dir | ADX | slope | n | n_ws | whipsaw<=3 | n_dp | median depth (dir all = absolute) | median bars to extreme |
|---|---|---|---|---|---|---|---|---|
| all | <20 | falling | 7 | 7 | 14.3% | 7 | 17.3% | 5.0 |
| all | <20 | rising | 0 | 0 | - | 0 | - | - |
| all | 20-40 | falling | 8 | 8 | 75.0% | 8 | 16.3% | 12.0 |
| all | 20-40 | rising | 0 | 0 | - | 0 | - | - |
| all | >40 | falling | 0 | 0 | - | 0 | - | - |
| all | >40 | rising | 0 | 0 | - | 0 | - | - |
| red | <20 | falling | 3 | 3 | 0.0% | 3 | -21.6% | 5.0 |
| red | <20 | rising | 0 | 0 | - | 0 | - | - |
| red | 20-40 | falling | 4 | 4 | 100.0% | 4 | -16.3% | 17.5 |
| red | 20-40 | rising | 0 | 0 | - | 0 | - | - |
| red | >40 | falling | 0 | 0 | - | 0 | - | - |
| red | >40 | rising | 0 | 0 | - | 0 | - | - |
| green | <20 | falling | 4 | 4 | 25.0% | 4 | 13.2% | 14.5 |
| green | <20 | rising | 0 | 0 | - | 0 | - | - |
| green | 20-40 | falling | 4 | 4 | 50.0% | 4 | 15.6% | 12.0 |
| green | 20-40 | rising | 0 | 0 | - | 0 | - | - |
| green | >40 | falling | 0 | 0 | - | 0 | - | - |
| green | >40 | rising | 0 | 0 | - | 0 | - | - |
| all | all | all | 15 | 15 | 46.7% | 15 | 17.3% | 9.0 |

### RECENT 2025-07-01..2026-11-07 (descriptive; holds CCU's Oct-2025 / Jan-2026 / May-2026 cases): 17 crosses (red 9, green 8)

| dir | ADX | slope | n | n_ws | whipsaw<=3 | n_dp | median depth (dir all = absolute) | median bars to extreme |
|---|---|---|---|---|---|---|---|---|
| all | <20 | falling | 5 | 5 | 40.0% | 5 | 13.4% | 17.0 |
| all | <20 | rising | 1 | 1 | 0.0% | 1 | 28.5% | 21.0 |
| all | 20-40 | falling | 11 | 10 | 60.0% | 8 | 14.3% | 11.5 |
| all | 20-40 | rising | 0 | 0 | - | 0 | - | - |
| all | >40 | falling | 0 | 0 | - | 0 | - | - |
| all | >40 | rising | 0 | 0 | - | 0 | - | - |
| red | <20 | falling | 2 | 2 | 100.0% | 2 | -18.6% | 25.5 |
| red | <20 | rising | 1 | 1 | 0.0% | 1 | -28.5% | 21.0 |
| red | 20-40 | falling | 6 | 5 | 40.0% | 4 | -28.6% | 12.0 |
| red | 20-40 | rising | 0 | 0 | - | 0 | - | - |
| red | >40 | falling | 0 | 0 | - | 0 | - | - |
| red | >40 | rising | 0 | 0 | - | 0 | - | - |
| green | <20 | falling | 3 | 3 | 0.0% | 3 | 13.4% | 17.0 |
| green | <20 | rising | 0 | 0 | - | 0 | - | - |
| green | 20-40 | falling | 5 | 5 | 80.0% | 4 | 8.3% | 9.0 |
| green | 20-40 | rising | 0 | 0 | - | 0 | - | - |
| green | >40 | falling | 0 | 0 | - | 0 | - | - |
| green | >40 | rising | 0 | 0 | - | 0 | - | - |
| all | all | all | 17 | 16 | 50.0% | 14 | 15.0% | 16.0 |

## CCU check: red crosses, 2020-01-01..2025-06-30 (DEV+VALIDATION, full 30-bar window), n = 35

| bars to the low (2d bars) | n | share | median depth |
|---|---|---|---|
| 1-3 | 13 | 37.1% | -3.6% |
| 4-7 | 7 | 20.0% | -7.3% |
| 8-12 | 3 | 8.6% | -13.9% |
| 13-20 | 5 | 14.3% | -21.6% |
| 21-30 | 7 | 20.0% | -22.9% |

(CCU: 1-3 weeks of consolidation = 7-10 bars of 2d, then a straight fall. The table counts where the low actually sits after EVERY red cross, not his three cases.)

## (a) every 2d cross

| date | dir | ADX | slope5 | bars to extreme | depth | nfwd | whip1 | whip2 | whip3 |
|---|---|---|---|---|---|---|---|---|---|
| 2020-01-05 | green | 17.1 | -3.8 | 19 | 35.3% | 30 | no | no | no |
| 2020-02-26 | red | 30.8 | -3.6 | 8 | -57.1% | 30 | no | no | no |
| 2020-03-05 | green | 24.3 | -8.5 | 28 | 3.6% | 30 | yes | yes | yes |
| 2020-03-07 | red | 23.9 | -7.0 | 3 | -52.9% | 30 | no | no | no |
| 2020-04-22 | green | 19.7 | -4.9 | 20 | 38.7% | 30 | no | no | no |
| 2020-05-24 | red | 17.3 | -4.1 | 1 | -2.3% | 30 | no | yes | yes |
| 2020-05-28 | green | 15.5 | -5.3 | 30 | 20.9% | 30 | no | no | no |
| 2020-06-15 | red | 14.3 | -2.0 | 6 | -7.3% | 30 | no | no | yes |
| 2020-06-21 | green | 12.4 | -3.4 | 28 | 28.7% | 30 | no | yes | yes |
| 2020-06-25 | red | 11.1 | -3.2 | 1 | -3.6% | 30 | no | no | no |
| 2020-07-07 | green | 9.4 | -1.6 | 20 | 32.1% | 30 | yes | yes | yes |
| 2020-07-09 | red | 8.8 | -1.8 | 3 | -2.6% | 30 | no | no | no |
| 2020-07-21 | green | 7.9 | -0.4 | 13 | 31.0% | 30 | no | no | no |
| 2020-09-03 | red | 26.1 | -2.8 | 1 | -5.9% | 30 | no | no | no |
| 2020-09-19 | green | 20.8 | -5.5 | 30 | 69.2% | 30 | yes | yes | yes |
| 2020-09-21 | red | 20.2 | -6.2 | 1 | -3.7% | 30 | no | no | no |
| 2020-10-09 | green | 16.9 | -1.2 | 26 | 76.1% | 30 | no | no | no |
| 2021-04-17 | red | 27.6 | -2.1 | 16 | -46.6% | 30 | no | no | no |
| 2021-07-28 | green | 41.1 | -7.2 | 20 | 32.2% | 30 | no | no | no |
| 2021-09-06 | red | 30.5 | -1.9 | 7 | -15.5% | 30 | no | no | no |
| 2021-09-16 | green | 22.3 | -8.2 | 27 | 45.9% | 30 | no | yes | yes |
| 2021-09-20 | red | 21.6 | -5.4 | 1 | -0.4% | 30 | no | no | no |
| 2021-09-30 | green | 22.5 | 0.9 | 20 | 43.3% | 30 | no | no | no |
| 2021-11-25 | red | 27.6 | -10.2 | 30 | -38.7% | 30 | no | yes | yes |
| 2021-11-29 | green | 24.4 | -8.9 | 1 | 3.7% | 30 | no | yes | yes |
| 2021-12-03 | red | 24.3 | -4.9 | 26 | -33.0% | 30 | no | no | no |
| 2022-02-15 | green | 30.7 | -11.5 | 20 | 9.8% | 30 | yes | yes | yes |
| 2022-02-17 | red | 29.5 | -9.9 | 3 | -14.1% | 30 | no | no | no |
| 2022-03-17 | green | 19.0 | -5.8 | 5 | 15.4% | 30 | no | no | no |
| 2022-04-06 | red | 15.7 | -1.3 | 18 | -38.5% | 30 | no | no | no |
| 2022-08-10 | green | 21.3 | -6.8 | 2 | 5.3% | 30 | no | no | no |
| 2022-08-18 | red | 18.4 | -4.0 | 17 | -13.0% | 30 | no | no | no |
| 2022-09-11 | green | 21.4 | -0.0 | 1 | 1.8% | 30 | yes | yes | yes |
| 2022-09-13 | red | 20.8 | -1.2 | 28 | -22.9% | 30 | no | no | no |
| 2022-10-03 | green | 17.2 | -3.5 | 16 | 5.6% | 30 | no | yes | yes |
| 2022-10-07 | red | 15.3 | -4.5 | 22 | -20.3% | 30 | no | no | yes |
| 2022-10-13 | green | 13.2 | -4.0 | 11 | 12.0% | 30 | no | no | no |
| 2022-11-08 | red | 18.2 | 3.9 | 6 | -2.8% | 30 | no | no | no |
| 2022-12-14 | green | 25.3 | -4.7 | 25 | 39.7% | 30 | yes | yes | yes |
| 2022-12-16 | red | 24.3 | -5.5 | 1 | -3.1% | 30 | no | no | no |
| 2023-01-09 | green | 16.6 | -3.8 | 19 | 44.8% | 30 | no | no | no |
| 2023-03-08 | red | 34.8 | -9.4 | 1 | -4.0% | 30 | no | yes | yes |
| 2023-03-12 | green | 33.0 | -7.5 | 16 | 28.6% | 30 | no | no | no |
| 2023-05-07 | red | 22.9 | -6.3 | 19 | -10.4% | 30 | no | no | no |
| 2023-05-27 | green | 17.7 | -2.2 | 23 | 13.3% | 30 | no | yes | yes |
| 2023-05-31 | red | 16.1 | -2.9 | 7 | -7.5% | 30 | no | no | no |
| 2023-06-20 | green | 21.5 | 3.0 | 11 | 6.0% | 30 | no | no | no |
| 2023-08-17 | red | 21.8 | 2.9 | 12 | -4.4% | 30 | no | no | no |
| 2023-08-29 | green | 24.2 | 1.2 | 28 | 29.2% | 30 | yes | yes | yes |
| 2023-08-31 | red | 23.0 | -1.5 | 5 | -3.5% | 30 | no | no | no |
| 2023-09-18 | green | 15.0 | -3.8 | 29 | 39.6% | 30 | no | no | no |
| 2024-01-22 | red | 28.6 | -6.6 | 1 | -1.0% | 30 | no | no | yes |
| 2024-01-28 | green | 24.3 | -7.2 | 23 | 70.4% | 30 | no | no | no |
| 2024-04-13 | red | 35.9 | -8.8 | 9 | -13.9% | 30 | no | no | no |
| 2024-05-15 | green | 20.5 | -3.3 | 11 | 10.4% | 30 | no | no | no |
| 2024-06-14 | red | 16.4 | -2.2 | 26 | -26.0% | 30 | no | no | no |
| 2024-07-20 | green | 22.7 | -4.7 | 4 | 2.8% | 30 | no | yes | yes |
| 2024-07-24 | red | 20.3 | -7.2 | 6 | -25.5% | 30 | yes | yes | yes |
| 2024-07-26 | green | 19.1 | -6.8 | 1 | 3.2% | 30 | no | yes | yes |
| 2024-07-30 | red | 17.1 | -5.6 | 3 | -24.2% | 30 | no | no | no |
| 2024-09-26 | green | 20.3 | -6.2 | 28 | 51.4% | 30 | no | yes | yes |
| 2024-09-30 | red | 19.3 | -4.9 | 5 | -3.1% | 30 | no | no | no |
| 2024-10-14 | green | 18.1 | -1.6 | 26 | 55.2% | 30 | no | no | no |
| 2024-12-27 | red | 31.1 | -11.3 | 30 | -13.7% | 30 | no | no | yes |
| 2025-01-02 | green | 25.9 | -9.6 | 9 | 11.6% | 30 | no | no | no |
| 2025-01-12 | red | 20.0 | -5.9 | 29 | -19.0% | 30 | yes | yes | yes |
| 2025-01-14 | green | 19.0 | -5.5 | 3 | 9.0% | 30 | no | no | no |
| 2025-02-01 | red | 18.0 | -2.4 | 19 | -21.6% | 30 | no | no | no |
| 2025-04-22 | green | 21.5 | -3.0 | 15 | 19.5% | 30 | no | no | no |
| 2025-06-21 | red | 21.3 | -4.6 | 1 | -1.3% | 30 | yes | yes | yes |
| 2025-06-23 | green | 19.8 | -4.9 | 26 | 17.3% | 30 | no | no | no |
| 2025-08-26 | red | 17.7 | -6.1 | 22 | -8.3% | 30 | no | no | yes |
| 2025-09-01 | green | 15.3 | -5.1 | 17 | 13.4% | 30 | no | no | no |
| 2025-09-23 | red | 15.6 | -0.5 | 29 | -28.9% | 30 | no | no | yes |
| 2025-09-29 | green | 14.3 | -3.6 | 3 | 10.7% | 30 | no | no | no |
| 2025-10-09 | red | 19.8 | 5.6 | 21 | -28.5% | 30 | no | no | no |
| 2026-01-05 | green | 29.5 | -6.7 | 4 | 4.5% | 30 | yes | yes | yes |
| 2026-01-07 | red | 27.7 | -7.6 | 15 | -34.1% | 30 | no | no | yes |
| 2026-01-13 | green | 24.1 | -7.3 | 1 | 0.2% | 30 | no | no | yes |
| 2026-01-19 | red | 22.4 | -3.7 | 9 | -32.1% | 30 | no | no | no |
| 2026-03-16 | green | 33.9 | -9.1 | 25 | 12.1% | 30 | yes | yes | yes |
| 2026-03-18 | red | 32.3 | -9.8 | 5 | -7.0% | 30 | no | no | no |
| 2026-04-07 | green | 23.7 | -4.9 | 14 | 16.6% | 30 | no | no | no |
| 2026-05-23 | red | 22.3 | -6.4 | 19 | -25.0% | 30 | no | no | no |
| 2026-08-17 | green | 18.6 | -4.1 | 17 | 35.0% | 30 | no | no | no |
| 2026-10-28 | red | 28.3 | -8.6 | - | - | 4 | no | no | yes |
| 2026-11-03 | green | 24.6 | -7.5 | - | - | 1 | yes | yes | yes |
| 2026-11-05 | red | 23.0 | -7.2 | - | - | 0 | - | - | - |

n = 88 crosses from 2020-01-01.

## (c) cascade 1d -> 2d (1h and 4h not run, see top)

| split | 2d crosses | with a same-direction 1d cross in the previous 20 days | share | median lead (days) |
|---|---|---|---|---|
| DEV | 56 | 52 | 92.9% | 400.0% |
| VALIDATION | 15 | 12 | 80.0% | 850.0% |
| RECENT | 17 | 15 | 88.2% | 1300.0% |

Lead per 2d cross (days from the first same-direction 1d cross close to the 2d cross close; 'none' = no 1d cross in the previous 20 days):

| date | dir | lead days |
|---|---|---|
| 2020-01-05 | green | 15.0 |
| 2020-02-26 | red | 10.0 |
| 2020-03-05 | green | 17.0 |
| 2020-03-07 | red | 20.0 |
| 2020-04-22 | green | 17.0 |
| 2020-05-24 | red | 1.0 |
| 2020-05-28 | green | 2.0 |
| 2020-06-15 | red | 2.0 |
| 2020-06-21 | green | 0.0 |
| 2020-06-25 | red | 12.0 |
| 2020-07-07 | green | 16.0 |
| 2020-07-09 | red | 16.0 |
| 2020-07-21 | green | 1.0 |
| 2020-09-03 | red | 10.0 |
| 2020-09-19 | green | 4.0 |
| 2020-09-21 | red | 20.0 |
| 2020-10-09 | green | 2.0 |
| 2021-04-17 | red | 0.0 |
| 2021-07-28 | green | 5.0 |
| 2021-09-06 | red | 0.0 |
| 2021-09-16 | green | none |
| 2021-09-20 | red | 14.0 |
| 2021-09-30 | green | 0.0 |
| 2021-11-25 | red | 10.0 |
| 2021-11-29 | green | none |
| 2021-12-03 | red | 18.0 |
| 2022-02-15 | green | 11.0 |
| 2022-02-17 | red | 1.0 |
| 2022-03-17 | green | 17.0 |
| 2022-04-06 | red | 1.0 |
| 2022-08-10 | green | 15.0 |
| 2022-08-18 | red | 0.0 |
| 2022-09-11 | green | 3.0 |
| 2022-09-13 | red | 1.0 |
| 2022-10-03 | green | 1.0 |
| 2022-10-07 | red | none |
| 2022-10-13 | green | 11.0 |
| 2022-11-08 | red | 1.0 |
| 2022-12-14 | green | 2.0 |
| 2022-12-16 | red | 1.0 |
| 2023-01-09 | green | 4.0 |
| 2023-03-08 | red | 6.0 |
| 2023-03-12 | green | 8.0 |
| 2023-05-07 | red | 17.0 |
| 2023-05-27 | green | 0.0 |
| 2023-05-31 | red | 1.0 |
| 2023-06-20 | green | 1.0 |
| 2023-08-17 | red | 17.0 |
| 2023-08-29 | green | 1.0 |
| 2023-08-31 | red | 16.0 |
| 2023-09-18 | green | 1.0 |
| 2024-01-22 | red | 20.0 |
| 2024-01-28 | green | none |
| 2024-04-13 | red | 13.0 |
| 2024-05-15 | green | 1.0 |
| 2024-06-14 | red | 4.0 |
| 2024-07-20 | green | 6.0 |
| 2024-07-24 | red | none |
| 2024-07-26 | green | 12.0 |
| 2024-07-30 | red | none |
| 2024-09-26 | green | 10.0 |
| 2024-09-30 | red | 0.0 |
| 2024-10-14 | green | 8.0 |
| 2024-12-27 | red | 8.0 |
| 2025-01-02 | green | none |
| 2025-01-12 | red | 5.0 |
| 2025-01-14 | green | 9.0 |
| 2025-02-01 | red | 7.0 |
| 2025-04-22 | green | 11.0 |
| 2025-06-21 | red | 18.0 |
| 2025-06-23 | green | 15.0 |
| 2025-08-26 | red | 8.0 |
| 2025-09-01 | green | 11.0 |
| 2025-09-23 | red | 2.0 |
| 2025-09-29 | green | 1.0 |
| 2025-10-09 | red | 18.0 |
| 2026-01-05 | green | 8.0 |
| 2026-01-07 | red | none |
| 2026-01-13 | green | 16.0 |
| 2026-01-19 | red | 0.0 |
| 2026-03-16 | green | 13.0 |
| 2026-03-18 | red | 13.0 |
| 2026-04-07 | green | 16.0 |
| 2026-05-23 | red | 6.0 |
| 2026-08-17 | green | none |
| 2026-10-28 | red | 16.0 |
| 2026-11-03 | green | 16.0 |
| 2026-11-05 | red | 17.0 |

1d crosses followed by a same-direction 2d cross within 5 2d bars (10 days): 74 of 165 (44.8%); red 41 of 83; green 33 of 82.

n is printed in every table; no conclusion is drawn here (operator reads this file).
