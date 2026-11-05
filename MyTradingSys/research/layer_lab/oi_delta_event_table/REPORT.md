# OI DATA NOW PRESENT — empirical DEV run pending (was BLOCKED)

## Correction 2026-11-05: OI is now in data

The `OI | 0` row and the `NOT_IN_DATA` reading below are superseded. Binance USD-M 5m metrics (OI, top-trader and global long/short ratios) now sit in the shared data root `<MTS_METRICS_ROOT>/<SYMBOL>/` (fleet path F:/MTS/data/metrics), written by `MyTradingSys/backtest/fetch_futures_metrics.py`: BTCUSDT and ETHUSDT 1768 of 1769 days each (2022-01-01..2026-11-04, 11-04 not yet published; 509,051 rows each), 4 short days, ratio columns blank on 91,781 rows up to 2022-12-13. Gap list: `MyTradingSys/system/DATA_NOTES.md`. The empirical DEV run is still to do; the sections below record the pre-fetch state.

## Built and verified

The DEV-only table implementation classifies the four price/OI sign states, computes forward return, MFE and MAE in stop-risk units from bars strictly after each event, and emits `NOT_IN_DATA` when OI is absent. Its synthetic test file passes: `python -m pytest MyTradingSys/research/layer_lab/oi_delta_event_table/test_event_table.py -q -p no:cacheprovider` -> `3 passed`.

The test is registered in `scripts/dev/run_extra_tests.py` (`EXTRA`, OI event-table entry), and the implementation is declared `REPRO` in `MyTradingSys/system/wiring_registry.json` (OI event-table entry).

## Input inventory and result

Command: `python MyTradingSys/research/layer_lab/oi_delta_event_table/event_table.py --inventory`

| Category | Candidate files | Empirical rows |
|---|---:|---:|
| OI | 0 | 0 |
| Funding | 78 | 0 |
| Whale | 0 | 0 |

No empirical events or forward outcomes can be produced. The 2026-10-10 read-only study uses snapshot files under `runtime_data/snapshots` and `runtime_data/outcome_labels.json` (`MyTradingSys/research/loose_code/oi_event_study_2026-10-10.py`, `SNAPS`/`LABELS` assignments); those raw inputs are not present in this checkout. Funding archives do not supply OI. The affected period is `NOT_IN_DATA`.

## Test-first record

At task start, `event_table.py`, `test_event_table.py`, and the initial reports already existed in the workspace. Therefore a genuine pre-implementation red run cannot be established from this session; the prior draft's claim that collection failed because the module did not exist is not independently supported. The current implementation's synthetic tests were rerun and pass as noted above.

No DEV empirical trial was run, so no row was added to `TRIALS.md`. No `tasks.py done` action was taken because the empirical input requirement is blocked by missing OI data.
