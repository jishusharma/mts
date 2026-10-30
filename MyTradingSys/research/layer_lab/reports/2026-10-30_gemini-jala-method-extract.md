# Report: Jala Method Extraction (`gemini-jala-method-extract`)
Date: 2026-10-30 (UTC)
Worker: Gemini Flash worker

## Summary & Verification
- Task ID: `gemini-jala-method-extract`
- Analyst: Jala (`@jalacrypto`)
- Captions fetched: 12 of latest 30 channels videos (18 returned HTTP 429 and were marked `UNVERIFIED`). SOURCED: `MyTradingSys/research/jala_layer_2026-10-31/transcripts/`
- Extraction output: `MyTradingSys/research/jala_layer_2026-10-31/method_jala.md`
- Verification command: `python scripts/dev/verify_extract_quotes.py MyTradingSys/research/jala_layer_2026-10-31/method_jala.md`
- Gate result: `PASS: 0 problem(s)` across 22 timed quotes.

## Key Sourced Findings
1. **400-Day Moving Average & Iron Dome**:
   - The 400D SMA marks the top of the "Iron Dome" structure formed with the 200D SMA (SOURCED: `4wlnRxGsSdE`, `4wlnRxGsSdE_raw.txt:43-45`).
   - Sits between 400D daily and 100W weekly ("gateway to upper liquidity voids", SOURCED: `-0UiEM32DX4`, `-0UiEM32DX4_raw.txt:58-60`).
2. **Fractal Cycle Overlay**:
   - Compares cycle patterns (2015, 2019, 2023) to assess potential head and shoulders or failed cup and handle breakdowns under 400D MA (SOURCED: `-0UiEM32DX4`, `xc4TyMS3HKc`, `p9KajODtBsU`).
3. **Alt Rotation & Bitcoin Dominance Rule**:
   - Jala does not chase BTC; when BTC breaks down or enters "latency / hibernation mode", Bitcoin dominance drops and altcoin dominance rises like a seesaw (SOURCED: `mZSSzC6C_Qg`, `mZSSzC6C_Qg_raw.txt:470-475`).
   - Buys alts at the floor when BTC completes its drop, anticipating altcoin dominance rotation before alts pop off 18-30% (SOURCED: `mZSSzC6C_Qg`, `lJ8rI4iiXG4`).
4. **Indicators Read**:
   - STH NUPL (Short-Term Holders Net Unrealized Profit/Loss) turning yellow through the zero line as bottom / cycle stage 3 confirmation (SOURCED: `p9KajODtBsU`, `dmC1U_r8PFc`, `xIUHpTirh_g`).
   - Proprietary "Sun and Moon zones" (stochastic trend tracker coded by Jala around anchored VWAP / ice line) (SOURCED: `5x8DhXBwX9c`, `5x8DhXBwX9c_raw.txt:130-140`).
5. **NOT_IN_DATA Items**:
   - Fixed pip or dollar stop-loss levels are `NOT_IN_DATA` (Jala uses macro daily candle closes under 400 SMA as structural invalidation rather than fixed stops).

Noticed: Jala relies primarily on macro cycle moving averages (400D daily SMA, 100W weekly SMA, 50W SMA) coupled with STH NUPL zero-line crossings and anchored VWAP stochastic bands for alt rotation triggers.
