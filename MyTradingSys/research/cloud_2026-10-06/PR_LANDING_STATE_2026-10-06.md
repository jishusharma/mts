# Cloud PR landing state - 2026-10-06 (base: fast-track 5f1e8bb)

Replaces the pipeline doc (old PR 1) and Wave 1 readiness report (old PR 3), which were cut from `main`
(199 commits behind `fast-track`) and described stale state. This file records only what was verified on `fast-track`.

## Draft PRs, all based on `fast-track`, none merged
| PR | Content | Verified |
|----|---------|----------|
| 2 | Two tests for book_imbalance 0.0 = no data. Fix already on fast-track (`runtime/math_object_builder.py`, `_book != 0.0`). | 51 tests pass; zero test fails without the guard |
| 4 | Fabio v3 core tests converted to unittest style, wrapper exports; restored missing `import pytest` in `test_manage.py`. | 129 pass, 4 skipped (pytest); layer step 5b passes |
| 5 | `mts runner` and `mts orphans` verbs. `runner` stays a narrow verb; `mts guard` also starts live_runner_cli plus loss monitor and orderflow. | static test passes; PowerShell parse check is a DESKTOP step |
| 6 | Consensus writer + RSI observation promoted from `.new`, with tests; 3m/1d TF map additions. | layer tests pass |
| 7 | `runtime/test_update_market_state.py` (10 tests). Java tests already on fast-track, so not duplicated. | 10 pass; not collected by the quick gate |

## Quick-gate failures that are NOT from these PRs (same on fast-track in the cloud container)
- Step 3c: guide paths `execution\plans\`, `journal\`, `halt_history\` are gitignored dirs absent from a fresh clone.
- Step 4: `test_go.py` (2) and `test_autogo.py` (1) fail on Linux. Re-check on the desktop.

## Still open
- `proof_direction_cases.py.new` is still staged (see STATUS.md); `test_quad_classify` and `test_regime_classifier` are already promoted on fast-track.
- Consensus writer is not wired into live_runner_cli/auto_trader; that needs an execution/alerts owner claim in SUPERVISOR_LOG.
