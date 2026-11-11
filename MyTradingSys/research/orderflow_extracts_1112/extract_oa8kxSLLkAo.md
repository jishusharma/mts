# Order-flow extract: The ONLY Footprint-Trading-Video you will EVER need (`oa8kxSLLkAo`)

- **Video ID:** `oa8kxSLLkAo`
- **Analyst:** unknown (Trade the Traders channel)
- **Source:** `raw_transcripts_canonical/oa8kxSLLkAo_raw.txt` (on disk, no network; captions carry no timestamps, position = third of transcript)
- **Scope:** order-flow idea only (who is forced, where size trades, absorption, auction); index-futures clocks are not BTC rules (OPERATOR_DECISIONS 2026-11-12)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### R1. Unfinished auction at an extreme (SOURCED)

Rule: Volume on both bid and ask at the high or low means the auction is unfinished; price tends to revisit.

> "When there are high volumes at the tops or lows, the auctions are very often not yet finished, not yet completed."
**Source GPS: oa8kxSLLkAo | BEGIN**

### R2. Finished auction (SOURCED)

Rule: A one-sided extreme (zeros on the other side) means no more interest; the market is done there.

> "This means that up here, there was only one side of the price with a number greater than zero. And in such phases, you can simply say there was no more interest here."
**Source GPS: oa8kxSLLkAo | BEGIN**

### R3. Liquidity magnet (SOURCED)

Rule: Where size remains traded at an extreme, price tends to move back toward it.

> "But if, like down here, you still have a lot of numbers at the low, that means the market has liquidity in this price area, and where do markets generally tend to go? Towards liquidity."
**Source GPS: oa8kxSLLkAo | MIDDLE**

### R4. Rejection at finished top (SOURCED)

Rule: A finished auction at a pre-defined resistance (value area high) supports a limit short.

> "For me, that means a great opportunity to place a limit order here, and then initially enter a short trade accordingly."
**Source GPS: oa8kxSLLkAo | MIDDLE**

### R5. No counterparty (SOURCED)

Rule: Market orders pushed with no counterparty left shows exhaustion on that side.

> "The buyers pushed in a few more market orders here, but there simply was no counterparty left who was interested in participating."
**Source GPS: oa8kxSLLkAo | MIDDLE**

### R6. Retest of a heavy-volume zone (SOURCED)

Rule: Price returning to a zone where strong sellers traded big, then showing no interest, gives a short; the zone is where size was done.

> "Then we know that this large price area was initiated by very strong sellers and now no one is interested anymore."
**Source GPS: oa8kxSLLkAo | MIDDLE**

### R7. Low-volume moves return to balance (SOURCED)

Rule: Fast low-volume moves are driven to return to the equilibrium (comfort) zone.

> "Whenever there are rapid movements with low volume, these are initiated by larger buyers in order to return to a comfort zone."
**Source GPS: oa8kxSLLkAo | END**

## OURS (no quote)

- Footprint needs per-price bid/ask data; Binance public aggTrades can rebuild it for BTC, testable as 'unfinished auction at 15m high/low'. (OURS)

