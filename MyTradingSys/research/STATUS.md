# Development Status

Generated: 2026-10-16 05:46:00

## Git Status
CI green: 0d98cd25 (2026-10-16 02:36:19 +0530, 3.2 h old), 46 trunk landing(s) / 164 commit(s) behind origin/fast-track: RED: oldest ungreen commit is 3.1 h old - CI is failing, auto-deploy is idle; fix CI first
CI card: FILED; filed ci-1bb1b39 (C:\Users\E-ngineers\IdeaProjects\BinanceDataFeed\.claude\worktrees\catalogue-p1-p2-830313\MyTradingSys\system\tasks\ci-1bb1b39.json); ship it: sync.py ship
LESSONS: digest in sync

## Gate Board
```
tom     G2  proof changed 3h ago | next: G3 blind marks (READER_PROTOCOL.md + g3_marks_2026-10-16) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
fabio   G2  proof changed 3h ago | next: G1 coverage check, then G3 | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
malkan  G2  proof changed 3h ago | next: G3 blind marks MAL-2/5, MAL-16/17 (g3_marks_2026-10-16) | proof: MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md
krown   G1  proof changed 31h ago | next: G2 (krown-g2: KROWN_SETUP_CATALOG.md) | proof: MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv
commits 24h: 376 = research 23% | claim/release 44% | other 32%  OVER 30% CAP
```

**Last 3 commits on origin/fast-track:**
```
7b5dbaf5 Merge remote-tracking branch 'origin/fast-track' into claude/fable-catalogue-audit-rebuild-679c65
578031f1 release ci-red-gate-discovery
139facc0 NEXT_SESSION: CI-FIX note (B150 step 3gd in every ship)
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (129.9h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (129.9h)

## Recent Reports (newest 5, last 3 days)
- MyTradingSys/research/pit_levels_2026-10-16/REPORT.md (2026-10-16 05:15) # Point-in-time levels, phases and cost: are the backtests reading what a trader could hav
- MyTradingSys/research/overnight_2026-10-16/MORNING_REPORT.md (2026-10-16 03:41) # Morning report - overnight 2026-10-15 evening IST -> 2026-10-16 (super-2, JIS-NB)
- MyTradingSys/research/observer_2026-10-15/OBSERVER_REPORT.md (2026-10-16 03:10) # Observer report, 2026-10-15 (cross-session alignment)
- MyTradingSys/research/pivot_pattern_audit_2026-10-14/REPORT.md (2026-10-14 19:56) # Pivot-pattern scope audit — 2026-10-14
- MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md (2026-10-14 17:41) # BTC candle-close research: first LAB result

## Screenshots
```
SHOTS landed 81: new 1, classified 10, read 0, done 70 | overdue(>24h) 1 | claims MATCH 733 MISMATCH 125 NOT_IN_DATA 183 | filed 14
  OVERDUE dfabf169cdc9 new        -                                    |
```

## Layer Lab (Codex)
```
Layer lab (Codex) at 2026-10-16 00:16Z: on
  This machine does not run the lab (it runs on JIS-NUC): the queue below is from the repo; allowance, runs and what needs a look are only known there.
  Queue: 4 ready
    lc-event-table [build, gpt-6-luna / medium]
    malkan-hindi-rows-gpt-read [audit, gpt-6-astra / low]
    krown-catalogue-gpt-audit [audit, gpt-6-astra / low]
    gpt-formulas-rederive [audit, gpt-6-astra / low]
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 29 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 2 (HIGH 1) closed 9 | OPS open 17 (HIGH 5) closed 25 | INFRA open 7 (HIGH 3) closed 12
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
