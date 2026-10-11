import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "dev"))
import codex_pack  # noqa: E402


def test_refuses_inside_repo():
    try:
        codex_pack.main(["relay-two-host-standby", "--out", str(ROOT / "MyTradingSys" / "x_pack")])
    except SystemExit as e:
        assert "refusing" in str(e)
    else:
        raise AssertionError("wrote inside the repo")


def test_writes_outside_repo():
    with tempfile.TemporaryDirectory() as d:
        codex_pack.main(["relay-two-host-standby", "--out", d])
        t = (Path(d) / "relay-two-host-standby.md").read_text(encoding="utf-8")
        assert "Task brief" in t and "Lessons digest" in t
