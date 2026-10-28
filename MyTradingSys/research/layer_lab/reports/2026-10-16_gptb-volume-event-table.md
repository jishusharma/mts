# BLOCKED -- DEV 1h/4h klines are unavailable

## What was built

Implemented the requested DEV-only per-bar event table in `event_table.py:21-107`. Relative volume divides current volume by the median of the prior N exact same-hour-of-week observations; the current bar is excluded and any missing prior slot leaves `NOT_IN_DATA` (`event_table.py:49-77`). Spikes use `>= 2x`. The forward window starts at the next bar open and reports signed close return, MFE and MAE in R, with R equal to the spike candle high-low range and direction set by its body (`event_table.py:78-106`). The R denominator/orientation are implementation choices; the read-only registration describes volume event definitions and horizons but does not define an R unit for this table (`PRE_REG_VOLUME_2026-10-09.md:47-49`). Incomplete or gapped forward windows are `NOT_IN_DATA`.

The module also has a CSV CLI (`event_table.py:109-151`). It filters timestamps to DEV, 2022-01-01 through 2024-06-30 (`event_table.py:6-7`), and does not load VALIDATION or HOLDOUT.

## DEV data and row counts

No empirical table could be generated. `Dumps/backtest` is absent. A workspace scan for kline/ohlc/raw_1h/raw_4h CSV, NPZ and parquet candidates found no matching DEV source files; the only broad CSV match resembling market data was a 1d pytest fixture under another layer's `pytest_tmp` directory, and it was not used. The source pre-registration defines DEV as bar opens before 2024-07-01 (`PRE_REG_VOLUME_2026-10-09.md:23`). Empirical rows: **0 input / 0 generated**. No data-backed run was logged to `TRIALS.md`. HOLDOUT was not accessed.

## Test-first record and verification

- Added `test_bearish_spike_excursions_are_directionally_correct` before the implementation fix. Red run: `python -m pytest MyTradingSys/research/layer_lab/volume_event_table/test_event_table.py -q -p no:cacheprovider` -> **1 failed, 3 passed**; bearish `mfe_R` was `0.0`, expected `1.5`.
- After fixing bearish MFE/MAE orientation and requiring a complete forward horizon: same command -> **5 passed**. Tests cover prior-only median/current exclusion, 1h spike detection and hand-computed forward R, insufficient history as `NOT_IN_DATA`, bearish excursions, and 4h baseline behavior.
- `python -m py_compile MyTradingSys/research/layer_lab/volume_event_table/event_table.py` -> passed.
- Wiring registry JSON parse -> valid JSON.

## Registration

The test is listed in `scripts/dev/run_extra_tests.py:27` EXTRA. The module is registered as a TOOL in `MyTradingSys/system/wiring_registry.json:827-830`, with no live imports.

## Findings

| Severity | Reference | Finding | Evidence / disposition |
|---|---|---|---|
| HIGH | `Dumps/backtest` (missing); `PRE_REG_VOLUME_2026-10-09.md:23` | Required DEV klines are unavailable in the permitted workspace, so empirical event row counts and forward outcomes cannot be produced. | `Test-Path Dumps/backtest` -> `False`; no matching 1h/4h DEV input was found. Empirical result: **NOT_IN_DATA**. |
| LOW | `event_table.py:25-26`; `PRE_REG_VOLUME_2026-10-09.md:47-49` | The research registration gives event definitions but not an R denominator for this event table. | Current implementation uses the event bar high-low range, body direction, and next-bar-open entry. This is an implementation choice, not trader-sourced. |

Follow-up cards created: none.

## Block reason

Required DEV 1h/4h klines are missing from the permitted workspace. Therefore, no DEV event table or empirical row counts can be generated. The code and synthetic tests are complete, but the card remains unmarked as instructed for blocked work.
