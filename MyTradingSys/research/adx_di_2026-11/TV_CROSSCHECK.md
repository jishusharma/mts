# ADX/DI (Wilder, n=14) cross-check: ours vs TradingView BINANCE:BTCUSDT 1D

Status: BLOCKED on the TradingView side. The chart and daily bars load on the free plan, but adding the
"Directional movement index" indicator opens a "Join for free" sign-up popup each time, so no DMI was added
and no TV value was read. I did not sign up. The 9 cells are NOT checked.

## Daily, ours: adx_di(n=14) directly on btc_daily.csv daily rows (no resample; warm-up from 2017-01-01)

| bar (UTC) | ours DI+ | ours DI- | ours ADX | TV bar start | TV DI+ | TV DI- | TV ADX | abs diff | PASS/FAIL (tol 0.5) |
|---|---|---|---|---|---|---|---|---|---|
| 2026-01-15 | 31.60 | 8.54 | 31.79 | not read | not read | not read | not read | - | NOT CHECKED |
| 2026-05-15 | 22.03 | 13.51 | 30.62 | not read | not read | not read | not read | - | NOT CHECKED |
| 2026-11-06 (last closed daily) | 16.78 | 20.97 | 20.13 | not read | not read | not read | not read | - | NOT CHECKED |

## Source
- btc_daily.csv has a `source` column: blockchain.info up to 2017-08-16, binance from 2017-08-17. All three bars above are binance.
- FORMULAS.md section 30 names no exchange or data file.
- TradingView reference: BINANCE:BTCUSDT (spot).

## 2d (earlier attempt, for reference only)
- 2D is paywalled on his account: custom intervals open the upgrade popup, so no 2D chart was read.
- Our 2d buckets are epoch-even-day aligned (registry.json, anchor 1970-01-01). Unverified against TV.
- Ours 2d (not checked): 2026-01-15..16 DI+ 23.36 DI- 15.22 ADX 23.89; 2026-05-15..16 DI+ 22.09 DI- 15.03 ADX 28.01; 2026-11-05..06 DI+ 16.68 DI- 17.49 ADX 22.99.

## Verdict
NOT VERIFIED. No TV value read. Blocker: the DMI indicator needs a free account on this TradingView session (sign-up popup).
Operator decision needed: sign in to TradingView himself to add DMI, or accept the formula check as unverified.

## Exchange-chart oracle (Binance / Bybit), attempted after the TradingView block
- binance.com/en/trade/BTC_USDT?type=spot: error page in the browser (region or access block). Not read.
- bybit.com/en/trade/usdt/BTCUSDT: loads, but it is the BTCUSDT PERPETUAL chart (not spot), and the chart toolbar is cut off at this window width. The indicator (f(x)) button was not reachable, so the DMI was not added. Only the interval 1D was set; a Custom Formula panel was opened by mistake and closed with Escape.
- Result: no DI+/DI-/ADX read from any exchange chart. The table above stays NOT CHECKED.
- Verdict unchanged: NOT VERIFIED. Operator options: sign in to TradingView, or a wider window on Bybit/Binance with the indicator button visible.
