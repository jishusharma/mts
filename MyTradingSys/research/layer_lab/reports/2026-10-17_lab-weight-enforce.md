Changed files + test output: `scripts/dev/tasks.py` now validates the full `REVIEWED: <who> <YYYY-MM-DD>` stamp; `scripts/dev/test_tasks.py` covers the CLI gates; `MyTradingSys/system/TASK_REFINEMENT.md` states the planner/reviewer ownership rule. Tests: `python scripts/dev/test_tasks.py` — 47 tests, OK. `python scripts/dev/tasks.py check lab-weight-enforce` — ready and passes.

What was checked or run:

- `scripts/dev/tasks.py:553-578`: crucial/critical weight or class C2/C3 requires a reviewer stamp; `done` also requires a non-empty receipt. The existing WEIGHTS tuple at line 61 and OPUS-needs-crucial rule were retained.
- `scripts/dev/tasks.py:579-615`: `cmd_take` and `cmd_done` call `review_gate` before changing card state.
- `scripts/dev/test_tasks.py:554-606`: tested missing stamp refusal via both CLI commands, missing finish receipt for C2, stamp format, class gating, and routine/important/C0/C1 passes.
- `MyTradingSys/system/TASK_REFINEMENT.md:81`: documents reviewer/planner ownership and requirements.
- Commands: `python scripts/dev/test_tasks.py`; `python scripts/dev/tasks.py check lab-weight-enforce`.

Findings:

| Severity | File:line | Finding | Evidence |
|---|---|---|---|
| LOW | `scripts/dev/tasks.py:553` | The prior stamp check accepted any single character after `REVIEWED:`. It now requires a reviewer token and ISO date. | Test `test_reviewed_stamp_requires_reviewer_and_iso_date` rejects `REVIEWED: reviewer` and accepts `REVIEWED: reviewer 2026-10-18`. |
| LOW | `scripts/dev/test_tasks.py:575-606` | Helper-only tests did not prove command enforcement. Added CLI tests that exercise `take` and `done`. | `python scripts/dev/test_tasks.py` — 47 tests, OK; both commands preserve `ready` state on refusal. |

Follow-up cards created: none.
