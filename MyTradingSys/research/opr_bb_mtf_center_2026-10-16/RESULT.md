INCONCLUSIVE

# RESULT: OPR-BB-MTF-CENTER, 1h touch of the BB mid in a lower-band trend, DEV screen (primary cell 1 min extra delay, h=120, cost 0.14 % round trip) + Krown M1-M4 descriptive tables

**Screen, ran before G3 marks by operator decision 2026-10-16.** DEV-only exploration (bars before 2024-07-01); VALIDATION and HOLDOUT were not read. Rules frozen in PRE_REG.md (committed before this file). SOURCED = the operator's words in the draft (closes around the centre decide direction/confirmation/range; 30m centre closes; next 1-4 h); every threshold, entry, horizon and cost is OURS, written in PRE_REG.md before the run (the operator states no entry or stop).

Study word = INCONCLUSIVE (PASS if any verdict arm passes; FAIL only if every arm is FAIL; otherwise INCONCLUSIVE). Verdict arms: AU INCONCLUSIVE; AD FAIL.

## Verdict arms (mean G % of notional after funding; SE day-clustered; control = wick touches of the 1h mid with NO precondition, same closing side, same cooldown)

| arm | n | mean G % (after funding) | SE (day-cl.) | net of 0.14 % | t_net | n_ctrl | mean_ctrl | DIFF vs ctrl % | t_DIFF | MDD (% clip) | MDE 80 % (2.8 SE) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AU: touch bar closes above its mid, LONG, h=120 | 194 | 0.0196 | 0.0824 | -0.1204 | -1.46 | 3951 | 0.0162 | 0.0034 | 0.04 | 26.41 | 0.2308 | INCONCLUSIVE |
| AD: touch bar closes below its mid, SHORT, h=120 | 282 | 0.0322 | 0.0397 | -0.1078 | -2.71 | 1572 | -0.0387 | 0.0709 | 1.56 | 34.79 | 0.1112 | FAIL |

Buy-and-hold DEV max drawdown 67.80 % of price. PASS needs n >= 200, mean >= 0.14 %, t_net >= 2, DIFF >= +0.05 % with t >= 2, MDD <= BH MDD.

## Secondary cells (no verdict)

| arm | n | mean G % (after funding) | SE (day-cl.) | net of 0.14 % | t_net | n_ctrl | mean_ctrl | DIFF vs ctrl % | t_DIFF | MDD (% clip) | MDE 80 % (2.8 SE) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AU h=60 | 194 | 0.0121 | 0.0598 | -0.1279 | -2.14 | 3952 | 0.0034 | 0.0087 | 0.14 | 25.24 | 0.1676 | secondary |
| AD h=60 | 282 | -0.0098 | 0.0266 | -0.1498 | -5.64 | 1572 | -0.0314 | 0.0215 | 0.71 | 42.60 | 0.0744 | secondary |
| AU h=240 | 194 | -0.0112 | 0.1094 | -0.1512 | -1.38 | 3951 | 0.0207 | -0.0319 | -0.29 | 32.01 | 0.3064 | secondary |
| AD h=240 | 282 | 0.0243 | 0.0644 | -0.1157 | -1.80 | 1572 | -0.0433 | 0.0676 | 0.95 | 38.38 | 0.1804 | secondary |

## U / D / R (primary events; counter-trend band = the touch bar's UPPER band, trend-continuation = its LOWER band; fixed levels; Wilson 95 % CI; cells with n < 10 are not read)

| set | H (h) | n | P(counter-trend band first) | P(trend-continuation band first) | P(neither) | both in one minute |
|---|---|---|---|---|---|---|
| primary: 1h, N=6, wick, first touch | 1 | 476 | 34/476 = 7.1% [5.2, 9.8] | 41/476 = 8.6% [6.4, 11.5] | 401/476 = 84.2% [80.7, 87.2] | 0 |
| primary: 1h, N=6, wick, first touch | 2 | 476 | 50/476 = 10.5% [8.1, 13.6] | 71/476 = 14.9% [12.0, 18.4] | 355/476 = 74.6% [70.5, 78.3] | 0 |
| primary: 1h, N=6, wick, first touch | 4 | 476 | 99/476 = 20.8% [17.4, 24.7] | 118/476 = 24.8% [21.1, 28.9] | 259/476 = 54.4% [49.9, 58.8] | 0 |

## U / D / R, H = 2 h, by condition (30m centre-close, pressure eases, flow, session, width, variants)

| set | H (h) | n | P(counter-trend band first) | P(trend-continuation band first) | P(neither) | both in one minute |
|---|---|---|---|---|---|---|
| 30m centre-close ON (m=2, y=0.25) | 2 | 71 | 6/71 = 8.5% [3.9, 17.2] | 5/71 = 7.0% [3.0, 15.4] | 60/71 = 84.5% [74.3, 91.1] | 0 |
| 30m centre-close OFF | 2 | 405 | 44/405 = 10.9% [8.2, 14.3] | 66/405 = 16.3% [13.0, 20.2] | 295/405 = 72.8% [68.3, 76.9] | 0 |
| 30m centre-close ON (m=2, y=0.5) | 2 | 204 | 15/204 = 7.4% [4.5, 11.8] | 28/204 = 13.7% [9.7, 19.1] | 161/204 = 78.9% [72.8, 84.0] | 0 |
| 30m centre-close ON (m=3, y=0.25) | 2 | 40 | 2/40 = 5.0% [1.4, 16.5] | 2/40 = 5.0% [1.4, 16.5] | 36/40 = 90.0% [76.9, 96.0] | 0 |
| 30m centre-close ON (m=3, y=0.5) | 2 | 165 | 11/165 = 6.7% [3.8, 11.5] | 24/165 = 14.5% [10.0, 20.7] | 130/165 = 78.8% [71.9, 84.3] | 0 |
| pressure eases (delta4) true | 2 | 388 | 47/388 = 12.1% [9.2, 15.7] | 47/388 = 12.1% [9.2, 15.7] | 294/388 = 75.8% [71.3, 79.8] | 0 |
| pressure eases (delta4) false | 2 | 88 | 3/88 = 3.4% [1.2, 9.5] | 24/88 = 27.3% [19.1, 37.4] | 61/88 = 69.3% [59.0, 78.0] | 0 |
| pressure eases (rsi) true | 2 | 431 | 49/431 = 11.4% [8.7, 14.7] | 57/431 = 13.2% [10.3, 16.8] | 325/431 = 75.4% [71.1, 79.2] | 0 |
| pressure eases (rsi) false | 2 | 45 | 1/45 = 2.2% [0.4, 11.6] | 14/45 = 31.1% [19.5, 45.7] | 30/45 = 66.7% [52.1, 78.6] | 0 |
| touch-bar taker delta > 0 | 2 | 374 | 46/374 = 12.3% [9.3, 16.0] | 43/374 = 11.5% [8.6, 15.1] | 285/374 = 76.2% [71.6, 80.2] | 0 |
| touch-bar taker delta <= 0 | 2 | 102 | 4/102 = 3.9% [1.5, 9.7] | 28/102 = 27.5% [19.7, 36.8] | 70/102 = 68.6% [59.1, 76.8] | 0 |
| decision 0-60 min after the US open | 2 | 28 | 9/28 = 32.1% [17.9, 50.7] | 8/28 = 28.6% [15.3, 47.1] | 11/28 = 39.3% [23.6, 57.6] | 0 |
| decision elsewhere | 2 | 448 | 41/448 = 9.2% [6.8, 12.2] | 63/448 = 14.1% [11.1, 17.6] | 344/448 = 76.8% [72.7, 80.5] | 0 |
| BB width above DEV median | 2 | 214 | 18/214 = 8.4% [5.4, 12.9] | 19/214 = 8.9% [5.8, 13.4] | 177/214 = 82.7% [77.1, 87.2] | 0 |
| BB width at/below DEV median | 2 | 262 | 32/262 = 12.2% [8.8, 16.7] | 52/262 = 19.8% [15.5, 25.1] | 178/262 = 67.9% [62.1, 73.3] | 0 |
| variant ('wick', 3) | 2 | 571 | 84/571 = 14.7% [12.0, 17.9] | 86/571 = 15.1% [12.4, 18.2] | 401/571 = 70.2% [66.4, 73.8] | 0 |
| variant ('wick', 12) | 2 | 327 | 38/327 = 11.6% [8.6, 15.5] | 38/327 = 11.6% [8.6, 15.5] | 251/327 = 76.8% [71.9, 81.0] | 0 |
| variant ('near0.1', 6) | 2 | 459 | 32/459 = 7.0% [5.0, 9.7] | 78/459 = 17.0% [13.8, 20.7] | 349/459 = 76.0% [71.9, 79.7] | 0 |
| variant ('near0.25', 6) | 2 | 444 | 20/444 = 4.5% [2.9, 6.9] | 89/444 = 20.0% [16.6, 24.0] | 335/444 = 75.5% [71.2, 79.2] | 0 |
| variant ('close0.0', 6) | 2 | 499 | 125/499 = 25.1% [21.4, 29.0] | 30/499 = 6.0% [4.2, 8.5] | 344/499 = 68.9% [64.7, 72.8] | 0 |

## Controls (mirror shows the trend-continuation band as the UPPER band)

| set | H (h) | n | P(counter-trend band first) | P(trend-continuation band first) | P(neither) | both in one minute |
|---|---|---|---|---|---|---|
| control: mirror (up-trend touch from above, bands fixed) | 1 | 500 | 47/500 = 9.4% [7.1, 12.3] | 37/500 = 7.4% [5.4, 10.0] | 416/500 = 83.2% [79.7, 86.2] | 0 |
| control: mirror (up-trend touch from above, bands fixed) | 2 | 500 | 73/500 = 14.6% [11.8, 18.0] | 71/500 = 14.2% [11.4, 17.5] | 356/500 = 71.2% [67.1, 75.0] | 0 |
| control: mirror (up-trend touch from above, bands fixed) | 4 | 500 | 112/500 = 22.4% [19.0, 26.3] | 111/500 = 22.2% [18.8, 26.0] | 277/500 = 55.4% [51.0, 59.7] | 0 |
| control: 30m mid touch (N=6), bands of the 30m bar | 1 | 1014 | 116/1014 = 11.4% [9.6, 13.5] | 118/1014 = 11.6% [9.8, 13.8] | 779/1014 = 76.8% [74.1, 79.3] | 1 |
| control: 30m mid touch (N=6), bands of the 30m bar | 2 | 1014 | 176/1014 = 17.4% [15.2, 19.8] | 191/1014 = 18.8% [16.5, 21.4] | 646/1014 = 63.7% [60.7, 66.6] | 1 |
| control: 30m mid touch (N=6), bands of the 30m bar | 4 | 1014 | 271/1014 = 26.7% [24.1, 29.5] | 286/1014 = 28.2% [25.5, 31.1] | 456/1014 = 45.0% [41.9, 48.0] | 1 |
| control: same trend state, random hours (no touch required, seed 0, <= 3000) | 1 | 3000 | 56/3000 = 1.9% [1.4, 2.4] | 774/3000 = 25.8% [24.3, 27.4] | 2170/3000 = 72.3% [70.7, 73.9] | 0 |
| control: same trend state, random hours (no touch required, seed 0, <= 3000) | 2 | 3000 | 106/3000 = 3.5% [2.9, 4.3] | 987/3000 = 32.9% [31.2, 34.6] | 1907/3000 = 63.6% [61.8, 65.3] | 0 |
| control: same trend state, random hours (no touch required, seed 0, <= 3000) | 4 | 3000 | 199/3000 = 6.6% [5.8, 7.6] | 1252/3000 = 41.7% [40.0, 43.5] | 1549/3000 = 51.6% [49.8, 53.4] | 0 |
| control: wick touch of the mid with no precondition | 1 | 12930 | 3572/12930 = 27.6% [26.9, 28.4] | 775/12930 = 6.0% [5.6, 6.4] | 8582/12930 = 66.4% [65.6, 67.2] | 1 |
| control: wick touch of the mid with no precondition | 2 | 12929 | 4531/12929 = 35.0% [34.2, 35.9] | 1205/12929 = 9.3% [8.8, 9.8] | 7192/12929 = 55.6% [54.8, 56.5] | 1 |
| control: wick touch of the mid with no precondition | 4 | 12927 | 5676/12927 = 43.9% [43.1, 44.8] | 1816/12927 = 14.0% [13.5, 14.7] | 5434/12927 = 42.0% [41.2, 42.9] | 1 |

## Close side of the 1h mid (touch bar and the next three closed bars)

| bar | n | closes above its own mid |
|---|---|---|
| touch bar k | 476 | 194/476 = 40.8% [36.4, 45.2] |
| bar k+1 | 476 | 243/476 = 51.1% [46.6, 55.5] |
| bar k+2 | 476 | 232/476 = 48.7% [44.3, 53.2] |
| bar k+3 | 476 | 246/476 = 51.7% [47.2, 56.1] |
| next 1 closes: all above / all below / mixed | 476 | 243 / 233 / 0 |
| next 2 closes: all above / all below / mixed | 476 | 188 / 189 / 99 |
| next 3 closes: all above / all below / mixed | 476 | 161 / 150 / 165 |

## MFE / MAE in ATR(14, 1h) from the entry open after the touch-bar close (medians)

| side | h (min) | n | median MFE | median MAE |
|---|---|---|---|---|
| LONG from touch-bar close | 60 | 476 | 0.38 | 0.36 |
| LONG from touch-bar close | 120 | 476 | 0.48 | 0.55 |
| LONG from touch-bar close | 240 | 476 | 0.77 | 0.75 |
| SHORT from touch-bar close | 60 | 476 | 0.36 | 0.38 |
| SHORT from touch-bar close | 120 | 476 | 0.55 | 0.48 |
| SHORT from touch-bar close | 240 | 476 | 0.75 | 0.77 |

## Krown range tests M1-M4 (descriptive only; OURS definitions; no verdict; not a confirmation or refutation of Krown)

### 1h: M1 range detector (n bars, zone tolerance x): number of ranges and median height % of the low

| n | x | ranges | median height % |
|---|---|---|---|
| 24 | 0.25 % | 345 | 2.08 |
| 24 | 0.50 % | 542 | 2.64 |
| 48 | 0.25 % | 196 | 3.58 |
| 48 | 0.50 % | 291 | 4.10 |
| 96 | 0.25 % | 97 | 6.60 |
| 96 | 0.50 % | 154 | 6.77 |

M2 band vs edges: share of bars with BOTH bands within y of the range high/low, and with the BB mid within y of the range midpoint

| windows | y | windows n | bars | both bands near edges | BB mid near midpoint |
|---|---|---|---|---|---|
| ranges (n=48, x=0.5 %) | 0.25 % | 291 | 13950 | 328/13950 = 2.4% [2.1, 2.6] | 3777/13950 = 27.1% [26.3, 27.8] |
| ranges (n=48, x=0.5 %) | 0.50 % | 291 | 13950 | 1423/13950 = 10.2% [9.7, 10.7] | 6294/13950 = 45.1% [44.3, 45.9] |
| ranges (n=48, x=0.5 %) | 1.00 % | 291 | 13950 | 4746/13950 = 34.0% [33.2, 34.8] | 9409/13950 = 67.4% [66.7, 68.2] |
| random windows failing the range test (seed 0) | 0.25 % | 291 | 13968 | 90/13968 = 0.6% [0.5, 0.8] | 1920/13968 = 13.7% [13.2, 14.3] |
| random windows failing the range test (seed 0) | 0.50 % | 291 | 13968 | 385/13968 = 2.8% [2.5, 3.0] | 3971/13968 = 28.4% [27.7, 29.2] |
| random windows failing the range test (seed 0) | 1.00 % | 291 | 13968 | 1893/13968 = 13.6% [13.0, 14.1] | 6879/13968 = 49.2% [48.4, 50.1] |

M3 pokes: reach the opposite range edge / the opposite BB band (fixed at the close-back bar) within 24 bars

| event | n | opposite range edge reached | opposite BB band reached |
|---|---|---|---|
| poke back inside within k=1 | 205 pokes, 112 back inside | 20/112 = 17.9% [11.9, 26.0] | 43/112 = 38.4% [29.9, 47.6] |
| poke back inside within k=2 | 205 pokes, 135 back inside | 24/135 = 17.8% [12.2, 25.1] | 55/135 = 40.7% [32.8, 49.2] |
| poke back inside within k=3 | 205 pokes, 143 back inside | 24/143 = 16.8% [11.5, 23.8] | 57/143 = 39.9% [32.2, 48.0] |
| control: first close outside the BB band (opposite band, fixed at the event bar) | 1345 events | n/a | 472/1341 = 35.2% [32.7, 37.8] |

M4 midpoint: share of the next 1 / 2 / 3 closes ABOVE the midpoint after a bar that touches it (descriptive; touches in one range overlap)

| midpoint | approach | n | next close above | 2nd close above | 3rd close above |
|---|---|---|---|---|---|
| range midpoint | from below | 1706 | 822/1706 = 48.2% [45.8, 50.6] | 845/1706 = 49.5% [47.2, 51.9] | 857/1706 = 50.2% [47.9, 52.6] |
| range midpoint | from above | 1679 | 865/1679 = 51.5% [49.1, 53.9] | 852/1679 = 50.7% [48.4, 53.1] | 848/1679 = 50.5% [48.1, 52.9] |
| BB mid inside the range | from below | 2015 | 1033/2015 = 51.3% [49.1, 53.4] | 1012/2015 = 50.2% [48.0, 52.4] | 1025/2015 = 50.9% [48.7, 53.0] |
| BB mid inside the range | from above | 2041 | 1076/2041 = 52.7% [50.6, 54.9] | 1123/2041 = 55.0% [52.9, 57.2] | 1110/2041 = 54.4% [52.2, 56.5] |

### 4h: M1 range detector (n bars, zone tolerance x): number of ranges and median height % of the low

| n | x | ranges | median height % |
|---|---|---|---|
| 24 | 0.25 % | 43 | 4.67 |
| 24 | 0.50 % | 106 | 5.67 |
| 48 | 0.25 % | 31 | 10.60 |
| 48 | 0.50 % | 58 | 9.82 |
| 96 | 0.25 % | 16 | 20.34 |
| 96 | 0.50 % | 28 | 15.23 |

M2 band vs edges: share of bars with BOTH bands within y of the range high/low, and with the BB mid within y of the range midpoint

| windows | y | windows n | bars | both bands near edges | BB mid near midpoint |
|---|---|---|---|---|---|
| ranges (n=48, x=0.5 %) | 0.25 % | 58 | 2765 | 16/2765 = 0.6% [0.4, 0.9] | 299/2765 = 10.8% [9.7, 12.0] |
| ranges (n=48, x=0.5 %) | 0.50 % | 58 | 2765 | 63/2765 = 2.3% [1.8, 2.9] | 559/2765 = 20.2% [18.8, 21.8] |
| ranges (n=48, x=0.5 %) | 1.00 % | 58 | 2765 | 304/2765 = 11.0% [9.9, 12.2] | 992/2765 = 35.9% [34.1, 37.7] |
| random windows failing the range test (seed 0) | 0.25 % | 58 | 2784 | 7/2784 = 0.3% [0.1, 0.5] | 213/2784 = 7.7% [6.7, 8.7] |
| random windows failing the range test (seed 0) | 0.50 % | 58 | 2784 | 26/2784 = 0.9% [0.6, 1.4] | 443/2784 = 15.9% [14.6, 17.3] |
| random windows failing the range test (seed 0) | 1.00 % | 58 | 2784 | 97/2784 = 3.5% [2.9, 4.2] | 724/2784 = 26.0% [24.4, 27.7] |

M3 pokes: reach the opposite range edge / the opposite BB band (fixed at the close-back bar) within 24 bars

| event | n | opposite range edge reached | opposite BB band reached |
|---|---|---|---|
| poke back inside within k=1 | 44 pokes, 24 back inside | 4/24 = 16.7% [6.7, 35.9] | 10/24 = 41.7% [24.5, 61.2] |
| poke back inside within k=2 | 44 pokes, 28 back inside | 4/28 = 14.3% [5.7, 31.5] | 11/28 = 39.3% [23.6, 57.6] |
| poke back inside within k=3 | 44 pokes, 30 back inside | 4/30 = 13.3% [5.3, 29.7] | 11/30 = 36.7% [21.9, 54.5] |
| control: first close outside the BB band (opposite band, fixed at the event bar) | 312 events | n/a | 91/310 = 29.4% [24.6, 34.7] |

M4 midpoint: share of the next 1 / 2 / 3 closes ABOVE the midpoint after a bar that touches it (descriptive; touches in one range overlap)

| midpoint | approach | n | next close above | 2nd close above | 3rd close above |
|---|---|---|---|---|---|
| range midpoint | from below | 250 | 123/250 = 49.2% [43.1, 55.4] | 119/250 = 47.6% [41.5, 53.8] | 126/250 = 50.4% [44.2, 56.5] |
| range midpoint | from above | 266 | 142/266 = 53.4% [47.4, 59.3] | 136/266 = 51.1% [45.1, 57.1] | 128/266 = 48.1% [42.2, 54.1] |
| BB mid inside the range | from below | 370 | 167/370 = 45.1% [40.1, 50.2] | 179/370 = 48.4% [43.3, 53.5] | 177/370 = 47.8% [42.8, 52.9] |
| BB mid inside the range | from above | 421 | 243/421 = 57.7% [53.0, 62.3] | 237/421 = 56.3% [51.5, 61.0] | 241/421 = 57.2% [52.5, 61.9] |

## Data and decisions

OI NOT_IN_DATA on DEV. The 'pressure eases' CVD-slope measure equals the 30m taker-delta measure over the same bars, so only delta4 and RSI are printed. Funding flat 1 bp per settlement crossed. A PASS would be a gross-effect finding on the Binance tape only.

## Count section (no return, U/D/R or other outcome column was computed)

1m bars missing on the DEV tape: 0 of 1313280. 1h bars 21888 (0 incomplete), 30m bars 43776, 4h bars 5472.
First-touch events, 1h, N=6, wick rule (primary): **n = 476** (closing above the mid 194, below 282). Precondition met before the bar (any touch state): 6047 bars.
Other event sets: wick N=3: 571; wick N=12: 327; near0.1 N=6: 459; near0.25 N=6: 444; close0.0 N=6: 499; mirror: 500; 30m: 1014.
Verdict arms after the 120-minute cooldown: AU (touch bar closes above its mid, LONG) n = 194, control (touch, no precondition, closes above) n = 3952; AD (closes below, SHORT) n = 282, control n = 1572.
Krown range detector (1h): n=24,x=0.0025: 345, n=24,x=0.005: 542, n=48,x=0.0025: 196, n=48,x=0.005: 291, n=96,x=0.0025: 97, n=96,x=0.005: 154; (4h): n=24,x=0.0025: 43, n=24,x=0.005: 106, n=48,x=0.0025: 31, n=48,x=0.005: 58, n=96,x=0.0025: 16, n=96,x=0.005: 28.
OI: NOT_IN_DATA on DEV (metrics archive starts 2025-09-01). Funding: raw_fund archive absent -> flat 1 bp per settlement crossed.
