# NEXT SESSION HANDOFF
# Rewritten 2026-09-22T19:00Z by MTS-2026-09-22-1737Z.

STATUS: Loop left running. Build PASS 104 rows. Position none. Sidecar live. Loop still 5.1; next natural restart spawns pwsh. Seven worker dispatches ready, zero replies received.

## QUEUE

Single source: MyTradingSys/mts/research/BUGS.md

Open: B058 (part D), B059, B062, B063, T034 (output type pending), T035, T037, T038, T039, T040, T041.

## FIRST ACTION NEXT SESSION

1. Confirm loop is up:
     Get-ChildItem .\data -Filter "*.lock*"
     Get-CimInstance Win32_Process -Filter "Name='java.exe' OR Name='pwsh.exe'" | Select-Object ProcessId, Name
2. Batch reads:
     Get-Content .\data\apparatus_log.txt -Tail 60
     Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 60
     Get-ChildItem .\data\snapshots -Filter "BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
     Get-Content .\MyTradingSys\mts\research\BUGS.md -Tail 40
3. Build-Check under pwsh:
     pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Build-Check.ps1
4. Optional: start next session in pwsh window, not 5.1.

## WORKER DISPATCHES READY (send to worker chats)

  Dumps/workers/W1_divergence_audit/DISPATCH.md            (B063 audit)
  Dumps/workers/W2_institutional_definitions/DISPATCH.md   (B063 GOLAS-A)
  Dumps/workers/W3_cross_indicator_relationships/DISPATCH.md (B063 GOLAS-B)
  Dumps/workers/W4_btc_tuning_consensus/DISPATCH.md       (B063 GOLAS-C)
  Dumps/workers/W5_backtest_design/DISPATCH.md            (B063 GOLAS-D)
  Dumps/workers/T040_tick_delta/DISPATCH.md               (tick-delta layer design)
  Dumps/workers/T041_verdict_timeframe_audit/DISPATCH.md  (verdict timeframe gap audit + research)

All carry R1-R5 inline. Send = paste into fresh chat with web access where research is required (W2-W5, T041 Part B).
Save reply to Dumps/workers/<folder>/REPLY.md.

## LANDED THIS SESSION (MTS-2026-09-22-1737Z, both closes)

NEXT_SESSION_HANDOFF rebuilt; SESSION_MANIFEST add; session_log events; DSA s11 amended; T039 sweep (8 item docs);
Build-Check enforcement (OPEN/IN-FIX/BLOCKED require items/), regex B-or-T, 63->103;
journal correction for five unrecorded 1215Z commits;
PS7 7.6.6 side-by-side, 5 spawn sites migrated to pwsh, WinForms/mvn/pytest verified, scan widened to runtime/*.md;
R1-R5 relabel across 7 files; 6 worker dispatches; T041 registered (row + item doc + dispatch); journal mojibake fixed.

## OPEN LOOPS AT CLOSE

PS7 Part 2 (loop restart under pwsh) not forced.
T034 output type decision owed by operator.
Worker replies: 0 of 7.

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
