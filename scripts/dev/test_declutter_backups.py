"""Spec-derived tests for scripts/dev/declutter_backups.py.

Covers:
  - classify:
    * reject dirs (_nuc_rejected, qwen_raw_015_017) and colon-prefixed scratch paths
    * non-backup filenames returning (None, None)
    * rejected/qwen worker outputs returning superseded
    * double-suffix .new.new returning superseded (Qwen verifier pattern)
    * blob in git history of tracked base returning superseded
    * in-flight .new returning staged when differing from live file
    * promoted .new returning superseded when identical to live file
    * backup of .new (e.g. .new.pre_tag) superseded when current .new is newer
    * pre_* backup superseded when base committed after backup
    * pre_* backup unknown when base not committed after backup / untracked
"""
import os
from pathlib import Path
import pytest

import declutter_backups as db


def test_classify_reject_dirs_and_scratch_prefixes(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "ROOT", str(tmp_path))
    assert db.classify("_nuc_rejected/stray.py")[0] == "superseded"
    assert db.classify("subdir/qwen_raw_015_017/out.txt")[0] == "superseded"
    assert db.classify("scratch/test.py")[0] == "superseded"


def test_classify_non_backup_files_returns_none(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "ROOT", str(tmp_path))
    assert db.classify("regular_script.py") == (None, None)
    assert db.classify("docs/README.md") == (None, None)


def test_classify_rejected_and_qwen_kinds(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "ROOT", str(tmp_path))
    cls, reason = db.classify("algo.py.rejected_run")
    assert cls == "superseded"
    assert "rejected worker output" in reason

    cls, reason = db.classify("engine.py.qwen_raw")
    assert cls == "superseded"
    assert "rejected worker output" in reason

    cls, reason = db.classify("layer.py.qwen1")
    assert cls == "superseded"
    assert "rejected worker output" in reason


def test_classify_double_suffix_new_new(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "ROOT", str(tmp_path))
    cls, reason = db.classify("model.py.new.new")
    assert cls == "superseded"
    assert "double-suffix Qwen output" in reason


def test_classify_blob_in_git_history(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "ROOT", str(tmp_path))
    rel = "strategy.py.pre_opt"
    f = tmp_path / rel
    f.write_text("historical content", encoding="utf-8")

    monkeypatch.setattr(db, "git", lambda *args: "blob12345" if args[0] == "hash-object" else "")
    monkeypatch.setattr(db, "tracked", lambda r: True)
    monkeypatch.setattr(db, "history_blobs", lambda r: {"blob12345"})

    cls, reason = db.classify(rel)
    assert cls == "superseded"
    assert "content exists in git history" in reason


def test_classify_staged_new_file_differing_from_live(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "ROOT", str(tmp_path))
    base = tmp_path / "signal.py"
    base.write_text("live content", encoding="utf-8")

    staged = tmp_path / "signal.py.new"
    staged.write_text("in-flight edited content", encoding="utf-8")

    monkeypatch.setattr(db, "git", lambda *args: "newblob")
    monkeypatch.setattr(db, "tracked", lambda r: True)
    monkeypatch.setattr(db, "history_blobs", lambda r: set())

    cls, reason = db.classify("signal.py.new")
    assert cls == "staged"
    assert "in-flight .new" in reason


def test_classify_promoted_new_file_identical_to_live(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "ROOT", str(tmp_path))
    base = tmp_path / "signal.py"
    base.write_text("identical content", encoding="utf-8")

    staged = tmp_path / "signal.py.new"
    staged.write_text("identical content", encoding="utf-8")

    monkeypatch.setattr(db, "git", lambda *args: "someblob")
    monkeypatch.setattr(db, "tracked", lambda r: True)
    monkeypatch.setattr(db, "history_blobs", lambda r: set())

    cls, reason = db.classify("signal.py.new")
    assert cls == "superseded"
    assert ".new identical to live file" in reason


def test_classify_pre_backup_of_staged_new_superseded_by_newer_new(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "ROOT", str(tmp_path))
    staged = tmp_path / "runner.py.new"
    staged.write_text("newer content", encoding="utf-8")

    backup = tmp_path / "runner.py.new.pre_tag"
    backup.write_text("older snapshot", encoding="utf-8")

    # Set backup mtime older than staged mtime
    os.utime(backup, (1000, 1000))
    os.utime(staged, (2000, 2000))

    monkeypatch.setattr(db, "git", lambda *args: "diffblob")
    monkeypatch.setattr(db, "tracked", lambda r: False)
    monkeypatch.setattr(db, "history_blobs", lambda r: set())

    cls, reason = db.classify("runner.py.new.pre_tag")
    assert cls == "superseded"
    assert "older snapshot of a still-staged .new" in reason


def test_classify_pre_backup_committed_base_vs_untracked(monkeypatch, tmp_path):
    monkeypatch.setattr(db, "ROOT", str(tmp_path))
    backup = tmp_path / "core.py.pre_patch"
    backup.write_text("old core", encoding="utf-8")
    os.utime(backup, (1000, 1000))

    monkeypatch.setattr(db, "git", lambda *args: "hashblob")
    monkeypatch.setattr(db, "tracked", lambda r: True)
    monkeypatch.setattr(db, "history_blobs", lambda r: set())

    # Case 1: base committed after backup (commit ts 2000 > mtime 1000)
    monkeypatch.setattr(db, "last_commit_ts", lambda r: 2000)
    cls, reason = db.classify("core.py.pre_patch")
    assert cls == "superseded"
    assert "base committed after backup" in reason

    # Case 2: base committed before backup or untracked (commit ts 500 < mtime 1000)
    monkeypatch.setattr(db, "last_commit_ts", lambda r: 500)
    cls, reason = db.classify("core.py.pre_patch")
    assert cls == "unknown"
    assert "base not committed after backup" in reason
