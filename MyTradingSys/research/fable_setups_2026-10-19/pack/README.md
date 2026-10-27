# Fable run 4 pack: BTCUSDT LOOK window

**Window: 2022-01-01 00:00 UTC to 2023-06-30 23:59 UTC. Nothing after 2023-06-30 is in this pack** (every bar opens
on or before 2023-06-30; `build/leak_check.py` checks every file, `build/test_pack.py` proves it fails on a planted row).
Source: public Binance USD-M perpetual BTCUSDT 1m klines (data.binance.vision), aggregated to each timeframe, so all
files agree bar for bar. Times are UTC. Prices are USDT.

## Files
| File | Content |
|---|---|
| `ohlcv_1w.csv` | 77 weeks (Monday 00:00 open); only complete weeks (first week opens 2022-01-03, last opens 2023-06-19) |
| `ohlcv_1d.csv`, `ohlcv_12h.csv`, `ohlcv_4h.csv` | 546 days, 1092 half-days (00:00 and 12:00), 3276 four-hour bars, all complete |
| `levels_daily.csv`, `levels_weekly.csv` | one row per completed day / completed week (same 15 columns) |
| `charts/` | 31 naked PNG charts (1W 1, 1D 6, 12h 6, 4h 18) |
| `RULES_DIGEST.md` | Tom and Fabio rules as SOURCED quotes with file:line, plus what already failed |

## Columns
`ohlcv_*`: `open_time_utc` (bar open), `open`, `high`, `low`, `close`, `volume` (BTC), `taker_buy_volume` (BTC bought by
takers inside the bar). Taker buy volume is the ONLY order-flow proxy here: taker sell = volume - taker_buy_volume,
delta = 2 * taker_buy_volume - volume. It is a bar total, not tick-level CVD, and says nothing about absorption inside a bar.

`levels_*`: one row per period, keyed by `period_open_utc`. The row describes that period **after it closed**: use it only from
the next period's open (a daily row dated D is the "prior day" on D+1, a weekly row dated Monday W is the "prior week" from
Monday W+7 days). Using it inside its own period is look-ahead.
- `open, high, low, close`: of the period.
- `poc, vah, val`: volume profile of the period per FORMULAS 18.1: 10 USD bins, each 1m bar's volume spread uniformly over
  its high-low, POC = lowest bin of maximum volume (value `bin center`), value area = 70 % of volume grown from the POC
  toward the larger neighbouring bin (ties go lower), `val` = lower edge of the lowest bin, `vah` = upper edge of the
  highest bin. Built from 1m bars (more precise than FORMULAS' bar-set wording needs; same rule).
- `asia_high/low`, `london_high/low`, `ny_high/low`: extremes inside UTC session windows of that period. Asia 00:00-08:00,
  London 08:00-14:00 (the EU window of the session_levels layer), NY 14:00-24:00 (US open to day end). The NY window is OURS: the
  session_levels layer defines no NY window. In `levels_weekly.csv` they are the highest high / lowest low of that session
  over the 7 days.

## Charts
Candles plus volume, no indicators. Per prior-week: blue line = POC, orange dashed = VAH and VAL, drawn over the week
AFTER the week they describe. Charts are context only: a rule may reference pack table columns, never levels read off an image.

## Cost
Round trip cost 14 bp of price (10 bp taker fee both legs + 2 bp slippage per FORMULAS 13, 2 bp OURS allowance on top,
set by the run 4 brief). Net R = gross R - 0.0014 / (stop distance as a fraction of entry). A 0.25 % stop costs 0.56 R.

## Not in the pack
Funding, open interest, order book, ticks, 1m/5m/1h bars, anything after 2023-06-30. No internet, no scripts on outside data (brief).
`build/` (not part of the Fable read set) holds the scripts that made this pack.
