# Malkan Hindi rows MAL-1,3,4,6,7,8,9: independent read of the Hindi ASR

Card `malkan-hindi-rows-gpt-read` (audit, report only; no extract, spec or code edited). Sources, read only:
`raw_transcripts_canonical/W1HrDl70Lhk_hi_raw.txt` (call **W**) and `raw_transcripts_canonical/A-CQiV_UFB4_hi_raw.txt` (call **A**). No VALIDATION / HOLDOUT data read.
Renderings are mine from the Hindi; "reconstruction" = inference from the neighbouring lines, not a quote. Status per field: STATED / NOT STATED / UNREADABLE.

## What the two files are

- **W** (Trader Insights, 2021) is not Hindi prose. It is auto-ASR of Hindi+English code-mix, and most of the English phrases are
  mis-heard into Hindi-script nonsense (`W:134-137`, `W:255`, `W:290`). The English "translation" in SETUP_SUMMARY is a
  second machine pass over that already broken ASR.
- **A** (Malkan himself, 2025) is the same code-mix but the ASR is largely clean (`A:127-312` reads as sentences).
- Recovery key inside W: the speaker repeats his phrases and one repetition is often readable. "sixty" = `सिक्सटी` `W:155`, `सिकटी` `W:215`, `rs.60` `W:185,345`.
  "stop loss will be below the candle" = `W:192-193`; "...below the lowest" = `W:221-222`; "...below low of the candle" = `W:263-264`.

## Per row

### MAL-1 (long entry type 1) `W:121-137`
| field | Hindi (file:line) | my English | status |
|---|---|---|---|
| condition | `फर्स्ट एडिशन द आरएसएस और वीकली एंड मंथली स्टॉक में है कि वीकली ओर मंथली ... 100 वीकली ओर मंथली आरएसएस के ऊपर होना चाहिए` `W:124-127` | first condition: weekly and monthly RSI both above the level | STATED, level mis-heard "100". Reconstruction 60: the same condition is spoken `rs.60 के ऊपर होना चाहिए` `W:185` and `W:333-336` ("both above, then the zone turns coloured") |
| entry | `सो एंट्री विल बेटर हाफ ग्रीन कैंडल` `W:132-133` | entry on the (high of the) green candle | UNREADABLE verbatim ("better half"); reconstruction entry above the signal candle. Readable twins: `एंट्री अबोध यह कैंडल` `W:192` (entry above this candle), `मैं तो अभी इसका हाई पर` `W:220` (entry on its high) |
| stop | `एंड स्टॉप लॉस विल बी ब्लॉक प्रिंटेड नॉट रिटारडेड चिल्ड्रन` `W:133-134` | "stop loss will be [noise]" | UNREADABLE on this line; **the same rule is STATED three times nearby**: `W:192-193` below the candle, `W:221-222` below the lowest, `W:263-264` below the low of the candle |
| target | `रिक्तियों के विरुद्ध वीडियो टारगेट जैसे ही सब्सक्राइब करें` `W:135-137` | noise (the YouTube "subscribe" ASR bleeds in) | UNREADABLE; real target talk is `W:159-160` and `W:168` (see MAL-3) |

### MAL-3 (short mirror of entry type 2) `W:161-168`
| field | Hindi | my English | status |
|---|---|---|---|
| condition | `सिमिलरली फॉर सेलिब्रिटी वीकली एंड मंथली आरएस 850 सिक्यूरिटी सिस्टम कॉफी लाइन फ्रॉम बेलो पॉवर्टी लाइन को नीचे क्रॉस करके वापस ऊपर जाकर वापस रुणिचे रहा है` `W:161-165` | "similarly for [sell side], weekly and monthly RSI ... [60] line ... crossing down, going back up and coming back down" | partly READABLE: "similarly" + "sell" (सेलिब्रिटी = "sell side") + the 60 line + cross / retest / reject. Exact wording UNREADABLE. It mirrors the buy sentence `W:151-157` (cross 60 from below, take support at 60, go up) |
| entry | none after `W:165` | | NOT STATED (only the "similarly") |
| stop | none | | NOT STATED |
| target | `हम रॉ टेस्ट वन रखते हैं` `W:168`; buy-side lead-in `टारगेट यहां कितना रखना है यह बताया है उन्होंने स्वयं रॉ टेस्ट वन रखते हैं` `W:159-160` | "how much target to keep here, he has told; we keep [raw test one]" | UNREADABLE. Two facts survive: the presenter says the target is Malkan's relayed rule, and that he will test it (`W:148-151`, `W:170-172` "numbers in the next video"). The value is not recoverable ("raw test one" could be "1R" or "RR 1", a guess) |

### MAL-4 (short examples) `W:279-313`
| field | Hindi | my English | status |
|---|---|---|---|
| condition | `वीकली ओर मंथली में दोनों पार्टी के नीचे आ गया` `W:280-281`; `दोनों ही टीमों के नीचे` `W:284` | weekly and monthly both [RSI] came below [60] | STATED apart from the level word ("party/teams" = 60, cf. `W:345` `दोनों rs.60 के नीचे`) |
| entry | `सोनिक चैनल पर हम सेल करेंगे` `W:297` | we will sell on the [?] candle | UNREADABLE noun ("sonic channel"); reconstruction sell on a (red) candle. It follows `W:294-296` RSI "coming down through the 60 line" (STATED-ish) |
| stop | `स्टॉप लॉस विल बी या बुद्ध हाय` `W:290`; `स्टॉपलॉस ...` `W:299` | stop loss will be [above the high] | UNREADABLE verbatim; "या बुद्ध हाय" = "above the high" is the natural reading (mirror of "below the low") but the words are not clean. Not a quote |
| target | none | | NOT STATED |
| context | `सेल में तो बहुत मैथिली दिल्ली टाइम प्रेम में सेल में पॉजिटिव बहुत लिमिटेड लग रहा है` `W:310-312` | "in sell, on monthly/daily time frame, the positives look very limited" | readable: his scan found few sell examples. Not a rule |

### MAL-6 (long example, "target 2068") `W:254-265`
| field | Hindi | my English | status |
|---|---|---|---|
| stop | `बहुत ही अ को स्टॉप लॉस विल बी दिलों दलों के पेंडल` `W:254-255`, then `स्टॉप लॉस विल बी विरुद्ध लो फिर कैंडल` `W:262-263` | "stop loss will be [noise]", then "stop loss will be below the low of the candle" | first UNREADABLE; second **STATED** (below the low of the entry candle) |
| target | `टारगेट 2068 सौर हीटर होता है लुट चले जाइए` `W:257-258` | "target 2068 [noise: ?hits / exit]" | the digits 2068 are in the ASR; their meaning is **UNREADABLE**. `W:240` `इसलिए हमको 1.5 है` ("that is why we have 1.5") is a second bare number in the same passage. A price 2068 on a stock chart is a guess; so is a ratio |
| entry | none | | NOT STATED (the nearby `W:260-261` `यहां पर इसने इसको टेस्ट करके ऊपर गया` = "here it tested it and went up" is the chart observation, STATED) |

### MAL-7 (PRD buy in an uptrend) `A:133-165`
- Condition/entry STATED, clear: `तो कभी भी अप ट्रेंड देखोगे तो ... पॉजिटिव रिवर्स डायवर्जेंस ढूंढना है` `A:133-135`; `व्हाट इज योर सिग्नल टू बाय ... वी कैप्चर ऑन पीआरडी` `A:159-161` (price higher bottom, RSI lower bottom, in an uptrend, `A:127-130,162-164`). Rendering in SETUP_SUMMARY is faithful.
- Stop: NOT STATED. Target: NOT STATED. (The only "entry exit stop loss target" in the file is the sales pitch for his paid course, `A:334-335`: it says those details exist elsewhere.)
- Timeframe STATED: `सारे टाइम फ्रेम पर दिखते हैं ... ट्रेड ... ज्यादातर डेली ... बहुत-बहुत तो वीकली` `A:262-265`. Monthly is "very difficult" to trade `A:265-267`. NB: this line answers "where do PRD/NRD show", i.e. it applies to PRD and NRD equally.
- Also STATED, not in the row: PRD beats the ordinary divergence when both show, `पीआरडी को पहले प्रेफरेंस देना है` `A:217-218`, but when both exist "which one to trade depends on your judgement" `A:222-225`.

### MAL-8 (PRD at the start of an uptrend) `A:170-176`
- STATED, clear: `ट्रेंड शुरू कब हुआ यहां से हुआ 60 के ऊपर ... उसके बाद तुरंत पीआरडी मिल गया दैट इज द बेस्ट अपॉर्चुनिटी टू हैव अ वेरी लो रिस्क बाय ट्रेड` `A:172-176`. **The trend start is defined as RSI crossing above 60** (the SETUP_SUMMARY quote has it, the row's field list does not isolate it as a rule).
- Stop, target, entry trigger beyond "the PRD": NOT STATED.

### MAL-9 (NRD sell in a downtrend) `A:234-278,292-293`
- STATED, clear: `ये कहां दिखेगा आपको डाउन ट्रेंड में ... डाउन ट्रेंड जो ऑलरेडी चल रहा है उसी के अंदर एनआरडी दिखेगा` `A:243-245`; `नया लो एंड देन एनआरडी यू गेट अ सेल सिग्नल` `A:277-278`; definition `ए और बी लोअर है बट आर एसआई हायर` `A:252`; repeated `A:292-293`.
- Stop, target: NOT STATED.

## Is the 5-star / 7-star rule in his words?

- **W (title "5 Star RSI Strategy"): NO.** No `स्टार`/`फाइव`/`सेवन`/5/7 in the body (only `W:85` `बिफोर स्टार्टिंग`). The video is the weekly+monthly-above-60 system; "5 star" is only in the title.
- **A: grades YES, conditions NO.** `उसमें होता है फाइव स्टार रिवर्स डायवर्जेंस सेवन स्टार रिवर्स डायवर्जेंस मतलब सारे कंडीशंस मैच हो गए तो वो सेवन स्टार हो जाएगा` `A:298-301` (all conditions met = seven star). Claimed hit rates: seven star "almost 80-90 %" `A:301-303`, five star "60-70 %" `A:304-305`, three star "loose, may or may not work" `A:305-307`. Conditions withheld: `देयर आर सर्टेन कंडीशंस बट आई थिंक इतना कुछ एक साथ में अगर दे दूंगा तो यू विल फील ओवरवेल्म` `A:307-309` (there are certain conditions, giving them all at once would overwhelm). Applies to reverse divergence only (`A:296-299`).
- The 80-90 / 60-70 % are his assertions, with no sample, so SOURCED claims, not evidence.

## Findings

| sev | where | what | evidence | proposed fix |
|---|---|---|---|---|
| MED | SETUP_SUMMARY MAL-1 / MAL-6 stop field; extract `S-W1HrDl70Lhk-01`, `-06` | stop labelled GARBLED, but the same speaker states the long stop readably in this passage: below the low of the entry candle. The summary understates STATED content, and MAL-5's "below the lowest" row is the same rule | `W:192-193`, `W:221-222`, `W:263-264` | relabel stop as "below the candle low (reconstruction from repeated readable lines)", keep class INFERRED not CLEAR (which low, buffer, not stated) |
| MED | MAL-1 condition quote "above 100" | RSI cannot exceed 100; 60 is stated on the same topic. Extract already infers 60 (`extract_W1HrDl70Lhk.md:157`, `:321`) but the summary row prints 100 unflagged | `W:185`, `W:333-336`, `W:345` | print "(60)" with an INFERRED tag in the row |
| MED | MAL-6 target "2068" | number is in the ASR but not shown to be a price or a unit; `W:240` has an unexplained 1.5 beside it. Must not feed any encoding as a target | `W:240,257-258` | keep as unresolved; do not encode |
| LOW | MAL-3 / MAL-4 target "raw test one" | UNREADABLE; value cannot be 1R by reading, only by guess | `W:159-160,168` | leave NOT STATED |
| LOW | MAL-4 stop "या बुद्ध हाय" | "above the high" is plausible but a guess | `W:290` | INFERRED-low only |
| LOW | MAL-7 timeframe line | the daily/weekly sentence answers where PRD **and** NRD trade, not PRD alone | `A:259-266` | none needed; row 9 reuses it correctly |
| LOW | 5/7-star | W video does not state it (title only); A states grades and rates but withholds conditions, so no encodable 5/7-star rule exists in either file; the only conditions are MAL-19 (Wvq1TZh8aF0, not read here) | see above | keep MAL-20 NOT STATED; no new card |

No HIGH finding, so no follow-up cards (`tasks.py new` not run). NOT_IN_DATA: chart frames (which candle, which low, what 2068 and 1.5 measure) are not in the transcripts.

## What was checked

All 7 rows' Hindi quotes located in the raw files with line numbers; every row's entry/stop/target/context field compared; `W` fully read (lines 1-372), `A:126-346` read, `A:1-125` skimmed via search (grade terms, PRD/NRD). The SETUP_SUMMARY quotes are verbatim from the files, no transcription error found. The English glosses are the weak part, as the card assumed.

**Verdict: SOUND** (the GARBLED / NOT STATED labels are honest and nowhere overstated; the errors are understatement of readable stop wording and an unflagged "100").
