# Development Status

Generated: 2026-11-11 02:30:02

## Git Status
CI green: ad67fc061 (2026-11-11 02:21:51 +0530) = origin/fast-track: OK
Layer pass: 0 of 40 fee-net row(s) carry a surviving PASS
GO-PRIVATE: A=0 B=1 TRIGGER B:carry_basis_2026-10-18 (2026-10-18)
LESSONS: digest in sync
Pages stale: 3
STALE mts_layer_map https://claude.ai/artifact/7eeXJJ9Sb44LaJeCu8jxfJ
STALE sim_desk https://claude.ai/artifact/KaPy7f5BKFsvmqin84DpyF
STALE mts_home https://claude.ai/artifact/8hKA1rhNRo6RAEdt5mtLg3

## Hand-over freshness (hand-overs are history: read disk and git, never quote them as current)
```
FRESH 2026-11-04 Unblock MTS coordinator, login C, 2026-11-04 (wave d-context-retest-11
```

## Gate Board
```
tom     G2  proof changed 257h ago | next: Live validation with drawn chart flags (d-live-validation; G3 blind marks dropped) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
fabio   G2  proof changed 257h ago | next: G1 coverage check, then live validation (d-live-validation) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
malkan  G2  proof changed 264h ago | next: Live validation (d-live-validation; G3 blind marks dropped); 1d/1w RSI divergence flags done (malkan_div_flags_2026-10-28) | proof: MyTradingSys/research/malkan_div_flags_2026-10-28/BTCUSDT_divergences.md, MyTradingSys/research/malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md
krown   G2  proof not on trunk | next: Live validation with drawn chart flags (d-live-validation; G3 blind marks dropped) | proof: MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md (commit f4a5182a)
NO GATE MOVED IN 24h: the next spawn targets a gate (LAYER_REBUILD_PLAN s5)
commits 24h: 194 = research 26% | claim/release 0% | other 74%  OVER 30% CAP
```

**Last 3 commits on origin/fast-track:**
```
ad67fc061 Merge remote-tracking branch 'origin/fast-track' into JIS-NB/arch-row2-1110
866ccbedd 4 Gemini blind reads landed (monday_clocks, news_study, news_weight, api_agent); plan log 20:58Z
ee0739c6e tasks: done gemini-blind-read-of-scripts-dev-api-age
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (750.7h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (750.7h)

## Recent Reports (newest 5, last 3 days)
- MyTradingSys/research/sim_desk/GUIDED_SESSION_PLAN_2026-11-10.md (2026-11-10 18:31) # Guided simulator session: how to read failures and look for an edge (plan by Lead C on F
- MyTradingSys/research/mts_doctor/REPORT_2026-11-09.md (2026-11-10 12:13) # MTS doctor report 2026-11-09
- MyTradingSys/research/mtf_lead_lag_2026-11-09/REPORT.md (2026-11-09 03:02) # Timeframe flip lead-lag, BTC 2019-2026 (mtf-timeframe-lead-lag-research)
- MyTradingSys/research/malkan_level_shorts_2026-11-09/REPORT.md (2026-11-09 02:45) # Malkan level short, BTC 4h, counted 2017-08 .. 2026-11
- MyTradingSys/research/news_effects_2026-11/REPORT.md (2026-11-08 14:43) # News effects on BTC and ETH: event catalogue v2 and measured reaction (2026-11-08)

## Screenshots
```
SHOTS landed 34: new 1, classified 33, read 0, done 0 | overdue(>24h) 34 | claims MATCH 0 MISMATCH 0 NOT_IN_DATA 0 | filed 0
  OVERDUE a05ef4efee82 classified app                                  | Antigravity Settings > mts-gemini project page: folder mts-gemini/, Security Preset Inherit Global, Local Permissions. Operator asked where the approval settings are.
  OVERDUE fa4f80543b00 classified app                                  | Antigravity mts-gemini project page scrolled: Local Permissions (File, Network, Terminal, Commands Outside Sandbox, MCP) and Customizations.
  OVERDUE e8a5a0751b51 classified app                                  | Antigravity Settings > General: Global Permissions Security Preset = Turbo Mode, Tool Permissions 8, Plan Review Policy Always Proceed. Operator asked where the approval settings are.
  OVERDUE 3a8568059f4f classified app                                  | Antigravity Settings > General lower part: Network Access Rules, Commands Outside Sandbox, Browser JS Execution Request Review; account jis jishusharma1985@gm.
  OVERDUE 7b4e1582397b classified app                                  | Claude desktop Settings > Claude Code > Remote Control folders; operator asks which Worktree toggle to pick for MTS folders
  OVERDUE 66562984c20d classified app                                  | Windows search 'control panel' shows only web results (no local app best match); operator reports Windows search broken
  OVERDUE f48076d6278d classified app                                  | Settings > System > Power & battery: Energy saver On, Power mode greyed Best Power Efficiency, two batteries; operator context for lid/keyboard and search problems
  OVERDUE b68e7af47e2c classified app                                  | Duplicate of earlier Windows search screenshot, control panel web-only results
  OVERDUE f0d63ededaae classified app                                  | Windows search after SearchHost restart: control panel still shows only web search results; operator says fix tried before did not work
  OVERDUE 833cc2d2678a classified app                                  | Duplicate of earlier search screenshot, web-only results after SearchHost restart
```

## Layer Lab (Codex)
```
Layer lab (Codex) at 2026-11-10 21:00Z: on
  This machine does not run the lab (it runs on JIS-NUC): the queue below is from the repo; allowance, runs and what needs a look are only known there.
  Queue: 12 ready
    tom-fabio-rebuild-from-beginner-videos-1109 [build, gpt-6-luna / medium]
    gemini-blind-read-of-vfi-py-vfi-engine-f [audit, gpt-6-luna / medium]
    tvfav-usage-adx-1107 [audit, gpt-6-luna / medium]
    gemini-blind-read-of-squeeze-py-bb-dev-q [audit, gpt-6-luna / medium]
    gpt-spec-tests-vfi-1108 [audit, gpt-6-luna / medium]
    gpt-spec-tests-squeeze-1108 [audit, gpt-6-luna / medium]
    gpt-spec-tests-cycles-1108 [audit, gpt-6-luna / medium]
    gpt-spec-tests-cycle-ma-clock-1108 [audit, gpt-6-luna / medium]
    gpt-rederive-v-recovery-low-sweep-1108 [audit, gpt-6-luna / medium]
    gpt-rederive-pre-us-failed-break-10sym-1108 [audit, gpt-6-luna / medium]
    gpt-rederive-fabio-cvd-1108 [audit, gpt-6-luna / medium]
    gpt-rederive-wt-extreme-cross-1108 [audit, gpt-6-luna / medium]
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 30 | SRC open 3 (HIGH 0) closed 10 | CORE open 3 (HIGH 0) closed 31 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 2 (HIGH 1) closed 1 | DESK open 5 (HIGH 2) closed 9 | OPS open 29 (HIGH 14) closed 28 | INFRA open 8 (HIGH 3) closed 13 | UNGROUPED 1
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
