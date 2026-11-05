# PRE_REG: big-candle stories, top-trader read, phase (operator ask 2026-11-05, d-bigcandle-story-toptraders-1105)

Descriptive, fee-free; no entries, no trade rule, no edge claim, so no costs and no fees.py import.

## Question
When a BTC 5m or 1h bar has a big move in price, OI or taker delta, which of the 8 anticipation_map stories is it, what did the top traders do over that hour (size vs head count), and how often did price continue or get undone over the next 1h / 4h / 24h, split by phase?

## Data and window
- Binance USD-M BTCUSDT 1m klines (F:/MTS/data/tom_raw/klines, aggregated to 5m, a bucket needs all 5 bars) + metrics 5m (F:/MTS/data/binance_metrics): sum_open_interest, sum_toptrader_long_short_ratio (POSITIONS), count_toptrader_long_short_ratio (ACCOUNTS). Blank or 0 = missing. SOURCED.
- DEV only: 2022-01-03 to 2024-06-30. Holdout never read for any table. The 2026-11-04 walk-through reads public days 2026-08-01..2026-11-04 (data.binance.vision, fetch_data.py) for event labels and phase only, no forward outcomes.

## Definitions (all OURS, fixed before any outcome column was read)
- Bar: 5m or calendar 1h. Price change = close/open - 1; OI change = OI at bar close minus OI at previous bar close; delta = sum of (2 x taker buy volume - volume). Metrics rows are stamped at bar close.
- Big: |z| >= 3 in price, OI change or delta, z vs mean/sd of the same series over the trailing 30 days, prior bars only (needs 80 % valid). No full-sample statistics.
- Story: signs of price, OI change, delta (no flat band; a zero or missing sign drops the bar) -> the 8 keys UP|UP|BUY .. DOWN|DOWN|BUY, same labels as anticipation_map.
- 5m events: after an event the next 12 bars are skipped (1h outcome windows never overlap). 1h events: every big hour; 4h and 24h outcomes overlap, so CIs are optimistic (said in RESULT).
- Top-trader class over the 60 min ending at the event bar close: relative change of positions ratio and of accounts ratio, each |change| < 0.2 % = FLAT. Classes: BU both up, BD both down, SL size long / accounts short (positions up, accounts down), SS size short / accounts long.
- Outcome at 1h, 4h, 24h after the event bar close: continues = close beyond the event close in the event direction; undone = close back past the event bar start price. Baseline = the same measure over every bar of that granularity with a non-zero price change, by direction and phase.
- Phase: weekly streak = number of consecutive red or green weekly candles (Monday 00:00 UTC grid, futures 5m bars, close vs open) before the event's week, grouped R3+ / R1-2 / G1-2 / G3+; band = trailing 30-day return > +10 % bull, < -10 % bear, else range.
- Wilson 95 % CI on every rate; n per cell; n < 30 = THIN.

## Context
Regime: none as a gate; band bull/bear/range is a split label and the mix is reported, not gated.
Phase: weekly red/green streak and the 30-day band, as split labels (OURS), never a filter.
Session: none, because events are every UTC bar; no session gate.
Entry: none, because there is no entry: fee-free descriptive follow-up only.

## What the result will say
RESULT.md: the 2026-11-04 walk-through first, then baseline vs story vs story x top-trader class x phase tables, the answer on size-long / accounts-short after a big up candle, Parameters SOURCED vs OURS, and a `Regime mix:` line.
FROZEN_UTC: 2026-11-05T14:00:00Z
