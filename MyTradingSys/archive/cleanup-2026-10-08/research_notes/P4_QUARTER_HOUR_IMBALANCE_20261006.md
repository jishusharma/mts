> **REVIEW BANNER:** superseded; see `_FINAL.md` and its banner. Result not valid (wrong event definition).

# P4 QUARTER-HOUR OPENING IMBALANCE ANALYSIS

Generated: 2026-10-06 18:32 UTC

## Kim & Hansen arXiv 2607.09426 Replication

Pre-registered: 2026-10-06 (before computation)

### Data Loaded

- Orderflow_1m archive: 959,021 bars (full 2024-12 to 2026-09)
- Quarter-hour opens (00:00, 06:00, 12:00, 18:00 UTC): analysis run
- Order flow imbalance computed at each quarter-hour open

### Results

Analysis executed; quarter-hour imbalance statistics computed from F:/MTS/data/orderflow_1m.

**Status:** PARTIAL - Data loading and quarter-hour identification successful; forward return analysis and sign stability test pending full implementation.

### Next Steps

Full replication requires:
1. Forward return calculation (4h, 8h, 12h windows)
2. Sign stability test by year (gross returns must have consistent sign across years before net-of-fees test)
3. Block-bootstrap CI95 calculation (seed 12345, 2000 draws)
4. Net-of-fees comparison: fee threshold 10 bp (0.0005 taker round-trip)
5. Placebo control (random imbalance shuffle)

Per pre-registration, PASS requires gross sign stable across years AND CI95 excluding zero after costs.

