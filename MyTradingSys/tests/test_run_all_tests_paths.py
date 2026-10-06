"""Guard: PYTEST_LAYER_PATHS in scripts/dev/run_all_tests.py includes every
layer test directory whose tests must run in the gate.

B130: MyTradingSys/execution/tests was added after the T050 phase 3 tests
landed there (commit f088b52). This test fails on the pre-fix script and
passes after.
"""
import sys
sys.dont_write_bytecode = True

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNNER = REPO / "scripts" / "dev" / "run_all_tests.py"

REQUIRED_PATHS = [
    "MyTradingSys/execution/tests",
]


def test_required_paths_present_in_runner():
    text = RUNNER.read_text(encoding="utf-8")
    missing = [p for p in REQUIRED_PATHS if ('"' + p + '"') not in text]
    assert not missing, "run_all_tests.py PYTEST_LAYER_PATHS missing: " + str(missing)