# Live trading aid: requirements (operator, 2026-11-02 16:30Z, voice, while in a BTC short)

Operator words: "This kind of wavetrend and other indicator reading when they are flipping through time frames is needed during live trading aid/dashboard - mark my requirements - good visuals - less text - actionable content."

## What it is
One screen the operator keeps open while in a trade. It replaces the Eagle_Eyes chat loop of today (screenshot -> question -> measured answer) with a page that already shows the measured answer for the current state on every timeframe.

## Must show (per timeframe 1m, 5m, 15m, 1h, 4h, side by side)
| Row | Content | Source today |
|---|---|---|
| Indicator state | WaveTrend (wt1/wt2, zone, cross up/down), RSI14, Stoch RSI, BB position + width rank, OI change, CVD / taker delta sign | coinglass + tradingview screenshots |
| Base rate for THIS state | the measured count: "WT 1h cross <0 from >=50, RSI<40: low first 62%, 6h up 67% (n=45)" | wt1h_zero.py, four_h_close.py, low_take.py, preus_oi_cvd.py, green_neg_delta.py, break_retest.py, oi_spike_absorbed.py |
| Levels in play | day low/high, prior-day low, open-bar low, BB bands, operator's drawn lines, with the hit-probability table (low_take.py style) | live_read.py + the studies |
| Clock | UTC now, minutes to US cash open / close, 4h and 1h bar close countdown | live_read.py |

## Style rules (his words)
- Good visuals: colour-coded cells (green/red/grey), sparklines, one glance per timeframe. No prose blocks.
- Less text: numbers and short labels only; the full study lives one click away.
- Actionable: every cell answers "what does this state do next, how often"; never an entry/exit/size call (Eagle_Eyes rule).
- Trailing 1m | 5m legend at the bottom (ask 11-02).

## Not in scope
Orders, position reading from Deribit, alerts that fire trades. Mainnet accounts stay out (testnet rule).

## Build notes
- Data: Bybit v5 public REST works from JIS-NB (Binance API times out). 1m klines + 5m OI.
- Base rates come from the committed scripts in this folder; the page recomputes the state, looks up the matching study row, shows n. HOLDOUT 2025-07-01.. stays sealed: all tables cut at END=2025-07-01.
- First version: static HTML artifact refreshed by a script every minute (same shape as the sim-demo artifact on trunk), no scheduler (SCHEDULING_POLICY): the operator starts it by hand.
