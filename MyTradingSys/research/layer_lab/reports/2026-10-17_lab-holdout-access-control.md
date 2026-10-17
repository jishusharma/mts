# Lab holdout access control

BLOCKED - implementation and tests are complete; task completion requires an independent reviewer stamp that is not present.

Build result: `scripts/dev/lab_flow.py` and `scripts/dev/test_lab_flow.py`; `python -m pytest -q scripts/dev/test_lab_flow.py --basetemp F:/MTS/mts-codex-lab/.pytest-tmp -p no:cacheprovider` — **27 passed**.

## What changed

- `scripts/dev/lab_flow.py:36-93`: data files inside `DATA_ROOT` are verified by content before return. NPZ `t`, CSV timestamp columns, and CSV members in ZIP files are supported. Unsupported extensions and absent/empty axes fail closed. Unix seconds are normalized to milliseconds before the `2024-07-01T00:00:00Z` cutoff check. Repository files receive path checks only; content timestamp checking covers `DATA_ROOT` files.
- `scripts/dev/test_lab_flow.py:250-279`: tests cover renamed NPZ content with a post-cutoff timestamp, unsupported `.parquet`, and a 2025 seconds-epoch CSV.
- Fail-first evidence: the unsupported-extension test failed against the prior implementation because `safe_file` returned without raising. With seconds normalization temporarily removed, `test_seconds_epoch_after_cutoff_is_refused` failed because `safe_file` did not raise. Restoring the fix made the full test file pass.

## Findings

| Severity | Evidence | Finding | Status |
|---|---|---|---|
| HIGH | `scripts/dev/lab_flow.py:36-93`; `scripts/dev/test_lab_flow.py:250-279` | Renamed/copy files in `DATA_ROOT` with later bars are rejected by timestamp; unsupported formats and second-based timestamps cannot bypass the bound. | MATCH |

## Blocker

`python scripts/dev/tasks.py done lab-holdout-access-control --result "27 passed; MyTradingSys/research/layer_lab/reports/2026-10-17_lab-holdout-access-control.md"` is gated by the card note: it requires `REVIEWED: <reviewer> <date>` for this CRUCIAL/C2 card. The note says independent Claude review found two defects and that cross-vendor review is owed. No independent reviewer has supplied a stamp, so the card must remain not done.
