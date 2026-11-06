# Blind read: wall_ledger_2026-11 (Gemini-lane worker, independent of producer)

Method: read only `RESULT.md` Rule + Parameters (THRESHOLD 1.5M, GRID 10, PERSIST 3; all OURS-adopted per RESULT.md Parameters table), then the fixtures in `test_wall_ledger.py`; derived expected rows by hand BEFORE opening `wall_ledger.py` (never opened it; only ran pytest after writing the derivations: 15 passed, OURS command output).
Base book (test_wall_ledger.py:20-21): bid 20 BTC x 99,500 = 1,990,000 USD >= 1.5M (wall); 1 BTC x 99,990 = 99,990 (not). ask 30 x 101,000 = 3,030,000 (wall); 1 x 100,010 small. Best bid 99,990, best ask 100,010, mid 100,000 (mid = (bestbid+bestask)/2 is my reading; RESULT.md says "mid" without defining it).

## Per-fixture derivation (rule only) vs test assert
| # | Fixture (test line) | Hand-derived expected | Test assert | Match |
|---|---|---|---|---|
| 1 | placed_wall_open_with_distance_and_age (:60) ts 0,5,10,20 base book | Both walls seen 4 snaps >= PERSIST 3 -> placed_ts=0 (first seen), never vanish -> open; bid age_s=20-0=20; bid distance=(99,500-100,000)/100,000x100=-0.5; ask distance=(101,000-100,000)/100,000x100=+1.0 | outcome open, placed_ts 0, age_s 20, dist -0.5, ask dist 1.0 (:60-70) | MATCH |
| 2 | pulled_without_trades_and_untouched (:72) base ts 0,1,2; ts3 bid wall removed | Placed at 0 (3 consecutive by ts2); at ts3 cell < threshold, no trades -> pulled; end_ts 3; age_s 3-0=3; touched: best bid 99,990 is in cell 99,990 not 99,500, no trades -> False | pulled, end_ts 3, age_s 3, touched False (:72-80) | MATCH |
| 3 | filled_when_trade_volume_in_cell_on_vanish (:83) ts3 wall gone + trade (99,505, 20) | Trade price floors to cell 99,500 = wall cell, volume printed, wall vanished at ts3 (vanish snapshot counts for touch) -> filled, touched True | filled, touched True (:83-89) | MATCH |
| 4 | trade_outside_cell_does_not_fill (:92) trade at 99,510 | 99,510 floors to 99,510, a different cell -> no volume in 99,500 -> pulled (touched also False, not asserted) | outcome pulled (:92-97) | MATCH |
| 5 | touched_by_best_price_then_pulled (:100) ts3 best bid 99,505 (in cell 99,500) with wall still 20 BTC; ts4 wall gone, no trades | Wall rests ts0-3; at ts3 best bid inside cell -> touched. ts4 cell value 0 -> below threshold, no trade volume -> pulled; touched True so NOT pulled-before-touch. Ask wall 101,000 stays open. | pulled, touched True (:100-109) | MATCH |
| 6 | dip_below_threshold_closes_wall (:112) ts0-2 base, ts3 bid 5 BTC x 99,500 = 497,500, ts4-6 base | Row 1: placed 0, ts3 value 497,500 < 1.5M, no trades -> pulled. Rule: reappearance starts a new row; ts4,5,6 = 3 consecutive -> placed_ts=4, still present at end -> open. Bid rows in order: [pulled, open], second placed_ts 4 | outcomes [pulled, open], bids[1].placed_ts 4 (:112-119) | MATCH |
| 7 | flicker_that_vanishes_before_persisting (:53) bid wall at ts0,1; gone ts2 | Only 2 consecutive snapshots < PERSIST 3 -> never placed -> no rows (ask side has no wall) | [] (:53-57) | MATCH |
| 8 | threshold_is_inclusive (:42) 15 BTC x 100,000 | 1,500,000 >= 1,500,000 -> candidate in cell 100,000 ask | ("ask",100000.0) in c (:42-45) | MATCH |
| 9 | pulled_before_touch_rate (:122) | pulled 3, filled 1, open 1 (excluded); pulled_before_touch = pulled & untouched = 2; rate 2/(3+1)=0.5; placed 5 | summary dict as derived (:122-132) | MATCH |

9 of 9 fixtures re-derived; 0 mismatches. (Requirement: >= 5.)

## Rule ambiguities noted (not mismatches)
- Mid definition (best-bid/best-ask midpoint) not stated in RESULT.md Rule; fixtures only exercise a symmetric book where any sane mid = 100,000.
- "Touched ... while the wall rested": whether pre-placement snapshots (ts0-1 of a not-yet-placed candidate) count is not specified; no fixture distinguishes it.
- age_s for an open wall = last snapshot ts - placed_ts (RESULT.md schema); fixture 1 matches; the filled/pulled age for a trade-only fill is only checked for pulled (fixture 2).
- Fixture 3 does not assert age_s or end_ts, so derived values (end_ts 3, age_s 3) are unverified by asserts.

VERDICT: MATCH