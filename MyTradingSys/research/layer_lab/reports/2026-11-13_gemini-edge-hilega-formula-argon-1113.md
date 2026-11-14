# Report: Hilega Milega Public Formula Definition & Parameter Extraction (Argon Twin)

Date: 2026-11-13 (UTC)
Task: `gemini-edge-hilega-formula-argon-1113`
Worker: `gemini-3.8-flash-low`
Role: Argon Twin (independent second-model execution)

## Objective & Scope

Pursuant to task instructions for `gemini-edge-hilega-formula-argon-1113`:
1. Conduct web search only (no YouTube caption fetch) to collect at least 3 independent public sources (TradingView / Pine Script communities, Indian broker forums, and technical scanner platforms).
2. Write `MyTradingSys/research/layer_lab/gemini_edge_1113/hilega-formula-argon/FORMULA.md` containing:
   - A core table of lines, formulas, lengths, source URLs, exact quoted sentences, and SOURCED / UNKNOWN status.
   - Cross-source comparison per parameter (AGREED / SINGLE / CONFLICT).
   - Primary video transcript extraction comparison against Nitish Kumar's (NK Sir's) own statements in `MyTradingSys/research/nk_stocktalk_1113/flash_deep/*/EXTRACT.md`.

## Deliverables & File Links

- **Formula Document:** [FORMULA.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-hilega-formula-argon-1113/MyTradingSys/research/layer_lab/gemini_edge_1113/hilega-formula-argon/FORMULA.md)
- **Report Document:** [2026-11-13_gemini-edge-hilega-formula-argon-1113.md](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-hilega-formula-argon-1113/MyTradingSys/research/layer_lab/reports/2026-11-13_gemini-edge-hilega-formula-argon-1113.md)

## Summary of Findings & Source Verification

### 1. Parameter Consensus Across Independent Sources

1. **RSI Length:** 9 (AGREED across FYERS community forum `community.fyers.in/post/hilega-milega-indicator-665d9ee7cdb14441cf2262d4`, Dhan MadeForTrade `madefortrade.in/t/hilega-milega-indicator/38890`, Nifty20 `nifty20.com/hilega-milega-scanner/`, and Chartink `chartink.com/screener/hilega-milega`).
2. **Red Line (WMA):** 21-period Weighted Moving Average applied on the 9-period RSI (`ta.wma(rsi, 21)`). Represents the slow baseline and volume-weighted proxy. AGREED.
3. **Green Line (EMA):** 3-period Exponential Moving Average applied on the 9-period RSI (`ta.ema(rsi, 3)`). Represents fast price sentiment/momentum. AGREED.
4. **Blue Line / Fill Role:** CONFLICT. In Fyers/TradingView implementations, Blue is the dynamic sub-50 background cloud fill (`color.new(color.blue, 85)`). In certain alternate Chartink/Pine scripts, the fast 3 EMA line is colored Blue instead of Green.
5. **Centerline / Boundary Levels:** 50 (midline), 80 (upper band), 20 (lower band). AGREED.

### 2. NK Sir Primary Video Extract Check

Across canonical transcripts in `MyTradingSys/research/nk_stocktalk_1113/flash_deep/`:
- **Stated by NK:**
  - Setup Name & W-Pattern: `"एक डब्ल्यू का निर्माण कर देगा हिलेगा मिलेगा ऐसे ऐसे और एक ऐसे ऊपर की तरफ डब्लू बन जाएगा"` ([JLcDdrHkB5M:EXTRACT.md:57](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-hilega-formula-argon-1113/MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md#L57)).
  - Target Zone 82: `"और जब डब्लू बन जाएगा तो ये वाले आरएसआई के पास भी जाने की फिर से कोशिश करेंगे 82 के ज़ोन में"` ([JLcDdrHkB5M:EXTRACT.md:63](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-hilega-formula-argon-1113/MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md#L63)).
  - Timeframe: 1-hour for SL hunting reduction ([JLcDdrHkB5M:EXTRACT.md:33](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-hilega-formula-argon-1113/MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md#L33)).
- **Unstated by NK (NOT_STATED in transcript):**
  - RSI length period for Hilega Milega (`NOT_STATED` in [JLcDdrHkB5M:EXTRACT.md:74](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-hilega-formula-argon-1113/MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md#L74)).
  - Fast average of RSI (`NOT_STATED` in [JLcDdrHkB5M:EXTRACT.md:75](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-hilega-formula-argon-1113/MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md#L75)).
  - Volume-weighted average length (`NOT_STATED` in [JLcDdrHkB5M:EXTRACT.md:76](file:///C:/Users/e-ngineers/.gemini/mts-gq/gemini-edge-hilega-formula-argon-1113/MyTradingSys/research/nk_stocktalk_1113/flash_deep/JLcDdrHkB5M/EXTRACT.md#L76)).

## Test Results

Execution:
`python scripts/dev/verify_extract_quotes.py MyTradingSys/research/layer_lab/gemini_edge_1113/hilega-formula-argon/FORMULA.md`
Result: PASS (0 problem(s), 5 cites verified).
