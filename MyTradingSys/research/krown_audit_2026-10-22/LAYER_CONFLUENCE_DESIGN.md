# Using the layers together: a confluence design for MTS (2026-10-22)

> **v2 after independent review (REVIEW_OPUS.md, SOUND WITH FIXES).** Section 9 supersedes sections 0.3(c), 0.6, 3, 4, 5, 6 and 7
> where they conflict. Kept: the role idea (s2), the independence rule, "what not to do" (s8). Read s9 first.

Follows `REPORT.md` (Krown audit). Question from the operator: how should the layers be used together so trades have better
edge, confluence, confidence and accuracy? This is a design, not a result. Every threshold below is OURS unless a ledger id is
given. Nothing here may be wired live before a DEV result and one VALIDATION read (CLAUDE.md, PROJECT_VISION "isolate, then combine").

## 0. Answer in eight lines
1. No single layer has passed fee-net on its own (LAYERS.md status lines: Tom stopped, Fabio v3 OOS FAIL, cryptocred FAIL, positioning
   C1 FAIL, session T087 FAIL, divergence no edge, wlow_bounce INCONCLUSIVE, OPR-BB-MTF-CENTER INCONCLUSIVE/FAIL, wavetrend FAIL/INCONCLUSIVE).
2. The binding constraint is the **fee wall**, not the hit rate: bb_top_reversal (15m) has a median stop 0.29 % away, so 0.10 % taker
   round trip = 0.349 R before any edge, and the power gate says no sample size passes (`bb_top_reversal_2026-10-18/BLOCKED.md`).
3. So confluence must do one of three things, measured separately: **(a) filter** (raise win rate at the same R), **(b) select
   bigger moves** (raise realised move per trade so cost/R falls), **(c) relocate** the trade to a structural level that allows a
   wider stop with the same reward multiple (cost/R falls). Vote-counting indicators does none of these by itself.
4. Layers get **roles**, not votes: CONTEXT (where/direction), REGIME (when), LOCATION (structure), TRIGGER (momentum/flow),
   RISK (stop, target, size), JUDGE (external calls). One role is filled by one layer at a time; same-object layers are not counted twice.
5. Krown fills CONTEXT, REGIME, LOCATION and part of RISK, which are exactly the empty slots: today every live adapter is a TRIGGER firing alone.
6. Test design: one pre-registered **context score** per event (3 ordinal dimensions), a **pooled** test across all trigger layers
   (layer fixed effects, day-clustered SE) plus one monotone test per layer: few tests, more power, Holm across the family.
7. Confidence = a **calibrated probability** per trade from DEV bins, checked once on VALIDATION (Brier score, reliability table),
   never a hand-weighted score.
8. Expected outcome, honestly: the context filter may turn some INCONCLUSIVE layers into small positives by removing the worst cells;
   it will not rescue a 1m trigger from the fee wall. The candidate trades in section 6 move triggers to 15m-4h for that reason.

## 1. What the evidence allows (inputs to the design)
| fact | source | design consequence |
|---|---|---|
| Every layer alone is FAIL/INCONCLUSIVE/untested | LAYERS.md status lines | combination is the only open route; but stacking also multiplies tests: control the family |
| 1m-15m stops are inside the cost band | bb_top BLOCKED.md (0.349 R cost) | prefer 1h-4h triggers or structural stops; report cost/R per cell |
| Event tables exist for 15 layers on DEV | `research/layer_lab/*_event_table/` (bb_top 1,577 events 15m; malkan 132 1h; divergence 643 1h/4h; session levels, candle patterns, funding, OI, fabio escalation/LVN, cc_msb, turn_of_candle, volume, bigtrade) | the join is cheap: one context table x existing events |
| wlow_bounce pre-reg rule: "no combined stack; a layer matters only if its own side passes" | `wlow_bounce_bbrsi60_2026-10-16/RESULT.md` | the stack test must be pre-registered as its own trial, not a variant hunt inside a layer study |
| Guidance cross-filters (Tom/Fabio x BB, LVN, regime) found no surviving cell (Q33) | LAYERS.md `guidance` | cell-hunting across many filters already failed once: use few ordinal dimensions, not many binary cells |
| Krown's own order: trend > volatility > structure > momentum | hNfjyrJEytI 00:10:22-00:10:50 (transcript on disk) | the role order below is SOURCED from him; the thresholds are OURS |
| Malkan's daily-60 sell sits inside monthly/weekly RSI < 40 | `extract_2HcJ3NeZmEQ.md:39-58` | same object as Krown's RSI regime: one dimension, not two |

## 2. Roles and which layer fills each
| role | question it answers | candidates (best first) | evidence state |
|---|---|---|---|
| CONTEXT | which side may I trade? | Krown trend_1d/1w + topdown agree (KR-L10, T03); weekly 55 EMA side (KR-M10); daily RSI regime 40/60 (KR-S03 = Malkan MTF) | built in krown_core, untested as a filter |
| REGIME | is now a fade market or a breakout market? | Krown BBWP 1d and 4h/1h (KR-Q01/Q02, Q07); range mode (KR-T06/T07); positioning heat (funding + OI, KR-LQC02) | BBWP built; intraday BBWP OURS |
| LOCATION | is price at a level that matters, and where does the stop go? | Krown ranked daily zones + range edges (KR-Z, KR-R01); levels confluence KEEP families (prior-day H/L, POC, naked POC, 4h fractals, round 1000, prior-week high); session levels; weekly low (wlow) | LC built live; Krown zones built |
| TRIGGER | did the market just say "now"? | bb_top_reversal 15m, MAL-BB-RSI-4060, rsi_events 40, malkan bull/bear 1h, rsi_divergence 1h, candle_close, fabio escalation/CVD absorption, turn_of_candle, cc failed_msb | all live as sampling adapters |
| RISK | stop, target, size | stop: Krown structural (far side of zone/compression, KR-Q05; close back beyond zone, KR-X01); target: range height (KR-R07), opposite edge, 55 EMA minimum target (event-study family), BBWP peak exit (KR-Q06); size: down as BBWP rises (KR-P02 spirit), throttle when funding hot (KR-LQC02) | none tested |
| JUDGE | does an outside analyst agree? | Krown daily call ledger; callers layer (Qriptal, RLinda ...) | collect forward only |

Independence rule (OURS): two layers that compute the same object fill **one** slot. Same-object pairs found so far: Krown RSI regime and
Malkan MTF RSI; Krown range edges and Tom balance edges (KR-S3/TOM-2); Krown BREAK-CLOSE and candle_close; Krown zones and
LC prior-day/fractal levels when within 0.25 ATR (to be measured, not assumed).

## 3. The context score (what gets pre-registered)
Three ordinal dimensions, each with three levels, computed at the last **closed** 1d bar before the event (and 4h for REGIME):
- **D1 direction fit** (+1 / 0 / -1): event side agrees with trend_1d and trend_1w (+1), one agrees and one is range (0), any disagrees (-1).
- **D2 regime fit** (+1 / 0 / -1), by event type: for a FADE trigger (band-touch reversal, divergence, level rejection): BBWP_4h >= 85 -> +1,
  normal -> 0, BBWP_4h rose from <= 30 within 6 bars -> -1; for a BREAKOUT/continuation trigger the signs flip. Event type is a fixed
  property of each layer, written in the pre-reg (table in 6.0), never chosen after the run.
- **D3 location fit** (+1 / 0 / -1): event within 0.5 ATR14(1d) of a ranked Krown zone or range edge on the correct side (+1), in the
  middle third of a daily range (-1, "no man's land" KR-R01), otherwise 0.
Score S = D1 + D2 + D3 in [-3, +3]. Primary hypothesis per layer: fee-net expectancy is **monotone increasing** in S (one ordinal test).
Pooled hypothesis: across all trigger layers (layer fixed effect), the slope on S is > 0. Secondary (descriptive, no verdict): each
dimension alone, to see which one carries the effect.
Why ordinal and few: Q33 already failed with many binary cross-filters; three ordinal dimensions = 1 slope per layer + 1 pooled slope.

## 4. How "better" is measured (all fee-net, DEV only)
| metric | definition | why |
|---|---|---|
| expectancy | mean R per trade after 0.10 % taker round trip (or 0.14 % per study convention, stated) and funding | the only thing that pays |
| cost/R | round-trip cost / stop distance | shows whether a filter beats the fee wall by relocation (c) |
| realised move | median abs move to the first of target/stop/time, in % | shows selection of bigger moves (b) |
| hit rate | share of trades reaching target first | (a) only; never reported alone |
| MAE/MFE | as in `layer_lab/forward_excursion` | stop and target placement |
| calibration | Brier score and reliability table of the per-S probability of target-first | "confidence" must mean a probability that holds |
| placebo | same events with the context row of a random other DEV day (drawn without replacement, same weekday mix), 200 draws | proves the context, not the trigger, carries the slope |
Inference: SE clustered by UTC day; Holm across the pre-registered family (pooled + one per layer); MDE at 80 % power reported before
any outcome is read; a layer with n < 100 is "underpowered" and only joins the pooled test.

## 5. Confidence and accuracy for a single trade
Output per alert (alert-only first): `{side, trigger layer, S, D1, D2, D3, p_target_first (DEV-calibrated by S bin), stop (structural),
target (rule), cost/R}`. p comes from DEV frequency per S bin with a Wilson interval, shrunk to the layer's overall rate when the bin
has n < 30. It is a reading, never a gate, until VALIDATION confirms the slope and the calibration.
Accuracy improvement then has a measurable meaning: the share of alerts in S >= +2 and their realised p vs the stated p on VALIDATION.

## 6. Candidate trade designs (each is one pre-registered trial; numbers OURS unless cited)
### 6.0 Event type per trigger (fixed now, for D2)
FADE: bb_top_reversal, rsi_divergence (regular), MAL-BB-RSI-4060, wlow_bounce, level rejections (LC, session levels), cc failed_msb.
BREAKOUT/CONTINUATION: candle_close (close-through), fabio escalation, rsi_events 40 reclaim with trend, malkan setups, Krown S8, hidden divergence.

### T1 Trend-aligned Bollinger mid rejection (the operator's RSI + BB short, moved off 1m)
- CONTEXT D1 +1: trend_1d down and trend_1w not up; daily RSI regime bear or range (KR-S03 = Malkan filter).
- REGIME: BBWP_1h not "rising from <= 30 within 6 bars" (no fade into a fresh expansion).
- LOCATION: price below the daily range midpoint or within 0.5 ATR(1d) under a ranked daily ceiling zone.
- TRIGGER: 15m bar wicks to the 15m BB mid and closes below it while RSI14(15m) turns down from 55-62 (operator's "60 rejection"; OURS band).
- RISK: stop above the higher of the 15m upper band and the zone's wick edge (structural); target the 15m lower band, then the range low;
  report cost/R; skip if cost/R > 0.25 (OURS).
### T2 Compression breakout with a flow trigger (Krown S8 x Fabio)
- REGIME: BBWP_4h <= 30 within the last 5 bars (KR-Q02 band, 30 OURS pick), now crossing > 50 (KR-Q02 confirm).
- CONTEXT: side = prior trend_1d (KR-L12 bias from the previous trend).
- TRIGGER: first 1h close beyond the 4h compression range, with fabio escalation or CVD in the same direction on 15m-1h.
- RISK: stop = close back inside beyond the far side of the compression zone (KR-Q05, SOURCED structure); exit when BBWP_4h >= 90
  then falls below its MA (KR-Q06) or range height reached (KR-R07).
### T3 Zone fade at a volatility extreme (Krown S16 x divergence x BB top)
- REGIME: BBWP_4h >= 85 (KR-Q02). LOCATION: within 0.5 ATR(1d) of a ranked daily zone or range edge. CONTEXT: D1 >= 0.
- TRIGGER: bb_top_reversal (15m) or regular rsi_divergence (1h) at that zone.
- RISK: stop beyond the zone's wick extreme (structural, wider than the candle high: relocation lowers cost/R); target the BB mid of the
  trigger tf, then the opposite range edge.
### T4 Weekly-low sweep and reclaim (wlow x Krown fake-out filter)
- LOCATION: prior ISO-week low (wlow). Krown rule: "act on the close back inside with proof" (KR-R02; extract_6aA-P4Gvhrc.md:182).
- TRIGGER: 1h close back above the weekly low within 1-3 bars of the poke (K-FILT window, OURS) + RSI(1h) back above 40.
- CONTEXT: trend_1w up or range. RISK: stop below the sweep low; target the weekly range midpoint, then the prior-week high (LC family).
### T5 Hidden-divergence continuation after a volatility base (his worked example)
- Source: hNfjyrJEytI 00:16:57-00:17:20 ("volatility base out at very low levels ... lower high on hidden bearish divergence within the
  context of a downtrend ... volatility goes up ... price continues in the same direction of the trend").
- CONTEXT trend_1d (and 1w) defined; REGIME BBWP_1d (or 4h) <= 30 in the last 10 bars; TRIGGER hidden divergence in the trend's direction
  on 4h/1d (KR-S14, MAL-7..9); RISK stop beyond the divergence swing; exit at BBWP >= 90 (his "price action stalls there").
- This is a daily-book trade (days to weeks). It is the one design where the fee wall is irrelevant and the sample is smallest.

## 7. Order of work (cheapest first)
1. `krown_context.py` + DEV backfill (one row per 1d/4h close). 2. Join with the 15 existing DEV event tables; compute S; MDE table
   before outcomes. 3. Pre-register the pooled slope + per-layer slopes + T1-T5. 4. Run DEV once. 5. VALIDATION once for whatever passes
   (one pooled trial). 6. Alert-only tags on testnet (the `htf_context_live.py` pattern). 7. Gate only after 5.

## 8. What not to do
- Do not add votes ("4 of 7 indicators agree"): correlated layers inflate the count and Q33 shows the cell-hunt fails.
- Do not tune S thresholds on DEV outcomes; the bands above are fixed before the run, alternates go in the trial ledger.
- Do not use Krown's hit rates or medians as inputs; they are hypotheses.
- Do not read VALIDATION 2024-07-01..2025-06-30 more than once, never HOLDOUT 2025-07-01..2026-09-30.
- Do not let a context filter run live as a gate before step 5.

## 9. v2: what changed after the Opus review (supersedes the sections named in the header)

### 9.1 Facts the v1 design missed
- **A context study already ran on this question**: `research/context_factors_2026-10-16/RESULT.md`, INCONCLUSIVE: operator context
  composite on 1h decisions, effect E = -0.0233 R (SE 0.0739), all 1,010 C trades net -0.137 R, matched days 241 of 387 needed,
  Holm family m = 37. Tools `context_factors_pit_2026-10-16/context_asof.py` and `context_null_2026-10-16/` exist and are reused, not rebuilt.
- **Governance**: PROJECT_VISION.md:262 "Confluence may gate a trade only after each input passed S3 on its own." The Krown context has
  never passed alone, so it must get a standalone read first (9.3 step B).
- **DEV is 2022-01-01..2024-06-30 for the intraday event tables** (912 days). trend_1d/1w is close to a year dummy (2022 bear,
  2023-24H1 bull): a trend slope mostly measures drift. Cluster by ISO week, split 2022 vs 2023-24H1, and add DEV_EXT 2020-2021
  where 1m/15m data exists (Krown fire counts already used 2020-01.. from local 1m files).
- **Route (c) "relocate the stop" is arithmetic, not edge**: net R = (gross % - cost %) / stop %. A wider stop cannot change the sign.
  The fee-wall metric is gross % edge per cell against cost %; cost/R is a feasibility filter only (< 0.25).
- **R is not one unit across event tables** (stop distance, ATR14, spike range, none): pooled tests use a fixed-horizon net signed
  return in % and in ATR(tf), combined per layer by random-effects meta-analysis with a weight cap.
- Power: S = +3 holds about 1.6 % of events, S >= +2 about 12 % (REVIEW_OPUS F8); per-layer verdicts only when MDE <= 0.10 R per unit.

### 9.2 Roles, revised
- CONTEXT = D1 direction fit only, raced against a **naive trend baseline** (price vs a simple 1d moving average) so Krown's
  dominant-high/low trend must beat the cheapest alternative to earn the slot.
- REGIME = BBWP used **first as a volatility forecast for sizing** (near-certain to work because volatility clusters), and only second as a
  fade/breakout contrast. D2 is set **per event** from the direction of the 4h expansion relative to the event side, not per layer.
- LOCATION = D3 edge vs middle, with coverage bands frozen from counts (REVIEW_OPUS F10: a prior study found 90 % of DEV hours have a same-side level
  within 1 ATR(1h): a loose D3 is saturated).
- KR-S16 (counter-trend at a volatility extreme) is a pre-registered interaction cell, not cancelled inside an additive sum.
- S = D1 + D2 + D3 stays as a descriptive summary only.

### 9.3 Order of work (replaces s7)
A. **Counts pass, no outcome read**: D1/D2/D3 shares, S histogram, D3 coverage, distinct ISO weeks per cell, MDE per layer (week-clustered).
   Bands frozen from counts. Decides what is testable at all.
B. **Standalone context read** on random entries with context-matched controls (`context_null`): (a) does D1 predict the signed
   24 h net return better than the naive trend baseline? (b) does BBWP_4h/1d predict next-24 h realised volatility? Only a context that
   passes (a) may enter any trade filter; (b) feeds sizing.
C. **Sizing arm next to every filter**: weight = 1 / predicted vol (BBWP or realised), optionally x (1 + 0.5 x D1); compare mean net % and
   Sharpe at equal capital. Sizing keeps the whole sample.
D. **One trade trial: T2** (Krown S8 on 4h: BBWP_4h <= 30 then > 50, first close beyond the compression range, stop = close back
   beyond the far side (KR-Q05), exit at the BBWP peak (KR-Q06) or range height (KR-R07); no flow conjunction (halves n)); taker 0.10 %,
   0.14 % and a maker-entry scenario (0.02 % + fill haircut). T4 descriptive; T1 only re-specified on 1h with a k x ATR stop giving
   cost/R <= 0.15, else dropped; T3 target = opposite range edge; T5 moves to the forward call ledger.
E. **Pooled conditional read** of trigger layers on D1/D2/D3 (only if B(a) passed): fixed-horizon return, meta-analysis, placebo =
   context-matched random entries plus >= 30-day circular shifts of the context series (200).
F. Every positive on DEV is hypothesis-generating (all triggers already failed or were inconclusive on this DEV: survivorship);
   it must agree in sign on DEV_EXT before the single VALIDATION read.
One Holm family: context read (a), pooled test, per-layer slopes, T2, T4; logged next to the context_factors m = 37 family.

### 9.4 Confidence output (replaces s5)
Logistic of sign(net) (or target-first for T2) on D1/D2/D3 with layer intercepts, fitted on DEV, 3 reliability bins (S <= -1, 0..1, >= 2),
Brier on VALIDATION once. Shown as a reading on alerts; never a gate before F.

### 9.5 Ideas logged as single trial-ledger rows (no new build)
Meta-labeling (logistic on D1/D2/D3 + funding over a frozen trigger, purged by week); horizon extension (same trigger, 4 h/24 h exit,
to raise gross move per unit cost); funding-sign x side interaction (KR-LQC02; funding only, no OI before 2025-09).
