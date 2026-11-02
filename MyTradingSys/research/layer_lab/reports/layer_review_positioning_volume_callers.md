# Layer review fact sheet: families positioning, volume_candles_ma, callers

Built 2026-11-02 from the repo only. Starting point: `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/positioning.md, volume_candles_ma.md, callers.md` (Gemini input, reviewed in `MyTradingSys/research/layer_lab/reports/2026-10-26_gemini-facts-review.md`); every file:line below was re-resolved against this tree by searching the cited file for the quoted text or the number on the line (the Gemini line numbers had drifted). No verdict wording on any layer (operator NO 2026-10-25, `MyTradingSys/research/mts_doctor/MAINNET_PATH_2026-10-25.md:34`). Numbers are copied with their file:line, never recomputed. Labels: SOURCED = a trader quote or paper is given; OURS = our choice, no trader quote found; NO-SOURCE = repo says so itself; NOT_IN_DATA = the repo is silent. Status words such as "closed" or "DEAD" appear only inside quotes of repo files.

## funding_cvd_fade

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md` lists "funding fade" as "Small adapter, low value"; no `studies/` file exists for it.

### Idea and source
- **Literature Source**: "Memon 2026 (funding-extreme reversion, tier T2, relayed by four AI replies) plus a CVD/price divergence (T055a H2), not from any trader: backtest/layers/FORMULAS.md:356-370 and funding_cvd_fade.py:1-9" (`MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:10`).
- **Specification Quote**: "candidate C1. Funding-extreme mean reversion (T2, Memon 2026, 7y Binance, via research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md; that source does NOT give the percentile threshold, so `hi`/`lo`/`lookback` are UNDEFINED in source and are grid parameters) merged with a CVD/price divergence fade (T055a H2). It is an independent layer, never a filter on the Tom core. Signals fade the crowded side: extreme high funding -> short, extreme low funding -> long." (`MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:1-8`).
- **Formula Specification Quote**: "Sources: funding-extreme reversion T2, Memon 2026 (7y Binance) via `research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md` (the percentile threshold is NOT given there: UNDEFINED in source, so it is a grid parameter); mechanism He/Manela/Ross/von Wachter arXiv 2212.06888 (T2); CVD/price divergence = same CVD as `bt_data.cvd_delta` (section above, `delta = 2*tbv - v`, running sum). Merge decision: supervisor 2026-09-29 (T055a H2 + T055b funding-extreme)." (`MyTradingSys/backtest/layers/FORMULAS.md:365-368`).
- **Trader Association Finding**: "Finding that frames everything: the tested layer is not a FlowHorse layer" (`MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:7`).
- **FlowHorse Grep Evidence**: "The three processed FlowHorse extracts contain zero mentions of funding, open interest or liquidation (grep of extracts/processed/flowhorse/*.md: 0/0/0). The rulebook counts FlowHorse rows built as layers: 0 of 32 (research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md:121)." (`MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:11`).
- **Whale Evidence Evaluation**: "Whale signals are coincident or lagged, not leading" (`MyTradingSys/research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md:19`); "DO NOT add whale-tracking DSA field (Rule 33: no T1/T2 evidence)." (`MyTradingSys/research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md:46`).
- **Trade Ledger / Ground Truth**: NOT_IN_DATA ("NOT_IN_DATA. There is no FlowHorse trade ledger and no dated call list... For C1 no trader exists, so a ledger cannot exist" in `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:33-34`).

### Parameters
- **Market**: Binance USDT-M BTCUSDT perpetual (`SOURCED`, quote: "Binance USDT-M perp" in `MyTradingSys/backtest/layers/FORMULAS.md:352`).
- **Execution / Taker Fee**: 10 bps round trip (0.0010) (`SOURCED`, quote: "taker fee 10 bps round trip (0.0010)" in `MyTradingSys/backtest/layers/FORMULAS.md:352`).
- **Slippage**: 2 bps round trip (0.0002) (`OURS`, quote: "realistic slippage added as `slip_rt` (default 0.0002 = 2 bps RT; source: internal fee floor in T055b 'SCALPING FEE FLOOR', internal arithmetic)" in `MyTradingSys/backtest/layers/FORMULAS.md:353`).
- **Funding Cashflow Accounting**: Binance perpetual funding convention (`SOURCED`, quote: "Funding: a position pays `side_sign * rate` (as a fraction of notional, entry notional used) for every funding record with `t_in < calc_time <= t_out`; `side_sign` = +1 long, -1 short, so longs pay positive rates and shorts receive them (Binance perpetual funding convention)" in `MyTradingSys/backtest/layers/FORMULAS.md:354`).
- **Funding Lookback Window**: 90 records default, 60/90/180 grid (`OURS`, quote: "Defaults (all UNDEFINED in source, grid-searched IS only): lookback 90 records, n 20, hi 0.95, lo 0.05" in `MyTradingSys/backtest/layers/FORMULAS.md:376`; grid `for lb in (60, 90, 180)` in `MyTradingSys/backtest/layers/run_t055.py:67`). STALE: the 09-29 run IS-chose "lookback 180, n 50, hi .99, lo .01, use_divergence true, horizon 48" (`MyTradingSys/system/layer_map.json:854`) and is marked "invalid, replaced" (`MyTradingSys/system/layer_map.json:858`); the valid rerun IS-chose lookback 90, n 50, hi 0.95, lo 0.05, horizon 48 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:29`).
- **CVD Divergence Lookback (n)**: 20 default, 20/50 grid (`OURS`, quote: "lookback 90 records, n 20, hi 0.95, lo 0.05" in `MyTradingSys/backtest/layers/FORMULAS.md:376`; "n 50" in `MyTradingSys/system/layer_map.json:836`).
- **Funding Percentile Thresholds (hi / lo)**: 0.95 / 0.05 default; 0.90 / 0.10 and 0.99 / 0.01 grid (`OURS`, quote: "lookback 90 records, n 20, hi 0.95, lo 0.05" in `MyTradingSys/backtest/layers/FORMULAS.md:376`; grid `for hi, lo in ((0.90, 0.10), (0.95, 0.05), (0.99, 0.01))` in `MyTradingSys/backtest/layers/run_t055.py:68`).
- **Use Divergence Switch**: true / false (`OURS`, quote: "use_divergence: bool = True" in `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:71`; grid `for ud in (True, False)` in `MyTradingSys/backtest/layers/run_t055.py:68`).
- **Holding Horizon**: 48 bars (12h on 15m) (`OURS`, quote: "C1 is a pure time-exit strategy holding 48 15m bars (12.0 hours)" in `MyTradingSys/research/positioning_c1_2026-10/PRE_REG_POSITIONING_C1.md:13`; grid horizons (4, 16, 48) in `MyTradingSys/backtest/layers/run_t055.py:87`; layer_map horizon (bars) value 48 in `MyTradingSys/system/layer_map.json:419-422`).

### Backtests
1. **Initial T055-C1 Run (2026-09-29)** [SUPERSEDED: "09-29 run had 12 months of funding only; invalid, replaced" in `MyTradingSys/system/layer_map.json:858`; "Data: funding exists 2025-09 on only." in `MyTradingSys/backtest/layers/FORMULAS.md:377`]:
   - **Path**: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:1-54`
   - **Fee-Net**: Fee-net evaluated (fee 10 bps RT + slip 2 bps RT + funding included; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:5`).
   - **IS / OOS Partition**: Single 70/30 split; 37536 15m bars (IS 26275 / OOS 11261; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:5`; "70/30 single split; 2 OOS years" in `MyTradingSys/system/layer_map.json:855`).
   - **Sample Size (n)**: IS n = 36 events, gross mean +0.7677%, net mean +0.6573%, net Sharpe 0.5433 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:11`); OOS n = 151 events, gross mean -0.2834%, net mean -0.3992%, net Sharpe -0.2035 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:12`).
   - **Alt 1h Run**: IS n = 21, net mean +2.0550%; OOS n = 43, gross mean +0.6085%, net mean +0.5031%, net Sharpe 0.1665 (< 0.3 FAIL mark) (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:50-51`).
2. **Corrected T055-C1 Rerun with Full Funding (2026-10-07)**:
   - **Path**: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:1-66`
   - **Fee-Net**: Fee-net evaluated (fee 10 bps RT + slip 2 bps RT + funding included, `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:27`; funding from all 7305 records, 2020-01..2026-08, `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:6`).
   - **IS / OOS Partition**: Single 70/30 split; 35008 15m bars clipped to funding coverage (IS 24505 / OOS 10503; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:27`; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:8`).
   - **Sample Size (n)**: IS n = 129 events, gross mean +0.5244%, net mean +0.4113%, net Sharpe 0.2736 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:33`); OOS n = 76 events, gross mean +0.0650%, net mean -0.0453%, net Sharpe -0.0346 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:34`).

### Bugs and assumptions
- **Ruling B103**: "Backtest funding cost is silently 0 outside the locally loaded funding range; local fundingRate holds 2025-09..2026-08 while the Binance archive has BTCUSDT 8h funding from 2020-01" (`python scripts/dev/lab_query.py rulings positioning`; `MyTradingSys/research/BUGS.md:213`). Closed 2026-10-04.
- **Data Truncation / Out-of-Bounds Crash**: Rerun crashed with ValueError in `trade_costs.funding_paid` when bars extended beyond funding history (fixed in test/driver by clipping bars to funding range; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:7-8`).
- **Live vs Backtest Timeframe Discrepancy**: "Funding/CVD tested on 15m, live on 1h, 0 of 34 coincide | BUG (timeframe) | LAYER_REALITY:17 | card positioning-c1 raw" (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:42`; `MyTradingSys/research/mts_doctor/LAYER_REALITY_2026-10-25.md:17`).
- **Live Exit Assumption**: "94% of live exits are time exits; the 1%/2%/8-bar bracket was never backtested, so live and tested numbers are not comparable for any layer" (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:39`).

### Confluence
- **Design Intention**: Independent standalone layer; never designed as a core filter (`MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:5`).
- **Merge Decision**: "Merge decision: supervisor 2026-09-29 (T055a H2 + T055b funding-extreme)" (`MyTradingSys/backtest/layers/FORMULAS.md:368`).
- **Live Wiring Role**: Listed (Lead draft, OURS) among families that could fill the CONTEXT slot; none passed S3 (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:13,30`).
- **Actual Live Trades Combined**: Zero real trades combined: "Nothing combines on a live trade." and "So no confluence rule has ever decided a real trade." (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

## oi_delta

Wired in the simulator: no. No `studies/` file; `MyTradingSys/research/sim_desk/PLUGIN.md` does not name oi_delta (NOT_IN_DATA).

### Idea and source
- **Origin Specification**: Four-state open-interest classifier; no named trader or paper (NOT_IN_DATA). The repo handoff lists "Source: BackQuant, TradingView scripts (OI Delta 4-state classification)" (`MyTradingSys/research/_archive/loose_2026-10/INDICATOR_IMPLEMENTATION_HANDOFF.md:58`) and calls the definitions "documented practitioner conventions, not exchange-defined ground truth", tier T3 (`MyTradingSys/research/fast_track_2026-09-27/T055a_POSITIONING_FLOW.md:45-46`).
- **Two Competing Schools**:
  - Volume-delta school: "delta_state (volume-delta school): sign of trade_flow.net_delta_1h" (`MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:5`).
  - Price school: "delta_state_price (price school): current_price[now] minus current_price[nearest snapshot at or before T-60m]" (`MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:6`).
- **Trader Ground Truth / Ledger**: NOT_IN_DATA (descriptive classifier; no dated trader call ledger exists; `MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:60`).

### Parameters
- **Classifier Input School**: choice between `volume-delta (net_delta_1h sign)` and `price (T-60m)` (`OURS`, quote: "volume-delta (net_delta_1h sign)" in `MyTradingSys/system/layer_map.json:623-627`; definitions "sign of trade_flow.net_delta_1h" and "current_price[nearest snapshot at or before T-60m]" in `MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:5-6`).
- **Forward Measurement Horizons**: 30m, 60m, 120m (`OURS`, quote: "Horizons: 30m, 60m, 120m" in `MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:9`).
- **Observation Window**: 60-minute delta window (`OURS`, quote: "delta_state_price (price school): current_price[now] minus current_price[nearest snapshot at or before T-60m]" in `MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:6`).
- **Four Categorical States**: aggressive_long, aggressive_short, rekt_long, rekt_short, plus neutral (origin NOT_IN_DATA; states as defined in `MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:11-12`).

### Backtests
1. **OI Delta 4-State Backtest (2026-09-21)**:
   - **Path**: `MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:1-62`
   - **Fee-Net**: Not fee-net; gross forward return % with day-clustered standard errors (`MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:14,56-62; MyTradingSys/system/layer_map.json:1042`).
   - **IS / OOS Partition**: None (descriptive study over single snapshot window 2026-09-13 to 2026-09-22; `MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:58`).
   - **Sample Size (n)**: 6362 joined snapshot rows (`MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:8`); each state row spans 8 days, day-clustered SE (`MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:20`).
2. **OI Divergence Event Study (2026-10-10)**:
   - **Path**: `MyTradingSys/research/_archive/loose_2026-10/OI_EVENT_STUDY_2026-10-10.md:1-35`
   - **Fee-Net**: Not fee-net; raw and abnormal forward returns minus unconditional mean (`MyTradingSys/research/_archive/loose_2026-10/OI_EVENT_STUDY_2026-10-10.md:6-10`).
   - **IS / OOS Partition**: None; snapshot window 2026-09-12 to 2026-10-10 (~28 days; `MyTradingSys/research/_archive/loose_2026-10/OI_EVENT_STUDY_2026-10-10.md:30`).
   - **Sample Size (n)**: bearish_div n = 66 events (17 days); bullish_div n = 48 events (15 days) (`MyTradingSys/research/_archive/loose_2026-10/OI_EVENT_STUDY_2026-10-10.md:12-26`).
3. **OI Divergence v2 Pre-Registered Backtest (2026-10-10)**:
   - **Path**: `MyTradingSys/research/_archive/loose_2026-10/OI_DIVERGENCE_V2_2026-10-10.md:1-54`
   - **Fee-Net**: Fee-net evaluated (fees 10 bps RT, slippage 2 bps RT, funding from records; `MyTradingSys/research/_archive/loose_2026-10/OI_DIVERGENCE_V2_2026-10-10.md:4`).
   - **IS / OOS Partition**: 3 walk-forward folds (train / test) with 96-bar embargo (`MyTradingSys/research/_archive/loose_2026-10/OI_DIVERGENCE_V2_2026-10-10.md:5,44-54`).
   - **Sample Size (n)**: 2350 total events; pooled long n = 1071, pooled short n = 1279 at horizons 4, 8, 16 bars (`MyTradingSys/research/_archive/loose_2026-10/OI_DIVERGENCE_V2_2026-10-10.md:8`; `MyTradingSys/research/_archive/loose_2026-10/OI_DIVERGENCE_V2_2026-10-10.md:14-19`).
4. **Price vs CVD Divergence with OI Split (2026-10-14, Rerun 2026-10-17)**:
   - **Path**: `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:1-61`
   - **Fee-Net**: Fee-net evaluated (taker fee 0.05% per side = 0.10% RT; funding unmodeled; `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:10,39-46`).
   - **IS / OOS Partition**: DEV 2022-2024 / VAL 2025 / HOLDOUT 2026 (OI split available only 2025-09+; `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:49`).
   - **Sample Size (n)**: S1 (1m) 4933 long / 5434 short DIV events (CONTROL: 10921 long / 11143 short); S5 (5m) 1411 long / 1858 short DIV events (CONTROL: 5147 long / 5447 short) (`MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:43-46`).

### Bugs and assumptions
- **Ruling B103**: Funding cost silently 0 outside locally loaded range (`python scripts/dev/lab_query.py rulings positioning`; `MyTradingSys/research/BUGS.md:213`).
- **Historical Data Availability Gap**: Historical DEV OI data (2022-01..2024-06) does not exist in repo; OI series begins 2025-09-01 (`MyTradingSys/system/tasks/archive/gptb-oi-delta-event-table.json:17`; `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:1`).
- **Short Window Sample Clustering**: Initial study clustered over 8-9 calendar days; samples cluster on few days, so standard errors are day-clustered (`MyTradingSys/research/_archive/loose_2026-10/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:58-61`).
- **Data Contamination in 2026-10-14 DEV Split**: "study.py split_of() is year-based (DEV = year <= 2024), so DEV includes 2024-07..12 (own copy, not fires_kline)" (`MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:3`). Corrected in 2026-10-17 DEV rerun (`MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:1`).

### Confluence
- **Design Intention**: Not stated. `htf_context_live.py` returns `oi_delta_1h_pct` as one field of its context dict (`MyTradingSys/backtest/layers/fabio/htf_context_live.py:2`; `MyTradingSys/backtest/layers/fabio/htf_context_live.py:104`); layer status: "T055 C1 FAIL; OI/long-short unused as filters." (`MyTradingSys/system/layer_index.json:358`).
- **Intended Interaction**: NOT_IN_DATA (no declared confluence role for the 4-state oi_delta layer).
- **Confirmed By / Tested With**: Evaluated as an interaction split with price/CVD divergence (`MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:5-10,49`).
- **Live Status**: Unused as an active filter on live trades (`MyTradingSys/system/LAYERS.md:122`).

## volume

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md:46` lists "Detectors and studies (volume, candle patterns, guidance matrix, callers)" as **Does not fit**: "They flag events but are not trading rules, so there are no trades to simulate."

### Idea and source

- Operator ask and method (session note): research what the phrase "volume cannot be hidden" gives MTS for mid/long-term BTC trades; protocol is pre-register, DEV / VALIDATION / sealed HOLDOUT, 14 bp costs plus funding (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:3`).
- Source label: the pre-registration says the phrase is not in the trader corpus and tags every number "NO-SOURCE-TRADER, EVIDENCE-ONLY" (`MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:13`).
- Report finding 1: "No volume rule we tested is a validated directional edge on BTC." (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:9`).
- Report finding 2: "Volume is not hidden, but what it reveals is intensity, not direction." (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:12`).
- Trader ledger: NOT_IN_DATA (no trader behind this layer; literature tiers T1-T3 are in the report table, `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:35`).

### Parameters

- Round-trip cost 14 bps (taker 5 bps + 2 bps slippage per side) and funding paid inside the hold: OURS (repo fee model), `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:28`.
- Windows: DEV = bar open before 2024-07-01; VALIDATION 2024-07-01 to 2025-06-30; HOLDOUT 2025-07-01 to 2026-09-30, sealed. OURS (protocol), `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:23`.
- Timeframes: 1d and 4h primary, 1h only for the descriptive time map: OURS, `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:24`.
- Event families: 36 events, definitions fixed, thresholds not tuned: OURS / NO-SOURCE-TRADER, `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:44`.
- Entry and exit timing: entry open(i+1), exit open(i+1+h): OURS, `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:28`.
- Time-adjusted relative volume (RVadj) as the core measure, added at the operator's request: OURS, `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:28`.
- Triage rule (N >= minimum, net mean > 0 with bootstrap CI lower bound > 0, Reality-Check p_adj < 0.10): OURS, `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:82`.
- V3 frozen candidate R40D_N: 4h, h=6, reversal (long after RSI(14) crosses down through 40 on RVadj < 1.5): OURS, `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:5`.

### Backtests

All rows are fee-net (14 bp plus funding); DEV 2020-01-01 to 2024-06-30, VALIDATION 2024-07-01 to 2025-06-30; HOLDOUT never opened (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:11`).

- Overall, `MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md`: 553 pre-registered trials, 1 marginal pass that failed VALIDATION at net -2 bp on 50 events vs +70 bp on DEV (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:9`).
- V1 event study, 1d, DEV (in-sample), `MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md`: 1472 bars, 216 trials (96 live, 120 INSUFFICIENT-N), 0 pass triage (`MyTradingSys/research/volume_2026-10-09/V1_DEV_RESULTS.md:5`).
- V2 state family, 1d, DEV (in-sample), `MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md`: 1272 bars, 96 trials (84 live, 12 INSUFFICIENT-N), 0 pass triage (`MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:3`).
- V3 validation (out of sample, run once), `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md`: R40D_N n=50, net -2 bp [-68, +64], registered min n 100 not met (`MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:11`).
- V4 confirmation premium, 4h h=18, `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md`: DEV (descriptive prior) VCP +88 bp, p=0.008; VALIDATION confirmed n=286, unconfirmed n=286, VCP -13 bp [-109, +81], p=0.597 (`MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:8`).

### Bugs and assumptions

- Bug rows for this layer in `MyTradingSys/research/BUGS.md`: NOT_IN_DATA (none found for the volume layer).
- Report-recorded limit: with 50-300 events only effects larger than roughly 60-170 bp (4h) or 100-550 bp (daily) are detectable (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:19`).
- Report-recorded time bias: plain relative volume is partly a clock (`MyTradingSys/research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:15`).
- Overlap: a state lasts many days so effective independent n is far below n (`MyTradingSys/research/volume_2026-10-09/V2_DEV_RESULTS.md:4`).

### Confluence

- Tested role: whether volume confirms breakouts and RSI 40/60 crosses (V4 pools BB-squeeze, Donchian-20 and RSI(14) cross pairs; `MyTradingSys/research/volume_2026-10-09/V4_RESULTS.md:3`).
- Live confluence: "Nothing combines on a live trade" (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).


## candle_patterns

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md:46` lists "Detectors and studies (volume, candle patterns, guidance matrix, callers)" as **Does not fit**: "They flag events but are not trading rules, so there are no trades to simulate."

### Idea and source
- **Classical Literature / Source**: Standard Bulkowski / Morris / Nison candlestick patterns (18 classical patterns across reversal and continuation) (`MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:1-18`).
- **Operator Hypothesis (P0)**: Operator formulation of engulfing patterns on daily BTC bars (`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:1-12`).
- **Candlestick Close Sequences**: Pre-registered close sequence study at higher-timeframe levels (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:1-15`).
- **Trader Association / Ledger**: NOT_IN_DATA (classical chartist technical analysis taxonomy; no named individual trader and no dated call ledger exists).

### Parameters
- **Market**: Binance USDT-M BTCUSDT perp archive, UTC bars (`SOURCED`, quote: "Binance USDT-M BTCUSDT perp archive, UTC bars" in `MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:15`).
- **Pattern Definitions**: 18 classical directional candle patterns plus three volatility-state candles (`SOURCED`, quote: "18 classical directional candle patterns, or three volatility-state candles" in `MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:7`; "18 patterns x 3 horizons = 54 tests per timeframe" in `MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:55`). The pattern-name list is not restated here.
- **Timeframes**: 1d and 1h in P0/P1 ("two timeframes (1d, 1h)", `MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:55`); 4h in D19 (`MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:1`); 1m close sequences in `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:7` (`OURS`).
- **Holding Horizons**: h = 1, 3, 5 bars (`OURS`, quote: "Horizons h in {1,3,5} bars." in `MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:55`).
- **Fee Floor**: 14 bps round trip plus realised funding on 1d and 1h; the 10 bps figure of the removed claim was wrong (`OURS`, quote: "Costs: 14 bps round trip (5 bps fee + 2 bps slippage per side) plus realised funding." in `MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:19`; "Net = sign*fwd - 14 bps - sign*realised funding" in `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:3`); candle-close sequences: "fixed 14bp round-trip cost screen" in `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:11`.

### Backtests
1. **P0 Operator Engulfing Pilot (2026-10-04)** [`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:1-35`]:
   - **Path**: `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:1-35`
   - **Fee-Net**: Fee-net evaluated (10 bps RT taker fee; `MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:10`).
   - **IS / OOS Partition**: DEV 2022-01..2025-06 (`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:12`).
   - **Sample Size (n)**: P0a n = 571 events, win 35.7%, net -0.7 bp/trade, Sharpe -0.01; P0c n = 364 events, win 29.7%, net -8.1 bp/trade, Sharpe -0.14 (`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:16-20`). Verdict: no edge vs random null (`MyTradingSys/system/layer_map.json:1303`).
2. **P1 Classical Pattern Scan (2026-10-07)** [`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:1-50`]:
   - **Path**: `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:1-50`
   - **Fee-Net**: Fee-net evaluated (`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:10`).
   - **IS / OOS Partition**: 108 total cells across 18 patterns x 3 horizons on 1d and 1h (`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:12-15`).
   - **Sample Size (n)**: 0 of 108 cells pass triage (1d: 36 FAIL, 18 INSUFFICIENT-N; 1h: 48 FAIL, 6 INSUFFICIENT-N) (`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:18-26`). Verdict: 0 pass triage (`MyTradingSys/system/LAYERS.md:188`).
3. **D19 4h Engulfing Study (2026-10-04)** [`MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:1-40`]:
   - **Path**: `MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:1-40`
   - **Fee-Net**: Fee-net evaluated (`MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:8`).
   - **Sample Size (n)**: n = 192 events, win 0.380 / 0.375, net R 0.2255 / 0.1295 vs buy-and-hold 1.6072 (`MyTradingSys/research/candle_patterns_2026-10-04/D19_4H_RESULTS.md:8-9`). Verdict: "NO-SOURCE; below buy-and-hold" (`MyTradingSys/system/LAYERS.md:182`).
4. **Candle Close Sequence Study (2026-10-14)** [`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:1-45`]:
   - **Path**: `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:1-45`
   - **Fee-Net**: Fee-net evaluated against 14 bps round-trip hurdle (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:22`).
   - **IS / OOS Partition**: DEV 912 days, 1,313,280 1m bars (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:7`).
   - **Sample Size (n)**: 105,541 event rows across 126 arms (59 to 1,761 per arm); every pooled arm negative after costs (-26.83 to -4.68 bp/event); 0 pass (`MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:11`). Verdict: EXPLORATORY NEGATIVE (`MyTradingSys/system/layer_map.json:1395`).

### Bugs and assumptions
- **Low Base-Rate Friction**: Classical candle patterns occur at frequencies too low to sustain edge after taker fees and slippage on crypto markets (`MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:30-34`).
- **Asymmetric Win-Loss Distribution**: Engulfing patterns on BTC suffer lower win rate (29-38%) with average losses exceeding average gains (`MyTradingSys/research/candle_patterns_2026-10-04/P0_RESULTS.md:22-26`).

### Confluence
- **Intended Role**: Trigger or confirmation layer for structure reversals (`MyTradingSys/research/candle_patterns_2026-10-04/CANDLE_PATTERNS_RESEARCH_2026-10-04.md:14`).
- **Integration Classification**: Classed as DEAD in layer review (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`).
- **Actual Live Confluence**: Zero live trades combined (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

## ma_daily

Wired in the simulator: no. No `studies/` file; `MyTradingSys/research/sim_desk/PLUGIN.md` does not name ma_daily (NOT_IN_DATA).

### Idea and source
- **Origin / Prompt Source**: Chatbot handoff pasted by operator: "operator pasted a 'Setup Alpha / Setup Beta' BTC perp handoff (daily SMA200 trend engine + 15m/1h liquidity sweep with CVD absorption and 5m MSS entry)" (`MyTradingSys/research/BUGS.md:276` [Ruling B163]); "NO-SOURCE: the setup numbers come from a chatbot handoff, not a trader transcript." (`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:4`).
- **Ruling B163 Quote**: "operator pasted a 'Setup Alpha / Setup Beta' BTC perp handoff (daily SMA200 trend engine + 15m/1h liquidity sweep with CVD absorption and 5m MSS entry)" (`MyTradingSys/research/BUGS.md:276`).
- **Implementation Specification**: Setup Alpha long entry: "Daily Close > SMA(200) AND Daily Close > EMA(7) AND RSI(2) > ADX(2)" (`MyTradingSys/research/BUGS.md:276`); coded as close > s200 and close > e7 and r2 > d2 (`MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:163`). Setup Beta: "Liquidity sweep + CVD absorption event study, Binance BTCUSDT perp, 15m levels / 5m entry." (`MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:3`; code `MyTradingSys/research/setup_alpha_beta_2026-10-10/beta_sweep.py:76-99`; the removed `beta_backtest.py` cite named a file that is not on trunk).
- **Trader Association / Ledger**: NOT_IN_DATA ("NO-SOURCE (chatbot handoff numbers)" in `MyTradingSys/system/LAYERS.md:167`; no named human trader and no verified trade ledger exists).

### Parameters
- **Market**: Binance BTCUSDT 1d, fee 0.05% per side plus funding (`OURS` / `NO-SOURCE`, quote: "Daily long-flat SMA200 variants, Binance BTCUSDT 1d, fee 0.05% per side + funding." in `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:3`).
- **Trend MA**: SMA 200-period (`OURS` / `NO-SOURCE`, variant name "A: SMA200+EMA7+RSI2>ADX2" in `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:8`; `s200 = sma(c, 200)` in `MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:154`).
- **Fast MA**: EMA 7-period (`OURS` / `NO-SOURCE`, variant name "A: SMA200+EMA7+RSI2>ADX2" in `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:8`; `e7 = ema(c, 7)` in `MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:154`).
- **Oscillator Filter**: RSI 2-period > ADX 2-period (`OURS` / `NO-SOURCE`; `r2 = rsi(c, 2); d2 = adx(bars, 2)` in `MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:155`; condition `r2[i] > d2[i]` in `MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:163`).
- **Long-Flat Rule**: Variant A is long when close > SMA200 and close > EMA7 and RSI2 > ADX2 (`OURS` / `NO-SOURCE`, `MyTradingSys/research/setup_alpha_beta_2026-10-10/alpha_backtest.py:163`; "Daily long-flat SMA200 variants" in `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:3`). The removed claim "EMA7 > SMA200" was not in the code.
- **Beta CVD Threshold**: CVD is a kline taker-buy proxy: "CVD = kline taker-buy volume proxy (T5_CVD_DEFINITION_2026-10-01.md)" (`OURS` / `NO-SOURCE`, `MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:4`; `cvd += (b["tb"]*2 - b["v"])` in `MyTradingSys/research/setup_alpha_beta_2026-10-10/beta_sweep.py:20`). No numeric threshold is stated in the cited files.

### Backtests
1. **Setup Alpha Backtest (2026-10-10)** [`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:1-55`]:
   - **Path**: `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:1-55`
   - **Fee-Net**: Fee-net evaluated (fee 0.05% per side plus funding; `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:3`).
   - **IS / OOS Partition**: claim removed (no cite verifiable on trunk).
   - **Sample Size (n)**: n = 42 trades, CAGR 20.53%, max drawdown 49.41% vs buy-and-hold CAGR 43.83% and maxDD 76.67% (`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:8`; `MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:11`). Verdict NO-SOURCE (`MyTradingSys/research/setup_alpha_beta_2026-10-10/ALPHA_RESULTS.md:1`; `MyTradingSys/system/LAYERS.md:170`).
2. **Setup Beta CVD Liquidity Sweep Backtest (2026-10-10)** [`MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:1-48`]:
   - **Path**: `MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:1-48`
   - **Fee-Net**: Evaluated fee-net (`MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:10`).
   - **Sample Size (n)**: All sessions no CVD n = 708,240, avg R -0.030; all sessions CVD n = 628,978, avg R -0.024; uniformly negative across London, NY, and all sessions (`MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:10`). Verdict: uniformly negative net returns (`MyTradingSys/research/setup_alpha_beta_2026-10-10/BETA_RESULTS.md:10`).

### Bugs and assumptions
- **Ruling B163**: "operator pasted a 'Setup Alpha / Setup Beta' BTC perp handoff (daily SMA200 trend engine + 15m/1h liquidity sweep with CVD absorption and 5m MSS entry)"; "the text is a chatbot summary, not a trader we follow" (`MyTradingSys/research/BUGS.md:276`).
- **Cherry-Picked Parameters**: claim removed (no cite verifiable on trunk).

### Confluence
- **Intended Role**: CONTEXT trend-regime filter (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:15,30`).
- **Integration Classification**: Classed as DEAD in layer review (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`).
- **Actual Live Confluence**: Zero live trades combined (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

## bigtrade_fires

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md` lists big-trade fires as "Small adapter, low value".

### Idea and source
- **Engine Observation Layer Spec**: "fire history of the kline-only live layers" (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:5`); 19 live kline keys replayed over 2022-01-01 .. 2026-10-07, 244,543 fires (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:14`).
- **ATR Zigzag Ground Truth**: title "BIGMOVES REPORT (big-move ground truth, backtest A)" (`MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:1`); "Legs: ATR zigzag, r in [1.5, 2.0]" with leg size threshold k in [3, 5, 8] (`MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:29`).
- **Exit Policy Evaluation Framework**: "EXIT POLICIES REPORT (backtest C)" (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:5`); six policies, "under all six policies in both splits" (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:144`).
- **Trader Association / Ledger**: NOT_IN_DATA (internal benchmarking and execution simulation framework; no external trader exists).

### Parameters
- **Market**: Binance BTCUSDT 1m merged klines, 2022-01-01 to 2026-10-07 UTC (`SOURCED`, quote: "2507040 bars (= 1741 days x 1440), 0 gaps" in `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:7`).
- **Execution Cost Model**: 10.0 bp RT taker + 2.0 bp slippage = 12 bp round trip (`OURS`, quote: "Costs 10.0 bp RT taker + 2.0 bp slippage (assumed)" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:7`; "The assumed round-trip cost is 12 bp" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:144`).
- **Exit Policy 1 (Live-like)**: 1% stop / 2% target / 8 bars time exit (`OURS`, quote: "live_like_1pct_2pct_8bars" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:28`).
- **Exit Policy 2 (Bracket 1x/2x ATR)**: 1 ATR stop / 2 ATR target / 24 bars (`OURS`, quote: "bracket_1atr_2atr_24" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:30`).
- **Exit Policy 3 (Bracket 1.5x/3x ATR)**: 1.5 ATR stop / 3 ATR target / 24 bars (`OURS`, quote: "bracket_1.5atr_3atr_24" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:32`).
- **Exit Policy 4 (Time 24 + Wide Stop)**: 2 ATR stop / 24 bars time exit (`OURS`, quote: "time_24_wide_stop_2atr" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:34`).
- **Exit Policy 5 (Time 96 + Wide Stop)**: 2 ATR stop / 96 bars time exit (`OURS`, quote: "time_96_wide_stop_2atr" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:36`).
- **Exit Policy 6 (Trailing Stop)**: Breakeven at 1 ATR, trail 2 ATR, 96 bars (`OURS`, quote: "be1atr_trail2atr_96" in `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:38`).

### Backtests
1. **BIGMOVES-A Ground Truth Study (2026-10-09)** [`MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:1-50`]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:1-50`
   - **Fee-Net**: Descriptive structural benchmark (no fee model; `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:10`).
   - **Sample Size (n)**: ATR zigzag legs counted: 4h n = 1930; 1h n = 8173; 15m n = 33790; 5m n = 105235 (`MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:160`; `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:165`; `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:170`; `MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:175`). Verdict: "ground truth, no verdict" (`MyTradingSys/system/LAYERS.md:173`).
2. **FIRES-B1 Parity Replay (2026-10-09)** [`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-85`]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:1-85`
   - **Fee-Net**: Replay parity audit (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:12`).
   - **Sample Size (n)**: 244,543 total fires across 19 kline live layers (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:14`). "parity PASS on spot rerun" (`MyTradingSys/system/LAYERS.md:174`).
3. **BIGTRADE-EXIT Backtest C (2026-10-09)** [`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:1-147`]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:1-147`
   - **Fee-Net**: Fee-net evaluated under 6 exit policies against 12 bps cost (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:120-145`).
   - **IS / OOS Partition**: TRAIN 2022-01..2025-06 / VALIDATE 2025-07..2026-08 (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:120-135`).
   - **Sample Size (n)**: 114 cells evaluated; 1 of 114 positive in both splits (CryptoCred sr_flip 1h, +9.8 bp TRAIN, +0.1 bp VALIDATE, n 1,024 / 163); all other layers negative under every policy (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:138-145`). Verdict: no exit policy rescues the fires (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:143`).
4. **CAPTURE-MATRIX Analysis (2026-10-09)** [`MyTradingSys/research/bigtrade_2026-10-09/CAPTURE_MATRIX_SPOT.md:1-60`]:
   - **Path**: `MyTradingSys/research/bigtrade_2026-10-09/CAPTURE_MATRIX_SPOT.md:1-60`
   - **Sample Size (n)**: Evaluated layer fire lift over ATR moves; capture lift hovered near 1.0 (uninformative) (`MyTradingSys/research/bigtrade_2026-10-09/CAPTURE_MATRIX_SPOT.md:25-35`).

### Bugs and assumptions
- **Synthetic Fixture in Capture Matrix**: Tool fixture `SYNTHETIC` is an algorithmic test probe, not an actual layer signal (`MyTradingSys/system/LAYERS.md:183`).
- **Time Exit Misattribution**: 94-97% of testnet trades end on time exits; backtest C proves that changing to dynamic brackets or trailing stops does not convert negative gross drift into profit (`MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:144-145`).

### Confluence
- **Intended Role**: Cross-layer execution and benchmarking harness (`MyTradingSys/research/bigtrade_2026-10-09/BIGMOVES_REPORT.md:5-8`).
- **Integration Classification**: Classed as DEAD in layer review (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:33`).
- **Actual Live Confluence**: Zero live trades combined (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

## callers

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md:46` lists "Detectors and studies (volume, candle patterns, guidance matrix, callers)" as **Does not fit**: "They flag events but are not trading rules, so there are no trades to simulate."

### Idea and source

- **Analyst Benchmark (Habib / Qriptal)**:
  - Quoted source: *"There is new research on Imbalance trading that DSA did - We have a analyst from you tube who also posts on discord. Habib his name. Imbalance trader. Discord is setup with his chanel - we need the feed - he provides trades with entried andtargets - he trades candles on diff time frames with imbalnces on diff exchanges - so we need his layer!"* (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:9`)
  - Quoted source: *"Working! It is easy - just place trades that he says! and do see his past record - verify."* (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:11`)
  - Quoted source: *"qriptal.com (operator paste): 86 setups, 67.1% win rate, 49 W / 13 BE / 24 L, avg winner 3.99%, avg loser 0.63%. Self-reported; not verified."* (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:23-24`)
  - Quoted source: *Qriptal is an external signal to be scored, not a rule source. His 'imbalance' indicator is sold and undisclosed, so a rule built from it is REJECT tier (playbook Part I). His imbalance = small-body high-volume candle; it is not an FVG and not the order-book imbalance in research/imbalance_2026-10-10/RESEARCH.md* (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:18`)
- **Crypto Chase (@Crypto_Chase)**:
  - Quoted source: *Trading Style: Patient swing and intraday trader. Identifies HTF displacement imbalances, waits for price to retrace and fill the inefficiency, and enters on confirmation wicks or structural flips.* (SOURCED: `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:101`)
  - Quoted source: *Imbalance Construct: Fair Value Gaps (FVG), Liquidity Imbalances, S/R Deviations.* (SOURCED: `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:100`)
- **Roman Trading (@Roman_Trading)**:
  - Quoted source: *Imbalance Construct: Volume Anomaly / Absorption Imbalances & CVD Divergences (Virtually identical to Habib's Construct F).* (SOURCED: `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:119`)
  - Quoted source: *"Specializes in finding volume absorption candles at key horizontal support/resistance levels. When high volume enters at a swing low but price fails to break down (small body/long lower wick), he flags it as institutional absorption and executes reversal fades."* (SOURCED: `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:120`)
- **Justin Bennett (@JustinBennettfx / Daily Price Action)**:
  - Quoted source: *Methodology: Unmitigated Fair Value Gaps, Daily Price Action Breakouts & Retests.* (SOURCED: `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:215`)
  - Quoted source: *Posts daily free written market plans with explicit: Entry: Retest of unmitigated FVG or daily breakout level. Stop Loss: Logical structural invalidation level. Take Profit: Multiple tiers (TP1, TP2) based on opposing major liquidity pools.* (SOURCED: `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:217`)
- **RLinda (TradingView Top Author)**:
  - Quoted source: *Methodology: Price Action, False Breakouts, Key S/R Liquidity Traps.* (SOURCED: `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:248`)
  - Quoted source: *TradingView Play-Button Verification: Once published on TradingView, ideas cannot be edited or deleted. Anyone can press 'Play' to see the future price bars validate or invalidate the setup.* (SOURCED: `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:256`)


### Parameters

- **Trade Direction (`direction`)**: `LONG` or `SHORT` (SOURCED: `MyTradingSys/research/analysts/schema.py:19-21`)
- **Entry Price (`entry_price`)**: Numerical execution level; limit or trigger level directly stated by the caller (SOURCED: `MyTradingSys/research/analysts/schema.py:46-47`)
- **Stop Loss (`stop_loss`)**: Explicit structural invalidation price stated by the caller; mandatory non-null (SOURCED: `MyTradingSys/research/analysts/schema.py:48-49`)
- **Profit Targets (`targets`)**: List of one or more target prices (non-empty, each > 0) stated by the caller (SOURCED: `MyTradingSys/research/analysts/schema.py:59-63`)
- **Price Geometry Validation**:
  - For `LONG`: `stop_loss < entry_price < targets[0]` (OURS: `MyTradingSys/research/analysts/schema.py:65-68`)
  - For `SHORT`: `stop_loss > entry_price > targets[0]` (OURS: `MyTradingSys/research/analysts/schema.py:70-73`)
- **Taker Fee**: `0.05%` per side (`0.10%` round-trip) (SOURCED: `MyTradingSys/backtest/layers/FORMULAS.md:s17`; `MyTradingSys/research/analysts/score_analysts.py:16`)
- **Slippage**: `2 bps` (OURS: `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:359`)
- **Fill Window**: `24 hours` (`1440` minutes) from `published_utc`; unreached limits expire as `NOT_FILLED` (OURS: `MyTradingSys/research/analysts/score_analysts.py:28`; `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:30`)
- **Max Holding Period / Timeout Window**: `7 days` (`10080` minutes); unresolved positions close at market (OURS: `MyTradingSys/research/analysts/score_analysts.py:29`; `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:31`)
- **Bar Collision Resolution**: Stop is checked first inside every candle (OURS: `MyTradingSys/research/qriptal_2026-10-10/RULES.md:3` "All numbers OURS"; "Stop is checked first inside every candle" in `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:81-82`; same rule in `MyTradingSys/research/analysts/score_analysts.py:7`).
- **Target Exit Policy**: Primary metric exits 100% position at Target 1 (`target_1`) (OURS: `MyTradingSys/research/analysts/score_analysts.py:129-130`; `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:59`)
- **Statistical Power Thresholds**:
  - Alpha: `0.05` one-sided exact binomial (OURS: `MyTradingSys/research/qriptal_2026-10-10/score_calls.py:37`). Two orientations exist: `MyTradingSys/research/analysts/SCORECARD.md:11` uses H0 = 50% (power to detect a 67.1% claim); `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:38` uses H0 = his 67.1% claim, H1 = 50%.
  - Minimum sample for triage ($60.5\%$ power): `n = 30` resolved trades (OURS: `MyTradingSys/research/analysts/SCORECARD.md:18`; `MyTradingSys/research/analysts/ROADMAP.md:68`)
  - Minimum sample for promotion gate: `n = 56` first reaches 80% power: 81.0% (analysts SCORECARD) or 82.5% (qriptal SCORECARD) depending on orientation (OURS: `MyTradingSys/research/analysts/SCORECARD.md:19,22`; `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:48,51`)


### Backtests

- **Habib / Qriptal Kline Scorecard (card `qriptal-score-binance`)**:
  - Report path: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:1-74`
  - Fee-net: Evaluated at `0.05%` taker fee per side (`0.10%` round-trip) (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:34,59`)
  - In-sample / Out-of-sample: DEV window `2025-09-01` to `2026-06-25`; HOLDOUT window `2026-06-26` to `2026-09-26` (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:7-13`)
  - Trades count ($n$): Scored $n = 0$ (DEV rows: 11 total, 0 ELIGIBLE; HOLDOUT rows: 67 total, 2 ELIGIBLE left unscored due to holdout partition seal; Total 81 candidate statements) (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:3,9-13`)
  - Result: No scored trades in DEV; statistical power is $0\%$ at $n = 0$ (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:3,38`)
- **Mechanical Volume Anomaly Candle Study (Habib Construct F baseline)**:
  - Report path: `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md:1-95`
  - Fee-net: Fee drag `0.09` to `0.38 R`; net edge after fees is flat to negative (SOURCED: `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md:81-83`)
  - In-sample / Out-of-sample: 22 named historical candles evaluated on Binance klines (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:41`)
  - Trades count ($n$): 22 labelled volume anomaly candles (labels); the fade backtest event counts are in the thousands (e.g. 2011/375 at 30m, `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md:74-78`) (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:41`)
  - Result: Candle anomaly statistically above chance ($p = 0.003$), but pure mechanical fade has NO EDGE after fees (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:41`; `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:32`). Caveats: p = 0.003 is the k=3 Binance-perp cell only (spot p = 0.001, `MyTradingSys/research/imbalance_qriptal_2026-10-16/README.md:51`); the README calls the p-values rough (`:61`); labels sit in the holdout window (`:62`); windows 2024-07..2026-06-25 are not clean OOS (`:98-101`).
- **Multi-Provider Analysts Scorecard (RLinda, Justin Bennett, Crypto Chase, Roman Trading)**:
  - Report path: `MyTradingSys/research/analysts/SCORECARD.md:1-33`
  - Fee-net: Evaluated at `0.05%` per side (SOURCED: `MyTradingSys/research/analysts/SCORECARD.md:4`)
  - In-sample / Out-of-sample: NOT_IN_DATA (kline evaluation run pending real ledger ingestion; `SAMPLE_CALL_LEDGER.csv` maintained header-only per `MyTradingSys/research/analysts/ROADMAP.md:14`)
  - Trades count ($n$): $n = 0$ evaluated trades in canonical `SCORECARD.md` (SOURCED: `MyTradingSys/research/analysts/SCORECARD.md:8-9`; `MyTradingSys/research/analysts/ROADMAP.md:14-15`)


### Bugs and assumptions

- **Rulings Query**:
  - `python scripts/dev/lab_query.py rulings callers` returns 1 closed ruling:
    - `B190` (Opened `2026-10-16`, Closed, Severity `LOW`): *"MTS-Backup git children flash visible console windows under the vbs/Store python.exe launcher"* (SOURCED: `MyTradingSys/research/BUGS.md:303`). Keyword hit only (its text mentions "the git callers"); unrelated to this layer. Bug rows for the callers layer: NOT_IN_DATA.
- **Self-Reported Performance Assumptions**:
  - Qriptal claims `86 setups, 67.1% win rate, 49 W / 13 BE / 24 L, avg winner 3.99%, avg loser 0.63%` on `qriptal.com`: unverified and not backed by public entry/stop/target timestamps in repo data (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:23-24`; `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:28-34`)
  - Unstated whether claimed percentages represent raw price movements or unleveraged/leveraged account equity changes (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:34`)
- **Staged Ledger Sample Purge**:
  - 4 illustrative mock rows were initially included in `MyTradingSys/research/analysts/SAMPLE_CALL_LEDGER.csv` and subsequently removed in commit `e544506d` to prevent fabricated trades from polluting the scorecard (`NO ASSUMPTIONS, NO FABRICATIONS`) (SOURCED: `MyTradingSys/research/analysts/ROADMAP.md:14`)
- **Undisclosed Proprietary Indicators**:
  - Qriptal's imbalance indicator is "sold and undisclosed" (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:18`); "exact indicator not reproducible from public material, mechanical fade NO EDGE after fees" (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:41`)
- **Social Media Call Survivorship / Deletion Bias**:
  - Spoken livestreams and Twitter posts carry potential survivorship or unpriced stop risks; 7 Qriptal statements had entries and targets but omitted priced stops, requiring classification as `NO-SOURCE` / unscored (SOURCED: `MyTradingSys/research/qriptal_2026-10-10/SCORECARD.md:55`; `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md:30`)


### Confluence

- **Confirming Other Layers**:
  - External caller setups act as discretionary confluence over raw mechanical imbalance occurrences (such as volume anomalies, Fair Value Gaps, and order-book delta imbalances) (SOURCED: `MyTradingSys/research/analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md:17`)
- **Confirmed By Other Layers**:
  - Binance USD-M 1m klines (data input, not a confirming layer; no live layer confirms callers: NOT_IN_DATA): Every ingested signal is verified against historical 1m price bars for fill feasibility and strict stop-loss checking before targets (SOURCED: `MyTradingSys/research/analysts/score_analysts.py:114-135`)
  - Key HTF Horizontal Support / Resistance & Order Flow: Callers' entries rely on confluence with pre-planned horizontal levels, value-area rotations, and wick sweeps (SOURCED: `MyTradingSys/research/_archive/loose_2026-10/IMBALANCE_AND_FREE_SETUP_ANALYSTS_2026-10-18.md:120,120`)
  - Testnet Shadow Account Isolation: Intended to operate on isolated testnet subaccounts (`layer:callers:<analyst_id>`), confirmed by live engine risk limits and `fail_closed` guards (SOURCED: `MyTradingSys/items/B162_qriptal_signal_layer.md:32`; `MyTradingSys/research/analysts/ROADMAP.md:81-84`)
- **Inter-analyst Correlation**:
  - NOT_IN_DATA (cross-analyst directional agreement or simultaneous trigger matrix has not been backtested)
