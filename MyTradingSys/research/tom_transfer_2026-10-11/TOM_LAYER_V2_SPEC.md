# TOM LAYER V2 SPEC - PART A: what Tom trades (card tom-layer-v2-spec, 2026-10-13)

Status: part A only. No code, no tuning, no outcome or holdout was read. Part B (per-market cost, stop-width transfer, build
cards) is card `tom-layer-v2-cost`. Sources: the seven trade-video transcripts in `F:/MTS/data/tom_videos/<id>.txt`
(cited `id:lines`, quotes verbatim, checked by `scripts/dev/check_spec_quotes.py`), the repaired ledger
(`TOM_TRADE_LEDGER.csv`, `TOM_LEDGER_CANONICAL_GROUPS.csv`), `RECALL_DAX.md`, `PRE_REG_DAX.md`,
`SetupCandidatesBuilder.java`. Captions are AI-translated: a quote proves what Tom says he looks at, never a price, date or time
(RECALL_DAX section 1). Ledger dates are unverified (card `rv-fix-tom-ledger-date-column`); nothing below depends on one.

## 0. Decisions (read this first)
1. **One family carries the layer: the imbalance fade (family A).** 10 of the 12 ledger groups are one trade idea: an
   opening or pre-market push that ran on no volume, sold from its top back to the volume below. The ledger's sub-labels
   (premarket, open, counter, after_rally, re-entry) are entry paths and sessions of that one idea, not families.
2. **Re-entry is a management rule of A, not a family.** T2b and T3b are the same idea taken again after a stop or partial.
3. **T4 is a second, separate family (C: gap-close pullback long)** with one ledger trade. Written down, not encoded yet.
4. **Fee-net acceptance test is fixed before any build (section 1).** Recall on the ledger is a wiring check only; the
   ledger can never show edge (Tom chose which trades to publish, and every group is EXPOSED).
5. **Design/check split is frozen now by a rule that reads no outcome (section 7):** design = sessions whose transcript
   was read to write these rules; check = the two sessions that have frames but no captions (T11, T12).
6. **Live gaps answered:** G2 the engine's `below_val -> long only` contradicts a ledger trade (section 8); G3 Tom's
   "unhealthy" is a move without volume under it, not a CVD divergence and not a position against value (section 8).
7. **No thresholds are invented.** Where Tom gives no number the cell says NO-SOURCE and part B must either find a
   source or express the condition relative to the same session (rank, not level). Sourced numbers: stop 20 DAX points
   when no reference exists; hit rate 40-45 %; minimum R:R 1.5; entry R:R about 6.

## 1. Fee-net acceptance test (stated up front; every prior layer showed about zero edge before fees)
Tom's own arithmetic, from his words: "have a hit rate somewhere in the range of 40 to 45% with such counter trading
strategies, then you need at least a riskreward ratio of 1.5" (k0zm5NYn0IQ:549-552). Expectancy per trade = p x RR - (1 - p):
at RR 1.5 that is 0.00 R (p 0.40) to 0.125 R (p 0.45); at RR 2.0 it is 0.20 R to 0.35 R. So the claimed edge is a few
tenths of R at best, and cost per trade must be small against 0.1 R.

| Market | Stop (Tom's frames: 20-63 points, 0.08-0.26 % of price) | Round-turn cost | Cost in R |
|---|---|---|---|
| FDAX, `FEES_FDAX` (0.000005 of price per side = 0.24 point at 24,000) | 20 points | 0.24 point | 0.012 R |
| FDAX + 1 point slippage on the stop leg (PRE_REG stress) | 20 points | 1.24 points | 0.062 R |
| FDAX | 63 points | 0.24 point | 0.004 R |
| BTC perp, all taker (10 bps round turn, fees.py:8-10) | 0.079 % of price | 0.10 % | 1.27 R |
| BTC perp, all taker | 0.255 % of price | 0.10 % | 0.39 R |
| BTC perp, maker in / maker target / taker stop (`FEES_DERIBIT`) | 0.079 % | 0.05 % on losers only | 0.63 R per loser |

Acceptance test, frozen (same bar as PRE_REG_DAX "Pass bar", applied to family A candidates only):
- Market: DAX first. Dev period, then holdout read once, both with every ledger session removed (section 7).
- PASS = at least 100 filled trades in the period AND 95 % CI lower bound of **net** R > 0 under `FEES_FDAX` plus 1 point
  slippage on stop and timeout legs AND net R above the random-entry null (same day, same side, same distances).
- Gross R is reported beside it but decides nothing. Fewer than 100 fills = "insufficient N", not a pass.
- BTC: not tested with DAX-sized stops. The table shows cost of 0.4 to 1.3 R per trade against a claimed edge of
  0.1 to 0.35 R: it cannot pass by arithmetic. A BTC test needs the stop-width transfer rule of part B first, and then
  the same bar with `FEES_ALL_TAKER`.
- FAIL on DAX dev = stop: no holdout read, no BTC transfer, the family is recorded as "no edge shown on home market".

## 2. Family A: imbalance fade - observable conditions
Tom's frame for every such trade: "First, you have an idea. Second, you have proof that it's really time now to implement
the idea. And third, you have a really clean risk management" (zQTbdEweG3c:28-32). The spec keeps that order.
Side: short in all 10 ledger groups. A long mirror has no ledger trade and no quote in these videos: NOT ENCODED.

### 2.1 Idea (context; all must be observable before any proof is counted)
| id | Condition (observable form) | Tom's words | Threshold |
|---|---|---|---|
| A-C1 | An impulse leg from the session start (pre-market or cash open) that expands the opening range far beyond a normal one; single prints in the profile of that leg | "started way down here and then suddenly shot up just like a powerful rocket" (T6hDJcHrVBM:114-116); "the initial balance is so large meaning the expansion of the trading opening is just very very big" (k0zm5NYn0IQ:361-364); "there was an immediate impulse and then there was a little, let's call it lethargy" (l8RZrBfzvp4:70-72) | size NO-SOURCE; use rank of the opening range against the prior sessions' |
| A-C2 | Price is above the prior value area (previous day or previous week) | "we are of course above the previous day. That means it's a very risky trade" (k0zm5NYn0IQ:51-53); "we're above last week's value" (n7ZSkjb7JXs:102-103); "the market was completely outside of the previous day's range" (l8RZrBfzvp4:55-57) | none needed |
| A-C3 | The session profile is thin at the top of the leg and the nearest volume node lies below (no volume traded above the session VPOC area) | "I can clearly see that there's no liquidity left" (k0zm5NYn0IQ:21-22); "There simply wasn't any more liquidity above which you can see perfectly here. Up here it just stopped" (n7ZSkjb7JXs:78-80); "there was simply no liquidity left here and the liquidity was down here" (zQTbdEweG3c:234-236) | "thin" NO-SOURCE; relative to the same session's POC volume |
| A-C4 | The push has no fundamental cause and other index/crypto markets are not confirming it | "if for example fundamental news had led to one market being extremely strong and the other not then that's a different story" (T6hDJcHrVBM:291-294); "especially if there's no fundamental sustainable story" (l8RZrBfzvp4:87-89) | NOT_IN_DATA for news; cross-market leg is observable (ES, NQ, BTC same-window return) |

### 2.2 Proof (what shows "it's really time"; count per trade, no minimum number is sourced)
"If you make trades against the trend, then you need many, many parameters that speak in your favor" (zQTbdEweG3c:23-26) and
"You need many, many different factors that all have to fit together" (n7ZSkjb7JXs:329-330). Tom gives no count. The engine's
"3 proofs" bar is NO-SOURCE for this family; part B must not tune it. Report recall at each count instead.
| id | Proof (observable form) | Tom's words | Data |
|---|---|---|---|
| A-P1 | Finished auction at the high | "we also had a finished auction. That means the market formed a completed auction at the top" (k0zm5NYn0IQ:84-86) | engine has it; needs aggressor data |
| A-P2 | Rejection from the high, and it is fast | "The market showed me that there is rejection up here. And the market also showed me that the speed with which it rejected this is promising for me" (k0zm5NYn0IQ:469-473) | OHLC |
| A-P3 | P-shaped leg whose upside breakout fails and price is accepted back inside the balance | "we have a beautiful P setup here. We broke out of this setup to the upside, moved into the resistance area, and simply didn't have any more liquidity up here" (n7ZSkjb7JXs:55-59); "a P pattern formation with a so-called fake breakout and a renewed acceptance of this balance" (T6hDJcHrVBM:220-222) | profile + OHLC |
| A-P4 | Inside bar at the top | "It had already shown me a very nice inside bar right here. And that is exactly what prompted me to take action" (T6hDJcHrVBM:147-150); "it's also forming an inside bar. That's always a sign of waiting of balance" (k0zm5NYn0IQ:334-337) | OHLC; timeframe NO-SOURCE (5-minute chart is the one he names, n7ZSkjb7JXs:290-293) |
| A-P5 | An old high / pre-market high was just taken out (weak-high ledge passed) | "trading well above those old highs which essentially formed a ledge, a weak high from small traders" (T6hDJcHrVBM:153-155); "We had taken out these highs here. Yes, you can see it clearly, typical pre-market highs" (ujedEcmvBMk:34-37); "we went out above the corresponding high again" (zQTbdEweG3c:140-141) | OHLC |
| A-P6 | Selling shows at the top: large sell volume in the stall, sell surplus in delta, a big seller in the footprint | "this lethargy was characterized by large sales volumes. And that prompted me to plan a short trade there" (l8RZrBfzvp4:72-76); "in these last two candles we had a selling surplus" (k0zm5NYn0IQ:249-250) | aggressor data: NOT on the DAX CFD feed |
| A-P7 | Price trades back below the opening price / the impulse candle (opening buyers under water) | "Here the market has already looked below the opening trade price" (l8RZrBfzvp4:100-102) | OHLC |
| A-P8 | b-shaped pullback lower on a smaller timeframe (acceptance below the high) | "we got a wonderful B setup with a pullback here in an even smaller time frame" (zQTbdEweG3c:144-146) | profile |
| A-P9 | Order book empty above | "in the order book. There's nothing left" (k0zm5NYn0IQ:300-301) | live only; no history |
| A-P10 | Retail derivative sentiment heavily long (UX sentiment) | ujedEcmvBMk:127-141, n7ZSkjb7JXs:139-145 (paraphrase, not quoted) | NOT_IN_DATA |

### 2.3 Entry paths (one family, three ways in; Tom names them himself)
"first philosophy up here, high risk. Second philosophy, pullback. Third philosophy, momentum trader" (l8RZrBfzvp4:212-214).
| Path | When | Tom's words | Ledger |
|---|---|---|---|
| A1 at the top | idea + proofs at the high, before price has left it | "For the first position, I'm setting a stop-loss of 20 points in the DAX" (k0zm5NYn0IQ:22-24); he calls it "really risky" (l8RZrBfzvp4:203-205, paraphrase) | T1, T2, T5, T6, T7, T11, T12 |
| A2 pullback after proof | price has rejected, traded through the first buying zone, then pulls back | "Anyone who wants to play it safe with such counter trades logically has to wait until this let's call it bullish zone here where you can also clearly see the liquidity gets traded through" (k0zm5NYn0IQ:316-321) | T3 (after the pre-market highs were taken and rejected), T2b |
| A3 range break | price leaves the top balance downward | "if I now see that we actually break out of this range to the downside, then I would definitely look for another position down here" (k0zm5NYn0IQ:308-312); "we went back into the price range and then we actually went below this price range" (ujedEcmvBMk:154-156) | T3b, the T2b third lot |
Order type (limit or market) is not stated in these videos: NO-SOURCE.

### 2.4 Stop
| id | Rule | Tom's words |
|---|---|---|
| A-S1 | Above the level where the seller sits / above the top volume bell; a context level, not a distance | "my stop loss is immediately above the 258" and "the aggressive seller is still there. If it goes above that, it can get uncomfortable" (ujedEcmvBMk:67-68, 71-74); "the stop loss was set above the bell" (n7ZSkjb7JXs:299-301); "there were strong sellers here. This means your stop loss is definitely in a great position here" (l8RZrBfzvp4:126-128) |
| A-S2 | No reference above (new highs): fixed 20 DAX points | "The simple reason for this is that I don't have any reference values up here" (k0zm5NYn0IQ:24-26) |
| A-S3 | Adds and re-entries: above the last traded volume | "my stop loss is now set exactly above the last volume levels. And if we push above here again, then it's over anyway" (k0zm5NYn0IQ:460-463) |
Frame-observed widths: 20, 22, 23, 36, 46, 63 points on FDAX; 6 points on ES. Width is an output of A-S1, never an input.

### 2.5 Target
| id | Rule | Tom's words |
|---|---|---|
| A-T1 | Final: the start of the impulse / the liquidity below it | "we'll take out the entire distance below the start of the impulse" (T6hDJcHrVBM:170-172); "I assume we'll go to the start of the corresponding impulse" (n7ZSkjb7JXs:245-247) |
| A-T2 | First: the nearest volume node or VPOC below; prior value area high | "this is the price range where the market was in equilibrium and where I then simply expect a reaction could occur" (zQTbdEweG3c:191-195); yesterday's value area high (k0zm5NYn0IQ:683-684, paraphrase) |
| A-T3 | Intraday gap / low-volume node as an intermediate target | "a huge intraday price gap during main trading hours. And those are always nice areas that I like to define as targets" (ujedEcmvBMk:103-106) |
| A-T4 | Place the target a little before the level everyone sees | "I would rather set my take profit a few points away from this range because often it is exactly the case that such levels that everyone sees" (l8RZrBfzvp4:151-155); "a few points" is NO-SOURCE as a number |
| A-T5 | Take it at the predefined level, do not extend | "it's always important to simply use predefined price ranges where you take your profits" (ujedEcmvBMk:254-257) |
R:R at entry: "In terms of riskreward ratio, we're currently at about 1:6" (k0zm5NYn0IQ:93-96); frames show 2.5 to 6.5.

### 2.6 Management
| id | Rule | Tom's words |
|---|---|---|
| A-M1 | Add when sellers show again and the added risk is small | "I'm going to add another position here because the risk is extremely small for me right now" (n7ZSkjb7JXs:163-165) |
| A-M2 | Do not trail at the start when R:R is about 6 | "Trailing the stop loss is something a lot of people like to do. In this case, I don't do that" (k0zm5NYn0IQ:194-196) |
| A-M3 | Partial when momentum stalls at a level or before a low-volume area | "I've now closed a small position here because I simply saw that the market wasn't showing any more action there for the time being" (n7ZSkjb7JXs:273-276); "Whenever the last volumes before such a price range are not traded, caution is advised, which prompted me to first reduce my position" (ujedEcmvBMk:119-122); "Take out one position here and the rest stays in" (T6hDJcHrVBM:247-249) |
| A-M4 | Stop to no-loss once a new balance has formed below | "it's time at the latest after a retrace to get out of the whole thing. Therefore, from now on, it's simply effective to definitely place the stop loss here" (k0zm5NYn0IQ:614-619) |
| A-M5 | Re-entry after a stop is allowed only on a fresh signal with the idea intact | "Then I would look for another position. If necessary, I would look for one if I saw again that the market is giving up its liquidity there" (k0zm5NYn0IQ:264-268); "Then you have the opportunity, if you get another signal, to play the whole thing again" (zQTbdEweG3c:168-170) |
| A-M6 | Reduce risk into the cash open when the trade started pre-market | "the closer we get to the cash open where by the way I also want to reduce risk" (n7ZSkjb7JXs:193-196) |
Lot counts, partial sizes and the number of re-entries allowed: NO-SOURCE (frames show 1 to 4 lots, one re-entry per session).

### 2.7 Session
Pre-market and the cash open of the DAX, morning only in the ledger. "the market phase where the highest liquidity is
present between 8:30, 9:00 and 17:35" (T6hDJcHrVBM:94-97). Pre-market carries less size: "taking on too much risk at this
time of day isn't really that effective" (n7ZSkjb7JXs:133-135). Clock times in the ledger are recording clocks, not
executions; the session of a trade is used as a label (pre-market / open / morning), never as a minute.

## 3. Counterexamples and invalidation (family A)
Counterexamples in Tom's own words, where the conditions were present and the trade lost or nearly lost:
| Case | What happened | Source |
|---|---|---|
| T2 first entry | all of A-C1..C3 and A-P1 stated, then new highs and the stop | "Now we've been stopped out and that's just part of it. So, I can definitely see that there's still no liquidity being played up here" (k0zm5NYn0IQ:272-275) |
| T1 session, earlier attempt | stopped before the shown trade | "I was already a bit too early this morning. Took a stop loss as well" (n7ZSkjb7JXs:31-33) |
| T7 session, earlier attempt | stopped in the pre-session | "I had already been stopped out in the pre-session when I was a bit too early, losing one R" (l8RZrBfzvp4:175-177) |
| T3 | stop run before the re-entry (trader-stated; no frame shows the fill) | "the market then shot past my stop-loss level that I had drawn in here, flushing me out of the market" (ujedEcmvBMk:144-147) |
| T5 | price went back above the entry and missed the stop; by his own account luck (T6hDJcHrVBM:208-217, paraphrase) | - |
| Base rate | he expects to lose more often than win | "such counter trades, they often get stopped out again" (zQTbdEweG3c:33-34); "it should definitely be in the range of 40 to 45%" (k0zm5NYn0IQ:111-113) |
Three of five design sessions show a losing first attempt that is not a ledger row. A backtest must count every attempt.

Conditions under which Tom does NOT fade (the family must not fire):
- Volume builds above: "if the market were to accumulate large volumes there then yes I would definitely be looking for a long position" (k0zm5NYn0IQ:357-360).
- A real cause: fundamental news behind the move (T6hDJcHrVBM:291-294, quoted in A-C4).
- A true breakaway gap. He fades this one because "we're not at the all-time high and didn't gap out of a range" (zQTbdEweG3c:87-89).
- Balance after a trend alone is not enough: "That doesn't mean it's going short yet. It can just as easily continue long" (zQTbdEweG3c:110-111).
- A P shape alone points the other way: "a P is usually something that strategically leads to a trend continuation" (T6hDJcHrVBM:161-163).

Trade invalidation (exit or no entry): aggressive buying appears at the top ("that suddenly aggressive buying happens up
here in the market and I haven't seen that so far", k0zm5NYn0IQ:240-243); price accepted above the A-S1 level; after the
first leg down, a retrace back above the new lower balance (A-M4).
Family invalidation (ours, not Tom's): the section 1 test fails on DAX dev, or check-set recall is 0 of 2 (section 7).

## 4. Family C: gap-close pullback long (T4 only; written, not encoded)
Idea: an opening gap far outside the previous day with no news behind it tends to close. "whether this gap that's present is
a gap that's likely to be closed or if there's a fundamental news story behind it" (UOBgXV20yCM:76-78); "Often on Mondays, we
have extremes in one direction or the other" (UOBgXV20yCM:84-85). Entry: "after the market made a pullback here and gave me a
buy signal here" (UOBgXV20yCM:89-90); the buy signal itself is not described: NO-SOURCE. Target: Friday's value ("Here was the
value. That was me profit target", UOBgXV20yCM:137-138), taken without extending. R:R: "an average risk-reward ratio of a good
2 2.5 as a rule" (UOBgXV20yCM:107-108). Stop rule: not stated (frame: 30 points). One trade is not a family to test: parked
until the ledger holds at least three. `conditions/gap_rules.md` (27 rules) stays the reference; it is not coded.

## 5. Ledger map: every group to exactly one family, with its rule path
Five written out in full (the card's check), the rest in one line. Dates deliberately omitted.
| Group | Family | Path | Rule path |
|---|---|---|---|
| T1 (n7Z, pre-market) | A | A1 | C2 above last week's value; C3 no volume above today's VPOC; P3 P setup broke up into resistance and came back; stop S1 above the bell; add M1 at break-even; partials M3 where action stalled; M6 reduce before the open; target T1 start of the impulse. Earlier attempt stopped (counterexample). |
| T2 (k0zm, open) | A | A1 | C1 oversized opening range; C2 above previous day; C3 no liquidity; P1 finished auction; stop S2 fixed 20 points (no reference); R:R about 6; no trailing M2; stopped out. |
| T2b (k0zm, same session) | A | A2, then A3 add | re-entry M5 on a fresh finished auction with liquidity still absent; P4 inside bar; add on the range break; stop S3 above last volume; P2 fast rejection; partials M3 at the low-volume node and at yesterday's value high; M4 stop to no-loss after the new balance. |
| T3 (ujed, morning) | A | A2 | P5 pre-market highs taken out, then rejected; context short from the weekly profile (VPOC, single prints); stop S1 above the level the seller defended; target T3 intraday gap; partial M3 before the untraded volume; then stopped (trader-stated). |
| T5 (T6hDJ, open) | A | A1 | C1 rocket from the open with single prints; C4 other markets falling; P4 inside bar; P5 above the old-high ledge; C3 liquidity moving lower; stop S1 above the weekly-profile level; target T1 below the start of the impulse; M3 one lot out, M4 stop to no-loss. Price went above the entry first. |
| T3b | A | A3 | re-entry M5 after the stop, on price back inside then below the range. |
| T6 (alias T10) | A | A1 | C3, P5, P8; R:R logic only; stop and target have no order label. |
| T7 (ES) | A | A1 | C2 outside previous day, C3 thin above, P6 selling in the stall, P7 below the open; target prior value area, T4 a few points early. |
| T11, T12 | A (check set) | A1 by frame | no captions: family assigned from the frame (short at the top of a morning push, R:R 3.4 and 6.2). Rule path is what the check measures. |
| T8 (gold) | A candidate | unknown | entry not shown: excluded from every recall count. |
| T4 (alias T9) | C | pullback | section 4. |

## 6. Engine today vs v2 (keep / change / drop)
| Engine item (SetupCandidatesBuilder.java) | Verdict | Why |
|---|---|---|
| `ct_short` at VAH / swing high / prior-day VAH zones (:417-421) | CHANGE | The zone must be the session extreme of the impulse leg (A-C1, A-C3). RECALL_DAX: at T2, T5, T6 no engine zone sat at his price. Blocked in `trend_healthy`, which is exactly when he fades (section 8). |
| `ct_long` (:422-424) | PARK | No ledger trade, no quote in the trade videos. Not part of v2 until sourced. |
| `tc_long` at VWAP in a healthy uptrend (:438) | PARK | The only ledger long (T4) is a gap-close pullback, not a VWAP pullback. |
| `scalp_long` / `scalp_short` at VWAP in balance (:433-436) | PARK | No ledger trade. |
| no `tc_short` / range-break short | ADD (path A3) | T3b and the T2b add. |
| `determineDirections`: `below_val -> long only` (:259-263) | DROP as a gate | Contradicted by T3/T3b (section 8, G2). |
| `classifyState`: `trend_unhealthy` only when `cvd_slope` is divergent (:248) | CHANGE | Tom's unhealthy = no volume under the move (A-C3). CVD divergence is not in these videos: NO-SOURCE for family A. |
| Proof: finished auction, rejection wick, absorption, delta flip | KEEP | A-P1, A-P2, A-P6. Absorption and delta need aggressor data (not on the DAX CFD). |
| Proof: speed (not counted since D4) | CHANGE | Count it only as speed of the rejection from the high (A-P2). |
| Proof: volume spike 2.0x over 240 bars | DROP | Already NO-SOURCE (B144); nothing here sources it. |
| Proof: book imbalance | KEEP live-only | A-P9; never in a historical test. |
| Missing proofs | ADD | A-P3 failed P breakout, A-P4 inside bar, A-P5 ledge passed, A-P7 below the open, A-P8 lower b-shape. All OHLC or profile: testable on the DAX CFD. |
| "3 proofs needed" | NO-SOURCE | Report recall and fire rate at each count; do not pick the count from outcomes. |
| Verdict net R:R with the BTC perp fee term | CHANGE in part B | Fee per market (section 1). |

## 7. Frozen design/check split (grouped by underlying trade and session; no outcome read)
Unit = session (one video-day), because trades in one session share context and are not independent. Aliases collapse first
(T9 into T4, T10 into T6, the second-video rows into T3/T3b).
| Session | Groups | Set | Why |
|---|---|---|---|
| S1 n7ZSkjb7JXs | T1 (+T8, excluded) | DESIGN | transcript read for this spec |
| S2 k0zm5NYn0IQ | T2, T2b | DESIGN | transcript read |
| S3 ujedEcmvBMk (+SANOimk8M9o) | T3, T3b | DESIGN | transcript read |
| S4 T6hDJcHrVBM | T5 | DESIGN | transcript read |
| S5 zQTbdEweG3c | T6 | DESIGN | transcript read; no stop/target order label, so entry-only |
| S6 l8RZrBfzvp4 | T7 (ES) | DESIGN, text only | not replayable until ES data exists |
| S7 liEJMfE_PXg | T11 | CHECK | frames only, no captions: no rule here came from it |
| S8 ZZeET7ng1nk | T12 | CHECK | frames only, no captions |
| S9 UOBgXV20yCM | T4 | family C, not in either set | one trade |
Assignment rule (frozen): a session is DESIGN if its transcript existed when this spec was written, CHECK otherwise. New
videos found later (card find-more recap videos) enter CHECK only if the encoding is frozen before anyone reads their
captions. The check set is two trades: it can show the encoding is broken (0 of 2), it cannot show it is good.

Recall definition (frozen): a family A short candidate emitted in the same session, before price has moved one stop-width
(his own frame-observed stop distance) below his entry price, with its entry price within one stop-width of his. No
minute anchor is used because no execution minute is certified. Targets: DESIGN at least 4 of 5 DAX sessions (S1-S5);
CHECK 2 of 2 to pass, 1 of 2 inconclusive, 0 of 2 fail. Beside every recall number report the fire rate (family A
candidates per session-day over the dev period) and the recall of the same number of random same-session instants: recall
that a random clock matches is not recall.

Contamination exclusions (frozen):
- Every ledger session is removed from DAX dev and holdout before any outcome is computed, all 9 sessions, both sets.
- While a group's trade date is unverified, remove every candidate date for it (recording date, inferred date, chart
  title date) and the trading day before each. The date list comes from card `rv-fix-tom-ledger-date-column`, not from here.
- A replay of a group runs only after that card marks its date verified. Unverified today: T4, T5, T6, T7, T11.
- The earlier losing attempts in S1, S2, S3 and S6 are in the same sessions and leave with them.
- BTC holdout 2026-06-26 onward stays burned (B147). The DAX holdout has not been read; this spec read no outcome file.

## 8. The two live gaps of 2026-10-12
**G2 (engine cannot short below value).** The engine allows only longs below the value area low. T3/T3b are shorts taken on
a day whose open was "very, very deep below the current price range of yesterday's profile" (ujedEcmvBMk:91-94), held because
"The trend is short. The entire market is currently trending downwards" (ujedEcmvBMk:187-189). So position against value does
not set the side. What sets it: "The direction you want to take for the day must be predefined and that can change if the
context breaks" (ujedEcmvBMk:277-279). v2: side comes from the family's idea (A = short at an unsupported high, including a
high below yesterday's value); `below_val -> long only` is removed as a gate. Card `tom-direction-health-vs-sources` owns the
code change. Caution: the 2026-10-12 BTC case was a market falling under value, which is not family A (no impulse up into a
thin top); nothing here says Tom would have shorted it.

**G3 ("healthy trend" = outside value).** Tom's test is whether volume supports the move: "The idea was that this trend isn't
entirely healthy" because "there was simply no liquidity left here and the liquidity was down here" (zQTbdEweG3c:231-232,
234-236); "the market open was too extreme. And above all, it wasn't accompanied by real volume" (k0zm5NYn0IQ:145-147); "all of
this is definitely not healthy" (k0zm5NYn0IQ:49-50). v2: unhealthy := A-C1 and A-C3 together (an impulse with a thin profile at
its extreme and the volume behind it). Outside-value is A-C2, a separate condition that makes the fade riskier, not the
trend healthy. The CVD-divergence requirement has no source in the trade videos.

## 9. What part A does not settle (for part B and the Sonnet cards)
1. NO-SOURCE list to resolve or express as same-session ranks: opening-range size (A-C1), "thin" (A-C3), inside-bar
   timeframe (A-P4), proof count, "a few points" (A-T4), order type, lot and partial sizes, re-entry limit.
2. Part B: fee term per market in the verdict, stop-width transfer rule for BTC, which proofs survive on each data feed,
   build cards for the A-P3/P4/P5/P7/P8 detectors and the session-extreme zone.
3. Date evidence found in the transcripts, for card `rv-fix-tom-ledger-date-column` (evidence only, not used here):
   T5 "what I traded there yesterday" (T6hDJcHrVBM:141-142) puts the trade one day before that recording.
4. More check trades: two is too few. Frames-only videos are the cleanest source (no captions to leak rules).
