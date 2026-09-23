# NEXT SESSION HANDOFF
# Rewritten 2026-09-23T05:55Z by MTS-2026-09-23-0430Z.

STATUS: Loop STOPPED by operator request (powering off). No procs, no locks. Build pending. Session MTS-2026-09-23-0430Z.

## QUEUE

Single source: MyTradingSys/mts/research/BUGS.md

Open: B058 (part D), B059, B062, B063, B064, T034, T035, T037, T038, T039, T040, T041.

## FIRST ACTION NEXT SESSION

1. Confirm no stale processes:
     Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "statemachine|start-trading-day|loop-supervisor|tape-watch|mts-watch" } | Select ProcessId, Name
2. Start the loop (desktop only):
     .\scripts\core\mode.ps1 -M armed
     Start-Process pwsh.exe -ArgumentList @("-NoProfile","-ExecutionPolicy","Bypass","-File","$PWD\scripts\core\loop-supervisor.ps1","-Mode","armed","-IntervalMin","1","-RestartGraceSec","90") -WindowStyle Hidden
3. Batch reads:
     Get-Content .\data\apparatus_log.txt -Tail 40
     Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 40
     Get-ChildItem .\data\snapshots -Filter "BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
4. Build-Check under pwsh:
     pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Build-Check.ps1

## WORKER DISPATCHES

Folder convention: <parent_id>-W#-<slug>. Index at Dumps/workers/README.md.

Replied this session:
  Dumps/workers/B063-W1-divergence-audit/REPLY.md
  Dumps/workers/B063-W2-institutional-definitions/REPLY.md
  Dumps/workers/B063-W3-cross-indicator-relationships/REPLY.md

Ready, not sent:
  Dumps/workers/B063-W4-btc-tuning-consensus/DISPATCH.md
  Dumps/workers/B063-W5-backtest-design/DISPATCH.md
  Dumps/workers/T040-W1-tick-delta/DISPATCH.md
  Dumps/workers/T041-W1-verdict-timeframe-audit/DISPATCH.md

Each carry the full research gate (playbook Part I, three steps) and R1-R5.
Send pattern: paste DISPATCH.md into fresh chat, then paste the matching
ROUND1_EVIDENCE.md (B063 item doc) if the dispatch names it. Save reply
to REPLY.md in the same folder.

## LANDED THIS SESSION (MTS-2026-09-23-0430Z)

Loop restarted under pwsh (PS7 Part 2 closed). Supervisor 3184 + wrapper 2736,
then wrapper 11988 after supervisor restart. Loop stopped by operator request
at 05:52Z. Worker folder convention adopted (parent-prefix). README index
written. Archive at Dumps/workers/_archive/. Research-gate fix applied to
four dispatches (W2, W3, W4, T041). W1/W2/W3 replies stored. B064 filed
(supervisor does not honor supervisor_stop.flag).

## OPEN LOOPS AT CLOSE

B064 fix design owed (supervisor must check supervisor_stop.flag at cycle top).
W4, W5, T040, T041 dispatches not sent.
T042 candidate not registered (schema gap: no 4h/daily/weekly structure).
CVD divergence: no T1/T2 source. Matches MTS_DICTIONARY note that CVD has no
Tom basis.
W2 tier corrections at storage: volume profile and open interest corrected
from T1 to T2 (journals not on playbook T1 list).

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Ledger is not truth. Files are truth.
- No receipt until the evidence command output is on disk.
- Log tail is not a health check. Read wrapper PID + lock + log mtime together.
- No inferred levels. No angle-bracket placeholders in pasted blocks.
- No here-strings over 30 lines. Use IntelliJ or a temp .py file.

# END