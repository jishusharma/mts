# Blind read: critical_test_wave2 RESULT.md (items 6-8)

Reader: Builder (second pass), 2026-11-06. Method: read item6_result.json, item7_census.tsv, item8_minbtl.tsv first; recomputed with
a fresh script (statistics.NormalDist, csv, json; study scripts not used); RESULT.md read only after this table was drafted.
Limit: raw 1m bars are not in the folder, so the gap percentiles are read from item6_result.json, not recomputed from bars (NOT RECOMPUTABLE).

## Item 6 (from item6_result.json; trade-level numbers recomputed from trades_b / trades_d)

| number in RESULT.md | my value | match |
|---|---|---|
| 44,640 bars, all aligned | 44640 / 44640 / 44640 | MATCH |
| open mean/p50/p95/p99/max +0.98/6.10/13.38/16.01/26.8 | 0.9836/6.097/13.375/16.005/26.77 | MATCH |
| close +0.99/6.11/13.56/16.29/26.8 | 0.9905/6.106/13.564/16.290/26.79 | MATCH |
| high +0.11/5.82/13.73/16.61/71.9 | 0.1091/5.820/13.730/16.613/71.87 | MATCH |
| low +1.87/6.37/13.46/15.98/83.6 | 1.8657/6.366/13.461/15.979/83.60 | MATCH |
| range USD -11.4/11.5/28.3/39.6/542.8 | -11.359/11.5/28.3/39.6/542.8 | MATCH |
| 66.4% wick >5 bps | 0.66434 | MATCH |
| corr 0.958; 8.7% opposite | 0.95834; 0.08748 | MATCH |
| funding Binance 0.637% (93), Deribit 0.607% (744) | 0.63722 (93), 0.60715 (744); diff 0.0301 pp | MATCH |
| events 52 / 55, shared 49 | 52 / 55 / 49 (from trade t_sig overlap: 49) | MATCH |
| 48 paired, mean diff +0.001 R, max 0.049 R | 48; 0.001329; 0.04893 | MATCH |
| sums +3.84 R vs +0.59 R; gap 3.25 R | 3.8413 / 0.5899; 3.2514 | MATCH |
| "3-6 events only one venue fires" | Binance-only 52-49=3, Deribit-only 55-49=6 | MATCH |
| "signal sets differ by 6-12%" | 3/52=5.8%, 6/55=10.9%, 6/52=11.5% | DIFF (minor: 6-11% by my count; 12% only if rounding 11.5 up) |
| lag check: lag 0 lowest (6.11; -1 6.72; +1 6.59) | lag values are not in the json | NOT RECOMPUTABLE |
| 1 trade each side has net_r None (51 / 54 traded vs 52 / 55 events) | trades_binance 51, trades_deribit 54 | consistent |

## Item 7 (item7_census.tsv, 104 rows, 104 distinct paths)

| number | my value | match |
|---|---|---|
| CHARGES 9 | 9 | MATCH |
| LIB 5 | 5 | MATCH |
| MENTIONS 21 | 21 | MATCH |
| NONE 69 | 69 | MATCH |
| total 104; non-library 99; fee-only 90 | 104; 99; 21+69=90 | MATCH |
Names of the charging scripts in the prose (chart_read_g5, gross_effect_screen, oi_divergence_v2, two DSA canaries) were not checked; counts only.

## Item 8 (item8_minbtl.tsv; MinBTL from the Bailey formula, g = 0.5772)

| number | my value | match |
|---|---|---|
| MinBTL N=7,8,9,10 = 1.92, 2.13, 2.31, 2.48 y | 1.923, 2.129, 2.313, 2.479 | MATCH |
| budget 10 configs at 2.5 y, Sharpe 1; 8 at 2.25 y | N=10 (2.479 <= 2.5, N=11 2.63 >); 2.25 y: N=8 (2.129), N=9 2.313 > | MATCH |
| needed Sharpe: 662 1.98; 553 1.95; 216 1.76; 96 1.59; 186 1.73; 80 1.55; 54 1.46; 48 1.43; 32 1.33; 3 0.54 | 1.98, 1.95, 1.76, 1.59, 1.73, 1.55, 1.46, 1.43, 1.33, 0.54 (E[max]/sqrt(2.5)) | MATCH |
| 41 rows, 15 record trials, 9 over budget, 26 unrecorded | 41, 15, 9, 26 | MATCH |
| standing passes 1 (L1-D3, PBO 0.030) | exactly one non-empty standing_pass cell | MATCH |
| -0.057%/trade fee-net (0.043 - 0.10) | arithmetic -0.057 | MATCH |

Totals: FOUND 40 rows MATCH, 1 DIFF (minor wording), 1 NOT RECOMPUTABLE (lag check). No headline number is wrong.

VERDICT: MATCH
