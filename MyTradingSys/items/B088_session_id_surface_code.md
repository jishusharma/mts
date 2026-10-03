# B088 - session-id surface code split

Status: CLOSED. Severity: LOW. Opened 2026-10-03.

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

2026-10-03 CLOSED. Part 1: one builder, code CLI, in pick_task.py; go.py imports it. Part 2: the 6h had no source; replaced by the existing stale-session window (check_sessions.MAX_OPEN), so a picked row is presumed dead on the same clock that flags its session record. A required value (no default) would stop every tick.
scripts/sched/pick_task.py:44 SURF, ROLE = CLI, BLD; :156 session_id() is the one builder (used :308); go.py:28 imports it, go.py:65-67 launches an inherited pre-B088 -CL- name as -CLI- and rewrites the prompt line. Cooldown: pick_task.py:149-153 default = check_sessions.MAX_OPEN (24h stale-session window, SCHEDULER_PLAN_2026-10-02.md:147; imported pick_task.py:31); env MTS_PICK_COOLDOWN_H still overrides; the unsourced 6h is gone. Tests: test_pick_task.py test_14, test_15, test_16; test_go.py test_8, test_9 (test_14, test_15, go test_8, go test_9 fail on pre-change code). Session MTS-2026-10-03-1230Z-CLI-BLD-fix-b088-b089.

# END
