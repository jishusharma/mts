# NK StockTalk, 55 captioned videos: merged rules (2026-11-14)

**Result: the Hilega Milega (HM) formula is not in any of the 47 non-interview videos, but the 55 give about 15 SOURCED parameter corrections to our tests (stop basis, RSI levels, first-hour definition, pivot set, filters), plus 10 new rules never tested.**

## How this was built

- Inputs: 5 batch extracts (`nk55_extract_b0..b4.md`, 55 videos minus 8 interview ids) and 5 verify files. Workers checked 423 quoted Hindi spans: 336 VERIFIED, 87 NOT FOUND (b0 57/16, b1 68/18, b2 64/12, b3 74/22, b4 73/19).
- Rule used here: only spans that match the cited video's `*_timed.txt` are quoted below. Every quote carries (video id, caption timestamp). A second pass re-checked every quote in this file against the transcript of the cited video (see "Quote audit" at the end). Rules whose only support was a NOT FOUND span are written as UNQUOTED (paraphrase, lower trust) or left out.
- Captions are auto-generated Hindi, so numbers and some words are garbled. Where a caption number is doubtful it is said so.
- HM formula status (from `NK_CLARIFICATIONS_1114.md`, interview/class worker, not re-checked here): RSI(9), EMA(3) and WMA(21) both on the RSI, zone 50/50, plus VWAP (class video Qdug_K_TNHg 00:24:18 and 00:39:49). Our guess (RSI9 with EMA3 vs WMA21) matches. The 55 videos add how NK READS it, not how it is built.
- Label key: SOURCED = NK's own words in a verified caption; OURS = our choice, never his; CLAIM = his statement, untested.

---

## Part 1. One table per concept

### 1.1 Hilega Milega (HM) state and use

| Rule | Parameter | Value | SOURCED quote (video, time) | Our tested guess and difference |
|---|---|---|---|---|
| Buy state | red line position | red line down/inside = buying; red line above = not buying | «ऊपर जाने के लिए इस रेड लाइन को नीचे जाना होगा।» (B7iGQef_z6I 00:03:03); «रेड लाइन जब तक ऊपर है डे टाइम फ्रेम में बाजार ऊपर नहीं जा» (i2bGV_Wo5Yw 00:15:48) | Ours was a flip/cross test (NK4). He reads a STATE (position of the red line), not a cross |
| Three states | not-buying is not selling | buy / neutral / sell | «सेल में चलने के लिए उसको 50 से नीचे जाना चाहिए» (B7iGQef_z6I 00:03:22) | NK4 had two states. Sell needs the oscillator under 50 AND the lines separated, so "not buy" must be neutral, not short |
| Sell trigger | level | HM RSI line under 50 | «ये 50 के नीचे जैसे ही... सेल चला जाएगा» (lmhqooBqJWU 00:05:06) | Matches our 50/50 zone; confirms the sell needs the 50 cross |
| Reaction zone | RSI line touching the red line | a touch of RSI and red line is the turn/pause zone | «जब ये आरएसआई और रेड लाइन जब टच करेगी» (i2bGV_Wo5Yw 00:03:39) | Not used by us. Candidate "touch" event |
| Monthly change needs a cross | timeframe | a monthly trend change is not accepted until the crossover happens | «हमारी ये अभी तक क्रॉसओवर नहीं हुई है» (i2bGV_Wo5Yw 00:03:20) | Higher-timeframe state change = crossover, not just position |
| Weekly buy claim | weekly HM, red line down | "market does not go down while the red line is down" (CLAIM, untested) | «ये वीकली टाइम फ्रेम पे हिलेगा मिलेगा। रेड लाइन नीचे है।» (FzNDQm7wC_s 00:03:09); «जब तक रेड लाइन नीचे है» (FzNDQm7wC_s 00:03:12) | We never tested a weekly HM state claim. Testable as a forward-return claim (Part 2, NKN-05) |
| Timeframes | which charts | entry reads on 5/10/15 min; confirmation on 1 hour; state on daily/weekly/monthly; "any timeframe you are comfortable with, bigger is better" | «वन आवर पे हिलेगा मिलेगा आपके फेवर में जरूर होना चाहिए।» (3KnEiKNh1pc 00:18:24); «किसी भी टाइम फ्रेम पे जिस टाइम फ्रेम में आप कंफर्ट हो» (i2bGV_Wo5Yw 00:16:37) | NK4 used 15m only. He pairs a 1h HM agreement with a 5-10m entry |
| Plain RSI beside HM | RSI length for the daily gate | plain RSI is 14 (not HM's 9); daily gate: RSI(14) above 50 | «आरएसआई हमारा 50 के ऊपर आ जाए। नॉर्मल 14 आरएसआई» (fZvp72BBmRI 00:04:58); «मैं सारे आर एसआई 14 की बात कर रहा हूं» (ysq6x0eCFvI 00:03:36) | We only had RSI9 inside HM. Two RSIs coexist: HM-RSI9 and a plain RSI(14) for the 50 gate |
| Overheat | RSI level | HM-RSI above 86 (also 86-88) means do not initiate longs | «हिलेगा मिलेगा आरएसआई 86 के ऊपर» (MLrMJ7rlL4U 00:16:38) | New filter. Caption "86" is garbled-prone; the 4SPDtbJVDr4 extract repeats 86-88 but its span was NOT FOUND, so use 86 as UNCONFIRMED |
| HM as a gate, never a trigger | "only closing is not OK" | price/MA event is not enough; HM must also agree | «सिर्फ क्लोज कर दिया। मेरे लिए ओके नहीं है भाई।» (cX2GZ7B5Gc8 00:16:00) | NK4 treated the HM flip as the trigger. He uses it as a confirmation of a price event |
| Exit and re-entry | HM flip | exit a positional trade on HM sell, re-enter on HM buy, do not wait for the convergence to break | «हिलेगा मिलेगा में सेल आ जाता है तो एक बार ट्रेड से निकल जाना है» (5GZIshXnxW8 00:17:37) | We never used HM flip as an exit on another entry |
| Short gate | what must be true to short | HM in sell AND the marked zone breaks | «शॉर्ट सेल तभी हमें जानी है जब हमारा हिलेगा मिलेगा हमारी सेल में आ जाए» (sbMyohOXRqE 00:13:41) | Two-condition short (HM sell + zone break) not tested |
| Overnight read | HM at the close | BTST/STBT only if HM on the last 5/10/15 min agrees | «हिलेगा मिलेगा लास्ट का 5 10 15 मिनट का देख लो» (6zDpjsesOyw 00:33:36) | Not tested. Crypto analogue needs an "end of session" definition (OURS) |
| Not stated anywhere | | line lengths, colour map, VWAP anchor for HM | none | still NOT_SEEN in the 47 non-interview videos; the formula rests on the class video only. NK promises a 30-40 min HM video: «हिलेगा मिलेगा पे हम लोग एक वीडियो ला रहे हैं» (J_BzeTB3PpA 00:14:09) |

### 1.2 First-hour setup (the 3KnEiKNh1pc intraday masterclass)

This is the most completely specified rule set in the 55. Order is the order he gives it.

| Step | Parameter | Value | SOURCED quote (video, time) | Our tested guess and difference |
|---|---|---|---|---|
| Scanner | first-hour move | stock up 2% or more in the first hour (sometimes 1%); mirror down for shorts | «आपको ऐसे स्टॉक की तलाश करनी है जो इंट्राडे में मॉर्निंग में फर्स्ट वन आवर में 2% या उससे» (3KnEiKNh1pc 00:09:15) | NK1 had no mover scanner. New filter (use the +-1% and +-2% first-hour move) |
| Trap window | first 5-10 minutes | price dips under yesterday's close, then comes back above it | «फर्स्ट 5 टू 10 मिनट में कल की जो क्लोजिंग प्राइस थी उसके नीचे प्राइस चला गया हो» (3KnEiKNh1pc 00:07:24) | NK1 trigger was a first-hour LOW break, not a prior-close dip-and-reclaim. Different trigger |
| Confirmation window | how long | the 1-hour candle must close above yesterday's high within 60 or 90 minutes | «फर्स्ट 60 मिनट में या 90 मिनट में» (3KnEiKNh1pc 00:08:58); «आज फर्स्ट वन आवर में ही क्लोज कर जाए» (3KnEiKNh1pc 00:08:07) | "First hour" = ONE 1-hour candle (60, optionally 90 min). Our "3 bars" is 15 min on 5m bars: too short. On 15m bars 3 bars = 45 min, near his alternate (8TQnHHwV_IU, see 1.5). Treat 3 bars as OURS and wrong unless the bar is 20 min |
| Skip rule | first-hour candle size | the first 1-hour candle must not be big; skip if it is | «पहली वन आवर की जो कैंडल है वह काफी बड़ी नहीं होनी चाहिए» (3KnEiKNh1pc 00:12:01) | New filter. No numeric cap spoken (examples 4-5%); the cap is OURS if tested |
| Entry | where | on the next candle, when price comes back to VWAP | «वीवप के पास जब प्राइस वीवप के पास आएगी तो वहां पे हमारी एंट्री बनेगी» (3KnEiKNh1pc 00:10:08) | NK1 entered "near VWAP" but after a different trigger |
| Stop level | where | under that day's low, measured on spot/future, never on the option | «नेकेड में उस दिन के डे लो का एसएल मानेंगे» (3KnEiKNh1pc 00:10:48) | Our stops were intraday volatility stops (R = max(structural, 0.5%, 0.6 ATR)). He uses the structural day low; keep our floor on top (cross-checked in Part 2) |
| VWAP stop | basis | only a 1-hour close under VWAP counts; 10 and 15 minutes do not | «1 आवर के नीचे आके क्लोज करो तब मानेंगे। हम 10 मिनट 15 मिनट पे नहीं मानेंगे।» (3KnEiKNh1pc 00:25:50) | CORRECTION: close-based, on the 1h. NK1/NK6 used intraday touches |
| HM filter | confirmation | HM on the 1h must favour the trade | «वन आवर पे हिलेगा मिलेगा आपके फेवर में जरूर होना चाहिए।» (3KnEiKNh1pc 00:18:24) | Not in NK1 |
| Index filter | for longs | Nifty (our BTC proxy) above its daily 20 and 50 SMA; otherwise cut size | «निफ्टी भी बाइंग में जाने का मतलब 20 और 50 एसएमएस से ऊपर ट्रेड कर रहा हो डे टाइम फ्रेम पे» (3KnEiKNh1pc 00:15:29) | Our phase label used a 20-day MA slope plus ADX; his filter is close above SMA20 AND SMA50 on daily |
| Patience | no jumping | do not act in the first minutes | «जल्दी का काम शैतान का होता है।» (3KnEiKNh1pc 00:15:10); «कोई ओपनिंग में जंप ना लगाए। बाजार को बोलने दीजिए» (dm7x3ZY9K9M 00:22:32) | Supports a wait-for-the-hour design |
| Strike, delta | options only | near-OTM, delta 0.3-0.4 | «वो नियर ओटीएम हो... डेल्टा 0.3 0.4» (3KnEiKNh1pc 00:05:19) | Options only (Part 3) |
| Hit-rate claim | CLAIM | he says it is right 6-7 of 10 trades | «10 ट्रेड में से छह से सात ट्रेड सही» (3KnEiKNh1pc 00:11:49) | Untested claim. Our NK1 win rates were 22-59% depending on exit |

### 1.3 Stops and confirmation closes

| Rule | Parameter | Value | SOURCED quote (video, time) | Our tested guess and difference |
|---|---|---|---|---|
| Day-timeframe stop | basis | closing basis, or at least 1 hour of holding beyond the level, whichever comes first | «क्लोजिंग बेसिस रखिएगा» (dm7x3ZY9K9M 00:08:18) | CORRECTION: all our studies used intraday stops; the close-based stop is untested (listed in `NK_TESTS_SYNTHESIS_1114.md` as open) |
| Stop quality | | size matters less than being right | «एसएल बड़ा छोटा से मतलब नहीं है। एसएल सही होने से मतलब है।» (dm7x3ZY9K9M 00:20:02) | Supports a structural stop; our 0.5% / 0.6 ATR floor is OURS and a hard requirement of the lab, not his |
| Two closes | confirmation | two closes, not one: "bear" arrives only after 2 daily closes under the 20 SMA | «20 एसएमए के नीचे जिस दिन क्लोज कर जाए दो क्लोज तो हमें मान के चलें» (a8RP5ftOfGo 00:08:50) | Our regime flips used one bar. CORRECTION: add the 2-close rule |
| Two closes (stop) | short stop | two closes back above the 20 SMA stop a short | «दो क्लोज दो क्लोज हो जाएगी तो हमारा फिर से एसएल हो जाएगा» (lmhqooBqJWU 00:07:26) | Same |
| Two closes (breakdown) | | breakdowns need at least two closes | «कम से कम दो क्लोजिंग इंपॉर्टेंट होती है किसी चीज को ब्रेक डाउन» (IjU9PpqvrI8 00:14:58) | Same |
| 200 DMA hold | duration | a break below the 200 DMA counts only if price sustains below for 10-12 days | «इसके नीचे आकर सस्टेन हो जाए प्राइस मतलब 10 दिन 12 दिन» (a8RP5ftOfGo 00:09:40) | New persistence parameter (OURS if we use 10 days as is: SOURCED as 10-12) |
| 200 DMA re-entry | | after a drop under it, wait for 2 daily closes (or 1 weekly) above 200 DMA and 50 SMA | «जब तक 200 डीएमए के ऊपर और 50 एसएमए के ऊपर दो क्लोज ना कर जाए» (PLJda-dtBIc 00:13:25); «200 डीएमए के ऊपर आ जाए और आकर वो दो क्लोज या वीकली क्लोज कर ले।» (PLJda-dtBIc 00:14:26) | New |
| MA type | | simple MA (SMA) for the 200 DMA, not EMA | «200 डीएमए एसएमए का यूज़ करना है। ईएमए का नहीं» (FzNDQm7wC_s 00:02:39) | We have not tested a 200 SMA rule; the convergence uses EMAs (see 1.4), the two are different |
| Stops on spot | options | stop on the spot price when buying options, on the option when selling | UNQUOTED (JMyLmFeMAUA 00:01:16; span NOT FOUND in the worker check, found only as fragment). Same point in 3KnEiKNh1pc 00:10:48 above | Our crypto trades have no option leg: stop on the underlying (already true) |
| Backtest caveat | his own words | "back-test it; it is all luck until you do" | «बैक टेस्ट के बाद... सारी चीजें तुक्का है» (dm7x3ZY9K9M 00:13:08) | Consistent with our approach |

### 1.4 Convergence (stacked moving averages)

| Rule | Parameter | Value | SOURCED quote (video, time) | Our tested guess and difference |
|---|---|---|---|---|
| Construction | averages | EMAs from 20 to 200 plotted together; when they sit together it is a "convergence" | «मैं 20 से लेकर 200 तक के ईएमए को जोड़ देता हूं।» (5GZIshXnxW8 00:04:30) | Never tested. Which EMA lengths between 20 and 200 is NOT stated (20/50/100/200 is OURS) |
| Tightness | width | sideways markets look thin; entries with spread-out averages are unreliable | «साइडवेज मार्केट में जब रहेगा तो ये काफी पतला रहेगा।» (5GZIshXnxW8 00:06:03); «डिस्टेंस नहीं होनी चाहिए अगर ये डिस्टेंस है तो रिलायबल नहीं है» (5GZIshXnxW8 00:14:52) | No numeric width. A tolerance (OURS) must be pre-registered |
| Context | direction | long side only after a fall | «एवरी डीपी बाय ही करना है, सेल नहीं करना है» (5GZIshXnxW8 00:13:58) | Not tested; matches a "buy the dip after a fall" bias |
| Entry | where | near the 20 SMA once price sustains above the convergence | «बेस्ट एंट्री होगा जब एक 20 एसएमए के पास कहीं आता हो» (5GZIshXnxW8 00:10:46) | New |
| Stop | where | under the lowest line of the convergence | «एसएल होगा इसके नीचे जो सबसे लोअर लाइन है» (5GZIshXnxW8 00:11:33) | New. Structural; our floor still applies |
| Exit | target | no target; book half, ride the rest | «कोई टारगेट नहीं होता है मार्केट में। आप 50% बुक कर लीजिएगा।» (5GZIshXnxW8 00:11:46) | New exit shape (partial + runner) |
| Two closes | confirmation | at least two closes above the convergence on the same timeframe | UNQUOTED (5GZIshXnxW8 00:07:20 and 00:12:14; both spans NOT FOUND in the worker check). The two-close idea itself is SOURCED elsewhere (1.3) | Use as OURS-informed until a clean re-read |

### 1.5 Opening range, pivots, levels

| Rule | Parameter | Value | SOURCED quote (video, time) | Our tested guess and difference |
|---|---|---|---|---|
| Opening range | size | the 1-hour opening range ("ORB" on the 1h); broken only when the 1h (or 45-min) candle closes outside | «एक्सट्रीमली रेंज बाउंड मार्केट» (8TQnHHwV_IU 00:07:09) | CORRECTION on the guess "first-hour range = 3 bars": his range is a 1h candle; alternate 45 min. Close-based, not touch-based. (Expiry-day Sensex context, so use as a definition, not as a signal.) |
| Pivots | set | R2 break leads to R3; sitting at R3 for 3 days leads to a large up move | «जब भी R2 के ऊपर प्राइस निकलती है तो R3 के आसपास जाने की कोशिश करती» (FzNDQm7wC_s 00:09:44); «तीन दिनों तक इस तरह पोजीशन बनती» (a8RP5ftOfGo 00:13:56) | CORRECTION: NK2 tested P, S1, R1 only. He also trades R2/R3 (and called S3/R3 strong earlier). Untested extension |
| Zones, not lines | | support/resistance is a zone | «कोई भी सपोर्ट रेजिस्टेंस कोई लाइन नहीं होता है» (FzNDQm7wC_s 00:04:44) | Levels as bands, width OURS |
| Prior-day high | intraday trigger | "above today's high, it goes to buying" | «आज के हाई के ऊपर अगर बाजार निकलती है तो वो बाइंग में चली जाएगी» (FzNDQm7wC_s 00:08:53) | Intraday high-break trigger; supports prior-high logic in 1.2 |
| Do not buy in the first range | liquidity | no entry at the primary support zone; buy a breakout or the second demand zone | «हम सपोर्ट पे एंट्री नहीं लेंगे» (fZvp72BBmRI 00:18:39); «इस ज़ोन में नहीं खरीदारी करनी चाहिए।» (fZvp72BBmRI 00:18:54) | Opposite of buying a first-touch support reclaim. Our NK2 pivot reclaim is a first-touch rule |
| Double-bottom stop | | stop under the double bottom range | «डबल बॉटम में बाइंग करते हैं। हमारा एसएल इसके नीचे होता» (fZvp72BBmRI 00:13:39) | Exists in our double-bottom retest study; stop basis not matched |
| Shorts at support | | no short entries near support | «सपोर्ट के पास कोई शॉर्ट का ट्रेड हम लोग नहीं लेते हैं» (ysq6x0eCFvI 00:03:00) | Mirror of the long rule; not applied in NK1/NK2 shorts |

### 1.6 RSI levels

| Rule | Parameter | Value | SOURCED quote (video, time) | Our tested guess and difference |
|---|---|---|---|---|
| Oversold is not a buy | | wait for RSI back above 30 AND daily HM in buy | «ओवरसोल्ड कंडीशन का मतलब यह नहीं होता है कि हम बाइंग कर लें।» (4-OtV5JVM4g 00:06:52) | CORRECTION: levels are 30/70 (SOURCED). We coded 35/65 in NK5 (OURS). Also he waits for the recovery above 30, not the touch |
| Plain RSI | length | 14 | see 1.1 | |
| Other people's levels | | "some use 55, some 45" (a habit he does not endorse) | «आरएसआई में कुछ लोग 55 ले लेते हैं कुछ लोग 45 ले लेते हैं» (PLJda-dtBIc 00:09:00) | The 35/65 variant is not his |
| Long-leg doji validity | | body no more than 5% of the whole candle | «पूरी बॉडी का 5% से ज्यादा नहीं होगा» (i2bGV_Wo5Yw 00:08:17) | New. Doji only meaningful near RSI 30/70 or a level (the RSI link is in an UNQUOTED span, i2bGV_Wo5Yw 00:09:30 is an adjacent verified fragment about a prior up/down move) |

### 1.7 Trend and regime reading (higher timeframe)

| Rule | Parameter | Value | SOURCED quote (video, time) | Our tested guess and difference |
|---|---|---|---|---|
| Reversal checklist | any one of | daily close above 200 DMA on weekly basis; daily RSI(14) above 50 held 1 week; weekly HM buy plus weekly close above 20 SMA; daily OBV above zero sustained | «प्राइस अपने डे टाइम फ्रेम पे 200 डीएमए के ऊपर वीकली बेसिस» (ysq6x0eCFvI 00:03:17); «हिलेगा मिलेगा वीकली बेसिस पे बाइंग में आ जाए और 20 एएमए क» (ysq6x0eCFvI 00:04:37); «ऑन बैलेंस वॉल्यूम डे टाइम फ्रेम पे जीरो लाइन के ऊपर सस्» (ysq6x0eCFvI 00:04:41) | Our phase label is a 20-day slope plus ADX(14). His regime change rests on 200 DMA, RSI(14)>50 held, weekly HM and OBV. A different regime definition |
| Hourly swing switch | | a close above the 200 average on the 1h chart puts the swing view in buy until it closes back under | «जब भी 200 डीएमए के ऊपर आवरली टाइम फ्रेम पे मार्केट क्लोज करती है» (a8RP5ftOfGo 00:13:14) | New regime filter on 1h |
| Trade with the index | | take trades on the index's side, not against | «आपको निफ्टी के ट्रेंड के साइड में ही ट्रेड लेना है» (t1b_1h2QMXw 00:18:13); «निफ़ी अगर अप ट्रेंड में है तभी हमारी पोजीशन बने।» (4SPDtbJVDr4 00:06:54) | Our matched-by-phase design already follows this idea; the filter for crypto would be the BTC trend |
| Counter-trend setup | HTF 20 SMA | 20 SMA is the one he uses day-trading; price rising into it meets resistance | «जब आप डे ट्रेडिंग करते हैं तो 20 एसएमए को हम लोग» (cX2GZ7B5Gc8 00:02:40) | Untested. Setup below in Part 2 (NKN-04) |
| Rare confluence | daily and weekly 20 SMA coincide | stronger effect | «डे टाइम फ्रेम की 20 एसएमए और वीकली टाइम फ्रेम की 20 एसएमए एक ही दिन» (cX2GZ7B5Gc8 00:06:43) | Untested |
| Failed pattern | | counter-trade only after an hourly-or-higher pattern has failed | «मिनिमम आवरली या उससे ऊपर के टाइम फ्रेम पे कोई पैटर्न बना हो» (cX2GZ7B5Gc8 00:04:50) | Relates to fakeout fade (NK3), but his minimum is 1h |
| Wait for confirmation | | no action until confirmed | «जब तक कंफर्मेशन ना हो कोई एक्शन नहीं लेना है।» (cX2GZ7B5Gc8 00:10:48) | Design principle |
| Spot trigger | small-timeframe 20 SMA cross | spot on 5/10/15 min crosses against its prior move: rising price falls under, falling price rises above its 20 SMA | «प्राइस 20 एसएमए के नीचे आ जाए। 10 मिनट के टाइम फ्रेम पे» (cX2GZ7B5Gc8 00:13:21) | Untested; options-chart confirmation half is not portable |

### 1.8 Candle patterns

| Rule | Parameter | Value | SOURCED quote (video, time) | Difference |
|---|---|---|---|---|
| Master candle | | a big candle with small wicks; 3-4 candles trade inside; the break of its high or low is the trade | «उसके अंदर तीन चार कैंडलें ट्रेड करेगी और उसके बाद ब्रेकआउट» (B7iGQef_z6I 00:12:36); «मास्टर कैंडल वो होती है जिसमें कि वीक हो सकता है» (B7iGQef_z6I 00:11:42) | Untested. "Big" and "small wicks" have no numbers |
| Doji in a trend | | ignore a doji in the middle of a trend | «बीच में कहीं डोजी ऐसा बनता जाए तो उसको आप इग्नोर करेंगे» (i2bGV_Wo5Yw 00:13:04) | Untested |
| Doji meaning | | "waiting" | «लॉन्ग लेग डोजी का मतलब... वेटिंग।» (i2bGV_Wo5Yw 00:11:24) | Untested; trigger is the next candle beyond the doji extreme |

### 1.9 Risk and sizing (not an edge, but a stated constraint)

| Rule | Value | Quote (video, time) |
|---|---|---|
| Risk per trade | 2% maximum | «जब भी आप कोई ट्रेड लेते हैं तो 2% से ज्यादा रिस्क आप नहीं ले सकते» (4SPDtbJVDr4 00:04:56) |
| Stop size | about 2% | «एक अच्छा स्टॉप लॉस जो होता है 2% के आसपास का होता है।» (MLrMJ7rlL4U 00:08:08) |
| Trades per day | at most 2 | «हर दिन दो ट्रेड से ज्यादा नहीं लेना है» (MLrMJ7rlL4U 00:10:46) |
| Never average a falling stock | | «गिरते हुए स्टॉक को पहले तो एवरेज मत करो» (4SPDtbJVDr4 00:06:19) |

Note: his 2% stop is wider than our 0.5% floor on coins with low volatility, but our floor is max(0.6 ATR, 0.5%), which on most altcoins at 15m-1h is also a few percent. Not a conflict.

---

## Part 2. New rules never tested, ranked by testability on crypto

Ranking basis: (a) every parameter is stated or has a single stated alternative, (b) enough events over 20 coins plus fresh coins on DEV/VALIDATION, (c) data we already hold (OHLCV 5m-1d, perp OI where useful), (d) no options leg. The ranking is a judgement; the ranks are OURS.

Common design for every draft below (to be copied into each PRE_REG.md):
- Splits: DEV <= 2023-12-31, VALIDATION >= 2024-01-01. Code committed WITH the PRE_REG this time (the 2026-11-14 review flagged late code commits).
- Fee-net: 12 bp taker round trip (also report 6 bp maker as a non-gating row). R = max(structural stop, 0.5% of price, 0.6 x ATR14 of the signal timeframe). Stop = R. The structural level NK names is used if it is further than the floor; if closer, the floor wins and is reported.
- Phase-specific: phase for each coin-day from data known at the prior close (20-day MA slope with 5-day lag plus ADX14 >= 20 with DI direction, else RANGE; same as the 11-14 studies). Primary rows: long in UP and RANGE-bottom, short in DOWN and RANGE-top, per rule. Control rows (mismatched direction) descriptive only.
- Regime-mix block (UP/DOWN/RANGE share and share above own 200-day SMA) per split, flagged "mixed" if no single phase over 50%.
- Gates (all must hold on VALIDATION): mean net R > 0; trade-level and day-cluster CI low > 0; ex-best-5 > 0; placebo (random same-phase entries) beaten; Benjamini-Hochberg q <= 0.10 across the rule's rows; n >= 200 trade rows per primary cell (else UNDERPOWERED, not PASS).
- Universe: the 20 coins used in NK1-NK6 for DEV/VALIDATION, plus a fresh holdout of 10 coins not yet used and every day since 2026-11-13 run forward once.
- Parameter labels: each parameter marked SOURCED (NK) or OURS in the PRE_REG; any OURS parameter takes exactly one pre-registered value, no grid.

### NKN-01. Convergence breakout long (5GZIshXnxW8)  [testability rank 1]

| Item | Draft |
|---|---|
| Hypothesis | After a fall, price that closes twice above a tight stack of EMAs (SOURCED: stack 20 to 200) on the same timeframe and pulls back to the 20 SMA has positive fee-net expectancy; shorts mirror in DOWN only if the stack is below price. |
| Timeframes | Daily and 4h (OURS; he says day/week/month, and lower for intraday: "same timeframe"). One row per timeframe, no mixing. |
| Phase | Long rows: UP and RANGE. Short rows (mirror): DOWN and RANGE. |
| Stack | EMA20, EMA50, EMA100, EMA200 (OURS: the spoken range is 20 to 200, lengths between are not stated). |
| Tight stack (OURS) | (max EMA - min EMA) / close <= 3% on daily, <= 1.5% on 4h, a single pre-registered value each. |
| Precondition | "Price fell first" (SOURCED): the close 10 bars before the first close above the stack is under the stack (OURS: 10 bars). |
| Trigger | Second consecutive close above the highest EMA of the stack (SOURCED two-close; the count of two for the convergence itself is in an UNQUOTED span, so treated as OURS-informed). |
| Entry | Next bar open (OURS), or limit at SMA20 if touched within 5 bars (SOURCED place, OURS window); both rows. |
| Stop | Under the lowest EMA of the stack (SOURCED), floored by R. |
| Exit | NK says no target and book half: book 50% at 2R (OURS level), trail the rest under the lowest EMA, exit all on two closes back inside the stack (SOURCED two-close). Report the blended R. |
| Kill | If n VAL < 200 per timeframe, report UNDERPOWERED. |
| NK claim to check | "rocket" move after sustained convergence break (5GZIshXnxW8 00:13:46, claim only). |

### NKN-02. Two-close regime switch and 200-average hold (a8RP5ftOfGo, lmhqooBqJWU, PLJda-dtBIc, IjU9PpqvrI8)  [rank 2]

| Item | Draft |
|---|---|
| Hypothesis | Regime flips confirmed by 2 closes (SOURCED) beat 1-close flips as a filter on a plain trend-following long/short: fewer whipsaws, positive fee-net R. |
| Signals | Long regime: two daily closes above SMA20 AND close above SMA200 (SOURCED SMA, 20, 200; AND is OURS). Short regime: two daily closes below SMA20 and a break of SMA200 that holds 10 days (SOURCED 10-12, use 10). |
| Phase | Run inside each phase label as a conditioning variable; also report unconditioned. |
| Entry | Next daily open after the second close. |
| Stop | Two closes against (SOURCED 2-close stop), plus a hard floor R = max(structural swing, 0.5%, 0.6 ATR14 daily); the hard floor is a risk cap, reported separately. |
| Exit | Regime flips back (two closes), time stop 60 days (OURS). |
| Controls | Same rule with a 1-close trigger (the thing NK says traps you), and a random-entry placebo. |
| Test of his claim | 2-close vs 1-close: does the 2-close version have the higher day-cluster CI low? |
| Open | Add a 1h version of the 200-average switch (a8RP5ftOfGo 00:13:14): swing long while 1h close > SMA200(1h). Separate row. |

### NKN-03. Full intraday sequence (3KnEiKNh1pc)  [rank 3]

| Item | Draft |
|---|---|
| Hypothesis | The complete NK sequence (mover scanner, prior-close dip then reclaim, 1h close above prior high, VWAP pullback entry, day-low stop, 1h-close VWAP stop) has positive fee-net expectancy in UP/RANGE phase (longs) and the mirror in DOWN/RANGE. |
| "Day" | UTC day, and a second row for the NY-session day (open 13:30 UTC); crypto has no gap, so "yesterday's close" = previous session close (OURS). |
| Scanner | First-hour return >= +2% (SOURCED), second row >= +1% (SOURCED alternate). Mirror for shorts. |
| Trap | Within first 10 minutes (on 1m bars, OURS; his chart is 2 min) price trades below yesterday's close, then closes back above it before the hour ends (SOURCED). |
| Confirmation | 1h candle closes above yesterday's high within 60 minutes (SOURCED; 90 as second row). |
| Skip | First 1h candle range > 4% (OURS cap; SOURCED only "big"); skip. |
| Index filter | BTC daily close above SMA20 and SMA50 (SOURCED rule, BTC is OURS proxy for Nifty); for BTC itself use its own. |
| HM filter | HM(9,3,21) on the 1h favourable (SOURCED agree; formula SOURCED from class video). |
| Entry | First touch of session VWAP (OURS: session VWAP from the session open) on the candle after confirmation (SOURCED). |
| Stop | Under the session low (SOURCED), floored by R; VWAP stop only on a 1h close below VWAP (SOURCED). |
| Exit | Three exits pre-registered once each: session end, 1h close below VWAP, 2R target (OURS). Primary verdict on the first only. |
| Overlap with earlier tests | NK1 tested first-hour low break + near-VWAP: different trigger. NK5 tested session-open HM: no prior-close trap, no scanner. This is a new combination, NOT a re-run. |

### NKN-04. Higher-timeframe 20 SMA reaction with small-timeframe 20 SMA counter-cross (cX2GZ7B5Gc8)  [rank 6]

| Item | Draft |
|---|---|
| Hypothesis | Price touching the daily or weekly SMA20 after an approach from below (resistance) or above (support), followed by a small-timeframe 20 SMA counter-cross, reverses at positive fee-net expectancy; confluence of daily and weekly SMA20 within 0.5% is stronger. |
| HTF level | Daily SMA20 and weekly SMA20; touch = high/low within 0.3% of the level (OURS). Confluence row: daily and weekly within 0.5% (OURS), SOURCED idea. |
| Trigger | 15m (and 5m as second row) close crosses its own SMA20 against the prior 2-hour move (SOURCED "against the prior move"; 2h window OURS). |
| Confirmation | HM(9,3,21) red line on the side of the trade on 15m (SOURCED gate: red line above = no long). Replaces the options-chart confirmation (not portable). |
| Failed pattern | Optional row: only after a failed 1h range break (SOURCED minimum 1h). |
| Phase | Counter-trend by construction: long in DOWN and RANGE-bottom at support; short in UP and RANGE-top at resistance. This is the one rule where "matched" means counter-trend. Pre-register as such. |
| Stop | Beyond the level touch extreme, floored by R; close-based exit: two closes through the level on 15m (OURS, from the two-close principle). |
| Exit | Half at 2R, runner trailed under each candle low (SOURCED trail in cX2GZ7B5Gc8 00:18:11 is an UNQUOTED span; treat as OURS). |

### NKN-05. HM state claims on the higher timeframe (FzNDQm7wC_s, fZvp72BBmRI, J_BzeTB3PpA, i2bGV_Wo5Yw)  [rank 4]

| Item | Draft |
|---|---|
| Hypothesis A (his claim) | While the weekly HM red line is down (buy state), forward 4-week returns and max drawdown beat the same coins in weekly HM sell state; "the market does not go down." |
| Hypothesis B (gate) | A long entered when the daily price is above SMA20, or daily HM is fully buying with plain RSI(14) above 50, has higher fee-net R than the same entries without the gate. |
| Measurement | Event study first: for each coin-week in the state, forward return and drawdown at 1, 2, 4 weeks; no entries needed. Then the gate as a filter on a simple weekly-close entry, in each phase. |
| HM formula | RSI9, EMA3 and WMA21 of the RSI; the buy state = WMA21 line below/inside the RSI lines (state label OURS-operationalised from SOURCED "red line down"; exact "inside" test pre-registered once). |
| Power | Weekly bars: about 10 years x 30 coins = few thousand coin-weeks, adequate; day-cluster must be week-cluster here (state it). |
| Gates | Same as common, with fees applied on the filtered-entry version only. |

### NKN-06. Pivot R2/R3 (and S2/S3) breakouts (FzNDQm7wC_s, a8RP5ftOfGo)  [rank 5]

| Item | Draft |
|---|---|
| Hypothesis | A daily close above R2 reaches R3 more often than a random same-phase long; three consecutive days near R3 are followed by upside. Mirror for S2/S3 in DOWN. |
| Pivots | Classic daily floor pivots P, R1-R3, S1-S3 computed from the prior day's H/L/C (OURS: the formula is not spoken; the classic floor-pivot set is the lab default, already built for NK2). |
| Trigger | 1h close above R2 (SOURCED idea of R2 break; 1h OURS). Second row: three daily closes within 0.5% under R3 (SOURCED "three days", band OURS). |
| Entry | Next bar open. |
| Target | R3 (SOURCED "going to R3") as the tested exit; stop = R-multiple floor (OURS), or the R2 level re-lost on a close (SOURCED close-based stop spirit). |
| Phase | Long in UP and RANGE; short mirror in DOWN. |
| Note | NK2 tested P/S1/R1 only, 6102 VAL trades, FAIL. R2/R3 are rarer, so n will be smaller; UNDERPOWERED is a likely outcome and must not be read as FAIL. |

### NKN-07. Reversal checklist as a regime detector (ysq6x0eCFvI)  [rank 7]

| Item | Draft |
|---|---|
| Hypothesis | Any one of the SOURCED reversal triggers marks a bear-to-bull change with positive forward return over the next 4-12 weeks. |
| Triggers | (1) weekly close above daily-chart SMA200; (2) daily RSI(14) above 50 held 7 days; (3) weekly HM buy plus a weekly close above SMA20; (4) daily OBV above zero for 5 days (OURS count; "sustained" is the quote). (A weekly engulfing candle covering 3-4 prior weeks is in the extract but its span is NOT FOUND: excluded.) |
| Test | First-signal-after-bear-state events per coin; forward 1/4/12 week returns vs placebo dates. This produces few events on BTC alone (flagged as a known limit: "BTC alone cannot power 1h+"); use 30 coins. |
| Use | If it works, it replaces the 20-day-slope phase label in later tests. |

### NKN-08. Master-candle breakout (B7iGQef_z6I)  [rank 8]

| Item | Draft |
|---|---|
| Hypothesis | After a master candle (body >= 2 x ATR14, each wick <= 20% of range: OURS definitions, since "big" and "small wicks" are not numbers), if price stays inside its range for 3-4 candles, the close beyond its high or low continues at positive fee-net R. |
| TFs | 1h, 4h. Phase: matched direction. |
| Stop | Other side of the master candle, floored by R. |
| Exit | 2R and master-candle-height projection, one row each. |

### NKN-09. Long-leg doji at RSI 30/70 (i2bGV_Wo5Yw)  [rank 9]

| Item | Draft |
|---|---|
| Hypothesis | A doji with body <= 5% of range (SOURCED 5%) at RSI(14) < 30 or > 70 (SOURCED zone), followed by a close beyond the doji high/low, reverses at positive fee-net R. |
| TFs | 1h, 4h, 1d. |
| Phase | Counter-trend at extremes: long in DOWN/RANGE, short in UP/RANGE. |
| Stop | Beyond the doji extreme floored by R. Note existing RSI-extreme studies (edge-rsi-extreme-confirm) failed; this adds only the doji filter, so expect a low prior. |

### NKN-10. HM overheat and next-session read (MLrMJ7rlL4U, lmhqooBqJWU)  [rank 10]

| Item | Draft |
|---|---|
| Hypothesis | (a) HM-RSI above 86 (SOURCED, caption-unconfirmed) marks poor long entries. (b) HM state on the last 5/10/15 min of a session predicts the next session's open direction (SOURCED idea in lmhqooBqJWU 00:08:43; the span is UNQUOTED, NOT FOUND in the worker check). |
| Crypto port | Next-session = next 8h or next UTC day, since crypto has no gap (OURS). |
| Warning | His own caveat in the extract is that it is not certain; it is a low-prior rule. |

Ranks 1-5 are recommended for registration first: NKN-01 (clear and mechanical), NKN-02 (a close-based stop and 2-close trend filter, both listed open in `NK_TESTS_SYNTHESIS_1114.md`), NKN-03 (the only fully specified intraday set, with stated parameters), NKN-05 (his strongest claim, cheap event study), NKN-06 (code mostly exists from NK2).

---

## Part 3. Equity/options-only rules (not testable on crypto data we hold)

| Rule | Why not testable | Evidence (video, time) |
|---|---|---|
| Hedge 23 (H23) expiry-day buyer: buy call and put when the combined premium decays to 40-50 (Nifty) or 80-100 (Sensex), stop at sum below 20 (Nifty) / 35 (Sensex), time stop | Needs weekly index option chains, expiry calendar, premium sums. No option chain in our pipeline | «50 पॉइंट ऊपर 50 पॉइंट नीचे कि कॉल और पुट को हम बाइंग करेंगे» (ovQp5I2ZIKs 00:18:38); «स्टॉप लॉस रखते हैं 20 के नीचे» (ovQp5I2ZIKs 00:20:11); «सेचुरेशन जोन होती है ससेक्स में 80 टू 100 का» (8TQnHHwV_IU 00:13:19) |
| H23 expiry-day seller: short ATM strangle at 9:35-9:40, SL-M at sold premium plus 5-10, flat by 12:00 | Needs option quotes; depends on NSE/BSE expiry time-of-day | «115 लगा दीजिए, 120 लगा दीजिए। दोनों साइड में» (ovQp5I2ZIKs 00:06:52); «12:00 बजे के बाद आपको नहीं करनी चाहिए» (ovQp5I2ZIKs 00:08:15); «मॉर्निंग में प्रीमियम ज्यादा मिलेगा» (kmYXItkzyv8 00:03:00) |
| H23 timing and VIX-linked sums (1:00-1:30 pm buy, VIX 12 split) | VIX-dependent premium thresholds, NSE hours | «उन दोनों को खरीदने का जो टाइमिंग है हमेशा प्रयास करना ह» (h9Ki-YvpS1k 00:11:10); «10 बार में सिक्स बार ऐसा होता होगा» (h9Ki-YvpS1k 00:10:25) |
| H23 permanent zones (Sensex 90-105, Nifty 30-35 while lot size is 65) | Lot-size and premium specific | «टू थ्री काफी इफेक्टिव है उसका एक लेवल दे दिया गया है परमानेंट ल» (JMyLmFeMAUA 00:05:40) |
| Stone Age (SA) deep option 70-100 premium, next-month expiry, option above its daily 20 SMA | Option premium series, lot size and monthly expiry | «एंटर तो आप लोअर टाइम फ्रेम पर करो बट एग्जिट आप हायर टाइम» (zqpI45bTiY4 00:02:34) and the premium zone span (zqpI45bTiY4 00:08:26); the exit-on-higher-TF idea is portable as a design hint, the rest is not |
| Strike selection: near-OTM delta 0.3-0.4, ATM/ITM in expiry week | Options only | «वो नियर ओटीएम हो... डेल्टा 0.3 0.4» (3KnEiKNh1pc 00:05:19) |
| Option-chart confirmation: call must break under its own 20 SMA while the put breaks above, on next week's expiry strikes | Needs paired option charts | «जब इसने ब्रेक किया है नीचे की तरफ तो पुट को नीचे से ऊपर की ओर» (cX2GZ7B5Gc8 00:15:15) |
| Option stop on spot, not on premium | Not applicable: our trades are spot or perp | «बाइंग में आप ऑप्शन पे स्टॉप लॉस नहीं दे सकते हो» (JMyLmFeMAUA 00:01:12) |
| Naked option buying after the 10th of the month is risky (theta) | Option decay | «10 तारीख के बाद नेकेड जो बाइंग होती है» (JMyLmFeMAUA 00:02:04, span NOT FOUND in worker check; paraphrase only) |
| Gap-based rules (gap up from support is strong, do not sell first hour; big gap needs one-sided trade) | Crypto trades 24/7 with no overnight gap | «सपोर्ट के पास कोई शॉर्ट का ट्रेड हम लोग नहीं लेते हैं» (ysq6x0eCFvI 00:03:00) is portable; the gap statements are not (fZvp72BBmRI 00:02:03-00:02:56) |
| Equity portfolio rules (lot sizing in lakhs, long-term ITM put hedge, "50 and 200 DMA" portfolio hedge, BTST/STBT) | Equity portfolio structure, India-specific | «हिलेगा मिलेगा लास्ट का 5 10 15 मिनट का देख लो» (6zDpjsesOyw 00:33:36) is portable as an idea (NKN-10); the rest is not |
| Yearly RSI near 90 and the 2008 match for Nifty | n = 1 episode on an index, no crypto equivalent | «इयरली टाइम फ्रेम का वो 90 के पास है» (sbMyohOXRqE 00:02:07) |
| Specific Nifty/Sensex price levels (23,200; 24,800; 25,491; 27,746) | Index levels, not rules | dm7x3ZY9K9M, a8RP5ftOfGo, h9Ki-YvpS1k |
| Career, psychology and sign-up videos (I4rHEfRhEWM, Xz61miXrOcY, RZzKYqTra3Y, UCGH6r1FOXw, VRUb4BFk2Oo, HJpxOMfLN7o) | No trading rules | worker notes in the five extracts |

---

## Counts

- SOURCED parameter corrections to our tested guesses: 15 (list in the table below).
- Our guess confirmed: HM RSI9 with EMA3/WMA21 and 50/50 zone (class video, not re-seen in the 47 here); RSI 30/70 (guess was 35/65 in code only).

| # | Correction | Was | Now (SOURCED) | Evidence |
|---|---|---|---|---|
| 1 | HM read as state, not cross | cross test (NK4) | red line position state; three states | B7iGQef_z6I 00:03:03, 00:03:22 |
| 2 | HM role | trigger | confirmation gate | cX2GZ7B5Gc8 00:16:00 |
| 3 | HM timeframe pairing | 15m only | 1h agreement plus 5-10m entry; higher TF state | 3KnEiKNh1pc 00:18:24 |
| 4 | Plain RSI for the 50 gate | RSI9 only | RSI(14) above 50 on daily | fZvp72BBmRI 00:04:58 |
| 5 | HM overheat cap | none | RSI above 86 no long (caption unconfirmed) | MLrMJ7rlL4U 00:16:38 |
| 6 | RSI levels | 35/65 (NK5 code) | 30/70, and wait for recovery above 30 | 4-OtV5JVM4g 00:06:52 |
| 7 | First-hour range | 3 bars | one 1h candle (60 or 90 min); 45 min alternate | 3KnEiKNh1pc 00:08:58, 8TQnHHwV_IU 00:07:09 |
| 8 | Break test | touch | close outside the range | 8TQnHHwV_IU 00:07:09 |
| 9 | Pivot set | P, S1, R1 | add R2/R3 (and S2/S3 per earlier notes) | FzNDQm7wC_s 00:09:44 |
| 10 | Stop basis | intraday touch | close basis or 1h sustain, whichever first | dm7x3ZY9K9M 00:08:18 |
| 11 | VWAP stop | intraday | 1h close only | 3KnEiKNh1pc 00:25:50 |
| 12 | Stop level for the VWAP entry | volatility stop | day low on spot (our floor stays) | 3KnEiKNh1pc 00:10:48 |
| 13 | Confirmation count | one bar | two closes | a8RP5ftOfGo 00:08:50; lmhqooBqJWU 00:07:26 |
| 14 | Index trend filter | 20-day slope plus ADX | close above daily 20 and 50 SMA | 3KnEiKNh1pc 00:15:29 |
| 15 | Mover and candle-size filters | none | first-hour move >= 2% (1%), skip big first 1h candle | 3KnEiKNh1pc 00:09:15, 00:12:01 |

## Quote audit

All quotes in this file were re-checked after writing (script outside the repo; method: both sides normalised, punctuation and nukta removed, "..." fragments in order, matched against the cited video's `_timed.txt` and a time window of 120 s around the cited timestamp). The result line is appended below by the shipper.
