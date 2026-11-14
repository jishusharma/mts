# Extract: Andrea Cimi, "The Indicator Banks ACTUALLY Use - Full Guide to VWAP" (`R5L890juvRw`)

- **Video ID:** `R5L890juvRw`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, free course EP "Complete Orderflow Trading Course")
- **Market in the video:** CME index futures (ES, NQ) session charts with VWAP and standard-deviation bands; no crypto. Concepts transfer, session clocks do not.
- **Source:** `raw_transcripts_canonical/R5L890juvRw_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### V1. VWAP definition and per-session reset (SOURCED)

Rule: VWAP = volume weighted average price, a moving average weighted by traded volume, recalculated continuously and reset at the start of each session. Computable on BTC from klines or aggTrades; the BTC session boundary (e.g. 00:00 UTC, or 8h funding blocks) is OURS and untested.

> "vwap stands for volume weighted average price it's basically a moving average that doesn't consider only price in its formula but also includes trading volume" [0:01:09]
**Source GPS: R5L890juvRw | BEGIN**

> "this line is being reset as soon as every single session starts again so with every new session this is being reset because it's a reference for the session" [0:06:21]
**Source GPS: R5L890juvRw | MIDDLE**

### V2. Premium and discount defined by VWAP side (SOURCED)

Rule: price below the session VWAP is discount and above is premium; institutions try to fill longs below the daily or weekly VWAP and shorts above it. Filter (OURS): longs only below VWAP, shorts only above, untested. Stop and target: NOT stated.

> "everything that sits below the vwap is Discount related to the volume weighted average price of the session" [0:03:07]
**Source GPS: R5L890juvRw | BEGIN**

> "a lot of times the reference for these trades as a discounted pricing or a discounted value will be whatever is below the daily vwap or the weekly vwap" [0:04:57]
**Source GPS: R5L890juvRw | MIDDLE**

### V3. VWAP standard-deviation bands at 1, 1.5, 2 and 3 (SOURCED)

Rule: bands plotted at 1, 1.5, 2 and 3 standard deviations around VWAP; he usually keeps 2. Parameter SOURCED as his usual setting, no test behind it. Computable (volume-weighted standard deviation of price, reset per session).

> "the first standard deviation is one the second here is 1.5 standard deviation usually I just keep it at two which is the third and even the third standard deviation" [0:07:34]
**Source GPS: R5L890juvRw | END**

### V4. Mean reversion to VWAP: outer bands raise bounce probability, VWAP is the target (SOURCED)

Rule: the further price travels from VWAP and the more time it spends in outer bands, the higher the chance of a bounce back toward VWAP; reversal strategies use the outer bands as overbought or oversold and the central VWAP as target for rebalancing. No probability given, he tells the viewer to back-test. Stop: NOT stated. Target: central VWAP (SOURCED).

> "the more prices go outside and reaches for example the higher bends the higher the chance there will be some level of reversal" [0:05:43]
**Source GPS: R5L890juvRw | MIDDLE**

> "the more we trade in the outer bands the higher is the probability that at least we are going going to see a bounce back to the fair value" [0:07:53]
**Source GPS: R5L890juvRw | END**

> "use the central vwap as a target for Price rebalancing" [0:09:20]
**Source GPS: R5L890juvRw | END**

### V5. Long idea: wait for the first or second band, then break and test, targets at outer bands (SOURCED)

Rule: for a long idea at the session open: wait until price has reached at least the first, better the second standard deviation, then after it broke and retested try the long; second and third band as targets. The caption wording is ambiguous on which level is broken and retested (OURS: reading unclear). Stop: NOT stated.

> "you might want to wait until the price has gone at least to the first if not the second standard deviation" [0:08:49]
**Source GPS: R5L890juvRw | END**

> "after we broke it and tested it we can try our long trade this can be one of the ways to use it and you can use the second and third standard deviation as a Target" [0:09:02]
**Source GPS: R5L890juvRw | END**

### V6. VWAP and bands as support and resistance (SOURCED)

Rule: price often reacts at VWAP and the first and second bands as dynamic support or resistance; after breaking and retesting, first band gives a little resistance, the second more. Reaction frequency: NOT given, he says to back-test for the actual edge.

> "often it will give a reaction and act as support or resistance" [0:06:46]
**Source GPS: R5L890juvRw | MIDDLE**

> "of course you might want to back test test it a lot and see for yourself the actual edge of the average" [0:07:26]
**Source GPS: R5L890juvRw | END**

### V7. What NOT to do: VWAP alone, and fading in strong trends (SOURCED)

Rule: VWAP does not always work; in high-momentum strong trends price keeps buying at premium levels, so a VWAP trade needs context from the trading idea and must not rely on VWAP alone. Trend filter threshold: NOT stated (OURS).

> "vwap is not always working it's always needed to have a context behind your trading idea you're not just going to trade based off of vwap only" [0:08:31]
**Source GPS: R5L890juvRw | END**

> "there is moments with high momentum and once we've established a strong Trend where still markets will keep buying even at higher and premium prices" [0:08:21]
**Source GPS: R5L890juvRw | END**

### V8. Value area is the 70 percent volume zone (SOURCED)

Rule: value area (fair value area) of a volume profile = zone holding about 70 percent of session volume, a convention set for convenience (SOURCED); computable from klines or aggTrades volume-by-price. How to trade it: NOT stated in this video.

> "what is highlighted also known as the value area or the fair value area is none other than a standard deviation Trader at some point decided to put this at 70% to make things easier" [0:02:23]
**Source GPS: R5L890juvRw | BEGIN**
