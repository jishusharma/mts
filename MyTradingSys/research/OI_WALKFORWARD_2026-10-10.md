# OI Divergence Walk-Forward - 2026-10-10

Method: 15-minute bars built from 1m klines. OI from Binance metrics 5-min snapshots (sum_open_interest).
Taker buy/sell ratio from kline taker_buy_volume / volume.

Signal short: 1h price change > +0.25% AND 1h OI change < 0 AND taker_buy_ratio < 0.5
Signal long:  1h price change < -0.25% AND 1h OI change > 0 AND taker_buy_ratio > 0.5
Horizons: 4, 8, 16 bars of 15m = 1h, 2h, 4h.
Split: first 60% of events train, rest test.

Events: 2350 total, 1410 train, 940 test

## TRAIN

| signal | horizon | n | mean pct | sd |
|---|---|---|---|---|
| long | 4 | 649 | -0.0240 | 0.6114 |
| long | 8 | 649 | -0.0412 | 0.8740 |
| long | 16 | 649 | -0.0573 | 1.2242 |
| short | 4 | 761 | +0.0333 | 0.5770 |
| short | 8 | 761 | +0.0429 | 0.7221 |
| short | 16 | 761 | +0.0746 | 1.0415 |

## TEST

| signal | horizon | n | mean pct | sd |
|---|---|---|---|---|
| long | 4 | 422 | -0.0303 | 0.5043 |
| long | 8 | 422 | +0.0179 | 0.6652 |
| long | 16 | 422 | +0.0308 | 0.8539 |
| short | 4 | 518 | -0.0039 | 0.4634 |
| short | 8 | 518 | -0.0049 | 0.6422 |
| short | 16 | 518 | -0.0781 | 0.8198 |

