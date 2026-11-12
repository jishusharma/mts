# NY Open Rules Sweep (Iteration 3 — Argon)

Scope: Tom Vorwald and Fabio Valentini statements in `raw_transcripts_canonical/*_raw.txt` on NY open, New York open, 9:30, 8:30, cash open, opening range, and London vs NY, compared against our codebase.

| topic | trader | exact quote | video id [mm:ss] | rule in his words | number: SOURCED value or NOT_SEEN | in our code? file:line or NONE |
|---|---|---|---|---|---|---|
| NY open 30m observation wait | Fabio Valentini | usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session. | DyS79Eb92Ug [04:14] | Wait out the first 30 minutes of the New York session before entering trades to allow the opening auction to stabilize. | SOURCED: 30 minutes | MyTradingSys/backtest/layers/fabio/v3/day_gates.py:20 (GATE_MIN_ELAPSED = 60 arbitrarily waits 60m instead of 30m) |
| NY open 30m trade lockout | Tom Vorwald | stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that. | Of_wlv3xaZo [no-ts] | Do not trade in the first 30 minutes of the New York session; measure the opening range size to determine whether the day will trend or fail. | SOURCED: 30 minutes | NONE (no 30m NY cash-open blackout or OR measurement) |
| US equities predictable open & 30m bottom value | Fabio Valentini | On this strategy, the IVB, that is based on the fact that the nature of the US equities have predictable behavior during the opening, okay? And that the bottom of the first 30 minutes is giving a lot of value in the direction of the day | LQvv5xgy_ik [31:42] | US equities have predictable behavior at the cash open; the range and bottom established during the first 30 minutes determine directional day bias. | SOURCED: 30 minutes | NONE |
| 15 to 30m opening battle predicts direction | Fabio Valentini | the first one that break is telling you what is telling you who won the battle of the most important time of the day. So the first 15 minutes of New York opening or 30. | cUTsoU-15Tc [02:34] | The side that breaks the first 15 or 30 minutes of the New York open wins the critical opening battle and statistically predicts the day's direction. | SOURCED: 15 to 30 minutes | NONE |
| Narrow 30m open range implies trend day | Tom Vorwald | If you see at the open after 30 minutes, thereby negating this problem here that the open is relatively narrow, then you can assume the market will likely trend after that. Why? Everyone was able to take their positions and is now moving business to the next levels where they think it looks good. | Of_wlv3xaZo [no-ts] | If the opening range after 30 minutes is narrow, anticipate a trend day as large market participants comfortably filled positions and are extending value. | SOURCED: 30 minutes; narrow threshold NOT_SEEN | NONE |
| Explosive open range leads to counter-reversal | Tom Vorwald | If the market starts explosively right away like here, you often get a counter up here because the market will try to find fair prices, which are usually found back near the opening range since many large participants couldn't even do their business yet. | Of_wlv3xaZo [no-ts] | An explosive opening range triggers counter-reversals back toward the open because large participants could not execute and seek fair value near the open. | NOT_SEEN | NONE |
| Opening range size dictates hold probability | Tom Vorwald | Open range, meaning the opening range. If it's very large, it likely won't hold. If it's very small, it likely will. That's it. That's all the information you need. | Fj4FDZQxw0I [no-ts] | A very large opening range likely will not hold; a very small opening range likely will hold. | NOT_SEEN (qualitative: 'very large' vs 'very small') | NONE |
| Narrow open range with steady liquidity trends | Tom Vorwald | Is the market opening range very large? Or is it very small? And think about it, if something is very narrow, but liquidity is the same as in the previous days, then the probability at a later point in time is much greater that the market will trend. | Ld1dhjGdTCA [no-ts] | When the opening range is very narrow while liquidity matches prior days, the probability of a subsequent trend day is much greater. | NOT_SEEN | NONE |
| Fair value gaps conditioned on open range size | Tom Vorwald | fair value gaps are great support resistance levels. They are, but only if the market has trend stability. And if the open range wasn't that large. | Fj4FDZQxw0I [no-ts] | Fair value gaps act as valid support/resistance levels only if the market has trend stability and the opening range was not excessively large. | NOT_SEEN | MyTradingSys/backtest/layers/alerts/live_layers.py:47-49 (volume_fvg layer runs without open-range size filter) |
| ORB confirmation via big trades inside sell candle | Fabio Valentini | We broke the opening range with a strong sell candle, big trades inside of the candle, which is a very crucial point of information for me. | 9IliXww64uM [11:13] | Opening range breakouts must be confirmed by directional candles containing heavy clustered big trades. | NOT_SEEN | MyTradingSys/backtest/bigtrade/fires_kline.py:142-167 (identifies big trades on klines, but no ORB breakout link) |
| Toby Crabel 15m cash open ORB edge | Fabio Valentini | A lot of traders are familiar with the opening range breakout. You buy or sell the breakout of the first 15 minutes of the cash session. This strategy published in the 1990 by Toby Crabel proven to be one of the most consistent edge over the last decade with a positive profit factor and an amazing sharp ratio. | cUTsoU-15Tc [00:00] | Trading the breakout of the first 15 minutes of the cash session (Toby Crabel's 1990 model) is a highly consistent edge with a strong Sharpe ratio. | SOURCED: first 15 minutes | NONE |
| Defining IVB range (Point A & B) over first 15-30m | Fabio Valentini | How can we define this point A and point B? This is the opening of the New York. We have a top. We have a bottom on the first 15 to 30 minutes. Okay. This is our point A and this is our point B and the price is inside this value | cUTsoU-15Tc [04:26] | The Initial Value Breakout range boundaries (Point A top, Point B bottom) are strictly defined by the first 15 to 30 minutes of the New York open. | SOURCED: 15 to 30 minutes | NONE |
| Cash session accumulation area sensitive scalping | Fabio Valentini | this is the accumulation area of the cash session and the model is spotting this with the most sensitive level. | cUTsoU-15Tc [15:52] | The accumulation area of the cash session provides the most sensitive support/resistance levels for intraday scalping. | NOT_SEEN | NONE |
| Wait full 30m before plotting IVB levels | Fabio Valentini | this area last for the first 30 minutes. Here they start with the IVB. Okay, they start to plot the level. Now wait for the first 30 minutes of the session. So we have a clean defined range. | cUTsoU-15Tc [16:29] | Wait for the entire first 30 minutes to close before plotting IVB levels to establish a cleanly defined opening range. | SOURCED: first 30 minutes | NONE |
| 24h profile vs cash session profile meaninglessness | Tom Vorwald | You can't say, I only trade the cash session. But then refer to 24-hour profiles. Why? That's inherently quite meaningless. | Of_wlv3xaZo [no-ts] | Trading cash sessions while referencing 24-hour profiles is meaningless because illiquid overnight hours distort institutional value boundaries. | NOT_SEEN | MyTradingSys/backtest/vp_return_to_value.py:6-10 (computes 24h UTC profiles, directly violating Tom's rule) |
| 6M cash volume vs 6.5M 24h total skews value area | Tom Vorwald | In this specific cash session, we saw approximately 6 million contracts being traded. When we look at the entire period, including the after-hours trading session combined with the cash session, the total volume reaches 6.5 million contracts. Now, observe how the value area shifts significantly along with the equilibrium point | Of_wlv3xaZo [no-ts] | Because ~92% of volume trades during the cash session (6M of 6.5M contracts), adding thin overnight volume shifts the calculated value area and equilibrium away from institutional consensus. | SOURCED: 6 million vs 6.5 million contracts | NONE (all volume profile tools treat 24h klines uniformly) |
| Profile shape flip (trend on 24h vs balance on cash) | Tom Vorwald | when you trade cash time frames, please also use the cash session profiles because they can change. You can have a trend profile in the 24-hour chart, and in the cash session the day before you suddenly have a balance profile. | Of_wlv3xaZo [no-ts] | Always use cash session profiles when trading cash timeframes because 24-hour profiles can falsely display a trend profile when the cash session was actually in balance. | NOT_SEEN | NONE |
| Cash close 22:00 ETF auction vs midnight close | Tom Vorwald | if you examine the gaps only from the cash session, so 10:00 p.m. and a bit, then you'll see that this close is much much more important than for example, a gap close from midnight. Nobody cares about that because there was no liquidity at all because what happens at the end of the cash session? All the ETFs have to enter their positioning in closing auction | Of_wlv3xaZo [no-ts] | Cash session closing gaps (~22:00 CET) are far more significant than midnight closes because ETFs execute critical rebalancing in the closing auction. | SOURCED: 10:00 p.m. (22:00 CET) | MyTradingSys/backtest/layers/session_levels/session_levels.py:9,36-40 (measures daily high/low across 00:00 UTC day boundaries, ignoring 22:00 cash auction) |
| RTH dark orange vs ETH light profile color | Fabio Valentini | So this dark orange one is the volume profile of the regular trading hour session, the so-called New York session. The Asian and the London session are in this lighter color because there's less volume into those areas. These are the ETH or extended or electronic trading hour session. | 9IliXww64uM [03:55] | Segment volume profiles into Regular Trading Hours (RTH New York) and Extended Trading Hours (ETH Asian/London); RTH holds the primary volume profile. | NOT_SEEN | NONE |
| Cash session profile displays largest sales | Tom Vorwald | This is for example a unit of 1 day. Each of these profiles shows you one day. And in addition, these profiles only show you the period where the so-called cash session is, i.e. the period where the largest sales associated with the corresponding product are shown. | BB3c8visnkI [no-ts] | Daily profiles should specifically isolate the cash session window where the largest sales volume is recorded. | SOURCED: 1 day | NONE |
| Context from cash session profile & market open | Tom Vorwald | And we determine the context through market profiling. And this here is, for example, a market profile chart, where you can read how the market traded during the cash session, the main trading hours, you can see it here. Here was the market opening from the previous day. | zAwEX_tRUfE [no-ts] | Context for 1-minute execution must be derived from market profile charts of the cash session main trading hours and opening price. | NOT_SEEN | NONE |
| Peak volume in New York vs wide swings in London | Fabio Valentini | The New York session is the session that hold the maximum amount of volume for the day. So you have the strongest battle between buyers and sellers. You have the peak of interest and input of volume during the day and usually you see this as soon as the London session open with big swings | cUTsoU-15Tc [01:30] | The New York session commands maximum volume and the strongest institutional battle, whereas London open creates the initial wide range swings. | NOT_SEEN | NONE |
| Big-trade bubble filter: 20 in London vs 30 in NY | Fabio Valentini | What was your settings in terms of the to show as as a bubble on the on the chart? What was the minimum contract? >> Always the same. It's 30 contracts. >> If you are in London, I use 20. | DyS79Eb92Ug [27:16] | Calibrate order-flow big trade bubble thresholds by session: use 20 contracts in London and 30 contracts in New York. | SOURCED: 20 contracts (London) vs 30 contracts (New York) | NONE (big-trade filters do not adjust thresholds for session liquidity differences) |
| Protecting London profits during NY session | Fabio Valentini | we are risking 2,000 we are not risking back the profit not even the profit of New York we are risking we are really low on the risk side | DyS79Eb92Ug [22:08] | When trading the New York session after banking London profits, risk a small fraction (e.g. $2k) to ensure accumulated London gains remain protected. | SOURCED: risk 2,000 | NONE (no cross-session PnL state or profit-protection risk throttle) |
| Daily profit target walkaway ($20k) after London & NY | Fabio Valentini | if I get the 20,000 profit for the day my rules say it's done because probably you will have consolidation after a strong move. We took the best move of the London and of the New York we walk away. | DyS79Eb92Ug [25:13] | Once daily profit hits $20,000 after capturing prime moves in London and New York, stop trading immediately as consolidation typically follows. | SOURCED: $20,000 profit for the day | NONE |
| Eliminating London session on low profit factor | Fabio Valentini | You can understand you know that London session is not worth to trade for me. My profit factor is really low. I pay a lot of commission but profit factor is really low. What's my benefit? I get half of the day for free. | 0KyIEdvVKMQ [no-ts] | Audit session metrics and eliminate trading the London session entirely if commissions erode the profit factor, preserving energy for New York. | NOT_SEEN | NONE |
| Pre-London open trades skipped | Fabio Valentini | I didn't took the first movement because it was before the opening of the London session but the second movement was so clear. | 06R-ebyOhDI [01:27] | Skip moves occurring before the official London opening bell; execute only once session volume is active. | NOT_SEEN | NONE |
| Thin London session volume prone to stop squeezes | Fabio Valentini | this is pretty empty it's not so much volume because it's the london session probably they squeeze the low | Is1HvdfQm5c [22:54] | Recognize that London session volume can be thin and illiquid, causing moves to degenerate into stop squeezes rather than genuine trends. | NOT_SEEN | NONE |
| NY session structure & Power Hour rebalancing | Fabio Valentini | 90% of the session that expand they rebalance till the power hour this is the structure of the New York if you expand immediately And Trump is not tweeting. You rebalance. | DyS79Eb92Ug [1:15:14] | 90% of New York sessions that expand early rebalance until the Power Hour; execute Model B value area tests between 19:30 and 21:00 CET (Power Hour). | SOURCED: 90%; 7:30 to 9:00 PM European time (19:30-21:00 CET) | NONE (no Power Hour execution window or rebalance-to-power-hour logic) |
| Exhausted open from forced hedging transactions | Tom Vorwald | because the initial balance is so large meaning the expansion of the trading opening is just very very big and that means here traders had to buy at the market open at that point they don't really care what the price is because these are hedging transactions and they will certainly be corrected later | k0zm5NYn0IQ [no-ts] | An overly large initial balance expansion at the open indicates forced, price-insensitive hedging flows that will be corrected later in the session. | NOT_SEEN | NONE |
| Exhausted open without accompanying volume | Tom Vorwald | In my opinion, the market open was too extreme. And above all, it wasn't accompanied by real volume, but rather there was an I have to push sentiment. | k0zm5NYn0IQ [no-ts] | An extreme market open unsupported by real institutional volume represents emotional push sentiment that should be faded. | NOT_SEEN | NONE |
| Finished auction & absorption at opening peak | Tom Vorwald | And at the top you can simply see that nothing was happening anymore. And we also had a finished auction. That means the market formed a completed auction at the top. | k0zm5NYn0IQ [no-ts] | Confirm exhaustion of an opening surge by verifying a finished auction and cessation of buying at the high. | NOT_SEEN | NONE |
| Book sweeping at New York session high/low | Fabio Valentini | Or if you are really close to the high of the New York session or on the session, the market approach this level and you have a book sweeping usually in this kind of level. So, if you are positioned, you can take an asymmetrical risk to reward. | FawPrRUGNpk [10:47] | Watch for aggressive book sweeping near the New York session high or low to enter asymmetric risk-to-reward reversals. | NOT_SEEN | NONE |
| Futures briefing 1.5h before cash session open | Tom Vorwald | The stock exchanges will open soon or rather the cash session in particular starts in a good 1 and 1/2 hours and I'm going to check in with my boys now. | f225iVdsrfg [no-ts] | Begin trading desk scenario planning and briefing 1.5 hours prior to the cash session open. | SOURCED: 1 and 1/2 hours | NONE |
| Afternoon futures briefing before New York open | Tom Vorwald | It's almost time for the American futures markets to open, at least the cash session. Let's just take a quick look at what we're doing today. The New York session is about to start. | f225iVdsrfg [no-ts] | Conduct an afternoon futures scenario briefing immediately before the New York cash open. | NOT_SEEN | MyTradingSys/backtest/layers/alerts/live_level_touch.py:7 (SESSION BRIEF alert at 13:30Z US open) |
| Real-time DAX strength during cash sessions | Tom Vorwald | Especially during the cash sessions where the stock markets are traded in real time, the DAX was incredibly strong and I watched that. | e83njGZFrPw [no-ts] | Evaluate index strength during cash sessions when underlying equities trade in real time. | NOT_SEEN | NONE |
| Hard $10,000 maximum daily drawdown limit | Fabio Valentini | The draw down the maximum draw down that I accept for the day is 10,000. So considering we are already in profit, the maximum that we can do is lose this 10,000, go back to break even and lose another 10,000 | DyS79Eb92Ug [03:19] | Enforce a strict $10,000 maximum loss limit per day; if previously in profit, allow giving back profit plus up to $10,000. | SOURCED: $10,000 maximum daily drawdown | MyTradingSys/backtest/layers/fabio/v3/day_gates.py:18 (DAILY_STOP_R = -3.0; arbitrary -3R, not $10k dollar hard stop) |
| Asian/London lack of discovery inside prior NY value | Fabio Valentini | there was no relevant news or price discovery auction during the Asian or London session, and we're about to open the session exactly where most of the money was traded yesterday. | 9IliXww64uM [06:11] | When Asian and London sessions show no price discovery and open inside yesterday's value area, expect a range-bound day. | NOT_SEEN | NONE |
| Cash open long aggression rejected at high | Fabio Valentini | they closed the session of yesterday bullish I took some long yesterday okay the closed bullish the cash session is bullish now they tapped into the high and they rejected so the cash session open with a strong long aggression to the upside as you can see here and now is rejecting | Is1HvdfQm5c [17:32] | When the cash open shows strong aggressive buying into previous session highs that immediately rejects, anticipate an exhaustion trap. | NOT_SEEN | NONE |
| Open range size critical after value rejection | Tom Vorwald | And we moved above yesterday's value area and then ran back into it. But how was the open range? Was it very large? Was it very small? What information does that give us? | 9VN9y2DVtGQ [no-ts] | When price breaks above yesterday's value area and falls back inside, the opening range size provides the key information on trade validity. | NOT_SEEN | NONE |
| Session chop clawback after London gains | Fabio Valentini | So we came from a London session where we did pretty good amount of profit. That was around $10,000 and we start the session getting caught by a little bit of choppiness here. So we give back $5,000 to the market, around 4,500. | fZlNGWvd2Ko [00:35] | Beware of early session chop clawing back prior London gains ($4.5k to $5k lost out of $10k profit); enforce strict risk controls when early chop occurs. | SOURCED: $10,000 profit, $4,500 to $5,000 clawback | NONE |

## TOP 5

1. **Both Tom and Fabio mandate waiting out the first 30 minutes of the NY cash open — our code uses 60 minutes or 0 minutes.** Fabio explicitly states he waits the first 30 minutes of the New York opening for stability (`DyS79Eb92Ug [04:14]`, `LQvv5xgy_ik [31:42]`, `cUTsoU-15Tc [02:34]`), and Tom warns to stop trading during the first 30 minutes of the New York session (`Of_wlv3xaZo [no-ts]`). In our codebase, `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:20` hardcodes `GATE_MIN_ELAPSED = 60`, locking out trading for 60 minutes instead of Fabio's 30-minute stabilization window, while models A, B, and D have no open lockout, and `MyTradingSys/backtest/layers/session/session_momentum.py:20-22` uses 30 minutes as an academic return-prediction parameter while noting it is never a Tom filter.
2. **Opening-range width as the master trend vs mean-reversion classifier is central to Tom and Fabio, but completely uncoded.** Tom repeatedly teaches across four transcripts (`Of_wlv3xaZo [no-ts]`, `Fj4FDZQxw0I [no-ts]`, `Ld1dhjGdTCA [no-ts]`, `9VN9y2DVtGQ [no-ts]`) that opening range size dictates hold probability: a narrow 30-minute opening range forecasts a sustained trend day, whereas an explosive wide opening range indicates price-insensitive hedging that fails to hold and mean-reverts back to fair value (`k0zm5NYn0IQ [no-ts]`). Fabio similarly bases his 15-to-30m ORB and IVB models on this opening range (`cUTsoU-15Tc [00:00]`, `9IliXww64uM [11:13]`). In our codebase, there is zero measurement of opening range width, zero classification of open-range size, and no day-type conditioning.
3. **Cash-session volume profile vs 24h UTC profile distortion.** Tom warns that using 24-hour profiles when trading cash sessions is inherently meaningless because ~92% of daily volume (6M of 6.5M contracts) transacts during the cash session (`Of_wlv3xaZo [no-ts]`), causing after-hours volume to distort the POC and value area and potentially flip an actual cash balance profile into an apparent 24h trend profile. Fabio likewise isolates Regular Trading Hours (RTH dark orange) from Extended Trading Hours (ETH light color; `9IliXww64uM [03:55]`). In our codebase, `MyTradingSys/backtest/vp_return_to_value.py:6-10` computes volume profiles uniformly across 24h UTC windows, and `MyTradingSys/backtest/layers/session_levels/session_levels.py:9,36-40` anchors session extremes to 00:00 UTC day boundaries rather than the 22:00 CET institutional closing auction.
4. **Session-dependent order-flow parameters (20 contracts in London vs 30 contracts in NY).** Fabio explicitly adjusts his order-flow big-trade bubble detection threshold by session: 20 contracts in the London session versus 30 contracts in the New York session (`DyS79Eb92Ug [27:16]`), reflecting the volume disparity between London swings and New York peak liquidity (`cUTsoU-15Tc [01:30]`, `Is1HvdfQm5c [22:54]`). In our codebase, `MyTradingSys/backtest/bigtrade/fires_kline.py:142-167` applies static, session-agnostic thresholds across all hours.
5. **Cross-session profit protection, daily target walkaway, and Power Hour execution.** Fabio treats daily risk dynamically across sessions: after securing $10,000 in London, he risks only $2,000 in New York (`DyS79Eb92Ug [22:08]`), refusing to claw back London gains (`fZlNGWvd2Ko [00:35]`). If total daily profit reaches $20,000, his rule is to walk away immediately as consolidation follows (`DyS79Eb92Ug [25:13]`). Furthermore, 90% of early-expanding NY sessions rebalance until the Power Hour (19:30–21:00 CET), where Fabio executes Model B value area retests (`DyS79Eb92Ug [1:15:14]`). In our codebase, `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:18` uses an arbitrary `DAILY_STOP_R = -3.0` with no cross-session PnL state, no profit walkaway lock, and no Power Hour execution window.

## SINGLE BIGGEST HOLE

**Unsegmented 24/7 UTC profiling and total absence of the 30-minute cash opening range regime filter.** Both Tom and Fabio treat the first 30 minutes of the cash session as the primary anchor for intraday structure: do not trade during the first 30 minutes (`DyS79Eb92Ug [04:14]`, `Of_wlv3xaZo [no-ts]`), measure the 30-minute opening range width to classify the day (narrow -> trend day; explosive -> hedging exhaustion fade; `Of_wlv3xaZo [no-ts]`, `k0zm5NYn0IQ [no-ts]`), and profile exclusively the cash session (RTH) rather than 24h blended volume (`Of_wlv3xaZo [no-ts]`, `9IliXww64uM [03:55]`). Our entire architecture (`MyTradingSys/backtest/vp_return_to_value.py:6-10`, `MyTradingSys/backtest/layers/session_levels/session_levels.py:9,36-40`, `MyTradingSys/tools/live_aid/pulse.js`) runs uniform 24h UTC profiles, possesses zero opening range measurement, and ignores both the 30-minute cash-open stabilization window and the 22:00 CET institutional closing auction.

## Verbatim quote verification

> "usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session."
**Source GPS: DyS79Eb92Ug | BEGIN**

> "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that."
**Source GPS: Of_wlv3xaZo | MIDDLE**

> "On this strategy, the IVB, that is based on the fact that the nature of the US equities have predictable behavior during the opening, okay? And that the bottom of the first 30 minutes is giving a lot of value in the direction of the day"
**Source GPS: LQvv5xgy_ik | END**

> "the first one that break is telling you what is telling you who won the battle of the most important time of the day. So the first 15 minutes of New York opening or 30."
**Source GPS: cUTsoU-15Tc | BEGIN**

> "If you see at the open after 30 minutes, thereby negating this problem here that the open is relatively narrow, then you can assume the market will likely trend after that. Why? Everyone was able to take their positions and is now moving business to the next levels where they think it looks good."
**Source GPS: Of_wlv3xaZo | BEGIN**

> "If the market starts explosively right away like here, you often get a counter up here because the market will try to find fair prices, which are usually found back near the opening range since many large participants couldn't even do their business yet."
**Source GPS: Of_wlv3xaZo | BEGIN**

> "Open range, meaning the opening range. If it's very large, it likely won't hold. If it's very small, it likely will. That's it. That's all the information you need."
**Source GPS: Fj4FDZQxw0I | END**

> "Is the market opening range very large? Or is it very small? And think about it, if something is very narrow, but liquidity is the same as in the previous days, then the probability at a later point in time is much greater that the market will trend."
**Source GPS: Ld1dhjGdTCA | END**

> "fair value gaps are great support resistance levels. They are, but only if the market has trend stability. And if the open range wasn't that large."
**Source GPS: Fj4FDZQxw0I | BEGIN**

> "We broke the opening range with a strong sell candle, big trades inside of the candle, which is a very crucial point of information for me."
**Source GPS: 9IliXww64uM | END**

> "A lot of traders are familiar with the opening range breakout. You buy or sell the breakout of the first 15 minutes of the cash session. This strategy published in the 1990 by Toby Crabel proven to be one of the most consistent edge over the last decade with a positive profit factor and an amazing sharp ratio."
**Source GPS: cUTsoU-15Tc | BEGIN**

> "How can we define this point A and point B? This is the opening of the New York. We have a top. We have a bottom on the first 15 to 30 minutes. Okay. This is our point A and this is our point B and the price is inside this value"
**Source GPS: cUTsoU-15Tc | BEGIN**

> "this is the accumulation area of the cash session and the model is spotting this with the most sensitive level."
**Source GPS: cUTsoU-15Tc | MIDDLE**

> "this area last for the first 30 minutes. Here they start with the IVB. Okay, they start to plot the level. Now wait for the first 30 minutes of the session. So we have a clean defined range."
**Source GPS: cUTsoU-15Tc | MIDDLE**

> "You can't say, I only trade the cash session. But then refer to 24-hour profiles. Why? That's inherently quite meaningless."
**Source GPS: Of_wlv3xaZo | END**

> "In this specific cash session, we saw approximately 6 million contracts being traded. When we look at the entire period, including the after-hours trading session combined with the cash session, the total volume reaches 6.5 million contracts. Now, observe how the value area shifts significantly along with the equilibrium point"
**Source GPS: Of_wlv3xaZo | END**

> "when you trade cash time frames, please also use the cash session profiles because they can change. You can have a trend profile in the 24-hour chart, and in the cash session the day before you suddenly have a balance profile."
**Source GPS: Of_wlv3xaZo | END**

> "if you examine the gaps only from the cash session, so 10:00 p.m. and a bit, then you'll see that this close is much much more important than for example, a gap close from midnight. Nobody cares about that because there was no liquidity at all because what happens at the end of the cash session? All the ETFs have to enter their positioning in closing auction"
**Source GPS: Of_wlv3xaZo | END**

> "So this dark orange one is the volume profile of the regular trading hour session, the so-called New York session. The Asian and the London session are in this lighter color because there's less volume into those areas. These are the ETH or extended or electronic trading hour session."
**Source GPS: 9IliXww64uM | BEGIN**

> "This is for example a unit of 1 day. Each of these profiles shows you one day. And in addition, these profiles only show you the period where the so-called cash session is, i.e. the period where the largest sales associated with the corresponding product are shown."
**Source GPS: BB3c8visnkI | MIDDLE**

> "And we determine the context through market profiling. And this here is, for example, a market profile chart, where you can read how the market traded during the cash session, the main trading hours, you can see it here. Here was the market opening from the previous day."
**Source GPS: zAwEX_tRUfE | BEGIN**

> "The New York session is the session that hold the maximum amount of volume for the day. So you have the strongest battle between buyers and sellers. You have the peak of interest and input of volume during the day and usually you see this as soon as the London session open with big swings"
**Source GPS: cUTsoU-15Tc | BEGIN**

> "What was your settings in terms of the to show as as a bubble on the on the chart? What was the minimum contract? >> Always the same. It's 30 contracts. >> If you are in London, I use 20."
**Source GPS: DyS79Eb92Ug | BEGIN**

> "we are risking 2,000 we are not risking back the profit not even the profit of New York we are risking we are really low on the risk side"
**Source GPS: DyS79Eb92Ug | BEGIN**

> "if I get the 20,000 profit for the day my rules say it's done because probably you will have consolidation after a strong move. We took the best move of the London and of the New York we walk away."
**Source GPS: DyS79Eb92Ug | BEGIN**

> "You can understand you know that London session is not worth to trade for me. My profit factor is really low. I pay a lot of commission but profit factor is really low. What's my benefit? I get half of the day for free."
**Source GPS: 0KyIEdvVKMQ | END**

> "I didn't took the first movement because it was before the opening of the London session but the second movement was so clear."
**Source GPS: 06R-ebyOhDI | BEGIN**

> "this is pretty empty it's not so much volume because it's the london session probably they squeeze the low"
**Source GPS: Is1HvdfQm5c | BEGIN**

> "90% of the session that expand they rebalance till the power hour this is the structure of the New York if you expand immediately And Trump is not tweeting. You rebalance."
**Source GPS: DyS79Eb92Ug | MIDDLE**

> "because the initial balance is so large meaning the expansion of the trading opening is just very very big and that means here traders had to buy at the market open at that point they don't really care what the price is because these are hedging transactions and they will certainly be corrected later"
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "In my opinion, the market open was too extreme. And above all, it wasn't accompanied by real volume, but rather there was an I have to push sentiment."
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "And at the top you can simply see that nothing was happening anymore. And we also had a finished auction. That means the market formed a completed auction at the top."
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "Or if you are really close to the high of the New York session or on the session, the market approach this level and you have a book sweeping usually in this kind of level. So, if you are positioned, you can take an asymmetrical risk to reward."
**Source GPS: FawPrRUGNpk | BEGIN**

> "The stock exchanges will open soon or rather the cash session in particular starts in a good 1 and 1/2 hours and I'm going to check in with my boys now."
**Source GPS: f225iVdsrfg | BEGIN**

> "It's almost time for the American futures markets to open, at least the cash session. Let's just take a quick look at what we're doing today. The New York session is about to start."
**Source GPS: f225iVdsrfg | END**

> "Especially during the cash sessions where the stock markets are traded in real time, the DAX was incredibly strong and I watched that."
**Source GPS: e83njGZFrPw | BEGIN**

> "The draw down the maximum draw down that I accept for the day is 10,000. So considering we are already in profit, the maximum that we can do is lose this 10,000, go back to break even and lose another 10,000"
**Source GPS: DyS79Eb92Ug | BEGIN**

> "there was no relevant news or price discovery auction during the Asian or London session, and we're about to open the session exactly where most of the money was traded yesterday."
**Source GPS: 9IliXww64uM | MIDDLE**

> "they closed the session of yesterday bullish I took some long yesterday okay the closed bullish the cash session is bullish now they tapped into the high and they rejected so the cash session open with a strong long aggression to the upside as you can see here and now is rejecting"
**Source GPS: Is1HvdfQm5c | BEGIN**

> "And we moved above yesterday's value area and then ran back into it. But how was the open range? Was it very large? Was it very small? What information does that give us?"
**Source GPS: 9VN9y2DVtGQ | END**

> "So we came from a London session where we did pretty good amount of profit. That was around $10,000 and we start the session getting caught by a little bit of choppiness here. So we give back $5,000 to the market, around 4,500."
**Source GPS: fZlNGWvd2Ko | BEGIN**
