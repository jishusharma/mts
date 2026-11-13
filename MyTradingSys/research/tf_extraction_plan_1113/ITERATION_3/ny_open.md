# Iteration 3 merge: ny_open

Sources: flash + argon. Rows 49: AGREED 9, SINGLE 39, CONFLICT 1, UNVERIFIED 0 (rows needing a quote that no transcript match supported). Verified quotes below: 30.
Pattern, ledger and fix columns are assigned by rule from the source rows (code column, numbers, transfer words); the ledger column matches video id plus two shared content words. First-pass labels, not a re-read. Rows paired across models by same video id plus quote or rule word overlap.

## Items

| id | item | model verdict | pattern | in ANSWER_LEDGER? | fix type |
|---|---|---|---|---|---|
| NY-01 | Wait out the first 30 minutes of the New York session before entering trades to allow the opening auction to stabilize. | AGREED | 4 | N | re-code |
| NY-02 | Do not trade in the first 30 minutes of the New York session; measure the opening range size to determine whether the day will trend ... | AGREED | 2 | N | extract |
| NY-03 | US equities have predictable behavior at the cash open; the range and bottom established during the first 30 minutes determine directional day bias. | SINGLE | 2 | N | extract |
| NY-04 | The side that breaks the first 15 or 30 minutes of the New York open wins the critical opening battle and statistically predicts the day's ... | AGREED | 2 | Y L12 | extract |
| NY-05 | If the opening range after 30 minutes is narrow, anticipate a trend day as large market participants comfortably filled positions and are extending value. | AGREED | 2 | N | extract |
| NY-06 | An explosive opening range triggers counter-reversals back toward the open because large participants could not execute and seek fair value near the open. | SINGLE | 2 | N | extract |
| NY-07 | A very large opening range likely will not hold; a very small opening range likely will hold. | AGREED | 2 | N | extract |
| NY-08 | When the opening range is very narrow while liquidity matches prior days, the probability of a subsequent trend day is much greater. | SINGLE | 2 | N | extract |
| NY-09 | Fair value gaps act as valid support/resistance levels only if the market has trend stability and the opening range was not excessively large. | SINGLE | NEW | N | test |
| NY-10 | Opening range breakouts must be confirmed by directional candles containing heavy clustered big trades. | SINGLE | 4 | N | re-code |
| NY-11 | Trading the breakout of the first 15 minutes of the cash session (Toby Crabel's 1990 model) is a highly consistent edge with a strong Sharpe ... | SINGLE | 5 | Y L12 | re-frame |
| NY-12 | Opening-range window for the IVB/ORB: Argon says 15 to 30 minutes, Flash says 15, 30 or 60 minutes | CONFLICT | 1 | Y L12 | extract |
| NY-13 | The accumulation area of the cash session provides the most sensitive support/resistance levels for intraday scalping. | SINGLE | 5 | N | re-frame |
| NY-14 | Wait for the entire first 30 minutes to close before plotting IVB levels to establish a cleanly defined opening range. | SINGLE | 2 | Y L12 | extract |
| NY-15 | Trading cash sessions while referencing 24-hour profiles is meaningless because illiquid overnight hours distort institutional value boundaries. | SINGLE | 5 | N | re-frame |
| NY-16 | Because ~92% of volume trades during the cash session (6M of 6.5M contracts), adding thin overnight volume shifts the calculated value area and equilibrium away ... | SINGLE | 5 | N | re-frame |
| NY-17 | Always use cash session profiles when trading cash timeframes because 24-hour profiles can falsely display a trend profile when the cash session was actually in ... | SINGLE | 5 | N | re-frame |
| NY-18 | Cash session closing gaps (~22:00 CET) are far more significant than midnight closes because ETFs execute critical rebalancing in the closing auction. | SINGLE | 5 | N | re-frame |
| NY-19 | Segment volume profiles into Regular Trading Hours (RTH New York) and Extended Trading Hours (ETH Asian/London); RTH holds the primary volume profile. | AGREED | 2 | N | extract |
| NY-20 | Daily profiles should specifically isolate the cash session window where the largest sales volume is recorded. | SINGLE | 5 | Y L13 | re-frame |
| NY-21 | Context for 1-minute execution must be derived from market profile charts of the cash session main trading hours and opening price. | SINGLE | 5 | N | re-frame |
| NY-22 | The New York session commands maximum volume and the strongest institutional battle, whereas London open creates the initial wide range swings. | SINGLE | 2 | Y L12 | extract |
| NY-23 | Calibrate order-flow big trade bubble thresholds by session: use 20 contracts in London and 30 contracts in New York. | AGREED | 2 | N | extract |
| NY-24 | When trading the New York session after banking London profits, risk a small fraction (e.g. $2k) to ensure accumulated London gains remain protected. | SINGLE | 2 | N | extract |
| NY-25 | Once daily profit hits $20,000 after capturing prime moves in London and New York, stop trading immediately as consolidation typically follows. | SINGLE | 2 | N | extract |
| NY-26 | Audit session metrics and eliminate trading the London session entirely if commissions erode the profit factor, preserving energy for New York. | AGREED | 2 | N | extract |
| NY-27 | Skip moves occurring before the official London opening bell; execute only once session volume is active. | SINGLE | 2 | Y L10 | extract |
| NY-28 | Recognize that London session volume can be thin and illiquid, causing moves to degenerate into stop squeezes rather than genuine trends. | SINGLE | 2 | N | extract |
| NY-29 | 90% of New York sessions that expand early rebalance until the Power Hour; execute Model B value area tests between 19:30 and 21:00 CET (Power ... | SINGLE | 2 | N | extract |
| NY-30 | An overly large initial balance expansion at the open indicates forced, price-insensitive hedging flows that will be corrected later in the session. | SINGLE | 2 | N | extract |
| NY-31 | An extreme market open unsupported by real institutional volume represents emotional push sentiment that should be faded. | SINGLE | 2 | N | extract |
| NY-32 | Confirm exhaustion of an opening surge by verifying a finished auction and cessation of buying at the high. | SINGLE | 2 | N | extract |
| NY-33 | Watch for aggressive book sweeping near the New York session high or low to enter asymmetric risk-to-reward reversals. | SINGLE | 2 | N | extract |
| NY-34 | Begin trading desk scenario planning and briefing 1.5 hours prior to the cash session open. | SINGLE | 5 | N | re-frame |
| NY-35 | Conduct an afternoon futures scenario briefing immediately before the New York cash open. | SINGLE | NEW | N | test |
| NY-36 | Evaluate index strength during cash sessions when underlying equities trade in real time. | SINGLE | 5 | N | re-frame |
| NY-37 | Enforce a strict $10,000 maximum loss limit per day; if previously in profit, allow giving back profit plus up to $10,000. | SINGLE | NEW | N | test |
| NY-38 | When Asian and London sessions show no price discovery and open inside yesterday's value area, expect a range-bound day. | AGREED | 2 | N | extract |
| NY-39 | When the cash open shows strong aggressive buying into previous session highs that immediately rejects, anticipate an exhaustion trap. | SINGLE | 2 | N | extract |
| NY-40 | When price breaks above yesterday's value area and falls back inside, the opening range size provides the key information on trade validity. | SINGLE | 2 | N | extract |
| NY-41 | Beware of early session chop clawing back prior London gains ($4.5k to $5k lost out of $10k profit); enforce strict risk controls when early chop ... | SINGLE | 2 | N | extract |
| NY-42 | Statistical excursion model gives 65-70% probability of reaching TP1 after an ORB/IVB breakout. | SINGLE | 2 | N | extract |
| NY-43 | Initial balance = high and low established in the first 30 minutes of regular cash trading. | SINGLE | NEW | N | test |
| NY-44 | Blind 30-min Nasdaq ORB at 1:1 RR shows a 13.5% skew over a coin flip without order-flow filtering. | SINGLE | 4 | N | re-code |
| NY-45 | Under the ORB model, the opening range low is not touched again 80% of the time after breakout. | SINGLE | 2 | N | extract |
| NY-46 | Switch from 1-minute candles to a 40-range chart at the NY open so fast candles do not hide intra-bar order flow. | SINGLE | 4 | N | re-code |
| NY-47 | US cash session opens at 15:30 CET (9:30 ET), when big money enters US indices (S&P 500). | SINGLE | 5 | N | re-frame |
| NY-48 | 8:30 ET is the macro news window before the 9:30 ET equity cash open. | SINGLE | 2 | N | extract |
| NY-49 | For US indices, trade only the NY session and build profiles from the cash (RTH) session only, excluding London. | SINGLE | NEW | N | test |

## Evidence

#### NY-01 AGREED
> "usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session."
**Source GPS: DyS79Eb92Ug | BEGIN**

#### NY-02 AGREED
> "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that."
**Source GPS: Of_wlv3xaZo | MIDDLE**

#### NY-03 SINGLE
> "On this strategy, the IVB, that is based on the fact that the nature of the US equities have predictable behavior during the opening, okay? And that the bottom of the first 30 minutes is giving a lot of value in the direction of the day"
**Source GPS: LQvv5xgy_ik | END**

#### NY-04 AGREED
> "the first one that break is telling you what is telling you who won the battle of the most important time of the day. So the first 15 minutes of New York opening or 30."
**Source GPS: cUTsoU-15Tc | BEGIN**

#### NY-05 AGREED
> "If you see at the open after 30 minutes, thereby negating this problem here that the open is relatively narrow, then you can assume the market will likely trend after that. Why? Everyone was able to take their positions and is now moving business to the next levels where they think it looks good."
**Source GPS: Of_wlv3xaZo | BEGIN**

#### NY-07 AGREED
> "Open range, meaning the opening range. If it's very large, it likely won't hold. If it's very small, it likely will. That's it. That's all the information you need."
**Source GPS: Fj4FDZQxw0I | END**

#### NY-11 SINGLE
> "A lot of traders are familiar with the opening range breakout. You buy or sell the breakout of the first 15 minutes of the cash session. This strategy published in the 1990 by Toby Crabel proven to be one of the most consistent edge over the last decade with a positive profit factor and an amazing sharp ratio."
**Source GPS: cUTsoU-15Tc | BEGIN**

#### NY-12 CONFLICT
- Flash claims: Two levels from the first 15, 30 or 60 minutes, chosen by scalp vs intraday use (cUTsoU-15Tc [2:10]); window set = {15, 30, 60}.
- Argon claims: Point A and B come from the first 15 to 30 minutes of the NY open (cUTsoU-15Tc [04:26]); window set = {15, 30}.
- Check that settles it: Both quotes sit in the same video; the 60-minute option appears only in the flash quote (verified below). Third check: a full read of cUTsoU-15Tc for any later statement that fixes the window per model (our IB_LEN = 30 for Model C is OURS either way).
> "How can we define this point A and point B? This is the opening of the New York. We have a top. We have a bottom on the first 15 to 30 minutes. Okay. This is our point A and this is our point B and the price is inside this value"
**Source GPS: cUTsoU-15Tc | BEGIN**
> "You have two defined levels that are the top and the bottom of the range of the first 15, 30 or 60 minutes. It depends how you want to use it. If you want to use it more scalp or more intraday bias"
**Source GPS: cUTsoU-15Tc | BEGIN**

#### NY-14 SINGLE
> "this area last for the first 30 minutes. Here they start with the IVB. Okay, they start to plot the level. Now wait for the first 30 minutes of the session. So we have a clean defined range."
**Source GPS: cUTsoU-15Tc | MIDDLE**

#### NY-16 SINGLE
> "In this specific cash session, we saw approximately 6 million contracts being traded. When we look at the entire period, including the after-hours trading session combined with the cash session, the total volume reaches 6.5 million contracts. Now, observe how the value area shifts significantly along with the equilibrium point"
**Source GPS: Of_wlv3xaZo | END**

#### NY-18 SINGLE
> "if you examine the gaps only from the cash session, so 10:00 p.m. and a bit, then you'll see that this close is much much more important than for example, a gap close from midnight. Nobody cares about that because there was no liquidity at all because what happens at the end of the cash session? All the ETFs have"
**Source GPS: Of_wlv3xaZo | END**

#### NY-19 AGREED
> "So this dark orange one is the volume profile of the regular trading hour session, the so-called New York session. The Asian and the London session are in this lighter color because there's less volume into those areas. These are the ETH or extended or electronic trading hour session."
**Source GPS: 9IliXww64uM | BEGIN**

#### NY-20 SINGLE
> "This is for example a unit of 1 day. Each of these profiles shows you one day. And in addition, these profiles only show you the period where the so-called cash session is, i.e. the period where the largest sales associated with the corresponding product are shown."
**Source GPS: BB3c8visnkI | MIDDLE**

#### NY-23 AGREED
> "What was your settings in terms of the to show as as a bubble on the on the chart? What was the minimum contract? >> Always the same. It's 30 contracts. >> If you are in London, I use 20."
**Source GPS: DyS79Eb92Ug | BEGIN**

#### NY-24 SINGLE
> "we are risking 2,000 we are not risking back the profit not even the profit of New York we are risking we are really low on the risk side"
**Source GPS: DyS79Eb92Ug | BEGIN**

#### NY-25 SINGLE
> "if I get the 20,000 profit for the day my rules say it's done because probably you will have consolidation after a strong move. We took the best move of the London and of the New York we walk away."
**Source GPS: DyS79Eb92Ug | BEGIN**

#### NY-26 AGREED
> "You can understand you know that London session is not worth to trade for me. My profit factor is really low. I pay a lot of commission but profit factor is really low. What's my benefit? I get half of the day for free."
**Source GPS: 0KyIEdvVKMQ | END**

#### NY-29 SINGLE
> "90% of the session that expand they rebalance till the power hour this is the structure of the New York if you expand immediately And Trump is not tweeting. You rebalance."
**Source GPS: DyS79Eb92Ug | MIDDLE**

#### NY-34 SINGLE
> "The stock exchanges will open soon or rather the cash session in particular starts in a good 1 and 1/2 hours and I'm going to check in with my boys now."
**Source GPS: f225iVdsrfg | BEGIN**

#### NY-37 SINGLE
> "The draw down the maximum draw down that I accept for the day is 10,000. So considering we are already in profit, the maximum that we can do is lose this 10,000, go back to break even and lose another 10,000"
**Source GPS: DyS79Eb92Ug | BEGIN**

#### NY-38 AGREED
> "there was no relevant news or price discovery auction during the Asian or London session, and we're about to open the session exactly where most of the money was traded yesterday."
**Source GPS: 9IliXww64uM | MIDDLE**

#### NY-41 SINGLE
> "So we came from a London session where we did pretty good amount of profit. That was around $10,000 and we start the session getting caught by a little bit of choppiness here. So we give back $5,000 to the market, around 4,500."
**Source GPS: fZlNGWvd2Ko | BEGIN**

#### NY-42 SINGLE
> "So you know that with 65 to 70% probability, you go here"
**Source GPS: cUTsoU-15Tc | BEGIN**

#### NY-43 SINGLE
> "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading."
**Source GPS: StaphlRH8NQ | MIDDLE**

#### NY-44 SINGLE
> "if the opening range of the first 30 minutes hold predicted value over the coin flip. And we can see that we have a skew of 13.5%"
**Source GPS: StaphlRH8NQ | MIDDLE**

#### NY-45 SINGLE
> "because the model is saying look that this low is not getting touched 80% of the time."
**Source GPS: DyS79Eb92Ug | END**

#### NY-46 SINGLE
> "I made the 40 range now. So it's a range chart because when you are in New York opening if you do one minute candle you can have huge candle and all the data inside gets aggregated."
**Source GPS: DyS79Eb92Ug | BEGIN**

#### NY-47 SINGLE
> "here was the market open today at say 9:00 in the DAX or at 15:30 the cash session which is where the big money enters the markets in America in this case that's the SNP500"
**Source GPS: rrHj24GSR6M | MIDDLE**

#### NY-48 SINGLE
> "because of news it was 8:30 and it did get a follow through before coming back down"
**Source GPS: rCTrQ4fkL1Y | MIDDLE**
