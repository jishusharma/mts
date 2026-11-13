# PRE_REG: weekly red-streak bounce, LONG only (edge9, 2026-11-14)

Written and committed before any outcome is computed. Research, not advice. Public spot data only.

## Context
- Operator thesis (2026-11-13): BTC closed 6 red weeks (-20%), a reaction up is likely; where and how to buy it.
- Phase definition (OURS): weekly close above its 50-week simple MA = BULL, below = BEAR (the 50wMA is the common cycle-trend line; the choice is not tuned). The current streak is a BEAR-phase streak (price below 50wMA). Every event is tagged and `Regime mix:` (share of VALIDATION events in BEAR) is reported; results are not generalised beyond the mix seen.
- Why the streak matters (hypothesis, OURS): long runs of red weeks mark capitulation/exhaustion, so mean reversion up is more likely than after a random week. Counter-hypothesis: in a bear phase trends persist and the streak is momentum. Test decides.
- Sample caveat: streak events are rare and cluster in few calendar weeks (many coins fire together). Cluster by week; VALIDATION is small.

## Data (public, no keys)
- Study universe: Binance SPOT public klines via data-api.binance.vision (never a futures host), `<COIN>USDT`, 1d. Weeks built from UTC daily bars, Monday 00:00 UTC, complete weeks only.
- Coins (rule, OURS): BTC, ETH, plus the 20 largest others by current CoinGecko market cap (rank list fetched 2026-11-14), excluding stablecoins and wrapped/staked tokens, that have a Binance USDT daily first bar on or before 2022-11-01 (>= 4 years). Survivorship bias (today's big coins) is acknowledged and favours longs; reported in RESULT.
- BTC streak table (descriptive only): Coinbase Exchange public BTC-USD daily from 2015 (longest history; Bitstamp unreachable from this host).

## Events (week W = completed week, event time = W close = Monday 00:00 UTC after)
- STREAK-N, N in {4,5,6}: event fires on the first week where the consecutive-red count (close<open) reaches exactly N. N=5 PRIMARY.
- DD20: weekly close <= 0.80 x max weekly close of the prior 8 weeks.
- Cooldown (OURS): per coin and per event type, no new event within 8 weeks of the previous.
- Tags: streak start (first red week's Monday; DD20: week of the 8-week max close) -> `base_low` = lowest daily low from that start to the event close; `L_event` = high of week W; `ref_low` = low of week W.

## Entries (day index d0 = Monday after the event)
- E1: buy open of d0.
- E2 bear trap: from d0 within 21 days, first day s with low < ref_low (sweep), then first day r >= s with close > ref_low (reclaim; r may equal s). Buy open of r+1. No sweep+reclaim in 21 days = no trade.
- E3 retest: from d0 within 28 days, first day c with close > L_event; then within 10 days after c, first day d with low <= L_event; buy at min(open_d, L_event). No trade otherwise.

## Exits
- X1/X2/X4: close of day (entry_day + 7k - 1), k = 1, 2, 4 weeks.
- XS: stop = base_low - 0.5 x ATR14 (daily, Wilder, value at the entry day's prior close); checked on daily lows from the entry day (E3: from the day after entry); fill at min(open, stop) on a gap; else time exit at 4 weeks. Skip the event if entry <= stop. R = net % return / ((entry-stop)/entry); reported alongside % return. For XS the tested quantity is net R.
- Costs (SOURCED: MyTradingSys/backtest/fees.py): BINANCE_TAKER 0.0005 per side = 10 bp round trip, plus SLIPPAGE_RT_S13 0.0002 (2 bp) = 12 bp round trip, subtracted from % return.

## Rows
4 event types x 3 entries x 4 exits = 48 rows. Observation = one trade (coin, entry date).

## Split
DEV = entry date <= 2021-12-31. VALIDATION = entry date >= 2022-01-01. Nothing is fit on DEV (no parameters tuned); DEV is shown for stability only.

## Gates (verdict per row, all on VALIDATION)
1. >= 30 VAL events, else UNDERPOWERED.
2. Mean fee-net return (R for XS) > 0 and week-cluster bootstrap (clusters = calendar week of entry, 10000 resamples, seed 7) 95% CI lower bound > 0.
3. Placebo: for each VAL event a random entry day (open) from the same coin's VAL days with the same hold; XS placebo uses the same stop recipe with the event's lookback length; 5000 draws of the mean; p = share of placebo means >= observed; need p < 0.05.
4. BH at 10% across the 48 placebo p-values.
5. Mean still > 0 after removing the 3 calendar-week clusters with the largest summed return.
PASS = all five. Otherwise the first failing gate is named.

## BTC descriptive table
Every streak of >= 5 red weeks in Coinbase BTC-USD: dates, depth (open of first red to close of last red), return over the next 1/2/4/8 weeks from the following Monday open, whether the last red week's low was swept (traded below) in the next 3 weeks before a close back above it.

## Label
All parameters OURS unless marked SOURCED (costs only). Round-trip cost constants: SOURCED. Weeks Monday 00:00 UTC: SOURCED convention (Binance/TradingView weekly).
