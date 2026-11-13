# Extract: Andrea Cimi with Fabio Valentini, "I Traded AGAIN with a PRO Scalper" (`agjftXPkLUE`)

- **Video ID:** `agjftXPkLUE`
- **Speaker:** Fabio Valentini (live trading, NASDAQ futures, DeepCharts platform) with host Andrea Cimi; 25 minutes, published 2025-10-01
- **Market in the video:** CME NASDAQ (NQ) futures, one live session (cash open), contracts of 2 to 6; no crypto. Concepts transfer, session clocks, option/gamma data and contract sizes do not.
- **Source:** `raw_transcripts_canonical/agjftXPkLUE_raw.txt` (caption via public transcript site, stored on F:\MTS\data_cache\youtube\fabio\)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote
- **Caption note:** the caption mishears words (the session "PFC" is a point of control, "whipso" is a whipsaw, "view app" elsewhere is VWAP); read by context. Prices and stops are named only once (invalidation 24,782); per-trade stop distances are NOT stated.
- **Not repeated here:** day-profit-as-risk and dynamic sizing are the same as `extract_cLgdXZnLL_0.md` D1, D6, D9, D12; scale-out, break-even, runner is the same as `extract_kYX05qESJMs.md` S6. Only the new wording and numbers below.

## Rules

### A1. Daily loss cap and daily profit cap, then stop (SOURCED)

Rule: both caps are 8,000 dollars; reaching either ends the day. He says the profit cap was reached only 3 or 4 times in 20 trading days. Applied: the session ended at 7,883 after four take-profits and one stop-loss. Cap size is account-specific (OURS: scale to BTC account). Computable as a rule on any trade list (yes); stop and target per trade NOT stated here.

> "The maximum stop loss for the day it's $8,000 and the maximum profit to stop for the day it's $8,000." [0:01:45]
**Source GPS: agjftXPkLUE | BEGIN**

> "So either we go in loss or in profit we will stop the $8,000 stop in 20 days of trading. I only reach three or four days." [0:01:55]
**Source GPS: agjftXPkLUE | BEGIN**

### A2. Same size every trade; never raise size to recover; grow only with realised profit (SOURCED)

Rule: base size 2 contracts, kept constant ("not scaling up"); one trade was upsized to 5 then 6 contracts only because he called it a premium setup (grade criteria NOT stated); size and the day's cap grow only after a profit threshold is banked. Never raise exposure after a loss. Risk is funded by the profit of the day.

> "now the secret guys is to never get greedy. Never risk everything. Never raise exposure to recover. Always the same size two contract." [0:13:42]
**Source GPS: agjftXPkLUE | MIDDLE**

> "Let's say that we load in the risk management five contract. Now let's do six because it's a really premium setup." [0:04:55]
**Source GPS: agjftXPkLUE | BEGIN**

> "Still the same exposure, not scaling up. Still two contracts and we build one contract here, one contract here and one contract here" [0:08:04]
**Source GPS: agjftXPkLUE | MIDDLE**

> "We are only using the starting profit of the session. In this case, we are not uh heavy in risk." [0:06:13]
**Source GPS: agjftXPkLUE | BEGIN**

> "we didn't risk a single scent because we are still only risking the profit of the day" [0:13:37]
**Source GPS: agjftXPkLUE | MIDDLE**

> "What we have is always the approach to build profit for the day. Build profit and stop when we are going in draw down." [0:02:26]
**Source GPS: agjftXPkLUE | BEGIN**

### A3. Compression day: scale size with the session, cap the best session (SOURCED)

Rule: on a range or compression day he starts small and scales size as the session proves itself, and he deliberately caps a good session because trend-following trades give the profit back inside a range. Day-type classifier (what makes a "compression" or "breakout" day) is NOT stated beyond the profile and the volume reading (see A9).

> "it's a compression day. So, we will go uh we will scale a little bit the size with the session going on." [0:01:38]
**Source GPS: agjftXPkLUE | BEGIN**

> "Yes, I put a cap to the best session because today we are in consolidation." [0:05:17]
**Source GPS: agjftXPkLUE | BEGIN**

> "I cannot be greedy because otherwise all my trend following trades will go back" [0:05:32]
**Source GPS: agjftXPkLUE | BEGIN**

### A4. Trade 1: position building at the zone where sellers were absorbed (SOURCED)

Rule: build small positions as price approaches the level where the sellers were absorbed the most (the spike up); the stop is the invalidation price of that zone (24,782 in the example, not a computed distance); the target is a small fixed profit (about 500 dollars on this small position). After the first target, remove the other longs, because if the auction fails price probably revisits the level. Zone detection computable (footprint absorption at a level: yes); stop = invalidation level of the absorbing zone; distance in ticks NOT stated.

> "All our position have an invalidation point that is 24,782 and position are built as soon as the price gets close to this level because that's where the sellers got absorbed the most" [0:02:39]
**Source GPS: agjftXPkLUE | BEGIN**

> "This one was not a precise shot was a position building. That's the reason I got really low on the sides." [0:02:32]
**Source GPS: agjftXPkLUE | BEGIN**

> "We are going for $500 in profit with this one." [0:02:21]
**Source GPS: agjftXPkLUE | BEGIN**

> "I remove immediately the other position long because if we go down I don't want to be long again because if this auction fail it's probably that we will revisit this level." [0:02:53]
**Source GPS: agjftXPkLUE | BEGIN**

### A5. Trade 2: cash-open momentum scalp from the buyers' cluster (SOURCED)

Rule: at the cash open, long from the cluster of aggressive buyers toward the top of the opening range; if the top breaks it becomes a momentum trade; the stop sits below the first aggression inside the candle ("exit is on the low"); three orders were entered; the target is the top of the range, taken as soon as price reaches it; trail the stops (order 1, order 2) and put the third at break-even within about 20 seconds ("risk free"). Continue holding only while the buyers still pay higher prices. Computable on BTC: yes (cluster of buying delta in the opening bar, swing low of that bar, range high). The opening-bar definition is session based (OURS for BTC: untested).

> "Yes. This is the cluster of the buyers. So, we can start to capitalize on the way up and get the momentum till the the top of the range." [0:03:15]
**Source GPS: agjftXPkLUE | BEGIN**

> "If they break through this level, this is a momentum trade. So, you are getting protected below the first aggression inside the candle." [0:03:23]
**Source GPS: agjftXPkLUE | BEGIN**

> "Your exit for these trades is on the low. One, two, and three. And you want to be out as take profit as soon as the market reach the top." [0:03:38]
**Source GPS: agjftXPkLUE | BEGIN**

> "We are going to trail this stop loss one, stop loss two, stop loss at zero for this one." [0:03:54]
**Source GPS: agjftXPkLUE | BEGIN**

> "This is really quick scalp. This is what you can do at the beginning of the session." [0:04:04]
**Source GPS: agjftXPkLUE | BEGIN**

> "Consider it that in 20 seconds we were risk-f free on this too." [0:04:07]
**Source GPS: agjftXPkLUE | BEGIN**

> "these buyers are still auctioning and they are willing to pay a higher price on this. So the probabilities are that we will continue up." [0:04:13]
**Source GPS: agjftXPkLUE | BEGIN**

### A6. Take-profit placement: a little before the session point of control (SOURCED)

Rule: inside a consolidation, take the trade out a little before the session POC (the caption says "PFC"), not at it. The size of "a little" is NOT stated (OURS: unknown, test 0 to 3 ticks of BTC tick). Computable: yes (session volume profile from aggTrades or klines).

> "you can go to the PFC of the session that is this one. So, you want to take out the trade a little bit before." [0:04:36]
**Source GPS: agjftXPkLUE | BEGIN**

### A7. Cover under big trades; get out if they are absorbed (SOURCED)

Rule: keep the stop just under (for longs) the cluster of big trades that carries the trade; if big trades get absorbed or the level is breached, exit; losing the cover without reason is the error. The big-trade filter he watches is 30 contracts on NQ (see A9; threshold OURS for BTC).

> "We should cover ourself under these big trades because otherwise the market if destroy them we lose a lot of money without a reason." [0:08:52]
**Source GPS: agjftXPkLUE | MIDDLE**

> "So it's better to be out if they absorb everything." [0:09:00]
**Source GPS: agjftXPkLUE | MIDDLE**

> "I want to be out if this level does not hold because we will reach this one here." [0:22:59]
**Source GPS: agjftXPkLUE | END**

### A8. Break-even, then stop in profit, then bank profit (SOURCED)

Rule: stops go to break-even when a named level is breached or the position is "risk free"; once a rejection (spike and reversal) shows he moves the stop into profit, not only to zero; when a big gain is floating he books part ("another 4,000") and places the stop below the aggressive buyers or below the gap; after the candle closes in line with the auction ("coherent with the results") he books again. Re-entry is allowed because taking profit cannot bust the account. Exact trigger distance NOT stated; same management idea as `extract_cLgdXZnLL_0.md` D9 and `extract_kYX05qESJMs.md` S6, new here: the explicit "stop to profit" after a rejection spike and the booking rule.

> "Remember guys that if we breach through this level, we go break even." [0:06:54]
**Source GPS: agjftXPkLUE | BEGIN**

> "We are going risk free. 1 2 3 risk free. 8,000 profit potential if they breach through this level." [0:14:30]
**Source GPS: agjftXPkLUE | MIDDLE**

> "If I get a spike here and the rejection, I can think about putting stop loss to profit, not only to zero." [0:16:09]
**Source GPS: agjftXPkLUE | END**

> "If we get this high, we can trail everything here. We secure secure another $4,000 for the day." [0:19:19]
**Source GPS: agjftXPkLUE | END**

> "So what I want to do is just let's recover this one and let's put the stop loss below this long aggression." [0:20:51]
**Source GPS: agjftXPkLUE | END**

> "Now, if this one gets recovered and the candle close, so the auction is coherent with the results, why not taking another $2,000 cover below the the delta" [0:21:37]
**Source GPS: agjftXPkLUE | END**

> "You cannot go bust by taking profit. This is a rule guys. You can never lose money by taking profit." [0:21:19]
**Source GPS: agjftXPkLUE | END**

### A9. Context panel: profile, big trades filtered at 30, option volume (SOURCED)

Rule: three read-outs give the day bias: the volume profile (where price sits in the distribution and whether value is building above the previous day), big trades filtered at 30 contracts (the "bubbles") and option volume direction; he trades long when all three read long. The option read (gamma, option volume) has no Binance equivalent. Profile and big-trade filter computable from aggTrades (yes); the filter value 30 is for NQ, OURS for BTC.

> "This one is for the profile. So it gives you context. Where are you? We are in the upper part of the distribution." [0:09:36]
**Source GPS: agjftXPkLUE | MIDDLE**

> "I want to see if we are building value above the previous day. We are not doing this successfully." [0:09:49]
**Source GPS: agjftXPkLUE | MIDDLE**

> "This is for interaction of borders. So I'm watching big trades filter by 30." [0:09:54]
**Source GPS: agjftXPkLUE | MIDDLE**

> "The volume are seeing that is long. The profile is seeing that is long. The big trades are seeing that is longer." [0:15:28]
**Source GPS: agjftXPkLUE | MIDDLE**

### A10. Failed auction, whipsaw and stop hunt: where he builds after sellers get trapped (SOURCED)

Rule: a failed auction with aggressive sellers confirms the long; he accepts a stop-out if the level is breached; he looks for a whipsaw (break, immediate failure) at a low and builds positions on the lows where aggressive sell gets absorbed ("happy to be liquidated" there); a sweep of stop losses (here 1,249 contracts liquidated) is read as a stop hunt, after which the best setup is a long covered below the hunt low. Computable (partly: sweep of a prior low then reclaim, delta absorbed at the low; the contract counts come from the platform liquidation feed, not aggTrades; Binance has a separate forced-liquidation stream, OURS to check).

> "This one was confirmed by this failed auction with aggressive sellers. If they breach through this level, I'm happy to take a stop loss." [0:17:52]
**Source GPS: agjftXPkLUE | END**

> "I want to see a whipso here. Whipso is when you see a f. It's probably a fail." [0:17:02]
**Source GPS: agjftXPkLUE | END**

> "we want to be liquidated and we are happy to be liquidated. If we go below this low just where it's more smart to build position we absorb we are absorbing the aggressive sell." [0:17:30]
**Source GPS: agjftXPkLUE | END**

> "we clearly swept some stop losses. That's why we're falling down." [0:16:47]
**Source GPS: agjftXPkLUE | END**

> "But still, still still this is the best setup if they get the high because I can cover myself below this." [0:11:27]
**Source GPS: agjftXPkLUE | MIDDLE**

> "I think that they didn't got the high. So, it's still it's not they got absorbed by passive orders." [0:15:15]
**Source GPS: agjftXPkLUE | MIDDLE**

### A11. Reading the battle at a level: sellers protect, buyers pay up, stacked orders (SOURCED)

Rule: at a level, buyers paying higher prices while sellers defend means a stacked battle; aggressive sellers at the top of a range that cannot push price down mean absorption, so the range top is not broken yet; the read is done zoomed in. Computable: partly (stacked imbalance at consecutive levels and delta at the level are computable; "willing to pay higher" is the rising bid-side print price).

> "Sellers are protecting from here. Buyers are willing to pay a higher price. These are stacked orders." [0:07:22]
**Source GPS: agjftXPkLUE | MIDDLE**

> "Sellers are aggressive at the top. This is something meaningful. It means that they are willing to pay a higher price to bridge to the level." [0:07:00]
**Source GPS: agjftXPkLUE | BEGIN**

### A12. Range compression and chart unit: scalp the top and bottom of the range; not 1 minute at the open (SOURCED)

Rule: in a range, price sells the top and buys the bottom, so trades are taken at the range edges; at the session open do not use a 1-minute bar because one candle then holds too much volume (volume-based or smaller units are implied). Computable: bars of N trades or N seconds from aggTrades (yes).

> "When it's like this, the market are selling the top and buying the B. So they are compressing." [0:10:21]
**Source GPS: agjftXPkLUE | MIDDLE**

> "1 minute is too small as a time frame to do session open because it's so volatile that you will have too much volume in one candle" [0:13:04]
**Source GPS: agjftXPkLUE | MIDDLE**

### A13. Exit when the auction is not confirmed; stop trading when the regime flips to range-bound (SOURCED)

Rule: hold only while price confirms; exit when it does not. At the end he stopped because the market returned to range-bound with positive gamma and the delta was falling, so extra trades risked the day's profit. Gamma has no Binance equivalent (OURS: use realised range expansion or falling delta as a proxy, untested). Session result as claimed (no trade list shown): 4 take-profits and 1 stop-loss, 7,883 dollars, maximum drawdown 1,000, so profit skew over loss is his point; single session, in-sample, unverified.

> "Follow the price till it confirm what it's going to say. Exit when it's not confirmed. Positive gamma. The delta is getting lower." [0:23:57]
**Source GPS: agjftXPkLUE | END**

> "Didn't risk anything else than uh profit getting back range bound with positive gamma. It's not uh worth to continue to trade." [0:23:15]
**Source GPS: agjftXPkLUE | END**

> "they took us out 8,000 7,883 for the day. Four take profit, one stop loss." [0:23:08]
**Source GPS: agjftXPkLUE | END**

> "That is maximum draw down $1,000, $7,000 profit." [0:23:40]
**Source GPS: agjftXPkLUE | END**

### A14. Big trades filtered by size are clearer than the footprint (SOURCED)

Rule: he trades from bubbles that show only large trades (a size filter) because filtering by quantity is clearer than raw footprint numbers. Computable on BTC: yes (aggTrades with quantity above a threshold; threshold OURS, scale by BTC volume).

> "With the bubbles, you can see the aggressive buyers and sellers that matters. This is better than the footprint." [0:18:19]
**Source GPS: agjftXPkLUE | END**

> "That's the reason with time I understood that filtering by quantity of orders is way more clear." [0:18:26]
**Source GPS: agjftXPkLUE | END**

## Trade log (OURS reading of the transcript; no quote lines)

| # | Setup | Direction | Trigger as stated | Stop | Target | Size |
|---|---|---|---|---|---|---|
| 1 | Position building at absorbed-seller zone (A4) | long | price close to the zone where sellers were absorbed most | invalidation 24,782 | about 500 dollars | small, 2 contracts |
| 2 | Cash-open momentum scalp (A5) | long | cluster of buyers at the open, momentum if the level breaks | below the first aggression in the candle | top of the range | 3 orders |
| 3 | Rebuy after hunt at lows (A10) | long | failed auction with aggressive sellers, whipsaw | NOT stated (the lows) | NOT stated | 2 to 6 contracts |
| 4 | Squeeze on the high of the day (A8) | long | squeeze at the day high, positions risk free | break-even then in profit | high of day, scaled out | 4 orders |
| 5 | Final trail (A8) | long | auction coherent with the result | below the long aggression | booked in parts | NOT stated |

## Not computable (needs CME-only data)

| Item | Why |
|---|---|
| Option volume (900 million, 3.29 billion) and gamma (negative or positive) used as day-type filters | needs options data; Deribit options exist but are not Binance data and the speaker gives no formula |
| Platform-provided liquidation counts (1,249 contracts) | not in aggTrades; the Binance futures forced-liquidation stream is a separate feed (OURS to check) |
| Per-trade stop and target distances for trades 3 to 5 | not stated in the video |
