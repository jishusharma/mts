"""Tests for scripts/worker/audit_t0_checks.py, written from the design in
Dumps/workers/NUC-QUEUE/specs/095-audit-t0-checks.md (T056, the T057 clutter inventory). The module
does not exist yet, so this file currently fails at import time with ModuleNotFoundError -- expected
until 095's reply is promoted from audit_t0_checks.py.new to audit_t0_checks.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_t0_checks  # noqa: E402


# ---------- find_stale_pre_backups ----------

def test_find_stale_pre_backups_flags_when_real_file_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_t0_checks, "REPO", tmp_path)
    (tmp_path / "real.py").write_text("x", encoding="utf-8")
    (tmp_path / "real.py.pre_fix3").write_text("old", encoding="utf-8")
    found = audit_t0_checks.find_stale_pre_backups()
    assert "real.py.pre_fix3" in found


def test_find_stale_pre_backups_ignores_backup_with_no_real_file(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_t0_checks, "REPO", tmp_path)
    (tmp_path / "orphan.py.pre_q024").write_text("old", encoding="utf-8")
    found = audit_t0_checks.find_stale_pre_backups()
    assert found == []


def test_find_stale_pre_backups_prunes_excluded_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_t0_checks, "REPO", tmp_path)
    dumps = tmp_path / "Dumps"
    dumps.mkdir()
    (dumps / "x.py").write_text("x", encoding="utf-8")
    (dumps / "x.py.pre_a").write_text("old", encoding="utf-8")
    found = audit_t0_checks.find_stale_pre_backups()
    assert found == []


# ---------- find_leftover_names ----------

def test_find_leftover_names_matches_rejected_and_raw(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_t0_checks, "DUMPS_WORKERS", tmp_path)
    monkeypatch.setattr(audit_t0_checks, "REPO", tmp_path)   # results are repo-relative; tmp_path is outside the real repo
    (tmp_path / "_nuc_rejected").mkdir()
    (tmp_path / "_nuc_rejected" / "inner.txt").write_text("x", encoding="utf-8")
    (tmp_path / "qwen_raw_042.txt").write_text("x", encoding="utf-8")
    (tmp_path / "normal.txt").write_text("x", encoding="utf-8")
    found = audit_t0_checks.find_leftover_names()
    assert any("_nuc_rejected" in f for f in found)
    assert any("qwen_raw_042.txt" in f for f in found)
    assert not any("normal.txt" in f for f in found)
    # the matched directory's own name is reported once, not once per file inside it
    assert not any("inner.txt" in f for f in found)


def test_find_leftover_names_empty_when_dumps_workers_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_t0_checks, "DUMPS_WORKERS", tmp_path / "nope")
    assert audit_t0_checks.find_leftover_names() == []


# ---------- find_big_dirs ----------

def test_find_big_dirs_flags_over_threshold(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_t0_checks, "REPO", tmp_path)
    monkeypatch.setattr(audit_t0_checks, "BIG_DIR_THRESHOLD_BYTES", 10)
    big = tmp_path / "bigdir"
    big.mkdir()
    (big / "f.bin").write_bytes(b"0" * 20)
    small = tmp_path / "smalldir"
    small.mkdir()
    (small / "f.bin").write_bytes(b"0" * 2)
    names = [n for n, _ in audit_t0_checks.find_big_dirs()]
    assert "bigdir" in names
    assert "smalldir" not in names


def test_find_big_dirs_skips_excluded_names(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_t0_checks, "REPO", tmp_path)
    monkeypatch.setattr(audit_t0_checks, "BIG_DIR_THRESHOLD_BYTES", 1)
    dumps = tmp_path / "Dumps"
    dumps.mkdir()
    (dumps / "f.bin").write_bytes(b"0" * 50)
    names = [n for n, _ in audit_t0_checks.find_big_dirs()]
    assert "Dumps" not in names


# ---------- find_orphan_docs ----------

def test_find_orphan_docs_flags_unreferenced_doc(tmp_path, monkeypatch):
    root = tmp_path / "items"
    root.mkdir()
    (root / "T999_orphan.md").write_text("nothing links here", encoding="utf-8")
    monkeypatch.setattr(audit_t0_checks, "REPO", tmp_path)
    monkeypatch.setattr(audit_t0_checks, "DOC_SCAN_ROOTS", [root])
    found = audit_t0_checks.find_orphan_docs()
    assert any("T999_orphan.md" in f for f in found)


def test_find_orphan_docs_not_flagged_when_referenced_elsewhere(tmp_path, monkeypatch):
    root = tmp_path / "items"
    root.mkdir()
    (root / "T998_linked.md").write_text("some content", encoding="utf-8")
    other = tmp_path / "other.md"
    other.write_text("see T998_linked.md for details", encoding="utf-8")
    monkeypatch.setattr(audit_t0_checks, "REPO", tmp_path)
    monkeypatch.setattr(audit_t0_checks, "DOC_SCAN_ROOTS", [root])
    found = audit_t0_checks.find_orphan_docs()
    assert not any("T998_linked.md" in f for f in found)


# ---------- render_report / run_t0_checks ----------

def test_render_report_has_required_headings_and_footer():
    text = audit_t0_checks.render_report([], [], [], [])
    for heading in (
        "## Stale .pre_* backups (real file already exists)",
        "## Leftover rejected/raw directories or files",
        "## Directories over 200 MB",
        "## Markdown docs referenced nowhere else",
    ):
        assert heading in text
    assert "(none found)" in text
    assert "Nothing is moved or deleted automatically" in text


def test_run_t0_checks_writes_report_and_never_deletes(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_t0_checks, "REPO", tmp_path)
    monkeypatch.setattr(audit_t0_checks, "DUMPS_WORKERS", tmp_path / "Dumps" / "workers")
    monkeypatch.setattr(audit_t0_checks, "DOC_SCAN_ROOTS", [])
    out_path = tmp_path / "MyTradingSys" / "research" / "audits" / "T0_CHECKS.md"
    monkeypatch.setattr(audit_t0_checks, "OUT_PATH", out_path)
    (tmp_path / "must_survive.py").write_text("current", encoding="utf-8")
    marker = tmp_path / "must_survive.py.pre_x"
    marker.write_text("old", encoding="utf-8")
    rc = audit_t0_checks.run_t0_checks()
    assert rc == 0
    assert out_path.exists()
    assert marker.exists()  # never deleted or moved
    assert "must_survive.py.pre_x" in out_path.read_text(encoding="utf-8")
