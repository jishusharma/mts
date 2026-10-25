# Layer Fact Sheet: positioning

Facts compiled strictly from repository files per `MyTradingSys/system/ANTIGRAVITY_LAPTOP.md` item C and task `lf-positioning-gemini-facts`.
No verdicts on keeping, dropping, demoting, or parking any layer. Every fact line cites `file:line` or `NOT_IN_DATA`.
Layers covered: `funding_cvd_fade`, `oi_delta` (`MyTradingSys/system/LAYERS.md:124-125`).

---

## 1. funding_cvd_fade

### ORIGIN (Quoted Source)
- **Literature Source**: "Memon 2026 (funding-extreme reversion, tier T2, relayed by four AI replies) plus a CVD/price divergence (T055a H2), not from any trader: backtest/layers/FORMULAS.md:356-370 and funding_cvd_fade.py:1-9" (`MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:10`).
- **Specification Quote**: "candidate C1. Funding-extreme mean reversion (T2, Memon 2026, 7y Binance, via research/whale_positioning_evidence_2026-09-12.md; that source does NOT give the percentile threshold, so `hi`/`lo`/`lookback` are UNDEFINED in source and are grid parameters) merged with a CVD/price divergence fade (T055a H2). It is an independent layer, never a filter on the Tom core. Signals fade the crowded side: extreme high funding -> short, extreme low funding -> long." (`MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:1-8`).
- **Formula Specification Quote**: "Sources: funding-extreme reversion T2, Memon 2026 (7y Binance) via `research/whale_positioning_evidence_2026-09-12.md` (the percentile threshold is NOT given there: UNDEFINED in source, so it is a grid parameter); mechanism He/Manela/Ross/von Wachter arXiv 2212.06888 (T2); CVD/price divergence = same CVD as `bt_data.cvd_delta` (section above, `delta = 2*tbv - v`, running sum). Merge decision: supervisor 2026-09-29 (T055a H2 + T055b funding-extreme)." (`MyTradingSys/backtest/layers/FORMULAS.md:358-361`).
- **Trader Association Finding**: "Finding that frames everything: the tested layer is not a FlowHorse layer" (`MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:7`).
- **FlowHorse Grep Evidence**: "The three processed FlowHorse extracts contain zero mentions of funding, open interest or liquidation (grep of extracts/processed/flowhorse/*.md: 0/0/0). The rulebook counts FlowHorse rows built as layers: 0 of 32 (research/fast_track_2026-09-27/CROSS_TRADER_RULEBOOK.md:121)." (`MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:11`).
- **Whale Evidence Evaluation**: "Whale signals are coincident or lagged, not leading" (`MyTradingSys/research/whale_positioning_evidence_2026-09-12.md:19`); "DO NOT add whale-tracking DSA field (Rule 33: no T1/T2 evidence)." (`MyTradingSys/research/whale_positioning_evidence_2026-09-12.md:46`).
- **Trade Ledger / Ground Truth**: NOT_IN_DATA ("NOT_IN_DATA. There is no FlowHorse trade ledger and no dated call list... For C1 no trader exists, so a ledger cannot exist" in `MyTradingSys/research/tom_transfer_2026-10-11/HOME_FIT_AUDIT_POSITIONING.md:33-34`).

### PARAMETERS (SOURCED or OURS)
- **Market**: Binance USDT-M BTCUSDT perpetual (`SOURCED`, quote: "Binance USDT-M perp" in `MyTradingSys/backtest/layers/FORMULAS.md:345`).
- **Execution / Taker Fee**: 10 bps round trip (0.0010) (`SOURCED`, quote: "taker fee 10 bps round trip (0.0010)" in `MyTradingSys/backtest/layers/FORMULAS.md:345`).
- **Slippage**: 2 bps round trip (0.0002) (`OURS`, quote: "realistic slippage added as `slip_rt` (default 0.0002 = 2 bps RT; source: internal fee floor in T055b 'SCALPING FEE FLOOR', internal arithmetic)" in `MyTradingSys/backtest/layers/FORMULAS.md:345-347`).
- **Funding Cashflow Accounting**: Binance perpetual funding convention (`SOURCED`, quote: "Funding: a position pays `side_sign * rate` (as a fraction of notional, entry notional used) for every funding record with `t_in < calc_time <= t_out`; `side_sign` = +1 long, -1 short, so longs pay positive rates and shorts receive them (Binance perpetual funding convention)" in `MyTradingSys/backtest/layers/FORMULAS.md:347-349`).
- **Funding Lookback Window**: 90 records default, 60/90/180 grid (`OURS`, quote: "Defaults (all UNDEFINED in source, grid-searched IS only): lookback 90 records, n 20, hi 0.95, lo 0.05" in `MyTradingSys/backtest/layers/FORMULAS.md:369`; "lookback 180 (IS-chosen)" in `MyTradingSys/system/layer_map.json:590-593`).
- **CVD Divergence Lookback (n)**: 20 default, 20/50 grid (`OURS`, quote: "lookback 90 records, n 20, hi 0.95, lo 0.05" in `MyTradingSys/backtest/layers/FORMULAS.md:369`; "n 50" in `MyTradingSys/system/layer_map.json:597-600`).
- **Funding Percentile Thresholds (hi / lo)**: 0.95 / 0.05 default; 0.99 / 0.01 and 0.90 / 0.10 grid (`OURS`, quote: "hi 0.95, lo 0.05" in `MyTradingSys/backtest/layers/FORMULAS.md:369`; "hi / lo percentile 0.99 / 0.01" in `MyTradingSys/system/layer_map.json:604-607`).
- **Use Divergence Switch**: true / false (`OURS`, quote: "use_divergence: bool = True" in `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:71`; choice "true", "false" in `MyTradingSys/system/layer_map.json:610-613`).
- **Holding Horizon**: 48 bars (12h on 15m) (`OURS`, quote: "horizon (bars): 48" in `MyTradingSys/system/layer_map.json:617-620`; "C1 is a pure time-exit strategy holding 48 15m bars (12.0 hours) [OURS, COUNT_POWER.md:88-94]" in `MyTradingSys/research/positioning_c1_2026-10/PRE_REG_POSITIONING_C1.md:13`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **Initial T055-C1 Run (2026-09-29)**:
   - **Path**: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:1-54`
   - **Fee-Net**: Fee-net evaluated (fee 10 bps RT + slip 2 bps RT + funding included; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:5`).
   - **IS / OOS Partition**: Single 70/30 split; 37,536 15m bars (IS 26,275 / OOS 11,261; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:5`).
   - **Sample Size (n)**: IS n = 36 events, gross mean +0.7677%, net mean +0.6573%, net Sharpe 0.5433 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:11`); OOS n = 151 events, gross mean -0.2834%, net mean -0.3992%, net Sharpe -0.2035 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:12`).
   - **Alt 1h Run**: IS n = 21, net mean +2.0550%; OOS n = 43, gross mean +0.6085%, net mean +0.5031%, net Sharpe 0.1665 (< 0.3 FAIL mark) (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_c1.md:50-51`).
2. **Corrected T055-C1 Rerun with Full Funding (2026-10-07)**:
   - **Path**: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:1-66`
   - **Fee-Net**: Fee-net evaluated (fee 10 bps RT + slip 2 bps RT + funding across full 2020-01..2026-08 archive, 7,305 records; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:6-9,27`).
   - **IS / OOS Partition**: Single 70/30 split; 35,008 15m bars clipped to funding coverage (IS 24,505 / OOS 10,503; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:8,27`).
   - **Sample Size (n)**: IS n = 129 events, gross mean +0.5244%, net mean +0.4113%, net Sharpe 0.2736 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:33`); OOS n = 76 events, gross mean +0.0650%, net mean -0.0453%, net Sharpe -0.0346 (`MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:34`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Ruling B103**: "Backtest funding cost is silently 0 outside the locally loaded funding range; local fundingRate holds 2025-09..2026-08 while the Binance archive has BTCUSDT 8h funding from 2020-01" (`python scripts/dev/lab_query.py rulings positioning`; `MyTradingSys/system/rulings.json:80-87`). Closed 2026-10-04.
- **Data Truncation / Out-of-Bounds Crash**: Rerun crashed with ValueError in `trade_costs.funding_paid` when bars extended beyond funding history (fixed in test/driver by clipping bars to funding range; `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:7-8`).
- **Live vs Backtest Timeframe Discrepancy**: "Funding/CVD tested on 15m, live on 1h, 0 of 34 coincide | BUG (timeframe) | LAYER_REALITY:17 | card positioning-c1 raw" (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:42`; `MyTradingSys/research/mts_doctor/LAYER_REALITY_2026-10-25.md:17`).
- **Live Exit Assumption**: "94% of live exits are time exits; the 1%/2%/8-bar bracket was never backtested, so live and tested numbers are not comparable for any layer" (`MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:39`).

### CONFLUENCE
- **Design Intention**: Independent standalone layer; never designed as a core filter (`MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:5`).
- **Merge Decision**: "Merge decision: supervisor 2026-09-29 (T055a H2 + T055b funding-extreme)" (`MyTradingSys/backtest/layers/FORMULAS.md:361`).
- **Live Wiring Role**: Classified as CONTEXT in role slot architecture (`MyTradingSys/research/layer_review_2026-10-26/LAYER_SHEETS.md:13,30`).
- **Actual Live Trades Combined**: Zero real trades combined ("Nothing combines on a live trade. `promoted_setups.json` ships empty... So no confluence rule has ever decided a real trade" in `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:8`).

---

## 2. oi_delta

### ORIGIN (Quoted Source)
- **Origin Specification**: Four-state open-interest classifier based on market microstructure positioning literature and trader concepts (`MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:3-6`).
- **Two Competing Schools**:
  - Volume-delta school: "delta_state (volume-delta school): sign of trade_flow.net_delta_1h" (`MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:5`).
  - Price school: "delta_state_price (price school): current_price[now] minus current_price[nearest snapshot at or before T-60m]" (`MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:6`).
- **Trader Ground Truth / Ledger**: NOT_IN_DATA (descriptive classifier; no dated trader call ledger exists; `MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:60`).

### PARAMETERS (SOURCED or OURS)
- **Classifier Input School**: choice between `volume-delta (net_delta_1h sign)` and `price (T-60m)` (`OURS`, quote: "delta school: volume-delta (net_delta_1h sign), price (T-60m)" in `MyTradingSys/system/layer_map.json:626-630`).
- **Forward Measurement Horizons**: 30m, 60m, 120m (`OURS`, quote: "Horizons: 30m, 60m, 120m" in `MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:9`).
- **Observation Window**: 60-minute delta window (`OURS`, quote: "delta_state_price (price school): current_price[now] minus current_price[nearest snapshot at or before T-60m]" in `MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:6`).
- **Four Categorical States**: aggressive_long, aggressive_short, rekt_long, rekt_short, plus neutral (`SOURCED` from orderflow / positioning taxonomy; `MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:11-12`).

### BACKTESTS (Path, Fee-Net, IS/OOS, n)
1. **OI Delta 4-State Backtest (2026-09-21)**:
   - **Path**: `MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:1-62`
   - **Fee-Net**: Not fee-net; gross forward return % with day-clustered standard errors (`MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:14,56-62; system/layer_map.json:1396`).
   - **IS / OOS Partition**: None (descriptive study over single snapshot window 2026-09-13 to 2026-09-22; `MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:58`).
   - **Sample Size (n)**: 6,362 joined snapshot rows across 8 to 9 days (`MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:8,18-35,38-55`).
2. **OI Divergence Event Study (2026-10-10)**:
   - **Path**: `MyTradingSys/research/OI_EVENT_STUDY_2026-10-10.md:1-35`
   - **Fee-Net**: Not fee-net; raw and abnormal forward returns minus unconditional mean (`MyTradingSys/research/OI_EVENT_STUDY_2026-10-10.md:6-10`).
   - **IS / OOS Partition**: None; snapshot window 2026-09-12 to 2026-10-10 (~28 days; `MyTradingSys/research/OI_EVENT_STUDY_2026-10-10.md:30`).
   - **Sample Size (n)**: bearish_div n = 66 events (17 days); bullish_div n = 48 events (15 days) (`MyTradingSys/research/OI_EVENT_STUDY_2026-10-10.md:12-26`).
3. **OI Divergence v2 Pre-Registered Backtest (2026-10-10)**:
   - **Path**: `MyTradingSys/research/OI_DIVERGENCE_V2_2026-10-10.md:1-54`
   - **Fee-Net**: Fee-net evaluated (fees 10 bps RT, slippage 2 bps RT, funding from records; `MyTradingSys/research/OI_DIVERGENCE_V2_2026-10-10.md:4`).
   - **IS / OOS Partition**: 3 walk-forward folds (train / test) with 96-bar embargo (`MyTradingSys/research/OI_DIVERGENCE_V2_2026-10-10.md:5,44-54`).
   - **Sample Size (n)**: 2,350 total events; pooled long n = 1,071, pooled short n = 1,279 across horizons 4, 8, 16 bars (`MyTradingSys/research/OI_DIVERGENCE_V2_2026-10-10.md:8-20`).
4. **Price vs CVD Divergence with OI Split (2026-10-14, Rerun 2026-10-17)**:
   - **Path**: `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:1-61`
   - **Fee-Net**: Fee-net evaluated (taker fee 0.05% per side = 0.10% RT; funding unmodeled; `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:10,39-46`).
   - **IS / OOS Partition**: DEV 2022-2024 / VAL 2025 / HOLDOUT 2026 (OI split available only 2025-09+; `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:49`).
   - **Sample Size (n)**: S1 (1m) 4,933 long / 5,434 short DIV events (CONTROL: 10,921 long / 11,143 short); S5 (5m) 1,411 long / 1,858 short DIV events (CONTROL: 5,147 long / 5,447 short) (`MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:41-46`).

### KNOWN BUGS, FABRICATIONS OR ASSUMPTIONS (Rulings)
- **Ruling B103**: Funding cost silently 0 outside locally loaded range (`python scripts/dev/lab_query.py rulings positioning`; `MyTradingSys/system/rulings.json:80-87`).
- **Historical Data Availability Gap**: Historical DEV OI data (2022-01..2024-06) does not exist in repo; OI series begins 2025-09-01 (`MyTradingSys/system/tasks/archive/gptb-oi-delta-event-table.json:17`; `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:1`).
- **Short Window Sample Clustering**: Initial study clustered over 8-9 calendar days; day-clustered standard errors required due to high autocorrelation (`MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:58-61`).
- **Data Contamination in 2026-10-14 DEV Split**: "study.py split_of() is year-based (DEV = year <= 2024), so DEV includes 2024-07..12 (own copy, not fires_kline)" (`MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:3`). Corrected in 2026-10-17 DEV rerun (`MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:1`).

### CONFLUENCE
- **Design Intention**: Context filter for higher-timeframe state (`MyTradingSys/backtest/layers/fabio/htf_context_live.py:14,104`; `MyTradingSys/system/layer_index.json:368`).
- **Intended Interaction**: Designed to confirm directional orderflow / price breakouts or detect absorption/exhaustion (`MyTradingSys/research/OI_DELTA_4STATE_BACKTEST_2026-09-21.md:3-6`).
- **Confirmed By / Tested With**: Evaluated as an interaction split with price/CVD divergence (`MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:5-10,49`).
- **Live Status**: Unused as an active filter on live trades (`MyTradingSys/system/LAYERS.md:122`).
