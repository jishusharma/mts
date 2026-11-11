"""Claude hooks must start windowless (operator 2026-11-11: consoles flash whenever he types in the Claude app)."""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LAUNCHER = HERE / "nowin_hook.py"


def hook_commands():
    s = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    for ev, groups in s.get("hooks", {}).items():
        for g in groups:
            for h in g.get("hooks", []):
                yield ev, h.get("command", "")


def test_every_repo_hook_goes_through_the_windowless_launcher():
    bad = [(ev, c) for ev, c in hook_commands() if re.match(r"\s*python[3w]?(\.exe)?\s", c)]
    assert not bad, f"hooks start a console python.exe (a window flashes per hook): {bad}; use sh scripts/dev/hook.sh <script>"


def test_hook_sh_falls_back_to_python_without_pythonw():
    text = (HERE / "hook.sh").read_text(encoding="utf-8")
    assert "command -v pythonw" in text and "nowin_hook.py" in text and "exec python" in text
    assert "\r" not in text, "hook.sh needs LF line endings for sh"


def test_launcher_relays_stdin_stdout_stderr_and_exit_code(tmp_path):
    child = tmp_path / "child.py"
    child.write_text("import sys\nd = sys.stdin.read()\nsys.stdout.write(d.upper())\nsys.stderr.write('E')\nsys.exit(2)\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(LAUNCHER), str(child)], input=b"abc", capture_output=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    assert (r.stdout, r.stderr, r.returncode) == (b"ABC", b"E", 2)


def test_launcher_without_script_exits_2():
    r = subprocess.run([sys.executable, str(LAUNCHER)], input=b"", capture_output=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    assert r.returncode == 2
