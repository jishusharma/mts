# V2 extract Is1HvdfQm5c (Fabio Valentini, live session answering chat, ASR transcript)

Method: EXTRACTION_METHOD_V2.md + EXTRACTION_METHOD_V2_FABIO.md with the ASR addendum (research/fabio_asr_2026-10-16/ASR_EXTRACTION_ADDENDUM.md). Source is a machine transcription (faster-whisper small.en, local), NOT captions; every anchor says ASR. The 2.5 h body (lines 11-932) was read in three parts by independent readers (L11-L322, L323-L633, L634-L932), each in chunks of about 60 lines, start to end; the part files are merged below in part order (row ids are part.n). Numbers are ASR numbers: check frames before use.

## 3.1 Header
```
video_id: Is1HvdfQm5c
trader: Fabio (Fabio Valentini; corpus label); chat questions from viewers are spoken in the same audio
title: World Cup Trader Reveals His Order Flow LIVE | Fabio Valentini Full Uncut Session
instrument_stated: NASDAQ mentioned in places; per-trade instrument NOT STATED in most rows
tick_size: unknown
translation_warning: yes (ASR, no speaker labels, numbers unreliable)
body_lines: 922 (lines 11-932); words 17227
parts: 3 (part 1 L11-L322, part 2 L323-L633, part 3 L634-L932)
n_decision_rows: 333
n_trade_blocks: 9 (4 + 2 + 3; no confirmed live position with stated entry and stop)
```

## 3.2 Decision log

| # | lines | pos% | type | side | speaker | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.1 | L23-L23 | 1 | CONTEXT | - | FABIO | - | previous session | "it was an amazing setup session we saw a garbage market" (he did not get the short (was driving)) | prior session | none stated |
| 1.2 | L26-L26 | 2 | LESSON | - | FABIO | - | order flow vs price action | "not be able to survive okay because I will be not fast enough to put my stop-loss to breakeven and we took multiple breakeven" | delta / aggressive buyers or sellers (order flow) | none stated |
| 1.3 | L29-L30 | 2 | CONTEXT | - | FABIO | - | session plan | "we are going to cover the mental models that" ; "we are going to do live charting" (announcement of what the live covers) | - | none stated |
| 1.4 | L32-L33 | 2 | CONTEXT | short | FABIO | POC "from 16" [ASR number: check frames] | yesterday trade by chat | "perfect rejection at the POC from 16 but I was delayed because of the profile" ; "unfortunately I was not with my setup so I couldn't manage because I" (viewers took the short; he says he was not with his setup (kind of passage: VIEWER trade praised)) | VAH/VAL/POC, prior-day profile | none stated |
| 1.5 | L43-L43 | 4 | LESSON | - | FABIO | - | drawdown mindset | "the only thing that can save you from doing damage it's your mental model" | - | after a stop-loss streak: "we close three stop loss, okay, four stop" |
| 1.6 | L53-L53 | 5 | LESSON | - | FABIO | - | his model | "the model is saying that I only enter in profile framing In in trend condition and I execute" (next line: "with big trades"; [?] "trend condition") | today's profile (profile framing), big trades | none stated |
| 1.7 | L52-L52 | 5 | LESSON | - | FABIO | - | process | "end of day result to end of day process" (rule 1 of 3) | - | none stated |
| 1.8 | L55-L55 | 5 | LESSON | - | FABIO | - | risk size | "I'm not risking triple the amount I should if I close the day with negative X" | - | process on point: not overtrading, not risking triple the size |
| 1.9 | L60-L61 | 6 | CONTEXT | long | FABIO | - | November bullish day | "a long super long bullish day on November and I started to load my position" ; "So I built the profit for the day till 41 42 thousand dollars." (story, no prices ("1 2 3 1 2 4 1 2 5" ASR fragment on the next line); [ASR number: check frames]) | - | none stated |
| 1.10 | L66-L66 | 7 | ERROR | long | FABIO | higher levels | profit target of the day | "Because I put in my mind the target of closing six figures in one day 100,000 dollar" (he calls his own thinking the trap: after 40,000 profit he marked higher levels) | - | none stated |
| 1.11 | L67-L68 | 7 | ADD | long | FABIO | - | reload after big profit | "i loaded again position here okay risking part of the profit of this one" ; "this i added and this snapback" (story of a past day (ILLUSTRATION, no prices, no stop stated); order type unknown; at risk with part of the open day profit) | - | risking part of the day profit |
| 1.12 | L68-L69 | 7 | ERROR | long | FABIO | - | result of the reload | "and this snapback taking me in a streak of four stop loss" ; "in profit i only lost 15 000 in profit" (out of "41 000" day profit he gave back "15 000") | - | none stated |
| 1.13 | L75-L75 | 8 | LESSON | - | FABIO | - | students and signals | "I want to make you profitable on your own" (against signal-following) | - | none stated |
| 1.14 | L76-L76 | 8 | ERROR | - | FABIO | - | yesterday ORA | "look at ORA yesterday i was up then lost everything because i was impatient" ("ORA" is an ASR token, instrument not clear) | - | none stated |
| 1.15 | L78-L81 | 9 | ERROR | - | FABIO | - | previous live in chop | "we took a crazy sniper 25 000" ; "these are condition that I don't trade usually" ; "we gave back 10,000" ; "to the market it's not smart" (amounts: ASR number: check frames; he states stopping the day at 15,000 (L80)) | - | live session (with "word of wisdom") ran choppy after a "sniper" |
| 1.16 | L85-L85 | 10 | LESSON | - | FABIO | - | three rules | "first point not end of end-of-day result end-of-day process second" (rule 1) | - | none stated |
| 1.17 | L88-L88 | 10 | REJECT | - | FABIO | - | emotional state | "you are not suitable to go in market" ; "you stay out of the market there" (rule 2: no trading when not suitable) | - | when emotionally disturbed (argument with family) he stays out |
| 1.18 | L95-L95 | 11 | LESSON | - | FABIO | - | one account | "Your personal account is your bullet and you have one" (rule 3) | - | none stated |
| 1.19 | L102-L102 | 12 | REJECT | - | FABIO | - | number of trades | "why are you trying to take five seven ten twenty five trades per day you will not get rich today you will only make damage" (about retail overtrading, general) | - | rule: no 5 to 25 trades per day |
| 1.20 | L108-L109 | 12 | LESSON | - | FABIO | Bitcoin | other market | "I don't use order from Bitcoin" ; "I use on-chain analysis" ([?] "order from Bitcoin" probably "order flow") | other market (Bitcoin), on-chain analysis [new source] | none stated |
| 1.21 | L111-L114 | 13 | LESSON | - | FABIO | - | volume spread analysis | "I made amazing results also Using the volume spread analysis" ; "it's another different type of analysis" (offers a TradingView template next week) | volume spread analysis with tick volume ("thick volume") [new source] | none stated |
| 1.22 | L116-L116 | 13 | CONTEXT | - | FABIO | - | template | "now going through profile framing let me remove one second the TPO" | today's profile, prior-day profile | none stated |
| 1.23 | L119-L119 | 13 | LOCATION | long | FABIO | 25,000 1x1 [ASR number: check frames] | prior pivot | "the level that i told you the 25,000 1x1 that's the bottom level before accumulation" (role: "bottom level before accumulation", later "this one was the pivot" (L120)) | prior-day profile, swing low | none stated |
| 1.24 | L120-L122 | 14 | CONTEXT | - | FABIO | the high | cash session story | "this one was the pivot now they are building up" ; "I took some long yesterday" ; "the cash session open with a strong long aggression to the upside" ; "now they tapped into the high and they rejected so" (yesterday closed bullish; he took long yesterday; cash open: strong buy aggression then rejection at the high) | prior-day profile, delta / aggressive buyers | none stated |
| 1.25 | L123-L123 | 14 | CONTEXT | short | FABIO | the high | chat poll | "if you took a shot from here based on the failed auction" (asks chat who shorted; no position of his own stated (HYPOTHETICAL)) | failed auction | none stated |
| 1.26 | L127-L127 | 14 | PROOF (no entry stated) | short | FABIO | horizontal level at the high | absorption | "we can see that there is a crazy absorption at this horizontal level" | absorption, order book / big orders | none stated |
| 1.27 | L131-L132 | 15 | PROOF (no entry stated) | short | FABIO | the top | buyers fading, sellers lock | "this aggression of the buyers fading" ; "the top failing the breakout at the top something that we can see okay and we can also see the lock-in from the sellers" | absorption, delta / aggressive buyers or sellers | none stated |
| 1.28 | L135-L136 | 15 | LESSON | short | FABIO | the top | failed auction definition | "you have a lot of aggressive buyers pushing failing to break out the top okay so" ; "this one becomes a failed auction okay" (pattern teaching (HYPOTHETICAL)) | absorption, delta / aggressive buyers | none stated |
| 1.29 | L138-L138 | 16 | PROOF (BEFORE entry) | short | FABIO | the top | sellers lock the movement | "you have an aggression aggressive sellers lock in the movement" | delta / aggressive sellers | sellers must be "with result" after the absorption |
| 1.30 | L139-L140 | 16 | ENTRY | short | FABIO | "the test of this level" | test of the absorbed level | "we can take one short" ; "the trade that in 2025 gave me the most amount of money is the test of this level with" ; "the confirmation of absorbed buyers" (HYPOTHETICAL; order type unknown; entered AFTER proof; he says this trade in "2025" gave him the most money) | absorption, delta / aggressive sellers | confirmation of absorbed buyers |
| 1.31 | L141-L142 | 16 | PROOF (BEFORE entry) | short | FABIO | the top | three signals | "so these buyers no follow through the aggression rewarded" ; "you have three order flow information going in the same direction" | absorption, delta / aggressive buyers or sellers | none stated |
| 1.32 | L143-L144 | 16 | PROOF (BEFORE entry) | short | FABIO | the top [ASR number: check frames] | contracts at the top | "absorption at the top aggressive sellers 165 contract really strong" ; "the market tried to break this level for i think 2000 contract total 1400 contract total fail always" (numbers are ASR: 165, 2000 and 1400 contracts) | absorption, delta / aggressive sellers, big trades | none stated |
| 1.33 | L144-L145 | 16 | ENTRY | short | FABIO | above the absorbed area | jump in | "this is your opportunity" ; "to jump in with a super small stop loss" (HYPOTHETICAL ("your opportunity"); order type unknown; entered AFTER proof) | absorption, big trades | after absorption and failed breakout |
| 1.34 | L145-L145 | 17 | STOP_SET | short | FABIO | above the area | stop | "you can cover yourself above the area" (plus "a super small stop loss" (L145); distance NOT STATED) | absorption area (the area of absorbed buyers) | none stated |
| 1.35 | L145-L145 | 17 | TARGET_SET | short | FABIO | 1 to 4.5 [ASR number: check frames] | target in R | "shoot for a 1 to 4.5" (target stated as ratio only, level NOT STATED) | - | none stated |
| 1.36 | L146-L148 | 17 | CONTEXT | - | FABIO | - | link to the 50,000 session | "this is exactly the same model that I used to take the trade of the session of $50,000 on YouTube absorption" ; "at the top aggression entering when there is aggression collapse" ; "was the second of December" (viewer notes (L146) and he confirms it is the model of the earlier $50,000 session; [ASR number: check frames]) | absorption, delta / aggressive sellers | none stated |
| 1.37 | L151-L152 | 17 | PROOF (no entry stated) | short | FABIO | the top | effort rewarded | "look at this absorption at the top again okay then" ; "you add all this effort candle is rewarded so a huge cluster of aggression and absorption at" (he praises a viewer ("John Pransch") who executed this trade) | absorption, delta / aggressive sellers, footprint | none stated |
| 1.38 | L153-L153 | 18 | ENTRY | short | UNKNOWN | the top (price NOT STATED) | viewer or Fabio short | "I entered the short also amazing setup" (two readings: Fabio saying he also entered, or Fabio reading a viewer message aloud; order type and time unknown; entered unknown vs proof) | absorption, aggression | none stated |
| 1.39 | L154-L155 | 18 | LOCATION | short | FABIO | 25 500 [ASR number: check frames] | squeeze low | "probably they squeeze this low" ; "not so much volume because it's the london session" ; "probably they squeeze the low 25 500" (expectation (squeeze of the low), not stated as a target) | time of day (London session, low volume), swing low | none stated |
| 1.40 | L157-L158 | 18 | LOCATION | short | FABIO | last sellers aggression | first point of interest | "the aggression of the last sellers is your first point of interest" ; "So where they can go to try to reload" (sellers' reload point; "then you need to see the battle here if they manage to break or not") | delta / aggressive sellers, absorption | after an absorption and a strong move down |
| 1.41 | L159-L161 | 18 | LOCATION | - | FABIO | origin of the movement | second point | "And the second one is the first aggression point" ; "the buyers got absorbed completely" ; "We are going to the origin of the movement from where they from where they rejected" (role: first aggression point, where buyers got absorbed) | absorption, swing high | none stated |
| 1.42 | L166-L166 | 19 | LOCATION | - | FABIO | most important absorption level of the chart | absorption level | "and the most important absorption level of the buyer so where the buyers got destroyed on the" (role: location where buyers got destroyed on the way up; he asks viewers to mark it themselves) | absorption | none stated |
| 1.43 | L169-L170 | 19 | ENTRY | short (carried from the pattern; not restated) | FABIO | at rejection | timing of entry | "is better to take the trade immediately from the absorption or from the aggression" ; "can already when you see rejection you can execute" (HYPOTHETICAL; two entry timings (from the absorption or from the aggression); order type unknown; entered AFTER proof (rejection seen)) | absorption, delta / aggressive sellers | a level to cover behind must exist |
| 1.44 | L169-L169 | 19 | STOP_SET | short (carried from the pattern; not restated) | FABIO | level to cover behind (price NOT STATED) | stop reference | "if you have a level where to cover yourself that is this one" (distance NOT STATED) | absorption level | none stated |
| 1.45 | L171-L171 | 20 | CONTEXT | - | FABIO | the level | who controls | "till they break from the downside buyers are still in control so probably they want to reach this level again" | delta / aggressive buyers | until they break from the downside, buyers still in control |
| 1.46 | L174-L175 | 20 | PROOF (no entry stated) | - | FABIO | bar | delta bar then dry volume | "look how much effort they put okay" ; "now you can see a dry in volume" (effort followed by dry volume) | delta, footprint, volume | none stated |
| 1.47 | L176-L179 | 20 | LESSON | - | FABIO | - | first rejection | "look at the first rejection because the first rejection is telling you if you mark level correctly" ; "identify resting orders" ; "You can see the inability of the buyers to break out for multiple times" ; "We only had one test" ([?] "We only had one test") | absorption, order book / big orders (resting orders) | none stated |
| 1.48 | L181-L183 | 21 | LOCATION | - | FABIO | first level of the day (blue) | level types | "this one was the first level of the day that we marked" ; "unfortunately it's counter trend" ; "trend following" (two levels: one counter trend, one trend following; ASR is garbled (L182-L183)) | prior-day profile, today's profile | none stated |
| 1.49 | L186-L186 | 21 | REJECT | long | FABIO | green box | taking a long into downside pressure | "not say that it's so smart to take a long yeah we can see we can see the downside pressure" (L185 ends "I will" so the phrase is "I will not say that it's so smart to take a long") | delta / aggressive sellers | while downside pressure is visible |
| 1.50 | L187-L187 | 22 | LESSON | - | FABIO | level | risk reward | "if you think about entering at the level a closing above it's a huge risk reward" (two readings kept (stop on a close above vs entry on a close above); side not stated) | bar close (TF not stated) | none stated |
| 1.51 | L189-L190 | 22 | PROOF (no entry stated) | - | FABIO | same level | sellers absorbed, reload | "all these sellers got absorbed all of them" ; "they try to reload on the same level" | absorption, delta / aggressive sellers | none stated |
| 1.52 | L192-L192 | 22 | LOCATION | - | FABIO | "this law" [?] | break of the low | "if we manage to break this law we have a good new movement" ("law" probably "low"; direction of the new movement not stated) | swing low | if the market breaks it |
| 1.53 | L196-L196 | 23 | LOCATION | short | FABIO | the wall (price NOT STATED) | sellers vs wall | "if these sellers push against this wall you have a movement that is interesting" | order book wall, delta / aggressive sellers | sellers push against the wall |
| 1.54 | L198-L199 | 23 | CONTEXT | long | FABIO | value area low of yesterday | bias long | "if the market bias today is long we" ; "don't need to go higher from the value area law of yesterday" ; "yes you can go long" ("law" probably "low") | prior-day profile VAL | if the market bias today is long |
| 1.55 | L201-L202 | 23 | CONTEXT | - | FABIO | POC / value area low | rejection at the top | "this rejection is not a good sign and that the value area low it's really far and they" ; "we have a little bit of space to retrace" (asks "Tom" (a chat name); direction of the retrace not stated) | prior-day profile VAL, POC | none stated |
| 1.56 | L203-L203 | 24 | CONTEXT | long | FABIO | value of the session | value says higher | "the value of the session is telling us that we go high" (answer to Tom; conflicts with the previous row) | today's profile | none stated |
| 1.57 | L205-L206 | 24 | LESSON | - | FABIO | the level | repeated tests | "no one two three four fourth time" ; "the level gets weaker because other orders gets filled" | order book / big orders | each attack on a level weakens it |
| 1.58 | L207-L207 | 24 | CONTEXT | - | UNKNOWN | naked POC | level comment | "nice level with the naked POC yes Amano" (viewer line plus reply) | VAH/VAL/POC | none stated |
| 1.59 | L208-L208 | 24 | LESSON | - | FABIO | - | viewer asks how to add | "what is your smartest way to add position as entry point changes" ; "a BA is not a problem honest a BA is not a problem" (VIEWER_Q; "BA" is an ASR token (breakeven?), meaning not settled) | - | none stated |
| 1.60 | L209-L210 | 24 | PROOF (no entry stated) | long | FABIO | block | level not holding, sellers absorbed | "if you see that your level is not holding and the sellers got absorbed like here for example" ; "this block here what is telling you going up or no squeeze up or no" | absorption, delta / aggressive sellers | level not holding and sellers absorbed |
| 1.61 | L211-L212 | 24 | PROOF (BEFORE entry) | long | FABIO | the broken level | buyers rewarded | "these buyers got the reward that the candle close long we managed to break this level" ; "we have a huge cluster between here and also the downside area" ; "they are squeezing the top" | bar close (TF not stated), delta / aggressive buyers, footprint cluster | none stated |
| 1.62 | L213-L214 | 25 | PROOF (BEFORE entry) | long | FABIO | the cluster | squeeze pattern | "you see this is the pattern that I take the squeeze is this sellers absorbed or no" ; "the sellers is absorbed the buyers got confirmed even" (it is the pattern he takes ("the squeeze")) | absorption, delta / aggressive buyers | none stated |
| 1.63 | L215-L215 | 25 | ENTRY | long | FABIO | "here" (price NOT STATED) | squeeze long | "if you enter here not here still an amazing run up" ; "you don't need to make one to three one to four always" (ILLUSTRATION; order type unknown; entered AFTER proof; entering late is still fine; he says you do not need always 1:3 or 1:4) | absorption, delta / aggressive buyers | sellers absorbed and buyers confirmed |
| 1.64 | L218-L219 | 25 | PROOF (BEFORE entry) | long | FABIO | testing level [ASR number: check frames] | rewarded or not | "there was a 97 sellers absorbed they put another 75 contract here is it rewarded or no" ; "no okay then when you make this framing of the area" (numbers are ASR: 97 and 75 contracts; "rewarded or no" answered "no" next line) | absorption, delta / aggressive sellers, big trades | none stated |
| 1.65 | L220-L220 | 25 | PROOF (BEFORE entry) | long | FABIO | 123.9 and 125 [ASR number: check frames] | third test | "this one is a 123.9" ; "we just tested again for the third time it's a 125" (meaning of 123.9 and 125 (price or contracts) not clear) | footprint cluster, big trades | none stated |
| 1.66 | L221-L221 | 26 | STOP_SET | long | FABIO | below the area | cover below the area | "covering yourself below the area this is the squeeze setup" (distance NOT STATED; "this is the squeeze setup") | footprint cluster, absorption | none stated |
| 1.67 | L221-L222 | 26 | PROOF (BEFORE entry) | long | FABIO | the cluster | repeated taps | "you see how the market continuously tap into this" ; "you see how we tap into a reload all this cluster" | footprint cluster, delta / aggressive buyers | none stated |
| 1.68 | L223-L224 | 26 | TARGET_SET | long | FABIO | 1 to 5 / 1 to 4.9 [ASR number: check frames] | target in R at the third touch | "this one it's target 1" ; "to 5 1 to 4.9 at the third touch" (ratio only, level NOT STATED) | - | at the third touch |
| 1.69 | L225-L226 | 26 | REJECT | long | FABIO | 1 to 10 | greedy target | "when you try to make the super sniper 1 to 10" ; "the more you are greedy with your target the less the probability that it get reached" (he rejects "super sniper" 1:10 targets) | - | none stated |
| 1.70 | L232-L234 | 26 | REJECT | - | FABIO | 255 contracts [ASR number: check frames] | another setup | "it's a trade that it's a little bit difficult to take" ; "because you have always also these inefficiency" ; "they tap into these 255 contracts" (side not stated) | big trades, volume (inefficiency) | inefficiency in the way |
| 1.71 | L235-L240 | 27 | LOCATION | - | FABIO | 255 [ASR number: check frames] | strongest aggression | "the most important aggression" ; "of all this chart area is this 255" ; "which level is the most strong" ("139 255 73 65 62" ASR number string at L234-L235) | big trades, delta / aggressive buyers or sellers | none stated |
| 1.72 | L241-L241 | 27 | CONTEXT | short | FABIO | - | shorting after the move | "we were short here the first time it took an amazing explosion down then it came" ("we were short": whose position is not stated) | - | none stated |
| 1.73 | L242-L243 | 28 | REJECT | short | FABIO | - | continuing to short | "when the market tell you something like this and you continue to short it's your responsibility" ; "you only want to be right" (says it is about wanting to be right, not about money) | - | when the market has shown the opposite |
| 1.74 | L244-L244 | 28 | STOP_SET | long | FABIO | before the area | conservative execution | "you can decide to execute with a stop loss before the area with the target here" ([?] "before the area" (in front of or behind)) | absorption area | none stated |
| 1.75 | L244-L244 | 28 | TARGET_SET | long | FABIO | home run | huge risk reward | "or you can go for the home run" (alternative to the near target) | - | none stated |
| 1.76 | L245-L245 | 28 | LESSON | long | FABIO | - | strike rate | "can go for the long setup with a huge risk reward but this one have a lower strike rate" ; "you will have around 30 to 35 percent win rate" (win rate 30 to 35 percent for the home run version [ASR number: check frames]) | - | none stated |
| 1.77 | L247-L247 | 28 | STOP_SET | long | FABIO | 640 [ASR number: check frames] | stop area | "we consider a stop area 640" ("640 640" repeated in ASR; full price NOT STATED) | - | if he needs to go long term |
| 1.78 | L248-L248 | 28 | TARGET_SET | long | FABIO | above the high ("eye" [?]) | near target | "you take a target above the eye" ("eye" probably "high") | swing high | none stated |
| 1.79 | L249-L249 | 28 | TARGET_SET | long | FABIO | 25 646.39 [ASR number: check frames] | next level | "the next level that i can see is the 25 646.39" (alternative: shoot to the next level) | order book / big orders | none stated |
| 1.80 | L250-L251 | 28 | PROOF (no entry stated) | - | FABIO | next level | failed auction | "is this a confirmation of selling pressure or buy pressure" ; "unfortunately failed auction" ; "they came back to the same level that so the sellers absorbed" (which side failed is not stated; "unfortunately" suggests against the long) | failed auction, absorption | none stated |
| 1.81 | L253-L255 | 29 | LESSON | - | FABIO | - | order flow is democratic | "order flow is democratic we see the same information all over" ; "look at this delta delta where the market rejected first time here" ; "there is only reading" | delta, fixed profile | none stated |
| 1.82 | L259-L260 | 30 | CONTEXT | - | FABIO | - | auction respects level | "what an amazing auction today" ; "amazing auction is respecting the level like crazy" | - | none stated |
| 1.83 | L264-L264 | 30 | LOCATION | long | FABIO | 25,646 [ASR number: check frames] | first reaction level | "I think the first reaction we will see at this level twenty five thousand six hundred and forty six" | order book / big orders | none stated |
| 1.84 | L265-L267 | 30 | LOCATION | long | FABIO | micro gap at 25,646 [ASR number: check frames] | gap between two candles | "there is a small gap between these two candle" ; "if the candle close green is shoot thus and goes to the next" ; "you see how would they reload on the gap" ; "this is inefficient volume because it created a micro gap" ; "and when they go back here the market reload" ([?] "shoot thus"; role: reload location) | volume (inefficient volume / gap), bar close (TF not stated) | if the candle closes green |
| 1.85 | L269-L272 | 31 | CONTEXT | - | FABIO | level | viewers took the sniper | "you see the first rejection when you get close to the level" ; "how many of you took this sniper" ; "three of them nice entry FTMO okay still money" (viewers' replies in the same audio; side not stated) | absorption | none stated |
| 1.86 | L276-L276 | 31 | REJECT | long | FABIO | - | drop the long | "long okay let's not consider the long" ; "i always think about the first touch" (reason for dropping the long not stated here) | absorption, order book / big orders | none stated |
| 1.87 | L276-L277 | 31 | PROOF (no entry stated) | - | FABIO | level | first touch, resting orders | "it's clearly visible the absorption" ; "on this level there are resting orders" | absorption, order book / big orders (resting orders) | none stated |
| 1.88 | L279-L279 | 32 | REJECT | short | FABIO | balance level | counter trend short | "but these are counter trend trade and I don't like to take them" (he says sellers absorbed or price back to a balance level would give a counter trend trade) | absorption | none stated |
| 1.89 | L280-L281 | 32 | LOCATION | long | FABIO | level sustained by "39 250 89" [ASR number: check frames] | wall level | "remember that this level is sustained by 39 250 89 around around" ; "25 million of notional value" ; "if this gets broken we shoot strong we shoot strong up you have" (role: level whose break gives a squeeze up; the number string is ASR garble) | order book / big orders | if this level gets broken |
| 1.90 | L284-L284 | 32 | LESSON | - | FABIO | - | squeeze definition | "squeeze guys is when you see a sudden acceleration" ([?] "closing of cell" (sell stops?)) | market speed | none stated |
| 1.91 | L285-L286 | 32 | PROOF (no entry stated) | long | FABIO | last loading | no big orders from buyers | "there is not a big participation from the aggressive buyers so big orders in this movement" ; "did one two three four then they stopped" | order book / big orders, delta / aggressive buyers | none stated |
| 1.92 | L287-L287 | 33 | REJECT | long | FABIO | - | nothing to execute | "now i don't see anything that we can execute" ; "just that they are high in the curve" | order book / big orders, delta / aggressive buyers | no big orders from aggressive buyers; "high in the curve" |
| 1.93 | L289-L290 | 33 | PROOF (no entry stated) | long | FABIO | the level | buyers reload and hold | "they go back to this level I can see the buyers reloading" ; "they try to break three four five times and they always hold this level that" ; "it means that their intent is go higher" | delta / aggressive buyers, absorption | none stated |
| 1.94 | L291-L292 | 33 | REJECT | long | FABIO | - | trade without support from aggressive participants | "like to take trades when there is no support from the aggressive order market participants" ; "but if you have other confirmation that you like to use maybe the delta" ; "profile footprint you can do it" (preceded by "i usually don't" on L290) | delta, footprint | unless another confirmation (delta, profile, footprint) exists |
| 1.95 | L293-L293 | 34 | PROOF (no entry stated) | - | FABIO | - | speed of tape | "speed of tape is dry but i think it will get soon soon" | market speed (speed of tape) | none stated |
| 1.96 | L297-L298 | 34 | LESSON | - | FABIO | - | model: big trades plus tape candle | "the same candle and it's the candle that initiated all this movement" ; "the model with deep trades" ; "plus the aggression candle of the speed of tape this mean that is interesting" ([?] "deep trades" probably "big trades") | order book / big orders, market speed (speed of tape), delta / aggressive sellers | none stated |
| 1.97 | L298-L298 | 34 | CONTEXT | long | VIEWER | 681 [ASR number: check frames] | viewer target | "is 681 a good TP where" (question read aloud; level 681 (likely 25,681) not stated in full) | - | none stated |
| 1.98 | L300-L300 | 34 | TARGET_SET | long | FABIO | 681 [ASR number: check frames] | viewer's take profit | "it's a smart TP" (HYPOTHETICAL / VIEWER_Q; no entry or stop given for it) | - | none stated |
| 1.99 | L300-L300 | 34 | REJECT | long | FABIO | no-man land | long from nothing | "I don't understand why you are trying long in the no-man land" ; "see that there is nothing here" | order book / big orders | none stated |
| 1.100 | L300-L301 | 34 | ENTRY | long | FABIO | cluster "one two six" [ASR number: check frames] | last long opportunity | "the last opportunity that I see long" ; "entering at this cluster one" (VIEWER_Q reply (HYPOTHETICAL); order type unknown; entry at the cluster; proof timing unknown) | big trades (cluster) | none stated |
| 1.101 | L302-L302 | 34 | STOP_SET | long | FABIO | - | stop | "entering with really high stop loss" (distance NOT STATED) | - | none stated |
| 1.102 | L302-L302 | 34 | TARGET_SET | long | FABIO | 1 to 2.5 [ASR number: check frames] | target in R | "so one to two point five still paying out" (ratio only) | - | none stated |
| 1.103 | L303-L303 | 35 | CONTEXT | long | VIEWER | - | viewer partial at 1:1 | "took two now securing one hour I took two one-to-one risk to reward" ; "it's it's still good yeah I know that it's burning Arsalan we" (a viewer message about taking two and securing one at 1:1 (not a Fabio PARTIAL); Fabio replies "it's still good") | - | none stated |
| 1.104 | L304-L304 | 35 | CONTEXT | - | FABIO | - | plan to chart | "I want to do some charting because today he already gave us multiple opportunities that are amazing" | - | none stated |
| 1.105 | L305-L309 | 35 | PROOF (no entry stated) | short | FABIO | level they will visit | sellers on the tape | "remember this level that I told you are the one that they will visit" ; "the aggression on the downside of the speed of tape" ; "which is the level that stopped at least for the first time all this collapse" | market speed (speed of tape), delta / aggressive sellers | none stated |
| 1.106 | L312-L314 | 35 | PROOF (no entry stated) | long | FABIO | the level | buyers reload to protect | "they are reloading to protect this level" ; "are fighting they are fighting in this area" ; "against sellers trying to recover the aggressive pressure that they put before" | market speed (speed of tape), delta / aggressive buyers | none stated |
| 1.107 | L315-L315 | 36 | CONTEXT | - | VIEWER | - | question: momentum breakout in balance | "like momentum breakout when you are in a whole balance space" (question read aloud) | - | none stated |
| 1.108 | L316-L318 | 36 | REJECT | - | FABIO | value area low | momentum trade in balance | "you need to be not exactly at one level value area value area low" ; "it's the limit price wall on the top or on the bottom it's giving keeping you in consolidation" ; "this is the worst case that you can have for a momentum trade" (answers the viewer; side not stated) | VAH/VAL/POC, order book wall | when sitting at a level at the value area low |
| 1.109 | L319-L319 | 36 | ENTRY | short | FABIO | break of the level (price NOT STATED) | sell continuation | "i will consider a cell continuation if we break out this level yes" (HYPOTHETICAL; order type unknown; entered AFTER proof (breakout); ASR "cell" for "sell") | bar close (TF not stated) | if the level breaks out |
| 1.110 | L320-L320 | 36 | PROOF (no entry stated) | long | FABIO | reclaimed level | absorbed aggression, reclaim | "this aggression that got absorbed here and this reclaim of the level that got reconfirmed here it's a really good sign for" | absorption, delta / aggressive sellers | none stated |
| 1.111 | L321-L322 | 37 | ENTRY | long | FABIO | recovery of the huge candle (price NOT STATED) | plan for the long | "if we manage to recover this huge candle okay" ; "a little bit of participation of the buyer some big trades" (HYPOTHETICAL plan; order type unknown; entered AFTER proof (not before)) | big trades, bar close (TF not stated) | recover the huge candle and see a little buyer participation (big trades) |
| 1.112 | L322-L322 | 37 | TARGET_SET | long | FABIO | the other guy's target | viewer's target | "then we go to the target that the other guy say that is this one" (likely the 681 of the earlier question; level not stated) | - | after recovery and some buyer big trades |
| 2.1 | L323-L324 [49:25-49:35] | 38 | LOCATION | - | FABIO | sensitive areas one and two (prices not stated) | his marked areas; absorption; intermediate area; playground | only mark the sensitive areas that i'm watching ; this is the playground | absorption | none stated |
| 2.2 | L325-L327 [49:49-50:09] | 38 | LOCATION | - | FABIO | 25,545 [ASR number: check frames] | downside break of the marked areas (viewer asked if he would shift his view) | i will consider shifting my view when the market tells me so ; attacking the 25,545 | delta / aggressive sellers | aggression on the downside that breaks this area (area named three times); then 'attack the law [?]' = 25,545 |
| 2.3 | L328-L329 [50:21-50:31] | 38 | CONTEXT | - | FABIO | most important area | pattern on the most important area | gives you the vibe of a rejection or a continuation short | - | none stated |
| 2.4 | L330-L332 [50:38-50:45] | 39 | LESSON | short | FABIO | breakout candle at the area (HYPOTHETICAL, viewer: will you short now) | breakout of the area on a candle | You can short now ; If the market gives you the breakout ; Here you can take a short on the momentum phase | delta / aggressive sellers; bar close (TF not stated) | the market gives the breakout; the candle is aggressive |
| 2.5 | L333-L335 [50:52-51:03] | 39 | REJECT | short | FABIO | area tested four times | buyers aggressive; four tests, each rejected | We don't have the clue that the aggressive sellers are strong enough | delta / aggressive buyers, absorption | buyers tested four times and each time rejected; sellers not shown strong enough to break |
| 2.6 | L336-L337 [51:07-51:17] | 39 | CONTEXT | - | FABIO | the level (price not stated) | buyers protecting the level; last test sellers absorbed | we have the clue that buyers are protecting the level ; the sellers got completely absorbed | absorption, order book (protection) | none stated |
| 2.7 | L338-L339 [51:23-51:33] | 39 | LOCATION | - | FABIO | 25,632 [ASR number: check frames] | intermediate wall of the sellers | this is the intermediate wall that the sellers are putting ; if this one gets broken from the buyers expect volatility | order book / big orders (wall) | if broken by the buyers, expect volatility; role: sellers' wall |
| 2.8 | L339-L340 [51:33-51:44] | 39 | REJECT | short | FABIO | the wall level (price not stated) | wall printing; no clean break yet | if you are waiting for a confirmation to get short wait for this level to collapse ; wait for it to stop printing this week and to have a clean break | order book / big orders, delta | no short until the level collapses, stops printing and breaks cleanly ('this week' [?]) |
| 2.9 | L342-L344 [52:01-52:22] | 40 | CONTEXT | - | FABIO | inefficiency; 139 executed contract [ASR number: check frames] | price filled into the inefficiency (micro gap); speed of tape long | another time they filled into the inefficiency ; the 139 executed contract ; the speed of tape of the aggressive market order on the buy side it's interesting | footprint / delta, market speed (speed of tape), inefficiency [new source: gap/inefficiency] | none stated |
| 2.10 | L345-L345 [52:32-52:32] | 40 | LOCATION | - | FABIO | horizontal level (price not stated) | buyers and sellers fighting at one horizontal level | now they are fighting this is an important decision level | market speed (speed of tape) | none stated |
| 2.11 | L348-L349 [52:49-53:00] | 40 | CONTEXT | - | FABIO | a little below the value area, almost at the POC | location in today's profile | a little bit below the value area ; we are almost at the POC | today's profile, VAH/VAL/POC | none stated |
| 2.12 | L350-L353 [53:15-53:44] | 40 | CONTEXT | - | FABIO | the level under test (price not stated) | sell-side speed of tape vs a buyers' absorption wall | i will be surprised if they don't break it now ; if they don't break with this speed of tape and with this pressure we reject | market speed (speed of tape), absorption / order book wall | if the sellers do not break it with this speed and pressure -> he calls rejection |
| 2.13 | L357-L359 [54:32-54:53] | 41 | LESSON | - | FABIO | decision level (HYPOTHETICAL) | slippage when an order and its stop sit just beyond a decision level | this is the moment where you risk sleepage ; the level gets broken and the candle squeeze really strong | order book | level breaks through a stop placed slightly below it ('sleepage' [?] = slippage) |
| 2.14 | L361-L362 [55:07-55:13] | 42 | CONTEXT | - | FABIO | the level (price not stated) | who is in control; level role if broken | the sellers are in control but | market speed | none stated |
| 2.15 | L362-L363 [55:13-55:23] | 42 | LOCATION | short | FABIO | the same level, role change (price not stated) | support level that becomes a sell-side reload level if broken | if they break it this level will be used to reload on the cell side | order book / big orders | if they break it; 'self-protection level' [?] = sell protection level |
| 2.16 | L364-L365 [55:27-55:37] | 42 | LESSON | - | FABIO | the level (price not stated) | break of the level squeezes the buyers' stops | if they break this level it's explosion because all these buyers needs to close | order book | if the level breaks |
| 2.17 | L365-L368 [55:37-56:08] | 42 | LESSON | - | FABIO | the level (price not stated) | volume against price: a lot of volume, level does not break | it broke it failed every time they try to break buyers absorb ; they put a lot of volume but they failed | absorption, order book / big orders | none stated |
| 2.18 | L371-L372 [56:27-56:33] | 43 | CONTEXT | - | FABIO | control levels (prices not stated) | size of the resting orders | they are putting billions here ; They are loading billions | order book / big orders (heat map family) | none stated |
| 2.19 | L373-L373 [56:36-56:36] | 43 | LOCATION | short | FABIO | the sensitive level that we saw before (price not stated) | the target of a downside move if the wall breaks | if this one breaks, it's an amazing opportunity to go on the downside to the level that we saw before | order book / big orders | if this one breaks |
| 2.20 | L377-L378 [57:20-57:30] | 43 | CONTEXT | - | VIEWER | - | viewer question on defending / protecting an area | how they are defending or for protecting an area | - | none stated |
| 2.21 | L379-L382 [57:39-57:58] | 44 | LESSON | - | FABIO | the level (price not stated) | passive orders stacking; sell aggression absorbed; they are loading long | the passive orders are stacking liquid here ; they are absorbing all this cell aggression ; And they are also loading long | order book (passive), absorption | none stated |
| 2.22 | L388-L390 [58:32-58:55] | 44 | LOCATION | - | FABIO | two levels: buyers' aggression / protection level, and the sellers' level (prices not stated) | only two important levels | we still have only two important level ; the aggression of the buyers and the protection level of the buyers | delta / aggressive buyers, order book (protection) | if you break this you have this level that it's really interesting |
| 2.23 | L390-L390 [58:55-58:55] | 44 | REJECT | - | FABIO | n/a | marking intermediate levels | it's not necessary to mark intermediate level that are useless for us | - | reason: useless for us |
| 2.24 | L396-L397 [1:00:01-1:00:11] | 45 | CONTEXT | - | FABIO | top and bottom of the range (prices not stated) | candle close green; sellers absorbed at the bottom; buyers at the top | the candle close green with sellers absorbed at the bottom and buyers at the top | absorption, bar close (TF not stated) | none stated |
| 2.25 | L399-L400 [1:00:25-1:00:35] | 45 | CONTEXT | - | FABIO | the range (prices not stated) | result of buyers zero and result of sellers zero | the result of the buyers at zero ; the result of the sellers zero we are stuck we are inside this range | absorption | none stated |
| 2.26 | L401-L404 [1:00:48-1:01:21] | 46 | LESSON | - | FABIO | control point at the range edge (HYPOTHETICAL plan) | waiting inside the range and stacking one order that capitalises on the explosion of the range | stacking one order that is capitalizing on the explosion of the range ; some big trades here at the top ; or clean breakout and test | order book / big orders, delta, bar close | a clean control point needs acceptance: big trades at the top, or a clean breakout and test |
| 2.27 | L404-L404 [1:01:21-1:01:21] | 46 | ADD | - | FABIO | third position for the day (price not stated) | stacking after the control point (plan or live not settled by the words; see flags) | we are stacking our third position for the day | - | after acceptance (big trades at the top or clean breakout and test) |
| 2.28 | L404-L405 [1:01:21-1:01:31] | 46 | CONTEXT | long | UNKNOWN | fair value gap; 400 buyers [ASR number: check frames] | a trade running with small risk from the fair value gap (likely a viewer message read aloud: 'nice one hey') | i got this one running with small risk from the fair value gap protected by 400 buyers ; nice one hey it's the one that we saw before | fair value gap [new source: gap], order book / big orders | none stated |
| 2.29 | L408-L411 [1:02:02-1:02:33] | 46 | CONTEXT | - | FABIO | level under test (price not stated) | interaction of the big orders; buyers interested, no follow through | we are watching the interaction from the big orders ; the buyers are interested but there is not follow through | order book / big orders, delta | none stated |
| 2.30 | L411-L412 [1:02:33-1:02:40] | 47 | CONTEXT | - | FABIO | n/a | direction not decided | the direction is still not decided ; if the direction was decided you will see aggression aggression aggression like here | delta / aggressive buyers or sellers | direction is decided only when aggression, aggression, aggression is seen |
| 2.31 | L413-L414 [1:02:49-1:02:57] | 47 | CONTEXT | long | FABIO | n/a | structure unfolding on the upside; absorption; no big participation | it's clear to me that we are going long ; we don't see participation of the big | swing high/low (structure), absorption, order book / big orders | no participation of the big trades yet |
| 2.32 | L415-L415 [1:03:02-1:03:02] | 47 | CONTEXT | long | FABIO | the target (price not stated) | length of the target | maybe this target is too long ; It's too on the upside | order book / big orders | none stated |
| 2.33 | L416-L417 [1:03:06-1:03:17] | 47 | STOP_MOVE | long | FABIO | entry (risk zero; level not stated) | no big-trade participation; target maybe too far | it makes sense to put the risk to zero on the upside ; so we are not even using the profit of the previous one | order book / big orders | no participation of the big trades; target maybe too long (rows above) |
| 2.34 | L417-L417 [1:03:17-1:03:17] | 48 | HOLD | long | FABIO | final target (price not stated) | bigger movement | then considering to run through the final target there is a bigger movement | - | bigger movement (sentence cut at 'and' [?]) |
| 2.35 | L418-L420 [1:03:30-1:03:51] | 48 | LESSON | - | FABIO | n/a (viewer asked: how you scaling when you are right) | price action and volume unfolding; position management still to be shown | now I want to see the how with the price action unfold and the volume unfold ; we need to see position management | - | none stated |
| 2.36 | L421-L422 [1:03:55-1:04:05] | 48 | LESSON | - | FABIO | n/a | exit from a compression phase | when you exit from a compression phase you have momentum | bar close (single aggressive candle; TF not stated) | none stated |
| 2.37 | L423-L424 [1:04:15-1:04:25] | 48 | PROOF (before/after entry unknown) | - | FABIO | the level (price not stated) | buyers stuck at top, sellers stuck at bottom, result of the buyers confirmed; test closes an inefficiency at the level with absorption | buyers stock at the top sellers stuck at the bottom result of the buyers confirmed ; it's closing an inefficiency touch the level and close the level with this absorption | absorption, inefficiency [new source: gap], bar close | none stated |
| 2.38 | L425-L426 [1:04:36-1:04:44] | 49 | ENTRY (ILLUSTRATION; order type unknown; entered AFTER the proof in the row above) | unknown (long suggested by context; not said) | FABIO | the tested level (price not stated) | where the entry would have been | this one here would have been your feeling point | absorption, inefficiency | test of the inefficiency closes at the level with absorption ('feeling point' [?] = filling point) |
| 2.39 | L427-L427 [1:04:50-1:04:50] | 49 | CONTEXT | - | FABIO | n/a | sellers loading while buyers protect | The sellers are loading new position even if the buyers are protecting now sellers are stronger | delta / aggressive sellers | none stated |
| 2.40 | L427-L428 [1:04:50-1:05:01] | 49 | STOP_MOVE | - | FABIO | when price goes out of the level (price not stated) | covering the risk on the position | this position to consider covering ; covering your risk when you go out of the level | - | when you go out of the level; sellers absorbed and buyers following up (next row) |
| 2.41 | L429-L430 [1:05:09-1:05:15] | 49 | STOP_MOVE | - | FABIO | entry (risk-free; level not stated) | risk-free if entered precisely and fast | You can also Go risk-free if you enter precisely really fast ; the sellers are being absorbed and the buyers are being follow-up | absorption, delta | enter precisely really fast; sellers absorbed and buyers following up |
| 2.42 | L431-L432 [1:05:25-1:05:36] | 49 | STOP_SET | - | FABIO | the level / top (price not stated) | break of the level invalidates the analysis | if it break this level the analysis invalidator ; So you go to stop loss | swing high/low | if it breaks on the downside, 'invalidator' [?] = invalidates; he goes to the stop loss |
| 2.43 | L433-L436 [1:05:45-1:06:11] | 50 | STOP_MOVE | - | FABIO | entry (stop loss at zero; level from before) | marked level from before; high probability of rejecting; time to go to zero | one minute risk-free ; We mark the level from before we know exactly where there is the high probability of rejecting ; we have time To go stop losing at zero so fast not even one candle | prior marked level (swing / order level) | stop to zero 'not even one candle' after entry; the level was marked before the trade |
| 2.44 | L436-L436 [1:06:11-1:06:11] | 50 | LESSON | - | FABIO | n/a | break-even versus loss | it's better to take three brekivan for brekivan that losing money | - | ('brekivan' [?] = break-even) |
| 2.45 | L437-L438 [1:06:20-1:06:30] | 50 | ENTRY (ILLUSTRATION; order type unknown; entered AFTER the proof named in the quote) | - | FABIO | n/a | absorption candle, two following absorption candles, then an aggression | when to enter you see this absorption in one candle you have two following absorption then you have an aggression | absorption, delta, bar close | one absorption candle, two following absorption candles, then an aggression |
| 2.46 | L439-L439 [1:06:35-1:06:35] | 50 | LESSON | - | FABIO | n/a | what other educators teach | this is the reason people lose money | - | none stated |
| 2.47 | L443-L444 [1:07:11-1:07:21] | 51 | CONTEXT | - | FABIO | viewer trade, one to four [ASR number: check frames] | a viewer's entry he comments on | what a sniper guys this one ; someone is making one to four | - | none stated |
| 2.48 | L445-L447 [1:07:28-1:07:44] | 51 | PARTIAL (HYPOTHETICAL alternative for viewers; 1.5 [ASR number: check frames]) | - | FABIO | 'here' (price not stated) | choppy price; alternative to take another one to one point five | I take another one to one point five here ; you close seven point five and you are done | - | the move is 'a little bit choppy' ('Presection' [?]) |
| 2.49 | L447-L448 [1:07:44-1:07:54] | 51 | STOP_MOVE | - | FABIO | break-even (level not stated) | break-even once the market allows | the confidence of going to break even when the market tell you that you can go ; if it breaks this level we go down | - | when the market tells you that you can go |
| 2.50 | L449-L449 [1:08:06-1:08:06] | 51 | LESSON | - | FABIO | n/a (viewer reply: Mario) | a viewer who thinks he is risk-free | you are not risk-free Mario you are still with position in the market be careful | - | none stated |
| 2.51 | L450-L451 [1:08:17-1:08:27] | 51 | LOCATION | - | FABIO | the level we marked (price not stated) | aggressive sellers slicing through aggressive buyers; first level of difficulty | the aggressive sellers are slicing through the aggressive buyers ; where is the first level where they find difficulty in going down the one that we marked | delta / aggressive sellers, prior marked level | none stated |
| 2.52 | L454-L454 [1:08:54-1:08:54] | 52 | PARTIAL (HYPOTHETICAL: 'you can say'; $200 [ASR number: check frames]) | - | FABIO | n/a | taking a little money out of the market | I take also a little bit of money out of the market maybe it's not much it's $200 | - | none stated |
| 2.53 | L459-L460 [1:09:48-1:09:53] | 52 | PARTIAL | - | FABIO | important level (price not stated) | rejection and precision on the level | You will take out your take profit your partial your first take profit ; Look at the rejection and the precision on the level | prior marked level | at the important level |
| 2.54 | L465-L465 [1:10:26-1:10:26] | 53 | CONTEXT | long | FABIO | n/a | profile framing | The profile is long | today's profile, prior-day profile (profile framing) | none stated |
| 2.55 | L466-L467 [1:10:36-1:10:46] | 53 | LESSON | - | FABIO | n/a (viewer asked how he manages a day that started with a loss) | daily stop-loss limit | if I start with a loss I continue till 3 ; if I reach a maximum of 3 stop loss either I lower the exposure but usually a stop for the day | day P&L | start with a loss; maximum of 3 stop losses |
| 2.56 | L467-L469 [1:10:46-1:11:07] | 53 | LESSON | - | FABIO | n/a | three stops in a row is rare; position management is fast | my position management it's fast ; the market only takes the commission out of me | - | 'two or three times per month' for three stops in a row |
| 2.57 | L471-L471 [1:11:25-1:11:25] | 53 | TARGET_SET | - | FABIO | final target 'here' (price not stated) | expecting a final target | I'm expecting a final target here | - | none stated |
| 2.58 | L476-L481 [1:12:39-1:13:19] | 54 | LOCATION | - | FABIO | the marked level: start of the sell move | huge absorption cluster at the initiation of the move | this level is the starting of the sell move participated by the aggressive sellers ; it's the huge absorption look here this cluster it's incredible ; this is the initiation of the move | absorption, footprint, delta / aggressive sellers | role: origin-of-the-move level, chosen for the absorption cluster |
| 2.59 | L487-L488 [1:14:29-1:14:40] | 55 | LESSON | - | FABIO | n/a | technical figures versus quantitative work | you understand that 95% of the stuff that they teach you don't work | - | none stated |
| 2.60 | L492-L493 [1:15:18-1:15:28] | 55 | LESSON | - | FABIO | n/a | students scalping gold with his momentum model | I have some students that scalp gold also | other market (gold; Nasdaq named as the model's other market) | none stated |
| 2.61 | L495-L498 [1:16:00-1:16:32] | 56 | LESSON | - | FABIO | n/a | range bars in a choppy market | when the market is getting in a choppy mood you can use the 40 range ; sellers absorbed at the bottom | absorption, bar close (40 range bars) | choppy market |
| 2.62 | L499-L500 [1:16:42-1:16:52] | 56 | STOP_MOVE (HYPOTHETICAL: alternative for viewers who did not take profit) | - | FABIO | stop loss in profit 'here' (price not stated) | managing the position after one-to-one is out | manage the position with a stop loss in profit here ; you are already taking out a one-to-one | - | if you decided not to take profit |
| 2.63 | L501-L501 [1:17:02-1:17:02] | 56 | LESSON | - | FABIO | back at this level (price not stated) | second trade after a stop-out | if you get taken out it goes back to this level you see another you can take another trade | - | if you get taken out and price goes back to this level |
| 2.64 | L511-L513 [1:18:23-1:18:44] | 57 | LESSON | - | FABIO | n/a (viewer asked: keep your 0.25 [ASR number]) | profit stacked during the day used as risk for the next trade | i stack profit for the day using it to risk another trade ; after i take three take profits at the next trade it's part of the profit i made | day P&L | after three take profits |
| 2.65 | L517-L518 [1:19:30-1:19:41] | 58 | CONTEXT | - | FABIO | the level (price not stated) | waiting to see price fill the level and reject | i want to see if it fill this level and reject | - | price fills the level and rejects |
| 2.66 | L521-L523 [1:20:33-1:20:54] | 58 | STOP_MOVE (HYPOTHETICAL: 'let's say') | - | FABIO | below the big trade on the downside (price not stated) | trailing on the big trade when close to the target | now you see how i also trade my position when i'm really close to target is trailing on the big trade ; i have a stop in profit i put below the big trade on this downside because i'm happy with a one to three instead | order book / big orders | he accepts the stop being hit; 'i'm not happy if the market touch this level from here and collapse down' |
| 2.67 | L522-L523 [1:20:44-1:20:54] | 58 | TARGET_SET (implied original target; stated as the alternative not taken; 3.6 [ASR number: check frames]) | - | FABIO | one to three point six (R multiples; no price) | R:R of the full target versus the one he would accept | i'm happy with a one to three instead of a one to three point six | - | none stated (hypothetical stop-in-profit) |
| 2.68 | L524-L524 [1:21:04-1:21:04] | 59 | CONTEXT | - | FABIO | 65 contract [ASR number: check frames] | demand under price | sustained by his demand created by the 65 contract | order book / big orders | none stated |
| 2.69 | L526-L527 [1:21:20-1:21:27] | 59 | LESSON | - | FABIO | n/a | trailing behind each aggression (past live session) | You saw me in the live like trailing Here then you have an aggression trailing here ; Then you have another aggression the 50,000 session | delta / aggressive buyers or sellers | each new aggression moves the trail |
| 2.70 | L529-L529 [1:22:07-1:22:07] | 59 | CONTEXT | - | FABIO | the top (price not stated) | rejection at the top | you see how we starting to reject the top | - | none stated |
| 2.71 | L530-L530 [1:22:11-1:22:11] | 59 | EXIT (HYPOTHETICAL / viewers who closed; numbers [ASR number: check frames]) | long | FABIO | one to two point seven; one two two point six (R multiples) | viewers' exit versus staying in the long | here you are out you are out with your one to two point seven one two two point six | - | none stated |
| 2.72 | L531-L532 [1:22:21-1:22:28] | 59 | TARGET_SET | long | FABIO | full target one two three [ASR number: check frames] | market went down, absorbed; full target for those who stayed | probably you go to the full target one two three | absorption | the market went down absorbed |
| 2.73 | L533-L534 [1:22:38-1:22:49] | 59 | ENTRY (past recap; order type unknown; price not stated) | long (from 'in the long', L530) | FABIO | beginning of the move | his own position versus viewers' later entries | we are inside from the beginning of the move with this precision | - | none stated |
| 2.74 | L537-L537 [1:23:04-1:23:04] | 60 | LESSON | - | FABIO | n/a | removing the position at a problem level | knowing where it's better to remove your position is part of the game knowing which level can create you problem | prior marked level | none stated |
| 2.75 | L539-L540 [1:23:34-1:23:48] | 60 | CONTEXT | - | FABIO | the level at the top (price not stated) | buyers at the top, absorption, speed of tape long | buyers at the top on the level that we saw with an absorption speed of tape long so they will try to reload | absorption, market speed (speed of tape) | none stated |
| 2.76 | L545-L547 [1:24:25-1:24:41] | 60 | CONTEXT | long | FABIO | high of the previous session | profile framing: yesterday's session and today's | the profile framing is long or short ; it's long ; they tap into the high of the previous session they rejected | prior-day profile, today's profile (profile framing) | none stated |
| 2.77 | L547-L548 [1:24:41-1:24:51] | 61 | LOCATION | - | FABIO | virgin POC (price not stated) | what he tried to capitalise on | what I was trying to take and to capitalize is the virgin POC test | prior-day profile (virgin POC) | role: aim of the trade ('this' the line, 'to do this in line' [?]) |
| 2.78 | L550-L551 [1:25:13-1:25:23] | 61 | LOCATION | - | FABIO | the first level marked for the day (bottom of the day) | the level marked at the start of the live | the first level that we marked for the day you remember this one is the bottom of the day when we start the life | today's profile | none stated |
| 2.79 | L552-L552 [1:25:35-1:25:35] | 61 | ENTRY (past recap; order type unknown; price not stated) | long ('this buy') | FABIO | the first level marked / bottom of the day | buy at the marked level while the sellers still controlled | this buy was counter thrown because at this moment sellers were still in control | today's profile | sellers still in control at that moment ('counter thrown' [?] = counter trend) |
| 2.80 | L552-L553 [1:25:35-1:25:46] | 61 | PROOF (AFTER the buy) | long | FABIO | after the breakout (price not stated) | aggression after the breakout | after this breakout look at this aggression there is no doubt | delta / aggressive buyers | none stated |
| 2.81 | L556-L557 [1:26:17-1:26:22] | 62 | CONTEXT | long | FABIO | n/a | profile framing and the expectation | profile framing is long we are here and we expect a long | prior-day profile, today's profile | none stated |
| 2.82 | L558-L559 [1:26:32-1:26:43] | 62 | PROOF (before/after entry unknown) | long | FABIO | the sellers' level | sellers tried two times, then broke 'with sellers absorbed and buyers rewarded' | with sellers absorbed and buyers rewarded | absorption, delta | ('then unfortunately they broke how they broke' [?]) |
| 2.83 | L559-L560 [1:26:43-1:26:53] | 62 | CONTEXT | - | FABIO | n/a | what the scenario rests on | I didn't created this based only on profile framing but I watched the live interaction between buyers and sellers | prior-day profile, today's profile, absorption, delta (live interaction) | none stated |
| 2.84 | L561-L562 [1:27:05-1:27:15] | 62 | LESSON | - | FABIO | n/a (HYPOTHETICAL contrast) | buyers absorbed, then aggressive sellers who break | if here we had this absorption okay of the buyers and then we have aggressive sellers ; well there be in a continuation because the sellers had enough strength to break | absorption, delta / aggressive sellers | buyers absorbed, then sellers aggressive and the movement breaks |
| 2.85 | L563-L565 [1:27:25-1:27:45] | 62 | REJECT | short | FABIO | from this moment (price not stated) | the sellers tried, failed, retraced, tried again, failed | there is no short opportunity that makes sense from this moment | absorption, delta / aggressive sellers | they tried they failed they retraced they tried again |
| 2.86 | L565-L566 [1:27:45-1:27:55] | 63 | ADD (past recap; funded/at-risk not stated) | long ('shoot up') | FABIO | after the test (price not stated) | reload after the test; 'zero down' [?] | it would have been an amazing risk to reward also after the test then we took the reload zero down and shoot up | absorption, delta | after the test |
| 2.87 | L566-L566 [1:27:55-1:27:55] | 63 | CONTEXT | long | FABIO | the final target | price rejecting at the final target | where is rejecting now at the final target | - | none stated |
| 2.88 | L567-L568 [1:28:06-1:28:20] | 63 | TARGET_SET | long | FABIO | final target for the position = the most sensitive level (price not stated) | position target versus day target | the final target not of the day is the final target for the position ; this is the most sensitive level | order book / big orders (sensitive level) | 'there is no reason why they will not break this level' (L568-569) |
| 2.89 | L569-L570 [1:28:30-1:28:40] | 63 | LESSON | - | FABIO | huge absorption at the top (price not stated) | alternative target if the aim is the full movement of the session | i want to take the full movement of the session then your target will be this huge absorption at the top | absorption | if the approach is to take the full movement of the session |
| 2.90 | L571-L572 [1:28:50-1:29:00] | 64 | REJECT | long | FABIO | n/a | holding for the full-session target; floating 10, 20, 30,000 that comes back | it's really frustrating for me when you are floating 10, 20, 30,000 ; And then you want to shoot for more and it comes back | day P&L | reason: giving back large floating profit is frustrating |
| 2.91 | L574-L576 [1:29:11-1:29:32] | 64 | LESSON | - | FABIO | n/a | three or four trades of about $10,000 versus one big shot of 40,000 reversing | I prefer to make three, four, $10,000 of trade, making a total of 40,000 [ASR number: check frames] | day P&L | 'bad for my mental health and it's not scalable' |
| 2.92 | L577-L578 [1:29:41-1:29:51] | 64 | LESSON | - | FABIO | n/a (big trades filter 60 [ASR number: check frames]) | big-trades filter and the 80 range | so the big trades guys are 60 the filter it's on 60 ; one time frame that I'm loving recently that is based on the range is the 80 range | order book / big orders (filter), bar close (80 range bars) | none stated |
| 2.93 | L580-L581 [1:30:14-1:30:24] | 65 | CONTEXT | long (implied: buyers aggressive at the bottom) | FABIO | absorption at the bottom (prices not stated) | the trade they took, in volume terms: absorption at the bottom, buyers aggressive, test, explosion | buyers aggressive at the this was our trade ; they came back to test huge absorption at the bottom buyers in the body another explosion | absorption, footprint, delta / aggressive buyers | none stated |
| 2.94 | L581-L582 [1:30:24-1:30:35] | 65 | PARTIAL (past recap) | long (implied: the trade above) | FABIO | absorption at the top by the sellers (price not stated) | sellers absorbed at the top; expected a move down from there | this one was absorption at the top sellers and we could expect that from here we will go down that's the reason we take partial | absorption, footprint, delta | sellers absorbed at the top |
| 2.95 | L582-L583 [1:30:35-1:30:45] | 65 | PROOF (AFTER the partial) | long | FABIO | after the partial (price not stated) | buyers absorb the sellers; first sign of weakness | and then the buyers absorb sellers aggressive buyers here when we have the first sign of weakness | absorption, delta / aggressive buyers | none stated |
| 2.96 | L583-L583 [1:30:45-1:30:45] | 65 | LESSON | - | FABIO | n/a | the same read on several chart types | i can go on 80 range i can go on 40 range i can go on one minute is it visible yes | bar close (80 range, 40 range, 1 minute) | none stated |
| 2.97 | L584-L584 [1:30:55-1:30:55] | 65 | REJECT | short | FABIO | n/a | short for the whole session | does this mean that we are going short for all the session no | - | reason: it only means he found a wall |
| 2.98 | L584-L585 [1:30:55-1:31:05] | 65 | LOCATION | - | FABIO | the wall (price not stated) | a wall identified earlier; market can reject there | i found a wall here there is a wall ; this wall got identified to us before | order book / big orders (wall) | none stated |
| 2.99 | L586-L586 [1:31:13-1:31:13] | 66 | LOCATION | - | FABIO | next level after the wall (price not stated) | next level if the wall breaks | if this wall gets broken where can we go we have already the level ready | order book / big orders | if this wall gets broken |
| 2.100 | L588-L593 [1:31:34-1:32:18] | 66 | LESSON | - | FABIO | n/a (HYPOTHETICAL) | if the level breaks: breakout, test on the absorbed sellers, then a follow-up | breakout test probably on the absorbed sellers like these and then you can consider a follow-up ; you need to have this breakout | absorption, delta | you need the breakout, otherwise this is a standpoint of control of the sellers |
| 2.101 | L595-L598 [1:32:31-1:32:50] | 66 | LESSON | - | FABIO | n/a | qualifying an area, way one: profile framing | the three main catalyst that they watch are the following ; so it can be the value area I the value area low or the POC | VAH/VAL/POC, prior-day profile | an area from profile framing |
| 2.102 | L599-L604 [1:33:01-1:33:52] | 67 | LESSON | long | FABIO | strong buy area (HYPOTHETICAL) | way two: order interaction using the trades; absorption of the sellers or aggression with result | the second reason I can do this is based on the observation of order interaction using the trades ; I have here an absorption that is so strong of the sellers for two times trade okay this is a strong buy area | absorption, delta, order book / big orders | absorption of the sellers, or aggression with result, makes a strong buy area |
| 2.103 | L606-L609 [1:34:06-1:34:27] | 67 | LESSON | short (stop above, L610) | FABIO | n/a (HYPOTHETICAL) | consistent absorption of aggressive buy orders at the top | if here I have a consistent absorption of aggressive buy orders on the top ; I have either the fading reversal | absorption, delta / aggressive buyers | consistent absorption of the aggressive buy orders at the top |
| 2.104 | L610-L611 [1:34:38-1:34:48] | 68 | LESSON | short (stop above) | FABIO | n/a (HYPOTHETICAL) | the fade: lower win rate, huge risk to reward | you trade the fade with a stop loss above and you try to take the beginning of the move for a huge risk to reward | - | 'even if your win rate will be lower' |
| 2.105 | L611-L614 [1:34:48-1:35:20] | 68 | LESSON | short (sellers take control) | FABIO | n/a (HYPOTHETICAL) | the confirmed fade: wait for the aggressive sellers to take control, then engage | you can trade the confirmed fade setup ; you wait for the aggressive sellers to take control of the movement that you qualified | delta / aggressive sellers, absorption | aggressive sellers take control of the movement you qualified; high win rate |
| 2.106 | L615-L616 [1:35:32-1:35:43] | 68 | LESSON | - | FABIO | n/a | way three: delta profile from fixed range | way to qualify area is using the delta profile from fixed range | delta profile from a fixed range [new source] | none stated |
| 2.107 | L617-L618 [1:35:47-1:35:55] | 68 | CONTEXT | - | FABIO | the area (price not stated) | a reload happening now; absorption of the buyers between the areas | this is a reload like I told you ; between these area you have this absorption | absorption, order book / big orders | none stated |
| 2.108 | L619-L620 [1:36:05-1:36:15] | 69 | REJECT | - | FABIO | n/a | other trades today | i will not take other trades okay because we already took amazing setup for today | day P&L | reason: the setup for today was already taken |
| 2.109 | L620-L622 [1:36:15-1:36:36] | 69 | LESSON | long ('skyrocket') | FABIO | n/a (HYPOTHETICAL: the same setup as the trade taken) | sellers absorbed at the bottom, buyers absorbed at the top, breakout of compression, reaction, test with aggressive sellers | sellers at the bottom absorbed sellers at the bottom absorbed buyers at the top absorbed buyers at the top absorbed ; perfect breakout of compression reaction phase test with aggressive sellers skyrocket to the moon | absorption, delta / aggressive sellers, bar close | none stated |
| 2.110 | L624-L624 [1:36:57-1:36:57] | 69 | REJECT | - | FABIO | close to the wall (price not stated) | the setup above, taken right next to the wall | it's not a smart setup that's the reason i will not consider it | order book / big orders (wall) | reason: really close to the wall |
| 2.111 | L625-L626 [1:37:08-1:37:18] | 70 | LESSON | - | FABIO | the wall (price not stated) | if the wall is pushed the momentum shows | if you manage it's lower probability but if you manage to push this level you have an aggression that is interesting | delta / aggressive orders, order book (wall) | if you break this wall you have the momentum; lower probability |
| 2.112 | L627-L628 [1:37:28-1:37:39] | 70 | LESSON | - | FABIO | n/a (35 to 40% [ASR number: check frames]) | the confirmed fade is the safe setup; the fade has a low win rate and a lot of reward | this one is the safe setup the confirm fate setup okay the fate setup it's having as I told you 35 to 40% but with a lot of risk reward | - | ('fate' [?] = fade) |
| 2.113 | L628-L633 [1:37:39-1:38:25] | 70 | LESSON | - | FABIO | n/a | way four: the origin of the move using price; the control area | a fourth way to qualify the area where you can execute from that is the origin of the move using price ; you can reason in the control area | swing high/low (price action), absorption | area explanation continues after L633 |
| 3.1 | L636-L637 | 68 | LESSON | - | FABIO | none (concept) | area that controls price (supply/demand) | "control area is the study of the area that is controlling price." | other: supply/demand control area [new source] | none stated |
| 3.2 | L638-L642 | 68 | LESSON | - | FABIO | demand under supply (chart, no prices) | which area is more important | "till we don't break it this demand is controlling" ; "pair with order flow maybe it's an absorption maybe it's an exhaustion" | other: supply/demand control area [new source]; absorption (exhaustion named too) | demand is the control area until it is broken; broken level makes the other area meaningless |
| 3.3 | L643-L649 | 69 | LESSON | - | FABIO | supply area, demand area (chart, no prices) | flip of control when a consolidation breaks | "When I break this consolidation phase My demand gets control" | other: supply/demand control area [new source]; swing structure | control stays with the sellers "as much as the structure is telling me that the sellers are in control"; flips when the demand breaks it |
| 3.4 | L650-L651 | 69 | LESSON | - | FABIO | area (no price) | taking part of profit at an area | "take out part of my profit on this area because I can't reverse" [?] (teaching, not a trade; kind HYPOTHETICAL) | other: control area | "with a confirmation that the sellers are in control" |
| 3.5 | L652-L655 | 70 | LESSON | long | FABIO | broken demand becomes support | bias flip to long after break | "when I break this becomes the demand so I can continue to search long" | other: control area; swing structure | after the break of the level; "you will have some stop loss but they are part of the game" |
| 3.6 | L656-L659 | 70 | PROOF (AFTER) | long | FABIO | area he marked in advance (price not stated) | buyers at the marked area, test after break | "the area that I marked for you again for the fourth time today rejected amazingly buyers" ; "when we break this we test they tested yes" | absorption; swing; marked area | break, then test, then "zero draw[down]" (cut off) |
| 3.7 | L660-L662 | 70 | LESSON | long | FABIO | pattern (chart, no prices) | absorbed sellers, buyers at top, breakout, test | "you are long of bias okay start to notice absorbed sellers buyers at the top break out and testing with absorption on the bottom" | absorption; delta / aggressive buyers | you are long of bias |
| 3.8 | L663-L666 | 71 | LOCATION | - | FABIO | level with absorbed buyers (price not stated) | level of absorbed buyers | "here we have a lot of absorbed buyers this means that this level for sellers is interesting" | absorption | role: interesting level for sellers; "all this area is not interesting" otherwise |
| 3.9 | L667-L669 | 71 | CONTEXT | long | FABIO | same level, long side | squeeze if buyers take the level | "if the buyers take control also over this level that we skyrocket here" ; "no way around it we squeeze it" | absorption; delta / aggressive buyers | buyers take control over the absorbed-buyers level |
| 3.10 | L670-L673 | 72 | CONTEXT | long | FABIO | live chart, level not stated | same setup as before, missing aggressive sellers | "absorption at the bottom buyers at the top you break and you test zero draw down" ; "we miss the aggressive sellers they didn't do" | absorption; delta / aggressive sellers | "I think they can come back print aggressive sellers and then go up"; setup incomplete until aggressive sellers print |
| 3.11 | L674-L674 | 72 | LOCATION | long | FABIO | the top of the range (price not stated) | break of the top | "it will explode up it will explode if they break this" | swing high | if they break the top |
| 3.12 | L675-L678 | 72 | PROOF (before any entry) | long | FABIO | CVD vs price at the top | cumulative volume delta, delta candlestick | "with the cvd they are already above the top it means that they are continuing to load" | delta (CVD) | none stated |
| 3.13 | L679-L681 | 73 | PROOF (before any entry) | long | FABIO | top of the range | CVD sell candle printing green | "they have a cvd cell candle but the candle is printing green so they are absorbing with passive liquidity" | delta (CVD), absorption, order book (passive liquidity) | none stated |
| 3.14 | L682-L684 | 73 | PROOF (before any entry) | long | FABIO | wall at the top | delta candles closing long inside a wall | "the buyers are putting back again passive order wall and they are pushing the auction down" [?] | order book (passive wall), delta | he expected sellers to take control inside a wall and says this is "not common" |
| 3.15 | L685-L688 | 73 | CONTEXT | - | FABIO | horizontal level, "a big gamma level" (price not stated) | fourth rejection at the level | "for the fourth time they got rejected on the level" | other: gamma level [new source]; swing level | none stated |
| 3.16 | L689-L692 | 74 | LESSON | - | FABIO | - | consolidation before trend | "you cannot expect always action you need to build some patience" | time of day / session phase | none stated |
| 3.17 | L693-L695 | 74 | CONTEXT | - | FABIO | - | chat asks whether he is loading | "no no i'm not loading guys i'm solving cash sheet" ; "i was trying to hide that i was loading but it's visible now" [?] two readings, see flags | - | none stated |
| 3.18 | L696-L697 | 74 | PROOF (before any entry) | long | FABIO | area (no price) | absorption on the chart | "look at this absorption look at this absorption" | absorption | none stated |
| 3.19 | L698-L704 | 75 | LESSON | long | FABIO | gap between two candles inside the area | next candle after the gap: rebalance and reject, or eat the gap | "if the candle next rebalance the gap now they rebalance and close green" ; "if the candle eat the gap on the downside ... completely absorbed" | gap (fair value gap family); bar close (timeframe not stated) | next candle closes green after rebalancing the gap -> violent move up; next candle eats the gap down to the start of the move -> absorbed (move fails) |
| 3.20 | L705-L707 | 75 | PROOF (before any entry) | long | FABIO | the candle after the gap | close, delta bomb | "the candle close purple and what happened market push down look at the delta bomb now all this aggressive sell all this pressure got confirmed or absorbed" [?] | bar close (timeframe not stated), delta / aggressive sellers, absorption | he does not resolve confirmed vs absorbed in these words (next row says long) |
| 3.21 | L708-L708 | 76 | CONTEXT | long | FABIO | - | reads the delta as long absorbed | "I think we continue long guys I think we continue long" | delta, absorption | none stated (bias, no order stated) |
| 3.22 | L709-L714 | 76 | LOCATION | long | FABIO | levels he marked: decision level from the downside; level for a potential up squeeze (prices not stated) | gap start not yet rebalanced | "this as a decision level from the downside and this level for a potential up squeeze" ; "they didn't yet rebalance the beginning of the level" | gap, profile (marked using the profile) | role: decision level (down) and up-squeeze level; gap start not yet rebalanced |
| 3.23 | L715-L715 | 76 | LOCATION | long | FABIO | the level he marked (price not stated) | price returned to the marked level | "it went back to the level this is the level that we marked" | marked level | none stated |
| 3.24 | L716-L717 | 77 | LESSON | long | FABIO | the marked level | hypothetical: aggressive absorption then long (kind HYPOTHETICAL) | "print this aggressive absorption and it goes long like he did here exactly like he did here just for the sake of making sure that the setup is complete" | absorption, delta / aggressive orders | setup is complete only with the aggressive order he says was missed |
| 3.25 | L717-L717 | 77 | CONTEXT | - | FABIO | - | news timing | "we have news in five minutes let's see" | news, time of day | none stated |
| 3.26 | L718-L718 | 77 | LESSON | - | FABIO | - | big-trade filter size | "with 30 you have more possibility with 60 you have less possibility" | big trades (filter size, [ASR number: check frames]) | none stated |
| 3.27 | L719-L721 | 77 | LESSON | - | FABIO | - | answers a viewer asking to lower the big-trade value | "do you consider to lower the value of BT no there is volume yet still 77 here speed of tape was so big" (kind VIEWER_Q) | big trades, market speed (speed of tape), delta (CVD) | none stated |
| 3.28 | L721-L722 | 77 | CONTEXT | - | FABIO | - | volatility ahead because of news | "they are preparing guys because there is volatility in four minutes" | news, time of day | none stated |
| 3.29 | L723-L724 | 77 | LOCATION | long | FABIO | the buy area he marked earlier (price not stated) | price taps the buy area before news | "they tap into the buy area that we saw" | marked area, time of day / news | none stated |
| 3.30 | L725-L727 | 78 | PROOF (before any entry) | - | FABIO | inside the area | big trades appear near news | "now we have three big trades in two candles it means that they are fighting here" | big trades, time of day / news | none stated |
| 3.31 | L728-L730 | 78 | CONTEXT | - | FABIO | sellers' big order (price not stated) | is the aggressive sellers' big order broken or still valid | "this aggressive seller here broken or still valid is still in control still valid okay" | order book / big orders, delta / aggressive sellers | role: sellers' control level; valid until broken |
| 3.32 | L731-L734 | 78 | CONTEXT | - | FABIO | the two extremes (prices not stated) | battle at the two areas, news gives the volatility burst | "the battle to decide is in these two areas okay the extreme" | absorption, order book / big orders, news | none stated |
| 3.33 | L735-L738 | 79 | REJECT | short | FABIO | viewer Leonardo's short (price not stated) | no short against the bias while the auction is on | "I will not consider a short here for only one reason" ; "the auction is still on" ; "I prefer not to go opposite to the direction of the bias" | time of day / session (auction state), delta | "of course if we break this level i change my mind but i want to see the market before breaking" |
| 3.34 | L739-L743 | 79 | PROOF (before any entry) | long | FABIO | level they are trying to break (price not stated) | speed of tape, absorption on buy side | "absorption on the buy side and confirmation on the downside" | market speed (speed of tape), absorption, bar close | next row: depends on how the candle closes |
| 3.35 | L743-L745 | 79 | CONTEXT | long | FABIO | the burst candle (timeframe not stated) | candle close decides the side | "if this candle gets completely rejected then in this case we can have a move up" ; "if get accepted is a squeeze on the downside" | bar close (timeframe not stated) | candle completely rejected -> move up; candle accepted -> squeeze on the downside |
| 3.36 | L746-L747 | 80 | REJECT | - | FABIO | the cluster / tape bit | does not execute during the candle, only watches the close | "you just want to see how the candle close you don't want to execute" | bar close (timeframe not stated), market speed | wait for the candle close; "a moment where the dominance is completed" |
| 3.37 | L748-L750 | 80 | PROOF (before entry) | long | FABIO | the almost-closing candle | candle closing with speed of tape eating the clusters | "what do you see long or short" ; "you see long" | market speed (speed of tape), bar close, absorption | candle closes with the speed of tape eating the clusters |
| 3.38 | L751-L753 | 80 | ENTRY (limit order implied by later "get filled"/"remove the order"; price not stated) | long | FABIO | level of the test of the broken level (price not stated) | places the last sniper order and waits for a test | "you have the last trade of the day let's see if it test" ; "i will go for the last one" | market speed, absorption, bar close | "let's see if it test": a test of the level is needed to get filled |
| 3.39 | L754-L755 | 81 | CONTEXT | - | FABIO | - | day trade count | "we did uh three trades one was i don't remember guys how many are we made" | - | none stated |
| 3.40 | L756-L756 | 81 | PROOF (before fill) | long | FABIO | level of the break (price not stated) | break that did not complete: fakeout | "it broke but was a fakeout it didn't complete the breakout" ; "wait for the close" | market speed (speed of tape), delta / aggressive orders, bar close | "wait for the close" (lesson he repeats) |
| 3.41 | L757-L759 | 81 | HOLD | long | FABIO | resting order | waits for the test and the fill | "let's see if it test" ; "let's see if we get filled" | market speed (speed of tape) | needs the test to fill |
| 3.42 | L760-L761 | 81 | LOCATION | long | FABIO | "the last point of aggression of the sellers" (price not stated) | will the buyers hold the ground there | "the last point of aggression of the sellers i'm really curious to see if they hold the ground or not" [?] role of the level (entry vs hold reference) is not settled | delta / aggressive sellers, swing | "if they hold the ground or not" |
| 3.43 | L762-L764 | 82 | PROOF (before fill) | long | FABIO | rejection decision level, horizontal level (price not stated) | fight at the level | "they are fighting like hell on this horizontal level the speed of tape it's incredible" | market speed (speed of tape) | none stated |
| 3.44 | L765-L766 | 82 | PROOF (before fill) | long | FABIO | the level the order was at | price breaks without testing; order unfilled by one tick | "we didn't got filled for like one tick" ; "it's not valid anymore" | market speed | "if they break this level ... they will never test here" |
| 3.45 | L767-L770 | 82 | REJECT | long | FABIO | the unfilled order | does not want a fill that comes back and breaks him | "if it comes back it break me So it's not so interesting" | swing, market speed | fill only interesting if it does not come back through |
| 3.46 | L771-L773 | 83 | EXIT (order cancelled, never filled) | long | FABIO | the resting order | removes the order | "if I don't get field I remove the order" ; "we removed anything anyway but it's good that we remove" | - | rule: unfilled order is removed |
| 3.47 | L774-L777 | 83 | CONTEXT | long | FABIO | buyers' controlled area on the deep effort study (price not stated) | deep effort shows who controls the auction | "this is deep effort is showing you who is in control" ; "buyers control of the option" | other: deep effort study (proprietary) [new source] | none stated |
| 3.48 | L778-L780 | 83 | CONTEXT | long | FABIO | level with the buyers' wall; the top; "the final target" (prices not stated) | probability of tapping the top and extending | "the probability instead of breaking this level is that we tap into top" ; "potentially reaching also the final target" | other: deep effort study [new source], order book (wall) | no order or position stated here; "final target" is not tied to the removed order |
| 3.49 | L781-L781 | 84 | CONTEXT | - | FABIO | most important sell level (price not stated) | weak sell level | "you see this one is not so strong didn't even got marked this absorption guys" | absorption | none stated |
| 3.50 | L784-L786 | 84 | CONTEXT | long | FABIO | buyer-controlled level (price not stated) | "you can put this one and see"; expects a surge (second order unsettled, see flags) | "now that you know that this level is controlled by buyers ... you can put this one and see okay" ; "now i expect a surge" | other: deep effort study [new source] | none stated |
| 3.51 | L787-L789 | 84 | CONTEXT | long | FABIO | top of the range (price not stated) | if filled on the downtick the result is already a stated multiple | "if this will that field does on the downtick it will already be one to one point five" [?] [ASR number: check frames] | market speed (speed of tape) | garbled; reading depends on whether an order was resting (see flags) |
| 3.52 | L790-L791 | 85 | PROOF (before any entry) | long | FABIO | absorbed order clusters 319 and 104 [ASR number: check frames] | calm in the volatility | "319 absorbed orders and one 104 on the bottom" | absorption, big orders, market speed | none stated |
| 3.53 | L792-L795 | 85 | CONTEXT | long | FABIO | rebalance level "three three 1.9" [ASR number: check frames] | price skyrockets after the speed-of-tape down was absorbed; he states his order is removed | "all the speed of tape down and everything got absorbed now they are coming to rebalance on the three three 1.9 of course I removed" | market speed, absorption | none stated |
| 3.54 | L795-L797 | 85 | LESSON | long | FABIO | viewers filled at the level (kind VIEWER_Q: he holds no position) | advises stop to entry for viewers who got filled | "go risk-free yeah go risk-free don't give back not even ten dollars to the market" | market speed (volatility spike risk) | only "if you got filled here"; reason: "don't let this volatility take you out with a spike" |
| 3.55 | L798-L798 | 85 | LESSON | - | FABIO | - | which tool is on screen | "this is not the delta it's the speed of tape" | market speed (speed of tape) | none stated |
| 3.56 | L800-L801 | 86 | CONTEXT | - | FABIO | liquidity wall at the high (price not stated) | absorption of sellers = wall; break either way runs | "there is a liquidity wall here and if this high gets broken we really skyrocket if we break this down on the other side we go down heavy" | absorption, order book (liquidity wall) | if the high breaks: skyrocket; if the low breaks: down heavy |
| 3.57 | L802-L804 | 86 | LESSON | short | FABIO | viewer Leonardo's short from the high (kind VIEWER_Q: he holds no position) | advises risk-free (stop to entry) for the viewer's short | "you could go risk free because you have you are short from here zero down" ; "good to take risk out of the market when the situation is so heated" | market speed / volatility | "if you are still short"; heated situation |
| 3.58 | L805-L809 | 86 | LOCATION | long | FABIO | aggressions 319 and 104 at the breakout level [ASR number: check frames] | aggression plus breakout of the level | "this aggression 319 this aggression 104 and this breakout of the level" ... "makes you think long makes you think an aggression" | delta / aggressive buyers, big orders | none stated |
| 3.59 | L809-L812 | 87 | CONTEXT | long | FABIO | the level with stacked sellers and absorbed buyers | break releases stacked sellers and absorbed buyers | "if they manage to break this you agree with me that all the sellers that are stacked and all these absorbed buyers needs to be released" ; "this movement is fast" | absorption, order book / big orders, market speed | if they manage to break the level |
| 3.60 | L813-L817 | 87 | PROOF (before any entry) | - | FABIO | two purple clusters, 104 and 300 [ASR number: check frames] | repeated loading into the clusters | "how many times they try to load and break these two clusters" ; "the 104 and the 300 that are standing still" | big orders, absorption | none stated |
| 3.61 | L817-L820 | 88 | CONTEXT | - | FABIO | 319 or the one on four [ASR number: check frames] | break or continued dance of initiative and absorption | "either they reject on the 319 or the one on four and they always dance here" | absorption, big orders | break of one of the clusters |
| 3.62 | L821-L822 | 88 | PROOF (before any entry) | - | FABIO | - | buyers stopped participating | "the buyers on the other side stop participating 10 minutes ago" | delta / aggressive buyers | none stated |
| 3.63 | L823-L823 | 88 | LESSON | - | FABIO | - | delta is the input, the candle is the result | "you need to pay delta with the result because delta is the input but then you need to see what the candle does" ["pay" may be "pair"] | delta, bar close | none stated |
| 3.64 | L824-L826 | 88 | CONTEXT | short | UNKNOWN | - | chat text about Leonardo's short (who is quoted is unclear) | "Leonardo say Fabio let it go today it's all break even but because you try to short the up move yeah" | - | none stated |
| 3.65 | L827-L830 | 89 | CONTEXT | long | FABIO | wall above the upside area (price not stated) | wall as obstacle is the best behavior before a squeeze | "this is the best behavior before a squeeze this is the best behavior before shooting up" | other: deep effort study [new source], order book (wall) | none stated |
| 3.66 | L831-L831 | 89 | PROOF (before any entry) | long | FABIO | top of the range | buyers loading | "buyers are trying to load heavy" | delta / aggressive buyers | none stated |
| 3.67 | L832-L835 | 89 | LESSON | - | FABIO | - | what the deep effort study measures | "it's a proprietary study and it's based on the thickness of the book" | other: deep effort study [new source], order book (book thickness) | none stated |
| 3.68 | L836-L837 | 90 | LOCATION | short | FABIO | red area he marked (price not stated) | path of least resistance down from the red area | "this red area that I marked for you is where the part of risk resistance is on the downside so from this area the sellers are in control" ["risk resistance" is a mishearing of least resistance, not repaired] | other: deep effort study [new source] | role: sellers in control from this area |
| 3.69 | L838-L839 | 90 | LESSON | - | FABIO | between the two deep effort areas | ping-pong between the two areas | "no-brainer ping-pong between these two areas pay you a lot of money" | other: deep effort study [new source] | none stated |
| 3.70 | L840-L844 | 90 | LESSON | - | FABIO | - | no single-tool dependence | "depending completely on one indicator it's not what you want to do" ; "understand volume 360 every tool" | other: volume tools, VSA | none stated |
| 3.71 | L844-L846 | 90 | LOCATION | long | FABIO | the "bi-control" [?] area just touched (price not stated) | price touches the area again | "we are going back to the bi-control area just touched just touched let's see what they do now that we are inside the area" | marked area, other: deep effort study | none stated |
| 3.72 | L847-L849 | 91 | PROOF (before any entry) | short | FABIO | top of the area (price not stated) | buyers' first participation completely absorbed | "amazing absorption at the top this is the first time buyers participated and got completely absorbed this is a really a strong wall" | absorption, order book (wall), delta / aggressive buyers | none stated |
| 3.73 | L852-L855 | 91 | LESSON | - | FABIO | viewer's trades today (prices not stated) | asks Michael where he got stopped out and whether he trailed (kind VIEWER_Q) | "where did you got stopped out you trail your stop I want to help you" | - | none stated |
| 3.74 | L856-L856 | 92 | CONTEXT | short | VIEWER | - | chat text read aloud: short on the open, gave it back later | "I took the short on open and made a lot but all the trading after the law I didn't trade well" | - | none stated |
| 3.75 | L857-L859 | 92 | CONTEXT | short | FABIO | the viewer's open short | asks how the profit was given back | "how is it possible that that you gave back this money to the market" | - | none stated |
| 3.76 | L860-L868 | 92 | LESSON | - | FABIO | stop distance on the platform (no price) | fixed dollar risk per trade sets contract count | "you want to risk the same amount always on the single trade" ; stop set to 2500 ; "seven mini contract" ; "15" ; "six point five contracts" [ASR number: check frames] | - | contracts change with the stop distance; risk amount stays at the same figure |
| 3.77 | L869-L870 | 93 | CONTEXT | long | FABIO | the day | market only went up, all longs on the way up were taken | "today the market only went up and we managed to take all the long on the way up" | - | none stated |
| 3.78 | L870-L871 | 93 | LESSON | short | FABIO | viewer's fade of the up move | the only explanation for the loss is fading the move | "the only explanation that I can have that you lost money is that you try to short to fade this movement" | - | none stated |
| 3.79 | L871-L872 | 93 | CONTEXT | short | FABIO | inside the area | sellers in control now, still inside the area | "yes sellers are in control now we are still inside the area but sellers are controlling" | delta, absorption | none stated |
| 3.80 | L873-L875 | 94 | LESSON | - | FABIO | - | pressure management when holding a longer position | "the best exercise to really understand pressure management when controlling a longer short position" [?] | - | none stated |
| 3.81 | L876-L878 | 94 | PROOF (before any entry) | long | FABIO | numbers 250 and 108 [ASR number: check frames] | huge speed of tape but a red candle: buyers completely absorbed | "it's a problem for the buyers they got completely absorbed" | market speed, delta, bar close, absorption | if the candle closes like this it is a problem for the buyers |
| 3.82 | L879-L881 | 94 | CONTEXT | long | FABIO | buy area of the "Nasdaq efforts" [?] | wants a close above to stay long-biased | "I want to see if they can manage to close above because if I'm not wrong we are still in the buy area" | bar close (timeframe not stated), other: deep effort study [new source] | buyers must manage to close above |
| 3.83 | L882-L883 | 95 | PROOF (before any entry) | long | FABIO | - | buyers recovering | "yeah they are recovering buyers to control back" | delta / aggressive buyers | none stated |
| 3.84 | L884-L885 | 95 | LESSON | long | FABIO | the deep effort area (no price) | when the area is invalidated | "the effort is invalidated when you break it" ; "it gets invalidated if it breaks" | other: deep effort study [new source] | area is invalidated only if it breaks |
| 3.85 | L886-L887 | 95 | CONTEXT | long | FABIO | the test candle | expected a breakout and collapse; did not happen | "I was thinking that the next candle here would be a breakout so they test and they collapse" [?] | bar close, absorption | none stated |
| 3.86 | L888-L889 | 95 | HOLD | long | FABIO | the deep effort area | area still valid, buyers strong, final target up | "still the area is valid and buyers are still strong still we can go to the final target up" | other: deep effort study [new source], absorption | "the effort is invalidated when you break it" (row invalid) |
| 3.87 | L890-L890 | 95 | CONTEXT | long | FABIO | setup shown: absorption here, buyers at the top, breakout (prices not stated) | multiple entry techniques on a past trade (kind ILLUSTRATION) | "We saw multiple entry technique so for example let's see the trade off before okay you have absorption here" | absorption, delta / aggressive buyers | none stated |
| 3.88 | L891-L891 | 96 | ENTRY (limit order; price not stated; placed before the touch) | long | FABIO | "this level" after the breakout (price not stated) | limit order at the level (past trade) | "you can put a limit order this level with" | absorption, delta / aggressive buyers | setup: absorption, buyers at the top, breakout |
| 3.89 | L892-L892 | 96 | STOP_SET | long | FABIO | between this aggression (price not stated) | stop between the aggression | "a stop loss between this aggression" | delta / aggressive buyers | none stated |
| 3.90 | L892-L892 | 96 | STOP_MOVE | long | FABIO | entry (stop to zero) | stop to zero on another confirmation from the buyers | "you can put your stop loss to zero like we did before" | delta / aggressive buyers | "when you have another confirmation from the buyers" |
| 3.91 | L893-L893 | 96 | STOP_SET | long | FABIO | below the area (price not stated) | variant: enter with the stop below the area (entry order type not stated) | "you can enter with the stop loss below the area" | absorption, marked area | none stated |
| 3.92 | L893-L893 | 96 | STOP_MOVE | long | FABIO | entry (stop to zero) | variant: stop to zero when you see "this" (event not named in words) | "put your stop loss at zero when you see this" | - | "when you see this" (chart event, not spoken) |
| 3.93 | L894-L894 | 96 | CONTEXT | long | FABIO | buyers controlling the auction (kind HYPOTHETICAL) | another example trade | "you get buyers that are controlling the auction okay and you can have for example speed of tape here" | delta / aggressive buyers, market speed | none stated |
| 3.94 | L895-L895 | 96 | STOP_SET | long | FABIO | below the aggression of the buyers, below the area (price not stated; kind HYPOTHETICAL) | stop below the buyers' aggression and the area | "you can add your stop loss below the aggression of the buyers below the area" | delta / aggressive buyers | none stated |
| 3.95 | L896-L898 | 96 | ENTRY (limit order; price not stated; placed before the touch) | long | FABIO | the "best entry" area on the zoomed chart (price not stated) | precise entry area for a limit order, fill not guaranteed | "the area where you have the best entry so if we want to be precise now I don't know if we will get filled" | marked area, other: deep effort study | fill not guaranteed |
| 3.96 | L899-L899 | 96 | STOP_SET | long | FABIO | "below here" (price not stated) | stop below the entry area | "the stop loss should be below here" | marked area | none stated |
| 3.97 | L899-L900 | 96 | TARGET_SET | long | FABIO | "this target" (price not stated) | target with stated multiple 1 2 3.5 (says it is way more than one to one) | "it's only one to one no it's way more because we can go to this target" ; "it's a 1 2 3.5 it's an amazing trade" [ASR number: check frames] | - | "it's limited so if you get field it's good" [?] |
| 3.98 | L901-L902 | 97 | ENTRY (order type not stated; price not stated; kind HYPOTHETICAL) | long | FABIO | after a strong buy-candle break and a pullback candle | second execution method after break and return | "we break this with a buy candle strong and we see the market coming back printing a candle like this Here you can have another execution" | bar close, delta / aggressive buyers | break with a strong buy candle, then the market coming back |
| 3.99 | L903-L903 | 97 | STOP_SET | long | FABIO | below the aggression of the sellers (price not stated; kind HYPOTHETICAL) | stop below the sellers' aggression | "a stop loss below the aggression of the sellers" | delta / aggressive sellers | none stated |
| 3.100 | L903-L903 | 97 | TARGET_SET | long | FABIO | "the target of both" (level not stated; kind HYPOTHETICAL) | same target for both executions (no number) | "The target of both is it clear guys" | - | none stated |
| 3.101 | L903-L904 | 97 | REJECT | long | FABIO | the hypothetical second execution | does not advise it: lower grade setup | "I don't advise you do this trade there" ; "I don't like it at all" ; "this one was triple-a" ["Be set up see set up" is garbled, see flags] | - | none stated |
| 3.102 | L906-L909 | 97 | LOCATION | long | FABIO | beginning of the candle with complete control of the buyers (price not stated) | interesting area | "the area that is interesting because it's the beginning of the candle with the complete control of the buyers" | delta / aggressive buyers, bar close | none stated |
| 3.103 | L910-L911 | 98 | REJECT | - | FABIO | - | no more trades: session done, anything now is study | "the session is done" ; "anything you take from now it's to study" | time of day (end of the volatility) | major volatility of the day is over |
| 3.104 | L911-L912 | 98 | LESSON | - | FABIO | - | later setups are average | "this is an average setup guys" | - | none stated |
| 3.105 | L917-L919 | 98 | CONTEXT | long | FABIO | - | market choppy, could still go up a little | "Choppy now, okay Think we can still go up a little bit." | - | none stated |
| 3.106 | L920-L921 | 99 | LOCATION | long | FABIO | the gap on the chart (price not stated) | reloading gap when they are really aggressive | "the gap this one is the reloading gap when they are really aggressive" | gap (fair value gap family), delta / aggressive orders | none stated |
| 3.107 | L924-L927 | 99 | CONTEXT | - | FABIO | gaps from here to here (prices not stated) | gaps one after another, pressure building (volatility score 1 to 3 stated) | "another gap they are building the pressure guys" ; "even with low volatility it's a 1 to 3" | gap, market speed | none stated |
| 3.108 | L930-L931 | 100 | CONTEXT | - | FABIO | - | last comment on the move | "think probably can go also here amazing" (direction not stated) | - | none stated |

## 3.3 Trade blocks


(part 1: Is1HvdfQm5c_part1.md)

```
TRADE T1.1 - short - rows 1.29-1.35   (also rows 1.43-1.44 for timing and stop reference)
kind: HYPOTHETICAL (a teaching example with stated ratio; no price) ; speaker: FABIO
state (day/week): "the cash session open with a strong long aggression to the upside" then "they tapped into the high and they rejected" ; yesterday "closed bullish"
location: the top / "horizontal level" at the high ("test of this level") ; level type: swing high / order level (price NOT STATED)
leading signal: "crazy absorption at this horizontal level", buyers' aggression fading, failed breakout at the top (rows 1.26, 1.27, 1.28)
trigger: "the test of this level with the confirmation of absorbed buyers" after "aggressive sellers lock in the movement" ; entered BEFORE or AFTER proof: after
entry order type: unknown ; placed before the touch: unknown
initial stop: "a super small stop loss", "cover yourself above the area" ; distance: NOT STATED ; % of price: unknown (no price, no distance)
target: "shoot for a 1 to 4.5" [ASR number: check frames] ; distance: NOT STATED ; stated R:R: 1 to 4.5
management: NOT STATED (row 1.43: execute "immediately from the absorption or from the aggression", "when you see rejection you can execute")
exit: NOT STATED ; exit type: unknown
rejects: none in this block
information sources: absorption, delta / aggressive buyers and sellers, big trades ("165 contract", "2000 contract total 1400 contract total" [ASR number: check frames])
outcome: NOT STATED
horizon: NOT STATED
mirror stated?: no - do not assume
```

```
TRADE T1.2 - short - rows 1.37-1.38   (speaker: UNKNOWN for the entry)
kind: ILLUSTRATION (a chart walked through; whose trade is not settled) ; speaker: UNKNOWN
state (day/week): London session, "not so much volume" ; the session of "the second of December" is cited as the same model
location: absorption and aggression cluster at the top ; level type: order level (price NOT STATED)
leading signal: "look at this absorption at the top again", "effort candle is rewarded"
trigger: unknown ; entered BEFORE or AFTER proof: unknown
entry order type: unknown ; placed before the touch: unknown
initial stop: NOT STATED ; distance: NOT STATED ; % of price: unknown
target: "probably they squeeze the low 25 500" [ASR number: check frames] (expectation, not a stated target) ; distance: NOT STATED ; stated R:R: unknown
management: NOT STATED
exit: NOT STATED ; exit type: unknown
rejects: none
information sources: absorption, delta / aggressive sellers, footprint cluster, time of day (London session)
outcome: NOT STATED
horizon: NOT STATED
mirror stated?: no - do not assume
```

```
TRADE T1.3 - long - rows 1.61-1.79
kind: ILLUSTRATION (chart walked through live, stop rule and R:R stated, no price entry) ; speaker: FABIO
state (day/week): bias long if value says higher (rows 1.54, 1.56) ; "amazing auction today ... respecting the level like crazy"
location: the cluster tapped for the third time ("third touch") ; level type: order / footprint cluster (price NOT STATED)
leading signal: "sellers got absorbed", "buyers got the reward that the candle close long", "they are squeezing the top"
trigger: after the break and the absorbed sellers ; entered BEFORE or AFTER proof: after ("if you enter here not here still an amazing run up")
entry order type: unknown ; placed before the touch: unknown
initial stop: "covering yourself below the area" (row 1.66) ; alternative "a stop loss before the area" (row 1.74) and "a stop area 640" [ASR number: check frames] (row 1.77) ; distance: NOT STATED ; % of price: unknown
target: "target 1 to 5 1 to 4.9 at the third touch" (row 1.68) ; or "the home run" (row 1.75) ; or "the next level 25 646.39" (row 1.79) ; stated R:R: 1 to 5 / 1 to 4.9 [ASR number: check frames] ; win rate 30 to 35 percent for the home run version (row 1.76)
management: NOT STATED
exit: NOT STATED ; exit type: unknown
rejects: row 1.69 greedy 1:10 targets ; row 1.70 another setup with inefficiency ; row 1.73 continuing to short against the market ; the outcome at the next level is a "failed auction" (row 1.80, side not stated)
information sources: absorption, delta / aggressive buyers, footprint cluster, big trades ("97 sellers absorbed", "75 contract" [ASR number: check frames])
outcome: NOT STATED
horizon: NOT STATED
mirror stated?: no - do not assume
```

```
TRADE T1.4 - long - rows 1.97-1.103, 1.106, 1.110-1.112 (the plan rows 1.111-1.112 are the end of this part)
kind: VIEWER_Q with a conditional HYPOTHETICAL plan ; speaker: FABIO
state (day/week): "the cash session open with a strong long aggression to the upside" then rejection ; the long idea is judged at a level where "buyers are protecting"
location: "this cluster one two six" [ASR number: check frames] and the reclaimed level ; level type: order cluster (price NOT STATED)
leading signal: "this aggression that got absorbed here and this reclaim of the level that got reconfirmed here"
trigger: recover "this huge candle" and see "some big trades" ; entered BEFORE or AFTER proof: after
entry order type: unknown ; placed before the touch: unknown
initial stop: "really high stop loss" (row 1.101) ; distance: NOT STATED ; % of price: unknown
target: "681" called "a smart TP" [ASR number: check frames] and "the target that the other guy say" ; distance: NOT STATED ; stated R:R: "one to two point five" [ASR number: check frames]
management: NOT STATED
exit: NOT STATED ; exit type: unknown
rejects: row 1.99 trying a long in "no-man land" ; row 1.92/1.94 no trade without aggressive big-order support
information sources: absorption, big trades, delta / aggressive buyers, speed of tape, bar close (TF not stated)
outcome: NOT STATED
horizon: NOT STATED
mirror stated?: no - do not assume
```


(part 2: Is1HvdfQm5c_part2.md)


Only two blocks: the range is mostly a viewer Q and A and a lecture. HYPOTHETICAL and VIEWER_Q items (short-now, fade, confirmed fade, stop-in-profit alternatives, the 'one to four' viewer) are decision rows only. The first-person trade rows are recaps in the past tense; entry prices, stop levels and money were not spoken in this range.

```
TRADE T2.1 - long - kind: LIVE_TRADE - speaker: FABIO (walk-through of a position he took today; the words 'we took', 'our trade', 'we take partial' settle it) - rows 2.54, 2.79, 2.82, 2.31, 2.33, 2.38, 2.40, 2.41, 2.42, 2.43, 2.45, 2.53, 2.57, 2.66, 2.67, 2.73, 2.86, 2.88, 2.94
state at start: continues from earlier part (unknown)
state (day/week): "the profile framing is long" ; they "tap into the high of the previous session they rejected" ; sellers were still in control at the first marked level, then "sellers absorbed and buyers rewarded" ; later "we are stuck we are inside this range"
location: the marked absorption area at the bottom of the day; "the virgin POC test" as the aim ; level type: absorption / acceptance area, prior-day POC (virgin) ; position at the start of the move: "inside from the beginning of the move"
leading signal: "sellers absorbed" at the bottom, buyers aggressive, "breakout of compression", "reaction phase", "test with aggressive sellers"
trigger: NOT STATED for the live entry ; the illustrated entry rule is "absorption in one candle, two following absorption, then an aggression" ; entered BEFORE or AFTER proof: unknown for the live entry (the illustration row 2.45 says after the proof)
entry order type: unknown ; placed before the touch: unknown
initial stop: NOT STATED as a price ; his rule words: "if it break this level the analysis invalidator" (row 2.42) ; distance: NOT STATED ; % of price: unknown (no price and no distance stated)
target: "the final target for the position", "the most sensitive level" (price NOT STATED) ; alternative "this huge absorption at the top" for a full-session approach (row 2.89) ; distance: NOT STATED ; stated R:R: "one to three point six" and "one to three" (row 2.67, [ASR number: check frames]) ; viewers' "full target one two three" (row 2.72)
management: STOP_MOVE to zero rows 2.33, 2.43 (also risk-free rows 2.40, 2.41) ; PARTIAL at the sellers' absorption at the top row 2.94 (first take profit at an important level, row 2.53) ; ADD "the reload" after the test row 2.86 ; trail "below the big trade" stop in profit (HYPOTHETICAL, row 2.66) ; order of events between rows is as spoken in the recap and not settled by the ASR
exit: NOT STATED in this range ("where is rejecting now at the final target", row 2.87) ; exit type: unknown
rejects: short for all the session (row 2.97) ; holding for the full-session target (row 2.90) ; marking intermediate levels (row 2.23)
information sources: absorption, delta / aggressive buyers and sellers, order book / big orders (big trades filter 60), speed of tape, prior-day profile (previous session high, virgin POC), today's profile, inefficiency (gap), 80 / 40 range bars
outcome: no money or R stated for his own trade ; R multiples are quoted only for viewers or as alternatives (rows 2.71, 2.67)
horizon: "not even one candle" to stop at zero (row 2.43) ; otherwise NOT STATED
mirror stated?: no - do not assume
```

```
TRADE T2.2 - long - kind: LIVE_TRADE (thin; may be the same position as T2.1 or an earlier trade of the day; the ASR does not settle it) - speaker: FABIO - rows 2.78, 2.79, 2.80
state at start: continues from earlier part (unknown)
state (day/week): "sellers were still in control" at that moment ; profile framing long
location: "the first level that we marked for the day ... the bottom of the day when we start the life" ; level type: day low / marked level
leading signal: NOT STATED beyond the marked level
trigger: "this buy" at the marked level, "counter thrown" [?] ; entered BEFORE or AFTER proof: unknown (aggression "after this breakout", row 2.80, is read after the buy)
entry order type: unknown ; placed before the touch: unknown
initial stop: NOT STATED ; distance: NOT STATED ; % of price: unknown
target: "the virgin POC test" as the aim (row 2.77) ; distance: NOT STATED ; stated R:R: NOT STATED
management: NOT STATED
exit: NOT STATED ; exit type: unknown
rejects: none stated
information sources: today's profile, prior-day profile (virgin POC), delta / aggression
outcome: NOT STATED
horizon: NOT STATED
mirror stated?: no - do not assume
```


(part 3: Is1HvdfQm5c_part3.md)

```
TRADE T3.1 - long - rows 3.36-3.46 (plus context rows 3.50, 3.51, 3.53)
kind: LIVE_TRADE (a resting order he calls "the last trade of the day"; it was NEVER filled, so there is no position, no stop and no P&L) ; speaker: FABIO
state at start: new trade in this part; earlier in the day "we did uh three trades" (row 3.39) and "the market only went up and we managed to take all the long on the way up" (row 3.77); news "in five minutes" / "in four minutes" (rows 3.25, 3.28)
state (day/week): long bias ("I think we continue long guys", row 3.21); "the auction is still on" (row 3.33)
location: "the last point of aggression of the sellers" (row 3.42; price not stated) ; level type: other (swing of the sellers' last aggression); the role (limit location vs level to hold) is not settled by the words
leading signal: speed of tape plus absorption on the buy side (row 3.34), candle close awaited (rows 3.35, 3.36, 3.37)
trigger: "let's see if it test" (row 3.38): a test of the broken level ; entered BEFORE or AFTER proof: order placed after the read "you see long" (row 3.37); the test and fill never came
entry order type: limit implied ("get filled", "remove the order"; the word limit is not said for this order) ; placed before the touch: yes (rows 3.41, 3.44)
initial stop: NOT STATED ; distance: NOT STATED ; % of price: unknown
target: NOT STATED for this order ("the final target" in row 3.48 and "one to one point five" in row 3.51 are not tied to it in his words) ; distance: NOT STATED ; stated R:R: NOT STATED
management: none (no fill). Row 3.46: "if I don't get field I remove the order".
exit: "if I don't get field I remove the order"; "it's not valid anymore" (row 3.44) ; exit type: order cancelled, never filled
rejects: row 3.36 (does not execute before the candle close); row 3.45 ("if it comes back it break me So it's not so interesting"); row 3.33 (viewer's short, against the bias)
information sources: market speed (speed of tape), absorption, delta / aggressive sellers, big orders, bar close (timeframe not stated), news, other: deep effort study [new source]
outcome: none (not filled by "one tick", row 3.44); after he removed it the market "skyrocket[ed]" (row 3.53) and he says "of course I removed" (row 3.53)
horizon: NOT STATED
mirror stated?: no - do not assume (he separately refuses a short against the bias, row 3.33)
open question: rows 3.50, 3.51 read as a possible SECOND resting order ("you can put this one and see", "if this ... filled ... one to one point five"); flagged, not rowed as an ENTRY.

TRADE T3.2 - long - rows 3.87-3.92
kind: ILLUSTRATION ("the trade off before", "like we did before"; a past trade of the day walked through as entry techniques) ; speaker: FABIO
state at start: continues from earlier part (unknown); the setup is "absorption here and you have buyers at the top, you have this breakout" (row 3.87)
state (day/week): NOT STATED here
location: "this level" after the breakout (price not stated) ; level type: other
leading signal: absorption at the bottom, buyers at the top, breakout
trigger: the breakout of the buyers' move ; entered BEFORE or AFTER proof: NOT STATED (the limit order is placed at the level)
entry order type: limit ("you can put a limit order this level", row 3.88) ; placed before the touch: yes (limit); variant B "you can enter with the stop loss below the area" (row 3.91) has no order type
initial stop: variant A "a stop loss between this aggression" (row 3.89) ; variant B "the stop loss below the area" (row 3.91) ; distance: NOT STATED ; % of price: unknown
target: NOT STATED ; distance: NOT STATED ; stated R:R: NOT STATED
management: STOP_MOVE row 3.90 (stop to zero on "another confirmation from the buyers"); STOP_MOVE row 3.92 (stop at zero "when you see this")
exit: NOT STATED ; exit type: unknown
rejects: none in these rows
information sources: absorption, delta / aggressive buyers
outcome: NOT STATED here (rows 3.10 and 3.6 only say "zero draw down" for the pattern)
horizon: NOT STATED
mirror stated?: no - do not assume

TRADE T3.3 - long - rows 3.95-3.97
kind: HYPOTHETICAL (a number is stated, so it gets a block: "if we want to be precise ... I don't know if we will get filled"; no position held) ; speaker: FABIO
state at start: new in this part; the buyers' deep effort area is "still valid" (row 3.86)
state (day/week): session after the main volatility; row 3.103 says anything now is study, row 3.104 calls the next setups average
location: "the area where you have the best entry" (price not stated) ; level type: other (deep effort area)
leading signal: buyers' control and speed of tape (rows 3.93, 3.86)
trigger: price coming to the area ; entered BEFORE or AFTER proof: NOT STATED (limit)
entry order type: limit ("if you get field it's good", "I don't know if we will get filled") ; placed before the touch: yes
initial stop: "the stop loss should be below here" (row 3.96; price not stated) ; distance: NOT STATED ; % of price: unknown
target: "this target" (row 3.97; level not stated) ; distance: NOT STATED ; stated R:R: "1 2 3.5" [ASR number: check frames] and "it's only one to one no it's way more"
management: NOT STATED
exit: NOT STATED ; exit type: unknown
rejects: row 3.101 rejects the second execution method of rows 3.98, 3.99, 3.100 ("I don't advise you do this trade there")
information sources: other: deep effort study [new source], delta / aggressive buyers
outcome: none (hypothetical)
horizon: NOT STATED
mirror stated?: no - do not assume
```


## 3.4 Rejections and conditions


(part 1: Is1HvdfQm5c_part1.md)

- 1.17: no trading when emotionally unfit ("you stay out of the market there").
- 1.19: no 5 to 25 trades per day.
- 1.49: no long while the downside pressure is visible.
- 1.69: no "super sniper" 1 to 10 targets (greed lowers the hit rate).
- 1.70: a setup that is "a little bit difficult to take" because of the inefficiency.
- 1.73: continuing to short after the market showed the opposite is "wanting to be right".
- 1.86: drops the long idea at the first touch, preferring the first touch ("i always think about the first touch").
- 1.88: counter trend trades (sellers absorbed or back to a balance level): "I don't like to take them".
- 1.92: nothing to execute when aggressive buyers show no big orders ("high in the curve").
- 1.94: usually no trades without support from aggressive order market participants, unless delta, profile or footprint confirm.
- 1.99: no long in "no-man land".
- 1.108: momentum breakout exactly at a level at the value area low is "the worst case" (limit wall, consolidation).
- Conditions: 1.29 sellers must lock the movement with result; 1.30 confirmation of absorbed buyers; 1.43 a level to cover behind must exist; 1.44; 1.45 buyers stay in control until broken from the downside; 1.52; 1.53 sellers push against the wall; 1.54 if the bias is long; 1.89 if the level breaks, squeeze up; 1.109 sell continuation if the level breaks out; 1.111 recover the huge candle and see big trades; 1.77 the stop area only if he needs to go long term.


(part 2: Is1HvdfQm5c_part2.md)


- 2.5 REJECT (short): We don't have the clue that the aggressive sellers are strong enough -- reason/condition: buyers tested four times and each time rejected; sellers not shown strong enough to break
- 2.8 REJECT (short): if you are waiting for a confirmation to get short wait for this level to collapse -- reason/condition: no short until the level collapses, stops printing and breaks cleanly ('this week' [?])
- 2.23 REJECT (-): it's not necessary to mark intermediate level that are useless for us -- reason/condition: reason: useless for us
- 2.85 REJECT (short): there is no short opportunity that makes sense from this moment -- reason/condition: they tried they failed they retraced they tried again
- 2.90 REJECT (long): it's really frustrating for me when you are floating 10, 20, 30,000 -- reason/condition: reason: giving back large floating profit is frustrating
- 2.97 REJECT (short): does this mean that we are going short for all the session no -- reason/condition: reason: it only means he found a wall
- 2.108 REJECT (-): i will not take other trades okay because we already took amazing setup for today -- reason/condition: reason: the setup for today was already taken
- 2.110 REJECT (-): it's not a smart setup that's the reason i will not consider it -- reason/condition: reason: really close to the wall

- 2.7 condition: if broken by the buyers, expect volatility; role: sellers' wall
- 2.12 condition: if the sellers do not break it with this speed and pressure -> he calls rejection
- 2.15 condition: if they break it; 'self-protection level' [?] = sell protection level
- 2.16 condition: if the level breaks
- 2.19 condition: if this one breaks
- 2.22 condition: if you break this you have this level that it's really interesting
- 2.26 condition: a clean control point needs acceptance: big trades at the top, or a clean breakout and test
- 2.27 condition: after acceptance (big trades at the top or clean breakout and test)
- 2.30 condition: direction is decided only when aggression, aggression, aggression is seen
- 2.40 condition: when you go out of the level; sellers absorbed and buyers following up (next row)
- 2.42 condition: if it breaks on the downside, 'invalidator' [?] = invalidates; he goes to the stop loss
- 2.43 condition: stop to zero 'not even one candle' after entry; the level was marked before the trade
- 2.49 condition: when the market tells you that you can go
- 2.62 condition: if you decided not to take profit
- 2.63 condition: if you get taken out and price goes back to this level
- 2.64 condition: after three take profits
- 2.66 condition: he accepts the stop being hit; 'i'm not happy if the market touch this level from here and collapse down'
- 2.86 condition: after the test
- 2.89 condition: if the approach is to take the full movement of the session
- 2.99 condition: if this wall gets broken
- 2.100 condition: you need the breakout, otherwise this is a standpoint of control of the sellers
- 2.104 condition: 'even if your win rate will be lower'
- 2.111 condition: if you break this wall you have the momentum; lower probability
- 2.113 condition: area explanation continues after L633


(part 3: Is1HvdfQm5c_part3.md)

- 3.33: REJECT: no short against the bias while "the auction is still on"; condition: "if we break this level i change my mind"
- 3.36: REJECT: does not execute while the candle forms, "you just want to see how the candle close"; condition: candle close decides
- 3.35: CONDITION: candle completely rejected -> move up; candle accepted -> "squeeze on the downside"
- 3.45: REJECT: a fill that "comes back it break me" is "not so interesting"
- 3.46: RULE: unfilled order is removed ("if I don't get field I remove the order")
- 3.41: CONDITION: the order needs a test of the level to fill ("let's see if it test")
- 3.40: CONDITION: wait for the candle close; a break that does not complete is a fakeout
- 3.54: CONDITION (advice to viewers): if filled in the spike, "go risk-free"; reason: "don't let this volatility take you out with a spike"
- 3.57: CONDITION (advice to a viewer's short): "if you are still short" go risk free; "good to take risk out of the market when the situation is so heated"
- 3.56: CONDITION: liquidity wall; if the high breaks "we really skyrocket", if the low breaks "we go down heavy"
- 3.59: CONDITION: break of the level releases the stacked sellers and absorbed buyers
- 3.84: CONDITION: the deep effort area is "invalidated when you break it"
- 3.86: CONDITION: area stays valid while it holds, then "we can go to the final target up"
- 3.101: REJECT: second execution method "I don't advise you do this trade there"; "I don't like it at all"
- 3.103: REJECT: no more trades, "the session is done"; "anything you take from now it's to study"
- 3.19: CONDITION: after the gap the next candle must rebalance and close green (move up) or it eats the gap (absorbed)
- 3.9: CONDITION: squeeze if the buyers take control over the absorbed-buyers level
- 3.11: CONDITION: "it will explode up" only if the top breaks
- 3.10: CONDITION: setup incomplete until aggressive sellers print; then up
- 3.90: CONDITION: stop to zero "when you have another confirmation from the buyers"
- 3.82: CONDITION: buyers must close above to keep the long reading
- 3.3: CONDITION: control stays with the sellers until the demand breaks the structure


## 3.5 Verbatim anchors (machine-checked)


(part 1: Is1HvdfQm5c_part1.md)

> "the model is saying that I only enter in profile framing In in trend condition and I execute"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L53-L53, [6:44]-[6:54])

> "i loaded again position here okay risking part of the profit of this one"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L67-L67, [8:54]-[9:04])

> "you stay out of the market there"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L88-L88, [12:26]-[12:36])

> "why are you trying to take five seven ten twenty five trades per day you will not get rich today you will only make damage"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L102-L102, [14:43]-[14:55])

> "you have an aggression aggressive sellers lock in the movement"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L138-L138, [20:00]-[20:10])

> "we can take one short"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L139-L139, [20:10]-[20:22])

> "the trade that in 2025 gave me the most amount of money is the test of this level with"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L139-L139, [20:10]-[20:22])

> "the confirmation of absorbed buyers"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L140-L140, [20:22]-[20:32])

> "so these buyers no follow through the aggression rewarded"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L141-L141, [20:32]-[20:43])

> "this is your opportunity"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L144-L144, [21:04]-[21:14])

> "you can cover yourself above the area"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L145-L145, [21:14]-[21:24])

> "shoot for a 1 to 4.5"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L145-L145, [21:14]-[21:24])

> "this is exactly the same model that I used to take the trade of the session of $50,000 on YouTube absorption"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L146-L146, [21:24]-[21:36])

> "I entered the short also amazing setup"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L153-L153, [22:34]-[22:44])

> "the aggression of the last sellers is your first point of interest"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L157-L157, [23:15]-[23:25])

> "if you have a level where to cover yourself that is this one"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L169-L169, [24:50]-[25:00])

> "can already when you see rejection you can execute"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L170-L170, [25:00]-[25:12])

> "this one was the first level of the day that we marked"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L181-L181, [26:43]-[26:53])

> "unfortunately it's counter trend"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L181-L181, [26:43]-[26:53])

> "not say that it's so smart to take a long yeah we can see we can see the downside pressure"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L186-L186, [27:21]-[27:31])

> "these buyers got the reward that the candle close long we managed to break this level"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L211-L211, [31:30]-[31:41])

> "the sellers is absorbed the buyers got confirmed even"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L214-L214, [31:55]-[32:05])

> "if you enter here not here still an amazing run up"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L215-L215, [32:05]-[32:16])

> "covering yourself below the area this is the squeeze setup"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L221-L221, [33:03]-[33:14])

> "to 5 1 to 4.9 at the third touch"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L224-L224, [33:32]-[33:39])

> "the more you are greedy with your target the less the probability that it get reached"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L226-L226, [33:49]-[33:59])

> "it's a trade that it's a little bit difficult to take"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L233-L233, [34:38]-[34:48])

> "when the market tell you something like this and you continue to short it's your responsibility"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L242-L242, [36:07]-[36:17])

> "you only want to be right"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L243-L243, [36:17]-[36:27])

> "you can decide to execute with a stop loss before the area with the target here"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L244-L244, [36:27]-[36:37])

> "or you can go for the home run"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L244-L244, [36:27]-[36:37])

> "you will have around 30 to 35 percent win rate"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L245-L245, [36:37]-[36:48])

> "we consider a stop area 640"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L247-L247, [36:53]-[37:04])

> "you take a target above the eye"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L248-L248, [37:04]-[37:14])

> "the next level that i can see is the 25 646.39"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L249-L249, [37:14]-[37:24])

> "this is inefficient volume because it created a micro gap"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L266-L266, [40:17]-[40:29])

> "long okay let's not consider the long"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L276-L276, [41:51]-[42:01])

> "but these are counter trend trade and I don't like to take them"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L279-L279, [42:22]-[42:38])

> "remember that this level is sustained by 39 250 89 around around"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L280-L280, [42:38]-[42:48])

> "squeeze guys is when you see a sudden acceleration"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, L284-L284, [43:08]-[43:21])

> "now i don't see anything that we can execute"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L287-L287, [43:36]-[43:47])

> "they try to break three four five times and they always hold this level that"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L289-L289, [43:57]-[44:07])

> "like to take trades when there is no support from the aggressive order market participants"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L291-L291, [44:18]-[44:28])

> "it's a smart TP"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L300-L300, [45:37]-[45:47])

> "I don't understand why you are trying long in the no-man land"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L300-L300, [45:37]-[45:47])

> "entering at this cluster one"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L301-L301, [45:47]-[45:59])

> "entering with really high stop loss"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L302-L302, [45:59]-[46:21])

> "so one to two point five still paying out"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L302-L302, [45:59]-[46:21])

> "they are reloading to protect this level"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L312-L312, [47:45]-[47:55])

> "you need to be not exactly at one level value area value area low"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L316-L316, [48:15]-[48:25])

> "it's the limit price wall on the top or on the bottom it's giving keeping you in consolidation"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L317-L317, [48:25]-[48:36])

> "this is the worst case that you can have for a momentum trade"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L318-L318, [48:36]-[48:44])

> "i will consider a cell continuation if we break out this level yes"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L319-L319, [48:44]-[48:54])

> "if we manage to recover this huge candle okay"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L321-L321, [49:04]-[49:14])

> "a little bit of participation of the buyer some big trades"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L322-L322, [49:14]-[49:25])

> "then we go to the target that the other guy say that is this one"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L322-L322, [49:14]-[49:25])


(part 2: Is1HvdfQm5c_part2.md)


Row 2.4 (LESSON, FABIO)

> "If the market gives you the breakout. So if this candle boom aggressive. Here you can take a short on the momentum phase."
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L331-L332, [50:40]-[50:45])

Row 2.5 (REJECT, FABIO)

> "I think we tested four times and each time they rejected. We don't have the clue that the aggressive sellers are strong enough."
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L333-L334, [50:52]-[50:59])

Row 2.6 (CONTEXT, FABIO)

> "we have the clue that buyers are protecting the level and they are doing this amazingly because also the last test that they did here the sellers got completely absorbed"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L336-L337, [51:07]-[51:17])

Row 2.7 (LOCATION, FABIO)

> "this is the intermediate wall that the sellers are putting if this one gets broken expect volatility twenty five thousand six hundred and thirty two"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L338-L339, [51:23]-[51:33])

Row 2.8 (REJECT, FABIO)

> "if you are waiting for a confirmation to get short wait for this level to collapse wait for it to stop printing this week and to have a clean break"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L339-L340, [51:33]-[51:44])

Row 2.9 (CONTEXT, FABIO)

> "another time they filled into the inefficiency see also of the 139 executed contract"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L342-L343, [52:01]-[52:11])

Row 2.15 (LOCATION, FABIO)

> "if they break the level will become a self-protection level exactly Jason you got the point if they break it this level will be used to reload on the cell side"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L362-L363, [55:13]-[55:23])

Row 2.18 (CONTEXT, FABIO)

> "And they are they are putting billions here. They are loading billions."
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L371-L372, [56:27]-[56:33])

Row 2.23 (REJECT, FABIO)

> "it's not necessary to mark intermediate level that are useless for us"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L390-L390, [58:55]-[58:55])

Row 2.27 (ADD, FABIO)

> "and we are stacking our third position for the day"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L404-L404, [1:01:21]-[1:01:21])

Row 2.28 (CONTEXT, UNKNOWN)

> "i got this one running with small risk from the fair value gap protected by 400 buyers"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L404-L405, [1:01:21]-[1:01:31])

Row 2.33 (STOP_MOVE, FABIO)

> "it makes sense to put the risk to zero on the upside to risk zero so we are not even using the profit of the previous one"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L416-L417, [1:03:06]-[1:03:17])

Row 2.37 (PROOF, FABIO)

> "now the markets is coming to test okay it's closing an inefficiency touch the level and close the level with this absorption"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L423-L424, [1:04:15]-[1:04:25])

Row 2.38 (ENTRY, FABIO)

> "this one here would have been your feeling point this one would have been your feeling point"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L425-L426, [1:04:36]-[1:04:44])

Row 2.40 (STOP_MOVE, FABIO)

> "Okay covering your risk when you go out of the level."
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L428-L428, [1:05:01]-[1:05:01])

Row 2.41 (STOP_MOVE, FABIO)

> "You can also Go risk-free if you enter precisely really fast"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L430-L430, [1:05:15]-[1:05:15])

Row 2.42 (STOP_SET, FABIO)

> "if it breaks on the downside even now if it break this level the analysis invalidator So you go to stop loss?"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L431-L432, [1:05:25]-[1:05:36])

Row 2.43 (STOP_MOVE, FABIO)

> "we have time To go stop losing at zero so fast not even one candle"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L435-L436, [1:06:00]-[1:06:11])

Row 2.45 (ENTRY, FABIO)

> "hey you see here when to enter you see this absorption in one candle you have two following absorption then you have an aggression here"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L437-L438, [1:06:20]-[1:06:30])

Row 2.48 (PARTIAL, FABIO)

> "I take another one to one point five here I close like the other session"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L446-L446, [1:07:34]-[1:07:34])

Row 2.49 (STOP_MOVE, FABIO)

> "the confidence of going to break even when the market tell you that you can go"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L447-L448, [1:07:44]-[1:07:54])

Row 2.52 (PARTIAL, FABIO)

> "I take also a little bit of money out of the market maybe it's not much it's $200 but better"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L454-L454, [1:08:54]-[1:08:54])

Row 2.53 (PARTIAL, FABIO)

> "You will take out your take profit your partial your first take profit."
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L459-L459, [1:09:48]-[1:09:48])

Row 2.57 (TARGET_SET, FABIO)

> "no I'm expecting a final target here"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L471-L471, [1:11:25]-[1:11:25])

Row 2.58 (LOCATION, FABIO)

> "level is the starting of the sell move participated by the aggressive sellers but it's the huge absorption look here this cluster it's incredible this is the initiation of the move"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L480-L481, [1:13:09]-[1:13:19])

Row 2.62 (STOP_MOVE, FABIO)

> "manage the position with a stop loss in profit here okay so you are already taking out a one-to-one you have additional R"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L500-L500, [1:16:52]-[1:16:52])

Row 2.66 (STOP_MOVE, FABIO)

> "let's say that i have a stop in profit i put below the big trade on this downside because i'm happy with a one to three instead of a one to three point six"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L522-L523, [1:20:44]-[1:20:54])

Row 2.67 (TARGET_SET, FABIO)

> "i'm happy with a one to three instead of a one to three point six"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L522-L523, [1:20:44]-[1:20:54])

Row 2.71 (EXIT, FABIO)

> "here you are out you are out with your one to two point seven one two two point six"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L530-L530, [1:22:11]-[1:22:11])

Row 2.72 (TARGET_SET, FABIO)

> "the market went down absorbed and probably you go to the full target one two three"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L531-L532, [1:22:21]-[1:22:28])

Row 2.73 (ENTRY, FABIO)

> "here we are inside from the beginning of the move with this precision"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L533-L534, [1:22:38]-[1:22:49])

Row 2.76 (CONTEXT, FABIO)

> "we started with the rejection of this so it means that they tap into the high of the previous session they rejected"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L546-L547, [1:24:31]-[1:24:41])

Row 2.77 (LOCATION, FABIO)

> "what I was trying to take and to capitalize is the virgin POC test"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L547-L548, [1:24:41]-[1:24:51])

Row 2.79 (ENTRY, FABIO)

> "this buy was counter thrown because at this moment sellers were still in control okay here and here"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L552-L552, [1:25:35]-[1:25:35])

Row 2.84 (LESSON, FABIO)

> "if here we had this absorption okay of the buyers and then we have aggressive sellers aggressive sellers aggressive sellers okay and we break these movements"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L561-L562, [1:27:05]-[1:27:15])

Row 2.85 (REJECT, FABIO)

> "there is no short opportunity that makes sense from this moment"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L564-L565, [1:27:35]-[1:27:45])

Row 2.86 (ADD, FABIO)

> "also after the test then we took the reload zero down and shoot up"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L565-L566, [1:27:45]-[1:27:55])

Row 2.88 (TARGET_SET, FABIO)

> "this is the final target not of the day is the final target for the position"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L567-L568, [1:28:06]-[1:28:20])

Row 2.90 (REJECT, FABIO)

> "you know why i don't trade like like this because it's really frustrating for me when you are floating 10, 20, 30,000."
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L571-L572, [1:28:50]-[1:29:00])

Row 2.93 (CONTEXT, FABIO)

> "volume absorption at the bottom buyers aggressive at the this was our trade they came back to test huge absorption at the bottom buyers in the body another explosion"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L580-L581, [1:30:14]-[1:30:24])

Row 2.94 (PARTIAL, FABIO)

> "this one was absorption at the top sellers and we could expect that from here we will go down that's the reason we take partial"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L581-L582, [1:30:24]-[1:30:35])

Row 2.97 (REJECT, FABIO)

> "does this mean that we are going short for all the session no"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L584-L584, [1:30:55]-[1:30:55])

Row 2.98 (LOCATION, FABIO)

> "this mean that i found a wall here there is a wall and this wall got identified to us before"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L584-L585, [1:30:55]-[1:31:05])

Row 2.100 (LESSON, FABIO)

> "breakout test probably on the absorbed sellers like these and then you can consider a follow-up but you need to have this breakout"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, L591-L592, [1:31:58]-[1:32:08])

Row 2.102 (LESSON, FABIO)

> "I have here an absorption that is so strong of the sellers for two times trade okay this is a strong buy area"
**Source GPS: Is1HvdfQm5c | END** (ASR, L601-L602, [1:33:22]-[1:33:32])

Row 2.104 (LESSON, FABIO)

> "you trade the fade with a stop loss above and you try to take the beginning of the move for a huge risk to reward"
**Source GPS: Is1HvdfQm5c | END** (ASR, L610-L611, [1:34:38]-[1:34:48])

Row 2.105 (LESSON, FABIO)

> "the confirmed fade setup is that you wait for the aggressive sellers to take control of the movement that you qualified"
**Source GPS: Is1HvdfQm5c | END** (ASR, L612-L613, [1:34:59]-[1:35:10])

Row 2.108 (REJECT, FABIO)

> "i will not take other trades okay because we already took amazing setup for today"
**Source GPS: Is1HvdfQm5c | END** (ASR, L619-L620, [1:36:05]-[1:36:15])

Row 2.109 (LESSON, FABIO)

> "sellers at the bottom absorbed sellers at the bottom absorbed buyers at the top absorbed buyers at the top absorbed"
**Source GPS: Is1HvdfQm5c | END** (ASR, L620-L621, [1:36:15]-[1:36:26])

Row 2.109 (LESSON, FABIO)

> "perfect breakout of compression reaction phase test with aggressive sellers skyrocket to the moon"
**Source GPS: Is1HvdfQm5c | END** (ASR, L622-L622, [1:36:36]-[1:36:36])

Row 2.110 (REJECT, FABIO)

> "it's not a smart setup that's the reason i will not consider it you are so close to the wall"
**Source GPS: Is1HvdfQm5c | END** (ASR, L624-L624, [1:36:57]-[1:36:57])

Row 2.112 (LESSON, FABIO)

> "the fate setup it's having as I told you 35 to 40% but with a lot of risk reward"
**Source GPS: Is1HvdfQm5c | END** (ASR, L627-L628, [1:37:28]-[1:37:39])



(part 3: Is1HvdfQm5c_part3.md)

Row 3.1 (LESSON):
> "control area is the study of the area that is controlling price."
**Source GPS: Is1HvdfQm5c | END** (ASR, L636-L636, [1:38:51]-[1:38:51])

Row 3.2 (LESSON):
> "give you amazing setup when you pair with order flow maybe it's an absorption maybe it's an exhaustion"
**Source GPS: Is1HvdfQm5c | END** (ASR, L642-L642, [1:39:52]-[1:39:52])

Row 3.4 (LESSON):
> "care to take out part of my profit on this area because I can't reverse okay but with a confirmation that the sellers are in control"
**Source GPS: Is1HvdfQm5c | END** (ASR, L651-L651, [1:41:05]-[1:41:05])

Row 3.5 (LESSON):
> "when I break this becomes the demand so I can continue to search long"
**Source GPS: Is1HvdfQm5c | END** (ASR, L653-L653, [1:41:22]-[1:41:22])

Row 3.6 (PROOF):
> "area that I marked for you again for the fourth time today rejected amazingly buyers I explained to you what when we break this we test they tested yes"
**Source GPS: Is1HvdfQm5c | END** (ASR, L658-L658, [1:42:19]-[1:42:19])

Row 3.7 (LESSON):
> "you are long of bias okay start to notice absorbed sellers buyers at the top break out and testing with"
**Source GPS: Is1HvdfQm5c | END** (ASR, L661-L661, [1:42:42]-[1:42:42])

Row 3.8 (LOCATION):
> "here we have a lot of absorbed buyers this means that this level for sellers is interesting"
**Source GPS: Is1HvdfQm5c | END** (ASR, L666-L666, [1:43:24]-[1:43:24])

Row 3.9 (CONTEXT):
> "no way around it we squeeze it"
**Source GPS: Is1HvdfQm5c | END** (ASR, L669-L669, [1:43:49]-[1:43:49])

Row 3.10 (CONTEXT):
> "absorption at the bottom buyers at the top you break and you test zero draw down okay"
**Source GPS: Is1HvdfQm5c | END** (ASR, L671-L671, [1:44:18]-[1:44:18])

Row 3.10 (CONTEXT):
> "I think they can come back I think they can come back print aggressive sellers and then go up let's see"
**Source GPS: Is1HvdfQm5c | END** (ASR, L673-L673, [1:44:39]-[1:44:39])

Row 3.11 (LOCATION):
> "it will explode up it will explode if they break this they need to break this"
**Source GPS: Is1HvdfQm5c | END** (ASR, L674-L674, [1:44:54]-[1:44:54])

Row 3.12 (PROOF):
> "with the cvd they are already above the top it means that they are continuing to load"
**Source GPS: Is1HvdfQm5c | END** (ASR, L678-L678, [1:45:24]-[1:45:24])

Row 3.13 (PROOF):
> "it's incredible that now they have a cvd cell candle but the candle is printing green so they are absorbing with"
**Source GPS: Is1HvdfQm5c | END** (ASR, L679-L679, [1:45:35]-[1:45:35])

Row 3.14 (PROOF):
> "if this happen it means that the buyers are putting back again passive order wall and they are pushing the"
**Source GPS: Is1HvdfQm5c | END** (ASR, L683-L683, [1:46:16]-[1:46:16])

Row 3.15 (CONTEXT):
> "it and for the fourth time they got rejected on the level"
**Source GPS: Is1HvdfQm5c | END** (ASR, L687-L687, [1:47:04]-[1:47:04])

Row 3.16 (LESSON):
> "you cannot expect always action you need to build some patience it's normal that you have some consolidation to give the market"
**Source GPS: Is1HvdfQm5c | END** (ASR, L691-L691, [1:47:49]-[1:47:49])

Row 3.17 (CONTEXT):
> "no no i'm not loading guys i'm solving cash sheet i was trying to hide that i was loading but it's visible now"
**Source GPS: Is1HvdfQm5c | END** (ASR, L694-L694, [1:48:58]-[1:48:58])

Row 3.19 (LESSON):
> "what I always tell you about the gap that is really important the candle next because if the candle next rebalance the gap now they rebalance and close green okay"
**Source GPS: Is1HvdfQm5c | END** (ASR, L702-L702, [1:50:19]-[1:50:19])

Row 3.19 (LESSON):
> "so they rebalance and reject and you have a good movement you have a good movement up violent one if the candle eat the gap on the downside so"
**Source GPS: Is1HvdfQm5c | END** (ASR, L703-L703, [1:50:29]-[1:50:29])

Row 3.19 (LESSON):
> "it eat the gaps till the beginning of the move then it got completely absorbed all with Nasdaq cap okay how"
**Source GPS: Is1HvdfQm5c | END** (ASR, L704-L704, [1:50:39]-[1:50:39])

Row 3.20 (PROOF):
> "candle close purple and what happened market push down look at the delta bomb now all this aggressive sell"
**Source GPS: Is1HvdfQm5c | END** (ASR, L706-L706, [1:50:59]-[1:50:59])

Row 3.21 (CONTEXT):
> "I think we continue long guys I think we continue long"
**Source GPS: Is1HvdfQm5c | END** (ASR, L708-L708, [1:51:19]-[1:51:19])

Row 3.22 (LOCATION):
> "this as a decision level from the downside and this level for a potential up squeeze we have"
**Source GPS: Is1HvdfQm5c | END** (ASR, L711-L711, [1:51:52]-[1:51:52])

Row 3.23 (LOCATION):
> "it went back to the level wait wait it's too fast at all it went back to the level this is the level that we marked imagine guys imagine now he"
**Source GPS: Is1HvdfQm5c | END** (ASR, L715-L715, [1:52:23]-[1:52:23])

Row 3.24 (LESSON):
> "print this aggressive absorption and it goes long like he did here exactly like he did here just for the sake of making"
**Source GPS: Is1HvdfQm5c | END** (ASR, L716-L716, [1:52:34]-[1:52:34])

Row 3.25 (CONTEXT):
> "we have news in five minutes let's see"
**Source GPS: Is1HvdfQm5c | END** (ASR, L717-L717, [1:52:44]-[1:52:44])

Row 3.26 (LESSON):
> "with 30 you have more possibility with 60 you have less possibility it"
**Source GPS: Is1HvdfQm5c | END** (ASR, L718-L718, [1:52:56]-[1:52:56])

Row 3.27 (LESSON):
> "you consider to lower the value of BT no there is volume yet still 77 here speed of tape was so big I"
**Source GPS: Is1HvdfQm5c | END** (ASR, L720-L720, [1:53:26]-[1:53:26])

Row 3.28 (CONTEXT):
> "why they are preparing guys because there is volatility in four minutes what"
**Source GPS: Is1HvdfQm5c | END** (ASR, L721-L721, [1:53:36]-[1:53:36])

Row 3.29 (LOCATION):
> "they tap into the buy area that we saw and now what you notice when we are getting close to a news you you notice how many"
**Source GPS: Is1HvdfQm5c | END** (ASR, L724-L724, [1:54:11]-[1:54:11])

Row 3.30 (PROOF):
> "now we have three big trades in two candles it means that they are fighting here"
**Source GPS: Is1HvdfQm5c | END** (ASR, L726-L726, [1:54:25]-[1:54:25])

Row 3.31 (CONTEXT):
> "or is still valid this aggressive seller here broken or still valid is still in control still valid okay"
**Source GPS: Is1HvdfQm5c | END** (ASR, L730-L730, [1:55:18]-[1:55:18])

Row 3.32 (CONTEXT):
> "what does it mean that the battle to decide is in these two areas okay the extreme"
**Source GPS: Is1HvdfQm5c | END** (ASR, L733-L733, [1:55:44]-[1:55:44])

Row 3.33 (REJECT):
> "but I will not consider a short here for only one reason the"
**Source GPS: Is1HvdfQm5c | END** (ASR, L736-L736, [1:56:34]-[1:56:34])

Row 3.33 (REJECT):
> "auction the auction is still on okay i prefer not to go opposite to the direction of the bias"
**Source GPS: Is1HvdfQm5c | END** (ASR, L737-L737, [1:56:44]-[1:56:44])

Row 3.33 (REJECT):
> "of course if we break this level i change my mind but i want to see the market before breaking okay"
**Source GPS: Is1HvdfQm5c | END** (ASR, L738-L738, [1:56:54]-[1:56:54])

Row 3.34 (PROOF):
> "on the buy side and confirmation on the downside now we see how this candle close okay if this candle gets"
**Source GPS: Is1HvdfQm5c | END** (ASR, L743-L743, [1:57:38]-[1:57:38])

Row 3.35 (CONTEXT):
> "completely rejected then in this case we can have a move up but this candle needs to be completely rejected and if"
**Source GPS: Is1HvdfQm5c | END** (ASR, L744-L744, [1:57:48]-[1:57:48])

Row 3.36 (REJECT):
> "you want to see how the candle close you just want to see how the candle close you don't want to execute you"
**Source GPS: Is1HvdfQm5c | END** (ASR, L747-L747, [1:58:11]-[1:58:11])

Row 3.37 (PROOF):
> "almost closing if it goes with the speed of tape eating up these and these what do you see long or short"
**Source GPS: Is1HvdfQm5c | END** (ASR, L749-L749, [1:58:32]-[1:58:32])

Row 3.38 (ENTRY):
> "you have the last trade of the day let's see if it test let's see if it test i will"
**Source GPS: Is1HvdfQm5c | END** (ASR, L752-L752, [1:58:53]-[1:58:53])

Row 3.38 (ENTRY):
> "go for the last one another one two three the last one two three"
**Source GPS: Is1HvdfQm5c | END** (ASR, L753-L753, [1:59:04]-[1:59:04])

Row 3.39 (CONTEXT):
> "we did uh three trades one was i don't remember guys how many are we made"
**Source GPS: Is1HvdfQm5c | END** (ASR, L754-L754, [1:59:11]-[1:59:11])

Row 3.40 (PROOF):
> "it broke but was a fakeout it didn't it didn't complete the breakout that's the reason i always tell you wait for the close because it heated with"
**Source GPS: Is1HvdfQm5c | END** (ASR, L756-L756, [1:59:26]-[1:59:26])

Row 3.41 (HOLD):
> "speed of tape and aggressive six are amazing let's see if it test i"
**Source GPS: Is1HvdfQm5c | END** (ASR, L757-L757, [1:59:36]-[1:59:36])

Row 3.41 (HOLD):
> "now i will show you let's see if we get filled"
**Source GPS: Is1HvdfQm5c | END** (ASR, L759-L759, [1:59:53]-[1:59:53])

Row 3.42 (LOCATION):
> "was the line point of the last point of aggression of the sellers i'm really curious to see if they hold the the ground or not"
**Source GPS: Is1HvdfQm5c | END** (ASR, L761-L761, [2:00:15]-[2:00:15])

Row 3.43 (PROOF):
> "they they are they are fighting like hell on this horizontal level the speed of tape it's it's incredible if"
**Source GPS: Is1HvdfQm5c | END** (ASR, L764-L764, [2:01:15]-[2:01:15])

Row 3.44 (PROOF):
> "they break this level guys is probably that they will never test here we didn't got filled for like one tick they"
**Source GPS: Is1HvdfQm5c | END** (ASR, L765-L765, [2:01:28]-[2:01:28])

Row 3.44 (PROOF):
> "are breaking it's not valid anymore I try to make another last sniper, but we didn't got field."
**Source GPS: Is1HvdfQm5c | END** (ASR, L766-L766, [2:01:39]-[2:01:39])

Row 3.45 (REJECT):
> "because if it comes back it break me So it's not so interesting."
**Source GPS: Is1HvdfQm5c | END** (ASR, L770-L770, [2:02:13]-[2:02:13])

Row 3.46 (EXIT):
> "So if I don't get field I remove the order"
**Source GPS: Is1HvdfQm5c | END** (ASR, L771-L771, [2:02:20]-[2:02:20])

Row 3.46 (EXIT):
> "we removed anything anyway but it's good that we remove because you see that this"
**Source GPS: Is1HvdfQm5c | END** (ASR, L773-L773, [2:02:50]-[2:02:50])

Row 3.47 (CONTEXT):
> "this is deep effort is showing you who is in control you see they show you it's controlled the auction buyers control of the option buyers who is controlling the auction now"
**Source GPS: Is1HvdfQm5c | END** (ASR, L777-L777, [2:03:19]-[2:03:19])

Row 3.48 (CONTEXT):
> "yeah it's like a wall it's like a wall it's like telling you that the buyers are in control of this movement so the probability instead of breaking this"
**Source GPS: Is1HvdfQm5c | END** (ASR, L778-L778, [2:03:32]-[2:03:32])

Row 3.48 (CONTEXT):
> "expansion sorry breaking this level and potentially reaching also the final target where was the I want to see the most important"
**Source GPS: Is1HvdfQm5c | END** (ASR, L780-L780, [2:03:52]-[2:03:52])

Row 3.49 (CONTEXT):
> "cell level you see this one is not so strong didn't even got marked this absorption guys"
**Source GPS: Is1HvdfQm5c | END** (ASR, L781-L781, [2:04:02]-[2:04:02])

Row 3.50 (CONTEXT):
> "now that you know that this level is controlled by buyers and you have a control of the buyers you can put this one and see okay"
**Source GPS: Is1HvdfQm5c | END** (ASR, L785-L785, [2:04:48]-[2:04:48])

Row 3.51 (CONTEXT):
> "it seems really aggressive to break it guys if this will that field does on the downtick it will already be one to one point five look"
**Source GPS: Is1HvdfQm5c | END** (ASR, L789-L789, [2:05:25]-[2:05:25])

Row 3.52 (PROOF):
> "now calm 319 absorbed orders and one 104 on the bottom"
**Source GPS: Is1HvdfQm5c | END** (ASR, L791-L791, [2:05:41]-[2:05:41])

Row 3.53 (CONTEXT):
> "speed of tape down and everything got absorbed now they are coming to rebalance on the three three 1.9 of course I removed but if you"
**Source GPS: Is1HvdfQm5c | END** (ASR, L795-L795, [2:06:08]-[2:06:08])

Row 3.54 (LESSON):
> "go risk-free yeah go risk-free don't give back not even ten dollars to the market"
**Source GPS: Is1HvdfQm5c | END** (ASR, L796-L796, [2:06:18]-[2:06:18])

Row 3.55 (LESSON):
> "is not the delta it's the speed of tape"
**Source GPS: Is1HvdfQm5c | END** (ASR, L798-L798, [2:06:37]-[2:06:37])

Row 3.56 (CONTEXT):
> "means that there is a liquidity wall here and if this high gets broken we really skyrocket if we break this down"
**Source GPS: Is1HvdfQm5c | END** (ASR, L801-L801, [2:07:10]-[2:07:10])

Row 3.57 (LESSON):
> "on the other side we go down heavy so if you are still short anyway you could go risk free because you have"
**Source GPS: Is1HvdfQm5c | END** (ASR, L802-L802, [2:07:20]-[2:07:20])

Row 3.57 (LESSON):
> "take risk out of the market when the situation is so heated because you can get a sleep edge"
**Source GPS: Is1HvdfQm5c | END** (ASR, L804-L804, [2:07:41]-[2:07:41])

Row 3.58 (LOCATION):
> "makes you think long makes you think an aggression okay now if they manage to break this no if"
**Source GPS: Is1HvdfQm5c | END** (ASR, L809-L809, [2:08:25]-[2:08:25])

Row 3.59 (CONTEXT):
> "they manage to break this you agree with me that all the sellers that are stacked and all these absorbed buyers needs to be released and these if all this huge"
**Source GPS: Is1HvdfQm5c | END** (ASR, L810-L810, [2:08:36]-[2:08:36])

Row 3.60 (PROOF):
> "cluster the 104 and the 300 that are standing still really"
**Source GPS: Is1HvdfQm5c | END** (ASR, L816-L816, [2:09:28]-[2:09:28])

Row 3.61 (CONTEXT):
> "see either they reject on the 319 or the one on four and they always dance here"
**Source GPS: Is1HvdfQm5c | END** (ASR, L820-L820, [2:10:05]-[2:10:05])

Row 3.62 (PROOF):
> "the buyers on the other side stop participating 10 minutes ago in the in the play I"
**Source GPS: Is1HvdfQm5c | END** (ASR, L821-L821, [2:10:13]-[2:10:13])

Row 3.63 (LESSON):
> "you need to pay delta with the result because delta is the input but then you need to see what the candle does"
**Source GPS: Is1HvdfQm5c | END** (ASR, L823-L823, [2:10:30]-[2:10:30])

Row 3.65 (CONTEXT):
> "to go up and this is the best behavior before a squeeze this is the best behavior before shooting up"
**Source GPS: Is1HvdfQm5c | END** (ASR, L829-L829, [2:11:50]-[2:11:50])

Row 3.66 (PROOF):
> "buyers are trying to load heavy"
**Source GPS: Is1HvdfQm5c | END** (ASR, L831-L831, [2:12:11]-[2:12:11])

Row 3.67 (LESSON):
> "now we are on the top of the range the deep effort it's a proprietary study and it's based on the thickness of the book so"
**Source GPS: Is1HvdfQm5c | END** (ASR, L832-L832, [2:12:20]-[2:12:20])

Row 3.67 (LESSON):
> "is watching the number of effort that is necessary to move the price and when it's really easy for one side to move the price we print the area so smart guys so"
**Source GPS: Is1HvdfQm5c | END** (ASR, L833-L833, [2:12:30]-[2:12:30])

Row 3.68 (LOCATION):
> "on the other side this red area that I marked for you is where the part of risk resistance is on the downside so from this area the sellers are in"
**Source GPS: Is1HvdfQm5c | END** (ASR, L837-L837, [2:13:13]-[2:13:13])

Row 3.69 (LESSON):
> "control now if you want to have a no-brainer ping-pong between these two areas pay you a lot of money pay"
**Source GPS: Is1HvdfQm5c | END** (ASR, L838-L838, [2:13:23]-[2:13:23])

Row 3.70 (LESSON):
> "yeah I think depending completely on one indicator it's not what you want to do because"
**Source GPS: Is1HvdfQm5c | END** (ASR, L840-L840, [2:13:45]-[2:13:45])

Row 3.71 (LOCATION):
> "we are going back to the bi-control area just touched just touched let's see what they do now that we are"
**Source GPS: Is1HvdfQm5c | END** (ASR, L845-L845, [2:14:38]-[2:14:38])

Row 3.72 (PROOF):
> "and got completely absorbed this is a strong wall this is a really a strong wall"
**Source GPS: Is1HvdfQm5c | END** (ASR, L849-L849, [2:15:14]-[2:15:14])

Row 3.73 (LESSON):
> "or here or on this test where did you got stopped out you trail your stop I want to help you"
**Source GPS: Is1HvdfQm5c | END** (ASR, L855-L855, [2:16:04]-[2:16:04])

Row 3.76 (LESSON):
> "good question i show you immediately let's say that you are here okay and you want to risk the same amount always on the"
**Source GPS: Is1HvdfQm5c | END** (ASR, L861-L861, [2:17:12]-[2:17:12])

Row 3.76 (LESSON):
> "the contract I have to put seven mini contract here if I I want to do this I have to put 15 if I want to risk 2500 if"
**Source GPS: Is1HvdfQm5c | END** (ASR, L866-L866, [2:17:53]-[2:17:53])

Row 3.77 (CONTEXT):
> "amazing Michael today the market only went up and we managed to take all the long on the way up how"
**Source GPS: Is1HvdfQm5c | END** (ASR, L869-L869, [2:18:25]-[2:18:25])

Row 3.78 (LESSON):
> "did you got taken out of this long you try to short here because the only explanation that I can have that you lost money is that you try to short to fade this movement to go"
**Source GPS: Is1HvdfQm5c | END** (ASR, L870-L870, [2:18:35]-[2:18:35])

Row 3.79 (CONTEXT):
> "back down yes sellers are in control now we are still inside the area but sellers are controlling you see from here let me clean this you"
**Source GPS: Is1HvdfQm5c | END** (ASR, L871-L871, [2:18:46]-[2:18:46])

Row 3.80 (LESSON):
> "is the best exercise to really understand pressure management when controlling a longer short position sometimes they struggle with it it's just exercise Mario there"
**Source GPS: Is1HvdfQm5c | END** (ASR, L874-L874, [2:19:18]-[2:19:18])

Row 3.81 (PROOF):
> "it's it's a problem for the buyers they got completely absorbed"
**Source GPS: Is1HvdfQm5c | END** (ASR, L878-L878, [2:19:56]-[2:19:56])

Row 3.82 (CONTEXT):
> "now they are trying to recover I want to see if they can manage to close above because if I'm not wrong we are still in the"
**Source GPS: Is1HvdfQm5c | END** (ASR, L880-L880, [2:20:13]-[2:20:13])

Row 3.83 (PROOF):
> "yeah they are recovering buyers to control back"
**Source GPS: Is1HvdfQm5c | END** (ASR, L882-L882, [2:20:38]-[2:20:38])

Row 3.84 (LESSON):
> "no and no the effort is invalidated when you break it"
**Source GPS: Is1HvdfQm5c | END** (ASR, L884-L884, [2:20:52]-[2:20:52])

Row 3.84 (LESSON):
> "it's uh you see the market tap into this area this is the area I think it's visible in colors but this is the area it gets invalidated if it breaks"
**Source GPS: Is1HvdfQm5c | END** (ASR, L885-L885, [2:20:58]-[2:20:58])

Row 3.85 (CONTEXT):
> "so now why should be invalid I was thinking that the next candle here would be a"
**Source GPS: Is1HvdfQm5c | END** (ASR, L887-L887, [2:21:19]-[2:21:19])

Row 3.86 (HOLD):
> "breakout so they test and they collapse but no they absorbed completely so still the area is valid and buyers are still strong still we can"
**Source GPS: Is1HvdfQm5c | END** (ASR, L888-L888, [2:21:30]-[2:21:30])

Row 3.87 (CONTEXT):
> "We saw multiple entry technique so for example let's see the trade off before okay you have absorption here"
**Source GPS: Is1HvdfQm5c | END** (ASR, L890-L890, [2:21:52]-[2:21:52])

Row 3.88 (ENTRY):
> "and you have buyers at the top you have this breakout you can put a limit order this level with"
**Source GPS: Is1HvdfQm5c | END** (ASR, L891-L891, [2:22:02]-[2:22:02])

Row 3.89 (STOP_SET):
> "a stop loss between this aggression and when you have another confirmation from the buyers"
**Source GPS: Is1HvdfQm5c | END** (ASR, L892-L892, [2:22:11]-[2:22:11])

Row 3.90 (STOP_MOVE):
> "you can put your stop loss to zero like we did before"
**Source GPS: Is1HvdfQm5c | END** (ASR, L892-L892, [2:22:11]-[2:22:11])

Row 3.91 (STOP_SET):
> "you can enter with the stop loss below the area"
**Source GPS: Is1HvdfQm5c | END** (ASR, L893-L893, [2:22:22]-[2:22:22])

Row 3.92 (STOP_MOVE):
> "put your stop loss at zero when you see this and let's"
**Source GPS: Is1HvdfQm5c | END** (ASR, L893-L893, [2:22:22]-[2:22:22])

Row 3.94 (STOP_SET):
> "example speed of tape here you can add your stop loss below the aggression of the buyers below the area for a risk to reward cannot surprise"
**Source GPS: Is1HvdfQm5c | END** (ASR, L895-L895, [2:22:42]-[2:22:42])

Row 3.95 (ENTRY):
> "the area where you have the best entry so if we want to be precise now I don't know if we will get filled but if we want to be really precise this one"
**Source GPS: Is1HvdfQm5c | END** (ASR, L898-L898, [2:23:07]-[2:23:07])

Row 3.96 (STOP_SET):
> "is should be the area and the stop loss should be below here okay"
**Source GPS: Is1HvdfQm5c | END** (ASR, L899-L899, [2:23:18]-[2:23:18])

Row 3.97 (TARGET_SET):
> "it's a 1 2 3.5 it's an amazing trade okay it's limited so if you get field it's good which"
**Source GPS: Is1HvdfQm5c | END** (ASR, L900-L900, [2:23:28]-[2:23:28])

Row 3.98 (ENTRY):
> "and we see the market coming back printing a candle like this Here you can have another execution or the"
**Source GPS: Is1HvdfQm5c | END** (ASR, L902-L902, [2:23:49]-[2:23:49])

Row 3.99 (STOP_SET):
> "first execution with a stop loss below the aggression of the sellers"
**Source GPS: Is1HvdfQm5c | END** (ASR, L903-L903, [2:23:59]-[2:23:59])

Row 3.100 (TARGET_SET):
> "and The target of both is it clear guys"
**Source GPS: Is1HvdfQm5c | END** (ASR, L903-L903, [2:23:59]-[2:23:59])

Row 3.101 (REJECT):
> "but I don't advise you do this trade there."
**Source GPS: Is1HvdfQm5c | END** (ASR, L903-L903, [2:23:59]-[2:23:59])

Row 3.101 (REJECT):
> "I don't like it at all. It's Be set up see set up this one was triple-a."
**Source GPS: Is1HvdfQm5c | END** (ASR, L904-L904, [2:24:09]-[2:24:09])

Row 3.102 (LOCATION):
> "it's the beginning of the candle with the complete control of the buyers"
**Source GPS: Is1HvdfQm5c | END** (ASR, L909-L909, [2:24:36]-[2:24:36])

Row 3.103 (REJECT):
> "yeah this point the session is done the major volatility of the day we had okay we had amazing risk to reward anything you take from now it's to study"
**Source GPS: Is1HvdfQm5c | END** (ASR, L911-L911, [2:24:49]-[2:24:49])

Row 3.104 (LESSON):
> "it's not because this is a good setup this is an average setup guys okay thank"
**Source GPS: Is1HvdfQm5c | END** (ASR, L912-L912, [2:24:59]-[2:24:59])

Row 3.105 (CONTEXT):
> "Choppy now, okay Think we can still go up a little bit."
**Source GPS: Is1HvdfQm5c | END** (ASR, L919-L919, [2:26:00]-[2:26:00])

Row 3.106 (LOCATION):
> "the gap this one is the reloading gap when they are"
**Source GPS: Is1HvdfQm5c | END** (ASR, L920-L920, [2:26:04]-[2:26:04])

Row 3.107 (CONTEXT):
> "another gap here is true another gap they are building the pressure guys"
**Source GPS: Is1HvdfQm5c | END** (ASR, L926-L926, [2:27:00]-[2:27:00])

Row 3.108 (CONTEXT):
> "think probably can go also here amazing"
**Source GPS: Is1HvdfQm5c | END** (ASR, L931-L931, [2:27:44]-[2:27:44])


## 3.6 Ambiguity flags


(part 1: Is1HvdfQm5c_part1.md)

- 1.14: "ORA" is an ASR token; instrument unknown.
- 1.20: [?] "I don't use order from Bitcoin": probably "order flow"; both readings stay.
- 1.4: [?] "POC from 16": number unknown; whether Fabio or a viewer owns the "short" is not settled (he says "that I was taking before").
- 1.9: ASR number string "1 2 3 1 2 4 1 2 5" at L60-L61; the profit "41 42 thousand" and the loss "15 000" are [ASR number: check frames].
- 1.15: "word of wisdom" and "the rates" are ASR tokens [?]; the two amounts 25,000 and 10,000 and 15,000 need frame checks.
- 1.38: [?] "I entered the short also amazing setup": Fabio about himself, or reading a viewer message. Kept UNKNOWN.
- 1.39: [?] "squeeze the lot this law": ASR; read as "this low".
- 1.48: L182-L183 "counter trend this one is" / "trend following": garbled.
- 1.50: "a closing above it's a huge risk reward": two readings (stop on a close above, or entry on a close above).
- 1.51/1.52: "this law" probably "this low"; direction of "a good new movement" not stated (sellers absorbed suggests up, "break this low" suggests down).
- 1.55/1.56: two readings of the bias: "space to retrace" (short) vs "the value of the session is telling us that we go high" (long). Both kept.
- 1.59: "BA" is an ASR token (breakeven?); meaning not settled.
- 1.64/1.65: 97, 75, 123.9, 125, 139, 255, 73, 65, 62 may be contracts or prices; frames needed.
- 1.74: "before the area": in front of or behind the area.
- 1.78: "eye" probably "high".
- 1.77: "640 640" repeated; full price missing (probably 25,640).
- 1.79: 25 646.39 [ASR number: check frames]; L264 reads it as "twenty five thousand six hundred and forty six".
- 1.80: "unfortunately failed auction": which side failed is not stated.
- 1.84: [?] "shoot thus".
- 1.89: "39 250 89 around around" and "25 million of notional" are ASR number strings.
- 1.96: [?] "deep trades" probably "big trades".
- 1.97/1.98: 681 may be 25,681; the viewer's long entry is not given.
- 1.103: "took two now securing one hour I took two one-to-one": a viewer message or Fabio about himself; kept as VIEWER, so no PARTIAL row. Reading 2: Fabio saying he took two and secured one at 1:1.
- Line 322 ends mid sentence; the next part starts with "so let me clean everything".
- Position tags: by character offset the BEGIN/MIDDLE border is at about line 286 to 292 (not 318); anchors from L287 on are tagged MIDDLE.


(part 2: Is1HvdfQm5c_part2.md)


- 2.2: 'attack the law' = low [?]; 25,545 is an ASR number, frames decide.
- 2.8: 'stop printing this week' [?] (weak / wick / wall?).
- 2.13: 'sleepage' [?] = slippage.
- 2.15: 'self-protection level' [?] and 'reload on the cell side' (cell = sell).
- 2.20: 'I understand the bottle' (L375-378) [?] = model; the viewer is asking how the passive orders defend an area.
- 2.27: 'we are stacking our third position for the day' reads either as a live add (third position of the day) or as the generic plan 'we stack a third position' after acceptance. Both readings stay open. Day count of trades before this range is not stated in this range.
- 2.28: 'I got this one running with small risk from the fair value gap protected by 400 buyers' then 'nice one hey it's the one that we saw before' reads as a viewer message read aloud; speaker UNKNOWN, not turned into a Fabio trade. Alternative reading: Fabio describing his own trade.
- 2.29: 'there is not follow through on the reduction' [?] (direction?).
- 2.34: sentence cut by the ASR ('there is a bigger movement and').
- 2.37: 'buyers stock at the top' [?] = stuck.
- 2.38: 'feeling point' [?] = filling point; whether the position was actually filled there (live) or it is only an illustration ('would have been') is not settled.
- 2.42: 'the analysis invalidator' [?]; whether this describes the stop of the live position or a general rule is not settled.
- 2.43: 'He one minute risk-free' [?]; 'stop losing at zero' = stop loss at zero (stop at entry); whether the position under discussion is the live one or a viewer's is not settled.
- 2.44: 'three brekivan for brekivan' [?] = three break-evens rather than one loss.
- 2.48: 'we took two one two three', 'one two three six are plus one point five you close seven point five' are garbled R multiples [ASR number: check frames]; the 'other session' reference is unclear.
- 2.49: 'the confidence of going to break even' - one reading: stop to break even when the market allows; other reading: viewers' confidence to go to break even. The first is used.
- 2.71: 'one to two point seven one two two point six' is two numbers (2.7 and 2.6?) or a repeat; 'if you stay in the long term' [?] = stay in the long. Hypothetical for viewers, not his exit.
- 2.73: side long is taken from 'if you stay in the long' (L530); 'we are inside from the beginning of the move' does not itself say long.
- 2.79: 'this buy was counter thrown' [?] = counter trend (his next words: sellers still in control). Which buy ('first level marked for the day') and whether it is part of T2.1 is not settled.
- 2.82: 'then unfortunately they broke how they broke with sellers absorbed' [?]; reading A: the sellers' attempt broke because sellers were absorbed and buyers rewarded; reading B: price broke the sellers' level. Kept as two readings.
- 2.86: 'the reload zero down and shoot up' [?]: zero down = stop to zero, or a reload from zero risk, or 'zero down' = price moving down to zero [?]. Unsettled.
- 2.94: 'we take partial' is spoken in the past recap of a day trade; which trade (side long assumed from the buyers' trade above) is the implied side, not said.
- 2.103/2.104: fade side is short only by 'stop loss above' (L610); the word short is not said in these rows.
- 2.112: 'confirm fate setup' / 'fate setup' = confirmed fade / fade; '35 to 40%' win rate is an ASR number.
- L463-L464 'Bravo Fabio ... cot Florian' [?]; L475 'interactive brokers' exchange is chat noise and has no row.
- Speaker note: this range is Fabio answering chat; viewer names (Damian, Mario, Jason, Peter, Arsalan) are spoken but the viewers' words are not separable from his in the ASR. Rows are FABIO only where first-person or answering style settles it.


(part 3: Is1HvdfQm5c_part3.md)

- 3.17 [?] "i'm not loading" then "i was trying to hide that i was loading but it's visible now": reading 1 he is joking and holds no position; reading 2 he was adding/loading size. Left open.
- 3.10 [?] "zero draw down" (rows 3.6, 3.10, with "zero draw" cut at a line end): reading 1 the pattern gave zero drawdown on past trades; reading 2 a statement about the live trade. Left open.
- 3.14 [?] "they are pushing the auction down" [?]: he is describing buyers absorbing with a passive wall, so "down" may be a slip for up, or the wall pushes the auction down. Not repaired.
- 3.15 [?] "big gamma level" and "i'm not watching gamma" (L689): reading 1 an options gamma level is named; reading 2 ASR garble of a viewer's name. Not resolved.
- 3.19 [?] "all with Nasdaq cap" (L704) and "Nasdaq efforts" (L881), "the Nasdaq effort" (L828): may be mishearings of "deep effort" (he names the deep effort study at L758, L768, L772, L832). The instrument stays NOT STATED.
- 3.20 [?] "all this aggressive sell all this pressure got confirmed or absorbed": two readings (sell pressure confirmed, or absorbed); the next lines say "long absorbed ... we continue long".
- 3.42 [?] "the line point of the last point of aggression of the sellers" [?]: reading 1 the limit order sat at that point; reading 2 it is the level the buyers must hold. Not resolved.
- 3.50 [?] L785-L789 and L795: "you can put this one and see" and "if this will that field does on the downtick it will already be one to one point five" then "of course I removed": reading 1 a second resting order existed and was removed by L795; reading 2 pure teaching to viewers. Not rowed as ENTRY.
- 3.38 [?] L752-L753 "another one two three the last one two three": ASR may be a count-down, or the number of orders. No size stated.
- 3.97 [?] "it's a 1 2 3.5" [ASR number: check frames]: may be "1 to 3.5" or a price list; "it's limited" may be "it's a limit [order]".
- 3.101 [?] "Be set up see set up this one was triple-a": reading 1 "B setup, C setup; this one was triple-A" (grades); reading 2 other words. "This one" may mean the earlier trade.
- 3.94 [?] "you can add your stop loss" (L895): may be "you can put"; may also be an ADD of size. Recorded as STOP_SET (hypothetical).
- 3.68 [?] "part of risk resistance" and "path of risk resistance" (L836-L837) are not repaired; the context reads like path of least resistance.
- 3.79 [?] "controlling a longer short position" (L874) and the Michael exchange: viewer's side (long vs short) is unclear in places; Michael's own words (L856) are chat text read aloud.
- 3.64 [?] L824-L826 "Leonardo say Fabio let it go today it's all break even": speaker UNKNOWN, may be a chat line he reads out, or his reply.
- 3.76 [?] L861-L867 numbers (2500, 2499, seven, 15, six point five contracts) are ASR numbers: check frames; instrument/contract type ("mini") not stated.
- 3.26 [?] L718-L720: "with 30 ... with 60", "still 77": big-trade filter sizes are ASR numbers: check frames; units not stated.
- 3.4 [?] L651 "care to take out part of my profit on this area because I can't reverse" [?]: first word cut ("with a personal care"), so who takes the partial is not settled; teaching, no PARTIAL row.


## 4. Day notes


(part 1: Is1HvdfQm5c_part1.md)

- Session phase: Fabio live with chat and a screen share, charting; London session called "not so much volume" at L155 (about 22 min in).
- No position of his own is stated in L11-L322 (no LIVE_TRADE). Trade blocks are HYPOTHETICAL, ILLUSTRATION or VIEWER_Q.
- P&L statements with spoken numbers (all [ASR number: check frames]): a November day built "41 42 thousand dollars", then "I only lost 15 000 in profit" after four stop losses (L61-L69); "do 10 20 30 40 50 000 per day" (L38); previous live: "a crazy sniper 25 000" then "we gave back 10,000" (L78-L81); "the session of $50,000 on YouTube" (L146, second of December).
- Risk and behaviour rules he states: three rules (process over result, stay out when emotionally unfit, one personal account = one bullet) at L85-L102; no 5 to 25 trades a day (L102); target not greedy (1 to 10 lowers the hit rate; L225-L226); win rate 30 to 35 percent for the home run version (L245); with absorbed sellers or buyers "first touch" thinking (L276); "I usually don't like to take trades when there is no support from the aggressive order market participants" (L290-L291).
- Chat (viewer) money lines: "Damian is $10,000 in profit", "I made $400 today" (L271-L273); not Fabio's.
- Announcements: "Avengers team" / battlefield chat opening tomorrow, a nutritionist guest idea, a TradingView volume spread analysis template next week (L12-L19, L111-L115). Not trade content.
- Previous session: "garbage market", multiple breakevens (L23-L27); yesterday: perfect rejection at the POC, he was delayed (L32-L33).


(part 2: Is1HvdfQm5c_part2.md)


- Session phase in this range: mid-session (about 49:25 to 1:38:25). A live long position is discussed in the past tense (partial taken, reload, final target 'rejecting now'), then a recap (profile framing, rows 2.76, 2.77, 2.78) and then a lecture on four ways to qualify an area (rows 2.101, 2.102, 2.106, 2.113).
- No spoken P&L for today in this range (no dollar total for the day). Dollar figures are examples or preferences: '$200' take-out for viewers (row 2.52), 'floating 10, 20, 30,000' as the frustrating case (row 2.90), 'three, four, $10,000' trades totalling '40,000' as his preference (row 2.91); '50,000 session' is a past session referenced at L527 (row 2.69).
- Risk rules he states: after a loss he continues 'till 3' and at 'a maximum of 3 stop loss' he lowers exposure but 'usually a stop for the day' (row 2.55); three stops in a row 'two or three times per month' (L467-L468); a stop is 'only the commission' because management is fast (row 2.56); day profit is stacked and used as risk for the next trade, 'after i take three take profits at the next trade it's part of the profit i made' (row 2.64); the viewer's '0.25' is [ASR number: check frames].
- Own stopping rule today: 'i will not take other trades okay because we already took amazing setup for today' (row 2.108).
- Trade count: 'our third position for the day' (L404, row 2.27) is ambiguous (plan or live). Wins and losses of the earlier trades are not stated in this range.
- Targets: 'the final target not of the day is the final target for the position' (row 2.88); he does not hold for the full-session absorption at the top because giving back large floating profit is frustrating (rows 2.89, 2.90).
- Win rates stated: 'high win rate like today' (L611-L612) for the confirmed fade; '35 to 40%' for the fade (row 2.112).


(part 3: Is1HvdfQm5c_part3.md)

- P&L: no P&L figure is spoken in L634-L932. "payout certificate 6000" (L923, [2:26:30]) is a viewer's comment read aloud [ASR number: check frames]; it is not his P&L.
- Trade count: "we did uh three trades one was i don't remember guys how many are we made" (row 3.39, [1:59:11]); earlier text also says "we already took amazing setup for today" (L619, previous range).
- Day story: "today the market only went up and we managed to take all the long on the way up" (row 3.77, [2:18:25]); the later chat read has him telling a viewer who shorted that sellers are only "in control now" inside the area (row 3.79).
- Session phase: news in five minutes at [1:52:44] and four minutes at [1:53:36]; volatility burst [1:57:07]; "the last trade of the day" at [1:58:53]; "the session is done the major volatility of the day we had" at [2:24:49]; stream ends [2:27:49] after about "two hours and half" ([2:25:09]-[2:25:19]).
- Risk rules he states: unfilled orders are removed (row 3.46); do not execute before the candle close (row 3.36); no short against the bias while the auction is on (row 3.33); fixed dollar risk per trade sets the contract count, example figure 2500 [ASR number: check frames] (row 3.76); stop to zero after another confirmation (row 3.90).
- Tools named: speed of tape, big trades (filter 30 / 60 / 77 [ASR number: check frames]), cumulative volume delta, delta candlestick, deep effort (proprietary study on thickness of the book), volume 360, VSA, gap (reload / rebalance), control area (supply/demand).


## 5. Setup candidates (proposal for the catalogue merge)


(part 1: Is1HvdfQm5c_part1.md)

- Candidate A: absorbed buyers at the top, then aggressive sellers lock the movement, short on the test of the level -> supports FAB-2 (absorbed push, failed auction of one side then the other side's aggression). Rows 1.28, 1.29, 1.30, 1.31, 1.32, 1.33, 1.34, 1.35, 1.36. Anchors: "you have an aggression aggressive sellers lock in the movement" ; "the trade that in 2025 gave me the most amount of money is the test of this level with" ; "shoot for a 1 to 4.5". Entry: "the test of this level with the confirmation of absorbed buyers" (after proof, order type unknown); stop: "a super small stop loss", "cover yourself above the area"; target: "shoot for a 1 to 4.5"; management: NOT STATED. Also supports the earlier-session link row 1.36 (the $50,000 session).
- Candidate B: "the squeeze setup" long at the third touch of a cluster (sellers absorbed, buyers rewarded and confirmed, cover below the area, target 1 to 5 / 1 to 4.9) -> supports FAB-5 (buyers protect a level, squeeze trapped sellers); NEW name in his words: "the squeeze setup" / "the pattern that I take the squeeze". Rows 1.61, 1.62, 1.63, 1.66, 1.68, 1.76. Anchors: "these buyers got the reward that the candle close long we managed to break this level" ; "the sellers is absorbed the buyers got confirmed even" ; "covering yourself below the area this is the squeeze setup". Entry: after the absorbed sellers and the rewarded buyers (order type unknown; late entry fine); stop: below the area, a stop area "640" [ASR number: check frames]; target: 1:5 / 1:4.9, or "the home run" (30 to 35 percent hit rate), or the next level 25 646.39; management: NOT STATED. Contradicts nothing; the "next level" later shows a failed auction (row 1.80).
- Candidate C: gap / inefficient volume as a reload place (a micro gap between two candles, "if the candle close green ... shoot") -> supports FAB-8 (volume-defined fair value gap rejection). Rows 1.83, 1.84. Anchor: "this is inefficient volume because it created a micro gap". Entry: reload on the gap, first reaction at the level (order type unknown); stop and target: NOT STATED; management: NOT STATED.
- Candidate D: buyers protect a level (reload on the tape, hold after repeated breaks, reclaimed level, plan to long after recovery of a huge candle plus big trades; target the viewer's 681) -> supports FAB-5. Rows 1.93, 1.106, 1.110, 1.111, 1.98, 1.112. Anchors: "they are reloading to protect this level" ; "they try to break three four five times and they always hold this level that". Entry: recover the huge candle and see some big trades; stop: "really high stop loss" (viewer's cluster idea); target: "681" / "one to two point five"; management: NOT STATED.
- Candidate E (contradicts / conditions): counter trend shorts are not taken ("I don't like to take them"; the first level of the day marked as "counter trend") -> conditions reversal rows FAB-2 and FAB-4: reversal short at an edge is declined when it is counter trend and when aggressive big orders do not support it; also his model line "I only enter in profile framing in trend condition and I execute with big trades". Anchors: "but these are counter trend trade and I don't like to take them" ; "the model is saying that I only enter in profile framing In in trend condition and I execute" ; "like to take trades when there is no support from the aggressive order market participants". Entry/stop/target: NOT STATED.
- Candidate F (contradicts / conditions): momentum breakout in a balance space exactly at the value area low is "the worst case" because of the limit wall -> conditions FAB-1 (balance with CVD pressure, break on volume): he takes a sell continuation "if we break out this level" (row 1.109) but not at a level with a wall. Anchors: "this is the worst case that you can have for a momentum trade" ; "i will consider a cell continuation if we break out this level yes". Entry: after the breakout of the level (order type unknown); stop/target: NOT STATED.
- Candidate G: heat-map family 4.1 (wall, reload, protection): "the limit price wall on the top or on the bottom it's giving keeping you in consolidation", "this level is sustained by ... 25 million of notional value" -> supports the tool family 4.1 (passive liquidity wall; break gives a squeeze). Rows 1.108, 1.89, 1.53. Entry/stop/target: NOT STATED.

(part 2: Is1HvdfQm5c_part2.md)


### S1
- relation: SUPPORTS FAB-5 (buyers protect a level, long, squeeze) and FAB-2 (absorbed push, then the other side's aggression)
- what he says: Sequence he calls the same setup as the trade taken: sellers absorbed at the bottom, buyers absorbed at the top, breakout of compression, reaction phase, test with aggressive sellers, then up. Buyers protect the level while the last test absorbed the sellers.
- anchors: rows 2.109 (two anchors), 2.6, 2.93
- entry: 'absorption in one candle, two following absorption, then an aggression' (row 2.45); 'inside from the beginning of the move' (row 2.73); stop: NOT STATED as a price, 'if it break this level the analysis invalidator' (row 2.42); target: 'the final target for the position', 'the most sensitive level' (row 2.88), R:R 1:3.6 [ASR number: check frames] (row 2.67); management: stop to zero 'not even one candle' (row 2.43), partial at the sellers' absorption at the top (row 2.94), 'the reload' after the test (row 2.86), trail 'below the big trade' (row 2.66). Condition he adds: do not take it right next to the wall (row 2.110).

### S2
- relation: heat-map liquidity family 4.1 (tool family: wall, protection level, reload, break and protect)
- what he says: Walls and protection levels as the read: sellers' intermediate wall at 25,632 [ASR number: check frames], a level that flips to a sell-side reload level if broken, buyers' protection level, 'they are putting billions here', a wall 'identified before' that does not mean short for the session.
- anchors: rows 2.7, 2.15, 2.18, 2.98
- entry: NOT STATED (wall is a location, not an entry); stop: 'put your order here with a stop loss slightly below' risks slippage at a decision level (row 2.13); target: next level if the wall breaks (rows 2.19, 2.99); management: wait for the level 'to stop printing' and a 'clean break' before a short (row 2.8).

### S3
- relation: NEW (his own words): 'virgin POC test' inside profile framing long; related to FAB-4 (rejection at the previous session high) but the aim is the untested POC
- what he says: Profile framing long: price tapped the previous session's high, was rejected, and he tried 'to capitalize' on the virgin POC test, with the first marked level at the bottom of the day.
- anchors: rows 2.76, 2.77, 2.79
- entry: 'this buy' at the bottom-of-day level, counter-trend while sellers were still in control (row 2.79); stop: NOT STATED; target: the virgin POC (price NOT STATED); management: NOT STATED.

### S4
- relation: SUPPORTS FAB-2 (failed auction of one side, then the other side's aggression) and FAB-4 (reversal at an edge) as the fade family; a win-rate statement on both variants
- what he says: Qualified area, consistent absorption of aggressive buy orders at the top. Fade: stop loss above, take the beginning of the move for a huge risk to reward, lower win rate (35 to 40% [ASR number: check frames]). Confirmed fade: wait for the aggressive sellers to take control of the movement you qualified, then engage, higher win rate.
- anchors: rows 2.104, 2.105, 2.112
- entry: confirmed fade after the sellers take control (row 2.105); stop: 'stop loss above' for the fade (row 2.104); target: NOT STATED; management: NOT STATED. HYPOTHETICAL (viewer lecture), not a trade he took in this range; mirror stated? no - do not assume (the long side is described by the S1 sequence, not mirrored here).

### S5
- relation: SUPPORTS FAB-8 (volume-defined fair value gap / inefficiency) weakly; speaker of the explicit fair value gap trade is UNKNOWN
- what he says: Price fills the inefficiency and reloads on it; a test 'is closing an inefficiency' and closes at the level with absorption; a viewer-style message mentions 'the fair value gap protected by 400 buyers'.
- anchors: rows 2.9, 2.37, 2.28
- entry: 'this one here would have been your feeling point' (row 2.38); stop: NOT STATED; target: NOT STATED; management: NOT STATED.

### S6
- relation: SUPPORTS FAB-1 (balance, break on volume) as the conditional momentum short, and records its rejection today
- what he says: Inside a balance at an edge: 'you can short now' only if the market gives the breakout on an aggressive candle (momentum phase); today he rejects it because the buyers rejected four tests and the sellers show no strength; a short needs the level to collapse cleanly.
- anchors: rows 2.4, 2.5, 2.8
- entry: momentum short on the breakout candle (HYPOTHETICAL, row 2.4); stop: NOT STATED; target: 'the level that we saw before' (row 2.19); management: NOT STATED.

### S7
- relation: NEW (his own words): 'stacking one order that is capitalizing on the explosion of the range' / 'clean breakout and test'
- what he says: Both sides stuck in a range (results zero); he waits and stacks one order after acceptance: big trades at the top or a clean breakout and test; ties to the position count 'third position for the day'.
- anchors: rows 2.27, 2.100
- entry: stack after a clean control point with acceptance (rows 2.26, 2.27); stop: NOT STATED; target: NOT STATED; management: stop to zero because the profit of the previous position is not to be used (row 2.33).

(part 3: Is1HvdfQm5c_part3.md)

- S1. NEW: "control area" (supply/demand that controls price, flips when broken, paired with order flow).
  - catalogue: supports none of FAB-1/2/4/5/6/8 directly (a structural framing); related to FAB-5 (demand protected by buyers) and FAB-2 (absorption/exhaustion at the area)
  - anchors: row 3.2, row 3.4, row 3.5 (see VERBATIM ANCHORS)
  - entry: NOT STATED (area plus absorption or exhaustion in order flow); stop: "you will have some stop loss but they are part of the game" (no level); target: NOT STATED; management: take part of profit at the area when sellers are confirmed in control [?] (teaching, row 3.4).
- S2. NEW (his words): "absorbed sellers, buyers at the top, break out and testing with absorption on the bottom" (long of bias; "zero draw down").
  - catalogue: supports FAB-2 (rewarded effort of one side then the other side's aggression; he says the missing piece is "the aggressive sellers" printing, row 3.10) and the heat-map family 4.1 (break and protect with a wall); see also FAB-5 (buyers protect the level)
  - anchors: row 3.7, row 3.10, row 3.6 (see VERBATIM ANCHORS)
  - entry: after the break, a test with absorption at the bottom (price NOT STATED); stop: NOT STATED; target: NOT STATED; management: NOT STATED ("zero draw down" is the stated result of the pattern).
- S3. Gap rule: the candle after the gap decides (rebalance and close green = violent move up; eating the gap down to the start of the move = absorbed, move fails); "the reloading gap when they are really aggressive".
  - catalogue: supports FAB-8 (volume-defined fair value gap rejection)
  - anchors: row 3.19, row 3.106 (see VERBATIM ANCHORS)
  - entry: NOT STATED; stop: NOT STATED; target: NOT STATED; management: read the next candle's close (bar timeframe NOT STATED).
- S4. NEW (his name): "deep effort" area (proprietary study on book thickness): long limit at the area the buyers control, valid until broken, "final target" up.
  - catalogue: NEW; relates to heat-map family 4.1 (wall, protection) and FAB-5 (buyers protect a level)
  - anchors: row 3.47, row 3.67, row 3.84 (see VERBATIM ANCHORS)
  - entry: limit at "the area where you have the best entry" (price NOT STATED); stop: "below here" / below the buyers' aggression and the area (no distance); target: "this target", stated multiple "1 2 3.5" [ASR number: check frames]; management: stop to zero after another confirmation (row 3.90).
- S5. Entry technique from a past trade: absorption, buyers at the top, breakout, limit at the level, stop between the aggression, stop to zero on another buyer confirmation.
  - catalogue: supports FAB-2 and FAB-5; instance of S2
  - anchors: row 3.88, row 3.89, row 3.90 (see VERBATIM ANCHORS)
  - entry: limit at "this level" after the breakout; stop: between the aggression or below the area; target: NOT STATED; management: stop to zero.
- S6. NEW (his name): "the last sniper" limit at the last point of aggression of the sellers, long, only filled on a test; removed if not filled.
  - catalogue: supports FAB-5 (buyers protect a level, long) tentatively; role of the level not settled (row 3.42); no fill, so it adds no outcome
  - anchors: row 3.38, row 3.42, row 3.46 (see VERBATIM ANCHORS)
  - entry: limit at the test of the broken level (price NOT STATED); stop: NOT STATED; target: NOT STATED; management: remove the order if not filled.
- S7. NEW filter (his words): "wait for the close" / do not execute during the news candle; speed of tape must complete the break.
  - catalogue: contradicts any entry on a news-candle break before the close; consistent with FAB-6 only in that timing matters (no IVB words here)
  - anchors: row 3.36, row 3.40 (see VERBATIM ANCHORS)
  - entry: after the close; stop: NOT STATED; target: NOT STATED; management: NOT STATED.
- S8. Counter-bias short refused while "the auction is still on"; a break of the level changes his mind.
  - catalogue: constrains FAB-4 (failed breakout reversal): here no reversal short while the bias auction is on
  - anchors: row 3.33 (see VERBATIM ANCHORS)
  - entry: NOT STATED; stop: NOT STATED; target: NOT STATED; management: NOT STATED.
- S9. CVD/passive wall reading: CVD above the top shows loading; a CVD sell candle printing green shows absorption with passive liquidity.
  - catalogue: supports FAB-1 (CVD pressure) as a reading and heat-map family 4.1 (passive wall); no entry attached
  - anchors: row 3.12, row 3.13, row 3.14 (see VERBATIM ANCHORS)
  - entry: NOT STATED; stop: NOT STATED; target: NOT STATED; management: NOT STATED.

## 6. Read ranges


(part 1: Is1HvdfQm5c_part1.md)

Read in order with the Read tool: L1-L60 (context incl. header), L60-L119, L120-L179, L180-L239, L240-L299, L300-L359 (rows only up to L322). The header lines L1-L10 and the separator L11 hold no spoken text; spoken text starts at L12 [0:03]. Rows were written for L12-L322 only; L323-L359 were read past the range end for the sentence close and are not used.


(part 2: Is1HvdfQm5c_part2.md)


Context only (no rows written): L263-L322 [39:51-49:14], read in one pass before the range.
- L323-L382 [49:25-57:58] read, rows written
- L383-L442 [58:02-1:06:59] read, rows written
- L443-L502 [1:07:11-1:17:12] read, rows written
- L503-L562 [1:17:17-1:27:15] read, rows written
- L563-L622 [1:27:25-1:36:36] read, rows written
- L623-L633 [1:36:47-1:38:25] read, rows written


(part 3: Is1HvdfQm5c_part3.md)

- Context only (not rowed): L574-L633 [1:29:11-1:38:25], 60 lines.
- L634-L693 [1:38:40-1:48:29]
- L694-L753 [1:48:58-1:59:04]
- L754-L813 [1:59:11-2:09:04]
- L814-L873 [2:09:11-2:19:08]
- L874-L932 [2:19:18-2:27:49]
- Lines L697-L699, L782-L783, L805-L807, L850-L851, L913-L916, L922-L923, L928-L929, L932 are chat banter, thanks, a Dubai meet-up joke, audio gaps or goodbyes without a decision; they were read and have no row.
