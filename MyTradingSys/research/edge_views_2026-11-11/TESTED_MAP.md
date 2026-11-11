# Tested map: every backtest, census and trial in MyTradingSys/research

Read-only inventory, 2026-11-11 (worker task, no tests run, nothing shipped). Sources: `edge_hunt_2026-11-09/EDGE_TABLE.md` (the 15 trials), all 106 `RESULT*.md` files under `MyTradingSys/research` (top lines read), `tom_fabio_course_correction_2026-11-07/` (two census files, no RESULT), `adx_di_2026-11/CENSUS.md`, `value_area_acceptance_2026-11-05/RESULT.md`, `live_aid_review_2026-11-11/RESULT.md`. Paths are relative to `MyTradingSys/research/`. `NOT_STATED` = the file does not say. Numbers copied as written in the file's headline or table; no fee or sign was recomputed.

Counts: 115 rows. 100 counted (of these, 4 are BLOCKED or count-only with no return read: R22, R32, R33, R49). 5 NOT RUN. 10 rows are not trials (audit, UI card, review, or census of files).

## Table 1: one row per trial

Family key: fade-at-level, trend-following, breakout, mean-reversion, momentum, seasonality/time, forced-flow, cross-asset, carry, analyst-context, other. Counted: Y = counted, NOTRUN = frozen but not run, N = not a trial.

| ID | Name | File (under research/) | Family | Timeframe | Stop | Holding | Symbols | n trades | Net result | Verdict | Counted |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T01 | 7-star spinning top, BTC+ETH | edge_hunt_2026-11-09/results/eh-h1-spinning-top-7star/RESULT.md | breakout | 4h/1d | stop at signal-bar extreme (size NOT_STATED) | 3R target, 20-bar cap (cut in read) | BTC, ETH | 108 | mean net -0.217 R (SE 0.150) | FAIL | Y |
| T02 | 7-star MTF long | edge_hunt_2026-11-09/results/eh-h2-malkan-star-grades/RESULT.md | other | daily | NOT_STATED | NOT_STATED | BTC, ETH | 7 | mean net +1.058 R (SE 1.012) | INCONCLUSIVE | Y |
| T03 | 5-star MTF long | edge_hunt_2026-11-09/results/eh-h2-malkan-star-grades/RESULT.md | other | daily | NOT_STATED | NOT_STATED | BTC, ETH | 8 | mean net +0.072 R (SE 0.509) | INCONCLUSIVE | Y |
| T04 | First-touch sweep-reclaim fade, PDH/PDL/PWH/PWL | edge_hunt_2026-11-09/results/eh-h3-first-touch-sweep/RESULT.md | fade-at-level | NOT_STATED | NOT_STATED | NOT_STATED | NOT_STATED | 1150 | mean net -0.221 R (SE 0.043) | FAIL | Y |
| T05 | Fast-in short-time level fade, BTC 15m | edge_hunt_2026-11-09/results/eh-h4-speed-time-at-level/RESULT.md | fade-at-level | 15m | at extreme (size NOT_STATED) | 2R or 96 bars | BTC | 300 | mean net -0.086 R (SE 0.081) | FAIL | Y |
| T06 | RSI14 cross of SMA14, 4h BTC+ETH | edge_hunt_2026-11-09/results/eh-h5-rsi-ma-cross-trigger/RESULT.md | momentum | 4h | NOT_STATED | NOT_STATED | BTC, ETH | 1322 | mean net +0.048 R (SE 0.040) | INCONCLUSIVE | Y |
| T07 | Malkan 5-layer level short, 4h | no results folder (malkan_level_shorts_2026-11-09/REPORT.md is not a trial verdict) | fade-at-level | 4h | NOT_STATED | NOT_STATED | BTC, ETH | NOT_STATED | NOT RUN | NOT RUN as a frozen trial | NOTRUN |
| T08 | T07 mirrored as a long | no results folder | fade-at-level | 4h | NOT_STATED | NOT_STATED | BTC, ETH | NOT_STATED | NOT RUN | NOT RUN | NOTRUN |
| T09 | HTF support wick long, BTC 15m | edge_hunt_2026-11-09/results/eh-s2-wick-level-context/RESULT.md | fade-at-level | 15m | sweep extreme (44 bps quoted in text) | 2.5R target | BTC | 41 | mean net -0.581 R (SE 0.235) | FAIL | Y |
| T10 | HTF resistance wick short, BTC 15m | edge_hunt_2026-11-09/results/eh-s2-wick-level-context/RESULT.md | fade-at-level | 15m | sweep extreme (44 bps quoted in text) | 2.5R target | BTC | 47 | mean net -0.804 R (SE 0.215) | FAIL | Y |
| T11 | RSI 40/60 bounce with MTF confluence | edge_hunt_2026-11-09/results/eh-s3-rsi-line-confluence/RESULT.md | mean-reversion | 1h+4h | beyond approach extreme (size NOT_STATED) | 2.5R or 48 bars | BTC, ETH (spot) | 1588 | mean net -0.146 R (SE 0.042) | FAIL | Y |
| T12 | T11 against HTF bias | edge_hunt_2026-11-09/results/eh-s3-rsi-line-confluence/RESULT.md | mean-reversion | 1h+4h | beyond approach extreme (size NOT_STATED) | 2.5R or 48 bars | BTC, ETH (spot) | 1477 | mean net -0.133 R (SE 0.044) | FAIL | Y |
| T13 | Confluence score 0-5 slope, 1h/4h levels | edge_hunt_2026-11-09/results/eh-o1-confluence-dose-response/RESULT.md | fade-at-level | 1h+4h | median 64 bps (p10 25, p90 200) | stop/target/time exits (cap NOT_STATED) | BTC, ETH | 13851 | slope +1.04 R per point (SE 0.99) | INCONCLUSIVE | Y |
| T14 | 1h level fade, balance phase | edge_hunt_2026-11-09/results/eh-o2-phase-lens/RESULT.md | fade-at-level | 1h | NOT_STATED | NOT_STATED | NOT_STATED | 358 | mean net -0.232 R (SE 0.071) | FAIL | Y |
| T15 | MLK-S1 4h RSI-40 long, accumulation/bull | edge_hunt_2026-11-09/results/eh-o2-phase-lens/RESULT.md | mean-reversion | 4h | NOT_STATED | NOT_STATED | NOT_STATED | 51 | mean net +0.016 R (SE 0.247) | INCONCLUSIVE | Y |
| R01 | Price x OI x taker delta base rates, 60 min | anticipation_map_2026-11-05/RESULT.md | forced-flow | 1h events | NOT_STATED | 60 min | BTC | 21855 | NOT_STATED (fee-free; continuation 42-49%) | descriptive, no edge | Y |
| R02 | B154 stratified verdicts (census of result files) | b154_stratified_2026-10-09/RESULT.md | other | n/a | n/a | n/a | n/a | 0 per-event files | n/a | not computable (audit) | N |
| R03 | Bollinger dance, 5m shorts, exit comparison | bb_dance_2026-10-30/RESULT.md | mean-reversion | 5m | NOT_STATED | 4 exit rules (NOT_STATED) | BTC | 11051 | gross +0.168% to +0.178% per short (no fees) | descriptive, no edge | Y |
| R04 | Long-window BB range (A) and level arm (B), spot | bb_long_window_2026-11-04/RESULT_LONG.md | mean-reversion | 15m | NOT_STATED | NOT_STATED | BTC spot | 9008 | A signal net -0.128% [-0.155,-0.102] | A FAIL; B INCONCLUSIVE | Y |
| R05 | 15m BB pierce near US open, force and reach | bb_pierce_force_2026-10-29/RESULT.md | other | 15m | n/a | 8 h window | BTC | 1009 | no fees; reach 30% (all pierces) | descriptive | Y |
| R06 | BB range-to-band retest, level arm | bb_range_retest_2026-11-04/RESULT.md | mean-reversion | 15m | k x ATR limit (k 0.25/0.5/1.0) | NOT_STATED | BTC | 1187 signals (cells 175-244) | net -0.073% to -0.201% (9 cells) | INCONCLUSIVE (underpowered) | Y |
| R07 | BB range retest, BTC+ETH pool | bb_range_retest_eth_pool_2026-11/RESULT.md | mean-reversion | 15m | k x ATR limit | NOT_STATED | BTC, ETH | 351-512 per cell | net -0.044% to -0.156% (0.14 cost) | INCONCLUSIVE (underpowered) | Y |
| R08 | BB range-to-range (band to band) | bb_range_to_range_2026-11-04/RESULT.md | mean-reversion | 15m | bracket at band (size NOT_STATED) | NOT_STATED | BTC | 4256 | net -0.130% [-0.161,-0.099] | FAIL | Y |
| R09 | Bear-proxy context tuning, shorts from 15m W12 divergence | bear_proxy_context_tuning_2026-11-04/RESULT.md | other | 15m-1d | NOT_STATED | 10-bar exit | BTC, ETH spot | 823 (baseline ALL) | ALL pick +0.003% [-0.281,+0.287]; baseline -0.166% | NO DEFAULT CHANGES (underpowered) | Y |
| R10 | Big-candle stories, 1h and 5m | bigcandle_story_2026-11-05/RESULT.md | forced-flow | 1h/5m | n/a | 1h/4h/24h continuation | BTC | 843 big 1h events | none (fee-free; 43-60% vs 45-50% base) | descriptive, no trade rule | Y |
| R11 | Oversold 5m cascade, bounce and momentum-shift signals | bounce_shift_2026-10-30/RESULT.md | mean-reversion | 5m | n/a | 60 min / 4 h | BTC | 755 | no fees; up 60 min 55.8% | no signal anticipates bounce | Y |
| R12 | Daily upper-BB-edge short in 50-day downtrend | c31_multi_symbol_2026-11/RESULT.md | trend-following | daily | 1R = ATR14 (size NOT_STATED) | NOT_STATED | BTC, ETH | 17 | fee-net +0.71 R (sd 1.89) | UNDERPOWERED, parked | Y |
| R13 | Candle-close colour probability per TF | candle_flip_probability_2026-11/RESULT.md | other | 1m-1w | n/a | n/a | NOT_STATED | 277001 rows (G1) | gain <= 0.9% Brier; 15 cells survive m=48 | descriptive, no mechanism | Y |
| R14 | Funding carry basis | carry_basis_2026-10-18/RESULT.md | carry | 8h funding | n/a (3x liquidation case) | always-on | BTC | 911 days (DEV) | net annual 15.35 / 12.06 / 6.26% (unlevered) | PASS unlevered; 3x FAIL | Y |
| R15 | 5m/15m session x ladder x node census, 7y | census_5m_15m_session_ladder_2026-11-09/RESULT.md | fade-at-level | 5m/15m | 5m median 28.6 bps (p25 17.6) | node/BE/half/trail exits | NOT_STATED | 698 (5m), 601 (15m) | B1R -0.372 +-0.046 (5m); -0.249 +-0.050 (15m) | no edge (10 of 10 negative) | Y |
| R16 | Operator context composite C vs matched controls | context_factors_2026-10-16/RESULT.md | analyst-context | 1h decisions | daily-candle stop ladder (size NOT_STATED) | NOT_STATED | BTC | 1010 | mean net -0.1367 R (SE 0.0426) | INCONCLUSIVE | Y |
| R17 | Cowen band daily event study (4 ideas) | cowen_q4_2026-10-31/event_study/RESULT.md | analyst-context | daily | 1R = ATR14 daily | 30 bars | BTC, ETH | 21 / 22 / 20 / 19 | mean net -0.20 / +0.69 / +0.33 / -0.40 R | NOT ENOUGH DATA (all 4) | Y |
| R18 | Critical test wave 2: venue gap, funding census | critical_test_wave2_2026-10-30/RESULT.md | other | 1m | 1% stop (item 6) | 16 h cap | BTC perp (Binance vs Deribit) | 52 vs 55 events | +3.84 R vs +0.59 R (one month) | FINDING (audit) | N |
| R19 | CryptoCred 4h sr_flip, 10 symbols | cryptocred_s3_pooled_2026-11/RESULT_10SYM.md | breakout | 4h | ATR 1.0 (size NOT_STATED) | 1.5R bracket | 10 symbols | 1981 | pooled -0.0467 R (CI -0.1097..+0.0162) | FAIL | Y |
| R20 | Fast 1m drop, bounce to BB mid | drop_bounce_2026-10-29/RESULT.md | mean-reversion | 1m | NOT_STATED | 4 h | BTC perp | 813 | no fees; low breaks 48% of matches | descriptive, coin flip | Y |
| R21 | Retested low then US-window break, leveraged short tests | eur_low_us_sweep_2026-10-14/RESULT.md | breakout | 1m | NOT_STATED | US window | BTC | 99 retested / 1027 single | no net; short leg EXPLORATORY NEGATIVE | descriptive | Y |
| R22 | EUR low US sweep follow-ups (3 legs) | eur_low_us_sweep_followups_2026-10-18/RESULT.md | fade-at-level | 1m | sweep low (median 0.41-0.53%) | NOT_STATED | BTC | 133 (A) / 208 (B) | not run (power gate) | BLOCKED | Y |
| R23 | Fabio CVD claims U7 and U8 | fabio_cvd_2026-10-30/RESULT.md | forced-flow | 15m | n/a | n/a | BTC | 87552 bars | no fees; descriptive | mostly price drift, not CVD | Y |
| R24 | Krown S8 squeeze break on 4h, pooled | fable_run6_powered_prereg/RESULT.md | breakout | 4h | 10-bar stop; 0.56% floor | 138 target, 44 time (hold NOT_STATED) | BTC, ETH, SOL | 420 | mean net +0.1312 R (SE 0.0760) | INCONCLUSIVE (t +1.73 < 3.364) | Y |
| R25 | 1h Williams pivots with 4h/daily confluence (F1) | fractals_2026-10-31/f1/RESULT.md | fade-at-level | 1h | NOT_STATED | NOT_STATED | BTC | 7416 trades | fee-net negative (value NOT_STATED) | FAIL | Y |
| R26 | Rolling 1h Hurst gate on RSI-DIV-MTF and F1 fade (F2) | fractals_2026-10-31/f2/RESULT.md | mean-reversion | 1h | NOT_STATED | NOT_STATED | BTC | NOT_STATED | lift not positive (values in table) | NEGATIVE | Y |
| R27 | Phase-matched analog forecast, 1h (F3) | fractals_2026-10-31/f3/RESULT.md | other | 1h | n/a | 24-bar queries | BTC | 1190 queries | no edge (both below controls) | INCONCLUSIVE both arms | Y |
| R28 | 8h look-alikes of BB squeeze plus volume (F4) | fractals_2026-10-31/f4/RESULT.md | breakout | 8h | NOT_STATED | 3 horizons (NOT_STATED) | BTC spot | 5705 signal bars | no set passes; fade long FAILS | NEGATIVE / INCONCLUSIVE | Y |
| R29 | RSI-DIV-MTF and Krown per-phase split (P1) | fractals_2026-10-31/p1_split/RESULT.md | other | n/a | n/a | n/a | n/a | 0 cells run | NOT_STATED | BLOCKED, no cell run | NOTRUN |
| R30 | RSI-DIV-MTF with frozen 1R/2R/24-bar bracket (P1b) | fractals_2026-10-31/p1b_rsi_feenet/RESULT.md | mean-reversion | 1h/4h | 1R (size NOT_STATED) | 2R or 24 bars | BTC | 640 | pooled fee-net -0.229 R (gross -0.100) | honest negative | Y |
| R31 | Gross-effect screen, time in market | gross_effect_screen_2026-10-15/RESULT.md | other | 1m (h=60 min) | n/a | 60 min | BTC | NOT_STATED | DIFF -0.0500% (t -0.37) | INCONCLUSIVE | Y |
| R32 | H3 NY-open low, 10-symbol count | h3_ny_open_10sym_2026-11/RESULT.md | seasonality/time | NOT_STATED | NOT_STATED | 30 min hold | 10 symbols | 263 pooled (need 1804) | no return read | BLOCKED (count only) | Y |
| R33 | Habib plan hit rate | habib_plan_imbalance_2026-10-20/RESULT_PLAN_HIT_RATE.md | analyst-context | n/a | n/a | n/a | BTC | 0 DEV (9 sealed in HOLDOUT) | n/a | BLOCKED | Y |
| R34 | Qriptal volume-anomaly filter on level-hold layer | imbalance_qriptal_2026-10-16/filter/RESULT.md | fade-at-level | 1m | NOT_STATED | NOT_STATED | BTC | NOT_STATED (KEEP none) | layer-alone base -0.412 R (legacy) | FAIL | Y |
| R35 | Kurisko Quad Rotation DEV event study | kurisko_2026-10-18/RESULT.md | other | NOT_STATED | n/a | n/a | NOT_STATED | 0 cells run | n/a | NOT RUN (0 frozen cells) | NOTRUN |
| R36 | Large trades: buying vs absorption, 5m | large_trade_absorption_2026-10-30/RESULT.md | forced-flow | 5m | n/a | n/a | BTC perp | NOT_STATED | no fees; descriptive | descriptive, no edge | Y |
| R37 | Probability table, model vs baseline log-loss | layer_lab/prob_table_1103/RESULT.md | other | multi | NOT_STATED | NOT_STATED | NOT_STATED | NOT_STATED | NOT_STATED (table not parsed) | see table | Y |
| R38 | Level approach study (C15) | level_approach_2026-10-30/RESULT.md | fade-at-level | 1m | n/a | n/a | BTC | 10822 approaches | none (fee-free) | DESCRIPTIVE | Y |
| R39 | Level approach replicated, ETH and pooled | level_approach_eth_2026-11/RESULT.md | fade-at-level | 1m | n/a | n/a | BTC, ETH | 64 rows (4 AGREE, 20 DISAGREE, 40 UNDERPOWERED) | none | REPLICATES (descriptive) | Y |
| R40 | Level approach base rates prep (U1-U3) | level_approach_prep_2026-11-05/RESULT.md | fade-at-level | n/a | n/a | n/a | NOT_STATED | 887 approaches | none (fee-free) | descriptive, no edge | Y |
| R41 | Level story on history, turn/through scores | level_story_1110/RESULT.md | other | 15m | n/a | n/a | BTC spot | 180 days | net of 10 bp negative in almost all buckets | descriptive, no edge | Y |
| R42 | Support break after lower highs, 4h | lh_break_2026-10-30/RESULT.md | breakout | 4h | n/a | n/a | BTC perp | NOT_STATED | none (descriptive) | descriptive | Y |
| R43 | Live Aid map tab (UI card) | live_aid_map_2026-11-09/RESULT.md | other | n/a | n/a | n/a | n/a | n/a | n/a | UI card, not a trial | N |
| R44 | Live Aid pulse, SETUP FORMING vs matched null | live_aid_pulse_2026-11/RESULT.md | other | 1m | n/a | 30 min | BTC perp | 10093 | fee-net -14.1 bp [-14.7,-13.4] at 30 min | FAIL | Y |
| R45 | Live Aid review, 2026-11-11 | live_aid_review_2026-11-11/RESULT.md | other | n/a | n/a | n/a | BTC spot | 29 days | no fees, descriptive | review, not a backtest | N |
| R46 | Live not-fired audit | live_not_fired_2026-10-29/RESULT.md | other | n/a | n/a | n/a | n/a | n/a | n/a | live audit, not a trial | N |
| R47 | Midline bounce, bearish engulf, second break | mal_bb_mid_engulf_2026-10-16/RESULT.md | mean-reversion | n/a | NOT_STATED | 60 min | NOT_STATED | NOT_STATED | A1 FAIL; A2 FAIL | FAIL | Y |
| R48 | Malkan regular-divergence windows, DEV | malkan_window_dev_2026-11/RESULT.md | other | n/a | NOT_STATED | 10 bars | BTC, ETH | 4 events in OURS bands | not computed (power BLOCK) | INCONCLUSIVE (underpowered) | Y |
| R49 | Malkan window bands, pivot strength 3, 10 symbols | malkan_window_wide_2026-11/RESULT.md | other | n/a | NOT_STATED | 10 bars | 10 symbols | NOT_STATED | no return read | BLOCKED (count only) | Y |
| R50 | Meta-label on break trades, DEV | meta_label_breaks_2026-10-31/RESULT.md | breakout | per TF (table) | NOT_STATED | NOT_STATED | BTC | NOT_STATED (table not parsed) | cost 0.10% RT; no TF passed DEV | FAIL (per file) | Y |
| R51 | Meta-label rerun, Fabio Model C stand-in, pre-DEV | meta_label_dev_ext_2026-10-31/RESULT.md | other | NOT_STATED | NOT_STATED | NOT_STATED | NOT_STATED | NOT_STATED | best third +0.430 R (95% +0.028..+0.869) | PASSED (marginal) | Y |
| R52 | Michael trend lines vs detector events | michael_lines_2026-11/RESULT.md | analyst-context | 4h/1d | n/a | n/a | BTC | NOT_STATED | none (descriptive) | descriptive; go (conditional) for alert card | Y |
| R53 | CoinGlass net delta panel unit identification | netdelta_panel_2026-10-18/RESULT.md | other | n/a | n/a | n/a | n/a | 7 | n/a | UNIDENTIFIED (identification, not a trial) | N |
| R54 | No-source sweep B142-B145 (transcript grep) | no_source_sweep_2026-10-09/RESULT.md | other | n/a | n/a | n/a | n/a | 154 files grepped | n/a | audit, not a trial | N |
| R55 | OI pivot candidates, 1h and 4h | oi_pivot_2026-10-26/RESULT_1H4H.md | forced-flow | 1h/4h | n/a | n/a | BTC | 32 cells (10 powered) | none in powered cells (abs z < 2) | DESCRIPTIVE / NO EFFECT | Y |
| R56 | Which side OI is picking | oi_side_2026-10-30/RESULT.md | forced-flow | 5m | n/a | n/a | BTC | 39-169 per sub-cell | none (descriptive) | hypothesis only | Y |
| R57 | 1h touch of BB mid in lower-band trend (OPR) | opr_bb_mtf_center_2026-10-16/RESULT.md | mean-reversion | 1h | NOT_STATED | 120 min | NOT_STATED | NOT_STATED | AU INCONCLUSIVE; AD FAIL | INCONCLUSIVE | Y |
| R58 | Pre-open tops, break speed vs outcome (OPR) | opr_preopen_tops_2026-10-16/RESULT.md | seasonality/time | NOT_STATED | NOT_STATED | 60 min | NOT_STATED | NOT_STATED | H1 INCONCLUSIVE; H2 INCONCLUSIVE | INCONCLUSIVE | Y |
| R59 | Weekly low and round-1000 sweep (OPR) | opr_weekly_low_round_sweep_2026-10-16/RESULT.md | fade-at-level | NOT_STATED | NOT_STATED | 60 min | NOT_STATED | NOT_STATED | RL FAIL; AS FAIL | FAIL | Y |
| R60 | Price vs CVD divergence on 1m and 5m, OI split | orderflow_views_2026-10-14/RESULT.md | forced-flow | 1m/5m | n/a | 60 min | BTC | NOT_STATED | DIV minus CONTROL (value in DEV rerun file) | DEV rerun 10-17; 1m claim holds | Y |
| R61 | Copy-paste pitchforks vs random parallels, BTC 4H | pitchfork_2026-10-19/RESULT_COPY_FORK.md | other | 4h | n/a | n/a | BTC | 931 pivots | NOT_STATED (verdict not parsed) | NOT_STATED | Y |
| R62 | Copy-paste pitchforks, ETH 4H | pitchfork_2026-10-19/RESULT_COPY_FORK_ETH.md | other | 4h | n/a | n/a | ETH | 0 | no ETH count (data absent) | NOT RUN | NOTRUN |
| R63 | Pre-US failed-break short, 10 symbols | pre_us_failed_break_10sym_2026-11/RESULT.md | breakout | NOT_STATED | NOT_STATED | NOT_STATED | 10 USD-M symbols | NOT_STATED | MDD 97.9 vs BH 66.9 (fails) | FAIL | Y |
| R64 | Pre-US failed-break short, BTC | pre_us_failed_break_2026-10/RESULT.md | breakout | NOT_STATED | NOT_STATED | NOT_STATED | BTC | NOT_STATED | MDD 12.6% of K vs 66.9% BH | INCONCLUSIVE | Y |
| R65 | Pre-US Bollinger contraction, 15m | pre_us_squeeze_2026-10-29/RESULT.md | other | 15m | n/a | US session | BTC | NOT_STATED | none (descriptive) | descriptive | Y |
| R66 | Previous-close break, any TF | prev_close_break_2026-10-29/RESULT.md | breakout | any (48 variants) | NOT_STATED | NOT_STATED | BTC perp | NOT_STATED | NOT_STATED (12 bp RT cost) | NOT_STATED | Y |
| R67 | Published rule-based strategies, perp | published_strats_2026-10-13/RESULTS.md | other | 4h/1d | NOT_STATED | NOT_STATED | BTC perp | 62 variants | NOT_STATED (best DEV net in table) | NOT_STATED | Y |
| R68 | Reclaim at close, stop back beyond level | reclaim_close_stop_2026-11/RESULT.md | fade-at-level | 4h/1d | close beyond level (size NOT_STATED) | NOT_STATED | BTC USD-M | 4h long 62; 4h short 52 | 4h long +0.427% (CI -0.251..1.218) | INCONCLUSIVE (4h and 1D) | Y |
| R69 | RSI 40/60 line behaviour, cushions and plays | rsi_40_60_line_behaviour_2026-11-04/RESULT.md | mean-reversion | multi | NOT_STATED | NOT_STATED | BTC, ETH spot | NOT_STATED | NOT_STATED | NO DEFAULT PLAY (6 cells INCONCLUSIVE) | Y |
| R70 | RSI divergence on every timeframe, 2022-2026 | rsi_divergence_mtf_2026-10-09/RESULT.md | other | multi | NOT_STATED | forward 1/5/10/20 bars | NOT_STATED | only 2h Malkan bearish reaches 300 (301) | NOT_STATED | no edge on any TF reaching 300 | Y |
| R71 | RSI divergence MTF, Malkan gate, DEV | rsi_divergence_mtf_gated_2026-11-04/RESULT.md | other | multi | NOT_STATED | 10 bars | BTC, ETH | NOT_STATED | NOT_STATED | INCONCLUSIVE (underpowered) | Y |
| R72 | RSI divergence MTF gated, long window | rsi_divergence_mtf_gated_2026-11-04/RESULT_LONG.md | other | multi | NOT_STATED | 10 bars | BTC spot | NOT_STATED | NOT_STATED | INCONCLUSIVE (underpowered) | Y |
| R73 | Setup Alpha and Beta v2 (NO-SOURCE) | setup_alpha_beta_v2_2026-10/RESULT.md | other | 1m | NOT_STATED | NOT_STATED | BTC | Beta S1 DEV n 50 | NOT_STATED | Alpha FAIL; Beta S1 INCONCLUSIVE | Y |
| R74 | Sim-desk result cards (337 files) | sim_desk/api_review/RESULTS_CARDS_2026-11-03.md | other | n/a | n/a | n/a | n/a | 337 result files | n/a | summary of results, not a trial | N |
| R75 | Failed first break of prior-day high or low (T087) | t087_session_levels_2026-10-09/RESULT.md | fade-at-level | 1m | spike extreme (size NOT_STATED) | 60 min close-back window | BTC | 466 high / 447 low | base rates only | NOT_STATED | Y |
| R76 | 7h anchor levels, robustness (T090) | t090_7h_2026-10-09/RESULT.md | seasonality/time | NOT_STATED | NOT_STATED | NOT_STATED | NOT_STATED | 18 anchor cells | mean ~+0.7% (17 of 18 positive) | NOT robust (3 of 18 t>2) | Y |
| R77 | Per-TF break event study (hold, reclaim, wick sweep) | tf_break_event_study_2026-10-30/RESULT.md | breakout | 15m etc | NOT_STATED | NOT_STATED | BTC | NOT_STATED | no class fee-net positive | FAIL (per file) | Y |
| R78 | TOM-CTX-DIV correlation trick | tom_correlation_trick_2026-10-26/RESULT.md | other | n/a | NOT_STATED | 3 days | NOT_STATED | NOT_STATED | NOT_STATED (see table) | NOT-ADD | Y |
| R79 | Return to prior-day value (70/30 claim) | tom_transfer_2026-10-11/vp_return/RESULT.md | other | daily | n/a | NOT_STATED | BTC perp | 911 days | NOT_STATED (placebo 55.8% post hoc) | per PRE_REG rule (not parsed) | Y |
| R80 | Return to value, near-band placebo, 2020-21 | tom_v2_gross_first_2026-11/RESULT.md | other | daily | n/a | NOT_STATED | BTC perp | 730 days | CI lower -0.3 pp | FAIL | Y |
| R81 | Transcript inventory, v2 done vs total | transcript_inventory_2026-10-09/RESULT.md | other | n/a | n/a | n/a | n/a | n/a | n/a | inventory, not a trial | N |
| R82 | Chronos-Bolt zero-shot forecast, 4h/8h | tsfm_2026-11/RESULT.md | other | 4h/8h | n/a | 1 bar horizon | BTC perp | NOT_STATED | no fee-net edge | FAIL 4h; INCONCLUSIVE 8h | Y |
| R83 | US open levels reached in 2h, held 60 min | us_open_levels_2026-10-30/RESULT.md | seasonality/time | 1m | n/a | 60 min | BTC | 1230 weekdays | none (descriptive) | descriptive | Y |
| R84 | 5-day low sweep and 50% win-back | v_recovery_low_sweep_2026-11-04/RESULT.md | fade-at-level | 4h/24h/72h | n/a | 4h/24h/72h | BTC | 435 events | not computed (power BLOCK) | INCONCLUSIVE (underpowered) | Y |
| R85 | Value-area acceptance on BTC | value_area_acceptance_2026-11-05/RESULT.md | other | 30m | n/a | n/a | BTC spot | 493 (R) / 300 (A) | R 44% reach far VA; A 77% reach further half-width | descriptive | Y |
| R86 | Wall ledger (offline) | wall_ledger_2026-11/RESULT.md | other | n/a | n/a | n/a | n/a | tests only | n/a | offline tool, not a trial | N |
| R87 | WaveTrend DEV atlas, 9 cells | wavetrend_2026-10-17/RESULT.md | other | NOT_STATED | NOT_STATED | NOT_STATED | BTC | 9 cells | gross; 0 of 9 pass | INCONCLUSIVE | Y |
| R88 | WaveTrend 30m retest with trend gate and RSI confluence | wavetrend_c30_retest_2026-11-04/RESULT.md | other | 30m | NOT_STATED | 12 bars | NOT_STATED | 48 pooled + 192 session cells | 0 cells clear the rule | INCONCLUSIVE (underpowered) | Y |
| R89 | WaveTrend 30m retest, spot long window | wavetrend_c30_retest_2026-11-04/RESULT_LONG.md | other | 30m | NOT_STATED | 12 bars | BTC spot | NOT_STATED | NOT_STATED | INCONCLUSIVE (underpowered) | Y |
| R90 | Prior-week low bounce, long, BB+RSI 60 | wlow_bounce_bbrsi60_2026-10-16/RESULT.md | mean-reversion | 1h | NOT_STATED | 4 h | BTC | 8 | NOT_STATED | INCONCLUSIVE (n 8 < 10) | Y |
| R91 | WaveTrend 30m sequence | wt30_sequence_2026-10-30/RESULT.md | other | 30m | NOT_STATED | NOT_STATED | NOT_STATED | NOT_STATED | no fees; descriptive | descriptive | Y |
| R92 | WaveTrend crosses on 15m and 30m | wt_15m_30m_1110/RESULT.md | other | 15m/30m | n/a | n/a | NOT_STATED | NOT_STATED | 50% coin flip; 5-10 bp tilt on 15m | below fee, not pursued | Y |
| R93 | WT 30m lower-high divergence short | wt_bible_studies_2026-11-04/wt30_div_short/RESULT.md | other | 30m | n/a | n/a | BTC | 183 event-days | NOT_STATED | INCONCLUSIVE (power BLOCK) | Y |
| R94 | WT cycle clock, counts | wt_bible_studies_2026-11-04/wt_cycle_clock/RESULT.md | other | n/a | n/a | n/a | BTC | counts only | n/a | COUNT-ONLY | Y |
| R95 | WT multi-timeframe cycle nesting | wt_bible_studies_2026-11-04/wt_mtf_nesting/RESULT.md | other | multi | NOT_STATED | NOT_STATED | BTC | NOT_STATED | NOT_STATED | FAIL | Y |
| R96 | WT extreme cross, bounce size 1m/5m/15m | wt_extreme_cross_2026-11/RESULT.md | mean-reversion | 1m/5m/15m | NOT_STATED | NOT_STATED | BTC | 135 cells | NOT_STATED (verdict not parsed) | NOT_STATED | Y |
| R97 | WT extreme cross vs volatility-matched baseline | wt_extreme_cross_volmatch_2026-11/RESULT.md | mean-reversion | NOT_STATED | NOT_STATED | NOT_STATED | BTC, ETH | NOT_STATED | NOT_STATED | VOLATILITY-ONLY | Y |
| A01 | Auction-context classifier census, 1h | tom_fabio_course_correction_2026-11-07/AUCTION_CENSUS_1108.md | fade-at-level | 1h | structural sweep extreme, no buffer | 24 bars, 1R target | NOT_STATED | 1871 gate-pass (7y) | -0.087 R fee-net (SE 0.022) | descriptive census, no strategy claim | Y |
| A02 | Auction census 5m and 15m, session blocks, node exits | tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md | fade-at-level | 15m | 40 bps stops | node / BE / half-off | NOT_STATED | 1484 (15m) | -0.11 R maker; -0.36 R taker (t -5.2) | NO EDGE | Y |
| A03 | ADX/DI 2d cross census | adx_di_2026-11/CENSUS.md | trend-following | 2d (1d vs 2d) | n/a | 30 2d bars swing window | BTC | 165 cascade events; 17 recent | none (no PnL, context layer) | descriptive, no edge claim | Y |

## Table 2: counted trials per family x timeframe bucket

Bucket = the timeframe the file's headline reads (the finest one for single-TF rows; 8h placed in 4h; carry placed in daily+ because its mark-to-market is daily). `n/a` = timeframe not stated. Row totals sum to the 100 counted trials.

| Family | <15m | 15m-1h | 4h | daily+ | n/a | total |
|---|---:|---:|---:|---:|---:|---:|
| fade-at-level | 7 | 8 | 2 | 0 | 2 | 19 |
| breakout | 1 | 1 | 5 | 0 | 4 | 11 |
| mean-reversion | 4 | 10 | 1 | 0 | 3 | 18 |
| trend-following | 0 | 0 | 0 | 2 | 0 | 2 |
| momentum | 0 | 0 | 1 | 0 | 0 | 1 |
| seasonality/time | 2 | 0 | 0 | 0 | 2 | 4 |
| forced-flow | 3 | 4 | 0 | 0 | 0 | 7 |
| cross-asset | 0 | 0 | 0 | 0 | 0 | 0 |
| carry | 0 | 0 | 0 | 1 | 0 | 1 |
| analyst-context | 0 | 1 | 1 | 1 | 1 | 4 |
| other | 3 | 11 | 3 | 4 | 12 | 33 |
| **total** | **20** | **35** | **13** | **8** | **24** | **100** |

## Gaps (cells with 0 or 1 counted trial, counts only)

- cross-asset: 0 trials in every bucket.
- momentum: 1 trial (T06, 4h). 0 in <15m, 15m-1h and daily+.
- carry: 1 trial (R14, daily+). 0 in every other bucket.
- trend-following: 2 trials (R12, A03), both daily+. 0 in <15m, 15m-1h and 4h.
- seasonality/time: 4 trials. 0 in 15m-1h, 4h and daily+.
- analyst-context: 4 trials. 0 in <15m, 1 in 4h, 1 in daily+.
- daily+ overall: 8 trials, 4 of them "other". fade-at-level, breakout, mean-reversion and forced-flow each have 0 at daily+; forced-flow also has 0 at 4h.
- Not in any bucket: 24 counted trials state no timeframe (n/a), and 5 frozen trials were never run (T07, T08, R29, R35, R62).

## Not counted

- Not trials (N): R02 b154 census of result files, R18 critical-test audit, R43 Live Aid map UI, R45 Live Aid review (descriptive, no backtest), R46 live not-fired audit, R53 net-delta unit identification, R54 no-source transcript sweep, R74 sim-desk result cards, R81 transcript inventory, R86 wall-ledger offline tool.
- NOT RUN: T07 and T08 (no results folder; `malkan_level_shorts_2026-11-09/REPORT.md` is a 10-arm screen, not a trial verdict, nearest count n=37, +0.13 R), R29 (0 cells), R35 Kurisko (0 frozen cells, refused), R62 pitchfork ETH (data absent on the machine).
- 29 folders hold a PRE_REG with no RESULT file in the same folder. Not counted; some may hold results in a subfolder (not checked): bb_top_reversal_2026-10-18, c26_roadmap_2026-11-01, candle_patterns_2026-10-04, context_factors_pit_2026-10-16, cryptocred_htf_2026-10, eagle_eyes_picture_2026-10-28, fast_track_2026-09-27, jala_layer_2026-10-31, krown_audit_2026-10-22, krown_free_2026-10-31, krown_ta101_2026-10-13, layer_lab/candle_close_corrected_2026-10-14, layer_lab/context_fix1_stop_strata, layer_lab/context_fix2_mde_rule, layer_lab/kurisko_quad_1103, malkan_extract_2026-10-15, meta_label_tom_fabio_2026-10-31, mtf_lead_lag_2026-11-09, pit_levels_2026-10-16, positioning_c1_2026-10, rumers_2026-11-01, session_flow_context_2026-10-18, tom_fabio_course_correction_2026-11-07, tom_fabio_guidance_2026-10-12, tom_swing_2026-11-09, tom_transfer_2026-10-11, trendlines_2026-10-17, volume_2026-10-09, wavetrend_2026-10-17/c1v2.

## Notes

- A02 (`tom_fabio_course_correction_2026-11-07/CENSUS_5M15M_1109.md`) and R15 (`census_5m_15m_session_ladder_2026-11-09/RESULT.md`) carry the same card id, `census-5m-15m-7y-session-ladder-1109`, and report different trade counts (1484 vs 698 and 601 headline events). Both are counted here; they may be the same run read two ways.
- EDGE_TABLE says 8 FAIL and 5 INCONCLUSIVE. Its own note says PLAN_24H had 9 FAIL and 4 INCONCLUSIVE; the RESULT files give 8 and 5.
- Stop and symbol fields are mostly NOT_STATED. Where a file states a stop, it is in bp or % of price (for example 64 bps median, 0.56% floor, 40 bps); no stop is stated in USD.
