F2 run: H hours valid 30168 of 30648; events kept / dropped for no H: RSI-DIV-MTF 634 / 6, FADE 7292 / 124.

| test | layer | gate | n kept | n removed | kept mean R [95% CI] | removed mean R | lift [95% CI] | S1 lift | S2 lift | switches S1/S2 | C1 p | C2 p | C3 flag | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F2-1 | RSI-DIV-MTF | A | 119 | 515 | -0.3045 [-0.5244, -0.1012] | -0.2130 | -0.0915 [-0.3454, +0.1452] | -0.1538 | +0.0257 | 74/109 | 0.761 | 0.765 | no | NOT_DECIDABLE |
| F2-2 | RSI-DIV-MTF | B | 484 | 150 | -0.2010 [-0.3249, -0.0673] | -0.3243 | +0.1233 [-0.1092, +0.3583] | +0.2412 | -0.3080 | 109/73 | 0.188 | 0.170 | no | INCONCLUSIVE |
| F2-3 | FADE | A | 1614 | 5678 | -0.2888 [-0.3471, -0.2286] | -0.2267 | -0.0621 [-0.1290, -0.0006] | -0.1127 | -0.0087 | 74/109 | 0.975 | 0.987 | no | FAIL |
| F2-4 | FADE | B | 6032 | 1260 | -0.2439 [-0.2757, -0.2116] | -0.2239 | -0.0200 [-0.0895, +0.0465] | -0.0182 | -0.0147 | 109/73 | 0.723 | 0.744 | no | INCONCLUSIVE |

C3 family-wise: 95th percentile of the null max lift over 4 tests = +0.2713 R (1,000 circular shifts of the H series, seed 31). Observed lifts: F2-1 -0.0915, F2-2 +0.1233, F2-3 -0.0621, F2-4 -0.0200.

Planted edge (cells demeaned first on gate A; real H and event times; same C3 nulls):
- no plant: C3 threshold +0.2794; lifts F2-1 -0.000, F2-2 +0.146, F2-3 +0.000, F2-4 -0.003; flagged [].
- plant +0.25 R on RSI A kept (pre-registered): C3 threshold +0.2786; lifts F2-1 +0.250, F2-2 +0.207, F2-3 +0.000, F2-4 -0.003; flagged []; F2-1 CI [-0.004, +0.487].
- plant +0.50 R on RSI A kept (extra, diagnostic): C3 threshold +0.2873; lifts F2-1 +0.500, F2-2 +0.269, F2-3 +0.000, F2-4 -0.003; flagged ['F2-1']; F2-1 CI [+0.246, +0.737].
- plant +0.25 R on FADE A kept (extra, diagnostic): C3 threshold +0.2794; lifts F2-1 -0.000, F2-2 +0.146, F2-3 +0.250, F2-4 +0.064; flagged []; F2-3 CI [+0.183, +0.311].

Power: sd of net R per event RSI-DIV-MTF 1.333, FADE 1.006; n per cell for a 0.17 R effect at 80 % power: RSI 483, FADE 276.

F2 overall: NEGATIVE.
