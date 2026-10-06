"""Unified offline test runner - runs all test suites in order.

Usage:
  python scripts/dev/run_all_tests.py         (run all steps)
  python scripts/dev/run_all_tests.py --quick (skip mvn and backtest)
"""
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Function-style pytest tests that step 5b (unittest) collects only partly: Fabio v3 + live writers (TF1, E7).
PYTEST_LAYER_PATHS = [
    "MyTradingSys/backtest/layers/fabio/v3/tests",
    "MyTradingSys/backtest/layers/fabio/test_orderflow_live.py",
    "MyTradingSys/backtest/layers/fabio/test_of_backfill.py",
    "MyTradingSys/backtest/layers/fabio/test_htf_context_live.py",
    "MyTradingSys/execution/tests",
]


def run_step(step_num, description, cmd, cwd=None):
    """Run a single test step. Return True on success, False on failure."""
    print(f"\n[Step {step_num}] {description}")
    print(f"  Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or str(REPO),
            capture_output=True,
            text=True,
            shell=isinstance(cmd, str),
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            print(f"Step {step_num}: PASS")
            return True, output
        else:
            print(f"Step {step_num}: FAIL")
            # Print last 15 lines of output on failure
            lines = output.splitlines()
            if lines:
                print("  Last output:")
                for line in lines[-15:]:
                    print(f"    {line}")
            return False, output
    except FileNotFoundError as e:
        print(f"Step {step_num}: SKIP (not found: {e})")
        return None, str(e)  # None means skip


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


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    quick = "--quick" in args

    results = []

    # Step 1: execution tests
    cmd1 = [
        sys.executable, "scripts/dev/run_staged_tests.py",
        "MyTradingSys/execution", "MyTradingSys/execution/testnet/offline",
        "--",
        "test_daily_loss_guard", "test_daily_loss_monitor", "test_mainnet_flag_offline", "test_gh_executor_offline",
        "test_gh_retry_offline", "test_halt_preflight_offline", "test_kill_switch", "test_kill_switch_account", "test_premainnet1_offline",
        "test_risk_guard", "test_s1_cap_offline", "test_s3_unprotected_offline",
        "test_s6_orphan_offline", "test_triggered_stop_offline", "test_soak_report", "test_fix3_offline", "test_fix4_offline",
        "test_plan_compiler", "test_executor_math", "test_auto_trader", "test_fabio_slot", "test_mts_kill_mainnet", "test_pm_heartbeat", "test_pm_heartbeat_wiring", "test_journal_env", "test_mainnet_plan_check", "test_env_wiring", "test_reconciler_env", "test_deribit_read_account", "test_orphan_watchdog", "test_orphan_watchdog_cli", "test_mainnet_pnl", "test_daily_pnl_wiring", "test_xferfix", "test_time_exit_offline", "test_trade_ledger", "test_netretry", "test_r2_runner_exit", "test_r2_breakeven_move",  # W2 R2: execution-math tests (FORMULAS.md 11)
    ]
    success, output = run_step(1, "Execution module tests", cmd1)
    results.append(("Step 1: Execution tests", success))

    # Step 2: g1g2 offline script test
    cmd2 = [
        sys.executable, "scripts/dev/run_staged_tests.py",
        "MyTradingSys/execution", "MyTradingSys/execution/testnet/offline",
        "--script", "test_g1g2_offline.py",
        "--fake", "fake_deribit_orders.py=deribit_orders.py",
    ]
    success, output = run_step(2, "G1G2 offline script test", cmd2)
    results.append(("Step 2: G1G2 offline test", success))

    # Step 3: static suite test
    cmd3 = [sys.executable, "MyTradingSys/execution/testnet/test_suite_static.py"]
    success, output = run_step(3, "Static test suite", cmd3)
    results.append(("Step 3: Static test suite", success))

    # Step 3b: user guide matches mts.ps1 (commands + paths)
    cmd3b = [sys.executable, "scripts/dev/test_check_guide.py"]
    success, output = run_step("3b", "User guide checker tests", cmd3b)
    results.append(("Step 3b: Guide checker tests", success))
    cmd3c = [sys.executable, "scripts/dev/check_guide.py"]
    success, output = run_step("3c", "User guide in sync with mts.ps1", cmd3c)
    results.append(("Step 3c: Guide in sync", success))
    cmd3r = [sys.executable, "scripts/dev/test_alert_rate_check.py"]
    success, output = run_step("3r", "Alert rate checker tests", cmd3r)
    results.append(("Step 3r: Alert rate checker tests", success))
    cmd3s = [sys.executable, "scripts/dev/test_testnet_status.py"]
    success, output = run_step("3s", "Testnet status summary tests", cmd3s)
    results.append(("Step 3s: Testnet status tests", success))
    cmd3f = [sys.executable, "scripts/dev/test_funnel_report.py"]
    success, output = run_step("3f", "Funnel report tests", cmd3f)
    results.append(("Step 3f: Funnel report tests", success))
    cmd3d = [sys.executable, "scripts/dev/test_verify_extract_quotes.py"]
    success, output = run_step("3d", "Extract quote checker tests", cmd3d)
    results.append(("Step 3d: Quote checker tests", success))
    cmd3h = [sys.executable, "scripts/dev/test_mts_launcher.py"]
    success, output = run_step("3h", "Launcher verb static tests (runner, orphans)", cmd3h)
    results.append(("Step 3h: Launcher static tests", success))
    cmd3g = [sys.executable, "scripts/dev/test_run_all_tests.py"]
    success, output = run_step("3g", "Gate coverage tests (Fabio v3 + live writers)", cmd3g)
    results.append(("Step 3g: Gate coverage tests", success))
    cmd3e = [sys.executable, "scripts/worker/test_dsa_worker.py"]
    success, output = run_step("3e", "DSA browser worker + queue lane tests", cmd3e)
    results.append(("Step 3e: DSA worker tests", success))

    # Step 4: pytest (math + doc tests)
    cmd4 = [sys.executable, "-m", "pytest", "MyTradingSys/tests", "-q",
            # function-style tests that unittest-based steps 5b/6 do not collect
            "MyTradingSys/backtest/bt/test_bt_rsi.py", "MyTradingSys/backtest/bt/test_bt_rsi_edge.py",
            "MyTradingSys/backtest/test_prob_table.py", "MyTradingSys/backtest/test_prob_table_edge.py",
            "MyTradingSys/backtest/test_tom_bt.py"] + PYTEST_LAYER_PATHS
    success, output = run_step(4, "Pytest (math + doc tests)", cmd4)
    results.append(("Step 4: Pytest tests", success))

    # Step 5: mvn test (unless --quick)
    if not quick:
        # Check if mvn is available
        try:
            mvn = shutil.which("mvn") or shutil.which("mvn.cmd") or "mvn"  # Windows: mvn.cmd
            check_mvn = subprocess.run(
                [mvn, "--version"],
                capture_output=True,
                text=True,
            )
            if check_mvn.returncode == 0:
                cmd5 = [mvn, "-q", "test"]
                success, output = run_step(5, "Maven Java tests", cmd5)
                results.append(("Step 5: Maven tests", success))
            else:
                print("\n[Step 5] Maven Java tests")
                print("Step 5: SKIP (mvn not found)")
                results.append(("Step 5: Maven tests", None))
        except FileNotFoundError:
            print("\n[Step 5] Maven Java tests")
            print("Step 5: SKIP (mvn not found)")
            results.append(("Step 5: Maven tests", None))
    else:
        print("\n[Step 5] Maven Java tests (skipped with --quick)")
        results.append(("Step 5: Maven tests", None))

    # Step 5b: indicator-layer tests (fast; run even with --quick)
    layer_modules = find_layer_modules()
    if layer_modules:
        cmd5b = [sys.executable, "-m", "unittest"] + layer_modules
        success, output = run_step("5b", f"Layer tests ({len(layer_modules)} modules)", cmd5b)
        results.append(("Step 5b: Layer tests", success))

    # Step 6: backtest (unless --quick)
    if not quick:
        modules = find_backtest_modules()
        if modules:
            cmd6 = [
                sys.executable, "scripts/dev/run_staged_tests.py",
                "MyTradingSys/backtest/bt",
                "--",
            ] + modules
            success, output = run_step(6, f"Backtest tests ({len(modules)} modules)", cmd6)
            results.append(("Step 6: Backtest tests", success))
        else:
            print("\n[Step 6] Backtest tests")
            print("Step 6: SKIP (no test modules found)")
            results.append(("Step 6: Backtest tests", None))
    else:
        print("\n[Step 6] Backtest tests (skipped with --quick)")
        results.append(("Step 6: Backtest tests", None))

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    failed = []
    for step_name, result in results:
        if result is True:
            print(f"{step_name}: PASS")
        elif result is False:
            print(f"{step_name}: FAIL")
            failed.append(step_name)
        else:
            print(f"{step_name}: SKIP")

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
