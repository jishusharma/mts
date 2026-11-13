# Report: Gemini Other Layers Gap Hunt Argon 1113

- **Date:** 2026-11-13 (UTC)
- **Task ID:** `gemini-other-layers-gap-hunt-argon-1113`
- **Output Artifact:** `MyTradingSys/research/tf_iteration3_1113/other_layers/argon.md`
- **Verification Command:** `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tf_iteration3_1113/other_layers/argon.md`
- **Verification Result:** PASS (0 problems)

---

## Findings Summary

1. **Layers & Transcripts Under Investigation:**
   - Traders analyzed: Vishal Malkan (RSI, multi-timeframe, divergence, Bollinger Bands Father-Son) and Eric Krown (Krown Trading: BBWP, hidden divergence, multi-timeframe RSI, setups S1-S11, microstructure).
   - Transcripts reviewed from `raw_transcripts_canonical/`:
     - Malkan: `Wvq1TZh8aF0`, `GbXnw_tNMtw`, `-CBvFi40sIQ`, `W1HrDl70Lhk_asr`, `fgN6QBFY3Ss`, `XFO49JlODxI`, `cQ-y1oULkBw`.
     - Krown: `INOCBmqQupc`, `kcMnnQr1VFg`, `_t_XIBrcjRk`, `7IxfsuD2wCM`, `14bxwxC8gBQ`, `P3rDSh187TE`, `UqAvU1loT_k`, `-NXzJs5JRks`.
   - Layer code compared:
     - Malkan: `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:1-120`, `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:1-140`, `MyTradingSys/backtest/layers/rsi/malkan_level_short.py:1-80`, `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:1-30`, `MyTradingSys/backtest/layers/alerts/live_confluence_feed.py:48-49`.
     - Krown: `MyTradingSys/backtest/layers/krown/krown_live.py:1-85`, `MyTradingSys/backtest/layers/krown/krown_events.py:1-100`, `MyTradingSys/backtest/layers/krown/krown_context.py:1-50`, `MyTradingSys/backtest/layers/krown/params/krown_params.json:1-40`, `MyTradingSys/backtest/layers/rsi/krown_hidden_divergence.py:1-60`.

2. **5-Pattern Gap Findings:**
   - **Pattern 1 (Our number labelled as his):**
     - In `MyTradingSys/backtest/layers/alerts/live_confluence_feed.py:48-49`, `WINDOW_STRONG = 12` and `WINDOW_MAX = 18` are both annotated `# SOURCED (operator relay of Malkan)`. However, Malkan explicitly states in `Wvq1TZh8aF0` [NO_TS] that regular divergence is strongest at 3 to 10 bars and gets diluted beyond 10 bars (15, 20, 25, 50). Neither 12 nor 18 is spoken in any transcript.
     - In `MyTradingSys/backtest/layers/krown/krown_live.py:24-25,63-64`, `STOP_BARS = 10` and `FLOOR = 0.0056` are hardcoded internal constants (OURS) used for BBWP S8 stops, whereas Krown explicitly states in `kcMnnQr1VFg` [NO_TS] to place stops on the opposite side of the compression zone.
   - **Pattern 2 (Named often, never coded):**
     - Malkan's Father-Son Bollinger Band dual timeframe system (higher TF supports at middle band, lower TF touches lower band with a 4x-6x timeframe ratio) in `fgN6QBFY3Ss` [NO_TS] has 0 lines of code in the repository.
     - Malkan's Spinning Top 7-Star high-volume reversal setup in `XFO49JlODxI` [NO_TS] has 0 lines of code.
     - Krown's crypto microstructure rules on liquidation cascades (2-3/year, perp funding rates 1h/4h/8h, shallow weekend order-books) in `P3rDSh187TE` [NO_TS] and wash trading / CME Bitcoin futures cross-checking in `UqAvU1loT_k` [NO_TS] are completely absent from `MyTradingSys/backtest/layers/krown/`.
     - Krown's Top-4 sell scaling (20% to 85% scale out across Daily/Weekly/Monthly) in `7IxfsuD2wCM` [NO_TS] is absent.
   - **Pattern 3 (One word, several claims):**
     - Malkan uses "7-Star" to mean two completely different things: (a) Monthly RSI > 60 + Daily divergence in his GFS momentum framework (`-CBvFi40sIQ`), and (b) a single-candle high-exhaustion volume spinning top reversal where RSI and Bollinger Bands are intentionally ignored (`XFO49JlODxI`).
     - Reverse divergence bar counts: in `GbXnw_tNMtw` [21:54], Malkan states 5 to 50 bars, whereas earlier in the same video he claims less than 15 bars.
   - **Pattern 4 (Method lost in translation):**
     - Malkan's 5-Star GFS enters via a buy-stop above the high of the signal candle with a stop below the candle low and 2:1 R:R (`W1HrDl70Lhk_asr` [9:03]). `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:94-103` reduces this to checking close color only (`b["c"] <= b["o"]`), completely omitting the candle-high entry trigger and candle-low stop loss.
     - In `MyTradingSys/backtest/layers/rsi/krown_hidden_divergence.py:11-12,30-45`, Krown's rule that hidden bullish divergence exists strictly within an established uptrend (`INOCBmqQupc` [NO_TS]) is discarded, stripping all trend and level filters to create a generic divergence indicator.
     - In `MyTradingSys/backtest/layers/FORMULAS.md:548`, RSI 40-60 is codified as `range` (`> 60` bull, `< 40` bear), whereas Krown explicitly states in `INOCBmqQupc` [NO_TS] that during uptrends RSI holds 40-80, misclassifying uptrend retracements as ranges.
   - **Pattern 5 (Transfer assumed):**
     - Malkan designed GFS for Nifty 500 equities across Monthly/Weekly/Daily timeframes (`-CBvFi40sIQ`). The repository runs it on 1-hour continuous crypto (`live_runner_cli.py:546-547`) using a 20-bar lookback regime (`malkan_40_60.py:24-59`) and adds WaveTrend indicators on 4h BTCUSDT (`malkan_level_short.py:20-26,53-61`) that Malkan never mentioned.
     - Krown emphasizes that Daily (00:00 UTC) is the gold standard timeframe for crypto (`_t_XIBrcjRk` [NO_TS]), while live runner executes Krown S8 BBWP break on 4-hour candles (`live_runner_cli.py:591-593`).

3. **Verifications & Citations:**
   - 20 distinct gap findings documented in `MyTradingSys/research/tf_iteration3_1113/other_layers/argon.md` across Malkan and Krown.
   - Exact transcript quotes verified against canonical files in `raw_transcripts_canonical/`.
   - `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/tf_iteration3_1113/other_layers/argon.md` executes with returncode 0 (PASS: 0 problems).
