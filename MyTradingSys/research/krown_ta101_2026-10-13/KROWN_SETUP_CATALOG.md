# KROWN SETUP CATALOG: every setup Krown's 15 extracts teach, in plain chart terms (2026-10-15)

Status: gate G2 of research/layer_rebuild_2026-10-15/LAYER_REBUILD_PLAN_2026-10-15.md (section 3 Krown, work order item 4). Rewrite of
the nine setups S1-S9 of KROWN_LAYER_SPEC.md:57-65 into the catalogue format of research/setup_catalog_2026-10-15/SETUP_CATALOG.md
(that file and the Malkan SETUP_SUMMARY.md are not edited), plus seven setups the extracts teach that S1-S9 miss (KR-S10 to KR-S16).
No code, no detector, no backtest, no fees, no stop-size math, no VALIDATION/HOLDOUT read. Nothing here is an MTS rule. Corpus: 14 TA
videos + 1 fees video (KROWN_RULES.csv, 120 rules); the 4 videos still blocked by HTTP 429 (MANIFEST.csv) and the 18 hidden playlist
entries are NOT read. Fable 5.1 audits this file against the raw transcripts on 2026-10-20.

How to read the quotes
- Block quotes `> "..."` + `**Source GPS: <id> | BEGIN/MIDDLE/END | t=<hh:mm:ss>**` are checked against `raw_transcripts_canonical/<id>_raw.txt` by
  `python scripts/dev/verify_extract_quotes.py` (verbatim after case/punctuation normalising, position third). They are copied by
  `tools/build_setup_catalog.py` from the extracts (Krown) or from the Tom/Fabio catalogue and the Malkan summary (section 4 only);
  nothing is retyped. The `t=` stamp is the caption time and shows where to listen.
- Captions are YouTube auto-captions (English, Krown speaks English): a quote proves what he says, never a price, date or edge. Garbled
  caption words are copied as written; the extract marks them INFERRED and the note is repeated here where it matters.
- `(paraphrase)` = the extract's "Stated mechanics" or an earlier spec, not his words. NOT STATED = he gives nothing in words; nothing is
  filled in. A chart shown with "here" and no words is NOT STATED too.
- Every number is labelled. SOURCED = his words, with the `extracts/...md:<line>` of the quote (a line number is the line of the quote in
  the extract). OURS = copied from KROWN_LAYER_SPEC.md (judgement or a grid value; never presented as his).
- Stop class (per row, from his words only): CLEAR = he states a readable reference where the trade is wrong (a level, a close beyond a
  zone); OURS = he states none and the earlier spec supplied one, shown as OURS; NOT STATED = he states none and the spec has none (or the
  row is a sell signal, not an entry). A CLEAR stop is a structure, never a distance: no stop distance exists anywhere in the corpus.
- BTC visible (Y/P/N) uses the key of SETUP_CATALOG.md: klines 1m (OHLC, volume), aggTrades, and profiles computed from them are held;
  Krown needs OHLCV only (KROWN_LAYER_SPEC.md:30-34). `YES*` = needs volume, and we hold Binance volume only; he says crypto volume can be
  faked (his words follow) and should be read on major venues (VOL-04, paraphrase), which our feed does not meet (rule KR-V11 BLOCKED, conflict C6). PARTIAL =
  the data exists but the history or the number of events is too thin (stated per row). His words (volume episode):

> "volume is also the one thing on a chart that can be faked in crypto"
**Source GPS: UqAvU1loT_k | BEGIN | t=00:03:52**

## 0. Summary

| id | setup | what you see (one line) | timeframe(s) | stop class | BTC visible | older id |
|---|---|---|---|---|---|---|
| KR-S1 | ZONE-TEST: a marked zone is tested and a proof candle appears | price returns to a wick-to-close zone that turned at least twice; a hammer, shooting star, strict engulfing or doji closes there, ideally on outsized volume, with the trend | 1d, 1w (first); 4h/6h timing | CLEAR | YES* | S1 |
| KR-S2 | BREAK-CLOSE: a candle closes through a zone or range boundary | a close (not a wick) beyond the outer boundary, volume expanding, then either no retest or a retest that holds | zone's own timeframe; weekly and daily examples | OURS | YES* | S2 |
| KR-S3 | RANGE-EDGE: trade the floor or the ceiling, never the middle | two zones with price stuck between; proof at an edge, or the close back inside after a poke beyond it (fake-out) | 1d, 1w | CLEAR (close back inside / beyond the edge; distance OURS) | YES* | S3 |
| KR-S4 | COIL-BREAK: a range on falling volume resolves | a range with every bounce quieter and the wedge tighter, volume down toward half its average, then the S2 close | 1d, 1w | OURS | YES* | S4 |
| KR-S5 | MA-CONTEXT: averages as filter, band and first-touch level | 21/55 EMA cross against the 200, first touch of the 200 after a long absence, pullback into the 21-55 band, weekly 55 EMA bias, range break with the averages | 1d, 1w | OURS | YES | S5 |
| KR-S6 | LEASH: whole candle floats above the 5 EMA | the candle low stays above the 5 EMA for about three closes; price tends to come back to the line | 1d (Bitcoin) | OURS | YES | S6 |
| KR-S7 | CAPITULATION: hammer on the biggest volume bar | after a long downtrend one mega candle with a huge lower wick and a strong close on the biggest volume bar of the chart | 1w, 1d | OURS | YES* | S7 |
| KR-S8 | VOL-COMPRESSION BREAKOUT (BBWP) | volatility percentile below about 25-35 and falling from a high; the first candle that breaks the range with volatility back above the 50th percentile | higher term (Bitcoin); his chart timeframe not named | CLEAR | YES | S8 |
| KR-S9 | TOP-4 SELL FRAMEWORK for a long-term holding | three of four around the same weeks: reversal candle, volume at 2x the 30-bar (or 60-bar) average of the chart timeframe, volatility above the 85th percentile, bearish RSI divergence or MACD cross | 1w (Bitcoin), 1M (traditional markets) | NOT STATED | PARTIAL | S9 |
| KR-S10 | TREND LINE, FIRST RETURN: reaction at a volume-anchored line | a line through two high-volume turning points (or three touches); price comes back to it for the first time | NOT STATED | NOT STATED | YES* | new (rule KR-L04) |
| KR-S11 | TREND LINE BREAK, then buy the higher low on the broken line | a legitimate line breaks with follow-through; the line becomes a base for a higher low | NOT STATED | NOT STATED | YES | new (rules KR-L06, KR-Z09) |
| KR-S12 | TREND REVERSAL CONFIRMED BY A CLOSE (dominant level) | price closes below the dominant higher low (or above the dominant lower high); the reclaim is the confirmation | every timeframe; higher outranks lower | NOT STATED | YES | new (rule KR-L10, a filter in the spec) |
| KR-S13 | EFFORT VERSUS RESULT: huge volume, tiny candle (absorption) | the biggest volume of the chart on a tiny candle at a level; or a huge candle on no volume | 1d, 1w | NOT STATED | YES* | new (rule KR-V06) |
| KR-S14 | RSI DIVERGENCE: regular and hidden | price makes a new low or high that the RSI does not confirm (regular), or a higher low / lower high that the RSI exceeds (hidden) | 1w/1M for tops; otherwise NOT STATED | NOT STATED | YES | new (rule KR-S05, descriptive only in the spec) |
| KR-S15 | 200-WEEK SMA: buy at or below the line | price at or below the weekly 200 SMA (about four years of price in one line) | 1w | NOT STATED | PARTIAL | new (rule KR-M04) |
| KR-S16 | COUNTER-TREND AT A VOLATILITY EXTREME | enter against the move when volatility is very high; exit as volatility comes down | NOT STATED | NOT STATED | YES | new (KCM-50, no rule id) |

Counts: 16 setups = the nine of the older spec (KR-S1 to KR-S9) + 7 the extracts teach that S1-S9 miss (KR-S10 to KR-S16). Stop class: CLEAR 3, OURS 5, NOT STATED 8. BTC visible: YES 14 (of which 7 need volume, YES*), PARTIAL 2, NO 0. Cross-trader overlap: 17 pairs (STRONG 7, PARTIAL 10; quoted-both-sides 15, paraphrase 2); 6 rows have none (KR-S6, KR-S7, KR-S10, KR-S11, KR-S12, KR-S15).

## 1. Where the older S1-S9 went (duplicate map)

| older id (KROWN_LAYER_SPEC.md:57-65) | now | what changed |
|---|---|---|
| S1 ZONE-TEST | KR-S1 | stop re-read from his words: close-based exit (CLEAR); the 1.5 x ATR14 hard stop and the opposite-zone / 2R target stay OURS |
| S2 BREAK-CLOSE | KR-S2 | stop is OURS (he gives none); the range-height target is his, and only for a range edge |
| S3 RANGE-EDGE | KR-S3 | stop class CLEAR for the fake-out arm (6aA-P4Gvhrc t=00:13:04 "You need to see a closure above, in this case, the wick high of that initial range."; t=00:18:04 "Only act on the close back inside with proof."); the distance stays OURS (GPT audit F1) |
| S4 COIL-BREAK | KR-S4 | the "volume near 50 % of average" cue is his, labelled an observation |
| S5 MA-CONTEXT | KR-S5 | split into variants 5a-5f; none has an entry, stop or target in his words |
| S6 LEASH, S7 CAPITULATION | KR-S6, KR-S7 | provisional (one or two videos); stops OURS |
| S8 VOL-COMPRESSION BREAKOUT | KR-S8 | unchanged in substance: the only setup with entry, stop structure and exit in his words |
| S9 TOP-4 SELL FRAMEWORK | KR-S9 | a sell signal, so stop class NOT STATED; BTC visibility lowered to PARTIAL for history/warm-up |
| none | KR-S10 to KR-S16 | trend-line first return, trend-line break and higher low, dominant-level reversal, effort vs result, RSI divergence, 200-week SMA, counter-trend at a volatility extreme |

Context filters of the spec (trend state per timeframe, mode, range-middle exclusion, volatility gates, RSI zones, volume confirms,
higher-timeframe veto) are not setups; they appear as "Context" lines in the rows and in section 2.

## 2. Shared frame (applies to every setup)

### 2.1 Time, timeframes, trend filter, "obvious or nothing"
His home is Bitcoin and crypto on the daily and weekly, daily close 00:00 UTC (rules KR-T04, KR-T08). Closed candles only.

> "the daily close is at zero zero UTC"
**Source GPS: 8MvxK_nxO-0 | BEGIN | t=00:09:04**

> "nothing is final until that clock hits zero meaning that your closing price is not solidified"
**Source GPS: 8MvxK_nxO-0 | BEGIN | t=00:09:24**

> "the daily is a gold standard for most cryptos for slower markets like equities the weekly earns the top slot followed by the monthly and the quarterly"
**Source GPS: _t_XIBrcjRk | MIDDLE | t=00:12:17**

Top-down routine (rule KR-T03): weekly = tide, daily = decision, 4h/6h = timing after the first two agree. "Agree" is not defined for
timeframes (the dominant-level trend state of KR-S12 is the nearest sourced definition).

> "the weekly time frame in general that's gonna be your tide which way is the ocean moving where are you trending towards you don't want to fight that direction generally"
**Source GPS: _t_XIBrcjRk | MIDDLE | t=00:13:16**

> "the daily time frame is generally where you're gonna want to make that decision however is there actually a trade here"
**Source GPS: _t_XIBrcjRk | MIDDLE | t=00:13:23**

> "really you only want to act on a four-hour time frame only after the first two agree the first two being the weekly and the daily"
**Source GPS: _t_XIBrcjRk | MIDDLE | t=00:13:57**

> "if the weekly and daily disagree with your four hour idea you probably shouldn't be trading on that side of the market or maybe just no trade at all"
**Source GPS: _t_XIBrcjRk | MIDDLE | t=00:14:35**

Trend filter in front of every strategy (rule KR-L11), "obvious or nothing" (rule KR-T05):

> "all you need to do is incorporate a condition that you only trade in the same direction of the current trend."
**Source GPS: 2-nG9bsMoPQ | BEGIN | t=00:03:23**

> "if I don't even have an uptrend here, I don't even have a trade. So I'm just going to shut off the chart"
**Source GPS: 2-nG9bsMoPQ | END | t=00:24:16**

> "Every every strategy I use starts really with this filter. It is is what it comes down to. Like that really is a big portion of a lot of my trading strategies is some form of a trend filter."
**Source GPS: 2-nG9bsMoPQ | END | t=00:24:33**

> "If it ain't obvious, it ain't there."
**Source GPS: qEfES84jwwo | BEGIN | t=00:08:14**

The eye test "obvious" has no formula; it becomes a fire-rate ceiling at G5, not a detector (rule KR-T05).

### 2.2 Management he states (all setups; none carries a number)
- He prefers to manage risk himself and exit when a zone breaks on a close, not to leave a resting stop. MTS requires a protective stop on
  every position (conflict C3, decision q-krown-stop open); the CLEAR stop class below is his close-based exit, not a stop order.

> "I don't like having stop losses, I like managing risk myself."
**Source GPS: qEfES84jwwo | END | t=00:29:43**

> "if my zone actually is breaking, then price is very much likely to move much more in that direction."
**Source GPS: qEfES84jwwo | END | t=00:29:56**

- He warns against the obvious stop placement (a pile of stops sits just under every obvious floor); no replacement distance is given.

> "Under every obvious floor is a pile of stop losses."
**Source GPS: qEfES84jwwo | BEGIN | t=00:00:04**

> "it's exactly why we draw zones instead of lines and keep stops away from the obvious price."
**Source GPS: qEfES84jwwo | END | t=00:29:35**

- Sizing: volatility up means wider stops and bigger risk, so size down (rule KR-Q09, one video); the tops row scales out 20-85 % (KR-S9).
- His own statistics (82 % reconnect within two closes, 80-95 % for the 21/55 cross, 70 % compression, 26 years of 200-week back-test,
  right side of the trend 90-95 %) are claims without data in the videos (rule KR-F08): hypotheses H-M3, H-M2, H-L1, H-Q1, never inputs.
- No hit rate or R:R is stated for any setup (the 70 % win rate in SNR-21 is an illustration of risk management, not a result).

## 3. Krown setups

### KR-S1 ZONE-TEST: a marked zone is tested and a proof candle appears
1. **Name / trader.** Krown (episodes SNR, LVL, CAN, RNG, VOL). Older spec id S1 (KROWN_LAYER_SPEC.md:57). His words: "zone", "wick to close", "reversal candle", "location beats shape". Side: both (the ceiling is the mirror of the floor). Rules: KR-Z01-Z04, Z08, Z15, Z17, C03-C10, V04.
2. **What you see.**
   - A zone on the daily or weekly chart, drawn from the wick extreme to the close of the pivot candle, where price turned at least twice; three to five zones at most; a pivot on heavy volume outranks the rest:

> "The way that we draw the zones is we anchor from a wick extreme To the closure of that candle the wick is the emotional overshoot"
**Source GPS: qEfES84jwwo | BEGIN | t=00:04:53**

> "That's where the price turned at least twice. One is an event twice as a memory."
**Source GPS: qEfES84jwwo | BEGIN | t=00:07:24**

> "Number three, three to five zones maximum. If you're drawing more than that, like you have fucking 10 plus zone."
**Source GPS: qEfES84jwwo | BEGIN | t=00:07:29**

> "zone stamped on heavy volume, outrank everything else."
**Source GPS: qEfES84jwwo | BEGIN | t=00:07:51**

   - Price comes back to it and a proof candle prints at the zone. The four candles he teaches, each with its location rule:

> "when a lot of buyers step in and you get a strong candle closure like this that's what's known as a hammer and it's usually good for a short-term reversal at the very least"
**Source GPS: 8MvxK_nxO-0 | MIDDLE | t=00:12:53**

> "you get a big long wick to the upside at the top of a trend and then you close down"
**Source GPS: 8MvxK_nxO-0 | MIDDLE | t=00:19:19**

> "an engulfing candle must trade below the low of the prior and if it's a bullish engulfing you need to close above the high of the prior candle"
**Source GPS: 8MvxK_nxO-0 | MIDDLE | t=00:20:49**

> "you got a green candlestick prior and your current one trades above the high of the prior and when it closes it it closes below the low of the prior"
**Source GPS: 8MvxK_nxO-0 | END | t=00:22:10**

> "a doji is just a complicated word for a very simple phenomenon which is a bodyless candle"
**Source GPS: 8MvxK_nxO-0 | END | t=00:23:02**

> "it must be at the low the exact low of that move meaning that price does not go lower on the left or right-hand side especially on the left-hand side"
**Source GPS: 8MvxK_nxO-0 | MIDDLE | t=00:13:39**

   - The pattern only counts at the zone, and volume adds weight:

> "location beats shape is the point that I'm working to every single time"
**Source GPS: 8MvxK_nxO-0 | END | t=00:28:45**

> "So we have candlestick formation plus volume plus well price reversed after that too. So all of these things matter."
**Source GPS: qEfES84jwwo | MIDDLE | t=00:21:16**

> "volume doesn't create the signal It confirms it or or condemns it"
**Source GPS: UqAvU1loT_k | MIDDLE | t=00:09:53**

3. **Entry, stop, target (his words).**
   - Entry: wait for the test, ask for proof; then trade the confirmation close beyond the pattern's wick, not the first candle. Trigger price and order type: NOT STATED.

> "at the floor, wait for the test, demand proof and episode one candle, basically, like a hammer or an engulfing, ideally on episode five volume"
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:17:19**

> "Price reacts to the level. You You watch it either bounce off of support or or pull back from resistance on the first pass, and then you validate."
**Source GPS: 2ei4fj-Ba24 | END | t=00:17:38**

> "you wanna see a closure in that same direction above the wick high or low depending upon which direction you're going to fully confirm that"
**Source GPS: 8MvxK_nxO-0 | END | t=00:24:50**

> "it's better in my experience to trade the confirmation of that rather than just the first candle especially when it comes to a doji"
**Source GPS: 8MvxK_nxO-0 | END | t=00:25:23**

   - Inside an unbroken resistance zone he also scalps short or simply does not buy:

> "all price that goes into this region is you know, you could take short scalps on it These sort of things or you could just know not too long in this region"
**Source GPS: qEfES84jwwo | MIDDLE | t=00:11:48**

   - Stop [stop class: CLEAR, structure only]: the zone is resolved only by a close beyond its outer wick boundary, and that close is where he takes the loss; no resting stop, no distance:

> "it's a zone, in order to resolve the zone, you must get a closure, not a wick, but a closure outside of that wick boundary."
**Source GPS: qEfES84jwwo | END | t=00:28:40**

> "if my zone actually is breaking, then price is very much likely to move much more in that direction."
**Source GPS: qEfES84jwwo | END | t=00:29:56**

   - Target: NOT STATED. (The nearest words are scalps: "first pass you almost always have a decent scalp", KR-S10, and "scalp the boundaries", KR-S3.)
   - Management: NOT STATED beyond section 2.2.
4. **Context and timeframe(s).** Support works best in an uptrend and resistance in a downtrend; a level against the trend is weaker. Testing a level more than three times raises the chance it breaks (C1: the levels episode, LVL-29, says more touches make a level more significant, not stronger). Timeframe: daily and weekly first, 4h/6h only for timing (section 2.1).

> "support works best in an uptrend. When you are in an uptrend, you want to be plotting out your previous supports"
**Source GPS: 2ei4fj-Ba24 | MIDDLE | t=00:13:35**

> "And against trend levels are weaker. That doesn't mean they don't matter, they're just weaker."
**Source GPS: 2ei4fj-Ba24 | END | t=00:14:13**

> "If you're testing a level more than three times, understand that the probability of it breaking gets very much higher."
**Source GPS: qEfES84jwwo | END | t=00:27:33**

5. **BTC visibility: YES\*.** Wick/close zones, candles and trend state come from klines resampled to 1d/1w; volume is Binance only (section 0).
6. **Evidence.** 0 trades in a ledger. Chart examples in the extracts (T3); one winner is shown without an entry price: "price goes from 84 to 126" (extracts/extract_2ei4fj-Ba24.md:317 (LVL-26)), instrument and timeframe not named.
7. **Gaps and numbers.**
   - SOURCED: at least 2 turns (extracts/extract_qEfES84jwwo.md:65 (SNR-06)); 3 to 5 zones (extracts/extract_qEfES84jwwo.md:74 (SNR-07)); heavy volume = 2x or more of the 20-period average (extracts/extract_UqAvU1loT_k.md:86 (VOL-09), extracts/extract_UqAvU1loT_k.md:68 (VOL-07)); hammer/star horizon the next 3 to 5 candles (extracts/extract_8MvxK_nxO-0.md:94 (CAN-10)); more than 3 tests (extracts/extract_qEfES84jwwo.md:196 (SNR-19)).
   - OURS (spec :57): stop A beyond the zone's far wick boundary; stop B = his close-back-beyond-zone exit plus a hard stop at 1.5 x ATR14; target = opposite zone or 2R; size of a "turn" in ATR units; ranking weights; what counts as "recent" touches.
   - NOT STATED: what makes a wick "big", how recent a touch must be, trigger price, target. Conflict C1 (more touches weaker, SNR-18/19, vs LVL-29: more touches matter more and the breakout response is stronger) is unresolved.

### KR-S2 BREAK-CLOSE: a candle closes through a zone or range boundary
1. **Name / trader.** Krown (SNR, RNG, VOL, LVL). Older spec id S2 (KROWN_LAYER_SPEC.md:58). His words: "break", "closure", "harvest", "fuel", "retest". Side: both. Rules: KR-Z07, Z10, Z11, V05, R06, R07, M13.
2. **What you see.** Price closes beyond the outer wick boundary of a zone or range edge (above the wick high of a ceiling, below the wick low of a floor); volume expands as price leaves; afterwards the old zone acts as the opposite level if price comes back. A wick through that snaps back is a stop harvest:

> "Only a close beyond the zone breaks a level. No close outside. We don't call it broken. Period."
**Source GPS: qEfES84jwwo | END | t=00:30:46**

> "how do you resolve the breakout? You need to see a closure above, in this case, the wick high of that initial range."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:13:04**

> "a real break of a real zone comes with fuel in the form of volume. That is your lie detector."
**Source GPS: UqAvU1loT_k | END | t=00:19:36**

> "The harvest is usually quiet, you know, when you are harvesting stop-losses or when you're watching a stop-loss hunt, they're usually quiet in terms of volume"
**Source GPS: UqAvU1loT_k | END | t=00:19:54**

> "the obvious poke that snaps back is a harvest, not a break."
**Source GPS: qEfES84jwwo | END | t=00:32:39**

3. **Entry, stop, target (his words).**
   - Entry: his checklist is a close through the zone, expanding volume, and a retest that holds if one comes. He says two things about the retest (conflict C2, both his): wait for it, and it is not required.

> "One, a close through the zone. Not a wick, but a close."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:20:55**

> "Real breakouts bring volume expansion. That is another confirmation tool here."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:21:03**

> "upgrade the other retest routine, close through the zone on expanding volume, retest holds, and that is it."
**Source GPS: UqAvU1loT_k | END | t=00:20:11**

> "don't chase the break, wait for the retest."
**Source GPS: qEfES84jwwo | END | t=00:31:00**

> "The break was real slices back through it. Well, it was a harvest."
**Source GPS: qEfES84jwwo | END | t=00:31:38**

> "The best breakouts do not retest by the way."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:21:29**

> "if you do get a retest, obviously the retest must hold."
**Source GPS: 6aA-P4Gvhrc | END | t=00:31:22**

   - Stop [stop class: OURS]: NOT STATED. The retest video defers "entries, stops and targets" to his course (SNR-15 Stated mechanics, paraphrase). The spec's stop is OURS (below).
   - Target: when the broken zone is the edge of a range, the range height from the trigger, which he calls a heuristic:

> "read the height of the range often projects the first leg of the move."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:21:51**

> "the spring releases about roughly what it stored during this phase, but that is a heuristic not a law"
**Source GPS: 6aA-P4Gvhrc | END | t=00:23:02**

   For a zone that is not a range edge: NOT STATED.
4. **Context and timeframe(s).** Confirmations he adds: the trend and an RSI above 70 in an upside resolution, or the averages turning the same way; each only "confirms", the close decides:

> "If the trend is up, and you're resolving a range, and it's overbought, that is your confirmation, it's breaking out."
**Source GPS: INOCBmqQupc | MIDDLE | t=00:08:44**

> "when the trend is down, or or if it's if it's in a range and then breaking to the downside, and moving below your most support or your your your most recent support zone, and the RSI's turning oversold, that's a damn good indication you're entering into a real reversal, and you should be expecting more down."
**Source GPS: INOCBmqQupc | MIDDLE | t=00:08:53**

> "moving averages are up starting here, so it actually kind of does alert you to the potential breakout coming later. But of course, you can't really validate that breakout until price has closed above the top side of the range, and with those moving averages confirming that same direction, okay, now you have a high probability continuation move."
**Source GPS: vjzy_KxJ_y8 | END | t=00:19:56**

   A level tested more than three times is "mature" (KR-S1). Timeframe: the zone's own (which timeframe's close counts is not stated, OURS); his examples are weekly and daily Bitcoin.
5. **BTC visibility: YES\*.** Closes, zone boundaries, bar volume against its 20-period average.
6. **Evidence.** 0 trades in a ledger. Weekly Bitcoin range examples (RNG, T3). Note: Tom's TOM-6 shows the same close-based verdict (section 4).
7. **Gaps and numbers.**
   - SOURCED: range height projected from the trigger (RNG-22, line above); RSI above 70 as the upside confirmation (extracts/extract_INOCBmqQupc.md:361 (RSI-40)); more than 3 tests (extracts/extract_qEfES84jwwo.md:196 (SNR-19)).
   - OURS (spec :44, :58): enter at the close (arm 1) or at the first retest that holds (arm 2); "discernible" volume threshold grid {1.0, 1.25, 1.5} x the average; stop = close back inside the zone; target 2R; which timeframe's close counts.
   - NOT STATED: stop, a "discernible" volume size, number of closes, target for a non-range zone.

### KR-S3 RANGE-EDGE: trade the floor or the ceiling, never the middle
1. **Name / trader.** Krown (episode RNG, KCM, VJZ). Older spec id S3 (KROWN_LAYER_SPEC.md:59). His words: "range", "floor and ceiling", "no man's land", "fake out". Side: both. Rules: KR-R01, R02, Z08, T06.
2. **What you see.** A range = two zones (floor and ceiling, drawn wick to close) with price stuck between. Only the two edges have an edge; the middle is no man's land. A quick poke beyond an edge that snaps back inside is the signature fake-out:

> "inside a range, there are exactly two places with an edge. The floor and the ceiling."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:05:58**

> "The middle, that's your no man's land. No memory, no zone, no edge."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:06:08**

> "You're going to continue to remain in those ranges and you can scalp a lot there for sure."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:07:29**

> "The quick poke below the floor that snaps back inside the range is signature fake out."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:17:43**

   Tells that a range is forming (flat, tangled averages and shrinking volume; the RSI hanging between 40 and 60):

> "The tell, flat tangled averages plus shrinking volume."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:04:04**

> "this zone right here where the RSI really is hanging out between 40 and 60 correlates to this whole consolidation right here."
**Source GPS: INOCBmqQupc | MIDDLE | t=00:10:56**

3. **Entry, stop, target (his words).**
   - Entry: at the edge, after the test, with proof (a candle, ideally on volume); in a fake-out only on the close back inside with proof. Scalp the range, do not use a trend strategy inside it. Order and price: NOT STATED.

> "at the floor, wait for the test, demand proof and episode one candle, basically, like a hammer or an engulfing, ideally on episode five volume"
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:17:19**

> "Only act on the close back inside with proof."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:18:04**

> "The close is effectively your verdict. Everything else is a rumor"
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:18:17**

> "you could buy, you know, buy near the low side of the range, sell near the high side of the range, but not look for the breakout until you get an objective signal of a breakout."
**Source GPS: kcMnnQr1VFg | MIDDLE | t=00:12:59**

   - Stop [stop class: CLEAR, structure only]: he states a close rule for range edges in the range video: "You need to see a closure above, in this case, the wick high of that initial range." (6aA-P4Gvhrc t=00:13:04) and "Only act on the close back inside with proof." (t=00:18:04). No distance is given; the spec's stop distance is OURS (below). (GPT audit F1)
   - Target: NOT STATED (the range videos say "scalp the boundaries"; no exit price or level). The opposite edge is OURS.
4. **Context and timeframe(s).** Read the mode first (trend tools fail in a range). A downside cross of the averages with no break of the range is a range play, not a reversal:

> "Whereas over here, you have a downside cross, right? But you don't have a range break to the to the downside. Thus, there's no real reversal, and it is more or less a range play. Thus, you should be scalping this range if you're going to be doing anything at all, and not trying to trade the trend reversal to the downside cuz you just don't have that yet."
**Source GPS: vjzy_KxJ_y8 | END | t=00:20:12**

   Timeframe: daily and weekly Bitcoin examples; the scalp is "a short hold he does not size" (KR-T08, KR-R01).
5. **BTC visibility: YES\*.** Two zones from klines; proof candle and volume as in KR-S1.
6. **Evidence.** 0 trades in a ledger; Bitcoin range examples (T3).
7. **Gaps and numbers.**
   - SOURCED: RSI hanging between 40 and 60 during a consolidation (extracts/extract_INOCBmqQupc.md:252 (RSI-28)); his own range view 40 to 60 against the textbook 30 to 70 (extracts/extract_INOCBmqQupc.md:244 (RSI-27)). No other number.
   - OURS (spec :59): stop = close beyond the edge; target = opposite edge; flat-average slope threshold; tightness score.
   - NOT STATED: edge width, how many touches before the edge counts, exit, stop.

### KR-S4 COIL-BREAK: a range on falling volume resolves
1. **Name / trader.** Krown (RNG, VOL, KCM). Older spec id S4 (KROWN_LAYER_SPEC.md:60). His words: "coil", "symmetrical triangle", "spring", "longer and tighter". Side: both (bias from the structure inside). Rules: KR-V09, R03, R04, R05, V10, T07.
2. **What you see.** A range where each bounce is quieter than the last and the wedge tightens; volume tails off toward half its average; the averages are flat and braided. The coil itself gives no direction; the structure inside does (same lows with lower highs = sellers; same highs with higher lows = buyers):

> "when a range runs on declining volume, every bounce quieter than the last, the market is effectively coiling."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:08:34**

> "We can call that a coil, basically a range on declining volume."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:09:53**

> "if you want to put a name on this pattern, that is a symmetrical triangle."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:08:42**

> "Falling volume tells you a big move is loading. It doesn't tell you which way."
**Source GPS: UqAvU1loT_k | END | t=00:21:04**

> "The longer and tighter that you consolidate for equals bigger breakout."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:10:32**

> "I don't want to say always because nothing is ever always, but it's damn close."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:10:49**

> "it's telling you sellers are getting more aggressive while buyers are not"
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:15:39**

> "you got same highs for sellers higher lows for buyers buyers getting more strong thus we have an upside breakout"
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:16:05**

> "it becomes almost like 50% of the average. That is when your breakout move actually starts to occur right around here."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:12:56**

> "that's not necessarily a rule but once it starts to get super super low like that the likelihood of it breaking out and following through becomes exponentially higher"
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:13:56**

3. **Entry, stop, target (his words).**
   - Entry: the resolution of KR-S2 (close beyond the edge, volume expansion). He waits for the volume to tail off as the best timing factor:

> "wait for that volume to tail off because that is your best timing factor alongside another tool as well."
**Source GPS: 6aA-P4Gvhrc | END | t=00:31:06**

> "how do you resolve the breakout? You need to see a closure above, in this case, the wick high of that initial range."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:13:04**

   - Stop [stop class: OURS]: NOT STATED (the spec says "as S2", OURS).
   - Target: the height of the range projected from the trigger (a heuristic):

> "read the height of the range often projects the first leg of the move."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:21:51**

   - Management: NOT STATED.
4. **Context and timeframe(s).** Bias from the previous trend when the range is sideways (rule KR-L12). Timeframe: weekly Bitcoin examples (the volume-near-half observation is from weekly charts); daily by extension (OURS).
5. **BTC visibility: YES\*.** Range, falling bar volume, wedge: klines.
6. **Evidence.** 0 trades in a ledger. His 70 % compression claim and "damn close to always" are claims (H-R1).
7. **Gaps and numbers.**
   - SOURCED: volume near 50 % of its average right before the breakout, an observation he says is not necessarily a rule (extracts/extract_6aA-P4Gvhrc.md:130 (RNG-13), extracts/extract_6aA-P4Gvhrc.md:132 (RNG-13)); range height as the first target (extracts/extract_6aA-P4Gvhrc.md:213 (RNG-22)).
   - OURS (spec :44, :60): volume-slope and tightness thresholds; flat-MA slope threshold; RSI 40-60 as a second tell; stop and target as S2.
   - NOT STATED: how long, how tight, how low the volume must go.

### KR-S5 MA-CONTEXT: averages as filter, band and first-touch level
1. **Name / trader.** Krown (MAV, VJZ). Older spec id S5 (KROWN_LAYER_SPEC.md:61). His words: "Silver Cross", "dynamic areas of interest", "first test after a long time". Side: both. Rules: KR-M01, M02, M03, M05, M07, M09-M13. He says an average is not an entry tool, so this row lists the variants he describes; each is a context or a location, none has an entry, stop or target in his words:

> "Most beginners use moving averages as a tool to get entries and honestly, that is perhaps one of the worst ways to use moving averages."
**Source GPS: vjzy_KxJ_y8 | BEGIN | t=00:00:00**

   The extract's gap note says the same in plain words: "No stop or target rules given for any moving-average trade" (extract_-NXzJs5JRks.md, Gaps section, paraphrase).
2. **What you see.**
   - 5a. Silver Cross: the 21 EMA crosses the 55 EMA; strongest with the 200 SMA (below it with a down-cross preceded the big drops; a cross plus a reclaim of the 200 was a reversal):

> "once the 21 EMA crossed the downside of the green 55 EMA, that represents again your shorter and medium term trends there."
**Source GPS: -NXzJs5JRks | MIDDLE | t=00:12:59**

> "it wasn't until Bitcoin was trading below the 200 simple with those two major moving averages crossed in the downside fashion where you really got the floor letting loose."
**Source GPS: -NXzJs5JRks | MIDDLE | t=00:14:09**

> "when we got these crossing plus Bitcoin reclaiming the 200 simple, well, that was your reversal."
**Source GPS: -NXzJs5JRks | MIDDLE | t=00:15:26**

> "generally, when you see the lower period, the 21 EMA crossing above the green 55 EMA, you're generally entering into an uptrend."
**Source GPS: vjzy_KxJ_y8 | MIDDLE | t=00:14:18**

   - 5b. First touch of the 200 after a long absence:

> "almost always will have a reaction any time it comes into contact with the 200 simple moving average on almost any time frame for the first time in a long time."
**Source GPS: -NXzJs5JRks | BEGIN | t=00:08:15**

> "an asset that is first testing a 200 moving average after a long time of being away from it almost always is going to find some sort of a reaction around that moving average, almost always."
**Source GPS: vjzy_KxJ_y8 | MIDDLE | t=00:12:01**

   - 5c. Pullback into the 21-55 band in an uptrend, best where a horizontal zone meets the 55 EMA:

> "the green 55 EMA as dynamic support and and also the yellow 21 EMA as dynamic support for the shorter term"
**Source GPS: -NXzJs5JRks | END | t=00:33:11**

> "You can see over here on the downtrend, Bitcoin likes to sell off on those tests of the 21 EMA. And during an uptrend over here, Bitcoin likes to kind of base off of them."
**Source GPS: vjzy_KxJ_y8 | MIDDLE | t=00:13:14**

> "So, your support zone aligning with your support or resistance zone aligning with a 55 EMA in general, that's a really high quality bounce or pullback zone. And if price obviously reclaims it or or or reverses from it, then you have a trending move likely emerging."
**Source GPS: vjzy_KxJ_y8 | END | t=00:26:12**

   - 5d. Weekly 55 EMA bias; a reclaim given up within about two closes is a bull trap:

> "Whenever Bitcoin's above it, you're generally bullish. Whenever Bitcoin's below it, you're generally bearish."
**Source GPS: vjzy_KxJ_y8 | MIDDLE | t=00:08:53**

> "You would have longed right here, and this is your traditional bull trap, really."
**Source GPS: vjzy_KxJ_y8 | MIDDLE | t=00:09:20**

> "you would have been very quickly dismayed because it gave that up just two closures after be claiming it. And that is a signal in and of itself that hey, downside's are very likely"
**Source GPS: vjzy_KxJ_y8 | MIDDLE | t=00:09:28**

   - 5e. Range break validated by a close beyond the edge with the averages turning the same way (a downside cross without a range break is a range play, KR-S3):

> "moving averages are up starting here, so it actually kind of does alert you to the potential breakout coming later. But of course, you can't really validate that breakout until price has closed above the top side of the range, and with those moving averages confirming that same direction, okay, now you have a high probability continuation move."
**Source GPS: vjzy_KxJ_y8 | END | t=00:19:56**

   - 5f. Golden/death cross of the 50 and 200 SMA, discounted when the 200 still slopes the other way:

> "A golden cross, as the name would imply, typically begets a lot more long-term upside, not short-term upside."
**Source GPS: -NXzJs5JRks | END | t=00:26:47**

> "The slope of the 200 simple was still up, so not really a great death cross in that case."
**Source GPS: -NXzJs5JRks | END | t=00:27:22**

> "you're probably looking to sell any rally towards that 200 simple realistically."
**Source GPS: -NXzJs5JRks | END | t=00:27:47**

3. **Entry, stop, target (his words).**
   - Entry: NOT STATED for every variant (5c: the pullback into the band is "a bounce area", no trigger). Stop [stop class: OURS]: NOT STATED; the spec's stop (below the 55 EMA, or a close beyond the line) and the trail on the 55 EMA are OURS. Target: NOT STATED. For 5a he accepts giving back profit because the cross comes after the reversal:

> "it will come after the fact when you do see a crossing of the direction after the trend reverses. That is okay. Again, you can afford to give up a little bit of these profits if you jump on the trend right here. And then let's say it reverses, you know, not and it doesn't confirm until you're back up like 80,000 bucks over here. You can afford to give some up. That is the essence of trend trading."
**Source GPS: vjzy_KxJ_y8 | END | t=00:18:14**

4. **Context and timeframe(s).** The averages are filters: they stop you shorting an uptrend and fail in chop. Timeframe: daily, and the weekly for 5d (Bitcoin, "most assets, not perfect") and the 200-week of KR-S15. Averages: 21 and 55 EMA, 200 SMA; 5 and 377 EMA on the edges.
5. **BTC visibility: YES.** All variants are closes and averages of closes.
6. **Evidence.** 0 trades in a ledger. He shows chart examples with moves (about 40,000 to 52,000 in VJZ-49, about 4,000 to 14,000 in VJZ-50); they are outcomes of a chart, not trades.
7. **Gaps and numbers.**
   - SOURCED: EMA 21, EMA 55, SMA 200 (extracts/extract_-NXzJs5JRks.md:92 (MAV-09)); EMA 377 (extracts/extract_vjzy_KxJ_y8.md:206 (VJZ-21)); EMA 5 (extracts/extract_-NXzJs5JRks.md:194 (MAV-19)); 50/200 SMA pair (extracts/extract_-NXzJs5JRks.md:201 (MAV-20)); weekly EMA 55 (the weekly and the 55 are in the extract's Stated mechanics of VJZ-12, paraphrase; the spoken line is extracts/extract_vjzy_KxJ_y8.md:118 (VJZ-12)); "about two closes" as an example of a failed reclaim (extracts/extract_vjzy_KxJ_y8.md:130 (VJZ-13)). His "more than 80 %, less than 95 %" for the 21/55 cross is a claim (extracts/extract_vjzy_KxJ_y8.md:269 (VJZ-27)), hypothesis H-M4, not an input.
   - OURS (spec :47, :61): "long time away" for 5b; slope thresholds; touch tolerance for the confluence in 5c; stop and trail.
   - NOT STATED: any entry, stop or target; what "a long time" is; slope numbers.

### KR-S6 LEASH: the whole candle floats above the 5 EMA (provisional)
1. **Name / trader.** Krown (MAV only: one video, PROVISIONAL). Older spec id S6 (KROWN_LAYER_SPEC.md:62). His words: "leash", "disconnect". Side: both. Rule: KR-M06.
2. **What you see.** On the Bitcoin daily the candle low stays above a 5 EMA (the candle does not touch the line). Price is "at the end of the leash"; it tends to reconnect or go sideways until it does:

> "short moving averages act like a leash. When price sprints so hard that the entire candles will float above a very low period moving average"
**Source GPS: -NXzJs5JRks | MIDDLE | t=00:23:34**

> "the low of the candle not reconnecting with the line is what we call a disconnect."
**Source GPS: -NXzJs5JRks | MIDDLE | t=00:23:45**

> "Even when it disconnects, it goes sideways until it reconnects."
**Source GPS: -NXzJs5JRks | END | t=00:24:59**

3. **Entry, stop, target (his words).**
   - Entry: NOT STATED. What he says is a reading: with about three closes not connecting you are late, and the 5 EMA is where to expect a basing pullback:

> "you're not really early. You're kind of late. It doesn't say the trend is over."
**Source GPS: -NXzJs5JRks | END | t=00:25:49**

> "your five EMA is probably where you should be expecting some basis to come in around on short-term pullbacks."
**Source GPS: -NXzJs5JRks | END | t=00:25:53**

   - Stop [stop class: OURS]: NOT STATED; the spec's "close below the 5 EMA" is OURS. Target: NOT STATED (prior extreme is OURS).
4. **Context and timeframe(s).** Bitcoin daily. No trend condition is stated for the disconnect itself.
5. **BTC visibility: YES.** Daily closes and a 5 EMA.
6. **Evidence.** His own statistics (a claim, hypothesis H-M3, to be recomputed, never an input):

> "I've measured this 14 plus years, by the way, 5,284 candles, 476 disconnects."
**Source GPS: -NXzJs5JRks | MIDDLE | t=00:23:57**

> "Median lasted one candle, 82% reconnect within two candles."
**Source GPS: -NXzJs5JRks | END | t=00:25:31**

> "the strongest disconnect in Bitcoin's entire history was seven closes."
**Source GPS: -NXzJs5JRks | END | t=00:25:35**

7. **Gaps and numbers.**
   - SOURCED: EMA 5 (extracts/extract_-NXzJs5JRks.md:194 (MAV-19)). "About 3 closes" = late is in the extract's Stated mechanics of MAV-19 (paraphrase); the spoken line is extracts/extract_-NXzJs5JRks.md:192 (MAV-19).
   - OURS (spec :62): the pullback-entry reading, stop at a close below the 5 EMA, target the prior extreme.

### KR-S7 CAPITULATION: hammer on the biggest volume bar (provisional)
1. **Name / trader.** Krown (VOL, CAN: PROVISIONAL, two videos). Older spec id S7 (KROWN_LAYER_SPEC.md:63). His words: "capitulation", "mega candle". Side: long. Rule: KR-V07 (with KR-V03).
2. **What you see.** After a long downtrend, one mega candle with a huge lower wick and a strong close, sitting on the biggest volume bar of the chart; a hammer at the exact low of the move:

> "one like massive mega candle with a huge wick down and a strong close. That's episode one's hammer basically, and it's sitting on the biggest volume bar on the chart."
**Source GPS: UqAvU1loT_k | END | t=00:18:31**

> "bottoms love heavy volume and top parabolic blow off tops do as well, but not all tops"
**Source GPS: UqAvU1loT_k | END | t=00:18:55**

> "you're looking for big wicks the upside and big wicks to the downside with a reversal on the closure that's what we're looking for"
**Source GPS: 8MvxK_nxO-0 | MIDDLE | t=00:18:01**

> "that is gonna be indicative that the low is probably in at least for now"
**Source GPS: 8MvxK_nxO-0 | MIDDLE | t=00:16:46**

   Major pivots come on outsized volume (his weekly Bitcoin examples):

> "when you get that major spike in volume on a higher timeframe, you're probably at a big pivot point."
**Source GPS: UqAvU1loT_k | MIDDLE | t=00:11:05**

> "volume spiked up, God, like three, three and a half times the average. Yeah. What do you know? That was the low and price reversed from there."
**Source GPS: UqAvU1loT_k | MIDDLE | t=00:11:33**

3. **Entry, stop, target (his words).**
   - Entry: NOT STATED (the hammer's confirmation close, KR-S1, is the only entry wording). Stop [stop class: OURS]: NOT STATED; the spec's "below the hammer low" is OURS. Target: NOT STATED.
4. **Context and timeframe(s).** A long downtrend with "everyone bleeding"; a drift to a low on no volume is apathy and is rarely finished:

> "a market drifting to a low on no volume is actually more so apathy rather than panic"
**Source GPS: UqAvU1loT_k | END | t=00:19:08**

   Timeframe: weekly and daily Bitcoin. Rare: his named lows are three, so power is nil.
5. **BTC visibility: YES\*.** Needs Binance volume only; "the biggest volume bar of the chart" depends on the lookback (OURS).
6. **Evidence.** 0 trades in a ledger. Named lows (FTX, June 2022, March 2020) are from the extract's Stated mechanics (paraphrase).
7. **Gaps and numbers.**
   - SOURCED: about 2x the average at a macro low and 3 to 3.5 x at the March 2020 low are examples, not thresholds (extracts/extract_UqAvU1loT_k.md:79 (VOL-08), extracts/extract_UqAvU1loT_k.md:124 (VOL-13)).
   - OURS (spec :63): lookback for "biggest" and for "long downtrend"; wick ratio; stop.

### KR-S8 VOL-COMPRESSION BREAKOUT (BBWP)
1. **Name / trader.** Krown (kcMnnQr1VFg, "How to Know Exactly When to Enter a Trade", 2026-04-06). One video, PROVISIONAL, but the only setup with an entry, a stop and an exit all in his words. Older spec id S8 (KROWN_LAYER_SPEC.md:64). He presents it as a quick hypothetical on a chart (KCM-63 Stated mechanics, paraphrase). Side: both. Rules: KR-Q01-Q07, KR-Q05.
2. **What you see.**
   - The volatility percentile (BBWP, Bollinger Band Width Percentile) falls below about 25-35, "especially if it's coming down from a high level", while price sits in a range:

> "Whenever it gets below, you know, about 30, 35 or 25 to 35, anywhere in that pocket really is going to be considered low, especially if it's coming down from a high level."
**Source GPS: kcMnnQr1VFg | END | t=00:24:34**

> "low volatility, that would be about any anywhere below about 25% tile."
**Source GPS: kcMnnQr1VFg | BEGIN | t=00:07:18**

> "However, low volatility periods always precede high volatility periods."
**Source GPS: kcMnnQr1VFg | BEGIN | t=00:09:11**

   - Bias from the previous trend (up: look for higher lows; down: lower highs); he is positioned during the compression, not after the expansion:

> "If it's up, our bias is for further continuation to the upside, but and essentially to look for higher lows and vice versa for a downtrend."
**Source GPS: kcMnnQr1VFg | END | t=00:24:51**

> "As long as Bitcoin's within this range, the trend is still to the downside, or at least the buys is on for the downside breakout."
**Source GPS: kcMnnQr1VFg | MIDDLE | t=00:11:14**

> "Position during a compression, not after expansion. At least that's my personal way of doing it."
**Source GPS: kcMnnQr1VFg | END | t=00:29:12**

3. **Entry, stop, target (his words).**
   - Entry: do not anticipate; wait for the first candle that breaks the range with volatility rising through the 50th percentile and the momentum oscillator agreeing. His preferred variant enters earlier, inside the range, near the edge on the side of the bias, so a wrong break costs little:

> "Wait for the first candle that breaks the range. If you see volatility rising through there, especially back above 50th percentile, um, plus your momentum oscillator is also pointing in that same direction, you probably are about right on that breakout."
**Source GPS: kcMnnQr1VFg | END | t=00:25:03**

> "The right way to do it is position during compression. If you really want to play a breakout, like I said, my preferred way, identify a compression range, enter in on the closest area to confirm the next trending higher low or trending lower high."
**Source GPS: kcMnnQr1VFg | MIDDLE | t=00:20:00**

> "I would prefer to pick a lower high as long as this thing is operating within this range."
**Source GPS: kcMnnQr1VFg | MIDDLE | t=00:11:29**

> "I would prefer to enter when price is as close to the top side of the range as possible because if I'm then wrong, if I enter, for example, right here, and I'm wrong, and price crosses above the top side of the range and starts to break out above the top side of the range, then I just can take a very small loss."
**Source GPS: kcMnnQr1VFg | MIDDLE | t=00:11:39**

> "I personally like to do it that way cuz then I don't have to risk as much to figure out if I'm going to be wrong."
**Source GPS: kcMnnQr1VFg | MIDDLE | t=00:20:22**

   - Stop [stop class: CLEAR, structure only]: the opposite side of the compression zone; for an upside break a close below the bottom of the range; after the break it can move to the breakout area. Distance beyond the structure: NOT STATED.

> "stop on the opposite side of the compression zone."
**Source GPS: kcMnnQr1VFg | END | t=00:25:32**

> "then your stop, if you're going to be playing this breakout to the upside, has to be on a break, a closure below the bottom end of this range."
**Source GPS: kcMnnQr1VFg | END | t=00:25:42**

> "after price breaks out to the upside in this case, then you can move that stop to the breakout area."
**Source GPS: kcMnnQr1VFg | END | t=00:25:53**

   - Target / exit: take profit as volatility peaks; his chart example reads the 93rd percentile, then a reversal candle on high volatility:

> "you take profit as the volatility peaks. Ideally, enter when volatility is low, exit when volatility is high."
**Source GPS: kcMnnQr1VFg | END | t=00:20:43**

> "This one gets up to 93rd percentile. You got to be thinking, okay, we probably seen most of this move. I should be taking at least some profit, if not all profit."
**Source GPS: kcMnnQr1VFg | END | t=00:26:15**

> "this is a shooting star right here. See that on high volatility? Okay, we've probably seen most of the move."
**Source GPS: kcMnnQr1VFg | END | t=00:26:34**

   - Management: size down as volatility rises (KR-Q09). He warns that chasing the breakout after expansion is the classic loss and that breakouts "fail very very often":

> "These will fail very very often, but you can make it work just you know, you might fall into that issue of death by a thousand cuts."
**Source GPS: kcMnnQr1VFg | END | t=00:29:19**

4. **Context and timeframe(s).** His settings are for Bitcoin on higher timeframes; his chart timeframe for this example is not named:

> "basis moving average length seven and look back period 100. That is where, you know, your settings might be different. Uh these are the settings that I particularly like on Bitcoin for the higher term time frames."
**Source GPS: kcMnnQr1VFg | BEGIN | t=00:06:18**

> "High volatility, I consider with Bitcoin anything above 85% higher or more."
**Source GPS: kcMnnQr1VFg | BEGIN | t=00:07:07**

5. **BTC visibility: YES.** The indicator is computed from closes; no volume venue issue.
6. **Evidence.** 0 trades in a ledger; the setup is an illustration on a chart, no result is given.
7. **Gaps and numbers.**
   - SOURCED: BBWP basis length 7 and lookback 100 (extracts/extract_kcMnnQr1VFg.md:100 (KCM-11)); low below about 25-35 (extracts/extract_kcMnnQr1VFg.md:524 (KCM-63)); high above 85 (extracts/extract_kcMnnQr1VFg.md:109 (KCM-12)); confirm above the 50th (extracts/extract_kcMnnQr1VFg.md:540 (KCM-65)); 93rd as an example, not a rule (extracts/extract_kcMnnQr1VFg.md:572 (KCM-69)); 252 as a relaxed lookback (extracts/extract_kcMnnQr1VFg.md:323 (KCM-38)).
   - OURS (spec :45, :64): band multiplier 2; exact percentile formula; grid {80, 85, 90} x {25, 30, 35}; distance beyond the structure stop; range height (RNG-22) as a second exit arm.
   - NOT STATED: stop distance, which oscillator, how a range is identified, position size.

### KR-S9 TOP-4 SELL FRAMEWORK for a long-term holding
1. **Name / trader.** Krown (7IxfsuD2wCM, "Here's How I Know When To Sell My Long Term Investments", 2026-06-28). One video, PROVISIONAL. Older spec id S9 (KROWN_LAYER_SPEC.md:65). It is a sell signal for a long-term holder, not a short entry. Side: sell (long). Rules: KR-P01-P06, C11, V02, Q02, S05, S07.
2. **What you see.** Four things around the same weeks on a weekly (Bitcoin) or monthly (traditional markets) chart: a reversal candle, extreme volume, extreme volatility and a momentum signal (bearish RSI divergence or a MACD cross). Three of four = at least a major top; all four = probably a macro top:

> "if three of the four align, then you're probably at the very least at a major top, maybe a macro top."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:00:33**

> "of these four indications necessarily need to happen at precisely the same time, but we do want to see more or less all of them kind of working in unison around the same time."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:00:23**

> "you see all four, especially on a very very high term time frame unless we're talking about like a monthly in many cases for traditional markets or a weekly in many cases for Bitcoin and cryptos, then you are perhaps at that next major macro top."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:00:40**

   - Reversal candle (the most powerful and often first; three black crows = three down bars from the high):

> "you don't necessarily see it first, but I would say once you see this, you should start to look for those other signals because this is I would say this is the most powerful one."
**Source GPS: 7IxfsuD2wCM | MIDDLE | t=00:14:08**

> "Or if you get three bars down or three crow or three black crows, I believe it's what it's called. It's just basically three down bars from the high."
**Source GPS: 7IxfsuD2wCM | MIDDLE | t=00:15:16**

> "Some people would call this and define this as a bearish engulfing. I would actually would not."
**Source GPS: 7IxfsuD2wCM | MIDDLE | t=00:15:36**

   - Extreme volume = about 2 x the average of the past 30 days; extreme volatility = BBWP above 85; momentum = bearish RSI divergence (a MACD cross is the weakest, ignored alone):

> "the extreme value would be a an order of magnitude like two times the the average of the past 30 days for that time frame's volume."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:05:27**

> "but even just above 85% high, you know, that's starting to get pretty damn high. That that is starting to get into outlier territory. Um so, I would start to pay attention above there."
**Source GPS: 7IxfsuD2wCM | MIDDLE | t=00:11:35**

> "you're just looking for a divergence between price going up and your RSI oscillator making a lower high. So, higher high in price, lower high in oscillator."
**Source GPS: 7IxfsuD2wCM | END | t=00:18:59**

> "that would be the least important out of all these things. If you see just that signal in and of itself without any of the other ones, I would just completely ignore it."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:06:57**

3. **Entry, stop, target (his words).**
   - Entry: not an entry. He sells part of a holding when three or four signals fire; signals usually confirm a bar or two after the high, and the goal is to sell well, not the exact top:

> "it's not about one, it's about how many. And ultimately, you want to see at least three in my experience. Every once in a while, you will see something that just tops out with like two, on you know, only two. Um but for the most part, it's going to be three."
**Source GPS: 7IxfsuD2wCM | END | t=00:21:09**

> "The goal isn't to sell literally the exact top. It's to sell well, and then if you want to reposition lower, you can do that."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:03:32**

> "most of them will confirm maybe a bar or two after the actual high. And that can be on a higher term time frame like a weekly or monthly."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:03:52**

   - How much: 20 % to 80-85 % of the holding, set by the asset and its role:

> "when I say some, that might be, you know, as much as 80 to 85% or as little as 20%."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:01:17**

   - Stop [stop class: NOT STATED]: n/a (a sell signal). Target / exit: after all four, wait for the signals to reset; "reset" and the time to reposition are not defined (rule KR-P06 BLOCKED):

> "and then just wait for them to reset and uh you know, price usually takes a long time to kind of, you know, correct those sort of moves. And at some point, it will happen again. But uh but usually those moves do hold for quite some time."
**Source GPS: 7IxfsuD2wCM | END | t=00:21:32**

4. **Context and timeframe(s).** Weekly and monthly, sometimes quarterly; the daily only for a very new asset:

> "we're focusing on very high-term time frames here, weekly, monthly, really is what we're operating. Sometimes a quarterly as well. If it's a very new asset, maybe the daily, but again, not going to be as relevant."
**Source GPS: 7IxfsuD2wCM | END | t=00:21:44**

   Ranking: the reversal candle first, volume and volatility matter for parabolic highs, divergence is last ("the nail in the coffin"); one signal alone means little, and he lists his own non-tops (KR-P04):

> "the reversal candle, certainly the most important. The volume and volatility, very important as well, but only with regards to parabolic highs, not with, you know, general indices that kind of just march their way upwards and onwards. And then bearish divergence is kind of like the nail in the coffin."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:07:05**

> "these things, like I said, they will happen typically within a few bars of each other."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:07:21**

5. **BTC visibility: PARTIAL.** All four signals are OHLCV-derived (YES\*, Binance volume). The weekly Bitcoin sample is a handful of tops (his examples: 2017, 2021); if the series we hold starts in 2017-08 (card k0) the 2017 top has no warm-up for the 100-bar BBWP lookback and the 30-bar volume average. Not verified against the disk here.
6. **Evidence.** 0 trades in a ledger. Dated Bitcoin examples for the recall check (rule KR-P05): 2017 weekly, 2021 weekly.
7. **Gaps and numbers.**
   - SOURCED: 3 of 4 (extracts/extract_7IxfsuD2wCM.md:374 (TOP-35)); volume 2 x the 30-bar average, or a 60-bar average as the stated alternative ("you could do a 60-period average. You could do a 30-period average." 7IxfsuD2wCM t=00:12:40; bars of the signal timeframe, weekly/monthly, not days; t=00:05:27-00:05:36) (extracts/extract_7IxfsuD2wCM.md:64 (TOP-05)); (GPT audit F2) BBWP above 85 (extracts/extract_7IxfsuD2wCM.md:157 (TOP-14)); scale out 20-85 % (extracts/extract_7IxfsuD2wCM.md:32 (TOP-02)); signals 1-2 bars after the high (extracts/extract_7IxfsuD2wCM.md:44 (TOP-03)); three down bars (extracts/extract_7IxfsuD2wCM.md:222 (TOP-20)); weekly/monthly (extracts/extract_7IxfsuD2wCM.md:390 (TOP-37)).
   - OURS (spec :51, :65): "a few bars" = {2, 3, 4}; which 3 of 4; MACD (12, 26, 9); the 1/3-per-signal scale-out arm.
   - NOT STATED: "a few bars", reversal-candle size, reset rule, reposition level.

### KR-S10 TREND LINE, FIRST RETURN: reaction at a volume-anchored line
1. **Name / trader.** Krown (TRL). Not in the spec's S1-S9 (rule KR-L04 only, "event study"). His words: "reaction", "first pass", "scalp". Side: both. Rules: KR-L01-L05, L08.
2. **What you see.** A line through swing highs or lows (a line through two points is a hypothesis; three touches make a trend); two touches are enough if both turning points sit on heavy volume, "double or more the recent volume bars around those lows or highs". Price comes back to the line for the first time:

> "two points draw a line but two points is basically a hypothesis"
**Source GPS: 14bxwxC8gBQ | BEGIN | t=00:06:17**

> "what makes this a trend is three touches three touches makes it a trend"
**Source GPS: 14bxwxC8gBQ | BEGIN | t=00:06:31**

> "two touches on heavy volume at both touches at both turning points that is acceptable to draw early"
**Source GPS: 14bxwxC8gBQ | BEGIN | t=00:06:51**

> "when I say heavy volume I mean like double or more the recent volume bars around those lows or highs"
**Source GPS: 14bxwxC8gBQ | BEGIN | t=00:07:01**

> "when we see big volume spikes on highs or lows we can be a little bit more aggressive with drawing trend lines from that because usually those are going to matter a lot more"
**Source GPS: 14bxwxC8gBQ | MIDDLE | t=00:12:44**

3. **Entry, stop, target (his words).**
   - Entry: expect a reaction on the first return, at least a bounce; the first pass gives a decent scalp, not a home run. Trigger: NOT STATED.

> "if Bitcoin were to get back down to this trend line at some later point we should expect a reaction there it should be at least a bounce maybe a reversal but at least a bounce"
**Source GPS: 14bxwxC8gBQ | MIDDLE | t=00:13:13**

> "first pass you almost always have a decent scalp from there"
**Source GPS: 14bxwxC8gBQ | MIDDLE | t=00:14:15**

> "we're not trying to predict the future what we're trying to do is we're trying to get a high probable trade"
**Source GPS: 14bxwxC8gBQ | MIDDLE | t=00:14:40**

   - Stop [stop class: NOT STATED]: NOT STATED. Target: NOT STATED. Management: NOT STATED.
4. **Context and timeframe(s).** Horizontal levels matter more than diagonals (KR-L08). Timeframe: NOT STATED (his Bitcoin examples; the spec scopes the layer to 1w/1d/6h/4h, OURS).
5. **BTC visibility: YES\*.** Swings from klines; "heavy volume" is Binance volume.
6. **Evidence.** 0 trades in a ledger; one short scalp into a resistance line is described.
7. **Gaps and numbers.**
   - SOURCED: 3 touches for a trend (extracts/extract_14bxwxC8gBQ.md:82 (TRL-08)); 2 touches on heavy volume, double or more the recent bars (extracts/extract_14bxwxC8gBQ.md:93 (TRL-09)).
   - OURS: number of recent bars for "recent", swing size k (spec :42), line tolerance ("slices through").
   - NOT STATED: stop, target, hold time, size.

### KR-S11 TREND LINE BREAK, then buy the higher low on the broken line
1. **Name / trader.** Krown (TRL, SNR). Not in the spec's S1-S9 (rules KR-L06, Z09). His words: "a break is new information", "the line changes jobs". Side: both.
2. **What you see.** A legitimate line (not bent to fit) breaks with real follow-through; the same line then becomes the base for one or more higher lows (or the ceiling for lower highs). A phantom line breaks and crashes back:

> "connecting these highs one two three when it breaks out over here you actually get real fall through that's what we're looking for"
**Source GPS: 14bxwxC8gBQ | MIDDLE | t=00:10:46**

> "a break is not your line failing it's the market telling you the trend is changing"
**Source GPS: 14bxwxC8gBQ | MIDDLE | t=00:18:06**

> "the same line you were vying against becomes the ceiling or resistance that typically gets sold against so the line changes jobs more or less old support new resistance"
**Source GPS: 14bxwxC8gBQ | END | t=00:18:26**

> "now if it's a support it's not gonna be as binary it's gonna be a selling area"
**Source GPS: 14bxwxC8gBQ | END | t=00:23:50**

3. **Entry, stop, target (his words).**
   - Entry: buy a higher low at the broken line after the break. Trigger candle and price: NOT STATED.

> "when price breaks through over here it uses it more importantly that same trend line as a basing point for a couple more higher lows"
**Source GPS: 14bxwxC8gBQ | MIDDLE | t=00:11:38**

> "in this case you get a pretty easy chance to buy what is effectively a higher low"
**Source GPS: 14bxwxC8gBQ | MIDDLE | t=00:12:00**

   - Stop [stop class: NOT STATED]: NOT STATED. Target: NOT STATED. Management: NOT STATED. He adds that the line can break again, especially on lower timeframes (TRL-15, paraphrase).
4. **Context and timeframe(s).** The zone version of the same flip is the retest of KR-S2 (SNR-14). Timeframe: NOT STATED.
5. **BTC visibility: YES.** Line and closes from klines.
6. **Evidence.** 0 trades in a ledger; chart example with a Bitcoin low base (T3).
7. **Gaps and numbers.** No number. NOT STATED: how many higher lows, how far the follow-through must run, stop, target.

### KR-S12 TREND REVERSAL CONFIRMED BY A CLOSE (dominant level)
1. **Name / trader.** Krown (TRD; the "dominant highs and lows" episode, 2026-03-16). In the spec only as a filter (rule KR-L10); catalogued here because he says when a reversal entry is "not late". Side: both. Rules: KR-L09, L10, L11, L12.
2. **What you see.** Every market on every timeframe is an uptrend (higher highs and higher lows), a downtrend (lower lows and lower highs) or a range. A dominant low is the lowest low before price makes a new high; in a downtrend the dominant lower high is the most recent high from which a new low was made. A reversal is not confirmed until price trades and closes beyond the dominant level:

> "we have an uptrend, which is effectively higher highs and higher lows. We have a downtrend, which is lower lows and lower highs."
**Source GPS: 2-nG9bsMoPQ | BEGIN | t=00:04:27**

> "the dominant lows are the lows that happen in an uptrend that are the lowest low traded to before price action makes a new high within that overall trend."
**Source GPS: 2-nG9bsMoPQ | MIDDLE | t=00:09:06**

> "I would not confirm a reversal to the from an uptrend in this case to a downtrend until you trade and close below the most recent dominant higher low."
**Source GPS: 2-nG9bsMoPQ | MIDDLE | t=00:09:51**

> "in a downtrend, the dominant lower highs are the points in which I would not confirm a reversal until price supersedes it or closes above it. Reclaims it is what we call it."
**Source GPS: 2-nG9bsMoPQ | MIDDLE | t=00:11:18**

> "if this high does not reclaim this high, again, just by closing above it, basically, we don't have a reversal. And you should be very much skeptical of any sort of real reverse coming from this region until that happens."
**Source GPS: 2-nG9bsMoPQ | MIDDLE | t=00:13:33**

   One-bar jagged peaks are not treated as highs or lows:

> "when you see these sort of one-bar jagged peaks, they usually don't amount to that much. I would not treat them as highs or lows. Some people do. I think it's just going to be more confusing than it's worth"
**Source GPS: 2-nG9bsMoPQ | MIDDLE | t=00:14:13**

3. **Entry, stop, target (his words).**
   - Entry: after the reclaim close; he reframes feeling late as being on time with a confirmation. Trigger price: NOT STATED.

> "you'll feel like you're late to the trade, but no, you're not late to the trade. You are right on time with a confirmation."
**Source GPS: 2-nG9bsMoPQ | MIDDLE | t=00:13:48**

   - Stop [stop class: NOT STATED]: NOT STATED. He accepts a trap loss quickly; no level, no size:

> "there is a fake out right here. This would be your bull trap effectively. And hey, bull traps happen. That's That's literally the purpose of them is to fake you out with that higher high and then slam it back down for a new low."
**Source GPS: 2-nG9bsMoPQ | END | t=00:22:12**

> "I'm okay with losing on that and quickly realizing that's a loss and not losing any more than I need to if I'm trading a a trend strategy like that"
**Source GPS: 2-nG9bsMoPQ | END | t=00:22:46**

   - Target: NOT STATED.
4. **Context and timeframe(s).** In a sideways range favour the previous trend; the higher timeframe is the dominant trend:

> "you're in a sideways range consolidation basically, you almost always want to favor the previous trend. The previous trend is your friend."
**Source GPS: 2-nG9bsMoPQ | END | t=00:17:38**

   Timeframe: every timeframe; which timeframe's close counts is not stated (OURS).
5. **BTC visibility: YES.** A state machine over swings and closes.
6. **Evidence.** 0 trades in a ledger. His claim that this keeps you on the right side of the trend 90-95 % of the time is hypothesis H-L1, not an input (rule KR-F08, paraphrase).
7. **Gaps and numbers.**
   - SOURCED: no numeric parameter; the state machine is in words.
   - OURS (spec :42): bars each side {2, 3, 5}; size of a "one-bar peak"; swings on closes vs highs/lows; "about the same" range tolerance.
   - NOT STATED: entry order, stop, target.

### KR-S13 EFFORT VERSUS RESULT: huge volume, tiny candle (absorption)
1. **Name / trader.** Krown (UqAvU1loT_k, volume episode, 2026-09-26). Not in the spec's S1-S9 (rule KR-V06). One video, PROVISIONAL. His words: "effort versus result", "absorbed", "hollow". Side: both.
2. **What you see.** A tiny candle on the biggest volume of the chart: someone absorbed everything without letting price move. At a ceiling price likely turns back; at a floor the selling is absorbed and a bounce follows. The mirror: a huge candle on no volume is hollow:

> "Someone threw everything at this price and someone else absorbed every share of it without letting price move."
**Source GPS: UqAvU1loT_k | BEGIN | t=00:00:04**

> "When they agree, trust the move. When they disagree, someone enormous is on the other side. And price usually goes their way."
**Source GPS: UqAvU1loT_k | END | t=00:17:29**

> "if it was on a support, those are buy walls essentially, and it's being absorbed. So the selling is being absorbed. What happens after the selling runs out, you get a bounce."
**Source GPS: UqAvU1loT_k | END | t=00:17:50**

> "a huge candle on no volume looks powerful, but it's kind of hollow. There's no, there's no weight underneath it."
**Source GPS: UqAvU1loT_k | END | t=00:18:10**

3. **Entry, stop, target (his words).** Entry, stop [stop class: NOT STATED], target: all NOT STATED. He states the expectation (turn at resistance, bounce at support), not an order.
4. **Context and timeframe(s).** Daily and weekly bars; it matters at a level (compare KR-S1). Volume is Binance only (section 0).
5. **BTC visibility: YES\*.** Volume against candle range from klines.
6. **Evidence.** 0 trades in a ledger.
7. **Gaps and numbers.** No number: "tiny", "huge" and "biggest volume of the chart" are undefined; OURS would be a ratio of range to ATR and of volume to its average.

### KR-S14 RSI DIVERGENCE: regular and hidden
1. **Name / trader.** Krown (INOCBmqQupc "RSI Is Lying to You", 2026-04-03; also TOP). In the spec as a descriptive rule only (KR-S05, conflict C14: an earlier repo study found no edge on any timeframe). His words: "divergence", "hidden or continuation divergence". Side: both. He calls divergence the primary value of an oscillator but also "a confirmation, not a trigger".
2. **What you see.**
   - Regular bullish: price makes new lows while the RSI makes higher lows, the downtrend is weakening. Hidden bullish (continuation): price makes a higher low while the RSI makes a lower low, in an uptrend. Hidden bearish: a lower high on price while the RSI makes a higher high, in a downtrend. Regular bearish: higher high in price, lower high in the RSI:

> "And it is effectively looking for divergences."
**Source GPS: INOCBmqQupc | END | t=00:13:14**

> "regular bullish divergence happens when your downtrend is weakening. How do you know that? Because your trend is making new lows on price, but your RSI is making higher lows."
**Source GPS: INOCBmqQupc | END | t=00:13:40**

> "hidden bullish divergence happens in uptrends and it is effectively a continuation higher low, in which the uptrend finds a higher low compared to a previous low, but the RSI is making a lower low compared to the previous low."
**Source GPS: INOCBmqQupc | END | t=00:14:09**

> "hidden bearish divergence is in the context of a downtrend. Your lower high compared to another lower high is producing a higher high on the RSI compared to the previous lower high."
**Source GPS: INOCBmqQupc | END | t=00:14:59**

> "you're just looking for a divergence between price going up and your RSI oscillator making a lower high. So, higher high in price, lower high in oscillator."
**Source GPS: 7IxfsuD2wCM | END | t=00:18:59**

   - At weekly or monthly tops it shows three, sometimes four drives, rarely two (TOP-31). He misspoke the regular bearish case in INOCBmqQupc and the extract records it as spoken:

> "Bearish divergence, both regular and hidden, same thing but opposite. So, downtrend, new lows with higher lows on the RSI equals trend weakening, thus we look for a bounce."
**Source GPS: INOCBmqQupc | END | t=00:14:46**

3. **Entry, stop, target (his words).**
   - Entry: NOT STATED. He says what to expect, "look for a bounce" (regular bullish), "another move to the upside" (hidden bullish), continuation of the downside (hidden bearish). He also says the RSI is never a trigger:

> "It's a confirmation, not a trigger, is the point that I'm really working towards."
**Source GPS: INOCBmqQupc | MIDDLE | t=00:08:15**

   - Stop [stop class: NOT STATED]: NOT STATED. Target: NOT STATED. Management: NOT STATED.
4. **Context and timeframe(s).** Trend first, RSI second (RSI-40). Weekly or monthly (quarterly for a long-history index) for the tops version; otherwise NOT STATED.

> "Two, use the RSI for confirmation. If you're in an uptrend and you're breaking out of a range or continuing and you're seeing the RSI move above 70, you just confirmed the next leg to the upside most likely."
**Source GPS: INOCBmqQupc | END | t=00:15:48**

5. **BTC visibility: YES.** RSI of closes; the period is never stated (OURS 14, spec :48).
6. **Evidence.** 0 trades in a ledger.
7. **Gaps and numbers.** No numeric parameter in his words. OURS (spec :48): RSI period 14, divergence lookback and spacing. NOT STATED: lookback, spacing, size of the RSI difference, entry, stop, target.

### KR-S15 200-WEEK SMA: buy at or below the line
1. **Name / trader.** Krown (-NXzJs5JRks, moving-average episode, 2026-10-03). Not in the spec's S1-S9 (rule KR-M04, hypothesis H-M2). Side: long.
2. **What you see.** Price at or below the 200 SMA on the weekly chart, "about four years of price in one line". The extract (paraphrase of the Stated mechanics) records that Bitcoin's lows of 2015, 2018, 2020 and 2022 were called by it, and that buys at or below it were valuable long term. His back-test (26 years, six assets, 80 touches) is a claim stated in another video:

> "This 200 simple on the weekly, which is basically four years of price in one line"
**Source GPS: -NXzJs5JRks | MIDDLE | t=00:21:48**

> "I back tested 26 years of this exact line across six assets and 80 touches"
**Source GPS: -NXzJs5JRks | MIDDLE | t=00:22:58**

3. **Entry, stop, target (his words).** Entry, stop [stop class: NOT STATED], target: all NOT STATED. The buy-at-or-below wording is the extract's paraphrase; there is no verbatim quote for it in the block.
4. **Context and timeframe(s).** Weekly only.
5. **BTC visibility: PARTIAL.** A 200-period weekly SMA needs 200 weekly bars. If the series we hold starts in 2017-08 (card k0, not verified against the disk) the first valid value is about mid-2021, so only the 2022 low of his four is on our data. Few events: descriptive only.
6. **Evidence.** 0 trades in a ledger; the touches are chart observations.
7. **Gaps and numbers.** SOURCED: 200 periods on the weekly (extracts/extract_-NXzJs5JRks.md:161 (MAV-16)). His 26 years / 6 assets / 80 touches is a claim (rule KR-F08), conflict C7. NOT STATED: how far below, how long, entry, stop, target.

### KR-S16 COUNTER-TREND AT A VOLATILITY EXTREME
1. **Name / trader.** Krown (kcMnnQr1VFg). A single sentence, not in the spec and not in the rules ledger as its own rule (it sits next to KR-Q05/Q06). He calls it "a little more advanced" and defers detail to a course that is not in the corpus. Side: both (against the move).
2. **What you see.** Volatility very high (BBWP at the extremes, above 85 on Bitcoin) after an expansion; he plays the move that runs against the trend and leaves as volatility comes down:

> "if you're going to play counter trend trend moves, enter in the opposite direction when volatility is very high, and then exit as volatility comes down."
**Source GPS: kcMnnQr1VFg | END | t=00:20:49**

   His high-volatility reading (KR-S8) and what he says about very high volatility:

> "High volatility, I consider with Bitcoin anything above 85% higher or more."
**Source GPS: kcMnnQr1VFg | BEGIN | t=00:07:07**

> "Very, very high volatility, your move is mostly done if not already always all done."
**Source GPS: kcMnnQr1VFg | MIDDLE | t=00:15:49**

3. **Entry, stop, target (his words).**
   - Entry: "enter in the opposite direction when volatility is very high" and nothing more (trigger NOT STATED). Exit: as volatility comes down (SOURCED in the quote above). Stop [stop class: NOT STATED]: NOT STATED. Target: NOT STATED.
4. **Context and timeframe(s).** Timeframe NOT STATED; his BBWP settings are for higher-term Bitcoin (KR-S8).
5. **BTC visibility: YES.** The indicator is computed from closes.
6. **Evidence.** 0 trades in a ledger; no example is walked through.
7. **Gaps and numbers.** SOURCED: BBWP above 85 as "high" (extracts/extract_kcMnnQr1VFg.md:109 (KCM-12)). Everything else NOT STATED. Treat as a lead, not a rule.

## 4. Cross-trader overlap (research leads, not findings)

Agreement between independent traders is a research lead, not evidence: Tom, Fabio, Malkan and Krown teach in different markets and
timeframes, and none of the rows has a fee-net result. A row is listed only where both describe the same chart event, meaning the same
level type and the same trigger class. STRONG = same level type and same trigger class; PARTIAL = same event seen through a different
instrument or trigger (the difference is stated). Evidence: `quoted-both-sides` = both rows carry a block quote for the event (quotes below
or in the cited rows); `paraphrase` = only one side is in his words, or the match is my reading of a thin quote.

| KR row | other trader's row | same chart event | what differs | strength | evidence |
|---|---|---|---|---|---|
| KR-S1 | TOM-15 | support or resistance area first, then a candle formation there | his three formations (three in a line, inside bar, outside bar) vs hammer, star, strict engulfing, doji | STRONG | quoted-both-sides |
| KR-S1 | FAB-5 | a level defended again and again by one side | price zone proven by wicks/candles vs a resting order wall proven by absorption in the tape | PARTIAL | quoted-both-sides |
| KR-S2 | TOM-6 | breakout of a balance/zone judged on the close, with volume behind it | Tom adds clear space to the left and order flow; Krown adds the retest routine and range-height target | STRONG | quoted-both-sides |
| KR-S3 | TOM-2 | sell the top and buy the bottom of a balance, the middle is noise | Tom's proof is the profile (b-profile, finished auction); Krown's is a candle at the edge | STRONG | quoted-both-sides |
| KR-S3 | TOM-12 | price pokes outside the balance, fails, and the return inside is the signal | Tom trades the pullback after the return with the move and targets the start of the impulse; Krown acts on the close back inside | STRONG | quoted-both-sides |
| KR-S3 | FAB-4 | a probe out of a balance that fails and comes back inside | FAB-4 has no verbatim quote in SETUP_CATALOG.md (its rows are OURS and a frame note), so only Krown's side is in his words | STRONG | paraphrase |
| KR-S3 | TOM-7 | short the top and long the bottom of a range, scalp | Tom's range is measured around a flat VWAP; Krown's is two wick-to-close zones | PARTIAL | quoted-both-sides |
| KR-S4, KR-S8 | TOM-15, TOM-6 | a compression comes first, then the breakout | Tom reads compression in any form at a breakout level (and waits for consolidation after news); Krown measures it with falling volume or a volatility percentile | PARTIAL | quoted-both-sides |
| KR-S4, KR-S8 | FAB-1 | a flat balance, then the first candle that breaks out with volume behind it | Fabio's volume is order-flow (CVD, big trades) on an intraday chart; Krown's is bar volume or the volatility percentile on daily/weekly bars | PARTIAL | quoted-both-sides |
| KR-S5 | TOM-4 | a rising average used as the pullback line inside a healthy trend | VWAP anchored to the day (Tom) vs EMA/SMA of closes (Krown): a different line, same role | PARTIAL | quoted-both-sides |
| KR-S9 | TOM-16 | extreme volume at a high, then sellers take over | Tom: hedger volume and an aggressive seller, entry on the break of the last big buyers; Krown: 2x the 30-day average plus a weekly reversal candle, one of four signals | PARTIAL | quoted-both-sides |
| KR-S9 | MAL-16 | bearish RSI divergence (price higher high, RSI lower high) as the momentum leg | Malkan trades it alone with a red-candle confirmation; Krown uses it only as one of four top signals | PARTIAL | quoted-both-sides |
| KR-S13 | FAB-2, FAB-5 | big effort (volume or delta) with no price result means the other side is absorbing | bar volume against candle size (Krown) vs delta against price result in the footprint (Fabio) | PARTIAL | quoted-both-sides |
| KR-S13 | TOM-2 (viT_ trade) | selling pressure shown but price keeps rising | Tom's remark is a reason to abandon a counter trade; Krown's is a setup description | PARTIAL | quoted-both-sides |
| KR-S14 | MAL-14, MAL-16, MAL-17 | regular divergence: price makes a new extreme, the RSI does not | Malkan gives entry on a confirming candle, stop at the swing, target the midpoint C; Krown gives none of the three | STRONG | quoted-both-sides |
| KR-S14 | MAL-7, MAL-8, MAL-9 | reverse divergence = hidden divergence: with the trend, price holds a higher low while the RSI makes a lower low | Malkan builds a daily/weekly entry on it; Krown only says to expect continuation | STRONG | quoted-both-sides |
| KR-S16 | TOM-1 | fade an overextended move, exit as the extreme unwinds | Krown's extreme is a volatility percentile with one sentence of text; Tom's is a stalled push with thin profile above value | PARTIAL | paraphrase |

No overlap found for: KR-S6, KR-S7, KR-S10, KR-S11, KR-S12, KR-S15 (leash on a 5 EMA, capitulation hammer, volume-anchored trend lines, dominant-level trend flips, the 200-week SMA have no counterpart in the Tom, Fabio or Malkan rows read for this file).

### 4.1 The side-by-side quotes behind the quoted-both-sides rows

**KR-S3 and TOM-2 (the middle is noise).**

> "The middle, that's your no man's land. No memory, no zone, no edge."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:06:08**

> "you go short at the top and long at the bottom and that's it and everything in between is just noise"
**Source GPS: 4VXpUjhKG2U | MIDDLE**

**KR-S3 and TOM-12 (poke outside the balance, then the return inside).**

> "The quick poke below the floor that snaps back inside the range is signature fake out."
**Source GPS: 6aA-P4Gvhrc | MIDDLE | t=00:17:43**

> "The market has traded, crossed over briefly, and we call that a break-in, and so it usually continues."
**Source GPS: m3IMdc7QwN4 | MIDDLE**

**KR-S2 and TOM-6 (the close is the verdict).**

> "Only a close beyond the zone breaks a level. No close outside. We don't call it broken. Period."
**Source GPS: qEfES84jwwo | END | t=00:30:46**

> "in the PBD concept, we don't use the absolute high and low points, but we always look at the closing prices and the market openings"
**Source GPS: Ly62G168MkQ | BEGIN**

> "I have a breakout here with this higher closing price."
**Source GPS: uFxYcpiaOpw | END**

**KR-S1 and TOM-15 (a candle formation only counts at a support or resistance area).**

> "when you align these things they become infinitely more powerful"
**Source GPS: 8MvxK_nxO-0 | END | t=00:29:10**

> "And it's also absolutely essential to check whether there was a resistance or support area beforehand where this candlestick formation could give me an advantage."
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**

**KR-S1 and FAB-5 (a level defended again and again).**

> "if you get a same hammer twice on the left it lands on a level the market is already defended twice so when you get two hammers on the same level that's a signal"
**Source GPS: 8MvxK_nxO-0 | END | t=00:28:20**

> "In this one, this is amazing because you have a protection wall that is there. This is a resting liquidity, is not fresh liquidity and as you can see the market approach here and get absorbed the first time, strike again this area, absorb the second time, strike this area, absorb the third time"
**Source GPS: FawPrRUGNpk | BEGIN**

**KR-S3 and TOM-7 (short the top, long the bottom).**

> "you could buy, you know, buy near the low side of the range, sell near the high side of the range, but not look for the breakout until you get an objective signal of a breakout."
**Source GPS: kcMnnQr1VFg | MIDDLE | t=00:12:59**

> "Then you have the opportunity to keep looking for shorts at the top and keep looking for longs at the bottom until a reversal of the market environment eventually occurs."
**Source GPS: 43JaKHRvxHk | END**

**KR-S4, KR-S8 and TOM-15, TOM-6 (compression first).**

> "We can call that a coil, basically a range on declining volume."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:09:53**

> "always make sure to check beforehand whether a compression has built up in whatever form"
**Source GPS: 2xnNPIyHGQ4 | MIDDLE**

> "I wait to see if a consolidation occurs, and only if a consolidation happens."
**Source GPS: gFJBg8Bsw68 | BEGIN**

**KR-S4, KR-S8 and FAB-1 (the first candle that breaks out with volume).**

> "Wait for the first candle that breaks the range. If you see volatility rising through there, especially back above 50th percentile, um, plus your momentum oscillator is also pointing in that same direction, you probably are about right on that breakout."
**Source GPS: kcMnnQr1VFg | END | t=00:25:03**

> "the first moment that we had some kind of follow up on volume and confirmation from price was exactly this candle. This was my first position because the market told me Fabio we are going down the volume pressure is down and we have the price action that is following up."
**Source GPS: 0jM5Y31YJak | MIDDLE**

**KR-S5 and TOM-4 (a rising average as the pullback line in a trend).**

> "the green 55 EMA as dynamic support and and also the yellow 21 EMA as dynamic support for the shorter term"
**Source GPS: -NXzJs5JRks | END | t=00:33:11**

> "If I see the whole thing as a trend following trader, I have to wait for a long trend and can wait until the VWAP gives me a pullback."
**Source GPS: 43JaKHRvxHk | MIDDLE**

**KR-S9 and TOM-16 (extreme volume at a high, then sellers).**

> "the extreme value would be a an order of magnitude like two times the the average of the past 30 days for that time frame's volume."
**Source GPS: 7IxfsuD2wCM | BEGIN | t=00:05:27**

> "This volume isn't created by us traders, but by so-called hedging transactions."
**Source GPS: cw8LWQmec1E | MIDDLE**

> "At this precise moment, we can see that an aggressive seller finally comes in to drive the price."
**Source GPS: cw8LWQmec1E | MIDDLE**

**KR-S9, KR-S14 and MAL-16 (bearish RSI divergence).**

> "you're just looking for a divergence between price going up and your RSI oscillator making a lower high. So, higher high in price, lower high in oscillator."
**Source GPS: 7IxfsuD2wCM | END | t=00:18:59**

> "It is making a new high from A to B but RSI has made a lower high from A to B, which means its upward speed has reduced at point B."
**Source GPS: Wvq1TZh8aF0 | BEGIN**

**KR-S14 and MAL-17, MAL-14 (regular bullish divergence).**

> "regular bullish divergence happens when your downtrend is weakening. How do you know that? Because your trend is making new lows on price, but your RSI is making higher lows."
**Source GPS: INOCBmqQupc | END | t=00:13:40**

> "Bullish divergence will come in a down trend. Right? And he will give us the signal to buy."
**Source GPS: Wvq1TZh8aF0 | BEGIN**

> "So, this divergence is now telling us to buy in Do Trade."
**Source GPS: cQ-y1oULkBw | MIDDLE**

**KR-S14 and MAL-7, MAL-8, MAL-9 (reverse divergence = hidden divergence).**

> "hidden bullish divergence happens in uptrends and it is effectively a continuation higher low, in which the uptrend finds a higher low compared to a previous low, but the RSI is making a lower low compared to the previous low."
**Source GPS: INOCBmqQupc | END | t=00:14:09**

> "a very powerful and very hidden concept which is called reverse divergence, which many people also call hidden divergence"
**Source GPS: A-CQiV_UFB4 | BEGIN**

> "Whenever you look at an up trend, what I have to look for is a positive reverse divergence."
**Source GPS: A-CQiV_UFB4 | MIDDLE**

**KR-S13 and FAB-2, FAB-5 (effort without result).**

> "Someone threw everything at this price and someone else absorbed every share of it without letting price move."
**Source GPS: UqAvU1loT_k | BEGIN | t=00:00:04**

> "the result of the price for a pressure in by delta was almost zero. So this is a confirmation that the buyers are punching a wall and I want to be short in this position."
**Source GPS: 0jM5Y31YJak | END**

**KR-S13 and TOM-2 (the viT_ trade).**

> "When they agree, trust the move. When they disagree, someone enormous is on the other side. And price usually goes their way."
**Source GPS: UqAvU1loT_k | END | t=00:17:29**

> "Thirdly, although the delta showed that a lot was being sold, the market continued to rise."
**Source GPS: viT_VzF5Fsw | END**

### 4.2 Context overlap that is not a row

Krown's RSI regime (KR-S03: in an uptrend the RSI generally holds above 40, in a downtrend below 60, 40-60 means a range) is the same
40/60 regime Malkan's RSI system uses (MAL-2, MAL-10, MAL-13; KROWN_LAYER_SPEC.md:89 already records this). Krown uses it as a context
filter, Malkan as the entry rule (RSI taking support at 60, daily RSI near 40 under a monthly/weekly RSI above 60). It is a lead for the
Malkan layer's G3 marks, not a Krown setup.

> "when you're in an uptrend, you generally oscillate or you generally stay above a 40 read on the RSI."
**Source GPS: INOCBmqQupc | MIDDLE | t=00:07:20**

> "I showed you a couple of examples of what we call as the by setup on setup number one which is five star setup with monthly about 60 weekly about 60 and daily at 40 support was the trend"
**Source GPS: 2HcJ3NeZmEQ | BEGIN**

## 5. What this catalogue does not settle

- Corpus: 14 TA videos + 1 fees video. The 4 videos blocked by HTTP 429 (hNfjyrJEytI, fMRvOt26xcA, LB3DRYxnA0A, _JoJbu_Ug-A) and the 18 hidden
  playlist entries are unread; a setup there would be missing from this file. 67 of the 105 non-reject rules come from fewer than 3 videos
  (PROVISIONAL, KROWN_LAYER_SPEC.md:15); every KR row except KR-S1 to KR-S4 and the filters in 2.1 rests on one or two videos.
- No Krown trade exists: the corpus is a concept course, so there is no ledger and no real-trade evidence for any row (tier T3).
- Stops: only KR-S1 (close-based exit) and KR-S8 (far side of the compression zone) have a stated structure; no distance exists. His preference
  not to leave a resting stop conflicts with the MTS protective-stop rule (C3, decision q-krown-stop).
- Volume: all `YES*` rows need volume and we hold Binance volume only (C6, KR-V11 BLOCKED).
- Open conflicts carried from KROWN_CONSOLIDATED.md and not settled here: C1 (touches weaken vs matter), C2 (retest required vs not), C3
  (resting stop), C5/C10 (plain relative volume is a clock on BTC; 20 vs 30 vs 60 periods), C13 (85 vs 80-85, 25 vs 25-35), C14 (RSI divergence
  has no edge in the repo's own study).
- Earlier repo evidence is not friendly to the S/R, candle and divergence rows (KROWN_LAYER_SPEC.md:21-24); this file does not test it.
- Next steps (not done here): G3 blind eye-read of KR-S1 to KR-S4, KR-S8 by two readers on BTC charts; the Krown cards Q66-Q69 stay untouched until then.
