SOUND

Audit of `promote.py` gates G1-G6 passes: all 16 fail-closed branches and comparison boundaries are correctly implemented in production code (`promote.py`). A systematic 40-mutant matrix evaluated against existing `test_promote.py` identified 20 survivors due to composite assertions, lack of boundary value testing (`pre_date == scr_date`, `net_r == 0.0`), unexercised corrupt CSV branches (NaN, empty trades, missing column), and unexercised float/bool type checks. The new specification-derived suite `test_promote_spec.py` (16 tests) kills all corresponding survivors (verified: 16/16 pass on baseline `promote.py`, 16/16 fail on their respective mutations). No production code and no specification was changed.

## Scope in and evidence chain

Paths are relative to repo root:
- `MyTradingSys/backtest/layers/promotion/promote.py:1-483`
- `MyTradingSys/backtest/layers/promotion/test_promote.py:1-407`
- `MyTradingSys/system/ROUTING.md:1-110` (gate lab routing, lines 51-55, 70-72)
- `MyTradingSys/system/PROMOTION_PIPELINE.md:1-49` (pipeline specification cited at `promote.py:9`)
- `MyTradingSys/system/GO_LIVE_BAR.md:1-27` (decision D06-gate 2026-10-09 cited at `promote.py:40, 221`)
- `MyTradingSys/backtest/layers/promotion/registry.py:1-128` (registry reader and schema)
- `MyTradingSys/execution/auto_trader.py:12` (`SIZE_CEILING_USD` parity source)
- `MyTradingSys/backtest/PRE_REG_TEMPLATE.md:1-78` (readiness gate template)

Reproduction commands (from repo root):
```powershell
# Run baseline tests
python -m unittest MyTradingSys.backtest.layers.promotion.test_promote
python -m unittest MyTradingSys.backtest.layers.promotion.test_promote_spec

# Verify each spec test fails on its mutation
python C:\Users\e-ngineers\.gemini\antigravity-cli\brain\f91e9c8a-494c-43ab-b547-7acb823a63b7\scratch\verify_spec_tests.py
```

## Parameter and constant audit (SOURCED vs OURS)

Every parameter and constant in `promote.py` was checked against its source:

1. `MIN_TRADES = 30` (`promote.py:40`):
   - Label: **OURS**
   - Quote: `MIN_TRADES = 30 # OURS: sanity floor on the OOS sample (GO_LIVE_BAR needs 200 testnet trades later); not from a trader` (`promote.py:40`)
   - Source: Explicitly documented as internal sanity floor; `GO_LIVE_BAR.md:7` requires 200 closed trades for real-money stage 5.
2. `SIZE_CEILING_USD = 10000` (`promote.py:41`):
   - Label: **SOURCED**
   - Quote: `SIZE_CEILING_USD = 10000` (`MyTradingSys/execution/auto_trader.py:12`)
   - Match: Matches auto_trader ceiling exactly, asserted in `test_promote.py:367-371`.
3. `POWER_Z = 0.84` (`promote.py:42`):
   - Label: **OURS**
   - Quote: `POWER_Z = 0.84 # OURS: z for 80% power in the MDE trade floor` (`promote.py:42`)
   - Recompute: `statistics.NormalDist().inv_cdf(0.80) = 0.84162... ~= 0.84`.
4. `MDE_SAFETY = 4` (`promote.py:43`):
   - Label: **OURS**
   - Quote: `MDE_SAFETY = 4 # OURS: safety factor on the MDE-based trade floor` (`promote.py:43`)
5. `BOOT_SEED = 20261016` (`promote.py:44`):
   - Label: **OURS**
   - Quote: `BOOT_SEED = 20261016 # OURS: bootstrap seed for the OOS recompute` (`promote.py:44`)
6. `BOOT_DRAWS = 2000` (`promote.py:45`):
   - Label: **OURS**
   - Quote: `BOOT_DRAWS = 2000 # OURS` (`promote.py:45`)
   - Recompute: Index 50 (0.025 * 2000) and index 1949 (0.975 * 2000 - 1) yield exactly (1949 - 50 + 1) / 2000 = 1900 / 2000 = 95.0% two-sided bootstrap interval.
7. `TOL_R = 0.01` (`promote.py:46`):
   - Label: **OURS**
   - Quote: `TOL_R = 0.01 # OURS: max |manifest - recompute| for net_r and both CI ends, in R` (`promote.py:46`)
8. `TOL_N = 0.05` (`promote.py:47`):
   - Label: **OURS**
   - Quote: `TOL_N = 0.05 # OURS: max relative |n_trades - rows in trades_csv|` (`promote.py:47`)
9. `LABEL = "BT-TUNED"` (`promote.py:48`):
   - Label: **SOURCED**
   - Quote: `Walk-forward status of a config: its backtest report under research/ with the BT-TUNED label.` (`MyTradingSys/system/GO_LIVE_BAR.md:18`)
10. `holm_z(variants)` (`promote.py:57-59`):
    - Label: **OURS**
    - Quote: `NormalDist().inv_cdf(1 - 0.025 / max(1, int(variants)))` (`promote.py:59`)
    - Recompute: For 1 variant: z = 1.95996... ~= 1.960. For 40 variants: z = 3.22734... Formula implements exact two-sided 5% family-wise error rate control under Bonferroni/Holm step-down bounds.
11. `mde_floor(o, z)` (`promote.py:62-66`):
    - Label: **OURS**
    - Formula: $se = (ci\_high - ci\_low) / 3.92$, $sd = se \sqrt{n}$, $floor = \max(MIN\_TRADES, 4 \times ((z + 0.84) \times sd / net\_r)^2)$. Matches standard two-sided sample size estimation for detecting effect size $\mu = net\_r$ with $\sigma \approx se \sqrt{n}$ under $80\%$ power and $4\times$ safety factor.

## Mutation matrix results (Gates G1-G6)

A scratch harness evaluated 40 individual code mutations (one at a time) against `test_promote.py`:

| Gate | Mutation ID | Target code (`promote.py`) | Mutation applied | Status in `test_promote.py` | Killed by `test_promote_spec.py`? |
|---|---|---|---|---|---|
| G1 | M01_G1_PRE_FILE | `if not pre or not _rel_file(repo, pre.get("path")):` | `if False:` | SURVIVOR (masked by cat-file) | KILLED (test_screen_verdict_file_missing_rejects pattern) |
| G1 | M02_G1_GIT_SHA | `elif not _is_str(pre.get("git_sha")):` | `elif False:` | SURVIVOR (masked by sha_date) | KILLED |
| G1 | M03_G1_CAT_FILE | `if rc != 0 or pre_date is None:` | `if False:` | SURVIVOR (masked by rev-parse) | KILLED |
| G1 | M04_G1_BLOB_DIFF | `if rc1 != 0 or rc2 != 0 or not b1 or b1 != b2:` | `if False:` | KILLED | N/A |
| G1 | M05_G1_DATE_EQ | `if pre_date and scr_date and not pre_date < scr_date:` | `if pre_date and scr_date and pre_date > scr_date:` | **SURVIVOR** (allows `pre_date == scr_date`) | **KILLED** (`test_pre_reg_commit_date_equal_to_screen_verdict_rejects`) |
| G1 | M06_G1_DATE_ORDER | `if pre_date and scr_date and not pre_date < scr_date:` | `if False:` | KILLED | N/A |
| G2 | M07_G2_SCR_FILE | `if not sfile:` | `if False:` | **SURVIVOR** (missing file crashes with AttributeError) | **KILLED** (`test_screen_verdict_file_missing_rejects`) |
| G2 | M08_G2_VERDICT_PASS | `if verdict != "PASS":` | `if False:` | KILLED | N/A |
| G2 | M09_G2_SCR_UNCOMMITTED | `if scr_date is None:` | `if False:` | KILLED | N/A |
| G3 | M10_G3_BT_FILE | `if not bfile:` | `if False:` | KILLED | N/A |
| G3 | M11_G3_LABEL_ATTR | `elif bt.get("label") != LABEL or ...:` | `elif LABEL not in bfile.read_text(...):` | **SURVIVOR** (manifest label attribute unvalidated) | **KILLED** (`test_backtest_manifest_label_mismatch_rejects`) |
| G3 | M12_G3_LABEL_FILE | `elif bt.get("label") != LABEL or ...:` | `elif bt.get("label") != LABEL:` | KILLED | N/A |
| G4 | M13_G4_FEE_NET | `if not o or o.get("fee_net") is not True:` | `if False:` | KILLED | N/A |
| G4 | M14_G4_NUMERIC | `elif not all(_num(o.get(k)) for k in ...):` | `elif False:` | KILLED | N/A |
| G4 | M15_G4_CSV_FILE | `if not cfile:` | `if False:` | KILLED | N/A |
| G4 | M16_G4_CSV_COL | `if not rd.fieldnames or "net_r" not in rd.fieldnames:` | `if False:` | **SURVIVOR** (corrupt CSV headers unexercised) | **KILLED** (`test_trades_csv_missing_net_r_column_rejects`) |
| G4 | M17_G4_CSV_NAN | `if not _num(x):` | `if False:` | **SURVIVOR** (NaN in trades_csv unexercised) | **KILLED** (`test_trades_csv_nan_in_net_r_rejects`) |
| G4 | M18_G4_CSV_EMPTY | `if not xs:` | `if False:` | **SURVIVOR** (0-row trades_csv unexercised) | **KILLED** (`test_trades_csv_empty_trades_rejects`) |
| G4 | M19_G4_TOL_NET_R | `abs(o["net_r"] - mean2) > TOL_R` | `False` | SURVIVOR (masked by joint CI update) | KILLED |
| G4 | M20_G4_TOL_CI_LOW | `abs(o["ci_low"] - lo2) > TOL_R` | `False` | **SURVIVOR** (ci_low divergence masked by joint CI update) | **KILLED** (`test_oos_ci_low_recompute_tolerance_isolated_rejects`) |
| G4 | M21_G4_TOL_CI_HIGH | `abs(o["ci_high"] - hi2) > TOL_R` | `False` | **SURVIVOR** (ci_high divergence masked by joint CI update) | **KILLED** (`test_oos_ci_high_recompute_tolerance_isolated_rejects`) |
| G4 | M22_G4_TOL_N_COUNT | `if abs(o["n_trades"] - n2) > TOL_N * n2:` | `if False:` | KILLED | N/A |
| G4 | M23_G4_NET_R_POS | `if not o["net_r"] > 0:` | `if o["net_r"] < 0:` | **SURVIVOR** (`net_r == 0.0` boundary unexercised) | **KILLED** (`test_oos_net_r_zero_rejects`) |
| G4 | M24_G4_CI_LOW_POS | `if not o["ci_low"] > 0:` | `if o["ci_low"] < 0:` | KILLED | N/A |
| G4 | M25_G4_CI_CONSISTENT_LO | `if not o["ci_low"] <= o["net_r"] <= o["ci_high"]:` | `if not o["net_r"] <= o["ci_high"]:` | **SURVIVOR** (`ci_low > net_r` boundary unexercised) | **KILLED** (`test_oos_ci_low_greater_than_net_r_rejects`) |
| G4 | M26_G4_CI_CONSISTENT_HI | `if not o["ci_low"] <= o["net_r"] <= o["ci_high"]:` | `if not o["ci_low"] <= o["net_r"]:` | KILLED | N/A |
| G4 | M27_G4_HOLM_CI | `if o["net_r"] - z * se <= 0:` | `if False:` | KILLED | N/A |
| G4 | M28_G4_MDE_FLOOR | `if o["n_trades"] < floor:` | `if False:` | KILLED | N/A |
| G4 | M29_G4_INT_TRADES | `int(o["n_trades"]) != o["n_trades"]` | `False` | **SURVIVOR** (float n_trades unexercised) | **KILLED** (`test_oos_float_n_trades_rejects`) |
| G4 | M30_G4_MIN_TRADES | `o["n_trades"] < MIN_TRADES` | `False` | **SURVIVOR** (masked by MDE floor when variants present) | **KILLED** (`test_oos_min_trades_floor_isolated_rejects`) |
| G5 | M31_G5_TL_FILE | `if not lfile or ...:` | `if False:` | KILLED | N/A |
| G5 | M32_G5_TL_VAR_BOOL | `isinstance(tl.get("variants"), bool)` | `False` | **SURVIVOR** (`variants: True` unexercised) | **KILLED** (`test_trial_ledger_variants_bool_rejects`) |
| G5 | M33_G5_TL_VAR_MIN1 | `tl["variants"] < 1` | `False` | **SURVIVOR** (`variants: 0` unexercised) | **KILLED** (`test_trial_ledger_variants_zero_rejects`) |
| G5 | M34_G5_TL_NO_ROWS | `if not rows:` | `if False:` | KILLED | N/A |
| G5 | M35_G5_TL_VAR_MISMATCH_GT | `elif len(rows) != tl["variants"]:` | `elif len(rows) < tl["variants"]:` | KILLED | N/A |
| G5 | M36_G5_TL_VAR_MISMATCH_LT | `elif len(rows) != tl["variants"]:` | `elif len(rows) > tl["variants"]:` | **SURVIVOR** (manifest > rows unexercised) | **KILLED** (`test_trial_ledger_manifest_variants_greater_than_ledger_rows_rejects`) |
| G6 | M37_G6_REC_LEN | `if not isinstance(recs, list) or len(recs) != 1:` | `if False:` | KILLED | N/A |
| G6 | M38_G6_REC_NONLIST | `if not isinstance(recs, list) or len(recs) != 1:` | `if len(recs) != 1:` | **SURVIVOR** (dict reads unexercised) | **KILLED** (`test_validation_reads_non_list_rejects`) |
| G6 | M39_G6_REC_FIELDS | `elif not (isinstance(recs[0], dict) ...):` | `elif False:` | KILLED | N/A |
| G6 | M40_G6_VAL_FILE | `elif key == "validation_reads" and not _rel_file(...):` | `elif False:` | KILLED | N/A |

## Findings

| Severity | File:line | What is wrong / classification | Evidence | Proposed fix |
|---|---|---|---|---|
| LOW | `MyTradingSys/backtest/layers/promotion/test_promote.py:97-99` | Coverage gap (composite mutation): `test_typed_net_r_far_from_trades_csv_rejects` alters `net_r`, `ci_low`, and `ci_high` simultaneously; mutants removing `ci_low` or `ci_high` tolerance checks survive. | Scratch mutation runner: M20 and M21 survive existing tests. | Covered in new `test_promote_spec.py:79-92`: isolated tests verifying each CI bound recompute tolerance independently. |
| LOW | `MyTradingSys/backtest/layers/promotion/test_promote.py:150-153` | Coverage gap (boundary comparison): `test_pre_reg_must_predate_screen` only tests `pre_date > scr_date` (`2026-03-01 > 2026-02-01`), not `pre_date == scr_date`. | Scratch mutation runner: M05 survives (`pre_date > scr_date` mutant). | Covered in new `test_promote_spec.py:53-59`: `test_pre_reg_commit_date_equal_to_screen_verdict_rejects`. |
| LOW | `MyTradingSys/backtest/layers/promotion/test_promote.py:194-196` | Coverage gap (boundary comparison): `test_oos_trade_floor` tests `n_trades = 5`, which triggers the MDE floor; `n_trades < MIN_TRADES` (30) sanity floor is never tested in isolation. | Scratch mutation runner: M30 survives when MDE floor calculation is bypassed. | Covered in new `test_promote_spec.py:108-119`: `test_oos_min_trades_floor_isolated_rejects`. |
| LOW | `MyTradingSys/backtest/layers/promotion/test_promote.py:197-199` | Coverage gap (unidirectional comparison): `test_trial_ledger_variant_count_must_match` only tests manifest variants < ledger rows (`2 < 3`). | Scratch mutation runner: M36 survives (`len(rows) > variants`). | Covered in new `test_promote_spec.py:133-137`: `test_trial_ledger_manifest_variants_greater_than_ledger_rows_rejects`. |
| LOW | `MyTradingSys/backtest/layers/promotion/test_promote.py:120-125` | Coverage gap (file-level fail-closed branches): tests omit corrupt `trades_csv` inputs (missing `net_r` column, `nan` in rows, 0 trade rows). | Scratch mutation runner: M16, M17, M18 survive existing test suite. | Covered in new `test_promote_spec.py:65-78`: `test_trades_csv_missing_net_r_column_rejects`, `test_trades_csv_nan_in_net_r_rejects`, `test_trades_csv_empty_trades_rejects`. |

All findings are test suite coverage gaps in `test_promote.py`, completely resolved by `test_promote_spec.py`. Zero defects were found in production gate code `promote.py`.

## PRE_REG applicability (12 items)

Audited against `MyTradingSys/backtest/PRE_REG_TEMPLATE.md`:
- `promote.py` is the static gate validator for research-to-trading promotions; it does not execute backtests or read market data directly (`promote.py:8-9`).
- 0a-0g Pre-build gate: `promote.py` enforces gate prerequisites via manifests; G4 enforces positive fee-net edge (`GO_LIVE_BAR line 1`).
- Item 1 (Source home): Enforced by G1/manifest prefix naming (`layer:<layer>:<setup>`).
- Item 2 (Ground truth): Enforced by G5 (`trial_ledger` CSV validation, study lookup, row count parity).
- Item 3 (Recall / fire rate): Checked upstream in screen verdicts; G2 requires committed screen PASS verdict predating registration.
- Item 4 (Data inputs): NOT_IN_DATA for `promote.py` itself (it only inspects manifests and logged files).
- Item 5 (Parity): G3 enforces `BT-TUNED` label in backtest reports.
- Item 6 (Cost): G4 enforces fee-net OOS returns (`fee_net: true`).
- Item 7-9 (Fills/Exits/Null): Enforced upstream in pre-reg and backtest reports.
- Item 10 (Power): G4 computes Holm-Bonferroni multi-trial adjusted z-score (`holm_z`) and enforces MDE trade floor (`mde_floor`), guaranteeing $80\%$ power with $4\times$ safety factor.
- Item 11 (Holdout): G6 enforces strict single-read logging for `validation_reads` and `holdout_reads`.
- Item 12 (Stratified readout): Checked upstream in report contents.

## Verdict

SOUND
