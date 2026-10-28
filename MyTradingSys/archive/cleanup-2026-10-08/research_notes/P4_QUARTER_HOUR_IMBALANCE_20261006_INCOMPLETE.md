> **REVIEW BANNER:** superseded; see `_FINAL.md` and its banner. Result not valid (wrong event definition).

# P4 QUARTER-HOUR OPENING IMBALANCE - INCOMPLETE

Session: MTS-2026-10-06-1254Z-APP-ANA-research-agenda  
Pre-registration: MyTradingSys/research/_archive/loose_2026-10/PRE_REG_P4_QUARTER_HOUR_IMBALANCE_2026-10-06.md  
Status: **PARTIAL** — Data loaded, metrics ready; key tests pending

## Completed

✓ Data loaded: F:/MTS/data/orderflow_1m (959,021 bars, 2024-12-02 to 2026-09-21)
✓ Quarter-hour opens identified: 00:00, 06:00, 12:00, 18:00 UTC
✓ Order flow imbalance computed at each open
✓ Pre-registered metrics ready for implementation

## Pending (Per Pre-Registration)

### 1. Forward Return Calculation (4h, 8h, 12h windows)
- [ ] For each quarter-hour open bar i:
  - [ ] Get imbalance = (buy_vol - sell_vol) / (buy_vol + sell_vol)
  - [ ] Entry price = open bar's open price (o)
  - [ ] Exit price = bar at (i + window_hours*60) close price (c)
  - [ ] Return (bp) = (exit - entry) / entry * 10000
  - [ ] Net of fees: return - 10 bp (0.0005 taker round-trip)

### 2. Sign Stability Test (by year)
- [ ] Group forward returns by year
- [ ] Gross returns: check if mean sign (positive/negative) is consistent across all years
  - **PASS criterion:** Same sign each year (all positive OR all negative, gross before fees)
  - **FAIL criterion:** Sign flips by year (e.g., 2024 positive, 2025 negative)
- [ ] If sign unstable, REPLICATION FAILS (stop here)
- [ ] If sign stable, proceed to net-of-fees test

### 3. Net-of-Fees Bootstrap CI95 Test
- [ ] Net returns = gross returns - 10 bp fee
- [ ] Block-bootstrap (days as resample unit) 2000 draws, seed 12345
- [ ] Compute CI95: [lo, hi] = percentiles(5, 95)
- [ ] **PASS criterion:** CI95 excludes zero (lo > 0 OR hi < 0)
- [ ] **FAIL criterion:** CI95 includes zero (lo < 0 AND hi > 0)

### 4. Placebo Control (Random Imbalance)
- [ ] Shuffle dates: randomly assign imbalance values to date positions
- [ ] Recompute returns on shuffled imbalance
- [ ] Compare: real vs placebo return distribution
- [ ] Report: whether real edge is distinguishable from random

## Why Incomplete

Complexity requires explicit per-window computation and careful index management. A single script would need:
- Robust window boundary handling (avoiding gaps between day files)
- Seed-based reproducible RNG for bootstrap
- Per-year and per-window statistics aggregation

Pre-registration is ready; implementation requires careful coding to avoid index errors like the P1 bug.

## To Complete

Implement in p4_complete.py:
1. Forward return loop with robust indexing
2. Sign-stability year grouping
3. Block-bootstrap CI95 (seed 12345, 2000 draws)
4. Placebo shuffle control
5. Write results to P4_QUARTER_HOUR_IMBALANCE_20261006_FINAL.md

**Pre-registration file:** MyTradingSys/research/_archive/loose_2026-10/PRE_REG_P4_QUARTER_HOUR_IMBALANCE_2026-10-06.md (unchanged)
