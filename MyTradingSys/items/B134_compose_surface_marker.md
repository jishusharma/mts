# B134 - compose() emits prose surface line, not the SURFACE marker check 13 requires

Status: OPEN. Severity: LOW. Opened 2026-10-05.
Filed by: 
MTS-2026-10-04-1325Z-DSA-COO

## Defect

scripts/sched/pick_task.py compose() L257 emits the surface statement as
prose:

    "Surface: Claude Win App, Code mode. Where the App cannot reach ..."

scripts/dev/prompt_check.ps1 check 13 (landed at 81c7e9f, B133 part 1)
requires exactly one line matching "SURFACE: APP" or "SURFACE: CLI". Zero
markers is a FAIL.

Consequence: any composed prompt run through prompt_check fails check 13.
The gate that B133 added to catch surface mistakes fails the scheduler own
output.

## Evidence

- pick_task.py L257-258 (compose() header).
- prompt_check.ps1 header L31: check 13 rule, "exactly one line SURFACE: APP
  or SURFACE: CLI; zero or two (or more) markers FAIL".
- prompt_check.ps1 L332: check 12 short-circuits when the marker is not APP;
  check 13 runs on the marker count.

## Fix shapes

A. compose() emits "SURFACE: APP" on its own line; the prose line stays
   or is dropped.
B. check 13 accepts the compose prose line "Surface: Claude Win App" as
   an APP marker.

A is one line in pick_task.py. B is one line in prompt_check.ps1.

## File set

pick_task.py (shape A) or prompt_check.ps1 (shape B).

B095 also edits pick_task.py. Sequence behind B095 or land together.

# END
