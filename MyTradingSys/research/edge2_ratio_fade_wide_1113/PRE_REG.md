# PRE_REG: account-ratio fade, 1d signal, 20 NEW Bybit USDT perps (wave 2 confirmation), 2026-11-13

Written and committed BEFORE any wave-2 outcome is computed. Slug edge2-ratio-fade-wide-1113.

## What was already seen (wave 1, 10 coins BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX)
Same rule, 1d signal, 7-day hold: DEV +196 bp (CI +74..+316, n 629), VALIDATION -86 bp (CI -311..+143, n 197), RECENT +131 bp (CI +6..+264, n 291). 1d/3d was also computed there (not read for this PRE_REG). Nothing from the 20 new coins has been looked at, not even a price chart.

## Hypothesis
Fading the account long/short ratio when it sits in its trailing-90-day top or bottom 5% earns a fee-net, funding-net positive return over 3 and 7 days on coins that were NOT used to find the rule. Wave 1's DEV/RECENT positive and VALIDATION negative is either a single-regime effect or noise; this test decides on fresh coins.

## Rule (identical to wave 1 `crowd.py`, parameters all OURS and unchanged)
Account buy-ratio (4h rows; the 1d signal uses the last completed 4h row at 00:00Z, decision at the close of the 20:00-24:00 bar): value in trailing 90-day (540 rows) top 5% -> short; bottom 5% -> long; window excludes the current row. Entry at next bar open (00:00Z), one position per coin, hold H days. Net = side x (exit/entry-1) - 2 x fees.BINANCE_TAKER - side x funding rates paid while held. Fee is the repo constant.

## Coins (20, list fixed now)
Chosen by Bybit 24h turnover rank on 2026-11-13, taken in rank order from the current top ~130 USDT perps, after removing (i) the 10 wave-1 coins, (ii) non-crypto contracts (stock, ETF, commodity, innovation-zone, gold token XAUT/PAXG), (iii) listings after 2024-03-31 (they have no 90-day window before VALIDATION). Literal turnover ranks 11-30 are mostly equities, commodity and 2025-26 listings, so the filter reaches down to rank 81:
ZEC NEAR 1000PEPE SUI UNI XMR AAVE WLD INJ XLM ONDO ARB TAO BCH TIA HBAR ICP QNT STRK APT.
SURVIVOR BIAS: ranking by today's turnover keeps coins that are alive and liquid in 2026; delisted or faded coins are absent, which flatters long-side and drift-sensitive results. Listing dates differ, so DEV n is smaller than wave 1 (several coins start 2022-2023).

## Cells (2, both tested in every split)
Primary: {1d signal, 7-day hold}. Secondary: {1d signal, 3-day hold}. For each: both sides pooled, long-only, short-only reported (the side cuts are descriptive; the pass is judged on both-sides pooled).

## Splits (entry time decides)
DEV 2020-01-01..2024-06-30; VALIDATION 2024-07-01..2025-06-30; RECENT 2025-07-01..now. Also per calendar year means (descriptive) to see whether weakness is one regime.

## Placebo (drift-matched)
For every real trade: same coin, same calendar month, same side, same hold, entry bar a random 00:00Z day in that month (200 draws, not restricted by the one-position rule). Placebo mean per draw; the cell must exceed the 95th percentile of the draw means (and the real-minus-placebo mean is reported).

## Bootstrap, multiple testing
Cluster bootstrap by ISO week (all coins in a week = one cluster), 4000 resamples, 95% CI of the mean, one-sided p of mean <= 0. BH at 10% over the cells' VALIDATION p-values (2 cells, both-sides pooled).

## Context
Account ratio is retail-heavy; fading it is the standard form. Regime mix: DEV mixed bull/bear/recovery, VALIDATION = 2024H2 bull then 2025 chop, RECENT = 2025H2 onward mixed/down; the exact share of 3-day windows up per split is printed from prices by study.py. Parameters (90d, 5%, 3/7 days) are OURS, none SOURCED.
Regime mix: DEV ~0.50 up, VALIDATION ~0.51, RECENT ~0.47 (wave-1 figures on prices; this coin set is printed before outcomes).

## Pass rule
VALIDATION both-sides fee-net mean > 0, bootstrap CI lower > 0, n >= 30, beats drift-matched placebo p95, BH 10% over 2 cells. n < 30 = UNDERPOWERED. Else FAIL. A DEV- or RECENT-only result is reported, not a pass. Pooled VALIDATION+RECENT is reported as extra context only.
