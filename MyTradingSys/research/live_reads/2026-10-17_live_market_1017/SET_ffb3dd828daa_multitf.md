# 2026-10-18 BTCUSDT multi-TF set (4h, 8h, 1h, 12h, 1D) at ~14:56Z, re-pasted
<!-- Process: methodology/screenshot_intake.md. Claim rows `| id | MATCH or MISMATCH or NOT_IN_DATA | claim | evidence |`. No trade advice; testnet only; no marks (G3 gated). Tag: NOTE (the LAB-VERIFY from this moment is in SHOT_2da0ed270ed8.md). -->

Shots: ffb3dd828daa (4h), 5763ffcc7333 (8h), 33369d758139 (1h), df60707599d8 (12h), 4d1696e42656 (1D)
Operator words: first sent mid-turn at ~14:57Z with "Observe how context/readings/bias changes with each time frames. So we need a way to form the right bias." Those images never reached disk (card mid-turn-image-intake-gap); re-pasted 15:38Z with no text, together with 41f213b5bea3 / 188135336af0 (already read).
Clocks: CoinGlass TradingView = UTC. Countdowns: 4h 01:04:14 (12:00 bar) -> 14:55:46Z; 1h 04:04 (14:00 bar) -> 14:55:56Z; 8h 01:03:50 (08:00 bar) -> 14:56:10Z; 12h 09:03:21 (12:00 bar) -> 14:56:39Z; 1D no countdown, same moment by price.
Pre-read (VVP-002 F.1): pass on all five. Together with 6h 2da0ed270ed8 the set spans 1h-1D; missing 1m-30m at this moment (30m/15m came 25-30 min later).
Data: Binance fapi klines per TF and 1m from 10-18 00:00Z, rebuilt at a 14:56Z cut; mirror oi_1m.csv; same pulls as SHOT_2da0ed270ed8.md. The full bias-by-TF table is in READ.md (section "10-18 14:53-14:57Z multi-TF set").

## Carried context
Prior: MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SHOT_2da0ed270ed8.md
Same moment as the prior read (6h). No Falsify lines there. Its watch line (close under weekly VAL 80,868) is UNTESTED: the 12:00 6h/4h/12h bars had not closed at the shot.

## Claims
| id | class | claim | evidence |
|---|---|---|---|
| ffb3dd828daa-1 | MATCH | 4h header O 82038.5 H 82100.3 L 80987.6 C 81047.8 (12:00 bar) | fapi 4h 12:00 O 82038.5; 1m rebuild to 14:56: H 82100.3 L 80987.6 C 81043.4 (4 s later) |
| ffb3dd828daa-2 | MATCH | 4h CVD step -67.274K -> -71.126K (-3,852) | Binance taker delta 12:00-14:56 = -3,860 |
| ffb3dd828daa-3 | MATCH | 4h VWAP 81661.1 | chart-bar hlc3 VWAP from 00:00Z (4h bars) = 81,659.8 |
| ffb3dd828daa-4 | MATCH | 4h OI O 94.8K H 94.864K L 92.891K C 93.703K | openInterestHist 12:00 94,808.5; oi_1m min 92,890.8 at 13:58:56Z, max 94,849.2 at 12:09:57Z |
| 33369d758139-1 | MATCH | 1h header O 81501.0 H 81520.1 L 80987.6 C 81044.6 (14:00 bar) | fapi 14:00 1h rebuild: O 81501.0 H 81520.1 L 80987.6 C 81043.4 |
| 33369d758139-2 | MATCH | 1h CVD step -20.421K -> -22.099K (-1,678); prior 13:00 bar large red | taker delta 14:00 bar -1,677; 13:00 bar -1,860 (81,952 -> 81,501) |
| 33369d758139-3 | MATCH | 1h VWAP 81673.6 | 1h-bar hlc3 VWAP from 00:00Z = 81,672.5 |
| 33369d758139-4 | MATCH | 1h OI O 92.907K C 93.703K (+0.8K in the 14:00 bar) after the 13:00 bar's large red OI candle | oi_1m 14:00:57Z 92,920.0 -> 14:50:57Z 93,674.9; 13:00-13:58 fall to 92,890.8 |
| 5763ffcc7333-1 | MATCH | 8h header O 81645.1 H 82268.7 L 80987.6 C 81039.9 (08:00 bar) | fapi 8h 08:00 O 81645.1; rebuild H 82268.7 L 80987.6 |
| 5763ffcc7333-2 | MATCH | 8h CVD step -7.607K -> -9.449K (-1,842) | taker delta 08:00-14:56 = -1,842 |
| 5763ffcc7333-3 | MATCH | 8h VWAP 81533.0 | 8h-bar hlc3 VWAP from 00:00Z = 81,533.5 |
| 5763ffcc7333-4 | MATCH | 8h compression since 10-08: lower highs, higher lows | fapi: high 84,340.2 (10-12 06:00), 10-16 high 82,900.5, 10-18 high 82,268.7; lows 79,732.3 (10-15), 80,751.0 (10-17), 80,987.6 (10-18) |
| df60707599d8-1 | MATCH | 12h header O 82038.5 H 82100.3 L 80987.6 C 81039.9 (12:00 bar) | same bar as 4h/6h 12:00 at this time |
| df60707599d8-2 | MATCH | 12h CVD step -38.868K -> -42.748K (-3,880); prior 00:00 bar up | taker delta 12:00-14:56 = -3,860; 10-18 00:00 12h bar +4,495 |
| df60707599d8-3 | MATCH | 12h VWAP 81694.0 | 12h-bar hlc3 VWAP from 00:00Z = 81,694.0 |
| 4d1696e42656-1 | MATCH | 1D header O 81455.8 H 82268.7 L 80987.6 C 81037.8 (-418.1) | fapi 1d 10-18 O 81455.8; rebuild H 82268.7 L 80987.6 |
| 4d1696e42656-2 | MATCH | 1D CVD step 8.735K -> 9.345K (+610): the day is still net buying while the 12:00 bars sell | taker delta 10-18 00:00-14:56 = +635 |
| 4d1696e42656-3 | MATCH | 1D VWAP 81431.4 = the day bar's own hlc3 | (82268.7 + 80987.6 + 81037.8) / 3 = 81,431.4; rebuild 81,433.2 |
| 4d1696e42656-4 | MATCH | 1D: OI step down ~110K -> ~96K around Sep 23-24, flat 92-96K since | openInterestHist 6h 09-23 12:00 106,267.5 -> 09-24 18:00 95,653.0 (see 2da0ed270ed8-8) |
| ffb3dd828daa-5 | NOT_IN_DATA | Net Delta panels on all five (4h -2.546K -> -3.643K, 1h -18.933K -> -19.73K, 8h 982.8 -> 869.6, 12h -22.727K -> -23.82K, 1D -53.261K -> -53.811K) | CoinGlass Net Delta series is in no file; recurring NOT_IN_DATA |
| ffb3dd828daa-6 | NOT_IN_DATA | Session volume-profile boxes (4h, 8h, 1h) | CoinGlass session VP blocks are not stored; our VP is daily/weekly/4h/post-funding (current_market_state.md), different anchors |

## Reading (the operator's question: why the bias changes per TF)
- VWAP alone moves with the TF: 1D 81,431 / 8h 81,533 / 4h 81,661 / 1h 81,674 / 12h 81,694, against the engine's 1m-built 81,676. Each chart builds VWAP from its own bars (all five reproduce to <2 points). "Above/below VWAP" is therefore not one fact across TFs.
- CVD sign differs by TF for the same moment: 1D +610 (day net buying), every intraday bar since 12:00 negative. Not a contradiction: the 1D bar contains the 00:00-12:00 buying (+4,495).
- Bias table and the proposed fixed stack: READ.md, card multi-tf-bias-stack-one-written-rule-tha.

## Live system
Same as SHOT_2da0ed270ed8.md (mirror@2026-10-18 14:51Z): HALT + HALT_DAILY_LOSS raised, all fires skipped_halt, Tom WAIT_PROOF both sides.

## Watch next
The 16:00Z 4h/8h closes: under 80,987 (acceptance below the 10-18 low) or back over 81,500 (squeeze of the 14:00-14:45 new shorts).
