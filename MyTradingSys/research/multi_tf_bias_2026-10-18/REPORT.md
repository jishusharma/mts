# REPORT: multi-TF bias stack (BTCUSDT perp, DEV 2022-01-01..2024-06-30)

Result: **NO EDGE SHOWN.** The written stack (RULE.md) gives a bias on 1,348 of 5,469 four-hourly decisions (524 days); 8h-forward net of 12 bps it is
**-6.58 bps (SE 5.62, t -1.17)**, gross +5.42 bps. The single-TF baselines are worse in mean but the gap is not significant: 1h-only -9.75 (t -4.12), 1D-only -8.25 (t -2.70),
always-long -9.73. The 1h trades the stack removed average -10.78 bps (t -3.74) against -6.58 kept, a 4.2 bps gap well inside one SE (5.6). Descriptive, DEV only; no VALIDATION/HOLDOUT read.

| arm | n | days | mean net bps | SE | t | mean gross bps |
|---|---|---|---|---|---|---|
| STACK | 1348 | 524 | -6.58 | 5.62 | -1.17 | +5.42 |
| 1h-only (sign of last 1h delta) | 5469 | 912 | -9.75 | 2.37 | -4.12 | +2.25 |
| 1D-only (sign of last 1D delta) | 5464 | 911 | -8.25 | 3.06 | -2.70 | +3.75 |
| ALL-LONG reference | 5469 | 912 | -9.73 | 3.06 | -3.18 | +2.27 |
| 1h-only trades the stack removed | 4121 | 907 | -10.78 | 2.88 | -3.74 | +1.22 |
| 1D-only trades the stack removed | 4116 | 906 | -5.54 | 3.30 | -1.68 | +6.46 |

Numbers: `RESULTS.csv`; code `study.py`; rule `RULE.md` (frozen before the run, thresholds OURS: N=20, ER 0.30, edge 0.15, 4h step, 8h hold, 12 bps cost).
SE = day-clustered, sqrt(sum_day (sum (x-m))^2)/n (hand-checked in `test_study.py`, 17 tests, failed before study.py existed).

## What this does and does not say
* The stack side always equals the 1h flow side by construction, so "stack vs 1h-only" is a filter question, answered by the removed-trade rows: the filter raises the mean by about 4 bps, not distinguishable from zero (n 1348 vs 4121, SEs 5.6 and 2.9).
* Gross is positive for every flow arm (+1 to +6 bps) and cost is 12 bps: the flow sign carries no net edge at 8h on this window, with or without the stack.
* The 1D-only arm's removed trades look better than the kept stack ones (-5.5 vs -6.6 bps gross +6.5 vs +5.4): the stack filter did not select the better 1D trades.
* Stack trades overlap in time (8h hold, 4h step), so n counts double-weight adjacent decisions; day clustering absorbs that.

## Deviations from the card
1. The 2026-10-18 14:56Z live table (VWAP 81,431..81,694 by TF) is NOT reproduced: the 1m archive on disk ends 2024-06 and DEV is sealed to it. What is tested instead is the construction that makes the spread vanish: one VWAP summed from 1m bars is identical through any TF aggregation path (`test_vwap_same_for_every_tf_path`). VWAP is built and unit-tested but the DEV rule uses flow sign, range location and efficiency, not VWAP distance (VWAP does not enter the rule table).
2. The context table of `session_flow_context_2026-10-18` was not reused: it covers 2025-10..2026-02 sessions only (not DEV); no second context builder was written, the stack builds its own per-TF state from the 1m archive.
3. Engine label change (mts_math.py:354) untouched, report only.

## Trial ledger
Four rows appended to `layer_lab/TRIALS.md` (STACK, 1h-only, 1D-only, ALL-LONG reference).

## Left on the card
VALIDATION read only after a pre-registration of this exact rule; power: the stack SE is 5.6 bps, so a net effect under about 11 bps (2 SE) is invisible here.
