# T057 - SIMPLIFY ARCHITECTURE, OPTIMISE, DECLUTTER

Convention: one item, one doc. Verbatim ask at top. Updates appended, newest last.
Related: DEV_VELOCITY_AUDIT.md (2026-09-27, 12 findings), T056 Qwen audit program (feeds this), NEXT_SESSION_PLAN W5.

## VERBATIM ASK (operator, 2026-09-28)
Where we are on simplification of the MTS architecture and optimization and decluttering stuff?

## STATE
2026-09-28 filed (supervisor). No item existed; only DEV_VELOCITY_AUDIT covered part of it.
Audit follow-up: done - #1 false BLOCKED on new files (CREATE:), #2 compile gate in verify, #4 SCOPE lint,
#5 run_all_tests.py, #7 partly (generated STATUS.md). Open - #3 now 0 pending .new but 60 untracked .pre_*
backups; #9 backup_session/ 139M inside repo; #12 no queue stats; handoff/doc sprawl (240 tracked .md);
Dumps/ 1.1G; misplaced code (e.g. runtime/backtest_oi_delta_4state.py); rejected_*/qwen_raw_* leftovers.
Plan (rules: archive, never delete without operator OK; one area per commit; gates re-run):
1. T0 inventory (audit_rotation.py --t0): .pre_* whose file is committed since, rejected/raw leftovers,
   docs referenced by nothing, duplicate docs, code outside its area, big dirs. -> research/audits/T0_CHECKS.md
2. Operator approves the list once -> move to an archive folder outside the repo (reversible).
3. Doc map: one README per area + STATUS.md; collapse handoff docs into STATUS/SUPERVISOR_LOG.
4. Architecture: Qwen A6 drift audits per area -> supervisor proposes merges/moves as specs.
