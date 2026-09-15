# COMMANDS
# Read once top-to-bottom. Then jump to your moment.
# Apparatus is the interface. User runs only what is below.
# Last updated: 2026-09-16.

## SESSION START
    cd C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed
    . .\scripts\load.ps1
    .\session-start.ps1 -NoClipboard
    # open Dumps\SESSION_PASTE.txt, Ctrl+A, Ctrl+C, paste into fresh chat

## SESSION START - APPARATUS DEAD
    .\scripts\core\mode.ps1 -M armed

## DURING SESSION (aliases, load with load.ps1)
    lx      quick read (price, snap, CVD, state, last verdict)
    ld      1m bar deltas
    lt      15-cycle trend
    lf      full snapshot fields
    lc      decision combo
    la      recent alerts
    lh      health (java, state_code, log tail)

## MONITORING STATIONS (feed reads for AI)
    .\scripts\monitor\stations.ps1                     # F1-F5 + health
    .\scripts\monitor\stations.ps1 -All                # everything
    .\scripts\monitor\stations.ps1 -Station F2 -Tail 60

## DECISION POINT
    python .\MyTradingSys\mts\runtime\session_state.py show
    python .\MyTradingSys\mts\runtime\session_state.py log
    python .\MyTradingSys\mts\runtime\log_decision.py passed "reason"

## SESSION END
    .\scripts\core\stop-day.ps1

## GIT SNAPSHOT
    gitsnap     commit runtime churn
    gitsee      log
    gitundo     revert last commit

## BROKEN - FIRST RESPONSE
    lh
    Get-Content .\data\apparatus_log.txt -Encoding UTF8 -Tail 15
    Get-Content .\data\last_alert.json -Raw | ConvertFrom-Json

## HARD RULES
    - never bare-kill java. use stop-day.ps1 or mode.ps1.
    - never run mode.ps1 twice. it kills + restarts.
    - critical file edits: hash before / hash after / diff.
      See DSA_SESSION_PROMPT.md section 10.
    - no writes to session_state.json thesis without user approval.

# END
