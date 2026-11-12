# Iteration 2 Adversarial Review / Refutations (argon)

Adversarial review of the 25 merged gaps in `MyTradingSys/research/tf_extraction_plan_1113/ITERATION_2.md`, searching `raw_transcripts_canonical/<id>_raw.txt` for counter-examples, self-contradictions, and cases where our existing code matches a stated variant.

| topic | trader | exact quote | video id [mm:ss] | rule in his words | number: SOURCED value or NOT_SEEN | in our code? file:line or NONE |
|---|---|---|---|---|---|---|
| I2-01 NY open (ORB at 15m) | Fabio | You buy or sell the breakout of the first 15 minutes of the cash session | cUTsoU-15Tc [00:04] | Trade the breakout of the first 15m of the NY cash session rather than skipping the first 30m | SOURCED: 15 minutes | `MyTradingSys/backtest/layers/fabio/v3/models.py:35` (IB_MINUTES = 30) |
| I2-01 NY open (30m liquidity) | Tom | It is sometimes the case that exactly in these 30 minutes, a lot of liquidity simply enters the market | Of_wlv3xaZo [16:45] | Acknowledges the first 30m can be where the main liquidity enters, softening a strict skip | SOURCED: 30 minutes | `MyTradingSys/backtest/layers/fabio/v3/models.py:35` |
| I2-02 24h profile (reference points) | Tom | It would be smart to say, for example, if I trade in the morning, I use the 24-hour session just to have some reference points | Of_wlv3xaZo [54:40] | Uses 24-hour session profile as reference points for morning trading, refuting that 24h is always meaningless | SOURCED: 24-hour | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:355` |
| I2-02 24h profile (swing model) | Tom | This 24-hour model was, of course, aimed at the swing trading approach | QClPWDJ-BrU [18:25] | 24-hour profile model is explicitly used for swing trading | SOURCED: 24-hour | `MyTradingSys/research/tom_swing_2026-11-09/PRE_REG.md:1` |
| I2-03 Balance via closing-price count | Tom | You can pinpoint that by counting closing prices or by all sorts of other means | 3o1VVsfBmmU [01:06] | Balance vs trend can be identified by counting closing prices, not exclusively by visual profile shape | NOT_SEEN (count threshold unstated here) | `MyTradingSys/backtest/layers/fabio/v3/signals.py:183` |
| I2-04 Trailing stop (Tom trails) | Tom | The second option would be to trail a stop-loss accordingly, especially when you think the market still has a journey ahead of it | e83njGZFrPw [11:22] | Tom explicitly trails his stop loss when he expects continuation, refuting the claim he never trails | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/manage.py:161` |
| I2-04 Trailing stop (Tom trails to high) | Tom | And then I decided to also trail the stop loss to the high | kXhIAug0Gh8 [04:19] | Tom actively trails his stop loss to the swing high in a live trade breakdown | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/manage.py:161` |
| I2-06 Big-trade filter not fixed at 60 | Fabio | Today there is a lot of volume. So I need to bigger filter | jasv3L-d8ZE [01:28] | Increases the big-trade filter when session volume is high, refuting a fixed-at-60 constant | NOT_SEEN (scaled to volume) | `MyTradingSys/backtest/layers/fabio/v3/signals.py:25` |
| I2-06 1-minute bars used (Fabio) | Fabio | i can go on 80 range i can go on 40 range i can go on one minute is it visible yes | Is1HvdfQm5c [76:01] | Reads the exact same order-flow setup on 1-minute bars as on 40/80 range bars | SOURCED: 80 range, 40 range, 1 minute | `MyTradingSys/backtest/layers/fabio/v3/signals.py:25` |
| I2-06 1-minute bars used (Tom) | Tom | for you as a short-term 1-minute scalper, is a truly great technical signal | zAwEX_tRUfE [08:00] | Teaches and endorses 1-minute chart signals for short-term scalping | SOURCED: 1-minute | `MyTradingSys/backtest/layers/fabio/v3/signals.py:25` |
| I2-07 Choppy day unpredictable | Fabio | But you cannot predict when it will go choppy. If I can predict when it will go like this, I will be billionaire | jasv3L-d8ZE [08:43] | Pre-session choppy-day filter is impossible by Fabio's own statement | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:151` |
| I2-07 Choppy session traded | Fabio | I took the choppy session to make you understand that even in days where you don't have a directional day still giving you an amazing edge when you break out | cUTsoU-15Tc [16:56] | Demonstrates trading and finding edge in a choppy, non-directional session | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:151` |
| I2-07 News/gap traded as counter-indicator | Tom | And for us in trading, that is the absolute best counter indicator | sQ_biBKhPVU [04:05] | Trades geopolitical news gaps as a counter-indicator rather than skipping news/gap days | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:151` |
| I2-08 Level stronger on retest | Tom | The market tested this top once, then twice, and then a third time, really confirming that level before it finally ran down | viT_VzF5Fsw [05:11] | Multiple tests confirm and strengthen a level, contradicting Fabio's claim that each test weakens it | SOURCED: 3 tests | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:726` |
| I2-09 Acceptance by closing prices | Tom | we can determine whether the closing prices were within the balance the value area or if the closing price was outside | 1utSjHs_Mq8 [09:11] | Uses closing prices outside vs inside the value area to determine acceptance/change | NOT_SEEN (our code uses 6) | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:724` |
| I2-09 Closing price count rule | Tom | the rule is ultimately always a derivation of market profiling combined with the corresponding closing price count | m3IMdc7QwN4 [08:59] | Explicitly pairs market profiling with closing price count as his core rule | NOT_SEEN | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:724` |
| I2-10 TPO removed by Fabio | Fabio | let me remove one second the TPO | Is1HvdfQm5c [16:08] | Fabio removes TPO (Market Profile) from his chart and works off Volume Profile alone | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/signals.py:143` |
| I2-11 Daily loss cut in $, not 3 stops | Fabio | I noticed that the days that start with three or four or five stop-loss end up with a losing of 20,000 15,000. I start to cut them at 8 9,000 | DyS79Eb92Ug [100:51] | Cuts losing days at a dollar/P&L threshold ($8k-$9k) after 3-5 stops, rather than a hard 3-stop count | SOURCED: 3 to 5 stops / $8,000-$9,000 cut | `MyTradingSys/backtest/layers/fabio/v3/day_gates.py:16` |
| I2-13 Crypto order flow scalping | Fabio | And in the weekend when I'm bored on Saturday, I do crypto order flow | DyS79Eb92Ug [130:07] | Actively trades crypto with order flow on weekends, contradicting Is1HvdfQm5c | NOT_SEEN | NONE |
| I2-13 FTX crypto scalper | Fabio | I was ranking in the leaderboard of FTX, I was an extremely active crypto scalper | LQvv5xgy_ik [32:30] | Built track record as an active crypto scalper on FTX | NOT_SEEN | NONE |
| I2-14 Resting limit orders (Tom) | Tom | Both were done with limit orders. So you could have basically ignored the market | yRvMW6lgN1o [13:01] | Places resting limit orders at predefined levels for both entry and exit | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/models.py:62` |
| I2-14 Resting limit orders (Fabio) | Fabio | So, you can already put a limit order here | 06R-ebyOhDI [06:54] | Places resting limit orders at absorption/reversal levels | NOT_SEEN | `MyTradingSys/backtest/layers/fabio/v3/models.py:62` |
| I2-17 Breakout RR 1:1 to 1.5:1 | Tom | This means that with breakout setups, you often have risk reward ratios that are not greater than 1:1 or 1.5:1 | uk4PZV59nYw [10:46] | Breakout setups often have RR <= 1:1 to 1.5:1, so our 1.20 RR floor is within his stated range | SOURCED: 1:1 to 1.5:1 | `MyTradingSys/research/tom_fabio_course_correction_2026-11-07/auction_context.py:49` |
| I2-18 RSI models used in balance | Tom | Consequently, I then turn my corresponding RSI models back on | VOiy8mAALWA [16:11] | Turns RSI models back on in balance phases, contradicting Fabio's D-tier dismissal | NOT_SEEN | `MyTradingSys/tools/live_aid/levelstory.js:45` |
| I2-25 London session traded live | Fabio | he's already traded London Session where he's made over $10,000 just in London session alone | DyS79Eb92Ug [02:42] | Trades London session live for $10k+ profit, contradicting his 0KyIEdvVKMQ claim that London is not worth trading | SOURCED: $10,000 | NONE |

## Verbatim Quote Verification Blocks

> "You buy or sell the breakout of the first 15 minutes of the cash session"
**Source GPS: cUTsoU-15Tc | BEGIN**

> "It is sometimes the case that exactly in these 30 minutes, a lot of liquidity simply enters the market"
**Source GPS: Of_wlv3xaZo | BEGIN**

> "It would be smart to say, for example, if I trade in the morning, I use the 24-hour session just to have some reference points"
**Source GPS: Of_wlv3xaZo | END**

> "This 24-hour model was, of course, aimed at the swing trading approach"
**Source GPS: QClPWDJ-BrU | END**

> "You can pinpoint that by counting closing prices or by all sorts of other means"
**Source GPS: 3o1VVsfBmmU | BEGIN**

> "The second option would be to trail a stop-loss accordingly, especially when you think the market still has a journey ahead of it"
**Source GPS: e83njGZFrPw | END**

> "And then I decided to also trail the stop loss to the high"
**Source GPS: kXhIAug0Gh8 | MIDDLE**

> "Today there is a lot of volume. So I need to bigger filter"
**Source GPS: jasv3L-d8ZE | BEGIN**

> "i can go on 80 range i can go on 40 range i can go on one minute is it visible yes"
**Source GPS: Is1HvdfQm5c | MIDDLE**

> "for you as a short-term 1-minute scalper, is a truly great technical signal"
**Source GPS: zAwEX_tRUfE | END**

> "But you cannot predict when it will go choppy. If I can predict when it will go like this, I will be billionaire"
**Source GPS: jasv3L-d8ZE | MIDDLE**

> "I took the choppy session to make you understand that even in days where you don't have a directional day still giving you an amazing edge when you break out"
**Source GPS: cUTsoU-15Tc | MIDDLE**

> "And for us in trading, that is the absolute best counter indicator"
**Source GPS: sQ_biBKhPVU | MIDDLE**

> "The market tested this top once, then twice, and then a third time, really confirming that level before it finally ran down"
**Source GPS: viT_VzF5Fsw | MIDDLE**

> "we can determine whether the closing prices were within the balance the value area or if the closing price was outside"
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

> "the rule is ultimately always a derivation of market profiling combined with the corresponding closing price count"
**Source GPS: m3IMdc7QwN4 | END**

> "let me remove one second the TPO"
**Source GPS: Is1HvdfQm5c | BEGIN**

> "I noticed that the days that start with three or four or five stop-loss end up with a losing of 20,000 15,000. I start to cut them at 8 9,000"
**Source GPS: DyS79Eb92Ug | MIDDLE**

> "And in the weekend when I'm bored on Saturday, I do crypto order flow"
**Source GPS: DyS79Eb92Ug | END**

> "I was ranking in the leaderboard of FTX, I was an extremely active crypto scalper"
**Source GPS: LQvv5xgy_ik | END**

> "Both were done with limit orders. So you could have basically ignored the market"
**Source GPS: yRvMW6lgN1o | END**

> "So, you can already put a limit order here"
**Source GPS: 06R-ebyOhDI | END**

> "This means that with breakout setups, you often have risk reward ratios that are not greater than 1:1 or 1.5:1"
**Source GPS: uk4PZV59nYw | END**

> "Consequently, I then turn my corresponding RSI models back on"
**Source GPS: VOiy8mAALWA | END**

> "he's already traded London Session where he's made over $10,000 just in London session alone"
**Source GPS: DyS79Eb92Ug | BEGIN**

## TOP 5

1. **I2-06 (Fixed filter 60 & range bars only vs percentile & 1m bars):** Fabio explicitly scales his big-trade filter up on high-volume days (`jasv3L-d8ZE`: *"Today there is a lot of volume. So I need to bigger filter"*), directly supporting a volume-relative/percentile filter rather than a fixed 60. Both Fabio (`Is1HvdfQm5c`: *"i can go on 80 range i can go on 40 range i can go on one minute is it visible yes"*) and Tom (`zAwEX_tRUfE`) use 1-minute bars.
2. **I2-09 & I2-03 (Closing-price count vs profile shape):** `ITERATION_2.md` faults `auction_context.py` for counting closing prices outside the level (`n_acc = 6`). Tom explicitly endorses closing-price counts for both balance/trend classification (`3o1VVsfBmmU`: *"You can pinpoint that by counting closing prices"*) and acceptance (`1utSjHs_Mq8`, `m3IMdc7QwN4`: *"a derivation of market profiling combined with the corresponding closing price count"*).
3. **I2-14 (Resting limit orders vs market/buy-stop):** `ITERATION_2.md` flags `MyTradingSys/backtest/layers/fabio/v3/models.py:62` (`_rest_trade`) for using resting limit entries instead of market/half-candle/buy-stop orders. Both Tom (`yRvMW6lgN1o`: *Both were done with limit orders. So you could have basically ignored the market*) and Fabio (`06R-ebyOhDI`: *So, you can already put a limit order here*) explicitly trade resting limit orders at levels.
4. **I2-17 (1.20 RR floor too low):** `ITERATION_2.md` claims `DEFAULT_MIN_NET_RR = 1.20` sits below his stated 1.5–2.5 floor. Tom explicitly states in `uk4PZV59nYw` that breakout setups often have RR *"not greater than 1:1 or 1.5:1"*, placing 1.20 squarely inside his stated breakout range.
5. **I2-07 & I2-11 (Day filters & 3-stop cap):** Fabio explicitly states you cannot predict a choppy day in advance (`jasv3L-d8ZE`), trades choppy sessions in `cUTsoU-15Tc`, and cuts losing days by dollar P&L (`$8k-$9k` after 3–5 stops in `DyS79Eb92Ug`) rather than a strict 3-stop count. Tom actively trades geopolitical news gaps (`sQ_biBKhPVU`) rather than skipping all news/gap days.

## SINGLE BIGGEST HOLE

`ITERATION_2.md` treats Tom and Fabio as a single unified rulebook and promotes single-video remarks into hard prohibitions—when the transcripts show both traders contradicting each other and themselves across videos on nearly every "gap" (30m open skip vs 15m ORB, 1m bars vs range bars, fixed 60 filter vs volume-scaled filter, trailing vs fixed target, resting limits vs market orders, 1:1–1.5:1 RR vs high RR, RSI off vs RSI on, TPO used vs TPO removed, London skipped vs London traded, choppy skipped vs choppy traded). Treating every difference between our code and a single quote as a coding bug misclassifies valid trader-specific or regime-specific variants as defects.
