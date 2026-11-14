# extreme_confirm_template_2026-11 REPORT

Verdict: FAIL. 0 of 54 pre-registered cells pass (0 BH rejections at 10%; no cell has a VALIDATION bootstrap CI lower bound above 0). 14 cells UNDERPOWERED (VALIDATION n < 30); 40 powered. PRE_REG.md frozen in commit ec64e8c92 before any outcome was computed.

- Setup: 1h Bybit linear, 10 coins, confirming candle, next-open entry, stop = setup extreme -/+ k ATR (k chosen on DEV), 2R or 24h, taker fees (fees.py) plus funding.
- Powered cells with VALIDATION mean > 0: 12 of 40; smallest one-sided p 0.098 (a_99 short, below-both bucket, n 158, +0.24%, CI lower -0.12%, but RECENT -0.28%); BH needs p <= 0.0025 for the first rank.
- Best VALIDATION means (all CI lower bounds < 0, none beat their 95th-percentile placebo with BH): b1_99 long below-both +1.17% n 73 (RECENT n 163 +0.01%), e long above-both +0.59% n 67 (RECENT n 61 +0.59%), e long below-both +0.53% n 114 (RECENT n 167 +0.61%), d short between +0.29% n 88 (RECENT +0.39%).
- Cells with positive mean in both VALIDATION and RECENT at n >= 30: 7, all with CI lower bound < 0; the capitulation bar long (e, above or below both) is consistent in sign (+0.5 to +0.6% in both) and is the lead, not a pass.
- DEV: 14 of 42 powered cells had mean > 0 (selection data only).
- BTC alone (descriptive, same rules): VALIDATION mean > 0 in 11 of 38 cells with n; see cells.csv BTC_* columns.
- Placebo pool ignores the one-position rule and is drawn with replacement (disclosed in the run).
- Per-cell numbers: cells.csv (n, mean, 95% day-cluster CI, p, placebo mean and 95th pct, per split).

Next test if anything: capitulation bar (e) long, pooled over buckets, 4h bars (more n per cell, fewer cells), tested once on RECENT-forward.
