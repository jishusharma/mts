# FT-1 RUNBOOK: Close Gaps G1 & G2 on Deribit TESTNET

## Revision 2026-09-28

Fixes applied after operator's session-5 handoff review. No section renumbered; changed content marked inline.

1. **Precondition "git working tree clean" (§0, §Step 1 x2, §1) — was unsatisfiable.** The repo tree has many unrelated untracked/modified files (research docs, harness scratch, logs) at all times; `git status` will never show "nothing to commit, working tree clean". Rescoped to: no uncommitted changes to the **specific files/dirs being promoted** in that phase (see the scoped `git status --porcelain --` commands below).
2. **Rollback (§4) — removed all destructive git lines.** `git reset --soft HEAD~2` is removed. Rollback is now file-backup restore only (`.backup` copies via `Move-Item -Force`), which is always safe and never rewrites history the operator didn't ask for.
3. **Staleness check (2026-09-28):** ran `git log -8 --oneline` and `ls` for `.new` files. Commits `73eb101` (B1+C1), `d90c297` (Batch A: D3+D4), `329e05b` (Batch C) have landed since this runbook was written, but **none touch any file this runbook promotes** (they're core-engine/proof-ladder work — `verdict.py`, `MarketDataSnapshot.java`, `SetupCandidatesBuilder.java`, `compiled_engine.md`). All `.new` files this runbook lists are still present; the promotion table is unchanged.
   - **New finding, not in the original runbook:** `execution/deribit_orders.py`, `execution/executor.py`, `execution/plan_compiler.py`, and `execution/reconciler.py` already exist as **untracked** real (non-`.new`) files (dated 2026-09-26, older than their `.new` counterparts) — i.e. an earlier, off-runbook copy already happened for 4 of the 7 production targets, without a git commit. `execution/position_manager.py` has no such copy yet. Step 2's `Copy-Item X X.backup` in both phases already handles this safely (it backs up whatever is currently there before promoting), but the operator should not be surprised that `git status` shows these as new/untracked before Step 6 — that's expected, not a sign anything went wrong.
4. **Java stale-bytecode lesson added** (§0): after any `.new` rename of a **Java** file, run `mvn clean test`, not just `mvn test` — stale `.class` files from a previous build can mask that the rename actually took effect. (No `.java` file is promoted by *this* runbook today, but the note is added here since this is the file operators check before any promotion.)
5. **G-h fix gate added** (§Session-3 Deploy Steps, new Step 0): `execution/deribit_orders.py.new` must contain the G-h fix (`OrderStateUnknown` raised instead of auto-retrying order-creating calls on an ambiguous error code) before promotion. Applied 2026-09-28 — see `MyTradingSys/execution/deribit_orders.py.new` v3 header and `execution/test_gh_retry_offline.py`.

---

**Date:** 2026-09-27
**Fast Track:** FT-1
**Goal:** Deploy session-3 + Batch B + run G1/G2 testnet suite; verify stop-shrink (G1) and reconciler forced-mismatch (G2)
**Sources:**
- MyTradingSys/research/core_readiness_2026-09-27/SESSION_3_HANDOFF.md
- MyTradingSys/research/core_readiness_2026-09-27/SESSION_4_HANDOFF.md
- MyTradingSys/execution/testnet/run_testnet_suite_g1g2.py.new

---

## 0. PRECONDITIONS

### Environment Variables / Config (Names Only)
- **DERIBIT_TESTNET_SECRET:** Location `MyTradingSys/execution/.secrets/testnet.secret.json` (file, not env var)
  - Must contain: `{"client_id": "...", "client_secret": "...", "env": "test"}`
  - **MUST NOT be readable by AI** — operator provides it once, not via session
- **TESTNET_BASE_URL:** Hardcoded to `https://test.deribit.com/api/v2` (not configurable)
- **INSTRUMENT:** Hardcoded to `"BTC-PERPETUAL"` (not configurable)

### Python & System
- **Python version:** 3.10+ (tested on 3.10.12)
- **PowerShell:** 7.x (Windows PowerShell 7 required for commands below; PS 5.1 not sufficient for UTF-8 handling in session close)
  - **Source:** MyTradingSys/research/core_readiness_2026-09-27/nuc_ps7_validation_gap.md
- **Working directory:** `$HOME/mnt/BinanceDataFeed` (or repo root)
- **Git:** No uncommitted changes to the **deploy target files** before any `.new` → real rename (the repo tree as a whole is never clean — see scoped check in each phase's Step 1; do not use plain `git status`)
- **Java rename lesson:** after any `.new` → real rename of a **Java** file elsewhere in the repo, run `mvn clean test` (not plain `mvn test`) — stale `.class` files from a prior build can hide that the rename didn't take effect.

### Testnet Account Status
- **Deribit testnet equity:** 100 BTC (per session 3 handoff)
- **Key scope:** READ ONLY, NO WITHDRAW (testnet safety requirement)
- **Start state:** Flat (0 open orders, 0 position), clean for every suite case

---

## PHASE 1: SESSION-3 BATCH (Prerequisite)

**What it does:** Deploy core executor v2, deribit_orders v2, plan_compiler v2 + testnet suite base (C1-C6 cases).
These are REQUIRED before Batch B can run (run_testnet_suite_g1g2.py runs C1-C6 first as proof).

**Source:** MyTradingSys/research/core_readiness_2026-09-27/SESSION_3_HANDOFF.md § 1, § 5

### Files to Deploy (Session-3)
| Staged File | Target | Rename Command |
|---|---|---|
| `execution/deribit_orders.py.new` | `execution/deribit_orders.py` | `mv execution/deribit_orders.py.new execution/deribit_orders.py` |
| `execution/executor.py.new` | `execution/executor.py` | `mv execution/executor.py.new execution/executor.py` |
| `execution/plan_compiler.py.new` | `execution/plan_compiler.py` | `mv execution/plan_compiler.py.new execution/plan_compiler.py` |
| `execution/testnet/run_testnet_suite.py.new` | `execution/testnet/run_testnet_suite.py` | `mv execution/testnet/run_testnet_suite.py.new execution/testnet/run_testnet_suite.py` |
| `backtest/fetch_binance_archive.py.new` | `backtest/fetch_binance_archive.py` | `mv backtest/fetch_binance_archive.py.new backtest/fetch_binance_archive.py` |

**Key constraint:** "Rename all three execution files together" — they have interdependencies (executor v2 imports the v2 names).

### Session-3 Deploy Steps (Windows PowerShell 7)

```powershell
# Step 0: Gate — deribit_orders.py.new MUST include the G-h fix (OrderStateUnknown
# raised instead of auto-retrying order-creating calls on an ambiguous error code)
# before it is promoted. Confirm, don't assume:
Select-String -Path execution/deribit_orders.py.new -Pattern "class OrderStateUnknown"
# EXPECT: a match. If none, STOP — do not promote; the G-h duplicate-order bug is unfixed.

# Step 1: Check git status for the files THIS PHASE promotes only.
# (Plain `git status` is never clean on this repo - untracked research docs,
# harness scratch, logs, etc. are always present. Scope to the targets.)
cd MyTradingSys
git status --porcelain -- execution/deribit_orders.py execution/executor.py execution/plan_compiler.py execution/testnet/run_testnet_suite.py backtest/fetch_binance_archive.py
# EXPECT: every line starts with "??" (untracked - expected; some of these
# already exist untracked from an earlier off-runbook copy, see Revision note)
# or nothing at all. A line starting with " M" means a TRACKED target file has
# uncommitted edits that promotion would silently overwrite - STOP and ask the
# operator before proceeding.

# Step 2: Backup current production files (before rename)
if (Test-Path execution/deribit_orders.py) { Copy-Item execution/deribit_orders.py execution/deribit_orders.py.backup }
if (Test-Path execution/executor.py) { Copy-Item execution/executor.py execution/executor.py.backup }
if (Test-Path execution/plan_compiler.py) { Copy-Item execution/plan_compiler.py execution/plan_compiler.py.backup }
if (Test-Path execution/testnet/run_testnet_suite.py) { Copy-Item execution/testnet/run_testnet_suite.py execution/testnet/run_testnet_suite.py.backup }
if (Test-Path backtest/fetch_binance_archive.py) { Copy-Item backtest/fetch_binance_archive.py backtest/fetch_binance_archive.py.backup }
Write-Host "Backups created with .backup suffix"

# Step 3: Diff each file (review changes)
diff -Path execution/deribit_orders.py -DifferenceObject (Get-Content execution/deribit_orders.py.new) | head -50
diff -Path execution/executor.py -DifferenceObject (Get-Content execution/executor.py.new) | head -50
diff -Path execution/plan_compiler.py -DifferenceObject (Get-Content execution/plan_compiler.py.new) | head -50

# Step 4: Promote (rename) all 5 files
Move-Item execution/deribit_orders.py.new execution/deribit_orders.py -Force
Move-Item execution/executor.py.new execution/executor.py -Force
Move-Item execution/plan_compiler.py.new execution/plan_compiler.py -Force
Move-Item execution/testnet/run_testnet_suite.py.new execution/testnet/run_testnet_suite.py -Force
Move-Item backtest/fetch_binance_archive.py.new backtest/fetch_binance_archive.py -Force
Write-Host "Session-3 files promoted"

# Step 5: Verify files exist
Get-Item execution/deribit_orders.py, execution/executor.py, execution/plan_compiler.py, execution/testnet/run_testnet_suite.py, backtest/fetch_binance_archive.py
# EXPECT: All 5 files exist and are readable

# Step 6: Git add and commit
git add execution/deribit_orders.py execution/executor.py execution/plan_compiler.py execution/testnet/run_testnet_suite.py backtest/fetch_binance_archive.py
git commit -m "S3: deploy executor v2, deribit_orders v2, plan_compiler v2, testnet base suite (C1-C6)"
# EXPECT: "5 files changed"
```

### Session-3 Verification: Run Base Suite (C1-C6)

```powershell
# TESTNET ONLY (requires .secrets/testnet.secret.json with Deribit testnet creds)
python MyTradingSys/execution/testnet/run_testnet_suite.py

# EXPECT OUTPUT:
# PASS C1 market long: ... (pos 100; stop_market 100 below fill; targets 50+50)
# PASS C2 market short: ... (pos -100; buy stop above fill)
# PASS C3 4-rung ladder: ... (pos 10 = stop 10; rungs 2-4 cancelled)
# PASS C4 preflight refusals: ... (all refused, nothing placed)
# PASS C5 forced stop fail: ... (flattened, halted, pos 0)
# PASS C6 same plan_id re-run: ... (refused - idempotency)
#
# 6/6 PASS
```

**Action if FAIL:** Run rollback (section 6) and investigate executor.py or deribit_orders.py.

---

## PHASE 2: BATCH B (Execution + G1/G2 Gap Closure)

**What it does:** Deploy position_manager v2, reconciler v2 + G1/G2 testnet suite (G1a/G1b/G2a cases).

**Source:** MyTradingSys/research/core_readiness_2026-09-27/SESSION_4_HANDOFF.md § 1

### Files to Deploy (Batch B)
| Staged File | Target | Rename Command |
|---|---|---|
| `execution/position_manager.py.new` | `execution/position_manager.py` | `mv execution/position_manager.py.new execution/position_manager.py` |
| `execution/reconciler.py.new` | `execution/reconciler.py` | `mv execution/reconciler.py.new execution/reconciler.py` |
| `execution/testnet/run_testnet_suite_g1g2.py.new` | `execution/testnet/run_testnet_suite_g1g2.py` | `mv execution/testnet/run_testnet_suite_g1g2.py.new execution/testnet/run_testnet_suite_g1g2.py` |
| `execution/testnet/offline/test_g1g2_offline.py.new` | `execution/testnet/offline/test_g1g2_offline.py` | `mv execution/testnet/offline/test_g1g2_offline.py.new execution/testnet/offline/test_g1g2_offline.py` |
| `execution/testnet/offline/fake_deribit_orders.py.new` | `execution/testnet/offline/fake_deribit_orders.py` | `mv execution/testnet/offline/fake_deribit_orders.py.new execution/testnet/offline/fake_deribit_orders.py` |

### Batch B Deploy Steps (Windows PowerShell 7)

```powershell
# Step 1: Check git status for the files THIS PHASE promotes only (see Session-3
# Step 1 note - plain `git status` is never clean on this repo).
cd MyTradingSys
git status --porcelain -- execution/position_manager.py execution/reconciler.py execution/testnet/run_testnet_suite_g1g2.py execution/testnet/offline/test_g1g2_offline.py execution/testnet/offline/fake_deribit_orders.py
# EXPECT: every line starts with "??" (untracked) or nothing at all.
# execution/reconciler.py already exists untracked from an earlier off-runbook
# copy (see Revision note) - that's expected. A line starting with " M" means a
# TRACKED target file has uncommitted edits promotion would overwrite - STOP.

# Step 2: Backup current production files (before rename)
if (Test-Path execution/position_manager.py) { Copy-Item execution/position_manager.py execution/position_manager.py.backup }
if (Test-Path execution/reconciler.py) { Copy-Item execution/reconciler.py execution/reconciler.py.backup }
if (Test-Path execution/testnet/offline/test_g1g2_offline.py) { Copy-Item execution/testnet/offline/test_g1g2_offline.py execution/testnet/offline/test_g1g2_offline.py.backup }
if (Test-Path execution/testnet/offline/fake_deribit_orders.py) { Copy-Item execution/testnet/offline/fake_deribit_orders.py execution/testnet/offline/fake_deribit_orders.py.backup }
Write-Host "Backups created with .backup suffix"

# Step 3: Diff each file (review changes)
# NOTE: deribit_orders.py, executor.py, plan_compiler.py are unchanged (already deployed in S3)
diff -Path execution/position_manager.py -DifferenceObject (Get-Content execution/position_manager.py.new) | head -100
diff -Path execution/reconciler.py -DifferenceObject (Get-Content execution/reconciler.py.new) | head -100

# Step 4: Promote (rename) all Batch B files
Move-Item execution/position_manager.py.new execution/position_manager.py -Force
Move-Item execution/reconciler.py.new execution/reconciler.py -Force
Move-Item execution/testnet/run_testnet_suite_g1g2.py.new execution/testnet/run_testnet_suite_g1g2.py -Force
Move-Item execution/testnet/offline/test_g1g2_offline.py.new execution/testnet/offline/test_g1g2_offline.py -Force
Move-Item execution/testnet/offline/fake_deribit_orders.py.new execution/testnet/offline/fake_deribit_orders.py -Force
Write-Host "Batch B files promoted"

# Step 5: Verify files exist
Get-Item execution/position_manager.py, execution/reconciler.py, execution/testnet/run_testnet_suite_g1g2.py, execution/testnet/offline/test_g1g2_offline.py, execution/testnet/offline/fake_deribit_orders.py
# EXPECT: All 5 files exist and are readable

# Step 6: Git add and commit
git add execution/position_manager.py execution/reconciler.py execution/testnet/run_testnet_suite_g1g2.py execution/testnet/offline/test_g1g2_offline.py execution/testnet/offline/fake_deribit_orders.py
git commit -m "B: deploy position_manager v2, reconciler v2, G1/G2 testnet suite"
# EXPECT: "5 files changed"
```

### Batch B Verification: Run Full G1/G2 Suite (C1-C6 + G1a/G1b/G2a)

```powershell
# TESTNET ONLY (requires .secrets/testnet.secret.json with Deribit testnet creds)
python MyTradingSys/execution/testnet/run_testnet_suite_g1g2.py

# WHAT IT DOES:
# 1. Runs run_testnet_suite.py (C1-C6 base proof)
# 2. If all pass, runs G1/G2 cases:
#    - G1a: Stop shrinks when target fills (position 100, target 50, stop must shrink to 50)
#    - G1b: Reduce-only oversize never reverses (position 10, sell 20 reduce-only → must not go short)
#    - G2a: Forced mismatch detection (close position externally → reconciler detects + halts)

# EXPECT OUTPUT:
# (C1-C6 first: 6/6 PASS)
# PASS G1a stop shrinks on target fill :: {...details...}
# PASS G1b reduce-only oversize never reverses :: {...details...}
# PASS G2a forced mismatch -> halt :: {...details...}
#
# G1/G2: 3/3 PASS
```

**Action if FAIL:** 
- Review the FAIL line (which test, what assertion)
- Run rollback (section 6)
- Investigate reconciler.py or position_manager.py logic

---

## 1. PRECONDITIONS (Checklist)

Before running either suite:

- [ ] No uncommitted changes to the deploy target files for the phase being run (`git status --porcelain -- <target files>`, see scoped command in each phase's Step 1 — NOT plain `git status`, which is never clean on this repo)
- [ ] Deribit testnet secret exists at `MyTradingSys/execution/.secrets/testnet.secret.json`
  - [ ] Contains `{"client_id": "...", "client_secret": "...", "env": "test"}`
  - [ ] Key has **READ ONLY** scope (no `wallet:write` / withdraw)
- [ ] Python 3.10+ is installed and in PATH
- [ ] Windows PowerShell 7 is in use (for UTF-8 and command compatibility)
- [ ] Internet connectivity to `https://test.deribit.com/api/v2` (testnet base URL)
- [ ] No running MTS loop or other background processes on this account

---

## 2. EXACT COMMANDS

### SESSION-3 BATCH: Base Suite Proof (C1-C6)

**File:** `MyTradingSys/execution/testnet/run_testnet_suite.py`
**Command:**
```powershell
python MyTradingSys/execution/testnet/run_testnet_suite.py
```

**Expected runtime:** ~1-2 minutes (self-cleans account after each case)
**Expected output:** `6/6 PASS` with per-case details

---

### BATCH B: Full G1/G2 Proof (C1-C6 + G1a/G1b/G2a)

**File:** `MyTradingSys/execution/testnet/run_testnet_suite_g1g2.py.new` → `run_testnet_suite_g1g2.py`
**Command:**
```powershell
python MyTradingSys/execution/testnet/run_testnet_suite_g1g2.py
```

**Expected runtime:** ~3-5 minutes (runs base suite first, then 3 G1/G2 cases)
**Expected output:** `6/6 PASS` (C1-C6) then `G1/G2: 3/3 PASS` (G1a/G1b/G2a)

**What each test validates:**
- **G1a (stop shrinks):** When target order fills (partial position reduction), stop must shrink to remaining size
  - Setup: position 100 BTC, targets 50+50, stop 2% below
  - Action: Target 1 (50 BTC) fills
  - Check: Stop must now be 50 BTC (not 100), stop_amount = 50
  - Status: PASS if reconcile result is "reconciled_ok"
  
- **G1b (reduce-only oversize):** Reduce-only order larger than position must not cause reverse (short)
  - Setup: position 10 BTC
  - Action: Issue reduce-only market sell 20 BTC
  - Check: Position must stay >= 0 (clamped or rejected by Deribit)
  - Status: PASS if pos_after >= 0
  
- **G2a (forced mismatch):** Reconciler detects externally-closed position
  - Setup: open position + plan running
  - Action: Close position manually (via UI / external call)
  - Check: reconciler.reconcile() raises ReconciliationMismatch with "position_size_mismatch" + journal is halted
  - Status: PASS if reconciler detects AND journal halted=true

---

## 3. OUTPUT & REPORTING

### Where Output Lands
- **Console:** Print output from Python (`sys.stdout`)
- **Files:** No log files auto-created; output is ephemeral from the test run
- **Journals:** Test cleans up journals after each case (self-healing)

### What to Capture & Send Back to Coordinator

**Minimal required:**
1. Final line showing pass/fail count: `G1/G2: X/3 PASS`
2. If any FAIL, the FAIL line with test name and error details
3. Console output from start to end (paste it all if ≤ 200 lines; if >200, paste first 50 + last 50 + all FAILs)

**Optional but helpful:**
- Full console output of any FAIL case (error traceback)
- Deribit testnet UI screenshot showing account state (pos/orders/funding) before and after run
- Timestamp of run completion

**Example send-back format:**
```
FT-1 G1/G2 TESTNET RUN COMPLETE
=============================
Status: 3/3 PASS (G1a, G1b, G2a)
Timestamp: 2026-09-27T15:10:00Z
Testnet account: FLAT (0 pos, 0 orders) after cleanup

Full output:
[paste console output here]
```

---

## 4. ROLLBACK COMMANDS

**If any step fails, restore from backups:**

```powershell
# Rollback Session-3 batch
if (Test-Path execution/deribit_orders.py.backup) { Move-Item execution/deribit_orders.py.backup execution/deribit_orders.py -Force }
if (Test-Path execution/executor.py.backup) { Move-Item execution/executor.py.backup execution/executor.py -Force }
if (Test-Path execution/plan_compiler.py.backup) { Move-Item execution/plan_compiler.py.backup execution/plan_compiler.py -Force }
if (Test-Path execution/testnet/run_testnet_suite.py.backup) { Move-Item execution/testnet/run_testnet_suite.py.backup execution/testnet/run_testnet_suite.py -Force }
if (Test-Path backtest/fetch_binance_archive.py.backup) { Move-Item backtest/fetch_binance_archive.py.backup backtest/fetch_binance_archive.py -Force }
Write-Host "Session-3 rolled back"

# Rollback Batch B
if (Test-Path execution/position_manager.py.backup) { Move-Item execution/position_manager.py.backup execution/position_manager.py -Force }
if (Test-Path execution/reconciler.py.backup) { Move-Item execution/reconciler.py.backup execution/reconciler.py -Force }
if (Test-Path execution/testnet/offline/test_g1g2_offline.py.backup) { Move-Item execution/testnet/offline/test_g1g2_offline.py.backup execution/testnet/offline/test_g1g2_offline.py -Force }
if (Test-Path execution/testnet/offline/fake_deribit_orders.py.backup) { Move-Item execution/testnet/offline/fake_deribit_orders.py.backup execution/testnet/offline/fake_deribit_orders.py -Force }
Write-Host "Batch B rolled back"
```

**Rollback is file-restore only.** No `git reset`, `git checkout`, or any other history-rewriting command is part of this rollback — those are destructive and out of scope for an automated runbook. If the operator separately decides a git commit needs to be undone, that is their call to make and run by hand, not something this rollback performs.

---

## 5. NOT FOUND IN REPO

**Items requested but not found in indexed docs/code:**
- NOT FOUND: Exact PowerShell 7 version requirement (guidance says "PS 7.x" but no version pin)
- NOT FOUND: Testnet data migration / snapshot restoration procedure between test runs (assumes fresh account)
- NOT FOUND: G1b expected outcome (Deribit clamps vs rejects oversized reduce-only) — run discovers behavior
- NOT FOUND: Formal test log output format (Python unittest vs custom print; suite uses custom print)

**Items inferred from code and docs but not explicitly stated:**
- deribit_orders.py.new requires deribit_orders.py NOT to exist OR be safely replaced (no side-by-side versioning)
- reconciler.py v2 comment: "reconcile()" call expects journal.reconstruct_belief() to have halted=true on mismatch
- run_testnet_suite_g1g2.py.new calls S.clean() between cases (clean = cancel all + close position); relies on session-3 execution batch being live

---

## 6. SUMMARY

**FT-1 path:** Session-3 deploy (5 files, C1-C6 proof) → Batch B deploy (5 files, G1/G2 proof) → Commit → Done

**Success criteria:**
- Session-3 suite: `6/6 PASS`
- Batch B suite: `6/6 PASS` (C1-C6) + `3/3 PASS` (G1a/G1b/G2a) = `9/9 PASS` total
- All output console lines captured and sent back
- Git commits recorded with appropriate messages

**Time budget:** ~10 minutes total (2 min per suite run + deploy time)

