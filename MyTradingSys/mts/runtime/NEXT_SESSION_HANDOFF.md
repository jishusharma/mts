# NEXT SESSION HANDOFF
# Rewritten 2026-09-18T20:49Z by MTS-2026-09-18-1726Z.

STATUS: Loop running. Wrapper 16624, java 6648, lock 16624, supervisor 8976. Build PASS. Queue 7 items.

## FIRST ACTION NEXT SESSION

1. Start mts-live (if not already running).
2. Read in one batch:
     Get-Content .\data\apparatus_log.txt -Tail 60
     Get-Content .\MyTradingSys\mts\runtime\live_session_journal.md -Tail 60
     Get-ChildItem .\data\snapshots -Filter 'BTCUSDT_*.json' | Sort LastWriteTime -Desc | Select -First 1
     Get-Content .\MyTradingSys\mts\research\BUGS.md -Tail 40

3. T028 check (WINDOW: 00:00-00:20 UTC only):
     Get-Content .\MyTradingSys\mts\runtime\state_code.json -Raw
   Look at: transition_chain_15m has no pre-00:00 letters; signals.cvd_slope is not spuriously "bearish".
   If both hold: close T028 with the rollover timestamp and chain head as receipt.
   If either fails: reopen B034 with state_code.json as evidence.
   Outside 00:00-00:20 UTC: T028 does not resolve. Carry.

4. Queue review: 7 open items (B003, B044, T028, T032-T035).
   Pick work. Recommended: T032 (Phase 1, lowest risk, code exists).

## LANDED THIS SESSION (MTS-2026-09-18-1726Z)

Code fixes:
  B047 finished_auction sign in math_object_builder.py. Python swapped. Live-verified both directions.
  B024 book_imbalance thresholds 0.4/1.5 -> 0.33/3.0.
  B025 2-cycle verdict debounce.
  B036 normalized dict carries setup_candidates + cvd.
  B037 exclude bool from isinstance.
  B039 momentum RR gate at 2.0 net.
  T021 tape-watch skip-on-same-snapshot.
  T027 regime label in verdict log line.

Doc/infra:
  T017+T030 CLOSED. TOM_VERBATIM_INDEX rebuilt: 213 quotes TOM-001..TOM-213. 213 tags across 5 condition files. verify_rule_citations PASS.
  T031 WONTFIX (session_timing_rules research-sourced).
  INDICATOR_IMPLEMENTATION_HANDOFF.md saved and indexed.
  T032-T035 filed (indicator phases 1,2,3,5).
  B044 reopened (dead takerBuySellVol method exists).
  B003 receipt corrected twice; kept OPEN pending repro.
  03_FILE_INDEX.md SIZE header drift fixed.

## QUEUE

| ID | Sev | Title |
|---|---|---|
| B003 | MED | stop-day.ps1 historical miss. Not reproducible. Kept for repro. |
| B044 | MED | CVD kline proxy. Reopened. Superseded by T032. |
| T028 | LOW | Verify B034 cvdSeries.clear at 00:00 UTC rollover. Window 00:00-00:20. |
| T032 | MED | Phase 1: wire takerBuySellVol, topLongShortPositionRatio, topLongShortAccountRatio. |
| T033 | MED | Phase 2: OI delta four-state classifier. |
| T034 | MED | Phase 3: Net Longs/Shorts positioning states. |
| T035 | LOW | Phase 5: multi-aggregated CVD (Bybit, OKX). |

## HARD RULES

- Never bare-kill java. Use stop-day.ps1 or mode.ps1.
- Never run mode.ps1 twice in a row.
- T028 window is 00:00-00:20 UTC. Outside it, the fix is unobservable.
- Ledger is not truth. Files are truth. Verify before writing.
- Rule 32: any verdict-path change needs 3-snapshot proof.
- Read before you write. Every receipt cites a command whose output is on disk.
- session_timing_rules.md is research-sourced. Do not add TOM-NNN tags there.

# END