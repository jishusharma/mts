# B089 - bugs filed only in BUGS.md are invisible to the scheduler

Status: CLOSED. Severity: MED. Opened 2026-10-03.

## Defect

pick_task.py reads BUILD_PIPELINE.md only (PIPE constant). BUGS.md
is read once as a status lookup keyed by id, for ids already present
in the pipeline. An OPEN bug that exists in BUGS.md and has no
pipeline row is not a candidate at any wave and is never picked by
any wake.

Consequence: a bug filed from a scheduler session or a live incident
sits unreachable until a human adds a pipeline row by hand.

## Evidence

- B088 filed 2026-10-03 is OPEN in BUGS.md, no pipeline row.
  Select-String BUILD_PIPELINE.md for B08[6-8] returns zero
  matches (2026-10-03T11:14Z read).
- B086 and B087 before they were closed by direct prompt: same
  pattern, no pipeline row, never picked.
- pick_log.jsonl: picks are R4-T2, B070 (x4), TF1. All of these
  have pipeline rows. No BUGS-only row appears.
- pick_task.py: parse_pipeline reads PIPE; skip_reason checks
  bugs[rid] only when the id is already in a pipeline row.

## Fix (Claude decides)

(A) pick_task.py sweeps BUGS.md for OPEN ids not present in any
    pipeline wave, treats them as pickable at a default wave.
(B) scripts/sched/backfill_pipeline.py, operator-run after each
    bug is filed, appends a wave-9 row per OPEN bug with no
    pipeline row.
(C) Discipline: every bug-file step also writes a pipeline row.
    No code; relies on humans.

Chosen fix must include a test that fails on the pre-change
pick_task.py at least once.

## Receipt

2026-10-03 CLOSED. Shape (A): automatic on every wake, no human step; (B) and (C) each need a person to act after every filing, which is the step that failed for B086 to B089 and the machine is not on 24/7.
Shape (A). scripts/sched/pick_task.py:74 parse_bug_rows, :88 sweep_rows (OPEN/IN-FIX register ids with no pipeline row become QUEUED rows of wave max+1, file order, source=bugs), :285 candidates = pipeline rows + swept rows; next_task.json, pick_log and the PICK line carry source; the prompt names BUGS.md instead of a pipeline row. Tests: test_pick_task.py test_17 to test_22 (17, 18, 19, 21, 22 fail on pre-change code). BUILD_PIPELINE rows 0.4 and 0.5 LANDED for the record. Session MTS-2026-10-03-1230Z-CLI-BLD-fix-b088-b089.

# END
