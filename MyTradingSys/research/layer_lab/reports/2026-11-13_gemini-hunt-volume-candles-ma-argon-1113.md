# Report: Gemini Hunt Volume Candles MA Argon 1113

- **Date:** 2026-11-13 (UTC)
- **Task ID:** `gemini-hunt-volume-candles-ma-argon-1113`
- **Output Artifact:** `MyTradingSys/research/tf_iteration3_1113/hunt_volume_candles_ma/argon.md`
- **Verification Command:** `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tf_iteration3_1113/hunt_volume_candles_ma/argon.md`
- **Verification Result:** PASS (0 problems)

---

## Findings Summary

1. **Layer Under Investigation:**
   - Catalogued in `MyTradingSys/system/LAYERS.md:149-177` as Volume, candle patterns, daily MA setups, bigtrade (volume_candles_ma).
   - Implementations and research modules:
     - Volume: `MyTradingSys/research/volume_2026-10-09` (run_v0.py through run_v4.py, vfeat.py, vstate.py, vstats.py).
     - Candle patterns: `MyTradingSys/research/candle_patterns_2026-10-04` (pilot/run_p1.py, d19_4h_test.py).
     - Daily MA setups: `MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:1-199`.
     - Bigtrade: `MyTradingSys/backtest/bigtrade`, `MyTradingSys/research/bigtrade_2026-10-09`.
     - Krown core TA components: `MyTradingSys/backtest/layers/krown/krown_core.py:1-550`, `MyTradingSys/backtest/layers/krown/params/krown_params.json:1-69`.

2. **Key 5-Pattern Gap Findings:**
   - **Pattern 1 (Our number labelled as his):**
     - In `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:4` and `MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:163-167`, the ma_daily setup parameters (SMA 200, EMA 7, RSI 2, ADX 2, EMA 20, ADX 14) are explicitly documented as NO-SOURCE from a chatbot handoff.
     - In `MyTradingSys/backtest/layers/krown/params/krown_params.json:32`, leash_n is labelled SOURCED with value 3, whereas Krown explicitly states on the tape in -NXzJs5JRks [NO_TS] that across 14+ years and 5,284 daily candles on Bitcoin, the median disconnect lasted only 1 close.
     - In `MyTradingSys/backtest/layers/krown/params/krown_params.json:63-64`, full_body_ratio (0.8) and tiny_range_frac (0.5) are internal parameters (OURS) invented to convert qualitative descriptions in 8MvxK_nxO-0 [NO_TS] and UqAvU1loT_k [NO_TS] into mechanical code.
     - In `MyTradingSys/backtest/layers/krown/params/krown_params.json:55-60`, four arbitrary thresholds (tell_n = 5, tell_flat = 0.005, tell_spread = 0.005, tell_vol = 0.8) are created (OURS) to codify Krown's rule in 6aA-P4Gvhrc [NO_TS].
   - **Pattern 2 (Named often, never coded):**
     - In vjzy_KxJ_y8 [NO_TS], Krown emphasizes the 377 EMA as his primary macro cycle moving average, yet it is completely absent from krown_params.json and krown_core.py.
     - In 8MvxK_nxO-0 [NO_TS], Krown insists that candlestick reversal patterns must never be traded on the pattern candle alone, but require confirmation closes beyond the wick extreme; this confirmation logic was never implemented in `MyTradingSys/research/candle_patterns_2026-10-04/pilot/run_p1.py:88`.
     - In 0jM5Y31YJak [NO_TS] and Is1HvdfQm5c [15:56], Fabio Valentini highlights Volume Spread Analysis (VSA) and buyers punching a passive wall as his core edge; our codebase has zero VSA logic.
   - **Pattern 3 (One word, several claims):**
     - **Volume:** Conflated across three distinct meanings: (a) a participation/agreement filter on breakouts (UqAvU1loT_k [NO_TS]), (b) effort vs result absorption on narrow candles (UqAvU1loT_k [NO_TS]), and (c) a crude statistical volatility filter (`MyTradingSys/research/volume_2026-10-09/vfeat.py:32`).
     - **Engulfing:** Conflated between retail body-to-body enclosure (`MyTradingSys/research/candle_patterns_2026-10-04/pilot/run_p1.py:88`) and Krown's strict liquidity sweep definition requiring trades below the prior low AND closes above the prior high (8MvxK_nxO-0 [NO_TS]).
   - **Pattern 4 (Method lost in translation):**
     - Both Krown (-NXzJs5JRks [NO_TS], vjzy_KxJ_y8 [NO_TS]) and Tom Vorwald (oPyUif2Zrtk [NO_TS]) warn that moving averages and candlestick formations cannot predict price when used in isolation. Krown explicitly states that using moving averages as entry tools is the worst way to use them.
     - Despite this, `MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:163` stripped away all horizontal support/resistance levels and tested standalone MA crossovers as directional entry engines.
     - In 8MvxK_nxO-0 [NO_TS], Krown advises that only 4 major candle patterns matter; the research team tested 18 classical textbook patterns across 108 variants (`MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:7`), discovering 0 of 108 had edge.
   - **Pattern 5 (Transfer assumed):**
     - In -NXzJs5JRks [NO_TS], Krown explains that 21 EMA represents one month (~21 trading days), 55 EMA one quarter, and 200/256 SMA one year of traditional equity market weekdays. Our codebase (`MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:154`, `MyTradingSys/backtest/layers/krown/params/krown_params.json:28-30`) applied these exact numbers to continuous 24/7 BTC perpetual klines without adjusting for crypto calendars.
     - In Is1HvdfQm5c [15:41], Fabio Valentini states that he does not use order flow on Bitcoin and uses on-chain analysis instead. Our system ignored this disclaimer and attempted to apply order flow, big trades, and absorption directly to Binance BTCUSDT (`MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:7`).
     - In DyS79Eb92Ug [05:36], Fabio explains that time-based candles aggregate and obscure order flow during active sessions, mandating range charts (40 range) on index futures. The codebase runs exclusively on time-bucketed klines.

3. **Verifications & Citations:**
   - 28 findings recorded in `MyTradingSys/research/tf_iteration3_1113/hunt_volume_candles_ma/argon.md`.
   - All 27 transcript quotes verified verbatim against canonical text in `raw_transcripts_canonical/` (-NXzJs5JRks, UqAvU1loT_k, 8MvxK_nxO-0, vjzy_KxJ_y8, 6aA-P4Gvhrc, 7IxfsuD2wCM, oPyUif2Zrtk, 0jM5Y31YJak, Is1HvdfQm5c, DyS79Eb92Ug).
   - All file:line citations checked and verified by `python scripts/dev/verify_extract_quotes.py`.
