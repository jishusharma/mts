# Development Status

Generated: 2026-10-23 17:29:39

## Git Status
CI green: af7812362 (2026-10-23 15:33:49 +0530), 28 docs-only commit(s) ahead (no CI-gated path changed): OK
LESSONS: digest in sync
Pages stale: 1
STALE mts_home https://claude.ai/artifact/8hKA1rhNRo6RAEdt5mtLg3

## Hand-over freshness (hand-overs are history: read disk and git, never quote them as current)
```
STALE 2026-10-23 Next card: nuc-unexpected-shutdown (hand-over, JIS-NUC session, 2026-1: 5 newer commits touch files it names (newest 8580a4117 NUC brief: watchdog hang during SMB copy after step 1). Verify on disk and git before quoting it.
FRESH 2026-10-23 Next card: tc4-desk-done-once (hand-over, super session DESKTOP-F7IU69
FRESH 2026-10-22 Next card: mid-turn-image-intake-gap (hand-over, plain pilot session o
FRESH 2026-10-21 Simulator desk R2: ETH 1m + symbol box (hand-over, Supervisor C, 2026-
FRESH 2026-10-22 Live host move coordinator (laptop) 2026-10-22: engine RUNNING from C:
STALE 2026-10-21 Live host move JIS-NB -> DESKTOP-F7IU69N: STAGED 2026-10-21, cutover N: 7 newer commits touch files it names (newest ec677b3bd LIVE_HOST_MOVE: register nuc_create_mts_shares.ps1, record that no NUC). Verify on disk and git before quoting it.
FRESH 2026-10-21 Simulator desk: RSI and WaveTrend studies shipped 2026-10-21 (hand-ove
STALE 2026-10-21 Simulator desk: plug-in seam + Questions panel shipped 2026-10-21 (han: 3 newer commits touch files it names (newest 8fd2c71ac sim-desk: symbol box (BTC/ETH) on RSI and WaveTrend, ETH 1m fetcher; s). Verify on disk and git before quoting it.
FRESH 2026-10-21 Simulator desk fixes shipped 2026-10-21 (hand-over, Opus lead; Fable r
FRESH 2026-10-21 LC3 ladder simulator (lc-ladder-dev) shipped 2026-10-21 (hand-over, Fa
FRESH 2026-10-20 Gate tiers by path: shipped 2026-10-20 (hand-over, Sonnet)
STALE 2026-10-20 Thinker hand-over 2026-10-20 (v1 plan written; nothing else changed): 2 newer commits touch files it names (newest 1d55f1a4e Thinker: D10 tuning to the operator's style (lean gates, claims off gi). Verify on disk and git before quoting it.
FRESH 2026-10-18 NB tandem coordinator 2026-10-18 hand-over (NB at 81% weekly on 2026-1
FRESH 2026-10-22 DOCTOR hand-over 2026-10-22
FRESH 2026-10-22 E2E run 2 (2026-10-22, Supervisor B)
```

## Gate Board
```
tom     G2  proof changed 115h ago | next: G3 blind marks (READER_PROTOCOL.md + g3_marks_2026-10-16) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
fabio   G2  proof changed 115h ago | next: G1 coverage check, then G3 | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
malkan  G2  proof changed 183h ago | next: G3 blind marks MAL-2/5, MAL-16/17 (g3_marks_2026-10-16) | proof: MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md
krown   G2  proof not on trunk | next: G3 blind marks (not started) | proof: MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md (commit f4a5182a)
NO GATE MOVED IN 24h: the next spawn targets a gate (LAYER_REBUILD_PLAN s5)
commits 24h: 229 = research 20% | claim/release 8% | other 72%  OVER 30% CAP
```

**Last 3 commits on origin/fast-track:**
```
be5f161d1 lease pipeliner: release by JIS-NB/0f9e82246827
0a42c104c Merge remote-tracking branch 'origin/fast-track' into claude/supervisor-c-machine-run-056dfd
14e43d101 desk: failed 20261023-055453-run-card-context-composite-v2-dev-read
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (309.6h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (309.6h)

## Recent Reports (newest 5, last 3 days)
- MyTradingSys/research/mts_doctor/REPORT_2026-10-23.md (2026-10-23 11:29) # MTS doctor report 2026-10-23
- MyTradingSys/research/mts_doctor/REPORT_2026-10-22.md (2026-10-23 04:19) # MTS doctor report 2026-10-22
- MyTradingSys/research/krown_audit_2026-10-22/REPORT.md (2026-10-22 16:37) # Krown layer audit: where it stands, what it adds, how it feeds the other layers (2026-10
- MyTradingSys/research/mts_doctor/REPORT_2026-10-21.md (2026-10-22 01:58) # MTS doctor report 2026-10-21
- MyTradingSys/research/context_load/REPORT.md (2026-10-21 10:23) # Context load at session start: measured, then trimmed (2026-10-21)

## Screenshots
```
SHOTS landed 136: new 4, classified 31, read 1, done 100 | overdue(>24h) 35 | claims MATCH 992 MISMATCH 131 NOT_IN_DATA 238 | filed 17
  OVERDUE dfabf169cdc9 new        -                                    | 
  OVERDUE 19f84e6aa598 classified app                                  | Claude app: Mts dispatcher session (Haiku 5.5) showing TICK NOOP; operator asks why idle dispatcher keeps running every 10 min
  OVERDUE 11760405153e classified chart     BTCUSDT 1m   2026-10-15T14:13:00Z | Operator asks where a short with confluence/divergence would be: price spiked ~81,38x (upper BB) then slipped back under 81,146.6 top; OI 93.26K flat after drop, RSI 69 off 77, StochRSI crossing down
  OVERDUE 1fdb4681c81e classified chart     BTCUSDT 1m   2026-10-15T14:15:00Z | Positioning panels after the 14:10 squeeze: Net Shorts collapsed ~1.3K->529, Net Longs(New) falling 1K->175, agg CVD rolling over -4.02K, OI flat 93.21K, price 81,025 under 81,146.6
  OVERDUE bfa91af3c34c classified other                                | Windows java.exe 0xc0000142 Application Error dialog; operator asked to investigate
  OVERDUE ab7581a78683 classified other                                | Chrome performance settings page, Memory Saver already on Maximum; operator confirming it was already set
  OVERDUE 9a9c9984cef2 classified other                                | Chrome Task Manager Browser tab: browser processes ~363MB total small; operator checking Chrome memory
  OVERDUE 531f784f2aee classified other                                | Chrome Task Manager Tabs & extensions: Deribit tab 918MB, Subaccounts 480MB, Gmail 377MB, CoinGlass tabs ~200-310MB each; operator checking Chrome memory
  OVERDUE 11a99a48fa09 classified app                                  | Task Manager: Defender 32% CPU, Claude 25%, PowerShell(7) 12.5%; operator says Defender spikes when Claude starts/stops
  OVERDUE c5aad5e179a0 classified app                                  | Operator's MTS Session Planner with 6 tasks selected; asks whether prompt matches selection
```

## Layer Lab (Codex)
```
Layer lab (Codex) at 2026-10-23 11:59Z: on
  This machine does not run the lab (it runs on JIS-NUC): the queue below is from the repo; allowance, runs and what needs a look are only known there.
  Queue: 4 ready
    lab-formula-spec-text [build, gpt-6-luna / medium]
    lab-planted-error-trial [build, gpt-6-luna / medium]
    t02-f3-fixtures-wlow-session-levels [build, gpt-6-luna / medium]
    t02-f3-fixtures-fabio-v3-grid [build, gpt-6-luna / medium]
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 30 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 3 (HIGH 1) closed 9 | OPS open 24 (HIGH 11) closed 26 | INFRA open 7 (HIGH 3) closed 13 | UNGROUPED 1
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
