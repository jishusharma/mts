# Iteration 3 merge: market_profile

Sources: flash + argon. Rows 100: AGREED 20, SINGLE 80, CONFLICT 0, UNVERIFIED 0 (rows needing a quote that no transcript match supported). Verified quotes below: 54.
Pattern, ledger and fix columns are assigned by rule from the source rows (code column, numbers, transfer words); the ledger column matches video id plus two shared content words. First-pass labels, not a re-read. Rows paired across models by same video id plus quote or rule word overlap.

## Items

| id | item | model verdict | pattern | in ANSWER_LEDGER? | fix type |
|---|---|---|---|---|---|
| MP-01 | Market Profile was developed in the 1980s by soybean floor trader Peter Steidlmayer to identify where and who is determining prices over time. | AGREED | 2 | N | extract |
| MP-02 | TPO (Time Price Opportunity) is a standardized time-based tool built in 30-minute blocks showing where momentum vs lethargy sits to establish daily context. | AGREED | 2 | N | extract |
| MP-03 | Market Profile lines up 30-minute candle blocks and collapses them onto the price axis to count how many 30-minute periods touched each price level. | AGREED | 2 | N | extract |
| MP-04 | Accumulating 30-minute periods across price forms a mountain-shaped profile; each block can be displayed as a number or letter representing its 30-minute window. | AGREED | 2 | N | extract |
| MP-05 | Market profiling is a 30-minute chart collapsed onto the vertical price axis by summing 30-minute candles at each traded price. | SINGLE | 2 | N | extract |
| MP-06 | The Market Profile Point of Control (PC) is the price level touched by the largest number of 30-minute candles (where the market spent the most ... | AGREED | 2 | N | extract |
| MP-07 | Market Profile has its own time-based Point of Control (PO) and time-based Value Area High/Low covering 70% of time-based trading activity, distinct from volume-weighted VPOC/VAH/VAL. | SINGLE | 2 | N | extract |
| MP-08 | VPOC is the volume equilibrium in Volume Profile, while POC in Market Profile is the time-weighted equilibrium where price spent the most time. | SINGLE | 2 | Y L17 | extract |
| MP-09 | Tom classifies Market Profiles into normal (balance bell curve, 70% of days), normal variation (balanced but probes one side and rejects back), trend profiles (small ... | SINGLE | 2 | N | extract |
| MP-10 | Check whether the daily close is inside or outside the Market Profile Value Area; a close outside value signals a structural shift, so a next-day ... | AGREED | 4 | N | re-code |
| MP-11 | Fabio turns off the TPO display on his chart during profile framing and relies on Session Volume Profile, composite volume profile, and orderflow instead. | AGREED | 2 | N | extract |
| MP-12 | Guest trader on Tom's channel analyzes TPO in parallel with daily, weekly, and monthly Volume Profiles to identify trend vs balance and big-picture bias. | SINGLE | 2 | N | extract |
| MP-13 | Daily profiles are restricted to the cash session (Regular Trading Hours) where the largest volume for the instrument occurs. | SINGLE | 5 | Y L13 | re-frame |
| MP-14 | Even when scalping on a 1-minute chart, higher-timeframe context is read from the cash-session Market Profile. | SINGLE | 5 | N | re-frame |
| MP-15 | For DAX futures, the cash session profile covers 08:30/09:00 to 17:35 CET when underlying cash equities trade and liquidity is highest. | SINGLE | 5 | N | re-frame |
| MP-16 | At the 15:30 CET (09:30 ET) US cash open, wait until 16:00 CET (the first 30 minutes) doing nothing while analyzing the cash profiles, Value ... | SINGLE | 2 | N | extract |
| MP-17 | Fabio builds US index profiles strictly on the New York cash session, excluding London/overnight volume based on statistical validation. | SINGLE | 5 | Y L10 | re-frame |
| MP-18 | Tom pairs the weekly Market Profile with the weekly Volume Profile to establish macro balance vs imbalance and single-print zones before zooming into intraday charts. | SINGLE | 2 | N | extract |
| MP-19 | When consecutive daily Market Profiles stay inside the same fair price range without shifting value, merge them into one combined profile to get updated fair ... | AGREED | 2 | N | extract |
| MP-20 | Refer to merged multi-day Market Profiles to spot overhead selling tails and failed breakouts that re-enter the prior Value Area. | SINGLE | 2 | N | extract |
| MP-21 | In the contested course video, the composite profile loads the last 10 days of chart volume to reveal macro double distributions and the Low Volume ... | SINGLE | 2 | N | extract |
| MP-22 | The Initial Balance is the price range of the first 30-minute block of the cash session open; its width (very large vs rather small) is ... | SINGLE | 5 | N | re-frame |
| MP-23 | The Initial Balance width in the Market Profile forecasts whether the session is more likely to trend steadily or oscillate back and forth in balance. | AGREED | 2 | N | extract |
| MP-24 | A narrow Initial Balance acts like a compressed rubber band; when price breaks out of a small IB, the move has substance and forms a ... | SINGLE | 2 | N | extract |
| MP-25 | When the opening 30-minute range is very large, the session is likely to stay in balance or retrace back to test the opposite side of ... | SINGLE | 2 | N | extract |
| MP-26 | A very large Initial Balance is driven by price-insensitive opening hedging transactions; Tom refuses to chase longs at the top of a wide IB and ... | SINGLE | 2 | N | extract |
| MP-27 | When trading US indices, trade during the cash session (15:30 to 22:00 CET). | SINGLE | 5 | N | re-frame |
| MP-28 | Referring to 24-hour profiles when trading the cash session is meaningless because 6 million of the day's 6.5 million contracts trade in the cash session, ... | SINGLE | 5 | N | re-frame |
| MP-29 | If the open range after the first 30 minutes is relatively narrow, expect the market to trend afterward; if the market starts explosively right away, ... | SINGLE | 2 | N | extract |
| MP-30 | Stop trading during the first 30 minutes of the New York session and use the width of that 30-minute opening range to determine whether the ... | SINGLE | 2 | N | extract |
| MP-31 | Fabio waits out the first 30 minutes of the New York open so the session stabilizes and market participants finish setting up. | SINGLE | 4 | N | re-code |
| MP-32 | Fabio defines Initial Balance as the high and low of the first 30 minutes of regular cash trading; volatility contraction (narrow IB) in that first ... | AGREED | NEW | N | test |
| MP-33 | Fabio's IVB model marks the top and bottom of the first 15 to 30 minutes of the New York open (04:30), waits for the first ... | SINGLE | NEW | Y L12 | test |
| MP-34 | Do not take longs after price breaks below the Initial Balance; pair profile framing or IVB directional bias with footprint/deep effort in the same direction. | AGREED | 2 | N | extract |
| MP-35 | A single print area (marked with blue horizontal lines) is a price range containing only a single TPO letter/block—meaning only one 30-minute candle traded there ... | AGREED | 2 | N | extract |
| MP-36 | Single prints are created by aggressive institutional pushes and are frequently revisited later to test whether those strong market participants still defend the zone. | SINGLE | 2 | N | extract |
| MP-37 | A genuine double-distribution day consists of two bell-curve profiles (two time POCs) separated by an interior single-print zone where no fair prices were traded; unless ... | AGREED | 2 | N | extract |
| MP-38 | A Market Profile single print is a price range where a 30-minute chart never retraced—identical in concept to a Fair Value Gap. | SINGLE | 2 | N | extract |
| MP-39 | Returning to a single print area is a high-probability profit-taking target, not a standalone entry; only enter at a single print when it aligns with ... | SINGLE | 2 | Y L17 | extract |
| MP-40 | A fast trend without pullback leaves a single print area ('space') in the Market Profile—an open zone left standing by aggressive participants (e.g. at 23,660). | SINGLE | 2 | N | extract |
| MP-41 | When the Market Profile contains multiple single prints, aggressive institutions are driving a trend; do not fade the move with counter-trend VWAP return strategies. | AGREED | 2 | N | extract |
| MP-42 | When a market surges and leaves 4 single print areas, it marks a powerful trend day; entering the next cash session carries a high probability ... | AGREED | 5 | N | re-frame |
| MP-43 | Identify weekly double distributions and unrepaired intraday single-print areas before the session and transfer those single-print zones onto smaller execution charts as support/resistance business zones. | SINGLE | 5 | N | re-frame |
| MP-44 | A single print area ('space') acts as support until filled; once price fills the single print and accepts inside it, price breaks through to the ... | SINGLE | 2 | N | extract |
| MP-45 | High-conviction support levels are formed where past Value Areas align with past single-print areas. | SINGLE | 2 | N | extract |
| MP-46 | Fabio identifies a double-distribution Volume Profile where a thin low-volume zone separates the lower distribution from a large upper distribution. | SINGLE | 2 | N | extract |
| MP-47 | A buying tail (or selling tail) requires at least 3 distinct single TPO letters standing completely alone at the extreme, proving strong institutional initiative rejection. ... | AGREED | 2 | N | extract |
| MP-48 | Individual letters at the top of a Market Profile form a selling tail and at the bottom form a buying tail (strong rejection). Multiple letters ... | AGREED | 2 | N | extract |
| MP-49 | A buying tail at the bottom of the Market Profile means price spent only a single 30-minute period at the low before shooting upward explosively. | SINGLE | 2 | N | extract |
| MP-50 | When a Market Profile has a strong low (buying tail) and a weak, shallow high (weak, shallow highs), there is a very high probability that ... | AGREED | 2 | N | extract |
| MP-51 | In Market Profile, selling tails and buying tails define strong highs and strong lows (institutional dominance), whereas their opposite—flat extremes without tails—are weak highs and ... | SINGLE | 2 | N | extract |
| MP-52 | Transfer prior sessions' buying tails onto the execution chart both as reaction support zones and as downside profit targets. | AGREED | 5 | N | re-frame |
| MP-53 | When price spikes above Value Area High, leaves a selling tail at the top, and re-enters prior value acceptance, the Market Profile 80% rule gives ... | SINGLE | 2 | N | extract |
| MP-54 | In Volume Profile, Fabio defines a 'volume ledge' as a sharp cliff where volume drops rapidly from a High Volume Node (HVN) peak to a ... | SINGLE | 2 | N | extract |
| MP-55 | Overlaying Volume Profile directly on the Market Profile reveals 'anomalies' where the price of highest volume (VPOC) diverges from the price where the market spent ... | SINGLE | 2 | N | extract |
| MP-56 | Overlaying Volume Profile onto Market Profile shows whether a session that looks balanced in time is actually imbalanced in volume because one or two institutional ... | SINGLE | 2 | N | extract |
| MP-57 | While Value Areas can be computed on time (Market Profile) or volume (Volume Profile), Tom prefers using Market Profile to read participant dominance (tails, single ... | SINGLE | NEW | N | test |
| MP-58 | When the volume-weighted VPOC separates from the time-based POC, it proves an aggressive institutional player built a large position in a short window of time. | SINGLE | 2 | N | extract |
| MP-59 | On the weekly chart, when the volume-weighted POC sits at the top of the range while the time-based Market Profile PO sits at the bottom, ... | SINGLE | 2 | N | extract |
| MP-60 | In Tom's PbD (Profile by Dynamic) strategy, gray Market Profile TPO blocks are layered directly over the Volume Profile: Market Profile reveals who is dominating ... | SINGLE | 3 | Y L16 | re-frame |
| MP-61 | Tom's static 3-indicator trilogy is (1) Market Profile + (2) Volume Profile on weekly/daily cash charts to identify balance/imbalance and transfer key levels, combined with ... | SINGLE | 5 | N | re-frame |
| MP-62 | Market profiling layers Market Profile and Volume Profile on top of each other; two single prints (where price stayed no longer than 30 minutes) show ... | SINGLE | 2 | N | extract |
| MP-63 | When price forms a buying tail below value after the open and re-enters value, use the pullback to target the Value Area High. | AGREED | 2 | N | extract |
| MP-64 | Layering the Market Profile timestamp with the Volume Profile reveals fair-value POCs alongside repaired buying tails, selling tails, and overhead single prints for route planning. | SINGLE | 2 | N | extract |
| MP-65 | A selling tail at the top of the prior week's profile above the Value Area and VPOC establishes a macro short bias for counter-trading. | SINGLE | 2 | N | extract |
| MP-66 | Mark the prior day's buying tail (strong buyers), selling tail (strong sellers), and equilibrium zone before the open; a buying tail near Value High expects ... | SINGLE | 2 | N | extract |
| MP-67 | Single print areas show where institutions hammered orders into the market very quickly; define trade target areas using Value Areas, naked POCs, or old single ... | SINGLE | 2 | N | extract |
| MP-68 | Inspect the cash-session Market Profiles to see when price breaks above, closes a single print, and rotates deeper into prior profiles. | SINGLE | 5 | N | re-frame |
| MP-69 | Use intraday Market Profiles to locate three primary target/puzzle levels: naked POCs (PCs), old single print areas, and old Value Areas. | SINGLE | NEW | N | test |
| MP-70 | Under Market Profile and Volume Profile rules, when equilibria (VPOCs) shift upward and a distinct single print forms from global institutional inflow, the trend is ... | SINGLE | NEW | N | test |
| MP-71 | When aggressive buying drives price out of a fair price range leaving single prints and upper balance, the Market Profile forms a bullish P-shaped profile ... | SINGLE | 2 | N | extract |
| MP-72 | In P-shaped and b-shaped profiles, the thin stem is the rapid trend section formed by single print areas or an open drive where the market ... | SINGLE | 2 | N | extract |
| MP-73 | Even in an extremely bullish structure, single print areas where price spent very little time during a fast run are often corrected/repaired later. | SINGLE | 2 | N | extract |
| MP-74 | When yesterday's daily profile has a single print below and the VPOC established at the top of the profile, upward pressure dominates. | SINGLE | 2 | N | extract |
| MP-75 | Combine Market Profile single prints, Volume Profile VPOC shifts, balance-zone acceptance, and the market open to confirm a DAX short even at an all-time high. | SINGLE | 2 | N | extract |
| MP-76 | When the market opens a single print above the previous day's Value Area, aggressive buyers have entered and price can accelerate strongly upward. | SINGLE | 2 | N | extract |
| MP-77 | A single print area below the VPOC (e.g., DAX 18,258) marks where aggressive sellers pushed the market down and serves as a key overhead resistance ... | SINGLE | 2 | N | extract |
| MP-78 | Transfer prior-day Value Areas, single print zones, and buying tails onto the execution chart; watch for open-test-drive buying tails that launch trend moves. | SINGLE | 5 | N | re-frame |
| MP-79 | Use the Market Profile concept to see aggressive buyers via single prints alongside the Value Area and VPOC of a big trend profile before planning ... | SINGLE | 2 | N | extract |
| MP-80 | Use the 30-minute footprint/candle chart for longer swings because 30 minutes is the foundational period of Market Profiling; check finished vs unfinished auctions at highs/lows. | SINGLE | 2 | N | extract |
| MP-81 | US equities exhibit predictable behavior during the first 30 minutes of the cash open, and the extreme of the first 30 minutes holds strong predictive ... | SINGLE | NEW | N | test |
| MP-82 | In a trending market structure, having two single prints is even stronger than one; pair those single prints with Low Volume Nodes (LVNs) in the ... | SINGLE | 2 | N | extract |
| MP-83 | Guest Wall Street scalper uses Market Profile as the clearest reference tool to see how all market participants behave over a given time period and ... | SINGLE | 2 | N | extract |
| MP-84 | Market profile provides time association with price levels: quick moves (low time) show where price is uncomfortable; slow moves show where price is accepted. | SINGLE | 2 | N | extract |
| MP-85 | Standardized market profile groups the session into 30-minute time blocks to distinguish momentum from lethargy/balance. | SINGLE | 2 | N | extract |
| MP-86 | Opening range breakout / initial balance breakout operates on the New York session cash open where maximum liquidity resides. | SINGLE | NEW | Y L12 | test |
| MP-87 | The initial balance breakout area remains sensitive; price frequently retests this breakout level and produces reactions. | SINGLE | 2 | N | extract |
| MP-88 | Staying inside the initial balance confirms range containment and gives an advantage for balance trading. | SINGLE | 2 | N | extract |
| MP-89 | Single prints show where market moved faster than 30 minutes, identifying whether strong or weak hands are dominating the market today. | SINGLE | 2 | N | extract |
| MP-90 | Multiple single prints explicitly forbid counter-trend trades or mean-reversion trades back to the VWAP. | SINGLE | 2 | N | extract |
| MP-91 | When price pulls back after a trend day, the probability that the market will first repair the single print area is relatively high. | SINGLE | 2 | N | extract |
| MP-92 | Single prints mark trend acceleration by big institutional money versus sideways balance absorption. | SINGLE | 2 | N | extract |
| MP-93 | Best confirmation for trend trading comes from a single print proving an aggressive participant defended the level and pushed price. | SINGLE | 2 | N | extract |
| MP-94 | An open drive generates a strong buying tail at the open; rules dictate that this tail will not offer support on an initial retest. | SINGLE | 2 | N | extract |
| MP-95 | The combination of a weak high with a strong low (tail at bottom, blunt edge at top) means the weak high has a very high ... | SINGLE | 2 | N | extract |
| MP-96 | Ledgers (German: Leisten / flat edges) are multiple letters at an extreme price level, signaling that weak hands rather than strong initiative traders halted price. | SINGLE | 2 | N | extract |
| MP-97 | A weak high ledge created by small traders offers no real resistance once large money pushes, catapulting right past it. | SINGLE | 2 | N | extract |
| MP-98 | A ledge / weak low combined with lower highs signals failed breakout and unfinished auction downward. | SINGLE | 2 | N | extract |
| MP-99 | In trend extensions, the fourth strong impulse represents the exhaustion excess of the move. | SINGLE | 2 | N | extract |
| MP-100 | Excess is defined as the extreme terminal phase of a parabolic trend move. | SINGLE | 2 | N | extract |

## Evidence

#### MP-01 AGREED
> "Peter Stylemire already developed market profile in the 1980s and he was a major soybean trader aiming to gain new perspectives in the market. This means that none of us developed or somehow reinvented this tool. No, we still use the possibilities of market profile today to be able to identify where and who is determining the prices."
**Source GPS: 1utSjHs_Mq8 | BEGIN**

#### MP-02 AGREED
> "TPO time price opportunity developed by Peter Stattlemeer who was a soybean floor trader at the time and it simply gives us really great information. The information should be viewed in such a way that it allows you to determine a context for the day. There are different profile types of the market profile, but first you have to understand"
**Source GPS: K8qtT2_axPo | BEGIN**

#### MP-03 AGREED
> "We see exactly the same picture only that we've lined up the 30inut blocks and placed them on the appropriate axis so that we can see over time how often the market has spent those 30 minutes in a particular price range."
**Source GPS: 1utSjHs_Mq8 | BEGIN**

#### MP-04 AGREED
> "That's why a kind of mountain forms here across the accumulated time frames that the market profile provides us with. You can also display each of these individual blocks as numbers or letters to see how far the market moved within the corresponding 30inut period."
**Source GPS: 1utSjHs_Mq8 | BEGIN**

#### MP-05 SINGLE
> "That means nothing else has happened here except that the 30inut candles are aggregated by time at the corresponding prices. Yes, where trading has taken place, they are summed up and then I get a wonderful, in this case a bell curve and that gives me really wonderful information. So let's summarize before we move on. We've understood that market"
**Source GPS: K8qtT2_axPo | BEGIN**

#### MP-06 AGREED
> "Here the market has touched 6,758 with 30 minute candles for example seven times here and from that the so-called PC's are derived and the PC's these are the so-called points of control which are the price ranges where according to the market profile the market spent the most time"
**Source GPS: 1utSjHs_Mq8 | BEGIN**

#### MP-07 SINGLE
> "Here we see the so-called PO, not to be confused with the Vpo, which is volume weighted. No, this is the P. This is the point where the market spent the most time on this day. And then we see value area high and value area low. These are also calculated based on the time when the market spent 70%"
**Source GPS: K8qtT2_axPo | BEGIN**

#### MP-08 SINGLE
> "The absolute equilibrium level is called the VPOC in the volume profile and the point of control in the market profile, the time-weighted moment where the market has spent the most time within the relevant time frame."
**Source GPS: aursfDVYzUk | BEGIN**

#### MP-09 SINGLE
> "This is for example a so-called normal variation profile. What does that mean? The market is actually balanced, but it looked down here and got rejected. That means here we immediately have the information that these unfair prices were pushed back up very strongly."
**Source GPS: K8qtT2_axPo | MIDDLE**

#### MP-10 AGREED
> "we can determine whether the closing prices were within the balance the value area or if the closing price was outside. If it was outside then the information is clear for us something changed at the close of trading. And that's important because if the market opens the next day and moves back there the probability is high that we"
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

#### MP-11 AGREED
> "so we start with our amazing template here and profile framing now going through profile framing let me remove one second the TPO"
**Source GPS: Is1HvdfQm5c | BEGIN**

#### MP-13 SINGLE
> "Each of these profiles shows you one day. And in addition, these profiles only show you the period where the so-called cash session is, i.e. the period where the largest sales associated with the corresponding product are shown."
**Source GPS: BB3c8visnkI | MIDDLE**

#### MP-14 SINGLE
> "When we look for trades on the 1-minute chart, we always look at what is the context. And we determine the context through market profiling. And this here is, for example, a market profile chart, where you can read how the market traded during the cash session, the main trading hours, you can see it here."
**Source GPS: zAwEX_tRUfE | BEGIN**

#### MP-15 SINGLE
> "Now here on the right side you can see the exact same information recorded during the live cash session. That means this is the market phase where the highest liquidity is present between 8:30, 9:00 and 17:35 where the cash times of the DAX future are simply present where the stocks are predominantly bought."
**Source GPS: T6hDJcHrVBM | BEGIN**

#### MP-16 SINGLE
> "Let's paint a picture. Market opens at 15:30. You wait until 16:00 and do nothing. During that time, I carefully look at the cash volume profiles and analyze the market activity to see exactly what is happening. See whether the market is falling or rising according to the value areas and the POCs or if we're in a range to"
**Source GPS: Of_wlv3xaZo | BEGIN**

#### MP-19 AGREED
> "And last but not least, seventh, we can also, and this is another great thing about market profile, we can merge profiles. Meaning we can combine them and create one large profile if we see that prices are consistently staying within a fair range."
**Source GPS: 1utSjHs_Mq8 | END**

#### MP-21 SINGLE
> "And this composite volume profile basically takes the entirety of the volume of the chart that I have loaded. And I typically load the last 10 days. And what I can see is we have a double distribution. So this is a first distribution, and this is a second distribution. We have a low volume node right over here."
**Source GPS: 9IliXww64uM | BEGIN**

#### MP-22 SINGLE
> "And here we can see this that means this day here expanded simply means 30 minute blocks where I first get the information what was the range in the first 30 minutes. The range of the first 30 minutes gives me information about how to assess the trading opening phase. Is it very large or is it rather small? That's"
**Source GPS: K8qtT2_axPo | BEGIN**

#### MP-23 AGREED
> "In the market profile, we can display what's called the initial balance showing how large the opening phase of trading was. This tells us whether we should expect a more trending day at first or rather a balanced day. This means is it more likely that the market will establish itself steadily in a trend or will it swing back"
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

#### MP-27 SINGLE
> "Okay, but keep in mind that you really only want to be trading during the main market hours or what we call the cash session, which runs from 15:30 all the way through to 22:00 hours and just a little bit more."
**Source GPS: Of_wlv3xaZo | END**

#### MP-28 SINGLE
> "In this specific cash session, we saw approximately 6 million contracts being traded. When we look at the entire period, including the after-hours trading session combined with the cash session, the total volume reaches 6.5 million contracts. Now, observe how the value area shifts significantly along with the equilibrium point, the value area low, and the value area high."
**Source GPS: Of_wlv3xaZo | END**

#### MP-29 SINGLE
> "If you see at the open after 30 minutes, thereby negating this problem here that the open is relatively narrow, then you can assume the market will likely trend after that. Why? Everyone was able to take their positions and is now moving business to the next levels where they think it looks good."
**Source GPS: Of_wlv3xaZo | BEGIN**

#### MP-30 SINGLE
> "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that. And you will be able to change your whole business."
**Source GPS: Of_wlv3xaZo | MIDDLE**

#### MP-31 SINGLE
> "usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session."
**Source GPS: DyS79Eb92Ug | BEGIN**

#### MP-32 AGREED
> "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading. Volatility contraction during this first half hour often revolves in explosive volume confirmed directional breakout runs that hold strong predictive power"
**Source GPS: StaphlRH8NQ | MIDDLE**

#### MP-33 SINGLE
> "We have a clean defined IVB top and bottom and we are waiting for the first 30 minutes of the session to be completed to define clearly the areas where we see breakout. We have a statistical edge that the price will continue in that direction."
**Source GPS: cUTsoU-15Tc | MIDDLE**

#### MP-34 AGREED
> "this was not viable for me because we broke below the initial balance and as you know, I like to pair the NASDAQ effort with the IVB model. So, you need to keep in mind a profile framing or IVB directional bias paired with the deep effort"
**Source GPS: Khgj5q1-ln8 | END**

#### MP-35 AGREED
> "Here we see what's called a single print area. These are the blue lines here. And single print areas, as the name suggests, are individual letters at a certain price range. That means if you were to carefully look at the corresponding 30inut chart, you would clearly see that the price never actually stayed at this specific level for more"
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

#### MP-37 AGREED
> "This is called a double distribution day. Essentially, these are two profiles in one. Very important. There must be what's called a single print here for it to be genuine. What does that mean? Single prints are always individual letters within a profile. And such single prints immediately tell us that there is a high probability the market has currently"
**Source GPS: K8qtT2_axPo | END**

#### MP-38 SINGLE
> "For example, we have these so-called single print areas here. These single print areas are in reality nothing more than specific price ranges where the market never actually retraced within this particular move, at least when viewed from a 30-minute chart. So, in the end, it's really almost the same thing. Except that this single print area shows a single"
**Source GPS: Fj4FDZQxw0I | MIDDLE**

#### MP-40 SINGLE
> "And that's why we call this price area a fast trend. And the market profiler sees a single print area here. Nothing more, nothing less. I also like to call such zones space. That simply means price areas where the market has left something open, left it standing."
**Source GPS: 3JqMyzE8jIQ | BEGIN**

#### MP-41 AGREED
> "We can go ahead and say we use the profiles from market profiling to get an overview for example to see if there are single prints present. That means have aggressive market participants entered this trend and started to dominate the market and aggressively push it downward. Why? That doesn't matter for now. What matters to us is that these"
**Source GPS: VumVuGnCcFM | MIDDLE**

#### MP-42 AGREED
> "And when a market really surges ahead like it did yesterday, it's successfully established 1 2 3 4 single print areas, which signifies significant and absolute market balances. And these four single print areas naturally created a substantial and powerful price movement in the 24-hour profile, as well as the weekly profile."
**Source GPS: UOBgXV20yCM | END**

#### MP-46 SINGLE
> "As you can see, this is a double distribution profile where you have a really thin low. The first point that is interesting is where the value area low is located and then you have a big profile on the upside"
**Source GPS: Pz8f0wWW12M | END**

#### MP-47 AGREED
> "We know precisely how significant tops and how crucial lows are ultimately formed. Were they formed with so-called buying tails, meaning at least three distinct letters standing completely alone? Or were they formed with so-called weak lows indicating a different market dynamic where the market has established several prices within a single price range. This information in turn gives us"
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

#### MP-48 AGREED
> "If there are individual letters at the top of a profile, then that's a selling tail. At the bottom, like here, that's a buying tail. That means we have strong rejections and with that we can also pinpoint who dominated the market on that day. Now we can go even further and look for what are called ledgers. That means"
**Source GPS: K8qtT2_axPo | END**

#### MP-49 SINGLE
> "What is the next thing we see here? We see what is called a buying tail. This means that the market only spent 30 minutes here and then moved explosively in this case upwards shot up. And such a buying tail shows us strength."
**Source GPS: K8qtT2_axPo | BEGIN**

#### MP-50 AGREED
> "Then we understand for example when we have such weak highs and strong lows that the probability is very high that something like this will be taken out again."
**Source GPS: 1utSjHs_Mq8 | END**

#### MP-52 AGREED
> "Here, for example, is a so-called buying tail. There was strong buying here. And these are always areas where you naturally have to be careful whether a reaction occurs there again. That means I'm now transferring this price range from this buying tail into my corresponding chart and setting it up as a so-called target area."
**Source GPS: vk0mkNPuhDc | END**

#### MP-53 SINGLE
> "At the top we have a nice selling tail and run back to the previous acceptance. Previously you would talk about the 80% rule which comes into play here. That means the probability is 80% that the market will return to this value."
**Source GPS: rFPCtOcfUMI | MIDDLE**

#### MP-59 SINGLE
> "Here you can also clearly see the discrepancy between the market and volume profile. The volume weighted POC is up here while the timebased PO that is the point of control from the market profile is down here. And I can already see that there is a discrepancy here. That's why I'm a bit cautious about going allin long right"
**Source GPS: Kg6sYKgtkrY | MIDDLE**

#### MP-60 SINGLE
> "What you see here, that's the volume profile and the gray areas you see in these wonderful blocks, that's the corresponding market profile. That means we layer them on top of each other. And with that we have two possibilities. On the one hand, we have the option to see who is currently dominating the market. For example, here with"
**Source GPS: jXR1afMy-3o | BEGIN**

#### MP-61 SINGLE
> "Here we have a completely normal chart which we use to get an overview. Then here we have the weekly market profile where we can see what the market looks like in the long term, whether it's in balance or imbalance and who is dominating. And for day trading, we take an even closer look to see which levels are"
**Source GPS: ridY2Z0hSQA | END**

#### MP-62 SINGLE
> "Let's start with a look at market profiling. Yeah, what is that? Well, it's the market profile and volume profile layered on top of each other. And here you can see, for example, the market opened here, it ran down briefly, it played upwards very aggressively, had a reaction up here, and then it went into a sideways phase. So,"
**Source GPS: m3IMdc7QwN4 | BEGIN**

#### MP-63 AGREED
> "If we look at yesterday's profile here, we formed a nice buying tail down here after the market opened, then moved back into value, saw rejection at the PC, and are now making the pullback. And now we should definitely reach the price area of the value high up here."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

#### MP-71 SINGLE
> "Here the market simply had a fair price range, but then aggressive buying came in. You can see that here in the profile with the single prints and so on. It's P-shaped."
**Source GPS: gFJBg8Bsw68 | END**

#### MP-74 SINGLE
> "And now let's see what yesterday's profile looked like. And we can already see this here is the value area. Here we have a single print. That means there was a lot of buying here. That shows me that the probability is higher for now that the market has upward pressure, especially since the VPOC has established itself at the"
**Source GPS: QClPWDJ-BrU | BEGIN**

#### MP-77 SINGLE
> "And the V POC, which is the volume point of control, had led to the market first establishing a negative balance just below it as a result. And additionally, there was a single print area. That means aggressive hands also decided to push the market down here. And so, let's also note the price range 18,258."
**Source GPS: ujedEcmvBMk | BEGIN**

#### MP-80 SINGLE
> "If you're going for, let's say, longer swings, you just use the 30 minute chart, which by the way is always very smart because it's based on market profiling."
**Source GPS: oPyUif2Zrtk | END**

#### MP-81 SINGLE
> "the nature of the US equities have predictable behavior during the opening, okay? And that the bottom of the first 30 minutes is giving a lot of value in the direction of the day, can be improved. For example, can be improved with option flow, and this is the study that I'm doing."
**Source GPS: LQvv5xgy_ik | END**

#### MP-82 SINGLE
> "What would you think if we said you have a market structure, it's currently trending, you can see that maybe single prints have formed. By the way, if there are two, it's always better than if there's only one. And now you use these low volume nodes in the volume profile to see how fast things move when pullbacks occur"
**Source GPS: 4P5WAxyPCis | MIDDLE**

#### MP-85 SINGLE
> "It's simply a timebased tool that when used in its standardized version shows you in 30inut blocks where there is momentum in the market and where there is not."
**Source GPS: K8qtT2_axPo | BEGIN**

#### MP-89 SINGLE
> "In addition, of course, you need to know that there are single print areas, areas where a market has not stayed longer than 30 minutes. These are individual letters which I'll gladly explain on the chart in a moment. And all of this gives us insight into who is dominating the market"
**Source GPS: ridY2Z0hSQA | BEGIN**

#### MP-99 SINGLE
> "When this fourth strong impulse comes, it's always the excess."
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**
