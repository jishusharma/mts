# Layer review fact sheet: families fabio and session_timing

Card `layer-review-fabio-session` (setup truth, repo only). Built 2026-11-02 at trunk `be2ce0ee9`. Start: `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/fabio.md` and `session_timing.md`; every file:line below was re-resolved against this tree (Gemini line numbers drift, and several `fabio_of_model.py` lines were off by 5 to 8). No verdict wording on any layer (operator NO 2026-10-25, `MyTradingSys/research/mts_doctor/MAINNET_PATH_2026-10-25.md:34`); labels such as "no edge" or "FAIL" below are copied from the cited result file, not ours. Numbers are copied with their source line, never recomputed. Parameter labels: SOURCED = a trader or paper quote is cited; OURS = our choice, never the trader's.

Layers (from `MyTradingSys/system/layer_index.json`): family fabio (`layer_index.json:102`) = fabio_cvd_absorption, fabio_escalation, fabio_volume_fvg, fabio_v3, fabio_of; family session_timing (`layer_index.json:416`) = session_momentum, turn_of_candle, session_levels. That is 8 sections.

Important change after the older result files: commit `2afc18be6` (2026-11-01) changed two detectors. `cvd_absorption_events` now tests the price level two-sided (`|cur/prev-1| <= tol`); `escalation_events` now needs the record bar to close beyond the level. Legacy callers (`run_backtest`, `run_bracket_grid`, `tom_bt_run`, `event_table`) pass the legacy flags; `live_layers` and `live_runner_cli` use the strict defaults. Descriptive DEV 1h counts in that commit: escalation 652 old -> 8 new, cvd_absorption 393 old -> 135 new, "descriptive counts, no edge claim" (commit body, `git show 2afc18be6`). Every fabio backtest table below was produced with the legacy behaviour.

Extract quotes (video) use the format `> "quote"` then `**Source GPS: id | third**` so `python scripts/dev/verify_extract_quotes.py` checks them against the transcripts.

## fabio_cvd_absorption

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md:44` says Fabio order flow "Does not fit as order flow"; only price-only v3 parts are plugged in.

### Idea and source

- Analyst: Fabio Valentini (name sourced at `MyTradingSys/research/fabio_asr_2026-10-16/ASR_EXTRACTION_ADDENDUM.md:14`).
- Code docstring: "FAB-007 CVD-vs-price divergence absorption detector" with the mirror (bearish) case "implemented as a documented symmetric extension" (`MyTradingSys/backtest/layers/fabio/fabio_cvd_absorption.py:2-6`).
- Rulebook row FR-16 "Absorption: delta in, price flat; CVD divergence; heavy absorption", citing FAB-007 (`MyTradingSys/research/fast_track_2026-09-27/FABIO_RULEBOOK.md:20`).

> "we have a lower low on the cumulative volume delta here while the market is still on the same level as before. This is what it's called it's called absorption."
**Source GPS: o-w5Gxss6T0 | END**

(Extract: `extracts/v2/fabio/o-w5Gxss6T0_v2.md:38-40`.)

### Parameters

- `left`, `right` swing width 2 and 2, `use_body` True, `price_tolerance` 0.001: OURS (`fabio_cvd_absorption.py:45`); the video gives no threshold ("UNDEFINED in the video", `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md:11`).
- Grid {2,3,5} x tolerance {0.05,0.1,0.2,0.5} % (12 variants): OURS (`FABIO_L1_REPORT.md:12`).
- Per-bar delta `2*tbv - v` from taker-buy volume (`fabio_cvd_absorption.py:9`): OURS.
- CVD anchor: reset once at the start of the input, no session reset: OURS. His definition resets CVD per session: "the cumulative volume delta that is the summary of all the delta exchange in the session" (`MyTradingSys/research/fabio_cvd_2026-10-30/CVD_CONCEPTS.md:16`; the BTC transfer is OURS per that file).
- Price test: two-sided same-level band since `2afc18be6` (OURS reading of "same level"; the old one-sided test is behind `same_level_only=False`).

### Backtests

- `MyTradingSys/backtest/layers/fabio/FABIO_L1_REPORT.md`: BTCUSDT 1m resampled to 5m/15m/1h, 2022-01-01..2026-09-26, 2,491,200 bars (line 5); fee-net, 0.10 % round trip subtracted (line 9); chronological 70 % in-sample / 30 % out-of-sample (line 7); legacy detector behaviour.
- OOS h5, frozen in-sample choice (`FABIO_L1_REPORT.md:33-35`): 5m n 1639, gross +0.000 %, net -0.100 %, PBO 0.683; 15m n 982, gross +0.001 %, net -0.099 %, PBO 0.330; 1h n 109, gross -0.042 %, net -0.142 %, PBO 0.333. Report label for all three: "no edge".
- `MyTradingSys/research/orderflow_views_2026-10-14/RESULT.md:8-37`: price versus CVD divergence on 1m and 5m, fee 0.05 % per side, "0 of 12 arms pass" the pre-registered mark (line numbers as in the file; read the table there for per-arm n).
- No run exists on the 2026-11-01 strict detector beyond the descriptive counts in commit `2afc18be6`.

### Bugs and assumptions

- `lab_query.py rulings fabio` lists B102 (CLOSED, fixed UTC session anchors, `MyTradingSys/research/BUGS.md:212`) and B103 (CLOSED, funding silently 0 outside the loaded range); neither is specific to this detector.
- L1 method: fixed-horizon close-to-close returns, "No stop/target simulation"; events overlap, n is not independent (`FABIO_L1_REPORT.md:21-25` region, "Caveats").
- No session reset of CVD against his per-session CVD (see Parameters).

### Confluence

- Rule FR-19 (failed auction and day direction) is the rulebook row this feeds (`FABIO_RULEBOOK.md:25`).
- Reuses `find_swings` from the `cc_structure` CryptoCred layer (`fabio_cvd_absorption.py:17-19`).
- Tom/Fabio guidance: "Fabio's CVD/absorption is what Tom calls proof" (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:59`); Krown KR-S13 effort-versus-result overlaps FAB-2/FAB-5 (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:992` region).
- Live wiring: `live_layers` uses the strict detector defaults (commit `2afc18be6` body); no `wiring_registry.json` row names this file.

## fabio_escalation

Wired in the simulator: no (same reason as above, `PLUGIN.md:44`).

### Idea and source

- Docstring: "FAB-002 ('aggression that fails to break a protected level = absorption') and FAB-003 ('escalating aggression -- a record-volume, record-delta bar -- into an already-absorbed level = expect a BREAKOUT in the aggressor's direction, not a reversal'). Both are quoted UNDEFINED on exact thresholds" (`MyTradingSys/backtest/layers/fabio/fabio_escalation.py:2-7`). This is a code quote of the rule text, not a transcript quote, so it carries no Source GPS line.
- Rulebook FR-16 and FR-18 (`FABIO_RULEBOOK.md:20`, `:22`).

### Parameters

- `left`, `right` 2, `use_body` True, `level_tolerance` 0.001, `aggression_k` 2.0, `record_lookback` 20: OURS (`fabio_escalation.py:16`); every threshold is "this module's own explicit grid parameter, not from the video" (docstring, lines 5-7).
- Grid level_tolerance {0.1,0.2} % x k {1.5,2,3} x lookback {20,50} (12 variants): OURS (`FABIO_L1_REPORT.md:13`).
- Break definition: record bar must close beyond the level in the aggressor direction, kwarg `require_break` (`fabio_escalation.py:19`): OURS ("break definition is OURS", commit `2afc18be6`).

### Backtests

- `FABIO_L1_REPORT.md:36-38`, same data and split as above, fee-net 0.10 %, legacy detector: OOS h5 5m n 7908, gross -0.004 %, net -0.104 %, PBO 0.657; 15m n 1095, gross -0.069 %, net -0.169 %, PBO 0.174; 1h n 182, gross +0.213 %, net +0.113 %, PBO 0.756. Labels in the file: 5m and 15m "no edge", 1h "no edge (fails PBO; see below)".
- Descriptive event table, DEV 1h, 652 events, 24-bar gross MFE 4.6065R / MAE 3.9069R, "descriptive gross excursion, not an edge claim": `MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-fabio-escalation-event-table.md:3`; listed in `MyTradingSys/research/layer_lab/TRIALS.md:14`. After `2afc18be6` the same 1h count is 8 (commit body).

### Bugs and assumptions

- Driver ran the detector on disjoint 1000-bar chunks with 500 bars of warm-up, so a level lived at most about 1500 bars, against the spec's unbounded life (`FABIO_L1_REPORT.md:17-20`).
- Open card `t09-f4-live-window-99-bars-swing-layers`: the 99-bar live window misses 68 of 96 escalation signals (`MyTradingSys/system/LAYERS.md:68`).
- B102 and B103 as above (`BUGS.md:212`).

### Confluence

- Requires prior absorption at the level before firing (`fabio_escalation.py:2-7`).
- Cross-guidance matrix card Q33 examined it; the matrix report is `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md` (`LAYERS.md:77`).
- Reuses `find_swings` from `cc_structure` (`fabio_escalation.py:9`).

## fabio_volume_fvg

Wired in the simulator: no (`PLUGIN.md:44`).

### Idea and source

- Docstring: FAB-005 fixed-range volume profile over one swing leg, value area 70 %, lowest-volume price level inside it; FAB-006 price expected to react there (`MyTradingSys/backtest/layers/fabio/fabio_volume_fvg.py:2-7`).

> "to identify a real fair value gap, you need to get inside the candle and you need to see how the volume transacted."
**Source GPS: o-w5Gxss6T0 | MIDDLE**

> "the lowest volume of interaction in all the area of value area. So where 70% of the volume got transacted is exactly this one is the level that goes from 24,318 to 24,317."
**Source GPS: o-w5Gxss6T0 | MIDDLE**

(Extract `extracts/v2/fabio/o-w5Gxss6T0_v2.md:23-26`.)

### Parameters

- Value area 70 %: SOURCED (quote above). Bins 20, swings 2/2, `use_body` True, first touch within 200 bars: OURS (`fabio_volume_fvg.py:51`, `FABIO_L1_REPORT.md:13-14`). No grid, so no PBO.
- Volume-at-price is approximated by spreading each 1m bar's volume uniformly over its range, because no aggTrades are used (`fabio_volume_fvg.py:12-15`): OURS.
- Touch side (bounce versus through) is not defined in the source, so both readings are reported (`FABIO_L1_REPORT.md:26`).

### Backtests

- `FABIO_L1_REPORT.md:53-58`, same data, split and 0.10 % fee note as above; fixed parameters, compared with a random-VA-bin control. OOS h5 gross: 5m bounce n 1228 +0.011 % (control n 1222, -0.003 %); 15m bounce n 377 -0.002 % (control n 379, +0.027 %); 1h bounce n 93 +0.274 % (control n 91, +0.130 %); the "through" rows are exact mirrors. Label in the file: "no edge" on every row (`FABIO_L1_REPORT.md:53-58`).
- Descriptive DEV 1h LVN touch table: `MyTradingSys/research/layer_lab/reports/2026-10-17_gptb-fabio-lvn-touch-event-table.md:1-8`; `TRIALS.md:17`.

### Bugs and assumptions

- Kline approximation of the volume profile (see Parameters). FVG touch side undefined (see above).
- B102 and B103 as above.

### Confluence

- Tom teaches an LVN as bounce, fill and revert; Fabio teaches sweep then empty level then fast through (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:42-45` region).
- Reuses `find_swings` from `cc_structure` (`fabio_volume_fvg.py:18`).

## fabio_v3

Wired in the simulator: partly. `PLUGIN.md:44`: "Does not fit as order flow; price-only parts plugged in 2026-10-31"; `studies/fabio_v3.py` runs Model C (first-30-minute range breakout) and Model B (failed breakout back into a balance box) on 1m klines; Models A and D, the big-trade push, absorption in Model B and order-flow exits are left out.

### Idea and source

- Spec title: "FABIO V3 SPEC - trade model as a layer module (location -> context -> trigger -> management)", v3.1 2026-09-30; "Nothing here is a result"; "Fabio is a separate layer, never a Tom filter" (`MyTradingSys/research/fast_track_2026-09-27/FABIO_V3_SPEC.md:1-6`). Source videos listed in the spec header (lines 8-9).

### Parameters

- Provenance table 7.1, P01-P41 (`FABIO_V3_SPEC.md:192-232`): SOURCED rows include trigger on the close (P08, line 199), failed-auction trigger (P09), anchor = last own control (P10), max adds 2 (P22), floor at day R 0 (P26), structural stop behind the level + 1 tick (P32), Model C initial balance 30 minutes (P38). OURS rows include balance window N in {60,120,240} (P01, line 192), big trade 99th / 99.9th percentile (P05), stop floor 0.3 % / 0.5 % (P31), daily stop -3R (P29, SAFETY), tick and fees (P41, line 232). Mixed rows (rule SOURCED, number OURS) are P11, P14, P16, P19, P28, P33.
- Sim-desk price-only study settings carry (trader) or (ours) tags on screen (`PLUGIN.md:49`).

### Backtests

- Order-flow run: `MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:43-46` (BTCUSDT 1m order-flow bars; maker 0, taker 0.0005, 2 bps slippage per taker leg; 266 in-sample and 120 out-of-sample windows). Models A, B, D: 0 trade days out-of-sample (not evaluable); Model C `C|m5|f0.005|rest|g0.8`: OOS mean -0.1038 at 2 bps, 79 trade days, CI95 [-0.2087, -0.0053], PBO 0.196, labelled FAIL (`PRE_REG_FABIO_V3.md:44-46`, with `MyTradingSys/research/_archive/loose_2026-10/P2_FABIO_V3_HOLDOUT_STATUS.md`). Holdout (2026-06-26 onward) not read for Fabio v3 per B147 (same status file).
- Sim desk price-only, DEV 2022-04-01..2024-06-30, fee-net (maker 0.02 %, taker 0.05 %, slip 0.02 %): Model C n 515-518 at mean net R +0.035 to +0.071, CIs spanning zero, "NOT ENOUGH DATA" (`TRIALS.md:415-418`); Model C with 2R target n 518 mean -0.074 (`TRIALS.md:419`); Model B n 155 mean -0.448 "FAILED" (`TRIALS.md:420`), n 64 mean -0.445 "FAILED" (`TRIALS.md:421`), n 19 mean -0.437 "NOT ENOUGH DATA" (`TRIALS.md:422`), n 64 target 2R mean -0.422 "FAILED" (`TRIALS.md:424`).
- Look-ahead truncation fixtures for the v3 grid: `MyTradingSys/research/layer_lab/reports/2026-10-23_t02-f3-fixtures-fabio-v3-grid.md`.

### Bugs and assumptions

- B099: the out-of-sample pass hung in the first 2026-10-04 run and was re-run as a new trial row (`PRE_REG_FABIO_V3.md:41`, `:43`).
- B147: a note that the holdout was burned was corrected; the holdout step was not executed (status file above).
- Declared engine limits: `engine.run` returns the first leg only (adds not executed), Model B and Model A confirm IN_TRADE reported unmanaged at 0 R (`PRE_REG_FABIO_V3.md`, limits section near the top).
- Order-flow bars start 2024-12-02, after the development window, so the real run cannot go on the desk (`PLUGIN.md:44`).

### Confluence

- Stated as a standalone layer, "never a Tom filter" (`FABIO_V3_SPEC.md:6`).
- Cross-guidance matrix Q33: no cell recorded in `LAYERS.md:77-82`; read that block for the wording.
- Session logic reuses the New York calendar and `day_gates` (`PLUGIN.md:44`).

## fabio_of

Wired in the simulator: no (`PLUGIN.md:44`).

### Idea and source

- Fabio on true order flow: state -> location -> trigger -> management, replacing the fixed-horizon "every trigger fire" test of FABIO_L1 (`MyTradingSys/backtest/layers/fabio/FABIO_OF_REPORT.md`, intro after the notice; modules `orderflow_bars.py` and `fabio_of_model.py`).
- The report opens with a notice: "SUPERSEDED: this report used legacy fees ... and fixed UTC sessions (pre-B102). Its numbers are not reusable." (`FABIO_OF_REPORT.md:1-2`, commit `5212cdba2`, 2026-11-01).

### Parameters

- `TICK` 0.1 USD (line 34), `TOL` 0.001 (35), `BIN` 10 USD (36), `STATE_MIN` 15 minutes (37), `RETEST_BARS` 6 (38), `FILL_TF_BARS` 3 (39), sessions Asia 00:00-08:00, London 08:00-13:30, New York 13:30-21:00 UTC (44): all OURS / SIM in `MyTradingSys/backtest/layers/fabio/fabio_of_model.py` (lines resolved at this trunk). The docstring about DST shifts per B102 is in the same file (commit `325ce2adc`).
- Grid: timeframe {5m,15m}, big trade {99th, 99.9th}, k {1.5, 2.5}, entry {market, limit}, management {plain, trail}, minimum stop {1 tick, 0.15 %}: 64 true-flow and 32 proxy variants: OURS (`FABIO_OF_REPORT.md`, setup section).

### Backtests

- `FABIO_OF_REPORT.md`: Binance USD-M BTCUSDT aggTrades, 2026-06-01..2026-09-28, 120 days (line 16), in-sample 62 days, out-of-sample 28 days; legacy fee pair 3.5 bp taker / -1.5 bp maker rebate (lines 1-4), so the stated net values are not reusable.
- Results table `FABIO_OF_REPORT.md:63-70` region: balance_fade all sessions OOS n 29, exp net -0.498 R, PF 0.40; balance_fade NY n 22, -0.099 R; imb_break all n 37, -0.426 R; imb_break NY n 31, -0.265 R; combined all n 42, -0.428 R; combined NY n 16, -0.053 R. Verdict column in the file: "insufficient n" or "no edge". "0 of 64 variants net-positive OOS with n >= 30" (`FABIO_OF_REPORT.md:123`).

### Bugs and assumptions

- B081 residue: legacy fees (`FABIO_OF_REPORT.md:1-4`); a rerun is stated as needed before reuse.
- Fixed UTC sessions before B102; MSB swing audit #14 fixed in commit `051084e44` (2026-10-06).
- Only 28 out-of-sample days on one four-month window.

### Confluence

- Uses footprint levels (VAH, VAL, POC, LVN) for location and big-trade delta for direction.
- "Tom-with-Fabio agreement not computed (no offline Tom detector on these bars); Fabio stays a separate layer and must not gate Tom." (`FABIO_OF_REPORT.md:142`).

## session_momentum

Wired in the simulator: no. `PLUGIN.md:43` rates "Session levels / momentum, funding fade, big-trade fires" as "Small adapter, low value"; no study file exists.

### Idea and source

- Paper: "Shen, Urquhart, Wang, Financial Review 57(2), 319-344, 2022, DOI 10.1111/fire.12290 (T1): the first half-hour return predicts the last half-hour return" (`MyTradingSys/backtest/layers/FORMULAS.md:381`; docstring `MyTradingSys/backtest/layers/session/session_momentum.py:3`). Screen row: candidate C2 of the T055 proven-setups screen, `MyTradingSys/research/fast_track_2026-09-27/T055b_PROVEN_SETUPS.md:30`.
- Counter-evidence: `BTC_SESSION_EXTERNAL:88-90` reports reversal at hour scale (`MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:142`).
- Trader source: NOT_IN_DATA (academic origin, no trader ledger).

### Parameters

- SOURCED: market Binance USDT-M BTCUSDT perp (`FORMULAS.md:352`); taker cost 10 bps round trip (`FORMULAS.md:352`); side = sign of the first-window return (T055b:30, `LAYER_PROVENANCE_AUDIT.md:142`).
- OURS: slippage 2 bps round trip (`FORMULAS.md:353`); first window 30 minutes and entry at minute 30 (clock minutes, while the paper uses volume time: `LAYER_PROVENANCE_AUDIT.md:137-138`, `FORMULAS.md:366`); session anchor 00:00 UTC and 24 h length (`LAYER_PROVENANCE_AUDIT.md:139-140`); `min_abs` 0.0 (`LAYER_PROVENANCE_AUDIT.md:141`); base bar 5m (`T055_BT_c2.md:7`).

### Backtests

- Run 1 (2026-09-29), `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c2.md`: fee-net (10 bps + 2 bps + partial funding), 70/30 split of 498,240 1m bars. In-sample n 1,211, net -0.0759 %; out-of-sample n 519, gross -0.1792 %, net -0.2988 % (lines 11-12); verdict FAIL (line 3). Funding history covered 2025-09 onward only, so this run is marked superseded in the rerun (`T055_BT_RERUN_FULLFUNDING_2026-10-07.md:3`).
- Run 2 (2026-10-07), `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md`: full funding from 2020-01, fee-net. In-sample n 731, net +0.0999 %; out-of-sample n 299, gross +0.1358 %, net +0.0177 %, net Sharpe 0.0084 (lines 80-81); verdict FAIL against the 0.3 Sharpe mark (lines 14-15).
- Exit-policy run (2026-10-09), `MyTradingSys/research/bigtrade_2026-10-09/EXIT_POLICIES_REPORT.md:123-128`: six exit policies on 15m fires, assumed cost 12 bp; TRAIN 2022-01..2025-06 n 1,095, mean net -10.7 to -15.2 bp; VALIDATE 2025-07..2026-08 n 181, mean net -6.2 to -12.3 bp.

### Bugs and assumptions

- B102: fixed UTC session anchors, CLOSED (`BUGS.md:212`); the `session_momentum.py` latest commit is the B102 fix (`layer_index.json`, session_timing layer entry).
- Clock minutes against the paper's volume time; default enters for the rest of the day rather than the last half-hour (`LAYER_PROVENANCE_AUDIT.md:137-138`; `FORMULAS.md:376`).

### Confluence

- Standalone candidate C2, "never a filter on Tom core" (`FORMULAS.md:370-389` region; `T055b_PROVEN_SETUPS.md:30`).
- Lead draft class TRIGGER (OURS): `MyTradingSys/research/layer_review_2026-10-26/INTEGRATION_MAP.md:18-20`; "Nothing combines on a live trade ... no confluence rule has ever decided a real trade" (`INTEGRATION_MAP.md:8`).
- Wiring rows: `MyTradingSys/system/wiring_registry.json:966-968`.

## turn_of_candle

Wired in the simulator: no (not among the studies named in `PLUGIN.md:4`).

### Idea and source

- Paper: "Shanaev, Vasenin, Stepanov, Heliyon, PMC10015199 (T1): returns concentrate at the opening of 15-minute candles ... The paper has no cost model" (`FORMULAS.md:394`; `MyTradingSys/research/_archive/loose_2026-10/TURN_OF_CANDLE_ORIGIN_2026-10-09.md:9`).
- Preprint: Kim and Hansen, "The Quarter-Hour Effect", order imbalance in the opening window predicts returns over 4 to 12 hours (`TURN_OF_CANDLE_ORIGIN_2026-10-09.md:11`).
- Trader source: NOT_IN_DATA.

### Parameters

- SOURCED: 15-minute candle, turn at minute 0 of the quarter (T055b:51, `LAYER_PROVENANCE_AUDIT.md:152-153`); market and 10 bps taker as above.
- OURS: lead 1 or 2 minutes (`T055_BT_c3.md:9`, `LAYER_PROVENANCE_AUDIT.md:154`); backtest side long fixed ("direction of the effect is NOT stated", `FORMULAS.md:389` region); live testnet side = sign of the minute-0 taker imbalance under the operator 2026-09-30 sampling ruling (`LAYER_PROVENANCE_AUDIT.md:156`); hold 2 bars (`T055_BT_c3.md:9`); slippage 2 bps.

### Backtests

- Part 1 driver default, `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:9`: fee-net, 2,491,200 1m bars, 70/30. In-sample n 116,255, net -0.1183 %; out-of-sample n 49,823, gross -0.0000 %, net -0.1201 %, net Sharpe -1.49; both out-of-sample years negative. Label "NO EDGE" (line 3).
- Part 2 order-imbalance grid (48 variants, taker-buy-volume proxy), `T055_BT_c3.md:11-24`: out-of-sample net -0.1179 % to -0.1195 % at 1, 2 and 5 bars (n 40,857); 4h n 3,113 net -0.1058 %; 8h n 1,556 net -0.1353 %; 12h n 1,029 net -0.1310 %.
- Exit policies, `EXIT_POLICIES_REPORT.md:129-134` and `:144`: TRAIN n 105,199, VALIDATE n 17,376, mean net -11.1 to -11.9 bp; "the signal pays its fees and nothing else" (`EXIT_POLICIES_REPORT.md:144`).
- Kline-fire parity replay: 167,130 fires, timing parity 99.7 %, side parity 70.8 % (`MyTradingSys/research/bigtrade_2026-10-09/FIRES_B1_REPORT.md:31`); not a P&L run.

### Bugs and assumptions

- The layer was deployed to the live testnet about 3.5 hours after its backtest read "no edge", under the "sampling" ruling (`TURN_OF_CANDLE_ORIGIN_2026-10-09.md:18-25`); it made 300 of 372 testnet trades (`TURN_OF_CANDLE_ORIGIN_2026-10-09.md:28`).
- The preprint effect needs trade-level data over 4-12 h; the repo only had the kline taker-buy proxy (`T055_BT_c3.md:26`).
- The 2026-10-09 origin note and the testnet log are the only live record; no real-money trade exists (`INTEGRATION_MAP.md:8`).

### Confluence

- "Never a Tom filter (layer stays separate)" (`T055_BT_c3.md:31`).
- Lead draft class TRIGGER (OURS), `INTEGRATION_MAP.md:18-20`; wiring rows `wiring_registry.json:958-960`.

## session_levels

Wired in the simulator: no. The levels study that is plugged in (`PLUGIN.md:35`) is the separate `studies/levels.py`; session levels / momentum are rated "Small adapter, low value" (`PLUGIN.md:43`).

### Idea and source

- Origin: task T087, "Session-levels observation layer: MTS did not see today's failed first break of the prior-day high ... add session-levels layer + pre-reg backtest" (`MyTradingSys/research/BUGS.md:189`).
- Operator observation (2026-10-14): "a local low is set - then a retest - does not take it out so that longs build then on US session start - low broken! happens quite often! ... A valid back test must be established first" (`MyTradingSys/research/eur_low_us_sweep_2026-10-14/RESULT.md:3-6`).
- Trader source: NOT_IN_DATA (operator prompts, no external trader).

### Parameters

All OURS, "All clocks/thresholds NO-SOURCE" (`MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:3`, `:43`): fail window 60 minutes, stop = spike extreme, target = Asia or EU session extreme, time exit 14:00 UTC; US open anchor 13:30 UTC under US DST else 14:30 (`eur_low_us_sweep_2026-10-14/RESULT.md:12`); retest within 0.20 % of the 24h low, at least 2 h after, bounce at least 0.6 %; ladder 1-1-2-3 with adds at +0.4 %, +0.8 %, +1.2 % and stop at +1.6 %; taker 0.05 % per side, funding not modelled (`eur_low_us_sweep_2026-10-14/RESULT.md:9`).

### Backtests

- T087 base rates, BTCUSDT 1m 2022-01-01..2026-10-07 (913 days), net of 2 x 0.05 % taker (`t087_session_levels_2026-10-09/RESULT.md:1`, `:3`): pooled Asia-target both sides n 911, net mean -0.036 %, t -1.72 (line 15); EU target n 269, net -0.049 %, t -1.39; file labels "no edge" (lines 7-13). Base rate "57-67 %" retake of the spike high (line 40).
- EUR-low US-sweep, `eur_low_us_sweep_2026-10-14/RESULT.md`: DEV 2022-2024, VAL 2025, HOLDOUT 2026 (line 8), fee-net taker 0.05 %; retested weekdays n 99 against single-low weekdays n 1,027; short on retested days mean net -0.02 %, t -0.24 (lines 37-38). The 1-1-2-3 ladder mean net -0.02 %, t -0.32 (lines 40-42).
- Levels plus staged sizing probe, 120 UTC days 2024-12-02..2025-03-31, 117 paired signal days, all 8 variants negative after costs, mean net R -0.195 to -0.216 (`MyTradingSys/research/levels_sizing_2026-10-14/REPORT.md:5`, `:16`).
- EUR-low follow-ups, DEV only, VAL and HOLDOUT sealed: arm A n 133 (arms B 208, C 100), all three BLOCKED by the power gate (`MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/RESULT.md:3`, `:9-11`).

### Bugs and assumptions

- Retake share is geometric (stop a few ticks above entry, targets far below): "a base rate, not an edge" (`t087_session_levels_2026-10-09/RESULT.md:41`).
- First ladder script averaged P&L per filled unit, which overweighted winners (false +0.30 %, t 3.4); fixed before write-up (`eur_low_us_sweep_2026-10-14/RESULT.md:43-44` region).
- Distance and volatility confounds on the retest and the US-window break rate (`eur_low_us_sweep_2026-10-14/RESULT.md:22-33`).
- B187: price-level study blocked by the power gate on available DEV data, 662 days against 2,427 needed (`BUGS.md:302`).

### Confluence

- Intended to feed level context and trigger setups (`BUGS.md:189`); lead draft class DEAD (provisional, OURS) at `INTEGRATION_MAP.md:18-22`; "no confluence rule has ever decided a real trade" (`INTEGRATION_MAP.md:8`).
- Wiring row: `wiring_registry.json:149` (t087 probe).
