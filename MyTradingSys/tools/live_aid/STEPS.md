# Live aid: steps

Narrow BTC trading aid that sits beside the operator's charts. Requirements: `REQUIREMENTS.md` (dash-reqs session records them; each new row becomes one small shipped step here). Observation only: no order buttons, no entry/exit or sizing wording.

## Open it

Double-click `live_aid.html` (Chrome or Edge, from disk). It needs `live_aid_indicators.js` beside it. Position, rungs and custom levels are saved in that browser only (localStorage); nothing is sent anywhere.

The claude.ai Artifact copy (`python build_artifact.py <out.html>`) is a layout preview only: the viewer blocks exchange connections, so its feeds read NOT_IN_DATA.

## Feeds (public mainnet market data; he trades Deribit TESTNET, prints differ)

| Feed | Route | Note |
|---|---|---|
| Deribit BTC-PERPETUAL last + mark | ws `ticker.BTC-PERPETUAL.100ms` | P&L and rung distances use this mark |
| Binance BTCUSDT perp last | ws `fstream.binance.com btcusdt@aggTrade` | blocked from JIS-NB on 2026-10-28: shows NOT_IN_DATA + error |
| Candles 1m/5m/15m, 1h for daily levels | Binance fapi REST first; else Deribit `get_tradingview_chart_data` over the same websocket | Deribit REST has no CORS for a page opened from disk; strip/levels header names the venue |

Deribit 1D candles open at 08:00Z, so prev-day high/low and weekly open come from 1h bars folded into UTC days (`utcDays`).

## Done

| Step | What | Status |
|---|---|---|
| v1 | 4 blocks: price+clock, position (inverse P&L, ATR15 multiples, rung ladder, uncovered size), 1m/5m/15m strip, levels (VWAP, day H/L with time, prev day H/L, weekly open, typed levels). Stale badge amber past 15 s; failed feed = NOT_IN_DATA + error | BUILT 2026-10-28 |
| R10 | WaveTrend table under the strip: wt1, wt2 (colour = wt1 above/below wt2), zone vs the 53/60 lines, last wt1/wt2 cross with bars ago and level, on 1m/5m/15m. Same maths as `backtest/layers/wavetrend/wavetrend.py` (test compares them) | BUILT 2026-10-28 |
| In-trade | In-trade block (needs side typed): supports/resistance, DOM, VWAP test, divergences, squeeze read, CVD vs delta, stay confidence, rule R. Maths in `live_aid_indicators.js`, tests `test_live_aid.py` (`LIVE_AID_BREAK=itdiv|itflow|itsqueeze|itdom|itsupport|itvwap|itconf`) | BUILT 2026-10-29 |

WaveTrend 10/21/4, 0.015, lines 53/60 = OURS (LazyBear defaults; his chart settings unknown). Parameters: RSI14 Wilder, SMA14 of RSI, BB(20,2) population, ATR14 Wilder, day VWAP hlc3 from 00:00Z = SOURCED (his chart setup). RSI 30/70 flag lines, session names = OURS.

## In-trade rules (OURS, written before any data was looked at; sd = +1 long, -1 short)

| Item | Rule |
|---|---|
| Feeds | Deribit public ws: `trades.BTC-PERPETUAL.100ms` (CVD, delta), `book.BTC-PERPETUAL.none.20.100ms` (DOM), `open_interest` in the ticker. A feed silent for 30 s or errored = NOT_IN_DATA + the error. CVD counts only trades since the page connected |
| Supports / resistance | the 2 nearest Levels-block prices below (long) or above (short) the Deribit mark; none = "none on that side" |
| DOM | within +/-0.25% of mark: bid size, ask size, imbalance (bid-ask)/(bid+ask), biggest level. Flag for if imbalance x sd > 0.2, against if < -0.2 |
| VWAP test | last 5 x 1m bars: touch = bar range contains day VWAP. No touch = "no test"; touched and last close on the trade side = held (flag for); other side = lost (flag against) |
| Divergence | per TF (1m/5m/15m) for RSI14 and WaveTrend wt1: last 30 bars as two halves of 15. Bullish: price lower low in 2nd half and indicator higher low; bearish: price higher high and indicator lower high. Flag uses 1m RSI only: with the side = for, against the side = against. CVD/delta/OI divergence: shown by the CVD and squeeze bullets, not separately |
| Squeeze read | price and Deribit OI change over up to 10 min of 10 s samples (needs 2 min); under +/-0.05% = flat. up+OI up new longs, up+OI down short covering, down+OI up new shorts, down+OI down long unwind. Flag: price against the side = against; with the side and OI up = for; else neutral |
| CVD vs delta | CVD = net taker USD over 15 min (or since connect), delta = net over the last 60 s. Both with the side = for, both against = against, split = neutral |
| Stay confidence | flags for / available among DOM, VWAP, 1m divergence, squeeze, flow (NOT_IN_DATA excluded) |
| Rule R | met if 3 or more available flags are against. A readout only: no size, no entry/exit wording (card note: sizing stays forbidden) |

## Backlog (his words first)

| Step | His words / source | Reading (OURS) |
|---|---|---|
| Liquidation tape, OI and flow | brief from Eagle_Eyes | live liquidation prints, open interest and taker flow beside price |
| Liquidation layer context (R08) | "now we have to find out how much of this is actually useful - worth trusting - so we need a constant context building for this liquidation layer" | show each typed heatmap band's track record from `research/liquidation_layer_2026-10-28/BANDS_LEDGER.csv` |
| Heatmap vs what played out, by timeframe (R09) | "we can also see it's diff timeframes to compare what platyed out at lower time frames since last weeks" | per band: touched / swept / rejected on 1m-15m since last week |
| Multi-timeframe flip watch | brief from Eagle_Eyes | flag when RSI crosses its SMA or %B crosses 0/1 on 1m, 5m, 15m |
| Per-layer looks at US open (R02) | "so now when us opens we can look into getting into positions based on each layer" | at 13:30Z show each layer's current reading, descriptive only |
| Setup checklist: pre-US failed break | brief from Eagle_Eyes; his Deribit log | failed break above last high + momentum shift before US open; OURS definition, not validated |
| Analyst strip from CBP | brief from Eagle_Eyes | latest Habib / analyst levels from CBP, labelled by venue |
| More timeframes | brief from Eagle_Eyes | 1h / 4h rows in the strip |
| All latest inputs (R03) | "all latest inputs" | every layer's latest input on the page, kept current |
