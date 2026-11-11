# Order-flow extract: Wall street scalper reveals the BEST scalping strategy in 2025 (`4P5WAxyPCis`)

- **Video ID:** `4P5WAxyPCis`
- **Analyst:** unknown (Trade the Traders; Serge Hoffmann ex-prop scalper)
- **Source:** `raw_transcripts_canonical/4P5WAxyPCis_raw.txt` (on disk, no network; captions carry no timestamps, position = third of transcript)
- **Scope:** order-flow idea only (who is forced, where size trades, absorption, auction); index-futures clocks are not BTC rules (OPERATOR_DECISIONS 2026-11-12)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### R1. Front running a big resting order (SOURCED)

Rule: A resting limit order about 10x the usual size per level moves price away at first; sit one or two ticks ahead with a tight stop below it.

> "And then it's just really nice to position yourself one or two ticks ahead of that position because at first the market always since many people and also algorithmic systems see that, the market usually moves away from it at first."
**Source GPS: 4P5WAxyPCis | BEGIN**

### R2. Applicability to crypto (SOURCED)

Rule: Front running still works in crypto, less in stocks; not for all assets.

> "in let's say in the crypto markets it still works very well, for example front running."
**Source GPS: 4P5WAxyPCis | BEGIN**

### R3. Hit and run (order about to be eaten) (SOURCED)

Rule: When aggressors push thousands of contracts into a big resting order and nothing refills it, the order gets eaten and a momentum move follows.

> "You hit into the order, you sell aggressively into the order and nothing gets added afterwards, so to speak. And if nothing gets added, then the order gets eaten up. And then there's a counter reaction, a momentum move to the downside."
**Source GPS: 4P5WAxyPCis | BEGIN**

### R4. Absorption scalp (SOURCED)

Rule: Far from VWAP, if tape speed slows while a passive seller soaks up buying, mean reversion back toward VWAP follows.

> "That means the market acts like a sponge. So the orders when someone buys are absorbed like a sponge."
**Source GPS: 4P5WAxyPCis | BEGIN**

### R5. Forced exit of the absorbed side (SOURCED)

Rule: Once the absorbed side cannot get through, they close aggressively and price flows the other way.

> "Then those who bought will start to aggressively close their positions."
**Source GPS: 4P5WAxyPCis | BEGIN**

### R6. Fast absorption does not hold (SOURCED)

Rule: Absorption seen at stable high speed is likely to fail; absorption with slowing speed and no aggressive buyers at the level is the tradable one.

> "if you see absorption happening at a very high speed, and you can see that it's being absorbed again and again and the speed is stable in that sense, then the probability is very high that the absorption won't hold."
**Source GPS: 4P5WAxyPCis | BEGIN**

### R7. Trend: low-volume nodes (SOURCED)

Rule: In a trend, repeated low-volume areas are pullback entries when activity between buyers and sellers disappears there.

> "when the market moves up or down and repeatedly, so to speak, low areas, meaning low volume areas are created, then it's actually a very good very good opportunity to join the trend"
**Source GPS: 4P5WAxyPCis | MIDDLE**

### R8. Balance edge acceptance (SOURCED)

Rule: At a balance-area edge, slow trading means participants refuse those prices and price returns to the high-volume area; fast active trading means acceptance and a breakout.

> "if you notice that there's not much trading happening at the lower edge or it's happening very slowly, then the probability is very high that market participants are not willing to accept lower prices."
**Source GPS: 4P5WAxyPCis | MIDDLE**

### R9. Four components (SOURCED)

Rule: Time, price, volume and speed together.

> "if you take these four components, then you have a very, very, very big advantage over others"
**Source GPS: 4P5WAxyPCis | END**

## OURS (no quote)

- Needs L2 order book history (not in public Binance archive); only the aggTrade speed half is testable on public data. (OURS)

