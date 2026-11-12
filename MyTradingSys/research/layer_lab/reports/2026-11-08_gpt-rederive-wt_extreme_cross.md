MATCH=10 DIFF=1 NOT_IN_DATA=3 (wt_extreme_cross RESULT.md headline numbers; re-derived from dev_cells.csv only)

Producer: gemini-*. T0-ONLY: no independent ACCEPT; needs a non-Gemini reviewer.

| RESULT.md number | recomputed | verdict |
|---|---|---|
| 135 rows in dev_cells.csv | 135 | MATCH |
| 9 headline cells (tf x side x lvl): n, days, MFE mean/median, median pts, base MFE, excess (t), net (t), hit | all 9 rows equal the table at the printed precision | MATCH (9) |
| Regime mix 130 weeks: 25 bull / 105 range | regime_mix_dev.txt same | MATCH |
| "The only positive net cell in the 135: 15m buy -60, same_range, n 309, net +0.043 (t 0.7)" | 4 cells have net_mean > 0: 15m buy card same_range/against n314 +0.060 (t 1.05); 15m buy -60 same_range/all n309 +0.043 (t 0.70); 15m buy -60 same_range/against n160 +0.139 (t 1.37); 15m buy -60 prior_trend/with n62 +0.069 (t 0.81). The quoted cell is correct, but "only" is wrong. None has t above 1.4. | DIFF |
| Window DEV 2022-01-01..2024-07-01 | not in the CSV | NOT_IN_DATA |
| Text figures: 1m ret mean -0.001, maker net about -0.09, 11-02 bounce 100-250 pts | not in the CSV | NOT_IN_DATA |

The DIFF does not change the verdict: no positive cell is significant.
Limit: only the aggregated cells were checked. The event counts were not recounted from bars (no 1m data in this tree), so n is taken as given.
