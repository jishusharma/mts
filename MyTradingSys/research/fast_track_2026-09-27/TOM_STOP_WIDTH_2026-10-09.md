# TOM stop width vs fees (B146), 2026-10-09

Rows: F:\MTS\data\tom_bt_2026-10-07 (holdout 2026-06-26.. excluded, burned per B147). Bars: F:\MTS\data\tom_raw\klines. Signal variants are SENSITIVITY (watch_episode = WATCH or SETUP_FORMING, p4_episode = proof>=4); the live rule has 0 signals.
Fees: DERIBIT = maker entry/target 0, taker stop/timeout 5 bp; ALL_TAKER = 5 bp every leg. R = |entry - stop|. Trials registered here: 2 variants x 2 fee profiles x 4 buckets + 6 admission cuts (all printed, none dropped).

## watch_episode / DERIBIT: 2699 filled trades

### By stop width

| bucket | period | gross R | net R | fee R |
|---|---|---|---|---|
| <0.10% | hist | n=1238 mean -0.139 med -1.000 | n=1238 mean -3.971 med -1.980 | n=1238 mean +3.832 med +1.053 |
| <0.10% | dev | n=309 mean -0.317 med -1.000 | n=309 mean -7.954 med -2.125 | n=309 mean +7.636 med +1.210 |
| 0.10-0.20% | hist | n=544 mean -0.083 med -1.000 | n=544 mean -0.445 med -1.331 | n=544 mean +0.362 med +0.369 |
| 0.10-0.20% | dev | n=131 mean -0.308 med -1.000 | n=131 mean -0.675 med -1.336 | n=131 mean +0.366 med +0.376 |
| 0.20-0.40% | hist | n=284 mean -0.213 med -1.000 | n=284 mean -0.393 med -1.156 | n=284 mean +0.181 med +0.186 |
| 0.20-0.40% | dev | n=54 mean -0.077 med -1.000 | n=54 mean -0.265 med -1.159 | n=54 mean +0.188 med +0.186 |
| >=0.40% | hist | n=113 mean -0.142 med -1.000 | n=113 mean -0.223 med -1.021 | n=113 mean +0.081 med +0.091 |
| >=0.40% | dev | n=26 mean -0.384 med -0.362 | n=26 mean -0.471 med -0.451 | n=26 mean +0.087 med +0.091 |

### Fee-to-stop admission (round trip taker fee / stop distance <= cut)

| cut | period | admitted | net R |
|---|---|---|---|
| none | hist | 2179 | n=2179 mean -2.430 med -1.512 |
| none | dev | 520 | n=520 mean -4.947 med -1.521 |
| 0.5 | hist | 397 | n=397 mean -0.345 med -1.116 |
| 0.5 | dev | 80 | n=80 mean -0.332 med -1.064 |
| 0.3 | hist | 161 | n=161 mean -0.289 med -1.057 |
| 0.3 | dev | 34 | n=34 mean -0.330 med -0.444 |
| 0.2 | hist | 67 | n=67 mean -0.148 med -0.461 |
| 0.2 | dev | 17 | n=17 mean -0.371 med -0.443 |
| 0.1 | hist | 15 | n=15 mean -0.279 med -0.199 |
| 0.1 | dev | 2 | n=2 mean +0.029 med +0.029 |
| 0.05 | hist | 2 | n=2 mean -0.527 med -0.527 |
| 0.05 | dev | 0 | n=0 |

## watch_episode / ALL_TAKER: 2699 filled trades

### By stop width

| bucket | period | gross R | net R | fee R |
|---|---|---|---|---|
| <0.10% | hist | n=1238 mean -0.139 med -1.000 | n=1238 mean -7.848 med -2.960 | n=1238 mean +7.709 med +2.133 |
| <0.10% | dev | n=309 mean -0.317 med -1.000 | n=309 mean -15.613 med -3.249 | n=309 mean +15.295 med +2.424 |
| 0.10-0.20% | hist | n=544 mean -0.083 med -1.000 | n=544 mean -0.830 med -1.663 | n=544 mean +0.747 med +0.747 |
| 0.10-0.20% | dev | n=131 mean -0.308 med -1.000 | n=131 mean -1.055 med -1.671 | n=131 mean +0.747 med +0.752 |
| 0.20-0.40% | hist | n=284 mean -0.213 med -1.000 | n=284 mean -0.593 med -1.313 | n=284 mean +0.380 med +0.390 |
| 0.20-0.40% | dev | n=54 mean -0.077 med -1.000 | n=54 mean -0.453 med -1.318 | n=54 mean +0.375 med +0.372 |
| >=0.40% | hist | n=113 mean -0.142 med -1.000 | n=113 mean -0.316 med -1.042 | n=113 mean +0.174 med +0.191 |
| >=0.40% | dev | n=26 mean -0.384 med -0.362 | n=26 mean -0.558 med -0.562 | n=26 mean +0.174 med +0.183 |

### Fee-to-stop admission (round trip taker fee / stop distance <= cut)

| cut | period | admitted | net R |
|---|---|---|---|
| none | hist | 2179 | n=2179 mean -4.759 med -2.024 |
| none | dev | 520 | n=520 mean -9.618 med -2.049 |
| 0.5 | hist | 397 | n=397 mean -0.514 med -1.232 |
| 0.5 | dev | 80 | n=80 mean -0.487 med -1.129 |
| 0.3 | hist | 161 | n=161 mean -0.398 med -1.115 |
| 0.3 | dev | 34 | n=34 mean -0.428 med -0.533 |
| 0.2 | hist | 67 | n=67 mean -0.223 med -0.517 |
| 0.2 | dev | 17 | n=17 mean -0.446 med -0.509 |
| 0.1 | hist | 15 | n=15 mean -0.316 med -0.244 |
| 0.1 | dev | 2 | n=2 mean -0.011 med -0.011 |
| 0.05 | hist | 2 | n=2 mean -0.547 med -0.547 |
| 0.05 | dev | 0 | n=0 |

## p4_episode / DERIBIT: 59 filled trades

### By stop width

| bucket | period | gross R | net R | fee R |
|---|---|---|---|---|
| <0.10% | hist | n=24 mean -1.000 med -1.000 | n=24 mean -5.134 med -2.248 | n=24 mean +4.134 med +1.248 |
| <0.10% | dev | n=8 mean +0.720 med -1.000 | n=8 mean -0.738 med -1.646 | n=8 mean +1.458 med +0.704 |
| 0.10-0.20% | hist | n=11 mean -1.000 med -1.000 | n=11 mean -1.357 med -1.329 | n=11 mean +0.357 med +0.329 |
| 0.10-0.20% | dev | n=7 mean +0.152 med -1.000 | n=7 mean -0.186 med -1.319 | n=7 mean +0.339 med +0.342 |
| 0.20-0.40% | hist | n=4 mean -0.492 med -1.000 | n=4 mean -0.718 med -1.224 | n=4 mean +0.226 med +0.224 |
| 0.20-0.40% | dev | n=3 mean -1.000 med -1.000 | n=3 mean -1.190 med -1.180 | n=3 mean +0.190 med +0.180 |
| >=0.40% | hist | n=2 mean -0.495 med -0.495 | n=2 mean -0.560 med -0.560 | n=2 mean +0.065 med +0.065 |
| >=0.40% | dev | n=0 | n=0 | n=0 |

### Fee-to-stop admission (round trip taker fee / stop distance <= cut)

| cut | period | admitted | net R |
|---|---|---|---|
| none | hist | 41 | n=41 mean -3.467 med -1.581 |
| none | dev | 18 | n=18 mean -0.599 med -1.333 |
| 0.5 | hist | 6 | n=6 mean -0.665 med -1.132 |
| 0.5 | dev | 3 | n=3 mean -1.190 med -1.180 |
| 0.3 | hist | 2 | n=2 mean -0.560 med -0.560 |
| 0.3 | dev | 0 | n=0 |
| 0.2 | hist | 2 | n=2 mean -0.560 med -0.560 |
| 0.2 | dev | 0 | n=0 |
| 0.1 | hist | 1 | n=1 mean -1.048 med -1.048 |
| 0.1 | dev | 0 | n=0 |
| 0.05 | hist | 0 | n=0 |
| 0.05 | dev | 0 | n=0 |

## p4_episode / ALL_TAKER: 59 filled trades

### By stop width

| bucket | period | gross R | net R | fee R |
|---|---|---|---|---|
| <0.10% | hist | n=24 mean -1.000 med -1.000 | n=24 mean -9.268 med -3.496 | n=24 mean +8.268 med +2.496 |
| <0.10% | dev | n=8 mean +0.720 med -1.000 | n=8 mean -2.195 med -2.291 | n=8 mean +2.915 med +1.408 |
| 0.10-0.20% | hist | n=11 mean -1.000 med -1.000 | n=11 mean -1.714 med -1.658 | n=11 mean +0.714 med +0.658 |
| 0.10-0.20% | dev | n=7 mean +0.152 med -1.000 | n=7 mean -0.524 med -1.638 | n=7 mean +0.677 med +0.682 |
| 0.20-0.40% | hist | n=4 mean -0.492 med -1.000 | n=4 mean -0.944 med -1.448 | n=4 mean +0.452 med +0.448 |
| 0.20-0.40% | dev | n=3 mean -1.000 med -1.000 | n=3 mean -1.381 med -1.360 | n=3 mean +0.381 med +0.360 |
| >=0.40% | hist | n=2 mean -0.495 med -0.495 | n=2 mean -0.624 med -0.624 | n=2 mean +0.129 med +0.129 |
| >=0.40% | dev | n=0 | n=0 | n=0 |

### Fee-to-stop admission (round trip taker fee / stop distance <= cut)

| cut | period | admitted | net R |
|---|---|---|---|
| none | hist | 41 | n=41 mean -6.008 med -2.163 |
| none | dev | 18 | n=18 mean -1.410 med -1.665 |
| 0.5 | hist | 6 | n=6 mean -0.837 med -1.264 |
| 0.5 | dev | 3 | n=3 mean -1.381 med -1.360 |
| 0.3 | hist | 2 | n=2 mean -0.624 med -0.624 |
| 0.3 | dev | 0 | n=0 |
| 0.2 | hist | 2 | n=2 mean -0.624 med -0.624 |
| 0.2 | dev | 0 | n=0 |
| 0.1 | hist | 1 | n=1 mean -1.096 med -1.096 |
| 0.1 | dev | 0 | n=0 |
| 0.05 | hist | 0 | n=0 |
| 0.05 | dev | 0 | n=0 |


## Conclusion (B146, 2026-10-09)
- Stops under 0.10 % of price are 57 % of filled trades (1238 + 309 of 2699, watch_episode) and cost 3.8 R (hist) to 7.6 R (dev) of fees per trade at Deribit maker/taker, double at all-taker. Net -4.0 R / -8.0 R.
- Gross R is negative in EVERY bucket (-0.08 to -0.38): wider stops do not create an edge, they only shrink the fee drag (fee R 0.36 at 0.10-0.20 %, 0.18 at 0.20-0.40 %, 0.08 at >= 0.40 %). Median trade is a stop-out at -1.0 R.
- A fee-to-stop admission cut of 0.3 R keeps 161 hist / 34 dev trades with net -0.29 / -0.33 R: damage limited, still negative, so it fails the PLAN section 4 rule (needs net > 0 in both splits). It is protective, not a source of edge.
- Staged: auto_trader `tom.max_fee_to_stop` (default OFF; fail closed on a bad value) + test_b146_fee_to_stop. Recommended value if the operator wants it: 0.3 (BT-TUNED, this file). Not enabled: it needs the operator decision on net_rr floor / pausing Tom.
- Holdout not read. Deribit maker 0 / taker 5 bp is the API-verified 2026-09-26 assumption (fees.py).
