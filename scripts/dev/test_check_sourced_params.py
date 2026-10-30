import importlib.util
import json
from datetime import date
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).with_name("check_sourced_params.py")
spec = importlib.util.spec_from_file_location("check_sourced_params_under_test", MODULE_PATH)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


@pytest.fixture(autouse=True)
def clear_allowlist():
    checker.ALLOWLIST = {}


def write_json(root, name, payload):
    path = root / "MyTradingSys/backtest/layers/rsi/params" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_allowlist_expiry_at_limit_is_still_allowed():
    item = ("p.json", "x", "no-label")
    checker.ALLOWLIST = {item: ("owner", "2026-10-30")}
    assert checker.evaluate(1, [item], today=date(2026, 10, 30)) == ([], 1)


def test_allowlist_one_day_below_expiry_is_allowed():
    item = ("p.json", "x", "no-label")
    checker.ALLOWLIST = {item: ("owner", "2026-10-30")}
    assert checker.evaluate(1, [item], today=date(2026, 10, 29)) == ([], 1)


def test_allowlist_one_day_above_expiry_fails():
    item = ("p.json", "x", "no-label")
    checker.ALLOWLIST = {item: ("owner", "2026-10-30")}
    fails, allowed = checker.evaluate(1, [item], today=date(2026, 10, 31))
    assert allowed == 0
    assert fails == ["EXPIRED allowlist ('p.json', 'x', 'no-label') (owner owner, expiry 2026-10-30)"]


def test_empty_root_scans_zero_params(tmp_path):
    assert checker.scan(tmp_path) == (0, [])


def test_valid_sourced_parameter_with_locator_has_no_findings(tmp_path):
    path = write_json(tmp_path, "valid.json", {"params": {"lookback": {"value": 12, "label": "SOURCED", "source": "KR-A12"}}})
    assert checker.check_file(path, None, None) == []
    assert checker.scan(tmp_path) == (1, [])


def test_malformed_json_raises_json_decode_error(tmp_path):
    path = write_json(tmp_path, "broken.json", {})
    path.write_text("{bad json", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        checker.scan(tmp_path)


def test_missing_root_value_is_reported_as_cli_argument_error(capsys):
    with pytest.raises(IndexError):
        checker.main(["--root"])
    assert capsys.readouterr().out == ""


def test_cli_lists_findings_and_returns_failure_for_unlabelled_param(tmp_path, capsys):
    write_json(tmp_path, "bad.json", {"params": {"length": {"value": 8}}})
    assert checker.main(["--root", str(tmp_path), "--list"]) == 1
    assert capsys.readouterr().out.splitlines() == [
        "('bad.json', 'length', 'no-label')",
        "check_sourced_params: 1 params checked, 0 allowlisted, 1 failing",
        "FAIL bad.json::length::no-label",
    ]


def test_flat_operator_source_is_ours_and_needs_no_locator(tmp_path):
    path = write_json(tmp_path, "operator.json", {"source": " Operator "})
    assert checker.check_file(path, None, None) == []
