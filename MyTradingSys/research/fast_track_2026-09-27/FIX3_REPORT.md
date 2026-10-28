# FIX3 report - FT-2 adversarial-review fixes (2026-09-28, code mode)

Branch `fast-track` (created from `master`; there is no `main` branch in this repo).
Nothing was pushed or merged, and nothing contacted an exchange.

## Commits
| Commit | Content |
|---|---|
| `c4c5507` | Batch 1 (FIX3): deribit_orders, executor, position_manager, kill_switch, daily_loss_monitor, run_testnet_suite.py (helpers), run_testnet_suite_ft2.py, offline tests (test_fix3_offline, test_fix3_mutants_offline, gh/s3/s6/halt_preflight, s1), review/ folder + `fix3_diff.patch` |
| `03bd840` | Batch 2: the rest of the FT2_RUNBOOK promotion table (risk_guard, daily_loss_guard, soak_report, 5 unit-test files, run_testnet_suite_g1g2.py G1c), scripts/worker/queue_tool.py, BT_BUILD_NOTES.md, PBO_019_RESULT.md |

Backups (untracked, per the rule): `<file>.pre_fix3` for every live file that was replaced, and
`<file>.py.new.pre_fix3` for the four staged files as they were before FIX3.

## Findings
| ID | Status | Fix (smallest change) | Test(s) in test_fix3_offline.py |
|---|---|---|---|
| C1 | FIXED | `_call`: transport errors (OSError/URLError/ValueError/RuntimeError) on order-creating calls -> `OrderStateUnknown`, never resent; reads/cancels retry MAX_RETRIES then `DeribitError`; a failed re-auth -> `DeribitError` | `test_C1_*` (3 on the real `_call`) + `test_C1_R1_*` |
| C2 | FIXED | everything after the intent event runs under `except Exception` -> `fail_closed("R7 unexpected")` (ExecutionHalted passes through) | `test_C2_*` (2) |
| C3 | FIXED | executor.fail_closed + position_manager.flatten_halt: cancel entries/targets -> close -> **re-read position** -> cancel the stop by id + label only when flat; if still open, the stop is kept and FAIL-CLOSED/FLATTEN ITSELF FAILED | `test_C3_*` (4, order + stop survives failed close) |
| H1 | FIXED | every cancel is its own `try/except Exception` (journaled), and the flatten always runs; a failed position read still attempts the close | `test_H1_*` (2) |
| H2 | FIXED | kill_switch CLI writes HALT **first**, then auth + kill_all under try; discovery `get_positions` failure falls back to BTC-PERPETUAL | `test_H2_*` (2) |
| H3 | FIXED | on breach, HALT_DAILY_LOSS + `breached_today` are written before kill_all; a kill_all exception is journaled; `main()` survives transient errors, and after 3 consecutive failures it writes HALT_DAILY_LOSS | `test_H3_*` (2) |
| H4 | FIXED | atomic `save_state` (tmp + `os.replace`); a present-but-unreadable/non-dict state -> HALT_DAILY_LOSS, no re-baseline, the file is left for the operator | `test_H4_*` (3) |
| H5 | FIXED | `query_failed` never re-places; it counts toward MAX_UNPROTECTED_SECONDS and then goes to flatten_halt, which keeps the stop until flat | `test_H5_*` (3) |
| H6 | FIXED | base-suite helpers (exec'd by g1g2 + FT-2) refuse to start while a real HALT/HALT_DAILY_LOSS exists, redirect `ex/pm.HALT_PATH` + `HALT_DAILY_LOSS_PATH` to a temp dir, and clear them in `clean()`; T-c passes temp `state_path`/`halt_path`. Suite plan_ids are cut to <= 24 chars (M6) | `test_H6_*` (2, static; they run only with `MTS_REPO_ROOT` set and are skipped in the staged sandbox) |
| M1 | FIXED | only a well-formed `YYYY-MM-DD` date strictly before today is non-blocking; today, future, garbage, non-string, or a non-object -> refuse | `test_M1_*` (3) |
| M3 | FIXED | HALT_DAILY_LOSS is read as utf-8-sig, then utf-16; any ValueError/OSError -> clean refusal | `test_M3_*` (2) |
| M5 | FIXED | fail_closed and flatten_halt write `execution/HALT` first (never raises) | `test_M5_*` (3) |
| M6 | FIXED | preflight refuses a plan_id that does not match `^[A-Za-z0-9_-]{1,24}$`; `_xlabel` raises instead of slicing | `test_M6_*` (3) |
| M2 | NOT FIXED (out of brief) | a valid past-dated HALT_DAILY_LOSS still only warns (auto-resume at 00:00 UTC). This is an operator contract decision | - |
| M4 | NOT FIXED (out of brief) | HALT is not re-checked mid-run (repro R14 still CONFIRMED) | - |
| M7, M8, L1-L7 | NOT FIXED (out of brief) | R15 (L1) and R16 (M7) still CONFIRMED | - |

Mutation survivors: `test_fix3_mutants_offline.py` has 13 tests, one per survivor (R3 M1 K1 K2 K4
E1 E2 E3 E7 E8 E11 P2 P5). A worker applied each mutation to a copy of the sandbox: **13/13
killed**. The FIX3 tests were also run against the pre-FIX3 code: every fix test fails there.
Only the positive/no-regression checks pass on both versions.

## Gate (run on the staged tree, and again on the promoted tree before each commit)
**Gap, fixed after verification:** this gate never executed the testnet suite files FIX3 edited
(`run_testnet_suite.py` plan builder, `run_testnet_suite_g1g2.py`), so D1/D2 below reached testnet.
The gate now also includes, and must include from here on:
- `python MyTradingSys/execution/testnet/test_suite_static.py` -> 5 OK. This offline AST check builds
  every suite plan through the real `plan()` builder and runs the validator structure check and the
  M6 plan_id rule on each. It also checks that every literal order and journal amount is a multiple
  of 10. It fails on the pre-D1 and pre-D2 sources.
- `python -m pytest MyTradingSys/tests/docs -q` -> 5 passed (boot build doc tests).
- `run_staged_tests ... test_daily_loss_guard ... test_soak_report test_fix3_offline`: **Ran 116 tests, OK**
  (baseline 68 + 48 new; with `MTS_REPO_ROOT` set, 0 skipped)
- `run_staged_tests ... --script test_g1g2_offline.py --fake ...`: **12/12 PASS**
- live tree after Batch 2: `python -m unittest test_risk_guard test_kill_switch test_daily_loss_guard test_daily_loss_monitor test_soak_report` in execution/: 43 OK

Side effect handled: fail_closed/flatten_halt now write HALT, so the existing offline tests
(gh_executor, s3, s6) clear the sandbox HALT in setUp/tearDown. Without that, later tests are
refused by a leftover HALT.

## repro_ft2.py against the staged (and then promoted) code
NOT REPRODUCED: R1 R2 R3 R4 R5 R6 R7 R8 R9 R11 R11b R12 R-DO.
Harness ERROR, **fixed by design**: R10 (run_once now returns `state=None` plus a HALT instead of a
re-baselined state, and the harness subscripts it) and R13 (`_xlabel` now raises on >64 instead of
colliding). Both are covered by `test_H4_torn_state_*` and `test_M6_xlabel_never_truncates`.
Still CONFIRMED (out of brief): R14 (M4), R15 (L1), R16 (M7).

## Batch 2: NUC task 019 + PBO
See `PBO_019_RESULT.md`. The verify verdict is REVIEW: `ref_pbo.py.new` matches the spec, but the
worker's own tests have 2 wrong expectations, so `ref_pbo` is left staged and not promoted.
`bt_stats.pbo_cscv` and `ref_pbo_cscv` agree **exactly** on 50 iid seeds (T=320, N=10, S=8). Across those seeds,
PBO has mean 0.56, median 0.62, std 0.24, and range [0.014, 0.971]. Only 64% of seeds fall
inside (0.2, 0.8).
**The (0.2, 0.8) band is not justified.** It is a single-seed flaky gate, with about a 36% false-fail rate
on correct code. Replace it with a multi-seed aggregate check (`test_bt_stats.py.new:62-64`).

## Independent review by Qwen (NUC task 022-fix3-review)
Packed with `fix3_diff.patch` + the adversarial review. Qwen took 1575 s on JIS-NUC (791 output tokens).
It marked all 12 in-scope IDs ADDRESSED, reported **no new defect**, and gave EXPECT 3/3.
The verify verdict is REVIEW only because the checker flags the live module names (`executor.py` etc.) as
"not in scope". The scope held the diff, not the modules, so this is a checker artefact.
Weight: this is a shallow confirmation, not an adversarial pass. It restates the changes, and one line is
mis-described: the executor `except (ValueError, OSError)` catches the error and refuses; it does not raise.
The binding evidence is the tests, the 13/13 mutant kills, and repro_ft2.

## What the operator runs next (testnet) - FT2_RUNBOOK.md
The promotion steps (runbook Steps 1-6) are **already done on `fast-track`** by the two commits
above. Do not rename anything. Check out `fast-track` and start at the verification steps:
1. Offline gate (runbook Step 7), now with the FIX3 tests added, plus
   `python MyTradingSys/execution/testnet/test_suite_static.py` (5 OK):
   `python scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline -- test_gh_retry_offline test_gh_executor_offline test_s6_orphan_offline test_s3_unprotected_offline test_s1_cap_offline test_risk_guard test_kill_switch test_daily_loss_guard test_daily_loss_monitor test_soak_report test_halt_preflight_offline test_fix3_offline`
   -> expect `Ran 116 tests ... OK`. Then the g1g2 offline script -> `12/12 PASS`.
2. Make sure `execution/HALT` and `execution/HALT_DAILY_LOSS` do **not** exist. The suites now
   refuse to start while either one exists.
3. `python MyTradingSys/execution/testnet/probe_account_summary.py` (runbook probe step).
4. `python MyTradingSys/execution/testnet/run_testnet_suite.py` -> 6/6 PASS (C1-C6). C5
   (fail-closed) now also writes HALT, but only into the suite's temp dir.
5. `python MyTradingSys/execution/testnet/run_testnet_suite_g1g2.py` -> base 6/6 + G1/G2 incl. G1c.
6. `python MyTradingSys/execution/testnet/run_testnet_suite_ft2.py` -> FT-2 4/4 (T-b..T-e). T-c no
   longer touches the real HALT_DAILY_LOSS or state file.
7. Kill-switch CLI check (runbook): `python MyTradingSys/execution/kill_switch.py --confirm KILL`.
   "HALT file written" is now printed **before** the KILL SWITCH REPORT. Delete `execution/HALT`
   afterwards.

Contract changes for the operator:
- a HALT_DAILY_LOSS with a malformed, future, or non-date `date` now **blocks**. Only a valid past date warns.
- any executor fail_closed or manager flatten now leaves `execution/HALT`, and nothing trades until you
  review the account and delete it.
- plan_ids must be <= 24 chars of `[A-Za-z0-9_-]`. Some `examples/*.json` ids are longer
  (e.g. `invalid_ladder_multiplier_mismatch`) and will be refused at preflight.

## Testnet verification result (operator machine, 2026-09-28)
The "6/6 PASS" lines above are the operator's *expected* results. The code session never ran testnet.
The actual run:
| Step | Result |
|---|---|
| offline gate / g1g2 offline | 116 OK / 12/12 PASS |
| probe_account_summary.py | PASS, flat, equity 99.99998156 |
| run_testnet_suite.py | 6/6 PASS (after D1) |
| run_testnet_suite_g1g2.py | 6/6 + G1/G2 4/4 (after D2) |
| run_testnet_suite_ft2.py | 6/6 + G1/G2 4/4 + FT-2 4/4 |
| kill_switch.py --confirm KILL | HALT printed before the report (H2 verified); HALT removed afterwards |

Defects found (suite files only; no execution-layer code changed):
- **D1** `run_testnet_suite.py:41`: the FIX3 M6 edit put its comment in front of the rest of the line,
  so `account`/`instrument`/`side` were commented out, and C1-C4 failed with "missing required field:
  account". Root cause: a code-session patch error. Fixed by splitting the line.
- **D2** `run_testnet_suite_g1g2.py:62` (G1c, from the FT-2 staged file): sell 25 is not a multiple of
  the contract size (Deribit -32602). Fixed to 30, with the comment and journal amount updated to match.
Both are now caught offline by `test_suite_static.py`. The boot build doc-test FAIL, which predates
this session, was fixed in the same commit: `research/` runbooks are exempt from the no-git-references
rule, and the stale SIZE header on `03_FILE_INDEX.md` was corrected. Boot build: compile PASS,
math 126/126, doc 5/5.

