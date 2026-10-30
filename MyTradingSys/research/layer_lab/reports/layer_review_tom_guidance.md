# Layer review fact sheet: families tom and guidance

Card `layer-review-tom-guidance` (stream A, setup truth, D11_PROGRAMME.md). Built 2026-10-30 from the repo only. Starting point: `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/tom.md` and `guidance.md`; every file:line below was re-resolved against this tree (the Gemini line numbers were approximate). No verdict wording on any layer (operator NO 2026-10-25, `MyTradingSys/research/mts_doctor/MAINNET_PATH_2026-10-25.md:34`). Numbers are copied with their file:line, never recomputed. Labels: SOURCED = a trader quote is given; OURS = our choice, no trader quote found. NOT_IN_DATA = the repo is silent.

Layers (from `MyTradingSys/system/layer_index.json`): family tom = tom_core, tom_proofs, tom_vp_pivot (`MyTradingSys/system/layer_index.json:40`); family guidance = bb_lvn_triggers (`MyTradingSys/system/layer_index.json:198`).

Video quotes below are in the extract format (`> "quote"` then `**Source GPS: id | third**`) so `python scripts/dev/verify_extract_quotes.py` can check them against `raw_transcripts_canonical/`.

## tom_core

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md:39` lists Tom (BTC) as "Small adapter" (needs a time wrapper and a settings list) and Tom DAX as "Does not fit"; no `studies/tom*.py` exists.

### Idea and source

- Plain statement: "Fade an oversized push into thin volume when sellers show at the top (and his other setups later), on BTC charts with real order flow." (`MyTradingSys/system/layer_index.json:44`).
- Status text in the repo: "STOP: do not backtest or tune the current BTC encoding (tom_transfer ROADMAP section 2); being redefined as Tom v2" (`MyTradingSys/system/LAYERS.md:13`; the ROADMAP stop list is at `MyTradingSys/research/tom_transfer_2026-10-11/ROADMAP.md:21`).
- Code: `src/main/java/datafeed/SetupCandidatesBuilder.java` (candidate builder), thresholds in `MyTradingSys/backtest/verdict.py`: proof < 3 is WAIT_PROOF, proof < 5 is WATCH, else SETUP_FORMING (`MyTradingSys/backtest/verdict.py:121`).
- Tom, the idea / proof / risk frame (spec `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:52`):

> "First, you have an idea. Second, you have proof that it's really time now to implement the idea. And third, you have a really clean risk management"
**Source GPS: zQTbdEweG3c | BEGIN**
- recorded at `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:52` (transcript cite zQTbdEweG3c:28-32)

> "started way down here and then suddenly shot up just like a powerful rocket"
**Source GPS: T6hDJcHrVBM | MIDDLE**
- recorded at `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:59` (transcript cite T6hDJcHrVBM:114-116)

> "I can clearly see that there's no liquidity left"
**Source GPS: k0zm5NYn0IQ | BEGIN**
- recorded at `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:61` (transcript cite k0zm5NYn0IQ:21-22)

### Parameters

- Proof count to fire (`min_proof`): OURS. The spec says Tom gives no count: "Tom gives no count. The engine's "3 proofs" bar is NO-SOURCE for this family" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:66`). Engine thresholds 3 (WATCH) and 5 (SETUP_FORMING) are at `MyTradingSys/backtest/verdict.py:121`; the sensitivity arms are listed at `MyTradingSys/system/layer_map.json:18`.
- Stop at a fixed 20 DAX points when no reference exists above: SOURCED (DAX market only). Quotes: "For the first position, I'm setting a stop-loss of 20 points in the DAX" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:85`, transcript k0zm5NYn0IQ:22-24) and "The simple reason for this is that I don't have any reference values up here" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:94`, k0zm5NYn0IQ:24-26).
- Stop above the seller level / volume bell: SOURCED. Quotes: "my stop loss is immediately above the 258" and "the stop loss was set above the bell" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:93`, transcripts ujedEcmvBMk:67-68 and n7ZSkjb7JXs).
- Minimum reward to risk 1.5: SOURCED. Quote: "riskreward ratio of 1.5" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:28`, k0zm5NYn0IQ:549-552). The 1:6 on his one trade is a reading of that trade, not a rule: "In terms of riskreward ratio, we're currently at about 1:6" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:106`).
- Flat at 17:35 Berlin time (DAX session end): SOURCED. Quote: "present between 8:30, 9:00 and 17:35" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:121`, T6hDJcHrVBM:94-97).
- Time exit of 8 zone-timeframe bars, one trade at a time, limit entry at the zone price, stop and target from the rank-1 candidate: OURS (`MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md:9`).
- Minimum stop width for BTC, `W_min = max(W_noise, W_fee)` = 0.40 % (all-taker) or 0.20 % (Deribit maker entry): OURS, derived from fees and a noise unit, not from a Tom quote (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:318`, `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:323`).
- Fee model (base / all_taker_0.05 / slip_5bps / target_first), market (BTCUSDT or GER40), proof shift 0 to 3: OURS, listed as choices with source tag "code" (`MyTradingSys/system/layer_map.json:24`); shift above 0 is called an EXTENSION arm in `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:22`.
- Period split used by the reports: hist 2022-01..2025-08, dev 2025-09-01..2026-06-25, holdout 2026-06-26..2026-09-26 (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:20`).

### Backtests

Format per run: report path | fee-net | in-sample or out-of-sample | n trades.

1. TOM-CORE-0929 | `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md` (registry `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:3`) | fee-net yes: gross and net columns, Deribit-style fees (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6`) | the report says "Tom has no fitted parameter, so every period is out-of-sample" (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:20`); holdout 2026-06-26.. run once (same line) | live rule SETUP_FORMING: 19 signals, 17 filled (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6`; table row `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:34`); proof >= 3 sensitivity: 4417 filled, mean gross R -0.07 [-0.11, -0.03], mean net R -0.30 [-0.34, -0.25], holdout n = 254 net R -0.32 [-0.46, -0.18] (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6`).
2. TOM-CORE-1007 (run tom_core_20261007, current Java after the stop floor was removed) | `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md`; full text `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06_full.md` | fee-net yes: previous run mean net R -0.30, this run -2.91 [-4.35, -1.89]; gross -0.15 [-0.29, 0.04]; fee cost about 2.76 R per trade (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:18`) | same no-fitted-parameter statement; holdout net R -2.80 [-4.77, -0.75] (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:19`) | live rule filled trades 17 -> 0; proof >= 3 episodes filled 4417 -> 2880; holdout n = 181 (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:15`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:16`).
3. DAX-SMOKE (run dax_bt_20261010_SMOKE) | `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md` | fee-net yes: DAX under `FEES_FDAX` 0.000005 of price per side (`MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:22`) | development period only, DAX holdout NOT read (`MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:17`); the header says the numbers test the pipeline and are "NOT a result" (`MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:1`) | pre-registered shift 0: 0 signals, 0 filled in the listed variants (`MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:27`); extension arm s2 watch_episode: 367 signals, 309 filled, mean net R -0.53 [-0.79, -0.26] (`MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:32`); s3 watch_episode: 341 filled, -0.58 (`MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:36`). Scope wording differs inside the file: header says 2026-01 only (`MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:1`), section 1 says DAX dev = 2024-11-04..2026-04-10 (`MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:17`); not reconciled here.
4. TOM-DIAG-BTC | `MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md` | fee-net: runs `tom_bt.run_variant` with default fees (`MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md:9`); the GO/SKIP rules are stated on gross R and MFE (`MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md:13`), a net-R headline is NOT_IN_DATA in the file | hist 2022-01-20..2025-08-31 and dev 2025-09-01..2026-06-25; holdout excluded as burned (`MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md:8`) | watch_episode n = 2699, p4_episode n = 59 (`MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md:9`); session SKIP, selection SKIP, management GO with 40.0 % reaching 1R and 27.4 % reaching 2R (`MyTradingSys/research/tom_transfer_2026-10-11/DIAG_BTC.md:19`).
5. Tom v2 BTC lab cards after the stop: no outcome numbers. The event study report states "No outcome calculation, pytest run, or trial was performed" (`MyTradingSys/research/layer_lab/reports/2026-10-15_tom-btc-event-study.md:21`); the other-setups report begins "BLOCKED" (`MyTradingSys/research/layer_lab/reports/2026-10-22_tom-btc-other-setups.md:1`). Result numbers for Tom v2: NOT_IN_DATA.
6. Ledgers: `MyTradingSys/research/TRIAL_LEDGER.csv` and `MyTradingSys/research/VERDICTS.csv` hold no row for tom_core, tom_proofs, tom_vp_pivot or Q33 (grep for the layer and study names returned only other studies that read `tom_raw` klines): NOT_IN_DATA. The Tom core trial registry is `bt_runs/TRIAL_REGISTRY.csv` (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:3`).

### Bugs and assumptions

Rulings returned by `python scripts/dev/lab_query.py rulings tom` plus related BUGS.md ids (two are keyword hits not about a Tom layer):

- B147: Tom live-rule evidence unreliable: 0 SETUP_FORMING signals on rerun vs 19 before; holdout read twice (CLOSED, HIGH) (`MyTradingSys/research/BUGS.md:258`).
- B146: no minimum stop width after the 0.1 % floor was removed: median stop 0.082 %, fees dominate (CLOSED, HIGH) (`MyTradingSys/research/BUGS.md:257`).
- B116: unsourced 0.1 percent minimum stop floor and 0.2 percent fallback stop (CLOSED, MED); the 1007 rerun note ties its stop change to this floor (`MyTradingSys/research/BUGS.md:227`).
- B154: no regime-stratified and no session-stratified backtest verdict; every edge is one aggregate number (OPEN, MED) (`MyTradingSys/research/BUGS.md:266`).
- B131: proof-5 candidate pool skewed 215 short : 105 long (CLOSED, MED) (`MyTradingSys/research/BUGS.md:242`).
- B191: live-loop snapshot timeouts (CLOSED, MED): keyword hit, not about the layer (`MyTradingSys/research/BUGS.md:304`).
- B156: Tom alert card SSOT_THESIS stale text (CLOSED, MED): about the alert card, not the engine rules (`MyTradingSys/research/BUGS.md:269`).
- Assumption, historical snapshots: "the history has no book-imbalance/funding/OI proofs (max proof 6, SETUP_FORMING needs 5)" (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6`); book imbalance, funding, OI, basis and liquidation cannot be in historical snapshots (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:14`).
- Observation, not reconciled: the current builder counts at most five flags (rejection wick, absorption, finished auction, delta flip, cvd_aligned; volume spike, speed and book imbalance are emitted but not counted) (`src/main/java/datafeed/SetupCandidatesBuilder.java:619`), and in historical mode cvd_aligned stays false because there is no trade flow (`src/main/java/datafeed/SetupCandidatesBuilder.java:880`). The reports above state a ceiling of 6 (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6`). Which ceiling applied in each run: NOT_IN_DATA here.
- Assumption, the 0 vs 19 live-rule difference between runs: the rerun note lists the cause as open and says it "needs a diff of the verdict rows" (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:29`).
- Assumption, cadence: signals come from 15-minute snapshots, so a signal can be seen up to 15 minutes late; funding, basis, queue position and mark-price stops are not modelled (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:18`).
- Assumption, fee dominance: in the rerun the stops are very tight so R is tiny and fees cost about 2.76 R per trade; the report calls the change in net R "mechanical" (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:22`).

### Confluence

- Tom x Fabio kline detectors: tagged "DESCRIPTIVE, NOT A FILTER" (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:96`). Rows for the 17 filled live-rule trades: any Fabio detector within 4 bars TAGGED n = 3, mean net R 1.63 [0.45, 3.14]; not tagged n = 14, mean net R -0.57 [-1.05, 0.01] (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:111`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:112`). n < 30 in every row, copied as printed.
- Tom is never filtered by layers: the architecture test says "Tom core is never filtered by layers" (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md:10`), and the audit finds no Tom <-> Fabio signal path (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md:31`).
- Context indicators inside Tom (VWAP + bands, volume profile POC/VAH/VAL, HVN as targets, multi-timeframe zones): audit table rows `MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md:25`, `MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md:26`, `MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md:27`.
- Latest commit touching the layer: "Pitchfork Layer: Wire Modified Schiff tine bounce and Volume Profile confluence into SetupCandidatesBuilder" (commit 91d2e43c31, output of `python scripts/dev/lab_query.py layers tom`; no file:line, it is commit history).
- Wiring registry: `tom_bt_report.py` writes TOM_CORE_BT.md (`MyTradingSys/system/wiring_registry.json:197`); `tom_dax_bt.py` is a research driver run by hand (`MyTradingSys/system/wiring_registry.json:205`).
- Confirmed by the proof flags of tom_proofs: the proof count is the input to the verdict thresholds (`src/main/java/datafeed/SetupCandidatesBuilder.java:185`, `MyTradingSys/backtest/verdict.py:121`).

## tom_proofs

Wired in the simulator: no. Same row as tom_core: Tom (BTC) is a "Small adapter" and the proof flags are inside the Java builder (`MyTradingSys/research/sim_desk/PLUGIN.md:39`).

### Idea and source

- Layer text: "book_imbalance never counts in historical snapshots (no raw source); P06 volume spike is NO-SOURCE" (`MyTradingSys/system/LAYERS.md:14`). Flags: absorption, cvd_aligned, delta_flip, finished_auction, book_imbalance, volume spike (`MyTradingSys/system/layer_map.json:62`).
- Spec, section on proofs: list of observable proofs A-P1..A-P10 with no sourced count (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:64`).

> "If you make trades against the trend, then you need many, many parameters that speak in your favor"
**Source GPS: zQTbdEweG3c | BEGIN**
- recorded at `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:65` (transcript cite zQTbdEweG3c:23-26)

> "we also had a finished auction. That means the market formed a completed auction at the top"
**Source GPS: k0zm5NYn0IQ | BEGIN**
- recorded at `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:70` (transcript cite k0zm5NYn0IQ:84-86)

> "The market showed me that there is rejection up here"
**Source GPS: k0zm5NYn0IQ | END**
- recorded at `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:71` (transcript cite k0zm5NYn0IQ:469-473)

> "this lethargy was characterized by large sales volumes. And that prompted me to plan a short trade there"
**Source GPS: l8RZrBfzvp4 | BEGIN**
- recorded at `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:75` (transcript cite l8RZrBfzvp4:72-76)

> "a very large buyer here who is absorbing everything that's being sold"
**Source GPS: y67l86cSqb8 | MIDDLE**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:55` (transcript cite y67l86cSqb8_raw.txt:19 [TOM-025])

> "in the order book. There's nothing left"
**Source GPS: k0zm5NYn0IQ | MIDDLE**
- recorded at `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:78` (transcript cite k0zm5NYn0IQ:300-301)

### Parameters

What is counted: `src/main/java/datafeed/SetupCandidatesBuilder.java:619`. Counted: rejection wick, absorption, finished auction (only when the exhausted side is opposite the trade), delta flip at the zone, cvd_aligned. Emitted but not counted: volume spike (comment "B144 ... has no source (operator D17)"), speed (D4), book imbalance (B131).

- rejection_wick: concept SOURCED (A-P2 quote above). Numbers OURS: touch of the zone in the last 20 bars; quality STRONG when wick share > 0.8 and body share < 0.2 (`src/main/java/datafeed/SetupCandidatesBuilder.java:717`, `src/main/java/datafeed/SetupCandidatesBuilder.java:743`).
- absorption: concept SOURCED (TOM-025 quote above). Numbers OURS: bar volume > 2.0 x 20-bar average, range < 0.3 x ATR14, within 0.1 % of the zone, last 10 bars (`src/main/java/datafeed/SetupCandidatesBuilder.java:763`, `src/main/java/datafeed/SetupCandidatesBuilder.java:771`).
- finished_auction: concept SOURCED (A-P1 quote above). Numbers OURS: |delta| > 3.0 x the 20-bar mean |delta|, next bar reverses and has less than 0.5 x the delta (`src/main/java/datafeed/SetupCandidatesBuilder.java:789`, `src/main/java/datafeed/SetupCandidatesBuilder.java:792`). The spec notes aggressor data is needed (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:70`).
- delta_flip: OURS; no Tom quote located for the flip rule (the nearest sourced idea is A-P6 "in these last two candles we had a selling surplus", `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:75`). Flip within 0.1 % of the zone and nearest zone wins (`src/main/java/datafeed/SetupCandidatesBuilder.java:806`).
- cvd_aligned: OURS. The spec states CVD divergence "is not in these videos: NO-SOURCE for family A" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:183`). In historical mode it stays false (`src/main/java/datafeed/SetupCandidatesBuilder.java:880`).
- volume_spike (P06): OURS / NO-SOURCE, 2.0 x over 240 one-minute bars, not counted (`src/main/java/datafeed/SetupCandidatesBuilder.java:630`, `src/main/java/datafeed/SetupCandidatesBuilder.java:836`; BUGS `MyTradingSys/research/BUGS.md:255`).
- speed: OURS, not counted since D4 (`src/main/java/datafeed/SetupCandidatesBuilder.java:631`).
- book_imbalance: not counted; no history; concept appears as A-P9 (quote above). Reason in code: "no Tom source; ask-heavy side is far more common, so it" gave every short +1 and every long +0 (`src/main/java/datafeed/SetupCandidatesBuilder.java:633`).
- masked (matched-proof BTC arm hides absorption, cvd_aligned, delta_flip, finished_auction): OURS (`MyTradingSys/system/layer_map.json:67`).
- Proof count to fire: OURS, see tom_core.

### Backtests

No backtest isolates one proof flag. The runs that exercise the proof count:

1. TOM-CORE-0929 | `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md` | fee-net yes (net R columns) | no fitted parameter, so out-of-sample by the report's own statement (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:20`) | live rule (proof >= 5) 17 filled; proof >= 3 sensitivity 4417 filled (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:6`).
2. TOM-CORE-1007 | `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md` | fee-net yes | same statement; holdout n = 181 | 0 live-rule trades, 2880 proof >= 3 episodes (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:15`, `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT_RERUN_2026-10-06.md:16`).
3. DAX-SMOKE matched-proof BTC arm | `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md` | fee-net yes (Deribit fees on BTC) | development period 2025-09-01..2026-06-25 only; the holdout is burned (`MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:17`) | 1800 rows, mask changed 1818 candidates; the order-flow mask changed the proof count of 0 DAX candidates, expected 0 because the archive taker-buy is exactly half the volume (`MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:15`, `MyTradingSys/research/tom_transfer_2026-10-11/DAX_BT_REPORT.md:11`).
4. Per-proof outcome table: NOT_IN_DATA. The Tom core report has no table split by individual proof flag (its group tables are by period, setup type, zone timeframe and Fabio tag, e.g. `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:37`).

### Bugs and assumptions

- B131: proof-5 pool skew 215 short : 105 long; book_imbalance gave every short +1 and every long +0 (CLOSED, MED) (`MyTradingSys/research/BUGS.md:242`).
- B135: proof-count thresholds in start-trading-day.ps1 after book_imbalance left the count (CLOSED, LOW) (`MyTradingSys/research/BUGS.md:246`).
- B144: volume-spike exhaustion proxy (2.0x over 240 one-minute bars) is NO-SOURCE; tag SCREENER (OPEN, MED) (`MyTradingSys/research/BUGS.md:255`).
- B147: live-rule evidence unreliable: 0 vs 19 signals, holdout read twice (CLOSED, HIGH) (`MyTradingSys/research/BUGS.md:258`).
- B085: proof-5 pool skew unexplained after the book_imbalance fix; residual cause unverified (CLOSED, MED) (`MyTradingSys/research/BUGS.md:196`).
- Assumption: the historical snapshots have no raw source for book imbalance, funding, OI, basis or liquidation (`MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:14`).
- Assumption: absorption and delta need aggressor data; the DAX CFD feed has none: "Absorption and delta need aggressor data (not on the DAX CFD)" (`MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:184`).
- The observation about the counted-flag ceiling is written under tom_core (`src/main/java/datafeed/SetupCandidatesBuilder.java:619`).

### Confluence

- Feeds tom_core: the proof count is stored on each candidate and drives WAIT_PROOF / WATCH / SETUP_FORMING (`src/main/java/datafeed/SetupCandidatesBuilder.java:185`, `MyTradingSys/backtest/verdict.py:121`).
- Fabio detectors tagged on the same signals, descriptive only: `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:96`.
- The Fabio layer overlaps in concept (CVD, absorption); the sources say each trader already holds both layers: "No passage found where either trader names or endorses the other" (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:60`).
- Wiring registry entry for the proof pipeline report writer: `MyTradingSys/system/wiring_registry.json:197`.

## tom_vp_pivot

Wired in the simulator: no study for this layer. `vp_pivot_probe.build_profile` is reused inside the Pitchfork study (`MyTradingSys/research/sim_desk/PLUGIN.md:38`), but the anchored-touch study itself has no `studies/` file.

### Idea and source

- Layer text: "Anchored volume-profile touch (POC/VAH/VAL, pivot vs calendar anchors)"; status "closed: no anchor beats placebo" (`MyTradingSys/system/layer_map.json:81`). Module `backtest/vp_pivot_probe.py (FORMULAS 18)` (`MyTradingSys/backtest/layers/FORMULAS.md:415`).
- FORMULAS 18 states the source of the anchor: Tom draws a composite profile "from the last major high to the last major low" (`MyTradingSys/backtest/layers/FORMULAS.md:417`).

> "You don't need four or five years of data, just all the data from the last major high to the last major low"
**Source GPS: sQ_biBKhPVU | MIDDLE**
- recorded at `MyTradingSys/backtest/layers/FORMULAS.md:418` (transcript cite sQ_biBKhPVU:19)

> "this is the price range where the market was in equilibrium and where I then simply expect a reaction could occur"
**Source GPS: zQTbdEweG3c | END**
- recorded at `MyTradingSys/research/tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md:102` (transcript cite zQTbdEweG3c:191-195)

### Parameters

- Anchor: A1 pivot high to low is SOURCED (quote above); prior_day, weekly, prior_week and session anchors are OURS calendar anchors that mirror the engine (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:8`, `MyTradingSys/backtest/layers/FORMULAS.md:418`).
- Pivot width n in {2, 3, 5} on 1h bars: OURS / NO-SOURCE (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:25`, `MyTradingSys/system/layer_map.json:98`).
- Size filter k in {0, 2}: OURS / NO-SOURCE (same lines as above).
- Bin width 10 USD: OURS / NO-SOURCE; FORMULAS notes the engine uses about 5 USD (`MyTradingSys/backtest/layers/FORMULAS.md:422`).
- Barrier: R = ATR14(1h), barriers +-1R, timeout H = 48 x 5m bars: OURS / NO-SOURCE, "not tuned" (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:4`).
- Placebo level offsets 0.5 to 3 ATR: OURS (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:9`).
- Fees: taker 0.0005, maker 0.0002; bootstrap 2000 day-block resamples, seed 20261009: OURS (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:4`).
- Event bar: Tom's 300-event bar is used to flag small n (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:5`).

### Backtests

1. TOM-VP-PHASE2 | `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md` | fee-net yes: all 48 streams negative; taker mean net R -0.185 .. -0.248, maker variant -0.10 .. -0.16, gross about zero (-0.042 .. +0.010); fees about 0.19 R per round trip (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:10`, `MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:12`) | no fitted parameter; the whole span 2022-01-01..2026-10-07 is used with a 60-day warm-up (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:4`); no dev / holdout split is stated in the file: NOT_IN_DATA. The span runs past the 2026-06-26 holdout start named in `MyTradingSys/research/fast_track_2026-09-27/TOM_CORE_BT.md:20` | n >= 1055 per stream (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:17`); real minus placebo: 46 of 48 CIs straddle zero, two worse than placebo, none better (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:13`); every year 2022-2026 negative for every stream (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:15`).
2. VP-PIVOT-P2 | `MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md` | fee-net yes: net R taker 0.0005 and maker 0.0002 columns (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:4`) | whole series 2022-01-01..2026-10-07, 2000 day-block bootstrap (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:3`) | n by family and level, copied: session poc 9073 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:9`), session vah 7039 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:10`), session val 7328 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:11`), weekly poc 4661 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:12`), weekly vah 2876 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:13`), weekly val 2797 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:14`), prior_day poc 3598 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:15`), prior_day vah 3256 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:16`), prior_day val 3071 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:17`), prior_week poc 1304 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:18`), prior_week vah 1055 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:19`), prior_week val 1109 (`MyTradingSys/research/tom_core_bt_2026-10-09/phase2/results.md:20`); A1 and A2 pivot rows follow in the same table.
3. Side table R-5Ljf-7 (prior-day POC vs candle bodies): "this is a measurement, not a trade" (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:20`).
4. Bull / bear / sideways split: "not run: the phase labels have no source" (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:15`). Ledgers (TRIAL_LEDGER.csv, VERDICTS.csv): no row for this study, NOT_IN_DATA.

### Bugs and assumptions

- B154: no regime-stratified backtest verdict; every reported edge is one aggregate number (OPEN, MED; `MyTradingSys/research/BUGS.md:266`).
- B146 (stop width) is returned by `lab_query.py rulings tom` but concerns the Tom core stops, not the volume-profile probe (`MyTradingSys/research/BUGS.md:257`).
- Assumption: "NO-SOURCE choices in this run (flagged, not tuned): bin width 10 USD, pivot width n {2,3,5} on 1h, size filter k {0,2}, R = ATR14(1h), barriers +-1R, timeout H = 48 x 5m, placebo offsets. A different barrier/horizon was not tried on purpose." (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:25`).
- Assumption: the footprint and CVD confirmations Tom uses need aggTrades, "not on disk"; the touch alone carries no edge in this run (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:24`).
- Live profile versus probe profile: a separate check compares the live Java `buildVp` with `vp_pivot_probe.build_profile` on sampled DEV days (`MyTradingSys/system/wiring_registry.json:805`). Result of that check: NOT_IN_DATA here.

### Confluence

- Confirms or is confirmed by tom_core: NOT_IN_DATA (no repo line says the touch study feeds the core candidate builder; the core builds its own zones from the live profile, audit row `MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md:26`).
- Reused by other code: the `pit_levels` count-only pass imports `vp_pivot_probe.build_profile` (`MyTradingSys/system/wiring_registry.json:59`); the Pitchfork study wraps it (`MyTradingSys/research/sim_desk/PLUGIN.md:38`).
- Wiring registry: "Offline research script that regenerates research/tom_core_bt_2026-10-09/phase2/results.md (PHASE2_RESULT.md); run by hand, no live process imports it." (`MyTradingSys/system/wiring_registry.json:236`).
- Phase 2 note: any edge "must come from Tom's confirmations (footprint, finished auction, CVD)" (`MyTradingSys/research/tom_core_bt_2026-10-09/PHASE2_RESULT.md:24`).

## bb_lvn_triggers

Wired in the simulator: no. `MyTradingSys/research/sim_desk/PLUGIN.md:44` lists "Detectors and studies (volume, candle patterns, guidance matrix, callers)" as "Does not fit" (they flag events, no trades).

### Idea and source

- Layer text: "Triggers T1 BB-outside, T2 LVN traverse, T3 hold/through, T4 x context filters"; family text "Cross-guidance filters (Bollinger, LVN, regime) stacked on Tom/Fabio triggers." (`MyTradingSys/system/layer_map.json:584`, `MyTradingSys/system/layer_index.json:200`).
- Source file for the quotes: `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md` (Q32). The file says the saffron sentence "Price moves fast through prices where nobody wants to trade" is the narrator's, "Neither trader says it" (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:9`). Bollinger bands, RSI, squeeze, OI, long/short ratio and funding are NO-SOURCE for Tom and Fabio (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:40`).

- S1 Tom, LVN bounce:

> "these price areas are zones with very low volume for the respective time frame we're looking at. And the market often bounces off these areas."
**Source GPS: YmygDgtoxO8 | MIDDLE**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:16` (transcript cite YmygDgtoxO8_raw.txt:19 [TOM-210])

- S2 Tom, LVN fills with liquidity:

> "we're in the low volume area. That means it's doing nothing other than filling this empty price area with liquidity now."
**Source GPS: 4MoNjEQ2Dd8 | MIDDLE**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:17` (transcript cite 4MoNjEQ2Dd8_raw.txt:19 [TOM-211])

- S3 Tom, fair value gap:

> "This creates a space where the market was ultimately traded quickly and aggressively."
**Source GPS: Fj4FDZQxw0I | BEGIN**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:18` (transcript cite Fj4FDZQxw0I_raw.txt:19)

- S4 Tom, single print:

> "single print areas are in reality nothing more than specific price ranges where the market never actually retraced within this particular move"
**Source GPS: Fj4FDZQxw0I | MIDDLE**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:19` (transcript cite Fj4FDZQxw0I_raw.txt:19 [TOM-202])

- S5 Tom, gaps need trend stability (first part):

> "fair value gaps are great support resistance levels. They are, but only if the market has trend stability."
**Source GPS: Fj4FDZQxw0I | BEGIN**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:20` (transcript cite Fj4FDZQxw0I_raw.txt:8 [TOM-204])

- S5 Tom, gaps traded through (second part):

> "volatile fair value gap in a sideways phase. And if liquidity up here isn't high, then there's a good chance it'll just be traded through."
**Source GPS: Fj4FDZQxw0I | END**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:20` (transcript cite Fj4FDZQxw0I_raw.txt:19 [TOM-209])

- S6 Tom, unhealthy trend:

> "this trend isn't entirely healthy."
**Source GPS: zQTbdEweG3c | END**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:21` (transcript cite zQTbdEweG3c_raw.txt:19 [TOM-056])

- S6 Tom, liquidity left behind:

> "there was simply no liquidity left here and the liquidity was down here. That means low volume."
**Source GPS: zQTbdEweG3c | END**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:21` (transcript cite zQTbdEweG3c_raw.txt:19 [TOM-140])

- S7 Tom, Bollinger outside and volume (a):

> "we gain an advantage because this allows us to see whether a market is supported by volume. Only then does it make sense to trade in that direction."
**Source GPS: 4VXpUjhKG2U | BEGIN**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:22` (transcript cite 4VXpUjhKG2U_raw.txt:7)

- S7 Tom, Bollinger outside and volume (b):

> "But now trading volumes are surging outward"
**Source GPS: 4VXpUjhKG2U | MIDDLE**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:22` (transcript cite 4VXpUjhKG2U_raw.txt:7)

- S7 Tom, Bollinger outside and volume (c):

> "then the market certainly won't return to that Ballinger band range quickly and definitely not within the same day."
**Source GPS: 4VXpUjhKG2U | MIDDLE**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:22` (transcript cite 4VXpUjhKG2U_raw.txt:7)

- S8 Tom, method order:

> "how we connect the dynamic context and then use the order flow to get the timing right."
**Source GPS: -dMWA_bbm3o | BEGIN**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:23` (transcript cite -dMWA_bbm3o_raw.txt:7)

- S9 Tom, narrow opening range:

> "if something is very narrow, but liquidity is the same as in the previous days, then the probability at a later point in time is much greater that the market will trend."
**Source GPS: Ld1dhjGdTCA | END**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:24` (transcript cite Ld1dhjGdTCA_raw.txt:19 [TOM-212])

- S10 Tom, VWAP side:

> "they're initially more bearishly inclined"
**Source GPS: 43JaKHRvxHk | MIDDLE**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:25` (transcript cite 43JaKHRvxHk_raw.txt:19 [TOM-049])

- S11 Fabio, fast move into an empty level:

> "If they squeeze this one on the top and they reach this one, probably, with high probability, they will go for a fast move all the way up because, as you can see, this level is pretty empty"
**Source GPS: FawPrRUGNpk | MIDDLE**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:26` (transcript cite FawPrRUGNpk_raw.txt:770-776)

- S12 Fabio, sweeps:

> "when you have a book sweeping, a fast movement."
**Source GPS: FawPrRUGNpk | BEGIN**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:27` (transcript cite FawPrRUGNpk_raw.txt:253)

- S13 Fabio, CVD read:

> "see what the CVD is telling us"
**Source GPS: FawPrRUGNpk | END**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:28` (transcript cite FawPrRUGNpk_raw.txt:1048)

- S13 Fabio, value area low target:

> "reaching the value area low"
**Source GPS: 8CWKfoSJu3c | MIDDLE**
- recorded at `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:28` (transcript cite 8CWKfoSJu3c_raw.txt:141)

- S14 (Fabio, hidden pressure inside balance) has no verbatim quote in the source table; it points to `MyTradingSys/research/fast_track_2026-09-27/FABIO_TRADE_MODEL.md:9-40` (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:29`).

### Parameters

Rule: "Every numeric threshold (percentiles, windows, 1.5x volume) | NO-SOURCE. They are grid values, counted in the FDR family, never tuned." (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:48`). So every number below is OURS.

- Concepts SOURCED: LVN bounce / fill (S1, S2), gap and single print (S3-S5), unhealthy trend (S6), Bollinger outside needs volume (S7), VWAP side (S10), CVD direction (S13). Quotes above; table `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:16`.
- Evaluation grid: 15m bars resampled from 1m, decision at close of bar t, entry open of t+1; horizons H = 1, 4, 16 bars; primary H = 4 (60 min); cooldown 4 bars: OURS (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:19`; code `MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py:18`, `MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py:19`, `MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py:20`).
- T1 Bollinger BB(20,2) on 15m close, population standard deviation: OURS; Bollinger is NO-SOURCE as a trigger (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:21`, `MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:43`).
- T2/T2b LVN from the prior-UTC-day profile of 1m closes, bin = ATR(14,1h)/10, 3-bin smoothing, HVN = local max >= median of non-empty bins, LVN run <= 0.5 x median between two HVNs; traverse within <= 2 bars; reject = wick >= 1 bin and close back: OURS (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:21`). The 1h ATR is replaced by 2 x ATR(14, 15m) (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:41`).
- T3/T3b 15m 3-bar fair value gap, unfilled <= 96 bars, first test and second test: OURS (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:22`).
- T4 sweep-void: break of the 16-bar prior high/low with close beyond, next prior-day HVN >= 1.0 x ATR(14,15m) away, CVD agrees: OURS (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:23`).
- Filters F1 (VWAP side, weekly POC migration, EMA20 4h slope; majority of 3), F2 RSI(14) Wilder <40 / 40-60 / >60 (labelled Malkan, NO-SOURCE for Tom/Fabio), F3 2-bar CVD delta z-score +-1 over 30 days, F7 BB-width percentile over 672 bars (<=20 squeeze, >=80 expanded), F8 relative volume >= 1.5 with CVD agreement: all OURS (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:24`; code constants `MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py:110`, `MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py:99`).
- VWAP anchored at 00:00 UTC for the side test: OURS (convention); S10 only sources "VWAP side sets the bias" (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:24`).
- Weekly POC migration sign: NOT_IN_DATA as a Tom quote (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:24` is a different rule: S9 compression).
- F4 open interest, F5 long/short ratio, F6 funding: not run, NOT_IN_DATA on the machine (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:8`, `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:37`).
- Cost: `FEES_ALL_TAKER`, both legs taker, 0.10 % round turn, no stop or target, market entry at the next bar open, exit at the close H bars later (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:10`, `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:5`).

### Backtests

Q33 matrix | report `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md` (cells `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_CELLS.csv`, summary `MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_SUMMARY.json`, runner `MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py`) | fee-net yes: 0.10 % taker round turn (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:5`) | event study, not a trade backtest; no holdout held out; first-half / second-half means per cell (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/PRE_REG_Q33.md:15`). The pre-registration names the halves 2022-2024 and 2025-2026 while the runner splits at the middle bar index (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/matrix_q33.py:266`); both cited, not reconciled | n: see below.

- Data: BTCUSDT perp 1m klines 2022-01-01..2026-10-11, 2,512,800 bars, 0 gaps, resampled to 15m (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:4`).
- Cells: "336 cells were built, 186 had n >= 300 and were tested at the primary horizon (60 min), 89 were underpowered (n 20-299, reported, not judged), the rest had n < 20" (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:8`).
- Survivors (n >= 300, BH-FDR q <= 0.05 on placebo p, net mean > 0, same sign in both halves): 0; smallest q 0.62 (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:9`).
- Events per baseline trigger (all-filter net mean at 60 min, long / short): T1 continuation 8,689, -0.091 % / -0.103 % (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:14`); T1 fade 8,689, -0.097 % / -0.109 % (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:15`); T2 traverse 1,491, -0.104 % / -0.115 % (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:16`); T2b reject 1,275, -0.102 % / -0.114 % (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:17`); T3 first test 19,282, -0.090 % / -0.093 % (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:18`); T3b through 8,427, -0.109 % / -0.100 % (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:19`); T4 sweep-void 1,870, -0.102 % / -0.097 % (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:20`).
- Median gross edge across the 186 tested cells at 60 min +0.0003 %; 0 of 186 cells positive net at 60 min; 3 positive at 240 min, best +0.039 % on `T3b_through short` (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:22`). The p 0.038, q 0.62 and half means -0.034 % / -0.071 % printed for that cell are the primary 60-minute statistics; whether the 240-minute result is significant or stable is NOT_IN_DATA (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:24`).
- Sparse-cell count (n < 20) is not printed in the report: NOT_IN_DATA. Ledgers: TRIAL_LEDGER.csv and VERDICTS.csv hold no Q33 row, NOT_IN_DATA.
- Not run: T4b sweep reject and T5/T6 frozen Tom / Fabio events (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:38`).

### Bugs and assumptions

- Rulings returned by `lab_query.py rulings guidance` are keyword hits on the word "guidance" and do not concern this layer: B172 (Sonnet ritual token use, `MyTradingSys/research/BUGS.md:286`) and B105 (deflated-sharpe unit note, `MyTradingSys/research/BUGS.md:216`). A BUGS.md row for Q33 or matrix_q33: NOT_IN_DATA (grep).
- Limits stated by the report (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:36`): (1) F4/F5/F6 not run; (2) T4b and T5/T6 not run so the Tom / Fabio agreement tag is not reported; (3) detection on 15m closes, a 1m re-run with stops/targets and maker entry is described as the one branch not excluded; (4) 1h ATR replaced by 2 x ATR(14,15m); (5) taker both ways is the pessimistic cost; (6) placebo p-values have resolution 0.001.
- Assumption: "It is not a verdict on Tom's or Fabio's own trades: their edge is management (breakeven, add, trail, 1:5 to 1:19 winners), which a fixed-horizon forward return cannot show." (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:33`).
- Assumption: Bollinger-band outside moves are a case Tom names as a trap; the band cannot say which side (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:35`).
- Code audit gap list (2026-10-12): no Tom <-> Fabio signal path; Tom core may not be filtered by layers; no Bollinger bands, RSI 40-60 regime or volatility squeeze state anywhere in the code; OI and long/short exist in the snapshot but are not tested as filters; Tom uses HVNs, not LVNs (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md:31`).

### Confluence

- Designed role: context filters and triggers stacked on the Tom and Fabio setups; the sources say Tom uses context first and order flow for timing (S8) and Fabio uses profile concepts then CVD (S13) (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/SOURCED_RULES.md:51`).
- In the code the two cores do not read each other: "Answer: NO. They are wired to run side by side, never to read or gate each other." (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md:3`).
- Layer boundary test: layers are alert-only, "Tom core is never filtered by layers" (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md:10`); the consensus hook is observation-only (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md:9`).
- Backtest result for the stacked filters: no cell survives (smallest q 0.62), so the Q34 wiring step is recorded as skipped: "Skip: no combination survived." (`MyTradingSys/research/tom_fabio_guidance_2026-10-12/MATRIX_REPORT.md:47`; layer_index status `MyTradingSys/system/layer_index.json:182`).
- Wiring registry: `matrix_q33.py` is an offline REPRO script that reproduces MATRIX_REPORT.md (`MyTradingSys/system/wiring_registry.json:516`).
