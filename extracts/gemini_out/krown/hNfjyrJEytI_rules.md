# Krown Video Rules Extract - hNfjyrJEytI

- URL: https://www.youtube.com/watch?v=hNfjyrJEytI
- Title: Most Traders Do Technical Analysis in the Wrong Order. Here's the Fix.
- Upload Date: 2026-07-26

## Trading Rules Stated (SOURCED)

### 1. Framework Sequence & Hierarchy (Setup / Process)
- SOURCED: "whenever I'm considering to make a trade or a new investment decision, there are four layers of a framework, a very specific framework that I go through before ever risking a single dollar." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 00:19)
- SOURCED: "the first layer, the most important layer, absolutely in my opinion... it is absolutely 100% trend." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 01:57 - 02:05)
- SOURCED: "Number one, trend tells you where or which direction. Two, volatility tells you when. And three, structure tells you about how things are likely to evolve from there, if they're actually changing. And then four is going to be momentum." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 10:38 - 10:50)
- Comparison with `krown_params.json`: MATCH. The parameter specification and layer architecture reflect this exact hierarchy: trend moving averages (`ma_fast`, `ma_slow`, `ma_long`), volatility (`bbwp_basis`, `bbwp_lookback`, `bbwp_high`, `bbwp_low`), structure (`zone_k`, `range_n`, `swing_tol`), and momentum (`rsi_period`, `rsi_bull`, `rsi_bear`).

### 2. Timeframe Dominance Hierarchy (Timeframe / Filter)
- SOURCED: "higher term time frames dominate lower term time frames. So, the reason why you kind of want to know what the dominant time frame trend is, like a weekly, in this case, it is to the downside is that your fiveminute trend while it is in an uptren while it is in an uptrend right here, it it's liable to fail at any moment because the weekly trend can just force things in that direction. It is stronger. In other words, it is stronger and it takes precedence." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 03:14 - 03:50)
- Comparison with `krown_params.json`: MATCH. Higher timeframe trend takes priority over lower timeframe tactical signals.

### 3. Volatility Compression and Exhaustion (Filter / Setup / Timing)
- SOURCED: "volatility is mean reverting. So when volatility is very high we can always assume that it is a mathematical certainty volatility will come down. However and just like that on the other side when volatility is very very low meaning that price is very boring very tight very close ranges you are very likely setting up for another major massive move." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 06:36 - 06:56)
- SOURCED: "Critical point. Once volatility is very very low and it starts to expand then we have a high probability of a continuation of the current trend" (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 07:46 - 07:54)
- SOURCED: "volatility spikes up over here, gets quite high. This was 89 percentile and then it forms a low. So when volatility gets very very high, you're probably near or at the end of your current trending move." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 07:18 - 07:28)
- SOURCED: "volatility once again gets very high in this case all the way up to 90 percentile and what do you know price action stalls there basically forming a low for a while" (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 17:18 - 17:28)
- Comparison with `krown_params.json`: MATCH. `bbwp_high` = 85 and `bbwp_low` = 30 directly match Krown's rules where low BBWP signals compression before expansion and high BBWP (~85-90th percentile) signals move exhaustion.

### 4. Structural Breakout Confirmation (Entry / Filter)
- SOURCED: "when we're talking about structure, all we're doing is we're marking off the range of a current consolidation. So in this case, we have range high and then over here, we have range low." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 08:54 - 09:04)
- SOURCED: "Whichever way that price closes above or below this range is likely the next major direction." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 09:18 - 09:24)
- SOURCED: "it did not close above that range. Thus, the structure remains intact. And what does this end up doing? It ends up forming a lower high. And then you get the real breakdown over here with Bitcoin closing below the lower range boundary." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 09:34 - 09:44)
- SOURCED: "Generally speaking, former range lows become new range highs." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 09:55 - 09:58)
- Comparison with `krown_params.json`: MATCH. `range_n`, `range_edge`, `confirm_horizon` enforce that boundaries are evaluated on a candle closing basis rather than wicks, and that former support flips to resistance.

### 5. Trend Reversal Confirmation Rule (Setup / Entry)
- SOURCED: "a higher low is a prereic kicate to the trend shifting and changing, but it is not confirmed until you get a higher high. And how do we how do we define a higher high? Well, Bitcoin must break the structure of the last previous high, the rejective high right here... once Bitcoin reclaims that on a weekly closing basis or even a daily closing basis in this point, you have a confirmed trend reversal." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 18:16 - 18:38)
- Comparison with `krown_params.json`: MATCH. Reversals require a structural higher low followed by a confirmed closing break above the prior swing high pivot (`zone_k`, `confirm_horizon`).

### 6. Momentum Divergence Exhaustion (Filter / Setup)
- SOURCED: "When the RSI is making lower highs but price actually making higher highs. What does that tell you? Price is moving higher but the momentum is waning. And if the momentum is getting weaker while price goes higher, what should we expect? A counter move." (URL: https://www.youtube.com/watch?v=hNfjyrJEytI at 13:00 - 13:11)
- Comparison with `krown_params.json`: MATCH. RSI divergence is treated as a momentum exhaustion warning (`rsi_bull`, `rsi_bear`).

### 7. Stop and Position Sizing Rules
- NO STOP DISTANCE STATED: Invalidation is defined strictly by closing back inside the range or failing the higher low / lower high structure; no numerical stop loss distance or dollar buffer is provided.
- NO SIZING RULE STATED: Position sizing formula is not stated in this video.

## Notes (OURS)

- The video lays out Krown's core four-pillar methodology: Trend (direction) -> Volatility (timing) -> Structure (levels & confirmation) -> Momentum (divergences/exhaustion).
- Wicks across support/resistance do not confirm a breakout; a valid break requires a candle close outside the boundary.
- Volatility (BBWP) acts as a timing gate: enter on expansion following compression (low BBWP), and avoid chasing or take profit when BBWP reaches the 85-90th percentile exhaustion zone.
- Higher timeframe trends (weekly) strictly overrule lower timeframe counter-trends (5-minute/hourly).
