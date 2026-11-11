# Order-flow extract: THE TRUTH about Heatmap & Liquidity - This is how the World Champion REALLY trades! (`Vd83oo_geMk`)

- **Video ID:** `Vd83oo_geMk`
- **Analyst:** unknown (Trade the Traders; Tom Vorwald)
- **Source:** `raw_transcripts_canonical/Vd83oo_geMk_raw.txt` (on disk, no network; captions carry no timestamps, position = third of transcript)
- **Scope:** order-flow idea only (who is forced, where size trades, absorption, auction); index-futures clocks are not BTC rules (OPERATOR_DECISIONS 2026-11-12)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### R1. Order book over heat map (SOURCED)

Rule: The book shows where liquidity was and is; the heat map adds nothing the book does not, and the source prefers the book.

> "the order books are the true market. And if I want to look for indications, if I want to see where liquidity was and where liquidity is, I don't need a heat map for that."
**Source GPS: Vd83oo_geMk | BEGIN**

### R2. Big is relative to the market (SOURCED)

Rule: An order is only large relative to that market's normal size; know the threshold per instrument (ES figure is index-futures, not a BTC rule).

> "But honestly, if you don't really know the market and for example, you don't know that in the SNP500, that is in the ES future, an order needs to be over 250 or 300 contracts isolated and on its own for you to be able to judge that it's truly large."
**Source GPS: Vd83oo_geMk | BEGIN**

### R3. Heat map hides how the block was executed (SOURCED)

Rule: A past block order on a heat map does not show whether it was filled in large or small chunks, fast or slow, so not who was aggressive.

> "you have no idea how they were executed. Were they filled in large chunks, in small chunks, at high speed, at low speed?"
**Source GPS: Vd83oo_geMk | BEGIN**

### R4. Who has the upper hand (SOURCED)

Rule: Dominance shows in whether more trades into bid or ask, the speed, and the reaction to large orders.

> "I can see that simply by observing whether more is being traded into the bid or the ask, what speed underlies the whole thing, and what reactions I get to corresponding large orders."
**Source GPS: Vd83oo_geMk | MIDDLE**

### R5. Environment decides (SOURCED)

Rule: A market seeks liquidity, but the useful question is what environment we are in and who is moving toward it.

> "it is true that a market seeks liquidity. But the question and this is very important is what kind of environment are we currently in."
**Source GPS: Vd83oo_geMk | MIDDLE**

### R6. Small players only (SOURCED)

Rule: A move that repairs a single print and drops below value without acceleration is small-player activity, not big-money.

> "I can tell you right now only the small players are active. There is absolutely no big game going on here so far."
**Source GPS: Vd83oo_geMk | MIDDLE**

### R7. Do not trade into big orders expecting them to be eaten (SOURCED)

Rule: Repeatedly buying toward a visible liquidity pool and getting stopped out is the classic loss; the market takes that liquidity later.

> "what happens if you're someone who constantly tries to trade in the direction of the large orders. you just get totally crushed if you think that these orders absolutely have to be eaten up."
**Source GPS: Vd83oo_geMk | MIDDLE**

### R8. Averaging into a range-crash sequence (SOURCED)

Rule: Building a position in every new range during a crash ends in a heavy drawdown if you cannot tell which participants are active.

> "and eventually there's a big crash and the account takes a heavy draw down."
**Source GPS: Vd83oo_geMk | END**

### R9. Iceberg (SOURCED)

Rule: Repeated large routing into one price with little change is an iceberg: more orders keep stacking.

> "you know, yes, that's an iceberg order. they just keep stacking up more orders there."
**Source GPS: Vd83oo_geMk | END**

### R10. Heat map is not an edge (SOURCED)

Rule: A heat map is fine for scanning many markets but not a way to build an edge; that needs context.

> "in my opinion, it's not a good way to build an edge. For that, you simply need to understand more context."
**Source GPS: Vd83oo_geMk | END**

## OURS (no quote)

- Public Binance data has no resting-order history; the heat-map half cannot be tested. Iceberg and speed can only be proxied from aggTrades (repeated same-size prints at one price, taker-delta without price progress). (OURS)
- Do not treat visible liquidity as a target by itself: test liquidity-pool touches only with a who-is-active context (volume-spike / acceleration filter), not unconditionally. (OURS)
