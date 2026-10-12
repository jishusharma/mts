#!/usr/bin/env python
"""run_extra_tests.py - run the tracked test files that live outside the dirs the main gate collects (B150).

Each file runs in its own pytest process with the file's directory as cwd (the way each was written to run), so same-named
helper modules in different dirs cannot collide. Exit 1 if any file fails. The list is checked by
MyTradingSys/tests/test_gate_discovery_b150.py: a new tracked test file must be gated, listed here, or skipped with a reason.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXTRA = [
    "scripts/dev/test_suplock.py",
    "scripts/dev/test_codex_pack.py",
    "scripts/dev/test_token_audit.py",
    "MyTradingSys/research/test_b141_htf_stage1.py",
    "MyTradingSys/research/test_b141_htf_stage2.py",
    "MyTradingSys/execution/tests/test_deribit_orders_phase3.py",
    "MyTradingSys/observation/tests/test_observation.py",
    "MyTradingSys/research/candle_patterns_2026-10-04/pilot/test_p1.py",
    "MyTradingSys/research/candle_patterns_2026-10-04/pilot/test_pilot.py",
    "MyTradingSys/research/fast_track_2026-09-27/backtest_xcheck/test_ref_ladder.py",
    "MyTradingSys/research/volume_2026-10-09/test_state.py",
    "MyTradingSys/research/volume_2026-10-09/test_volume.py",
    "MyTradingSys/runtime/test_update_market_state.py",
    "scripts/dev/test_backfill_naked_pocs.py",
    "scripts/dev/test_testnet_canary.py",
    "scripts/worker/test_audit_digest.py",
    "scripts/worker/test_audit_rotation.py",
    "scripts/worker/test_audit_t0_checks.py",
    "tests/test_worker_prefix_hash.py",
]


def main():
    bad = []
    for rel in EXTRA:
        p = REPO / rel
        if not p.exists():
            bad.append(f"{rel}: missing")
            continue
        r = subprocess.run([sys.executable, "-m", "pytest", p.name, "-q", "-p", "no:cacheprovider"], cwd=p.parent,
                           capture_output=True, text=True)
        tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        print(f"{'ok  ' if r.returncode == 0 else 'FAIL'} {rel}: {tail}")
        if r.returncode != 0:
            bad.append(rel)
    print("extra tests: " + ("FAIL " + ", ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
