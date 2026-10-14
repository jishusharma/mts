#!/usr/bin/env python
"""run_extra_tests.py - run the tracked test files that live outside the dirs the main gate collects (B150).

Each file runs in its own pytest process with the file's directory as cwd (the way each was written to run), so same-named
helper modules in different dirs cannot collide. Exit 1 if any file fails. The list is checked by
MyTradingSys/tests/test_gate_discovery_b150.py: a new tracked test file must be gated, listed here, or skipped with a reason.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXTRA = [
    "MyTradingSys/research/layer_lab/candle_close_2026-10-14/test_study.py",
    "scripts/dev/test_suplock.py",
    "MyTradingSys/research/mfe_exit_2026-10-13/test_mfe_exit_study.py",
    "scripts/dev/test_make_layer_map.py",
    "scripts/dev/test_make_layers_board.py",
    "scripts/dev/test_session_log.py",
    "scripts/dev/test_codex_pack.py",
    "scripts/dev/test_token_audit.py",
    "MyTradingSys/research/test_b141_htf_stage1.py",
    "MyTradingSys/research/test_b141_htf_stage2.py",
    "MyTradingSys/execution/tests/test_deribit_orders_phase3.py",
    "MyTradingSys/execution/tests/test_executor_reject_diag.py",
    "MyTradingSys/observation/tests/test_observation.py",
    "MyTradingSys/research/candle_patterns_2026-10-04/pilot/test_p1.py",
    "MyTradingSys/research/candle_patterns_2026-10-04/pilot/test_pilot.py",
    "MyTradingSys/research/fast_track_2026-09-27/backtest_xcheck/test_ref_ladder.py",
    "MyTradingSys/research/volume_2026-10-09/test_state.py",
    "MyTradingSys/research/volume_2026-10-09/test_volume.py",
    "MyTradingSys/research/tom_btc_2026-10-13/test_chart_lab.py",
    "MyTradingSys/runtime/test_update_market_state.py",
    "scripts/dev/test_testnet_canary.py",
    "scripts/worker/test_audit_digest.py",
    "scripts/worker/test_audit_rotation.py",
    "scripts/worker/test_audit_t0_checks.py",
    "tests/test_worker_prefix_hash.py",
    "scripts/dev/test_fabio_prescreen.py",
    "scripts/dev/test_sched_scripts.py",
]


def main():
    bad = []
    # Own basetemp per file: pytest's default %TEMP%/pytest-of-<user>/pytest-current cleanup raises PermissionError
    # (exit 1 after all tests pass) when another account left that link behind (JIS-NB 2026-10-14).
    tmp = Path(tempfile.mkdtemp(prefix="mts_xt_"))
    for i, rel in enumerate(EXTRA):
        p = REPO / rel
        if not p.exists():
            bad.append(f"{rel}: missing")
            continue
        r = subprocess.run([sys.executable, "-m", "pytest", p.name, "-q", "-p", "no:cacheprovider",
                            f"--basetemp={tmp / str(i)}"], cwd=p.parent, capture_output=True, text=True)
        tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        print(f"{'ok  ' if r.returncode == 0 else 'FAIL'} {rel}: {tail}")
        if r.returncode != 0:
            bad.append(rel)
    shutil.rmtree(tmp, ignore_errors=True)
    print("extra tests: " + ("FAIL " + ", ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
