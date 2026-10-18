Changed files: `MyTradingSys/backtest/tom_dax_bt.py`, `MyTradingSys/backtest/test_tom_dax_bt.py`, `MyTradingSys/research/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md`. H7 red then green; 3 H7 tests and 58 total harness tests pass.

# lab-dax-readiness-gate

Surface COD, unattended build, 2026-10-12 UTC. Completion: DONE.

## What was checked

- Audit file legend at `2026-10-11_lab-audit-tom-dax-bt.md:13-22`, twelve-item assessment and H7 at lines 31-62; historical D references 488-593 and 677-698 now correspond to the expanded report builder and CLI. Current report builder inspected at `tom_dax_bt.py:793-923` before edits, CLI at 1059-1084.
- `PRE_REG_TEMPLATE.md:1-65`, all twelve numbered headings and answer/evidence requirement; `PRE_REG_DAX.md:1-38` read only. `LAYERS.md:11-42` Tom section and `ROADMAP.md:21-29` STOP rules read.
- H7's cited source evidence: `PROFILE_PARITY.md:1-24` remains NOT_IN_DATA; `RECALL_DAX.md:1-9` reports historical 0/7 and STOP. These documents supply context, not new readiness approvals.
- Synthetic fixtures only: twelve-item declarations, fabricated split/session JSON, empty verdict rows, two constant-price bars and a fabricated BTC-cache metadata file. Temporary report/registry writes and price inputs were patched into fixtures; git was stubbed. Final suite runs set `tempfile.tempdir` to the work tree and `PYTHONPATH` to `F:\MTS\mts-codex-lab`.

## Findings and changes

| Severity | File:line | Claim | Evidence | Fix / disposition |
|---|---|---|---|---|
| HIGH | `tom_dax_bt.py:828-831` | MISMATCH before; MATCH after: missing/partial/unanswered readiness must block before outcome access. | 74 corrected pre-fix subcases reached the coverage sentinel instead of raising a readiness error. | Mandatory completeness validation is the first operation of `build_report`, before split/session, coverage, prices, simulation and holdout reservation. |
| HIGH | `tom_dax_bt.py:411-445,1121` | MATCH: all twelve items require answers/evidence or explicit named waivers. | `test_tom_dax_bt.py:932-966` removes each item in turn and checks unanswered status, TODO answer, missing evidence, NOT_IN_DATA evidence and unnamed waiver. `test_tom_dax_bt.py:1009-1029` checks malformed JSON/types and holdout reservation ordering. | Required `--readiness-manifest`; exact string keys `1`..`12`, corresponding to template heading numbers. `ANSWERED`/`WAIVED` only; answer and evidence nonempty/non-placeholder; `WAIVED` also requires approver. No bypass flag. |
| MED | `tom_dax_bt.py:829,841,993-1005` | MATCH: the declaration used by the report is captured before outcomes. | Parsed items and full exact-byte SHA-256 enter accounting and are printed alongside answer, evidence and approver. | In-memory frozen declaration; completeness validation does not certify evidence truth. H8 still owns full immutable experiment/cache identity. |
| HIGH | `tom_dax_bt.py:874`; `test_tom_dax_bt.py:968-1007` | MATCH in the starting checkout: selected DAX market already excludes BTC. | Synthetic CLI call with BTC cache present: exactly four `simulate('dax', ...)` calls, zero BTC simulation calls, zero BTC price reads; only DAX rows requested. | Existing loop retained and regression guard added. The card's historical claim that both markets run is superseded by the inspected code. |
| MED | `PROFILE_PARITY.md:6-23`; `RECALL_DAX.md:3-7` | NOT_IN_DATA / MATCH: this build supplies no production readiness evidence. | Parity remains unverified; historical recall is 0/7. | Existing research/encoding owners provide the real manifest, including authorized price-only scope if applicable. No evidence inferred or trader parameter changed. |

Manifest schema (example describes fields, not production approval):

```json
{"items": {"1": {"status": "ANSWERED", "answer": "owner's answer", "evidence": "file:line"}, "5": {"status": "WAIVED", "answer": "explicit waiver reason/scope", "evidence": "authorization-file:line", "approver": "named owner"}}}
```

The illustrative object is partial and is rejected; a usable manifest must include every key through `12`. Answer/evidence/approver placeholders `TODO`, `NOT_ANSWERED`, `NOT_IN_DATA`, blank strings and nonstrings are refused. Evidence content is not scientifically adjudicated by the harness.

## Red then green

EXPECT: invalid declarations fail before any coverage/data/simulation access; a complete synthetic answered declaration and a named parity waiver pass; DAX-only CLI never reads or simulates BTC.

Corrected red command, executed against unchanged product code after fixing two fixture mistakes (an incorrect helper class name and an incomplete stub split):

```powershell
$env:PYTHONPATH=(Get-Location).Path
python -B -c "import unittest; from MyTradingSys.backtest.test_tom_dax_bt import TestReadinessGate; r=unittest.TestResult(); unittest.defaultTestLoader.loadTestsFromTestCase(TestReadinessGate).run(r); print('Ran',r.testsRun,'tests; failures=',len(r.failures),'errors=',len(r.errors)); print('FIRST FAILURE:',r.failures[0][1] if r.failures else 'none'); print('FIRST ERROR:',r.errors[0][1] if r.errors else 'none'); raise SystemExit(not r.wasSuccessful())"
```

RESULT (2026-10-12, COD lab), red exit 1:

```text
Ran 2 tests; failures= 74 errors= 2
FIRST FAILURE: AssertionError: data accessed before readiness
  build_report -> require_download_coverage (old tom_dax_bt.py:815)
FIRST ERROR: SystemExit: 2
  error: unrecognized arguments: --readiness-manifest .../readiness.json
```

The supplemental malformed/holdout test was also checked against an in-memory reconstruction of the pre-gate `build_report` (removed the new first readiness call and restored the original accounting dictionary; no disk reversion): 1 test, 10 failures, 0 errors. It reached the old split error instead of the required readiness error. The original two tests were run red on the actual unchanged file, not this reconstruction.

Final green commands:

```powershell
$env:PYTHONPATH=(Get-Location).Path
python -B -c "import tempfile,unittest; from pathlib import Path; tempfile.tempdir=str(Path.cwd()); suite=unittest.defaultTestLoader.loadTestsFromName('MyTradingSys.backtest.test_tom_dax_bt.TestReadinessGate'); r=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(not r.wasSuccessful())"
python -B -c "import tempfile,unittest; from pathlib import Path; tempfile.tempdir=str(Path.cwd()); suite=unittest.defaultTestLoader.loadTestsFromName('MyTradingSys.backtest.test_tom_dax_bt'); r=unittest.TextTestRunner(verbosity=1).run(suite); raise SystemExit(not r.wasSuccessful())"
```

RESULT (2026-10-12, COD lab), both exit 0:

```text
test_complete_manifest_and_dax_cli_with_btc_cache ... ok
test_malformed_manifest_and_no_holdout_reservation ... ok
test_missing_partial_or_unanswered_manifest_before_any_simulation ... ok
Ran 3 tests in 0.208s
OK

Ran 58 tests in 0.423s
OK
```

Existing split/session/coverage tests were supplied explicit synthetic readiness fixtures (or an isolated readiness stub when testing another missing-manifest guard), preserving their prior assertions. Report serialization is exercised with synthetic inputs, including digest and named-approver assertions.

No market-data backtest, recall or holdout read was run; no empirical trial or TRIALS.md row was created. No git, sync claim/ship/release or full quick gate was run. Runner owns shipping checks. The required `tasks.py done` closure also updates its card and regenerates the layer index as that command normally does.

## Follow-up cards

None created. Existing `tom-encode-spike-fade`, `tom-profile-parity-check`, `tom-holdout-clean-split` and `tom-layer-v2-cost` remain evidence owners. This build does not authorize a real outcome run.
