# Habib concept book (2026-11-07)

**Result: Habib's "imbalance" is a volume-anomaly candle (per exchange, per timeframe) used as a location marker inside a three-part setup: a pre-planned level, an imbalance candle at it, and a wick rejection. His threshold and indicator formula are not public, so ours is a stand-in. This book is concepts only: no backtest, no trade advice, testnet only.**

Method (operator, 2026-11-06, `MyTradingSys/system/OPERATOR_DECISIONS.md:1812`): understand the concept first, then see how it shows up in his calls; no backtest first. Habib is the analyst; Qriptal is the channel.

## 0. Labels used in this book

| Tag | Meaning |
|---|---|
| SOURCED `file:line` | quoted or read from that file line (paths below are relative to `MyTradingSys/research/` unless they start with `extracts/`) |
| VERIFIED | the quote was checked by me against the raw caption file in `extracts/_staged_2026-09-27/raw/` this session (line given) |
| UNVERIFIED | the quote comes from an extract whose caption file is not in the repo; Gemini caption-check card `gemini-habib-caption-check-1107` filed (done when each quote is VERIFIED or UNVERIFIED against captions) |
| OURS | a number or reading we chose; never call it his |

Known weakness of the sources: captions are YouTube auto-captions (words and numbers can be wrong, `imbalance_qriptal_2026-10-16/discord/transcripts/INDEX.md:7`); the Discord table was read from screenshots (`.../discord/habib_trading_thoughts.md:1-10`).

Short names used: `RULES` = `gemini_burn_2026-10-24/habib_yt_rules.md`; `README16` = `imbalance_qriptal_2026-10-16/README.md`; `DISC` = `imbalance_qriptal_2026-10-16/discord/habib_trading_thoughts.md`; `LEVELS` = `gemini_burn_2026-10-31/HABIB_LATEST_LEVELS.md`; `RAW:<id>` = `extracts/_staged_2026-09-27/raw/qriptal_<id>_raw.txt`.

---

## 1. How Habib trades imbalances

### 1.1 Concept map (the IDs C1-C12 are used in `CALLS_VS_BOOK.md`)

| ID | Concept | One line |
|---|---|---|
| C1 | Imbalance candle | a candle whose volume is anomalous for its timeframe, read per exchange |
| C2 | Small body + wick | volume came in, price failed to move: trapped traders, fade candidate |
| C3 | Large body | volume and price moved together: strength, never fade (a veto) |
| C4 | Wickless imbalance | an unfilled magnet and support/resistance until recovered |
| C5 | Imbalance open / midpoint as level | the level to trade is the candle's open, or its 50 % midpoint after an instant retest |
| C6 | Multi-timeframe, multi-exchange stack | 30m/1h/4h/12h/1d imbalances on Binance, Bybit and Coinbase checked separately |
| C7 | Three-part setup | pre-planned level + imbalance + wick reaction |
| C8 | Liquidity sweep first | equal highs/lows, round numbers, Monday high, "scam wicks" must be swept before a reversal is acceptable |
| C9 | Weekly / monthly clock | weekly open, Monday trap, month-start wick, Sunday plan with two branches |
| C10 | Range value levels | range POC, value-area high/low, daily/weekly/monthly/quarterly pivots, previous-day and Friday highs and lows |
| C11 | Execution and risk | hard structure stop, break-even after TP1, leverage inverse to stop width, front-run risk |
| C12 | Breakout validation | a real breakout holds the open of its imbalance candle on retest; losing it makes it a fakeout |

### 1.2 Definition and formula (C1): what is known and what is not

| Question | Answer | Source |
|---|---|---|
| What does it measure? | volume, "an indicator that measures volume" | README16:32 (cites `RAW:ZPFK3ZsLwoo` about lines 560-600; the exact phrase was not found by grep in that file: UNVERIFIED wording; the sense is VERIFIED at RAW:ZPFK3ZsLwoo:567-577) |
| Is it per timeframe? | yes: 30m, 1h, 4h, 12h, daily; higher timeframes weigh more | README16:36; RULES:57 (one plan stacked 12h, 4h and 1h imbalances; UNVERIFIED) |
| Per exchange? | yes, separately: Binance, Bybit, Coinbase | README16:35 (VERIFIED "two hourly imbalances" at RAW:AsAI5mglRSw:135); RULES:402-405 (UNVERIFIED) |
| How does it look on a chart? | the candle is coloured purple on TradingView | RULES:231 (UNVERIFIED) |
| Formula, lookback, threshold | **not public**: closed TradingView indicator sold via a login portal | RULES:407-411; README16:39 |
| Our stand-in (OURS) | relative volume = volume / median of the prior 50 bars of the same timeframe; flag at k = 2.0 (1.5 and 3.0 as sensitivity) | `imbalance_qriptal_2026-10-16/imb.py:168-172`; `habib_concept_book_2026-11/habib_common.py` |
| Does the stand-in match him? | partly: it picks his labelled candles more often than chance (k = 3: 12 hits vs 8.0 chance, lift 1.50) but misses many of his 12h/daily ones; his higher-timeframe imbalances look like milder volume spikes than his intraday ones | README16:49-58 |

Reading: the family (volume anomaly) is right, the number is unknown. Any "imbalance candle" we list is a candidate, never "his" candle (README16:64 calls a detector claiming to be his indicator REJECT tier).

### 1.3 Body reading (C2, C3)

- Small body on high volume: "volume anomalies but you have very small bodies. That means that volume came in but price ... failed to move"; "99% of the time ... price comes back down to take out that liquidity". VERIFIED RAW:ZPFK3ZsLwoo:577-596. Cited by README16:33.
- Large body on high volume: "this is not an imbalance to pay attention to for a short because it has a very large body", and "a lot of volume ... price is moving along with the volume. So this is a big sign of strength". VERIFIED RAW:ZPFK3ZsLwoo:567-577 (see also README16:34).
- Our test of the claim: fading a high-volume large-body candle lost 0.10-0.42 R gross on every timeframe (the net numbers are not meaningful, README16:103), so "do not fade a large body" is the one rule of his that held in our data. SOURCED README16:83.
- Wick quality: "ugly" wicks are wide and erratic and leave liquidity behind; a small body with a clean wick allows a tight stop. UNVERIFIED RULES:421-424 (quotes at 421-423). No mathematical rule exists; ours (OURS): wick side of at least 40 % of range = a usable rejection, at most 5 % = wickless.

### 1.4 The three-part setup (C7)

His summary: "Have your levels ready. If you have your volume and your reaction, you take the short ... Monitor the volume and the reaction. And that's all you need to do." UNVERIFIED RULES:161 (video PrHoIQ-YWX0, 18:26), echoed RULES:163. In his own words on a stream: "I look for a good resistance or support. I look for imbalances, and I look for a good reaction" VERIFIED RAW:wveE-r1mzTc:108-120 (cited README16:38); "my strategy requires a wick" VERIFIED RAW:u0T-jOoesfc:41.

Discord version, as a four-item check he posts before a trade: "Volume is good / Timing good / Level good / Reaction good so I think it's worth the trade" (DISC:59); skips are phrased the same way: "no reaction no trade", "would like a bit more volume ... skipping this long" (DISC:105, 21).

| Pillar | What it is | Source |
|---|---|---|
| 1. Level | planned in advance (weekend plan): open or midpoint of an HTF imbalance, order block, double top/bottom, range POC / value-area edge, weekly or monthly open | RULES:32-35,311-322 (UNVERIFIED) |
| 2. Imbalance | anomalous-volume candle (30m/1h at the level, 4h/12h/1d as the level itself) | README16:36; RULES:329-331 |
| 3. Reaction | a wick away from the level; he does not trade a level blind: "if you don't get a reaction ... I don't have a problem at all" (UNVERIFIED RULES:92) | RULES:96 |

His own confession that the plan needs the reaction: "risk is inherently higher because this trade isn't pre-planned" (DISC:84).

### 1.5 Level types he names (C4, C5, C8, C9, C10, C12)

| Level type | How he uses it | Source |
|---|---|---|
| Open of an imbalance candle (4h/12h/daily/1h) | the level to trade ("you take the open") | RULES:62,175,180 (UNVERIFIED) |
| Midpoint (H+L)/2 of an imbalance with an instant retest | "as usual, you take the midpoint" | RULES:142,146 (UNVERIFIED) |
| Wickless imbalance | magnet to be filled, and support/resistance | RULES:127,159,176 (UNVERIFIED) |
| Partially filled imbalance | stays a magnet until fully filled | RULES:164 (UNVERIFIED) |
| Order block, double top / triple bottom | confluence and a liquidity target | RULES:131,165 (UNVERIFIED); DISC:63 |
| Sweep of a round number or equal highs | entry on the sweep ("a sweep of 82") | RULES:113 (UNVERIFIED); DISC:49 ("82k breach + good volume + good reaction") |
| Monday high, month-start wick | Monday open sweeps weekend stops, then reverses; the monthly candle prints its wick early | RULES:130,181 (UNVERIFIED) |
| Weekly open | "84.4 ... this is the weekly open" short zone | LEVELS:40 |
| Daily open (dOpen) | support/resistance and a reclaim test | DISC:86,108 |
| Monthly and quarterly pivots | targets and sweep levels: "range low and monthly pivot taken out", quarterly pivot 78,000 | DISC:41; LEVELS:13,16,36,37 |
| Binance "scam wick" | an aberrant Binance-only wick that tends to be recovered; he will not short below one | RULES:214 (UNVERIFIED); DISC:23 |
| Breakout hold | a breakout must hold the open of its imbalance candle; losing it targets the origin of the range | RULES:265-266 (UNVERIFIED) |

### 1.6 Entry, stop, leverage, management (C11)

| Habit | Evidence | Source |
|---|---|---|
| Waits for a reaction, but also places limits at pre-planned levels and gets "frontrun" often | limits at 80,050 with SL 80,550; "frontrun" appears in 13 lines of the table | DISC:44,38,43,46,58,78,85 |
| He knows the front-run problem and chooses not to front-run his own level | "could you go for orders front running my level? ... I don't think we front on it" | VERIFIED RAW:ZPFK3ZsLwoo:1087-1101 |
| Stop on structure, not on a percentage of margin | stop distances on the Bitunix cards 0.08 % to 1.43 % of price; "-50 %" on a card is a structure stop at 75x | `imbalance_qriptal_2026-10-16/discord/README.md:15` |
| 50x leverage and the "50 % stop" | the card leverages seen are 30x, 35x, 50x, 75x (DISC:114). The -51 % card is at 75x for a 0.58 % price move (DISC:16: entry 81,944.4, close 81,472.8; OURS arithmetic). The 50x cards lose 9-38 % of margin (DISC:58,62,64,70), a stop of 0.08-0.65 % in price. A 50 % margin loss at 50x equals about a 1 % price move (OURS arithmetic; fees on the card are about 0.1 % x leverage). No 50x card shows a -50 % loss: it is the operator's reading, not seen as his rule | DISC:16,58,62,64,70,114 |
| Leverage scales inversely with stop width | "25x ... if I can pinpoint a more accurate entry, a higher leverage ... if not confident ... a wider stop with lower leverage"; "a 5x long since the stop will be a bit wider"; a stop of 1 % on a clean small-body wick | RULES:143,210-211 (UNVERIFIED) |
| Swing longs use low leverage | "4-10x leverage long ... holding it until new ATH"; "long around 73K with 30x" | DISC:103-104; VERIFIED RAW:ZPFK3ZsLwoo:1283-1284 |
| Break-even after the first move | TP1 then stop to entry; "no TP1" on high-conviction runners | RULES:97,282,389 (UNVERIFIED); DISC:25-27 |
| Adds only in profit, with the stop at entry | "added a bit to my short today while SL remains at entry"; "2 nice adds" on a long | DISC:74; `habib_plan_imbalance_2026-10-20/README.md:15` |
| After a loss he reduces risk, he does not double | "because i took that 1st loss i wanted to reduce risk"; "if i get stopped again im done for the day" | DISC:68,70-71 |
| Losses are posted | 14 cards: 4 wins, 10 losses; he says "great read ... mediocre execution" | DISC:96,113 |

So the "martingale in a range" idea is not his habit in the sources read: he re-tries once after a stop with lower risk and a daily cap, and adds only when the trade is already in profit (see `LADDER_PROPOSAL.md`).

### 1.7 Previous-day range and point of control (C10)

| Item | Finding | Source |
|---|---|---|
| Previous-day / Friday / daily highs and lows | used as stop and sweep levels: "moved my SL to yesterday's low at 76.2", "SL at daily high", "setup remains a sweep of Friday's high" | DISC:53,61,40 |
| Point of control | named as a level and as the center of a range: "support below us was the point of control"; "fixed range point of control has moved up ... if we lose this level I would expect again a drop to the low"; the best-conviction stack includes a 12h and daily wickless imbalance, a 3-day imbalance midpoint "and the cherry on top ... the volume profile" | RULES:292,295,144 (UNVERIFIED) |
| Value-area highs | a 4h imbalance plus "two value area highs" = major resistance | RULES:212 (UNVERIFIED) |
| **Previous-day POC specifically** | **not found in the sources read**: his POC is a range or fixed-range POC, not named as the previous day's. Previous-day POC is the operator's framing and a clean way to test the idea: the live-aid already computes it (`MyTradingSys/tools/live_aid/tf_strip.js:61-81,95-105`: 1m typical price in 50 USD bins, 70 % value area) | this search |

### 1.8 What we do not know (open, needs captions or his own words)

| Gap | Action |
|---|---|
| Indicator formula and threshold | closed product; not recoverable; label OURS |
| Which exchange wins when Bybit and Binance disagree | needs captions: RULES:405 cites `yHFg7oVN3ts` (UNVERIFIED) |
| 15 of the videos behind RULES have no caption file in the repo | Gemini card `gemini-habib-caption-check-1107` |
| Plans before 2026-05-28 and Discord before that date | unread (DISC:7) |

---

## 2. How the wider trading world defines and trades "imbalance"

All sources are practitioner pages, vendor docs or papers; none gives a fee-net crypto track record (README16:41; the search done 2026-11-07 found none either). Quote marks are paraphrase unless stated.

| Construct | Definition | Where used | Source | Habib: match or differ |
|---|---|---|---|---|
| Fair value gap (FVG, ICT/SMC) | three candles; candle 1 high below candle 3 low (bullish) leaves a gap; many tools add a minimum size because raw gaps print constantly | ICT / smart-money traders, most TradingView "imbalance" scripts | [LuxAlgo: Fair Value Gap](https://www.luxalgo.com/library/concept/fair-value-gap/) | differs: price geometry only, no volume. His word "imbalance" is volume. The 10-20 note lists it as hypothesis H-FVG (`habib_plan_imbalance_2026-10-20/README.md:34`) |
| Volume imbalance (ICT) | two adjacent candles whose bodies do not overlap while wicks do; some indicators also require volume expansion | ICT | [The Right Trader](https://therighttrader.com/learn/smart-money-concepts/volume-imbalance), [LuxAlgo: Volume Imbalance](https://www.luxalgo.com/library/concept/volume-imbalance.md) | partly: his "wickless imbalance" behaves like a gap magnet, but he defines the candle by volume, not by a body gap |
| Single prints / excess (Market Profile) | one-letter tail at a session extreme = decisive rejection (excess); flat extremes with 2+ prints are "poor" and likely revisited; single prints inside a profile come from fast initiative moves | auction-market traders (Steidlmayer, Dalton) | [LuxAlgo: Single Prints](https://www.luxalgo.com/library/concept/single-prints.md), [LuxAlgo: Poor High/Low](https://www.luxalgo.com/library/concept/poor-high-poor-low/), [NexusFi](https://nexusfi.com/a/market-structure/single-prints-poor-highs-poor-lows-market-profile) | partly: his "wickless = magnet to be filled" and "ugly wick = unfinished" read like poor extremes and repair of single prints; he uses POC and value areas too. Different data (TPO vs candles) |
| Balance vs imbalance (auction) | balance: price rotates inside accepted value; imbalance: value area migrates and one side dominates | Market Profile | [LuxAlgo: Balance vs Imbalance](https://www.luxalgo.com/library/concept/balance-vs-imbalance/) | differs in meaning: for Habib an imbalance is one candle, for auction theory a market state. This is the fork between his "range phase" and "trend phase" |
| Footprint diagonal imbalance | ask volume at a price compared with bid volume one tick below; 3:1 (300 %) is the common default, some use 150-200 %; tools suggest a minimum absolute volume per cell | order-flow traders | [Quantower](https://www.quantower.com/blog/imbalance-footprint-chart-and-rithmic-plugin), [LuxAlgo: Bid/Ask Imbalance](https://www.luxalgo.com/library/concept/bid-ask-imbalance.md) | differs: needs trade-level data; he works from candle volume per exchange |
| Stacked imbalances | three or more same-side footprint imbalances in consecutive rows; treated as a zone until price trades back in | order-flow traders | [Quantower](https://www.quantower.com/blog/imbalance-footprint-chart-and-rithmic-plugin) | differs: closest cousin is his "multiple imbalances at 82.8k" (DISC:25) but built from candles |
| Delta / taker imbalance | (taker buy - taker sell) / volume of a bar | klines-based studies | our own past tests P4, T093, C3: no replication (README16:9-12) | differs: not his candle; "nobody had defined his candle until now" (README16:18) |
| Order-flow imbalance (OFI) | net change of bid and ask size at the best quotes; price change over short intervals is roughly linear in OFI with slope inversely proportional to depth | microstructure research | [Cont, Kukanov, Stoikov (arXiv 1011.6402)](https://arxiv.org/abs/1011.6402) | differs in horizon: seconds to minutes and smaller than retail fees (`imbalance_2026-10-10/RESEARCH.md` per README16:12); he trades hours to days |
| Volume spread analysis (VSA, Wyckoff lineage) | high volume with a narrow spread is effort without result, read as absorption; direction needs context | VSA / Wyckoff traders | [TradingView VSA library](https://th.tradingview.com/script/HXOgXfMr-ml-vsa/) | **closest match**: his small-body anomaly = "effort without result"; his large body = "effort with result". README16:41 reached the same conclusion |

Where Habib matches the world: location-first thinking (levels, value areas, magnets that get revisited), absorption reading of high-volume narrow candles, wick/rejection as confirmation. Where he differs: he defines the candle by per-exchange volume rather than by a price gap, uses higher timeframes as the level and lower ones as the trigger, and checks three venues. What the world also tells us: the generic FVG-fill statistics come from vendors and are not fee-net (README16:41), and orderflow sources warn that an imbalance pressed into a larger opposing level is routinely absorbed (Quantower page above).

---

## 3. How to read a Habib call (one-page checklist)

Use on any plan or trade post. Answer in order; a "no" at 1-3 means "not a Habib setup", record it and move on.

| # | Question | If yes | If no / unknown |
|---|---|---|---|
| 1 | Is the level named and priced before the move? (Sunday plan or earlier post) | note the post time and price; candidate for scoring | "not pre-planned" (his own risk flag, DISC:84): do not score as a plan |
| 2 | What kind of level is it? (C5 imbalance open/mid, C8 sweep of equal highs or round number, C9 weekly/Monday, C10 POC/value area/daily-weekly-monthly pivot, C12 breakout hold) | write the type and its timeframe | say "type not stated" |
| 3 | Is there an imbalance candle at the level? (our list: relative volume >= 2.0 vs 50-bar median, `habib_watch.py`) | classify body: small + wick = C2 fade candidate; large = C3 do not fade; wickless = C4 magnet | "no imbalance yet": he waits (DISC:105) |
| 4 | Did the candle on the trigger timeframe (30m/1h) show a wick away from the level? | pillar 3 met | not met: his own rule says no trade (RAW:u0T-jOoesfc:41) |
| 5 | Which exchanges show it? (Binance first; Bybit, Coinbase) | stack = stronger (C6) | single venue: weaker; Binance-only wick may be a "scam wick" that gets recovered |
| 6 | Did a liquidity sweep come first? (equal highs/lows, Monday high, round number) | sweep done = acceptable; stop sits beyond it | "no sweep, no long/short" (UNVERIFIED RULES:93,350-354) |
| 7 | Where is the stop and how wide in percent? | width in price % x leverage = loss in % of margin (50x: 1 % = 50 %) | no stop stated = unscoreable as a trade, scoreable as a plan |
| 8 | Is there a hedge, break-even or add-in-profit rule? | note: his adds are in profit (DISC:74) | none |
| 9 | Plan phase: range (fade extremes, C2) or trend (join retest of the imbalance open, C3/C12)? | pick the matching read | mixed: wait |
| 10 | Score the plan, not the execution: did price reach entry, then target? (`plan_score.py`, `CALLS_VS_BOOK.md`) | log full / partial / miss | NO_DATA is never a miss |

---

## 4. Wired to his calls

The 9 priced plans are scored in `CALLS_VS_BOOK.md` (concept used, level type, imbalance candle where identifiable, outcome). The daily watch is `habib_watch.py`. The range-ladder question is `LADDER_PROPOSAL.md`.

## 5. Numbers: SOURCED vs OURS

| Number | Value | Label |
|---|---|---|
| Relative-volume threshold | 2.0 x median of prior 50 bars (1.5 and 3.0 sensitivity) | OURS; his number unknown |
| Small / large body | <= 30 % / >= 70 % of range | OURS (`imb.py`); his words "very small", "very large" are qualitative |
| Wickless | side wick <= 5 % of range | OURS |
| Rejection wick | >= 40 % of range on the reaction side | OURS |
| Level match tolerance | range +-0.4 %, open or midpoint +-0.25 % | OURS (`imb.py` TOL_RANGE, TOL_MID) |
| Fill window / open window | 24 h / 7 d | OURS, pre-reg draft `habib_plan_imbalance_2026-10-20/PRE_REG_HABIB_PLANS.md:31` |
| Value area | 70 % on 50 USD bins | OURS, inherited from the live-aid (`tf_strip.js:61`) |
| His leverage and stop distances | 30-75x; stops 0.08-1.43 % of price | SOURCED DISC:114; `discord/README.md:15` |
