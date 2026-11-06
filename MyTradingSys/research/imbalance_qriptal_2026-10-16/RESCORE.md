# RESCORE: Habib imbalance fade 10-16 with plan stops and maker fees (card fee-stop-rescore-fabio-habib-1106)

**Verdict: cost killed the old result; a wider plan stop cuts the fee drag but gross stays about 0, so net stays negative.** Wider stops (PLAN1 +0.5 range, PLAN2 +1.0 range beyond the candle extreme; both OURS, no stop rule of his is public) lift 30m/1h net from about -0.28 to -0.13 R (taker) or -0.06..-0.09 R (maker-in), never above 0 with n >= 30. Only 1d (n 16 design, 2 check) and 4h 2R check (n 53, design negative) are >= 0, too small or inconsistent.

Method: `rescore_habib.py` re-runs imb.py's imb_small events (k = 2, next-bar-open entry, 24-bar hold, 1R and 2R targets, Binance USDT-M 1m, design 2022-01..2025-09, check 2025-09..2026-06-25; holdout not read) with the old stop and two plan stops. Costs from fees.py via fabio/rescore.py (Deribit taker 5 bp, maker 0; the 10-16 study used 5 bp taker, same). Regime A: taker in, taker exits. Regime B: maker entry at the next open (OPTIMISTIC: fill assumed, no queue risk), target maker, stop/time taker. Net R = gross R - fee x entry / risk. Check: OLD net A reproduces BACKTEST.md (30m 2R design -0.287 / check -0.443; 1h -0.278 / -0.092). Exposure: same windows as the 10-16 study, so no clean OOS (see README section 6).

Columns: n, gross R, net R regime A (taker), net R regime B (maker in), median stop bp. 'old' = candle's own extreme.

## design

| tf | target | stop | n | gross R | net A | net B | median stop bp |
|---|---|---|---|---|---|---|---|
| 30m | 1R | old | 2011 | -0.018 | -0.279 | -0.087 | 51 |
| 30m | 1R | PLAN1 | 2011 | -0.036 | -0.170 | -0.073 | 88 |
| 30m | 1R | PLAN2 | 2011 | -0.031 | -0.125 | -0.061 | 127 |
| 30m | 2R | old | 2011 | -0.027 | -0.287 | -0.118 | 51 |
| 30m | 2R | PLAN1 | 2011 | -0.071 | -0.205 | -0.124 | 88 |
| 30m | 2R | PLAN2 | 2011 | -0.042 | -0.135 | -0.082 | 127 |
| 1h | 1R | old | 1013 | -0.069 | -0.251 | -0.114 | 73 |
| 1h | 1R | PLAN1 | 1013 | -0.094 | -0.185 | -0.122 | 127 |
| 1h | 1R | PLAN2 | 1013 | -0.055 | -0.118 | -0.075 | 180 |
| 1h | 2R | old | 1013 | -0.096 | -0.278 | -0.158 | 73 |
| 1h | 2R | PLAN1 | 1013 | -0.110 | -0.201 | -0.147 | 127 |
| 1h | 2R | PLAN2 | 1013 | -0.062 | -0.125 | -0.089 | 180 |
| 4h | 1R | old | 197 | -0.019 | -0.104 | -0.042 | 144 |
| 4h | 1R | PLAN1 | 197 | -0.049 | -0.091 | -0.061 | 262 |
| 4h | 1R | PLAN2 | 197 | -0.037 | -0.066 | -0.047 | 376 |
| 4h | 2R | old | 197 | +0.020 | -0.065 | -0.010 | 144 |
| 4h | 2R | PLAN1 | 197 | +0.015 | -0.027 | -0.001 | 262 |
| 4h | 2R | PLAN2 | 197 | +0.008 | -0.021 | -0.004 | 376 |
| 12h | 1R | old | 38 | -0.105 | -0.149 | -0.115 | 281 |
| 12h | 1R | PLAN1 | 38 | -0.278 | -0.298 | -0.285 | 517 |
| 12h | 1R | PLAN2 | 38 | -0.211 | -0.225 | -0.216 | 749 |
| 12h | 2R | old | 38 | -0.132 | -0.175 | -0.146 | 281 |
| 12h | 2R | PLAN1 | 38 | -0.319 | -0.339 | -0.328 | 517 |
| 12h | 2R | PLAN2 | 38 | -0.282 | -0.296 | -0.289 | 749 |
| 1d | 1R | old | 16 | +0.125 | +0.103 | +0.120 | 590 |
| 1d | 1R | PLAN1 | 16 | +0.206 | +0.195 | +0.203 | 1075 |
| 1d | 1R | PLAN2 | 16 | +0.119 | +0.111 | +0.116 | 1492 |
| 1d | 2R | old | 16 | +0.240 | +0.218 | +0.233 | 590 |
| 1d | 2R | PLAN1 | 16 | +0.182 | +0.171 | +0.178 | 1075 |
| 1d | 2R | PLAN2 | 16 | +0.211 | +0.204 | +0.208 | 1492 |

## check

| tf | target | stop | n | gross R | net A | net B | median stop bp |
|---|---|---|---|---|---|---|---|
| 30m | 1R | old | 375 | +0.002 | -0.375 | -0.084 | 44 |
| 30m | 1R | PLAN1 | 375 | -0.055 | -0.215 | -0.100 | 78 |
| 30m | 1R | PLAN2 | 375 | -0.058 | -0.167 | -0.092 | 112 |
| 30m | 2R | old | 375 | -0.066 | -0.443 | -0.183 | 44 |
| 30m | 2R | PLAN1 | 375 | -0.114 | -0.274 | -0.177 | 78 |
| 30m | 2R | PLAN2 | 375 | -0.048 | -0.157 | -0.092 | 112 |
| 1h | 1R | old | 219 | +0.097 | -0.130 | +0.048 | 56 |
| 1h | 1R | PLAN1 | 219 | -0.035 | -0.143 | -0.064 | 106 |
| 1h | 1R | PLAN2 | 219 | -0.013 | -0.086 | -0.035 | 155 |
| 1h | 2R | old | 219 | +0.136 | -0.092 | +0.065 | 56 |
| 1h | 2R | PLAN1 | 219 | -0.073 | -0.182 | -0.116 | 106 |
| 1h | 2R | PLAN2 | 219 | +0.019 | -0.055 | -0.011 | 155 |
| 4h | 1R | old | 53 | -0.023 | -0.113 | -0.045 | 122 |
| 4h | 1R | PLAN1 | 53 | -0.003 | -0.048 | -0.015 | 228 |
| 4h | 1R | PLAN2 | 53 | -0.030 | -0.061 | -0.040 | 320 |
| 4h | 2R | old | 53 | +0.094 | +0.004 | +0.066 | 122 |
| 4h | 2R | PLAN1 | 53 | -0.166 | -0.211 | -0.184 | 228 |
| 4h | 2R | PLAN2 | 53 | -0.034 | -0.065 | -0.048 | 320 |
| 12h | 1R | old | 7 | -0.714 | -0.760 | -0.735 | 247 |
| 12h | 1R | PLAN1 | 7 | -0.429 | -0.453 | -0.438 | 410 |
| 12h | 1R | PLAN2 | 7 | -0.262 | -0.279 | -0.268 | 569 |
| 12h | 2R | old | 7 | -0.571 | -0.617 | -0.592 | 247 |
| 12h | 2R | PLAN1 | 7 | -0.292 | -0.317 | -0.303 | 410 |
| 12h | 2R | PLAN2 | 7 | -0.169 | -0.186 | -0.176 | 569 |
| 1d | 1R | old | 2 | +0.000 | -0.022 | -0.006 | 460 |
| 1d | 1R | PLAN1 | 2 | +0.000 | -0.013 | -0.004 | 795 |
| 1d | 1R | PLAN2 | 2 | -0.307 | -0.317 | -0.312 | 1130 |
| 1d | 2R | old | 2 | +0.500 | +0.478 | +0.494 | 460 |
| 1d | 2R | PLAN1 | 2 | -0.418 | -0.431 | -0.425 | 795 |
| 1d | 2R | PLAN2 | 2 | -0.307 | -0.317 | -0.312 | 1130 |

Reading: the fee is 0.26 R at the old 51 bp 30m stop and 0.13 R at PLAN1 / 0.09 R at PLAN2, so wider stops help net R while gross R stays at -0.07..0. A wider stop alone does not create an edge (matches README section 6). No setup is net positive with n >= 30 in both windows, so no testnet watch card (Next: END).
