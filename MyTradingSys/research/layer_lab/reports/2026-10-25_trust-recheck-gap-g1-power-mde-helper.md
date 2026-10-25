# Trust re-check: gap-g1-power-mde-helper

Verdict: BLOCKED — arithmetic matches the written spec and the fail-first mutation turns the tests red, but this COD/GPT reviewer is the same vendor as the producer and cannot propose VERIFIED-C2 under the cross-vendor re-check rule. Proposal: DISPUTED pending a Gemini or Claude re-check.

## Reviewer

- Vendor/model: OpenAI / GPT-6 (Codex, surface COD).
- Independent arithmetic was derived from the written definition in `MyTradingSys/research/backtest_gap_review_2026-10-13/REPORT.md:90-99,211-213`; producer implementation was not used to derive expected values.
- The requested prior report `MyTradingSys/research/layer_lab/reports/2026-10-23_trust-recheck-gap-g1-power-mde-helper.md` was absent from this work tree. The card scope and cited written spec were used as the audit target.

## Re-derived numbers

| Written-spec number | Independent calculation | Result |
|---|---:|---|
| 80%-power N, p=.45, RR=1.5, cost=.012; REPORT.md:94,211-213 | mean = .45*1.5-.55-.012 = .113; SD = 1.243792; `((1.96+.8416)*SD/mean)^2` = 950.935407 → 951 | MATCH |
| 80%-power N, p=.45, RR=2.5, cost=.062; REPORT.md:99,211-213 | mean = .45*2.5-.55-.062 = .513; SD = 1.742331; same formula = 90.539709 → about 90 | MATCH (rounds to 91 under conventional nearest-integer rounding; table reports approximate 90) |

The report formula says one-sided power `1-Phi(1.96-mean/(SD/sqrt(n)))`. Independent power at N=100 is 14.651724% for the first row and 83.752352% for the second, matching the table’s rounded 15% and 84% (REPORT.md:94,99,211).

## Tests and fail-first mutation

- Audited tests: `MyTradingSys/tests/test_power_mde.py:1-34`. They assert the table means, power at N=100/150/300 and the two anchor N estimates.
- Baseline command: `python -m pytest MyTradingSys/tests/test_power_mde.py -q` — 7 passed, 1 cache warning.
- Mutation: copied the test and implementation to `C:\Users\E-NGIN~1\AppData\Local\Temp\mde_mutation_5sl28jg3`; changed only the copied power assignment to `power = 0.0`. Ran pytest against the copied test with the scratch directory on `PYTHONPATH` — exit 1, 7 failed. The table power assertions and anchor power assertions detect the defect. Real audited files were left unchanged.

## Findings

| Severity | Location | Finding | Evidence | Proposed disposition |
|---|---|---|---|---|
| HIGH | `MyTradingSys/research/backtest_gap_review_2026-10-13/REPORT.md:94,99,211-213` | The two requested 80%-power values reproduce from the written formula. | Independent values 950.935407 and 90.539709. MATCH. | Retain the calculations; consider reporting the latter as 91 if conventional rounding is intended. |
| HIGH | `MyTradingSys/tests/test_power_mde.py:17-34` | The test suite fails on a broken power calculation. | Scratch mutation `power=0.0`: 7 failures. | Test sensitivity demonstrated. |
| HIGH | `MyTradingSys/research/layer_lab/reports/2026-10-23_trust-recheck-gap-g1-power-mde-helper.md` | Prior requested report is absent in this work tree. | Read attempt returned file-not-found. | Cross-vendor reviewer must complete the dated re-check before VERIFIED-C2. |
| HIGH | This review | Cross-vendor requirement cannot be satisfied by this COD/GPT reviewer of GPT-produced work. | Layer-lab protocol requires a different vendor for a trust re-check. | Proposal DISPUTED; obtain Gemini or Claude review. |

No market data or producer code was used. No source or test file was edited. No follow-up card was created.
