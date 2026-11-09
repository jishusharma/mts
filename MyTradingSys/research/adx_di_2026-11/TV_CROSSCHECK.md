# ADX/DI cross-check against the operator's TradingView (card adx-di-tradingview-crosscheck-1107)

Verdict 2026-11-07: **VERIFIED-TV** for the formula. Built-in Directional Movement Index 14/14 on BINANCE:BTCUSDT daily, read by a
Haiku Chrome worker on his signed-in chart: the two historical bars match to 0.01 on all six values. The last bar (2026-11-06)
differs by 0.80 (DI+) and 0.69 (ADX) because btc_daily.csv was committed 2026-11-06 18:00Z, before that day closed (csv close
75,771.76 vs the exchange close about 75,848): a partial-row artefact, not a formula gap. Fix for the census: refresh the csv after
00:00Z before each run. 2D is paywalled on his TradingView plan, so our 2d buckets (epoch-even-day aligned) stay unverified against
TradingView; the formula itself does not depend on the bucket.

## Daily read (Haiku, 2026-11-07 ~14:20Z)
# TradingView DMI daily check: BINANCE:BTCUSDT (spot)

TradingView inputs: built-in "Directional movement index" (DMI), lengths 14 / 14 (legend reads `DMI 14 14`). Symbol BINANCE:BTCUSDT, interval 1D, new tab (not his chart tab). Legend order read as ADX, +DI, -DI (the three values match ours in that order on Jan 15 and May 15).

| bar | value | ours | TradingView | abs diff | PASS/FAIL (tol 0.5) |
|---|---|---|---|---|---|
| 2026-01-15 | DI+ | 31.60 | 31.6044 | 0.00 | PASS |
| 2026-01-15 | DI- | 8.54 | 8.5400 | 0.00 | PASS |
| 2026-01-15 | ADX | 31.79 | 31.7909 | 0.00 | PASS |
| 2026-05-15 | DI+ | 22.03 | 22.0264 | 0.00 | PASS |
| 2026-05-15 | DI- | 13.51 | 13.5115 | 0.00 | PASS |
| 2026-05-15 | ADX | 30.62 | 30.6196 | 0.00 | PASS |
| 2026-11-06 | DI+ | 16.78 | 17.5818 | 0.80 | FAIL |
| 2026-11-06 | DI- | 20.97 | 20.9749 | 0.00 | PASS |
| 2026-11-06 | ADX | 20.13 | 20.8239 | 0.69 | FAIL |

Bar dates confirmed by the crosshair tooltip: "Thu 15 Jan 26", "Fri 15 May 26", "Fri 06 Nov 26" (last closed daily bar; Nov 6 OHLC O 80504.01 H 80918.01 L 75208.42 C 76088.01).

2D interval: paywalled. Typing 2D in the interval box applied, then an Upgrade popup ("Custom intervals", Basic plan) appeared.

Verdict: PARTIAL, 7/9 cells pass. Failing cells are the 2026-11-06 DI+ (diff 0.80) and ADX (diff 0.69). Jan and May match to 0.01. Nov 6 DI- matches. The gap is confined to the latest bar, so the cause is either our last-bar input (possibly a different feed or a bar still forming when we ran) or TradingView's data for that bar. Not resolved here.

Cleanup: the DMI indicator was added on a new tab, not his tab (his tab untouched). The new tab was not saved. Close of the new tab did not respond on one attempt.
