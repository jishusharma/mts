"""Spec-derived boundary tests for retention.py; all paths are isolated in tmp_path."""
import importlib.util
from pathlib import Path

import pytest


SPEC = importlib.util.spec_from_file_location("retention_under_test", Path(__file__).with_name("retention.py"))
retention = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(retention)


def _mkdir(root, rel):
    path = root / rel
    path.mkdir(parents=True)
    (path / "payload.txt").write_text("fixture", encoding="utf-8")
    return path


@pytest.mark.parametrize("age, expected", [(14.0, []), (13.999, []), (14.001, ["old"])])
def test_old_children_14_day_boundary(tmp_path, monkeypatch, age, expected):
    parent = tmp_path / "backup_session"
    parent.mkdir()
    child = parent / "old"
    child.mkdir()
    now = 2_000_000_000.0
    monkeypatch.setattr(retention.time, "time", lambda: now)
    import os
    os.utime(child, (now - age * retention.DAY, now - age * retention.DAY))

    assert [Path(p).name for p in retention.old_children(str(parent), 14)] == expected


def test_empty_root_has_no_candidates(tmp_path):
    assert retention.plan(str(tmp_path)) == []


def test_protected_nuc_queue_done_is_not_a_candidate(tmp_path):
    protected = _mkdir(tmp_path, "Dumps/workers/NUC-QUEUE/done")
    assert str(protected) not in [item[1] for item in retention.plan(str(tmp_path))]


@pytest.mark.parametrize("size, included", [(200_000, False), (200_001, True)])
def test_log_size_limit_is_strictly_greater_than_200000(tmp_path, size, included):
    log = tmp_path / "runtime_data/mts-watch.log"
    log.parent.mkdir()
    log.write_bytes(b"x" * size)

    planned = [item for item in retention.plan(str(tmp_path)) if item[1] == str(log)]
    assert bool(planned) is included


def test_dry_run_prints_plan_without_changing_log(tmp_path, monkeypatch, capsys):
    log = tmp_path / "runtime_data/mts-watch.log"
    log.parent.mkdir()
    original = b"first line\n" + b"tail line\n" * 20_000
    log.write_bytes(original)
    item = ("trim", str(log), len(original), "log with no reader; keep last 2000 lines")
    monkeypatch.setattr(retention, "plan", lambda: [item])
    monkeypatch.setattr(retention, "ROOT", str(tmp_path))

    retention.main([])

    assert log.read_bytes() == original
    assert "dry run; add --apply" in capsys.readouterr().out


def test_trim_keeps_exactly_last_2000_lines(tmp_path):
    log = tmp_path / "watch.log"
    log.write_text("".join(f"line-{n}\n" for n in range(2_005)), encoding="utf-8")
    before = log.stat().st_mtime
    retention.apply([("trim", str(log), log.stat().st_size, "test")])

    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2_000
    assert lines[0] == "line-5"
    assert lines[-1] == "line-2004"
    assert log.stat().st_mtime == pytest.approx(before, abs=0.01)


def test_duplicate_copy_requires_same_bytes(tmp_path):
    original = _mkdir(tmp_path, "Dumps")
    duplicate = _mkdir(tmp_path, "Dumps.pre_B138")
    (original / "payload.txt").write_bytes(b"source")
    (duplicate / "payload.txt").write_bytes(b"target")

    assert retention.dup_copy_is_subset(str(duplicate), str(original)) is False
