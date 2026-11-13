# Report: gemini-edge-hilega-recheck-1114

**Date (UTC):** 2026-11-13  
**Card:** `gemini-edge-hilega-recheck-1114`  
**Deliverable:** `MyTradingSys/research/layer_lab/gemini_edge_1114/hilega-recheck/RECHECK.md`

## Summary of Findings

1. **Prior Claims from FORMULA.md (`MyTradingSys/research/layer_lab/gemini_edge_1113/hilega-formula/FORMULA.md`):**
   - Base RSI: Length 9
   - Slow baseline: 21-period WMA calculated on the 9-period RSI (Red line)
   - Fast sentiment line: 3-period EMA calculated on the 9-period RSI (Green line)
   - Blue line: Unsettled / conflicting role
   - Midline threshold: 50
   - Signal: Fast EMA crosses above slow WMA with RSI > 50

2. **New Sources Fetched:**
   - **Source 1:** `https://raw.githubusercontent.com/nkr760-ux/SCREENER/main/hilega_milega_scanner.py` (Fetched HTTP 200 OK, 2929 bytes; also verified `app.py`, 3091 bytes).
     - Verbatim quote line 13: `RSI_LEN, EMA_LEN, WMA_LEN = 9, 3, 21`
     - Verbatim quote line 10: `Uptrend  : RSI(9) > WMA21(RSI) and EMA3(RSI) > WMA21(RSI) and RSI(9) > MIN_RSI`
     - Formula implementation line 42: `r = rsi_wilder(close, RSI_LEN)`, `e = r.ewm(span=EMA_LEN, adjust=False).mean()`, `w = wma(r, WMA_LEN)`
   - **Source 2:** `https://chartink.com/screener/copy-hilega-milega-25` (Fetched HTTP 200 OK).
     - Verbatim Atlas query payload: `( {33489} ( [0] 1 hour rsi( 9 ) > 50 and [0] 1 hour wma( [0] 1 hour close , 21 ) < [0] 1 hour ema( [0] 1 hour close , 3 ) ) )`
     - Confirms RSI(9) > 50 and 3 EMA > 21 WMA crossover logic, though on Chartink the moving averages are calculated on close price due to platform UI limitations.
   - **Source 3 (Web search / Pine Script):** TradingView open-source scripts mark blue as the sub-50 background fill (`fill(..., color = ema_val >= 50 ? color.new(color.green, 85) : color.new(color.blue, 85))`) or alternative 3 EMA coloring (marked UNVERIFIED per prompt rules).

3. **Status of the Blue Line:**
   - There is NO separate 4th indicator calculation. The mathematical model only has `RSI(9)`, `EMA(3)`, and `WMA(21)`.
   - "Blue" represents either the sub-50 ribbon fill zone between EMA and WMA, an alternative line color for the 3-period EMA, or the raw RSI(9) line styling.

All results and comparison tables are detailed in `MyTradingSys/research/layer_lab/gemini_edge_1114/hilega-recheck/RECHECK.md`.
