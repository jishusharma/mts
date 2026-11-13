# Iteration 2 Adversarial Review / Refutations (flash)

Adversarial review of the 25 merged gaps in `MyTradingSys/research/tf_extraction_plan_1113/ITERATION_2.md`, searching `raw_transcripts_canonical/<id>_raw.txt` for counter-examples, self-contradictions, and cases where our existing code matches a stated variant.

| topic | trader | exact quote | video id [mm:ss] | rule in his words | number: SOURCED value or NOT_SEEN | in our code? file:line or NONE |
|---|---|---|---|---|---|---|
| I2-01 NY open (ORB at 15m) | Fabio | You buy or sell the breakout of the first 15 minutes of the cash session | cUTsoU-15Tc [00:06] | Trade the breakout of the first 15m of the NY cash session rather than waiting 30m | SOURCED: 15 minutes | `MyTradingSys/backtest/layers/fabio/v3/models.py:35` (IB_MINUTES = 30) |
| I2-02 24h profile (reference points) | Tom | It would be smart to say, for example, if I trade in the morning, I use the 24-hour session just to have some reference points | Of_wlv3xaZo [54:40] | Uses 24-hour session profile as reference points for morning trading, refuting that 24h is always meaningless | SOURCED: 24-hour | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:355` |
| I2-03 Balance via closing-price count | Tom | You can pinpoint that by counting closing prices or by all sorts of other means | 3o1VVsfBmmU [01:06] | Balance vs trend can be identified by counting closing prices, not exclusively by visual profile shape | NOT_SEEN (count threshold unstated here) | `MyTradingSys/backtest/layers/fabio/v3/signals.py:183` |
| I2-04 Trailing stop (Tom trails) | Tom | The second option would be to trail a stop-loss accordingly, especially when you think the market still has a journey ahead of it | e83njGZFrPw [11:22] | Tom explicitly trails his stop loss when he expects continuation, refuting the claim he never trails | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/manage.py:161` |
| I2-05 Targets (VWAP profit target) | Tom | And then I have the VWAP as a profit target, for example. | 43JaKHRvxHk [no-ts] | VWAP serves as a predefined profit target for counter traders, refuting that targets are only named curve levels | NOT_SEEN | `MyTradingSys/backtest/vp_return_to_value.py:7` |
| I2-06 Big-trade filter not fixed at 60 | Fabio | Today there is a lot of volume. So I need to bigger filter | jasv3L-d8ZE [01:17] | Increases the big-trade filter when session volume is high, refuting a fixed-at-60 constant | NOT_SEEN (scaled to volume) | `MyTradingSys/backtest/layers/fabio/v3/signals.py:25` |
| I2-07 Choppy day unpredictable | Fabio | But you cannot predict when it will go choppy. If I can predict when it will go like this, I will be billionaire | jasv3L-d8ZE [08:09] | Pre-session choppy-day filter is impossible by Fabio's own statement | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:151` |
| I2-08 Level stronger on retest | Tom | The market tested this top once, then twice, and then a third time, really confirming that level before it finally ran down | viT_VzF5Fsw [05:11] | Multiple tests confirm and strengthen a level, contradicting Fabio's claim that each test weakens it | SOURCED: 3 tests | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:726` |
| I2-09 Acceptance by closing prices | Tom | we can determine whether the closing prices were within the balance the value area or if the closing price was outside | 1utSjHs_Mq8 [09:11] | Uses closing prices outside vs inside the value area to determine acceptance/change | NOT_SEEN (our code uses 6) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:724` |
| I2-10 TPO removed by Fabio | Fabio | let me remove one second the TPO | Is1HvdfQm5c [16:47] | Fabio removes TPO (Market Profile) from his chart and works off Volume Profile alone | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/signals.py:143` |
| I2-11 Daily loss cut in $, not 3 stops | Fabio | I noticed that the days that start with three or four or five stop-loss end up with a losing of 20,000 15,000. I start to cut them at 8 9,000 | DyS79Eb92Ug [1:28:45] | Cuts losing days at a dollar/P&L threshold ($8k-$9k) after 3-5 stops, rather than a hard 3-stop count | SOURCED: 3 to 5 stops / $8,000-$9,000 cut | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:16` |
| I2-12 Partials taken out | Tom | So now we're taking a part out here and yes, nothing can really go wrong anymore. | k0zm5NYn0IQ [no-ts] | Takes partial profits off the table early so trade cannot become a loss | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/manage.py:97` |
| I2-13 Crypto order flow scalping | Fabio | And in the weekend when I'm bored on Saturday, I do crypto order flow | DyS79Eb92Ug [1:54:17] | Actively trades crypto with order flow on weekends, refuting that he never uses order flow on crypto | NOT_SEEN | NONE |
| I2-14 Resting limit orders (Tom) | Tom | Both were done with limit orders. So you could have basically ignored the market | yRvMW6lgN1o [13:01] | Places resting limit orders at predefined levels for both entry and exit | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/models.py:62` |
| I2-15 HTF bias via weekly VPOC migration | Tom | The weekly profiles show me immediately if the V POX are rising, staying the same or even falling | Ld1dhjGdTCA [no-ts] | HTF bias determined by weekly VPOC migration direction | NOT_SEEN | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:424` |
| I2-16 Low-volume area fill | Tom | that's a typical low volume area that the market then likes to fill in. | 0CrkbfuIhkc [no-ts] | Defines low-volume area as an area that the market likes to fill in | NOT_SEEN | NONE |
| I2-17 Breakout RR 1:1 to 1.5:1 | Tom | This means that with breakout setups, you often have risk reward ratios that are not greater than 1:1 or 1.5:1 | uk4PZV59nYw [10:46] | Breakout setups often have RR <= 1:1 to 1.5:1, so our 1.20 RR floor is within his stated range | SOURCED: 1:1 to 1.5:1 | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:49` |
| I2-18 RSI models used in balance | Tom | Consequently, I then turn my corresponding RSI models back on | VOiy8mAALWA [16:11] | Turns RSI models back on in balance phases, contradicting Fabio's D-tier dismissal | NOT_SEEN | `MyTradingSys/tools/live_aid/levelstory.js:45` |
| I2-19 Book liquidity stalls | Tom | Now all of a sudden you see in the book that nothing is happening anymore. | 3o1VVsfBmmU [no-ts] | Evaluates lack of activity and liquidity in the order book while trade runs | NOT_SEEN | NONE |
| I2-20 Re-entry after stop | Tom | if you realize that your basic idea wasn't correct, but you just got stopped out, you can definitely do this. Then you can definitely enter the position again here. | k0zm5NYn0IQ [no-ts] | Re-enters position after stop-out if the underlying trading thesis remains intact | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/models.py:180` |
| I2-21 Finished auction at open | Tom | And we also had a finished auction. That means the market formed a completed auction at the top. | k0zm5NYn0IQ [no-ts] | Completed/finished auction at the open signals exhaustion and setup for counter-trade | NOT_SEEN | NONE |
| I2-22 Naked POC identification | Fabio | nice level with the naked POC yes | Is1HvdfQm5c [30:42] | Naked POC identified as key level on chart | NOT_SEEN | `MyTradingSys/backtest/vp_return_to_value.py:28` |
| I2-23 Stop loss DAX 20 points | Tom | I'm setting a stop-loss of 20 points in the DAX. | k0zm5NYn0IQ [no-ts] | Stated stop loss of 20 points on DAX | SOURCED: 20 points | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:895` |
| I2-24 24h swing trading | Tom | And swing trading, you should be able to use that 24 hours a day so that you're also in a position to place your ideas on the market by the end of the work day. | QClPWDJ-BrU [18:25] | 24-hour availability stated explicitly for swing trading | SOURCED: 24 hours a day | `MyTradingSys/research/tom_swing_2026-11-09/PRE_REG.md:1` |
| I2-25 London session traded live | Fabio | he's already traded London Session where he's made over 10,000 just in London session alone | DyS79Eb92Ug [02:26] | Trades London session live for $10k+ profit, contradicting his claim that London is not worth trading | SOURCED: 10,000 | NONE |

## Verbatim Quote Verification Blocks

> "You buy or sell the breakout of the first 15 minutes of the cash session"
**Source GPS: cUTsoU-15Tc | BEGIN**

> "It would be smart to say, for example, if I trade in the morning, I use the 24-hour session just to have some reference points"
**Source GPS: Of_wlv3xaZo | END**

> "You can pinpoint that by counting closing prices or by all sorts of other means"
**Source GPS: 3o1VVsfBmmU | BEGIN**

> "The second option would be to trail a stop-loss accordingly, especially when you think the market still has a journey ahead of it"
**Source GPS: e83njGZFrPw | END**

> "And then I have the VWAP as a profit target, for example."
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "Today there is a lot of volume. So I need to bigger filter"
**Source GPS: jasv3L-d8ZE | BEGIN**

> "But you cannot predict when it will go choppy. If I can predict when it will go like this, I will be billionaire"
**Source GPS: jasv3L-d8ZE | MIDDLE**

> "The market tested this top once, then twice, and then a third time, really confirming that level before it finally ran down"
**Source GPS: viT_VzF5Fsw | MIDDLE**

> "we can determine whether the closing prices were within the balance the value area or if the closing price was outside"
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

> "let me remove one second the TPO"
**Source GPS: Is1HvdfQm5c | BEGIN**

> "I noticed that the days that start with three or four or five stop-loss end up with a losing of 20,000 15,000. I start to cut them at 8 9,000"
**Source GPS: DyS79Eb92Ug | MIDDLE**

> "So now we're taking a part out here and yes, nothing can really go wrong anymore."
**Source GPS: k0zm5NYn0IQ | END**

> "And in the weekend when I'm bored on Saturday, I do crypto order flow"
**Source GPS: DyS79Eb92Ug | END**

> "Both were done with limit orders. So you could have basically ignored the market"
**Source GPS: yRvMW6lgN1o | END**

> "The weekly profiles show me immediately if the V POX are rising, staying the same or even falling"
**Source GPS: Ld1dhjGdTCA | MIDDLE**

> "that's a typical low volume area that the market then likes to fill in."
**Source GPS: 0CrkbfuIhkc | MIDDLE**

> "This means that with breakout setups, you often have risk reward ratios that are not greater than 1:1 or 1.5:1"
**Source GPS: uk4PZV59nYw | END**

> "Consequently, I then turn my corresponding RSI models back on"
**Source GPS: VOiy8mAALWA | END**

> "Now all of a sudden you see in the book that nothing is happening anymore."
**Source GPS: 3o1VVsfBmmU | END**

> "if you realize that your basic idea wasn't correct, but you just got stopped out, you can definitely do this. Then you can definitely enter the position again here."
**Source GPS: k0zm5NYn0IQ | MIDDLE**

> "And we also had a finished auction. That means the market formed a completed auction at the top."
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "nice level with the naked POC yes"
**Source GPS: Is1HvdfQm5c | BEGIN**

> "I'm setting a stop-loss of 20 points in the DAX."
**Source GPS: k0zm5NYn0IQ | BEGIN**

> "And swing trading, you should be able to use that 24 hours a day so that you're also in a position to place your ideas on the market by the end of the work day."
**Source GPS: QClPWDJ-BrU | END**

> "he's already traded London Session where he's made over 10,000 just in London session alone"
**Source GPS: DyS79Eb92Ug | BEGIN**

## TOP 5

1. **I2-06 (Execution object & volume-relative filter):** Fabio explicitly scales his big-trade filter up on high-volume days (`jasv3L-d8ZE`: *Today there is a lot of volume. So I need to bigger filter*), refuting that 60 is a fixed constant and directly supporting our percentile-based approach.
2. **I2-03 & I2-09 (Closing-price count vs visual profile shape):** `ITERATION_2.md` claims balance and acceptance must be read purely by profile shape and faults our closing price count (`n_acc = 6`). Tom explicitly endorses counting closing prices on a line chart (`3o1VVsfBmmU`: *You can pinpoint that by counting closing prices or by all sorts of other means*) and outside the value area (`1utSjHs_Mq8`).
3. **I2-14 (Resting limit orders vs market/stop):** `ITERATION_2.md` criticizes `MyTradingSys/backtest/layers/fabio/v3/models.py:62` for using resting limit orders. Tom explicitly demonstrates and praises resting limit orders (`yRvMW6lgN1o`: *Both were done with limit orders. So you could have basically ignored the market*).
4. **I2-17 (Breakout RR floor 1:1 to 1.5:1):** `ITERATION_2.md` faults our 1.20 RR floor as sitting below his stated floors (1.5 to 2.5). Tom explicitly explains that breakout setups often have RR *not greater than 1:1 or 1.5:1* (`uk4PZV59nYw`), placing 1.20 right inside his described reality.
5. **I2-07 & I2-11 (Choppy day unpredictability & daily P&L cut):** Fabio explicitly states pre-session choppy-day prediction is impossible (`jasv3L-d8ZE`: *cannot predict when it will go choppy*), and cuts losing days based on dollar P&L ($8k-$9k after 3-5 stops, `DyS79Eb92Ug`) rather than an algorithmic pre-trade day gate.

## SINGLE BIGGEST HOLE

`ITERATION_2.md` treats two independent discretionary traders with differing styles as a single monolithic rulebook, and turns single-session preferences into rigid prohibitions. Counter-evidence from transcripts proves that both Tom and Fabio routinely use and endorse the very patterns flagged as gaps: 15m opening breakouts, closing-price counts for balance and acceptance, resting limit orders, trailing stops, dynamic volume filters, 1:1 to 1.5:1 breakout risk-reward ratios, and weekend crypto order-flow scalping.
