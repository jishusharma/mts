# Layer Lab Report: Cross-Vendor Audit of CBP Scorecard Spec Tests and Mutations

- **Task**: `gemini-rerun-cbp-scorecard-spec-tests-1103` (`OURS`)
- **Auditor**: Gemini 3.8 Flash (medium) worker (Antigravity JIS-NUC) (`OURS`)
- **Date**: 2026-11-03 (`OURS`)
- **Audited Target**: `MyTradingSys/research/layer_lab/reports/2026-11-02_gpt-spec-tests-cbp-scorecard.md` (Commit `6267cc8d21b2`) (`SOURCED`: commit `6267cc8d21b2`)
- **Audit Table Output**: `MyTradingSys/research/gemini_audits_2026-11-03/cbp_scorecard_rerun.md` (`OURS`)
- **Sources**: `MyTradingSys/research/layer_lab/reports/2026-11-01_gpt-mutation-research-kit.md:1-20` (`SOURCED`: `MyTradingSys/research/layer_lab/reports/2026-11-01_gpt-mutation-research-kit.md:1-20`)

---

## 1. Summary of Findings

1. **Unmutated Test Suite**:
   - Command: `python -m pytest scripts/dev/test_cbp_scorecard.py -v` (`OURS`)
   - Result: 13 passed, 0 failed in 0.15s (`OURS`).
   - Verifies GPT report line 20: `"python -m pytest scripts/dev/test_cbp_scorecard.py -q --basetemp=F:/MTS/_pt_codex_cbp_scorecard_eco -> 13 passed"` (`SOURCED`: `MyTradingSys/research/layer_lab/reports/2026-11-02_gpt-spec-tests-cbp-scorecard.md:20`).
   - Status: **FOUND**.

2. **Mutation 1 (Folded Analyst Names)**:
   - Target: `scripts/dev/cbp_scorecard.py:23` (`OURS`)
   - Change: `r.get("analyst", "UNKNOWN")` -> `str(r.get("analyst", "UNKNOWN")).lower()` (`OURS`)
   - Result: 11 failed, 2 passed; suite failed with returncode 1 (`OURS`).
   - Killing Test: `test_michael_and_michaal_are_distinct` (`scripts/dev/test_cbp_scorecard.py:22-27`) fails because casing difference is folded (`OURS`).
   - Verifies GPT report line 21: `"folded analyst names ... caused the suite to fail"` (`SOURCED`: `MyTradingSys/research/layer_lab/reports/2026-11-02_gpt-spec-tests-cbp-scorecard.md:21`).
   - Status: **FOUND**.

3. **Mutation 2 (Counting Qualifying Trades Not Rows)**:
   - Target: `scripts/dev/cbp_scorecard.py:26` (`OURS`)
   - Change: `1 if cbp.is_tradable(r) else 0` -> `sum(1 for t in r.get("trades") or [] if cbp.is_tradable({"trades": [t]}))` (`OURS`)
   - Result: 1 failed, 12 passed; suite failed with returncode 1 (`OURS`).
   - Killing Test: `test_row_with_multiple_trades_counts_as_one_tradable_row` (`scripts/dev/test_cbp_scorecard.py:65-68`) fails with `assert {'rows': 1, 'trades': 2, 'tradable_rows': 2} == {'rows': 1, 'trades': 2, 'tradable_rows': 1}` (`OURS`).
   - Verifies GPT report line 21: `"counted qualifying trades instead of qualifying rows ... caused the suite to fail"` (`SOURCED`: `MyTradingSys/research/layer_lab/reports/2026-11-02_gpt-spec-tests-cbp-scorecard.md:21`).
   - Status: **FOUND**.

4. **Mutation 3 (Accepting SIDEWAYS as Direction)**:
   - Target: `MyTradingSys/cbp/__init__.py:104` (`OURS`)
   - Change: `t.get("direction") in DIRECTIONS and` -> `t.get("direction") in DIRECTIONS + ("SIDEWAYS",) and` (`OURS`)
   - Result: 1 failed, 12 passed; suite failed with returncode 1 (`OURS`).
   - Killing Test: `test_invalid_direction_is_not_tradable` (`scripts/dev/test_cbp_scorecard.py:53-56`) fails with AssertionError because `SIDEWAYS` was accepted as tradable (`OURS`).
   - Verifies GPT report line 21: `"and accepted SIDEWAYS as a direction"` (`SOURCED`: `MyTradingSys/research/layer_lab/reports/2026-11-02_gpt-spec-tests-cbp-scorecard.md:21`).
   - Status: **FOUND**.

---

## 2. Line 1 Header Compliance

First line of `MyTradingSys/research/gemini_audits_2026-11-03/cbp_scorecard_rerun.md` is strictly:
`# PASS: 13 | FOUND: 4 | DIFF: 0 | NOT_IN_DATA: 0`
giving the unmutated pass count (13) and all three classification counts (FOUND: 4, DIFF: 0, NOT_IN_DATA: 0).
