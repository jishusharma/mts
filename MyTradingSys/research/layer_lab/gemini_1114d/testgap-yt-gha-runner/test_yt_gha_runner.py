"""Tests for scripts/dev/yt_gha_runner.py (argument/env parsing, output shaping, monkeypatched network).

Existing coverage check (git grep -l "yt_gha_runner" scripts MyTradingSys):
- scripts/dev/test_yt_freedom.py:100-105 tests only the subprocess refusal outside GitHub Actions
  (`test_runner_script_refuses_outside_github_actions`). No test file named test_yt_gha_runner.py existed.

Mutation check on a broken scratch copy:
- Mutated line 49 in a scratch copy of scripts/dev/yt_gha_runner.py from
  `all(v.startswith("OK") for v in summary.values())` to
  `any(v.startswith("OK") for v in summary.values())`.
- Failing test: `test_langs_parsing_and_mixed_outcomes_return_nonzero` (`assert 0 == 1`).
"""
import importlib.util
import json
import os
import runpy
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
SCRIPTS_DEV = REPO_ROOT / "scripts" / "dev"
RUNNER_PATH = Path(os.environ.get("YT_GHA_RUNNER_PATH", str(SCRIPTS_DEV / "yt_gha_runner.py")))

if str(SCRIPTS_DEV) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DEV))


def _load_runner(monkeypatch):
    monkeypatch.setenv("YT_RUNNER_TEST", "1")
    monkeypatch.delenv("YT_ALLOW_DIRECT", raising=False)
    spec = importlib.util.spec_from_file_location("yt_gha_runner_under_test", RUNNER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_env_guard_sets_yt_allow_direct_and_writes_single_ok_json(tmp_path, monkeypatch):
    mod = _load_runner(monkeypatch)
    assert os.environ.get("YT_ALLOW_DIRECT") == "1"

    out_dir = tmp_path / "out"
    seen = {}

    def fake_build_routes(names=None, runner=False):
        seen["runner"] = runner
        return ["fake-route"]

    def fake_get_captions(vid, routes, langs):
        seen["call"] = (vid, routes, langs)
        res = {
            "cues": [(0, "hello"), (4, "world")],
            "info": {"title": "T"},
            "lang": "en",
            "auto": False,
        }
        return res, "direct", ["direct:ok"], False

    monkeypatch.setattr(mod.yt, "build_routes", fake_build_routes)
    monkeypatch.setattr(mod.yt, "get_captions", fake_get_captions)

    rc = mod.main(["--ids", "aaaaaaaaaaa", "--out", str(out_dir)])
    assert rc == 0
    assert seen["runner"] is True
    assert seen["call"] == ("aaaaaaaaaaa", ["fake-route"], ["en", "hi"])

    vid_payload = json.loads((out_dir / "aaaaaaaaaaa.json").read_text(encoding="utf-8"))
    assert vid_payload == {
        "cues": [[0, "hello"], [4, "world"]],
        "info": {"title": "T"},
        "lang": "en",
        "auto": False,
        "route": "direct",
    }
    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary == {"aaaaaaaaaaa": "OK via direct"}


def test_langs_parsing_and_mixed_outcomes_return_nonzero(tmp_path, monkeypatch):
    mod = _load_runner(monkeypatch)
    out_dir = tmp_path / "out"
    calls = []

    def fake_get_captions(vid, routes, langs):
        calls.append((vid, langs))
        if vid == "aaaaaaaaaaa":
            return (
                {"cues": [(1, "hi")], "info": {}, "lang": "en", "auto": True},
                "invidious",
                ["direct:down", "invidious:ok"],
                False,
            )
        if vid == "bbbbbbbbbbb":
            return None, None, ["direct:nocaps"], True
        return None, None, ["direct:down"], False

    monkeypatch.setattr(mod.yt, "build_routes", lambda runner=False: ["r1"])
    monkeypatch.setattr(mod.yt, "get_captions", fake_get_captions)

    rc = mod.main([
        "--ids", " https://youtu.be/aaaaaaaaaaa , bad_id , bbbbbbbbbbb , ccccccccccc ",
        "--langs", "en, ,fr,",
        "--out", str(out_dir),
    ])
    assert rc == 1
    assert calls == [
        ("aaaaaaaaaaa", ["en", "fr"]),
        ("bbbbbbbbbbb", ["en", "fr"]),
        ("ccccccccccc", ["en", "fr"]),
    ]
    assert (out_dir / "aaaaaaaaaaa.json").exists()
    assert not (out_dir / "bbbbbbbbbbb.json").exists()
    assert not (out_dir / "ccccccccccc.json").exists()

    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary == {
        "aaaaaaaaaaa": "OK via invidious",
        " bad_id ": "BADID",
        "bbbbbbbbbbb": "NOCAPS",
        "ccccccccccc": "FAIL",
    }


def test_all_ok_multiple_videos_returns_zero_and_normalizes_cues(tmp_path, monkeypatch):
    mod = _load_runner(monkeypatch)
    out_dir = tmp_path / "out"

    def fake_get_captions(vid, routes, langs):
        return (
            {"cues": [(1.5, "one"), (3.0, "two")], "info": {"title": vid}, "lang": "hi", "auto": False},
            "piped",
            ["piped:ok"],
            False,
        )

    monkeypatch.setattr(mod.yt, "build_routes", lambda runner=False: ["r1"])
    monkeypatch.setattr(mod.yt, "get_captions", fake_get_captions)

    rc = mod.main(["--ids", "aaaaaaaaaaa,bbbbbbbbbbb", "--out", str(out_dir)])
    assert rc == 0
    for vid in ("aaaaaaaaaaa", "bbbbbbbbbbb"):
        data = json.loads((out_dir / f"{vid}.json").read_text(encoding="utf-8"))
        assert data["cues"] == [[1.5, "one"], [3.0, "two"]]
        assert data["route"] == "piped"
    summary = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary == {"aaaaaaaaaaa": "OK via piped", "bbbbbbbbbbb": "OK via piped"}


def test_refuses_outside_github_actions_without_test_env(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("YT_RUNNER_TEST", raising=False)
    with mock.patch.object(sys, "argv", [str(RUNNER_PATH), "--ids", "aaaaaaaaaaa"]):
        with pytest.raises(SystemExit) as excinfo:
            runpy.run_path(str(RUNNER_PATH), run_name="__main__")
    assert "only inside GitHub Actions" in str(excinfo.value)
