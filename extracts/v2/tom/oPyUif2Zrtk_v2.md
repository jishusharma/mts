# V2 extract oPyUif2Zrtk (session 2026-10-09, jisnb/tom-extract-2026-10-09b)

Method: EXTRACTION_METHOD_V2.md (decision rows, anchors machine-checked) + playbook Part J tiers on the derived rules (section 3.7).
Read in full, one chunk. Chart walk-through on S&P footprint charts (5-minute and 30-minute). No trade is taken; the long at the end is a hypothetical ("let's assume the market gives us the chance to do a pullback").

## 3.1 Header
```
video_id: oPyUif2Zrtk
trader: Tom Vorwald (channel "Tom Vorwald EN"; he speaks of himself in the third person once: "what Tom is even talking about here")
title: Forget Candlestick Charts... Use THIS Instead!
instrument_stated: S&P ("this time frame from the 5-minut chart in the SNP")
instrument_inferred: none
tick_size: unknown
session / time of day: "at the market opening" (one 5-minute example); otherwise unknown
translation_warning: yes (auto-captioned, non-native English; "30inut" = 30-minute, "5-minut" = 5-minute; sponsor break "World class edge" left in the raw file)
body_chars: 10501
n_decision_rows: 14
n_trades: 0
```

## 3.2 Decision log
| # | pos% | type | side | price/level | what he looks at | decision (his words, short) | info used | condition |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | LESSON | - | - | candlestick formations | some "work quite well, provided they are at the right price level" | candles | "provided they are at the right price level" |
| 2 | 6 | LESSON | - | - | footprint, volume profile | three questions: "where is the highest liquidity", "what do the highs and lows look like", what the areas with "absolutely no liquidity" tell you | footprint chart | none stated |
| 3 | 17 | CONTEXT | - | impulse + inside bar | candle pattern | impulse and inside bar are "a trend" and then "a waiting station", "a price range where a market usually accumulates volume" | candles, volume | "depending on the time frame" |
| 4 | 27 | CONTEXT | - | one footprint row | bid/ask per price | "104 sales, 147 purchases": blue "Because there's a large buying imbalance" | footprint | none stated |
| 5 | 30 | LESSON | - | high / low of a move | finished / unfinished auction | real exhaustion at the top means "no more liquidity is being played there", "a sign that a reversal could be coming" | footprint extremes | none stated |
| 6 | 37 | LESSON | - | high-volume price range | volume profile | if price "runs below such a price range" with constant liquidity, "it looks down at all that liquidity again" | volume profile | "if the market then runs below such a price range" |
| 7 | 44 | CONTEXT | - | top of the S&P 5-minute move | footprint imbalance | after a buying-imbalance push up, "the selling imbalance is dominant" at the top | footprint | none stated |
| 8 | 51 | LESSON | - | greatest-liquidity price | volume profile | "the market likes to head back exactly to where it picks up this information, namely where the greatest liquidity was" | volume profile | "very often" |
| 9 | 57 | CONTEXT | - | 30-minute low | footprint at the low | lots of liquidity at the low, "the market didn't go any lower even though there were significantly more sales" and "several strong buying levels" | footprint | none stated |
| 10 | 65 | LESSON | short | top of an impulsive candle | liquidity above | large buys "probably just short covering because the big seller is still dominant"; trend continuation "provided you're currently trading the short side" | footprint, larger time frame | "the big seller is still dominant" |
| 11 | 71 | LESSON | - | range low | break below | the run back down to liquidity holds "only if the market also goes below this point"; if it continues over, "a higher probability that it's still striving for further highs" | price vs range | "If it continues over as it's doing now" |
| 12 | 75 | LESSON | - | range top and bottom | liquidity at both ends | "this entire range here is much more important to evaluate than a single move" | volume profile, footprint | none stated |
| 13 | 82 | ENTRY (hypothetical) | long | pullback into a strong-buy price area | footprint at pullback | "more likely to go long here" where "there were strong buys" and "below this range there was rejection" | footprint | "let's assume the market gives us the chance to do a pullback" |
| 14 | 88 | REJECT | long | opening-range price area | selling surplus | "I won't be looking for a long position in this price range"; "from 71 onwards, it makes sense to look for a trend continuation" | footprint at the open | "there was a significant selling surplus right here" |

## 3.3 Trade blocks
No trade is taken. Row 13 is a hypothetical long on a pullback; row 14 names a level ("from 71 onwards") with no entry, stop or target. n_trades: 0.

## 3.4 Rejections and conditions
- Row 14 (REJECT): no long in a price range with "a significant selling surplus"; looking for continuation only "from 71 onwards", after big buyers stepped in.
- Row 11 condition: the move back down to the high-liquidity area only counts if price goes below the range low; holding above means further highs are more likely.
- Row 10 condition: buys at the top of an impulse are read as short covering while "the big seller is still dominant".
- Row 1 condition: candle formations only "provided they are at the right price level".

## 3.5 Verbatim anchors
> "Yes, there are some that work quite well, provided they are at the right price level."
**Source GPS: oPyUif2Zrtk | BEGIN**

> "A waiting station is nothing more than a price range where a market usually accumulates volume."
**Source GPS: oPyUif2Zrtk | BEGIN**

> "Why is that blue? Because there's a large buying imbalance."
**Source GPS: oPyUif2Zrtk | BEGIN**

> "And if no more liquidity is being played, that's a sign that a reversal could be coming."
**Source GPS: oPyUif2Zrtk | BEGIN**

> "And if the market then runs below such a price range like here and continues to have constant liquidity, what's the likely result?"
**Source GPS: oPyUif2Zrtk | MIDDLE**

> "the market likes to head back exactly to where it picks up this information, namely where the greatest liquidity was."
**Source GPS: oPyUif2Zrtk | MIDDLE**

> "Even if there were large buys here, it was probably just short covering because the big seller is still dominant."
**Source GPS: oPyUif2Zrtk | MIDDLE**

> "Yes, but only if the market also goes below this point."
**Source GPS: oPyUif2Zrtk | END**

> "this entire range here is much more important to evaluate than a single move."
**Source GPS: oPyUif2Zrtk | END**

> "And so we have the possibility to claim now that it's more likely to go long here because the market has given me this information."
**Source GPS: oPyUif2Zrtk | END**

> "Because of that, I won't be looking for a long position in this price range."
**Source GPS: oPyUif2Zrtk | END**

> "you just use the 30 minute chart, which by the way is always very smart because it's based on market profiling."
**Source GPS: oPyUif2Zrtk | END**

## 3.6 Ambiguity flags
- Row 14: "71" is a price on the S&P 5-minute chart with no handle; the full level is not readable from the transcript.
- Rows 4-5: "finished and unfinished auction" is named but not defined in this video (no rule for how many contracts at the extreme make an auction finished).
- Row 6 vs row 11: two images give opposite outcomes for the same structure; he resolves it with the break below the range (row 11). Which range edge counts as "this point" is from the picture, not stated.
- Row 13: "strong buys" has no threshold; row 4 ("104 sales, 147 purchases" coloured blue) is the only number for an imbalance and the colour rule of his software is not stated.

## 3.7 Candidate rules, with provenance and the Naked BTC chart test
Tier = playbook Part J (T1 example, T2 self-check, T3 calculation, T4 recommendation, T5 command). Location tag = [T/id:file line@char offset in the raw file].

R-oPyU-1 | T1 (example) | Price that leaves a high-volume price range tends to return to it ("the market likes to head back exactly to where it picks up this information"), but in a range only after price goes below the range low; holding above the range points to further highs.
- Source: [T/oPyUif2Zrtk:7@5453] ; [T/oPyUif2Zrtk:7@7533] ; [T/oPyUif2Zrtk:7@7634]
- Naked BTC chart test: partly. The highest-volume price of a range is computable from candle volume (volume profile over the range); the range edges and "goes below this point" are drawn from his picture, NO-SOURCE as a definition. "very often" is not a rate.

R-oPyU-2 | T1 (example) | Exhaustion at a high (no more liquidity traded there, a finished auction) is a sign a reversal could be coming.
- Source: [T/oPyUif2Zrtk:7@3156] ; [T/oPyUif2Zrtk:7@3427]
- Naked BTC chart test: no. Needs footprint (bid/ask volume per price at the extreme). Not computable from OHLCV.

R-oPyU-3 | T4 | Do not take a candle formation alone as the entry; check it against where liquidity sits (footprint and volume profile) at both ends of the range.
- Source: [T/oPyUif2Zrtk:7@10186] ; [T/oPyUif2Zrtk:7@9624]
- Naked BTC chart test: the volume-profile half is computable from candles; the footprint half is not.

R-oPyU-4 | T1 (example) | No long inside a price range that shows a significant selling surplus at the open; look for continuation only after big buyers step in above it.
- Source: [T/oPyUif2Zrtk:7@9244] ; [T/oPyUif2Zrtk:7@9395]
- Naked BTC chart test: no. "selling surplus" and "big buyers" are footprint reads; no threshold given.

R-oPyU-5 | T4 | For longer swings use the 30-minute chart ("based on market profiling").
- Source: [T/oPyUif2Zrtk:7@9954]
- Naked BTC chart test: yes as a time-frame choice. No other parameter.

Rules with parameters and no source: none in this file. Not found in this video: any stop, target, size or numeric imbalance threshold.

## 3.8 Self-check
- Last decision row pos% 88: row 14 is the last chart item; after it only the closing lines, which restate rules 3 and 5 (no new decision).
- Terms CT / TC / trend_healthy / tier: tier appears only in section 3.7, as the playbook Part J tiers.
- Gate result is pasted at the end of the file after the run.

## Gate result (2026-10-09)
```
verify_extract_quotes.py: PASS: 0 problem(s) (12 anchors)
inline quoted fragments: all verbatim (extract_fix_gps.py)
```
