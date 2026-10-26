# MTS-2026-10-02-1900Z-CLI-ANA-scheduler-plan
surface: CLI
host: JIS-NB
account: A
model: claude-sonnet-5-5
role: ANA
branch: fast-track
branch_alias: none (brief named claude/scheduler-plan; not created, tree runs the live testnet system and CLAUDE.md fixes branch fast-track)
predecessor: none
lanes: none (no subagents)
started: 2026-10-02 19:00Z
ended: 2026-10-02 19:30Z (approx)
status: closed
commits: 368397b
handoff: none; follow-ups below

## Scope
Design plan only: MyTradingSys/research/_archive/loose_2026-10/SCHEDULER_PLAN_2026-10-02.md answering the eight questions of
SCHEDULER_DESIGN_2026-10-02.md section 8 (bullet 1 split into two to reach eight).

## Outcome
- Stack: Tier-1 detectors (8, free, 15 min) -> one Haiku worker (event + digest modes) -> Sonnet on ESCALATE -> Opus only on safety diffs.
- Expected spend $3.65/month (ASSUMED event rates); unbounded flapping exhausts $20 in 8.3 days (Haiku) / 1.3 days (Sonnet).
- Paths: existing ones Test-Path True; scripts/sched/*, worker_prefix.md, runtime/sched/, sched_reports/ listed as NEW.

## Follow-ups
- Operator: is the $20 credit shared with scripts/manager/mts-manager.ps1 runs?
- Dumps/SESSION_PASTE.txt is 150,554 bytes, already over the 80 KB check.
- Verify Build-Check exit codes, run_all_tests --quick runtime, claude flag spellings before any build.
