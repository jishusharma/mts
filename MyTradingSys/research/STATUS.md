# Development Status

Generated: 2026-10-14 17:34:58

## Git Status
**Branch:** jis-nb/ops-1014 (the host that generated this file; yours may differ)

CI green: 1e5ed30f (2026-10-14 01:22:33 +0530), 4 commit(s) behind origin/fast-track: CI running
LESSONS: digest STALE (synced de2de3a7, now ad79e76d): read the new LESSONS_LEARNED.md entries (git diff), add their rule lines to LESSONS_DIGEST.md, update the blob

**Last 10 commits:**
```
c8a86f11 gate: candle-close test skips per class without pandas; extra tests use own basetemp
29c786e6 gap review follow-up: merge origin, D-a/D-b/D-c decisions, source-verify desk row done
5a839bfb gap review follow-up: sources checked, G2 spread measured, cards G1-G8 filed
f8b666f3 desk task: Fold G1, G2, G4 into the Tom v2 spec and the spike-fade build (DAX)
c2856d1c ops: route backtest fixes to GPT lab, handoff to NB+DSA, pages rebuilt
b1b8364d release tom-btc-chart-lab
65b7d7bb release gap-g4-through-ticks-flag
7bd4a43d release reg-close-stale-rows
8ca3975e release live-market-gap-analysis-2026-10-12-oper
d17d0ca7 release backtest-gap-review-followup
```

## Queue Status
```
WORKER   no heartbeat yet (worker version 2 has not reached this queue)
QUEUE    waiting 0; running 0; replies 0; not yet verified 0
DSA-WORKER no heartbeat (not running); incoming_dsa 0; running 0
```

## In-Flight .new Files
- MyTradingSys\backtest\layers\fabio\htf_context_live.py.new (0.2h)
- MyTradingSys\backtest\layers\fabio\test_htf_context_live.py.new (0.2h)

## Recent Reports (last 7 days)
- MyTradingSys/research/backtest_gap_review_2026-10-13/REPORT.md (2026-10-14 16:56) # Backtest and extraction gap review: are we backtesting correctly? (2026-10-13, cloud session)
- MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md (2026-10-14 12:19) # BTC candle-close research: first LAB result
- MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md (2026-10-14 00:41) # Levels + staged position sizing: quick DEV probe
- MyTradingSys/research/mts_flow_audit_2026-10-13/REPORT.md (2026-10-13 22:30) # MTS end to end: the mistake at each step, and whether to buy FDAX data (2026-10-13, cloud, read-only)
- MyTradingSys/research/tom_dax_what_is_proven_2026-10-13/REPORT.md (2026-10-13 21:10) # What the DAX tests prove about Tom, and what is missing (2026-10-13, cloud, read-only)
- MyTradingSys/research/layer_combo_verdict_2026-10-13/REPORT.md (2026-10-13 20:20) # Layer-combination verdict: can any combination of layers trade profitably? (2026-10-13, cloud, read-only)
- MyTradingSys/research/mfe_exit_2026-10-13/REPORT.md (2026-10-13 01:20) # MFE exit study: can exits be reverse-engineered from the peak-profit bar? (2026-10-13, JIS-NUC)
- MyTradingSys/research/non_core_layer_audit_2026-10-12/CLAUDE_HANDOFF.md (2026-10-12 22:40) # Claude handoff - non-core layer evidence audit
- MyTradingSys/research/non_core_layer_audit_2026-10-12/REPORT.md (2026-10-12 22:40) # Independent layer audit: RSI, WaveTrend and the other non-core layers
- MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md (2026-10-12 17:46) # Q33 matrix report (2026-10-12, JIS-NUC): nothing survives
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
SHOTS landed 40: new 0, classified 0, read 0, done 40 | overdue(>24h) 0 | claims MATCH 413 MISMATCH 59 NOT_IN_DATA 98 | filed 2
```

## Layer Lab (Codex)
```
Layer lab (Codex) at 2026-10-14 12:04Z: on
  This machine does not run the lab (it runs on JIS-NUC): queue and deliveries below are from the repo; allowance, runs and what needs a look are only known there.
  Queue: 7 ready
    tom-btc-chart-lab [build, gpt-6-luna / medium]
    lc-levels-hold [build, gpt-6-luna / medium]
    tom-v2-btc-min-stop-width [build, gpt-6-luna / medium]
    gap-g4-through-ticks-flag [build, gpt-6-luna / medium]
    gap-g6-trial-ledger [build, gpt-6-luna / medium]
    qriptal-call-ledger [build, gpt-6-luna / medium]
    candle-close-independent-audit [audit, gpt-6-luna / medium]
  Delivered (latest 5; all in MyTradingSys/research/layer_lab/INDEX.md):
    2026-10-14 lab-candle-close-dev: 126 DEV arms, 105541 correlated events, 0 pass; eight tests and independent 126-event reconstruction pass; validation unread.
    2026-10-14 lab-candle-close-research: FIX-FIRST for edge claims: verified sources, causal study design, split audit and two follow-up cards; full research report saved.
    2026-10-13 gap-g1-power-mde-helper: six G1 rows within 2 points; 7 tests pass; MyTradingSys/research/layer_lab/reports/2026-10-13_gap-g1-power-mde-helper.md
    2026-10-13 rv06-live-read-claims: FIX-FIRST: 6 findings; 3 cards confirmed faithful; report MyTradingSys/research/layer_lab/reports/2026-10-13_rv06-live-read-claims.md
    2026-10-13 rv05-fabio-ledger-frame-pass: FIX-FIRST: 2 remaining rows checked, 3 HIGH carried forward and 2 MED; MyTradingSys/research/layer_lab/reports/2026-10-13_rv05-fabio-ledger-frame-pass.md
```

## Daily Hygiene (scheduled)
```
(no hygiene run on this host yet: python scripts/dev/daily_hygiene.py, or register_cicd_tasks.ps1)
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 29 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 10 (HIGH 2) closed 5 | EVID open 13 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 2 (HIGH 1) closed 9 | OPS open 17 (HIGH 4) closed 24 | INFRA open 7 (HIGH 3) closed 12
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
