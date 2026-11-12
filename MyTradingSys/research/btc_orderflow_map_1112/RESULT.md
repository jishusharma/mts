# RESULT: BTC order-flow map, assembled (cards btc-native-orderflow-map-1112 + btc-of-level-auction B1), DEV only

Regime mix: clocks 851 DEV days bull 35% / bear 16% / range 42% / n/a 7%; A3 funding 819 events bull 283 / bear 127 / range 344 / n/a 65; A2 170 events bull 51 / bear 10 / range 103 / n/a 6; B1 at level 524 events bull 135 / bear 31 / range 344 / n/a 14 (regime cuts differ by family, OURS; copied from CLOCKS.md, EVENTS.md, B1.md). No per-regime cell passes the fee, so no verdict depends on regime.

DEV = 2022-02-01 .. 2024-05-31. VALIDATION/GAP/RESERVE/HOLDOUT never opened. Fee 10 bp round trip (fees.py). Nothing re-run: every number is copied from CLOCKS.md, PRINTS.md, EVENTS.md and ../btc_of_level_auction_1112/B1.md (full per-bucket tables live there). Net bp = net % x 100.

## Verdict table (60m horizon unless stated)

| Family | Cell | n | Net bp | Verdict |
|---|---|---|---|---|
| Clocks | 24 hour buckets x long/short, best long h22 | 851 | -5.22 | no edge (every long and short cell below 0 after fee) |
| Clocks | best short h01 | 851 | -6.31 | no edge |
| Clocks | funding windows (00Z/08Z/16Z), best 08Z/00Z long | 851 | -8.3 / -8.5 | no edge |
| Clocks | weekdays Mon-Sun, best Mon long | 2904 | -8.16 | no edge |
| Prints A1 | large print, trade with it (60-day sample) | 204 | -9.19 (gross +0.81) | no edge (z60 +0.12 vs placebo; fee eats it) |
| Prints A2 | absorption, 60-day sample | 15 | +1.43 | INSUFFICIENT_N (no verdict) |
| Events A2 | absorption, full DEV | 170 | -3.4 (15m -5.9) | INSUFFICIENT_N (<180) |
| Events A3 | funding extreme | 819 | -7.5 (15m -9.0) | no edge (t -3.8; 15m below placebo band). Count 754 in dda59e2e2, 819 in e84dafc48: unresolved, immaterial to the sign |
| Level B1 | absorption at PDH/PDL/VAH/VAL | 524 | -13.6 (15m -11.5) | no edge, worse than placebo mean |
| Level B1 control | same flow, away from level | 3804 | -9.1 | level adds nothing: at minus away -4.5 bp |
| Level B2 | unfinished auction at 24h extreme (fade), aggTrades on D: | 480 | -15.8 (15m -11.3; gross 60m -5.8, 15m -1.3) | FAIL on DEV (t -3.95 / -5.72; both cells inside the placebo band); VALIDATION not opened. See btc_of_level_auction_1112/B2.md |

## Plain words
BTC's own clocks (hour, weekday, funding window), large prints, absorption and funding extremes show no move big enough to pay the 10 bp fee. The few clock cells that beat a shuffle (h01, h13, h16, h22, funding 16Z) are one-sided noise: the best is still 5 bp short of break-even. Absorption at a prior-day level does worse than absorption anywhere else, so the level is not the edge. Two cells (A2, B2) could not be judged: too few events or no data.

## What would change the verdict
- A2 reaching n >= 180 (more DEV days or window) with net above 0 and |z| >= 2 vs placebo.
- B2: done (btc_of_level_auction_1112/B2.md, FAIL on DEV).
- Liquidation-cascade history (no public feed) and full-DEV aggTrades for A1.
- A cell positive net of fee in DEV, then again in the sealed VALIDATION (not opened here). Fee below 10 bp would not rescue any cell: best gross is +4.8 bp (h22 long).

## Paper slot
NOT_IN_DATA / no edge. No cell passed the PREREG bar, so no rule is frozen and no PAPER_SLOT.md exists. DECISION (OURS): conservative, queue nothing.

## Source tables, copied unchanged (card btc-native-orderflow-map-1112 step 1)

### CLOCKS.md DEV table

| Bucket | n | delta share | abs ret bp | fwd15 gross bp | fwd60 gross bp | long net60 bp | short net60 bp |
|---|---|---|---|---|---|---|---|
| h00 | 851 | -0.0057~ | 4.86 | +1.68~ | +1.84~ | -8.16~ | -11.84~ |
| h01 | 851 | -0.0060~ | 4.46~ | +0.20~ | -3.69 | -13.69 | -6.31 |
| h02 | 851 | -0.0043~ | 4.10 | +0.49~ | -0.82~ | -10.82~ | -9.18~ |
| h03 | 851 | +0.0012~ | 3.68 | -0.46~ | +0.43~ | -9.57~ | -10.43~ |
| h04 | 851 | -0.0068~ | 3.44 | -0.01~ | +0.91~ | -9.09~ | -10.91~ |
| h05 | 851 | -0.0073~ | 3.47 | -0.03~ | +1.26~ | -8.74~ | -11.26~ |
| h06 | 851 | -0.0032~ | 3.63 | +0.25~ | +1.07~ | -8.93~ | -11.07~ |
| h07 | 851 | -0.0039~ | 3.80 | +0.20~ | +0.29~ | -9.71~ | -10.29~ |
| h08 | 851 | +0.0003~ | 4.04 | +1.19~ | +1.98~ | -8.02~ | -11.98~ |
| h09 | 851 | -0.0008~ | 3.84 | -1.09~ | +0.09~ | -9.91~ | -10.09~ |
| h10 | 851 | -0.0001~ | 3.83 | -1.14~ | +2.64~ | -7.36~ | -12.64~ |
| h11 | 851 | -0.0028~ | 3.96 | -1.09~ | +0.24~ | -9.76~ | -10.24~ |
| h12 | 851 | -0.0020~ | 4.90 | +1.50~ | +1.30~ | -8.70~ | -11.30~ |
| h13 | 851 | -0.0086 | 5.64 | +0.53~ | -3.66 | -13.66 | -6.34 |
| h14 | 851 | +0.0007~ | 6.25 | -0.94~ | +1.57~ | -8.43~ | -11.57~ |
| h15 | 851 | -0.0002~ | 6.00 | +0.63~ | +0.38~ | -9.62~ | -10.38~ |
| h16 | 851 | -0.0069~ | 5.74 | -0.40~ | -2.01~ | -12.01~ | -7.99~ |
| h17 | 851 | -0.0038~ | 5.32 | +0.05~ | -0.56~ | -10.56~ | -9.44~ |
| h18 | 851 | +0.0058 | 5.27 | -1.69~ | +1.82~ | -8.18~ | -11.82~ |
| h19 | 851 | -0.0019~ | 5.24 | -1.53~ | -1.97~ | -11.97~ | -8.03~ |
| h20 | 851 | +0.0058 | 5.00 | +1.38~ | +3.73~ | -6.27~ | -13.73~ |
| h21 | 851 | -0.0054~ | 4.85 | +1.41~ | -0.26~ | -10.26~ | -9.74~ |
| h22 | 851 | -0.0045~ | 4.73~ | +2.67 | +4.78 | -5.22 | -14.78 |
| h23 | 851 | -0.0080~ | 4.39~ | +0.89~ | -0.78~ | -10.78~ | -9.22~ |
| fund 00Z (20-04) | 851 | -0.0031~ | 4.51~ | +1.78~ | +1.73~ | -8.27~ | -11.73~ |
| fund 08Z (04-12) | 851 | -0.0025~ | 3.75 | +0.67~ | +1.55~ | -8.45~ | -11.55~ |
| fund 16Z (12-20) | 851 | -0.0022~ | 5.55 | -0.85~ | -2.92 | -12.92 | -7.08 |
| Mon | 2904 | -0.0006~ | 4.95 | +0.65~ | +1.84~ | -8.16~ | -11.84~ |
| Tue | 2928 | -0.0027~ | 5.17 | -0.10~ | +0.25~ | -9.75~ | -10.25~ |
| Wed | 2928 | -0.0028~ | 5.36 | -0.10~ | +1.18~ | -8.82~ | -11.18~ |
| Thu | 2928 | -0.0039~ | 5.10 | +0.02~ | -0.69~ | -10.69~ | -9.31~ |
| Fri | 2928 | -0.0037~ | 4.97 | +0.20~ | -0.02~ | -10.02~ | -9.98~ |
| Sat | 2904 | -0.0053~ | 3.23 | -0.11~ | -0.17~ | -10.17~ | -9.83~ |
| Sun | 2904 | -0.0009~ | 3.42 | +0.81~ | +0.70~ | -9.30~ | -10.70~ |

Headline (clocks): best cell h22 long, net60 -5.22 bp, n=851, fwd60 gross +4.78 bp z=+2.19 vs 1,000 label-shuffle placebos (OURS, results_clocks.json). Gross edge exists in noise-sized amounts but is 5.2 bp short of the 10 bp fee: FAIL, no paper slot.

### PRINTS.md DEV table

| Event | n | fwd 15m net bp | control 15m (p1..p99) | z15 | t15 | fwd 60m net bp | control 60m (p1..p99) | z60 | t60 | gross 60m bp | mark 15m / 60m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 large print (with L) | 204 (L 111 / S 93) | -11.37 | -10.01 (-14.81..-4.45) | -0.61 | -3.38 | -9.19 | -9.73 (-19.98..+0.77) | +0.12 | -1.62 | +0.81 | none / gross only |
| A2 absorption (against delta) | 15 (L 5 / S 10) | -1.23 | -10.18 (-30.98..+7.03) | +1.12 | -0.20 | +1.43 | -11.59 (-54.49..+26.00) | +0.81 | +0.18 | +11.43 | INSUFFICIENT_N / INSUFFICIENT_N |

Headline (prints): A1 large print with trade, n=204, net60 -9.19 bp, z60 +0.12 vs placebo (|z|<2); A2 n=15 INSUFFICIENT_N. FAIL / no verdict, no paper slot.
