# PRE_REG edge2_capitulation_long_2026-11 (frozen before any outcome is computed)

Slug edge2-capitulation-long-1113. Wave 2 of the 5h edge push; confirms the one lead of wave 1 (edge-extreme-confirm-template-1113, folder extreme_confirm_template_2026-11, reading "e").

## Disclosure of what was already seen
Wave 1 computed the 1h version of this reading on the original 10 coins (BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX), including VALIDATION and RECENT. Capitulation-bar long made about +0.5..+0.6% per trade fee-net there in two trend buckets, CI including 0. So the 1h original-10 data is NOT out-of-sample here. The honest out-of-sample tests are (a) NEW coins not in wave 1 and (b) the 4h timeframe (never computed). 4h bars were never looked at on any coin. Final coin list is fixed before any outcome by data availability only (no returns computed on them).

## Hypothesis
A capitulation bar (huge range, closes in its lower quarter) followed by a confirming bar that closes above the capitulation close, bought at the confirming close, gives a fee-net positive mean per trade, pooled over daily-trend buckets.

## Rule (exact)
- Bars: Bybit v5 linear klines (public). 1h as cached by wave 1 for the 10 original coins and fetched for the NEW 20; 4h = UTC-aligned resample of 1h (4 complete bars; open of first, max high, min low, close of last).
- ATR = Wilder 14 (bigmoves.atr, SOURCED standard default), on the bars of the timeframe being traded.
- Setup bar i = reading "e" long, identical to wave 1: high-low >= 3 x ATR[i-1] AND close in the lower 25% of the bar's range ((close-low)/(high-low) <= 0.25). 3x and 25% SOURCED from the wave-1 brief (OURS to the trader).
- Confirming bar i+1: close[i+1] > close[i]. Entry at close[i+1] (change vs wave 1: close of the confirming candle, not next open).
- Stop = low[i] - 0.25 x ATR[i] (0.25 fixed, no DEV selection). Checked on every bar after entry, filled at min(stop, that bar open). Entry skipped if entry <= stop. No profit target.
- Exit: stop, else close of the bar `hold` bars after entry. Exit 24h = 24 bars (1h) / 6 bars (4h); exit 3d = 72 bars (1h) / 18 bars (4h).
- One open position per coin per cell. Pooled over the three daily-trend buckets (no bucket filter, no bucket cells).
- Costs: 2 x fees.BINANCE_TAKER round trip (fees.py) plus Bybit funding history charged while held (long pays). No slippage (disclosed).
- All thresholds are fixed up front: nothing is fitted on DEV. DEV is reported descriptively only.

## Coin sets
- OLD10 = the wave-1 ten.
- NEW20 = the first 20 of this ordered candidate list that have >= 2 years of Bybit 1h linear history: DOT UNI ATOM NEAR FIL TRX ETC BCH AAVE XLM ICP APT ARB OP INJ SAND MANA AXS ALGO GRT (reserves EOS THETA). The realised list is in the run output and RESULTS.

## Cells (6, all tested)
{1h on NEW20, 4h on OLD10, 4h on NEW20} x {exit 24h, exit 3d}. Descriptive only (not tested, no BH): all-30-coin pooled on 1h and 4h, and 1h OLD10 (already seen in wave 1).

## Splits (by setup bar close, UTC)
DEV 2020-01-01..2024-06-30, VALIDATION 2024-07-01..2025-06-30, RECENT 2025-07-01..now. Coins listed later simply contribute from their first bar.

## Metric and pass rule
Per-trade fee-net return, pooled over coins in the cell. 95% CI = bootstrap over entry-week blocks (2000 resamples, seed 1113); one-sided p = share of resamples with mean <= 0. PASS (cell) = VALIDATION n >= 30, mean > 0, CI lower bound > 0, mean above the 95th percentile of the placebo, Benjamini-Hochberg 10% over the 6 tested cells on VALIDATION p. Headline additionally needs RECENT n >= 30, mean > 0, CI lower bound > 0. n < 30 = UNDERPOWERED.
Placebo: same coin, same calendar month, same split, same number of trades as the cell, entries at random bars (any bar; no extreme and no confirm condition) with identical mechanics (stop = low of the preceding bar - 0.25 ATR, same hold), 500 draws with replacement; pool ignores the one-position rule (disclosed).

## Context
Wave 1 found the capitulation long positive in both VALIDATION and RECENT but with CIs spanning 0 because 54 cells diluted the test and n was small. This wave tests one rule, 6 cells, and more trades (30 coins, 4h). Daily-trend context is deliberately pooled (the lead appeared in two of three buckets).
Regime mix: not computed here (no bucket in the rule); wave 1 DEV daily bars over the original 10 coins: above both 38% | between 15% | below both 47%.

## How this differs from what already failed
bb_range_to_range, bb_lvn_triggers, BIGCANDLE-STORY (BTC, descriptive), CANDLE-P1/D19 (fixed patterns on BTC) and wave 1 (54 cells, 1h, 10 coins): none tests an ATR-scaled capitulation bar with a confirm-close entry on 4h or on 20 new coins with a confirmatory 6-cell family.
