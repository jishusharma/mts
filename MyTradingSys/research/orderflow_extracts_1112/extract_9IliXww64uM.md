# Order-flow extract: Fabio Valentini, S&P 500 futures session breakdown (`9IliXww64uM`)

- **Video ID:** `9IliXww64uM`
- **Analyst:** Fabio Valentini, single-speaker trade breakdown (S&P futures session)
- **Source:** `raw_transcripts_canonical/9IliXww64uM_raw.txt` (on disk, no network; position = third of transcript)
- **Scope:** order-flow idea only (who is forced, where size trades, absorption, auction); index-futures clocks are not BTC rules (OPERATOR_DECISIONS 2026-11-12)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### R1. Big trades filtered by size (SOURCED)

Rule: Order-flow bubbles are filtered by size so only large prints (the participants who move price) show; small prints are noise.

> "so we can filter out the noise and just see the big trades from big banks, from the smart money, the trades that actually matter"
**Source GPS: 9IliXww64uM | BEGIN**

### R2. Frame the day's path first (SOURCED)

Rule: Before any trigger, map where price is most likely to stay and the likely path of the auction, using volume profiles (composite profile over recent days plus the prior session profile).

> "what I want to see is where is most likely price is going to stay throughout the day, or what's the most likely path for the price and for the auction throughout the day"
**Source GPS: 9IliXww64uM | BEGIN**

### R3. Acceptance versus discovery (SOURCED)

Rule: A breakout candle alone is price discovery, not acceptance; acceptance needs a range to form outside the old value, so both sides treat the new prices as fair.

> "just the face of price discovery doesn't mean price acceptance"
**Source GPS: 9IliXww64uM | MIDDLE**

### R4. Qualify a breakout by waiting for a range (SOURCED)

Rule: A breakout is only qualified after a range forms outside the previous value area.

> "in order to qualify a breakout, I wait for a range to form"
**Source GPS: 9IliXww64uM | MIDDLE**

### R5. Start inside value means range expected (SOURCED)

Rule: When the session starts inside the previous value area with no news or discovery before it, expect to stay in that range and look for fades from its edges. The session-open timing is an index-futures clock (not a BTC rule); only the value-area idea is carried.

> "This is already a good sign that we're probably going to stay inside of this range for the rest of the day"
**Source GPS: 9IliXww64uM | MIDDLE**

### R6. Buyers absorbed at the range top (SOURCED)

Rule: Aggressive buying at the top of the value area that fails to make progress is absorbed by sellers, and price is pushed back down.

> "we had buyers genuinely trying to push the auction up and up and up, but they were absorbed by seller in all of this effort"
**Source GPS: 9IliXww64uM | MIDDLE**

### R7. Delta-price divergence trigger (SOURCED)

Rule: Negative delta (cumulative volume delta falling) while price rises is a divergence in pressure: effort without follow-through. Entry is taken at the close of the signal candle.

> "you have a negative delta with a positive price action. That's a very clear divergence in market pressure. There was an effort from seller that is not having any follow through"
**Source GPS: 9IliXww64uM | MIDDLE**

### R8. Order flow shows what price action does not (SOURCED)

Rule: The absorbed side is invisible on a price chart alone.

> "This stuff you cannot see it with price action, unfortunately"
**Source GPS: 9IliXww64uM | MIDDLE**

### R9. Reversal target is the other side of the range (SOURCED)

Rule: After an absorbed side is confirmed inside a range, the target is the opposite edge of the range, where the other side is likely to get aggressive.

> "And then I traded all the way to the other side of the range where sellers are likely to get aggressive"
**Source GPS: 9IliXww64uM | MIDDLE**

### R10. Failed breakout back inside (SOURCED)

Rule: A breakout with a lot of volume that is rejected and returns inside the range, with selling dominance inside, is a failed auction and a fade setup.

> "We had a very strong rejection with a lot of volume"
**Source GPS: 9IliXww64uM | END**

### R11. Continuation needs volume to persist (SOURCED)

Rule: A real breakout does not dry up in volume immediately after the break; continued volume with big trades inside the candles supports continuation.

> "What happens to the volume when we break out? Do we have a dry up in volume immediately? No. We have a lot of volume in this"
**Source GPS: 9IliXww64uM | END**

### R12. Exit before the opposite response zone (SOURCED)

Rule: Take profit before an area where the other side responded strongly (start of a strong impulse), because that is where control may change.

> "Well, because the beginning of a strong impulse happened here, and that's typically a very strong area for a buyer response"
**Source GPS: 9IliXww64uM | END**

### R13. Adapt to the flow, do not marry the analysis (SOURCED)

Rule: The plan changes when new flow information arrives; align with where the biggest flow of money is.

> "we don't need to marry an analysis. We need to adapt our idea as the market gives us new information, and we want to align ourselves where the biggest flow of money is"
**Source GPS: 9IliXww64uM | MIDDLE**

### R14. Join only when the flow invites (SOURCED)

Rule: Trade when the auction gives a setup; otherwise stay out.

> "I don't need to guess. Whenever they show me the invitation, I join or I choose to not join"
**Source GPS: 9IliXww64uM | END**

## OURS (no quote)

- Idea kept for BTC (OURS): absorption (large prints that do not move price) and failed-breakout fades can be tested on Binance aggTrades; the size filter must be per-symbol and per-regime (a rolling percentile of print size, not a fixed contract count). Not a rule until tested.
- DECISION (OURS): S&P session clocks (New York open, previous-session value area, 5-minute close entries) are not carried to BTC; only the value-area range-fade idea, untested. Account figures (session profit, track record) are anecdote, not adopted.
