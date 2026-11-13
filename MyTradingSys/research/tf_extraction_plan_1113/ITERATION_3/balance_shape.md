# Iteration 3 merge: balance_shape

Sources: flash + argon. Rows 48: AGREED 13, SINGLE 34, CONFLICT 1, UNVERIFIED 0 (rows needing a quote that no transcript match supported). Verified quotes below: 27.
Pattern, ledger and fix columns are assigned by rule from the source rows (code column, numbers, transfer words); the ledger column matches video id plus two shared content words. First-pass labels, not a re-read. Rows paired across models by same video id plus quote or rule word overlap.

## Items

| id | item | model verdict | pattern | in ANSWER_LEDGER? | fix type |
|---|---|---|---|---|---|
| BS-01 | When profile shape is a bell curve (balance equilibrium profile, 60-70% of the time), market participants bring price back inside the range; trade counter-setups at ... | AGREED | 2 | Y L17 | extract |
| BS-02 | Value area boundaries enclose 70% of traded liquidity over the chosen profile period (e.g., 1 week). | SINGLE | NEW | Y L13 | test |
| BS-03 | Market profile aggregates 30-minute candles by time spent at each price; a bell curve of time-at-price defines a normal balanced market. | AGREED | 2 | N | extract |
| BS-04 | Volume profile forms a Gaussian distribution with 68% of volume inside the value area; moving away from the mean and exiting the value area creates ... | AGREED | 4 | N | re-code |
| BS-05 | VAH and VAL bound the 68% volume share of the distribution. | SINGLE | NEW | N | test |
| BS-06 | On an A-to-B fixed impulse profile, the value area is where 70% of volume transacted (contradicting 68% in Pz8f0wWW12M), and the single lowest-volume price inside ... | SINGLE | 4 | N | re-code |
| BS-07 | D-shape = large balance phase; P-shape = aggressive upward trend phase; B-shape = aggressive downward trend phase, derived from market profiling plus a closing-price count. | SINGLE | 2 | Y L16 | extract |
| BS-08 | P and B structures (~30% of markets) are acceleration/trend setups; D balance phases (~70% of markets) are value-fade phases (short at top, long at bottom). | SINGLE | 3 | N | re-frame |
| BS-09 | A D structure forms when price oscillates up and down repeatedly within a range, building a large sideways balance phase defined by candle bodies/closes rather ... | SINGLE | 4 | Y L01 | re-code |
| BS-10 | A symmetric normal (bell-shaped) profile indicates the market is in balance. | SINGLE | 2 | N | extract |
| BS-11 | Do not blindly fade a single day's D-profile in isolation if the preceding days had strongly rising profiles. | SINGLE | 2 | N | extract |
| BS-12 | A balance profile appearing after a strong trend signals that the trend is pausing/sorting itself out and price is likely to rotate in balance. | SINGLE | 4 | N | re-code |
| BS-13 | Never trade breakouts inside a balanced sideways market; trade breakouts only when out of balance, and restrict sideways phases strictly to counter-trades at the extremes. | SINGLE | 2 | N | extract |
| BS-14 | Classify market into Phase 1 (consolidation/balance, trapped 70% of the time -> counter setups) vs Phase 2 (accelerated trend, 30% of the time -> breakouts). | SINGLE | 2 | N | extract |
| BS-15 | One-sentence verbal slip reversing the phase numbers he defined immediately before in the same passage. | SINGLE | 2 | N | extract |
| BS-16 | Disable trend-following and breakout setups while the market remains in balance. | SINGLE | 2 | N | extract |
| BS-17 | After 2 consecutive higher VPOCs or 2 consecutive lower VPOCs following a balance phase, stop taking counter-trades and switch to trend continuation. | SINGLE | 2 | N | extract |
| BS-18 | When volume accepts inside VAH-VAL (balance market condition / compression), trade it by fading the top and bottom with order flow. | AGREED | NEW | N | test |
| BS-19 | A daily cash-session profile with value built on the upside and a close near the high is a P-shape, signalling aggressive buyers and next-day bullish ... | SINGLE | 5 | N | re-frame |
| BS-20 | In a daily P-shape profile, the POC is located above the 50% midpoint of the day's range, with a thin low-volume rejection stem below VAL. | AGREED | 2 | N | extract |
| BS-21 | An up-day without a P-shape is still balanced/indecision; a true P-shape has absorbed low volume on the downside and volume concentrated at the top, forecasting ... | AGREED | 2 | N | extract |
| BS-22 | Intraday P-shape has volume concentrated in the upper part of the profile; price pulls back to test/rebalance the upper volume node and then continues higher. | AGREED | 2 | N | extract |
| BS-23 | A P-profile means aggressive buyers have pushed price out of equilibrium and shifted the balance area to the top of the structure, used for trend ... | SINGLE | 2 | N | extract |
| BS-24 | A P-profile represents a buy-side imbalance (impulse up followed by high-level acceptance/liquidity). | SINGLE | 2 | Y L01 | extract |
| BS-25 | A P-shaped profile features single prints in the lower stem and volume/time concentration at the top. | AGREED | 2 | N | extract |
| BS-26 | When an extreme upward imbalance (e.g., hedging spike above weak highs) forms a P-formation whose upper liquidity is decreasing and prints a fakeout at the ... | SINGLE | 2 | N | extract |
| BS-27 | A b-profile forms when price drops dynamically and then builds volume/acceptance at the lower prices, raising the probability of downward trend continuation. | SINGLE | 2 | N | extract |
| BS-28 | At the top of a larger balanced range, a newly formed b-profile confirms seller dominance and shifts the local balance lower, triggering a counter-trade short. | SINGLE | 2 | N | extract |
| BS-29 | A b-profile shows both aggressive selling and a downward shift in the profile's center of gravity (POC/value area). | SINGLE | 2 | N | extract |
| BS-30 | Applies PBD profile-shape reading directly to Bitcoin, reading repeated B-structures as bearish instability. | SINGLE | 5 | N | re-frame |
| BS-31 | When price rallies back into the upper stem/belly of a prior B-profile and volume dries up, short it back toward the low of the B-profile. | SINGLE | 2 | N | extract |
| BS-32 | A weekly double distribution has two distinct balance zones separated by single prints; both balance zones and the single-print vacuum between them act as key ... | AGREED | 4 | N | re-code |
| BS-33 | A double distribution day consists of two separate balance distributions separated by single prints; price either stays in the new distribution or fills the single-print ... | AGREED | 2 | N | extract |
| BS-34 | Single prints (price levels where the market spent only one 30-minute TPO letter) identify a trend profile. | SINGLE | 2 | N | extract |
| BS-35 | In a double distribution cash-session profile, mark the VAL and the thin low-volume rejection zone between the lower and upper distributions as the primary pullback/rejection ... | AGREED | 5 | N | re-frame |
| BS-36 | When consecutive daily cash-session profiles overlap at the same price level, merge them into a single multi-day (2-day or 3-day) composite balance profile to get ... | AGREED | 5 | N | re-frame |
| BS-37 | Merge consecutive profiles into one composite profile whenever price remains within the same fair value range. | SINGLE | 2 | N | extract |
| BS-38 | A market transitions from balance to out-of-balance only when both price and volume accept outside VAH or VAL, ending accumulation/distribution and starting the trend move. | AGREED | NEW | N | test |
| BS-39 | When the New York session expands immediately in the first hour (forming a P-shape or b-shape), 90% of the time it rebalances/consolidates until power hour ... | SINGLE | 2 | N | extract |
| BS-40 | A 24-hour profile and a cash-session profile on the same day can have opposite shapes (e.g., 24h trend profile vs cash-session balance profile); cash-session traders ... | SINGLE | 5 | N | re-frame |
| BS-41 | Even when the time-based Market Profile (TPO) looks balanced, overlaying the Volume Profile can reveal a lopsided volume bulge (an anomaly/imbalance) where large participants aggressively ... | SINGLE | 2 | N | extract |
| BS-42 | For US indices, build the profile on the NY cash session only (London excluded by statistical validation). | SINGLE | 5 | N | re-frame |
| BS-43 | Initial balance / opening range is defined over the first 15, 30, or 60 minutes; after breakout, the zone between VA and POC is the ... | SINGLE | 4 | Y L12 | re-code |
| BS-44 | (ASR) Can take a momentum breakout inside a broad balance space only if entry is not right into VAH/VAL. | SINGLE | 2 | N | extract |
| BS-45 | Large initial balance (first 30-60m, see K8qtT2_axPo) predicts a balanced day; small initial balance predicts a trend day. | SINGLE | 2 | N | extract |
| BS-46 | Buying/selling tails require at least 3 single TPO letters at an extreme (rejection), whereas weak lows/highs show multiple prints at one price; combine tails with ... | SINGLE | 2 | N | extract |
| BS-47 | When a market re-enters an old value area and finds acceptance (1utSjHs_Mq8), there is an 80% probability it will traverse the full value area/profile. | SINGLE | 2 | N | extract |
| BS-49 | Does Tom name D, P and B profiles? Flash: never D-shape or b-shape; Argon: quotes D, P, B profile in 20+ videos | CONFLICT | 3 | N | extract |

## Evidence

#### BS-01 AGREED
> "Especially when the curves look like bell curves, the market participant will try to bring the price back into this range. Therefore, depending on the profile shape, but especially 60 to 70% of the time, we have so-called balance equilibrium profiles. You can then look here quite wonderfully to see where I can find a counter trade."
**Source GPS: BB3c8visnkI | MIDDLE**

#### BS-02 SINGLE
> "And these boundaries simply show us where 70% of the greatest liquidity associated with the corresponding price level we are looking at in this case 1 week has been traded."
**Source GPS: BB3c8visnkI | MIDDLE**

#### BS-03 AGREED
> "That means nothing else has happened here except that the 30inut candles are aggregated by time at the corresponding prices. Yes, where trading has taken place, they are summed up and then I get a wonderful, in this case a bell curve and that gives me really wonderful information."
**Source GPS: K8qtT2_axPo | BEGIN**

#### BS-04 AGREED
> "what the volume profile gave us, it's a Gaussian distribution, where we have the majority of the volume being exchanged in this 68% and as we move from the mean, we have a condition that is called imbalance market. And if we manage to go out from the value area, usually it's where trend start."
**Source GPS: Pz8f0wWW12M | MIDDLE**

#### BS-05 SINGLE
> "And the value area is clearly defined by value area high and value area low. They are the points where the 68% of the volume of the distribution took place."
**Source GPS: Pz8f0wWW12M | MIDDLE**

#### BS-06 SINGLE
> "When you remove the price action and deep dive, you can see that the lowest volume of interaction in all the area of value area. So where 70% of the volume got transacted is exactly this one"
**Source GPS: o-w5Gxss6T0 | MIDDLE**

#### BS-08 SINGLE
> "This logic applies to round about 30% of markets. The P's and the B's are both structures, setups that typically cause a market to accelerate. The other 70% in the so-called balance phases, sideways markets, those are the market phases where you can trade value, short at the top, long at the bottom."
**Source GPS: jXR1afMy-3o | BEGIN**

#### BS-14 SINGLE
> "So, start by carefully examining if we have a consolidation phase, a sideways phase, phase one, where the market tends to remain trapped 70% of the time. Or if we're currently in a strongly trending and accelerated phase, which is the specific phase where I can effectively trade breakouts."
**Source GPS: VxN5IxTwpbE | MIDDLE**

#### BS-17 SINGLE
> "You can go ahead and say if I understand that after two higher and two lower Vpo following a balance phase, I shouldn't be taking counter trades anymore."
**Source GPS: VOiy8mAALWA | END**

#### BS-18 AGREED
> "This is the so-called balance market condition. Now, going on, this type of market can be traded with multiple strategy. Usually, strategy that fade the top and the bottom using order flow."
**Source GPS: Pz8f0wWW12M | MIDDLE**

#### BS-20 AGREED
> "This is a P-shape, so the buyers from daily point of view are in control of the movement. You can see that also the POC is higher. It's located above the 50%."
**Source GPS: Pz8f0wWW12M | END**

#### BS-21 AGREED
> "It's not a P-shape, so it's still balanced. You can use this as indecision. You can put blue instead of green, and then you have our P-shape. Low volume on the downside, completely absorbed, and we have a strong P. What can we expect? That we will have the following days of strong trend up. And we have 1 2"
**Source GPS: Pz8f0wWW12M | END**

#### BS-22 AGREED
> "It means that all the volume is built on the top part here."
**Source GPS: DyS79Eb92Ug | MIDDLE**

#### BS-25 AGREED
> "You can see that here in the profile with the single prints and so on. It's P-shaped."
**Source GPS: gFJBg8Bsw68 | END**

#### BS-30 SINGLE
> "Oh, Bitcoin doesn't look stable at all because we've already seen a perfect B structure twice here."
**Source GPS: 0CrkbfuIhkc | MIDDLE**

#### BS-32 AGREED
> "And then we have a beautiful, what's called a double distribution here. And what information does this double distribution give me? I need to know that before the week starts. And then you can already see it here, all right. This upper balance, which is distinct, and the lower one, which is also distinct, were both aggressively bought. And now"
**Source GPS: -dMWA_bbm3o | MIDDLE**

#### BS-33 AGREED
> "This is called a double distribution day. Essentially, these are two profiles in one."
**Source GPS: K8qtT2_axPo | END**

#### BS-34 SINGLE
> "Single prints are always individual letters within a profile. And such single prints immediately tell us that there is a high probability the market has currently established a trend profile."
**Source GPS: K8qtT2_axPo | END**

#### BS-35 AGREED
> "As you can see, this is a double distribution profile where you have a really thin low. The first point that is interesting is where the value area low is located and then you have a big profile on the upside that where the majority of the volume got traded."
**Source GPS: Pz8f0wWW12M | END**

#### BS-36 AGREED
> "So, these two profile can be merged. You can merge them and you can see one piece of information because when they are overlapping on the same level, they are just telling you that they stayed in this balance area for two days."
**Source GPS: Pz8f0wWW12M | END**

#### BS-38 AGREED
> "when the the price accept and the volume accept below the value area low or the value area high, the market participants are telling you that we are in a situation of out of balance. So, the accumulation or the distribution is finished and you are ready for the real move of the price."
**Source GPS: Pz8f0wWW12M | MIDDLE**

#### BS-39 SINGLE
> "90% of the session that expand they rebalance till the power hour this is the structure of the New York if you expand immediately"
**Source GPS: DyS79Eb92Ug | MIDDLE**

#### BS-43 SINGLE
> "of the first 15, 30 or 60 minutes."
**Source GPS: cUTsoU-15Tc | BEGIN**

#### BS-45 SINGLE
> "In the market profile, we can display what's called the initial balance showing how large the opening phase of trading was. This tells us whether we should expect a more trending day at first or rather a balanced day."
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

#### BS-46 SINGLE
> "Were they formed with so-called buying tails, meaning at least three distinct letters standing completely alone? Or were they formed with so-called weak lows indicating a different market dynamic where the market has established several prices within a single price range."
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

#### BS-47 SINGLE
> "Previously you would talk about the 80% rule which comes into play here. That means the probability is 80% that the market will return to this value."
**Source GPS: rFPCtOcfUMI | MIDDLE**

#### BS-49 CONFLICT
- Flash claims: Neither Tom nor Fabio uses D-shape or b-shape in any of 164 transcripts; Tom says normal profile, balance profile or bell curve (items 12 and 48 of flash).
- Argon claims: Tom names D (large balance phase), P (aggressive up) and B (aggressive down) profiles in many videos (m3IMdc7QwN4, vk0mkNPuhDc, rFPCtOcfUMI, OUM9LYwL8eA).
- Check that settles it: Grep of raw_transcripts_canonical (run in this merge): 'D profile' in 17 files, 'B profile' in 5 files, 'P profile' in 6 files, 'b-shape' and 'D shape' in 0 files. Both are right on the literal word (-shape never said), Argon is right on the concept: Tom does use the D/P/B letters. Third check: none needed beyond the lead reading m3IMdc7QwN4.
> "By the way, the D's are nothing more than large balance phases. The P's are the aggressive trend phases upwards, and the B's are the aggressive trend phases downwards."
**Source GPS: m3IMdc7QwN4 | END**
