import sys; sys.dont_write_bytecode = True
"""B209 item 2: tasks.py list hides done/dropped cards unless --all or --state is given."""
import os
import subprocess
from pathlib import Path

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])


def lines(*args):
    p = subprocess.run([sys.executable, str(ROOT / "scripts/dev/tasks.py"), "list", *args], capture_output=True, text=True, cwd=ROOT, timeout=120)
    return [x for x in p.stdout.splitlines() if x.strip()]


def test_default_list_has_no_closed_cards():
    out = lines()
    assert not [x for x in out if " done " in x[:40] or " dropped " in x[:40]]


def test_all_flag_brings_closed_cards_back():
    assert len(lines("--all")) > len(lines())
