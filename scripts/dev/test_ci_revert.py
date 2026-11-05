"""ci_revert.py: plan from fake fast-track runs, refusals (merge, not on trunk, later commits on the same files), dry run, --apply.
Real throwaway git repos in tmp_path; no network (runs are dicts, the ship step is a stub)."""
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ci_revert as CR
import mts_doctor as D

GATED = lambda sha: True   # stub: every red sha touched a CI path


def _run(sha, conclusion, minute):
    return {"head_sha": sha, "conclusion": conclusion, "created_at": f"2026-10-25T10:{minute:02d}:00Z"}


def _g(repo, *args):
    out = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return out.stdout.strip()


def _commit(repo, name, text, msg):
    p = Path(repo) / name
    p.write_text(text, encoding="utf-8", newline="\n")
    _g(repo, "add", name)
    _g(repo, "commit", "-q", "-m", msg)
    return _g(repo, "rev-parse", "HEAD")


def _repo(tmp_path):
    """A repo whose 'origin/fast-track' ref is its HEAD (update-ref, no remote): base, A (breaks a.py), B (other file)."""
    r = tmp_path / "r"
    r.mkdir()
    _g(r, "init", "-q")
    _g(r, "config", "user.email", "t@t")
    _g(r, "config", "user.name", "t")
    _g(r, "config", "commit.gpgsign", "false")
    base = _commit(r, "a.py", "x = 1\n", "base")
    a = _commit(r, "a.py", "x = 2\n", "A breaks")
    b = _commit(r, "b.py", "y = 1\n", "B other")
    _g(r, "update-ref", "refs/remotes/origin/fast-track", "HEAD")
    return r, base, a, b


def test_first_red_sha_names_the_first_red_of_the_open_streak():
    runs = [_run("g" * 40, "success", 0), _run("a" * 40, "failure", 5), _run("b" * 40, "failure", 9)]
    assert D.first_red_sha(runs, gated=GATED) == "a" * 40
    assert D.first_red_sha(runs + [_run("c" * 40, "success", 12)], gated=GATED) is None
    assert D.first_red_sha(runs, gated=lambda sha: False) is None


def test_plan_names_A_and_dry_run_makes_no_commit(tmp_path, capsys):
    r, base, a, b = _repo(tmp_path)
    runs = [_run(base, "success", 0), _run(a, "failure", 5), _run(b, "failure", 9)]
    head = _g(r, "rev-parse", "HEAD")
    assert CR.main([], repo=r, runs=runs, gated=GATED) == 0
    out = capsys.readouterr().out
    assert f"PLAN: git revert --no-commit {a}" in out and b not in out
    assert _g(r, "rev-parse", "HEAD") == head and _g(r, "status", "--porcelain") == ""


def test_merge_commit_refused(tmp_path, capsys):
    r, base, a, b = _repo(tmp_path)
    _g(r, "checkout", "-q", "-b", "side", base)
    _commit(r, "c.py", "z = 1\n", "side")
    _g(r, "checkout", "-q", "-")
    _g(r, "merge", "-q", "--no-ff", "-m", "merge side", "side")
    m = _g(r, "rev-parse", "HEAD")
    _g(r, "update-ref", "refs/remotes/origin/fast-track", "HEAD")
    assert CR.main([], repo=r, runs=[_run(b, "success", 0), _run(m, "failure", 5)], gated=GATED) == CR.REFUSED
    out = capsys.readouterr().out
    assert "REFUSED" in out and "merge commit" in out and f"git revert -m 1 {m}" in out


def test_later_commit_touching_same_files_refused(tmp_path, capsys):
    r, base, a, b = _repo(tmp_path)
    c = _commit(r, "a.py", "x = 3\n", "C forward-fix on a.py")
    _g(r, "update-ref", "refs/remotes/origin/fast-track", "HEAD")
    assert CR.main([], repo=r, runs=[_run(base, "success", 0), _run(a, "failure", 5), _run(c, "failure", 9)], gated=GATED) == CR.REFUSED
    out = capsys.readouterr().out
    assert "REFUSED" in out and "a.py" in out and "later commits" in out


def test_not_on_trunk_refused(tmp_path, capsys):
    r, base, a, b = _repo(tmp_path)
    _g(r, "checkout", "-q", "-b", "side", base)
    s = _commit(r, "s.py", "s = 1\n", "side only")
    _g(r, "checkout", "-q", "-")
    assert CR.main([], repo=r, runs=[_run(base, "success", 0), _run(s, "failure", 5)], gated=GATED) == CR.REFUSED
    assert "not on origin/fast-track" in capsys.readouterr().out


def test_green_trunk_has_nothing_to_revert(tmp_path, capsys):
    r, base, a, b = _repo(tmp_path)
    assert CR.main([], repo=r, runs=[_run(a, "failure", 5), _run(b, "success", 9)], gated=GATED) == 0
    assert "trunk green" in capsys.readouterr().out


def test_apply_makes_one_revert_commit_and_ships_without_force(tmp_path):
    r, base, a, b = _repo(tmp_path)
    shipped = []
    rc = CR.main(["--apply"], repo=r, runs=[_run(base, "success", 0), _run(a, "failure", 5)], gated=GATED,
                 ship=lambda repo: shipped.append(repo) or 0)
    assert rc == 0 and shipped == [r]
    assert _g(r, "rev-list", "--count", f"{b}..HEAD") == "1"
    msg = _g(r, "log", "-1", "--format=%B")
    assert msg.startswith("Revert ") and f"Result: reverts {a} (CI red)" in msg
    assert (r / "a.py").read_text(encoding="utf-8") == "x = 1\n" and _g(r, "status", "--porcelain") == ""
    assert not any(w in " ".join(CR.SHIP_CMD) for w in ("--force", "rebase", "reset"))


def test_apply_conflict_aborts_and_leaves_tree_clean(tmp_path, capsys):
    r, base, a, b = _repo(tmp_path)
    _commit(r, "a.py", "x = 9\n", "local edit on a.py, not on trunk")   # caller's tree diverged on the same file
    head = _g(r, "rev-parse", "HEAD")
    rc = CR.main(["--apply"], repo=r, runs=[_run(base, "success", 0), _run(a, "failure", 5)], gated=GATED,
                 ship=lambda repo: 0)
    assert rc == CR.REFUSED and "conflict" in capsys.readouterr().out
    assert _g(r, "rev-parse", "HEAD") == head and _g(r, "status", "--porcelain") == ""


def test_doctor_red_now_detail_names_the_command():
    now = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
    st, msg = D.ci_revert([_run("a" * 40, "success", 0), _run("b" * 40, "failure", 5)], now, gated=GATED)
    assert st == "WARN" and msg.endswith("run: python scripts/dev/ci_revert.py")
