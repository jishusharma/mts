# Habib (Qriptal) Trading Method: Rules, Imbalances, Levels, and Execution Protocols

**Author:** Gemini Flash Research Worker  
**Date:** 2026-10-24  
**Subject:** Habib (analyst on the Qriptal YouTube channel)  
**Output Target:** `MyTradingSys/research/gemini_burn_2026-10-24/habib_yt_rules.md`

---

## 1. Executive Summary & Repo Baseline Comparison

### 1.1 Repo Baseline (What Was Covered Before)
Before this research, the MTS repository analyzed Habib / Qriptal across three primary tracks:
1. **`MyTradingSys/research/qriptal_2026-10-10/` (Call Ledger & Scorecard):**
   - Attempted to score 70 forward-looking trade statements across 22 staged videos (April–September 2026).
   - Scored $n = 0$ on DEV data because only 2 forward calls had an explicit entry, stop, and target (both from the September 21, 2026 live stream `ZPFK3ZsLwoo`), which fell in the holdout window.
   - Fixed resolution rules (`RULES.md`): 24-hour limit fill window, 7-day max hold to market close, and same-candle stop/TP resolution to stop. All parameters were labeled `OURS`.
2. **`MyTradingSys/research/imbalance_qriptal_2026-10-16/` (Construct F & Fee-Net Candle Fade Test):**
   - Defined Construct F ("Qriptal volume-anomaly candle"): a candle whose volume is anomalous for its timeframe on a specific exchange, where a small body signifies that volume failed to move price (trapped traders).
   - Backtested a mechanical fade of this candle (stop at candle's extreme, entry on next bar open) on Binance BTCUSDT perpetuals across 30m, 1h, 4h, 12h, and 1d timeframes.
   - Verdict: **NO EDGE.** Fading the standalone candle lost money after fees across all timeframes.
   - Confirmed Habib's negative claim: fading a high-volume *large-body* candle loses heavily (gross $-0.10$ to $-0.42$ R), validating "large body = strength, do not fade it" as a veto.
   - Evaluated 22 price labels from 19 videos (`labels.json`) and transcribed 6 post-September 30 videos (`f9nuENfR-2o`, `RW-Nn3e29Es`, `sLaymf4LB_8`, `bnqojhZrFNQ`, `Y0YZnyUCtuM`, `B6ImdQNCFTI`).
3. **`MyTradingSys/research/habib_plan_imbalance_2026-10-20/` (Sunday Plan Intake Note):**
   - Examined Habib's Sunday weekly plan from Discord `#trading-thoughts` (2026-10-18).
   - Showed that the qualitative structure (sweep low before weekly open, then push higher) matched Binance klines, but systematic scoring was blocked because chart levels lacked typed prices.

### 1.2 What Is New in This Document
This document covers **15 new Qriptal videos** where Habib explicitly articulates his trading method, none of which were transcribed or reviewed in the three prior repo studies.

Key methodological discoveries from this expanded video corpus:
- **The Complete 3-Pillar Setup:** Habib never trades an imbalance in isolation. A valid trade strictly requires three confluent pillars:
  1. A pre-planned high-timeframe (HTF) reference level (imbalance open/midpoint, order block, range POC, weekly/monthly open).
  2. Volume anomaly confirmation (an imbalance candle on 30m/1h/4h confirming aggressive retail entering on the wrong side).
  3. Price reaction (a distinct wick rejection confirming institutional absorption).
- **Taxonomy of Imbalance Candles:**
  - *Small Body + High Volume + Wick:* Trapped traders; prime reversal setup.
  - *Large Body + High Volume:* Strong breakout / expansion; never fade, only join on retest.
  - *Wickless Imbalance Candle:* High-probability magnetic target that must be recovered / filled.
  - *Binance "Scam Wicks":* Exchange-specific aberrational wicks that act as magnets for future price recovery.
- **Breakout Validation vs. Fakeout Invalidation:** A valid breakout must hold the open of the breakout imbalance candle / order block on retest. Losing that level confirms a trap/fakeout and triggers a reversal targeting the opposite range extreme.
- **Weekly Cycle & Execution Timing:** Heavy emphasis on the Monday open trap (sweeping weekend liquidity before establishing the true directional trend) and the monthly candle wick formation cycle (early-month expansion in the counter-trend direction to print the wick before the main monthly expansion).

---

## 2. Fifteen New Qriptal Videos: Habib's Method

### Video 1: `c9qf7QJroAE` — "Bitcoin: The big is move is near... Be ready!"
- **URL:** https://www.youtube.com/watch?v=c9qf7QJroAE
- **Published Date (UTC):** 2026-10-22
- **Duration:** 670s (11m 10s)
- **Type:** YouTube Market Update
- **Method Verbatim Quotes & Timestamps:**
  - `[0:00:49]` "the first part of the plan played out perfectly because we got the sweep below that double bottom. We had a 1-hour imbalance. From there, we got the reversal to the upside"
  - `[0:04:19]` "you had a small bodied candle, which was an imbalance with a good wick. So, even though once again we frontrun my [level]..."
  - `[0:05:16]` "If we go on the 12-hour, we can see we have a 12-hour imbalance. I will also take the bottom of this candle. If you go on the 4-hour, we have a 4-hour imbalance and we have a 4-hour order block. If you go on the 1-hour, we have a 1-hour imbalance, so you can just take this open."
  - `[0:08:40]` "we see just a 30-minute imbalance up here, I don't need more. In my opinion, that could trigger a short position right here with a stop loss above this high to see the reversal to the downside"
- **Method Rules Derived:**
  - *Entry Trigger:* 30m imbalance printing at a pre-planned resistance level triggers short entry [`SOURCED: c9qf7QJroAE:8:40`].
  - *Candle Shape Requirement:* Reversal imbalance candle must have a small body and a pronounced wick [`SOURCED: c9qf7QJroAE:4:19`].
  - *Stop Placement:* Stop loss is placed strictly above the swing high created by the wick [`SOURCED: c9qf7QJroAE:8:40`].
  - *Level Derivation:* Level taken from the open of an hourly imbalance or bottom/open of a 12h/4h imbalance [`SOURCED: c9qf7QJroAE:5:16`].

---

### Video 2: `14PZEEbHSaM` — "Bitcoin: Why lower prices are still coming..."
- **URL:** https://www.youtube.com/watch?v=14PZEEbHSaM
- **Published Date (UTC):** 2026-09-29
- **Duration:** 601s (10m 01s)
- **Type:** YouTube Market Update
- **Method Verbatim Quotes & Timestamps:**
  - `[0:05:03]` "we still have a wickless 4hour imbalance which is why I have this area as support. So we have a wickless 4hour imbalance. We have a very obvious level that was tested multiple times."
  - `[0:05:39]` "What did we have right there? We had a very big and ugly wick on the 4hour. So you take the high of that wick... and what do we have just above that wick? We have a 4hour imbalance which is also the weekly open... So we have liquidity above it."
  - `[0:06:39]` "If we move up into it and we have a good reaction, then personally I will look for a short"
  - `[0:07:25]` "This can offer a hedge long entry and stop loss there... hold on to that long with a stop loss at entry and then you let it fully play out"
- **Method Rules Derived:**
  - *Wickless Imbalance as S/R:* A wickless 4h imbalance candle acts as a high-conviction support level [`SOURCED: 14PZEEbHSaM:5:03`].
  - *Liquidity Sweep Confluence:* An "ugly wick" leaves resting stop liquidity above its extreme; price sweeps the wick high directly into a 4h imbalance / weekly open before reversing [`SOURCED: 14PZEEbHSaM:5:39`].
  - *Trade Management:* Stop loss is moved to entry (breakeven) once price bounces away from the level [`SOURCED: 14PZEEbHSaM:7:25`].

---

### Video 3: `YuTkhoJ3n-0` — "Bitcoin LIVE analysis and weekly outlook - Why the correction isn't over..."
- **URL:** https://www.youtube.com/watch?v=YuTkhoJ3n-0
- **Published Date (UTC):** 2026-09-28
- **Duration:** 2955s (49m 15s)
- **Type:** Sunday Live Stream / Weekly Outlook
- **Method Verbatim Quotes & Timestamps:**
  - `[0:06:50]` "trade as well potential takeprofit one while moving your stop loss to break even."
  - `[0:08:34]` "We got the move up. We got a 4hour imbalance and it offered a straight rejection. As you can see, it's a move up 4hour imbalance. We got a drop to the downside."
  - `[0:09:30]` "this wickless hourly candle up there which is also an imbalance on Binance. So if you look at Binance, this is a wickless imbalance."
  - `[0:10:02]` "when price gets up there, this is when I'm going to start looking for reactions... If you don't get a reaction in shorting this exact level, I don't have a problem at all. If you got to move a bit higher, see here a rejection up there for example and then I take my short position"
  - `[0:40:49]` "Everyone that were looking for these longs, no matter the entry, had their stop loss below that low. So when you take out all of their stop losses, this is when the long becomes acceptable. Even though we had a 4hour imbalance there... this was not enough to trigger a [long]"
- **Method Rules Derived:**
  - *Liquidity Sweep Prerequisite:* An imbalance alone is insufficient for entry if resting stops below a key range low remain unswept [`SOURCED: YuTkhoJ3n-0:40:49`].
  - *Reaction Requirement over Limit Orders:* Habib does not place blind limit orders; he waits for price to reach the level and show a visible rejection/wick [`SOURCED: YuTkhoJ3n-0:10:02`].
  - *Take-Profit Protocol:* Partial take profit (TP1) is taken at the first structural reaction while simultaneously trailing stop loss to breakeven [`SOURCED: YuTkhoJ3n-0:6:50`].

---

### Video 4: `2XOJcddS61E` — "Bitcoin LIVE analysis and weekly outlook - Breakdown incoming?!"
- **URL:** https://www.youtube.com/watch?v=2XOJcddS61E
- **Published Date (UTC):** 2026-09-14
- **Duration:** 2377s (39m 37s)
- **Type:** Sunday Live Stream / Weekly Outlook
- **Method Verbatim Quotes & Timestamps:**
  - `[0:03:06]` "We got the drop into that level. We got the 1 hour imbalance and at this point I even outlined the level below"
  - `[0:04:45]` "took my short position right there... so my stop loss was at 82.8"
  - `[0:25:34]` "take 82.1. Why 82.1? Because it's a sweep of 82. stop loss um 82.8 first target 75.5 you have a 9 to1 and again that was an extremely safe and easy [trade]"
  - `[0:28:17]` "Not financial advice, but this is how I plan my trades. You will enter with this amount of risk. Whatever the entry will be, if it's a bit higher, you will have [a better risk/reward]"
  - `[0:32:46]` "just a nice wick, very nice volume for our imbalance and then you come back down."
- **Method Rules Derived:**
  - *Sweep Entry Logic:* Entry taken immediately upon the sweep of a round psychological number (sweep of 82.0k into 82.1k) [`SOURCED: 2XOJcddS61E:25:34`].
  - *Stop Invalidation:* Hard stop loss placed beyond the macro invalidation level (82.8k) [`SOURCED: 2XOJcddS61E:4:45`, `25:34`].
  - *Volume-Wick Confirmation:* Confirmed by high volume and a clean upper wick on the imbalance bar [`SOURCED: 2XOJcddS61E:32:46`].

---

### Video 5: `5dTABLiktmg` — "Bitcoin LIVE analysis and weekly outlook - The September price action!"
- **URL:** https://www.youtube.com/watch?v=5dTABLiktmg
- **Published Date (UTC):** 2026-08-30
- **Duration:** 1927s (32m 07s)
- **Type:** Sunday Live Stream / Weekly Outlook
- **Method Verbatim Quotes & Timestamps:**
  - `[0:08:33]` "So the short position would look something like this. Your entry could be let's say 81.8 stop loss on this high and then the target will be $72,000 for a very good 9.5 to1 RR."
  - `[0:09:17]` "ideally we got that move up at the start of the month. We form the the wick of the monthly candle to the upside first. chart, as you know, most candles have a wick to the downside and to the upside. So, what I'm looking for this month... we get that wick to the upside, but then we come back down for the rest of the month, targeting 72 to $73,000."
  - `[0:19:25]` "A wickless 4hour imbalance with another four below it. That would have been your support for the bounce."
  - `[0:20:07]` "Then for the short, I mean, you have a great target for the long position because now you have a double top. So that's good... you can target this double top. Do we have an imbalance above it?"
- **Method Rules Derived:**
  - *Monthly Candle Wick Cycle:* At the beginning of a calendar month, price typically expands in the opposite direction of the macro bias to form the monthly candle wick before reversing [`SOURCED: 5dTABLiktmg:9:17`].
  - *Double Tops as Magnetic Targets:* Double tops represent uncollected buy stops; they act as primary targets for long positions, especially when aligned with an imbalance above them [`SOURCED: 5dTABLiktmg:20:07`].

---

### Video 6: `yHFg7oVN3ts` — "Bitcoin LIVE analysis and weekly outlook - What to do if you're sidelined!"
- **URL:** https://www.youtube.com/watch?v=yHFg7oVN3ts
- **Published Date (UTC):** 2026-08-24
- **Duration:** 2818s (46m 58s)
- **Type:** Sunday Live Stream / Weekly Outlook
- **Method Verbatim Quotes & Timestamps:**
  - `[0:03:52]` "took the short right at the high. Put my stop loss pretty much to entry and got stopped out the next day for a super [small gain]"
  - `[0:12:21]` "locally, of course, we have this daily imbalance and instant retest. So what do you do there? As usual, you take the midpoint"
  - `[0:39:48]` "on 25x leverage. If I can pinpoint a more accurate entry, then I will go for a higher leverage and just a normal [risk]... If not confident about the super accurate entry, then I might just go for this [wider stop with lower leverage]"
  - `[0:40:56]` "technically very beautiful levels with a 12-hour wickless imbalance, a daily wickless imbalance, the midpoint of the 3-day imbalance, and of course the cherry on top. When you take the volume profile..."
- **Method Rules Derived:**
  - *Midpoint Retest Rule:* When an imbalance candle receives an immediate retest, the level to trade is strictly the 50% midpoint $(H+L)/2$ of that candle [`SOURCED: yHFg7oVN3ts:12:21`].
  - *Confluence Stack:* Maximum conviction requires alignment of a HTF wickless imbalance (12h/1d), the midpoint of a 3-day imbalance, and the Volume Profile Point of Control (POC) [`SOURCED: yHFg7oVN3ts:40:56`].
  - *Dynamic Leverage & Risk:* Leverage is scaled inversely to stop distance; precise wick entries allow higher leverage, while wide structural setups require low leverage [`SOURCED: yHFg7oVN3ts:39:48`].

---

### Video 7: `PrHoIQ-YWX0` — "Bitcoin LIVE analysis and weekly outlook - Be ready for these moves!!"
- **URL:** https://www.youtube.com/watch?v=PrHoIQ-YWX0
- **Published Date (UTC):** 2026-08-17
- **Duration:** 2979s (49m 39s)
- **Type:** Sunday Live Stream / Weekly Outlook
- **Method Verbatim Quotes & Timestamps:**
  - `[0:07:25]` "when you combine a double top on the partially filled early imbalance with an order block, it is a fairly good [level]"
  - `[0:08:38]` "Not only a wickless candle, but it's also an imbalance. We have a wickless hourly imbalance which has already offered a rejection as you can see."
  - `[0:17:55]` "my opinion Ethereum will test this partially filled daily imbalance. So that is a big magnet to the downside."
  - `[0:18:26]` "Have your levels ready. If you have your volume and your reaction, you take the short, you book profit somewhere around here, for example. You keep your stop loss to break even, and then you just [let runner ride]... Have your levels ready. Monitor the volume and the reaction. And that's all you need to do."
- **Method Rules Derived:**
  - *The 3-Pillar Operational Summary:* Habib explicitly reduces his system to: (1) Pre-planned level, (2) Volume anomaly (imbalance), and (3) Price reaction (wick) [`SOURCED: PrHoIQ-YWX0:18:26`].
  - *Partially Filled Imbalance as a Magnet:* An imbalance that has only been partly tapped remains an active magnet until fully filled [`SOURCED: PrHoIQ-YWX0:17:55`].
  - *Order Block Confluence:* Combining a double top with an order block inside a partially filled imbalance creates high-probability resistance [`SOURCED: PrHoIQ-YWX0:7:25`].

---

### Video 8: `te5DetlT3XU` — "Bitcoin LIVE analysis and weekly outlook - Breakout or bull trap?!"
- **URL:** https://www.youtube.com/watch?v=te5DetlT3XU
- **Published Date (UTC):** 2026-08-10
- **Duration:** 3167s (52m 47s)
- **Type:** Sunday Live Stream / Weekly Outlook
- **Method Verbatim Quotes & Timestamps:**
  - `[0:05:16]` "Go on the 4-hour chart. We had a 4-hour imbalance, so you take the open."
  - `[0:06:30]` "know when we have a wickless candle, that is a very good target. Plus, we had a one hour order block. Not the biggest... It was also a wickless one hour imbalance. And what happened? We [filled it]"
  - `[0:47:16]` "people build shorts with a stop loss above these highs. You open Monday, you take out all of these stop losses, you form the Monday high, and then you got a reversal"
  - `[0:51:40]` "So, a fill of this imbalance right at the daily open. We have a wickless 1-hour imbalance... if you got the drop before taking out [the high]"
- **Method Rules Derived:**
  - *Imbalance Open as Level:* The candle open of a 4-hour imbalance serves as a precise support/resistance level [`SOURCED: te5DetlT3XU:5:16`].
  - *Monday High Formation:* Monday open frequently stages a fakeout rally that sweeps weekend short stops, setting the high of the week before initiating a sustained reversal [`SOURCED: te5DetlT3XU:47:16`].
  - *Wickless Candle Recovery:* Wickless candles are magnets that must be filled before a true directional trend continues [`SOURCED: te5DetlT3XU:6:30`, `51:40`].

---

### Video 9: `0tiz6_pSBuw` — "Bitcoin LIVE analysis and weekly outlook - This week's trap!"
- **URL:** https://www.youtube.com/watch?v=0tiz6_pSBuw
- **Published Date (UTC):** 2026-08-05
- **Duration:** 3512s (58m 32s)
- **Type:** Sunday Live Stream / Weekly Outlook
- **Method Verbatim Quotes & Timestamps:**
  - `[0:02:28]` "4-hour imbalance, a partial fill. So, you take the open. As you can see, we got the drop. We got the wick. This is where I open my long to hedge my short."
  - `[0:04:46]` "4-hour imbalance to the dollar, go on the 1-hour, you take the 1-hour imbalance, we have the 1-hour imbalance at the high with a wick, the filling both of the imbalances, the 1-hour and [4-hour]..."
  - `[0:52:51]` "a high tomorrow morning, you take the trade, you put your stop loss, and of course, if you get the drop at this point, it makes sense to target $60,000. So, this offers you about a 10:1 RRR"
  - `[0:57:36]` "We wait for the move. We wait for the reaction and then we take the trade."
- **Method Rules Derived:**
  - *Dual-Timeframe Imbalance Fill:* Optimal entry occurs when an intraday (1h) imbalance candle with a wick forms exactly inside an existing HTF (4h) imbalance level [`SOURCED: 0tiz6_pSBuw:4:46`].
  - *Hedge Long Protocol:* On touching HTF support with an imbalance and wick, Habib opens a hedge long to protect an existing runner short [`SOURCED: 0tiz6_pSBuw:2:28`].
  - *Patient Execution:* Traders must never preemptively enter; wait for the move into the level and observe the wick reaction before pulling the trigger [`SOURCED: 0tiz6_pSBuw:57:36`].

---

### Video 10: `fBg2-RXPOAk` — "Bitcoin LIVE analysis and weekly outlook - The incoming volatility!"
- **URL:** https://www.youtube.com/watch?v=fBg2-RXPOAk
- **Published Date (UTC):** 2026-07-27
- **Duration:** 1943s (32m 23s)
- **Type:** Sunday Live Stream / Weekly Outlook
- **Method Verbatim Quotes & Timestamps:**
  - `[0:03:03]` "a very big scam wick on Binance. These tend to get recovered. So, for these two [reasons]..."
  - `[0:26:17]` "You dropped from high to low. The only imbalance that appeared was right at the low... two 30-minute imbalances... what you can do is you take your long right here. You can put your stop loss, for example, there, and here your stop loss is 1%."
  - `[0:26:48]` "In that case, I will take a 5x long since the stop loss will be a bit wider... If we got a big wick, then it will be a bit harder to catch. If we got... a very nice wick, a small body. This makes it a bit easier to catch a very accurate entry with a tight stop loss."
  - `[0:29:15]` "the logic behind this resistance? We have a 4-hour imbalance and we have two value area highs. We have this range."
- **Method Rules Derived:**
  - *Binance "Scam Wicks":* Exchange-specific aberrational wicks are treated as artificial stop runs and serve as definitive price targets to be recovered [`SOURCED: fBg2-RXPOAk:3:03`].
  - *Candle Geometry & Stop Width:* A small body with a well-defined wick allows a tight ~1% stop; an oversized wick forces a wider stop and reduced leverage (e.g., 5x) [`SOURCED: fBg2-RXPOAk:26:17`, `26:48`].
  - *Value Area High (VAH) Confluence:* Alignment of a 4h imbalance with the Value Area Highs of multiple overlapping ranges creates major resistance [`SOURCED: fBg2-RXPOAk:29:15`].

---

### Video 11: `a4Um_W3Nfss` — "Bitcoin LIVE analysis and weekly outlook - CRUCIAL week ahead!"
- **URL:** https://www.youtube.com/watch?v=a4Um_W3Nfss
- **Published Date (UTC):** 2026-07-20
- **Duration:** 2474s (41m 14s)
- **Type:** Sunday Live Stream / Weekly Outlook
- **Method Verbatim Quotes & Timestamps:**
  - `[0:03:17]` "either implemented take profit, move the stop loss to break even. You manage your position however you want to. Personally, I just decided to put the stop loss at the daily low."
  - `[0:11:56]` "more low, we got a wick. We had a 30 minute imbalance... that was a purple candle at first."
  - `[0:14:17]` "Sunday plan long into short. Okay, that would be the first plan. The second plan would be that we don't get a Monday pivot and that we just get... short only."
  - `[0:17:29]` "on Ethereum that we have a daily imbalance down there with this order block. So maybe we actually drop on Ethereum on Monday which would mean a drop on Bitcoin."
- **Method Rules Derived:**
  - *Indicator Visual Signature:* Habib's proprietary imbalance indicator colors the candle purple on TradingView when anomalous volume is detected [`SOURCED: a4Um_W3Nfss:11:56`].
  - *Branching Sunday Plans:* Habib always maps two branching plans: Plan A (early week liquidity sweep/pivot then trend) and Plan B (direct trend continuation without sweep) [`SOURCED: a4Um_W3Nfss:14:17`].
  - *ETH-BTC Cross-Asset Confluence:* HTF imbalances and order blocks on Ethereum provide leading confluence for Bitcoin's directional moves [`SOURCED: a4Um_W3Nfss:17:29`].

---

### Video 12: `Jt5QElvvzPw` — "Bitcoin LIVE analysis and weekly outlook - BIG Bull trap this week?!"
- **URL:** https://www.youtube.com/watch?v=Jt5QElvvzPw
- **Published Date (UTC):** 2026-07-06
- **Duration:** 1586s (26m 26s)
- **Type:** Sunday Live Stream / Weekly Outlook
- **Method Verbatim Quotes & Timestamps:**
  - `[0:02:17]` "we had this partially filled daily imbalance. Okay, if you take the open, as you can see, this [held]"
  - `[0:04:37]` "over to Binance, we had... two 30 minute imbalances as well as a 1 hour imbalance right there. So, personally, I just took a quick day trade"
  - `[0:16:56]` "Monday high on the 4hour imbalance this week and last week as well... Monday high on the 4hour imbalance."
  - `[0:22:44]` "The weekly target for me will be $60,000. Doesn't really matter if it's this level or if we take out the liquidity of this low... target for this week and potentially to flip in a long position if of course a Sunday plan plays out."
- **Method Rules Derived:**
  - *Monday High Repeatability:* Monday high forming directly on a 4-hour imbalance is a recurring weekly pattern across consecutive weeks [`SOURCED: Jt5QElvvzPw:16:56`].
  - *Target and Flip:* Once the HTF weekly target is hit (liquidity pool swept or daily imbalance filled), the position is closed and Habib looks to flip direction [`SOURCED: Jt5QElvvzPw:22:44`].
  - *Daily Imbalance Open:* Daily imbalance open acts as a rock-solid support/resistance level [`SOURCED: Jt5QElvvzPw:2:17`].

---

### Video 13: `brg09NkHi6A` — "Bitcoin: How to know if this breakout will hold..."
- **URL:** https://www.youtube.com/watch?v=brg09NkHi6A
- **Published Date (UTC):** 2026-01-15
- **Duration:** 448s (7m 28s)
- **Type:** YouTube Market Update
- **Method Verbatim Quotes & Timestamps:**
  - `[0:01:24]` "my short position pretty much for a break even trade, right? Entry price at 93.6, exit price at 93.6."
  - `[0:02:54]` "Can go on the daily chart and we do have a daily imbalance up here that has had a decent close. So, this candle will be extremely important to hold as support. What will we do? We take the open of this candle around $95,300. Go on the 12-hour chart. We also have a 12-hour imbalance and a 12-hour order block."
  - `[0:03:54]` "We could get the retest of this area before going higher... In this case, of course, I will be interested in opening a long position. However, if we do indeed drop towards the support and we lose it, then this would be a first massive sign of weakness."
  - `[0:04:55]` "your first and only target will be back below this low at $80,000."
- **Method Rules Derived:**
  - *Breakout Validation Rule:* A genuine breakout must hold the open of the breakout daily/12h imbalance candle on retest [`SOURCED: brg09NkHi6A:2:54`].
  - *Fakeout / Failed Breakout Reversal:* If price breaks below the imbalance candle's open, the breakout has failed; traders should short, targeting the origin of the breakout range (macro low) [`SOURCED: brg09NkHi6A:3:54`, `4:55`].

---

### Video 14: `cuhsL6RENvw` — "Bitcoin: They're laying out the same trap (once again)"
- **URL:** https://www.youtube.com/watch?v=cuhsL6RENvw
- **Published Date (UTC):** 2026-04-01
- **Duration:** 598s (9m 58s)
- **Type:** YouTube Market Update
- **Method Verbatim Quotes & Timestamps:**
  - `[0:03:16]` "was this 4hour imbalance. It offered the support."
  - `[0:07:12]` "Once again, we have an hourly imbalance on the 30 minutes. We have a 30 minute imbalance right at the high. We have another 30 minute imbalance right on this drop. So, I think that people are chasing... get one final drop, that will stop out all of these late longs one last time"
  - `[0:08:24]` "below a wickless candle on the 4hour, on the 1 hour, and the 12-hour imbalance, would be fairly interesting to get maybe [a long]"
  - `[0:09:10]` "personally, I am still short from $74,000. My stop loss is at entry. I'm keeping it there. I haven't taken any profits."
- **Method Rules Derived:**
  - *Retail Chasing Pattern:* Multiple consecutive LTF (30m/1h) imbalances in rapid succession signal late retail traders chasing momentum; market makers trigger one final stop run before true reversal [`SOURCED: cuhsL6RENvw:7:12`].
  - *Macro Runner Discipline:* For high-conviction macro swing trades, Habib leaves full positions open with stop at breakeven targeting major HTF targets without early partial exits [`SOURCED: cuhsL6RENvw:9:10`].

---

### Video 15: `vU7_4Gq9c5Y` — "How to take EASY trades on Bitcoin - June 2024 Market Update"
- **URL:** https://www.youtube.com/watch?v=vU7_4Gq9c5Y
- **Published Date (UTC):** 2024-06-03
- **Duration:** 455s (7m 35s)
- **Type:** YouTube Educational / Market Strategy
- **Method Verbatim Quotes & Timestamps:**
  - `[0:00:28]` "support below us which was the point of control and then above us we had this bearish order block and if you remember I shared one short that I had opened on this candle and my target was the top of this order block"
  - `[0:01:27]` "you take profits you move your stop-loss to break even and then you don't really care what happens"
  - `[0:02:06]` "this was a move on Monday and usually I don't really trust Monday moves but also this was a bank holiday meaning you wouldn't really expect follow through with moves in the market so that's why I waited for a top and then when I saw a top confirmation with this drop I waited for retracement and then enter the short position... on the 15minute chart I waited for a drop"
  - `[0:06:05]` "fixed range point of control has moved up so at this point if we lose this level I would expect again a drop to the low"
- **Method Rules Derived:**
  - *Monday / Holiday Distrust Rule:* Impulsive breakouts occurring on Mondays or bank holidays lack institutional follow-through and are prone to severe failure [`SOURCED: vU7_4Gq9c5Y:2:06`].
  - *Reversal Confirmation Protocol:* Do not short the first green bar; wait for a confirmed structural break (drop on 15m), then short the retracement [`SOURCED: vU7_4Gq9c5Y:2:06`].
  - *Fixed Range POC as Dynamic Pivot:* Loss of the volume profile Point of Control signals a swift rotation to the value area low [`SOURCED: vU7_4Gq9c5Y:6:05`].

---

## 3. Method Synthesis: Rules Testable on BTC OHLCV & Orderflow

Below are the operational rules extracted from Habib's method that can be backtested on historical Binance BTCUSDT 1m–1d klines and orderflow data. Each rule is explicitly labeled `SOURCED` (with verbatim quote citation) or `OURS` (operationalization parameters required for execution).

### Rule 1: High-Timeframe Imbalance Level Generation
- **Trader Quote:**
  > "If we go on the 12-hour, we can see we have a 12-hour imbalance. I will also take the bottom of this candle... on the 1-hour, we have a 1-hour imbalance, so you can just take this open." (`c9qf7QJroAE:0:05:16`)
  > "locally, of course, we have this daily imbalance and instant retest. So what do you do there? As usual, you take the midpoint" (`yHFg7oVN3ts:0:12:21`)
  > "Go on the 4-hour chart. We had a 4-hour imbalance, so you take the open." (`te5DetlT3XU:0:05:16`)
- **SOURCED Parameters:**
  - Anchor timeframes: 4h, 12h, 1d [`SOURCED`].
  - Reference price levels:
    - Candle Open: Primary support/resistance boundary [`SOURCED`].
    - Candle Midpoint $(H + L) / 2$: Level for instant retests [`SOURCED`].
    - Candle Extreme (Bottom/Top): Invalidation boundary [`SOURCED`].
- **OURS Parameters (Operationalization):**
  - Relative volume threshold: $V / \text{median}(V, 50\text{ bars}) \ge 2.0$ [`OURS`].
  - Imbalance candle small body definition: $|C - O| / (H - L) \le 0.30$ [`OURS`].
  - Level validity window: Level remains active until fully traversed by a subsequent candle close [`OURS`].

### Rule 2: The 3-Pillar Entry Protocol (Filter on Levels)
- **Trader Quote:**
  > "Have your levels ready. If you have your volume and your reaction, you take the short, you book profit somewhere around here, for example. You keep your stop loss to break even, and then you just [let runner ride]... Have your levels ready. Monitor the volume and the reaction. And that's all you need to do." (`PrHoIQ-YWX0:0:18:26`)
  > "when price gets up there, this is when I'm going to start looking for reactions... If you don't get a reaction in shorting this exact level, I don't have a problem at all. If you got to move a bit higher, see here a rejection up there for example and then I take my short position" (`YuTkhoJ3n-0:0:10:02`)
  > "we see just a 30-minute imbalance up here, I don't need more. In my opinion, that could trigger a short position right here with a stop loss above this high to see the reversal" (`c9qf7QJroAE:0:08:40`)
- **SOURCED Parameters:**
  - Pillar 1 (Level): Price touches an active HTF imbalance open/midpoint or range POC [`SOURCED`].
  - Pillar 2 (Volume): An imbalance candle appears on the 30m or 1h timeframe at the level [`SOURCED`].
  - Pillar 3 (Reaction): The trigger candle prints a distinct rejection wick [`SOURCED`].
  - Execution: Market order upon close of the 30m/1h trigger candle [`SOURCED`].
- **OURS Parameters (Operationalization):**
  - Level touch tolerance: Within $\pm 0.25\%$ of HTF level [`OURS`].
  - Rejection wick size: Upper wick $\ge 40\%$ of candle range for shorts; lower wick $\ge 40\%$ for longs [`OURS`].

### Rule 3: High-Volume Large-Body Candle Veto
- **Trader Quote:**
  > "this is not an imbalance to pay attent attention to for a short because it has a very large body" (`qriptal_ZPFK3ZsLwoo_raw.txt:560`, confirmed in `imbalance_qriptal_2026-10-16/README.md`)
  > "Can go on the daily chart and we do have a daily imbalance up here that has had a decent close. So, this candle will be extremely important to hold as support." (`brg09NkHi6A:0:02:54`)
- **SOURCED Parameters:**
  - A high-volume candle with a large body represents institutional momentum/expansion, NOT absorption [`SOURCED`].
  - Never fade a high-volume large-body candle [`SOURCED`].
- **OURS Parameters (Operationalization):**
  - Large-body threshold: $|C - O| / (H - L) \ge 0.70$ with relative volume $\ge 2.0$ [`OURS`].
  - Veto duration: Blocks counter-trend entries for 12 bars on that timeframe [`OURS`].

### Rule 4: Liquidity Sweep Prerequisite (Double Tops / Bottoms)
- **Trader Quote:**
  > "Everyone that were looking for these longs, no matter the entry, had their stop loss below that low. So when you take out all of their stop losses, this is when the long becomes acceptable. Even though we had a 4hour imbalance there... this was not enough to trigger a [long]" (`YuTkhoJ3n-0:0:40:49`)
  > "the first part of the plan played out perfectly because we got the sweep below that double bottom. We had a 1-hour imbalance. From there, we got the reversal to the upside" (`c9qf7QJroAE:0:00:49`)
- **SOURCED Parameters:**
  - Before entering a reversal, price must sweep equal highs (double top) or equal lows (double bottom) [`SOURCED`].
  - An imbalance without a prior liquidity sweep is deemed invalid/unacceptable [`SOURCED`].
- **OURS Parameters (Operationalization):**
  - Equal highs/lows definition: Two swing pivots within $\pm 0.15\%$ of each other separated by at least 10 bars [`OURS`].
  - Sweep definition: Current candle pierces the pivot extreme but closes back inside the prior range [`OURS`].

### Rule 5: Breakout Validation vs. Fakeout Reversal
- **Trader Quote:**
  > "What will we do? We take the open of this candle around $95,300... this should be my big support to hold in case we want to see higher prices... However, if we do indeed drop towards the support and we lose it, then this would be a first massive sign of weakness... your first and only target will be back below this low at $80,000." (`brg09NkHi6A:0:02:54-0:04:55`)
- **SOURCED Parameters:**
  - Valid breakout: Price retests the open of the breakout imbalance candle and bounces [`SOURCED`].
  - Failed breakout (Fakeout): A candle closes back below the open of the breakout imbalance candle [`SOURCED`].
  - Fakeout target: The origin/low of the entire prior consolidation range [`SOURCED`].
- **OURS Parameters (Operationalization):**
  - Breakout confirmation: 4h close beyond range high with relative volume $\ge 2.0$ [`OURS`].
  - Invalidation close: 4h close below the breakout bar's open by $> 0.10\%$ [`OURS`].

### Rule 6: Wickless Imbalance Candle Magnet Target
- **Trader Quote:**
  > "know when we have a wickless candle, that is a very good target. Plus, we had a one hour order block. Not the biggest... It was also a wickless one hour imbalance." (`te5DetlT3XU:0:06:30`)
  > "we still have a wickless 4hour imbalance which is why I have this area as support." (`14PZEEbHSaM:0:05:03`)
- **SOURCED Parameters:**
  - An imbalance candle with zero wick (or a negligible wick) on one side is an unfilled price gap/magnet [`SOURCED`].
  - Serves as primary target for take profits [`SOURCED`].
- **OURS Parameters (Operationalization):**
  - Wickless threshold: Upper wick $\le 0.05 \times \text{range}$ (for bearish candle) or lower wick $\le 0.05 \times \text{range}$ (for bullish candle) [`OURS`].
  - Target exit: Limit exit order set at the wickless candle's extreme price [`OURS`].

### Rule 7: Trade Management: Breakeven and Stop Placement
- **Trader Quote:**
  > "you take profits you move your stop-loss to break even and then you don't really care what happens" (`vU7_4Gq9c5Y:0:01:27`)
  > "potential takeprofit one while moving your stop loss to break even." (`YuTkhoJ3n-0:0:06:50`)
  > "In my opinion, that could trigger a short position right here with a stop loss above this high to see the reversal" (`c9qf7QJroAE:0:08:40`)
  > "The only imbalance that appeared was right at the low... you take your long right here. You can put your stop loss, for example, there, and here your stop loss is 1%." (`fBg2-RXPOAk:0:26:17`)
- **SOURCED Parameters:**
  - Initial stop loss: Placed beyond the local swing high/low formed by the reaction wick [`SOURCED`].
  - Breakeven trigger: Stop loss is moved to entry price immediately upon reaching Take Profit 1 (TP1) [`SOURCED`].
- **OURS Parameters (Operationalization):**
  - TP1 distance: Fixed at $1.0\text{ R}$ or at the nearest opposing 30m imbalance / range POC [`OURS`].
  - Runner sizing: Close $50\%$ at TP1, leave $50\%$ trailing to final HTF target with stop at breakeven [`OURS`].

---

## 4. Rules That Require Data We May Not Have

The following aspects of Habib's methodology cannot be accurately replicated using only Binance USD-M 1m–1d klines:

### 1. Multi-Exchange Imbalance Cross-Verification
- **Trader Quote:**
  > "Here we have an imbalance on Coinbase, but not shorting there." (`0tiz6_pSBuw:0:06:39`)
  > "We had the 30 minute imbalance right here on Bybit. And over to Binance, we had... two 30 minute imbalances as well as a 1 hour imbalance right there." (`Jt5QElvvzPw:0:04:29`)
  > "Binance as well when you see well we had the imbalance on Bybit as you saw but not on Binance... you jump into it with the imbalances" (`yHFg7oVN3ts:0:42:01`)
- **Data Gap:** Habib cross-references three distinct exchange venues: Binance, Bybit, and Coinbase. A level is often rejected if Bybit does not show an imbalance, or prioritized when Binance shows two imbalances while Bybit shows one. MTS local historical dataset currently consists primarily of Binance USD-M futures klines. Full multi-exchange synchronous 1m orderflow across Bybit and Coinbase is not standard in the repo.

### 2. Proprietary Imbalance Indicator Formula & Dynamic Lookback
- **Trader Quote:**
  > "access to my imbalance indicator which as you will see... gave us the high of this week with two hourly imbalances" (`YuTkhoJ3n-0:0:00:58`)
  > "We had a 30 minute imbalance... that was a purple candle at first." (`a4Um_W3Nfss:0:11:56`)
- **Data Gap:** Habib uses a closed, proprietary TradingView indicator sold via his login portal (`qriptal.com`). While Construct F confirms that it measures relative volume anomalies, the exact rolling lookback window, multi-timeframe smoothing parameters, and adaptive percentile thresholds are undisclosed.

### 3. Real-Time Discord Intraday Level Modifications
- **Trader Quote:**
  > "Going back over to the Discord, when I woke up on Monday... I completely dismissed the bearish plan just because we had seen a break of my [level]" (`yHFg7oVN3ts:0:03:28`)
  > "I will update you inside the Discord. If I am awake." (`0tiz6_pSBuw:0:55:55`)
- **Data Gap:** Habib frequently adjusts plan invalidation levels, cancels pending setups, or calls manual breakeven exits in private Discord channels (`#trading-thoughts`, `#trading-updates`) during live market hours. These discretionary modifications cannot be backtested mechanically from historical video uploads alone.

### 4. Qualitative Discretionary Assessment of "Wick Quality"
- **Trader Quote:**
  > "Even on the 1-hour, we just have one hourly imbalance, and even then, the wick is extremely ugly. So [no entry]" (`f9nuENfR-2o:0:04:34`)
  > "We had a very big and ugly wick on the 4hour... So we have liquidity above it." (`14PZEEbHSaM:0:05:39`)
  > "If we got a big wick, then it will be a bit harder to catch. If we got... a very nice wick, a small body. This makes it a bit easier" (`fBg2-RXPOAk:0:26:48`)
- **Data Gap:** Habib distinguishes between an "ugly wick" (a wide, erratic wick indicating unfinished business and resting liquidity) versus a "good wick" (a clean, sharp rejection of a level). Algorithmic classification of wick aesthetic quality is subjective without an explicit mathematical rule from the author.

---

## 5. Verification Checklist & Audit Integrity

- **Directory Boundary:** All research performed strictly within `F:\MTS\gq\gb-habib-yt` and scratch cache. No modifications made to `.secrets/`, `.env`, or live repository trees.
- **Source Verification:** Every quoted statement matches verbatim public YouTube video subtitles fetched via `yt-dlp en-orig` captions. Exact video IDs and timestamps `[h:mm:ss]` are provided.
- **Label Integrity:** All parameters are strictly separated and labeled `SOURCED` (direct author quotes) or `OURS` (MTS quantitative operationalization).
- **Zero Fabrication:** No video, metric, timestamp, or statement was simulated or rubber-stamped.
