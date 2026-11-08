# Opus post-mortem: Argon's Tom/Fabio work (2026-11-09)

**Verdict: the "no edge" result is about a mechanical proxy, not about Tom or Fabio. The census tested a symmetric 1R bracket, entered at market on the reclaim close, against UTC-day levels, with no session, no order flow and no phase. Both traders sourced a 30-40 % win rate paid by 3R+ targets, adds and break-even. A 1R bracket cannot carry that payoff, so gross ~0 R (-0.010 R on 7y 1h) is what any symmetric bracket returns. Argon got the diagnosis of the old engines mostly right. It then built the fix around four hand-picked winners, and its fee fix (a stop of at least 40 bps) filters out the traders' real trade.**

Scope: process and design, not a recount (Fable recounts). Inputs: AUDIT_AND_COURSE_CORRECTION.md (AUDIT), REVALIDATION_LOG.md (REVAL), auction_context.py (AC), auction_census.py (CEN), AUCTION_CENSUS_1108.md (CENSUS), Lead C review d-argon-tom-fabio-review-1108, Java fix 36513c888, v3 rerun 2eda09a40. Trader rules: CONCEPTS.md (tom_fabio_concepts_2026-10-29), TOM_VERBATIM_INDEX.md, FABIO_V3_SPEC.md s7.1, the raw transcripts. Tom = Tom Vorwald (raw_transcripts_canonical/5Ljfwvtktek_raw.txt:4). Fabio = NQ scalper, NY session (8CWKfoSJu3c_raw.txt:7).

## 1. Argon's claims, graded

| # | Argon claim | Grade | Evidence |
|---|---|---|---|
| C1 | Fee-to-stop geometry killed the old engines | PROVEN (for those engines) | fabio RESCORE: gross +0.079..+0.155 R, net -1.423 R at 5-8 bps stops (AUDIT:14,37) |
| C1b | Fix = block every trade with fee_r > 0.25 R (stop of at least 40 bps) | WRONG as a fix | It drops the traders' own trade: Fabio's NQ stops are 3-16 pts, ~1-6 bps (FABIO_TRADE_LEDGER.md:19-26). Gate-pass gross is still ~0 (CENSUS:113). The levers that matter are target size and maker entry (fees.py:48 FEES_DERIBIT: maker entry and target = 0) |
| C2 | Old engines were over-gated (S1 balance holds in 3.1 % of windows) or blind (raw touches) | PROVEN | AUDIT:16-17; v3 rerun 2eda09a40: only 1-2 nonzero windows for A, B, D |
| C2b | The middle path (2-3 plain proofs) fixes it | WRONG so far | Census FAST_REJECTION gross -0.010 R over 7y; every year negative (CENSUS:113,152-163) |
| C3 | The 1M/1w/1d ladder was missing | PROVEN (absence) | AUDIT:18; tf_strip lacked 1M |
| C3b | The missing ladder caused the no-edge result | UNPROVEN | AC uses the ladder only for the sizing tier, never as a gate (AC:890-898). The census used a different proxy (daily SMA20, CEN daily_bias) and found no with/against gap (CENSUS:139-146) |
| C4a | Java above_vah / below_val asymmetry | PROVEN, fixed | 36513c888 (RulesTest 21/21). Effect on any count: not measured |
| C4b | Fabio v3 Model A in confirm mode came back "unmanaged" | PROVEN, fixed | engine.py diff in 9358461e2. Rerun 2eda09a40: still starved, so the fix does not change the result |
| C5 | Order flow away from a level reads as continuation | PLAUSIBLE-to-PROVEN | n=2,175 b99 study, 18 % reversal vs 27 % baseline (AUDIT:39) |
| C5b | (implied) The new engine reads order flow at the level | WRONG | The census klines carry no delta, so `delta` defaults to 0 and absorption reduces to wick plus rel_vol (AC:604,620,636). Fabio's half was never tested |
| C6 | Four Oct-Nov trades show that plain auction theory works | WRONG as evidence | Hand-picked. The same 5m window holds 67 FAST_REJECTION events with 42 % reaching target first (CENSUS:168,175) |
| C7 | "77 % continuation" after acceptance below VAL, labelled SOURCED to accept80 | WRONG label | accept80 marks its own acceptance count as OURS. The 77 % has no placebo and no fees, and it measures a half-VA-width touch, not R (value_area_acceptance_2026-11-05/RESULT.md:5-12). Census ACCEPTED gate-pass: -0.096 R |
| C8 | Trade 2 triggers the "Dalton 80 % rotation" | WRONG | The same source measures 44 % on BTC (RESULT.md:9) |
| C9 | Thresholds (rel_vol 2.0, 3-bar reclaim, 6-bar acceptance, 5 bps buffer, net RR 1.2) | OURS, mostly unlabelled in AUDIT | Lead C review; only AC:14,544 carry labels |
| C10 | Four-stage revalidation proves the work | WRONG (process) | All four stages checked arithmetic and code; none asked for a count. Stage D "confirmed the root-cause diagnoses" with no data (REVAL:59) |
| C11 | Unit tests validate the classifier | WEAK | The tests replay the same Nov-6 bars that drove the reclaim_idx fix (test_auction_context.py:102-145; REVAL:42), so the rule was tuned to the anecdote |

## 2. Tested thing vs what the trader does

| Dimension | Tom (sourced) | Fabio (sourced) | Argon AC / census | Label of tested value | Gap |
|---|---|---|---|---|---|
| Timeframe ladder | weekly and daily profile, then 5m, then "even smaller" for entry (TOM-041; TOM-015) | 1m execution with footprint; range bars (Is1HvdfQm5c:578) | 5m (35 days, bear only) and 1h (7y); 1h counts hours: 6 bars = 6 h (CENSUS:15) | OURS | 1h is no trader's entry chart; 5m n=10 gate-pass |
| Session | DAX cash 9-12, lunch is dead (5Ljfwvtktek:7; TOM-029) | NY only; London profile "not so valuable" (Pz8f0wWW12M:655-660) | none (CENSUS:10) | OURS (absent) | High: every Asia event is in the pool |
| Value area | prior day, cash session only, volume profile, 70 % weekly (TOM-142, TOM-281, TOM-277) | cash-session profile, prior-session VAL (Pz8f0wWW12M:654; Is1HvdfQm5c:200) | UTC 00-24 prior day, 70 %, bin 0.067 % (CENSUS:16) | 70 % SOURCED (Tom); UTC day OURS | BTC has no cash session: the NY-session profile is the closer analogue, never built |
| Entry trigger | limit order at the zone, or pullback after proof; idea + proof (TOM-005, TOM-012, TOM-067) | absorption then aggression on the footprint; big-trade filter (Is1HvdfQm5c:140-142, 609-613) | market at the close of the first firing bar, up to 3 bars after the reclaim (CEN:128-129; AC:692) | OURS | No limit fill; late entry; no footprint |
| Stop | below the last liquidity / swing (TOM-072, TOM-073); DAX 0.08-0.26 % (RECALL_DAX.md:22) | "super small", above the area (Is1HvdfQm5c:144); NQ ~1-6 bps | sweep extreme, no buffer; ACCEPTED stop = the level itself (CEN:132-136) | structural SOURCED; no buffer OURS | ACCEPTED stop at the level means tiny stops and fee 0.54 R (CENSUS:116) |
| Target | next high-volume price (TOM-018); a few points short of a range (TOM-262) | session VAL / absorbed cluster; 1:4.5 (8CWKfoSJu3c:139-143; Is1HvdfQm5c:145) | fixed 1R, 24-bar horizon (CEN:44, CENSUS:18) | OURS | Biggest gap: the payoff shape is not the traders' |
| Management | partials, adds at breakout, no early stop move (TOM-014, TOM-017, TOM-079) | fast break-even, aggressive trail, adds from profit (fZlNGWvd2Ko:43-61) | none | absent | All right-tail R is cut |
| Market state | trend vs balance needs different setups (TOM-065); ~70 % balance (TOM-046) | volatility days only (8CWKfoSJu3c:84-88); with bias (Is1HvdfQm5c:737) | no state gate; bias SMA20 used only as a split | OURS | Fades run in trends, continuations run in ranges |
| Win rate / R | 30-40 % hit rate at >3R (TOM-091) | 30-35 % at a huge RR (Is1HvdfQm5c:245); few trades a day (:102) | 42-50 % at 1R | - | The census asks "does a 1R bracket win > 50 %?", which neither trader claims |
| Fees | futures, ~0.5-1 bps round trip (OURS estimate, RECALL_DAX.md:51) | NQ, no quote | 10 bps taker round trip on every leg | 10 bps SOURCED (fees.py) for taker; taker-only OURS | MTS's own Deribit model is maker entry and target at 0, taker stop 5 bps (fees.py:48) |

## 3. Which gaps could hide an edge, and the cheapest test

| Gap | Could hide an edge? | Why | Cheapest test |
|---|---|---|---|
| 1R bracket vs 3R+ target with BE/trail | YES, strongest | The traders' R lives in the tail. Gross ~0 at 1R says nothing about 3R at a 30 % hit rate | Re-score the census event list with exit = next HVN or opposite VA edge, BE at +1R, no fixed R (card 1). No new events, so no tuning |
| Session (NY / London) | YES | Both traders exclude the quiet sessions; the pool is ~1/3 Asia | Same re-score, split by session (card 1) |
| Taker-only fees | PARTLY | Maker entry and target cut fees on winners to 0. At 6 bps stops, losers still pay 0.8 R: Fabio-size stops do not survive on BTC under either model. 15+ bps stops at 1:3 can | Re-score with FEES_DERIBIT (card 1) |
| No order flow at the level | YES (Fabio) | Absorption then aggression is his trigger; the census never saw delta | Live delta exists (orderflow_live). Log NY-session level events with delta on testnet (card 3) |
| No phase | YES | The census pools seven years and every regime; the current phase is a 75.4-80.9k range (BIBLE.md:28), where range-edge fades are the operator's own claim | Phase-scoped testnet run (below) |
| HTF ladder used for size only | MAYBE | Not tested as a gate | Gate it in the testnet plan; log with/against |
| UTC-day VA vs NY-session VA | MAYBE | Different POC/VAH/VAL on most days | Build the NY profile (card 2); A/B in the testnet log |
| Java bugs, v3 unmanaged | NO | Fixed; counts did not change | none |

### Phase-scoped testnet-forward plan (replaces "another backtest")

| Item | Rule | Label |
|---|---|---|
| Phase | Current 4h/1h range 75,400-80,900 (BIBLE.md:28). The run ends when a daily close lands outside the range, which records the phase end | phase SOURCED (Bible); exit rule OURS |
| Levels | range edges, PDH/PDL, NY-session VAH/VAL/POC (prior session) | Tom/Fabio SOURCED; NY analogue OURS |
| Session | London open and NY session only | SOURCED (Fabio NY; Tom cash hours) |
| Trigger | probe beyond the level, reclaim within 3 bars, rel_vol of at least 2 or opposing delta | AC thresholds OURS |
| Entry | maker limit at the level after the reclaim (Tom's limit order); no fill within 3 bars = no trade | SOURCED (TOM-005); 3 bars OURS |
| Stop | beyond the sweep extreme (the plan's invalidation, d-stops-follow-trade-1106); no floor | SOURCED |
| Target | opposite range edge or next HVN; skip if it is under 2.5R | Tom TOM-018 SOURCED; 2.5R OURS |
| Management | BE at +1R; half off at POC | Fabio BE SOURCED; split OURS |
| Size | testnet, fixed risk per trade | OURS |
| Logged per trade | session, level type, delta at reclaim, with/against 1M bias, fill or no fill, R net under FEES_DERIBIT | - |
| Fails when | 8 losses in a row (0.65^8 = 3 % at a 35 % hit rate), or net R < 0 after 20 trades | OURS |

Existing card auction-plan-testnet-forward-1108 carries this; card 4 below amends its setup list.

## 4. Method alignment (did Argon apply our current method?)

| Method rule | Where written | What Argon / the census did | Gap | Effect on the no-edge result | Could hide an edge? |
|---|---|---|---|---|---|
| Phase-first: judge by the current phase, testnet at once | OPERATOR_DECISIONS.md d-phase-first-method-1106 | Argon filed a "multi-month OOS backtest" as its next step (AUDIT:74; card tom-fabio-auction-context-oos-bt-1107). The census pooled 7y with no phase split (CENSUS:9) | Large | The 7y pool averages phases in which fades should lose (trends) with phases in which they should win (ranges) | YES |
| Context before backtest: `## Context`, `Regime mix:` | d-context-retest-1104; PRE_REG_TEMPLATE.md:80-89 | REVAL and AUDIT: no Context block, no Regime mix. The census has both, but with Phase: none and Session: none (CENSUS:7-11,92,150) | Partial | Longs and shorts were tested against the phase: bear 5m window and pooled 7y | YES |
| Bible cycle clock | d-mts-bible-1106; BIBLE.md:31-36 | Not cited. AC labels the phase "macro bear" from the 20M SMA and sizes longs at support as scalps with capped targets (AUDIT:68; AC:898) | Large | The Bible reads now as the bottom window (two clocks). Cycle-bottom longs are MTS's core trade, and Argon caps them | YES |
| Stops follow the plan's invalidation | d-stops-follow-trade-1106 | AC: structural stop, aligned. But the 0.25 R gate is a fixed-percent floor in disguise (40 bps). The census ACCEPTED stop sits at the level, not at the invalidation | Medium | Fee R 0.54 on ACCEPTED; the gate removes tight-stop trades | PARTLY |
| Pattern book / trader's eye, not proxies | d-three-studies-1106 | Mechanical proxy: no footprint, no NY profile, no adds, 1R exit | Large | See section 2 | YES |
| MTS = leveraged directional (cycle-bottom longs, Tom/Fabio session trades) | memory note 11-06; d-phase-first-method-1106 | Session trades without sessions | Large | Same as the session gap | YES |
| No layer discard before simulator review | operator note 10-25 | Census: "status descriptive, no layer change" (CENSUS:3), aligned | none | - | - |

## 5. Process: why Argon went wrong

| What happened | Effect | Fix |
|---|---|---|
| The strategy was built from four recent winners, then tested on the same bars | anecdote fitting (C6, C11) | count first, then draw the rule |
| The trader's payoff was never written down before coding | the census tested a 1R bracket | Context block plus a SOURCED exit line in every PRE_REG |
| Four reviewers checked numbers and code, none checked the method or demanded a count | false confidence | a review question: "what count supports this?" |
| SOURCED was claimed where the source said OURS (77 %, 80 %) | the wrong anchor carried into the census | blind-read of labels (Haiku) |

## Cards filed
See the ship commit: tf-census-trader-exits-rescore-1109, tf-ny-session-va-profile-1109, tf-delta-at-level-testnet-log-1109, tf-testnet-forward-range-phase-amend-1109, tf-acceptance-77-label-placebo-1109.
