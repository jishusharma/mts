# NK Analyst Rules: Indicator Extreme + Confirming Candle + Stop

This document compiles 15 mechanically testable rules mined from NK stocktalk source files (`MyTradingSys/research/nk_stocktalk_1113/flash_deep/` and `flash/`). Every parameter traces strictly to a file or a verbatim quote. Unstated parameters are marked `NOT_STATED` per specification.

---

## 1. Rules Summary Table (15 Rules)

| ID | Indicator | Extreme Threshold | Confirming Candle | Entry | Stop | Exit | Timeframe | Source File |
|---|---|---|---|---|---|---|---|---|
| NK-R01 | RSI (14) & Standard Pivot | RSI falls below 30 then crosses back above 30 | Candle closes above Pivot level | Buy on close above Pivot | Full body close below Pivot | R1, R2, R3 levels | 15-minute / 1-hour | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:16-17` |
| NK-R02 | Standard Pivot Points | Price falls to Pivot Support S3 | Reversal / bounce candle holding S3 support | Buy bounce off S3 | Closing basis stop below S3 | Pivot / R1 / R2 / R3 | Whichever timeframe followed | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:30-31` |
| NK-R03 | Standard Pivot Points | Price reaches Pivot Resistance R1 | Candle closes above R1 | Buy breakout as soon as candle closes above R1 | Full body close below R1 / Pivot | R2, R3, midpoint of R2-R3 | 15-minute | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:44-45` |
| NK-R04 | 14-period RSI (15-min / 10-min / 5-min) | 14-period RSI touches 30 zone on 15m chart | Multi-timeframe match at closing window (3:00-3:30 PM) | Buy call option / long at closing window (3:00-3:30 PM) | Based on spot index chart (not option premium) | Trailing stop at prior candle lows (or 20m / 1h rule) | 15-minute (with 10m & 5m confirmation) | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:23-24` |
| NK-R05 | 14-period RSI (15-min / 10-min / 5-min) | 14-period RSI touches 70 zone on 15m chart | Multi-timeframe match at closing window (3:00-3:30 PM) | Short / buy put option at closing window (3:00-3:30 PM) | Based on spot index chart (not option premium) | Trailing stop at prior candle highs | 15-minute (with 10m & 5m confirmation) | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:58-59` |
| NK-R06 | Option Spread Conversion | Bought option premium doubles (e.g. 100 to 200) | Price touches 200 level | Short sell higher strike (e.g. 150 strike) to lock 50 pts gain | NOT_STATED | Locked spread profit | NOT_STATED | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:44-45` |
| NK-R07 | Intraday Opening Low Range | Price breaks below opening low | First 10-minute candle breaks low | Short breakdown below first 10m low | 1-hour candle close | NOT_STATED | 10-minute (filter on 1-hour) | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:15-16` |
| NK-R08 | Nifty Weekly Level Resistance | Price tests 24,766 resistance level | Weekly candle closes above 24,766 | Long on weekly breakout above 24,766 | Weekly close below 24,766 | NOT_STATED | Weekly | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:45-46` |
| NK-R09 | Hilega Milega & RSI | Hilega Milega forms W pattern towards 82 RSI zone | Confirming W formation candle structure | Long on W pattern confirmation | 1-hour candle structure | RSI 82 zone | 1-Hour / Daily / Weekly | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:57-58` |
| NK-R10 | Monthly Bollinger Bands | Price approaches / touches upper Bollinger Band | Breakout candle heading towards new high | Long on Bollinger Band blast towards new high | Breakout candle low | NOT_STATED | Monthly | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:51-52` |
| NK-R11 | 20 SMA & Bollinger Bands | Price sustains below 20 SMA with Bollinger Band blast | Daily candle fails to cross back above 20 SMA | Bearish continuation / short below 20 SMA | Close above 20 SMA | NOT_STATED | Daily | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:14-15` |
| NK-R12 | Resistance Breakout & Retest | Price breaks out above key resistance zone | Breakout candle high must be broken | Long entry on breakout high breach or retest of 20/50 SMA/AVWAP | Breakout candle low (or previous candle low) | Trailing SL via previous candle low | Daily / Weekly | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:77-78` |
| NK-R13 | Support Fakeout Reversal | Price breaks below support zone (false breakdown) | Candle reverses and closes back above support zone | Reversal long upon close back above support zone | Low of the fakeout candle | 3 to 4 times faster target momentum | Daily / Intraday | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:98-99` |
| NK-R14 | Expiry Combined ATM Premium (Hedge 23) | Sum of ATM CE + PE falls to 50 (with India VIX < 15) | Post-2:00 PM time window on expiry day | Staggered Buy Tranche 1: ATM CE + PE at 50 | Combined premium falls below 9 or 10 | Target 100 (1:1 minimum reward) | Expiry day intraday (post 2:00 PM) | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/ZuVWAu_MR2Q/EXTRACT.md:31-32` |
| NK-R15 | Expiry Combined ATM Premium (Hedge 23 Tranche 2/3) | Sum of ATM CE + PE falls to 30 (or < 20) | Post-3:00 PM (for 30) or post-3:21 PM (for 20) | Staggered Buy Tranche 2 at 30 / Tranche 3 below 20 | Combined premium falls below 9 or 10 | Exit at 70 (for 30 entry) / Exit half at 45 (for 20 entry) | Expiry day intraday (post 3:00 / 3:21 PM) | `MyTradingSys/research/nk_stocktalk_1113/flash_deep/ZuVWAu_MR2Q/EXTRACT.md:43-44` |

---

## 2. Verbatim Quotes and Source Citations

### Rule NK-R01: RSI Oversold (< 30) Reversal & Pivot Close
> "जैसे गिरते हुए केस में अगर आरएसआई 30 बिलो जाकर दोबारा 30 के ऊपर आए और पीवेट के ऊपर क्लोज कर जाए तो प्राइस में बहुत तेज मूवमेंट देखने को मिलती है"
**Source GPS: 3EpXq8JC4jU | BEGIN**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:16-17` ("Indicator Settings & RSI Filter")

### Rule NK-R02: Standard Pivot S3 / R3 Support & Resistance
> "पिवट में S3 और R3 ये काफी अच्छा सपोर्ट रेजिस्टेंस होता है"
**Source GPS: 3EpXq8JC4jU | BEGIN**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:30-31` ("Key Levels S3 & R3")

### Rule NK-R03: Pivot R1 Breakout Close
> "जैसे ही यह R1 के ऊपर क्लोज कर गया हमारी बाइंग होती है"
**Source GPS: 3EpXq8JC4jU | MIDDLE**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/3EpXq8JC4jU/EXTRACT.md:44-45` ("Buy Condition & Entry")

### Rule NK-R04: 14-Period RSI 30 Zone Touch on 15m Chart (Closing Window Gap Up)
> "30 का जो जोन है उस पे टच करता है कौन से पीरियड की 14 पीरियड की आरएसआई 15 मिनट के टाइम फ्रेम"
**Source GPS: cmH38Uo4sYM | MIDDLE**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:23-24` ("Indicator Parameters: 14-Period RSI Touching 30 Zone on 15-Minute Chart")

### Rule NK-R05: Multi-Timeframe Closing Window RSI Extreme Match
> "याद रखिएगा अगर ये तीन कंडीशन मैच कर जाती है क्लोजिंग टाइम पे मतलब 3:00 बजे से लेके 3:30 की ट्रेडिंग के दौरान आरएसआई 15 मिनट की 70 या 30 के जोन"
**Source GPS: cmH38Uo4sYM | END**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:58-59` ("Entry Timing & Triple Condition: 3:00 to 3:30 PM Window and 15m RSI 70/30")

### Rule NK-R06: Profit Locking Spread Conversion
> "मैंने अगर ₹100 पे खरीदा 200 हो गया तो 150 वाली ऑप्शन को शॉर्ट सेल करेंगे ताकि 50 पॉइंट को हम घर लेके जाएंगे"
**Source GPS: cmH38Uo4sYM | END**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/cmH38Uo4sYM/EXTRACT.md:44-45` ("Profit Locking / Spread Conversion: Converting into Spread to Lock Gain")

### Rule NK-R07: Intraday Opening Low Breakout
> "फर्स्ट 10 मिनट में लो ब्रेक हो जानी चाहिए"
**Source GPS: JLcDdrHkB5M | BEGIN**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:15-16` ("Intraday Opening Low Break")

### Rule NK-R08: Nifty Weekly 24,766 Momentum Breakout
> "निफ्टी अगर इसके ऊपर वीकली आती है 24,766 के ऊपर तो कहीं ना कहीं प्राइस में एक तेज मोमेंटम दिखाई देगी"
**Source GPS: JLcDdrHkB5M | END**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:45-46` ("Nifty Weekly Breakout Level 24,766")

### Rule NK-R09: Hilega Milega W Formation to RSI 82 Zone
> "एक डब्ल्यू का निर्माण कर देगा हिलेगा मिलेगा ऐसे ऐसे और एक ऐसे ऊपर की तरफ डब्लू बन जाएगा"
**Source GPS: JLcDdrHkB5M | END**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:57-58` ("Hilega Milega W Formation")

### Rule NK-R10: Monthly Bollinger Band Blast on New High
> "तो मंथली टाइम फ्रेम कहता है कि अगर ये नया हाई की ओर निकलेगा तो यहां से ही बुलिंजर बैंड ब्लास्ट कर जाएगी"
**Source GPS: JLcDdrHkB5M | END**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md:51-52` ("Monthly Bollinger Band Blast")

### Rule NK-R11: 20 SMA Sustained Breakdown & BB Blast
> "20 एसए में डे टाइम फ्रेम के ऊपर नहीं जा पाई और बुलिंजर बैंड ब्लास्ट भी कर गई"
**Source GPS: wrEEf8o9n9E | BEGIN**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:14-15` ("Bollinger Band Blast & 20 SMA Resistance (BB Length)")

### Rule NK-R12: Breakout Candle High Must Be Broken
> "अगर कोई भी कैंडल ब्रेकआउट लिया है ज़ोन को तो उसका हाई मस्ट बी ब्रोकन"
**Source GPS: wrEEf8o9n9E | END**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:77-78` ("Fakeout Condition (Breakout Candle High Must Be Broken)")

### Rule NK-R13: Support Fakeout Candle Close Reversal
> "अगर ये जोन के ऊपर आ के क्लोज हो जाए तो आप ये मान लेना कि फेक आउट की घटना हुई है"
**Source GPS: wrEEf8o9n9E | END**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/wrEEf8o9n9E/EXTRACT.md:98-99` ("Support Fakeout Confirmation")

### Rule NK-R14: Nifty Hedge 23 Expiry Premium Threshold (< 50)
> "सी ई और प्लस पी ई दोनों का जोड़ 50 से नीचे आ रहा हो"
**Source GPS: ZuVWAu_MR2Q | BEGIN**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/ZuVWAu_MR2Q/EXTRACT.md:31-32` ("Combined CE + PE Premium Threshold")

### Rule NK-R15: Staggered Averaging Entry Triggers (50-30-20 Method)
> "एवरेजिंग का रूल ये होगा कि हमारी पहली एंट्री 50 पे, दूसरी एंट्री 30 पे, तीसरी एंट्री एंट्री 20 के नीचे"
**Source GPS: ZuVWAu_MR2Q | MIDDLE**
- Context: `MyTradingSys/research/nk_stocktalk_1113/flash_deep/ZuVWAu_MR2Q/EXTRACT.md:43-44` ("Staggered Averaging Entry Triggers (50-30-20 Method)")

---

## 3. Ranked Top 5 Rules by Fewest NOT_STATED Fields

Ranking evaluated across the core rule parameter fields (Indicator, Extreme Threshold, Confirming Candle, Entry, Stop, Exit, Timeframe):

1. **NK-R01 (RSI Reversal + Pivot Close)**: 0 `NOT_STATED` fields. All parameters specified (RSI 14, <30 to >30 extreme, close above Pivot confirming candle, buy entry, full body close below Pivot stop, R1/R2/R3 exits, 15m/1h timeframe).
2. **NK-R14 (Hedge 23 Expiry Setup Tranche 1)**: 0 `NOT_STATED` fields. All parameters specified (ATM CE+PE combined premium, <=50 extreme, post-2:00 PM candle/time, buy entry at 50, SL < 9 or 10, target 100 exit, expiry day post-2:00 PM timeframe).
3. **NK-R15 (Hedge 23 Expiry Setup Tranche 2/3)**: 0 `NOT_STATED` fields. All parameters specified (ATM CE+PE combined premium, 30 / <20 extreme, post-3:00 / post-3:21 PM candle/time, buy entry at 30 / <20, SL < 9 or 10, targets 70 / 45 exits, expiry day post-3:00 / post-3:21 PM timeframe).
4. **NK-R04 (15m RSI 30 Zone Gap-Up Setup)**: 0 `NOT_STATED` fields. All parameters specified (14 RSI, 30 zone extreme, 10m/5m match at 3:00-3:30 PM confirming candle, buy entry, spot chart low SL, trailing candle lows exit, 15m timeframe).
5. **NK-R05 (15m RSI 70 Zone Gap-Down Setup)**: 0 `NOT_STATED` fields. All parameters specified (14 RSI, 70 zone extreme, 10m/5m match at 3:00-3:30 PM confirming candle, short entry, spot chart high SL, trailing candle highs exit, 15m timeframe).
