# Pre-registration: timeframe flip lead-lag, BTC (mtf-timeframe-lead-lag-research)

Frozen by B (JIS-NUC, Claude Opus) on 2026-11-08 before any lead-lag number was computed. Operator ask (2026-10-28, card note): identify the timeframe flip early, then anticipate it.

## Context

- Regime: DEV 2019-11-08 .. 2023-12-31 pooled; VALIDATION 2024-01-01 .. 2026-11-07 opened once, after DEV rules are frozen in the DEV commit. Split by daily close vs 200-day SMA.
- Phase: none (multi-year study); the current range is too short to judge.
- Session: none (state flips are dated by bar close in UTC).
- Entry: none for the lead-lag tables; the forward-return check enters at the close of the bar that confirms the early-flip rule, holds 1/3/7 days, 0.10 % round-trip fee (fees.FEES_ALL_TAKER, 5 bps each side).

## Definitions

- Timeframes: 15m, 1h, 4h, 1d, 1w (Binance spot BTCUSDT, data-api.binance.vision, closed bars).
- RSI state (Wilder 14): BULL when RSI closes >= 60, BEAR when <= 40, else MID. Malkan's 40/60 lines (SOURCED). A flip is the close of the bar where the state changes to BULL or BEAR from any other state; it is dated at that bar's close time (causal).
- WaveTrend (LazyBear 10/21, wt2 = SMA4 of wt1): a flip is a wt1/wt2 cross, dated at the close of the crossing bar.
- Lead-lag: for every 1d flip (and every 4h flip), take the most recent same-direction flip on each lower timeframe within the 7 days before it; lead = hours between them. No lower-TF flip in the window = "no lead".
- Early-flip rules (all fixed here, no search): R1 4h flips to BULL/BEAR; R2 4h and 1h both in the same new state; R3 R2 plus the 1d RSI already on the same side of 50.
- Hit: a 1d flip in the same direction follows within 7 days. False flip: none follows.

## Outputs

Lead table per TF pair (n, median, IQR, share with a lead); hit and false-flip rates of R1-R3; fee-net forward return after each rule vs the unconditional return over the same horizon; DEV, then VALIDATION.

## Kill line

A rule is a lead only if its VALIDATION hit rate beats the base rate of a 1d flip in any random 7-day window by 10 points or more, and its fee-net forward return beats the baseline at 3 days by more than 2 SE. Otherwise: no usable early-flip rule from RSI/WT states alone.
