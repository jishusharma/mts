"""B127 M29-01 / M30-01 / M30-02: declutter_backups moves (never deletes) superseded files to Dumps/_archive/<date>/ with a
MANIFEST.csv row (path, class, reason, sha256), and --exclude leaves a prefix alone. Spec: the tool's own docstring."""
import csv
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "dev"))
import declutter_backups as db  # noqa: E402


def _run(monkeypatch, root, *argv):
    monkeypatch.setattr(db, "ROOT", str(root))
    monkeypatch.setattr(sys, "argv", ["declutter_backups.py", *argv])
    db.main()


def _tree(root):
    (root / "pkg").mkdir()
    (root / "pkg" / "live.py").write_bytes(b"live\n")
    (root / "pkg" / "old.py.rejected_x").write_bytes(b"rejected\n")
    (root / "area").mkdir()
    (root / "area" / "w.py.rejected_y").write_bytes(b"other session\n")


def test_apply_moves_superseded_keeps_bytes_and_writes_manifest(tmp_path, monkeypatch):
    _tree(tmp_path)
    want = hashlib.sha256(b"rejected\n").hexdigest()
    _run(monkeypatch, tmp_path, "--apply", "--date", "2026-01-02")
    arch = tmp_path / "Dumps" / "_archive" / "2026-01-02"
    assert not (tmp_path / "pkg" / "old.py.rejected_x").exists()
    assert (arch / "pkg" / "old.py.rejected_x").read_bytes() == b"rejected\n"      # moved, not deleted
    assert (tmp_path / "pkg" / "live.py").exists()                                  # live file untouched
    rows = list(csv.DictReader(open(arch / "MANIFEST.csv", newline="")))
    assert any(r["path"] == "pkg/old.py.rejected_x" and r["class"] == "superseded" and r["sha256"] == want for r in rows)


def test_exclude_prefix_is_left_alone(tmp_path, monkeypatch):
    _tree(tmp_path)
    _run(monkeypatch, tmp_path, "--apply", "--date", "2026-01-02", "--exclude", "area")
    assert (tmp_path / "area" / "w.py.rejected_y").exists()
    assert not (tmp_path / "pkg" / "old.py.rejected_x").exists()


def test_dry_run_moves_nothing(tmp_path, monkeypatch):
    _tree(tmp_path)
    _run(monkeypatch, tmp_path, "--date", "2026-01-02")
    assert (tmp_path / "pkg" / "old.py.rejected_x").exists()
    assert not (tmp_path / "Dumps").exists()
