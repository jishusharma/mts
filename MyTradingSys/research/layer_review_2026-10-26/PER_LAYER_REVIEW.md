# Per-layer review: 13 families (Fable, 2026-10-26; corrected 2026-10-27)

Task: for each of the 13 layer families, fill the a-h fields using `LAYER_SHEETS.md`
(commit cb903f9d, 2026-10-26) as the starting point and `FABLE_LAYER_REVIEW_RUBRIC.md`
(commit dd3f311c1, 2026-10-26) as the evaluation structure. Research-only: no layer is
kept, dropped, demoted, parked or wired by this file; it records what the repo says and
what the simulator can currently show. Standing operator rule 2026-10-25: no layer is
dropped before it has been seen in the simulator, so every family gets a (g) simulator
line. For the 8 NOT_IN_DATA families the numbers are not invented; the gate is named.

Field key per layer:
- (a) idea, one line.
- (b) source, every parameter/claim labelled SOURCED (trader file, cited) vs OURS vs NO-SOURCE.
- (c) what the backtest shows: exact number + window (DEV/VALIDATION/HOLDOUT) + n trades + fee-net vs gross.
- (d) known bugs/errors from the sheet (`LAYER_SHEETS.md` Errors column) and the simulator (planted-edge, CI).
- (e) assumptions: data window, one asset BTC 1m, sealed splits, no walk-forward by design.
- (f) combines-with / confluence per `FABLE_CONFLUENCE_MAP.md`.
- (g) whether the simulator can show it: covered / partial / NOT_IN_DATA per the argon matrix
  (`argon_sim_layer_coverage.md`, commit 0f9e76065); if NOT_IN_DATA, what would take it there.
- (h) one-line verdict against the rubric: proven / promising / NOT ENOUGH DATA, with the
  95% range where the desk computed one. Rubric verdict words are PASSED/FAILED/NOT ENOUGH DATA;
  "FAILED" below is the h-field shorthand for a rubric FAILED.

Conventions: "R" is one stopped-out risk unit. DEV = 2022-04-01..2024-06-30 (some reports
carry 2022-01-01..2024-06-30, noted where it matters). VALIDATION is read once, then sealed;
HOLDOUT sealed. No walk-forward by design (one fixed split). One asset: BTC 1m bars (desk
fills on 1m even when the signal is a higher TF; ETH/SOL 1m not yet on disk).

## 1. tom (Order flow + volume profile)
- (a) Order flow + volume profile; Tom v2 being redefined.
- (b) Source: `TOM_LAYER_V2_SPEC.md`, `SOURCED_RULES.md`, `TOM_VERBATIM_INDEX.md`. Provenance
  (`fast_track_2026-09-27/PROVENANCE_AUDIT_TOM.md`, authored 5f816ae12 2026-09-30, counts
  updated through aaf007a5b 2026-10-08): 2 TOM-SOURCED / 34 TOM-CONCEPT-ONLY / 35 NO-SOURCE /
  3 plumbing, 74 rows (table PROVENANCE_AUDIT_TOM.md:11-15). Only the 70% value area is
  TOM-SOURCED; stop floor, fallback stop, target window, net R:R gate, proof bands, book veto,
  distance caps, below-VAL rule are NO-SOURCE. book_imbalance never counts in historical
  snapshots; P06 volume spike NO-SOURCE. Counts NOT_IN_DATA.
- (c) `TOM-CORE-0929` (created 5831eadd7 2026-09-30; relocated to _archive by f8d0799de
  2026-10-26): net -0.30 R [95% -0.34..-0.25], holdout -0.32 R [-0.46..-0.18] n=254, gross
  -0.07 R; window 4.7y BTCUSDT 1m, fee-net (Deribit-style fees; tight stops make fees ~0.23 R/
  trade). `TOM-CORE-1007` (report commit 36a114939, 2026-10-07): net -2.91 R [-4.35..-1.89],
  holdout -2.80 R [-4.77..-0.75] n=181, gross -0.15 R; mechanical -2.9 R is from PR #12
  removing the 0.1% stop floor (B116) so R is tiny and fees cost ~2.76 R/trade. VP anchors:
  46/48 real-minus-placebo CIs straddle 0 (L19).
- (d) B146, B147, B131, B085, B084 (BACKTEST_ERRORS part 1, commit a50ff56bd, 2026-10-26): B146 no
  minimum stop width (median stop 0.082%, planned gross R:R 79, fees dominate); B147 live-rule
  evidence unreliable (0 signals vs 19 earlier; holdout read twice; Oct-7 run not on HEAD); B131/B085
  proof-5 pool skews 215 short : 105 long; B084 book_imbalance 0.0 origin unverified.
- (e) BTC 1m; sealed splits; no walk-forward. The 1007/0929 windows span beyond the protocol DEV
  (hist 2022-01..2025-08, holdout 2026-06-26..) - noted, these are out-of-protocol OOS reads.
- (f) Combines: fabio (order flow), guidance (its triggers), shared CVD rows (`PRICE-CVD-DIV-1M5M`).
- (g) partial / NOT_IN_DATA for the order-flow core. No standalone tom study in `studies/*.py`
  (`PLUGIN.md` "Tom DAX: Does not fit"). Only 4 TOM-sourced daily level families are routed via
  `studies/levels.py` (prior_day high/low/poc, naked_poc). To make it covered: wrap
  `backtest/tom_bt.py` (footprint/order-flow bars exist on JIS-NUC from 2024-12, after the DEV
  window) in a study file.
- (h) FAILED - net -0.30 R, holdout -0.32 R n=254, both fee-net, at-or-below-zero gross; the
  simulator cannot currently show the order-flow core (g partial).

## 2. fabio (Order-flow layer)
- (a) Order-flow pressure and absorption at the NY open; v3 OOS FAIL, being redefined as v2.
- (b) Source: `FABIO_V3_SPEC.md`, `FABIO_RULEBOOK.md` (report commits efa186306 2026-09-29 /
  02fc346f0 2026-09-30). Legacy fee pair on fabio_of. Counts NOT_IN_DATA. The stop for the
  extra setups (B142) is the previous 1m bar high/low with no trader source (NO-SOURCE).
- (c) FABIO-V3 OOS FAIL: 79 trades, mean -0.1038 R, only model C evaluable (fee-net, OOS);
  holdout 2026-06-26.. NOT read for Fabio (B147). L1-FABIO (report commit efa186306 2026-09-29):
  no edge / insufficient n (rule OOS n>=30, net>0, PBO<0.5). FABIO-OF: no edge / insufficient n,
  "numbers not reusable" under correct fees. CVD divergence adds nothing over price alone on
  1m/5m (`orderflow_views_2026-10-14/RESULT.md`, commit 26c6f3a83 2026-10-17).
- (d) B142 (extra-setup stop NO-SOURCE), B039, T09 F1/F4 (side inverted 0/24; live 99-bar window
  misses 68 of 96 escalation signals, `LAYER_REALITY:8`).
- (e) BTC 1m footprint/aggressor side; sealed splits; no walk-forward. Order-flow bars start
  2024-12-02, after the desk DEV window, so most fabio encodings predate the desk data.
- (f) Combines: tom (order flow), guidance filters stacked on its triggers; CVD rows shared with
  positioning.
- (g) NOT_IN_DATA for all 5 order-flow layers (`PLUGIN.md` "Fabio order flow v3: Does not fit yet");
  only 4h fractal high/low are pooled in `studies/levels.py`. To make it covered: ETH/SOL 1m fetch
  and order-flow bars before 2024-12, plus a fabio study file.
- (h) FAILED - v3 OOS -0.1038 R n=79 fee-net, L1 no edge / insufficient n; simulator cannot show
  the order-flow encodings (g NOT_IN_DATA).

## 3. guidance (Tom/Fabio cross-guidance)
- (a) Cross-guidance filters: Bollinger bands, LVN, regime, stacked on Tom/Fabio trigger events.
- (b) Source: `GUIDANCE_AUDIT.md`, `PRE_REG_Q33.md`. Parameters NOT_IN_DATA (no per-parameter
  provenance row).
- (c) Q33 (`MATRIX_REPORT.md`, commit 72c2090ef 2026-10-12): 336 cells built, 186 had n>=300 and
  were tested at the 60-min primary horizon, 89 passed n; 0 cell survives (net mean > 0, same sign
  in both halves), smallest q 0.62 - gross screen (no fee-net claim); "do not wire cross-guidance"
  (Q34 skipped).
- (d) none recorded in the sheet's Errors column.
- (e) DEV window; event-driven filters on top of trigger families; sealed splits; no walk-forward.
- (f) Its inputs ARE tom and fabio triggers + BB/LVN/regime levels; it is the filter that would
  gate them. Overlaps the levels family (bb_top_reversal, rsi, volume, candle joined in the pre-reg
  pool, PRE_REG_CONFLUENCE s3.4).
- (g) NOT_IN_DATA (`PLUGIN.md` "guidance matrix: Does not fit"; `matrix_q33.py` not imported in any
  `studies/*.py`; only the E4 "outer Bollinger band" flag is exposed on 5m bars via
  `studies/levels.py`). To make it covered: route `matrix_q33.py` cells through a study file.
- (h) FAILED - 0 of 336 cells survives (smallest q 0.62), gross screen; simulator cannot show it
  (g NOT_IN_DATA).

## 4. rsi (RSI 40/60 / Malkan / Kurisko)
- (a) RSI 40/60 levels (Malkan), RSI divergence, Kurisko quad rotation.
- (b) Source: `KURISKO_SPEC.md`, `FORMULAS.md`, Malkan blog/Chartink text (WR). Provenance
  (`research/LAYER_PROVENANCE_AUDIT.md`, authored 9b76e716f 2026-10-04; touched by f8d0799de
  2026-10-26) rsi row (LAYER_PROVENANCE_AUDIT.md:46): 4 SOURCED / 10 CONCEPT-ONLY /
  12 NO-SOURCE, 26 rows. SOURCED = levels 40/60 (WR:45) and green/red entry candle (WR:77,144). No
  sourced exit (stop 1%, target 2%, 100-bar time exit are NO-SOURCE, R21-R23). Kurisko stop is the
  pattern-low minus 1 tick (SOURCED) but "skip if stop distance < 14 bp round trip" is OURS; exact
  stochastic smoothing and numeric turn-up are OPEN/OURS.
- (c) L1-D3 (`BACKTEST_L1_REPORT.md`): only 1h / level-40 support, tol 0.5, clears the PBO bar,
  PBO 0.030 (IS n 193, OOS n 89 h5 mean +0.043% / hit 56.2%); every other cell PBO 0.39-0.91.
  RSI-DIV-MTF (`research/rsi_divergence_mtf_2026-10-09/RESULT.md`, created 1157dbe6c 2026-10-09,
  amended 0aa8f5644 2026-10-09): 31 of 32 net negative after a 0.10% taker round trip; 32 cells
  >= 300 events (1m-1h except 1h operator bullish at 277, plus 2h Malkan bearish 301); 6h/2d
  leads have n 6-54. Sim-desk trial `TRIALS.md:274` (row dated 2026-10-21, added by 2b80ef52b
  2026-10-21): rsi 1d BREAK RSI 60/40 band 2 trend 20, fee-net, n 2 filled (3 never filled), mean
  net R -1.036 [-1.042,-1.030]. `TRIALS.md:282` rsi-deep-prob-tables (added by 28565f801
  2026-10-26): the only rsi trial that read VALIDATION (2024-07..2025-06 read once; HOLDOUT
  refused by the loader).
- (d) T09 F3 (live event set differs - live trades 384 of 461 events on 5m, not covered by the
  tested set, `LAYER_REALITY:10`); provenance exit NO-SOURCE; Kurisko stop too narrow for the 14 bp
  round trip (fee 2.1-2.3 R on 1m, 0.60-0.79 R on 5m, `LAYER_REALITY:12`).
- (e) BTC 1m/1h/4h/1d/4h multi-TF; sealed splits; no walk-forward. Malkan's own reads gate on
  Monthly+Weekly RSI value, code uses the 20-bar regime (MLK-GAP1, CONCEPT-ONLY).
- (f) Combines: krown regime (RSI 40/60 as confirmation, same-object pair), PRE_REG_CONFLUENCE
  joins malkan_rsi, rsi_reclaim, rsi_divergence_1h/4h in the s2 Holm pool.
- (g) covered - `studies/rsi.py` (ID 'rsi') routes malkan_40_60 + rsi_core; desk default 1d BREAK
  60/40. Unrouted: `malkan_mtf.py`, rsi_divergence / `run_divergence_mtf.py`, Kurisko
  `quad_rotation.py` / `stoch_core.py` are NOT_IN_DATA in `studies/*.py`. To cover them: add a
  divergence / Kurisko study file.
- (h) NOT ENOUGH DATA - divergence 31/32 net negative, L1-D3 only 1h support PBO 0.030, sim-desk
  n 2 [-1.042,-1.030]; the one clear cell (1h 40-support) is a gross-PBO result, not a fee-net
  trade edge yet.

## 5. cryptocred (S/R flip, fib pullback, failed MSB)
- (a) CryptoCred price-structure setups: S/R flip, fib pullback, failed market-structure break.
- (b) Source: CryptoCred videos BHwoN7VPrBE / inqHN8q57X4 (`extract_BHwoN7VPrBE.md`,
  `extract_inqHN8q57X4.md`). Provenance cryptocred row (LAYER_PROVENANCE_AUDIT.md:82): 6 SOURCED /
  11 CONCEPT-ONLY / 8 NO-SOURCE, 25 rows. SOURCED = bodies-not-wicks, close-through break,
  prior-sequence requirement, entry at the broken level, fib 0.618/0.786. NO-SOURCE = 0.1% stop
  buffer (C14/C23), 200-bar retest expiry, 20-bar failure window. The 1.5:1 and 2:1 are the
  trader's MINIMUM R:R filters (BH:82) used as fixed take-profit targets - a role swap, NO-SOURCE.
- (c) FAIL after trade-through rerun (`LAYER_REALITY:9`, sheet Backtests L107): 15m brackets FAIL;
  daily/4h untested. BIGTRADE-EXIT first row negative both splits (`EXIT_POLICIES_REPORT.md`,
  commit 26c6f3a83 2026-10-17); full table not read. L1-D3 mixed (shared row, PBO 0.030 at 1h
  support). Gross MFE/MAE event tables (TRIALS `gptb-cc-msb-event-table`) are gross, 24-bar, DEV
  2022-01..2024-06.
- (d) B143 (0.1% stop buffer + 1.5R target have no source, BLOCKED), B151 (limit-fill backtest
  fills on touch and drops signals on a future event, so its PASS numbers are upper bounds), B145
  (filter_range_noise off in the live layer; no evidence it is neutral).
- (e) Price-only klines; BTC; sealed splits; no walk-forward. Limit-fill model is optimistic
  (B151), so fee-net claims are upper bounds.
- (f) Combines: levels layers (S/R flip, fib, failed MSB are level families); shares BIGTRADE-EXIT
  and FIRES-B1 rows with fabio, rsi, session_timing, volume_candles_ma.
- (g) NOT_IN_DATA (`PLUGIN.md` "CryptoCred: Small adapter layers/cryptocred/cc_bt_adapter.py"; not
  imported in any `studies/*.py`). To make it covered: a `studies/cryptocred.py` wrapping
  `cc_bt_adapter.py`.
- (h) FAILED - trade-through rerun FAIL, unsourced stop/target (B143) and optimistic limit-fill
  upper bounds (B151); simulator cannot show it yet (g NOT_IN_DATA).

## 6. positioning (Funding, OI, whale / FlowHorse)
- (a) Funding / OI / long-short positioning as a filter or context (whale / FlowHorse).
- (b) Source: `whale_positioning_evidence_2026-09-12.md` (Memon 2026 T2), `FORMULAS.md:356-370`.
  Provenance positioning row: 0 SOURCED / 4 CONCEPT-ONLY / 3 NO-SOURCE, 7 rows. The Memon 2026
  citation is REJECT (repo holds only a tier label, no title/URL/quote, `LAYER_PROVENANCE_AUDIT`
  REJECT list item 2). Funding-extreme reversion direction has no source sentence in repo (CONCEPT-ONLY).
- (c) T055-C1 funding_cvd_fade rerun (`T055_BT_RERUN_FULLFUNDING_2026-10-07.md`, commit 36a114939
  2026-10-07, candidate table row 14): OOS FAIL, n 76, OOS net -0.0453%, OOS net Sharpe -0.0346,
  fee-net (fee 10 bps RT + slip 2 bps RT + funding, full funding from 2020-01); single-year OOS
  (2026: n=76), "provisional". OI-DELTA: descriptive only, no verdict line
  (`OI_DELTA_4STATE_BACKTEST_2026-09-21.md`).
- (d) funding tf mismatch: live 1h vs 15m tested, 0 of 34 coincide (`LAYER_REALITY:17`); B103
  (backtest funding cost silently 0 outside the loaded funding range, CLOSED); B075 (historical
  mode zeroed funding/OI and pulled live into a past snapshot - look-ahead, CLOSED).
- (e) Funding/OI/long-short ratios 2020-09.. (gap G5 being fetched); BTC; sealed splits; no
  walk-forward. The live-vs-test timeframe mismatch means live numbers are not comparable to the
  15m-tested ones.
- (f) Combines: CVD component overlaps tom/fabio order flow (`PRICE-CVD-DIV-1M5M`); context for
  other families.
- (g) NOT_IN_DATA (`PLUGIN.md` "funding fade: Small adapter, low value"; not imported in any
  `studies/*.py`). To make it covered: a `studies/positioning.py` on the funding/OI series plus the
  G5 fetch.
- (h) FAILED - OOS net -0.0453% n 76 fee-net (provisional single-year OOS), OI descriptive only,
  live/test tf mismatch; simulator cannot show it yet (g NOT_IN_DATA).

## 7. session_timing (Session levels, turn of candle, session momentum)
- (a) Session levels, turn-of-candle, session momentum.
- (b) Source: `TURN_OF_CANDLE_ORIGIN_2026-10-09.md` (Shanaev, Vasenin, Stepanov, Heliyon T1);
  session Shen/Urquhart/Wang 2022 (T1). Provenance: session 1 SOURCED / 2 CONCEPT-ONLY / 3
  NO-SOURCE, 6 rows; turn_of_candle 2 SOURCED / 1 CONCEPT-ONLY / 2 NO-SOURCE, 5 rows. SOURCED =
  15-min candle turn-of-candle (T055b:51) and first-window predicts last-window; session 1/2/3 and
  turn_of_candle 2/1/2 (sheet Params) are clock-time, NO-SOURCE (fixed UTC, no DST - B102).
- (c) T087 (`RESULT.md`, commit 71df3aad8 2026-10-09): failed first-break, BTCUSDT 1m
  2022-01-01..2026-10-07, no edge: asia_target|touch_all|both n 911, net -0.036%, t -1.72, win 31%
  (gross, no fee claim); EU-touch cells insufficient n (asia_target|touch_eu|low n 144, net
  -0.101%, t -1.95). T055-C2 session_momentum rerun (`T055_BT_RERUN_FULLFUNDING_2026-10-07.md`,
  commit 36a114939 2026-10-07, candidate table row 15): OOS FAIL, n 299, OOS net +0.0177%,
  Sharpe 0.0084, 1 of 2 OOS years positive (2025 +0.0636% / 2026 -0.0332%; fee 10 bps + slip
  2 bps + funding). T055-C3 (turn_of_candle + quarter-hour opening order imbalance, original
  `T055_BT_c3.md`): no gross edge at 4h/8h/12h on the BTC proxy (T055_BT_c3.md:31); not re-run in
  the 10-07 full-funding rerun (C1/C2 only). EUR-low sweeps BLOCKED by power gate (`RESULT.md`
  commit ecefc522c 2026-10-18); LC-SIZING-QUICK exploratory negative.
- (d) B102 (offline session models anchor NY/London at fixed UTC minutes, no DST, wrong ~40% of
  days, CLOSED), B187 (price-level study blocked by a power gate it cannot pass on current data,
  OPEN). turn_of_candle is 71% of live alerts (`LAYER_REALITY:20`) but exits differ.
- (e) BTC, session clock in UTC (no DST - B102); sealed splits; no walk-forward.
- (f) Combines: levels (session levels), krown (session context); session_momentum is in the pre-reg
  pool (5m, 48-bar horizon, PRE_REG_CONFLUENCE s3.4).
- (g) NOT_IN_DATA (`PLUGIN.md` "Session levels / momentum: Small adapter, low value";
  `backtest/layers/session`, `session_levels`, `turn_of_candle` not imported in any `studies/*.py`).
  To make it covered: a session study file on klines + session clock.
- (h) FAILED - T087 no edge net -0.036% t -1.72 (n 911, gross), C2 FAIL n 299 OOS net +0.0177%
  1/2 years positive, EUR-low blocked by power gate; simulator cannot show it yet (g NOT_IN_DATA).

## 8. volume_candles_ma (Volume, candle patterns, daily MA, bigtrade)
- (a) Volume flags, candle patterns, daily MA, big-trade fires.
- (b) Source: `FORMULAS.md` only. ma_daily numbers are NO-SOURCE, from a chatbot handoff (sheet
  L164); ALPHA labelled NO-SOURCE. volume, candle_patterns, ma_daily, bigtrade_fires have no
  trader source.
- (c) VOLUME (`VOLUME_RESEARCH_REPORT_2026-10-09.md`, commit 3cb5b521c 2026-10-09): no validated
  directional edge, "volume gives intensity, not direction" (report :9-10: 553 pre-registered
  trials -> 1 marginal DEV pass that failed VALIDATION, net -2 bp on 50 events vs +70 bp on DEV);
  volume HOLDOUT sealed. ALPHA (`ALPHA_RESULTS.md`, commit 457d13043 2026-10-12): NO-SOURCE, A CAGR
  20.5% / maxDD 49% vs buy-and-hold 43.8% / 76.7% - "not a result". CANDLE-P1 1d engulfing rows all
  FAIL; CANDLE-CLOSE-DEV exploratory negative. BIGTRADE-EXIT first row negative both splits. Gross
  MFE/MAE event tables (TRIALS `gptb-volume-event-table`, `gptb-candle-pattern-event-table`) are
  gross, DEV 2022-01..2024-06.
- (d) B163 (an operator-pasted "Setup Alpha / Beta" handoff listed as a request, not a layer
  result, so it is not mistaken for a tested strategy); B144 (exhaustion proxy volume 2.0x over 240
  1m bars, no source, OPEN).
- (e) OHLCV; BTC; sealed splits (volume HOLDOUT sealed, VALIDATION unread); no walk-forward.
- (f) Combines: krown ("volume at 2x its average", "four candle patterns"); bigtrade rows shared
  with fabio, rsi, session_timing.
- (g) NOT_IN_DATA (`PLUGIN.md` "big-trade fires: Small adapter, low value; volume, candle patterns
  Does not fit"; not imported in any `studies/*.py`). Additionally `_bars.py:4,69` loads only OHLC
  columns without volume. To make it covered: add a volume/candle study and extend `_bars.py` to
  load the volume column.
- (h) NOT ENOUGH DATA - no validated directional edge (intensity, not direction), HOLDOUT sealed,
  MA numbers NO-SOURCE; no 95% range computed on the desk for this family.

## 9. live_engine (Engine, execution, live reads)
- (a) The execution engine and live-market reads; infrastructure, not a strategy - it feeds every
  layer.
- (b) Source: `live_session_protocol.md`, `screenshot_intake.md`. Proof bands 3 and 5, net_rr floor
  1.25, and min stop floors are NO-SOURCE (BUGS.md B117 :228, B153 :264, B116 :227). No trading
  parameter is trader-sourced: this is an infra layer.
- (c) No backtest row - live_engine has no strategy P&L number. Testnet HALT since 2026-10-12
  09:46Z (executor fail_closed; supervisor clears it; `system/layer_index.json:532`).
- (d) B075, B081 (four different fee sets for the same Deribit BTC perp), B116-B118, B136, T085
  (97% of testnet trades end on the time exit; the 1%/2%/8-bar bracket on every layer was never
  backtested, T09:3-5/86). B042 day_type, B054 cvd_aligned proof direction-blind (WONTFIX).
- (e) It is the execution/read layer, not a strategy; assumptions are those of the live runner
  (HALT, restart/reset, non-trade balance moves, API errors - live-path tests).
- (f) Feeds all 12 strategy families (its plain says "feeds every layer"); callers score against the
  same klines it produces.
- (g) NOT_IN_DATA (`PLUGIN.md` "Live engine: Does not fit - it is execution, not a backtest";
  `MyTradingSys/execution` not imported in any `studies/*.py`). By design the simulator does not
  show it: it is the runner, not a backtest layer.
- (h) NOT ENOUGH DATA - no backtest row; infra layer under Testnet HALT since 2026-10-12, with
  open engine-gate bug B136 and T085; not a strategy P&L, so no 95% range applies.

## 10. callers (Posted trade calls)
- (a) Score the posted calls of named analysts (Qriptal, RLinda, Bennett, Crypto Chase, Roman) on
  Binance klines before anything is traded.
- (b) Source: B162 item, analysts REVIEW. Self-reported 67.1% wins, avg win 3.99%, avg loss 0.63%
  are unverified (sheet L209). No trader file is the "source" here - the analysts are the subject,
  not a spec; parameters NOT_IN_DATA.
- (c) No backtest result yet. The kline scorecard (multi-provider parser + ingestion, built
  2026-10-18) scores the record before anything is traded; the 67.1% / 3.99% / 0.63% are the
  analysts' own claims, unverified. Triage floor: n=30 resolved trades gives 60.5% power vs a
  50% coin-flip null at the claimed 67.1% win rate (`analysts/ROADMAP.md` :68).
- (d) B139 (analyst-rules adapter has no tracked item; candidates file never produced; analyst
  rules unbacktested, OPEN). Ingestion is unfinished: 4 ingestion cards ready
  (analyst-ingest-rlinda-tv / -bennett-dpa / -cryptochase-x / -roman-x,
  `analysts/REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md` :103-106 + ROADMAP.md:15).
- (e) Scored on the same BTC klines every backtest uses; sealed splits; no walk-forward; fee-net
  sum R < 0 at n=30 drops the analyst.
- (f) JUDGE role - scores calls on the same klines; no strategy-family confluence, it judges.
- (g) NOT_IN_DATA (`PLUGIN.md` "callers: Does not fit"; `research/analysts/{schema,ingest_analysts,
  score_analysts,run_scorecard}.py` not imported in any `studies/*.py`). To make it covered: a
  callers study file wrapping `run_scorecard.py` over the klines.
- (h) NOT ENOUGH DATA - scorecard unverified (self-reported 67.1% wins unconfirmed), B139 unbacktested,
  4 ingestion cards open; no 95% range computed.

## 11. krown (TA 101: zones, volume, candles, averages, ranges)
- (a) Krown TA 101: zones, volume, candles, averages, ranges; D1/D2/D3 context + T2/T4 signals.
- (b) Source: `KROWN_LAYER_SPEC.md`, `PRE_REG_KROWN.md` (commits 1abed63bd 2026-10-19 /
  989d7040f 2026-10-14). 120-rule ledger from 15 of 19 reachable TA 101 videos (LAYERS.md:221) -
  `LAYER_REALITY:13` says 127 rules from 16 of 20 (the sheet's Stale block notes LAYERS.md is
  generated and the source text needs a fix). One structural stop (compression breakout); stop
  distance and size are OURS (sheet L222); the rest is OURS. `krown_params.json` carries 47 entries
  (ma_fast 21, ma_slow 55, ma_long 200, bbwp 7/100/2.0/30/50, range_n 20, etc.).
- (c) No DEV event study yet (sheet L222, `LAYER_REALITY:13`). Sim-desk trial `TRIALS.md:280`
  (row dated 2026-10-25, added by 60f53e24c 2026-10-25 "sim desk: Krown study"): krown S5 4h
  target 2R, fees 0.02/0.05% slip 0.02%, DEV 2022-04-01..2024-06-30, fee-net: filled n 35 (0 never
  filled), mean net R +0.278 [-0.161, +0.750], worst losing streak 4 - NOT ENOUGH DATA. Confluence-
  s1 D3/D2 band grids (`TRIALS.md:275-277`, rows dated 2026-10-23) are counts only, no outcome
  column read (DEV decision times only).
- (d) B141 (Krown/levels `htf_context_live` bal_4h/bal_1d null on every row: the balance rule holds
  in 0.4% (4H) and 0% (1D) of windows, so failed_breakout is null, OPEN); detector recall check
  3 of 12 (`RECALL.md`/`KROWN_GAP_AUDIT_2026-10-18.md` commit 8e5c3647 2026-10-18) - RECALL FAIL
  (0 strict hits within 2 bars), fire rate PASS. Detectors S1-S9 exist, 49 tests, but `enabled:false`.
- (e) OHLCV 1d/1w only (Binance spot krown_daily; basis note F17); sealed splits; no walk-forward.
  LAYERS.md is generated: "120 rules / 15 of 19" vs LAYER_REALITY "127 rules / 16 of 20" - source
  fix pending.
- (f) Context slot (design): rsi (RSI 40/60 confirmation), volume_candles_ma (volume, candles); its
  context is pooled over the 13 joined layers (PRE_REG_CONFLUENCE s3.4). Levels family shares
  `studies/levels.py` pooling with krown.
- (g) covered - `studies/krown.py` (ID 'krown') routes krown_core + krown_events S4/S5/S8. Unrouted:
  S1/S2/S7/S9 need volume (`_bars.py:69` omits it), S3 range edge, S6 5-EMA leash (`krown.py:33-35`
  SKIPPED). To cover those: extend `_bars.py` to load volume.
- (h) NOT ENOUGH DATA - no DEV event study; sim-desk n 35 [+0.278 mean, 95% -0.161..+0.750]
  (fee-net) is too small; recall check FAIL 3 of 12.

## 12. wavetrend (LazyBear oscillator)
- (a) Causal BTC context layer: WaveTrend oscillator states (LazyBear).
- (b) Source: `PARITY_CONTRACT.md`, `ATLAS_STUDY_SPEC.md`. Parameters NOT_IN_DATA in the sheet;
  the oscillator constants (N1=10, N2=21, SMA_N=4, K=0.015, OB1=60, OB2=53, WARMUP=200) are in
  `backtest/layers/wavetrend/wavetrend.py:16-19` - OURS (LazyBear formula, no trader source in repo).
- (c) `research/wavetrend_2026-10-17/RESULT.md` (commit 249f01fd0 2026-10-17): W01-03/W09 FAIL;
  W04-08 INCONCLUSIVE per the MTS re-gate; W07/W08 also use an invalid C1 detector; 0 of 9 frozen
  cells pass the gross DEV screen (gross, no fees, DEV 2022-01-01..2024-06-30, RESULT.md:3,5).
  Sim-desk trial `TRIALS.md:273` (row dated 2026-10-21, added by 2b80ef52b 2026-10-21):
  wavetrend 1h band 53 BOTH target 1.5R, fees 0.02/0.05%, DEV 2022-04-01..2024-06-30, fee-net:
  filled n 369 (0 never filled), mean net R -0.158 [-0.288, -0.023], worst losing streak 8 - FAILED.
- (d) Invalid C1 detector (L244): W07/W08 used a wrong divergence detector; card `wavetrend-c1-v2`
  (p1, refined) is the correction.
- (e) BTCUSDT USD-M DEV bars 2022-01-01..2024-06-30; sealed splits; no walk-forward; desk fills on
  1m even when the signal is higher-TF.
- (f) RSI (sheet combines-with). Atlas variants W01-W09 are not routed in `studies/wavetrend.py`
  (NOT_IN_DATA); only the default 1h band 53 is exposed.
- (g) covered - `studies/wavetrend.py` (ID 'wavetrend') routes `wt.compute(...)`. Unrouted: the
  9 atlas variants W01-W09. To cover them: add the atlas variants to the study file.
- (h) FAILED - sim-desk fee-net n 369 [-0.288, -0.023] (whole range below zero); gross screen 0 of 9
  cells pass; W07/W08 used an invalid C1 detector.

## 13. pitchfork (Andrews / Schiff / Morge median line)
- (a) Dynamic equilibrium channels: median-line reach (80% rule) and Hagopian failure breakout.
- (b) Source: papers 01-03 (`papers/01_MASTERS_PITCHFORK_FOUNDATIONS.md` etc.). Parameters
  NOT_IN_DATA in the sheet (no per-parameter provenance row).
- (c) None recorded with a verdict. The YouTube BTC evaluation benchmark: Daily 1D event study
  (2,461 bars, 2020-01-01..2026-09-26, 361 setups, `PHASE1_EVENT_STUDY.md`) confirms Andrews' 80%
  rule on Bitcoin, per-model ML reach: Standard Andrews 55.96%, Schiff 86.15%, Modified Schiff
  89.2%, Log-Modified Schiff 90.03%. The P&L column is fee-net (0.10% RT taker + 0.02% slip): mean
  returns Schiff -1.12%, Modified -1.12%, Log-Modified -0.95%. A 4H study (PHASE2) ran on 14,766
  klines / 1,273 confirmed swing setups. These span 2020-2026, not DEV-only - the reach rates are
  a descriptive benchmark, and the fee-net P&L is negative; no DEV fee-net edge. Detector built with
  unit tests (100% pass).
- (d) Studies span 2020-2026, not DEV-only (`LAYER_REALITY:18`); no VERDICTS row.
- (e) 4H/1D klines on BTC; sealed splits; no walk-forward; the DEV-only rerun is an open card.
- (f) levels (structure zones; subject overlaps krown/cryptocred only - the map marks the confluence
  as UNKNOWN).
- (g) NOT_IN_DATA (`PLUGIN.md` "pitchfork: Does not fit"; `pitchfork_detector.py` not imported in any
  `studies/*.py`). To make it covered: a pitchfork study file wrapping `pitchfork_detector.py` on a
  DEV-only rerun.
- (h) NOT ENOUGH DATA - no DEV-only fee-net verdict (studies span 2020-2026, no VERDICTS row);
  detector built with tests; no 95% range computed.

## Cross-family reading (OURS, no verdict)
- Simulator coverage: 3 dedicated studies covered (rsi, krown, wavetrend via `studies/{rsi,krown,
  wavetrend}.py`); 2 partial via `studies/levels.py` level-family inputs (tom, fabio tagged 6 of 8
  KEEP level families, `argon_sim_layer_coverage.md` :12); 8 NOT_IN_DATA (guidance, cryptocred,
  positioning, session_timing, volume_candles_ma, live_engine, callers, pitchfork). The two common
  gates: (1) order-flow bars before 2024-12 and ETH/SOL 1m (takes tom/fabio there), and (2) a small
  study/adapter file per family (takes the other 6 there); live_engine is out of scope by design
  (execution, not a backtest).
- Rubric verdict tally: proven 0, promising 0, FAILED 7 (tom, fabio, guidance, cryptocred,
  positioning, session_timing, wavetrend), NOT ENOUGH DATA 6 (rsi, volume_candles_ma, live_engine,
  callers, krown, pitchfork). No family is dropped: the standing rule keeps every family until it
  has been seen in the simulator, and the 8 NOT_IN_DATA families name the gate above.
- Fee stop rule (`FABLE_FEE_STOP_RULE.md`, 91170f43c 2026-10-26): a stop must be at least 4x the
  round-trip fee before gross edge can survive (0.40% taker / 0.20% maker floors, SOURCED from
  `PRE_REG_CRYPTOCRED_HTF.md` gate 0a). This is why tom (B146 median stop 0.082%), kurisko (14 bp
  round trip) and the tight K5 stop all lose to fees - the single largest recurring fee-net
  failure across the FAILED families.

## Corrections vs the wrong-model draft (shipped 983f96a33)

Verified line by line against disk + git on 2026-10-27; the headline numbers, bug ids,
provenance totals, confluence/coverage routing and 20 cited commit hashes all held. What the
draft got wrong or thin:

1. `TRIALS.md` row attributions (draft §4/§11/§12): the draft cited commit 28565f801
   (2026-10-26) for rows :273 (wavetrend), :274 (rsi) and :280 (krown). 28565f801 added only
   :282 (rsi-deep-prob-tables). Row :273 and :274 are dated 2026-10-21 and came with 2b80ef52b
   ("sim-desk: RSI 40/60 (Malkan) and WaveTrend (LazyBear) studies on the desk"); row :280 is
   dated 2026-10-25 and came with 60f53e24c ("sim desk: Krown study (S5/S8/S4), exploratory,
   DEV only"). Fixed per row.
2. TOM-CORE-0929 (draft §1c): "report commit 2026-10-26" was a relocation, not an authorship.
   The report was created in 5831eadd7 (2026-09-30, WIP commit carrying `TOM_CORE_BT.md`);
   f8d0799de (2026-10-26) only moved research/ files into `_archive/`. Fixed.
3. RSI-DIV-MTF (draft §4c): the draft cited 0aa8f5644 as the RESULT.md commit. Created by
   1157dbe6c ("T089+T091: RSI divergence on every timeframe", 2026-10-09); 0aa8f5644 ("T088")
   amended it minutes later. Fixed.
4. `PROVENANCE_AUDIT_TOM.md` (draft §1b): the draft dated it 2026-10-26. Authored 5f816ae12
   (2026-09-30, "36 NO-SOURCE, 33 concept-only, 2 sourced"); counts updated through aaf007a5b
   (2026-10-08, "A11 reclassified, B127 closed, B145 filed") to the current 2/34/35/74. Fixed.
5. `LAYER_PROVENANCE_AUDIT.md` (draft §4b): the draft cited f8d0799de 2026-10-26. Authored
   9b76e716f (2026-10-04, "81 non-core params, 17 SOURCED / 34 CONCEPT-ONLY / 30 NO-SOURCE");
   f8d0799de only touched 4 lines. Fixed.
6. Pitchfork (draft §13c): "86.15%-90.03% reach on Modified Schiff" conflated the four ML
   models: 86.15% is Schiff, 89.2% Modified Schiff, 90.03% Log-Modified Schiff (Standard Andrews
   is 55.96%). Also the P&L column of PHASE1 is fee-net (0.10% RT taker + 0.02% slip), not
   gross: mean returns Schiff -1.12% / Modified -1.12% / Log-Modified -0.95% on 2020-2026. Fixed.
7. T055-C3 (draft §7c): "NO EDGE gross OOS ~0 at every horizon" is supported but the source is
   the original `T055_BT_c3.md` (:31 "no gross edge at 4/8/12h on BTC proxy"), NOT the 10-07
   full-funding rerun - that rerun carries C1/C2 only. Re-sourced.

Also refined (wording, not error): §6c now points at the candidate-table rows (report :14/:15),
§8c cites the volume report's "1 marginal pass failed VALIDATION" line (:9-10), §9c adds
`system/layer_index.json:532` for the HALT, §10d names the 4 ingestion cards with sources
(`REVIEW_AND_INGESTION_EVALUATION_2026-10-18.md` :103-106 + ROADMAP.md:15), §12c cites
RESULT.md:3,5 for the 0-of-9 gross screen.

Cross-check: sibling FABLE_FULL_AUDIT (`FABLE_FULL_AUDIT.md`, commit ccc3d661e 2026-10-26,
sibling session fable-audit) found no numeric conflicts against this review's sim-desk
numbers; its open card `krown-review-feenet-prose` (fee-net prose in `krown_study_review.md` +
`test_krown.py:67`, off ~100x on the fee figure - the test assertion itself is correct) is
outside this file's scope and noted here so the fix gets attributed to the right card. The
audit's "Krown S4 = OURS" note reads the params-json label; TRIALS.md:280's trial is the S5
trial as cited here.
