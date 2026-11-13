# Blind Review: edge4-rsi-confirm-layers

**Verdict: SOUND** (The verdict of **FAIL** reported in the study result is internally sound and completely supported by the data and decision rules; what would change it is pre-registered out-of-sample data showing positive fee-and-slippage-net mean R with lower CI > 0 across consistent regimes, which is absent here).

## 1. Table & Arithmetic Verification

- **Claim & Location**:
  - The text reports: "Verdict: FAIL. 0 of 56 pre-registered layer tests PASS on VALIDATION (6 UNDERPOWERED, 50 FAIL); pairs: none passed. No edge claim." (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:3`).
  - Base claim: "The bare rule is negative fee-net on 1h in both periods; 4h VALIDATION is positive but not distinguishable from zero (CI includes 0) and negative in DEV." (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:17`).
- **Internal Consistency**: **YES**.
  - All 56 layer rows in the main table were parsed and counted (OURS). Exactly 50 rows have verdict `FAIL` and 6 rows have verdict `UNDERPOWERED` (OURS).
  - The 6 `UNDERPOWERED` rows are: `Deep, 1h +1R` (n=1 VAL), `Deep, 1h +2R` (n=1 VAL), `BTC/ETH, 4h +1R` (n=15 VAL), `Deep, 4h +1R` (n=0 VAL), `BTC/ETH, 4h +2R` (n=15 VAL), and `Deep, 4h +2R` (n=0 VAL). Each has `n < 30` on VALIDATION, correctly triggering `UNDERPOWERED` under the pre-registered requirement `n >= 30` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:80`).
  - Recomputed `vs base` arithmetic (`mean R VAL - base mean R VAL`):
    - Base VAL means: 1h +1R = `-0.169`, 1h +2R = `-0.095`, 4h +1R = `+0.093`, 4h +2R = `+0.220` (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:12-15`).
    - Across all 56 rows and 3 pair rows, every reported `vs base` delta matches `mean R VAL - base mean R VAL` within rounding precision (+/- 0.001) (OURS).
  - Pass criteria check: "PASS needs all of: n >= 30, mean > 0, CI lower > 0, beats base, placebo p <= 0.05, BH 10 %." (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:80`).
    - Only 2 rows out of 56 have VALIDATION mean > 0 and CI lower > 0: `dADX20-25, 4h +1R` (mean +0.307, CI [+0.01, +0.57], p=0.075) and `dADX20-25, 4h +2R` (mean +0.648, CI [+0.17, +1.10], p=0.012) (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:86-87`).
    - Both fail the required criteria: `dADX20-25, 4h +1R` has placebo `p = 0.075 > 0.05`. `dADX20-25, 4h +2R` with `p = 0.012` is rank 5 across the 56 tests; Benjamini-Hochberg critical threshold at rank 5 under 10% FDR is `(5 / 56) * 0.10 = 0.0089` (OURS); `p = 0.012 > 0.0089`, so it fails the BH 10% correction (OURS). Moreover, both splits had negative DEV means (`-0.085` and `-0.183`), failing stability (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:86-87,89`).
  - Stage 2 pairs: All 3 tested pairs have `mean R VAL < 0` or negative vs base (`-0.083`, `+0.168` [vs base +0.075, CI lower -0.12], `-0.076`) and placebo p > 0.30, failing all criteria (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:97-99`).

## 2. Concrete Risks Exposed Directly by the Text

The study result text explicitly discloses several methodological and market risks:

1. **Look-ahead Risk**:
   - The text asserts: "Layers use only data closed at or before the signal bar's close." (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:6`).
   - However, it also explicitly notes: "the OI/funding timestamp alignment uses the last record at or before signal close." (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:121`).
   - If Bybit's API publishes 1h OI or 8h funding timestamps at bar open or with latency, conditioning on records aligned to the signal bar's exact close exposes mild timestamp alignment / latency risk.

2. **Fee & Slippage Risk**:
   - The text explicitly states: "fees 2 x BINANCE_TAKER (10 bp RT, taker both legs, no slippage, no funding)" (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:5`) and "Limits: no slippage, no funding charge, 10 bp RT fee (taker)" (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:121`).
   - Because entry occurs immediately following an RSI extreme and a confirmation candle across 20 volatile altcoins, zero slippage is unrealistically optimistic. Additionally, omitting 8h funding costs over trade durations capped at 72h ("72 h cap", SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:5`) further underestimates trade friction.

3. **Placebo Validity**:
   - Placebo methodology is specified as: "random-subset placebo 1000" (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:5`) and "placebo p = share of same-size random subsets of the base with mean >= the layer's" (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:19`).
   - The text flags a critical artifact: "The two layers with Deep n = 0..5 ('UNDERPOWERED') carry p ~ 0 by construction and take BH ranks; excluding them does not change any verdict." (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:80`).
   - A random subset of size 1 can have extreme variance, potentially yielding spurious p-values if not carefully bounded; here, classifying `n < 30` as `UNDERPOWERED` appropriately prevents false discoveries.

4. **Clustering & Cross-Asset Independence**:
   - The text explicitly notes: "trades across the 20 coins overlap in time (week blocks cover part)" (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:121`).
   - Market-wide crypto liquidations cause RSI <= 20 to trigger across many of the 20 coins simultaneously. While week-block bootstrap addresses serial dependence across time, simultaneous cross-sectional coin clustering inflates the nominal sample size (`n=515` 1h VAL trades does not represent 515 independent events).

5. **Multiple Testing & Regime Shift**:
   - Multiple testing: 56 layer tests plus interaction pairs were tested across 2 timeframes and 2 exit targets (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:19,91`).
   - Regime shift: The text documents: "DEV 2020-2023 bull 51 % / bear 40 % / range 10 %; VALIDATION 2024-01..2026-11-05 bull 56 % / bear 30 % / range 15 % (to 2025-06 bull 74 % / bear 7 %; from 2025-07 bull 36 % / bear 54 %)." (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:4`).
   - The text notes sign instability across splits: "Layers that look good on VALIDATION (OI-unwind and US session on 1h; daily ADX 20-25 on 4h) all had NEGATIVE DEV means, i.e. the sign flips between periods, which is what chance across 56 looks gives." (SOURCED: `MyTradingSys/research/layer_lab/gemini_edge_1114/inputs/edge4-rsi-confirm-layers_RESULTS.md:116`).

## 3. Conclusion

The conclusion of **FAIL (No edge claim)** is completely sound, conservative, and truthful to the data. No positive edge was discovered, and the negative result is correctly accepted rather than curve-fit.
