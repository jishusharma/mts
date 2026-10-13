# Development Status

Generated: 2026-10-13 11:25:42

## Git Status
**Branch:** jis-nuc/s1013-ops (the host that generated this file; yours may differ)

CI green: a3626dc (2026-10-13 01:46:42 +0530), 12 commit(s) behind origin/fast-track: RED: oldest ungreen commit is 9.6 h old - CI is failing, auto-deploy is idle; fix CI first
LESSONS: digest STALE (synced de2de3a7, now ad79e76d): read the new LESSONS_LEARNED.md entries (git diff), add their rule lines to LESSONS_DIGEST.md, update the blob

**Last 10 commits:**
```
9b1b716 claim rv06-live-read-claims
5331077 lab: rv05 fabio ledger frame pass report + 3 evidence cards
372788c release rv05-fabio-ledger-frame-pass
701dcb0 Merge remote-tracking branch 'origin/fast-track' into jis-nuc/krown-ta101
4ba4e73 claim rv05-fabio-ledger-frame-pass
7f968e5 handoff: NUC recovery state, Krown card note (429, run from JIS-NB)
df9eb78 lane health: GPT up
69ff649 card: krown-ta101-extract-remaining-10
7cb7acb release krown-ta101-extraction-host-jis-nuc
ba09f64 Merge remote-tracking branch 'origin/fast-track' into jis-nuc/krown-ta101
```

## Queue Status
```
WORKER   no heartbeat yet (worker version 2 has not reached this queue)
QUEUE    waiting 0; running 0; replies 0; not yet verified 0
DSA-WORKER no heartbeat (not running); incoming_dsa 0; running 0
```

## In-Flight .new Files
- MyTradingSys\backtest\layers\fabio\htf_context_live.py.new (0.1h)
- MyTradingSys\backtest\layers\fabio\test_htf_context_live.py.new (0.1h)

## Recent Reports (last 7 days)
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
SHOTS landed 0: new 0, classified 0, read 0, done 0 | overdue(>24h) 0 | claims MATCH 0 MISMATCH 0 NOT_IN_DATA 0 | filed 0
```

## Layer Lab (Codex)
```
Layer lab (Codex) at 2026-10-13 05:55Z: on
  Codex allowance (plus): 5-hour window 37% used (resets 10-13 10:08Z); week 6% used (resets 10-20 05:08Z)
  Lab spend guard: window 20/50 pts, 1/4 runs (astra 1/1); week 4/35 pts; resets 10:08Z
  Last check by the scheduler: 2026-10-13T05:38Z RAN rv05-fabio-ledger-frame-pass OUT_OF_SCOPE model=gpt-6-astra effort=medium 299s tokens=811992 window+20.0 week+4.0 report=MyTradingSys/research/layer_lab/reports/2026-10-13_rv05-fabio-ledger-frame-pass.md note=6 uncommitted file(s) left in F:\MTS\mts-codex-lab: MyTradingSys/system/LAYERS.md
  Queue: 1 ready
    rv06-live-read-claims [audit, gpt-6-luna / medium]
  Delivered (latest 5; all in MyTradingSys/research/layer_lab/INDEX.md):
    2026-10-13 rv05-fabio-ledger-frame-pass: FIX-FIRST: 2 remaining rows checked, 3 HIGH carried forward and 2 MED; MyTradingSys/research/layer_lab/reports/2026-10-13_rv05-fabio-ledger-frame-pass.md
    2026-10-12 rv02-dax-harness-fixes: FIX-FIRST; 4 HIGH, 7 MED, 1 LOW; 66 tests passed; MyTradingSys/research/layer_lab/reports/2026-10-12_rv02-dax-harness-fixes.md
    2026-10-12 lab-dax-trial-identity: H8 fixed; 62 synthetic harness tests pass (red first): MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-trial-identity.md
    2026-10-12 lab-dax-readiness-gate: H7 fixed; 3 readiness tests and 58 harness tests pass; MyTradingSys/research/layer_lab/reports/2026-10-12_lab-dax-readiness-gate.md
    2026-10-12 lab-audit-tom-ledger-frames: FIX-FIRST: 37 rows, 65 cited plus 7 supplemental images; 4 HIGH and 4 MED; exact missing evidence per row; 4 repair cards. Report: MyTradingSys/research/layer_lab/reports/2026-10-12_lab-audit-tom-ledger-frames.md
  Last runs:
    2026-10-12 17:00Z lab-audit-fabio-ledger-frames INCOMPLETE (gpt-6-astra / high, 383k tokens, 777s)
    2026-10-12 19:33Z rv02-dax-harness-fixes DONE (gpt-6-astra / high, 284k tokens, 815s)
    2026-10-12 20:00Z lab-audit-fabio-ledger-frames LIMIT (gpt-6-astra / high, 63k tokens, 68s)
    2026-10-13 05:01Z lab-audit-fabio-ledger-frames DONE (gpt-6-astra / medium, 307k tokens, 545s)
    2026-10-13 05:33Z rv05-fabio-ledger-frame-pass OUT_OF_SCOPE (gpt-6-astra / medium, 811k tokens, window +20 pts, 299s)
  NEEDS A LOOK: 
    - only 1 card(s) left in the queue: add scoped cards (LAYER_LAB.md, Allowance)
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
