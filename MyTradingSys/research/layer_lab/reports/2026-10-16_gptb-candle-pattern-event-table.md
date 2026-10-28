# BLOCKED - gptb-candle-pattern-event-table

**Verdict: BLOCKED - required DEV klines are absent.**

## What was checked / built

- Pre-registration fixes hourly DEV to 2022-01-01 through 2024-06-30 (`MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:9-12`). The `F:/MTS/data/binance_tf/um/1h` and `4h` archive listings contain 2025-11 through 2026-09 only (checked 2026-10-17 with `Get-ChildItem <dir> -File | Sort-Object Name`). Result: **0 DEV event rows**, no MFE/MAE output. No other period was substituted.
- Detector definitions and thresholds: `PRE_REG_CANDLE_PILOT.md:41-48,56`. Implemented pure engulfing, pin-bar-shape, inside-bar, and doji functions in `MyTradingSys/research/layer_lab/candle_pattern_event_table/patterns.py:1-26`.
- Forward excursion table in `MyTradingSys/research/layer_lab/candle_pattern_event_table/event_table.py:1-17`: event timestamp/price from signal close, future starts at next bar, MFE/MAE divided by signal range.
- Synthetic tests in `MyTradingSys/research/layer_lab/candle_pattern_event_table/test_patterns.py:1-45`; test registration at `scripts/dev/run_extra_tests.py:21`; helper registration at `MyTradingSys/system/wiring_registry.json:808-811`.

## Findings

| Severity | Evidence | Finding | Status |
|---|---|---|---|
| HIGH | `PRE_REG_CANDLE_PILOT.md:9-12`; 1h/4h archive listings | DEV input period is unavailable in both requested timeframes. | NOT_IN_DATA |
| LOW | `patterns.py:5-26`; `PRE_REG_CANDLE_PILOT.md:41-48,56` | Four requested detector shapes implemented without filters or tuning. | MATCH |
| LOW | `event_table.py:3-17`; `test_patterns.py:29-45` | Timestamp is signal close; forward bars start at i+1; direction-specific excursions covered. | MATCH |

## Tests

Red first: the read-only context pack captured the pre-existing report, whose pre-fix run failed the short-side excursion test (1 failed, 5 passed); the side-aware correction was green. Current command `python -m pytest MyTradingSys/research/layer_lab/candle_pattern_event_table/test_patterns.py -q`: **6 passed** (2026-10-17; cache warning only).

No trial row was added because no DEV result was run. `MyTradingSys/research/layer_lab/candle_pattern_event_table/REPORT.md` contains the implementation and test detail. Provide the registered DEV klines to resume.
