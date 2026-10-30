"""Spec-derived tests for the deploy backup helper; all filesystem state is temporary."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest


SOURCE = Path(os.environ.get("DEPLOY_UNTRACK_BACKUP_MODULE", Path(__file__).with_name("deploy_untrack_backup.py")))
SPEC = importlib.util.spec_from_file_location("deploy_untrack_backup_under_test", SOURCE)
deploy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deploy)


def write_file(root, rel, data):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


@pytest.mark.parametrize("size", [(1 << 20) - 1, 1 << 20, (1 << 20) + 1])
def test_sha256_chunk_boundary_below_at_and_above(tmp_path, size):
    path = tmp_path / "payload"
    payload = bytes((i % 251 for i in range(size)))
    path.write_bytes(payload)
    assert deploy.sha256(path) == hashlib.sha256(payload).hexdigest()


def test_collect_returns_sorted_unique_matching_files_only(tmp_path):
    write_file(tmp_path, "MyTradingSys/runtime/oi_live/b.csv", b"b")
    write_file(tmp_path, "MyTradingSys/runtime/oi_live/a.csv", b"a")
    write_file(tmp_path, "MyTradingSys/runtime/oi_live/ignored.txt", b"x")
    write_file(tmp_path, "MyTradingSys/runtime/BUILD_REPORT.md", b"report")
    assert deploy.collect(tmp_path) == [
        "MyTradingSys/runtime/BUILD_REPORT.md",
        "MyTradingSys/runtime/oi_live/a.csv",
        "MyTradingSys/runtime/oi_live/b.csv",
    ]


def test_empty_backup_writes_empty_manifest_and_verifies(tmp_path):
    stamp, manifest = deploy.backup(tmp_path, "fixed")
    assert stamp == "fixed"
    assert manifest == {}
    assert json.loads((deploy.backup_dir(tmp_path, stamp) / deploy.MANIFEST).read_text()) == {}
    assert deploy.verify_backup(tmp_path, stamp) == []


def test_backup_records_copy_hash_and_size_and_restore_returns_expected_paths(tmp_path):
    rel = "MyTradingSys/research/audits/AUDIT_DIGEST.md"
    original = b"audit\n"
    write_file(tmp_path, rel, original)
    stamp, manifest = deploy.backup(tmp_path, "s1")
    assert manifest == {rel: {"sha256": hashlib.sha256(original).hexdigest(), "size": 6}}
    (tmp_path / rel).unlink()
    assert deploy.restore(tmp_path, stamp) == ([rel], [], [])
    assert (tmp_path / rel).read_bytes() == original


def test_restore_keeps_existing_different_live_file_and_reports_newer(tmp_path):
    rel = "MyTradingSys/runtime/BUILD_REPORT.md"
    write_file(tmp_path, rel, b"backup")
    stamp, _ = deploy.backup(tmp_path, "s2")
    write_file(tmp_path, rel, b"newer")
    restored, kept, problems = deploy.restore(tmp_path, stamp)
    assert restored == [] and problems == []
    assert kept == [f"{rel}: KEPT-NEWER (live {hashlib.sha256(b'newer').hexdigest()[:12]} vs backup {hashlib.sha256(b'backup').hexdigest()[:12]})"]
    assert (tmp_path / rel).read_bytes() == b"newer"


def test_verify_reports_missing_and_changed_backup_files(tmp_path):
    rel1 = "MyTradingSys/runtime/oi_live/a.csv"
    rel2 = "MyTradingSys/runtime/oi_live/b.csv"
    write_file(tmp_path, rel1, b"a")
    write_file(tmp_path, rel2, b"b")
    stamp, _ = deploy.backup(tmp_path, "s3")
    dest = deploy.backup_dir(tmp_path, stamp)
    (dest / rel1).unlink()
    (dest / rel2).write_bytes(b"changed")
    assert deploy.verify_backup(tmp_path, stamp) == [
        f"{rel1}: missing from backup",
        f"{rel2}: backup sha differs from manifest",
    ]


def test_malformed_manifest_is_rejected_by_json_parser(tmp_path):
    dest = deploy.backup_dir(tmp_path, "bad")
    dest.mkdir(parents=True)
    (dest / deploy.MANIFEST).write_text("{", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        deploy.load_manifest(tmp_path, "bad")


def test_duplicate_backup_refuses_to_overwrite(tmp_path):
    deploy.backup(tmp_path, "same")
    with pytest.raises(RuntimeError, match="already exists; refusing to overwrite"):
        deploy.backup(tmp_path, "same")


def test_restore_reports_corrupt_backup_and_leaves_live_file_unchanged(tmp_path):
    rel = "MyTradingSys/research/htf_context/x.jsonl"
    write_file(tmp_path, rel, b"original")
    stamp, _ = deploy.backup(tmp_path, "s4")
    (deploy.backup_dir(tmp_path, stamp) / rel).write_bytes(b"corrupt")
    restored, kept, problems = deploy.restore(tmp_path, stamp)
    assert restored == [] and kept == []
    assert problems == [f"{rel}: backup copy missing or changed, cannot restore"]
    assert (tmp_path / rel).read_bytes() == b"original"


@pytest.mark.parametrize("argv", [[], ["unknown", "root"], ["reset", "root"]])
def test_cli_malformed_arguments_print_usage_and_return_one(argv, capsys):
    assert deploy.main(argv) == 1
    assert "Manual helper for deploying" in capsys.readouterr().out


def test_cli_error_path_returns_one_and_prints_problem(tmp_path, capsys):
    assert deploy.main(["restore", str(tmp_path), "absent"]) == 1
    assert "PROBLEM no backup manifest at" in capsys.readouterr().out
