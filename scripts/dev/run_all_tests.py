"""Unified offline test runner - runs all test suites.

Usage:
  python scripts/dev/run_all_tests.py         (run all steps)
  python scripts/dev/run_all_tests.py --quick (skip mvn and backtest)
  python scripts/dev/run_all_tests.py --quick --smoke --changed-file F   (what `sync.py ship` runs: only the steps gate_select picks
                                                                          for the paths listed in F; live-path or unknown paths = all)
  sync.py ship adds --precheck --fail-fast --slot --record (MyTradingSys/system/GATE_SPEED.md): cheap steps first without the gate
  slot, stop at the first failure, the slot around the main phase only, steps that passed on this exact clean tree are not rerun.

Steps that share no state run concurrently in MTS_GATE_JOBS worker threads (default min(4, cpu count); MTS_GATE_JOBS=1 runs
one step at a time in definition order, the old behaviour). SERIAL_STEPS (they scan or write checkout state) and Maven run one
at a time after the pool. Each step prints its block when it finishes, line-buffered, with its own time and a progress count, so
a redirected or backgrounded run shows progress; the SUMMARY lists every step in definition order. A foreground tool call dies
at 600 s: start the gate (and `sync.py ship`, which calls it) in the background and read the output once.
"""
import atexit
import contextlib
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))   # gate_select

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
    "scripts/dev/test_live_owner.py",
    "scripts/dev/test_loop_supervisor_grace.py",
    "scripts/dev/test_nowin.py",
    "scripts/dev/test_outcome_labeler_incremental.py",
    "scripts/dev/test_wrapper_load_resilience.py",
    "scripts/dev/test_gate_priority.py",
    "scripts/dev/test_gate_scratch.py",
    "scripts/dev/test_feed_watchdog_script.py",
    "MyTradingSys/observation/tests",
]

# Function-style pytest tests of the backtest tree (shard 4e).
BACKTEST_PYTEST_PATHS = [
    "MyTradingSys/backtest/test_prob_table.py",
    "MyTradingSys/backtest/test_prob_table_edge.py",
    "MyTradingSys/backtest/test_tom_bt.py",
    "MyTradingSys/backtest/test_tom_probe_diag.py",
    "MyTradingSys/backtest/test_dax_data.py",
    "MyTradingSys/backtest/test_tom_dax_recall.py",
    "MyTradingSys/backtest/test_tom_v2_recall.py",
    "MyTradingSys/backtest/test_tom_dax_bt.py",
]

# These steps scan or write checkout state (layer index, artifact registry, wiring --check, STATUS generator, group map), and
# Step 4's tests drop fixtures in the tree, so they never run beside the pool. Maven (step 5) is serial as well.
SERIAL_STEPS = ("3ly", "3af", "3x", "3ms", "3mg", "5")
# Submitted first so the pool's last step is not the slowest one (measured: 4, 3xt, 5b, 3k, 3ds, 3dk, 3bk, 3w).
# Pytest shards of MyTradingSys/tests and the measured seconds of its slow files (2026-10-16 profile, loaded machine); the rest ~2 s each.
PYTEST_SHARD_NUMS = ("4", "4b", "4c", "4g", "4h")
TEST_FILE_DEFAULT_S = 2
TEST_FILE_SECONDS = {
    "test_turn_meter.py": 8,     # 150 until GATE_SPEED D7 (2026-10-18) ran its hook calls in-process: 7 s

    "test_aibridge_payload.py": 95,
    "test_b091_build_check_tiers.py": 60,
    "test_build_check_report_reasons.py": 32,
    "test_relay_tick.py": 32,
    "test_relay.py": 25,
    "test_tom_profile_parity.py": 12,
    "test_net_rr_floor_single_source.py": 8,
    "test_sync_where_unborn.py": 6,
    "test_dsa_direct_mode.py": 6,
}
SLOWEST_FIRST = ("4", "4b", "4c", "4g", "4h", "4e", "4f","3xt", "5b", "3k", "3ds", "3dk", "3bk", "3w")
_LOCK = threading.Lock()

# GATE_SPEED D1 (ship only, --precheck): these run first, PRECHECK_JOBS at a time and WITHOUT a gate slot; any failure stops the gate
# before the slow steps start. OURS: the steps whose median is <= 25 s over 4106 step rows of 30 trees' gate_timing.jsonl (2026-10-18),
# plus 3x (ALWAYS, 18 s in ship logs, 8 failures) and 3js. 2026-10-18: RELAY.md over its size cap failed step 4d (6.6 s) at +438 s.
CHEAP_STEPS = ("1", "2", "3", "3b", "3c", "3r", "3cv", "3tm", "3s", "3f", "3td", "3hs", "3sq", "3ly", "3cy", "3tl", "3q", "3p", "3t",
               "3d", "3h", "3g", "3gs", "3rc", "3e", "3sh", "3cs", "3pc", "3rb", "3af", "3vd", "3lm", "3gd", "3dl", "3x", "3mg", "3js",
               "4d", "4e", "5c")
PRECHECK_JOBS = 2
TARGET_STEP = "4t"   # precheck pytest of the MyTradingSys/tests files that reference the change (they also run in their shard)
TARGET_CAP = 12      # OURS: at most this many files (sorted), so the precheck stays about a minute
SLOW_FILE_S = 30     # files measured at >= this many seconds stay in their shard only
CHEAP_STEPS += ("3qn", "3gi")
# GATE_SPEED X2 (ship only, --fast, smoke mode): the fast path. One phase, tests chosen by gate_impact, a time budget, the rest left to CI.
FAST_STEP_TIMEOUT_S = 240     # OURS: a fast-gate step still running after this is hung (a held slot would block every later ship)
FAST_BASE_S = 6              # OURS: seconds of ALWAYS-step work counted against the budget before any test is added
UNIT_DEFAULT_S = 8            # OURS: estimated seconds of a script-style test step that is not in STEP_EST
EXTRA_FILE_S = 4              # OURS: estimated seconds per step-3xt file (one pytest process each) and per step-5b module
# Estimated CPU seconds of the script-style test steps a change can reach (each run alone on JIS-NB, 2026-10-18; 3k/3ds/3dk/3bk run as
# 2-3 shards, the figure is their sum); a step above the budget is deferred to CI unless a changed file names it.
STEP_EST = {"3k": 200, "3ds": 30, "3bk": 25, "3dk": 14, "3ad": 24, "3sig": 21, "3cx": 11, "3tk": 13, "3lh": 9, "3ms": 13, "3sg": 9,
            "3cr": 8, "3lm": 4, "3hy": 1, "3w": 9, "3x": 3}
RECORD_NAME = "mts_gate_record.json"   # GATE_SPEED D3: per-worktree git dir, never shared between trees or machines
RECORD_MAX_AGE_S = 24 * 3600

# Why gate_select chose the plan (set by apply_selection) and the mode, for the timing log.
gate_reason = None
gate_mode = None
TIMING_FILE = Path("runtime_data") / "gate_timing.jsonl"   # gitignored: per-step timings, nothing sensitive


_SHA = []


def _short_sha():
    if _SHA:   # one `git rev-parse` per gate, not one per step (GATE_SPEED X2: 0.1 s each on Windows)
        return _SHA[0]
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=str(REPO), capture_output=True, text=True, timeout=10)
        _SHA.append(r.stdout.strip() or "?")
        return _SHA[0]
    except Exception:
        return "?"


def record_timing(num, name, seconds, ok, mode, path=None):
    """Append one JSON line {step, name, secs, ok, mode, utc, sha} to the untracked timing log (MTS_GATE_TIMING overrides the path).
    Never raises: a log that cannot be written must not fail the gate."""
    try:
        path = Path(path or os.environ.get("MTS_GATE_TIMING") or REPO / TIMING_FILE)
        path.parent.mkdir(parents=True, exist_ok=True)
        row = {"step": str(num), "name": name, "secs": round(seconds, 2), "ok": ok, "mode": mode,
               "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "sha": _short_sha()}
        with open(path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(row) + "\n")
    except Exception:
        pass


def transient_ignore_glob(root=REPO):
    """pytest `--ignore-glob` for tempfile's default scratch dirs ("tmp" + 8 of [a-z0-9_]) anywhere under `root`. On Windows pytest
    lstat()s every directory entry beside each path it descends into, so a tmpXXXXXXXX dir that another gate step creates and removes
    in the same folder raised FileNotFoundError at collection (2026-10-16: step 4f in CI run 38825784050, the JIS-NB deploy gate on
    50f8f6b). An ignored entry never becomes a collection node. The set [/\\] is the path separator (pytest runs the pattern through
    os.path.abspath, which turns / into \\ on Windows); tmp_fixtures-style folders and test_tmp_* names do not match."""
    return "--ignore-glob=" + glob.escape(str(root)) + "*[/\\]tmp" + "[a-z0-9_]" * 8


_GATE_TMP_DIRS = []


def _remove_gate_tmp():
    while _GATE_TMP_DIRS:
        shutil.rmtree(_GATE_TMP_DIRS.pop(), ignore_errors=True)


def gate_tmp(prefix):
    """mkdtemp that is removed when this gate process exits. Every ship built 5+ basetemp dirs and never removed them: 24k mts_s4_*
    dirs (1.2 GB) piled up in %TEMP% on JIS-NB by 2026-10-18 and C: ran low (c_drive_guard.py prunes what a killed gate leaves)."""
    if not _GATE_TMP_DIRS:
        atexit.register(_remove_gate_tmp)
    d = tempfile.mkdtemp(prefix=prefix)
    _GATE_TMP_DIRS.append(d)
    return Path(d)


def pytest_cmd(targets, root=REPO, deselect=()):
    """One gate pytest step: own basetemp (parallel pytest processes share %TEMP%/pytest-of-<user> and its cleanup raises PermissionError
    after all tests pass: JIS-NB 2026-10-14, six ships at once), no cache dir, and transient tmp dirs ignored (transient_ignore_glob)."""
    scratch = tempfile.mkdtemp(prefix="mts_s4_")
    _SCRATCH.append(scratch)
    return [sys.executable, "-m", "pytest", *targets, "-q", "-p", "no:cacheprovider", transient_ignore_glob(root),
            f"--basetemp={Path(scratch) / 'bt'}", *[a for d in deselect for a in ("--deselect", d)]]


_SCRATCH = []


@atexit.register
def _drop_scratch():
    """B194: every gate run left ~12 mts_s4_* dirs of ~1000 files in %TEMP% (963 dirs / 374k files on JIS-NB by 2026-10-18, one run per
    AutoDeploy tick); the User Profile Service logon step grew from 18 s to 340 s as they piled up. Remove them when the run ends."""
    for d in _SCRATCH:
        shutil.rmtree(d, ignore_errors=True)


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


STEP_TIMEOUT_S = None   # set by the fast path (FAST_STEP_TIMEOUT_S); None = no limit, as before


def exec_step(cmd, cwd=None):
    """Run one command to completion. Returns (ok, output): ok is True/False, or None with a reason when the executable is missing.
    A step over STEP_TIMEOUT_S (fast path only) fails: a hung step must not hold a gate slot for ever."""
    try:
        result = subprocess.run(cmd, cwd=cwd or str(REPO), capture_output=True, text=True, errors="replace",
                                shell=isinstance(cmd, str), timeout=STEP_TIMEOUT_S)
    except FileNotFoundError as e:
        return None, f"not found: {e}"
    except subprocess.TimeoutExpired:
        return False, f"step timed out after {STEP_TIMEOUT_S} s (fast gate limit): treated as a failure"
    return result.returncode == 0, result.stdout + result.stderr


def ci_annotation(num, description, output, limit=3000):
    """A GitHub Actions ::error line for a failed step, or None off Actions. Job logs need a login even on a public repo (2026-10-16: the
    ubuntu job failed three times and no session could read why); annotations are public through the check-runs API."""
    if not os.environ.get("GITHUB_ACTIONS"):
        return None
    lines = output.splitlines()
    first = next((i for i, ln in enumerate(lines) if ln.lstrip().startswith(("FAIL", "ERROR", "E  ", "Traceback"))), max(len(lines) - 25, 0))
    body = "\n".join(lines[first:])[-limit:] or "(no output)"
    body = body.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    return f"::error title=Step {num} FAIL::{description} | {body}"


def format_step(num, description, cmd_text, ok, output, elapsed, progress="", tail=15):
    """The block one finished step prints. tail = how many output lines a failure shows (None = all; CI always shows all)."""
    lines = [f"\n[Step {num}] {description}", f"  Command: {cmd_text}"]
    if ok is None:
        lines.append(f"Step {num}: SKIP ({output})")
        return lines
    lines.append(f"  Elapsed: {elapsed:.1f}s" + (f" ({progress})" if progress else ""))
    lines.append(f"Step {num}: {'PASS' if ok else 'FAIL'}")
    out = output.splitlines()
    if not ok:
        if out:
            lines.append("  Last output:")
            lines += [f"    {ln}" for ln in (out if (os.environ.get("CI") or tail is None) else out[-tail:])]
        note = ci_annotation(num, description, output)
        if note:
            lines.append(note)
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
    # Python 3.12+ exits 5 when a chunk holds only modules with no unittest cases ('NO TESTS RAN'): that is not a failure.
    def passed(p, o):
        return p.returncode == 0 or (p.returncode == 5 and "NO TESTS RAN" in o)
    ok = all(passed(p, o) for p, o in zip(procs, outs))
    if ok:
        return True, "\n".join(outs)
    keep = [o if os.environ.get("CI") else "\n".join(o.splitlines()[-15:]) for p, o in zip(procs, outs) if not passed(p, o)]
    return False, "\n".join(keep)


def exec_unittest_shards(script, jobs):
    """Run one slow unittest script as `jobs` concurrent processes (its test ids split round-robin; union = every test, each once).
    cwd stays the repo root and scripts/dev goes on PYTHONPATH, as when the script runs directly. Returns (ok, output)."""
    import importlib
    import unittest
    mod_dir = str(REPO / Path(script).parent)
    sys.path.insert(0, mod_dir)
    try:
        suite = unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module(Path(script).stem))
    finally:
        sys.path.remove(mod_dir)

    def ids(t):
        return [i for x in t for i in (ids(x) if isinstance(x, unittest.TestSuite) else [x.id()])]

    chunks = split_modules(ids(suite), jobs)
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([mod_dir, os.environ.get("PYTHONPATH", "")]).rstrip(os.pathsep))
    procs = [subprocess.Popen([sys.executable, "-m", "unittest"] + c, cwd=str(REPO), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, errors="replace", env=env) for c in chunks]
    outs = [p.communicate()[0] for p in procs]
    ok = all(p.returncode == 0 for p in procs)
    def failing(o):   # from the first FAIL/ERROR header (a plain tail is only the tests' own prints), capped
        lines = o.splitlines()
        first = next((i for i, l in enumerate(lines) if l.startswith(("FAIL:", "ERROR:"))), max(len(lines) - 15, 0))
        return "\n".join(lines[first:first + 60])

    keep = outs if ok else [o if os.environ.get("CI") else failing(o) for p, o in zip(procs, outs) if p.returncode != 0]
    return ok, "\n".join(keep)


def isolate_pytest_tmp():
    """Give every pytest child of this gate its own fresh temp root (inherited via env). A stale pytest-of-<user>/pytest-current link in
    %TEMP% that cannot be unlinked (WinError 5, seen 2026-10-11 after the ESET removal reboot) makes pytest exit 1 even when every test passes,
    which turned the deploy gate red. Returns the path."""
    import tempfile
    root = os.environ.get("PYTEST_DEBUG_TEMPROOT") or str(gate_tmp("mts_pytest_"))
    os.environ["PYTEST_DEBUG_TEMPROOT"] = root
    return root


class Step:
    """One gate step. cmd is an argv list (or a string), or run is a zero-argument callable returning (ok, output); skip = reason
    it does not run. lane 'seq' steps run one at a time after the concurrent pool."""

    def __init__(self, num, desc, label, cmd=None, run=None, cmd_text=None, skip=None, tail=15, key=None):
        self.num, self.desc, self.label, self.skip, self.tail = str(num), desc, label, skip, tail
        self.cmd_text = cmd_text or (" ".join(cmd) if isinstance(cmd, list) else str(cmd))
        self.run = run or (lambda: exec_step(cmd))
        self.lane = "seq" if self.num in SERIAL_STEPS else "par"
        self.key = key   # what the step runs beyond cmd_text (a module subset); part of its pass-record signature
        self.est = None  # estimated seconds, set by the fast path (orders the pool longest first)

    def sig(self):
        """Signature for the pass record: the command without its per-run scratch paths, plus `key`."""
        import hashlib
        import re
        text = re.sub(r"--(basetemp|ignore-glob)=\S+", "", self.cmd_text.replace(sys.executable, "python"))
        return hashlib.sha1(f"{self.num}|{self.desc}|{' '.join(text.split())}|{self.key or ''}".encode("utf-8")).hexdigest()[:16]


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
        "test_daily_loss_guard", "test_daily_loss_monitor", "test_mainnet_flag_offline", "test_gh_executor_offline", "test_settlement_skip_offline",
        "test_gh_retry_offline", "test_halt_preflight_offline", "test_kill_switch", "test_kill_switch_account", "test_premainnet1_offline",
        "test_risk_guard", "test_s1_cap_offline", "test_s3_unprotected_offline",
        "test_s6_orphan_offline", "test_triggered_stop_offline", "test_soak_report", "test_fix3_offline", "test_fix4_offline",
        "test_plan_compiler", "test_executor_math", "test_auto_trader", "test_dlm_aggregate", "test_b148_reauth_account", "test_b146_fee_to_stop", "test_dlm_failure_cap", "test_dlm_blind_recovery", "test_auto_trader_blocklist", "test_auto_trader_sizes", "test_auto_trader_confirm", "test_auto_trader_promotion", "test_orphan_sweep_loop", "test_fabio_slot", "test_fix3_mutants_offline", "test_capture_txlog_settlement", "test_mts_kill_mainnet", "test_pm_heartbeat", "test_pm_heartbeat_wiring", "test_journal_env", "test_mainnet_plan_check", "test_env_wiring", "test_reconciler_env", "test_deribit_read_account", "test_orphan_watchdog", "test_orphan_watchdog_cli", "test_mainnet_pnl", "test_daily_pnl_wiring", "test_xferfix", "test_time_exit_offline", "test_trade_ledger", "test_netretry", "test_r2_runner_exit", "test_r2_breakeven_move",  # W2 R2: execution-math tests (FORMULAS.md 11)
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
    add("3cv", "Chart verify (RSI/BB/StochRSI) tests", [sys.executable, "scripts/dev/test_chart_verify.py"], "Step 3cv: Chart verify tests")
    add("3tm", "One timeframe map tests", [sys.executable, "scripts/dev/test_tf_map.py"], "Step 3tm: TF map tests")
    add("3s", "Testnet status summary tests", [sys.executable, "scripts/dev/test_testnet_status.py"], "Step 3s: Testnet status tests")
    add("3f", "Funnel report tests", [sys.executable, "scripts/dev/test_funnel_report.py"], "Step 3f: Funnel report tests")
    plan.append(Step("3dk", "Desk board tests", "Step 3dk: Desk board tests", run=lambda: exec_unittest_shards("scripts/dev/test_desk.py", gate_jobs() if gate_jobs() == 1 else 2), cmd_text="python -m unittest (scripts/dev/test_desk.py, 2 shards)", tail=None))
    add("3tk", "Task card tests", [sys.executable, "scripts/dev/test_tasks.py"], "Step 3tk: Task card tests")
    add("3td", "Tom ledger date tests", [sys.executable, "scripts/dev/test_tom_ledger_dates.py"], "Step 3td: Tom ledger date tests")   # Tom ledger date column: observed or empty (RV01 D4)
    add("3hs", "Tom holdout split tests", [sys.executable, "scripts/dev/test_tom_holdout_split.py"], "Step 3hs: Tom holdout split tests")   # Tom holdout clean split, dates only
    add("3sq", "Spec quote checker tests", [sys.executable, "scripts/dev/test_check_spec_quotes.py"], "Step 3sq: Spec quote checker tests")   # spec quotes verbatim in the cited transcript lines
    add("3ly", "Layer index tests", [sys.executable, "scripts/dev/test_make_layers_md.py"], "Step 3ly: Layer index tests")   # LAYERS.md: no dead pointer, every layer owned
    add("3cx", "Layer lab runner tests", [sys.executable, "scripts/dev/test_codex_run.py"], "Step 3cx: Layer lab runner tests")
    add("3cy", "ask_model tests", [sys.executable, "scripts/dev/test_ask_model.py"], "Step 3cy: ask_model tests")
    add("3tl", "Task cards meet the Definition of Ready", [sys.executable, "scripts/dev/tasks.py", "lint"], "Step 3tl: Task card lint")   # a ready/active card that fails the Definition of Ready is an error
    add("3q", "INDEX/BUGS consistency", [sys.executable, "scripts/dev/test_registry_consistency.py"], "Step 3q: INDEX/BUGS consistency")
    add("3p", "P4 corrected script tests", [sys.executable, "MyTradingSys/research/test_p4_corrected.py"], "Step 3p: P4 corrected script tests")
    add("3t", "T093 turn-of-candle imbalance tests", [sys.executable, "MyTradingSys/research/test_t093_toc_imbalance_klines.py"], "Step 3t: T093 imbalance tests")
    add("3d", "Extract quote checker tests", [sys.executable, "scripts/dev/test_verify_extract_quotes.py"], "Step 3d: Quote checker tests")
    add("3h", "Launcher verb static tests (runner, orphans)", [sys.executable, "scripts/dev/test_mts_launcher.py"], "Step 3h: Launcher static tests")
    add("3g", "Gate coverage tests (Fabio v3 + live writers)", [sys.executable, "scripts/dev/test_run_all_tests.py"], "Step 3g: Gate coverage tests")
    plan.append(Step("3k", "sync.py parallel ship tests", "Step 3k: sync.py tests", run=lambda: exec_unittest_shards("scripts/dev/test_sync.py", gate_jobs() if gate_jobs() == 1 else 3), cmd_text="python -m unittest (scripts/dev/test_sync.py, 3 shards)", tail=None))
    add("3gs", "Gate selector tests (path -> smoke steps, fail closed)", [sys.executable, "scripts/dev/test_gate_select.py"], "Step 3gs: Gate selector tests")
    add("3rc", "Red CI task card tests (one card per red run)", [sys.executable, "scripts/dev/test_ci_red_card.py"], "Step 3rc: Red CI card tests")
    add("3sg", "Stop guard tests (a session cannot end holding unshipped work)", [sys.executable, "scripts/dev/test_stop_guard.py"], "Step 3sg: Stop guard tests")
    add("3sig", "Signals between logins (mts_signal.py)", [sys.executable, "scripts/dev/test_mts_signal.py"], "Step 3sig: Signals tests")
    add("3e", "DSA browser worker + queue lane tests", [sys.executable, "scripts/worker/test_dsa_worker.py"], "Step 3e: DSA worker tests")
    add("3sh", "Screenshot intake tests (save, classify, read, close gates)", [sys.executable, "scripts/dev/test_shot.py"], "Step 3sh: Screenshot intake tests")
    add("3mg", "Project group map tests (every row and file has one group)", [sys.executable, "scripts/dev/test_make_groups.py"], "Step 3mg: Project group map tests")
    add("3xt", "Extra tests outside the collected dirs (B150 discovery)", [sys.executable, "scripts/dev/run_extra_tests.py"], "Step 3xt: Extra tests")
    add("3ad", "Scheduled auto-deploy tests (stops on red gate)", [sys.executable, "scripts/dev/test_auto_deploy.py"], "Step 3ad: Auto-deploy tests")
    add("3hy", "Daily hygiene job tests", [sys.executable, "scripts/dev/test_daily_hygiene.py"], "Step 3hy: Daily hygiene tests")
    add("3ms", "STATUS.md generator tests (commit-dated reports, CI green line)", [sys.executable, "scripts/dev/test_make_status.py"], "Step 3ms: make_status tests")
    add("3cs", "Cloud SessionStart hook tests (no-op off cloud)", [sys.executable, "scripts/dev/test_cloud_setup.py"], "Step 3cs: Cloud setup hook tests")
    add("3pc", "Prompt contract tests (DSA_SESSION_PROMPT 5d, B155)", [sys.executable, "scripts/dev/test_prompt_contract.py"], "Step 3pc: Prompt contract tests")
    plan.append(Step("3ds", "DSA helper CLI tests (dsa.py)", "Step 3ds: DSA helper CLI tests", run=lambda: exec_unittest_shards("scripts/dev/test_dsa.py", gate_jobs() if gate_jobs() == 1 else 2), cmd_text="python -m unittest (scripts/dev/test_dsa.py, 2 shards)", tail=None))   # dsa.py: DSA one-call helpers (put/edit/commit/begin/end/host)
    add("3cr", "Control Room page generator tests", [sys.executable, "scripts/dev/test_make_control_room.py"], "Step 3cr: Control Room tests")
    add("3lh", "GPT lane health tests (down/up rules, reroute, pause, resume, DSA prompt)", [sys.executable, "scripts/dev/test_lane_health.py"], "Step 3lh: GPT lane health tests")
    add("3rb", "Claude-GPT relay board tests (shared notes, lanes, pack)", [sys.executable, "scripts/dev/test_relay_board.py"], "Step 3rb: Relay board tests")
    add("3af", "Artifact registry tests (one url per page per account)", [sys.executable, "scripts/dev/test_artifacts.py"], "Step 3af: Artifact registry tests")
    plan.append(Step("3bk", "Backup snapshot tests (dirty/untracked work reaches the remote)", "Step 3bk: Backup snapshot tests", run=lambda: exec_unittest_shards("scripts/dev/test_backup_snapshot.py", gate_jobs() if gate_jobs() == 1 else 2), cmd_text="python -m unittest (scripts/dev/test_backup_snapshot.py, 2 shards)", tail=None))
    add("3vd", "Verdict registry override tests (sourced hand corrections survive backfill)", [sys.executable, "scripts/dev/test_verdicts.py"], "Step 3vd: Verdict registry tests")
    add("3lm", "Live mirror tests (read-only desktop->work-tree data, fail-closed)", [sys.executable, "scripts/dev/test_live_mirror.py"], "Step 3lm: Live mirror tests")
    add("3js", "Config check (settings.json parses, hook scripts exist, secrets stay ignored)", [sys.executable, "scripts/dev/test_config_check.py"], "Step 3js: Config check")   # GATE_SPEED D5
    add("3gi", "Gate impact tests (import-graph test selection, budget, quarantine)", [sys.executable, "scripts/dev/test_gate_impact.py"], "Step 3gi: Gate impact tests")   # GATE_SPEED X1
    add("3qn", "Gate quarantine list valid (owner, reason, not expired)", [sys.executable, "scripts/dev/gate_impact.py", "--check-quarantine"], "Step 3qn: Quarantine check")   # GATE_SPEED X5

    # Step 3w: wiring gate - every unrun code file is declared in wiring_registry.json or archived (fast, in --quick too)
    add("3w", "Wiring gate tests", [sys.executable, "scripts/dev/test_wiring_scan.py"], "Step 3w: Wiring gate tests")
    add("3x", "Wiring check: no undeclared unwired code (wiring_scan.py --check)", [sys.executable, "scripts/dev/wiring_scan.py", "--check"], "Step 3x: Wiring check")
    # Step 3gd: B150 discovery in every ship (2026-10-16: two research test files shipped unregistered and turned CI red twice in 3 h;
    # the smoke gate never picked the pytest shard that holds this test)
    add("3gd", "Gate discovery: every tracked test file is gated (B150)", [sys.executable, "MyTradingSys/tests/test_gate_discovery_b150.py"], "Step 3gd: Gate discovery")
    # Step 3dl: CI deps lint (2026-10-16: pandas imported by research tests, missing from the ci.yml pip line; the desktop has every package, so
    # only CI saw ModuleNotFoundError at collection, three red rounds in 3 h). Always runs, ~5 s.
    add("3dl", "CI deps lint: no gated test hard-imports a package the ci.yml pip line lacks", [sys.executable, "scripts/dev/ci_deps_lint.py"], "Step 3dl: CI deps lint")

    # Step 4: pytest (math + doc tests), sharded so the slowest step no longer sets the gate's wall time (2026-10-16: one process
    # took 919 s of a 15 min gate). 4/4b/4c = MyTradingSys/tests files round-robin, 4d = doc size/contract tests, 4e = backtest
    # files, 4f = layer/live-writer paths. Every shard gets its own basetemp and ignores transient tmp dirs: see pytest_cmd above.
    tests_dir = REPO / "MyTradingSys" / "tests"
    doc_shard = ["MyTradingSys/tests/docs", "MyTradingSys/tests/test_relay_prompts.py"]
    top = sorted(f"MyTradingSys/tests/{f.name}" for f in tests_dir.glob("test_*.py")) if tests_dir.exists() else []
    top = [f for f in top if f not in doc_shard]
    # a new test subfolder under MyTradingSys/tests is collected wholesale, as before the split
    top += sorted(f"MyTradingSys/tests/{d.name}" for d in tests_dir.iterdir()
                  if d.is_dir() and d.name not in ("docs", "fixtures", "__pycache__") and any(d.rglob("test_*.py"))) if tests_dir.exists() else []
    # Greedy balance by measured seconds (heaviest first into the lightest shard); an unlisted file counts TEST_FILE_DEFAULT_S.
    bins = [[0, []] for _ in PYTEST_SHARD_NUMS]
    for f in sorted(top, key=lambda f: -TEST_FILE_SECONDS.get(Path(f).name, TEST_FILE_DEFAULT_S)):
        b = min(bins, key=lambda b: b[0])
        b[0] += TEST_FILE_SECONDS.get(Path(f).name, TEST_FILE_DEFAULT_S)
        b[1].append(f)
    for i, (num, (_, chunk)) in enumerate(zip(PYTEST_SHARD_NUMS, bins)):
        if chunk:
            add(num, f"Pytest shard {i + 1}/{len(bins)} (MyTradingSys/tests, {len(chunk)} files)", pytest_cmd(sorted(chunk)), f"Step {num}: Pytest tests")
    add("4d", "Pytest doc size/contract tests", pytest_cmd(doc_shard), "Step 4d: Pytest doc tests")
    add("4e", "Pytest backtest function-style tests", pytest_cmd(BACKTEST_PYTEST_PATHS), "Step 4e: Pytest backtest tests")
    add("4f", "Pytest layer + live-writer tests", pytest_cmd(PYTEST_LAYER_PATHS), "Step 4f: Pytest layer tests")

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
    cmd5c = [sys.executable, "-m", "pytest", "MyTradingSys/options/tests", "-q", "-p", "no:cacheprovider", transient_ignore_glob(),
             f"--basetemp={gate_tmp('mts_s5c_') / 'bt'}"]
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


NOT_RUN = {}   # step num -> why it did not run (fail-fast / precheck failed); results[num] is None for these


def run_plan(plan, jobs, out=None, fail_fast=False, precheck=False, slot=None, reused=None, precheck_slot=None):
    """Run the plan and print each step's block as it finishes. Independent steps run `jobs` at a time, slowest first; SERIAL_STEPS
    follow one by one; jobs == 1 runs everything in definition order. Returns {step num: True|False|None}.
    GATE_SPEED (sync.py ship only; CI, auto_deploy and a bare run pass none of these):
      precheck   CHEAP_STEPS and the targeted step run first, PRECHECK_JOBS at a time, holding precheck_slot when provided;
                 any failure there and the rest is NOT RUN (the whole precheck still runs, so every cheap failure shows at once)
      fail_fast  in the main phase, after the first failed step the steps not yet started are NOT RUN; started ones finish
      slot       zero-argument context manager (the gate slot) held around the main phase only
      reused     {num: note} of steps the pass record shows passing on this exact tree: PASS without running"""
    out = out or sys.stdout
    results = {}
    reused = reused or {}
    skipped = [s for s in plan if s.skip]
    todo = [s for s in plan if not s.skip and s.num not in reused]
    for s in skipped:
        print(f"\n[Step {s.num}] {s.desc}\nStep {s.num}: SKIP ({s.skip})", file=out, flush=True)
        results[s.num] = None
    for s in plan:
        if not s.skip and s.num in reused:
            print(f"\n[Step {s.num}] {s.desc}\nStep {s.num}: PASS ({reused[s.num]})", file=out, flush=True)
            results[s.num] = True
    t_start = time.monotonic()
    finished = [0]
    failed_first = []

    def not_run(s, why):
        NOT_RUN[s.num] = why
        results[s.num] = None
        with _LOCK:
            print(f"\n[Step {s.num}] {s.desc}\nStep {s.num}: NOT RUN ({why})", file=out, flush=True)

    def run_one(s, stop_on_fail):
        if stop_on_fail and failed_first:
            return not_run(s, f"fail-fast: step {failed_first[0]} failed")
        t0 = time.monotonic()
        try:
            ok, output = s.run()
        except Exception:   # a crashing step is a failed step, not a dead gate
            ok, output = False, traceback.format_exc()
        elapsed = time.monotonic() - t0
        record_timing(s.num, s.desc, elapsed, ok, gate_mode)
        with _LOCK:
            finished[0] += 1
            if ok is False and not failed_first:
                failed_first.append(s.num)
            progress = f"{finished[0]}/{len(todo)} done, +{time.monotonic() - t_start:.0f}s"
            print("\n".join(format_step(s.num, s.desc, s.cmd_text, ok, output, elapsed, progress, s.tail)), file=out, flush=True)
        results[s.num] = ok

    def run_steps(steps, n_jobs, stop_on_fail):
        if n_jobs <= 1:
            for s in steps:
                run_one(s, stop_on_fail)
            return
        par = [s for s in steps if s.lane == "par"]
        if any(getattr(s, "est", None) for s in par):   # fast path: longest estimated first
            par.sort(key=lambda s: -(getattr(s, "est", None) or UNIT_DEFAULT_S))
        else:
            par.sort(key=lambda s: SLOWEST_FIRST.index(s.num) if s.num in SLOWEST_FIRST else len(SLOWEST_FIRST))   # stable: the rest keep definition order
        with ThreadPoolExecutor(max_workers=n_jobs) as pool:
            list(pool.map(lambda s: run_one(s, stop_on_fail), par))
        for s in steps:
            if s.lane == "seq":
                run_one(s, stop_on_fail)

    if precheck:
        pre = [s for s in todo if s.num in CHEAP_STEPS or s.num == TARGET_STEP]
        main_steps = [s for s in todo if s not in pre]
        slot_msg = "with precheck slot" if precheck_slot else "no gate slot"
        print(f"Gate: {len(todo)} steps; precheck {len(pre)} cheap steps, {min(jobs, PRECHECK_JOBS)} at a time, {slot_msg}"
              + (f"; {len(reused)} reused from the pass record" if reused else ""), file=out, flush=True)
        with (precheck_slot() if precheck_slot else contextlib.nullcontext()):
            run_steps(pre, min(jobs, PRECHECK_JOBS), False)
        if failed_first:
            for s in main_steps:
                not_run(s, f"precheck failed: step {failed_first[0]}")
            return results
        print(f"Precheck passed in {time.monotonic() - t_start:.0f}s; main {len(main_steps)} steps, {jobs} at a time", file=out, flush=True)
    else:
        main_steps = todo
        print(f"Gate: {len(todo)} steps, {jobs} at a time" + (f"; {len(reused)} reused from the pass record" if reused else ""),
              file=out, flush=True)
    if main_steps:
        with (slot() if slot else contextlib.nullcontext()):
            run_steps(main_steps, jobs, fail_fast)
    return results


def changed_files(args):
    """The --changed-file list (one path per line), or None when absent or unreadable."""
    if "--changed-file" not in args:
        return None
    try:
        lines = Path(args[args.index("--changed-file") + 1]).read_text(encoding="utf-8").splitlines()
    except (OSError, IndexError):
        return None
    return [f.strip().replace("\\", "/") for f in lines if f.strip()]


def targeted_tests(files, root=REPO):
    """GATE_SPEED D1: MyTradingSys/tests/test_*.py files (the step-4 shard files) that changed, reference a changed module or name a
    changed non-.py file (docs too: test_relay_prompts names RELAY.md); files measured >= SLOW_FILE_S are left to their shard. Sorted,
    at most TARGET_CAP."""
    import gate_select
    tests_dir = Path(root) / "MyTradingSys" / "tests"
    if not tests_dir.exists():
        return []
    out = []
    for t in sorted(tests_dir.glob("test_*.py")):
        rel = f"MyTradingSys/tests/{t.name}"
        if TEST_FILE_SECONDS.get(t.name, 0) >= SLOW_FILE_S:
            continue
        for f in files:
            p = PurePosixPath(f)
            if rel == f or (f.endswith(".py") and p.stem not in gate_select.SHARED_STEMS and gate_select.references(p.stem, t)) \
                    or (not f.endswith(".py") and gate_select.names(p.name, t)):
                out.append(rel)
                break
    return out[:TARGET_CAP]


FAST_JOBS_MAX = 6
FAST_SLOTS = 2
FAST_COSTLY_ALWAYS = ("3w", "3tl", "3dl")   # gate_select.ALWAYS steps of 3-9 s that a fast gate runs only when the change can matter to them
FAST_ALWAYS = ("4d", "3qn")   # 4d: the doc/tree-scanning pytest tests, 3qn: the quarantine list stays valid (both seconds)
fast_applied = False
fast_info = {}


def fast_jobs():
    """Workers of the fast path: MTS_GATE_JOBS, else cpu count - 2 (the gate is pinned off the top 2 logical CPUs) within 2..FAST_JOBS_MAX."""
    try:
        n = int(os.environ.get("MTS_GATE_JOBS", ""))
    except ValueError:
        n = min(FAST_JOBS_MAX, max(2, (os.cpu_count() or 4) - 2))
    return max(1, n)


def step_test_files(s, root=REPO):
    """Repo-relative test files a pytest step covers: its file arguments and every test_*.py under its directory arguments."""
    import gate_select
    out = set()
    for p in gate_select._cmd_files(s.cmd_text, root):
        try:
            out.add(Path(p).resolve().relative_to(Path(root).resolve()).as_posix())
        except ValueError:
            pass
    return sorted(out)


def apply_fast(plan, files, nums, jobs):
    """GATE_SPEED X1/X2: replace the smoke selection of a ship (`--fast`) by the tests the import graph reaches (gate_impact.reach), kept inside
    a time budget. `nums` = what gate_select.explain picked (ALWAYS steps, doc steps, steps whose test names a changed file; its shard picks
    are replaced here). Returns (plan, info); plan None = live code imports the change, the caller runs the full gate. Raises on any
    surprise: the caller then keeps the old whole-shard smoke selection."""
    import gate_impact
    import gate_select
    import run_extra_tests
    reach = gate_impact.reach(files)
    info = {"reached": len(reach.tests), "direct": len(reach.direct), "deferred": []}
    if reach.live_hit:
        info["live_hit"] = reach.live_hit
        return None, info
    est_file = lambda f: gate_impact.estimate(f, TEST_FILE_SECONDS)   # noqa: E731
    step_est = lambda n: STEP_EST.get(n, UNIT_DEFAULT_S)              # noqa: E731
    all_nums = [s.num for s in plan]
    pytest_nums = [n for n in all_nums if n.startswith("4") and n not in FAST_ALWAYS and n != TARGET_STEP]
    steps_list = [(s.num, s.cmd_text) for s in plan]
    # ALWAYS steps that cost 3-9 s each run in a fast gate only when the change can matter to them: a file their command names, a ride-along
    # doc (task cards, INDEX/BUGS), a changed test file (CI deps lint). 3x (wiring check), 3gd (test discovery), 3qn, 4d always run.
    needed = set()
    for f in files:
        needed.update(gate_select._name_matches(f, steps_list))
        if f.endswith(".py") or f.endswith("ci.yml") or gate_impact.is_test_file(f):
            needed.add("3dl")
    if any(gate_select._is_doc(f) for f in files):
        needed.update(gate_select.DOC_STEPS)
    keep_nums = {n for n in nums if n in all_nums and n not in pytest_nums and n not in ("3xt", "5b") and (n not in FAST_COSTLY_ALWAYS or n in needed)}         | {n for n in FAST_ALWAYS if n in all_nums}
    units = {}   # key -> (estimated seconds, direct)

    def unit(key, e, direct):
        old = units.get(key)
        units[key] = (e, direct or (old[1] if old else False))

    for n in keep_nums:
        unit(("sc", n), step_est(n), True)
    pyt = {}
    for s in plan:
        if s.num in pytest_nums:
            hit = [f for f in step_test_files(s) if f in reach.tests]
            if hit:
                pyt[s.num] = hit
                for f in hit:
                    unit(("py", s.num, f), est_file(f), f in reach.direct)
    for t in reach.tests:
        for n in gate_select._name_matches(t, steps_list):
            if n not in pytest_nums and n not in ("3xt", "5b") and n not in keep_nums:
                unit(("sc", n), step_est(n), t in reach.direct)
    extras = run_extra_tests.all_tests()
    ex = {t for t in gate_select.extra_subset(files, extras) if t in extras} | {t for t in extras if t in reach.tests}
    for t in ex:
        unit(("ex", t), EXTRA_FILE_S, t in reach.direct)
    modules = find_layer_modules()
    ly = set(gate_select.layer_subset([f for f in files if not f.endswith(gate_select.DOC_SUFFIXES)], modules)) \
        | {m for m in modules if m.replace(".", "/") + ".py" in reach.tests}
    for m in ly:
        unit(("ly", m), EXTRA_FILE_S, m.replace(".", "/") + ".py" in reach.direct)
    direct = [k for k, (e, d) in units.items() if d]
    others = [k for k, (e, d) in units.items() if not d]
    workers = min(jobs, gate_impact.EFFECTIVE_WORKERS)
    kept, deferred = gate_impact.plan_budget(direct, others, lambda k: units[k][0], workers, base_s=FAST_BASE_S, budget=gate_impact.FAST_BUDGET_S)
    kept = set(kept)
    info["deferred"] = sorted(("/".join(k[1:]) for k in deferred))
    info["kept"], info["budget"] = len(kept), gate_impact.FAST_BUDGET_S
    info["est_s"] = round((FAST_BASE_S + sum(units[k][0] for k in kept)) / max(1, workers))
    deselect = gate_impact.active_deselects(gate_impact.trunk_quarantine())
    info["quarantined"] = deselect
    new_plan = []
    for s in plan:
        n = s.num
        if n == TARGET_STEP:
            continue
        if n in pytest_nums:
            fk = sorted(f for f in pyt.get(n, []) if ("py", n, f) in kept)
            if not fk:
                s.skip = "fast: no reached test in this shard" if n not in pyt else "fast: reached tests deferred to CI (budget)"
                new_plan.append(s)
                continue
            total = sum(est_file(f) for f in fk)
            chunks = gate_impact.balance(fk, est_file, max(1, min(jobs, round(total / 10) or 1)))
            for i, c in enumerate(chunks):
                if sum(len(f) + 1 for f in c) > 24000:      # Windows command line limit is 32 KB: fall back to the whole-shard smoke gate
                    raise ValueError(f"fast gate: {len(c)} test files do not fit one command line")
                ds =[d for d in deselect if d.split("::")[0] in c]
                step = Step(n if i == 0 else f"{n}.{i}", f"Pytest (fast): {len(c)} of {len(step_test_files(s))} files that the change reaches"
                            + (f" (chunk {i + 1}/{len(chunks)})" if len(chunks) > 1 else ""), s.label, cmd=pytest_cmd(c, deselect=ds))
                step.est = sum(est_file(f) for f in c) + 1
                new_plan.append(step)
            continue
        if n == "3xt":
            sub = [t for t in extras if ("ex", t) in kept]
            if sub:
                s = Step("3xt", f"Extra tests the change reaches ({len(sub)} of {len(extras)} files)", s.label,
                         cmd=[sys.executable, "scripts/dev/run_extra_tests.py", "--only", *sub])
                s.est = len(sub) * EXTRA_FILE_S / 2
            else:
                s.skip = "fast: no extra test reached (CI runs it)"
            new_plan.append(s)
            continue
        if n == "5b":
            sub = [m for m in modules if ("ly", m) in kept]
            if sub:
                s = Step("5b", f"Layer tests the change reaches ({len(sub)} of {len(modules)} modules)", s.label, tail=None,
                         run=(lambda sub=sub, jobs=jobs: exec_layer_chunks(sub, jobs)), key=",".join(sub), cmd_text=f"python -m unittest ({len(sub)} modules)")
                s.est = len(sub) * EXTRA_FILE_S / 2
            else:
                s.skip = "fast: no layer test reached (CI runs it)"
            new_plan.append(s)
            continue
        if n in keep_nums or ("sc", n) in kept:
            s.est = step_est(n)
        elif ("sc", n) in units:
            s.skip = "fast: reached but deferred to CI (budget)"
        else:
            s.skip = "fast: not reached by the change (CI runs it)"
        new_plan.append(s)
    return new_plan, info


def apply_selection(plan, args):
    """--changed-file F (one path per line, vs origin/fast-track) with --smoke: skip the steps gate_select.select does not pick.
    --smoke without --changed-file, or an unreadable file, runs everything (fail closed). Returns (plan, mode or None).
    GATE_SPEED D6: a smoke/docs 3xt runs only gate_select.extra_subset, a smoke 5b only gate_select.layer_subset.
    D1: with --precheck and a readable list, the targeted step 4t is added (every mode)."""
    files = changed_files(args)
    if "--precheck" in args and files:
        tt = targeted_tests(files)
        if tt:
            plan.append(Step(TARGET_STEP, f"Precheck pytest: {len(tt)} test file(s) that reference the change", f"Step {TARGET_STEP}: Targeted pytest",
                             cmd=pytest_cmd(tt)))
    if "--smoke" not in args or files is None:
        return plan, None
    import gate_select
    import run_extra_tests
    global gate_reason, gate_mode
    extras, modules = run_extra_tests.all_tests(), find_layer_modules()
    mode, nums, gate_reason = gate_select.explain(files, [(s.num, s.cmd_text) for s in plan], step_files={"3xt": extras, "5b": modules})
    gate_mode = mode
    if mode == "full":
        return plan, mode
    global fast_applied, fast_info
    if "--fast" in args and mode == "smoke":
        try:
            new_plan, info = apply_fast(plan, files, nums, fast_jobs())
        except Exception as e:   # any surprise: the old whole-shard smoke selection below (a larger, slower set)
            for s in plan:
                if str(s.skip).startswith("fast:"):
                    s.skip = None
            print(f"fast path unavailable ({type(e).__name__}: {e}); using the whole-shard smoke selection", flush=True)
        else:
            fast_info = info
            if new_plan is None:
                gate_reason = f"full: live code imports the change ({', '.join(info['live_hit'][:3])})"
                gate_mode = "full"
                return plan, "full"
            fast_applied = True
            return new_plan, mode
    for s in plan:
        if s.num not in nums and not s.skip and s.num != TARGET_STEP:
            s.skip = f"not selected by the {mode} gate (CI runs it)"
    for i, s in enumerate(plan):
        if s.skip:
            continue
        if s.num == "3xt":
            sub = gate_select.extra_subset(files, extras)
            plan[i] = Step("3xt", f"Extra tests the change reaches ({len(sub)} of {len(extras)} files)", s.label,
                           cmd=[sys.executable, "scripts/dev/run_extra_tests.py", "--only", *sub])
        elif s.num == "5b":
            sub = gate_select.layer_subset(files, modules)
            jobs = gate_jobs()
            plan[i] = Step("5b", f"Layer tests the change reaches ({len(sub)} of {len(modules)} modules)", s.label, tail=None,
                           run=(lambda sub=sub, jobs=jobs: exec_layer_chunks(sub, jobs)), key=",".join(sub),
                           cmd_text=f"python -m unittest ({len(sub)} modules)")
    return plan, mode


def _git_out(root, *args):
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip())
    return r.stdout


def tree_state(root=REPO):
    """(HEAD tree id, clean): clean = `git status --porcelain` shows nothing (untracked files count, ignored ones do not; the
    pulled live mirror is regenerable noise). A dirty tree never writes or reads the pass record: the gate ran on files HEAD lacks."""
    tree = _git_out(root, "rev-parse", "HEAD^{tree}").strip()
    rows = [r for r in _git_out(root, "status", "--porcelain").splitlines() if r.strip() and "runtime_data/_mirror" not in r]
    return tree, not rows


def record_path(root=REPO):
    return Path(_git_out(root, "rev-parse", "--absolute-git-dir").strip()) / RECORD_NAME


def load_reused(plan, root=REPO, now=None):
    """GATE_SPEED D3 (same-tree retry only, reviewers 2026-10-18): {num: note} for selected steps the record shows PASSING on this exact,
    clean tree with the same step signature, written by the same python less than RECORD_MAX_AGE_S ago. Anything else (other tree, dirty
    tree, unreadable record, other python) = {}: run everything selected. Typical hit: a push that failed after ALL TESTS PASSED, or a
    rerun after one flaky step (only the failed step runs again)."""
    try:
        tree, clean = tree_state(root)
        rec = json.loads(record_path(root).read_text(encoding="utf-8"))
        if not clean or rec.get("tree") != tree or rec.get("python") != sys.version:
            return {}
        if (now or time.time()) - float(rec.get("epoch", 0)) > RECORD_MAX_AGE_S:
            return {}
        passed = rec.get("passed", {})
        return {s.num: f"reused: passed on this tree {rec.get('utc', '?')}" for s in plan
                if not s.skip and passed.get(s.num) == s.sig()}
    except Exception:
        return {}


def save_record(plan, results, root=REPO, start_tree=None, deferred=None):
    """Write the passing steps of this run (and the still-valid passes of the same tree) to the record. Skipped when the tree is dirty or
    HEAD moved while the gate ran (a session edited or committed mid-gate). Atomic (temp + os.replace, 3 tries on a Windows lock); never
    raises: a record that cannot be written only costs a rerun."""
    try:
        tree, clean = tree_state(root)
        if not clean or (start_tree and tree != start_tree):
            return False
        path = record_path(root)
        passed = {}
        old = {}
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
            if old.get("tree") == tree and old.get("python") == sys.version:
                passed = dict(old.get("passed", {}))
        except Exception:
            pass
        for s in plan:
            if results.get(s.num) is True:
                passed[s.num] = s.sig()
            elif results.get(s.num) is False:
                passed.pop(s.num, None)
        row = {"tree": tree, "python": sys.version, "epoch": time.time(), "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "passed": passed}
        if deferred is not None:
            row["deferred"] = list(deferred)
        elif old.get("tree") == tree and "deferred" in old:
            row["deferred"] = old["deferred"]
        tmp = path.with_name(f"{RECORD_NAME}.{os.getpid()}.tmp")
        with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(row, fh)
        for i in range(3):
            try:
                os.replace(tmp, path)
                return True
            except PermissionError:
                time.sleep(0.5 * (i + 1))
        os.unlink(tmp)
    except Exception:
        pass
    return False


def lower_priority():
    """Run the gate (and every child it starts, which inherit the class) below normal priority on Windows.
    2026-10-16: parallel sessions' gates (4 steps at a time each) kept the 8-core live host at 100% CPU; the loop's mvn
    snapshot then took > 90 s, the supervisor restarted the loop over and over and live health went RED. The live loop
    and its feeds run at normal priority, so they now win against any gate. MTS_GATE_PRIORITY=normal opts out."""
    if sys.platform != "win32" or os.environ.get("MTS_GATE_PRIORITY", "").lower() == "normal":
        return False
    try:
        import ctypes
        from ctypes import wintypes
        k = ctypes.WinDLL("kernel32", use_last_error=True)
        k.GetCurrentProcess.restype = wintypes.HANDLE
        k.SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        ok = bool(k.SetPriorityClass(k.GetCurrentProcess(), 0x00004000))   # BELOW_NORMAL_PRIORITY_CLASS
        reserve_cores(k)
        return ok
    except Exception:
        return False


RESERVED_CPUS = 2


def reserve_cores(k=None):
    """B191: priority only orders who runs first; it cannot stop a gate from filling every logical CPU. Pin the gate (children
    inherit the mask) off the top RESERVED_CPUS logical CPUs, so the live loop's snapshot JVM always has one physical core
    (i7-4770K: 4 cores / 8 threads, cpus 6-7 are one core) no matter how many sessions gate at once. MTS_GATE_RESERVE=0 opts out."""
    n = os.cpu_count() or 1
    try:
        reserve = int(os.environ.get("MTS_GATE_RESERVE", RESERVED_CPUS))
    except ValueError:
        reserve = RESERVED_CPUS
    if sys.platform != "win32" or reserve <= 0 or n < reserve + 2:
        return False
    try:
        import ctypes
        from ctypes import wintypes
        k = k or ctypes.WinDLL("kernel32", use_last_error=True)
        k.GetCurrentProcess.restype = wintypes.HANDLE
        k.SetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.c_size_t]
        return bool(k.SetProcessAffinityMask(k.GetCurrentProcess(), (1 << (n - reserve)) - 1))
    except Exception:
        return False


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    unbuffer()
    lower_priority()
    isolate_pytest_tmp()
    quick = "--quick" in args

    plan = build_plan(quick)
    plan, mode = apply_selection(plan, args)
    if mode:
        print(f"Gate mode: {mode} ({sum(1 for s in plan if not s.skip)} steps); CI runs the full suite behind the push", flush=True)
        print(f"Gate reason: {gate_reason}", flush=True)
    global STEP_TIMEOUT_S
    if fast_applied:
        STEP_TIMEOUT_S = FAST_STEP_TIMEOUT_S
        print(f"Fast gate (GATE_SPEED X2): {fast_info['reached']} test files reached ({fast_info['direct']} direct), {fast_info['kept']} units kept, "
              f"estimated {fast_info['est_s']} s (budget {fast_info['budget']} s) on {fast_jobs()} workers; {len(fast_info['deferred'])} deferred to CI (budget)", flush=True)
        if fast_info["deferred"]:
            print(f"  DEFERRED to CI ({len(fast_info['deferred'])}): " + ", ".join(fast_info["deferred"]), flush=True)
        if fast_info["quarantined"]:
            print("  QUARANTINED (deselected here, CI runs them): " + ", ".join(fast_info["quarantined"]), flush=True)
    # GATE_SPEED: the ship-only flags (sync.run_gate passes them; CI, auto_deploy and daily_hygiene never do)
    use_record = "--record" in args and not os.environ.get("CI")
    start_tree, reused = None, {}
    if use_record:
        try:
            start_tree = tree_state()[0]
        except Exception:
            use_record = False
        reused = load_reused(plan) if use_record else {}
    slot = None
    precheck_slot = None
    if "--slot" in args and mode not in ("docs", "none"):
        import sync
        if fast_applied:   # own pool: a fast gate never queues behind the 9-minute full gates
            slot = lambda: sync.gate_slot(REPO, slots=FAST_SLOTS, name="gate-slots-fast")   # noqa: E731
        else:
            slot = lambda: sync.gate_slot(REPO)   # noqa: E731 - the slot is taken after the precheck, released when the main phase ends
            precheck_slot = lambda: sync.gate_slot(REPO, slots=sync.GATE_PRECHECK_SLOTS, name="gate-slots-precheck")   # noqa: E731
    results = run_plan(plan, fast_jobs() if fast_applied else gate_jobs(), fail_fast="--fail-fast" in args,
                       precheck="--precheck" in args and not fast_applied, slot=slot, reused=reused, precheck_slot=precheck_slot)
    if use_record:
        save_record(plan, results, start_tree=start_tree, deferred=fast_info.get("deferred") if fast_applied else None)

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
        elif s.num in NOT_RUN:
            print(f"{s.label}: NOT RUN ({NOT_RUN[s.num]})")
        else:
            print(f"{s.label}: SKIP")

    print("=" * 70)
    if not failed and NOT_RUN:   # fail closed: a step that did not run never counts as a pass
        failed = [s.label for s in plan if s.num in NOT_RUN]
    if failed:
        print(f"FAILED: {len(failed)} step(s)")
        for f in failed:
            print(f"  - {f}")
        if os.environ.get("GITHUB_ACTIONS"):   # one line that names every failed step, whatever the per-step annotations were (cap: 10 per step)
            print(f"::error title=Gate FAIL::{len(failed)} step(s) failed: " + "; ".join(failed).replace("%", "%25"))
        return 1
    else:
        print("ALL TESTS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
