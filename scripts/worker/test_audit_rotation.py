"""Tests for scripts/worker/audit_rotation.py, written from the design in
Dumps/workers/NUC-QUEUE/specs/094-audit-rotation-backfill.md (T056). The module does not exist yet,
so this file currently fails at import time with ModuleNotFoundError -- that is expected until 094's
reply is promoted from audit_rotation.py.new to audit_rotation.py.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_rotation  # noqa: E402


def _target(id_, template="A1", paths=None, note="n", last_audited=None):
    return {
        "id": id_,
        "template": template,
        "paths": paths or ["some/path.py"],
        "note": note,
        "last_audited": last_audited,
    }


# ---------- registry I/O ----------

def test_load_registry_roundtrip(tmp_path, monkeypatch):
    reg_path = tmp_path / "audit_targets.json"
    data = {"schema": 1, "targets": [_target("A1-x")]}
    reg_path.write_text(json.dumps(data), encoding="utf-8", newline="\n")
    monkeypatch.setattr(audit_rotation, "REGISTRY_PATH", reg_path)
    loaded = audit_rotation.load_registry()
    assert loaded == data


def test_save_registry_is_atomic_and_lf(tmp_path, monkeypatch):
    reg_path = tmp_path / "audit_targets.json"
    monkeypatch.setattr(audit_rotation, "REGISTRY_PATH", reg_path)
    reg = {"schema": 1, "targets": [_target("A1-x")]}
    audit_rotation.save_registry(reg)
    raw = reg_path.read_bytes()
    assert b"\r\n" not in raw
    assert json.loads(raw.decode("utf-8")) == reg
    # no leftover temp file
    assert not (tmp_path / ".audit_targets.json.tmp").exists()


def test_load_registry_missing_file_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_rotation, "REGISTRY_PATH", tmp_path / "nope.json")
    try:
        audit_rotation.load_registry()
        assert False, "expected an exception for a missing registry"
    except Exception:
        pass


# ---------- targets_due ----------

def test_targets_due_never_audited_sorts_first():
    reg = {"targets": [
        _target("old", last_audited="2026-01-01T00:00:00Z"),
        _target("never", last_audited=None),
        _target("mid", last_audited="2026-06-01T00:00:00Z"),
    ]}
    due = audit_rotation.targets_due(reg, 3)
    assert [t["id"] for t in due] == ["never", "old", "mid"]


def test_targets_due_does_not_mutate_registry():
    reg = {"targets": [_target("a"), _target("b")]}
    before = json.dumps(reg, sort_keys=True)
    audit_rotation.targets_due(reg, 1)
    after = json.dumps(reg, sort_keys=True)
    assert before == after


def test_targets_due_n_larger_than_list_returns_all():
    reg = {"targets": [_target("a"), _target("b")]}
    due = audit_rotation.targets_due(reg, 10)
    assert len(due) == 2


# ---------- queue_waiting_count ----------

def test_queue_waiting_count_zero_when_dirs_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_rotation, "QUEUE", tmp_path / "does_not_exist")
    assert audit_rotation.queue_waiting_count() == 0


def test_queue_waiting_count_counts_incoming_and_claimed(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_rotation, "QUEUE", tmp_path)
    (tmp_path / "incoming").mkdir()
    (tmp_path / "claimed").mkdir()
    (tmp_path / "incoming" / "001-x.task.json").write_text("{}", encoding="utf-8")
    (tmp_path / "incoming" / "002-x.task.json").write_text("{}", encoding="utf-8")
    (tmp_path / "claimed" / "003-x.task.json").write_text("{}", encoding="utf-8")
    (tmp_path / "incoming" / "not-a-task.txt").write_text("x", encoding="utf-8")
    assert audit_rotation.queue_waiting_count() == 3


# ---------- build_spec_text ----------

def test_build_spec_text_has_no_expect_line():
    target = _target("A1-x", template="A1", paths=["a.py", "b.md:1-5"], note="check it")
    text = audit_rotation.build_spec_text(target)
    assert text.startswith("TASK: Audit (A1)")
    assert "SCOPE: a.py,b.md:1-5" in text
    assert "NOTE: check it" in text
    assert "EXPECT:" not in text
    assert "FINDING" in text  # reply format is restated in the body
    assert "NO FINDINGS" in text


def test_build_spec_text_uses_correct_template_hint_key():
    for tpl in ("A1", "A2", "A3", "A4", "A5", "A6", "A7"):
        text = audit_rotation.build_spec_text(_target("x", template=tpl))
        assert f"Audit ({tpl})" in text


# ---------- next_audit_spec_id ----------

def test_next_audit_spec_id_starts_at_900(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_rotation, "SPECS_DIR", tmp_path)
    assert audit_rotation.next_audit_spec_id("foo") == "900-audit-foo"


def test_next_audit_spec_id_increments_past_existing(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_rotation, "SPECS_DIR", tmp_path)
    (tmp_path / "900-audit-bar.md").write_text("x", encoding="utf-8")
    (tmp_path / "905-audit-baz.md").write_text("x", encoding="utf-8")
    (tmp_path / "093-not-an-audit.md").write_text("x", encoding="utf-8")
    assert audit_rotation.next_audit_spec_id("foo") == "906-audit-foo"


# ---------- pack_one ----------

def test_pack_one_writes_spec_file(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_rotation, "SPECS_DIR", tmp_path)

    class FakeCompleted:
        returncode = 0
        stdout = "PACKED  900-audit-foo\n"
        stderr = ""

    monkeypatch.setattr(audit_rotation.subprocess, "run", lambda *a, **k: FakeCompleted())
    ok = audit_rotation.pack_one(_target("foo", template="A2"))
    assert ok is True
    written = list(tmp_path.glob("900-audit-foo.md"))
    assert len(written) == 1
    assert "Audit (A2)" in written[0].read_text(encoding="utf-8")


def test_pack_one_false_on_nonzero_returncode(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_rotation, "SPECS_DIR", tmp_path)

    class FakeCompleted:
        returncode = 1
        stdout = ""
        stderr = "REFUSED: something"

    monkeypatch.setattr(audit_rotation.subprocess, "run", lambda *a, **k: FakeCompleted())
    ok = audit_rotation.pack_one(_target("bad"))
    assert ok is False


# ---------- cmd_backfill ----------

def test_cmd_backfill_skips_when_waiting(monkeypatch):
    monkeypatch.setattr(audit_rotation, "queue_waiting_count", lambda: 2)
    calls = []
    monkeypatch.setattr(audit_rotation, "pack_one", lambda t: calls.append(t) or True)
    saved = []
    monkeypatch.setattr(audit_rotation, "save_registry", lambda r: saved.append(r))
    reg = {"targets": [_target("a")]}
    rc = audit_rotation.cmd_backfill(reg)
    assert rc == 0
    assert calls == []
    assert saved == []


def test_cmd_backfill_packs_due_targets_and_updates_last_audited(monkeypatch):
    monkeypatch.setattr(audit_rotation, "queue_waiting_count", lambda: 0)
    monkeypatch.setattr(audit_rotation, "pack_one", lambda t: True)
    saved = []
    monkeypatch.setattr(audit_rotation, "save_registry", lambda r: saved.append(dict(r)))
    reg = {"targets": [_target("a"), _target("b")]}
    rc = audit_rotation.cmd_backfill(reg)
    assert rc == 0
    assert all(t["last_audited"] is not None for t in reg["targets"])
    assert len(saved) == 1


def test_cmd_backfill_failed_pack_leaves_last_audited_alone(monkeypatch):
    monkeypatch.setattr(audit_rotation, "queue_waiting_count", lambda: 0)
    monkeypatch.setattr(audit_rotation, "pack_one", lambda t: False)
    monkeypatch.setattr(audit_rotation, "save_registry", lambda r: None)
    reg = {"targets": [_target("a", last_audited=None)]}
    audit_rotation.cmd_backfill(reg)
    assert reg["targets"][0]["last_audited"] is None


# ---------- cmd_t0 (delegates to the sibling audit_t0_checks module) ----------

def test_cmd_t0_returns_1_when_sibling_module_missing(monkeypatch):
    monkeypatch.setitem(sys.modules, "audit_t0_checks", None)
    rc = audit_rotation.cmd_t0({})
    assert rc == 1


def test_cmd_t0_delegates_to_run_t0_checks(monkeypatch):
    import types
    fake = types.ModuleType("audit_t0_checks")
    fake.run_t0_checks = lambda: 7
    monkeypatch.setitem(sys.modules, "audit_t0_checks", fake)
    rc = audit_rotation.cmd_t0({})
    assert rc == 7


# ---------- main ----------

def test_main_no_flags_returns_2(monkeypatch, capsys):
    rc = audit_rotation.main([])
    assert rc == 2


def test_main_backfill_flag_invokes_cmd_backfill(monkeypatch):
    monkeypatch.setattr(audit_rotation, "load_registry", lambda: {"targets": []})
    calls = []
    monkeypatch.setattr(audit_rotation, "cmd_backfill", lambda reg: calls.append(reg) or 0)
    rc = audit_rotation.main(["--backfill"])
    assert rc == 0
    assert len(calls) == 1
