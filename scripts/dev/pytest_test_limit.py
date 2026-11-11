"""Per-test time limit for the ship gate, without pytest-timeout (not installed: `pip list` 2026-11-11; no dependency added).

Loaded with `-p pytest_test_limit` (run_all_tests.pytest_cmd). A watchdog timer is armed around every test (setup + call + teardown). If the
test is still running after the limit, the plugin prints `TEST TIMEOUT: <nodeid> exceeded <n> s` plus every thread's stack to stderr and
ends the pytest process with exit 1, so the shard fails with the test's name instead of holding the ship (2026-11-11: one ship sat 50 min on a
hung pytest with no test name).

DECISION (OURS): limit 120 s; MTS_TEST_LIMIT_S overrides it (0 = off). SLOW_OK holds the files measured slower than that on purpose.
"""
import faulthandler
import os
import sys
import threading

import pytest

DEFAULT_LIMIT_S = 120
SLOW_OK = {"test_aibridge_exploratory.py": 400}   # OURS: 139 s alone for the file (headless browser + run-task.ps1, up to 180 s each)


def limit_for(nodeid, env=None):
    env = os.environ if env is None else env
    try:
        base = float(env.get("MTS_TEST_LIMIT_S", DEFAULT_LIMIT_S))
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
