# PROCESS MANAGEMENT AUDIT - 2026-09-17
# Written by MTS-2026-09-17-1142Z. For new session to investigate.
# Scope: supervisor, loop wrapper, lock, stop paths.

## WHY THIS EXISTS

Session MTS-2026-09-17-1142Z ended with two java datafeed processes
running at 18:07:10 IST, same second. Clean restart sequence had been
followed. Cause: operator ran mode.ps1 while supervisor was up. Both
started a loop inside the same lock-read window.

## WHAT THE LOCK DOES (verified)

- File: runtime_data\apparatus.lock
- Format: "<PID> <epoch_seconds>" (start-trading-day.ps1 L278)
- Writer: start-trading-day.ps1 L250-279
- Readers: mode.ps1 L21-31, stop-day.ps1 L10, supervisor L19
- Stale rule: lock older than 600s auto-clears (start-trading-day.ps1 L265)
- Lock removed on clean stop (start-trading-day.ps1 L631, L643)

## GAP 1 - SUPERVISOR HAS NO SINGLETON LOCK (confirmed)

File: scripts\core\loop-supervisor.ps1
Evidence: L1-86. The supervisor checks the loop's lock file at start.
It never checks for another running supervisor. Nothing prevents:
  Start-Process loop-supervisor.ps1   (twice)
Two supervisors would each restart the loop independently. The lock
does not help because supervisors do not use the lock to gate
themselves; they use it only to decide if a wrapper is alive.

Recommendation: add a supervisor lock file runtime_data\supervisor.lock with
PID + epoch. Second launch aborts. Same pattern as apparatus.lock.

## GAP 2 - STARTUP GRACE IS A RACE WINDOW (confirmed)

File: scripts\core\loop-supervisor.ps1 L69-86 and L108-153.
At startup, if the lock has a live PID, the supervisor enters a
RestartGraceSec window (default 180s, our runtime uses 90s). During
that window it will not restart a dead wrapper. After the window it
will. If mode.ps1 is run by hand in that same window and the lock is
not yet written by the wrapper, both start.

The 4-second window we saw today:
  12:32:51 mode.ps1 writes lock PID 8828
  12:32:55 supervisor starts wrapper PID 14992 (supervisor lost the race)
Result: two java at 18:03:11 IST.

Recommendation: mode.ps1 should refuse to start if a supervisor
process is present. Or the supervisor should be the only entry point
for starting the loop. Pick one. Not both.

## GAP 3 - TWO DIFFERENT LOCK ACQUISITION PATHS

File A: scripts\core\mode.ps1 L21-36
File B: scripts\core\start-trading-day.ps1 L250-279
Both read the same lock file. Both check the PID with
Get-Process -Id. Neither uses an atomic create. A TOCTOU window
exists between Test-Path and Set-Content. In practice the window is
milliseconds. Today it was hit because two callers ran in the same
4-second span from different parents.

Recommendation: use New-Item -ItemType File with -ErrorAction Stop as
an atomic create. If it exists, refuse. Only after acquisition, write
PID. This closes the TOCTOU.

## DOC MISMATCH 1 - STOP FLAG WAIT TIME

COMMANDS.md L107: "Wait 35 seconds. The supervisor exits on its next
check."
Actual: CheckIntervalSec default is 30 (loop-supervisor.ps1 L7).
COMMANDS.md is wrong by 5 seconds. Cosmetic. Recommend fixing to 30
or to "poll until the supervisor process is gone" (no hardcoded wait).

## DOC MISMATCH 2 - FILE NAME IN apparatus_fixes.md

apparatus_fixes.md L36 (table row "Singleton lock"):
  "start_trading_day.ps1" (underscores)
Actual file: scripts\core\start-trading-day.ps1 (dashes)
Also in apparatus_fixes.md L319 (SESSION 2026-09-17 COORDINATOR WORK):
  "start-trading-day.ps1" (correct dashes)
Same file, two spellings. Cosmetic. Recommend fixing L36.

## RELATED OPEN BUGS

B029 (MED, OPEN): "Supervisor not running after manual restart".
  L_ITEMS I35. Directly relevant. A manual restart path that leaves
  the supervisor down explains why some sessions find no supervisor.
B043 (proposed, not yet on disk): supervisor double-start risk.
  Should be opened after this report.
B014 (MED, OPEN): "Loop exit orphans mvn/java child".
  Not verified this session. May share root cause.

## WHAT THE NEW SESSION SHOULD DO

1. Read this file. Read loop-supervisor.ps1 L55-153 in full.
2. Decide which of the three gaps to fix first. My order:
   - Gap 1 (supervisor singleton lock). Small. 15 lines.
   - Gap 2 (mode.ps1 refuses when supervisor present). Small.
   - Gap 3 (atomic lock create). Small but touches two files.
3. Open B043 in BUGS.md.
4. Fix the two doc mismatches (COMMANDS.md L107, apparatus_fixes.md L36).
5. Add a regression: after every clean restart, verify exactly one
   supervisor, one wrapper, one java. If count is not 1, log the
   mismatch to supervisor_log.txt and exit.

## WHAT NOT TO DO

- Do not remove the supervisor. It catches hangs the lock cannot.
- Do not bare-kill java. Use stop-day.ps1 or mode.ps1.
- Do not edit start-trading-day.ps1 without four-step proof. It is a
  critical file.

## EVIDENCE INDEX

File                                Lines used
scripts\core\loop-supervisor.ps1    1-90 (full content read), 108-153
scripts\core\mode.ps1               21-36
scripts\core\start-trading-day.ps1  249-279, 631, 643
scripts\core\stop-day.ps1           9-38
COMMANDS.md                         72, 89-111
DSA_SESSION_PROMPT.md               158
BUGS.md                             51 (B029)
apparatus_fixes.md                  36, 319
NEXT_SESSION_HANDOFF.md             5, 47-61

# END