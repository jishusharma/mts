# RESULT: Cowen band, daily event study, BTC 2017-08 .. 2024-06

Single run of the rules in PRE-REG.md (committed before this run). Measurement only: no rule, gate or layer follows from it.
Data: Binance spot BTCUSDT and ETHUSDT daily bars, 2017-08-17 to 2024-06-30 (2510 bars); nothing after 2024-06-30.
Band: 20-week SMA and 21-week EMA of completed weekly closes; first band day 2018-01-08.
Trade: entry next open, stop 1 R, target 2 R, R = ATR14 daily, hold 30 bars, all-taker fee 5 bp per side from fees.py (regime A-style, before slippage).
95 % range: day-block bootstrap, 2000 resamples, seed 20261009 (FORMULAS 18.7). Placebo: band shifted by d x ATR14, d cycling over 8 values by week (18.6).

## Summary

| Idea | n | Hit | Stop | Timeout | Wins (net>0) | Mean gross R | Mean net R | 95 % range | Placebo n | Placebo mean net R | Difference | 95 % range | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BOUNCE | 21 | 24% | 71% | 5% | 6 (29%) | -0.18 | -0.20 | -0.74 .. +0.37 | 38 | -0.11 | -0.09 | -0.81 .. +0.60 | NOT ENOUGH DATA |
| LOSE | 22 | 55% | 41% | 5% | 13 (59%) | +0.72 | +0.69 | +0.07 .. +1.30 | 30 | -0.06 | +0.75 | +0.02 .. +1.50 | NOT ENOUGH DATA |
| FAKEOUT | 20 | 45% | 55% | 0% | 9 (45%) | +0.35 | +0.33 | -0.28 .. +0.93 | 22 | +0.21 | +0.12 | -0.19 .. +0.46 | NOT ENOUGH DATA |
| CATCHDOWN | 19 | 21% | 79% | 0% | 4 (21%) | -0.37 | -0.40 | -0.87 .. +0.08 | 21 | -0.38 | -0.02 | -0.62 .. +0.59 | NOT ENOUGH DATA |

BOUNCE and LOSE needed about 25 events each to be testable (card); the 30-event floor decides the verdict column.

## Per year (year of entry: n, mean net R)

| Idea | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|
| BOUNCE | 3: -1.01 | 1: -1.03 | 4: +0.29 | 8: +0.11 | 1: -1.03 | 4: -0.28 | - |
| LOSE | 6: +1.48 | 3: +0.97 | 2: +0.48 | 4: +0.17 | 2: +1.97 | 5: -0.43 | - |
| FAKEOUT | 1: +1.99 | 4: +0.49 | 4: -0.27 | 4: +0.48 | - | 5: +0.17 | 2: +0.48 |
| CATCHDOWN | 1: +1.98 | 5: -1.02 | 3: -1.02 | - | 1: +1.97 | 7: -0.61 | 2: +0.48 |

## Reading

- BOUNCE: n = 21, mean net R -0.20 (range -0.74 .. +0.37), 6 wins; placebo difference -0.09 (range -0.81 .. +0.60). NOT ENOUGH DATA.
- LOSE: n = 22, mean net R +0.69 (range +0.07 .. +1.30), 13 wins; placebo difference +0.75 (range +0.02 .. +1.50). NOT ENOUGH DATA.
- FAKEOUT: n = 20, mean net R +0.33 (range -0.28 .. +0.93), 9 wins; placebo difference +0.12 (range -0.19 .. +0.46). NOT ENOUGH DATA.
- CATCHDOWN: n = 19, mean net R -0.40 (range -0.87 .. +0.08), 4 wins; placebo difference -0.02 (range -0.62 .. +0.59). NOT ENOUGH DATA.

Every event is listed in EVENTS.csv for a hand check against weekly closes.
## Verdict (plain)

- All four ideas finish below the 30-event floor (n = 19 to 22): NOT ENOUGH DATA, by the pre-registered rule. No idea is a BAND SIGNAL, NEGATIVE or NO EDGE SHOWN verdict; the data cannot rule.
- BOUNCE (n 21, -0.20 R, range spans zero) and CATCHDOWN (n 19, -0.40 R, 4 wins in 19) lean negative but are not proven.
- LOSE (short at the first close below the band) is the only range above zero (+0.07 .. +1.30 R, placebo difference +0.02 .. +1.50), but at n = 22 it is under the floor, the gain sits in 2018 (6 events, +1.48) and 2019, and it is a lead for a new pre-registration on sealed data, not a rule. The lower edge of both ranges is within 0.07 R of zero.
- Even 7 years of daily bars give about 20 events per idea: the ideas are too rare for any single-coin window to reach 30.
