# BLOCKED — DEV klines are absent

## Built

`event_table.py:20-24` builds a per-bar table for 1h/4h klines. RV is current volume divided by the median of the previous N observations at the same hour-of-week slot. It excludes the current bar and requires every prior slot to exist. Rows without a complete baseline are `NOT_IN_DATA` (`event_table.py:37-77`); spikes use the configured `>= 2x` threshold. Forward return, MFE and MAE are measured in units of the spike bar's high-low range, from the next bar open, oriented by the spike candle body (`event_table.py:79-101`). Both denominator and orientation are implementation choices because the read-only volume study specifies forward-return horizons but no R definition for volume spikes.

## DEV run and row counts

No empirical run was possible. `Test-Path Dumps/backtest` returned `False`; workspace scan for kline/ohlc/raw_1h/raw_4h CSV, NPZ and parquet candidates returned `candidate_count 0`. The required DEV data range is 2022-01-01 through 2024-06-30 from `PRE_REG_VOLUME_2026-10-09.md:19-24`. Empirical rows: **0 available / 0 generated**. No row was added to `TRIALS.md` because there was no data-backed trial.

## Test-first record and verification

- Red first: `python -m pytest MyTradingSys/research/layer_lab/volume_event_table/test_event_table.py -q -p no:cacheprovider` failed during collection with `FileNotFoundError` for the then-absent `event_table.py`.
- Green: the same command -> **3 passed**. Tests cover a hand-computed median that excludes the current bar, a known spike and forward R excursions, and fewer than N prior weeks returning `NOT_IN_DATA`.
- `python -m py_compile MyTradingSys/research/layer_lab/volume_event_table/event_table.py` -> passed.
- Wiring registry JSON parse -> `wiring_registry.json: valid JSON`.

## Registration

The test is listed in `scripts/dev/run_extra_tests.py:27` EXTRA. The standalone builder is registered as TOOL in `MyTradingSys/system/wiring_registry.json:827-830`; it has no live imports.

## Block reason

Required DEV klines are missing from the permitted workspace (`Dumps/backtest` does not exist). The empirical DEV event table and its row counts cannot be produced. HOLDOUT was not accessed. The card remains unmarked.
