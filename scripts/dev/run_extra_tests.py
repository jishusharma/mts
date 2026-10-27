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
    out = subprocess.run(["git", "ls-files", "--", STUDY_ROOT], cwd=repo, capture_output=True, text=True).stdout.splitlines()
    gate_py = repo / "scripts" / "dev" / "run_all_tests.py"
    gate = gate_py.read_text(encoding="utf-8") if gate_py.exists() else ""
    return sorted(p for p in out if p.endswith(".py") and Path(p).name.startswith("test_") and "archive" not in p.lower()
                  and p not in EXTRA and f'"{Path(p).stem}"' not in gate and f"{Path(p).stem}.py" not in gate)


def all_tests(repo=None):
    return EXTRA + discovered(repo)


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
    tail = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
    if r.returncode != 0:
        tail += failure_detail(r.stdout, r.stderr)
    return r.returncode == 0, tail


def failure_detail(stdout, stderr, n=30):
    """Last `n` lines of a failed file's pytest output, indented under its FAIL line, so a CI log shows the cause (2026-10-16:
    five files failed on the runners with only '1 error in 0.6s' in the log and passed on every desktop)."""
    lines = (stdout or "").strip().splitlines()[-n:] + (stderr or "").strip().splitlines()[-10:]
    return "".join(chr(10) + "        | " + ln[:300] for ln in lines)


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
    bad = run_files(tests, jobs(), tmp=tmp)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"extra tests ({len(tests)} files): " + ("FAIL " + ", ".join(bad) if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
