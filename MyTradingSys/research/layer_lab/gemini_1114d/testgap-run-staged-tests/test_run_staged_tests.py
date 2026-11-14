"""Unit tests for scripts/dev/run_staged_tests.py.

Mutation check on a scratch copy of scripts/dev/run_staged_tests.py:
- Mutation: in `run_staged_tests.py` line 29, changed
  `shutil.copy(p, tmp / p.name[:-4])` to `shutil.copy(p, tmp / p.name)`
  so `.py.new` no longer overrides the live `.py` filename.
- Failing test: `test_py_new_overrides_live_py_and_copies_json_unittest_cmd`
  (failed with AssertionError because `mod.py` retained `"VAL = 'live'\\n"`
  instead of `"VAL = 'staged'\\n"`).
"""

import importlib.util
import os
import sys
from pathlib import Path

import pytest


def _load_module():
    repo_root = Path(__file__).resolve().parents[5]
    mod_path = Path(
        os.environ.get(
            "RUN_STAGED_TESTS_PATH",
            repo_root / "scripts" / "dev" / "run_staged_tests.py",
        )
    )
    spec = importlib.util.spec_from_file_location("run_staged_tests", mod_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_py_new_overrides_live_py_and_copies_json_unittest_cmd(tmp_path, monkeypatch):
    mod = _load_module()
    src = tmp_path / "src"
    src.mkdir()
    (src / "mod.py").write_text("VAL = 'live'\n", encoding="utf-8")
    (src / "mod.py.new").write_text("VAL = 'staged'\n", encoding="utf-8")
    (src / "cfg.json").write_text('{"k": 1}\n', encoding="utf-8")

    seen = {}

    def fake_call(cmd, cwd=None, env=None):
        cwd_path = Path(cwd)
        seen["cmd"] = cmd
        seen["cwd"] = cwd_path
        seen["env_root"] = env["MTS_REPO_ROOT"]
        seen["mod_text"] = (cwd_path / "mod.py").read_text(encoding="utf-8")
        seen["json_text"] = (cwd_path / "cfg.json").read_text(encoding="utf-8")
        seen["has_new"] = (cwd_path / "mod.py.new").exists()
        return 0

    monkeypatch.setattr(mod.subprocess, "call", fake_call)
    rc = mod.main([str(src), "--", "test_alpha", "test_beta"])

    assert rc == 0
    assert seen["cmd"] == [sys.executable, "-m", "unittest", "-v", "test_alpha", "test_beta"]
    assert seen["mod_text"] == "VAL = 'staged'\n"
    assert seen["json_text"] == '{"k": 1}\n'
    assert seen["has_new"] is False
    assert seen["env_root"] == str(Path.cwd())
    assert not seen["cwd"].exists()


def test_script_mode_and_fake_replacement(tmp_path, monkeypatch):
    mod = _load_module()
    src = tmp_path / "src"
    src.mkdir()
    (src / "real.py").write_text("SRC = 'real'\n", encoding="utf-8")
    (src / "fake_real.py").write_text("SRC = 'fake'\n", encoding="utf-8")
    (src / "runner.py").write_text("print('ok')\n", encoding="utf-8")

    seen = {}

    def fake_call(cmd, cwd=None, env=None):
        cwd_path = Path(cwd)
        seen["cmd"] = cmd
        seen["cwd"] = cwd_path
        seen["real_text"] = (cwd_path / "real.py").read_text(encoding="utf-8")
        return 0

    monkeypatch.setattr(mod.subprocess, "call", fake_call)
    rc = mod.main(
        [str(src), "--script", "runner.py", "--fake", "fake_real.py=real.py"]
    )

    assert rc == 0
    assert seen["cmd"] == [sys.executable, "runner.py"]
    assert seen["real_text"] == "SRC = 'fake'\n"
    assert not seen["cwd"].exists()


def test_nonzero_exit_code_propagates_and_cleans_up(tmp_path, monkeypatch):
    mod = _load_module()
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.py").write_text("X = 1\n", encoding="utf-8")

    seen = {}

    def fake_call(cmd, cwd=None, env=None):
        seen["cwd"] = Path(cwd)
        return 3

    monkeypatch.setattr(mod.subprocess, "call", fake_call)
    rc = mod.main([str(src), "--", "test_fail"])

    assert rc == 3
    assert not seen["cwd"].exists()


def test_later_dir_overrides_earlier_dir_and_cleanup_on_exception(tmp_path, monkeypatch):
    mod = _load_module()
    d1 = tmp_path / "d1"
    d2 = tmp_path / "d2"
    d1.mkdir()
    d2.mkdir()
    (d1 / "shared.py").write_text("FROM = 'd1'\n", encoding="utf-8")
    (d2 / "shared.py").write_text("FROM = 'd2'\n", encoding="utf-8")

    seen = {}

    def fake_call(cmd, cwd=None, env=None):
        cwd_path = Path(cwd)
        seen["cwd"] = cwd_path
        seen["shared_text"] = (cwd_path / "shared.py").read_text(encoding="utf-8")
        raise RuntimeError("boom")

    monkeypatch.setattr(mod.subprocess, "call", fake_call)
    with pytest.raises(RuntimeError, match="boom"):
        mod.main([str(d1), str(d2), "--", "test_shared"])

    assert seen["shared_text"] == "FROM = 'd2'\n"
    assert not seen["cwd"].exists()
