# FOLLOW-UP: candle-flip cells vs a session-adjusted null (card flip-engine-follow-up-session-adjusted-s)

Regime mix: score 2025-01-01..now: 96 weeks: bull 23 (24%) | bear 0 (0%) | range 73 (76%) | n/a 0 (0%)
Regime mix: fit 2024-01-01..2025-01-01: 53 weeks: bull 35 (66%) | bear 0 (0%) | range 18 (34%) | n/a 0 (0%)

**Verdict: with volatility spread over the UTC day (session-adjusted null), 2 of the 7 cells that survived the recalibrated baseline still survive it at Holm m = 48 (G1 split/Asia/at, G2 aligned/Asia/at); 5 do not. Against the session-adjusted null itself, 5 of the 7 still count. The gains stay tiny (Brier moves in the 4th-5th decimal) and the whole score window is in the burned holdout, so this is a calibration check of a context probability, not an edge claim; no trade, no fee-net return exists to report. A fresh-data run is pre-registered in `PRE_REG.md` (Follow-up section) and has not been run.**

## What changed vs `RESULT.md`

Only the clock of the null. `RESULT.md` spends the bar's variance evenly over time (`t_left`). Here it is spent by an hour-of-day volatility profile fitted on 2024 only (`session_null.py`; mean squared 1m log return per UTC hour, mean 1; OURS): `t_left_s` = profile weight of the minutes left in the bar / mean profile weight of the 14 prior bars. `d` (ATR14/1.5958) is unchanged, null P(keeps) = Phi(|d|/sqrt(t_left_s)). The recalibrated baseline is refitted on (|d|, t_left_s) with the same bins. Same bars, rows, windows, week clusters, Holm and Brier rules (`flip_model.evaluate` imported unchanged). Check: the flat recomputation on the same table gives 16 / 15 / 9 / 7 counted cells, identical to the committed `cells.csv`.

Profile (UTC hour 00..23): 00: 0.972, 01: 1.217, 02: 0.830, 03: 0.648, 04: 0.544, 05: 0.535, 06: 0.604, 07: 0.602, 08: 0.663, 09: 0.640, 10: 0.583, 11: 0.612, 12: 1.230, 13: 1.396, 14: 1.953, 15: 1.592, 16: 1.335, 17: 1.344, 18: 1.142, 19: 1.215, 20: 1.333, 21: 1.171, 22: 1.129, 23: 0.712

## The 7 cells (score window, open-colour)

| cell | n | bars | weeks | realised | flat null | session null | delta flat | delta session | delta2 flat base | delta2 session base | Brier null flat | Brier null session | Brier cond (session null) | Brier session base | Brier cond2 | Holm48 session null | Holm48 session base | counts vs session null | counts vs session base |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 split/Asia/at | 3671 | 2077 | 97 | 0.8287 | 0.8701 | 0.8716 | -0.0414 | -0.0429 | -0.0249 | -0.0291 | 0.12316 | 0.12340 | 0.12163 | 0.12277 | 0.12202 | 4.36e-07 | 0.00497 | YES | YES |
| G1 split/EU/at | 2177 | 1241 | 96 | 0.8218 | 0.8686 | 0.8634 | -0.0468 | -0.0416 | -0.0297 | -0.0239 | 0.12525 | 0.12469 | 0.12314 | 0.12385 | 0.12340 | 0.000212 | 0.327 | YES | no |
| G2 aligned/Asia/at | 5352 | 1555 | 96 | 0.7954 | 0.8398 | 0.8604 | -0.0444 | -0.0650 | -0.0401 | -0.0672 | 0.13734 | 0.13953 | 0.13588 | 0.14113 | 0.13721 | 1.72e-09 | 3.78e-10 | YES | YES |
| G2 aligned/US/at | 8850 | 2659 | 97 | 0.8059 | 0.8484 | 0.8282 | -0.0425 | -0.0223 | -0.0382 | -0.0145 | 0.13602 | 0.13365 | 0.13318 | 0.13408 | 0.13389 | 0.0127 | 0.601 | YES | no |
| G2 aligned/US/inside | 44297 | 10025 | 97 | 0.7350 | 0.7478 | 0.7272 | -0.0128 | 0.0078 | -0.0277 | -0.0012 | 0.17368 | 0.17240 | 0.17237 | 0.17244 | 0.17253 | 0.264 | 1 | no | no |
| G2 split/Asia/inside | 31945 | 7207 | 97 | 0.7570 | 0.7104 | 0.7354 | 0.0466 | 0.0216 | 0.0254 | 0.0028 | 0.16444 | 0.16231 | 0.16178 | 0.16220 | 0.16220 | 3.79e-06 | 1 | YES | no |
| G3 aligned/US/inside | 10024 | 3286 | 97 | 0.7376 | 0.7377 | 0.7225 | -0.0000 | 0.0151 | -0.0213 | 0.0030 | 0.17233 | 0.17229 | 0.17201 | 0.17201 | 0.17205 | 0.658 | 1 | no | no |

## All 48 cells re-tested

Against the session-adjusted null: 11 count, 11 survive m = 48 (G1 aligned/Asia/at; G1 aligned/US/at; G1 split/Asia/at; G1 split/EU/at; G1 split/US/at; G2 aligned/Asia/at; G2 aligned/US/at; G2 split/Asia/inside; G2 split/EU/inside; G2 split/US/inside; G3 split/US/inside). Against the session-adjusted recalibrated baseline: 6 count, 4 survive m = 48 (G1 aligned/Asia/at; G1 split/Asia/at; G2 aligned/Asia/at; G2 split/US/inside). Full per-cell table: `followup_cells.csv` (`_flat` vs `_sess` columns).

Two cells that were not among the 7 now survive the session baseline (G1 aligned/Asia/at, G2 split/US/inside): they were not pre-selected, so they are named here, not added to the fresh-run family (no post-hoc additions).

## Reading

- Brier null changes with the clock (e.g. G2 aligned/Asia/at 0.13734 -> 0.13953), so the null's calibration by session matters; the 'at band' Asia cells keep a negative delta against every null tried, the US and inside cells mostly do not.
- Cells in G3 and G2 aligned/US/inside lose their effect once the clock is session-aware: their earlier gain was largely the null mis-spending variance across sessions.
- Statistical gains only: no materiality floor was pre-registered, the score window is the burned holdout, and `realised - null` of a few points is not a trading return. Nothing here is a fee-net out-of-sample edge; the test is on probability calibration of the open candle's colour.
