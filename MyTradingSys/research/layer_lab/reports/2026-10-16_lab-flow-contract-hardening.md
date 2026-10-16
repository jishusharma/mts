# BLOCKED — lab flow contract hardening (2026-10-16)

## Verdict

BLOCKED: implementation and lab-flow tests pass, and both existing recipe-pilot receipts remain accepted. The required broader regression suite has one repeatable failure in an unrelated Windows cleanup test, so the card's “104 prior tests ... stay green” condition is not met. Card not marked done.

## Work and evidence

- `scripts/dev/lab_flow.py:40` adds nonempty `commands` and `tests` to the flow contract. `scripts/dev/lab_flow.py:75` rejects command/test drift and requires the exact previous stage dependency. `scripts/dev/lab_flow.py:175` rejects report reuse, requires the card id in a report line, and requires path:line or fenced-command evidence tokens.
- `scripts/dev/test_lab_flow.py:150`, `:161`, `:168`, and `:175` add the four regression cases. Before implementation, `pytest scripts/dev/test_lab_flow.py -q --basetemp .pytest-temp` showed all four new tests failing and the other 16 passing. After implementation, `pytest scripts/dev/test_lab_flow.py -q --basetemp .pytest-temp -p no:cacheprovider` passed: 20 passed.
- Existing pilot receipts: `recipe-pilot-1-map=True`, `recipe-pilot-2-challenge=True`, verified with `python -c "import sys; sys.path.insert(0, 'scripts/dev'); import tasks, lab_flow as f; cards=tasks.load_all(tasks.REPO); ids=['recipe-pilot-1-map','recipe-pilot-2-challenge']; print({cid: f.accepted(tasks.get(tasks.REPO,cid), tasks.REPO) for cid in ids})"`.
- Documentation at `MyTradingSys/system/LAB_RECIPES.md:59` describes all four checks.
- Broader command: `pytest scripts/dev/test_lab_flow.py scripts/dev/test_tasks.py scripts/dev/test_codex_run.py scripts/dev/test_codex_pack.py -q --basetemp .pytest-temp`. Result: 107 passed, 1 failed, 235 subtests passed. The failure is `scripts/dev/test_codex_run.py::TimeBoxTest::test_a_hung_sweep_is_cut_off_and_recorded_so_the_tick_can_go_on`; it also fails when run alone because its `TemporaryDirectory` cleanup cannot remove `wt` (`PermissionError: [WinError 32]`, directory in use; cleanup then reports `WinError 5`). No unrelated test or process code was changed.

## Findings

| Severity | File:line | Result | Evidence | Proposed fix |
|---|---|---|---|---|
| HIGH | `scripts/dev/lab_flow.py:40` | MATCH | Nonempty run commands and build tests now affect the contract and card fields are checked against them. | None. |
| MED | `scripts/dev/lab_flow.py:75` | MATCH | Later stage `depends_on` must equal the prior recipe card id. | None. |
| MED | `scripts/dev/lab_flow.py:175` | MATCH | Reused report paths are refused; report must name its card id. | None. |
| LOW | `scripts/dev/lab_flow.py:175` | MATCH | Status-only report is refused unless it carries enough path:line or fenced-command tokens for the criteria. | None. |
| MED | `scripts/dev/test_codex_run.py:580` | BLOCKED | Its temp-directory cleanup reproducibly fails on a locked `wt` directory in this Windows sandbox; this prevents the full specified suite from being green. | Re-run the existing test in an environment that can close/remove its temporary worktree, then rerun the suite. |

