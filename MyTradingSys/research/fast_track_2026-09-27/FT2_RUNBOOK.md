# FT-2 RUNBOOK: HALT preflight, kill-switch CLI, FT-2 testnet trip suite

**Date:** 2026-09-28
**Fast Track:** FT-2
**Goal:** Deploy the FT-2 batch (HALT-file preflight in executor, one-command
kill_switch CLI, and everything the S1/daily-loss/kill-switch/soak-report
work already staged this session depends on) and run the FT-2 testnet trip
suite, alongside the existing base + G1/G2 suites.
**Sources:**
- `MyTradingSys/execution/executor.py.new` (HALT-files note in its docstring)
- `MyTradingSys/execution/daily_loss_monitor.py.new` (HALT file contract)
- `MyTradingSys/execution/kill_switch.py.new` (CLI docstring)
- `MyTradingSys/execution/testnet/run_testnet_suite_ft2.py.new`
- FT-1's runbook (`FT1_RUNBOOK.md`) for the git-scoping and rollback conventions reused below

---

## 0. PRECONDITIONS

Same environment as FT-1 (Python 3.10+, Windows PowerShell 7, testnet secret
at `MyTradingSys/execution/.secrets/testnet.secret.json`, READ+TRADE-only /
no-withdraw key, `https://test.deribit.com/api/v2` reachable, no other MTS
process running against this account). See FT1_RUNBOOK.md §0/§1 for the full
checklist - not repeated here.

**python vs python3 on Windows:** this runbook and the harness scripts were
written/tested with `python3` on Linux (this session's operator desktop).
On the Windows machine that actually runs FT-2 on testnet, use whichever of
`python` / `python3` / `py` the operator's PATH resolves to a Python 3.10+
interpreter - check first:
```powershell
python --version
python3 --version
```
Everywhere this runbook shows `python3 ...`, substitute the working command
for that machine. Do not assume `python3` exists on Windows - many installs
only register `python`.

**Git scoping reminder (from FT-1):** plain `git status` is never clean on
this repo. Every git-status check below is scoped to just the files this
runbook promotes, exactly like FT-1's Step 1.

---

## 1. WHAT THIS BATCH ADDS (context, not steps)

This is the first promotion for six brand-new modules (`risk_guard.py`,
`daily_loss_guard.py`, `daily_loss_guard.py`, `kill_switch.py`,
`soak_report.py`, and their offline tests) plus updates to two files already
live from FT-1 (`executor.py` - S1 account cap + S6 orphan-stop sweep +
FT-2's HALT-file preflight; `position_manager.py` - S3 explicit
MAX_UNPROTECTED_SECONDS bound + S6 sweep) and one testnet-suite update
(`run_testnet_suite_g1g2.py` - adds case G1c). One new testnet suite file
(`run_testnet_suite_ft2.py`) is added, not a promotion of anything existing.

**HALT files (operator-relevant, not code):** after this batch, two files in
`execution/` gate every future `execute_plan()` call:
- `execution/HALT` - a manual, operator-only brake. Nothing in the code ever
  creates or deletes it. To pause all new trading by hand: create an empty
  file there. To resume: delete it.
- `execution/HALT_DAILY_LOSS` - written automatically by
  `daily_loss_monitor.py` on a daily-loss-cap breach (kill_all already ran by
  the time this file appears). Only a file dated **today (UTC)** blocks; a
  file from a previous day only prints a warning. Deleting it is a deliberate
  operator decision (review the account first) - nothing auto-clears it.

---

## 2. FILES TO PROMOTE (FT-2 batch)

| Staged File | Target | Kind |
|---|---|---|
| `execution/executor.py.new` | `execution/executor.py` | update (already live from FT-1; back up first) |
| `execution/position_manager.py.new` | `execution/position_manager.py` | update (already live from FT-1; back up first) |
| `execution/risk_guard.py.new` | `execution/risk_guard.py` | new |
| `execution/daily_loss_guard.py.new` | `execution/daily_loss_guard.py` | new |
| `execution/daily_loss_monitor.py.new` | `execution/daily_loss_monitor.py` | new |
| `execution/kill_switch.py.new` | `execution/kill_switch.py` | new |
| `execution/soak_report.py.new` | `execution/soak_report.py` | new |
| `execution/test_risk_guard.py.new` | `execution/test_risk_guard.py` | new |
| `execution/test_kill_switch.py.new` | `execution/test_kill_switch.py` | new (no prior live copy) |
| `execution/test_daily_loss_guard.py.new` | `execution/test_daily_loss_guard.py` | new |
| `execution/test_daily_loss_monitor.py.new` | `execution/test_daily_loss_monitor.py` | new |
| `execution/test_soak_report.py.new` | `execution/test_soak_report.py` | new |
| `execution/testnet/run_testnet_suite_g1g2.py.new` | `execution/testnet/run_testnet_suite_g1g2.py` | update (adds G1c; back up first) |
| `execution/testnet/run_testnet_suite_ft2.py.new` | `execution/testnet/run_testnet_suite_ft2.py` | new |

**Already live, not touched by this batch:** `execution/testnet/offline/test_s1_cap_offline.py`,
`execution/testnet/offline/test_halt_preflight_offline.py` - these are
offline-only test files (no exchange calls), promoted the same way the
existing `test_gh_executor_offline.py` / `test_s3_unprotected_offline.py` /
`test_s6_orphan_offline.py` / `test_g1g2_offline.py` were: written directly
as plain `.py` files, no `.new` staging step, since they never run against
the real exchange and carry no live-file risk. Nothing to promote for them
in this runbook.

---

## 3. DEPLOY STEPS (Windows PowerShell 7)

```powershell
cd MyTradingSys

# Step 1: git status, scoped to this batch's targets only
git status --porcelain -- execution/executor.py execution/position_manager.py `
  execution/risk_guard.py execution/daily_loss_guard.py execution/daily_loss_monitor.py `
  execution/kill_switch.py execution/soak_report.py `
  execution/test_risk_guard.py execution/test_kill_switch.py `
  execution/test_daily_loss_guard.py execution/test_daily_loss_monitor.py execution/test_soak_report.py `
  execution/testnet/run_testnet_suite_g1g2.py execution/testnet/run_testnet_suite_ft2.py
# EXPECT: "??" (untracked, for the brand-new files) or nothing. A line
# starting with " M" on executor.py / position_manager.py / run_testnet_suite_g1g2.py
# means a TRACKED file has uncommitted edits this promotion would overwrite - STOP.

# Step 2: Backup the two files that already have a previous FT-1 version
# (file-backup only, matching FT-1's rollback convention - never git reset/checkout)
Copy-Item execution/executor.py execution/executor.py.backup -Force
Copy-Item execution/position_manager.py execution/position_manager.py.backup -Force
Copy-Item execution/testnet/run_testnet_suite_g1g2.py execution/testnet/run_testnet_suite_g1g2.py.backup -Force

# Step 3: Diff each updated file before promoting (new files have no prior
# version to diff against - skip diff for those, just review the .new directly)
diff -Path execution/executor.py -DifferenceObject (Get-Content execution/executor.py.new) | head -80
diff -Path execution/position_manager.py -DifferenceObject (Get-Content execution/position_manager.py.new) | head -80
diff -Path execution/testnet/run_testnet_suite_g1g2.py -DifferenceObject (Get-Content execution/testnet/run_testnet_suite_g1g2.py.new) | head -80

# Step 4: Promote (rename) every file in the table above
Move-Item execution/executor.py.new execution/executor.py -Force
Move-Item execution/position_manager.py.new execution/position_manager.py -Force
Move-Item execution/risk_guard.py.new execution/risk_guard.py -Force
Move-Item execution/daily_loss_guard.py.new execution/daily_loss_guard.py -Force
Move-Item execution/daily_loss_monitor.py.new execution/daily_loss_monitor.py -Force
Move-Item execution/kill_switch.py.new execution/kill_switch.py -Force
Move-Item execution/soak_report.py.new execution/soak_report.py -Force
Move-Item execution/test_risk_guard.py.new execution/test_risk_guard.py -Force
Move-Item execution/test_kill_switch.py.new execution/test_kill_switch.py -Force
Move-Item execution/test_daily_loss_guard.py.new execution/test_daily_loss_guard.py -Force
Move-Item execution/test_daily_loss_monitor.py.new execution/test_daily_loss_monitor.py -Force
Move-Item execution/test_soak_report.py.new execution/test_soak_report.py -Force
Move-Item execution/testnet/run_testnet_suite_g1g2.py.new execution/testnet/run_testnet_suite_g1g2.py -Force
Move-Item execution/testnet/run_testnet_suite_ft2.py.new execution/testnet/run_testnet_suite_ft2.py -Force
Write-Host "FT-2 batch promoted"

# Step 5: Verify every file exists
Get-Item execution/executor.py, execution/position_manager.py, execution/risk_guard.py, `
  execution/daily_loss_guard.py, execution/daily_loss_monitor.py, execution/kill_switch.py, `
  execution/soak_report.py, execution/test_risk_guard.py, execution/test_kill_switch.py, `
  execution/test_daily_loss_guard.py, execution/test_daily_loss_monitor.py, execution/test_soak_report.py, `
  execution/testnet/run_testnet_suite_g1g2.py, execution/testnet/run_testnet_suite_ft2.py

# Step 6: Git add and commit
git add execution/executor.py execution/position_manager.py execution/risk_guard.py `
  execution/daily_loss_guard.py execution/daily_loss_monitor.py execution/kill_switch.py `
  execution/soak_report.py execution/test_risk_guard.py execution/test_kill_switch.py `
  execution/test_daily_loss_guard.py execution/test_daily_loss_monitor.py execution/test_soak_report.py `
  execution/testnet/run_testnet_suite_g1g2.py execution/testnet/run_testnet_suite_ft2.py `
  execution/testnet/offline/test_halt_preflight_offline.py
git commit -m "FT-2: HALT preflight (manual + daily-loss), kill_switch CLI, risk_guard/daily_loss_guard/daily_loss_monitor/soak_report, FT-2 testnet trip suite"
# EXPECT: "15 files changed"
```

---

## 4. VERIFICATION - RUN IN THIS ORDER

### 4a. Offline tests (fast, no exchange - run first, always)

```powershell
python3 scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline -- test_gh_retry_offline test_gh_executor_offline test_s6_orphan_offline test_s3_unprotected_offline test_s1_cap_offline test_risk_guard test_kill_switch test_daily_loss_guard test_daily_loss_monitor test_soak_report test_halt_preflight_offline
# EXPECT: "Ran 68 tests ... OK"

python3 scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline --script test_g1g2_offline.py --fake fake_deribit_orders.py=deribit_orders.py
# EXPECT: "12/12 PASS"
```

Both ran clean against the staged (`.new`) code in this session before
promotion - 68/68 and 12/12 - so a failure here after promotion means the
promoted files differ from what was tested (check Step 3's diffs again).

### 4b. Account probe (operator-run, read-only - do this before trusting live PnL numbers)

```powershell
cd MyTradingSys/execution/testnet
python3 probe_account_summary.py
```
Read its own docstring / printed output before trusting `daily_loss_monitor.py`'s
live numbers - see that file and `daily_loss_monitor.py`'s own docstring for
exactly what to check (equity's PnL-netting behavior, BTC vs USD denomination).

### 4c. Base regression (must still be 6/6 before anything FT-2-specific)

```powershell
python3 MyTradingSys/execution/testnet/run_testnet_suite.py
# EXPECT: 6/6 PASS (C1-C6)
```

### 4d. G1/G2 suite, now with G1c

```powershell
python3 MyTradingSys/execution/testnet/run_testnet_suite_g1g2.py
# EXPECT: base 6/6 PASS, then:
# PASS G1a stop shrinks on target fill
# PASS G1b reduce-only oversize never reverses
# PASS G1c partial target fill then forced flatten - zero plan-label orders left
# PASS G2a forced mismatch -> halt
#
# G1/G2: 4/4 PASS
```

### 4e. FT-2 suite (the new gaps)

```powershell
python3 MyTradingSys/execution/testnet/run_testnet_suite_ft2.py
# WHAT IT DOES: runs run_testnet_suite_g1g2.py first (which itself runs the
# base suite first) - so a FT-2 FAIL with the base/G1G2 suites not shown
# passing above means STOP there, not in this file.
#
# EXPECT OUTPUT:
# (base 6/6, then G1/G2 4/4, printed by the subprocess it runs first)
# PASS T-b account cap refused before any order
# PASS T-c daily loss breach -> kill + HALT_DAILY_LOSS + next refused
# PASS T-d unprotected -> re-placed or flattened, never naked
# PASS T-e kill switch -> flat, zero open orders
#
# FT-2: 4/4 PASS
```

**Uncertain / operator judgment call - T-c specifically:** this case forces
a real breach by doing a tiny market-in/market-out round trip on
BTC-PERPETUAL and checking against a cap of **-$0.01** - i.e. it relies on
TESTNET's real (even if tiny) taker fees making the round trip cost more
than one cent, not on any injected/fabricated loss. This is the one case in
this suite that depends on live TESTNET fee behavior rather than pure code
logic. If T-c fails with `"breach": false` specifically (not a HALT-file or
kill_switch problem), check whether TESTNET fees are temporarily
zero/rebated, or whether the round trip's own price movement happened to be
net positive by more than the fee cost - a larger round-trip size (not a
code change) is the fix, not evidence of a bug in `daily_loss_monitor.py`.

**T-b's cap override:** `risk_guard.check_new_plan_against_cap` reads `MAX_ACCOUNT_NOTIONAL_USD` at call time (`cap=None` default, Opus fix 2026-09-28), so the module constant is the single place to tune the cap. T-b lowers it in-process and restores it in a `finally`.

### 4f. Manual kill-switch CLI smoke check (operator-run once, optional but recommended)

```powershell
cd MyTradingSys/execution
python3 kill_switch.py --confirm KILL
# EXPECT: "KILL SWITCH REPORT" printed, then "HALT file written: ...execution\HALT ..."
Get-Item HALT   # confirm it exists
Remove-Item HALT   # delete it yourself once you've reviewed the account - nothing else will
```
Confirm `python3 kill_switch.py` with no `--confirm` (or any value other than
the literal `KILL`) prints `REFUSED: --confirm KILL required ...` and does
**not** create `HALT` or touch the exchange.

---

## 5. ROLLBACK (file-backup restore only - no git reset/checkout, per FT-1's convention)

```powershell
if (Test-Path execution/executor.py.backup) { Move-Item execution/executor.py.backup execution/executor.py -Force }
if (Test-Path execution/position_manager.py.backup) { Move-Item execution/position_manager.py.backup execution/position_manager.py -Force }
if (Test-Path execution/testnet/run_testnet_suite_g1g2.py.backup) { Move-Item execution/testnet/run_testnet_suite_g1g2.py.backup execution/testnet/run_testnet_suite_g1g2.py -Force }
Write-Host "FT-2 executor/position_manager/run_testnet_suite_g1g2 rolled back"
```
The six brand-new modules (`risk_guard.py`, `daily_loss_guard.py`,
`daily_loss_monitor.py`, `kill_switch.py`, `soak_report.py`,
`run_testnet_suite_ft2.py`) and their tests have no prior live version to
restore - rolling back means deleting them (`Remove-Item`) if the operator
decides the whole batch should be reverted, not restoring a `.backup`.
Deleting is a deliberate operator call, not automated here.

If any HALT file was left behind by a partial/failed run
(`execution/HALT` or `execution/HALT_DAILY_LOSS`), review the account state
on the testnet UI before deleting it - do not delete either file reflexively
as part of rollback.

---

## 6. SUMMARY

**FT-2 path:** promote 14 files (2 updates + 1 test-suite update + 11 new) →
offline tests (68/68 + 12/12) → probe → base suite (6/6) → G1/G2 (4/4,
now with G1c) → FT-2 suite (4/4) → optional manual kill-switch CLI smoke
check → commit.

**Success criteria:** every count above matches; the FT-2 suite's own
subprocess chain means a single `4/4 PASS` on `run_testnet_suite_ft2.py`
already implies the base and G1/G2 suites passed too, but running them
separately first (§4c/§4d) gives a clearer failure point if something is
wrong.

**Time budget:** offline ~instant; probe ~seconds; base+G1G2+FT-2 testnet
suites together ~5-8 minutes (FT-2 alone re-runs the other two as its own
precondition, so most of that time is those, not the four new cases).

### HALT Files (Post-FIX3)

FIX3 introduced significant changes to how HALT files are handled and enforced:

1. **Enforcement Timing:** The preflight check for HALT files now happens only once at the start of `execute_plan()`. However, a new mid-run check (`_halt_check_mid_run()`) is added that re-evaluates both HALT files before every order-creating call (entries, stop create/resize, targets). This prevents a race condition where an operator or kill_switch/daily_loss_monitor writes a HALT file while a plan is in progress.

2. **Kill Switch Integration:** The `kill_switch.py` CLI now explicitly writes the `execution/HALT` file before performing any exchange operations. This ensures that even if the kill switch fails partway through, trading is immediately halted to prevent further activity.

3. **File Contract Clarification:** 
   - `HALT`: A generic operator-only brake with no content requirements.
   - `HALT_DAILY_LOSS`: Must be a valid JSON file containing:
     ```json
     {"date": "YYYY-MM-DD", "reason": str, "ts_iso": str}
     ```
     The file's existence blocks execution regardless of date. A well-formed past-dated file refuses with a clear message indicating the operator must review and delete it.

4. **Operator Workflow:**
   - If `HALT` exists, no new trades are allowed.
   - If `HALT_DAILY_LOSS` exists and is dated today, execution is blocked.
   - If `HALT_DAILY_LOSS` exists but is from a previous day, only a warning is printed (not a refusal).
   - If `HALT_DAILY_LOSS` cannot be parsed as JSON, it is treated as blocking (fail closed) rather than ignored.

5. **Fail-Closed Behavior:** Any failure after an order has been placed now triggers a fail-closed mechanism that ensures the position is flattened and halted, regardless of whether the HALT file was present at the start or not.

These changes ensure more robust and predictable behavior when HALT files are involved, especially in concurrent or race-condition scenarios.
