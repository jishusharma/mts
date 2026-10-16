# BLOCKED - Candle pattern detectors and DEV event table

## Verdict

**BLOCKED - the required DEV klines are absent.** The pre-registered DEV interval is 2022-01-01 through 2024-06-30 (`MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:10-12`). `Get-ChildItem F:/MTS/data/binance_tf/um/1h -File | Sort-Object Name` and the corresponding `4h` listing show monthly BTCUSDT archives only from 2025-11 through 2026-09 (checked 2026-10-16). There are therefore **0 DEV event rows** and no MFE/MAE aggregates or DEV trial result. No substitute data was used.

## What was built

- `patterns.py:2-26` contains pure closed-bar predicates for engulfing, pin-bar shape, inside bar, and doji. Their shape/thresholds map to the registered definitions at `PRE_REG_CANDLE_PILOT.md:41-48,56`; zero-range bars do not signal as required at line 42. No filters, rules, or tuning were added.
- `event_table.py:2-17` stamps each valid event at the signal bar timestamp and close, starts the forward path at `i+1`, normalizes forward favorable/adverse excursions by the signal bar range, and handles long and short extrema separately.
- `test_patterns.py:1-47` covers each pattern firing and its near-miss, forward-path start and timestamp, and short-side excursions.
- The test is registered in `scripts/dev/run_extra_tests.py:21`; `patterns.py` is registered as a `TOOL` in `MyTradingSys/system/wiring_registry.json:808-811`.

## Findings

| Severity | Evidence | Finding | Status |
|---|---|---|---|
| HIGH | `F:/MTS/data/binance_tf/um/{1h,4h}` listings; `PRE_REG_CANDLE_PILOT.md:10-12` | Required 2022-01-01..2024-06-30 DEV interval is unavailable; cannot produce DEV rows. | NOT_IN_DATA |
| LOW | `patterns.py:5-25`; `PRE_REG_CANDLE_PILOT.md:41-48,56` | The four requested shape detectors implement the registered predicates and thresholds without rule filters. | MATCH |
| LOW | `event_table.py:8-16`; `test_patterns.py:29-47` | Event time is taken from the signal bar and the forward slice begins at the following bar; both sides use side-correct extrema. | MATCH |

## Test output

- Command: `python -m pytest test_patterns.py -q` from `MyTradingSys/research/layer_lab/candle_pattern_event_table` — **6 passed** (2026-10-16).
- The prior report in this folder records a fail-first run of **1 failed, 5 passed** on the short-excursion case, followed by **6 passed** after the side-aware correction. The current implementation is green. No DEV data run was possible.

## Follow-up

Provide the missing 2022-01-01..2024-06-30 DEV klines in both requested timeframes. No trial row was appended to `TRIALS.md`: no DEV outcomes were run. The card remains blocked and must not be marked done.
