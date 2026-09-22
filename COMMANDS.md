# COMMANDS

Read once top to bottom. Then jump to your moment. Last updated: 2026-09-16.

## START THE SESSION

    cd C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\scripts
    .\start-session.ps1

That loads the shortcuts and writes Dumps\SESSION_PASTE.txt.
Then open that file, copy all, paste into a fresh chat.

If the runtime loop is not running:

    .\scripts\core\mode.ps1 -M armed

## DURING THE SESSION

    quick     quick read - price, snapshot, CVD, state, last verdict
    deltas    last 12 minutes of one-minute bars
    trend     last 15 snapshots, side by side
    snapshot  one snapshot, all decision fields
    overview  live, snapshot, state, and log together
    alerts    last 10 alerts
    health    java process, state file age, log tail

Monitoring stations:

    .\scripts\monitor\stations.ps1
    .\scripts\monitor\stations.ps1 -All
    .\scripts\monitor\stations.ps1 -Station F2 -Tail 60

## BEFORE ANY WRITE

    .\scripts\tools\verify_data.ps1
    # read the STATUS line. If FAIL, stop. Do not write.

    python .\MyTradingSys\mts\tests\docs\test_integrity.py -v
    # read the last line. If not all passed, stop. Do not write.

    .\scripts\Build-Check.ps1
    # read the STATUS line. If not PASS, stop.

## DECISION POINT

    python .\MyTradingSys\mts\runtime\session_state.py show
    python .\MyTradingSys\mts\runtime\session_state.py log
    python .\MyTradingSys\mts\runtime\log_decision.py passed "reason"

## END THE SESSION

    .\scripts\core\stop-day.ps1
    gitsnap "close: one line on what happened"

## SNAPSHOT COMMANDS

    gitsnap   commit everything, move the snapshot tag
    gitsee    last five commits, plus dirty count
    gitundo   revert to the snapshot tag

## WHEN SOMETHING IS BROKEN

    health
    Get-Content .\data\apparatus_log.txt -Encoding UTF8 -Tail 15
    Get-Content .\data\last_alert.json -Raw | ConvertFrom-Json

## HARD RULES

One per line. No compression.

- Never bare-kill Java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row. It kills and restarts.
- Before editing a critical file: hash, edit, hash, diff. Critical list
  is in DSA_SESSION_PROMPT.md section 5.
- No writes to the session state thesis without user approval.
- All timestamps UTC. Line endings LF.
- The user runs all commands. The AI issues them.

## MAINTENANCE

These run rarely. Not part of the daily flow.

    python -m pytest MyTradingSys/mts/tests -q         # math tests
    python -m pytest MyTradingSys/mts/tests/docs -q    # doc tests
    python .\MyTradingSys\mts\runtime\outcome_labeler.py
    .\scripts\Dump_All.ps1                             # full dump set


## SUPERVISOR

The supervisor watches the loop wrapper. Restarts it if it dies. Start it in its own window:

    Start-Process pwsh.exe -ArgumentList @(
        "-NoProfile","-ExecutionPolicy","Bypass",
        "-File","$PWD\scripts\core\loop-supervisor.ps1",
        "-Mode","armed","-IntervalMin","1","-RestartGraceSec","90"
    ) -WindowStyle Hidden

Verify it is running:

    Get-CimInstance Win32_Process -Filter "Name='powershell.exe' OR Name='pwsh.exe'" | Where-Object { $_.CommandLine -match "loop-supervisor" } | Select-Object ProcessId, CommandLine

Stop it cleanly:

    New-Item .\data\supervisor_stop.flag -ItemType File -Force

Wait 35 seconds. The supervisor exits on its next check. Then remove the flag:

    Remove-Item .\data\supervisor_stop.flag

The supervisor log is at data\supervisor_log.txt.

# END
    mts-paste        continuous live snapshot to Dumps/LIVE_PASTE.txt, 30s cadence
    mts-paste-now    one-shot grab and print
    mts-paste-stop   stop the loop
