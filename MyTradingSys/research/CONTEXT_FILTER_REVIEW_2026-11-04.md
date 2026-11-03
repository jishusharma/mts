# Context-filter review of every backtest (operator 2026-11-04: "we back-tested not so smartly")

Operator's thesis (chat, login C JIS-NB, 11-04): most FAIL verdicts tested a concept without context (a raw trigger on every bar in every
regime), so the FAIL says nothing about the trader's claim, which assumes trend / phase, confluence, session and a retest entry. Example given:
WaveTrend (c30) bought zero-line crosses in a 5-week BTC downtrend. This file is the read of VERDICTS.csv (123 rows, 38 study_dirs) against
five context dimensions. Read by a Sonnet reader from each study's PRE_REG / RESULT / runner; numbers below are counts of that read, not re-runs.

Dimensions: TREND = higher-TF trend or regime gate; PHASE = range / breakout / retest / trend distinguished; CONFL = a second layer required;
SESSION = time-of-day gate; ENTRY = signal bar vs retest after the signal. CLASS: CONCEPT-ONLY (all NO or one PARTIAL), PARTIAL-CONTEXT (1-2 YES),
CONTEXTED (3+ YES). Y / P / N = yes / partial / no. Paths are under `MyTradingSys/research/`.

## Counts

| class | studies | VERDICTS rows | FAIL rows |
|---|---|---|---|
| CONCEPT-ONLY | 10 | 42 | 30 (20 of them one study, imbalance_qriptal) |
| PARTIAL-CONTEXT | 14 | 52 | 16 |
| CONTEXTED | 9 | 22 | 11 |
| not a backtest / carry | 5 | 7 | 1 |

Only 4 of 33 backtests say what regime their window was (jala, published_strats, rumers, t087). The rest: NOT_IN_DATA.

## Verdict on the thesis

- TRUE for 10 studies and 30 of 58 FAIL rows: the trader's context was never applied. Clearest: `rsi_divergence_mtf_2026-10-09` ran the raw
  divergence with no monthly / weekly RSI gate, while Malkan's rule (monthly and weekly RSI >= 60 bull, <= 40 bear, then the daily setup) is
  written in `malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:11-16`. That FAIL is a FAIL of our run, not of his rule.
- HALF-TRUE for WaveTrend: all 9 cells carried a bin (EMA200 with-trend on 5 cells, next-higher-TF WT zone on 4), but none had an RSI
  confluence, a daily / weekly regime gate, a session gate or a retest entry; it measured a fixed 12-bar return from the signal bar, gross.
- NOT TRUE for 11 FAIL rows: `eur_low_us_sweep`, `mal_bb_mid_engulf`, rumers R2 / R3 / R5 and meta_label already had trend, phase, confluence
  or session gates and still failed fee-net. Context does not fix everything.

## Table (CONCEPT-ONLY first)

| study_dir | family | best (rows) | TREND | PHASE | CONFL | SESSION | ENTRY | WINDOW | CLASS |
|---|---|---|---|---|---|---|---|---|---|
| rsi_divergence_mtf_2026-10-09 | RSI divergence, all TFs | FAIL (1) | N: "measures the raw signal only" (RESULT.md:20) | N | N | N | SIGNAL | 2022-01..2026-10, no split; regime NOT_IN_DATA | CONCEPT-ONLY |
| t090_7h_2026-10-09 | 7h anchor probe of RSI divergence | INC (1) | N | N | N | N | SIGNAL | 2022-01..2026-10 | CONCEPT-ONLY |
| jala_layer_2026-10-31/trigger_study | Jala 400D close and 200/400 cross | INC (12; 4 FAIL) | P: the 400D MA is the trigger itself | N | N | N | SIGNAL (close, hold h days) | DEV 2022-01..2024-07; "DEV was a bear market" (TRIGGER_RESULT.md:37) | CONCEPT-ONLY |
| tsfm_2026-11 | Chronos zero-shot forecast | INC (2; 1 FAIL) | N | N | N | N | SIGNAL | DEV 2022-01..2024-06 | CONCEPT-ONLY |
| kurisko_2026-10-18 | Kurisko Quad Rotation | BLOCKED (1) | N | N | N | N | SIGNAL | DEV; count only | CONCEPT-ONLY |
| orderflow_views_2026-10-14 | price vs CVD divergence, 1m/5m | FAIL (1) | P: micro trend only | N | N | N | SIGNAL (next 1m open) | DEV-only rerun 10-17 | CONCEPT-ONLY |
| imbalance_qriptal_2026-10-16 | Qriptal volume-anomaly candle fade | FAIL (20) | N | N | P: new 20-bar extreme | N | SIGNAL | 2022-01..2025-09 design | CONCEPT-ONLY |
| tom_v2_gross_first_2026-11 | Tom return-to-value, near-band placebo | FAIL (1) | N | P: first 5m close beyond prior-day value area | N | N | SIGNAL (a count) | DEV_EXT 2020-01..2021-12 | CONCEPT-ONLY |
| bb_top_reversal_2026-10-18 | 15m BB top-reversal short | BLOCKED (1) | N | N | N | N | SIGNAL (E1-E3) | DEV; blocked on cost | CONCEPT-ONLY |
| opr_weekly_low_round_sweep_2026-10-16 | prior-week-low and round-1000 sweep | FAIL (2) | N | P: reclaim classes descriptive only | N | N: US-open window descriptive only | SIGNAL (d=1) | DEV | CONCEPT-ONLY |
| wavetrend_2026-10-17 | WaveTrend atlas, 9 cells | INC (9; 4 FAIL) | P: 5 of 9 cells EMA200 with-trend (PRE_REG s.1, s.5) | P: W05/W06 centre-test | P: 4 cells next-higher-TF WT zone | N | SIGNAL (open t+1, 12 bars) | DEV, gross | PARTIAL-CONTEXT |
| published_strats_2026-10-13 | 62 published rules | FAIL (1) | P: Connors RSI(2) above SMA200 | N | N | Y: session-block arms | SIGNAL | 2021-01..2023-06; "one bull run and one bear" | PARTIAL-CONTEXT |
| mts_audit_2026-11-03 | Pitchfork 4H exact recheck | FAIL (1) | N | N | Y: VA_CONFLUENT vs UNFILTERED | N | RETEST-like (resting limit) | 2020-01..2024-06 | PARTIAL-CONTEXT |
| fable_run6_powered_prereg | Krown S8 squeeze break, 4h | INC (9) | N | Y: BBWP squeeze then break | N | N | SIGNAL | 2020-01..2024-06 | PARTIAL-CONTEXT |
| tf_break_event_study_2026-10-30 | swing break / reclaim / wick sweep | INC (18) | N | Y: H, R, W1 split | N | N | BOTH | DEV + VAL | PARTIAL-CONTEXT |
| reclaim_close_stop_2026-11 | reclaim at close, 4h/1D | INC (2) | N | Y: break then reclaim | N | N | SIGNAL | DEV | PARTIAL-CONTEXT |
| gross_effect_screen_2026-10-15 | session-extreme fade plus delta flow | INC (2; 1 FAIL) | N | N | Y: delta flow vs plain location | N: UTC-day anchor only | SIGNAL | DEV | PARTIAL-CONTEXT |
| opr_preopen_tops_2026-10-16 | pre-open tops, break speed | INC (2) | N | P: break-speed terciles | N | Y: US cash session | SIGNAL | DEV | PARTIAL-CONTEXT |
| opr_bb_mtf_center_2026-10-16 | 1h BB-mid touch in a lower-band trend | INC (2; 1 FAIL) | Y: 6 closes below a falling mid | P | Y: 30m centre-close | N | SIGNAL | DEV | PARTIAL-CONTEXT |
| wlow_bounce_bbrsi60_2026-10-16 | weekly-low break, bounce, hold under RSI 60 | INC (1) | N | Y | Y: BB upper plus RSI 52-60 | N | SIGNAL | DEV; 8 events | PARTIAL-CONTEXT |
| cryptocred_s3_2026-11 | CryptoCred S/R flip and fib pullback | BLOCKED (1) | P: MSB structure | Y: retest | Y: S/R flip plus fib | N | RETEST (resting limit) | DEV; blocked on power | PARTIAL-CONTEXT |
| h3_ny_open_low_2026-10 | NY open+180 min new low holds | BLOCKED (1) | N | Y | N | Y: NY open | NOT_IN_DATA (no PRE_REG) | DEV, n=35 | PARTIAL-CONTEXT |
| imbalance_qriptal_2026-10-16/filter | imbalance candle as a filter at levels | FAIL (2) | N | P: first touch | Y: 8 level families | N | SIGNAL | 2022-04..2024-06 | PARTIAL-CONTEXT |
| pit_levels_2026-10-16 | failed auction at prior-day value-area edge | BLOCKED (1) | N | Y | Y: VAH/VAL | N | SIGNAL (close) | DEV; blocked on power | PARTIAL-CONTEXT |
| context_factors_2026-10-16 | operator context composite | INC (1) | P: trend tag in the control key | N | Y: f2, f3, f5, f7 | Y: f7_session | SIGNAL (T+60 s) | DEV, 821 decision days | CONTEXTED |
| context_factors_pit_2026-10-16 | context factors on a level trade | UNPARSED (1) | Y: weekly htf_align | P | Y: F4, F5 | P: descriptive | SIGNAL | DEV | CONTEXTED |
| eur_low_us_sweep_2026-10-14 | retested low, then US-window break | FAIL (1) | N | Y: RETESTED vs SINGLE | Y: level L | Y: EU low, US window | SIGNAL (T0) | 2022-01..2026-10 | CONTEXTED |
| eur_low_us_sweep_followups_2026-10-18 | follow-ups A, B, C | BLOCKED (3) | N | Y: sweep then reclaim | Y: RSI divergence | Y: pre-US | SIGNAL | DEV; blocked on power | CONTEXTED |
| mal_bb_mid_engulf_2026-10-16 | BB-mid bounce, engulf, second break | FAIL (2) | Y: 1h and 4h RSI below 50 (PRE_REG s.2) | Y | Y | N | BOTH | DEV | CONTEXTED |
| setup_alpha_beta_v2_2026-10 | Alpha SMA200, Beta sweep + CVD | INC (4; 2 FAIL) | Alpha Y | Beta Y | Beta Y: PDH/PDL plus CVD | Beta Y: 07-21 UTC | SIGNAL | DEV + VAL | CONTEXTED (the 2 FAILs are Alpha) |
| meta_label_breaks_2026-10-31 | context features on tf_break events | INC (4; 3 FAIL) | Y: trend_d (daily SMA200) | Y: H/R/W1 | Y | Y: session | BOTH | DEV | CONTEXTED |
| t087_session_levels_2026-10-09 | failed first break of prior-day high/low before 14:00 UTC | INC (1) | N | Y | Y: prior-day level | Y: before 14:00 UTC | SIGNAL | 2022-01..2026-10; by-year table | CONTEXTED |
| rumers_2026-11-01 | 5 Rumers rules | INC (5; 3 FAIL) | Y: R4 daily SMA50 bias | Y: sweep then reversal bar | Y: PDH/PDL, VWAP+RSI, pitchfork | Y: 00:00 / 13:30 UTC opening range | SIGNAL (next 1m open) | DEV; "both Daily-SMA50 regimes" (DEV_CHECK.md:36) | CONTEXTED |
| carry_basis_2026-10-18 | funding carry | PASS (3) | n/a | n/a | n/a | n/a | n/a | DEV / VAL / HOLD | N/A (non-directional) |
| b154_stratified, no_source_sweep, transcript_inventory, netdelta_panel | notes | UNPARSED | not backtests | | | | | | N/A |

## Sourced context rules a re-run can use (SOURCED, not OURS)

| study to re-run | context rule | where it is written |
|---|---|---|
| rsi_divergence_mtf | monthly and weekly RSI >= 60 (bull) / <= 40 (bear) before the daily setup; buy on the retest of 40, not the touch | malkan_rsi_2026-10-31/MALKAN_RULES_2026-10-31.md:11-16; malkan_rsi_2026-09-28/DIVERGENCE_RESEARCH_2026-10-09.md:32-33 |
| tom_v2 | family A: the opening / pre-market push on no volume, by session | tom_transfer_2026-10-11/TOM_LAYER_V2_SPEC.md (decision list read only) |
| jala trigger_study | 400D as a gate for fractals F1-F4, not as the trigger | jala_layer_2026-10-31/FRACTAL_METHOD_JALA.md (not opened by the reader) |
| wavetrend c30 | retest after the dot plus RSI confluence, by session (operator 11-04, OURS until a transcript line is found) | OPERATOR_DECISIONS d-context-retest-1104 |
| opr_weekly_low_round_sweep, orderflow_views, tsfm | no trader rule: our own ideas | - |

## Reusable regime / session code (so no builder writes a fourth trend tag)

`backtest/layers/rsi/malkan_mtf.py` (weekly / monthly gate; DIVERGENCE_RESEARCH:81 says it is a 20-bar window, not Malkan's level test: fix
first); `research/context_factors_pit_2026-10-16/context_asof.py` (session_of, vol_regime_of, weekly htf_align, trend tag);
`backtest/tom_bt.py:290` trend_tag; `research/meta_label_breaks_2026-10-31/meta.py` features_at (trend_d, session hours);
`research/wavetrend_2026-10-17/count_events.py` (EMA200 with-trend bin); `backtest/layers/fabio/v3/day_gates.py`, `fabio/htf_context_live.py`;
`research/bb_state_map_2026-10/bb_state_study.py`; `research/c26_roadmap_2026-11-01/PRE_REG_C26_REGIME.md` (frozen regime rule, OURS).

## What follows (d-context-retest-1104)

1. One shared context harness (OURS until each gate is sourced): regime tag (daily SMA200 side + weekly / monthly RSI band), phase tag
   (range / break / retest from the tf_break classes), session tag, and a retest-entry mode (enter on the first pullback to the signal level
   within N bars, not on the signal bar). Built once in `backtest/research_kit.py`, tests first, reused by every re-run.
2. Re-run order (sourced first): rsi_divergence_mtf under Malkan's monthly / weekly gate; wavetrend c30 with retest + RSI + session;
   bb range-to-range (operator's edge claim: in a range the band-to-band move repeats; Tom: larger ranges by session), as a new PRE_REG.
3. Every new RESULT.md states the regime mix of its window (bull / bear / range weeks) in one line; the reader found it in 4 of 33.
4. Wavetrend reader note: the "contexted" claim is half true; the reader read PRE_REG and RESULT, not every runner.

Noticed by the reader: VERDICTS.csv labels imbalance_qriptal as DEV+VALIDATION+HOLDOUT while its README says HOLDOUT was not read;
orderflow_views still carries the CONTAMINATED header; h3_ny_open_low has no PRE_REG; fable_run6 C1-C8 and context_factors_pit are UNPARSED
in VERDICTS.csv; tf_break and meta_label share the same events (one piece of PHASE evidence, not two).
