# Lab Report: Gap G6 Trial Ledger Builder

- Date: 2026-10-18
- Task: `gap-g6-trial-ledger`
- Author: Gemini (Google AI Pro, JIS-NUC)
- Command / Tool: `python scripts/dev/trial_ledger.py`

## Purpose
Build an append-friendly `MyTradingSys/research/TRIAL_LEDGER_BUILT.csv` aggregating all historical trial registries across the codebase, while keeping `MyTradingSys/research/TRIAL_LEDGER.csv` strictly untouched. Also create the skeleton `MyTradingSys/research/holdout_reads.csv` for tracking holdout looks.

## Registries Discovered and Row Counts
Total registries discovered: 9
- `MyTradingSys/research/candle_patterns_2026-10-04/TRIAL_REGISTRY.csv`: 132 rows
- `MyTradingSys/research/fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY.csv`: 50 rows
- `MyTradingSys/research/fast_track_2026-09-27/bt_runs/TRIAL_REGISTRY_SMOKE.csv`: 64 rows
- `MyTradingSys/research/layer_lab/candle_close_2026-10-14/TRIAL_REGISTRY.csv`: 126 rows
- `MyTradingSys/research/levels_sizing_2026-10-14/TRIAL_REGISTRY.csv`: 8 rows
- `MyTradingSys/research/mfe_exit_2026-10-13/rerun_dev_2026-10-17/TRIAL_REGISTRY.csv`: 51 rows
- `MyTradingSys/research/mfe_exit_2026-10-13/TRIAL_REGISTRY.csv`: 102 rows
- `MyTradingSys/research/published_strats_2026-10-13/TRIAL_REGISTRY.csv`: 133 rows
- `MyTradingSys/research/volume_2026-10-09/TRIAL_REGISTRY.csv`: 613 rows

**Total Rows Processed:** 1,279 rows

## Output Files Created
1. `MyTradingSys/research/TRIAL_LEDGER_BUILT.csv`
   - Fields: `study,variant,date,split,verdict`
   - Row count: 1,279 rows (+ 1 header row = 1,280 lines)
   - Deterministic stable sorting by `(study, date, variant, file, idx)`.
2. `MyTradingSys/research/holdout_reads.csv`
   - Fields: `timestamp_utc,study,holdout_window,accessor,reason,verdict`
   - Skeleton header initialized.

## Verification
- Unit test suite in `scripts/dev/test_trial_ledger.py`: 3 passed.
- Red test before build confirmed (missing module / fail first).
- Hand-kept `MyTradingSys/research/TRIAL_LEDGER.csv` verified byte-identical.
