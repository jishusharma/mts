# NEXT SESSION HANDOFF
# Rewritten 2026-09-19T08:00Z by MTS-2026-09-19-0755Z.

STATUS: Loop running. Lock 15296, java 5928. No supervisor. Build PASS.

## QUEUE

Do not mirror the queue here. Single source:
  MyTradingSys/mts/research/BUGS.md

## FIRST ACTION NEXT SESSION

1. Start mts-live (if not already running).
2. Read in one batch:
     Get-Content .\data\apparatus_log.txt -Tail 60
     Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 60
     Get-ChildItem .\data\snapshots -Filter 'BTCUSDT_*.json' | Sort LastWriteTime -Desc | Select -First 1
     Get-Content .\MyTradingSys\mts\research\BUGS.md -Tail 40
3. Read the queue from BUGS.md. Pick work.

## LANDED PRIOR TWO SESSIONS

Session MTS-2026-09-18-1726Z:
  B047 finished_auction sign fixed in Python, live-verified both directions.
  B024, B025, B036, B037, B039 code fixes with tests.
  T021 tape-watch skip-on-same-snapshot. T027 regime label in verdict log.
  T017+T030 CLOSED: TOM_VERBATIM_INDEX rebuilt 213 quotes, 213 tags, verifier PASS.
  T031 WONTFIX. B044 reopened. INDICATOR_IMPLEMENTATION_HANDOFF saved. T032-T035 filed.

Session MTS-2026-09-19-0552Z:
  7cd5976 Queue consolidation. BUGS.md is the only queue source.
  Evidence: SETUP_FORMING n=139, +30m win 64.7%, avg +0.107pct; baseline 51.1pct.
  dc1a239 Build-Card prints SESSION and US_OPEN from snapshot.session_timing.
  186b95a Session close.

## OPEN LOOP AT CLOSE

Build-Card SESSION / US_OPEN lines are on disk and loaded into the running
loop (restart 07:48:30Z, lock 15296). Not yet observed on a live alert card.
First alert after boot will confirm.

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Ledger is not truth. Files are truth.
- Rule 32: verdict-path change needs 3-snapshot proof.
- No receipt until the evidence command output is on disk.
- session_timing_rules.md is research-sourced. No TOM-NNN tags there.
- Journal and DSA timestamps must use (Get-Date).ToUniversalTime(). Local time with Z is wrong.

# END
