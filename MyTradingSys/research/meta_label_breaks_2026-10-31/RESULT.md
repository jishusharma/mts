# RESULT: can other layers sort the break trades into winners and losers, and does getting out early help? (2026-10-31, JIS-NB)

Card `meta-label-break-events-layer-features`. Rules frozen in `PRE_REG.md` (commit a991d61ff) before any outcome was read. DEV only
(2022-01..2024-06); VALIDATION was not read because no timeframe passed DEV; HOLDOUT never opened. Cost 0.10 % round trip
(`fees.BINANCE_TAKER` both legs), no slippage. Full tables: `output.md` (from `report.py`); raw numbers `F:/MTS/runs/meta_label_breaks/dev.json`.

## Answer
- **Filter before entry: no pass.** 15m FAIL, 4h FAIL, 1h INCONCLUSIVE. The 1h model's best third makes +0.063 % per trade after fees
  (CI -0.048..+0.179), positive in both halves (+0.129 % / +0.035 %), and beats 98 % of the label shuffles (p 0.020), but the Holm-adjusted
  p is 0.060 and the CI includes zero. A 1h lift has to be about 0.16 % to be seen with 360 trades per third; the measured lift is 0.096 %.
- **Exit early when not in profit: no gain anywhere.** No difference at 15m or 1h. At 4h it is +0.07..+0.09 % per trade, but the CI includes zero
  and the trades still lose overall.
- **Why early exit cannot work here:** after one bar, 27-28 % of the trades that end as winners are still under water, and 62-67 % of the
  losers are. A "not in profit yet" rule closes about half of all trades and takes a quarter of the winners with them.

## Meta-label (DEV, out of fold, 6 purged time blocks, cut from the training fold)
| TF | trades | all trades net % | best third: n | gross % | net % | 95 % CI | worst third net % | placebo p | Holm p | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 15m | 4114 | -0.094 | 1379 | +0.020 | -0.080 | -0.121..-0.036 | -0.108 | 0.090 | 0.129 | FAIL |
| 1h | 1078 | -0.033 | 360 | +0.163 | +0.063 | -0.048..+0.179 | -0.101 | 0.020 | 0.060 | INCONCLUSIVE |
| 4h | 417 | -0.153 | 145 | +0.197 | +0.097 | -0.210..+0.403 | -0.223 | 0.065 | 0.129 | FAIL |

BH-FDR beside Holm: 1h 0.060, 15m and 4h 0.090. The 1h best third has gross +0.163 % against a 0.10 % fee, so this is a direction lift,
not "fewer, larger trades".

## Early exit (DEV, all trades; exit at the close of bar k if not in profit, else hold 4 bars)
| TF | k | hold net % | early-exit net % | difference | diff 95 % CI | winners under water at k | losers under water at k | verdict |
|---|---|---|---|---|---|---|---|---|
| 15m | 1 | -0.094 | -0.101 | -0.007 | -0.016..+0.002 | 27 % | 62 % | no difference |
| 15m | 2 | -0.094 | -0.097 | -0.004 | -0.012..+0.005 | 18 % | 66 % | no difference |
| 1h | 1 | -0.033 | -0.062 | -0.029 | -0.066..+0.007 | 28 % | 65 % | no difference |
| 1h | 2 | -0.033 | -0.031 | +0.003 | -0.023..+0.031 | 17 % | 69 % | no difference |
| 4h | 1 | -0.154 | -0.065 | +0.089 | -0.019..+0.211 | 28 % | 67 % | no difference |
| 4h | 2 | -0.154 | -0.081 | +0.072 | -0.017..+0.165 | 20 % | 71 % | no difference |

## What the 1h feature table shows (descriptive, no verdict; net % per trade in the feature's DEV thirds, n about 360 each)
- Daily trend with the trade (trend_d): low third -0.103, high third +0.041.
- 4h BBWP (volatility building): low third -0.087, high third +0.009.
- Taker flow against the trade at entry (flow_e): low third +0.072, high third -0.112. Entering when the last 5 bars' aggressive flow ran
  the other way did better.
- Reclaim trades (class R, trading back inside the level): +0.037 (n 229); wick-sweep fades (W1): -0.068 (n 641).
None of these is a test; each is one cut of 15 on the same trades.

## Deviations and limits
- The daily SMA200 needs 200 days, so DEV trades before about 2022-07-19 have no trend_d and were dropped (15m 1123, 1h 300, 4h 107 trades).
  PRE_REG did not say how missing values are handled; the "2022" half is effectively 2022-07..12.
- `move_e` thirds are lopsided (all W1 trades are 0 by definition); the binary rows in `output.md` show value 0 / value 1 under the first
  two third columns.
- Funding: NOT RUN. Corrected 2026-10-31: it IS on disk (`F:/MTS/Dumps/backtest/raw/fundingRate`, 81 files; I looked only under
  `F:/MTS/data`). A 4-bar hold crosses at most one 8-hourly funding stamp at 15m/1h, so the effect is small, but it is not in these numbers. No slippage. Exit at the bar close (not the next open).

## Next (card filed)
The 1h result is the one lead. The honest next check is fresh data, not VALIDATION: refit the same frozen model on all DEV and score
2019-2021 1h break events, which no part of this study has seen. That 1m data is not on JIS-NB (`F:/MTS/data/tom_raw/klines` starts
2022-01). Card `meta-label-1h-dev-ext-check`.

## Follow-up 2026-10-31: Malkan divergence at entry and as exit (EXPLORATORY, DEV, `explore_div.py`, tables in `explore_div_output.md`)
Operator ask: plan exits from divergences (RSI regular, reverse PRD/NRD, CVD), on the trade timeframe and the next lower one, and see
whether divergences separate winners from losers. Malkan settings SOURCED from `backtest/layers/rsi/params/malkan_divergence_default.json`;
look-back 10 bars, max hold 24/24/12 bars and CVD as a stand-in for RSI are OURS. No pre-registration, so no verdict.
- Exit on the first divergence against the trade: no better than simply holding longer. 1h: fixed 4 bars -0.053 %, fixed 24 bars -0.062 %,
  best divergence exit (CVD, lower TF) -0.042 % [-0.148, +0.066]. 4h: fixed 4 -0.157 %, fixed 12 -0.013 %, CVD lower TF +0.029 %
  [-0.187, +0.242]. The lower-TF CVD exit cuts the hold to about 6 bars and leans less on the best 5 % (1h -0.248 % without them vs
  -0.413 % for the fixed 24 bars).
- Divergence at entry: about 66 cells, most under 100 trades, so large means are expected by chance. One pattern holds in all six
  timeframe x side splits: a Malkan REVERSE divergence in the trade's direction (PRD for a long, NRD for a short) on the next lower
  timeframe, known in the last 10 bars, does better than trades without it (15m -0.085 / -0.069 vs -0.105 %; 1h +0.121 (n 65) / +0.015
  (n 58) vs about -0.06 %; 4h +0.493 (n 36) / +0.322 (n 32) vs about -0.20 %). This is a lead to freeze, not a result.
- Next: card `div-reverse-lower-tf-confirm-2020-2021`, the frozen rule run once on 2020-2021 (data on disk), never seen by this look.
