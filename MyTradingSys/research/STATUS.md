# Development Status

Generated: 2026-10-12 11:51:30

## Git Status
**Branch:** jis-nuc/codex-layer-lab (the host that generated this file; yours may differ)

CI green: 8d76d93 (2026-10-12 11:44:47 +0530), 1 commit(s) behind origin/fast-track: CI running
LESSONS: digest STALE (synced de2de3a7, now ad79e76d): read the new LESSONS_LEARNED.md entries (git diff), add their rule lines to LESSONS_DIGEST.md, update the blob

**Last 10 commits:**
```
1fa1f0e claim codex-lab-status-for-operator-and-status
8d76d93 Merge remote-tracking branch 'origin/fast-track' into jis-nuc/codex-layer-lab
5f522b2 Merge remote-tracking branch 'origin/fast-track' into jisnb/nb-idle
493a110 lab: build cards run their own tests, the runner's ship is the gate
51adb23 declutter: archive superseded proof_direction_cases.py.new
d315317 lab lab-dax-proof-parity: DONE after session check (build)
b75bf76 release lab-dax-proof-parity
5069e7c Merge remote-tracking branch 'origin/fast-track' into jis-nuc/codex-lab
938205d Merge remote-tracking branch 'origin/fast-track' into jisnb/dsa
2efe15c TWO_HOST: record JIS-NB idle-tick short-circuit and verified crons
```

## Queue Status
```
WORKER   no heartbeat yet (worker version 2 has not reached this queue)
QUEUE    waiting 0; running 0; replies 0; not yet verified 0
DSA-WORKER no heartbeat (not running); incoming_dsa 0; running 0
```

## In-Flight .new Files
- MyTradingSys\backtest\layers\fabio\htf_context_live.py.new (10.5h)
- MyTradingSys\backtest\layers\fabio\test_htf_context_live.py.new (10.5h)

## Recent Reports (last 7 days)
- MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md (2026-10-11 21:39) # BIGMOVES REPORT (big-move ground truth, backtest A)
- MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md (2026-10-11 21:39) # FIRES_B1_REPORT - fire history of the kline-only live layers (worker B1, 2026-10-09)
- MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md (2026-10-11 02:13) # DAX_BT_REPORT: untuned Tom core on DAX vs matched-proof BTC (card tom-dax-backtest)
- MyTradingSys/research/screenshot_context_2026-10-10/REPORT.md (2026-10-10 02:22) # T092 REPORT - what context does a single screenshot read get? (2026-10-10, Opus, JIS-NUC)
- MyTradingSys/research/rsi_divergence_mtf_2026-10-09/REPORT_T088.md (2026-10-09 21:25) # T089 RSI divergence on every timeframe (+ T091 operator long-range column)
- MyTradingSys/research/rsi_divergence_mtf_2026-10-09/REPORT.md (2026-10-09 21:06) # T089 RSI divergence on every timeframe (+ T091 operator long-range column)
- MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md (2026-10-09 09:09) # EXIT POLICIES REPORT (backtest C), 2026-10-09
- MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md (2026-10-09 07:01) # BTC volume research: buy volume, sell volume, exhaustion, patterns, time (2026-10-09)

## Screenshots
```
SHOTS landed 0: new 0, classified 0, read 0, done 0 | overdue(>24h) 0 | claims MATCH 0 MISMATCH 0 NOT_IN_DATA 0 | filed 0
```

## Layer Lab (Codex)
```
Layer lab (Codex) at 2026-10-12 06:21Z: on
  Codex allowance (plus): 5-hour window 5% used (resets 10-12 10:47Z); week 12% used (resets 10-18 13:41Z)
  Last check by the scheduler: 2026-10-12T06:02Z RAN lab-dax-proof-parity SHIP_FAILED model=gpt-6.1-sol effort=medium 452s report=MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-proof-parity.md note=sync: offline gate (--quick) failed; nothing pushed | release failed: sync: offline gate (--quick) failed; nothing pushed
  Queue: 5 ready
    lab-dax-closed-executions [build, gpt-6.1-sol / medium]
    lab-dax-net-fee-verdict [build, gpt-6.1-sol / medium]
    lab-dax-trial-identity [build, gpt-6.1-sol / medium]
    lab-audit-fabio-ledger-frames [audit, gpt-6-astra / high]
    lab-audit-tom-ledger-frames [audit, gpt-6-astra / high]
  Delivered (latest 5; all in MyTradingSys/research/layer_lab/INDEX.md):
    2026-10-12 lab-dax-proof-parity: H1 fixed: volume_spike no longer counted (Java B144), stale rows and snapshots refused, proof ceiling printed as 1; 33 harness tests pass, quick gate green outside the sandbox. reports/2026-10-12_lab-dax-proof-parity.md
    2026-10-11 lab-audit-tom-dax-bt: FIX-FIRST: 8 HIGH + 6 MED in the DAX backtest harness (stale proof count, dev trades exiting on holdout bars, fills on closed-market bars, fee gate bypassed); 8 follow-up cards lab-dax-*; report layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md. Claude spot-check: H1 and H5 MATCH the code. Closed by Claude: Codex left it open only because video frames are not on the NUC.
  Last runs:
    2026-10-11 20:06Z lab-audit-tom-dax-bt INCOMPLETE (gpt-6-astra / high, 23k tokens, 38s)
    2026-10-11 20:12Z lab-audit-tom-dax-bt BLOCKED (gpt-6-astra / high, 199k tokens, 512s)
    2026-10-12 05:47Z lab-dax-proof-parity SHIP_FAILED (gpt-6.1-sol / medium, 94k tokens, 452s)
  NEEDS A LOOK: nothing
```

## Daily Hygiene (scheduled)
```
(no hygiene run on this host yet: python scripts/dev/daily_hygiene.py, or register_cicd_tasks.ps1)
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 29 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 10 (HIGH 2) closed 5 | EVID open 13 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 2 (HIGH 1) closed 9 | OPS open 16 (HIGH 4) closed 24 | INFRA open 7 (HIGH 3) closed 12
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
