# Large trades: buying vs absorption on 5m bars (2026-10-30)

These are descriptive counts only: no fees and no edge claim. Definitions are in the header of `study.py` (all OURS).

Data: `F:/MTS/data/orderflow_1m`, Binance BTCUSDT perp aggTrades rolled to 1m. "Large" = prints at or above the trailing 99th-percentile trade size, the same thing as CoinGlass's bubbles. DEV 2024-12 to 2025-12 only; 2026 untouched.

Trigger, shot d107df338858 (10-29, axis in IST):
- Big green bubbles on red bars just after the 81,953.7 top, and again on the 80.5k breakdown bar. Price kept falling.
- Red bubbles on the cascade, then both colours at the 78,210 low, and a bounce.

## Counts

A large-buy bar = large-trade net in the top 2% of 5m bars (>= +244.5 BTC); a large-sell bar = bottom 2% (<= -259.2 BTC).

| Class | What the chart shows | n | Up 60 min | Up 4 h | +0.5% first | -0.5% first |
|---|---|---|---|---|---|---|
| buy-aggression | big buys, green bar | 1,155 | 47.4% | 48.1% | 44.8% | 45.2% |
| buy-absorbed | big buys, red bar (effort, no result) | 99 | 50.5% | 51.5% | 47.5% | 42.4% |
| sell-aggression | big sells, red bar | 1,168 | 53.5% | 55.5% | 46.6% | 45.2% |
| sell-absorbed | big sells, green bar | 95 | 44.2% | 43.2% | 35.8% | 54.7% |

Reading:
- **Aggression fades a little.** After a big-buy green bar, the next hour was up 47%; after a big-sell red bar, 54%. Large aggressors tend to mark short-term exhaustion.
- **Absorption is rare:** about 100 cases a year each way.
- **On its own, absorption did not reverse price as the textbook says.**
  - After absorbed big sells, price went DOWN first more often (55% vs 36%), at about 2 standard errors.
  - Absorbed big buys showed no clear lean.
- **Fabio's reading needs his context, which this count does not have:** the absorption sits at a level (VAH/VAL, daily high/low) after a push. The shot is that case: absorbed buys right after the run to 81.95k.
- **So the next count is level x absorption** (U1 in `level-approach-prep`). It is now measurable with this data.

## What MTS needs to read this live (plan, cards)

1. **Live input:** the live order-flow writer (`backtest/layers/fabio/test_orderflow_live.py` covers it) already rolls aggTrades to the same 1m fields (b99 buy/sell, footprint).
2. **Classifier:** the four classes above per closed 5m bar, plus the level context (distance to the prior-day high/low, VAH/VAL, last swing). Card `level-approach-prep`.
3. **Panel:** live_aid shows the class, the measured odds and n from the context table, never a call.
4. **Live threshold:** the 2% cut here comes from the whole DEV sample (look-ahead lint WARN, fine for a description). Live, it must be a trailing quantile.
5. **Gate:** a class reaches the panel only with n >= 100 in its context cell on DEV.
