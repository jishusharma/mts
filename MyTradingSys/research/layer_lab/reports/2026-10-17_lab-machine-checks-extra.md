# Lab machine checks: lab-machine-checks-extra

Verdict: PASS - all four seeded bad-card cases are refused and good cases pass.

## What changed and evidence

- `scripts/dev/tasks.py:57, 200-212` recognizes `formula_id` and `formula_ids`, and checks each against numbered headings in `MyTradingSys/backtest/layers/FORMULAS.md`. Seeded unknown `s999` is refused; `s1` passes (`scripts/dev/test_tasks.py:511-513`).
- `scripts/dev/tasks.py:215-226` compares exact card mentions in `TRIALS.md` with `card` rows in `F:/codex_home/lab_runs/runs.jsonl` for CODEX run cards. Seeded ledger/run mismatch is refused; matching count passes (`scripts/dev/test_tasks.py:515-522`). Existing NUC log was readable; the current tracked run card `rv04-q33-matrix-rerun` has zero ledger rows and zero runner rows.
- `scripts/dev/tasks.py:86-107` scans `scope_in` citations on save and raises the cited card's weight to `B-SHARED`; the value is accepted by card validation. Seeded citation promotes `BASE1` (`scripts/dev/test_tasks.py:524-530`).
- `scripts/dev/tasks.py:228-247` requires new CODEX build cards to name `path/to/test.py::test_*`; the named test must exist and its source must include a dummy/shuffled probe plus rejection assertion/exception. Missing or non-rejecting probes fail (`scripts/dev/test_tasks.py:532-543`). `scripts/dev/lab_flow.py:64-65, 107-108, 162-179` includes this metadata in the flow contract and validates generated build cards.

## Verification

`python -m pytest scripts/dev/test_tasks.py scripts/dev/test_lab_flow.py -q -p no:cacheprovider --basetemp=F:/MTS/mts-codex-lab/.pytest-tmp`

Result: **73 passed, 307 subtests passed**. The four new tests cover a bad and good seed for each check; flow tests also verify mutation metadata is carried into the contract.

Mutation validation is a deterministic source-level gate: it verifies a named test exists and contains a dummy/shuffled negative assertion or expected exception. The test itself remains part of the card's named suite and is run by that suite.
