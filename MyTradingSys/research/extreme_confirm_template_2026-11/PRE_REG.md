# PRE_REG extreme_confirm_template_2026-11 (frozen before any outcome is computed)

Slug edge-extreme-confirm-template-1113. Operator idea 2026-11-13: measure how extreme a reading gets, then daily context, then a rare reading on 1h, then a confirming candle, then entry. RSI is NOT tested here (sibling worker).

## Hypothesis
After a rare one-sided extreme on 1h (long = oversold side, short = mirrored), a confirming bar (next bar closes above the setup close for longs, below for shorts) followed by a next-open entry gives a fee-net positive mean per trade, and more than random confirmed bars in the same coin and daily context bucket.

## Rule (exact)
- Bars: Bybit v5 1h linear klines, 10 coins BTC ETH SOL XRP DOGE BNB ADA LINK LTC AVAX, from each coin's first bar available (BTC 2020-03-25, others later; Bybit API depth, disclosed). Setup bar i. Confirming bar i+1: close[i+1] > close[i] (long), < (short). Entry at open[i+2].
- Reuse (no new indicator code): krown_core.ema / rsi, bigmoves.atr (Wilder 14), live_bb_top_reversal.bollinger (20,2), kurisko stoch_core.stoch_line.
- Readings (long side; short = mirror: upper band, EMA below price, K high, up-run, close in upper 25%):
  - a: m = (lower BB(20,2) - close)/ATR14; fire when m >= DEV percentile 99 (a1) or 95 (a5) of m, per coin.
  - b1: m = (EMA200(1h) - close)/ATR14, b2: m = (daily EMA20 last closed - close)/ATR14; fire at m >= DEV q99 / q95 per coin (b1_99 b1_95 b2_99 b2_95).
  - c: StochRSI(14,14,3,3): K = SMA3 of raw stoch of RSI14 over 14 < 5 AND 4h StochRSI K (last closed 4h bar, 1h resampled UTC-aligned) < 20. Short: K > 95 and 4h K > 80.
  - d: run of consecutive lower closes; N = ceil of DEV 99th percentile of run length per coin; fire on the bar where run == N. Short: higher closes.
  - e: range >= 3 x ATR14[i-1] and close in the lower 25% of the bar's range. Short: upper 25%.
- Daily context bucket at setup close: last closed daily close vs daily EMA20/EMA50: above both / between / below both. Cells are split by bucket (3).
- Stop: long = setup-bar low - k*ATR14[i], short = setup high + k*ATR; k in {0.25, 1.0} chosen per cell on DEV by higher DEV mean (tie -> 1.0). Target 2R (R = entry - stop). Time stop: exit at close of the 24th bar from entry. Stop checked before target in the same bar. Entry with R <= 0 skipped.
- One open position per coin per cell. Fees 2 x fees.BINANCE_TAKER round trip (fees.py); funding from Bybit funding history charged while held (long pays, short receives). No slippage modelled (disclosed).
- Params: all thresholds OURS (percentiles 99/95 chosen from the operator idea, not a trader source); StochRSI 14,14,3,3, BB 20,2, ATR 14 SOURCED (standard defaults); 3x ATR and lower 25% SOURCED from the brief; stops 0.25/1.0, 2R, 24h from the brief.

## Cells (54, all pre-registered)
18 conditions x 3 buckets: a (2 pct x 2 sides =4), b (2 readings x 2 pct x 2 sides = 8), c (2 sides), d (2 sides), e (2 sides). Longs and shorts are separate families. BTC alone = descriptive rows only (not tested). Stop choice is part of the cell (DEV selection), not extra cells.

## Splits (by setup bar close, UTC)
DEV 2020-01-01..2024-06-30 (thresholds and stop choice only), VALIDATION 2024-07-01..2025-06-30, RECENT 2025-07-01..now.

## Metric and pass rule
Per-trade fee-net return %, pooled over coins; 95% CI by cluster bootstrap over entry day (2000 resamples, seed 1113). One-sided p = share of resamples with mean <= 0. PASS (cell) = VALIDATION n >= 30, mean > 0, CI lower bound > 0, beats placebo, BH 10% across all 54 cells on VALIDATION p. Headline "passes VALIDATION and RECENT" additionally needs RECENT n >= 30, mean > 0, CI lower bound > 0. n < 30 = UNDERPOWERED.
Placebo: same coin, same bucket, same side, same split; random bars with the same confirming-candle condition but the extreme condition false, same trade mechanics and stop k; per coin the same number of trades as the cell, 500 draws; beats = cell mean above the 95th percentile of the placebo means. Placebo pool ignores the one-position rule (disclosed).

## Context
Daily context is the as-of bucket above; bucket is a filter and a cell dimension. Cross-coin pooling is the new element.
Regime mix: DEV daily bars pooled over the 10 coins by bucket: above both 38% | between 15% | below both 47% (11542 coin-days; research_kit regime_tag not used because the bucket is the context).

## How each cell differs from what already failed (layer_map.json)
- bb_range_to_range 2026-11-04 (BB 15m FAIL, 0/6 cells, net -0.12 to -0.15%): BTC only, 15m, range gate and sessions, bracket at band close; here 1h, 10 coins, percentile-extreme distance beyond the band, plus a confirming close, ATR stop, daily-EMA bucket.
- bb_lvn_triggers (BB-outside triggers, no cell survives): BTC, no confirm candle, no percentile-extreme threshold.
- VOL-V1..V4 (volume events, premium not supported): volume-based; none here uses volume.
- CANDLE-P1 / D19 / CANDLE-CLOSE-DEV (patterns, close sequences at levels; 0/126 arms): fixed patterns or levels on BTC 1d/4h; d here is a run-length at a DEV percentile on 1h across coins, e is an ATR-scaled capitulation bar; none tests an ATR-unit distance from EMA200/daily EMA20 (b) or StochRSI with 4h agreement (c).
- BIGCANDLE-STORY (big 1h BTC candles, 8 stories): BTC, descriptive; e here is traded with a confirm candle and pooled over coins.
