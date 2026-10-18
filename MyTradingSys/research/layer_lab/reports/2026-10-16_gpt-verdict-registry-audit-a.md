# GPT verdict registry audit A ? 2026-10-16

**FIX-FIRST**

Audited rows 1?10 only. The checked copy is `MyTradingSys/research/layer_lab/gpt-verdict-registry-audit/VERDICTS_CHECKED_a.csv`; it retains the registry columns, adds `source`, and replaces answerable `UNPARSED` values. The registry and `verdicts.py` were not edited. `NOT_IN_DATA` means the permitted study text did not provide the field; no values were inferred.

## Parser and method

Read `scripts/dev/verdicts.py:1-24` for the parser and gate rules, and `scripts/dev/verdicts.py:292-317` for the exact `check` behavior. Read `MyTradingSys/research/VERDICTS.csv` rows 1?10 (header and rows 2?11). For every row, read its own `RESULT.md`; also read `PRE_REG.md` where present. Cross-checked the shared DEV/VALIDATION/HOLDOUT boundaries at `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md:21-23`. Read the supplied cross-reference `MyTradingSys/research/fable_audit_2026-10-16/FABLE_RUNS_AUDIT.md:1-4, 1.3` (not a substitute for a study's own source).

## Row-by-row results

| Row | Study files read | split_read | n; gross mean; SE | verdict | one_run; kill_scope | Existing parsed-field check |
|---:|---|---|---|---|---|---|
| 1 | `b154_stratified_2026-10-09/RESULT.md:7-12,20-48` | NOT_IN_DATA | NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA | NOT_IN_DATA | no (no PRE_REG); NOT_IN_DATA | No parsed values to compare. The report concerns missing per-event records, not a trade-result arm. |
| 2 | `eur_low_us_sweep_2026-10-14/RESULT.md:8-9,19-39,62-68` | DEV+VALIDATION+HOLDOUT | NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA | FAIL | yes; NOT_IN_DATA | Existing split and verdict MATCH. Existing `one_run=no` is **MISMATCH**: RESULT says one definition, one run (:8). No arm-level n/mean/SE table exists; aggregate short-leg means do not identify the requested registry arm fields. |
| 3 | `gross_effect_screen_2026-10-15/RESULT.md:1-12,50`; `PRE_REG.md:17,73-95` | DEV | 40; -0.0568; 0.1304 | INCONCLUSIVE | yes; `FAIL/INCONCLUSIVE: stop; no detector, chart, layer or management work follows on this family.` | Newly filled fields read from the primary T row (:6-8) and single-run PRE_REG (:17). No previously parsed field to check. |
| 4 | Same as row 3 | DEV | 1439; -0.0081; 0.0246 | FAIL | yes; same stop sentence as row 3 | Control row C is FAIL under its own criteria: RESULT :10 and PRE_REG :79-81; Fable audit section 1.3 independently notes T INCONCLUSIVE and C FAIL. Study headline INCONCLUSIVE does not replace the arm verdict. |
| 5 | `mal_bb_mid_engulf_2026-10-16/RESULT.md:5-16`; `PRE_REG.md:23-44` | DEV | 1179; 0.0124; 0.0212 | FAIL | yes; NOT_IN_DATA | Parsed n/mean/SE/verdict MATCH the primary A1 row (:13); split DEV MATCH (:5). No FAIL-stop scope sentence was found in the permitted PRE_REG/RESULT. |
| 6 | Same as row 5 | DEV | 807; 0.0143; 0.0257 | FAIL | yes; NOT_IN_DATA | Parsed n/mean/SE/verdict MATCH the primary A2 row (:14); split DEV MATCH (:5). No FAIL-stop scope sentence was found in the permitted PRE_REG/RESULT. |
| 7 | `no_source_sweep_2026-10-09/RESULT.md:1-36` | NOT_IN_DATA | NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA | NOT_IN_DATA | no (no PRE_REG); NOT_IN_DATA | No trade-result verdict arm or split appears; this is a source audit. |
| 8 | `opr_bb_mtf_center_2026-10-16/RESULT.md:5-16`; `PRE_REG.md:23-45` | DEV | 194; 0.0196; 0.0824 | INCONCLUSIVE | yes; NOT_IN_DATA | Parsed n/mean/SE/verdict MATCH the primary AU row (:13); split DEV MATCH (:5). |
| 9 | Same as row 8 | DEV | 282; 0.0322; 0.0397 | FAIL | yes; NOT_IN_DATA | Parsed n/mean/SE MATCH the primary AD row (:14); CSV verdict FAIL MATCHES the row verdict (study headline is INCONCLUSIVE because AU is inconclusive). Split DEV MATCH (:5). |
| 10 | `opr_preopen_tops_2026-10-16/RESULT.md:5-16,152-158`; `PRE_REG.md:29-50` | DEV | 105; -0.0111; 0.0929 | INCONCLUSIVE | yes; NOT_IN_DATA | Parsed n/mean/SE/verdict MATCH the primary H1 row (:13); split DEV MATCH (:5). |

The requested `gross_mean_pct` is taken from the study's reported mean G field; it is not net of the registry's separate cost column. Cost values were not changed. For rows 1, 2, and 7 the sources do not provide a matching arm-level trio, so all three remain `NOT_IN_DATA`.

## Split exposure and check behavior

- Row 2 is the only one of rows 1?10 whose own study result reports VALIDATION and HOLDOUT outcome numbers: break rates DEV 53%, VAL 48%, HOLDOUT 72% (RESULT :20-21), and retested-short means DEV +0.10%, VAL -0.37%, HOLDOUT +0.01% (RESULT :37-39). Row 2 is therefore recorded as `DEV+VALIDATION+HOLDOUT`.
- Row 2's corrected `one_run=yes` changes the printed `one_run` value for a matching PRE_REG. It does not change the gate's block outcome for this row, because its corrected verdict is FAIL as well. The mismatch follow-up is `correct-verdict-registry-one-run-for-eur`.
- Rows 5, 6, and 9 have FAIL verdicts but no explicit kill-scope sentence in their own permitted study text, so `kill_scope=NOT_IN_DATA`. Under `verdicts.py check` a FAIL with any kill_scope other than literal `none` blocks a matching new PRE_REG; the parser docstring states missing scopes are UNPARSED and family-wide. Keep those families treated as blocking until their scope is explicitly documented. Rows 3?4 contain a broad stop sentence; row 4's source scope spans beyond its C arm, which is itself a registry-scope concern but not rewritten here.
- Row 8 is INCONCLUSIVE at n=194 and row 10 at n=105, consistent with their PRE_REG power rule. The validation/holdout exclusion is explicit in their respective study text.

## Findings and follow-up

| Severity | Evidence | Finding | Follow-up |
|---|---|---|---|
| HIGH | `eur_low_us_sweep_2026-10-14/RESULT.md:8`; existing registry row 3 | `one_run` is `no` in the registry although the study says one definition, one run. A matching PRE_REG is displayed with inaccurate metadata. | Card created: `correct-verdict-registry-one-run-for-eur` (SONNET). |
| MED | `mal_bb_mid_engulf_2026-10-16/RESULT.md:13-14`; `opr_bb_mtf_center_2026-10-16/RESULT.md:14`; corresponding PRE_REG files | FAIL rows have no explicit kill-scope text in the permitted files. `check` conservatively treats a non-`none` scope as blocking; the actual scope text is unavailable. | `NOT_IN_DATA`; no card required because no source value can be entered faithfully in this audit copy. |
| MED | `gross_effect_screen_2026-10-15/RESULT.md:10,50`; `PRE_REG.md:79-81`; `FABLE_RUNS_AUDIT.md:1.3` | Arm C is FAIL even though the overall study header is INCONCLUSIVE; the row-by-row copy preserves the control arm's result. Its registered stop sentence also names the broader family. | No additional card; scope is reported as written. |

The checked CSV has no `UNPARSED` values in fields the permitted source files can answer. Remaining `NOT_IN_DATA` values are documented above. No `verdicts.py check` command was run because the task explicitly limited this audit to reading the parser and did not authorize running a study or touching the registry.
