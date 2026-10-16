# Candle pattern event table ? 2026-10-16

**BLOCKED ? required DEV klines are not present in this workspace.** Synthetic detector/event-boundary tests pass, but requested DEV event counts and outcomes cannot be computed.

## Work completed

- Added pure closed-bar predicates in `candle_pattern_event_table/patterns.py`: engulfing, pin bar, inside bar and doji. Engulfing follows pre-registered body/range rules (`PRE_REG_CANDLE_PILOT.md:42,45`); pin-bar wick geometry follows the hammer family (`:47`); inside-bar and doji thresholds follow `:56`. Pin bar intentionally omits trend context because this card asks for shape detection only.
- Added event-row forward excursion calculation in `event_table.py`, using signal close as event stamp/price, signal range as 1R, and bars strictly after the signal bar for MFE/MAE.
- Added five synthetic tests, including a fire/non-fire near-miss per detector and a next-bar-forward boundary check. Registered the test in `scripts/dev/run_extra_tests.py` and the two modules in `system/wiring_registry.json`.

## Data availability

Requested source: `F:/MTS/data/binance_tf/um/{1h,4h}`. Directory inspection found only `BTCUSDT-{1h,4h}-2025-11.zip` through `...-2026-09.zip` in both folders. The source study defines hourly DEV as 2022-01-01 through 2024-06-30 (`CANDLE_PATTERNS_RESEARCH_2026-10-04.md:12-13`) and separates later VALIDATION/HOLDOUT (`PRE_REG_CANDLE_PILOT.md:10-12`). Therefore **DEV data = NOT_IN_DATA**, no event rows were run, and no trial row was created.

## Test evidence

- Red first: `python -m pytest MyTradingSys/research/layer_lab/candle_pattern_event_table/test_patterns.py -q` ? failed at collection before implementation (`ModuleNotFoundError: patterns`).
- Green: from `MyTradingSys/research/layer_lab/candle_pattern_event_table`, `python -m pytest test_patterns.py -q` ? **5 passed**.

## Findings

| Severity | Evidence | Finding | Status / action |
|---|---|---|---|
| HIGH | `F:/MTS/data/binance_tf/um/{1h,4h}` listing; `CANDLE_PATTERNS_RESEARCH_2026-10-04.md:12-13` | Required 2022-2024 DEV klines are absent; only 2025-11 through 2026-09 files are available. | NOT_IN_DATA; provide authorized DEV archive and rerun event count. |
| LOW | `PRE_REG_CANDLE_PILOT.md:42,45,47,56` | Shape and thresholds implemented with no trade rules or tuning. | MATCH; synthetic tests green. |

No follow-up cards created. Card is intentionally not marked done because the required DEV event table cannot be populated.
