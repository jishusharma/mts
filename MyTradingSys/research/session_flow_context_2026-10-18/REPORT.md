# REPORT: context-conditioned session flow states (BTCUSDT perp, DEV 2025-10-01..2026-02-28)

Result: **INCONCLUSIVE (underpowered).** The operator's claim (flow behaviour is stable only inside a context) can neither be confirmed nor refuted on the
13 months of OI data on disk (only the 5-month DEV window was read): 27 heterogeneity tests, smallest p = 0.032 (SHORT_COVER x oitrend) against the frozen alpha 5.7e-4 (m = 87); only 2 of 84
context cells have MDE <= 50 bps. Rules, labels and thresholds: `PRE_REG.md` (frozen before `event_table.py` ran). Code-bug correction after review: the first `build_rows.py` run skipped the last day (2026-02-28, loop `<`); fixed to `<=` and re-run, 600 -> 604 rows; no rule or threshold changed (the PRE_REG s.7 counts below were printed from the 600-row file, see REPORT numbers for the final ones). VALIDATION and HOLDOUT unread.

## What was built
- `build_rows.py`: 604 DEV session rows (151 days x ASIA/LDN/US/LATE) with price chg, taker delta (FORMULAS.md s.14), 5m OI chg, quadrant, sweep-reclaim,
  five as-of context buckets and the next-session return / range. `rows_dev.csv` is the output (public market aggregates only).
- `event_table.py`: pattern x context table (`EVENT_TABLE.csv`, 84 cells + 6 ALL rows), heterogeneity Wald tests (`HETEROGENEITY.csv`), verdict.
- `test_build_rows.py`: 12 tests; hand-computed fixture (delta, OI change, quadrant, sweep-reclaim, vol percentile), a no-look-ahead test that overwrites all
  data after a session end, the split seal, cluster SE by hand, chi-square values, and a planted-difference Wald check. Failed before `build_rows.py` existed.

## Numbers (DEV, signed next-session return in bps, day-clustered SE; ALL contexts pooled)
| pattern | n | days | mean bps | SE | t | MDE |
|---|---|---|---|---|---|---|
| NEW_LONG | 143 | 100 | -12.35 | 11.04 | -1.12 | 47.3 |
| SHORT_COVER | 153 | 106 | -5.9 | 9.95 | -0.59 | 42.6 |
| NEW_SHORT | 148 | 94 | 0.22 | 12.08 | 0.02 | 51.8 |
| LONG_LIQ | 159 | 110 | 13.39 | 9.77 | 1.37 | 41.8 |
| SR_BEAR | 56 | 47 | -5.32 | 17.04 | -0.31 | 73.0 |
| SR_BULL | 64 | 55 | -16.55 | 18.55 | -0.89 | 79.5 |
No pooled pattern has |t| > 1.4; the round-trip cost is 12 bps. Of 84 context cells only 2 have |t| > 2 (expected by chance at this count: about 4).
Within-cell H1/H2 sign agreement is 47 of 83 (57 %, a coin flip); pooled patterns 4 of 6. The "stable within a context" half of the claim therefore shows
no signal here, and the data cannot tell a small within-context effect from noise.

## Verdict on the operator's claim
INCONCLUSIVE, not refuted. Cells are 2-116 events; a cell needs about 566 days to see 0.30 sd (`prereg_gate.py`, BLOCK at the design stage, PRE_REG s.7).
Deviations from the card: (1) data gate only partly met: metrics on disk start 2025-09-01, not 2020-09-01; (2) 3 of the 30 planned tests could not be run
(fewer than two cells with 15 distinct days); (3) OI end value uses the last sample strictly before the session end (look-ahead safe).

## Left on the card
1. Desk fetch (DSA-NUC): `fetch_binance_archive.py` metrics BTCUSDT 2020-09-01..2025-08-31 (about 1,800 daily files), plus the 1m klines for the same span (already in `F:/MTS/data/tom_raw/klines` to 2024-06).
2. New PRE_REG re-cutting DEV/VALIDATION/HOLDOUT on the long history (same code, thresholds re-registered first), then run once.
3. Optional after that: delta_agree and delta_norm as a fifth state axis (stored in rows, untested here).
