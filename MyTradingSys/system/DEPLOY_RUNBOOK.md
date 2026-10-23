# DEPLOY RUNBOOK (live tree = the folder holding `.mts_live`: JIS-NB today, DESKTOP-F7IU69N after the cutover)

> **Live host move staged 2026-10-21 (LIVE_HOST_MOVE.md).** Steps below name the live tree by its `.mts_live` marker: after the cutover read "JIS-NB" here as DESKTOP-F7IU69N (live tree `C:\MTS\mts-live`). The cutover is the one-owner checklist in LIVE_HOST_MOVE.md section 4, run by the operator or a named coordinator only; builders never run it. Deploy-specific rules: section "Live host cutover" at the end.

Per **SCHEDULING_POLICY.md** (2026-10-17), automated background tasks (`MTS-AutoDeploy`, `MTS-Supervisor`, `MTS-DailyHygiene`) are retired across all devices. The **manual deploy procedure below is the standard deployment process** for MTS.

---

## 1. Standard Manual Deploy Procedure

Operator pre-authorised "just do it" on 2026-10-09.

### Step 1: Pre-flight Verification
1. Ensure you are on the machine hosting the live tree (the folder containing `.mts_live`).
2. Verify with `sync.py where` (or `git -C <live> status --porcelain`) that there are no uncommitted edits or conflicts in the live tree. If other sessions have uncommitted edits in the live tree, do **NOT** merge or stash there.
3. Code reaches the live tree only from `origin/green/fast-track` (the SHA CI gated on Ubuntu and Windows in `.github/workflows/ci.yml`, job `mark-green`), or from a tested, reviewed tip.

### Step 2: Runtime State Protection (B152)
Before merging or checking out files, ensure untracked runtime state is preserved:
- Copy `MyTradingSys/runtime/orderflow_live/_state.json` to a temporary backup location (`runtime_data/deploy_backup/<stamp>/_state.json`).
- If a checkout or fast-forward merge removes `_state.json`, restore it from the backup copy immediately so `orderflow_live.py` does not lose historical tracking.

### Step 3: Checkout or Fast-Forward Merge
- For selective file deployments:
  ```bash
  git -C <live> checkout origin/fast-track -- <only the changed live-path files>
  ```
- For full fast-forward update to a green commit:
  ```bash
  git -C <live> merge --ff-only origin/green/fast-track
  ```
- Run unit/regression tests for the affected components before restarting processes.

---

## 2. Process Restart Map

When code changes land in the live tree, restart **only** the process that imports the modified files:

| Modified Paths | Process to Restart | Notes |
| :--- | :--- | :--- |
| `execution/auto_trader*`, `executor`, `deribit_orders` | `auto_trader.py` | `loop-supervisor` revives it in ~1 minute. |
| `daily_loss_monitor`, `mainnet_pnl`, `kill_switch`, `deribit_orders` | `daily_loss_monitor.py` | Safety & risk monitor. |
| `backtest/layers/alerts/*`, layer packages, `bt/`, `fees` | `layers.alerts.live_runner_cli` | Runs as a module (`-m`), not `.py`. |
| `position_manager.py` | **NEVER KILLED** | Guards open positions; new managers load updated code on new trades. |
| `src/main/java/*`, `pom.xml` | **Java JVM** | Requires `mvn compile` and a dedicated JVM restart window; builders never touch it. |

Builders never stop or restart any other process, touch HALT files, or interfere with active trades.

---

## 3. Deploying the "Untrack Generated Files" Commit (Coordinator Procedure)

For commits that run `git rm --cached` on generated runtime files (`AUDIT_DIGEST.md`, `T0_CHECKS.md`, `runtime/BUILD_REPORT.md`, `runtime/oi_live/*.csv`, `research/htf_context/*`):
1. `python scripts/dev/deploy_untrack_backup.py backup <live>`: Copies files to `runtime_data/deploy_backup/<stamp>/untrack/` with a SHA-256 `MANIFEST.json`.
2. `python scripts/dev/deploy_untrack_backup.py reset <live> <stamp>`: Restores committed copies of dirty files.
3. `git -C <live> merge --ff-only <target>`: Fast-forwards the live tree.
4. `python scripts/dev/deploy_untrack_backup.py restore <live> <stamp>`: Restores every missing file verified against the manifest.
5. Confirm `git -C <live> status --porcelain` is clean and `check_live_health.py` reports no missing data.

---

## 4. Quick-Gate Speed & Host Health

- Quick gate runs independent steps in parallel (`MTS_GATE_JOBS`, default `min(4, CPUs)`).
- Gate steps `3gd` (every test file gated) and `3dl` (`ci_deps_lint.py`) ensure environment consistency across machines.
- Machine backups run via local bare repo (`F:\MTS_backup.git`) with `install_backup_task.ps1 -Repo <path> --remote backup`. Snapshots are never pushed to the public origin.

---

## 5. Live Host Cutover (JIS-NB -> DESKTOP-F7IU69N)

Full checklist is maintained in **LIVE_HOST_MOVE.md** section 4 (single-owner procedure):
- Fresh clone created on the target machine at the gated green SHA (`git switch --detach <origin/green/fast-track>`).
- Exactly one `.mts_live` marker exists across all hosts: rename JIS-NB's marker to `.mts_live.retired-<date>` prior to starting live loops on the laptop.
- Untracked runtime state (`_state.json` and recorder databases) copied with SHA-256 verification via local network share.
- Post-cutover, manual deployments run on the target laptop: `git -C C:\MTS\mts-live ...`.

---

## 6. Historical AutoDeploy Archive

For historical details on the retired 15-minute scheduled AutoDeploy service (`auto_deploy.py`), CI starvation fallbacks, and zero-cost tick designs, see:
[`MyTradingSys/archive/deploy_2026-10-19/AUTODEPLOY_HISTORY.md`](../archive/deploy_2026-10-19/AUTODEPLOY_HISTORY.md).
