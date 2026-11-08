# Pre-registration: auction census on 5m and 15m, session blocks, HTF ladder gate, node exits (census-5m-15m-7y-session-ladder-1109)

Frozen by B (JIS-NUC, Claude Opus) on 2026-11-08 before any 5m/15m result was looked at. The 1h census (AUCTION_CENSUS_1108.md) and Fable's 2R/3R recompute are already known; this run tests the two exits and frames the post-mortem (POSTMORTEM_OPUS.md s6) left untested.

## Context

- Regime: 7 years pooled, split by the HTF ladder bias (auction_context.build_mtf_context: monthly colour vs the 20-month SMA, SOURCED in that file) and by year.
- Phase: two buckets. `range_1024` = days from 2026-10-24 (the Bible range 75.4-80.9k, BIBLE.md:28) and `rest`. The range bucket is about 2 weeks, so it is reported, not judged.
- Session: UTC blocks, OURS: asia 00-07, london 07-13, ny 13-21, late 21-24.
- Entry: the census rule unchanged (close of the classifier's firing bar, levels from prior day/week only, auction_census.py). Market entry at the close is a taker fill in reality; the Deribit fee arm charges it as maker, as the card asks, and the taker arm is the honest bound.

## Data

Binance spot BTCUSDT 5m and 15m from data-api.binance.vision, 2019-11-08 .. 2026-11-07, closed bars only; daily bars from the same source for the ladder and the bias. Public mirror; no order flow (klines carry no delta, so Fabio's absorption half stays untested).

## Hypothesis

H1 (primary): on 15m, rejection fades (FAST_REJECTION and WEAK_REJECTION) taken only in the london and ny blocks and only with the ladder (long needs a bullish HTF bias, short a bearish one), exited node to node with break-even at +1R and half off at the prior-day POC, have mean net R > 0 under FEES_DERIBIT.

## Arms (all reported; only H1 is judged)

- timeframe: 5m, 15m
- exit: 1R bracket (the old census) vs node + BE
- fee: FEES_DERIBIT (maker entry and target 0, taker stop and timeout 5 bps; fees.py:48) vs FEES_ALL_TAKER (5 bps each leg)
- gate: none, session (london+ny), ladder, session + ladder
- split: session, ladder bias, phase, year

## Slippage stress (folds census-fetch-binance-mirror-1109)

A third fee arm, `taker+slip`, subtracts trade_costs.net_return's own `slip_rt` default (4 bps round trip in code; FORMULAS.md s13 text says 2 bps, so the code value is the conservative one). H1 must also stay > 0 there to be called robust; it is reported, not part of the kill line.

## Kill line

H1 has an edge only if its mean net R > 0 AND > 2 standard errors (SE = stdev / sqrt(n)), AND it is positive under the taker arm too. Anything else: no edge for this exit shape, and the node+BE exit joins the closed list. n < 100 for H1: INCONCLUSIVE (underpowered), not a pass.

## Not changed

The classifier, the levels, cooldowns (5m 48 bars, 15m 16 bars = 4 h), the 60-bar window, horizon (5m 24 bars = 2 h on the old census; this run uses 5m 96 bars and 15m 32 bars = 8 h so a node target has time to fill; OURS, frozen here).
