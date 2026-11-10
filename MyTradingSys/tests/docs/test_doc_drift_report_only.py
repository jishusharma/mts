"""ARCH_REVIEW row 1: a doc-wording drift yields a report line and a pass, not a failed gate.
Fail-first: on the pre-change tests, test_8 and the super-session wording tests raise AssertionError on drift."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pytest  # noqa: E402
import test_integrity as I  # noqa: E402
from doc_drift import report_only  # noqa: E402


def test_report_only_prints_the_drift_and_passes(capsys):
    @report_only
    def test_x():
        assert "a" == "b", "wording moved"
    test_x()
    assert "DOC-DRIFT test_x" in capsys.readouterr().err


def test_wording_drift_in_claude_md_is_a_report_line_not_a_failure(tmp_path, monkeypatch, capsys):
    (tmp_path / "CLAUDE.md").write_text("- CI RED: something else\n", encoding="utf-8")
    monkeypatch.setattr(I, "REPO", tmp_path)
    I.test_8_red_trunk_is_reverted_not_forward_fixed()
    assert "DOC-DRIFT test_8" in capsys.readouterr().err


def test_claude_md_size_cap_still_fails(tmp_path, monkeypatch):
    (tmp_path / "CLAUDE.md").write_bytes(b"x" * (I.SIZE_CAPS["CLAUDE.md"] + 1))
    monkeypatch.setattr(I, "REPO", tmp_path)
    monkeypatch.delenv("MTS_GATE_CHANGED_FILES", raising=False)
    with pytest.raises(AssertionError):
        I.test_7_size_cap("CLAUDE.md")


def test_other_cap_over_is_reported(tmp_path, monkeypatch, capsys):
    (tmp_path / "MyTradingSys/system").mkdir(parents=True)
    (tmp_path / "MyTradingSys/system/RELAY.md").write_bytes(b"x" * 99999)
    monkeypatch.setattr(I, "REPO", tmp_path)
    monkeypatch.delenv("MTS_GATE_CHANGED_FILES", raising=False)
    I.test_7_size_cap("MyTradingSys/system/RELAY.md")
    assert "DOC-DRIFT test_7_size_cap" in capsys.readouterr().err
