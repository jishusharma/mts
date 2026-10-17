# Development Status

Generated: 2026-10-17 15:45:00

## Git Status
CI green: 614bbc88 (2026-10-17 15:12:46 +0530, 0.5 h old), 5 trunk landing(s) / 32 commit(s) behind origin/fast-track: CI running
LESSONS: digest in sync

## Gate Board
```
tom     G2  proof changed 12h ago | next: G3 blind marks (READER_PROTOCOL.md + g3_marks_2026-10-16) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
fabio   G2  proof changed 12h ago | next: G1 coverage check, then G3 | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
malkan  G2  proof changed 37h ago | next: G3 blind marks MAL-2/5, MAL-16/17 (g3_marks_2026-10-16) | proof: MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md
krown   G1  proof changed 65h ago | next: G2 (krown-g2: KROWN_SETUP_CATALOG.md) | proof: MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv
commits 24h: 417 = research 25% | claim/release 39% | other 36%  OVER 30% CAP
```

**Last 3 commits on origin/fast-track:**
```
45f6c5e3 Merge remote-tracking branch 'origin/fast-track' into claude/mts-operator-guide-0875b3
736704f6 Merge remote-tracking branch 'origin/fast-track' into claude/mts-live-market-reader-623b37
69b0d3de layers: index the tom audit card
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (163.9h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (163.9h)

## Recent Reports (newest 5, last 3 days)
- MyTradingSys/research/mts_doctor/REPORT_2026-10-17.md (2026-10-17 15:12) # MTS doctor report 2026-10-17
- MyTradingSys/research/wavetrend_2026-10-17/REPORT.md (2026-10-17 11:23) # WaveTrend: outside evidence, then MTS application
- MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md (2026-10-17 09:01) # EXIT POLICIES REPORT (backtest C), 2026-10-09
- MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md (2026-10-17 09:01) # FIRES_B1_REPORT - fire history of the kline-only live layers (worker B1, 2026-10-09)
- MyTradingSys/research/mfe_exit_2026-10-13/REPORT.md (2026-10-17 09:01) # MFE exit study: can exits be reverse-engineered from the peak-profit bar? (2026-10-13, J

## Screenshots
```
SHOTS landed 92: new 1, classified 17, read 1, done 73 | overdue(>24h) 14 | claims MATCH 762 MISMATCH 125 NOT_IN_DATA 198 | filed 15
  OVERDUE dfabf169cdc9 new        -                                    | 
  OVERDUE 19f84e6aa598 classified app                                  | Claude app: Mts dispatcher session (Haiku 5.5) showing TICK NOOP; operator asks why idle dispatcher keeps running every 10 min
  OVERDUE 11760405153e classified chart     BTCUSDT 1m   2026-10-15T14:13:00Z | Operator asks where a short with confluence/divergence would be: price spiked ~81,38x (upper BB) then slipped back under 81,146.6 top; OI 93.26K flat after drop, RSI 69 off 77, StochRSI crossing down
  OVERDUE 1fdb4681c81e classified chart     BTCUSDT 1m   2026-10-15T14:15:00Z | Positioning panels after the 14:10 squeeze: Net Shorts collapsed ~1.3K->529, Net Longs(New) falling 1K->175, agg CVD rolling over -4.02K, OI flat 93.21K, price 81,025 under 81,146.6
  OVERDUE 34a949f8dc68 classified chart     BTCUSDT 1m   2026-10-15T14:22:00Z | Operator marks 1m bearish RSI divergence: price equal/higher high ~81,3xx (14:10 vs 14:18) while RSI lower high 77->~68; CVD lower high, low volume retest; price back on 81,146.6
  OVERDUE bfa91af3c34c classified other                                | Windows java.exe 0xc0000142 Application Error dialog; operator asked to investigate
  OVERDUE ab7581a78683 classified other                                | Chrome performance settings page, Memory Saver already on Maximum; operator confirming it was already set
  OVERDUE 9a9c9984cef2 classified other                                | Chrome Task Manager Browser tab: browser processes ~363MB total small; operator checking Chrome memory
  OVERDUE 531f784f2aee classified other                                | Chrome Task Manager Tabs & extensions: Deribit tab 918MB, Subaccounts 480MB, Gmail 377MB, CoinGlass tabs ~200-310MB each; operator checking Chrome memory
  OVERDUE 11a99a48fa09 classified app                                  | Task Manager: Defender 32% CPU, Claude 25%, PowerShell(7) 12.5%; operator says Defender spikes when Claude starts/stops
```

## Layer Lab (Codex)
```
Layer lab (Codex) at 2026-10-17 10:15Z: on
  This machine does not run the lab (it runs on JIS-NUC): the queue below is from the repo; allowance, runs and what needs a look are only known there.
  Queue: 12 ready
    malkan-hindi-rows-gpt-read [audit, gpt-6-astra / low]
    krown-catalogue-gpt-audit [audit, gpt-6-astra / low]
    gpt-formulas-rederive [audit, gpt-6-astra / low]
    gptb-candle-pattern-event-table [build, gpt-6-luna / medium]
    gptb-volume-event-table [build, gpt-6-luna / medium]
    gptb-malkan-rsi-event-table [build, gpt-6-luna / medium]
    gptb-cc-msb-event-table [build, gpt-6-luna / medium]
    gptb-fabio-escalation-event-table [build, gpt-6-luna / medium]
    gptb-rsi-reclaim-event-table [build, gpt-6-luna / medium]
    gptb-session-momentum-event-table [build, gpt-6-luna / medium]
    gptb-fabio-lvn-touch-event-table [build, gpt-6-luna / medium]
    gptb-turn-of-candle-event-table [build, gpt-6-luna / medium]
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 29 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 2 (HIGH 1) closed 9 | OPS open 18 (HIGH 6) closed 25 | INFRA open 7 (HIGH 3) closed 12
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
