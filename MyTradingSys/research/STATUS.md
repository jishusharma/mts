# Development Status

Generated: 2026-10-21 17:58:28

## Git Status
CI green: f25986227 (2026-10-21 16:49:21 +0530, 1.2 h old), 2 trunk landing(s) / 2 commit(s) behind origin/fast-track: RED: oldest ungreen commit is 1.0 h old - CI is failing, auto-deploy is idle; fix CI first
CI card: GREEN; CI on fast-track is green or still running; nothing to file
LESSONS: digest in sync
Pages stale: 1
STALE mts_home https://claude.ai/artifact/8hKA1rhNRo6RAEdt5mtLg3

## Hand-over freshness (hand-overs are history: read disk and git, never quote them as current)
```
STALE 2026-10-21 Live host move JIS-NB -> DESKTOP-F7IU69N: STAGED 2026-10-21, cutover N: 4 newer commits touch files it names (newest 2e6d4479b Live host move: laptop internet is a SIM, not Ethernet (operator decis). Verify on disk and git before quoting it.
FRESH 2026-10-21 Simulator desk: RSI and WaveTrend studies shipped 2026-10-21 (hand-ove
STALE 2026-10-21 Simulator desk: plug-in seam + Questions panel shipped 2026-10-21 (han: 2 newer commits touch files it names (newest 2b80ef52b sim-desk: RSI 40/60 (Malkan) and WaveTrend (LazyBear) studies on the d). Verify on disk and git before quoting it.
FRESH 2026-10-21 Simulator desk fixes shipped 2026-10-21 (hand-over, Opus lead; Fable r
FRESH 2026-10-21 LC3 ladder simulator (lc-ladder-dev) shipped 2026-10-21 (hand-over, Fa
FRESH 2026-10-20 Gate tiers by path: shipped 2026-10-20 (hand-over, Sonnet)
STALE 2026-10-20 Thinker hand-over 2026-10-20 (v1 plan written; nothing else changed): 2 newer commits touch files it names (newest 1d55f1a4e Thinker: D10 tuning to the operator's style (lean gates, claims off gi). Verify on disk and git before quoting it.
FRESH 2026-10-18 NB tandem coordinator 2026-10-18 hand-over (NB at 81% weekly on 2026-1
```

## Gate Board
```
tom     G2  proof changed 67h ago | next: G3 blind marks (READER_PROTOCOL.md + g3_marks_2026-10-16) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
fabio   G2  proof changed 67h ago | next: G1 coverage check, then G3 | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
malkan  G2  proof changed 135h ago | next: G3 blind marks MAL-2/5, MAL-16/17 (g3_marks_2026-10-16) | proof: MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md
krown   G1  proof changed 62h ago | next: G2 (krown-g2: KROWN_SETUP_CATALOG.md) | proof: MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv
NO GATE MOVED IN 24h: the next spawn targets a gate (LAYER_REBUILD_PLAN s5)
commits 24h: 105 = research 31% | claim/release 8% | other 61%  OVER 30% CAP
```

**Last 3 commits on origin/fast-track:**
```
442c96f41 sim-desk: ROADMAP.md (review so far, why the data is small, what is built when, 2-hour session plan)
2ead83703 usage bounds: unattended read budget 1M for every model and the Supervisor, note at 500k (operator 2026-10-21)
f25986227 Merge remote-tracking branch 'origin/fast-track' into claude/elastic-mirzakhani-bbb6e5
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (262.1h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (262.1h)

## Recent Reports (newest 5, last 3 days)
- MyTradingSys/research/context_load/REPORT.md (2026-10-21 10:23) # Context load at session start: measured, then trimmed (2026-10-21)
- MyTradingSys/research/layer_lab/candle_close_corrected_2026-10-14/REPORT.md (2026-10-21 03:14) # Corrected candle-close study — DEV findings
- MyTradingSys/research/layer_lab/candle_close_corrected_2026-10-14/analysis_v1/REPORT.md (2026-10-21 03:14) # Corrected phase-first BTC candle study
- MyTradingSys/research/gap_audit_2026-10-19/REPORT.md (2026-10-19 09:40) # MTS Critical-Gap Audit, Revalidation & End-to-End Roadmap (2026-10-19)
- MyTradingSys/research/mts_doctor/REPORT_2026-10-18.md (2026-10-19 03:53) # MTS doctor report 2026-10-18

## Screenshots
```
SHOTS landed 132: new 2, classified 29, read 1, done 100 | overdue(>24h) 29 | claims MATCH 992 MISMATCH 131 NOT_IN_DATA 238 | filed 17
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
Layer lab (Codex) at 2026-10-21 12:28Z: on
  This machine does not run the lab (it runs on JIS-NUC): the queue below is from the repo; allowance, runs and what needs a look are only known there.
  Queue: 5 ready
    lab-formula-spec-recount [build, gpt-6-luna / medium]
    lab-formula-spec-text [build, gpt-6-luna / medium]
    lab-planted-error-trial [build, gpt-6-luna / medium]
    tom-btc-other-setups [build, gpt-6-luna / medium]
    argon-blind-read-7-frames [run, gpt-6-luna / low]
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 30 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 2 (HIGH 1) closed 9 | OPS open 19 (HIGH 6) closed 26 | INFRA open 7 (HIGH 3) closed 13 | UNGROUPED 1
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
