# Blind read: rsi_40_60_line_behaviour_2026-11-04

Method: behaviour_dev.csv (64 rows), behaviour_val.csv (16), plays_dev.csv (320), plays_val.csv (6) read and recomputed first (also contrast_dev.csv and context_dev.csv for Table 2 and the context claim); RESULT.md read afterwards. There is no raw event file, so recompute means: re-derive the cushion pick (largest |hold - break|, n >= 100, >= 40 days, per TF x line x side), binomial 95 % CI on hold (1.96 sqrt(p(1-p)/n)), benchmark differences, per-TF averages, DEV play counts and the VALIDATION join of each pick to its DEV row.

## Table 1 (picked cushion, 16 rows)

| Number | RESULT.md | Recomputed | |
|---|---|---|---|
| Pick cushions c (16 cells) | 5,1,1,5 / 5,2,1,5 / 5,1,1,5 / 5,2,5,5 | identical for all 16 | FOUND |
| n events per cell | 6026,1574,1693,6222,1456,627,461,1361,465,142,150,414,248,105,147,209 | identical | FOUND |
| hold / break / range, chop / inside, all 16 | as tabled (e.g. 1h 40 above 56.8/18.4/24.8) | identical to 0.1 pp | FOUND |
| benchmark hold/break/range | as tabled | identical | FOUND |
| hold minus benchmark (pp), 16 cells | +4.4,-0.7,-0.1,+6.7,+5.5,+1.9,+1.3,+2.7,-1.6,+2.6,-2.0,-3.0,+5.8,+0.6,+6.9,-7.2 | same | FOUND |
| Hold CIs (e.g. 1h 40 above [55.4,58.2], 12h 60 above [17.8,31.6]) | as tabled | binomial CI within 0.1 pp | FOUND |
| Mean over 16: hold +1.5 pp, break -1.7 pp | +1.5 / -1.7 | +1.50 / -1.73 | FOUND |
| Hold range 25-58, break 15-51, range 21-33 % | as stated | 24.7-58.2 / 15.3-50.7 / 21.1-32.7 | FOUND |
| Per-TF mean hold excess over all 16 grid rows: +1.95 (12h) to +4.98 (4h) | as stated | 12h 1.95, 1d 2.24, 1h 3.67, 4h 4.98 | FOUND |
| Per-TF break below benchmark by 2.3 to 5.6 | as stated | 2.34 (12h) to 5.56 (4h) | FOUND |
| RANGE 21-33 % in all 64 rows; inside 0-7 % | as stated | 21.1-32.7 %; inside max 7.4 % (rounds to 7) | FOUND |
| VALIDATION 1h 40 above c5 hold 53.6 vs 56.8; 1h 60 below 57.3 vs 58.2; 4h 60 below 53.9 vs 53.9 | as stated | 53.6/56.8; 57.3/58.2; 53.9/53.9 | FOUND |
| "12h and 1d VAL cells have 19-98 events" | 19-98 | 19-98 (n 19,21,25,26,42,58,98,19) | FOUND |
| 1h/4h VAL cells n >= 200 within ~5 pts of DEV | within ~5 | 1h 40 below 21.1 vs 25.5 (4.4), 1h 60 above 0.1, 4h 40 above 3.9 | FOUND |

## Table 2 (contrasts, 16 rows from contrast_dev.csv)

All 16 rows (n A / n B, hold A / B, difference, CI) match RESULT.md to the printed precision, including the "spans 0" flags (1h/4h/12h fresh_vs_mature and bull_vs_range, 1d htf_aligned, fresh_vs_mature, bull_vs_range). Plain-words figures: confluence +7 / +12 / +18 / +17, bias aligned -10 / -12 / -14 / -2 (1d unclear): FOUND. 16 of 16 FOUND.
Context file: 10 context values average hold 37.4-43.0 %, break 28.8-33.1 % (RESULT: 37-43 / 29-33), confl_1plus 42.9 vs confl_0 37.4 (RESULT: 43 vs 37), reg_bear empty: FOUND (4).

## Table 3 and play counts

| Number | RESULT.md | Recomputed | |
|---|---|---|---|
| 6 VAL picks: DEV n/days, net, CI (joined to plays_dev) | 39/38 +7.51 [2.01,13.02]; 49/48 +4.42 [0.94,7.91]; 58/54 +2.22 [-1.11,5.56]; 86/79 +2.14 [0.25,4.04]; 37/37 +1.85 [-1.29,4.99]; 57/53 +1.82 [-0.95,4.60] | identical | FOUND (6) |
| 6 VAL picks: n/days, net, CI, Holm, verdict | 2/2 +1.44 [-5.02,7.89] 1.00; 5/5 +4.59 [-0.26,9.43] 0.38; 4/4 +1.61 [-7.62,10.83]; 8/8 -1.49 [-7.46,4.47]; 5/5 +4.39 [-5.71,14.50]; 9/7 +0.93 [-5.97,7.84]; all INCONCLUSIVE | identical (Holm 0.381, 1,1,1,1,1) | FOUND (6) |
| Cells with n >= 30 | 214 | 214 of 320 | FOUND |
| Cells with DEV CI lo > 0 | 15 (7 %) | 15 (7.0 %) | FOUND |
| Mean net, ALL context: bounce +0.005, wait +0.028; medians -0.16, -0.08 | as stated | +0.0046 / +0.0276; -0.156 / -0.083 | FOUND |
| Every play cell BLOCK | yes | 320 of 320 BLOCK | FOUND |
| Trials: rates 64, context 144, contrasts 16, plays 320 = 544 | 544 | 64 + 16 + 320 + (160 context rows, 16 reg_bear empty = 144) = 544 | FOUND |
| "smallest MDE 0.22 % on 1h" | 0.22 | minimum mde in plays_dev.csv is 0.2495 (1h, ALL, bounce) | DIFF |
| "vs 0.16 % allowed" | 0.16 | no allowed-threshold column in the files | not checkable |
| "DEV nets of +2 to +7.5 %" | +2 to +7.5 | +1.82 to +7.51 (rounding) | FOUND |

Counts: FOUND 47, DIFF 1 (smallest-MDE figure 0.22 stated vs 0.2495 in the CSV; the BLOCK conclusion is unchanged because the gate is still not met), not checkable 1.

VERDICT: MATCH
