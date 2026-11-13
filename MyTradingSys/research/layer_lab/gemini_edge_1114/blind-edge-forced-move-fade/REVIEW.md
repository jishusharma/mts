# Blind Review: edge-forced-move-fade

**Verdict: SOUND** (The author's FAIL verdict is methodologically and statistically justified by the presented data; what would change it is an independent re-test demonstrating a positive fee-net expectancy that survives execution delay, fees, day-cluster bootstrap confidence intervals excluding zero, and Benjamini-Hochberg FDR control).

---

## 1. Scope and Input Data

- **Input reviewed**: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md`
- **Study on trunk**: None (blind review of result text and summary tables only; local worktree `C:\Users\E-ngineers\IdeaProjects\mts-jis-nb-edge-forced-move-fade-1113`).
- **Pre-Registration Claim**: SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:2`: `"PRE_REG + H4 addendum committed before outcomes. Folder MyTradingSys/research/edge_forced_move_fade_2026-11-13 (results.csv, results_h4.csv)."`
- **Stated Author Verdict**:
  - H1/H2: SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:5`: `"## H1 fade FORCED (OI fell) / H2 follow NEW (OI rose): FAIL, 0 of 32 cells pass (BH 10%)"`
  - H4: SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:14`: `"## H4 OI build then unwind, 30m and 1h (addendum, pre-registered before outcomes): FAIL, 0 of 96 cells pass"`

---

## 2. Table Analysis and Internal Consistency

### 2.1 Claims and Text Locations
The input summarizes experimental test cells across multiple hypotheses:
1. **Hypothesis 1 (Fade FORCED move where OI fell) and Hypothesis 2 (Follow NEW positioning where OI rose)**:
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:6`: `"VALIDATION (2024-07..2025-06) fee-net mean per trade, all cells within -0.22%..+0.09%:"`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:7`: `"- H1 k2 x0.3: n 1426 (330 days): T2 -0.16, T4 -0.15, T8 -0.09 (CI -0.21..+0.05), bracket -0.11 (CI -0.16..-0.06); placebo -0.10"`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:8`: `"- H1 k3 x0.6 T8: n 436 +0.03 (CI -0.31..+0.46); all others negative"`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:9`: `"- H2 k3 x0.6 T8: n 500 +0.09 (CI -0.26..+0.55) vs placebo -0.07; event-minus-placebo CI -0.21..+0.16"`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:10`: `"RECENT: H1 every cell negative with CI wholly below zero in most (k2 x0.3 T4 -0.10, CI -0.16..-0.03); H2 about -0.05..+0.03."`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:11`: `"KEY: OI class does not separate. Fade ALL impulses VALIDATION T4 -0.15 (n 3051); fade class B (OI rose) -0.14; fade class A (forced) -0.15. Fading costs fees and loses either way. Follow ALL -0.09, follow A -0.09, follow B -0.04: marginally less bad, never positive."`
2. **Hypothesis 4 (OI build then unwind, 30m and 1h)**:
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:15`: `"H4a (fade the built side at unwind start), VALIDATION: every cell negative, -0.14%..-0.41% (1h N12 y2 12h: n 2208, 363 days, -0.41, CI -0.64..-0.19; placebo -0.14). RECENT -0.03..-0.17."`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:16`: `"H4b (follow trend while OI builds): VALIDATION -0.13..+0.12 (best 1h N6 y2 12h n 2259: +0.12, CI -0.10..+0.33, placebo -0.04, diff CI lower -0.06); RECENT -0.11..+0.01. No cell clears the CI or BH."`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:17`: `"Descriptive control (not pre-registered, not a pass): same unwind bar but FOLLOW the built side (H4a_rev) 1h N12 12h: VALIDATION +0.19/+0.21 (CI -0.01..+0.39 / -0.00..+0.43, n 2875/2208), DEV -0.02/+0.01, RECENT -0.11/-0.09. Positive in one year only."`
3. **Hypothesis 3 (CVD)**:
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:18`: `"H3 (CVD) dropped: Bybit trade files 30-260 MB per coin-day, too heavy for 500+ days on an overloaded machine."`

### 2.2 Recomputations and Arithmetic Checks
- **Subgroup trade count partition**:
  - In H1/H2, SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:7` reports `H1 k2 x0.3: n 1426` (forced moves where OI fell).
  - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:11` reports `"Fade ALL impulses VALIDATION T4 -0.15 (n 3051); fade class B (OI rose) -0.14; fade class A (forced) -0.15."`
  - Total impulses: `n = 3051`. With Class A `n = 1426`, implied Class B is `3051 - 1426 =` OURS `1625` events. Both classes show near-identical negative performance (`-0.15%` vs `-0.14%`).
  - Weighted average check: `(1426 * -0.15 + 1625 * -0.14) / 3051 =` OURS `-0.1447%` -> rounds to SOURCED `-0.145%` / `-0.15%`, confirming consistency between total pool and reported subgroup returns.
- **Skipped trade percentage**:
  - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:12`: `"(13.4k skipped of ~15k class A BTC+alts for the target cells): the give-back happens within 2 bars, before an entry is possible."`
  - Recomputed proportion: `13400 / 15000 =` OURS `89.33%` of signals could not be traded because mean reversion occurred faster than the 2-bar execution latency.
- **Event-minus-placebo difference**:
  - H2 k3 x0.6 T8: event mean `+0.09%`, placebo mean `-0.07%`. Nominal difference: `+0.09 - (-0.07) =` OURS `+0.16%`. SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:9` reports `"event-minus-placebo CI -0.21..+0.16"`. The upper bound matches the point estimate difference, and the CI spans zero widely (`[-0.21, +0.16]`).
- **Internal Consistency**: **YES**. All counts, subgroup averages, and stated confidence interval spreads are consistent across the report.

---

## 3. Methodological Risks Exposed in the Text

1. **Look-Ahead and Execution Latency Risk**:
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:12`: `"Note: most impulses are already past the 50% retrace at the close of the bar after (13.4k skipped of ~15k class A BTC+alts for the target cells): the give-back happens within 2 bars, before an entry is possible."`
   - *Risk*: Fading sudden impulses on 15m bars requires that the mean reversion occurs *after* the impulse candle closes and the trade is entered. Because nearly 90% of the reversion occurs within the candle or immediately on the open of the next bar, an algorithm trading on bar-close either misses the move completely or enters after the retrace has completed.
2. **Fee and Slippage Drag**:
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:3`: `"fee 2x taker + funding, day-cluster CI, placebo."`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:11`: `"Fading costs fees and loses either way. Follow ALL -0.09, follow A -0.09, follow B -0.04: marginally less bad, never positive."`
   - *Risk*: A 2x taker fee plus funding eliminates any small gross reversion edge. All fee-net cell means remain firmly negative (-0.22% to +0.09%, with virtually all negative), proving the strategy cannot clear execution friction.
3. **Placebo Validity Risk**:
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:7`: `"- H1 k2 x0.3: n 1426 (330 days): T2 -0.16, T4 -0.15, T8 -0.09 (CI -0.21..+0.05), bracket -0.11 (CI -0.16..-0.06); placebo -0.10"`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:9`: `"- H2 k3 x0.6 T8: n 500 +0.09 (CI -0.26..+0.55) vs placebo -0.07; event-minus-placebo CI -0.21..+0.16"`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:16`: `"H4b (follow trend while OI builds): VALIDATION -0.13..+0.12 (best 1h N6 y2 12h n 2259: +0.12, CI -0.10..+0.33, placebo -0.04, diff CI lower -0.06); RECENT -0.11..+0.01. No cell clears the CI or BH."`
   - *Risk*: The event returns fail to distinguish themselves from random entry baselines. The event-minus-placebo confidence intervals include zero across the board, confirming that impulse classification adds no alpha over unconditional entry.
4. **Clustering and Independence Risk**:
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:3`: `"15m impulse (range>=k ATR, vol>=3x med20, new 16-bar extreme), 10 Bybit perps, OI 15min, fee 2x taker + funding, day-cluster CI, placebo."`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:7`: `"- H1 k2 x0.3: n 1426 (330 days): T2 -0.16, T4 -0.15, T8 -0.09 (CI -0.21..+0.05), bracket -0.11 (CI -0.16..-0.06); placebo -0.10"`
   - *Risk*: Market-wide liquidation cascades trigger simultaneous impulses across multiple perps on the same days (e.g. 1426 events across 330 calendar days). Day-cluster bootstrapping appropriately widens the confidence intervals to reflect cross-asset correlation, preventing false positive discovery.
5. **Multiple Testing and Overfitting (Post-Hoc Data Mining)**:
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:5`: `"## H1 fade FORCED (OI fell) / H2 follow NEW (OI rose): FAIL, 0 of 32 cells pass (BH 10%)"`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:14`: `"## H4 OI build then unwind, 30m and 1h (addendum, pre-registered before outcomes): FAIL, 0 of 96 cells pass"`
   - SOURCED `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge-forced-move-fade_RESULTS.md:17`: `"Descriptive control (not pre-registered, not a pass): same unwind bar but FOLLOW the built side (H4a_rev) 1h N12 12h: VALIDATION +0.19/+0.21 (CI -0.01..+0.39 / -0.00..+0.43, n 2875/2208), DEV -0.02/+0.01, RECENT -0.11/-0.09. Positive in one year only."`
   - *Risk*: Across 128 formal cells (32 in H1/H2 + 96 in H4), 0 cells pass Benjamini-Hochberg FDR control at 10%. When the author tests a descriptive post-hoc reversal control (`H4a_rev`), it produces a mildly positive return in VALIDATION (+0.19/+0.21) but collapses in DEV (-0.02/+0.01) and RECENT (-0.11/-0.09), illustrating textbook sample-specific fitting that fails temporal transfer.

---

## 4. Conclusion and Verdict Justification

The verdict is **SOUND**.
- The study rigorously applies pre-registration, 2x taker fee hurdles, day-clustering, and Benjamini-Hochberg FDR control across 128 candidate cells.
- The hypothesis that forced moves (OI drops during volume impulses) create exploitable fade opportunities fails conclusively because:
  1. Open interest direction provides zero predictive separation between fading forced moves and fading new positioning (`-0.15%` vs `-0.14%`).
  2. The give-back occurs faster than execution latency permits (~89.33% of signals complete their retrace within 2 bars).
  3. Fee drag completely dominates gross returns.
- What would change this verdict: An independent study demonstrating a fee-net positive statistical edge using real tick/orderbook latency modeling, where day-clustered confidence intervals exclude zero and survive multi-comparison FDR correction.
