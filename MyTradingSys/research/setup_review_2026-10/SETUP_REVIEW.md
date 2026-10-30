# Setup review sheet: 22 chart setups from Tom and Fabio (2026-10-30)

- What this is: one page per setup, taken from `setup_catalog_2026-10-15/SETUP_CATALOG.md`. Nothing here is tested. No results are claimed.
- How you answer: read 3-4 setups, then write keep / rewrite / reject on the "Operator verdict" line of each. Say it in chat; the coordinator fills the Verdict log at the bottom.
- After all verdicts, pick 2-3 setups to test first (the "Picks" table at the bottom).
- SOURCED = the trader's own words, with the video id. OURS = a number or rule we added; never his. NOT STATED = he gives nothing in words (he often points: "here").
- Captions are machine-translated (Tom) or auto-captions (Fabio): a quote shows what he looks at, never an exact price or time.
- Example charts: `examples/<id>.png` (drawn separately). BTC = Binance BTCUSDT data we hold: candles, every trade (the "tape"), volume profiles. We hold no order-book history, no news, no stock/index data.

## Overview table

| id | plain name | trader | BTC can show | his examples | stop stated by him |
|---|---|---|---|---|---|
| TOM-1a | Fade a rushed push up (intraday short) | Tom | PARTIAL | 11 | Y |
| TOM-1b | Fade a swing top / rejected gap (daily bars) | Tom | YES (gap part NO) | 5 | Y |
| TOM-2 | Sell top, buy bottom of a sideways range | Tom | YES | 1 (a loss) | Y |
| TOM-3 | Resting sell order just under the last volume step | Tom | YES | 1 | Y |
| TOM-4 | Buy the pullback in a healthy uptrend | Tom | YES | 3 | Y |
| TOM-6 | Breakout / break-in | Tom | YES | 0 | N |
| TOM-7 | Range scalp around the day's average price | Tom | YES | 0 | N |
| TOM-8 | Gap close | Tom | NO | 1 | N |
| TOM-9 | Gap stays open: trade with the trend | Tom | NO | 0 | N |
| TOM-10 | Closing-auction gap reversal | Tom | NO | 0 | N |
| TOM-11 | Crude oil leads, index future follows | Tom | NO | 0 | N |
| TOM-12 | Break-in: price falls back into the old range | Tom | YES | 0 | N |
| TOM-14 | After a news shock, trade back to where it started | Tom | PARTIAL | 0 | N |
| TOM-15 | Candle patterns at a range edge | Tom | YES | 0 | N |
| TOM-16 | Short a top built by forced hedger buying | Tom | PARTIAL | 0 | N |
| TOM-17 | Low-volume-zone scalp decided by trading speed | Tom | PARTIAL | 0 | N |
| FAB-1 | Flat range, pressure builds, break on volume | Fabio | PARTIAL | 1 | N |
| FAB-2 | Big effort absorbed ("punch to the wall"), trade the other side | Fabio | PARTIAL | 3 | N |
| FAB-4 | Failed breakout back into yesterday's range | Fabio | YES | 2 (weak) | N |
| FAB-5 | Buyers defend a level: long | Fabio | PARTIAL | 11 | Y |
| FAB-6 | First 30 minutes of the US open | Fabio | PARTIAL | 0 | N* |
| FAB-8 | Rejection at the thinnest-volume price of a swing | Fabio | YES | 0 | N |

Stop column = does he name a stop LOCATION in words (never a distance as a rule), per catalogue section 0 and section 7. *FAB-6: section 0 says N; the 2026-10-18 merge under FAB-6 adds "a candle close beyond the value area low = invalidation" and "stop below the protected area" (cUTsoU-15Tc, described in the catalogue but not block-quoted). Left N here because section 7 still counts Fabio 1 of 6.

## Gaps status

Source: `EXTRACTION_CRITICAL_GAPS_2026-10-18.md`, checked against catalogue sections 4.2 and 6.4.

| gap | status | evidence |
|---|---|---|
| G-TOM-1 (Tom videos and V2 extracts missing from the catalogue) | Mostly merged, 15 videos still open | Section 6.4: 8 V2 extracts (6.4.1), 7 V1 extracts (6.4.2) and the batch-1 delta (6.4.3) are merged. Section 6.4.4 lists 15 videos with no usable extract (backlog, not merged). The old rows were not rewritten (6.4.3 last bullet), so section 6.2 still shows 10 videos as "gate FAILS". |
| G-FAB-1 (5 recovered Fabio transcripts) | Merged | Section 4.2 (FAB-9, FAB-10, two filters, U2 split, LVN rationale), plus the FAB-6 and FAB-8 merge notes and section 6.3. FAB-9 and FAB-10 are "candidate rows" only: not in the section 0 table, so not on this sheet. |
| G-FAB-2 (Fabio V2 delta never merged) | Merged | Section 4.2 "Other items merged": retest entry FAB-7b, 1% daily loss stop, FAB-6 definition (StaphlRH8NQ). The false "minimum 1:3" rule FR-13 is recorded as NOT CONFIRMED (section 5). FAB-7b stays inside the heat-map tool family (section 4.1), not a setup. |

---

## Tom setups

### TOM-1a Fade a rushed push up (Tom)
- What you see on the chart: Price shoots far above yesterday's range from the session start. Then it stalls at the top (a small inside bar, big sell volume), and little trading volume sits up there ("no liquidity left"). Price starts falling back toward where the volume is.
- Rule in one breath: WHEN a fast push from the session start sits far above prior value [value = price band with 70% of volume], stalls with large sell volume, and the daily value centres are not stacking higher (SOURCED: k0zm5NYn0IQ, VOiy8mAALWA) THEN go short (three paths: at the top, on the pullback, or on a break lower; SOURCED: l8RZrBfzvp4, k0zm5NYn0IQ; order type NOT STATED) STOP above the level where the sellers sit (SOURCED: n7ZSkjb7JXs; 20 DAX points in one trade, k0zm5NYn0IQ, not a rule) TARGET below the start of the push, first the old balance zone (SOURCED: T6hDJcHrVBM, zQTbdEweG3c). OURS (never his): the BTC "session start", the number of proofs, opening-range ranking, 0.40% minimum stop, one re-entry per session.
- His exact words:
  - "I can clearly see that there's no liquidity left" (k0zm5NYn0IQ)
  - "this lethargy was characterized by large sales volumes. And that prompted me to plan a short trade there" (l8RZrBfzvp4)
- What BTC can show: PARTIAL. Missing on BTC: a real session open or pre-market (any anchor is OURS), gaps, news data, empty order book above (live only), ES/NQ confirmation (ETH only).
- Evidence so far: 11 assigned examples including 1 candidate (not certified trades). No MTS backtest measured on this setup.
- Open gaps:
  - He calls a P shape [a profile bulging at the top] both a trend sign and an exhaustion short (T6hDJcHrVBM); we only resolved it by reading it as a failed upside break.
  - "Many proofs" needed, no count stated; "healthy vs unhealthy trend" is tested by volume under the move, not by position against value.
  - Reward-to-risk he quotes differs by video (1.5 at 40-45% hits vs over 3 at 30-40%).
- Example chart: `examples/TOM-1a.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-1b Fade a swing top / rejected gap (Tom)
- What you see on the chart: On daily bars a big run (earnings jump, short squeeze) ends in a B profile [a profile bulging at the bottom, a sign of weakness] at the top. Or the day opens far above yesterday and is rejected at the high. Price then goes back toward the volume below.
- Rule in one breath: WHEN a run ends in a B profile at the top, or a far gap-up open is rejected (SOURCED: tS6ZEiHj8gQ, OUM9LYwL8eA, kXhIAug0Gh8) THEN go short; a limit order is placed again if the first one is hit (SOURCED: kXhIAug0Gh8) STOP above the level (e.g. entry 640, stop 730; SOURCED: tS6ZEiHj8gQ, one example) TARGET value, or "the next short" once price breaks the last range low (SOURCED: kXhIAug0Gh8, OUM9LYwL8eA). OURS: the written-down definition of a B profile (his is NOT STATED).
- His exact words:
  - "Because this here is a wonderful B profile." (tS6ZEiHj8gQ)
  - "I said, if we go over this again, there's a high probability we'll run to value." (kXhIAug0Gh8)
- What BTC can show: YES on daily bars for the B-profile top once we write our own B-profile rule. NO for the gap case (BTC has no gaps).
- Evidence so far: 5 assigned examples (ANG R1, R2, R16, R4, R5), none certified; R4 and R5 are marked open. No MTS backtest measured.
- Open gaps:
  - B-profile definition, stop distance, and entry trigger beyond "after the rejection": NOT STATED.
  - R4 sits on the gap-close idea (TOM-8) and R5 on the range idea (TOM-2); the split is unsettled.
- Example chart: `examples/TOM-1b.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-2 Sell top, buy bottom of a sideways range (Tom)
- What you see on the chart: A sideways market where buyers and sellers are about equal. Price reaches the top of the range (or its bottom). A weak-looking profile at the top, or a lower range after a rejection, is "the setup itself".
- Rule in one breath: WHEN the market is sideways and price is at the range top with proof of weakness (finished auction [no more trades at the extreme price]; B profile; lower balance) (SOURCED: BVpYGKz9PBU, VxN5IxTwpbE) THEN short at the zone, or better on the pullback to the setup (SOURCED: BVpYGKz9PBU) STOP back above the level he sold under (SOURCED: BVpYGKz9PBU; the invalidation is a state, not a price: viT_VzF5Fsw) TARGET the next price area / volume below, or VWAP [volume-weighted average price] if VWAP is steep (SOURCED: BVpYGKz9PBU, 43JaKHRvxHk). Mirror for longs at the bottom. OURS: the engine's VAH/VAL zones and the "3 proofs" bar.
- His exact words:
  - "I can definitely look for short trades up here and long trades down here." (BVpYGKz9PBU)
  - "if we move back above this level then I have a problem with my short position" (BVpYGKz9PBU)
- What BTC can show: YES (range, value edges, VWAP, volume all computable). Nothing missing except that "B profile" needs our written rule.
- Evidence so far: 1 taken trade (viT_VzF5Fsw, a loss; he says he should have given up once price traded through and accepted the range) + 1 plan (ANG R24). No MTS backtest measured.
- Open gaps:
  - One older rule says shorts sit BELOW yesterday's value low, the other says at the range top: which is the setup is open.
  - No definition of B profile; when a balance turns into a breakout is NOT STATED.
  - A level alone is not an entry: he called his first sell zone "just a target area, not a real entry area" (viT_VzF5Fsw).
- Example chart: `examples/TOM-2.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-3 Resting sell order just under the last volume step (Tom)
- What you see on the chart: A trend flattening into a range, with an inside day [a whole day inside yesterday's range] near the high. The volume profile has a sharp edge (a "step"); below it price can fall fast.
- Rule in one breath: WHEN the trend flattens, an inside day forms near the high, and a "smart support" zone (old value areas plus single-print areas [prices touched once]) sits below (SOURCED: yRvMW6lgN1o) THEN place a resting sell limit just below the last volume step (SOURCED: yRvMW6lgN1o) STOP not above the high, at the level where the largest footprint volumes traded [footprint = volume at each price]; no price given (SOURCED: yRvMW6lgN1o) TARGET last week's point of control [price with most volume] and the smart-support zone (SOURCED: yRvMW6lgN1o). OURS: the written-down meaning of "volume step".
- His exact words:
  - "I said I would place a limit order specifically right below the last volume step of the corresponding price profile of the volume profile" (yRvMW6lgN1o)
  - "It doesn't belong above the high." (yRvMW6lgN1o)
- What BTC can show: YES (range, inside day with a UTC-day boundary that is OURS, profile step from the tape).
- Evidence so far: 1 trade (ANG R13): risk 12 ticks, gain 97 ticks. That is one result, not a rule. No MTS backtest measured.
- Open gaps:
  - Stop price and distance NOT STATED; what exactly makes a "volume step" NOT STATED.
  - Overlaps with TOM-2 (sell the top of a range) and with TOM-1a's pullback path; kept apart only because the entry is a resting order at a profile edge.
  - Source video is V1-only (never re-extracted).
- Example chart: `examples/TOM-3.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-4 Buy the pullback in a healthy uptrend (Tom)
- What you see on the chart: A rising market with real volume behind it, not quick spikes. Price pulls back to VWAP, to the value it just accepted, or to yesterday's point of control after a buying tail [a long lower shadow on the day's profile]. Buyers show aggressive buying there.
- Rule in one breath: WHEN the trend structure is healthy, the previous reaction was up, and large volumes have shifted upward (SOURCED: ODdF0Bn_KSc, qLnQan0KGmQ, YkclL6xgu-s) THEN buy the pullback after proof (SOURCED: qLnQan0KGmQ) STOP below the last volumes; distance and time stop NOT STATED (SOURCED: YkclL6xgu-s) TARGET the next high-volume area, or where large volumes used to be (SOURCED: qLnQan0KGmQ, YkclL6xgu-s). Mirror for shorts. OURS: where VWAP is anchored on BTC. The merge of the old TOM-5 into this row is the catalogue's reading, not his statement.
- His exact words:
  - "where does my stop loss belong. Yes, below the last volumes." (YkclL6xgu-s)
  - "Not with quick spikes but with real acceptance." (qLnQan0KGmQ)
- What BTC can show: YES (trend, VWAP, value areas, volume under the move). Nothing missing apart from the OURS anchors.
- Evidence so far: 3 assigned examples (ANG R17 win; R6 crude long, stopped; R7 crude re-entry, win). No MTS backtest measured.
- Open gaps:
  - Stop distance, time stop and the exact entry trigger at the pullback are NOT STATED.
  - One video (4MoNjEQ2Dd8) is filed as a breakout by one source and as a pullback long by another; the catalogue picks "pullback" and says whether he files it that way is NOT STATED.
  - Two stop wordings in one video ("below the last low", "below the business zone").
- Example chart: `examples/TOM-4.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-6 Breakout / break-in (Tom)
- What you see on the chart: A sideways zone is about to resolve. Price pushes through old highs (a "ledge"), speed picks up, buying shows. He also wants clear empty space to the left of the breakout.
- Rule in one breath: WHEN the market is out of balance, there is clear space to the left, a strong candle, a short pullback and another strong candle, with matching order flow [who is buying or selling] (SOURCED: uk4PZV59nYw, 4VXpUjhKG2U) THEN enter or add at the break if speed holds (SOURCED: 4MoNjEQ2Dd8; order type NOT STATED) STOP NOT STATED TARGET the next high-volume price (SOURCED: qLnQan0KGmQ); he says to exit at once if the opposite of your trend direction appears (uk4PZV59nYw).
- His exact words:
  - "whenever you trade breakouts, you need to have plenty of clear space to the left" (uk4PZV59nYw)
  - "with breakout setups, you often have risk reward ratios that are not greater than 1:1 or 1.5:1." (uk4PZV59nYw)
- What BTC can show: YES (balances, ledges, VWAP shift, buying/selling speed from the tape).
- Evidence so far: 0 own trades. The only taken instance is an add inside the TOM-4 example. No MTS backtest measured.
- Open gaps:
  - Stop, speed threshold and entry trigger NOT STATED.
  - He says breakouts pay only 1:1 to 1.5:1 in one video, but holds "for the explosion" in another (4MoNjEQ2Dd8); not resolved.
  - TOM-6 and TOM-12 are one family (he calls the break-in "variant one for a breakout"); read them together.
- Example chart: `examples/TOM-6.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-7 Range scalp around the day's average price (Tom)
- What you see on the chart: VWAP [volume-weighted average price of the day] is flat, so no trend day. Price swings in a range around it: short near the top, long near the bottom.
- Rule in one breath: WHEN VWAP is flat and the day is not trending (SOURCED: 43JaKHRvxHk) THEN short the top and buy the bottom of the range (SOURCED: 43JaKHRvxHk; trigger NOT STATED) STOP NOT STATED (he asks "where do I give up on my trade?" and does not answer) TARGET VWAP, a "modest" target (SOURCED: 43JaKHRvxHk). OURS: where VWAP is anchored on BTC; the old engine's scalp rules.
- His exact words:
  - "keep looking for shorts at the top and keep looking for longs at the bottom" (43JaKHRvxHk)
  - "where do I have to set my stop loss? So, where do I give up on my trade?" (43JaKHRvxHk)
- What BTC can show: YES. (The older BTC study notes it fits poorly for cost reasons: outside this catalogue.)
- Evidence so far: 0 trades. No MTS backtest measured.
- Open gaps:
  - Stop, entry trigger and range definition NOT STATED.
  - A 1-minute scalp video (zAwEX_tRUfE) gives a target at the upper edge of yesterday's balance and says a last-1-minute-low stop gives a poor reward, but no numeric stop.
  - A 5-minute scalp video (vk0mkNPuhDc) is still unextracted (backlog).
- Example chart: `examples/TOM-7.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-8 Gap close (Tom)
- What you see on the chart: A stock or index opens far from yesterday's close. After the open the push fails, price settles into a range, then leaves it with volume rising again. Price then trades back into the gap, toward yesterday's value.
- Rule in one breath: WHEN a cash-session gap with no big news behind it, the extension fails, a range forms and price leaves it with liquidity [trading activity] returning (SOURCED: 96iPFDpXEcU, lO-Iptd29t4) THEN trade toward the gap close (SOURCED: 96iPFDpXEcU; the buy signal NOT STATED) STOP NOT STATED (30 points in one frame is a ledger value, not his rule) TARGET prior value (SOURCED: UOBgXV20yCM).
- His exact words:
  - "So, stop with this nonsense that you can always assume gaps will be closed." (lO-Iptd29t4)
  - "Here was the value. That was me profit target" (UOBgXV20yCM)
- What BTC can show: NO. BTC trades 24/7, so there are no session gaps.
- Evidence so far: 1 trade (TL T4, a DAX future long; same as ANG R12). No MTS backtest measured.
- Open gaps:
  - Stop and entry trigger NOT STATED; only one trade.
  - He says intraday gaps in the footprint were closed in over 95% of cases but "stop using the strategy" now (lO-Iptd29t4).
  - Political gaps close, big-news gaps and breakaway gaps often do not.
- Example chart: `examples/TOM-8.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-9 Gap stays open: trade with the trend (Tom)
- What you see on the chart: A gap above the whole previous day, with volume building at the new, higher prices (a P shape [profile bulging at the top]). People betting on a gap close were wrong. The market holds the new range.
- Rule in one breath: WHEN a gap holds, prices are accepted there and liquidity returns without closing the gap (SOURCED: 96iPFDpXEcU, lO-Iptd29t4) THEN trade in the direction of the trend "using the corresponding structures available to you" (SOURCED: lO-Iptd29t4; no setup named) STOP NOT STATED TARGET NOT STATED.
- His exact words:
  - "Then you are allowed to trade in the direction of the trend here using the corresponding structures available to you."  (lO-Iptd29t4)
  - "It tells me that the people who speculated down here on gap closes were initially wrong." (YopZ5ZDmMFw)
- What BTC can show: NO (no gaps on BTC).
- Evidence so far: 0 trades. No MTS backtest measured.
- Open gaps:
  - Everything after "trade in the direction of the trend" is NOT STATED; it hands over to TOM-4 / TOM-6.
  - A true breakaway gap is not expected to close for a long time.
- Example chart: `examples/TOM-9.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-10 Closing-auction gap reversal (Tom)
- What you see on the chart: A stock or index closes very strong, with a big share of the day's volume printed in the closing auction [the single closing price match]. Next day it opens down and starts to reverse.
- Rule in one breath: WHEN the close is very strong with an extreme in the closing auction and the next day opens back in the red (SOURCED: DVZVE9rXGtU) THEN go short once the reversal starts (SOURCED: DVZVE9rXGtU; trigger NOT STATED) STOP NOT STATED TARGET back to the original value (SOURCED: catalogue note on GAP G23).
- His exact words:
  - "So, if the market closes really strong and the next day it goes back into the red, then it just makes sense to take a contrarian position."  (DVZVE9rXGtU)
- What BTC can show: NO (no closing auction on BTC).
- Evidence so far: 0 trades. No MTS backtest measured.
- Open gaps:
  - All execution fields (entry, stop, management) NOT STATED.
  - One video only.
- Example chart: `examples/TOM-10.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-11 Crude oil leads, index future follows (Tom)
- What you see on the chart: Two charts side by side: crude oil and the S&P future. A level is hit in crude oil and crude reacts for some seconds. The index future follows a little later, so you enter it early.
- Rule in one breath: WHEN a level is reached in crude oil and crude reacts for seconds (SOURCED: YYYuaetck_0) THEN trade the index future in that direction, before its own breakout (SOURCED: YYYuaetck_0) STOP NOT STATED TARGET the index's last reference level (SOURCED: YYYuaetck_0). A BTC version (e.g. BTC against ETH) would be OURS.
- His exact words:
  - "And this is the way that I use informations for me that I have a lot of seconds reactions before in crude oil and after it in index futures." (YYYuaetck_0)
  - "And I'm going long earlier than the breakout is coming." (YYYuaetck_0)
- What BTC can show: NO. Crude oil and index futures are not on disk, and the lead is a matter of seconds.
- Evidence so far: 0 dated trades (chart illustrations only). No MTS backtest measured.
- Open gaps:
  - Stop, target type, how big the crude reaction must be: NOT STATED.
  - One video, one market regime (war and oil); whether it works elsewhere is NOT STATED.
- Example chart: `examples/TOM-11.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-12 Break-in: price falls back into the old range (Tom)
- What you see on the chart: Price went outside the old balance with a P above or a B below [profile shapes bulging at top or bottom], but with no volume base under those prices. Then it drops back inside the old value area fast. People who entered outside are now underwater.
- Rule in one breath: WHEN outside prices have no volume foundation and price re-enters the old value area with momentum (SOURCED: gFJBg8Bsw68, m3IMdc7QwN4) THEN enter the pullback, trading WITH the move back inside (SOURCED: gFJBg8Bsw68; trigger beyond "pullback" NOT STATED) STOP NOT STATED TARGET below the start of the outside impulse, then the next fair price area (SOURCED: jXR1afMy-3o, m3IMdc7QwN4).
- His exact words:
  - "And the moment it re-enters the value area here, very often strong momentum arises." (gFJBg8Bsw68)
  - "So, I know my next target is below the start of the impulse." (jXR1afMy-3o)
- What BTC can show: YES (old value area, P/B shapes, volume under the outside move, speed of the return).
- Evidence so far: 0 trades; weekly-chart examples only. No MTS backtest measured.
- Open gaps:
  - Stop, entry trigger, and how far inside price must close (his closing-price counting rule is "taught elsewhere") NOT STATED.
  - Same family as TOM-1a path 3, TOM-2 "lower balance" and TOM-6; listed apart because he names it a break-in.
- Example chart: `examples/TOM-12.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-14 After a news shock, trade back to where it started (Tom)
- What you see on the chart: A sudden news move with no base under it. Then a small pause (an inside bar [a candle within the previous candle]). Then price reacts the other way, often back to the origin of the shock. He calls these V reversals.
- Rule in one breath: WHEN a fast news move has no volume base and a small pause forms, and the reaction has started (SOURCED: 6BAzqewtPUk) THEN trade back toward the origin, never at the extreme (SOURCED: 6BAzqewtPUk; trigger NOT STATED) STOP NOT STATED TARGET the origin of the move (SOURCED: 6BAzqewtPUk). VIX level 20 as a mood filter is his (SOURCED: 15JoLK0PbMU); any BTC volatility gauge would be OURS.
- His exact words:
  - "After that comes the reaction upwards and very often such reactions go back to the origin of the alpha movement." (6BAzqewtPUk)
  - "when unpredictable movements occur, always wait to see what happens next. Does a V reversal follow or does a balance form?" (6BAzqewtPUk)
- What BTC can show: PARTIAL. Fast moves, inside bars and the origin are visible. Missing: the news itself (no news data) and VIX.
- Evidence so far: 0 trades; chart illustrations only. No MTS backtest measured.
- Open gaps:
  - Entry trigger, stop, how large a move counts as an overreaction, time frame: NOT STATED.
  - Close to TOM-1a (fade a push) and TOM-11 (news regime).
- Example chart: `examples/TOM-14.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-15 Candle patterns at a range edge (Tom)
- What you see on the chart: Near a support or resistance area after a squeeze, one of three candle shapes: three same-colour candles in a row; an inside bar after a big move [a candle within the previous one]; or an outside bar [a candle covering both sides of the previous one].
- Rule in one breath: WHEN the shape appears at a breakout level or support/resistance area after a real compression (SOURCED: 2xnNPIyHGQ4) THEN for an inside bar look for a reversal; after three in a row expect an extreme third move (SOURCED: 2xnNPIyHGQ4; trigger candle and price NOT STATED) STOP NOT STATED TARGET the next support or resistance area (SOURCED: 2xnNPIyHGQ4).
- His exact words:
  - "Three candlesticks of the same color in one direction." (2xnNPIyHGQ4)
  - "I should only look for it when a market is at a so-called breakout level." (2xnNPIyHGQ4)
- What BTC can show: YES (candles and volume at any time frame; the time frame is not fixed in the video).
- Evidence so far: 0 trades. He says the patterns can be back-tested but gives no results. No MTS backtest measured.
- Open gaps:
  - Time frame, trigger candle, stop, target distance, volume threshold: NOT STATED.
  - Overlaps TOM-6 in location; separate because the signal is the candle pattern.
- Example chart: `examples/TOM-15.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-16 Short a top built by forced hedger buying (Tom)
- What you see on the chart: Price far above its average, with volume far above average and traded at much higher prices. He says that volume comes from hedgers (industrial buyers forced to buy), not trader conviction. Then one aggressive seller appears and the hedgers who bought near the high are underwater.
- Rule in one breath: WHEN price and volume are far above average and an aggressive seller appears (SOURCED: cw8LWQmec1E) THEN short when price breaks below the level of the last big buyers (SOURCED: cw8LWQmec1E) STOP NOT STATED TARGET NOT STATED (the hedgers' entry area is the pressure zone, no price given).
- His exact words:
  - "This volume isn't created by us traders, but by so-called hedging transactions." (cw8LWQmec1E)
  - "Where were the last big buyers? And then you'll see when the market goes below that. Then the probability is high that sales will increase, and then you have the big short." (cw8LWQmec1E)
- What BTC can show: PARTIAL. Volume by price and the break below a large volume node are visible. Missing: the hedgers and expiry months (BTC perpetuals have no hedging buyers of this kind).
- Evidence so far: 0 trades; gold and silver chart illustrations. No MTS backtest measured.
- Open gaps:
  - Stop, target, how far above average counts, how large the volume must be: NOT STATED.
  - The hedging story fits commodity futures; fit to BTC is not shown.
- Example chart: `examples/TOM-16.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### TOM-17 Low-volume-zone scalp decided by trading speed (Tom)
- What you see on the chart: Price ticks into a price zone where little has traded. If it goes through, stalls and turns, it runs back to the high-volume area ("lethargic back and forth"). If it arrives at constant high speed with big players active, it keeps running.
- Rule in one breath: WHEN price enters a low-volume zone and either stalls (branch one) or keeps high speed with large participants (branch two) (SOURCED: G0CiJcuXCRs) THEN branch one: trade back toward the high volume; branch two: trade with the run (SOURCED: G0CiJcuXCRs; order type NOT STATED) STOP NOT STATED TARGET branch one: the nearest high-volume level (SOURCED: G0CiJcuXCRs).
- His exact words:
  - "Quite simply, it will run back to the high volume. That is lethargic back and forth scalping" (G0CiJcuXCRs)
  - "the market goes down here, reaches the low volume area and has a constantly high speed" (G0CiJcuXCRs)
- What BTC can show: PARTIAL. Volume by price and trade speed from the tape: YES. Missing: resting big orders in the order book (no history); "large vs small orders" only roughly (one tape row is not one order).
- Evidence so far: 0 trades (a teaching session). No MTS backtest measured.
- Open gaps:
  - Stop, target distance, the speed threshold, what counts as "low volume", entry order type: NOT STATED.
  - Not the same as TOM-7: here the trigger is tape speed. Closest cousin of the Fabio setups.
- Example chart: `examples/TOM-17.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

---

## Fabio setups

### FAB-1 Flat range, pressure builds, break on volume (Fabio)
- What you see on the chart: A flat range with a fair price in the middle. Inside it, CVD [running total of buyer minus seller volume] drifts hard one way while price stays flat. Then the first candle where price follows the volume out of the range, with big trades in that direction.
- Rule in one breath: WHEN the market is in balance, CVD pressure runs one way, and a range forms OUTSIDE yesterday's value area (not just an impulse) (SOURCED: 0jM5Y31YJak, 9IliXww64uM) THEN enter on the first candle with volume follow-up and price confirmation (SOURCED: 0jM5Y31YJak) STOP "here" on the chart, location NOT STATED in words (0jM5Y31YJak) TARGET no level; he exits when big trades stop pushing (SOURCED: 0jM5Y31YJak). OURS: all the BTC numbers (bar counts, percentile for "big trade", daily loss limits, tier sizes).
- His exact words:
  - "the first moment that we had some kind of follow up on volume and confirmation from price was exactly this candle."  (0jM5Y31YJak)
  - "I don't want to just see an impulse during the breakout." (9IliXww64uM)
- What BTC can show: PARTIAL. Balance, profile, CVD, follow-through candle: YES. "Big trades": only roughly (one tape row is not one order).
- Evidence so far: 1 assigned example (FL F2), plus ANG R26-R27 from the same session. No MTS backtest measured.
- Open gaps:
  - Initial stop and balance length NOT STATED. His NQ "big trade" size is 30 contracts (SOURCED, DyS79Eb92Ug); the BTC equivalent is OURS.
  - In a live Q&A he calls a momentum entry exactly at a resting-order wall "the worst case that you can have for a momentum trade" (Is1HvdfQm5c).
- Example chart: `examples/FAB-1.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### FAB-2 Big effort absorbed ("punch to the wall"), trade the other side (Fabio)
- What you see on the chart: One side pushes hard (big delta [buyer minus seller volume]) but price barely moves: "punching a wall". The other side then pushes and price does move. Variant: after a consolidation where one side was absorbed, the other side attacks that same level and breaks it.
- Rule in one breath: WHEN one side's aggression is absorbed (big delta, almost zero price result) and the other side gets the result (SOURCED: 0jM5Y31YJak, 8CWKfoSJu3c) THEN trade with the side that gets the result (SOURCED: 8CWKfoSJu3c; trigger bar NOT STATED) STOP NOT STATED in words (15.75 points in one frame is a ledger value) TARGET one far fixed target in one trade (1:19, 8CWKfoSJu3c), or flow exits; he trails behind the last point of aggression (SOURCED: 8CWKfoSJu3c). OURS: all the BTC thresholds (window, z-score, ratios).
- His exact words:
  - "the result of the price for a pressure in by delta was almost zero. So this is a confirmation that the buyers are punching a wall and I want to be short in this position."  (0jM5Y31YJak)
  - "I want to try uh good risk to reward trades and amazing risk to reward trades to take the top of the day." (fZlNGWvd2Ko)
- What BTC can show: PARTIAL. Delta against price result per bar: YES. Missing: "big trades" (rough only), the order-book "path of least resistance" (no history), dealer gamma (no options data).
- Evidence so far: 3 assigned examples (FL F1; F3c, F5). No MTS backtest measured.
- Open gaps:
  - "Failed auction" and "almost zero" have no mechanical definition; the ledger label of F1 mixes the two sides of this setup.
  - The older rule extraction lost which side was absorbed and turned a scratch plan into a break-even rule that contradicts another video.
  - In a live Q&A (Is1HvdfQm5c) he quotes a stop "above the area" and a 1 to 4.5 target; the number is an auto-caption number, to check on video frames.
- Example chart: `examples/FAB-2.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### FAB-4 Failed breakout back into yesterday's range (Fabio)
- What you see on the chart: Yesterday's value area [price band with 70% of volume] is his "area of comfort". Price pokes out, volume rises on the way out and again on the way back, delta [buyer minus seller volume] disagrees with the price move, and a 5-minute candle closes back inside. Price then runs to the other side of the range.
- Rule in one breath: WHEN price opens inside yesterday's value area, probes out, the absorbed side shows in the footprint [volume at each price], and the 5-minute candle closes back inside (SOURCED: 9IliXww64uM) THEN enter on that close, his "signal for the entry" (SOURCED: 9IliXww64uM) STOP "somewhere above here", a chart point only (SOURCED: 9IliXww64uM) TARGET the other side of the range (SOURCED: 9IliXww64uM). OURS: reclaim within 5 bars, stop beyond the probe extreme plus 1 tick, midnight-UTC "previous session", BTC big-trade size.
- His exact words:
  - "This is a clear failed auction. And that was exactly the second trade." (9IliXww64uM)
  - "Stop was likely somewhere above here, and we took profits around the beginning of this candle." (9IliXww64uM)
- What BTC can show: YES (value area, the probe, delta against price, volume in and out, the 5-minute close). The "previous session" boundary and big-trade size are OURS; "no relevant news" cannot be marked.
- Evidence so far: 2 assigned examples (FL F4a, F4b), weak: from screenshots, 1 lot, no visible stops. The video shows three trades. No MTS backtest measured.
- Open gaps:
  - Stop level, entry order type, how far a probe may go before it counts: NOT STATED.
  - Which ledger row is which trade is not re-checked.
  - In a live Q&A (Is1HvdfQm5c) he says "these are counter trend trade and I don't like to take them", so a reversal against the day's trend may be excluded.
- Example chart: `examples/FAB-4.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### FAB-5 Buyers defend a level: long (Fabio)
- What you see on the chart: Price drops to a level (value-area low [bottom of the 70% price band], a gap, or a big resting order wall). Sellers hit it several times and are absorbed each time. Buyers defend it, trapped sellers get squeezed, price rises. His names: "AAA setup", "value area low fade".
- Rule in one breath: WHEN price is at the defended level, selling is absorbed repeatedly, and the day's direction agrees (SOURCED: FawPrRUGNpk, DyS79Eb92Ug) THEN go long at the level (SOURCED: DyS79Eb92Ug) STOP small, just BELOW the level the buyers protect; no distance (SOURCED: DyS79Eb92Ug; his dollar risk of 1,500-2,000 is a session figure) TARGET a sell limit at a fixed distance in the ledger frames; rule NOT STATED. Re-entry allowed if it fails. OURS: nothing was added in the catalogue for this row.
- His exact words:
  - "I can have a really small stop loss here" (DyS79Eb92Ug)
  - "Okay, we are covered below the protection level for buyers in this case." (DyS79Eb92Ug)
- What BTC can show: PARTIAL. Value-area low and repeated absorption at a price: YES. Missing: the resting "protection wall" (no order-book history) and gap levels (BTC has none).
- Evidence so far: 11 assigned entry rows (FL F3a, F3b, F6-F14). Ledger outcomes: F6 target hit; F7 scratch; F8 stopped; F9 small win; F10 target hit; F11-F14 stopped. These come from his sessions, not an MTS backtest. No MTS backtest measured.
- Open gaps:
  - F11-F14 are labelled "chase long after squeeze above prior high"; whether they belong here or are breakout chases is NOT STATED.
  - Management contradicts itself: one video says adding low in the curve is not best, yet F7-F9 re-enter the same level three times in five minutes.
  - His live wall reading uses a heat map we do not hold.
- Example chart: `examples/FAB-5.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### FAB-6 First 30 minutes of the US open (Fabio)
- What you see on the chart: The range of the first 30 minutes of the US stock market open (the "initial balance"). Its bottom or top says which way the day leans; the trade is the break of that range.
- Rule in one breath: WHEN the first 30 minutes of the US cash open have set a high and low (SOURCED: StaphlRH8NQ, LQvv5xgy_ik) THEN trade the break of that range (OURS: V3 model C, break of the edge; no entry rule of his is quoted in the catalogue) STOP OURS: at the range midpoint plus 1 tick; the 2026-10-18 merge adds that he treats a candle close beyond the value area low as the invalidation and puts the stop below the protected area (cUTsoU-15Tc, not block-quoted in the catalogue) TARGET NOT STATED as a level; the merge cites a reward of 1:2 to 1:2.5.
- His exact words:
  - "the bottom of the first 30 minutes is giving a lot of value in the direction of the day" (LQvv5xgy_ik)
  - "The initial balance represent the high and low price established during the first 30 minutes of a regular cash trading" (StaphlRH8NQ)
- What BTC can show: PARTIAL. The 30-minute range is computable. Missing: the US equity open is not a BTC event; the 13:30 UTC mapping is OURS and may not carry over.
- Evidence so far: 0 trades. No MTS backtest measured.
- Open gaps:
  - Entry, stop in ticks, order type and the "protection level" (an unpublished tool) NOT STATED.
  - The catalogue's own FAB-6 fields 3 and 7 still say "all NOT STATED", older than the merge note under them.
  - The 13.5% and "positive skew" figures come from a rulebook line, only partly verified.
- Example chart: `examples/FAB-6.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

### FAB-8 Rejection at the thinnest-volume price of a swing (Fabio)
- What you see on the chart: Not the usual three-candle gap. Take a swing from A to B and draw its volume profile. Inside the value area [the 70% price band] find the price with the least volume. Price tends to reject there.
- Rule in one breath: WHEN a swing A-to-B has a value area with one lowest-volume price inside it (SOURCED: o-w5Gxss6T0) THEN expect a rejection there (SOURCED: o-w5Gxss6T0; entry order NOT STATED) STOP NOT STATED TARGET NOT STATED. OURS: swing selection, bin size and time frame (all UNDEFINED); "thousand of times" is his claim with no count.
- His exact words:
  - "to identify a real fair value gap, you need to get inside the candle and you need to see how the volume transacted."  (o-w5Gxss6T0)
  - "And what you will see thousand of times is that this is exactly where the price will reject." (o-w5Gxss6T0)
- What BTC can show: YES (swing profile and its lowest-volume price come from the tape).
- Evidence so far: 0 trades. No MTS backtest measured.
- Open gaps:
  - Entry order, stop, target and context all NOT STATED; the setup is mostly our structure around his one definition.
  - A different quote from a live Q&A (Is1HvdfQm5c) uses a plain candle gap ("micro gap"); catalogue says keep it as colour only.
- Example chart: `examples/FAB-8.png`
- Operator verdict: ____ (keep / rewrite / reject)   Pick to test: ____

---

## Verdict log

| date | setup | verdict | his words |
|---|---|---|---|
|  |  |  |  |

## Picks

| rank | setup | why (his words) |
|---|---|---|
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
