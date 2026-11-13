# Extract: Andrea Cimi, "The Only FOOTPRINT Chart Guide you'll Ever Need - Accelerated Orderflow Course" (`h4emw9_2LU8`)

- **Video ID:** `h4emw9_2LU8`
- **Speaker:** Andrea Cimi (DeepCharts co-founder, free course EP "Complete Orderflow Trading Course", playlist PLBVwIU37953qr7DBLMJVXqcaVrJAaQy3D)
- **Market in the video:** CME index futures (S&P 500 futures footprint, 1-minute and 5-minute bars, one worked session shown); no crypto. Concepts transfer, session clocks and contract sizes do not.
- **Source:** `raw_transcripts_canonical/h4emw9_2LU8_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Note:** CVD and bar-level delta rules are in `extract_Ni6quY00dcw.md` (not repeated here). No stop or target is stated anywhere in this video.

## Rules

### F1. Footprint = volume at bid and at ask per price level (SOURCED)

Rule: for each bar, split executed volume per price level into traded at the bid (aggressive sellers) and traded at the ask (aggressive buyers). Computable from Binance aggTrades (isBuyerMaker flag gives the side; price bins are OURS, not stated).

> "if we take all those contracts that has been executed and summarize them on the side of the candle this is a footprint chart" [0:02:58]
**Source GPS: h4emw9_2LU8 | BEGIN**

### F2. Diagonal imbalance, 2x and 4x (SOURCED)

Rule: compare the ask volume at one price level with the bid volume at the level one tick below (diagonal, because the best ask sits one tick above the best bid). Ask at least 2x the diagonal bid = buy imbalance (200 percent); at least 4x = strong (400 percent). Mirror for sell imbalance. Speaker says the 200/400 values "can also be optimized"; no other values given.

> "these 324 contracts are highlighted because they are at least four times bigger than 51 so imbalances are calculated diagonally" [0:04:36]
**Source GPS: h4emw9_2LU8 | MIDDLE**

> "if this number is at least two times bigger than this one it would be highlighted as a sell imbalance or if it's bigger more than four times of the counterpart it would be highlighted even more" [0:05:04]
**Source GPS: h4emw9_2LU8 | MIDDLE**

> "these numbers 200% 400% can also be optimized eventually" [0:05:28]
**Source GPS: h4emw9_2LU8 | MIDDLE**

### F3. Point of control shift (SOURCED)

Rule: POC = price level with the most traded volume inside the bar. A shift of the POC lower from one bar to the next is "the first signal of bearishness" (mirror for up). Only the first signal; no magnitude, stop or target stated.

> "in every candle there is a yellow box which is the level at which most contracts has been executed so a shift in the point of control where the point of control is here and then it's here is the first signal of bearishness" [0:04:18]
**Source GPS: h4emw9_2LU8 | BEGIN**

### F4. Unfinished auction (SOURCED)

Rule: a bar extreme where both bid and ask volume are non-zero at the last price level is an unfinished auction, and "there's a good chance" that level is revisited. A finished (normal) auction has zero on one side at the extreme. Probability not quantified (OURS: testable as touch-rate of the level within N bars).

> "usually in a normal auction you will find a zero here and a zero here so there's a zero here and a zero here" [0:05:35]
**Source GPS: h4emw9_2LU8 | MIDDLE**

> "usually when we have numbers in both we will call this an unfinished auction and there's a good chance that these level will be taken" [0:05:55]
**Source GPS: h4emw9_2LU8 | MIDDLE**

### F5. Delta per level and absorption (SOURCED)

Rule: delta at a price level = ask traded minus bid traded at that level. A level with a very large total volume (example 700 contracts) and strong one-sided delta is aggression and passive absorption at once. Absorption threshold NOT stated (this version of the indicator also folds in aggregate volume).

> "this color is determined by the relationship between the contracts traded here and the contract traded here this is called the Delta because it's the difference between these two" [0:06:10]
**Source GPS: h4emw9_2LU8 | MIDDLE**

> "these color means a strong level of aggression and absorption at the same time because 700 contracts were executed here" [0:06:29]
**Source GPS: h4emw9_2LU8 | MIDDLE**

### F6. Response and initiative (RNI) pattern (SOURCED)

Rule: at a highs area the sequence is an initiative phase up (aggression, imbalances, delta), then sell imbalances on top with exhaustion of buyers in the last levels, then an absorption/response phase where a retest of the level is absorbed, then an initiative phase down (imbalance burst, low volume, high aggression). Sell from the absorption area after the first imbalances. Mirror for lows. Entry, stop and target: NOT stated.

> "what often happens alltime highs is that there's going to be a huge phase of absorption here followed by a phase of initiative this is a pattern I love to use which is called the rni pattern or response and initiative pattern" [0:07:23]
**Source GPS: h4emw9_2LU8 | MIDDLE**

> "to First have a phase of initiative where we see a lot of aggression and imbalances and Delta once we reach the top we have cell imbalances on top" [0:07:39]
**Source GPS: h4emw9_2LU8 | MIDDLE**

> "this bar is full of aggressive buyers that tried to buy into this level but there was a seller front running all of that pressure absorbing all of those buyers" [0:08:30]
**Source GPS: h4emw9_2LU8 | MIDDLE**

### F7. Three imbalances in a row (stacked imbalance) (SOURCED)

Rule: three consecutive price levels with sell imbalance inside one bar is called "a really high probability" sell signal (the caption writes "cell"). Mirror for buy. Count of 3 is stated; win rate is not.

> "then three imbalances in a row which is a really high probability cell signal" [0:09:35]
**Source GPS: h4emw9_2LU8 | MIDDLE**

### F8. Imbalance cluster is an area that gets retested (SOURCED)

Rule: mark the price area of a stacked imbalance cluster (and the absorption level next to it); price comes back to tap it. Most reliable early in an impulse, "less and less likely" later in the impulse. Entry: after a confirmation, "enter one tick below" the cluster (as said for a short). Stop and target: NOT stated.

> "just use this as a confirmation for the entry and enter one tick below so we have our first imbalance cluster over here" [0:11:28]
**Source GPS: h4emw9_2LU8 | END**

> "every imbalance cluster or fail value Gap was exactly tapped in and retested every single time this is most common in the beginning part in the latter part of the impulse is less and less High likely to happen" [0:11:36]
**Source GPS: h4emw9_2LU8 | END**

### F9. Exhaustion of aggressive buying at the extreme, then new imbalances (SOURCED)

Rule: at a retest of a defended level, imbalance on top of the bar plus exhaustion of aggressive buying (volume falls at the last levels), followed by new imbalances, was followed by price down again. Exhaustion threshold NOT stated.

> "imbalance on top exhaustion in in aggressive buying new imbalances and we go down again" [0:12:58]
**Source GPS: h4emw9_2LU8 | END**

> "buyers try to tap back into that level and they get absorbed once more this is a clear sign that they are not willing to let price go back up" [0:13:21]
**Source GPS: h4emw9_2LU8 | END**

### F10. Fair value gap seen as low-volume imbalance zone (SOURCED)

Rule: after an initiative candle (many imbalances, low volume) the zone of low volume between the absorption level and where "fair value" is found again is the area to see filled; the absorption level is the other edge of the trade area. Precision claim only; no number.

> "the next candle is an initiative candle a lot of imbalances low volume and then we find for Value again" [0:10:06]
**Source GPS: h4emw9_2LU8 | END**

> "the fair value Gap is here because there's low volume and already here we started finding fair value so the part that I would like to see fill is actually this one" [0:10:20]
**Source GPS: h4emw9_2LU8 | END**

### F11. 5-minute bars for less noise (SOURCED parameter)

Rule: speaker sometimes reads the same footprint on 5-minute bars because it removes noise. Default timeframe in the example is 1 minute (OURS for BTC: untested).

> "this instead is the 5 minute version of the same chart and sometimes I like to use the 5 minute because it removes some of the noise" [0:07:09]
**Source GPS: h4emw9_2LU8 | MIDDLE**
