# Development Status

Generated: 2026-10-19 16:53:48

## Git Status
CI green: bcabb044 (2026-10-19 16:31:20 +0530), 5 docs-only commit(s) ahead (no CI-gated path changed): OK
LESSONS: digest in sync
Pages stale: 3
STALE mts_control_room https://claude.ai/artifact/MNuodXmi5RiEihX7rFpqUp
STALE mts_layer_map https://claude.ai/artifact/7eeXJJ9Sb44LaJeCu8jxfJ
STALE mts_home https://claude.ai/artifact/8hKA1rhNRo6RAEdt5mtLg3

## Gate Board
```
tom     G2  proof changed 18h ago | next: G3 blind marks (READER_PROTOCOL.md + g3_marks_2026-10-16) | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
fabio   G2  proof changed 18h ago | next: G1 coverage check, then G3 | proof: MyTradingSys/research/setup_catalog_2026-10-15/SETUP_CATALOG.md
malkan  G2  proof changed 86h ago | next: G3 blind marks MAL-2/5, MAL-16/17 (g3_marks_2026-10-16) | proof: MyTradingSys/research/malkan_extract_2026-10-15/SETUP_SUMMARY.md
krown   G1  proof changed 13h ago | next: G2 (krown-g2: KROWN_SETUP_CATALOG.md) | proof: MyTradingSys/research/krown_ta101_2026-10-13/KROWN_RULES.csv
commits 24h: 541 = research 20% | claim/release 36% | other 44%  OVER 30% CAP
```

**Last 3 commits on origin/fast-track:**
```
f5645f83 desk: done 20261018-170620-aibridge-extension-v0-7-1-copy-scripts-a
8dc8394d artifacts-home-1019: Artifacts_Guy note, regenerated MTS Home (nothing republished)
3d0e1053 release artifacts-home-1019
```

## In-Flight .new Files
- MyTradingSys/backtest/layers/fabio/htf_context_live.py.new (213.0h)
- MyTradingSys/backtest/layers/fabio/test_htf_context_live.py.new (213.0h)

## Recent Reports (newest 5, last 3 days)
- MyTradingSys/research/gap_audit_2026-10-19/REPORT.md (2026-10-19 09:40) # MTS Critical-Gap Audit, Revalidation & End-to-End Roadmap (2026-10-19)
- MyTradingSys/research/mts_doctor/REPORT_2026-10-18.md (2026-10-19 03:53) # MTS doctor report 2026-10-18
- MyTradingSys/research/mts_doctor/REPORT_2026-10-19.md (2026-10-19 02:46) # MTS_Doctor report 2026-10-19: ship-gate speed and cost (fast path bd1b0c7d, Codex verifi
- MyTradingSys/research/live_loop_timeouts_2026-10-18/REPORT.md (2026-10-18 17:58) # Live-Loop Timeouts Post-B191 Audit Report
- MyTradingSys/research/binance_backtesting_2026-10-18/CLAUDE_HANDOFF.md (2026-10-18 10:02) # Claude handoff: Binance BTC backtesting foundations

## Screenshots
```
SHOTS landed 113: new 1, classified 25, read 1, done 86 | overdue(>24h) 24 | claims MATCH 911 MISMATCH 125 NOT_IN_DATA 221 | filed 15
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
Layer lab (Codex) at 2026-10-19 11:23Z: on
  This machine does not run the lab (it runs on JIS-NUC): the queue below is from the repo; allowance, runs and what needs a look are only known there.
  Queue: 8 ready
    lc-ladder-dev [build, gpt-6-luna / medium]
    lab-formula-spec-recount [build, gpt-6-luna / medium]
    lab-formula-spec-text [build, gpt-6-luna / medium]
    lab-planted-error-trial [build, gpt-6-luna / medium]
    tom-btc-other-setups [build, gpt-6-luna / medium]
    simulator-validation-planted-edge [build, gpt-6-luna / medium]
    argon-blind-read-7-frames [run, gpt-6-luna / low]
    one-timeframe-map-for-the-whole-toolchai [build, gpt-6-luna / medium]
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 30 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 8 (HIGH 1) closed 7 | EVID open 14 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 2 (HIGH 1) closed 9 | OPS open 18 (HIGH 6) closed 26 | INFRA open 7 (HIGH 3) closed 13 | UNGROUPED 1
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
