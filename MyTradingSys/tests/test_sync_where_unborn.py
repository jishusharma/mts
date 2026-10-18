"""sync.py where must not abort on a worktree whose branch ref is gone (unborn HEAD)."""
import importlib.util
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("mts_sync", ROOT / "scripts" / "dev" / "sync.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def _git(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True)


def test_where_reports_unborn_worktree(tmp_path, capsys):
    repo = tmp_path / "repo"
    _git(tmp_path, "init", "-q", str(repo))
    _git(repo, "symbolic-ref", "HEAD", f"refs/heads/{sync.TRUNK}")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "a.txt").write_text("a\n")
    _git(repo, "add", "a.txt")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "remote", "add", "origin", str(repo))  # the repo is its own origin: fetch works offline
    _git(repo, "fetch", "-q", "origin", sync.TRUNK)
    # `worktree add --orphan` needs git >= 2.42; delete the branch ref instead so HEAD is unborn on any git
    _git(repo, "worktree", "add", "-q", "-b", "gone", str(tmp_path / "wt"))
    _git(repo, "update-ref", "-d", "refs/heads/gone")
    sync.where(repo)
    out = capsys.readouterr().out
    assert "BROKEN" in out and "wt" in out  # default: one line naming the broken trees
    assert "worktree(s) hold work" in out
    sync.where(repo, all_=True)
    full = capsys.readouterr().out
    assert any(l.startswith("BROKEN") and "wt" in l and "worktree remove" in l for l in full.splitlines())  # --all: one row, with the fix
