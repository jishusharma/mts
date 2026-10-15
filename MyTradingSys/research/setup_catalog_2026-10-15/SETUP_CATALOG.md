# SETUP CATALOG: every trade setup Tom and Fabio describe, in plain chart terms (2026-10-15)

Status: consolidation of what the repo already holds. No new extraction, no test design, no fees, no stop-size math, no
backtest, no VALIDATION/HOLDOUT read. Operator decision 2026-10-15: identify all bare setups first (what the naked eye sees on a
BTC chart and how the trader applies it) before any further test design. This file is the base for: filling gaps from unread
transcripts, blind eye-read marking on BTC charts by two readers, then stops/fees/code. Fable 5.1 audits it against raw
transcripts on 2026-10-20.

How to read the quotes
- Block quotes `> "..."` + `**Source GPS: <id> | BEGIN/MIDDLE/END**` are checked against `raw_transcripts_canonical/<id>_raw.txt` by `python scripts/dev/verify_extract_quotes.py` (verbatim after case/punctuation normalising, position third).
- Inline quotes `"..." (<id>:<a>-<b>)` cite caption lines of `F:/MTS/data/tom_videos/<id>.txt` and are checked by `python scripts/dev/check_spec_quotes.py`. All of them are copied from TOM_LAYER_V2_SPEC.md (already checked there).
- `(paraphrase)` or `(ledger, frame)` = not a verbatim quote; a frame value read from a video by an earlier session.
- Captions are AI-translated (Tom) or auto-captions (Fabio): a quote proves what the trader says he looks at, never a price, date or time.
- NOT STATED = the trader gives nothing in words (often he points at the chart: "here", "up here"). Nothing is filled in.
- OURS = a number or rule an earlier spec or engine added (judgement or tuned). Listed per setup, never presented as his.

Source keys: V2 = research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md; STR = conditions/setup_type_rules.md; GAP =
conditions/gap_rules.md; TOB = research/tom_btc_2026-10-13/TOM_ON_BTC.md; ANG = research/fast_track_2026-09-27/ANGLE_TRADE_CATALOG.md
(rows R1-R39); TL = research/tom_transfer_2026-10-11/TOM_TRADE_LEDGER.md + .csv (groups T1-T12); FTM = FABIO_TRADE_MODEL.md;
V3 = FABIO_V3_SPEC.md; FR = FABIO_RULEBOOK.md; LBL = FABIO_LINE_BY_LINE_fZlNGWvd2Ko.md; FL = research/fabio_transfer/FABIO_TRADE_LEDGER.md
+ .csv (rows F1-F14).

BTC visibility key (Binance BTCUSDT data we hold): klines 1m (OHLC, volume, taker-buy volume); aggTrades tape (delta, CVD,
footprint by price, large prints; one aggTrades row is not one order); volume profile / value area / POC / VWAP computed from
those. NOT held: order book history (only live, and bookDepth bands from 2023 as a proxy, TOB s2.3), news, retail sentiment
(Binance long/short ratios exist from 2020-09 per TOB, not on disk), other markets' bars (ES/NQ not on disk; ETH yes). BTC has no
cash open, no pre-market, no closing auction and no session gaps (CME BTC now trades 24/7, operator 2026-10-11, GAP header).
A day or session boundary on BTC (UTC day, a chosen "open") is OURS; where a setup needs only a day boundary it is marked YES.

## 0. Summary

| id | setup (his name where he has one) | trader | what you see on the chart (one line) | stop stated in words | BTC visible | real trades |
|---|---|---|---|---|---|---|
| TOM-1 | Counter trade at the top of an unhealthy push ("no liquidity left"; imbalance fade) | Tom | a fast push from the open far above prior value, thin profile at its top, the push stalls and sellers show, short back to the volume below | Y | PARTIAL | 16 (10 ledger groups + T8 candidate + 5 ANG rows) |
| TOM-2 | Counter trade in balance ("short trades up here and long trades down here") | Tom | sideways market, sell the top and buy the bottom of the balance, b-profile / lower balance as the proof | Y | YES | 0 (1 plan, ANG R24) |
| TOM-3 | Limit sell below the last volume step | Tom | trend flattening into a range, an inside day at the high, a resting sell order just below the last volume step of the profile | N | YES | 1 (ANG R13) |
| TOM-4 | Trend continuation pullback | Tom | healthy trend with volume behind it, price pulls back to VWAP or a fair zone, buy with the trend, target the next high-volume area | N | YES | 0 |
| TOM-5 | Pullback long into value after a buying tail | Tom | yesterday's profile has a buying tail, price came back into value and pulls back to the POC, buyers aggressive, long to value high / the ledge above | Y | YES | 3 (ANG R6, R7, R17) |
| TOM-6 | Breakout / break-in | Tom | a balance or overlap zone resolves, a ledge above old highs, speed picks up and buying shows, enter or add at the break | N | YES | 0 (adds inside TOM-5) |
| TOM-7 | Scalp in balance around VWAP | Tom | flat VWAP, no trend day from the open, shorts at the top and longs at the bottom of ranges around VWAP | N | YES | 0 |
| TOM-8 | Gap close (incl. Monday gap pullback long) | Tom | the open is far outside the prior day with no news, a failed extension, range, liquidity returns, trade back into the gap / prior value | N | NO | 1 (TL T4) |
| TOM-9 | Gap not closed: trade with the trend | Tom | the gap holds, prices are accepted (P shape), liquidity returns: trade in the gap direction | N | NO | 0 |
| TOM-10 | Closing-auction gap reversal | Tom | a very strong close with a closing-auction extreme, next day opens back in the red: contrarian | N | NO | 0 |
| FAB-1 | Balance with CVD pressure, break on volume ("sell model day") | Fabio | flat balance while CVD runs hard one way, first candle where price follows the volume out of balance with big trades | N | PARTIAL | 1 (FL F2) |
| FAB-2 | Absorbed push, rewarded effort ("punch to the wall") | Fabio | one side's aggression hits a wall (big delta, no price result), the other side's aggression moves price: trade with the side that gets the result | N | PARTIAL | 1 (FL F1) |
| FAB-3 | Failed auction of one side, then aggression of the other at the level | Fabio | consolidation where one side was absorbed, then the other side aggresses at that level with big trades: enter with the aggressor | N | PARTIAL | 2 (FL F3c, F5) |
| FAB-4 | Failed breakout back into balance | Fabio | a probe out of balance that fails and comes back inside: reversal | N | YES | 2 (FL F4a, F4b; assignment weak) |
| FAB-5 | Buyers protect a level (value-area low / gap / wall): long, squeeze trapped sellers | Fabio | price comes down to a level, buyers defend it (absorbed selling, protection wall), long with a tight stop, re-enter if it fails | N | PARTIAL | 11 (FL F3a, F3b, F6-F14) |
| FAB-6 | IVB: first 30 minutes of the US open | Fabio | the first 30 minutes' range sets the day's direction; trade the break of it | N | PARTIAL | 0 |
| FAB-7 | Heat-map liquidity: reload, protection wall, break and protect, book sweep | Fabio | resting order walls on the heat map get hit, absorb, reload; trade the reload or the break that is protected | N | NO | 0 (1 hypothetical, ANG R35) |
| FAB-8 | Volume-defined fair value gap rejection | Fabio | the lowest-volume price inside the value area of a swing; price rejects there | N | YES | 0 |

Counts: Tom 10 setups, 3 with a stop stated in words, BTC visible YES 6 / PARTIAL 1 / NO 3. Fabio 8 setups, 0 with an initial
stop stated in words (his management rules are stated; the initial stop is always "here" on the chart), BTC visible YES 2 /
PARTIAL 5 / NO 1. Real trades: Tom 21 assigned + 1 unassigned (ANG R20) + 2 anti-examples; Fabio 17 FL entry rows assigned (F1, F2,
F3a-c, F4a-b, F5, F6-F14; F15 never filled), 2 unassigned trade groups (ANG R31, R33).

## 1. Duplicate map (one setup, many file names)

| setup | names used in the files |
|---|---|
| TOM-1 | V2 family A "imbalance fade", entry paths A1/A2/A3, "re-entry" (management A-M5); TL `spike_fade`, `spike_fade_candidate`, `re-entry after stop`; STR s4 "Counter-Trade", variant 4.2B "Trend Extreme With Proof of Exhaustion"; ANG "counter trade at highs, no liquidity above", "B setup/B profile pullback after a failed push into no-liquidity highs", "P profile exhaustion short", "short-squeeze fade", "gap exaggeration close"; GAP G19-G22 "gap-fade trade (exaggeration)"; TOB s2.2 "session extreme of an oversized impulse leg"; engine `ct_short`, `SpikeFadeDetector` `fade_short` |
| TOM-2 | STR s3 matrix row "Balance / prior day VAH/VAL/VPOC -> Counter-Trade", s4.2A "Primary: Balance Market", 4.4A "B Profile = Weakness", 4.4D "Lower Balance After Rejection = PBD Logic"; ANG R24 (plan) |
| TOM-3 | ANG "limit sell below the last volume step (yRvM)", "smart S/R zone; inside day at ATH" |
| TOM-4 | STR s5 "Execution mode: Trend-Continuation"; TOB s2.5 "Trend continuation: pullback to a fair zone"; engine `tc_long` (VWAP) |
| TOM-5 | ANG "pullback to prior-day value/POC with buying tail for longs (4MoN, UOBg)", "buy at prior-day value area / VPOC zone" (crude R6), "re-entry on buyer stability" (R7). STR files the same 4MoN video under s6 breakout (ledge, speed) |
| TOM-6 | STR s6 "Breakout", "breakin or breakout"; TOB s2.5 "Breakout / break-in" |
| TOM-7 | STR s7 "Scalp"; TOB s2.5 "Scalp in balance"; engine `scalp_long`/`scalp_short` |
| TOM-8 | V2 family C "gap-close pullback long"; TL `gap pullback`, `breakout_pullback_teaching` (T9 = alias of T4); ANG R12 "gap + P profile + pullback buy signal"; GAP G05, G09, G14, G15 |
| TOM-9 | GAP G06 (accepted prices = P), G11, G16 |
| TOM-10 | GAP G23 |
| FAB-1 | FTM s1 "the trade (both videos teach the same one)"; V3 S1+S2+S5 and model A trigger; FR-10, FR-11; FL `balance_distribution_breakout_short`; ANG R26-R27 "CVD distribution + big trades + price follow-through", "continuation in redistribution phase; sell model day" |
| FAB-2 | FTM s1 step 3 "punch to the wall"; FR-16, FR-20, FR-22; FL F1 `balance_failed_auction_punch_to_wall`; ANG R28, R29; V3 S3 ABSORBED/CONTROL |
| FAB-3 | V3 model D "failed-auction breakout" (S5D); LBL T2 and M4; FR-19, FR-86, FR-88; FL `failed_auction_reentry...`, `failed_auction_short_rewarded_effort...`; ANG R32, R34 |
| FAB-4 | V3 model B "failed-breakout reclaim, mean reversion" (cites FR-19, FR-86); FL F4 (`hand-drawn schematic at t=780: balance -> failed breakout -> reversal`) |
| FAB-5 | FL `protection_wall_buy_reversal`, `value_area_low_reaction_long_scale_in`, `protection_level_squeeze_long`, `chase_long_after_squeeze`; FR-35, FR-63, FR-67, FR-68 |
| FAB-6 | V3 model C "IVB, first 30 minutes"; FR-81 "Opening range breakout has positive skew" |
| FAB-7 | FR-17, FR-31 to FR-73 (heat-map family, L2); ANG R35 |
| FAB-8 | FR-94, FR-95, FR-96 |
| OURS only | V3 model A "LVN pullback trend": its source is FBR:28-29 and V3 P35 says "not in these transcripts". It is not a Fabio setup until a quote is found (section 4) |

## 2. Shared frame (applies to every setup of the trader)

### 2.1 Tom: idea, proof, risk
"First, you have an idea. Second, you have proof that it's really time now to implement the idea. And third, you have a really clean risk management" (zQTbdEweG3c:28-32)

> "what is a setup? A setup is nothing more than a formation of price or volume or a footprint or whatever that gives me an advantage in keeping my risk smaller."
**Source GPS: NkQeOVDTAec | MIDDLE**

> "Whether it's trend or balance because I have to use different setups there and that is absolutely crucial."
**Source GPS: Ld1dhjGdTCA | END**

Tom management rules quoted in the trade videos (V2 s2.6; they were stated inside TOM-1 trades and are the only management
rules with a quote; whether they carry to his other setups is NOT STATED):
| id | rule | his words |
|---|---|---|
| A-M1 | add when sellers show again and the added risk is small | "I'm going to add another position here because the risk is extremely small for me right now" (n7ZSkjb7JXs:163-165) |
| A-M2 | no trailing at the start when R:R is about 6 | "Trailing the stop loss is something a lot of people like to do. In this case, I don't do that" (k0zm5NYn0IQ:194-196) |
| A-M3 | partial when momentum stalls at a level or before a low-volume area | "Whenever the last volumes before such a price range are not traded, caution is advised, which prompted me to first reduce my position" (ujedEcmvBMk:119-122) |
| A-M4 | stop to no-loss once a new balance has formed below | "it's time at the latest after a retrace to get out of the whole thing. Therefore, from now on, it's simply effective to definitely place the stop loss here" (k0zm5NYn0IQ:614-619) |
| A-M5 | re-entry after a stop only on a fresh signal with the idea intact | "Then you have the opportunity, if you get another signal, to play the whole thing again" (zQTbdEweG3c:168-170) |
| A-M6 | reduce risk into the cash open when the trade started pre-market | "the closer we get to the cash open where by the way I also want to reduce risk" (n7ZSkjb7JXs:193-196) |
| A-T5 | take profit at the predefined level, do not extend | "it's always important to simply use predefined price ranges where you take your profits" (ujedEcmvBMk:254-257) |

### 2.2 Fabio: management he states (all his setups; the initial stop is never described in words)
| rule | his words | where |
|---|---|---|
| stop to break-even once the market moves | see quote below (0jM5) | FR-12 |
| scratch plan: break-even fast if the level fails; the next absorption level becomes the pivot | see LBL quote below | LBL D09 |
| stop to zero when the OTHER side's push is absorbed | see LBL quote below | LBL D20, V3 E_opp |
| lower risk when his OWN side fails | see LBL quote below | LBL D14, V3 E_own |
| trail behind the last point of aggression / the level the other side protects | see 8CWK and LBL quotes below | FR-24, V3 S6/S9 |
| exit when big trades stop pushing / a new balance (redistribution) | see 0jM5 quote below | FR-15 |
| exit when the other side takes back control | see 8CWK quote below | FR-30 |
| exit on climax + failed auction | see LBL quote below | LBL D26 |
| adds: load and reload, risk only the day's profit; floor at day P&L 0 | see LBL quotes below | FR-05, LBL D05, D12 |
| day selection: needs volatility, not every day | see 8CWK quote below | V3 P40 |

> "So, the market exploded in my direction and I put my stop loss to break even. The first stop loss was here."
**Source GPS: 0jM5Y31YJak | MIDDLE**

> "I will be really fast in putting my position to break even if this level failed, okay? Because if this level failed, this one become the new pivot"
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "the market did a really good acceleration of the sell and stop before these aggressive buyers. Now my position is stop loss to zero. Why? Because we already saw that the sellers got stopped again in the movement and buyers are starting to continue up."
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "buyers failed again. So I want to lower my risk because if this big trade sell gets stopped out, I don't want to be in the position because we will have a really fast snapback of the market."
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "I will lower my risk to be above the eye or a stop to zero and run this train on the way down trailing aggressively my stop loss when I see that buyers might take back control."
**Source GPS: 8CWKfoSJu3c | BEGIN**

> "They are still closed in the last point of aggression of the sellers."
**Source GPS: 8CWKfoSJu3c | END**

> "you can cover behind this level, you can cover behind this level. The buyers took complete control. You can see all these big trades. And you can see that sellers are trying to protect this level. So if we have another breakout, we can trail our stop in profit."
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "Because I start to see that the big trades are not pushing anymore the price down. We are in a redistribution phase."
**Source GPS: 0jM5Y31YJak | END**

> "because if these buyers aggressive buyers take back control I want to be out of the market."
**Source GPS: 8CWKfoSJu3c | BEGIN**

> "the market explode from this level. You see all these aggression and a failed auction and this is the reason I closed my trade."
**Source GPS: fZlNGWvd2Ko | END**

> "I'm loading and scaling in position trying to get my losses smaller and smaller."
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "I'm only risking the profit of the day, okay? I'm not risking more."
**Source GPS: fZlNGWvd2Ko | MIDDLE**

> "the trades that we continue to take with a maximum drawdown that is break even. So if we go back to break even, we stop the session."
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "You need volatility to do these kind of trades. And unfortunately, volatility is not there every day."
**Source GPS: 8CWKfoSJu3c | MIDDLE**

## 3. Tom setups

### TOM-1 Counter trade at the top of an unhealthy push (imbalance fade)
1. **Name / trader.** Tom. He calls it counter trading; the trade videos describe "no liquidity left" at the top. Merged files: section 1.
2. **What you see.**
   - Location: the extreme of an impulse leg that starts at the session start (pre-market or cash open) and expands the opening range far beyond normal; price above the prior day's or prior week's value, often outside the prior day's range; old highs / pre-market highs just taken out (a "ledge" of weak highs).
   - Price: the push stalls (lethargy, inside bar at the top), is rejected fast, a P shape breaks up and fails back inside the balance, price trades back below the opening price; later a lower b-shape / lower balance forms.
   - Profile: thin at the top of the leg, the volume sits below ("no liquidity left").
   - Order flow: large sell volume in the stall, selling surplus in delta, a big seller in the footprint, a finished auction at the high; order book empty above (live only).
   - His words: "started way down here and then suddenly shot up just like a powerful rocket" (T6hDJcHrVBM:114-116); "I can clearly see that there's no liquidity left" (k0zm5NYn0IQ:21-22); "we also had a finished auction. That means the market formed a completed auction at the top" (k0zm5NYn0IQ:84-86); "It had already shown me a very nice inside bar right here. And that is exactly what prompted me to take action" (T6hDJcHrVBM:147-150); "this lethargy was characterized by large sales volumes. And that prompted me to plan a short trade there" (l8RZrBfzvp4:72-76); "Here the market has already looked below the opening trade price" (l8RZrBfzvp4:100-102); "we got a wonderful B setup with a pullback here in an even smaller time frame" (zQTbdEweG3c:144-146); "we have a beautiful P setup here. We broke out of this setup to the upside, moved into the resistance area, and simply didn't have any more liquidity up here" (n7ZSkjb7JXs:55-59).
   - Full condition/proof table with ids A-C1..C4, A-P1..P10: V2 s2.1-2.2 (all quoted there).
3. **Entry, stop, target, management (his words).**
   - Entry, three paths: "first philosophy up here, high risk. Second philosophy, pullback. Third philosophy, momentum trader" (l8RZrBfzvp4:212-214). A1 at the top after the proofs; A2 "Anyone who wants to play it safe with such counter trades logically has to wait until this let's call it bullish zone here where you can also clearly see the liquidity gets traded through" (k0zm5NYn0IQ:316-321); A3 "if I now see that we actually break out of this range to the downside, then I would definitely look for another position down here" (k0zm5NYn0IQ:308-312). Order type: one limit-order instance (kXhI, below); otherwise NOT STATED.
   - Stop: above the level where the seller sits / above the volume bell: "the stop loss was set above the bell" (n7ZSkjb7JXs:299-301); "there were strong sellers here. This means your stop loss is definitely in a great position here" (l8RZrBfzvp4:126-128). No reference above: "For the first position, I'm setting a stop-loss of 20 points in the DAX" (k0zm5NYn0IQ:22-24) because "The simple reason for this is that I don't have any reference values up here" (k0zm5NYn0IQ:24-26). Adds: "my stop loss is now set exactly above the last volume levels. And if we push above here again, then it's over anyway" (k0zm5NYn0IQ:460-463).
   - Target: "we'll take out the entire distance below the start of the impulse" (T6hDJcHrVBM:170-172); first target the equilibrium below: "this is the price range where the market was in equilibrium and where I then simply expect a reaction could occur" (zQTbdEweG3c:191-195); intraday gap as target: "a huge intraday price gap during main trading hours. And those are always nice areas that I like to define as targets" (ujedEcmvBMk:103-106); a little before the level everyone sees: "I would rather set my take profit a few points away from this range because often it is exactly the case that such levels that everyone sees" (l8RZrBfzvp4:151-155).
   - Management: section 2.1 (A-M1..M6, A-T5).
   - R:R / hit rate he states: "have a hit rate somewhere in the range of 40 to 45% with such counter trading strategies, then you need at least a riskreward ratio of 1.5" (k0zm5NYn0IQ:549-552); "In terms of riskreward ratio, we're currently at about 1:6" (k0zm5NYn0IQ:93-96).
   - Same setup on a stock after a short squeeze (Avis, ANG R1-R2):

> "If I now enter such a short position, how do I manage my risk? And I can tell you you have to place your risk above this level. That means, for example, if you entered the market at 640, you had a stop loss at 730."
**Source GPS: tS6ZEiHj8gQ | MIDDLE**

> "Because this here is a wonderful B profile."
**Source GPS: tS6ZEiHj8gQ | END**

> "And now, I have a unique opportunity that otherwise wouldn't be possible for me if I were just selling the high. Here, I have a risk that is suddenly significantly and substantially reduced."
**Source GPS: tS6ZEiHj8gQ | END**

   - Same idea after a gap open far from the prior day (ES, ANG R4-R5):

> "Day two after that was the market opening. Very very very very very far away from the previous day."
**Source GPS: kXhIAug0Gh8 | BEGIN**

> "And here you can see it wonderfully that the market simply had rejection up here. And I could then dynamically recognize that there was simply an absolute selling overhang. And so I opened my position here. I said, if we go over this again, there's a high probability we'll run to value."
**Source GPS: kXhIAug0Gh8 | BEGIN**

> "The market had also made its balance here, played exactly the same game as before. And then I did the following and placed another limit order here in case it picked me up again and it did."
**Source GPS: kXhIAug0Gh8 | MIDDLE**

   - B-profile top after an earnings run (Nasdaq, ANG R16):

> "Nvidia had made the earnings running up to this level from my B profile. And if you understand the B profile, you will understand that we know in the top we will go back um to the lower of this price."
**Source GPS: OUM9LYwL8eA | BEGIN**

> "After it go deeper than my last range, I decide for the next short trade."
**Source GPS: OUM9LYwL8eA | END**

4. **Context he requires.** A push without volume under it and without a fundamental story: "especially if there's no fundamental sustainable story" (l8RZrBfzvp4:87-89); other markets not confirming: "if for example fundamental news had led to one market being extremely strong and the other not then that's a different story" (T6hDJcHrVBM:291-294). Many proofs against the trend: "If you make trades against the trend, then you need many, many parameters that speak in your favor" (zQTbdEweG3c:23-26); no count given. Session: DAX pre-market and cash open, "the market phase where the highest liquidity is present between 8:30, 9:00 and 17:35" (T6hDJcHrVBM:94-97); pre-market with less size. Do NOT fade when volume builds above: "if the market were to accumulate large volumes there then yes I would definitely be looking for a long position" (k0zm5NYn0IQ:357-360); not on a true breakaway gap: "we're not at the all-time high and didn't gap out of a range" (zQTbdEweG3c:87-89). Direction is set for the day in advance: "The direction you want to take for the day must be predefined and that can change if the context breaks" (ujedEcmvBMk:277-279).
5. **BTC visibility: PARTIAL.**
   | element | BTC |
   |---|---|
   | impulse leg, prior day/week value, prior range, old highs, inside bar, fast rejection, b/P shapes, thin top profile | YES (klines + computed profile) |
   | sell volume in the stall, delta surplus, big seller in footprint, finished auction | YES (aggTrades) |
   | "from the session start / pre-market / cash open", "below the opening price" | PARTIAL: BTC has no open; any anchor is OURS (TOB s2.3: "needs a BTC open") |
   | gap away from the prior day (kXhI) | NO (no BTC session gaps) |
   | no news behind the move | NO (no news data) |
   | other markets not confirming | PARTIAL (ETH yes; ES/NQ not on disk) |
   | order book empty above | NO for history (live only) |
   | retail sentiment heavily long (A-P10, paraphrase) | NO on disk |
6. **Evidence.** 16 trades = 10 TL groups (T1, T2, T2b, T3, T3b, T5, T6 = T10, T7, T11, T12; V2 s5 maps each to family A; T11/T12 from frames only) + TL candidate T8 (gold, entry not shown) + 5 ANG rows not in TL: R1, R2 (Avis), R4 (ES), R5 (NQ limit order; ambiguous with TOM-2), R16 (Nasdaq B-profile top). ANG R8-R11, R14, R15, R18, R19 are TL T6, T3, T3b, T5, T2, T2b, T1, T7 and are not counted twice. Three of five design sessions also show a losing first attempt that is not a ledger row (V2 s3).
7. **Gaps and contradictions.**
   - P shape: ANG names T6hD a "P profile exhaustion short", but in the same video Tom says "a P is usually something that strategically leads to a trend continuation" (T6hDJcHrVBM:161-163). V2 resolves it as a P whose upside breakout fails ("a P pattern formation with a so-called fake breakout and a renewed acceptance of this balance", T6hDJcHrVBM:220-222).
   - Healthy vs unhealthy: STR s3 (reconstructed matrix, not his table) makes counter trades invalid in a healthy trend and the old engine blocked the fade in `trend_healthy`; Tom's test is volume under the move ("The idea was that this trend isn't entirely healthy" + "there was simply no liquidity left here and the liquidity was down here", zQTbdEweG3c:231-232, 234-236), not position against value (V2 s8 G2/G3).
   - R:R: 1.5 at 40-45 % hit rate (k0zm5NYn0IQ:549-552) vs greater than 3 at 30-40 % (BVpY, TOM-2 below). Both his.
   - Proof count: NOT STATED ("many, many"); the old engine's 3 proofs are OURS.
   - kXhI R4/R5: the ES trade sits after a gap away from the prior day (TOM-8/GAP G19 territory) and R5 is "the same game" after a balance (TOM-2 territory); assigned here because the target is value after a rejection at an extreme. Open.
   - OURS from older specs (never his): opening-range size as rank above the median of 20 prior sessions; "thin" = top third volume below each lower third; 5-minute inside bar (only chart he names, paraphrase n7ZSkjb7JXs:290-293); proof count k*; order types (A1/A2 limit, A3 stop-market); 1 lot, no partial, no add; at most 1 re-entry per session; flat at 17:35; session start 07:00 Berlin; A-C2 coded as close above the prior day's HIGH (stricter than his words); A-S1 = lowest prior session high above the zone; A-P5 = high above 20 daily highs; BTC minimum stop width 0.40 % (V2 s11-s16). Old engine: 3 proofs, volume spike 2x over 240 bars, CVD-divergence "unhealthy", 8-bar timeout, 0.1 % stop floor, 2-3.5R target window (TOB s2).

### TOM-2 Counter trade in balance
1. **Name / trader.** Tom, "counter trading" in a sideways market. Merged files: section 1.
2. **What you see.** A sideways market (balance profile); price at the top of the balance (prior VAH, balance high) for shorts or at the bottom for longs; a b-profile at the top or a lower balance after a rejection is "the setup itself"; volume comes in on the side that moves price.

> "Sideways means that supply and demand are in balance. And when supply and demand are balanced, the market will always try to return to that equilibrium."
**Source GPS: BVpYGKz9PBU | BEGIN**

> "I can definitely look for short trades up here and long trades down here."
**Source GPS: BVpYGKz9PBU | BEGIN**

> "here is a B profile and that shows me that there is weakness in the market. So first I have the information that this is where I need to look for a counter trading setup and secondly I'm now also being given the setup itself."
**Source GPS: BVpYGKz9PBU | MIDDLE**

> "It gets sold off again and we get a lower balance. That means from the PBD logic, we now have an opportunity here to enter the market."
**Source GPS: BVpYGKz9PBU | MIDDLE**

3. **Entry, stop, target, management.**
   - Entry: at the zone with a setup (dynamic) or on the pullback to the setup after proof:

> "this is always the most pleasant scenario happens when the price action unfolds like this. And there's a pullback to my setup because I waited patiently. That approach is even more effective for me."
**Source GPS: BVpYGKz9PBU | MIDDLE**

> "Now here at 260 I have the opportunity to take my entry."
**Source GPS: BVpYGKz9PBU | END**

   - Stop: back above the level he sells under:

> "if we move back above this level then I have a problem with my short position"
**Source GPS: BVpYGKz9PBU | END**

   - Target: the next price area / volume below (plan: 260 -> 140, ANG R24); with a steep VWAP, VWAP as the target:

> "If we want to use the volume weighted average price or VWAP as a counter trader, we can look at whether the VWAP is very steep, for example, and if the price is running extremely high, then we can define the VWAP as a profit target."
**Source GPS: 43JaKHRvxHk | END**

   - Management: NOT STATED for this setup (section 2.1 rules come from TOM-1 trades). R:R he states:

> "even with a hit rate of 30 to 40% you have an average riskreward ratio of greater than three and you will be incredibly successful mathematically with this approach"
**Source GPS: BVpYGKz9PBU | END**

4. **Context.** Balance, not trend; continue "until either the big player here or the big players here decide that the market will continue" (STR s6.2A, BVpY). After a strong trend a balance is not yet a short: "That doesn't mean it's going short yet. It can just as easily continue long" (zQTbdEweG3c:110-111). Time of day, news: NOT STATED.
5. **BTC visibility: YES.** Balance, VAH/VAL/POC, b-profile, lower balance, VWAP: computed from klines/aggTrades. Volume coming in: aggTrades.
6. **Evidence.** 0 real trades. 1 plan (ANG R24, illustration). kXhI R5 is a possible instance (assigned to TOM-1, open).
7. **Gaps and contradictions.**
   - Zone side: STR 4.3 lists "Prior day VAL (for shorts) or VAH (for longs)" and quotes "look here is yesterday's value area low and maybe that's where the VPOC is. First in terms of price range if I see that the market is below that then I can definitely try a short trade" (BVpY, STR TOM-145): a short BELOW value low is not a fade of the balance top. Which one is the setup is open; the quote is not verified here.
   - "B profile" has no definition in his words (STR s10 gap 3); PBD logic is taught in never-extracted videos (section 6).
   - When balance turns into breakout (TOM-6): NOT STATED (STR s10 gap 9).
   - Stop tighter "depending on the setup" (STR 4.7, BVpY): no rule.
   - OURS: engine `ct_short`/`ct_long` at VAH/VAL zones and the "3 proofs" bar.

### TOM-3 Limit sell below the last volume step
1. **Name / trader.** Tom (yRvMW6lgN1o, one taken trade: risk $250, gain about $1,212).
2. **What you see.** A trend that flattens into a range; an inside day (the whole day inside the previous day's range) near the high; a spike lower that leaves "stability in trading volume"; the profile has a step (a sharp edge of volume); below it price can move fast.

> "I can see that we have a range here. That means the trend now seems to be flattening out. But of course, this information alone is not enough to say I want to generate a short trade."
**Source GPS: yRvMW6lgN1o | BEGIN**

> "The next piece of information I have is that we had a so-called inside day trading completely within the previous day's range."
**Source GPS: yRvMW6lgN1o | BEGIN**

3. **Entry, stop, target, management.**
   - Entry: a resting sell limit on the pullback, just below the last volume step:

> "That was the moment when I decided that below this price range here, I was interested in entering a trade on a pullback with the target down here."
**Source GPS: yRvMW6lgN1o | BEGIN**

> "I said I would place a limit order specifically right below the last volume step of the corresponding price profile of the volume profile"
**Source GPS: yRvMW6lgN1o | MIDDLE**

   - Stop: "up here" only (location NOT STATED in words); size in ticks:

> "with a stop-loss up here, we now have a risk of 12 ticks. We have a profit of 97 ticks."
**Source GPS: yRvMW6lgN1o | END**

   - Target: "down here" (NOT STATED as a level type in the quotes read). Management: waited patiently (no rule).
4. **Context.** Trend flattening, inside day, near the all-time high (ANG R13). Session, news: NOT STATED.
5. **BTC visibility: YES.** Range, inside day (UTC day OURS), profile step from aggTrades. His order-book remark ("This is exactly the boundary in our order book", yRvM MIDDLE) is commentary, not needed to see the setup.
6. **Evidence.** 1 trade (ANG R13; index future, levels about 6,763-6,768, not named).
7. **Gaps.** Stop location, target level type, what makes a "volume step": NOT STATED. Possible overlap with TOM-2 (sell the top of a range) and with TOM-1 path A2 (pullback after proof); kept separate because the entry is a resting order at a profile edge, the only one of its kind. yRvMW6lgN1o is V1-only, not in the 26 never-extracted list; worth a V2 pass (inventory).

### TOM-4 Trend continuation pullback
1. **Name / trader.** Tom, "trend continuation setup", "trend following".
2. **What you see.** A healthy trend: volume backs the move, real acceptance (not quick spikes), the previous reaction was in the trend direction; price pulls back to VWAP (trend-based VWAP) or to the value it just accepted; a full P impulse shows acceptance.

> "You should then definitely only look for a trend continuation setup here."
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "If I see the whole thing as a trend following trader, I have to wait for a long trend and can wait until the VWAP gives me a pullback."
**Source GPS: 43JaKHRvxHk | MIDDLE**

> "Not with quick spikes but with real acceptance."
**Source GPS: qLnQan0KGmQ | END**

> "Always check what was the previous reaction. Ah, it was bullish. And if it was bullish, the probability is initially higher that this path will then continue upwards."
**Source GPS: qLnQan0KGmQ | END**

3. **Entry, stop, target, management.**
   - Entry: on the pullback after proof:

> "Sure, the very brave ones just buy here, but you can also wait until the proof arrives."
**Source GPS: qLnQan0KGmQ | MIDDLE**

> "Now you have options to enter here via pullback or to enter here again via pullback."
**Source GPS: qLnQan0KGmQ | MIDDLE**

   - Stop: "The stop loss belonged right here" (qLnQ, STR 5.7): location NOT STATED in words.
   - Target: the next high-volume area:

> "In theory, I can plan the next leg up to the next high volume area. Especially when the market shows me once again that it's working with power and it accepts these price ranges."
**Source GPS: qLnQan0KGmQ | END**

   - Management: NOT STATED.
4. **Context.** Trend, not balance ("in a sequence like this, you mustn't trade a trend continuation", 43JaKHRvxHk, TOM-7); VWAP must have a trend: "first rule, very important, the VWAP must be based on a trend" (43Ja BEGIN, STR s3). Time, news: NOT STATED.
5. **BTC visibility: YES.** Trend, VWAP (anchor OURS), value areas, volume under the move, high-volume nodes.
6. **Evidence.** 0 trades (TL and ANG have none tagged as this; TOM-5 trades are possible instances).
7. **Gaps.** Stop location, entry trigger at the pullback: NOT STATED. Trend speeds (fast, normal, creeping; TOB s2.1) not in these quotes. OURS: engine `tc_long` at VWAP only, no `tc_short` (V2 s6).

### TOM-5 Pullback long into value after a buying tail
1. **Name / trader.** Tom; ANG names it "pullback to prior-day value/POC with buying tail for longs".
2. **What you see.** Yesterday's profile has a buying tail; today price moved back into value, was rejected at the POC ("PC" in the caption), and pulls back; buyers aggressive at the level; a ledge of old highs above as the target.

> "If we look at yesterday's profile here, we formed a nice buying tail down here after the market opened, then moved back into value, saw rejection at the PC, and are now making the pullback. And now we should definitely reach the price area of the value high up here."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "You can really see here how aggressively people are buying."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

3. **Entry, stop, target, management.**
   - Entry: long at the pullback level (trigger NOT STATED beyond aggressive buying).
   - Stop and target:

> "The stop loss goes below the last low here and my take-profit is set above the highs."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "Because up here, we've formed a beautiful ledge and I expect the market will take those out."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

> "Stop loss as mentioned below the bid below the business zone."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

   - Management: add at the breakout if speed holds (TOM-6 quote); after a stop, re-enter on buyer stability with the stop below the last swing low (crude, ANG R7):

> "And that prompted me to use this buyer stability again even though I was kicked out to re-enter the market, yeah. And I then placed my stop loss below the last swing low again."
**Source GPS: kXhIAug0Gh8 | END**

4. **Context.** Prior day with a buying tail and an equilibrium zone; "There was a nice buying tail here, so strong buyers. A nice selling tail, strong sellers and with a huge volume as well. And here was the equilibrium zone." (kXhI BEGIN, the ES prior day; quoted for the tail/equilibrium reading). Time, news: NOT STATED.
5. **BTC visibility: YES.** Prior UTC-day profile, buying tail, value high, POC, old highs, buying aggression (aggTrades).
6. **Evidence.** 3: ANG R17 (4MoN, win), R6 (crude long at prior-day value / VPOC zone, stopped 2 ticks beyond the stop: "Specifically two ticks lower than where my stop loss had been set.", kXhI END per ANG), R7 (crude re-entry, win, exited early).
7. **Gaps and contradictions.** STR files 4MoN under breakout (s6: ledge, speed, add at breakout); ANG under this pullback. Both are in the video: entry on the pullback, add on the breakout. The "last low" vs "below the business zone" stop: two phrasings in one video, same trade. Whether TOM-5 is a case of TOM-4 (trend continuation) is NOT STATED.

### TOM-6 Breakout / break-in
1. **Name / trader.** Tom, "breakin or breakout".
2. **What you see.** A balance about to resolve, an overlap zone (volume nodes, value highs, several POCs in one range), a ledge above prior highs; speed picks up and buying shows; VWAP and the day's average price shift in the break direction.

> "I have the opportunity to trade the market for myself either through a breakin or a breakout."
**Source GPS: BVpYGKz9PBU | MIDDLE**

> "should the VWAP suddenly start to go lower and lower, and thus the price, the average price of the day, shifts downwards, then the probability increases that a trend continuation downwards will occur here again, or even a breakout."
**Source GPS: 43JaKHRvxHk | END**

> "if it accepts new prices, then it looks for the next high volume price and that is your target."
**Source GPS: qLnQan0KGmQ | END**

3. **Entry, stop, target, management.** Entry/add at the break:

> "If we continue to move steadily up and carefully maintain the current speed, I'll add to the position again at the breakout."
**Source GPS: 4MoNjEQ2Dd8 | BEGIN**

   Stop: NOT STATED for a breakout entry (STR s10 gaps 6-7). Target: the next high-volume price (quote above). Management: hold for the explosion, not the scalper's exit:

> "As I said, for the scalpers, they're getting out up here now. But we intraday swing traders, breakout traders who are waiting for the explosion. We wait"
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**

4. **Context.** Balance resolving or trend accelerating; overlap zones (YmygDgtoxO8, STR 6.3, not re-verified here). Time, news: NOT STATED.
5. **BTC visibility: YES.** Balances, overlaps, ledges, VWAP shift, buying/selling speed (aggTrades).
6. **Evidence.** 0 standalone trades; the 4MoN add (TOM-5) is the only taken instance.
7. **Gaps.** Entry trigger, speed threshold, stop: NOT STATED. Never-extracted `uk4PZV59nYw` ("his EXACT breakout setup") and `gFJBg8Bsw68` ("BEST breakout strategy") are the obvious sources (section 6).

### TOM-7 Scalp in balance around VWAP
1. **Name / trader.** Tom, "dynamic scalping".
2. **What you see.** VWAP flat (sideways), no trend day from the open; price ranges around VWAP; short the top, long the bottom.

> "Then you have the opportunity to keep looking for shorts at the top and keep looking for longs at the bottom until a reversal of the market environment eventually occurs."
**Source GPS: 43JaKHRvxHk | END**

> "You can define so-called price ranges from the VWAP where you expect a reaction."
**Source GPS: 43JaKHRvxHk | MIDDLE**

3. **Entry, stop, target, management.** Entry: at the range edges (trigger NOT STATED). Stop: NOT STATED (he asks where to give up and does not answer, STR s10 gap 8). Target: VWAP, modest:

> "And if I were to only ever take the trade up to the VWAP, I can already see those are very modest profit targets."
**Source GPS: 43JaKHRvxHk | END**

   Management: NOT STATED.
4. **Context.** Only with a sideways VWAP: "in a sequence like this, you mustn't trade a trend continuation. You absolutely have to go for counter trades." (43JaKHRvxHk MIDDLE, STR 7.2).
5. **BTC visibility: YES** (VWAP anchor OURS). TOB s2.5 notes BTC fit is poor for cost reasons (outside this file's scope).
6. **Evidence.** 0 trades.
7. **Gaps.** Stop, entry trigger, range definition: NOT STATED. Scalping videos `G0CiJcuXCRs`, `YVUcLTsCOZI` (V1 with no anchors) and never-extracted `viT_VzF5Fsw`, `uFxYcpiaOpw` may fill it (section 6). OURS: engine `scalp_*` at VWAP.

### TOM-8 Gap close (incl. Monday gap pullback long)
1. **Name / trader.** Tom, gap trading. V2 family C (T4). GAP G01-G22.
2. **What you see.** The cash-session open far from the prior close (a price gap; cash session only); open inside the prior range makes a fill likely; open above the whole prior day: look at liquidity there; after the open the extension fails (liquidity decreases), price goes into a range, then below the range with liquidity rising again; Mondays often extreme.

> "since the market is within fair prices, there's simply, technically speaking, the 80% rule where the market trades within value. So, there's a high probability the market fills it first, unless the fundamental story is extreme, which we'll get to."
**Source GPS: 96iPFDpXEcU | BEGIN**

> "Now the market goes back into a range and eventually goes below the range. And if it goes below the range and liquidity increases again, then you can reasonably expect that the gap will be closed. It's a very high probability and is simply a great thing from a logical standpoint."
**Source GPS: 96iPFDpXEcU | END**

   T4 in his words: "whether this gap that's present is a gap that's likely to be closed or if there's a fundamental news story behind it" (UOBgXV20yCM:76-78); "Often on Mondays, we have extremes in one direction or the other" (UOBgXV20yCM:84-85).
3. **Entry, stop, target, management.**
   - Entry: wait for the liquidity to drop and return:

> "But if you just wait a moment until the liquidity goes down and then increases again, then the probability is much higher that you can trade this gap close with a great risk reward ratio."
**Source GPS: 96iPFDpXEcU | END**

     T4: "after the market made a pullback here and gave me a buy signal here" (UOBgXV20yCM:89-90); the buy signal: NOT STATED.
   - Stop: NOT STATED (T4 frame: 30 points, TL ledger frame value, not a rule).
   - Target: prior value: "Here was the value. That was me profit target" (UOBgXV20yCM:144-146) [V2 s4 cites lines 137-138, which do not hold it]. R:R: "an average risk-reward ratio of a good 2 2.5 as a rule" (UOBgXV20yCM:107-108).
   - Management: take it at the predefined level (A-T5, section 2.1; UOBg is a video about not moving targets).
4. **Context.** Story first: political gaps close ("political markets have short legs", GAP G08), substantial economic news gaps likely do not (G07); the close often comes the day after (G09); only cash-session gaps matter and intraday gap work only in main hours (G02); product matters (commodity gaps differ, G10).

> "So, stop with this nonsense that you can always assume gaps will be closed."
**Source GPS: lO-Iptd29t4 | MIDDLE**

5. **BTC visibility: NO.** No session gaps on BTC (24/7). The day-3 and "open vs prior range" readings need a cash session. Intraday price gaps that price ran through fast exist on BTC but Tom uses those as TARGETS (G24, TOM-1), not as this setup.
6. **Evidence.** 1 trade: TL T4 (= T9 alias; FDAX long, frame stop 30 points, target Friday's value). ANG R12 is the same trade. l8RZ (TL T7, gap exaggeration fade) is a gap trade too but assigned to TOM-1 by V2 s5.
7. **Gaps and contradictions.** G18: footprint intraday bar-to-bar gaps "closed in well over 95% of cases" historically but "stop using the strategy" now (lO-Iptd29t4 END). Stop and entry trigger: NOT STATED. Only one trade (V2 parks the family).

### TOM-9 Gap not closed: trade with the trend
1. **Name / trader.** Tom (GAP G06, G11, G16).
2. **What you see.** A gap above the whole prior day where volume builds (prices accepted, a P forms); gap-fill speculators wrong at the open; market holds the new range; liquidity returns without closing the gap.

> "Because at the very moment they become substantial, it means that the market is accepting prices up here. And what do we have then? Then, according to my PBD logic, we have a P."
**Source GPS: 96iPFDpXEcU | BEGIN**

> "It tells me that the people who speculated down here on gap closes were initially wrong. It also gives me further information namely that I see supply and demand have shifted to a new higher price range."
**Source GPS: YopZ5ZDmMFw | MIDDLE**

3. **Entry, stop, target, management.** Entry: "with the corresponding structures available to you" (no setup named):

> "Now the market might briefly move above it again, but doesn't close the gap, and the liquidity returns. Then you are allowed to trade in the direction of the trend here using the corresponding structures available to you."
**Source GPS: lO-Iptd29t4 | END**

   Stop, target, management: NOT STATED. A breakaway gap is not expected to close for a long time (G17).
4. **Context.** Substantial news behind the gap (G07); after a huge gap the market is lethargic first (G13).
5. **BTC visibility: NO** (no gaps).
6. **Evidence.** 0 trades.
7. **Gaps.** Everything after "trade in the direction of the trend" is NOT STATED; it hands over to TOM-4/TOM-6.

### TOM-10 Closing-auction gap reversal
1. **Name / trader.** Tom (GAP G23; DVZVE9rXGtU).
2. **What you see.** A very strong close where a big share of the day's volume prints in the closing auction (a closing extreme and a gap), then the next day opens down / goes red.

> "Most of the time in the closing auction, if another extreme is reached there, you'll see a gap down at the open the next day and then things start to reverse. And that's when you can short."
**Source GPS: DVZVE9rXGtU | MIDDLE**

> "So, if the market closes really strong and the next day it goes back into the red, then it just makes sense to take a contrarian position."
**Source GPS: DVZVE9rXGtU | MIDDLE**

3. **Entry, stop, target, management.** Entry: short once the reversal starts (trigger NOT STATED). Target: back to the original value (G23 first quote, "trade something like that back to the original value"). Stop, management: NOT STATED.
4. **Context.** Closing auction of a cash market (stocks/index).
5. **BTC visibility: NO** (no closing auction).
6. **Evidence.** 0 trades.
7. **Gaps.** All execution fields NOT STATED. One video.

### Tom: unassigned and anti-examples
- ANG R20 (wPMiyJXL0zU): ANG infers a short counter trade, but the target he names reads like a long: "In this case, for example, I take the value area high of the current day as my target area." (MIDDLE) followed by "the market can continue to rise" (context window, same passage). Side is unresolved; not assigned. Stated risk:

> "So I simply had a risk of about 15 points, but a planned range of nearly 80 points."
**Source GPS: wPMiyJXL0zU | MIDDLE**

- ANG R21, R22 (dh-ysRR8f-M): crude-oil dip buy into the 2020 storage crisis and a long held over a weekend; told as his biggest losses. Anti-examples, not setups.
- ANG R3, R23, R25, R36-R38: duplicates or illustrations (sizing, R:R), not counted.

## 4. Fabio setups

### FAB-1 Balance with CVD pressure, break on volume
1. **Name / trader.** Fabio ("sell model day", FTM). Merged files: section 1.
2. **What you see.** A balance (profile with fair value in the middle, no direction); inside it CVD runs hard one way while price stays flat (distribution = falling CVD, accumulation = rising); then the first candle where price follows the volume out of balance, with big trades in that direction.

> "We can see that the market is balanced at this time and if we plot a profile for the current situation we can just see balance and there is the fair value on the middle there is no clear direction"
**Source GPS: 0jM5Y31YJak | BEGIN**

> "So the market was balanced at this time but as you can see the direction from the pressure of the market and cumulative volume delta is pretty huge even before the breakout. So the market is clearly building pressure down."
**Source GPS: 0jM5Y31YJak | BEGIN**

3. **Entry, stop, target, management.**
   - Entry: the first candle with volume follow-through and price confirmation:

> "the first moment that we had some kind of follow up on volume and confirmation from price was exactly this candle. This was my first position because the market told me Fabio we are going down the volume pressure is down and we have the price action that is following up."
**Source GPS: 0jM5Y31YJak | MIDDLE**

   - Stop: "The first stop loss was here" (section 2.2 quote): location NOT STATED in words. FTM's "just past the absorbed/breakout extreme" is an interpretation.
   - Target: NOT STATED as a level; exits by flow (section 2.2: big trades stop pushing, redistribution); FR-21 "take profit at the extreme when big trades sell into it" (rulebook paraphrase, not verified here).
   - Management: break-even once it explodes; second and third positions in the trend, funded by the first (FR-14); section 2.2.
4. **Context.** Directional, volatile day (section 2.2); NASDAQ futures, World Cup session. Session time in this video: NOT STATED (8CWK says he scalps the New York session).
5. **BTC visibility: PARTIAL.** Balance, profile, CVD, candle follow-through: YES. "Big trades": PARTIAL (aggTrades rows are not orders; V3 s1 notes "Big print" = one aggTrades row).
6. **Evidence.** 1: FL F2 (+ F2-m1 second balance box continuation); ANG R26, R27 (positions 1-5 in the same session).
7. **Gaps.** Initial stop, what counts as "big", balance length: NOT STATED. OURS (V3 s7.1): N {60,120,240} bars, k_bal 0.8, POC band 0.25, pressure p {0.05,0.10}, drift 0.25, big trade = prior-30-day 99th/99.9th percentile, tier VR 1.5, S4 window m, S8(a) 15 bars, NY window 390 bars / cutoff 330, 13:30 UTC mapping, BE distance be_k, stop floor f, Dmax 1 %, -3R daily stop, 10 first legs.

### FAB-2 Absorbed push, rewarded effort ("punch to the wall")
1. **Name / trader.** Fabio, "punch to the wall", "rewarded effort".
2. **What you see.** One side's aggression is absorbed: big delta, almost zero price result ("punching a wall"); the other side's aggression moves price (effort with result) and controls the auction; trade with the side that gets the result, usually with the day's trend.

> "What we have in this situation is the path of least resistance of the buyers getting completely absorbed. You can see the punch to the wall I marked for you and you can see the rewarded effort of the sellers."
**Source GPS: 8CWKfoSJu3c | BEGIN**

> "the result of the price for a pressure in by delta was almost zero. So this is a confirmation that the buyers are punching a wall and I want to be short in this position."
**Source GPS: 0jM5Y31YJak | END**

3. **Entry, stop, target, management.**
   - Entry: after the absorption, with the controlling side (trigger bar NOT STATED beyond the quotes).
   - Stop: NOT STATED in words (F1 frame: 15.75 points, risk $3,150, FL).
   - Target: a far fixed target on the label (F1 1:19, "Final target is 27,600 for 1 to 19 risk-to-reward", 8CWK MIDDLE, not block-quoted here); or flow exits (section 2.2).
   - Management: stop to zero, trail behind the last point of aggression (section 2.2); add high in the curve, not low:

> "Now in this case we have complete control on the auction of the sellers. We are really high in the curve"
**Source GPS: 8CWKfoSJu3c | BEGIN**

> "They did another punch to the wall. And this could be a level where we cover ourself is if the market decide to break again the low. This is an aggressive trailing stop that I take when we have already a nice floating profit."
**Source GPS: 8CWKfoSJu3c | BEGIN**

4. **Context.** New York session; volatile days only (section 2.2). "I scalp the NASDAQ during the New York session" (8CWK BEGIN, V3 P33).
5. **BTC visibility: PARTIAL.** Delta vs price result per bar: YES (aggTrades). Big trades: PARTIAL. "Path of least resistance" in the heat-map sense: NO (L2).
6. **Evidence.** 1: FL F1 (NQ short 10, trailed to +$23,000). ANG R28 (0jM5 third position) is the same setup inside the FAB-1 session; ANG R29 = F1.
7. **Gaps and contradictions.** FL labels F1 `balance_failed_auction_punch_to_wall` (FAB-3 words) while ANG/8CWK describe absorbed buyers + seller control (this setup). FAB-2 and FAB-3 may be one setup seen at two moments (absorption, then the other side's aggression); kept apart because FAB-3 is a side flip at a consolidation and FAB-2 a with-trend add point. Absorption threshold: NOT STATED ("almost zero"). OURS: V3 S3 L 60, z_hi {2.0,2.5,3.0}, r_abs 0.25, r_ctl 1.0.

### FAB-3 Failed auction of one side, then aggression of the other at the level
1. **Name / trader.** Fabio, "failed auction of the seller and then aggression of the level of the buyers".
2. **What you see.** A consolidation where one side pressed and was absorbed; then the other side aggresses at that same level with big trades and breaks it; a horizontal level whose break makes the move "exponential".

> "this consolidation area got completely wrecked by buyers that took control. The sellers got absorbed here."
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "capitalize on the failed auction of the seller and then aggression of the level of the buyers."
**Source GPS: fZlNGWvd2Ko | BEGIN**

> "It means that if we can break this low, this horizontal level, probability that we go down it's exponential."
**Source GPS: jasv3L-d8ZE | MIDDLE**

3. **Entry, stop, target, management.**
   - Entry: with the aggressor at the level (side flip allowed: in fZ two continuation shorts failed first, then this long).
   - Stop: initial NOT STATED in words; scratch plan if the level fails (section 2.2, "this one become the new pivot").
   - Target: none fixed, ride to the day's extreme:

> "I want to try uh good risk to reward trades and amazing risk to reward trades to take the top of the day."
**Source GPS: fZlNGWvd2Ko | BEGIN**

   - Management: the whole fZ sequence (section 2.2: load/reload, de-risk on own failure, stop to zero on the other side's failure, trail on the break of the defended level, exit on climax + failed auction). LBL s2 D06-D28 is the full decision log.
4. **Context.** Day P&L floor at 0, risk only the day's profit (section 2.2); jasv3L: a compression day with dealers "long gamma", he expects a breakdown:

> "Now the market maker are long gamma. So they will try to compress volatility. I expect a good explosion down."
**Source GPS: jasv3L-d8ZE | END**

5. **BTC visibility: PARTIAL.** Consolidation, absorption by side, aggression, level break: YES. Big trades in the candle body: derivable from aggTrades but not in our bars (V3 s1, M10). "Buyers wall": NO (L2). Dealer gamma: NO (no options history; V3 dropped it).
6. **Evidence.** 2: FL F3c (fZ long re-entry, risk $980 to make $25,000), F5 (jasv3L short 15->18 lots after a losing start). ANG R32 = F3; R34 = F5.
7. **Gaps and contradictions.** LBL s4: the V1 extract atomized this sequence (R2 "failed auction plus buyer aggression" lost the side relation), and turned the scratch plan into a BE rule that FR-12 then merged with 0jM5's opposite trigger (BE after success vs BE on failure). "Failed auction" has no mechanical definition (FR s4). OURS: V3 S5D/model D (rest 3 bars, limit at the edge), M9 re-pivot not applied.

### FAB-4 Failed breakout back into balance
1. **Name / trader.** Fabio (FR-19, FR-86 via V3 model B; FL F4 schematic).
2. **What you see.** A balance; price probes outside it; the probing side is absorbed; price closes back inside; reversal toward the other side of the balance. In his words only as the FL frame note (`hand-drawn schematic at t=780: balance -> failed breakout -> reversal`, 9IliXww64uM) and the rulebook paraphrase "CVD absorption confirms failed auction and day direction" (FR-19, source o-w5Gxss6T0, not in raw_transcripts_canonical: no verbatim quote available).
3. **Entry, stop, target, management.** NOT STATED in any verified quote. OURS (V3 model B): reclaim within 5 bars, limit valid 3 bars, stop beyond the probe extreme + 1 tick, target the opposite balance edge (or a trail variant).
4. **Context.** NOT STATED.
5. **BTC visibility: YES.** Balance, probe, absorption (delta vs result), reclaim: klines + aggTrades.
6. **Evidence.** 2, weak: FL F4a, F4b (ES shorts from pasted screenshots, 1 lot, no stops visible; assigned only by the schematic in the same video).
7. **Gaps.** This setup exists in our files mostly as OURS structure. Needs a verbatim source; `9IliXww64uM` has captions on F: (FL:28-31) but not in raw_transcripts_canonical; `o-w5Gxss6T0` has no raw transcript (section 6).

### FAB-5 Buyers protect a level: long, squeeze trapped sellers
1. **Name / trader.** Fabio ("protection wall", "buyers protecting the level", FL).
2. **What you see.** Price comes down into a level (a value-area low, a gap, a resting "protection wall"); selling is absorbed there (struck several times, absorbed each time); buyers defend it; long, expecting a squeeze of trapped sellers; in line with the day's main direction.

> "In this one, this is amazing because you have a protection wall that is there. This is a resting liquidity, is not fresh liquidity and as you can see the market approach here and get absorbed the first time, strike again this area, absorb the second time, strike this area, absorb the third time"
**Source GPS: FawPrRUGNpk | BEGIN**

> "This is the mean reverting on the protection wall of the buyers in line with the main direction."
**Source GPS: FawPrRUGNpk | BEGIN**

3. **Entry, stop, target, management.** Entry: at the defended level (F6: buyers protecting the gap / value-area low, FL:55, caption paraphrase). Stop: "tight stop" and a fixed dollar risk of 1,500-2,000 (FL:55, 62, caption paraphrase of DyS79Eb92Ug, not verified against a raw transcript): location NOT STATED. Target: a sell limit at a fixed distance on the frames (F6 25001, F10 25074.25; FL), rule NOT STATED. Management: stop to about zero fast, scratch if the auction fails, re-enter ("can try another time", FL:62 paraphrase); scale 4 -> 8 -> 10 lots (FL).
4. **Context.** US cash session (every FL frame with a clock). "Wait for buyer protection before long" (FR-67) and "No counter-trend long while CVD is falling" (FR-66) are rulebook paraphrases of FawPr, not verified here.
5. **BTC visibility: PARTIAL.** Value-area low, repeated absorption at a price (aggTrades by price): YES. The resting "protection wall" (passive liquidity): NO (no order-book history). Gap level: NO (no BTC gaps).
6. **Evidence.** 13 entry rows: FL F3a, F3b (fZ, protection wall buy), F6, F7, F8, F9, F10 (DyS79/Jpd96 protection-level squeeze longs), F11, F12, F13, F14 (four chase longs near the 25,110 prior high, all stopped). Outcomes in FL: F6 TP hit; F7 scratch; F8 stopped; F9 small win; F10 TP hit; F11-F14 stopped.
7. **Gaps and contradictions.** F11-F14 are labelled "chase long after squeeze above prior high"; whether they are this setup or a breakout chase is NOT STATED (FL assigns them by sequence). No raw transcript for DyS79Eb92Ug / Jpd96fLqr5M in raw_transcripts_canonical: the setup's words come only from FawPr (a heat-map lecture) and FL paraphrases. Contradiction in management: 8CWK says adding "low in the curve" is not the best idea (V3 P11) while F7-F9 re-enter the same level three times in five minutes after losses (FL:67).

### FAB-6 IVB: first 30 minutes of the US open
1. **Name / trader.** Fabio ("the IVB"; LQvv5xgy_ik).
2. **What you see.** The first 30 minutes of the US equity open; its range (bottom/top) sets the day's direction.

> "the bottom of the first 30 minutes is giving a lot of value in the direction of the day"
**Source GPS: LQvv5xgy_ik | END**

3. **Entry, stop, target, management.** NOT STATED in the verified quote. OURS (V3 model C): break of the IB edge with S4, stop at the IB midpoint + 1 tick, one IVB trade per day. FR-81 (StaphlRH8NQ): "Opening range breakout has positive skew", "first 30 minutes" and "13.5%" (rulebook paraphrase, not verified here).
4. **Context.** "the nature of the US equities have predictable behavior during the opening" (LQvv END, same passage; not block-quoted). Can be improved with option flow (same passage).
5. **BTC visibility: PARTIAL.** The 30-minute range is computable from klines; the US equity open is not a BTC event (the 13:30 UTC mapping is OURS; V3 MP:128 says it may not port).
6. **Evidence.** 0 trades.
7. **Gaps.** Entry, stop, target all NOT STATED. LQvv is a risk-management lecture; the IVB is mentioned as an example.

### FAB-7 Heat-map liquidity: reload, protection wall, break and protect, book sweep
1. **Name / trader.** Fabio (FawPrRUGNpk, a liquidity heat-map lecture; FR-17, FR-31 to FR-73: 34 rules need L2).
2. **What you see.** Resting limit-order walls on a heat map (darker = more important); price hits a wall and is absorbed; walls reload (icebergs); a break whose new level is then protected by fresh resting orders; the path of least resistance summed over five price levels; sweeps at all-time high/low, range extremes, the NY high.
3. **Entry, stop, target, management.** Rulebook paraphrases only (not verified here): FR-43 "Reload breakout entry and stop" ("breakout protected below the reload level"), FR-47 "Stop below next liquidity area", FR-44 target "next liquidity cluster", FR-58 partial when aggression stops at a ceiling. The one trade example is hypothetical:

> "So if I took a short from here, I would consider bringing my full take profit way lower than the low."
**Source GPS: FawPrRUGNpk | END**

4. **Context.** A directional bias first (FR-45); "you need to start with an idea" (FawPr BEGIN passage around the protection wall).
5. **BTC visibility: NO.** No order-book history (live only; bookDepth bands from 2023 are a coarse proxy, TOB s2.3). The aggression side (big trades, CVD) is visible, the liquidity side is not.
6. **Evidence.** 0 real trades (ANG R35 hypothetical).
7. **Gaps.** All thresholds UNDEFINED (FR s4). FawPr was extracted in three V1 chunks; no V2.

### FAB-8 Volume-defined fair value gap rejection
1. **Name / trader.** Fabio (FR-94 to FR-96; source o-w5Gxss6T0).
2. **What you see.** Not the candle-gap FVG: from a swing A to B, the value area (70 %) and inside it the lowest-volume price; price rejects there (rulebook paraphrase; example "24,318 to 24,317").
3. **Entry, stop, target, management.** NOT STATED beyond "price will reject" (FR-96, paraphrase).
4. **Context.** NOT STATED.
5. **BTC visibility: YES.** Swing profile and its low-volume price from aggTrades.
6. **Evidence.** 0 trades.
7. **Gaps.** Source transcript o-w5Gxss6T0 is not in raw_transcripts_canonical: no quote can be verified. Swing selection, bin size, timeframe UNDEFINED (FR s4).

### Fabio: unassigned
- ANG R31 (fZ): two "continuation short" trades that failed; setup not described: "The first trades that we took was a continuation short and we gave back two trades inside here." (fZ BEGIN, ANG R31).
- ANG R33 (jasv3L): a "trend following model" that took stops on a compression day:

> "So my trend following model took a straight stop loss."
**Source GPS: jasv3L-d8ZE | BEGIN**

  His trend-following model is never described in the transcripts we hold. FR-20 "Trend-following entry: absorption of counter-trend aggression inside momentum" (source o-w5Gxss6T0, not verified) may be it; it would then be FAB-2.
- OURS-only model: V3 model A "LVN pullback trend" (enter a pullback to a low-volume node of the breakout leg). V3 P35: "not in these transcripts (FBR:28-29)". Not a Fabio setup until a source is found.

## 5. Cross-source contradictions (both quoted or cited)
| topic | source 1 | source 2 |
|---|---|---|
| Tom R:R bar | 1.5 at 40-45 % hit rate (k0zm5NYn0IQ:549-552) | greater than 3 at 30-40 % (BVpY, TOM-2) |
| Tom P shape | "P profile exhaustion short" (ANG, T6hD) | "a P is usually something that strategically leads to a trend continuation" (T6hDJcHrVBM:161-163); GAP G06 P = accepted prices |
| Tom short side vs value | engine `below_val -> long only`; STR matrix: no counter trade in a healthy trend | T3/T3b shorts far below yesterday's value (ujedEcmvBMk:91-94, V2 s8 G2) |
| Tom counter-trade zone | STR 4.3 "Prior day VAL (for shorts)" | TOM-2 "short trades up here" at the top of a balance |
| Tom 4MoN | STR s6 breakout (ledge, speed) | ANG pullback-to-POC buying-tail long (TOM-5) |
| Fabio break-even | after the market explodes in his direction (0jM5 MIDDLE) | fast if the level FAILS, re-pivot (fZ BEGIN); FR-12 merged both (LBL s4 R3) |
| Fabio adds | "raise the exposure low in the curve" is not the best idea (8CWK, V3 P11) | loading while still at risk, funded by the day's profit (fZ, LBL D12); F7-F9 re-entries at one level |
| Fabio exit on new balance | V3 v3.0 S8(b): any new balance after entry exits | fZ: a consolidation where the OTHER side is absorbed is a hold (LBL D18; fixed in v3.1) |
| Fabio F1 label | FL `balance_failed_auction_punch_to_wall` (FAB-3 words) | 8CWK/ANG: buyers absorbed, sellers control (FAB-2) |
| Fabio R:R | FR-13 minimum 1:3 (0jM5) | FR-74 prop risk geometry 1:1 to 0.75:1, max 1.5:1 (LQvv) |

## 6. Unread sources and which gaps they could fill
From research/transcript_inventory_2026-10-09.md (counts parsed by `transcript_inventory.py`): Tom 84 raw transcripts: 11 V2,
47 V1 only (9 of them gate PASS with anchors), 26 never extracted. Fabio 8 raw, all V1 only, 0 V2. Unread Fabio sessions:
FABIO_TRADE_LEDGER.md:48 and :90.

### 6.1 Tom, never extracted (26)
| id | title (inventory) | could fill |
|---|---|---|
| uk4PZV59nYw | The PERFECT trade entry: World Champion explains his EXACT breakout setup! | TOM-6 entry trigger, stop (rank 1 by risk/stop density) |
| gFJBg8Bsw68 | Trading World Champion reveals the BEST breakout strategy in 2026! | TOM-6 trigger, speed, stop |
| Kg6sYKgtkrY | The ONLY Trading Strategy you need for 2026 (PbD Method) | PBD definitions: P, b, D shapes used by TOM-1/2/8/9 (STR gap 3) |
| jXR1afMy-3o | PbD: The World's BEST trading strategy (explained in detail) | same |
| m3IMdc7QwN4 | PbD: The BEST trading strategy for times of crisis | same; TOM-1 in fast markets |
| Ly62G168MkQ | The Simplest Day Trading Strategy for Beginners (PbD Method) | same; simple entry/stop rules |
| ODdF0Bn_KSc | Perfect trade entry: Trading World Champion reveals exact strategy! | entry triggers for TOM-1/2/4 |
| YYYuaetck_0 | The #1 Trading Strategy for the Current Market | unknown setup; rank 2 by density |
| kKZCJui4S9U | THIS strategy puts you ahead of 99% of traders! | unknown; rank 3 |
| viT_VzF5Fsw | THIS Trading Strategy Delivers MAXIMUM Win Rates NOW! | TOM-7 scalp stop/target |
| uFxYcpiaOpw | My Simplest Trading Strategy (80-90% Win Rate) | TOM-7 or a high-hit-rate setup not catalogued |
| VOiy8mAALWA | The #1 Trading Indicator for 2026 | proof items (volume/footprint) |
| ridY2Z0hSQA | THIS is the World Trading Champion's Favorite Indicator! | proof items |
| YkclL6xgu-s | How powerful is Volume Trading REALLY? | TOM-1 A-C3 "thin" in his words |
| 1utSjHs_Mq8 | The ONLY Market-Profile-Video you will EVER need | TOM-2 balance edges, single prints, tails (TOM-5) |
| K8qtT2_axPo | Market Profile: How Trading World Champions REALLY read the Market! | same |
| 0CrkbfuIhkc | Crash or All-In? THIS is What Volume Profile Tells Us NOW! | context reading, HTF value |
| lO-Iptd29t4 | The ONLY Newstrading-Video you'll EVER need | partly read by GAP (G01-G18); TOM-1 A-C4 news, TOM-8/9 |
| 6BAzqewtPUk | Forget newstrading! THIS is the strategy of the trading world champion! | TOM-1 news condition |
| 9VN9y2DVtGQ | Forget Technical Analysis! THIS is the strategy of the World Trading Champion! | unknown |
| 2xnNPIyHGQ4 | Trading World Champions show: THIS strategy wins EVERY time! | unknown |
| 4VXpUjhKG2U | How to Always Win as a Trader! (3 Mistakes Every...) | management, mistakes (entry too early, TOM-1) |
| Sy-x5AQ9-Pk | The Only Technical Analysis Guide You'll Ever Need | unknown, beginner |
| VxN5IxTwpbE | How I Would Start Trading in 2026 (Beginner's Blueprint) | unknown, beginner |
| 15JoLK0PbMU | VIX Strategy revealed | day selection / volatility context |
| cw8LWQmec1E | Gold & Silver Bubble WARNING | TL T8 gold short context |

### 6.2 Tom, V1 only (47): the ones that carry setup fields above
Every STR quote (TOM-2, -4, -6, -7) comes from V1 extracts whose gate FAILS with NO-GPS (BVpYGKz9PBU 0/35, 43JaKHRvxHk 0/25,
qLnQan0KGmQ 0/28, Ld1dhjGdTCA 0/38, NkQeOVDTAec 0/25, YmygDgtoxO8 0/22): a V2 pass of these six would re-anchor TOM-2/4/6/7 and
may give the missing stops. The trade videos themselves are V1 only (k0zm5NYn0IQ, n7ZSkjb7JXs, ujedEcmvBMk, T6hDJcHrVBM,
l8RZrBfzvp4, UOBgXV20yCM, OUM9LYwL8eA); V2 spec quotes their captions directly. Scalping videos G0CiJcuXCRs and YVUcLTsCOZI
(V1, no anchors) are the best source for TOM-7 stops. oa8kxSLLkAo (footprint, 0/27) for TOM-1 A-P6 footprint reading;
Vd83oo_geMk (heat map, 0/42) for Tom's view of FAB-7-type liquidity; 3o1VVsfBmmU ("The #1 Trading Setup for 2026", 0/34; ANG R25
"10 ticks" stop example) may name a setup not catalogued here; yRvMW6lgN1o (TOM-3) and gWjHq5UMisY / hQ8sOq67x5o / pgdmKLJ0hhA
(highest risk/stop density, V2 candidates per the inventory) for swing setups not catalogued here.

### 6.3 Fabio (8 raw, all V1; plus videos without raw transcripts)
| source | state | could fill |
|---|---|---|
| 0jM5Y31YJak, 8CWKfoSJu3c, jasv3L-d8ZE | V1 only; applied readings in FTM/V3 | a line-by-line pass like LBL for each: initial stop words for FAB-1/2/3, the "trend following model" (ANG R33) |
| FawPrRUGNpk | V1 in three chunks | FAB-5 and FAB-7 stop/target words (FR-43, FR-47 verbatim) |
| LQvv5xgy_ik | V1 | FAB-6 IVB rules beyond one sentence |
| 0KyIEdvVKMQ, StaphlRH8NQ | V1 | mental models; FR-80..85 (non-MTS hypotheses) |
| fZlNGWvd2Ko | V1 + LBL (read line by line) | done |
| o-w5Gxss6T0 | extract exists, no raw transcript | FAB-4, FAB-8, FR-16..20, FR-93..96: needs the transcript |
| 9IliXww64uM, Jpd96fLqr5M, DyS79Eb92Ug, gLHd20jE8UQ | frames read, captions on F: only (not in raw_transcripts_canonical) | FAB-4 and FAB-5 words; big-trade size filter ("30 to 40 on NQ", gLHd slide, FL:50) |
| 9I5vTvwsMBk | not downloaded (f398 not available, FL:48) | unknown live session |
| Is1HvdfQm5c | 2.5 h; only t=0-500 read (FL:90 and CSV) | "Live Charting" and "Execution Method Trick" agenda items: entry/stop rules |
| xUyqIjCfZzg | 3.8 h; unread (FL:57) | live session: more FAB-3/FAB-5 trades |

## 7. What this catalog does not settle (for the next steps)
1. Initial stop in words: Tom 3 of 10 setups, Fabio 0 of 8. Every other stop is a chart point ("here") or a frame value. The blind eye-read marking should record where each reader would put the stop and the next extraction should search for it.
2. Session anchors on BTC (cash open, pre-market, US open, closing auction) are needed by TOM-1, TOM-8/9/10, FAB-6. Any choice is OURS.
3. Two setups are mostly our structure (FAB-4, FAB-8) and one is only ours (V3 model A).
4. Real-trade evidence is concentrated: TOM-1 16 of Tom's 21 and FAB-5 11 of Fabio's 17 assigned trades; TOM-2, -4, -6, -7, -9, -10 and FAB-6, -7,
   -8 have none.
