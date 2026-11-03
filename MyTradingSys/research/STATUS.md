# Development Status

Generated: 2026-11-04 01:10:58

## Git Status
CI green: 3f39b0f7f (2026-11-04 00:49:49 +0530, 0.4 h old), 8 trunk landing(s) / 8 commit(s) behind origin/fast-track: CI running
Layer pass: 0 of 37 fee-net row(s) carry a surviving PASS
GO-PRIVATE: A=0 B=1 TRIGGER B:carry_basis_2026-10-18 (2026-10-18)
LESSONS: digest STALE (synced c5767610, now e42f1a54): read the new LESSONS_LEARNED.md entries (git diff), add their rule lines to LESSONS_DIGEST.md, update the blob
Pages stale: 3
STALE mts_layer_map https://claude.ai/artifact/7eeXJJ9Sb44LaJeCu8jxfJ
STALE sim_desk https://claude.ai/artifact/KaPy7f5BKFsvmqin84DpyF
STALE mts_home https://claude.ai/artifact/8hKA1rhNRo6RAEdt5mtLg3

## Hand-over freshness (hand-overs are history: read disk and git, never quote them as current)
```
(no dated hand-over blocks)
```

## Gate Board
```
tom     G2  proof changed 88h ago | next: Live validation with drawn chart flags (d-live-validation; G3 blind marks dropped) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
fabio   G2  proof changed 88h ago | next: G1 coverage check, then live validation (d-live-validation) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
malkan  G2  proof changed 212h ago | next: Live validation + 1d/1w RSI divergence flags (d-live-validation; G3 blind marks dropped) | proof: MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md
krown   G2  proof not on trunk | next: Live validation with drawn chart flags (d-live-validation; G3 blind marks dropped) | proof: MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md (commit f4a5182a)
NO GATE MOVED IN 24h: the next spawn targets a gate (LAYER_REBUILD_PLAN s5)
commits 24h: 186 = research 33% | claim/release 0% | other 67%  OVER 30% CAP
```

**Last 3 commits on origin/fast-track:**
```
87964ab59 ship: regenerated LAYERS.md
4afd88410 cards: full-path smoke test gap for run_v3_l3
b1e15c564 task: card fabio-v3-is-only-loads-oos-bars closed with its result
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (581.3h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (581.3h)

## Recent Reports (newest 5, last 3 days)
- MyTradingSys/research/mts_doctor/REPORT_2026-11-01.md (2026-11-02 01:35) # MTS doctor report 2026-11-01

## Screenshots
```
SHOTS landed 90: new 41, classified 41, read 0, done 8 | overdue(>24h) 82 | claims MATCH 31 MISMATCH 5 NOT_IN_DATA 10 | filed 3
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
Layer lab (Codex) at 2026-11-03 19:41Z: on
  Codex allowance (plus): 5-hour window 0% used; week 30% used (resets 11-09 06:11Z)
  Lab spend guard: window 0/65 pts, 0/14 runs (astra 0/1); week 6/90 pts; resets 00:35Z
  Last check by the scheduler: 2026-11-03T13:08Z IDLE the last run started 3 minutes ago (minimum gap 20); one card per tick
  Queue: 2 ready
    gpt-spec-tests-live-aid-us-open-1103 [build, gpt-6-luna / medium]
    gemini-blind-read-eagle-c36-wt-confluence-1103 [audit, gpt-6-luna / medium]
  Last runs:
    2026-11-02 18:36Z aibridge-sandbox-chat-run-acl-proof BLOCKED (gpt-6-luna / medium, 139k tokens, window +0 pts, 38s)
    2026-11-02 19:15Z aibridge-sandbox-chat-run-acl-proof BLOCKED (gpt-6-luna / medium, 127k tokens, window +0 pts, 27s)
    2026-11-02 20:02Z mts-audit-1103-independent-recheck BLOCKED (gpt-6-luna / medium, 1.2M tokens, window +1 pts, 99s)
    2026-11-03 13:05Z mts-audit-1103-independent-recheck BLOCKED (gpt-6-luna / medium, 376k tokens, window +1 pts, 63s)
    2026-11-03 15:57Z kurisko-quad-15m-1h-maker-prereg DONE (gpt-6-luna / low, 4.3M tokens, window +38 pts, 782s)
  NEEDS A LOOK: 
    - STALLED: 2 card(s) ready, lane up, no allowance hold, but nothing ran for 3.7 h: read last_tick.txt and last_lane.txt on the lab host
    - only 2 card(s) left in the queue: add scoped cards (LAYER_LAB.md, Allowance)
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 30 | SRC open 3 (HIGH 0) closed 10 | CORE open 3 (HIGH 0) closed 31 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 2 (HIGH 1) closed 1 | DESK open 5 (HIGH 2) closed 9 | OPS open 29 (HIGH 14) closed 28 | INFRA open 8 (HIGH 3) closed 13 | UNGROUPED 1
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
