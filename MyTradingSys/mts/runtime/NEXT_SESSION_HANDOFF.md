# NEXT SESSION HANDOFF
# Rewritten 2026-09-19T08:40Z by MTS-2026-09-19-0823Z.

STATUS: Loop running. Lock 15296, java 5928. No supervisor. Build PASS.

## QUEUE

Do not mirror the queue here. Single source:
  MyTradingSys/mts/research/BUGS.md

## FIRST ACTION NEXT SESSION

1. Start mts-live (if not already running).
2. Read in one batch:
     Get-Content .\data\apparatus_log.txt -Tail 60
     Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 60
     Get-ChildItem .\data\snapshots -Filter 'BTCUSDT_*.json' | Sort LastWriteTime -Desc | Select -First 1
     Get-Content .\MyTradingSys\mts\research\BUGS.md -Tail 40
3. Read the queue from BUGS.md. Pick work.

## LANDED THIS SESSION (MTS-2026-09-19-0823Z)

T032 WONTFIX (stale title; superseded by T036 and B044).
T036 CLOSED: topLongShortAccountRatio wired as oi_breakdown.topAccounts.
B044 WONTFIX: 4-model source validation + coordinator fact-check. Option C.
start-session.ps1 guard note closed as phantom (guard already at L46).
live_session_protocol rule 2 corrected: interactive throw does not abort a paste.
Read-anchor-before-compose rule added to live_session_protocol.
WORKER PROTOCOL W1-W5 added (evidence channel, receipt tags, no Confirmed).
EXTRACTION_TO_ALERT_AUDIT_2026-09-19.md: Phase 4 engine doc only, no code trace.
MTS_DICTIONARY source tag scheme (7 families).
B050 OPEN: buildStructure pivot dead code (swing zones never tighter than window).
B051 OPEN: state_code letter S not reconciled against long setups.
SESSION_RESUME triage: 3 RESOLVED, 1 FILED, 1 PHANTOM, 1 REFERRED, 1 PENDING, 1 OPEN-NEW, 2 DECISION.
LOOP_LIFECYCLE_DESIGN_2026-09-19.md: 4-stage plan for one-owner loop control.

## PENDING DECISIONS

SR-3 mode.ps1 refuse when supervisor present. Recommendation: do it (Stage 4 of loop design).
SR-4 atomic lock create. Recommendation: defer (Stage 2 of loop design, supervisor covers today).

## OPEN LOOP AT CLOSE

Build-Card SESSION / US_OPEN lines loaded at 07:48:30Z restart. Not yet
observed on a live alert card. No popup since restart; every cycle WAIT_RR.
First WATCH or higher card after boot will confirm. Unverified.

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Ledger is not truth. Files are truth.
- Rule 32: verdict-path change needs 3-snapshot proof.
- No receipt until the evidence command output is on disk.
- During loop lifecycle stages 1-3, do not run mode.ps1 (supervisor duplicate
  detection is reduced; mode.ps1 still kills).
- session_timing_rules.md is research-sourced. No TOM-NNN tags there.
- Journal and DSA timestamps must use (Get-Date).ToUniversalTime(). Local time with Z is wrong.

# END
