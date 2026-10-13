# Development Status

Generated: 2026-10-13 12:19:35

## Git Status
**Branch:** jis-nuc/tom-v2-partb (the host that generated this file; yours may differ)

CI green: a0080f0 (2026-10-13 11:44:27 +0530), 11 commit(s) behind origin/fast-track: CI running
LESSONS: digest STALE (synced de2de3a7, now ad79e76d): read the new LESSONS_LEARNED.md entries (git diff), add their rule lines to LESSONS_DIGEST.md, update the blob

**Last 10 commits:**
```
38f614b release tom-layer-v2-cost
1e0c065 Merge remote-tracking branch 'origin/fast-track' into jis-nuc/tom-v2-partb
2a6061c tom_noise_units test: move under MyTradingSys/tests so the gate collects it
125cb21 Merge pull request #26 from jishusharma/claude/zen-mayer-g4t5ui
7af0ffc research: backtest + extraction gap review vs BTC/Binance literature (cloud, read-only)
2e20a9e handoff: NUC cleanup state, remaining permission-gated steps
d0bff9e Merge remote-tracking branch 'origin/fast-track' into jis-nuc/tom-v2-partb
9b26093 Tom v2 spec part B: stop-width transfer rule, per-market proofs, test protocol, 7 Sonnet build cards
1d5d2ca shot.py: store path survives git 2.24 echoing --path-format as line 1 (JIS-NUC)
b83bf69 Merge remote-tracking branch 'origin/fast-track' into jis-nuc/cleanup-1013
```

## Queue Status
```
WORKER   no heartbeat yet (worker version 2 has not reached this queue)
QUEUE    waiting 0; running 0; replies 0; not yet verified 0
DSA-WORKER no heartbeat (not running); incoming_dsa 0; running 0
```

## In-Flight .new Files
- MyTradingSys\backtest\layers\fabio\htf_context_live.py.new (0.4h)
- MyTradingSys\backtest\layers\fabio\test_htf_context_live.py.new (0.4h)

## Recent Reports (last 7 days)
- MyTradingSys/research/backtest_gap_review_2026-10-13/REPORT.md (2026-10-13 12:07) # Backtest and extraction gap review: are we backtesting correctly? (2026-10-13, cloud session)
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
SHOTS landed 17: new 9, classified 1, read 0, done 7 | overdue(>24h) 10 | claims MATCH 31 MISMATCH 5 NOT_IN_DATA 10 | filed 3
  OVERDUE fdaf61046aae classified app                                  | DeepSeek DSA chat with AIBridge panel 'waiting for DSA after #2', auto-run 1/50, Run block not executed; operator reports bridge stuck
  OVERDUE ca93edd5a668 new        -                                    | 
  OVERDUE 7d9e56172f38 new        -                                    | i restarted - now i see this. Wjat needs to be done?
  OVERDUE f35e98c02d0c new        -                                    | We needed sreen-shots and chart related work - things were pending on me like tr
  OVERDUE 25050b52c03d new        -                                    | i need to know what is going on right now?
  OVERDUE c0b4ba1b62f9 new        -                                    | i need to know what is going on right now?
  OVERDUE bf07502e25bf new        -                                    | keeping in mind what we are doing on NUC - what to do with this? I need actions.
  OVERDUE 0a687a5cdc7e new        -                                    | <pasted_content id="cdc4"> it installed - computed restarted but it failed. i ah
  OVERDUE 616ec264d2e2 new        -                                    | 
  OVERDUE be93c2b8ab49 new        -                                    |
```

## Layer Lab (Codex)
```
Layer lab (Codex) at 2026-10-13 06:49Z: on
  Codex allowance (plus): 5-hour window 37% used (resets 10-13 10:08Z); week 6% used (resets 10-20 05:08Z)
  Lab spend guard: window 20/50 pts, 2/4 runs (astra 1/1); week 4/35 pts; resets 10:08Z
  Last check by the scheduler: 2026-10-13T06:30Z IDLE no CODEX card to run (0 ready; claimed or out of tries are skipped)
  Queue: 0 ready
  Delivered (latest 5; all in MyTradingSys/research/layer_lab/INDEX.md):
    2026-10-13 rv06-live-read-claims: FIX-FIRST: 6 findings; 3 cards confirmed faithful; report MyTradingSys/research/layer_lab/reports/2026-10-13_rv06-live-read-claims.md
    2026-10-13 rv05-fabio-ledger-frame-pass: FIX-FIRST: 2 remaining rows checked, 3 HIGH carried forward and 2 MED; MyTradingSys/research/layer_lab/reports/2026-10-13_rv05-fabio-ledger-frame-pass.md
    2026-10-12 rv02-dax-harness-fixes: FIX-FIRST; 4 HIGH, 7 MED, 1 LOW; 66 tests passed; MyTradingSys/research/layer_lab/reports/2026-10-12_rv02-dax-harness-fixes.md
    2026-10-12 lab-dax-trial-identity: H8 fixed; 62 synthetic harness tests pass (red first): MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-trial-identity.md
    2026-10-12 lab-dax-readiness-gate: H7 fixed; 3 readiness tests and 58 harness tests pass; MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-readiness-gate.md
  Last runs:
    2026-10-12 19:33Z rv02-dax-harness-fixes DONE (gpt-6-astra / high, 284k tokens, 815s)
    2026-10-12 20:00Z lab-audit-fabio-ledger-frames LIMIT (gpt-6-astra / high, 63k tokens, 68s)
    2026-10-13 05:01Z lab-audit-fabio-ledger-frames DONE (gpt-6-astra / medium, 307k tokens, 545s)
    2026-10-13 05:33Z rv05-fabio-ledger-frame-pass OUT_OF_SCOPE (gpt-6-astra / medium, 811k tokens, window +20 pts, 299s)
    2026-10-13 05:54Z rv06-live-read-claims OUT_OF_SCOPE (gpt-6-luna / medium, 321k tokens, window +0 pts, 104s)
  NEEDS A LOOK: 
    - the queue is empty, so the Codex allowance goes unused: move scoped cards to lane CODEX (LAYER_LAB.md, Allowance)
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
