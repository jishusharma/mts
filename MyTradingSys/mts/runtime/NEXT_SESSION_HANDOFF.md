# NEXT SESSION HANDOFF
# Rewritten 2026-09-17T17:40Z by MTS-2026-09-17-1624Z.

STATUS: Loop running. Supervisor 8200, java 596, lock 17792. WRAP COUNT=0 anomaly open (wrapper matcher) - loop runs, flag only. Do not stop. B034 loaded.

## FIRST ACTION NEXT SESSION
Start the live feed:
  mts-live

In another window, read in one batch:
  Get-Content .\data\apparatus_log.txt -Tail 60
  Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 30
  Get-ChildItem .\data\snapshots -Filter 'BTCUSDT_*.json' | Sort LastWriteTime -Desc | Select -First 1

## LANDED THIS SESSION (MTS-2026-09-17-1624Z)
1. B044 B045 written to BUGS.md. CVD/trade_flow are kline proxy; WebSocket roadmap unrealized.
2. mts-watch.ps1 extended: compiled blocks MTS-HSTOP, MTS-PROOF, MTS-CAND, MTS-DELTA.
3. Live feed naming scheme (mts- prefix commands, MTS- prefix blocks) in MTS_DICTIONARY.md.
4. Aliases mts-live, mts-live-fast, mts-live-stop, mts-live-log, mts-tape in load.ps1.
5. mts-watch.ps1 version header v1.1.0.

## OPEN - CARRIED
- WRAP COUNT=0 anomaly. Wrapper matcher not finding wrapper. Lock held. Not urgent.
- B042 day_type: 2 of 3 snapshots. Need one more after next 13:30 UTC anchor.
- B018 zones move per cycle. Live in tape.
- B024 book imbalance instability. Real; verdict impact not proven.
- B044 B045: CVD/trade_flow kline proxy, WebSocket roadmap unrealized.
- Pre-open playbook gap.

## HARD RULES
- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 while a live lock is held by a running wrapper.
- Live mode uses mts-live. Every live session reads and extends the feed.
- Live claims: read live_session_protocol.md first. 10 checks + PROCESS SPEED RULES.
- To stop a supervisor: direct kill on the PID.
- Interactive PS: use throw, not return.

# END
