DISAGREES=69 (quoted below), AGREES=354; 35 further DISAGREES-by-regex rows are document freeze/run dates or data-start notes, not window labels (excluded)

# Split-window scan (independent recount, DSA direct 2026-11-02)

Source: MyTradingSys/backtest/splits.py:1-12 and the constants at splits.py:30-37: DEV 2022-01-01 up to 2024-07-01 (exclusive), VALIDATION 2024-07-01 up to 2025-07-01, HOLDOUT from 2025-07-01 (DEV_START :30, DEV_END :34, VALIDATION_END :36, HOLDOUT_START :37).
Method: python over `git ls-files` (1408 files: 1335 system/tasks/**/*.json incl. archive, 73 PRE_REG*.md under research), regex for DEV/VALIDATION/VAL/HOLDOUT followed within 25 non-digit chars by a date range or a bound (`..`,`to`,`>=`,`after`,`before`). A row AGREES when all dates fall inside that label's months in splits.py. Month-granular check; text is quoted exactly (truncated regex match).
Caveat: many windows are deliberate other-asset or extended windows (DEV_EXT 2020-01.., Tom/DAX 2024-11.., session_flow 2025-10..): they DISAGREE with splits.py as written but splits.py:17-21 itself records that Tom/LC use 2024-12..2025-03. Listed, not judged.

| file:line | label | exact matched text | verdict |
|---|---|---|---|
| MyTradingSys/research/_archive/loose_2026-10/PRE_REG_HTF_REPLACE_2026-10-07.md:49 | DEV | `dev 2025-09-01 .. 2026-06-25` | DISAGREES |
| MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:10 | DEV | `DEV: daily 2020-01-01 .. 2024-06-30` | DISAGREES |
| MyTradingSys/research/fable_run6_powered_prereg/PRE_REG.md:1 | DEV | `DEV stage 2020-01..2024-06` | DISAGREES |
| MyTradingSys/research/fable_run6_powered_prereg/PRE_REG.md:63 | HOLDOUT | `Holdout:** DEV stage = 2020-01-01..2024-06-30` | DISAGREES |
| MyTradingSys/research/fractals_2026-10-31/f2/PRE_REG.md:17 | DEV | `DEV 2022-01..2025-06` | DISAGREES |
| MyTradingSys/research/gross_effect_screen_2026-10-15/PRE_REG.md:94 | DEV | `DEV (2024-12..2025-03` | DISAGREES |
| MyTradingSys/research/habib_plan_imbalance_2026-10-20/PRE_REG_HABIB_PLANS.md:55 | DEV | `DEV pool for t': 2022-01-01 .. 2025-08-31` | DISAGREES |
| MyTradingSys/research/habib_plan_imbalance_2026-10-20/PRE_REG_HABIB_PLANS.md:55 | DEV | `dev window (2025-09-01 .. 2026-06-25` | DISAGREES |
| MyTradingSys/research/habib_plan_imbalance_2026-10-20/PRE_REG_HABIB_PLANS.md:60 | DEV | `DEV (2022-01 .. 2025-08` | DISAGREES |
| MyTradingSys/research/habib_plan_imbalance_2026-10-20/PRE_REG_HABIB_PLANS.md:61 | VALIDATION | `VALIDATION (2025-09-01 .. 2026-06-25` | DISAGREES |
| MyTradingSys/research/habib_plan_imbalance_2026-10-20/PRE_REG_HABIB_PLANS.md:101 | DEV | `DEV 2022-01..2025-08` | DISAGREES |
| MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:63 | DEV | `DEV 2017-08..2024-06` | DISAGREES |
| MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:69 | DEV | `DEV BTC spot 2017-08 .. 2024-06` | DISAGREES |
| MyTradingSys/research/malkan_extract_2026-10-15/PRE_REG_MALKAN_GFS_BTC.md:17 | DEV | `DEV period (2017-08-17 to 2024-06-30` | DISAGREES |
| MyTradingSys/research/opr_preopen_tops_2026-10-16/PRE_REG.md:50 | DEV | `DEV only. VALIDATION (2024-07-01..2025-06-30` | DISAGREES |
| MyTradingSys/research/published_strats_2026-10-13/PRE_REG.md:8 | DEV | `DEV 2021-01-01..2023-06-30` | DISAGREES |
| MyTradingSys/research/published_strats_2026-10-13/PRE_REG.md:8 | VALIDATION | `VAL 2023-07-01..2024-06-30` | DISAGREES |
| MyTradingSys/research/session_flow_context_2026-10-18/PRE_REG.md:22 | DEV | `DEV 2025-10-01..2026-02-28` | DISAGREES |
| MyTradingSys/research/session_flow_context_2026-10-18/PRE_REG.md:23 | VALIDATION | `VALIDATION 2026-03-01..` | DISAGREES |
| MyTradingSys/research/tom_correlation_trick_2026-10-26/PRE_REG.md:25 | DEV | `DEV 2017-07-14..2024-01-11` | DISAGREES |
| MyTradingSys/research/tom_correlation_trick_2026-10-26/PRE_REG.md:25 | VALIDATION | `VAL 2024-01-12..2025-06-04` | DISAGREES |
| MyTradingSys/research/tom_correlation_trick_2026-10-26/PRE_REG.md:25 | VALIDATION | `VAL 2024-01-25..2025-06-11` | DISAGREES |
| MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_ARMS.md:88 | DEV | `Dev Period:** 2025-09-01 .. 2026-06-25` | DISAGREES |
| MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_ARMS.md:94 | DEV | `Dev Period:** 2024-11-04 .. 2026-04-10` | DISAGREES |
| MyTradingSys/research/tom_transfer_2026-10-11/PRE_REG_DAX.md:25 | DEV | `dev = 2024-11-04 .. 2026-04-10` | DISAGREES |
| MyTradingSys/research/tom_transfer_2026-10-11/vp_return/PRE_REG.md:42 | HOLDOUT | `Holdout: DEV only, 2022-01-01..2024-06-30` | DISAGREES |
| MyTradingSys/research/trendlines_2026-10-17/PRE_REG_TRENDLINES.md:124 | DEV | `DEV above. One VALIDATION (2024-07-01..2025-06-30` | DISAGREES |
| MyTradingSys/system/tasks/archive/gap-g2-dax-ask-candles.json:29 | DEV | `dev window 2024-11-04..2026-04-10` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-cc-msb-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-cc-msb-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-01` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-fabio-escalation-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-fabio-escalation-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-01` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-fabio-lvn-touch-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-fabio-lvn-touch-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-01` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-malkan-rsi-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-malkan-rsi-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-01` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-rsi-reclaim-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-rsi-reclaim-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-01` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-session-momentum-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-session-momentum-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-01` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-turn-of-candle-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-` | DISAGREES |
| MyTradingSys/system/tasks/archive/gptb-turn-of-candle-event-table.json:26 | HOLDOUT | `HOLDOUT bars (open on/after 2024-07-01` | DISAGREES |
| MyTradingSys/system/tasks/archive/gross-screen-refuse-a-changed-data-manif.json:27 | HOLDOUT | `holdout bars >= 2024-07-` | DISAGREES |
| MyTradingSys/system/tasks/archive/gross-screen-refuse-a-changed-data-manif.json:27 | HOLDOUT | `holdout bars >= 2024-07-01` | DISAGREES |
| MyTradingSys/system/tasks/archive/lc-levels-hold.json:28 | DEV | `DEV 2024-12..2025-03` | DISAGREES |
| MyTradingSys/system/tasks/archive/tom-btc-chart-lab.json:9 | DEV | `DEV 2024-12..2025-03` | DISAGREES |
| MyTradingSys/system/tasks/archive/tom-btc-data-check.json:27 | DEV | `DEV + VALIDATION (2024-12..2025-06` | DISAGREES |
| MyTradingSys/system/tasks/ask-p0-45-tf-break-event-study.json:34 | VALIDATION | `VAL 2024-07..2025-08` | DISAGREES |
| MyTradingSys/system/tasks/ask-p0-47-h3-ny-open-low-prereg.json:12 | DEV | `DEV 2020-01..2021-12` | DISAGREES |
| MyTradingSys/system/tasks/ask-p0-65-setup-alpha-beta-backtest.json:34 | DEV | `DEV 2019-09..2023-12` | DISAGREES |
| MyTradingSys/system/tasks/ask-p0-65-setup-alpha-beta-backtest.json:34 | VALIDATION | `VAL 2024-01..2025-08` | DISAGREES |
| MyTradingSys/system/tasks/fable-run6-powered-prereg.json:31 | HOLDOUT | `HOLDOUT reads (bars >= 2024-07-` | DISAGREES |
| MyTradingSys/system/tasks/fable-setups-pack-prep.json:28 | HOLDOUT | `HOLDOUT data', 'any bar at or after 2023-07-01` | DISAGREES |
| MyTradingSys/system/tasks/fill-rule-gap-frequency.json:28 | VALIDATION | `VALIDATION and HOLDOUT bars (DEV 2022-01-01..2024-06-30` | DISAGREES |
| MyTradingSys/system/tasks/fractal-hurst-regime-gate-f2.json:12 | DEV | `DEV 2022-01..2025-06` | DISAGREES |
| MyTradingSys/system/tasks/fractal-mtf-swing-confluence-f1.json:11 | DEV | `DEV 2022-01-01..2025-06-30` | DISAGREES |
| MyTradingSys/system/tasks/fractal-mtf-swing-confluence-f1.json:30 | DEV | `DEV 2022-01..2025-06` | DISAGREES |
| MyTradingSys/system/tasks/fractal-phase-analog-f3.json:12 | DEV | `DEV 2022-01..2025-06` | DISAGREES |
| MyTradingSys/system/tasks/gap-g3-shadow-fills.json:25 | HOLDOUT | `HOLDOUT >= 2024-07-` | DISAGREES |
| MyTradingSys/system/tasks/gap-g3-shadow-fills.json:25 | HOLDOUT | `HOLDOUT >= 2024-07-01` | DISAGREES |
| MyTradingSys/system/tasks/krown-dev-event-study-candles.json:11 | DEV | `dev-event-study. BTC DEV 2017-08..2024-06` | DISAGREES |
| MyTradingSys/system/tasks/krown-dev-event-study-levels.json:11 | DEV | `dev-event-study. BTC DEV 2017-08..2024-06` | DISAGREES |
| MyTradingSys/system/tasks/krown-dev-event-study.json:10 | DEV | `DEV 2017-08..2024-06` | DISAGREES |
| MyTradingSys/system/tasks/krown-s8-4h-e2-dev-run.json:13 | DEV | `DEV stage 2020-01-01..2024-06-30` | DISAGREES |
| MyTradingSys/system/tasks/krown-s8-4h-validation-read.json:15 | DEV | `DEV 2020-01..2024-06` | DISAGREES |
| MyTradingSys/system/tasks/lab-verify-trend-healthy-in-balance.json:30 | DEV | `DEV only (before 2025-04-` | DISAGREES |
| MyTradingSys/system/tasks/lab-verify-trend-healthy-in-balance.json:30 | DEV | `DEV only (before 2025-04-01` | DISAGREES |
| MyTradingSys/system/tasks/pooled-short-lookback-trend-tsmom-30d-sm.json:16 | DEV | `DEV/ETH, and opening 2025-07..2026-09` | DISAGREES |
| MyTradingSys/system/tasks/tom-btc-cards-window-rescope.json:11 | DEV | `DEV 2024-12..2025-03` | DISAGREES |

AGREES rows (sample of first 40 of 354):

| file:line | label | text |
|---|---|---|
| MyTradingSys/research/_archive/loose_2026-10/PRE_REG_HTF_REPLACE_2026-10-07.md:49 | HOLDOUT | `holdout 2026-06-26 .. 2026-09-26` |
| MyTradingSys/research/bb_top_reversal_2026-10-18/PRE_REG.md:3 | DEV | `DEV only (2022-01-01..2024-06-30` |
| MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:11 | VALIDATION | `VALIDATION: 2024-07-01 .. 2025-06-30` |
| MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:12 | HOLDOUT | `HOLDOUT: 2025-07-01 .. 2026-09-26` |
| MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:24 | DEV | `DEV 2022-01..2024-06` |
| MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:36 | DEV | `DEV 2022-01..2024-06` |
| MyTradingSys/research/carry_basis_2026-10-18/PRE_REG.md:17 | HOLDOUT | `holdout from 2025-07-` |
| MyTradingSys/research/carry_basis_2026-10-18/PRE_REG.md:17 | HOLDOUT | `holdout from 2025-07-01` |
| MyTradingSys/research/context_factors_2026-10-16/PRE_REG.md:95 | DEV | `DEV 2022-04-01..2024-06-30` |
| MyTradingSys/research/context_factors_2026-10-16/PRE_REG.md:105 | DEV | `DEV only (bar open 2022-01-01 .. 2024-06-30` |
| MyTradingSys/research/context_factors_2026-10-16/PRE_REG.md:105 | VALIDATION | `VALIDATION (2024-07-01 .. 2025-06-30` |
| MyTradingSys/research/context_factors_pit_2026-10-16/PRE_REG.md:104 | DEV | `DEV: bar open 2022-01-01 .. 2024-06-30` |
| MyTradingSys/research/context_factors_pit_2026-10-16/PRE_REG.md:106 | VALIDATION | `VALIDATION 2024-07-01 .. 2025-06-30` |
| MyTradingSys/research/context_factors_pit_2026-10-16/PRE_REG.md:107 | HOLDOUT | `HOLDOUT 2025-07-01 ..` |
| MyTradingSys/research/context_factors_pit_2026-10-16/PRE_REG_V3.md:3 | DEV | `DEV only (bar open 2022-01-01 .. 2024-06-30` |
| MyTradingSys/research/context_factors_pit_2026-10-16/PRE_REG_V3.md:19 | DEV | `DEV only (bar open 2022-01-01 .. 2024-06-30` |
| MyTradingSys/research/cryptocred_htf_2026-10/PRE_REG_CRYPTOCRED_HTF.md:13 | DEV | `DEV window (2022-01-01 to 2024-06-30` |
| MyTradingSys/research/cryptocred_htf_2026-10/PRE_REG_CRYPTOCRED_HTF.md:14 | DEV | `DEV fills (2022-01-01 to 2024-06-30` |
| MyTradingSys/research/cryptocred_htf_2026-10/PRE_REG_CRYPTOCRED_HTF.md:51 | DEV | `DEV window (2022-01-01 to 2024-06-30` |
| MyTradingSys/research/cryptocred_htf_2026-10/PRE_REG_CRYPTOCRED_HTF.md:176 | DEV | `DEV window: 2022-01-` |
| MyTradingSys/research/cryptocred_htf_2026-10/PRE_REG_CRYPTOCRED_HTF.md:177 | VALIDATION | `VALIDATION window: 2024-07-` |
| MyTradingSys/research/cryptocred_htf_2026-10/PRE_REG_CRYPTOCRED_HTF.md:178 | HOLDOUT | `HOLDOUT window: 2025-07-` |
| MyTradingSys/research/eagle_eyes_picture_2026-10-28/PRE_REG_C30.md:7 | DEV | `DEV only, 2022-01-01..2024-06-30` |
| MyTradingSys/research/eagle_eyes_picture_2026-10-28/PRE_REG_C30.md:35 | VALIDATION | `VALIDATION 2024-07-01..2025-06-30` |
| MyTradingSys/research/eagle_eyes_picture_2026-10-28/PRE_REG_C30.md:36 | HOLDOUT | `HOLDOUT 2025-07-01..2026-09-30` |
| MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/PRE_REG.md:7 | DEV | `DEV = bars before 2024-07-` |
| MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/PRE_REG.md:7 | VALIDATION | `VALIDATION 2024-07..2025-06` |
| MyTradingSys/research/eur_low_us_sweep_followups_2026-10-18/PRE_REG.md:7 | DEV | `DEV = bars before 2024-07-01` |
| MyTradingSys/research/fable_run6_powered_prereg/PRE_REG.md:3 | DEV | `DEV (2022-01..2024-06` |
| MyTradingSys/research/fable_run6_powered_prereg/PRE_REG.md:63 | VALIDATION | `VALIDATION 2024-07-01..2025-06-30` |
| MyTradingSys/research/fable_run6_powered_prereg/PRE_REG.md:63 | HOLDOUT | `HOLDOUT 2025-07-` |
| MyTradingSys/research/fable_run6_powered_prereg/PRE_REG.md:72 | DEV | `DEV 2022-01..2024-06` |
| MyTradingSys/research/fable_run6_powered_prereg/PRE_REG.md:73 | DEV | `DEV 2022-01..2024-06` |
| MyTradingSys/research/fast_track_2026-09-27/PRE_REG_FABIO_V3.md:13 | HOLDOUT | `holdout 2026-06-26..2026-09-28` |
| MyTradingSys/research/fractals_2026-10-31/p1b_rsi_feenet/PRE_REG.md:10 | DEV | `DEV 2022-01..2024-06` |
| MyTradingSys/research/fractals_2026-10-31/p1b_rsi_feenet/PRE_REG.md:39 | DEV | `DEV only: a bar at/after 2024-07-` |
| MyTradingSys/research/fractals_2026-10-31/p1b_rsi_feenet/PRE_REG.md:39 | DEV | `DEV only: a bar at/after 2024-07-01` |
| MyTradingSys/research/gross_effect_screen_2026-10-15/PRE_REG.md:91 | DEV | `DEV: bar open 2022-01-01 .. 2024-06-30` |
| MyTradingSys/research/gross_effect_screen_2026-10-15/PRE_REG.md:92 | VALIDATION | `VALIDATION: 2024-07-01 .. 2025-06-30` |
| MyTradingSys/research/gross_effect_screen_2026-10-15/PRE_REG.md:93 | HOLDOUT | `HOLDOUT: 2025-07-01 .. 2026-09-30` |
