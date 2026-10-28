# SESSION RESUME
# Written 2026-09-17T13:53:50.1196933Z for continuation into a new chat.
# Source session: MTS-2026-09-17-1241Z

## ROLE
COORDINATOR. Same mission: live oversight, gap capture, code readiness.

## WHAT LANDED THIS SESSION
- live_session_log.md created. Append-only analytical log. 4 entries.
- tape-watch.ps1 created. Divergence classifier, 30s tick, popup on non-neutral.
- mts-watch.ps1 created. Full-state console feed + runtime_data\mts-watch.log.
- live_session_protocol.md created. 10 AI-side checks + mistake ledger.
- 03_FILE_INDEX.md: 4 rows added.
- session_log.json: task logged for attempt-number context at a zone.
- apparatus_fixes.md: pre-open playbook gap appended.

## OPEN CODE ITEMS (queued for after close)
- B043 open: supervisor double-start risk.
- Supervisor singleton lock: fix to loop-supervisor.ps1.
- mode.ps1 should refuse when supervisor present.
- Lock acquisition: atomic create (TOCTOU).
- buildStructure pivot detection dead code at MarketDataSnapshot.java ~L695-720.
- tape-watch duplicate line when snapshot does not change between ticks.

## OPEN DESIGN ITEMS
- Attempt-number context at a zone. No retest counter. Task logged.
- Multi-day swing ladder / CVD anchor / OI trajectory: schema gaps.
- day_type evidence: 1 of 3 snapshots collected (13:31). Need 2 more.
- I23 live: state S vs long setups, engine does not reconcile.

## LIVE STATE AT HANDOFF
- Price ~76313 (13:48:15 UTC). Session low 75975. Session high 76558.8.
- IB 75975 - 76558.8. IB window closes 14:00 UTC.
- day_type balance/provisional. Not to be trusted until 14:00.
- Engine direction: long. Top setup ct_long @ daily_val 76080.43 nrr 2.87.
- State A, bear=2 bull=2. Prior state S for 13 minutes.

## PROCESS
- Single chain: sup=32 wrap=16708 java=13144 lock=16708.
- tape-watch PID 636, mts-watch PID 16492.
- First read on continuation: Get-Content .\runtime_data\mts-watch.log -Tail 40

## RULES THAT APPLY
- USER.md binds.
- DSA_SESSION_PROMPT.md binds.
- live_session_protocol.md: 10 operational checks before any live claim.
- Do not run mode.ps1 while supervisor 32 is alive.
- Do not bare-kill java.


## TRIAGE 2026-09-19

Every item from SESSION_RESUME OPEN CODE ITEMS and OPEN DESIGN ITEMS.
Verified against BUGS.md, apparatus_fixes.md, source, and repository history.

| Item | Verdict | Evidence |
|---|---|---|
| SR-1 supervisor double-start / B043 | RESOLVED | BUGS.md B043 CLOSED 2026-09-17 |
| SR-2 supervisor singleton lock | RESOLVED | loop-supervisor.ps1 L71-86 startup lock; L114-117 duplicate wrapper detection |
| SR-3 mode.ps1 refuse when supervisor | DECISION NEEDED | mode.ps1 reads lock only (L20-38). No supervisor check. Design choice, not defect |
| SR-4 lock creation atomic (TOCTOU) | DECISION NEEDED | 0 hits. Supervisor duplicate detection may cover the race |
| SR-5 buildStructure pivot dead code | FILED B050 | MarketDataSnapshot.java L701-712; consumers confirmed |
| SR-6 tape-watch duplicate line | RESOLVED | BUGS.md T021 CLOSED 2026-09-18 |
| SR-7 attempt-number / retest counter | PHANTOM | 0 hits in BUGS.md, apparatus_fixes.md, Java, scripts. No receipt |
| SR-8 swing ladder / CVD anchor / OI trajectory | REFERRED | schema_v5.1.0_spec.md Open decisions is the tracking home |
| SR-9 day_type evidence 1/3 | PENDING | Field exists in snapshot but reads UNKNOWN / confidence none pre-13:30Z anchor. Original task was evidence collection (1/3 snapshots). Not closed. |
| SR-10 I23 state S vs long setups | OPEN-NEW | Different subsystem from B019/I23. B019 covers quad_classify direction vs setup. SR-10 covers state_code letter S vs long setups. No engine reconciliation found. File as B051. |

This file is now historical. Live queue is MyTradingSys/research/BUGS.md.

# END
