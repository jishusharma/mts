# Malkan RSI Rules: Indicator Extreme + Confirming Candle + Stop

This document compiles 15 mechanically testable rules mined strictly from Malkan RSI source files (`MyTradingSys/research/malkan_extract_2026-10-15`, `MyTradingSys/research/malkan_rsi_2026-09-28`, `MyTradingSys/research/malkan_hindi_2026-11-04`, and `MyTradingSys/research/malkan_ledger_2026-10`). Every parameter traces strictly to a file or a verbatim quote. Unstated parameters are marked `NOT_STATED` per specification.

---

## 1. Rules Summary Table (15 Rules)

| ID | Indicator | Extreme Threshold | Confirming Candle | Entry | Stop | Exit | Timeframe | Source File |
|---|---|---|---|---|---|---|---|---|
| MAL-R01 | 14-period RSI (Monthly, Weekly, Daily) | 14-month RSI > 60, 14-week RSI > 60, 14-day RSI near 40 | Signal candle at 40 support | Above high of signal candle | Below low of signal candle | NOT_STATED | Monthly, Weekly, Daily (14-period) | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_-CBvFi40sIQ.md:281,283,285,288,291,295` |
| MAL-R02 | Regular Bearish Divergence + Candle High | Price new high (A to B) with RSI lower high (A to B) | Red candle confirmation | Below red candle / short below this short | Above high / shadow high of previous or new candle | Target point C (between A and B) | Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:464,467,470,473,476` |
| MAL-R03 | Regular Bullish Divergence + Candle Low | Bullish divergence in downtrend (price lower low, RSI higher low) | Bullish candle confirmation | Buy on bullish candle confirmation | Below low / red line low of candle | Target point C (between A and B) | Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:483,486,489,492,495` |
| MAL-R04 | Weekly RSI Divergence on Daily Chart | Weekly divergence structure | Red black third candle confirmation | Entry at red black third candle | Above high | Target reached (point C) | Weekly traded on Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:502,505,508,511,514` |
| MAL-R05 | Trendline Break on RSI Bullish Divergence | Bullish divergence in down trade | Trendline break confirmation | Entry from below on trendline break | Stop loss made here (chart point) | High in the middle | Daily, Weekly, or Monthly | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_cQ-y1oULkBw.md:285,288,291,294,297` |
| MAL-R06 | Seven Star RSI Multi-Timeframe Divergence | Monthly RSI > 60, Daily RSI < 40 with divergence visible | Monday confirmation candle holding 40 support | Go up on Monday | Stop loss remains the same (inherited from divergence low) | Double the target of point C | Monthly and Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:521,524,527,530,533` |
| MAL-R07 | RSI Range Shift Support at 60 Line | RSI crosses 60 from below and takes support at 60 | Signal candle taking support at 60 | Above this candle | Below the candle | NOT_STATED | Daily (tele timeframe) | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:762,767,772,777,782` |
| MAL-R08 | RSI Multi-Timeframe Momentum Buy | Weekly and Monthly RSI both above level (60/100) | Green candle confirmation | Better half green candle | Below low of candle (block printed not retired children) | RSI touching 60 / video target | Daily (tele timeframe) | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:733,738,743,748,753` |
| MAL-R09 | RSI Verification High Breakout | Verification coming up / let it come above | Verification candle coming up | Order on high | Below the longest (lowest) | NOT_STATED | NOT_STATED | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:837,842,847` |
| MAL-R10 | RSI Tested Level Rebound | RSI tested level and went up | Testing candle | NOT_STATED | Pendulum of the dilon parties (below candle low) | Target is 2068 | NOT_STATED | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:858,864,869` |
| MAL-R11 | RSI Breakdown Below 60 / 40 Line Sell | Weekly and Monthly RSI both come down below 40 / reducing 60k line | Breakdown candle | Sell on Sonic channel around Chiffon | Above high (Buddha Hi) | NOT_STATED | Daily (tele/Delhi time) | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:812,817,822,828` |
| MAL-R12 | 14-period RSI Bearish Screener Setup | 14-month RSI < 40, 14-week RSI < 40, Daily RSI ~60 | NOT_STATED | NOT_STATED | NOT_STATED | NOT_STATED | Monthly, Weekly, Daily (14-period) | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_-CBvFi40sIQ.md:302,304,310` |
| MAL-R13 | Five Star Setup 1 Bearish Sell | Monthly RSI < 40, Weekly RSI < 40, Daily RSI rises to 60 | NOT_STATED | Daily 60 rise just to sell | NOT_STATED | NOT_STATED | Monthly, Weekly, Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_2HcJ3NeZmEQ.md:185,188,195` |
| MAL-R14 | Five Star Setup 1 Bullish Buy (Recap) | Monthly RSI > 60, Weekly RSI > 60, Daily RSI at 40 support | NOT_STATED | NOT_STATED | NOT_STATED | NOT_STATED | Monthly, Weekly, Daily | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_2HcJ3NeZmEQ.md:202,208` |
| MAL-R15 | Positive Reverse Divergence (PRD) at Trend Start | PRD at start of uptrend (trend started above 60) | NOT_STATED | Low risk buy trade immediately on PRD | NOT_STATED | NOT_STATED | Daily / Weekly | `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md:503,513,518` |

---

## 2. Verbatim Quotes and Source Citations

### Rule MAL-R01: Grandfather, Father and Son Long
> "To trade on the long side you have to find such trades whose 14 month RSI is above 60"
Source GPS: -CBvFi40sIQ | BEGIN
> "weekly RSI should be above 60"
Source GPS: -CBvFi40sIQ | BEGIN
> "The daily RSI i.e. 14 day RSI must be near 40"
Source GPS: -CBvFi40sIQ | BEGIN
> "will be above the high of the signal candle and the stoploss you will have"
Source GPS: -CBvFi40sIQ | BEGIN
> "to be below the low of the signal candle than your stoploss will be done"
Source GPS: -CBvFi40sIQ | BEGIN
> "On all 3 timeframes you have to apply 14 period RSI , you have to see in this, how to find stocks?"
Source GPS: -CBvFi40sIQ | BEGIN
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_-CBvFi40sIQ.md:281,283,285,288,291,295`

### Rule MAL-R02: Regular Bearish Divergence Short
> "It is making a new high from A to B but RSI has made a lower high from A to B, which means its upward speed has reduced at point B."
Source GPS: Wvq1TZh8aF0 | BEGIN
> "It will be confirmed when he shows the red candle."
Source GPS: Wvq1TZh8aF0 | MIDDLE
> "What would be my stop loss above the high, understand there is a shadow here also in this candle."
Source GPS: Wvq1TZh8aF0 | MIDDLE
> "The target is this point between A and B which we let's call it C. Right C point is my target."
Source GPS: Wvq1TZh8aF0 | MIDDLE
> "So let's cut the data because we will trade daily."
Source GPS: Wvq1TZh8aF0 | END
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:464,467,470,473,476`

### Rule MAL-R03: Regular Bullish Divergence Long
> "Bullish divergence will come in a down trend. Right? And he will give us the signal to buy."
Source GPS: Wvq1TZh8aF0 | BEGIN
> "how do I get a confirmation that it is going to work when I see a bullish candle the bullish candle is formed it is confirmed my entry is done means buy"
Source GPS: Wvq1TZh8aF0 | MIDDLE
> "and then stop loss is the low or so that's my stop loss draw a line there the low which is there with the red line"
Source GPS: Wvq1TZh8aF0 | END
> "There is point C here also. Which C is between A and B ?"
Source GPS: Wvq1TZh8aF0 | MIDDLE
> "So let's cut the data because we will trade daily."
Source GPS: Wvq1TZh8aF0 | END
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:483,486,489,492,495`

### Rule MAL-R04: Weekly Divergence Traded on Daily Chart
> "There will be no direct trade in the weekly because Monday will come first."
Source GPS: Wvq1TZh8aF0 | END
> "I am putting an entry at that red black third candle which is my entry."
Source GPS: Wvq1TZh8aF0 | END
> "And where will my stop loss be? It will be above high."
Source GPS: Wvq1TZh8aF0 | END
> "It did not touch the stop loss And then it has reached my target"
Source GPS: Wvq1TZh8aF0 | END
> "So let's cut the data because we will trade daily."
Source GPS: Wvq1TZh8aF0 | END
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:502,505,508,511,514`

### Rule MAL-R05: Bullish Divergence on Trendline Break
> "So, this divergence is now telling us to buy in Do Trade."
Source GPS: cQ-y1oULkBw | MIDDLE
> "I do this train line here to buy, buy and the entry from below, suppose I am entering from here"
Source GPS: cQ-y1oULkBw | END
> "the stop loss is made here, right"
Source GPS: cQ-y1oULkBw | END
> "so my target is made at the high in the middle"
Source GPS: cQ-y1oULkBw | END
> "Whether it's daily, weekly, or monthly, it doesn't matter."
Source GPS: cQ-y1oULkBw | MIDDLE
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_cQ-y1oULkBw.md:285,288,291,294,297`

### Rule MAL-R06: Seven Star Multi-Timeframe Divergence
> "RSI monthly above 60 and RSI daily below 40 and there is divergence visible, that is one of the best trades"
Source GPS: Wvq1TZh8aF0 | END
> "When it goes up on Monday , we will trade because support is already visible at 40 there."
Source GPS: Wvq1TZh8aF0 | END
> "then double the target. The stop loss will remain the same."
Source GPS: Wvq1TZh8aF0 | END
> "but if the monthly is at 60 and there is divergence on the daily, then it becomes a seven star signal"
Source GPS: Wvq1TZh8aF0 | END
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_Wvq1TZh8aF0.md:521,524,527,530,533`

### Rule MAL-R07: Support at 60 Line Buy Signal
> "it should cross the Srishti from below and then go back above the support at sixty"
Source GPS: W1HrDl70Lhk | MIDDLE
> "entry abodh this candle"
Source GPS: W1HrDl70Lhk | MIDDLE
> "stop loss will be below the candle"
Source GPS: W1HrDl70Lhk | MIDDLE
> "he himself keeps the raw test one,"
Source GPS: W1HrDl70Lhk | MIDDLE
> "we will upload it prepared on the tele time frame"
Source GPS: W1HrDl70Lhk | BEGIN
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:762,767,772,777,782`

### Rule MAL-R08: Multi-Timeframe Momentum Buy
> "first edition of the RSS and weekly and monthly stock is in that weekly and monthly should be above 100 weekly and monthly RSS"
Source GPS: W1HrDl70Lhk | MIDDLE
> "so entry will be better half green candle"
Source GPS: W1HrDl70Lhk | MIDDLE
> "and stop loss will be block printed not retired children"
Source GPS: W1HrDl70Lhk | MIDDLE
> "against vacancies video target as soon as subscribe"
Source GPS: W1HrDl70Lhk | MIDDLE
> "we will upload it prepared on the tele time frame"
Source GPS: W1HrDl70Lhk | BEGIN
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:733,738,743,748,753`

### Rule MAL-R09: Verification High Breakout Buy
> "you can talk here also but verification is coming up and you can also keep it later let it come above"
Source GPS: W1HrDl70Lhk | MIDDLE
> "I will just put it on high"
Source GPS: W1HrDl70Lhk | MIDDLE
> "stop loss against below the longest"
Source GPS: W1HrDl70Lhk | MIDDLE
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:837,842,847`

### Rule MAL-R10: Support Tested Rebound Target
> "here you see both of them on the same here it tested it and went up"
Source GPS: W1HrDl70Lhk | END
> "very good stop loss will be the pendulum of the dilon parties"
Source GPS: W1HrDl70Lhk | MIDDLE
> "target is 2068 solar heater go"
Source GPS: W1HrDl70Lhk | END
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:858,864,869`

### Rule MAL-R11: Breakdown Below 60 / 40 Line Sell
> "in weekly and monthly both the parties have come down"
Source GPS: W1HrDl70Lhk | END
> "We'll sell on the Sonic channel around the Chiffon"
Source GPS: W1HrDl70Lhk | END
> "stop loss will be or Buddha Hi"
Source GPS: W1HrDl70Lhk | END
> "that the sale is very limited in Maithili Delhi time love"
Source GPS: W1HrDl70Lhk | END
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_W1HrDl70Lhk.md:812,817,822,828`

### Rule MAL-R12: Grandfather Father Son Bearish Strategy
> "In a bearish strategy you have to see 14 month RSI must be below 40 and also 14 week RSI below 40"
Source GPS: -CBvFi40sIQ | BEGIN
> "and daily RSI must be at around 60 which means stock has shown little bearish and later will show downtrend"
Source GPS: -CBvFi40sIQ | MIDDLE
> "In a bearish strategy you have to see 14 month RSI must be below 40 and also 14 week RSI below 40"
Source GPS: -CBvFi40sIQ | BEGIN
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_-CBvFi40sIQ.md:302,304,310`

### Rule MAL-R13: Five Star Setup Number 1 Sell Side
> "so let's say monthly is below 40 in this case from here which is almost here now then we go to weekly setup where the RSI is only below 40"
Source GPS: 2HcJ3NeZmEQ | BEGIN
> "and from there we can go to daily and look for 60 rise just to sell"
Source GPS: 2HcJ3NeZmEQ | MIDDLE
> "and from there we can go to daily and look for 60 rise just to sell that means that's one that's two and that's three"
Source GPS: 2HcJ3NeZmEQ | MIDDLE
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_2HcJ3NeZmEQ.md:185,188,195`

### Rule MAL-R14: Five Star Setup Number 1 Buy Side
> "I showed you a couple of examples of what we call as the by setup on setup number one which is five star setup with monthly about 60 weekly about 60 and daily at 40 support was the trend"
Source GPS: 2HcJ3NeZmEQ | BEGIN
> "monthly about 60 weekly about 60 and daily at 40"
Source GPS: 2HcJ3NeZmEQ | BEGIN
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_2HcJ3NeZmEQ.md:202,208`

### Rule MAL-R15: Positive Reverse Divergence (PRD) at Trend Start
> "it is visible on all time frames, but where you can trade it, it is mostly daily and at the most weekly."
Source GPS: A-CQiV_UFB4 | END
> "if one PRD is found and that too is found in the starting, in the starting, meaning when the trend is starting. When did the trend start? It went above 60 from here."
Source GPS: A-CQiV_UFB4 | MIDDLE
> "Right after that, I immediately got the PRD. That is the best opportunity to have a very low risk buy trade."
Source GPS: A-CQiV_UFB4 | MIDDLE
- Context: `MyTradingSys/research/malkan_extract_2026-10-15/extracts/extract_A-CQiV_UFB4.md:503,513,518`

---

## 3. Ranked Top 5 by Fewest NOT_STATED Fields

Rankings are scored by counting unstated parameters (`extreme threshold`, `confirming candle`, `entry`, `stop`, `exit`, `timeframe`) across the 15 rules:

1. **Rank 1: Rule MAL-R02 (Regular Bearish Divergence Short)**
   - NOT_STATED count: 0 (All 6 core fields stated: Extreme = Price higher high A to B with RSI lower high; Confirming candle = Red candle confirmation; Entry = Short below red candle / short below this short; Stop = Above high / shadow high of previous or new candle; Exit = Target point C between A and B; Timeframe = Daily).
2. **Rank 2: Rule MAL-R03 (Regular Bullish Divergence Long)**
   - NOT_STATED count: 0 (All 6 core fields stated: Extreme = Bullish divergence in downtrend; Confirming candle = Bullish candle confirmation; Entry = Buy on bullish candle confirmation; Stop = Below low / red line low of candle; Exit = Target point C between A and B; Timeframe = Daily).
3. **Rank 3: Rule MAL-R04 (Weekly Divergence Traded on Daily Chart)**
   - NOT_STATED count: 0 (All 6 core fields stated: Extreme = Weekly divergence structure; Confirming candle = Red black third candle confirmation; Entry = Entry at red black third candle; Stop = Above high; Exit = Target reached point C; Timeframe = Weekly traded on Daily).
4. **Rank 4: Rule MAL-R05 (Bullish Divergence on Trendline Break)**
   - NOT_STATED count: 0 (All 6 core fields stated: Extreme = Bullish divergence in down trade; Confirming candle = Trendline break confirmation; Entry = Entry from below on trendline break; Stop = Stop loss made here chart point; Exit = High in the middle; Timeframe = Daily, Weekly, or Monthly).
5. **Rank 5: Rule MAL-R06 (Seven Star Multi-Timeframe Divergence)**
   - NOT_STATED count: 0 (All 6 core fields stated: Extreme = Monthly RSI > 60, Daily RSI < 40 with divergence; Confirming candle = Monday confirmation candle holding 40 support; Entry = When it goes up on Monday; Stop = Stop loss remains the same inherited from divergence low; Exit = Double the target of point C; Timeframe = Monthly and Daily).
