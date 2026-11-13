# Iteration 3 merge: code_vs_rulebook

Sources: argon only. Rows 35: AGREED 0, SINGLE 35, CONFLICT 0, UNVERIFIED 0 (rows needing a quote that no transcript match supported). Verified quotes below: 13.
Only one model ran this topic, so no row can be AGREED; every row is SINGLE. Pattern, ledger and fix columns are assigned by rule from the source row (code column, numbers, transfer words) and the ledger column matches video id plus two shared content words; both are first-pass labels, not a re-read.

## Items

| id | item | model verdict | pattern | in ANSWER_LEDGER? | fix type |
|---|---|---|---|---|---|
| CR-01 | Wait for a clear breakout confirmation signal such as a strong impulse candle accompanied by rising volume/liquidity. | SINGLE | 4 | N | re-code |
| CR-02 | Negative delta with positive price action shows seller effort without follow-through; enter as the 5-minute bar closes. | SINGLE | 4 | N | re-code |
| CR-03 | Fast rejection speed on the tape confirms immediate entry. | SINGLE | 1 | N | re-frame |
| CR-04 | Breakout momentum out of a sideways phase must be accompanied by increasing trading volume. | SINGLE | NEW | N | test |
| CR-05 | High buy-delta pressure producing almost zero price movement confirms passive seller absorption to enter short. | SINGLE | NEW | Y L09 | test |
| CR-06 | Place limit entries 1 or 2 ticks in front of visible resting limit-order blocks on the heatmap/DOM. | SINGLE | 2 | N | extract |
| CR-07 | Join a trend on a pullback into low-volume areas created during the impulse move. | SINGLE | 1 | N | re-frame |
| CR-08 | When price enters a low-volume / no-resistance pocket, it moves rapidly through the pocket in one direction. | SINGLE | NEW | N | test |
| CR-09 | Classify the market into balance (range/accumulation) vs. trend and switch setup families accordingly. | SINGLE | 3 | N | re-frame |
| CR-10 | Acceptance beyond a level requires price to build a new sideways range / equilibrium there, not just quick spikes or a fixed bar count. | SINGLE | NEW | N | test |
| CR-11 | A new acceptance equilibrium is established only when another sideways phase emerges above or below the broken level. | SINGLE | 4 | Y L01 | re-code |
| CR-12 | High-volume nodes act as reaction magnets when price returns to them. | SINGLE | 4 | N | re-code |
| CR-13 | Order-flow exhaustion/absorption is valid only when it occurs at a strong HTF/session technical level. | SINGLE | NEW | N | test |
| CR-14 | Judge volume relative to when large participants are active (session / time-of-day baseline). | SINGLE | 1 | N | re-frame |
| CR-15 | Place the stop loss below the entire last sideways accumulation phase (or behind the support zone where the opposite move is expected), not tightly at ... | SINGLE | NEW | N | test |
| CR-16 | Place intraday order-flow stop just above/below the absorption candle / trapped participants. | SINGLE | NEW | N | test |
| CR-17 | Set profit target at the next high-liquidity cluster / HVN (or opposite boundary of the range). | SINGLE | 4 | N | re-code |
| CR-18 | When trading at highs without overhead liquidity references, project a 1:1 measured move of the prior momentum impulse leg as the target. | SINGLE | 2 | N | extract |
| CR-19 | Fast trend leaves a Market Profile single-print (unfair price) area that is only traded when returning first to a fair-value area with a predefined high-probability ... | SINGLE | 2 | N | extract |
| CR-20 | Require reward-to-risk ratio > 1.5 (and in intraday videos >= 2.0 to 2.5, or 1:16-1:19 on Fabio curve-low runners). | SINGLE | NEW | N | test |
| CR-21 | For swing trading (including 24/7 markets like Bitcoin), wait for daily closing prices rather than overtrading intraday noise. | SINGLE | 5 | N | re-frame |
| CR-22 | Do not fade or buy pullbacks into a Market Profile open-drive buying tail; it offers no support. | SINGLE | 2 | N | extract |
| CR-23 | Do not fade active institutional selling / forced flow; wait until order flow shows the move is over. | SINGLE | 1 | N | re-frame |
| CR-24 | Repeated absorption at stable high tape speed means the level is breaking (orders being eaten), so do not fade it—trade the breakout instead. | SINGLE | 4 | N | re-code |
| CR-25 | Higher-timeframe bias is read from whether weekly volume-profile POCs rise, hold or fall; code uses 1M candle colour, 20M SMA and weekly streaks | SINGLE | 4 | N | re-code |
| CR-26 | Cash-session traders must anchor Volume Profiles to the cash session, not 24-hour UTC days. | SINGLE | 5 | N | re-frame |
| CR-27 | Use time-based Market Profile (30-minute TPO periods, single prints, buying/selling tails, double distributions) alongside Volume Profile to judge acceptance and levels. | SINGLE | 2 | N | extract |
| CR-28 | Wait out the first 30 minutes of the New York session (and evaluate the opening range size) before taking trades. | SINGLE | 4 | N | re-code |
| CR-29 | The 30-minute Initial Balance (IVB) strategy relies on predictable opening behavior of US equities, where the extreme of the first 30 minutes gives directional value ... | SINGLE | 5 | N | re-frame |
| CR-30 | Execute on range bars (40 range or 80 range so NY-open volatility is not aggregated into one huge 1m bar) with a big-trade filter set ... | SINGLE | 4 | Y L07 | re-code |
| CR-31 | Enter breakouts/reclaims via stop orders (build by stop) or immediate market execution while the bar is moving, rather than waiting for bar close + 3-bar ... | SINGLE | 4 | N | re-code |
| CR-32 | Fabio moves the stop to break-even immediately (not even one candle in Is1HvdfQm5c [38:15]); Tom either does not trail a planned target (k0zm5NYn0IQ) or moves ... | SINGLE | NEW | Y L20 | test |
| CR-33 | Start with a partial position size to scale in as price moves in favor, and take partial profits at intermediate liquidity levels while letting a ... | SINGLE | NEW | N | test |
| CR-34 | Re-enter when the trade idea remains valid after a tight stop-out (k0zm5NYn0IQ), and stop trading for the day after 3 stop-losses (or if P&L drops ... | SINGLE | 4 | N | re-code |
| CR-35 | In Is1HvdfQm5c Fabio says he does not use order flow on Bitcoin (uses on-chain analysis), whereas in DyS79Eb92Ug ([1:48:37], [1:54:14]) he says crypto order-flow scalping ... | SINGLE | 5 | N | re-frame |

## Evidence

#### CR-02 SINGLE
> "you have a negative delta with a positive price action. That's a very clear divergence in market pressure. There was an effort from seller that is not having any follow through. And the 5-minute was about to close right over here and that was my signal for the entry."
**Source GPS: 9IliXww64uM | MIDDLE**

#### CR-06 SINGLE
> "And then it's just really nice to position yourself one or two ticks ahead of that position because at first the market always since many people and also algorithmic systems see that, the market usually moves away from it at first."
**Source GPS: 4P5WAxyPCis | BEGIN**

#### CR-09 SINGLE
> "Whether it's trend or balance because I have to use different setups there and that is absolutely crucial."
**Source GPS: Ld1dhjGdTCA | END**

#### CR-18 SINGLE
> "Alternatively, if we happen to be trading at all-time highs, we simply mirror the current momentum move to the upside to determine our next target."
**Source GPS: M7ompiwv5co | MIDDLE**

#### CR-20 SINGLE
> "And only if that is, for example, at least greater than 1.5 or so, then I have a really great strategy that will make me money."
**Source GPS: M7ompiwv5co | END**

#### CR-21 SINGLE
> "in swing trading, where we can simply wait for daily closing prices, we can trade much, much more patiently."
**Source GPS: M7ompiwv5co | END**

#### CR-25 SINGLE
> "The weekly profiles show me immediately if the V POX are rising, staying the same or even falling"
**Source GPS: Ld1dhjGdTCA | MIDDLE**

#### CR-26 SINGLE
> "You can't say, I only trade the cash session. But then refer to 24-hour profiles. Why? That's inherently quite meaningless."
**Source GPS: Of_wlv3xaZo | END**

#### CR-27 SINGLE
> "the price never actually stayed at this specific level for more than 30 minutes"
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

#### CR-28 SINGLE
> "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that."
**Source GPS: Of_wlv3xaZo | MIDDLE**

#### CR-29 SINGLE
> "On this strategy, the IVB, that is based on the fact that the nature of the US equities have predictable behavior during the opening, okay? And that the bottom of the first 30 minutes is giving a lot of value in the direction of the day"
**Source GPS: LQvv5xgy_ik | END**

#### CR-30 SINGLE
> "the big trades guys are 60 the filter it's on 60 and you know what one time frame that I'm loving recently that is based on the range is the 80 range"
**Source GPS: Is1HvdfQm5c | MIDDLE**

#### CR-34 SINGLE
> "if I reach a maximum of 3 stop loss either I lower the exposure but usually a stop for the day"
**Source GPS: Is1HvdfQm5c | MIDDLE**
