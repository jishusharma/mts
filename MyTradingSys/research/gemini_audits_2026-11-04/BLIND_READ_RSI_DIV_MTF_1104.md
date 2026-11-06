# Blind read: rsi_divergence_mtf_gated_2026-11-04 RESULT.md and RESULT_LONG.md vs raw CSVs (re-read 2026-11-06)

Method: recomputed from dev_cells.csv, dev_cells_long.csv, counts.csv, counts_long.csv, regime_mix_*.txt only (pandas, no study code); RESULT files read after the tables below were computed. Cost check: gross - net = 0.14 in every row of both CSVs. Gate partition check: aligned+counter+range n = all n for every (arm, entry, kind, tf) in dev_cells.csv and in the primary rows of dev_cells_long.csv. Survivors: 0 True of 256 and 0 True of 272 rows.

Counts: FOUND 32, DIFF 1, NOT_IN_DATA 3.

## Side by side (W12 unless stated; net/CI in % per trade, day-clustered)

| # | Claim in RESULT | CSV value | Status |
|---|---|---|---|
| 1 | DEV regime mix 130 weeks bull 25 / bear 0 / range 105 | regime_mix_dev.txt identical | FOUND |
| 2 | 15m signal ungated n 973, net -0.161 [-0.229,-0.092] | 973, -0.1608 [-0.2294,-0.0923] | FOUND |
| 3 | 15m aligned n 164 / 96 days, gross -0.036, net -0.176 [-0.307,-0.045] | 164/96, -0.0361, -0.1761 [-0.3067,-0.0454] | FOUND |
| 4 | excess over drift -0.064 (t -1.0) | -0.0635, t -1.015 | FOUND |
| 5 | gate removed 83 % of events | 1 - 164/973 = 83.1 % | FOUND |
| 6 | 1h aligned n 43/32, net +0.111 [-0.394,+0.615], t 0.43 | 43/32, +0.1107 [-0.3939,+0.6153], t 0.4300 (excess_t 0.568) | FOUND |
| 7 | 4h aligned n 18, net -0.736 [-2.58,+1.11] | 18, -0.7365 [-2.5819,+1.1090] | FOUND |
| 8 | 1d aligned n 1, +15.3 % | 1, net +15.25 (gross 15.39) | FOUND |
| 9 | positive-looking cells CI spans zero | 1h/4h/1d all span zero or NaN CI | FOUND |
| 10 | Retest fills 126/164, 34/43, 15/18 | 126, 34, 15 (signals 164/43/18) | FOUND |
| 11 | Retest net 15m -0.130 [-0.293,+0.034]; 1h +0.123 [-0.547,+0.793] | -0.1297 [-0.2930,+0.0335]; +0.1229 [-0.5474,+0.7933] | FOUND |
| 12 | Min Holm p 0.265 (15m aligned signal) | 0.2645 on 15m aligned signal; min over 16 non-empty-family rows | FOUND |
| 13 | W12 and W18 identical event sets | W12 = W18 n in every aligned cell | FOUND |
| 14 | Original windows 3-10 and 5-14 differ by at most 2 events per cell, same sign | C3_10 differs by 2/1/0/0 (15m signal 162 vs 164); C5_14 has 58/14/3/0 vs 164/43/18/1 (differs by up to 106) | DIFF (true for C3_10 only, false for C5_14) |
| 15 | Counter bearish 15m net -0.176 n 208 | 208, -0.1766, t -3.00 | FOUND |
| 16 | Range bearish 15m net -0.179 n 810, t -3 to -5.3 | 810, -0.1799, t -5.30 | FOUND |
| 17 | 1h/4h/1d counter and range bearish span zero | all t between -1.49 and +0.08 | FOUND |
| 18 | Aligned bearish cells empty | n 0 on all TFs, both entries | FOUND |
| 19 | 0 survivors, dev_survivors.json [] | survivor False x16 / NaN; file size 2 bytes | FOUND |
| 20 | Monthly RSI low 41.4 in 2022; 4 prereg_gate BLOCKs, n needed 401/2259/... | not in the CSVs | NOT_IN_DATA |
| 21 | Long regime mix 360 weeks bull 73 / bear 0 / range 222 / n/a 65; P40 bear 57 | regime_mix_dev_long.txt identical | FOUND |
| 22 | Long 15m aligned n 482 / 282 days, net -0.080 [-0.216,+0.055], excess +0.027 (t 0.40) | 482/282, -0.0802 [-0.2158,+0.0554], +0.0268, t 0.404 | FOUND |
| 23 | Ungated 15m long n 2091 net -0.102 [-0.160,-0.045] | 2091, -0.1024 [-0.1597,-0.0450] | FOUND |
| 24 | Long 15m retest n 345 net -0.205 [-0.346,-0.065], Holm 0.185 | 345, -0.2052 [-0.3457,-0.0647], 0.1853 | FOUND |
| 25 | Long 1h signal n 125/94 -0.066 [-0.495,+0.364]; retest n 93 +0.097 [-0.458,+0.652] | identical | FOUND |
| 26 | Long 4h n 36 +0.185 [-1.40,+1.77]; retest n 25 -0.437 [-2.50,+1.63] | identical | FOUND |
| 27 | Long 1d n 1, +15.2 | 1, +15.19 | FOUND |
| 28 | P40 15m short signal n 434/236 -0.158 [-0.278,-0.039], excess -0.013 (t -0.23); retest n 330 -0.222 [-0.386,-0.059] | identical; raw p 0.0095 / 0.0077, Holm 0.379 / 0.325 | FOUND |
| 29 | P40 1h n 101 +0.057 [-0.439,+0.553]; 4h n 26 +0.893 [-0.661,+2.448], excess t 1.53 | identical | FOUND |
| 30 | P40 1d n 2 net +16.3, Holm 0.013 / 0.000 | 2, +16.32 (signal) Holm 0.0129; retest Holm 0.0000 | FOUND |
| 31 | Ungated bearish 15m n 2358 -0.179 [-0.227,-0.131]; 1h -0.275; 4h retest -1.385 [-2.32,-0.45] | identical | FOUND |
| 32 | W12 = W18 everywhere except one P40 1h cell (101 vs 102) | P40 1h bear signal W12 101 vs W18 102; retest equal (83) | FOUND |
| 33 | C3_10 15m long n 478 net -0.075; C5_14 n 187 net -0.156 | 478, -0.0750; 187, -0.1556 (the numbers match; the conclusion "window choice moves nothing" is contradicted by 187 vs 482 events) | FOUND (numbers) |
| 34 | 0 survivors of 48 long cells; only t>=2 cell is n=2 artifact | 0 True; P40 1d rows (n 2) carry excess t 3.7 and 7.7 | FOUND |
| 35 | Monthly RSI closest 40.4 in 2023-01; 282 days vs 424 needed | not in the CSVs | NOT_IN_DATA |
| 36 | Exchange gaps 9-25 per series | not in the CSVs | NOT_IN_DATA |

Aggregates (not quoted in RESULT, for the gated-vs-ungated and strict-vs-proxy question), W12 signal, n-weighted net: short window all 2681 events -0.192, aligned 226 -0.098, counter 286 -0.295, range 2169 -0.188; long window primary bullish+bearish all 6080 -0.191, aligned 644 -0.039, counter 858 -0.342, range 4578 -0.184; P40 aligned 563 -0.013.

Finding: one statement is wrong as written (row 14: C5_14 is not within 2 events); the numeric tables and verdict (INCONCLUSIVE, 0 survivors) reproduce exactly. Row 33's reading ("window choice moves nothing") should be limited to W12 vs W18 and C3_10.

VERDICT: MATCH (all quoted numbers reproduce; 1 prose claim, row 14, overstated)
