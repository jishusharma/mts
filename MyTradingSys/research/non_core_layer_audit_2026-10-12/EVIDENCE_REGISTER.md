# Evidence register v1.0.0 (as of 2026-10-12)

Machine-readable twin: `EVIDENCE_REGISTER.json`; check with `verify_register.py`. Fidelity: FAITHFUL | PARTIAL | MISMATCH | UNKNOWN | NA. Historical verdicts are kept beside the current assessment.

| ID | System | Fidelity | Historical verdict | Current assessment | Calibration | Deployment | Next acceptance gate |
|---|---|---|---|---|---|---|---|
| ER-01 | RSI calculation (Wilder, period 14) | FAITHFUL | n/a (calculation, not a strategy) | REPRODUCED: period-3 worked case 83.333333 then 66.666667 matches; 134 rsi tests pass on fast-track | n/a | CODE: used by every RSI consumer; deployment SHA UNKNOWN (mirror stale) | Golden fixture from a real chart export matches to 1e-6 after warm-up |
| ER-02 | RSI level events (live: 40-support long, 0.5 tolerance) | MISMATCH | D3 1h OOS n=89, gross +0.043%, PBO 0.030 (RECORDED); below 10 bp round trip | No edge shown; tolerance is an in-sample boundary pick, so the 0.5 live value is unsourced | Live RSI 5m/15m/1h closed rows exist in stale mirror (RSI 5m 48, 15m 13, 1h 4); not an experiment | CODE: registered 5m/15m/1h; running process/version UNKNOWN | One versioned event->side->exit identity used by both research and calibration; tolerance either sourced or labelled operator hypothesis |
| ER-03 | Malkan 40/60 single-timeframe (regime + candle at 40/60) | PARTIAL | Generic 1%/2% bracket: 1h n=43 net -0.092% PBO .760; 4h n=17; 1d n=5 (RECORDED) | Rejects the tested proxy, not the complete Malkan entry; regime BULL can hold while current RSI is 45 (REPRODUCED), which matches a range-shift definition but is not a threshold gate | No closed Malkan rows in stale mirror (unexplained: rare vs routing vs rejection) | CODE: malkan_bull/malkan_bear 1h registered; running version UNKNOWN | Own-source rule ledger resolves target/confirmation/HTF gates or marks them UNKNOWN; only then a frozen strategy run |
| ER-04 | Malkan multi-timeframe composer | PARTIAL | No full-strategy MTF run receipt located on this machine | UNKNOWN: absence locally does not prove global absence | none | CODE only; not a registered live key | Causal HTF test: timestamps carry available_at; no query returns a bar closing after the signal |
| ER-05 | RSI divergence (Malkan-window detector + operator variants) | PARTIAL | 92 cells: 36 NO EDGE, 56 INSUFFICIENT-N, 0 edge candidates (RECORDED, regenerated exactly) | Raw ten-bar forward-return event study less 0.10% fee; overlapping events; not a strategy. 1h operator bearish n=332 net +0.038% t=0.39 is not evidence | none | Research only; no live key | Event rows exported; recall/false-positive measured on held-back source examples before any strategy exit is encoded |
| ER-06 | RSI reclaim / 2a / long-range operator ideas | UNKNOWN | Higher-timeframe leads small-n and anchor-dependent (6h/7h: n 35-55, 3 of 18 cells t>2) RECORDED | Unvalidated, underpowered; no promotion | none | Research only | Frozen spec + trial registry entry before any run; new combinations counted as new trials |
| ER-07 | WaveTrend with Crosses [LazyBear] | UNKNOWN | none | No backtest, no output; not a failed layer | none | Parked on Layer Board; not registered | One module path; golden fixtures reproduce exported values; warm-up, d=0, equality and closed-bar tests pass; observation-only, no side inferred |
| ER-08 | Other LazyBear indicators (Squeeze, Better Volume, VFI) | UNKNOWN | none (T3, no MTS backtest) | none | none | none | Source-version decision recorded per indicator before any code |
| ER-09 | CryptoCred setups (SR flip, fib pullback, failed MSB) | MISMATCH | Fill-bias corrections recorded; setups not S3-validated (RECORDED) | Not evidence of edge in either direction under native geometry | Stale mirror closed: SR flip 15m 19, 1h 2; fib 15m 7; failed MSB 15m 1 (event counts, not reconciled) | CODE: auto_trader.layer_signal builds market plan from configured stop_pct/targets, ignoring native entry/stop | Role-level provenance corrected; live-vs-backtest contract written with distinct experiment ids |
| ER-10 | Positioning / funding-CVD fade | PARTIAL | Full-funding rerun n=76 net -0.0453% (fails gate; RECORDED) | Negative; reopen only with a materially different sourced hypothesis | No closed rows in stale mirror | CODE: positioning|funding_cvd_fade|1h registered; defaults differ from research variant | Variant identity frozen (research == live defaults or explicitly separate) |
| ER-11 | Session momentum | MISMATCH | n=299 net +0.0177% Sharpe .0084, 1 of 2 OOS years positive (RECORDED, fails gate) | Tiny, inconsistent; variant differs from live | 5 closed session rows in stale mirror | CODE: session|session_momentum|15m registered | Test exactly the intended contract; report per-year; do not retrofit research variant to live |
| ER-12 | Turn of candle | MISMATCH | 49,823 OOS events, ~0 gross, net -0.1201% (RECORDED); imbalance variants fail | High frequency is not edge; research enters at opening-window close, live at minute 14 | 548 closed rows in stale mirror: calibration ledger, not validation | CODE: turn_of_candle|1m registered | Timing reconciled; calibration results kept separate from strategy evidence |
| ER-13 | Session levels / failed first break | PARTIAL | Cells with sufficient n negative (RECORDED) | No parameter search to rescue | none | Research only | Event rows + justified boundaries + matched null |
| ER-14 | Tick / extreme flags | UNKNOWN | Flag rate 0.11/day on aggTrades window (RECORDED) | Rare flags do not prove predictiveness | none | Not in default registry | Mismatch mechanism identified; builder wording corrected or data fixed; no threshold promotion before |
| ER-15 | Timeframe resampling infrastructure | PARTIAL | n/a | REPRODUCED: gapped bucket returned with gap_count=20,n_bars=40; the divergence driver does not read gap_count, so the info exists but is not enforced | n/a | CODE | Consumer filters or reports gap_count>0; variable-duration buckets not described as uniform 7h |
| ER-16 | Consensus / RSI observation hook | PARTIAL | n/a | 52 tests pass; README says nothing calls it, which is stale | n/a | CODE: hook wired in live runner; running state UNKNOWN | as-of/age fields so stale RSI cannot look current; README corrected |
| ER-17 | MA / candle / volume research | NA | V3 candidate n=50 net -2 bp CI [-68,+64] INSUFFICIENT-N vs min 100; candle results DEV triage | No validated standalone entry system | none | none | Frozen candidates only; event rows; multiplicity control |
| ER-18 | Kurisko candidate | UNKNOWN | none | none | none | none | Source confirmation before any parameter set |
| ER-19 | Probability / options / analyst-caller feeds (inventory only) | UNKNOWN | not audited | UNKNOWN, not passed | not audited | not audited | Separate calibration and feed-integrity audit |

## Unknowns and missing inputs

**ER-01 RSI calculation (Wilder, period 14)**
- UNKNOWN: Warm-up/missing-value parity with a charting platform on real series
- NEEDS: Platform export of RSI(14) for one real BTC 1h series (golden fixture)

**ER-02 RSI level events (live: 40-support long, 0.5 tolerance)**
- UNKNOWN: Whether the live 0.5 tolerance was ever re-derived from a source
- UNKNOWN: Which event types (support/rejection/failure/cross) the executed trades came from
- NEEDS: Event-level outcome rows with event type and side
- NEEDS: Deployed config SHA

**ER-03 Malkan 40/60 single-timeframe (regime + candle at 40/60)**
- UNKNOWN: Complete daily entry/stop/target and HTF conditions
- UNKNOWN: Why the mirror has no closed Malkan rows
- NEEDS: Source ledger with frames (P0-B)
- NEEDS: Funnel logs: detector -> alert -> plan -> fill

**ER-04 Malkan multi-timeframe composer**
- UNKNOWN: Whether a full MTF run exists on another machine
- NEEDS: Run manifest from data owner
- NEEDS: Explicit bar-open vs bar-close availability field

**ER-05 RSI divergence (Malkan-window detector + operator variants)**
- UNKNOWN: Detection precision/recall against annotated source charts
- NEEDS: Per-event outcome rows
- NEEDS: Source frames for target C

**ER-06 RSI reclaim / 2a / long-range operator ideas**
- UNKNOWN: Frozen confluence definition (BB, CVD/OI, RSI-MA, speed trigger)
- NEEDS: Preregistered hypothesis; untouched period or symbols

**ER-07 WaveTrend with Crosses [LazyBear]** (acceptance checklist updated 2026-10-17, card wavetrend-priority-source-parity; contract: `research/wavetrend_2026-10-17/PARITY_CONTRACT.md`)
- DONE: Exact Pine version = lonestar108 republication of LazyBear (TV script 2295, created 2016-02-20), math identical to the plain WaveTrend gist; open source, no licence text, courtesy note only
- DONE: Saved Pine source snapshot (`research/wavetrend_2026-10-17/source_snapshot/`, sha256 pinned)
- DONE (contract): EMA seed, d=0 -> NaN no event, wt2 warm-up, cross equality "le", gap handling, WARMUP=200; PINE-UNVERIFIED stays for runtime seed/equality (not needed after warm-up)
- DONE: Owner path = `backtest/layers/wavetrend/`; `layers/momentum/wavetrend.py` dropped
- OPEN: golden fixtures from a spreadsheet on a real dated BTC 1h sequence, ideally a TradingView export (card wavetrend-observation-module); FORMULAS.md entry
- NEEDS: Chart export for flat, trending, alternating and one real series

**ER-08 Other LazyBear indicators (Squeeze, Better Volume, VFI)**
- UNKNOWN: Squeeze BB multiplier: displayed source vs corrected version
- UNKNOWN: VFI is not measured aggressor CVD
- NEEDS: Updated Squeeze source
- NEEDS: Chart parity exports

**ER-09 CryptoCred setups (SR flip, fib pullback, failed MSB)**
- UNKNOWN: Own-source instruction for fixed exits
- UNKNOWN: Whether live and backtest exits are the same experiment
- NEEDS: Canonical ledger
- NEEDS: Deployed config SHA

**ER-10 Positioning / funding-CVD fade**
- UNKNOWN: Raw CVD/funding coverage for the research window
- NEEDS: Data manifest

**ER-11 Session momentum**
- UNKNOWN: Intended sourced/adapted session contract
- NEEDS: Per-year and per-session risk-adjusted table

**ER-12 Turn of candle**
- UNKNOWN: Exact timing parity between research entry and live entry
- NEEDS: Entry timestamps per event

**ER-13 Session levels / failed first break**
- UNKNOWN: Justified session boundaries
- NEEDS: Event rows; like-for-like null

**ER-14 Tick / extreme flags**
- UNKNOWN: Why kline vs aggTrades delta differs (max 68.25 BTC over 126,720 bars). missing_in_klines=2880 is exactly 2x1440, i.e. two whole days absent, which explains the missing count but not the delta gap; distribution of differences not recorded
- NEEDS: Raw 1m klines for the compared window (Dumps/backtest/raw_1m_2022 absent on this machine)
- NEEDS: Per-bar difference list

**ER-15 Timeframe resampling infrastructure**
- UNKNOWN: Impact of gapped closed buckets on divergence results
- NEEDS: Per-event gap_count in export

**ER-16 Consensus / RSI observation hook**
- UNKNOWN: Write-failure accounting
- NEEDS: Freshness tag spec

**ER-17 MA / candle / volume research**
- UNKNOWN: Whether frozen candidates survive on unseen data
- NEEDS: Reserved data

**ER-18 Kurisko candidate**
- UNKNOWN: Oscillator definition, third setting, trigger, market translation
- NEEDS: Primary chart/source confirmation

**ER-19 Probability / options / analyst-caller feeds (inventory only)**
- UNKNOWN: Calibration, feed integrity, execution readiness
- NEEDS: Dedicated audit

## Review notes (2026-10-12)

- ER-02: the audit's 'tolerance 0 invalid' finding was already provenance-logged as R04/Q3; the open question (what does the live runner pass?) is answered: live_layers passes 0.5 and default.json is read only by tests. New: 0.5 is the boundary value of an in-sample grid, so it is itself NO-SOURCE.
- ER-03: a live tolerance of 0.5 (ER-02) and 2.0 (ER-03 params, labelled source MalkanView) coexist for the same 40 level; the two are different experiments and must not share a label.
- ER-15: the audit asked for a 'duration field'; gap_count and n_bars already exist per bucket. The defect is consumer-side (not read), not schema-side.
- ER-14: 2880 missing bars is exactly two days; narrows the mechanism question but does not settle the 68.25 BTC maximum.
- ER-05: independent recount from summary.json/summary_T088.json at horizon 10 gives 92 cells, 36 with n>=300 (35 net negative, one +0.038% t=0.39), 56 insufficient. All 36 powered cells are on 1m-2h; gross spans -18 to +14 bp against a 10 bp fee, so the result is a fee-and-power statement about low timeframes, not a measurement of divergence information on 4h/1d where n is too small.
- Roadmap P0-A deliverable is the register; roadmap wording caveat stands: a fixed bracket is not a proven lower bound on source management.

## Citations

**ER-01**
- code: `MyTradingSys/backtest/layers/rsi/rsi_core.py:7` `def rsi_core(closes: List[float], period: int = 14)`
- tests: `MyTradingSys/research/non_core_layer_audit_2026-10-12/tests_rsi.txt:1` 

**ER-02**
- code: `MyTradingSys/backtest/layers/alerts/live_layers.py:143` `RSI_TOL = 0.5`
- code: `MyTradingSys/backtest/layers/alerts/live_layers.py:142` `RSI_LEVEL = 40.0`
- code: `MyTradingSys/backtest/layers/rsi/rsi_events.py:21` `raise ValueError("tolerance must be > 0")`
- code: `MyTradingSys/backtest/layers/rsi/params/default.json:15` `"tolerance": 0,`
- provenance: `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:53` `| R04 |`
- provenance: `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:74` `| R25 |`
- provenance: `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:75` `| R26 |`
- stats: `MyTradingSys/backtest/layers/BACKTEST_L1_REPORT.md:14` `## D3 tolerance study`

**ER-03**
- code: `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` `def malkan_regime(rsi: list`
- code: `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:12` `"regime_lookback": 20,`
- code: `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:13` `"event_tolerance": 2,`
- provenance: `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:60` `| R11 |`
- provenance: `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:61` `| R12 |`

**ER-04**
- code: `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:22` `def state_asof(times: list, values: list, t: int):`
- code: `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:53` `def malkan_mtf_bull(bars: list, rsi: list, daily_regime: list`

**ER-05**
- code: `MyTradingSys/backtest/layers/rsi/rsi_divergence.py:32` `def rsi_divergence(close: list`
- code: `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:6` `"min_bars_quote": "How many candles are needed? Three."`
- stats: `MyTradingSys/research/rsi_divergence_mtf_2026-10-09/RESULT.md:1` `# T089 + T091 result`
- stats: `MyTradingSys/research/t090_7h_2026-10-09/RESULT.md:1` `# T090 7h research`

**ER-06**
- code: `MyTradingSys/backtest/layers/rsi/rsi_reclaim.py:33` `def rsi_reclaim_events(`
- spec: `MyTradingSys/research/rsi_2a_2026-10-09/RSI_2A_SPEC.md:1` 

**ER-07**
- spec: `MyTradingSys/items/T061_wavetrend_lazybear.md:28` `wt2   = SMA(wt1, 4)`
- spec: `MyTradingSys/items/T061_wavetrend_lazybear.md:16` `Overbought Level 2 = 53`
- survey: `MyTradingSys/research/T065_LAZYBEAR_SURVEY.md:5` `## 0. Evidence status`
- board: `MyTradingSys/system/control_room.json:254` `"id": "wavetrend",`

**ER-08**
- survey: `MyTradingSys/research/T065_LAZYBEAR_SURVEY.md:9` `Not verified: the Squeeze Momentum author's *updated* source`

**ER-09**
- code: `MyTradingSys/backtest/layers/cryptocred/cc_setups.py:53` `target_r: float = 1.5`
- code: `MyTradingSys/execution/auto_trader.py:367` `def layer_signal(alert: dict, cfg: dict, now: datetime)`
- provenance: `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:100` `| C15 |`
- provenance: `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:109` `| C24 |`
- source: `extracts/processed/cryptocred/extract_BHwoN7VPrBE.md:82` `greater minimum risk reward requirements`

**ER-10**
- code: `MyTradingSys/backtest/layers/positioning/funding_cvd_fade.py:70` `def funding_cvd_fade_events(`
- provenance: `MyTradingSys/research/LAYER_PROVENANCE_AUDIT.md:124` `| P05 |`
- stats: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:1` `# T055 C1/C2 RERUN, full funding`

**ER-11**
- code: `MyTradingSys/backtest/layers/session/session_momentum.py:16` `def session_momentum_events(`
- stats: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_RERUN_FULLFUNDING_2026-10-07.md:11` `## Result`

**ER-12**
- code: `MyTradingSys/backtest/layers/turn_of_candle/turn_of_candle.py:59` `def turn_of_candle_events(`
- stats: `MyTradingSys/research/fast_track_2026-09-27/T055_BT_c3.md:1` `# T055 backtest - C3`

**ER-13**
- code: `MyTradingSys/backtest/layers/session_levels/session_levels.py:23` `FAIL_WINDOW_MIN = 60`
- stats: `MyTradingSys/research/t087_session_levels_2026-10-09/RESULT.md:1` `# T087 failed first break`

**ER-14**
- code: `MyTradingSys/backtest/layers/tick/build_tiers.py:6` `identical to the aggTrades 1m delta`
- code: `MyTradingSys/backtest/layers/tick/tiers_meta.json:12` `"max_abs_delta_diff_btc"`
- code: `MyTradingSys/backtest/layers/tick/tick_flagger.py:107` `def make_flag(`

**ER-15**
- code: `MyTradingSys/backtest/layers/timeframe/tf_resample.py:145` `gap_count = max(0, n_expected - n_bars)`
- code: `MyTradingSys/backtest/layers/timeframe/tf_realdata_gate.py:81` `if bucket["gap_count"] != 0:`

**ER-16**
- code: `MyTradingSys/backtest/layers/consensus/hook.py:112` `def consensus_after_poll(`
- doc: `MyTradingSys/backtest/layers/consensus/README.md:10` `## Status: nothing calls it yet`

**ER-17**
- stats: `MyTradingSys/research/volume_2026-10-09/V3_VALIDATION_RESULTS.md:1` `# V3 VALIDATION RESULTS`
- stats: `MyTradingSys/research/candle_patterns_2026-10-04/P1_RESULTS.md:1` `# P1 RESULTS`

**ER-18**
- history: `MyTradingSys/research/rsi_kurisko_2026-10-09/RSI_HISTORY.md:1` `# RSI line of work`

**ER-19**
- code: `MyTradingSys/backtest/prob_table.py:1` 

