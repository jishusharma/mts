# PRE_REG: positioning crowding as a contrarian signal, 4h and 1d, 10 Bybit USDT perps (2026-11-13)

Written and committed BEFORE any outcome (forward return) is computed. Slug edge-crowding-reversal-1113.

## Hypothesis
When positioning is crowded one way (funding or account long/short ratio in its own trailing 90-day top/bottom 5%), the crowded side loses over the next 1-7 days, enough to pay taker fees both legs plus funding. Not a duplicate: `layer_lab/funding_extreme_event_table` is a BTC-only 1h DEV excursion table with no fees and no verdict; `oi_side_2026-10-30` is BTC 5m descriptive counts; T055 was funding carry (hold the side that receives funding), not crowding reversal. The account-ratio signal and the pooled cross-coin 4h/1d test have not been run in the repo.

## Data (Bybit v5 public, cached under runtime_data/edge-crowding-reversal-1113/)
Coins: BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX (those that return data). Kline 4h, funding/history (8h), open-interest 4h, account-ratio 4h. A coin enters a split only once its own 90-day trailing window is full.

## Signals (each x timeframe x hold = a cell). Decision at close of a TF bar (TF = 4h or 1d).
All values are PIT: a funding print is usable at its timestamp; a 4h OI or ratio row is stamped at its period start and is usable only from period start + 4h (conservative). Percentile windows exclude the current value.
- (a) FUND: funding in trailing 90-day (OURS) top 5% (OURS) of its own prints -> short; bottom 5% -> long.
- (b) RATIO: account buy-ratio (4h rows; for 1d the last completed 4h row at 00:00Z) in trailing 90-day top 5% -> short; bottom 5% -> long.
- (c) FUND+PUSH: (a) AND 3-day return in the crowded direction > X, X = 1.0 x ATR14(daily) x sqrt(3) as a fraction of price (OURS; "coin's own 3d ATR multiple"). Positive-extreme needs price up > X; negative-extreme needs price down > X.
- (d) OIFLAT: 3-day OI change > 2 sd (sd over trailing 90 days of 3-day OI changes, OURS) AND |3-day return| < 0.5 x X (OURS "flat") -> trade against the funding sign (funding > 0 -> short, < 0 -> long, 0 -> skip).

## Trade
Entry at the next TF bar open; hold H in {1, 3, 7} days (OURS, set by the brief), exit at the open of the first bar at or after entry + H. One position per coin at a time (a signal during an open hold is skipped). Net = side x (exit/entry - 1) - 2 x fees.BINANCE_TAKER - side x (sum of funding rates of prints with entry < ts <= exit). Fee is the repo constant (Bybit taker is within 1 bp of it).
Cells: 4 signals x 2 TF x 3 holds = 24, tested in every split; the pass is judged on VALIDATION.

## Splits
DEV 2020-01-01..2024-06-30; VALIDATION 2024-07-01..2025-06-30; RECENT 2025-07-01..now (entry time decides the split). No parameter is tuned on any split; every parameter is fixed above before the run.

## Placebo, bootstrap, multiple testing
- Placebo: for every real trade, a random entry bar of the same coin, same calendar month, same side, same TF and hold (200 draws, free of the one-position rule); placebo mean per draw; the cell must exceed the 95th percentile of the 200 draw means.
- CI: cluster bootstrap by ISO week (all coins in one week = one cluster), 4000 resamples, 95% percentile CI of the mean; one-sided p = share of resampled means <= 0.
- BH at 10% over the 24 VALIDATION cells.

## Context
Crowding as a reversal cue is a common trader belief (squeeze after one-sided funding); the account ratio is retail-heavy so fading it is the standard form. OUR expectation is small: 4h/1d moves are 10-100x the round-trip fee, so fees matter little, but funding paid while held can eat or add to the edge. Parameters 90d, 5%, 2 sd, 1.0 x ATR3d, 0.5 x X, holds 1/3/7 are all OURS; none is SOURCED from a trader.

Regime mix: DEV = 2020-21 bull, 2022 bear, 2023-24H1 recovery (about 60% up-trend days); VALIDATION = 2024H2 bull into 2025 chop; RECENT = 2025H2 onward mixed/down. Descriptive from price history; the exact up/down share per split is printed by study.py from prices before outcomes are read.

## Primary metric and pass rule
Primary: mean fee-net, funding-net return per trade, pooled over coins, VALIDATION split. PASS = VALIDATION fee-net mean > 0 AND bootstrap 95% CI lower bound > 0 AND n >= 30 AND beats placebo AND survives BH 10% over the 24 cells. n < 30 = UNDERPOWERED. Otherwise FAIL. A DEV-only or RECENT-only result is reported but is not a pass.
