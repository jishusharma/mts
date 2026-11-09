"""Find the Antigravity CLI `agy.exe` on any MTS host (ROUTING.md "Gemini access").

Measured install paths: NUC ~/.gemini/bin/agy.exe (2026-10-17); Lenovo laptop ~/AppData/Local/agy/bin/agy.exe
(login A check, 2026-11-09 22:30Z). First existing path wins; none -> the NUC default, so callers' "missing" checks still fire.
"""
from __future__ import annotations

from pathlib import Path


def candidates(home: Path | None = None) -> list[Path]:
    h = home or Path.home()
    return [h / '.gemini' / 'bin' / 'agy.exe', h / 'AppData' / 'Local' / 'agy' / 'bin' / 'agy.exe']


def find_agy(home: Path | None = None) -> Path:
    c = candidates(home)
    return next((p for p in c if p.is_file()), c[0])
