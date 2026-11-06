# Habib's 9 priced plans vs the concept book (2026-11-07)

**Result: scored as pre-registered (24 h to fill, 7 d to reach the target), 1 of 9 plans is full, 8 are misses. Read with a 7-day entry window instead (descriptive, not pre-registered), 7 of 9 entries were reached, 2 plans reached the target, 1 got over half way. His levels are good places; his targets are far and mostly not reached in a week. n = 9 plans from 7 posts: no p-value, no edge claim.**

Scoring: `plan_score.score_plan` unchanged (`habib_plan_imbalance_2026-10-20/plan_score.py:39-64`; full = entry touched in 24 h then first target touched in 7 d; partial = at least 50 % of the way; execution excluded) on Binance spot BTCUSDT 1m klines from `https://data-api.binance.vision/api/v3/klines`. Script `calls_score.py`; numbers in `CALLS_SCORED.csv`. Post time is the video publish time (`qriptal_2026-10-10/PUBLISH_TIMES.tsv`): the ZPFK stream was recorded about six hours earlier (CALL_LEDGER note, `qriptal_2026-10-10/CALL_LEDGER.csv`, call `QRP-ZPFK3ZsLwoo-06`), so those two plans may be early by hours.

Release: the 9 plans sat inside the sealed window (`PRE_REG_HABIB_PLANS.md:15`). The operator's order of 2026-11-06 to study his calls releases them (decision `d-habib-calls-unsealed-1106`, recorded by Lead C per the session brief; it was not yet on trunk when this ran). Scoring his plans tunes nothing of ours. Kill rule 1 of the pre-reg applies (fewer than 12 distinct posts: `PRE_REG_HABIB_PLANS.md:74`): descriptive only, no placebo p-value, no claim.

## 1. The table

Columns: Concept = IDs from `HABIB_CONCEPT_BOOK.md` section 1.1. Level type = what the quote says, plus the nearest known level within 0.3 % of the entry at post time (prior-day, week, month levels from the live-aid logic, plus prior 7d/14d high and low). Imbalance candle = highest-timeframe candle closed before the post, relative volume >= 2.0 vs the 50-bar median (OURS), whose open or midpoint (tight) or range (loose) holds the entry; **identifiable is not proof**, because our flag picks his labelled candles only 1.3-1.5x above chance (`imbalance_qriptal_2026-10-16/README.md:49-58`). Trigger = flagged 30m/1h candle at the fill. Pre-reg = result under the 24 h / 7 d rule. Reach = descriptive 7 d / 30 d read on 1h bars (see section 2).

| Plan (post UTC) | Side, entry -> target | Concepts used | Level type | Imbalance candle on Binance | Trigger candle at fill | Pre-reg | Reach (descriptive) |
|---|---|---|---|---|---|---|---|
| `yKm-03` (07-14 11:47) | short 65,600 -> 60,000 (854 bp) | C8 sweep, C7 | sweep of a swing high ("short above 65.6"); no known level within 0.3 % | none found | not filled in 24 h (high stopped 49 bp short of the entry) | miss | entry touched +27 h (just after the window), 59 % of the way, target not reached |
| `dYl-01` (07-21 11:21) | short 66,400 -> 65,400 (151 bp) | C7, C5, C8 | "needs the right volume and a reaction"; prior 7d high 66,421 (0.03 %) | 1h 07-21 10:00, rv 2.4, mid body, wickless-bottom, entry = its open | 1h 13:00 rv 2.4, mid body, rejection wick only 5 % | **full** (filled 07-21 12:11, target 07-23 07:11) | worst move against it before the target 0.84 % |
| `tJn-02` (08-11 11:59) | short 64,600 -> 62,000 (402 bp) | C7, C5, C8 (target = triple bottom) | "reaction required"; no known level within 0.3 % | 4h 08-10 12:00, rv 2.4, **large body**, entry = its midpoint | not filled (high stopped 13 bp short) | miss | touched +150 h; 22 % of the way; no target |
| `xnu-01` (08-27 11:39) | long 76,600 -> 81,000 (574 bp) | C8 sweep of the liquidity below ("at 76.6"), C7 | sweep long; no known level within 0.3 % | 12h 08-21 12:00, rv 2.7, mid body, entry = its open | not filled (low stayed 303 bp above) | miss | touched +126 h (outside 24 h), **target 45 h later**; this is the long he took and closed with +150 % to +178 % on a 30x card (DISC:50-51) |
| `xnu-02` (08-27 11:39) | long 72,000 -> 100,000 (3,889 bp) | C10 macro support 72-73k | round-number macro support; horizon months | 12h 08-20 12:00, rv 2.5, entry = its open (chance-level match) | not filled | miss | never touched in 30 d; **not a 7-day plan: unfair to score** |
| `t5x-03` (09-15 11:45) | short 80,000 -> 75,500 (562 bp) | C8 sweep of 80k, C10 target = range low | round number and prior 7d high 79,890 (0.14 %); "only if a retest comes" | 12h 09-03 12:00, rv 2.1, large body, wickless-bottom, entry = its midpoint | not filled (high stopped 332 bp short) | miss | touched +73 h; 0 % of the way; the Monday order was front-run (DISC:38,43) |
| `ZPFK-05` (09-21 07:11) | short 79,500 -> 73,000 (818 bp) | C12 loss of a level, C10 | "wait for a loss of that level"; stop 82,800 stated | 12h 09-18 12:00, rv 2.2, large body, midpoint match | not filled (low stayed 279 bp above) | miss | never touched in 30 d (price went up, not down) |
| `ZPFK-06` (09-21 07:11) | short 82,200 -> 73,000 (1,119 bp), stop 82,800 | C8 sweep, C7 | "aggressive short above 82.2"; prior 7d high 82,100 (0.12 %) | 12h 09-03 12:00 (range match only, weak) | **1h 08:00 rv 10.5 large body and 30m 08:30 rv 21.0 large body** at the fill 08:24 | miss: filled, then the stop 82,800 was hit; worst move against it 6.32 % | 26 % of the way before the stop; **fading a large-body anomaly = his own veto (C3)** |
| `lRB-02` (09-22 12:16) | short 82,800 back below -> 73,000 (1,184 bp) | C12 fakeout after a broken level, C5 | "back below 82.8"; no known level within 0.3 % | 1h 09-21 08:00, rv 10.5, large body, entry = its midpoint | not filled (low stayed 298 bp above) | miss | touched +137 h; 31 % of the way; no target |

Notes: `dYl-01` and `xnu-01` are the two that reached the target. The 9/21 to 9/22 plans are the Sunday weekly plan and its follow-up; the upside break of 82.8k invalidated them, as he said it would (`DISC:35`, plan stop 82,800).

## 2. Descriptive 7 d / 30 d read (outside the pre-reg)

The pre-reg fixes a 24 h fill window (`PRE_REG_HABIB_PLANS.md:31`) and bars other windows (`:88`). It is an unapproved draft and the operator's order of 2026-11-06 overrides it; this read is **one extra descriptive variant**, used for no decision and with no p-value.

| Measure (OURS, 1h bars, entry touched = bar range holds the entry) | Count of 9 |
|---|---|
| Entry touched within 24 h (the pre-reg window) | 2 (`dYl-01`, `ZPFK-06`) |
| Entry touched within 7 d | 7 |
| Entry never touched in 30 d | 2 (`xnu-02`, `ZPFK-05`) |
| Target reached after the touch, within 30 d (strictly later bar) | 2 (`dYl-01`, `xnu-01`) |
| At least 50 % of the way after the touch (partial) | 1 more (`yKm-03`, 59 %) |
| Entry stopped short by at most 50 bp in the first 24 h ("front-run") | 2 (`yKm-03` 49 bp, `tJn-02` 13 bp) |

Fee-net rule of the pre-reg (`:69`, 10 bp round trip, no stop): `dYl-01` full = +141 bp net (151 bp distance); `ZPFK-06` filled and not full = -122 bp net by the close at 7 d (no stop in this rule; with his own stop 82,800 the loss is 73 bp plus 10 bp fee). Plans not filled in 24 h count 0, reported separately. `dYl-01` distance 151 bp is above the 20 bp fee-dominated flag.

## 3. Verdict: what his method does well and where it fails

| | Finding | Evidence |
|---|---|---|
| Does well | **Locations.** Price came to the planned level within 7 days in 7 of 9 plans; `dYl-01` sat 0.03 % from the prior 7d high and the 1h imbalance open, and went to target in 43 h | table; `CALLS_SCORED.csv` |
| Does well | **Sweep-then-reverse long.** `xnu-01` (wait for the sweep under 76.6k, then 81k) reached the target 45 h after the touch, and matches the long he really took with a 30x card and closed in profit | table; DISC:50-51 |
| Does well | **The large-body veto is right.** The one plan filled into a high-volume large-body candle (`ZPFK-06`) lost 6.3 % against the entry before stopping out; this is the one rule of his that also held in our fade test | table; `imbalance_qriptal_2026-10-16/README.md:83` |
| Fails | **Targets are far.** 8 of 9 targets sit 4-39 % away (median of all 9: 818 bp, only `dYl-01` is near at 151 bp; `CALLS_SCORED.csv`); only 2 of 9 reached them inside 30 days of entry | section 2 |
| Fails | **Front-running and timing.** 5 entries were touched only after day one, and 2 of those (`yKm-03`, `tJn-02`) had stopped 49 and 13 bp short of the entry inside the first 24 h. His own words: "frontrun" 13 times in the Discord table (DISC), "my execution has been quite poor" (DISC:30) | section 2 |
| Fails | **Against the trend.** The September short plans (`t5x-03`, `ZPFK-05/06`, `lRB-02`) faced an upside break of 82.8k; levels do not say which phase the market is in | table; `DISC:35` |
| Not measurable | **The imbalance candle's own value.** It is identifiable on Binance data at 7 of 9 entries by open or midpoint and at 8 of 9 counting a loose range match, but the flag matches his key only 1.3-1.5x better than chance, and `dYl-01` (the winner) had a mid body with a 5 % wick, not the textbook small-body wick. n = 9 cannot separate "imbalance helps" from "levels help" | `imbalance_qriptal_2026-10-16/README.md:49-58` |

Plain reading: Habib's plans are good maps of where price will go within a few days and poor forecasts of how far (n = 9, descriptive). A trade that uses his levels for entry and a closer, structural target, and respects the large-body veto, matches what he does well; a plan that needs the full 4-12 % move inside a week usually does not arrive.

## 4. Limits

- n = 9 rows from 7 distinct posts (two posts carry two rows); the pre-reg needs 12 posts for any claim (`:74`).
- Plans enter the set only with a spoken entry and first target (selection; `:92`). Direction-only plans are absent.
- Post time is the publish time, not the planning time (`:94`); levels were read from auto-captions; the 9 ledger quotes were re-checked this session against `extracts/_staged_2026-09-27/raw/` with the `verify_extract_quotes.py` normalisation and all 9 occur verbatim (words and numbers can still be mis-heard by the captions).
- Imbalance matches use OURS thresholds and a 50-bar median, not his indicator; tight matches (open or midpoint within 0.25 %) are still frequent by chance on 12h/1d candles.
- The 1h-bar reach read cannot order events inside an hour; the target was required on a strictly later bar.
- Reproduce: `python MyTradingSys/research/habib_concept_book_2026-11/calls_score.py` (public klines, about 3 minutes). Test: `test_habib_concept_book.py`.
