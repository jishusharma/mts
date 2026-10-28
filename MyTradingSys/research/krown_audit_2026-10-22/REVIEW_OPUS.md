# Independent review: Krown audit REPORT.md + LAYER_CONFLUENCE_DESIGN.md (2026-10-22, Opus 5.5)

**Verdict: SOUND WITH FIXES.** REPORT.md is factually accurate where checked: its audit rows A1, A2, A5 and A7 hold on disk, and
`pytest MyTradingSys/backtest/layers/krown` gives 49 passed. LAYER_CONFLUENCE_DESIGN.md has the right shape: roles instead of votes,
few ordinal dimensions, pre-registration, fee-net. But it should not be pre-registered as written. Five things have to be fixed first:
- It ignores a prior context study that already ran and came back INCONCLUSIVE.
- Its fee-wall mechanism (c) is arithmetic, not edge.
- It pools layers whose R units are not comparable.
- It underestimates the dependence in a context that persists for weeks.
- It conflicts with the PROJECT_VISION rule on when confluence may gate.

Scope of this review: read-only. No VALIDATION or HOLDOUT data was read and no outcome was computed. The power numbers in the
findings table are OURS approximations (method stated in F8).

## 1. Findings

| id | sev | claim (doc s) | evidence (file:line) | fix |
|---|---|---|---|---|
| F1 | HIGH | Neither doc mentions that a point-in-time context study already ran on the same question. It covered Krown 4h pivot zones, BB state, vol regime, HTF alignment, phase and funding. Design s1 calls the join "cheap" as if new. | `research/context_factors_2026-10-16/REPORT.md:17-21` (DEV too short for any single factor: 1,242 independent days needed per bucket and side, 0 of 86 buckets qualify); `RESULT.md:1,9-15` (composite INCONCLUSIVE, E -0.023 R, SE 0.074, all-C mean net -0.137 R over 1,010 events); `research/context_null_2026-10-16/README.md` (context-matched null harness; location-only arm lost to cost, t_cost -6.0) | Cite both studies. Reuse `context_asof.py` (point-in-time proven by a replay vs vectorised build plus planted leaks) and `context_null.py`. Log the new trial as a sibling of the C composite (same family for Holm). |
| F2 | HIGH | The design assumes a long DEV and day-level independence. In fact every event table is DEV 2022-01-01..2024-06-30 (912 days). trend_1d/1w is close to a year dummy (2022 bear, 2023-24H1 bull), so the D1 slope mostly measures drift. Day-clustered SE (design s4) understates the error because D1 stays constant for weeks. | `layer_lab/malkan_rsi_event_table/REPORT.md` (21,888 DEV 1h bars = 912 d); `system/OPERATOR_DECISIONS.md:883,894` (DEV kept at 2022..2024-06; DEV_EXT 2020-21 opt-in); `krown_core.py:190-249` (k=3 swings, a swing is known k bars later) | Cluster by ISO week, or use a 20-day block bootstrap. Report the slope separately for 2022 and for 2023-24H1 and require the same sign in both. Add DEV_EXT 2020-21 as a second regime set; it is allowed at DEV stage. |
| F3 | HIGH | Fee-wall route (c), "relocate so cost/R falls" (design s0.3, s4 cost/R row, T3 RISK), cannot change the sign of a trade. Net R = (gross % move - cost %) / stop %. A wider stop shrinks cost/R and gross R by the same factor. BLOCKED.md's unblock path (b) inherits the same issue: its 0.30 R plausible-gross cap is fixed in R, so it falls with a wider stop. | `bb_top_reversal_2026-10-18/BLOCKED.md:5,7`; design `:12-14,67,103-104` | Measure the fee wall as cost % / mean signed gross move % per cell, i.e. gross edge in % against the 0.10-0.14 % cost. Keep cost/R < 0.25 only as a feasibility constraint (PROJECT_VISION economics line). Route (c) counts only if gross % expectancy rises with the structural stop (fewer noise stop-outs). |
| F4 | HIGH | The pooled test (design s0.6, s3) assumes "fee-net expectancy in R" can be pooled with layer fixed effects. R differs by table: stop distance (bb_top), ATR14 (malkan, cc_msb, fabio, rsi_reclaim), spike bar range (volume), signal bar range (candles), \|spike - level\| (session_levels). The tables hold gross MFE/MAE with no exit rule, so "fee-net expectancy" needs a new exit per layer, which adds new degrees of freedom. Pooled OLS weights by n, so candle_pattern (12,219), volume (3,392) or turn_of_candle (87,552) would swamp it. | each `layer_lab/*_event_table/REPORT.md` R line; design `:59` | Use one outcome unit for all layers: net signed return over a fixed horizon (per layer tf: 1h->4 bars, 15m->16 bars, frozen now), in % and in ATR units. Estimate a slope per layer and combine with inverse-variance random effects, capping any one layer's weight at 1/3. Use trigger layers only (F16). |
| F5 | HIGH | The design says "combination is the only open route" (s1) and ends with "Gate only after 5" (s7). The vision forbids that: confluence may gate only after each input passes S3 alone. The Krown context has never had an independent read, and its detectors failed recall (F12). | `PROJECT_VISION.md:93,112,262`; design `:28,119` | Give the context its own S3-style read first (amendment 2), or get a signed operator decision to amend line 262. Until then the context is a tag only. |
| F6 | MED | D2 assigns a sign per layer ("event type is a fixed property of each layer"). KR-S16 says enter "against the move", which depends on the direction of the expansion relative to the event's side, so it varies per event. A 15m upper-band short during a 4h expansion that went down is a with-trend short, not a fade. The BBWP timeframe also differs across the docs: trading tf (REPORT H-K1), 4h (D2) and 1h (T1). Malkan setups are labelled BREAKOUT (s6.0), but bull/bear setups are pullbacks with the trend. | `KROWN_SETUP_CATALOG.md` KR-S16 row; REPORT `:112`; design `:53-55,84-85,90` | Define D2 per event. Expansion direction = sign of the 4h close change since BBWP_4h was last <= 50. FADE = event side opposite to that direction. One timeframe (4h) everywhere. |
| F7 | MED | Equal additive weights encode a contradiction. S16, his "near the end of the move" rule (`hNfjyrJEytI_timed.txt` [00:07:20]-[00:07:31]), says fade against trend at a vol extreme. D1 rewards trading with the trend. So a counter-trend fade at BBWP >= 85 scores D1 -1, D2 +1, S = 0, the same as a neutral event. The ordinal sum hides the one interaction his framework actually asserts. | design `:52-58`; transcript lines 233-237 | Primary test: D1 alone, the most powered and simplest. D2 and D3 are separate pre-registered contrasts. The S16 claim gets its own D1 x D2 interaction cell, not the sum. |
| F8 | MED | Power is not costed (design s4 promises an MDE table but sets the bar at n >= 100). Expected cell sizes: S = +3 holds about 1.6 %, S >= +2 about 12 %, S <= -2 about 13 % of events. That gives bb_top 25/183/208, fabio_lvn 24/179/205, rsi_reclaim 15/113/130, cc_msb 13/96/110, rsi_div 1h 8/58/67, malkan 2/15/18, wlow 0/1/1 (S = +3 / >= +2 / <= -2). Slope MDE at 80 % power with Holm m ~ 16 and sd 1.5 R is 0.14-0.25 R per S unit under day-iid SE and >= 0.39 R with week blocks. malkan (132) and rsi_div 4h (138) clear n >= 100 with an MDE of about 0.46 R. | counts from `layer_lab/*_event_table/REPORT.md`; D-level shares OURS (D1 .35/.30/.35, D2 .15/.60/.25, D3 .30/.45/.25, independent) | Gate per-layer verdicts on MDE <= 0.10 R per S unit with week clustering; otherwise the layer is descriptive only. Expect only the pooled test to be powered. Compute the real D-level shares from data before freezing (amendment 1). |
| F9 | MED | The placebo (context of a random other DEV day, s4) breaks the autocorrelation in the context and tests "context != noise". It does not test "trigger adds value inside the context". D1 will beat it from drift alone, which REPORT s1.10 already concedes. | design `:72`; `context_null_2026-10-16/README.md` (same-context controls are the right null) | Use two nulls. (i) Context-matched random entries in the same S cell (context_null), which are verdict-bearing. (ii) A circular shift of the whole context series by >= 30 days, 200 shifts, which preserves the autocorrelation. |
| F10 | MED | D3 is undefined in places and probably saturated. A prior study found 90 % of DEV hours have a same-side level within 1 ATR(1h); 0.5 ATR(1d) is several ATR(1h). The "middle third" (design) disagrees with code `range_edge` 0.2 (outer 20 %). `range_state` returns None when width > 25 %, so in trends D3 collapses to 0. "Correct side" is not defined for BREAKOUT triggers. | `context_factors_2026-10-16/REPORT.md` s3.1; `FORMULAS.md` 21.8 (`:543`); `krown_core.py:353-370`; design `:56-57` | Measure D3 coverage first and choose bands so +1 covers 15-30 % and -1 covers 15-30 % of events. Use one range definition. For breakouts: +1 = the event closes through a ranked zone. |
| F11 | MED | "Daily RSI regime 40/60 = Malkan MTF filter" (design s1, s2, T1) is the wrong timeframe. Malkan's filter is monthly AND weekly RSI < 40; the daily 60 is his trigger. The source is Indian equities, and "winds" is a garbled word that the extract reads as RSI. | `malkan_extract_2026-10-15/extracts/extract_2HcJ3NeZmEQ.md:37-55` | Treat weekly RSI < 40 as the Malkan-matching object. Daily RSI regime = KR-S03 only. Note that monthly < 40 in DEV is essentially 2022 alone. |
| F12 | MED | Construct validity. "Krown trend/zones" are OURS v0 detectors (k=3, tol 0.01, range_n 20) that failed recall: 3 of 12 examples verify and 0 strict hits. Positive results would validate our detectors, not Krown. | `RECALL.md:36`; `params/krown_params.json` (zone_k, swing_tol, range_n OURS) | Label every context field "OURS impl. of KR-x". Run a naive trend baseline (close vs 200d SMA, sign of the 20d return) next to D1. Krown D1 must beat it to be credited. |
| F13 | MED | T1-T5 feasibility. **T1 dead on arrival.** The stop at the 15m upper band from the mid is about one band half-width (~0.3-0.5 %), so cost/R is 0.2-0.47. The target (lower band) is about +1 R, so it needs a >= 60 % hit rate. The skip rule removes most events. MAL-BB-RSI-4060 is not in this branch's catalogue and has no event table. **T4 underpowered:** the parent wlow has n=8 on DEV, and a sweep variant is maybe ~60 over 130 weeks. **T5 dead as a test:** his example is weekly over 4-5 months, single-digit n in DEV, and funding over multi-week holds is not "irrelevant". **T3 self-defeating:** a zone-wick stop with a 15m-BB-mid target gives a reward multiple far below 1. **T2 is the only plausible one:** the stop is the far side of the 4h compression range so cost/R is small, but n after the fabio-escalation intersection is tens. | `MALKAN_DIVERGENCE_GLOSSARY.md:474`; `wlow_bounce_bbrsi60_2026-10-16/RESULT.md:3-4`; transcript [00:17:20]-[00:17:29]; design `:87-114` | Drop T1 (or re-specify on 1h with a vol-scaled stop), T3's 15m target and T5 (move T5 to the call ledger). Keep T2 without the flow conjunction as the primary trade trial (Krown S8 on 4h, OURS timeframe), run on DEV + DEV_EXT. Keep T4 as descriptive. |
| F14 | LOW | REPORT s5.1 says "all fields computable from krown_core.py". There is no ATR function, there is no 1h/4h data path (the Krown data is 1d/1w spot), and the published 1w series has 8 gaps inside 2022 (DEV). | `grep -i atr krown_core.py` (none); `krown_ta101_2026-10-13/DATA_COVERAGE.md` gaps list | Aggregate 1w from 1d (already cross-checked there). Add ATR per FORMULAS. Build 4h from the 1m perp tape. |
| F15 | LOW | REGIME "positioning heat (funding + OI)" and the KR-LQC02 throttle cannot be tested on DEV because there is no OI before 2025-09. Funding only. | `wlow_bounce_bbrsi60_2026-10-16/PRE_REG.md` s1 (OI NOT_IN_DATA for DEV) | Funding-only arm; OI is a live collection field. |
| F16 | LOW | "Event tables exist for 15 layers" overstates it. oi_delta has no empirical rows; bigtrade was contaminated and refixed (5,685 OK); turn_of_candle is every quarter-hour (not a trigger); candle_pattern and volume are descriptive. About 10 are usable trigger tables. | `layer_lab/oi_delta_event_table/REPORT.md`, `bigtrade_event_table/REPORT.md`, `turn_of_candle_event_table/REPORT.md` | List the trigger set in the pre-reg by name. |
| F17 | LOW | Join and definition gaps. D1 is undefined when both 1d and 1w are range. The event tables key on bar open, while the decision time is open + tf. The 1d row is available at close + write latency. Krown 1d is Binance spot; the events are USD-M perp (basis). | design `:52,105`; `htf_context_live.py:97-142` (writes after close) | Join on `available_at < decision_ts` (strict, +1 min). Both range -> 0. Add a lookahead lint plus a truncation test as in `test_context_asof.py`. State the venue. |
| F18 | LOW | Quotes and framing. "A precursor" is auto-captioned as "prereic kicate" ([00:18:16]); mark it [sic]/read-as. H-K2 says "the short works" (REPORT `:111`), but the wlow primary is LONG and live emits long. Other quotes and ids check out: lines 321-350 = [00:10:29]-[00:11:29], BBWP [00:05:33]-[00:05:40], worked example [00:16:57]-[00:17:24], all cited KR ids present in `KROWN_RULES.csv`. | transcript line ~553; `live_runner_cli.py:503-506`; wlow `PRE_REG.md` s5 | Fix the wording. Re-frame H-K2 on the long side. |

## 2. Amendments to the design (numbered; each replaces or adds to the cited section)
1. **Counts pass before any pre-reg (new s3.0).** On DEV, using timestamps and context only with no outcome columns, compute:
   - the D1, D2 and D3 shares per layer;
   - D3 coverage;
   - the S histogram per layer;
   - distinct ISO weeks per cell;
   - the MDE per layer with week clustering.

   Freeze the bands from these counts (coverage targets as in F10), never from outcomes. This is cheap, reads no outcome and
   decides whether the design is runnable.
2. **Standalone context read (new s3.1, satisfies the F5 rule).** Use the same fixed-horizon outcome for random entries, not
   triggers, with context-matched controls (`context_null.py`). Two questions:
   - (a) Does side-agreement with D1 predict the signed 24h net return better than the naive trend baseline (F12)?
   - (b) Does BBWP_4h/1d predict next-24h realised volatility?

   (b) is close to certain (volatility clusters) and yields a sizing input directly. Only a context that passes (a) may enter S.
3. **Outcome unit (replaces s4 "expectancy").** Net signed return over a fixed horizon per trigger tf, in % and in ATR(tf)
   units, at 0.10 % taker and 0.14 %. Add a maker-entry arm (0.02 % maker plus a fill-probability haircut) as a stated scenario,
   because BLOCKED.md (a) names maker modelling as the real unblock.
4. **Fee-wall metric (replaces s0.3(c), cost/R row).** Report gross % edge per cell against the cost %. cost/R stays a
   feasibility filter (< 0.25 R) and is never evidence of improvement.
5. **Inference (replaces s4 "Inference").**
   - SE clustered by ISO week, or a 20-day block bootstrap.
   - Year-split sign check: 2022 vs 2023-24H1.
   - Per-layer slopes combined by random-effects meta-analysis, with a weight cap.
   - A per-layer verdict only when MDE <= 0.10 R per S unit; otherwise descriptive.
   - One Holm family covering the pooled test, the per-layer slopes, T2, T4 and the context read. Log it next to the
     context_factors m = 37 family.
6. **D2 per event (replaces s3 D2 and s6.0).** Use the direction of the expansion relative to the event side, on 4h only. Drop
   the per-layer FADE/BREAKOUT table.
7. **Score structure (replaces "S = D1 + D2 + D3" as primary).**
   - Primary: D1 (with the trend baseline as competitor).
   - Secondary pre-registered contrasts: D2 (fade at an extreme vs fade into a fresh expansion) and D3 (edge vs middle).
   - S16 interaction cell: counter-trend x BBWP >= 85.
   - S stays as a descriptive summary.
8. **Placebo (replaces s4 placebo).** Context-matched random entries (verdict-bearing), plus a >= 30-day circular shift of the
   context series (200 shifts).
9. **Context as size, not gate (new s5.1).** Pre-register a sizing rule next to the filter, at the same total exposure:
   - weight = vol-target (1 / predicted vol from BBWP or realised vol);
   - optionally x (1 + 0.5 x D1).

   Evaluate the change in mean net % and in Sharpe at equal capital. Sizing uses the whole sample (no n loss), and vol-targeting
   is the most robust known improvement on BTC.
10. **Calibration (replaces s5).** Fit a logistic of target-first (or of sign(net)) on S with layer intercepts on DEV, plus 3
    reliability bins (S <= -1, 0..1, >= 2). Do not use per-S bins with n < 30 shrinkage, which empties exactly the S = +/-3 cells.
11. **Trade trials (replaces s6).**
    - T2 primary: Krown S8 on 4h, structural stop, BBWP-peak exit; no flow conjunction (it halves n).
    - T4 descriptive.
    - T1 re-specified on 1h with a k x ATR stop chosen so that cost/R <= 0.15, or dropped.
    - T3 target = opposite range edge, not the 15m mid.
    - T5 moved to the forward call ledger.

    DEV + DEV_EXT 2020-21 for all, VALIDATION once.
12. **Layer survivorship (new s8 bullet).** Every trigger in the pool already failed or was inconclusive on this same DEV, so
    re-reading DEV conditional on them is a second look. Treat any pooled positive as hypothesis-generating until DEV_EXT agrees
    in sign. Only then spend the single VALIDATION read.
13. **Ideas worth one row each in the trial ledger (no new build):**
    - meta-labeling: logistic on D1/D2/D3 plus funding over the frozen trigger, purged by week;
    - horizon extension: the same trigger with a 4h/24h exit, to raise gross move per unit cost;
    - funding-sign interaction with side (KR-LQC02, funding only).

## 3. Top-3 priority (max information per cost)
1. **Amendment 1 counts pass plus the registry fixes** (Haiku/Sonnet, S). No outcome is read. It decides which layers and
   cells are testable at all, and it fixes D2/D3 definitions before anyone sees a return. Fold in REPORT card 1 (A1/A2 registry
   and STATE corrections); it is free.
2. **Amendment 2 standalone context read**, reusing `context_asof.py` and `context_null.py` (Sonnet, M):
   - D1 vs the naive trend baseline on random entries;
   - BBWP -> realised-vol forecast;
   - both on DEV + DEV_EXT.

   If D1 does not beat the trend baseline, the Krown CONTEXT role is closed cheaply. The vol forecast almost surely passes and
   directly feeds amendment 9 (sizing), the cheapest fee-wall lever after maker execution.
3. **One trade trial: T2 (4h compression breakout, structural stop) with a maker-entry scenario** (Sonnet, M). It is the only
   candidate whose stop geometry clears the fee wall by construction (cost/R << 0.25) and is SOURCED in structure (KR-Q05/Q06).
   Pre-register it alone, on DEV + DEV_EXT, then VALIDATION once.
