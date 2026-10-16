# BLOCKED - Candle pattern detector and DEV event table

## Verdict

**BLOCKED - required DEV klines are missing.** The requested `F:/MTS/data/binance_tf/um/1h` and `4h` folders contain only monthly BTCUSDT archives from 2025-11 through 2026-09. The registered DEV interval is 2022-01-01 through 2024-06-30 for hourly data (`MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:10-12`). Therefore no DEV event rows, counts, MFE/MAE totals, or `TRIALS.md` entry were produced. Supply those DEV archives to unblock.

## Work completed

- `patterns.py` provides pure predicates for engulfing, pin-bar geometry, inside bar, and doji. Definitions cite the registered notation and pattern thresholds (`PRE_REG_CANDLE_PILOT.md:41-48,56`). Trend context is deliberately not applied to the shape detector.
- `event_table.py` stamps at the signal bar close and measures excursions from bars strictly after it, normalizing by the signal bar range (`event_table.py:8-14`). A short-side calculation bug discovered during this run was fixed: favorable movement for shorts now uses lows and adverse movement uses highs.
- `test_patterns.py` covers each detector's fire and near-miss, next-bar boundary, and short-side excursions.
- Test discovery and wiring are registered in `scripts/dev/run_extra_tests.py` and `MyTradingSys/system/wiring_registry.json`.

## Evidence

| Severity | Evidence | Finding | Status |
|---|---|---|---|
| HIGH | `F:/MTS/data/binance_tf/um/1h` and `/4h` directory listings: monthly files span 2025-11 through 2026-09; `PRE_REG_CANDLE_PILOT.md:10-12` | Required hourly DEV interval 2022-01-01..2024-06-30 is unavailable. No input substitution was used. | NOT_IN_DATA |
| MED | `test_patterns.py` short excursion case; `event_table.py:11-15` | The initial implementation returned zero short MFE due to applying the long-side extrema. Fixed with side-aware favorable and adverse extrema. | FIXED |
| LOW | `patterns.py:5-25`; `PRE_REG_CANDLE_PILOT.md:41-48,56` | Detector predicates implement specified shape definitions without rule filters or tuning. | MATCH |

## Test output

- Red regression check: `python -m pytest test_patterns.py -q` from `MyTradingSys/research/layer_lab/candle_pattern_event_table` ? **1 failed, 5 passed** (`test_short_event_excursions_use_favorable_low_and_adverse_high`; prior short MFE was 0.0, expected 0.75R).
- Green: same command after correction: **6 passed**.

## Follow-up

Provide the missing 2022-01-01..2024-06-30 hourly archives (including inputs needed to construct both requested timeframes). No follow-up card was created. Card not marked done because DEV data is missing, per unattended lab instruction.
