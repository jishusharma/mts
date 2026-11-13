# Extract: Andrea Cimi, "The Only Orderflow Basics Video You'll Ever Need... maybe - Complete Beginner Course EP. 2" (`xR5-jm_KA9k`)

- **Video ID:** `xR5-jm_KA9k`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, free course EP2 "Complete Orderflow Trading Course", playlist PLBVwIU37953qr7DBLMJVXqcaVrJAaQy3D)
- **Market in the video:** CME index futures order book and footprint, drawn examples (6 contracts at the ask etc.); no crypto, no trading strategy.
- **Source:** `raw_transcripts_canonical/xR5-jm_KA9k_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### B1. Footprint: aggressive buys and sells per price level (SOURCED, definition)

Rule: per bar, per price level, record contracts bought at the ask (aggressive buyers, market buy lifts the ask) and sold at the bid (aggressive sellers). On Binance: aggTrades with isBuyerMaker false = buy at ask, true = sell at bid, bucketed by price tick. Stop and target: NOT stated (definition only).

> "The footprint is really cool because it tells us it gives us a very detailed information about aggressive buyers on this side and aggressive sellers on this side." [0:10:16]
**Source GPS: xR5-jm_KA9k | END**

### B2. Volume profile = ask plus bid per level (SOURCED, definition)

Rule: volume profile at each price level is bought-at-ask plus sold-at-bid, with no aggressor distinction.

> "volume profile, which very simply adds the contracts, makes an addition between sold at the bid and bought at the ask." [0:11:02]
**Source GPS: xR5-jm_KA9k | END**

### B3. Point of control (SOURCED, definition)

Rule: POC is the price level of the candle (or session) where the most contracts traded. No trading rule attached in this video.

> "This level is defined as the point of control, POC, which is the point of the candle where most contracts were traded." [0:11:42]
**Source GPS: xR5-jm_KA9k | END**

### B4. Delta profile = ask minus bid per level (SOURCED, definition)

Rule: delta profile at each price level is ask volume minus bid volume; it shows who was more aggressive at that level.

> "If instead of sum we make a difference between ask and bid, we will get the so-called delta profile." [0:11:52]
**Source GPS: xR5-jm_KA9k | END**

### B5. Aggressors move price; a large passive wall resists them (SOURCED, concept, partly computable)

Rule: price moves because aggressive orders accept worse prices; the speed of a move depends on the number of aggressors and on the passive liquidity in the way, and a big resting order is hard to break with similar aggressive volume. Binance aggTrades show only the aggressive side; the passive wall needs depth-stream snapshots (not in aggTrades/klines), so test only the proxy "large aggressive volume at a level without price progress" (OURS). Stop and target: NOT stated.

> "who moves the market, who moves the singular candle are aggressive liquidity." [0:09:21]
**Source GPS: xR5-jm_KA9k | END**

> "if there is a 100 or 1,000 contract order right here, if around the same volume of aggressive sellers try to hit this price and try to sell here, it's very hard for them to break that level." [0:09:39]
**Source GPS: xR5-jm_KA9k | END**

## Not computable from aggTrades/klines

| Item | Why |
|---|---|
| Order book / DOM / heat map liquidity zones | needs Binance depth stream history (not aggTrades or klines); no threshold given here |
| Market makers vs takers as "passive vs aggressive liquidity" | passive side only visible in book, not in trades |
