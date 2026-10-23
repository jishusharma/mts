# RULES_DIGEST: Tom and Fabio, SOURCED quotes only (Fable run 4 pack)

Every quote below was machine-checked as a substring of the cited file:line when this file was built
(`build/build_digest.py`). Files are under `MyTradingSys/` (`research/...`, `system/LAYERS.md`).
Tom's words are AI-translated captions: a quote proves what he says he looks at, never a price or a threshold.
Where a rule needs a number the source does not give, that number is OURS in your setup and you must say so.
Quotes about 1m order flow, L2 or footprint cannot be used as such: the pack has 4h/12h/1d/1w bars, taker buy
volume and the level tables only (README).

## TOM

### Balance and value
- "where the market is in balance, everyone is satisfied. And where the market is out of balance, there is often dissatisfaction among the big players." (TOM_VERBATIM_INDEX.md:43)
- "when supply and demand are balanced, the market will always try to return to that equilibrium." (TOM_VERBATIM_INDEX.md:44)
- "balance profile means the probability is high for now that the market will repeatedly try to play in balance." (TOM_VERBATIM_INDEX.md:46)
- "if you see that a market has spent a lot of time at a certain price range, the probability is relatively high that a lot of trades have also taken place there." (TOM_VERBATIM_INDEX.md:48)
- "markets are only about 30% truly stably trending. And about 70% they're just not." (TOM_VERBATIM_INDEX.md:59)
- "when such a balance profile comes after a strong trend, then it means the market is starting to sort itself out." (TOM_VERBATIM_INDEX.md:71)

### Weekly POC and value trend (HTF context)
- "The weekly profiles show me immediately if the V POX are rising, staying the same or even falling" (TOM_VERBATIM_INDEX.md:54)
- "try drawing a trend based only on the V POX and the value areas and you'll find that you can immediately see if a market is flattening out in terms of global money flow or not." (TOM_VERBATIM_INDEX.md:66)
- "Where are we in balance or are we currently in an active aggressive trend?" (TOM_VERBATIM_INDEX.md:77)
- "Whether it's trend or balance because I have to use different setups there and that is absolutely crucial." (TOM_VERBATIM_INDEX.md:78)
- "we are of course above the previous day. That means it's a very risky trade" (TOM_LAYER_V2_SPEC.md:60)
- "we're above last week's value" (TOM_LAYER_V2_SPEC.md:60)

### Rejection, acceptance, targets at value
- "The market showed me that there is rejection up here. And the market also showed me that the speed with which it rejected this is promising for me." (TOM_VERBATIM_INDEX.md:23)
- "if it accepts new prices, then it looks for the next high volume price and that is your target." (TOM_VERBATIM_INDEX.md:31)
- "Not with quick spikes but with real acceptance." (TOM_VERBATIM_INDEX.md:32)
- "When there are high volumes at the tops or lows, the auctions are very often not yet finished, not yet completed." (TOM_VERBATIM_INDEX.md:26)
- "this is the price range where the market was in equilibrium and where I then simply expect a reaction could occur" (TOM_LAYER_V2_SPEC.md:102)
- "we'll take out the entire distance below the start of the impulse" (TOM_LAYER_V2_SPEC.md:101)
- "if the market were to accumulate large volumes there then yes I would definitely be looking for a long position" (TOM_LAYER_V2_SPEC.md:138)
- "these price areas are zones with very low volume for the respective time frame we're looking at. And the market often bounces off these areas." (SOURCED_RULES.md:16)
- "this trend isn't entirely healthy." (SOURCED_RULES.md:21)
- "if something is very narrow, but liquidity is the same as in the previous days, then the probability at a later point in time is much greater that the market will trend." (SOURCED_RULES.md:24)

### Stops, risk, hit rate (Tom's own arithmetic)
- "my stop loss belongs below the last liquidity." (TOM_VERBATIM_INDEX.md:85)
- "even with a hit rate of 30 to 40% you have an average riskreward ratio of greater than three" (TOM_VERBATIM_INDEX.md:104)
- "have a hit rate somewhere in the range of 40 to 45% with such counter trading" (TOM_LAYER_V2_SPEC.md:27)
- "my stop loss is immediately above the 258" (TOM_LAYER_V2_SPEC.md:93)
- "such counter trades, they often get stopped out again" (TOM_LAYER_V2_SPEC.md:134)
- "Trailing the stop loss is something a lot of people like to do. In this case, I don't do that" (TOM_LAYER_V2_SPEC.md:112)

### Method order
- "how we connect the dynamic context and then use the order flow to get the timing right." (SOURCED_RULES.md:23)
- "First, you have an idea. Second, you have proof that it's really time now to implement" (TOM_LAYER_V2_SPEC.md:52)

## FABIO

### Fabio model (FM lines are the supervisor's reading; quoted words are Fabio's)
- "if these aggressive buyers take back control, I want to be out" (FABIO_TRADE_MODEL.md:26)
- "redistribution" (FABIO_TRADE_MODEL.md:24)
- "risking again the profit" (FABIO_TRADE_MODEL.md:20)
- "last point of aggression/break" (FABIO_TRADE_MODEL.md:21)
- "see what the CVD is telling us" (SOURCED_RULES.md:28)
- "reaching the value area low" (SOURCED_RULES.md:28)

### Fabio rulebook lines (rule text, FR-nn; class and data need are in the file)
- "Absorption: delta in, price flat; CVD divergence; heavy absorption" (FABIO_RULEBOOK.md:20)
- "Absorption + reload = sustained move / entry" (FABIO_RULEBOOK.md:21)
- "First entry on volume plus price confirmation" (FABIO_RULEBOOK.md:15)
- "Exit when big trades stop pushing / get stopped out" (FABIO_RULEBOOK.md:19)
- "No counter-trend long while CVD is falling" (FABIO_RULEBOOK.md:70)
- "Flat CVD while price rises = no buyer aggression" (FABIO_RULEBOOK.md:74)
- "Price above VWAP +1 SD = buyers in control" (FABIO_RULEBOOK.md:66)
- "Do not trend-follow on compression days" (FABIO_RULEBOOK.md:95)
- "Do not cut profit early on choppy days" (FABIO_RULEBOOK.md:94)
- "Minimum 1:3 reward-to-risk on initial trades" (FABIO_RULEBOOK.md:17)
- "Price rejects at the volume-defined FVG" (FABIO_RULEBOOK.md:100)
- "is proprietary/undefined" (FABIO_RULEBOOK.md:150)
- "has no numeric threshold." (FABIO_RULEBOOK.md:151)
- "has no numeric threshold." (FABIO_RULEBOOK.md:152)

## What already failed (system/LAYERS.md; do not re-propose, or say what is different)

| Item | Result (verbatim) | file:line |
|---|---|---|
| tom_core: stopped, being redefined | STOP: do not backtest or tune the current BTC encoding | LAYERS.md:13 |
| TOM-CORE-0929 | no edge: gross -0.07 R, net -0.30 R, holdout net -0.32 R (n=254) | LAYERS.md:23 |
| TOM-CORE-1007 | no edge: gross -0.15 R, net -2.91 R; holdout -2.80 R | LAYERS.md:21 |
| tom_vp_pivot (VP anchors) | closed: no anchor beats placebo | LAYERS.md:15 |
| TOM-VP-PHASE2 | no anchor has an edge; 46/48 real-minus-placebo CIs straddle 0; every year negative | LAYERS.md:19 |
| VP-PIVOT-P2 | negative net R; no level beats placebo | LAYERS.md:20 |
| Fabio v3 | OOS FAIL (only model C evaluable, 79 trades, mean -0.1038R) | LAYERS.md:43 |
| fabio_cvd_absorption | L1 no edge / insufficient n | LAYERS.md:45 |
| fabio_escalation | L1 no edge / insufficient n | LAYERS.md:46 |
| FABIO-OF | no edge / insufficient n (stands under correct fees | LAYERS.md:53 |
| PRICE-CVD-DIV-1M5M | NEGATIVE: CVD divergence adds nothing over price alone on 1m/5m | LAYERS.md:51 |

In words: TOM-CORE net -0.30 R (-2.91 R on the rerun); VP anchors (a plain touch of a VP level) show no edge over
placebo; Fabio v3 OOS -0.10 R; CVD divergence adds nothing over price alone on 1m/5m.

## NO-SOURCE list (never present these as Tom or Fabio)

- Bollinger bands as a trigger or level | NO-SOURCE (SOURCED_RULES.md:43)
- Every numeric threshold (percentiles, windows, 1.5x volume) | NO-SOURCE (SOURCED_RULES.md:48)
- RSI(14) and the 40-60 regime | NO-SOURCE for Tom and Fabio (SOURCED_RULES.md:44)

## Cost and R

- Round trip cost in this pack: 14 bp (README). R cost of a trade = 14 bp / stop distance in percent.
- Tom's own arithmetic: hit rate 40-45 % needs RR >= 1.5 (TOM_LAYER_V2_SPEC.md:27 above); on BTC a stop of 0.25 %
  of price already costs 0.14/0.25 = 0.56 R, so tight stops cannot pass by arithmetic.
