"""Card move-live-host-generated-files-status-md, commit 1: the live-host generated files are untracked + ignored, every reader copes
with them present, untracked and ABSENT (SKIP/stale/WARN, never PASS and never a crash), and the untrack commit can be deployed
without losing the files (backup / reset / merge / restore / sha verify, on throw-away git repos only).
Expected behaviour comes from MyTradingSys/system/card_specs/move-live-host-generated-files-status-md.md (done_when 1-4)."""
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "dev"))
sys.path.insert(0, str(REPO / "scripts" / "sched"))
import cicd_run as cr  # noqa: E402
import deploy_untrack_backup as dub  # noqa: E402
import make_status as ms  # noqa: E402

GENERATED = (
    "MyTradingSys/research/audits/AUDIT_DIGEST.md",
    "MyTradingSys/research/audits/T0_CHECKS.md",
    "MyTradingSys/runtime/BUILD_REPORT.md",
    "MyTradingSys/runtime/oi_live/oi_1m.csv",
    "MyTradingSys/runtime/oi_live/oi_5m_30d.csv",
    "MyTradingSys/research/htf_context/2026-10-08.jsonl",
    "MyTradingSys/research/htf_context/2026-10-08_summary.json",
)
STAYS_TRACKED = ("MyTradingSys/research/STATUS.md", "MyTradingSys/runtime/oi_live/oi_recorder.py",
                 "MyTradingSys/backtest/layers/fabio/htf_context_live.py", "MyTradingSys/research/audits/AUDIT_DIGEST_CLOSED.json")


def git(root, *args, check=True):
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    import os
    p = subprocess.run(["git", "-C", str(root), "-c", "commit.gpgsign=false", *args], capture_output=True, text=True,
                       env={**os.environ, **env})
    if check:
        assert p.returncode == 0, (args, p.stderr)
    return p


def init_main(root):
    git(root, "init", "-q")
    git(root, "symbolic-ref", "HEAD", "refs/heads/main")   # `git init -b` needs git 2.28


def put(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))
    return p


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def in_git_checkout():
    return subprocess.run(["git", "-C", str(REPO), "rev-parse", "--git-dir"], capture_output=True).returncode == 0


# ---------------------------------------------------------------- done_when (2): what the repo tracks
@pytest.mark.skipif(not in_git_checkout(), reason="needs a git checkout")
def test_no_generated_path_is_tracked_but_code_and_status_are():
    tracked = set(git(REPO, "ls-files").stdout.split("\n"))
    assert [g for g in GENERATED if g in tracked] == []
    assert not [t for t in tracked if t.startswith("MyTradingSys/research/htf_context/") and t.endswith((".jsonl", ".json"))]
    assert not [t for t in tracked if t.startswith("MyTradingSys/runtime/oi_live/") and t.endswith(".csv")]
    assert [t for t in STAYS_TRACKED if t not in tracked] == []


@pytest.mark.skipif(not in_git_checkout(), reason="needs a git checkout")
def test_every_generated_path_is_gitignored_and_the_live_status_copy_too():
    for rel in GENERATED + ("runtime_data/STATUS_live.md",):
        assert git(REPO, "check-ignore", "-q", rel, check=False).returncode == 0, f"{rel} is not git-ignored"
    for rel in STAYS_TRACKED:
        assert git(REPO, "check-ignore", "-q", rel, check=False).returncode != 0, f"{rel} must not be ignored"


# ---------------------------------------------------------------- done_when (1): readers
def test_check_new_aging_absent_build_report_warns_and_does_not_crash(tmp_path, capsys, monkeypatch):
    import check_new_aging as na
    monkeypatch.setattr(na, "REPO", tmp_path)
    assert na.main() == 1                                   # WARN, never OK (0) and never a raised FileNotFoundError
    out = capsys.readouterr().out
    assert out.startswith("new_aging WARN") and "absent" in out


def test_check_new_aging_present_report_still_reads(tmp_path, capsys, monkeypatch):
    import check_new_aging as na
    monkeypatch.setattr(na, "REPO", tmp_path)
    put(tmp_path, "MyTradingSys/runtime/BUILD_REPORT.md", "  - a/b.new (age 9999m)\n")
    assert na.main() == 1 and "older than 24h" in capsys.readouterr().out
    put(tmp_path, "MyTradingSys/runtime/BUILD_REPORT.md", "STATUS: PASS\n")
    assert na.main() == 0


def test_make_status_live_tree_writes_the_ignored_copy_other_trees_the_tracked_page(tmp_path):
    assert ms.get_status_path(tmp_path) == "MyTradingSys/research/STATUS.md"
    (tmp_path / ".mts_live").write_text("x")
    assert ms.get_status_path(tmp_path) == "runtime_data/STATUS_live.md"


def _ctx(repo, tmp_path):
    return cr.Ctx(repo=repo, profile="postclose", session="", run=None, which=lambda n: None, out_dir=tmp_path / "out",
                  quick=False, emit=lambda _x: None)


def test_cicd_postclose_build_report_absent_is_skip_present_is_information(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    put(repo, "a.txt", "x")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "c")
    by = {c["check"]: c for c in cr.stage_postclose(_ctx(repo, tmp_path))}
    assert by["postclose/P8-build-report"]["status"] == cr.SKIP and "absent" in by["postclose/P8-build-report"]["detail"]
    put(repo, cr.BUILD_REPORT_REL, "STATUS: PASS\n")
    by = {c["check"]: c for c in cr.stage_postclose(_ctx(repo, tmp_path))}
    assert by["postclose/P8-build-report"]["status"] == cr.PASS
    assert git(repo, "status", "--porcelain").stdout.strip() != ""   # untracked here (no .gitignore in this toy repo); readers never ask git


# ---------------------------------------------------------------- done_when (3): the hazard and the backup/restore step, on temp repos
def _origin_and_live(tmp_path):
    origin = tmp_path / "origin"
    origin.mkdir()
    init_main(origin)
    put(origin, ".gitignore", "")
    for rel in GENERATED:
        put(origin, rel, f"committed {rel}\n")
    put(origin, "MyTradingSys/runtime/oi_live/oi_recorder.py", "code\n")
    git(origin, "add", "-A")
    git(origin, "commit", "-q", "-m", "base")
    live = tmp_path / "live"
    git(tmp_path, "clone", "-q", str(origin), str(live))
    # the live host rewrites them (dirty) and the recorders append:
    for rel in GENERATED:
        put(live, rel, f"LIVE-WRITTEN {rel}\n" + "row\n" * 50)
    # the untrack commit on origin: .gitignore + git rm --cached
    put(origin, ".gitignore", "\n".join(GENERATED + ("runtime_data/deploy_backup/",)) + "\n")
    git(origin, "rm", "--cached", "-q", *GENERATED)
    git(origin, "add", ".gitignore")
    git(origin, "commit", "-q", "-m", "untrack generated")
    git(live, "fetch", "-q", "origin")
    return origin, live


def test_hazard_untracking_commit_deletes_files_in_a_tree_that_takes_it(tmp_path):
    """Documents why the backup step exists: with clean copies the fast-forward REMOVES the files from the clone."""
    origin = tmp_path / "origin"
    origin.mkdir()
    init_main(origin)
    for rel in GENERATED:
        put(origin, rel, f"committed {rel}\n")
    git(origin, "add", "-A")
    git(origin, "commit", "-q", "-m", "base")
    clone = tmp_path / "clone"
    git(tmp_path, "clone", "-q", str(origin), str(clone))
    git(origin, "rm", "--cached", "-q", *GENERATED)
    put(origin, ".gitignore", "\n".join(GENERATED) + "\n")
    git(origin, "add", ".gitignore")
    git(origin, "commit", "-q", "-m", "untrack")
    git(clone, "pull", "-q", "--ff-only")
    assert [g for g in GENERATED if (clone / g).exists()] == []


def test_dirty_generated_file_blocks_the_fast_forward_until_reset(tmp_path):
    origin, live = _origin_and_live(tmp_path)
    p = git(live, "merge", "--ff-only", "origin/main", check=False)
    assert p.returncode != 0                                # local changes would be overwritten: the merge refuses


def test_backup_reset_merge_restore_returns_byte_identical_files_and_a_clean_tree(tmp_path):
    origin, live = _origin_and_live(tmp_path)
    before = {g: sha(live / g) for g in GENERATED}
    stamp, manifest = dub.backup(live, stamp="T1")
    assert set(manifest) == set(GENERATED) and dub.verify_backup(live, stamp) == []
    reset = dub.reset_dirty_tracked(live, stamp)
    assert sorted(reset) == sorted(GENERATED)               # all were tracked + dirty
    assert git(live, "merge", "--ff-only", "origin/main").returncode == 0
    assert [g for g in GENERATED if (live / g).exists()] == []   # the hazard: the merge removed them
    restored, kept, problems = dub.restore(live, stamp)
    assert sorted(restored) == sorted(GENERATED) and kept == [] and problems == []
    assert {g: sha(live / g) for g in GENERATED} == before   # identical sha
    assert git(live, "status", "--porcelain").stdout.strip() == ""   # ignored now: working tree clean
    assert (live / "MyTradingSys/runtime/oi_live/oi_recorder.py").exists()


def test_restore_never_overwrites_a_file_a_recorder_recreated(tmp_path):
    origin, live = _origin_and_live(tmp_path)
    stamp, _ = dub.backup(live, stamp="T2")
    dub.reset_dirty_tracked(live, stamp)
    git(live, "merge", "--ff-only", "origin/main")
    newer = "MyTradingSys/runtime/oi_live/oi_1m.csv"
    put(live, newer, "recreated by the recorder\n")
    restored, kept, problems = dub.restore(live, stamp)
    assert newer not in restored and any(newer in k and "KEPT-NEWER" in k for k in kept) and problems == []
    assert (live / newer).read_text() == "recreated by the recorder\n"


def test_reset_refuses_when_the_backup_does_not_verify(tmp_path):
    origin, live = _origin_and_live(tmp_path)
    stamp, _ = dub.backup(live, stamp="T3")
    (dub.backup_dir(live, stamp) / "MyTradingSys/runtime/BUILD_REPORT.md").write_text("tampered\n")
    with pytest.raises(RuntimeError, match="does not verify"):
        dub.reset_dirty_tracked(live, stamp)
    assert (live / "MyTradingSys/runtime/BUILD_REPORT.md").read_text().startswith("LIVE-WRITTEN")   # nothing was reset


def test_backup_refuses_to_overwrite_an_existing_backup(tmp_path):
    origin, live = _origin_and_live(tmp_path)
    dub.backup(live, stamp="T4")
    with pytest.raises(RuntimeError, match="already exists"):
        dub.backup(live, stamp="T4")


def test_rows_appended_between_backup_and_reset_survive(tmp_path):
    """Review finding: a recorder appends after `backup`; reset must fold those rows into the backup before `git checkout --`."""
    origin, live = _origin_and_live(tmp_path)
    stamp, _ = dub.backup(live, stamp="T5")
    grown = live / "MyTradingSys/runtime/oi_live/oi_1m.csv"
    with open(grown, "ab") as f:
        f.write(b"appended-after-backup\n")
    want = sha(grown)
    dub.reset_dirty_tracked(live, stamp)
    git(live, "merge", "--ff-only", "origin/main")
    dub.restore(live, stamp)
    assert sha(grown) == want and b"appended-after-backup" in grown.read_bytes()


def test_cli_exits_1_when_a_recreated_file_was_kept(tmp_path, capsys):
    origin, live = _origin_and_live(tmp_path)
    stamp, _ = dub.backup(live, stamp="T6")
    dub.reset_dirty_tracked(live, stamp)
    git(live, "merge", "--ff-only", "origin/main")
    put(live, "MyTradingSys/runtime/oi_live/oi_5m_30d.csv", "recreated\n")
    assert dub.main(["restore", str(live), stamp]) == 1
    assert "KEPT-NEWER" in capsys.readouterr().out
    assert dub.main(["restore", str(live), "nope"]) == 1                      # no such backup: loud, not a crash


def test_helper_groups_cover_every_generated_path_and_no_code():
    for rel in GENERATED:
        assert any(Path(rel).match(g) and Path(rel).parent == Path(g).parent for g in dub.GROUPS), f"{rel} not in GROUPS"
    for code in STAYS_TRACKED:
        assert not any(Path(code).match(g) and Path(code).parent == Path(g).parent for g in dub.GROUPS), f"{code} must not be backed up/reset"


def test_second_reset_never_replaces_a_fuller_backup_with_a_reverted_file(tmp_path):
    """Review round 2: backup, append, reset, recorder dirties the reverted file again, merge refuses, reset re-run: the backup keeps the full rows."""
    origin, live = _origin_and_live(tmp_path)
    stamp, _ = dub.backup(live, stamp="T7")
    csv = live / "MyTradingSys/runtime/oi_live/oi_1m.csv"
    full = csv.read_bytes() + b"late-row\n"
    csv.write_bytes(full)
    dub.reset_dirty_tracked(live, stamp)                        # first reset: backup now holds `full`
    with open(csv, "ab") as f:
        f.write(b"after-reset\n")                               # recorder dirties the reverted (committed) file again
    dub.reset_dirty_tracked(live, stamp)                        # re-run: must not overwrite the fuller backup
    git(live, "merge", "--ff-only", "origin/main")
    dub.restore(live, stamp)
    assert csv.read_bytes() == full
    side = dub.backup_dir(live, stamp) / "MyTradingSys/runtime/oi_live/oi_1m.csv.pre-reset-1"
    assert side.is_file() and b"after-reset" in side.read_bytes()    # the rows the checkout discarded are kept beside the backup
