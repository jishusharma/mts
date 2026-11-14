# PRE_REG nk4-hilega-milega-recon-1114 (written before any outcome)

Rule: NK Hilega Milega (cmH38Uo4sYM). NK never gives the formula; the reconstruction is OURS.

## Parameters (S = SOURCED from NK EXTRACT, O = OURS)
| Param | Value | Label |
|---|---|---|
| HM RSI | RSI(9) on close, Wilder | O (published reconstruction) |
| HM fast line | EMA(3) of RSI | O |
| HM slow line | WMA(21) of RSI | O |
| Buy state | RSI > EMA3 and RSI > WMA21 and EMA3 > WMA21; sell = mirror | O |
| Timeframes | 5m, 10m, 15m | S |
| Confirm | 15m RSI(14) <= 30 (long) / >= 70 (short) on any of last 3 completed 15m bars; 5m, 10m and 15m HM states all agree with direction | S zones 30/70 and RSI14, 3-bar lookback O |
| Flip | state becomes buy (sell) on a completed signal-tf bar; entry at next 5m open | O |
| Stop | S = max(1.5 x ATR14(signal tf), 0.5% of entry) (min stop floor against fee drag) | O |
| Exit | first of: stop (intrabar, stop wins ties), HM state of the signal tf no longer buy/sell (exit next 5m open after that bar's close), cap 48 signal-tf bars | O |
| Costs | 12 bp round trip taker (primary); 6 bp maker-entry row (cost-only, fill risk not modelled) | task |
| Fee in R | reported = cost_frac * entry / S, median per row | task |

## Data
Binance spot USDT 5m, data.binance.vision bulk zips, 20 coins (BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL EOS), from 2019 where listed. 10m/15m built from 5m on UTC-aligned buckets (complete buckets only). Higher-tf values used only after their bar close.
DEV to 2023-12-31, VALIDATION from 2024-01-01 (by entry time). Gates only on VALIDATION; DEV reported.

## Context (operator order)
Daily phase for day D from data to prior day close: MA20 slope = MA20[D-1]/MA20[D-6]-1; Wilder ADX(14), DI+/DI-. UP: ADX>=20, DI+>DI-, slope>0. DOWN: ADX>=20, DI->DI+, slope<0. Else RANGE.
Matched (primary) direction: long in UP, short in DOWN, both ways in RANGE (buy flip long, sell flip short). Control: mismatched direction (short in UP, long in DOWN). Regime mix reported.
Regime: none beyond the daily phase label; the regime mix is reported only.
Phase: daily UP/DOWN/RANGE from ADX(14), DI and MA20 slope; long in UP, short in DOWN, both ways in RANGE; mismatched direction = control rows.
Session: none, because 5m/10m/15m signals run 24h with no hour filter.
Entry: Hilega Milega state flips to buy/sell on a completed signal-tf bar (confirmed rows also need 15m RSI14 <= 30 / >= 70 and 5m/10m/15m agreement); entry at the next 5m open.
(Context lines restated at ship 2026-11-14 from this file and the study code, after the run; no rule was changed.)

## Rows
For tf in {5m,10m,15m}: filter in {raw (control, no RSI/agree filter), confirmed}; cost in {12bp, 6bp}; set in {matched, mismatched control}. 24 rows. PASS is judged on matched rows at 12 bp (6 rows: 3 confirmed, 3 raw-control reported but also gated; raw is a control and cannot be the headline).

## Gates for PASS (VALIDATION, matched row)
n >= 100; mean net R > 0; bootstrap 95% CI lower > 0 per trade and per day cluster (2000 resamples, seed 7); placebo p < 0.05 (matched random entries: same coin, same direction, same phase, VAL period, same stop rule, hold = the real trade's held bars, 300 draws; trade set subsampled to 20000 if larger, seed 11); survives BH (q 0.05) across all 24 rows using one-sided day-cluster bootstrap p; mean net R > 0 after removing the best 5 days (by sum R).

## Tests
test_study.py: look-ahead variant (env STUDY_BUG=1 lets the signal see the signal bar's next close) must change results and a planted-edge check must fail under it; real version passes.
