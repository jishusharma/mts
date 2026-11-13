# Extract: Andrea Cimi, "I Analyzed 1.000 "Stop Hunts" with Orderflow... Here's What I Found Out" (`3MID2HLZS30`)

- **Video ID:** `3MID2HLZS30`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, free course EP "Complete Orderflow Trading Course")
- **Market in the video:** CME E-mini S&P 500 (ES) futures footprint and heat map; no crypto. Concepts transfer, session clocks and MBO data do not.
- **Source:** `raw_transcripts_canonical/3MID2HLZS30_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### S1. A stop run is one-sided aggressive market orders through the extreme (SOURCED)

Rule: stops are market orders, so a stop run through a low shows as a burst of aggressive sells hitting the bid below the low (and through a high, aggressive buys lifting the ask). Test on BTC: aggressor-side volume per price level beyond the prior swing extreme, in a fast move. Threshold, stop and target: NOT stated (the next rule gives delta percent).

> "stop orders are very specific they are sell order hitting the bid so all of the orders here in the purple part are aggressive selling order so if this magnitude of aggressive selling happens below a low we can deduce it's an actual stop run" [0:08:38]
**Source GPS: 3MID2HLZS30 | MIDDLE**

> "it's called a run because the moves happens really fast" [0:08:55]
**Source GPS: 3MID2HLZS30 | END**

### S2. Footprint signature: empty opposite side and delta above 50 percent (SOURCED)

Rule: the stop-run candle has almost no trades on the far side of the bar (zero cells in the footprint), and candle delta percent is far above 50. His example numbers are single ES candles, not a study. Threshold 50 percent is the speaker's own reading of one example (OURS: untested). Stop and target: NOT stated.

> "you can realize that there was a Sprint in this candle because there's zero contract and zero contracts all over here" [0:01:15]
**Source GPS: 3MID2HLZS30 | BEGIN**

> "in fact the Delta is way above 50% and there is a lot of volumes this this is an actual stop run" [0:09:38]
**Source GPS: 3MID2HLZS30 | END**

### S3. Sweep without aggression is a failed auction, not a stop run (what NOT to call a stop run) (SOURCED)

Rule: a low or high sweep with few imbalances and little delta is a failed auction (the pushing side lacks strength; new aggressive opposite side enters). Do not treat every sweep of a swing extreme as a stop run. Computable: sweep bars with low absolute delta percent and low aggressor imbalance. Direction after: opposite side takes over in his examples (no count given). Stop and target: NOT stated.

> "there's not a lot of imbalances not a lot of Delta then once we go below those lows once again there's a little bit of a selling activity but very few so this is not a stop run per se" [0:01:37]
**Source GPS: 3MID2HLZS30 | BEGIN**

> "this is what we called a failed auction so sellers trying to break below but not having enough strength to push it lower and lower instead new aggressive buyers start skiing in" [0:01:48]
**Source GPS: 3MID2HLZS30 | BEGIN**

### S4. A breakout with a delta of only 14 percent is not a stop run (SOURCED)

Rule: above a daily high the candle showed a delta of 14 with plenty of aggressive selling inside the bar, so it was judged not to be a stop run: a pure stop run bar would be very green with a much higher delta. A bar with 10 percent delta is also called 'not a lot'. Delta percent below roughly 10 to 14 = not a stop run (his reading of single candles, OURS as a threshold).

> "once we break above here the Delta is 14 so this is not a stop run because there's a lot of aggressive selling activity in this area if it was just stops we would have seen a very green candle above here in all this part and hence a much higher Delta" [0:02:45]
**Source GPS: 3MID2HLZS30 | BEGIN**

> "there's a lot of buying on this candle this is 10% Delta this is not a lot" [0:11:10]
**Source GPS: 3MID2HLZS30 | END**

### S5. After a genuine stop run the move continues after re-absorbing the imbalance (SOURCED)

Rule: after a stop run price does not necessarily reverse: market makers absorb the burst as passive counterparties and the move can keep going. Qualitative, no percentage given. Stop and target: NOT stated.

> "when stops hit they ask they raise up price and Market maker are absorbing all of that buy inertia by being passive Sellers" [0:01:07]
**Source GPS: 3MID2HLZS30 | BEGIN**

> "we don't go down right away and invert for the rest of the session we just simply reabsorb this quick imbalance created by the stop run and then we keep moving higher" [0:02:28]
**Source GPS: 3MID2HLZS30 | BEGIN**

### S6. Volume beyond the swept extreme is tiny; the real liquidity is the high-volume area (SOURCED)

Rule: volume traded above a swept high or below a swept low is small (e.g. 2,000 and about a thousand contracts on ES) compared with the volume inside the range, so a wick beyond the extreme cannot be what fuels the next move. Computable: volume beyond the extreme divided by session or range volume from aggTrades. No threshold given (OURS to measure).

> "there must be a lot of volume right 2,000 contracts breadcrumbs okay very very few contracts a couple of stops being executed here but nothing worth hunting" [0:06:00]
**Source GPS: 3MID2HLZS30 | MIDDLE**

> "the real liquidity was exchanged here not above this High not below these lows but here because in all of this area a lot of volume has been exchanged" [0:06:36]
**Source GPS: 3MID2HLZS30 | MIDDLE**

### S7. Real liquidity grab = extended time and volume spent beyond prior lows (accumulation or distribution) (SOURCED)

Rule: the move that matters is a whole phase of trading below several lows (volume consolidates there), not the single sweep wick. Computable: share of session volume traded beyond the prior swing lows and time spent there. No threshold, stop or target stated.

> "the more time price spends below a low or below more lows the more liquidity they are grabbing all of the session is consolidating below those lows then it's an actual liquidity grab" [0:12:08]
**Source GPS: 3MID2HLZS30 | END**

### S8. Last candle of the CME session is high-volume passive absorption, not a stop run (SOURCED)

Rule: a very high volume, balanced-delta bar at the end of the cash session (53,000 contracts in his example) is market-maker absorption and index-fund flow, not a stop run. CME session clock: no direct BTC equivalent (24/7 market; any daily-close analogue is OURS and untested).

> "the last candle of the session is when all the day trading algorithm exit the market where a lot of hedge funds or long-term funds like ETFs are buying the underlying asset because they're required to do it by law" [0:07:25]
**Source GPS: 3MID2HLZS30 | MIDDLE**

> "so this is not a stop run this is a huge absorption of contracts in every part" [0:07:49]
**Source GPS: 3MID2HLZS30 | MIDDLE**

### S9. His own count: few sweeps were real stop runs (no number reported in the video) (SOURCED)

Rule: title says 1,000 stop hunts analysed, but the caption states no count and no percentage; the only statement is qualitative: few sweeps were actual stop runs or liquidity grabs, and he says the pattern still has an edge. He also says qualifying needs market-by-order data, which Binance aggTrades does not have (aggressor side and size only).

> "all of the rest we have seen in the previous example really few of them were actual stop runs or actual liquidity grabs" [0:09:45]
**Source GPS: 3MID2HLZS30 | END**

> "yes this pattern has an edge but calling it stop hunting or liquidity grabbing if you look at actual volume most of the times it doesn't make sense" [0:08:02]
**Source GPS: 3MID2HLZS30 | MIDDLE**

> "we would need MB data to qualify it" [0:04:36]
**Source GPS: 3MID2HLZS30 | MIDDLE**
