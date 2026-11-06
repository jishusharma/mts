# Blind read: anticipation_map_2026-11-05 (D11 feeder check)

Producer of this audit: Gemini (independent of the study author). Read PRE_REG.md definitions only; RESULT.md was opened only after the numbers below were computed. study.py not read.
Script: `MyTradingSys/research/gemini_audits_2026-11-05/blind_read_anticipation_map.py` (variant A); raw output `blind_read_output_A.txt`. Command: `python MyTradingSys/research/gemini_audits_2026-11-05/blind_read_anticipation_map.py A`.
Data: `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv` (1,313,280 DEV rows, < 2024-07-01) and `F:/MTS/data/metrics/BTCUSDT/BTCUSDT-metrics-*.csv` sum_open_interest (262,395 rows after dropping 133 zero-OI rows).

## Interpretation choices (PRE_REG is silent; OURS)
- Price at t-60 = open of bar t-60; price at t = close of bar t-1; price at t+60 = close of bar t+59. Variant B (close of bar t-60 as start) was also run and drifts further (13,270 non-flat events vs 13,332; cells off by 20-25), so A is used.
- OI zero rows treated as missing. Without that rule: 21,874 events (+18). RESULT.md "Deviations" (RESULT.md:31) states the same rule, which I did not know when I chose it.
- Continue = sign(close t+60 - close t) equals price state; undone = close t+60 strictly past the window start price against the state; OI keeps = sign(OI t+60 - OI t) equals OI state.

## Per-number table (RESULT.md line in brackets)
| Number | Mine (OURS recompute) | RESULT.md | Match |
|---|---|---|---|
| Hourly events [3] | 21856 | 21855 | off by 1 |
| UP/UP [24] | 3750 | 3750 | exact |
| DOWN/DOWN [24] | 3277 | 3279 | off by 2 |
| DOWN/UP [24] | 3235 | 3236 | off by 1 |
| UP/DOWN [24] | 3070 | 3072 | off by 2 |
| UP/UP/BUY n,share,cont,undone,OI [14] | 3262, 87%, 47%, 19%, 60% | 3262, 87%, 47%, 19%, 60% | exact |
| UP/UP/SELL [15] | 488, 13%, 48%, 29%, 60% | 488, 13%, 48%, 29%, 60% | exact |
| UP/DOWN/BUY [16] | 2642, 86%, 45%, 14%, 51% | 2644, 86%, 45%, 14%, 51% | n off by 2, rates match |
| UP/DOWN/SELL [17] | 428, 14%, 46%, 28%, 57% | 428, 14%, 46%, 28%, 57% | exact |
| DOWN/UP/SELL [18] | 2824, 87%, 44%, 19%, 58% | 2825, 87%, 44%, 19%, 58% | n off by 1, rates match |
| DOWN/UP/BUY [19] | 411, 13%, 49%, 30%, 58% | 411, 13%, 49%, 30%, 58% | exact |
| DOWN/DOWN/SELL [20] | 2958, 90%, 42%, 18%, 51% | 2959, 90%, 42%, 18%, 51% | n off by 1, rates match |
| DOWN/DOWN/BUY [21] | 319, 10%, 48%, 26%, 53% | 320, 10%, 48%, 26%, 53% | n off by 1, rates match |

All 32 rounded percentages (share, continue, undone, OI keeps) match RESULT.md. 5 of 13 count lines are exact; the other 8 differ by 1-2 events (0.03% of the 21,855). The pattern (RESULT's counts slightly higher in state cells, one event higher overall) fits a boundary rule I cannot see without reading study.py (e.g. the 0.1 % flat test or the missing-bar/OI-at-t rule); I did not read study.py, so the cause is UNKNOWN.
Headline claims in RESULT.md:5-7 (delta agrees with price 86-90 %, minority reading 10-14 %, continues 42-49 %, undone 26-30 % vs 14-19 %) all reproduce from my table.

## Conclusion
The study's findings reproduce. Exact counts do not reproduce to the event: 1 event overall, 1-2 in 8 cells. By the strict per-number test the counts mismatch.

VERDICT: MISMATCH (counts off by 1-2 events; all rounded rates and the Verdict-paragraph claims match)
