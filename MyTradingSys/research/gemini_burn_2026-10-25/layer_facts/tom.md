# Layer Family Fact Sheet: Tom (`tom`)

Generated per `MyTradingSys/system/ANTIGRAVITY_LAPTOP.md` item C for the layer review (card `layer-review-after-simulator`).
Scope: Layer family `tom` consisting of layers `tom_core`, `tom_proofs`, and `tom_vp_pivot` (`MyTradingSys/system/LAYERS.md:10-15`, `MyTradingSys/system/layer_index.json:40-43`).
Rules: Repo files only; every fact line carries `file:line` or `NOT_IN_DATA`; parameters labelled `SOURCED` or `OURS`; no verdict on keeping, dropping, demoting, or parking any layer (`MyTradingSys/system/ANTIGRAVITY_LAPTOP.md:16,27-33`).

---

## 1. Layer `tom_core`

### 1.1 ORIGIN
- **Analyst / Trader**: Tom (trader/analyst on DAX / index / order flow).
  - Source quote: "First, you have an idea. Second, you have proof that it's really time now to implement the idea. And third, you have a really clean risk management" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:52-53` quoting transcript `zQTbdEweG3c:28-32`).
  - Source quote on setup: "started way down here and then suddenly shot up just like a powerful rocket" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:59` quoting transcript `T6hDJcHrVBM:114-116`).
  - Source quote on liquidity / volume profile: "I can clearly see that there's no liquidity left" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:61` quoting transcript `k0zm5NYn0IQ:21-22`).
- **Description / Plain summary**: Tom core engine (setup candidates + proofs). "Fade an oversized push into thin volume when sellers show at the top (and his other setups later), on BTC charts with real order flow." (`MyTradingSys/system/LAYERS.md:13,44`, `MyTradingSys/system/layer_index.json:44`).
- **Module**: `src/main/java/datafeed/SetupCandidatesBuilder.java; backtest/verdict.py; backtest/tom_bt.py` (`MyTradingSys/system/LAYERS.md:13`, `MyTradingSys/system/layer_map.json:49`).
- **Status in repo**: STOP: do not backtest or tune the current BTC encoding (tom_transfer ROADMAP section 2); being redefined as Tom v2 (`MyTradingSys/system/LAYERS.md:13`, `MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md:21-25`).

### 1.2 PARAMETERS
- `min_proof` [OURS]: choice of proof threshold to fire candidate signals (`live SETUP_FORMING` requiring 5 proofs, `3 (WATCH, sensitivity)`, `4 (p4, sensitivity)`) (`MyTradingSys/system/layer_map.json:52-62`). Note: Tom gives no proof count threshold; "3 proofs" and "5 proofs" are OURS / NO-SOURCE (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:66-67`).
- `fee_model` [OURS]: fee/slippage variants tested (`base`, `all_taker_0.05`, `slip_5bps`, `target_first`) (`MyTradingSys/system/layer_map.json:63-74`).
- `market` [OURS]: choice of market (`BTCUSDT (snapshots)`, `DAX / GER40 (FDAX fees)`) (`MyTradingSys/system/layer_map.json:75-85`).
- `shift` [OURS]: proof shift extension arms (`0 (pre-registered)`, `1`, `2`, `3`) (`MyTradingSys/system/layer_map.json:86-98`).
- `stop_loss_fixed_dax` [SOURCED]: 20 DAX points when no reference exists above ("For the first position, I'm setting a stop-loss of 20 points in the DAX" / "The simple reason for this is that I don't have any reference values up here") (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:85,94` quoting transcript `k0zm5NYn0IQ:22-26`).
- `stop_loss_context` [SOURCED]: stop placed above the seller level / volume bell ("my stop loss is immediately above the 258" / "the stop loss was set above the bell") (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:93` quoting transcripts `ujedEcmvBMk:67-74` and `n7ZSkjb7JXs:299-301`).
- `min_stop_width_btc` [OURS]: minimum stop width `W_min = max(W_noise, W_fee)` (0.40% for taker, 0.20% for Deribit maker) derived from noise unit N5 and fee tolerance (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:313-335`).
- `target_rr` [SOURCED]: expected R:R minimum 1.5, entry R:R ~1:6 ("need at least a riskreward ratio of 1.5", "In terms of riskreward ratio, we're currently at about 1:6") (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:27-28,106` quoting transcript `k0zm5NYn0IQ:93-96,549-552`).
- `time_exit_session` [SOURCED]: flat at 17:35 Berlin time ("the market phase where the highest liquidity is present between 8:30, 9:00 and 17:35") (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:120-121,385` quoting transcript `T6hDJcHrVBM:94-97`).
- `time_exit_8bar` [OURS]: 8 zone-timeframe bars timeout in legacy engine (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:385`, `MyTradingSys/system/layer_map.json:442`).

### 1.3 BACKTESTS
1. **TOM-CORE-0929**
   - Report path: `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md` (`MyTradingSys/system/LAYERS.md:23`, `MyTradingSys/system/layer_map.json:415-429`).
   - Fee-net: Evaluated both gross and net; net of fees using Deribit schedule (maker 0 / taker 0.05%) and stress variants (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6,41-47`).
   - In-sample / Out-of-sample: In-sample 2022-01-20..2026-06-25; Out-of-sample holdout 2026-06-26..2026-09-26 (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6,10`).
   - n trades: Live rule `SETUP_FORMING` (proof >= 5) had 19 signals, 17 filled trades (0 in holdout); sensitivity `watch_episode` (proof >= 3) had 4,417 filled trades total (254 in holdout) (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6,14,35-40`).
2. **TOM-CORE-1007** (run `tom_core_20261007`)
   - Report path: `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md` and full report `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06_full.md` (`MyTradingSys/system/LAYERS.md:21-22`, `MyTradingSys/system/layer_map.json:430-444`).
   - Fee-net: Evaluated gross and net; fee cost ~2.76 R per trade after stop-floor removal (`MyTradingSys/system/layer_map.json:436`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:1-15`).
   - In-sample / Out-of-sample: In-sample 2022-01-20..2026-06-25; holdout 2026-06-26..2026-09-26 (`MyTradingSys/system/layer_map.json:435`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:9`).
   - n trades: Live rule `SETUP_FORMING` had 0 filled trades (17 -> 0); sensitivity episodes had 2,880 filled trades total, 181 in holdout (`MyTradingSys/system/layer_map.json:437-438`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:15`).
3. **DAX-SMOKE** (run `dax_bt_20261010_SMOKE`)
   - Report path: `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md` (`MyTradingSys/system/LAYERS.md:18`, `MyTradingSys/system/layer_map.json:460-474`).
   - Fee-net: Fee-net evaluated under `FEES_FDAX` (0.000005 per side) vs BTC Deribit fees (`MyTradingSys/system/layer_map.json:466`, `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:9-11`).
   - In-sample / Out-of-sample: Smoke only; dev period 2026-01 (1 month) on GER40; DAX holdout NOT read (`MyTradingSys/system/layer_map.json:464,470`, `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:1-5,11`).
   - n trades: Pipeline smoke test; 1,251 valid snapshot rows remain after filtering; 0 filled trades reportable as edge (`MyTradingSys/system/layer_map.json:468-470`, `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:1,11`).
4. **TOM-DIAG-BTC**
   - Report path: `MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md` (`MyTradingSys/system/LAYERS.md:17`, `MyTradingSys/system/layer_map.json:499-510`).
   - Fee-net: Fee-net with default `tom_bt` fee schedules (`MyTradingSys/system/layer_map.json:505`, `MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md:9`).
   - In-sample / Out-of-sample: Historical 2022-01-20..2025-08-31; Dev 2025-09-01..2026-06-25; holdout 2026-06-26.. excluded/burned (`MyTradingSys/system/layer_map.json:504`, `MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md:8`).
   - n trades: n = 2,699 `watch_episode` trades, 59 `p4_episode` trades (`MyTradingSys/system/layer_map.json:507`, `MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md:9`).

### 1.4 KNOWN BUGS, FABRICATIONS, ASSUMPTIONS (Rulings)
- Ruling **B191** [CLOSED, MED]: Live-loop snapshot timeouts: loop spawned cmd + Maven JVM per cycle and the gates competed with live loop for CPU (`scripts/dev/lab_query.py rulings tom`).
- Ruling **B179** [OPEN, MED]: Turn Tom and Fabio layers story into slide deck artifact for operator review (`scripts/dev/lab_query.py rulings tom`).
- Ruling **B158** [CLOSED, MED]: Screenshot reads never write `runtime/session_state.json` (persisted thesis store); last written 2026-09-14 (`scripts/dev/lab_query.py rulings tom`).
- Ruling **B156** [CLOSED, MED]: Tom alert card `SSOT_THESIS` stale text (`scripts/dev/lab_query.py rulings tom`).
- Ruling **B154** [OPEN, MED]: No regime-stratified and no session-stratified backtest verdict exists; every reported edge is one aggregate number (`scripts/dev/lab_query.py rulings tom`).
- Ruling **B147** [CLOSED, HIGH]: Tom live-rule evidence unreliable: rerun showed 0 signals vs 19 previously; holdout read twice; Oct-7 run not on HEAD (`scripts/dev/lab_query.py rulings tom`).
- Ruling **B146** [CLOSED, HIGH]: No minimum stop width after commit `0c34a2d` removed 0.1% floor: median stop 0.082%, fees dominate (`scripts/dev/lab_query.py rulings tom`, `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:278-290`).
- Ruling **B135** [CLOSED, LOW]: Proof count thresholds in `start-trading-day.ps1` after `book_imbalance` left count (`scripts/dev/lab_query.py rulings tom`).
- Ruling **B131** [CLOSED, MED]: Tom proof-5 candidate pool skewed 215 short : 105 long, baked into `SetupCandidatesBuilder` before proof guard (`scripts/dev/lab_query.py rulings tom`).
- Ruling **B127** [CLOSED, MED]: Audit PARTIAL group (e): 13 findings where code exists but test is missing or staged (`scripts/dev/lab_query.py rulings tom`).

### 1.5 CONFLUENCE
- **Fabio layers**: In `TOM_CORE_BT.md`, Tom core signals were evaluated for confluence with Fabio kline detectors (`cvd_absorption`, `escalation`, `fvg_bounce`) tagged within 4 and 12 bars (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:96-120`). Tagged descriptive only, not a filter (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:96`, `MyTradingSys/system/layer_map.json:421`).
- **Pitchfork layer**: Modified Schiff tine bounce and Volume Profile confluence wired into `SetupCandidatesBuilder.java` (`MyTradingSys/system/LAYERS.md:13`, commit `91d2e43c31`).
- **Cross-guidance (BB / LVN)**: Tested in `Q33` matrix (`bb_lvn_triggers` x context filters) to confirm Tom moves; no cell survived (`MyTradingSys/system/LAYERS.md:73-80`, `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:1-10`).

---

## 2. Layer `tom_proofs`

### 2.1 ORIGIN
- **Analyst / Trader**: Tom (order flow proofs for trade confirmation).
  - Source quote: "If you make trades against the trend, then you need many, many parameters that speak in your favor" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:65` quoting transcript `zQTbdEweG3c:23-26`).
  - Source quote: "we also had a finished auction. That means the market formed a completed auction at the top" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:70` quoting transcript `k0zm5NYn0IQ:84-86`).
  - Source quote: "this lethargy was characterized by large sales volumes. And that prompted me to plan a short trade there" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:75` quoting transcript `l8RZrBfzvp4:72-76`).
- **Description / Plain summary**: Tom order-flow proof flags (`absorption`, `cvd_aligned`, `delta_flip`, `finished_auction`, `book_imbalance`, `volume_spike` [P06]) (`MyTradingSys/system/LAYERS.md:14`, `MyTradingSys/system/layer_index.json:41`).
- **Module**: `SetupCandidatesBuilder.java (proof flags)` (`MyTradingSys/system/LAYERS.md:14`, `src/main/java/datafeed/SetupCandidatesBuilder.java:582-636`).
- **Status in repo**: `book_imbalance` never counts in historical snapshots (no raw source wired); `P06` volume spike is NO-SOURCE (`MyTradingSys/system/LAYERS.md:14`, `src/main/java/datafeed/SetupCandidatesBuilder.java:630-634`).

### 2.2 PARAMETERS
- `rejection_wick` [OURS]: wick touching candidate zone (`src/main/java/datafeed/SetupCandidatesBuilder.java:621,718`).
- `absorption` [OURS]: absorption detected via volume ratio and candle count (`src/main/java/datafeed/SetupCandidatesBuilder.java:584-587,622`).
- `finished_auction` [SOURCED]: completed auction opposite the trade direction; Tom quotes A-P1 (`src/main/java/datafeed/SetupCandidatesBuilder.java:623-628`, `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:70`).
- `delta_flip` [OURS]: delta flip at zone level (`src/main/java/datafeed/SetupCandidatesBuilder.java:593-596,629`).
- `volume_spike` (P06) [OURS / NO-SOURCE]: 2.0x volume spike over 240 bars; dropped from active count as unsourced (`src/main/java/datafeed/SetupCandidatesBuilder.java:630`, `MyTradingSys/system/LAYERS.md:14`).
- `speed` [OURS]: speed proxy; dropped from count toward proof in D4 (`src/main/java/datafeed/SetupCandidatesBuilder.java:631`).
- `cvd_aligned` [OURS]: CVD aligned with setup direction (`src/main/java/datafeed/SetupCandidatesBuilder.java:607,632`).
- `book_imbalance` [OURS / NO-SOURCE]: order book imbalance; dropped from count due to skew and lack of historical data (`src/main/java/datafeed/SetupCandidatesBuilder.java:608,633-634`).
- `masked` [OURS]: parameter in backtests to mask off order-flow proofs (`absorption`, `cvd_aligned`, `delta_flip`, `finished_auction`) for matched-proof cross-market comparisons (`MyTradingSys/system/layer_map.json:107-117`).

### 2.3 BACKTESTS
1. **TOM-CORE-0929**
   - Report path: `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md` (`MyTradingSys/system/layer_map.json:415-429`).
   - Fee-net: Evaluated net of Deribit fees (`MyTradingSys/system/layer_map.json:420`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6`).
   - In-sample / Out-of-sample: In-sample 2022-01-20..2026-06-25; Holdout 2026-06-26..2026-09-26 (`MyTradingSys/system/layer_map.json:419`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6`).
   - n trades: Evaluated proof >= 3 (4,417 trades) and proof >= 4 (`p4_episode`); live proof >= 5 had 17 filled trades (`MyTradingSys/system/layer_map.json:423-424`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6,14`).
2. **TOM-CORE-1007**
   - Report path: `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md` (`MyTradingSys/system/layer_map.json:430-444`).
   - Fee-net: Evaluated net of fees (`MyTradingSys/system/layer_map.json:436`).
   - In-sample / Out-of-sample: In-sample 2022-01-20..2026-06-25; holdout 2026-06-26.. (n=181) (`MyTradingSys/system/layer_map.json:435`).
   - n trades: 2,880 filled episodes at proof >= 3 (`MyTradingSys/system/layer_map.json:438`).
3. **DAX-SMOKE**
   - Report path: `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md` (`MyTradingSys/system/layer_map.json:460-474`).
   - Fee-net: Evaluated under `FEES_FDAX` vs BTC fees (`MyTradingSys/system/layer_map.json:466`).
   - In-sample / Out-of-sample: Dev only (GER40 2026-01 smoke); holdout unread (`MyTradingSys/system/layer_map.json:464`).
   - n trades: Matched-proof BTC arm masked order-flow proofs across 1,818 candidates; DAX order-flow mask changed proof count on 0 candidates (`MyTradingSys/system/layer_map.json:467`, `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:11-15`).

### 2.4 KNOWN BUGS, FABRICATIONS, ASSUMPTIONS (Rulings)
- Ruling **B131** [CLOSED, MED]: Proof-5 candidate pool skewed 215 short : 105 long; `book_imbalance` gave +1 to shorts and +0 to longs (`scripts/dev/lab_query.py rulings tom`, `src/main/java/datafeed/SetupCandidatesBuilder.java:633-634`).
- Ruling **B135** [CLOSED, LOW]: `start-trading-day.ps1` proof-count thresholds after `book_imbalance` removal (`scripts/dev/lab_query.py rulings tom`).
- Ruling **B147** [CLOSED, HIGH]: Missing raw data in historical snapshots capped max proof count at 6 instead of 7 (`scripts/dev/lab_query.py rulings tom`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:14`).

### 2.5 CONFLUENCE
- Confirms candidate setups generated by `tom_core` (gating setups into `WATCH` or `SETUP_FORMING` states) (`src/main/java/datafeed/SetupCandidatesBuilder.java:619-636`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:14`).
- Confirms/interacts with Fabio kline indicators (`cvd_absorption`, `escalation`) (`MyTradingSys/system/layer_map.json:421`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:96-120`).

---

## 3. Layer `tom_vp_pivot`

### 3.1 ORIGIN
- **Analyst / Trader**: Tom (Volume Profile anchoring methodology: pivot high/low anchors vs session/calendar anchors).
  - Source quote: "these price areas are zones with very low volume for the respective time frame we're looking at. And the market often bounces off these areas." (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:16` quoting transcript `YmygDgtoxO8_raw.txt:19 [TOM-210]`).
  - Source quote on balance / VPOC: "this is the price range where the market was in equilibrium and where I then simply expect a reaction could occur" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:102` quoting transcript `zQTbdEweG3c:191-195`).
- **Description / Plain summary**: Anchored volume-profile touch study (POC/VAH/VAL, pivot vs calendar anchors) (`MyTradingSys/system/LAYERS.md:15`, `MyTradingSys/system/layer_map.json:118-124`).
- **Module**: `backtest/vp_pivot_probe.py (FORMULAS 18)` (`MyTradingSys/system/LAYERS.md:15`, `MyTradingSys/system/layer_map.json:122`).
- **Status in repo**: Closed: no anchor beats placebo (`MyTradingSys/system/LAYERS.md:15`, `MyTradingSys/system/layer_map.json:123`, `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:7-15`).

### 3.2 PARAMETERS
- `anchor` [SOURCED / OURS]: Anchor families tested: A1 pivot high to low [SOURCED Tom], prior_day [OURS], weekly [OURS], calendar [OURS] (`MyTradingSys/system/layer_map.json:126-136`, `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:8-9`).
- `pivot_n` [OURS / NO-SOURCE]: Pivot width n on 1h bars ({2, 3, 5}) (`MyTradingSys/system/layer_map.json:137-147`, `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:4`).
- `size_k` [OURS / NO-SOURCE]: Pivot size filter k ({0, 2}) (`MyTradingSys/system/layer_map.json:148-158`).
- `bin_usd` [OURS / NO-SOURCE]: Volume profile bin width = 10 USD (`MyTradingSys/system/layer_map.json:159-167`, `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:4`).
- `barrier` [OURS / NO-SOURCE]: Barrier definition: ATR14(1h), +-1R, timeout 48x5m bars (`MyTradingSys/system/layer_map.json:168-176`, `MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:4`).
- `placebo_offset` [OURS]: Placebo levels shifted 0.5 to 3.0 ATR (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:4,9`).

### 3.3 BACKTESTS
1. **TOM-VP-PHASE2**
   - Report path: `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md` (`MyTradingSys/system/LAYERS.md:19`, `MyTradingSys/system/layer_map.json:445-459`).
   - Fee-net: Evaluated gross and net; taker fee ~0.19 R per round trip, maker variant (-0.10..-0.16 R) (`MyTradingSys/system/layer_map.json:451`, `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:10-12`).
   - In-sample / Out-of-sample: Full span 2022-01-01..2026-10-07 (1,741 days, 2,507,040 1m bars); tested per-year 2022-2026 (`MyTradingSys/system/layer_map.json:448,450`, `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:5,15`).
   - n trades: n >= 1,055 per stream across 48 family x level streams (thousands per stream) (`MyTradingSys/system/layer_map.json:453-454`, `MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:7-15`).
2. **VP-PIVOT-P2**
   - Report path: `MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md` (`MyTradingSys/system/LAYERS.md:20`, `MyTradingSys/system/layer_map.json:511-523`).
   - Fee-net: Net evaluated under taker 0.0005 / maker 0.0002 (`MyTradingSys/system/layer_map.json:517`, `MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:4`).
   - In-sample / Out-of-sample: Full historical series 2022-01-01..2026-10-08; 2,000 day-block bootstrap resamples (`MyTradingSys/system/layer_map.json:514,516`, `MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:1-4`).
   - n trades: Session POC n = 9,073; Session VAH n = 7,039; Session VAL n = 7,328; Weekly POC n = 4,661; Weekly VAH n = 2,876; Weekly VAL n = 2,797; Prior day POC n = 3,598 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:9-15`).

### 3.4 KNOWN BUGS, FABRICATIONS, ASSUMPTIONS (Rulings)
- Ruling **B154** [OPEN, MED]: No regime-stratified backtest verdict exists; every reported edge is one aggregate number (`scripts/dev/lab_query.py rulings tom`).
- Ruling **B146** [CLOSED, HIGH]: Stop distance and fees in raw level-touch setups: fixed ATR barrier with taker fees produced net negative returns across all levels (`scripts/dev/lab_query.py rulings tom`, `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:10-12`).
- Fixed barrier assumption [OURS / NO-SOURCE]: +-1R ATR14 barrier and 48-bar timeout assumed without source from Tom (`MyTradingSys/system/layer_map.json:173`, `MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:4`).

### 3.5 CONFLUENCE
- Confirms `tom_core`: Intended to provide anchor levels (POC, VAH, VAL) for setup zones (`ct_short` at VAH / swing high, `scalp` at VWAP/POC) in `SetupCandidatesBuilder.java` (`MyTradingSys/system/layer_map.json:442`, `src/main/java/datafeed/SetupCandidatesBuilder.java:417-438`).
- Confirms pitchfork / guidance layers: Pitchfork tine bounce with Volume Profile confluence (`MyTradingSys/system/LAYERS.md:13`, commit `91d2e43c31`).
- Confirmation from other layers: NOT_IN_DATA (tested as isolated level touch vs placebo in Phase 2) (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:8-14`).
