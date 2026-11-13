# NK extract batch 0: quote verification

Source checked: nk55_extract_b0.md (73 quoted spans in «…»). Transcripts: F:\MTS\data_cache\youtube\nk\<id>_timed.txt. Video for each quote = its section heading; table rows (HM facts) checked against all 11 files.

verify_extract_quotes.py was not used: it expects `> "quote"` blocks with `Source GPS` tags and raw_transcripts_canonical/ at repo root; this extract uses «…» spans. Matcher: Devanagari-aware normalisation (punctuation, whitespace, timestamps dropped; immediate repeats collapsed), "..." / … fragments must occur in order.

**Result: 57 VERIFIED, 16 NOT FOUND (of 73).**

## Output
```
  1 L14   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | वो ऑप्शन ज्यादा बड़ा नहीं हो। मतलब एटीएम नहीं हो, आईटीएम नहीं हो, वो न
  2 L17   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | लेकिन अगर लास्ट वीक है तो वहां पे एटीएम लेंगे या आईटीएम लेंगे।
  3 L18   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | कोई स्टॉक अगर 5000 की चल रही है तो 5100 5200 की ऑप्शन लेंगे। कोई स्टॉक
  4 L20   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | फर्स्ट 5 टू 10 मिनट में कल की जो क्लोजिंग प्राइस थी उसके नीचे प्राइस च
  5 L21   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | ये ब्रेक करना आवश्यक है।
  6 L23   NOT FOUND 3KnEiKNh1pc  3KnEiKNh1pc          not in 3KnEiKNh1pc | कल की हाई के वन आवर के ऊपर वन आवर की कैंडल क्लोज करो।
  7 L25   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | आपको ऐसे स्टॉक की तलाश करनी है जो इंट्राडे में मॉर्निंग में फर्स्ट वन 
  8 L27   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | वीवप के पास जब प्राइस वीवप के पास आएगी तो वहां पे हमारी एंट्री बनेगी
  9 L30   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | हमारा जो एसएल होगा उस दिन का लो के नीचे होगा लेकिन वो एसएल स्पॉट वाइज 
 10 L31   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | ऑप्शन बाइंग में 50% का एसएल होता है।
 11 L33   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | वीवप को आप वन आवर का यूज़ कीजिए कि 1 आवर के नीचे आके क्लोज करो तब माने
 12 L35   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | पहली वन आवर की जो कैंडल है वह काफी बड़ी नहीं होनी चाहिए... अगर ऐसा है 
 13 L37   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | इंट्राडे में बस 30 मिनट का लो और हाई में इंट्राडे का हाई। ब्रेक करो।
 14 L38   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | यह ट्रेडेबल नहीं है।
 15 L40   NOT FOUND 3KnEiKNh1pc  3KnEiKNh1pc          not in 3KnEiKNh1pc | वन आवर पे हिलेगा मिलेगा आपके फेवर में जरूर होना चाहिए।... एक एडिशनल कन
 16 L42   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | निफ्टी भी बाइंग में जाने का मतलब 20 और 50 एसएमएस से ऊपर ट्रेड कर रहा ह
 17 L44   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | अगर आपने रख लिया जनरली इंट्राडे में बुक कर लेनी है।
 18 L47   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | मोर देन मेरी बातें 80% सही हो तभी आप उस बैक टेस्ट के बाद आगे अपना पैसा
 19 L48   VERIFIED  3KnEiKNh1pc  3KnEiKNh1pc           | जल्दी का काम शैतान का होता है। कोई जल्दबाजी नहीं करेंगे। आपके पास वन आ
 20 L55   VERIFIED  5GZIshXnxW8  5GZIshXnxW8           | मैं 20 से लेकर 200 तक के ईएमए को जोड़ देता हूं। तो एक कन्वर्ज बन जाता 
 21 L57   VERIFIED  5GZIshXnxW8  5GZIshXnxW8           | साइडवेज मार्केट में जब रहेगा तो ये काफी पतला रहेगा।
 22 L58   NOT FOUND 5GZIshXnxW8  5GZIshXnxW8          not in 5GZIshXnxW8 | जब... एवरेज एक जगह पे आ जाता हो तो प्राइस वहां से एक बड़ी मूवमेंट लेती
 23 L60   NOT FOUND 5GZIshXnxW8  5GZIshXnxW8          not in 5GZIshXnxW8 | वो प्राइस पहले गिरा हो और गिरने के बाद वो दोबारा से कन्वर्जेंस के ऊपर 
 24 L64   VERIFIED  5GZIshXnxW8  5GZIshXnxW8           | एसएल होगा इसके नीचे जो सबसे लोअर लाइन है
 25 L65   VERIFIED  5GZIshXnxW8  5GZIshXnxW8           | कोई टारगेट नहीं होता है मार्केट में। आप 50% बुक कर लीजिएगा। 50% आप राइ
 26 L67   VERIFIED  5GZIshXnxW8  5GZIshXnxW8           | एवरी डीपी बाय ही करना है, सेल नहीं करना है
 27 L68   NOT FOUND 5GZIshXnxW8  5GZIshXnxW8          not in 5GZIshXnxW8 | एक जगह प्राइस आनी ही चाहिए... जहां डिस्टेंस होगा कन्वर्ज नहीं माना जाए
 28 L70   VERIFIED  5GZIshXnxW8  5GZIshXnxW8           | अगर आप पोजीशनल लिए हो और हिलेगा मिलेगा में सेल आ जाता है तो एक बार ट्र
 29 L72   VERIFIED  5GZIshXnxW8  5GZIshXnxW8           | एवरेज बेस्ट सबसे अच्छा है... प्राइस एक्शन में भी आपके साथ धोखा हो सकती
 30 L78   NOT FOUND dm7x3ZY9K9M  dm7x3ZY9K9M          not in dm7x3ZY9K9M | वीकली ट्रेंड तो आवरली टाइम फ्रेम पे... बिल्कुल नहीं। आपको जाना है डे ट
 31 L80   VERIFIED  dm7x3ZY9K9M  dm7x3ZY9K9M           | डे टाइम फ्रेम पे जो रखेंगे क्लोजिंग बेसिस रखिएगा या कम से कम उसके ऊपर 
 32 L82   VERIFIED  dm7x3ZY9K9M  dm7x3ZY9K9M           | बढ़ते हुए चार्ट में अगर लो ब्रेक हो जाए तभी हम सेल का ट्रेड लेंगे डे ट
 33 L84   VERIFIED  dm7x3ZY9K9M  dm7x3ZY9K9M           | कैंडल के तीन पार्ट होते हैं... प्राइस की नेचर होती है कि वो एक क्वार्ट
 34 L88   VERIFIED  dm7x3ZY9K9M  dm7x3ZY9K9M           | हमें उस स्पॉट के प्राइस से या फ्यूचर के प्राइस से ट्रेड करनी है डे टाइ
 35 L89   NOT FOUND dm7x3ZY9K9M  dm7x3ZY9K9M          not in dm7x3ZY9K9M | सेलर हैं तो स्पॉट पे... एसएल इसके ऊपर होगी
 36 L91   VERIFIED  dm7x3ZY9K9M  dm7x3ZY9K9M           | कोई ओपनिंग में जंप ना लगाए। बाजार को बोलने दीजिए
 37 L92   VERIFIED  dm7x3ZY9K9M  dm7x3ZY9K9M           | बाय की साइड में मुझे डर लगता है... फटाफट भागेंगे छोटे-छोटे प्रॉफिट बुक
 38 L93   NOT FOUND dm7x3ZY9K9M  dm7x3ZY9K9M          not in dm7x3ZY9K9M | आरएसआई ओवरबाउट या ओवरसोल्ड हो गई हो तो वहां पे इस चीज को थोड़ा सा इग्न
 39 L95   VERIFIED  dm7x3ZY9K9M  dm7x3ZY9K9M           | एसएल बड़ा छोटा से मतलब नहीं है। एसएल सही होने से मतलब है।
 40 L96   VERIFIED  dm7x3ZY9K9M  dm7x3ZY9K9M           | मोर देन 80% केस में ये चीजें आपके फेवर में होगी
 41 L96   VERIFIED  dm7x3ZY9K9M  dm7x3ZY9K9M           | बैक टेस्ट के बाद... सारी चीजें तुक्का है
 42 L102  VERIFIED  J_BzeTB3PpA  J_BzeTB3PpA           | हमें इस रिवर्सल को ट्रेड करना है ना कि इस मेन ट्रेड को करना है।
 43 L103  NOT FOUND J_BzeTB3PpA  J_BzeTB3PpA          not in J_BzeTB3PpA | आईटीएम ऑप्शन के वॉल्यूम पर नजर रखो
 44 L103  NOT FOUND J_BzeTB3PpA  J_BzeTB3PpA          not in J_BzeTB3PpA | जब मार्केट सपोर्ट और रेजिस्टेंस के पास हो... या एक्सपायरी का दिन है
 45 L104  VERIFIED  J_BzeTB3PpA  J_BzeTB3PpA           | महीने के चार पांच अच्छे ट्रेड ढूंढने हैं।
 46 L110  VERIFIED  J_BzeTB3PpA  J_BzeTB3PpA           | एक ही न्यूज़ के कारण बाजार दो बार नहीं गिरती है।
 47 L115  VERIFIED  i2bGV_Wo5Yw  i2bGV_Wo5Yw           | पूरी बॉडी का 5% से ज्यादा नहीं होगा
 48 L117  NOT FOUND i2bGV_Wo5Yw  i2bGV_Wo5Yw          not in i2bGV_Wo5Yw | डोजी यूजफुल वहीं पर हैं जब बाजार में एक अच्छी खासी अपसाइड के बाद अगर ल
 49 L119  VERIFIED  i2bGV_Wo5Yw  i2bGV_Wo5Yw           | जब तक कि कोई बड़ी सी कैंडल जो भी हाई डोजी लगी है उसके ऊपर क्लोज ना कर 
 50 L120  NOT FOUND i2bGV_Wo5Yw  i2bGV_Wo5Yw          not in i2bGV_Wo5Yw | जितने भी सिंगल कैंडल पैटर्न है उनमें वो कैंडल ज्यादा नहीं होता है। उसक
 51 L121  VERIFIED  i2bGV_Wo5Yw  i2bGV_Wo5Yw           | लॉन्ग लेग डोजी का मतलब... वेटिंग।
 52 L122  NOT FOUND i2bGV_Wo5Yw  i2bGV_Wo5Yw          not in i2bGV_Wo5Yw | Verify, back-test.
 53 L130  VERIFIED  B7iGQef_z6I  B7iGQef_z6I           | मास्टर कैंडल वो होती है जिसमें कि वीक हो सकता है... वो पूंछ बॉडी से छो
 54 L130  NOT FOUND B7iGQef_z6I  B7iGQef_z6I          not in B7iGQef_z6I | उसके अंदर तीन चार कैंडलें ट्रेड करेगी और उसके बाद ब्रेकआउट और ब्रेकडाउ
 55 L133  VERIFIED  B7iGQef_z6I  B7iGQef_z6I           | हिलेगा मिलेगा... बाइंग में नहीं चल रही है। वो बता रहा है कि प्राइस स्ट
 56 L140  VERIFIED  t1b_1h2QMXw  t1b_1h2QMXw           | मार्केट के ट्रेंड के अपोजिट नहीं जाना है... हर एवरी रेजिस्टेंस पर निकल
 57 L143  VERIFIED  t1b_1h2QMXw  t1b_1h2QMXw           | इंट्राडे ट्रेंड किस साइड से डिफाइन होगा 10 टू 15 मिनट 30 मिनट के चार्ट
 58 L152  VERIFIED  lmhqooBqJWU  lmhqooBqJWU           | हिलेगा मिलेगा ने बोल दिया कि हम तो सेल में हैं... रेड लाइन जा रहा है ल
 59 L153  VERIFIED  lmhqooBqJWU  lmhqooBqJWU           | जब तक ये 50 एसएमए से ऊपर नहीं आ जाए। स्विंग में हम बाइंग नहीं करते हैं
 60 L154  VERIFIED  lmhqooBqJWU  lmhqooBqJWU           | दो क्लोज दो क्लोज हो जाएगी तो हमारा फिर से एसएल हो जाएगा शॉर्ट के लिए
 61 L156  VERIFIED  lmhqooBqJWU  lmhqooBqJWU           | पुराने 5 मिनट 10 मिनट 15 मिनट में अगर हिलेगा मिलेगा सिस्टम बाइंग बोल क
 62 L157  NOT FOUND lmhqooBqJWU  lmhqooBqJWU          not in lmhqooBqJWU | जब भी 20 से कर्व मुड़ जाता है ना तो... छोटे टाइम फ्रेम पे स्विंग में म
 63 L158  VERIFIED  lmhqooBqJWU  lmhqooBqJWU           | इंट्राडे में जैसा मार्केट सजेस्ट करेगा पिछले दिन के हाई लो को मार के स
 64 L160  VERIFIED  lmhqooBqJWU  lmhqooBqJWU           | ये वाली रेड लाइन के ऊपर 50 एसएमए के ऊपर आने का वेट करते हैं।... रेड ला
 65 L161  NOT FOUND lmhqooBqJWU  lmhqooBqJWU          not in lmhqooBqJWU | जल्दी का काम शैतान का होता है। हमें जंपिंग बेबी नहीं बनना है।
 66 L167  VERIFIED  table        B7iGQef_z6I           | सेल में चलने के लिए उसको 50 से नीचे जाना चाहिए
 67 L167  VERIFIED  table        lmhqooBqJWU           | ये 50 के नीचे जैसे ही... सेल चला जाएगा
 68 L168  VERIFIED  table        i2bGV_Wo5Yw           | रेड लाइन जब तक ऊपर है डे टाइम फ्रेम में बाजार ऊपर नहीं जाएगी... इस रेड
 69 L169  VERIFIED  table        i2bGV_Wo5Yw           | जब ये आरएसआई और रेड लाइन जब टच करेगी
 70 L170  VERIFIED  table        i2bGV_Wo5Yw           | हमारी ये अभी तक क्रॉसओवर नहीं हुई है... मंथली टाइम फ्रेम का चेंज नहीं 
 71 L172  VERIFIED  table        i2bGV_Wo5Yw           | किसी भी टाइम फ्रेम पे जिस टाइम फ्रेम में आप कंफर्ट हो... जितना बड़ा टा
 72 L174  VERIFIED  table        5GZIshXnxW8           | एक बार निकल जाएंगे और दोबारा जब हिलेगा मिलेगा में बाय आएगा फिर आप बाय 
 73 L175  VERIFIED  table        J_BzeTB3PpA           | हिलेगा मिलेगा पे हम लोग एक वीडियो ला रहे हैं... 30-40 मिनट का वीडियो

total 73 verified 57 not_found 16
NOT FOUND:
  #6 L23 [3KnEiKNh1pc] first-missing-fragment='कल की हाई के वन आवर के ऊपर वन आवर की कैंडल क्लोज करो।' not in 3KnEiKNh1pc | कल की हाई के वन आवर के ऊपर वन आवर की कैंडल क्लोज करो।
  #15 L40 [3KnEiKNh1pc] first-missing-fragment='एक एडिशनल कन्फर्मेशन है। इसको इग्नोर मत कीजिए।' not in 3KnEiKNh1pc | वन आवर पे हिलेगा मिलेगा आपके फेवर में जरूर होना चाहिए।... एक एडिशनल कन्फर्मेशन है। इसको इग
  #22 L58 [5GZIshXnxW8] first-missing-fragment='एवरेज एक जगह पे आ जाता हो तो प्राइस वहां से एक बड़ी मूवमेंट लेती है।' not in 5GZIshXnxW8 | जब... एवरेज एक जगह पे आ जाता हो तो प्राइस वहां से एक बड़ी मूवमेंट लेती है।
  #23 L60 [5GZIshXnxW8] first-missing-fragment='वो प्राइस पहले गिरा हो और गिरने के बाद वो दोबारा से कन्वर्जेंस के ऊपर कम से कम दो क्लोज दिया हो।' not in 5GZIshXnxW8 | वो प्राइस पहले गिरा हो और गिरने के बाद वो दोबारा से कन्वर्जेंस के ऊपर कम से कम दो क्लोज दि
  #27 L68 [5GZIshXnxW8] first-missing-fragment='एक जगह प्राइस आनी ही चाहिए' not in 5GZIshXnxW8 | एक जगह प्राइस आनी ही चाहिए... जहां डिस्टेंस होगा कन्वर्ज नहीं माना जाएगा।
  #30 L78 [dm7x3ZY9K9M] first-missing-fragment='वीकली ट्रेंड तो आवरली टाइम फ्रेम पे' not in dm7x3ZY9K9M | वीकली ट्रेंड तो आवरली टाइम फ्रेम पे... बिल्कुल नहीं। आपको जाना है डे टाइम फ्रेम पे।
  #35 L89 [dm7x3ZY9K9M] first-missing-fragment='सेलर हैं तो स्पॉट पे' not in dm7x3ZY9K9M | सेलर हैं तो स्पॉट पे... एसएल इसके ऊपर होगी
  #38 L93 [dm7x3ZY9K9M] first-missing-fragment='आरएसआई ओवरबाउट या ओवरसोल्ड हो गई हो तो वहां पे इस चीज को थोड़ा सा इग्नोर कर देना है। वहां पे वेट करना है कि डे हाई क्लोज करो तब देखेंगे।' not in dm7x3ZY9K9M | आरएसआई ओवरबाउट या ओवरसोल्ड हो गई हो तो वहां पे इस चीज को थोड़ा सा इग्नोर कर देना है। वहां 
  #43 L103 [J_BzeTB3PpA] first-missing-fragment='आईटीएम ऑप्शन के वॉल्यूम पर नजर रखो' not in J_BzeTB3PpA | आईटीएम ऑप्शन के वॉल्यूम पर नजर रखो
  #44 L103 [J_BzeTB3PpA] first-missing-fragment='या एक्सपायरी का दिन है' not in J_BzeTB3PpA | जब मार्केट सपोर्ट और रेजिस्टेंस के पास हो... या एक्सपायरी का दिन है
  #48 L117 [i2bGV_Wo5Yw] first-missing-fragment='आरएसआई का 30 का ज़ोन के आसपास और आरएसआई 70 के ऊपर' not in i2bGV_Wo5Yw | डोजी यूजफुल वहीं पर हैं जब बाजार में एक अच्छी खासी अपसाइड के बाद अगर लॉन्ग लेग डोजी बन जात
  #50 L120 [i2bGV_Wo5Yw] first-missing-fragment='जितने भी सिंगल कैंडल पैटर्न है उनमें वो कैंडल ज्यादा नहीं होता है। उसकी अगली कैंडल जो होती है वो होती है।' not in i2bGV_Wo5Yw | जितने भी सिंगल कैंडल पैटर्न है उनमें वो कैंडल ज्यादा नहीं होता है। उसकी अगली कैंडल जो होती
  #52 L122 [i2bGV_Wo5Yw] first-missing-fragment='Verify, back-test.' not in i2bGV_Wo5Yw | Verify, back-test.
  #54 L130 [B7iGQef_z6I] first-missing-fragment='उसके अंदर तीन चार कैंडलें ट्रेड करेगी और उसके बाद ब्रेकआउट और ब्रेकडाउन होंगे। तो वह काफी ट्रेडेबल होता है।' not in B7iGQef_z6I | उसके अंदर तीन चार कैंडलें ट्रेड करेगी और उसके बाद ब्रेकआउट और ब्रेकडाउन होंगे। तो वह काफी 
  #62 L157 [lmhqooBqJWU] first-missing-fragment='जब भी 20 से कर्व मुड़ जाता है ना तो' not in lmhqooBqJWU | जब भी 20 से कर्व मुड़ जाता है ना तो... छोटे टाइम फ्रेम पे स्विंग में मार्केट बाइंग में है.
  #65 L161 [lmhqooBqJWU] first-missing-fragment='जल्दी का काम शैतान का होता है। हमें जंपिंग बेबी नहीं बनना है।' not in lmhqooBqJWU | जल्दी का काम शैतान का होता है। हमें जंपिंग बेबी नहीं बनना है।
```
