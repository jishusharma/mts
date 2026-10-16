# BLOCKED - Candle pattern detectors and DEV event table

## Verdict

**BLOCKED - required DEV klines are not present.** The registered hourly DEV period is 2022-01-01 through 2024-06-30 (`MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:9-12`). Available archive names in `F:/MTS/data/binance_tf/um/1h` and `4h` span 2025-11 through 2026-09 only (checked with `Get-ChildItem ... | Sort-Object Name`). Thus neither timeframe contains bars in the requested DEV period; event row count is **0** and no MFE/MAE result is reported.

## What was built

- `patterns.py:1-26`: pure predicates for engulfing, pin-bar shape, inside bar, and doji. The engulfing, wick, doji and zero-range definitions follow `PRE_REG_CANDLE_PILOT.md:41-48,56`. Signals are evaluated on the supplied closed bar; no filters, rules, or tuning are added.
- `event_table.py:1-17`: event timestamp/price use the signal bar close, and the forward slice begins at `i+1`; excursions are normalized by signal-bar high-low range.
- `test_patterns.py:1-45`: synthetic positive and near-miss examples for every detector, event close timestamp and next-bar forward path, and short-side extrema.
- Registration: test listed in `scripts/dev/run_extra_tests.py:21`; `patterns.py` is registered as a research `TOOL` in `MyTradingSys/system/wiring_registry.json:808-811`.

## Findings

| Severity | Evidence | Finding | Status |
|---|---|---|---|
| HIGH | `PRE_REG_CANDLE_PILOT.md:9-12`; directory listings of `F:/MTS/data/binance_tf/um/{1h,4h}` | Required DEV-period klines are absent; no DEV event table or outcomes can be generated. | NOT_IN_DATA |
| LOW | `patterns.py:5-26`; `PRE_REG_CANDLE_PILOT.md:41-48,56` | Four requested shape detectors are implemented as pure functions with the registered shape thresholds. | MATCH |
| LOW | `event_table.py:3-17`; `test_patterns.py:29-45` | Signal is stamped at close and forward excursion begins at the following bar; long and short extrema are side-aware. | MATCH |

## Test output

- Red-first evidence: the read-only context pack captured the pre-existing report, whose prior run failed the short-side excursion assertion (1 failed, 5 passed); this exposed an adverse/favorable extrema issue. The corrected side-aware implementation was then green.
- Command: `python -m pytest MyTradingSys/research/layer_lab/candle_pattern_event_table/test_patterns.py -q` ? **6 passed** (2026-10-17; one pytest cache warning caused by an existing cache path).
- No DEV event run was possible; no row was appended to `MyTradingSys/research/layer_lab/TRIALS.md`.

## Follow-up

Provide the pre-registered 2022-01-01 through 2024-06-30 DEV klines for 1h and 4h. Card remains blocked; it must not be marked done.
