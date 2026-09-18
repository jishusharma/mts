# NEXT SESSION HANDOFF
# Rewritten 2026-09-18T17:08:59Z by MTS-2026-09-18-1600Z.

STATUS: Loop running. Wrapper 16208, java 11668, lock 16208. No supervisor (SUP COUNT=0). Build-Check PASS. B049 T023 T024 CLOSED. B047 HIGH OPEN. T026 T027 OPEN.

## FIRST ACTION NEXT SESSION
Start the live feed:
  mts-live

In another window, read in one batch:
  Get-Content .\data\apparatus_log.txt -Tail 60
  Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 60
  Get-ChildItem .\data\snapshots -Filter 'BTCUSDT_*.json' | Sort LastWriteTime -Desc | Select -First 1
  Get-Content .\MyTradingSys\mts\research\BUGS.md

## LANDED THIS SESSION (MTS-2026-09-18-1600Z)
1. B046, T001-T008, T012, T013 closed (stale rows).
2. B048 CLOSED: verify_rule_citations.ps1 now fails on unreferenced ids.
3. T018 WONTFIX (frame display-only, superseded by 04_final_report).
4. B049 + T024 CLOSED: state gate on CT at VAH/VAL, tc_long path at VWAP.
   Verified by VerifyScbEdits.java 12/12. Commit 6816cc0, test at 87cc085.
5. T023 CLOSED (merged into B049). T025 CLOSED.
6. T026/T027 filed: frame Stage 2 wiring, annotation only.
7. 04_final_report_corrected_diagnosis.md saved and indexed.
8. SIZE header drift caught by doc test 4; header updated. Build-Check PASS.

## PRIMARY NEXT WORK - B047 HIGH
finished_auction sign inverted in math_object_builder.py L391, L398.
Java emits "sell" on negative delta at an extreme (SetupCandidatesBuilder L703).
Python flags SELL as a contradiction for LONG. Question: is the sign semantic correct?
Needed: Tom source read (raw_transcripts_canonical, search "auction"). Decide. Rule 32 proof.
04_final_report Step 3.

## SECONDARY QUEUE
- B044 MED: takerBuySellVol wire (kline proxy to real taker data). Report Step 4.
- T017 IN-FIX: content pass. Write TOM-NNN refs into 6 condition files.
- T014 rank-1 gate; T015 proof count options; T016 comparison questions.
- T019 RSI doc conflict; T020 GATE cell pad; T021 tape-watch dup; T022 last_verdict.json.
- B018, B024, B034, B045 carried.

## HARD RULES
- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 while a live lock is held by a running wrapper.
- Live mode uses mts-live. Every live session reads and extends the feed.
- To stop a supervisor: direct kill on the PID.
- Ledger is not truth. Files are truth. Verify before logging DONE.
- On any string replace, use [regex]::Matches with [regex]::Escape. String.Split(string) is not a valid overload.
- Interactive PS: no throw on multi-line if/else; use single-line if, or separate blocks.
- Build-Check PASS reads from Dumps/BUILD_REPORT.md, not from the Write-Host stream.
- Gate every commit on Build-Check PASS before staging files.

# END
