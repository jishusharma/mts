#!/usr/bin/env python
"""run_extra_tests.py - run the tracked test files that live outside the dirs the main gate collects (B150).

Each slow file (SLOW_FIRST) runs in its own pytest process; the fast files of a directory share one (run_group; a red group is re-run per file). Each process runs with the file's directory as cwd (the way each was written to run), so same-named
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
EXTRA_TSV = Path(__file__).resolve().with_name("extra_tests.tsv")


def load_extra(path=EXTRA_TSV):
    """The registered extra tests: one path per line of extra_tests.tsv (blank and # lines skipped). A missing file raises."""
    return [ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.lstrip().startswith("#")]


EXTRA = load_extra()
STUDY_ROOT = "MyTradingSys/research/"


def discovered(repo=None):
    """Tracked test_*.py under a study folder that EXTRA does not list and run_all_tests.py does not name: they run
    without a hand-kept entry (2026-10-17 audit: the two-list registration cost ~100 commits and several red gates in 72 h)."""
    repo = Path(repo or REPO)
    out = subprocess.run(["git", "ls-files", "--", STUDY_ROOT], cwd=repo, capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout.splitlines()
    gate_py = repo / "scripts" / "dev" / "run_all_tests.py"
    gate = gate_py.read_text(encoding="utf-8") if gate_py.exists() else ""
    return sorted(p for p in out if p.endswith(".py") and Path(p).name.startswith("test_") and "archive" not in p.lower()
                  and p not in EXTRA and f'"{Path(p).stem}"' not in gate and f"{Path(p).stem}.py" not in gate)


def all_tests(repo=None):
    return EXTRA + discovered(repo)


JOBS_MAX = 8   # OURS 2026-11-11: default cap; half the logical CPUs above 8 (12 on JIS-NUC -> 6), never under the old min(4, cpu)


def jobs(cpu=None):
    """Concurrent pytest processes: MTS_GATE_JOBS (the gate's knob), else min(JOBS_MAX, max(min(4, cpu), cpu // 2)):
    4 on a 4- to 8-CPU box as before, 6 on the 12-CPU NUC (3xt measured 245 s wall at 4 jobs, 2026-11-11)."""
    try:
        n = int(os.environ.get("MTS_GATE_JOBS", ""))
    except ValueError:
        cpu = cpu or os.cpu_count() or 1
        n = min(JOBS_MAX, max(min(4, cpu), cpu // 2))
    return max(1, n)


# OURS: seconds per file measured 2026-11-11 on JIS-NUC (GATE_SLOW_STEPS.md, 4 jobs, idle); every other file is about 2 s.
# These start first so the pool does not end on one 60 s file running alone. Order only: every file still runs.
SLOW_FIRST = {
    "scripts/dev/test_planted_error_trial.py": 65,
    "MyTradingSys/research/context_factors_2026-10-16/test_context_asof.py": 56,
    "MyTradingSys/tools/live_aid/test_live_aid.py": 46,
    "MyTradingSys/tools/live_aid/test_live_aid_replay.py": 43,
    "MyTradingSys/research/context_factors_pit_2026-10-16/test_context_asof.py": 37,
    "scripts/dev/test_lab_query.py": 27,
}


def slowest_first(rels):
    """`rels` with the SLOW_FIRST files first (slowest leading), the rest in their list order; same files, each once."""
    return sorted(rels, key=lambda r: -SLOW_FIRST.get(r, 0))


def child_env(repo=None):
    """Environment for a test child: the repo root appended after any existing PYTHONPATH, so a test run from its own folder can
    still import repo-root packages (`from MyTradingSys...`)."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(p for p in (env.get("PYTHONPATH"), str(repo or REPO)) if p)
    return env


FILE_TIMEOUT_S = 600   # OURS: ceiling per extra test file; a file still running at it = hung, it fails and frees its slot. Was 300 (all took < 60 s): under 3 gates at once test_planted_error_trial ran 212 s and failed 3xt on 2 ships 2026-11-11 (audit)


def run_one(rel, basetemp, timeout=None):
    """(ok, one-line result) for one extra test file: its own pytest process, cwd and basetemp. A file past `timeout`
    (FILE_TIMEOUT_S) fails as 'timed out'. A child that dies with no output at all (2026-11-10: a native crash while pytest
    imported numpy/pandas at collection, one CI shard; the re-run of the same commit passed) is run once more."""
    p = REPO / rel
    if not p.exists():
        return False, "missing"
    limit = timeout or FILE_TIMEOUT_S
    for attempt in (1, 2):
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", p.name, "-q", "-p", "no:cacheprovider", f"--basetemp={basetemp}"],
                               cwd=p.parent, capture_output=True, text=True, errors="replace", env=child_env(), timeout=limit, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except subprocess.TimeoutExpired:
            return False, f"timed out after {limit}s (hung; killed)"
        if r.returncode == 0 or (r.stdout or "").strip() or attempt == 2:
            break
    tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
    if r.returncode != 0:
        tail += failure_detail(r.stdout, r.stderr)
    return r.returncode == 0, tail


def failure_detail(stdout, stderr, n=30):
    """Last `n` lines of a failed file's pytest output, indented under its FAIL line, so a CI log shows the cause (2026-10-16:
    five files failed on the runners with only '1 error in 0.6s' in the log and passed on every desktop)."""
    lines = (stdout or "").strip().splitlines()[-n:] + (stderr or "").strip().splitlines()[-10:]
    return "".join(chr(10) + "        | " + ln[:300] for ln in lines)


GROUP_MAX = 12   # OURS 2026-11-11: files per merged pytest process; keeps several groups per dir so the pool stays busy


def plan_units(rels, group_max=GROUP_MAX):
    """Split `rels` into run units: ("one", rel) for a SLOW_FIRST file (its time is known to be large) and ("group", dir, [rels])
    for the other files of one directory, at most `group_max` per group (most of the ~400 files take under 1 s, so their wall is
    pytest start-up; one process per group pays it once). A group of one is a plain "one". Same files, each exactly once;
    slow singles lead (slowest first), then the groups in list order. Anything unexpected -> the caller runs per file."""
    units, by_dir = [], {}
    for rel in slowest_first(rels):
        if rel in SLOW_FIRST:
            units.append(("one", rel))
        else:
            by_dir.setdefault(str(Path(rel).parent), []).append(rel)
    for d, files in by_dir.items():
        for i in range(0, len(files), group_max):
            chunk = files[i:i + group_max]
            units.append(("group", d, chunk) if len(chunk) > 1 else ("one", chunk[0]))
    return units


_REPORTED = {"PASSED", "SKIPPED", "XFAIL", "XPASS"}   # -rA short-summary words; a file with none of them collected no test


def run_group(rels, basetemp, timeout=None):
    """{rel: (ok, line)} for files of ONE directory run in one pytest process (cwd = that dir, one start-up). Only an all-green
    group (exit 0, output present) is accepted as it stands; any failure, timeout, crash or missing file makes the group
    undecidable and every file is re-run alone with run_one, so a failure is still reported by file name with its own detail and
    the per-file timeout is unchanged (the group gets one ceiling for the lot; past it, each file gets its own)."""
    paths = [REPO / r for r in rels]
    if all(p.exists() for p in paths) and len({p.parent for p in paths}) == 1:
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", *[p.name for p in paths], "-q", "-rA", "-p", "no:cacheprovider", f"--basetemp={basetemp}"],
                               cwd=paths[0].parent, capture_output=True, text=True, errors="replace", env=child_env(),
                               timeout=timeout or FILE_TIMEOUT_S, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            seen = {ln.split("::")[0].split()[-1] for ln in (r.stdout or "").splitlines() if "::" in ln and ln.split(None, 1)[0] in _REPORTED}
            if r.returncode == 0 and (r.stdout or "").strip() and all(p.name in seen for p in paths):   # a file with no test (exit 5 alone) must not hide in a green group
                tail = (r.stdout.strip().splitlines() or [""])[-1]
                return {rel: (True, f"{tail} (grouped x{len(rels)})") for rel in rels}
        except subprocess.TimeoutExpired:
            pass
    return {rel: run_one(rel, Path(basetemp) / f"f{i}", timeout) for i, rel in enumerate(rels)}


def run_files(rels, n_jobs, one=run_one, tmp=None, many=None):
    """Run every file `n_jobs` at a time and print one flushed line per file as it finishes. Returns the failures in list order.
    `many` (run_group in main) merges the fast files of a directory into one process; None = one process per file."""
    # Own basetemp per file: pytest's default %TEMP%/pytest-of-<user>/pytest-current cleanup raises PermissionError
    # (exit 1 after all tests pass) when another account left that link behind (JIS-NB 2026-10-14); it is also what lets
    # the files run beside each other.
    tmp = Path(tmp or tempfile.mkdtemp(prefix="mts_xt_"))
    lock = threading.Lock()
    done = {}

    def report(rel, ok, tail):
        with lock:
            print(f"{'ok  ' if ok else 'FAIL'} {rel}: {tail}", flush=True)
        done[rel] = (ok, tail)

    def work(item):
        i, unit = item
        if unit[0] == "group":
            try:
                res = many(unit[2], tmp / str(i))
            except Exception:   # fail closed: undecidable grouping -> the per-file run
                res = {rel: one(rel, tmp / f"{i}_{j}") for j, rel in enumerate(unit[2])}
            for rel in unit[2]:
                report(rel, *res[rel])
        else:
            report(unit[1], *one(unit[1], tmp / str(i)))

    units = plan_units(rels) if many else [("one", r) for r in slowest_first(rels)]
    with ThreadPoolExecutor(max_workers=max(1, n_jobs)) as pool:
        list(pool.map(work, enumerate(units)))
    return [f"{rel}: missing" if done[rel][1] == "missing" else rel for rel in rels if not done[rel][0]]


def pick(argv, tests):
    """`--only A B ...` (the smoke gate's subset, GATE_SPEED D6): those of `tests`, in list order; a name not in `tests` is an error
    (a typo must not pass as 'nothing to run'). No --only: every test."""
    if "--only" not in argv:
        return list(tests)
    want = [a.replace("\\", "/") for a in argv[argv.index("--only") + 1:]]
    unknown = [w for w in want if w not in tests]
    if unknown:
        raise SystemExit(f"run_extra_tests: not an extra test: {', '.join(unknown)}")
    return [t for t in tests if t in want]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    try:
        sys.stdout.reconfigure(line_buffering=True, errors="replace")
    except (AttributeError, ValueError):
        pass
    tests = pick(argv, all_tests())
    tmp = Path(tempfile.mkdtemp(prefix="mts_xt_"))
    try:
        bad = run_files(tests, jobs(), tmp=tmp, many=run_group)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"extra tests ({len(tests)} files): " + ("FAIL " + ", ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
