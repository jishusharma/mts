# Live dashboard: "What the money is doing" (OI commentary tile), spec 2026-10-31

Operator ask (10-31 ~19:45Z, verbatim): "this is the kind of commentary that I need on my dashboard. When OI is changing, then what is
the actual scenario? Is the money entering or is the money leaving? What has just happened? What to expect?"

Model answer he liked: the 19:31Z read "OI is favouring what?" (C24 row, `BACKTEST_CANDIDATES.md`).

Target: `MyTradingSys/tools/live_aid/live_aid.html` (today one line, "Squeeze (price vs open interest)", Deribit OI only, 10 min).
Descriptive only: no entry, exit or size words.

## Inputs (all public)
| Feed | Source | Note |
|---|---|---|
| Deribit OI + last | already on the page (ticker) | USD contracts |
| Bybit OI + last | `tickers.BTCUSDT` WS already open (`openInterest` field) | BTC |
| Binance OI | `fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT`, poll 30 s from the browser | blocked on some hosts: show NOT_IN_DATA, never guess |
| Liquidations | already on the page (Bybit, Binance, Deribit) | side = position liquidated |
| Taker flow / CVD | already on the page | |
| Funding | already on the page | |

## Read (rules OURS, thresholds fixed here before use)
Per venue and summed in BTC, windows 5 / 15 / 60 min, price change dp and OI change doi (flat = |doi| < 0.1 %, |dp| < 0.1 %):

| Price | OI | Plain sentence |
|---|---|---|
| up | up | Money entering on the long side: new longs are buying. |
| down | up | Money entering on the short side: new shorts are selling. |
| up | down | Money leaving: shorts are covering (a squeeze); the rise is not fed by new buyers. |
| down | down | Money leaving: longs are closing or being liquidated (a flush). |
| flat | up | Positions building without a move: both sides adding, pressure stored for the next break. |
| flat | down | Positions closing quietly; interest is fading. |

Add one line each, only when it applies:
- Venues disagree (one OI up >= 0.2 %, another down >= 0.2 %): "Binance adding, Bybit closing: positions moving between exchanges, net money about flat."
- Who: liquidation side in the window ("longs liquidated 4.1M"), CVD agrees / disagrees with price, funding sign.
- Just happened (event, last 60 min): FLUSH = a 5m bar with price -0.25 % or worse and OI -0.2 % or worse (mirror for a SQUEEZE up). Show time, low/high, size.
- Trapped side and the line: after a flush, new shorts building + price under the bounce high = "shorts trapped above <bounce high>; longs trapped below <flush low>".

## What to expect (MEASURED lines only, each with n and the study)
- After a flush, OI path over the next 40 min (C24, Bybit 120 days): rebuilding n=18, flat n=9, still falling n=22: 4h up 53/56/55 % vs 52 % base -> "no direction from OI alone"; still falling -> 4h drop > 1 % 14 % vs 6 % base -> "a bigger move is twice as likely, direction open".
- No measured line for a state -> print "not measured yet" and file it in `BACKTEST_CANDIDATES.md`; never a guessed probability without the OURS label.

## Done when
- The tile shows the six-state sentence per window, the venue-disagreement line, the last event, the trapped-side line and the measured lines, each with data age; a dead feed says NOT_IN_DATA.
- Tests: each of the six states, the disagreement line, the flush detector, a stale feed and a 0 OI value (fails on the pre-change page).
- The 10-30 18:50Z flush replayed from Bybit 5m data prints: FLUSH 18:50, price -0.6 %, OI -0.37 %, longs liquidated.
