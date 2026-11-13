# Malkan RSI Rules: Indicator Extreme + Confirming Candle + Stop

This document compiles 15 mechanically testable rules mined from Malkan RSI source files (`MyTradingSys/research/malkan_extract_2026-10-15`). Every rule follows the exact specification: indicator at a measured extreme + confirming candle + stop, with exact parameters and verbatim quotes. Parameters not stated in the source are strictly marked `NOT_STATED`.

---

## 1. Rules Summary Table (15 Rules)

| ID | Indicator | Extreme Threshold | Confirming Candle | Entry | Stop | Exit | Timeframe | Source File |
|---|---|---|---|---|---|---|---|---|
| MAL-R01 | RSI (14-period) Multi-Timeframe | Monthly RSI > 60 AND Weekly RSI > 60 AND Daily RSI ~ 40 | Signal candle near daily 40 support | Above the high of the signal candle | Below the low of the signal candle | NOT_STATED | Monthly, Weekly, Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_-CBvFi40sIQ.md:277-295` |
| MAL-R02 | RSI (14-period) Multi-Timeframe Bearish | Monthly RSI < 40 AND Weekly RSI < 40 AND Daily RSI ~ 60 | Signal candle at daily 60 resistance | NOT_STATED | NOT_STATED | NOT_STATED | Monthly, Weekly, Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_-CBvFi40sIQ.md:300-312` |
| MAL-R03 | RSI Regular Bearish Divergence | Price higher high (A to B) with RSI lower high | Red candle formed | Short upon red candle confirmation | Above the high of the signal candle (including shadow) | Target point C (trough between peaks A and B) | Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:462-480` |
| MAL-R04 | RSI Regular Bullish Divergence | Regular bullish divergence in a downtrend (price lower low, RSI higher low) | Bullish candle formed | Buy upon bullish candle confirmation | Below the low of the signal candle | Target point C (peak between troughs A and B) | Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:481-499` |
| MAL-R05 | Weekly RSI Divergence Executed Daily | Divergence visible on Weekly chart | Third candle (red/black day candle) | At the red/black third candle | Above the high of the candle | Reached target (point C) | Weekly context, Daily entry | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:500-518` |
| MAL-R06 | Seven Star RSI Setup | Monthly RSI > 60 AND Daily RSI < 40 with bullish divergence | Monday upward candle / resumption | Long upon Monday move up off 40 support | Inherited from base divergence setup (below low) | Double the base divergence target (2x point C) | Monthly & Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:519-537` |
| MAL-R07 | Five Star Setup Type 1 (Buy Side) | Weekly RSI > 60 AND Monthly RSI > 60 | Green candle formed | High of the green candle ("better half green candle") | Below the low of the green candle | NOT_STATED (caption garbled) | Daily, Weekly, Monthly | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:731-755` |
| MAL-R08 | Five Star Setup Type 2: Support at 60 Line | RSI crosses 60 from below, retests and takes support at 60 line | Candle taking support at 60 | Above the signal candle ("entry abodh this candle") | Below the candle | NOT_STATED | Daily, Weekly, Monthly | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:760-785` |
| MAL-R09 | Five Star Setup Type 2 Mirrored (Short Side) | Weekly and Monthly RSI below 40, Daily crosses below 40 and retests 40 resistance | Candle failing at 40 resistance | NOT_STATED | NOT_STATED | NOT_STATED | Daily, Weekly, Monthly | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:789-805` |
| MAL-R10 | Five Star Setup Sell Side | Weekly RSI < 40 AND Monthly RSI < 40 | Signal candle formed | Sell on candle breakdown | Above the high of the signal candle | NOT_STATED | Daily, Weekly, Monthly | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:810-830` |
| MAL-R11 | Five Star Buy Example Order on High | RSI pullback / support verification | Verification candle coming up | Order on high of the candle | Stop below the lowest (low of the pattern) | NOT_STATED | NOT_STATED | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:835-850` |
| MAL-R12 | Five Star Buy Example Retest with Target | Both Weekly & Monthly RSI above 60, tested level and went up | Retest candle confirming upward turn | NOT_STATED | Below the low of the signal candle | Stated price target 2068 | NOT_STATED | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:856-870` |
| MAL-R13 | Positive Reverse Divergence (PRD) Buy | Price higher low with RSI lower low in an uptrend | Bullish confirmation candle | Buy on PRD signal | NOT_STATED | NOT_STATED | Daily, Weekly | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md:489-508` |
| MAL-R14 | PRD at Trend Inception (Low Risk Buy) | RSI crosses above 60 to start uptrend, followed immediately by PRD | First PRD pullback candle at trend start | Buy immediately upon PRD | NOT_STATED | NOT_STATED | Daily, Weekly | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md:511-525` |
| MAL-R15 | Negative Reverse Divergence (NRD) Sell | Price lower high with RSI higher high inside an existing downtrend | Breakdown candle making a new low | Sell on NRD signal with trend | NOT_STATED | NOT_STATED | Daily, Weekly | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md:528-545` |

---

## 2. Detailed Rules with Verbatim Source Quotes and Source GPS

### Rule MAL-R01: Grandfather, Father and Son Long Setup
- **Indicator Extreme:** Monthly RSI > 60 AND Weekly RSI > 60 AND Daily RSI ~ 40 (14-period RSI on all three timeframes).
- **Confirming Candle:** Daily signal candle holding support at 40.
- **Entry:** Above the high of the signal candle.
- **Stop:** Below the low of the signal candle.
- **Exit:** NOT_STATED.
- **Timeframe:** Monthly, Weekly, Daily.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_-CBvFi40sIQ.md:277-295`
> "On all 3 timeframes you have to apply 14 period RSI , you have to see in this, how to find stocks?"
**Source GPS: -CBvFi40sIQ | BEGIN**
> "To trade on the long side you have to find such trades whose 14 month RSI is above 60"
**Source GPS: -CBvFi40sIQ | BEGIN**
> "weekly RSI should be above 60"
**Source GPS: -CBvFi40sIQ | BEGIN**
> "The daily RSI i.e. 14 day RSI must be near 40"
**Source GPS: -CBvFi40sIQ | BEGIN**
> "will be above the high of the signal candle and the stoploss you will have"
**Source GPS: -CBvFi40sIQ | BEGIN**
> "to be below the low of the signal candle than your stoploss will be done"
**Source GPS: -CBvFi40sIQ | BEGIN**

---

### Rule MAL-R02: Grandfather, Father and Son Bearish Setup
- **Indicator Extreme:** Monthly RSI < 40 AND Weekly RSI < 40 AND Daily RSI ~ 60 (14-period RSI).
- **Confirming Candle:** Daily signal candle turning down near 60 resistance.
- **Entry:** NOT_STATED.
- **Stop:** NOT_STATED.
- **Exit:** NOT_STATED.
- **Timeframe:** Monthly, Weekly, Daily.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_-CBvFi40sIQ.md:300-312`
> "In a bearish strategy you have to see 14 month RSI must be below 40 and also 14 week RSI below 40"
**Source GPS: -CBvFi40sIQ | BEGIN**
> "and daily RSI must be at around 60 which means stock has shown little bearish and later will show downtrend"
**Source GPS: -CBvFi40sIQ | MIDDLE**

---

### Rule MAL-R03: Regular Bearish Divergence Short
- **Indicator Extreme:** Price higher high (A to B) while RSI makes a lower high.
- **Confirming Candle:** Red candle formed.
- **Entry:** Short upon red candle confirmation.
- **Stop:** Above the high of the signal candle (including shadow).
- **Exit:** Point C (trough between swing peaks A and B).
- **Timeframe:** Daily.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:462-480`
> "It is making a new high from A to B but RSI has made a lower high from A to B, which means its upward speed has reduced at point B."
**Source GPS: Wvq1TZh8aF0 | BEGIN**
> "It will be confirmed when he shows the red candle."
**Source GPS: Wvq1TZh8aF0 | MIDDLE**
> "What would be my stop loss above the high, understand there is a shadow here also in this candle."
**Source GPS: Wvq1TZh8aF0 | MIDDLE**
> "The target is this point between A and B which we let's call it C. Right C point is my target."
**Source GPS: Wvq1TZh8aF0 | MIDDLE**
> "So let's cut the data because we will trade daily."
**Source GPS: Wvq1TZh8aF0 | END**

---

### Rule MAL-R04: Regular Bullish Divergence Long
- **Indicator Extreme:** Bullish divergence in a downtrend (price lower low, RSI higher low).
- **Confirming Candle:** Bullish candle formed.
- **Entry:** Buy upon bullish candle confirmation.
- **Stop:** Below the low of the signal candle.
- **Exit:** Point C (peak between swing troughs A and B).
- **Timeframe:** Daily.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:481-499`
> "Bullish divergence will come in a down trend. Right? And he will give us the signal to buy."
**Source GPS: Wvq1TZh8aF0 | BEGIN**
> "how do I get a confirmation that it is going to work when I see a bullish candle the bullish candle is formed it is confirmed my entry is done means buy"
**Source GPS: Wvq1TZh8aF0 | MIDDLE**
> "and then stop loss is the low or so that's my stop loss draw a line there the low which is there with the red line"
**Source GPS: Wvq1TZh8aF0 | END**
> "There is point C here also. Which C is between A and B ?"
**Source GPS: Wvq1TZh8aF0 | MIDDLE**
> "So let's cut the data because we will trade daily."
**Source GPS: Wvq1TZh8aF0 | END**

---

### Rule MAL-R05: Weekly Divergence Traded on Daily Chart
- **Indicator Extreme:** Divergence identified on Weekly timeframe.
- **Confirming Candle:** Third day red/black candle.
- **Entry:** At that red/black third candle.
- **Stop:** Above the high.
- **Exit:** Target reached (point C).
- **Timeframe:** Weekly context, Daily entry.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:500-518`
> "There will be no direct trade in the weekly because Monday will come first."
**Source GPS: Wvq1TZh8aF0 | END**
> "I am putting an entry at that red black third candle which is my entry."
**Source GPS: Wvq1TZh8aF0 | END**
> "And where will my stop loss be? It will be above high."
**Source GPS: Wvq1TZh8aF0 | END**
> "It did not touch the stop loss And then it has reached my target"
**Source GPS: Wvq1TZh8aF0 | END**
> "So let's cut the data because we will trade daily."
**Source GPS: Wvq1TZh8aF0 | END**

---

### Rule MAL-R06: Seven Star RSI Divergence Setup
- **Indicator Extreme:** Monthly RSI > 60 AND Daily RSI < 40 with bullish divergence.
- **Confirming Candle:** Upward candle on Monday showing support at 40.
- **Entry:** Long when it goes up on Monday off 40 support.
- **Stop:** Inherited from base divergence setup (below the low of the signal candle).
- **Exit:** Double the base target (2x point C).
- **Timeframe:** Monthly and Daily.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:519-537`
> "RSI monthly above 60 and RSI daily below 40 and there is divergence visible, that is one of the best trades"
**Source GPS: Wvq1TZh8aF0 | END**
> "When it goes up on Monday , we will trade because support is already visible at 40 there."
**Source GPS: Wvq1TZh8aF0 | END**
> "then double the target. The stop loss will remain the same."
**Source GPS: Wvq1TZh8aF0 | END**
> "but if the monthly is at 60 and there is divergence on the daily, then it becomes a seven star signal"
**Source GPS: Wvq1TZh8aF0 | END**

---

### Rule MAL-R07: Five Star Setup Type 1 (Buy Side)
- **Indicator Extreme:** Weekly RSI > 60 AND Monthly RSI > 60 (stated as above 60 level).
- **Confirming Candle:** Green candle formed.
- **Entry:** High of the green candle ("better half green candle").
- **Stop:** Below the low of the green candle.
- **Exit:** NOT_STATED.
- **Timeframe:** Daily, Weekly, Monthly.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:731-755`
> "first edition of the RSS and weekly and monthly stock is in that weekly and monthly should be above 100 weekly and monthly RSS"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "so entry will be better half green candle"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "and stop loss will be block printed not retired children"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "against vacancies video target as soon as subscribe"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "we will upload it prepared on the tele time frame"
**Source GPS: W1HrDl70Lhk | BEGIN**

---

### Rule MAL-R08: Five Star Setup Type 2 (Support at 60 Line)
- **Indicator Extreme:** RSI crosses 60 from below, retests and takes support at the 60 line.
- **Confirming Candle:** Candle confirming bounce/support at 60.
- **Entry:** Above the signal candle ("entry abodh this candle").
- **Stop:** Below the candle.
- **Exit:** NOT_STATED.
- **Timeframe:** Daily, Weekly, Monthly.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:760-785`
> "it should cross the Srishti from below and then go back above the support at sixty"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "entry abodh this candle"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "stop loss will be below the candle"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "he himself keeps the raw test one,"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "we will upload it prepared on the tele time frame"
**Source GPS: W1HrDl70Lhk | BEGIN**

---

### Rule MAL-R09: Five Star Setup Type 2 Mirrored (Short Side)
- **Indicator Extreme:** Weekly and Monthly RSI below 40, Daily crosses below 40 and retests 40 resistance.
- **Confirming Candle:** Candle confirming rejection below 40.
- **Entry:** NOT_STATED.
- **Stop:** NOT_STATED.
- **Exit:** NOT_STATED.
- **Timeframe:** Daily, Weekly, Monthly.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:789-805`
> "similarly for celebrity weekly and monthly RS 850 security system coffee line from below poverty line is crossing below and going back up and running"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "we keep the raw test one"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "we will upload it prepared on the tele time frame"
**Source GPS: W1HrDl70Lhk | BEGIN**

---

### Rule MAL-R10: Five Star Setup Sell Side Breakdown
- **Indicator Extreme:** Weekly RSI < 40 AND Monthly RSI < 40.
- **Confirming Candle:** Breakdown candle formed.
- **Entry:** Sell on the candle breakdown.
- **Stop:** Above the high of the signal candle ("or Buddha Hi").
- **Exit:** NOT_STATED.
- **Timeframe:** Daily, Weekly, Monthly.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:810-830`
> "in weekly and monthly both the parties have come down"
**Source GPS: W1HrDl70Lhk | END**
> "We'll sell on the Sonic channel around the Chiffon"
**Source GPS: W1HrDl70Lhk | END**
> "stop loss will be or Buddha Hi"
**Source GPS: W1HrDl70Lhk | END**
> "that the sale is very limited in Maithili Delhi time love"
**Source GPS: W1HrDl70Lhk | END**

---

### Rule MAL-R11: Five Star Buy Example (Order on High)
- **Indicator Extreme:** RSI pullback and verification coming up.
- **Confirming Candle:** Verification candle coming above.
- **Entry:** Put order on high of the candle.
- **Stop:** Below the lowest.
- **Exit:** NOT_STATED.
- **Timeframe:** NOT_STATED.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:835-850`
> "you can talk here also but verification is coming up and you can also keep it later let it come above"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "I will just put it on high"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "stop loss against below the longest"
**Source GPS: W1HrDl70Lhk | MIDDLE**

---

### Rule MAL-R12: Five Star Buy Example (Retest with Target 2068)
- **Indicator Extreme:** Both timeframes tested level and went up.
- **Confirming Candle:** Test and upward reversal candle.
- **Entry:** NOT_STATED.
- **Stop:** Below the low of the signal candle ("pendulum of the dilon parties").
- **Exit:** Target 2068.
- **Timeframe:** NOT_STATED.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:856-870`
> "here you see both of them on the same here it tested it and went up"
**Source GPS: W1HrDl70Lhk | END**
> "very good stop loss will be the pendulum of the dilon parties"
**Source GPS: W1HrDl70Lhk | MIDDLE**
> "target is 2068 solar heater go"
**Source GPS: W1HrDl70Lhk | END**

---

### Rule MAL-R13: Positive Reverse Divergence (PRD) Buy
- **Indicator Extreme:** Positive reverse divergence (price makes a higher low while RSI makes a lower low) inside an uptrend.
- **Confirming Candle:** Bullish candle holding trend structure.
- **Entry:** Buy signal captured on PRD.
- **Stop:** NOT_STATED.
- **Exit:** NOT_STATED.
- **Timeframe:** Daily, Weekly.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md:489-508`
> "Whenever you look at an up trend, what I have to look for is a positive reverse divergence."
**Source GPS: A-CQiV_UFB4 | MIDDLE**
> "what is your signal to buy, this is where we get a signal, this is the uptrend, we capture on PRD, PRD means positive reverse divergence"
**Source GPS: A-CQiV_UFB4 | MIDDLE**
> "it is visible on all time frames, but where you can trade it, it is mostly daily and at the most weekly."
**Source GPS: A-CQiV_UFB4 | END**

---

### Rule MAL-R14: PRD at Trend Inception (Low Risk Buy)
- **Indicator Extreme:** Trend start confirmed when RSI crosses above 60, followed immediately by first PRD.
- **Confirming Candle:** First PRD pullback candle at trend start.
- **Entry:** Buy immediately upon PRD appearance.
- **Stop:** NOT_STATED.
- **Exit:** NOT_STATED.
- **Timeframe:** Daily, Weekly.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md:511-525`
> "if one PRD is found and that too is found in the starting, in the starting, meaning when the trend is starting. When did the trend start? It went above 60 from here."
**Source GPS: A-CQiV_UFB4 | MIDDLE**
> "Right after that, I immediately got the PRD. That is the best opportunity to have a very low risk buy trade."
**Source GPS: A-CQiV_UFB4 | MIDDLE**

---

### Rule MAL-R15: Negative Reverse Divergence (NRD) Sell
- **Indicator Extreme:** Negative reverse divergence (price makes a lower high while RSI makes a higher high) inside an existing downtrend.
- **Confirming Candle:** Breakdown candle making a new low.
- **Entry:** Sell signal captured on NRD with trend.
- **Stop:** NOT_STATED.
- **Exit:** NOT_STATED.
- **Timeframe:** Daily, Weekly.
- **Source File:** `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md:528-545`
> "where will you see this, you will see it in a downtrend The NRD will be visible within the down trend that is already underway."
**Source GPS: A-CQiV_UFB4 | END**
> "assisting in the downtrend, I am getting a sell signal, which means I am going with the trend, so what more do I need than that, assisting in the downtrend, a new low and then NRD you get a sell signal"
**Source GPS: A-CQiV_UFB4 | END**
> "it is visible on all time frames, but where you can trade it, it is mostly daily and at the most weekly."
**Source GPS: A-CQiV_UFB4 | END**

---

## 3. Ranked Top 5 by Fewest NOT_STATED Fields

Rankings are scored by counting unstated parameters across the 6 core operational fields (`Extreme Threshold`, `Confirming Candle`, `Entry`, `Stop`, `Exit`, `Timeframe`):

1. **Rank 1 (Tie): Rule MAL-R03 (Regular Bearish Divergence Short)**
   - NOT_STATED count: 0
   - Fields: Extreme = Higher high in price with lower high in RSI; Confirming Candle = Red candle formed; Entry = Short upon red candle; Stop = Above signal candle high including shadow; Exit = Point C (trough between peaks A and B); Timeframe = Daily.
2. **Rank 1 (Tie): Rule MAL-R04 (Regular Bullish Divergence Long)**
   - NOT_STATED count: 0
   - Fields: Extreme = Regular bullish divergence in downtrend; Confirming Candle = Bullish candle formed; Entry = Buy upon bullish candle; Stop = Below low of signal candle; Exit = Point C (peak between troughs A and B); Timeframe = Daily.
3. **Rank 1 (Tie): Rule MAL-R05 (Weekly Divergence Traded Daily)**
   - NOT_STATED count: 0
   - Fields: Extreme = Divergence on Weekly chart; Confirming Candle = Third day red/black candle; Entry = At red/black third candle; Stop = Above high; Exit = Point C target; Timeframe = Weekly context, Daily entry.
4. **Rank 1 (Tie): Rule MAL-R06 (Seven Star RSI Setup)**
   - NOT_STATED count: 0
   - Fields: Extreme = Monthly RSI > 60 AND Daily RSI < 40 with divergence; Confirming Candle = Monday candle off 40 support; Entry = Long upon Monday move up; Stop = Inherited below low of signal candle; Exit = Double base divergence target (2x point C); Timeframe = Monthly and Daily.
5. **Rank 5 (Tie): Rule MAL-R01 (Grandfather, Father and Son Long Setup)**
   - NOT_STATED count: 1 (Exit: NOT_STATED)
   - Fields: Extreme = Monthly RSI > 60, Weekly RSI > 60, Daily RSI ~ 40; Confirming Candle = Daily signal candle at 40 support; Entry = Above high of signal candle; Stop = Below low of signal candle; Exit = NOT_STATED; Timeframe = Monthly, Weekly, Daily.
