# B136 - Binance /futures/data endpoints broken since 2026-09-24 (OI, L/S ratios, taker vol) - fail-open

Opened 2026-10-05 by MTS-2026-10-05-1500Z-APP-ANA-operator-asks. Status OPEN. Severity P0 (live input dead 11 days, reported as HIGH confidence).
Master: research/OPERATOR_ASKS_2026-10-05.md section 1. Task list rows 1-2.

## Evidence
- SNAP open_interest.change_1h_pct = 0.0, direction flat, confidence HIGH on 3,338 of 3,338 snapshots 10-03..10-05.
- Public Binance 5m OI at the same time: 14:30Z 97,319 -> 14:40Z 96,211 BTC (-1.1%).
- src/main/java/datafeed/BinanceClient.java:43,47,51,66,71 use `/futures/runtime_data/...`; correct path `/futures/data/...`.
- Introduced in acca1d0 (2026-09-24 folder flatten). MarketDataSnapshot.java:218-229 swallows the exception, keeps "flat".
- Also explains MA 2026-10-05 G5 (oi_breakdown "unavailable").

## Fix (builder; Java producer = live path: build + gate, supervisor rebuilds/restarts)
1. Restore `/futures/data/` in the 5 methods.
2. Fail closed: on fetch failure emit confidence UNAVAILABLE (never HIGH on a default) for open_interest and oi_breakdown.
3. Tests (must fail on pre-change code): mocked 404 -> confidence != HIGH; recorded JSON -> change_1h_pct computed.
4. Grep for other `runtime_data/` strings inside URLs (none found in src/main besides these 5, 2026-10-05).
5. List consumers of open_interest/oi_breakdown; mark testnet results 09-24..fix as OI-tainted in TESTNET_STATUS.

## Done when
SNAP OI change matches public openInterestHist within 0.05% for 1 h; Maven + run_all_tests green.

## Taint note (2026-10-05)
OI-dependent results from 2026-09-24 (acca1d0 folder-flatten) to the B136 fix commit ran on a constant OI (change_1h_pct 0.0, direction flat, confidence HIGH). Treat open_interest-derived fields and any testnet/backtest conclusion that used them as OI-tainted. Fixed: all five futures-data URLs restored to /futures/data/; open_interest now emits UNAVAILABLE/LOW on fetch failure. oi_breakdown (buildOiBreakdown) was not changed in this session.
