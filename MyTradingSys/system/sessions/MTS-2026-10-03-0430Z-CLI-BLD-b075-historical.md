# MTS-2026-10-03-0430Z-CLI-BLD-b075-historical
surface: CLI | model: claude-sonnet-5-5 | role: BLD | branch: fast-track | status: closed
scope: CORE_READINESS_PLAN.md D1-L0 (L126-L128), B075. No process stopped; no live-imported file edited; Java NOT rebuilt in target/ (compiled in a scratch copy).

## T0 facts (pre-change MarketDataSnapshot.java, CRLF=1468 LF=0 sha256 138379C1...; verified)
(a) live calls in fetchHistoricalSnapshot: L1140 `ObjectNode spotPerpBasis = buildSpotPerpBasis(symbol);` and L1190 `root.set("oi_breakdown", buildOiBreakdown(symbol));`
(b) zeroed: L1161-1164 `tradeFlow.put("net_delta_{1m,5m,15m,1h}", 0.0);` L1130 `cond.put("book_imbalance", 0.0);` L1175 `fund.put("current_rate", 0.0);`
(c) L1191-1194 builds `liquidationWarning` (status none / note "Historical snapshot; liquidation data not available."), never `root.set`. (Live path L240-243 builds it and does not attach either.)
(d) `buildSession` exists at L745 but with a 7-arg signature, not (klines): `buildSession(JsonNode klines1m, double priorDayClose, double currentPrice, double dailyVah, double dailyVal, double priorDayHigh, double priorDayLow)`; live call L376. Historical path has all 7 inputs, so the same call is used.
(e) CRLF=1468, LF-only=0, hash 138379c10a5f4617.
After: CRLF=1493, LF-only=0, hash 3fceeae2. Backup: MarketDataSnapshot.java.pre_b075 (untracked, not staged).

## T1 changes (historical method only)
spot_perp_basis and oi_breakdown now `unavailableNode(..)` (confidence UNAVAILABLE, reason, null payload fields); trade_flow net_delta_* null + UNAVAILABLE; conditions.book_imbalance null; funding.current_rate null + UNAVAILABLE; root.liquidation_warning attached; root.session = buildSession(...); root.data_quality.unavailable_fields lists the 8 paths. New helper unavailableNode().

## T2
proof_direction (math_object_builder.py:430-445) already treats book None as aligned for long and short (`isinstance` guard fails on None; the 0.0/None rule was added 2026-09-30). No code change; test_book_imbalance_nodata.py::test_long_book_none_is_no_data already covered long.

## T3
Java HistoricalSnapshotNoLiveCallsTest (2 tests): fail-before 2/2 on .pre_b075 source, pass after. Python test_b075_book_none_short.py (2 tests): pass both before and after, because the behaviour pre-existed; fail-before is not achievable (T2).

## T4
Live runtime_data/snapshots/BTCUSDT_2026-10-03_1791001512149.json (04:25:11.266Z) vs historical regenerated for 2026-10-03T04:25:11.266Z (direct network, no proxy needed). Sections compared: daily_vp, weekly_vp, post_funding_vp, intraday_4h_vp, vwap, cvd, structure, prior_day, session = 89 leaf fields; 0 mismatches at 0.01 pct tolerance (current_price 84548.5 both).

## Notes for supervisor
- SetupCandidatesBuilder still emits proof.book_imbalance 0.0 and reads trade_flow.net_delta_1m via asDouble() (null -> 0.0), so candidates in historical snapshots still see 0.0 for those; out of scope, follow-up.
- funding.extreme / open_interest.* / conditions.oi_trend remain neutral defaults (not in the brief list); not in data_quality.
- Promotion/rebuild of the Java jar for the live process is supervisor-only.
