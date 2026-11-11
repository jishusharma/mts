# Edge from other points of view, 2026-11-11

Operator order 2026-11-11 16:15Z: refine the edge ideas, look from several points of view, run Haiku and Sonnet in parallel.
Five readers ran in parallel; each folder has its PREREG.md (written before results) and RESULT.md. Compared by the Supervisor.
Descriptive; no edge claim; no forecast. All rules: fixed in advance, no sweeps, DEV / 30-day gap / VALIDATION, placebo, fee 10 bp.

## 1. Results
| View | Model | Rule | DEV | VALIDATION | Verdict |
|---|---|---|---|---|---|
| TREND | Sonnet | Daily Donchian 20/10 | +11.7 % per trade, n 50, t 1.49 | +0.87 %, n 38, t 0.39 | FAIL |
| TREND | Sonnet | 4h Donchian 55/20 | +1.90 %, n 123, t 1.62 | +0.95 %, n 85, t 0.97 | closest; not provable |
| TREND | Sonnet | 28-day momentum, weekly | +6.6 %, n 64, t 1.17 | +1.9 %, n 40, t 0.76 | FAIL |
| FLOW | Sonnet | Funding bottom 5 % long, 3 d | +1.33 %, n 55, t 1.75 | -0.34 %, n 58 | FAIL |
| FLOW | Sonnet | Long after a 1h drop of 3 % or more on 3x volume, 24 h | +0.58 % (long side) | +1.34 %, n 17 | LEAD, n too small |
| FLOW | Sonnet | Long after OI -5 % in 4 h, 24 h | -0.11 %, n 75 | +0.67 %, n 18 | INCONCLUSIVE |
| TIME | Sonnet | 44 clock cells (hour, weekday, session, funding hour) | 0 of 44 beyond Bonferroni (t 3.25) | - | FAIL; best hour +4.4 bp, under the fee |

Trend: the long side carries all the gain and it does not beat buy-and-hold (+453 % DEV, +179 % VALIDATION); shorts are zero
or negative. The trend placebo matches direction, so long-only rows cannot be separated from simply being long BTC.

## 2. Maps (Haiku)
- TESTED_MAP.md: 100 counted studies, not 15. Per family: other 33, fade-at-level 19, mean-reversion 18, breakout 11,
  forced-flow 7 (all descriptive, no fees, 1m-1h), analyst-context 4, seasonality 4, trend-following 2, momentum 1, carry 1,
  cross-asset 0. 29 folders have a PRE_REG and no RESULT. With 100 tries, some will look good by luck: one good result needs a higher bar.
- DATA_MAP.md: nine more coins have 1m candles on disk (ETH 2022 to 2026-09; ADA, AVAX, BNB, DOGE, LINK, LTC, SOL, XRP 2022-01
  to 2024-06). Funding is BTC only; OI is BTC and ETH; no liquidation history; analyst calls cover 5 days structured.

## 3. Reading (Supervisor)
1. Three more views fail on BTC alone. The single lead is buying a forced sell-off (the only rule positive in both periods,
   and the only one that names who pays). Validation n is 17, so BTC alone cannot prove or kill it.
2. The pooled test is possible today: the same frozen rule on ten coins from the 1m data on disk. Card
   forced-selloff-long-pooled-10-coins-1111. Coins move together, so events are counted per day, not per coin.
3. Same pooling for the 4h Donchian rule (positive in both periods, t under 2): second rule in the same card.
4. Corrections to earlier statements: "15 trials" is the last edge table only; forced flows were looked at 7 times before,
   never as a trade rule with fees.
5. Not done: his own journaled trades (card operator-trade-journal-private-1111), analyst calls as a filter (5 days of data,
   too short), liquidation history (not on disk).
