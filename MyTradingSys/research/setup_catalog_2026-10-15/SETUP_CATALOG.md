# SETUP CATALOG: every trade setup Tom and Fabio describe, in plain chart terms (2026-10-15)

Status: consolidation of what the repo already holds, extended 2026-10-15 by a line-by-line pass over the 26 never-extracted Tom
transcripts (batches 1-3: all 26 read, section 6.1a). Before that pass: no new extraction, no test design, no fees, no stop-size math, no
backtest, no VALIDATION/HOLDOUT read. Operator decision 2026-10-15: identify all bare setups first (what the naked eye sees on a
BTC chart and how the trader applies it) before any further test design. This file is the base for: filling gaps from unread
transcripts, blind eye-read marking on BTC charts by two readers, then stops/fees/code. Fable 5.1 audits it against raw
transcripts on 2026-10-20.

Revision 2026-10-16 (Fable 5.1 audit `fable_audit_2026-10-16/CATALOGUE_AUDIT.md` section 5, corrections P1 + P2 and decision D3; session `catalogue-p1-p2`). Fixed: three wrong rows (TOM-3 target and stop, FAB-5 stop,
FAB-4 rewritten from 9IliXww64uM) and the stale fields (TOM-4 stop, the "Fabio 0 of 8 stops" tally, the TOM-1 count, the FAB-5 row count). Added: 2 setups and 6 rules (T-1 = TOM-17; F-1 = FAB-4 and the FAB-1 breakout
rule; F-2 = stop in FAB-5, big-trade filter, named models, session rules in sections 2.2/4; T-2 and T-3 = sections 2.1 and 5). Structure (D3): TOM-5 merged into TOM-4, FAB-3 into FAB-2, TOM-1 split into TOM-1a/1b,
TOM-13 moved to section 2.3, FAB-7 moved to section 4.1. Old ids stay as alias headings or map rows (section 1), so no ledger row, ANG row or trade loses its place. P2: `9IliXww64uM` and `DyS79Eb92Ug` are now canonical
transcripts, so their quotes are gate-checked block quotes. Not done here (other audit corrections): the OURS definition page (P3), the G3 window design (P4), the plan edits (P5-P7).

How to read the quotes
- Block quotes `> "..."` + `**Source GPS: <id> | BEGIN/MIDDLE/END**` are checked against `raw_transcripts_canonical/<id>_raw.txt` by `python scripts/dev/verify_extract_quotes.py` (verbatim after case/punctuation normalising, position third).
- Inline quotes `"..." (<id>:<a>-<b>)` cite caption lines of `F:/MTS/data/tom_videos/<id>.txt` and are checked by `python scripts/dev/check_spec_quotes.py`. All of them are copied from TOM_LAYER_V2_SPEC.md (already checked there).
- `(paraphrase)` or `(ledger, frame)` = not a verbatim quote; a frame value read from a video by an earlier session.
- Captions are AI-translated (Tom) or auto-captions (Fabio): a quote proves what the trader says he looks at, never a price, date or time.
- NOT STATED = the trader gives nothing in words (often he points at the chart: "here", "up here"). Nothing is filled in.
- OURS = a number or rule an earlier spec or engine added (judgement or tuned). Listed per setup, never presented as his.
- Fabio `9IliXww64uM` and `DyS79Eb92Ug` are canonical since P2 (2026-10-16; converter and check output in `evidence/vtt_to_canonical.py`, `evidence/vtt_to_canonical_output.txt`). Their block quotes carry the canonical
  line and the [m:ss] stamp after the GPS tag, e.g. `(DyS79Eb92Ug_raw.txt:1453-1454, [56:53])`. DyS79 is built from the `.en.vtt`: the flattened `DyS79Eb92Ug.txt` the audit read omits about 266 words (back-channel
  "mhm"/"yeah" and a few short clauses); the audit's `t` seconds equal the stamps to within a few seconds. The other four Fabio vtt files (0jM5Y31YJak, 8CWKfoSJu3c, fZlNGWvd2Ko, jasv3L-d8ZE) match their canonical copies word for word (100 %).

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
| TOM-1a | Intraday counter trade at the top of an unhealthy push ("no liquidity left"; imbalance fade) | Tom | a fast push from the session start far above prior value, thin profile at its top, the push stalls and sellers show, short back to the volume below | Y | PARTIAL | 11 assigned examples incl. 1 candidate (10 ledger groups + T8 candidate) |
| TOM-1b | Swing counter trade: B-profile top after a run, or rejection back to value after a gap (daily bars) | Tom | an earnings run or short squeeze ends in a B profile at the top (or an open far above the prior day is rejected), short with the stop above the level, target the value below | Y | YES (gap part NO) | 5 assigned examples (ANG R1, R2, R16; R4, R5 open) |
| TOM-2 | Counter trade in balance ("short trades up here and long trades down here") | Tom | sideways market, sell the top and buy the bottom of the balance, b-profile / lower balance as the proof | Y | YES | 1 (viT_, lost; + 1 plan, ANG R24) |
| TOM-3 | Limit sell below the last volume step | Tom | trend flattening into a range, an inside day at the high, a resting sell order just below the last volume step of the profile, target last week's POC / the smart-support zone below | Y (location rule: not above the high, at the largest footprint volumes; no price) | YES | 1 (ANG R13) |
| TOM-4 | Trend continuation pullback (incl. the former TOM-5: pullback long into value after a buying tail) | Tom | healthy trend with volume behind it, price pulls back to VWAP, a fair zone or the prior-day POC after a buying tail, buyers aggressive, buy with the trend, target the next high-volume area / value high / the ledge above | Y (below the last volumes) | YES | 3 assigned examples (former TOM-5: ANG R6, R7, R17) |
| TOM-6 | Breakout / break-in | Tom | a balance or overlap zone resolves, a ledge above old highs, speed picks up and buying shows, enter or add at the break | N | YES | 0 (adds inside TOM-4, former TOM-5) |
| TOM-7 | Scalp in balance around VWAP | Tom | flat VWAP, no trend day from the open, shorts at the top and longs at the bottom of ranges around VWAP | N | YES | 0 |
| TOM-8 | Gap close (incl. Monday gap pullback long) | Tom | the open is far outside the prior day with no news, a failed extension, range, liquidity returns, trade back into the gap / prior value | N | NO | 1 (TL T4) |
| TOM-9 | Gap not closed: trade with the trend | Tom | the gap holds, prices are accepted (P shape), liquidity returns: trade in the gap direction | N | NO | 0 |
| TOM-10 | Closing-auction gap reversal | Tom | a very strong close with a closing-auction extreme, next day opens back in the red: contrarian | N | NO | 0 |
| TOM-11 | Cross-market lead: crude oil reacts first, index future follows | Tom | two charts: a level is hit in crude oil, crude reacts for seconds, the index future lags and is bought/sold early | N | NO | 0 |
| TOM-12 | Break-in: price returns into the old balance after outside prices fail to hold | Tom | P or B outside the old value area with no volume base, then a fast return inside, enter the pullback with the move, target the start of the outside impulse | N | YES | 0 |
| TOM-14 | After a news shock: counter trade back to the origin of the move (V reversal) | Tom | a fast news move with no base, an inside bar, then a reaction back toward where the shock started | N | PARTIAL | 0 |
| TOM-15 | Candle formations at a range edge: three in a line, inside bar, outside bar | Tom | after a compression or at a support/resistance area: three same-colour candles, an inside bar after an impulse, or an outside bar that clears both sides | N | YES | 0 |
| TOM-16 | Top after forced hedger buying: short when the large volumes break down | Tom | price and volume far above average, large volume at the high, an aggressive seller appears, trade the break below the last big buyers | N | PARTIAL | 0 |
| TOM-17 | Low-volume-node scalp decided by market speed (order-book scalp) | Tom | price ticks into a low-volume price range: if it goes through and stalls it runs back to the high volume ("lethargic back and forth"), if it runs through at constant high speed with big participants active it continues | N | PARTIAL | 0 |
| FAB-1 | Balance with CVD pressure, break on volume ("sell model day") | Fabio | flat balance while CVD runs hard one way, first candle where price follows the volume out of balance with big trades | N | PARTIAL | 1 (FL F2) |
| FAB-2 | Absorbed push, rewarded effort ("punch to the wall"), incl. the failed auction of one side then the other side's aggression at the level (former FAB-3) | Fabio | one side's aggression hits a wall (big delta, no price result), the other side's aggression moves price: trade with the side that gets the result; variant: consolidation where one side was absorbed, then the other aggresses at that level | N (chart point) | PARTIAL | 3 (FL F1; F3c, F5) |
| FAB-4 | Failed breakout back into balance (reversal at the edge of the previous day's value area) | Fabio | a probe out of the previous day's value area fails: volume on the way out and back, delta against the price result, the 5-minute closes back inside; trade to the other side of the range | N (chart point: "somewhere above here") | YES | 2 (FL F4a, F4b; assignment weak; the video has 3 trades) |
| FAB-5 | Buyers protect a level (value-area low / gap / wall): long, squeeze trapped sellers (his names: "AAA setup", "value area low fade") | Fabio | price comes down to a level, buyers defend it (absorbed selling, protection wall), long with a small stop below the protection level, re-enter if it fails | Y (below the protection level; no distance) | PARTIAL | 11 (FL F3a, F3b, F6-F14) |
| FAB-6 | IVB: first 30 minutes of the US open | Fabio | the first 30 minutes' range sets the day's direction; trade the break of it | N | PARTIAL | 0 |
| FAB-8 | Volume-defined fair value gap rejection | Fabio | the lowest-volume price inside the value area of a swing; price rejects there | N | YES | 0 |
| FAB-9 | Delta print zone: reload where the previous swing leg's big trades, delta and value area high overlap (added 2026-10-18, 06R-ebyOhDI) | Fabio | trend day, price returns to the zone, aggressive orders print again, stop beyond the zone | Y (location: beyond the area) | PARTIAL | 0 (2 shown, no prices) |
| FAB-10 | Volume ledge plus absorbed counter-traders: limit order at the retrace (added 2026-10-18, 06R-ebyOhDI) | Fabio | volume falls from a peak node to a low node fast, the candle body shows aggressive trend-side orders and absorbed counter-side | N | YES | 0 |

Moved or merged 2026-10-16 (D3): TOM-5 -> TOM-4 (worked example), TOM-13 -> section 2.3 (routes and targets, not a setup), FAB-3 -> FAB-2 (variant), FAB-7 -> section 4.1 (heat-map tool family, not a setup),
TOM-1 -> TOM-1a + TOM-1b. TOM-6 and TOM-12 are one family (he files the break-in as "variant one for a breakout", gFJBg8Bsw68): read them together; the rows stay separate.

Counts (revised 2026-10-16): Tom 16 setup rows (TOM-1a, 1b, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17), 5 with a stop location stated in words (TOM-1a, TOM-1b, TOM-2, TOM-3, TOM-4; TOM-3 gained its rule from
yRvMW6lgN1o, TOM-4 from YkclL6xgu-s; no stop price or distance is stated as a rule anywhere) plus the generic "below the last liquidity" for any level entry (section 2.1, T-2); BTC visible YES 8 / PARTIAL 4 / NO 4.
Fabio 6 setup rows (FAB-1, 2, 4, 5, 6, 8), 1 with the initial stop location stated in words (FAB-5: below the protection level, DyS79Eb92Ug); the earlier "0 of 8" was wrong. The FAB-1, FAB-2 and FAB-4 initial stops are
chart points ("here"), not rules; the FawPr lecture gives below-reload and below-next-liquidity stops for the heat-map variants (section 4.1). BTC visible YES 2 / PARTIAL 4 / NO 0.
Real trades are "assigned examples", not certified executions: Tom 22 assigned (TOM-1a 11 incl. the T8 candidate, TOM-1b 5, TOM-2 1 (viT_, lost), TOM-3 1, TOM-4 3, TOM-8 1) + 1 unassigned (ANG R20) + 2 anti-examples;
Fabio 17 FL entry rows assigned (F1, F2, F3a-c, F4a-b, F5, F6-F14; F15 never filled: FAB-1 1, FAB-2 3, FAB-4 2, FAB-5 11), 2 unassigned trade groups (ANG R31, R33).

## 1. Duplicate map (one setup, many file names)

| setup | names used in the files |
|---|---|
| TOM-1a / TOM-1b | V2 family A "imbalance fade", entry paths A1/A2/A3, "re-entry" (management A-M5); TL `spike_fade`, `spike_fade_candidate`, `re-entry after stop`; STR s4 "Counter-Trade", variant 4.2B "Trend Extreme With Proof of Exhaustion"; ANG "counter trade at highs, no liquidity above", "B setup/B profile pullback after a failed push into no-liquidity highs", "P profile exhaustion short", "short-squeeze fade", "gap exaggeration close"; GAP G19-G22 "gap-fade trade (exaggeration)"; TOB s2.2 "session extreme of an oversized impulse leg"; engine `ct_short`, `SpikeFadeDetector` `fade_short`. Split 2026-10-16 (D3): TOM-1b = ANG R1, R2 (Avis, tS6ZEiHj8gQ), R16 (Nvidia, OUM9LYwL8eA) and the kXhI rows R4, R5 (post-gap rejection to value); every other name in this row is TOM-1a |
| TOM-2 | STR s3 matrix row "Balance / prior day VAH/VAL/VPOC -> Counter-Trade", s4.2A "Primary: Balance Market", 4.4A "B Profile = Weakness", 4.4D "Lower Balance After Rejection = PBD Logic"; ANG R24 (plan) |
| TOM-3 | ANG "limit sell below the last volume step (yRvM)", "smart S/R zone; inside day at ATH" |
| TOM-4 | STR s5 "Execution mode: Trend-Continuation"; TOB s2.5 "Trend continuation: pullback to a fair zone"; engine `tc_long` (VWAP); absorbs the TOM-5 names below (D3) |
| TOM-5 (merged into TOM-4, worked example) | ANG "pullback to prior-day value/POC with buying tail for longs (4MoN, UOBg)", "buy at prior-day value area / VPOC zone" (crude R6), "re-entry on buyer stability" (R7). STR files the same 4MoN video under s6 breakout (ledge, speed) |
| TOM-6 | STR s6 "Breakout", "breakin or breakout"; TOB s2.5 "Breakout / break-in" |
| TOM-7 | STR s7 "Scalp"; TOB s2.5 "Scalp in balance"; engine `scalp_long`/`scalp_short` |
| TOM-8 | V2 family C "gap-close pullback long"; TL `gap pullback`, `breakout_pullback_teaching` (T9 = alias of T4); ANG R12 "gap + P profile + pullback buy signal"; GAP G05, G09, G14, G15 |
| TOM-9 | GAP G06 (accepted prices = P), G11, G16 |
| TOM-10 | GAP G23 |
| TOM-11 | none before 2026-10-15 (YYYuaetck_0, never extracted) |
| TOM-12 | TOM-6 "breakin" (undefined there); V2 A3 "P that fails back inside"; PBD "break-in" (m3IM, jXR1, gFJB, Ly62) |
| TOM-13 (section 2.3, not a setup) | "route planning" with market profile (1utSjHs_Mq8, K8qtT2_axPo); single prints, double distribution, weak highs/lows; target/location rule used by TOM-1a, TOM-2, TOM-4, TOM-12 |
| TOM-17 | "The real scalping strategy" (G0CiJcuXCRs): order-book / low-volume-node scalp decided by market speed; not TOM-7 (VWAP range scalp). Added 2026-10-16 (audit T-1) |
| FAB-1 | FTM s1 "the trade (both videos teach the same one)"; V3 S1+S2+S5 and model A trigger; FR-10, FR-11; FL `balance_distribution_breakout_short`; ANG R26-R27 "CVD distribution + big trades + price follow-through", "continuation in redistribution phase; sell model day" |
| FAB-2 | FTM s1 step 3 "punch to the wall"; FR-16, FR-20, FR-22; FL F1 `balance_failed_auction_punch_to_wall`; ANG R28, R29; V3 S3 ABSORBED/CONTROL |
| FAB-3 (merged into FAB-2, variant) | V3 model D "failed-auction breakout" (S5D); LBL T2 and M4; FR-19, FR-86, FR-88; FL `failed_auction_reentry...`, `failed_auction_short_rewarded_effort...`; ANG R32, R34 |
| FAB-4 | V3 model B "failed-breakout reclaim, mean reversion" (cites FR-19, FR-86); FL F4 (`hand-drawn schematic at t=780: balance -> failed breakout -> reversal`); his own words now in 9IliXww64uM ("failed breakout", "clear failed auction", "qualify a breakout"), P2 canonical |
| FAB-5 | FL `protection_wall_buy_reversal`, `value_area_low_reaction_long_scale_in`, `protection_level_squeeze_long`, `chase_long_after_squeeze`; FR-35, FR-63, FR-67, FR-68; his names in DyS79Eb92Ug: "the AAA setup", "value area low fade", "model B testing of the value area after their expansion" (which of his models equals which row beyond AAA / value area low fade: NOT STATED) |
| FAB-6 | V3 model C "IVB, first 30 minutes"; FR-81 "Opening range breakout has positive skew" |
| FAB-7 (tool family, section 4.1, not a setup) | FR-17, FR-31 to FR-73 (heat-map family, L2); ANG R35 |
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
| A-M7 | (T-2) stay in while liquidity is traded quickly and aggressively your way; after the book goes quiet stay out until the market speed picks up again | see the T-2 quotes below (3o1VVsfBmmU) |

Added 2026-10-16 from the V1-only videos `3o1VVsfBmmU` and `hQ8sOq67x5o` (audit T-2, T-3; Tom Vorwald, the speaker of both).

**Stop and target for any level entry (T-2, 3o1VVsfBmmU, "The #1 Trading Setup for 2026").** The only general stop statement in his words; the catalogue's A-M table has none. The 10-tick example is his illustration, the profit side of
the example (about 70 ticks) is read from the video and not block-quoted:

> "all right my stop loss belongs below the last liquidity."
**Source GPS: 3o1VVsfBmmU | MIDDLE**

> "My takerit goes to the predefined price area from this intelligent support resistance element that I analyzed and I just let it run."
**Source GPS: 3o1VVsfBmmU | MIDDLE**

> "my stop loss in this case let's say is 10 ticks"
**Source GPS: 3o1VVsfBmmU | MIDDLE**

> "with a riskreward ratio of 1:7, you can have a hit rate of less than 20% and still make money"
**Source GPS: 3o1VVsfBmmU | MIDDLE**

Management by market speed (new rule A-M7, in the table above): stay in while liquidity is traded your way, stay out when the book goes quiet:

> "as long as liquidity is being traded quickly and aggressively in your direction and you see the surplus is there you stay in"
**Source GPS: 3o1VVsfBmmU | END**

> "Now all of a sudden you see in the book that nothing is happening anymore"
**Source GPS: 3o1VVsfBmmU | END**

> "the market speed picks up for you again"
**Source GPS: 3o1VVsfBmmU | END**

His top-down order in six steps (paraphrase of the video): quick watch by closing prices -> weekly market and volume profile, single prints, VPOC -> daily profiles to see where strong hands give up -> transfer to the
5-minute chart -> a fair/unfair check -> footprint timing (step 6 is the order book). The ODdF0Bn_KSc chain under TOM-4 has three of the six steps. The fair/unfair check in his words:

> "is there acceptance through real trading volume or does the market lack liquidity down here"
**Source GPS: 3o1VVsfBmmU | MIDDLE**

**Hit rates and payoffs by setup type (T-3, hQ8sOq67x5o, his metrics video; SOURCED, his claims, untested).** These sit in section 5 as a contradiction row. Breakout and trend-phase trades are said to win often with a small
payoff; the intraday swing trader accepts a low hit rate for a payoff about four times the risk; counter trading is quoted at a payoff of three to four with long losing streaks; the account-level rule is a 20 % maximum drawdown.
Read the surrounding passage before pairing a number with a row.

> "High win rates, 75% typical for breakout trades"
**Source GPS: hQ8sOq67x5o | MIDDLE**

> "a win rate of 35%"
**Source GPS: hQ8sOq67x5o | MIDDLE**

> "your stop loss is, for example, 10 points, and your profit target is 40 points"
**Source GPS: hQ8sOq67x5o | MIDDLE**

> "16 individual losses one after another"
**Source GPS: hQ8sOq67x5o | MIDDLE**

> "usually in the range of three to four"
**Source GPS: hQ8sOq67x5o | MIDDLE**

> "12 or 13 losses in a row"
**Source GPS: hQ8sOq67x5o | END**

> "never have a strategy that has a drawdown of more than 20%"
**Source GPS: hQ8sOq67x5o | BEGIN**

Caution: the canonical transcript of hQ8sOq67x5o introduces the speaker with a garbled name field ("I'm Tom Hougaard", an AI-translation error; the names that follow are the trade-the-traders names, so the speaker is Tom Vorwald):

> "I'm Tom Hougaard"
**Source GPS: hQ8sOq67x5o | BEGIN**

### 2.2 Fabio: management he states (all his setups; the initial stop is a chart point everywhere except FAB-5, where DyS79Eb92Ug gives its location)
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

**Scope of the day rules (card catalog-audit-fabio-risk-scope, GPT H2).** The quotes above on "floor at day P&L 0", "risking only the profit of the day" and "if we go back to break even, we stop the session" are the
rules of the fZlNGWvd2Ko session (a session he planned as a profit run); they are not a condition of every Fabio trade. In jasv3L-d8ZE he enters F5 after a losing start:

> "We are at $9,000 in draw down for the day."
**Source GPS: jasv3L-d8ZE | BEGIN** (jasv3L-d8ZE_raw.txt:34-35, model took a straight stop loss. We are at  ])

and in DyS79Eb92Ug (added 2026-10-16) he states day-level limits in dollars, a different rule, also session-scoped (his words, NQ, 2.4 h live session):

> "the maximum draw down that I accept for the day is 10,000."
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:90-92, [3:16])

> "if I get the 20,000 profit for the day my rules say it's done because probably you will have consolidation after a strong move."
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:630-633, [25:10])

> "My rule was three losing trades to stop is exactly what we did here"
**Source GPS: DyS79Eb92Ug | MIDDLE** (DyS79Eb92Ug_raw.txt:2013-2015, [1:19:13])

**Big-trade filter (F-2b, SOURCED, NQ).** The size of a "big trade" bubble is his own number, not OURS (the gLHd slide "30 to 40 on NQ" is a different presenter's slide about Fabio: SECONDARY_NOT_SOURCED, H6; the SOURCED words are the quote below, 30 contracts, London 20). The BTC equivalent stays OURS (the 99th-percentile rule of V3):

> "What was the minimum contract? >> Always the same. It's 30 contracts. >> If you are in London, I use 20."
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:682-684, [27:14])


### 2.3 Routes and targets (was TOM-13, not a setup): single prints and the gap between two POCs get revisited
1. **Name / trader.** Tom, no name of his own; "route planning" with market profile (1utSjHs_Mq8, K8qtT2_axPo). Not a stand-alone entry: he says so. Moved out of the setup list on 2026-10-16 (D3): it is a target/location rule that other setups (TOM-1a, TOM-2, TOM-4, TOM-12) use.
2. **What you see.** A single print area (a price range the market stayed in for one 30-minute block only) or a double distribution day (two profiles with two POCs and a low-volume gap between them, single prints in between), or weak highs/lows (several letters at one price) next to strong tails. Strong tails come from strong participants, weak highs/lows from weak ones.

> "Such price ranges are often revisited to see if that strong market participant still reacts."
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

> "The probability is very high that these will be taken out again because weak price areas are initiated by weak traders"
**Source GPS: 1utSjHs_Mq8 | MIDDLE**

> "in between them no fair prices have ever been traded"
**Source GPS: K8qtT2_axPo | END**

3. **Entry, stop, target, management (his words).**
   - Entry: NOT STATED (this is a context rule, not a trigger).
   - Stop: NOT STATED. Target: the unfair prices are filled.

> "it will try to fill in these unfair price levels here"
**Source GPS: K8qtT2_axPo | END**

> "This is not a self-contained trading strategy but rather a root planning that we have to and can carry out with this."
**Source GPS: K8qtT2_axPo | MIDDLE**

   - Management: NOT STATED.
4. **Context he requires.** Profile type: single prints make it a trend profile; two POCs with a gap make a double distribution. If the market re-enters an old value area and is accepted there, the profile is traversed (1utSjHs_Mq8, paraphrase). The volume profile must be laid over the market profile to see whether time and volume disagree.
5. **BTC visibility: YES.** 30-minute profiles of klines, single prints and POCs; volume from aggTrades. Letter-count rules are his; the 30-minute block is his, the BTC session boundary would be OURS.
6. **Evidence.** 0 trades. Chart illustrations only.
7. **Gaps.** Entry, stop, time frame to wait, how many revisits before the level is spent: NOT STATED. Overlaps with TOM-8 (gap close) in meaning: here the empty zone is inside a profile, there it is between two days.

## 3. Tom setups

### TOM-1a Intraday counter trade at the top of an unhealthy push (imbalance fade)
Split 2026-10-16 (D3, audit 4.2): TOM-1a is the intraday model (needs a BTC session anchor, OURS, and intraday panels). The swing and gap examples that used to sit here are TOM-1b below.

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
4. **Context he requires.** A push without volume under it and without a fundamental story: "especially if there's no fundamental sustainable story" (l8RZrBfzvp4:87-89); other markets not confirming: "if for example fundamental news had led to one market being extremely strong and the other not then that's a different story" (T6hDJcHrVBM:291-294). Many proofs against the trend: "If you make trades against the trend, then you need many, many parameters that speak in your favor" (zQTbdEweG3c:23-26); no count given. Session: DAX pre-market and cash open, "the market phase where the highest liquidity is present between 8:30, 9:00 and 17:35" (T6hDJcHrVBM:94-97); pre-market with less size. Do NOT fade when volume builds above: "if the market were to accumulate large volumes there then yes I would definitely be looking for a long position" (k0zm5NYn0IQ:357-360); not on a true breakaway gap: "we're not at the all-time high and didn't gap out of a range" (zQTbdEweG3c:87-89). Direction is set for the day in advance: "The direction you want to take for the day must be predefined and that can change if the context breaks" (ujedEcmvBMk:277-279).
   - Added 2026-10-15 from never-extracted videos (batch 1, section 6.1a), context filter and proof wording (VOiy8mAALWA): the value centres (VPOCs) decide whether counter trades are allowed.

> "if they shift upward overlapping each other stop doing counter trades"
**Source GPS: VOiy8mAALWA | MIDDLE**

> "after two higher and two lower Vpo following a balance phase, I shouldn't be taking counter trades anymore"
**Source GPS: VOiy8mAALWA | END**

> "And during such trend phases, you should never use counter trading mechanics for yourself."
**Source GPS: VOiy8mAALWA | MIDDLE**

> "But of course, even better are counterrading setups in terms of volume, in terms of being able to see in the footprint chart that liquidity is gone. I have a finished auction or something similar."
**Source GPS: VOiy8mAALWA | END**

   His test for "real" flow: is the shift accompanied by genuine volume at the higher prices, or does the bulk of the money still sit lower (footprint). The count "two" is his (VOiy), "two higher" read as VPOC shifts day over day; whether it carries to BTC UTC days is OURS. This tightens the "healthy vs unhealthy" gap below (item 7) from volume-under-the-move to value-centre shift; both are his.

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
6. **Evidence.** 11 assigned examples incl. 1 candidate, not 11 certified executions: 10 TL groups (T1, T2, T2b, T3, T3b, T5, T6 = T10, T7, T11, T12; V2 s5 maps each to family A; T11/T12 from frames only) + TL candidate T8 (gold, entry not shown, row_kind ENTRY_CANDIDATE). ANG R8-R11, R14, R15, R18, R19 are TL T6, T3, T3b, T5, T2, T2b, T1, T7 and are not counted twice. The five ANG rows not in TL (R1, R2, R4, R5, R16) are TOM-1b; with them the old total of 16 is "assigned examples incl. candidates" (GPT M10: not a recall denominator). Three of five design sessions also show a losing first attempt that is not a ledger row (V2 s3).
7. **Gaps and contradictions.**
   - P shape: ANG names T6hD a "P profile exhaustion short", but in the same video Tom says "a P is usually something that strategically leads to a trend continuation" (T6hDJcHrVBM:161-163). V2 resolves it as a P whose upside breakout fails ("a P pattern formation with a so-called fake breakout and a renewed acceptance of this balance", T6hDJcHrVBM:220-222).
   - Healthy vs unhealthy: STR s3 (reconstructed matrix, not his table) makes counter trades invalid in a healthy trend and the old engine blocked the fade in `trend_healthy`; Tom's test is volume under the move ("The idea was that this trend isn't entirely healthy" + "there was simply no liquidity left here and the liquidity was down here", zQTbdEweG3c:231-232, 234-236), not position against value (V2 s8 G2/G3).
   - R:R: 1.5 at 40-45 % hit rate (k0zm5NYn0IQ:549-552) vs greater than 3 at 30-40 % (BVpY, TOM-2 below). Both his.
   - Proof count: NOT STATED ("many, many"); the old engine's 3 proofs are OURS.
   - kXhI R4/R5 moved to TOM-1b (post-gap rejection to value: TOM-8/GAP G19 and TOM-2 territory, open).
   - OURS from older specs (never his): opening-range size as rank above the median of 20 prior sessions; "thin" = top third volume below each lower third; 5-minute inside bar (only chart he names, paraphrase n7ZSkjb7JXs:290-293); proof count k*; order types (A1/A2 limit, A3 stop-market); 1 lot, no partial, no add; at most 1 re-entry per session; flat at 17:35; session start 07:00 Berlin; A-C2 coded as close above the prior day's HIGH (stricter than his words); A-S1 = lowest prior session high above the zone; A-P5 = high above 20 daily highs; BTC minimum stop width 0.40 % (V2 s11-s16). Old engine: 3 proofs, volume spike 2x over 240 bars, CVD-divergence "unhealthy", 8-bar timeout, 0.1 % stop floor, 2-3.5R target window (TOB s2).

### TOM-1b Swing counter trade: B-profile top after a run, or rejection back to value after a gap (daily bars)
1. **Name / trader.** Tom. Split out of TOM-1 on 2026-10-16 (D3): the same idea (a stalled push, sellers show, short back to the volume below) on daily or swing bars and on one gap open, with none of the intraday session-start, pre-market or 5-minute-panel elements of TOM-1a.
2. **What you see.** A run (an earnings run, a short squeeze) ends in a B profile at the top; or the open is very far from the prior day and is rejected at the high; price goes back toward value. The B profile is the proof in his words (below); a new low under the last range sets the next short.
3. **Entry, stop, target, management (his words).** Stop above the level (tS6Z: entered at 640, stop at 730), a limit order that is placed again when the first one is picked up (kXhI), target value or the next lower range (kXhI, OUM9):

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

4. **Context he requires.** The shared TOM-1a filters (item 4 above) apply in spirit; none is restated in these three videos. The gap case needs a cash session.
5. **BTC visibility: YES on daily bars for the B-profile top** (the B-profile definition is not in his words: write the OURS rule before marking, audit 4.3), **NO for the gap case** (no BTC gaps).
6. **Evidence.** 5 assigned examples, none certified executions: ANG R1, R2 (Avis, tS6ZEiHj8gQ), R16 (Nvidia, OUM9LYwL8eA), R4 (ES, kXhIAug0Gh8), R5 (NQ limit order, kXhI; ambiguous with TOM-2). R4 and R5 stay "open": the ES trade sits after a gap away from the prior day (TOM-8/GAP G19 territory) and R5 is "the same game" after a balance (TOM-2 territory).
7. **Gaps.** B-profile definition, stop distance, entry trigger beyond "after the rejection": NOT STATED.

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
   - Added 2026-10-15 from never-extracted videos (batch 1, section 6.1a), one taken trade that failed, with the exit rule in his words (viT_VzF5Fsw; DAX-type index, prepared levels = prior-day value area and a single-print rejection):

> "I had booked a wonderful short trade and then held the position there. I was of the opinion that we could close the market opening and the gap from the previous day."
**Source GPS: viT_VzF5Fsw | MIDDLE**

> "I absolutely should have given up the position up here because we completely traded through and accepted this balance here."
**Source GPS: viT_VzF5Fsw | MIDDLE**

> "It's not a good idea to then continue to hold on to the counter trade."
**Source GPS: viT_VzF5Fsw | MIDDLE**

> "For me, point one, where I went short was initially just a target area, not a real entry area."
**Source GPS: viT_VzF5Fsw | END**

> "Secondly, the volume kept increasing, which means the acceptance of market participants kept going higher."
**Source GPS: viT_VzF5Fsw | END**

> "Thirdly, although the delta showed that a lot was being sold, the market continued to rise."
**Source GPS: viT_VzF5Fsw | END**

> "I decided that I would try to take the opposite position."
**Source GPS: viT_VzF5Fsw | END**

   Reading: the invalidation is a state, not a price: the market trades through the balance he sells and accepts it (volume rising at higher prices). It is a counter-trade exit (TOM-1/TOM-2 family), no distance or tick stop is given. After it he flips long (a break-in of acceptance, TOM-12). The sell zone was "a target area, not a real entry area": a level alone is not an entry. Assigned here (counter trade at prepared levels; target = gap close, so TOM-8 overlaps; TOM-1 overlaps as a counter to the trend). Open.

5. **BTC visibility: YES.** Balance, VAH/VAL/POC, b-profile, lower balance, VWAP: computed from klines/aggTrades. Volume coming in: aggTrades.
6. **Evidence.** 0 real trades. 1 plan (ANG R24, illustration). kXhI R5 is a possible instance (assigned to TOM-1, open).
7. **Gaps and contradictions.**
   - Zone side: STR 4.3 lists "Prior day VAL (for shorts) or VAH (for longs)" and quotes "look here is yesterday's value area low and maybe that's where the VPOC is. First in terms of price range if I see that the market is below that then I can definitely try a short trade" (BVpY, STR TOM-145): a short BELOW value low is not a fade of the balance top. Which one is the setup is open; the quote is not verified here.
   - "B profile" has no definition in his words (STR s10 gap 3); PBD logic is taught in never-extracted videos (section 6).
   - When balance turns into breakout (TOM-6): NOT STATED (STR s10 gap 9).
   - Stop tighter "depending on the setup" (STR 4.7, BVpY): no rule.
   - OURS: engine `ct_short`/`ct_long` at VAH/VAL zones and the "3 proofs" bar.

   - Added 2026-10-15 from never-extracted videos (batch 3, section 6.1a), the counter-trade rule and its proof (4VXpUjhKG2U, VxN5IxTwpbE). No stop, no target distance: NOT STATED.

> "you go short at the top and long at the bottom and that's it and everything in between is just noise"
**Source GPS: 4VXpUjhKG2U | MIDDLE**

> "But what does it look like at the top? Do I have unfinished auctions there or do I have finished auctions, meaning completed auctions?"
**Source GPS: VxN5IxTwpbE | END**

> "Now I'm gathering the necessary proof whether it actually makes sense to do a counter trade here."
**Source GPS: VxN5IxTwpbE | END**

   Wording slip in VxN5IxTwpbE: "phase two is counter setups and phase one is breakout setups" (raw) contradicts the same passage (counter trades work in the 70 % balance phase, breakouts in the 30 % trend phase). Read as balance = counter, trend = breakout, like every other video; the slip is recorded here, not used.

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

   - Stop: not a price. He gives the selection rule (GPT H1, confirmed at the source by the Fable audit): not above the high, and at the level where the largest volumes occurred on the footprint chart, "the perfect level where we should abandon our trading idea". The exact price is NOT STATED; the 12 ticks below are the result of this one trade, not a rule:

> "It doesn't belong above the high."
**Source GPS: yRvMW6lgN1o | MIDDLE**

> "see where the largest volumes occurred. For this, we like to use footprint charts. for example, so we can easily identify the perfect level where we should abandon our trading idea"
**Source GPS: yRvMW6lgN1o | MIDDLE**

   Size in this one trade (a result, not a rule):

> "with a stop-loss up here, we now have a risk of 12 ticks. We have a profit of 97 ticks."
**Source GPS: yRvMW6lgN1o | END**

   - Target: sourced (GPT H1, Fable audit section 2). The level type is last week's point of control plus his "smart support" zone (a combination of value areas and single-print areas from the past); he set 6,768 as the target level in advance (an index future; the number is his illustration):

> "Last week, we had the point of control as the target area around 6,763 roughly."
**Source GPS: yRvMW6lgN1o | BEGIN**

> "And these smart support levels are simply a combination of the value areas and the corresponding single print areas from the past."
**Source GPS: yRvMW6lgN1o | BEGIN**

> "I expect the market to reach the corresponding intelligent price zone down here that I just introduced to you."
**Source GPS: yRvMW6lgN1o | MIDDLE**

> "I've initially defined 6,768 as my target level."
**Source GPS: yRvMW6lgN1o | MIDDLE**

   Management: waited patiently (no rule).
4. **Context.** Trend flattening, inside day, near the all-time high (ANG R13). Session, news: NOT STATED.
5. **BTC visibility: YES.** Range, inside day (UTC day OURS), profile step from aggTrades. His order-book remark ("This is exactly the boundary in our order book", yRvM MIDDLE) is commentary, not needed to see the setup.
6. **Evidence.** 1 trade (ANG R13; index future, levels about 6,763-6,768, not named).
7. **Gaps.** Stop price and distance, what makes a "volume step" (an edge of the volume profile: write the OURS definition before marking): NOT STATED. The stop location rule and the target level type were NOT STATED here before 2026-10-16 and are now sourced (card catalog-audit-tom3-source-fields). Possible overlap with TOM-2 (sell the top of a range) and with TOM-1 path A2 (pullback after proof); kept separate because the entry is a resting order at a profile edge, the only one of its kind. yRvMW6lgN1o is V1-only, not in the 26 never-extracted list; worth a V2 pass (inventory).

### TOM-4 Trend continuation pullback (incl. the former TOM-5, pullback long into value after a buying tail)
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

   - Stop: below the last volumes (YkclL6xgu-s, quoted in the batch 2 addition below; the same location rule as "below the last liquidity" in section 2.1, T-2). qLnQ only says "The stop loss belonged right here" (a chart point, STR 5.7). Distance and time stop: NOT STATED.
   - Target: the next high-volume area:

> "In theory, I can plan the next leg up to the next high volume area. Especially when the market shows me once again that it's working with power and it accepts these price ranges."
**Source GPS: qLnQan0KGmQ | END**

   - Management: NOT STATED.
4. **Context.** Trend, not balance ("in a sequence like this, you mustn't trade a trend continuation", 43JaKHRvxHk, TOM-7); VWAP must have a trend: "first rule, very important, the VWAP must be based on a trend" (43Ja BEGIN, STR s3). Time, news: NOT STATED.
   - Added 2026-10-15 from never-extracted videos (batch 1, section 6.1a), the order he checks before any setup (ODdF0Bn_KSc), which says where trend continuation is allowed:

> "That's step one. I determine whether the trend structure is healthy."
**Source GPS: ODdF0Bn_KSc | BEGIN**

> "And this setup needs to show us that actual buying is taking place."
**Source GPS: ODdF0Bn_KSc | MIDDLE**

> "So, you absolutely need to know which setups you're looking for and at which points."
**Source GPS: ODdF0Bn_KSc | MIDDLE**

   Three layers in his order: (1) trend structure on 15 min / 30 min / daily and the weekly profiles (is there "a foundation behind this trend"); (2) a support or resistance zone from old profiles (naked POC, value area, single-print zone); (3) the setup, which "needs to show us that actual buying is taking place". A pullback long into an upward weekly structure is his example; a breakout setup to the downside there "makes absolutely no sense". No stop, no target distance: NOT STATED. This is the same chain as the worked example below (the former TOM-5). The only reason for a separate row was the stop wording; TOM-4 now has it (YkclL6xgu-s), so the two are merged (D3, 2026-10-16).

   - Added 2026-10-15 from never-extracted videos (batch 2, section 6.1a), the first stop in his words for this setup (YkclL6xgu-s). Entry rule: check that the large volumes shifted up, then enter on the return; stop: below the last volumes (location, no distance); target: where large volumes used to be. Numbers: none added.

> "I have to check whether the volumes have really shifted upwards and then I can wonderfully look for a new entry for myself."
**Source GPS: YkclL6xgu-s | END**

> "where does my stop loss belong. Yes, below the last volumes."
**Source GPS: YkclL6xgu-s | END**

> "And where are my targets? with high probability there where there used to be large volumes in the past."
**Source GPS: YkclL6xgu-s | END**

> "greater acceptance of lower prices means that for now the probability is high that the downtrend will continue"
**Source GPS: YkclL6xgu-s | END**

   The mirror holds for shorts (acceptance of lower prices). Which volumes count as large is instrument specific ("know which volume sizes are typical for each instrument", same video, paraphrase). Still NOT STATED: distance below the last volumes, time stop.

5. **BTC visibility: YES.** Trend, VWAP (anchor OURS), value areas, volume under the move, high-volume nodes.
6. **Evidence.** 3 assigned examples: the former TOM-5 trades (ANG R17, R6, R7, see the worked example below). TL and ANG tagged none as this row before the merge.
7. **Gaps.** Stop distance, time stop, entry trigger at the pullback: NOT STATED (the stop location is sourced: below the last volumes).

#### TOM-4 worked example (was TOM-5): pullback long into value after a buying tail
Merged into TOM-4 on 2026-10-16 (D3): a pullback to prior-day value or the POC after a buying tail, with the trend, is the same setup (same stop rule, same target logic). The field numbers below are the old TOM-5's.

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
7. **Gaps and contradictions.** STR files 4MoN under breakout (s6: ledge, speed, add at breakout); ANG under this pullback. Both are in the video: entry on the pullback, add on the breakout. The "last low" vs "below the business zone" stop: two phrasings in one video, same trade. Whether Tom himself files this under trend continuation is NOT STATED; the merge is this catalogue's reading.

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
   - Added 2026-10-15 from never-extracted videos (batch 1, section 6.1a), where a breakout is allowed and what proof he wants (uk4PZV59nYw, gFJBg8Bsw68, uFxYcpiaOpw). He says the three basic trader types are breakout, trend following and counter trading (gFJB, paraphrase). Location and proof:

> "whenever you trade breakouts, you need to have plenty of clear space to the left"
**Source GPS: uk4PZV59nYw | MIDDLE**

> "In addition to this, these breakouts should ideally be accompanied by the right kind of order flow."
**Source GPS: uk4PZV59nYw | MIDDLE**

> "we now have a strong candlestick followed by a brief pullback, and then another strong candlestick appears."
**Source GPS: uk4PZV59nYw | END**

> "It's complete nonsense to think that markets only make rapid moves at highs or lows."
**Source GPS: gFJBg8Bsw68 | END**

> "Market profilers would say it leaves a single print."
**Source GPS: gFJBg8Bsw68 | MIDDLE**

> "if it then moves above the absolute high above the value area you can assume that a breakout will occur there and then you can expect the market to accelerate sharply again"
**Source GPS: gFJBg8Bsw68 | MIDDLE**

> "I wait to see if a consolidation occurs, and only if a consolidation happens."
**Source GPS: gFJBg8Bsw68 | BEGIN**

> "We need a setup here that provides us with proof that the market is indeed strong."
**Source GPS: uFxYcpiaOpw | MIDDLE**

> "we see the market opening a single print here, which means aggressive buyers have entered the market."
**Source GPS: uFxYcpiaOpw | MIDDLE**

> "And there we can see, boom, and it gives us a wonderful P."
**Source GPS: uFxYcpiaOpw | END**

> "I have a breakout here with this higher closing price."
**Source GPS: uFxYcpiaOpw | END**

   Reading: the breakout is a chain, not a pattern: (a) the location (his words for the wrong place: a fresh low or high inside an "unfair" price range with volume still below, uk4P; the right place: clear space to the left, an unfinished auction, a single print, uk4P/gFJB), (b) a stronger-than-normal first bar ("strong candlestick, brief pullback, another strong candlestick", uk4P, on a footprint view), (c) a P (or B) on a fast chart (1-minute in the Nikkei example, uFxY) with a higher close, (d) order flow behind it (large volume pushed in dynamically, uk4P). After news he waits for a consolidation, then volume again, then the trend direction (gFJB, wording above). In uFxY he says this model "only works about once a day" and "only works in 30% of the market phases" (hit rate 80 to 90 %, his claim, not tested).

   Exit and R:R in his words (uk4P): the breakout hit rate is high but the payoff is small, and he leaves when momentum reverses.

> "with breakout setups, you often have risk reward ratios that are not greater than 1:1 or 1.5:1."
**Source GPS: uk4PZV59nYw | END**

> "you need to check whether the exact opposite of what aligns with your trend direction is actually happening there. If that's the case, you need to exit immediately."
**Source GPS: uk4PZV59nYw | END**

> "with breakout trading, defining your target is often not so easy because it frequently happens that the market quickly reacts in the opposite direction"
**Source GPS: uk4PZV59nYw | END**

   Still NOT STATED: breakout stop (price or distance), entry order type, speed threshold. The 1:1 to 1.5:1 R:R contradicts the "explosion" holding style of TOM-5/6 (4MoN): he says both, in different videos. Not resolved. Evidence: no trade is taken in uk4P, gFJB or uFxY (chart examples only), so the count stays 0.

5. **BTC visibility: YES.** Balances, overlaps, ledges, VWAP shift, buying/selling speed (aggTrades).
6. **Evidence.** 0 standalone trades; the 4MoN add (TOM-5) is the only taken instance.
7. **Gaps.** Entry trigger, speed threshold, stop: NOT STATED. Never-extracted `uk4PZV59nYw` ("his EXACT breakout setup") and `gFJBg8Bsw68` ("BEST breakout strategy") are the obvious sources (section 6).

   - Added 2026-10-15 from never-extracted videos (batch 3, section 6.1a), the second attempt, the early entry and the tested-level rule (4VXpUjhKG2U, Sy-x5AQ9-Pk). No stop: NOT STATED.

> "Breakout trading only works when a market is out of balance."
**Source GPS: 4VXpUjhKG2U | MIDDLE**

> "And on the second run, the probability is even greater that the market will continue to push higher after a small pullback."
**Source GPS: 4VXpUjhKG2U | MIDDLE**

> "I can already trade a breakout before it takes out the high"
**Source GPS: Sy-x5AQ9-Pk | END**

> "should it return there, the probability is higher that it will fall through"
**Source GPS: Sy-x5AQ9-Pk | END**

   Reading: untested impulse and sideways zones are reaction zones; a zone that was tested once is "checked off" and more likely to break on the next return. The early entry before the old high is his wording; its size is NOT STATED.

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

   - Added 2026-10-15 from never-extracted videos (batch 2, section 6.1a), news gaps (lO-Iptd29t4): a gap is closed only after a range has formed and left again. Before that, no gap trade.

> "stop driving yourself crazy thinking that this gap will be closed"
**Source GPS: lO-Iptd29t4 | MIDDLE**

> "if a quick move happens after the news and then a range forms, please be careful that these gaps get closed only when the market leaves this range again and also signals that there's new liquidity, then you can trade for the gap to be closed"
**Source GPS: lO-Iptd29t4 | END**

> "If you have such a breakaway gap, assume that this gap here will not be closed."
**Source GPS: lO-Iptd29t4 | END**

   Stop, target size, intraday footprint gaps ("stop using the strategy of looking for these intraday price gaps in the footprint charts", paraphrase: liquidity dried up): NOT STATED / rejected by him.

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

   - Added 2026-10-15 from never-extracted videos (batch 2, section 6.1a), same video (lO-Iptd29t4), the trend-with-the-gap case:

> "Then you are allowed to trade in the direction of the trend here using the corresponding structures available to you."
**Source GPS: lO-Iptd29t4 | END**

> "Please don't let anyone tell you that trend continuation always works in news trading."
**Source GPS: lO-Iptd29t4 | END**

> "wait for the range after the market, for example, has moved abruptly from here to here"
**Source GPS: lO-Iptd29t4 | END**

   Stop: NOT STATED.

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

### TOM-11 Cross-market lead: crude oil reacts first, the index future follows
1. **Name / trader.** Tom (YYYuaetck_0, "my trading style currently"). No name of his own; this catalog calls it a cross-market lead.
2. **What you see.** Two charts at once: crude oil and an index future (S&P). In the high-volatility geopolitical phase of the video big money moves from risk-on stocks into commodities, so crude oil is the "pre-indicator". A technical level is reached in crude oil, crude reacts for seconds, the index future reacts a little later.

> "And I know it is crude oil most of the time."
**Source GPS: YYYuaetck_0 | MIDDLE**

> "And this is the way that I use informations for me that I have a lot of seconds reactions before in crude oil and after it in index futures."
**Source GPS: YYYuaetck_0 | MIDDLE**

> "Please use two charts, and use if you are looking for long trades, look is here a level with short reaction."
**Source GPS: YYYuaetck_0 | END**

3. **Entry, stop, target, management (his words).**
   - Entry: not in the crude oil but in the index future, a few seconds after the crude oil reaction, before the breakout of the index. Long example: a small technical pullback in the index while crude oil sells for about 30 seconds.

> "I use it here to make my long trade. And I'm going long earlier than the breakout is coming."
**Source GPS: YYYuaetck_0 | END**

> "You can put your position inside of the index future. It will be a little bit lagging behind the crude oil."
**Source GPS: YYYuaetck_0 | END**

> "You can use it, I think, four to five times per day."
**Source GPS: YYYuaetck_0 | END**

   - Stop: NOT STATED. Target: "the last reference level" of the index (the quote below); a level he points at ("Here is my target"). Management: NOT STATED.

> "I know now it's time to invest me long in this way into"
**Source GPS: YYYuaetck_0 | END**

> "And also I know opportunity is very high that we go over the last reference level with a long situation."
**Source GPS: YYYuaetck_0 | END**

4. **Context he requires.** The video is about one regime (war and oil, inflation up and growth down, capital moving into commodities); whether it works outside that regime is NOT STATED. Without the second chart the plain index breakout often fails:

> "if you don't look also in other markets in this way, especially crude oil, often you have this opportunity"
**Source GPS: YYYuaetck_0 | END**

5. **BTC visibility: NO.** Crude oil and index futures are not on disk, and the lead is seconds. A BTC/ETH or BTC/perp version would be OURS (ETH is held, no crude, no index).
6. **Evidence.** 0 trades with dates or prices; he shows a long and a "normal breakout" long in S&P as chart illustrations (not counted).
7. **Gaps.** Stop, target level type, the size of the crude oil reaction that counts, how to tell "pullback" in the index: all NOT STATED. Single video, single regime.

### TOM-12 Break-in: price returns into the old balance after outside prices fail to hold
1. **Name / trader.** Tom, "break-in" (PBD logic). TOM-6 names it ("breakin or breakout") without a definition; these videos give one, so it is catalogued on its own. Merged files: TOM-6, TOM-1 path A3 (the P that fails back inside).
2. **What you see.** Price accepted new prices outside the old balance (a P above, a B below) but with no volume foundation under them; then it falls back into the old value area with momentum. Participants who entered outside are now underwater and have to close; the move back through the old range is fast ("the best breakouts you can get").

> "is there here a fundamental base in terms of volume or did the market rise very quickly here without any foundation"
**Source GPS: gFJBg8Bsw68 | MIDDLE**

> "And the moment it re-enters the value area here, very often strong momentum arises."
**Source GPS: gFJBg8Bsw68 | BEGIN**

> "the probability that it breaks in here that it breaks through the P and goes below the last value area is very high"
**Source GPS: gFJBg8Bsw68 | MIDDLE**

> "All these market participants here, they're no longer in a good position. Suddenly, they're underwater."
**Source GPS: gFJBg8Bsw68 | MIDDLE**

> "The market has traded, crossed over briefly, and we call that a break-in, and so it usually continues."
**Source GPS: m3IMdc7QwN4 | MIDDLE**

> "We call this a break-in."
**Source GPS: jXR1afMy-3o | END**

   PBD in his words (shared by TOM-6, -12): the structures are P (aggressive trend up), B (aggressive trend down), D (large balance); he counts closing prices, not highs and lows.

> "By the way, the D's are nothing more than large balance phases. The P's are the aggressive trend phases upwards, and the B's are the aggressive trend phases downwards."
**Source GPS: m3IMdc7QwN4 | END**

> "The P's and the B's are both structures, setups that typically cause a market to accelerate."
**Source GPS: jXR1afMy-3o | BEGIN**

> "in the PBD concept, we don't use the absolute high and low points, but we always look at the closing prices and the market openings"
**Source GPS: Ly62G168MkQ | BEGIN**

3. **Entry, stop, target, management (his words).**
   - Entry: the pullback after the move back inside.

> "And look at what a great opportunity you have here. Pullback. And then the thing breaks downwards."
**Source GPS: gFJBg8Bsw68 | MIDDLE**

> "the market goes below the range and then back in. Yes, then the probability is initially high that it will go back up."
**Source GPS: jXR1afMy-3o | END**

   - Stop: NOT STATED. Target: the start of the impulse that formed the outside move, then the next fair price area.

> "So, I know my next target is below the start of the impulse."
**Source GPS: jXR1afMy-3o | END**

> "We will, with high probability, run below the start of this movement."
**Source GPS: m3IMdc7QwN4 | END**

   - R:R and hit rate: break-in is the better payoff of the two kinds.

> "And with both approaches, you can make money just as quickly, although the break-in scenarios usually have much higher riskreward ratios."
**Source GPS: gFJBg8Bsw68 | END**

   - Management: NOT STATED.
4. **Context he requires.** The outside prices must lack a volume base (above), the old value area must still be the place of the weekly or daily profile. Trade direction is with the break-in (a B above the old range breaking back down, or a P below breaking back up); a failed break-in he reads as the market not accepting the outside prices.
   - Added 2026-10-15 from never-extracted videos (batch 2, section 6.1a), the fast re-entry as a risk sign (0CrkbfuIhkc, index and Bitcoin charts; no entry or stop):

> "And this re-entry very, very fast and aggressive back into this old balance has meant that we've basically unchecked, shot right past it."
**Source GPS: 0CrkbfuIhkc | BEGIN**

5. **BTC visibility: YES.** Old value area, P/B shapes, volume under the outside move, the speed of the return: klines and aggTrades.
6. **Evidence.** 0 trades. Weekly-chart examples only (gFJB). The viT_ trade (TOM-2) ends with a long that is this idea (acceptance above, pullback, up), told after the fact (viT_VzF5Fsw, "By the way, I bought here.").
7. **Gaps.** Stop, entry trigger beyond "pullback", how far inside the old range price must close (closing-price counting rule is "taught elsewhere", not in these videos), timeframe: NOT STATED. Overlap with TOM-1 path A3 and TOM-2 "lower balance after rejection": same family, listed separately because he names it a break-in and enters it WITH the move inside.

### TOM-14 After a news shock: counter trade back to the origin of the move (V reversal)
1. **Name / trader.** Tom, no name of his own (6BAzqewtPUk, news flow video). "Check if there's an overreaction", then trade a path back to the origin of the shock.
2. **What you see.** An unpredictable news shock moves price fast with no base under it (political markets "have short legs"; liquidated hedges exaggerate the move). After the shock a small consolidation appears (an inside bar), then a reaction in the other direction, often back to the origin of the shock move.

> "But here for example we see a wonderful inside bar. That's nothing more than a consolidation point after a fast movement."
**Source GPS: 6BAzqewtPUk | MIDDLE**

> "After that comes the reaction upwards and very often such reactions go back to the origin of the alpha movement."
**Source GPS: 6BAzqewtPUk | MIDDLE**

> "Often these are V reversals because in these moments there's no foundation where large market participants have accumulated for a long time so the market can just go back."
**Source GPS: 6BAzqewtPUk | MIDDLE**

3. **Entry, stop, target, management (his words).**
   - Entry: after the reaction has occurred, never at the extreme.

> "you can quite well time looking for counter trades after a news event for example and you'll never get them at the very bottom"
**Source GPS: 6BAzqewtPUk | MIDDLE**

> "Check if there's an overreaction, check what the volumes are like and then simply look at the original value."
**Source GPS: 6BAzqewtPUk | END**

   - Stop: NOT STATED. Target: the origin of the move.

> "First, try to trade a path back to that point and that is very, very effective and it helps us tremendously."
**Source GPS: 6BAzqewtPUk | END**

   - Management: NOT STATED.
4. **Context he requires.** Wait and watch which of two things follows: V reversal or balance forming. A sideways phase with volume means price accepted there; PBD logic decides ("if it goes back in, they accept these prices", paraphrase).

> "when unpredictable movements occur, always wait to see what happens next. Does a V reversal follow or does a balance form?"
**Source GPS: 6BAzqewtPUk | END**

   Context filter (15JoLK0PbMU, VIX video; the 20 is his number, SOURCED): political news moves are overreactions that reverse; the VIX level decides whether institutions invest.

> "political markets have short legs"
**Source GPS: 15JoLK0PbMU | MIDDLE**

> "So, for us, the absolutely most important figure in the volatility index is the 20."
**Source GPS: 15JoLK0PbMU | END**

   Below 20: steady inflow, "relaxed balance trading"; above 20 sustained: large swings, strong breakouts or counter trades (paraphrase). BTC has no VIX; any BTC volatility gauge would be OURS.
5. **BTC visibility: PARTIAL.** Fast shocks, inside bars, volume spikes and the origin of the move are visible in klines; whether the cause was a political headline is not (news timestamps would need a source).
6. **Evidence.** 0 trades. Crude oil and DAX-future chart illustrations after a political message (video context 2026 Middle East), no dates or prices given.
7. **Gaps.** Entry trigger beyond "after the reaction", stop, how far a move counts as an overreaction, time frame: NOT STATED. Close to TOM-1 (counter trade of an exhausted push) and TOM-11 (news regime); listed apart because the target is the origin of a news shock.

### TOM-15 Candle formations at a range edge: three in a line, inside bar, outside bar
1. **Name / trader.** Tom, "three in a line", inside bar, outside bar (2xnNPIyHGQ4, "less is more"). Candle patterns are his only taught ones; he says they work only with location and volume.
2. **What you see.** (a) Three candles of the same colour in one direction, ideally with spikes, at a breakout level after a real compression (range or support area); the next move is often extreme and the fourth strong impulse is the excess that ends the run. (b) An inside bar after an impulse: a stopping point where balance starts, a place to look for a reversal. (c) An outside bar that trades above and below the previous candle: stops and equilibrium are cleared, an impulse often follows.

> "Three candlesticks of the same color in one direction."
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**

> "I should only look for it when a market is at a so-called breakout level."
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**

> "always make sure to check beforehand whether a compression has built up in whatever form"
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**

> "When this fourth strong impulse comes, it's always the excess."
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**

> "And such outside bars often give me an indication that the market has now made a decision."
**Source GPS: 2xnNPIyHGQ4 | END**

3. **Entry, stop, target, management (his words).**
   - Entry: for the inside bar, look for the reversal; for the three in a line, the third move after it. Trigger candle and price: NOT STATED.

> "And I then look to see if there's an opportunity for a reversal here."
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**

> "The third move after the three in a line is often an extreme move."
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**

   - Stop: NOT STATED. Target: the next support or resistance area.

> "where is my next interesting support or resistance area"
**Source GPS: 2xnNPIyHGQ4 | END**

   - Management: NOT STATED.
4. **Context he requires.** A support or resistance area or a compression beforehand; in the middle of a range the formation does not help. Volume: falling volumes with room below let him treat a three in a line as trend continuation instead of an S/R trade.

> "And it's also absolutely essential to check whether there was a resistance or support area beforehand where this candlestick formation could give me an advantage."
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**

> "markets always tend to move toward areas of high trading volume"
**Source GPS: 2xnNPIyHGQ4 | END**

5. **BTC visibility: YES.** Candle bodies, ranges and volume from klines at any time frame (the time frame is not fixed in the video; 30-minute and 5-minute shown).
6. **Evidence.** 0 trades. He says the three patterns can be back tested "with the relevant previous support and resistance levels" (paraphrase); he gives no results.
7. **Gaps.** Time frame, trigger candle, stop, target distance, volume threshold: NOT STATED. Overlaps TOM-6 (breakout level) in location; separate because the signal is the candle pattern.

### TOM-16 Top after forced hedger buying: short when the large volumes break down
1. **Name / trader.** Tom, no name of his own (cw8LWQmec1E, gold and silver futures, "shorting the tops").
2. **What you see.** A market far above its average: volume is much larger than average and traded at much higher prices. The volume at the top is hedging (industrial buyers who had to buy after the breakout from the old balance), not trader conviction. Then an aggressive seller appears and the hedgers who bought near the high are underwater.

> "This volume isn't created by us traders, but by so-called hedging transactions."
**Source GPS: cw8LWQmec1E | MIDDLE**

> "At this precise moment, we can see that an aggressive seller finally comes in to drive the price."
**Source GPS: cw8LWQmec1E | MIDDLE**

> "if it's much lower, well, then simply no one is interested anymore. And then there's a high probability that the market will return to its average."
**Source GPS: cw8LWQmec1E | BEGIN**

3. **Entry, stop, target, management (his words).**
   - Entry: when price goes below the level of the last big buyers (large volumes break downward); intraday: heavy selling after heavy buying, then watch the price range below.

> "Where were the last big buyers? And then you'll see when the market goes below that. Then the probability is high that sales will increase, and then you have the big short."
**Source GPS: cw8LWQmec1E | END**

> "we're waiting for the moment when large volumes break downward"
**Source GPS: cw8LWQmec1E | END**

> "And then you have a price range here where you can watch what happens if we drop below it."
**Source GPS: cw8LWQmec1E | END**

   - Stop: NOT STATED. Target: NOT STATED (the hedgers' entry area is the pressure zone, no price named as target). Management: NOT STATED.

> "And that's the moment where you're usually even in earlier than if you analyze the volume the way I just showed you."
**Source GPS: cw8LWQmec1E | END**

4. **Context he requires.** Compare current volume with the product's average liquidity; prices far above where the main volume traded. The hedging story applies to commodity futures (producers, expiry months).
5. **BTC visibility: PARTIAL.** Volume by price, a large volume node under the high and the break below it are visible in klines and aggTrades; hedgers and expiries are not (perpetuals have no hedging buyers of this kind).
6. **Evidence.** 0 trades. Gold and silver chart illustrations (the TL T8 gold short is the same context, section 6.1).
7. **Gaps.** Stop, target, how much above the average counts, how large the volume must be: NOT STATED.

### TOM-17 Low-volume-node scalp decided by market speed (order-book scalp)
1. **Name / trader.** Tom ("The real scalping strategy", G0CiJcuXCRs; V1 only, not in the 26 never-extracted list). Added 2026-10-16 (audit T-1). Not TOM-7 (a VWAP range scalp): the trigger here is tape speed at a low-volume price range. It is the only Tom setup with a tape-speed trigger, the closest cousin of the Fabio rows.
2. **What you see.** Preparation: look at how liquidity was played so far today, locate the areas of low volume, notice where volume increases a lot.

> "take a quick look at how liquidity has been played so far today"
**Source GPS: G0CiJcuXCRs | BEGIN**

> "locate areas of low volume"
**Source GPS: G0CiJcuXCRs | BEGIN**

Then price ticks down (or up) into a low-volume price range. Branch one, the market goes through, does nothing and returns: it runs back to the high volume ("lethargic back and forth scalping"):

> "this price range is such a low volume level where I actually assume it will go through again, and now it goes below that and does nothing and stops and starts going up again"
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "Quite simply, it will run back to the high volume. That is lethargic back and forth scalping"
**Source GPS: G0CiJcuXCRs | MIDDLE**

Branch two, the market arrives at the low-volume area at a constantly high speed and large participants are active: it continues to run:

> "the market goes down here, reaches the low volume area and has a constantly high speed"
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "Large market participants are ready to interact"
**Source GPS: G0CiJcuXCRs | MIDDLE**

3. **Entry, stop, target, management.** Entry trigger: the stall (branch one) or the sustained speed (branch two); order type NOT STATED. Target: the nearest high-volume level (branch one, "run back to the high volume"). Stop and management: NOT STATED. On the order book he reads large against small market orders:

> "which orders traded at market are large and which are small"
**Source GPS: G0CiJcuXCRs | MIDDLE**

> "That's easy money for breakfast when you see something like that pre-market"
**Source GPS: G0CiJcuXCRs | END**

4. **Context.** Liquid instruments; he warns about thin ones:

> "the DAX future, which I absolutely don't recommend for order book scalping due to the extremely thin uh liquidity"
**Source GPS: G0CiJcuXCRs | END**

5. **BTC visibility: PARTIAL.** Low-volume and high-volume price levels from aggTrades by price: YES. Tape speed (trade rate and delta rate from aggTrades timestamps): YES. Resting big orders and "eaten up" orders: NO (no order-book history). Large against small market orders: PARTIAL (one aggTrades row is not one order). Pre-market is not a BTC event.
6. **Evidence.** 0 trades (a teaching session).
7. **Gaps.** Stop, target distance, the speed threshold, what counts as a low-volume range, entry order type: NOT STATED.

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
   - Breakout qualification (rule added 2026-10-16 from 9IliXww64uM, audit F-1; his words on an ES session): a breakout counts only when a range forms outside the previous day's value area, not on an impulse alone:

> "I don't want to just see an impulse during the breakout. Basic market structure is not enough. What I want to see is a range being formed outside of the previous day valuation"
**Source GPS: 9IliXww64uM | MIDDLE** (9IliXww64uM_raw.txt:145-149, [4:58])

> "just the face of price discovery doesn't mean price acceptance. This would be only price discovery. This is price acceptance. So, in order to qualify a breakout, I wait for a range to form."
**Source GPS: 9IliXww64uM | MIDDLE** (9IliXww64uM_raw.txt:154-158, [5:19])


4. **Context.** Directional, volatile day (section 2.2); NASDAQ futures, World Cup session. Session time in this video: NOT STATED (8CWK says he scalps the New York session).
5. **BTC visibility: PARTIAL.** Balance, profile, CVD, candle follow-through: YES. "Big trades": PARTIAL (aggTrades rows are not orders; V3 s1 notes "Big print" = one aggTrades row).
6. **Evidence.** 1: FL F2 (+ F2-m1 second balance box continuation); ANG R26, R27 (positions 1-5 in the same session).
7. **Gaps.** Initial stop (a chart point in 0jM5), balance length: NOT STATED. What counts as "big" is SOURCED for NQ (30 contracts, 20 in London: section 2.2, DyS79Eb92Ug); the BTC equivalent is OURS. OURS (V3 s7.1): N {60,120,240} bars, k_bal 0.8, POC band 0.25, pressure p {0.05,0.10}, drift 0.25, big trade = prior-30-day 99th/99.9th percentile, tier VR 1.5, S4 window m, S8(a) 15 bars, NY window 390 bars / cutoff 330, 13:30 UTC mapping, BE distance be_k, stop floor f, Dmax 1 %, -3R daily stop, 10 first legs.

**ASR addition 2026-10-16 (Is1HvdfQm5c).** Condition on momentum entries in a balance (live Q&A, one video, ASR; the speaker is Fabio by first-person answering, not by label). A momentum breakout exactly at the value-area low, where a resting limit wall sits, is the case he rejects; he would consider the sell continuation only if the level breaks (rows 1.108, 1.109 of the V2 extract). Stop and target NOT STATED.

> "this is the worst case that you can have for a momentum trade"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, Is1HvdfQm5c_raw.txt:318, [48:36])

> "it's the limit price wall on the top or on the bottom it's giving keeping you in consolidation"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, Is1HvdfQm5c_raw.txt:317, [48:25])


### FAB-2 Absorbed push, rewarded effort ("punch to the wall"), incl. the failed auction of one side then the other side's aggression (former FAB-3)
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
7. **Gaps and contradictions.** FL labels F1 `balance_failed_auction_punch_to_wall` (FAB-3 words) while ANG/8CWK describe absorbed buyers + seller control (this setup). FAB-2 and FAB-3 are one setup seen at two moments (absorption of one side, then the other side's aggression at that level): merged 2026-10-16 (D3, audit 4.1; GPT M5: the fZ narrative starts at F3a). The side flip at a consolidation (the former FAB-3, below) is a variant; the with-trend add point is the other. Absorption threshold: NOT STATED ("almost zero"). OURS: V3 S3 L 60, z_hi {2.0,2.5,3.0}, r_abs 0.25, r_ctl 1.0.

#### FAB-2 variant (was FAB-3): failed auction of one side, then aggression of the other at the level
Merged into FAB-2 on 2026-10-16 (D3). The field numbers below are the old FAB-3's.

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
4. **Context.** the fZlNGWvd2Ko session's own floor at day P&L 0 and "risk only the day's profit" (section 2.2, scoped there: not a condition of every Fabio trade; F5 is entered at a $9,000 drawdown for the day, card catalog-audit-fabio-risk-scope); jasv3L: a compression day with dealers "long gamma", he expects a breakdown:

> "Now the market maker are long gamma. So they will try to compress volatility. I expect a good explosion down."
**Source GPS: jasv3L-d8ZE | END**

5. **BTC visibility: PARTIAL.** Consolidation, absorption by side, aggression, level break: YES. Big trades in the candle body: derivable from aggTrades but not in our bars (V3 s1, M10). "Buyers wall": NO (L2). Dealer gamma: NO (no options history; V3 dropped it).
6. **Evidence.** 2: FL F3c (fZ long re-entry, risk $980 to make $25,000), F5 (jasv3L short 15->18 lots after a losing start). ANG R32 = F3; R34 = F5.
7. **Gaps and contradictions.** LBL s4: the V1 extract atomized this sequence (R2 "failed auction plus buyer aggression" lost the side relation), and turned the scratch plan into a BE rule that FR-12 then merged with 0jM5's opposite trigger (BE after success vs BE on failure). "Failed auction" has no mechanical definition (FR s4). OURS: V3 S5D/model D (rest 3 bars, limit at the edge), M9 re-pivot not applied.

**ASR addition 2026-10-16 (Is1HvdfQm5c).** Fresh read of the 2.5 h session (extracts/v2/fabio/Is1HvdfQm5c_v2.md, ASR). He walks one setup as an illustration/hypothetical (no live fill with a stated entry): absorption at the top, then aggressive sellers with a result, short on the test of the level; stop NOT a distance but a small one above the area; target stated as a multiple (the number is an ASR number: check frames before using it). Speaker not labelled by ASR; first-person teaching style.

> "the trade that in 2025 gave me the most amount of money is the test of this level with"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, Is1HvdfQm5c_raw.txt:139, [20:10])

> "to jump in with a super small stop loss okay you can cover yourself above the area and shoot for a 1 to 4.5"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, Is1HvdfQm5c_raw.txt:145, [21:14])


### FAB-4 Failed breakout back into balance (reversal at the edge of the previous day's value area)
1. **Name / trader.** Fabio ("failed breakout", "clear failed auction"; 9IliXww64uM, an ES session, "a little over $4,000"). Rewritten 2026-10-16 from the caption file converted in P2 (`9IliXww64uM_raw.txt`); the old row held only OURS structure, the FL schematic note and a rulebook paraphrase (FR-19, FR-86, source `o-w5Gxss6T0`; that transcript has been on disk since 2026-10-18 and gives no failed-breakout rule beyond the CVD absorption of section 4.2). Merged files: section 1.
2. **What you see.** Frame: the previous session's value area holds 70 % of its activity and is the area of comfort; he opens inside it and expects to stay inside for the day:

> "I consider this to be a very strong area of comfort where price is likely to be keep trading because already 70% of the trading activity happened within this range in the previous session."
**Source GPS: 9IliXww64uM | BEGIN** (9IliXww64uM_raw.txt:133-138, [4:26])

> "we opened the session exactly inside of the previous value area. This is already a good sign that we're probably going to stay inside of this range for the rest of the day because there was no relevant news or price discovery auction during the Asian or London session"
**Source GPS: 9IliXww64uM | MIDDLE** (9IliXww64uM_raw.txt:173-181, [6:02])

Inside the range an attempt out fails. Trade 1 (a long at the bottom): the initial balance had two failed attempts, sellers are absorbed at the bottom, volume rises on the way out and again on the way back, a strong volume reversal, the 5-minute candle closes back inside:

> "when I saw these aggressive sellers being absorbed at the bottom, it's simply the same thing that happened over here, but from the sell side of the market."
**Source GPS: 9IliXww64uM | MIDDLE** (9IliXww64uM_raw.txt:212-216, [7:24])

> "you have a negative delta with a positive price action. That's a very clear divergence in market pressure. There was an effort from seller that is not having any follow through. And the 5-minute was about to close right over here and that was my signal for the entry."
**Source GPS: 9IliXww64uM | MIDDLE** (9IliXww64uM_raw.txt:239-246, [8:28])

Trade 2 (a short at the top, the failed auction): buyers reabsorb the price at the top of the wick, activity rises as price breaks back inside with selling dominance:

> "buyers very aggressive at the top of the wick completely reabsorbing the price action."
**Source GPS: 9IliXww64uM | MIDDLE** (9IliXww64uM_raw.txt:262-264, [9:14])

> "as we broke back inside, the activity started rising. Buyers and sellers start auctioning very aggressively again on both sides of the auction, but with a clear selling dominance."
**Source GPS: 9IliXww64uM | END** (9IliXww64uM_raw.txt:283-288, [10:02])

> "This is a clear failed auction. And that was exactly the second trade."
**Source GPS: 9IliXww64uM | END** (9IliXww64uM_raw.txt:292-294, [10:22])

3. **Entry, stop, target, management (his words).** Entry: the close of the 5-minute candle after the footprint shows the absorbed side (B6, "my signal for the entry"). Stop: a chart point only, NOT STATED as a level or distance:

> "Stop was likely somewhere above here, and we took profits around the beginning of this candle."
**Source GPS: 9IliXww64uM | END** (9IliXww64uM_raw.txt:296-298, [10:31])

Target: the other side of the range, and an early exit when a strong impulse starts at a place where the other side responds:

> "And then I traded all the way to the other side of the range where sellers are likely to get aggressive."
**Source GPS: 9IliXww64uM | MIDDLE** (9IliXww64uM_raw.txt:249-251, [8:48])

> "that's already another one to four risk to reward."
**Source GPS: 9IliXww64uM | END** (9IliXww64uM_raw.txt:300-301, [10:38])

> "the beginning of a strong impulse happened here, and that's typically a very strong area for a buyer response."
**Source GPS: 9IliXww64uM | END** (9IliXww64uM_raw.txt:302-305, [10:42])

> "that's where I want to be out, where I have a risk that buyers will take control again."
**Source GPS: 9IliXww64uM | END** (9IliXww64uM_raw.txt:310-312, [10:59])

   The continuation trade of the same session (a short on the break of a short-term bearish value area), and his own count of the session:

> "I take my volume profile from the top to the last of the range, and whenever I see on this short-term bearish value area, I want to see a breakout of this level."
**Source GPS: 9IliXww64uM | END** (9IliXww64uM_raw.txt:338-342, [11:58])

> "So, two setups were reversal trades, one setup was a continuation trade"
**Source GPS: 9IliXww64uM | END** (9IliXww64uM_raw.txt:372-374, [13:06])

   Breakout qualification (F-1, also in FAB-1): the quotes B2 and B3 above FAB-1's management line.
4. **Context.** The previous day's value area and a composite profile of the last 10 days (a double distribution with a low-volume node between its two parts), the big-trades panel filtered by size (the NQ filter is in section 2.2):

> "I typically load the last 10 days."
**Source GPS: 9IliXww64uM | BEGIN** (9IliXww64uM_raw.txt:106-107, [3:27])

> "the big trades taken through the order flow of the entire futures market filtered by size so we can filter out the noise and just see the big trades from big banks"
**Source GPS: 9IliXww64uM | BEGIN** (9IliXww64uM_raw.txt:16-20, [0:19])

5. **BTC visibility: YES** for the value area, the probe, absorption (delta against price result), the volume on the way out and in, and the 5-minute close back inside (klines + aggTrades). The previous-session boundary is OURS (D1: 00:00 UTC); the big-trade size is OURS on BTC; "no relevant news" is not markable.
6. **Evidence.** 2, weak: FL F4a, F4b (ES shorts from pasted screenshots, 1 lot, no stops visible). The words show three trades: two reversals (a long at the bottom after absorbed sellers, a short at the top = the failed auction) and one continuation short (B15). Which FL row is which trade is not re-checked here (frame review needed).
7. **Gaps.** The stop is a chart point; entry order type; how far a probe goes before it counts as an attempt; "relevant news": NOT STATED. OURS (V3 model B, not his): reclaim within 5 bars, limit valid 3 bars, stop beyond the probe extreme + 1 tick, target the opposite balance edge (or a trail variant).

**ASR addition 2026-10-16 (Is1HvdfQm5c).** Condition (live Q&A): the reversal short at an edge is declined when it is counter trend; he states the filter as a model line (candidate E of section 5 of the V2 extract). Entry, stop, target NOT STATED here.

> "but these are counter trend trade and I don't like to take them"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, Is1HvdfQm5c_raw.txt:279, [42:22])

> "the model is saying that I only enter in profile framing In in trend condition and I execute"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, Is1HvdfQm5c_raw.txt:53, [6:44])


### FAB-5 Buyers protect a level: long, squeeze trapped sellers
1. **Name / trader.** Fabio ("protection wall", "buyers protecting the level", FL).
2. **What you see.** Price comes down into a level (a value-area low, a gap, a resting "protection wall"); selling is absorbed there (struck several times, absorbed each time); buyers defend it; long, expecting a squeeze of trapped sellers; in line with the day's main direction.

> "In this one, this is amazing because you have a protection wall that is there. This is a resting liquidity, is not fresh liquidity and as you can see the market approach here and get absorbed the first time, strike again this area, absorb the second time, strike this area, absorb the third time"
**Source GPS: FawPrRUGNpk | BEGIN**

> "This is the mean reverting on the protection wall of the buyers in line with the main direction."
**Source GPS: FawPrRUGNpk | BEGIN**

3. **Entry, stop, target, management.** Entry: at the defended level (F6: buyers protecting the gap / value-area low, FL:55, caption paraphrase). Stop (corrected 2026-10-16; the row said location NOT STATED and the old tally said Fabio 0 of 8 stops): the stop sits BELOW the level the buyers protect, a small one because the level is defended, in his words in DyS79Eb92Ug (canonical since P2). The first quote names the side of the protected level as "aggressive sellers" and does not say which way the trade runs; the later ones name "the protection level for buyers":

> "I have an amazing level to to cover myself behind that is this level of aggressive sellers. So they are bu protecting the level like crazy."
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:494-498, [19:08])

> "I can have a really small stop loss here"
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:499-500, [19:22])

> "Auction going back up covering myself below the low one stop loss."
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:599-600, [23:44])

> "What we can do is try an expansion phase with our stop loss below here risking maybe $2,000."
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:1113-1115, [44:16])

> "If they break this level, I can put all my stop loss below this."
**Source GPS: DyS79Eb92Ug | MIDDLE** (DyS79Eb92Ug_raw.txt:1310-1311, [51:47])

> "Okay, we are covered below the protection level for buyers in this case."
**Source GPS: DyS79Eb92Ug | MIDDLE** (DyS79Eb92Ug_raw.txt:1453-1455, [56:53])

   The distance is a dollar risk of 1,500-2,000 in his sessions (FL:55, 62, caption paraphrase, and "risking maybe $2,000" above), not a rule. Target: a sell limit at a fixed distance on the frames (F6 25001, F10 25074.25; FL), rule NOT STATED. Management: stop to about zero fast, scratch if the auction fails, re-enter ("can try another time", FL:62 paraphrase); scale 4 -> 8 -> 10 lots (FL).
4. **Context.** US cash session (every FL frame with a clock). "Wait for buyer protection before long" (FR-67) and "No counter-trend long while CVD is falling" (FR-66) are rulebook paraphrases of FawPr, not verified here. His names and the invalidation for the long (DyS79Eb92Ug, audit F-2c; the clock is his, European time, not converted):

> "the setup that I explained in chart fanatic that is going from the value area low in a momentum day to the value area high"
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:186-189, [7:00])

> "This is the AAA setup."
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:259, [10:14])

> "Why AAA setup? Value area low. So we are really low on the curve."
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:261-262, [10:17])

> "it's called value area low fade okay so"
**Source GPS: DyS79Eb92Ug | MIDDLE** (DyS79Eb92Ug_raw.txt:1832, [1:11:49])

> "My execution of model B testing of the value area after their expansion is from 7:30 European time till 9 because it's the power hour movement."
**Source GPS: DyS79Eb92Ug | MIDDLE** (DyS79Eb92Ug_raw.txt:1918-1921, [1:15:30])

> "If this area gets broken, I don't want to be long for the day. So it will be really with a big probability a consolidation day."
**Source GPS: DyS79Eb92Ug | BEGIN** (DyS79Eb92Ug_raw.txt:223-226, [8:30])


5. **BTC visibility: PARTIAL.** Value-area low, repeated absorption at a price (aggTrades by price): YES. The resting "protection wall" (passive liquidity): NO (no order-book history). Gap level: NO (no BTC gaps).
6. **Evidence.** 11 entry rows (2 + 9; the earlier "13" was a miscount, GPT M6): FL F3a, F3b (fZ, protection wall buy), F6, F7, F8, F9, F10 (DyS79/Jpd96 protection-level squeeze longs), F11, F12, F13, F14 (four chase longs near the 25,110 prior high, all stopped). Outcomes in FL: F6 TP hit; F7 scratch; F8 stopped; F9 small win; F10 TP hit; F11-F14 stopped.
7. **Gaps and contradictions.** F11-F14 are labelled "chase long after squeeze above prior high"; whether they are this setup or a breakout chase is NOT STATED (FL assigns them by sequence). DyS79Eb92Ug is a canonical transcript since 2026-10-16 (stop location, names, session rules); Jpd96fLqr5M has no captions on disk. His live reading of the wall uses the heat map (section 4.1), which is not on disk. Contradiction in management: 8CWK says adding "low in the curve" is not the best idea (V3 P11) while F7-F9 re-enter the same level three times in five minutes after losses (FL:67).

**ASR addition 2026-10-16 (Is1HvdfQm5c).** Names and stop words for the same family (live Q&A, ASR). He calls the third-touch long "the squeeze setup" and covers himself below the area; the buyers' reload on a held level is the proof. This adds a second transcript to the stop-below-the-protection-level words above; the price and the multiple he quotes are ASR numbers (check frames).

> "covering yourself below the area this is the squeeze setup"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, Is1HvdfQm5c_raw.txt:221, [33:03])

> "they are reloading to protect this level"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, Is1HvdfQm5c_raw.txt:312, [47:45])

> "they try to break three four five times and they always hold this level that"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, Is1HvdfQm5c_raw.txt:289, [43:57])


### FAB-6 IVB: first 30 minutes of the US open
1. **Name / trader.** Fabio ("the IVB"; LQvv5xgy_ik).
2. **What you see.** The first 30 minutes of the US equity open; its range (bottom/top) sets the day's direction.

> "the bottom of the first 30 minutes is giving a lot of value in the direction of the day"
**Source GPS: LQvv5xgy_ik | END**

3. **Entry, stop, target, management.** NOT STATED in the verified quote. OURS (V3 model C): break of the IB edge with S4, stop at the IB midpoint + 1 tick, one IVB trade per day. FR-81 (StaphlRH8NQ): "Opening range breakout has positive skew", "first 30 minutes" and "13.5%" (rulebook paraphrase, not verified here).
4. **Context.** "the nature of the US equities have predictable behavior during the opening" (LQvv END, same passage; not block-quoted). Can be improved with option flow (same passage).
5. **BTC visibility: PARTIAL.** The 30-minute range is computable from klines; the US equity open is not a BTC event (the 13:30 UTC mapping is OURS; V3 MP:128 says it may not port).
6. **Evidence.** 0 trades.
7. **Gaps.** Entry, stop, target all NOT STATED in LQvv5xgy_ik (a risk-management lecture; the IVB is an example).

**Merge 2026-10-18 (cUTsoU-15Tc, StaphlRH8NQ; `extracts/v2/fabio/cUTsoU-15Tc_v2.md`).** SOURCED: location (value area to POC block after the breakout), invalidation (a candle CLOSE beyond the value area low), two order-flow triggers (seller absorption on the POC; seller exhaustion with buyer momentum), stop below the protected area, reward 1:2 to 1:2.5, "1 2 3 1 to 2.5" quoted as the consistent target. Definition (StaphlRH8NQ): "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading". Still NOT STATED: stop in ticks, order type, the "protection level" (an unpublished Deep Charts algorithm; his 65 to 70 % is the tool's claim, OURS untested). FR-81 is now partly verified; the 13.5 % and 1:1 test are in `extracts/v2/fabio/CATALOG_DELTA.md` N3.

### FAB-8 Volume-defined fair value gap rejection
1. **Name / trader.** Fabio (FR-94 to FR-96; source o-w5Gxss6T0).
2. **What you see.** Not the candle-gap FVG: from a swing A to B, the value area (70 %) and inside it the lowest-volume price; price rejects there (rulebook paraphrase; example "24,318 to 24,317").
3. **Entry, stop, target, management.** SOURCED definition and "this is exactly where the price will reject" (o-w5Gxss6T0, below). Entry order, stop and target NOT STATED.
4. **Context.** NOT STATED.
5. **BTC visibility: YES.** Swing profile and its low-volume price from aggTrades.
6. **Evidence.** 0 trades.
7. **Gaps.** Transcript o-w5Gxss6T0 is in raw_transcripts_canonical since 2026-10-18 (merge below). Swing selection, bin size, timeframe UNDEFINED (FR s4).

**Merge 2026-10-18 (o-w5Gxss6T0; `extracts/v2/fabio/o-w5Gxss6T0_v2.md`).**

> "to identify a real fair value gap, you need to get inside the candle and you need to see how the volume transacted."
**Source GPS: o-w5Gxss6T0 | MIDDLE** (raw_transcripts_canonical/o-w5Gxss6T0_raw.txt, line numbers in the V2 file)

> "the lowest volume of interaction in all the area of value area. So where 70% of the volume got transacted is exactly this one is the level that goes from 24,318 to 24,317."
**Source GPS: o-w5Gxss6T0 | MIDDLE**

> "And what you will see thousand of times is that this is exactly where the price will reject."
**Source GPS: o-w5Gxss6T0 | MIDDLE**

"thousand of times" is his claim; no count is given (OURS: untested).

**ASR addition 2026-10-16 (Is1HvdfQm5c).** A gap read from a transcript we hold (Is1HvdfQm5c, ASR): he calls a small gap between two candles "inefficient volume" and a place to reload. This is the candle-gap reading, not the volume-defined fair value gap of this row's source (o-w5Gxss6T0); keep it as supporting colour only. Entry, stop, target NOT STATED.

> "this is inefficient volume because it created a micro gap"
**Source GPS: Is1HvdfQm5c | BEGIN** (ASR, Is1HvdfQm5c_raw.txt:266, [40:17])


### Fabio: unassigned
- ANG R31 (fZ): two "continuation short" trades that failed; setup not described: "The first trades that we took was a continuation short and we gave back two trades inside here." (fZ BEGIN, ANG R31).
- ANG R33 (jasv3L): a "trend following model" that took stops on a compression day:

> "So my trend following model took a straight stop loss."
**Source GPS: jasv3L-d8ZE | BEGIN**

  His trend-following model is never described in the transcripts we hold. FR-20 "Trend-following entry: absorption of counter-trend aggression inside momentum" now has a SOURCED line (o-w5Gxss6T0: "when you are in a momentum phase like this one and you can see a huge amount of aggression following an absorption, you can understand that the buyers are in control"); it may be this model and would then be FAB-2. No stop or target is stated for it.
- OURS-only model: V3 model A "LVN pullback trend" (enter a pullback to a low-volume node of the breakout leg). V3 P35: "not in these transcripts (FBR:28-29)". The idea now has a Fabio quote (Pz8f0wWW12M, section 4.2: "Usually, the market like to rebalance the low volume node before continuing in the direction of the trend."), but no entry, stop or target of his: the rule stays OURS, the rationale is SOURCED.

**ASR addition 2026-10-16 (Is1HvdfQm5c).** Names from the 2.5 h live session (Is1HvdfQm5c, ASR; one video each, no filled trade with entry and stop, so none becomes a FAB row). "Virgin POC test" inside profile framing (long bias); "last sniper" (a resting long at the last point of aggression of the sellers, removed when not filled); "deep effort" (his proprietary book-thickness study that marks who controls the auction). Candidates for a later row if a second video states entry, stop and target.

> "to capitalize is the virgin POC test"
**Source GPS: Is1HvdfQm5c | MIDDLE** (ASR, Is1HvdfQm5c_raw.txt:548, [1:24:51])

> "I try to make another last sniper, but we didn't got field."
**Source GPS: Is1HvdfQm5c | END** (ASR, Is1HvdfQm5c_raw.txt:766, [2:01:39])

> "now we are on the top of the range the deep effort it's a proprietary study and it's based on the thickness of the book so"
**Source GPS: Is1HvdfQm5c | END** (ASR, Is1HvdfQm5c_raw.txt:832, [2:12:20])


### 4.1 Tool family, not a setup: heat-map liquidity (was FAB-7)
Moved out of the setup list on 2026-10-16 (D3): the heat map is a tool; its only tradeable pattern (the protection wall and the reload) is FAB-5, the rest needs L2 history we do not hold.
1. **Name / trader.** Fabio (FawPrRUGNpk, a liquidity heat-map lecture; FR-17, FR-31 to FR-73: 34 rules need L2).
2. **What you see.** Resting limit-order walls on a heat map (darker = more important); price hits a wall and is absorbed; walls reload (icebergs); a break whose new level is then protected by fresh resting orders; the path of least resistance summed over five price levels; sweeps at all-time high/low, range extremes, the NY high.
3. **Entry, stop, target, management.** Rulebook paraphrases only (not verified here): FR-43 "Reload breakout entry and stop" ("breakout protected below the reload level"), FR-47 "Stop below next liquidity area", FR-44 target "next liquidity cluster", FR-58 partial when aggression stops at a ceiling. The one trade example is hypothetical:

> "So if I took a short from here, I would consider bringing my full take profit way lower than the low."
**Source GPS: FawPrRUGNpk | END**

4. **Context.** A directional bias first (FR-45); "you need to start with an idea" (FawPr BEGIN passage around the protection wall).
5. **BTC visibility: NO.** No order-book history (live only; bookDepth bands from 2023 are a coarse proxy, TOB s2.3). The aggression side (big trades, CVD) is visible, the liquidity side is not.
6. **Evidence.** 0 real trades (ANG R35 hypothetical).
7. **Gaps.** All thresholds UNDEFINED (FR s4). FawPr was extracted in three V1 chunks; no V2.

## 4.2 Merge 2026-10-18: five recovered transcripts and the V2 delta
Source files (raw promoted by cc3d27bf; V2 extracts all PASS the quote checker): `extracts/v2/fabio/{o-w5Gxss6T0,cUTsoU-15Tc,Pz8f0wWW12M,Khgj5q1-ln8,06R-ebyOhDI}_v2.md`. Identity check done 2026-10-18: all five are Fabio in the first person (competition record, Deep Charts, staged as fabervaale_*), and none duplicates a file already in raw_transcripts_canonical (8-word overlap with the nearest file under 0.3 %). Label rule: SOURCED = verbatim quote with file:line; OURS = our reading or number.

**FAB-9 Delta print zone (06R-ebyOhDI).** SOURCED: the zone is drawn from the previous swing leg (profile, big trades, delta) and is strongest where value area high, big trades and delta level overlap; short entry on the approach, protected above the area; a re-entry covers above the area and targets a swing point, reward quoted 1:3, 1:4, 1:5 "It depends on how much you want to be safe on the stop-loss placement". NOT STATED: stop distance, big-trade size, order type. BTC visibility PARTIAL (aggTrades give big trades and delta; his delta-level indicator is unpublished).

> "So you have a confluence of value area high, big trades and delta level. This one is a super strong area."
**Source GPS: 06R-ebyOhDI | BEGIN** (raw_transcripts_canonical/06R-ebyOhDI_raw.txt:53-54)

**FAB-10 Volume ledge (06R-ebyOhDI).** SOURCED: a ledge is a fast drop from a high-volume node to a low-volume node; it is not enough alone; aggressive trend-side orders in the candle body plus absorbed counter-traders confirm it, after which "you can already put a limit order here". Stop and target NOT STATED.

> "But you cannot just execute based on this. So you need to go to check what's happening here in details."
**Source GPS: 06R-ebyOhDI | END** (raw_transcripts_canonical/06R-ebyOhDI_raw.txt:112)

**Two filters, not setups (Khgj5q1-ln8).** (a) Daily bias: with a bias from profile framing, counter-bias setups are skipped. (b) Mandatory retest: a close beyond the area with no test is a momentum setup he does not take. Both are testable on our data without his tool; his deep-effort series is not reproducible from the words. His count "six R ... lost two ... four R positive" is a hindsight illustration on one chosen week (OURS: selection bias, not a result). Partial: one position out at 50 % of the full profit, runner left.

> "So, I had a clear bias for the day and for this I use profile framing. So, all the short setup if I have a bias, I'm not interested into taking, okay? So, I can save the counter trend setups."
**Source GPS: Khgj5q1-ln8 | MIDDLE** (raw_transcripts_canonical/Khgj5q1-ln8_raw.txt:158-164)

> "This one it's a momentum setup. Why momentum setup? Because it closed above it and never test. So, this one you couldn't take because the market don't give you a test."
**Source GPS: Khgj5q1-ln8 | MIDDLE** (raw_transcripts_canonical/Khgj5q1-ln8_raw.txt:178-181)

**U2 split (Pz8f0wWW12M).** Continuation: aggressive orders absorbed and the candle closes with the trend. Reversal: volume dries up into the extreme and a contrarian imbalance prints. No numeric thresholds are stated; any number is OURS and goes through DEV, one VALIDATION look, holdout once.

> "from the concept of vertical volume you can find an exhaustion where you can see that the market is pushing really strong, printing another green candle, but the volume is getting lower and lower. This is a dry up in volume, and usually what you see this in a pattern order flow is that you have a sudden reversal in price."
**Source GPS: Pz8f0wWW12M | MIDDLE** (raw_transcripts_canonical/Pz8f0wWW12M_raw.txt:418-425)

**V3 model A rationale (Pz8f0wWW12M).** See the unassigned block of section 4: idea SOURCED, rule OURS.

**FAB-7b retest entry (FawPrRUGNpk, CATALOG_DELTA N1; teaching illustration, no trade).** Noted with the heat-map family of 4.1 (needs L2) so that FR-43 is not read as breakout-only: "I can enter on the test" (FawPrRUGNpk_raw.txt:443), stop "below the wall reload", target the next liquidity level at 1:2 to 1:3. BTC visibility NO.

**Other items merged from `extracts/v2/fabio/CATALOG_DELTA.md`.** 1 % daily drawdown stop (0KyIEdvVKMQ: "If I reach 1% of draw down, I stop for the day."): a loss-side stop, different from the profit-side floor of fZlNGWvd2Ko ("if we go back to break even, we stop the session"). FAB-6 verbatim definition (StaphlRH8NQ, in FAB-6 above). The four non-intraday edges of StaphlRH8NQ (earnings drift, politician tracking, option premium, MVRV allocation) are OUT OF SCOPE for BTC intraday. Delta contradictions C1 to C6 stand as listed there. The rulebook line FR-13 "minimum 1:3" is NOT CONFIRMED (section 5).

**Counts after this merge.** Fabio setup rows: FAB-1, 2, 4, 5, 6, 8, 9, 10 (8 rows). Rows that gained SOURCED text: FAB-6 (rules), FAB-8 (definition), FAB-9 and FAB-10 (new). Real trades added: 0.

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
| Fabio R:R | FR-13 minimum 1:3 (0jM5): NOT CONFIRMED, the V2 read finds only the realised "almost 1 to three even more 1:5" (CATALOG_DELTA C5) | FR-74 prop risk geometry 1:1 to 0.75:1, max 1.5:1 (LQvv); cUTsoU-15Tc: "better to take 1 2 3 1 to 2.5" |
| Tom hit rate and payoff by setup type (SOURCED, T-3 hQ8sOq67x5o, quotes in section 2.1) | breakout 75 % typical (hQ8s); R:R 1:1 to 1.5:1 (uk4P, TOM-6); 80-90 % hit rate claimed for the 1-minute P model (uFxY, TOM-6) | intraday swing 35 % at about 4x risk; counter trading payoff "three to four" (hQ8s) against 1.5 at 40-45 % (k0zm5NYn0IQ) and greater than 3 at 30-40 % (BVpY) |
| Fabio stop in words | "initial stop is always 'here' on the chart" (the old tally, 0 of 8) | below the protection level, DyS79Eb92Ug (FAB-5); FawPr gives below-reload / below-next-liquidity for the heat-map variants |

## 6. Unread sources and which gaps they could fill
From research/transcript_inventory_2026-10-09.md (counts parsed by `transcript_inventory.py`): Tom 84 raw transcripts: 11 V2,
47 V1 only (9 of them gate PASS with anchors), 26 never extracted. Fabio 8 raw, all V1 only, 0 V2. Unread Fabio sessions:
FABIO_TRADE_LEDGER.md:48 and :90.

### 6.1 Tom, never extracted (26)
| id | title (inventory) | could fill |
|---|---|---|
| uk4PZV59nYw | The PERFECT trade entry: World Champion explains his EXACT breakout setup! | TOM-6 entry trigger, stop (rank 1 by risk/stop density) **(READ 2026-10-15, see 6.1a)** |
| gFJBg8Bsw68 | Trading World Champion reveals the BEST breakout strategy in 2026! | TOM-6 trigger, speed, stop **(READ 2026-10-15, see 6.1a)** |
| Kg6sYKgtkrY | The ONLY Trading Strategy you need for 2026 (PbD Method) | PBD definitions: P, b, D shapes used by TOM-1/2/8/9 (STR gap 3) **(READ 2026-10-15, see 6.1a)** |
| jXR1afMy-3o | PbD: The World's BEST trading strategy (explained in detail) | same **(READ 2026-10-15, see 6.1a)** |
| m3IMdc7QwN4 | PbD: The BEST trading strategy for times of crisis | same; TOM-1 in fast markets **(READ 2026-10-15, see 6.1a)** |
| Ly62G168MkQ | The Simplest Day Trading Strategy for Beginners (PbD Method) | same; simple entry/stop rules **(READ 2026-10-15, see 6.1a)** |
| ODdF0Bn_KSc | Perfect trade entry: Trading World Champion reveals exact strategy! | entry triggers for TOM-1/2/4 **(READ 2026-10-15, see 6.1a)** |
| YYYuaetck_0 | The #1 Trading Strategy for the Current Market | unknown setup; rank 2 by density **(READ 2026-10-15, see 6.1a)** |
| kKZCJui4S9U | THIS strategy puts you ahead of 99% of traders! | unknown; rank 3 **(READ 2026-10-15, see 6.1a)** |
| viT_VzF5Fsw | THIS Trading Strategy Delivers MAXIMUM Win Rates NOW! | TOM-7 scalp stop/target **(READ 2026-10-15, see 6.1a)** |
| uFxYcpiaOpw | My Simplest Trading Strategy (80-90% Win Rate) | TOM-7 or a high-hit-rate setup not catalogued **(READ 2026-10-15, see 6.1a)** |
| VOiy8mAALWA | The #1 Trading Indicator for 2026 | proof items (volume/footprint) **(READ 2026-10-15, see 6.1a)** |
| ridY2Z0hSQA | THIS is the World Trading Champion's Favorite Indicator! | proof items **(READ 2026-10-15, see 6.1a)** |
| YkclL6xgu-s | How powerful is Volume Trading REALLY? | TOM-1 A-C3 "thin" in his words **(READ 2026-10-15, see 6.1a)** |
| 1utSjHs_Mq8 | The ONLY Market-Profile-Video you will EVER need | TOM-2 balance edges, single prints, tails (TOM-5) **(READ 2026-10-15, see 6.1a)** |
| K8qtT2_axPo | Market Profile: How Trading World Champions REALLY read the Market! | same **(READ 2026-10-15, see 6.1a)** |
| 0CrkbfuIhkc | Crash or All-In? THIS is What Volume Profile Tells Us NOW! | context reading, HTF value **(READ 2026-10-15, see 6.1a)** |
| lO-Iptd29t4 | The ONLY Newstrading-Video you'll EVER need | partly read by GAP (G01-G18); TOM-1 A-C4 news, TOM-8/9 **(READ 2026-10-15, see 6.1a)** |
| 6BAzqewtPUk | Forget newstrading! THIS is the strategy of the trading world champion! | TOM-1 news condition **(READ 2026-10-15, see 6.1a)** |
| 9VN9y2DVtGQ | Forget Technical Analysis! THIS is the strategy of the World Trading Champion! | unknown **(READ 2026-10-15, see 6.1a)** |
| 2xnNPIyHGQ4 | Trading World Champions show: THIS strategy wins EVERY time! | unknown **(READ 2026-10-15, see 6.1a)** |
| 4VXpUjhKG2U | How to Always Win as a Trader! (3 Mistakes Every...) | management, mistakes (entry too early, TOM-1) **(READ 2026-10-15, see 6.1a)** |
| Sy-x5AQ9-Pk | The Only Technical Analysis Guide You'll Ever Need | unknown, beginner **(READ 2026-10-15, see 6.1a)** |
| VxN5IxTwpbE | How I Would Start Trading in 2026 (Beginner's Blueprint) | unknown, beginner **(READ 2026-10-15, see 6.1a)** |
| 15JoLK0PbMU | VIX Strategy revealed | day selection / volatility context **(READ 2026-10-15, see 6.1a)** |
| cw8LWQmec1E | Gold & Silver Bubble WARNING | TL T8 gold short context **(READ 2026-10-15, see 6.1a)** |

### 6.1a Pass status (2026-10-15, line by line from raw_transcripts_canonical/<id>_raw.txt)
Read in inventory order: 26 of 26 (batch 1: 12, batch 2: 7, batch 3: 7). Pass complete.
Result of the 12 (no fees, no backtest, no VALIDATION/HOLDOUT; any number added is OURS or his, labelled where used):
| id | read | what it gave |
|---|---|---|
| uk4PZV59nYw | READ | TOM-6: clear space to the left, order flow, strong-pullback-strong bar pattern, R:R 1:1 to 1.5:1, exit when momentum reverses. No stop, no trade taken **(READ 2026-10-15, see 6.1a)** |
| gFJBg8Bsw68 | READ | TOM-6 (single print variant, news-then-consolidation) and new TOM-12 (break-in) with trapped-participant logic. No stop, no trade **(READ 2026-10-15, see 6.1a)** |
| Kg6sYKgtkrY | READ | market overview (Bitcoin B structure, 6E, S&P, silver, copper). No setup. BTC context only: "no acceptance in the old balances" reading; nothing quoted **(READ 2026-10-15, see 6.1a)** |
| jXR1afMy-3o | READ | PBD definitions (P/B accelerate, 30 % of markets, D balance, 70 %), break-in, target = start of impulse (TOM-12) **(READ 2026-10-15, see 6.1a)** |
| m3IMdc7QwN4 | READ | PBD definitions P/B/D in his words, B break-in, failure case: run below the start of the move (TOM-12) **(READ 2026-10-15, see 6.1a)** |
| Ly62G168MkQ | READ | closing prices not extremes, impulse then sideways phase, D area counter trading, failure rule: stops hit and price runs back in means a bigger balance. No stop distance **(READ 2026-10-15, see 6.1a)** |
| ODdF0Bn_KSc | READ | trend / smart-zone / setup order (TOM-4 filter); the four trader types by temperament. No stop **(READ 2026-10-15, see 6.1a)** |
| YYYuaetck_0 | READ | NEW setup TOM-11 (crude oil leads, index future follows). No stop **(READ 2026-10-15, see 6.1a)** |
| kKZCJui4S9U | READ | mindset only. No setup, no quote used **(READ 2026-10-15, see 6.1a)** |
| viT_VzF5Fsw | READ | a failed counter short with its exit reason in words (TOM-2 evidence, first taken trade there); flip long (TOM-12) **(READ 2026-10-15, see 6.1a)** |
| uFxYcpiaOpw | READ | TOM-6: single print open, P on 1-minute, higher close; "once a day", "30 % of market phases" **(READ 2026-10-15, see 6.1a)** |
| VOiy8mAALWA | READ | TOM-1/TOM-2 filter: stop counter trades after shifting VPOCs (two days), footprint "liquidity is gone, finished auction" proof **(READ 2026-10-15, see 6.1a)** |
| ridY2Z0hSQA | READ | the three static tools (market profile, volume profile, footprint) and the fair/unfair price question; value-area shift = accepted new fair prices. No setup, no stop, no quote used (batch 2) |
| YkclL6xgu-s | READ | TOM-4: stop below the last volumes, target at old large volumes, volume must shift first; open and closing-auction volume as activity gauge. First stated stop gained (batch 2) |
| 1utSjHs_Mq8 | READ | profile basics; single prints revisited, weak highs/lows taken out: new TOM-13 (batch 2) |
| K8qtT2_axPo | READ | profile types (normal, variation, trend, double distribution): TOM-13 fill rule; "context, not a strategy" (batch 2) |
| 0CrkbfuIhkc | READ | index, Bitcoin and Mag 7 level reads; fast re-entry into old balance as risk sign (TOM-12 note); acceptance levels are states, no stops (batch 2) |
| lO-Iptd29t4 | READ | news gaps: gaps are not always closed; trade the gap or the trend only after a range forms and leaves; breakaway gaps stay open (TOM-8/9 notes) (batch 2) |
| 6BAzqewtPUk | READ | news shock then inside bar then reaction to the origin: new TOM-14 (batch 2) |
| 9VN9y2DVtGQ | READ | against trend lines and indicators; order of reading (who dominates, then dynamic setup, then order book). No setup, no stop, no quote used (batch 3) |
| 2xnNPIyHGQ4 | READ | new TOM-15: three in a line, inside bar, outside bar, each with location and volume conditions (batch 3) |
| 4VXpUjhKG2U | READ | TOM-2 and TOM-6 notes: counter only in balance ("short at the top and long at the bottom"), breakout needs imbalance, the second attempt; against moving averages and Bollinger bands. No stop (batch 3) |
| Sy-x5AQ9-Pk | READ | TOM-6 notes: dynamic impulse then sideways phase, tested zones are checked off, early breakout entry before the old high. No stop (batch 3) |
| VxN5IxTwpbE | READ | TOM-2 proof (finished vs unfinished auctions); 70/30 balance vs trend; one wording slip recorded under TOM-2. Trader-type content ignored (batch 3) |
| 15JoLK0PbMU | READ | VIX 20 as regime figure and "political markets have short legs" (TOM-14 context); "buy when the cannons thunder" is a market saying, no setup. BTC has no VIX (batch 3) |
| cw8LWQmec1E | READ | new TOM-16: hedger-driven top in gold and silver, short on the break below the last big buyers. No stop (batch 3) |
Setups that gained a stated stop from batch 1: 0 (the invalidation exit in viT_ is a state, not a price; recorded under TOM-2). New setups: 2 (TOM-11, TOM-12).
Batch 2 (7 videos): setups that gained a stated stop: 1 (TOM-4, location only: below the last volumes). New setups: 2 (TOM-13, TOM-14). Numbers added: none.
Batch 3 (7 videos): setups that gained a stated stop: 0. New setups: 2 (TOM-15, TOM-16). Numbers added: none (the VIX 20 is his, quoted). Pass total: 26/26 videos read, 6 new setups (TOM-11 to TOM-16), 1 setup gained a stated stop (TOM-4, location only).

### 6.2 Tom, V1 only (47): the ones that carry setup fields above
Every STR quote (TOM-2, -4, -6, -7) comes from V1 extracts whose gate FAILS with NO-GPS (BVpYGKz9PBU 0/35, 43JaKHRvxHk 0/25,
qLnQan0KGmQ 0/28, Ld1dhjGdTCA 0/38, NkQeOVDTAec 0/25, YmygDgtoxO8 0/22): a V2 pass of these six would re-anchor TOM-2/4/6/7 and
may give the missing stops. The trade videos themselves are V1 only (k0zm5NYn0IQ, n7ZSkjb7JXs, ujedEcmvBMk, T6hDJcHrVBM,
l8RZrBfzvp4, UOBgXV20yCM, OUM9LYwL8eA); V2 spec quotes their captions directly. Scalping videos G0CiJcuXCRs and YVUcLTsCOZI
(V1, no anchors) are the best source for TOM-7 stops. oa8kxSLLkAo (footprint, 0/27) for TOM-1 A-P6 footprint reading;
Vd83oo_geMk (heat map, 0/42) for Tom's view of FAB-7-type liquidity; 3o1VVsfBmmU ("The #1 Trading Setup for 2026", 0/34; ANG R25
"10 ticks" stop example) may name a setup not catalogued here; yRvMW6lgN1o (TOM-3) and gWjHq5UMisY / hQ8sOq67x5o / pgdmKLJ0hhA
(highest risk/stop density, V2 candidates per the inventory) for swing setups not catalogued here.
Status 2026-10-16 (Fable audit section 3): `G0CiJcuXCRs` -> TOM-17; `3o1VVsfBmmU` -> section 2.1 (T-2: stop for any level entry, management by speed, top-down order); `hQ8sOq67x5o` -> sections 2.1 and 5 (T-3); `yRvMW6lgN1o` -> TOM-3 fixed. Still V1-only: `YVUcLTsCOZI`, `gWjHq5UMisY`, `pgdmKLJ0hhA`.

### 6.3 Fabio (8 raw, all V1; plus videos without raw transcripts)
| source | state | could fill |
|---|---|---|
| 0jM5Y31YJak, 8CWKfoSJu3c, jasv3L-d8ZE | V1 only; applied readings in FTM/V3 | a line-by-line pass like LBL for each: initial stop words for FAB-1/2/3, the "trend following model" (ANG R33) |
| FawPrRUGNpk | V1 in three chunks | FAB-5 and FAB-7 stop/target words (FR-43, FR-47 verbatim) |
| LQvv5xgy_ik | V1 | FAB-6 IVB rules beyond one sentence |
| 0KyIEdvVKMQ, StaphlRH8NQ | V1 | mental models; FR-80..85 (non-MTS hypotheses) |
| fZlNGWvd2Ko | V1 + LBL (read line by line) | done |
| o-w5Gxss6T0 | raw promoted 2026-10-18, V2 `extracts/v2/fabio/o-w5Gxss6T0_v2.md` | done: FAB-8 definition, FR-20 line; FR-16..19 and FR-93..95 not re-checked line by line |
| cUTsoU-15Tc, Pz8f0wWW12M, Khgj5q1-ln8, 06R-ebyOhDI | raw promoted 2026-10-18, V2 extracts in `extracts/v2/fabio/` | done (section 4.2): FAB-6 rules, LVN rationale, U2 split, bias and retest filters, FAB-9, FAB-10 |
| 9IliXww64uM, DyS79Eb92Ug | canonical transcripts since P2 (2026-10-16), used in FAB-4, FAB-5, FAB-1 and section 2.2 | done for the quoted passages; the rest of DyS79 (2.4 h) is not line-by-line read |
| Jpd96fLqr5M, gLHd20jE8UQ | frames read, no captions on disk | the big-trade size slide "30 to 40 on NQ" (gLHd, FL:50; secondary presenter, not Fabio's own words, H6) |
| 9I5vTvwsMBk | not downloaded (f398 not available, FL:48) | unknown live session |
| Is1HvdfQm5c | ASR transcript (faster-whisper small.en, 2026-10-16, raw_transcripts_canonical) read in full, V2 extract extracts/v2/fabio/Is1HvdfQm5c_v2.md (333 rows, 9 blocks: 0 confirmed live fills with stated entry and stop; mostly illustration and viewer Q&A) | done; numbers are ASR numbers, frames are the arbiter |
| xUyqIjCfZzg | 3.8 h; unread (FL:57); ASR transcription started 2026-10-16 (resumable job, see research/fabio_asr_2026-10-16/ASR_RUN.md); two speakers (Fabio and Carmine Rosato) | live session: more FAB-2/FAB-5 trades |

## 7. What this catalog does not settle (for the next steps)
1. Initial stop in words (a location, never a distance as a rule): Tom 5 of 16 rows (TOM-1a, 1b, 2, 3, 4), Fabio 1 of 6 (FAB-5, below the protection level). Every other stop is a chart point ("here") or a frame value. The blind eye-read marking should record where each reader would put the stop and the next extraction should search for it.
2. Session anchors on BTC (cash open, pre-market, US open, closing auction) are needed by TOM-1, TOM-8/9/10, FAB-6. Any choice is OURS.
3. One setup is mostly our structure (FAB-8); FAB-4 now has his words (9IliXww64uM) but its entry stays a chart point; one is only ours (V3 model A).
4. Real-trade evidence is concentrated: TOM-1a 11 of Tom's 22 assigned examples (incl. 1 candidate) and FAB-5 11 of Fabio's 17. TOM-6, -7, -9, -10, -11, -12, -14, -15, -16, -17 and FAB-6, -8 have none; TOM-4 has 3 since the merge; TOM-2 has 1 (a loss).
