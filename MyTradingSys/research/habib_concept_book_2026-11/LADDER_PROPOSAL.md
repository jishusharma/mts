# Range ladder proposal (2026-11-07): fixed-risk ladder vs single buy vs martingale

**Proposal only. Nothing is built, no order is placed, testnet only, not trade advice. It is for the operator to decide.**

**Result: a fixed-risk ladder (total risk set first, split over 3-4 levels, one stop below the whole range) keeps the maximum loss equal to the risk you chose; a martingale on the same levels risks 2.1x that. The ladder gives away upside when the first level holds. Today's market is not a range by our own value-area test, so the ladder would wait.**

## 1. The three ways, side by side

| | Single buy (Habib's usual) | Fixed-risk ladder (proposed) | Martingale (double each lower level) |
|---|---|---|---|
| How | one entry at the planned level, one stop | 3-4 entries across the range, equal risk per rung, one common stop | each lower rung twice the size of the one above |
| Max loss | the risk you chose | **the risk you chose (by construction)** | grows with each rung: 2.1x the ladder total at 4 rungs, in the example below |
| Size of the stop | set by the structure, 0.08-1.43 % of price on his cards (`imbalance_qriptal_2026-10-16/discord/README.md:15`) | set by the range: below the whole range, wider on the first rung than on the last | same stop, much larger size at the bottom |
| When the first level holds | full position, best reward | small position, smaller reward | small position, smaller reward |
| When price falls through the level and then bounces | stopped, or frontrun and not filled ("frontrun" 13 lines of `habib_trading_thoughts.md`) | later rungs fill at better prices; average entry improves | biggest size at the best price: biggest win, and the biggest loss if the range breaks |
| When the range breaks | loses the chosen risk | loses the same chosen risk | loses up to 2.1x |
| In the sources read | his habit (`HABIB_CONCEPT_BOOK.md` 1.6) | not his: closest is "adds only in profit" (DISC:74) | not his: after a loss he cuts risk and caps the day ("if i get stopped again im done for the day", DISC:68-71) |

A true martingale (double the stake after each stopped trade) is worse than the rung version: stakes of 1, 2, 4, 8 units give losses of 25, 50, 100, 200 and a cumulative 375 after four stops in the example below, with each stop at leverage. Not recommended at any leverage.

## 2. Worked example on the current BTC range

Data: Binance spot BTCUSDT, 2026-11-06 20:18Z (the live-aid levels logic, `MyTradingSys/tools/live_aid/tf_strip.js:61-105`, run through `habib_common.py`). All numbers below are OURS; the account size is only an illustration.

| Input | Value | Source of the level |
|---|---|---|
| Last price | 75,827 | public klines |
| Prior-day range | 75,208 - 80,918 (width 5,710) | prior UTC day high and low |
| Prior-day POC / VAL / VAH | 76,000 / 75,300 / 79,650 | `tf_strip.js` value area (1m typical price, 50 USD bins, 70 %) |
| Today so far | low 74,888, high 76,416 | today's 1m bars: price has already swept 320 below the prior-day low |
| Total risk R | $100 (1 % of an illustrative $10,000 account) | OURS, chosen first |
| Rungs | 76,000 (prior POC), 75,736, 75,472, 75,208 (prior-day low): the POC-to-low distance in thirds | OURS |
| One invalidation | 74,637 = prior-day low minus 10 % of the range (571), 251 below today's sweep low | OURS: stop width comes from the range, not from a percentage of margin |
| Target for the comparison | 79,650 (prior VAH) | OURS |

Size per rung = (R / 4) / (rung price - stop) = $25 / distance:

| Rung | Price | Stop distance | Size (BTC) | Loss at the stop |
|---|---|---|---|---|
| 1 | 76,000 | 1,363 (1.79 %) | 0.01834 | $25 |
| 2 | 75,736 | 1,099 (1.45 %) | 0.02275 | $25 |
| 3 | 75,472 | 835 (1.11 %) | 0.02994 | $25 |
| 4 | 75,208 | 571 (0.76 %) | 0.04378 | $25 |

What each way does in four cases (same $100 total risk for the ladder and the single buy; martingale uses the ladder's first rung as its base unit):

| Case | Ladder | Single buy at 76,000 | Single buy at 75,208 | Martingale 1-2-4-8 |
|---|---|---|---|---|
| Rung 1 holds, price goes to 79,650 | +$67 (0.67 R) | +$268 (2.68 R) | not filled | +$67 |
| Price reaches rung 2, then bounces to 79,650 | +$156 (1.56 R) | +$268 | not filled | +$210 |
| Price reaches rung 4, then bounces to 79,650 | +$476 (4.76 R); average entry 75,508 | +$268 | +$778 (7.78 R) | +$1,169 (avg 75,402) |
| Price falls through everything to the stop 74,637 | **-$100** | -$100 | -$100 | **-$210** (all 4 rungs filled; -$127 after rung 3) |

Leverage: the loss at the stop in percent of margin is stop distance x leverage. At 25x the rungs lose 45 %, 36 %, 28 %, 19 % of their margin; at 50x they lose 90 %, 73 %, 56 %, 38 %, so only rung 4 fits his own "about 1 % stop at 50x is a 50 % loss" habit (`HABIB_CONCEPT_BOOK.md` 1.6) and rung 1 would sit near liquidation (roughly 1/leverage minus maintenance margin: OURS, check the exchange's own figure). Leverage only changes margin, not the loss: with all rungs filled the notional is $8,669, which is $347 of margin at 25x or $173 at 50x.

## 3. Phase check: why the ladder waits today

The ladder belongs to a range phase. By the auction rule (balance = successive value areas overlap, imbalance = they migrate; [LuxAlgo: Balance vs Imbalance](https://www.luxalgo.com/library/concept/balance-vs-imbalance/)): the POC moved from 80,650 (day before) to 76,000 (prior day), a 4,650 drop (5.8 %), and today's low is below the prior-day low. That reads as a trend/imbalance day, not a range. Buying a "range" here is catching a falling market; Habib's own rule agrees ("a wick and a reaction first", `HABIB_CONCEPT_BOOK.md` 1.4) and so does the large-body veto for the 4h candle of 11-05 12:00 (`habib_watch.py`, rv 4.7, large body).

| Phase read | Tool | Rule |
|---|---|---|
| Range (value areas overlap, POC flat) | fixed-risk ladder | rungs from prior POC down to the prior-day low, one stop below the range |
| Trend (POC migrates, large-body volume candles) | add only in profit (Fabio / Habib) | below |

## 4. Fabio's counterpart for the trend phase: add in profit

| Rule | Evidence |
|---|---|
| Move to break-even fast, add on confirmation, trail | "Management is the edge. Breakeven fast, pyramid on confirmation, trail behind S6" `research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md:49` |
| Scale in only after risk is zero, at most 3 adds | `research/fast_track_2026-09-27/ANGLE_TRADER_SOURCES.md:54` (our v3 spec, stricter than the source, `FABIO_V3_SPEC.md:137-141`); minimum add 0.25 x initial size is OURS (`LAYER_PARAM_LABELS_G1.md:74`) |
| In his ledger | stop tightened above the average entry, then scale-in from 6 to 18 lots, held through a pullback `research/fabio_transfer/FABIO_TRADE_LEDGER.md:36` |
| Habib does the same on his Discord | "added a bit to my short today while SL remains at entry" `DISC:74` |

Max loss on an add-in-profit trade is the first stop only; each add is placed after the stop is at or beyond entry, so the add cannot turn a winner into a loser. That is the structural opposite of a ladder (adds below the entry, risk first) and of a martingale (adds below the entry, risk doubled).

## 5. What the operator decides

| # | Decision | My default if you say nothing |
|---|---|---|
| 1 | Is a range ladder worth a testnet run at all, given today reads as a trend day? | wait for a day when the prior POC and today's POC are within 0.5 % of each other; nothing is built |
| 2 | If yes: total risk R per ladder and number of rungs (3 or 4) | 1 % of the testnet account, 4 rungs, one stop below the range |
| 3 | Do we write the ladder as a pattern for the pattern book (`pattern-book` session) with this proposal as the spec? | no, until 1 is a yes |

## 6. Limits

- One snapshot (2026-11-06 20:18Z). The prior-day levels change at 00:00Z; recompute with `python MyTradingSys/research/habib_concept_book_2026-11/habib_watch.py`.
- The target, the rungs, the stop buffer (10 % of range) and the $10,000 account are OURS and illustrative. The arithmetic is exact for the stated inputs and comes from a hand-checkable formula (size = $25 / distance).
- No fill model: rungs are assumed filled at their price, no slippage, no fees (fee 10 bp round trip would cost $1-$9 on these notionals, `MyTradingSys/backtest/fees.py` BINANCE_TAKER 0.0005 per side), no funding.
- Not tested against history: by the method of 2026-11-06 (`OPERATOR_DECISIONS.md:1812`) a pattern valid in the current phase goes to testnet and runs until it fails; this document says when it would be valid, not that it works.
