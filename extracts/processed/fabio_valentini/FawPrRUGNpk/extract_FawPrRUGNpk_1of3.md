# Extract FawPrRUGNpk chunk 1 of 3 (lines 1-401)

### FAB-FawPrRUGNpk-R1: Guessed retail liquidity is unreliable
- Rule: Do not treat above-high/below-low (compression) or above/below swing (trend) as liquidity without heat-map confirmation; the guess is only 60-70% accurate.
- Topic: zones
> "So, retail is usually seen as resting above the high and below the low in a compression phase"
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R2: Heat map intensity = level importance
- Rule: A brighter/darker heat-map level (more resting contracts) is a stronger liquidity level than dim levels.
- Topic: zones
> "you have the darker level or the level it's more powerful from a visual perspective"
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R3: Path of least resistance (5 levels)
- Rule: Sum passive limit orders over the five price levels above and below price; price is biased toward the side with the smaller total (273 above vs 122 below = down).
- Topic: proof
> "So, fixing the effort, it's easier to move price down in this particular behavior."
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R4: Rising liquidity lifts the path of least resistance
- Rule: If passive liquidity on a side repeatedly grows (raised, raised again), treat that side as the blocked direction and price as likely to bounce between heat-map levels.
- Topic: proof
> "here that the liquidity raised and raised again going on. So it means that they are lifting, okay, the path of least resistance."
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R5: Bid reload in compression
- Rule: In a consolidation/compression phase, a new large bid (e.g. 110 contracts) appearing supports a long idea; expect price to go directly to that level (front-running).
- Topic: entry
> "will try to front run it. So there is a big probability that you will go directly to this level."
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R6: Spoofing caution on bid reload
- Rule: Treat a bid-reload appearing without being traded into as possible spoofing; do not rely on it alone.
- Topic: risk
> "Be careful also because this pattern here it's used a lot by the spoofing"
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R7: Iceberg = hidden reloading
- Rule: A level showing few contracts that keeps being refilled as it is consumed is an iceberg (needs an iceberg indicator); treat it as much larger than displayed.
- Topic: zones
> "There are only eight contract here, but every time sellers step in and consume it, they get reloaded."
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R8: Book sweep location
- Rule: Book-sweep (fast movement) setups occur near all-time high/low, range extremes, or the New York session high.
- Topic: session
> "this one you can find really close to all-time high, all-time low of the range."
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R9: Book sweep asymmetric risk
- Rule: When positioned at a book sweep, risk only a few ticks for a large reward multiple.
- Topic: risk
> "you can take an asymmetrical risk to reward. You can risk few ticks to get a really good risk to reward multiplier."
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R10: Book flip management
- Rule: In a short, when the level breaks and liquidity is reloaded on the downside (door closes above), trail the stop or add contracts.
- Topic: management
> "covered here, you can trail your stop loss here or you can also add other contract"
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R11: Buyers reload absorption sequence
- Rule: A resting (not fresh) bid wall that absorbs repeated strikes (three times) supports mean-reversion long in the main-trend direction.
- Topic: proof
> "market approach here and get absorbed the first time, strike again this area, absorb the second time"
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R12: Scalper aggression confirmation
- Rule: Before entering a reload trade, require visible aggression (big trades) in the trade direction.
- Topic: proof
> "So you want to see maybe big trades confirming that there is an aggression there"
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R13: Reload breakout entry and stop
- Rule: With a directional bias, enter long at the breakout with the stop below the reload level.
- Topic: entry
> "you can enter at the breakout protected below the reload level"
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R14: Reload targets
- Rule: Take TP1 at the major liquidity area, TP2 and TP3 at further resting liquidity areas.
- Topic: target
> "you can run the setups with the first take profit on the major liquidity areas"
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R15: Directional bias prerequisite
- Rule: Take reload setups only with a directional bias/probability framework derived from order flow.
- Topic: other
> "you need to start with a directional bias and a probability framework that comes from the order flow."
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R16: Sellers reload confirmation
- Rule: Short confirmation = sellers aggressive while simultaneously reloading fresh passive liquidity at the level.
- Topic: proof
> "they get aggressive and at the same time they reload fresh liquidity."
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R17: Target is next liquidity cluster
- Rule: Target the next liquidity cluster; if it is very close, the risk-to-reward is poor.
- Topic: target
> "the price usually goes to the next liquidity cluster."
**Source GPS: FawPrRUGNpk | BEGIN**

### FAB-FawPrRUGNpk-R18: Stop below next liquidity area
- Rule: With a long bias, place the stop below the next liquidity area (not just below the low) to survive a spike during accumulation.
- Topic: stop
> "you could decide to enter here, yes, but to put your stop loss below the next liquidity area."
**Source GPS: FawPrRUGNpk | BEGIN**

## Unclear
- "Path of least resistance" in trend terms: number of levels (5) given only in an example; no threshold ratio.
- Fill mechanics (passive vs aggressive, lines 87-152): explanatory, no trading rule.
- "Reload plus absorption" entry trigger: no exact criteria for absorption count or size.
- What qualifies as "big trades" or a "major" liquidity area: no thresholds.
- Bias sources (IVB, statistical pivot, volume profile, VWAP) named but not defined.
