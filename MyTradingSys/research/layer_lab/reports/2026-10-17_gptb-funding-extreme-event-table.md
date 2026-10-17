# Funding extreme event table — 2026-10-17

**BUILT** — 2,736 DEV funding-print rows; 726 extreme events, all with complete 24h forward MFE/MAE in ATR14 units.

## Work and evidence

- `MyTradingSys/backtest/bt/bt_data.py:56-77` is the read-only history loader: CSV `calc_time` and `last_funding_rate` become sorted `(timestamp, rate)` pairs.
- `MyTradingSys/research/layer_lab/funding_extreme_event_table/event_table.py:16-77` implements the trailing 90-print 95th percentile with current print excluded, fade side, last-completed-bar ATR14 R, and 24-hour excursion. Missing inputs return `NOT_IN_DATA`.
- `MyTradingSys/research/layer_lab/funding_extreme_event_table/event_table.py:78-119` reads only funding zip months through June 2024 and slices the 1h kline archive to the DEV cutoff.
- `python -m pytest MyTradingSys/research/layer_lab/funding_extreme_event_table/test_event_table.py -q -p no:cacheprovider` -> **5 passed**. Before implementation it failed collection because `event_table.py` was absent.
- `python MyTradingSys/research/layer_lab/funding_extreme_event_table/event_table.py --output %TEMP%\funding_extreme_event_table.csv` -> 2,736 rows, 726 extreme, 90 `NOT_IN_DATA`.
- The saved CSV recount found 2,646 `OK` baseline rows, with 726 of 726 extreme rows having complete forward excursions (695 short fades, 31 long fades).
- Trial recorded in `MyTradingSys/research/layer_lab/TRIALS.md`.

## Findings

| Severity | File:line | Finding | Evidence | Fix |
|---|---|---|---|---|
| LOW | `event_table.py:21-27` | Baseline availability is fail-closed before 90 prior prints. | Synthetic test confirms the first 90 prints are `NOT_IN_DATA`; 90 real DEV prints so labeled. | None. |
| LOW | `event_table.py:29-35` | PIT percentile excludes the event print and fades its sign. | Hand-computed synthetic baseline q95 is `0.008455`; current spike does not change it. | None. |
| LOW | `event_table.py:42-77` | Entry ATR and price come from the prior completed bar; forward excursion is bounded to 24 hours. | Synthetic test distinguishes prior close (90) from the still-open bar (500), confirms 24 bars and ignores a post-horizon high; 726 empirical extreme windows complete. | None. |

No validation or holdout bars were read; no trading rules were added.
