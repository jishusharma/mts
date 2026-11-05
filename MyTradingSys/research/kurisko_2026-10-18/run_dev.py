"""DEV event study for the frozen Kurisko PRE_REG cells (card kurisko-dev-event-study). One run only.

The guard runs before any bar is read and refuses when: the PRE_REG commit does not precede this run (PRE_REG.md
uncommitted or modified), the PRE_REG freezes 0 cells, a requested cell is not in the frozen list, a DEV data file sha
differs from DATA_MANIFEST.csv, or a run receipt already exists. The loader refuses any bar >= 2024-07-01
(count_events.load_1m). Net R follows FORMULAS 13: net = gross - cost_rt - side * funding; R = net / stop.

PRE_REG 2026-10-18 freezes 0 of 8 cells, so this script exits 2 at the guard and reads no outcome.
Usage: python run_dev.py [--cell 5m:stoch:long ...]
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import count_events as ce  # noqa: E402

PRE_REG = HERE / "PRE_REG.md"
RECEIPT = HERE / "run_receipt.json"
SEED = 20261018   # PRE_REG has no seed (0 frozen cells); only used if a later PRE_REG freezes cells and names its own


class GuardError(Exception):
    pass


def frozen_cells(text):
    """Frozen cells as 'tf:arm:side'; a 'Frozen cells: 0 of N' header means none. A frozen list is a line
    'Frozen: 5m:stoch:long, ...' written by the PRE_REG author."""
    m = re.search(r"Frozen:\s*([0-9a-z:, ]+)$", text, re.M)
    if m:
        return sorted(c.strip() for c in m.group(1).split(",") if c.strip())
    if re.search(r"Frozen cells:\s*0 of \d+", text):
        return []
    raise GuardError("PRE_REG states no frozen-cell list")


def pre_reg_committed(path=PRE_REG, root=ROOT):
    """sha of the last commit touching PRE_REG.md, or None when it is uncommitted / modified in the tree."""
    rel = Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--", rel], capture_output=True, text=True).stdout
    sha = subprocess.run(["git", "-C", str(root), "log", "-1", "--format=%H", "--", rel], capture_output=True, text=True).stdout
    return None if dirty.strip() or not sha.strip() else sha.strip()


def check_data(files, manifest_sha):
    for f in files:
        h = hashlib.sha256(Path(f).read_bytes()).hexdigest()
        if h != manifest_sha.get(Path(f).name):
            raise GuardError(f"data sha of {Path(f).name} differs from the PRE_REG manifest")


def guard(text, cells, pre_reg_sha, receipt, files=(), manifest_sha=None):
    if not pre_reg_sha:
        raise GuardError("PRE_REG.md is not committed before this run")
    if Path(receipt).exists():
        raise GuardError(f"run receipt exists ({Path(receipt).name}): one run per PRE_REG")
    frozen = frozen_cells(text)
    if not frozen:
        raise GuardError("PRE_REG freezes 0 cells: nothing may be run")
    if sorted(cells or frozen) != frozen:
        raise GuardError(f"cells {sorted(cells)} differ from the frozen list {frozen}")
    if manifest_sha is not None:
        check_data(files, manifest_sha)
    return frozen


def load_dev(files, check_sha=True):
    return ce.load_1m(files, check_sha)


def net_r(side, p_in, p_out, stop_frac, cost_rt, funding_rates=()):
    """FORMULAS 13 net return over the stop width (1 R = stop_frac of entry). side 'long'/'short'."""
    s = 1 if side == "long" else -1
    net = s * (p_out - p_in) / p_in - cost_rt - s * sum(funding_rates)
    return net / stop_frac


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", action="append", default=[])
    a = ap.parse_args(argv)
    try:
        guard(PRE_REG.read_text(encoding="utf-8"), a.cell, pre_reg_committed(), RECEIPT)
    except GuardError as e:
        print(f"REFUSED: {e}")
        return 2
    raise SystemExit("frozen cells present: the outcome run needs its PRE_REG outcome definitions; not built (no cell frozen)")


if __name__ == "__main__":
    sys.exit(main())
