"""Per-test time limit for the ship gate, without pytest-timeout (not installed: `pip list` 2026-11-11; no dependency added).

Loaded with `-p pytest_test_limit` (run_all_tests.pytest_cmd). A watchdog timer is armed around every test (setup + call + teardown). If the
test is still running after the limit, the plugin prints `TEST TIMEOUT: <nodeid> exceeded <n> s` plus every thread's stack to stderr and
ends the pytest process with exit 1, so the shard fails with the test's name instead of holding the ship (2026-11-11: one ship sat 50 min on a
hung pytest with no test name).

DECISION (OURS): limit 300 s locally (raised from 120 s 2026-11-12: test_aibridge_selftest_concurrent ran past 120 s on a loaded machine); MTS_TEST_LIMIT_S overrides it on any host (0 = off). ON GITHUB CI THE LIMIT IS ON (300 s, since ci-hang-fix-1113; it was off 2026-11-11..12 and a hang cancelled shards).
The first version (582709541, reverted c2771d345) applied 120 s on CI and killed test_aibridge_chain's long test (the CI file total of
that file was 121-144 s in runs 43074883278/43075303873). CI prints per-FILE seconds only, so per-test CI times are unknown until the
"Gate test times" notice (run_all_tests.times_notice, top 25 single tests) has shown one green CI run; then set MTS_TEST_LIMIT_S on CI.
SLOW_OK = {path substring: seconds}: an allowance is at least 3x the slowest CI seconds seen for the file (CI per-file totals, runs
43074634134, 43074883278, 43075303873, 2026-11-11); a file total is an upper bound for any one test in it. OURS.
"""
import faulthandler
import os
import sys
import threading

import pytest

DEFAULT_LIMIT_S = 300
SLOW_OK = {
    "test_aibridge_chain.py": 450,        # CI file total 121-144 s (long unattended chain test) x3
    "test_aibridge_selftest_concurrent.py": 450,  # blocked a ship 2026-11-12 at 120 s on a loaded machine (CI 27-39 s)
    "test_aibridge_exploratory.py": 400,  # CI 46-56 s; 139 s locally (headless browser + run-task.ps1, up to 180 s each)
    "test_context_asof.py": 360,          # CI file total 87-111 s x3
    "test_trunk_lag.py": 360,             # CI file total 72-114 s x3
    "test_relay.py": 300,                 # CI file total 92-99 s x3
}


def limit_for(nodeid, env=None):
    env = os.environ if env is None else env
    raw = env.get("MTS_TEST_LIMIT_S")
    # CI uses the same 300 s default as a local run (ci-hang-fix-1113): with the limit off, one hung test (test_sync's gate-slot test, 2026-11-12)
    # held a shard to the 30 min job timeout and GitHub cancelled it with no test name. SLOW_OK allowances are all >= 300 s.
    try:
        base = float(raw) if raw is not None else DEFAULT_LIMIT_S
    except ValueError:
        base = DEFAULT_LIMIT_S
    if base <= 0:
        return 0
    return max([base] + [v for k, v in SLOW_OK.items() if k in nodeid])


_CONFIG = []


def pytest_configure(config):
    _CONFIG[:] = [config]


def _expire(nodeid, limit):
    try:   # pytest captures fd 1/2 while a test runs: switch capture off so the message reaches the gate's pipe
        _CONFIG[0].pluginmanager.get_plugin("capturemanager").suspend_global_capture(in_=True)
    except Exception:
        pass
    sys.stderr.write(f"\nTEST TIMEOUT: {nodeid} exceeded {limit:g} s (per-test limit of the ship gate)\n")
    sys.stderr.flush()
    try:
        faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
        sys.stderr.flush()
    except Exception:
        pass
    os._exit(1)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    limit = limit_for(item.nodeid)
    timer = None
    if limit:
        timer = threading.Timer(limit, _expire, (item.nodeid, limit))
        timer.daemon = True
        timer.start()
    try:
        yield
    finally:
        if timer:
            timer.cancel()
