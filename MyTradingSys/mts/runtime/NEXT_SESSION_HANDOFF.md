# NEXT SESSION HANDOFF
# Rewritten 2026-09-18T15:55:04Z by MTS-2026-09-18-0848Z.

STATUS: Loop running. Wrapper 15424, java 7280, lock 15424. No supervisor (SUP COUNT=0). BUGS.md is BUGS AND TASKS. B047 open HIGH (finished_auction sign, engine fix blocked pending three-snapshot proof).

## FIRST ACTION NEXT SESSION
Start the live feed:
  mts-live
Optional sidecar:
  mts-tape

In another window, read in one batch:
  Get-Content .\data\apparatus_log.txt -Tail 60
  Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 60
  Get-ChildItem .\data\snapshots -Filter 'BTCUSDT_*.json' | Sort LastWriteTime -Desc | Select -First 1
  Get-Content .\MyTradingSys\mts\research\BUGS.md

## LANDED THIS SESSION (MTS-2026-09-18-0848Z)
1. B043 CLOSED. mts-watch v1.1.1 synced 4 files.
2. chart_read_protocol.md new. Anchor C decided.
3. Three FYI docs archived under MyTradingSys/mts/research/fyi_archive/2026-09-18/.
4. BUGS.md extended to BUGS AND TASKS. B046, B047 filed. T001-T022 filed.
5. T004-T013, T020-T022 landed. See BUGS.md TASKS section for receipts.
6. DSP section 11 and handoff rewritten (B046 was the ledger lie; fixed).

## OPEN - CARRIED
- B047 HIGH: finished_auction sign inverted. Engine fix BLOCKED until three-snapshot proof exists.
- B046: ledger claimed work that was not run. Now closed. Hard rule: ledger is not truth, files are truth.
- B018 zones move per cycle. B024 book imbalance.
- B044 B045: CVD kline proxy, WebSocket roadmap unrealized.
- T014-T022 OPEN in BUGS.md TASKS section.
- SUP COUNT=0 all day. No supervisor.
- MTS-TAPE is manual sidecar. Restart with mts-tape; feed flags STALE over 120s.

## HARD RULES
- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 while a live lock is held by a running wrapper.
- Live mode uses mts-live. Every live session reads and extends the feed.
- To stop a supervisor: direct kill on the PID.
- Interactive PS: no throw on multi-line if/else. Use single-line if, or two separate if blocks.
- Ledger is not truth. Files are truth. Verify before logging DONE.
- On any string replace, use [regex]::Matches with [regex]::Escape. String.Split(string) is not a valid overload; it splits on every character.

# END
