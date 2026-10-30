"""Spec-derived tests for the frames-only check-set validator.

All fixtures live under pytest's temporary directory; none of the real ledgers
or video data are read.
"""
import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).with_name("check_set_frames.py")
SPEC = importlib.util.spec_from_file_location("check_set_frames_under_test", SCRIPT)
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


def configure_paths(monkeypatch, tmp_path):
    check.REPO_ROOT = tmp_path
    check.CHECK_SET_DIR = tmp_path / "check"
    check.CHECK_SET_MD = check.CHECK_SET_DIR / "CHECK_SET.md"
    check.TOM_LEDGER_CSV = tmp_path / "ledger.csv"
    check.TOM_LEDGER_MD = tmp_path / "ledger.md"
    check.TOM_VIDEOS_DIR = tmp_path / "videos"
    check.TOM_VIDEOS_DIR.mkdir()


def put_csv(path, text):
    path.write_text(text, encoding="utf-8")


def test_check_md_at_acceptance_boundary_has_required_and_none_phrase(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    check.CHECK_SET_DIR.mkdir()
    check.CHECK_SET_MD.write_text("NO CAPTION READ\nnone found beyond S7/S8 with the queries tried", encoding="utf-8")
    assert check.check_check_set_md() == []


def test_check_md_one_requirement_below_boundary_reports_both(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    check.CHECK_SET_DIR.mkdir()
    check.CHECK_SET_MD.write_text("no caption read\nstatus pending", encoding="utf-8")
    assert check.check_check_set_md() == [
        "CHECK_SET.md must state trades found or 'none found beyond S7/S8 with the queries tried'"
    ]


def test_check_md_one_phrase_above_minimum_is_accepted(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    check.CHECK_SET_DIR.mkdir()
    check.CHECK_SET_MD.write_text("no caption read; 3 trades found", encoding="utf-8")
    assert check.check_check_set_md() == []


def test_empty_csv_is_an_error_for_no_check_rows(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    put_csv(check.TOM_LEDGER_CSV, "id,video,frame,note,time_evidence_type,evidence_unresolved,executed_contract,prior_exposure\n")
    assert check.check_check_set_ledger_rows() == ["No CHECK set rows found in TOM_TRADE_LEDGER.csv"]


def test_malformed_csv_header_returns_the_current_key_error(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    put_csv(check.TOM_LEDGER_CSV, "video,frame\nliEJMfE_PXg,frame.png\n")
    with pytest.raises(KeyError, match="'id'"):
        check.check_check_set_ledger_rows()


def test_missing_csv_is_reported_without_reading_it(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    assert check.check_check_set_ledger_rows() == [f"Missing ledger CSV: {check.TOM_LEDGER_CSV}"]


def test_qualifying_row_checks_path_caption_fields_and_contract(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    put_csv(check.TOM_LEDGER_CSV,
        "id,video,frame,note,time_evidence_type,evidence_unresolved,executed_contract,prior_exposure\n"
        "T11,liEJMfE_PXg,missing.png,read file.vtt,,,. ,CHECK\n".replace(". ,", ","))
    result = check.check_check_set_ledger_rows()
    assert result == [
        "Row T11: frame path does not exist on disk: missing.png",
        "Row T11: caption file referenced in field note: read file.vtt",
        "Row T11: executed_contract must be NOT_IN_DATA, got ''",
    ]


def test_valid_qualifying_row_and_unrelated_row_pass(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    frame = tmp_path / "frame.png"
    frame.touch()
    put_csv(check.TOM_LEDGER_CSV,
        "id,video,frame,note,time_evidence_type,evidence_unresolved,executed_contract,prior_exposure\n"
        "T11,liEJMfE_PXg,frame.png,,, ,NOT_IN_DATA,\n"
        "X1,other,absent.png,,,,,\n")
    assert check.check_check_set_ledger_rows() == []


def test_existing_caption_file_is_reported(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    (check.TOM_VIDEOS_DIR / "liEJMfE_PXg.vtt").touch()
    frame = tmp_path / "frame.png"
    frame.touch()
    put_csv(check.TOM_LEDGER_CSV,
        "id,video,frame,note,time_evidence_type,evidence_unresolved,executed_contract,prior_exposure\n"
        "T11,liEJMfE_PXg,frame.png,,,,NOT_IN_DATA,\n")
    assert check.check_check_set_ledger_rows() == [
        f"Row T11: video liEJMfE_PXg has caption file {check.TOM_VIDEOS_DIR / 'liEJMfE_PXg.vtt'} on disk (violates frames-only)"
    ]


def test_ledger_count_accepts_trade_ids_or_expected_count(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    check.TOM_LEDGER_MD.write_text("There are 2 trade ids.", encoding="utf-8")
    assert check.check_ledger_md_count() == []
    check.TOM_LEDGER_MD.write_text("14 trade ids / 37 rows", encoding="utf-8")
    assert check.check_ledger_md_count() == []


def test_missing_ledger_markdown_is_reported(monkeypatch, tmp_path):
    configure_paths(monkeypatch, tmp_path)
    assert check.check_ledger_md_count() == [f"Missing ledger MD: {check.TOM_LEDGER_MD}"]


def test_main_error_path_prints_all_failures_and_returns_one(monkeypatch, tmp_path, capsys):
    configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(check, "check_check_set_md", lambda: ["md problem"])
    monkeypatch.setattr(check, "check_check_set_ledger_rows", lambda: [])
    monkeypatch.setattr(check, "check_ledger_md_count", lambda: ["count problem"])
    assert check.main() == 1
    assert capsys.readouterr().out == (
        "FAIL: check_set_frames.py violations found:\n"
        "  - md problem\n"
        "  - count problem\n"
    )


def test_main_success_path_prints_pass(monkeypatch, tmp_path, capsys):
    configure_paths(monkeypatch, tmp_path)
    monkeypatch.setattr(check, "check_check_set_md", lambda: [])
    monkeypatch.setattr(check, "check_check_set_ledger_rows", lambda: [])
    monkeypatch.setattr(check, "check_ledger_md_count", lambda: [])
    assert check.main() == 0
    assert capsys.readouterr().out == "PASS: check_set_frames.py all checks passed\n"
