STATUS: Session 2026-09-16 AM complete. Next session builds the session block.

# NEXT SESSION HANDOFF
# Written: 2026-09-16 12:00 UTC
# Mission: session block (schema_v5.1.0_spec.md, sixteen fields). Vision doc step 3.

## WHAT LANDED 2026-09-16 AM

- L18 CLOSED. start-trading-day.ps1 silent-exit instrumentation: exit phase tracking, catch, and phase in finally log line. Verified: Ctrl+C mid-sleep logged "APPARATUS END (finally) phase=sleeping".
- verify_data.ps1 built at scripts/tools/. Checks A (snapshot price vs Binance 1m close, same minute), B (spot/perp basis internal), C (price_vs_va vs any VP), E (state_code age under 90s). Passed live.
- Alias verify added to load.ps1. COMMANDS.md updated under BEFORE ANY WRITE.
- L28 OPENED. Loop exit orphans mvn/java child. Repro: Ctrl+C, Get-Process java shows 1. Fix candidate: match CommandLine datafeed.Main statemachine inside finally.
- PROJECT_VISION.md anchor blocker RESOLVED. Two anchors: UTC 00:00 for raw data calculation; US cash open (DST-aware) for session frame.

## MISSION FOR NEXT SESSION

### Task 1: Session block (schema_v5.1.0_spec.md, sixteen fields)
Outer frame. Vision doc says build first.
- Java side: session_open_price, session_high, session_low, gap_from_prior_close, session_vwap_anchor_utc, initial_balance_high, initial_balance_low. MarketDataSnapshot.java.
- Python side: range_position_pct, day_type, day_type_confidence, open_location, sweep_flag, liquidity_sweep_direction, gap_direction. mts_math.py.
- Config constant: initial_balance_window_minutes.
- Anchor: US cash open (13:30 UTC summer, 14:30 UTC winter, DST-aware).
- Output: snapshot.session object. Backward compatible.
- Close these before coding: initial balance window length; sweep flag scope (prior day only or prior day plus current session); day type source (build classifier or reuse VP shape).

### Task 2: context.ps1 (rolling 24h per-TF envelope)
After session block. Pure archive read. No schema change.
- Windows: 1h timeframe to 24h, 15m to 6h, 5m to 2h. Fixed 24-bar lookback.
- Fields per window: high, low, range_pct, slope_pct_per_hour, range_position_pct, slope_word (rising/falling/sideways).
- Output style like live.ps1.
- No regime label. Regime is a separate layer (TREND_REGIME_DETECTOR_SPEC.md).

### Task 3: regime_classifier.py (TREND_REGIME_DETECTOR_SPEC.md)
After context.ps1. Vote-based, per-cycle, session-tagged. Standalone. Writes JSON sub-object into state_code.json. No verdict consumption.

### Task 4 (deferred): RSI 40-60 (MalkanView) external read.

## LAYERED ARCHITECTURE (working order)

1. Per-cycle engine fields (LIVE).
2. Rolling 24h per-TF envelope (context.ps1, Task 2).
3. Session block (schema v5.1.0, Task 1).
4. Regime label (regime_classifier.py, Task 3).
5. RSI read (external, isolated).
6. Probability layer (parked, labels ~154 of 500).
7. Analyst verdicts (distant).

Rule 32 does not gate layers 2-4. It gates wiring when a layer changes a verdict.

## OPEN LOOPS
- L5, L6 NO EVIDENCE.
- L8 stop_day repro.
- L13 proof-change alert noise.
- L14-L28 in L_ITEMS_MASTER.md. L28 is this session's new one.
- L25 US cash open classifier DST bug. MarketDataSnapshot.java line 761. Fold into Task 1 since the session-open classifier is the same code path.

## CONSTRAINTS
- User runs commands, AI issues.
- No emoji in system files.
- Hash plus line count plus non-ASCII after any write.
- Read-only on live apparatus.
- Human commits all writes.

# END