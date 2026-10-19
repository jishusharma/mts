# lc-ladder-dev report - 2026-10-19

**BLOCKED - preregistered LC3 DEV window is outside the permitted data range.**

## What was checked

- Read `MyTradingSys/research/levels_confluence_2026-10-14/PLAN.md` (LC3 and data-window lines 58-70), `separation.md` (LC3 registration lines 26-32), `event_table.py`, `levels.py`, `levels_sizing_2026-10-14/METHOD.md`, and `MyTradingSys/backtest/fees.py`.
- Inspected the permitted local cache before declaring data unavailable. The command loaded only `t` arrays from `F:/MTS/data/bigtrade/cache/perp/{klines_1m,klines_15m,klines_1h}.npz`, counted timestamps strictly before 2024-07-01, and printed first/last allowed opens. It found 1,313,280 1m bars (2022-01-01 00:00 through 2024-06-30 23:59 UTC), 87,552 15m bars, and 21,888 1h bars. The 1m ZIP archive listing likewise ends at `BTCUSDT-1m-2024-06.zip`.
- No event-table rows or bars at/after 2024-07-01 were read. No simulation, tests, or trial variants were run.

## Finding

| Severity | Evidence | Finding | Disposition |
|---|---|---|---|
| HIGH | `PLAN.md:68-70` specifies DEV 2024-12..2025-03; inspected cache has allowed bars only through 2024-06-30 (command described above). | There is no admissible bar overlap with the preregistered LC3 DEV window. Running on 2022-01..2024-06 would silently substitute a different development period, while reading the preregistered period violates the explicit `< 2024-07-01` bar cutoff. | BLOCKED pending a re-scoped preregistration or an authorized DEV window. No substitute period was used. |
| MED | `separation.md:28-30` selects `E1_rsi_holds_40_60` and `E4_outer_band` as candidate filters, and explicitly says no LC3 simulation is included. | The preregistration exists, but is not a substitute for the underlying bars needed to simulate exits, scale-ins, stops, and fees. | No results inferred from LC2 summary statistics. |

## Deliverables and close status

No `ladder.py`, `test_ladder.py`, `ladder_dev.md`, or `frozen_rule.json` was produced because the required registered bars cannot be legally evaluated in this run. `TRIALS.md` was not changed because no LC3 variant was run. The requested pytest command was not run: there is no new ladder implementation to test and the data-window conflict blocks implementation against the registered study. The card was **not** marked done, as required for BLOCKED.
