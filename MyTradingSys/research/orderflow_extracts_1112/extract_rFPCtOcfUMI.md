# Order-flow extract: Wall Street Scalper reveals: How to spot trend reversals BEFORE they happen (`rFPCtOcfUMI`)

- **Video ID:** `rFPCtOcfUMI`
- **Analyst:** unknown (Trade the Traders; Tom Vorwald with Serge Hoffmann)
- **Source:** `raw_transcripts_canonical/rFPCtOcfUMI_raw.txt` (on disk, no network; captions carry no timestamps, position = third of transcript)
- **Scope:** order-flow idea only (who is forced, where size trades, absorption, auction); index-futures clocks are not BTC rules (OPERATOR_DECISIONS 2026-11-12)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### R1. Absorption at a top (footprint) (SOURCED)

Rule: Very large traded volume at the high on the bid side with zero beside it, then price moving down, marks a passive absorber; reversal candidate.

> "We know that immediately that in this area a strong accumulation is taking place. And when we see all this then at this point a reversal could take place so to speak."
**Source GPS: rFPCtOcfUMI | BEGIN**

### R2. Who is absorbing (SOURCED)

Rule: Buying piled in at a top that stops moving price means a large passive seller took it all.

> "then you know that someone has absorbed everything that in the end was bought into the market."
**Source GPS: rFPCtOcfUMI | BEGIN**

### R3. Do not fade accepted prices (SOURCED)

Rule: Big trades at the top that also print on the other side mean prices are accepted and the auction is unfinished; be careful fading.

> "When you see a lot of big trades there, but those trades are also happening on your side, then you should be careful because that means there's strong demand."
**Source GPS: rFPCtOcfUMI | BEGIN**

### R4. Single print at the high (SOURCED)

Rule: A single print at the high that returns inside the prior value area is a reversal sign; supports value-area return idea.

> "a single print forms at the high and then moves back into the value area basically below the previous day's value area high and we see that a single print is formed at the top then that's also a good sign for a reversal."
**Source GPS: rFPCtOcfUMI | MIDDLE**

### R5. Aggressive side must show up (SOURCED)

Rule: A level becomes support or resistance only when aggressive trading happens there; a drawn line alone is nothing.

> "Support and resistance are based on active trading. That means only when something happens actively and aggressively there does support and resistance actually form."
**Source GPS: rFPCtOcfUMI | MIDDLE**

### R6. Slowdown plus aggressive sellers (SOURCED)

Rule: For a short at the top, need absorption, a slowdown, then aggressive sellers to the downside.

> "we should definitely see aggressive sellers to the downside showing up. It's important that there's aggressive selling because then, so to speak, a resistance has formed here"
**Source GPS: rFPCtOcfUMI | MIDDLE**

### R7. Delta divergence (SOURCED)

Rule: Price rising while cumulative delta falls is absorption; never trade the divergence alone, confirm with footprint or order book.

> "Never combine such a divergence based solely on cumulative data divergence. You can always confirm it, for example, with footprints or the order book."
**Source GPS: rFPCtOcfUMI | END**

### R8. Rejection vs absorption at the top (SOURCED)

Rule: No liquidity at the top is plain rejection; large absorption means someone is willing to sell there.

> "That's a simple rejection. They don't want to trade any higher."
**Source GPS: rFPCtOcfUMI | END**

### R9. Context first (SOURCED)

Rule: Entries need pre-planned levels; order flow is the trigger, not the location.

> "you need to have planned paths for where you enter trades and where those trades are headed and then trading is actually pretty cool"
**Source GPS: rFPCtOcfUMI | END**

## OURS (no quote)

- Crypto test: bid-side aggTrade volume spike in the top price bucket of a 5m candle with near-zero ask side, followed by a down close; needs fee-net OOS before use. (OURS)

