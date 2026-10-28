# GAP_RULES
# MTS Condition File - Tom Vorwald's rules for PRICE gaps (not fair value gaps)
# Scope: DAX-ONLY layer. Operator 2026-10-11: CME bitcoin futures now trade 24/7, so there are
#        no BTC weekend/CME gaps; nothing in this file applies to BTC. Fair value gaps are
#        out of scope (already extracted in zone_identification_rules.md).
# Source: 8 of the 9 task transcripts carry Tom's own gap statements (raw_transcripts_canonical/):
#         96iPFDpXEcU lO-Iptd29t4 l8RZrBfzvp4 YopZ5ZDmMFw ujedEcmvBMk DVZVE9rXGtU Of_wlv3xaZo 3JqMyzE8jIQ.
#         5Ljfwvtktek was read in full and excluded (see section 9).
# Built: 2026-10-11
# Provenance rule: every rule below has a verbatim quote, video id and position. A number, window or
#   threshold that is not in his words is marked NO-SOURCE and must not be tuned or invented.

---

## 0. COUNTS

- Rules: 27 (G01-G26 plus sub-rule G13b)
- CONTEXT-NEEDED (quote depends on what he points at: "here", "this", "there", "such a price range", with no stated level): 10 rules
  - whole rule depends on a pointer (5): G13b, G21, G22, G25, G26
  - one quote of the rule depends on a pointer, the rest is usable (5): G12, G16, G17, G20, G23
- DATA-NEEDED (testable form needs data that 1m DAX bars do not carry: news tags, closing-auction volume): 5 rules: G07, G08, G09, G19 (story tag), G23 (part A)
- Rules testable on 1m DAX bars alone: G01, G02, G03, G05, G06, G11, G14, G15, G18, G20 (entry part), G23 (part B), G24
- Parameters that are NO-SOURCE across the file: gap size minimum, "substantial"/"incredibly low" volume, "huge"/"large" gap, "a few points" before
  the prior value area, length of the post-gap range, length of "lethargy", what counts as a closing-auction "extreme", DAX cash clock times.

Position tag meaning: BEGIN / MIDDLE / END are thirds of the transcript body, as checked by
`scripts/dev/verify_extract_quotes.py`.

DAX test frame used by every "Testable form" below (1m DAX futures bars):
- cash session = the exchange's cash-hours session; gap = first cash-session open vs the previous cash-session close
  (Tom: "if you examine the gaps only from the cash session", G02). Weekend gap = Friday close vs Monday open.
- fill = price trades back to the previous cash-session close.
- prior range / prior value area = previous cash session high-low / value area from the 1m volume profile.
- Cash-session clock times are NOT in his DAX words: NO-SOURCE, read them from the instrument calendar, do not tune.

---

## 1. DEFINITION AND UNIVERSE

### G01 - What a price gap is, and where it comes from

Rule: a price gap is the jump between the last price of one session and the first price of the next; it is created
mostly outside main hours (after hours, overnight, off-exchange, news), but can also occur intraday.

> "Gaps are nothing more than the market closed here and the next day it opened here. That means we have a price gap here."

**Source GPS: lO-Iptd29t4 | MIDDLE** [TOM-215]

> "A price gap that usually occurs during after hours trading. But there are also price gaps that happen intraday."

**Source GPS: 96iPFDpXEcU | BEGIN** [TOM-216]

> "And gaps, such price gaps, yes, they always occur exactly when big players, for whatever reason, do their business pre-market, after hours, in the middle of the night, or in off-exchange trading."

**Source GPS: lO-Iptd29t4 | MIDDLE** [TOM-217]

Testable form: gap = |cash open - previous cash close| > 0 (any non-zero gap; he says in futures "you almost never have the opening at the
exact same level"). Minimum size: NO-SOURCE. Tag each gap by when its price move occurred (overnight/weekend vs intraday).

### G02 - Only gaps measured on the cash session matter; intraday gap work only in main hours

Rule: measure gap closes from the cash session close, not from an overnight/midnight price; when detecting intraday gaps
do it only in main trading hours.

> "if you examine the gaps only from the cash session, so 10:00 p.m. and a bit, then you'll see that this close is much much more important than for example, a gap close from midnight."

**Source GPS: Of_wlv3xaZo | END** [TOM-218]

> "Even if the markets have gapped like crazy, most of the volume ran in the cash session, and that's what interests market participants."

**Source GPS: Of_wlv3xaZo | END** [TOM-219]

> "I know that a lot of people always try to program things like this and so on. Please only do this during the main trading hours."

**Source GPS: lO-Iptd29t4 | MIDDLE** [TOM-220]

Testable form: reference price for fill = previous cash-session close; compare fill rate vs a midnight/overnight reference price.
Note: "10:00 p.m." is the guest's/other market's cash close in that dialogue, not DAX; DAX clock time is NO-SOURCE in his words.

### G03 - Not every gap closes; there is no unconditional gap fade

Rule: never assume every gap is closed. The task is to know when it closes and when it stays open.

> "So, stop with this nonsense that you can always assume gaps will be closed."

**Source GPS: lO-Iptd29t4 | MIDDLE** [TOM-221]

> "It's much more important to know when do these price gaps cause something to happen and what makes them get filled. Meaning, when does the market move back to close them and when do they stay open?"

**Source GPS: 3JqMyzE8jIQ | BEGIN** [TOM-222]

Testable form: no layer may fade every gap. Baseline: measure same-day / 3-day fill rate of all DAX cash gaps, then split by G05-G09, G14-G17.
Pass condition for the whole layer: classes G05+G14 (fill expected) fill more often than class G06/G17 (no fill expected).

---

## 2. THE TWO-QUESTION FRAMEWORK

### G04 - Fundamental story first, technical substance second

Rule: for each gap ask (1) what fundamental data is behind it and (2) technically, is the gap substantial (accepted)
or not; and judge whether the gap makes sense.

> "Now, there are two ways to get to the bottom of this. One way is to check what fundamental data is behind it. Yes, that is incredibly important. And the second is how can I evaluate technically if this gap is substantial or not?"

**Source GPS: 96iPFDpXEcU | BEGIN** [TOM-223]

> "That means as a first step I determine for myself whether the gap makes sense or is it a gap that logically doesn't make sense to me."

**Source GPS: YopZ5ZDmMFw | MIDDLE** [TOM-224]

Testable form: every gap gets two labels: news class (G07-G09) and acceptance class (G06, G11, G14). "Makes sense" is a judgement with no
stated measure: NO-SOURCE for automation; use the news class as its only proxy.

---

## 3. WHERE THE OPEN IS RELATIVE TO THE PRIOR RANGE

### G05 - Open inside the prior day's range: fill is more likely

Rule: when the open is within the previous day's range (within fair prices / value), the 80% rule applies and the gap is
likely filled first, unless the fundamental story is extreme.

> "On one hand, the market might open above or it might open within the previous day's range."

**Source GPS: 96iPFDpXEcU | BEGIN** [TOM-225]

> "since the market is within fair prices, there's simply, technically speaking, the 80% rule where the market trades within value. So, there's a high probability the market fills it first, unless the fundamental story is extreme, which we'll get to."

**Source GPS: 96iPFDpXEcU | BEGIN** [TOM-226]

Testable form: bucket = open inside previous-session range (variant B: inside previous-session value area). Test fill-to-previous-close
rate for that bucket vs open outside. The only number is "80%" as the name of the rule; no tradable threshold is stated.

### G06 - Gap above (or below) the whole prior day: check liquidity there; accepted prices mean do not fade

Rule: when the open is beyond the entire previous day's range, look at volume in the gap area. Substantial volume means the
market accepts those prices (P-type structure); then do not trade the gap close, wait for the breakout direction.

> "The second scenario is we have a gap above the entire day. And when a gap like that occurs, it's very important to look at one thing. How is the liquidity up here? What is the volume like?"

**Source GPS: 96iPFDpXEcU | BEGIN** [TOM-227]

> "Because at the very moment they become substantial, it means that the market is accepting prices up here. And what do we have then? Then, according to my PBD logic, we have a P."

**Source GPS: 96iPFDpXEcU | BEGIN** [TOM-228]

> "And then you just have to see in which direction is the market breaking out now."

**Source GPS: 96iPFDpXEcU | BEGIN** [TOM-229]

Testable form: open > previous high (or < previous low). Volume traded inside the gap zone / above the previous high on the 1m profile after the open;
"incredibly low" vs "substantial" has no number: NO-SOURCE (use a rank vs previous-day volume-at-price only as a descriptive stat, never as a tuned cut).
P/b structure: as defined in market_state_rules.md. If accepted and price breaks out away from the prior close, the fade is off.

### G17 - Breakaway gap: skipped range, expect no fill for a long time

Rule: a breakaway gap is the market skipping a previous price range; assume it will not be closed for a very long time.

> "Of course, there are also gaps called breakaway gaps. That means nothing other than the market skipping over a previous price range."

**Source GPS: lO-Iptd29t4 | END** [TOM-230]

> "If you have such a breakaway gap, assume that this gap here will not be closed. It will take a very very very very long time for that to happen."

**Source GPS: lO-Iptd29t4 | END** [TOM-231]

> "It could be a breakaway gap, for example. But you don't have to make everything so mega complex and complicated. Instead, you can just think about it. Is this gap substantial or is it not?"

**Source GPS: 96iPFDpXEcU | MIDDLE** [TOM-232]

Testable form: breakaway = open outside the entire previous-session range (G06 geometry) AND accepted/substantial (G06). Measure median/percentile
time-to-fill vs inside-range gaps. "Previous price range" could be the prior day or a multi-day range: he does not say; test both.
CONTEXT-NEEDED (part): "this gap here" in the second quote has no stated level of its own; the geometry above comes from the first quote.

---

## 4. THE STORY BEHIND THE GAP (NEWS CLASS)

### G07 - Substantive economic/central bank/inflation news: gap likely not closed

> "If it has to do with economic news that is substantial, the gap will likely not be closed."

**Source GPS: 96iPFDpXEcU | MIDDLE** [TOM-233]

> "If, for example, a large gap occurs in the DAX future now, especially over the weekend, and the market is very far away, and the story behind it has to do with inflationary building blocks. So, inflation data is influenced by that, then pay close attention because this gap will likely not be closed."

**Source GPS: 96iPFDpXEcU | MIDDLE** [TOM-234]

Testable form: DATA-NEEDED, an event-tag per gap (central bank / inflation / economic data) from the economic calendar or headlines;
not derivable from 1m bars. Apply to DAX weekend gaps and overnight gaps. "Large" gap: NO-SOURCE.

### G08 - Political/non-economic story: "short legs", gap likely closed

> "But, and this is a really cool thing, if this gap has to do with political stock markets, and then I don't care about the direction, the probability is high that the market will close this gap again. That means there's this nice saying, political markets have short legs."

**Source GPS: 96iPFDpXEcU | MIDDLE** [TOM-235]

Testable form: DATA-NEEDED, event-tag "political / not economically substantial" (his example: threats, warnings). Either direction of gap. Fill-rate by tag.

### G09 - Day-3 behaviour: the close usually comes one day after the gap, not the same day

> "Usually it doesn't happen on the same day, but one day later. So, we had day one here. We had day two here, where the gap was created, and now comes day three."

**Source GPS: 96iPFDpXEcU | MIDDLE** [TOM-236]

> "then you'll see often on that day the market goes and closes the gap."

**Source GPS: 96iPFDpXEcU | END** [TOM-237]

Testable form: for G08-tagged gaps (political), P(fill on gap day) vs P(fill on the next session). DATA-NEEDED for the tag. Day 1 = last pre-gap
session, day 2 = gap session, day 3 = the following session.

### G10 - Product matters: commodity-type gaps (limit moves, hedging) are not DAX-like

> "So, you have to know which product has which internal characteristics."

**Source GPS: 96iPFDpXEcU | MIDDLE** [TOM-238]

> "The hedgers, that is, those who carry out the hedging transactions, they have to hedge themselves."

**Source GPS: 96iPFDpXEcU | MIDDLE** [TOM-239]

> "You can forget about such markets closing such a price gap extremely quickly."

**Source GPS: 96iPFDpXEcU | MIDDLE** [TOM-240]

Testable form: scope rule only. He ties the hedger effect to commodity futures (limit up/down), not to index futures. For DAX there is NO statement that the
hedger effect applies: do not port commodity gap-persistence to DAX (NO-SOURCE for DAX).

---

## 5. AFTER THE OPEN: ACCEPTANCE OR REJECTION OF THE GAP

### G11 - If the gap-fill speculators are wrong at the open, prices are accepted

Rule: after a news gap, watch the opening behaviour. A brief move toward the gap close that fails and turns back with time spent at the new levels
means supply and demand moved to the new range; gap-close bets were wrong.

> "The second thing I do now of course is look at how the market behaves at the opening of trading."

**Source GPS: YopZ5ZDmMFw | MIDDLE** [TOM-241]

> "It tells me that the people who speculated down here on gap closes were initially wrong. It also gives me further information namely that I see supply and demand have shifted to a new higher price range."

**Source GPS: YopZ5ZDmMFw | MIDDLE** [TOM-242]

> "And with that, I know that market participants are accepting these higher prices because they are spending a lot of time here."

**Source GPS: YopZ5ZDmMFw | MIDDLE** [TOM-243]

Testable form: gap up; early dip toward prior close that does not fill and reverses up; then count time spent above the dip low. "A lot of time": NO-SOURCE.
Mirror for gap down. (The "down here" depth of the dip is not stated: the test uses "any pullback that stays above the prior close".)

### G12 - Daily-chart gap check: where did it open, where was the close, is a close probable

> "Then I look at the next time frame on the daily chart. What does the whole thing look like? How was the market opening? Where was my closing price? Is there a high probability that the gap will be closed or not?"

**Source GPS: YopZ5ZDmMFw | END** [TOM-244]

> "Like here when I see that strength is simply coming into the market after the market went down at the opening then I have an important piece of information."

**Source GPS: YopZ5ZDmMFw | END** [TOM-245]

Testable form: first quote = list of inputs (open, prior close, probability of close). Second quote: gap down at the open followed by strength coming in is
"important information" (direction of the implication, and what counts as "strength", is not stated: for the test, treat it as a failed gap-down continuation = G11 mirror).
CONTEXT-NEEDED (second quote): "Like here" points at a chart moment; the direction of the implication is not stated, so only the G11 mirror reading is testable.

### G13 - Huge gaps: the market goes lethargic; ranges and P structure follow

Rule: after a really huge gap the market is lethargic while participants redefine themselves; then use value (space area) to locate balance and the P structure.

> "When huge gaps occur, it's often the case, if they're really huge, that the market is a bit lethargic afterwards. That's because the market participants have to redefine themselves."

**Source GPS: 96iPFDpXEcU | END** [TOM-246]

Testable form: after a "huge" gap (NO-SOURCE: no size), the first N 1m bars after the open show lower range/volume than normal. N: NO-SOURCE.

### G13b - Moving the value area over to the gap (CONTEXT-NEEDED)

> "And now you go and take the space area, and look at where the balance is. You transfer that over here and then you have a P structure. And this structure, this gap structure, is nothing more than a dynamic impulse without substance."

**Source GPS: 96iPFDpXEcU | END** [TOM-247]

CONTEXT-NEEDED: "the space area" and "over here" are pointers on a drawing; the quote does not say which prior zone is transferred to which level.
Do not backtest until this is resolved with the screenshot/video frame; "gap structure = a dynamic impulse without substance" is usable as a label only.

---

## 6. TRADING THE GAP CLOSE: SEQUENCE AND ENTRY

### G14 - Gap close entry: wait for the failed extension, the range and the liquidity return

Rule: sequence in his words: gap, break further out with falling liquidity (participants lose interest), return into a range, move out of the range in the
gap-closing direction with rising liquidity: then the close is "a very high probability" and the risk/reward is good.

> "Now comes the break upwards and the liquidity decreases. What does that mean? It means that many market participants no longer have any interest up there."

**Source GPS: 96iPFDpXEcU | END** [TOM-248]

> "Now the market goes back into a range and eventually goes below the range. And if it goes below the range and liquidity increases again, then you can reasonably expect that the gap will be closed. It's a very high probability and is simply a great thing from a logical standpoint."

**Source GPS: 96iPFDpXEcU | END** [TOM-249]

> "But if you just wait a moment until the liquidity goes down and then increases again, then the probability is much higher that you can trade this gap close with a great risk reward ratio."

**Source GPS: 96iPFDpXEcU | END** [TOM-250]

Testable form (gap up; mirror for gap down): (1) 1m volume falls while price extends beyond the opening zone; (2) price returns inside a range; (3) price closes below that range's low with volume above its
range-average: entry short, target = previous cash close. Range definition, volume comparison window and stop are NO-SOURCE in these quotes (stop/target: see G20, G21).

### G15 - News gap: a range after the move blocks the close; leaving the range with new liquidity allows it

> "if a quick move happens after the news and then a range forms, please be careful that these gaps get closed only when the market leaves this range again and also signals that there's new liquidity, then you can trade for the gap to be closed."

**Source GPS: lO-Iptd29t4 | END** [TOM-251]

> "And we already know the PBD logic, and then you can already see, as long as the market holds this range, you shouldn't expect this gap to be closed."

**Source GPS: lO-Iptd29t4 | MIDDLE** [TOM-252]

Testable form: a balance (range) with accepted volume forming after the gap and holding blocks the fill; test fill probability while price stays in the post-gap range vs after
a range break accompanied by a volume increase. The first quote is self-contained and defines "this range" as the range formed after the quick move.

### G16 - Gap not closed and liquidity returns: continue with the trend

> "Now the market might briefly move above it again, but doesn't close the gap, and the liquidity returns. Then you are allowed to trade in the direction of the trend here using the corresponding structures available to you."

**Source GPS: lO-Iptd29t4 | END** [TOM-253]

Testable form: gap-direction continuation after a post-gap range that does not close the gap, with volume back; the entry structures are other layers (not specified here).
CONTEXT-NEEDED (small): "above it" has no stated level; for the test it is read as above the post-gap range. Entry structure: NO-SOURCE in this passage.

### G18 - Intraday bar-to-bar price gaps (footprint): stop using them as a strategy

> "These price gaps were closed in well over 95% of cases. In the meantime, liquidity has dried up. So, stop using the strategy of looking for these intraday price gaps in the footprint charts."

**Source GPS: lO-Iptd29t4 | END** [TOM-254]

> "If the market shoots up and leaves price gaps behind, those gaps often never get filled."

**Source GPS: lO-Iptd29t4 | END** [TOM-255]

Testable form: negative rule, do not build a layer on intraday footprint-block gaps. A descriptive check on 1m DAX bars (bar low > prior bar high) is allowed only to confirm that the historical
fill rate has declined; the ">95%" is his historical claim, not a parameter.

---

## 7. THE GAP-FADE TRADE (EXAGGERATION) AND ITS MANAGEMENT

### G19 - Gap outside the prior range with no sustainable fundamental story: plan a short back toward the prior value

Rule: market fully outside the previous day's range, thin volume at first, then increasing volume with many more sales than purchases; the open has an immediate impulse then lethargy with large sales volume:
plan the counter (short) trade; the target is the prior day's value area; probability of the close is there when the exaggeration has no sustainable fundamental origin.

> "That means the market was completely outside of the previous day's range."

**Source GPS: l8RZrBfzvp4 | BEGIN** [TOM-256]

> "And then for me it's always like this. I say the probability that the market returns to balance, especially if there's no fundamental sustainable story."

**Source GPS: l8RZrBfzvp4 | MIDDLE** [TOM-257]

> "The story is the probability of a gap close is there. The exaggeration has no fundamental origin that is sustainable."

**Source GPS: l8RZrBfzvp4 | END** [TOM-258]

Testable form: open outside previous-session range; first minutes after the open show a sell-volume (ask hit vs bid hit) dominance at the top of the range for a gap up; short; target = previous-session value area. "Many more sales than purchases" has no ratio: NO-SOURCE.
Fundamental-story tag: DATA-NEEDED (see G07/G08).

### G20 - Proof of selling: price trades below the cash-open price

Rule: a trade below the opening trade price is proof that pre-session buyers who jumped in at the open are under water; the pullback after this is the best entry spot.

> "Second, what this does is it provides me with clear proof that all of the buyers who entered during the pre-session, those participants who came in before the official market opening, then immediately jumped right into the market at the cash open without any hesitation. They have already been traded below."

**Source GPS: l8RZrBfzvp4 | MIDDLE** [TOM-259]

> "Look, if the market had such a zone and has already provided me with proof that weakness can occur, then I have a great combination and that means at this point at the latest, it is by far the best spot for people who like to enter the market on a pullback."

**Source GPS: l8RZrBfzvp4 | MIDDLE** [TOM-260]

> "And then you know, there were strong sellers here. This means your stop loss is definitely in a great position here because if the market were to go above that, there is a high probability that other market participants will be pushed out and an upward impulse is created."

**Source GPS: l8RZrBfzvp4 | MIDDLE** [TOM-261]

Testable form: gap up; after the opening impulse and lethargy, price trades below the cash-open price (first cash trade). Entry: pullback after that proof. Stop: CONTEXT-NEEDED, "here" and "that" in the third quote
point at the strong-seller zone on the chart (the box), with no stated level: do not code a stop from this quote; the zone's top is the likely reading but it is not in his words.

### G21 - Take profit short of the prior value area (CONTEXT-NEEDED)

> "That is why I said I would rather set my take profit a few points away from this range because often it is exactly the case that such levels that everyone sees, remember this was the value area, are not hit at first."

**Source GPS: l8RZrBfzvp4 | MIDDLE** [TOM-262]

CONTEXT-NEEDED: "a few points away" is not a number (NO-SOURCE) and "this range" is the first pre-session balance pointed at on the chart, not the value area named in the same sentence.
Testable only as a measurement: how often the prior value area edge is NOT touched on gap-fade trades (descriptive, no tuning).

### G22 - Gap fade failed attempts: stopped early is part of it (CONTEXT-NEEDED for the pre-session entry)

> "And it doesn't always have to work directly on the first trade because especially in the phases where the market starts at the opening, it is often the case that a lot of games take place there."

**Source GPS: l8RZrBfzvp4 | END** [TOM-263]

CONTEXT-NEEDED: "the first trade" refers to the pre-session attempt he was stopped out of (one R) in this chart; the quote gives no rule for a re-entry limit or a time rule. Use only as evidence that a second entry after the stop is allowed;
no count or window is stated (NO-SOURCE).

---

## 8. THE GAP AS A TARGET OR A LEVEL; CLOSING AUCTION

### G23 - Closing-auction gaps: trade back to original value, and reversals after a strong close

Rule: ETF/index trackers must route their volume in the closing auction; when much of the day's volume is pushed in at the close, a gap results; it can be traded back. A close at an extreme that gaps the other way at next day's open
and then reverses is a contrarian entry.

> "And you can trade great gap strategies there off exchange, for example, when you see that at the closing price they've pushed another 60% of their total volume into the market. And as a result, of course, a price gap has emerged because they didn't get it at a single price. And you can then trade something like that back to the original value."

**Source GPS: DVZVE9rXGtU | BEGIN** [TOM-264]

> "Most of the time in the closing auction, if another extreme is reached there, you'll see a gap down at the open the next day and then things start to reverse. And that's when you can short."

**Source GPS: DVZVE9rXGtU | MIDDLE** [TOM-265]

> "So, if the market closes really strong and the next day it goes back into the red, then it just makes sense to take a contrarian position."

**Source GPS: DVZVE9rXGtU | MIDDLE** [TOM-266]

Testable form: DATA-NEEDED, closing-auction volume share is not in 1m bars (the 60% is his illustration of one observation, not a threshold: NO-SOURCE as parameter). Part B on 1m bars: cash-session close at the day's extreme (extreme: NO-SOURCE), next
day opens lower (gap down), then reversal and short. "The original value" is not defined (prior close? value area?): CONTEXT-NEEDED for part A only; part B is self-contained.

### G24 - An intraday price gap that price ran through fast is a target area

> "What's exciting for me is that the market simply showed me a huge intraday price gap during main trading hours. And those are always nice areas that I like to define as targets. Because what happened there? The market ran through there extremely strongly and quickly."

**Source GPS: ujedEcmvBMk | MIDDLE** [TOM-267]

Testable form: during main hours, a fast run leaving a zone with little trading (price discontinuity / thin 1m volume) becomes a target level for an open position. "Huge" size and the exact edge to use: NO-SOURCE. Note this is
the one place he treats an intraday gap as useful, in contrast to G18 (footprint-block gaps as an entry strategy).

### G25 - Caution at a thin-volume range edge: reduce the position (CONTEXT-NEEDED)

> "Whenever the last volumes before such a price range are not traded, caution is advised, which prompted me to first reduce my position and say, well, what you have, you have."

**Source GPS: ujedEcmvBMk | MIDDLE** [TOM-268]

CONTEXT-NEEDED: "such a price range" points at the gap area on the chart and "the last volumes before" it are pointed at on a profile: the quote does not give the level or what portion to reduce (NO-SOURCE).
Not testable until a frame is read.

### G26 - A gap that formed outside cash hours is not a substantial support zone (CONTEXT-NEEDED)

> "There was never any trading here. So, is this price area interesting for us or is it just boring because there probably won't be any support there?"

**Source GPS: 3JqMyzE8jIQ | END** [TOM-269]

> "And now look over here and you'll see I'm talking exactly about this price area where in this picture the market during cash hours has no substantial support zone at all. It may pause there briefly, but it's not substantial."

**Source GPS: 3JqMyzE8jIQ | END** [TOM-270]

CONTEXT-NEEDED: "this price area" and "over here" point at a drawing; the principle (an overnight gap area with no cash-session volume gives no substantial support, price only pauses) is clear, the level is not.
Testable principle: after an overnight gap, price crossing the gap zone does not hold there; measure pause time vs a volume-supported level. The pause length is NO-SOURCE.

---

## 9. EXCLUDED AND RECONCILIATION

- 5Ljfwvtktek (interview with a guest trader): "gap" there is a fair-value-gap / intraday-structure discussion, the speakers are not separable in the cleaned text, and Tom's own line ("I actually never see gaps there",
  S&P) is about a different instrument and ambiguous in meaning. Read in full, no rule extracted. Not counted.
- Fair value gap passages in 3JqMyzE8jIQ and Of_wlv3xaZo: out of scope (already extracted).
- Numbers in his words but NOT parameters: 80% (name of a rule, G05), 60% (illustration, G23), >95% (history, G18), one R / four R (a trade example, G22).

Rule numbering note: G17 and G18 sit in sections 3 and 6 by topic, so ids are not sequential in the file. G13b is counted as its own rule (27 total).
