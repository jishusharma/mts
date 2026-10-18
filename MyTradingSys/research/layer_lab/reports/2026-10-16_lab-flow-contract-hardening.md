# Lab flow contract hardening (2026-10-16)

## Verdict

**BLOCKED**: the full prior regression set cannot complete in this sandbox: `scripts/dev/test_codex_run.py::TimeBoxTest::test_a_hung_sweep_is_cut_off_and_recorded_so_the_tick_can_go_on` fails while cleaning its temporary worktree. Windows returns `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process` for `%TEMP%\tmpgcqqivkd\wt`, followed by `[WinError 5] Access is denied`. The requested rule says not to mark the card done when a test cannot pass.

## Work checked

The requested hardening is present in the workspace and verified: `scripts/dev/lab_flow.py:40-47` includes nonempty `commands` and `tests` in `contract()`; `:91-101` pins later-stage dependency to the preceding card; `:184-193` rejects a report already receipted elsewhere and requires a card-id line; `:200-202` requires criterion evidence. Regressions are in `scripts/dev/test_lab_flow.py:150-180`. The four checks are documented under Evidence and advancement in `MyTradingSys/system/LAB_RECIPES.md:59-62`.

The pilot report's throwaway-repo reproductions document the pre-fix failures: G1 `gate()` and `problems()` returned no errors and contract hash stayed unchanged; G2 stage 2 remained runnable after clearing `depends_on`; G3 stage 2 accepted stage 1's report; G4 status-only lines were accepted (`MyTradingSys/research/layer_lab/reports/2026-10-16_claude-recipe-pilot.md`, Findings).

## Verification

- `pytest scripts/dev/test_lab_flow.py -q -p no:cacheprovider --basetemp F:/MTS/mts-codex-lab/.lab_pytest_run_20261016_flow` ? **20 passed**. Includes the four requested regression tests.
- `pytest scripts/dev/test_lab_flow.py scripts/dev/test_tasks.py scripts/dev/test_codex_run.py scripts/dev/test_codex_pack.py -q -p no:cacheprovider --basetemp F:/MTS/mts-codex-lab/.lab_pytest_run_20261016_confirm` ? **107 passed, 237 subtests passed, 1 failed** in 70.34s. The single failure is the temp-worktree cleanup error above.
- `lab_flow.accepted` ? `recipe-pilot-1-map=True`, `recipe-pilot-2-challenge=True`; both `gate()` calls returned `[]`. Existing receipts were not changed.
- The first pytest invocation used the host temp root and could not access it; rerunning with an isolated workspace basetemp yielded the results above.

## Findings

| Severity | Location | Result |
|---|---|---|
| HIGH | `scripts/dev/lab_flow.py:40-47`, `scripts/dev/test_lab_flow.py:150-158` | Commands/tests are contract-bound when nonempty; mutation is rejected. |
| MED | `scripts/dev/lab_flow.py:91-101`, `scripts/dev/test_lab_flow.py:161-165` | Stage 2 dependency must exactly name stage 1. |
| MED | `scripts/dev/lab_flow.py:184-193`, `scripts/dev/test_lab_flow.py:168-172` | Reused reports and missing card identity are rejected. |
| LOW | `scripts/dev/lab_flow.py:200-202`, `scripts/dev/test_lab_flow.py:175-180` | Criterion status lines without evidence are rejected. |
| BLOCKER | `scripts/dev/test_codex_run.py` test named above | Temporary worktree cleanup is denied by Windows sandbox access/lock (`WinError 32`, then `WinError 5`). |

No ship or git operation was run. The runner must resolve or rerun the cleanup test in an environment where its temporary worktree can be removed before this card is marked done.
