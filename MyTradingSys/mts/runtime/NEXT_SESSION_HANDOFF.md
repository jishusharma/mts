# NEXT SESSION HANDOFF
# Rewritten 2026-09-22T18:45Z by MTS-2026-09-22-1737Z.

STATUS: Loop left running. Build PASS 18:45:30Z. Position none. Sidecar restarted. PS7 7.6.6 side-by-side; five spawn sites migrated to pwsh, but running supervisor 11348 and wrapper 9636 are still 5.1. Next natural restart picks up pwsh.

## QUEUE

Single source: MyTradingSys/mts/research/BUGS.md

Open: B058 (part D needs live tape), B059, B062, B063, T034 (output type pending), T035, T037, T038, T039, T040.
Closed 2026-09-22: none.

## FIRST ACTION NEXT SESSION

1. Confirm loop is up:
     Get-ChildItem .\data -Filter "*.lock*"
     Get-CimInstance Win32_Process -Filter "Name='java.exe' OR Name='pwsh.exe'" | Select-Object ProcessId, Name, CommandLine
2. Batch reads:
     Get-Content .\data\apparatus_log.txt -Tail 60
     Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 60
     Get-ChildItem .\data\snapshots -Filter "BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
     Get-Content .\MyTradingSys\mts\research\BUGS.md -Tail 40
3. Confirm sidecar mts-tape running.
4. Run Build-Check under pwsh to verify migrated scripts:
     pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Build-Check.ps1

## LANDED THIS SESSION (MTS-2026-09-22-1737Z)

NEXT_SESSION_HANDOFF rebuilt.
SESSION_MANIFEST: operator_reminders.md added.
session_log.json: two entries (91->93).
DSA section 11 amended at close.
T039 sweep: 8 item docs (B058, B059, B062, T034, T035, T037, T038, T039). 10 items total.
Build-Check enforcement: OPEN/IN-FIX/BLOCKED rows need items/ file. Regex B-or-T. 63->103 rows.
Journal correction: 5 commits from 1215Z logged.
W1 dispatch file created.
Sidecar restarted.
PS7 7.6.6 installed side-by-side. 5 spawn sites migrated to pwsh. WinForms, mvn, pytest verified in pwsh.
Build-Check scan widened to runtime/*.md.

## OPEN LOOPS AT CLOSE

PS7 Part 2 (loop restart under pwsh) not forced. Supervisor 11348 and wrapper 9636 are 5.1.
Operator PowerShell window still 5.1. New pwsh window or profile change for future sessions.
T034 output type decision owed by operator (boolean / strength / both).
W2-W5 divergence dispatch files not written; only W1 exists.

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Ledger is not truth. Files are truth.
- Rule 32: verdict-path change needs 3-snapshot proof.
- No receipt until the evidence command output is on disk.
- Log tail is not a health check. Read wrapper PID + lock + log mtime together.
- No inferred levels. No angle-bracket placeholders in pasted blocks.
- Loop is not stopped at session close. Operator runs stop-day.ps1 before powering off.

# END
