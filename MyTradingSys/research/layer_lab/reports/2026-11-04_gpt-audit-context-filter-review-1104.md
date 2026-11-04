# Context-filter review audit — 2026-11-04

FIX-FIRST — 2 of the 33 directional study classifications do not meet the review's stated `CONTEXTED = 3+ YES dimensions` rule; 31 classifications match that rule. Carry is non-directional and excluded; four notes are not backtests.

## What was checked

Read `MyTradingSys/research/CONTEXT_FILTER_REVIEW_2026-11-04.md` (dimensions and rule: lines 7-8; study table: lines 37-69). Inspected each named study's Python runner/detector and its PRE_REG or result description where present. This was a source audit only: no market bars or outcomes were loaded and no backtest was run. Evidence references below give the registry row and the study's executable Python entry point; quoted dimension counts are from the registry table itself.

## Findings

| Study | Audit | Evidence / reason |
|---|---|---|
| rsi_divergence_mtf_2026-10-09 | MATCH — CONCEPT-ONLY | `CONTEXT_FILTER_REVIEW_2026-11-04.md:37`; detector `backtest/layers/rsi/rsi_divergence.py:1`; raw divergence run, no listed context gate. |
| t090_7h_2026-10-09 | MATCH — CONCEPT-ONLY | `CONTEXT_FILTER_REVIEW_2026-11-04.md:38`; anchor probe result `research/t090_7h_2026-10-09/RESULT.md:1`; all five dimensions N. |
| jala_layer_2026-10-31/trigger_study | MATCH — CONCEPT-ONLY | Registry `:39`; `research/jala_layer_2026-10-31/trigger_study/trigger_study.py:1-16`; MA is the trigger, not an independent trend gate. |
| tsfm_2026-11 | MATCH — CONCEPT-ONLY | Registry `:40`; `research/tsfm_2026-11/run_tsfm.py:29-70`; forecast signal has no context gate. |
| kurisko_2026-10-18 | MATCH — CONCEPT-ONLY | Registry `:41`; `research/kurisko_2026-10-18/count_events.py:80-121`; count-only rotation arms, no context dimension. |
| orderflow_views_2026-10-14 | MATCH — CONCEPT-ONLY | Registry `:42`; `research/orderflow_views_2026-10-14/study.py:12-18,175-176`; micro trend is part of raw signal definition only. |
| imbalance_qriptal_2026-10-16 | MATCH — CONCEPT-ONLY | Registry `:43`; `research/imbalance_qriptal_2026-10-16/imb.py:266-282`; new extreme is part of the event class, not a separate context filter. |
| tom_v2_gross_first_2026-11 | MATCH — CONCEPT-ONLY | Registry `:44`; `research/tom_v2_gross_first_2026-11/run_near_placebo.py:1-29`; near-band event count, no applied gate. |
| bb_top_reversal_2026-10-18 | MATCH — CONCEPT-ONLY | Registry `:45`; `research/bb_top_reversal_2026-10-18/count_gate.py:1`; blocked count/power work, no independent context gate. |
| opr_weekly_low_round_sweep_2026-10-16 | MATCH — CONCEPT-ONLY | Registry `:46`; `research/opr_weekly_low_round_sweep_2026-10-16/study.py:28,72,178-191`; reclaim/session are descriptive arms, not gates. |
| wavetrend_2026-10-17 | MATCH — PARTIAL-CONTEXT | Registry `:47`; `research/wavetrend_2026-10-17/atlas.py:33,103-111`; trend and HTF bins appear in cells, while entry is still signal-bar forward return. |
| published_strats_2026-10-13 | MATCH — PARTIAL-CONTEXT | Registry `:48`; `research/published_strats_2026-10-13/run_pub.py:182-195`; RSI/SMA arm and session blocks are separate rule arms; fewer than three YES dimensions. |
| mts_audit_2026-11-03 | MATCH — PARTIAL-CONTEXT | Registry `:49`; `research/mts_audit_2026-11-03/pitchfork_recheck.py:142,295`; resting-limit entry and VA_CONFLUENT comparison, below three YES. |
| fable_run6_powered_prereg | MATCH — PARTIAL-CONTEXT | Registry `:50`; `research/fable_run6_powered_prereg/e2_run.py:3-4,48`; S8 squeeze/break is one phase dimension. |
| tf_break_event_study_2026-10-30 | MATCH — PARTIAL-CONTEXT | Registry `:51`; `research/tf_break_event_study_2026-10-30/study.py:1,4,19`; break/reclaim/wick classes are phase, without three YES dimensions. |
| reclaim_close_stop_2026-11 | MATCH — PARTIAL-CONTEXT | Registry `:52`; `research/reclaim_close_stop_2026-11/reclaim.py:42,65`; break then reclaim event construction is phase only. |
| gross_effect_screen_2026-10-15 | MATCH — PARTIAL-CONTEXT | Registry `:53`; `research/gross_effect_screen_2026-10-15/screen.py:271-278`; delta flow is compared against location as one context dimension. |
| opr_preopen_tops_2026-10-16 | MATCH — PARTIAL-CONTEXT | Registry `:54`; `research/opr_preopen_tops_2026-10-16/study.py:21,29`; US session and break-speed arms, fewer than three YES dimensions. |
| opr_bb_mtf_center_2026-10-16 | MATCH — PARTIAL-CONTEXT | Registry `:55`; `research/opr_bb_mtf_center_2026-10-16/study.py:1,27`; center/trend comparisons do not reach three YES dimensions. |
| wlow_bounce_bbrsi60_2026-10-16 | MATCH — PARTIAL-CONTEXT | Registry `:56`; `research/wlow_bounce_bbrsi60_2026-10-16/study.py:1-4`; bounce/BB/RSI setup has two YES dimensions. |
| cryptocred_s3_2026-11 | MATCH — PARTIAL-CONTEXT | Registry `:57`; `research/cryptocred_s3_2026-11/cc_s3_run.py:1,21-22`; retest and S/R/fib confluence, fewer than three YES. |
| h3_ny_open_low_2026-10 | MATCH — PARTIAL-CONTEXT | Registry `:58`; `research/h3_ny_open_low_2026-10/BLOCKED.md:1`; registry explicitly records missing PRE_REG and NOT_IN_DATA entry semantics. No harness script was present in that study folder. |
| imbalance_qriptal_2026-10-16/filter | MATCH — PARTIAL-CONTEXT | Registry `:59`; `research/imbalance_qriptal_2026-10-16/filter/filter_join.py:90-114`; first-touch event and level-family filter, fewer than three YES dimensions. |
| pit_levels_2026-10-16 | MATCH — PARTIAL-CONTEXT | Registry `:60`; `research/pit_levels_2026-10-16/count_prior_va.py:10-13,121`; value-area edge setup is one setup/context dimension. |
| context_factors_2026-10-16 | **MISMATCH — should be PARTIAL-CONTEXT** | Registry `:61` marks TREND P, PHASE N, CONFL Y, SESSION Y: exactly two YES, not the stated three. Executable filter requires event plus F2/F3/F5/F6 (`research/context_factors_2026-10-16/study.py:160-165`); the several confluence factors still constitute one CONFL dimension. |
| context_factors_pit_2026-10-16 | **MISMATCH — should be PARTIAL-CONTEXT** | Registry `:62` marks TREND Y, PHASE P, CONFL Y, SESSION P: exactly two YES. The independent episode table names F2 confluence and F6 phase and F7 HTF alignment as separate contrasts (`research/context_factors_pit_2026-10-16/episode_counts.py:27-33`); the two partials do not satisfy 3+ YES. |
| eur_low_us_sweep_2026-10-14 | MATCH — CONTEXTED | Registry `:63`; `research/eur_low_us_sweep_2026-10-14/study.py:1-18,90-99`; retested-vs-single phase, level, and EU/US window dimensions yield three YES. |
| eur_low_us_sweep_followups_2026-10-18 | MATCH — CONTEXTED | Registry `:64`; `research/eur_low_us_sweep_followups_2026-10-18/followups.py:1-13,41-45`; sweep/reclaim, divergence, and pre-US dimensions yield three YES. |
| mal_bb_mid_engulf_2026-10-16 | MATCH — CONTEXTED | Registry `:65`; `research/mal_bb_mid_engulf_2026-10-16/study.py:24,82-89,107`; higher-TF RSI, phase/setup and BB-mid context meet three dimensions. |
| setup_alpha_beta_v2_2026-10 | MATCH — CONTEXTED at study level; arm caveat retained | Registry `:66`; `research/setup_alpha_beta_v2_2026-10/setup_v2.py:1,101-108,145,170-187`; Beta has sweep/CVD, level and session context; registry correctly says the two FAILs are Alpha. |
| meta_label_breaks_2026-10-31 | MATCH — CONTEXTED | Registry `:67`; `research/meta_label_breaks_2026-10-31/meta.py:29,37-50`; daily trend and event features include phase/setup and session inputs. |
| t087_session_levels_2026-10-09 | MATCH — CONTEXTED | Registry `:68`; `research/t087_session_levels_2026-10-09/RESULT.md:1`; failed first break is phase, prior-day level and time cutoff supply three reported dimensions. |
| rumers_2026-11-01 | MATCH — CONTEXTED | Registry `:69`; `research/rumers_2026-11-01/run_dev.py:33,122-136`; session-specific setups and daily SMA50 bias plus setup rules support the listed dimensions. |

The two mismatches are **class-label errors**, not evidence that the scripts lack context: both context-factor studies have two YES dimensions plus partial dimensions, and the registry rule counts YES dimensions. Fix those labels to PARTIAL-CONTEXT (or amend and justify the rule if the intended counting unit is different). The contexted count then falls from 9 to 7 and partial-context rises from 14 to 16, keeping the 33-study total.

## Scope accounting notes

`carry_basis_2026-10-18` is correctly `N/A` (non-directional), not one of the 33 classified directional rows (`research/carry_basis_2026-10-18/carry_basis.py:1-12`). The four note entries on registry line 71 are not backtests. The note at registry line 13 says only four studies state their window regime; this audit did not re-evaluate those window labels.

Follow-up cards created: none.
