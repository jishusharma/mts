# RSI "buy the lowest RSI" - Opus framing and critique (2026-10-20)

Status: thinking only. No backtest was run, no data touched. Every number below is either arithmetic I show, a quote from a prior file (path:line), or labelled OURS (judgement). Fee-net out-of-sample results decide, never this document.
Read with `SPEC.md` (Supervisor v3). Where this file and SPEC disagree on scope or order, this file wins until the PRE_REG is written.

## 0. Short version

1. The idea is testable and cheap to kill. Kill it first at the economic floor (section 1, H1), before building depth maps, context tables or an engine.
2. "Lowest RSI" can never be known at the time. What a trader can know is a state ("RSI just hit L, n-th time this window, X hours since the last touch") and what that state did before. The honest output is P(price makes a lower low within N bars | state), a survival curve, never a yes/no.
3. RSI low is not price low. RSI measures how one-sided the last ~14-30 bars were, not how far price fell. A single -5% bar drops RSI 62 -> 13; a 33-bar grind of -0.02% per bar (-0.7% total) reaches RSI 20 (my demo, section 2.1). So an RSI-level ladder and a %-price ladder are different things.
4. No-stop plus doubling does not create edge, it reshapes the distribution: many small wins, rare ruin. Worked example: section 2.4 (a 1.05% win vs a 45.7% mark-down).
5. SPEC v3 is over-built for a first look (thousands of cells, three label schemes, nine TFs, six lookbacks) and has real gaps (undefined E1/E2, higher-TF alignment rule, survivorship, regime imbalance). Section 2.
6. Plan: five stages, each with a kill; the first is one script on BTC 1m (section 5).

## 1. The idea restated: four hypotheses with kill criteria

Common protocol (SOURCED where noted, else OURS): RSI14 Wilder on close (SOURCED, operator; `rsi_core.py:7`), UTC bars, fee 0.10% round trip (SOURCED, `backtest/fees.py`, SPEC s1), fill = next bar open, DEV 2022-01-01..2024-06-30 / VALIDATION 2024-07-01..2025-06-30 / HOLDOUT read once (SPEC s5). Unit of evidence = independent DAYS, not events (events cluster in crashes). Baseline for every comparison = matched random bars (same time of day, same trailing-volatility tercile), because after any fall the forward range is larger and a naked mean says nothing.

**Event definition (fixed, OURS):** an EPISODE START = RSI(t) closes at or below level L after being at least h=3 points above L (hysteresis h=3, fixed, not varied; SPEC varies h in 3 values: pointless early). Levels L are either absolute (30, 20, 10) or relative-causal (RSI at or below the trailing-90d 2nd percentile for that TF; section 4.3).

- **H1 Economic floor.** After an episode start at a deep level, the gross forward return minus the matched baseline exceeds the 0.10% fee on some TF.
  Kill: on every TF in the Stage-0 set, the upper end of the day-clustered 95% CI of (gross minus baseline) at the best horizon is below 0.10%. All TFs dead = stop the whole study; do not build the engine.
  My prior (OURS, judgement, not a result): 1m-5m die here (10 bp is 1-3 typical 1m bar ranges; prior divergence work shows gross of 0.00% +-0.05% at 1m-15m, REPORT.md:7-30). 1h-4h may survive but with tiny n.
- **H2 State matters.** The probability of "bounce" and of "new lower low" depends on how rare the reading is relative to its recent past (trailing floor, time since last touch, macro regime), beyond the absolute level.
  Kill: a walk-forward predictor with the context beats the level-only predictor on neither log-loss nor reliability on VALIDATION. Then the answer is the unconditional table and Step F of SPEC is dropped.
- **H3 Confirmation helps.** At least one causal confirmation (section 3) lowers P(new lower low within N bars) enough that net EV per day, after paying the delay, beats entering at the raw RSI touch.
  Kill: no confirmation improves fee-net EV per day over the raw touch on DEV and VALIDATION, same sign. Then "buy the low" cannot be filtered and stays an all-or-nothing bet.
- **H4 The operator's full trade survives.** Entry at the deep reading, scale-in, no price stop, exit at RSI 40/50/60 or divergence is fee-net positive per day AND the capital needed to survive its worst episode is within a stated bankroll, on BTC, ETH, SOL and on assets that did not recover.
  Kill: any of (a) fee-net per day not above 0 on DEV and VALIDATION, (b) ruin test fails (section 2.4) on the 2022 bear or on a non-survivor, (c) result sign flips between bear and bull sub-periods.

## 2. What SPEC v3 got wrong, missed or over-built (blunt)

### 2.1 RSI mechanics the SPEC treats too lightly
- RSI is path dependent and bounded. Wilder smoothing gives it a memory of roughly 2x14 = 28 bars with exponentially fading weight; the seed matters for ~200 bars (warm-up needed; the first value depends on where the data starts).
- RSI is scale-free. Synthetic check (seed 1, 60 mixed +-0.1% bars then straight falls; computed with `rsi_core`): fall of 0.02%/bar reaches RSI 30/20 after 25/33 bars, never 10 in 40 bars; 0.1%/bar reaches 30/20/10 after 10/16/25 bars (-2.5% total); 2%/bar after 1/2/4 bars. One -5% bar after quiet bars: RSI 61.7 -> 12.7. Consequence: "RSI 12" on 1m can be a 0.5% drift or a 5% crash. Position-size ladders keyed to price % and exits keyed to RSI levels mix two unrelated scales. Report price depth (and depth in ATR) next to every RSI level.
- RSI low is not price low. In a persistent fall RSI bottoms when the fall is steepest and most consistent, usually before price bottoms; it then rises while price grinds lower (that is a bullish divergence, and it is the common case, not a special one). So "buy the lowest RSI" systematically buys into momentum, early.
- RSI "bounce 80%" is nearly mechanical: one up-close lifts RSI. The informative number is price: P(close above fill by more than fee within H) and the adverse move before it. Report RSI bounce only as an intermediate for the exit rule.
- A level's rarity is time-scale dependent (a 1m RSI of 10 is common on crash days, a 1d RSI of 10 is a handful of dates), and "unvisited for years" is untestable for 1m: the file has 4.8 years (2022-01..2026-09). Anything rarer than the sample is extrapolation (section 4.4).

### 2.2 Look-ahead traps (SPEC mentions some, misses the worst)
1. **Higher-TF alignment (missed).** A 1h RSI "resampled from 1m" is only known at the 1h bar close. Using the 1h value at a 1m event inside that hour is look-ahead. Rule: any higher-TF feature = last COMPLETED bar, shifted one. Needed for F2, divergence TF D != entry TF, and confirmation C7. The PRE_REG must state it and a planted-future-bar test must cover it.
2. **Trough rank and window minimum (partly caught).** Step A ranks troughs with +-k bars and calls the lowest "rank1": known only after the window ends, and a trough is confirmed k bars late. Fine as a description for the operator; forbidden as a condition. The usable causal object is the running record: "RSI just printed a new low for this window / this lookback, record number n". Section 4.1.
3. **Fixed UTC windows (over-built).** An episode straddling 00:00 is split into two "lowest of window" events; each new window restarts the record count. Use a trailing window (last W hours/days at each bar) for anything tradeable; keep fixed windows only for the operator's descriptive curve.
4. **Macro labels need history before DEV (missed).** 200d average and "30d range width vs its 1y percentile" need a year of data before 2022-01-01. The 1m file starts 2022-01 (`F:/MTS/data/tom_raw/klines/BTCUSDT-1m-2022-01.csv`). Either fetch 2021 (free public, pre-approved) or leave 2022 unlabeled. Stage 2 card must decide; default in section 6.
5. **Divergence swing confirmation.** `rsi_divergence.py` stamps one bar after the second swing (`RSI_2A_SPEC.md:54`); a swing needs bars after it to be recognised, so check the stamp is not earlier than the confirming bar. Cheap test, put it in the engine card.
6. **Reusing VALIDATION to pick memory length, rarity line, TF.** SPEC says DEV only: keep it that way; any "which memory length predicts best" is a DEV question.

### 2.3 Multiple testing, clustering, over-building
- Cell count. 9 TFs x 4 windows x 46 levels x k x h x q x d x b x H, then 3 macro schemes x 6 states, 6 lookbacks, then 6 exits x 4 ladders x 3 M x 3 a x 5 D. SPEC itself expects "a few thousand cells". With ~900 DEV days, most cells hold under 30 independent days; Holm over thousands means p below ~1e-5 and the MDE is huge. The cells are also highly correlated (neighbouring levels), so Holm is both too harsh and not the right structure.
  Fix: 4 hypotheses (section 1), 3 TFs for the first pass (1m, 15m, 1h; add 5m/4h/1d only where H1 survives), 3 absolute levels + 1 relative level, one h, one k, one b, one fixed horizon set. Everything else is exploratory and labelled so.
- Events cluster. A crash day gives hundreds of 1m episode starts. SPEC counts effective N in days (good). Add: cluster again by "stress cluster" (consecutive days with RSI-low episodes) in the CI, otherwise a single week like 2022-06 or 2022-11 looks like 30 independent days.
- Rank 2..5 troughs inside one hour are the same sell-off. Not independent evidence.
- E1/E2 are undefined. SPEC s2 "Entry arms (E1/E2 as before)" points at an earlier draft not in the file; card `rsi-deep-prereg` cannot freeze what is not written. Definition adopted here: E1 = first down-cross of the absolute level L (fill next open); E2 = same with relative level (trailing quantile); E3 oracle = true window min, diagnostic only (can never be traded).
- X5 divergence exit will rarely bind. After an entry at RSI 15 the exit at 40 is usually hit before two RSI swing highs form. X5 only matters combined with X3 (hold to 60, leave on bearish divergence). Test it only as "X3 + divergence", not alone.
- Malkan source mismatch to state loudly. His method is daily/weekly/monthly Indian equities with a candle-based stop and a price target (`RSI_2A_SPEC.md:17-31`), and he says bullish divergence is strongest near 40 and that at the 20/80 extremes reverse divergences negate it (`RSI_2A_SPEC.md:23`, Wvq1 D3). The operator rule (deepest RSI, no stop, 1m) is OPERATOR hypothesis, not Malkan. Do not describe it as his.
- Cards route to stalled lanes. `ROUTING.md` conflicts C2 and C7: GPT lab stalled (16 ready, nothing ran 17 h), DSA-NB rows untaken 75 h. A chain whose engine is lane CODEX and whose runs are DSA-NB may sit for days. Section 5 gives fallbacks.
- Already known, do not redo: divergence as an ENTRY on 1m-1w, BTC 2022-2026, is net negative (1m malkan bullish n=28961, net -0.096%, t -65; 1h bullish -0.036%, t -0.43; REPORT.md:7,35); RSI 40/60 bounce/reclaim events on 1h DEV show MFE about equal to MAE, no directional edge unfiltered (layer_lab reports 2026-10-17; 982 and 132 events, MFE 2.8 vs MAE 2.9 R and 3.18 vs 3.06 R); weekly-low bounce with BB/RSI60 INCONCLUSIVE n=8 (`wlow_bounce_bbrsi60_2026-10-16/RESULT.md`); generic-bracket RSI backtests no edge (`RSI_HISTORY.md` s4). What was NEVER tested: entry at a DEEP absolute or relative RSI level (<=30/20), the depth distribution itself, any scale-in or no-stop exit, RSI-level exits (the old tests used 1%/2% brackets), any confirmation study at an RSI low.

### 2.4 No stop plus scale-in: ruin arithmetic (worked example, spot, 1x, no leverage)
Unit u = $1,000. Entry 1u at price 100, then add on every further -2%, doubling: 2u, 4u, 8u, 16u, 32u. Fills at 100, 98, 96.04, 94.12, 92.24, 90.39 (exact: 0.98^k). Total deployed $63,000, quantity 684.5, average cost 92.03.
- Win: price only has to climb to 92.03, which is 1.8% above the last fill and 8% BELOW the start. Exit at 93: +$662 = +1.05% on capital deployed. Exit at 95: +$2,031 (+3.2%). Fees on 6 fills about $63 (0.10% of deployed) are already 10% of the small win.
- Loss, if price never returns: mark at 80: -$8,237 (-13.1%); at 70: -$15,082 (-23.9%); at 60: -$21,928 (-34.8%); at 50: -$28,773 (-45.7%).
- Break-even win rate: with a +1.05% win and a -23.9% loss you need P(win) above 95.8%; against -45.7% above 97.8%. The strategy therefore shows a 95%+ hit rate and still has negative EV if the tail comes once in ~25-45 episodes. One -50% episode erases about 43 average wins ($28,773 / $662).
- Doubling creates no edge. If E[return] of each add is zero before fees it stays zero; it only moves outcomes from many small to few huge. It helps only if mean reversion strengthens as price falls (true in ranges, false in trends/crashes), and that is precisely what the test must show.
- Time is the second hidden cost: the losing tail sits underwater for weeks to years (the unrealised loss also blocks the capital). BTC drawdowns in the DEV window include 2022 (bear, dozens of RSI-low episodes in a row); approximate historical crashes outside it (March 2020 about -50% in two days; FTX Nov 2022 about -25% in two weeks; 2024-08-05 flush about -15% intraday; these are from memory, verify against the data) - 2020 is NOT in the data and would need fetching.
- Survivorship: BTC recovered every time. "Buy and never stop out" on BTC is the canonical survivor-biased backtest. Mandatory (not optional, SPEC called ETH/SOL optional): replay the same rules on ETH, SOL and on assets that went to ~0 (LUNA May 2022, FTT Nov 2022) if the Binance archives hold them, else report NOT_IN_DATA.
- Regime imbalance: DEV is mostly a bear and a recovery, VALIDATION (2024-07..2025-06) is mostly a bull. A dip-buyer looks great in a bull. Report every metric per regime year; the verdict "same sign in more than half the years" is weak with 3-4 years.
- What to do with "no stop": keep it as the operator's arm, but make it testable: (i) bankroll cap B (OURS: B = 20u): when deployed capital would exceed B, the position just waits, and the report states time-to-recover; (ii) a CONTROL arm with a capital-based catastrophe exit (-X% of B), because a price-based stop is what the operator rejects but a capital-based exit is the standard way to bound the tail; (iii) ruin test = minimum bankroll that survives each replay, reported before any mean.
- Primary metrics for this arm: fee-net per day, worst mark-down, longest underwater days, share of episodes unclosed at data end (marked, not dropped).

## 3. Confirmations at an RSI low (what a trader can measure causally on a "naked" chart)

Principle: a confirmation is a delay bought with information. It avoids some of the adverse move but gives up part of the bounce. Judge it by ONE curve: for each confirmation, P(new lower price low within N bars after the confirmation bar) and fee-net EV per day if you enter at the confirmation bar's next open, versus entering at the raw RSI touch. Everything below must be computable from bars up to and including the signal bar (higher TF = last completed bar, section 2.2).

Test first (Tier A: price and RSI only, no extra data; each is a one-line causal rule):
1. **RSI hook** (C1): RSI closes up by b points from its running minimum (b=3, fixed, OURS; 5 as a sensitivity) while still below the level. Cheapest, directly answers "did momentum already turn". Expect: removes some continuation falls, costs the first part of the bounce.
2. **Structure shift** (C3): first close above the high of the lowest bar of the episode (Malkan: bullish candle then entry on break of its high, `RSI_2A_SPEC.md:25`) or first higher low on the same TF. This is the naked-chart trader's version of "is this the low". Gives a defined price level too.
3. **Fall speed / climax** (C5): trailing return of the last 14 bars in ATR units and bar range z-score; a climax bar (large range, close in upper third = long lower wick) versus a slow grind. Tests the section 2.1 point: sharp capitulation and slow bleed behave differently.
4. **Higher-TF RSI state** (C7): HTF RSI (last completed bar of the next two TFs up) above 40, between 30 and 40, below 30. Malkan reads one TF up and one down (`RSI_2A_SPEC.md:31`, a T3 transfer). Buying a 1m RSI low when the 1h RSI is also deep is a trend-continuation bet; when the 1h is neutral it is a pullback.
5. **Volume and delta at the low** (C9): volume z-score of the low bar, and taker-buy share from the kline taker-buy column (available in the 1m klines: free CVD proxy, no extra data). Absorption (high volume, close off the low, taker-sell dominance shrinking) versus no volume.

Test second (Tier B):
6. **Time below the level / dwell** (C6): bars spent below L before the signal (operator Case A vs B, `RSI_2A_SPEC.md:9-10`, bucketed, no number picked).
7. **Location** (C8): distance below the lower Bollinger band, below VWAP of the day, and whether this is a NEW trailing 7d/30d price low (breakdown) or a higher low (retest). The wlow study used breakdown plus bounce (n=8, INCONCLUSIVE).
8. **Divergence** (C4): bullish RSI divergence at the low. Low priority: it already failed as a standalone entry on every TF (REPORT.md) and Malkan says it fails at 20/80. Include only as "does it change the hazard of a new low", not as an entry.
9. **Funding**: 8h resolution, usable as a slow state only.
10. **Candle patterns** (hammer, engulfing): one pre-registered family definition, lowest prior.

NOT testable on DEV: open interest (Binance metrics archive starts 2025-09-01, `wlow_bounce_bbrsi60_2026-10-16/RESULT.md` L1 NOT_IN_DATA) and liquidation data. Forward-collected only.

Rule for combining: one confirmation at a time first, then at most the best two together (pre-register the pair); no stacks of five (cell explosion, overfit).

## 4. The probability framework

### 4.1 What can be estimated honestly
Object: the EPISODE (section 1). State at the episode start s = (TF, level L or relative level, time since the same TF last touched L, record number n inside the trailing window, fraction of trailing window elapsed, volatility tercile, regime label optional). All of s is known at the start bar.
Estimable outcomes (each with a Wilson 95% CI and N in independent days):
- P(RSI makes a further d-point low | s) for d in {2, 5}: the depth question (operator b).
- P(price makes a lower low than the fill within N bars) and the distribution of the further drop (MAE): this is the "am I at the lowest" question.
- P(price above fill + fee within H bars), the size distribution of the bounce (p10/p50/p90), time to reach it.
- The survival curve S(n) = P(no lower price low within n bars) (Kaplan-Meier over episodes). It answers "how long must I wait to be 90% sure" as a curve, not a promise.
Null model for "is this the lowest": for i.i.d. returns, the chance that a record low at position n of N is the final record is n/N, so the only information is how much of the window is gone. Real data are more persistent; the gain of the state over n/N is the information content of everything in section 3.
Not estimable: certainty that this is the low; the probability of an event class with fewer than about 30 independent days.

### 4.2 Recent vs infrequent vs rare: why they differ statistically
| Class (causal, per TF, from trailing data only; OURS cut-offs) | Example definition | Expected sample (BTC, 900 DEV days) | Statistical issue |
|---|---|---|---|
| Recent / common | level touched in 3+ of the last 7 days | hundreds of independent days | plenty of N, but the answer is regime-bound; estimate on a rolling window and check calibration drift |
| Infrequent | touched in the last 90d but not in the last 7d | tens of independent days | usable with shrinkage to the neighbouring level |
| Rare | not touched in the last 365d (or at a trailing 2nd percentile) | single digits to ~20 days on BTC | cannot meet the 100-day verdict gate on BTC alone; only a bound |
With zero failures in n independent episodes the 95% upper bound on the failure rate is about 3/n: 18 days gives 17%, which cannot rule out a 1-in-6 failure. So for the rare class the study can only (a) pool, (b) bound, or (c) fit a tail model; it cannot "prove" a high bounce rate from BTC alone.
Pooling options (in order): smooth across neighbouring levels (monotone in L, isotonic / empirical-Bayes shrink to the 1-point-wider bin), across TFs for the same relative rarity, across assets (ETH, SOL, others) with the day-cluster correction (assets crash on the same days, so pooled N in days barely grows). Always show the shrunk and the raw estimate side by side.

### 4.3 Absolute vs relative coordinates
The operator's two examples are different questions: "RSI 22" (absolute) and "RSI hasn't touched 30 all week so look at 31-32" (relative to the trailing floor). Both are kept as coordinates; the primary one in Stage 2 is the RELATIVE causal one (RSI minus trailing-W floor, rank among the visits in W, hours since last touch) because it is what makes "rare" mean something. SPEC's Step C defines rare by P_touch below q, which makes the rare zone a fixed event frequency BY CONSTRUCTION (q is a quantile), so it cannot tell you whether rare events behave differently. Use q only to name classes; compare the outcome across classes.

### 4.4 Tails
Depth below a threshold u (RSI units below u) is a peaks-over-threshold problem; a generalised Pareto fit (finite endpoint at 0 since RSI is bounded) gives P(RSI < 10 | < 20) smoothly and can be checked against the empirical count. Use it for the rare class instead of a table of three events. Report the fit only if the empirical tail agrees on DEV.

### 4.5 Calibration and honesty
Walk-forward: each event's probability is built from events before it. Report a reliability table (predicted decile vs realised) and Brier/log-loss on VALIDATION. A probability cell is tradeable only if its VALIDATION realised value is inside its DEV interval and N >= 30 independent days (SPEC rule, kept).

## 5. Minimal staged plan (smallest experiment first; each stage has a kill)

| Stage | What | Cards | Cheapest model / machine | Kill |
|---|---|---|---|---|
| 0 | Economic floor (H1): BTC 1m DEV only, TFs 1m, 15m, 1h; levels abs 30/20/10 + relative 2nd percentile of trailing 90d; fixed horizons {1,4,16} bars + bounce/MAE + "lower low within N" + RSI-min to price-min lag + matched baseline. ONE script, one CSV, one table. Reuses `rsi_core`, `forward_excursion`. | NEW `rsi-deep-econ-floor` | Sonnet writes and runs (NB holds the 1m data; ~1 session). DSA-NB only if its queue is taken (stale 75 h) | all TFs below fee: stop the study, report |
| 1 | Operator's depth map (descriptive, SPEC Steps A-C) reduced to TFs that survived Stage 0 plus 1m/5m for the operator's curiosity; add the running-record (causal) table next to the ranked-trough table | `rsi-deep-depth-map` (edited) | Sonnet | none (descriptive); output decides the level grid |
| 2 | Hazard and context (H2): S(n), P(deeper), P(bounce > fee), rarity classes (4.2), walk-forward, calibration on VALIDATION once. Absorbs SPEC Steps D-F in one card | `rsi-deep-prob-tables`, `rsi-deep-context-tables` | Sonnet; DSA-NB run if exact commands | context no better than level-only: drop it |
| 3 | Confirmations (H3): C1, C3, C5, C7, C9 one at a time, then best pair; same curve for each | NEW `rsi-deep-confirmations` | Sonnet; independent re-derivation of the top cell by GPT luna (NUC) or Gemini Flash review | none helps: unfiltered idea stays, H4 is tested raw |
| 4 | Freeze: PRE_REG with E1/E2/E3 defined, higher-TF rule, grid cut to survivors, ruin rule, regime split. Then the episode engine (entry arms, X1-X5 as listed, S0-S3, bankroll cap B, capital-exit control, non-survivor assets). | `rsi-deep-prereg`, `rsi-deep-engine`, `rsi-deep-run-dev` | prereg Sonnet; engine: CODEX lane is stalled (ROUTING C2): default Sonnet builds, GPT/Gemini re-derives the top cell; run DSA-NB with Sonnet fallback after 24 h | H4 kills: sign, ruin, or regime flip |
| 5 | VALIDATION once, Gemini cross-vendor review before, HOLDOUT once for survivors; ruin test reported first | `rsi-deep-crossvendor-review` (SPEC card 5, not yet created) | Gemini Flash via `gemini_queue.py` (producer != reviewer) | same-sign and ruin gates |

Gemini review of THIS document and SPEC for look-ahead (section 2.2) is a cheap pre-step before Stage 0 (10 minutes of Flash); not a card unless the coordinator wants one.
Ordering change vs SPEC: SPEC runs depth map first and prereg after context tables; here Stage 0 comes first (it can end the study), and PRE_REG is written once Stage 3 has told us which confirmations and levels are alive, not before the engine grid is cut.

## 6. Questions for the operator (defaults taken, no answer needed)

1. Which TFs first? Default: 1m, 15m, 1h (Stage 0); 5m, 3m, 4h, 1d only where 1m/15m/1h show something. Operator listed 1m, 2m, 3m, 5m: 2m and 3m are near-duplicates of 1m/5m on the same tape, added only on request.
2. Is a bankroll cap acceptable? Default: yes, B = 20u in the headline, with "no cap" reported as a second line so the operator sees both; a capital-based catastrophe exit as control only.
3. Macro labels (trending / consolidating / accumulation / distribution) need pre-2022 history. Default: use 2022-01..2022-12 as warm-up for labels from 2023 (macro phase tested on 2023-01+ only), and fetch 2021 free public klines only if Stage 2 needs the 2022 bear labelled.
4. Rare class definition. Default: "not touched at or below the level in the last 365d" and "trailing-90d 2nd percentile", both reported.
5. Non-survivor assets. Default: ETH and SOL for H4; LUNA 2022-05 and FTT 2022-11 from the free archives if present, else NOT_IN_DATA stated.
6. Exits. Default: X1 (RSI 40), X2 (50), X3 (60), "X3 + bearish divergence on D in {entry TF, one TF up}"; X4 Malkan loop and X6 time stop as controls. D in {1m,2m,3m,5m,15m} is cut to two values until something survives.
7. Perp 3x arm. Default: dropped from the headline; funding file sensitivity only after H4 passes.
8. Does the operator want a human-readable live chart read tool ("is this a deep reading now")? Default: not before Stage 3; the study's output should first say whether any state has an edge.

## 7. Label table for parameters I introduce (SOURCED vs OURS)

| Parameter | Value | Label |
|---|---|---|
| RSI period 14, close | 14 | SOURCED (operator; Wilder) |
| Fee round trip | 0.10% | SOURCED (`backtest/fees.py`, SPEC s1) |
| Exit levels 40 / 50 / 60 | 40/50/60 | SOURCED (operator message; Malkan loop `WEB_RESEARCH.md:42-43`, T3 transfer) |
| No price stop | yes | SOURCED (operator) |
| Divergence min bars | 3..10 | SOURCED (Malkan, `RSI_2A_SPEC.md:21-22`; T3) |
| Hysteresis h | 3 | OURS, fixed |
| Hook b | 3 (5 sensitivity) | OURS |
| Absolute levels 30/20/10 | | OURS (operator named 20 and 80/90 as rare; 30/10 added) |
| Relative level | trailing-90d 2nd percentile | OURS |
| Bankroll cap B | 20u | OURS |
| Scale-in step a, M | per SPEC s3 (0.5/1/2%, M 2/4/6) | OURS; cut to a=1%, M=4 plus ATR-scaled sensitivity in the first pass |
| Rarity cut-offs 7d/90d/365d | | OURS |
| Matched baseline (time of day x vol tercile) | | OURS |
