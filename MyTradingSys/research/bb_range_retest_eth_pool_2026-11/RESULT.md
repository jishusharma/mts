Regime mix: POOL 260 weeks DEV: bull 36 (14%) | bear 0 (0%) | range 224 (86%) | n/a 0 (0%) (BTCUSDT bull 19% / range 81%; ETHUSDT bull 8% / range 92%)
Verdict: INCONCLUSIVE (underpowered), not FAIL: pooling BTC + ETH doubles the days (300-385 symbol-days per cell) but prereg_gate still BLOCKs all 9 pooled family cells (BLOCKED.md: 600-1944 needed). 0 of 9 cells survive (dev_survivors.json is []); every pooled cell has net below zero at 0.14 % (-0.044 to -0.156 % per trade), lowest Holm p 0.19. VALIDATION and HOLDOUT not read. Says nothing about other exits, band settings, maker cost, a bear regime (none in DEV) or the trader's discretionary read.

# bb_range_retest_eth_pool_2026-11 result (DEV 2022-01-01..2024-06-30, USD-M futures 1m, PRE_REG.md frozen first)

Same frozen level arm as bb_range_retest_2026-11-04 (no retuning). ETH adds the same picture as BTC: gross about +0.02 to +0.15 %, net
negative after 0.14 %, CIs about +-0.14 % wide pooled. ETH ny is the only cell with net >= 0 (k 0.5: +0.011 % [-0.197, +0.219], n 241),
one of 27 per-symbol cells and far from significant (Holm p 1.0).

## BTC reproduction row (futures vs the shipped spot run; tolerance n within 25 %, same sign)

| cell (range, tagged) | shipped spot n / net % | this run futures n / net % |
|---|---|---|
| asia 0.25 / 0.5 / 1.0 | 225 / 235 / 244; -0.094 / -0.105 / -0.132 | 222 / 232 / 241; -0.087 / -0.093 / -0.121 |
| london 0.25 / 0.5 / 1.0 | 175 / 180 / 186; -0.133 / -0.175 / -0.201 | 174 / 179 / 185; -0.126 / -0.168 / -0.195 |
| ny 0.25 / 0.5 / 1.0 | 215 / 224 / 233; -0.118 / -0.083 / -0.073 | 209 / 217 / 226; -0.127 / -0.105 / -0.091 |

n within 3 % in every cell, every sign the same (test_btc_row_reproduces_shipped_n passes); the BTC regime mix is identical (130 weeks, bull 25 / range 105).

## Confirmatory family: POOL (15m, range gate, tagged, sides pooled; cluster = symbol-day; Holm m = 9)

| session | k | n | days | fill | gross % | net % at 0.14 [95 % CI] | net % at 0.10 [95 % CI] | target hit | Holm p | vs all-regime t |
|---|---|---|---|---|---|---|---|---|---|---|
| asia | 0.25 | 472 | 363 | 63 % | +0.070 | -0.070 [-0.200, +0.060] | -0.030 [-0.160, +0.100] | 18 % | 1.00 | -0.8 |
| asia | 0.5 | 495 | 376 | 66 % | +0.058 | -0.082 [-0.206, +0.043] | -0.042 [-0.166, +0.083] | 19 % | 0.99 | -1.2 |
| asia | 1.0 | 512 | 385 | 69 % | +0.050 | -0.090 [-0.211, +0.030] | -0.050 [-0.171, +0.070] | 18 % | 0.86 | -1.1 |
| london | 0.25 | 351 | 300 | 64 % | +0.026 | -0.114 [-0.260, +0.031] | -0.074 [-0.220, +0.071] | 29 % | 0.86 | 0.6 |
| london | 0.5 | 364 | 310 | 66 % | -0.005 | -0.145 [-0.281, -0.009] | -0.105 [-0.241, +0.031] | 29 % | 0.29 | 1.2 |
| london | 1.0 | 374 | 317 | 68 % | -0.016 | -0.156 [-0.288, -0.024] | -0.116 [-0.248, +0.016] | 29 % | 0.19 | 1.3 |
| ny | 0.25 | 439 | 339 | 59 % | +0.072 | -0.068 [-0.213, +0.078] | -0.028 [-0.173, +0.118] | 18 % | 1.00 | 1.0 |
| ny | 0.5 | 458 | 352 | 61 % | +0.096 | -0.044 [-0.185, +0.097] | -0.004 [-0.145, +0.137] | 19 % | 1.00 | 0.7 |
| ny | 1.0 | 472 | 361 | 63 % | +0.084 | -0.056 [-0.196, +0.084] | -0.016 [-0.156, +0.124] | 19 % | 1.00 | 0.2 |

## Per symbol (descriptive; same cells, Holm m = 9 each; dev_cells.csv)

| symbol | net % at 0.14 range over 9 cells | days per cell | lowest Holm p | all sessions k 0.5: n, net [CI] |
|---|---|---|---|---|
| BTCUSDT | -0.087 to -0.195 | 145-184 | 0.21 | 771, -0.109 [-0.197, -0.022] |
| ETHUSDT | -0.122 to +0.011 | 155-201 | 1.00 | 865, -0.115 [-0.214, -0.015] |
| POOL | -0.044 to -0.156 | 300-385 | 0.19 | 1636, -0.112 [-0.179, -0.045] |

- Pooled all sessions (k 0.5): net -0.112 % [-0.179, -0.045] at 0.14 and -0.072 % [-0.139, -0.005] at 0.10: below zero at both costs.
- The range gate does nothing measurable (pooled vs all-regime t -1.2 to 1.3); the session-range tag does nothing (vs untagged t -0.1 to 1.1).
- A pooled gross edge of about +0.10 to +0.14 % per trade is still not excluded in the asia/ny cells, so this stays INCONCLUSIVE, not a disproof.

Parameter labels: BB(20,2), M = 10, N = 10, k grid {0.25, 0.5, 1.0}, ATR(14), stop 0.5 x distance, 24-bar time-out, session-range tag, symbol-day cluster, spot-1d context source, REPRO_N_TOL 25 % all OURS; range band 60/40 SOURCED Malkan, SMA200 SOURCED-in-repo; cost 0.14 % SOURCED research_kit, 0.10 % SOURCED fees.py (2 x BINANCE_TAKER).

Files: PRE_REG.md, BLOCKED.md, counts.csv, dev_cells.csv (symbol x gate x tag x side x session x k), dev_survivors.json, regime_mix_count.txt, regime_mix_dev.txt, study.py, test_pool.py (4 tests; all 4 failed on the stub, now 4 pass). Data: F:/MTS/data/tom_raw/klines USD-M futures 1m, loaded only to 2024-07-01.
