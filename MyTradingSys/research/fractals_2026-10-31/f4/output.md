# F4 output (BTCUSDT spot 8h from 1h; 2017-08-17 08:00:00 .. 2025-06-30 16:00:00; 8584 bars, 5705 valid)

RULE raw events 36; ANALOG queries 306 (answered 104)

| set | h (bars) | n | hit | net R/trade | net %/trade | month-boot 95% CI | half A / B | B1 mean (p, Holm p) | B2 mean (p) | sd R | n for 0.10 R | POST-HOC net-% control mean (p) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RULE-cont | 3 | 36 | 0.472 | +0.109 | +1.080 | [-0.181, +0.423] | +0.294 / -0.076 | -4.974 (0.041, 0.373) | -0.078 (0.160) | 0.84 | 549 | -0.125 (0.000) | INCONCLUSIVE |
| RULE-fade | 3 | 36 | 0.306 | -0.475 | -0.104 | [-0.826, -0.060] | -0.404 / -0.546 | -5.647 (0.828, 1.000) | -0.363 (0.683) | 1.31 | 1340 | -0.066 (0.545) | FAIL |
| ANALOG | 3 | 33 | 0.424 | +0.020 | +0.055 | [-0.421, +0.388] | +0.018 / +0.022 | -5.298 (0.126, 1.000) | -0.307 (0.089) | 1.32 | 1360 | -0.077 (0.295) | INCONCLUSIVE |
| RULE-cont | 6 | 36 | 0.417 | -0.115 | +0.068 | [-0.425, +0.200] | +0.078 / -0.309 | -4.974 (0.212, 1.000) | -0.094 (0.523) | 0.89 | 625 | -0.126 (0.246) | INCONCLUSIVE |
| RULE-fade | 6 | 36 | 0.250 | -0.506 | -0.171 | [-0.870, -0.080] | -0.443 / -0.568 | -5.647 (0.846, 1.000) | -0.393 (0.683) | 1.32 | 1361 | -0.053 (0.634) | FAIL |
| ANALOG | 6 | 28 | 0.321 | -0.560 | -0.625 | [-1.228, +0.066] | -0.674 / -0.447 | -5.985 (0.828, 1.000) | -0.361 (0.759) | 1.70 | 2269 | -0.047 (0.973) | NOT_DECIDABLE |
| RULE-cont | 9 | 36 | 0.306 | -0.138 | +0.223 | [-0.477, +0.215] | +0.214 / -0.490 | -4.974 (0.240, 1.000) | -0.092 (0.567) | 1.08 | 921 | -0.129 (0.138) | INCONCLUSIVE |
| RULE-fade | 9 | 36 | 0.278 | -0.471 | -0.143 | [-0.843, -0.029] | -0.447 / -0.495 | -5.643 (0.814, 1.000) | -0.373 (0.654) | 1.43 | 1600 | -0.041 (0.601) | FAIL |
| ANALOG | 9 | 29 | 0.310 | -0.504 | -0.413 | [-1.266, +0.182] | +0.040 / -1.011 | -6.497 (0.790, 1.000) | -0.355 (0.702) | 1.74 | 2381 | -0.028 (0.884) | NOT_DECIDABLE |

## Phase splits (h = 6, descriptive)

### RULE-cont (n 36, mean -0.115 R)

| labelling | cell | n | mean net R | gap vs pooled |
|---|---|---|---|---|
| cowen|sma200 | above|above | 17 | -0.118 | -0.003 |
| cowen|sma200 | above|below | 1 | +0.371 | +0.486 |
| cowen|sma200 | below|below | 15 | -0.306 | -0.191 |
| cowen|sma200 | inside|above | 1 | +0.033 | +0.149 |
| cowen|sma200 | FAMILY-WISE | 32 | max gap 0.100 vs thr 0.317, p 0.508 | flagged none |
| wsma10_phase | above_down | 3 | -0.696 | -0.580 |
| wsma10_phase | above_up | 15 | +0.063 | +0.178 |
| wsma10_phase | below_down | 14 | -0.348 | -0.233 |
| wsma10_phase | below_up | 4 | +0.466 | +0.582 |
| wsma10_phase | FAMILY-WISE | 29 | max gap 0.213 vs thr 0.345, p 0.166 | flagged none |
| dd_bin | deep | 17 | -0.396 | -0.280 |
| dd_bin | mid | 10 | +0.075 | +0.190 |
| dd_bin | shallow | 9 | +0.203 | +0.318 |
| dd_bin | FAMILY-WISE | 27 | max gap 0.296 vs thr 0.508, p 0.236 | flagged none |
| cycle_year | 1.0 | 9 | -0.413 | -0.298 |
| cycle_year | 2.0 | 12 | +0.284 | +0.399 |
| cycle_year | 3.0 | 6 | +0.024 | +0.139 |
| cycle_year | 4.0 | 9 | -0.443 | -0.327 |
| (layers, entries 2022+ only, n 20) | | | | |
| layer | RSI-DIV-MTF fired | 6 | -0.291 | -0.044 |
| layer | RSI-DIV-MTF not fired | 14 | -0.228 | +0.019 |
| layer | Hurst H<0.45 | 6 | -0.501 | -0.255 |
| layer | Hurst 0.45-0.55 | 12 | -0.282 | -0.035 |
| layer | Hurst H>0.55 | 2 | +0.729 | +0.976 |

### RULE-fade (n 36, mean -0.506 R)

| labelling | cell | n | mean net R | gap vs pooled |
|---|---|---|---|---|
| cowen|sma200 | above|above | 17 | -0.363 | +0.143 |
| cowen|sma200 | above|below | 1 | -1.095 | -0.589 |
| cowen|sma200 | below|below | 15 | -0.776 | -0.271 |
| cowen|sma200 | inside|above | 1 | -0.232 | +0.274 |
| cowen|sma200 | FAMILY-WISE | 32 | max gap 0.220 vs thr 0.469, p 0.416 | flagged none |
| wsma10_phase | above_down | 3 | +0.149 | +0.655 |
| wsma10_phase | above_up | 15 | +0.185 | +0.691 |
| wsma10_phase | below_down | 14 | -1.212 | -0.706 |
| wsma10_phase | below_up | 4 | -1.119 | -0.613 |
| wsma10_phase | FAMILY-WISE | 29 | max gap 0.723 vs thr 0.647, p 0.001 | flagged [np.str_('below_down')] |
| dd_bin | deep | 17 | -0.649 | -0.143 |
| dd_bin | mid | 10 | -0.718 | -0.213 |
| dd_bin | shallow | 9 | +0.001 | +0.507 |
| dd_bin | FAMILY-WISE | 27 | max gap 0.043 vs thr 0.615, p 0.956 | flagged none |
| cycle_year | 1.0 | 9 | -0.039 | +0.467 |
| cycle_year | 2.0 | 12 | -0.531 | -0.025 |
| cycle_year | 3.0 | 6 | -0.952 | -0.446 |
| cycle_year | 4.0 | 9 | -0.642 | -0.136 |
| (layers, entries 2022+ only, n 20) | | | | |
| layer | RSI-DIV-MTF fired | 6 | -1.158 | -0.537 |
| layer | RSI-DIV-MTF not fired | 14 | -0.391 | +0.230 |
| layer | Hurst H<0.45 | 6 | +0.169 | +0.790 |
| layer | Hurst 0.45-0.55 | 12 | -0.939 | -0.318 |
| layer | Hurst H>0.55 | 2 | -1.083 | -0.462 |

### ANALOG (n 28, mean -0.560 R)

| labelling | cell | n | mean net R | gap vs pooled |
|---|---|---|---|---|
| cowen|sma200 | above|above | 18 | -0.545 | +0.016 |
| cowen|sma200 | below|above | 2 | -0.434 | +0.126 |
| cowen|sma200 | below|below | 7 | -0.537 | +0.024 |
| cowen|sma200 | inside|above | 1 | -1.260 | -0.700 |
| wsma10_phase | above_down | 1 | -1.275 | -0.715 |
| wsma10_phase | above_up | 14 | -0.171 | +0.389 |
| wsma10_phase | below_down | 10 | -1.151 | -0.591 |
| wsma10_phase | below_up | 3 | -0.169 | +0.391 |
| wsma10_phase | FAMILY-WISE | 24 | max gap 0.572 vs thr 0.749, p 0.146 | flagged none |
| dd_bin | deep | 5 | -0.470 | +0.090 |
| dd_bin | mid | 7 | -0.909 | -0.348 |
| dd_bin | shallow | 16 | -0.436 | +0.124 |
| cycle_year | 1.0 | 14 | -0.960 | -0.400 |
| cycle_year | 2.0 | 3 | +0.283 | +0.844 |
| cycle_year | 4.0 | 11 | -0.282 | +0.279 |
| (layers, entries 2022+ only, n 28) | | | | |
| layer | RSI-DIV-MTF fired | 9 | -0.737 | -0.177 |
| layer | RSI-DIV-MTF not fired | 19 | -0.476 | +0.084 |
| layer | Hurst H<0.45 | 10 | -0.479 | +0.081 |
| layer | Hurst 0.45-0.55 | 16 | -0.548 | +0.012 |
| layer | Hurst H>0.55 | 2 | -1.065 | -0.504 |

