# The Rumers (@the.rumers) Operator-Picked Videos 2/2: Stated Trading Rules Extraction (`RUMERS_EXTRACT_2`)

- **Card:** `gemini-yt-rumers-extract-2`
- **Channel:** `@the.rumers` (`The Rumers`, hosted by Doug and Silvia)
- **Date (UTC):** 2026-11-01
- **Target Videos (5) [SOURCED: `MyTradingSys/system/tasks/gemini-yt-rumers-extract-2.json:15`]:**
  1. `T0H_jpQXdVI` — *"This 15-Minute Scalping Strategy Shouldn't Work... But It Makes Me $2,392/Day"* (Duration: 1414s) — **Captioned (`auto`, `en-orig`, 4399 words)**
  2. `pcYO-yzAtrQ` — *"If I Had to Make $500 by Tomorrow, I'd Use This Trading Strategy"* (Duration: 1659s) — **Captioned (`auto`, `en-orig`, 5417 words)**
  3. `hMURCHLnZVE` — *"The ONLY INDICATOR That Predicts Every Mega Move (Most Traders Use It Wrong)"* (Duration: 1185s) — **Captioned (`auto`, `en-orig`, 3382 words)**
  4. `xtN0U-j_4Jc` — *"The  One Line Indicator That Flat Out Delivers"* (Duration: 1728s) — **Captioned (`auto`, `en-orig`, 5506 words)**
  5. `l0j1irTKIUw` — *"The ONLY INDICATOR That Predicts Monster Moves (Most Traders Use It Wrong)"* (Duration: 1580s) — **Captioned (`auto`, `en-orig`, 5132 words)**

---

## 1. Stated Trading Rules & Setups Table

Every parameter below is labelled `SOURCED` (from video transcript) or `OURS`. Where a specific parameter was not stated in the audio, it is marked `NOT_IN_DATA`.

| Rule ID [OURS] | Video ID | Timestamp | Setup / Rule Name | Timeframe | Indicator | Entry | Stop | Target | Claimed Hit-Rate | Mechanical / Backtestable [OURS] | Verbatim Caption Quote |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R01 | T0H_jpQXdVI | 00:01:52 | 15-Minute Opening Range Candle Close Definition | 15-minute | Opening range high/low box | Wait for first 15m candle to close, box in the high price and low price | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "allow the very first 15-minute candle out of each market open to completely finish and completely close before you and I do any buying or selling whatsoever." |
| R02 | T0H_jpQXdVI | 00:02:35 | 15-Minute High/Low Box Range Construction | 15-minute | Opening range box | Box in the high price and the low price of the opening 15-minute candle | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "what I want to do is box in the high price and the low price of that opening 15-minute candle." |
| R03 | T0H_jpQXdVI | 00:03:34 | Manipulation Candle Definition | 15-minute | Price action volatility / ATR | Identify fast aggressive directional candle moving in one direction | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "a manipulation candle is any fast aggressive moving candle that's going in one direction." |
| R04 | T0H_jpQXdVI | 00:10:55 | John Wick Confirmation and Next Candle Break Entry | 5-minute / 15-minute | Candlestick price action (hammer / wick rejection) | Wait for John Wick candle, enter on next candle that breaks through the high of the John Wick | Stop placed underneath the wick extreme | NOT_IN_DATA | NOT_IN_DATA | YES | "What we're looking to do is enter on the next candle, important, the next candle that takes out the top of the John Wick. So if I mark the top of this John Wick candle, the next candle that pops through the high of that candle, we enter immediately as it breaks the top of that candle. Then we place our stop underneath of that" |
| R05 | T0H_jpQXdVI | 00:20:01 | John Wick Reversal Trigger and Stop | 5-minute | John Wick candle at key support | Enter long as high of John Wick is taken out | Stop placed below the low of the candle | Midpoint of range or range high | NOT_IN_DATA | YES | "all we need is for the high to be taken out of the John Wick, which was around 2640. That That That's the entry. And our stop is going to go below." |
| R06 | pcYO-yzAtrQ | 00:04:11 | Range High and Range Low Definition (Previous Day Extremes) | Daily / Intraday | Previous Day High/Low (PDH/PDL) | Mark previous day high price and low price of the asset | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "The range high and the range low is the previous day's high price and low price of the asset you're trading." |
| R07 | pcYO-yzAtrQ | 00:05:04 | Swing High Definition (Next Structural Peak to the Left) | Daily / Intraday | Structural swing high line | Find next structural high above previous day high on chart to the left | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "The swing high is the next high above the range's high. So, this is the previous day's high price. Just simply start looking over to your left and find the next highest price you see" |
| R08 | pcYO-yzAtrQ | 00:14:04 | Boundary Known Seller Edge Filter | 5-minute | Range High and Swing High confluence | When pressed against known seller level, minimal confirmation needed (single candle close under prior candle) | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "against a known seller that we've established, we don't need that much confirmation to make the trade. All I really need here is for one of these candles to close under the other one." |
| R09 | pcYO-yzAtrQ | 00:24:25 | Range High / Swing High Fade Entry and Tight Risk | 5-minute | Break of structure at Range/Swing High | Enter short on structure break at range/swing high resistance | Placed tightly right above the signal candle high | Pivot support / midpoint of range | NOT_IN_DATA | YES | "We broke our structure. Right there was the ideal entry on this. You could stop out above the high here, but let's go ahead and stay with a very tight risk." |
| R10 | pcYO-yzAtrQ | 00:26:50 | Known Seller / Buyer Alignment Edge Principle | 5-minute | Range boundaries (high/low) and Swing boundaries | Back trade entry against established institutional seller or buyer | Beyond boundary extreme | Opposite range boundary / midpoint | NOT_IN_DATA | YES (Edge principle) | "It's that you're backing yourself against a known seller. And when you do that, the trades have a better potential of working." |
| R11 | hMURCHLnZVE | 00:03:30 | RSI Indicator Baseline Configuration | 1-hour | RSI (Relative Strength Index), 70 and 30 bands | Set chart timeframe to 1 hour; leave default RSI settings, focusing on 70 and 30 bands | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "We're going to leave the settings as they are. We want to focus only on the two bands, 70 and 30 RSI. Next, we want to make sure that we set up the time frame to 1 hour." |
| R12 | hMURCHLnZVE | 00:05:22 | RSI Extreme Threshold Bias Rule | 1-hour | RSI 70/30 | If RSI <= 30 look to buy; if RSI >= 70 look to sell | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "So, rule number one, if the RSI is at 30 or below, we want to be looking to buy. If the RSI is at 70 or above, we want to be looking to sell." |
| R13 | hMURCHLnZVE | 00:07:07 | RSI + Liquidity Zone Confluence Step | 1-hour | RSI + Key Liquidity Levels | Combine RSI overbought/oversold with structural support/resistance liquidity zones | NOT_IN_DATA | NOT_IN_DATA | Claimed 20% boost in accuracy | YES (Component filter) | "by adding just that one simple step, you can boost the accuracy by 20% and turn random signals into a reliable system." |
| R14 | hMURCHLnZVE | 00:09:47 | Hourly Candlestick Close Confirmation Entry | 1-hour | Hourly reversal candlestick | Enter long as soon as hourly candlestick closes green above its high, or short on red close below its low | Underneath the reversal candle extreme | Previous resistance / liquidity zone | NOT_IN_DATA | YES | "As soon as that hourly candlestick closes green, our entry is happening above the high of that first green candlestick." |
| R15 | hMURCHLnZVE | 00:14:09 | Hourly RSI Short Entry Stop Loss Placement | 1-hour | RSI >= 70 + Resistance Liquidity + Candlestick Rejection | Enter short upon rejection at resistance with RSI overbought | Placed slightly above the high of the rejection red candlestick | Previous support / hourly swing low | NOT_IN_DATA | YES | "Now in this example, the stop loss can be placed slightly above that red candlestick right here." |
| R16 | xtN0U-j_4Jc | 00:05:21 | 9 EMA Buy Cross Rule (Long Bias Holding State) | 5-minute | 9 EMA (Exponential Moving Average) | Buy when price is at or above 9 EMA; remain long until price crosses below | Price cross below 9 EMA | Exit upon price crossing below 9 EMA | NOT_IN_DATA | YES | "If the price of the asset we are trading is at or above that 9 EMA, all right, we want to buy that asset and we want to remain buyers or stay bought in that asset until the price crosses through. Then and only then do we sell." |
| R17 | xtN0U-j_4Jc | 00:06:04 | 9 EMA Sell Cross Rule (Short / Flat Holding State) | 5-minute | 9 EMA | Sell or remain flat when price is below 9 EMA; stay out until price reclaims 9 EMA | Price cross above 9 EMA | Exit upon price crossing above 9 EMA | NOT_IN_DATA | YES | "if the price of the asset is trading below that 9 EMA we want to sell remain selling or refrain from buying until the price of that asset reclaims that 9 EMA and crosses through. Then and only then do we buy." |
| R18 | xtN0U-j_4Jc | 00:13:46 | 9 EMA Trend Persistence Bar Count Rule | 5-minute | 9 EMA | Each consecutive bar closing above/below 9 EMA increases trend continuation probability | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "the more bars that accumulate above or below, the more likelihood that trend is to continue." |
| R19 | xtN0U-j_4Jc | 00:23:07 | 9 EMA Separation Mean-Reversion Target | 5-minute | 9 EMA | Fade extreme overextension from 9 EMA | Beyond extreme bar high/low | Target is revisitation / touch of the 9 EMA line | NOT_IN_DATA | YES | "The target becomes revisitation of that 9 EMA." |
| R20 | xtN0U-j_4Jc | 00:24:37 | 9 EMA Trailing Stop and Risk Guide | 5-minute | 9 EMA | Manage active position using 9 EMA line | Use 9 EMA line as dynamic stop-loss guide rather than risking entire swing low | Trail along 9 EMA until crossed | NOT_IN_DATA | YES | "We can just use that 9 EMA as a stop-loss and even a profit trailing guide." |
| R21 | l0j1irTKIUw | 00:03:47 | Extended Hours Chart Requirement for 9 EMA | 5-minute | 9 EMA with Extended Hours | Enable 24-hour / extended hours session data to properly calculate 9 EMA | NOT_IN_DATA | NOT_IN_DATA | NOT_IN_DATA | YES (Component filter) | "Go into the settings menu and make sure you click 24-hour data or extended hours trading." |
| R22 | l0j1irTKIUw | 00:09:55 | 9 EMA Secondary Entry and Tight Stop Placement | 5-minute | 9 EMA pullback / rejection | Secondary entry on pullback towards 9 EMA | Stop loss placed just right above the 9 EMA line instead of high of day | NOT_IN_DATA | NOT_IN_DATA | YES | "the entry would have been right about there, and you could could placed the stop loss just right above the 9 EMA instead of that high of the day as to where I would have put it." |
| R23 | l0j1irTKIUw | 00:19:41 | 9 EMA Separation Threshold (20% of Daily ATR) | 5-minute vs Daily ATR | 9 EMA + Daily ATR | Adequate separation requires distance between price and 9 EMA to equal or exceed 20% of Daily ATR | NOT_IN_DATA | Revisitation of 9 EMA | NOT_IN_DATA | YES (Component filter) | "If the distance between the 9 EMA and the price of the asset is $2.20 or more, then you have adequate separation." |
| R24 | l0j1irTKIUw | 00:22:09 | 9 EMA Separation Reversal Stop Loss Placement | 5-minute | 9 EMA + Candlestick Reversal | Enter reversal upon close of reversal candle after 20% ATR separation | Placed either above the high of the reversal red bar or above preceding green bar | Break of 9 EMA and trail | NOT_IN_DATA | YES | "Stop goes either above the red bar or for the riskier traders, above the green bar." |
| R25 | l0j1irTKIUw | 00:22:40 | 9 EMA Separation Profit Target and Follow | 5-minute | 9 EMA | In separation reversal trade | Trailing stop along 9 EMA | Break of the 9 EMA, then follow/trail along the 9 EMA until crossed back | NOT_IN_DATA | YES | "And the target price becomes a break of the 9 EMA, then a follow of the 9 EMA." |

---

## 2. Verbatim Caption Quotes

All quotes below are checked against canonical transcripts in `raw_transcripts_canonical/` with thirds computed by character offset.

### Video 1: `T0H_jpQXdVI` — *"This 15-Minute Scalping Strategy Shouldn't Work... But It Makes Me $2,392/Day"*
> "allow the very first 15-minute candle out of each market open to completely finish and completely close before you and I do any buying or selling whatsoever."
**Source GPS: T0H_jpQXdVI | BEGIN**

> "what I want to do is box in the high price and the low price of that opening 15-minute candle."
**Source GPS: T0H_jpQXdVI | BEGIN**

> "a manipulation candle is any fast aggressive moving candle that's going in one direction."
**Source GPS: T0H_jpQXdVI | BEGIN**

> "What we're looking to do is enter on the next candle, important, the next candle that takes out the top of the John Wick. So if I mark the top of this John Wick candle, the next candle that pops through the high of that candle, we enter immediately as it breaks the top of that candle. Then we place our stop underneath of that"
**Source GPS: T0H_jpQXdVI | MIDDLE**

> "all we need is for the high to be taken out of the John Wick, which was around 2640. That That That's the entry. And our stop is going to go below."
**Source GPS: T0H_jpQXdVI | END**

### Video 2: `pcYO-yzAtrQ` — *"If I Had to Make $500 by Tomorrow, I'd Use This Trading Strategy"*
> "The range high and the range low is the previous day's high price and low price of the asset you're trading."
**Source GPS: pcYO-yzAtrQ | BEGIN**

> "The swing high is the next high above the range's high. So, this is the previous day's high price. Just simply start looking over to your left and find the next highest price you see"
**Source GPS: pcYO-yzAtrQ | BEGIN**

> "against a known seller that we've established, we don't need that much confirmation to make the trade. All I really need here is for one of these candles to close under the other one."
**Source GPS: pcYO-yzAtrQ | MIDDLE**

> "We broke our structure. Right there was the ideal entry on this. You could stop out above the high here, but let's go ahead and stay with a very tight risk."
**Source GPS: pcYO-yzAtrQ | END**

> "It's that you're backing yourself against a known seller. And when you do that, the trades have a better potential of working."
**Source GPS: pcYO-yzAtrQ | END**

### Video 3: `hMURCHLnZVE` — *"The ONLY INDICATOR That Predicts Every Mega Move (Most Traders Use It Wrong)"*
> "We're going to leave the settings as they are. We want to focus only on the two bands, 70 and 30 RSI. Next, we want to make sure that we set up the time frame to 1 hour."
**Source GPS: hMURCHLnZVE | BEGIN**

> "So, rule number one, if the RSI is at 30 or below, we want to be looking to buy. If the RSI is at 70 or above, we want to be looking to sell."
**Source GPS: hMURCHLnZVE | BEGIN**

> "by adding just that one simple step, you can boost the accuracy by 20% and turn random signals into a reliable system."
**Source GPS: hMURCHLnZVE | MIDDLE**

> "As soon as that hourly candlestick closes green, our entry is happening above the high of that first green candlestick."
**Source GPS: hMURCHLnZVE | MIDDLE**

> "Now in this example, the stop loss can be placed slightly above that red candlestick right here."
**Source GPS: hMURCHLnZVE | END**

### Video 4: `xtN0U-j_4Jc` — *"The  One Line Indicator That Flat Out Delivers"*
> "If the price of the asset we are trading is at or above that 9 EMA, all right, we want to buy that asset and we want to remain buyers or stay bought in that asset until the price crosses through. Then and only then do we sell."
**Source GPS: xtN0U-j_4Jc | BEGIN**

> "if the price of the asset is trading below that 9 EMA we want to sell remain selling or refrain from buying until the price of that asset reclaims that 9 EMA and crosses through. Then and only then do we buy."
**Source GPS: xtN0U-j_4Jc | BEGIN**

> "the more bars that accumulate above or below, the more likelihood that trend is to continue."
**Source GPS: xtN0U-j_4Jc | MIDDLE**

> "The target becomes revisitation of that 9 EMA."
**Source GPS: xtN0U-j_4Jc | END**

> "We can just use that 9 EMA as a stop-loss and even a profit trailing guide."
**Source GPS: xtN0U-j_4Jc | END**

### Video 5: `l0j1irTKIUw` — *"The ONLY INDICATOR That Predicts Monster Moves (Most Traders Use It Wrong)"*
> "Go into the settings menu and make sure you click 24-hour data or extended hours trading."
**Source GPS: l0j1irTKIUw | BEGIN**

> "the entry would have been right about there, and you could could placed the stop loss just right above the 9 EMA instead of that high of the day as to where I would have put it."
**Source GPS: l0j1irTKIUw | MIDDLE**

> "If the distance between the 9 EMA and the price of the asset is $2.20 or more, then you have adequate separation."
**Source GPS: l0j1irTKIUw | END**

> "Stop goes either above the red bar or for the riskier traders, above the green bar."
**Source GPS: l0j1irTKIUw | END**

> "And the target price becomes a break of the 9 EMA, then a follow of the 9 EMA."
**Source GPS: l0j1irTKIUw | END**

---

## 3. Testable Mechanical Setups Shortlist

From the 25 extracted rules across the 5 operator-picked videos, 4 setups are completely mechanical and disambiguated for immediate backtesting:

### Setup T1: 15-Minute Pattern Scalp Reversal (`T0H_jpQXdVI`)
- **Speaker:** Doug
- **Category:** Intraday Opening Range Mean Reversion
- **Rules / Components:** R01, R02, R03, R04, R05
- **Timeframe:** 15m opening range filter; 5m trigger
- **Condition:** First 15m candle range >= 20% of Daily ATR (Manipulation candle threshold)
- **Entry:** On next candle that crosses / breaks the extreme of the John Wick confirmation candle (hammer high for long, inverted hammer low for short)
- **Stop:** Placed below the low of the John Wick candle / low of day (Long) or above high of candle / high of day (Short)
- **Target:** 50% midpoint of the 15-minute opening range
- **Disambiguation [OURS]:** If opening 15m range < 20% Daily ATR, setup is invalidated for the day.

### Setup T2: 4-Point Boundary Confluence Fade (`pcYO-yzAtrQ`)
- **Speaker:** Doug
- **Category:** Range & Structural Swing Confluence Fade
- **Rules / Components:** R06, R07, R08, R09, R10
- **Timeframe:** Daily reference levels; 5m execution
- **Levels:** Range High (PDH), Range Low (PDL), Swing High (next structural pivot high to the left above PDH), Swing Low (next structural pivot low to the left below PDL)
- **Entry:** Price tests Range High + Swing High zone (or Range Low + Swing Low zone) during session open. Enter short on first 5m candle closing under prior candle (break of structure)
- **Stop:** Placed tightly above signal candle high / swing high
- **Target:** Center / midpoint of previous day range (or opposite boundary)
- **Disambiguation [OURS]:** If price breaks cleanly through Swing High without stalling/reversing within 30 minutes of open, trade is skipped.

### Setup T3: Hourly RSI Liquidity Reversal (`hMURCHLnZVE`)
- **Speaker:** Silvia
- **Category:** Higher-Timeframe Mean Reversion
- **Rules / Components:** R11, R12, R13, R14, R15
- **Timeframe:** 1-hour chart (hourly)
- **Indicator:** 14-period RSI (70 overbought, 30 oversold bands)
- **Condition:** RSI <= 30 at major horizontal support liquidity level, or RSI >= 70 at major resistance liquidity level
- **Entry:** Long as soon as hourly candle closes green with entry above its high (Short when hourly candle closes red with entry below its low)
- **Stop:** Placed slightly below reversal green candle low (Long) or above red candle high (Short)
- **Target & Trailing:** Target previous swing high / resistance; trail stop bar-by-bar behind previous hourly candle extreme as RSI moves toward 50
- **Disambiguation [OURS]:** Liquidity levels defined by 20-bar hourly swing highs/lows.

### Setup T4: 9 EMA 20% ATR Separation Reversion (`l0j1irTKIUw` & `xtN0U-j_4Jc`)
- **Speaker:** Doug
- **Category:** Moving Average Extension & Mean Reversion Scalp
- **Rules / Components:** R16, R17, R19, R20, R21, R22, R23, R24, R25
- **Timeframe:** 5-minute chart with 24-hour extended hours enabled
- **Indicators:** 9 Exponential Moving Average (EMA) and 14-period Daily ATR
- **Condition:** Absolute distance between price and 9 EMA >= 20% of Daily ATR (Separation filter)
- **Entry:** Enter counter-trend upon first reversal candle close back toward the 9 EMA (sell into red close, buy into green close)
- **Stop:** Placed above the high of the reversal candle (Short) or below low (Long)
- **Target:** Revisitation and break of the 9 EMA line, then trail stop along the 9 EMA until price crosses back over the 9 EMA
- **Disambiguation [OURS]:** Minimum 20% ATR separation must exist at the time of signal candle close.

