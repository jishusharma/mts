"""Unit tests for scripts/dev/aibridge_verify.py (hand-computed, no network).

Mutation check on broken scratch copy:
- Mutation: in `lf(b)`, replaced `return b.replace(b'\\r\\n', b'\\n')` with `return b`
  (no-op CRLF normalization).
- Failing test: `test_lf_normal_empty_and_lone_cr` failed with
  `AssertionError: assert b'a\\r\\nb\\r\\nc' == b'a\\nb\\nc'`.
"""
import json
import os
import sys
from pathlib import Path

import pytest

DEV_DIR = Path(
    os.environ.get(
        "AIBRIDGE_VERIFY_DIR",
        str(Path(__file__).resolve().parents[5] / "scripts" / "dev"),
    )
)
sys.path.insert(0, str(DEV_DIR))

import aibridge_verify  # noqa: E402


def test_lf_normal_empty_and_lone_cr():
    """Normal CRLF normalization, empty bytes, and lone CR preservation."""
    assert aibridge_verify.lf(b"a\r\nb\r\nc") == b"a\nb\nc"
    assert aibridge_verify.lf(b"") == b""
    assert aibridge_verify.lf(b"a\nb\rc") == b"a\nb\rc"


def test_mask_bg_normal_empty_and_malformed():
    """Mask TOKEN/AGENT_CWD/AGENT_URL; handle empty and malformed UTF-8 bytes."""
    normal = (
        b"const TOKEN = 'secret123';\n"
        b"const AGENT_CWD = 'F:/MTS';\n"
        b"const AGENT_URL = 'http://127.0.0.1:7181';\n"
    )
    expected = (
        b"const TOKEN = 'X';\n"
        b"const AGENT_CWD = 'X';\n"
        b"const AGENT_URL = 'X';\n"
    )
    assert aibridge_verify.mask_bg(normal) == expected
    assert aibridge_verify.mask_bg(b"") == b""

    malformed = b"\xff\xfeconst TOKEN = 'abc';\nconst TOKEN = 'unterminated\n"
    expected_malformed = (
        b"\xef\xbf\xbd\xef\xbf\xbdconst TOKEN = 'X';\n"
        b"const TOKEN = 'unterminated\n"
    )
    assert aibridge_verify.mask_bg(malformed) == expected_malformed


def test_ext_id_for_path_normal_and_empty():
    """Chrome unpacked extension ID derivation for normal and empty paths."""
    assert (
        aibridge_verify.ext_id_for_path("F:/AIBridge/extension")
        == "kgighilgkdgkdghegpibjbjcidcmejkg"
    )
    assert (
        aibridge_verify.ext_id_for_path("F:\\AIBridge\\extension\\")
        == "kgighilgkdgkdghegpibjbjcidcmejkg"
    )
    assert aibridge_verify.ext_id_for_path("") == "ahfndnnpfkdkicgobdkjcciioifdlmel"


def test_check_missing_root_returns_installed_fail(tmp_path):
    """Empty root directory fails early on `installed` without network calls."""
    rows = aibridge_verify.check(str(tmp_path), roundtrip=False)
    assert len(rows) == 1
    assert rows[0]["check"] == "installed"
    assert rows[0]["status"] == "FAIL"
    assert "missing agent.ps1, config.json, manifest.json" in rows[0]["evidence"]


def test_check_malformed_config_raises_json_decode_error(tmp_path):
    """Malformed config.json raises json.JSONDecodeError when required files exist."""
    (tmp_path / "src").mkdir()
    (tmp_path / "extension").mkdir()
    (tmp_path / "src" / "agent.ps1").write_text("# stub\n", encoding="utf-8")
    (tmp_path / "extension" / "manifest.json").write_text("{}", encoding="utf-8")
    (tmp_path / "src" / "config.json").write_text("{not json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        aibridge_verify.check(str(tmp_path), roundtrip=False)
