# Development Status

Generated: 2026-10-15 20:58:10

## Git Status
CI green: 86ee2701 (2026-10-15 16:20:57 +0530, 4.6 h old), 16 trunk landing(s) / 118 commit(s) behind origin/fast-track: RED: oldest ungreen commit is 3.2 h old - CI is failing, auto-deploy is idle; fix CI first
LESSONS: digest in sync

**Last 3 commits on origin/fast-track:**
```
4408f0a1 release video-priority-malkan-caption-selection
ed0f503c Merge remote-tracking branch 'origin/fast-track' into claude/unruffled-goldberg-0d2e71
12a11c6f claim gate-slot-limit
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (121.1h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (121.1h)

## Recent Reports (newest 5, last 3 days)
- MyTradingSys/research/pivot_pattern_audit_2026-10-14/REPORT.md (2026-10-14 19:56) # Pivot-pattern scope audit — 2026-10-14
- MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md (2026-10-14 17:41) # BTC candle-close research: first LAB result
- MyTradingSys/research/backtest_gap_review_2026-10-13/REPORT.md (2026-10-14 16:56) # Backtest and extraction gap review: are we backtesting correctly? (2026-10-13, cloud ses
- MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md (2026-10-14 00:41) # Levels + staged position sizing: quick DEV probe
- MyTradingSys/research/mts_flow_audit_2026-10-13/REPORT.md (2026-10-13 22:30) # MTS end to end: the mistake at each step, and whether to buy FDAX data (2026-10-13, clou

## Screenshots
```
SHOTS landed 18: new 9, classified 2, read 0, done 7 | overdue(>24h) 10 | claims MATCH 31 MISMATCH 5 NOT_IN_DATA 10 | filed 3
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
Layer lab (Codex) at 2026-10-15 15:28Z: on
  Codex allowance (plus): 5-hour window 1% used (resets 10-15 19:03Z); week 0% used (resets 10-22 14:03Z)
  Lab spend guard: window 1/50 pts, 1/4 runs (astra 0/1); week 0/35 pts; resets 19:03Z
  Last check by the scheduler: 2026-10-15T15:00Z IDLE no CODEX card to run (2 ready; claimed or out of tries are skipped)
  Queue: 2 ready
    tom-btc-event-study [build, gpt-6-luna / medium] SKIPPED after failed tries
    gap-g6-trial-ledger [build, gpt-6-luna / medium]
  Last runs:
    2026-10-14 19:05Z tom-btc-event-study BLOCKED (gpt-6-luna / medium, 428k tokens, window +0 pts, 60s)
    2026-10-14 22:33Z lc-levels-hold BLOCKED (gpt-6-luna / medium, 275k tokens, window +0 pts, 42s)
    2026-10-14 23:00Z lc-levels-hold SHIP_FAILED (gpt-6-luna / medium, 2.7M tokens, window +1 pts, 378s)
    2026-10-15 14:03Z gap-g4-through-ticks-flag BLOCKED (gpt-6-luna / medium, 1.4M tokens, window +0 pts, 154s)
    2026-10-15 14:30Z gap-g4-through-ticks-flag DONE (gpt-6-luna / medium, 982k tokens, window +1 pts, 125s)
  NEEDS A LOOK: 
    - tom-btc-event-study failed 2 times and is skipped: read its report and run log, then fix the card
    - only 1 card(s) left in the queue: add scoped cards (LAYER_LAB.md, Allowance)
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 29 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 2 (HIGH 1) closed 9 | OPS open 17 (HIGH 5) closed 25 | INFRA open 7 (HIGH 3) closed 12
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
