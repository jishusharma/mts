# RESULT: Michael's stated trend lines vs trendline_core events (BTC DEV 2022-01-01..2024-06-30)

Verdict: **descriptive only. Go (conditional) for the alert card: detector events exist at all 5 kinds on 4h/1d; stated lines cannot be matched to detector lines because chart frames are not in the repo.**

Source of counts: committed DEV run `trendlines_2026-10-17/counts/CELLS.csv` (config wick_log_age500, tercile ALL). A re-run was NOT possible on this machine (no F:/MTS klines); the committed run reads DEV only (splits guard in count_only.py). VALIDATION/HOLDOUT untouched.

Stated lines: 11 statements in 8 of 10 videos (STATED_LINES.md). 8 of 11 reference oil/gold/Nasdaq (OURS keyword guess), not BTC; so BTC replay is a base-rate only, not a comparison.

| tf | eligibility arm | eligible lines n | first_touch n | all_touches n | break n | retested n | reclaimed n |
|---|---|---|---|---|---|---|---|
| 1d | A | 17 | 6 | 8 | 14 | 10 | 2 |
| 1d | B | 19 | 3 | 5 | 17 | 15 | 8 |
| 1d | V | 1 | 1 | 1 | 1 | 0 | 0 |
| 4h | A | 177 | 105 | 133 | 166 | 140 | 98 |
| 4h | B | 208 | 66 | 78 | 199 | 167 | 109 |
| 4h | V | 114 | 84 | 96 | 110 | 90 | 58 |

Stated-kind to event-kind map (OURS): support/resistance touch = first_touch/all_touches; break = break; retest = retested; none stated for reclaimed.

Cannot compare: line anchors/dates live only on chart frames (NOT_IN_DATA); non-BTC assets have no DEV klines here; 'trend line' ASR mentions are not a count of distinct lines.

Parameters: eligibility arms A/B/V, age cap 500, wick/log = OURS (TRENDLINE_CONTRACT.md); no parameter SOURCED from Michael (he states none numerically).

Go/no-go: GO for an alert-only card on first_touch/break/retested (event n large enough on 4h); no edge claim, no orders.
