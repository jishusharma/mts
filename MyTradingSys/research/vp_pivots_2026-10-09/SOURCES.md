# VP anchored at pivots: what Tom says, and what the engine does today (2026-10-09)

Operator ask: "we do not draw volume profiles from pivot points ... From Highs and lows that are meaningful!"
Scope: Step 1 (sources first). All Tom quotes are verbatim from `raw_transcripts_canonical/<id>_raw.txt`
(file:line = the physical line in that file; the auto-caption files hold a whole video on 1-20 very long lines,
so the quote text itself is the locator). Quote blocks are checked by
`python scripts/dev/verify_extract_quotes.py MyTradingSys/research/vp_pivots_2026-10-09/SOURCES.md`.
All transcripts below are Tom's channel (titles "Trading World Champion reveals" / "World Champion LIVE").
`FawPrRUGNpk`, `StaphlRH8NQ`, `fZlNGWvd2Ko` (timestamped English captions, other creators) were searched and
excluded: their "pivot" / "anchor" hits are unrelated.

## 1. Result in one paragraph

Tom DOES say where a volume profile is drawn from: a *composite* profile over the data "from the last major high
to the last major low" (sQ_biBKhPVU:19), i.e. the leg between the two extremes, not years of data; he also says a
profile is just "a price movement ... started at time X ... reached ... time Y" (YmygDgtoxO8:19), profiles can be
merged while price stays in one fair range (1utSjHs_Mq8:19), and the reaction levels are POC, VAH, VAL
(aursfDVYzUk:7). He does NOT give a mechanical rule for what a "major"/"significant" high or low is: no fractal
width, no ATR or percent size, no time-frame, no count of legs. Only qualitative cues exist (section 3). Therefore
the pivot definition is a NO-SOURCE parameter. It is the single thing to be varied openly (section 4).

## 2. Tom on where a profile is anchored

Q1. The composite anchor (the key quote):

> "Just load all the data you see on the left side relative to the current price. That means what data is above, what data is below, and what can you derive from that. You don't need four or five years of data, just all the data from the last major high to the last major low."
**Source GPS: sQ_biBKhPVU | MIDDLE**
(sQ_biBKhPVU_raw.txt:19, after "Number two is volume profile composite".)

Q2. What he does with it (reaction at high-volume areas, rejection at low-volume areas):

> "And if you just draw in these high volume areas, you'll see that the market repeatedly triggers reactions there."
**Source GPS: sQ_biBKhPVU | MIDDLE**

> "the market likes to reject such low volume areas and runs back to liquidity."
**Source GPS: sQ_biBKhPVU | MIDDLE**

Q3. A profile is the volume of one price movement between two points in time (the anchor is the start of a move):

> "At some point it started at time X and has now reached this point here at time Y."
**Source GPS: YmygDgtoxO8 | BEGIN**
(YmygDgtoxO8_raw.txt:19)

> "The volume profile clearly shows us exactly how much trading volume was transacted in this particular price movement"
**Source GPS: YmygDgtoxO8 | BEGIN**

Q4. Merging / re-anchoring rule (a bigger profile only while price stays in one range; value area = 70% of trades):

> "we can merge profiles. Meaning we can combine them and create one large profile if we see that prices are consistently staying within a fair range."
**Source GPS: 1utSjHs_Mq8 | END**
(1utSjHs_Mq8_raw.txt:19)

> "And this makes sense as long as a market doesn't generate new shifts for itself."
**Source GPS: 1utSjHs_Mq8 | END**

> "we immediately know for each respective day where to narrow down where 70% of the trades took place"
**Source GPS: 1utSjHs_Mq8 | END**

Q5. The levels read off a profile:

> "They are always the point of control, always the value area high, and the value area low."
**Source GPS: aursfDVYzUk | END**
(aursfDVYzUk_raw.txt:7; same line: "I have here so-called reaction levels, value high, value low, and if applicable, the point of control.")

Q6. Old (session / day / week) profiles as the second anchor family he uses today:

> "Here, I consider where in these old profiles the major market participants entered and from which point the probability is high that the trading volume will drop off."
**Source GPS: ODdF0Bn_KSc | MIDDLE**
(ODdF0Bn_KSc_raw.txt:7)

> "A naked POC isn't an edge in itself, but rather it's an indication for me that there was aggressive trading there"
**Source GPS: ODdF0Bn_KSc | MIDDLE**

> "In day trading we can now do the following. For example, we can analyze the previous day"
**Source GPS: BVpYGKz9PBU | BEGIN**
(BVpYGKz9PBU_raw.txt:19)

Q7. A profile of a specific prior range, used as a reaction zone:

> "This right here is the volume profile for this price range. Then we can assume the market is accepting this level again."
**Source GPS: 0CrkbfuIhkc | BEGIN**
(0CrkbfuIhkc_raw.txt:19)

No quote anywhere says "anchor", "fixed range", "pivot", "from the swing low" or "AVWAP" for a volume profile
(searched all 102 files for: swing high/low, pivot, anchor, from the high/low, composite, merge, naked, significant,
major, meaningful, draw the profile, and profile within 120 characters of high/low/range/from/since/start).

## 3. What makes a high or low "meaningful" to Tom (qualitative only)

M1. Bounds of the range he is interested in; "last", "significant", no number:

> "Where was the last high? It was right here. Where was the last low of the movement that we currently find interesting? As you can clearly see, right here was the last significant low. This means that with this high and this low, I'm going to define the current trading range"
**Source GPS: HySZZSjMxF8 | BEGIN**
(HySZZSjMxF8_raw.txt:58-66; this is the only place he names the high/low pair that defines a range.)

M2. Higher time frame = more significant:

> "the larger a time period is, the more likely it is that the signal will be significant when a technical level is broken, overtraded, or whatever."
**Source GPS: HySZZSjMxF8 | BEGIN**
(HySZZSjMxF8_raw.txt:41-44)

M3. A top or bottom is real (finished) only if volume dries up at the extreme; high volume at the extreme means unfinished:

> "When there are high volumes at the tops or lows, the auctions are very often not yet finished, not yet completed."
**Source GPS: oa8kxSLLkAo | BEGIN**
(oa8kxSLLkAo_raw.txt:19)

> "Often, you'll see a zero, a zero, a three, a five, a seven, then you know this auction is really finished."
**Source GPS: oa8kxSLLkAo | MIDDLE**

M4. "Swing" without a definition (used for stops and targets, not profiles):

> "And I then placed my stop loss below the last swing low again."
**Source GPS: kXhIAug0Gh8 | END**
(kXhIAug0Gh8_raw.txt:19)

Reading: "meaningful" = the extremes of the current range on a higher time frame; and, at footprint level, an
extreme with a thin (zero / one-sided) tail is a finished auction. M3 needs tick or footprint data (not in the 1m
cache), so it is a later layer, not part of phase A. There is NO size, ATR, fractal-count or time rule. So:

**NO-SOURCE: the pivot definition.** (flagged per the provenance rule; never tuned on results)

## 4. The one thing varied openly (pre-registered, all cells reported, nothing selected)

| Parameter | Values | Why these | Status |
|---|---|---|---|
| Fractal width n (bars each side, 1h bars, strict > / <, wicks) | 2, 3, 5 | operator's list; the repo's only swing implementation `layers/cryptocred/cc_structure.py find_swings` (FORMULAS.md section 9) | NO-SOURCE |
| Size filter k (leg to previous opposite pivot >= k x ATR14(1h), plain SMA ATR per FORMULAS.md section 12) | 0 (none), 2 | "major / significant" has no number; 2 is a placeholder, reported next to 0 | NO-SOURCE |
| Pivot time frame | 1h only | M2 says higher is more significant; 1h is the lowest frame the engine already trusts for swings (SetupCandidatesBuilder.java:304-307) | NO-SOURCE choice, not varied |

The profile SHAPE is sourced (Q1: last high to last low); the choice of an alternative anchor "from the last pivot
to now" (developing profile) is the operator's idea, not Tom's words, and is reported as a separate source family
(A2), never merged into the Tom-shaped family (A1).

## 5. What the engine anchors today (code, with file:line)

All in `src/main/java/datafeed/`. Not a single profile is anchored to a swing; every anchor is a calendar boundary.

| Profile | Anchor | Where |
|---|---|---|
| `daily_vp` ("session") | 00:00 UTC to now, 1m bars (falls back to the last 200 1m bars if empty) | MarketDataSnapshot.java:91-100, 182 |
| `weekly_vp` | Monday 00:00 UTC to now, 1h bars | MarketDataSnapshot.java:102-111, 154 |
| `prior_week_poc`, `two_week_ago_poc` | previous / second previous Monday-Sunday, 1h bars | MarketDataSnapshot.java:156-180 |
| `post_funding_vp` | last 08:00 UTC to now, 1m, fixed 10.0 bin (module, demoted out of the zone list) | MarketDataSnapshot.java:113-121, 183; SetupCandidatesBuilder.java:278-279 |
| `intraday_4h_vp` | last 4h boundary (00,04,08..) to now, 1m bars | MarketDataSnapshot.java:122-130, 184 |
| `prior_day` (POC/VAH/VAL, plus close/high/low) | previous UTC calendar day, 1m bars | MarketDataSnapshot.java:131-140, 185-197 |
| naked POCs | prior UTC day's POC, "visited" when a later 1m bar's range contains it | MarketDataSnapshot.java:202; NakedPocTracker.java:135-147; revisit threshold 0.3% at :26 |

Profile builder `buildVp` (MarketDataSnapshot.java:538-660): bins = max(50, floor(range/5)) so about $5 per bin;
each bar's volume is spread over its high-low points with triangular weights around the typical price and
normalised so a bar adds exactly its own volume (F-BT-09, :583-607); POC = max bin; value area = 70%
(`VALUE_AREA_PCT`, :28) grown from the POC one bin at a time toward the larger neighbour (:613-626). Zone list that
feeds setups: SetupCandidatesBuilder.java:272-322 (weekly, daily, 4h, VWAP, prior_day, 1h/15m/5m swings, FVG,
naked POCs). Swings there (MarketDataSnapshot.java:780-815 `buildStructure`) are "close pivots" inside a short
lookback (24 x 1h, 16 x 15m, 12 x 5m bars) and are used as price zones only; their volume is never profiled.

Consequences for the test: (1) the comparator families are session (developing UTC day), prior day, weekly and
prior week; (2) the engine refreshes levels on a 15 min snapshot cadence (TomSnapshotGen stepMin=15,
`backtest/tom_bt.py` STEP_S = 900), so developing profiles are refreshed every 15 min in the test too;
(3) this probe uses 5m bars (not 1m / 1h as the engine does for some profiles) and one shared profile builder for
every family, so the comparison isolates the anchor, not the builder.
