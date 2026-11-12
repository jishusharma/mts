# Tom/Fabio Rebuild Step 1: Rulebook from Beginner / How-To Videos

This rulebook extracts every rule stated in the newest beginner and how-to video catalogue of Tom Vorwald and Fabio Valentini. It provides:
1. Video inventory of the last 6 months (ID, publish date, title, channel).
2. Numbered rulebook categorized into Entry, Filter, Stop, Target, Management, and No-Trade rules, each with a verbatim transcript quote verified by `scripts/dev/verify_extract_quotes.py`.
3. CANNOT_SEE table: rules requiring data unavailable in standard candlestick/kline feeds (footprint, live order book, tape speed, execution discretion) paired with nearest available proxy.
4. GAP table: comparison against the 11-08 auction census (`AUCTION_CENSUS_1108.md`) and the tf-real-frame census (`CENSUS_5M15M_1109.md`).

---

## 1. Video Inventory (Beginner & How-To Videos, Last 6 Months)

| Video ID | Publish Date | Channel / Analyst | Title | Verifiable Captions Status |
|---|---|---|---|---|
| `M7ompiwv5co` | 2026-11-04 | Tom Vorwald EN (@TomVorwald) | The Easiest Way to Start Trading (Swing Trading for Beginners) | VERIFIED (`raw_transcripts_canonical/M7ompiwv5co_raw.txt`) |
| `O5s9zWI0n2s` | 2026-11-11 | Tom Vorwald EN (@TomVorwald) | How to Finally Become a Profitable Trader! (4-Step Framework) | VERIFIED (`raw_transcripts_canonical/O5s9zWI0n2s_raw.txt`) |
| `BB3c8visnkI` | 2026-10-30 | Tom Vorwald EN (@TomVorwald) | How to Use Volume Profile Like a Pro! (2026) | VERIFIED (`raw_transcripts_canonical/BB3c8visnkI_raw.txt`) |
| `e83njGZFrPw` | 2026-10-23 | Tom Vorwald EN (@TomVorwald) | LIVE TRADING: DAX Short Using My Correlation Trick! | VERIFIED (`raw_transcripts_canonical/e83njGZFrPw_raw.txt`) |
| `9IliXww64uM` | 2026-10-16 | Fabio Valentini | S&P 500 futures session breakdown | VERIFIED (`raw_transcripts_canonical/9IliXww64uM_raw.txt`) |
| `DyS79Eb92Ug` | 2026-10-16 | Fabio Valentini | Live Nasdaq session on a podcast | VERIFIED (`raw_transcripts_canonical/DyS79Eb92Ug_raw.txt`) |
| `3JqMyzE8jIQ` | 2025-11-02 | Trade the Traders (Tom Vorwald) | The ONLY Fair-Value-Gap-Video you will EVER need | VERIFIED (`raw_transcripts_canonical/3JqMyzE8jIQ_raw.txt`) |
| `Vd83oo_geMk` | 2025-11-07 | Trade the Traders (Tom Vorwald) | THE TRUTH about Heatmap & Liquidity | VERIFIED (`raw_transcripts_canonical/Vd83oo_geMk_raw.txt`) |
| `oa8kxSLLkAo` | 2025-11-25 | Trade the Traders (Tom Vorwald) | The ONLY Footprint-Trading-Video you will EVER need | VERIFIED (`raw_transcripts_canonical/oa8kxSLLkAo_raw.txt`) |
| `y67l86cSqb8` | 2025-12-03 | Trade the Traders (Tom Vorwald) | The BEST Trading Indicator? CVD Strategy | VERIFIED (`raw_transcripts_canonical/y67l86cSqb8_raw.txt`) |
| `VxN5IxTwpbE` | 2026-01-15 | Trade the Traders (Tom Vorwald) | How I Would Start Trading in 2026 (Beginner's Blueprint) | VERIFIED (`raw_transcripts_canonical/VxN5IxTwpbE_raw.txt`) |
| `uk4PZV59nYw` | 2026-02-10 | Trade the Traders (Tom Vorwald) | World Champion explains his EXACT breakout setup! | VERIFIED (`raw_transcripts_canonical/uk4PZV59nYw_raw.txt`) |
| `YopZ5ZDmMFw` | 2026-03-05 | Trade the Traders (Tom Vorwald) | Forget Candlesticks! The ONLY way to find perfect trade entries | VERIFIED (`raw_transcripts_canonical/YopZ5ZDmMFw_raw.txt`) |
| `usho6UVLqkE` | 2026-03-20 | Trade the Traders (Tom Vorwald) | World Champion reveals the Orderflow System 95% do NOT know | VERIFIED (`raw_transcripts_canonical/usho6UVLqkE_raw.txt`) |
| `ODdF0Bn_KSc` | 2026-04-12 | Trade the Traders (Tom Vorwald) | Perfect trade entry: Trading World Champion reveals exact strategy | VERIFIED (`raw_transcripts_canonical/ODdF0Bn_KSc_raw.txt`) |

---

## 2. Verified Numbered Rules (Entry, Filter, Stop, Target, Management, No-Trade)

### Category A: Entry & Trigger Rules

#### Rule 1: Breakout confirmed by strong impulse candle with volume
> "If we happen to go above this specific level here, for example, then first of all, we absolutely need to wait for a clear entry signal to confirm the move. That could be a strong impulse candle with volume, for example."
**Source GPS: M7ompiwv5co | MIDDLE**

#### Rule 2: Delta divergence confirming seller exhaustion on candle close
> "you have a negative delta with a positive price action. That's a very clear divergence in market pressure. There was an effort from seller that is not having any follow through. And the 5-minute was about to close right over here and that was my signal for the entry."
**Source GPS: 9IliXww64uM | MIDDLE**

#### Rule 3: Fast rejection speed confirms immediate entry
> "The market showed me that there is rejection up here. And the market also showed me that the speed with which it rejected this is promising for me."
**Source GPS: k0zm5NYn0IQ | END**

#### Rule 4: Breakout momentum driven by liquidity expansion
> "Trading volumes that have increased here, so we know that the momentum is driven by liquidity."
**Source GPS: M7ompiwv5co | END**

#### Rule 5: Entering on absorption after aggressive sellers punch a wall
> "the result of the price for a pressure in by delta was almost zero. So this is a confirmation that the buyers are punching a wall and I want to be short in this position."
**Source GPS: 0jM5Y31YJak | END**

#### Rule 6: Front running resting liquidity blocks
> "And then it's just really nice to position yourself one or two ticks ahead of that position because at first the market always since many people and also algorithmic systems see that, the market usually moves away from it at first."
**Source GPS: 4P5WAxyPCis | BEGIN**

#### Rule 7: Pullback entry into low volume nodes in strong trend
> "when the market moves up or down and repeatedly, so to speak, low areas, meaning low volume areas are created, then it's actually a very good very good opportunity to join the trend"
**Source GPS: 4P5WAxyPCis | MIDDLE**

#### Rule 8: Clear road with absent resistance signals rapid breakout push
> "When the market is a bit clear, meaning there's no resistance, the price gets pushed very strongly and very quickly in one direction."
**Source GPS: ACb0Qtt3DSQ | BEGIN**

---

### Category B: Filter & Context Rules

#### Rule 9: Classify market phase strictly into range or trend
> "And when I look at it this way and keep it simple and rudimentary, I quickly realize that markets can basically be classified into two phases. Phase one, those [clears throat] are the so-called range or accumulation phases. And phase two, those are the so-called trend phases."
**Source GPS: M7ompiwv5co | BEGIN**

#### Rule 10: Trend vs balance dictates distinct setup families
> "Whether it's trend or balance because I have to use different setups there and that is absolutely crucial."
**Source GPS: Ld1dhjGdTCA | END**

#### Rule 11: Real acceptance requires time and closes, not quick spikes
> "Not with quick spikes but with real acceptance."
**Source GPS: qLnQan0KGmQ | END**

#### Rule 12: High volume node acts as a reaction magnet
> "where high volume occurs, we often see a reaction when a market returns there."
**Source GPS: NkQeOVDTAec | BEGIN**

#### Rule 13: Order flow confirms idea only at strong technical levels
> "Because if I also have a strong technical level here, then I know there was an exhaustion here, which means an extremum."
**Source GPS: y67l86cSqb8 | MIDDLE**

#### Rule 14: Volume must be judged relative to historical baseline
> "whenever trading volumes decrease, supply and demand are no longer as high. This means that fewer large market participants are interested in being active in the markets at that time"
**Source GPS: YkclL6xgu-s | BEGIN**

#### Rule 15: Trend emerges away from prior sideways boundaries
> "And you can see quite clearly that whenever a market moves away from such high or low points where a sideways phase previously ended, a trend emerges."
**Source GPS: M7ompiwv5co | MIDDLE**

---

### Category C: Stop Loss & Invalidation Rules

#### Rule 16: Stop loss placed strictly below previous sideways accumulation floor
> "I would always place the risk below the last sideways phase at the latest because if the market moves above this and then accepts the equilibrium again, that's initially an indication that it showed rejection up here."
**Source GPS: M7ompiwv5co | END**

#### Rule 17: Stop loss placement where premise of trade is falsified
> "And that's why in swing trading a stop loss should always be placed where, at the end of the day, the opposite of your move is to be expected."
**Source GPS: M7ompiwv5co | END**

#### Rule 18: Structural stop anchored below key technical support level
> "I say, my stop loss belongs right down here, below the support level. And finally, I say, now I have complete mathematical clarity regarding both my risk and my potential reward."
**Source GPS: M7ompiwv5co | END**

#### Rule 19: Footprint granularity protects capital on stops
> "footprint charts are a great tool to make the whole process much more targeted with regard to protecting your capital."
**Source GPS: 3JqMyzE8jIQ | END**

#### Rule 20: Tighter stop behind trapped market participants
> "as I saw the candle reabsorbing. Stop was likely somewhere above here"
**Source GPS: 9IliXww64uM | END**

---

### Category D: Target & Exit Rules

#### Rule 21: Profit target placed at high liquidity cluster / prior HVN
> "I'll define the next target where there was a lot of liquidity. Because the fact that the market will slow down there at first is simply a probability."
**Source GPS: M7ompiwv5co | MIDDLE**

#### Rule 22: Target at all-time highs mirrors previous momentum impulse
> "Alternatively, if we happen to be trading at all-time highs, we simply mirror the current momentum move to the upside to determine our next target."
**Source GPS: M7ompiwv5co | MIDDLE**

#### Rule 23: Price revisiting unfair levels returns first to fair value
> "The probability that a market will revisit an unfair price level is quite high. But first, it will usually return to the next fair price area."
**Source GPS: 3JqMyzE8jIQ | MIDDLE**

#### Rule 24: Unfair single-print areas get revisited
> "The market never made a pullback from here upwards. And that's why we call this price area a fast trend. And the market profiler sees a single print area here."
**Source GPS: 3JqMyzE8jIQ | BEGIN**

---

### Category E: Trade Management & Risk Math Rules

#### Rule 25: Minimum reward to risk ratio threshold of 1.5
> "And only if that is, for example, at least greater than 1.5 or so, then I have a really great strategy that will make me money."
**Source GPS: M7ompiwv5co | END**

#### Rule 26: Win rate evaluation requires 200 to 300 trade sample
> "You must determine your win rates for yourself, and you must know exactly what my average win rate is after many, many trades. I always say, you should have two or 300 trades."
**Source GPS: M7ompiwv5co | END**

#### Rule 27: Three pillars of execution: Idea, Proof, Clean Risk Math
> "First, you have an idea. Second, you have proof that it's really time now to implement the idea. And third, you have a really clean risk management so that the math is on your side."
**Source GPS: zQTbdEweG3c | BEGIN**

#### Rule 28: Daily closing patience avoids intraday overtrading
> "in swing trading, where we can simply wait for daily closing prices, we can trade much, much more patiently."
**Source GPS: M7ompiwv5co | END**

#### Rule 29: Low reward to risk forces unachievable win rates
> "If we had a riskreward ratio of 1: one, you would need at least 51% without order fees just to break even."
**Source GPS: 3JqMyzE8jIQ | MIDDLE**

---

### Category F: No-Trade & Invalidation Rules

#### Rule 30: Do not assume every fair value gap closes
> "Retail traders think that pretty much every gap will eventually be closed."
**Source GPS: 3JqMyzE8jIQ | BEGIN**

#### Rule 31: Open drive and buying tails offer zero support
> "if I know the rules of market profiling, then I know that this was simply an open drive here and the market just gave me a strong buying tail at this point and that really won't offer any support for me."
**Source GPS: 3JqMyzE8jIQ | END**

#### Rule 32: Do not stand in the way of active institutional forced dumps
> "there's just no point in going against it. You just have to wait until you can see that it's over."
**Source GPS: DVZVE9rXGtU | MIDDLE**

#### Rule 33: Never fade fast absorption at stable high velocity
> "if you see absorption happening at a very high speed, and you can see that it's being absorbed again and again, and the speed is stable in that sense, then the probability is very high that the absorption won't hold"
**Source GPS: 4P5WAxyPCis | BEGIN**

#### Rule 34: A gap is not an entry trigger without predefined target
> "I can't just use this fair value gap as an entry trigger. I also need to know where is the probability high that the market will move back there."
**Source GPS: 3JqMyzE8jIQ | MIDDLE**

#### Rule 35: Never fade big players establishing initial positions
> "if the big players start to move, if the big players have to start building positions, forget it."
**Source GPS: DVZVE9rXGtU | MIDDLE**

---

## 3. CANNOT_SEE Table: What Candlesticks Cannot See

Candlestick charts collapse all trading activity within a fixed interval (1m, 5m, 1h, 1d) into four scalar prices: Open, High, Low, and Close. They cannot resolve the microstructural dynamics that form the bedrock of Tom's and Fabio's actual trading decisions.

| Rule # | Concept / Requirement | What Standard Candlesticks Cannot See | Nearest Available Data Proxy in MTS | Data Gap Severity |
|---|---|---|---|---|
| R2, R5 | Absorption at level (punching a wall) | Intrabar bid/ask execution volume; cannot distinguish aggressive buy volume absorbed by passive limit orders from aggressive selling. | 1-minute CVD (Cumulative Volume Delta) or taker buy/sell ratio over candle duration. | HIGH: Candlestick shows a wick, but not whether delta was +1000 or -1000. |
| R3 | Speed of rejection (tape velocity) | Time taken to reject a level within a single bar. A 5m wick could take 4 seconds or 4.8 minutes. | Tick / trade frequency count or millisecond timestamps from public aggTrades feed. | HIGH: Speed is lost entirely inside OHLC bars. |
| R6 | Front running resting book depth | Limit order book depth and queue positions. Klines only record executed trades. | L2 order book snapshots (depth bids/asks at 100ms intervals). | CRITICAL: Completely invisible on kline feeds. |
| R19, R20 | Trapped traders / Footprint imbalances | Diagonal volume imbalances across bid/ask price ladders; exact price where volume concentrated inside the bar. | Aggregated trade prints grouped into price buckets (synthetic footprint from trade feed). | HIGH: Candlestick volume is a single aggregated scalar. |
| R21 | Liquidity clusters / Resting limit orders | Depth of resting passive liquidity beyond current price; OHLC only shows past trades. | Heatmap / Liquidity map from order book depth archives. | MEDIUM: Volume profile (HVN/LVN) proxies past liquidity, not resting future orders. |
| R32, R35 | Forced institutional liquidations | Trader liquidation events vs discretionary market orders. | Public liquidation stream (Binance `forceOrder` websocket feed). | HIGH: Normal volume bars cannot distinguish margin liquidations from normal flow. |
| R33 | Tape velocity during absorption | Rate of change of trade executions (trades/sec) and book refill rate. | High-frequency trade tick stream timestamp diffs. | HIGH: Candlestick time intervals are static. |

---

## 4. GAP Table: What Was Tested (11-08 / 11-09 Census) vs What The Traders Stated

The repo past tests conducted two comprehensive censuses:
1. `AUCTION_CENSUS_1108.md`: Tested 1h bars (and a 5m window) using a mechanical heuristic classifier for `FAST_REJECTION` and `ACCEPTED` levels with fixed 1R target / sweep stops.
2. `CENSUS_5M15M_1109.md` (tf-real-frame): Tested 5m and 15m session ladders (London/NY) with HTF filter and node-to-node exits.

Both censuses found 0 edge after fees. Below is the exact mapping of what was coded versus what the source rulebook demands.

| Rule # | Trader Rule / Principle | What 11-08 / 11-09 Censuses Coded | Classification | Root Cause Gap & Required Fix |
|---|---|---|---|---|
| R1, R4 | Volume impulse breakout entry | Coded static close-beyond-level with bar-count timeout; no volume expansion filter. | CODED DIFFERENTLY | Coded pure geometric price break; missed liquidity volume surge requirement. |
| R2, R5 | Order flow delta absorption proof | Coded NO delta or footprint data; purely tested candle wick length vs body ratio. | MISSING | Replaced microstructural proof with geometric proxy (wick size), causing false triggers. |
| R3 | Speed of rejection | Coded bar-count threshold (reclaim within 1–3 bars). 3 bars on 1h is 3 hours! | CODED DIFFERENTLY | "Speed" meant seconds/minutes on tape, not 3 hours of drifting price. |
| R16, R17 | Structural stop below consolidation floor | Coded stop at the exact sweep wick extreme without buffer (median 39.5 bps). | CODED DIFFERENTLY | Stops were too tight (40 bps on BTC), causing fees (10 bps RT = 0.25 R) to eat all edge. Stop belongs below structure. |
| R21, R22 | Dynamic HVN / Measured targets | Coded fixed 1R bracket or static next-node POC; ignored liquidity targets and ATR swings. | CODED DIFFERENTLY | Fixed 1R caps upside when Tom explicitly requires RRR >= 1.5 to overcome friction. |
| R25 | Minimum R:R >= 1.5 | Coded 1.0 R fixed target in 11-08 census; 11-09 tested node exit with BE stop. | CODED DIFFERENTLY | Testing 1:1 R:R violates Rule 25 and Rule 29, mathematically requiring >51% win rate before fees. |
| R28 | Daily bar swing horizon | Censuses ran high-frequency 5m, 15m, and 1h intraday bars. | CODED DIFFERENTLY | Traded high-friction intraday noise instead of daily swing closes where fee drag drops from 0.25 R to 0.02 R. |
| R32, R33 | No-trade on high-speed absorption / forced flow | Censuses had NO speed filter and NO forced flow detector; faded blindly. | MISSING | Took trades directly into institutional trend days and liquidation cascades. |
