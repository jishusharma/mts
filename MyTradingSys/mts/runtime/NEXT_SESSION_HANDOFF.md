# NEXT SESSION HANDOFF
# Rewritten 2026-09-21T12:35Z by MTS-2026-09-21-0729Z.

STATUS: Loop running. Wrapper 4828, supervisor 13412, java 11404, lock 4828. Build PASS 12:23Z. start-trading-day.ps1 352EFC9A.

## QUEUE

Do not mirror the queue here. Single source:
  MyTradingSys/mts/research/BUGS.md

## FIRST ACTION NEXT SESSION

1. Run mts-live.
2. Read in one batch:
     Get-Content .\data\apparatus_log.txt -Tail 60
     Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 60
     Get-ChildItem .\data\snapshots -Filter 'BTCUSDT_*.json' | Sort LastWriteTime -Desc | Select -First 1
     Get-Content .\MyTradingSys\mts\research\BUGS.md -Tail 40
3. Read the queue from BUGS.md. Pick work.
4. Read MyTradingSys/mts/research/MODEL_ALIGNMENT_2026-09-21.md (delivered 2026-09-21).

## LANDED THIS SESSION (MTS-2026-09-21-0729Z)

B058 parts C+D. Part C live-observed 11:25:23Z: WAIT_PROOF (flow contradiction) on ct_short. Part D per-zone cooldown 900s wired, not observed.
B062 position-aware suppression. Verdict line gains pos=none|long|short. position.json direction + opened_utc + optional stop, target. Same-direction SETUP_FORMING suppressed when position open.
EXIT_HINT. Opposing candidate in range logs EXIT_HINT pos=X setup=Y zone=Z price=N nrr=R. No popup. Wired, not observed.
Stop and target from position.json feed the existing STOP_NEAR / TARGET_NEAR alerts. Launch-time -Stop -Target win when set.
tape-watch.ps1 history-on-start, 40 lines. Hash 61EC0CE0, 107 lines.
apparatus_fixes.md: log tail is not a health check. Loop-state claim requires wrapper PID + lock + log mtime in the same read.
live_session_protocol rule 15: no inferred levels. SCREENER levels are not signals. Prior-day POC/VAH/VAL not in conditions are SCREENER.
MODEL_ALIGNMENT_2026-09-21.md delivered. Five issues + pre-committed chain. Disk verdicts cited, web UNVERIFIED-WEB.
03_FILE_INDEX.md: MODEL_ALIGNMENT row; 16 pre-existing em-dashes normalized.

## RULE 32 OBSERVATIONS CARRIED

B058 part D per-zone cooldown - needs same-zone repeat WATCH or SETUP_FORMING.
B062 suppression - needs live SETUP_FORMING matching open position.json direction.
EXIT_HINT - needs position.json + opposing candidate in range.

## OPEN LOOP AT CLOSE

Journal 964 lines. Section 11 of DSA updated 12:35Z. Ledger logged 2026-09-21T12:35Z.

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Ledger is not truth. Files are truth.
- Rule 32: verdict-path change needs 3-snapshot proof.
- No receipt until the evidence command output is on disk.
- During loop lifecycle stages 1-3, do not run mode.ps1 (supervisor duplicate detection reduced).
- session_timing_rules.md is research-sourced. No TOM-NNN tags there.
- Journal and DSA timestamps must use (Get-Date).ToUniversalTime(). Local time with Z is wrong.
- Log tail is not a health check. Read wrapper PID + lock + log mtime together.
- No inferred levels. No angle-bracket placeholders in pasted blocks.

# END