# Order-flow extract: The BEST Trading Indicator? World Champions reveal the secret CVD Strategy (`y67l86cSqb8`)

- **Video ID:** `y67l86cSqb8`
- **Analyst:** unknown (Trade the Traders channel; index futures examples)
- **Source:** `raw_transcripts_canonical/y67l86cSqb8_raw.txt` (on disk, no network; captions carry no timestamps, position = third of transcript)
- **Scope:** order-flow idea only (who is forced, where size trades, absorption, auction); index-futures clocks are not BTC rules (OPERATOR_DECISIONS 2026-11-12)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### R1. Delta defined (SOURCED)

Rule: Delta per candle = buying actions minus selling actions; cumulative delta is the running sum.

> "Delta means the total accumulated buying actions minus the corresponding selling actions."
**Source GPS: y67l86cSqb8 | BEGIN**

### R2. Extreme is per-market (SOURCED)

Rule: What counts as an extreme delta must be calibrated per product; no universal threshold.

> "That means you can't standardize this for every market. You can't just use the same values everywhere. Instead, you need to know the specific metrics."
**Source GPS: y67l86cSqb8 | BEGIN**

### R3. Context needed (SOURCED)

Rule: Delta only matters at a prior technical level; a delta extreme mid-air is not information.

> "Because if I also have a strong technical level here, then I know there was an exhaustion here, which means an extremum."
**Source GPS: y67l86cSqb8 | MIDDLE**

### R4. Absorption (big passive buyer) (SOURCED)

Rule: Heavy selling that does not move price lower marks a large passive buyer absorbing sell orders; the level becomes a long-setup zone.

> "It means that there is a very large buyer here who is absorbing everything that's being sold. So, it's an absorption, a catching of all the sale orders."
**Source GPS: y67l86cSqb8 | MIDDLE**

### R5. Re-test of absorption level (SOURCED)

Rule: If price returns to the absorption level and the buyer is still there, long entry.

> "And if I see, aha, the buyer is still there and is interested in buying again in this price area, then I can easily enter a long trade here."
**Source GPS: y67l86cSqb8 | MIDDLE**

### R6. Trapped / failed side in a range (SOURCED)

Rule: In a range, an extreme build-up that fails to push price, then neutral delta while price falls, means the dominant side has a problem and must give up the position; breakout in the other direction likely.

> "That tells me this buyer, at some point they're going to have to give up their position here."
**Source GPS: y67l86cSqb8 | END**

### R7. Range break direction (SOURCED)

Rule: When no extreme buyers are present in a range, probability favours a drop.

> "what doesn't break out to the upside will break out to the downside."
**Source GPS: y67l86cSqb8 | END**

### R8. Trend continues until delta extreme (SOURCED)

Rule: A trend ends with a delta/volume extreme; no extreme means the trend continues, even then needs a second look.

> "If it doesn't get big, the probability is simply very high that the market will continue to fall."
**Source GPS: y67l86cSqb8 | END**

### R9. Selling pressure easing (SOURCED)

Rule: A smaller delta on the next down candle shows pressure easing.

> "That shows me the pressure is easing."
**Source GPS: y67l86cSqb8 | MIDDLE**

## OURS (no quote)

- Crypto mapping: use per-symbol rolling percentile of candle delta (not a fixed number) as the extreme test; to be backtested, not a rule. (OURS)

