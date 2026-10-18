# Session-level failed-break event table

**Verdict: 445 events; tests green (4 passed).**

## What was built and run

- `event_table.py` imports the detector read-only and calls `failed_break_events` for both sides using its default 60-minute failure window. It reads BTCUSDT 1m zip CSVs only through 2024-06-30, computes four-hour forward MFE/MAE normalized by `R = abs(spike - level)`, and marks incomplete or missing forward minutes `NOT_IN_DATA`. See `event_table.py` lines 1-90.
- Output: `events.csv`; 445 rows: 225 high and 220 low. All 445 have complete forward windows. This is event-table construction, with no rules, fees, or outcome inference.
- Red proof: before implementation, `python -m pytest MyTradingSys/research/layer_lab/session_levels_event_table/test_event_table.py -q` failed collection because `event_table.py` did not exist.
- Green: same command after implementation: `4 passed` (2026-10-17).
- DEV run: `python MyTradingSys/research/layer_lab/session_levels_event_table/event_table.py --output MyTradingSys/research/layer_lab/session_levels_event_table/events.csv` -> `events=445 high=225 low=220 forward={'OK': 445, 'NOT_IN_DATA': 0}`.
- Trial logged in `MyTradingSys/research/layer_lab/TRIALS.md`. Test gate registration and wiring disposition are in `scripts/dev/run_extra_tests.py` and `MyTradingSys/system/wiring_registry.json`.

## Findings

| Severity | File:line | Finding | Evidence |
|---|---|---|---|
| LOW | `event_table.py:15-23` | Archive reader uses the allowed BTCUSDT 1m DEV source and excludes bars opening on/after 2024-07-01. | Archive set available Jan 2022 through Jun 2024; output has 445 rows. |
| LOW | `event_table.py:31-62` | Each event is normalized by spike-to-level distance; incomplete forward coverage is represented as `NOT_IN_DATA`. | Synthetic missing-minute case passes; DEV contained 445 complete windows. |
| LOW | `test_event_table.py:1-60` | Tests cover hand-computed event values, insufficient prior-day bars, four-hour horizon, missing data. | `4 passed`. |

No follow-up cards created.
