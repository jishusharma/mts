"""The ship gate and its helpers must install nowin, or every python/git child of a windowless parent opens a console window
(operator 2026-11-10: three python.exe windows popping during ships)."""
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SCRIPTS = ["sync.py", "mts_run.py", "status_board.py", "bg_watch.py", "mts_signal.py"]


@pytest.mark.parametrize("name", SCRIPTS)
def test_script_installs_nowin(name):
    assert "nowin.install()" in (HERE / name).read_text(encoding="utf-8")


@pytest.mark.parametrize("name", SCRIPTS)
def test_script_still_compiles(name):
    compile((HERE / name).read_text(encoding="utf-8"), name, "exec")
