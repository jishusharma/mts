# GPT verdict registry audit ? 2026-10-16

Verdict: **BLOCKED**

## Checked

Read `scripts/dev/verdicts.py` parsing docstring (lines 1?31) and `MyTradingSys/research/VERDICTS.csv` (20 data rows). Checked study source availability for all 15 distinct study directories and recorded each available RESULT/RESULTS/PRE_REG/REPORT path in `MyTradingSys/research/layer_lab/gpt-verdict-registry-audit/VERDICTS_CHECKED.csv`.

## Row-by-row coverage

| # | study_dir / arm | Source files reviewed or located | Outcome |
|---:|---|---|---|
| 1 | b154_stratified_2026-10-09 / (study) | `b154_stratified_2026-10-09/RESULT.md` | BLOCKED: original UNPARSED fields need full extraction; report says only aggregate result files exist (RESULT.md:9?18). |
| 2 | eur_low_us_sweep_2026-10-14 / (study) | `eur_low_us_sweep_2026-10-14/RESULT.md` | MISMATCH: row includes holdout and side-by-side VAL/HOLDOUT numbers (RESULT.md:8, 20?21, 38); registry verdict FAIL at least agrees with study verdict text at line 62. |
| 3 | gross_effect_screen_2026-10-15 / T | `gross_effect_screen_2026-10-15/RESULT.md`; `PRE_REG.md` | Parsed values available in registry; source result primary cell is lines 5?12; one-run rule PRE_REG:17; family kill rule PRE_REG:81. |
| 4 | gross_effect_screen_2026-10-15 / C | same as row 3 | Parsed values available; derived control verdict rule documented PRE_REG:77?81. |
| 5 | mal_bb_mid_engulf_2026-10-16 / A1 | `mal_bb_mid_engulf_2026-10-16/RESULT.md`; `PRE_REG.md` | Registry values agree with primary table RESULT.md:7?14; PRE_REG one-run text and stop scope require full targeted extraction. |
| 6 | mal_bb_mid_engulf_2026-10-16 / A2 | same as row 5 | Registry values agree with primary table RESULT.md:7?14; stop scope needs extraction. |
| 7 | no_source_sweep_2026-10-09 / (study) | `no_source_sweep_2026-10-09/RESULT.md` | BLOCKED: narrative verdict is multi-parameter source audit, no statistical arm table (RESULT.md:8?31). |
| 8 | opr_bb_mtf_center_2026-10-16 / AU | `opr_bb_mtf_center_2026-10-16/RESULT.md`; `PRE_REG.md` | Parsed numeric/verdict values agree with RESULT.md:7?16; PRE_REG one-run/scope not fully adjudicated. |
| 9 | opr_bb_mtf_center_2026-10-16 / AD | same as row 8 | Numeric/verdict values agree with RESULT.md:7?16; registry kill_scope UNPARSED remains unresolved. |
| 10 | opr_preopen_tops_2026-10-16 / H1 | `opr_preopen_tops_2026-10-16/RESULT.md`; `PRE_REG.md` | Numeric/verdict fields agree with RESULT.md:7?16; one_run remains UNPARSED in registry. |
| 11 | opr_preopen_tops_2026-10-16 / H2 | same as row 10 | Numeric/verdict fields agree with RESULT.md:7?16; one_run remains UNPARSED. |
| 12 | opr_weekly_low_round_sweep_2026-10-16 / RL | `opr_weekly_low_round_sweep_2026-10-16/RESULT.md`; `PRE_REG.md` | Numeric/verdict fields agree with RESULT.md:7?14; kill scope unresolved. |
| 13 | opr_weekly_low_round_sweep_2026-10-16 / AS | same as row 12 | Numeric/verdict fields agree with RESULT.md:7?14; kill scope unresolved. |
| 14 | orderflow_views_2026-10-14 / (study) | `orderflow_views_2026-10-14/RESULT.md` | BLOCKED: no extraction of verdict and table values; report contains DEV/VAL/HOLDOUT test in RESULT.md:37?51. |
| 15 | published_strats_2026-10-13 / (study) | `published_strats_2026-10-13/RESULTS.md`; `PRE_REG.md` | Registry FAIL matches ?Nothing survives? at RESULTS.md:8?10; DEV only, VAL/HOLD never opened, holdout untouched (lines 5?6). Remaining UNPARSED arm statistics need extraction. |
| 16 | rsi_divergence_mtf_2026-10-09 / (study) | `rsi_divergence_mtf_2026-10-09/RESULT.md`; `REPORT.md` | BLOCKED: aggregate cells and thresholded verdict, no single registry n/mean/SE (RESULT.md:3?20). |
| 17 | t087_session_levels_2026-10-09 / (study) | `t087_session_levels_2026-10-09/RESULT.md` | BLOCKED: multiple event cells, registry does not identify one arm; RESULT.md:5?15. |
| 18 | t090_7h_2026-10-09 / (study) | `t090_7h_2026-10-09/RESULT.md` | BLOCKED: multiple anchor cells; summary verdict NOT robust at RESULT.md:36. |
| 19 | transcript_inventory_2026-10-09 / (study) | `transcript_inventory_2026-10-09/RESULT.md` | BLOCKED: inventory has no financial verdict or gross/SE fields (RESULT.md:8?16). |
| 20 | wlow_bounce_bbrsi60_2026-10-16 / EVENT | `wlow_bounce_bbrsi60_2026-10-16/RESULT.md`; `PRE_REG.md` | Parsed values match RESULT.md:1?14; one-run PRE_REG:38; result states DEV only line 3. |
| 21 | context_factors_2026-10-16 / C pooled | `context_factors_2026-10-16/RESULT.md`; `PRE_REG.md`; `REPORT.md` | Numeric registry values are in different units/fields than table; verdict INCONCLUSIVE and kill scope none supported RESULT.md:11?21, 80?83; split DEV at PRE_REG:104?106. |

## Split-read disclosures and gate effect

Study text explicitly reports VALIDATION/HOLDOUT results: `eur_low_us_sweep_2026-10-14` (RESULT.md:8, 20?21, 38); `orderflow_views_2026-10-14` (RESULT.md:37?51). `published_strats_2026-10-13` explicitly says those splits were never opened and project holdout untouched (RESULTS.md:5?6). DEV-only declarations include the 2026-10-16 screen results (for example `mal_bb_mid_engulf.../RESULT.md:5`, `opr_bb_mtf_center.../RESULT.md:5`, `opr_preopen_tops.../RESULT.md:5`, `opr_weekly_low_round_sweep.../RESULT.md:5`, `context_factors.../RESULT.md:3`).

The existing UNPARSED kill_scope on FAIL rows changes `verdicts.py check` because its documented check treats missing kill scope as family-wide. Known affected families include MAL-BB-MID-ENGULF, OPR-BB-MTF-CENTER, OPR-WEEKLY-LOW-ROUND-SWEEP, plus legacy FAIL study rows whose scopes were not fully checked. UNPARSED one_run can alter whether a new PRE_REG is blocked; this affects H1/H2 in OPR-PREOPEN-TOPS and the published strategies row. No follow-up cards were created because exact mismatches were not fully adjudicated.

## Block reason

The required complete source-by-source extraction and parsed-field comparison did not finish in this run; the checked CSV therefore still contains UNPARSED entries and cannot be treated as a corrected registry audit. Per the card?s blocked rule, this report records BLOCKED and the card is not marked done.
