# Development Status

Generated: 2026-10-12 00:48:05

## Git Status
**Branch:** jis-nuc/relay (the host that generated this file; yours may differ)

CI green: eec03a1 (2026-10-12 00:24:08 +0530), 3 commit(s) behind origin/fast-track: CI running
LESSONS: digest STALE (synced de2de3a7, now ad79e76d): read the new LESSONS_LEARNED.md entries (git diff), add their rule lines to LESSONS_DIGEST.md, update the blob

**Last 10 commits:**
```
d0c4705 CODEX_BRIDGE: correct budget policy (NB account is the low one) and note NUC data limits
0a47d9d Q31: NB dispatcher yields to NUC (--peer-quiet-min 90), fixed hourly
ac52bc7 TWO_HOST: correct the budget facts - NUC is the primary, NB should yield
eec03a1 TWO_HOST: NB stays primary (no peer flag) while NUC budget is low
9d55313 release backtest-readiness-template
931d9f5 Backtest readiness: 12-item pre-registration template (card backtest-readiness-template)
586e717 claim backtest-readiness-template
0a4fdb4 Relay prompts: dispatcher is the relay worker on every host; TWO_HOST.md
336f1d2 release relay-two-host-standby
015dedc Merge remote-tracking branch 'origin/fast-track' into fast-track
```

## Queue Status
```
WORKER   no heartbeat yet (worker version 2 has not reached this queue)
QUEUE    waiting 0; running 0; replies 0; not yet verified 0
DSA-WORKER no heartbeat (not running); incoming_dsa 0; running 0
```

## In-Flight .new Files
- MyTradingSys\backtest\layers\fabio\htf_context_live.py.new (0.5h)
- MyTradingSys\backtest\layers\fabio\test_htf_context_live.py.new (0.5h)
- MyTradingSys\research\core_readiness_2026-09-27\harness\proof_direction_cases.py.new (0.5h)

## Recent Reports (last 7 days)
- MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md (2026-10-11 21:39) # BIGMOVES REPORT (big-move ground truth, backtest A)
- MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md (2026-10-11 21:39) # FIRES_B1_REPORT - fire history of the kline-only live layers (worker B1, 2026-10-09)
- MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md (2026-10-11 02:13) # DAX_BT_REPORT: untuned Tom core on DAX vs matched-proof BTC (card tom-dax-backtest)
- MyTradingSys/research/screenshot_context_2026-10-10/REPORT.md (2026-10-10 02:22) # T092 REPORT - what context does a single screenshot read get? (2026-10-10, Opus, JIS-NUC)
- MyTradingSys/research/rsi_divergence_mtf_2026-10-09/REPORT_T088.md (2026-10-09 21:25) # T089 RSI divergence on every timeframe (+ T091 operator long-range column)
- MyTradingSys/research/rsi_divergence_mtf_2026-10-09/REPORT.md (2026-10-09 21:06) # T089 RSI divergence on every timeframe (+ T091 operator long-range column)
- MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md (2026-10-09 09:09) # EXIT POLICIES REPORT (backtest C), 2026-10-09
- MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md (2026-10-09 07:01) # BTC volume research: buy volume, sell volume, exhaustion, patterns, time (2026-10-09)

## Screenshots
```
SHOTS landed 0: new 0, classified 0, read 0, done 0 | overdue(>24h) 0 | claims MATCH 0 MISMATCH 0 NOT_IN_DATA 0 | filed 0
```

## Daily Hygiene (scheduled)
```
(no hygiene run on this host yet: python scripts/dev/daily_hygiene.py, or register_cicd_tasks.ps1)
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 29 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 10 (HIGH 2) closed 5 | EVID open 13 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 2 (HIGH 1) closed 9 | OPS open 15 (HIGH 4) closed 24 | INFRA open 7 (HIGH 3) closed 12
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
