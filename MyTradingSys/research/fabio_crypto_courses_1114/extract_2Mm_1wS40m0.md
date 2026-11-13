# Extract: Andrea Cimi, "banks don't hunt for your stop loss... here's how it ACTUALLY works" (`2Mm_1wS40m0`)

- **Video ID:** `2Mm_1wS40m0`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, free course EP "Complete Orderflow Trading Course")
- **Market in the video:** CME E-mini S&P 500 (ES) futures footprint and heat map; no crypto. Concepts transfer, session clocks and MBO data do not.
- **Source:** `raw_transcripts_canonical/2Mm_1wS40m0_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### M1. Stop run footprint: ask side much heavier, candle delta at least 25 percent (SOURCED)

Rule: stops execute as market orders at the best available price and sweep the book; in a low-liquidity moment the bar shows zeros on the far side and delta at least 25 percent. Real example ES 29 April about 4 a.m.: delta almost above 40 percent. Thresholds 25 and 40 percent are the speaker's own (OURS: untested, no study count). Computable on BTC from aggTrades per bar. Stop and target: NOT stated.

> "the ask side of the footprint is going to be way more voluptuous than the bid part of the footprint and since ask lifted minus bid hit is our Delta the Delta of this candle is going to be really high at least above 25%" [0:10:18]
**Source GPS: 2Mm_1wS40m0 | MIDDLE**

> "the Delta of the candle is really high almost above 40%" [0:11:42]
**Source GPS: 2Mm_1wS40m0 | MIDDLE**

### M2. Stop run is purely aggressive orders in one direction; balanced candles are not stop runs (SOURCED)

Rule: a bar with strong aggression but heavy trade on the other side too (large opposite volume) is a fight between large participants, not stops. Balanced delta bars (2 percent and 5 percent in his example) mean no stop run even if a low was broken. Computable: abs(delta percent) small = no stop run. Stop and target: NOT stated.

> "a stop run is purely stops being triggered and hitting the bid or hitting the as" [0:14:26]
**Source GPS: 2Mm_1wS40m0 | END**

> "this other move down which was allegedly taking stops below here which were very few has a 2% and 5% Delta which means that they are really balanced candles also on the aggression side of things" [0:14:38]
**Source GPS: 2Mm_1wS40m0 | END**

### M3. After a stop run price tends to refill the swept zone, then maybe inverts (his estimate) (SOURCED)

Rule: after the burst the path of least resistance is back into the swept levels (the book repopulates); he cites a 60 to 70 percent chance, from his own 2 years of pattern study, but immediately says the chance is 'not that high' and that sometimes the aggression wins and the market keeps going. Probability is the speaker's own claim, no data shown (SOURCED as a claim, OURS untested). Stop and target: NOT stated.

> "the first thing that will happen is that price is going to go through the path of list resistance and get back feeling this level" [0:10:54]
**Source GPS: 2Mm_1wS40m0 | MIDDLE**

> "while there is a 60 to 70% chance that this will happen the chance of this happening are actually not that high and trust me I've been studying this pattern for the last 2 years" [0:11:04]
**Source GPS: 2Mm_1wS40m0 | MIDDLE**

> "we reabsorb the candle and then maybe we can invert but sometimes these aggressions will win" [0:11:16]
**Source GPS: 2Mm_1wS40m0 | MIDDLE**

### M4. The swept liquidity is passive limit orders; stops are the aggressor (SOURCED)

Rule: definition for a stop-run detector: stops are market orders that consume resting limit orders; measure the aggressor-side volume that cleared the levels beyond the extreme. Binance aggTrades give the aggressor side and size per trade but not the resting book (no heat map), so the book side is not observable.

> "so actually the liquidity sweep it's not a sweep of stop- loss because stop- loss are the ones which are sweeping the book so in a stop run the liquidity which is being swept or sweeped is sell limits" [0:08:55]
**Source GPS: 2Mm_1wS40m0 | MIDDLE**

> "buy stops are Market orders and they will be executed at the best possible price where there is at least one contract as a counterparty" [0:08:09]
**Source GPS: 2Mm_1wS40m0 | MIDDLE**

### M5. Confirm a stop run with tape speed and market-by-order data (SOURCED)

Rule: his stop-run indicator confirms stop orders with tape speed and MBO data. Tape speed is computable from aggTrades (trades or volume per second); MBO is not available on Binance public data. Thresholds NOT stated.

> "tell us with even more accuracy and Confirmation by using tape speed and MBO data if those were actually stop orders" [0:13:01]
**Source GPS: 2Mm_1wS40m0 | MIDDLE**

### M6. Iceberg absorption: huge volume at a single price level (SOURCED)

Rule: a level with abnormal volume (26,000 plus 699 plus about 1,200 contracts at one price in the ES example) is an iceberg order and absorption by a large participant, not retail stops. Computable on BTC: per-price-level volume outliers in the footprint. No volume threshold, entry, stop or target stated; direction implied by the side absorbing (here a sell iceberg blocking buyers).

> "there is 26,000 contracts plus 699 plus 1. 2,000 contracts all executed at one level this is what we call an iceberg order" [0:15:16]
**Source GPS: 2Mm_1wS40m0 | END**

> "this was one of the big players in this market that was trying to block all the buyers" [0:15:44]
**Source GPS: 2Mm_1wS40m0 | END**

### M7. Large total volume beyond a level means a fight, not stop hunting (SOURCED)

Rule: volume beyond a swept low is always two-sided (every contract has a buyer and a seller); 50,000 ES contracts below a low is a war between big participants, so high volume below the level argues against a pure stop run. Threshold is example-only (OURS to calibrate). Stop and target: NOT stated.

> "below here 50,000 contracts were executed which means 50,000 sell contracts but also 50,000 buy contracts because every single one of the contracts that you see here are contracts being exchanged" [0:13:40]
**Source GPS: 2Mm_1wS40m0 | END**

### M8. Context numbers he reports: retail share and concentration (not tradeable) (SOURCED)

Rule: SOURCED numbers from the speaker: retail about 5 percent of daily volume; more than 40 percent of E-mini shorts held by eight or fewer participants (his COT reading); one claimed 15,000 stops produced only 2.4 thousand contracts at the level. Context only, no trading rule, not computable from Binance.

> "retail trading activity only accounts for 5% of the total daily volume" [0:01:29]
**Source GPS: 2Mm_1wS40m0 | BEGIN**

> "more than 40% of the shorts are held by eight or less participants" [0:16:43]
**Source GPS: 2Mm_1wS40m0 | END**

> "only 2.4k contracts were executed here" [0:19:31]
**Source GPS: 2Mm_1wS40m0 | END**
