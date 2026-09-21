# NEXT SESSION HANDOFF
# Rewritten 2026-09-21T21:35Z by MTS-2026-09-21-1905Z.

STATUS: Loop left running at close. Build PASS 21:17:14Z. Position none. Both new OI-delta fields on disk, not yet in a live snapshot (Java edit landed after the last snapshot write; first snapshot with the new keys is next cycle after restart of the Java process).

## QUEUE

Single source: MyTradingSys/mts/research/BUGS.md

Open: B058 (part D needs live tape), B059 (queue note only, retracted non-repro claim), B062 (blocked on spec),
T034 (positioning states - "_new" undefined in HANDOFF Phase 3), T035 (multi-venue CVD), T037 (test coverage gap).
T033 CLOSED 2026-09-21.

## FIRST ACTION NEXT SESSION

1. Confirm loop is up: Get-ChildItem .\data -Filter "*.lock*"; Get-Process java -ErrorAction SilentlyContinue
2. Read in one batch:
     Get-Content .\data\apparatus_log.txt -Tail 60
     Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 60
     Get-ChildItem .\data\snapshots -Filter "BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
     Get-Content .\MyTradingSys\mts\research\BUGS.md -Tail 40
3. Verify both new fields in the first cycle snapshot:
     $s = Get-ChildItem .\data\snapshots -Filter "BTCUSDT_*.json" | Sort LastWriteTime -Desc | Select -First 1
     (Get-Content $s.FullName -Raw | ConvertFrom-Json).open_interest | ConvertTo-Json
   Expect keys: direction, change_1h_pct, confidence, delta_state, delta_state_price.

## LANDED THIS SESSION (MTS-2026-09-21-1905Z)

T033 closed. open_interest.delta_state L366 (volume-delta school, nd1h). Sibling open_interest.delta_state_price L373
(price school, close delta over 60 1m bars). Fallbacks L1164-1165 neutral. Helper L1375 with 8-line comment.
Hash chain 3006E87F -> 3B4E6325 -> 2C0C2064 -> 5B2270A4.

backtest_oi_delta_4state.py new. Report MyTradingSys/mts/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md.
Both schools near-identical. aggressive_short positive at all horizons in both - contradicts spec. rekt_short near zero
at all horizons in both. 8-9 days. No verdict.

## RULE 32 OBSERVATIONS CARRIED

B058 part D per-zone cooldown - needs same-zone repeat WATCH or SETUP_FORMING.
B062 suppression - needs live SETUP_FORMING matching open position.json direction.
EXIT_HINT - needs position.json + opposing candidate in range.

## OPEN LOOPS AT CLOSE

T034 spec gap: HANDOFF Phase 3 does not define "_new". Do not write until defined.
Backtest finding: aggressive_short positive at all horizons in both schools. Revisit when window grows.
03_FILE_INDEX.md needs rows for backtest_oi_delta_4state.py and OI_DELTA_4STATE_BACKTEST_2026-09-21.md.

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
