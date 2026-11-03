# Development Status

Generated: 2026-11-04 00:04:48

## Git Status
CI green: 2c2bcd80a (2026-11-03 23:55:27 +0530, 0.2 h old), 2 trunk landing(s) / 2 commit(s) behind origin/fast-track: CI running
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
tom     G2  proof changed 87h ago | next: Live validation with drawn chart flags (d-live-validation; G3 blind marks dropped) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
fabio   G2  proof changed 87h ago | next: G1 coverage check, then live validation (d-live-validation) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
malkan  G2  proof changed 211h ago | next: Live validation + 1d/1w RSI divergence flags (d-live-validation; G3 blind marks dropped) | proof: MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md
krown   G2  proof not on trunk | next: Live validation with drawn chart flags (d-live-validation; G3 blind marks dropped) | proof: MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md (commit f4a5182a)
NO GATE MOVED IN 24h: the next spawn targets a gate (LAYER_REBUILD_PLAN s5)
commits 24h: 189 = research 35% | claim/release 0% | other 65%  OVER 30% CAP
```

**Last 3 commits on origin/fast-track:**
```
124800210 ship: regenerated LAYERS.md
98d821708 fabio run_backtest: --dev-end (default 2026-06-25) clips 1m bars before split; holdout never read
2c2bcd80a Merge remote-tracking branch 'origin/fast-track' into DESKTOP-F7IU69N/planner-a-1103c-2
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (580.2h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (580.2h)

## Recent Reports (newest 5, last 3 days)
- MyTradingSys/research/mts_doctor/REPORT_2026-11-01.md (2026-11-02 01:35) # MTS doctor report 2026-11-01

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
Layer lab (Codex) at 2026-11-03 18:34Z: on
  This machine does not run the lab (it runs on JIS-NUC): the queue below is from the repo; allowance, runs and what needs a look are only known there.
  Queue: 5 ready
    gpt-spec-tests-live-aid-us-open-1103 [build, gpt-6-luna / medium]
    gemini-blind-read-volume-candles-facts-1103 [audit, gpt-6-luna / medium]
    gemini-blind-read-eagle-c36-wt-confluence-1103 [audit, gpt-6-luna / medium]
    gemini-mutation-rerun-research-kit-1103 [audit, gpt-6-luna / medium]
    gemini-rerun-cbp-scorecard-spec-tests-1103 [audit, gpt-6-luna / medium]
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 30 | SRC open 3 (HIGH 0) closed 10 | CORE open 3 (HIGH 0) closed 31 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 2 (HIGH 1) closed 1 | DESK open 5 (HIGH 2) closed 9 | OPS open 29 (HIGH 14) closed 28 | INFRA open 8 (HIGH 3) closed 13 | UNGROUPED 1
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
