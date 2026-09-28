# EXTRACT: Fabio Valentini (Fabervaale ENG) — Pz8f0wWW12M
# Title: "The Only Orderflow Guide You'll Ever Need"
# Duration: 41:04 | Instrument shown: NASDAQ (NQ) footprint/replay + multi-month daily profile
# Source text: auto-generated YouTube captions (word-level timestamps)
#              /mnt/user-data/uploads/BinanceDataFeed/extracts/_staged_2026-09-27/raw/fabervaale_Pz8f0wWW12M_raw.txt
# Extractor: Sonnet worker (Phase 1, clean slate)
# Date extracted: 2026-09-27 | Status: EXTRACTED | Phase: 1 (clean slate)
# Tier: T3 (individual practitioner). "High win rate" / "amazing risk-to-reward"
#       claims are stated with no statistics shown — EXPECTATION (UNQUANTIFIED).
# ---

## ASSESSMENT
This is Fabio's foundational/from-scratch guide and by far the richest of the three
videos: it defines market microstructure (aggressive vs passive orders, footprint,
order-book sweep mechanics), the effort/result vocabulary (absorption, initiative
auction, book sweeping, exhaustion), delta, volume profile (value area, POC, low
volume node), a full multi-day "profile framing" methodology (P-shape, merged
profiles, the "hook," failed-auction fakeouts, premium/discount), and finally a
complete named trade model ("deep trades" area-qualification + big-participant filter,
feeding an absorption-confirmation entry with a breakeven-stop rule and a "momentum
model" for trailing stops).

Critically, this video is the ONLY one of the three that explicitly gives BOTH sides
of the open question (U2 — when does absorption imply reversal vs breakout/
continuation): absorption where the candle still closes in the surviving/rewarded
side's direction (delta shows the absorbed effort, but price confirms the other side)
is read as CONTINUATION (FAB-038); exhaustion — a mismatch where volume is fading
while price keeps pushing in the existing direction against a contrarian imbalance —
is read as the trigger for REVERSAL (FAB-040). See ADDRESSES U2 tags below.

No numeric thresholds are given for what counts as "huge," "aggressive," "a lot," or
"strong" anywhere in this video; all specific contract counts and price levels shown
on-screen (25, 33, 75, 6841, 122 vs 273, 300 contracts, etc.) are EXAMPLE VALUES from
his live chart walk-through, not thresholds. The value-area percentage he states (68%)
and the stated 65-70%-type probability claims elsewhere in his other videos are NOT
repeated here in quantified form except the 68% value-area convention itself, which is
a definitional constant as he states it, not a backtested statistic.

Clean-slate rule honoured: no Tom Vorwald or other Fabio-video (Khgj5q1-ln8,
cUTsoU-15Tc) material used while extracting this file.

---

## RULES EXTRACTED

### FAB-030 — Footprint defined: per-price-level record of executed aggressive orders on both sides of a candle
**Source:** Pz8f0wWW12M @2:29-2:53 | Tier T3 | Tag: DEFINITION
> "Here, we can see a new candle with the order flow tool that represented the
> executed order called the footprint and a record, a detailed record of what
> occurred on both the bid on the left side and the ask on the right. And it provide a
> list of all the aggressive sellers who entered the market, and on the right of all
> the aggressive buyers that joined the action."

Definition as stated: the "footprint" is a per-candle, per-price-level record of
executed aggressive (market) orders, split between the bid side (aggressive sellers)
and ask side (aggressive buyers).
**UNDEFINED:** none beyond the definition itself; this is pure market-structure
vocabulary, not a trading rule.

### FAB-031 — Order-book depletion / sweep mechanics: an aggressive order larger than the resting size at the best price consumes successive levels, producing slippage
**Source:** Pz8f0wWW12M @1:49-5:15 | Tier T3 | Tag: DEFINITION
> "a market order by 25 contracts it's about to hit the book. And these aggressive
> buyers are accepting the prices by the best ask, the so-called passive sellers, the
> passive forces that we saw before, that are providing 33 units at a price level of
> 101. Now, the 33 unit of passive sell orders are sufficient to satisfy the 25 buy
> market orders that are the aggressive forces. And after execution, only eight sell
> orders remain in the best ask, and the price moves up to 101."

> "when we see 75 aggressive participants market order that enters here, what happens
> to the market? And in this case, the 75 buy market order found only eight contract
> on the 101 level, so the best ask. And they moved directly to 102 to fill the
> remaining 67 contract. The 102 level don't have enough sell limit order to be able to
> satisfy the buy market demand. So, considering the order matching, execution moved to
> the next level available, that is 103... the 75 aggressive orders that we saw in the
> beginning received and experienced a slippage of three tick going to be filled
> completely at the 103 level with 31 remaining contract available."

Definition/mechanics as stated: when an aggressive (market) order's size is less than
or equal to the resting passive size at the best price, price does not move beyond
that level (only the passive size is drawn down). When the aggressive order's size
exceeds what is resting at the best price, execution continues ("sweeps") into
successive price levels until the aggressive order is filled, and the initiator
experiences "slippage" measured in ticks from the starting price to the final fill
price. All contract counts (25, 33, 75, 8, 67, 32, 42, 31...) are EXAMPLE VALUES from
this illustrative walk-through, not thresholds.
**UNDEFINED:** none beyond the mechanics as stated; this is order-book mechanics, not
a discretionary trading rule.

### FAB-032 — Passive vs aggressive orders: price certainty/authority vs execution certainty/authority
**Source:** Pz8f0wWW12M @5:15-6:15 | Tier T3 | Tag: PRINCIPLE
> "we have two forces that have different features. We start with the passive forces,
> the limit order that have pricing authority and price certainty because they choose
> the level where they want to be filled, but they experience the execution
> uncertainty. So they don't have the guarantee to be filled because to be filled,
> someone else need to accept this level. The market orders have execution authority
> and execution certainty... but you don't have price certainty because you can be
> filled, for example, you can press buy market on the 101 and be filled at 102
> because maybe your order experience execution [slippage]."

Principle as stated: limit (passive) orders control price but not whether/when they
fill; market (aggressive) orders are guaranteed to fill but not at what price. This
underlies the effort/result and absorption vocabulary used throughout the rest of the
video.
**UNDEFINED:** none; foundational principle.

### FAB-033 — "Path of least resistance": relative resting-order depth on each side of a level indicates which side is easier to push through
**Source:** Pz8f0wWW12M @9:00-11:19 | Tier T3 | Tag: DEFINITION
> "we have only five and 16 here and we have 23 25 18 14. So, the path of least
> resistance is on the upside. This is what I call the path of least resistance."

> "We have 122 total contract on this block here on the book, and we have a total of
> 273 on this part, okay? Which part do you think will be more difficult to pierce
> from the side of aggressive market participants? Of course, this one is the easier
> side to pierce. This one is the more difficult. Why? Because this one hold more
> resistance from passive market participants. So, you need a lot more aggression to
> pierce through this... it's easier for the market to continue higher here and pierce
> through these passive orders instead of breaching through this level."

> "The concept of probability and the concept of what's easier doesn't mean that it's
> always like this, but it's an information that we can use."

Definition as stated: compare the resting (passive) order size on each side of the
book/level; the side with less resting size is easier for aggressive orders to break
through ("path of least resistance"), and is treated as a probabilistic bias, not a
certainty ("doesn't mean it's always like this"). All contract counts shown (5, 16,
23, 25, 18, 14, 122, 273) are EXAMPLE VALUES, not thresholds.
**UNDEFINED:** what depth/how many book levels to aggregate when comparing sides; no
ratio or threshold given for how much thinner one side must be to count.

### FAB-034 — Absorption defined: high effort against a level with zero/negative reward on that candle
**Source:** Pz8f0wWW12M @11:19-12:25 | Tier T3 | Tag: DEFINITION
> "we have a breakdown of forces. We have buyers on the right side and the sellers on
> the left side. And here we can see a huge effort on the top from the buyers to break
> this level that got completely absorbed by passive forces. The sellers on the other
> side received a lot of result more because they did less effort to achieve more
> results. The candle closed sell here. So we have a short candle with left less
> effort from the sellers and a lot of effort from the buyers that received zero
> reward. This is the perfect case of absorption. Why? Because you have no reward for
> buyers and you have a lot of buy pressure. Probably this candle will have positive
> delta but negative closure. This is the textbook example for absorption."

Definition as stated: absorption (his "textbook example") = a single candle where one
side (here, buyers) puts in heavy aggressive effort against a level and is completely
absorbed by the passive side, receiving zero reward, while the other side (sellers)
achieves the candle's price result with comparatively little effort — producing a
candle whose delta and close direction disagree (e.g., positive delta, negative/down
close). This definition is purely descriptive of the candle itself; no forward
(reversal/continuation) claim is attached to it in this passage.
**UNDEFINED:** what counts as "huge effort" / "a lot of effort" (no volume threshold);
single-candle scope only, per his wording.

### FAB-035 — Initiative auction / aggression defined: high effort with high, coherent reward, read as raising the probability of continuation
**Source:** Pz8f0wWW12M @12:28-13:25 | Tier T3 | Tag: DEFINITION + EXPECTATION (UNQUANTIFIED)
> "Let's see now an an example of aggression. So [I have high?] effort and high
> results. You have the same breakdowns on the right of the candle you can see the
> aggressive market participants on the buy side and you can see that this strong move
> on the upside had a lot of effort backing it and they got also rewarded. Probably
> here we see a lot of levels from the book that got swept and we managed to close
> with a full green candle. It means that in this case the big buy effort got
> rewarded and you have what we call an initiative auction and a confirmation of the
> aggression of the buyers. So in this case you can probably guess that in the balance
> of forces buyers won the battle and it's more it's higher probability to see a
> continuation on the next candles." [caption damage: "I have word and high results" —
> almost certainly "I have [high] effort and high results," see UNCLEAR U1]

Definition/expectation as stated: the mirror case of absorption (FAB-034) — heavy
effort on one side that IS rewarded (candle closes in that side's favor) is termed an
"initiative auction," read as confirmation that side won the balance of forces, with
a stated but unquantified higher probability of continuation on subsequent candles.
**UNDEFINED:** "higher probability" is not quantified; no statement of how many
candles the expected continuation should last.

### FAB-036 — "Book sweeping" defined: low effort producing a large price result due to an absence of resting orders
**Source:** Pz8f0wWW12M @13:27-14:14 | Tier T3 | Tag: DEFINITION
> "let's go through an example of book sweeping. So, low effort and high result. In
> this case, we see a lot of executed orders on the bottom side of the candle, and
> then we see a candle that closed with an amazing reward. So, there is movement of
> the candle, but there is an absence of participants. So, we can see that there are
> no sell limit players in all this area. There are, but they are few, and price
> moves, but not the money. So, in this case, we show an example where the effort is
> low and the result is high because in this case, in this area that I'm lining up for
> you, there were no sell limit player. So, a small aggression from the buyers swept
> multiple levels of the book."

Definition as stated: a distinct third pattern (alongside absorption and initiative
auction) — low aggressive effort producing an outsized price move because there was
little/no resting liquidity to consume ("price moves, but not the money"). No forward
directional claim is stated for this pattern in this passage.
**UNDEFINED:** what counts as "few" resting orders / the liquidity threshold for
calling an area a sweep versus a normal move.

### FAB-037 — Delta defined: the difference between aggressive buy and aggressive sell volume, viewable horizontally (per price) or vertically (per candle)
**Source:** Pz8f0wWW12M @14:14-14:44 | Tier T3 | Tag: DEFINITION
> "let's introduce a new concept that is called delta. Delta is the difference between
> aggressive market participants on the buy side and aggressive market participants on
> the sell side. So, it's the different on the horizontal level from aggressive sell
> and aggressive buy market participants. And we can have two different representation
> of this information. We can have an horizontal visualization, and we can have a
> vertical reference for the delta."

Definition as stated: delta = aggressive buy volume minus aggressive sell volume,
representable either horizontally (a delta-footprint profile, by price level) or
vertically (a single delta value per candle/bar).
**UNDEFINED:** none; pure definition.

### FAB-038 — Delta-based absorption where the candle still closes in the surviving side's direction is read as a signal to CONTINUE the move
**Source:** Pz8f0wWW12M @14:44-15:31, @17:06-18:25 | Tier T3 | Tag: DEFINITION + SETUP-CONDITION — **ADDRESSES U2**
> "On the left side, what we are seeing here, it's a delta footprint profile, and we
> can see, for example, that the delta it's really high from the point of view of the
> sellers on the downside, but the candle closed [buy/up — caption reads "by," see
> UNCLEAR U2note]. This is the perfect absorption example that you can see from delta
> footprint profile."

> "On the right side, if you want to use the vertical delta information, we have a
> market that is in a consolidation phase here, and we can spot that all these
> aggressive market participants here got absorbed and the candle closed green. This
> is a potential continuation of the move and an absorption pattern that you can spot
> using the delta per candle in a vertical pack of data."

> "we can see here that we have an absorption in the middle of the candle... we have a
> sudden drop in the delta when this big aggression arrive from the market orders or
> the aggressive participant on the sell side and it got completely absorbed, got run
> through and this market order got completely absorbed on this horizontal level and
> the price continued to push it down and close the candle long. So you have the price
> going up like ignoring this small inefficiency in delta and the delta followed
> through the price and the candle closed long. This example here is the reason I
> always watch the matching of value and the matching of volume here... what the
> volume is doing, what the aggressive market participants are doing and what is the
> result, so the correlation between the effort and the results of the player."

> "this one can be seen as a general absorption because from the horizontal volume you
> can see a lot of effort here, but the candle closed green. So what is telling us that
> all this input of volume delta got absorbed and probably this absorption happened
> here and we will continue on the upside."

Discriminator as stated (his clearest, most repeated statement on the reversal-vs-
continuation question): when a candle/area shows one side's aggression fully absorbed
by delta (a "sudden drop in the delta" or a one-sided delta reading), but the price
STILL closes/continues in the direction of the surviving (non-absorbed) side — i.e.,
price and the post-absorption delta "follow through" together rather than diverging —
this is read as a "potential continuation of the move," not a reversal. He states he
watches specifically for "the matching of value and the matching of volume" (i.e.,
whether price confirms which side survived the absorption) as the deciding factor.
Contrast with FAB-040 (exhaustion), where the mismatch instead runs in the OPPOSITE
direction of the existing move (a genuine divergence) and is read as a reversal
trigger.
**UNDEFINED:** how large the "sudden drop in delta" must be; what confirms "the
candle closed green/long" is not itself already a lagging/late confirmation for entry
purposes — no entry-timing rule is given beyond the descriptive pattern.

### FAB-039 — Initiative auction via delta coherence: constant one-sided aggression with a supporting strong delta is a trend-join trigger
**Source:** Pz8f0wWW12M @15:49-17:04 | Tier T3 | Tag: DEFINITION + SETUP-CONDITION
> "let's see an example of initiative auction. So, a concept that is usually
> representing follow-up and reward. In this case, we can see from the executed order
> a constant aggression of the buyers. So, there is consistent pressure on the upside.
> One side print that is also called imbalance and you can use as a really strong
> point to join the trend when it's developing and you have a strong delta. So, you
> have coherence of information. A strong delta and a candle that close on the upside.
> And in this case, you can see that is the delta that is leading the price on the
> upside. This is the best example that you can have of aggressive momentum and it's
> represented by what we call initiative auction that can also be spotted when you
> have an outline from the vertical volume with a reward from the close of the candle.
> ...it's usually an amazing signal if you are a trend following trader."

Rule as stated: when one side shows constant/consistent aggression (a "one side
print"/imbalance) AND the delta is strong and coherent with the candle's close
direction (delta "leading" price), this "initiative auction" pattern is a trend-join
trigger for a trend-following trader.
**UNDEFINED:** what counts as "constant" aggression (duration/number of prints);
threshold for "strong delta"; "amazing signal" is an unquantified subjective claim.

### FAB-040 — Exhaustion defined: declining volume plus a contrarian imbalance/divergence from price is the reversal trigger
**Source:** Pz8f0wWW12M @18:25-19:26 | Tier T3 | Tag: DEFINITION + SETUP-CONDITION — **ADDRESSES U2**
> "The next example that we can have is an exhaustion. In this case we can see that
> there is a decreasing volume, so the aggression of the market participants from the
> volume standpoint is getting lower and lower and we have also a contrarian
> imbalance, so we have an imbalance at the top from the sellers. So you have the
> price going up up up up up not being followed by the volume, so you have this
> divergence and the price snap back to the value, to the efficiency of the market and
> you can see that you have a rejection here. These signals are usually amazing
> opportunities to capitalize on a reversal trade."

> "from the concept of vertical volume you can find an exhaustion where you can see
> that the market is pushing really strong, printing another green candle, but the
> volume is getting lower and lower. This is a dry up in volume, and usually what you
> see this in a pattern order flow is that you have a sudden reversal in price."

Discriminator as stated: this is the reversal-side counterpart to FAB-038's
continuation-side reading. Exhaustion = (a) the aggressive volume/effort behind the
CURRENT trend direction is visibly decreasing over successive candles/prints ("dry up
in volume"), while (b) a contrarian imbalance appears against that trend (e.g.,
seller aggression printing at the top of an uptrend) even as price keeps extending —
producing a price/volume divergence. This combination (fading effort + a
price/volume divergence against the prevailing move), NOT the absorption-with-
confirming-close pattern of FAB-038, is what he ties to an expected reversal
("amazing opportunities to capitalize on a reversal trade," "sudden reversal in
price" — both EXPECTATION (UNQUANTIFIED), no win-rate or frequency given).
**UNDEFINED:** how many candles/how much volume decline counts as "getting lower and
lower"; how large the contrarian imbalance must be; no invalidation/stop rule is
attached to this pattern in this passage.

### FAB-041 — Volume profile defined: the horizontal distribution of transacted volume by price
**Source:** Pz8f0wWW12M @19:26-19:47 | Tier T3 | Tag: DEFINITION
> "let's go through the volume profile. Every time a limit order is matched with a
> market order, we have a transaction. Every successful transaction, we can visualize
> in a way that is distributed for each tick. And what comes out from this point of
> view is this distribution. This distribution is the volume profile. Now, when we are
> watching the volume profile, we are not extracting from the market information
> related to imbalance, not information related to aggression, but we are watching how
> market participants are interacting from an horizontal point of view."

Definition as stated: the volume profile is the distribution of transacted (matched)
volume by price ("tick"), explicitly framed by Fabio as orthogonal information to
imbalance/aggression (delta, footprint) — a purely horizontal, location-based lens.
**UNDEFINED:** none; pure definition.

### FAB-042 — Value area and point of control (POC) defined; leaving the value area marks the start of a trend
**Source:** Pz8f0wWW12M @19:47-22:25 | Tier T3 | Tag: DEFINITION + SETUP-CONDITION
> "what the volume profile gave us, it's a Gaussian distribution, where we have the
> majority of the volume being exchanged in this 68% and as we move from the mean, we
> have a condition that is called imbalance market. And if we manage to go out from
> the value area, usually it's where trend start."

> "value area is where the majority of the volume for the volume profile that you are
> visualizing it's exchange. And the value area is clearly defined by value area high
> and value area low. They are the points where the 68% of the volume of the
> distribution took place. The point where you can see the maximum level of
> transaction... this one takes the name of the POC, the so-called point of control...
> this one is the level that hold the most amount of transaction of the day."

> "the highest density of executed transaction take place here between the value area
> high and the value area low. And high execution mean strong price acceptance. So,
> institutions are really happy to transact in this area. And big players can find a
> counterparty. This is the so-called balance market condition."

Definition as stated: value area = the price band containing 68% of a profile's
transacted volume (his stated figure), bounded by value area high (VAH) and value
area low (VAL); POC = the single price level with the maximum transacted volume
("most amount of transaction of the day," for a daily profile). High transaction
density inside the value area signals "strong price acceptance" ("balance market
condition"). Moving price+volume outside the value area is stated as usually where a
trend begins.
**UNDEFINED:** exact statistical method for the 68% band (standard-deviation-style
calculation vs an iterative volume-inclusion method is not specified); what
"usually" means quantitatively for the trend-start claim.

### FAB-043 — Range-bound/consolidation market defined as the pre-trend driver; the accumulation/distribution finishes when price and volume accept beyond the value area
**Source:** Pz8f0wWW12M @22:25-24:25 | Tier T3 | Tag: DEFINITION + SETUP-CONDITION
> "this type of market can be traded with multiple strategy. Usually, strategy that
> fade the top and the bottom using order flow. And this market takes the name of
> range bound or compression or consolidation. And is the driver of the trend that is
> coming after... if you want to join the trend early in its development, you need to
> understand that the when the the price accept and the volume accept below the value
> area low or the value area high, the market participants are telling you that we are
> in a situation of out of balance. So, the accumulation or the distribution is
> finished and you are ready for the real move of the price."

Definition/rule as stated: a value-area-bound (range/compression/consolidation)
market is treated as the accumulation/distribution phase that precedes a trend; the
early-trend-join signal is when BOTH price and volume "accept" beyond the value
area's boundary (not price alone) — that dual acceptance marks the end of
accumulation/distribution and the start of "the real move."
**UNDEFINED:** what specifically qualifies as volume "accepting" a break (as distinct
from price merely trading through it) is not operationalized here.

### FAB-044 — Low volume node (LVN) defined; price tends to return to rebalance an LVN before resuming trend, acting as a pivot
**Source:** Pz8f0wWW12M @24:25-25:55 | Tier T3 | Tag: DEFINITION + SETUP-CONDITION
> "let's go through the concept of low volume node. In our distribution of the
> profile, we will have some point where you can see that the price is really low. So,
> on this level, the transaction was not so efficient... the price probably jumped
> from one level to the other with really low volume. And this is the levels where the
> interaction inefficient. You have poor fills, you have dissatisfied market
> participants, and you have low execution. So, no price acceptance."

> "Usually, the market like to rebalance the low volume node before continuing in the
> direction of the trend. So, these area are really important area from a volume point
> of view because it's an area where you don't have high density of executed
> transaction. So, you don't have a price acceptance and big players cannot find
> counterparty there. So, it's areas where you usually see a ceiling or a bottom
> before resuming to the direction of the auction."

> "When you have a low volume node and the market goes in price discovery, you can
> clearly see a lot of days the price coming back to rebalance in this low volume node
> and using this as a pivot before resuming the direction of the auction. In this
> case, you have a lot of unfilled buyers due to the low volume node."

Definition/rule as stated: a low volume node (LVN) is a price level within a profile
where very little volume transacted (a fast, inefficient price jump through it —
"poor fills," "no price acceptance"). The market "likes to" revisit and rebalance
LVNs before continuing the prior trend direction, so an LVN functions as a pivot/
ceiling-or-floor reference for a continuation entry, best used "with confluence" of
other order-flow patterns.
**UNDEFINED:** no threshold for how little volume qualifies a node as "low"; "usually"
is an unquantified frequency claim; how close price must come to the LVN to count as
"rebalancing" it.

### FAB-045 — "P-shape" profile defined: value building on the upside signals aggressive buyer control and a bullish next-day bias
**Source:** Pz8f0wWW12M @26:42-26:59, @29:52-30:20 | Tier T3 | Tag: DEFINITION + EXPECTATION (UNQUANTIFIED)
> "We have the value building on the upside. This is what we call the P shape. It's
> where the buyers are really aggressive and you close the cash session on the upside,
> so you can expect a directional move also on the day after."

> "We have a strong move up. This is a P-shape, so the buyers from daily point of view
> are in control of the movement. You can see that also the POC is higher. It's
> located above the 50%. This means that this movement is really aggressive."

Definition/expectation as stated: a "P-shape" profile is one where the bulk of the
day's volume/value builds toward the upper part of the day's range (POC located above
the midpoint of the range) with a close on the upside — read as aggressive buyer
control for that session and an expectation of a directional continuation the
following day. No probability is attached to this expectation.
**UNDEFINED:** how far above the 50% mark the POC must sit to qualify; no mirrored
statement in this video for a bearish/"b-shape" equivalent (not named here).

### FAB-046 — Merging repeated overlapping day-profiles builds a composite support/resistance reference from their rejection zones
**Source:** Pz8f0wWW12M @30:47-33:00 | Tier T3 | Tag: PROCEDURE
> "these two profile can be merged. You can merge them and you can see one piece of
> information because when they are overlapping on the same level, they are just
> telling you that they stayed in this balance area for two days."

> "you can do from here merge and do a double day profile on a single level and you
> can have a really precise value area low point."

> "as you can see, the auction is really clear. This was amazing long trade. After
> this, you have three profile on an horizontal level. Also, we can merge them and you
> can identify how much it was beautiful the rejection that we saw from the value area
> low."

Procedure as stated: when successive sessions' volume profiles overlap at the same
horizontal level, merge them into a single composite profile; the merged profile
yields a more precise value-area boundary and highlights a reinforced rejection zone
(a "gray area" the price never accepted, per the earlier framing at @30:28) that
functions as a stronger support/resistance reference for subsequent price action.
**UNDEFINED:** how much overlap between two days' profiles is required before merging
is appropriate (no percentage/price-distance threshold given).

### FAB-047 — Repeated-top rejection with a declining POC/value area (no matching low) is a warning sign of a shift from accumulation to distribution
**Source:** Pz8f0wWW12M @33:00-33:37 | Tier T3 | Tag: SETUP-CONDITION
> "we start to notice something interesting. For two day, they reject the top here and
> they go lower in the POC and the value area. So, they don't have the value area I[H]
> matching, but they go down. So, they are starting to distribute. So, what you can do
> is noticing and putting this as a warning because you already rejected for today on
> the same level. This one could be a market shift."

Rule as stated: when price rejects the same top level on two (or more) consecutive
days, but each day's POC and value area print progressively lower without the value
area high matching the prior day's, this pattern is read as an early warning of
accumulation shifting to distribution — a flag to "monitor" (he separately mentions
color-coding it orange), not a confirmed reversal signal by itself.
**UNDEFINED:** how many days of this pattern are required before acting on it; what
distinguishes "monitor" from an actual trade trigger — this rule as stated is a
caution flag, not an entry rule.

### FAB-048 — The "hook": a failed breakdown attempt below the value area that reverses back inside is a trend-continuation setup
**Source:** Pz8f0wWW12M @26:03-26:39 | Tier T3 | Tag: DEFINITION + SETUP-CONDITION
> "we have our setup below the value area low joined with low volume node, and here is
> where we want to see what the market is telling us. After this, we continue the
> price delivery on the upside... when we go back to the value area low and down, we
> do what we call the hook. So, they do a failed auction, they try to break, they get
> rejected. So, all this it's a rejection area, and when you go back inside, you have
> your continuation trade, and so on."

Definition/rule as stated: the "hook" pattern = price dips back to/below the value
area low (ideally aligned with a low volume node, per FAB-044), attempts to break
down further, fails ("failed auction," gets rejected), and returns back inside the
value area — this reversal-back-inside is treated as a continuation-trade trigger in
the direction of the pre-existing (upside, in this example) trend.
**UNDEFINED:** how far below the value area the price must go, and how quickly it
must return, to qualify as a "hook" versus a genuine breakdown.

### FAB-049 — Failed-auction fakeout at the value area high: a hook from the downside that fails to hold typically slices back through toward the value area low
**Source:** Pz8f0wWW12M @27:16-27:52 | Tier T3 | Tag: DEFINITION + SETUP-CONDITION + EXPECTATION (UNQUANTIFIED)
> "After price having a hard time breaking the previous value area low, you can see
> that it also hook the value area high from the downside. And this is what we like to
> call a fake out, a failed auction, trap traders, and you can use all the tools of
> order flow to understand this in real time. And when you have this, usually the
> price slice through the value area high to go to seek orders on the value area low.
> This is one really profitable setup with high win rate."

Definition/rule as stated: the mirror/reversal-side variant of the hook — when price
has already had difficulty breaking a prior value area low, and then also probes
(hooks) the value area high from below without holding, that is called a fakeout/
failed auction (a trap). The stated expectation is that price then reverses back
through the value area high toward the value area low. "High win rate" and
"profitable" are stated with no supporting statistics — EXPECTATION (UNQUANTIFIED).
**UNDEFINED:** how "hard time breaking" the prior VAL is quantified; how long/far the
hook at VAH must extend before being classified as a failed auction versus a genuine
breakout; no stop-loss rule attached to this setup in this passage.

### FAB-050 — Premium/discount: joining a trend from a price considered "expensive" (or "cheap") relative to the volume distribution, targeting a return to value or further discovery
**Source:** Pz8f0wWW12M @27:52-28:27 | Tier T3 | Tag: DEFINITION + SETUP-CONDITION
> "This is the real concept of premium and discount. When you are going lower with the
> value and the market gives you the opportunity to join the trend from a point that
> is considered expensive in the distribution of the volume. You have a trade that you
> can join bringing heat to the value area low or projecting it for additional price
> discovery on the downside."

Definition as stated: "premium" = a price located at the expensive/high extreme of
the recent volume distribution (mirror concept "discount" implied but not separately
worded in this passage); in a downward-shifting-value context, entries taken at
premium are aimed at either a return to the value area low or continued price
discovery lower if the trend extends. He frames this as the general lens for building
directional bias "using volume, so actual executed orders, not theory."
**UNDEFINED:** what price level specifically counts as "expensive" (no distance-from-
POC/value-area threshold given); the discount (long-side mirror) case is not spelled
out symmetrically in this passage.

### FAB-051 — Once a directional shift is confirmed, each retest of the value area boundary in the new trend's favor is a repeatable continuation entry
**Source:** Pz8f0wWW12M @33:58-34:27 | Tier T3 | Tag: DEFINITION + SETUP-CONDITION
> "Look how much it was clear that they are continuing to push the low without
> accepting the high. You have a rejection, an amazing rejection here. It gives us a
> clear trend. And as you can see from here, another test of the value area high,
> amazing short here. Another test of the value area high, amazing short here. Another
> test of the value area high, amazing short. And another test and an amazing short."

Rule as stated: after a "confirmation day" establishes a clear trend (a strong
rejection breaking the prior value area, distinguishing this from the earlier warning
pattern in FAB-047), each subsequent retest of the value area boundary opposing the
new trend (value area high, in this downtrend example) is treated as a repeatable
entry in the trend's direction, until the pattern changes.
**UNDEFINED:** how many repeat entries are safe to take before assuming the pattern is
exhausted; no stop-loss level specified for these repeat entries in this passage.

### FAB-052 — Stops are a normal part of this framework even when directionally correct; rejection strength depends on where the level sits within the larger distribution
**Source:** Pz8f0wWW12M @35:47-36:33 | Tier T3 | Tag: RISK
> "they tried to shift down, they failed because this one, if you try a short, would
> have been a stop loss, the first stop loss in all these days... if you try to short
> this value area you would have taken a stop loss. You have a shift again, and these
> two trades would pay you out. But why the market when it reached this sensitive
> level is having a stronger rejection? Because we are on the upper part of the
> distribution. So, this one was completely predictable."

Rule/observation as stated: even within a framework he otherwise describes as highly
predictable, isolated stop-outs happen when the market briefly shifts against the
prevailing read; he attributes the strength of a given level's rejection to its
position within the broader (multi-day) volume distribution (e.g., "the upper part of
the distribution") rather than treating every level as equal.
**UNDEFINED:** no rule for distinguishing, in real time, a shift that will produce a
stop-out from one that will hold — this is offered as a retrospective observation, not
a forward-looking filter.

### FAB-053 — "Deep Trades" model, short example: independently qualify an area, filter to big-participant orders, use absorption at that level as the entry trigger, move to breakeven on confirmation
**Source:** Pz8f0wWW12M @37:31-38:46 | Tier T3 | Tag: PROCEDURE + ENTRY + STOP
> "In this case here, I can see that all these effort 72, 61, 60, 62. So, a total of
> 300 contract on this horizontal level where also the aggressive sellers already show
> their strong aggression with result showing me that all this effort is being
> absorbed. So, this is a perfect example of absorption. This is a confirmation for me
> to start building my position on the downside and the information for me that I can
> put my position at risk-free comes immediately 3 minutes after when the market is
> telling me, 'Look at that. They are adding short position.' And the result of the
> candle is really strong. So, I can capitalize on this movement."

> "What I watch is the interaction between my level and the market participants, the
> big market participants... This was an area qualified for the short that you can
> qualify as I show you previously using the profile, using your technical analysis
> strategies, using everything."

Procedure exactly as stated: (1) qualify an area of interest using ANY independent
method (volume profile, other technical analysis — his own words, "using
everything"); (2) at that pre-qualified level, watch only the filtered, big-
participant order flow ("deep trades," a size filter); (3) when those large orders
show strong aggression that is absorbed with no result, treat that as an absorption
confirmation to build (open) a position in the level's expected direction; (4) once
the market shows a follow-through confirmation shortly afterward ("3 minutes after" in
this example — an EXAMPLE timing, not a rule) with a strong resulting candle, move the
stop to breakeven ("risk-free").
**UNDEFINED:** the size threshold for "big market participants"; how much contract
volume constitutes "strong aggression" (300 contracts here is an EXAMPLE VALUE); the
"3 minutes" breakeven timing is example-specific, not stated as a fixed rule; no
initial stop-loss placement is given for this example before the breakeven move.

### FAB-054 — "Deep Trades" model, long example: repeated absorbed retests reinforce a level ("ping pong"); a subsequent break is the entry, with a momentum trailing-stop model for management
**Source:** Pz8f0wWW12M @38:57-40:37 | Tier T3 | Tag: PROCEDURE + ENTRY + STOP + TARGET
> "It was a qualified area to search for longs and the market comes back to this area
> the first time. It comes back and you can see 105 executed order on Nasdaq on this
> horizontal level on the week. So, it means that these aggressive orders got
> rejected. They didn't add a result. They got completely absorbed. The market tried
> again. Fail. The market tried again another time and the last time that it tried, it
> tried with 101 contract always on the same horizontal level."

> "let's do a summary. You have a method of qualifying important areas that it can be
> volume profile, it can be view up[VWAP], it can be anything you like to use supply
> and demand. And then you have an information from the execution point of view of the
> market participants... So, now we are stuck here. You can do this ping pong till
> here. And when you break this level, you can decide to put your stop loss to break
> even. So, if you decide to enter here like this with a target here, okay, you can
> decide to go from 1 to 2 to 1 to 5 and put your stop loss to break even."

> "What happened yesterday was the following. So, you have another attempt after
> breaking out of the sellers of breaking complete absorption and you have an amazing
> explosion on the upside where you can trail... this for example is my momentum model
> that you saw live for 1,000 time. You can trail your position following the
> aggression of the market. So, this one print a new one, you bring your stop loss
> here and you continue."

Procedure exactly as stated: (1) qualify an area for longs by any independent method
(volume profile, VWAP[his caption reads "view up" — see UNCLEAR], supply/demand); (2)
each time price retests that level and the aggressive orders there get completely
absorbed without a result, treat it as reinforcing the level (repeated "ping pong,"
i.e., the level holds); (3) when the level finally breaks in the qualified direction,
enter, moving the stop to breakeven, with an example target framed as an R-multiple
("1 to 2 to 1 to 5" — an EXAMPLE, not a fixed target rule); (4) once price explodes in
the trade's favor, switch to his named "momentum model": trail the stop behind each
new aggression print in the trade's direction as the move continues.
**UNDEFINED:** how many absorbed retests are needed before a level is considered
reinforced; the precise trailing-stop rule for the momentum model (how far behind each
new print the stop is placed is not specified — only "you bring your stop loss here
and you continue"); the R-multiple given is explicitly an example, not a stated
target rule.

---

## UNCLEAR
- U1 @12:28: "So [I have word] and high results" — caption damage; almost certainly
  "I have [high] effort and high results" given the surrounding aggression/initiative-
  auction context (mirrors "low effort and high result" phrasing used for book
  sweeping at @13:33). Best guess, not corrected inline in FAB-035's quote beyond a
  bracketed flag.
- U2-note @14:44-15:02: "the candle closed by" almost certainly "closed buy" (i.e.
  closed up/green) given the surrounding logic (sellers pushing hard but price still
  goes up = absorption of sellers by buyers); flagged inline in FAB-038 rather than
  silently corrected.
- U2 (the open question carried from the template/other extracts): does this video
  state the discriminator for absorption → reversal vs breakout/continuation?
  ADDRESSED, and more explicitly than in either other video in this set. FAB-038
  (absorption where price/delta still confirm the surviving side → continuation) and
  FAB-040 (exhaustion — fading effort plus a genuine price/volume divergence against
  the prevailing move → reversal) together give a coherent discriminator: the
  deciding factor he repeatedly names is whether "the matching of value and the
  matching of volume" holds (continuation) or diverges (reversal), not the mere
  presence of absorption/high-effort-no-result. FAB-034's bare textbook absorption
  definition, by contrast, is presented with no forward directional claim at all —
  it only becomes predictive once combined with the delta/price-follow-through read
  of FAB-038 or FAB-039, or the volume-decline-plus-divergence read of FAB-040.
- U3 @39:44: "view up" is likely a mis-transcription of "VWAP" (volume-weighted
  average price), listed alongside volume profile and supply/demand as ways to
  qualify an area in FAB-054; kept bracketed as a guess, not corrected.
- U4: no mirrored/named bearish counterpart to the "P-shape" (FAB-045) is given in
  this video (e.g., no "B-shape" or similar term used), despite the multi-day
  walkthrough showing clearly bearish sessions — an asymmetry in his own terminology,
  not resolved here.

## EXCLUDED
- @0:00-1:15: intro framing ("institutional trading space," "traded live in front of
  millions of people," Telegram channel plug) — biographical/promotional, no rule
  content.
- @1:52-2:29: fully worked toy order-book example (25 buy vs 33 passive sell at 101,
  then 25 sell vs 41 passive buy at 99) — folded into FAB-031/032 as the source of the
  mechanics rule; all contract counts are EXAMPLE VALUES, not separately extracted.
  1:10-1:12, @40:57-41:04: Telegram/subscribe outro.
- @24:44-24:53, "price discovery, bullish move, buy side intent, unfilled buyers due
  to low volume" — appears to be an on-screen chart annotation read aloud rather than
  new spoken content; folded into FAB-044, not separately extracted.

## SUMMARY
| Category | Count |
|---|---|
| DEFINITION | 12 (FAB-030, 031, 034, 036, 037, 041–045, 048, 050 — several also
  carry a second tag) |
| PRINCIPLE | 1 (FAB-032) |
| SETUP-CONDITION | 11 (FAB-038, 039, 040, 042, 043, 044, 045, 047, 048, 049, 050, 051
  — counted once each where tagged) |
| PROCEDURE | 3 (FAB-046, 053, 054) |
| ENTRY | 2 (FAB-053, 054) |
| STOP | 2 (FAB-053, 054) |
| TARGET | 1 (FAB-054) |
| RISK | 1 (FAB-052) |
| EXPECTATION (unquantified) | 3 (FAB-035, 045, 049 — each also tagged DEFINITION) |
| Total rules | 25 (FAB-030–FAB-054) |
| Numeric thresholds given | 1 definitional constant (68% value area, FAB-042); all
  other numbers are EXAMPLE VALUES from chart walk-throughs |
| UNCLEAR items | 5 |
| U2 verdict | Addressed — FAB-038 (continuation: absorption + price/delta
  confirmation of the surviving side) vs FAB-040 (reversal: exhaustion = fading
  effort + genuine price/volume divergence) |
| Trade model named | "Deep Trades" area-qualification + big-participant filter,
  feeding an absorption-confirmation entry, breakeven-stop rule, and his named
  "momentum model" for trailing stops (FAB-053/FAB-054) |

# END
