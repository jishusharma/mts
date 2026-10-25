# Layer Fact Sheet: rsi

> **Claude review 2026-10-26** (`MyTradingSys/research/layer_lab/reports/2026-10-26_gemini-facts-review.md`): content errors below are fixed; about 70 line cites drift from trunk (content true, line off) and are listed in that report, not rewritten here. Treat any line number as approximate (+-15).

Facts compiled strictly from repository files per `MyTradingSys/system/ANTIGRAVITY_LAPTOP.md` item C and task `lf-rsi-gemini-facts`.
No verdicts on keeping, dropping, demoting, or parking any layer. Every fact line cites `file:line` or `NOT_IN_DATA`.
Layers covered: `rsi_levels`, `rsi_divergence` (`MyTradingSys/system/LAYERS.md:88-89`; `MyTradingSys/system/layer_index.json:115-116`; `MyTradingSys/system/layer_map.json:448-478`).

---

## 1. rsi_levels

### ORIGIN (Quoted Source)
- **Practitioner Source**: Vishal B Malkan (MalkanView) (`MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:12-16`).
- **Core Concept & 40/60 Range-Shift Quote**: "When the market is bearish, it won't be able to cross 60, and whenever in a bullish trend, it won't be able to cross 40." (`MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:45`; `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:6-7`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:57-58`).
- **Bullish Level Signal Quote**: "Bullish candlestick forms at 40 RSI level on daily chart = buy signal" (`MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:120`; `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:8`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:61,63`).
- **Bearish Level Signal Quote**: "Bearish candlestick forms at 60 RSI level on daily chart = short signal" (`MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:144`; `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:9`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:64`).
- **Indicator Foundation**: J. Welles Wilder Jr. (1978), *New Concepts in Technical Trading Systems* (`MyTradingSys/backtest/layers/FORMULAS.md:27-30`).
- **Trade Ledger / Ground Truth**: NOT_IN_DATA ("There is no dated Malkan trade list. Six videos are extracted (19 setups plus one grade) and every row records "0 trades in a ledger": they are lectures" in `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:19`).

### PARAMETERS (SOURCED or OURS)
- **RSI Calculation Formula**: Wilder recursive smoothing seeded by simple average of first `length` gains/losses (`SOURCED`, quote: "Wilder's own recursive average (equivalent to an EMA with alpha = 1/period... TradingView Pine Script Reference Manual, ta.rsi/ta.rma" in `MyTradingSys/backtest/layers/FORMULAS.md:28-33`).
- **RSI Period**: 14 (`CONCEPT-ONLY` per provenance audit R01: researcher bullet, no Malkan quote, not SOURCED; quote: "Period: 14 (RSI 14)" in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:35`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:50`).
- **Bull Support Level**: 40 (`SOURCED`, quote: "whenever in a bullish trend, it won't be able to cross 40" in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:45`; `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:10`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:57`).
- **Bear Rejection Level**: 60 (`SOURCED`, quote: "Whenever the market is bearish, it won't be able to cross 60" in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:45`; `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:11`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:58`).
- **Regime Lookback Window**: 20 bars (`OURS` / `CONCEPT-ONLY`, quote: "Regime lookback 20 bars - (no window in WR)" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:60`; `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:12`).
- **Event Tolerance Band**: 2.0 RSI points default (`OURS` / `CONCEPT-ONLY`, quote: "Band tolerance around 40/60 2.0 RSI pts WR:116 'at or near Daily RSI 40' (bullet); quote WR:120 'Bullish candlestick forms at 40 RSI level'" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:61`; `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:13`); swept 0.5 to 5.0 step 0.5 in D3 study (`OURS`, `MyTradingSys/system/layer_map.json:456-459`; `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:8-10`).
- **Candle Color Confirmation Requirement**: true (green candle for bull setup, red candle for bear setup) (`SOURCED`, quotes: "Daily RSI supporting near 40 with entry on Green Candle" and "Bearish candlestick forms at 60 RSI level on daily chart = short signal" in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:77,144`; `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:14-15`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:63-64`).
- **Generic Levels (70/50/30)**: [70, 50, 30] in `default.json` (`OURS` / `NO-SOURCE`, quote: "source: operator... Standard RSI reading levels only (70/50/30)" in `MyTradingSys/backtest/layers/rsi/params/default.json:3-15`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:52`).
- **Generic RSI Smoothing Line**: SMA 14 (`OURS` / `NO-SOURCE`, quote: "no Malkan text mentions an RSI MA... default.json:3 'source': 'operator'" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:51`; `MyTradingSys/backtest/layers/rsi/params/default.json:9-12`).
- **Backtest Exit Stop**: 1% from entry (`OURS` / `NO-SOURCE`, quote: "run_rsi_backtest.py:56,109 Stop 1% from entry - WR:123 'Place below the low of the bullish entry candle' (bullet) NO-SOURCE" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:70`).
- **Backtest Exit Target**: 2% from entry (`OURS` / `NO-SOURCE`, quote: "Target 2% from entry - WR:128 'Target is 60 RSI level on daily chart' NO-SOURCE. Malkan's target is an RSI level, not a price %." in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:71`).
- **Backtest Time Exit**: 100 bars (`OURS` / `NO-SOURCE`, quote: "Time exit 100 bars - WR:132-133: hold while Monthly and Weekly RSI stay > 60 NO-SOURCE" in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:72`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **D3 RSI Tolerance Study (L1-D3, 2026-09-27)**:
   - **Path**: `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:1-36` (summary in `MyTradingSys/system/layer_map.json:626-641`).
   - **Fee-Net**: Not fee-net; gross forward return % at horizon h=5 bars (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:27; system/layer_map.json:633`).
   - **IS / OOS Partition**: Chronological 70% in-sample (IS) / 30% out-of-sample (OOS) over BTCUSDT 1m (2022-01-01..2026-09-26, 2,491,200 bars) resampled to 15m, 1h, 4h, 1d (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:5-7`).
   - **Sample Size (n)**:
     - 15m 40 support: IS n = 1,552, OOS n = 698 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:18`).
     - 15m 60 rejection: IS n = 1,617, OOS n = 767 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:19`).
     - 1h 40 support: IS n = 193, OOS n = 89 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:20`).
     - 1h 60 rejection: IS n = 564, OOS n = 219 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:21`).
     - 4h 40 support: IS n = 93, OOS n = 32 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:22`).
     - 4h 60 rejection: IS n = 39, OOS n = 19 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:23`).
     - 1d 40 support: IS n = 55, OOS n = 23 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:24`).
     - 1d 60 rejection: IS n = 23, OOS n = 8 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:25`).
2. **Market Guide Digest Study (MARKET-GUIDE, 2026-10-07)**:
   - **Path**: `MyTradingSys/research/MARKET_GUIDE_RESULTS_2026-10-07.md:20-22` (summary in `MyTradingSys/system/layer_map.json:710-724`).
   - **Fee-Net**: Fee-net evaluated in sub-reports (`Dumps/backtest/runs/rsi_malkan_40_60/REPORT.md: 1h OOS n 43, -0.092% net, PBO 0.760; 4h n 17, 1d n 5` cited in `MyTradingSys/research/MARKET_GUIDE_RESULTS_2026-10-07.md:21`; `rsi_ma_events: 1h OOS n 357, -0.199% net, PBO 0.352; 4h n 69, -0.216%, PBO 0.455` in `MyTradingSys/research/MARKET_GUIDE_RESULTS_2026-10-07.md:22`).
   - **IS / OOS Partition**: Layer drivers' own splits (`MyTradingSys/system/layer_map.json:1023`); 70/30 not stated here.
   - **Sample Size (n)**: OOS n = 43 (1h), n = 17 (4h), n = 5 (1d) for malkan_40_60 (`MyTradingSys/research/MARKET_GUIDE_RESULTS_2026-10-07.md:21`); OOS n = 357 (1h), n = 69 (4h) for rsi_ma_events (`MyTradingSys/research/MARKET_GUIDE_RESULTS_2026-10-07.md:22`).
3. **Kline Replay Fire History (FIRES-B1, 2026-10-09)** [SUPERSEDED: counts below are the perp run; the spot rerun passes parity 92-100% (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:11`)]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-50` (summary in `MyTradingSys/system/layer_map.json:738-755`).
   - **Fee-Net**: None (fire counts and parity verification; `MyTradingSys/system/layer_map.json:748`).
   - **IS / OOS Partition**: None (full history 2022-01-01..2026-10-07, 2,507,040 1m bars; `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:15`).
   - **Sample Size (n)**:
     - `rsi_events 5m`: 41,538 fires (5,241 tradable) (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:32`).
     - `rsi_events 15m`: 13,411 fires (1,566 tradable) (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:33`).
     - `rsi_events 1h`: 3,136 fires (380 tradable) (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:34`).
     - `malkan_bull 1h`: 116 fires (116 tradable) (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:35`).
     - `malkan_bear 1h`: 143 fires (143 tradable) (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:36`).
4. **Malkan RSI Event Table (2026-10-17)**:
   - **Path**: `MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-malkan-rsi-event-table.md:1-25`.
   - **Fee-Net**: Gross excursion R, no fees (`MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-malkan-rsi-event-table.md:4`).
   - **IS / OOS Partition**: DEV only (bar open 2022-01-01 .. 2024-06-30); VALIDATION/HOLDOUT never loaded (`MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-malkan-rsi-event-table.md:3`).
   - **Sample Size (n)**: 132 event rows total (long bull bounce at 40: n = 59; short bear reject at 60: n = 73) on 21,888 DEV 1h bars (`MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-malkan-rsi-event-table.md:9-14`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Ruling B161**: "screenshot indicator header values (BB, RSI, VWAP) are hand-typed and recomputed ad hoc per read; no check tool" (`MyTradingSys/research/BUGS.md:274`).
- **Ruling B163** (OPEN, MED): operator pasted a 'Setup Alpha / Setup Beta' BTC perp handoff and asks for it to be implemented and backtested (`MyTradingSys/research/BUGS.md:276`).
- **Ruling B125**: "Consensus writer exists only as staged writer.py.new and test_writer.py.new; not promoted, so not live" (`MyTradingSys/research/BUGS.md:236`).
- **Absence of MTF Gate in Backtests (MLK-GAP1)**: "this D3 study runs rsi_events directly (generic level support/rejection), not malkan_setup_bull/bear (which additionally gate on malkan_regime and candle color, per 073). The design's own MLK-GAP1 note says the full 5-star setup also needs Monthly+Weekly regime, which is out of scope here." (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:76-79`).
- **Single-Timeframe Substitution Assumption**: "Bottom line: 2 FAIR (items 4, 6), 10 UNFAIR. The Malkan 'no edge' is a statement about the encoding: single-timeframe RSI 40/60 bounces on BTC 1h/4h/1d (the weekly and monthly gate that defines his 5-star is not applied in the run on record)... His home is Indian equities on daily, weekly and monthly charts" (`MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:9-13`).
- **Live Event Set Divergence (T09 F3)**: Live runner polls spot klines while historical backtest archive was USD-M perp, parity drift on the perp run (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:15`); resolved by the spot rerun, parity 92-100% (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:11`); LAYER_SHEETS still lists it ( `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:11`).

### CONFLUENCE
- **Higher Timeframe Regime Composition**: Malkan 5-star setup requires Monthly RSI >= 60 AND Weekly RSI >= 60 for Daily bullish bounce; Monthly RSI <= 40 AND Weekly RSI <= 40 for Daily bearish rejection (`MyTradingSys/backtest/layers/rsi/malkan_40_60.py:13-16`; `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:69,95`; `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:77-81`).
- **Regime Context Pairing**: Identified in layer review as candidate for REGIME slot combining with Krown regime (same-object pair) (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:11,31`).
- **Live Auto-Trader Gap**: "RSI cross events are rejected as unmapped in the auto-trader (no layer_rules entry); and no layer stacks level" (`MyTradingSys/system/LAYERS.md:103`).

---

## 2. rsi_divergence

### ORIGIN (Quoted Source)
- **Practitioner Source**: Vishal B Malkan (MalkanView), video extracts `extract_Wvq1TZh8aF0.md` ("RSI Divergence Explained Simply", 2026-04-15) and `extract_cQ-y1oULkBw.md` (`MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:3`; `extracts/processed/malkan/extract_Wvq1TZh8aF0.md:1`).
- **Comparison Basis Quote**: "What do we have to compare? Close to close. Because RSI is based on closing price." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:6; MyTradingSys/backtest/layers/rsi/rsi_divergence.py:3`).
- **Minimum Bars Quote**: "How many candles are needed? Three." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:10; MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:6`).
- **Maximum Bars Quote**: "I will say that less than 10 bars is the most powerful divergence. It should be between three and 10." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:16; MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:7`).
- **Dilution of Long-Range Divergence Quote**: "at the most 10 times divergence. If you have 30 times divergence, 50 times divergence, that is diluted." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:13; MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:13-14`).
- **Decimal Differences Acceptable Quote**: "Sometimes there is divergence in decimals and that will also be acceptable." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:27; MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:9`).
- **Optimal Level Location Quote**: "the most powerful divergence come near 60 bearish divergence and the most powerful bullish divergence comes near 40." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:20`).
- **Trade Ledger / Ground Truth**: NOT_IN_DATA (no dated trade ledger in repo; `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:33-35`).

### PARAMETERS (SOURCED or OURS)
- **Minimum Lookback Bars**: 3 bars (`SOURCED`, quote: "How many candles are needed? Three." in `extracts/processed/malkan/extract_Wvq1TZh8aF0.md:10`; `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:4,6`).
- **Maximum Lookback Bars**: 10 bars (`SOURCED`, quote: "It should be between three and 10." in `extracts/processed/malkan/extract_Wvq1TZh8aF0.md:16`; `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:5,7`).
- **Price and RSI Comparison Basis**: close_to_close (`SOURCED`, quote: "What do we have to compare? Close to close. Because RSI is based on closing price." in `extracts/processed/malkan/extract_Wvq1TZh8aF0.md:6`; `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:10`).
- **Minimum RSI Difference (min_rsi_diff)**: 0.0 (`SOURCED`, quote: "Sometimes there is divergence in decimals and that will also be acceptable." in `extracts/processed/malkan/extract_Wvq1TZh8aF0.md:27`; `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:8-9`).
- **Operator Long-Range Window Variant**: 11-60 bars (`OURS` / `NO-SOURCE`, quote: "operator T091, operator idea, NO-SOURCE: long-range divergence 11-60 bars between a swing point A and a later same-kind swing point B, NON-adjacent... Malkan rejects this range in his own words" in `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:10-14`; `MyTradingSys/system/layer_map.json:468-472`).
- **Timeframes Evaluated**: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 1d, 2d (`OURS` grid, `MyTradingSys/system/layer_map.json:473-477`; `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:4`).
- **Evaluation Horizons**: 1, 5, 10, 20 bars (`OURS` / `NO-SOURCE`, quote: "10 bars, t 2 and the 00/12 UTC halves are engineering choices fixed before the run (NO-SOURCE)" in `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:15-16`).
- **Causal Event Timestamp**: Bar after swing point B closes (`ts[i+1]`) (`OURS`, quote: "Swing point = strict local extreme of the CLOSE... It is only known one bar later, so the event time is ts[i+1] (causal)" in `MyTradingSys/backtest/layers/rsi/rsi_divergence.py:10-12`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **Multi-Timeframe RSI Divergence Backtest (RSI-DIV-MTF / T089 + T091, 2026-10-09)**:
   - **Path**: `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:1-24` and `REPORT.md` (summary in `MyTradingSys/system/layer_map.json:643-659`).
   - **Fee-Net**: Fee-net evaluated (one taker round trip 0.10% = 0.0010; `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:6,14; system/layer_map.json:651`).
   - **IS / OOS Partition**: Per-year evaluation 2022-2026 across 2,507,040 1m bars (1,741 full days) of BTCUSDT (`MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:6,17-18; system/layer_map.json:650`).
   - **Sample Size (n)**:
     - 32 cells reached n >= 300 events across 1m to 1h timeframes plus 2h Malkan bearish (n = 301) (`MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:5-7`).
     - 1h operator bullish: n = 277 (`MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:5`).
     - 1h operator bearish: n = 332 (`MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:8`).
     - 6h operator bullish: n = 54 (`MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:9`).
     - 6h operator bullish n=54; 2d operator cells and 6h together n 6-54 (`MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:12-13`).
2. **Anchor Shift Probe (T090 Addendum, 2026-10-09)**:
   - **Path**: `MyTradingSys/research/t090_7h_2026-10-09/RESULT.md:12-36`.
   - **Fee-Net**: net of taker x2, horizon 10 bars, BTCUSDT 2022-01..2026-10 (`MyTradingSys/research/t090_7h_2026-10-09/RESULT.md:12`).
   - **IS / OOS Partition**: Full period with 00:00 UTC vs 18:00 NY (22:00 / 23:00 UTC) session shift on 7h timeframe (`MyTradingSys/system/layer_map.json:475-477`).
   - **Sample Size (n)**: 7h@00 n=46 (+1.09%, t 2.11); 7h@18 n=47 (+0.15%, t 0.25); 7h@22 n=45 (+0.65%, t 1.18); 7h@23 n=43 (+0.46%, t 1.23); only the 18:00 NY (22/23 UTC) anchor is sourced (`MyTradingSys/research/t090_7h_2026-10-09/RESULT.md:9,17-20`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Ruling B154**: "No regime-stratified and no session-stratified backtest verdict exists; every reported edge is one aggregate number... B154 regime split not available in code yet" (`MyTradingSys/research/BUGS.md:266`; `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:16`).
- **Consecutive Swings Constraint in v1**: "A and B are CONSECUTIVE swing points of the same kind (v1 limit: a divergence against an older, non-adjacent swing is not detected)." (`MyTradingSys/backtest/layers/rsi/rsi_divergence.py:12-14`).
- **Absence of Sourced Exits**: No stop/target bracket or candle confirmation was tested in the raw signal backtest (`MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:16`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:40-42`).
- **Unverified Operator Arm Provenance**: Operator 11-60 bar range was explicitly flagged as NO-SOURCE and contrary to Malkan's stated warning on dilution (`MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:10-14`).

### CONFLUENCE
- **40/60 Zone Anchoring**: Malkan specifies that regular divergence is strongest when occurring near the 40 level (bullish) or 60 level (bearish) (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:20`).
- **Candlestick Confirmation Confluence**: Malkan requires candle color confirmation (e.g. red candle to confirm bearish divergence) before entry (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:31-35`).
- **Role in Combined System**: Classified in Layer Review as candidate for TRIGGER slot (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:33`).
- **Interaction with Quad Rotation (Kurisko Super Signal)**: Kurisko's "Super Signal" = quad rotation + a (price vs stochastic) divergence (`MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:10,42`).

---

## 3. Related Family Candidate: Kurisko Quad Rotation (Stochastic / RSI Arm)

*Note: Documented here because `MyTradingSys/system/layer_index.json:104` and `MyTradingSys/system/LAYERS.md:85,95` group Kurisko within the `rsi` family spec files, but repo provenance establishes Kurisko as a Stochastic system with an unsourced operator RSI hypothesis.*

### ORIGIN (Quoted Source)
- **Practitioner Source**: John Kurisko (DayTradingRadio) (`MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:7-9`).
- **Discrepancy Between Memory and Source**: "John Kurisko (DayTradingRadio) has exactly one multi-indicator scalp that fits your memory: the Quad Rotation... It is four STOCHASTIC oscillators, not four RSIs. No source I opened ties Kurisko to RSI." (`MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:7-8`).
- **Transcript Verification**: "'RSI' occurs 0 times in S8 (KURISKO_SPEC s4)... If you want the RSI version tested anyway, it has to be labelled 'operator hypothesis', not Kurisko." (`MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:11`; `MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:12`).

### PARAMETERS (SOURCED or OURS)
- **Stochastic Lookback Bands (k, d)**: (9, 3), (14, 3), (40, 4), (60, 10) (`SOURCED`, quote: "(9,3), (14,3) SOURCED KURISKO_SPEC s3 rows Stochastic 1-2 (S4); 60 SOURCED R1 ('These are 40 candles and these are 60 candles', char 21291) with d=10 (S4 (60,10,10))" in `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:5`). Caveat at the same line: (40,4) is "SOURCED but contested: S3 says 44; the smoothing d=4 is on slide S4 only".
- **Signal Line**: D line, SMA_d(raw %K) (`SOURCED`, quote: "R8 'here I'm using the D line. And the D line is the signal line'; D = SMA_d(raw %K) per spec_review_kurisko_2026-10-18.md FIX" in `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:6`).
- **Oversold Threshold (level_lo)**: 20 (`SOURCED`, quote: "R2 'all of these bands get oversold below 20' (char 20846)" in `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:7`).
- **Overbought Threshold (level_hi)**: 80 (`SOURCED` from Kurisko slide S4/S2; `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:8`).
- **Turn Trigger Rule**: fast[t] > fast[t-1] with all four < 20 on s..t-1 (`OURS`, quote: "no source defines the number for 'turn back up' (R3 'visual confirmation', KURISKO_SPEC s5 gap 3)" in `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:9`).
- **RSI Arm Parameters**: Lookbacks (9, 14, 40, 60), levels 20/80 (`OURS` / `OPERATOR-HYPOTHESIS`, quote: "operator memory '4 RSI with params'; 'RSI' occurs 0 times in S8... Wilder RSI via rsi_core on the same four lookbacks, levels 20/80 reused, NOT Kurisko" in `MyTradingSys/backtest/layers/kurisko/params/kurisko_default.json:11; backtest/layers/FORMULAS.md:567`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
- **Status in Repo**: NOT_IN_DATA (DEV event study open on card `kurisko-dev-event-study`; no completed backtest on record in `layer_map.json` or `MyTradingSys/system/LAYERS.md:98-99`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Indicator Substitution Assumption**: Kurisko uses Stochastics; the "4 RSI" variant is an unsourced operator hypothesis (`MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:7-12`).
- **Plotted Line Fix**: Plotted line was corrected from raw %K to smoothed %D following cross-vendor spec review (`MyTradingSys/research/lab_guy/spec_review_kurisko_2026-10-18.md`; `MyTradingSys/backtest/layers/FORMULAS.md:561`).

### CONFLUENCE
- **Super Signal**: Quad rotation + (price vs stochastic) divergence (`MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:10,42`).
