# Extract: Deep Charts, "The Hidden Order Banks Use to Move the Market - And How to See It" (`aukc_NLGmxo`)

- **Video ID:** `aukc_NLGmxo`
- **Speaker:** DeepCharts presenter (not named in the caption); iceberg-order detection on CME ES/NQ with market-by-order (MBO) data and a heat map (DeepDOM); two trades by a community trader ("Rodulfo") are replayed
- **Market in the video:** CME ES and NASDAQ futures with an MBO (order by order) feed; no crypto. Binance public data has NO order-by-order feed, so the iceberg indicator itself cannot be rebuilt; only the trade logic around it can be tested on a proxy.
- **Source:** `raw_transcripts_canonical/aukc_NLGmxo_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Not repeated here (same as finished extracts):** absorption as aggression met by passive size = `extract_h4emw9_2LU8.md` F5; response/initiative logic = F6 there; value area edge tests = `extract_KObUowoFiK0.md` K8.
- **Stop placement:** NOT stated for the initial stop in either example; only break-even and trailing are described. Entry price rule: NOT stated beyond "searching for a trigger".

## Rules

### I1. Iceberg = small visible order that keeps reloading (SOURCED)

Rule: a big participant hides size by showing a small order (example 8 contracts) that refills each time it is hit. Observable signature: a lot of aggressive volume hits a level with a tiny displayed size and the level does not break. Needs order-by-order data (MBO) to see the reload; with aggregate trades only, the proxy is "large aggressive volume at one level without price breaking through" (OURS, untested). Win rate after the signal: NOT stated.

> "And when a seller is going to come and eat this eight contract level, it's going to appear again a new contract level of eight contracts." [0:05:55]
**Source GPS: aukc_NLGmxo | BEGIN**

> "So maybe you start seeing a lot of sellers pushing and pushing and pushing against a little level of eight contracts. Doesn't make sense." [0:06:40]
**Source GPS: aukc_NLGmxo | MIDDLE**

> "You can start seeing market by order by order each level of price." [0:07:38]
**Source GPS: aukc_NLGmxo | MIDDLE**

### I2. Detection filter: larger minimum size, fewer but more important icebergs (SOURCED)

Rule: the indicator has a minimum and a maximum iceberg size. A lower minimum shows more absorptions but smaller and less important; a higher minimum shows fewer, more important orders. His setting in the cash session: 300 contracts (ES); 150 before the cash session, 30 only to demonstrate. BTC sizes: OURS, untested.

> "Obviously, if you get a minimum filter lower, you are going to see more iceberg, more absorptions, but they are going to be less big and less important." [0:09:11]
**Source GPS: aukc_NLGmxo | MIDDLE**

> "I normally like to put 300, but we are not yet in the cash session." [0:09:29]
**Source GPS: aukc_NLGmxo | MIDDLE**

### I3. Trade 1: long at the value area low of a new value area in an uptrend, iceberg as trigger (SOURCED)

Rule: context = bullish trend, price accepting higher prices and building a new small value area (a swing volume profile). Setup = price reaches the value area low of that new value area. Trigger = repeated icebergs absorbing sell pressure at that level (also on a second test, plus another iceberg higher up). Entry on the trigger. First target = the value area high, or beyond. Initial stop: NOT stated.

> "The first thing that we see is that we are in a bullish trend." [0:13:36]
**Source GPS: aukc_NLGmxo | END**

> "Rodulfo after seeing that the market reaches the the value area low of this little new value area in an uptrend it start thinks that is a good zone to try to buy" [0:14:00]
**Source GPS: aukc_NLGmxo | END**

> "at least until the other side of the value area sold to the value area high or even breaking and going further." [0:14:11]
**Source GPS: aukc_NLGmxo | END**

> "When Rulfo sees all the smart money activity, he enters the market searching for a movement up at least to the valuary high." [0:14:49]
**Source GPS: aukc_NLGmxo | END**

### I4. Trade management: break-even, then trail below supporting liquidity (SOURCED)

Rule: after entry the stop goes to break-even and the trade runs toward the last big level of persistent liquidity above; on consolidation the stop is trailed below the level that supports price; on a new push to the high the stop is trailed again, and the trade ends stopped out in profit. Trail distance: NOT stated. Layered persistent resting orders above price are described as "a good magnet for the price" (needs order-book history; speaker claim, no data shown).

> "So he put himself to break even and let the market run a little bit further searching for the last big level of persistent liquidity." [0:15:10]
**Source GPS: aukc_NLGmxo | END**

> "So he decides to trail his stop loss below this level that is supporting the price." [0:15:26]
**Source GPS: aukc_NLGmxo | END**

> "But he's also seeing that in the heat map he has these levels of persistent liquidity in layering. So one above the other one that can be a good magnet for the price." [0:14:59]
**Source GPS: aukc_NLGmxo | END**

### I5. Trade 2: re-entry into the value area after a failed break, partial at the value area high, exit on fresh sell liquidity (SOURCED)

Rule: price ranges in a fair value area; heavy selling pushes out and reaches a persistent liquidity level, then falls back into the value area (a failed auction / failed break). Iceberg absorbs the selling, he engages. Half is closed in the low volume area at the value area high of the first fair value area; the remainder is run toward the POC, with the stop trailed as price nears it and trailed aggressively when about five points from the target; the trade is closed when a big fresh sell liquidity level appears. Exit by liquidity needs depth history (partly computable with Binance depth snapshots, OURS). Stop initial: NOT stated.

> "What you are not seeing is that there's a huge big market participant putting a lot of iceberg orders to absorb all this pressure." [0:17:15]
**Source GPS: aukc_NLGmxo | END**

> "So he engaged the market and after closing half of his position in the low volume area and the value area high of this first fair value area he let a partial run searching for the P." [0:17:48]
**Source GPS: aukc_NLGmxo | END**

> "When the market start reaching the nearest of the PC, he trail his stop loss to secure some profits." [0:18:01]
**Source GPS: aukc_NLGmxo | END**

> "And when he sees a big new fresh level of sell liquidity, he decides to close his trade" [0:18:15]
**Source GPS: aukc_NLGmxo | END**

### I6. Book flip and spoof-like loading as read of intent (SOURCED)

Rule: a "book flip" = a big resting level on the book is eaten and a big level re-appears on the same tick on the other side; read as support for a move in the flip direction. Many big levels added and deleted at high frequency while price ranges = orders "pressing the market to stay down", so going long into it is not easy. Both need order-book event data; Binance depth stream would only give a coarse proxy (OURS). No stop/target, no sample.

> "This is another pattern where you see a big level being eated and again a big level on the same tick being reload on the other side. This should support a movement up." [0:13:11]
**Source GPS: aukc_NLGmxo | END**

> "When you see this type of behavior, it's not easy to see the market going up because these type of orders are pressing the market to stay down." [0:16:55]
**Source GPS: aukc_NLGmxo | END**
