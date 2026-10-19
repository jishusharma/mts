# Result trust tags and dependent-card gate

**DONE: explicit result citations are gated by evidence-bound trust receipts.** No historical result was marked verified. Reviewer authority remains the separate open R1 stamp-writer problem; these checks enforce receipt/content consistency, not scientific truth or authenticated reviewer identity.

## Implementation

| File / line | Behavior |
|---|---|
| `scripts/dev/tasks.py:194,883` | Ready checks and shared start/close review gates check cited-result trust. This covers take, active/ready done, sweep and DSA close through their existing shared gates. |
| `scripts/dev/tasks.py:901,904` | Tags: UNCHECKED, MACHINE-OK, VERIFIED-C1, VERIFIED-C2, DISPUTED. Citations are explicit `card:ID`, existing bare ID, or exact task JSON path in scope_in. Missing/self references fail closed. Ordinary report/source-file reads are not heuristically interpreted as trusting another card. |
| `scripts/dev/tasks.py:933` | Deterministic fingerprint binds explicit code/spec/data files, immutable question/result fields, flow data_scope and cited-result semantics. Mutable B-SHARED metadata is excluded so classifying a dependency does not falsely expire its result. Directory-only or missing-file scopes cannot receive positive pins. Upstream dependencies are also checked recursively, so changed input code is caught even if the upstream task JSON did not change. |
| `scripts/dev/tasks.py:974` | make_result_trust records supplied tag, checker_model, effort, UTC date, data_hash, code_revision, evidence and evidence_sha256. It never selects a VERIFIED tag automatically. Evidence must exist inside the checkout. |
| `scripts/dev/tasks.py:989` | Done state, minimum tier, nonempty typed fields, valid/non-future date, current input revision/data and unchanged evidence are required. Malformed/missing/weak/disputed/expired trust returns blocking errors. C3 has no sufficient tag in this schema and remains fail closed. A declared flow risk_class is included in the required tier. |
| `scripts/dev/tasks.py:1032,1050,1078` | Mutating lifecycle commands mark cited bases B-SHARED, class at least C2, and record shared_consumers. Pure queue/gate queries do not rewrite cards. Existing save-time B-SHARED marking remains compatible. |
| `scripts/dev/tasks.py:1085`; `scripts/dev/lab_flow.py:319,360` | Ordinary/flow completion defaults only to UNCHECKED; flow finish applies the same cited-base gate. No success receipt is automatically scientific verification. |
| `MyTradingSys/system/roles/lab_guy.md`, Result trust receipt contract | Documents tier mapping, explicit citation grammar, pinning, re-check bootstrap, expiry and the R1 authority limitation. |

The code revision is scoped-content/contract plus its last scoped commit, not the moving branch HEAD. Data-less source/code results get a deterministic empty-dataset hash; no fictitious market dataset is asserted. Declared raw files must be individually pinned, not silently skipped behind a directory name. Undeclared data cannot be certified by a receipt.

## Validation

Red first, before the helpers/gates existed:

```
python -m pytest scripts/dev/test_tasks.py::ResultTrustTest -q --tb=short
```

**7 failed, 1 passed**, including actual unchecked take acceptance and absent helper failures. Subsequent focused red tests exposed directory scopes being silently unpinned, code-only results lacking a usable empty-data hash, and flow risk_class being ignored. A transitive test also caught false expiry from save-time B-SHARED metadata; binding cited-result semantics rather than whole task-JSON bytes fixed that without weakening upstream expiry.

Tests cover UNCHECKED rejection; VERIFIED-C1 allowance and C2 strength; code/data/evidence expiry; missing/malformed/disputed/weak receipts; explicit task-file citations; query purity and shared-base marking; take and active done; ready/active flow close; completion's UNCHECKED default; flow data pins/risk class; transitive input changes; and rejection of directory-only positive pins.

Final focused command:

```
python -m pytest scripts/dev/test_tasks.py scripts/dev/test_lab_flow.py scripts/dev/test_lane_health.py MyTradingSys/tests/test_tasks_lab_precheck.py MyTradingSys/tests/test_review_receipts.py -q --tb=short
```

Final result: **181 passed, 508 subtests passed in 25.14 s**. Task lint passed. `git diff --check` passed.

The first ship gate additionally caught the Lab_Guy role header's stale content token after the contract documentation edit. Ran `python scripts/dev/role_loader.py retoken MyTradingSys/system/roles/lab_guy.md`; the focused `test_builder_role.py` then passed 4 tests and `role_loader.py check` reported every role token fresh. No role policy was changed during this correction.

Mutation probes on temporary test objects: replacing result_trust_problems with a no-op made the real unchecked-take test fail; replacing result_fingerprint with a fixed digest made code and data expiry subtests fail. Both mutants were killed. No product source mutation was left behind.

## Inventory and required independent re-checks

Machine-readable inventory: `2026-10-19_lab-trust-tag-inventory.json` beside this report. Selection: all 16 finished event-table cards, plus eight foundational gate/formula/power/fee candidates from the task registry. This is a bounded base inventory, not a claim to have discovered every downstream consumer in arbitrary prose.

**24 bases: 24 UNCHECKED.** C1/C2 assignments below are OURS risk candidates for refinement, not retrospective acceptance stamps. No outcomes or old backtests were rerun.

| C2 candidate | Raw re-check card |
|---|---|
| gap-g1-power-mde-helper | trust-recheck-gap-g1-power-mde-helper |
| gpt-formulas-rederive | trust-recheck-gpt-formulas-rederive |
| gptb-dev-split-guard | trust-recheck-gptb-dev-split-guard |
| gptb-forward-excursion-helper | trust-recheck-gptb-forward-excursion-hel |
| lab-data-pin-hash | trust-recheck-lab-data-pin-hash |
| lab-dax-net-fee-verdict | trust-recheck-lab-dax-net-fee-verdict |
| lab-machine-checks-extra | trust-recheck-lab-machine-checks-extra |
| q76-dev-ext-power-check | trust-recheck-q76-dev-ext-power-check |

Each C2 candidate has one raw independent-review card, with producer identity/different-vendor verification required during refinement. The 16 table candidates remain C1 and require review before trusted consumption. Re-checks audit source/evidence with the base identified in refs; they do not assume the unchecked base as a trusted scope_in premise. Raw cards authorize no outcome rerun and carry no review stamp.

## Limits

Explicit card citations are enforced; arbitrary prose/report paths are not automatically resolved to producer cards. This avoids silently classifying every source-file read as a result dependency. Receipt fields do not authenticate a reviewer: R1 remains open and the independent C1/C2 review policy still applies. VERIFIED-C2 does not authorize live-path C3 use. No holdout read, live deployment, scheduler, or model call was added.

Separate delivery receipt: content commit, empty git cherry against origin/fast-track, and upstream report existence. Full CI follows the mandatory ship gate.
