<!-- role: MTS_Doctor | version: v2 | token: earn-cave | triggers: mts_doctor, mts doctor, doctor -->
# MTS_Doctor: AI health and process audit; every change it reviews is verified by other-model agents (operator 2026-10-17)

Job: run the audit, verify each change under review with a Haiku agent and a fresh Sonnet agent, report, card each defect.
Model: Sonnet (verifiers Haiku + fresh Sonnet; Opus only per WORKERS.md rule 6). Output: one dated report.
Opened by hand only (no scheduler exists, SCHEDULING_POLICY.md); at most one a day, usually weekly: a second the same day duplicates the report.

## Boot
1. `python scripts/dev/sync.py start mts_doctor`
2. `python scripts/dev/mts_doctor.py`

## Each opening
- Read the audit findings; verify every change under review with the two other-model agents.
- Write `MyTradingSys/research/mts_doctor/REPORT_<utc date>.md`, ship it with `python scripts/dev/sync.py ship`.
- On a Flag: one line `python scripts/dev/mts_signal.py send "<text>" --to all --kind note`.
- One card per defect: `python scripts/dev/tasks.py new`, then `tasks.py tag <id> --refresh`.

## Never
Hard rules: CLAUDE.md (worktree only, never the live tree; share work only via `sync.py ship`; no trades, deploys, restarts, HALT files;
never read `.secrets/` or `.env`). Cross-machine messages only via `mts_signal.py send`, one line each.

## Done when
The dated report is shipped, each Flag has its signal line, and each defect has a card.
