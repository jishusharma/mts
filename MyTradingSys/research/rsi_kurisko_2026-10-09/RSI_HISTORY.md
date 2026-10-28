# RSI line of work: what was planned, built, tested, and why it stopped (2026-10-09)

Operator ask: "What happened to RSI setups and research - it was stalled."
Method: every claim below cites a file I read in worktree `mts-rsi` (origin/fast-track 46ef159) or, for run
outputs and the trade ledger, the live tree read-only (`Dumps/backtest/runs/*`, `MyTradingSys/execution/trade_ledger.jsonl`;
both are gitignored runtime data). MATCH = stated by a file I read. NOT_IN_DATA = I looked and the file set has no answer.
Paths are relative to `MyTradingSys/` unless prefixed. `WR` = `research/malkan_rsi_2026-09-28/WEB_RESEARCH.md`.

## 1. Short answer

1. The RSI system is Vishal B Malkan's ("MalkanView") RSI 40/60 method. It was designed on 2026-09-28, fully built as an offline layer the same
   day, and wired to the live testnet runner on 2026-09-29. [MATCH: research/fast_track_2026-09-27/RSI_TF_LAYER_DESIGN.md; git log 4f74c20..0817968..4d1bc36]
2. What was backtested is NOT Malkan's actual 5-star setup. Every backtest used the project's generic 1% stop / 2% target / 100-bar bracket and a
   single-timeframe regime. The multi-timeframe "Grandfather-Father-Son" composer (`malkan_mtf`) has a backtest driver but no run exists on disk.
   [MATCH: LAYER_PROVENANCE_AUDIT.md:70-73; run_rsi_backtest.py:9-12; NOT_IN_DATA: no `rsi_malkan_mtf` folder in `Dumps/backtest/runs/`, listing: fabio_l1, fabio_l1_smoke, l1_2ee35b1e79, rsi_malkan_40_60, rsi_rsi_ma_events, t055_c1, t055_c1_1h, t055_c2, t055_c3_imb]
3. The tests that were run all came back "no edge" (numbers in section 4), so on 2026-10-06/07 the RSI work was closed as a verdict row, not as a
   finished investigation. Nobody holds an open item to finish it. [MATCH: MARKET_GUIDE_RESULTS_2026-10-07.md:20-22; scripts/dev/market_guide_verdicts.json:6; NOT_IN_DATA: no RSI/Malkan row in items/INDEX.md other than B128:93, which is only the rsi:cross side mapping]
4. Malkan's own words were never extracted. Three Malkan transcripts have sat in `raw_transcripts_canonical/` since 2026-09-28
   (`-CBvFi40sIQ`, `cQ-y1oULkBw`, `Wvq1TZh8aF0`, 7,954 + 16,777 + 39,058 bytes) but there is no `extracts/processed/malkan*` folder, and the
   provenance audit still lists "fetch a Malkan transcript" as an open question. [MATCH: `ls extracts/processed` = cryptocred, fabio_valentini; LAYER_PROVENANCE_AUDIT.md:206; research/fast_track_2026-09-27/NEXT_SESSION_PLAN.md:129 "No video extraction yet"]
5. Live, the RSI alerts keep firing and trade on the testnet, and 1h RSI is the only layer that reached targets. That is 4 trades, not evidence.
   [MATCH: trade_ledger.jsonl parse below; CONSOLIDATED_ROADMAP_2026-10-09.md:32]

## 2. Timeline

| Date | Event | Source |
|---|---|---|
| 2026-08-29 | "Malkans RSI 40/60 integrated" into the Tom chart layout (E4) | system/COMPILED_DECISIONS.md:40 |
| 2026-09-01 | VVP-001 demotes RSI: removed from default layout, "NEVER let RSI or BB override a Tom-validated setup" | research/_archive/loose_2026-10/visual_validation_protocol_vvp001.md:116,119; BUGS.md T019 (line 105) |
| 2026-09-28 | Operator directive (verbatim): Malkan 40-60 is private to its own sub-layer; RSI MA support; "slippage" tolerance around 40/60 to be measured; alerts per timeframe incl. 1,2,3,10 min and 2d,3d,5d; fine-tune later on testnet | PROJECT_VISION.md:189-203 |
| 2026-09-28 | Opus design D1-D7 (timeframe layer + rsi_core / rsi_ma / rsi_events / malkan_40_60) | research/fast_track_2026-09-27/RSI_TF_LAYER_DESIGN.md |
| 2026-09-28 | Web research on Malkan (secondary sources: eLearnMarkets blog, Chartink screeners, YouTube titles). 10 gaps listed | WR (400 lines) |
| 2026-09-28 | Built and committed: rsi_core + rsi_ma (d9eba41), rsi_events (77be7ef), malkan_40_60 (6bce07f), rsi_ma_events (13558c0), malkan_mtf (ae30eda), tolerance_sweep (8ea2f68), runner (d9f0d2a) | git log -- backtest/layers/rsi |
| 2026-09-28 | L1 backtest report (D3 tolerance study) | backtest/layers/BACKTEST_L1_REPORT.md |
| 2026-09-29 | Live runner: RSI-40 tol 0.5 on 1h/15m (0817968); malkan_bull / malkan_bear added (4d1bc36); failure-event side (adc75b3). 5m added 2026-09-30 (7058bc2) | NEXT_SESSION_PLAN.md:145; SUPERVISOR_LOG.md:185,221 |
| 2026-09-30 | Cloud Sonnet writes `run_rsi_backtest.py` (35 tests) with families malkan_40_60, malkan_mtf, rsi_ma_events | research/fast_track_2026-09-27/DSA_BACKLOG.md:23-24 |
| 2026-10-04 | Layer provenance audit: rsi = 4 SOURCED, 10 CONCEPT-ONLY, 12 NO-SOURCE | research/LAYER_PROVENANCE_AUDIT.md:46 |
| 2026-10-07 | Desktop runs malkan_40_60 and rsi_ma_events; both NO-EDGE. malkan_mtf not run. Verdict table written | research/_archive/loose_2026-10/MARKET_GUIDE_RESULTS_2026-10-07.md:20-22,36 |
| 2026-10-08 | Closeout: rsi:cross now side-by-level (40 down = short, 60 up = long, else no side); the trade blocklist is emptied for testnet data collection and parked | items/B128 row M29-11; research/_archive/loose_2026-10/AUDIT_CLOSEOUT_2026-10-07.md:53; execution/auto_trader_config.json:2,104-111 |
| 2026-10-09 | Volume study re-tests RSI 40/60 cross events with volume: one 4h DEV pass, failed VALIDATION (n=50, net -2 bp) | research/volume_2026-10-09/VOLUME_RESEARCH_REPORT_2026-10-09.md:96 |

## 3. What exists (built)

All under `backtest/layers/rsi/`: `rsi_core` (Wilder RSI, period 14), `rsi_ma` (SMA/EMA/RMA/WMA of RSI, default SMA 14), `rsi_events` (tolerance band
support / rejection / failure / cross), `malkan_40_60` (20-bar regime + bounce/reject setups, lo 40 / hi 60 / tolerance 2),
`malkan_mtf` (weekly+monthly regime gate on a daily entry), `rsi_ma_events`, `tolerance_sweep`, `run_rsi_backtest.py`, `observation.py`
(RSI block for the consensus writer, wired 2026-10-08, commit 2fccf66). Params with provenance: `params/default.json`,
`params/malkan_40_60_default.json`. Live detectors: `alerts/live_layers.py` (`rsi_level_layer` fixed at level 40, tol 0.5, lines 142-143;
`malkan_bull_layer` / `malkan_bear_layer`, lines 103-119).

## 4. What was tested, with numbers

| Test | Result | Source |
|---|---|---|
| D3 level-event tolerance study, BTCUSDT 1m 2022-01..2026-09-26 (2,491,200 bars), IS 70 / OOS 30, tolerance 0.5-5.0 | 8 cells (15m, 1h, 4h, 1d x level 40 long, 60 short). Only 1h / level-40 support / tol 0.5 has PBO 0.030 (OOS n 89, +0.043% mean h5, 56.2% hit). All other cells PBO 0.39-0.91. 15m: OOS mean near zero or negative | BACKTEST_L1_REPORT.md:16-25 (table), 28-32 |
| That one good cell vs cost | +0.043% gross OOS is below the 14 bp round-trip cost used elsewhere | MARKET_GUIDE_RESULTS_2026-10-07.md:20; SUPERVISOR_LOG.md:114 |
| malkan_40_60, 27 variants x 3 tf, bracket 1%/2%, taker 5 bp | 1h: OOS n 43, mean net -0.092%, hit 32.6%, PBO 0.760, no edge. 4h: OOS n 17, -0.203%, insufficient n. 1d: OOS n 5, insufficient n | `Dumps/backtest/runs/rsi_malkan_40_60/REPORT.md` (read) |
| rsi_ma_events, 24 variants x 2 tf | 1h: OOS n 357, -0.199% net, PBO 0.352. 4h: OOS n 69, -0.216%, PBO 0.455. Both no edge. 15m dropped after a 30-minute timeout | `Dumps/backtest/runs/rsi_rsi_ma_events/REPORT.md` (read) |
| malkan_mtf (5-star, 1M + 1w gate, 1d entry) | NOT_IN_DATA: driver exists (run_rsi_backtest.py:6,225-236,267), default tf 1d (line 272); no run output | see section 1 item 2 |
| Volume x RSI(14) cross 60 up / 40 down (V1 DEV, 4h) | RSI down-cross 40 with unconfirmed volume: pass on DEV (+70 bp net), then failed VALIDATION n=50, -2 bp [-68,+64] | VOLUME_RESEARCH_REPORT_2026-10-09.md:96 |
| Live testnet ledger (389 rows to 2026-10-09T08:08Z; I parsed the JSONL) | rsi_events 1h: 4 trades, 4 wins, +11.46 USD net. 15m: 11 rows, 6 wins, +2.44 (1 row has no P/L). 5m: 29 trades, 11 wins, +0.25. malkan_bull / malkan_bear: 0 ledger rows although accounts jishu_7 / jishu_8 are mapped (auto_trader_config.json:8-9). For scale, turn_of_candle 1m = 311 of 389 rows | `execution/trade_ledger.jsonl` (live tree, read-only) |

Note on the 1h live result: 4 trades are inside the noise. The backtest of the same cell (L1 report) shows +0.043% gross OOS, which does not
cover fees. These two facts do not contradict; neither is proof.

## 5. Where and why it stalled (quotes)

1. **The tests did not test Malkan.** The driver's bracket is its own: `LAYER_PROVENANCE_AUDIT.md:70-72` R21-R23: stop 1%, target 2%, time exit
   100 bars, all "NO-SOURCE", with "Malkan's target is an RSI level, not a price %." (line 71) Malkan's exit (WR:123 stop below signal-candle low, WR:128
   "Target is 60 RSI level on daily chart", WR:132-133 hold while monthly+weekly stay above 60) was never coded as an exit.
2. **The regime gate is a guess.** Audit R10-R11 (lines 59-60, CONCEPT-ONLY): "the second clause (max >= 60, min <= 40) has no quote", lookback 20 bars "no window in WR".
   R16 (line 65): the single-timeframe module gates on the entry timeframe's own regime, "WR:77 gates on Monthly + Weekly, not the entry TF"
   (self-documented as MLK-GAP1 in malkan_40_60.py:13-16).
3. **Grids were tuning, which the provenance rule forbids.** Audit R19-R20 (lines 68-69), R25 (line 74): period 10/14/21, tolerance, lookback, HTF lookback were swept; "Sweeping a sourced value (period) is tuning."
   Notes item 4 (lines 197-199): "these grids should not choose live values."
4. **Sample too small on the timeframes Malkan actually uses.** malkan_40_60 4h OOS n 17 and 1d OOS n 5 (REPORT.md above). Malkan's 5-star is a
   daily/weekly/monthly swing setup: WR:100-134 and the Samco transcript line 26-35 below. The live system, by contrast, fires on 5m/15m/1h
   (auto_trader_config.json:5-7), where Malkan gives no rule (WR gap 5: "No specific text found on crypto vs. equity differences").
5. **Malkan's own words were never read.** SUPERVISOR_LOG.md:47 "Malkan rules have no verbatim extract yet (only research/malkan_rsi_2026-09-28/WEB_RESEARCH.md; NUC 040 reply PARTIAL)";
   NEXT_SESSION_PLAN.md:129 "No video extraction yet"; audit Q1 (line 206) "fetch a Malkan transcript or page capture for period 14 (R01), the regime window (R11) and the band (R12)".
   The transcripts are in the repo already (see section 6). LAYER_PROVENANCE_AUDIT.md:191-193 (notes item 1) states: "no Malkan transcript or saved page is in the repo" - that is wrong as of
   commit 80b2edd (2026-09-28, "first Malkan transcript") and ba4a396.
6. **Priority moved.** From 2026-10-01 the roadmap centres on Tom core and Fabio ("two cores"); RSI is a sub-line there (ARCHITECTURE_TWO_CORES_2026-10-01.md:23,39,58). The 10-07 market-guide
   pass classified RSI as context: "None of them is a proven entry signal on our data" (MARKET_GUIDE_RESULTS_2026-10-07.md:32). The trade blocklist that stopped RSI-15m
   testnet trades was parked on 2026-10-08 for data collection (auto_trader_config.json:2,111). No owner or next step was recorded for RSI.
7. **Bookkeeping ambiguity** (does not change the verdict): the backlog line "never tested historically" (DSA_BACKLOG.md:23) was written 09-30, before the 10-07 runs; it is still unchecked for malkan_mtf.

## 6. What the repo's Malkan transcripts say (read 2026-10-09; not yet an extract, no quote-gate run)

Labels: T3 practitioner content. The Samco file is a third-party host (Apurva Sheth, Samco) explaining Malkan's strategy (header line 5: "third-party (Samco), secondary source").
The other two are Malkan's own channel, auto-captions (garbled in places). The files are single long lines, so line numbers apply only to the Samco file.

- Period and levels, Samco host: "you have 14 period RSI ... on monthly weekly and daily" (`-CBvFi40sIQ_raw.txt:26-27`); long = monthly RSI above 60, weekly above 60, "daily RSI i.e. 14 day RSI must be near 40" (lines 28-30); short = monthly below 40, weekly below 40, "daily RSI must be at around 60" (lines 42-44). This is the first transcript support for period 14 (audit R01 was CONCEPT-ONLY, WR:35 is a researcher bullet).
- Entry/stop, Samco host: entry "above the high of the signal candle", stop "below the low of the signal candle" (lines 34-35). No RSI-60 target is stated in this transcript; that target exists only in the eLearnMarkets blog quoted in WR:128 (secondary).
- Waiting: "So you have to wait patiently" (line 74) - said of the rarity of all three criteria lining up in the same stock.
- Malkan, `Wvq1TZh8aF0_raw.txt:8` (published 2026-04-15): "bearish below 40, bullish above 60, sideways between 40 and 60, so this is our fixed cut"; the most powerful divergence comes "near 60 bearish ... and near 40" bullish; seven-star = "RSI monthly is above 60 and then there is divergence in the daily".
- **Conflict with the repo:** WR "Setup 2: 7-Star" says 7-star = 5-star plus "Previous 3 consecutive days' RSI > 60" (Chartink screener text, secondary). Malkan's own video defines seven-star as monthly above 60 plus a daily divergence. The repo's WR version is wrong or screener-specific; it is unused in code (no 7-star module).
- Malkan, `cQ-y1oULkBw_raw.txt:8`: "shorter duration of number of divergences, the stronger the divergence" (3, 5, 7 bars; 15-40 bars "diluted completely").
- NOT_IN_DATA in all three files: any crypto or intraday rule, RSI-60 profit target, regime lookback window, tolerance around 40/60.

## 7. What is open now

| Open item | State |
|---|---|
| Extract Malkan transcripts through the quote gate (`verify_extract_quotes.py`) | not started; 3 files ready |
| Backtest malkan_mtf (1M + 1w gates, 1d entry) | driver written, no run |
| Code Malkan's own exit (signal-candle stop, RSI-60/40 target, HTF-hold) instead of 1%/2%/100 bars | audit Q2 is an "operator call", no answer recorded |
| Replace NO-SOURCE items R02-R05, R07, R19-R23, R25-R26 (remove or source) | no ticket found |
| Divergence (Malkan's core RSI edge per Wvq1TZh8aF0 and cQ-y1oULkBw) | not in code as an RSI-divergence layer; DIVERGENCE_AUDIT_AND_RESEARCH.md only lists it as "UNVERIFIED-WEB" |
| Daily/weekly/monthly RSI on BTC | data present (LAYER_READINESS.md:200-204 says monthly+weekly computable) |
| Live malkan_bull / malkan_bear produce 0 ledger trades | cause not investigated here |
| audit Q3 / Q4 (tolerance 0 invalid; HTF open-vs-close leak in `state_asof` doc) | driver passes close times (run_rsi_backtest.py:22-24); doc fix open |

Suggested order (cheapest tier first, not started): T0 extract the 3 transcripts; T2 one pre-registered backtest of the sourced rule only (5-star long/short on 1d with
the 1w+1M RSI gates, Malkan's stop/target/hold); T3 operator decision on audit Q2. Anything on 5m/15m stays "context, no rule".
