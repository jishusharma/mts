# GPT verdict registry audit B — rows 11–20

Verdict: **FIX-FIRST**

## What was checked

Read `scripts/dev/verdicts.py` docstring and parser/check implementation (lines 1–19, 76–137, 210–228), `MyTradingSys/research/VERDICTS.csv`, then the study files listed per row below. Also read `MyTradingSys/research/volume_2026-10-09/PRE_REG_VOLUME_2026-10-09.md` section 1 (line 23) for the project split boundaries. No study was run, no market data or study code was examined, and no registry file was edited.

The checked copy is [VERDICTS_CHECKED_b.csv](../gpt-verdict-registry-audit/VERDICTS_CHECKED_b.csv). It contains all 23 existing registry rows, adds a `source` column, and updates rows 11–20. `NOT_IN_DATA` means the permitted study text does not provide a corresponding scalar/statement. Row/field citations in `source` refer to the original study files.

| Row | Files read | Checked values (split; n; gross mean; SE; verdict; one_run; kill_scope) | Existing parsed fields | Finding |
|---:|---|---|---|---|
| 11 | `opr_preopen_tops_2026-10-16/RESULT.md:5,7,11-14`; `PRE_REG.md:37-45` | DEV; 104; 0.0373; 0.0814; INCONCLUSIVE; yes; none | n, mean, SE, verdict, one_run, split, kill_scope: MATCH | RESULT explicitly calls the study DEV-only. Arm H2 row statistics and inconclusive verdict match. PRE_REG records the one-run frozen screen. |
| 12 | `opr_weekly_low_round_sweep_2026-10-16/RESULT.md:1-14`; `PRE_REG.md:12-15,38-46` | DEV; 685; 0.0317; 0.0335; FAIL; yes; NOT_IN_DATA | split, n, mean, SE, verdict, one_run: MATCH; kill_scope: MISMATCH (UNPARSED) | The source has no explicit `FAIL means stop` sentence. `verdicts.py check` currently treats UNPARSED as family-wide; follow-up is needed to determine the documented scope before encoding it. |
| 13 | Same RESULT/PRE_REG as row 12 | DEV; 525; -0.0389; 0.0462; FAIL; yes; NOT_IN_DATA | split, n, mean, SE, verdict, one_run: MATCH; kill_scope: MISMATCH (UNPARSED) | Same missing explicit stop-scope sentence and check consequence as row 12. |
| 14 | `orderflow_views_2026-10-14/RESULT.md:6,35-45,51-55` | DEV+VALIDATION+HOLDOUT; cost 0.10; NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA; FAIL; no; NOT_IN_DATA | split: MISMATCH (UNPARSED); cost 0.10: MISMATCH (UNPARSED); n/mean/SE: NOT_IN_DATA (no single study-level value); verdict FAIL: MATCH; one_run no: MATCH; kill_scope: MISMATCH (UNPARSED) | Report has split-wise DIV−CONTROL contrasts for all three periods, but not one aggregate n/mean/SE. `NEGATIVE` maps to FAIL. No PRE_REG exists, so parser returns `no` for one_run. No stop-scope sentence is present. This is the only row that reports numerical VALIDATION and HOLDOUT results explicitly. |
| 15 | `published_strats_2026-10-13/RESULTS.md:4-10,12-22`; `PRE_REG.md:8-11,37-43` | DEV; NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA; FAIL; NOT_IN_DATA; NOT_IN_DATA | split: MATCH; n/mean/SE: NOT_IN_DATA (62 variants, no one study-level value); verdict FAIL: MATCH; one_run/kill_scope: NOT_IN_DATA (UNPARSED) | Result says nothing survived on DEV and explicitly says VAL and HOLD were never opened. No numerical validation/holdout results. |
| 16 | `rsi_divergence_mtf_2026-10-09/RESULT.md:3-20`; `REPORT.md:3-5,37,49` | DEV+VALIDATION+HOLDOUT; cost 0.10; NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA; FAIL; no; NOT_IN_DATA | split, verdict, one_run: MATCH; n/mean/SE: NOT_IN_DATA (many timeframe/side cells); kill_scope: NOT_IN_DATA (UNPARSED) | File covers data through 2026-10-07 and summarizes many cells; it does not report one aggregate value for these fields. The result says no edge for cells meeting its n bar; remaining cells are insufficient-n. |
| 17 | `t087_session_levels_2026-10-09/RESULT.md:1-5,7-24,39-43` | DEV+VALIDATION+HOLDOUT; cost 0.10; NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA; FAIL; no; NOT_IN_DATA | split: MISMATCH (UNPARSED); verdict: NOT_IN_DATA (no aggregate verdict); n/mean/SE/one_run/kill_scope: NOT_IN_DATA | Report spans 2022-01-01 through 2026-10-07 and gives many event cells, including by-year numbers, not a single registry scalar. Cells with n≥300 are called no-edge; the remaining cells insufficient-n. The study text does not provide one aggregate verdict, so the verdict is NOT_IN_DATA. |
| 18 | `t090_7h_2026-10-09/RESULT.md:12-36` | DEV+VALIDATION+HOLDOUT; cost 0.10; NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA; INCONCLUSIVE; no; none | split: MISMATCH (UNPARSED); verdict: NOT_IN_DATA (no aggregate verdict); n/mean/SE/one_run/kill_scope: NOT_IN_DATA | It reports 18 anchor cells with n 35–55 over 2022–2026, says no verdict either way, and describes the lead as not robust. It does not give an aggregate verdict; verdict is NOT_IN_DATA. No failure stop sentence. |
| 19 | `transcript_inventory_2026-10-09/RESULT.md:1-33` | NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA; NOT_IN_DATA; no; NOT_IN_DATA | split/n/mean/SE/verdict/kill_scope: NOT_IN_DATA; one_run no: MATCH | Inventory reports extraction counts and gate status, not trading outcomes or split reads. Parser returns `no` because no PRE_REG exists. |
| 20 | `wlow_bounce_bbrsi60_2026-10-16/RESULT.md:1-14,61-64`; `PRE_REG.md:12-18,38-45` | DEV; 8; -0.293; 0.116; INCONCLUSIVE; yes; none | split, n, mean, SE, verdict, one_run: MATCH; kill_scope: MISMATCH (UNPARSED) | INCONCLUSIVE has no stop scope; explicit PRE_REG sentence says a FAIL (if any) only kills composite C as defined, not other factors/setups. Since this row is not FAIL, `none` is correct for the registry parser. |

## Check behavior and follow-up

- Rows 12 and 13 carry FAIL, so `verdicts.py check` blocks a matching new PRE_REG today. Their kill scope remains NOT_IN_DATA in the checked copy because the source lacks the explicit stop sentence; follow-up will resolve this.
- Row 14 also has FAIL and an unavailable explicit kill sentence. `UNPARSED` in the original means the checker applies a family-wide stop. The source has no stop rule to support that scope; create a follow-up card to review the missing scope. This will not make it safe to rerun until resolved.
- Row 20 is INCONCLUSIVE, so its kill scope does not block a new PRE_REG. `one_run=yes` is sufficient for the checker to block rerunning that PRE_REG family.
- Rows 11, 12, 13, and 20 all report DEV-only in their study-specific texts. Row 14 reports DEV, VALIDATION, and HOLDOUT contrasts; row 15 explicitly says VAL and HOLD were not opened. No other row gives explicitly named validation or holdout result numbers.

## Follow-up cards

- `determine-explicit-failure-scope-for-weekly-low` — rows 12–13 have FAIL, but PRE_REG only says study word is FAIL if both arms fail; no explicit stop sentence.
- `resolve-missing-orderflow-divergence-kil` — row 14 has FAIL and no explicit stop sentence.
- `backfill-t087-session-level-split-and-ve` — row 17 has UNPARSED split; the overall verdict is NOT_IN_DATA because the result provides only per-cell conclusions.
- `backfill-t090-7h-split-and-inconclusive-` — row 18 has UNPARSED split and verdict; the report says no verdict either way.

No MISMATCH was found in study-answerable fields already parsed in the input registry. The audit is FIX-FIRST because rows 12–14 and 17–18 have missing or overbroad registry values that affect what the gate reports/blocks.
