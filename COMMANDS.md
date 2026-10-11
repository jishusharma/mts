# COMMANDS

For daily operation use MTS_USER_GUIDE.md (the `mts` command). This file keeps the
older AI-session shortcuts and loop internals.

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

    python .\MyTradingSys\tests\docs\test_integrity.py -v
    # read the last line. If not all passed, stop. Do not write.

    .\scripts\Build-Check.ps1
    # read the STATUS line. If not PASS, stop.

## DECISION POINT

    python .\MyTradingSys\runtime\session_state.py show
    python .\MyTradingSys\runtime\session_state.py log
    python .\MyTradingSys\runtime\log_decision.py passed "reason"


# END THE SESSION

    .\scripts\core\stop-day.ps1
    gitsnap "close: one line on what happened"

## SNAPSHOT COMMANDS

    gitsnap   commit everything, move the snapshot tag
    gitsee    last five commits, plus dirty count
    gitundo   revert to the snapshot tag

## WHEN SOMETHING IS BROKEN

    health
    Get-Content .\runtime_data\apparatus_log.txt -Encoding UTF8 -Tail 15
    Get-Content .\runtime_data\last_alert.json -Raw | ConvertFrom-Json

## HARD RULES

One per line. No compression.

- Never bare-kill Java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row. It kills and restarts.
- Before editing a critical file: hash, edit, hash, diff. Critical list
  is in DSA_SESSION_PROMPT.md section 6.
- No writes to the session state thesis without user approval.
- All timestamps UTC. Line endings LF.
- The user runs all commands. The AI issues them.

## MAINTENANCE

These run rarely. Not part of the daily flow.

    python -m pytest MyTradingSys/tests -q         # math tests
    python -m pytest MyTradingSys/tests/docs -q    # doc tests
    python .\MyTradingSys\runtime\outcome_labeler.py
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

    mts-loop stop

Writes runtime_data\loop_stop.flag once. Wrapper exits at next cycle top, then the
supervisor exits on its next 30s check. stop-day.ps1 waits for both locks
to clear. supervisor_stop.flag is retired.

The supervisor log is at runtime_data\supervisor_log.txt.


## LOOP LIFECYCLE (new 2026-09-24)

```powershell
    mts-loop status    # read runtime_data\loop_state.json
    mts-loop start     # start-session.ps1 + mts-up
    mts-loop stop      # runs stop-day.ps1 (single flag stops wrapper AND supervisor)
```

One stop flag: `runtime_data\loop_stop.flag`. Honored by wrapper, supervisor, and stop-day.ps1.
Supervisor writes `runtime_data\loop_state.json` every 30s with: action, reason, wrapper_pid,
java_pid, snapshot_age_sec, state_code_age_sec, stale_strikes, restart_count_24h.
Stale detection: snapshot or state_code.json older than 150s for 2 consecutive ticks
triggers a tree-kill of the wrapper and a restart. Circuit breaker: 5 restarts in
15 minutes refuses further restarts.

# END
