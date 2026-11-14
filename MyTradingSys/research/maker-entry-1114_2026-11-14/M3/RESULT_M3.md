# RESULT_M3: NK6 confluence L2&L3&L5, maker entry at signal-bar close

VERDICT: FAIL (gates 2, 3, 6 fail; gate 5 moot). Maker entry improves net R from -0.112 (taker) to -0.093 per filled trade, still negative.

## Context
Phase gate as the original (daily ADX14/DI/SMA20-slope at D-1; matched direction only: LONG in UP/RANGE, SHORT in DOWN/RANGE). Session: all UTC hours. Signals, stop (max(1 ATR, 0.5% of L)), target 2R, 24-bar time stop frozen. Limit L = close of signal bar; fill model per PRE_REG (one tick through, 15 x 1m life, stop-before-fill cancels).

Regime mix: VAL signals UP 19% / RANGE 58% / DOWN 23%; DEV signals UP 24% / RANGE 53% / DOWN 23% (original bar mix: VAL UP 25 / RANGE 40 / DOWN 35).

## Baseline replication (original taker, next open, 12 bp, VALIDATION)
Original RESULT: n 1996, gross +0.084, net -0.112. Mine (original code copied unchanged, re-run): n 1996, gross +0.084, net12 -0.112, net6 -0.014. Exact match.

## Results
| | VALIDATION | DEV (reference) |
|---|---|---|
| signals | 1996 | 2991 |
| fills (rate) | 1890 (94.7%) | 2845 (95.1%) |
| taker baseline net R (12 bp, all signals) | -0.112 | -0.163 |
| maker net R per filled trade | -0.093 | -0.138 |
| maker gross R per filled trade | +0.040 | -0.022 |
| mean fee in R (maker model) | 0.133 | 0.116 |
| net R per signal (miss = 0) | -0.088 | -0.131 |
| adverse selection (orig gross, filled minus all) | -0.030 | -0.026 |
| taker net on filled subset vs all | -0.142 vs -0.112 | -0.188 vs -0.163 |
| CI95 per trade | [-0.156, -0.030] | |
| CI95 per UTC day | [-0.172, -0.009] | |
| ex best 5 days | -0.135 | -0.168 |

Exit types (VAL filled): {'time': 188, 'stop': 1141, 'target': 561}. Misses: {'no_through': 106}. THIN: no (fill rate far above 30%).

## Gates (VALIDATION)
1 n>=100: PASS (1890). 2 mean>0: FAIL. 3 CI lower>0: FAIL (trade -0.156, day -0.172). 4 placebo p<0.05: PASS (p=0.0010, placebo mean -0.188, 1000 draws, same fill model, 1890 fills per draw). 5 BH over 6 rows: not computable per row, moot. 6 ex-best-5>0: FAIL.

## Reading
- The close-of-bar limit fills 95% of the time (the next minute almost always trades one tick through the close), so there is almost no selection. The gain over taker is fees (maker entry and target 3 bp), not entry price. Gross falls from +0.084 to +0.040 per filled trade (the 5.3% missed signals were better than average; adverse selection -0.030 R).
- It beats random phase-matched maker entries (-0.19 R) but, as in the original, beating placebo is not an edge: net stays negative with both CIs below zero.
- Stop exits (taker 6 bp on a ~0.5% stop) dominate: about 60% of fills end at the stop.
- Cautions: the original non-overlap signal set (picked with taker exits) is kept; a maker trade may overlap the next signal. Stop distance is computed from L rather than the next open (OURS). 1m data has small gaps. Time stop exits at the open of the 1m bar after bar i+24 (taker; the original exits at that bar's close).

Files: study.py, orig_study.py (original code unchanged), test_study.py (6 pass; test_signal_bar_itself_not_used shows the naive variant starting at the signal bar fills), results.json, results_raw.json, rows.json.
