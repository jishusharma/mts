# Blind read: wt_extreme_cross_volmatch_2026-11 RESULT.md vs dev_cells.csv / summary.json

Method: loaded dev_cells.csv and summary.json first and computed counts, focal cells and net signs from them; RESULT.md was opened afterwards and every table number was machine-compared to the CSV (rounded as RESULT.md rounds). Study code not re-run; CSV cells taken as given, so this checks the prose and tables against the CSV, not the event simulation.

| Item | From CSV / JSON | RESULT.md | Match |
|---|---|---|---|
| Rows | 162 (BTC 54, ETH 54, POOL 54) | "162 rows" | yes |
| Cells with net @0.10 below zero | 161 (range -0.2029 to -0.0078 %) | "161 of 162 (-0.203 to -0.025 %)" | count yes; see note |
| Cells with net @0.14 below zero | 162 of 162 | "none at 0.14 %" | yes |
| Single net@0.10 >= 0 cell | ETH 15m sell prior_trend HTF with, n 242, 89 days, +0.026 (t 0.3), net14 -0.014 | same | yes |
| Verdict | VOLATILITY-ONLY (summary.json) | VOLATILITY-ONLY | yes |
| Focal POOL buy 1m against | n 15208, days 875, matched -0.010 (t -3.2), p 0.999 | same | yes |
| Focal 1m prior_trend | 8203, 458, -0.010 (-2.4), p 0.992 | same | yes |
| Focal 15m against | 964, 506, +0.013 (0.3), p 0.371 | same | yes |
| Focal 15m prior_trend | 512, 269, -0.046 (-1.0), p 0.840 | same | yes |
| Holm passes | 0 of 4; min days 269 | "0 of 4, >= 269 days" | yes |
| Focal unmatched excess (t) | 0.045 (8.6), 0.044 (6.1), 0.251 (5.6), 0.223 (4.1) | same | yes |
| Per symbol / pooled table | 18 rows x 8 numbers = 144 numbers (n, days, unmatched excess and t, matched excess and t, net10, net14) | | 144 of 144 match, 0 diffs |
| BTC reproduction futures column | 15935 / 7433 / 1422 / 476 / 243; unmatched 0.013 (3.7), 0.033 (5.4), 0.105 (4.3), 0.211 (3.7), 0.238 (3.3) | same | yes (spot column not checkable here, no spot file) |
| Regime mix line (summary.json) | BTC 130 wk bull 25 / bear 0 / range 105; ETH 130 wk bull 11 / bear 0 / range 119 | same, percentages 19/0/81 and 8/0/92 | yes |

Notes (diffs listed, none changes a verdict):
1. Range wording: RESULT.md says the 161 negative net10 cells span "-0.203 to -0.025 %". The CSV's least-negative net10 is -0.0078 %, not -0.025 %. The -0.025 figure is the ETH 15m buy prior_trend cell (shown in its table), but a cell closer to zero exists (-0.0078). Minor prose diff, 1.
2. Reading item 1 says matched excess is "-0.05 .. +0.02 %" on both symbols. Across all 162 CSV cells matched excess spans -0.204 to +0.085 % (12 cells >= 0, all buy / HTF against, mostly 15m or prior_trend). The statement holds for the focal and all-tag cells shown but not for the whole CSV. Prose-range diff, 1.
3. Item 2 "mostly NEGATIVE on the all-tag cells": 150 of 162 cells negative, consistent.

FOUND: 12 headline items and 144 table numbers match. DIFF: 2 (both prose ranges, numeric content correct; no table number differs).

VERDICT: MATCH
