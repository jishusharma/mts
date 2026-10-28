# V2 extract o-w5Gxss6T0 (Fabio; "3 Order-flow Trading Tricks Exposed!": volume-defined fair value gap, CVD absorption)

Method: EXTRACTION_METHOD_V2.md, compact form (a lecture with illustrations; no live trade). Read in full, start to end, 2026-10-18.
Label rule: every quote is SOURCED (file:line in `raw_transcripts_canonical/o-w5Gxss6T0_raw.txt`, caption file, 8 minutes, no `# ---` header). Anything marked OURS is our reading, not Fabio's.

## Header
```
video_id: o-w5Gxss6T0
trader: Fabio (first person: "I was ranked four times in the world most famous competition as a top sculper"; staged as fabervaale_o-w5Gxss6T0_raw.txt; Deep Charts promotion at the end of the intro)
identity check: not a duplicate of any file in raw_transcripts_canonical (8-word overlap with the nearest file 0.08 %)
instrument_stated: NASDAQ chart (19 September 2025 candlestick example, prices 24,800 / 24,825; fixed-profile example 24,318 to 24,317)
trades: 0 (illustrations only). Entry, stop, target: NOT STATED anywhere in this video.
```

## Rows (all SOURCED)
### R1 Aggressive buyers absorbed at a level, then breakout 
Buyers punch a horizontal level, are absorbed, sellers show little effort; he expects the next move to be a breakout (the call is made before the break).
> "What you can expect is that the next move will give you a breakout and this is a way to get anformational advantage over the price action traders."
**Source GPS: o-w5Gxss6T0 | BEGIN** (raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:46, raw line)

### R2 Volume-defined fair value gap (FAB-8; resolves the NOT_IN_DATA of SETUP_CATALOG FAB-8 item 7)
Price-action FVG is "typically wrong"; the real one needs the volume inside the candle. Method: fixed profile from swing point A to point B, 70 % value area, lowest-volume price inside it.
> "to identify a real fair value gap, you need to get inside the candle and you need to see how the volume transacted."
**Source GPS: o-w5Gxss6T0 | MIDDLE** (raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:60, raw line)

> "the lowest volume of interaction in all the area of value area. So where 70% of the volume got transacted is exactly this one is the level that goes from 24,318 to 24,317."
**Source GPS: o-w5Gxss6T0 | MIDDLE** (raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:74, raw line)

> "It's where the volume didn't transacted in a balanced way."
**Source GPS: o-w5Gxss6T0 | MIDDLE** (raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:81, raw line)

> "And what you will see thousand of times is that this is exactly where the price will reject."
**Source GPS: o-w5Gxss6T0 | MIDDLE** (raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:82, raw line)

Still NOT STATED: how the swing A/B is chosen, bin size, timeframe, entry order type, stop, target, how many times it has to hold. "thousand of times" is his claim; we have no count (OURS: untested here).

### R3 Failed auction confirmed by CVD absorption
CVD makes a lower low while price holds the same level: passive buyers absorb aggressive sellers; he reads it as a failed auction and a direction for the day.
> "we have a lower low on the cumulative volume delta here while the market is still on the same level as before. This is what it's called it's called absorption."
**Source GPS: o-w5Gxss6T0 | END** (raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:111, raw line)

> "there are passive buyers here that are absorbing all the aggressive sellers and the market is not willing to go down."
**Source GPS: o-w5Gxss6T0 | END** (raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:115, raw line)

### R4 Trend join: aggression after absorption, and the mismatch of delta and price
> "when you are in a momentum phase like this one and you can see a huge amount of aggression following an absorption, you can understand that the buyers are in control."
**Source GPS: o-w5Gxss6T0 | END** (raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:123, raw line)

> "So, it's a mismatch in price and volume."
**Source GPS: o-w5Gxss6T0 | END** (raw_transcripts_canonical/o-w5Gxss6T0_raw.txt:136, raw line)

## Verdict for the catalogue
- FAB-8 gets its verbatim definition (R2). BTC visibility stays YES (fixed profile from aggTrades). Entry, stop, target stay NOT STATED.
- FR-20 "trend-following entry: absorption of counter-trend aggression inside momentum" is now sourced to R4 (still no stop or target).
