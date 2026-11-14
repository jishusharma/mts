# Extract: Andrea Cimi, "How Banks Hide their Orders Behind Price: a Guide on Icebergs" (`WPAP7JaVzF4`)

- **Video ID:** `WPAP7JaVzF4`
- **Speaker:** Andrea Cimi (DeepCharts co-founder; iceberg pattern shown on ES, 19 April 2024 example)
- **Market in the video:** CME E-mini S&P 500 footprint, London/Asian vs New York session; no crypto. Speaker states he did not give all the answers ("you have to do a part of the homework").
- **Source:** `raw_transcripts_canonical/WPAP7JaVzF4_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### I1. Spot an iceberg from the footprint (SOURCED, trigger)

Rule: a candle where a huge volume prints at one level (the candle's POC) and delta is large, yet that level does not break: big aggression, no price result. Computable from aggTrades footprint per tick (volume at one price, delta, break/no-break of the level); the size threshold is NOT stated (examples: 223 contracts executed, later 1,000 at the level; indicator minimum cluster 300 contracts, said to be too low for the New York session). Threshold for BTC is OURS and must be scaled to the session volume.

> "a level not being broken the the P the pock of the candle so the majority of the volume there a huge Delta on the candle which represents a huge aggression without any result in price action" [0:07:50]
**Source GPS: WPAP7JaVzF4 | MIDDLE**

> "indicator is set on a minimum cluster of volume of 400 of 300 contracts but 300 contracts as a threshold for the New York session is not close to be enough" [0:11:32]
**Source GPS: WPAP7JaVzF4 | END**

### I2. First edge: fade the iceberg, repeatedly (SOURCED, entry)

Rule: sell into the iceberg level (a hidden big sell limit) with a stop above it, aiming for a couple of ticks, and repeat for every bounce price makes off that level. Stop distance and exact target: NOT stated beyond "stop above" and "a couple ticks"; "a lot of times icebergs are going to fail". Mirror for a buy iceberg is implied, not stated (OURS).

> "the very first Edge that we can actually use to make money and trade this is by actually selling it with a stop above to get a couple ticks" [0:06:07]
**Source GPS: WPAP7JaVzF4 | MIDDLE**

> "the first Edge is to sell it for as many times as price can Bounce from there" [0:09:14]
**Source GPS: WPAP7JaVzF4 | END**

### I3. Second edge: trade the break of the iceberg (SOURCED, entry)

Rule: when the level finally breaks, trade the breakout in the break direction; speaker claims it works "a good 60 70% of the time" (his own number, no study shown, treat as untested). A break came with unprecedented size at the level and then a near-zero-volume next candle (liquidity void). Stop and target: NOT stated.

> "the second Edge you can try to find is when the iceberg gets broken you can eventually trade the breakout which happens a good 60 70% of the time" [0:09:18]
**Source GPS: WPAP7JaVzF4 | END**

> "1,000 contracts was never seen in in any one of the candles before" [0:08:51]
**Source GPS: WPAP7JaVzF4 | MIDDLE**

### I4. Session filter: edge is in low-liquidity sessions (SOURCED, filter)

Rule: the pattern matters mainly in the Asian/London session, where a big order at one level is an anomaly; in the New York cash session 2,000 contracts per level are eaten in milliseconds, so thresholds must be raised or the setup skipped. Frequency stated: about once or twice a month on ES. For BTC (24h, no cash session) the equivalent low-liquidity window is OURS and untested.

> "that's why it has an edge mainly in the London session" [0:09:49]
**Source GPS: WPAP7JaVzF4 | END**

> "it's so easy to execute 2,000 contracts per level during the New York session" [0:10:01]
**Source GPS: WPAP7JaVzF4 | END**

## Not computable (needs CME MBO / book)

| Item | Why |
|---|---|
| Iceberg reload seen as the book repeatedly refilling 20 contracts at the same level | needs book snapshots or MBO; Binance aggTrades show only executed trades |
| Iceberg indicator with alert (DeepCharts) | proprietary tool, no formula given |
| Same operator trading with itself, rollover, "banks hide orders" narrative | explanation, no rule |
