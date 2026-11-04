# PRE_REG: WT extreme cross, volatility-matched baseline, BTCUSDT + ETHUSDT (frozen 2026-11-05, before any return was computed)

Card `ms-wt-extreme-cross-volmatch-eth`. The source study `wt_extreme_cross_2026-11` (BTCUSDT spot, DEV) found the buy bounce larger
AGAINST the HTF trend (+0.033 % excess on 1m, +0.207 % on 15m) and after a trend day (prior_trend +0.038 % 1m, +0.232 % 15m), against an
UNMATCHED baseline (every 7th bar). Both are high-volatility states. This study asks: does that excess survive when the baseline is
drawn only from bars in the same ATR(14) decile as the event bar? Descriptive; fee-net shown, no survivor / trade claim.

verdicts.py check "wavetrend extreme cross": no prior row matches. Safe to pre-register.

## Parameters (every one labelled; event definitions reused from the source study by path, no retuning)

| Parameter | Value | Label |
|---|---|---|
| Buy event | wt1 crosses above wt2 with wt1 <= -50 | SOURCED card (operator) |
| Sell event | wt1 crosses below wt2 with wt1 >= +40 | SOURCED card / bible lesson 8 |
| K | 10 bars after the event-bar close | SOURCED operator "5-10 bars"; upper end = OURS |
| HTF | daily close vs its MA (research_kit.regime_tag side), with / against the trade side; context from each symbol's spot 1d history (as bb_range_retest_eth_pool) | SOURCED-in-repo |
| Day tag | prior UTC day trend iff abs(close - open) / (high - low) >= 0.6 (fabio v3 P41); prior = as-of | SOURCED-in-repo |
| ATR | Wilder ATR(14) on the event TF, as % of the bar close | ATR(14) SOURCED Wilder; % normalisation OURS |
| ATR deciles | edges = deciles of ATR % over all DEV bars of that symbol and TF | OURS |
| Matched baseline | mean same-side 10-bar MFE over every DEV bar in the event bar's ATR decile (stride 1) | OURS |
| Unmatched baseline | mean same-side 10-bar MFE over every DEV bar (stride 1), shown for comparison | OURS |
| Cost | net = 10-bar close-to-close return minus 2 x fees.BINANCE_TAKER (0.10 % round trip); second column minus research_kit.TAKER_RT_PCT (0.14 %, the source's cost) | SOURCED fees.py / research_kit |
| Statistics | day-clustered SE, cluster = (symbol, UTC day of the event close); t = mean / SE | SOURCED research_kit; symbol-day cluster OURS |
| Data | BTCUSDT and ETHUSDT USD-M futures 1m (F:/MTS/data/tom_raw/klines), resampled 5m / 15m; BTC futures reproduction row vs the shipped spot n first | OURS |
| Windows | DEV only: event closes in [2022-01-01, 2024-07-01); the loader raises on an end after 2024-07-01. VALIDATION and HOLDOUT are not read | SOURCED backtest/splits.py |

## Verdict rule (decided before any number)

Focal cells = POOL buy, {1m, 15m} x {HTF against, prior_trend} = 4 cells (the four claims of the source). Matched excess p from the
normal of t (one-sided, excess > 0), Holm m = 4 at 0.05.
- SURVIVES-MATCHING: at least one focal cell passes Holm.
- VOLATILITY-ONLY: no focal cell passes Holm AND every focal cell has >= 100 days (OURS power floor).
- UNDERPOWERED: otherwise.
Per-symbol cells (BTC, ETH) and all other tf x side x HTF x day-tag cells are descriptive only.

## What the result will say

RESULT.md: `Regime mix:` line, verdict, BTC reproduction row (futures n vs shipped spot n), per tf x side x HTF cell: n, days, unmatched
excess, matched excess (t), net at 0.10 and 0.14, for BTC, ETH and POOL; the source's unmatched row for comparison.

## Context
Regime: none as a gate, because this is a descriptive all-regime study; the DEV regime mix (research_kit.regime_tag, weekly) is reported per symbol.
Phase: none, because the event is the WaveTrend extreme cross itself; HTF with/against and prior-day trend/range are the split dimensions.
Session: none, because the source study pooled all UTC hours and the hypothesis is about volatility, not session.
Entry: event-bar close at market (taker), fixed 10-bar exit; descriptive only.

FROZEN_UTC: 2026-11-05T05:40:00Z
