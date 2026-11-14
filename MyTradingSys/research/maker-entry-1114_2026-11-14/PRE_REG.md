# PRE_REG maker-entry-1114 (written before any maker-fill outcome was computed)

Question: do resting limit-order (maker) entries turn the near-miss ideas (gross about 0 to +0.10 R, slightly positive at 6 bp) into a fee-net pass, when the fill is modelled conservatively and missed fills are counted? Label: SOURCED = the original study's rule; OURS = our choice here.

## Context
Regime: per idea, the SAME phase gate the original study used (coin-day UP/DOWN/RANGE from daily ADX14 + MA20 slope at D-1 for NK2/NK3/NK5/NK6; balanced-day gate for the NY-value row; session gate for the sweep row). Primary rows = matched direction only. Unchanged from the originals, nothing re-tuned.
Phase: matched direction only (LONG in UP/RANGE, SHORT in DOWN/RANGE). Mismatched rows are controls, not gated.
Session: as in each original (NK5 NY open to 08:00 UTC hold; NY value row NY session; sweep row Europe-low sweep then US reclaim; NK2/NK3/NK6 all UTC hours).
Entry: a resting LIMIT order placed at the signal level after the signal bar closes (fill model below). Original rule triggers and parameters are frozen as in each original PRE_REG.

## The six rows (picked from the notes by best gross R; fixed here)
| Id | Idea | Original best row | Gross / net evidence | Limit level L |
|---|---|---|---|---|
| M1 | NK2 pivot reclaim | 1h SHORT-P | gross +0.101, 12bp -0.009, 6bp +0.046 | pivot P (the rejected level) |
| M2 | NK3 fakeout fade | 1h B, X1 target, no filter | 12bp -0.034, 6bp +0.030 | the broken level (the fakeout level) |
| M3 | NK6 confluence | L2&L3&L5 | gross +0.084, 12bp -0.112 | close of the signal bar (no level in the rule) |
| M4 | NK5 session open | NY-asia, hold to 08:00 UTC | 12bp +0.074, placebo p 0.000 | close of the signal bar |
| M5 | NY value area, POC target | edge5-ny-value-poc-target best cell | gross +0.077, 12bp -0.006 | the value-area edge the rule enters at |
| M6 | Europe-low sweep reclaim | edge-session-sweep-reclaim best maker cell | maker +0.105, taker -0.23 to -0.32 | the swept low being reclaimed |
If an original's code or best row cannot be found, the row is reported BLOCKED with the reason, never swapped silently; the next-best gross row from COMBO/EDGE_POSTMORTEM may replace it only with that stated in RESULT.

## Fill model (conservative, fixed, applies to the study AND the placebo)
| Item | Rule | Label |
|---|---|---|
| Signal | exactly the original rule, evaluated at bar close; no look-ahead | SOURCED |
| Order | limit at L (long = buy at L, short = sell at L); placed at the signal bar close | OURS |
| Fill | filled only if a 1m bar AFTER the signal bar trades THROUGH L by at least one tick (long: 1m low <= L - tick; short: 1m high >= L + tick). Touching L exactly is NOT a fill. Fill price = L (never better). If the next 1m opens already through L, fill at L. | OURS |
| Tick | smallest nonzero price increment observed in that symbol's 1m data | OURS |
| Order life | one entry-timeframe bar after the signal bar (60 x 1m for 1h; 15 x 1m for 15m); then cancelled, counted as a missed fill | OURS |
| Cancel | if the original stop price trades before the fill, the order is cancelled, counted as missed | OURS |
| After fill | original stop, target and time stop, evaluated on 1m bars from the fill bar. Stop and target are on a tick-through basis for the target (resting limit, needs one tick through); stop is a market stop (taker) at the stop price; same 1m bar touching both = stop wins; a close-basis stop (NK2) exits at the 1m close that confirms it | OURS |
| Same-bar fill + stop | a 1m bar that fills the entry may also stop it out (stop wins, pessimistic) | OURS |
| Missed fills | counted: reported as fill rate; per-signal mean R counts a miss as 0 R | OURS |

Fees (per side of the notional): taker 6 bp, maker 3 bp (12 bp taker round trip, 6 bp maker round trip, as the originals). Entry maker 3; target exit maker 3; stop exit taker 6; time exit taker 6. Fee in R = fee fraction x entry / stop distance.

## Reported per row (VALIDATION, and DEV for reference)
signals, fills, fill rate; net R per filled trade, taker baseline (the ORIGINAL next-open entry, 12 bp, all signals) and maker model; gross R; adverse selection = mean gross R of the ORIGINAL model over the filled subset minus over all signals, and mean net R filled vs mean net R of the taker baseline; net R per signal with misses = 0; regime mix per row.

## Universe and split
Same universe as each original (20 Binance spot USDT coins from 2019 for NK rows). 1m data fetched from public Binance archive (data.binance.vision) into F:\MTS\data_cache\binance_1m. DEV to 2023-12-31 (reported only, nothing tuned), VALIDATION from 2024-01-01.

## PASS gates (VALIDATION, maker net R per filled trade, per row)
1. filled n >= 100. 2. mean net R > 0. 3. bootstrap 95% CI lower > 0 per trade AND per UTC-day cluster (10000 / 5000, seed 7). 4. like-for-like placebo p < 0.05: random bars, same symbol, side, allowed phases and timeframe, VALIDATION period, same stop/target machinery, SAME fill model, with the limit placed at the signal bar close shifted by an offset drawn from the empirical distribution of the real signals' (L - close) in ATR units; 1000 draws at the same filled n; p = (1+#random >= observed)/1001. 5. Benjamini-Hochberg q=0.05 over the 6 rows' placebo p. 6. mean net R > 0 after removing the 5 highest-R UTC days. PASS only if all six; else FAIL naming the gates. A row is also flagged THIN when fill rate < 30% (selection dominates).

## Independent checker (per row, adversarial)
Checks: fill logic cannot fill on a touch, never fills at a better price, uses only bars after the signal; fee by exit type; DEV/VAL split by signal bar; replication of the original taker baseline within tolerance of the original RESULT; placebo uses the same fill code; look-ahead by truncation test. Flags go in RESULT; a checker CONFIRMED-BUG overrides the row to INVALID until fixed.

## Not done
No forecast, no trades, no testnet orders, no live-tree touch.
