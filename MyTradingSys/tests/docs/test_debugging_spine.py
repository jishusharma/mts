"""DEBUGGING.md is the one starting point for a dev-system fault (ARCHITECTURE.md). It rots the moment it names a
script that was moved, so: every repo path it quotes must exist, every hook script in .claude/settings.json must have
a row, and every system doc it points at must be a real file."""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SYSTEM = REPO / "MyTradingSys" / "system"
DOC = SYSTEM / "DEBUGGING.md"
# Gitignored runtime state: named so a reader knows where to look, absent from a clean checkout by design.
RUNTIME_STATE = ("runtime_data/", "MyTradingSys/runtime/sched/", "MyTradingSys/execution/HALT")


def _text():
    assert DOC.exists(), "MyTradingSys/system/DEBUGGING.md is missing"
    return DOC.read_text(encoding="utf-8")


def test_every_quoted_repo_path_exists():
    missing = []
    for path in re.findall(r"((?:scripts|MyTradingSys)/[\w./<>-]+)", _text()):
        path = path.rstrip(".")
        if "<" in path or path.startswith(RUNTIME_STATE):
            continue
        if not (REPO / path).exists():
            missing.append(path)
    assert not missing, "DEBUGGING.md names paths that do not exist: %s" % sorted(set(missing))


def test_every_hook_script_has_a_row():
    settings = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    scripts = set()
    for groups in settings.get("hooks", {}).values():
        for group in groups:
            for hook in group.get("hooks", []):
                scripts.update(re.findall(r"scripts/dev/(\w+\.py)", hook.get("command", "")))
    assert scripts, "no hook scripts parsed from .claude/settings.json"
    text = _text()
    absent = sorted(s for s in scripts if "scripts/dev/" + s not in text)
    assert not absent, "hook scripts with no DEBUGGING.md row: %s" % absent


def test_every_doc_it_points_at_exists():
    missing = []
    for name in set(re.findall(r"\b([A-Z][A-Z0-9_]+\.md)\b", _text())):
        if not ((SYSTEM / name).exists() or (REPO / name).exists()):
            missing.append(name)
    assert not missing, "DEBUGGING.md points at docs that do not exist: %s" % sorted(missing)
