"""Unified offline test runner - runs all test suites.

Usage:
  python scripts/dev/run_all_tests.py         (run all steps)
  python scripts/dev/run_all_tests.py --quick (skip mvn and backtest)

Steps that share no state run concurrently in MTS_GATE_JOBS worker threads (default min(4, cpu count); MTS_GATE_JOBS=1 runs
one step at a time in definition order, the old behaviour). SERIAL_STEPS (they scan or write checkout state) and Maven run one
at a time after the pool. Each step prints its block when it finishes, line-buffered, with its own time and a progress count, so
a redirected or backgrounded run shows progress; the SUMMARY lists every step in definition order. A foreground tool call dies
at 600 s: start the gate (and `sync.py ship`, which calls it) in the background and read the output once.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Function-style pytest tests that step 5b (unittest) collects only partly: Fabio v3 + live writers (TF1, E7).
PYTEST_LAYER_PATHS = [
    "MyTradingSys/backtest/layers/fabio/v3/tests",
    "MyTradingSys/backtest/layers/fabio/test_orderflow_live.py",
    "MyTradingSys/backtest/layers/fabio/test_of_backfill.py",
    "MyTradingSys/backtest/layers/fabio/test_htf_context_live.py",
    "MyTradingSys/execution/tests",
    "scripts/dev/test_market_guide.py",
    "scripts/dev/test_dax_engine_flag.py",
    "scripts/dev/test_check_handoff.py",
    "MyTradingSys/observation/tests",
]

# These steps scan or write checkout state (layer index, artifact registry, wiring --check, STATUS generator, group map), and
# Step 4's tests drop fixtures in the tree, so they never run beside the pool. Maven (step 5) is serial as well.
SERIAL_STEPS = ("3ly", "3af", "3x", "3ms", "3mg", "5")
# Submitted first so the pool's last step is not the slowest one (measured: 4, 3xt, 5b, 3k, 3ds, 3dk, 3bk, 3w).
SLOWEST_FIRST = ("4", "3xt", "5b", "3k", "3ds", "3dk", "3bk", "3w")
_LOCK = threading.Lock()


def unbuffer(stream=None):
    """Line-buffer stdout so a redirected or backgrounded run shows each step as it finishes (block buffering printed nothing
    until the end and a run killed at the tool cap left an empty file). errors=replace: a failing step's tail with a character the
    console code page cannot encode must not crash the gate."""
    stream = stream or sys.stdout
    try:
        stream.reconfigure(line_buffering=True, errors="replace")
    except (AttributeError, ValueError):
        pass
    return stream


def exec_step(cmd, cwd=None):
    """Run one command to completion. Returns (ok, output): ok is True/False, or None with a reason when the executable is missing."""
    try:
        result = subprocess.run(cmd, cwd=cwd or str(REPO), capture_output=True, text=True, errors="replace",
                                shell=isinstance(cmd, str))
    except FileNotFoundError as e:
        return None, f"not found: {e}"
    return result.returncode == 0, result.stdout + result.stderr


def format_step(num, description, cmd_text, ok, output, elapsed, progress="", tail=15):
    """The block one finished step prints. tail = how many output lines a failure shows (None = all; CI always shows all)."""
    lines = [f"\n[Step {num}] {description}", f"  Command: {cmd_text}"]
    if ok is None:
        lines.append(f"Step {num}: SKIP ({output})")
        return lines
    lines.append(f"  Elapsed: {elapsed:.1f}s" + (f" ({progress})" if progress else ""))
    lines.append(f"Step {num}: {'PASS' if ok else 'FAIL'}")
    out = output.splitlines()
    if not ok and out:
        lines.append("  Last output:")
        lines += [f"    {ln}" for ln in (out if (os.environ.get("CI") or tail is None) else out[-tail:])]
    elif ok:
        lines += [f"  {ln}" for ln in out if ln.startswith("WARN")][:5]   # a passing step can still warn (wiring NO-READER)
    return lines


def run_step(step_num, description, cmd, cwd=None):
    """Run one step now and print its block. Return (True|False|None, output); None means skipped."""
    t0 = time.monotonic()
    ok, output = exec_step(cmd, cwd)
    block = format_step(step_num, description, " ".join(cmd) if isinstance(cmd, list) else cmd, ok, output, time.monotonic() - t0)
    with _LOCK:
        print("\n".join(block), flush=True)
    return ok, output


def find_backtest_modules():
    """Find all test_*.py modules (including .new) in MyTradingSys/backtest/bt."""
    bt_dir = REPO / "MyTradingSys" / "backtest" / "bt"
    if not bt_dir.exists():
        return []
    modules = set()
    for py_file in bt_dir.glob("test_*.py"):
        modules.add(py_file.stem)
    for py_new_file in bt_dir.glob("test_*.py.new"):
        # For test_xxx.py.new, the stem is test_xxx.py, we want test_xxx
        stem = py_new_file.stem  # e.g., "test_bt_data.py"
        if stem.endswith(".py"):
            stem = stem[:-3]  # remove .py
        modules.add(stem)
    return sorted(modules)


def find_layer_modules():
    """Dotted names of committed test_*.py modules under MyTradingSys/backtest/layers (fast, run in --quick too)."""
    layers = REPO / "MyTradingSys" / "backtest" / "layers"
    if not layers.exists():
        return []
    return sorted(".".join(f.relative_to(REPO).with_suffix("").parts) for f in layers.rglob("test_*.py"))


def gate_jobs():
    """Concurrent workers: MTS_GATE_JOBS, default min(4, cpu count); 1 = one step at a time (the old single call)."""
    try:
        n = int(os.environ.get("MTS_GATE_JOBS", ""))
    except ValueError:
        n = min(4, os.cpu_count() or 1)
    return max(1, n)


def split_modules(modules, jobs):
    """Round-robin the module list into at most `jobs` non-empty chunks; their union is exactly `modules`."""
    jobs = max(1, min(jobs, len(modules))) if modules else 1
    return [c for c in (modules[i::jobs] for i in range(jobs)) if c]


def exec_layer_chunks(modules, jobs):
    """Run every layer module in `jobs` concurrent unittest processes. Returns (ok, output); fails if any chunk fails, and then
    the output is the last lines of each failing chunk."""
    chunks = split_modules(modules, jobs)
    procs = [subprocess.Popen([sys.executable, "-m", "unittest"] + c, cwd=str(REPO), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, errors="replace") for c in chunks]
    outs = [p.communicate()[0] for p in procs]
    ok = all(p.returncode == 0 for p in procs)
    if ok:
        return True, "\n".join(outs)
    keep = [o if os.environ.get("CI") else "\n".join(o.splitlines()[-15:]) for p, o in zip(procs, outs) if p.returncode != 0]
    return False, "\n".join(keep)


def isolate_pytest_tmp():
    """Give every pytest child of this gate its own fresh temp root (inherited via env). A stale pytest-of-<user>/pytest-current link in
    %TEMP% that cannot be unlinked (WinError 5, seen 2026-10-11 after the ESET removal reboot) makes pytest exit 1 even when every test passes,
    which turned the deploy gate red. Returns the path."""
    import tempfile
    root = os.environ.get("PYTEST_DEBUG_TEMPROOT") or tempfile.mkdtemp(prefix="mts_pytest_")
    os.environ["PYTEST_DEBUG_TEMPROOT"] = root
    return root


class Step:
    """One gate step. cmd is an argv list (or a string), or run is a zero-argument callable returning (ok, output); skip = reason
    it does not run. lane 'seq' steps run one at a time after the concurrent pool."""

    def __init__(self, num, desc, label, cmd=None, run=None, cmd_text=None, skip=None, tail=15):
        self.num, self.desc, self.label, self.skip, self.tail = str(num), desc, label, skip, tail
        self.cmd_text = cmd_text or (" ".join(cmd) if isinstance(cmd, list) else str(cmd))
        self.run = run or (lambda: exec_step(cmd))
        self.lane = "seq" if self.num in SERIAL_STEPS else "par"


def run_mvn():
    """Maven, or (None, reason) when mvn is not installed."""
    mvn = shutil.which("mvn") or shutil.which("mvn.cmd") or "mvn"  # Windows: mvn.cmd
    try:
        if subprocess.run([mvn, "--version"], capture_output=True, text=True).returncode != 0:
            return None, "mvn not found"
    except FileNotFoundError:
        return None, "mvn not found"
    return exec_step([mvn, "-q", "test"])


def build_plan(quick):
    """Every step in report order. One step per line: parallel sessions append here (a shared line is a guaranteed conflict)."""
    plan = []

    def add(num, desc, cmd, label):
        plan.append(Step(num, desc, label, cmd=cmd))

    # Step 1: execution tests
    cmd1 = [
        sys.executable, "scripts/dev/run_staged_tests.py",
        "MyTradingSys/execution", "MyTradingSys/execution/testnet/offline",
        "--",
        "test_daily_loss_guard", "test_daily_loss_monitor", "test_mainnet_flag_offline", "test_gh_executor_offline",
        "test_gh_retry_offline", "test_halt_preflight_offline", "test_kill_switch", "test_kill_switch_account", "test_premainnet1_offline",
        "test_risk_guard", "test_s1_cap_offline", "test_s3_unprotected_offline",
        "test_s6_orphan_offline", "test_triggered_stop_offline", "test_soak_report", "test_fix3_offline", "test_fix4_offline",
        "test_plan_compiler", "test_executor_math", "test_auto_trader", "test_dlm_aggregate", "test_b148_reauth_account", "test_b146_fee_to_stop", "test_dlm_failure_cap", "test_auto_trader_blocklist", "test_auto_trader_sizes", "test_auto_trader_confirm", "test_orphan_sweep_loop", "test_fabio_slot", "test_fix3_mutants_offline", "test_capture_txlog_settlement", "test_mts_kill_mainnet", "test_pm_heartbeat", "test_pm_heartbeat_wiring", "test_journal_env", "test_mainnet_plan_check", "test_env_wiring", "test_reconciler_env", "test_deribit_read_account", "test_orphan_watchdog", "test_orphan_watchdog_cli", "test_mainnet_pnl", "test_daily_pnl_wiring", "test_xferfix", "test_time_exit_offline", "test_trade_ledger", "test_netretry", "test_r2_runner_exit", "test_r2_breakeven_move",  # W2 R2: execution-math tests (FORMULAS.md 11)
    ]
    add(1, "Execution module tests", cmd1, "Step 1: Execution tests")

    # Step 2: g1g2 offline script test
    cmd2 = [
        sys.executable, "scripts/dev/run_staged_tests.py",
        "MyTradingSys/execution", "MyTradingSys/execution/testnet/offline",
        "--script", "test_g1g2_offline.py",
        "--fake", "fake_deribit_orders.py=deribit_orders.py",
    ]
    add(2, "G1G2 offline script test", cmd2, "Step 2: G1G2 offline test")

    # Step 3: static suite test, then the small script-level steps (one per line)
    add(3, "Static test suite", [sys.executable, "MyTradingSys/execution/testnet/test_suite_static.py"], "Step 3: Static test suite")
    add("3b", "User guide checker tests", [sys.executable, "scripts/dev/test_check_guide.py"], "Step 3b: Guide checker tests")
    add("3c", "User guide in sync with mts.ps1", [sys.executable, "scripts/dev/check_guide.py"], "Step 3c: Guide in sync")
    add("3r", "Alert rate checker tests", [sys.executable, "scripts/dev/test_alert_rate_check.py"], "Step 3r: Alert rate checker tests")
    add("3s", "Testnet status summary tests", [sys.executable, "scripts/dev/test_testnet_status.py"], "Step 3s: Testnet status tests")
    add("3f", "Funnel report tests", [sys.executable, "scripts/dev/test_funnel_report.py"], "Step 3f: Funnel report tests")
    add("3dk", "Desk board tests", [sys.executable, "scripts/dev/test_desk.py"], "Step 3dk: Desk board tests")
    add("3tk", "Task card tests", [sys.executable, "scripts/dev/test_tasks.py"], "Step 3tk: Task card tests")
    add("3td", "Tom ledger date tests", [sys.executable, "scripts/dev/test_tom_ledger_dates.py"], "Step 3td: Tom ledger date tests")   # Tom ledger date column: observed or empty (RV01 D4)
    add("3hs", "Tom holdout split tests", [sys.executable, "scripts/dev/test_tom_holdout_split.py"], "Step 3hs: Tom holdout split tests")   # Tom holdout clean split, dates only
    add("3sq", "Spec quote checker tests", [sys.executable, "scripts/dev/test_check_spec_quotes.py"], "Step 3sq: Spec quote checker tests")   # spec quotes verbatim in the cited transcript lines
    add("3ly", "Layer index tests", [sys.executable, "scripts/dev/test_make_layers_md.py"], "Step 3ly: Layer index tests")   # LAYERS.md: no dead pointer, every layer owned
    add("3cx", "Layer lab runner tests", [sys.executable, "scripts/dev/test_codex_run.py"], "Step 3cx: Layer lab runner tests")
    add("3tl", "Task cards meet the Definition of Ready", [sys.executable, "scripts/dev/tasks.py", "lint"], "Step 3tl: Task card lint")   # a ready/active card that fails the Definition of Ready is an error
    add("3q", "INDEX/BUGS consistency", [sys.executable, "scripts/dev/test_registry_consistency.py"], "Step 3q: INDEX/BUGS consistency")
    add("3p", "P4 corrected script tests", [sys.executable, "MyTradingSys/research/test_p4_corrected.py"], "Step 3p: P4 corrected script tests")
    add("3t", "T093 turn-of-candle imbalance tests", [sys.executable, "MyTradingSys/research/test_t093_toc_imbalance_klines.py"], "Step 3t: T093 imbalance tests")
    add("3d", "Extract quote checker tests", [sys.executable, "scripts/dev/test_verify_extract_quotes.py"], "Step 3d: Quote checker tests")
    add("3h", "Launcher verb static tests (runner, orphans)", [sys.executable, "scripts/dev/test_mts_launcher.py"], "Step 3h: Launcher static tests")
    add("3g", "Gate coverage tests (Fabio v3 + live writers)", [sys.executable, "scripts/dev/test_run_all_tests.py"], "Step 3g: Gate coverage tests")
    add("3k", "sync.py parallel ship tests", [sys.executable, "scripts/dev/test_sync.py"], "Step 3k: sync.py tests")
    add("3e", "DSA browser worker + queue lane tests", [sys.executable, "scripts/worker/test_dsa_worker.py"], "Step 3e: DSA worker tests")
    add("3sh", "Screenshot intake tests (save, classify, read, close gates)", [sys.executable, "scripts/dev/test_shot.py"], "Step 3sh: Screenshot intake tests")
    add("3mg", "Project group map tests (every row and file has one group)", [sys.executable, "scripts/dev/test_make_groups.py"], "Step 3mg: Project group map tests")
    add("3xt", "Extra tests outside the collected dirs (B150 discovery)", [sys.executable, "scripts/dev/run_extra_tests.py"], "Step 3xt: Extra tests")
    add("3ad", "Scheduled auto-deploy tests (stops on red gate)", [sys.executable, "scripts/dev/test_auto_deploy.py"], "Step 3ad: Auto-deploy tests")
    add("3hy", "Daily hygiene job tests", [sys.executable, "scripts/dev/test_daily_hygiene.py"], "Step 3hy: Daily hygiene tests")
    add("3ms", "STATUS.md generator tests (commit-dated reports, CI green line)", [sys.executable, "scripts/dev/test_make_status.py"], "Step 3ms: make_status tests")
    add("3cs", "Cloud SessionStart hook tests (no-op off cloud)", [sys.executable, "scripts/dev/test_cloud_setup.py"], "Step 3cs: Cloud setup hook tests")
    add("3pc", "Prompt contract tests (DSA_SESSION_PROMPT 5d, B155)", [sys.executable, "scripts/dev/test_prompt_contract.py"], "Step 3pc: Prompt contract tests")
    add("3ds", "DSA helper CLI tests (dsa.py)", [sys.executable, "scripts/dev/test_dsa.py"], "Step 3ds: DSA helper CLI tests")   # dsa.py: DSA one-call helpers (put/edit/commit/begin/end/host)
    add("3cr", "Control Room page generator tests", [sys.executable, "scripts/dev/test_make_control_room.py"], "Step 3cr: Control Room tests")
    add("3lh", "GPT lane health tests (down/up rules, reroute, pause, resume, DSA prompt)", [sys.executable, "scripts/dev/test_lane_health.py"], "Step 3lh: GPT lane health tests")
    add("3rb", "Claude-GPT relay board tests (shared notes, lanes, pack)", [sys.executable, "scripts/dev/test_relay_board.py"], "Step 3rb: Relay board tests")
    add("3af", "Artifact registry tests (one url per page per account)", [sys.executable, "scripts/dev/test_artifacts.py"], "Step 3af: Artifact registry tests")
    add("3bk", "Backup snapshot tests (dirty/untracked work reaches the remote)", [sys.executable, "scripts/dev/test_backup_snapshot.py"], "Step 3bk: Backup snapshot tests")
    add("3lm", "Live mirror tests (read-only desktop->work-tree data, fail-closed)", [sys.executable, "scripts/dev/test_live_mirror.py"], "Step 3lm: Live mirror tests")

    # Step 3w: wiring gate - every unrun code file is declared in wiring_registry.json or archived (fast, in --quick too)
    add("3w", "Wiring gate tests", [sys.executable, "scripts/dev/test_wiring_scan.py"], "Step 3w: Wiring gate tests")
    add("3x", "Wiring check: no undeclared unwired code (wiring_scan.py --check)", [sys.executable, "scripts/dev/wiring_scan.py", "--check"], "Step 3x: Wiring check")

    # Step 4: pytest (math + doc tests)
    cmd4 = [sys.executable, "-m", "pytest", "MyTradingSys/tests", "-q",
            # function-style tests that unittest-based steps 5b/6 do not collect
            # one entry per line: parallel sessions append here (a shared line is a guaranteed conflict)
            "MyTradingSys/backtest/test_prob_table.py",
            "MyTradingSys/backtest/test_prob_table_edge.py",
            "MyTradingSys/backtest/test_tom_bt.py",
            "MyTradingSys/backtest/test_tom_probe_diag.py",
            "MyTradingSys/backtest/test_dax_data.py",
            "MyTradingSys/backtest/test_tom_dax_recall.py",
            "MyTradingSys/backtest/test_tom_v2_recall.py",
            "MyTradingSys/backtest/test_tom_dax_bt.py",
            ] + PYTEST_LAYER_PATHS
    # Own basetemp: parallel gates share %TEMP%/pytest-of-<user>/pytest-current and its cleanup raises
    # PermissionError after all tests pass (JIS-NB 2026-10-14, six ships at once); same fix as run_extra_tests.py.
    cmd4 += ["-p", "no:cacheprovider", f"--basetemp={Path(tempfile.mkdtemp(prefix='mts_s4_')) / 'bt'}"]
    add(4, "Pytest (math + doc tests)", cmd4, "Step 4: Pytest tests")

    # Step 5: mvn test (unless --quick)
    if not quick:
        plan.append(Step(5, "Maven Java tests", "Step 5: Maven tests", run=run_mvn, cmd_text="mvn -q test"))
    else:
        plan.append(Step(5, "Maven Java tests", "Step 5: Maven tests", skip="skipped with --quick"))

    # Step 5b: indicator-layer tests (fast; run even with --quick)
    layer_modules = find_layer_modules()
    if layer_modules:
        jobs = gate_jobs()
        if jobs == 1:
            add("5b", f"Layer tests ({len(layer_modules)} modules)", [sys.executable, "-m", "unittest"] + layer_modules, "Step 5b: Layer tests")
        else:
            plan.append(Step("5b", f"Layer tests ({len(layer_modules)} modules, {jobs} parallel processes)", "Step 5b: Layer tests",
                             run=lambda: exec_layer_chunks(layer_modules, jobs), cmd_text=f"python -m unittest ({len(layer_modules)} modules)",
                             tail=None))

    # Step 5c: options module (own pytest run: its bare module names, e.g. fees.py, collide with other packages); own basetemp and
    # no cache dir because it runs beside other pytest processes
    cmd5c = [sys.executable, "-m", "pytest", "MyTradingSys/options/tests", "-q", "-p", "no:cacheprovider",
             f"--basetemp={Path(tempfile.mkdtemp(prefix='mts_s5c_')) / 'bt'}"]
    add("5c", "Options module tests", cmd5c, "Step 5c: Options tests")

    # Step 6: backtest (unless --quick)
    if quick:
        plan.append(Step(6, "Backtest tests", "Step 6: Backtest tests", skip="skipped with --quick"))
    else:
        modules = find_backtest_modules()
        if modules:
            cmd6 = [
                sys.executable, "scripts/dev/run_staged_tests.py",
                "MyTradingSys/backtest/bt",
                "--",
            ] + modules
            add(6, f"Backtest tests ({len(modules)} modules)", cmd6, "Step 6: Backtest tests")
        else:
            plan.append(Step(6, "Backtest tests", "Step 6: Backtest tests", skip="no test modules found"))
    return plan


def run_plan(plan, jobs, out=None):
    """Run the plan and print each step's block as it finishes. Independent steps run `jobs` at a time, slowest first; SERIAL_STEPS
    follow one by one; jobs == 1 runs everything in definition order. Returns {step num: True|False|None}."""
    out = out or sys.stdout
    results = {}
    skipped = [s for s in plan if s.skip]
    todo = [s for s in plan if not s.skip]
    for s in skipped:
        print(f"\n[Step {s.num}] {s.desc}\nStep {s.num}: SKIP ({s.skip})", file=out, flush=True)
        results[s.num] = None
    print(f"Gate: {len(todo)} steps, {jobs} at a time", file=out, flush=True)
    t_start = time.monotonic()
    finished = [0]

    def run_one(s):
        t0 = time.monotonic()
        try:
            ok, output = s.run()
        except Exception:   # a crashing step is a failed step, not a dead gate
            ok, output = False, traceback.format_exc()
        elapsed = time.monotonic() - t0
        with _LOCK:
            finished[0] += 1
            progress = f"{finished[0]}/{len(todo)} done, +{time.monotonic() - t_start:.0f}s"
            print("\n".join(format_step(s.num, s.desc, s.cmd_text, ok, output, elapsed, progress, s.tail)), file=out, flush=True)
        results[s.num] = ok

    if jobs <= 1:
        for s in todo:
            run_one(s)
    else:
        par = [s for s in todo if s.lane == "par"]
        par.sort(key=lambda s: SLOWEST_FIRST.index(s.num) if s.num in SLOWEST_FIRST else len(SLOWEST_FIRST))   # stable: the rest keep definition order
        with ThreadPoolExecutor(max_workers=jobs) as pool:
            list(pool.map(run_one, par))
        for s in todo:
            if s.lane == "seq":
                run_one(s)
    return results


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    unbuffer()
    isolate_pytest_tmp()
    quick = "--quick" in args

    plan = build_plan(quick)
    results = run_plan(plan, gate_jobs())

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    failed = []
    for s in plan:
        result = results.get(s.num)
        if result is True:
            print(f"{s.label}: PASS")
        elif result is False:
            print(f"{s.label}: FAIL")
            failed.append(s.label)
        else:
            print(f"{s.label}: SKIP")

    print("=" * 70)
    if failed:
        print(f"FAILED: {len(failed)} step(s)")
        for f in failed:
            print(f"  - {f}")
        return 1
    else:
        print("ALL TESTS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
