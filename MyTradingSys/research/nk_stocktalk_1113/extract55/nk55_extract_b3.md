# NK StockTalk extract, batch 3 of 5 (11 videos)

Source: F:\MTS\data_cache\youtube\nk\*_timed.txt (auto Hindi captions; garbled words kept verbatim, flagged where it matters). Selection: 55 non-interview files sorted by name, every 5th from index 3. Quotes are verbatim captions with the timestamp. Translations are mine.

Headline: the Hilega Milega (HM) formula is NOT given in any of these 11 videos. What they add is the state reading (red line below = buying), the RSI 14 > 50 companion on the daily, timeframe usage (monthly, weekly, daily, 15-20 min, last 5-10-15 min), and what HM must do for a reversal to count. HM is always a confirmation/filter, never an entry trigger on its own.

---

## ovQp5I2ZIKs - "HEDGE 23 Buyer vs Seller Battle | Intraday Setup & Hedging Strategy" (2025-11-07, Nifty/Sensex weekly-expiry day)
This is the only video with fully mechanical rules (options, expiry day). Three variants: seller (short straddle/strangle), buyer (long strangle of cheap legs), hedger.

1. Seller entry time. Wait for price to settle after the open, then short.
   - Quote [00:02:40]: «ओपनिंग होने के 10-15 मिनट में बस प्राइस को स्टेबल हो जाने दें। अगर कोई गैप अप या गैप डाउन हुआ है तो प्राइस को स्टेबल हो जाने दें।»
   - EN: In the first 10-15 minutes after open just let price stabilise; if there was a gap up/down, let it settle.
   - Quote [00:02:55]: «9:35 9:40 के आसपास तो आपको करना क्या है कि जो भी उस समय का नियर ओटीएम स्ट्राइक होगा या एटीएम स्ट्राइक होगा ... उसे हम शॉर्ट सेल कर देंगे कॉल और पुट दोनों को मतलब एक स्ट्रडल की तरह या स्ट्रेंगल की तरह»
   - EN: Around 9:35-9:40 short the near-OTM or ATM call and put together, straddle or strangle.
   - Quote [00:16:14]: «खुलते ही मत करना। थोड़ा स्टेबल होने देना प्रीमियम और वो 9:30 9:35 तक हो जाता है मैक्सिमम स्टेबल»
   - EN: Do not do it at the open; premium is most stable by 9:30-9:35. (He actually entered around 9:37-9:40; "9:40 price is standard" [00:18:01].)
2. Seller stop = SUM stop (combined premium), placed on both legs.
   - Quote [00:03:45]: «दोनों साइड दोनों स्ट्राइक का 110 से ऊपर आपको स्टॉप लॉस लगा देनी है»
   - EN: Place a stop on both strikes above the combined premium (example 50 + 60 = 110, so stop at 115-120 on each leg).
   - Quote [00:06:52]: «115 लगा दीजिए, 120 लगा दीजिए। दोनों साइड में लगाकर छोड़ दीजिए। उससे क्या होगा कि किसी साइड में अगर वाइल्ड मूव आएगी तो आपका स्टॉप लॉस उसी साइड का कटेगा»
   - EN: Put 115 or 120 on both sides and leave it. In a wild move only the side that moves gets stopped.
   - Quote [00:12:19]: «एसएल एम डालनी है ... ट्रिगर प्राइस ... 115 ... या आप चाहते हैं कि नहीं हम पूछ से बचे तो एसएल पर भी जा सकते हैं»
   - EN: Use SL-M with trigger 115 (or SL-limit if you fear the expiry-tail spike). 120 vs 115: "5 points".
   - Risk claim [00:07:08]: «मुश्किल से 15 20 पॉइंट का रिस्क आपका होगा»  (about 15-20 points risk) and later «30-30 पॉइंट का स्टॉप लॉस ले लो» [00:16:41] (budget 30 points per stop-out).
3. After one leg stops, exit the other too.
   - Quote [00:07:08]: «जब कट जाए आप देख ले कट गया तो उसे भी निकल जाइए क्योंकि अभी एक साइड लगभग जीरो हो जाता है»
   - Quote [00:07:35]: «जब मेरा स्टॉप लॉस कट जाए तो हाथ जोड़ के पीछे हट जाना है और समझ जाना है कि आज बाजार में मोमेंटम है»
   - EN: Once a stop is hit, walk away; today has momentum, better for the buyer.
4. Seller time limit: no new risk after 12:00 (backtest only until 12:00).
   - Quote [00:08:21]: «12:00 बजे के बाद आपको नहीं करनी चाहिए। 12:00 बजे तक का ही स्टॉप लॉस कीजिए अगर आप बैक टेस्ट करते हैं»
   - Quote [00:20:39]: «सेलर 12:00 बजे के पहले अगर प्रॉफिट बुक करना जानते हैं»
   - EN: Do not do it after 12:00; if you backtest, only count the stop-outs until 12:00. Book profit before 12:00.
   - Quote [00:08:32]: «एक्सपायरी के दिन अगर आप 11 11:30 के बाद कुछ भी करते हो तो नालायकी और कुछ भी नहीं है»  (entering after 11-11:30 on expiry day is foolish).
5. Seller expectation and the student backtest.
   - Quote [00:08:06]: «मैक्सिमम लॉस 40 पॉइंट का हुआ था और शायद दो-तीन बार हुआ है। बाकी बार प्रॉफिट दिया है। लेकिन उन्होंने क्या कहा कि 3:30 तक मैंने रख लिया था»
   - EN: A student's 1-year backtest: max loss 40 points, only 2-3 times, rest profit, but he held to 3:30. NK says count only to 12:00.
   - Quote [00:16:41]: «आठ एक्सपायरी होती है महीने में आठ में दो बार भी अगर आप लॉस देते हो ... बाकी टाइम आपको प्रॉफिट दे सकते हैं»  (about 2 of 8 expiries lose).
   - Late stop = small stop: quote [00:16:57] «जितनी लेट से स्टॉप लॉस होगी स्टॉप लॉस उतना ही छोटा होगा»  (the later the stop hits, the smaller the loss, as time decay eats the far leg).
6. Buyer variant: buy both OTM legs when combined premium is under 50, 50 points either side.
   - Quote [00:18:14]: «50 पॉइंट का दायरा चाहिए ... 50 पॉइंट ऊपर 50 पॉइंट नीचे कि कॉल और पुट को हम बाइंग करेंगे कब? जब वो 40 से 50 के ज़ोन में होंगे»
   - EN: Buy the call about 50 points above and the put about 50 below spot, when the combined premium ("sum") is in the 40-50 zone; try to get near 40.
   - Example [00:19:04]: «25600 की पुट और 25750 की कॉल और इन दोनों का वेट करेंगे कि सम 50 से नीचे आ जाए» (wait for the sum to fall under 50; at the time 38 + 22 = 60).
   - Quote [00:20:11]: «स्टॉप लॉस रखते हैं 20 के नीचे» — stop when the sum drops below 20 (risk about 30 points if bought at 50, 20-22 if bought near 40). Quote [00:20:26]: «सिस्टम में ही नहीं रख सकते हैं। आपको माइंड में रखना होगा» (cannot be an order in the system, a mental stop on the sum).
   - Timing: quote [00:24:25] «बयर को 40 के पास आने दीजिए। 45 आने दीजिए आराम से 50 के नीचे आया तो ऐसा नहीं कि जंप लगा दिए»; quote [00:24:52] «12:00 बजे के बाद भी अगर आ जाता है तो वैलिड हो जाता है» (a sum of about 110 combined... see item 7: entry is also valid after 12:00).
   - Quote [00:27:03]: stop is time-based, not price-based: «उसकी स्टॉप लॉस टाइम आधारित हो जाएगी। प्राइस आधारित नहीं होगी»; and [00:26:22] «ये 20 के नीचे आने के लिए इसको 2 बजने होंगे» (sum should not reach 20 before about 14:00).
7. Premium-decay regime filter (what the sum is telling you).
   - Quote [00:24:39]: «अगर ये प्रीमियम 110 के आसपास आती है ... प्रीमियम गल नहीं रहा है तो बाजार में कहीं ना कहीं मोमेंटम होने की संभावना है लेकिन प्रीमियम तेजी से गल रहा है तो ये इंडिकेट करता है कि बाजार कहीं ना कहीं रेंज बाउंड कर दे»
   - EN: If premium is not decaying (sum around 110) expect momentum; if it decays fast expect a range day.
8. Index and stop-rate comparison.
   - Quote [00:21:09]: «बयर के यहां पे स्टॉप लॉस जाने की रफ्तार ज्यादा हो सकती है। तीन हो सकती है, चार हो सकती है। 50% के आसपास भी हो सकती है»  (buyer stop-out rate 3-4 of 8, maybe 50%).
   - Quote [00:21:23]: «निफ्टी में स्टॉप लॉस चार में से आपके दो जा सकते हैं। ससेक्स में चार में आपके एक जा सकते हैं»  (Nifty: 2 of 4 stop; Sensex: 1 of 4; Sensex 100-pt moves are faster).
   - Bank Nifty skipped: only one expiry [00:27:30].
9. Hedger variant (still R&D by his words).
   - Quote [00:22:50]: «750 क्वांटिटी है तो सेलिंग यहां पर रहती है ना इससे कम से कम 300 क्वांटिटी ज्यादा मतलब 1050 क्वांटिटी ... ये क्या करता है ब्लॉक करता है वाइल्ड मूव में»
   - EN: Short 750 qty (25,600 put / 25,800 call), buy at least 300 qty more than the short quantity (1050+) as the wild-move block. "R&D going on" [00:23:07].
10. What not to do.
   - Quote [00:09:11]-[00:09:44] fat-finger example: bought wrong strike 25,900, exited in 23 seconds; no setup content.
   - Quote [00:26:09]: «अगर आप सिस्टम में स्टॉप लॉस नहीं लगाओगे तो आपने कमाए हो 10 दिन एक दिन में मार्केट बत्ती गुड कर सकती है»  (no stop in the system = one day wipes out ten days).
   - Quote [00:14:10]: «मैं जो भी चीजें यहां बताता हूं मैं पहले बैक टेस्ट करता हूं»  and [00:25:03] «बैक टेस्ट के बाद ही कोई ट्रेड करनी है»  (backtest before trading; he says he may be "100 out of 100 times wrong").

---

## fZvp72BBmRI - "Price Action & SL Hunting Demand Zone" (2025-07-23, Nifty, price-action lesson)
Six bullish price-action patterns where stops are hunted (PDF "6 bullish price action patterns"). Only the HM clarifications here are indicator rules.

HM and indicator clarifications:
- HM used as confirmation on a smaller timeframe: quote [00:02:12] «20 एसएमए के आसपास तो गैप अप लेने की संभावना होती है। खास करके वहां पे हम लोग हिलेमगा मिलेगा छोटे टाइम फ्रेम को चेक कर लेते हैं कंफर्मेशन के लिए»  (near the 20 SMA gap-up odds rise; we check HM on a smaller timeframe for confirmation).
- Daily trend gate (strongest HM definition in this batch): quote [00:04:31] «जब तक ये 20 एसएमए से ऊपर नहीं आ जाए डे टाइम फ्रेम पे या हिलेगा मिलेगा पूरी तरह बाइंग में ना आ जाए पूरी तरह बाइंग का मतलब आप समझते हैं ना कि इस तरफ से रेड लाइन अंदर चली जाए। बढ़िया से पूरी तरह बाइंग में आ जाए। आरएसआई हमारा 50 के ऊपर आ जाए। नॉर्मल 14 आरएसआई तब हम इसको 20 एसएमए को भी कुछ हद तक अवॉइड कर सकते हैं»
  - EN: Until daily price is above the 20 SMA, or HM is fully in buying (the red line has gone fully "inside", i.e. below), plus the normal RSI 14 above 50, we stay cautious; with those two we can partly ignore the 20 SMA.
  - Parameters stated: RSI = normal 14 (not HM's own RSI), threshold 50, daily timeframe, 20 SMA. Formula still not given.
- Monthly HM: quote [00:07:30] «यह मंथली पे बाइंग में नहीं है। यह मंथली में जाकर रेजिस्टेंस फेस करवाया है। और जब भी रेड लाइन इसे रेजिस्टेंस फेस करवाती है तो ... वो आपको परेशानी उत्पन्न करता है बुल के लिए»  (monthly HM is not in buying; the red line acting as resistance is trouble for bulls).
- Hourly use: gap-up above the 1h 20 SMA with strong close = more gap-ups likely [00:01:57]; trade-guide: «आज का हाई को एसएल मान के ... ट्रेडिंग डिसीजन पुट साइड में होगी» [00:02:39] (short with today's high as stop if price breaks below VWAP / today's low on 10-minute candles) but «गैप अप हुआ है तो ... उसको स्ट्रांग माना जाता है ... सचेत रहेंगे ... एसएल हंटिंग करवाई जा सकती है» [00:03:06] (a gap up from support is strong; be careful shorting, stops get hunted). Preferred action: wait one hour, no decision in the morning [00:03:20].
- Long trigger: quote [00:03:48] «अगर आज 1 ऑवर के टाइम फ्रेम पे वीवाप के ऊपर ट्रेड करने लगता है तो लो हमारा एसएल होगा और लो के एसएल के साथ हम लॉन्ग की तरफ»  (if price trades above VWAP on 1h, long with the day's low as stop).
- Levels with closes: «25167 के ऊपर आवरली टाइम फ्रेम पे» closing above gives next resistance 25255, 25539 [00:03:34]. Weekly close above 25800 needed before believing a move up [00:06:25]. Weekly support 24665; no further downside until a weekly close below it [00:08:19].
- Until price reclaims the previous high or 1h VWAP: quote [00:09:04] «जब तक इस हाई के ऊपर नहीं जाता है या वीबप के ऊपर वन आवर नहीं जाता है। इन दोनों केस में हम कोई बाइंग का ट्रेड लेंगे तो हमें नुकसान का सामना करना पड़ सकता है»  (no long until above the high or above the 1h VWAP).

The six patterns (entry, stop, target, what not to do):
1. Gap-filled pullback [00:10:53]-[00:12:59]. Price breaks out, ranges, big candle, then gap down through the first support. Mark the second demand zone (low and high of the red candle). Quote «पहला के पास इस प्रकार कोई गैप डाउन करे तो आपको सतर्क रहना है। दूसरे ज़ोन को मार्क कर लेना है डिमांड ज़ोन को ... यहां अगर कोई भी प्राइस एक्शन आपको दिखे या हिलेगा मिलेगा बाइंग में दिखे तो हम एक्शन बाइंग साइड में लेते हैं। इस लो का एसएल मान के» (when a gap down hits the first support, mark the second demand zone; buy there on any price action or HM buying, stop = the low of that zone; target = above the breakout high).
2. Double-bottom pullback [00:13:10]. Slow grind down (no gap), W in the demand zone: quote «डबल बॉटम में बाइंग करते हैं। हमारा एसएल इसके नीचे होता है या हम डब्ल्यू के ऊपर बाइंग करते हैं लेकिन एसएल फिर हमारा इसके नीचे होगा क्योंकि एसएल काफी बड़ा हम नहीं ले सकते हैं» (buy the double bottom or on a break above the W; stop below the W). Target: first target = the old high, run "five to six times the area" [00:13:55].
3. Break-block retest [00:14:47]. Price breaks a level, retests it with one candle, ranges 10-12 days, then sharp drop to the old zone, single candle, rip. Take the retest of the second zone.
4. Aggressive pullback [00:16:11]. V-shape on news, no gap down, quick recovery; in it you do not stay long.
5. Normal pullback [00:17:18]. Slow drop, stops at each support, retests the primary demand zone then up; stop below it.
6. Liquidity grab [00:17:45]. Stop below the obvious support gets run, then the second demand zone is the real reversal.
- Core rule: the stop belongs at the SECOND zone, not the first. Quote [00:14:21] «रेंज के नीचे एसएल लगा देते हैं। बट ऐसा करना गलत है। आपको दूसरा जो रेंज है वहां एसएल होनी चाहिए। क्योंकि लिक्विडिटी जो होती है प्राइमरी रेंज में सबसे ज्यादा होती है»
  - Entry rule [00:18:31]: «हम सपोर्ट पे एंट्री नहीं लेंगे ... आप ब्रेकआउट लो। यहां से ब्रेकआउट ले। इस ज़ोन के ऊपर निकलोगे। फिर से ले लेंगे। अन्यथा इसको आप ब्रेक करके दूसरे डिमांड ज़ोन में जाओ तब ले»
  - NOT to do: quote [00:18:43] «इस ज़ोन में नहीं खरीदारी करनी चाहिए। ट्रैपिंग की संभावना सबसे ज्यादा होती है प्राइमरी लिक्विडिटी ज़ोन में» (do not buy in the primary liquidity zone, highest trap odds).
- He prefers cash/MTF to option buying: quote [00:19:51] «आप कैश ट्रेडिंग करो। कैश में एमटीएफ के द्वारा ट्रेडिंग कर लो। वो ज्यादा बेहतर रिजल्ट आपको देगा»

---

## a8RP5ftOfGo - "Nifty Ready For Big Move or Massive Crash" (2026-04-10, Nifty + crude)
Rules (swing/investing level, Nifty, after the Iran-US news dip):
1. Swing direction by HM on weekly and daily: quote [00:08:30] «बाजार अभी बाइंग में है। सेलिंग में नहीं है। यह बात आपको ध्यान रखना है। कि हिलेगा मिलेगा बाइंग में है»  (market in buying, not selling; HM is buying). Quote [00:11:23] «स्विंग में हमारा सेल नहीं है। स्विंग बाइंग में है।»
2. 20 SMA daily as the bull/bear line, two closes for bear:
   - Quote [00:08:44] «अगर बाजार को नीचे गिरना है और आपको बियर व्यू लेना भी है तो इस 20 एसएमए के नीचे जिस दिन क्लोज कर जाए दो क्लोज तो हमें मान के चलेंगे बाजार में बियर आ रहा है। लेकिन जब तक इस 20 एसएमए से ऊपर है बाजार में हमें बुल देखना चाहिए। जब भी कोई गिरावट हो तो वहां पे बाइंग का अप्रोच होना चाहिए ना कि सेलिंग का»
   - EN: Two daily closes below the 20 SMA = bear; above it, buy dips, not sell.
3. 200 DMA/200-hour average:
   - Quote [00:13:14] «जब भी 200 डीएमए के ऊपर आवरली टाइम फ्रेम पे मार्केट क्लोज करती है ये निफ़ी या बैंक निफ्टी या ससेक्स तो वो वो स्विंग में बाइंग हो जाता है और तब तक सेल में नहीं होता है जब तक दोबारा से 200 डीएमए के नीचे नहीं आए»
   - EN: A close above the 200-period average on the 1h chart makes swing = buy until it closes below again; market cannot go lower until a close below 23682 (the 200 on 1h at the time).
   - Daily 200 DMA reclaim must be validated by time below: quote [00:09:30] «शर्त है कि इसके नीचे आकर सस्टेन हो जाए प्राइस मतलब 10 दिन 12 दिन महीने दिन सस्टेन कर जाए उसके बाद ऊपर आए ऐसा नहीं हो कि गया नीचे और 2 दिन बाद ऊपर आ गया तो वो वैलिडेट नहीं होता है» (a reclaim only counts if price stayed below for 10-12 days to a month; 2 days is not valid).
4. Pivot/option filter: quote [00:13:51] «R3 के आसपास है और जब भी R3 के आसपास तीन दिनों तक इस तरह पोजीशन बनती है तो एक बड़ा मूव आता है अपसाइड में» (hold near R3 for three days = big up move; options above hourly R3 can go 40-50 to 200-250). R2 above leads to R3 [FzND 00:09:44].
5. Quarterly RSI bottom: quote [00:04:32] «48 49 जब आरएसआई आ जाती है तो मार्केट का कहीं-न-कहीं बॉटम होता है क्वार्टरली बेसिस पे»  (quarterly RSI 48-49 = a bottom); quarterly RSI 57-60 area is a "discount" zone [00:11:07].
6. Calendar/valuation notes: 17% drawdown zone appears every ~4.8 years [00:01:15]; yearly close above prior high for 7-8 years running [00:05:14]; discount window Feb-Mar each year, around March 15-20 [00:10:41]; crude above 70-75 caps the bull [00:06:16].
7. Crude: volume rule. Quote [00:15:02] «पहली बार ऐसा हुआ है क्रूड में कि उसकी वॉल्यूम सेल में गई है ... क्रूड में अब अपसाइड जाता है तो हम शॉर्ट देखेंगे बाइंग नहीं देखनी चाहिए» (first heavy selling volume with red candle in 7 weeks = at resistance sell, do not buy). Support 72-ish; close under 86-85 targets 72.
8. Short-covering expectation: quote [00:11:36] «24000 के ऊपर जब बाजार क्लोज की है तो एक शॉर्ट कवरिंग आनी चाहिए ... 3400 पॉइंट और ऊपर»  (an estimate, not a rule).
9. Not to do: do not rotate out of down stocks into other stocks [00:10:15]; do not chase after a sharp up move from FOMO, wait for support [00:03:05] «सपोर्ट का वेट करना है फ्रेश बाइंग के लिए».

---

## FzNDQm7wC_s - "Nifty Move After Iran-US News" (2026-05-06, Nifty daily plan)
1. Weekly HM: quote [00:03:12] «ये वीकली टाइम फ्रेम पे हिलेगा मिलेगा। रेड लाइन नीचे है। मैंने पहले भी कहा कि जब तक रेड लाइन नीचे है बाजार नीचे नहीं जाएगी»  (weekly HM, red line below; as long as it is below the market will not go down).
   - Quote [00:11:42] «जब तक ये रेड लाइन नीचे है वीकली में आपको भ्रम से बाहर रहना है। जिस दिन ये ऊपर आ जाएगा हम भी भ्रम में आ जाएंगे»  (as long as red is below on the weekly, do not fall for the bear stories; the day it crosses above, doubt returns).
   - Quote [00:11:30] «वीकली टाइम फ्रेम आपकी बाइंग में है तो कोई अंडरस्टिब प्राइस को नहीं करना है»  (weekly in buying: do not underestimate price).
2. Intraday trigger on the prior high: quote [00:03:24] «जैसे ही निकलेगी तो आज इंट्राडे में बाइंग में चली जाएगी 24,360 के ऊपर»  and [00:08:57] «आज के हाई के ऊपर अगर बाजार निकलती है तो वो बाइंग में चली जाएगी»  (above the prior high = buying; next resistance 24,520-24,621 zone). Pivot: «R2 के ऊपर प्राइस निकलती है तो R3 के आसपास जाने की कोशिश» [00:09:44]; hourly close above R2 (24601) means a stronger Friday.
3. Supports as zones: 24130-24150 and 23990-24000 are long supports; sell only if the lower support breaks [00:01:25]-[00:01:43]. Zones not lines: quote [00:04:44] «कोई भी सपोर्ट रेजिस्टेंस कोई लाइन नहीं होता है। लाइन अगर तुक्के से आया और गिर गया तो तुक्का था। एक जोन होता है»  (S/R is a zone, not a line; the zone width scales with the timeframe cycle).
4. Moving average type: quote [00:02:35] «200 डीएमए एसएमए का यूज़ करना है। ईएमए का नहीं डे टाइम फ्रेम पे सिंपल मूविंग एवरेज का»  (use the 200 DMA as SMA, not EMA, on daily).
5. Monthly close definition: last trading day of the month [00:02:48]. Monthly/weekly close above 24,800 breaks the pivot and targets 27,746 [00:10:49].
6. Probabilities he states (a view, not a rule): December close 27,000-27,500 about 60-70%, 25,200-26,000 about 20%, 22,000 about 10% [00:05:39].
7. Position-management rules: quote [00:07:23] «जो बढ़ रहा है उसको बेचना नहीं है और अगर बेचना ही है तो हम 50% क्वांटिटी बेचेंगे और 50 को राइड करेंगे»  (sell 50%, ride 50%); basket: 30-40% large cap, rest mid/small, speculative sleeve 10-20% (30% max aggressive) [00:08:05]-[00:08:20]. "Volume is real; price action can be faked" [00:12:32].
8. For stocks: quote [00:11:56] «स्टॉक के ट्रेडर हो तो ... वीकली टाइम फ्रेम, डे टाइम फ्रेम या मंथली ... हिलेगा मिलेगा कि हेल्प जरूर लेना है»  (stock traders: use HM on weekly/daily/monthly).

---

## ysq6x0eCFvI - "Market Crash! Recovery Kab Hogi?" (2025-02-21, Nifty reversal conditions)
Explicit reversal-confirmation checklist (any one suffices for an index):
- Quote [00:03:12]: «जब भी प्राइस अपने डे टाइम फ्रेम पे 200 डीएमए के ऊपर वीकली बेसिस पे जाकर क्लोज कर जाए ... रिवर्सल हो चुकी है»  (1: a weekly close above the 200 DMA (daily-chart 200).)
- Quote [00:03:27]: «आर एसआई डे टाइम फ्रेम का 50 से [ऊपर] आ जाए और वन वीक सस्टेन कर जाए ... मैं सारे आर एसआई 14 की बात कर रहा हूं»  (2: daily RSI 14 back above 50 and holds one week. "Above" is garbled in the caption.)
- Quote [00:04:26]: «हिलेगा मिलेगा वीकली बेसिस पे बाइंग में आ जाए और 20 एएमए के ऊपर वीकली प्राइस क्लोज कर जाए»  (3: weekly HM in buying AND a weekly close above the 20 SMA.)
- Quote [00:04:41]: «ऑन बैलेंस वॉल्यूम डे टाइम फ्रेम पे जीरो लाइन के ऊपर सस्टेन कर जाए»  (4: daily OBV above its zero line and sustains.)
- Weekly trend-change candle [00:07:17]-[00:08:15]: a big weekly candle that closes above the previous 3-4 weeks' closes (or a weekly close below the last 3-4 week low plus below the weekly 20 SMA = bear). «नियम सिर्फ इंडेक्सेस में नहीं है ये नियम हर जगह लागू है».
- Averaging a stock: quote [00:05:13] «एवरेज करना तो ... 200 डीएमए के जब ऊपर आए तो वो बेहतर एवरेज होता है या कोई प्रीवियस मेजर सपोर्ट के पास»  (only average at a major support or above the 200 DMA).
- News sequence: quote [00:06:21] «जब बियर मार्केट होगा तो बैड न्यूज भी लगातार आएंगे ... सीक्वेंस ज्यादा चलने लगा बैड न्यूज का इसका मतलब है कि अब कहीं ना कहीं ये खत्म होने वाला है»  (a long run of bad news means the end is near).

---

## IjU9PpqvrI8 - "Stock Market Crashed | Opportunity or wait?" (2025-03-05, Nifty drawdown zones)
- Drawdown ladder: quote [00:03:39] «फिलहाल हमारी जो बाजार है वह 17 पर के जोन पे आ चुकी है 17 पर का जोन आपका 21800 900 का जोन बनता है»  and «38 पर का जोन आपका स्वागत कर रहा है»  (market at the 17% zone, ~21,800-21,900; a break goes toward the 38% zone; more than ~20% is recession).
- Entry zones: quote [00:04:15] «प्राइमरी ... जहा हम 30 40 पर के आसपास का एंट्री बनाते हैं क्योंकि 17 पर का जोन है फिर 38 प आता है तो वहां फिर हम एंट्री बनाते हैं»  (scale in at the 17% zone and again at the 38% zone; "30 40" is a caption mangling, probably 30-40% of the position).
- Portfolio only: fundamentally sound stocks will recover; don't panic [00:04:33]. No HM/RSI settings.

---

## 6zDpjsesOyw - "How to Avg Portfolio / Evergreen Sector / US vs Iran" (2026-03-22, Nifty monthly/daily/hourly, hedging)
HM and MA rules:
- Monthly HM reversal gate: quote [00:07:42] «मंथली हिलेगा मिलेगा का एक नियम है। ये ध्यान रखिएगा कि बाजार तब तक ऊपर नहीं जाएगी तब तक रिवर्सल नहीं माना जाएगा जब तक ये जो ग्रीन लाइन यहां पे आप देख रहे हो ये इस प्रकार से आरएसआई में जाकर टच ना कर जाए। अगर ये नहीं करता है मंथली टाइम फ्रेम पे तो रिवर्सल नहीं माना जाएगा»
  - EN: Monthly HM rule: no reversal until the green line (touches / meets the RSI line) — the red line is the one in the "RSI" pane. Caption wording is unclear; it reads as the green line must come and touch the RSI (the line that is its other partner). He says monthly HM was in sell with a double-top. Needed for any reversal call. This is the best hint that HM has two lines: green (fast, an RSI-derived line) and red (slow), plus a separate RSI plot.
- 20/50 SMA small golden cross on daily = reversal hint, not full confirmation [00:08:29]; full confirmation needs 50 above 200 (golden cross) [00:12:44].
- 200 DMA as the swing stop: quote [00:16:42] «200 पे आया सपोर्ट लिया मोस्टली 50 लेता है लेकिन 200 मेजर सपोर्ट होता है ईली ब्रेक नहीं करता तो एक बार क्रॉसओवर हो गया तो दोबारा 200 हमारा स्टॉप लॉस हो जाता है»  (after a golden cross the 200 becomes the stop).
- Hourly 200 as the "cover shorts" signal: quote [00:18:38] «आवरली के 200 डीएमए के ऊपर भी अगर बाजार आ जाती है तो उसको एक रिवर्सल का छोटा साइन मान लेना है शॉर्ट्स को बाय-बैक कर देना है»  (price above the 1h 200 = cover shorts, never keep shorting above it).
- Short-timeframe HM use: quote [00:19:43] «22940 अगर ब्रेक करता है तो बाजार सेल में चली जाएगी और ऊपर आता है तो एक रेजिस्टेंस फेस करेगा 23400 के आसपास ... अगर छोटे टाइम फ्रेम पे 15-20 मिनट पे सेल दिखती है हिलेगा मिलेगा सेल में आता है तो हम उसका यूज़ किया जा सकता है»  (level 22,940 break = sell; near 23,400 resistance sell only if the 15-20 minute HM shows sell). Also [00:19:57] «50 और 200 अगर रख लेते हैं छोटे टाइम फ्रेम पे» (keeping 50 and 200 averages on the small timeframe).
- BTST/STBT rule (overnight): quote [00:33:36] «बीटीएसटी करते हैं। एसटीबीटी करते हैं। हिलेगा मिलेगा लास्ट का 5 10 15 मिनट का देख लो। बस लास्ट का उसी पे करना है। नहीं है तो नहीं करेंगे। है तो करेंगे»  (for buy-today-sell-tomorrow or the reverse, read HM on the last 5, 10, 15 minute chart at the close; if it agrees take it, otherwise skip).
- Overheated bull: quote [00:27:08] «जब बाजार बुल साइकिल में हो 86 के ऊपर आरएसआई हो तो वहां पे हमें कम से कम पोर्टफोलियो को हेज कर लेना चाहिए»  (the "86" is likely a caption error for a Hilega-Milega RSI/monthly RSI reading; companion line in MLrM below says «हिलेगा मिलेगा आरएसआई 86 के ऊपर»). Treat as "HM RSI above ~86 = hedge" but unverified.
- Stops: long-term option stop is small («202 पॉइंट का ही वहां स्टॉप लॉस» [00:13:57], figure garbled, about 200 points on Nifty). Hedging is insurance, not profit [00:30:50]; do not carry unhedged overnight on war news [00:31:48].

---

## jmwo9IaRr-0 - "Portfolio ko kaise hedge karen... Nifty View IRAN vs US" (2026-04-03)
- Trend-change trigger after a low break: quote [00:04:54] «हमें चाहिए क्या कि ये 20 एसएमए से अगर ऊपर बाजार आ जाती है या ये 10 वीए में से ऊपर बाजार आ जाती है तब माना जाएगा कि ट्रेंड चेंज हो गया»  (need price above the 20 SMA (or the garbled "10 ..." average) before calling a trend change; a bounce that does not sustain 2-3 days fails).
- Real reversal: quote [00:05:44] «मार्केट का मूल रिवर्सल तभी आएगा प्राइस का जब मार्केट 200 डीएमए और 50 डीएमए के क्रॉसओवर के ऊपर आकर गोल्डन क्रॉसओवर बना लेगी»  and [00:06:19] until a daily golden cross, the upside meets resistance at the 200/50: «छोटा टाइम फ्रेम पे सेल दिखता है तो वहां पोर्टफोलियो को हैज कर देंगे».
- Bear-market playbook: quote [00:08:02] «लॉन्ग अभी करना नहीं चाहिए ... शॉर्ट के लिए हमें हमेशा रेजिस्टेंस ढूंढना है»  and [00:08:48] «वॉल्यूम के बेस पर ही हम कुछ डिसीजन ले और हिलेगा मिलेगा उसमें सपोर्ट कर दे या कोई पैटर्न बन जाए तो लेकिन उसमें भी क्वांटिटी कम होनी चाहिए ... स्टॉप लॉस छोटे होने चाहिए»  (below the 200 DMA: no swing longs; shorts only at resistance, with volume plus HM agreeing or a pattern, reduced size, tight stops).
- Put-hedge exit rule: quote [00:20:09] «हम इतना जानते हैं कि 200 डीएमए के ऊपर मेरा, 200 डीएमए के नीचे तेरा»  (above the 200 DMA mine (bulls), below yours); stay in the put until Nifty breaks the 200 DMA upward [00:19:53]; book hedge profit then and use it to average stocks [00:18:57].
- Do not average a portfolio until Nifty is above the 200 DMA [00:09:00].

---

## 4-OtV5JVM4g - "Trading Psychology: Fear, Greed & Discipline" (2026-09-12)
Mostly psychology; one concrete pattern call:
- XABCD-style reversal on Nifty [00:03:55]-[00:07:14]: entry only after confirmation (bullish engulfing or high-volume breakout at the D level). Quote «डी से जब ऊपर जाता है प्राइस तो उसमें कंफर्मेशन होनी होती है पैटर्न की और वॉल्यूम की ... तभी हमारी एंट्री होनी चाहिए और डी के नीचे हमारा स्टॉप लॉस उस केस में होता है या मेन स्टॉप लॉस x के नीचे होता है। और वहां से जो टारगेट होता है पुराने जो सी है इसके ऊपर निकल जाता है»  (entry on confirmation at D; stop below D, or main stop below X; target = beyond the old C.) Invalid on two closes below X (23,000; 23,650 minus a 50 point buffer) [00:04:28].
- RSI + HM: quote [00:07:00] «ओवरसोल्ड कंडीशन का मतलब यह नहीं होता है कि हम बाइंग कर लें ... इस आरएसआई को हमें इसके कम से कम 30 के ऊपर आने का वेट करना चाहिए। अगर ये 30 के ऊपर आ जाता है तो यह कंफर्मेशन भी माना जाएगा कि 30 के ऊपर और हिलेगा मिलेगा वहां आपको बता ही देगा। तो अगर यहां इस केस में हिलेगा मिलेगा डे टाइम फ्रेम बाइंग में आ जाती है तो आपको रिवर्सल ये मानना चाहिए»
  - EN: Oversold is not a buy; wait for RSI to come back above 30 and for daily HM to turn to buying; then the reversal counts (target above 24,800, stalls at each Fibonacci level).
- NOT to do / sizing: bigger capital means the same percentage stop feels bigger and gets hunted [00:13:12]-[00:16:44] («स्टॉप लॉस ... नॉर्मल स्टॉप लॉस से आठ से 10 गुना»); put a stop only if it is part of a predefined risk. Focus on one thing.

---

## MLrMJ7rlL4U - "SPLIT Basket - Can Change Your Mindset" (2026-09-26, position sizing)
- Sizing rule: quote [00:07:55] «एक अच्छा स्टॉप लॉस जो होता है 2% के आसपास का होता है। 2% से ज्यादा का अगर आप स्टॉप लॉस लेते हैं तो कहीं ना कहीं आपके फेवर में वो नहीं होगा»  (a good stop is about 2%; more than that is against you long-term). Position = 2% risk plus 50% = 3% of capital per trade [00:09:10]; capital under 5 lakh: 5%; 5-15 lakh: 3%; above 15 lakh reduce [00:20:58]-[00:21:14]; "should not exceed 10%".
- Averaging conditions (the clearest HM mention): quote [00:16:12] «एवरेज करेंगे लेकिन एवरेज जब भी करेंगे वहां पे हम टेक्निकल देखेंगे। जब वो स्टॉक बाइंग में होगा तभी एवरेज करेंगे। 50% करेक्शन पे नहीं करेंगे। मतलब हिलेगा मिलेगा बाइंग हो या जो आपको टेक्निकल आता हो तभी करेंगे ... और अगर वह स्टॉक 200 डीएमए के नीचे है तो भी एवरेज नहीं करेंगे। हम वेट करेंगे कि 200 डीएमए के ऊपर आए»
  - EN: Average only if the stock is in HM buying, not merely after a 50% correction; do not average below the 200 DMA.
- Overbought block: quote [00:16:28] «साथ ही साथ अगर हिलेगा मिलेगा आरएसआई 86 के ऊपर हो अगर एसआरटी 1.24 के ऊपर हो वीकली या डेली एसआरटी 1.3 के ऊपर हो या नॉर्मल मंथली आरएसआई 81 के ऊपर हो निफ्टी की बात है ... तो भी हम इनको रुकेंगे»  (do not add if HM RSI above 86, or the weekly "SRT" above 1.24 (daily above 1.3), or normal monthly RSI above 81 for Nifty; cut the trade size from 6% to 3% in such markets [00:17:07]; use an ITM 1-year Nifty put as hedge [00:17:25]). "SRT" is unidentified (caption of an indicator, maybe a ratio like Nifty/200 DMA).

---

## UCGH6r1FOXw - "How to Register on NK StockTalk Research Website" (2025-11-25)
No trading content. Skipped (site sign-up steps).

---

# Top 10 most specific rules (for the return value)
1. ovQp5 (expiry day short straddle/strangle): enter 9:35-9:40 after price settles, short near-OTM/ATM call+put, stop on EACH leg at combined premium +5 to +10 (e.g. 110 -> 115/120), exit the survivor when one stops, no new risk after 12:00.
2. ovQp5 (expiry buyer): buy call about 50 pts above and put about 50 pts below spot when the combined premium is 40-50 (try near 40), mental stop when the sum is under 20, time-based exit, valid after 12:00 too, premium not decaying near 110 means momentum.
3. fZvp7 (Hilega Milega daily gate): "red line goes inside" (below) = fully buying AND normal RSI 14 above 50 on the daily, then the 20 SMA can be partly ignored; else stay out of longs.
4. ysq6x (reversal checklist, any one): weekly close above 200 DMA; daily RSI 14 above 50 for a week; weekly HM buying AND weekly close above 20 SMA; daily OBV above zero.
5. 6zDpj (BTST/STBT): read HM on the last 5, 10, 15 minute chart at the close; take the overnight trade only if it agrees.
6. 6zDpj (monthly HM): no reversal call until the monthly HM green line touches the RSI line (caption unclear), plus daily golden cross 50>200 for full confirmation.
7. a8RP5/FzND (weekly HM): weekly red line below = market will not go down, buy dips; two daily closes below 20 SMA to turn bearish; 1h close above 200-SMA means swing = buy.
8. 4-OtV5 (reversal entry): RSI must come back above 30 and daily HM must turn to buying before calling a reversal; entry on confirmation (bullish engulfing / high-volume break), stop below D or X.
9. fZvp7 (SL hunting): stop goes under the SECOND demand zone (the V-bottom), never the first range; do not buy in the primary liquidity zone; buy on a breakout above the zone or after the break into the second zone.
10. MLrMJ (averaging/overheat filters): average only in HM buying and above the 200 DMA; stand down when HM RSI above 86 (or weekly SRT above 1.24, daily SRT above 1.3, monthly RSI above 81 for Nifty); size 2% stop, 3% of capital per trade (5% under 5 lakh).

Gaps remaining for our tests: HM RSI length and averages are still not stated (only "normal RSI 14" next to it and the unexplained "86" threshold); the "86" and "SRT" figures are caption-ambiguous and need a clean re-listen or a Gemini pass.
