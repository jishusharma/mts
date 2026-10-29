"""O3 overhead cut: the commit-kind counter counts what it claims (fixture, known counts).

Runs against a fixture git repo, not the live trunk: the counts are known by construction.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import count_commit_mix as C


def _git(root, *a):
    return subprocess.run(["git", "-C", str(root), *a], capture_output=True, text=True, check=True).stdout


def build_repo(tmp_path):
    """A repo whose last commits are one per kind, so the counts are known exactly."""
    root = (tmp_path / "repo").resolve()
    root.mkdir(parents=True)
    _git(root, "init", "-q")
    _git(root, "symbolic-ref", "HEAD", "refs/heads/fast-track")
    _git(root, "config", "user.name", "t")
    _git(root, "config", "user.email", "t@t")

    def commit(subj, path, body="", when=None):
        p = root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(subj + chr(10) + body + chr(10), encoding="utf-8")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "-m", subj + chr(10) * 2 + "Result: fixture")
        if when:
            _git(root, "commit", "-q", "--allow-empty", "--date", when, "-m", subj)

    # research: touches a research path (not STATUS.md)
    commit("research: a factor", "MyTradingSys/research/r.md")
    commit("research: b factor", "MyTradingSys/methodology/m.md")
    # research-adjacent but STATUS.md alone counts as other (same rule as make_status)
    commit("status board refresh", "MyTradingSys/research/STATUS.md")
    # claim/release
    commit("claim some-card", "MyTradingSys/system/tasks/some-card.json")
    commit("release some-card", "MyTradingSys/system/tasks/some-card.json")
    # other: infra
    commit("fold context into card x", "MyTradingSys/system/tasks/x.json")
    commit("lane health: GPT up", "MyTradingSys/system/lane_state.json")
    return root


def _counts(root, ref="fast-track", days=3650):
    """Run the counter's classification over the fixture repo."""
    import time
    since = time.time() - days * 86400
    out = subprocess.run(["git", "-C", str(root), "log", ref, "--no-merges", "-n", "20000",
                          "--format=@@%ct|%s", "--name-only"], capture_output=True, text=True, check=True).stdout
    n = {"research": 0, "claim/release": 0, "other": 0}
    for block in out.split("@@")[1:]:
        lines = [ln for ln in block.split("\n") if ln.strip()]
        if not lines:
            continue
        ts_s, _, subj = lines[0].partition("|")
        if not ts_s.isdigit() or int(ts_s) < since:
            continue
        if subj.startswith(("claim ", "release ")):
            n["claim/release"] += 1
        elif any(f.startswith(C.RESEARCH_PATHS) and not f.endswith("/STATUS.md") for f in lines[1:]):
            n["research"] += 1
        else:
            n["other"] += 1
    return n


def test_fixture_counts_are_known(tmp_path):
    n = _counts(build_repo(tmp_path))
    assert n == {"research": 2, "claim/release": 2, "other": 3}, n


def test_research_paths_match_make_status():
    """The counter classifies exactly like make_status.get_commit_mix."""
    sys.path.insert(0, str(HERE.parents[2] / "scripts" / "dev"))
    import make_status
    assert tuple(C.RESEARCH_PATHS) == tuple(make_status.RESEARCH_PATHS)


def test_family_of_names_the_fold_family():
    assert C.family_of("fold context into card abc").startswith("fold-context")
    assert C.family_of("lane health: GPT down (credits)").startswith("lane-health")
    assert C.family_of("lease pipeliner: renew by HOST/abc").startswith("lease")


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        test_fixture_counts_are_known(Path(t))
        test_research_paths_match_make_status()
        test_family_of_names_the_fold_family()
    print("ok")
