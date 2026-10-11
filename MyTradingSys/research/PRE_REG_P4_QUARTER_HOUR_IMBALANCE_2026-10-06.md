# PRE-REGISTRATION P4 QUARTER-HOUR OPENING IMBALANCE REPLICATION - 2026-10-06

**Session:** MTS-2026-10-06-1254Z-APP-ANA-research-agenda  
**Registered:** 2026-10-06 12:55 UTC (before computation)  
**Paper:** Kim & Hansen arXiv 2607.09426 (quarter-hour opening order imbalance → 4/8/12h returns)  
**Source data:** orderflow_1m buy/sell volume at exact quarter-hour opens (00:00, 06:00, 12:00, 18:00 UTC)

## Design

**Symbols:** BTC/USDT perp; ETH/USDT and other perps if on disk (F:/MTS/data/orderflow_1m)  
**Windows:** 1m, 5m, 15m (non-overlapping)  
**Imbalance proxy:** (buy_volume - sell_volume) / (buy_volume + sell_volume) at the exact quarter-hour bar  
**Returns windows:** 4h, 8h, 12h (forward-looking from the quarter-hour open)  

**Sign stability test (pre-registration):** Gross returns sign must be consistent across all years in the data before netting fees. If sign flips by year, replication fails.  
**Net-of-fees test:** After applying backtest/fees.py (taker 0.0005 round-trip), CI95 must exclude 0 for a PASS. Otherwise, replication does not support the edge.

## Thresholds (pre-registered)

**PASS criteria:** 
1. Gross sign stable across years (same sign each year)
2. Net return mean ≠ 0 at CI95 (block-bootstrap, 2000 draws, seed 12345)

**FAIL criteria:** Sign flips or CI95 includes 0 after costs

## Stop rule

Replication only if gross sign is stable. Report effective n (number of quarter-hour opens per window), block-bootstrap CI95 and p-value.

**Placebo control:** Random (shuffled date) imbalance vs. actual returns (to detect spurious correlation).

## Pre-computed constants

- Taker fee per side: 0.0005 (from backtest/fees.py v3.1, round-trip = 0.001)
- **NO-SOURCE TAG:** None — fee value from committed backtest/fees.py

## Result block

(To be appended after computation; this file was committed before running)
