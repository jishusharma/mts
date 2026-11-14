# RECOMPUTE: independent recompute of 3 (plus 2 extra) dev trades

Verdict: MATCH. Largest absolute difference on any field 1.6e-15 (float noise); nothing above 1e-6 R.

Method: throwaway script (outside the repo, scratchpad `recompute.py`) written from PRE_REG.md and FORMULAS.md (s1, s4, s5 RSI/EMA/WMA, s12 ATR plain SMA, s13 costs, s25 halving, s30 ADX/DI) only; t3_study.py logic was not read. Inputs: raw `spot_1d` klines and `funding` prints in `F:\MTS\data_cache\binance\t3-early-uptrend-1114`. Cost = 2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 = 0.0010 + 0.0002 = 0.0012 (imported from fees.py). Trades: 1 stop (A NEAR), 1 RIDE exit (A FIL), 1 time exit on cell B (B THETA); extras: B stop (ALGO), A time (MATIC).

Phase labels of the entry day (BTC closes of days <= D-1; SMA200, SMA200 20 days earlier, days since halving) and signal conditions, all reproduced:

| trade | BTC close D-1 | SMA200 | SMA200 20d ago | days since halving | UP_E | signal bar condition | onset |
|---|---|---|---|---|---|---|---|
| A NEAR 2021-08-21 | 48821.87 | 45762.29 | 44712.02 | 467 | yes | ADX 47.59, DI+ 53.24 > DI- 4.51, vol 24.55M = 3.79 x median30 6.48M | prev bar vol ratio 1.23 -> onset |
| A FIL 2021-08-11 | 45511.00 | 45086.62 | 44633.37 | 457 | yes | ADX 35.58, DI+ 38.31 > DI- 9.83, vol ratio 2.075 | prev ratio 1.49 -> onset |
| B THETA 2021-01-26 | 32467.77 | 16728.23 | 14084.61 | 260 | yes | RSI9 66.70, EMA3 60.32, WMA21 54.79 (WMA21 below both), close 2.2870 > weekly VWAP 2.1813 | prev close below VWAP -> onset |
| B ALGO 2021-03-28 | 55777.63 | 28351.03 | 23826.10 | 321 | yes | RSI9 61.09, EMA3 54.72, WMA21 50.78, close 1.2354 > VWAP 1.1172 | prev HM not buy -> onset |
| A MATIC 2021-01-10 | 38150.02 | 14686.37 | 12558.44 | 244 | yes | ADX 31.42, DI+ 31.80 > DI- 13.81, vol ratio 2.754 | prev ratio 1.86 -> onset |

ATR14 (plain SMA of TR, signal bar) and S = max(2.5 x ATR14, 2% of entry): NEAR 0.516743 -> S 1.291857; FIL 4.656429 -> 11.641071; THETA 0.259944 -> 0.649859; ALGO 0.132964 -> 0.332411; MATIC 0.004468 -> 0.011170. Net R = (gross return - 0.0012 - funding) / (S / entry).
### A NEAR signal 2021-08-21 (entry 2021-08-22, exit 2021-08-24 STOP)

| field | builder | yours | diff |
|---|---|---|---|
| exit_date / reason | 2021-08-24 / STOP | 2021-08-24 / STOP | same |
| entry_px | 6.1803 | 6.1803 | 0.00e+00 |
| S | 1.291857143 | 1.291857143 | 4.44e-16 |
| stop | 4.888442857 | 4.888442857 | -8.88e-16 |
| exit_px | 4.888442857 | 4.888442857 | -8.88e-16 |
| gross_R | -1 | -1 | -4.44e-16 |
| funding | 0.00591646 | 0.00591646 | -4.34e-17 |
| net_R | -1.03404545 | -1.03404545 | 0.00e+00 |

### A FIL signal 2021-08-11 (entry 2021-08-12, exit 2021-09-22 SIGNAL)

| field | builder | yours | diff |
|---|---|---|---|
| exit_date / reason | 2021-09-22 / SIGNAL | 2021-09-22 / SIGNAL | same |
| entry_px | 71.76 | 71.76 | 0.00e+00 |
| S | 11.64107143 | 11.64107143 | 0.00e+00 |
| stop | 60.11892857 | 60.11892857 | 0.00e+00 |
| exit_px | 69.54 | 69.54 | 0.00e+00 |
| gross_R | -0.1907040957 | -0.1907040957 | 0.00e+00 |
| funding | 0.03301929 | 0.03301929 | 1.39e-17 |
| net_R | -0.4016448382 | -0.4016448382 | 0.00e+00 |

### B THETA signal 2021-01-26 (entry 2021-01-27, exit 2021-03-27 TIME)

| field | builder | yours | diff |
|---|---|---|---|
| exit_date / reason | 2021-03-27 / TIME | 2021-03-27 / TIME | same |
| entry_px | 2.28384 | 2.28384 | 0.00e+00 |
| S | 0.6498589286 | 0.6498589286 | 0.00e+00 |
| stop | 1.633981071 | 1.633981071 | 0.00e+00 |
| exit_px | 11.81375 | 11.81375 | 0.00e+00 |
| gross_R | 14.6645827 | 14.6645827 | 0.00e+00 |
| funding | 0.12650164 | 0.12650164 | -1.39e-16 |
| net_R | 14.21579281 | 14.21579281 | 0.00e+00 |

### B ALGO signal 2021-03-28 (entry 2021-03-29, exit 2021-05-19 STOP)

| field | builder | yours | diff |
|---|---|---|---|
| exit_date / reason | 2021-05-19 / STOP | 2021-05-19 / STOP | same |
| entry_px | 1.2354 | 1.2354 | 0.00e+00 |
| S | 0.3324107143 | 0.3324107143 | 0.00e+00 |
| stop | 0.9029892857 | 0.9029892857 | 0.00e+00 |
| exit_px | 0.9029892857 | 0.9029892857 | 0.00e+00 |
| gross_R | -1 | -1 | 0.00e+00 |
| funding | 0.10389942 | 0.10389942 | -3.75e-16 |
| net_R | -1.390600597 | -1.390600597 | 1.55e-15 |

### A MATIC signal 2021-01-10 (entry 2021-01-11, exit 2021-03-11 TIME)

| field | builder | yours | diff |
|---|---|---|---|
| exit_date / reason | 2021-03-11 / TIME | 2021-03-11 / TIME | same |
| entry_px | 0.0302 | 0.0302 | 0.00e+00 |
| S | 0.01116964286 | 0.01116964286 | 0.00e+00 |
| stop | 0.01903035714 | 0.01903035714 | 0.00e+00 |
| exit_px | 0.40884 | 0.40884 | 0.00e+00 |
| gross_R | 33.89902478 | 33.89902478 | 0.00e+00 |
| funding | 0.16591416 | 0.16591416 | -2.22e-16 |
| net_R | 33.4471887 | 33.4471887 | 0.00e+00 |

## Notes (not discrepancies)
- Funding window convention found by recompute: rates with entry-open < ts <= end of the exit bar (exit-day open + 24 h) for STOP and TIME exits; for a SIGNAL exit (fills at the next open) the window ends at that open. Matches FORMULAS s13 and the builder to 1e-15 on all 5 trades. PRE_REG does not state the intrabar stop time; end of the stop bar is the conservative choice (funding window not shorter than the true one).
- Day 60 of a time exit counts the entry day as day 1 (entry 2021-01-11, exit close 2021-03-11), confirmed on THETA and MATIC.
- All 5 trades have real funding prints (fund_flat False); the flat 1 bp / 8 h path was not exercised by this recompute.
- Not covered: CAP3R rows, Cell B VWAP edge cases across a week boundary, trades whose exit hits the stop on the entry day.
