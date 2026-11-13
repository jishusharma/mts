# Report: Gemini Hunt Positioning Argon 1113

- **Date:** 2026-11-13 (UTC)
- **Task ID:** `gemini-hunt-positioning-argon-1113`
- **Output Artifact:** `MyTradingSys/research/tf_iteration3_1113/hunt_positioning/argon.md`
- **Verification Command:** `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tf_iteration3_1113/hunt_positioning/argon.md`
- **Verification Result:** PASS (0 problems)

---

## Findings Summary

1. **Layer Under Investigation:**
   - Catalogued in `MyTradingSys/system/LAYERS.md:114-126` as `Positioning (funding, OI, whale / FlowHorse) (positioning)`.
   - Implementation: `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:1-130`, `MyTradingSys/backtest/layers/positioning/trade_costs.py:1-68`.
   - Driver and grid: `MyTradingSys/backtest/layers/run_t055.py:65-87` (36 parameter cells x 3 holding horizons = 108 variants).
   - Specifications: `MyTradingSys/backtest/layers/FORMULAS.md:350-377`.

2. **Key 5-Pattern Gap Findings:**
   - **Pattern 1 (Our number labelled as his):** Lookback `90` records, CVD window `20` bars, funding percentiles `hi = 0.95, lo = 0.05` (`MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:70-71`), holding horizons `4, 16, 48` bars (`MyTradingSys/backtest/layers/run_t055.py:87`), fee `0.0010` and slippage `0.0004` (`MyTradingSys/backtest/layers/positioning/trade_costs.py:51`) are all internal grid parameters (`OURS`), with zero numbers sourced from Memon 2026 or any practitioner.
   - **Pattern 2 (Named often, never coded):** Open Interest is in the section title (`MyTradingSys/system/LAYERS.md:114`) and extensively taught by Krown (`P3rDSh187TE [NO_TS]`) and FlowHorse (`extracts/fresh/extract_UrnES-HzQ6w_the_flow_horse.txt:295,318`), but has zero lines of code in `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:1-130` (`MyTradingSys/system/LAYERS.md:115` admits "OI/long-short unused as filters"). 0 of 32 FlowHorse rules coded (`MyTradingSys/research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md:121`).
   - **Pattern 3 (One word, many claims):** "Whale", "Positioning", and "Liquidation" conflate incompatible concepts across academic literature (Memon 2026 funding reversion), on-chain macro valuation (Fabio MVRV `StaphlRH8NQ [15:09]`), practitioner liquidation mechanics (Krown `P3rDSh187TE [NO_TS]`), and aggressive CVD order flow (`MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:48`).
   - **Pattern 4 (Method lost in translation):** Krown explicitly teaches that extreme funding + high OI is a "weather warning" / "fuel gauge" advising traders to pull capital away and enter *after* the cascade exhausts into patient limit bids (`P3rDSh187TE [NO_TS]`). Our code inverted this into an immediate aggressive fade directly into the liquidation knife (`MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:88-91`).
   - **Pattern 5 (Transfer assumed):** Krown highlights that cascades concentrate in "thin sessions" and "weekend books" with shallow liquidity (`P3rDSh187TE [NO_TS]`). Our backtest executed uniformly across continuous 24/7/365 15m bars without liquidity or session conditioning.

3. **Verifications & Citations:**
   - All 26 transcript quotes verified verbatim against canonical text in `raw_transcripts_canonical/` (`P3rDSh187TE`, `8MvxK_nxO-0`, `StaphlRH8NQ`, `6BAzqewtPUk`, `sQ_biBKhPVU`, `DyS79Eb92Ug`, `Khgj5q1-ln8`).
   - All file:line citations validated by `verify_extract_quotes.py`.
