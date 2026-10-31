# Report: Jala Fractal Method Extraction (`gemini-jala-fractal-method`)
Date: 2026-10-31 (UTC)
Worker: Gemini Flash worker
Lane: CODEX | Task: `gemini-jala-fractal-method`

## 1. Summary & Verification Metrics
- Videos read: 50 [SOURCED `MyTradingSys/research/jala_layer_2026-10-31/FRACTAL_METHOD_JALA.md:1`]
- Captioned: 12 [SOURCED `MyTradingSys/research/jala_layer_2026-10-31/FRACTAL_METHOD_JALA.md:1`]
- UNVERIFIED (HTTP 429 / IpBlocked): 38 [SOURCED `MyTradingSys/research/jala_layer_2026-10-31/FRACTAL_METHOD_JALA.md:1`]
- Videos with 'fractal': 11 (9 in captions, 2 in unverified titles) [SOURCED `MyTradingSys/research/jala_layer_2026-10-31/FRACTAL_METHOD_JALA.md:1`]
- Gate verification command: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/jala_layer_2026-10-31/FRACTAL_METHOD_JALA.md`
- Verification outcome: `PASS: 0 problem(s)` across 23 GPS-verified quotes (exit code 0).

## 2. Key Sourced Findings on Jala's Fractal Method

1. **Which Past Cycles are Overlaid**:
   - **November 2021 ATH**: Overlaid as the primary 4-year sister fractal reference cycle ($69k ATH aligned with current cycle top, SOURCED: `J2h0pm74iw4`, `J2h0pm74iw4_raw.txt:95-102`).
   - **2018-2019 Cycle**: Overlaid for bottom pocket double test ('one and two') and sunny reaccumulation ('three', SOURCED: `xIUHpTirh_g`, `xIUHpTirh_g_raw.txt:180-186`).
   - **2015 Cycle**: Cited for macro fakeouts killing both longs and shorts before finding 100W support (SOURCED: `p9KajODtBsU`, `p9KajODtBsU_raw.txt:298-305` and `NOtT6auErWQ`, `NOtT6auErWQ_raw.txt:233-238`).
   - **2023 Cycle**: Overlaid using TradingView bar replay to observe consolidation behavior inside the sweet spot pocket between 400D and 100W MAs (SOURCED: `mZSSzC6C_Qg`, `mZSSzC6C_Qg_raw.txt:50-56`).

2. **Alignment Anchor**:
   - **All-Time High Month-to-Month Symmetry**: Anchors current cycle top to November 2021 ATH ("almost four years to the month: October to November", SOURCED: `J2h0pm74iw4`, `J2h0pm74iw4_raw.txt:100-104`).
   - **Cycle Lows in Bottom Pocket**: Anchors bottom recovery phases ('the three') off the lowest low of the bear cycle (SOURCED: `p9KajODtBsU`, `p9KajODtBsU_raw.txt:44-48`).

3. **Timeframe & Moving Average Grid**:
   - Evaluated on **daily** and **3-day** charts (SOURCED: `p9KajODtBsU`, `p9KajODtBsU_raw.txt:36`).
   - Moving average grid: 400D SMA (Iron Dome roof), 200D SMA (Iron Dome base), 100W weekly SMA ("gateway to upper liquidity"), and 50W weekly SMA ("wall of fire" / secondary support).

4. **Confirm and Fail Rules**:
   - **Confirm Rule**: Qualitative structural match; fractal projected a head-and-shoulders breakdown which price confirmed upon losing 100W resistance and retesting 400D SMA (SOURCED: `xc4TyMS3HKc`, `xc4TyMS3HKc_raw.txt:60-65` and `lJ8rI4iiXG4`, `lJ8rI4iiXG4_raw.txt:42-45`).
   - **Fail / Invalidation Rule**: Daily candle close beneath 400D SMA confirms a failed cup-and-handle pattern, triggering the bearish fractal algorithm (SOURCED: `-0UiEM32DX4`, `-0UiEM32DX4_raw.txt:140-148`).

5. **Outcome Called Afterwards**:
   - On 2026-10-08, Jala called for a 20-25% retracement from the 400D MA towards the 50W SMA in the $79k-$80k zone based on past cycle fractal retracements (SOURCED: `lJ8rI4iiXG4`, `lJ8rI4iiXG4_raw.txt:80-92`).
   - On 2026-10-30, Jala verified that BTC fell under $79k and tested the 50W SMA, directly attributing the call to the fractal algorithm (SOURCED: `dmC1U_r8PFc`, `dmC1U_r8PFc_raw.txt:30-38`).

6. **NOT_IN_DATA / Operator Gaps**:
   - Mathematical similarity metric: `NOT_IN_DATA` (Jala uses visual TradingView bar replay, disclaiming tick-by-tick precision: "the length of these waves vary").
   - Fixed dollar or pip stop loss: `NOT_IN_DATA` (risk management is strictly structural candle closes).
   - Numerical order entry type and sizing: `NOT_IN_DATA` (fractal is an orienting context filter, while trades are executed on altcoins using proprietary Sun & Moon indicators).

Noticed: Jala treats fractals not as an automated quantitative signal, but as an orienting macro wave map ("getting from Dallas to Atlanta") aligned around the 4-year cycle ATH and bottom pocket, paired with 400D and 100W moving averages for structural confirmation.
