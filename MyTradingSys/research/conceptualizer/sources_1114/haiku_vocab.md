# Gap hunt 1113: vocabulary sweep (worker haiku_vocab, method stage E)

Read-only. No commits, no ship, no Chrome, no YouTube fetch. Scripts: `C:\Users\E-NGIN~1\AppData\Local\Temp\claude\daf915e1cb198d32\9b0ce8fb-f501-4fac-9178-48bbfbffdb4d\scratchpad\gap_hap\` (`sweep2.py`, `absent_terms.json`, `top60.json`, `quotes.py`, `verify_quotes.py`).

## Method and counts

| Step | What | Result |
|---|---|---|
| a. Load | 164 `raw_transcripts_canonical/*_raw.txt` from origin/fast-track; 42 excluded by header as non-Tom/Fabio (Malkan 17, Krown 16, Kurisko 8, LongShort 1) | 122 Tom/Fabio videos used |
| b. Count | 1-3 word n-grams, stopwords and generic English dropped, no n-gram across punctuation; df = number of videos | 490 candidates with df>=5 and a trading word; 479 after sub-phrase dedupe |
| c. Check | exact normalised phrase count in brief corpus: TOM_FABIO_FACTS.md, RULEBOOK.md (tom_fabio_rebuild), ORDERFLOW_RULES.md, tf_extraction_plan_1113 ANSWERS (4 files), auction_context.py, fabio/v3 signals.py + models.py, vp_return_to_value.py | 227 terms with <=1 hit; curated to top 60 trader terms below |
| Quotes | 36 quotes checked by script: each is an exact substring of the cleaned transcript (whitespace only collapsed) | 36 of 36 OK |

Limits: captions are auto (ASR errors, e.g. "30-inut", "Workclass edge"). "Absent" means absent from the brief's corpus only. Repo-wide, the same phrases hit .md notes often (e.g. "footprint chart" 144 py+md hits), and some concepts are coded in other fabio modules (e.g. `fabio/orderflow_bars.py`), so treat "0 hits" as "not in the scoped docs or code".

Sponsor copy: a "World Class Edge" plug sits in 13 transcripts. It inflates "institutional traders" and "market makers", so those two rows were checked and quotes taken only from non-plug text.

Control: the brief's "closing-price count in 116 transcripts" is not reproduced. "closing price" is in 24 of the 122 Tom/Fabio videos (37 of 164 canonical files). "closing" alone is in 43 of 122. Our docs already hold it (13 "closing price" hits, 7 "closing price count"), so it is uncoded, not absent. That matches iteration 1.

## Gap rows (brief format)

| id | stage | pattern | gap in one line | evidence | already in iteration 1? | fix |
|---|---|---|---|---|---|---|
| V1 | C | NEW (merged concepts) | Market profile (time-based, TPO) is his main level source in 23 videos. Our docs and code hold only volume profile. He uses both together. | 3o1VVsfBmmU: "The combination of market profile and volume profile."; 5Ljfwvtktek: "I look at the value area high, the value area low, the overall market profile, and the point of control or POC." | N | re-frame (two level inputs) + extract |
| V2 | C | 3 (one word, several claims) | "volume area" (9 videos) means a low-volume gap between two peaks, not the value area. Our docs say "value area" (48 hits) and "volume area" zero times; "low volume node" appears 3 times. | 4P5WAxyPCis: "an area of low volume between two peaks"; 0CrkbfuIhkc: "that's a typical low volume area that the market then likes to fill in." | N | re-frame (LVN vs value area) + extract |
| V3 | C | NEW (setup chosen by phase) | Counter-trade, breakout and trend-follow are three setups he picks by market phase, not one entry. No setup switch in the scoped code (grep of signals.py and models.py: 0 hits). | 3o1VVsfBmmU: "Are you more of a counter trader? Are you more of a trend following trader?"; 2xnNPIyHGQ4: "Are the markets more suitable for counter trades or are they better for breakouts and trend following setups?" | N | extract (phase to setup rule) + re-code (switch) |
| V4 | T | 4 (method by eye) | Execution chart: he goes from the high-TF profile to a 1-min or 5-min footprint to time the entry. The bar size depends on style. Our models fix one bar size each (1m in v3 IB, 5m in vp_return). | 3o1VVsfBmmU: "I transfer these price areas over to my small simple chart. In this case, a five-minute chart. That also depends on what you like, what you prefer, longer trades or shorter trades"; 4P5WAxyPCis: "Personally, I like to use the 5-minute chart." | N | extract (TF rule by style) + re-code (two-TF stack) |
| V5 | T | NEW | Entry order type: he uses a market order or a limit at the halfway point of the candle, and the rule for choosing is not stated. Our models have a rest limit valid 3 bars (models.py:33) and no market branch. | 5Ljfwvtktek: "I decide to enter the trade either by a market order or alternatively by a limit order placed right at the halfway point of that specific candle." | N (Q4/Q5 touch stop and speed only) | extract (choice rule) + re-code (market branch) |
| V6 | E | NEW | Tool ranking never captured: footprint "A tier", MACD "F tier" (lagging). Footprint is in 33 videos; no tool-priority rule exists in our docs. | 3JZH06L28us: "MACD. >> F tier. It's lagging." / "Footprint chart. A tier. It's really reliable." | N | extract (low value, but cheap) |
| V7 | C | 1 (unstated count) | "major market participants" (19 videos) is the causal frame for levels ("this is where the major market participants were"). It is not coded; we treat levels as numbers only. | BB3c8visnkI: "this is where the major market participants were"; C9n_d91Uitc: "there's a high probability we'll return to equilibrium because major market participants always want equilibrium." | N | re-frame (context label, not signal) |
| V8 | T | 5 (transfer assumed) | "dax future" (18 videos) is his index and his ATR examples. Those numbers (e.g. a 180-point average move after the open) do not carry to 24/7 BTC. | UOBgXV20yCM: "the average move of the DAX future, for example, after the market opening is initially 180 points based on the ATR." | Y (Q14 partial) | label as transfer, no BTC number |
| V9 | T | 4 (session read) | "market opening" (23 videos): the open type sets the day's read. Iteration 1 covered session windows (Q7) but not the open-type read. | 43JaKHRvxHk: "how is the market opening formed? The open. And if the open tells me the market is going to be very trendy today" | Partly (Q7 windows only) | extract (open-type rule) |
| V10 | E | 2 (named, not coded) | "cumulative volume delta" (5 videos, 1 hit in the rulebook) is the pressure read he uses against price. | 0jM5Y31YJak: "the power of the cumulative volume delta and the concept of the volume spread analysis" | N | extract, low priority |
| V11 | E | NEW (shape words) | Profile shape vocabulary is uncoded: "double distribution" (-dMWA_bbm3o, "what's called a double distribution here"), "selling tail", "b profile", "p profile", "trend profile", "balance profile" (5 to 8 videos each, 0 to 1 hits). | -dMWA_bbm3o: "what's called a double distribution here. And what information does this double distribution give me?" | N | extract (shape list) before coding |

## Top 60 trader terms: in >=5 Tom/Fabio videos, <=1 hit in the brief corpus

Class key: CONCEPT, TA, TAPE, SESSION, PROFILE, TF-chart, ENTRY, SIZING, STYLE and similar are a rough label. "name" = concept present under another word in our docs. Dropped on purpose: generic English ("current market", "specific price", "many traders"), brand or sponsor text ("World Class Edge", "trading world"), and near-duplicates (kept the best-counted one).

| # | term | videos | occurrences | corpus hits | class |
|---|---|---|---|---|---|
| 1 | footprint chart | 33 | 57 | 0 | CONCEPT (name; "footprint" 38 hits) |
| 2 | counter trading | 30 | 62 | 1 | CONCEPT |
| 3 | trend following | 26 | 46 | 1 | CONCEPT |
| 4 | minute chart | 25 | 51 | 0 | TF-chart |
| 5 | breakouts | 25 | 42 | 1 | CONCEPT |
| 6 | market profile | 23 | 71 | 0 | CONCEPT (name; "volume profile" 17 hits) |
| 7 | market opening | 23 | 48 | 1 | SESSION |
| 8 | market phases | 22 | 51 | 1 | CONCEPT |
| 9 | market makers | 21 | 29 | 0 | CONCEPT (sponsor copy in 13 files) |
| 10 | institutional traders | 21 | 22 | 0 | CONCEPT (sponsor copy) |
| 11 | major market participants | 19 | 23 | 1 | CONCEPT |
| 12 | dax future | 18 | 34 | 1 | TRANSFER |
| 13 | distribution | 15 | 42 | 1 | CONCEPT (profile shape) |
| 14 | hedging | 15 | 42 | 0 | CONCEPT |
| 15 | aggressive buyers | 15 | 31 | 1 | TAPE |
| 16 | scale | 15 | 24 | 0 | MGMT (scale in/out; "smaller scale" is noise) |
| 17 | market environment | 13 | 15 | 0 | CONTEXT |
| 18 | capital flows | 8 | 8 | 0 | CONCEPT |
| 19 | resistance levels | 11 | 18 | 0 | TA |
| 20 | trend reversal | 11 | 18 | 0 | CONCEPT |
| 21 | corresponding volume profile | 11 | 13 | 0 | PROFILE (period) |
| 22 | candlestick chart | 10 | 24 | 0 | CHART |
| 23 | daily chart | 10 | 20 | 0 | TF-chart |
| 24 | york session (new york session) | 10 | 19 | 1 | SESSION |
| 25 | volume weighted | 10 | 16 | 1 | TA (VWAP name) |
| 26 | trading session | 10 | 12 | 0 | SESSION |
| 27 | trading setup | 10 | 12 | 0 | CONCEPT |
| 28 | aggressive buying | 10 | 11 | 0 | TAPE |
| 29 | market order | 9 | 27 | 0 | ENTRY (order type, V5) |
| 30 | london session | 9 | 17 | 0 | SESSION |
| 31 | average risk reward | 5 | 6 | 0 | SIZING |
| 32 | volume area | 9 | 14 | 0 | PROFILE (naming, V2) |
| 33 | intraday swing | 9 | 13 | 0 | STYLE |
| 34 | volume profiles | 9 | 12 | 0 | PROFILE (name) |
| 35 | pullbacks | 9 | 12 | 1 | CONCEPT |
| 36 | market structure | 9 | 10 | 0 | CONTEXT |
| 37 | swing trader | 9 | 9 | 0 | STYLE |
| 38 | hedge fund | 8 | 43 | 0 | CONTEXT |
| 39 | cluster | 8 | 23 | 1 | FOOTPRINT |
| 40 | inside bar | 8 | 13 | 0 | PATTERN |
| 41 | price discovery | 8 | 12 | 1 | AUCTION |
| 42 | balance area | 8 | 11 | 0 | PROFILE |
| 43 | live session | 8 | 10 | 0 | SESSION |
| 44 | trend structure | 8 | 10 | 1 | CONTEXT |
| 45 | moving sideways | 8 | 9 | 0 | BALANCE |
| 46 | finds acceptance | 8 | 8 | 0 | ACCEPTANCE |
| 47 | trailing | 7 | 13 | 1 | STOP (management) |
| 48 | selling pressure | 7 | 11 | 1 | TAPE |
| 49 | price zones | 7 | 10 | 0 | LEVELS |
| 50 | trader dna | 7 | 10 | 0 | TOM-PROFILE (9eHZMVXilgc: "we use what's called the trader DNA") |
| 51 | trade entry | 7 | 9 | 1 | ENTRY |
| 52 | trading hours | 7 | 9 | 1 | SESSION |
| 53 | counter setup | 7 | 8 | 0 | CONCEPT (V3) |
| 54 | positive expected value | 7 | 8 | 0 | EV |
| 55 | horizontal level | 6 | 29 | 0 | LEVELS |
| 56 | trend profile | 6 | 13 | 0 | PROFILE (V11) |
| 57 | opening phase | 6 | 9 | 0 | SESSION |
| 58 | selling tail | 6 | 8 | 0 | PROFILE (V11) |
| 59 | cumulative volume delta | 5 | 14 | 1 | CVD (V10) |
| 60 | balance profile | 5 | 12 | 0 | PROFILE (V11) |

Also in the candidate list, not in the top 60: "b profile" and "p profile" (5 videos each; "p profile" 1 hit, "b profile" 0), "double distribution", and "world class edge" (sponsor, 13 videos, dropped).

## Top 15: two exact quotes each

All quotes are exact transcript substrings (script check: 36 of 36). Timestamps in the text are kept as the caption has them.

1. **footprint chart** (33): "Here we have a footprint chart. I've set it to 5 minutes now." [3JqMyzE8jIQ]; "I'm simply analyzing the trading volumes using a footprint chart within the same time frame that I'm currently using as a basis here." [2xnNPIyHGQ4]
2. **counter trading** (30): "Are you someone who prefers to buy at the bottom, meaning you do counter trading, or are you someone who trades following the trend?" [3o1VVsfBmmU]; "counter trading is called for here." [-dMWA_bbm3o]
3. **trend following** (26): "my trend following strategy don't perform really good in consolidation market." [0KyIEdvVKMQ]; "Are you more of a counter trader? Are you more of a trend following trader?" [3o1VVsfBmmU]
4. **minute chart** (25): "then take a 1-minute chart and compare whether the movement you saw in the book roughly matches what you see on the chart." [3oqxklw9zuU]; "Personally, I like to use the 5-minute chart." [4P5WAxyPCis]
5. **breakouts** (25): "Trust me, a lot of people think they can trade breakouts, counter trades in every phase of the markets. Forget it." [15JoLK0PbMU]; "Many traders look for setups within ranges to trade quick breakouts because they only know the setup." [4VXpUjhKG2U]
6. **market profile** (23): "The combination of market profile and volume profile." [3o1VVsfBmmU]; "I look at the value area high, the value area low, the overall market profile, and the point of control or POC." [5Ljfwvtktek]
7. **market opening** (23): "how is the market opening formed? The open." [43JaKHRvxHk]; "today during the market opening phase, it was such that the market told me" [9VN9y2DVtGQ]
8. **market phases** (22): "how to classify market phases (bullish, bearish or balance)" [HySZZSjMxF8]; "this only works in 30% of market phases where we are truly trend stable." [Fj4FDZQxw0I]
9. **market makers** (21): "Search for liquidity [1:01] that market makers will come to hunt [1:04] your stop loss." [FawPrRUGNpk]; "Market makers, they offer." [_xEhztnK2g0]
10. **institutional traders** (21): "many institutional traders look at the VWAP." [43JaKHRvxHk]; "I'll share three great insights that institutional traders have used for decades and still use today." [Sy-x5AQ9-Pk]
11. **major market participants** (19): "this is where the major market participants were" [BB3c8visnkI]; "there's a high probability we'll return to equilibrium because major market participants always want equilibrium." [C9n_d91Uitc]
12. **dax future** (18): "If, for example, a large gap occurs in the DAX future now, especially over the weekend" [96iPFDpXEcU]; "the average move of the DAX future, for example, after the market opening is initially 180 points based on the ATR." [UOBgXV20yCM]
13. **distribution** (15): "what's called a double distribution here. And what information does this double distribution give me?" [-dMWA_bbm3o]; "This in this specific case this is a distribution." [0jM5Y31YJak]
14. **hedging** (15): "They do hedging, so they scalp in order to hedge options positions." [4P5WAxyPCis]; "market participants simply have to engage in hedging very aggressively." [96iPFDpXEcU]
15. **aggressive buyers** (15): "there are aggressive buyers." [4MoNjEQ2Dd8]; "We know aggressive buyers." [0CrkbfuIhkc]

## Top 5 gaps and the single biggest hole

1. V1: market profile (time-based) is absent from docs and code. It is his main level source in 23 videos, and he uses it with volume profile.
2. V3: counter-trade, breakout and trend-follow are chosen by market phase. We run one entry per model, with no phase-to-setup switch.
3. V4: the execution chart. He sets levels on a higher timeframe and times entries on a 1-min or 5-min footprint, chosen by trade length. Our models fix one bar size each.
4. V5: entry order type. He uses a market order or a half-candle limit, and the choice rule is not stated. Our models have a rest limit only.
5. V2: "volume area" means a low-volume gap, not the value area. Our naming merges the two.

**Single biggest hole: the level map.** Tom's levels come from market profile (time-based) plus volume profile, read on a higher timeframe. Our docs and code have only volume profile, so the levels that drive the trade are not what he uses. This is the C-stage version of the iteration-1 finding that concepts were framed wrong.
