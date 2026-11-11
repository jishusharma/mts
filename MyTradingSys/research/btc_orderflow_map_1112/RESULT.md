# RESULT: BTC native order-flow map (card btc-native-orderflow-map-1112), DEV only

VALIDATION/GAP/RESERVE/HOLDOUT never opened. Tables below are copied unchanged from CLOCKS.md, PRINTS.md, EVENTS.md. Fee 10 bp round trip (fees.py).

## CLOCKS DEV table
Headline: effect = none that survives the fee; n = 851 days per hour bucket (2904-2928 per weekday); z vs 1,000 placebos: only h01/h13/h16/fund16Z/h22 reach |z|>=2 on fwd60, best long net60 is h22 -5.22 bp, every long/short net60 cell is below 0 after 10 bp.

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

## PRINTS table (A1 large print, A2 absorption)
Headline: effect = none; A1 n=204, net60 -9.19 bp, z60 +0.12 vs placebo (z15 -0.61), gross60 +0.81 bp so fees eat it; A2 n=15 INSUFFICIENT_N (z60 +0.81), no verdict.

| Event | n | fwd 15m net bp | control 15m (p1..p99) | z15 | t15 | fwd 60m net bp | control 60m (p1..p99) | z60 | t60 | gross 60m bp | mark 15m / 60m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 large print (with L) | 204 (L 111 / S 93) | -11.37 | -10.01 (-14.81..-4.45) | -0.61 | -3.38 | -9.19 | -9.73 (-19.98..+0.77) | +0.12 | -1.62 | +0.81 | none / gross only |
| A2 absorption (against delta) | 15 (L 5 / S 10) | -1.23 | -10.18 (-30.98..+7.03) | +1.12 | -0.20 | +1.43 | -11.59 (-54.49..+26.00) | +0.81 | +0.18 | +11.43 | INSUFFICIENT_N / INSUFFICIENT_N |

## EVENTS table (A2 absorption, A3 funding extreme)
Headline: A2 n=170 INSUFFICIENT_N (< 180); A3 n=819 net60 -0.075 % t -3.82, net15 -0.090 % below the placebo band; no mark. A1 on full DEV NOT_RUN (no aggTrades).

| Event | Horizon | n | mean net % | sd | t | share positive | placebo 1-99 % | session mix | Regime mix |
|---|---|---|---|---|---|---|---|---|---|
| A2 absorption | 15m | 170 INSUFFICIENT_N | -0.059 | 0.591 | -1.30 | 38.8 % | n/a | Asia 35 Europe 48 US 72 Late 15 | n/a 6 range 103 bear 10 bull 51 |
| A2 absorption | 60m | 170 INSUFFICIENT_N | -0.034 | 0.895 | -0.49 | 47.6 % | n/a | Asia 35 Europe 48 US 72 Late 15 | n/a 6 range 103 bear 10 bull 51 |
| A3 funding extreme | 15m | 819 | -0.090 | 0.321 | -8.04 | 32.2 % | -0.123..-0.075 | Asia 275 Europe 274 US 270 Late 0 | n/a 65 range 344 bear 127 bull 283 |
| A3 funding extreme | 60m | 819 | -0.075 | 0.562 | -3.82 | 37.2 % | -0.138..-0.045 | Asia 275 Europe 274 US 270 Late 0 | n/a 65 range 344 bear 127 bull 283 |

## Decision
No cell has DEV |z|>=2 vs placebo with positive net after the 10 bp fee. No PAPER_SLOT.md. NOT_IN_DATA.md names the missing feeds. DECISION (OURS): conservative, no rule frozen.
