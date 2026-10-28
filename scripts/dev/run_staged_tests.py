"""Run tests against STAGED (.new) code without touching the tree.

Copies every *.py and *.py.new from the given source dirs into one temp dir,
the .new version winning over the live name (foo.py.new -> foo.py), plus any
*.json next to them, then runs the given test modules (or scripts) there.

Usage (repo root):
  python scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline -- test_gh_retry_offline test_gh_executor_offline
  python scripts/dev/run_staged_tests.py MyTradingSys/execution MyTradingSys/execution/testnet/offline --script test_g1g2_offline.py --fake fake_deribit_orders.py=deribit_orders.py
Nothing in the repo is written. Exit code = test exit code.
"""
import shutil, subprocess, sys, tempfile
from pathlib import Path

def main(argv):
    script, fakes, dirs, tests = None, [], [], []
    it = iter(argv); after = False
    for a in it:
        if after: tests.append(a)
        elif a == "--": after = True
        elif a == "--script": script = next(it)
        elif a == "--fake": fakes.append(next(it).split("=", 1))
        else: dirs.append(Path(a))
    tmp = Path(tempfile.mkdtemp(prefix="staged_tests_"))
    for d in dirs:
        for p in sorted(d.glob("*.py")) + sorted(d.glob("*.json")):
            shutil.copy(p, tmp / p.name)
        for p in sorted(d.glob("*.py.new")):          # .new overrides live
            shutil.copy(p, tmp / p.name[:-4])
    for src, dst in fakes:                            # e.g. fake module stands in for the real one
        shutil.copy(tmp / src, tmp / dst)
    cmd = [sys.executable, script] if script else [sys.executable, "-m", "unittest", "-v", *tests]
    print(f"[run_staged_tests] {tmp}: {' '.join(cmd[1:])}")
    import os
    try:
        return subprocess.call(cmd, cwd=tmp, env={**os.environ, "MTS_REPO_ROOT": str(Path.cwd())})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
