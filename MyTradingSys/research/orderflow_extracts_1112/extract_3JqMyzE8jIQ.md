# Order-flow extract: The ONLY Fair-Value-Gap-Video you will EVER need (Trading World Champion reveals) (`3JqMyzE8jIQ`)

- **Video ID:** `3JqMyzE8jIQ`
- **Analyst:** unknown (Trade the Traders; Tom Vorwald)
- **Source:** `raw_transcripts_canonical/3JqMyzE8jIQ_raw.txt` (on disk, no network; captions carry no timestamps, position = third of transcript)
- **Scope:** order-flow idea only (who is forced, where size trades, absorption, auction); index-futures clocks are not BTC rules (OPERATOR_DECISIONS 2026-11-12)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### R1. Gaps are unfair auctions (SOURCED)

Rule: A price gap is an area with no fair auction: one side was completely dominant, so participants want to check whether fair business can still happen there.

> "There was no fair auction there between buyers and sellers. One side was completely dominant."
**Source GPS: 3JqMyzE8jIQ | BEGIN**

### R2. Three outcomes at a gap (SOURCED)

Rule: At a gap there are three scenarios: counter-trade idea, exit point only, or a range forming; a reaction is usually a range, not a quick reversal.

> "But the reaction is not a quick counterrading move. Instead, a range forms there, and that's exactly what you need to distinguish."
**Source GPS: 3JqMyzE8jIQ | BEGIN**

### R3. Not every gap fills (SOURCED)

Rule: Retail assumes every gap will eventually close; that is the common mistake.

> "Retail traders think that pretty much every gap will eventually be closed."
**Source GPS: 3JqMyzE8jIQ | BEGIN**

### R4. Fast trend leaves single prints (SOURCED)

Rule: A fast trend that never pulled back leaves a single-print area (space): price the market left open.

> "The market never made a pullback from here upwards. And that's why we call this price area a fast trend. And the market profiler sees a single print area here."
**Source GPS: 3JqMyzE8jIQ | BEGIN**

### R5. Gap entry needs a target first (SOURCED)

Rule: A gap is not an entry trigger alone; first know the next target area and the realistic hit rate, otherwise reward-to-risk is unknown.

> "I can't just use this fair value gap as an entry trigger. I also need to know where is the probability high that the market will move back there."
**Source GPS: 3JqMyzE8jIQ | MIDDLE**

### R6. Unfair price revisits, but fair price first (SOURCED)

Rule: Unfair prices are likely revisited, but price usually returns first to the next fair-price (value) area.

> "The probability that a market will revisit an unfair price level is quite high. But first, it will usually return to the next fair price area."
**Source GPS: 3JqMyzE8jIQ | MIDDLE**

### R7. Same setup, different reward to risk (SOURCED)

Rule: The same counter-trade has a far worse reward-to-risk if the structure is a balance with only one target, so structure at the gap matters more than the gap.

> "Then all of a sudden, if I know how markets work, I only have one target left up here. And suddenly my riskreward ratio is only 1 one."
**Source GPS: 3JqMyzE8jIQ | MIDDLE**

### R8. Breakeven hit rate at 1:1 (SOURCED)

Rule: At 1:1 reward-to-risk a trade needs at least 51 percent hit rate before fees to break even.

> "If we had a riskreward ratio of 1: one, you would need at least 51% without order fees just to break even."
**Source GPS: 3JqMyzE8jIQ | MIDDLE**

### R9. Open drive and buying tail give no support (SOURCED)

Rule: A level created by an open drive with a strong buying tail will not offer support when retested; exit there rather than counter-trade (index-futures example, not a BTC rule).

> "if I know the rules of market profiling, then I know that this was simply an open drive here and the market just gave me a strong buying tail at this point and that really won't offer any support for me."
**Source GPS: 3JqMyzE8jIQ | END**

### R10. Where volume actually traded is the support (SOURCED)

Rule: When price leaves an area with no trading, it drops to the next area where real volume traded.

> "it will simply drop down to the next price area where real volume took place"
**Source GPS: 3JqMyzE8jIQ | END**

### R11. Footprint for stop placement (SOURCED)

Rule: Footprint charts help place stops tighter, which improves reward-to-risk.

> "footprint charts are a great tool to make the whole process much more targeted with regard to protecting your capital."
**Source GPS: 3JqMyzE8jIQ | END**

## OURS (no quote)

- Gap = unfinished auction maps to the unfinished-auction rule in wave 1; a candle-only three-bar gap detector is not claimed by the source as a stand-alone edge. (OURS)
- Testable on public data: gap fill rate conditional on whether a value area or single print sits between the gap and the target (daily/4h BTC bars), reward-to-risk measured, not assumed. (OURS)
