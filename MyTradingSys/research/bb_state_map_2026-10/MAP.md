# BB state x candle x regime x TF map (descriptive, fee-free, DEV 2022-2025)

Status: RUN 2026-10-30 on JIS-NB (tom_raw present). map.csv written.
All definitions are OURS (not the trader's). Holdout (2026+) is never loaded.

## Definitions (OURS)
- TF bars: 15m, 1h, 4h, 12h, built from BTCUSDT 1m (F:/MTS/data/tom_raw/klines), UTC-aligned, open/high/low/close.
- Bands at close of bar t: BB(20,2) on closes, population std (ddof=0). Levels frozen at t.
- BB state (close[t]): ABOVE_UP (close>=upper), UP_HALF (mid<=close<upper), LOW_HALF (lower<close<mid), BELOW_LOW (close<=lower).
- Prior candle (the bar that just closed, t): GREEN (close>open, body>=10% of range), RED (close<open, body>=10%), DOJI (body<10% of range).
- Regime (OURS, fixed first): MOVING if |mid[t]-mid[t-5]| > 0.5*sd[t], else NOT_MOVING.
- Cell = TF x state x candle x regime.
- Outcomes, looking forward from t, horizon H=12 TF bars:
  - next-bar direction: share of close[t+1]>close[t].
  - reach lower / mid / upper: share of cells where a later bar's low/high touches the frozen level within H; plus first-touch of lower vs upper (lower_first / upper_first / same-bar / neither).
  - max favourable = max(high)-close[t], max adverse = close[t]-min(low), over H, as % of close; medians reported both for up-side and down-side excursion.
- Cells with n<30 are greyed (flag grey=1 in map.csv).
- Operator shots 8faf2cac14be, f2fb8d432eb7, 85ba89446b0d are located by their timestamps/TF in their cells once the shot times are read from the screenshots (step 3; needs data).

## Counts (run on JIS-NB, DEV 2022-2025, descriptive, fee-free)
- Total bar-observations: 186,860 (15m 140,219; 1h 35,027; 4h 8,729; 12h 2,885).
- Cells: 96 (24 per TF = 4 state x 3 candle x 2 regime); grey (n<30): 13 (12h 8, 4h 5, 15m 0, 1h 0).
- Output: map.csv (one row per cell). Operator-shot cell lookup (step 3) not done.
- Data note: 2025-09-01..07 exist as both monthly and daily files; load() now de-duplicates by timestamp and sorts (counts identical).
