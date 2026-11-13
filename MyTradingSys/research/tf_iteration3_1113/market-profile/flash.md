# Iteration 3: Market Profile & TPO Sweep (flash)

Iteration 3 extraction across `raw_transcripts_canonical/` for statements by Tom Vorwald and Fabio Valentini on market profile, TPO (Time Price Opportunity), 30-minute letters/blocks, initial balance, single prints, poor highs/lows (weak highs/lows, ledgers), excess, and buying/selling tails.

Note on timestamps: Transcripts with inline timestamps (Fabio) carry `[mm:ss]`; cleaned transcripts without inline timestamps carry `[no-ts]`.

## Extraction Table

| topic | trader | exact quote | video id [mm:ss] | rule in his words | number: SOURCED value or NOT_SEEN | in our code? file:line or NONE |
|---|---|---|---|---|---|---|
| TPO / Stylemire origin | Tom Vorwald | Dear friends, market profile, market profiling, the way we actually use it is a wonderful tool. TPO time price opportunity developed by Peter Stattlemeer who was a soybean floor trader at the time and it simply gives us really great information. | K8qtT2_axPo [no-ts] | Market profile is TPO (Time Price Opportunity), developed in the 1980s by Peter Steidlmayer (CBOT soybean floor trader), used every morning and every week to define trend direction. | NOT_SEEN | NONE (sim_desk synthetic study pitchfork.py:15 mentions TPO; no market profile indicator in codebase) |
| Market profile origin | Tom Vorwald | Peter Stylemire already developed market profile in the 1980s and he was a major soybean trader aiming to gain new perspectives in the market. This means that none of us developed or somehow reinvented this tool. No, we still use the possibilities of market profile today to be able to identify where and who is determining the prices. | 1utSjHs_Mq8 [no-ts] | Market profile was developed in the 1980s by Peter Steidlmayer to identify who is determining prices and where big vs small players act. | 1980s | NONE |
| Time association & speed | Tom Vorwald | The great thing is thanks to the speed, the single print areas and the corresponding PC's and value areas from market profile, you get a fantastic view of the time association with the respective price levels. | 1utSjHs_Mq8 [no-ts] | Market profile provides time association with price levels: quick moves (low time) show where price is uncomfortable; slow moves show where price is accepted. | NOT_SEEN | NONE |
| 30m blocks & aggregation | Tom Vorwald | these are 30inut candles. So a 30inut candlestick chart and each of these candles gives us information about whether it was negative or positive. That's all for now in market profile. And here you see the corresponding time frame. We see exactly the same picture only that we've lined up the 30inut blocks and placed them on the appropriate axis so that we can see over time how often the market has spent those 30 minutes in a particular price range. | 1utSjHs_Mq8 [no-ts] | Market profile is built from 30-minute candlestick blocks collapsed and summed onto the vertical price axis to show accumulated time spent at each level. | 30 minutes (30-minute candles/blocks) | NONE |
| Letter / number display | Tom Vorwald | You can also display each of these individual blocks as numbers or letters to see how far the market moved within the corresponding 30inut period. | 1utSjHs_Mq8 [no-ts] | Each 30-minute block can be displayed as letters or numbers to track how far the auction moved during that 30-minute period. | 30 minutes | NONE |
| 30m standardized TPO | Tom Vorwald | It's simply a timebased tool that when used in its standardized version shows you in 30inut blocks where there is momentum in the market and where there is not. | K8qtT2_axPo [no-ts] | Standardized market profile groups the session into 30-minute time blocks to distinguish momentum from lethargy/balance. | 30 minutes | NONE |
| Initial balance definition | Tom Vorwald | In the market profile, we can display what's called the initial balance showing how large the opening phase of trading was. This tells us whether we should expect a more trending day at first or rather a balanced day. | 1utSjHs_Mq8 [no-ts] | Initial balance is the opening trading phase; its range size predicts whether the day will be a trend day or a balance day. | NOT_SEEN | NONE |
| Initial balance 30m span | Fabio Valentini | The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading. | StaphlRH8NQ [8:12] | Initial balance is the high and low price established during the first 30 minutes of regular cash trading. | 30 minutes | MyTradingSys/backtest/layers/fabio/v3/models.py:35 (IB_MINUTES = 30 in Model C only) |
| Initial balance breakout | Fabio Valentini | So in this video we are going to understand how the opening range breakout or initial balance breakout works and how we can improve it. Now the logic behind the opening range breakout or initial balance is the following. The New York session is the session that hold the maximum amount of | cUTsoU-15Tc [1:16] | Opening range breakout / initial balance breakout operates on the New York session cash open where maximum liquidity resides. | NOT_SEEN | MyTradingSys/backtest/layers/fabio/v3/models.py:35 |
| Initial balance retest | Fabio Valentini | You can see that every time, see how much is sensitive the initial balance breakout area. Okay. Every time they come to test this area back, they have | cUTsoU-15Tc [13:44] | The initial balance breakout area remains sensitive; price frequently retests this breakout level and produces reactions. | NOT_SEEN | NONE |
| Initial balance failure | Fabio Valentini | this was not viable for me because we broke below the initial balance and as you know, I like to pair the NASDAQ effort with the IVB model. | Khgj5q1-ln8 [10:37] | Breaking below the initial balance invalidates long continuation and stops trade entry in the IVB model. | NOT_SEEN | NONE |
| Initial balance containment | Tom Vorwald | there are currently aggressive sellers here, there's an initial balance here, and we're staying in this balance again. Well, then that gives you the advantage | m3IMdc7QwN4 [no-ts] | Staying inside the initial balance confirms range containment and gives an advantage for balance trading. | NOT_SEEN | NONE |
| Single print definition | Tom Vorwald | Here we see what's called a single print area. These are the blue lines here. And single print areas, as the name suggests, are individual letters at a certain price range. That means if you were to carefully look at the corresponding 30inut chart, you would clearly see that the price never actually stayed at this specific level for more than 30 minutes. This significant observation means there is only a single candle that was truly present at this particular price range. And we call these distinct price ranges single prints. And single prints are always initiated by strong market participants because they have a reason to create a push. What does that mean for us in the future? And you can see that beautifully here. Such price ranges are often revisited to see if that strong market participant still reacts. | 1utSjHs_Mq8 [no-ts] | Single prints are individual letters (single 30m candle presence) where price stayed < 30 minutes, initiated by strong participants pushing price; revisited later to test participant response. | 30 minutes (single candle / individual letter) | NONE |
| Single print trend profile | Tom Vorwald | There must be what's called a single print here for it to be genuine. What does that mean? Single prints are always individual letters within a profile. And such single prints immediately tell us that there is a high probability the market has currently established a trend profile. Or simply put, it's a trend profile. | K8qtT2_axPo [no-ts] | For a profile to be a genuine trend profile (double distribution), single prints (individual letters) must separate the distributions. | NOT_SEEN (letter count) | NONE |
| Single prints & dominance | Tom Vorwald | In addition, of course, you need to know that there are single print areas, areas where a market has not stayed longer than 30 minutes. These are individual letters which I'll gladly explain on the chart in a moment. And all of this gives us insight into who is dominating the market | ridY2Z0hSQA [no-ts] | Single prints show where market moved faster than 30 minutes, identifying whether strong or weak hands are dominating the market today. | 30 minutes | NONE |
| Single print trend check | Tom Vorwald | We can go ahead and say we use the profiles from market profiling to get an overview for example to see if there are single prints present. That means have aggressive market participants entered this trend and started to dominate | VumVuGnCcFM [no-ts] | Check market profile for single prints to confirm whether aggressive market participants entered and are driving the trend. | NOT_SEEN | NONE |
| Single prints anti-counter | Tom Vorwald | And that is the first indication where we have to clearly say if we have several single prints, caution is advised with such counter strategies aiming for a return to the VWAP. | VumVuGnCcFM [no-ts] | Multiple single prints explicitly forbid counter-trend trades or mean-reversion trades back to the VWAP. | NOT_SEEN (number of single prints) | NONE (v3 Model A counter-trend runs without single-print suppression) |
| Multiple single print zones | Tom Vorwald | And when a market really surges ahead like it did yesterday, it's successfully established 1 2 3 4 single print areas, which signifies significant and absolute market balances. | UOBgXV20yCM [no-ts] | A surging trend market establishes 1 to 4 distinct single print areas, marking intermediate structural auction balances. | SOURCED: 1, 2, 3, 4 single print areas | NONE |
| Single print repair target | Tom Vorwald | The probability that it will repair this single print area first is relatively high. | UOBgXV20yCM [no-ts] | When price pulls back after a trend day, the probability that the market will first repair the single print area is relatively high. | NOT_SEEN | NONE |
| Single prints trend acceleration | Tom Vorwald | whether the big money which needs time to invest is currently moving sideways or if the trend is accelerating because single prints have caused aggressive moves that push the market in one direction or the other. | 3o1VVsfBmmU [no-ts] | Single prints mark trend acceleration by big institutional money versus sideways balance absorption. | NOT_SEEN | NONE |
| Single print trend proof | Tom Vorwald | That's when I have my best evidence for trend trading with confirmation from the single print showing that someone reacted aggressively there and was able to push the price further down so to speak. | rFPCtOcfUMI [no-ts] | Best confirmation for trend trading comes from a single print proving an aggressive participant defended the level and pushed price. | NOT_SEEN | NONE |
| Buying tail / selling tail | Tom Vorwald | Were they formed with so-called buying tails, meaning at least three distinct letters standing completely alone? Or were they formed with so-called weak lows indicating a different market dynamic where the market has established several prices within a single price range. This information in turn gives us insight into whether the market will trade above or below these levels again. | 1utSjHs_Mq8 [no-ts] | A buying or selling tail requires at least 3 distinct single letters standing completely alone at the profile extreme; marks strong participant rejection. | SOURCED: at least 3 distinct letters | NONE |
| Tails identify dominator | Tom Vorwald | If there are individual letters at the top of a profile, then that's a selling tail. At the bottom, like here, that's a buying tail. That means we have strong rejections and with that we can also pinpoint who dominated the market on that day. | K8qtT2_axPo [no-ts] | Individual letters at the top indicate a selling tail; at the bottom, a buying tail. Both represent strong price rejection that identifies the session dominator. | NOT_SEEN | NONE |
| Buying tail from open drive | Tom Vorwald | Because if I know the rules of market profiling, then I know that this was simply an open drive here and the market just gave me a strong buying tail at this point and that really won't offer any support for me. | 3JqMyzE8jIQ [no-ts] | An open drive generates a strong buying tail at the open; rules dictate that this tail will not offer support on an initial retest. | NOT_SEEN | NONE |
| Buying tail pullback setup | Tom Vorwald | If we look at yesterday's profile here, we formed a nice buying tail down here after the market opened, then moved back into value, saw rejection at the PC, and are now making the pullback. | 4MoNjEQ2Dd8 [no-ts] | After a buying tail forms at the open, price trades into value, rejects POC, and sets up a pullback trade. | NOT_SEEN | NONE |
| Buying tail target zone | Tom Vorwald | Look here. Here, for example, is a so-called buying tail. There was strong buying here. And these are always areas where you naturally have to be careful whether a reaction occurs there again. That means I'm now transferring this price range from this buying tail into my corresponding chart and setting it up as a so-called target area. | vk0mkNPuhDc [no-ts] | Prior buying tails are marked and transferred to lower timeframe charts as high-probability reaction target areas. | NOT_SEEN | NONE |
| Weak lows / highs taken out | Tom Vorwald | The probability is very high that these will be taken out again because weak price areas are initiated by weak traders and not like those buying tales or selling tails by strong traders who have quickly created an initiative move which leads the market to simply give us information that this could now be the end. | 1utSjHs_Mq8 [no-ts] | Weak lows/highs (no tail, multiple letters at extreme) are initiated by weak traders and have a very high probability of being revisited and taken out. | NOT_SEEN | NONE |
| Weak high & strong low combo | Tom Vorwald | Then we understand for example when we have such weak highs and strong lows that the probability is very high that something like this will be taken out again. | 1utSjHs_Mq8 [no-ts] | The combination of a weak high with a strong low (tail at bottom, blunt edge at top) means the weak high has a very high probability of being taken out. | NOT_SEEN | NONE |
| Ledgers / multiple letters | Tom Vorwald | Now we can go even further and look for what are called ledgers. That means multiple letters at a single price level. And these ledgers in turn show us that weak hands are taking over the market there or have held it up because that also happens. | K8qtT2_axPo [no-ts] | Ledgers (German: Leisten / flat edges) are multiple letters at an extreme price level, signaling that weak hands rather than strong initiative traders halted price. | NOT_SEEN (exact letter threshold) | NONE |
| Catapult past weak high ledge | Tom Vorwald | Plus, we are currently trading well above those old highs which essentially formed a ledge, a weak high from small traders, and we just catapulted right past it. | T6hDJcHrVBM [no-ts] | A weak high ledge created by small traders offers no real resistance once large money pushes, catapulting right past it. | NOT_SEEN | NONE |
| Weak low ledge structure | Tom Vorwald | If we don't manage the breakout and have here, as it looks right now, but that doesn't mean it is And here a nice ledge, weak low, lower highs. | 0CrkbfuIhkc [no-ts] | A ledge / weak low combined with lower highs signals failed breakout and unfinished auction downward. | NOT_SEEN | NONE |
| 4th impulse excess | Tom Vorwald | When this fourth strong impulse comes, it's always the excess. | 2xnNPIyHGQ4 [no-ts] | In trend extensions, the fourth strong impulse represents the exhaustion excess of the move. | SOURCED: fourth (4th) impulse | NONE |
| Excess extreme trend | Tom Vorwald | We also always call this the excess, the extreme trend. | VOiy8mAALWA [no-ts] | Excess is defined as the extreme terminal phase of a parabolic trend move. | NOT_SEEN | NONE |
| TPO vs Volume POC anomaly | Tom Vorwald | the market had the highest trading volume up here but spent the most time here. This means that in this window I can immediately see aha the market did spend the most time here but the highest trading volumes were traded here. This is what's called an anomaly. If you were to look at all of this using only the market profile, you wouldn't recognize this anomaly. | 1utSjHs_Mq8 [no-ts] | An anomaly occurs when Market Profile (Time POC) and Volume Profile (Volume POC) diverge (e.g. price spent most time at level A, but traded highest volume at level B). | NOT_SEEN | NONE (we only compute Volume Profile; cannot detect TPO vs VP anomalies) |
| Merging consecutive profiles | Tom Vorwald | seventh, we can also, and this is another great thing about market profile, we can merge profiles. Meaning we can combine them and create one large profile if we see that prices are consistently staying within a fair range. | 1utSjHs_Mq8 [no-ts] | Multiple daily profiles are merged into a composite profile as long as prices remain within the established fair price range. | NOT_SEEN | NONE |
| Value area traversal | Tom Vorwald | Because if we know the rules and understand that a market re-enters an old value area and finds acceptance there, then we know there are rules that clearly tell us the probability is high that the profile will be fully traversed. | 1utSjHs_Mq8 [no-ts] | If a market re-enters a previous value area and finds acceptance, there is a high probability the profile will be fully traversed from one edge to the other (the 80% Rule). | NOT_SEEN | NONE |
| Fabio profile framing with TPO | Fabio Valentini | and profile framing now going through profile framing let me remove one second the TPO how is the session of today guys | Is1HvdfQm5c [16:59] | TPO profile is actively used alongside volume profile framing to evaluate daily session context. | NOT_SEEN | NONE |

## TOP 5

1. **Market Profile (TPO) is completely missing from the codebase:** Across 23+ videos, Tom and Fabio use Market Profile (TPO 30-minute letter/block distributions) as their foundational context tool to separate trend from balance, identify participant time-spend, and spot anomalies between time-POC and volume-POC (`1utSjHs_Mq8`, `K8qtT2_axPo`, `ridY2Z0hSQA`, `Is1HvdfQm5c [16:59]`). Our codebase only builds Volume Profile (`MyTradingSys/backtest/vp_return_to_value.py:7`); we have zero TPO construction, zero 30m letter aggregation, and zero capability to detect time/volume anomalies.
2. **Buying and Selling Tails (>= 3 letters) as hard rejection indicators:** Tom provides a strict, sourced quantitative rule for excess tails: a buying or selling tail requires **at least 3 distinct letters standing completely alone** at the profile extreme (`1utSjHs_Mq8`, `K8qtT2_axPo`). Tails prove initiative rejection by strong participants and serve as reaction/target zones (`vk0mkNPuhDc`, `4MoNjEQ2Dd8`). Our code has no tail detector and cannot differentiate a strong rejection extreme from a weak one.
3. **Poor/Weak Highs and Lows ("Ledgers") as magnet targets:** Tom explicitly defines weak highs/lows and ledgers as flat extremes formed by **multiple letters at a single price level** without single-print excess (`1utSjHs_Mq8`, `K8qtT2_axPo`, `0CrkbfuIhkc`, `T6hDJcHrVBM`). He states the rule: weak extremes are created by weak retail traders and have a **very high probability of being revisited and taken out**. This unfinished-auction principle provides high-probability directional targets, but our code has zero poor high/low detection.
4. **Single Prints (<30m duration) as trend confirmation and counter-trade veto:** Tom defines single prints as price levels where the market stayed for less than 30 minutes (a single letter/candle), created by aggressive buyers or sellers (`1utSjHs_Mq8`, `ridY2Z0hSQA`). Critically, Tom gives a negative filter: **if several single prints are present, counter-trend trading back to VWAP is strictly forbidden** (`VumVuGnCcFM`). Furthermore, single prints indicate double-distribution trend profiles (`K8qtT2_axPo`) and serve as high-probability repair targets (`UOBgXV20yCM`). Our models (such as Model A counter-trend) have no single-print veto.
5. **Initial Balance (IB) 30-minute range as a day regime classifier:** Both Tom (`1utSjHs_Mq8`) and Fabio (`StaphlRH8NQ [8:12]`, `cUTsoU-15Tc [1:16]`, `Khgj5q1-ln8 [10:37]`) define the Initial Balance as the high-low range of the **first 30 minutes of cash session trading**. The IB range size dictates whether the day will be a trend day or balance day, and the IB breakout area serves as a sensitive retest trigger. In our codebase, only Model C checks 30 minutes (`MyTradingSys/backtest/layers/fabio/v3/models.py:35`), while Tom's balance models use a static 60-minute box (`MyTradingSys/backtest/layers/fabio/v3/signals.py:183`) and have no IB expansion or retest logic.

## SINGLE BIGGEST HOLE

**The complete absence of the Market Profile / TPO Layer (Time-Price Opportunities, 30-minute letter distributions, single prints, excess tails, and poor extremes) leaves our entire context engine blind to auction structure.**
Tom and Fabio both state that volume alone is insufficient: market profile reveals the **time association** of price (`1utSjHs_Mq8`, `K8qtT2_axPo`). Where the market spent the most time (TPO POC) versus where it traded the most volume (Volume POC) reveals structural anomalies; single prints (<30 min presence) confirm aggressive initiative participants and veto counter-trend setups (`VumVuGnCcFM`); buying/selling tails (>= 3 isolated letters) confirm authentic auction tops/bottoms, while weak highs/lows (multiple letters at extreme) mark unfinished auctions that must be taken out (`1utSjHs_Mq8`). Because our codebase (`vp_return_to_value.py`, `fabio/v3/signals.py`, `auction_context.py`) only constructs 24-hour UTC volume histograms, it cannot compute TPO, cannot identify single prints, cannot detect excess tails or poor highs/lows, and cannot execute the profile-merging and value-area traversal rules that Tom and Fabio use on every session.

## Verbatim Quote Verification Appendix

> "Dear friends, market profile, market profiling, the way we actually use it is a wonderful tool. TPO time price opportunity developed by Peter Stattlemeer who was a soybean floor trader at the time and it simply gives us really great information."
**Source GPS: K8qtT2_axPo | BEGIN**

> "Peter Stylemire already developed market profile in the 1980s and he was a major soybean trader aiming to gain new perspectives in the market. This means that none of us developed or somehow reinvented this tool. No, we still use the possibilities of market profile today to be able to identify where and who is determining the prices."
**Source GPS: 1utSjHs_Mq8 | BEGIN**

> "The great thing is thanks to the speed, the single print areas and the corresponding PC's and value areas from market profile, you get a fantastic view of the time association with the respective price levels."
**Source GPS: 1utSjHs_Mq8 | BEGIN**

> "these are 30inut candles. So a 30inut candlestick chart and each of these candles gives us information about whether it was negative or positive. That's all for now in market profile. And here you see the corresponding time frame. We see exactly the same picture only that we've lined up the 30inut blocks and placed them on the appropriate axis so that we can see over time how often the market has spent those 30 minutes in a particular price range."
**Source GPS: 1utSjHs_Mq8 | BEGIN**

> "You can also display each of these individual blocks as numbers or letters to see how far the market moved within the corresponding 30inut period."
**Source GPS: 1utSjHs_Mq8 | BEGIN**

> "It's simply a timebased tool that when used in its standardized version shows you in 30inut blocks where there is momentum in the market and where there is not."
**Source GPS: K8qtT2_axPo | BEGIN**

> "In the market profile, we can display what's called the initial balance showing how large the opening phase of trading was. This tells us whether we should expect a more trending day at first or rather a balanced day."
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

> "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading."
**Source GPS: StaphlRH8NQ | MIDDLE**

> "So in this video we are going to understand how the opening range breakout or initial balance breakout works and how we can improve it. Now the logic behind the opening range breakout or initial balance is the following. The New York session is the session that hold the maximum amount of"
**Source GPS: cUTsoU-15Tc | BEGIN**

> "You can see that every time, see how much is sensitive the initial balance breakout area. Okay. Every time they come to test this area back, they have"
**Source GPS: cUTsoU-15Tc | MIDDLE**

> "this was not viable for me because we broke below the initial balance and as you know, I like to pair the NASDAQ effort with the IVB model."
**Source GPS: Khgj5q1-ln8 | END**

> "there are currently aggressive sellers here, there's an initial balance here, and we're staying in this balance again. Well, then that gives you the advantage"
**Source GPS: m3IMdc7QwN4 | END**

> "Here we see what's called a single print area. These are the blue lines here. And single print areas, as the name suggests, are individual letters at a certain price range. That means if you were to carefully look at the corresponding 30inut chart, you would clearly see that the price never actually stayed at this specific level for more than 30 minutes. This significant observation means there is only a single candle that was truly present at this particular price range. And we call these distinct price ranges single prints. And single prints are always initiated by strong market participants because they have a reason to create a push. What does that mean for us in the future? And you can see that beautifully here. Such price ranges are often revisited to see if that strong market participant still reacts."
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

> "There must be what's called a single print here for it to be genuine. What does that mean? Single prints are always individual letters within a profile. And such single prints immediately tell us that there is a high probability the market has currently established a trend profile. Or simply put, it's a trend profile."
**Source GPS: K8qtT2_axPo | END**

> "In addition, of course, you need to know that there are single print areas, areas where a market has not stayed longer than 30 minutes. These are individual letters which I'll gladly explain on the chart in a moment. And all of this gives us insight into who is dominating the market"
**Source GPS: ridY2Z0hSQA | BEGIN**

> "We can go ahead and say we use the profiles from market profiling to get an overview for example to see if there are single prints present. That means have aggressive market participants entered this trend and started to dominate"
**Source GPS: VumVuGnCcFM | MIDDLE**

> "And that is the first indication where we have to clearly say if we have several single prints, caution is advised with such counter strategies aiming for a return to the VWAP."
**Source GPS: VumVuGnCcFM | MIDDLE**

> "And when a market really surges ahead like it did yesterday, it's successfully established 1 2 3 4 single print areas, which signifies significant and absolute market balances."
**Source GPS: UOBgXV20yCM | END**

> "The probability that it will repair this single print area first is relatively high."
**Source GPS: UOBgXV20yCM | END**

> "whether the big money which needs time to invest is currently moving sideways or if the trend is accelerating because single prints have caused aggressive moves that push the market in one direction or the other."
**Source GPS: 3o1VVsfBmmU | BEGIN**

> "That's when I have my best evidence for trend trading with confirmation from the single print showing that someone reacted aggressively there and was able to push the price further down so to speak."
**Source GPS: rFPCtOcfUMI | END**

> "Were they formed with so-called buying tails, meaning at least three distinct letters standing completely alone? Or were they formed with so-called weak lows indicating a different market dynamic where the market has established several prices within a single price range. This information in turn gives us insight into whether the market will trade above or below these levels again."
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

> "If there are individual letters at the top of a profile, then that's a selling tail. At the bottom, like here, that's a buying tail. That means we have strong rejections and with that we can also pinpoint who dominated the market on that day."
**Source GPS: K8qtT2_axPo | END**

> "Because if I know the rules of market profiling, then I know that this was simply an open drive here and the market just gave me a strong buying tail at this point and that really won't offer any support for me."
**Source GPS: 3JqMyzE8jIQ | END**

> "If we look at yesterday's profile here, we formed a nice buying tail down here after the market opened, then moved back into value, saw rejection at the PC, and are now making the pullback."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "Look here. Here, for example, is a so-called buying tail. There was strong buying here. And these are always areas where you naturally have to be careful whether a reaction occurs there again. That means I'm now transferring this price range from this buying tail into my corresponding chart and setting it up as a so-called target area."
**Source GPS: vk0mkNPuhDc | END**

> "The probability is very high that these will be taken out again because weak price areas are initiated by weak traders and not like those buying tales or selling tails by strong traders who have quickly created an initiative move which leads the market to simply give us information that this could now be the end."
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

> "Then we understand for example when we have such weak highs and strong lows that the probability is very high that something like this will be taken out again."
**Source GPS: 1utSjHs_Mq8 | END**

> "Now we can go even further and look for what are called ledgers. That means multiple letters at a single price level. And these ledgers in turn show us that weak hands are taking over the market there or have held it up because that also happens."
**Source GPS: K8qtT2_axPo | END**

> "Plus, we are currently trading well above those old highs which essentially formed a ledge, a weak high from small traders, and we just catapulted right past it."
**Source GPS: T6hDJcHrVBM | MIDDLE**

> "If we don't manage the breakout and have here, as it looks right now, but that doesn't mean it is And here a nice ledge, weak low, lower highs."
**Source GPS: 0CrkbfuIhkc | MIDDLE**

> "When this fourth strong impulse comes, it's always the excess."
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**

> "We also always call this the excess, the extreme trend."
**Source GPS: VOiy8mAALWA | MIDDLE**

> "the market had the highest trading volume up here but spent the most time here. This means that in this window I can immediately see aha the market did spend the most time here but the highest trading volumes were traded here. This is what's called an anomaly. If you were to look at all of this using only the market profile, you wouldn't recognize this anomaly."
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

> "seventh, we can also, and this is another great thing about market profile, we can merge profiles. Meaning we can combine them and create one large profile if we see that prices are consistently staying within a fair range."
**Source GPS: 1utSjHs_Mq8 | END**

> "Because if we know the rules and understand that a market re-enters an old value area and finds acceptance there, then we know there are rules that clearly tell us the probability is high that the profile will be fully traversed."
**Source GPS: 1utSjHs_Mq8 | END**

> "and profile framing now going through profile framing let me remove one second the TPO how is the session of today guys"
**Source GPS: Is1HvdfQm5c | BEGIN**
