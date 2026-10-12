BLOCKED

# DAX H1 proof-count parity

RESULT (2026-10-12 UTC, unattended COD lab): H1 regression is red then green; all 33 DAX harness tests pass. The required quick gate exits 1 with six failed stages outside this card's editable scope. The card is not marked done.

## What was checked and changed

Source: `MyTradingSys/research/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md:14-24,56` (file legend and H1).
Read-only Java evidence: `src/main/java/datafeed/SetupCandidatesBuilder.java:568-626`, especially B144 at 579, emitted volume-spike flag at 615-616; scoring at 182-185.
The audited Python counter, rescore guard and printed ceiling cited by H1 were read before editing.

Changed files:

- `MyTradingSys/backtest/tom_dax_bt.py:69-98,175-180,374-405,428-447,641-654,666-670`: exclude volume_spike from the mirrored counter; version row envelopes and metadata with `java-b144-no-volume-spike-v1`; reject missing/incompatible versions both on reuse and on load; print ceiling 1 and corresponding minimum shifts (WATCH 2, SETUP_FORMING 4); refresh the parity/deviation text.
- `MyTradingSys/backtest/test_tom_dax_bt.py:202-343,347-383`: add current spike-only acceptance and stale snapshot/cache rejection regressions; update obsolete six-to-two proof fixtures to five-to-one; verify synthetic versioned cache generation/reuse/load and reject an unversioned envelope even with valid metadata. The fee-pair test uses synthetic shift 2 to exercise WATCH with one surviving proof; operational shifts/defaults were not changed.
- This report.

No real market data, archive, snapshot, recall or holdout was read or run. The cache-generation test uses a temporary synthetic gzip fixture and the BTC branch only to avoid any archive loader; it is not a BTC backtest. The original audit report, Java, runtime, PRE_REG_DAX, trial registries and task state are unchanged. Runner-owned Git/shipping operations were not invoked directly.

## Findings

| Severity | File:line or command | Classification and evidence | Fix / disposition |
|---|---|---|---|
| HIGH | `src/main/java/datafeed/SetupCandidatesBuilder.java:579,615-616`; `MyTradingSys/backtest/tom_dax_bt.py:80-98`; `MyTradingSys/backtest/test_tom_dax_bt.py:209-219` | MATCH after fix: spike-only proof counts 0 and rescore accepts current Java count 0. Before fix, count was 1 and rescore raised the exact H1 error. | Removed the spike increment; retained its emitted proof flag. |
| HIGH | `MyTradingSys/backtest/test_tom_dax_bt.py:202-207,347-383`; `MyTradingSys/backtest/tom_dax_bt.py:154-156,175-180,374-405,428-447` | MATCH: old spike-only snapshot count 1 is rejected; old unversioned rows fail both cache reuse and report loading. Current generated rows pass both paths. | Snapshot proof-count parity fails closed; row metadata and every row envelope require the new schema. Snapshots whose old/current counts are identical cannot be dated from proof JSON alone; the guard rejects incompatible counts. Broader source/config identity remains H8, outside this fix. |
| MED | `MyTradingSys/backtest/tom_dax_bt.py:641-654,666-670`; Java counter at 568-585 | MATCH: five counted proofs minus the four masked order-flow proofs leaves only rejection_wick, hence maximum 1. WATCH threshold 3 requires at least shift 2; SETUP_FORMING threshold 5 requires at least shift 4. | Corrected printed ceiling and related deviation text. No operational threshold or shift was tuned. |
| HIGH | `python scripts/dev/run_all_tests.py --quick` | MISMATCH against required green gate: exit 1, `FAILED: 6 step(s)`. See exact failed stages below. | BLOCKED: failing gate infrastructure/tests are outside scope; this sandbox also refuses temporary Git repository creation. Do not mark done or bypass the gate. |

## Red then green evidence

All commands ran from `F:\MTS\mts-codex-lab` with PowerShell environment setup `$env:PYTHONPATH = (Get-Location).Path` so the script can import `MyTradingSys`. The initial bare script invocation failed before test collection with `ModuleNotFoundError: No module named 'MyTradingSys'`; that import failure is not the red proof.

EXPECT from Java B144: volume_spike alone contributes 0; the valid snapshot's `score.proof_count=0` is accepted.

Before changing product code:

```text
python MyTradingSys/backtest/test_tom_dax_bt.py TestMask.test_volume_spike_only_counts_zero_and_rescore_accepts
FE
ERROR [current Java snapshot accepted]:
ValueError: proof JSON gives 1, score.proof_count is 0 (vwap)
FAIL [current Java count]:
AssertionError: 1 != 0
Ran 1 test in 0.002s
FAILED (failures=1, errors=1)
```

Additional rejection regressions were also run before the fix:

```text
python MyTradingSys/backtest/test_tom_dax_bt.py TestMask.test_old_volume_spike_snapshot_rejected TestDriver.test_old_rows_rejected_on_load_and_cache_reuse
FF
AssertionError: ValueError not raised  [old snapshot]
AssertionError: ValueError not raised  [old rows loaded]
Ran 2 tests in 0.011s
FAILED (failures=2)
```

After the fix, commands:

```text
python MyTradingSys/backtest/test_tom_dax_bt.py TestMask.test_volume_spike_only_counts_zero_and_rescore_accepts TestMask.test_old_volume_spike_snapshot_rejected TestDriver.test_old_rows_rejected_on_load_and_cache_reuse
Ran 3 tests
OK

python MyTradingSys/backtest/test_tom_dax_bt.py
Ran 33 tests
OK
```

Both final commands exit 0. These are synthetic correctness checks, not strategy trials.

## Exact completion blocker

`python scripts/dev/run_all_tests.py --quick` exited 1. Its complete stage summary reports:

```text
FAILED: 6 step(s)
  - Step 3dk: Desk board tests
  - Step 3k: sync.py tests
  - Step 3xt: Extra tests
  - Step 3ad: Auto-deploy tests
  - Step 3bk: Backup snapshot tests
  - Step 4: Pytest tests
```

Observed failure evidence from the gate output:

- Step 3dk: five setup errors in `scripts/dev/test_desk.py:23`; temporary `git init --bare` returns exit 128.
- Step 3k: ten setup errors in `scripts/dev/test_sync.py:29`; temporary `git init --bare` returns exit 128.
- Step 3bk: four setup errors in `scripts/dev/test_backup_snapshot.py:23`; explicit stderr: `fatal: cannot mkdir C:\Users\E-NGIN~1\AppData\Local\Temp\tmpwa5dgbvd\remote.git: Permission denied`.
- Step 3xt identifies `scripts/dev/test_suplock.py` as its failing extra test file; its inner failure detail was not printed by the gate's final-output excerpt.
- Step 3ad: 39 tests, one failure, observed `AssertionError: Lists differ: [1] != []`; the gate excerpt does not identify the failing test name.
- Step 4: `6 failed, 717 passed, 7 skipped, 2 warnings, 2 subtests passed`. The six failures are `test_b074_override_wins_for_every_proof_dir`, `test_b069_wrapper_log_agrees_with_exit_code`, `test_sync_news_runs_inside_a_live_tree_and_shows_the_result_line`, and `TestWrapperPs.test_wrapper_fails_closed_when_floor_unreadable`, `test_wrapper_matches_python_on_the_boundary`, `test_wrapper_rereads_floor_each_cycle`. The gate excerpt also reports pytest cache write warnings. Inner causes of these six failures were not established from that excerpt.

The gate itself invokes Git in its infrastructure tests; after these failures were known, no Git test was rerun. No permission escalation, Git command, gate modification or out-of-scope repair was attempted. The existing H1 code fixes and passing synthetic tests are retained for review, but the required quick gate has not passed, so `tasks.py done lab-dax-proof-parity` was deliberately not invoked.

## Follow-up cards created

None. The runner/owner must address the gate environment and out-of-scope failures before this card can close.
