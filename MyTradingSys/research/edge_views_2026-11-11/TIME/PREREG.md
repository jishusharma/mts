# PREREG: TIME view (does BTC drift at fixed clock times?) 2026-11-11, written before any result

Data: Binance SPOT BTCUSDT 1h klines, F:/MTS/Dumps/backtest/spot_2017/BTCUSDT/1h/klines/*.csv (2017-08 .. 2026-10; the 7y+ set; 2025+ files stamp in microseconds).
Return of a window = close(last bar)/open(first bar) - 1, in bp. All windows are fixed UTC (OURS); no DST adjustment. Hourly bars only, so 13:30 becomes 14:00:
Europe = 08-14Z, US = 14-21Z, first US hour = bar 14-15Z. A window with any missing bar is dropped.
Observations are dated by window start. DEV = first 60 % of days; 30-day gap; VALIDATION = the rest. RECENT = last 365 days (reported, not a gate).
Per cell: n, mean bp, t (mean/SE, normal approx), share positive; same on DEV, VAL, RECENT.

## Fixed family (OURS), 44 cells, no additions
| Id | Cells | Count |
|---|---|---|
| a | mean bar return by UTC hour 00..23 | 24 |
| b | mean 24h return (00Z to 00Z) by weekday | 7 |
| c | weekend (Sat 00Z to Mon 00Z) return; weekday (Mon 00Z to Sat 00Z) return, per week | 2 |
| d | blocks Asia 00-08Z, Europe 08-14Z, US 14-21Z | 3 |
| e | continuation: sign(14-15Z bar) * return(15-21Z) | 1 |
| f | Asia to US: sign(00-08Z) * return(14-21Z) | 1 |
| g | bar before (h-1..h) and bar after (h..h+1) each of h = 00, 08, 16Z | 6 |
Family size m = 44. Bonferroni: two-sided alpha 0.05/44 = 0.00114, |t| >= 3.25 (normal).

## Mark rule (all three)
1. |t| >= 3.25 in DEV. 2. Same sign of mean in VALIDATION. 3. |mean| > 10 bp (the taker round trip; maker 5 bp noted). Else no mark.
Cells e,f are sign-aligned (positive = continuation). Weekday and weekend cells are long-only means; a negative mean means a short drift, same 10 bp bar.
Existing work (cited, not repeated): session_sweeps/session_open_study + us_open_oos_2026-10-30/REPORT.md (US-open first 10/15/30 min does not predict the rest, P~0.50, 1m perp 2020-26); census_5m_15m_session_ladder_2026-11-09 (session x level fade, no edge); monday_open_2026-11-09 (Monday clocks); research hour-of-day placebo inside us_open_oos (24 anchors 0.44..0.555).
