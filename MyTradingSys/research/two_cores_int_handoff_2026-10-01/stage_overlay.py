"""stage_overlay.py DEST [--prefix P ...]

Copy the repo (no .git, no __pycache__) to DEST, then for every staged file X.new in the repo (restricted to the given
repo-relative path prefixes if any) copy it over X inside DEST. Nothing in the repo is written. Use it to run tests
against "what the tree would look like after promotion":
    python $SP/stage_overlay.py $SP/ov_w1 --prefix MyTradingSys/runtime --prefix scripts/dev
    cd $SP/ov_w1 && python -m pytest MyTradingSys/tests -q
"""
import shutil, sys
from pathlib import Path

import os
REPO = Path(os.environ.get("MTS_REPO", "/home/user/mts"))

def main(argv):
    dest = Path(argv[0]); prefixes = []
    it = iter(argv[1:])
    for a in it:
        if a == "--prefix":
            prefixes.append(next(it).replace("\\", "/").rstrip("/") + "/")
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(REPO, dest, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
    n = 0
    for p in sorted(REPO.rglob("*.new")):
        rel = p.relative_to(REPO).as_posix()
        if ".git/" in rel:
            continue
        if prefixes and not any(rel.startswith(x) for x in prefixes):
            continue
        shutil.copy(p, dest / rel[:-4])
        (dest / rel).unlink()
        n += 1
        print("overlay:", rel[:-4])
    print(f"{n} staged file(s) applied -> {dest}")

if __name__ == "__main__":
    main(sys.argv[1:])
