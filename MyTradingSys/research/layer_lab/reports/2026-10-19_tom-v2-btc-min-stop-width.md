# Minimum-stop-width gate: completion and as-of causality fix

**DONE.** The existing optional research gate and fee/noise floor fixtures pass. Independent verification found and fixed a look-ahead defect in the N5 input estimator: an incomplete five-minute candle could enter the as-of value, and timestamped iterables ignored the window entirely. No market backtest, tuning, or protected-data read was performed.

## Confirmed defect and fix

`scripts/dev/tom_noise_units.py:79-129` previously filtered one-minute rows with timestamps <=asof, then treated any five-row aggregate as complete even if the fifth minute had not closed. Its iterable branch did not filter timestamps at all.

Independent synthetic fixture (DEV timestamp 2024-01-01): bucket 0 is H=101,L=99,C=100; bucket 1 ends with H=150,L=50,C=100. At minute 09:30 only bucket 0 has closed, so no TR with a preceding completed candle exists: N5=0. At minute 10:00 both are closed: TR=max(150-50,abs(150-100),abs(50-100))/100=1.0. Before the fix all three representations returned 1.0 at 09:30. An iterable extended with future extreme bars changed the minute-10 value from 1.0 to 99.99.

Fix:

- Apply the same `[window_start, cutoff)` row filtering to dictionaries, timestamped iterables and Bars1m.
- Retain aggregated candles only when `bucket_open + 5 minutes <= cutoff`.
- A date cutoff denotes the whole UTC day, ending at the next midnight; the final 23:55 candle remains included.
- Timestamp-less HLC fixtures remain supported without asof; an asof calculation now requires timestamps. Datetimes must declare a timezone rather than inherit a host-local interpretation (OURS API validation).

No fee, lookback, stop, or trading rule was changed. `tom_bt.run_variant(min_width=None)` remains unchanged and its identity fixture still passes. Stops are still dropped, never widened. The gate remains off by default; no live path was edited.

## Red / green validation

```
python -m pytest MyTradingSys/tests/test_tom_min_stop_width.py -q --tb=short
```

Before fix: **5 failed, 2 passed**. Failures reproduced premature candles for dict/iterable/Bars1m, iterable future leakage and accepting untimestamped as-of input.

```
python -m pytest MyTradingSys/tests/test_tom_min_stop_width.py MyTradingSys/tests/test_tom_noise_units.py MyTradingSys/tests/test_tom_through_ticks.py -q
```

After fix: **15 passed in 0.14s**. Coverage includes the exact five-minute close boundary, future-prefix invariance, end-of-UTC-day inclusion, timestamp/timezone validation, FORMULAS 12 true range, incomplete/gapped aggregation, the existing fee-floor worked example and default-off identity. `git diff --check` passed.

Independent read-only diff review: **ACCEPT**, no actionable defects. The reviewer checked cutoff equality, complete UTC dates, all three input forms and unchanged default-off behavior. Remaining test limitations: no explicit trailing-20-day lower-bound case or aware non-UTC datetime case; no market data was accessed. The reviewer inspected tests and did not duplicate the test run.

Expected arithmetic comes from FORMULAS.md section 12 and TOM_LAYER_V2_SPEC.md:312-335, not producer output. SOURCED inputs retained per the card: 0.88 width normalization and the 0.25 R fee ceiling; OURS lookback=20 UTC days, with 10/40 reported but not selected.

## Archived 10 / 20 / 40-day floor readout

The original shipped report `2026-10-18_tom-v2-btc-min-stop-width.md` records the as-of-2026-06-25 figures. Its N5 values are archived producer measurements, not independently recomputed in this session; no protected price rows were reopened. The old and new date-only row windows include the same complete day-end minute rows, so this cutoff fix changes intraday as-of behavior without requiring a new date-window study.

| Lookback (OURS) | Archived N5 | All-taker minimum width | Deribit maker-entry/taker-stop minimum width |
|---|---|---|---|
| 10 UTC days | 0.13746% | 0.40% | 0.20% |
| 20 UTC days | 0.15029% | 0.40% | 0.20% |
| 40 UTC days | 0.13640% | 0.40% | 0.20% |

Independent fee arithmetic: 0.10% / 0.25 = 0.40%; 0.05% / 0.25 = 0.20%. Each archived noise floor (0.88 times N5, roughly 0.12-0.13%) is smaller, so fees dominate all six readouts. Nothing is chosen on these results. They retain UNCHECKED result trust until the required independent base review.

Delivery receipt is separate: content commit, empty git cherry against origin/fast-track, and upstream report existence.
