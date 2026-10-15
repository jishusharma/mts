#!/usr/bin/env python
"""run_extra_tests.py - run the tracked test files that live outside the dirs the main gate collects (B150).

Each file runs in its own pytest process with the file's directory as cwd (the way each was written to run), so same-named
helper modules in different dirs cannot collide. Files run MTS_GATE_JOBS at a time (default min(4, cpu count); 1 = one after
the other), each with its own --basetemp, and print their line when they finish. Exit 1 if any file fails. The list is checked by
MyTradingSys/tests/test_gate_discovery_b150.py: a new tracked test file must be gated, listed here, or skipped with a reason.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXTRA = [
    "MyTradingSys/research/qriptal_2026-10-10/test_ledger.py",
    "MyTradingSys/research/qriptal_2026-10-10/test_score_calls.py",
    "MyTradingSys/research/chart_read_g5_2026-10-16/test_common.py",
    "MyTradingSys/research/opr_preopen_tops_2026-10-16/test_study.py",
    "MyTradingSys/research/mal_bb_mid_engulf_2026-10-16/test_study.py",
    "MyTradingSys/research/layer_lab/candle_close_2026-10-14/test_study.py",
    "MyTradingSys/research/gross_effect_screen_2026-10-15/test_screen.py",
    "scripts/dev/test_suplock.py",
    "MyTradingSys/research/mfe_exit_2026-10-13/test_mfe_exit_study.py",
    "MyTradingSys/research/malkan_extract_2026-10-15/tools/test_check_numbers.py",
    "MyTradingSys/research/g3_marks_2026-10-16/test_g3_pack.py",
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
    "MyTradingSys/research/levels_confluence_2026-10-14/test_levels.py",
    "MyTradingSys/runtime/test_update_market_state.py",
    "scripts/dev/test_testnet_canary.py",
    "scripts/worker/test_audit_digest.py",
    "scripts/worker/test_audit_rotation.py",
    "scripts/worker/test_audit_t0_checks.py",
    "tests/test_worker_prefix_hash.py",
    "scripts/dev/test_fabio_prescreen.py",
    "scripts/dev/test_sched_scripts.py",
]


def jobs():
    """Concurrent pytest processes: MTS_GATE_JOBS (the gate's knob), default min(4, cpu count)."""
    try:
        n = int(os.environ.get("MTS_GATE_JOBS", ""))
    except ValueError:
        n = min(4, os.cpu_count() or 1)
    return max(1, n)


def run_one(rel, basetemp):
    """(ok, one-line result) for one extra test file: its own pytest process, cwd and basetemp."""
    p = REPO / rel
    if not p.exists():
        return False, "missing"
    r = subprocess.run([sys.executable, "-m", "pytest", p.name, "-q", "-p", "no:cacheprovider", f"--basetemp={basetemp}"],
                       cwd=p.parent, capture_output=True, text=True, errors="replace")
    return r.returncode == 0, (r.stdout.strip().splitlines() or ["(no output)"])[-1]


def run_files(rels, n_jobs, one=run_one, tmp=None):
    """Run every file `n_jobs` at a time and print one flushed line per file as it finishes. Returns the failures in list order."""
    # Own basetemp per file: pytest's default %TEMP%/pytest-of-<user>/pytest-current cleanup raises PermissionError
    # (exit 1 after all tests pass) when another account left that link behind (JIS-NB 2026-10-14); it is also what lets
    # the files run beside each other.
    tmp = Path(tmp or tempfile.mkdtemp(prefix="mts_xt_"))
    lock = threading.Lock()
    done = {}

    def work(item):
        i, rel = item
        ok, tail = one(rel, tmp / str(i))
        with lock:
            print(f"{'ok  ' if ok else 'FAIL'} {rel}: {tail}", flush=True)
        done[rel] = (ok, tail)

    with ThreadPoolExecutor(max_workers=max(1, n_jobs)) as pool:
        list(pool.map(work, enumerate(rels)))
    return [f"{rel}: missing" if done[rel][1] == "missing" else rel for rel in rels if not done[rel][0]]


def main():
    try:
        sys.stdout.reconfigure(line_buffering=True, errors="replace")
    except (AttributeError, ValueError):
        pass
    tmp = Path(tempfile.mkdtemp(prefix="mts_xt_"))
    bad = run_files(EXTRA, jobs(), tmp=tmp)
    shutil.rmtree(tmp, ignore_errors=True)
    print("extra tests: " + ("FAIL " + ", ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
