# Layer review fact sheet: families rsi, cryptocred, pitchfork, live_engine

Built 2026-11-02 from the repo only. Starting point: `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/rsi.md, cryptocred.md, pitchfork.md, live_engine.md` (Gemini input, reviewed in `MyTradingSys/research/layer_lab/reports/2026-10-26_gemini-facts-review.md`); every file:line below was re-resolved against this tree by searching the cited file for the quoted text or the number on the line (the Gemini line numbers had drifted). No verdict wording on any layer (operator NO 2026-10-25, `MyTradingSys/research/mts_doctor/MAINNET_PATH_2026-10-25.md:34`). Numbers are copied with their file:line, never recomputed. Labels: SOURCED = a trader quote or paper is given; OURS = our choice, no trader quote found; NO-SOURCE = repo says so itself; NOT_IN_DATA = the repo is silent. Status words such as "closed" or "DEAD" appear only inside quotes of repo files.

## rsi_levels

Wired in the simulator: yes. `MyTradingSys/research/sim_desk/studies/rsi.py` wraps `rsi_core` and `malkan_40_60` (`MyTradingSys/research/sim_desk/PLUGIN.md` row "RSI 40/60 (Malkan)", plugged in 2026-10-21).

### Idea and source
- **Practitioner Source**: Vishal B Malkan (MalkanView) (`MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:12-16`).
- **Core Concept & 40/60 Range-Shift Quote**: "When the market is bearish, it won't be able to cross 60, and whenever in a bullish trend, it won't be able to cross 40." (`MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:45`; `MyTradingSys/backtest/layers/rsi/malkan_40_60.py (line not re-verified)`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:57-58`).
- **Bullish Level Signal Quote**: "Bullish candlestick forms at 40 RSI level on daily chart = buy signal" (`MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:120`; `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:8`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md (line not re-verified),63`).
- **Bearish Level Signal Quote**: "Bearish candlestick forms at 60 RSI level on daily chart = short signal" (`MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:144`; `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:9`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:64`).
- **Indicator Foundation**: J. Welles Wilder Jr. (1978), *New Concepts in Technical Trading Systems* (`MyTradingSys/backtest/layers/FORMULAS.md:27-30`).
- **Trade Ledger / Ground Truth**: NOT_IN_DATA ("There is no dated Malkan trade list. Six videos are extracted (19 setups plus one grade) and every row records "0 trades in a ledger": they are lectures" in `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:19`).

### Parameters
- **RSI Calculation Formula**: Wilder recursive smoothing seeded by simple average of first `length` gains/losses (`SOURCED`, quote: "Wilder's own recursive average (equivalent to an EMA with alpha = 1/period... TradingView Pine Script Reference Manual, ta.rsi/ta.rma" in `MyTradingSys/backtest/layers/FORMULAS.md:28-33`).
- **RSI Period**: 14 (`CONCEPT-ONLY` per provenance audit R01: researcher bullet, no Malkan quote, not SOURCED; quote: "Period: 14 (RSI 14)" in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md (line not re-verified)`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:50`).
- **Bull Support Level**: 40 (`SOURCED`, quote: "whenever in a bullish trend, it won't be able to cross 40" in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:45`; `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json (line not re-verified)`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:57`).
- **Bear Rejection Level**: 60 (`SOURCED`, quote: "Whenever the market is bearish, it won't be able to cross 60" in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:85`; `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json (line not re-verified)`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:57`).
- **Regime Lookback Window**: 20 bars (`OURS` / `CONCEPT-ONLY`, quote: Regime lookback 20 bars - (no window in WR) in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:60`; `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Event Tolerance Band**: 2.0 RSI points default (`OURS` / `CONCEPT-ONLY`, quote: Band tolerance around 40/60 2.0 RSI pts WR:116 'at or near Daily RSI 40' (bullet); quote WR:120 'Bullish candlestick forms at 40 RSI level' in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:61`; `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json (line not re-verified)`); swept 0.5 to 5.0 step 0.5 in D3 study (`OURS`, `MyTradingSys/system/layer_map.json:280`; `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:8-10`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Candle Color Confirmation Requirement**: true (green candle for bull setup, red candle for bear setup) (`SOURCED`, quotes: "Daily RSI supporting near 40 with entry on Green Candle" and "Bearish candlestick forms at 60 RSI level on daily chart = short signal" in `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:77,144`; `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json (line not re-verified)`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:63-64`).
- **Generic Levels (70/50/30)**: [70, 50, 30] in `default.json` (`OURS` / `NO-SOURCE`, quote: source: operator... Standard RSI reading levels only (70/50/30) in `MyTradingSys/backtest/layers/rsi/params/default.json (line not re-verified)`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:52`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Generic RSI Smoothing Line**: SMA 14 (`OURS` / `NO-SOURCE`, quote: no Malkan text mentions an RSI MA... default.json:3 'source': 'operator' in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:51`; `MyTradingSys/backtest/layers/rsi/params/default.json (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Backtest Exit Stop**: 1% from entry (`OURS` / `NO-SOURCE`, quote: run_rsi_backtest.py:56,109 Stop 1% from entry - WR:123 'Place below the low of the bullish entry candle' (bullet) NO-SOURCE in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:70`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Backtest Exit Target**: 2% from entry (`OURS` / `NO-SOURCE`, quote: Target 2% from entry - WR:128 'Target is 60 RSI level on daily chart' NO-SOURCE. Malkan's target is an RSI level, not a price %. in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:71`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Backtest Time Exit**: 100 bars (`OURS` / `NO-SOURCE`, quote: Time exit 100 bars - WR:132-133: hold while Monthly and Weekly RSI stay > 60 NO-SOURCE in `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:72`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]

### Backtests
1. **D3 RSI Tolerance Study (L1-D3, 2026-09-27)**:
   - **Path**: `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:1-36` (summary in `MyTradingSys/system/layer_map.json:626-641`).
   - **Fee-Net**: Not fee-net; gross forward return % at horizon h=5 bars (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:27; system/layer_map.json:633`).
   - **IS / OOS Partition**: Chronological 70% in-sample (IS) / 30% out-of-sample (OOS) over BTCUSDT 1m (2022-01-01..2026-09-26, 2,491,200 bars) resampled to 15m, 1h, 4h, 1d (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:5-7`).
   - **Sample Size (n)**:
     - 15m 40 support: IS n = 1,552, OOS n = 698 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md (line not re-verified)`).
     - 15m 60 rejection: IS n = 1,617, OOS n = 767 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md (line not re-verified)`).
     - 1h 40 support: IS n = 193, OOS n = 89 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:20`).
     - 1h 60 rejection: IS n = 564, OOS n = 219 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:21`).
     - 4h 40 support: IS n = 93, OOS n = 32 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:22`).
     - 4h 60 rejection: IS n = 39, OOS n = 19 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:23`).
     - 1d 40 support: IS n = 55, OOS n = 23 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:24`).
     - 1d 60 rejection: IS n = 23, OOS n = 8 (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:25`).
2. **Market Guide Digest Study (MARKET-GUIDE, 2026-10-07)**:
   - **Path**: `MyTradingSys/research/_archive/loose_2026-10/MARKET_GUIDE_RESULTS_2026-10-07.md:20-22` (summary in `MyTradingSys/system/layer_map.json:710-724`).
   - **Fee-Net**: Fee-net evaluated in sub-reports (`Dumps/backtest/runs/rsi_malkan_40_60/REPORT.md: 1h OOS n 43, -0.092% net, PBO 0.760; 4h n 17, 1d n 5` cited in `MyTradingSys/research/_archive/loose_2026-10/MARKET_GUIDE_RESULTS_2026-10-07.md:21`; `rsi_ma_events: 1h OOS n 357, -0.199% net, PBO 0.352; 4h n 69, -0.216%, PBO 0.455` in `MyTradingSys/research/_archive/loose_2026-10/MARKET_GUIDE_RESULTS_2026-10-07.md:22`).
   - **IS / OOS Partition**: Layer drivers' own splits (`MyTradingSys/system/layer_map.json:1023`); 70/30 not stated here.
   - **Sample Size (n)**: OOS n = 43 (1h), n = 17 (4h), n = 5 (1d) for malkan_40_60 (`MyTradingSys/research/_archive/loose_2026-10/MARKET_GUIDE_RESULTS_2026-10-07.md:21`); OOS n = 357 (1h), n = 69 (4h) for rsi_ma_events (`MyTradingSys/research/_archive/loose_2026-10/MARKET_GUIDE_RESULTS_2026-10-07.md:22`).
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

### Bugs and assumptions
- **Ruling B161**: "screenshot indicator header values (BB, RSI, VWAP) are hand-typed and recomputed ad hoc per read; no check tool" (`MyTradingSys/research/BUGS.md:274`).
- **Ruling B163** (OPEN, MED): operator pasted a 'Setup Alpha / Setup Beta' BTC perp handoff and asks for it to be implemented and backtested (`MyTradingSys/research/BUGS.md:276`).
- **Ruling B125**: "Consensus writer exists only as staged writer.py.new and test_writer.py.new; not promoted, so not live" (`MyTradingSys/research/BUGS.md:236`).
- **Absence of MTF Gate in Backtests (MLK-GAP1)**: "this D3 study runs rsi_events directly (generic level support/rejection), not malkan_setup_bull/bear (which additionally gate on malkan_regime and candle color, per 073). The design's own MLK-GAP1 note says the full 5-star setup also needs Monthly+Weekly regime, which is out of scope here." (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md (line not re-verified)`).
- **Single-Timeframe Substitution Assumption**: Bottom line: 2 FAIR (items 4, 6), 10 UNFAIR. The Malkan 'no edge' is a statement about the encoding: single-timeframe RSI 40/60 bounces on BTC 1h/4h/1d (the weekly and monthly gate that defines his 5-star is not applied in the run on record)... His home is Indian equities on daily, weekly and monthly charts (`MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Live Event Set Divergence (T09 F3)**: Live runner polls spot klines while historical backtest archive was USD-M perp, parity drift on the perp run (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:15`); resolved by the spot rerun, parity 92-100% (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:11`); LAYER_SHEETS still lists it ( `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:11`).

### Confluence
- **Higher Timeframe Regime Composition**: Malkan 5-star setup requires Monthly RSI >= 60 AND Weekly RSI >= 60 for Daily bullish bounce; Monthly RSI <= 40 AND Weekly RSI <= 40 for Daily bearish rejection (`MyTradingSys/backtest/layers/rsi/malkan_40_60.py:13-16`; `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:69,95`; `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md:77-81`).
- **Regime Context Pairing**: Identified in layer review as candidate for REGIME slot combining with Krown regime (same-object pair) (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:11,31`).
- **Live Auto-Trader Gap**: "RSI cross events are rejected as unmapped in the auto-trader (no layer_rules entry); and no layer stacks level" (`MyTradingSys/system/LAYERS.md:103`).

## rsi_divergence

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md` row "RSI 40/60 (Malkan)" covers the 40/60 level study only; no divergence study file exists.

### Idea and source
- **Practitioner Source**: Vishal B Malkan (MalkanView), video extracts `extract_Wvq1TZh8aF0.md` ("RSI Divergence Explained Simply", 2026-04-15) and `extract_cQ-y1oULkBw.md` (`MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:3`; `extracts/processed/malkan/extract_Wvq1TZh8aF0.md:1`).
- **Comparison Basis Quote**: "What do we have to compare? Close to close. Because RSI is based on closing price." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:6; MyTradingSys/backtest/layers/rsi/rsi_divergence.py:3`).
- **Minimum Bars Quote**: "How many candles are needed? Three." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:10; MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:6`).
- **Maximum Bars Quote**: "I will say that less than 10 bars is the most powerful divergence. It should be between three and 10." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:16; MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json (line not re-verified)`).
- **Dilution of Long-Range Divergence Quote**: "at the most 10 times divergence. If you have 30 times divergence, 50 times divergence, that is diluted." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:13; MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py (line not re-verified)`).
- **Decimal Differences Acceptable Quote**: "Sometimes there is divergence in decimals and that will also be acceptable." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:27; MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:9`).
- **Optimal Level Location Quote**: "the most powerful divergence come near 60 bearish divergence and the most powerful bullish divergence comes near 40." (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:20`).
- **Trade Ledger / Ground Truth**: NOT_IN_DATA (no dated trade ledger in repo; `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_MALKAN.md:33-35`).

### Parameters
- **Minimum Lookback Bars**: 3 bars (`SOURCED`, quote: "How many candles are needed? Three." in `extracts/processed/malkan/extract_Wvq1TZh8aF0.md:10`; `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:4,6`).
- **Maximum Lookback Bars**: 10 bars (`SOURCED`, quote: "It should be between three and 10." in `extracts/processed/malkan/extract_Wvq1TZh8aF0.md:16`; `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:5,7`).
- **Price and RSI Comparison Basis**: close_to_close (`SOURCED`, quote: "What do we have to compare? Close to close. Because RSI is based on closing price." in `extracts/processed/malkan/extract_Wvq1TZh8aF0.md:6`; `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json (line not re-verified)`).
- **Minimum RSI Difference (min_rsi_diff)**: 0.0 (`SOURCED`, quote: "Sometimes there is divergence in decimals and that will also be acceptable." in `extracts/processed/malkan/extract_Wvq1TZh8aF0.md:27`; `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:8-9`).
- **Operator Long-Range Window Variant**: 11-60 bars (`OURS` / `NO-SOURCE`, quote: operator T091, operator idea, NO-SOURCE: long-range divergence 11-60 bars between a swing point A and a later same-kind swing point B, NON-adjacent... Malkan rejects this range in his own words in `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py (line not re-verified)`; `MyTradingSys/system/layer_map.json (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Timeframes Evaluated**: 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 1d, 2d (`OURS` grid, `MyTradingSys/system/layer_map.json:473-477`; `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:4`).
- **Evaluation Horizons**: 1, 5, 10, 20 bars (`OURS` / `NO-SOURCE`, quote: "10 bars, t 2 and the 00/12 UTC halves are engineering choices fixed before the run (NO-SOURCE)" in `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md (line not re-verified)`).
- **Causal Event Timestamp**: Bar after swing point B closes (`ts[i+1]`) (`OURS`, quote: Swing point = strict local extreme of the CLOSE... It is only known one bar later, so the event time is ts[i+1] (causal) in `MyTradingSys/backtest/layers/rsi/rsi_divergence.py (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]

### Backtests
1. **Multi-Timeframe RSI Divergence Backtest (RSI-DIV-MTF / T089 + T091, 2026-10-09)**:
   - **Path**: `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:1-24` and `REPORT.md` (summary in `MyTradingSys/system/layer_map.json:643-659`).
   - **Fee-Net**: Fee-net evaluated (one taker round trip 0.10% = 0.0010; `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:6,14; system/layer_map.json:651`).
   - **IS / OOS Partition**: Per-year evaluation 2022-2026 across 2,507,040 1m bars (1,741 full days) of BTCUSDT (`MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:23,17-18; system/layer_map.json:650`).
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
   - **Sample Size (n)**: 7h@00 n=46 (+1.09%, t 2.11); 7h@18 n=47 (+0.15%, t 0.25); 7h@22 n=45 (+0.65%, t 1.18); 7h@23 n=43 (+0.46%, t 1.23); only the 18:00 NY (22/23 UTC) anchor is sourced (`MyTradingSys/research/t090_7h_2026-10-09/RESULT.md:17,17-20`).

### Bugs and assumptions
- **Ruling B154**: "No regime-stratified and no session-stratified backtest verdict exists; every reported edge is one aggregate number... B154 regime split not available in code yet" (`MyTradingSys/research/BUGS.md:266`; `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md (line not re-verified)`).
- **Consecutive Swings Constraint in v1**: "A and B are CONSECUTIVE swing points of the same kind (v1 limit: a divergence against an older, non-adjacent swing is not detected)." (`MyTradingSys/backtest/layers/rsi/rsi_divergence.py:12-14`).
- **Absence of Sourced Exits**: No stop/target bracket or candle confirmation was tested in the raw signal backtest (`MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:16`; `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:40-42`).
- **Unverified Operator Arm Provenance**: Operator 11-60 bar range was explicitly flagged as NO-SOURCE and contrary to Malkan's stated warning on dilution (`MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:10-14`).

### Confluence
- **40/60 Zone Anchoring**: Malkan specifies that regular divergence is strongest when occurring near the 40 level (bullish) or 60 level (bearish) (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:20`).
- **Candlestick Confirmation Confluence**: Malkan requires candle color confirmation (e.g. red candle to confirm bearish divergence) before entry (`extracts/processed/malkan/extract_Wvq1TZh8aF0.md:31-35`).
- **Role in Combined System**: Classified in Layer Review as candidate for TRIGGER slot (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:33`).
- **Interaction with Quad Rotation (Kurisko Super Signal)**: Kurisko's "Super Signal" = quad rotation + a (price vs stochastic) divergence (`MyTradingSys/research/rsi_kurisko_2026-10-09/KURISKO_SPEC.md:10,42`).

## cryptocred

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md` lists CryptoCred as "Small adapter" ("Its tested setups failed").

### Idea and source

- **Analyst / Trader**: CryptoCred (`MyTradingSys/system/LAYERS.md (line not re-verified)`, `MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md (line not re-verified),935`).
- **Primary Source Clusters (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:255-440`)**:
  - Cluster C08: Market Structure Break (MSB): Definition & Significance (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:321`, `MyTradingSys/backtest/layers/FORMULAS.md:167-172`).
  - Cluster C07: Retests (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:255`, `MyTradingSys/backtest/layers/FORMULAS.md:167-172`).
  - Cluster C10: Setup Types: Entry Patterns (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:401`, `MyTradingSys/backtest/layers/FORMULAS.md:167-172`).
  - Source video inventory (`XeQV2ECtZVQ`, `_ndAoizXy64`, `Yp0k8HD5xro`, `BHwoN7VPrBE`, `inqHN8q57X4`): (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:5`).
- **Quoted Sources (file:line)** (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:263-431`):
  - **MSB Definition (C08-E01 / CT-021)**: "my definition is a shift in the sequence of highs and lows in the opposite direction so for a bullish market structure break it is when a sequence of lower highs is violated by a higher high and of course for bearish market structure break is when a sequence of higher lows is violated by a lower low" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:327`, citing video `BHwoN7VPrBE` ~22:00).
  - **Swing High/Low Definition (C09-E01 / CT-020)**: "a swing low is a low with a higher low on both sides and a swing high is a high with a lower high on both sides... there's no single formula... recency is important, significance and size of the move following that high or low is important... the basic smell test... what's the most obvious or outstanding high or low you probably can't go wrong with that" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:370-372`, citing video `BHwoN7VPrBE` ~08:00; also `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md (line not re-verified)`).
  - **Retest Optionality (C07-E01 / CT-035)**: "what you'll often see is this blanket statement that the market needs to retest x to confirm it as support resistance just forget it right i don't know i can't call this anything other than the notion because it's complete fiction... the significant event tends to be the break of structure itself it doesn't suddenly become magically valid if price decides to come back to it" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:263-265`, citing video `inqHN8q57X4` ~06:15).
  - **Setup 1 - S/R Flip Continuation (C10-E01 / CT-025)**: "the long trade is taken on a pullback to the broken high... the short trade is taken on a pullback to the broken low... broken support turning to resistance on re-test broken resistance turning to support on a re-test" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:409-410`, citing video `BHwoN7VPrBE` ~45:00).
  - **Setup 2 - Fib Pullback Continuation (C10-E04 / CT-032)**: "the continuation trade is taken below the breakout point but above the most recent low... i'll map out the low and then the higher high and then as the market starts pulling back it's between these levels that i'll look for structure... personally i look for support resistance structures anywhere between the 618 and 786 retracement... there's no fixed answer really" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:428-431`, citing video `BHwoN7VPrBE` ~50:00, ~55:00).
  - **Setup 3 - Counter-trend / Defensive Rules (C10-E02 / CT-028)**: "if you're trading counter trend you're trading against the current so to speak and therefore you have to be more defensive and less liberal with those positions... shorter holding periods... greater minimum risk reward requirements... let's say two reward for one risk instead of 1.5... different sizing is also another consideration... smaller or more conservative" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:417-419`, citing video `BHwoN7VPrBE` ~33:00).
  - **Stop Placement / Invalidation Principle**: "stop placement is inextricably linked with the trade idea itself your stop reflects your invalidation" (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:12`, citing video `XeQV2ECtZVQ:L33`).


### Parameters

**Swing Detection & Market Structure (cc_structure.py)**
- `left: int = 2`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:12`). Fixed-width fractal choice; repo-chosen default.
- `right: int = 2`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:12`). Fixed-width fractal choice; repo-chosen default.
- `use_body: bool = True`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:12`). Compares candle bodies `max(o, c)` / `min(o, c)` instead of wicks.
- `require_prior_sequence: bool = True`: **SOURCED** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:68`, `MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:330-331`). Enforces sequence violation (lower-high broken by higher-high for bull MSB; higher-low broken by lower-low for bear MSB) per C08-E01.
- `filter_range_noise: bool = False`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:68`, `MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:8-10`).
- `range_lookback: int = 50`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:47,68`, `MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:23-25`).
- `range_extreme_pct: float = 0.25`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_structure.py:63,68`, `MyTradingSys/items/B145_cc_range_noise_live_neutrality.md (line not re-verified)`). Proxies C08-E03 ("not noise" boundary); value is unsourced.

**Retest Classification (cc_retest.py)**
- `tolerance_pct: float = 0.0015`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_retest.py:18`). Price touch threshold `level * (1 +/- tolerance_pct)`.
- `invalidate_pct: float = 0.005`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_retest.py:18`). Invalidation threshold before retest touch `level * (1 -/+ invalidate_pct)`.
- `expiry_bars: int = 200`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_retest.py:18`). Maximum scan window for retest.
- `immediate_bars: int = 5`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_retest.py:57`). Categorization threshold between immediate and rounded retest.

**Trade Setups (cc_setups.py)**
- **Setup 1 (`setup1_sr_flip`)** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53-78`):
  - `stop_buffer_pct: float = 0.001`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53`, `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:18`). Marked NO-SOURCE.
  - `target_r: float = 1.5`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53`, `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:13-14`). Marked NO-SOURCE as fixed value (BHwoN7VPrBE:82 cites 1.5R as a minimum requirement, not a fixed target).
- **Setup 2 (`setup2_fib_pullback`)** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89-172`):
  - `fib_lo: float = 0.618`: **SOURCED** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89`, `MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:428-431`). C08/C10-E04 quote: "structures anywhere between the 618 and 786 retracement".
  - `fib_hi: float = 0.786`: **SOURCED** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89`, `MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:428-431`). C10-E04.
  - `stop_buffer_pct: float = 0.001`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89`, `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:18,18`). Marked NO-SOURCE.
  - `target_r: float = 1.5`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:89`, `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:13,18`). Marked NO-SOURCE.
  - `expiry_bars: int = 200`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:90`). Limit validity timeout.
- **Setup 3 (`setup3_failed_msb_reversal`)** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:178-220`):
  - `failure_lookback: int = 20`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:178`). Window after break to observe failure to make a new extreme.
  - `stop_buffer_pct: float = 0.001`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:178`, `MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:18,40`). Marked NO-SOURCE.
  - `target_r: float = 2.0`: **SOURCED** (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py:178`, `MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:417-419`). C10-E02: counter-trend minimum R requirement "two reward for one risk instead of 1.5".

**Runner & Simulation Parameters (run_cc_setups.py)**
- `tf: str = "1h`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py (line not re-verified)`). Trader quote on timeframes (CT-048): I'll be trading high timeframe from the daily and weekly but a lot of my entries and management will be on the hourly timeframe" (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:515`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- `is_frac: float = 0.70`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:77`). 70/30 chronological train/test split.
- `max_bars: int = 1440`: **OURS** (`MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:356`). Max 1m bars a trade can stay open.
- `tick: float = 0.1`: **OURS (protocol)** (`MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py:102`, `MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:24`). BTCUSDT tick; the 1-tick trade-through rule is BACKTEST_PROTOCOL, not the trader.


### Backtests

**Run 1: L1-D3 075 CryptoCred Adapter Baseline (2026-09-27)**
- **Report path**: `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:37-64`
- **Fee-net or not**: Gross 5-bar forward return stats, plus simulated trades with default taker/maker fees without funding (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:37-43,92-95`).
- **In-sample or out-of-sample**: NOT_IN_DATA for the CC adapter (the 70/30 split is stated only for the D3 RSI study, `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:7`); CC adapter on 1h bars (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:37`).
- **n trades & results** (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:39-42`):
  - `setup1_sr_flip`: 2,517 signals, 500 sim trades (capped), h5 mean return +0.021%, hit rate 46.3%, sim win rate 51.2% (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:39-42`).
  - `setup2_fib_pullback`: 839 signals, 500 sim trades (capped), h5 mean return +0.006%, hit rate 52.1%, sim win rate 61.4% (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:39-42`).
  - `setup3_failed_msb_reversal`: 290 signals, 290 sim trades, h5 mean return +0.036%, hit rate 47.6%, sim win rate 33.4% (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:39-42`).

**Run 2: CC Setups Touch-Fill Model Rerun (2026-10-07)**
- **Report path**: `MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:1-125`
- **Fee-net or not**: Net of fees, both with funding (7,305 records) and without funding (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md (line not re-verified)`). Fee variants: `all_taker` and `maker_entry`.
- **In-sample or out-of-sample**: 70/30 chronological split (IS: 29,063 bars, OOS: 12,457 bars; 41,520 total 1h bars) (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:323`).
- **n trades & results** (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:33-140`):
  - `setup1_sr_flip`: 1,527 signals, 1,477 trades (50 unfilled limits); IS n=1,056, OOS n=421 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:29,52`).
    - `all_taker`: IS mean net R -1.0668 (-0.1067%), OOS mean net R -1.0683 (-0.1068%), Sharpe -0.883 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:34`).
    - `maker_entry`: IS mean net R -0.3802 (-0.0380%), OOS mean net R -0.3819 (-0.0382%), Sharpe -0.263 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:56-57`).
  - `setup2_fib_pullback`: 508 signals, 508 trades (0 unfilled limits); IS n=372, OOS n=136 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:71,90`).
    - `all_taker`: IS mean net R -0.3363 (-0.0659%), OOS mean net R -1.8558 (-0.0383%), Sharpe -0.112 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:75-76`).
    - `maker_entry`: IS mean net R 0.0167 (+0.0049%), OOS mean net R -0.7079 (+0.0331%), Sharpe 0.091 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:94-95`).
  - `setup3_failed_msb_reversal`: 167 signals, 167 trades (0 unfilled limits); IS n=119, OOS n=48 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:113,128`).
    - `all_taker`: IS mean net R -0.0431 (+0.1595%), OOS mean net R -0.2514 (-0.2976%), Sharpe -0.193 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:113-114`).
    - `maker_entry`: IS mean net R 0.0431 (+0.2201%), OOS mean net R -0.1745 (-0.2403%), Sharpe -0.155 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:139`).

**Run 3: CC Setups Trade-Through by 1 Tick Rerun (2026-10-09)**
- **Report path**: `MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:144-245`
- **Fee-net or not**: Net of fees, funding included (7,305 records); both `maker_entry` and `all_taker` (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:185,168`).
- **In-sample or out-of-sample**: 70/30 chronological split (IS: 29,248 bars, OOS: 12,536 bars; 41,784 total 1h bars) (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md (line not re-verified),168`).
- **n trades & results** (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:154-245`):
  - `setup1_sr_flip`: 1,536 signals, 1,486 trades (50 unfilled limits); IS n=1,063, OOS n=423 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:134,172,190`).
    - `maker_entry`: OOS net -0.0380%, Sharpe -0.262, 0 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:167,195`).
    - `all_taker`: OOS net -0.1067%, Sharpe -0.881, 0 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:168,177`).
  - `setup2_fib_pullback`: 516 signals, 516 trades (0 unfilled limits); IS n=373, OOS n=143 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:134,209`).
    - `maker_entry`: OOS net +0.0416%, Sharpe 0.106, 1 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:169`).
    - `all_taker`: OOS net -0.0298%, Sharpe -0.080, 1 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:170,213`).
  - `setup3_failed_msb_reversal`: 167 signals, 167 trades; IS n=119, OOS n=48 (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md (line not re-verified),225-245`).
    - `maker_entry`: OOS net -0.2403%, Sharpe -0.155, 1 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:171`).
    - `all_taker`: OOS net -0.2976%, Sharpe -0.193, 0 of 2 positive OOS years (`MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:172`).

**Run 4: BigTrade Exit Policies Backtest (2026-10-09)**
- **Report path**: `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:21-56`
- **Fee-net or not**: Net of fees and slippage (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:12-14`).
- **In-sample or out-of-sample**: TRAIN (IS) vs VALIDATE (OOS) splits (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:20-56`).
- **Caveats in report** (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:1-3,7`): CONTAMINATED, DEV read VALIDATION 2024-07..12; TRAIN ran to 2025-01-01; VALIDATE is 2025-01..06 only; HOLDOUT 2025-07.. not read. DEV-only rerun: sr_flip:1h time_96_wide_stop_2atr TRAIN +9.8 bp (n 1024) -> +7.6 bp (n 878).
- **n trades & results** (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:21-56`):
  - `layer:cryptocred:failed_msb:15m`: TRAIN n=396, VALIDATE n=57 across 6 exit policies; mean returns negative in both splits across all policies (e.g. `live_like_1pct_2pct_8bars`: -8.0 bp TRAIN, -11.2 bp VALIDATE) (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:21-26`).
  - `layer:cryptocred:failed_msb:1h`: TRAIN n=109, VALIDATE n=17 across 6 exit policies (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:27-32`).
  - `layer:cryptocred:fib_pullback:15m`: TRAIN n=1,149, VALIDATE n=147 across 6 exit policies; all 6 policies negative in both splits (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md (line not re-verified)`).
  - `layer:cryptocred:fib_pullback:1h`: TRAIN n=278, VALIDATE n=47 across 6 exit policies (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:39-44`).
  - `layer:cryptocred:sr_flip:15m`: TRAIN n=4,035, VALIDATE n=583 across 6 exit policies; all 6 policies negative in both splits (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md (line not re-verified)`).
  - `layer:cryptocred:sr_flip:1h`: TRAIN n=1,024, VALIDATE n=163 across 6 exit policies; `time_96_wide_stop_2atr` policy recorded +9.8 bp TRAIN / +0.1 bp VALIDATE, while remaining 5 policies were net negative (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:51-56,143`).

**Run 5: BigTrade Fires Parity Check (2026-10-09)**
- **Report path**: `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:16,24`
- **Fee-net or not**: Parity check only (firing agreement between offline detector and live engine alerts; no P&L) (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:16`).
- **In-sample or out-of-sample**: Last 5 days live comparison (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:16`).
- **n trades & results**: Superseded perp run: parity 0-4% for cryptocred and fabio keys (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:12`). Spot rerun 2026-10-09: "All kline keys 92-100 % parity" (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:11`). No P&L.

**Run 6: Stop Placement & Parameter Sweep Study (2026-10-10)**
- **Report path**: `MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:47-69`, `MyTradingSys/research/cryptocred_stop_2026-10-10/stop_sweep_result.json`
- **Fee-net or not**: Net R after costs on 1h bars (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:47-49`).
- **In-sample or out-of-sample**: DEV / full archive dataset (`raw_1m_2022` 1h bars) (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:47`).
- **n trades & sweep results** (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:51-65`):
  - `setup1_sr_flip` (n=1,487): (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md (line not re-verified)`):
    - `pct_0.1` (NO-SOURCE): net R -1.069, hit rate 0.373 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:58`).
    - `pct_0.25` (NO-SOURCE): net R -0.386, hit rate 0.406 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:59`).
    - `pct_0.5` (NO-SOURCE): net R -0.174, hit rate 0.411 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:60`).
    - `atr_1.0` (CC-invalidation): net R -0.162, hit rate 0.411 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:55`).
    - `atr_1.5` (CC-invalidation): net R -0.095, hit rate 0.421 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:62`).
    - `atr_2.0` (CC-invalidation): net R -0.101, hit rate 0.420 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:63`).
  - `setup2_fib_pullback` (n=1,392): (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md (line not re-verified)`):
    - `pct_0.1` (NO-SOURCE): net R -1.307, hit rate 0.306 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:58`).
    - `pct_0.5` (NO-SOURCE): net R -0.209, hit rate 0.367 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:59`).
    - `atr_1.0` (CC-invalidation): net R -0.184, hit rate 0.361 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:60`).
    - `atr_2.0` (CC-invalidation): net R -0.073, hit rate 0.405 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:61`).
  - `setup3_failed_msb_reversal` (n=167): (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:62-65`):
    - `pct_0.1` (NO-SOURCE): net R -1.050, hit rate 0.317 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:62`).
    - `pct_0.5` (NO-SOURCE): net R -0.272, hit rate 0.305 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:63`).
    - `atr_1.0` (CC-invalidation): net R -0.217, hit rate 0.329 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:64`).
    - `atr_2.0` (CC-invalidation): net R -0.040, hit rate 0.371 (`MyTradingSys/research/cryptocred_stop_2026-10-10/STOP_SOURCES.md:65`).

**Run 7: Live Range Noise Neutrality Archive Replay (2026-10-10)**
- **Report path**: `MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:29-34`
- **Fee-net or not**: Net R after fees (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:14,30`).
- **In-sample or out-of-sample**: Archive replay (`Dumps/backtest/raw_1m_2022 + raw`, 1h) (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:14,30`).
- **n trades & results** (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:30-34`):
  - `setup1_sr_flip`: n=474 with flag vs n=1,477 without; mean net R -1.1351 with flag vs -1.0707 without (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:30-31`).
  - `setup3_failed_msb_reversal`: n=52 with flag vs n=167 without; mean net R -0.1504 with flag vs -0.1029 without (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:31-32`).
  - `setup2_fib_pullback`: passed neutrality check (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:32`).


### Bugs and assumptions

- Ruling B143 (BLOCKED / MED) (`MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:1-8`):
  - Title: CryptoCred 0.1 percent stop buffer and 1.5R target are NO-SOURCE (`MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:1-8`).
  - Findings: Setup 1, 2, and 3 stops utilize a hardcoded 0.1% buffer (`cc_setups.py:53,89,178`), and setups 1 and 2 utilize a fixed 1.5R target (`cc_setups.py:53,89`), which are repo-invented numbers (NO-SOURCE) (`MyTradingSys/items/B143_cryptocred_stop_buffer_and_target_unsourced.md:12-14,40`).
- Ruling B145 (CLOSED / LOW) (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:1-8`):
  - Title: `classify_msb` `filter_range_noise` is off in the live CryptoCred layer; no evidence it is neutral or better (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:1-8`).
  - Receipt: Tested on archive replay; turning the flag on made net R worse for `setup1_sr_flip` and `setup3_failed_msb_reversal`; flag kept disabled (`MyTradingSys/items/B145_cc_range_noise_live_neutrality.md:29-34`).
- Ruling B151 (CLOSED / MED) (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:1-8`):
  - Title: CryptoCred limit-fill backtest fills on touch and drops signals by a future event, so its PASS numbers are upper bounds; maker-entry fee refund applied on touch fills with a 0.1% stop (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md (line not re-verified)`).
  - Receipt: Earlier PASS verdicts were artifacts of filling resting limits on mere touch and post-close bias (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:16-20`, `MyTradingSys/research/fast_track_2026-09-27/CC_SETUPS_RERUN_LIMITFILL_2026-10-07.md:13-17`). Fixed in runner by requiring trade-through by 1 tick (TICK=0.1) and surfacing `open_at_end` trades; on trade-through rerun, all setups fail net of fees (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:27-39`). Also fixed bear fib zone indexing bug where bear branches built descending zones preventing short signals from ever being emitted (`MyTradingSys/items/B151_backtest_fill_optimism_and_selection.md:32`).
- Ruling B154 (OPEN / MED) (`MyTradingSys/items/B154_regime_and_session_stratified_backtest.md:1-8`):
  - Title: No regime-stratified and no session-stratified backtest verdict exists; every reported edge is one aggregate number (`MyTradingSys/items/B154_regime_and_session_stratified_backtest.md:1-8`).
  - Finding: CryptoCred backtest verdicts are reported as aggregate numbers across the entire dataset; no stratification by market regime (bull, bear, range) or session (e.g. US equity open, 12h boundaries) exists (`MyTradingSys/items/B154_regime_and_session_stratified_backtest.md:17-21`).
- Historical Module Bug (BACKTEST_L1_REPORT) (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:50-64`):
  - `cc_setups.setup2_fib_pullback` originally indexed `swings[broken_swing_i]`, treating a bar index as a swings-list index, raising `IndexError` on real data (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:50-58`). Fixed in commit `54ad393` (`MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:60-64`).


### Confluence

- Intended Confirmation Sources (Trader Spec) (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:280-395`):
  - CryptoCred explicitly specifies that MSB and structure setups require confluence from high-timeframe key levels, horizontal support/resistance, open prices (monthly, weekly, daily opens), funding rates, and open interest (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md:375-385`, citing C09-E02 / CT-024, CT-030).
  - Timeframe confluence: Higher timeframe structure dominates lower timeframe moves; break validity requires close on the structure's anchor timeframe (`MyTradingSys/research/_archive/loose_2026-10/cross_trader_consolidated.md (line not re-verified),389-395`, citing C07-E04 / CT-037, C09-E04 / CT-084).
- Repo Implementation State (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py (line not re-verified),89,178`):
  - `cc_structure.py`, `cc_retest.py`, and `cc_setups.py` evaluate setups on isolated single-timeframe price series without multi-timeframe confirmation (`MyTradingSys/backtest/layers/cryptocred/cc_setups.py (line not re-verified),89,178`).
  - Confirmation from Tom (order flow / volume profile): NOT_IN_DATA.
  - Confirmation from Fabio (CVD absorption / escalation): NOT_IN_DATA.
  - Confirmation from RSI levels / divergence: NOT_IN_DATA.
  - Multi-layer combination in live alerts: Live alerts wire `cc_sr_flip_layer`, `cc_fib_pullback_layer`, and `cc_failed_msb_layer` as standalone event streams (`MyTradingSys/backtest/layers/alerts/live_layers.py:140-142`); no multi-layer confluence filter is active in code (`MyTradingSys/system/LAYERS.md:106-116`).

## pitchfork

Wired in the simulator: yes. `MyTradingSys/research/sim_desk/studies/pitchfork.py` (`MyTradingSys/research/sim_desk/PLUGIN.md` row "Pitchfork", plugged in 2026-10-28).

### Idea and source

> Reviewer note: the biographies and book titles below come from one LLM-written synthesis (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md`) with no external reference; treat as single-source, unverified. `MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_362293de1b70_pitchfork.md:25` (TradingView) defines Schiff vs Modified Schiff the opposite way to papers/01 and `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:68-75`.

- **Primary Historical Inventor:** Dr. Alan Hall Andrews (1900–1985), private Babson Action-Reaction Course (1960–1975) [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:26-28`].
  - *Quoted Source:* Dr. Alan Hall Andrews (1900–1985), an MIT-educated engineer, mathematician, and Babson attendee, refined Babson’s macroeconomic observations into micro-level chart geometry... The cornerstone of Andrews' teachings was the Median Line Method—a three-point geometric vector construction that market participants colloquially termed the 'Pitchfork' due to its distinctive three-pronged appearance. [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:26-28`]. [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
  - *Quoted 80% Rule:* Prices will reach the Median Line approximately 80% of the time following the completion of Pivot 2. [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:83`, citing Alan H. Andrews, *The Babson Action-Reaction Course*, Section 2, p. 12 via `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:35`]. [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
  - *Quoted Hagopian's Rule:* If price reverses before reaching the Median Line, it signals an acute imbalance of order flow. Price will accelerate violently in the opposite direction and break completely out of the pitchfork channel through the opposite parallel line. [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:97`, citing Alan H. Andrews, Section 4 via `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:41`]. [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Schiff Pitchfork Modification:** Jerome Schiff [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:121-128`, `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:9`].
  - *Quoted Source:* Jerome Schiff observed that after an impulsive breakout, the initial retracement ($P_1 \to P_2$) is often shallow, causing a standard $P_0 \to M$ vector to possess a steep angle ($> 60^\circ$)... Schiff solved this by displacing the origin point $P_0$ 50% of the distance toward $P_1$ in both time and price: $t_{0,\text{Schiff}} = \frac{t_0 + t_1}{2}, p_{0,\text{Schiff}} = \frac{p_0 + p_1}{2}$. [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:121-128`]. [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Modified Schiff Pitchfork:** attribution not stated (paper: Popularized in modern futures and algorithmic charting) [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:130-136`, `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:29`]. [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
  - *Quoted Source:* Popularized in modern futures and algorithmic charting, the Modified Schiff Pitchfork maintains the original time coordinate $t_0$, but shifts the price coordinate $p_0$ to the vertical midpoint between $P_0$ and $P_1$: $t_{0,\text{ModSchiff}} = t_0, p_{0,\text{ModSchiff}} = \frac{p_0 + p_1}{2}$. [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:131-134`; no author named in the source paragraph; RESEARCH_PITCHFORK_LAYER.md:27-28 cites Dologa for the slope-switch rule P-02, not this construction]. [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Institutional Median Line & Channel Extensions:** Timothy Morge (1954–2020), *Trading with Median Lines: Mapping the Markets* (2002) [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:141-152`].
  - *Quoted Source:* Formulated quartile lines (25%, 50%, 75% inner parallels), warning lines ($WL_1, WL_2, WL_3$), sliding parallel lines, and energy coils around the median line [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:144-152`].
- **Algorithmic Codification & Confirmation Delay:** Patrick Mikula, *The Best Trendline Methods of Alan Andrews and Five New Techniques* (2002) [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:153-157`, `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:23`].
  - *Quoted Source:* "Pivots $P_0, P_1, P_2$ must be confirmed swing extrema with a minimum clearance of $N \ge 3$ bars on each side and a swing amplitude exceeding $k \ge 2.5 \times \text{ATR}_{14}$." [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:24`, citing Mikula 2002:42].
- **MTS Operator Own Chart Input:** Stacked Schiff pitchforks on 1W spot BTC [SOURCED: `MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_362293de1b70_pitchfork.md:3-6`].
  - *Quoted Source:* Operator words: 'Now my own charts. I use pitch forks. Let us also add that pitchfork layer now!!! Ask Gemini to d' ... Tool settings: Style = Schiff, Extend lines on, Median red, only level 1 enabled (blue), other levels (0.382 .. 2.45) off, Background on [SOURCED: `MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_362293de1b70_pitchfork.md:21, 19`]. [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]


### Parameters

- **Pivot confirmation lookback delay ($N = 3$ bars for 1D, $N = 4$ bars for 4H):** [SOURCED / OURS: see sub-items]
  - $N \ge 3$ bars lookahead delay: SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:24`, citing Patrick Mikula, *The Best Trendline Methods of Alan Andrews*, p. 42; Timothy Morge, *Trading with Median Lines*, p. 18].
  - $N = 4$ bars (16 hours) for 4H study: OURS [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:8`].
- **Swing amplitude threshold ($k \ge 2.5 \times \text{ATR}_{14}$ or $\text{min\_change\_pct} = 0.02$):** [SOURCED / OURS: see sub-items]
  - $k \ge 2.5 \times \text{ATR}_{14}$: SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:24`, citing Mikula 2002:42].
  - $\text{min\_change\_pct} = 0.02$ (2% reversal threshold in ZigZag): OURS [SOURCED: `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:337`].
- **Schiff switch slope angle threshold ($|\theta| > 55^\circ$):** SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:28-29`, citing Jerome Schiff; Mircea Dologa, *Integrated Pitchfork Analysis*, Vol 1, p. 65].
- **Extreme slope invalidation angle threshold ($|\theta| > 75^\circ$):** SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:31`, citing Dologa 2007:65].
- **Relative slope steepness ratio for auto Schiff (`max_slope_bars_ratio = 1.0`):** OURS [SOURCED: `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:313, 327`].
- **Median Line Reach criteria (price low $\le ML \le$ high or directional close across ML):** SOURCED [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:82-85`, Alan H. Andrews; implemented in `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:169-176`].
- **Hagopian failure minimum approach threshold ($15\%$ distance towards ML from origin tine before rollover):** OURS [SOURCED: `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:201-204`].
- **Hagopian failure target (measured move equal to channel width $W = |p_{UML} - p_{ML}|$):** SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:42`, citing Alan H. Andrews, Section 4; Timothy Morge, p. 74].
- **Stop-loss level for tine bounces (1.0 ATR beyond Pivot 2):** SOURCED [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:52-53`, `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:186`]. The backtests used fixed % stops instead: 1.5% (1D, `MyTradingSys/research/pitchfork_2026-10-19/run_pitchfork_event_study.py:242`; 4H tine entry, `MyTradingSys/research/pitchfork_2026-10-19/run_pitchfork_4h_poc_study.py:278`), 2.0% (4H confirm entry, `:249`).
- **Logarithmic pitchfork transformation ($y = \ln(p)$, geometric midpoint $M_{\ln} = \sqrt{p_1 \cdot p_2}$):** OURS [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:43-58`, `MyTradingSys/backtest/layers/pitchfork/pitchfork_detector.py:231-250`].
- **Volume Profile Value Area Confluence ($P_2$ inside 70% Value Area $[VAL, VAH]$):** OURS (study design, `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:26,80-82`; papers/03:20-22,51-55 describe only a POC/HVN idea, not a 70% VA filter).
- **Volume Profile POC alignment tolerance ($\pm 0.35\%$ or $\pm 0.75\%$ or $\pm 1.5\%$):** [OURS: see sub-items]
  - $\pm 0.35\%$: OURS [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:207`, `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:138`].
  - $\pm 0.75\%$ and $\pm 1.5\%$: OURS [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:27-28`].
- **Tine limit retest entry execution mode (`TINE_LIMIT_RETEST`):** OURS [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:22-24`].
- **Volume Profile bin grid width ($w = 10.0$ USD, FORMULAS 18.1):** OURS [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:9`].


### Backtests

**A. Phase 1 Daily (1D) Historical Event Study (2020–2026)**
- **Report Path:** `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:1-46` [SOURCED: file exists]
- **Runner Script:** `MyTradingSys/research/pitchfork_2026-10-19/run_pitchfork_event_study.py:1-40` [SOURCED: file exists]
- **Ledger/Trial Path:** `MyTradingSys/research/pitchfork_2026-10-19/TRIALS_PITCHFORK.csv:1-5` [SOURCED: file exists]
- **Data Period & Span:** 2020-01-01 to 2026-09-26, 2,461 daily bars [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:4`]
- **In-Sample / Out-of-Sample (Split):** `DEV` split (`F:/MTS/data/tom_raw + dev_ext`) [`MyTradingSys/research/pitchfork_2026-10-19/TRIALS_PITCHFORK.csv:2-5`]; the DEV label is hard-coded (`MyTradingSys/research/pitchfork_2026-10-19/run_pitchfork_event_study.py:372`) and the data window runs to 2026-09-26 (`MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:4`), overlapping the 2026-06-26.. holdout other layers use: holdout status NOT_IN_DATA, not "unread"
- **Fee Model:** Net of fees ($0.10\%$ round-trip taker fee + $0.02\%$ slippage hurdle) [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:6`]
- **Sample Size ($n$ Setups):** $n = 361$ setups per model (same 361 forks for each of the 4 models) [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:16-20`, `MyTradingSys/research/pitchfork_2026-10-19/TRIALS_PITCHFORK.csv:2-5`]
- **Reported Numbers per Variant ($n = 361$):** [SOURCED: see sub-items]
  1. *Standard Andrews:* ML Reach Rate = $55.96\%$, Avg Bars to ML = $6.5$, Premature Breaches = $50.97\%$, Hagopian Hit Rate = $33.88\%$, Win Rate = $36.84\%$, Mean Net Return = $+0.86\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:17`].
  2. *Schiff:* ML Reach Rate = $86.15\%$, Avg Bars to ML = $4.7$, Premature Breaches = $19.11\%$, Hagopian Hit Rate = $33.9\%$, Win Rate = $34.9\%$, Mean Net Return = $-1.12\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:18`].
  3. *Modified Schiff:* ML Reach Rate = $89.2\%$, Avg Bars to ML = $4.3$, Premature Breaches = $12.74\%$, Hagopian Hit Rate = $34.04\%$, Win Rate = $36.84\%$, Mean Net Return = $-1.12\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:19`].
  4. *Log Modified Schiff:* ML Reach Rate = $90.03\%$, Avg Bars to ML = $4.6$, Premature Breaches = $12.74\%$, Hagopian Hit Rate = $34.0\%$, Win Rate = $37.12\%$, Mean Net Return = $-0.95\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:20`].

**B. Phase 2 4-Hour (4H) Pitchfork & Volume Profile Event Study (2020–2026)**
- **Report Path:** `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:1-121` [SOURCED: file exists]
- **Runner Script:** `MyTradingSys/research/pitchfork_2026-10-19/run_pitchfork_4h_poc_study.py:1-40` [SOURCED: file exists]
- **Ledger/Trial Path:** `MyTradingSys/research/pitchfork_2026-10-19/TRIALS_PITCHFORK_4H.csv:1-33` [SOURCED: file exists]
- **Data Period & Span:** 2020-01-01 00:00:00 to 2026-09-26 20:00:00, 14,766 4-hour bars [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:4`]
- **In-Sample / Out-of-Sample (Split):** no split column in `MyTradingSys/research/pitchfork_2026-10-19/TRIALS_PITCHFORK_4H.csv`; window to 2026-09-26 (`MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:4`), overlapping the 2026-06-26.. holdout: holdout status NOT_IN_DATA
- **Fee Model:** Net of fees (Binance VIP0: $0.02\%$ maker entry + $0.05\%$ taker exit + $0.02\%$ slippage = $0.09\%$ limit round-trip; $0.12\%$ market round-trip) [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:7`]
- **Sample Size ($n$ Setups):** $n = 1,273$ alternating 3-pivot swing structures across 32 experimental conditions [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:6, 36-70`]
- **Key Reported Conditions & Numbers ($n$ fills / trades):** [SOURCED: see sub-items]
  1. *Standard Andrews (UNFILTERED, TINE_LIMIT_RETEST):* Qualified Setups = $1,273$, Fills $n = 1,045$, Win Rate = $27.56\%$, ML Reach = $19.04\%$, Mean Net PnL = $+0.39\%$, Profit Factor = $1.34$, Avg Win = $+5.57\%$, Avg Loss = $-1.58\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:38`].
  2. *Standard Andrews (UNFILTERED, CONFIRM_CLOSE_MKT):* Qualified Setups = $1,273$, Fills $n = 1,273$, Win Rate = $30.95\%$, ML Reach = $47.53\%$, Mean Net PnL = $-0.93\%$, Profit Factor = $0.41$, Avg Win = $+2.10\%$, Avg Loss = $-2.29\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:39`].
  3. *Standard Andrews (VA_CONFLUENT, TINE_LIMIT_RETEST):* Qualified Setups = $326$, Fills $n = 282$, Win Rate = $29.79\%$, ML Reach = $21.63\%$, Mean Net PnL = $+0.69\%$, Profit Factor = $1.62$, Avg Win = $+6.05\%$, Avg Loss = $-1.58\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:40`].
  4. *Standard Andrews (POC_1.5PCT, TINE_LIMIT_RETEST):* Qualified Setups = $177$, Fills $n = 162$, Win Rate = $33.95\%$, ML Reach = $25.31\%$, Mean Net PnL = $+0.88\%$, Profit Factor = $1.83$, Avg Win = $+5.67\%$, Avg Loss = $-1.59\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:42`].
  5. *Schiff (UNFILTERED, TINE_LIMIT_RETEST):* Qualified Setups = $1,273$, Fills $n = 758$, Win Rate = $29.68\%$, ML Reach = $26.12\%$, Mean Net PnL = $+0.05\%$, Profit Factor = $1.04$, Avg Win = $+3.86\%$, Avg Loss = $-1.56\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:46`].
  6. *Schiff (VA_CONFLUENT, TINE_LIMIT_RETEST):* Qualified Setups = $326$, Fills $n = 285$, Win Rate = $30.18\%$, ML Reach = $24.21\%$, Mean Net PnL = $+0.36\%$, Profit Factor = $1.33$, Avg Win = $+4.79\%$, Avg Loss = $-1.56\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:48`].
  7. *Modified Schiff (UNFILTERED, TINE_LIMIT_RETEST):* Qualified Setups = $1,273$, Fills $n = 782$, Win Rate = $34.14\%$, ML Reach = $30.43\%$, Mean Net PnL = $+0.18\%$, Profit Factor = $1.18$, Avg Win = $+3.81\%$, Avg Loss = $-1.70\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:54`].
  8. *Modified Schiff (UNFILTERED, CONFIRM_CLOSE_MKT):* Qualified Setups = $1,273$, Fills $n = 1,273$, Win Rate = $41.87\%$, ML Reach = $87.98\%$, Mean Net PnL = $-0.76\%$, Profit Factor = $0.43$, Avg Win = $+1.66\%$, Avg Loss = $-2.50\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:55`].
  9. *Modified Schiff (VA_CONFLUENT, TINE_LIMIT_RETEST):* Qualified Setups = $326$, Fills $n = 279$, Win Rate = $39.07\%$, ML Reach = $34.05\%$, Mean Net PnL = $+0.61\%$, Profit Factor = $1.63$, Avg Win = $+4.67\%$, Avg Loss = $-1.99\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:56`].
  10. *Log Modified Schiff (VA_CONFLUENT, TINE_LIMIT_RETEST):* Qualified Setups = $326$, Fills $n = 278$, Win Rate = $37.05\%$, ML Reach = $31.65\%$, Mean Net PnL = $+0.59\%$, Profit Factor = $1.59$, Avg Win = $+4.61\%$, Avg Loss = $-1.77\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:64`].
  11. *Log Modified Schiff (POC_0.75PCT, TINE_LIMIT_RETEST):* Qualified Setups = $51$, Fills $n = 42$, Win Rate = $45.24\%$, ML Reach = $42.86\%$, Mean Net PnL = $+0.54\%$, Profit Factor = $1.62$, Avg Win = $+3.52\%$, Avg Loss = $-1.92\%$ [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:68`].

**C. Algorithmic Benchmarking of YouTube & Practitioner Models**
- **Report Path:** `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:86-111` [SOURCED: file exists]
- **Runner Script:** `MyTradingSys/research/pitchfork_2026-10-19/eval_btc_pitchfork_traders.py:1-40` [SOURCED: file exists]
- **Data Period & Span:** Macro Bitcoin swings 2017 to 2026 [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:86-88`]
- **NOT REPRODUCIBLE:** the figures in this block appear only in `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:93-110`; `MyTradingSys/research/pitchfork_2026-10-19/eval_btc_pitchfork_traders.py` runs 2 synthetic-path setups and computes none of these metrics.
- **Fee Model:** NOT_IN_DATA (Evaluates geometric channel metrics: slope angle, ML reach rate, premature breach rate, and edge score) [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:89-111`]
- **In-Sample / Out-of-Sample:** NOT_IN_DATA
- **Sample Size ($n$):** NOT_IN_DATA (script uses 2 hand-typed synthetic weekly paths) [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/eval_btc_pitchfork_traders.py:34-40`]
- **Results Summary Table:** [SOURCED: see sub-items]
  1. *Fractal Flow (Mod. Schiff, Vol Profile Confluence):* Slope = $28^\circ - 35^\circ$, ML Reach = $81.2\%$, Premature Breach = $8.4\%$, Algorithmic Edge Score = $92/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:93-95`].
  2. *MTS Operator Model (Stacked Schiff Grid, TV Style):* Slope = $32^\circ - 42^\circ$, ML Reach = $78.5\%$, Premature Breach = $11.2\%$, Algorithmic Edge Score = $90/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:96-98`].
  3. *Timothy Morge / Mikula (Standard + Mod. Schiff, Hagopian):* Slope = $35^\circ - 45^\circ$, ML Reach = $77.8\%$, Premature Breach = $12.0\%$, Algorithmic Edge Score = $88/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:99-100`].
  4. *Bob Loukas (Logarithmic Andrews):* Slope = $25^\circ - 32^\circ$, ML Reach = $75.0\%$, Premature Breach = $9.8\%$, Algorithmic Edge Score = $85/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:102-104`].
  5. *CryptoCred (Standard, Strict S/R):* Slope = $40^\circ - 55^\circ$, ML Reach = $71.4\%$, Premature Breach = $18.5\%$, Algorithmic Edge Score = $82/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:105-107`].
  6. *Generic Retail Tutorials (Standard Linear):* Slope = $65^\circ - 78^\circ$, ML Reach = $48.2\%$, Premature Breach = $62.4\%$, Algorithmic Edge Score = $24/100$ [SOURCED: `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:108-110`].


### Bugs and assumptions

- **Official Lab Rulings:** Query command `python scripts/dev/lab_query.py rulings pitchfork` returns `{"family": "pitchfork", "rulings": []}`. There are currently zero recorded lab rulings against family `pitchfork` [SOURCED: `python scripts/dev/lab_query.py rulings pitchfork`].
- **Late-Entry Penalty Bug / Structural Drag in Naive Market Entries:** The Phase 2 study identified that entering on the market close of the confirmation bar (`CONFIRM_CLOSE_MKT`, 16 hours after Pivot 2) caused negative expectancy ($-0.16\%$ to $-1.31\%$) across all models because $40\%-60\%$ of the move toward the Median Line had already transpired while the full stop-loss remained [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:19-22, 75-77`].
- **Linear Slope Distortion & Premature Boundary Breaches:** Standard Andrews Pitchfork on arithmetic scales produces steep slopes ($> 60^\circ$ to $78^\circ$) on Bitcoin, resulting in a high rate of premature false tine breaches ($42.5\%$ to $62.4\%$) during normal sideways consolidations [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:29-32`, `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:108-110, 118-120`, `MyTradingSys/research/pitchfork_2026-10-19/PHASE1_EVENT_STUDY.md:30-32`].
- **Subjective / Cherry-Picked Anchor Risk:** Discretionary chartists select anchor pivots with hindsight; algorithmic implementations must enforce non-repainting ZigZag confirmation with lookahead delays ($N \ge 3$ or $N \ge 4$ bars) [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:68-96`, `MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_362293de1b70_pitchfork.md:27-28`].
- **Missing Raw Coordinates in TradingView Export:** Exact anchor coordinate numbers from the MTS Operator's TradingView charts are not stored in any repo file (`NOT_IN_DATA`) [SOURCED: `MyTradingSys/research/live_reads/2026-10-17_live_market_1017/SET_362293de1b70_pitchfork.md:17`].


### Confluence

The pitchfork layer is designed as a **Layer 1 Dynamic Location & Horizon Filter** that is confirmed by, and provides confluence to, the following layers:

1. **Tom Core / Microstructural Proof Gates (`src/main/java/datafeed/SetupCandidatesBuilder.java`):** [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:62-72`]
   - *Absorption Proof (`proof_absorption`):* At the Lower Median Line ($LML$), volume on the 5-minute bar must exceed the 80th percentile with negative Delta, but price closes in the upper half of the bar (passive buy absorption) [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:65-66`].
   - *CVD Alignment Proof (`proof_cvd_aligned`):* At the bounce point, Cumulative Volume Delta must not diverge downward against the trade direction [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:67-68`].
   - *Delta Flip Proof (`proof_delta_flip`):* Confirmation bar following the tine touch exhibits positive Delta on an up-close [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/RESEARCH_PITCHFORK_LAYER.md:69-70`].
2. **Volume Profile Layers (Anchored POC / Value Area High & Low):** [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:25-29`]
   - *Value Area Confluence (`VA_CONFLUENT`):* Swing origin pivot $P_2$ must reside within the 70% Value Area $[VAL, VAH]$ of the foundational impulse swing [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:26, 80-82`].
   - *Point of Control Confluence (`POC_1.5PCT` / `POC_0.75PCT`):* Tine touches aligning within $\pm 0.75\%$ to $\pm 1.5\%$ of the Point of Control [SOURCED: `MyTradingSys/research/pitchfork_2026-10-19/PHASE2_4H_POC_STUDY.md:27-28, 88-92`].
   - Confluence with high-volume POC or prior session VAH/VAL reaction probability: papers/02:207 says 77.7% -> 86.4%; papers/03:125 says 77.8% -> 88.4%; two inconsistent unbacked claims, no run in the repo supports either [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:206-208`, `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:124-125`].
3. **CryptoCred Dynamic Channels & Swing Failure:** [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:169-172`]
   - Treats the pitchfork Median Line as dynamic Fair Value / Point of Control, and outer tines as dynamic support/resistance corridors aligned with swing failure patterns [SOURCED: `papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md:169-172`, `papers/03_YOUTUBE_PITCHFORK_MASTERS_BTC_STUDY.md:36-38`].
4. **Positioning / Open Interest Delta:** [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:156-163`]
   - In Hagopian failures, buyer/seller exhaustion before the Median Line accompanied by rising Open Interest and stagnating CVD precedes liquidation cascades [SOURCED: `papers/02_PITCHFORK_APPLICATION_ON_BTC.md:156-163`].

## live_engine

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md` lists the live engine as "Does not fit" (execution, not a backtest).

### Idea and source
- **Primary Infrastructure Specification**: "The live engine, execution and live-market reads that feed every layer (infrastructure, not a strategy)." (`MyTradingSys/system/layer_index.json:554`).
- **Family Classification**: kind: infrastructure, layers: [], ledger: [] (`MyTradingSys/system/layer_index.json (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Live Session Reading Protocol**: Operational discipline for live market reading and state tracking... Check 1: Quote the number (direct quote from paste, zero rounding)... Check 2: Delta check before verdict (compare current to prior number in same paste series) (`MyTradingSys/methodology/live_session_protocol.md (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Screenshot Intake Specification**: Takes incoming chart screenshots from the operator, classifies them against the setup library, extracts levels and annotations, logs an intake event, and files a finding or no-action note (`MyTradingSys/methodology/screenshot_intake.md (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Deployment Runbook Specification**: Single procedure for promoting validated research code to the live execution runner... Live tree defined exclusively by `.mts_live` marker; background deployment tasks retired 2026-10-17 (`MyTradingSys/system/DEPLOY_RUNBOOK.md (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Execution Architecture Overview**: Auto-trader, order execution, position manager, risk guards, reconciler, journal, testnet suites (`MyTradingSys/execution/README.md (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Trader Association / Ledger**: NOT_IN_DATA (kind: infrastructure... layers: [], ledger: [] in `MyTradingSys/system/layer_index.json (line not re-verified)`; infrastructure engine, not an individual trader strategy; no trader trade ledger exists). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]

### Parameters
- **Venue & Contract Market**: Deribit BTC-PERPETUAL inverse contract (`SOURCED`, quote: Deribit BTC-PERPETUAL inverse contract in `MyTradingSys/execution/TESTNET_SUBACCOUNTS.md (line not re-verified)`; `MyTradingSys/execution/trade_ledger.py (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Position Sizing Calibration**: 20 to 1000 USD notional, base testnet size 20 USD (`OURS`, quote: size_usd: 20 in `MyTradingSys/execution/auto_trader_config.json (line not re-verified)`; `MyTradingSys/execution/FABIO_TESTNET_SLOT.md (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Subaccount Routing Tiers**: 5 primary tiers (`main`, `jishu_1` through `jishu_4`) expanding to 16 discrete signal prefix routes (`OURS`, quote: 16 discrete signal prefix routes in `MyTradingSys/execution/auto_trader_config.json (line not re-verified)`; `MyTradingSys/execution/TESTNET_SUBACCOUNTS.md (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Position Netting Isolation**: 1 concurrent trade per subaccount (Deribit nets inverse contracts per account) (`SOURCED`, quote: Deribit nets 1 BTC-PERPETUAL position per account (1 account = 1 concurrent trade) in `MyTradingSys/execution/TESTNET_SUBACCOUNTS.md:3`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Execution Fee Floor**: Deribit taker fee 0.05% (5 bps per side = 10 bps RT) (`SOURCED`, quote: DERIBIT_TAKER = 0.0005 per side in `MyTradingSys/backtest/fees.py:10`; `MyTradingSys/backtest/layers/FORMULAS.md:410`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Safety State Propagation**: Global propagation of `HALT`, `HALT_DAILY_LOSS`, and `AUTO_PAUSE` across all subaccount slots (`OURS`, quote: HALT, HALT_DAILY_LOSS, and AUTO_PAUSE remain strictly global in `MyTradingSys/execution/FABIO_TESTNET_SLOT.md:4`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Unsourced Bracket Parameters**: Stop percentage 1.0%, target 2.0%, horizon 8 bars (1h) (`OURS` / `NO-SOURCE`, quote: "Layer bracket in auto_trader.py is a fixed unsourced stop_pct 1.0, targets 2, size 20" in `MyTradingSys/research/BUGS.md:229` [B118]).
- **Unsourced Stop Floors**: Minimum stop floor 0.1% and fallback stop 0.2% (`OURS` / `NO-SOURCE`, quote: "Unsourced 0.1 percent minimum stop floor and 0.2 percent fallback stop are still live in code" in `MyTradingSys/research/BUGS.md:227` [B116]).
- **Unsourced Proof Gating Bands**: Proof bands 3 and 5 gating entry (`OURS` / `NO-SOURCE`, quote: "Unsourced proof bands 3 and 5 gate WAIT_PROOF, WATCH and SETUP_FORMING" in `MyTradingSys/research/BUGS.md:228` [B117]).
- **Unsourced Net R:R Hurdle**: Net R:R floor 1.25 (`OURS` / `NO-SOURCE`, quote: net_rr floor 1.25 is NO-SOURCE in `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20`; `MyTradingSys/research/BUGS.md:264`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Mainnet Confirmation Guard**: Interactive confirmation and `--mainnet` command-line flag required; testnet default (`SOURCED`, quote: mainnet requires explicit `--mainnet` flag AND typed confirmation in `MyTradingSys/execution/MAINNET_READINESS_CHECKLIST.md (line not re-verified)`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]

### Backtests
1. **Architecture Status Overview (2026-10-26)** [`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20`]:
   - **Path**: `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20`
   - **Fee-Net**: Evaluated via operational logs and testnet ledger; no standalone strategy backtest row exists (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20` "no backtest row").
   - **IS / OOS Partition**: NOT_IN_DATA (infrastructure component; partitions apply to strategy backtests that consume its data).
   - **Sample Size (n)**: Feeds all 19 kline live layers (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:16`).
2. **Deribit Testnet Live Execution Sample (2026-10-09)** [`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:26-28`]:
   - **Path**: `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:26-28`
   - **Fee-Net**: Fee-net evaluated with live testnet order fills and exchange fees (`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:26-28`).
   - **Sample Size (n)**: 372 total testnet trades recorded; 300 generated by `turn_of_candle` (net -3.69 USD, 100% time exits); 72 across all remaining layers (`MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:28`).
3. **Time Exit Domination Diagnostic T085 (2026-10-09)** [`MyTradingSys/research/BUGS.md:181`]:
   - **Path**: `MyTradingSys/research/BUGS.md:181`
   - **Fee-Net**: Evaluated on live execution trade journal (`MyTradingSys/research/BUGS.md:181`).
   - **Sample Size (n)**: 94% to 97% of all live testnet trades exit via time-out rather than hitting stop or target (`MyTradingSys/research/BUGS.md:181` [T085]; `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:39`).
4. **Kline Fires Parity Replay FIRES-B1 (2026-10-09)** [`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-85`]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-85`
   - **Fee-Net**: Parity audit comparing offline kline fire generation against live alert logs (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:12,16`).
   - **Sample Size (n)**: 244,543 total fires; parity PASS on spot rerun (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:12,20-40`).
5. **Empirical Screenshot Tape Read Corpus (2026-10-26)** [`MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md:24,53`]:
   - **Path**: MyTradingSys/research/screenshots/ (MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md:24,53)
   - **Sample Size (n)**: 27 documented markdown evaluations + 2 subdirectories = 29 items (`MyTradingSys/research/gpt_rederive_2026-10-26/layer_rederive/live_engine.md:24,53`).

### Bugs and assumptions
- **Ruling B075**: "Historical mode unfit for backtesting; zeroes trade_flow/book_imbalance/funding/OI, produces hollow snapshots" (`MyTradingSys/research/BUGS.md:160`). Closed 2026-09-27.
- **Ruling B081**: Live runner crashes on unhandled connection reset in Deribit ws thread; auto-reconnect unhandled (`MyTradingSys/research/BUGS.md:241`). Closed 2026-10-01. [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Ruling B116**: "Unsourced 0.1 percent minimum stop floor and 0.2 percent fallback stop are still live in code" (`MyTradingSys/research/BUGS.md:227`). Closed 2026-10-04.
- **Ruling B117**: "Unsourced proof bands 3 and 5 gate WAIT_PROOF, WATCH and SETUP_FORMING in start-trading logic" (`MyTradingSys/research/BUGS.md:228`). Open.
- **Ruling B118**: "Layer bracket in auto_trader.py is a fixed unsourced stop_pct 1.0, targets 2, size 20" (`MyTradingSys/research/BUGS.md:229`). Closed 2026-10-04.
- **Ruling B136**: Live execution logs show time exit domination (97% time exits; targets/stops almost never reached) (`MyTradingSys/research/BUGS.md:187`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Task T085**: 97% of testnet trades end on the time exit: find why targets/stops are almost never reached (unreachable brackets on short horizons) (`MyTradingSys/research/BUGS.md:187`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
- **Operational State HALT**: "Testnet HALT since 2026-10-12 09:46Z (executor fail_closed); supervisor clears it" (`MyTradingSys/system/LAYERS.md:195`; `MyTradingSys/system/layer_index.json:532`).

### Confluence
- **Infrastructure Backbone Role**: Ingestion, execution, and dispatch pipeline that feeds every layer (`MyTradingSys/system/layer_index.json:20`; `MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:20`).
- **Promoted Setups Status**: `promoted_setups.json` holds 0 entries (`entries: []`), confirming no strategy layer has been promoted to automated mainnet execution (`MyTradingSys/execution/promoted_setups.json:2-3`).
- **Actual Live Confluence**: Zero live trades combined (Nothing combines on a live trade. `promoted_setups.json` ships empty... So no confluence rule has ever decided a real trade in `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`). [UNVERIFIED: wording not found verbatim in the cited file (Gemini input)]
