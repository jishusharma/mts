# Development Status

Generated: 2026-10-11 21:17:46

## Git Status
**Branch:** jisnb/relay-1011154728 (the host that generated this file; yours may differ)

CI green: 003c94a (2026-10-11 20:00:41 +0530), 10 commit(s) behind origin/fast-track: RED: oldest ungreen commit is 1.3 h old - CI is failing, auto-deploy is idle; fix CI first
LESSONS: digest in sync

**Last 10 commits:**
```
6cdde0b release fabio-trade-ledger
2e02c1b relay: fabio ledger window t=6525-6775 (flat, no trade); handoff depth 36
39fba81 claim fabio-trade-ledger
83a53de Merge remote-tracking branch 'origin/fast-track' into jisnb/dsa
fc83682 desk: done 20261011-140307-nuc-register-ci-cd-scheduled-tasks-no-de
10e8804 desk: done 20261011-140621-nuc-set-up-codex-work-tree-and-codex-hom
1e36b30 desk: done 20261011-140930-nuc-run-offline-gate-and-report
16baea4 release fabio-trade-ledger
d335f44 fabio ledger: DyS79Eb92Ug t=6275-6525 flat, no trade; handoff
5d5e77e claim fabio-trade-ledger
```

## Queue Status
```
WORKER   no heartbeat yet (worker version 2 has not reached this queue)
QUEUE    waiting 0; running 0; replies 0; not yet verified 0
DSA-WORKER no heartbeat (not running); incoming_dsa 0; running 0
```

## In-Flight .new Files
- MyTradingSys\backtest\layers\fabio\htf_context_live.py.new (0.0h)
- MyTradingSys\backtest\layers\fabio\test_htf_context_live.py.new (0.0h)
- MyTradingSys\research\core_readiness_2026-09-27\harness\proof_direction_cases.py.new (0.0h)

## Recent Reports (last 7 days)
- MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md (2026-10-11 02:13) # DAX_BT_REPORT: untuned Tom core on DAX vs matched-proof BTC (card tom-dax-backtest)
- MyTradingSys/research/screenshot_context_2026-10-10/REPORT.md (2026-10-10 02:22) # T092 REPORT - what context does a single screenshot read get? (2026-10-10, Opus, JIS-NUC)
- MyTradingSys/research/rsi_divergence_mtf_2026-10-09/REPORT_T088.md (2026-10-09 21:25) # T089 RSI divergence on every timeframe (+ T091 operator long-range column)
- MyTradingSys/research/rsi_divergence_mtf_2026-10-09/REPORT.md (2026-10-09 21:06) # T089 RSI divergence on every timeframe (+ T091 operator long-range column)
- MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md (2026-10-09 09:09) # EXIT POLICIES REPORT (backtest C), 2026-10-09
- MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md (2026-10-09 07:01) # BTC volume research: buy volume, sell volume, exhaustion, patterns, time (2026-10-09)

## Screenshots
```
SHOTS landed 35: new 0, classified 1, read 0, done 34 | overdue(>24h) 0 | claims MATCH 323 MISMATCH 59 NOT_IN_DATA 73 | filed 2
```

## Daily Hygiene (scheduled)
```
(no hygiene run on this host yet: python scripts/dev/daily_hygiene.py, or register_cicd_tasks.ps1)
```

## Project Groups
```
GROUPS DATA open 5 (HIGH 0) closed 29 | SRC open 4 (HIGH 0) closed 9 | CORE open 4 (HIGH 0) closed 30 | LAYR open 8 (HIGH 2) closed 5 | EVID open 13 (HIGH 2) closed 4 | EXEC open 7 (HIGH 3) closed 10 | VIS open 1 (HIGH 0) closed 1 | DESK open 1 (HIGH 1) closed 9 | OPS open 12 (HIGH 3) closed 24 | INFRA open 7 (HIGH 3) closed 12
```

## Open Findings
- L6: 0bbace1 (part 1), 1542151 + 924d7a0 (part 2) Part 1 (re-arm) committed. Part 2 (PnL source = transaction log + session UPL, mainnet_pnl.py) IMPLEMENTED; open only the B149 question: settlement/funding are excluded and session UPL resets at 08:00 UTC, unverified on a captured testnet log (tool: execution/capture_txlog_settlement.py). Must close before mainnet
