# PASS: 13 | FOUND: 4 | DIFF: 0 | NOT_IN_DATA: 0

# Cross-Vendor Audit & Mutation Re-run: CBP Scorecard Spec Tests

- **Card**: `gemini-rerun-cbp-scorecard-spec-tests-1103` (`OURS`)
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC) (`OURS`)
- **Date (UTC)**: 2026-11-03 (`OURS`)
- **Audited Target**:
  - Report: `MyTradingSys/research/layer_lab/reports/2026-11-02_gpt-spec-tests-cbp-scorecard.md` (Commit `6267cc8d21b2`, 2026-11-02) (`SOURCED`: commit `6267cc8d21b2`)
  - Target implementation: `scripts/dev/cbp_scorecard.py` (42 lines) (`OURS`)
  - Spec tests: `scripts/dev/test_cbp_scorecard.py` (73 lines, 13 test functions) (`OURS`)
  - Tradability definition: `MyTradingSys/cbp/__init__.py:101-108` (`SOURCED`: `MyTradingSys/cbp/__init__.py:101-108`)
- **Sources**: `MyTradingSys/research/layer_lab/reports/2026-11-01_gpt-mutation-research-kit.md:1-20` (`SOURCED`: `MyTradingSys/research/layer_lab/reports/2026-11-01_gpt-mutation-research-kit.md:1-20`)
- **Counts on Line 1**: `PASS: 13 | FOUND: 4 | DIFF: 0 | NOT_IN_DATA: 0` (`OURS`)

---

## 1. Summary of Verification

1. **Unmutated Spec Suite**:
   - `scripts/dev/test_cbp_scorecard.py` executed cleanly with 13 passed tests out of 13 (`OURS`).
   - Confirms GPT claim: `python -m pytest scripts/dev/test_cbp_scorecard.py -q --basetemp=F:/MTS/_pt_codex_cbp_scorecard_eco -> 13 passed` (`SOURCED`: `MyTradingSys/research/layer_lab/reports/2026-11-02_gpt-spec-tests-cbp-scorecard.md:20`, quote: `"13 passed"`).
   - Status: **FOUND**.

2. **Mutation 1 (Folded analyst names)**:
   - In scratch copy outside repository, mutated `scripts/dev/cbp_scorecard.py:23` from `r.get("analyst", "UNKNOWN")` to `str(r.get("analyst", "UNKNOWN")).lower()`.
   - Running `pytest scripts/dev/test_cbp_scorecard.py -v` failed with returncode 1 (11 failed, 2 passed) (`OURS`).
   - Primary killing test: `test_michael_and_michaal_are_distinct` (`scripts/dev/test_cbp_scorecard.py:22-27`), asserting distinct case-preserved analyst keys (`OURS`).
   - Confirms GPT claim: `folded analyst names ... caused the suite to fail` (`SOURCED`: `MyTradingSys/research/layer_lab/reports/2026-11-02_gpt-spec-tests-cbp-scorecard.md:21`).
   - Status: **FOUND**.

3. **Mutation 2 (Counting qualifying trades not rows)**:
   - In scratch copy outside repository, mutated `scripts/dev/cbp_scorecard.py:26` from `1 if cbp.is_tradable(r) else 0` to `sum(1 for t in r.get("trades") or [] if cbp.is_tradable({"trades": [t]}))`.
   - Running `pytest scripts/dev/test_cbp_scorecard.py -v` failed with returncode 1 (1 failed, 12 passed) (`OURS`).
   - Killing test: `test_row_with_multiple_trades_counts_as_one_tradable_row` (`scripts/dev/test_cbp_scorecard.py:65-68`), which verifies that a row with multiple qualifying trades increments `tradable_rows` by exactly 1, not 2 (`OURS`).
   - Confirms GPT claim: `counted qualifying trades instead of qualifying rows ... caused the suite to fail` (`SOURCED`: `MyTradingSys/research/layer_lab/reports/2026-11-02_gpt-spec-tests-cbp-scorecard.md:21`).
   - Status: **FOUND**.

4. **Mutation 3 (Accepting SIDEWAYS as a direction)**:
   - In scratch copy outside repository, mutated `MyTradingSys/cbp/__init__.py:104` from `t.get("direction") in DIRECTIONS and` to `t.get("direction") in DIRECTIONS + ("SIDEWAYS",) and`.
   - Running `pytest scripts/dev/test_cbp_scorecard.py -v` failed with returncode 1 (1 failed, 12 passed) (`OURS`).
   - Killing test: `test_invalid_direction_is_not_tradable` (`scripts/dev/test_cbp_scorecard.py:53-56`), asserting that `SIDEWAYS` trade direction yields 0 tradable rows (`OURS`).
   - Confirms GPT claim: `and accepted SIDEWAYS as a direction. All mutations were reverted in the scratch copy` (`SOURCED`: `MyTradingSys/research/layer_lab/reports/2026-11-02_gpt-spec-tests-cbp-scorecard.md:21`).
   - Status: **FOUND**.

---

## 2. Four-Row Verification Table

| # | Item / Target | GPT Claim (`SOURCED`) | Gemini Rerun Result (`OURS`) | Killing Test / Output | Status | Notes |
|---|---|---|---|---|---|---|
| 1 | Unmutated baseline test run | `13 passed` (`SOURCED`: `2026-11-02_gpt-spec-tests-cbp-scorecard.md:20`, quote: `"13 passed"`) | `13 passed in 0.15s` (`OURS`: command `python -m pytest scripts/dev/test_cbp_scorecard.py -v`) | None: all 13 passed (`test_missing_rows_key_is_empty`, `test_empty_rows_is_empty`, `test_unknown_analyst_is_counted`, `test_michael_and_michaal_are_distinct`, `test_none_trades_contributes_zero`, `test_empty_trades_contributes_zero`, `test_trade_count_includes_each_trade_independent_of_tradability`, `test_complete_long_trade_is_tradable`, `test_complete_short_trade_is_tradable`, `test_invalid_direction_is_not_tradable`, `test_blank_or_em_dash_levels_are_not_tradable`, `test_row_with_multiple_trades_counts_as_one_tradable_row`, `test_counts_accumulate_by_exact_analyst_key`) (`OURS`) | FOUND | Identical pass count of 13 confirmed. |
| 2 | Mutation 1: Folded analyst names | Suite fails (`SOURCED`: `2026-11-02_gpt-spec-tests-cbp-scorecard.md:21`, quote: `"folded analyst names"`) | `11 failed, 2 passed` (exit code 1) (`OURS`: mutated `scripts/dev/cbp_scorecard.py:23` to lowercased analyst) | `scripts/dev/test_cbp_scorecard.py::test_michael_and_michaal_are_distinct` (AssertionError: `assert {'michael': {'rows': 1, 'trades': 0, 'tradable_rows': 0}} == {'Michael': ...}`); also fails `test_unknown_analyst_is_counted` (`assert {'unknown': ...} == {'UNKNOWN': ...}`) and 9 other tests (`OURS`) | FOUND | Mutant killed. Suite fails as reported by GPT. |
| 3 | Mutation 2: Counting qualifying trades not rows | Suite fails (`SOURCED`: `2026-11-02_gpt-spec-tests-cbp-scorecard.md:21`, quote: `"counted qualifying trades instead of qualifying rows"`) | `1 failed, 12 passed` (exit code 1) (`OURS`: mutated `scripts/dev/cbp_scorecard.py:26` to sum qualifying trades) | `scripts/dev/test_cbp_scorecard.py::test_row_with_multiple_trades_counts_as_one_tradable_row` (AssertionError: `assert {'rows': 1, 'trades': 2, 'tradable_rows': 2} == {'rows': 1, 'trades': 2, 'tradable_rows': 1}`) (`OURS`) | FOUND | Mutant killed. Suite fails as reported by GPT. |
| 4 | Mutation 3: Accepting SIDEWAYS as a direction | Suite fails (`SOURCED`: `2026-11-02_gpt-spec-tests-cbp-scorecard.md:21`, quote: `"accepted SIDEWAYS as a direction"`) | `1 failed, 12 passed` (exit code 1) (`OURS`: mutated `MyTradingSys/cbp/__init__.py:104` to include `"SIDEWAYS"`) | `scripts/dev/test_cbp_scorecard.py::test_invalid_direction_is_not_tradable` (AssertionError: `assert cbp_scorecard.recount(...)['A']['tradable_rows'] == 0`, actual returned 1) (`OURS`) | FOUND | Mutant killed. Suite fails as reported by GPT. |

---

## 3. Repository State Integrity

- All mutants were executed exclusively in a scratch directory outside the repository (`F:/MTS/_gemini_cbp_scratch`) and subsequently removed (`OURS`).
- `scripts/dev/cbp_scorecard.py`, `scripts/dev/test_cbp_scorecard.py`, and `MyTradingSys/cbp/__init__.py` remain completely untouched (`git diff` clean) (`OURS`).
