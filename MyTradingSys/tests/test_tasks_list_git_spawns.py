import sys; sys.dont_write_bytecode = True
"""tasks-list-all-slow-32s-speedup: `tasks.py list` must not spawn git per card (193 spawns for 64 cards = 20-32 s)."""
import argparse
import io
import os
import subprocess
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(os.environ.get("MTS_REPO_ROOT") or Path(__file__).resolve().parents[2])


def test_list_spawns_few_git_processes(monkeypatch):
    sys.path.insert(0, str(ROOT / "scripts" / "dev"))
    import tasks
    real = subprocess.run
    n = {"git": 0}

    def counting(cmd, *a, **k):
        if cmd and str(cmd[0]) == "git":
            n["git"] += 1; n.setdefault("c", []).append(" ".join(map(str, cmd))[-90:])
        return real(cmd, *a, **k)

    monkeypatch.setattr(subprocess, "run", counting)
    ready = [c for c in tasks.load_all(ROOT) if c["state"] in ("ready", "active")]
    assert len(ready) >= 10, "needs a repo with 10+ open cards"   # old code spawned ~3 git per card, so 10 cards already break the <= 10 cap below
    with redirect_stdout(io.StringIO()):
        tasks.cmd_list(argparse.Namespace(all=False, state=None, lane=None, prefix=None))
    assert n["git"] <= 10, n   # DECISION (OURS): 7 fixed spawns (claims, shallow, one log), card-count independent; old code ~190
