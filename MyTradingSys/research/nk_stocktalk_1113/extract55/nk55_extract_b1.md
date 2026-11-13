# NK StockTalk batch 1 extract (10 videos + 1 trivial)

Source: F:\MTS\data_cache\youtube\nk\*_timed.txt. Batch 1 = every 5th non-interview file from index 1 (11 files). Quotes are verbatim from the Hindi captions (captions are garbled in places; timestamps are caption times). English is my translation. NK says repeatedly this is "education, not advice" and "100% sure only after backtest"; he states no numbers for most things. Items marked [PARAM] fill a gap our tests guessed.

Files covered: 3KnEiKNh1pc, 5GZIshXnxW8, B7iGQef_z6I, I4rHEfRhEWM, J_BzeTB3PpA, RZzKYqTra3Y, Xz61miXrOcY, dm7x3ZY9K9M, i2bGV_Wo5Yw, lmhqooBqJWU, t1b_1h2QMXw.
Not rule-bearing (skim + keyword scan only): I4rHEfRhEWM (career roadmap), Xz61miXrOcY (skill vs conviction), RZzKYqTra3Y (22 s Patna class clip). B7iG is mostly a PGP/career Q&A with a short market view and the master-candle rule.

Global HM facts gathered in this batch (answers to "key parameters guessed"):
- HM is read as TWO lines: an RSI line and a RED line (red = smoothing of it, he never gives lengths). Quote i2bG 00:03:39: «जब ये आरएसआई और रेड लाइन जब टच करेगी» (when this RSI and the red line touch). HM "crossover" on the monthly chart = trend change on monthly (i2bG 00:03:20).
- Buy state = red line is BELOW/inside, sell state = red line above. 50 is the dividing level: B7iG 00:03:17 "not buying does not mean selling; to be in sell it must go below 50".
- No RSI length, no MA type, no formula stated in any of these 11 videos. He promises a dedicated 30-40 min HM video (J_Bz 00:14:09 «हिलेगा मिलेगा पे हम लोग एक वीडियो ला रहे हैं... 30-40 मिनट का वीडियो होगा»). That video is the place to get the formula: look for it in the other 44 NK files.
- HM is used as a FILTER/direction, never an entry trigger: entry comes from levels (prev-day low/high, VWAP, day-close SL).
- Timeframes used for HM: 1h for intraday option entries (3KnE), 5/10/15 min at the close to predict next-day gap (lmhq), daily/weekly/monthly for swing/positional (J_Bz, i2bG, 5GZ).

---------------------------------------------------------------
## 3KnEiKNh1pc  Intraday Masterclass: Option Buying, Selling, Cash, Crypto & Commodity (2025-08-13, 2065 s)
This is the most specific rule set in the batch. NK says it also works on cash, commodity, gold, silver, crypto (00:32:44).

R1. Stock selection scanner: stock up (long) or down (short) by 1% or 2% in the first hour.
- Q: «ऐसे स्टॉक की तलाश करनी है जो इंट्राडे में मॉर्निंग में फर्स्ट वन आवर में 2% या उससे ज्यादा बढ़े हुए हो। सम टाइम हम 1% भी देखते हैं» [00:09:11]
- EN: Look for stocks that are up 2% or more in the first hour; sometimes 1%. Build two scanners (1% and 2%) and mirror for the downside (-1%, -2%).
- Q: «एक 1% का भी एक बना लीजिएगा। एक 2% का भी ... या बना लीजिएगा डाउन साइड में वाइसवरसा» [00:09:32]

R2. Trap/reclaim rule (the core "TRAPPING" condition), long side. Mirror for short.
- Q: «फर्स्ट 5 टू 10 मिनट में कल की जो क्लोजिंग प्राइस थी उसके नीचे प्राइस चला गया हो और उस क्लोजिंग प्राइस के नीचे जाकर फिर से दोबारा उसके ऊपर आ चुका हो बाइंग के केस में» [00:07:11-00:07:37]
- EN: In the first 5-10 minutes price must dip below yesterday's close and come back above it (long). He checks it on the 2-minute chart (00:18:56: «2 मिनट के टाइम फ्रेम पे... इस क्लोजिंग प्राइस को इसने ब्रेक कर दिया है... ये ब्रेक करना आवश्यक है»).
- Q: the dip must also take out yesterday's LAST-30-MIN low: «कल के लोएस्ट पॉइंट पे जितने भी लास्ट 30 मिनट में एवरेजिंग हुई थी प्राइस की उसकी लो को ब्रेक कर दिया गया है» [00:07:37] and «इंट्राडे में बस 30 मिनट का लो और हाई में इंट्राडे का हाई» [00:28:55]. EN: "low" = low of yesterday's last 30 minutes; "high" = yesterday's full-day high.

R3. 1h confirmation: first-hour (or 90-minute) candle must CLOSE above yesterday's high.
- Q: «कल के हाई के ऊपर वन आवर की कैंडल क्लोज करो» [00:19:26]; «फर्स्ट 60 मिनट में या 90 मिनट में» [00:08:48]; «आज फर्स्ट वन आवर में ही क्लोज कर जाए» [00:08:01]
- EN: Wait for the 1h close above prior day high; do not rush: «जल्दी का काम शैतान का होता है... आपके पास वन आवर है» [00:15:04].

R4. Reject if the first-hour candle is too big.
- Q: «पहली वन आवर की जो कैंडल है वह काफी बड़ी नहीं होनी चाहिए... अगर ऐसा है तो आपको वैसे स्टॉक को अवॉइड कर देनी है» [00:11:49-00:12:01]
- EN: Skip stocks whose first-hour candle is huge (example 4-5% single candle, 6% LKM Lab day is "almost our work is done", 00:14:35, 00:28:20). The setup works when the first-hour candle is about the size of neighbouring candles (00:28:10).
- Counter-example SGBN: broke yesterday's high but did NOT break yesterday's last-30-min low and had a huge candle: «एक लो ब्रेक नहीं हुआ और छोटी कैंडल नहीं» [00:28:01] -> not tradable. «एव्री ब्रेकआउट ट्रेडेबल नहीं है» [00:27:19]. [PARAM: no numeric cap on candle size given; only "similar to nearby candles".]

R5. ENTRY: pullback to VWAP on the next candle.
- Q: «अगली कैंडल पर वीवप के पास जब प्राइस वीवप के पास आएगी तो वहां पे हमारी एंट्री बनेगी» [00:10:01]; example «10:15 के बाद यह 10 मिनट की कैंडल... 4926 27 पे 10 बजके 25 पे आया» [00:20:05-00:20:17]
- EN: After the 1h confirmation, drop to a small timeframe (he uses the 10-minute chart in the example) and buy when price comes back to VWAP. (Spot or futures VWAP, then buy the option.)

R6. STOP: day low, on SPOT/FUTURES not on the option.
- Q: «हमारा जो एसएल होगा उस दिन का लो के नीचे होगा लेकिन वो एसएल स्पॉट वाइज होगा या फ्यूचर वाइज होगा। ऑप्शन वाइज नहीं होगा» [00:10:01-00:10:16]
- Q: «नेकेड में उस दिन के डे लो का एसएल मानेंगे» [00:10:39]. Example: low 498 -> SL 497 [00:14:05-00:14:13] (1 tick/point under the low).
- Reason: «कल के क्लोजिंग प्राइस को ब्रेक करके ऊपर आया था तो वो काफी अच्छा एसएल का काम करता है» [00:10:48].

R7. VWAP as a stop only on the 1-HOUR close, never 10/15 min.
- Q: «वीवप को आप वन आवर का यूज़ कीजिए कि 1 आवर के नीचे आके क्लोज करो तब मानेंगे। हम 10 मिनट 15 मिनट पे नहीं मानेंगे» [00:25:40-00:25:50]. Reason: option premium decay makes the option close below VWAP when spot has not.

R8. Strike selection (option buying).
- Q: «वो नियर ओटीएम हो... डेल्टा 0.3 0.4» [00:05:14]; «स्टॉक 5000 की चल रही है तो 5100 5200... 500 की चल रही है तो 520... बहुत अच्छा मोमेंटम है तो 530... उससे आगे नहीं» [00:06:01-00:06:10]; ATM/ITM only in expiry week: «लास्ट वीक है तो वहां पे एटीएम लेंगे या आईटीएम» [00:06:10]
- EN: Near-OTM, delta 0.3-0.4; roughly 4% OTM max (5000 -> 5200, 500 -> 520, 530 on strong momentum). In the last week to expiry use ATM/ITM. As expiry gets closer shift to nearer strikes (00:30:24). Choose the cheaper strike when the stop is small: option SL is "50% premium" in buying generally (00:21:13).

R9. Alignment filters.
- HM on the 1h chart in your favour (both long and short), and the option's own chart HM must also be in your favour. Q: «वन आवर पे हिलेगा मिलेगा आपके फेवर में जरूर होना चाहिए... एक एडिशनल कन्फर्मेशन है। इसको इग्नोर मत कीजिएगा» [00:18:14-00:18:24]; «5200 का कॉल ऑप्शन तो हिलेगा मिलेगा हमें सब में फेवर में चाहिए... अगर आपके फेवर में नहीं है तो आप मोह माया में है» [00:22:27-00:22:37]
- Index trend: Q: «निफ्टी भी बाइंग में जाने का मतलब 20 और 50 एसएमए से ऊपर ट्रेड कर रहा हो डे टाइम फ्रेम पे... उसके नीचे कर रहा है तो ट्रैपिंग हो सकती है» [00:15:14-00:15:36]. EN: for longs, Nifty daily above SMA20 and SMA50; if not, reduce size («पोजीशन थोड़ी कम रखेंगे» 00:29:14).

R10. Exit / carry.
- Book intraday normally; to carry overnight (BTST) keep one lot or convert to a spread: Q: «इन केस मेरे पास दो लॉट में है, तीन लॉट में है। तो वहां हम क्या करते हैं कि एक लॉट को रख लेते हैं अगले दिन के लिए या प्रॉफिट को लॉक कर देते हैं स्प्रेड में» [00:24:18]. Claim: next-day move in the option is bigger than the stock's (00:03:31).
- Risk cap: «कभी भी एक ट्रेड में 2% से ज्यादा रिस्क नहीं रखनी है अपनी पूरी पोर्टफोलियो साइज का» [00:31:00].

R11. Validation bar he sets himself: check at least 30-40 stocks; trust only if his rules are right more than 80% of the time, else drop them. Q: «कम से कम 30 से 40 स्टॉक के मोमेंटम को चेक करें और उसमें मोर देन मेरी बातें 80% सही हो» [00:31:08-00:31:30]. Expected result: «10 ट्रेड में से छह से सात ट्रेड सही» [00:11:36-00:11:49]. After a loss do not break discipline [00:11:11].

Market-condition: works on a momentum day; range-bound days kill option premium («रेंज बाउंड हो जाए बाजार तो ... प्रीमियम गलता रहता है» 00:04:20). Skip if first-hour candle huge.
Nifty view at end [00:33:36]: HM buying -> yesterday's low acts as support; below it target monthly SMA20 (weekly SMA20 nearby).

---------------------------------------------------------------
## 5GZIshXnxW8  Convergence Strategy (positional, MA convergence)
Claims average-based reading beats price action: «एवरेज बेस्ट सबसे अच्छा है... एवरेज की एक्शन में आपके साथ कोई धोखा नहीं» [00:01:51-00:01:58].

C1. Setup: all averages (20 to 200, EMA/SMA mix) converge to ONE spot; price must have fallen first, then reclaimed the cluster.
- Q: «जब अपने एवरेज के साथ... 200 डे का एवरेज और फाइव डे या 20 डे का एवरेज जब एक जगह पे आ जाता हो... प्राइस वहां से एक बड़ी मूवमेंट लेती है» [00:06:26-00:06:50]
- Q: «प्राइस पहले गिरा हो और गिरने के बाद वो दोबारा से कन्वर्जेंस के ऊपर कम से कम दो क्लोज दिया हो» [00:07:14-00:07:25]; «जो डे पे... वीकली पे... मंथली पे... मिनिमम दो क्लोज चाहिए। एक क्लोज में आपको ट्रैप किया जा सकता है» [00:07:25-00:07:50]
- EN: Need at least 2 closes above the cluster on the SAME timeframe (daily on daily, etc.), or one close then hold above the first close's high for 1-2 hours.
- Cluster must be tight, no gaps between averages: «डिस्टेंस नहीं होनी चाहिए अगर ये डिस्टेंस है तो रिलायबल नहीं है» [00:14:46]. Flat converged averages = strongest («रॉकेट की तरह जाएगा» 00:13:40). View it on a line chart for a clean picture (00:15:21).

C2. Trend vs sideways test: put a Bollinger band on the daily; thin band = sideways; band "blast" = trend. Use once, then remove. [00:05:34-00:06:16]. Horizontal line must be drawn where price CLOSED, not at wicks [00:09:23-00:09:54].

C3. Entry: best entry when price comes back near the 20 SMA/EMA while holding above the cluster. Q: «बेस्ट एंट्री होगा जब एक 20 एसएमए के पास कहीं आता हो» [00:10:46]; «जब कन्वर्जेंस के ऊपर वो सस्टेन करने लगा तो 20 एसएमए के आसपास या 20 ईएमए के आसपास» [00:11:12]. Another best-buy spot: near the 200 line on daily/weekly/monthly (00:16:24).
C4. Stop (positional): below the lowest line of the cluster. Q: «एसएल होगा इसके नीचे जो सबसे लोअर लाइन है» [00:11:28]
C5. Target: none; 50% booked, 50% ridden until the lower line breaks: Q: «कोई टारगेट नहीं होता है मार्केट में। आप 50% बुक कर लीजिएगा। 50% आप राइड करते रहिए» [00:11:40]
C6. Cluster break = 2 closes below it (00:12:10); death cross confirms.
C7. Above the convergence "every dip is a buy"; below it "every rise is a sell": Q: «एवरी डीप इज बाय... एव्री राइज इज सेल» [00:13:51-00:14:06]

C8. HILEGA MILEGA overlay (positional, short term): Q: «हिलेगा मिलेगा शॉर्ट में हेल्प ले सकते हैं... इग्नोर मत कीजिएगा» [00:16:47]. Q: «अगर आप पोजीशनल लिए हो और हिलेगा मिलेगा में सेल आ जाता है तो एक बार ट्रेड से निकल जाना है और दोबारा जब हिलेगा मिलेगा में बाय आ जाता है तो फिर आप एंटर कर जाइएगा... कन्वर्जन टूटने का वेट मत कीजिएगा» [00:17:27-00:17:48]. EN: Exit when HM flips to sell, re-enter when HM flips to buy again; do not wait for the convergence to break. (Timeframe of the HM here = same chart as the position, daily implied.)
Example: Tata Motors 372 -> 446 then double top gave back gains if held without the 50% rule [00:17:03-00:17:16].

---------------------------------------------------------------
## dm7x3ZY9K9M  Stop-Loss kaise lagayein (2025, Nifty intraday + options)
Method: "price follows the higher timeframe" (00:05:01). Day timeframe sets the stop; hourly confirms. NK says small timeframes need 5-10 years of experience (00:06:17).

S1. Stop is on the DAY timeframe, on closing basis, or 1 hour sustain, whichever happens first.
- Q: «डे टाइम फ्रेम पे जो रखेंगे क्लोजिंग बेसिस रखिएगा या कम से कम उसके ऊपर 1 घंटे सस्टेन अगर लगता है कोई न्यूज़ आ गया है तेजी से भाग तो वन ऑवर सस्टेन रख लो» [00:08:12-00:08:33]
- Q: «25399 25400 पे शॉर्ट करते हैं तो मेरा एसएल होगा 25491 के ऊपर क्लोज करो या वन आवर सस्टेन करो। दोनों में से जो भी पहले हो जाता है» [00:12:16-00:12:29] (91-pt stop on Nifty).
S2. Entry zone = the "quarter" of yesterday's candle: split yesterday's daily candle into three parts; the first third from the extreme in the trend direction is the entry zone. Q: «कैंडल के तीन पार्ट होते हैं... 33 33 33... एक क्वार्टर तक जाने की तो कोशिश करती है» [00:10:22-00:10:35]; «यह जो मार्क किया है लोएस्ट साइड का यह हमारा एंट्री पॉइंट होता है... जिस साइड में डायरेक्शन है» [00:10:53-00:11:03]. Then drop to 30m/15m/10m/1h and enter where risk-reward is good; price need not touch it exactly (00:11:56). [PARAM: "quarter" is actually a third in his own words.]
S3. Only trade WITH the daily trend: after an up-trending daily, a gap-down plus break of the previous low triggers sell; in a falling daily, break of previous high triggers buy; 1h must sustain. Q: «बढ़ते हुए चार्ट में अगर लो ब्रेक हो जाए तभी हम सेल का ट्रेड लेंगे डे टाइम फ्रेम पे और घटते हुए चार्ट में हाई ब्रेक हो जाती है तभी हम बाय का ट्रेड लेते हैं» [00:09:37-00:09:46]. Same idea restated 00:21:07-00:22:50 ("don't jump at the open; wait for yesterday's low break or a sell signal on the 1m-timeframe at the quarter").
S4. Options: stop is on spot/futures day-low/high, converted to option; buyers' stops look big but are "right": «एसएल बड़ा छोटा से मतलब नहीं है। एसएल सही होने से मतलब है» [00:20:02]. Sellers: stop above the day high on SPOT [00:16:54]. VWAP stop is too tight/hunted [00:01:25].
S5. RSI overbought/oversold nuance: when RSI is at an extreme (<30 or >70) ignore the extreme and wait for the day high/low to be closed beyond. Q: «अगर आरएसआई ओवरबाउट या ओवरसोल्ड हो गई हो तो वहां पे इस चीज को थोड़ा सा इग्नोर कर देना है। वहां पे वेट करना है कि डे हाई क्लोज करो तब देखेंगे» [00:25:10-00:25:22]. RSI length not stated.
S6. Buy-side in a downtrend: book quickly; sell-side hold longer. Q (t1b, see below) and here: «बाय के साइड में अगर जाते हैं तो फटाफट भागेंगे छोटे-छोटे प्रॉफिट बुक करके» [00:23:00]
S7. Claim: stop-hunt rate drops a lot ("more than 80% of cases in your favour" 00:25:48) but he says no strategy is 100% and rules from him are "tukka" until backtested (00:13:08).

---------------------------------------------------------------
## i2bGV_Wo5Yw  How to trade Long Leg Doji (Beginner series 2)
D1. Definition: body < 5% of the high-low range, otherwise it is a spinning top. Q: «पूरी बॉडी का 5% से ज्यादा हमारा यह नहीं होनी चाहिए जो भी हाई और लो है» [00:08:38-00:08:59]
D2. Valid only at an extreme: RSI near 30 or above 70, or at support/resistance (static or dynamic) or demand/supply zone, after a good move. Q: «आरएसआई का 30 का ज़ोन के आसपास और आरएसआई 70 के ऊपर के ज़ोन के आसपास अगर इस प्रकार की डोजी बनती है तो उस केस में ये ज्यादा रिलायबल होता है» [00:09:36-00:09:48]; «बीच में कहीं डोजी ऐसा बनता जाए तो उसको आप इग्नोर करेंगे» [00:13:04]
D3. Trigger: the NEXT candle must close beyond the doji's high (long) or low (short); stop = other side of the doji. Q: «जब तक कि कोई बड़ी सी कैंडल जो भी हाई डोजी लगी है उसके ऊपर क्लोज ना कर जाए... अगर हाई के ऊपर ग्रीन कैंडल क्लोज कर गई तो ... इस एसएल के साथ हम ट्रेड करेंगे» [00:10:34-00:10:44]; «सिंगल कैंडल पैटर्न में सिंगल कैंडल की कीमत नहीं होती है हमेशा सेकंड कैंडल की होती है» [00:12:13]
D4. If a position is open when a doji appears, reduce or book profit and wait [00:11:20]. If price pokes beyond the doji and fails, the doji is invalid [00:17:26].
D5. "Black doji" (long-leg doji coloured black) is stronger; at the close after a fall it tends to gap up next day, after a rise gap down. Q: «क्लोजिंग टाइम पे अगर ब्लैक डोजी बन जाती है और मार्केट गिरा हुआ है तो अगले दिन गैप अप होने की कोशिश करती है» [00:14:23-00:14:43]. (Caption does not say what black means in his chart colouring.)
D6. HILEGA MILEGA: «हिलेगा मिलेगा जिस दिशा में लेके जा रहा है... हम भी उसी डायरेक्शन में जाएंगे... रेड लाइन जब तक ऊपर है डे टाइम फ्रेम में बाजार ऊपर नहीं जाएगी। बाजार को ऊपर जाने के लिए इस रेड लाइन को अंदर आना ही होगा» [00:15:40-00:15:59]. Also: «अगर आप छोटे क्वांटिटी में सिर्फ हिलेगा मिलेगा को फॉलो करें। किसी भी टाइम फ्रेम पे... दो-तीन महीने बाद... आप अच्छी स्थिति में हैं... ब्लाइंडली फॉलो करना पड़ेगा. और जितना बड़ा टाइम फ्रेम फॉलो कीजिए उतना अच्छा है... डे टाइम फ्रेम या आवरली, और अगर ज्यादा लंबे समय के लिए है तो वीकली» [00:16:37-00:16:55]. EN: follow HM blindly on daily/hourly (weekly for long holds); larger timeframe = better.
D7. Monthly HM: no monthly crossover yet -> don't call monthly trend changed [00:03:20-00:03:30].
D8. Targets: «मेरा टारगेट था 100 लेकिन 100 ना जाके 60 पे ही लग रहा है कि रिवर्सल ले सकती है तो चलो जी ओके बाहर» [00:05:49] (exit early when momentum fades; no fixed target).

---------------------------------------------------------------
## B7iGQef_z6I  Candle series #3 (master candle) + market view + PGP career Q&A
M1. MASTER CANDLE: a big candle (bigger than neighbours; wicks both sides but each wick smaller than the body) followed by 3-4 candles trading INSIDE it for 1-4 days; trade the break of its high (bull) or low (bear). Q: «मास्टर कैंडल वो होती है जिसमें कि वीक हो सकता है... वो पूंछ बॉडी से छोटी होनी चाहिए दोनों साइड की... उसके बाद इसी कैंडल के अंदर ही ट्रेड करना शुरू कर देता है प्राइस... 1 2 3 दिन 4 दिन... इस कैंडल का हाई अगर ब्रेक कर जाए तो वहां पे ब्रेकआउट होता है, बुल आ जाता है और लो अगर ब्रेक हो जब ब्रेकडाउन हो जाती है, फिर बियर आ जाता है» [00:11:28-00:12:32]. Works for swing and intraday. No stop/target stated (obvious stop = other side).
M2. Daily close needed above a weekly high for trend strength: Q: «25,100 के ऊपर वन डे की क्लोजिंग चाहिए» [00:01:33]; NK's closing-basis habit again.
M3. HM daily "not strong" is not a sell: Q: «बट इसका मतलब यह नहीं कि सेल में भी चल रहा है। सेल में चलने के लिए उसको 50 से नीचे जाना चाहिए» [00:03:17]. Up requires the red line to go down: «ऊपर जाने के लिए इस रेड लाइन को नीचे जाना होगा। तभी प्राइस स्ट्रांग होगा» [00:02:59]. [PARAM: sell state = HM line below 50.]
M4. Trade support-zone buys only inside multiple supports: «हमें उन सपोर्ट ज़ोन में ही ट्रेडिंग डिसीजन लेनी चाहिए» [00:03:58].

---------------------------------------------------------------
## J_BzeTB3PpA  Nifty ka agla move: Volume analysis
V1. Trade the REVERSAL of a volume climax, not the move itself, near support/resistance or on expiry day. Q: «वॉल्यूम... नीचे की तरफ बनता है तो अगली कैंडल पे... रिवर्सल ले लेगी तो हमें इस रिवर्सल को ट्रेड करना है ना कि इस मेन ट्रेड को» [00:04:03-00:04:19]; «रिवर्सल कब आती है जब मार्केट सपोर्ट और रेजिस्टेंस के पास हो» [00:04:35]; «एक्सपायरी का दिन है तो भी यह ज्यादा होगा» [00:04:55]. Watch ITM option volume (00:04:28). He says there are 10-12 ways to read volume; this video gives only the basic (no number).
V2. Frequency: find only 4-5 good trades a month [00:04:55-00:05:04].
V3. Break/hold rule: 24,350 hold for at least 1 hour above = move up; closing basis resistance (24,200/24,300) [00:01:16, 00:12:44-00:13:03]. Monthly close above 24,444 -> target 26,600 [00:10:25]. «एक ही न्यूज़ के कारण बाजार दो बार नहीं गिरती है» [00:09:48].
V4. HM: weekly HM buy with red line inside = market won't fall: Q: «वीकली में हिलेगा मिलेगा यह बाइंग दिखा रहा है कि रेड लाइन जब तक अंदर रहेगी मार्केट को गिरने नहीं देगा» [00:07:03]. Short-term (daily/intraday) HM sell, red line outside: market must bring red line down first: Q: «रेड लाइन ऊपर आया है मुझे लगता है एक झटका देकर इसको क्रॉस करने की कोशिश करेगा» [00:12:16]. Bollinger + HM: «बुलिंजर बैंड के 20 एसएमए के जस्ट ऊपर चल रहा है... इसको हम बोलते हैं हिलेगा मिलेगा चीटिंग» [00:09:03-00:09:11] (price hugging BB basis (20 SMA) while HM says sell = "HM cheating" = divergence, buy dips; don't short until below 23,550).
V5. Range rule: with multiple supports below, no swing shorts: Q: «लोअर लेवल पे मल्टीपल जब सपोर्ट होते हैं तो हम स्विंग में शॉर्ट नहीं करते हैं» [00:06:47]. Range 23,800-24,300: play 20-20 until a break, then check volume [00:10:03, 00:11:58]. Narrow range -> big move in 2-5 days [00:11:33].
V6. Nifty 200 DMA; bull confirmed only on close above 200 DMA and 50 crossing above 200 [00:05:39].

---------------------------------------------------------------
## lmhqooBqJWU  Nifty mein girawat ya rally?
L1. HM predicts the next-day gap on 5/10/15-min charts at the close. Q: «5 मिनट 10 मिनट 15 मिनट में अगर हिलेगा मिलेगा सिस्टम बाइंग बोल के जाए तो इसका मतलब गैप अप होगा सेल बोल के जाए तो गैप डाउन होने की संभावना है। जरूरी नहीं कि होगा» [00:08:43-00:08:54]. Testable: HM state at last 5/10/15m bar vs next open gap.
L2. HM sell condition: red line rising; flips fully to sell once RSI goes below 50 and the gap opens between lines: Q: «रेड लाइन जा रहा है लेकिन अभी तक ये 50 के नीचे जैसे ही 50 के नीचे आएगा इस तरह से और ये गैप बन जाएगा तो ये सेल चला जाएगा» [00:05:02-00:05:11]. [PARAM: 50-level on the HM RSI; "gap" = visible separation between the two HM lines.]
L3. Three moving averages (20 SMA, 50 SMA/EMA, 200 DMA). Don't call trend reversal until price is above all; mixed EMA/SMA noted (00:05:41-00:06:29). Long only after a CLOSE above the candle-close/50 SMA: Q: «बाइंग तभी होनी चाहिए जब इस कैंडल के क्लोजिंग प्राइस के ऊपर प्राइस क्लोज करे या ये 50 एसएमए के ऊपर जाकर क्लोज करे» [00:07:39-00:07:50].
L4. Shorts need TWO closes below the 20 SMA: Q: «इस 20 एसएमए के नीचे जाकर क्लोज नहीं करेगा... दो क्लोज दो क्लोज हो जाएगी तो हमारा फिर से एसएल हो जाएगा शॉर्ट के लिए» [00:07:08-00:07:30].
L5. Swing vs intraday: Q: «जब तक ये 50 एसएमए से ऊपर नहीं आ जाए। स्विंग में हम बाइंग नहीं करते हैं... स्विंग में हम सेल नहीं करते। इंट्राडे में कर सकते हैं» [00:10:22-00:10:39]. Intraday: use prior day's high/low with stop-loss [00:11:26]. Also «जब भी 20 से कर्व मुड़ जाता है... स्विंग में मार्केट बाइंग में है» [00:11:09] (20 SMA slope turns up -> stop "every rise is a sell").
L6. Targets for shorts: first gap-fill/pivot (23,200), then the low [00:12:14-00:12:35].

---------------------------------------------------------------
## t1b_1h2QMXw  Beginners trading, special strategy for new traders
T1. Intraday trend = 10/15/30-min chart; trade only in the direction of Nifty's intraday trend; never sell into support / buy into resistance of the daily; close existing counter-trend positions when price reaches the daily support/resistance. Q: «आपको निफ्टी के ट्रेंड के साइड में ही ट्रेड लेना है» [00:18:13]; «जब भी प्राइस सपोर्ट के पास आए हमें वहां पर प्रीवियस जो पोजीशन है कट कर देनी» [00:18:58]. Mark daily-timeframe support/resistance first [00:18:49].
T2. Trend flag: index below the 200 DMA (daily) = downtrend: Q: «मार्केट हमारी 200 डीएमए के नीचे चल रही है... जब जब ऊपर आएगी ना तो सस्टेन नहीं करेगी... सेलिंग साइड का ट्रेड होगा तो हम थोड़ा उसे लंबे समय तक इंट्राडे में रखेंगे» [00:15:43-00:16:15]. Buy-side trades: take quick profit, avoid BTST.
T3. Three stock classes: moves with Nifty, own rhythm, circuit/range-bound; build separate watchlists [00:16:25-00:17:15].
T4. Position size rule: protect capital first; «लोअर द कैपिटल हायर द रिटर्न» [00:21:46]. 2 lines on the chart eventually replace 4-5 indicators [00:19:37]. (The rest of the video is career/wealth talk.)

---------------------------------------------------------------
## I4rHEfRhEWM, Xz61miXrOcY, RZzKYqTra3Y
No actionable trading rules (career roadmap with CA/tax compliance; "skill vs conviction" discussion; physical class clip). Keyword scan for HM/RSI/SL/VWAP/MA found nothing rule-like.
