# STABILITY - per study x year x side, top-5-days-removed (T10-F4, D4)

DEV bars only (2022-01-01..2024-06-30); no VALIDATION/HOLDOUT read. Produced by `scripts/T10/stability.py` (tests: `test_stability.py`). Mean per trade; units: gross_effect_screen and RSI in % net (0.14 % is the screen's cost bar, already subtracted for the screen; RSI uses its fee model), LC1 in pp of hold rate over the random-line control. Cut `year` = all sides; `long`/`short` rows with a year are the year x side cells; `top5_removed` drops every trade on the 5 days with the largest summed net.

## Sign change when the top 5 days go

**rsi malkan_40_60 4h (+0.2556 -> -0.3961) and rsi malkan_40_60 1d (+0.0091 -> -1.1000) change sign; no other study does.** gross_effect_screen arms T and C are negative before and after (T -0.1968 -> -0.3564); LC1 stays +9.6 -> +9.2 pp; rsi_ma_events 4h (+0.1201 -> +0.0350) and malkan 1h (+0.1714 -> +0.0271) stay positive but lose most of the edge. n is 18 and 11 for the two flipping rows, so the flip is also a small-sample warning.

## DECISIONs (OURS)

- gross_effect_screen: read the published `ledger.csv` (no rerun), primary cell d=1 h=60, net = G - flat 0.01 funding when an 8h settlement lies in [entry, exit] - 0.14 (all PRE_REG values, SOURCED from PRE_REG.md). Arms T (F=1) and C (all).
- LC1: no per-trade payoff exists; each KEEP-family touch counts HOLD(1/0) minus the family's pooled random-line hold rate, in pp, so the mean equals the published `difference`. The 0.14 % bar does not apply to it. Standard DEV 2022-04-01..2024-06-30 as in the Q79 addendum.
- RSI: chosen params fixed from RERUN_FUNDING.md (SOURCED), bars cut at 2024-06-30 (that rerun's IS span reached into VALIDATION, so these rows differ from it), funding off (raw_fund absent on this machine; its effect there was <= 0.0147 pp). Bracket 1 % / 2 %, max 100 bars. malkan_mtf 1d skipped (7 trades, no usable cut).
- Not filed as new cards: both flips are on pre-existing non-PASS rows.

## Table

| study | year | cut | n | mean |
|---|---|---|---|---|
| gross_effect_screen arm T | all | all | 40 | -0.1968 |
| gross_effect_screen arm T | all | top5_removed | 35 | -0.3564 |
| gross_effect_screen arm T | 2022 | year | 16 | -0.2610 |
| gross_effect_screen arm T | 2023 | year | 13 | -0.2251 |
| gross_effect_screen arm T | 2024 | year | 11 | -0.0699 |
| gross_effect_screen arm T | 2022 | long | 12 | -0.2094 |
| gross_effect_screen arm T | 2022 | short | 4 | -0.4158 |
| gross_effect_screen arm T | 2023 | long | 7 | -0.0573 |
| gross_effect_screen arm T | 2023 | short | 6 | -0.4208 |
| gross_effect_screen arm T | 2024 | long | 3 | -0.0084 |
| gross_effect_screen arm T | 2024 | short | 8 | -0.0929 |
| gross_effect_screen arm T | all | long | 22 | -0.1336 |
| gross_effect_screen arm T | all | short | 18 | -0.2740 |
| gross_effect_screen arm C | all | all | 1439 | -0.1481 |
| gross_effect_screen arm C | all | top5_removed | 1406 | -0.1710 |
| gross_effect_screen arm C | 2022 | year | 575 | -0.0938 |
| gross_effect_screen arm C | 2023 | year | 565 | -0.1935 |
| gross_effect_screen arm C | 2024 | year | 299 | -0.1670 |
| gross_effect_screen arm C | 2022 | long | 309 | -0.1970 |
| gross_effect_screen arm C | 2022 | short | 266 | +0.0261 |
| gross_effect_screen arm C | 2023 | long | 251 | -0.1469 |
| gross_effect_screen arm C | 2023 | short | 314 | -0.2307 |
| gross_effect_screen arm C | 2024 | long | 145 | -0.1319 |
| gross_effect_screen arm C | 2024 | short | 154 | -0.2000 |
| gross_effect_screen arm C | all | long | 705 | -0.1658 |
| gross_effect_screen arm C | all | short | 734 | -0.1312 |
| levels_hold LC1 KEEP | all | all | 6968 | +9.6412 |
| levels_hold LC1 KEEP | all | top5_removed | 6897 | +9.2320 |
| levels_hold LC1 KEEP | 2022 | year | 2233 | +9.5710 |
| levels_hold LC1 KEEP | 2023 | year | 3094 | +10.1711 |
| levels_hold LC1 KEEP | 2024 | year | 1641 | +8.7377 |
| levels_hold LC1 KEEP | 2022 | long | 1061 | +10.2531 |
| levels_hold LC1 KEEP | 2022 | short | 1172 | +8.9536 |
| levels_hold LC1 KEEP | 2023 | long | 1556 | +9.3130 |
| levels_hold LC1 KEEP | 2023 | short | 1538 | +11.0393 |
| levels_hold LC1 KEEP | 2024 | long | 801 | +6.9942 |
| levels_hold LC1 KEEP | 2024 | short | 840 | +10.4002 |
| levels_hold LC1 KEEP | all | long | 3418 | +9.0614 |
| levels_hold LC1 KEEP | all | short | 3550 | +10.1995 |
| rsi malkan_40_60 1h | all | all | 80 | +0.1714 |
| rsi malkan_40_60 1h | all | top5_removed | 74 | +0.0271 |
| rsi malkan_40_60 1h | 2022 | year | 36 | +0.3403 |
| rsi malkan_40_60 1h | 2023 | year | 32 | -0.2091 |
| rsi malkan_40_60 1h | 2024 | year | 12 | +0.6790 |
| rsi malkan_40_60 1h | 2022 | long | 18 | +0.2558 |
| rsi malkan_40_60 1h | 2022 | short | 18 | +0.4248 |
| rsi malkan_40_60 1h | 2023 | long | 23 | -0.1255 |
| rsi malkan_40_60 1h | 2023 | short | 9 | -0.4226 |
| rsi malkan_40_60 1h | 2024 | long | 5 | +1.3401 |
| rsi malkan_40_60 1h | 2024 | short | 7 | +0.2069 |
| rsi malkan_40_60 1h | all | long | 46 | +0.1830 |
| rsi malkan_40_60 1h | all | short | 34 | +0.1556 |
| rsi malkan_40_60 4h | all | all | 18 | +0.2556 |
| rsi malkan_40_60 4h | all | top5_removed | 13 | -0.3961 |
| rsi malkan_40_60 4h | 2022 | year | 9 | -0.4222 |
| rsi malkan_40_60 4h | 2023 | year | 7 | +0.6429 |
| rsi malkan_40_60 4h | 2024 | year | 2 | +1.9500 |
| rsi malkan_40_60 4h | 2022 | long | 4 | -1.0995 |
| rsi malkan_40_60 4h | 2022 | short | 5 | +0.1197 |
| rsi malkan_40_60 4h | 2023 | long | 3 | -0.0830 |
| rsi malkan_40_60 4h | 2023 | short | 4 | +1.1874 |
| rsi malkan_40_60 4h | 2024 | long | 1 | +1.9500 |
| rsi malkan_40_60 4h | 2024 | short | 1 | +1.9500 |
| rsi malkan_40_60 4h | all | long | 8 | -0.3371 |
| rsi malkan_40_60 4h | all | short | 10 | +0.7298 |
| rsi malkan_40_60 1d | all | all | 11 | +0.0091 |
| rsi malkan_40_60 1d | all | top5_removed | 6 | -1.1000 |
| rsi malkan_40_60 1d | 2022 | year | 4 | +0.4250 |
| rsi malkan_40_60 1d | 2023 | year | 3 | +0.9332 |
| rsi malkan_40_60 1d | 2024 | year | 4 | -1.0997 |
| rsi malkan_40_60 1d | 2022 | long | 3 | +0.9335 |
| rsi malkan_40_60 1d | 2022 | short | 1 | -1.1005 |
| rsi malkan_40_60 1d | 2023 | long | 1 | +1.9500 |
| rsi malkan_40_60 1d | 2023 | short | 2 | +0.4248 |
| rsi malkan_40_60 1d | 2024 | long | 3 | -1.0995 |
| rsi malkan_40_60 1d | 2024 | short | 1 | -1.1005 |
| rsi malkan_40_60 1d | all | long | 7 | +0.2074 |
| rsi malkan_40_60 1d | all | short | 4 | -0.3379 |
| rsi rsi_ma_events 15m | all | all | 1556 | -0.0846 |
| rsi rsi_ma_events 15m | all | top5_removed | 1541 | -0.1044 |
| rsi rsi_ma_events 15m | 2022 | year | 718 | -0.0035 |
| rsi rsi_ma_events 15m | 2023 | year | 510 | -0.1135 |
| rsi rsi_ma_events 15m | 2024 | year | 328 | -0.2174 |
| rsi rsi_ma_events 15m | 2022 | long | 371 | -0.0136 |
| rsi rsi_ma_events 15m | 2022 | short | 347 | +0.0074 |
| rsi rsi_ma_events 15m | 2023 | long | 251 | -0.0359 |
| rsi rsi_ma_events 15m | 2023 | short | 259 | -0.1887 |
| rsi rsi_ma_events 15m | 2024 | long | 162 | -0.2085 |
| rsi rsi_ma_events 15m | 2024 | short | 166 | -0.2262 |
| rsi rsi_ma_events 15m | all | long | 784 | -0.0610 |
| rsi rsi_ma_events 15m | all | short | 772 | -0.1086 |
| rsi rsi_ma_events 1h | all | all | 648 | -0.0360 |
| rsi rsi_ma_events 1h | all | top5_removed | 637 | -0.0703 |
| rsi rsi_ma_events 1h | 2022 | year | 281 | -0.0274 |
| rsi rsi_ma_events 1h | 2023 | year | 223 | -0.1394 |
| rsi rsi_ma_events 1h | 2024 | year | 144 | +0.1072 |
| rsi rsi_ma_events 1h | 2022 | long | 139 | -0.0792 |
| rsi rsi_ma_events 1h | 2022 | short | 142 | +0.0233 |
| rsi rsi_ma_events 1h | 2023 | long | 90 | -0.0491 |
| rsi rsi_ma_events 1h | 2023 | short | 133 | -0.2004 |
| rsi rsi_ma_events 1h | 2024 | long | 65 | +0.3080 |
| rsi rsi_ma_events 1h | 2024 | short | 79 | -0.0579 |
| rsi rsi_ma_events 1h | all | long | 294 | +0.0156 |
| rsi rsi_ma_events 1h | all | short | 354 | -0.0789 |
| rsi rsi_ma_events 4h | all | all | 135 | +0.1201 |
| rsi rsi_ma_events 4h | all | top5_removed | 129 | +0.0350 |
| rsi rsi_ma_events 4h | 2022 | year | 48 | +0.2979 |
| rsi rsi_ma_events 4h | 2023 | year | 56 | -0.0106 |
| rsi rsi_ma_events 4h | 2024 | year | 31 | +0.0808 |
| rsi rsi_ma_events 4h | 2022 | long | 25 | +0.3643 |
| rsi rsi_ma_events 4h | 2022 | short | 23 | +0.2258 |
| rsi rsi_ma_events 4h | 2023 | long | 32 | -0.1465 |
| rsi rsi_ma_events 4h | 2023 | short | 24 | +0.1705 |
| rsi rsi_ma_events 4h | 2024 | long | 23 | -0.0388 |
| rsi rsi_ma_events 4h | 2024 | short | 8 | +0.4248 |
| rsi rsi_ma_events 4h | all | long | 80 | +0.0441 |
| rsi rsi_ma_events 4h | all | short | 55 | +0.2306 |

