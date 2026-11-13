# Gap hunt iteration 2: merged and ranked (2026-11-13)

Sources: four hunters plus the DSA revalidation. Gemini blind map: **pending** (card `gemini-blind-concept-map-1113`; not waited for, add its rows when it lands).
Hunters: **opus** = opus_trade_replay (10 narrated trades, 104 steps, TR1-TR25); **sonnet-cond** = sonnet_conditions (G01-G26); **sonnet-param** = sonnet_param_trace (PT-01..PT-18); **haiku** = haiku_vocab (V1-V11). Notes folder: `gap_hunt_1113/` in the side-session notes.
Third check 2026-11-13: `THIRD_CHECK_I2_REFUTE.md` (this folder) re-read 8 argon refute rows; amended I2-01, I2-03, I2-06, I2-11, I2-13, I2-17 (markers inline); I2-08 untouched (IR-14 REFUTED, gap stands).
Ranking: number of distinct hunters, ties stage T first. Iteration-1 column: Y = iteration 1 already covers it, P = partly (a question exists, the new part is not covered), N = not covered. Iteration 1 = PLAN.md questions Q1-Q14 in this folder.
Speaker labels on quotes: Tom = Tom channel set, Fabio = Fabio set, GUEST and CONTESTED as in the hunters' files; ASR = machine captions.

## 1. Table of merged gaps (25 rows)

| id | stage | pattern | gap | hunters | iter 1 | fix type | card |
|---|---|---|---|---|---|---|---|
| I2-01 | T | 5 | NY open handling: he waits for the opening range (15 to 30 minutes, 60 for slower use) to complete, then trades the breakout or retest; Tom stops trading in the first 30 minutes; ours starts at the open with no wait (was: "he skips or waits the first 30 minutes and reads the open type"; "skips" deleted) [amended 2026-11-13 per THIRD_CHECK_I2_REFUTE IR-01: PARTIAL] | 4: opus, cond, param, haiku | P (Q7 windows) | extract | tf-y3 |
| I2-02 | C/T | 5 | Every value area is a 24h UTC day; Tom calls that meaningless for a cash-session trader; the NY-session function exists and nothing calls it | 4: opus, cond, param, haiku | P (Q8) | re-frame + test | none |
| I2-03 | C | 1,3,4 | Balance is read by a closing-price count on a line chart as first pass, then by weekly and daily profile shape, which picks the setup (counter, breakout, trend); ours is a 60-minute box true in 3.1% of windows (was: "read by profile shape", not exclusive) [amended 2026-11-13 per THIRD_CHECK_I2_REFUTE IR-05: PARTIAL] | 4: opus, cond, param, haiku | P (Q1, Q2) | extract | tf-y1 |
| I2-04 | T | 4 | Break-even and trail are events (immediately, not even one candle, only at the opposite level); ours is a distance of 1 D that is 5-8x his stop | 3: opus, cond, param | P (Q6) | re-code + test | none |
| I2-05 | T | 4 | Targets are named levels (far side of range, curve low, impulse origin, measured move); ours is the nearest volume node and models A/C/D have none | 3: opus, cond, param | P (Q10) | extract | tf-y4 |
| I2-06 | T | 1,4 | Execution object: he prefers range bars (40/80) at the open but accepts one-minute; he sets the big-trade filter by session volume (60 on the Is1HvdfQm5c chart, raised on a high-volume day; units NOT_SEEN); 5m-close trigger; v3 uses 1m bars and a percentile (was: "range bars (40/80) and a fixed big-trade filter 60"; bar type is not a gap) [amended 2026-11-13 per THIRD_CHECK_I2_REFUTE IR-08: CONFIRMED; IR-09: PARTIAL] | 3: opus, param, haiku | N | extract | tf-y6 |
| I2-07 | T | NEW | Day filters never coded: news/gap skip, choppy or fully absorbed day, bias-only trades, opening-range size, volatility regime, day-side lock | 3: opus, cond, param | N | extract | tf-y3 |
| I2-08 | C | 1,3,4 | Proof is a sequence and a volume shape (falling volume under VAH, spike then trade-off, level weaker each test, delta never alone); ours is one event | 3: opus, cond, param | P (Q11) | extract | tf-y5 |
| I2-09 | C | 1,3 | Acceptance is a new range forming outside the level; ours counts 6 closes, three code versions disagree, docstring cites the wrong source | 3: opus, cond, param | P (Q3) | re-frame + re-code | none |
| I2-10 | C/E | 2 | Market profile (time at price, 30-minute blocks, single prints, tails) is a level source in 23 videos; docs and code hold only volume profile | 3: opus, param, haiku | P (30-min TPO note) | extract | tf-y2 |
| I2-11 | T | NEW | Day rules coded but called by no engine; his P&L-keyed management, 3-stop day and trade-count limits are not in the tests | 2: opus, cond | P (Q12) | re-code + test | none |
| I2-12 | T | 4 | Partials, runner, scale-in from a part size, and adds (two different add rules) cannot be expressed: one exit per leg | 2: opus, param | P (Q6) | re-code + test | none |
| I2-13 | T | 5 | Fabio on order flow for Bitcoin: scalps crypto futures with order flow as income (weekends, own account); the "no order flow for Bitcoin, on-chain" line refers to his long-term account; not a contradiction (was: one line says he does not use it, another says crypto order-flow scalping is extremely profitable) [amended 2026-11-13 per THIRD_CHECK_I2_REFUTE IR-19: CONFIRMED] | 2: cond, param | N | extract | tf-y6 |
| I2-14 | T | NEW | Entry order type: market or half-candle limit (rule unstated), buy-stop entry before the 5m close, pullback entry; ours is a rest limit or next open | 2: opus, haiku | N | extract | tf-y6 |
| I2-15 | C | 4 | Higher-timeframe bias is weekly or 10-day volume-profile migration and the last reaction; ours is a candle ladder (monthly colour vs 20M SMA) | 2: opus, param | P (Q8) | extract | tf-y1 |
| I2-16 | C | 3 | Low-volume area means four different things (fill target, edge scalp, trend join, in-VA gap); his words say volume area for a low-volume gap | 2: param, haiku | N | extract + re-frame | tf-y2 |
| I2-17 | C | 4 | Setup grade (AAA = value-area low plus 30 minutes in) drives size; our sizing tier and 1.20 RR floor are OURS; Tom says breakout RR is often 1:1 to 1.5:1, Fabio reports 1:2 to 1:2.5 with order-flow entries; no stated floor seen (was: "sit below his stated floors"; 'his stated floors 1.5 to 2.5' is NOT_SEEN) [amended 2026-11-13 per THIRD_CHECK_I2_REFUTE IR-23: PARTIAL] | 2: opus, param | P (Q12) | re-frame | none |
| I2-18 | E | NEW | Tool tier list (footprint A, MACD F, Bollinger F, RSI D) never used; Live Aid header credits Tom and Fabio for Bollinger, WaveTrend and OI votes | 2: haiku, param | N | extract (tiny) | tf-y6 |
| I2-19 | T | 4 | Tom reads speed and liquidity in the book while the trade runs; management and proof are conditioned on bars, no depth data | 2: cond, param | P (Q4, x5) | extract | tf-y5 |
| I2-20 | T | NEW | No re-entry after a stop on the same idea; both Tom and Fabio do it and call it part of the method | 1: opus | N | extract | tf-y4 |
| I2-21 | T | NEW | Counter-trade at an exhausted open (finished auction, forced open, no real volume) has no path; our classifier calls the bars ACCEPTED and plans the long | 1: opus | N | extract | tf-y3 |
| I2-22 | T | 1 | Labels and modules: stale acceptance docstring, naked-POC percent labelled SOURCED, dead branch, two value-area rules in AC and v3 | 1: param | N | re-frame + test | none |
| I2-23 | T | 1 | His stops fail our gates (DAX 20 pts = 8 bps; gate needs 40 bps) and Tom puts the stop beyond the whole value zone, not the wick | 1: opus (+DSA row 1) | Y (FACTS H2) | test | none |
| I2-24 | T | 3,5 | Tom's swing method is the only one he shows on Bitcoin and says works 24h; pre-reg only, never run; impulse-leg precondition missing | 1: cond | P (A8) | test | none |
| I2-25 | C | 3 | Fabio contradicts himself: NY only vs London trades, choppy day skip vs choppy day edge; no per-model record | 1: cond | P (x4) | re-frame | none |

Hunter counts are distinct hunters per merged gap. A hunter row can feed two merged rows (opus TR15 and TR17, haiku V8, param PT-09); the map in section 6 shows every row.

## 2. Expected-on-top check (supervisor items)

| item | what the files say | multi-hunter? |
|---|---|---|
| (a) context layer: balance by profile shape, weekly value migration, NY-session profile not 24h | Three sub-gaps. Balance by shape = I2-03: param PT-03/PT-09, cond G06/G08, haiku V3/V11, opus TR17. Weekly migration = I2-15: param PT-04, opus TR16/TR22 only (cond and haiku have no row). NY-session = I2-02: cond G01-G03, param PT-09, opus TR17, haiku V8. Three of the four hunters name the context or level layer as their single biggest hole (param: PT-03/PT-04, cond: G01/G02, haiku: market profile level map). | YES, all 4 hunters on the layer; migration alone is 2 |
| (b) post-fill management, 41 of 104 steps, 4 run | The figure 41 of 104 and 4 matching is opus only (checker count 104 = 23+4+37+36+4; the 41 is a hand count, not re-counted here). Direction is confirmed by cond (G18 trail contradiction, G19 no acceptance exit, G21 book-conditioned management) and param (PT-07 no-trail and planned target, section 3 partials and adds Tom side none). Haiku has no row, only the terms scale and trailing in its top 60. | YES, 3 hunters (opus, cond, param); the 41/104 count is single-source |
| (c) Fabio not using order flow on BTC | Two hunters (cond G13, param PT-01) quote the same ASR line in Is1HvdfQm5c. They do not agree on the finding: param says Fabio does not use it and the transfer is unflagged; cond adds that DyS79Eb92Ug says crypto order-flow scalping is extremely profitable, so the files show a contradiction, not a plain no. Speaker of Is1HvdfQm5c is ASR; opus and haiku have no row. | YES, 2 hunters (both Sonnet), finding = CONTRADICTION, not NO |

## 3. Evidence per gap (verbatim quotes, gated)

### I2-01 NY open handling
> "stop trading in the first 30 minutes of the New York session, and secondly, look at how big the open range is and learn from what results from that."
**Source GPS: Of_wlv3xaZo | MIDDLE** (Tom)

> "usually I wait for for European time the first 30 minutes of New York opening to to have a little bit of stability in the session."
**Source GPS: DyS79Eb92Ug | BEGIN** (Fabio)

> "how is the market opening formed? The open."
**Source GPS: 43JaKHRvxHk | MIDDLE** (Tom)
Code: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/census_session_ladder.py:138` NY block starts at the cash open, no skip. `MyTradingSys/backtest/layers/fabio/v3/models.py:35` only model C waits for the initial balance.

### I2-02 24h UTC profile versus the cash session
> "You can't say, I only trade the cash session. But then refer to 24-hour profiles. Why? That's inherently quite meaningless."
**Source GPS: Of_wlv3xaZo | END** (Tom)

> "the average move of the DAX future, for example, after the market opening is initially 180 points based on the ATR."
**Source GPS: UOBgXV20yCM | BEGIN** (Tom)
Code: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:355` defines prior_ny_session_profile; its only callers are its own tests at `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/test_auction_context.py:379`. `MyTradingSys/backtest/vp_return_to_value.py:7` builds the profile from the prior UTC day.

### I2-03 Balance by shape, setup by phase
> "depending on the profile shape, but especially 60 to 70% of the time, we have so-called balance equilibrium profiles"
**Source GPS: BB3c8visnkI | MIDDLE** (Tom)

> "these setups simply fail to perform 70% of the time."
**Source GPS: VxN5IxTwpbE | MIDDLE** (Tom)

> "Breakout trading only works when a market is out of balance."
**Source GPS: 4VXpUjhKG2U | MIDDLE** (Tom)

> "Are you more of a counter trader? Are you more of a trend following trader?"
**Source GPS: 3o1VVsfBmmU | MIDDLE** (Tom)

> "Secondly, when a market becomes strongly trending, please stop trying to get back to the VWOP."
**Source GPS: VumVuGnCcFM | END** (Tom)

> "we opened the session exactly inside of the previous value area. This is already a good sign that we're probably going to stay inside of this range for the rest of the day"
**Source GPS: 9IliXww64uM | MIDDLE** (CONTESTED speaker)
Code: `MyTradingSys/backtest/layers/fabio/v3/signals.py:183` balance() is a 60-minute box (3.1% of 1m windows per cond/param, from FACTS E16, not re-run here).

### I2-04 Break-even and trail as events
> "And the first position went to break even immediately."
**Source GPS: 0jM5Y31YJak | MIDDLE** (Fabio)

> "Trailing the stop loss is something a lot of people like to do. In this case, I don't do that"
**Source GPS: k0zm5NYn0IQ | BEGIN** (Tom)

> "I moved the stop loss to a price range where I simply expect the opposite of my long position. And before that, it doesn't make sense to move the stop-loss."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE** (Tom)

> "we have time To go stop losing at zero so fast not even one candle"
**Source GPS: Is1HvdfQm5c | MIDDLE** (Fabio, ASR)
Code: `MyTradingSys/backtest/layers/fabio/v3/manage.py:28` be_update at +be_k x D; `MyTradingSys/backtest/layers/fabio/v3/manage.py:155` dist mode; `MyTradingSys/backtest/layers/fabio/v3/manage.py:161` trail starts right after BE. Is1HvdfQm5c is ASR. Param shows Tom does not trail a planned target; cond G18 shows Tom also says he trails in other videos: treat as per-trade choice (Q6), not a rule.

### I2-05 Targets as named levels
> "the total riskto-reward to get to the low of the curve is like 1 to 16 1 to 19 on the final target."
**Source GPS: 8CWKfoSJu3c | MIDDLE** (Fabio)

> "And then I traded all the way to the other side of the range where sellers are likely to get aggressive."
**Source GPS: 9IliXww64uM | MIDDLE** (CONTESTED speaker)

> "this trade is usually, and this is the great thing, to be valued in terms of profit planning, about as large as that first impulse already showed you."
**Source GPS: 7BQPMJ39WpI | END** (Tom)

> "I actually want to get back below the liquidity from this morning specifically into this free session impulse that we saw here."
**Source GPS: k0zm5NYn0IQ | BEGIN** (Tom)
Code: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:931` targets sorted nearest first.

### I2-06 Execution bars, big-trade filter, trigger
> "the big trades guys are 60 the filter it's on 60 and you know what one time frame that I'm loving recently that is based on the range is the 80 range"
**Source GPS: Is1HvdfQm5c | MIDDLE** (Fabio, ASR)

> "I made the 40 range now. So it's a range chart because when you are in New York opening if you do one minute candle you can have huge candle and all the data inside gets aggregated."
**Source GPS: DyS79Eb92Ug | BEGIN** (Fabio)

> "And the 5-minute was about to close right over here and that was my signal for the entry."
**Source GPS: 9IliXww64uM | MIDDLE** (CONTESTED speaker)

> "I transfer these price areas over to my small simple chart. In this case, a five-minute chart."
**Source GPS: 3o1VVsfBmmU | MIDDLE** (Tom)
Code: `MyTradingSys/backtest/layers/fabio/v3/signals.py:25` profile bin and header P05: big trade is a percentile of the prior 30 days on 1m bars. Units of the number 60 are not stated in the held text (contracts or lots, instrument): NOT_SEEN until card tf-y6.

### I2-07 Day filters
> "will I even trade today or have such groundbreaking things happened overnight that brings us to the gap so I'd better stay on the sidelines for now"
**Source GPS: Ld1dhjGdTCA | BEGIN** (Tom)

> "when they are outside the timing or counter trend in respect to the bias, we don't take it."
**Source GPS: Khgj5q1-ln8 | END** (Fabio)

> "Every movement got absorbed in the first two hours. This is the worst market condition you can get for my strategy."
**Source GPS: jasv3L-d8ZE | BEGIN** (Fabio)

> "Open range, meaning the opening range. If it's very large, it likely won't hold. If it's very small, it likely will."
**Source GPS: Fj4FDZQxw0I | END** (Tom)

> "If this area gets broken, I don't want to be long for the day."
**Source GPS: DyS79Eb92Ug | BEGIN** (Fabio)

> "large institutionals generally assume increased volatility for anything over 20 and increased risk assessment and many of the large investors stay out in such market phases"
**Source GPS: C9n_d91Uitc | BEGIN** (Tom)
Code: `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:151` day_gate_open compares day range to prior ranges only; model B has no gate. Quote of 9IliXww64uM on overnight news is CONTESTED speaker and left out.

### I2-08 Proof
> "look here very crucially, the volumes kept getting lower and lower."
**Source GPS: kXhIAug0Gh8 | MIDDLE** (Tom)

> "you have an absorption at the top okay you have an aggression that is rewarded so these buyers no follow through the aggression rewarded and the buyers again absorbed you have three order flow information going in the same direction"
**Source GPS: Is1HvdfQm5c | BEGIN** (Fabio, ASR)

> "remember that every time that you attack the level the level gets weaker because other orders gets filled"
**Source GPS: Is1HvdfQm5c | BEGIN** (Fabio, ASR)

> "but please as I said don't trade the delta divergence alone, always use confirmation"
**Source GPS: rFPCtOcfUMI | END** (Tom)
UNVERIFIED: the spike-then-trade-off line (haiku and param, id HySZZSjMxF8) sits in the video description, not in the spoken text, so it is dropped; the claim that a volume spike must trade off before a counter trade rests on no verified quote here.
Code: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:726` bars_in_zone branch calls a stall under the level ACCEPTED.

### I2-09 Acceptance
> "does another sideways phase emerge after that? Then we have a new model where we can clearly say that the equilibrium, meaning the new acceptance, because the market then spends more time above or below there"
**Source GPS: Sy-x5AQ9-Pk | MIDDLE** (Tom)

> "So, in order to qualify a breakout, I wait for a range to form."
**Source GPS: 9IliXww64uM | MIDDLE** (CONTESTED speaker)

> "Not with quick spikes but with real acceptance."
**Source GPS: qLnQan0KGmQ | END** (Tom)
Code: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:724` n_acc 6; `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:726` early and in-zone branches; `MyTradingSys/tools/live_aid/levelstory.js:42` both ternary arms identical (dead branch); stale docstring at `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:13`.

### I2-10 Market profile (time-based)
> "The combination of market profile and volume profile."
**Source GPS: 3o1VVsfBmmU | BEGIN** (Tom)

> "the price never actually stayed at this specific level for more than 30 minutes"
**Source GPS: 1utSjHs_Mq8 | MIDDLE** (Tom)

> "what's called a double distribution here. And what information does this double distribution give me?"
**Source GPS: -dMWA_bbm3o | MIDDLE** (Tom)

> "There was a nice buying tail here, so strong buyers."
**Source GPS: kXhIAug0Gh8 | BEGIN** (Tom)
Haiku count: market profile in 23 videos, 71 mentions, 0 hits in the scoped docs and code.

### I2-11 Day rules not wired, P&L-keyed management
> "So if we go back to break even, we stop the session."
**Source GPS: fZlNGWvd2Ko | BEGIN** (Fabio)

> "it will be smart to take profit and to bring your balance back to break even so you can take a next trade in a calm way."
**Source GPS: 8CWKfoSJu3c | MIDDLE** (Fabio)

> "if I reach a maximum of 3 stop loss either I lower the exposure but usually a stop for the day"
**Source GPS: Is1HvdfQm5c | MIDDLE** (Fabio, ASR)

> "why are you trying to take five seven ten twenty five trades per day"
**Source GPS: Is1HvdfQm5c | BEGIN** (Fabio, ASR)
Code: `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:120` first_leg_allowed and `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:140` first_leg_risk have callers only in tests and the package init (opus git grep, not re-run). `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:16` daily stop -3 R is NO-SOURCE; his rules are a stop count (3, then lower size or stop) and a dollar cut ($8k to $9k on his account, unit conversion NOT_SEEN) (was: a count of stops only) [amended 2026-11-13 per THIRD_CHECK_I2_REFUTE IR-18: PARTIAL]. Is1HvdfQm5c is ASR.

### I2-12 Partials, scale-in, adds
> "So now we're taking a part out here and yes, nothing can really go wrong anymore."
**Source GPS: k0zm5NYn0IQ | END** (Tom)

> "Now, I didn't load it full size because I want to scale as we go up."
**Source GPS: DyS79Eb92Ug | BEGIN** (Fabio)
Code: `MyTradingSys/backtest/layers/fabio/v3/manage.py:97` single exit per leg in dist and event modes.

### I2-13 Fabio and order flow on Bitcoin
> "Bitcoin guys, I don't use order from Bitcoin. I use on-chain analysis"
**Source GPS: Is1HvdfQm5c | BEGIN** (Fabio, ASR)

> "There is nothing comparable to order flow scalping for me also on crypto is extremely profitable"
**Source GPS: DyS79Eb92Ug | END** (Fabio)

> "And in the weekend when I'm bored on Saturday, I do crypto order flow"
**Source GPS: DyS79Eb92Ug | END** (Fabio)

> "Financial markets, stock, crypto, everything, every financial asset class that comes to your mind, it's moved by a flow of orders matching liquidity."
**Source GPS: FawPrRUGNpk | BEGIN** (Fabio)
First quote is ASR with the speaker not settled in iteration 1 for this id; the other three are readable captions. Cond also records Is1HvdfQm5c saying the market is open every day, so not 5-25 trades a day (I2-11).

### I2-14 Entry order type
> "I decide to enter the trade either by a market order or alternatively by a limit order placed right at the halfway point of that specific candle."
**Source GPS: 5Ljfwvtktek | END** (GUEST)

> "I can start to build by stop."
**Source GPS: DyS79Eb92Ug | BEGIN** (Fabio)
First quote speaker is GUEST (interview). Code: `MyTradingSys/backtest/layers/fabio/v3/models.py:62` rest limit entry only.

### I2-15 Higher-timeframe bias
> "The weekly profiles show me immediately if the V POX are rising, staying the same or even falling"
**Source GPS: Ld1dhjGdTCA | MIDDLE** (Tom)

> "And I typically load the last 10 days."
**Source GPS: 9IliXww64uM | BEGIN** (CONTESTED speaker)

> "Always check what was the previous reaction."
**Source GPS: qLnQan0KGmQ | END** (Tom)
Code: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:424` bias from monthly colour vs 20M SMA and weekly streak. The streak idea appears only in a Cowen video (param), not in Tom or Fabio.

### I2-16 Low-volume area
> "that's a typical low volume area that the market then likes to fill in."
**Source GPS: 0CrkbfuIhkc | MIDDLE** (Tom)

> "an area of low volume between two peaks"
**Source GPS: 4P5WAxyPCis | MIDDLE** (GUEST)
4P5WAxyPCis speaker is not stated (guest on Tom's channel): GUEST. Param adds that Fabio's fair-value-gap LVN is the lowest bin inside a fixed A-to-B profile (o-w5Gxss6T0); not quoted here.

### I2-17 Setup grade and sizing
> "Why AAA setup? Value area low. So we are really low on the curve."
**Source GPS: DyS79Eb92Ug | BEGIN** (Fabio)
Code: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:953` sizing tier from the candle bias; min net RR 1.20 at `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:49`.

### I2-18 Tool tier list
> "MACD. >> F tier. It's lagging."
**Source GPS: 3JZH06L28us | MIDDLE** (Fabio)

> "Footprint chart. A tier. It's really reliable."
**Source GPS: 3JZH06L28us | MIDDLE** (Fabio)
Code: `MyTradingSys/tools/live_aid/levelstory.js:45` vote weights for Bollinger and WaveTrend (OURS).

### I2-19 Book reading in the trade
> "Now all of a sudden you see in the book that nothing is happening anymore."
**Source GPS: 3o1VVsfBmmU | END** (Tom)
No code possible without depth data (34 of 97 rulebook rows need L2 per FACTS C4, from param). Extract only the stated book states.

### I2-20 Re-entry after a stop
> "if you realize that your basic idea wasn't correct, but you just got stopped out, you can definitely do this. Then you can definitely enter the position again here."
**Source GPS: k0zm5NYn0IQ | MIDDLE** (Tom)

> "So I then started a re-entry."
**Source GPS: kXhIAug0Gh8 | END** (Tom)
Code: `MyTradingSys/backtest/layers/fabio/v3/models.py:180` one trade per call.

### I2-21 Counter-trade at an exhausted open
> "And we also had a finished auction. That means the market formed a completed auction at the top."
**Source GPS: k0zm5NYn0IQ | BEGIN** (Tom)
Desk replay R4 (opus): our classifier planned the opposite side on the same shape.

### I2-22 Labels and module inconsistency (no quote needed)
Code only: `MyTradingSys/backtest/vp_return_to_value.py:28` NAKED_PCT labelled SOURCED, taken from our own Java constant; `MyTradingSys/tools/live_aid/levelstory.js:42` dead branch; `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:13` stale acceptance docstring; value-area rules differ between AC and v3 (`MyTradingSys/backtest/layers/fabio/v3/signals.py:143` two-bin expansion).

### I2-23 His stops fail our gates
> "I'm setting a stop-loss of 20 points in the DAX."
**Source GPS: k0zm5NYn0IQ | BEGIN** (Tom)
Code: `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:895` fee gate; `MyTradingSys/backtest/layers/fabio/v3/models.py:38` stop floor. Default fee profile is maker entry, so the gate bites hardest on all-taker runs (DSA revalidation).

### I2-24 Tom swing method on Bitcoin
> "And swing trading, you should be able to use that 24 hours a day so that you're also in a position to place your ideas on the market by the end of the work day."
**Source GPS: QClPWDJ-BrU | END** (Tom)
Code: pre-reg only at `MyTradingSys/research/tom_swing_2026-11-09/PRE_REG.md:1`.

### I2-25 Fabio contradictions
> "I only trade in the New York session for US indices because it's where the majority of the volume get traded"
**Source GPS: Pz8f0wWW12M | END** (Fabio)

> "you know that London session is not worth to trade for me. My profit factor is really low."
**Source GPS: 0KyIEdvVKMQ | END** (Fabio)
Cond also lists DyS79Eb92Ug (host) with London trades and 06R-ebyOhDI showing a London execution; extract which instrument they trade is in tf-y3 notes only if time allows.

## 4. Stopping rule check: iteration 3

Rule: iteration 3 runs only if iteration 2 finds a pattern-2 hole = a concept named in 10+ videos and never coded. Source: haiku top-60 table (videos = distinct Tom/Fabio videos of 122). "Code check" = git grep of the term family in `MyTradingSys/backtest/`, the course-correction folder and `MyTradingSys/tools/live_aid/` on this branch (this session).

| concept (haiku row) | videos | code check | pattern-2 hole? |
|---|---|---|---|
| market profile (time-based, TPO) | 23 | no hit for tpo, single print | YES (haiku V1, already qualifies) |
| market opening / open type | 23 | no open_type or open location selector | YES |
| market phases (phase read, shapes) | 22 | only S1 box, 3.1% of windows; no phase classifier | YES (coded as a different thing) |
| distribution (P, B, D, double distribution) | 15 | no hit for double distribution or profile-shape classes | YES |
| hedging | 15 | no hit in code and no hit in scoped docs | YES (not even defined) |
| counter trading / trend following (switch by phase) | 30 / 26 | models exist, no phase-to-setup switch (no hit for the terms) | YES (the switch) |
| scale (scale in and out, partials) | 15 | adds exist in manage.py but no caller; partials none | YES |
| major market participants | 19 | no hit; a context label, low value | YES, low value |
| trend reversal | 11 | name only in bigtrade bigmoves (own study), not his concept | UNCLEAR, needs one read |
| footprint chart | 33 | footprint code exists (orderflow_bars, fabio models) | no, coded |
| breakouts | 25 | model C and IB break exist, not phase-conditional | partly (covered by the switch row) |
| aggressive buyers | 15 | big-trade push in v3 signals | no, coded in kind |
| minute chart, daily chart, candlestick chart | 25 / 10 / 10 | bars exist; the range-bar and TF-stack part is I2-06 | no |
| market makers, institutional traders | 21 / 21 | sponsor copy in 13 files | excluded |
| dax future | 18 | transfer label, not a concept | excluded |
| new york session, trading session, volume weighted | 10 / 10 / 10 | coded (NY window, VWAP) | no |

**ITERATION 3: GO.** What it should hunt:
1. The seven concept holes above (profile, open type, phase read and shapes, distribution, hedging, setup switch, scale/partials): for each, one worker reads every video that names it and writes what he says it is, a number if any, and the trade it feeds. Hedging first, it has no definition anywhere.
2. Rows 17-60 of the haiku table (5-9 videos each) with the same corpus check; 227 terms had 0-1 hits.
3. More narrated trades through the opus method: only 10 trades were replayed; the live-session videos hold more.
4. Code not yet traced for pattern 1: tom_swing PRE_REG, fabio_of_model, Java ExecutionMathConstants and the Live Aid page.
5. Compare with the Gemini blind concept map once it lands: any concept it lists that none of the four hunters found.
New methods wanted: a second reader per concept row on a different model; no Tom-only or Fabio-only passes.

## 5. Already known, not new (iteration-1 corrections from the DSA revalidation)

| item | status |
|---|---|
| DSA fee claim 1.4-2.3 R | PARTIAL: true for all-taker plus slippage runs only; default profile is maker entry, a stopped trade pays about 0.61 R, a target pays 0 |
| Audit root cause 4 (VAH counter short killed when trend healthy) | FIXED in 36513c888 (2026-11-08) and e6f378bf3 (2026-11-10); audit text not amended |
| DAX 0/7 recall | was run with DAX fees; BTC fee was not the cause (proofs 1-2 of 3 and no same-side candidate on 3 spike shorts were) |
| 116 videos naming the closing-price count | wrong: 24 of 122 Tom/Fabio videos (37 of 164 files) |
| SETUP_REVIEW rows | 15 rows, not 17; 11 with no fee-net number |

Filed by the lead (no card here): auction_context.py:47 maker fee treated per side where the argument is round trip (`fix-auction-context-maker-fee-roundtrip-1113`); Fabio v3 default management mode dist versus README event (`fix-fabio-v3-default-mgmt-dist-vs-event-1113`).

## 6. Source-row map (which hunter row feeds which merged gap)

| id | opus | sonnet-cond | sonnet-param | haiku |
|---|---|---|---|---|
| I2-01 | TR15 (30 min part) | G04 | PT-10 | V9 |
| I2-02 | TR17 (UTC day) | G01, G02, G03 | PT-09, PT-10 (TVP period) | V8 |
| I2-03 | TR17, TR7 | G06, G07, G08 | PT-03, PT-09 | V3, V11 |
| I2-04 | TR2, TR14 | G18 | PT-07 | none |
| I2-05 | TR3, TR4 | G17 | PT-07, PT-05 | none |
| I2-06 | TR15 (range chart), TR20 (5m close) | none | PT-02, PT-13 | V4 |
| I2-07 | TR25 | G05, G09, G10, G24, G25 | PT-08 | none |
| I2-08 | TR7, TR19 | G22 | PT-12 | none |
| I2-09 | TR6 | G20 | PT-06 | none |
| I2-10 | TR18 | none | PT-17 | V1, V11 |
| I2-11 | TR9, TR10, TR11 | G14, G10 (gate default off) | none | none |
| I2-12 | TR5, TR12, TR13 | none | section 3 table (partials, adds) | none |
| I2-13 | none | G13 | PT-01 | none |
| I2-14 | TR20 | none | none | V5 |
| I2-15 | TR16, TR22 | none | PT-04 | none |
| I2-16 | none | none | PT-05 | V2 |
| I2-17 | TR21 | none | PT-14 | none |
| I2-18 | none | none | PT-11 | V6 |
| I2-19 | none | G21 | section 3 table (heat-map row) | none |
| I2-20 | TR1 | none | none | none |
| I2-21 | TR8 | none | none | none |
| I2-22 | none | none | PT-06 (docstring), PT-15, PT-16 | none |
| I2-23 | TR23, TR24 | none | none | none |
| I2-24 | none | G16, G17 | none | none |
| I2-25 | none | G11, G12 | none | none |

### Singletons (not in the 25)

| source row | one line | hunter | fix |
|---|---|---|---|
| G15 | Tom uses Bitcoin as a risk lead for other markets, not as a traded value-area market | cond | re-frame |
| G23 | Tom's counter-trade needs a 40-45% hit rate for its ratio; our 1R bracket has 50% break-even | cond | test |
| G26 | v3 volume tier skips weekends, BTC weekend behaviour untested by design | cond | test |
| PT-18 | Re-entry into an old value area and acceptance means traverse to the far edge; we trade the opposite direction | param | re-code |
| V7 | major market participants as causal label for levels, never coded | haiku | re-frame |
| V10 | cumulative volume delta named in 5 videos, 1 rulebook hit | haiku | extract (low) |
| TR22 split | bias from the last reaction out of balance (kept inside I2-15) | opus | re-frame |

## 7. Cards created (extract fixes only)

Six cards, each over held transcripts, no YouTube fetch. Questions Q15-Q36 are defined here and answered per BRIEF_GAP_EXTRACT.md rules (Verdict, quotes with Source GPS, NOT_SEEN for any number he does not say). No Gemini card is needed: every id below is held.

| card | gaps | questions |
|---|---|---|
| tf-y1-phase-shape-setup-map-1113 | I2-03, I2-15 | Q15 which setup per market phase and profile shape; Q16 share of time per phase with base; Q17 how weekly or composite profile gives bias |
| tf-y2-market-profile-tpo-lvn-1113 | I2-10, I2-16 | Q18 market profile versus volume profile use; Q19 low-volume area meanings and trades; Q20 every profile-shape word with its stated meaning |
| tf-y3-open-dayfilter-exhaust-1113 | I2-01, I2-07, I2-21 (and the I2-02 sentence) | Q21 first 30 minutes and open type; Q22 day filters (news, gap, choppy, bias, volatility); Q23 exhausted open signs; Q24 24h versus cash-session profile reason |
| tf-y4-mgmt-targets-reentry-1113 | I2-05, I2-20 (and extract part of I2-11, I2-12) | Q25 target types per trade; Q26 re-entry after a stop; Q27 day P&L locks and stop counts; Q28 partials and first-size fraction |
| tf-y5-proof-volume-book-1113 | I2-08, I2-19 | Q29 what counts as proof, volume shape, touch count, delta with confirmation; Q30 what he reads in the book while in a trade |
| tf-y6-btc-orderflow-exec-entry-1113 | I2-13, I2-06, I2-14, I2-18 | Q31 order flow on crypto; Q32 range bars, big-trade filter 60 units, 5m close; Q33 entry order types and choice rule; Q34 tool tier list verdicts |

## 8. For the builder (re-code and test, no card)

| gap | one line |
|---|---|
| I2-02 | feed prior_ny_session_profile into census levels and the return-to-value count; rerun on NY-session value, weekdays only |
| I2-04 | event break-even (own-side follow-through or level failure) beside the distance mode; test BE timing against his stop size |
| I2-09 | acceptance = new balance forms outside the level, stop beyond it; one shared acceptance function; fix the stale docstring |
| I2-11 | wire first_leg_allowed, first_leg_risk and add logic into the engine; stop count instead of -3 R sum |
| I2-12 | multi-exit legs (partial, runner), first size a fraction, two add rules (Fabio after BE, Tom at retest) |
| I2-17 | label the sizing tier and 1.20 RR floor OURS; no stated floor seen (was: "floor at his stated 1.5 to 2.5", NOT_SEEN) [amended 2026-11-13 per THIRD_CHECK_I2_REFUTE IR-23: PARTIAL] |
| I2-22 | one profile library, fix labels |
| I2-23 | fee-net run at his stop sizes on a maker venue; stop anchor at the far edge of the value zone |
| I2-24 | run the pre-registered swing cells first (only cells with a stated 24h transfer) |
| I2-25 | per-model record of the Fabio contradictions |
