# NEXT SESSION HANDOFF
# Rewritten 2026-09-17T16:22:23Z by MTS-2026-09-17-1514Z.

STATUS: Loop running. Supervisor 8200, wrapper 17792, java 596. Lock 17792. Do not stop. B034 loaded.

## FIRST ACTION NEXT SESSION
Read in one batch:
  Get-Content .\data\apparatus_log.txt -Tail 60
  Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 30
  Get-ChildItem .\data\snapshots -Filter 'BTCUSDT_*.json' | Sort LastWriteTime -Desc | Select -First 1

## LANDED THIS SESSION
1. B027 CLOSED. False alarm. OI updates hourly, not per minute. Verified by direct endpoint match.
2. B034 fixed. CVD ring clears on UTC day rollover. Live in java 596.
3. B026 fixed. no-change log now prints verdict.
4. B011 fixed. apparatus_fixes.md trimmed; historical tail archived.
5. Build-Check.ps1 line 89 UTC parse fix.
6. start-session.ps1 tail read default lines=60.
7. B043 fixed. Supervisor matcher extended to mode.ps1.
8. PROCESS SPEED RULES 8 and 9 added. No ampersand on mode.ps1. Direct kill for supervisor.

## OPEN - CARRIED
- B042 day_type: 2 of 3 snapshots. Need one more after next 13:30 UTC anchor.
- B018 zones move per cycle. Not audited this session.
- B024 book imbalance instability. Real; verdict impact not proven. Defer.
- buildStructure pivot dead code. tape-watch duplicate line.
- Multi-day ladder / CVD anchor / OI trajectory: schema gaps.
- Pre-open playbook gap.

## HARD RULES
- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 while a live lock is held by a running wrapper.
- Live claims: read live_session_protocol.md first. 10 checks + PROCESS SPEED RULES.
- To stop a supervisor: direct kill on the PID. Do not use the flag plus poll.
- Interactive PS: use throw, not return, to abort a block.

# END