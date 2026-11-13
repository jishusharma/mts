# NK Analyst Rules: Indicator Extreme + Confirming Candle + Stop

This document compiles 15 mechanically testable rules mined from NK StockTalk extracts (`MyTradingSys/research/nk_stocktalk_1113/flash_deep/` and `flash/`).
Every parameter traces strictly to a file or a verbatim quote. Unstated parameters are marked `NOT_STATED` per specification.
Quotes and Source GPS tags have been validated against transcript baselines with `scripts/dev/verify_extract_quotes.py`.

---

## 1. Rules Summary Table (15 Rules)

| ID | Indicator | Extreme Threshold | Confirming Candle | Entry | Stop | Exit | Timeframe | Source File |
|---|---|---|---|---|---|---|---|---|
| NK-R01 | RSI (14) & Standard Pivot | RSI goes below 30 then crosses back above 30 | Candle closes above Pivot level | Reversal buy on close above Pivot | Full body candle close below Pivot | NOT_STATED | NOT_STATED | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:16` |
| NK-R02 | Standard Pivot Points | Price reaches S3 level (oversold extreme support) | NOT_STATED | Bounce support buy at S3 | Full body closing stop | Resistance target at R3 | NOT_STATED | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:30` |
| NK-R03 | Standard Pivot Points (Resistance Breakout) | Price tests / breaks out of R1 level | Candle closes above R1 | Buy triggered on close above R1 | Full body closing below R1 | Target 2 at R2, Target 3 at R3 | NOT_STATED | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:44` |
| NK-R04 | RSI (14-period) | RSI touches 30 zone on 15m chart | 15m candle close near 30 zone | Buy for overnight gap up prediction between 3:00 PM and 3:30 PM | Low of spot candle on daily/intraday chart | Trailing stop on each candle low | 15-minute (with 10-minute and 5-minute confirmation) | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:23` |
| NK-R05 | RSI (14-period) | RSI reaches 70 zone on 15m chart | 15m candle close near 70 zone | Sell / short for overnight gap down prediction between 3:00 PM and 3:30 PM | Spot chart swing high | Trailing stop on candle highs | 15-minute (with 10-minute and 5-minute confirmation) | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:58` |
| NK-R06 | 10-Minute Opening Range | First 10 minutes session low breached | Breakdown candle breaks below opening 10-minute low | Intraday short entry upon low break | NOT_STATED | NOT_STATED | 10-minute | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:15` |
| NK-R07 | 1-Hour Chart Trend Filter | Price reaches support / resistance on 1-hour timeframe | 1-hour candle completion / close | Trend trade entry on 1-hour structure | 1-hour candle low / high (minimizes SL hunting) | NOT_STATED | 1-hour | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:27` |
| NK-R08 | Hilega Milega (RSI + RSI Averages) | Indicator forms 'W' pattern structure at low extreme | Reversal candle completing upward leg of W formation | Buy on upward break of W structure | NOT_STATED | RSI reaches 82 zone | NOT_STATED | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:57` |
| NK-R09 | 20 SMA & Bollinger Bands | Price fails to go above 20 SMA while Bollinger Band blasts | Candle rejected at 20 SMA | Short entry on 20 SMA rejection during BB blast | Previous candle high (closing basis) | NOT_STATED | Daily | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:14` |
| NK-R10 | 20 SMA Trend Regime Filter | Price falls and sustains below 20 SMA | Candle sustains and closes below 20 SMA | Bearish continuation / short bias (no longs until reclaim) | Close back above 20 SMA | NOT_STATED | Daily | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:21` |
| NK-R11 | Bollinger Band Breakout / Blast | Price breaks out of Bollinger Bands / price zone | Breakout candle high is broken | Long breakout entry when breakout candle high is breached | Low of the breakout candle (trailed to previous candle low) | Trailing stop via previous candle low | Scaled by timeframe | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:42` |
| NK-R12 | Moving Average Retest (20 SMA / 50 SMA / AVWAP) | Price pullbacks to 20 SMA, 50 SMA, or AVWAP trendline | Retest candle bounce at moving average support | Retest entry in direction of primary trend | Low of retest candle | Scaled target by timeframe | NOT_STATED | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:63` |
| NK-R13 | Zone Fakeout Reversal | Price breaks zone boundary then closes back inside zone | Reversal candle closes back above/inside zone | Fakeout reversal entry (momentum 3-4x faster than normal breakout) | Low of fakeout candle | Scaled target by timeframe | NOT_STATED | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:98` |
| NK-R14 | ATM Option Staggered Entry (Hedge 23) | Combined ATM CE + PE premium falls below 50 | 5-minute / 1-minute price check post 2:00 PM on expiry day | Buy 2 lots ATM CE + PE when combined premium reaches 50 | Combined premium falls below 9-10 (max loss ~25 pts) | Profit target at 100 (100% gain, half exit) | Expiry day intraday (post 2:00 PM) | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/ZuVWAu_MR2Q/EXTRACT.md:31` |
| NK-R15 | ATM Option Staggered Entry Tier 2 (Hedge 23) | Combined ATM CE + PE premium falls to 30 | Price check post 3:00 PM on expiry day | Buy 2 lots ATM CE + PE when combined premium reaches 30 | Combined premium falls below 9-10 | Profit target at 65-70 (half exit) | Expiry day intraday (post 3:00 PM) | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/ZuVWAu_MR2Q/EXTRACT.md:43` |

---

## 2. Verbatim Quotes and Source Citations

### Rule NK-R01: RSI Oversold Reversal with Pivot Close
> "जैसे गिरते हुए केस में अगर आरएसआई 30 बिलो जाकर दोबारा 30 के ऊपर आए और पीवेट के ऊपर क्लोज कर जाए तो प्राइस में बहुत तेज मूवमेंट देखने को मिलती है"
Source GPS: 3EpXq8JC4jU | BEGIN

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:16`
- Translation: "Like in a falling case, if RSI goes below 30 and then comes back above 30 and closes above the Pivot, then very fast movement is seen in price."

### Rule NK-R02: Standard Pivot S3 Support & R3 Target
> "पिवट में S3 और R3 ये काफी अच्छा सपोर्ट रेजिस्टेंस होता है"
Source GPS: 3EpXq8JC4jU | BEGIN

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:30`
- Translation: "In Pivot, S3 and R3 act as very good support and resistance."

### Rule NK-R03: Pivot R1 Breakout Entry
> "जैसे ही यह R1 के ऊपर क्लोज कर गया हमारी बाइंग होती है"
Source GPS: 3EpXq8JC4jU | MIDDLE

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:44`
- Translation: "As soon as this closes above R1, our buy is triggered."

### Rule NK-R04: 15-Minute RSI 30 Zone Gap-Up Setup
> "30 का जो जोन है उस पे टच करता है कौन से पीरियड की 14 पीरियड की आरएसआई 15 मिनट के टाइम फ्रेम"
Source GPS: cmH38Uo4sYM | MIDDLE

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:23`
- Translation: "Touches the 30 zone, of which period, 14-period RSI on 15-minute timeframe"

### Rule NK-R05: Closing Window RSI 70/30 Gap Rule
> "याद रखिएगा अगर ये तीन कंडीशन मैच कर जाती है क्लोजिंग टाइम पे मतलब 3:00 बजे से लेके 3:30 की ट्रेडिंग के दौरान आरएसआई 15 मिनट की 70 या 30 के जोन"
Source GPS: cmH38Uo4sYM | END

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:58`
- Translation: "Remember, if these three conditions match at closing time, meaning during 3:00 to 3:30 trading: 15-minute RSI at 70 or 30 zone"

### Rule NK-R06: 10-Minute Opening Low Breakdown
> "फर्स्ट 10 मिनट में लो ब्रेक हो जानी चाहिए"
Source GPS: JLcDdrHkB5M | BEGIN

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:15`
- Translation: "In the first 10 minutes the low should be broken"

### Rule NK-R07: 1-Hour Timeframe Trend Filter
> "1 ऑवर के टाइम फ्रेम को देखो"
Source GPS: JLcDdrHkB5M | MIDDLE

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:27`
- Translation: "Look at the 1 hour timeframe"

### Rule NK-R08: Hilega Milega W Formation towards RSI 82
> "एक डब्ल्यू का निर्माण कर देगा हिलेगा मिलेगा ऐसे ऐसे और एक ऐसे ऊपर की तरफ डब्लू बन जाएगा"
Source GPS: JLcDdrHkB5M | END

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:57`
- Translation: "It will form a W, Hilega Milega like this and like this a W will form upwards"

### Rule NK-R09: Bollinger Band Blast Rejection at 20 SMA
> "20 एसए में डे टाइम फ्रेम के ऊपर नहीं जा पाई और बुलिंजर बैंड ब्लास्ट भी कर गई"
Source GPS: wrEEf8o9n9E | BEGIN

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:14`
- Translation: "Could not go above the 20 SMA on the day timeframe and Bollinger Band blast also happened"

### Rule NK-R10: 20 SMA Regime Filter
> "जब भी प्राइस 20 एसएमए के नीचे आकर सस्टेन कर जाए निफ्टी में या बैंक निफ्टी कोई भी इंडेक्सेस में तो वहां पे जब तक वो 20 एसएमए के ऊपर फिर से जाकर क्लोज नहीं करता है वो बुलिशनेस उसमें नहीं आती है"
Source GPS: wrEEf8o9n9E | BEGIN

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:21`
- Translation: "Whenever price sustains below 20 SMA in Nifty or Bank Nifty or any indices, until it closes above 20 SMA again, bullishness does not return"

### Rule NK-R11: Breakout Candle High Break Requirement
> "जो कैंडल ब्रेक करेगी उसका लो हमारे लिए इंपॉर्टेंट होता है"
Source GPS: wrEEf8o9n9E | MIDDLE

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:42`
- Translation: "The candle that breaks will have its low important for us"

### Rule NK-R12: Retest of 20 SMA / 50 SMA / AVWAP
> "प्राइस में फॉल आती है और एक ट्रेंड लाइन आप ले लेते हैं। ट्रेंड लाइन के आसपास कहीं ना प्राइस आती है या कोई मूविंग एवरेज होगी 20 50 या एब होगा उसके पास प्राइस आएगी"
Source GPS: wrEEf8o9n9E | END

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:63`
- Translation: "Price sees a fall and you take a trendline. Price comes around trendline or moving average 20, 50 or AVWAP"

### Rule NK-R13: Fakeout Confirmation via Zone Close
> "अगर ये जोन के ऊपर आ के क्लोज हो जाए तो आप ये मान लेना कि फेक आउट की घटना हुई है"
Source GPS: wrEEf8o9n9E | END

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:98`
- Translation: "If it comes and closes above this zone, then assume that a fakeout event has taken place"

### Rule NK-R14: Expiry ATM Premium Sum < 50
> "सी ई और प्लस पी ई दोनों का जोड़ 50 से नीचे आ रहा हो"
Source GPS: ZuVWAu_MR2Q | BEGIN

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/ZuVWAu_MR2Q/EXTRACT.md:31`
- Translation: "Sum of both CE and PE should come below 50"

### Rule NK-R15: Expiry Staggered Averaging Entry at 30
> "एवरेजिंग का रूल ये होगा कि हमारी पहली एंट्री 50 पे, दूसरी एंट्री 30 पे, तीसरी एंट्री एंट्री 20 के नीचे"
Source GPS: ZuVWAu_MR2Q | MIDDLE

- Source file: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/ZuVWAu_MR2Q/EXTRACT.md:43`
- Translation: "The rule of averaging will be that our first entry is at 50, second entry at 30, third entry below 20"

---

## 3. Top 5 Rules Ranked by Fewest NOT_STATED Fields

Each rule is evaluated across the 7 mechanical execution fields: Indicator, Extreme Threshold, Confirming Candle, Entry, Stop, Exit, Timeframe.

| Rank | Rule ID | Description | Count of NOT_STATED Fields | List of NOT_STATED Fields |
|---|---|---|---|---|
| 1 | NK-R04 | 15m RSI 30 Reversal Gap Up | 0 | None (all 7 parameters specified) |
| 2 | NK-R05 | 15m RSI 70 Reversal Gap Down | 0 | None (all 7 parameters specified) |
| 3 | NK-R14 | Expiry Day ATM CE+PE < 50 Entry | 0 | None (all 7 parameters specified) |
| 4 | NK-R15 | Expiry Day ATM CE+PE Tier 2 (30) Entry | 0 | None (all 7 parameters specified) |
| 5 | NK-R11 | Bollinger Band Breakout with Previous Candle Low SL | 0 | None (all 7 parameters specified) |
