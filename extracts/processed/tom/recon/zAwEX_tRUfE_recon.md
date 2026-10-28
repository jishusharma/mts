# Trade reconstruction zAwEX_tRUfE
Trader: Tom (per task/path; not stated in the video). Video title: "My Simple 1-Minute Scalping Strategy for $10,000/Month" (source header). Instrument: S&P 500, 1-minute chart. Session/time of day: cash session, exact time NOT STATED; quote: "during the cash session, the main trading hours". Type: lesson / chart replay with illustrative trades; no live execution stated.

## Trade 1
Concrete chart example, not live: long from below equilibrium to equilibrium.

| field | reading |
|---|---|
| market state | "I can see immediately that we are simply not yet above the equilibrium point. It is clear we have more ground to cover. Here is the equilibrium from the previous day. And the market always strives to stay in equilibrium at first." |
| location | "If you now consider making your purchase here, with this closing price, for example, outside in the price range at 7,482." |
| leading signal | "a setup could be a nice P, like the one I'm showing you here. Yeah, from the PBD structure." |
| trigger | "So, if I now book this trade here, as I just showed, I can plan it up to the upper edge of the equilibrium." |
| initial stop (price and % of price, and ticks if futures) | Stop location: "And most traders on the 1-minute chart take the risk below the last low. That is the risk." Price: NOT STATED. % of price: NOT STATED. Ticks: NOT STATED. |
| target(s) and planned R:R | "recognize that 785 is the equilibrium limit." "So, now I have a trade that I can plan from, well, not even $3, $2.75, and that's the profit range I should plan now." "The risk-reward ratio is somewhere in the range of 0.8 here" |
| management (breakeven, adds, trail anchor) | NOT STATED |
| exit (what actually ended it) | "equilibrium was at 7485, and the market reached this target. Here was the entry, yeah, and here was the equilibrium. So, to take your exit." |
| outcome in R and in money if stated | Target reached: "the market reached this target". R: NOT STATED. Money: NOT STATED. |
| day selection / day type | NOT STATED |
| horizon (minutes held) | NOT STATED |
| what he explicitly does NOT do | "Now, many traders have this idea that the market should, of course, keep running much further. And I don't think this idea is good, nor is it effective." |

## Trade 2
Concrete chart example, not live: breakout long above the value area.

| field | reading |
|---|---|
| market state | "Here we suddenly have another nice entry signal above the value area, and we already had a signal here that the market is breaking out of this range." |
| location | "Here we suddenly have another nice entry signal above the value area" |
| leading signal | "This signal right here, I'm going to make it very thick and bold for you, is the specific signal that, for you as a short-term 1-minute scalper, is a truly great technical signal." |
| trigger | "another nice entry signal above the value area" and "the market is breaking out of this range." |
| initial stop (price and % of price, and ticks if futures) | "you're out relatively quickly down here if the market accepts the old equilibrium again." Price: NOT STATED. % of price: NOT STATED. Ticks: NOT STATED. |
| target(s) and planned R:R | "You have a much more predictable profit run." Numeric target: NOT STATED. Planned R:R: NOT STATED. Related: "even with just a 50 or 60% win rate, you can make money with this." |
| management (breakeven, adds, trail anchor) | NOT STATED |
| exit (what actually ended it) | "if the market accepts the old equilibrium again" |
| outcome in R and in money if stated | NOT STATED |
| day selection / day type | NOT STATED |
| horizon (minutes held) | NOT STATED |
| what he explicitly does NOT do | "Do I truly possess the necessary patience to refrain from having already attempted 20 impulsive trades within this specific price range, simply because I find myself trading somewhere in the middle of the action?" and "am I disciplined enough to actually let the market come to me instead of forcing the trade?" |

## Session view
Whole-session result: NOT STATED. The video is a lesson, not a live session P&L. Quote: "And that's all. Less is more."

## Section 3.2 additions
- Instrument line: S&P 500, 1-minute chart. Tick value: NOT STATED. Stop in ticks: NOT STATED. Stop in ATR: NOT STATED.
- Order type per leg (maker/taker), and when the order was placed (before or after the touch): NOT STATED.
- Outcome: Trade 1 target reached; R and money NOT STATED. Trade 2 outcome NOT STATED.
- Gate replay: NOT IN SCOPE: verdict.py or our layer is not in the SOURCE blocks.
- Portability arithmetic: Trade 1 stop width is NOT STATED. Using the stated profit range of 2.75 points and R:R 0.8 gives inferred risk ≈ 3.44 points; at entry 7,482 this is ≈ 0.046% of price. Deribit BTC-PERPETUAL round trip at taker 5 bps per side = 10 bps = 0.10%. Fee per stop-out in R = 0.10% / 0.046% ≈ 2.18R. Trade 1 does not survive at that stop width. Trade 2 stop width is NOT STATED, so portability arithmetic cannot be computed. BTC hours corresponding to his S&P 500 cash session: US cash open 13:30 UTC summer / 14:30 UTC winter.
- Ambiguity flags: "785 is the equilibrium limit" conflicts with later "equilibrium was at 7485"; "not even $3, $2.75" conflicts with 7,482 to 7,485 being $3; "outside in the price range at 7,482" is an illustrative entry, not a stated fill.
- Coverage rule: one lesson extract, no losing session reconstructed; the 1-losing-per-2-winning coverage rule is not met by this file alone.
