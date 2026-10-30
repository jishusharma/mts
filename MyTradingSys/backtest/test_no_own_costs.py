"""No study defines its own fee or slippage constant (T06-F2, card fix-single-cost-module).

Scans tracked *.py under backtest/ and research/ for a module-level-looking assignment of a numeric literal to a name that
contains fee, slip, taker or maker (FEE = 0.001, FEE_RT = 0.0012, slip_bps = 2). Any file outside cost_allowlist.txt fails.
The allowlist is frozen: the 57+ existing offenders are listed, not edited. New code imports MyTradingSys/backtest/fees.py.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ALLOWLIST = HERE / "cost_allowlist.txt"
ROOTS = ("MyTradingSys/backtest", "MyTradingSys/research")
SKIP_DIR = "dsa_backtest_audit_2026-10-16"
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
ASSIGN = re.compile(rf"^[ \t]*([A-Za-z_]\w*)[ \t]*(?::[^=\n]+)?=[ \t]*(?:{NUM}[ \t]*(?:#.*)?$|\d[\d.eE+-]*[ \t]*[*/])", re.M)
KEY = re.compile(r"fee|slip|taker|maker", re.I)


def load_allowlist(path=ALLOWLIST):
    return {ln.strip() for ln in Path(path).read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.lstrip().startswith("#")}


def own_cost_names(text):
    return [m.group(1) for m in ASSIGN.finditer(text) if KEY.search(m.group(1))]


def scan(files, root):
    """files: repo-relative paths. Returns {path: [names]} for files that define a cost constant."""
    out = {}
    for rel in files:
        name = rel.rsplit("/", 1)[-1]
        if (not rel.endswith(".py") or name.startswith("test_") or SKIP_DIR in rel or rel == "MyTradingSys/backtest/fees.py"
                or not rel.startswith(ROOTS)):
            continue
        p = Path(root) / rel
        if p.is_file():
            names = own_cost_names(p.read_text(encoding="utf-8", errors="replace"))
            if names:
                out[rel] = names
    return out


def offenders(files, root, allow):
    return sorted(set(scan(files, root)) - set(allow))


def tracked(repo=REPO):
    return subprocess.run(["git", "-C", str(repo), "ls-files", "--", *ROOTS], capture_output=True, text=True).stdout.split("\n")


def test_trunk_has_no_new_own_cost_file():
    bad = offenders([f for f in tracked() if f], REPO, load_allowlist())
    assert not bad, "own fee/slippage constant outside cost_allowlist.txt (import MyTradingSys/backtest/fees.py): " + ", ".join(bad)


def test_planted_fee_file_fails(tmp_path):
    f = tmp_path / "MyTradingSys/research/new_study/study.py"
    f.parent.mkdir(parents=True)
    f.write_text("FEE = 0.001\n", encoding="utf-8")
    assert offenders(["MyTradingSys/research/new_study/study.py"], tmp_path, set()) == ["MyTradingSys/research/new_study/study.py"]


def test_planted_rt_line_passes_only_when_allowlisted(tmp_path):
    rel = "MyTradingSys/backtest/x/run.py"
    f = tmp_path / rel
    f.parent.mkdir(parents=True)
    f.write_text("import os\nFEE_RT = 0.0012\n", encoding="utf-8")
    assert offenders([rel], tmp_path, set()) == [rel]
    assert offenders([rel], tmp_path, {rel}) == []


def test_clean_import_file_passes(tmp_path):
    rel = "MyTradingSys/research/s/study.py"
    f = tmp_path / rel
    f.parent.mkdir(parents=True)
    f.write_text("from MyTradingSys.backtest import fees\nRT = 2 * fees.DERIBIT_TAKER\nN_FEES = len(x)\n", encoding="utf-8")
    assert offenders([rel], tmp_path, set()) == []


def test_allowlist_covers_audit_csv_offenders():
    import csv
    p = REPO / "MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/costs.csv"
    rows = list(csv.DictReader(p.open(newline="", encoding="utf-8")))
    need = {r["file"] for r in rows if r["imports_fees"] == "0" and r["kind"] == "assign" and (REPO / r["file"]).exists()}
    assert need <= load_allowlist(), sorted(need - load_allowlist())


def test_allowlist_has_no_stale_paths():
    gone = [a for a in load_allowlist() if not (REPO / a).exists()]
    assert not gone, gone


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
