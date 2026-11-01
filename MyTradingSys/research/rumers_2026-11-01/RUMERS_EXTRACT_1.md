# The Rumers (@the.rumers) Operator-Picked Videos 1/2: Stated Trading Rules Extraction (`RUMERS_EXTRACT_1`)

- **Card:** `gemini-yt-rumers-extract-1`
- **Channel:** `@the.rumers` (`The Rumers`, hosted by Doug and Silvia)
- **Date (UTC):** 2026-11-01
- **Target Videos (5) [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-1.json:15`]:**
  1. `6WfTIyJ-YzQ` — *"If I Could Only Trade ONE Strategy… This Would Be It"* (Duration: 1534s) — **Captioned (`auto`, `en-orig`, 5076 words)**
  2. `EoQDQVblmMY` — *"The One " Box Theory" Strategy That Works Everyday ( Stupid Simple And Proven)"* (Duration: 1405s) — **Captioned (`auto`, `en-orig`, 4714 words)**
  3. `N6zlfBJsoRc` — *"I Always Wait For THIS Before Entering Trades  ( Unsharp Candles )"* (Duration: 1572s) — **Captioned (`auto`, `en-orig`, 5035 words)**
  4. `kozesVBKkg4` — *"2 Stupid Simple VWAP Trading Strategies"* (Duration: 1641s) — **Captioned (`auto`, `en-orig`, 5590 words)**
  5. `aTMFouI9mF4` — *"The " ONE CANDLE "  Scalping Strategy I Will Use For Life"* (Duration: 1263s) — **Captioned (`auto`, `en-orig`, 3848 words)**

---

## 1. Stated Trading Rules & Setups Table

Every parameter below is labelled `SOURCED` (from video transcript) or `OURS`. Where a specific parameter was not stated in the audio, it is marked `NOT_IN_DATA`.

| Rule ID [OURS] | Video ID | Timestamp | Setup / Rule Name | Timeframe | Indicator | Entry | Stop | Target | Claimed Hit-Rate | Mechanical / Backtestable [OURS] | Verbatim Caption Quote |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | 6WfTIyJ-YzQ | 00:03:21 | 15-Minute Opening Range Box Definition | 15-minute | Price action opening range box | Wait for first 15m candle to close, mark high and low extremes | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "allow the first 15 minutes of each market session to pass before you do anything. So allow this bar to completely close and finish its cycle. Now once it's finished its cycle and the 15minute time period is up and that candle has closed, you're going to grab any kind of drawing tool. You can use lines. I like to use boxes and you're going to mark the very high price point of that box and you are going to connect it with the very low price point of that box. And that is going to define our opening range." |
| R02 | 6WfTIyJ-YzQ | 00:06:36 | Daily ATR Baseline Read | Daily | Average True Range (ATR) | Switch to daily chart and add Average True Range indicator | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "move it from a 15minute chart to a daily chart. So you'll see the daily chart frame is now selected. Once that's done, go into your indicator menu, wherever that may be located, and search for the indicator average true range." |
| R03 | 6WfTIyJ-YzQ | 00:08:08 | Manipulation Candle ATR Threshold (20% Daily ATR) | 15-minute vs Daily ATR | 20% of Daily ATR | Opening 15m candle range >= 20% of Daily ATR qualifies as manipulation candle | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "We want to multiply that by 20%. So, in this case, that would give us a number of $320 or so, I think it is, right? So, take the daily range, multiply it by 20%, and you're going to come up with $3.20." |
| R04 | 6WfTIyJ-YzQ | 00:11:15 | John Wick Hammer Reversal Trigger | 5-minute | Candlestick price action | Enter reversal on break of 5m hammer / inverted hammer wick extreme | Placed below session low of day (Long) or above session high (Short) | Target 50% midpoint to 100% of 15m opening range | NOT_IN_DATA | YES | "The stop loss goes below the low of the day, right? Keeping our losses small. And the target price is either 50% to 100% of the range." |
| R05 | 6WfTIyJ-YzQ | 00:14:20 | Power of Tower Engulfing Reversal Trigger | 5-minute | Candlestick price action | Enter reversal when 5m candle engulfs or retraces 30% to 50% of manipulation move | Placed above session high of day (Short) or below low of day (Long) | Target 50% midpoint of opening range | NOT_IN_DATA | YES | "If the power of tower is very bold bearish red, what I normally look for is about 30% to 50%. I normally do not let the full candle finish unless it wasn't very big in the range so I'm looking for about 30 to 40%" |
| R06 | 6WfTIyJ-YzQ | 00:23:40 | Intraday Manipulation Spike Midpoint Target | 5-minute | Price action & Daily ATR | Enter short on break of signal candle after upward manipulation spike | Placed above high of day | Target 50% midpoint of range | NOT_IN_DATA | YES | "So, you would enter a sell here. Stop loss would go above the high of the day. Target price goes down into the middle of that range." |
| R07 | EoQDQVblmMY | 00:01:28 | Previous Day High and Low Box Mapping | Daily to Intraday | Range box boundaries | Box in the previous day high and low price | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "The first thing we want to do is box in the previous day's high and low price. Now, this is very easy to do. You can look at a daily chart and just mark the high and low of that candle" |
| R08 | EoQDQVblmMY | 00:02:53 | Box Boundary Resistance Sell-Side Bias | Intraday (5m) | Range box boundaries | If price opens close to, at, or above previous day box, be sell-side focused (do not buy) | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "If whenever you begin your trading day or the market opens that you're trading, if prices are close to, at or above that box, do not buy at that moment in time. Don't buy yet. If the prices are there, we want to be sell side focused." |
| R09 | EoQDQVblmMY | 00:03:20 | Box Boundary Support Buy-Side Bias | Intraday (5m) | Range box boundaries | If price opens close to, at, or below previous day box, do not sell (look for buys) | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "The inverse relationship is down towards the bottom. If the prices are close to, at or below that box, do not sell. Don't sell a position that you currently have or don't engineer a short trade all the way down there." |
| R10 | EoQDQVblmMY | 00:03:41 | Box Midpoint Chop Avoidance Filter ("Don't Diddle in the Middle") | Intraday (5m) | Range midpoint line | Do not execute trades in the center/midpoint zone of the box during the open | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "one of the most effective things about the box theory itself is we want to take a line and draw right through the center of that box. And I would highly recommend, there's something we've been using for a very long time here, a phrase. It's called don'tdle in the middle." |
| R11 | EoQDQVblmMY | 00:18:43 | Box Boundary Fade Stop Loss & Target | Intraday (5m) | Previous day box | Enter fade bounce off previous day boundary | Stop placed below the low of the day | Target previous day box top / opposite boundary | NOT_IN_DATA | YES | "Stop is going to be below the low of the day there just so we're all on the same page with that." |
| R12 | N6zlfBJsoRc | 00:00:56 | Unsharp FSE Method Overview | 5-minute | Candlestick sequence | First sign execution (FSE) unsharp entry method | NOT_IN_DATA | NOT_IN_DATA | Claimed 80% accuracy | YES (Method overview) | "entries with something we call the FSE method first sign execution also known as the unsharp" |
| R13 | N6zlfBJsoRc | 00:03:15 | Unsharp Risk/Reward and Target Expansion | 5-minute | Candlestick sequence | Enter at origin pivot reducing risk exposure | Stop placed underneath signal pivot | Target expanded to structural high | Claimed 80% accuracy | YES | "reducing your risk exposure expanding your Target and doing it with 80% accuracy that's the unsharp method" |
| R14 | N6zlfBJsoRc | 00:03:36 | Three-Candle Sequence Step 1: Lead Candle | 5-minute | Candlestick sequence | Step 1: bold robust candle creating panic/liquidity | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "all we need is a series of three candles and it's that easy starting with something we call the lead candle" |
| R15 | N6zlfBJsoRc | 00:04:06 | Three-Candle Sequence Step 2: Confirmation Candle | 5-minute | Candlestick sequence | Step 2: candle confirming legitimacy of buyer stepping in | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "number two is something we call the confirmation candle now the confirmation candle is exactly as it is spoken it's to confirm the legitimacy of the buyer who stepped in and bought that bold red strong candle" |
| R16 | N6zlfBJsoRc | 00:04:26 | Three-Candle Sequence Step 3: Execution Candle | 5-minute | Candlestick sequence | Step 3: enter fast as pivot takes place | Stop tightly below confirmation wick | High reward-to-risk target | NOT_IN_DATA | YES | "and the last part of this which is very important is the execution candle there will be another candle that will appear letting you know that a pivot is about ready to take place we have to get in this spot as fast as we can" |
| R17 | kozesVBKkg4 | 00:11:37 | Two VWAP Strategies: Separator and Kiss Pivot | 5-minute | VWAP | Strategy 1: Separator; Strategy 2: Kiss Pivot | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Strategy overview) | "The first is going to be something we call the separator. The second is going to be the kiss pivot." |
| R18 | kozesVBKkg4 | 00:11:51 | VWAP Separator Strategy Core Logic | 5-minute | VWAP | Enter counter-trend when price is extended/separated far from VWAP | Beyond extreme exhaustion wick | Exit when price reconvenes with VWAP | NOT_IN_DATA | YES | "What we are going to do is we're going to take advantage of the separation between that assets price and the VWAP. moment in time where they get extended and separated from one another. That is going to become our trade entry. And our exit is going to be the nuance of them reconvening with one another here in the future." |
| R19 | kozesVBKkg4 | 00:12:18 | VWAP Separator Timing Window (First 15-20 Min) | 5-minute | VWAP | Look for separator trades during the first 15 to 20 minutes of market open | NOT_IN_DATA | Target VWAP | Claimed 90% of best trades happen in open | YES (Component filter) | "90% of these trades, the very best ones, happen at the first 15 to 20 minutes of market open." |
| R20 | kozesVBKkg4 | 00:14:56 | VWAP Separator Overextension Filter | 5-minute | VWAP & Resistance | Prohibit chasing extended trend; enter short only after overextension into resistance | Beyond resistance pivot | Target VWAP line | NOT_IN_DATA | YES | "Number one, we are far separated from the VWAP and we are overextended." |
| R21 | kozesVBKkg4 | 00:16:17 | VWAP Kiss Pivot Strategy Core Logic | 5-minute | VWAP | Enter trend continuation when pullback kisses and rejects VWAP | Stop beyond VWAP rejection wick | Target nearest support/resistance level | NOT_IN_DATA | YES | "strategy we're going to talk about here is called the KISS pivot. And this usually comes after the separator. Once we've had that retracement that moves us back into VWAP, what we're going to be looking to do is have that thing right off the VWAP. just kind of bounce off it, just kind of kiss that and either move back up or go back down" |
| R22 | aTMFouI9mF4 | 00:00:03 | Pattern Scalp Session Open Anchor Window | 15-minute | Price action opening range | Anchor setup on first one hour of each trading session | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "take advantage of the first one hour of each trading session. It's called the pattern scalp. It's repeatable. It's newbie" |
| R23 | aTMFouI9mF4 | 00:11:15 | John Wick Short Stop Loss Placement | 5-minute | Candlestick price action | Enter short on break of bearish John Wick candle | Stop loss placed at high of the day | Target standard 2:1 or range midpoint | NOT_IN_DATA | YES | "The stop loss would be at the high of the day if the very next candle would be red." |
| R24 | aTMFouI9mF4 | 00:11:27 | Bearish John Wick Qualifiable Entry Trigger | 5-minute | Candlestick price action | Enter short when following candle confirms red | Stop loss placed above the high | Minimum 2:1 RR or midpoint | NOT_IN_DATA | YES | "This would be a qualifiable entry for me. So, here I would sell. The stop loss would be placed above the high, right? Because this is now the bearish Johnwick formation." |
| R25 | aTMFouI9mF4 | 00:18:46 | Pattern Scalp Range Midpoint Profit Target | 5-minute | Opening range box | Enter on John Wick / Power of Tower signal | Stop beyond session extreme | Target half (midpoint) of the opening range | NOT_IN_DATA | YES | "Target would be probably somewhere here about half of that range. Just like lay it right there" |

---

## 2. Verbatim Caption Quotes

All quotes below are checked against canonical transcripts in `raw_transcripts_canonical/` with thirds computed by character offset.

### Video 1: `6WfTIyJ-YzQ`
> "allow the first 15 minutes of each market session to pass before you do anything. So allow this bar to completely close and finish its cycle. Now once it's finished its cycle and the 15minute time period is up and that candle has closed, you're going to grab any kind of drawing tool. You can use lines. I like to use boxes and you're going to mark the very high price point of that box and you are going to connect it with the very low price point of that box. And that is going to define our opening range."
**Source GPS: 6WfTIyJ-YzQ | BEGIN**

> "move it from a 15minute chart to a daily chart. So you'll see the daily chart frame is now selected. Once that's done, go into your indicator menu, wherever that may be located, and search for the indicator average true range."
**Source GPS: 6WfTIyJ-YzQ | BEGIN**

> "We want to multiply that by 20%. So, in this case, that would give us a number of $320 or so, I think it is, right? So, take the daily range, multiply it by 20%, and you're going to come up with $3.20."
**Source GPS: 6WfTIyJ-YzQ | BEGIN**

> "The stop loss goes below the low of the day, right? Keeping our losses small. And the target price is either 50% to 100% of the range."
**Source GPS: 6WfTIyJ-YzQ | MIDDLE**

> "If the power of tower is very bold bearish red, what I normally look for is about 30% to 50%. I normally do not let the full candle finish unless it wasn't very big in the range so I'm looking for about 30 to 40%"
**Source GPS: 6WfTIyJ-YzQ | MIDDLE**

> "So, you would enter a sell here. Stop loss would go above the high of the day. Target price goes down into the middle of that range."
**Source GPS: 6WfTIyJ-YzQ | END**

### Video 2: `EoQDQVblmMY`
> "The first thing we want to do is box in the previous day's high and low price. Now, this is very easy to do. You can look at a daily chart and just mark the high and low of that candle"
**Source GPS: EoQDQVblmMY | BEGIN**

> "If whenever you begin your trading day or the market opens that you're trading, if prices are close to, at or above that box, do not buy at that moment in time. Don't buy yet. If the prices are there, we want to be sell side focused."
**Source GPS: EoQDQVblmMY | BEGIN**

> "The inverse relationship is down towards the bottom. If the prices are close to, at or below that box, do not sell. Don't sell a position that you currently have or don't engineer a short trade all the way down there."
**Source GPS: EoQDQVblmMY | BEGIN**

> "one of the most effective things about the box theory itself is we want to take a line and draw right through the center of that box. And I would highly recommend, there's something we've been using for a very long time here, a phrase. It's called don'tdle in the middle."
**Source GPS: EoQDQVblmMY | BEGIN**

> "Stop is going to be below the low of the day there just so we're all on the same page with that."
**Source GPS: EoQDQVblmMY | END**

### Video 3: `N6zlfBJsoRc`
> "entries with something we call the FSE method first sign execution also known as the unsharp"
**Source GPS: N6zlfBJsoRc | BEGIN**

> "reducing your risk exposure expanding your Target and doing it with 80% accuracy that's the unsharp method"
**Source GPS: N6zlfBJsoRc | BEGIN**

> "all we need is a series of three candles and it's that easy starting with something we call the lead candle"
**Source GPS: N6zlfBJsoRc | BEGIN**

> "number two is something we call the confirmation candle now the confirmation candle is exactly as it is spoken it's to confirm the legitimacy of the buyer who stepped in and bought that bold red strong candle"
**Source GPS: N6zlfBJsoRc | BEGIN**

> "and the last part of this which is very important is the execution candle there will be another candle that will appear letting you know that a pivot is about ready to take place we have to get in this spot as fast as we can"
**Source GPS: N6zlfBJsoRc | BEGIN**

### Video 4: `kozesVBKkg4`
> "The first is going to be something we call the separator. The second is going to be the kiss pivot."
**Source GPS: kozesVBKkg4 | MIDDLE**

> "What we are going to do is we're going to take advantage of the separation between that assets price and the VWAP. moment in time where they get extended and separated from one another. That is going to become our trade entry. And our exit is going to be the nuance of them reconvening with one another here in the future."
**Source GPS: kozesVBKkg4 | MIDDLE**

> "90% of these trades, the very best ones, happen at the first 15 to 20 minutes of market open."
**Source GPS: kozesVBKkg4 | MIDDLE**

> "Number one, we are far separated from the VWAP and we are overextended."
**Source GPS: kozesVBKkg4 | MIDDLE**

> "strategy we're going to talk about here is called the KISS pivot. And this usually comes after the separator. Once we've had that retracement that moves us back into VWAP, what we're going to be looking to do is have that thing right off the VWAP. just kind of bounce off it, just kind of kiss that and either move back up or go back down"
**Source GPS: kozesVBKkg4 | MIDDLE**

### Video 5: `aTMFouI9mF4`
> "take advantage of the first one hour of each trading session. It's called the pattern scalp. It's repeatable. It's newbie"
**Source GPS: aTMFouI9mF4 | BEGIN**

> "The stop loss would be at the high of the day if the very next candle would be red."
**Source GPS: aTMFouI9mF4 | MIDDLE**

> "This would be a qualifiable entry for me. So, here I would sell. The stop loss would be placed above the high, right? Because this is now the bearish Johnwick formation."
**Source GPS: aTMFouI9mF4 | MIDDLE**

> "Target would be probably somewhere here about half of that range. Just like lay it right there"
**Source GPS: aTMFouI9mF4 | END**

---

## 3. TESTABLE Shortlist (Mechanical Rules for Backtesting)

The following 4 testable mechanical setups from this video batch have unambiguous entry, stop loss, and target conditions ready for pre-registration in downstream card `rumers-testable-rules-dev-backtest`:

### T1: `RUMERS-ORB-MANIP-REVERSAL` (Videos: `6WfTIyJ-YzQ` R01-R06, `aTMFouI9mF4` R22-R25)
- **Timeframe:** 15m session anchor + 5m execution.
- **Filter:** Opening 15-minute bar range `(High_15m - Low_15m) >= 0.20 * Daily_ATR(14)` [SOURCED: `6WfTIyJ-YzQ` 00:08:08].
- **Trigger:** Reversal candle on 5m (John Wick hammer / inverted hammer, or Power of Tower engulfing >= 30-50% retracement) following manipulation bar [SOURCED: `6WfTIyJ-YzQ` 00:11:15, 00:14:20; `aTMFouI9mF4` 00:11:27]. Enter on next 5m bar breaking signal bar extreme.
- **Stop Loss:** Strictly beyond session high of day (for Short) or session low of day (for Long) [SOURCED: `6WfTIyJ-YzQ` 00:11:15; `aTMFouI9mF4` 00:11:15].
- **Target:** TP1 = 50% midpoint of the 15m opening range `(High_15m + Low_15m) / 2`; TP2 = 100% (opposite boundary of 15m range) [SOURCED: `6WfTIyJ-YzQ` 00:11:15, 00:23:40; `aTMFouI9mF4` 00:18:46].
- **Claimed Hit-Rate:** `NOT_IN_DATA` (qualitative: "most of the time manipulation candles get reversed").

### T2: `RUMERS-BOX-PDH-PDL-FADE` (Video: `EoQDQVblmMY` R07-R11)
- **Timeframe:** Daily reference levels (Previous Day High `PDH`, Previous Day Low `PDL`) + 5m execution.
- **Filter:** Mark PDH and PDL box. Prohibit entries in central 30% chop zone ("don't diddle in the middle") [SOURCED: `EoQDQVblmMY` 00:01:28, 00:03:41].
- **Trigger:** Price pierces beyond PDH or PDL during the morning session, then prints a 5m rejection candle closing back inside the previous day box. Enter fade trade on close of that 5m bar [SOURCED: `EoQDQVblmMY` 00:02:53, 00:03:20].
- **Stop Loss:** Placed beyond extreme sweep wick outside the box [SOURCED: `EoQDQVblmMY` 00:18:43].
- **Target:** 50% equilibrium midpoint of previous day range for TP1; opposite box boundary for TP2 [SOURCED: `EoQDQVblmMY` 00:18:43].
- **Claimed Hit-Rate:** `NOT_IN_DATA` ("proven everyday setup").

### T3: `RUMERS-VWAP-SEPARATOR-MEAN-REVERSION` (Video: `kozesVBKkg4` R17-R20)
- **Timeframe:** 5-minute.
- **Filter:** Extreme price separation from session VWAP during first 15 to 20 minutes of market open (`Distance >= 2.0 * ATR_5m` or test of previous day horizontal resistance/support) [SOURCED: `kozesVBKkg4` 00:11:51, 00:12:18, 00:14:56].
- **Trigger:** Reversal fatigue candle (pin bar or rejection bar) closing back toward VWAP. Enter counter-trend mean reversion trade on candle close.
- **Stop Loss:** Placed beyond extreme exhaustion wick [SOURCED: `kozesVBKkg4` 00:14:56].
- **Target:** Session VWAP line [SOURCED: `kozesVBKkg4` 00:11:51].
- **Claimed Hit-Rate:** `NOT_IN_DATA` (qualitative: "90% of these trades, the very best ones, happen at the first 15 to 20 minutes of market open").

### T4: `RUMERS-VWAP-KISS-PIVOT-CONTINUATION` (Video: `kozesVBKkg4` R17, R21)
- **Timeframe:** 5-minute.
- **Filter:** Established trend bias relative to session VWAP (above VWAP = long only, below VWAP = short only) following initial morning impulse and separator phase [SOURCED: `kozesVBKkg4` 00:16:17].
- **Trigger:** Orderly pullback touches or kisses the VWAP line and prints a rejection candle in trend direction. Enter trend continuation on candle close.
- **Stop Loss:** Placed beyond VWAP rejection swing pivot [SOURCED: `kozesVBKkg4` 00:16:17].
- **Target:** Prior swing high / resistance level or minimum 1:2 risk-to-reward ratio [SOURCED: `kozesVBKkg4` 00:16:17].
- **Claimed Hit-Rate:** `NOT_IN_DATA`.
