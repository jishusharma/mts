BLOCKED

## What was checked
- Read `MyTradingSys/system/LAYER_LAB.md` lines 51-55 and 107-118. It limits audit writes to `research/layer_lab/` and `system/tasks/`; an audit output elsewhere is OUT_OF_SCOPE. The card requires a new file at `MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/session_timing.md`, outside those paths.
- Read `MyTradingSys/system/layer_index.json` lines 416-439. `session_timing` has two indexed result directories (`t087_session_levels_2026-10-09`, `eur_low_us_sweep_2026-10-14`) and an empty ledger list.
- Read `MyTradingSys/backtest/layers/FORMULAS.md` sections 13, 15, 16; indexed result files `t087_session_levels_2026-10-09/RESULT.md`, `eur_low_us_sweep_2026-10-14/RESULT.md`, their summary JSON files, and `_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md`.
- No DEV bars were opened. The task’s headline result reports contain aggregate summaries, not per-trade ledger rows; the indexed ledger is empty. A raw independent recount of mean returns, fee netting, and split metrics cannot be proven from those aggregates alone. User instruction prohibits reading bars after 2024-07-01, so the full-window result files cannot be independently replayed here.

## Findings

| Severity | File:line | Finding | Evidence / status |
|---|---|---|---|
| HIGH | `MyTradingSys/system/LAYER_LAB.md:107-109` | Requested task artifact is outside allowed write locations for an audit card. | Writing the required file would make the run OUT_OF_SCOPE. BLOCKED. |
| HIGH | `MyTradingSys/system/layer_index.json:428-431` | No indexed ledger is available for a raw trade recount. | `ledger: []`; only two result directories are indexed. BLOCKED for the requested independent recount. |
| MED | `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:7-24`; `summary.json` | Headlines include n, win/target/stop proportions, net mean and t-stat across cells, but source contains only aggregate counts/summary values. | Quoted values are visible, but no per-trade rows to independently recompute mean R or fee-net result. NOT_IN_DATA. |
| MED | `MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:20-44`; `results.json` | Headlines include counts, break rates, split rates, short mean returns and ladder returns. | Aggregated report/JSON lacks trade-level outcomes; only DEV bars before 2024-07-01 may be read. Independent raw replay is blocked. NOT_IN_DATA. |
| LOW | `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:15-19` | Turn-of-candle citation summarizes T055 C3 OOS metrics but is not one of the two indexed result paths and has no ledger attached in the index. | Reports OOS gross approximately zero and net -0.1201%; cannot independently recount from this summary. NOT_IN_DATA. |

## Completion
The requested re-derive file was not written because the lab protocol explicitly disallows that destination for an audit run. `tasks.py done` was not run because the task instructions say not to mark a blocked card done. No recompute script was written; no raw-ledger proof could be produced from the indexed inputs without violating scope/data restrictions.
