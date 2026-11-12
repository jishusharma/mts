# Order-flow extract: Fabio Valentini live Nasdaq session on a podcast (`DyS79Eb92Ug`)

- **Video ID:** `DyS79Eb92Ug`
- **Analyst:** Fabio Valentini live session with a podcast host (Nasdaq futures; only Fabio's own lines quoted)
- **Source:** `raw_transcripts_canonical/DyS79Eb92Ug_raw.txt` (on disk, no network; position = third of transcript)
- **Scope:** order-flow idea only (who is forced, where size trades, absorption, auction); index-futures clocks are not BTC rules (OPERATOR_DECISIONS 2026-11-12)
- **Labels:** SOURCED = verbatim quote verified by `scripts/dev/verify_extract_quotes.py`; OURS = our reading, no quote

## Rules

### R1. Who is winning the battle (SOURCED)

Rule: The read is which side is winning at a level, not volume or price in isolation.

> "it's not about volume, it's not about price, it's about who is winning the battle"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R2. Absorption seen with big trades (SOURCED)

Rule: Large prints that hit a level without moving it mean the aggressor is hitting a wall (absorption).

> "How can we see absorption? As I explained to you big trades it means they are hitting a wall"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R3. Do not trade against a breaching flow (SOURCED)

Rule: If the flow is breaching a level, no long there; cancel the pending order and use the next area.

> "So I don't want to go against the flow if they are managing to breach this level"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R4. Point of control as maximum-interest area (SOURCED)

Rule: The highest-volume price inside the value area low marks the point of maximum interest for the accumulation behind the prior move; it is the second candidate area.

> "So where the most volume got exchanged in the value area low. So basically is giving me the point of maximum interest for the accumulation that created this up movement"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R5. Broken area ends the bias (SOURCED)

Rule: If the high-volume area breaks, the directional bias for the day is dropped (consolidation expected).

> "If this area gets broken, I don't want to be long for the day"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R6. Do not fight a gap's pressure (SOURCED)

Rule: A setup against a large opposing move (gap pressure) is inconvenient; absorption must show first.

> "this gap is not really convenient for us to trade because we are trading against this huge pressure"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R7. Aggressive buyers at the top mean squeeze (SOURCED)

Rule: Buyers lifting at the top of a move are willing to pay up; expect continuation and a squeeze.

> "If the buyers are aggressive on the top, it means that they are willing to pay a higher price to get an asset. So I can expect a continuation and squeeze"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R8. Forced closing of the absorbed side (SOURCED)

Rule: Where aggressive sellers are absorbed and then must close, the closing buys power an expansion higher.

> "If sellers needs to close, we have a an expansion higher"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R9. Stop goes beyond the aggressive side (SOURCED)

Rule: Cover the position just beyond the aggressive counter-side's level, not at an arbitrary distance.

> "Where can we cover ourself? Below the aggressive sellers"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R10. Failed auction means the buyers are weak (SOURCED)

Rule: If the auction fails after entry, stay out: the move lacks strong buyers.

> "I don't want to be in because it means that the buyers are not strong"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R11. Trade low on the curve on absorption (SOURCED)

Rule: The preferred long is low in the range, at the value area low, on absorption.

> "This is simply a trade that is done low on the curve on absorption"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R12. Wait for the winner to win another round (SOURCED)

Rule: Do not bet on a side in a contested two-sided fight; enter only after that side wins another round (probability rises).

> "I want to place a bet if you win another round. Why? Because my probability gets higher"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R13. After an expansion, wait (elastic band) (SOURCED)

Rule: After a strong expansion move the market needs time to reset before the next throw; setups right after it are weaker.

> "Now like you had the expansion now. It's like an elastic band. You cannot only throw. You need time to get it back to normal state"
**Source GPS: DyS79Eb92Ug | MIDDLE**

### R14. Take protected trades only (SOURCED)

Rule: Takes a trade only when it is protected by resting size (a buy wall). Resting size needs L2 history, absent from public Binance data.

> "I'm not taking a trade that is not protected. I'm taking a trade that is protected by a buy wall"
**Source GPS: DyS79Eb92Ug | MIDDLE**

### R15. Price action is the result, order flow the driver (SOURCED)

Rule: Candles are the impact; flow is what drives them.

> "price action is the impact and the result. Order flow is exactly what's driving the price"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R16. Big-trade threshold varies by session (SOURCED)

Rule: The bubble size filter differs with the session's activity (30 contracts in one session, 20 in another).

> "If you are in London, I use 20"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R17. Time bars clutter at spikes (SOURCED)

Rule: At opening-type spikes a one-minute bar aggregates all the data inside; a range (fixed-price-width) bar reads cleaner. For BTC this becomes a non-time-bar test.

> "if you do one minute candle you can have huge candle and all the data inside gets aggregated"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R18. Liquidity disappears on shocks (SOURCED)

Rule: On a shock headline market makers do not put risk in, liquidity disappears and price melts.

> "liquidity completely disappear because they don't want to input risk here so the price melt"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R19. Leveraged crypto: slippage on shocks (SOURCED)

Rule: On shock days leveraged crypto can slip or not fill at the intended level.

> "specifically if you are leverage on crypto because you can get slippage you can get not filled at the level that you want"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R20. Hold-to-target hurts in contraction days (SOURCED)

Rule: Shooting for very high reward-to-risk is destroyed on contraction days; he prefers consistent smaller days and a lower win rate (43 to 49 percent, his own stat, not adopted).

> "if you shoot for high riskto-reward you will be completely destroyed in contraction day"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R21. Wrong fast (SOURCED)

Rule: Losses must be contained so that losers are small relative to winners.

> "making sure that when you are wrong, you are wrong fast"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R22. Manage by profit risk too (SOURCED)

Rule: Each open trade is judged by what unrealised profit is put at risk, not just by the stop.

> "I treat every trade not only from stop perspective but from profit perspective"
**Source GPS: DyS79Eb92Ug | BEGIN**

### R23. Order flow is not a magic tool (SOURCED)

Rule: Order flow alone does not make a profitable trader.

> "it's not a magic tool"
**Source GPS: DyS79Eb92Ug | BEGIN**

## OURS (no quote)

- Idea kept for BTC (OURS): per-trade profit-risk management and confirmation entries are testable only as rules on public data; absorption plus failed breakout use the same aggTrade test as the sister video.
- DECISION (OURS): host lines (sponsor, intro, anecdotes), dollar figures, the 43-49 percent win rate and the VWAP-deviation claim, 0DTE options sentiment, and the buy-wall resting-size claims (need L2 history) were not adopted as parameters. The tweet-shock day is a news-shock example only.
- DECISION (OURS): captions carry no speaker labels; only first-person trading lines were quoted.
