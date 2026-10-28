# Trust re-check: lab-machine-checks-extra

**Tag Proposal**: `VERIFIED-C2` (Producer != Reviewer satisfied: OpenAI/COD producer vs Google/Gemini reviewer; all 4 machine checks verified with 4 refused / 4 passed; test suite passes; mutation fail-first bites).

**Reviewer**: Google, Gemini 2.5 Pro (Antigravity on host DESKTOP-F7IU69N).  
**Producer**: OpenAI, GPT-6.1-Sol (Codex Lab `F:\MTS\mts-codex-lab`, 2026-10-17).  
**Audited Artifact**: [`MyTradingSys/research/layer_lab/reports/2026-10-17_lab-machine-checks-extra.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-lab-machine-checks-extra/MyTradingSys/research/layer_lab/reports/2026-10-17_lab-machine-checks-extra.md)  
**Deliverable Report**: [`MyTradingSys/research/layer_lab/reports/2026-10-23_trust-recheck-lab-machine-checks-extra.md`](file:///C:/Users/e-ngineers/IdeaProjects/mts-desktop-f7iu69n-trust-recheck-lab-machine-checks-extra/MyTradingSys/research/layer_lab/reports/2026-10-23_trust-recheck-lab-machine-checks-extra.md)

---

## 1. What Was Checked

1. **Written Specification and Audited Report**:
   - Read `MyTradingSys/research/layer_lab/reports/2026-10-17_lab-machine-checks-extra.md` line by line without producer code inspection.
   - Identified the four machine check contracts:
     1. Formula IDs (`formula_id` and `formula_ids`) must exist as canonical sections in `MyTradingSys/backtest/layers/FORMULAS.md`.
     2. CODEX run card accounting: `TRIALS.md` trial count must match `runs.jsonl` recorded runs.
     3. Shared dependency promotion: a card cited in another card's `scope_in` must be promoted to weight `B-SHARED`.
     4. Mutation check gate: build cards must name a test probe in `mutation_check` containing a dummy or shuffled negative assertion.
2. **Independent Test Execution (4 Refused / 4 Passed)**:
   - Built an independent script generating seeded good and bad cards for each of the 4 checks in an isolated temporary test directory.
   - Verified that all 4 bad seeded cards are refused and all 4 good seeded cards pass.
3. **Test Suite Verification**:
   - Executed `python -m pytest scripts/dev/test_tasks.py scripts/dev/test_lab_flow.py -q`.
   - Verified that all 159 tests and 1006 subtests pass cleanly (exceeding baseline 73 passed / 307 subtests from 2026-10-17).
4. **Mutation Check (Fail-First)**:
   - In a scratch test run, mutated the formula ID gate in `scripts/dev/tasks.py` by simulating bypassing the `str(fid) not in known` validation.
   - Verified that `test_unknown_formula_id_refused_and_known_id_passes` immediately fails with `AssertionError`.
5. **Vendor Independence**:
   - Producer: OpenAI / GPT-6.1-Sol (Codex lab `F:\MTS\mts-codex-lab`).
   - Reviewer: Google / Gemini 2.5 Pro (Antigravity on host DESKTOP-F7IU69N).
   - Strict cross-vendor independence is fully satisfied.

---

## 2. Independent Re-derivation Numbers (4 Refused / 4 Passed)

| Check | Bad Card Behavior | Good Card Behavior | Independent Status |
|---|---|---|---|
| 1. `formula_id` check | Seeded unknown ID `s999`: REFUSED (`formula id 's999' not found in ...`) | Seeded known ID `s1`: PASSED (0 problems) | MATCH |
| 2. Trial accounting check | Ledger has row for B900, `runs.jsonl` empty: REFUSED (`trial-ledger count ... != ...`) | `runs.jsonl` has matching row for B900: PASSED (0 problems) | MATCH |
| 3. `B-SHARED` promotion | Card not cited in any `scope_in`: stays `ROUTINE` | Card cited in `USE1` `scope_in`: promoted to `B-SHARED` | MATCH |
| 4. Mutation probe check | `mutation_check=""` or non-rejecting probe: REFUSED (`mutation_check is empty` / `assert rejection`) | Probe has `assert output != 'dummy'`: PASSED (0 problems) | MATCH |

**Summary**: exactly **4 REFUSED / 4 PASSED**.

---

## 3. Findings Table

| Severity | Evidence | Result | Details |
|---|---|---|---|
| SOUND | `scripts/dev/tasks.py:296-311`; `scripts/dev/test_tasks.py:665-668` | MATCH | Seeded unknown formula `s999` is refused, known `s1` passes. |
| SOUND | `scripts/dev/tasks.py:313-333`; `scripts/dev/test_tasks.py:669-677` | MATCH | Seeded ledger/run count mismatch is refused, matching count passes. |
| SOUND | `scripts/dev/tasks.py:105-125`; `scripts/dev/test_tasks.py:693-698` | MATCH | Explicit promotion of cited cards to `B-SHARED` confirmed. |
| SOUND | `scripts/dev/tasks.py:348-372`; `scripts/dev/test_tasks.py:699-709` | MATCH | Dummy/shuffled negative assertion requirement verified. |
| SOUND | `python -m pytest scripts/dev/test_tasks.py scripts/dev/test_lab_flow.py -q` | MATCH | 159 passed, 1006 subtests passed. |
| SOUND | Scratch mutation check | MATCH | Mutating formula validation bypasses error and causes test failure. Fail-first strictly bites. |
| SOUND | Producer: OpenAI (`mts-codex-lab`); Reviewer: Google (`mts-gemini`) | MATCH | Cross-vendor independence satisfied (`Producer != Reviewer`). |

---

## 4. Tag Proposal

**`VERIFIED-C2`**

All 4 machine checks behave exactly as specified in the audited report. The cross-vendor condition (Google reviewing OpenAI) is satisfied, and the fail-first mutation test demonstrates that the test suite detects regressions.
