# Report: lf-krown-gemini-facts

- **Card ID**: `lf-krown-gemini-facts`
- **Date (UTC)**: 2026-10-25
- **Task**: [GEMINI] Layer fact sheet: krown (file:line facts only, no verdict)
- **Output Artifact**: `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/krown.md`

## Findings and Evidence Summary

1. **Origin**:
   - Source analyst: Eric Krown (@ECKrown / "Crown", Krown Trading) (`MyTradingSys/options/research/KROWN_FREE_VS_PAID.md:1`).
   - Core methodology: Swing and context method for daily/weekly BTC/crypto (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:8-12`).
   - Corpus status: Spec v0.2 + 120-rule ledger from 15 of 19 reachable TA 101 videos (`MyTradingSys/system/LAYERS.md:222`, `MyTradingSys/system/layer_index.json:426`).

2. **Parameters**:
   - Module parameters extracted and labelled across 11 modules (`tf`, `swings`, `zones`, `volume`, `vol_regime`, `candles`, `mas`, `rsi`, `range`, `topdown`, `tops`) per `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:39-52`.
   - Setup parameters and stop/exit classes mapped per `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:54-68` and `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:36-53`.
   - Structural stop identified only for setup S8 (vol-compression breakout, far side of compression zone, KR-Q05, SOURCED); general stop distance or risk per trade is NOT_IN_DATA (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:16,69-70`).

3. **Backtests**:
   - Strategy backtests on Krown layer: 0 runs (`MyTradingSys/system/LAYERS.md:222`: "Detectors not built, not backtested"; `MyTradingSys/system/layer_index.json:426`).
   - Related exploratory study: `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:3,8,13`: 105,541 correlated event rows across 126 pooled arms, fee-net (14 bp round trip), DEV sample only (Jan 2022 - Jun 2024), 0 pass screen. Validation and holdout were not opened (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:8`).

4. **Rulings / Bugs / Assumptions**:
   - `python scripts/dev/lab_query.py rulings krown` returns 0 rulings (`{"family": "krown", "rulings": []}`).
   - Documented assumptions and gaps: no resting stop (`SNR-21`, `MyTradingSys/research/krown_ta101_2026-10-13/reflexivity_log.md:12`), no numerical stop distance (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:69-70`), unverified statistical claims (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:72-74`), volume baseline conflict (`MyTradingSys/research/krown_ta101_2026-10-13/PROTOCOL.md:28`), Coinbase/index volume NOT_IN_DATA (`MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:32-34`), and ground truth trade ledger NOT_ANSWERED (`MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:14-19`).

5. **Confluence**:
   - Cross-trader overlaps identified and catalogued with Tom (10 setups), Fabio (4 setups), Malkan/RSI (4 setups/regimes), CryptoCred, Moving Averages, Candle Patterns, and Liquidation Cascades (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:978-999`; `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:82-96`).
   - Six setups have no overlap in existing repo layers (`KR-S6`, `KR-S7`, `KR-S10`, `KR-S11`, `KR-S12`, `KR-S15`; `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:998-1000`).

6. **Verdict**:
   - None given, per specification.
