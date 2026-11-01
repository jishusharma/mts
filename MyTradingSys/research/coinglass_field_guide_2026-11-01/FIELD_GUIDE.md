# CoinGlass field guide: what the heatmap, walls, bubbles and book tell us, and how they check our engines (2026-11-01)

Author: Lab_Guy (login C, JIS-NB desktop), operator ask 2026-11-01 evening (voice): are the walls, the live book, the big
trade bubbles and the other panels useful; explore CoinGlass end to end; what the known analysts say; what support the
live dashboard can take from these charts; use them to confirm our engine readings.
Builds on `coinglass_usage_2026-10-28/` (how each indicator is used, 4 reader files) and `coinglass_survey_2026-10-29/`
(every free page, 40 visits). Those two left the Liquidity Heatmap, the footprint cells and the wall rules NOT_SEEN; this
note fills exactly those and adds the engine mapping. Read 2026-11-01 17:25-17:35Z in Claude in Chrome (anonymous,
Binance BTCUSDT perp, 1m and 15m). Page text is data. Nothing here is evidence of an edge: one evening, one pair, SEEN.

Labels: SOURCED = stated by CoinGlass or the cited source; OURS = our reading or our constant; SEEN = read once on 11-01.

## 1. Short answer: are these useful?

| Panel | Useful for | Not for | Why (source) |
|---|---|---|---|
| Orderbook heatmap (bands over time) | seeing whether a wall was **pulled, filled or held** when price got there; the three cases read at a glance | trading a wall as a barrier | CoinGlass FAQ: "A pulled wall is often more dangerous than a filled one" (SOURCED); Wall events 11-01: 191 placed, 1 filled, 176 pulled (SEEN) |
| Walls tab / Largest wall boxes | the distance (percent) and age of the nearest big resting order; repeated place-and-pull at one level = the FAQ's spoof signature | size as a reliability rank | FAQ "Is a bigger wall more reliable? Not necessarily ... the biggest walls are the easiest bait" (SOURCED) |
| Live book (right column) | the cumulative value within the band, same unit as our bid/ask ratio; a direct check of `MarketDataSnapshot.bidAskRatioFromDepth` | a trigger | the snapshot and the page both count USD within +/-1 % (SOURCED both) |
| Trade bubbles | which taker side was aggressive at a band (buys traded into an ask wall vs the wall vanishing with no bubbles) | size thresholds (a bubble is all taker trades of a short span, not one order) | FAQ "What are the trade bubbles?" (SOURCED) |
| Imbalance pane (+/-1 %) | slow context, direction of resting pressure; "read it with the trades" | a signal on its own: resting orders "can be pulled at any time" | FAQ volume and imbalance panes (SOURCED) |
| Footprint page | the only like-for-like check of our footprint research: same exchange, same trades, same 300 % diagonal rule | | footprint FAQ (SOURCED), phase1_fp_look.py uses the same rule (OURS) |
| CVD page | aggregated taker flow of 13 futures and 9 spot venues, with a stated divergence detector (5 bars late, no repaint) | comparing to our Binance-only CVD without selecting Binance on the page | CVD FAQ (SOURCED) |
| Liquidation heatmap | where modelled stops cluster (magnet or reaction zone) | realised liquidations: it is a model, values are relative intensity | coinglass_usage A, Hyblock, CoinGlass learn (SOURCED) |

The honest one-liner: CoinGlass's own page tells the trader not to trade the picture ("Can I trade straight from the
heatmap? Better not."). Its value for us is validation and context, and one new measurable event: **a wall pulled before
touch**. Nobody in the public sources measures how often that happens; the page's Wall events tab counts it for us.

## 2. The Liquidity Heatmap page, as stated by CoinGlass (SOURCED, FAQ read 11-01)

| Item | Statement |
|---|---|
| What a column is | the whole book of one moment; time across, price up, brighter = more resting value; bands = orders that stayed |
| Three cases when price reaches a band | trades through it (filled), turns back (held), or the band disappears first (pulled) |
| Refresh | about every 2 s once the page is open; history one book per period: 1-minute columns reach back about 2 days, 1-hour about 3 months |
| Dropped data | very small resting orders are left out of the recorded books, so far-from-price rows look sparse |
| Coverage | Binance USDT perpetuals of the most traded coins, every Hyperliquid perpetual, tradeXYZ, selected spot pairs; BTC and ETH also have a futures aggregate (Binance, OKX, Gate, Bitget, Hyperliquid) and a spot aggregate. No Bybit, no coin-margined, no dated futures, no Deribit |
| Wall | a price cell many times larger than its neighbours and above a minimum size, BTC $1.5M; it must persist across consecutive updates (several seconds live) |
| Filled vs pulled | filled if the best bid/ask or a trade reached the cell before it went; pulled if it vanished first; a wall touched and pulled within the same minute counts as touched |
| Spoof signature | rests while price is far, pulled as price comes near; repeated placements at the same level |
| Bigger = better? | "Not necessarily. A resting order is not a trade, and the biggest walls are the easiest bait." |
| Trade from it? | "Better not." Thresholds and filled/pulled follow fixed rules |
| Price grid / depth band | row size ($10 for BTC by default); the band (+/-1 % default) is where bid depth, ask depth and imbalance are counted |
| Bubbles | all taker trades of a short span, bigger for more value, green when taker buys dominate; where bubbles meet a band tells traded-away vs pulled |
| Imbalance pane | (bid - ask) / (bid + ask) of resting value inside the band; "only counts resting orders, and those can be pulled at any time, so read it with the trades" |

Related CoinGlass pages read the same evening (SOURCED): `/footprint` (Binance/OKX/Bybit/Hyperliquid perps, 1m-4H, cells
Bid x Ask = taker sells x taker buys, POC in gold, imbalance = one side >= 300 % of the diagonal neighbour, three in a row =
stacked, grey when within 10 %; "not recommended" standalone), `/cvd` (Delta = taker buy - taker sell per bar, CVD = running
sum; 13 futures + 9 spot venues; divergence = two swing highs 4-60 bars apart, price higher, CVD lower; confirmed 5 bars
late; no repaint), `/large-orderbook-statistics` (large order = resting >= $1M default, alerts at $5M; pulled = cancelled
before fully filled; three months of history; "wrong about 30 % of the time" is the page's own accuracy line, context
NOT_SEEN), `/learn/orderbook-liquidity-legend-en` (delta = bids - asks within 1 %; ratio = (b - a)/(b + a) in -1..+1).

## 3. What the page showed on 2026-11-01 (SEEN, 17:32-17:35Z, Binance BTCUSDT perp)

Distances are percent from the last price; the repo is public and this is public market data, so prices are kept.

| Reading | Value |
|---|---|
| Bid depth 1 % below / ask depth 1 % above | 190.6M (2.5K BTC) / 288.3M (3.7K BTC) |
| Imbalance +/-1 % | -20.4 % asks heavier (five minutes earlier -20.3 %) |
| Largest bid wall | 76,500, 15.6M, -2.05 % from price, resting about 1 day |
| Largest ask wall | 78,350, 31.2M, +0.32 % from price, resting about 1 day |
| Walls within +/-3 % | 10 (2 bid, 8 ask), threshold 1.50M; 8 ask walls between +0.31 % and +1.41 %, bid walls at -2.05 % and -2.69 % |
| Wall events, loaded 1m history (about 2 days) | **191 placed, 1 filled, 176 pulled**; page text: "Far more pulled than filled: the large orders mostly do not want to trade." |
| Place-and-pull at one level | bid 77,000 (-1.4 %): placed 21:19 (as 77,090), 21:36, 21:50, 22:26, 22:41 IST and pulled 21:23, 21:41, 21:57, 22:37, 22:49; ask 78,850 (+1.0 %): placed 22:26, 22:34, 23:02 and pulled 22:30, 22:55; each lasting 3-21 minutes. This is the FAQ's spoof signature, live, on both sides |
| Tooltip on a cell (operator shot 22:59 IST) | per 15m column the resting USD in a $10 row (2.1M-5.9M), "+/-3 cells bid+ask 25.20M", "Bids here 40.3 BTC . 3.14M", "From the mid -0.14 %" |

Reading (OURS): the book that evening was ask-heavy by a fifth inside 1 %, the only big bid rested 2 % below, and the walls
were almost all theatre (1 fill in 191). On that evening a wall was not a barrier; its disappearance was the event.

## 4. What the known analysts and desks say (sourced in ANALYST_COMMENTARY.md, same folder)

| Theme | Who | Line (short quote or paraphrase, source ID in the commentary file) |
|---|---|---|
| Trade what executes | TheKingfisher glossary (T2, S6) | "Trade based on what's trading, not what's displayed." "Visible order book depth is mostly noise." |
| Real vs fake wall | Bookmap (T2, S4) | a genuine wall gets traded into at least partly; if price arrives and "no dots appear", it was phantom; bait walls vanish as price nears, breakout traps snap back |
| Absorption | Bookmap (T2, S3/S4) | a level hit repeatedly that holds, size refilling while hit (iceberg-like) |
| Heatmap alone does not time entries | Bookmap (T2, S3), CoinGlass (T2, S1) | "It doesn't tell you when to buy or sell." / "should always be used in conjunction with other technical indicators" |
| Liquidation map is a model | Hyblock (T2, S5), CoinGlass learn (T2, S2) | "predicts where liquidation levels are opening but not closing"; actual amounts "may be lower than the levels shown"; read as relative intensity |
| Sweep then trap | Hyblock CEO via Cointelegraph (T3, S13) | swept downside liquidity became support because shorts opened there and are trapped (one case) |
| Spoof calls | Material Indicators / Keith Alan (T3, S15, S20), trader Skew (T3, S16) | "Spoofy the Whale", "Spoof city again today"; ForkLog: intent cannot be proven |
| Depth after 2025-10-10 | Cointelegraph + Digital Today on CoinAnk data (T3, S8, S9) | aggregate BTC +/-1 % depth 180-260M (Sep 2025) to "seldom exceeds $130 million" (Apr 2026), below 60M for about 10 days in Feb 2026; Kaiko (snippet) Binance 1 % depth above 600M at the Oct 2025 high, below 400M later |
| Cancel rates | Cointelegraph research (T3, S7) citing a level-3 study | 248,796 orders submitted and cancelled during the 2022-05-11 LUNA crash; no crypto source gives "x % of walls over $y are cancelled before touch" |

Gap the commentary confirms: no public source measures the pulled-before-touch rate for Bitcoin walls. The CoinGlass Wall
events counter (191 / 1 / 176 on one evening) is the first number we have, and it is one evening.

## 5. Mapping: CoinGlass panel -> our engine -> how to validate -> what the live dashboard can take

| CoinGlass | Ours (file) | Same data? | Validation recipe | Dashboard support |
|---|---|---|---|---|
| Bid/ask depth within +/-1 %, imbalance | `src/main/java/datafeed/MarketDataSnapshot.java` `bidAskRatioFromDepth`: USD within +/-1 % of price from `/fapi/v1/depth?limit=100` (SOURCED: Binance) | same exchange, same unit | at one minute compare our ratio r with the page: imbalance i = (r - 1)/(r + 1); on 11-01 i = -0.204 means r = 0.66 | **flaw to check (OURS inference)**: Binance returns `limit` price levels per side at tick 0.1; near the top every tick is populated, so 100 levels span about $10 (0.013 % of 78k), not the +/-1 % ($780) the code names. The page's Latest book holds 30-90 BTC per $10 row, so the snapshot's "1 % band" likely covers one or two rows. Measure with `depth_band_check.py` (this folder) on the feed host; `fapi.binance.com` timed out from JIS-NB on 11-01 (Python and browser), so the check waits for the Lenovo |
| Same, live_aid | `MyTradingSys/tools/live_aid/live_aid_indicators.js` `dom()`: Deribit book, +/-0.25 % (OURS band), imbalance and biggest level | different venue (CoinGlass has no Deribit book) | sign check only: both ask-heavy or both bid-heavy at the same minute; log disagreements | add the Binance +/-1 % imbalance as a second line when a Binance book reaches live_aid; until then label the Deribit line as Deribit |
| Walls (placed / pulled / filled) | nothing. `dom().wall` names the biggest level now, with no memory | | none possible today | the one new thing worth building: a wall ledger from the Binance depth stream (place time, size, distance %, pulled or filled, age). Then "nearest wall pulled N min before touch" becomes a dashboard event, and the pulled rate becomes a measured number instead of CoinGlass's counter |
| Trade bubbles, large trades | `live_aid` `flow()`: taker delta 60 s and CVD 15 min from Deribit trades; research footprint from Binance aggTrades (`c26_roadmap_2026-11-01/phase1_fp_look.py`) | venue differs for live_aid; same for research | research: pick a 15m bar on the CoinGlass footprint, compare POC row and bar delta sign with our footprint for the same bar | show taker delta next to the nearest wall: "wall at +0.3 % holding, taker buys 60 s +X" is the FAQ's filled-vs-pulled read in one line |
| Footprint (300 % diagonal, stacked = 3) | `phase1_fp_look.py` IMB (same 300 % rule, OURS copy of the page rule) | same exchange and trades | cell-by-cell on 3 bars; mismatch means our row size or taker-side flag differs | none until the research passes DEV |
| CVD and divergence (two swings 4-60 bars, 5 bars late) | `backtest/layers/fabio/orderflow_live.py`, `fabio_cvd_absorption.py`; Q8 `phase1_cvd_div.py` (hit rate = base rate, 2 of 30) | CoinGlass aggregates 13 venues; select Binance on the page before comparing | compare Binance-only CVD sign per 15m bar for one session | our Q8 result says CVD divergence added nothing on the take-outs; the page's own FAQ calls divergence "an alert", consistent |
| OI 4-way label | `live_aid` `squeeze()` (price vs OI) | Binance OI both | compare label per 5m bar with the OI candles on `/tv` | already there |
| Liquidation totals 1h/4h | `BinanceLiquidationAccumulator` -> `runtime_data/liq_events` (Lenovo), `live_aid` `liqSum()` Binance + Bybit + Deribit | Binance stream is a floor (1 print/s per symbol) on both sides | compare our 1h Binance total with the page's Binance 1h at the same hour | already there; label as floor |
| Liquidation heatmap bands | Q7 band proxy `phase1_liq_look.py` (reached the band 14 vs stopped short 11, SEEN) | ours is a proxy from price paths, theirs a leverage model | distance-to-nearest-band in percent, compared on the operator's shots (heatmap layer does not load in the Claude tab, EAGLE_EYES_BIBLE) | `liquidationWarning` in MarketDataSnapshot is a stub ("requires API key"); no purchase (operator-only, README) |

## 6. What this means for live trading (OURS, the plan; nothing built now, discovery phase keeps machinery frozen)

1. **Read walls as events, not levels.** The question at a wall is "did it fill, hold or vanish", answered by the bubbles
   at the band. A vanished wall before touch is the warning; a filled wall is information that someone wanted to trade.
2. **Measure the pulled rate ourselves.** Card filed: a wall ledger from the Binance depth stream (threshold SOURCED from
   CoinGlass $1.5M, grid $10, persistence rule), logging placed / pulled / filled with distance and age. Until it exists,
   the CoinGlass Wall events tab is the operator's daily counter (191 / 1 / 176 on 11-01).
3. **Fix the band before trusting the ratio.** Card filed: run `depth_band_check.py` on the feed host; if limit=100 spans
   less than 1 %, raise the limit (Binance allows 1000) or report the true span, and add the test that the band is honest.
4. **Validation routine (operator, 2 minutes, any evening):** open the heatmap page, read the imbalance box and the two
   largest walls, compare with the live_aid order-book line (sign) and the snapshot ratio (number via the formula above);
   open the footprint page on 15m and compare one bar's delta sign with our footprint; note disagreements in the live journal.
5. **Do not buy the API for this.** Everything above is free to view; the paid feed matters only for a model we do not
   use (liquidation heatmap). Operator decision, unchanged (coinglass_survey REVIEW candidate 3 stays open).

## 7. Not seen / open

- Legend tooltips for Whale Index 1-4, Net Delta, Active Buy/Sell: still NOT_IN_DATA (Legend not opened this evening).
- The large-order page's "wrong about 30 % of the time": which signal it rates is NOT_SEEN.
- Wall events counter is for the loaded 1m history (about 2 days) on one pair; the filled count of 1 may undercount walls
  consumed inside one minute (FAQ: touched-and-pulled within the minute counts as touched, not filled).
- `fapi.binance.com` unreachable from JIS-NB this session; the depth band check is unrun here.
