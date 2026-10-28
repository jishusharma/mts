# COUNTS: every row of COUNTS.csv (counts only, no outcome read; built by counts_only.py --m-base 56, 2026-10-28)

Rows: 45 = 30 cells (5 family x timeframe cells x 3 symbols x 2 windows) + 15 pooled rows (per cell: DEV, DEV_EXT, DEV+DEV_EXT; days = distinct UTC days across symbols). Formulas and sources: PRE_REG.md section 1.

| family | rule | timeframe | symbol | window | events | days | mean_stop_pct | cost_r | data_from | months_missing | note |
|---|---|---|---|---|---|---|---|---|---|---|---|
| krown | S5 | 4h | BTCUSDT | DEV | 55 | 55 | 5.602 | 0.0386 | 2022-01-01 | 0 |  |
| krown | S5 | 4h | BTCUSDT | DEV_EXT | 46 | 46 | 6.480 | 0.0288 | 2020-01-01 | 0 |  |
| krown | S5 | 4h | ETHUSDT | DEV | 51 | 50 | 6.743 | 0.0267 | 2022-01-01 | 0 |  |
| krown | S5 | 4h | ETHUSDT | DEV_EXT | 41 | 41 | 8.566 | 0.0216 | 2020-01-01 | 0 |  |
| krown | S5 | 4h | SOLUSDT | DEV | 58 | 55 | 9.121 | 0.0204 | 2022-01-01 | 0 |  |
| krown | S5 | 4h | SOLUSDT | DEV_EXT | 26 | 26 | 15.677 | 0.0125 | 2020-09-14 | 8 | partial: months missing upstream |
| krown | S8 | 4h | BTCUSDT | DEV | 135 | 135 | 4.254 | 0.0402 | 2022-01-01 | 0 |  |
| krown | S8 | 4h | BTCUSDT | DEV_EXT | 142 | 142 | 6.107 | 0.0273 | 2020-01-01 | 0 |  |
| krown | S8 | 4h | ETHUSDT | DEV | 142 | 141 | 5.808 | 0.0299 | 2022-01-01 | 0 |  |
| krown | S8 | 4h | ETHUSDT | DEV_EXT | 146 | 144 | 8.238 | 0.0196 | 2020-01-01 | 0 |  |
| krown | S8 | 4h | SOLUSDT | DEV | 156 | 156 | 9.017 | 0.0176 | 2022-01-01 | 0 |  |
| krown | S8 | 4h | SOLUSDT | DEV_EXT | 86 | 85 | 13.448 | 0.0115 | 2020-09-14 | 8 | partial: months missing upstream |
| malkan_rsi | rsi40_60 | 1d | BTCUSDT | DEV | 5 | 5 | 3.192 | 0.0460 | 2022-01-01 | 0 |  |
| malkan_rsi | rsi40_60 | 1d | BTCUSDT | DEV_EXT | 1 | 1 | 1.959 | 0.0715 | 2020-01-01 | 0 |  |
| malkan_rsi | rsi40_60 | 1d | ETHUSDT | DEV | 5 | 5 | 5.135 | 0.0322 | 2022-01-01 | 0 |  |
| malkan_rsi | rsi40_60 | 1d | ETHUSDT | DEV_EXT | 1 | 1 | 6.711 | 0.0209 | 2020-01-01 | 0 |  |
| malkan_rsi | rsi40_60 | 1d | SOLUSDT | DEV | 5 | 5 | 10.091 | 0.0195 | 2022-01-01 | 0 |  |
| malkan_rsi | rsi40_60 | 1d | SOLUSDT | DEV_EXT | 3 | 3 | 12.394 | 0.0114 | 2020-09-14 | 8 | partial: months missing upstream |
| malkan_rsi | rsi40_60 | 1w | BTCUSDT | DEV | 3 | 3 | 10.146 | 0.0142 | 2022-01-03 | 0 |  |
| malkan_rsi | rsi40_60 | 1w | BTCUSDT | DEV_EXT | 0 | 0 | nan | nan | 2020-01-06 | 0 |  |
| malkan_rsi | rsi40_60 | 1w | ETHUSDT | DEV | 1 | 1 | 8.836 | 0.0158 | 2022-01-03 | 0 |  |
| malkan_rsi | rsi40_60 | 1w | ETHUSDT | DEV_EXT | 0 | 0 | nan | nan | 2020-01-06 | 0 |  |
| malkan_rsi | rsi40_60 | 1w | SOLUSDT | DEV | 1 | 1 | 24.793 | 0.0056 | 2022-01-03 | 0 |  |
| malkan_rsi | rsi40_60 | 1w | SOLUSDT | DEV_EXT | 0 | 0 | nan | nan | 2020-09-14 | 8 | partial: months missing upstream |
| pitchfork | triplet | 1d | BTCUSDT | DEV | 133 | 133 | 1.500 | 0.0933 | 2022-01-01 | 0 |  |
| pitchfork | triplet | 1d | BTCUSDT | DEV_EXT | 109 | 109 | 1.500 | 0.0933 | 2020-01-01 | 0 |  |
| pitchfork | triplet | 1d | ETHUSDT | DEV | 149 | 149 | 1.500 | 0.0933 | 2022-01-01 | 0 |  |
| pitchfork | triplet | 1d | ETHUSDT | DEV_EXT | 106 | 106 | 1.500 | 0.0933 | 2020-01-01 | 0 |  |
| pitchfork | triplet | 1d | SOLUSDT | DEV | 140 | 140 | 1.500 | 0.0933 | 2022-01-01 | 0 |  |
| pitchfork | triplet | 1d | SOLUSDT | DEV_EXT | 62 | 62 | 1.500 | 0.0933 | 2020-09-14 | 8 | partial: months missing upstream |
| krown | S5 | 4h | POOLED | DEV | 164 | 129 | 7.201 | 0.0285 |  |  | m=58 z_holm=3.332 n_needed=443 NOT POWERED |
| krown | S5 | 4h | POOLED | DEV_EXT | 113 | 100 | 9.353 | 0.0224 |  |  | m=58 z_holm=3.332 n_needed=424 NOT POWERED |
| krown | S5 | 4h | POOLED | DEV+DEV_EXT | 277 | 229 | 8.079 | 0.0260 |  |  | m=58 z_holm=3.332 n_needed=435 NOT POWERED |
| krown | S8 | 4h | POOLED | DEV | 433 | 274 | 6.480 | 0.0287 |  |  | m=58 z_holm=3.332 n_needed=444 NOT POWERED |
| krown | S8 | 4h | POOLED | DEV_EXT | 374 | 265 | 8.627 | 0.0207 |  |  | m=58 z_holm=3.332 n_needed=419 NOT POWERED |
| krown | S8 | 4h | POOLED | DEV+DEV_EXT | 807 | 539 | 7.475 | 0.0250 |  |  | m=58 z_holm=3.332 n_needed=432 POWERED |
| malkan_rsi | rsi40_60 | 1d | POOLED | DEV | 15 | 15 | 6.139 | 0.0325 |  |  | m=58 z_holm=3.332 n_needed=457 NOT POWERED |
| malkan_rsi | rsi40_60 | 1d | POOLED | DEV_EXT | 5 | 5 | 9.170 | 0.0253 |  |  | m=58 z_holm=3.332 n_needed=433 NOT POWERED |
| malkan_rsi | rsi40_60 | 1d | POOLED | DEV+DEV_EXT | 20 | 20 | 6.897 | 0.0307 |  |  | m=58 z_holm=3.332 n_needed=451 NOT POWERED |
| malkan_rsi | rsi40_60 | 1w | POOLED | DEV | 5 | 5 | 12.813 | 0.0128 |  |  | m=58 z_holm=3.332 n_needed=396 NOT POWERED |
| malkan_rsi | rsi40_60 | 1w | POOLED | DEV_EXT | 0 | 0 | nan | nan |  |  | m=58 z_holm=3.332 n_needed=nan NOT POWERED |
| malkan_rsi | rsi40_60 | 1w | POOLED | DEV+DEV_EXT | 5 | 5 | 12.813 | 0.0128 |  |  | m=58 z_holm=3.332 n_needed=396 NOT POWERED |
| pitchfork | triplet | 1d | POOLED | DEV | 422 | 272 | 1.500 | 0.0933 |  |  | m=57 z_holm=3.327 n_needed=763 NOT POWERED |
| pitchfork | triplet | 1d | POOLED | DEV_EXT | 277 | 204 | 1.500 | 0.0933 |  |  | m=57 z_holm=3.327 n_needed=763 NOT POWERED |
| pitchfork | triplet | 1d | POOLED | DEV+DEV_EXT | 699 | 476 | 1.500 | 0.0933 |  |  | m=57 z_holm=3.327 n_needed=763 NOT POWERED |
