# Bigtrade forward event table

**CONTAMINATED (DEV read VALIDATION 2024-07..12)** - the numbers below (DEV ended 2024-12-31, 153,685 rows) read six months of VALIDATION. Fixed 2026-10-17, now DEV = 2022-01-01..2024-06-30, 128,078 rows (5,685 OK). See DEV_BOUNDARY_FIX_2026-10-17.md. Text below is the original, kept for the record.

Build result: `event_table.py`, `test_event_table.py`, and `event_table.csv`; the CSV contains 153,685 TRAIN/DEV fire rows measured against the existing cached klines.

## What was built

- `event_table.py` loads the existing fire CSVs and cached timeframe arrays through the read-only `fires_kline` interface. It does not replay or alter fire rules.
- DEV is the existing TRAIN date range, 2022-01-01 through 2024-12-31 UTC. Fires outside that range are omitted; excursion bars must be after the fire close and before 2025-01-01 UTC.
- Risk in R is absolute fire price to stop distance. MFE/MAE are the maximum favourable/adverse excursions over the next 20 bars. First-hit levels are ±1R; if the same bar reaches both, the stop is recorded first.
- Missing klines, invalid side/risk, missing stop, or no future DEV bars produces a row with `NOT_IN_DATA` and blank metrics.

## Data and verification

Source: `F:\MTS\data\bigtrade\fires` and `F:\MTS\data\bigtrade\cache\perp` (cache metadata reports 2,507,040 1m bars, 501,408 5m, 167,136 15m, and 41,784 1h bars; first timestamp 2022-01-01 UTC). Fire records store candle close times while cache arrays store candle open times, so the loader adds one timeframe duration before matching.

Command: `python MyTradingSys/research/layer_lab/bigtrade_event_table/event_table.py --output MyTradingSys/research/layer_lab/bigtrade_event_table/event_table.csv`

Result: 153,685 rows total; 6,748 `OK`; 146,937 `NOT_IN_DATA`. The high missing count is retained as missing data, never interpreted as zero. Per timeframe: 1m 105,209 missing; 5m 25,878 missing; 15m 5,400 OK / 13,046 missing; 1h 1,348 OK / 2,804 missing.

Tests were written before implementation. Red check: pytest collection failed because `event_table.py` did not exist. Green check: `python -m pytest MyTradingSys/research/layer_lab/bigtrade_event_table/test_event_table.py -q -p no:cacheprovider` -> `4 passed in 0.39s`.

## Files

- `event_table.py`: table generation and DEV clipping.
- `test_event_table.py`: hand-computed excursions, forward-bar measurement, missing-klines row, and conservative ambiguous-bar tie.
- `event_table.csv`: generated per-fire research table.
- `scripts/dev/run_extra_tests.py`: test registered in EXTRA.
- `MyTradingSys/system/wiring_registry.json`: module registered as REPRO.
