# Michael's trend lines vs trendline_core on BTC DEV (card tl-michael-lines-detect-alert, step 1)

Descriptive only. No forward return, no fee, no edge claim. DEV only (2022-01-01..2024-06-30); VALIDATION and HOLDOUT untouched (loader refuses any bar >= 2024-07-01; KLINE_DIGESTS.csv lists the bytes read).
Command: `python MyTradingSys/research/trendlines_2026-10-17/count_only.py --split DEV --tfs 1d,4h --out MyTradingSys/research/michael_lines_2026-11/counts` (27 s). Raw cells: `counts/CELLS.csv`.

## Stated lines (STATED_LINES.md)
11 stated-line rows in 8 of the 10 videos: oil 8, Nasdaq 1, gold 1, BTC 1. Kinds read from the words: mention 6, resistance 2, break 2, retest 1 (kind heuristic is OURS). Only one row (avnJKLxX4FY 00:02:19, BTC downward line) is on the asset we have DEV bars for; oil, gold and Nasdaq bars are not in the repo.

## Detector event counts, BTC DEV, primary family wick / log / age cap 500 (all slope terciles pooled)
Eligibility arms A, B, V overlap (a line can be eligible in several), so arm rows are not additive. Line totals use every line.

| tf | arm | eligible lines (support/resist) | first_touch | all_touches | break | retested | reclaimed |
|---|---|---|---|---|---|---|---|
| 1d | A | 17 (10/7) | 6 | 8 | 14 | 10 | 2 |
| 1d | B | 19 (7/12) | 3 | 5 | 17 | 15 | 8 |
| 1d | V | 1 (1/0) | 1 | 1 | 1 | 0 | 0 |
| 1d | all lines | 130 (86/44) | | 104 contact episodes | 119 lines broken | | |
| 4h | A | 177 (98/79) | 105 | 133 | 166 | 140 | 98 |
| 4h | B | 208 (119/89) | 66 | 78 | 199 | 167 | 109 |
| 4h | V | 114 (47/67) | 84 | 96 | 110 | 90 | 58 |
| 4h | all lines | 1004 (511/493) | | 882 contact episodes | 975 lines broken | | |

Sensitivity arms (wick/noage, wick/linear, close/log) are in `counts/CELLS.csv`; close/log gives far fewer lines (1d 30, 4h 232).

## Compared and not comparable
- Comparable by kind: support and resistance lines, break, retest. Michael's "break back on top", "test its trend line" and "lower high beneath this trend line" map to detector break and retested; "lines up with 50% level" has no detector event.
- Not comparable: the date anchors and price of every line except _LDxOX42NS8 (anchors in the chart frame, NOT_IN_DATA); asset (10 of 11 rows are not BTC, no bars here); his times are 2026-10, the DEV bars end 2024-06, so no line can be matched to a detector line, only kinds and counts.
- Parameters: detector parameters are the contract's (OURS unless PRE_REG says SOURCED); none of the thresholds come from Michael, who states no number for touch tolerance, pivot width or age.

## Go / no-go for the alert card
GO, conditional: build alert-only events (first_touch, all_touches, break, retested, reclaimed) for BTC on 4h and 1d only from the 4h arms A and B (n >= 66 first touches over 912 days) and 1d arm A/B as descriptive (n 3 to 6 first touches, too few to judge); NO-GO for 1d arm V (n = 1) and for any claim that his lines carry an edge, which needs a fee-net out-of-sample test. The alert card is live-path (CRITICAL): restart/reset-state, API-error and fail-closed tests required, no orders.

DECISION (OURS): the go line is about event availability only, because counts here cannot say whether the lines pay.
