# NEXT SESSION HANDOFF
# Rewritten 2026-09-19T05:53Z by MTS-2026-09-19-0552Z.

STATUS: Loop running. Lock 14180, java 2456. No supervisor. Build PASS.

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

## LANDED LAST SESSION (MTS-2026-09-18-1726Z through MTS-2026-09-19-0552Z)

Code: B047, B024, B025, B036, B037, B039, T021, T027.
Infra: T017+T030 (213-quote TOM_VERBATIM_INDEX, 213 tags, verifier PASS).
Infra: T028 CLOSED via VerifyStateCodeCvd 4/4 (reflection seam, no midnight wait).
Infra: INDICATOR_IMPLEMENTATION_HANDOFF.md saved and indexed. T032-T035 filed.
Docs: T031 WONTFIX. B044 reopened (dead takerBuySellVol exists).

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- Ledger is not truth. Files are truth.
- Rule 32: verdict-path change needs 3-snapshot proof.
- No receipt until the evidence command output is on disk.
- session_timing_rules.md is research-sourced. No TOM-NNN tags there.

# END
