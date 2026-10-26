> Superseded by MyTradingSys/items/B063_divergence.md (2026-09-22). Retained for history.

# DIVERGENCE_AUDIT_AND_RESEARCH

## A. AUDIT

- tape-watch.ps1 L59-60 defines bearish_div as price up and CVD down, and bullish_div as price down and CVD up; this is a two-term rule with a one-snapshot window. per excerpt 2 / per dispatch facts
- divergence_monitor.py compares consecutive snapshots at least 10 minutes apart and uses PRICE_MIN 30.0 pts, CVD_MIN 200.0, ND_MIN 20.0. per excerpt 3 / per dispatch facts
- SetupScreener.java L54 has a boolean cvdDivergence parameter; L107-109 appends "CVD divergence detected." to a reason string when the boolean is true; the caller is not shown. per excerpt 4 / per dispatch facts
- SetupCandidatesBuilder.java L276 maps cvdSlope == "divergent" to regime "trend_unhealthy"; the producer of cvdSlope is not shown. per dispatch facts
- mtf_flow_alignment_design_2026-09-12.md uses per-TF state vocabulary +A, -A, +D, -D, N and patterns such as all_aligned_long, all_aligned_short, fast_aligned_slow_divergent, slow_aligned_fast_divergent, all_divergent_same, mixed_no_majority, thin_data; the design is approved, inert, and has no consumer. per excerpt 5 / per dispatch facts
- entry_timing_triggers.md uses absorption, finished auction, and delta flip as reaction/trigger language, not divergence as a named term. per excerpt 6

- The live loop emits ALERT lines from start-trading-day.ps1 L582-720; alerts fire on verdict-word change, proof-count crossing 3<->5, zone change, STATE change, ADVERSE, STOP NEAR, TARGET NEAR; alerts do not fire on divergence as such. per dispatch facts
- Excerpt 1 last 30 ALERT lines show verdict, proof, zone, STATE, and price-delta changes; none contain a divergence token. per excerpt 1
- Divergence appears only as a sidecar popup from tape-watch.ps1; L76 writes "DIVERGENCE: $div". per dispatch facts / per excerpt 2
- divergence_monitor.py shows threshold logic, but no link to the alert emitter or sidecar popup is shown. inferred from excerpt 3 and dispatch facts
- SetupScreener.java reason-string append is an annotation when the boolean is true; no alert path is shown. inferred from excerpt 4 and dispatch facts
- SetupCandidatesBuilder.java regime mapping is a classification; no alert path is shown. inferred from dispatch facts

- tape-watch.ps1 header lists ts, price, dPx, dCVD, dND5m, dOI, state, setup nrr, divergence. per excerpt 2
- divergence_monitor.py reads snapshot JSON fields timestamp_utc, current_price, cvd.value, trade_flow.net_delta_1m, open_interest.direction, open_interest.change_1h_pct, cvd.session_start_utc. per excerpt 3
- SetupScreener.java cvdDivergence is an input parameter; its producer is not shown. per excerpt 4 / per dispatch facts
- The MTF design state vocabulary has no shown data producer or consumer. per excerpt 5 / per dispatch facts
- MTS_DICTIONARY.md warns that CVD is flow, positioning is different, anchors differ, and cross-validation by sign should not be done. per dispatch facts

- The ALERT lines in excerpt 1 are backed by the alert categories in dispatch facts; no divergence alert appears. per excerpt 1 / per dispatch facts
- The sidecar DIVERGENCE popup is backed by tape-watch.ps1 L59-60 and L76 for its two-term rule. per excerpt 2
- divergence_monitor.py threshold logic is backed by excerpt 3, but not by any shown alert emission. inferred
- SetupScreener.java reason-string append is backed for the string append when the boolean is true; the boolean origin is not shown. per excerpt 4 / per dispatch facts
- SetupCandidatesBuilder.java mapping is backed only as a line fact; no evidence it reaches alerts. per dispatch facts / inferred
- The MTF design is approved but inert and has no consumer. per dispatch facts / per excerpt 5
- Overall divergence handling is fragmented across a sidecar, a tool, a screener flag, a regime mapping, and an inert MTF design. inferred

## B. GOLAS-A - INDICATOR DEFINITIONS

1. RSI divergence, regular and hidden.
- UNVERIFIED-WEB; coordinator search: "institutional RSI divergence definition regular hidden", "RSI divergence peer-reviewed". Tier target: T1/T2 for textbook or peer-reviewed definitions; T3 for practitioner definitions. Regular bearish divergence compares price higher high with RSI lower high; regular bullish compares price lower low with RSI higher low. Hidden bearish compares price lower high with RSI higher high; hidden bullish compares price higher low with RSI lower low. The comparison is swing-pivot based, commonly two-point and sometimes three-point after pivot validation. Failure modes include lookback sensitivity, repainting, oscillator pinning in strong trends, and multiple-swing ambiguity. It holds in a bounded oscillator context. UNVERIFIED-WEB / inferred

2. MACD divergence, histogram and signal-line.
- UNVERIFIED-WEB; coordinator search: "MACD divergence histogram signal line institutional definition". Tier target: T1/T2 for textbook or peer-reviewed definitions; T3 for practitioner definitions. Regular divergence compares price swings against the MACD line or histogram; histogram divergence is a derivative view of the MACD line, while signal-line divergence is read around crossover context. Hidden divergence follows the RSI hidden pattern structurally. Failure modes include parameter sensitivity around 12/26/9, lag, histogram-versus-line ambiguity, and trending behavior. MACD is bounded-ish but can trend, so divergence is less stationary than RSI. UNVERIFIED-WEB / inferred

3. OBV divergence.
- UNVERIFIED-WEB; coordinator search: "OBV divergence institutional definition cumulative volume". Tier target: T2 for exchange-published or replicated studies; T3 for practitioner definitions. Regular bearish divergence compares price higher high with OBV lower high; regular bullish compares price lower low with OBV higher low. OBV is cumulative flow, so divergence means volume is not validating the price swing. Failure modes include session-start choice, exchange coverage, cumulative offset, and lack of natural reset. Hidden divergence is not standard for OBV. UNVERIFIED-WEB / inferred

4. CVD divergence, cumulative volume delta.
- UNVERIFIED-WEB; coordinator search: "cumulative volume delta divergence institutional crypto". Tier target: T2 for exchange-published analysis; T3 for practitioner order-flow definitions. MTS itself defines bearish_div as price up and CVD down, and bullish_div as price down and CVD up. per excerpt 2 / per dispatch facts Institutional order-flow definitions treat CVD as aggregated aggressive buy/sell delta, so divergence is a price-swing versus CVD-swing disagreement. Failure modes include aggregation window, exchange coverage, session reset, and baseline choice. It is a cumulative-flow context. UNVERIFIED-WEB / per excerpt 2 / inferred

5. Delta divergence, per-bar or short-window.
- UNVERIFIED-WEB; coordinator search: "per-bar delta divergence order flow". Tier target: T2/T3. Bearish delta divergence is price up on a bar or short window while delta is negative or lower; bullish is price down while delta is positive or higher. The comparison is adjacent-bar or short-window, not long cumulative. Failure modes include one-print noise, liquidation prints, spoofing, and window-choice sensitivity. It is not a bounded oscillator context. UNVERIFIED-WEB / inferred

6. OI divergence.
- UNVERIFIED-WEB; coordinator search: "open interest price divergence institutional crypto". Tier target: T1/T2 for exchange data research; T3 for practitioner summaries. Price up with OI up suggests new longs; price up with OI down suggests short covering; price down with OI up suggests new shorts; price down with OI down suggests long liquidation. Divergence is read when price and OI contradict the expected trend-confirmation relationship. Failure modes include contract roll, reporting lag, and leverage effects. It is a positioning context, not a flow context; MTS_DICTIONARY.md warns not to cross-validate flow and positioning by sign. per dispatch facts / UNVERIFIED-WEB

7. Volume divergence.
- UNVERIFIED-WEB; coordinator search: "volume divergence institutional definition". Tier target: T2/T3. Price up with volume down suggests weak participation; price down with volume up suggests strong participation. The comparison can be bar-based or swing-based. Failure modes include time-of-day effects, wash trading, and 24/7 market unevenness. It can be cumulative or per-bar depending on the implementation. UNVERIFIED-WEB / inferred

8. Hidden divergence.
- UNVERIFIED-WEB; coordinator search: "hidden divergence supported indicators RSI MACD stochastic". Tier target: T3 practitioner. Hidden divergence is commonly supported by RSI, MACD, and stochastic-type bounded oscillators; it is not standard for OBV, CVD, OI, or volume because those are cumulative-flow or positioning measures rather than bounded mean-reverting oscillators. UNVERIFIED-WEB / inferred

9. Divergence versus exhaustion versus absorption.
- UNVERIFIED-WEB; coordinator search: "absorption vs exhaustion order flow divergence". Tier target: T1/T2 for microstructure absorption research; T3 for practitioner usage. Divergence is a multi-swing disagreement between price and an indicator. Exhaustion is an end-of-move state and can occur without divergence. Absorption is large limit orders catching market orders, per excerpt 6 L499. The conditions file uses absorption and finished auction for the same reaction event per excerpt 6 L43 and L577. Delta flip at zone is a trigger per excerpt 6 L225, L303, and L502. The boundary is that absorption and delta flip are event triggers, while divergence is context. per excerpt 6 / UNVERIFIED-WEB

## C. GOLAS-B - CRYPTO RELATIONSHIPS

1. Which divergence pairs tend to co-occur.
- Price/CVD and price/OI divergences often co-occur at reversal zones. UNVERIFIED-WEB; coordinator search: "crypto CVD divergence open interest divergence co-occurrence". Tier target: T2/T3.
- CVD is flow; OI is positioning; MTS_DICTIONARY.md warns that anchors differ and cross-validation by sign should not be done. per dispatch facts
- Inferred: co-occurrence can strengthen a reversal hypothesis only when flow and positioning both support the same read. inferred

2. Which pairs tend to disagree, and what disagreement means.
- Price/CVD bullish while OI falls can be short covering rather than new buying. UNVERIFIED-WEB; search: "crypto CVD bullish open interest falling short covering". Tier target: T3.
- Price/OI divergence without CVD support can be positioning unwind rather than aggressive flow. UNVERIFIED-WEB; search: "crypto open interest divergence without CVD". Tier target: T3.
- Inferred: disagreement means flow and positioning conflict; the practical response is lower conviction or waiting for a delta flip or absorption trigger. inferred / per excerpt 6

3. Setup types crypto practitioners associate with each divergence.
- Reversal at zone: regular bearish divergence at resistance, VAH, or VAL; regular bullish divergence at support. UNVERIFIED-WEB; search: "crypto divergence reversal at zone". Tier target: T3.
- Continuation after pullback: hidden divergence or absorption/delta flip at zone. UNVERIFIED-WEB / per excerpt 6. Tier target: T3.
- Exhaustion at extreme: divergence plus OI or funding extreme. UNVERIFIED-WEB; search: "crypto divergence exhaustion funding OI". Tier target: T3.
- Crypto practitioners often wait for delta flip at zone rather than trading divergence alone. UNVERIFIED-WEB / per excerpt 6 L225, L303, L502. Tier target: T3.

4. Mapping to MTS setup_type vocabulary.
- ct_short maps to regular bearish divergence at a zone. inferred
- ct_long maps to regular bullish divergence at a zone. inferred
- tc_long maps to hidden bullish divergence or pullback absorption/delta flip. inferred
- fvg_short maps to bearish divergence plus FVG rejection. inferred
- fvg_long maps to bullish divergence plus FVG hold. inferred
- These mappings are inferred because setup_type definitions are not shown in the excerpts. inferred

5. Where the MTF design vocabulary fits.
- +A, -A, +D, -D, N are per-timeframe states. per excerpt 5
- Patterns include all_aligned_long, all_aligned_short, fast_aligned_slow_divergent, slow_aligned_fast_divergent, all_divergent_same, mixed_no_majority, thin_data. per excerpt 5
- Inferred: divergence families map into fast_aligned_slow_divergent and slow_aligned_fast_divergent patterns. inferred
- The MTF design is approved, inert, and has no consumer. per dispatch facts / per excerpt 5

## D. GOLAS-C - TUNING FOR BTC

- Lookback windows commonly cited for BTC include RSI 14, MACD 12/26/9, divergence swing 5-20 bars, and order-flow windows of 1-10 minutes. UNVERIFIED-WEB; coordinator search: "BTC RSI divergence lookback 14", "BTC MACD 12 26 9", "crypto order flow divergence window". Most such claims are T3 practitioner; exchange-published microstructure work may be T2.
- Practitioner consensus often claims thresholds should scale with volatility, e.g. ATR-normalized or percentage thresholds, rather than absolute points. UNVERIFIED-WEB; search: "BTC ATR normalized divergence threshold". This is mostly T3.
- MTS divergence_monitor.py uses absolute thresholds PRICE_MIN 30.0 pts, CVD_MIN 200.0, ND_MIN 20.0; no ATR scaling is shown. per excerpt 3 / inferred
- Bar-count divergences are commonly preferred by technical-analysis practitioners, while tick or short-window divergences are preferred by order-flow practitioners. UNVERIFIED-WEB; search: "BTC divergence bar count vs tick window". This is mostly T3.
- Filter rules commonly cited include trend filter, higher-timeframe alignment, volume confirmation, waiting for delta flip or absorption, and avoiding low-liquidity sessions. UNVERIFIED-WEB; search: "BTC divergence false positive filter trend filter". This is mostly T3; liquidity parts may be T2 if exchange-published.
- BTC-specific structure includes 24/7 tape, funding windows commonly around 8 hours, thinner weekend liquidity, and CME gap effects. UNVERIFIED-WEB; search: "BTC funding window divergence", "weekend liquidity BTC divergence". Exchange funding and liquidity research can be T2; most trading rules are T3.
- T1/T2 versus T3 flag: specific numeric thresholds and lookbacks are mostly T3 practitioner claims; exchange-published microstructure and funding analyses can be T2; peer-reviewed T1 work may cover general divergence definitions but not BTC-specific tuning. UNVERIFIED-WEB / inferred

## E. GOLAS-D - BACKTEST LINK

- The backtest method reference is MyTradingSys\research\_archive\loose_2026-10\BACKTEST_METHOD_2026-09-21.md; it is not rewritten here. per dispatch facts
- Testable with snapshots: CVD divergence using current_price and cvd.value; delta divergence partially using trade_flow.net_delta_1m; OI divergence partially using open_interest.direction and open_interest.change_1h_pct; session context using cvd.session_start_utc. per excerpt 3 / inferred
- Not testable with shown snapshot fields: RSI divergence, MACD divergence, OBV divergence, volume divergence, hidden divergence, absorption events, finished auction, delta flip as an event, order book, liquidations, and funding. inferred
- Missing fields include RSI, MACD line/signal/histogram, OBV series, per-bar volume, per-bar delta beyond net_delta_1m, full OI history, funding rate, mark price, liquidation data, order book depth, absorption events, setup_type labels, and the outcome_labels.json schema. inferred
- GOLAS-B relationship tests are partially testable if outcome_labels.json contains setup_type and outcome; otherwise they are not testable from the shown inventory. inferred
- GOLAS-C tuning tests require volatility fields, ATR, funding windows, weekend flags, and liquidity metrics; these are not shown. inferred
- Any GOLAS-A/B/C finding used to justify a system rule must pass meta-research, source validation, and execute per playbook gate; otherwise it is an unverified assumption. per excerpt 7

TASK / Produce DIVERGENCE_AUDIT_AND_RESEARCH with sections A-E.
STATUS / Complete as a reasoning surface; no web was run.
SUMMARY / Divergence handling is fragmented; live alerts do not fire on divergence; sidecar and tools define it differently.
FINDINGS / Definitions vary by indicator; crypto relationships require separate flow and positioning anchors; BTC tuning claims are mostly T3.
NEXT / Coordinator should verify UNVERIFIED-WEB claims and map missing data fields to BACKTEST_METHOD_2026-09-21.md.