# Reply-shape CLI input contract

**Result:** A bare invocation now exits with argparse status 2 instead of waiting for stdin EOF. Stdin remains supported through an explicit `-` argument.

## Evidence

- `scripts/dev/reply_shape_check.py` accepted an optional path and read stdin whenever the path was omitted. The 2026-10-28 health-check report records a 120-second timeout for that invocation (`MyTradingSys/research/health_checks_run_2026-10-28/REPORT.md:56-58`).
- Before the fix, the new no-argument/open-pipe test timed out after 2 seconds. Both explicit-`-` tests failed because the old implementation tried to open a file named `-`. The targeted test file reported **3 failed, 5 passed**.
- After the fix, `python -m unittest scripts.dev.test_reply_shape_check -q` reported **8 tests, OK** (0.276s). This covers prompt no-argument failure with stdin left open, shaped and dummy piped replies with explicit `-`, and existing file-path behavior.
- Repository caller search found no invocation relying on implicit no-argument stdin. The only code caller is the test module, which passes a file path; `extra_tests.tsv` already registers that test file. The tool inventory in `LAYER_LAB.md` names the script but does not invoke it.

## Contract

- `REPLY_FILE` reads the named file.
- `-` reads stdin.
- Omitting the input source exits with usage status 2 and does not read stdin, whether stdin is a terminal or an open pipe.

## Files

- `scripts/dev/reply_shape_check.py`: document and enforce the input contract.
- `scripts/dev/test_reply_shape_check.py`: add subprocess regressions for an open stdin pipe and explicit stdin input.
- `MyTradingSys/system/tasks/reply-shape-explicit-stdin.json`: routine CODEX build card.
