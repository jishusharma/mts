As a stand-alone ride-it-all-cycle rule the belief does not hold on BTC: the signal is rare (since 2017 on BTC: 1D 19 bearish / 17 bullish, 3D 7 / 2, 1W 3 / 3), 14 of the 19 daily bearish signals fired inside bull markets where riding the short to the next bullish divergence lost on average 53% per trade (26% win, ~190 days), and the stop-at-pivot version is stopped out in 75-95% of higher-timeframe cases; it did flag two real tops (1D 2021-11-10 at 69,000, 1W 2025-10-06 at 126,200) but nothing visible at signal time separated those from the failures, and on the long side random entries ridden the same way did better than the signals.

# htf-divergence-outside-bb-ride-1114 (2026-11-14)

Study of: "short with divergence outside the Bollinger Band on higher timeframes, with confirmation and confluence, ride it the full cycle; same for longs." Understanding first; pre-registered rules in PRE_REG.md (committed before any outcome), code in study.py, full tables in tables.md, every BTC 1D/3D/1W signal in btc_signals_1d_3d_1w.csv. Data: Binance spot 4h/1d/1w (3D = daily regrouped on Binance's epoch-day//3 alignment) for BTC, ETH, SOL, BNB, XRP from listing to 2026-11-13; cached in F:\MTS\data_cache\binance_spot_htf. Spot prices stand in for perpetuals (no funding), fee 12 bp round trip.

## What I learned (plain words)

| # | Finding | Evidence |
|---|---|---|
| 1 | The signal is a rarity on higher timeframes. A pivot high that is also outside the band AND has a lower RSI than the previous pivot happens about twice a year on 1D, once a year on 3D, once every 2-3 years on 1W. The sample is too small to prove or kill anything on 3D/1W. | Counts table |
| 2 | Bearish divergence outside the upper band mostly appears while the trend is still going up. A lower RSI high with price above the band is trend strength, not exhaustion, in most cases (2020: four 1D shorts in 5 months; three were stopped at the pivot, and every full-cycle ride lost 27 to 77 R). | 1D shorts by phase: bull 14, bear 3, base 2; 3D and 1W shorts: all in bull |
| 3 | "Ride it until the opposite signal" is the part that breaks. The opposite (bullish) signal arrives only at the next washout, so a short opened in a bull market is carried hundreds of days against a rising price. | 1D short full-cycle: n=19, 26% win, mean -53% per trade, median 189 d; 3D: n=7, 0% win; flip equity 1D RSI ends 0.08x vs buy-and-hold 18x |
| 4 | With the stop at the pivot high it is the opposite problem: the divergence extreme is very often exceeded. 1D shorts: 5% win; 3D: 0% win (7 of 7). 4H is the only place the stopped version is not clearly negative (+0.17 R, placebo -0.17 R, CI includes 0). | BTC RSI tables, placebo table |
| 5 | Confirmation changes little on higher timeframes. "Close back inside the band" is identical to no confirmation on 1D/3D/1W (price is already back inside by the 2-bar pivot confirmation). Break of the swing low or MACD cross cut the trades by 40-70% and shrink the full-cycle loss (1D shorts -14.6 R to -3.1 R) but stay negative. Confluence of RSI and WaveTrend: fewer signals, same story. | Confirm rows in BTC tables |
| 6 | Phase matters more than the confirmation. 4H shorts in the post-peak bear phase: +1.03 R with the pivot stop (n=28, 36% win) vs +0.02 R in bull phase (n=47). Same direction as your belief (shorts belong to the bear phase), but only on 4H and with a wide interval; higher timeframes have almost no bear-phase shorts to test (1D 3, 3D 0, 1W 0). | Phase table |
| 7 | Bullish side: higher-timeframe bullish divergence outside the lower band looks better in raw numbers (BTC 1W longs 3/3 winners, +40% per trade full-cycle; pooled five symbols 3D n=16, 69% win, +12.9 R; 1W n=7, 7/7 up) but it does not beat the alternatives: placebo long entries on random bars ridden the same way give +2.0 R (1D), +9.8 R (3D), +12.2 R (1W) vs signals -0.03, -4.8, +2.5, and forward returns after bullish 3D signals (+16.5% at 60 bars) are below the average 3D bar (+54%, crypto drift). It is a "buy washouts in a rising asset" effect, not a timing edge. | Placebo and forward-return tables |
| 8 | Two cells look significant for BTC (1D bullish + swing-break + full-cycle: +1.5 R, CI [0.55, 2.60], n=10; WT 1D bullish full-cycle +5.3 R, n=7) but there are about 320 cells in the BTC tables; a handful will show CI above zero by chance. Not a finding. | multiplicity |
| 9 | What did work as a story: the 1W bearish signal at the Oct 2025 top (126,200, RSI 63.6 then 55.4, band exceeded; +4.4 R full-cycle) and the 1D at the Nov 2021 top (+5.4 R). At the June-July 2026 lows both a 1W (pivot 2026-06-01, low 59,131) and a 1D (pivot 2026-07-01, low 57,800, confirmed 2026-07-04) bullish divergence outside the lower band printed. The 1W one was exceeded on the downside two weeks later (low 58,115, 57,800) before the move to 87k; the 1D one was at the low. Anecdotes, n=1 each. | CSV |

Why the operator's picture and these numbers can both be true: the divergence is a good marker of where a move is stretched, but "stretched" often keeps going in a trend; riding for a full cycle needs a rule for when NOT to take the signal (trend phase) and a stop wider than the pivot, and those are exactly the parts the data does not yet support on higher timeframes because there are so few cases. What the data does hint at: use the phase filter (bear-phase shorts, base-or-bear-phase longs) and look at 4H/1D for entries inside a 1W/3D context, which is a multi-timeframe rule that has not been tested here.

Caveats: signals overlap in time (4H clusters), so n overstates independence; shorts are simulated on spot data; the no-stop full-cycle R is expressed in pivot-stop units, so huge negative R values (like -38) mean "price went far above a tight stop", which is why per-trade percent return is shown next to it; the phase label uses a daily SMA200 rule (OURS), n/a before 2018-03.

## Context

Regime mix of BTC days since 2018-03 (rule: bull = close above rising daily SMA200, bear = below and falling, base = rest): bull 47%, bear 31%, base 22% (3,146 days). Current label (2026-11-13): base. Signal mix: BTC RSI 1D shorts bull 14 / bear 3 / base 2; 1D longs bear 8 / bull 8 / base 1; 3D shorts bull 7; 1W shorts bull 3, 1W longs one each. DEV is to 2023-12-31, VALIDATION 2024+, so VALIDATION contains one bull leg and the 2025-26 decline; 1W has 1 DEV and 2 VAL shorts. All labels use data known at the signal close. Sources: thresholds, indicator settings, phase rule, stop and exit definitions are OURS (RSI 14 / BB 20,2 / MACD 12,26,9 are conventional); fee 12 bp SOURCED (fees.py + slippage per other PRE_REGs).


## Signal counts and results

Generated by study.py (same text in tables.md). Cell format: n / win / mean net R / 95% bootstrap CI / median hold / mean per-trade percent return. Full-cycle ('opp') rows are best read in percent.

### Signal counts (confirm none)
|sym|tf|bear RSI high-out|bear RSI close-out|bear WT high-out|bull RSI high-out|bull RSI close-out|bull WT high-out|
|-|-|-|-|-|-|-|-|
|BTC|4h|105|7|90|105|4|98|
|BTC|1d|19|4|15|17|0|7|
|BTC|3d|7|2|6|2|0|4|
|BTC|1w|3|1|2|3|0|2|
|ETH|4h|90|6|92|87|8|94|
|ETH|1d|13|1|14|13|0|12|
|ETH|3d|6|1|3|3|0|3|
|ETH|1w|2|0|0|2|0|2|
|SOL|4h|82|4|67|79|5|56|
|SOL|1d|7|2|8|8|0|7|
|SOL|3d|2|0|1|2|0|1|
|SOL|1w|3|2|2|1|0|2|
|BNB|4h|98|9|68|76|3|79|
|BNB|1d|21|4|17|9|0|5|
|BNB|3d|6|0|7|2|0|3|
|BNB|1w|2|1|0|1|0|1|
|XRP|4h|60|6|75|86|7|76|
|XRP|1d|14|1|7|13|0|8|
|XRP|3d|3|0|2|7|0|3|
|XRP|1w|2|0|2|0|0|3|

### BTC RSI short: cell = n / win / mean net R / 95% CI / median hold
|tf|confirm|opp|opp_stop|2R|3R|trail|
|-|-|-|-|-|-|-|
|4h|none|99 / 45% / -10.64 R / [-19.68,-3.43] / 18d / -20.8% per trade|99 / 20% / +0.17 R / [-0.44,1.02] / 3d / -0.5% per trade|99 / 42% / +0.21 R / [-0.07,0.51] / 1d / +0.3% per trade|99 / 30% / +0.14 R / [-0.22,0.50] / 2d / +0.1% per trade|99 / 38% / +0.10 R / [-0.20,0.48] / 1d / +0.2% per trade|
|4h|backin|100 / 45% / -10.65 R / [-20.01,-3.46] / 19d / -20.7% per trade|100 / 20% / +0.15 R / [-0.46,0.97] / 2d / -0.5% per trade|100 / 43% / +0.22 R / [-0.07,0.51] / 1d / +0.3% per trade|100 / 30% / +0.13 R / [-0.23,0.51] / 2d / +0.1% per trade|100 / 39% / +0.10 R / [-0.20,0.48] / 1d / +0.2% per trade|
|4h|swing|59 / 42% / -3.23 R / [-7.05,-0.59] / 15d / -14.1% per trade|59 / 39% / +0.16 R / [-0.29,0.66] / 5d / -0.1% per trade|59 / 39% / +0.14 R / [-0.22,0.50] / 5d / +0.3% per trade|59 / 31% / +0.18 R / [-0.28,0.66] / 7d / +0.2% per trade|59 / 47% / +0.22 R / [-0.06,0.52] / 3d / +0.9% per trade|
|4h|macd|56 / 48% / -7.86 R / [-16.05,-1.50] / 17d / -14.4% per trade|56 / 30% / +0.12 R / [-0.42,0.75] / 4d / -0.3% per trade|56 / 41% / +0.18 R / [-0.19,0.56] / 2d / +0.8% per trade|56 / 27% / +0.02 R / [-0.41,0.52] / 2d / -0.1% per trade|56 / 41% / +0.17 R / [-0.28,0.80] / 2d / +0.0% per trade|
|1d|none|19 / 26% / -14.59 R / [-24.99,-6.05] / 189d / -53.2% per trade|19 / 5% / -0.70 R / [-1.04,-0.02] / 7d / -2.9% per trade|19 / 21% / -0.40 R / [-0.88,0.23] / 6d / -2.4% per trade|19 / 16% / -0.40 R / [-1.03,0.23] / 6d / -2.6% per trade|19 / 26% / -0.12 R / [-0.65,0.53] / 5d / -0.4% per trade|
|1d|backin|19 / 26% / -14.59 R / [-24.57,-6.51] / 189d / -53.2% per trade|19 / 5% / -0.70 R / [-1.04,-0.02] / 7d / -2.9% per trade|19 / 21% / -0.40 R / [-0.88,0.23] / 6d / -2.4% per trade|19 / 16% / -0.40 R / [-1.03,0.23] / 6d / -2.6% per trade|19 / 26% / -0.12 R / [-0.66,0.52] / 5d / -0.4% per trade|
|1d|swing|6 / 33% / -3.07 R / [-6.91,-0.07] / 188d / -60.1% per trade|6 / 17% / -0.58 R / [-1.01,0.29] / 34d / -12.8% per trade|6 / 33% / -0.01 R / [-1.00,0.99] / 20d / -6.8% per trade|6 / 17% / -0.34 R / [-1.01,0.99] / 34d / -7.8% per trade|6 / 33% / -0.12 R / [-0.56,0.36] / 11d / -5.8% per trade|
|1d|macd|8 / 25% / -10.69 R / [-23.45,-0.72] / 160d / -47.3% per trade|8 / 12% / -0.23 R / [-1.04,1.38] / 6d / +0.1% per trade|8 / 12% / -0.65 R / [-1.04,0.11] / 6d / -3.2% per trade|8 / 12% / -0.53 R / [-1.04,0.48] / 6d / -2.2% per trade|8 / 25% / -0.12 R / [-0.79,0.80] / 4d / +0.1% per trade|
|3d|none|7 / 0% / -38.27 R / [-76.42,-8.61] / 663d / -288.1% per trade|7 / 0% / -1.02 R / [-1.04,-1.01] / 15d / -12.3% per trade|7 / 14% / -0.59 R / [-1.03,0.27] / 15d / -8.6% per trade|7 / 0% / -1.02 R / [-1.04,-1.01] / 15d / -12.3% per trade|7 / 0% / -0.79 R / [-1.03,-0.50] / 12d / -9.6% per trade|
|3d|backin|7 / 0% / -38.27 R / [-75.68,-8.73] / 663d / -288.1% per trade|7 / 0% / -1.02 R / [-1.04,-1.01] / 15d / -12.3% per trade|7 / 14% / -0.59 R / [-1.03,0.27] / 15d / -8.6% per trade|7 / 0% / -1.02 R / [-1.04,-1.01] / 15d / -12.3% per trade|7 / 0% / -0.79 R / [-1.03,-0.52] / 12d / -9.6% per trade|
|3d|swing|3 / 0% / -5.08 R / n<5 / 363d / -122.0% per trade|3 / 0% / -1.01 R / n<5 / 132d / -28.7% per trade|3 / 33% / -0.01 R / n<5 / 45d / -18.3% per trade|3 / 0% / -1.01 R / n<5 / 132d / -28.7% per trade|3 / 33% / -0.20 R / n<5 / 33d / -0.3% per trade|
|3d|macd|5 / 0% / -22.83 R / [-48.26,-6.45] / 639d / -131.3% per trade|5 / 0% / -1.02 R / [-1.02,-1.01] / 3d / -9.8% per trade|5 / 20% / -0.42 R / [-1.02,0.79] / 3d / -4.6% per trade|5 / 0% / -1.02 R / [-1.03,-1.01] / 3d / -9.8% per trade|5 / 0% / -0.88 R / [-1.02,-0.62] / 3d / -8.6% per trade|
|1w|none|3 / 67% / +1.15 R / n<5 / 210d / +8.1% per trade|3 / 33% / +0.79 R / n<5 / 14d / +4.5% per trade|3 / 33% / -0.01 R / n<5 / 14d / -3.7% per trade|3 / 33% / +0.32 R / n<5 / 14d / -0.3% per trade|3 / 33% / +0.35 R / n<5 / 14d / -0.0% per trade|
|1w|backin|3 / 67% / +1.15 R / n<5 / 210d / +8.1% per trade|3 / 33% / +0.79 R / n<5 / 14d / +4.5% per trade|3 / 33% / -0.01 R / n<5 / 14d / -3.7% per trade|3 / 33% / +0.32 R / n<5 / 14d / -0.3% per trade|3 / 33% / +0.35 R / n<5 / 14d / -0.0% per trade|
|1w|swing|1 / 100% / +0.97 R / n<5 / 217d / +32.7% per trade|1 / 100% / +0.97 R / n<5 / 217d / +32.7% per trade|1 / 100% / +0.60 R / n<5 / 350d / +20.5% per trade|1 / 100% / +0.60 R / n<5 / 350d / +20.5% per trade|1 / 100% / +0.49 R / n<5 / 161d / +16.4% per trade|
|1w|macd|1 / 100% / +1.59 R / n<5 / 77d / +30.1% per trade|1 / 0% / -1.01 R / n<5 / 0d / -19.0% per trade|1 / 0% / -1.01 R / n<5 / 0d / -19.0% per trade|1 / 0% / -1.01 R / n<5 / 0d / -19.0% per trade|1 / 0% / -1.01 R / n<5 / 0d / -19.0% per trade|

### BTC RSI long: cell = n / win / mean net R / 95% CI / median hold
|tf|confirm|opp|opp_stop|2R|3R|trail|
|-|-|-|-|-|-|-|
|4h|none|105 / 51% / -0.58 R / [-3.37,2.37] / 22d / +5.9% per trade|105 / 26% / -0.12 R / [-0.47,0.30] / 3d / -0.3% per trade|105 / 37% / +0.06 R / [-0.23,0.34] / 2d / +0.1% per trade|105 / 30% / +0.12 R / [-0.22,0.50] / 2d / +0.4% per trade|105 / 36% / +0.11 R / [-0.17,0.41] / 1d / +0.4% per trade|
|4h|backin|105 / 51% / -0.58 R / [-3.18,2.28] / 22d / +5.9% per trade|105 / 26% / -0.12 R / [-0.48,0.29] / 3d / -0.3% per trade|105 / 37% / +0.06 R / [-0.22,0.34] / 2d / +0.1% per trade|105 / 30% / +0.12 R / [-0.22,0.47] / 2d / +0.4% per trade|105 / 36% / +0.11 R / [-0.16,0.46] / 1d / +0.4% per trade|
|4h|swing|64 / 50% / -0.03 R / [-0.87,0.80] / 15d / -1.7% per trade|64 / 31% / +0.05 R / [-0.43,0.68] / 6d / -0.3% per trade|64 / 28% / -0.18 R / [-0.51,0.19] / 6d / -0.8% per trade|64 / 22% / -0.15 R / [-0.53,0.28] / 6d / -0.9% per trade|64 / 28% / +0.10 R / [-0.28,0.53] / 2d / -0.1% per trade|
|4h|macd|59 / 44% / -1.65 R / [-4.65,0.68] / 27d / -1.6% per trade|59 / 24% / -0.06 R / [-0.60,0.61] / 3d / -0.8% per trade|59 / 39% / +0.13 R / [-0.23,0.53] / 2d / -0.1% per trade|59 / 27% / +0.04 R / [-0.37,0.52] / 3d / -1.0% per trade|59 / 29% / -0.01 R / [-0.32,0.42] / 1d / -0.2% per trade|
|1d|none|17 / 65% / -0.03 R / [-5.97,3.88] / 126d / +10.3% per trade|17 / 12% / -0.42 R / [-1.03,0.56] / 8d / -2.6% per trade|17 / 41% / +0.21 R / [-0.49,0.91] / 8d / -0.1% per trade|17 / 24% / -0.09 R / [-0.80,0.83] / 9d / -0.8% per trade|17 / 35% / -0.22 R / [-0.55,0.16] / 5d / -1.1% per trade|
|1d|backin|17 / 65% / -0.03 R / [-5.84,4.04] / 126d / +10.3% per trade|17 / 12% / -0.42 R / [-1.03,0.52] / 8d / -2.6% per trade|17 / 41% / +0.21 R / [-0.49,0.91] / 8d / -0.1% per trade|17 / 24% / -0.09 R / [-0.80,0.85] / 9d / -0.8% per trade|17 / 35% / -0.22 R / [-0.56,0.16] / 5d / -1.1% per trade|
|1d|swing|10 / 70% / +1.54 R / [0.55,2.60] / 124d / +16.1% per trade|10 / 20% / -0.03 R / [-0.94,1.26] / 16d / -4.8% per trade|10 / 30% / -0.11 R / [-1.01,0.79] / 10d / -3.6% per trade|10 / 20% / -0.21 R / [-1.01,0.99] / 23d / -7.2% per trade|10 / 30% / -0.15 R / [-0.53,0.34] / 14d / -3.1% per trade|
|1d|macd|9 / 67% / +2.22 R / [-0.62,5.21] / 125d / +9.7% per trade|9 / 11% / -0.22 R / [-1.02,1.35] / 8d / -2.8% per trade|9 / 22% / -0.35 R / [-1.02,0.65] / 8d / -4.3% per trade|9 / 11% / -0.57 R / [-1.02,0.32] / 9d / -5.4% per trade|9 / 33% / -0.17 R / [-0.65,0.47] / 4d / -2.3% per trade|
|3d|none|2 / 0% / -4.76 R / n<5 / 522d / -29.2% per trade|2 / 0% / -1.02 R / n<5 / 24d / -8.6% per trade|2 / 50% / +0.48 R / n<5 / 20d / -2.3% per trade|2 / 0% / -1.02 R / n<5 / 24d / -8.6% per trade|2 / 50% / +0.21 R / n<5 / 14d / -0.6% per trade|
|3d|backin|2 / 0% / -4.76 R / n<5 / 522d / -29.2% per trade|2 / 0% / -1.02 R / n<5 / 24d / -8.6% per trade|2 / 50% / +0.48 R / n<5 / 20d / -2.3% per trade|2 / 0% / -1.02 R / n<5 / 24d / -8.6% per trade|2 / 50% / +0.21 R / n<5 / 14d / -0.6% per trade|
|3d|swing|1 / 0% / -2.05 R / n<5 / 654d / -28.9% per trade|1 / 0% / -1.01 R / n<5 / 30d / -14.2% per trade|1 / 0% / -1.01 R / n<5 / 30d / -14.2% per trade|1 / 0% / -1.01 R / n<5 / 30d / -14.2% per trade|1 / 0% / -0.43 R / n<5 / 12d / -6.0% per trade|
|3d|macd|0|0|0|0|0|
|1w|none|3 / 100% / +2.49 R / n<5 / 427d / +39.6% per trade|3 / 33% / +0.43 R / n<5 / 301d / +18.5% per trade|3 / 67% / +0.99 R / n<5 / 21d / +24.1% per trade|3 / 67% / +1.66 R / n<5 / 49d / +37.3% per trade|3 / 67% / +0.94 R / n<5 / 147d / +21.0% per trade|
|1w|backin|3 / 100% / +2.49 R / n<5 / 427d / +39.6% per trade|3 / 33% / +0.43 R / n<5 / 301d / +18.5% per trade|3 / 67% / +0.99 R / n<5 / 21d / +24.1% per trade|3 / 67% / +1.66 R / n<5 / 49d / +37.3% per trade|3 / 67% / +0.94 R / n<5 / 147d / +21.0% per trade|
|1w|swing|3 / 33% / +0.14 R / n<5 / 350d / +6.8% per trade|3 / 33% / -0.10 R / n<5 / 266d / -2.6% per trade|3 / 0% / -0.52 R / n<5 / 266d / -19.1% per trade|3 / 0% / -0.52 R / n<5 / 266d / -19.1% per trade|3 / 67% / -0.08 R / n<5 / 112d / -2.0% per trade|
|1w|macd|3 / 67% / +1.14 R / n<5 / 371d / +21.8% per trade|3 / 67% / +0.92 R / n<5 / 259d / +12.8% per trade|3 / 67% / +0.99 R / n<5 / 91d / +11.8% per trade|3 / 67% / +0.76 R / n<5 / 259d / -1.6% per trade|3 / 100% / +0.69 R / n<5 / 105d / +10.5% per trade|

### BTC WT short: cell = n / win / mean net R / 95% CI / median hold
|tf|confirm|opp|opp_stop|2R|3R|trail|
|-|-|-|-|-|-|-|
|4h|none|84 / 50% / -7.19 R / [-12.24,-2.39] / 29d / -12.9% per trade|84 / 18% / -0.34 R / [-0.80,0.27] / 2d / -0.9% per trade|84 / 23% / -0.40 R / [-0.65,-0.11] / 1d / -1.1% per trade|84 / 17% / -0.42 R / [-0.74,-0.11] / 1d / -1.3% per trade|84 / 21% / -0.44 R / [-0.63,-0.23] / 1d / -0.8% per trade|
|4h|backin|84 / 50% / -7.21 R / [-12.16,-2.68] / 29d / -12.9% per trade|84 / 18% / -0.37 R / [-0.82,0.27] / 2d / -0.9% per trade|84 / 23% / -0.40 R / [-0.65,-0.11] / 1d / -1.1% per trade|84 / 17% / -0.42 R / [-0.70,-0.08] / 2d / -1.3% per trade|84 / 21% / -0.47 R / [-0.63,-0.27] / 1d / -0.8% per trade|
|4h|swing|39 / 46% / -0.95 R / [-2.54,0.48] / 28d / -4.9% per trade|39 / 33% / +0.35 R / [-0.34,1.24] / 6d / +1.2% per trade|39 / 36% / +0.05 R / [-0.41,0.51] / 6d / -0.5% per trade|39 / 26% / -0.02 R / [-0.53,0.57] / 9d / -0.8% per trade|39 / 33% / +0.00 R / [-0.22,0.25] / 2d / -0.1% per trade|
|4h|macd|40 / 52% / -6.41 R / [-16.23,0.34] / 29d / -4.5% per trade|40 / 12% / -0.38 R / [-0.89,0.23] / 2d / -1.1% per trade|40 / 30% / -0.16 R / [-0.54,0.28] / 1d / -0.2% per trade|40 / 20% / -0.26 R / [-0.76,0.24] / 1d / -0.6% per trade|40 / 30% / -0.23 R / [-0.54,0.13] / 1d / -0.6% per trade|
|1d|none|15 / 20% / -27.65 R / [-48.74,-9.85] / 79d / -153.3% per trade|15 / 13% / -0.40 R / [-1.03,0.39] / 6d / -0.7% per trade|15 / 33% / -0.03 R / [-0.64,0.76] / 4d / -0.3% per trade|15 / 20% / -0.23 R / [-1.03,0.57] / 5d / -0.7% per trade|15 / 27% / -0.27 R / [-0.74,0.34] / 4d / -1.8% per trade|
|1d|backin|15 / 20% / -27.61 R / [-49.66,-11.06] / 79d / -153.3% per trade|15 / 13% / -0.40 R / [-1.03,0.44] / 6d / -0.7% per trade|15 / 33% / -0.03 R / [-0.63,0.77] / 4d / -0.3% per trade|15 / 20% / -0.23 R / [-1.03,0.57] / 5d / -0.8% per trade|15 / 27% / -0.27 R / [-0.74,0.34] / 4d / -1.8% per trade|
|1d|swing|6 / 33% / -5.05 R / [-11.49,0.29] / 328d / -107.6% per trade|6 / 33% / -0.10 R / [-1.01,0.92] / 22d / -2.9% per trade|6 / 17% / -0.51 R / [-1.01,0.49] / 32d / -15.0% per trade|6 / 17% / -0.50 R / [-1.01,0.51] / 32d / -14.9% per trade|6 / 17% / -0.22 R / [-0.63,0.42] / 10d / -3.5% per trade|
|1d|macd|6 / 17% / -15.20 R / [-34.89,-1.71] / 184d / -112.4% per trade|6 / 17% / -0.26 R / [-1.02,0.97] / 22d / +2.8% per trade|6 / 33% / -0.02 R / [-1.02,0.99] / 28d / +5.0% per trade|6 / 17% / -0.35 R / [-1.02,0.99] / 39d / -1.8% per trade|6 / 0% / -0.28 R / [-0.59,-0.09] / 14d / -1.6% per trade|
|3d|none|6 / 67% / -7.88 R / [-28.95,4.83] / 354d / +5.7% per trade|6 / 17% / -0.47 R / [-1.04,0.64] / 16d / -5.3% per trade|6 / 17% / -0.52 R / [-1.04,0.49] / 16d / -6.1% per trade|6 / 17% / -0.35 R / [-1.04,0.99] / 16d / -3.3% per trade|6 / 17% / -0.58 R / [-1.03,-0.01] / 12d / -7.6% per trade|
|3d|backin|6 / 67% / -8.01 R / [-29.09,4.51] / 354d / +5.1% per trade|6 / 17% / -0.61 R / [-1.04,0.22] / 16d / -5.9% per trade|6 / 17% / -0.52 R / [-1.04,0.49] / 16d / -3.7% per trade|6 / 0% / -1.02 R / [-1.04,-1.01] / 16d / -15.8% per trade|6 / 17% / -0.65 R / [-1.03,-0.22] / 12d / -8.5% per trade|
|3d|swing|2 / 50% / -0.48 R / n<5 / 374d / +5.7% per trade|2 / 0% / -1.00 R / n<5 / 82d / -37.8% per trade|2 / 0% / -1.00 R / n<5 / 82d / -37.8% per trade|2 / 0% / -1.00 R / n<5 / 82d / -37.8% per trade|2 / 50% / -0.07 R / n<5 / 36d / +2.0% per trade|
|3d|macd|4 / 75% / -4.71 R / n<5 / 540d / +14.0% per trade|4 / 25% / -0.51 R / n<5 / 10d / -0.7% per trade|4 / 25% / -0.26 R / n<5 / 10d / +7.2% per trade|4 / 0% / -1.01 R / n<5 / 10d / -16.4% per trade|4 / 25% / -0.76 R / n<5 / 9d / -8.3% per trade|
|1w|none|2 / 50% / +1.36 R / n<5 / 1085d / +10.1% per trade|2 / 50% / +1.69 R / n<5 / 119d / +15.0% per trade|2 / 50% / +0.49 R / n<5 / 10d / +2.8% per trade|2 / 50% / +0.99 R / n<5 / 46d / +7.9% per trade|2 / 50% / +1.03 R / n<5 / 91d / +8.3% per trade|
|1w|backin|2 / 50% / +1.36 R / n<5 / 1085d / +10.1% per trade|2 / 50% / +1.69 R / n<5 / 119d / +15.0% per trade|2 / 50% / +0.49 R / n<5 / 10d / +2.8% per trade|2 / 50% / +0.99 R / n<5 / 46d / +7.9% per trade|2 / 50% / +1.03 R / n<5 / 91d / +8.3% per trade|
|1w|swing|1 / 100% / +0.97 R / n<5 / 217d / +32.7% per trade|1 / 100% / +0.97 R / n<5 / 217d / +32.7% per trade|1 / 100% / +0.60 R / n<5 / 350d / +20.5% per trade|1 / 100% / +0.60 R / n<5 / 350d / +20.5% per trade|1 / 100% / +0.49 R / n<5 / 161d / +16.4% per trade|
|1w|macd|1 / 0% / -1.54 R / n<5 / 1883d / -29.2% per trade|1 / 0% / -1.01 R / n<5 / 0d / -19.0% per trade|1 / 0% / -1.01 R / n<5 / 0d / -19.0% per trade|1 / 0% / -1.01 R / n<5 / 0d / -19.0% per trade|1 / 0% / -1.01 R / n<5 / 0d / -19.0% per trade|

### BTC WT long: cell = n / win / mean net R / 95% CI / median hold
|tf|confirm|opp|opp_stop|2R|3R|trail|
|-|-|-|-|-|-|-|
|4h|none|95 / 56% / +2.36 R / [-0.63,5.93] / 26d / +8.0% per trade|95 / 25% / +1.12 R / [-0.28,3.60] / 2d / +2.0% per trade|95 / 38% / +0.07 R / [-0.22,0.36] / 1d / +0.6% per trade|95 / 28% / +0.07 R / [-0.31,0.45] / 2d / +0.7% per trade|95 / 37% / +0.03 R / [-0.28,0.43] / 1d / +0.2% per trade|
|4h|backin|94 / 56% / +2.40 R / [-0.54,6.04] / 26d / +8.2% per trade|94 / 26% / +1.14 R / [-0.28,3.50] / 2d / +2.1% per trade|94 / 38% / +0.08 R / [-0.23,0.38] / 1d / +0.6% per trade|94 / 28% / +0.04 R / [-0.31,0.39] / 2d / +0.6% per trade|94 / 37% / +0.04 R / [-0.28,0.44] / 1d / +0.3% per trade|
|4h|swing|52 / 54% / +0.17 R / [-1.01,1.44] / 30d / +2.3% per trade|52 / 37% / +0.25 R / [-0.44,1.29] / 8d / +1.0% per trade|52 / 35% / +0.01 R / [-0.33,0.42] / 8d / +0.6% per trade|52 / 21% / -0.18 R / [-0.57,0.28] / 11d / -0.7% per trade|52 / 31% / -0.04 R / [-0.23,0.18] / 2d / -0.2% per trade|
|4h|macd|48 / 60% / +1.37 R / [-1.23,4.35] / 33d / +3.8% per trade|48 / 29% / +1.49 R / [-0.25,4.07] / 4d / +3.0% per trade|48 / 50% / +0.44 R / [0.01,0.88] / 2d / +1.0% per trade|48 / 40% / +0.53 R / [0.02,1.11] / 3d / +1.0% per trade|48 / 42% / +0.80 R / [0.00,1.88] / 1d / +0.9% per trade|
|1d|none|7 / 71% / +5.25 R / [0.66,9.97] / 270d / +33.2% per trade|7 / 0% / -1.02 R / [-1.02,-1.01] / 10d / -8.9% per trade|7 / 0% / -1.02 R / [-1.02,-1.01] / 10d / -8.9% per trade|7 / 0% / -1.02 R / [-1.02,-1.01] / 10d / -8.9% per trade|7 / 14% / -0.53 R / [-0.85,-0.16] / 3d / -4.0% per trade|
|1d|backin|7 / 71% / +5.25 R / [0.71,10.15] / 270d / +33.2% per trade|7 / 0% / -1.02 R / [-1.02,-1.01] / 10d / -8.9% per trade|7 / 0% / -1.02 R / [-1.02,-1.01] / 10d / -8.9% per trade|7 / 0% / -1.02 R / [-1.02,-1.01] / 10d / -8.9% per trade|7 / 14% / -0.53 R / [-0.85,-0.15] / 3d / -4.0% per trade|
|1d|swing|4 / 75% / +2.04 R / n<5 / 299d / +22.4% per trade|4 / 0% / -1.01 R / n<5 / 24d / -18.0% per trade|4 / 0% / -1.01 R / n<5 / 24d / -18.0% per trade|4 / 0% / -1.01 R / n<5 / 24d / -18.0% per trade|4 / 25% / -0.30 R / n<5 / 10d / -4.7% per trade|
|1d|macd|3 / 67% / +3.09 R / n<5 / 266d / +38.5% per trade|3 / 0% / -1.01 R / n<5 / 11d / -11.5% per trade|3 / 0% / -1.01 R / n<5 / 11d / -11.5% per trade|3 / 0% / -1.01 R / n<5 / 11d / -11.5% per trade|3 / 33% / -0.45 R / n<5 / 4d / -5.6% per trade|
|3d|none|4 / 75% / +13.35 R / n<5 / 420d / +146.0% per trade|4 / 25% / -0.37 R / n<5 / 14d / +1.0% per trade|4 / 50% / +0.48 R / n<5 / 9d / +5.9% per trade|4 / 25% / -0.02 R / n<5 / 14d / +6.9% per trade|4 / 50% / -0.30 R / n<5 / 12d / -3.3% per trade|
|3d|backin|4 / 75% / +13.61 R / n<5 / 420d / +146.2% per trade|4 / 50% / +2.77 R / n<5 / 70d / +20.4% per trade|4 / 75% / +1.23 R / n<5 / 30d / +10.6% per trade|4 / 50% / +0.98 R / n<5 / 32d / +13.2% per trade|4 / 75% / +1.21 R / n<5 / 15d / +6.0% per trade|
|3d|swing|2 / 100% / +0.48 R / n<5 / 402d / +15.0% per trade|2 / 100% / +0.48 R / n<5 / 402d / +15.0% per trade|2 / 100% / +2.00 R / n<5 / 268d / +61.5% per trade|2 / 100% / +1.58 R / n<5 / 526d / +49.6% per trade|2 / 50% / +0.45 R / n<5 / 52d / +13.7% per trade|
|3d|macd|3 / 100% / +19.59 R / n<5 / 429d / +201.4% per trade|3 / 67% / +2.19 R / n<5 / 111d / +23.9% per trade|3 / 100% / +1.99 R / n<5 / 36d / +27.7% per trade|3 / 100% / +2.99 R / n<5 / 42d / +41.6% per trade|3 / 67% / +1.49 R / n<5 / 63d / +13.8% per trade|
|1w|none|2 / 100% / +12.11 R / n<5 / 238d / +392.3% per trade|2 / 50% / +10.23 R / n<5 / 172d / +379.9% per trade|2 / 50% / +0.49 R / n<5 / 32d / +32.3% per trade|2 / 50% / +0.99 R / n<5 / 70d / +50.1% per trade|2 / 50% / +9.15 R / n<5 / 206d / +341.3% per trade|
|1w|backin|2 / 100% / +12.11 R / n<5 / 238d / +392.3% per trade|2 / 50% / +10.23 R / n<5 / 172d / +379.9% per trade|2 / 50% / +0.49 R / n<5 / 32d / +32.3% per trade|2 / 50% / +0.99 R / n<5 / 70d / +50.1% per trade|2 / 50% / +9.15 R / n<5 / 206d / +341.3% per trade|
|1w|swing|2 / 50% / +2.54 R / n<5 / 126d / +174.3% per trade|2 / 50% / +2.54 R / n<5 / 126d / +174.3% per trade|2 / 50% / +0.81 R / n<5 / 88d / +60.0% per trade|2 / 50% / +1.31 R / n<5 / 91d / +92.9% per trade|2 / 50% / +2.23 R / n<5 / 161d / +153.9% per trade|
|1w|macd|2 / 100% / +4.86 R / n<5 / 203d / +243.6% per trade|2 / 100% / +4.86 R / n<5 / 203d / +243.6% per trade|2 / 100% / +1.99 R / n<5 / 112d / +66.9% per trade|2 / 100% / +2.99 R / n<5 / 140d / +100.5% per trade|2 / 100% / +4.42 R / n<5 / 238d / +218.1% per trade|

### BTC RSI, confirm none, by phase at signal: cell = n / win / mean net R
|dir|tf|phase|opp|opp_stop|3R|
|-|-|-|-|-|-|
|short|4h|bear|28 / 50% / -11.66|28 / 36% / +1.03|28 / 29% / +0.07|
|short|4h|base|20 / 45% / -3.90|20 / 15% / -0.45|20 / 20% / -0.26|
|short|4h|bull|47 / 45% / -9.87|47 / 15% / +0.02|47 / 34% / +0.28|
|short|1d|bear|3 / 33% / -19.68|3 / 0% / -1.04|3 / 0% / -1.04|
|short|1d|base|2 / 0% / -7.41|2 / 0% / -1.03|2 / 0% / -1.03|
|short|1d|bull|14 / 29% / -14.53|14 / 7% / -0.57|14 / 21% / -0.18|
|short|3d|bear|0|0|0|
|short|3d|base|0|0|0|
|short|3d|bull|7 / 0% / -38.27|7 / 0% / -1.02|7 / 0% / -1.02|
|short|1w|bear|0|0|0|
|short|1w|base|0|0|0|
|short|1w|bull|3 / 67% / +1.15|3 / 33% / +0.79|3 / 33% / +0.32|
|long|4h|bear|30 / 60% / -3.91|30 / 33% / +0.15|30 / 40% / +0.54|
|long|4h|base|25 / 68% / +0.96|25 / 32% / +0.07|25 / 24% / -0.08|
|long|4h|bull|46 / 39% / -1.29|46 / 20% / -0.32|46 / 28% / +0.07|
|long|1d|bear|8 / 62% / -3.04|8 / 12% / -0.68|8 / 38% / +0.47|
|long|1d|base|1 / 100% / +1.70|1 / 0% / -1.01|1 / 0% / -1.01|
|long|1d|bull|8 / 62% / +2.76|8 / 12% / -0.09|8 / 12% / -0.53|
|long|3d|bear|0|0|0|
|long|3d|base|1 / 0% / -7.34|1 / 0% / -1.03|1 / 0% / -1.03|
|long|3d|bull|1 / 0% / -2.18|1 / 0% / -1.01|1 / 0% / -1.01|
|long|1w|bear|1 / 100% / +2.74|1 / 0% / -1.02|1 / 0% / -1.02|
|long|1w|base|1 / 100% / +1.42|1 / 0% / -1.01|1 / 100% / +2.99|
|long|1w|bull|1 / 100% / +3.30|1 / 100% / +3.30|1 / 100% / +2.99|

### BTC RSI, confirm none: DEV (to 2023) vs VALIDATION (2024+)
|dir|tf|exit|DEV n|DEV mean R|VAL n|VAL mean R|
|-|-|-|-|-|-|-|
|short|4h|opp|62|-16.97|37|-0.04|
|short|4h|opp_stop|62|-0.35|37|+1.03|
|short|4h|3R|62|+0.10|37|+0.21|
|short|1d|opp|13|-20.00|6|-2.87|
|short|1d|opp_stop|13|-0.54|6|-1.03|
|short|1d|3R|13|-0.42|6|-0.37|
|short|3d|opp|5|-50.40|2|-7.94|
|short|3d|opp_stop|5|-1.02|2|-1.01|
|short|3d|3R|5|-1.02|2|-1.01|
|short|1w|opp|1|+2.25|2|+0.59|
|short|1w|opp_stop|1|-1.01|2|+1.69|
|short|1w|3R|1|-1.01|2|+0.99|
|long|4h|opp|59|-1.56|46|+0.67|
|long|4h|opp_stop|59|+0.07|46|-0.37|
|long|4h|3R|59|+0.44|46|-0.28|
|long|1d|opp|10|+0.54|7|-0.85|
|long|1d|opp_stop|10|-0.35|7|-0.53|
|long|1d|3R|10|+0.17|7|-0.45|
|long|3d|opp|0|-|2|-4.76|
|long|3d|opp_stop|0|-|2|-1.02|
|long|3d|3R|0|-|2|-1.02|
|long|1w|opp|1|+1.42|2|+3.02|
|long|1w|opp_stop|1|-1.01|2|+1.14|
|long|1w|3R|1|+2.99|2|+0.99|

### Pooled BTC ETH SOL BNB XRP, RSI, confirm none: n / win / mean net R / CI / hold
|dir|tf|opp|opp_stop|3R|trail|
|-|-|-|-|-|-|
|short|4h|423 / 52% / -9.23 R / [-13.00,-5.63] / 26d / -25.9% per trade|423 / 20% / -0.08 R / [-0.35,0.22] / 2d / -0.8% per trade|423 / 27% / +0.01 R / [-0.15,0.19] / 2d / -0.2% per trade|423 / 36% / -0.02 R / [-0.16,0.15] / 1d / -0.3% per trade|
|short|1d|74 / 39% / -19.57 R / [-35.45,-7.60] / 196d / -104.2% per trade|74 / 18% / -0.23 R / [-0.67,0.31] / 9d / -1.1% per trade|74 / 26% / -0.00 R / [-0.38,0.41] / 8d / -0.3% per trade|74 / 34% / +0.04 R / [-0.32,0.50] / 7d / +0.0% per trade|
|short|3d|24 / 46% / -23.72 R / [-43.75,-6.98] / 423d / -193.7% per trade|24 / 17% / -0.55 R / [-0.93,-0.08] / 15d / -6.7% per trade|24 / 12% / -0.59 R / [-1.01,-0.09] / 15d / -7.0% per trade|24 / 33% / -0.31 R / [-0.65,0.09] / 12d / -2.4% per trade|
|short|1w|12 / 58% / -9.09 R / [-26.72,1.02] / 500d / -175.1% per trade|12 / 33% / -0.03 R / [-0.82,0.87] / 98d / -3.1% per trade|12 / 25% / -0.29 R / [-1.01,0.57] / 74d / -6.6% per trade|12 / 42% / -0.09 R / [-0.70,0.62] / 77d / -4.0% per trade|
|long|4h|430 / 56% / +0.50 R / [-0.42,1.49] / 25d / +5.0% per trade|430 / 23% / +0.19 R / [-0.11,0.54] / 3d / +1.2% per trade|430 / 28% / +0.08 R / [-0.09,0.24] / 2d / +0.2% per trade|430 / 38% / +0.05 R / [-0.08,0.19] / 1d / +0.4% per trade|
|long|1d|60 / 58% / +4.01 R / [0.19,8.57] / 166d / +20.2% per trade|60 / 15% / +0.54 R / [-0.59,2.13] / 9d / +2.8% per trade|60 / 27% / +0.04 R / [-0.36,0.51] / 8d / +2.2% per trade|60 / 33% / +0.23 R / [-0.32,0.95] / 4d / +2.5% per trade|
|long|3d|16 / 69% / +12.92 R / [3.36,24.97] / 544d / +129.0% per trade|16 / 31% / +6.31 R / [0.01,15.92] / 52d / +52.6% per trade|16 / 62% / +1.48 R / [0.48,2.47] / 22d / +9.7% per trade|16 / 75% / +1.73 R / [0.24,3.83] / 26d / +7.1% per trade|
|long|1w|7 / 100% / +2.83 R / [1.77,4.16] / 175d / +65.4% per trade|7 / 71% / +1.94 R / [0.26,3.79] / 175d / +56.4% per trade|7 / 71% / +1.85 R / [0.14,2.99] / 56d / +42.8% per trade|7 / 71% / +8.57 R / [0.11,24.37] / 147d / +255.6% per trade|

### Placebo: random entries, same n, same exit (100 draws), BTC RSI confirm none
|dir|tf|exit|n|real mean R|placebo mean R|
|-|-|-|-|-|-|
|short|4h|opp|99|-10.64|-6.60|
|short|4h|opp_stop|99|+0.17|-0.17|
|short|4h|3R|99|+0.14|-0.09|
|short|1d|opp|19|-14.59|-14.38|
|short|1d|opp_stop|19|-0.70|-0.07|
|short|1d|3R|19|-0.40|-0.06|
|short|3d|opp|7|-38.27|-95.75|
|short|3d|opp_stop|7|-1.02|-0.94|
|short|3d|3R|7|-1.02|-0.33|
|short|1w|opp|3|+1.15|-16.39|
|short|1w|opp_stop|3|+0.79|-0.45|
|short|1w|3R|3|+0.32|-0.43|
|long|4h|opp|105|-0.58|+1.69|
|long|4h|opp_stop|105|-0.12|+0.85|
|long|4h|3R|105|+0.12|+0.02|
|long|1d|opp|17|-0.03|+1.99|
|long|1d|opp_stop|17|-0.42|+0.29|
|long|1d|3R|17|-0.09|+0.14|
|long|3d|opp|2|-4.76|+9.78|
|long|3d|opp_stop|2|-1.02|+2.57|
|long|3d|3R|2|-1.02|+0.49|
|long|1w|opp|3|+2.49|+12.15|
|long|1w|opp_stop|3|+0.43|+4.84|
|long|1w|3R|3|+1.66|+0.35|

### BTC full-cycle equity (start 1.0; 12 bp per trade; flips on opposite divergence, confirm none)
|osc|tf|mode|trades|final x|max DD (bar close)|buy&hold x same window|
|-|-|-|-|-|-|-|
|rsi|4h|flip|105|0.01|-100%|16.01|
|rsi|4h|long_only|52|0.46|-88%|9.49|
|rsi|4h|short_only|53|0.03|-99%|16.01|
|rsi|1d|flip|18|0.08|-94%|18.44|
|rsi|1d|long_only|9|1.21|-63%|18.44|
|rsi|1d|short_only|9|0.07|-94%|18.76|
|rsi|3d|flip|1|0.06|-97%|9.50|
|rsi|3d|long_only|0|0.72|-51%|0.72|
|rsi|3d|short_only|1|0.08|-95%|9.50|
|rsi|1w|flip|5|4.53|-75%|1.47|
|rsi|1w|long_only|2|2.58|-75%|2.18|
|rsi|1w|short_only|3|1.76|-41%|1.47|
|wt|4h|flip|91|1.27|-76%|16.01|
|wt|4h|long_only|45|4.52|-69%|9.49|
|wt|4h|short_only|46|0.28|-88%|16.01|
|wt|1d|flip|9|0.49|-96%|10.60|
|wt|1d|long_only|4|2.28|-50%|20.81|
|wt|1d|short_only|5|0.21|-94%|10.60|
|wt|3d|flip|5|18.36|-64%|9.50|
|wt|3d|long_only|2|13.22|-51%|10.15|
|wt|3d|short_only|3|1.39|-64%|9.50|
|wt|1w|flip|2|8.23|-87%|12.73|
|wt|1w|long_only|1|10.23|-21%|12.73|
|wt|1w|short_only|1|0.80|-87%|1.47|

### BTC RSI equity at year end (x), by mode
|tf|mode|2018|2019|2020|2021|2022|2023|2024|2025|2026|
|-|-|-|-|-|-|-|-|-|-|-|
|1d|flip|0.96|0.52|0.31|0.31|0.17|0.27|0.13|0.10|0.08|
|1d|long_only|0.96|0.98|1.53|1.93|0.85|1.71|1.78|1.48|1.21|
|1d|short_only|1.00|0.53|0.20|0.16|0.20|0.16|0.07|0.07|0.07|
|3d|flip|1.00|1.12|0.24|0.17|0.47|0.17|0.08|0.07|0.06|
|3d|long_only|1.00|1.00|1.00|1.00|1.00|1.00|1.00|0.86|0.72|
|3d|short_only|1.00|1.12|0.24|0.17|0.47|0.17|0.08|0.08|0.08|
|1w|flip|1.00|1.00|1.00|2.05|0.72|1.83|1.82|2.65|4.53|
|1w|long_only|1.00|1.00|1.00|1.38|0.49|1.23|1.88|2.18|2.58|
|1w|short_only|1.00|1.00|1.00|1.49|1.49|1.49|0.97|1.22|1.76|

### Forward return after signal (entry = next open; close after N bars; profit sign for signal direction); pooled 5 symbols, RSI, confirm none, high outside band
|dir|tf|n signals|+5 bars mean (hit%)|+20 bars|+60 bars|baseline all bars +5 / +20 / +60|
|-|-|-|-|-|-|-|
|short|4h|435|-0.2% (50%) n=435|-1.3% (48%) n=435|-3.4% (47%) n=435|-0.2% / -0.7% / -2.2%|
|short|1d|74|-1.7% (57%) n=74|-9.6% (39%) n=74|-34.4% (38%) n=72|-1.0% / -4.5% / -16.4%|
|short|3d|24|-2.1% (38%) n=24|-10.3% (50%) n=22|-144.8% (48%) n=21|-2.8% / -14.0% / -54.3%|
|short|1w|12|-1.4% (58%) n=12|-25.3% (67%) n=12|-137.2% (60%) n=10|-7.5% / -38.7% / -186.7%|
|long|4h|432|0.5% (54%) n=432|0.5% (54%) n=428|1.8% (52%) n=425|0.2% / 0.7% / 2.2%|
|long|1d|60|-1.7% (40%) n=60|0.9% (42%) n=60|12.5% (50%) n=58|1.0% / 4.5% / 16.4%|
|long|3d|16|5.6% (69%) n=16|11.3% (50%) n=16|16.5% (56%) n=16|2.8% / 14.0% / 54.3%|
|long|1w|7|18.5% (86%) n=7|80.4% (100%) n=5|344.7% (80%) n=5|7.5% / 38.7% / 186.7%|

## Every BTC RSI signal on 1D / 3D / 1W since 2017 (confirm none; R net of 12 bp; WT list in the CSV)

R full-cycle = ride to the next opposite divergence, no stop, in units of the pivot-stop distance (big negatives mean price went far past a tight stop). R pivot-stop = same exit with the stop at the pivot. 'open' = no opposite signal yet, marked to the last close.

| TF | confirmed | dir | pivot | pivot px | RSI prev>now | phase | R full-cycle | R pivot-stop | R 2R | R 3R | R trail | hold d | open |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
|1d|2018-11-28|long|2018-11-25|3653|10.5>17.8|bear|-0.32|-1.02|+1.98|-1.02|-1.02|91|False|
|1d|2018-12-11|long|2018-12-08|3222|17.8>23.8|bear|+1.75|-1.02|-1.02|-1.02|-1.02|78|False|
|1d|2019-02-27|short|2019-02-24|4198|57.2>50.8|bear|-8.70|-1.01|-1.01|-1.01|-0.14|297|False|
|1d|2019-03-24|short|2019-03-21|4069|63.3>58.0|bear|-50.34|-1.08|-1.08|-1.08|+0.83|272|False|
|1d|2019-04-26|short|2019-04-23|5600|84.8>75.2|base|-5.20|-1.02|-1.02|-1.02|-1.02|239|False|
|1d|2019-05-07|short|2019-05-04|5900|75.2>75.0|base|-9.63|-1.05|-1.05|-1.05|-1.05|228|False|
|1d|2019-12-21|long|2019-12-18|6435|36.0>47.5|bear|+5.31|-1.01|+1.99|+2.99|+0.01|228|False|
|1d|2020-08-05|short|2020-08-02|12123|82.7>65.9|bull|-27.38|-1.01|-1.01|-1.01|-1.01|310|False|
|1d|2020-08-20|short|2020-08-17|12468|70.7>70.4|bull|-34.95|-1.02|+1.98|-1.02|+0.04|295|False|
|1d|2020-10-31|short|2020-10-28|13859|79.6>72.5|bull|-77.27|-1.05|-1.05|-1.05|-1.05|223|False|
|1d|2020-12-04|short|2020-12-01|19888|74.4>62.1|bull|-37.11|-1.05|+1.95|+2.95|+1.27|189|False|
|1d|2021-06-11|long|2021-06-08|31000|34.4>34.4|base|+1.70|-1.01|-1.01|-1.01|-0.21|91|False|
|1d|2021-09-10|short|2021-09-07|52920|60.2>48.1|bull|+1.32|-1.01|-1.01|-1.01|-0.27|236|False|
|1d|2021-11-13|short|2021-11-10|69000|60.9>59.3|bull|+5.40|+5.40|+1.98|+2.98|+2.71|172|False|
|1d|2022-05-04|long|2022-05-01|37386|36.6>41.7|bear|-38.36|-1.13|+1.87|+2.87|-1.13|291|False|
|1d|2022-09-10|long|2022-09-07|18511|29.2>35.9|bear|+1.14|-1.01|-1.01|-1.01|-0.43|162|False|
|1d|2022-10-16|long|2022-10-13|18190|43.3>47.3|bear|+6.31|-1.03|+1.97|-1.03|+0.27|126|False|
|1d|2023-02-19|short|2023-02-16|25250|60.1>60.0|bull|-3.64|-1.05|-1.05|-1.05|-1.05|98|False|
|1d|2023-05-28|long|2023-05-25|25872|40.1>40.2|bull|+9.90|-1.03|-1.03|-1.03|-0.07|174|False|
|1d|2023-06-18|long|2023-06-15|24800|40.9>41.2|bull|+5.86|+5.86|+1.98|+2.98|+2.10|153|False|
|1d|2023-08-04|long|2023-08-01|28586|42.2>51.1|bull|+12.15|-1.06|-1.06|-1.06|+0.12|106|False|
|1d|2023-11-18|short|2023-11-15|37980|82.7>72.7|bull|-5.55|-1.03|-1.03|-1.03|-0.61|49|False|
|1d|2023-11-27|short|2023-11-24|38414|72.7>61.6|bull|-6.98|-1.05|-1.05|-1.05|-1.05|40|False|
|1d|2024-01-06|long|2024-01-03|40750|50.1>51.8|bull|-0.40|-0.40|-1.02|-1.02|-0.42|8|False|
|1d|2024-01-14|short|2024-01-11|48969|63.4>62.2|bull|-3.62|-1.01|-1.01|-1.01|-0.08|99|False|
|1d|2024-03-08|short|2024-03-05|69000|87.3>69.4|bull|+0.83|-1.04|-1.04|-1.04|-1.04|45|False|
|1d|2024-04-22|long|2024-04-19|59600|42.2>44.8|bull|+0.87|-1.01|-1.01|-1.01|+0.26|49|False|
|1d|2024-06-10|short|2024-06-07|71997|58.9>55.4|bull|-10.66|-1.04|+1.96|+2.96|+3.73|216|False|
|1d|2024-12-08|short|2024-12-05|104088|68.6>62.7|bull|+1.20|-1.03|-1.03|-1.03|-0.33|35|False|
|1d|2025-01-12|long|2025-01-09|91204|41.6>41.9|bull|+2.59|-1.03|-1.03|-1.03|-1.03|123|False|
|1d|2025-05-15|short|2025-05-12|105819|70.2>69.4|bull|-5.01|-1.05|-1.05|-1.05|-1.05|151|False|
|1d|2025-10-13|long|2025-10-10|102000|38.4>41.8|bull|-2.91|-1.01|-1.01|-1.01|-0.39|194|False|
|1d|2026-04-25|short|2026-04-22|79473|67.4>65.3|bear|+0.01|-1.05|-1.05|-1.05|-1.05|31|False|
|1d|2026-05-26|long|2026-05-23|74290|45.1>45.7|bear|-1.96|-1.03|-1.03|-1.03|-1.03|170|True|
|1d|2026-07-04|long|2026-07-01|57800|30.5>37.2|bear|+1.84|+1.84|+1.98|+2.98|+0.31|131|True|
|1d|2026-10-18|long|2026-10-15|79800|47.0>48.9|bull|-5.99|-1.06|+1.94|-1.06|-0.10|25|True|
|1w|2021-03-08|short|2021-02-15|58353|94.8>88.3|bull|+2.25|-1.01|-1.01|-1.01|-1.01|126|False|
|1w|2021-07-12|long|2021-06-21|28805|44.1>44.6|base|+1.42|-1.01|+1.99|+2.99|+2.77|931|False|
|1w|2024-01-29|short|2024-01-08|48969|83.2>67.2|bull|-3.21|-1.01|-1.01|-1.01|-1.01|210|False|
|1w|2024-08-26|long|2024-08-05|49000|45.8>48.5|bull|+3.30|+3.30|+1.99|+2.99|+1.08|427|False|
|1w|2025-10-27|short|2025-10-06|126200|63.6>55.4|bull|+4.39|+4.39|+1.99|+2.99|+3.07|238|False|
|1w|2026-06-22|long|2026-06-01|59131|31.8>34.2|bear|+2.74|-1.02|-1.02|-1.02|-1.02|133|True|
|3d|2019-06-07|short|2019-05-29|9074|89.3>80.0|bull|-73.43|-1.01|-1.01|-1.01|-1.01|2055|False|
|3d|2021-03-01|short|2021-02-20|58353|92.2>77.9|bull|-4.33|-1.00|-1.00|-1.00|-1.00|1422|False|
|3d|2021-03-22|short|2021-03-13|61844|77.9>67.5|bull|-10.01|-1.02|-1.02|-1.02|-1.02|1401|False|
|3d|2023-03-30|short|2023-03-21|28868|76.2>71.0|bull|-142.35|-1.07|-1.07|-1.07|-1.07|663|False|
|3d|2023-12-16|short|2023-12-07|44700|81.1>81.0|bull|-21.88|-1.02|-1.02|-1.02|-1.02|402|False|
|3d|2024-01-18|short|2024-01-09|48969|70.1>69.8|bull|-9.61|-1.01|-1.01|-1.01|-0.09|369|False|
|3d|2024-06-16|short|2024-06-07|71997|60.6>59.4|bull|-6.26|-1.01|+1.99|-1.01|-0.35|219|False|
|3d|2025-01-21|long|2025-01-12|89257|56.5>58.8|bull|-2.18|-1.01|-1.01|-1.01|-0.36|657|True|
|3d|2025-10-18|long|2025-10-09|102000|44.5>45.4|base|-7.34|-1.03|+1.97|-1.03|+0.78|387|True|

## BTC now (descriptive levels and states, no advice)

Last bar 2026-11-13: BTC 68,954 (low of the forming bar 67,568; the 67,468 in the brief reads 67,568 in Binance spot data). 200-week SMA 68,001, so price sits just above it. Cycle low in this data: 57,800 (daily 2026-07-01, weekly bar of 06-29); the current low is 17% above it, so a move to roughly 58-62k would be the retest-of-the-low case, while 67-69k is the first test of the 200-week SMA. Phase label by the study rule: base (not a clean bull or bear by the SMA200 test). Six red weekly bars since the 2026-10-05 open of 86,530.

| TF | Close | RSI at the new low | WaveTrend | Lower band | Bullish divergence building? |
|-|-|-|-|-|-|
| 4H | 68,954 | 16.7 (prior low 41.0) | -84.6 (prior -52.5) | 67,704 | No: new low 67,568 with lower RSI and lower WT, low outside the band |
| 1D (11-13, forming) | 68,954 | 25.4 (prior pivot low 34.4) | -74.1 (prior -51.2) | 70,517 | No: lower low with lower RSI and WT, low outside the band |
| 3D (forming) | 68,954 | 32.1 (prior 59.2) | -33.7 (prior +41.8) | 71,747 | No: momentum making new lows with price |
| 1W (forming) | 68,954 | 41.7 (prior 58.7) | 9.3 (prior 13.9) | 57,819 | No on the forming bar. On closed bars only (to 11-02) WT showed a lower low with a higher WT, but the low was inside the band, so it is not the study signal |

What it would take: price makes a lower low while RSI/WT print above the table values (1D RSI above 25.4, 4H above 16.7). If the low extends to the 57.8k area, the bar to beat on 1D is RSI 37.2 (the 2026-07-01 pivot; 30.5 at the low before it) and on 1W RSI 34.2 (pivot week 2026-06-01; 31.8 before). Confirmation levels (study definitions): close back above the lower band (4H 67,704; 1D 70,517; 3D 71,747); close above the last swing high between the two lows (4H 74,811; 1D 81,196; 3D 84,898; 1W 87,396); 20-bar mean (4H 72,030; 1D 76,744; 3D 80,657; 1W 74,095); MACD above its signal (MACD minus signal now: 4H -318, 1D -679, 3D -1,830, 1W -156). Last confirmed bullish RSI divergence outside the lower band: 4H pivot 2026-11-10 (72,727); 1D 2026-10-15 (79,800, since undercut); 3D 2025-10 (102,000); 1W 2026-06-01 (59,131).

Raw per-timeframe output: btc_now.md.
