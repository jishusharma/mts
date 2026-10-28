# T02 Look-ahead and time (DSA backtest audit, 2026-10-18, Lenovo DESKTOP-F7IU69N, no F: drive, no DEV data)

## 1. Summary
- Checked: every testnet layer in `build_default_registry` ({{N_LAYERS}} registry keys) with a cut-the-future test and a garbage-future test on synthetic seeded bars; a code sweep for look-ahead patterns; the clock rules of the studies.
- Found: no testnet layer shows look-ahead (0 repaint, 0 late, 0 poison differences where the test could fire). Five layers produced no events on synthetic bars, so they are untested, not cleared. The repo look-ahead gate has 132 forward-index/pivot hits that were never reviewed, and the session clocks disagree (lead L6 confirmed).
- Changes: no published verdict is shown to be wrong by this audit; the study detectors that read F:/MTS/data are BLOCKED-DATA (this machine has no DEV data), and a Lenovo-with-data rerun is posted to the desk.

## 2. Scope
| Item | Window | Method | Result |
|---|---|---|---|
| Testnet layers (table 3a) | synthetic seeded bars in %TEMP%/dsa_audit/T02 (seed 20261016), no market data | `scripts/T02/t02_truncation.py --quick` (about 50 cuts per layer, last-bar cuts dense; 10 cuts for the 1m history layers) | table 3a |
| Harness self-test | synthetic | `scripts/T02/t02_planted.py`: a planted peek at bars[i+1] and a planted centred pivot must FAIL, the causal detector must PASS | out/planted_selftest.txt: causal PASS, planted_next_close FAIL (11 late, 15 poison diffs), planted_centered FAIL (12 late, 34 poison diffs) |
| Static sweep | whole `MyTradingSys/*.py` | `git grep` of the card patterns plus a wider pattern set, and the repo's own `scripts/dev/lookahead_lint.py` | table 3c, out/sweep_raw.txt, out/sweep2_raw.txt, out/lint_output.txt |
| Clocks | code and result files, no event counts | read of session and bar-stamp rules | table 3d |
| Study detectors (1b) | DEV | truncation / poison | BLOCKED-DATA (section 5) |

## 3. Findings
| ID | Sev | Status | Evidence | Affects | Fix | Card |
|---|---|---|---|---|---|---|
| T02-F1 | S2 | SUSPECTED | `scripts/dev/lookahead_allowlist.tsv`: 118 `fwd-index` + 14 `pivot-right-neighbour` + 15 `fullsample-quantile` rows read "pre-existing, unreviewed" (233 rows total; `python scripts/dev/lookahead_lint.py`, out/lint_output.txt). Unreviewed fwd-index/pivot rows sit in files behind 1b verdicts: opr_bb_mtf_center study.py (4), mfe_exit_study.py (5), published_strats run_pub.py (5), tom_fabio_guidance matrix_q33.py (4), opr_preopen_tops study.py (3), eur_low_us_sweep study.py (3), orderflow_views study.py (3), plus layers/fabio/v3/models.py (5), fabio_volume_fvg.py (4), cc_setups.py (2), rsi_divergence.py (2) | The CI look-ahead gate gives no assurance for these hits: it only blocks NEW ones. Size of any bias: not measured (needs DEV data) | Review each unreviewed hit (safe / unsafe + reason) and run the truncation test on the study detector on a data machine | t02-f1-review-the-132-unreviewed-look-ah |
| T02-F2 | S3 | CONFIRMED (code read) | L6: `layers/tick/tick_extremes.py:80-94` session_tag fixed UTC minutes; `layers/session_levels/session_levels.py:23` and `run_session_levels.py:69-71` "US open 14:00 UTC" placeholder, reused by the TESTNET layer `session_levels` (`live_session_levels.py:5`); DST-aware: `fabio/v3/day_gates.py:60-64` ny_open_utc, `fabio_of_model.py:120`, `opr_*` ZoneInfo New York 09:30, `eur_low_us_sweep study.py:6`; fixed-UTC 00:00 day for `levels.py`, `wlow` ISO week | The US cash open is 13:30Z in US DST and 14:30Z otherwise; a fixed 14:00Z marker is 30 min late in DST (about 238 of 365 calendar days) and 30 min early outside it. Changed-label event counts: BLOCKED-DATA | One shared session module, DST-aware, used by all studies and layers | none (S3) |
| T02-F3 | S3 | CONFIRMED | Table 3a: `wlow_bounce|bbrsi60|1h`, `session_levels|session_levels|1m`, `fabio|v3_grid|1m`, `positioning|funding_cvd_fade|1h`, `rsi|malkan_bull|1h` produced 0 events on the synthetic bars | These testnet layers are NOT cleared of look-ahead; the test was vacuous for them | Hand-built event-forcing fixtures for those five (or the DEV rerun on a data machine) | t02-f3-event-forcing-fixtures-for-wlow-b |
| T02-F4 | S3 | CONFIRMED (code read) | `research/layer_lab/candle_close_2026-10-14/study.py:78,114,115,117` stamps bars by CLOSE (`label='right'`); the rest of the repo stamps by OPEN (`timeframe/tf_resample.py:90-140`, `wlow study.py:57-60`, `screen.py:4`) | Safe inside that study (table 3c), but a join of its stamps with any other study is off by one bar | Document the stamp in every output file name or column | none (S3) |
| T02-F5 | S3 | SUSPECTED | `mal_bb_mid_engulf study.py:163` variant grid "entry at the engulf close" | A fill at the signal bar's own close; the rule "entry at or after the close" holds only if that print is tradable. The primary arm (entry at next open, `study.py:20`) is not affected | Keep E1 as report-only | none (S3) |

Numbers: layers tested {{N_LAYERS}}; verdicts: {{TRUNC_SUMMARY}}. No FAIL. Counts are from `scripts/T02/out/trunc_log_*.txt`.

### 3a. Detector table, testnet layers (step 2, steps 3): truncation and poison on synthetic bars
Test: for each cut index k (closed bar, time T) the layer runs on all bars, on bars cut after k, and on bars cut after k with every later bar set to NaN, then with later open/high/low/close x10. `late` = event stamped <= T in the full run but absent in the cut run. `repaint` = event in the cut run missing from the full run. NaN/x10 diff = events stamped <= T differ from the cut run. A layer with 0 events is NOT DECISIVE.

{{TRUNC_TABLE}}

Files and functions behind the keys (all in `MyTradingSys/backtest/layers/alerts/live_runner_cli.py:432-528` unless noted): rsi `live_layers.rsi_level_layer` -> `rsi/rsi_events.py` (bars: closes, 1h/15m/5m); fabio cvd_absorption `fabio/fabio_cvd_absorption.py:45 cvd_absorption_events` (1h/15m, event at `confirmed_i`); fabio escalation `fabio_escalation.py:16` and volume_fvg `live_layers.py` `volume_fvg_layer` (1h/15m, declared confirm lag 1); session_momentum `session/session_momentum.py` (15m); funding_cvd_fade `positioning/funding_cvd_fade.py` (1h, funding fetch injected as-of the cut); malkan bull/bear `rsi/malkan_40_60.py` (1h); cryptocred sr_flip / fib_pullback / failed_msb `cryptocred/cc_setups.py` (1h/15m, t = entry_t); turn_of_candle `turn_of_candle/turn_of_candle.py` (1m); fabio v3_grid `live_runner_cli.py:200 make_fabio_v3_layer` (1m order-flow bars, flow injected); wlow_bounce `live_runner_cli.py:263 make_wlow_bounce_layer` -> `wlow_bounce/detector.py` (1h, fetch injected); rsi_divergence `live_rsi_divergence.py` (1h); bb_top_reversal `live_bb_top_reversal.py` (15m); session_levels `live_session_levels.py` (1m, needs 2900 bars); candle_close `live_candle_close.py` (1m, 10200 bars); levels confluence `live_levels_confluence.py` (1m, 24480 bars).
For the three history layers the cut run uses the same window start as the full run (window = last `need` bars up to the cut), so the comparison is like for like. The 1m history layers use 10 cuts (the 200-cut run is the script default without `--quick`).

### 3b. Detector table, study verdicts behind brief 1b (step 2 only; truncation BLOCKED-DATA)
| # | Study | Detector file | Bars / timeframe (from file headers and greps) | Truncation / poison |
|---|---|---|---|---|
| 1 | Session-extreme fade + 1m delta | gross_effect_screen_2026-10-15/screen.py | 1m DEV (tom_raw klines), index = (open_time - TS0)/60000 (`screen.py:4`) | BLOCKED-DATA |
| 2 | Pre-open tops | opr_preopen_tops_2026-10-16/study.py | 1m tape, New York 09:30 (`:29`) | BLOCKED-DATA |
| 3 | MAL BB mid engulf | mal_bb_mid_engulf_2026-10-16/study.py | 1m DEV, 5m/1h views | BLOCKED-DATA |
| 4 | BB MTF centre | opr_bb_mtf_center_2026-10-16/study.py | 1m with higher-timeframe bands | BLOCKED-DATA |
| 5 | Weekly-low round sweep | opr_weekly_low_round_sweep_2026-10-16/study.py | 1m | BLOCKED-DATA |
| 6 | Weekly-low bounce | wlow_bounce_bbrsi60_2026-10-16/study.py + layers/wlow_bounce/detector.py | 1h from 1m (`study.py:57`), entry open[t+1] (`:97-101`) | detector run on synthetic bars: NOT DECISIVE (table 3a); DEV run BLOCKED-DATA |
| 7 | Krown/Malkan counts | krown_malkan_g3_2026-10-16/event_counts.py | daily/weekly spot | BLOCKED-DATA |
| 8 | Qriptal calls | qriptal_2026-10-10/ledger.py, score_calls.py | calls ledger, n=0 scored | no detector |
| 9 | Candle close | layer_lab/candle_close_2026-10-14/study.py | 1m -> pandas resample, close-stamped | live twin `candle_close|candle_close|1m` PASS (1 event, weak); DEV BLOCKED-DATA |
| 10 | Levels sizing | levels_sizing_2026-10-14/probe.py | 1m footprint window | BLOCKED-DATA |
| 11 | Level hold rates | levels_confluence_2026-10-14/levels.py, levels_hold.py | 1m, UTC-day levels from bars before day open (`levels.py:1`) | live twin `levels|confluence|1m` PASS (29 events) ; DEV BLOCKED-DATA |
| 12 | Order-flow views | orderflow_views_2026-10-14/study.py | 1m, entry open of next 1m bar (`:20`, `:187`) | BLOCKED-DATA |
| 13 | EUR low US sweep | eur_low_us_sweep_2026-10-14/study.py | 1m, US open DST-aware (`:6`) | BLOCKED-DATA |
| 14 | MFE exits | mfe_exit_2026-10-13/mfe_exit_study.py | 1m | BLOCKED-DATA |
| 15 | Published strategies | published_strats_2026-10-13/run_pub.py | own resample to 1h/4h/1d (`:47`, `:519`) | BLOCKED-DATA |
| 16 | Tom/Fabio matrix | tom_fabio_guidance_2026-10-12/matrix_q33.py | 1m | BLOCKED-DATA |
The bar/timeframe column is read from file headers and greps, not from running the code.

### 3c. Static sweep (step 4). Raw: out/sweep_raw.txt (87 hits of the card pattern), out/sweep2_raw.txt (314 hits of a wider pattern set), out/lint_output.txt
Non-test hits of the card pattern: only `resample(` calls and one `shift(-1)`. `center=True`, `merge_asof`, `find_peaks`, `argrelextrema`, `iloc[i+1]` have no non-test hit (hits are in test_lookahead_lint.py, test_tf_resample.py and other test files, whose job is to plant them).
| Hit (file:line) | Class | Reason |
|---|---|---|
| backtest/layers/timeframe/tf_resample.py:90 `resample` (callers bigmoves.py:119, cc_htf_count.py:90, run_cc_setups.py:333, fabio/run_backtest.py:52, run_divergence_mtf.py:271, run_rsi_backtest.py:283/290, run_t055.py:316, trendline_core.py:39, tf_realdata_gate.py:58/142, kurisko count_events.py:77, positioning_c1 count_power.py:171) | SAFE | bucket stamped by its OPEN; a bucket is emitted only when `bucket_end <= last 1m close` (`:116-119`); gap buckets reported, not filled |
| backtest/layers/tick/tick_extremes.py:9 `resample` (callers :226, build_tiers.py:50) | SAFE | same open-stamp rule, closed buckets only (`:5-8`, `:36-40`) |
| research/layer_lab/candle_close_2026-10-14/study.py:78, 114, 115, 117 | SAFE | `closed='left', label='right'`: the label is the availability time; `known()` as-of joins on the bar START (`b.index - tf`), entry = `a.o` at the label (`forward`, `:93-100`) |
| research/context_factors_pit_2026-10-16/indep_pandas.py:71, 73 | SAFE | `label='left', closed='left'`, origin epoch / Monday |
| research/context_factors_2026-10-16/context_asof.py:631 `shift(-1)` in `_leak_fwd_next` | SAFE (planted-leak helper, docstring "tests only") | call sites not traced: SUSPECTED until grep of callers |
| research/context_factors_pit_2026-10-16/context_asof.py `_last_completed` (searchsorted of start+length <= T) | SAFE | last COMPLETED bucket only |
| fabio `find_swings` (fabio_cvd_absorption.py), used by cvd_absorption, escalation, volume_fvg | SAFE | pivot needs `right` future bars, but the event uses `confirmed_i = i + right`; truncation test PASS on all three (table 3a) |
| live_levels_confluence.py `build_levels` / `_agg_4h` fractals | SAFE | only days < d, fractal needs 2 closed 4h bars each side; truncation PASS |
| imbalance_qriptal imb.py:126, volume_2026-10-09 vdata.py:69, published_strats run_pub.py:47, wavetrend count_events.py:55, backtest/vp_pivot_probe.py:315, setup_catalog rsi_divergence_mtf_checks.py:23 (own `resample`) | NOT CLASSIFIED | own implementations, not read; their pivot/forward-index lines are in the unreviewed lint rows (T02-F1) |
| Wider pattern set: 314 hits; 233 allowlist rows, of which 46+17+7 reviewed and 118+14+15 unreviewed | see T02-F1 | |

### 3d. Clock table (step 5, lead L6). Counts of events that change label under the other convention: BLOCKED-DATA (needs the DEV bars)
| Study / module | Bar stamp | Session or clock rule | Source |
|---|---|---|---|
| tf_resample, screen.py, wlow, orderflow_views, mal_bb | open | UTC day, no DST | tf_resample.py:90; screen.py:4 |
| candle_close study | CLOSE (label right) | UTC epoch buckets, Monday week | study.py:78 |
| tick_extremes session_tag | open | fixed UTC minutes: Asian 00-08, European 08-13, overlap 13:00-16:30, American 16:30-21:00 | tick_extremes.py:80-94 |
| session_levels, live session_levels (TESTNET) | open | fixed 14:00 UTC "US open" placeholder | session_levels.py:23 |
| fabio v3, fabio_of_model | open | DST-aware NY 13:30/14:30Z, London 07/08Z | day_gates.py:60-72; fabio_of_model.py:120 |
| opr_preopen_tops, opr_bb_mtf_center, opr_weekly_low_round_sweep, tom_btc chart_lab | open | New York 09:30 via ZoneInfo | study.py:20-29 |
| eur_low_us_sweep | open | US open DST-aware, T0 = A - 90 min | study.py:6 |
| levels.py | open | UTC day, levels from bars before 00:00Z | levels.py:1 |
Lead L6 result: CONFIRMED (the five session definitions disagree; B102 fixed only fabio_of_model). Size on events: BLOCKED-DATA.

### 3e. Entry timing (step 6)
Code-level only (no ledger check done, see section 5): wlow_bounce enters at open of bar t+1 (`study.py:97-101`); orderflow_views at the open of the next 1m bar (`study.py:20, 187`); candle_close at the open of the minute equal to the bar's close label (`study.py:93-100`); mal_bb primary arm at the next open, variant E1 at the engulf close (T02-F5). The other studies were not read for this step: BLOCKED-DATA / not done. The 10-events-per-study hand check is not done.

## 4. Leads
| Lead | Result |
|---|---|
| L6 session clocks disagree | CONFIRMED, S3, table 3d and T02-F2; event counts BLOCKED-DATA |

## 5. Not checked
- BLOCKED-DATA: truncation and poison tests of the study detectors that load F:/MTS/data (3b rows 1-5, 7, 9-16); changed-label counts of the clock table; entry timing hand check on 10 events per study (needs the 1m bars). Desk row posted (target DSA, title starts "T02 BLOCKED-DATA").
- Layers with 0 events on synthetic bars (T02-F3).
- The default run uses about 50 cuts per layer, not 200; the 200-cut run is `python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/t02_truncation.py` (no flag) and was stopped for time (a 311-cut run on rsi was PASS).
- The own `resample` implementations listed in 3c as NOT CLASSIFIED.

## 6. Decisions taken
- DECISION (OURS): synthetic bars are a seeded random walk with small open gaps (with exact open == previous close the body-swing detectors find no swing at all). Seed 20261016.
- DECISION (OURS): the quick profile (about 50 cuts per layer, 10 for the 1m history layers, 10 for v3_grid) replaces the 200-cut profile because of the session cap; the script default stays 200.
- DECISION (OURS): a layer with 0 events is NOT DECISIVE, never PASS.
- DECISION (OURS): the lag column is read only when `late` > 0; the history layers use sparse cuts, which alias the lag. The raw log `out/trunc_log_levelsconfluence.txt` still carries the first-draft verdict FAIL-LAG (lag 6 from every-4th-bar cuts) with late=0 and repaint=0 at every cut; under the final rule it is PASS.
- DECISION (OURS): three rows were appended to `scripts/dev/lookahead_allowlist.tsv` for this audit's own harness lines (the harness slices the future on purpose; the planted-leak fixture peeks on purpose), reason written on each row.
- DECISION (OURS): the work tree was started twice by mistake; `mts-desktop-f7iu69n-dsa02-lenovo` is an unused duplicate tree, all work is in `...dsa02-lenovo-2`.

## 7. Bridge log
No AIBridge was used (Claude worker session on the Lenovo). No bridge rows.

## 8. Handover
1. Top fix: review the 132 unreviewed forward-index/pivot allowlist rows, starting with the studies behind 1b verdicts (T02-F1).
2. File: `scripts/dev/lookahead_allowlist.tsv`, then each study named in T02-F1.
3. Proving test: `scripts/T02/t02_truncation.py` extended with the study detectors on DEV on a machine that has F:/MTS/data (the desk row); plus event-forcing fixtures for the five NOT DECISIVE layers.
4. Risk: S1 would be a study whose event uses a bar after its stamp; none is shown, but 3b rows are untested.
5. Rerun after the fix: `python MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/t02_truncation.py` (200 cuts) and `python scripts/dev/lookahead_lint.py`.
