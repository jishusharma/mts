# PRE-REGISTRATION: published rule-based strategies on BTCUSDT perp (frozen before any outcome)

Thread task 2026-10-13 (JIS-NUC). Question: does any simple, published, rule-based strategy survive 0.1 % per side fees +
funding on a frozen holdout, after placebo and multiple-testing correction? Everything below is fixed before `run_pub.py` is run.

## Data and windows
- BTCUSDT USD-M perp, Binance archive 1h klines 2020-01..2026-09 (resampled to 4h, 1d, UTC), 8h funding rates. Path: Dumps/backtest/raw_1h, raw_fund.
- 2020 is warm-up only. DEV 2021-01-01..2023-06-30. VAL 2023-07-01..2024-06-30 (one look, only for DEV advancers).
  HOLD 2024-07-01..2025-06-30 (one look, only for VAL advancers).
- The project's sealed HOLDOUT 2025-07-01..2026-09-30 (volume study, A7: opening needs an operator decision) is NOT touched; the loader
  refuses it. 2024-07..2025-06 was used by 4 frozen volume tests only; none of these strategies.
- No second market: no ETH/NQ/FDAX bar data on disk for the same timeframes. Stated, not hidden.

## Execution model
Signal on bar close t, position held over bar t+1 at its open. Fee 0.10 % per side on |change in position| (coordinator figure; the
repo's Binance taker is 0.05 %, reported as sensitivity). Funding: position x sum of settled rates inside the bar (long pays positive).
No slippage beyond the fee. Williams breakout fills at the trigger, exits at bar close; if both triggers hit in one bar, no trade.

## Variants (62, none tuned; published defaults only)
- TSMOM (Moskowitz-Ooi-Pedersen 2012): daily, lookback 30/90/180/365 d; long-short unit, long-flat unit, long-short vol-scaled
  (40 % target, EWMA com=60 d, cap 3x). 12.
- Donchian / Turtle (Dennis/Faith; Lukac-Brorsen-Irwin 1988): entry/exit 20/10 and 55/20, close-based, long-short and long-flat,
  on 1d and 4h. 8. (System-1 skip-after-winner rule not implemented.)
- Moving average: price>SMA 50/100/200 (Faber 2007; BLL 1992) long-flat and long-short; SMA50/200 cross LF, LS; price>SMA7 (Detzel et al 2021
  PMA1 construct) LF, LS. 10.
- Mean reversion (Connors-Alvarez 2008; Pagonidis IBS): RSI(2) <10 / <5 long above SMA200, exit close>SMA5; long-short mirrored; Double-7
  long and long-short; IBS<0.2 long and long-short (IBS>0.8 short); RSI(2)<10 on 4h LF and LS. 10.
- Volatility breakout: Williams k=0.5 on 1d LF, 1d LS, 4h LS; Bollinger(20,2) close breakout 1d LF, LS. 5.
- Calendar: long on each weekday (Caporale-Plastun 2019: Monday) 7; turn-of-month (Lakonishok-Smidt 1988: last day through day 3) 1;
  session blocks long 00-08, 08-16, 16-24 UTC (exploratory, no published rule) 3. 11.
- Funding / carry: delta-neutral carry always-on, carry switched on trailing-3-settlement funding>0 (Schmeling-Schrimpf-Todorov 2023;
  costs 4 legs, basis and margin risk NOT modelled); directional funding contrarian and momentum (exploratory) on 1d. 4.
- Volatility targeting of long BTC (Moreira-Muir 2017; 40 % target, 20 d vol, cap 1x and 2x). 2.
Benchmarks reported, not tested: buy-and-hold.

## Statistics and gates
- Effect: mean net return per bar, annualised %, Sharpe, trades, max drawdown, delta vs buy-and-hold.
- Placebo (all but always-on carry): the position series is circularly shifted by 2000 random lags (>= 30 days), fees and funding
  recomputed on the shifted series; p = share of placebo mean-net >= actual (add-one). Preserves exposure and turnover, so it tests
  timing, not drift. Always-on carry: stationary block bootstrap (block 10) one-sided p for mean > 0.
- Multiple testing: Benjamini-Hochberg and Holm over all 62 DEV p-values (global, no per-family relief).
- Advance DEV -> VAL: DEV net mean > 0, BH q <= 0.10, trades >= 20. VAL -> HOLD: VAL net mean > 0 and placebo p < 0.10.
  SURVIVOR: HOLD net mean > 0 and placebo p < 0.10, with its net-vs-buy-and-hold shown beside it. Survivor is "worth a card", never adopt.
- Every variant logged in TRIAL_REGISTRY.csv, including failures.
