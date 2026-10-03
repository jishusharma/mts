# B088 - session-id surface code split

Status: OPEN. Severity: LOW. Opened 2026-10-03.

## Defect

pick_task.py writes session id MTS-<date>-<time>Z-CL-BLD-<slug>
  (pick_task.py:270).
go.py writes session id MTS-<date>-<time>Z-CLI-BLD-<slug>
  (go.py:33).
SURFACE_POLICY.md section 4 lists the surface codes as
CLD APP CLI LAP DSA ASK. There is no CL.

Every scheduler-generated session id therefore carries a code
outside the policy, and the two files disagree on which.
Origin: the DSA prompt that built the dispatcher used CL-BLD.

## Second item in the same row (Claude decides)

Cooldown default 6h at pick_task.py:123 (env MTS_PICK_COOLDOWN_H).
No source on disk names 6h. Operator rule from MTS-2026-10-03-0430Z
session: numeric values need a source or an operator ruling.
Decide: document the 6h as an operator default, replace it with a
sourced number, or make it required (no default).

## Fix (Claude decides)

1. One code, CLI, in both files. Do not change SURFACE_POLICY.
2. Resolve the cooldown source.

## Receipt

-

# END
