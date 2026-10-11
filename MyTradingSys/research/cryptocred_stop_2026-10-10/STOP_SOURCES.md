# CryptoCred stop placement - source hunt (D20/B143)

Date: 2026-10-10 UTC. Session: MTS-2026-10-10-1405Z-DSA-COO.
Source files: extracts/processed/cryptocred/*.md (repo root, not MyTradingSys/extracts).
Video ids: XeQV2ECtZVQ, _ndAoizXy64, Yp0k8HD5xro, BHwoN7VPrBE, inqHN8q57X4.

Operator note driving this: the 0.1% stop in cc_setups.py makes no sense.
Provenance rule forbids tuning an unsourced number, so hunt his words first.

## QUOTED STOP RULES (file:line)

### extract_XeQV2ECtZVQ.md - stop = invalidation
- L31 RULE 2 STOP PLACEMENT = INVALIDATION
- L33 "stop placement is inextricably linked with the trade idea itself your stop reflects your invalidation"
- L36 "if you dont know where to put a stop that often means the idea itself was not defined very clearly"
- L39 "would i want to buy where my long gets stopped out ... if the answer is yes then the trade sucks"
- L48 "strictness with stop usage and placement is inversely correlated with the size of the move"
- L51 "if youre being precise with the trade your stop placement should also be precise"
- L61 RULE 4 HARD STOP VS SOFT STOP
- L63 "hard stop ... market order to close the full position at a certain price"
- L66 "soft stop ... mental stop ... suitable for swing trades and less precise ideas"
- L78 position size = (Portfolio x Risk%) / Distance to Invalidation
- L151 RULE 10 BREAK-EVEN STOPS ARE PSYCHOLOGICAL COPE

### extract__ndAoizXy64.md - trailing vs fixed, anti break-even
- L124 RULE 7 PROFIT TAKING - TRAILING STOPS VS FIXED TARGETS
- L126 "you can trade and never take profit and instead continually move your stop as the market moves"
- L129 "a trend following system in a trending market ... trailing stops"
- L138 "trailing stops under swing lows for trending; fixed at range boundaries/ATR for ranging"
- L160 RULE 9 SKEPTICISM OF AUTOMATIC BREAK-EVEN STOPS
- L165 "the risk doesnt become risk-free ... the risk becomes getting stopped out while still being right"

### extract_Yp0k8HD5xro.md - break-even on first reaction is the graveyard
- L161 RULE 11 SWING TRADE GRAVEYARD - BREAK-EVEN ON FIRST REACTION
- L162 "you get involved at the trade at the level the market moves in your favor ... moves to break-even"
- L165 "I generally almost never encourage swing traders to move their stop on the very first reaction"

### extract_BHwoN7VPrBE.md - what a swing point is (the stop anchor)
- L11 RULE 1 SWING HIGH/LOW QUALITY FILTERS
- L12 "a swing low is a low with a higher low on both sides ... there is no single formula"

## WHAT THE QUOTES IMPLY FOR A STOP RULE

1. The stop is the trade invalidation point, not a fixed percent. For these setups
   the invalidation is the structural level being traded (broken SR level, fib zone edge,
   broken MSB level), so a stop just beyond that level is the source-consistent rule.
2. Precision scales with move size: a 1h structural setup wants a wider stop than a scalp.
3. No quote gives a numeric percent. 0.1% / 0.25% / 0.5% are OUR numbers, marked NO-SOURCE.


## NET R SWEEP RESULT (D20/B143) - 2026-10-11

Driver: backtest/layers/cryptocred/cc_stop_sweep.py. Data: raw_1m_2022 1h bars.
Metric: net_r after costs, and hit rate. Source column is the rule origin.

| setup | n | rule | src | net_r | hit |
|---|---|---|---|---|---|
| setup1_sr_flip | 1487 | pct_0.1 | NO-SOURCE | -1.069 | 0.373 |
| setup1_sr_flip | 1487 | pct_0.25 | NO-SOURCE | -0.386 | 0.406 |
| setup1_sr_flip | 1487 | pct_0.5 | NO-SOURCE | -0.174 | 0.411 |
| setup1_sr_flip | 1487 | atr_1.0 | CC-invalidation | -0.162 | 0.411 |
| setup1_sr_flip | 1487 | atr_1.5 | CC-invalidation | -0.095 | 0.421 |
| setup1_sr_flip | 1487 | atr_2.0 | CC-invalidation | -0.101 | 0.420 |
| setup2_fib_pullback | 1392 | pct_0.1 | NO-SOURCE | -1.307 | 0.306 |
| setup2_fib_pullback | 1392 | pct_0.5 | NO-SOURCE | -0.209 | 0.367 |
| setup2_fib_pullback | 1392 | atr_1.0 | CC-invalidation | -0.184 | 0.361 |
| setup2_fib_pullback | 1392 | atr_2.0 | CC-invalidation | -0.073 | 0.405 |
| setup3_failed_msb_reversal | 167 | pct_0.1 | NO-SOURCE | -1.050 | 0.317 |
| setup3_failed_msb_reversal | 167 | pct_0.5 | NO-SOURCE | -0.272 | 0.305 |
| setup3_failed_msb_reversal | 167 | atr_1.0 | CC-invalidation | -0.217 | 0.329 |
| setup3_failed_msb_reversal | 167 | atr_2.0 | CC-invalidation | -0.040 | 0.371 |

Conclusion: every stop rule is net-negative on all three setups. Stop placement
alone does not make a CryptoCred entry profitable. The widest ATR stop is least bad
in each setup; the NO-SOURCE 0.1 percent stop is worst everywhere, which matches the
operator note that drove this hunt. The fix is not a stop number: the entry needs a
separate edge before stop tuning matters. Source hunt found no numeric percent in his
words; the source-consistent rule is the structural invalidation level, per the quotes
above.
