# PRE_REG_C26_REGIME: the C26 regime rule and Candidates A (single short), B (hedge book), C (ladder in the range), frozen before any new DEV P&L

Builder, card c26-phase2-freeze-regime-ladder, 2026-11-03. Proposals and reasons: C26_REVALIDATION_2026-11-01.md section 3, PHASE1_RANGE.md Q1b.
Every number below is OURS unless it says SOURCED. This file contains no P&L number on purpose.

STATUS: FROZEN by the author. Two checks stay open and are named so nobody reads this as finished: (1) the operator has not yet confirmed the three
chart encodings in section 8 (PRE_REG_TEMPLATE 0g); until he does, the regime rule and H1 definitions are OURS, not "his", and every result says so;
(2) the non-Claude spec review (card note, E4) has not run. Any rule change after this commit is a NEW pre-registration with new TRIAL_REGISTRY rows.
DECISION (OURS): with zero operator input the file is committed now so Phase 3 can be built; the open checks do not move a frozen number.

## 0. Data-leak statement (read first)

- An earlier DEV look at the single short already exists (phase3_dev.py, TRIAL_REGISTRY rows P3_*), run under a different regime proxy (200-bar mean of 15m
  closes) and filters F0..F4c. Its numbers are not copied here. Consequence: DEV 2022-04-01 .. 2024-06-30 is SEEN for Candidate A, and for B and C by design
  (same events). DEV can only KILL a candidate, never pass it (C26_REVALIDATION contradiction 1).
- The one confirmation look is 2024-07-01 .. 2026-06-30 (perp 1m); the clean test is FORWARD from the commit date of this file, n >= 30 trades.
- The regime rule of section 1 is NEW (daily SMA50). phase3_dev.py REG_N = 200 bars is superseded for C26 book runs; Phase 3 of the book must use section 1.

## 1. Regime rule (OURS)

Known at the time of the signal, no look-ahead:
- Daily bars are UTC calendar days of the perp 1m data resampled. D = the last COMPLETED UTC day before the 15m signal bar opens.
- SMA50(D) = mean of the 50 daily closes ending at D (D included). Needs 50 completed days; before that, no trade.
- DOWN if close(D) < SMA50(D); UP otherwise (equality = UP). Only DOWN is traded. UP is reported as the paired readout, not in the family.
- One regime value per UTC day; it does not change intraday.

## 2. Event definition (OURS, as in phase1_recent.py / phase3_dev.py, restated so Phase 3 cannot drift)

- Venue and bars: Binance USDT-M perp BTCUSDT, 1m rebuilt to 15m (DEV and confirmation files). The first line of the Phase 3 output prints the event-count
  difference against the spot run (contradiction 4).
- H1 sets (two, both built once, never tuned on P&L):
  K = Krown dominant lower high (KROWN_SETUP_CATALOG.md line 820, SOURCED principle; KR_K = 2, KR_M = 12 OURS, as set in phase3_dev.py). PRIMARY set.
  C = C26 pivot high +-16 bars, pull-back >= 0.8 %, retest within 0.4 %, held 4 bars, age <= 72h (C26_PRE_REG.md, OURS). DESCRIPTIVE set (see section 6).
- Take-out = first 15m high above H1 within 72h of H1. Signal bar s = first 15m close back under H1 from the take-out bar on (the take-out bar itself counts).
- L1 = lowest low between H1 and its retest (the C26 pull-back extreme). Time stop T = close of the take-out bar + 96 bars (24h).
- Entries are shifted (primary): market at the OPEN of bar s+1. The unshifted close-of-s entry is a printed check, not a cell.
- One book per distinct take-out bar (the event with the highest H1); overlapping holds are not modelled.
- Both exits touched in one 15m bar count the STOP (fail closed).

## 3. Common numbers

| item | frozen value | label |
|---|---|---|
| X (range top, the one stop is H1 + X) | 1.0 % of H1 | OURS, from PHASE1_RANGE Q1b (21 of 30 inside, 76 % of those reach L1) |
| X sensitivity lines (not cells) | 0.65 % and 1.5 % | OURS, printed only |
| target | L1 touch | OURS |
| fee model | fees.py BINANCE_TAKER x 2 per leg round trip (0.10 % of price per leg); stress line 0.14 % per leg round trip | SOURCED (fees.py, research_kit TAKER_RT_PCT); the 0.14 line is from contradiction 3 |
| slippage | none beyond the fee, stated: every fill is a taker fill at the bar open or at the level | OURS |
| P&L unit | % of leg-1 notional at the fill price, minus fees per leg; also R = book P&L / book max loss at the stop with all legs filled | OURS |
| days of data | confirmation and forward only after DEV is scored | OURS |

## 4. The three candidates

All three trade only the DOWN regime on the same events, so A, B, C differ only in the book.

**Candidate A, single short.** Short size 1 at the open of s+1. Stop = H1 + X (1.0 %). Target = L1 touch. Time = T.
Free of the filters F0..F4c (those stay in the earlier Phase 3 run; this pre-reg adds none).

**Candidate B, hedge book** (the card names it without a recipe; this is the frozen recipe, DECISION OURS):
- Short 1 at the open of s+1, as A.
- Hedge: after the first 15m close >= H1 + 0.5 X (0.5 %), buy 1 at the next open. While hedged the book is flat and the A stop is disarmed.
- Hedge off: after the first 15m close <= H1 following the hedge, sell the hedge long at the next open; the A stop re-arms at H1 + X. One hedge cycle per book, no second hedge.
- Book hard stop: price touches H1 + 2 X (2.0 %): everything closed at that level (worst book loss is a scored number).
- Target L1 touch and time T close the whole book. The fee is charged on every leg actually opened.

**Candidate C, ladder in H1 .. H1 + X** (the operator's idea, fixed by rule, not by the indicator):
- 3 resting short limits placed from the retest decision bar j, at H1, H1 + 0.3 %, H1 + 0.6 % (price steps, OURS; not one leg per divergence: 83-96 % of
  take-outs carried 8-16 divergence signals in 1h, PHASE1_RANGE reading 4, so the divergence is a clock and is NOT a trigger here).
- Fill rule: a limit fills when a 15m high trades THROUGH the level by at least one tick (0.1). Touch-only fills are printed as a sensitivity line.
  The H1 rung fills in the take-out bar by construction (entry before the signal bar), so C is not a copy of A's entry; Phase 3 states that.
- One stop for the whole book at H1 + X, no per-leg stops. Target = L1 touch for all filled legs, time T.
- Size steps, both scored: C112 = 1-1-2 and C124 = 1-2-4 (shallowest rung first).
- Max book loss at the stop with all legs filled, in leg-1 units and before fees: C112 = 1.0 + 0.7 + 2 x 0.4 = 2.5 ; C124 = 1.0 + 2 x 0.7 + 4 x 0.4 = 4.0 (computed here by hand from
  the rung prices and X = 1.0 %; Phase 3 prints the realised worst book loss and it must not exceed these plus fees, else the code is wrong).
- If nothing fills, there is no trade.

## 5. Cells, family and power (PRE_REG_TEMPLATE item 10, 0e)

Verdict cells (H1 set K, DOWN regime, DEV then one confirmation look): A, B, C112, C124. Family m = 4, Holm over these four.
Descriptive cells (H1 set C, same four books, plus UP regime for all): printed, no verdict (the C set has about 100 DOWN distinct take-outs on DEV, see below).

Gate (`python scripts/dev/prereg_gate.py --n <n> --sd 1.3 --cost 0.10 --m 4`, sd is the two-point value of a stop-bounded book: -1.1 R and +1.5 R at 50/50 gives sd 1.3 R, OURS;
cost 0.10 R = fee 0.10 % over a 1.0 % stop; n = DEV distinct DOWN take-outs of set K from PHASE1_RANGE counts, 695 under the old 200-bar regime):

| run | output |
|---|---|
| n 695, sd 1.3, m 4, cost 0.10 | MDE 0.165 R + 0.10 = 0.265 vs 0.30: PASS; n needed 471 |
| n 695, sd 1.3, m 4, cost 0.14 (stress) | 0.305 vs 0.30: BLOCK by 0.005; n needed 735 |
| n 108 (set C), sd 1.3, m 4, cost 0.10 | 0.518: BLOCK; n needed 471 |

Reading, frozen in advance: the verdict cells are powered only at fee 0.10 % and only if set K has >= 471 distinct DOWN take-outs on DEV under the section 1 regime.
If the count is below 471, every K cell is written INCONCLUSIVE in advance (never "no edge"). The 0.14 % stress line is a required robustness check
(section 7), not part of the power gate, because its n needed (735) exceeds the data. Set C is below 471 and is descriptive only.

## 6. Parameters and sources (item 1, 11)

| parameter | value | label |
|---|---|---|
| SMA50 daily regime | 50 days, close below | OURS (proposal in C26_REVALIDATION section 3; no source) |
| KR_K, KR_M | 2, 12 | OURS (set once on the operator's six 10-30/31 lines, not on P&L) |
| C26 pivot W, PB, NEAR, CONF, MAXAGE | 16, 0.8 %, 0.4 %, 4 bars, 72h | OURS (C26_PRE_REG.md) |
| X, hedge trigger, hard stop | 1.0 %, 0.5 X, 2 X | OURS |
| rungs, size steps | 0 / 0.3 / 0.6 %, 1-1-2 and 1-2-4 | OURS |
| time stop | 96 bars | OURS |
| fees | 0.10 % per leg (stress 0.14 %) | SOURCED fees.py / research_kit |
| Holm m, alpha, power | 4, 0.05, 0.80 (z 0.84) | OURS (prereg_gate.py) |
| Krown "most recent high from which a new low was made" | principle only | SOURCED, KROWN_SETUP_CATALOG.md line 820 |

Fills (item 7): the passive rung fill is trade-through; entries of A and B are market orders at the next open. Exits match no trader's management: a fixed
bracket plus a time stop is a LOWER BOUND only (item 8). Null (item 9): per event, the same book geometry on 20 random DOWN-regime bars entered at the next open,
same hold, paired test, normal p, seed 20261101.

## 7. Pass rule (frozen)

A cell PASSES only if ALL hold; a miss on any one is not a pass:
1. Power: set K count >= 471 (section 5), else INCONCLUSIVE.
2. DEV (SEEN) cannot pass. DEV may only KILL: mean net per book <= 0 at fee 0.10 %, or Holm-adjusted p >= 0.05, ends the cell.
3. Confirmation look (2024-07-01 .. 2026-06-30, once): mean net > 0 at 0.10 % AND at the 0.14 % stress, Holm p < 0.05 over the same m = 4, same sign as DEV.
4. The shifted entry is the number; the unshifted entry must not differ by more than 0.05 % of leg-1 notional (OURS), else the result is a data artefact.
5. No single calendar month supplies more than half of the summed net P&L (OURS).
6. Candidates B and C count only if their R (net per book max loss) beats A's R on the same events; otherwise A is the book and B, C are noted as dominated.
7. UP regime printed beside DOWN for each cell (B154); a cell that is equally positive in UP is not a regime result and is written as such.
8. Even a full pass is research: the clean test is FORWARD n >= 30 from the commit date; no order, no size, no live path without the operator and the normal gates.

Kill rule (0f): if Candidate A's GROSS mean (before fees) on DEV DOWN is not above 0.14 % of notional, nothing built on it can pay (C26_REVALIDATION section 3):
B and C are then reported descriptively and the C26 magnet/fade source is closed. Redesigns allowed: 0. An extra variant, filter or parameter change is a new
pre-registration with new TRIAL_REGISTRY rows, and the trial count includes it.

## 8. Operator chart encodings (PRE_REG_TEMPLATE 0g; written in, confirmation PENDING)

Built from his dated chart notes on disk, prices on Binance spot 15m (fixture_btc15m_2026-10-28_31.json, PHASE1_EVENTS.md, PHASE1_RANGE.md Q4; spot runs
+0.10 to +0.22 % above Bitstamp). Regime inputs: daily closes from data-api.binance.vision 1d klines, SMA50 of the 50 closes ending the day before the event.

| # | his chart | H1 | L1 | event by the rule | regime (prior close vs SMA50) | what he reads | match |
|---|---|---|---|---|---|---|---|
| E1 | 10-31 chart: the 10-28 highs held, taken 10-29, then the drop (phase1_recent op event) | 81,789 (10-28 20:00Z pivot, set C) | 79,710 (10-29 02:45Z) | retest held 10-29 15:30; take-out 10-29 15:45 (high 81,900); the take-out bar closes 81,777.74 under H1, so s = 15:45, entry at the 16:00 open; stop 82,607, 10-29 high 81,971 inside X | DOWN (10-28 close 81,343.5 vs SMA50 81,943) | the high that held, then the drop | YES, rule fires where he marks the break |
| E2 | six TradingView lines 10-29/30 (Q4), dominant lower high 77,937 Bitstamp | 78,110 (10-30 15:15Z, Krown dominant, set K) | 76,326 (10-30 18:45Z, lower in the full window possible; depth 2.2 % in PHASE1_EVENTS) | retest held 11-01 03:00Z; NO take-out on spot: the 11-01 09:45Z close 78,107 is 3 under the 78,110 high and no high exceeded it | DOWN (prior close 77,582 vs SMA50 81,960) | the 09:45Z close is the first close above his line ("reclaim") | PARTIAL: the rule waits for a high above 78,110; on Bitstamp his line was already crossed. The basis (0.1-0.2 %) decides it |
| E3 | daily "last lower high" 82,035 perp / 82,061 spot, approach 10-29 ~15:30Z (T3, C15) | 82,061 spot is NOT a fractal pivot (TEST_LEDGER T3), so no H1 in either set; nearest set-C H1 is E1 | n/a | no take-out of 82,061: the 10-29 16:00Z high is 81,971, 90 under | DOWN (10-28 close 81,343.5 vs SMA50 81,943) | a rejection at his daily line, missed by about 82 perp | NO as an H1: his daily line is a different level family; E1 is the rule's reading of the same hour |

Reading: all three days are DOWN, so these rows cannot test the UP side of the regime rule; that is stated, not hidden. Rows E2 and E3 are mismatches or partial
matches and are listed for him to rule on. If he rejects the rule or moves any H1, the change is a new pre-registration (section 7, kill rule).
He is asked only to confirm or reject E1..E3; nothing else is waiting on him.

## 9. Files and rows

- TRIAL_REGISTRY_c26_roadmap.csv: eight rows added, 4 verdict cells (set K) status `pre-registered` and 4 descriptive (set C) status `descriptive`, run_utc 2026-11-03, no run yet.
- Next card: c26-phase3-dev-book builds the book scorer; it must read sections 1, 2, 4 and 7 literally and print the checks of sections 4 and 5.
- Simulator cards: three, one per candidate, after the scorer exists (not in this card).
