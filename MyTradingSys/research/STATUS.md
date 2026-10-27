# Development Status

Generated: 2026-10-27 23:58:02

## Git Status
CI green: 3fc30ac12 (2026-10-27 13:27:39 +0530, 10.5 h old), 56 trunk landing(s) / 95 commit(s) behind origin/fast-track: RED: oldest ungreen commit is 9.9 h old - CI is failing, auto-deploy is idle; fix CI first
CI card: GREEN; CI on fast-track is green or still running; nothing to file
LESSONS: digest in sync
Pages stale: 0

## Gate Board
```
tom     G2  proof changed 43h ago | next: G3 blind marks (READER_PROTOCOL.md + g3_marks_2026-10-16) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
fabio   G2  proof changed 43h ago | next: G1 coverage check, then G3 | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
malkan  G2  proof changed 43h ago | next: G3 blind marks MAL-2/5, MAL-16/17 (g3_marks_2026-10-16) | proof: MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md
krown   G1  proof changed 212h ago | next: G2 (krown-g2: KROWN_SETUP_CATALOG.md) | proof: MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv
NO GATE MOVED IN 24h: the next spawn targets a gate (LAYER_REBUILD_PLAN s5)
commits 24h: 225 = research 24% | claim/release 4% | other 72%  OVER 30% CAP
```

**Last 3 commits on origin/fast-track:**
```
2b11e51a7 lead: NUC - record the ordered test adapter (SellZone 120W, centre +)
51fa3cd67 Merge remote-tracking branch 'origin/fast-track' into claude/suspicious-jones-57835d
adefffc69 lead: card exhaust-broadcasts-skip-gateway-profile- (READY)
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (412.1h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (412.1h)

## Recent Reports (newest 5, last 3 days)
(none)

## Screenshots
```
SHOTS landed 34: new 1, classified 33, read 0, done 0 | overdue(>24h) 33 | claims MATCH 0 MISMATCH 0 NOT_IN_DATA 0 | filed 0
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
Layer lab (Codex) at 2026-10-27 18:28Z: on
  This machine does not run the lab (it runs on JIS-NUC): the queue below is from the repo; allowance, runs and what needs a look are only known there.
  Queue: 16 ready
    gap-g1-prereg-power [build, gpt-6-luna / medium]
    dsa-audit-08-split-trials [audit, gpt-6-luna / medium]
    lc-ladder-dev [build, gpt-6-luna / medium]
    lab-review-gate-harden [build, gpt-6-luna / medium]
    lab-formula-spec-recount [build, gpt-6-luna / medium]
    lab-formula-spec-text [build, gpt-6-luna / medium]
    lab-planted-error-trial [build, gpt-6-luna / medium]
    lab-trust-tag [build, gpt-6-luna / medium]
    lab-vendor-gate-harden2 [build, gpt-6-luna / medium]
    lab-review-gate-harden2 [build, gpt-6-luna / medium]
    tom-v2-btc-min-stop-width [build, gpt-6-luna / medium]
    tom-btc-other-setups [build, gpt-6-luna / medium]
    simulator-validation-planted-edge [build, gpt-6-luna / medium]
    gross-screen-refuse-a-changed-data-manif [build, gpt-6-luna / medium]
    argon-blind-read-7-frames [run, gpt-6-luna / low]
    one-timeframe-map-for-the-whole-toolchai [build, gpt-6-luna / medium]
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 30 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 2 (HIGH 1) closed 9 | OPS open 18 (HIGH 6) closed 26 | INFRA open 7 (HIGH 3) closed 13 | UNGROUPED 1
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
