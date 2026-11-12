COUNTS: MATCH=6 DIFF=2 NOT_IN_DATA=0
Source: MyTradingSys/research/edge_views_2026-11-11/TREND/RESULT.md (internal-consistency check only; no raw data read)

1. MATCH RESULT.md:12 (R1 DEV ALL, n=50, net/trade +11.67): long 24 x 23.51 + short 26 x 0.74 over 50 = 11.67. n = 24+26.
2. MATCH RESULT.md:15 (R1 VAL ALL, n=38, +0.87): (19 x 4.35 + 19 x -2.62)/38 = 0.865. n = 19+19.
3. MATCH RESULT.md:24 (R2 DEV ALL, n=123, +1.90, R +0.39): (65 x 3.48 + 58 x 0.14)/123 = 1.90. R: (65 x 0.57 + 58 x 0.19)/123 = 0.39.
4. DIFF  RESULT.md:26 (R2 DEV short, net/trade +0.14 %, net R +0.19): this implies an average risk of about 0.7 % per trade. The same segment's long row (:25) implies about 6 % (3.48/0.57). The ALL row (:24) implies about 4.9 %. The short row's avg loss is -5.90, so a 0.7 % stop is not plausible. The %/trade and R columns are not mutually consistent for this row. R1 DEV short (:14, 0.74 % vs R +0.02, about 37 % implied) is similarly odd.
5. MATCH RESULT.md:36 (R3 DEV ALL, n=64, +6.63): (32 x 15.12 + 32 x -1.87)/64 = 6.63. R = nan, which is consistent with the header at :4 (no stop for rule 3).
6. MATCH RESULT.md:43 (VAL ALL t-stats and placebo percentiles): t +0.39 (:15), +0.97 (:27), +0.76 (:39) and placebo 69, 88, 79 match the tables. All are under the bars of 2 and 95.
7. DIFF  RESULT.md:45 ("n 19-39 per row"): the VAL short rows are n=19, 39, 20, but the DEV short rows are n=26, 58, 32 (:14, :26, :38). The range should be 19-58. The claims about the signs of the short rows are correct: DEV +0.74/+0.14/-1.87 is about zero, and VAL -2.62/-0.25/-1.63 is negative.
8. MATCH RESULT.md:47 (verdict): R2 is positive in both segments (+1.90 and +0.95 %). t is 1.62/0.97 (:24, :27) and n is 123/85. The FAIL verdict follows from VAL t < 2 and placebo < 95 in every rule. Also checked MATCH RESULT.md:44 (R1 +11.7 %, placebo 100, VAL +0.87) and :46 (long-only placebo percentiles run 62-96, which matches).
