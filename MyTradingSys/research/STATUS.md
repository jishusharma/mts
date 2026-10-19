# Development Status

Generated: 2026-10-19 12:43:55

## Git Status
CI green: ed732be0 (2026-10-19 11:49:35 +0530), 7 docs-only commit(s) ahead (no CI-gated path changed): OK
LESSONS: digest in sync
Pages stale: 3
STALE mts_control_room https://claude.ai/artifact/MNuodXmi5RiEihX7rFpqUp
STALE mts_layer_map https://claude.ai/artifact/7eeXJJ9Sb44LaJeCu8jxfJ
STALE mts_home https://claude.ai/artifact/8hKA1rhNRo6RAEdt5mtLg3

## Gate Board
```
tom     G2  proof changed 14h ago | next: G3 blind marks (READER_PROTOCOL.md + g3_marks_2026-10-16) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
fabio   G2  proof changed 14h ago | next: G1 coverage check, then G3 | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
malkan  G2  proof changed 82h ago | next: G3 blind marks MAL-2/5, MAL-16/17 (g3_marks_2026-10-16) | proof: MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md
krown   G1  proof changed 9h ago | next: G2 (krown-g2: KROWN_SETUP_CATALOG.md) | proof: MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv
commits 24h: 535 = research 21% | claim/release 35% | other 44%  OVER 30% CAP
```

**Last 3 commits on origin/fast-track:**
```
755ce518 lease pipeliner: release by JIS-NUC/5f400cc73e52
a060067c pipeliner opening 5: decided DSA-NB audit rows stay, install status recorded
a9ade2bf lease pipeliner: acquire by JIS-NUC/5f400cc73e52
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (208.9h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (208.9h)

## Recent Reports (newest 5, last 3 days)
- MyTradingSys/research/gap_audit_2026-10-19/REPORT.md (2026-10-19 09:40) # MTS Critical-Gap Audit, Revalidation & End-to-End Roadmap (2026-10-19)
- MyTradingSys/research/mts_doctor/REPORT_2026-10-18.md (2026-10-19 03:53) # MTS doctor report 2026-10-18
- MyTradingSys/research/mts_doctor/REPORT_2026-10-19.md (2026-10-19 02:46) # MTS_Doctor report 2026-10-19: ship-gate speed and cost (fast path bd1b0c7d, Codex verifi
- MyTradingSys/research/live_loop_timeouts_2026-10-18/REPORT.md (2026-10-18 17:58) # Live-Loop Timeouts Post-B191 Audit Report
- MyTradingSys/research/binance_backtesting_2026-10-18/CLAUDE_HANDOFF.md (2026-10-18 10:02) # Claude handoff: Binance BTC backtesting foundations

## Screenshots
```
SHOTS landed 39: new 11, classified 21, read 0, done 7 | overdue(>24h) 24 | claims MATCH 31 MISMATCH 5 NOT_IN_DATA 10 | filed 3
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
Layer lab (Codex) at 2026-10-19 07:14Z: on
  Codex allowance (plus): 5-hour window 81% used (resets 10-19 08:32Z); week 39% used (resets 10-24 20:42Z)
  Lab spend guard: window 0/50 pts, 0/10 runs (astra 0/1); week 0/60 pts; resets 08:32Z
  Last check by the scheduler: 2026-10-17T18:54Z RAN gap-g2-dax-ask-candles BLOCKED model=gpt-6-luna effort=medium 68s tokens=501142 window+0.0 week+0.0 report=MyTradingSys/research/layer_lab/reports/2026-10-17_gap-g2-dax-ask-candles.md
  Queue: 8 ready
    lc-ladder-dev [build, gpt-6-luna / medium]
    lab-formula-spec-recount [build, gpt-6-luna / medium]
    lab-formula-spec-text [build, gpt-6-luna / medium]
    lab-planted-error-trial [build, gpt-6-luna / medium]
    tom-btc-other-setups [build, gpt-6-luna / medium]
    simulator-validation-planted-edge [build, gpt-6-luna / medium]
    argon-blind-read-7-frames [run, gpt-6-luna / low]
    one-timeframe-map-for-the-whole-toolchai [build, gpt-6-luna / medium]
  Last runs:
    2026-10-17 22:37Z lab-crossvendor-same-vendor-gate SHIP_FAILED (gpt-6-luna / medium, 1.1M tokens, window +0 pts, 107s)
    2026-10-17 22:48Z lab-review-gate-harden BLOCKED (gpt-6-luna / medium, 1.4M tokens, window +0 pts, 163s)
    Z lab-review-gate-harden REOPENED (None / None, tokens ?, ?s)
    Z tom-v2-btc-min-stop-width REOPENED (None / None, tokens ?, ?s)
    2026-10-17 22:52Z lab-vendor-gate-harden DONE (gpt-6-luna / medium, 1.4M tokens, window +1 pts, 134s)
  NEEDS A LOOK: 
    - STALLED: 8 card(s) ready, lane up, no allowance hold, but nothing ran for 32.4 h: read last_tick.txt and last_lane.txt on the lab host
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 30 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 2 (HIGH 1) closed 9 | OPS open 18 (HIGH 6) closed 26 | INFRA open 7 (HIGH 3) closed 13 | UNGROUPED 1
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
