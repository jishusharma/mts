# Order-flow extract: World Champion reveals the Orderflow System that 95% of Traders do NOT know! (`usho6UVLqkE`)

- **Video ID:** `usho6UVLqkE`
- **Analyst:** unknown (Trade the Traders; Tom Vorwald)
- **Source:** `raw_transcripts_canonical/usho6UVLqkE_raw.txt` (on disk, no network; captions carry no timestamps, position = third of transcript)
- **Scope:** order-flow idea only (who is forced, where size trades, absorption, auction); index-futures clocks are not BTC rules (OPERATOR_DECISIONS 2026-11-12)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### R1. Order size is instrument-specific (SOURCED)

Rule: To read a book you must know what order sizes are normal for that instrument; scalping from the book needs those key figures per instrument.

> "you absolutely have to first get to know which key figures are actually necessary for the relevant instrument."
**Source GPS: usho6UVLqkE | BEGIN**

### R2. Low and high volume nodes (SOURCED)

Rule: Low-volume areas are where the market rushed through; high-volume nodes are acceptance and likely bounce points.

> "In those areas, the market simply had no interest in lingering and usually rushed through quickly."
**Source GPS: usho6UVLqkE | BEGIN**

### R3. Large resting order as magnet (SOURCED)

Rule: An order far larger than neighbouring levels signals someone with a reason; markets seek liquidity, so price likely travels there.

> "The probability is relatively high that the market will move there. Because markets are always looking for liquidity."
**Source GPS: usho6UVLqkE | MIDDLE**

### R4. Approach speed decides push-through or reversal (SOURCED)

Rule: Approaching a high-volume area: fast market orders into one side means it pushes through; slow routing then sudden larger counter orders means it reverses.

> "If you see that a lot of market orders are being routed very quickly into the sell side here, the probability is high that the market will push through at first."
**Source GPS: usho6UVLqkE | MIDDLE**

### R5. Front running the magnet (SOURCED)

Rule: Price keeps moving toward a big resting order and most likely bounces back at first, because traders expect a big fill that thin books do not give.

> "That means the market will keep trying to move toward this point because there's a big buyer there, and then most likely bounce back at first."
**Source GPS: usho6UVLqkE | MIDDLE**

### R6. Order eaten fast = real player (SOURCED)

Rule: If price rushes down, stays fast, eats the order, then below it speed drops and price reverses up at high speed, the buyer was a real big player.

> "then you know that this buyer here was really a big player who wants to drive the market upward."
**Source GPS: usho6UVLqkE | MIDDLE**

### R7. Large block executed then holds above (SOURCED)

Rule: After a large sell block is executed and price holds above it, the seller got his liquidity, so a pullback to fair price is likely.

> "The seller who dumped his positions in there is satisfied that he got his liquidity"
**Source GPS: usho6UVLqkE | END**

### R8. Absorption (SOURCED)

Rule: A buyer keeps hitting the same prices but price does not advance: a big seller absorbs everything.

> "we know that there is a big seller at this price level who simply absorbs everything that is being bought in the market."
**Source GPS: usho6UVLqkE | END**

### R9. Absorption then speed drop and larger counter orders (SOURCED)

Rule: When speed falls and the orders pushed into the bid get larger, price goes back down to predefined areas.

> "when the speed suddenly decreases and you see that the orders being pushed into the buy prices are getting larger, well, what do you think will happen? It's clear, the market will go down again"
**Source GPS: usho6UVLqkE | END**

### R10. Level then absorption then speed pick-up trigger (SOURCED)

Rule: Predefine a level from the prior profile; at it wait for absorption and then speed picking up on the other side as the trigger, with a distant target.

> "Now, all I have to do is wait for the moment when I see the speed picking up, more orders are being hit on the buy side and then, I know this is the point where my trade begins."
**Source GPS: usho6UVLqkE | END**

### R11. Missing liquidity test (SOURCED)

Rule: Price re-checks whether liquidity is still at a level; if not, it moves away and larger purchases confirm the reversal.

> "It checked if there was still liquidity there. No, there was no liquidity and then, it moved up here."
**Source GPS: usho6UVLqkE | END**

## OURS (no quote)

- Same family as wave 1 4P5WAxyPCis (front run, absorption, speed). The new point here is the two-way read of approach speed at a low-to-high volume boundary. (OURS)
- Book-dependent steps (resting size, executed block) need L2 history that public Binance data lacks; the speed and absorption half is testable with aggTrades. Numeric sizes (676, 712 contracts) are ES figures, not BTC parameters. (OURS)
