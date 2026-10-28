# OI Divergence v2 - Pre-registered - 2026-10-10

Pre-registration: research/_archive/loose_2026-10/PRE_REG_OI_DIVERGENCE_2026-10-10.md
Costs: fees 10 bps RT, slippage 2 bps RT, funding from records.
Folds: full / first-two-thirds / last-third. Embargo 96 bars at each boundary.
Cells reported: 24. Bonferroni divisor: 24.

Events: 2350

## Pooled (all events)

| signal | horizon | n | mean net % | t |
|---|---|---|---|---|
| long | 4 | 1071 | -0.1468 | -8.40 |
| long | 8 | 1071 | -0.1387 | -5.68 |
| long | 16 | 1071 | -0.1441 | -4.31 |
| short | 4 | 1279 | -0.1380 | -9.24 |
| short | 8 | 1279 | -0.1429 | -7.39 |
| short | 16 | 1279 | -0.1315 | -4.89 |

## Per regime, full window

| signal | horizon | regime | n | mean net % | t |
|---|---|---|---|---|---|
| long | 4 | trend_up | 157 | -0.0887 | -2.86 |
| long | 4 | trend_down | 775 | -0.1547 | -7.35 |
| long | 4 | range | 139 | -0.1684 | -3.03 |
| long | 8 | trend_up | 157 | -0.0802 | -1.71 |
| long | 8 | trend_down | 775 | -0.1541 | -5.22 |
| long | 8 | range | 139 | -0.1188 | -1.61 |
| long | 16 | trend_up | 157 | -0.0807 | -1.28 |
| long | 16 | trend_down | 775 | -0.1810 | -4.46 |
| long | 16 | range | 139 | -0.0096 | -0.10 |
| short | 4 | trend_up | 266 | -0.1460 | -5.53 |
| short | 4 | trend_down | 812 | -0.1485 | -7.80 |
| short | 4 | range | 201 | -0.0851 | -1.96 |
| short | 8 | trend_up | 266 | -0.1018 | -3.08 |
| short | 8 | trend_down | 812 | -0.1491 | -5.90 |
| short | 8 | range | 201 | -0.1722 | -3.26 |
| short | 16 | trend_up | 266 | -0.0527 | -1.00 |
| short | 16 | trend_down | 812 | -0.1513 | -4.47 |
| short | 16 | range | 201 | -0.1559 | -2.07 |

## Walk-forward (3 folds, test only)

| fold | train range | test range | signal | horizon | train mean | test mean | test n | test t |
|---|---|---|---|---|---|---|---|---|
| 2 | 0-1566 | rest | long | 4 | -0.1457 | -0.1492 | 343 | -5.14 |
| 2 | 0-1566 | rest | long | 8 | -0.1639 | -0.0850 | 343 | -2.22 |
| 2 | 0-1566 | rest | long | 16 | -0.1656 | -0.0984 | 343 | -2.04 |
| 2 | 0-1566 | rest | short | 4 | -0.1480 | -0.1190 | 441 | -5.23 |
| 2 | 0-1566 | rest | short | 8 | -0.1601 | -0.1103 | 441 | -3.55 |
| 2 | 0-1566 | rest | short | 16 | -0.2017 | +0.0020 | 441 | +0.05 |

