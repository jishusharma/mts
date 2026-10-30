import sys; sys.dont_write_bytecode = True
"""B209 item 5: read-only blocks were stamped kind=write because words inside quoted patterns matched the write regex.
Dot-sources src/checks.ps1 and asks Get-CmdKind (Windows PowerShell only)."""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])
CHECKS = ROOT / "scripts" / "aibridge" / "src" / "checks.ps1"
PS = shutil.which("powershell.exe") or shutil.which("powershell")
pytestmark = pytest.mark.skipif(not PS, reason="needs Windows PowerShell")


def kind(cmd):
    script = ". '%s'; $pol = [pscustomobject]@{}; Get-CmdKind @'\n%s\n'@ $pol" % (CHECKS, cmd)
    p = subprocess.run([PS, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], capture_output=True, text=True, timeout=60)
    return p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr


def test_quoted_write_words_do_not_make_a_read_block_write():
    assert kind("Select-String -Path a.md -Pattern 'git commit|Remove-Item|a>b'") == "read"
    assert kind('Select-String -Path a.md -Pattern "Set-Content"') == "read"


def test_real_writes_still_write():
    assert kind("Set-Content -Path x.txt -Value 'hi'") == "write"
    assert kind("git commit -m 'x'") == "write"
    assert kind("Get-Date > out.txt") == "write"
