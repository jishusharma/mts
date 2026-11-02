"""Spec-derived boundary tests for operator_questions.py; all fixtures stay under pytest tmp_path."""
import importlib.util
import os
from pathlib import Path

SOURCE = Path(os.environ.get("OPQ_MODULE_PATH", Path(__file__).with_name("operator_questions.py")))
spec = importlib.util.spec_from_file_location("operator_questions_under_test", SOURCE)
opq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(opq)


def test_prompt_at_typed_char_limit_is_not_automated():
    assert opq.is_automated("x" * 3000) is False


def test_prompt_one_below_limit_is_not_automated():
    assert opq.is_automated("x" * 2999) is False


def test_prompt_one_above_limit_is_automated():
    assert opq.is_automated("x" * 3001) is True


def test_empty_log_file_returns_no_rows(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("", encoding="utf-8")
    assert opq.read_rows(p) == []


def test_missing_log_path_returns_no_rows(tmp_path):
    assert opq.read_rows(tmp_path / "missing.jsonl") == []


def test_valid_jsonl_preserves_rows_and_ignores_blank_lines(tmp_path):
    p = tmp_path / "rows.jsonl"
    p.write_text('{"prompt":"hello","tags":[]}\n\n{"prompt":"world","tags":["x"]}\n', encoding="utf-8")
    assert opq.read_rows(p) == [{"prompt": "hello", "tags": []}, {"prompt": "world", "tags": ["x"]}]


def test_malformed_json_line_raises_json_decode_error(tmp_path):
    p = tmp_path / "bad.jsonl"
    p.write_text('{"prompt": broken}\n', encoding="utf-8")
    try:
        opq.read_rows(p)
    except ValueError as exc:
        assert "line" in str(exc).lower() or exc.__class__.__name__ == "JSONDecodeError"
    else:
        raise AssertionError("malformed JSONL must fail instead of being silently accepted")


def test_unreadable_path_error_is_propagated(tmp_path):
    # A directory exists, but read_text cannot read it as a file: the I/O error is intentionally visible.
    p = tmp_path / "directory.jsonl"
    p.mkdir()
    try:
        opq.read_rows(p)
    except OSError:
        pass
    else:
        raise AssertionError("read errors must propagate; only a missing path maps to an empty log")


def test_automated_prefix_after_leading_whitespace_is_filtered():
    assert opq.is_automated("  <system-reminder>injected") is True


def test_long_prompt_after_leading_whitespace_still_hits_length_guard():
    assert opq.is_automated(" " + "x" * 3000) is True
