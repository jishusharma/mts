import ast
import csv
from pathlib import Path

import pytest

SRC = (Path(__file__).parent / "study.py").read_text(encoding="utf-8")


def _load():
    """Extract guard_phases without importing study.py (no data load, no numpy needed)."""
    tree = ast.parse(SRC)
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "guard_phases"]
    assert fn, "guard_phases missing"
    ns = {"csv": csv, "Path": Path, "READS_PATH": Path("missing.csv")}
    exec(compile(ast.Module(body=fn, type_ignores=[]), "study.py", "exec"), ns)
    return ns["guard_phases"]


@pytest.fixture
def reads(tmp_path):
    p = tmp_path / "holdout_reads.csv"
    p.write_text("timestamp_utc,study,holdout_window,accessor,reason,verdict\n2026-10-20T00:00:00Z,x,2026,me,r,v\n", encoding="utf-8")
    return p


def test_default_dev_only(reads):
    assert _load()({}, reads) == ["DEV"]


def test_empty_auth_raises(reads):
    with pytest.raises(PermissionError):
        _load()({"OFV_PROTECTED_AUTH": ""}, reads)


def test_unknown_id_raises(reads):
    with pytest.raises(PermissionError):
        _load()({"OFV_PROTECTED_AUTH": "made-up"}, reads)


def test_known_id_accepted(reads):
    assert _load()({"OFV_PROTECTED_AUTH": "2026-10-20T00:00:00Z"}, reads) == ["DEV", "VAL", "HOLDOUT"]


def test_default_flag_is_dev_only():
    assert "DEV_ONLY = guard_phases(os.environ) == [\"DEV\"]" in SRC
