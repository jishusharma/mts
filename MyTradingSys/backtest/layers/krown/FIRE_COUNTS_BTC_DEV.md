# Krown v0 fire counts, BTCUSDT DEV only

Bars: 1d 1643 (2020-01-01 .. 2024-06-30), 1w 234. DEV 2020-01..2024-06 from local 1m files (2017-2019 NOT_IN_DATA here). VALIDATION/HOLDOUT not read. Ceiling (PRE_REG_KROWN item 3): <= 1.0 event per 10 daily bars per setup.

## 1d (1643 bars)

| detector | count |
|---|---|
| swing highs/lows (confirmed) | 323 |
| trend state: up bars | 555 |
| trend state: down bars | 300 |
| trend reversals (state flips up<->down) | 14 |
| bars with >=1 ranked zone | 1617 |
| volume >= 2x (prior-20 baseline) | 74 |
| volume >= 2x (same-slot baseline) | 94 |
| volume <= 0.5x | 144 |
| BBWP >= 85 (expansion) | 246 |
| BBWP <= 30 (compression) | 512 |
| strict bullish engulfing | 58 |
| strict bearish engulfing | 50 |
| hammer | 91 |
| shooting star | 66 |
| doji | 197 |
| three black crows | 153 |
| 21/55 EMA crosses | 25 |
| leash events (5 EMA, >=3 closes) | 41 |
| RSI zone bars: bull/range/bear | 486/861/282 |
| bearish RSI divergences | 24 |
| range bars (n=20 prior, width<=25%) | 1062 |
| range edge bars | 423 |
| range breakout closes | 111 |

| setup | events | per 10 bars | long/short |
|---|---|---|---|
| S1 | 0 | 0.0 | 0/0 |
| S2 | 61 | 0.371272 | 32/29 |
| S3 | 23 | 0.139988 | 8/15 |
| S4 | 24 | 0.146074 | 15/9 |
| S5 | 12 | 0.073037 | 7/5 |
| S6 | 41 | 0.249544 | 25/16 |
| S7 | 2 | 0.012173 | 2/0 |
| S8 | 51 | 0.310408 | 32/19 |
| S9 | 29 | 0.176506 | 0/29 |

Over the 1.0 per 10 bars ceiling: none

## 1w (234 bars)

| detector | count |
|---|---|
| swing highs/lows (confirmed) | 46 |
| trend state: up bars | 110 |
| trend state: down bars | 24 |
| trend reversals (state flips up<->down) | 3 |
| bars with >=1 ranked zone | 214 |
| volume >= 2x (prior-20 baseline) | 7 |
| volume >= 2x (same-slot baseline) | 11 |
| volume <= 0.5x | 12 |
| BBWP >= 85 (expansion) | 10 |
| BBWP <= 30 (compression) | 57 |
| strict bullish engulfing | 7 |
| strict bearish engulfing | 4 |
| hammer | 14 |
| shooting star | 13 |
| doji | 33 |
| three black crows | 20 |
| 21/55 EMA crosses | 2 |
| leash events (5 EMA, >=3 closes) | 8 |
| RSI zone bars: bull/range/bear | 89/93/38 |
| bearish RSI divergences | 4 |
| range bars (n=20 prior, width<=25%) | 2 |
| range edge bars | 1 |
| range breakout closes | 0 |

| setup | events | per 10 bars | long/short |
|---|---|---|---|
| S1 | 0 | 0.0 | 0/0 |
| S2 | 11 | 0.470085 | 6/5 |
| S3 | 0 | 0.0 | 0/0 |
| S4 | 0 | 0.0 | 0/0 |
| S5 | 0 | 0.0 | 0/0 |
| S6 | 8 | 0.34188 | 5/3 |
| S7 | 0 | 0.0 | 0/0 |
| S8 | 3 | 0.128205 | 3/0 |
| S9 | 1 | 0.042735 | 0/1 |

Over the 1.0 per 10 bars ceiling: none

