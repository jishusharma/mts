# PRE-REGISTRATION P1 COST FLOOR ANALYSIS - 2026-10-06

**Session:** MTS-2026-10-06-1254Z-APP-ANA-research-agenda  
**Registered:** 2026-10-06 12:55 UTC (before computation)  
**Source code:** p1_cost_floor.py logic from GitHub PR #11 (claude/project-thread-mvbseb branch), applied to full orderflow_1m archive.

## Design

**Data:** F:/MTS/data/orderflow_1m (2024-12-02 onward, contiguous segments only)  
**Strategy:** Passive limit orders (no active signal), offset levels 0/2/5 bp below/above prior 1m close  
**Execution:** Fills by touch and strictly-through (aggTrades trade-through if on disk)  
**Holds:** 5m and 15m (per p1_cost_floor.py specification)  
**Output metric:** Mean adverse selection (bp from limit price per month, aggregated across days and symbols)  

**Bootstrap:** Day-block bootstrap 95% CI (days as resampling unit; accounts for intra-day correlations)  

**Decision rule:** If mean adverse selection < maker-vs-taker fee saving (from backtest/fees.py), passive execution is worth modelling per candidate.

## Pre-computed constants

- Maker fee: 0.00 (from backtest/fees.py v3.1)
- Taker fee: 0.0005 (from backtest/fees.py v3.1)
- Maker-vs-taker fee saving per round-trip: 0.0005 × 2 = 0.0010 (10 bp)
- **NO-SOURCE TAG:** None — all fee values from committed backtest/fees.py, not tuned for this analysis

## Thresholds (pre-registered, not tuned)

**PASS criteria:** Mean adverse selection < 10 bp (the fee saving threshold)  
**Report:** Month-level and aggregate statistics with effective n (number of filled orders), placebo control (random execution at prior close), and CI95 bounds

## Stop rule

Run the full archive (2024-12-02..2026-10-06). No re-tuning of offsets, symbol selection, or hold periods.

## Result block

(To be appended after computation; this file was committed before running)
