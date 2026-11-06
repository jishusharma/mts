MATCH 61 | DIFF 2 | NOT_IN_DATA 8

# GPT re-derive: malkan_window_dev RESULT.md numbers (2026-11-06)

Source: counts.csv and dev_cells.csv in `MyTradingSys/research/malkan_window_dev_2026-11/`, formulas OURS: net = gross - 0.14, CI = net +- 1.96 se, p = 2-sided normal on net/se, Holm m=16 (step-down, monotone). FORMULAS.md has no fee-net/Holm/power section (grep of fee|net|Wilson|mean: only sections 10, 13 costs). No raw per-trade returns or klines in the folder, so gross and se cannot be re-derived: NOT_IN_DATA. Arithmetic recomputed with python (ad hoc, not saved).

Verdict INCONCLUSIVE follows from PRE_REG.md:50 given the BLOCK numbers; power rows DIFF by <0.1% (rounding), same verdict.

| Number | RESULT value | Recomputed | Status | Note |
|---|---|---|---|---|
| Regime weeks 130 | 130 | 130.29 weeks (912 d /7), 130 full | MATCH | date arithmetic, splits window per PRE_REG.md:24 |
| Regime bull 25 (19%) | 25 / 19% | 19.2% if 25 of 130 | MATCH | pct only; 25 itself NOT re-countable here (no weekly regime data) |
| Regime bear 0 / range 105 (81%) | 0 / 105 (81%) | 105/130=80.8% | MATCH | pct and 25+105+0=130; counts as above |
| Regime n/a 0 | 0 | 0 | NOT_IN_DATA | no weekly tags in folder |
| Cost 0.14% | 0.14 | 0.14 = PRE_REG.md:29 (not verified vs research_kit) | MATCH | label SOURCED by PRE_REG only |
| Holm m=16 | 16 | 4 arms x 2 TF x 2 sides = 16 | MATCH | PRE_REG.md:31 |
| Events in OURS windows total 4 | 4 | B11_12 1h bear 1 + C13_18 1h bear 2 + B11_12 4h bull 1 = 4 | MATCH | counts.csv:2,3,14 |
| n 1h bearish B11_12 | 1 | 1 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 1h bearish B11_12 | 1 | 1 | MATCH | same |
| n 1h bearish C13_18 | 2 | 2 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 1h bearish C13_18 | 2 | 2 | MATCH | same |
| n 1h bearish D19_50 | 0 | 0 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 1h bearish D19_50 | 0 | 0 | MATCH | same |
| n 1h bearish S3_10 | 550 | 550 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 1h bearish S3_10 | 405 | 405 | MATCH | same |
| n 1h bullish B11_12 | 0 | 0 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 1h bullish B11_12 | 0 | 0 | MATCH | same |
| n 1h bullish C13_18 | 0 | 0 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 1h bullish C13_18 | 0 | 0 | MATCH | same |
| n 1h bullish D19_50 | 0 | 0 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 1h bullish D19_50 | 0 | 0 | MATCH | same |
| n 1h bullish S3_10 | 517 | 517 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 1h bullish S3_10 | 399 | 399 | MATCH | same |
| n 4h bearish B11_12 | 0 | 0 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 4h bearish B11_12 | 0 | 0 | MATCH | same |
| n 4h bearish C13_18 | 0 | 0 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 4h bearish C13_18 | 0 | 0 | MATCH | same |
| n 4h bearish D19_50 | 0 | 0 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 4h bearish D19_50 | 0 | 0 | MATCH | same |
| n 4h bearish S3_10 | 132 | 132 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 4h bearish S3_10 | 128 | 128 | MATCH | same |
| n 4h bullish B11_12 | 1 | 1 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 4h bullish B11_12 | 1 | 1 | MATCH | same |
| n 4h bullish C13_18 | 0 | 0 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 4h bullish C13_18 | 0 | 0 | MATCH | same |
| n 4h bullish D19_50 | 0 | 0 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 4h bullish D19_50 | 0 | 0 | MATCH | same |
| n 4h bullish S3_10 | 129 | 129 | MATCH | counts.csv vs dev_cells.csv n (study output, not raw) |
| days 4h bullish S3_10 | 125 | 125 | MATCH | same |
| gross 1h bearish B11_12 | 1.49 | only in dev_cells.csv (study output) | NOT_IN_DATA | raw per-trade returns/OHLC not in folder; copy matches CSV 1.493 |
| net 1h bearish B11_12 | 1.35 | 1.353 | MATCH | gross - 0.14 (given gross) |
| CI 1h bearish B11_12 | n/a | n/a (n=1, no se) | MATCH |  |
| Holm p 1h bearish B11_12 | 1.0 | 1.0000 | MATCH | 2-sided normal p from net/se, Holm m=16 |
| gross 1h bearish C13_18 | 2.22 | only in dev_cells.csv (study output) | NOT_IN_DATA | raw per-trade returns/OHLC not in folder; copy matches CSV 2.217 |
| net 1h bearish C13_18 | 2.08 | 2.077 | MATCH | gross - 0.14 (given gross) |
| CI 1h bearish C13_18 | 0.48..3.68 | 0.475..3.679 | MATCH | mean+-1.96*se (se from CSV; se itself NOT_IN_DATA) |
| Holm p 1h bearish C13_18 | 0.177 | 0.1767 | MATCH | 2-sided normal p from net/se, Holm m=16 |
| gross 1h bearish S3_10 | -0.106 | only in dev_cells.csv (study output) | NOT_IN_DATA | raw per-trade returns/OHLC not in folder; copy matches CSV -0.106 |
| net 1h bearish S3_10 | -0.246 | -0.246 | MATCH | gross - 0.14 (given gross) |
| CI 1h bearish S3_10 | -0.443..-0.049 | -0.443..-0.049 | MATCH | mean+-1.96*se (se from CSV; se itself NOT_IN_DATA) |
| Holm p 1h bearish S3_10 | 0.213 | 0.2134 | MATCH | 2-sided normal p from net/se, Holm m=16 |
| gross 1h bullish S3_10 | -0.021 | only in dev_cells.csv (study output) | NOT_IN_DATA | raw per-trade returns/OHLC not in folder; copy matches CSV -0.021 |
| net 1h bullish S3_10 | -0.161 | -0.161 | MATCH | gross - 0.14 (given gross) |
| CI 1h bullish S3_10 | -0.393..0.072 | -0.393..0.072 | MATCH | mean+-1.96*se (se from CSV; se itself NOT_IN_DATA) |
| Holm p 1h bullish S3_10 | 1.0 | 1.0000 | MATCH | 2-sided normal p from net/se, Holm m=16 |
| gross 4h bearish S3_10 | 0.092 | only in dev_cells.csv (study output) | NOT_IN_DATA | raw per-trade returns/OHLC not in folder; copy matches CSV 0.092 |
| net 4h bearish S3_10 | -0.048 | -0.048 | MATCH | gross - 0.14 (given gross) |
| CI 4h bearish S3_10 | -0.748..0.653 | -0.748..0.653 | MATCH | mean+-1.96*se (se from CSV; se itself NOT_IN_DATA) |
| Holm p 4h bearish S3_10 | 1.0 | 1.0000 | MATCH | 2-sided normal p from net/se, Holm m=16 |
| gross 4h bullish B11_12 | 4.30 | only in dev_cells.csv (study output) | NOT_IN_DATA | raw per-trade returns/OHLC not in folder; copy matches CSV 4.301 |
| net 4h bullish B11_12 | 4.16 | 4.161 | MATCH | gross - 0.14 (given gross) |
| CI 4h bullish B11_12 | n/a | n/a (n=1, no se) | MATCH |  |
| Holm p 4h bullish B11_12 | 1.0 | 1.0000 | MATCH | 2-sided normal p from net/se, Holm m=16 |
| gross 4h bullish S3_10 | 0.181 | only in dev_cells.csv (study output) | NOT_IN_DATA | raw per-trade returns/OHLC not in folder; copy matches CSV 0.181 |
| net 4h bullish S3_10 | 0.041 | 0.041 | MATCH | gross - 0.14 (given gross) |
| CI 4h bullish S3_10 | -0.818..0.900 | -0.818..0.900 | MATCH | mean+-1.96*se (se from CSV; se itself NOT_IN_DATA) |
| Holm p 4h bullish S3_10 | 1.0 | 1.0000 | MATCH | 2-sided normal p from net/se, Holm m=16 |
| Finding: only CI wholly below 0 is 1h bear S3_10 (Holm 0.21) | -0.25 / 0.21 | CI hi -0.049; Holm 0.2134 | MATCH | C13_18 CI above 0 but n=2 |
| Power 1h n needed ~3227 | 3227 | 3229 | DIFF | alpha .05/(2*236), power .8, gap .30-.14=.16, sd 2.0, 405 d; formula inferred NOT in FORMULAS.md; 0.06% off |
| Power 4h n needed ~12907 | 12907 | 12917 | DIFF | sd 4.0; 0.08% off, z rounding in study |
| Power MDE+cost 1h 0.592 / 4h 1.747 (BLOCKED.md) | 0.592 / 1.747 | 0.592 / 1.747 | MATCH | same inferred formula |
